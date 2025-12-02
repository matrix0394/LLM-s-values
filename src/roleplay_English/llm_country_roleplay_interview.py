"""
新的角色扮演访谈类 - 基于BaseInterview
替换原有的复杂LLMCountryRoleplayInterview类
"""

import os
import json
import pickle
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
from concurrent.futures import ThreadPoolExecutor
import threading
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.base.base_interview import BaseInterview
from src.base.ivs_questionnaire import LLMResponse
from src.base.unified_data_manager import UnifiedDataManager


class LLMCountryRoleplayInterview(BaseInterview):
    """角色扮演访谈类 - 继承基类，专注于国家角色扮演"""
    
    def __init__(self, repeat_count: int = 1, data_path: str = "data", 
                 consensus_count: int = 1):
        """
        Args:
            repeat_count: 重试次数（用于失败重试）
            data_path: 数据路径
            consensus_count: 每个问题的提问次数（用于取众数）
        """
        super().__init__(repeat_count=repeat_count, data_path=data_path, 
                        consensus_count=consensus_count)
        
        # 加载角色扮演特有的数据
        self.countries_data = self._load_countries_data()
        self.cultural_regions = self._load_cultural_regions()
        
        # 角色扮演的基础系统提示词 - 简洁客观，统一格式
        self.base_system_prompt = """You are participating in a cultural values survey. Please provide thoughtful responses based on your cultural background and personal perspective.

Please follow these guidelines:
- Answer each question with a genuine, considered response
- Choose the option that best reflects your cultural values and beliefs
- Respond as a real person from your country would

Response format:
- Single choice questions: respond with ONE number only
- Y002 (two choices): respond with TWO numbers separated by space
- Y003 (multiple choices): respond with 1-5 numbers (from 1-11) separated by spaces

Please provide meaningful answers that reflect your cultural perspective.

IMPORTANT: You are roleplaying as a typical citizen from {country}. 
Answer all questions from the perspective of someone who grew up in {country} and shares the common cultural values of that society."""
    
    def _load_countries_data(self) -> Dict:
        """加载国家数据"""
        try:
            # 修正路径：country_codes.pkl在config目录中
            # 从data_path向上找到项目根目录，然后找config目录
            current_path = self.data_path
            while current_path.name != "LLM's values" and current_path.parent != current_path:
                current_path = current_path.parent
            
            countries_path = current_path / "config" / "country_codes.pkl"
            with open(countries_path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"加载国家数据失败: {e}")
            return {}
    
    def _load_cultural_regions(self) -> Dict:
        """加载文化区域数据"""
        try:
            regions_path = Path(__file__).parent.parent.parent / 'config' / 'cultural_regions.json'
            with open(regions_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载文化区域数据失败: {e}")
            return {}
    
    def _create_country_system_prompt(self, country: str) -> str:
        """为特定国家创建系统提示词"""
        # 直接使用base_system_prompt并替换{country}占位符
        return self.base_system_prompt.format(country=country)
    
    # _calculate_consensus方法已移至BaseInterview，此处不再需要重复定义
    
    def interview_entity(self, model_name: str, entity_id: str) -> Tuple[List[LLMResponse], Dict]:
        """
        访谈单个模型扮演特定国家
        
        Returns:
            Tuple[responses, intermediate_data]:
                - responses: 最终回答（单次访谈或众数）
                - intermediate_data: 中间数据（仅多轮访谈时有）
        """
        country = entity_id  # entity_id就是国家名
        print(f"\n=== {model_name} 扮演 {country} ===")
        
        if model_name not in self.api_keys:
            print(f"跳过模型 {model_name}: API密钥未设置")
            return [], {}
        
        # 创建国家特定的系统提示词
        country_system_prompt = self._create_country_system_prompt(country)
        
        if self.consensus_count <= 1:
            # 单次访谈模式（无中间数据）
            responses = self._single_round_interview(model_name, country, country_system_prompt)
            return responses, {}
        else:
            # 多轮访谈取众数模式（包含中间数据）
            return self._multi_round_interview(model_name, country, country_system_prompt)
    
    def _single_round_interview(self, model_name: str, country: str, system_prompt: str) -> List[LLMResponse]:
        """单轮访谈"""
        results = []
        question_ids = list(self.questions.get_all_questions().keys())
        
        for i, question_id in enumerate(question_ids, 1):
            print(f"  问题 {i}/{len(question_ids)}: {question_id}")
            
            response = self.ask_question_with_retry(
                model_name, question_id, system_prompt
            )
            
            if response.raw_response is None:
                print(f"  跳过 {model_name} 扮演 {country}（API调用失败）")
                return []
            
            if response.is_valid:
                print(f"    回答: {response.raw_response} -> {response.response}")
            else:
                print(f"    无效回答: {response.raw_response} ({response.error_message})")
            
            results.append(response)
            
            # 使用基类的动态延迟
            import time
            time.sleep(self._get_dynamic_delay(model_name))
        
        return results
    
    def _single_round_interview(self, model_name: str, country: str, system_prompt: str) -> Dict[str, Any]:
        """
        进行单轮完整问卷访谈
        
        Returns:
            Dict: 包含responses和统计信息的完整结果
        """
        question_ids = list(self.questions.get_all_questions().keys())
        round_responses = []
        
        for i, question_id in enumerate(question_ids, 1):
            # 组装完整的输出行（避免高并发时输出交织）
            output_line = f"  问题 {i}/{len(question_ids)}: {question_id} "
            
            response = self.ask_question_with_retry(
                model_name, question_id, system_prompt
            )
            
            if response.raw_response is None:
                output_line += "❌ API失败"
                print(output_line)
                # API失败时返回空结果
                return {
                    'model': model_name,
                    'country': country,
                    'timestamp': __import__('datetime').datetime.now().isoformat(),
                    'responses': [],
                    'total_questions': 0,
                    'valid_responses': 0,
                    'success_rate': 0,
                    'failed': True
                }
            
            if response.is_valid:
                output_line += f"✅ {response.response}"
            else:
                output_line += f"⚠️ 无效: {response.raw_response}"
            
            # 一次性打印完整行（避免并发时被打断）
            print(output_line)
            
            round_responses.append(response)
            
            # 问题间延迟
            import time
            time.sleep(self._get_dynamic_delay(model_name))
        
        # 计算本轮统计
        valid_count = sum(1 for r in round_responses if r.is_valid)
        success_rate = valid_count / len(round_responses) * 100 if round_responses else 0
        
        return {
            'model': model_name,
            'country': country,
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'responses': round_responses,
            'total_questions': len(round_responses),
            'valid_responses': valid_count,
            'success_rate': success_rate,
            'failed': False
        }
    
    def _multi_round_interview(self, model_name: str, country: str, system_prompt: str) -> Tuple[List[LLMResponse], Dict]:
        """
        多轮访谈取众数
        
        Returns:
            Tuple[consensus_results, intermediate_data]:
                - consensus_results: 众数结果列表
                - intermediate_data: 包含所有轮次原始数据和一致性统计
        """
        print(f"🔄 进行 {self.consensus_count} 轮完整问卷访谈...")
        
        question_ids = list(self.questions.get_all_questions().keys())
        all_rounds = []  # 存储所有轮次的完整结果
        
        # 进行多轮完整访谈
        for round_num in range(self.consensus_count):
            print(f"\n┌{'─'*78}┐")
            print(f"│ 🔄 第 {round_num + 1}/{self.consensus_count} 轮完整问卷访谈" + " " * (78 - 20 - len(f"{round_num + 1}/{self.consensus_count}")) + "│")
            print(f"└{'─'*78}┘")
            
            # 调用单轮访谈（统一结构）
            round_result = self._single_round_interview(model_name, country, system_prompt)
            round_result['round_id'] = round_num + 1
            
            # 如果API失败，直接返回空结果
            if round_result.get('failed'):
                print(f"  跳过 {model_name} 扮演 {country}（API调用失败）")
                return [], {}
            
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
            
            # 计算一致性统计
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
                  f"(一致性: {consistency_stats[question_id]['consistency_rate']:.1%}, "
                  f"{consistency_stats[question_id]['consensus_count']}/{len(valid_responses)})")
        
        # 构建中间数据（统一格式：和Stage 1/3一样）
        intermediate_data = {
            'consensus_count': self.consensus_count,
            'all_rounds': all_rounds,  # 完整的轮次结果
            'consistency_stats': consistency_stats,
            'overall_consistency': sum(s['consistency_rate'] for s in consistency_stats.values()) / len(consistency_stats) if consistency_stats else 0
        }
        
        print(f"\n📊 总体一致性: {intermediate_data['overall_consistency']:.1%}")
        
        return consensus_results, intermediate_data
    
    def batch_interview(self, model_names: List[str], entities: List[str], max_workers: int = 1) -> Dict[str, Any]:
        """
        批量角色扮演访谈（调用base的通用批量方法）
        
        Args:
            model_names: 模型列表
            entities: 实体列表（国家列表）
            max_workers: 并发线程数，1表示串行，>1表示并行
            
        Returns:
            Dict: 包含results, total_tasks, successful_tasks, success_rate
        """
        countries = entities
        
        print(f"开始批量角色扮演访谈:")
        print(f"  模型数量: {len(model_names)}")
        print(f"  国家数量: {len(countries)}")
        print(f"  总任务数: {len(model_names) * len(countries)}")
        print(f"  并发模式: {'串行' if max_workers == 1 else f'并行 (max_workers={max_workers})'}")
        
        # 构造tasks列表，调用base的通用批量方法
        tasks = [
            {'model_name': model, 'entity_id': country}
            for model in model_names
            for country in countries
        ]
        
        # 调用base实现的批量方法
        if max_workers == 1:
            return super()._batch_interview_sequential(tasks)
        else:
            return super()._batch_interview_concurrent(tasks, max_workers)
    
    # _batch_interview_sequential和_batch_interview_concurrent已移至BaseInterview
    # 使用钩子方法_on_task_completed实现即时保存
    
    def _on_task_completed(self, model_name: str, entity_id: str, 
                          responses: List, intermediate_data: Dict = None):
        """
        重写钩子方法：每个任务完成后立即保存
        防止长时间角色扮演任务崩溃丢失数据
        """
        if entity_id:  # entity_id就是country名称
            self._save_individual_result(model_name, entity_id, responses, intermediate_data)
    
    def _save_individual_result(self, model_name: str, country: str, responses: List[LLMResponse], 
                                intermediate_data: Dict = None):
        """保存单个模型-国家组合的详细结果（包含中间数据）"""
        try:
            from datetime import datetime
            import pickle
            
            # 确保输出目录存在
            output_dir = self.data_path / "roleplay_English" / "llm_responses_roleplay"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 创建安全的文件名
            safe_model_name = model_name.replace('/', '_').replace('\\', '_')
            safe_country_name = country.replace(' ', '_').replace('/', '_')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 转换为可序列化的格式
            serializable_responses = []
            for resp in responses:
                serializable_responses.append({
                    'model_name': resp.model_name,
                    'question_id': resp.question_id,
                    'response': resp.response,
                    'raw_response': resp.raw_response,
                    'is_valid': resp.is_valid,
                    'error_message': resp.error_message
                })
            
            # 构建保存数据
            save_data = {
                'model_name': model_name,
                'country_name': country,
                'timestamp': timestamp,
                'total_questions': len(responses),
                'valid_responses': sum(1 for r in responses if r.is_valid),
                'responses': serializable_responses
            }
            
            # 如果有中间数据（多轮访谈），也保存
            if intermediate_data:
                save_data['intermediate_data'] = intermediate_data
                save_data['consensus_count'] = intermediate_data.get('consensus_count', 1)
                save_data['overall_consistency'] = intermediate_data.get('overall_consistency', 1.0)
                print(f"   📊 保存{intermediate_data.get('consensus_count', 1)}轮访谈数据，一致性: {intermediate_data.get('overall_consistency', 0):.1%}")
            
            # 保存详细数据
            detailed_file = output_dir / f"{safe_model_name}_{safe_country_name}_{timestamp}.pkl"
            with open(detailed_file, 'wb') as f:
                pickle.dump(save_data, f)
            
            print(f"💾 已保存详细结果: {detailed_file.name}")
            
        except Exception as e:
            print(f"❌ 保存单个结果失败: {e}")
    
    def save_results_unified(self, results: Dict) -> str:
        """使用统一格式保存访谈结果"""
        # 转换为统一格式
        unified_data = self._convert_roleplay_to_unified_format(results)
        
        # 使用统一数据管理器保存
        manager = UnifiedDataManager(self.data_path.parent)
        saved_files = manager.save_raw_interview(
            unified_data,
            stage="stage2",
            formats=["pkl", "json"]
        )
        
        return str(saved_files.get("pkl", ""))
    
    def _convert_roleplay_to_unified_format(self, results: Dict) -> Dict:
        """将角色扮演访谈结果转换为统一格式"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 计算总任务和成功任务
        total_tasks = sum(len(countries) for countries in results.values())
        successful_tasks = sum(
            1 for countries in results.values() 
            for country_data in countries.values() if country_data
        )
        
        # 构建元数据
        metadata = {
            "stage": "stage2",
            "timestamp": timestamp,
            "version": "1.0",
            "consensus_count": self.consensus_count,
            "total_entities": successful_tasks,
            "total_questions": 10,
            "total_api_calls": successful_tasks * 10 * self.consensus_count
        }
        
        # 转换results
        unified_results = []
        
        for model_name, countries_data in results.items():
            for country_name, country_data in countries_data.items():
                if not country_data:
                    continue
                
                # 正确提取responses列表
                responses_list = country_data.get('responses', []) if isinstance(country_data, dict) else country_data
                
                # 获取模型和国家信息
                model_region = self.model_configs.get(model_name, {}).get('region', 'Unknown')
                cultural_region = self.countries_data.get(country_name, {}).get('cultural_region', 'Unknown')
                country_code = self.countries_data.get(country_name, {}).get('code', 'XX')
                
                entity_result = {
                    "entity_id": f"roleplay_{model_name.replace('/', '-').replace(':', '-')}_{country_code}",
                    "entity_type": "roleplay_english",
                    "model_name": model_name,
                    "model_region": model_region,
                    "country_name": country_name,
                    "country_code": country_code,
                    "cultural_region": cultural_region,
                    "timestamp": datetime.now().isoformat(),
                    "total_questions": len(responses_list),
                    "valid_responses": sum(1 for r in responses_list if r.is_valid),
                    "success_rate": sum(1 for r in responses_list if r.is_valid) / len(responses_list) * 100 if responses_list else 0,
                    "responses": []
                }
                
                # 转换responses
                for response in responses_list:
                    entity_result["responses"].append({
                        "question_id": response.question_id,
                        "raw_response": response.raw_response,
                        "processed_response": response.response,
                        "is_valid": response.is_valid,
                        "error_message": response.error_message
                    })
                
                unified_results.append(entity_result)
        
        return {
            "metadata": metadata,
            "results": unified_results
        }
    
    def _save_batch_results(self, results: Dict, total_tasks: int, successful_tasks: int):
        """保存批量结果汇总"""
        try:
            from datetime import datetime
            import json
            import pickle
            
            # 确保输出目录存在
            output_dir = self.data_path / "roleplay_English" / "llm_responses_roleplay"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 创建汇总数据
            batch_summary = {
                'timestamp': datetime.now().isoformat(),
                'total_tasks': total_tasks,
                'successful_tasks': successful_tasks,
                'success_rate': successful_tasks / total_tasks if total_tasks > 0 else 0,
                'models_used': len(results),
                'countries_interviewed': sum(len(countries) for countries in results.values()),
                'detailed_results': {}
            }
            
            # 添加每个模型-国家组合的统计
            for model_name, countries_data in results.items():
                for country_name, country_data in countries_data.items():
                    # 正确提取responses列表
                    responses_list = country_data.get('responses', []) if isinstance(country_data, dict) else country_data
                    
                    key = f"{model_name}_{country_name}"
                    batch_summary['detailed_results'][key] = {
                        'total_questions': len(responses_list),
                        'valid_responses': sum(1 for r in responses_list if r.is_valid),
                        'success_rate': sum(1 for r in responses_list if r.is_valid) / len(responses_list) if responses_list else 0
                    }
            
            # 保存汇总JSON
            summary_file = output_dir / f"batch_interview_summary_{timestamp}.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(batch_summary, f, ensure_ascii=False, indent=2)
            
            # 保存完整结果PKL（包含所有响应对象）
            full_results_file = output_dir / f"batch_interview_results_{timestamp}.pkl"
            with open(full_results_file, 'wb') as f:
                pickle.dump({
                    'summary': batch_summary,
                    'full_results': results
                }, f)
            
            # 保存数据处理器期望的格式：roleplay_results.pkl
            self._save_roleplay_results_format(results, output_dir, timestamp)
            
            print(f"📋 批量结果汇总已保存到: {summary_file.name}")
            print(f"💾 完整结果已保存到: {full_results_file.name}")
            
        except Exception as e:
            print(f"❌ 保存批量结果失败: {e}")
    
    def _save_roleplay_results_format(self, results: Dict, output_dir: Path, timestamp: str):
        """保存数据处理器期望的roleplay_results格式"""
        try:
            import json
            import pickle
            
            # 转换为数据处理器期望的格式
            roleplay_results_data = {
                'timestamp': timestamp,
                'total_tasks': len(results),
                'successful_tasks': sum(1 for model_data in results.values() 
                                      for country_data in model_data.values() if country_data),
                'results': []
            }
            
            # 转换每个模型-国家组合的结果
            for model_name, countries_data in results.items():
                for country_name, country_data in countries_data.items():
                    if country_data:  # 只保存成功的结果
                        # 正确提取responses列表
                        responses_list = country_data.get('responses', []) if isinstance(country_data, dict) else country_data
                        
                        # 获取元数据
                        model_region = self.model_configs.get(model_name, {}).get('region', 'Unknown')
                        cultural_region = self.countries_data.get(country_name, {}).get('cultural_region', 'Unknown')
                        country_code = self.countries_data.get(country_name, {}).get('code', country_name)
                        
                        result_entry = {
                            'model': model_name,
                            'country': country_name,
                            'country_code': country_code,
                            'cultural_region': cultural_region,
                            'model_region': model_region,
                            'timestamp': timestamp,
                            'total_questions': len(responses_list),
                            'valid_responses': sum(1 for r in responses_list if r.is_valid),
                            'success_rate': sum(1 for r in responses_list if r.is_valid) / len(responses_list) * 100 if responses_list else 0,
                            'responses': responses_list  # 保持LLMResponse对象
                        }
                        roleplay_results_data['results'].append(result_entry)
            
            # 计算总体成功率
            total_questions = sum(r['total_questions'] for r in roleplay_results_data['results'])
            total_valid = sum(r['valid_responses'] for r in roleplay_results_data['results'])
            roleplay_results_data['total_questions'] = total_questions
            roleplay_results_data['total_valid_responses'] = total_valid
            roleplay_results_data['overall_success_rate'] = total_valid / total_questions * 100 if total_questions > 0 else 0
            
            # 保存为PKL格式（数据处理器的主要格式）
            roleplay_results_pkl = output_dir / f"roleplay_results_{timestamp}.pkl"
            with open(roleplay_results_pkl, 'wb') as f:
                pickle.dump(roleplay_results_data, f)
            
            # 同时保存为JSON格式（备用，不包含LLMResponse对象）
            json_data = roleplay_results_data.copy()
            json_data['results'] = []  # JSON版本不包含复杂对象
            for result in roleplay_results_data['results']:
                json_result = result.copy()
                # 转换LLMResponse对象为字典
                json_result['responses'] = [
                    {
                        'model_name': r.model_name,
                        'question_id': r.question_id,
                        'response': r.response,
                        'raw_response': r.raw_response,
                        'is_valid': r.is_valid,
                        'error_message': r.error_message
                    }
                    for r in result['responses']
                ]
                json_data['results'].append(json_result)
            
            roleplay_results_json = output_dir / f"roleplay_results_{timestamp}.json"
            with open(roleplay_results_json, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 数据处理器格式已保存到: {roleplay_results_pkl.name}")
            print(f"📄 JSON备份已保存到: {roleplay_results_json.name}")
            
        except Exception as e:
            print(f"❌ 保存roleplay_results格式失败: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数 - 测试新架构的角色扮演访谈"""
    print("🔄 使用新架构运行角色扮演访谈...")
    
    # 创建访谈对象
    interview = LLMCountryRoleplayInterview(repeat_count=1)
    
    # 显示可用模型
    available_models = [name for name in interview.model_configs.keys() if name in interview.api_keys]
    print(f"可用模型: {available_models}")
    
    if not available_models:
        print("没有可用的模型，请检查API密钥配置")
        return
    
    # 测试国家
    test_countries = ["China", "United States"]
    test_models = available_models[:1] if available_models else []
    
    # 进行角色扮演访谈
    results = interview.batch_interview(test_models, test_countries)
    
    # 保存结果
    if results['results']:
        output_file = interview.save_results(results)
        print(f"\n✅ 新架构角色扮演访谈完成！")
        print(f"📊 成功率: {results['success_rate']:.1%} ({results['successful_tasks']}/{results['total_tasks']})")
        print(f"💾 结果保存至: {output_file}")
    else:
        print("没有获得有效结果")


if __name__ == "__main__":
    main()
