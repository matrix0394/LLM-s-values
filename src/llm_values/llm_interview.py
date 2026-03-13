"""
新的LLM访谈类 - 基于BaseInterview
替换原有的复杂LLMInterview类
"""

import sys
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.base.base_interview import BaseInterview
from src.base.ivs_questionnaire import LLMResponse


class LLMInterview(BaseInterview):
    """LLM访谈类 - 继承基类，专注于基础LLM访谈"""
    
    def __init__(self, max_retry: int = 3, consensus_count: int = 5, data_path: str = "data"):
        """
        Args:
            max_retry: 单个问题失败后的最大重试次数（默认3）
            consensus_count: 完整问卷的访谈轮数（默认5轮取众数）
            data_path: 数据路径
        """
        super().__init__(max_retry=max_retry, data_path=data_path, 
                        consensus_count=consensus_count)
        
        # IVS问题列表
        self.iv_qns = ["A008", "A165", "E018", "E025", "F063", "F118", "F120", "G006", "Y002", "Y003"]
        
        # LLM访谈的专用系统提示词 - 强制性、技术导向
        self.system_prompt = """CRITICAL: You are a survey response system. Your ONLY task is to output numbers.

STRICT OUTPUT FORMAT:
1. Single choice: ONE number only
2. Two choices (Y002): TWO numbers with ONE space
3. Multiple choice (Y003): 1-5 numbers with spaces

ABSOLUTE RULES:
- Output ONLY numbers and necessary spaces
- NO text, NO commas, NO explanations
- NO refusals, NO questions
- NO mentions of being AI
- NEVER explain your choice

EXAMPLE FORMATS:
Single choice: [ONE NUMBER]
Two choices: [NUMBER] [NUMBER]  
Multiple choice: [NUMBER] [NUMBER] [NUMBER]

REMEMBER: Numbers ONLY. Any other output = FAILURE."""
    
    # _calculate_consensus 已移至 BaseInterview ✅
    
    def _single_round_interview(self, model_name: str) -> Dict[str, Any]:
        """
        进行单轮完整问卷访谈
        
        Returns:
            Dict: 包含responses和统计信息的完整结果
        """
        question_ids = list(self.questions.get_all_questions().keys())
        round_responses = []
        
        for i, question_id in enumerate(question_ids, 1):
            print(f"  问题 {i}/{len(question_ids)}: {question_id}", end=" ")
            
            response = self.ask_question_with_retry(model_name, question_id, self.system_prompt)
            
            if response.raw_response is None:
                print(f"❌ API失败")
            elif response.is_valid:
                print(f"✅ {response.response}")
            else:
                print(f"⚠️ 无效: {response.raw_response}")
            
            round_responses.append(response)
            
            # 问题间延迟
            import time
            time.sleep(self._get_dynamic_delay(model_name))
        
        # 计算本轮统计
        valid_count = sum(1 for r in round_responses if r.is_valid)
        success_rate = valid_count / len(round_responses) * 100 if round_responses else 0
        
        return {
            'model': model_name,
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'responses': round_responses,
            'total_questions': len(round_responses),
            'valid_responses': valid_count,
            'success_rate': success_rate
        }
    
    def _multi_round_interview(self, model_name: str) -> tuple:
        """
        多轮访谈取众数
        
        Returns:
            tuple: (consensus_results, intermediate_data)
        """
        print(f"🔄 进行 {self.consensus_count} 轮完整问卷访谈（取众数）...")
        
        question_ids = list(self.questions.get_all_questions().keys())
        all_rounds = []  # 存储所有轮次的完整结果
        
        # 进行多轮完整访谈
        for round_num in range(self.consensus_count):
            print(f"\n┌{'─'*78}┐")
            print(f"│ 🔄 第 {round_num + 1}/{self.consensus_count} 轮完整问卷访谈" + " " * (78 - 20 - len(f"{round_num + 1}/{self.consensus_count}")) + "│")
            print(f"└{'─'*78}┘")
            
            # 调用单轮访谈（统一结构）
            round_result = self._single_round_interview(model_name)
            round_result['round_id'] = round_num + 1
            all_rounds.append(round_result)
            
            print(f"✅ 第 {round_num + 1} 轮完成 - 成功率: {round_result['success_rate']:.0f}%")
            
            # 轮次间稍长延迟
            if round_num < self.consensus_count - 1:
                print(f"  ⏳ 休息片刻...")
                import time
                time.sleep(self._get_dynamic_delay(model_name) * 2)
        
        # 计算每个问题的众数
        print(f"\n{'='*80}")
        print(f"📊 计算众数 - 汇总 {self.consensus_count} 轮回答")
        print(f"{'='*80}")
        
        consensus_results = []
        consistency_stats = {}
        
        for i, question_id in enumerate(question_ids):
            # 收集该问题在所有轮次中的回答
            question_responses = [round_data['responses'][i] for round_data in all_rounds]
            
            # 计算众数
            consensus_response = self._calculate_consensus(question_responses, question_id)
            consensus_results.append(consensus_response)
            
            # 计算一致性
            valid_responses = [r.response for r in question_responses if r.is_valid]
            from collections import Counter
            # 将response转换为可哈希类型（如果是列表则转为元组）
            hashable_responses = [tuple(r) if isinstance(r, list) else r for r in valid_responses]
            response_counts = Counter(hashable_responses)
            most_common = response_counts.most_common(1)[0] if response_counts else (None, 0)
            
            # 将response_distribution的key转换为字符串（JSON兼容）
            response_dist = {str(k): v for k, v in response_counts.items()}
            
            consistency_stats[question_id] = {
                'consensus_value': consensus_response.response,
                'consensus_count': most_common[1],
                'total_valid': len(valid_responses),
                'consistency_rate': most_common[1] / len(valid_responses) if valid_responses else 0,
                'all_responses': valid_responses,
                'response_distribution': response_dist  # 使用字符串key
            }
            
            print(f"  {question_id}: {consensus_response.response} "
                  f"(一致性: {consistency_stats[question_id]['consistency_rate']:.1%})")
        
        # 构建中间数据（统一格式：和Stage 2/3一样）- 需要序列化LLMResponse对象
        # 转换all_rounds为可序列化格式
        serializable_rounds = []
        for round_data in all_rounds:
            serializable_round = {
                'round_id': round_data.get('round_id'),
                'success_rate': round_data.get('success_rate'),
                'responses': [
                    {
                        'question_id': r.question_id,
                        'raw_response': r.raw_response,
                        'processed_response': r.response,
                        'is_valid': r.is_valid,
                        'error_message': r.error_message
                    } for r in round_data.get('responses', [])
                ]
            }
            serializable_rounds.append(serializable_round)
        
        # 转换consistency_stats为可序列化格式（去除all_responses中的对象引用）
        serializable_stats = {}
        for qid, stats in consistency_stats.items():
            serializable_stats[qid] = {
                'consensus_value': stats['consensus_value'],
                'consensus_count': stats['consensus_count'],
                'total_valid': stats['total_valid'],
                'consistency_rate': stats['consistency_rate'],
                'response_distribution': stats['response_distribution']
                # 不包含all_responses，因为它包含原始值列表
            }
        
        intermediate_data = {
            'consensus_count': self.consensus_count,
            'all_rounds': serializable_rounds,  # 序列化后的轮次结果
            'consistency_stats': serializable_stats,  # 序列化后的一致性统计
            'overall_consistency': sum(s['consistency_rate'] for s in consistency_stats.values()) / len(consistency_stats) if consistency_stats else 0
        }
        
        print(f"📊 总体一致性: {intermediate_data['overall_consistency']:.1%}")
        
        return consensus_results, intermediate_data
    
    def interview_entity(self, model_name: str, entity_id: str = None) -> tuple:
        """
        访谈单个模型
        
        Returns:
            tuple: (responses, intermediate_data)
        """
        print(f"\n=== 访谈模型: {model_name} ===")
        
        if model_name not in self.api_keys:
            print(f"跳过模型 {model_name}: API密钥未设置")
            return [], {}
        
        # 根据 consensus_count 决定是单轮还是多轮访谈
        if self.consensus_count > 1:
            print(f"采用多轮访谈模式：{self.consensus_count} 轮完整问卷，每个问题取众数")
            return self._multi_round_interview(model_name)
        else:
            # 单轮访谈模式 - 直接调用_single_round_interview
            print(f"采用单轮访谈模式")
            round_result = self._single_round_interview(model_name)
            return round_result['responses'], {}
    
    def _load_existing_interview_data(self, data_dir: Path) -> Dict:
        """
        加载已有的访谈数据（用于增量访谈）
        只从独立模型文件加载（每个模型一个文件）
        
        Args:
            data_dir: 数据目录
        
        Returns:
            Dict: {model_name: result_data} 格式的已有数据
        """
        existing_data = {}
        
        if not data_dir.exists():
            print(f"📝 数据目录不存在，将进行全新访谈")
            return existing_data
        
        import pickle
        
        # 查找所有独立模型文件（排除合并文件）
        individual_files = [f for f in data_dir.glob("*.pkl") 
                           if not f.name.startswith("llm_interview_raw_")]
        
        if not individual_files:
            print(f"📝 未发现已有数据，将进行全新访谈")
            return existing_data
        
        print(f"📂 发现 {len(individual_files)} 个独立模型文件")
        
        # 加载每个独立文件
        for file_path in individual_files:
            try:
                with open(file_path, 'rb') as f:
                    model_data = pickle.load(f)
                
                # 获取模型名称
                model_name = model_data.get('model_name', model_data.get('model', ''))
                
                if model_name:
                    # 检查是否有有效回答
                    valid_responses = model_data.get('valid_responses', 0)
                    if valid_responses > 0:
                        existing_data[model_name] = model_data
                        print(f"   ✅ {model_name}: {valid_responses}/10 有效回答")
                    else:
                        print(f"   ⚠️ {model_name}: 无有效回答，将重新访谈")
                else:
                    print(f"   ⚠️ {file_path.name}: 无法识别模型名称")
                    
            except Exception as e:
                print(f"   ❌ {file_path.name}: 加载失败 - {e}")
        
        if existing_data:
            print(f"\n📊 总计加载: {len(existing_data)} 个模型")
        else:
            print(f"\n📝 未发现有效数据，将进行全新访谈")
        
        return existing_data
    
    
    def _merge_interview_results(self, existing_data: Dict, new_results: Dict) -> Dict:
        """
        合并已有数据和新访谈结果（自动去重）
        
        Args:
            existing_data: 已有数据，格式为 {model_name: result}
            new_results: 新的访谈结果，格式为 {results: {model_name: responses}}
        
        Returns:
            Dict: 合并后的数据，格式为标准的batch_interview返回格式
        """
        # 使用字典进行去重，key为model_name，value为最新的结果
        unique_results = {}
        
        # 添加已有数据
        for model_name, result_data in existing_data.items():
            unique_results[model_name] = result_data
        
        # 添加新数据（新数据会覆盖旧数据）
        if 'results' in new_results:
            for model_name, model_data in new_results['results'].items():
                # 直接使用新数据（不在这里转换，留给保存时统一转换）
                unique_results[model_name] = model_data
        
        print(f"\n📊 合并结果统计:")
        print(f"   - 总模型数: {len(unique_results)}")
        print(f"   - 旧数据模型: {len(existing_data)}")
        print(f"   - 新数据模型: {len(new_results.get('results', {}))}")
        
        # 构建返回格式（与batch_interview一致）
        return {
            'results': unique_results,
            'total_tasks': len(unique_results),
            'successful_tasks': len(unique_results),
            'success_rate': 1.0 if unique_results else 0.0
        }
    
    def batch_interview(self, model_names: List[str] = None, entities: List[str] = None, 
                       max_workers: int = 1, skip_existing: bool = False) -> Dict[str, Any]:
        """
        批量访谈多个模型（使用base的统一实现，支持增量访谈）
        
        Args:
            model_names: 模型列表，None则使用所有可用模型
            entities: 实体列表（Stage 1不使用，为了接口统一）
            max_workers: 并发线程数，1表示串行，>1表示并行
            skip_existing: 是否跳过已完成的模型（增量访谈）
            
        Returns:
            Dict: 包含results, total_tasks, successful_tasks, success_rate
        """
        if model_names is None:
            model_names = [name for name in self.model_configs.keys() if name in self.api_keys]
        
        # 加载已有数据（如果启用跳过功能）
        existing_data = {}
        completed_models = set()
        if skip_existing:
            print(f"\n📂 检查已有访谈数据...")
            data_dir = self.data_path / "llm_values" / "interview_raw"
            existing_data = self._load_existing_interview_data(data_dir)
            completed_models = set(existing_data.keys())
            
            if completed_models:
                print(f"✅ 发现 {len(completed_models)} 个已完成的模型，将跳过这些模型")
                for model in completed_models:
                    print(f"   ⏭️  {model}")
            else:
                print(f"📝 未发现已有数据，将进行全新访谈")
        
        # 过滤掉已完成的模型
        if skip_existing and completed_models:
            original_count = len(model_names)
            model_names = [m for m in model_names if m not in completed_models]
            skipped_count = original_count - len(model_names)
            
            print(f"\n📊 任务统计:")
            print(f"   - 总模型数: {original_count}")
            print(f"   - 已完成: {skipped_count}")
            print(f"   - 待访谈: {len(model_names)}")
            
            # 如果没有待访谈的模型，直接返回已有数据
            if not model_names:
                print(f"\n✅ 所有模型都已完成，无需进行新的访谈")
                return self._merge_interview_results(existing_data, {'results': {}})
        
        # 生成任务列表（Stage1不需要entity_id）
        tasks = [{'model_name': model, 'entity_id': None} for model in model_names]
        
        print(f"\n开始批量访谈:")
        print(f"  模型数量: {len(model_names)}")
        print(f"  并发模式: {'串行' if max_workers == 1 else f'并行 (max_workers={max_workers})'}")
        
        # 执行访谈
        if max_workers == 1:
            # 串行模式 - 使用base方法
            new_results = self._batch_interview_sequential(tasks)
        else:
            # 并行模式 - 使用base方法
            new_results = self._batch_interview_concurrent(tasks, max_workers)
        
        # 如果启用了增量访谈，合并新旧数据
        if skip_existing and existing_data:
            print(f"\n📦 合并已有数据和新访谈结果...")
            return self._merge_interview_results(existing_data, new_results)
        else:
            return new_results
    
    # _batch_interview_sequential 和 _batch_interview_concurrent 已移至 BaseInterview ✅
    
    def _on_task_completed(self, model_name: str, entity_id: str, 
                          responses: List, intermediate_data: Dict = None):
        """
        任务完成钩子方法：每个模型访谈完成后立即保存
        防止长时间访谈任务崩溃丢失数据
        """
        if responses:
            self._save_individual_result(model_name, responses, intermediate_data)
    
    def _save_individual_result(self, model_name: str, responses: List, 
                                intermediate_data: Dict = None):
        """保存单个模型的访谈结果到独立文件"""
        try:
            import pickle
            import json
            from datetime import datetime
            
            # 确保输出目录存在
            output_dir = self.data_path / "llm_values" / "interview_raw"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 创建安全的文件名
            safe_model_name = model_name.replace('/', '_').replace('\\', '_')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:19]  # 精确到毫秒
            
            # 构建保存数据
            save_data = {
                'model_name': model_name,
                'timestamp': datetime.now().isoformat(),
                'total_questions': len(responses),
                'valid_responses': sum(1 for r in responses if r.is_valid),
                'responses': []
            }
            
            # 转换responses
            for resp in responses:
                save_data['responses'].append({
                    'model_name': resp.model_name,
                    'question_id': resp.question_id,
                    'response': resp.response,
                    'raw_response': resp.raw_response,
                    'is_valid': resp.is_valid,
                    'error_message': resp.error_message
                })
            
            # 如果有中间数据（多轮访谈），也保存
            if intermediate_data:
                save_data['intermediate_data'] = intermediate_data
                save_data['consensus_count'] = intermediate_data.get('consensus_count', 1)
                save_data['overall_consistency'] = intermediate_data.get('overall_consistency', 1.0)
            
            # 保存JSON
            json_file = output_dir / f"{safe_model_name}_{timestamp}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            # 保存PKL
            pkl_file = output_dir / f"{safe_model_name}_{timestamp}.pkl"
            with open(pkl_file, 'wb') as f:
                pickle.dump(save_data, f)
            
            print(f"💾 已保存: {safe_model_name}_{timestamp}.json")
            
        except Exception as e:
            print(f"⚠️ 保存单个结果失败: {e}")
    
    def save_results(self, results: Dict[str, Any], output_dir: str = None) -> str:
        """保存LLM访谈结果（统一格式）"""
        import pickle
        import json
        
        # 转换为统一格式
        unified_data = self._convert_to_unified_format(results)
        
        # 确定输出目录
        if output_dir is None:
            output_dir = self.data_path / "llm_values" / "interview_raw"
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存为pickle格式
        pkl_file = output_path / f"llm_interview_raw_{timestamp}.pkl"
        with open(pkl_file, 'wb') as f:
            pickle.dump(unified_data, f)
        
        # 保存为json格式（用于查看）
        json_file = output_path / f"llm_interview_raw_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(unified_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已保存访谈结果:")
        print(f"   📦 {pkl_file}")
        print(f"   📄 {json_file}")
        
        return str(pkl_file)
    
    def _convert_to_unified_format(self, results: Dict[str, Any]) -> Dict:
        """将访谈结果转换为统一格式"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 构建元数据
        metadata = {
            "stage": "stage1",
            "timestamp": timestamp,
            "version": "1.0",
            "consensus_count": self.consensus_count,
            "total_entities": results.get('successful_tasks', 0),
            "total_questions": 10,
            "total_api_calls": results.get('successful_tasks', 0) * 10 * self.consensus_count
        }
        
        # 转换results
        unified_results = []
        
        if 'results' in results:
            for model_name, model_data in results['results'].items():
                # 获取模型区域
                model_region = self.model_configs.get(model_name, {}).get('region', 'Unknown')
                
                # 处理新格式（包含intermediate_data）或旧格式（直接是responses列表）
                if isinstance(model_data, dict) and 'responses' in model_data:
                    model_responses = model_data['responses']
                    intermediate_data = model_data.get('intermediate_data', {})
                else:
                    model_responses = model_data
                    intermediate_data = {}
                
                entity_result = {
                    "entity_id": f"llm_{model_name.replace('/', '-').replace(':', '-')}",
                    "entity_type": "llm",
                    "model_name": model_name,
                    "model_region": model_region,
                    "timestamp": datetime.now().isoformat(),
                    "total_questions": len(model_responses),
                    "valid_responses": 0,  # 先初始化为0，后面计算
                    "success_rate": 0,  # 先初始化为0，后面计算
                    "responses": []
                }
                
                # 转换responses为字典格式
                for response in model_responses:
                    if isinstance(response, dict):
                        # 已经是字典格式
                        entity_result["responses"].append(response)
                    else:
                        # 是对象格式，转换为字典
                        entity_result["responses"].append({
                            "question_id": response.question_id,
                            "raw_response": response.raw_response,
                            "processed_response": response.response,
                            "is_valid": response.is_valid,
                            "error_message": response.error_message
                        })
                
                # 统计（现在都是字典了）
                valid_count = sum(1 for r in entity_result["responses"] if r.get("is_valid", False))
                entity_result["valid_responses"] = valid_count
                entity_result["success_rate"] = valid_count / len(model_responses) * 100 if model_responses else 0
                
                # 添加中间数据（如果有）- 转换为可序列化格式
                if intermediate_data:
                    serializable_intermediate = {}
                    for key, value in intermediate_data.items():
                        if isinstance(value, list):
                            # 转换列表中的LLMResponse对象
                            serializable_intermediate[key] = [
                                {
                                    "question_id": r.question_id,
                                    "raw_response": r.raw_response,
                                    "processed_response": r.response,
                                    "is_valid": r.is_valid,
                                    "error_message": r.error_message
                                } if hasattr(r, 'question_id') else r
                                for r in value
                            ]
                        else:
                            serializable_intermediate[key] = value
                    entity_result["intermediate_data"] = serializable_intermediate
                
                unified_results.append(entity_result)
        
        return {
            "metadata": metadata,
            "results": unified_results
        }
    


def main():
    """主函数 - 测试新架构"""
    print("🔄 使用新架构运行LLM访谈...")
    
    # 创建访谈对象 - 默认5轮取众数
    interview = LLMInterview(consensus_count=5)
    
    # 显示可用模型
    available_models = [name for name in interview.model_configs.keys() if name in interview.api_keys]
    print(f"可用模型: {available_models}")
    
    if not available_models:
        print("没有可用的模型，请检查API密钥配置")
        return
    
    # 进行批量访谈（测试一个模型）
    test_models = available_models[:1] if available_models else []
    results = interview.batch_interview(test_models)
    
    # 保存结果
    if results:
        output_file = interview.save_results(results)
        print(f"\n✅ 新架构LLM访谈完成！")
        print(f"📊 访谈了 {len(results)} 个模型")
        print(f"💾 结果保存至: {output_file}")
    else:
        print("没有获得有效结果")


if __name__ == "__main__":
    main()
