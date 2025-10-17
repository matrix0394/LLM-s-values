"""
新的角色扮演访谈类 - 基于BaseInterview
替换原有的复杂LLMCountryRoleplayInterview类
"""

import os
import json
import pickle
import sys
from pathlib import Path
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor
import threading

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.base.base_interview import BaseInterview
from src.llm_values.llm_questionnaire import LLMResponse


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
        super().__init__(repeat_count=repeat_count, data_path=data_path)
        self.consensus_count = consensus_count
        
        # 加载角色扮演特有的数据
        self.countries_data = self._load_countries_data()
        self.cultural_regions = self._load_cultural_regions()
        
        # 角色扮演的基础系统提示词 - 人性化、文化导向
        self.base_system_prompt = """You are participating in a cultural values survey. Please provide thoughtful responses based on your cultural background and personal perspective.

Please follow these guidelines:
- Answer each question with a genuine, considered response
- Choose the option that best reflects your cultural values and beliefs
- Respond as a real person from your country would

Response format:
- Single choice questions: respond with ONE number only
- Y002 (two choices): respond with TWO numbers separated by space
- Y003 (multiple choices): respond with 1-5 numbers separated by spaces

Please provide meaningful answers that reflect your cultural perspective."""
    
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
        base_prompt = self.base_system_prompt
        
        # 添加国家特定的角色扮演指令
        country_context = f"""
        
IMPORTANT: You are roleplaying as a typical citizen from {country}. 
Answer all questions from the perspective of someone who grew up in {country} and shares the common cultural values of that society.
Consider the cultural, social, and historical context of {country} when making your choices."""
        
        return base_prompt + country_context
    
    def _calculate_consensus(self, responses: List[LLMResponse], question_id: str) -> LLMResponse:
        """计算多个回答的众数"""
        from collections import Counter
        
        # 提取有效回答
        valid_responses = [r.response for r in responses if r.is_valid and r.response is not None]
        
        if not valid_responses:
            return responses[0]  # 返回第一个回答（即使无效）
        
        # 根据问题类型处理众数计算
        if question_id in ['Y002', 'Y003']:
            # 对于复杂问题，将回答转换为字符串进行比较
            response_strings = [str(resp) for resp in valid_responses]
            most_common = Counter(response_strings).most_common(1)[0][0]
            
            # 找到对应的原始回答
            for i, resp_str in enumerate(response_strings):
                if resp_str == most_common:
                    consensus_value = valid_responses[i]
                    break
        else:
            # 对于单选题，直接计算众数
            most_common = Counter(valid_responses).most_common(1)[0][0]
            consensus_value = most_common
        
        # 创建众数回答对象
        base_response = responses[0]  # 使用第一个回答作为模板
        return LLMResponse(
            model_name=base_response.model_name,
            question_id=question_id,
            response=consensus_value,
            raw_response=f"Consensus from {len(valid_responses)} responses: {consensus_value}",
            is_valid=True,
            error_message=None
        )
    
    def interview_entity(self, model_name: str, entity_id: str) -> List[LLMResponse]:
        """访谈单个模型扮演特定国家"""
        country = entity_id  # entity_id就是国家名
        print(f"\n=== {model_name} 扮演 {country} ===")
        
        if model_name not in self.api_keys:
            print(f"跳过模型 {model_name}: API密钥未设置")
            return []
        
        # 创建国家特定的系统提示词
        country_system_prompt = self._create_country_system_prompt(country)
        
        if self.consensus_count <= 1:
            # 单次访谈模式
            return self._single_round_interview(model_name, country, country_system_prompt)
        else:
            # 多轮访谈取众数模式
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
    
    def _multi_round_interview(self, model_name: str, country: str, system_prompt: str) -> List[LLMResponse]:
        """多轮访谈取众数"""
        print(f"🔄 进行 {self.consensus_count} 轮完整问卷访谈...")
        
        question_ids = list(self.questions.get_all_questions().keys())
        all_rounds_responses = []  # 存储所有轮次的回答
        
        # 进行多轮完整访谈
        for round_num in range(self.consensus_count):
            print(f"\n📋 第 {round_num + 1}/{self.consensus_count} 轮访谈:")
            round_responses = []
            
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
                
                round_responses.append(response)
                
                # 问题间延迟
                import time
                time.sleep(self._get_dynamic_delay(model_name))
            
            all_rounds_responses.append(round_responses)
            
            # 轮次间稍长延迟
            if round_num < self.consensus_count - 1:
                print(f"  ⏳ 第{round_num + 1}轮完成，休息片刻...")
                import time
                time.sleep(self._get_dynamic_delay(model_name) * 2)
        
        # 计算每个问题的众数
        print(f"\n🧮 计算 {len(question_ids)} 个问题的众数...")
        consensus_results = []
        
        for i, question_id in enumerate(question_ids):
            # 收集该问题在所有轮次中的回答
            question_responses = [round_resp[i] for round_resp in all_rounds_responses]
            
            # 计算众数
            consensus_response = self._calculate_consensus(question_responses, question_id)
            consensus_results.append(consensus_response)
            
            print(f"  {question_id}: {consensus_response.response} (来自{len([r for r in question_responses if r.is_valid])}个有效回答)")
        
        return consensus_results
    
    def batch_interview(self, model_names: List[str], entities: List[str]) -> Dict[str, Any]:
        """批量角色扮演访谈"""
        countries = entities  # entities就是国家列表
        
        print(f"开始批量角色扮演访谈:")
        print(f"  模型数量: {len(model_names)}")
        print(f"  国家数量: {len(countries)}")
        print(f"  总任务数: {len(model_names) * len(countries)}")
        
        results = {}
        successful_tasks = 0
        total_tasks = len(model_names) * len(countries)
        
        for model_name in model_names:
            if model_name not in results:
                results[model_name] = {}
            
            for country in countries:
                print(f"\n{'='*60}")
                print(f"任务: {model_name} 扮演 {country}")
                print(f"{'='*60}")
                
                country_results = self.interview_entity(model_name, country)
                if country_results:
                    results[model_name][country] = country_results
                    successful_tasks += 1
                    print(f"✅ {model_name} 扮演 {country} 完成: {len(country_results)} 个回答")
                else:
                    print(f"❌ {model_name} 扮演 {country} 失败")
        
        return {
            'results': results,
            'total_tasks': total_tasks,
            'successful_tasks': successful_tasks,
            'success_rate': successful_tasks / total_tasks if total_tasks > 0 else 0
        }
    
    def batch_interview_concurrent(self, model_names: List[str], countries: List[str], 
                                 max_workers: int = 3) -> Dict[str, Any]:
        """并发批量角色扮演访谈"""
        print(f"开始并发角色扮演访谈:")
        print(f"  模型数量: {len(model_names)}")
        print(f"  国家数量: {len(countries)}")
        print(f"  并发数: {max_workers}")
        print(f"  总任务数: {len(model_names) * len(countries)}")
        
        results = {}
        successful_tasks = 0
        total_tasks = len(model_names) * len(countries)
        results_lock = threading.Lock()
        
        def interview_task(model_name: str, country: str):
            """单个访谈任务"""
            nonlocal successful_tasks
            
            print(f"🚀 开始任务: {model_name} 扮演 {country}")
            country_results = self.interview_entity(model_name, country)
            
            with results_lock:
                if model_name not in results:
                    results[model_name] = {}
                
                if country_results:
                    results[model_name][country] = country_results
                    successful_tasks += 1
                    print(f"✅ 完成: {model_name} 扮演 {country} ({len(country_results)} 个回答)")
                    
                    # 立即保存单个任务的详细结果
                    self._save_individual_result(model_name, country, country_results)
                else:
                    print(f"❌ 失败: {model_name} 扮演 {country}")
        
        # 创建任务列表
        tasks = [(model_name, country) for model_name in model_names for country in countries]
        
        # 并发执行
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(interview_task, model_name, country) 
                      for model_name, country in tasks]
            
            # 等待所有任务完成
            for future in futures:
                future.result()
        
        # 保存批量汇总结果
        self._save_batch_results(results, total_tasks, successful_tasks)
        
        return {
            'results': results,
            'total_tasks': total_tasks,
            'successful_tasks': successful_tasks,
            'success_rate': successful_tasks / total_tasks if total_tasks > 0 else 0
        }
    
    def _save_individual_result(self, model_name: str, country: str, responses: List[LLMResponse]):
        """保存单个模型-国家组合的详细结果"""
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
            
            # 保存详细数据
            detailed_file = output_dir / f"{safe_model_name}_{safe_country_name}_{timestamp}.pkl"
            with open(detailed_file, 'wb') as f:
                pickle.dump({
                    'model_name': model_name,
                    'country_name': country,
                    'timestamp': timestamp,
                    'responses': serializable_responses
                }, f)
            
            print(f"💾 已保存详细结果: {detailed_file.name}")
            
        except Exception as e:
            print(f"❌ 保存单个结果失败: {e}")
    
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
                for country_name, responses in countries_data.items():
                    key = f"{model_name}_{country_name}"
                    batch_summary['detailed_results'][key] = {
                        'total_questions': len(responses),
                        'valid_responses': sum(1 for r in responses if r.is_valid),
                        'success_rate': sum(1 for r in responses if r.is_valid) / len(responses) if responses else 0
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
                for country_name, responses in countries_data.items():
                    if responses:  # 只保存成功的结果
                        result_entry = {
                            'model': model_name,
                            'country': country_name,
                            'timestamp': timestamp,
                            'total_questions': len(responses),
                            'valid_responses': sum(1 for r in responses if r.is_valid),
                            'success_rate': sum(1 for r in responses if r.is_valid) / len(responses) * 100 if responses else 0,
                            'responses': responses  # 保持LLMResponse对象
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
