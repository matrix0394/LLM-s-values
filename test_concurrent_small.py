#!/usr/bin/env python3
"""
测试小规模并发访谈
"""

import sys
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

# 添加src路径
sys.path.append('src')

from llm_country_roleplay_interview import LLMCountryRoleplayInterview

def interview_single(model, country, question_id):
    """访谈单个问题"""
    try:
        interview = LLMCountryRoleplayInterview()
        response = interview.ask_question_roleplay(model, country, question_id)
        return {
            'model': model,
            'country': country,
            'question': question_id,
            'response': response.raw_response,
            'valid': response.is_valid,
            'error': response.error_message
        }
    except Exception as e:
        return {
            'model': model,
            'country': country,
            'question': question_id,
            'response': None,
            'valid': False,
            'error': str(e)
        }

def main():
    """主函数"""
    print("=== 测试小规模并发访谈 ===")
    
    # 测试配置
    models = ['openai/gpt-4o-mini', 'google/gemini-2.0-flash-001']
    countries = ['United States', 'China', 'Germany']
    questions = ['A008', 'A165', 'E018']
    
    print(f"测试配置:")
    print(f"  模型: {models}")
    print(f"  国家: {countries}")
    print(f"  问题: {questions}")
    print(f"  总任务数: {len(models) * len(countries) * len(questions)}")
    
    # 创建任务列表
    tasks = []
    for model in models:
        for country in countries:
            for question in questions:
                tasks.append((model, country, question))
    
    # 并发执行
    results = []
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        # 提交所有任务
        future_to_task = {
            executor.submit(interview_single, model, country, question): (model, country, question)
            for model, country, question in tasks
        }
        
        # 收集结果
        completed = 0
        for future in as_completed(future_to_task):
            model, country, question = future_to_task[future]
            try:
                result = future.result()
                results.append(result)
                completed += 1
                
                # 显示进度
                progress = completed / len(tasks) * 100
                elapsed = time.time() - start_time
                
                status = "✅" if result['valid'] else "❌"
                print(f"进度: {completed}/{len(tasks)} ({progress:.1f}%) - {status} {model} -> {country} -> {question}: {result['response']}")
                
            except Exception as e:
                print(f"任务失败: {model} -> {country} -> {question}: {e}")
                results.append({
                    'model': model,
                    'country': country,
                    'question': question,
                    'response': None,
                    'valid': False,
                    'error': str(e)
                })
    
    total_time = time.time() - start_time
    print(f"\\n所有任务完成! 总用时: {total_time:.1f}s")
    
    # 统计结果
    total_tasks = len(results)
    valid_tasks = sum(1 for r in results if r['valid'])
    success_rate = valid_tasks / total_tasks * 100 if total_tasks > 0 else 0
    
    print(f"\\n=== 结果统计 ===")
    print(f"总任务数: {total_tasks}")
    print(f"成功任务数: {valid_tasks}")
    print(f"成功率: {success_rate:.1f}%")
    
    # 按模型统计
    print(f"\\n=== 按模型统计 ===")
    model_stats = {}
    for result in results:
        model = result['model']
        if model not in model_stats:
            model_stats[model] = {'total': 0, 'valid': 0}
        model_stats[model]['total'] += 1
        if result['valid']:
            model_stats[model]['valid'] += 1
    
    for model, stats in model_stats.items():
        rate = stats['valid'] / stats['total'] * 100 if stats['total'] > 0 else 0
        print(f"{model:30s}: {stats['valid']:2d}/{stats['total']:2d} ({rate:5.1f}%)")
    
    # 保存结果
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    filename = f'data/llm_responses_roleplay/test_concurrent_{timestamp}.json'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': timestamp,
            'total_tasks': total_tasks,
            'valid_tasks': valid_tasks,
            'success_rate': success_rate,
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\\n结果已保存到: {filename}")

if __name__ == "__main__":
    main()
