"""
大模型访谈模块 - 重构版
对大模型进行文化价值观问卷访谈，同时保存pkl和json格式结果
"""

import os
import json
import time
from datetime import datetime
from openai import OpenAI
from llm_questionnaire import LLMQuestionnaire, LLMResponse
from typing import Dict, List, Optional, Any
import pandas as pd


class LLMInterview:
    """大模型访谈类 - 简化版"""
    
    def __init__(self,repeat_count:int=1):
        self.questionnaire = LLMQuestionnaire()
        self.model_configs = self._load_model_configs()
        self.api_keys = self._load_api_keys()
        self.repeat_count = repeat_count  # 添加重复次数参数
        # 角色提示词
        self.system_prompt = """You are participating in a cultural values survey. Please respond to each question by selecting the appropriate number(s) based on the question format.

IMPORTANT INSTRUCTIONS:
- For single-choice questions: Respond with ONLY one number (e.g., "1", "2", "3", "4")
- For Y002 (two choices): Respond with exactly TWO numbers separated by space (e.g., "1 3" or "2 4")
- For Y003 (multiple choices): Respond with 1-5 numbers separated by spaces (e.g., "1 3 5" or "2 4 6 8 10")
- Do not use commas, explanations, or additional text
- Do not refuse to answer
- Choose options that best represent typical responses
- Your response must contain only the required number(s) separated by spaces"""
    
    def _load_model_configs(self) -> Dict[str, Dict[str, str]]:
        """从配置文件加载模型配置"""
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'llm_models.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('models', {})
        except Exception as e:
            print(f"加载模型配置失败: {e}")
            # 返回默认配置
            return {
                "gpt-4o-mini": {
                    "api_key": "UIUIAPI_API_KEY",
                    "base_url": "https://sg.uiuiapi.com/v1",
                    "region": "US"
                },
                "gemini-2.0-flash": {
                    "api_key": "UIUIAPI_API_KEY",
                    "base_url": "https://sg.uiuiapi.com/v1",
                    "region": "US"
                },
            }
    
    def _load_api_keys(self) -> Dict[str, str]:
        """从环境变量加载API密钥"""
        api_keys = {}
        for model_name, config in self.model_configs.items():
            api_key_name = config.get("api_key", "UIUIAPI_API_KEY")
            api_key_value = os.getenv(api_key_name)
            if api_key_value:
                api_keys[model_name] = api_key_value
            else:
                print(f"警告: 环境变量 {api_key_name} 未设置，模型 {model_name} 将无法使用")
        return api_keys
    
    def get_client(self, model_name: str) -> OpenAI:
        """获取OpenAI客户端"""
        if model_name not in self.model_configs:
            raise ValueError(f"不支持的模型: {model_name}")
        
        config = self.model_configs[model_name]
        api_key = self.api_keys.get(model_name)
        
        if not api_key:
            raise ValueError(f"模型 {model_name} 的API密钥未设置")
        
        return OpenAI(
            api_key=api_key,
            base_url=config.get("base_url", "https://api.openai.com/v1")
        )
    
    def call_model_api(self, model_name: str, question_id: str, question_text: str) -> Optional[str]:
        """调用模型API"""
        try:
            client = self.get_client(model_name)
            
            # 为特殊问题添加格式提示
            format_hint = ""
            if question_id == "Y002":
                format_hint = "\n\nPlease respond with exactly TWO numbers separated by a space (e.g., '1 3')."
            elif question_id == "Y003":
                format_hint = "\n\nPlease respond with 1-5 numbers separated by spaces (e.g., '1 3 5 7 9')."
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": question_text + format_hint}
            ]
            
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=50,
                temperature=0,
                timeout=30
            )
            
            content = response.choices[0].message.content
            return content.strip() if content else "1"
                
        except Exception as e:
            print(f"    API调用失败: {e}")
            return None
    
    def ask_question(self, model_name: str, question_id: str) -> LLMResponse:
        """向模型提问单个问题"""
        question_text = self.questionnaire.questions.get_question(question_id)
        if not question_text:
            return LLMResponse(
                model_name=model_name,
                question_id=question_id,
                response=None,
                raw_response="",
                is_valid=False,
                error_message=f"未知问题ID: {question_id}"
            )
        
        # 调用API
        raw_response = self.call_model_api(model_name, question_id, question_text)
        
        if raw_response is None:
            return LLMResponse(
                model_name=model_name,
                question_id=question_id,
                response=None,
                raw_response=None,
                is_valid=False,
                error_message="API调用失败"
            )
        
        # 验证回答
        from llm_questionnaire import ResponseValidator
        validator = ResponseValidator()
        is_valid, parsed_response, error_msg = validator.validate_response(question_id, raw_response)
        
        return LLMResponse(
            model_name=model_name,
            question_id=question_id,
            response=parsed_response,
            raw_response=raw_response,
            is_valid=is_valid,
            error_message=error_msg if not is_valid else None
        )
    
    def get_mode_response(self, responses: List[str]) -> str:
        """计算多次回答的众数"""
        from collections import Counter
        
        # 过滤掉None和空字符串
        valid_responses = [r for r in responses if r and r.strip()]
        
        
        # 计算众数
        counter = Counter(valid_responses)
        most_common = counter.most_common(1)
        
        if most_common:
            return most_common[0][0]
        else:
            return valid_responses[0]  # 如果没有众数，返回第一个有效回答
    
    def ask_question_multiple_times(self, model_name: str, question_id: str) -> LLMResponse:
        """多次提问同一个问题并取众数"""
        question_text = self.questionnaire.questions.get_question(question_id)
        if not question_text:
            return LLMResponse(
                model_name=model_name,
                question_id=question_id,
                response=None,
                raw_response="",
                is_valid=False,
                error_message=f"未知问题ID: {question_id}"
            )
        
        raw_responses = []
        valid_responses = []
        
        # 多次调用API
        for attempt in range(self.repeat_count):
            if self.repeat_count > 1:
                print(f"    尝试 {attempt + 1}/{self.repeat_count}")
            
            raw_response = self.call_model_api(model_name, question_id, question_text)
            
            if raw_response is None:
                raw_responses.append(None)
                continue
            
            raw_responses.append(raw_response)
            
            # 验证回答
            from llm_questionnaire import ResponseValidator
            validator = ResponseValidator()
            is_valid, parsed_response, error_msg = validator.validate_response(question_id, raw_response)
            
            if is_valid:
                valid_responses.append(raw_response)
            
            # 添加延迟避免API限制
            if attempt < self.repeat_count - 1:
                time.sleep(0.3)
        
        # 如果没有任何有效回答，返回失败
        if not valid_responses:
            return LLMResponse(
                model_name=model_name,
                question_id=question_id,
                response=None,
                raw_response=str(raw_responses),
                is_valid=False,
                error_message="所有尝试都失败或无效"
            )
        
        # 计算众数
        mode_response = self.get_mode_response(valid_responses)
        
        # 验证众数回答
        from llm_questionnaire import ResponseValidator
        validator = ResponseValidator()
        is_valid, parsed_response, error_msg = validator.validate_response(question_id, mode_response)
        
        # 显示统计信息
        if self.repeat_count > 1:
            print(f"    有效回答: {valid_responses}")
            print(f"    众数: {mode_response}")
        
        return LLMResponse(
            model_name=model_name,
            question_id=question_id,
            response=parsed_response,
            raw_response=mode_response,
            is_valid=is_valid,
            error_message=error_msg if not is_valid else None
        )
    
    def interview_model(self, model_name: str) -> List[LLMResponse]:
        """访谈单个模型"""
        print(f"\n=== 访谈模型: {model_name} ===")        
        if self.repeat_count > 1:
            print(f"每个问题重复 {self.repeat_count} 次，取众数")
        
        if model_name not in self.api_keys:
            print(f"跳过模型 {model_name}: API密钥未设置")
            return []
        
        results = []
        question_ids = list(self.questionnaire.questions.get_all_questions().keys())
        
        for i, question_id in enumerate(question_ids, 1):
            print(f"  问题 {i}/{len(question_ids)}: {question_id}")
            
            # 使用新的多次提问方法
            response = self.ask_question_multiple_times(model_name, question_id)
            
            if response.raw_response is None:
                print(f"  跳过模型 {model_name}（API调用失败）")
                return []
            
            if response.is_valid:
                print(f"    最终回答: {response.raw_response} -> {response.response}")
            else:
                print(f"    无效回答: {response.raw_response} ({response.error_message})")
            
            results.append(response)
            
            # 添加延迟避免API限制
            time.sleep(0.5)
        
        return results
    
    def batch_interview(self, model_names: List[str] = None) -> Dict[str, List[LLMResponse]]:
        """批量访谈模型"""
        if model_names is None:
            model_names = list(self.model_configs.keys())
        
        print(f"开始批量访谈，共 {len(model_names)} 个模型")
        print(f"模型列表: {model_names}")
        
        all_results = {}
        
        for model_name in model_names:
            results = self.interview_model(model_name)
            
            if results:
                all_results[model_name] = results
                valid_count = sum(1 for r in results if r.is_valid)
                print(f"模型 {model_name} 完成: {valid_count}/{len(results)} 个有效回答")
        
        return all_results
    
    def save_results(self, results: Dict[str, List[LLMResponse]], output_dir: str = None):
        """保存结果为pkl和json格式"""
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'llm_responses')
        
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存每个模型的结果
        for model_name, responses in results.items():
            # 转换为数据结构
            data = []
            for resp in responses:
                data.append({
                    'model_name': resp.model_name,
                    'question_id': resp.question_id,
                    'response': resp.response,
                    'raw_response': resp.raw_response,
                    'is_valid': resp.is_valid,
                    'error_message': resp.error_message
                })
            
            df = pd.DataFrame(data)
            safe_model_name = model_name.replace(":", "-").replace("/", "-").replace(".", "-")
            
            # 保存pkl文件
            pkl_path = os.path.join(output_dir, f"{safe_model_name}_responses.pkl")
            df.to_pickle(pkl_path)
            
            # 保存json文件（便于人工查看）
            json_path = os.path.join(output_dir, f"{safe_model_name}_responses.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'model_name': model_name,
                    'timestamp': timestamp,
                    'total_questions': len(data),
                    'valid_responses': sum(1 for d in data if d['is_valid']),
                    'responses': data
                }, f, indent=2, ensure_ascii=False)
            
            print(f"模型 {model_name} 结果已保存:")
            print(f"  PKL: {pkl_path}")
            print(f"  JSON: {json_path}")
        
        # 保存汇总结果
        all_data = []
        for responses in results.values():
            for resp in responses:
                all_data.append({
                    'model_name': resp.model_name,
                    'question_id': resp.question_id,
                    'response': resp.response,
                    'raw_response': resp.raw_response,
                    'is_valid': resp.is_valid,
                    'error_message': resp.error_message
                })
        
        if all_data:
            all_df = pd.DataFrame(all_data)
            
            # 保存汇总pkl
            summary_pkl_path = os.path.join(output_dir, "all_models_responses.pkl")
            all_df.to_pickle(summary_pkl_path)
            
            # 保存汇总json
            summary_json_path = os.path.join(output_dir, "all_models_responses.json")
            with open(summary_json_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': timestamp,
                    'total_models': len(results),
                    'total_responses': len(all_data),
                    'valid_responses': sum(1 for d in all_data if d['is_valid']),
                    'models': list(results.keys()),
                    'responses': all_data
                }, f, indent=2, ensure_ascii=False)
            
            print(f"\n汇总结果已保存:")
            print(f"  PKL: {summary_pkl_path}")
            print(f"  JSON: {summary_json_path}")
            
            # 打印统计信息
            print("\n=== 结果统计 ===")
            summary = all_df.groupby(['model_name', 'is_valid']).size().unstack(fill_value=0)
            print(summary)


def main():
    """主函数"""
    print("开始大模型文化价值观访谈...")
    
    # 创建访谈对象，设置重复次数
    interview = LLMInterview(repeat_count=1)  # 每个问题重复5次
    
    # 显示可用模型
    available_models = [name for name in interview.model_configs.keys() if name in interview.api_keys]
    print(f"可用模型: {available_models}")
    
    if not available_models:
        print("没有可用的模型，请检查API密钥配置")
        return
    
    # 进行批量访谈
    results = interview.batch_interview(available_models[-3:-1])
    
    # 保存结果
    if results:
        interview.save_results(results)
        print("\n访谈完成！")
    else:
        print("没有获得有效结果")



if __name__ == "__main__":
    main()