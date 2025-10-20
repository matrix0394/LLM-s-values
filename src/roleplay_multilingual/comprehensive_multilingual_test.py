"""
全面多语言测试模块
每个语言3个国家，所有模型，每个问题回答5遍取众数
"""

import json
import time
import pickle
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import Counter
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import threading

# 导入基础模块
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.roleplay_multilingual.multilingual_roleplay_interview import MultilingualRoleplayInterview
from src.base.ivs_question_processor import IVSQuestionProcessor


class ComprehensiveMultilingualTest:
    """全面多语言测试类"""
    
    def __init__(self, config_path: str = "comprehensive_multilingual_config.json"):
        """初始化"""
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.data_path = Path("data/roleplay_multilingual")
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # 初始化访谈器（使用配置文件中的repeat_count）
        repeat_count = self.config.get('repeat_count', 5)
        self.interviewer = MultilingualRoleplayInterview(
            repeat_count=repeat_count,  # 使用配置的重复次数
            data_path=str(self.data_path)
        )
        print(f"📋 访谈器初始化: repeat_count={repeat_count}")
        
        # IVS问题处理器
        self.question_processor = IVSQuestionProcessor()
        
        # 线程锁
        self.lock = threading.Lock()
        self.progress_counter = 0
        self.total_tasks = 0
        
    def _load_config(self) -> Dict:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 尝试不同的配置键名
            if 'comprehensive_test_config' in config:
                return config['comprehensive_test_config']
            elif 'small_scale_test_config' in config:
                return config['small_scale_test_config']
            else:
                # 如果都没有，返回第一个配置
                keys = list(config.keys())
                if keys:
                    print(f"⚠️ 使用配置键: {keys[0]}")
                    return config[keys[0]]
                else:
                    raise ValueError("配置文件为空")
                    
        except Exception as e:
            print(f"❌ 加载配置失败: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "repeat_count": 5,
            "temperature": 0.1,
            "max_tokens": 50,
            "languages": {
                "zh-cn": {
                    "countries": [{"name": "China", "code": "CHN", "priority": 1}]
                },
                "en": {
                    "countries": [{"name": "United States of America (the)", "code": "USA", "priority": 1}]
                }
            },
            "models": ["openai/gpt-4o-mini", "anthropic/claude-3.7-sonnet"]
        }
    
    def calculate_majority_vote(self, responses: List[str]) -> Tuple[str, float, Dict]:
        """计算众数及置信度"""
        if not responses:
            return None, 0.0, {}
        
        # 过滤有效回答
        valid_responses = [r for r in responses if r and str(r).strip()]
        if not valid_responses:
            return None, 0.0, {}
        
        # 计算众数
        counter = Counter(valid_responses)
        most_common = counter.most_common(1)[0]
        majority_vote = most_common[0]
        majority_count = most_common[1]
        
        # 计算置信度
        confidence = majority_count / len(valid_responses)
        
        # 统计信息
        stats = {
            "total_responses": len(responses),
            "valid_responses": len(valid_responses),
            "majority_count": majority_count,
            "confidence": confidence,
            "response_distribution": dict(counter),
            "is_unanimous": len(counter) == 1
        }
        
        return majority_vote, confidence, stats
    
    def interview_single_task(self, model: str, country: str, language: str) -> Dict:
        """执行单个访谈任务（直接使用新的重复访谈方法）"""
        task_id = f"{model}_{country}_{language}"
        
        try:
            # 直接调用新的重复访谈方法
            # 它会自动处理重复、计算众数、显示清晰的进度
            result = self.interviewer.interview_country_multilingual_with_repeats(
                model, country, language
            )
            
            # 添加任务ID
            result['task_id'] = task_id
            result['success'] = True
            
            # 更新进度
            with self.lock:
                self.progress_counter += 1
                progress = (self.progress_counter / self.total_tasks) * 100
                print(f"\n🟢 进度: [{self.progress_counter}/{self.total_tasks}] ({progress:.1f}%) - {task_id} 完成")
            
            return result
            
        except Exception as e:
            print(f"\n❌ 任务失败 {task_id}: {e}")
            with self.lock:
                self.progress_counter += 1
            return {
                "model": model,
                "country": country, 
                "language": language,
                "task_id": task_id,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _process_repeated_responses(self, all_responses: List[Dict], 
                                  model: str, country: str, language: str) -> Dict:
        """处理5次重复回答，计算众数"""
        if not all_responses:
            return {
                "model": model,
                "country": country,
                "language": language,
                "success": False,
                "error": "No valid responses"
            }
        
        # 按问题ID组织回答
        question_responses = {}
        for response_data in all_responses:
            if 'responses' in response_data:
                for resp in response_data['responses']:
                    q_id = resp['question_id']
                    if q_id not in question_responses:
                        question_responses[q_id] = []
                    
                    # 获取处理后的回答
                    processed_resp = resp.get('processed_response')
                    if processed_resp is not None:
                        question_responses[q_id].append(processed_resp)
        
        # 计算每个问题的众数 //by=>friday
        print(f"\n📊 计算众数结果:")
        final_responses = []
        majority_stats = {}
        
        for q_id, responses in question_responses.items():
            majority_vote, confidence, stats = self.calculate_majority_vote(responses)
            
            # 打印每个问题的众数计算过程 //by=>friday
            print(f"  📝 {q_id}: {responses} → 众数: '{majority_vote}' (置信度: {confidence*100:.1f}%)")
            
            final_responses.append({
                "question_id": q_id,
                "raw_responses": responses,
                "majority_vote": majority_vote,
                "confidence": confidence,
                "processed_response": majority_vote,
                "is_valid": majority_vote is not None
            })
            
            majority_stats[q_id] = stats
        
        # 计算整体统计
        overall_confidence = sum(
            stats['confidence'] for stats in majority_stats.values()
        ) / len(majority_stats) if majority_stats else 0
        
        return {
            "model": model,
            "country": country,
            "language": language,
            "task_id": f"{model}_{country}_{language}",
            "success": True,
            "responses": final_responses,
            "majority_stats": majority_stats,
            "overall_confidence": overall_confidence,
            "total_questions": len(final_responses),
            "valid_questions": sum(1 for r in final_responses if r['is_valid']),
            "raw_response_data": all_responses,  # 保存原始数据
            "timestamp": datetime.now().isoformat()
        }
    
    def run_comprehensive_test(self, max_workers: int = 4) -> Dict[str, Any]:
        """运行全面测试"""
        print("🚀 开始全面多语言测试")
        print("=" * 60)
        
        # 计算总任务数
        total_tasks = 0
        for lang_config in self.config['languages'].values():
            total_tasks += len(lang_config['countries']) * len(self.config['models'])
        
        self.total_tasks = total_tasks
        
        print(f"📊 测试配置:")
        print(f"   - 语言数量: {len(self.config['languages'])}")
        print(f"   - 每语言国家数: 3")
        print(f"   - 模型数量: {len(self.config['models'])}")
        print(f"   - 每问题重复: {self.config['repeat_count']} 次")
        print(f"   - 总任务数: {total_tasks}")
        print(f"   - 总API调用: {total_tasks * self.config['repeat_count'] * 10} 次")
        print(f"   - 预计费用: ~${total_tasks * self.config['repeat_count'] * 10 * 0.01:.2f}")
        print()
        
        # 确认继续
        response = input("⚠️ 这将进行大量API调用，是否继续? (y/n): ").lower().strip()
        if response != 'y':
            print("❌ 用户取消测试")
            return {}
        
        start_time = datetime.now()
        all_results = []
        
        # 准备任务列表
        tasks = []
        for language, lang_config in self.config['languages'].items():
            for country_info in lang_config['countries']:
                country = country_info['name']
                for model in self.config['models']:
                    tasks.append((model, country, language))
        
        print(f"🔄 开始并发执行 {len(tasks)} 个任务...")
        
        # 并发执行
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(self.interview_single_task, model, country, language)
                for model, country, language in tasks
            ]
            
            for future in futures:
                try:
                    result = future.result(timeout=300)  # 5分钟超时
                    all_results.append(result)
                except Exception as e:
                    print(f"⚠️ 任务执行异常: {e}")
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        # 统计结果
        successful_tasks = sum(1 for r in all_results if r.get('success', False))
        failed_tasks = len(all_results) - successful_tasks
        
        print(f"\n📊 测试完成统计:")
        print(f"   - 总任务数: {len(all_results)}")
        print(f"   - 成功任务: {successful_tasks}")
        print(f"   - 失败任务: {failed_tasks}")
        print(f"   - 成功率: {successful_tasks/len(all_results)*100:.1f}%")
        print(f"   - 总耗时: {duration}")
        
        # 保存结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_data = {
            "experiment_config": self.config,
            "execution_summary": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration.total_seconds(),
                "total_tasks": len(all_results),
                "successful_tasks": successful_tasks,
                "failed_tasks": failed_tasks,
                "success_rate": successful_tasks/len(all_results) if all_results else 0
            },
            "results": all_results,
            "timestamp": timestamp
        }
        
        # 保存到文件
        output_file = self.data_path / f"comprehensive_test_results_{timestamp}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, ensure_ascii=False, indent=2)
        
        pkl_file = self.data_path / f"comprehensive_test_results_{timestamp}.pkl"
        with open(pkl_file, 'wb') as f:
            pickle.dump(results_data, f)
        
        print(f"\n💾 结果已保存:")
        print(f"   - JSON: {output_file}")
        print(f"   - PKL: {pkl_file}")
        
        return results_data


def main():
    """主函数"""
    print("🌐 全面多语言测试")
    print("=" * 50)
    
    # 创建测试实例
    tester = ComprehensiveMultilingualTest()
    
    # 运行测试
    results = tester.run_comprehensive_test(max_workers=3)
    
    if results:
        print("\n🎊 全面测试完成!")
        return results
    else:
        print("\n❌ 测试未完成")
        return None


if __name__ == "__main__":
    main()
