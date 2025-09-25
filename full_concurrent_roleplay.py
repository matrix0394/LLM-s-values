#!/usr/bin/env python3
"""
完整的并发roleplay访谈系统
- 支持所有7个模型
- 支持109个国家的完整覆盖
- 支持断点续传
- 支持随时停止和开始
- 自动跳过已完成的模型-国家组合
"""

import sys
import os
import time
import json
import pickle
import signal
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Set, Tuple
import threading
from datetime import datetime

# 添加src路径
sys.path.append('src')

from llm_country_roleplay_interview import LLMCountryRoleplayInterview

class FullConcurrentRoleplaySystem:
    def __init__(self, max_workers: int = 8, checkpoint_interval: int = 10, repeat_count: int = 3):
        self.max_workers = max_workers
        self.checkpoint_interval = checkpoint_interval
        self.repeat_count = repeat_count
        self.interview = LLMCountryRoleplayInterview(repeat_count=repeat_count)
        self.results = []
        self.completed_tasks = set()  # 存储已完成的 (model, country) 组合
        self.lock = threading.Lock()
        self.running = True
        self.start_time = None
        
        # 获取所有模型
        self.models = list(self.interview.model_configs.keys())
        print(f"可用模型: {self.models}")
        
        # 获取所有问题
        self.question_ids = ['A008', 'A165', 'E018', 'E025', 'F063', 'F118', 'F120', 'G006', 'Y002', 'Y003']
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # 检查点文件
        self.checkpoint_file = 'data/llm_responses_roleplay/roleplay_checkpoint.json'
        self.results_file = 'data/llm_responses_roleplay/roleplay_results.json'
        
        # 确保目录存在
        os.makedirs(os.path.dirname(self.checkpoint_file), exist_ok=True)
    
    def signal_handler(self, signum, frame):
        """处理中断信号"""
        print(f"\n收到信号 {signum}，正在保存检查点...")
        self.running = False
        self.save_checkpoint()
        print("检查点已保存，程序退出")
        sys.exit(0)
    
    def load_countries_from_pca(self) -> List[str]:
        """从country_scores_pca.json加载国家列表"""
        try:
            with open('data/country_scores_pca.json', 'r') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                countries = [item['Country'] for item in data if 'Country' in item]
                print(f"从country_scores_pca.json加载了 {len(countries)} 个国家")
                return countries
            else:
                print("country_scores_pca.json格式不正确")
                return []
                
        except Exception as e:
            print(f"读取country_scores_pca.json失败: {e}")
            return []
    
    def load_checkpoint(self) -> bool:
        """加载检查点"""
        try:
            if os.path.exists(self.checkpoint_file):
                with open(self.checkpoint_file, 'r') as f:
                    checkpoint = json.load(f)
                
                self.completed_tasks = set(tuple(task) for task in checkpoint.get('completed_tasks', []))
                self.results = checkpoint.get('results', [])
                
                # 处理模型名称映射，将mistral-nemo:free的任务映射到mistral-nemo
                self._handle_model_mapping()
                
                print(f"加载检查点: {len(self.completed_tasks)} 个已完成任务")
                return True
        except Exception as e:
            print(f"加载检查点失败: {e}")
        
        return False
    
    def _handle_model_mapping(self):
        """处理模型名称映射，将free版本的任务映射到paid版本"""
        # 模型映射关系
        model_mappings = {
            'mistralai/mistral-nemo:free': 'mistralai/mistral-nemo'
        }
        
        # 创建新的已完成任务集合
        new_completed_tasks = set()
        
        for task in self.completed_tasks:
            model, country = task
            
            # 如果当前模型在映射中，添加映射后的任务
            if model in model_mappings:
                mapped_model = model_mappings[model]
                new_completed_tasks.add((mapped_model, country))
                print(f"映射任务: {model} -> {country} -> {mapped_model} -> {country}")
            
            # 同时保留原始任务
            new_completed_tasks.add(task)
        
        self.completed_tasks = new_completed_tasks
    
    def save_checkpoint(self):
        """保存检查点"""
        try:
            checkpoint = {
                'timestamp': datetime.now().isoformat(),
                'completed_tasks': list(self.completed_tasks),
                'results': self.results,
                'total_tasks': len(self.completed_tasks),
                'total_results': len(self.results)
            }
            
            with open(self.checkpoint_file, 'w') as f:
                json.dump(checkpoint, f, indent=2, default=str)
            
            print(f"检查点已保存: {len(self.completed_tasks)} 个已完成任务")
            
        except Exception as e:
            print(f"保存检查点失败: {e}")
    
    def interview_single_task(self, model: str, country: str) -> Dict[str, Any]:
        """访谈单个模型-国家组合"""
        task_key = (model, country)
        
        # 检查是否已完成
        if task_key in self.completed_tasks:
            print(f"跳过已完成任务: {model} -> {country}")
            return None
        
        try:
            print(f"开始访谈: {model} -> {country}")
            
            # 访谈所有问题
            responses = []
            valid_count = 0
            
            for question_id in self.question_ids:
                if not self.running:
                    print(f"收到停止信号，中断访谈: {model} -> {country}")
                    return None
                
                try:
                    response = self.interview.ask_question_roleplay(model, country, question_id)
                    responses.append(response)
                    if response.is_valid:
                        valid_count += 1
                except Exception as e:
                    print(f"  问题 {question_id} 失败: {e}")
                    responses.append(None)
            
            result = {
                'model': model,
                'country': country,
                'timestamp': datetime.now().isoformat(),
                'total_questions': len(self.question_ids),
                'valid_responses': valid_count,
                'success_rate': valid_count / len(self.question_ids) * 100,
                'responses': responses
            }
            
            # 标记为已完成
            with self.lock:
                self.completed_tasks.add(task_key)
                self.results.append(result)
            
            print(f"完成访谈: {model} -> {country} ({valid_count}/{len(self.question_ids)})")
            return result
            
        except Exception as e:
            print(f"访谈失败: {model} -> {country}: {e}")
            error_result = {
                'model': model,
                'country': country,
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'total_questions': 0,
                'valid_responses': 0,
                'success_rate': 0,
                'responses': []
            }
            
            with self.lock:
                self.completed_tasks.add(task_key)
                self.results.append(error_result)
            
            return error_result
    
    def run_concurrent_interviews(self):
        """运行并发访谈"""
        # 加载国家列表
        countries = self.load_countries_from_pca()
        if not countries:
            print("无法加载国家列表，退出")
            return
        
        # 加载检查点
        self.load_checkpoint()
        
        # 创建任务列表
        all_tasks = []
        for model in self.models:
            for country in countries:
                all_tasks.append((model, country))
        
        # 过滤已完成的任务
        remaining_tasks = [(model, country) for model, country in all_tasks 
                          if (model, country) not in self.completed_tasks]
        
        print(f"任务统计:")
        print(f"  总任务数: {len(all_tasks)}")
        print(f"  已完成: {len(self.completed_tasks)}")
        print(f"  剩余: {len(remaining_tasks)}")
        print(f"  并发数: {self.max_workers}")
        
        if not remaining_tasks:
            print("所有任务已完成！")
            return
        
        # 开始并发执行
        self.start_time = time.time()
        self.running = True
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有剩余任务
            future_to_task = {
                executor.submit(self.interview_single_task, model, country): (model, country)
                for model, country in remaining_tasks
            }
            
            # 收集结果
            completed_count = len(self.completed_tasks)
            total_count = len(all_tasks)
            
            for future in as_completed(future_to_task):
                if not self.running:
                    print("收到停止信号，正在退出...")
                    break
                
                model, country = future_to_task[future]
                try:
                    result = future.result()
                    if result is not None:
                        completed_count += 1
                        
                        # 显示进度
                        progress = completed_count / total_count * 100
                        elapsed = time.time() - self.start_time
                        eta = elapsed / completed_count * (total_count - completed_count) if completed_count > 0 else 0
                        
                        print(f"进度: {completed_count}/{total_count} ({progress:.1f}%) - 已用时: {elapsed:.1f}s - 预计剩余: {eta:.1f}s")
                        
                        # 定期保存检查点
                        if completed_count % self.checkpoint_interval == 0:
                            self.save_checkpoint()
                            # 也保存部分单独文件
                            self.save_individual_files()
                
                except Exception as e:
                    print(f"任务执行失败: {model} -> {country}: {e}")
        
        # 最终保存
        self.save_checkpoint()
        self.save_final_results()
        
        total_time = time.time() - self.start_time
        print(f"\\n所有访谈完成! 总用时: {total_time:.1f}s ({total_time/60:.1f} 分钟)")
    
    def save_final_results(self):
        """保存最终结果"""
        try:
            # 统计结果
            total_tasks = len(self.results)
            successful_tasks = sum(1 for r in self.results if 'error' not in r)
            total_questions = sum(r.get('total_questions', 0) for r in self.results)
            total_valid = sum(r.get('valid_responses', 0) for r in self.results)
            overall_success_rate = total_valid / total_questions * 100 if total_questions > 0 else 0
            
            final_data = {
                'timestamp': datetime.now().isoformat(),
                'total_tasks': total_tasks,
                'successful_tasks': successful_tasks,
                'total_questions': total_questions,
                'total_valid_responses': total_valid,
                'overall_success_rate': overall_success_rate,
                'models': self.models,
                'countries_count': len(set(r['country'] for r in self.results)),
                'results': self.results
            }
            
            # 保存JSON
            with open(self.results_file, 'w', encoding='utf-8') as f:
                json.dump(final_data, f, ensure_ascii=False, indent=2, default=str)
            
            # 保存PKL
            pkl_file = self.results_file.replace('.json', '.pkl')
            with open(pkl_file, 'wb') as f:
                pickle.dump(final_data, f)
            
            # 按模型-国家组合保存单独文件（与之前系统保持一致）
            self.save_individual_files()
            
            print(f"\\n最终结果已保存:")
            print(f"  JSON: {self.results_file}")
            print(f"  PKL: {pkl_file}")
            print(f"  单独文件: data/llm_responses_roleplay/")
            
            # 打印摘要
            self.print_summary(final_data)
            
        except Exception as e:
            print(f"保存最终结果失败: {e}")
    
    def save_individual_files(self):
        """按模型-国家组合保存单独文件（与之前系统保持一致）"""
        try:
            # 按模型分组保存
            for model in self.models:
                model_results = [r for r in self.results if r['model'] == model]
                if not model_results:
                    continue
                
                # 创建模型目录（处理模型名称映射）
                model_dir_name = model.replace('/', '_')
                model_dir = f"data/llm_responses_roleplay/{model_dir_name}"
                os.makedirs(model_dir, exist_ok=True)
                
                # 按国家分组
                country_data = {}
                for result in model_results:
                    country = result['country']
                    if country not in country_data:
                        country_data[country] = []
                    
                    # 转换响应格式
                    for response in result.get('responses', []):
                        if response is not None and hasattr(response, 'question_id'):
                            country_data[country].append({
                                'question_id': response.question_id,
                                'response': response.response,
                                'raw_response': response.raw_response,
                                'is_valid': response.is_valid,
                                'error_message': response.error_message
                            })
                        elif response is not None:
                            # 如果response不是None但没有question_id属性，可能是其他格式
                            print(f"警告: 响应格式异常: {type(response)} - {response}")
                
                # 保存每个国家的数据
                for country, responses in country_data.items():
                    country_file = f"{model_dir}/{country.replace(' ', '_')}.json"
                    with open(country_file, 'w', encoding='utf-8') as f:
                        json.dump(responses, f, ensure_ascii=False, indent=2, default=str)
                    
                    # 同时保存PKL格式
                    pkl_file = country_file.replace('.json', '.pkl')
                    with open(pkl_file, 'wb') as f:
                        pickle.dump(responses, f)
                
                print(f"  模型 {model}: 保存了 {len(country_data)} 个国家的数据")
                
        except Exception as e:
            print(f"保存单独文件失败: {e}")
    
    def print_summary(self, data: Dict[str, Any]):
        """打印结果摘要"""
        print(f"\\n=== 最终结果摘要 ===")
        print(f"总任务数: {data['total_tasks']}")
        print(f"成功任务数: {data['successful_tasks']}")
        print(f"总问题数: {data['total_questions']}")
        print(f"有效回答数: {data['total_valid_responses']}")
        print(f"总体成功率: {data['overall_success_rate']:.1f}%")
        print(f"涉及国家数: {data['countries_count']}")
        
        # 按模型统计
        print(f"\\n=== 按模型统计 ===")
        model_stats = {}
        for result in data['results']:
            model = result['model']
            if model not in model_stats:
                model_stats[model] = {'total': 0, 'valid': 0, 'tasks': 0}
            model_stats[model]['total'] += result.get('total_questions', 0)
            model_stats[model]['valid'] += result.get('valid_responses', 0)
            model_stats[model]['tasks'] += 1
        
        for model, stats in model_stats.items():
            success_rate = stats['valid'] / stats['total'] * 100 if stats['total'] > 0 else 0
            print(f"{model:30s}: {stats['valid']:3d}/{stats['total']:3d} ({success_rate:5.1f}%) - {stats['tasks']:2d} 任务")
        
        # 识别问题模型和国家
        self.identify_problem_areas(data)
    
    def identify_problem_areas(self, data: Dict[str, Any]):
        """识别问题模型和国家"""
        print(f"\\n=== 问题分析 ===")
        
        # 按模型分析
        model_problems = {}
        for result in data['results']:
            model = result['model']
            if model not in model_problems:
                model_problems[model] = []
            
            if result.get('success_rate', 0) < 50:  # 成功率低于50%
                model_problems[model].append({
                    'country': result['country'],
                    'success_rate': result.get('success_rate', 0)
                })
        
        print("成功率低于50%的模型-国家组合:")
        for model, problems in model_problems.items():
            if problems:
                print(f"  {model}: {len(problems)} 个国家")
                for problem in sorted(problems, key=lambda x: x['success_rate'])[:5]:  # 显示最差的5个
                    print(f"    {problem['country']}: {problem['success_rate']:.1f}%")
        
        # 按国家分析
        country_problems = {}
        for result in data['results']:
            country = result['country']
            if country not in country_problems:
                country_problems[country] = []
            
            if result.get('success_rate', 0) < 50:
                country_problems[country].append({
                    'model': result['model'],
                    'success_rate': result.get('success_rate', 0)
                })
        
        print("\\n成功率低于50%的国家:")
        for country, problems in country_problems.items():
            if problems:
                avg_success = sum(p['success_rate'] for p in problems) / len(problems)
                print(f"  {country}: 平均成功率 {avg_success:.1f}% ({len(problems)} 个模型)")

def main():
    """主函数"""
    print("=== 完整并发Roleplay访谈系统 ===")
    print("支持功能:")
    print("  - 所有7个模型")
    print("  - 109个国家完整覆盖")
    print("  - 断点续传")
    print("  - 随时停止 (Ctrl+C)")
    print("  - 自动跳过已完成任务")
    print()
    
    # 创建系统
    system = FullConcurrentRoleplaySystem(max_workers=8, checkpoint_interval=10, repeat_count=3)
    
    try:
        # 运行访谈
        system.run_concurrent_interviews()
    except KeyboardInterrupt:
        print("\\n用户中断，正在保存检查点...")
        system.save_checkpoint()
        print("检查点已保存")
    except Exception as e:
        print(f"\\n系统错误: {e}")
        system.save_checkpoint()
        print("检查点已保存")

if __name__ == "__main__":
    main()
