#!/usr/bin/env python3
"""
并发运行roleplay访谈，处理所有国家
"""

import sys
import os
import asyncio
import aiohttp
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
import threading
from queue import Queue
import pickle

# 添加src路径
sys.path.append('src')

from llm_country_roleplay_interview import LLMCountryRoleplayInterview
from llm_questionnaire import LLMQuestionnaire

class ConcurrentRoleplayInterview:
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.interview = LLMCountryRoleplayInterview()
        self.questionnaire = LLMQuestionnaire()
        self.results = []
        self.lock = threading.Lock()
        self.progress_queue = Queue()
        
        # 获取所有问题ID
        self.question_ids = [
            'A008', 'A165', 'E018', 'E025', 'F063', 
            'F118', 'F120', 'G006', 'Y002', 'Y003'
        ]
        
        # 获取所有模型
        self.models = list(self.interview.model_configs.keys())
        print(f"可用模型: {self.models}")
        
    def load_countries_from_valid_data(self) -> List[str]:
        """从valid_data.pkl加载国家列表"""
        try:
            with open('data/valid_data.pkl', 'rb') as f:
                valid_data = pickle.load(f)
            
            if hasattr(valid_data, 'columns') and 'Country' in valid_data.columns:
                countries = valid_data['Country'].unique().tolist()
                print(f"从valid_data加载了 {len(countries)} 个国家")
                return countries
            else:
                print("valid_data中没有找到Country列，使用默认国家列表")
                return self.get_default_countries()
                
        except Exception as e:
            print(f"加载valid_data失败: {e}，使用默认国家列表")
            return self.get_default_countries()
    
    def get_default_countries(self) -> List[str]:
        """获取默认的国家列表"""
        return [
            "United States", "China", "Japan", "Germany", "United Kingdom",
            "France", "Italy", "Brazil", "India", "Russia", "Canada", "Australia",
            "South Korea", "Spain", "Mexico", "Indonesia", "Netherlands", "Saudi Arabia",
            "Turkey", "Switzerland", "Belgium", "Argentina", "Sweden", "Poland",
            "Thailand", "Israel", "Austria", "Nigeria", "South Africa", "Egypt",
            "Chile", "Finland", "Bangladesh", "Vietnam", "Romania", "Czech Republic",
            "Peru", "New Zealand", "Iraq", "Portugal", "Greece", "Algeria",
            "Kazakhstan", "Hungary", "Kuwait", "Morocco", "Slovakia", "Ecuador",
            "Ethiopia", "Angola", "Oman", "Azerbaijan", "Belarus", "Sri Lanka",
            "Myanmar", "Tanzania", "Kenya", "Ghana", "Uganda", "Albania",
            "Senegal", "Cambodia", "Zimbabwe", "Malawi", "Mali", "Burkina Faso",
            "Niger", "Madagascar", "Rwanda", "Guinea", "Benin", "Tunisia",
            "Burundi", "South Sudan", "Togo", "Sierra Leone", "Libya", "Liberia",
            "Central African Republic", "Mauritania", "Eritrea", "Gambia",
            "Botswana", "Namibia", "Gabon", "Lesotho", "Guinea-Bissau",
            "Equatorial Guinea", "Mauritius", "Eswatini", "Djibouti", "Comoros",
            "Cape Verde", "Sao Tome and Principe", "Seychelles"
        ]
    
    def interview_single_country(self, country_name: str, model_name: str) -> Dict[str, Any]:
        """访谈单个国家"""
        try:
            print(f"开始访谈: {model_name} -> {country_name}")
            
            # 获取该国家的所有问题回答
            responses = []
            for question_id in self.question_ids:
                try:
                    response = self.interview.ask_question_roleplay(
                        model_name, country_name, question_id
                    )
                    responses.append(response)
                    
                    # 更新进度
                    with self.lock:
                        self.progress_queue.put({
                            'model': model_name,
                            'country': country_name,
                            'question': question_id,
                            'status': 'completed' if response.is_valid else 'failed',
                            'response': response.raw_response
                        })
                        
                except Exception as e:
                    print(f"  问题 {question_id} 失败: {e}")
                    with self.lock:
                        self.progress_queue.put({
                            'model': model_name,
                            'country': country_name,
                            'question': question_id,
                            'status': 'error',
                            'error': str(e)
                        })
            
            # 统计结果
            valid_count = sum(1 for r in responses if r.is_valid)
            total_count = len(responses)
            
            result = {
                'model_name': model_name,
                'country_name': country_name,
                'timestamp': time.strftime('%Y%m%d_%H%M%S'),
                'total_questions': total_count,
                'valid_responses': valid_count,
                'success_rate': valid_count / total_count * 100 if total_count > 0 else 0,
                'responses': responses
            }
            
            print(f"完成访谈: {model_name} -> {country_name} ({valid_count}/{total_count})")
            return result
            
        except Exception as e:
            print(f"访谈失败: {model_name} -> {country_name}: {e}")
            return {
                'model_name': model_name,
                'country_name': country_name,
                'timestamp': time.strftime('%Y%m%d_%H%M%S'),
                'error': str(e),
                'total_questions': 0,
                'valid_responses': 0,
                'success_rate': 0,
                'responses': []
            }
    
    def run_concurrent_interviews(self, countries: List[str] = None, models: List[str] = None):
        """并发运行访谈"""
        if countries is None:
            countries = self.load_countries_from_valid_data()
        
        if models is None:
            models = self.models
        
        print(f"开始并发访谈:")
        print(f"  国家数量: {len(countries)}")
        print(f"  模型数量: {len(models)}")
        print(f"  并发数: {self.max_workers}")
        print(f"  总任务数: {len(countries) * len(models)}")
        
        # 创建任务列表
        tasks = []
        for model in models:
            for country in countries:
                tasks.append((model, country))
        
        # 并发执行
        results = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_task = {
                executor.submit(self.interview_single_country, country, model): (model, country)
                for model, country in tasks
            }
            
            # 收集结果
            completed = 0
            for future in as_completed(future_to_task):
                model, country = future_to_task[future]
                try:
                    result = future.result()
                    results.append(result)
                    completed += 1
                    
                    # 显示进度
                    progress = completed / len(tasks) * 100
                    elapsed = time.time() - start_time
                    eta = elapsed / completed * (len(tasks) - completed) if completed > 0 else 0
                    
                    print(f"进度: {completed}/{len(tasks)} ({progress:.1f}%) - 已用时: {elapsed:.1f}s - 预计剩余: {eta:.1f}s")
                    
                except Exception as e:
                    print(f"任务失败: {model} -> {country}: {e}")
                    results.append({
                        'model_name': model,
                        'country_name': country,
                        'timestamp': time.strftime('%Y%m%d_%H%M%S'),
                        'error': str(e),
                        'total_questions': 0,
                        'valid_responses': 0,
                        'success_rate': 0,
                        'responses': []
                    })
        
        total_time = time.time() - start_time
        print(f"\\n所有访谈完成! 总用时: {total_time:.1f}s")
        
        return results
    
    def save_results(self, results: List[Dict[str, Any]], filename: str = None):
        """保存结果"""
        if filename is None:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f'data/llm_responses_roleplay/concurrent_roleplay_results_{timestamp}.json'
        
        # 确保目录存在
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # 准备保存的数据
        save_data = {
            'timestamp': time.strftime('%Y%m%d_%H%M%S'),
            'total_tasks': len(results),
            'successful_tasks': sum(1 for r in results if 'error' not in r),
            'total_questions': sum(r.get('total_questions', 0) for r in results),
            'total_valid_responses': sum(r.get('valid_responses', 0) for r in results),
            'overall_success_rate': 0,
            'results': results
        }
        
        # 计算总体成功率
        if save_data['total_questions'] > 0:
            save_data['overall_success_rate'] = save_data['total_valid_responses'] / save_data['total_questions'] * 100
        
        # 保存JSON文件
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2, default=str)
        
        # 保存Pickle文件
        pkl_filename = filename.replace('.json', '.pkl')
        with open(pkl_filename, 'wb') as f:
            pickle.dump(save_data, f)
        
        print(f"结果已保存:")
        print(f"  JSON: {filename}")
        print(f"  PKL: {pkl_filename}")
        
        return filename, pkl_filename
    
    def print_summary(self, results: List[Dict[str, Any]]):
        """打印结果摘要"""
        print(f"\\n=== 访谈结果摘要 ===")
        
        total_tasks = len(results)
        successful_tasks = sum(1 for r in results if 'error' not in r)
        total_questions = sum(r.get('total_questions', 0) for r in results)
        total_valid = sum(r.get('valid_responses', 0) for r in results)
        
        print(f"总任务数: {total_tasks}")
        print(f"成功任务数: {successful_tasks}")
        print(f"总问题数: {total_questions}")
        print(f"有效回答数: {total_valid}")
        print(f"总体成功率: {total_valid/total_questions*100:.1f}%" if total_questions > 0 else "总体成功率: 0%")
        
        # 按模型统计
        print(f"\\n=== 按模型统计 ===")
        model_stats = {}
        for result in results:
            model = result['model_name']
            if model not in model_stats:
                model_stats[model] = {'total': 0, 'valid': 0, 'tasks': 0}
            model_stats[model]['total'] += result.get('total_questions', 0)
            model_stats[model]['valid'] += result.get('valid_responses', 0)
            model_stats[model]['tasks'] += 1
        
        for model, stats in model_stats.items():
            success_rate = stats['valid'] / stats['total'] * 100 if stats['total'] > 0 else 0
            print(f"{model:30s}: {stats['valid']:3d}/{stats['total']:3d} ({success_rate:5.1f}%) - {stats['tasks']:2d} 任务")

def main():
    """主函数"""
    print("=== 并发Roleplay访谈系统 ===")
    
    # 创建并发访谈器
    interviewer = ConcurrentRoleplayInterview(max_workers=8)  # 可以调整并发数
    
    # 运行访谈
    results = interviewer.run_concurrent_interviews()
    
    # 保存结果
    json_file, pkl_file = interviewer.save_results(results)
    
    # 打印摘要
    interviewer.print_summary(results)
    
    print(f"\\n访谈完成! 结果已保存到:")
    print(f"  {json_file}")
    print(f"  {pkl_file}")

if __name__ == "__main__":
    main()
