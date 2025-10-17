#!/usr/bin/env python3
"""
运行所有国家的roleplay访谈 - 简化版
"""

import sys
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import pickle

# 添加src路径
sys.path.append('src')

from llm_country_roleplay_interview import LLMCountryRoleplayInterview

def get_countries_from_valid_data():
    """从valid_data获取国家列表"""
    try:
        # 尝试读取valid_data.pkl
        with open('data/valid_data.pkl', 'rb') as f:
            data = pickle.load(f)
        
        # 检查数据结构
        if hasattr(data, 'columns'):
            if 'Country' in data.columns:
                countries = data['Country'].unique().tolist()
                print(f"从valid_data加载了 {len(countries)} 个国家")
                return countries
            elif 'country' in data.columns:
                countries = data['country'].unique().tolist()
                print(f"从valid_data加载了 {len(countries)} 个国家")
                return countries
        
        # 如果找不到Country列，尝试其他可能的列名
        print("未找到Country列，尝试其他列名...")
        print(f"可用列: {list(data.columns) if hasattr(data, 'columns') else 'N/A'}")
        
    except Exception as e:
        print(f"读取valid_data失败: {e}")
    
    # 返回默认国家列表
    default_countries = [
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
    
    print(f"使用默认国家列表: {len(default_countries)} 个国家")
    return default_countries

def interview_country_model(country, model, question_ids):
    """访谈单个国家-模型组合"""
    try:
        print(f"开始: {model} -> {country}")
        
        # 创建访谈器
        interview = LLMCountryRoleplayInterview()
        
        # 访谈所有问题
        responses = []
        valid_count = 0
        
        for question_id in question_ids:
            try:
                response = interview.ask_question_roleplay(model, country, question_id)
                responses.append(response)
                if response.is_valid:
                    valid_count += 1
            except Exception as e:
                print(f"  问题 {question_id} 失败: {e}")
                responses.append(None)
        
        result = {
            'model': model,
            'country': country,
            'timestamp': time.strftime('%Y%m%d_%H%M%S'),
            'total_questions': len(question_ids),
            'valid_responses': valid_count,
            'success_rate': valid_count / len(question_ids) * 100,
            'responses': responses
        }
        
        print(f"完成: {model} -> {country} ({valid_count}/{len(question_ids)})")
        return result
        
    except Exception as e:
        print(f"失败: {model} -> {country}: {e}")
        return {
            'model': model,
            'country': country,
            'timestamp': time.strftime('%Y%m%d_%H%M%S'),
            'error': str(e),
            'total_questions': 0,
            'valid_responses': 0,
            'success_rate': 0,
            'responses': []
        }

def main():
    """主函数"""
    print("=== 运行所有国家的Roleplay访谈 ===")
    
    # 获取国家列表
    countries = get_countries_from_valid_data()
    
    # 获取模型列表
    interview = LLMCountryRoleplayInterview()
    models = list(interview.model_configs.keys())
    
    # 问题列表
    question_ids = ['A008', 'A165', 'E018', 'E025', 'F063', 'F118', 'F120', 'G006', 'Y002', 'Y003']
    
    print(f"配置:")
    print(f"  国家数量: {len(countries)}")
    print(f"  模型数量: {len(models)}")
    print(f"  问题数量: {len(question_ids)}")
    print(f"  总任务数: {len(countries) * len(models)}")
    
    # 创建任务列表
    tasks = []
    for model in models:
        for country in countries:
            tasks.append((model, country))
    
    # 并发执行
    results = []
    start_time = time.time()
    
    # 使用线程池并发执行
    with ThreadPoolExecutor(max_workers=6) as executor:  # 可以调整并发数
        # 提交所有任务
        future_to_task = {
            executor.submit(interview_country_model, country, model, question_ids): (model, country)
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
                    'model': model,
                    'country': country,
                    'timestamp': time.strftime('%Y%m%d_%H%M%S'),
                    'error': str(e),
                    'total_questions': 0,
                    'valid_responses': 0,
                    'success_rate': 0,
                    'responses': []
                })
    
    total_time = time.time() - start_time
    print(f"\\n所有访谈完成! 总用时: {total_time:.1f}s")
    
    # 保存结果
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    
    # 保存JSON
    json_file = f'data/llm_responses_roleplay/all_countries_roleplay_{timestamp}.json'
    os.makedirs(os.path.dirname(json_file), exist_ok=True)
    
    save_data = {
        'timestamp': timestamp,
        'total_tasks': len(results),
        'successful_tasks': sum(1 for r in results if 'error' not in r),
        'total_questions': sum(r.get('total_questions', 0) for r in results),
        'total_valid_responses': sum(r.get('valid_responses', 0) for r in results),
        'overall_success_rate': 0,
        'results': results
    }
    
    if save_data['total_questions'] > 0:
        save_data['overall_success_rate'] = save_data['total_valid_responses'] / save_data['total_questions'] * 100
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2, default=str)
    
    # 保存PKL
    pkl_file = json_file.replace('.json', '.pkl')
    with open(pkl_file, 'wb') as f:
        pickle.dump(save_data, f)
    
    # 打印摘要
    print(f"\\n=== 结果摘要 ===")
    print(f"总任务数: {save_data['total_tasks']}")
    print(f"成功任务数: {save_data['successful_tasks']}")
    print(f"总问题数: {save_data['total_questions']}")
    print(f"有效回答数: {save_data['total_valid_responses']}")
    print(f"总体成功率: {save_data['overall_success_rate']:.1f}%")
    
    # 按模型统计
    print(f"\\n=== 按模型统计 ===")
    model_stats = {}
    for result in results:
        model = result['model']
        if model not in model_stats:
            model_stats[model] = {'total': 0, 'valid': 0, 'tasks': 0}
        model_stats[model]['total'] += result.get('total_questions', 0)
        model_stats[model]['valid'] += result.get('valid_responses', 0)
        model_stats[model]['tasks'] += 1
    
    for model, stats in model_stats.items():
        success_rate = stats['valid'] / stats['total'] * 100 if stats['total'] > 0 else 0
        print(f"{model:30s}: {stats['valid']:3d}/{stats['total']:3d} ({success_rate:5.1f}%) - {stats['tasks']:2d} 任务")
    
    print(f"\\n结果已保存:")
    print(f"  JSON: {json_file}")
    print(f"  PKL: {pkl_file}")

if __name__ == "__main__":
    main()
