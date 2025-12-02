"""
统一的访谈基类
消除不同interview类之间的代码重复
"""

import os
import json
import time
import pickle
from datetime import datetime
from openai import OpenAI
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
from pathlib import Path
from abc import ABC, abstractmethod

# 导入基础模块 - 避免循环导入，直接导入
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.base.ivs_questionnaire import IVSQuestions, LLMResponse, ResponseValidator


class BaseInterview(ABC):
    """访谈基类 - 统一技术功能，业务逻辑由子类实现"""
    
    def __init__(self, repeat_count: int = 1, data_path: str = "data", 
                 consensus_count: int = 1):
        """
        Args:
            repeat_count: 单次失败重试次数
            data_path: 数据路径
            consensus_count: 多轮访谈取众数的轮数（1表示不取众数）
        """
        self.questions = IVSQuestions()
        self.validator = ResponseValidator()
        self.model_configs = self._load_model_configs()
        self.api_keys = self._load_api_keys()
        self.repeat_count = repeat_count
        self.consensus_count = consensus_count
        self.data_path = Path(data_path)
    
    def _load_model_configs(self) -> Dict[str, Dict[str, str]]:
        """从配置文件加载模型配置"""
        # 统一配置文件路径
        config_path = Path(__file__).parent.parent.parent / 'config' / 'llm_models.json'
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('models', {})
        except Exception as e:
            print(f"加载模型配置失败: {e}")
            return {}
    
    def _load_api_keys(self) -> Dict[str, str]:
        """从环境变量加载API密钥"""
        api_keys = {}
        for model_name, config in self.model_configs.items():
            api_key_name = config.get('api_key', 'OPENROUTER_API_KEY')
            api_key = os.getenv(api_key_name)
            if api_key:
                api_keys[model_name] = api_key
            else:
                print(f"警告: 模型 {model_name} 的API密钥 {api_key_name} 未设置")
        return api_keys
    
    def get_client(self, model_name: str) -> OpenAI:
        """创建OpenAI客户端 - 统一客户端管理"""
        if model_name not in self.model_configs:
            raise ValueError(f"未知模型: {model_name}")
        
        config = self.model_configs[model_name]
        api_key = self.api_keys.get(model_name)
        
        if not api_key:
            raise ValueError(f"模型 {model_name} 的API密钥未设置")
        
        return OpenAI(
            api_key=api_key,
            base_url=config.get('base_url', 'https://api.openai.com/v1')
        )
    
    def _get_format_hint(self, question_id: str, attempt: int = 0) -> str:
        """生成格式提示 - 统一格式处理"""
        format_hint = ""
        if question_id == "Y002":
            format_hint = "\n\nPlease respond with exactly 2 numbers separated by space."
        elif question_id == "Y003":
            format_hint = "\n\nPlease respond with 1-5 numbers (from 1-11) separated by spaces."
        else:
            format_hint = "\n\nPlease respond with ONE number only."
        
        # 重试时加强提示
        if attempt > 0:
            format_hint += f"\n\nThis is attempt {attempt + 1}. Please provide a genuine numerical answer."
        
        return format_hint
    
    def _get_dynamic_delay(self, model_name: str) -> float:
        """获取动态延迟时间 - 统一延迟策略"""
        if any(x in model_name.lower() for x in ['gpt', 'claude']):
            return 0.2  # 快速模型，短延迟
        else:
            return 0.3  # 其他模型，稍长延迟
    
    def _call_model_api_base(self, model_name: str, messages: List[Dict], **kwargs) -> Optional[str]:
        """基础API调用方法 - 统一API调用逻辑"""
        try:
            client = self.get_client(model_name)
            
            # 默认参数
            params = {
                'model': model_name,
                'messages': messages,
                'max_tokens': kwargs.get('max_tokens', 50),
                'temperature': kwargs.get('temperature', 0.1)
            }
            
            # 添加其他参数，但避免重复
            for key, value in kwargs.items():
                if key not in params:
                    params[key] = value
            
            # 特殊模型处理
            if "deepseek" in model_name.lower():
                params['max_tokens'] = 500
            
            response = client.chat.completions.create(**params)
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"API调用失败 ({model_name}): {e}")
            return None
    
    def call_model_api(self, model_name: str, question_id: str, question_text: str, 
                      system_prompt: str, **kwargs) -> Optional[str]:
        """统一的模型API调用方法 - 带重试机制，系统提示词由调用方提供"""
        max_retries = 5
        for attempt in range(max_retries):
            try:
                # 生成格式提示
                format_hint = self._get_format_hint(question_id, attempt)
                
                # 构建消息 - 系统提示词完全由调用方决定
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question_text + format_hint}
                ]
                
                # 固定温度 - 保持实验严格控制，避免温度成为混淆变量
                # 配合5次重复取众数策略，固定温度能确保测量的是模型真实倾向而非随机性
                temperature = 0.1
                
                # 从kwargs中移除temperature以避免重复参数
                filtered_kwargs = {k: v for k, v in kwargs.items() if k != 'temperature'}
                
                # 调用API
                response = self._call_model_api_base(
                    model_name, messages, 
                    temperature=temperature, 
                    **filtered_kwargs
                )
                
                if response:
                    return response
                    
            except Exception as e:
                print(f"API调用失败 ({model_name}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(1 * (attempt + 1))  # 递增延迟
        
        return None
    
    def ask_question_with_retry(self, model_name: str, question_id: str, 
                               system_prompt: str) -> LLMResponse:
        """询问单个问题 - 带重试和验证"""
        question_data = self.questions.get_question(question_id)
        if not question_data:
            return LLMResponse(
                model_name=model_name,
                question_id=question_id,
                response=None,
                raw_response=None,
                is_valid=False,
                error_message=f"未找到问题: {question_id}"
            )
        
        question_text = question_data['question']
        
        # 多次尝试获取有效回答
        for attempt in range(self.repeat_count):
            raw_response = self.call_model_api(
                model_name, question_id, question_text, system_prompt
            )
            
            if raw_response is None:
                continue
            
            # 验证回答
            is_valid, processed_response, error_msg = self.validator.validate_response(
                question_id, raw_response
            )
            
            if is_valid:
                return LLMResponse(
                    model_name=model_name,
                    question_id=question_id,
                    response=processed_response,
                    raw_response=raw_response,
                    is_valid=True
                )
            
            # 问题间延迟
            time.sleep(self._get_dynamic_delay(model_name))
        
        # 所有尝试都失败
        return LLMResponse(
            model_name=model_name,
            question_id=question_id,
            response=None,
            raw_response=raw_response if 'raw_response' in locals() else None,
            is_valid=False,
            error_message=error_msg if 'error_msg' in locals() else "所有尝试都失败"
        )
    
    def _calculate_consensus(self, responses: List[LLMResponse], 
                            question_id: str) -> LLMResponse:
        """
        计算多个回答的众数（通用实现）
        
        Args:
            responses: 多次回答的列表
            question_id: 问题ID
            
        Returns:
            众数回答的LLMResponse对象
        """
        from collections import Counter
        
        # 提取有效回答
        valid_responses = [r.response for r in responses 
                          if r.is_valid and r.response is not None]
        
        if not valid_responses:
            print(f"  ⚠️ {question_id}: 所有{len(responses)}次尝试都失败")
            return responses[0]  # 返回第一个回答（即使无效）
        
        # 根据问题类型处理众数计算
        if question_id in ['Y002', 'Y003']:
            # 复杂问题（列表类型）：转字符串比较
            response_strings = [str(resp) for resp in valid_responses]
            most_common_str, count = Counter(response_strings).most_common(1)[0]
            
            # 找到对应的原始回答
            consensus_value = None
            for i, resp_str in enumerate(response_strings):
                if resp_str == most_common_str:
                    consensus_value = valid_responses[i]
                    break
        else:
            # 单选题：直接计算众数
            most_common_value, count = Counter(valid_responses).most_common(1)[0]
            consensus_value = most_common_value
        
        # 计算置信度
        confidence = count / len(valid_responses) if valid_responses else 0
        
        # 创建众数回答对象
        base_response = responses[0]  # 使用第一个回答作为模板
        return LLMResponse(
            model_name=base_response.model_name,
            question_id=question_id,
            response=consensus_value,
            raw_response=f"Consensus from {len(valid_responses)} responses (confidence={confidence:.1%}): {consensus_value}",
            is_valid=True,
            error_message=None
        )
    
    @abstractmethod
    def interview_entity(self, model_name: str, entity_id: str) -> List[LLMResponse]:
        """访谈单个实体 - 子类必须实现"""
        pass
    
    @abstractmethod
    def batch_interview(self, model_names: List[str], entities: List[str]) -> Dict[str, Any]:
        """批量访谈 - 子类必须实现"""
        pass
    
    def save_results(self, results: Dict[str, Any], output_dir: str = None) -> str:
        """保存结果 - 统一保存逻辑"""
        if output_dir is None:
            output_dir = self.data_path / "interview_results"
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存为pickle格式
        pkl_file = output_path / f"interview_results_{timestamp}.pkl"
        with open(pkl_file, 'wb') as f:
            pickle.dump(results, f)
        
        # 保存为JSON格式（如果可序列化）
        try:
            json_file = output_path / f"interview_results_{timestamp}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            print(f"JSON保存失败: {e}")
        
        print(f"✅ 结果已保存到: {pkl_file}")
        return str(pkl_file)
    
    def _on_task_completed(self, model_name: str, entity_id: str, 
                          responses: List, intermediate_data: Dict = None):
        """
        任务完成钩子方法（供子类重写）
        
        在并行批量访谈中，每个任务完成后立即调用此方法。
        子类可以重写此方法实现即时保存功能，防止长时间任务崩溃丢失数据。
        
        Args:
            model_name: 模型名称
            entity_id: 实体ID（如国家名称），Stage1为None
            responses: 访谈响应列表
            intermediate_data: 中间数据（如一致性信息）
        
        Example:
            # Stage2重写示例：保存角色扮演结果
            def _on_task_completed(self, model_name, entity_id, responses, intermediate_data):
                self._save_individual_result(model_name, entity_id, responses, intermediate_data)
        """
        # 默认实现：不做任何操作
        pass
    
    def _batch_interview_sequential(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        串行批量访谈（通用实现）
        
        Args:
            tasks: 任务列表，每个任务是一个字典，包含interview_entity所需的参数
                   例如: [{'model_name': 'gpt-4', 'entity_id': 'China'}, ...]
                   或: [{'model_name': 'gpt-4', 'entity_id': None}, ...]
        
        Returns:
            包含results、total_tasks、successful_tasks、success_rate的字典
        """
        results = {}
        successful_tasks = 0
        total_tasks = len(tasks)
        
        for i, task in enumerate(tasks, 1):
            model_name = task['model_name']
            entity_id = task.get('entity_id', None)
            
            print(f"\n{'='*50}")
            print(f"任务 {i}/{total_tasks}: {model_name}", end="")
            if entity_id:
                print(f" → {entity_id}")
            else:
                print()
            print(f"{'='*50}")
            
            # 调用子类实现的interview_entity
            responses, intermediate_data = self.interview_entity(model_name, entity_id)
            
            if responses:
                # 生成结果键
                if entity_id:
                    result_key = f"{model_name}_{entity_id}"
                else:
                    result_key = model_name
                
                results[result_key] = {
                    'model_name': model_name,
                    'entity_id': entity_id,
                    'responses': responses,
                    'intermediate_data': intermediate_data
                }
                successful_tasks += 1
                
                # 打印一致性信息（如果有）
                consistency_info = ""
                if intermediate_data and 'overall_consistency' in intermediate_data:
                    consistency_info = f" (一致性: {intermediate_data['overall_consistency']:.1%})"
                print(f"✅ 完成: {len(responses)} 个回答{consistency_info}")
            else:
                print(f"❌ 失败")
        
        return {
            'results': results,
            'total_tasks': total_tasks,
            'successful_tasks': successful_tasks,
            'success_rate': successful_tasks / total_tasks if total_tasks > 0 else 0
        }
    
    def _batch_interview_concurrent(self, tasks: List[Dict[str, Any]], 
                                   max_workers: int = 4) -> Dict[str, Any]:
        """
        并行批量访谈（通用实现）
        
        Args:
            tasks: 任务列表，每个任务是一个字典
            max_workers: 最大并发线程数
        
        Returns:
            包含results、total_tasks、successful_tasks、success_rate的字典
        """
        from concurrent.futures import ThreadPoolExecutor
        import threading
        
        results = {}
        successful_tasks = 0
        total_tasks = len(tasks)
        results_lock = threading.Lock()
        
        def interview_task(task: Dict[str, Any]):
            """单个访谈任务"""
            nonlocal successful_tasks
            
            model_name = task['model_name']
            entity_id = task.get('entity_id', None)
            
            print(f"\n🚀 开始任务: {model_name}", end="")
            if entity_id:
                print(f" → {entity_id}")
            else:
                print()
            
            # 调用子类实现的interview_entity
            responses, intermediate_data = self.interview_entity(model_name, entity_id)
            
            with results_lock:
                if responses:
                    # 生成结果键
                    if entity_id:
                        result_key = f"{model_name}_{entity_id}"
                    else:
                        result_key = model_name
                    
                    results[result_key] = {
                        'model_name': model_name,
                        'entity_id': entity_id,
                        'responses': responses,
                        'intermediate_data': intermediate_data
                    }
                    successful_tasks += 1
                    
                    # 打印一致性信息
                    consistency_info = ""
                    if intermediate_data and 'overall_consistency' in intermediate_data:
                        consistency_info = f" (一致性: {intermediate_data['overall_consistency']:.1%})"
                    
                    entity_info = f" → {entity_id}" if entity_id else ""
                    print(f"✅ 完成: {model_name}{entity_info} ({len(responses)} 个回答{consistency_info})")
                    
                    # 🔧 钩子方法：子类可以重写实现即时保存
                    try:
                        self._on_task_completed(model_name, entity_id, responses, intermediate_data)
                    except Exception as e:
                        print(f"⚠️ 任务完成钩子执行失败: {e}")
                else:
                    entity_info = f" → {entity_id}" if entity_id else ""
                    print(f"❌ 失败: {model_name}{entity_info}")
        
        # 并发执行
        print(f"\n🔄 启动并行访谈: {total_tasks} 个任务，{max_workers} 个并发线程")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(interview_task, task) for task in tasks]
            # 等待所有任务完成
            for future in futures:
                future.result()
        
        return {
            'results': results,
            'total_tasks': total_tasks,
            'successful_tasks': successful_tasks,
            'success_rate': successful_tasks / total_tasks if total_tasks > 0 else 0
        }
