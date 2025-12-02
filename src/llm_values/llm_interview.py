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
    
    def __init__(self, consensus_count: int = 5, data_path: str = "data"):
        """
        Args:
            consensus_count: 每个完整问卷的重复次数（用于取众数），默认5次
            data_path: 数据路径
        """
        super().__init__(repeat_count=1, data_path=data_path, 
                        consensus_count=consensus_count)  # 传递到base
        
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
            # 单轮访谈模式
            print(f"采用单轮访谈模式")
            results = []
            question_ids = list(self.questions.get_all_questions().keys())
            
            for i, question_id in enumerate(question_ids, 1):
                print(f"  问题 {i}/{len(question_ids)}: {question_id}")
                
                # 使用基类的统一方法，传入LLM专用的系统提示词
                response = self.ask_question_with_retry(model_name, question_id, self.system_prompt)
                
                if response.raw_response is None:
                    print(f"  跳过模型 {model_name}（API调用失败）")
                    return []
                
                if response.is_valid:
                    print(f"    最终回答: {response.raw_response} -> {response.response}")
                else:
                    print(f"    无效回答: {response.raw_response} ({response.error_message})")
                
                results.append(response)
                
                # 使用基类的动态延迟
                import time
                time.sleep(self._get_dynamic_delay(model_name))
            
            return results, {}
    
    def _load_existing_interview_data(self, data_dir: Path) -> Dict:
        """
        加载已有的访谈数据（用于增量访谈）
        
        Args:
            data_dir: 数据目录
        
        Returns:
            Dict: {model_name: result_data} 格式的已有数据
        """
        existing_data = {}
        
        if not data_dir.exists():
            print(f"📝 数据目录不存在，将进行全新访谈")
            return existing_data
        
        # 查找所有访谈结果文件
        pkl_files = list(data_dir.glob("llm_interview_raw_*.pkl"))
        json_files = list(data_dir.glob("llm_interview_raw_*.json"))
        
        if not pkl_files and not json_files:
            print(f"📝 未发现已有数据，将进行全新访谈")
            return existing_data
        
        # 优先使用最新的pkl文件
        if pkl_files:
            latest_file = max(pkl_files, key=lambda x: x.stat().st_mtime)
            print(f"✅ 发现已有访谈数据: {latest_file.name}")
            
            try:
                import pickle
                with open(latest_file, 'rb') as f:
                    data = pickle.load(f)
                
                # 处理统一格式: {metadata: {...}, results: [...]}
                if isinstance(data, dict) and 'results' in data:
                    for result in data.get('results', []):
                        model_name = result.get('model_name', '')
                        if model_name and result.get('valid_responses', 0) > 0:
                            existing_data[model_name] = result
                    
                    print(f"✅ 加载了 {len(existing_data)} 个模型的已有数据")
                    print(f"   - 数据格式: 统一格式（Stage1）")
                    print(f"   - 模型列表: {list(existing_data.keys())}")
                else:
                    print(f"⚠️ 数据格式不符合预期，将重新访谈")
                    
            except Exception as e:
                print(f"⚠️ 加载已有数据失败: {e}")
                print(f"   将进行全新访谈")
        
        return existing_data
    
    def _get_completed_models(self, existing_data: Dict) -> set:
        """
        从已有数据中提取已完成的模型列表
        
        Args:
            existing_data: _load_existing_interview_data返回的字典
        
        Returns:
            set: 已完成模型名称的集合
        """
        return set(existing_data.keys())
    
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
                # 检查是否有有效数据
                if isinstance(model_data, dict) and 'responses' in model_data:
                    responses = model_data['responses']
                    valid_count = sum(1 for r in responses if r.is_valid)
                    if valid_count > 0:
                        # 构建标准result格式
                        unique_results[model_name] = {
                            'model_name': model_name,
                            'responses': responses,
                            'valid_responses': valid_count,
                            'total_questions': len(responses),
                            'success_rate': valid_count / len(responses) * 100 if responses else 0,
                            'timestamp': datetime.now().isoformat()
                        }
                elif isinstance(model_data, list):  # 直接是responses列表
                    valid_count = sum(1 for r in model_data if r.is_valid)
                    if valid_count > 0:
                        unique_results[model_name] = {
                            'model_name': model_name,
                            'responses': model_data,
                            'valid_responses': valid_count,
                            'total_questions': len(model_data),
                            'success_rate': valid_count / len(model_data) * 100 if model_data else 0,
                            'timestamp': datetime.now().isoformat()
                        }
        
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
            completed_models = self._get_completed_models(existing_data)
            
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
    
    def save_results(self, results: Dict[str, Any], output_dir: str = None, use_unified_format: bool = True) -> str:
        """
        保存LLM访谈结果
        
        Args:
            results: 访谈结果字典
            output_dir: 输出目录
            use_unified_format: 是否使用统一格式（默认True）
            
        Returns:
            保存文件路径
        """
        if use_unified_format:
            return self._save_unified_format(results, output_dir)
        else:
            return self._save_legacy_format(results, output_dir)
    
    def _save_unified_format(self, results: Dict[str, Any], output_dir: str = None) -> str:
        """使用统一数据格式保存"""
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
                    "valid_responses": sum(1 for r in model_responses if r.is_valid),
                    "success_rate": sum(1 for r in model_responses if r.is_valid) / len(model_responses) * 100 if model_responses else 0,
                    "responses": []
                }
                
                # 转换responses
                for response in model_responses:
                    entity_result["responses"].append({
                        "question_id": response.question_id,
                        "raw_response": response.raw_response,
                        "processed_response": response.response,
                        "is_valid": response.is_valid,
                        "error_message": response.error_message
                    })
                
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
    
    def _save_legacy_format(self, results: Dict[str, Any], output_dir: str = None) -> str:
        """保存LLM访谈结果 - 旧格式（向后兼容）"""
        if output_dir is None:
            output_dir = self.data_path / "llm_values" / "llm_responses"  # 使用独立目录
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 转换结果为DataFrame格式
        if 'results' in results:
            all_responses = []
            
            for model_name, model_results in results['results'].items():
                for response in model_results:
                    # 将LLMResponse对象转换为字典
                    if hasattr(response, '__dict__'):
                        response_dict = response.__dict__.copy()
                    else:
                        response_dict = response
                    
                    # 确保有model_name
                    response_dict['model_name'] = model_name
                    all_responses.append(response_dict)
            
            if all_responses:
                # 转换为DataFrame（长格式）
                df_long = pd.DataFrame(all_responses)
                
                # 保存长格式数据（原始格式）
                long_file = output_path / f"llm_interview_responses_long_{timestamp}.pkl"
                df_long.to_pickle(long_file)
                
                # 转换为宽格式：每行一个模型，每列一个问题
                if 'question_id' in df_long.columns and 'response' in df_long.columns:
                    pivot_df = df_long.pivot_table(
                        index='model_name', 
                        columns='question_id', 
                        values='response', 
                        aggfunc='first'
                    ).reset_index()
                    
                    # 添加必要的元数据列
                    pivot_df['data_source'] = 'LLM'
                    pivot_df['entity_id'] = pivot_df['model_name']
                    
                    # 保存宽格式数据（用于后续PCA分析）
                    wide_file = output_path / f"llm_interview_responses_wide_{timestamp}.pkl"
                    pivot_df.to_pickle(wide_file)
                    
                    print(f"✅ LLM访谈结果已保存（旧格式）:")
                    print(f"   📊 长格式数据: {long_file}")
                    print(f"   📊 宽格式数据: {wide_file}")
                    print(f"   📈 数据形状: {pivot_df.shape}")
                    print(f"   🤖 包含模型: {list(pivot_df['model_name'])}")
                    print(f"   ❓ 包含问题: {[col for col in pivot_df.columns if col in self.iv_qns]}")
                    
                    return str(wide_file)  # 返回宽格式文件路径
        
        # 如果转换失败，使用基类方法
        return super().save_results(results, output_dir)


def main():
    """主函数 - 测试新架构"""
    print("🔄 使用新架构运行LLM访谈...")
    
    # 创建访谈对象 - 默认5次重复取众数
    interview = LLMInterview(repeat_count=5)
    
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
