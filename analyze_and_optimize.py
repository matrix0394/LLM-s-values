#!/usr/bin/env python3
"""
分析roleplay回答效果并生成针对性优化建议
"""

import sys
import os
import json
import pickle
from collections import defaultdict, Counter
from typing import Dict, List, Any, Tuple

# 添加src路径
sys.path.append('src')

def analyze_roleplay_results(results_file: str = None):
    """分析roleplay结果"""
    if results_file is None:
        # 查找最新的结果文件
        results_dir = 'data/llm_responses_roleplay'
        json_files = [f for f in os.listdir(results_dir) if f.startswith('roleplay_results') and f.endswith('.json')]
        if not json_files:
            print("未找到结果文件")
            return
        
        results_file = os.path.join(results_dir, sorted(json_files)[-1])
    
    print(f"分析文件: {results_file}")
    
    # 加载结果
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = data['results']
    
    print(f"\\n=== 总体统计 ===")
    print(f"总任务数: {data['total_tasks']}")
    print(f"成功任务数: {data['successful_tasks']}")
    print(f"总问题数: {data['total_questions']}")
    print(f"有效回答数: {data['total_valid_responses']}")
    print(f"总体成功率: {data['overall_success_rate']:.1f}%")
    
    # 按模型分析
    print(f"\\n=== 按模型分析 ===")
    model_stats = defaultdict(lambda: {'total': 0, 'valid': 0, 'tasks': 0, 'countries': set()})
    
    for result in results:
        model = result['model']
        model_stats[model]['total'] += result.get('total_questions', 0)
        model_stats[model]['valid'] += result.get('valid_responses', 0)
        model_stats[model]['tasks'] += 1
        model_stats[model]['countries'].add(result['country'])
    
    model_performance = []
    for model, stats in model_stats.items():
        success_rate = stats['valid'] / stats['total'] * 100 if stats['total'] > 0 else 0
        model_performance.append((model, success_rate, stats))
        print(f"{model:30s}: {stats['valid']:3d}/{stats['total']:3d} ({success_rate:5.1f}%) - {stats['tasks']:2d} 任务")
    
    # 按国家分析
    print(f"\\n=== 按国家分析 ===")
    country_stats = defaultdict(lambda: {'total': 0, 'valid': 0, 'models': set(), 'success_rates': []})
    
    for result in results:
        country = result['country']
        country_stats[country]['total'] += result.get('total_questions', 0)
        country_stats[country]['valid'] += result.get('valid_responses', 0)
        country_stats[country]['models'].add(result['model'])
        country_stats[country]['success_rates'].append(result.get('success_rate', 0))
    
    country_performance = []
    for country, stats in country_stats.items():
        avg_success_rate = sum(stats['success_rates']) / len(stats['success_rates']) if stats['success_rates'] else 0
        country_performance.append((country, avg_success_rate, stats))
    
    # 按成功率排序
    country_performance.sort(key=lambda x: x[1])
    
    print("成功率最低的10个国家:")
    for country, avg_rate, stats in country_performance[:10]:
        print(f"  {country:20s}: {avg_rate:5.1f}% ({len(stats['models'])} 个模型)")
    
    print("\\n成功率最高的10个国家:")
    for country, avg_rate, stats in country_performance[-10:]:
        print(f"  {country:20s}: {avg_rate:5.1f}% ({len(stats['models'])} 个模型)")
    
    # 按问题分析
    print(f"\\n=== 按问题分析 ===")
    question_stats = defaultdict(lambda: {'total': 0, 'valid': 0, 'models': set(), 'countries': set()})
    
    for result in results:
        if 'responses' in result:
            for i, response in enumerate(result['responses']):
                if response and hasattr(response, 'question_id'):
                    question_id = response.question_id
                    question_stats[question_id]['total'] += 1
                    if response.is_valid:
                        question_stats[question_id]['valid'] += 1
                    question_stats[question_id]['models'].add(result['model'])
                    question_stats[question_id]['countries'].add(result['country'])
    
    question_performance = []
    for question_id, stats in question_stats.items():
        success_rate = stats['valid'] / stats['total'] * 100 if stats['total'] > 0 else 0
        question_performance.append((question_id, success_rate, stats))
    
    question_performance.sort(key=lambda x: x[1])
    
    print("最难回答的问题:")
    for question_id, success_rate, stats in question_performance[:5]:
        print(f"  {question_id:6s}: {success_rate:5.1f}% ({stats['valid']:3d}/{stats['total']:3d})")
    
    print("\\n最容易回答的问题:")
    for question_id, success_rate, stats in question_performance[-5:]:
        print(f"  {question_id:6s}: {success_rate:5.1f}% ({stats['valid']:3d}/{stats['total']:3d})")
    
    # 识别问题组合
    print(f"\\n=== 问题组合分析 ===")
    problem_combinations = []
    
    for result in results:
        if result.get('success_rate', 0) < 30:  # 成功率低于30%
            problem_combinations.append({
                'model': result['model'],
                'country': result['country'],
                'success_rate': result.get('success_rate', 0),
                'valid_responses': result.get('valid_responses', 0),
                'total_questions': result.get('total_questions', 0)
            })
    
    problem_combinations.sort(key=lambda x: x['success_rate'])
    
    print("成功率低于30%的模型-国家组合 (前20个):")
    for combo in problem_combinations[:20]:
        print(f"  {combo['model']:25s} -> {combo['country']:15s}: {combo['success_rate']:5.1f}% ({combo['valid_responses']}/{combo['total_questions']})")
    
    # 生成优化建议
    generate_optimization_suggestions(model_performance, country_performance, question_performance, problem_combinations)
    
    return {
        'model_performance': model_performance,
        'country_performance': country_performance,
        'question_performance': question_performance,
        'problem_combinations': problem_combinations
    }

def generate_optimization_suggestions(model_perf, country_perf, question_perf, problem_combos):
    """生成优化建议"""
    print(f"\\n=== 优化建议 ===")
    
    # 模型优化建议
    print("\\n1. 模型优化建议:")
    poor_models = [model for model, rate, stats in model_perf if rate < 50]
    if poor_models:
        print(f"   表现较差的模型: {poor_models}")
        print("   建议:")
        print("   - 为这些模型设计更简单的prompt")
        print("   - 增加重试次数")
        print("   - 使用更低的温度参数")
        print("   - 考虑使用不同的API端点")
    
    # 国家优化建议
    print("\\n2. 国家优化建议:")
    poor_countries = [country for country, rate, stats in country_perf if rate < 40]
    if poor_countries:
        print(f"   表现较差的国家: {poor_countries[:10]}")
        print("   建议:")
        print("   - 为这些国家提供更详细的文化背景信息")
        print("   - 使用更具体的身份描述")
        print("   - 增加文化特征描述")
        print("   - 考虑使用不同的身份prompt")
    
    # 问题优化建议
    print("\\n3. 问题优化建议:")
    poor_questions = [q for q, rate, stats in question_perf if rate < 40]
    if poor_questions:
        print(f"   表现较差的问题: {poor_questions}")
        print("   建议:")
        print("   - 为这些问题设计专门的prompt")
        print("   - 提供问题的文化背景解释")
        print("   - 使用更简单的语言描述")
        print("   - 考虑分解复杂问题")
    
    # 组合优化建议
    print("\\n4. 特定组合优化建议:")
    if problem_combos:
        # 按模型分组
        model_problems = defaultdict(list)
        for combo in problem_combos:
            model_problems[combo['model']].append(combo)
        
        for model, combos in model_problems.items():
            if len(combos) > 5:  # 如果该模型有超过5个问题组合
                countries = [combo['country'] for combo in combos]
                print(f"   {model}: 问题国家 {countries[:5]}")
                print(f"     建议: 为该模型设计专门的国家prompt")
    
    # 生成具体的prompt优化代码
    generate_prompt_optimization_code(model_perf, country_perf, problem_combos)

def generate_prompt_optimization_code(model_perf, country_perf, problem_combos):
    """生成具体的prompt优化代码"""
    print(f"\\n=== 生成优化代码 ===")
    
    # 识别需要优化的模型
    poor_models = [model for model, rate, stats in model_perf if rate < 50]
    poor_countries = [country for country, rate, stats in country_perf if rate < 40]
    
    if poor_models or poor_countries:
        print("\\n建议的prompt优化策略:")
        
        if poor_models:
            print("\\n# 为表现较差的模型优化prompt")
            print("def get_optimized_system_prompt_for_model(model_name):")
            print("    if model_name in ['model1', 'model2']:  # 替换为实际的差模型")
            print("        return \"\"\"简化的系统prompt...\"\"\"")
            print("    return default_system_prompt")
        
        if poor_countries:
            print("\\n# 为表现较差的国家优化身份prompt")
            print("def get_optimized_identity_prompt_for_country(country_name):")
            print("    if country_name in ['country1', 'country2']:  # 替换为实际的差国家")
            print("        return \"\"\"更详细的文化身份描述...\"\"\"")
            print("    return default_identity_prompt")
        
        print("\\n# 为特定问题优化prompt")
        print("def get_optimized_question_prompt(question_id):")
        print("    if question_id in ['E018', 'G006']:  # 最难的问题")
        print("        return \"\"\"包含文化背景解释的问题描述...\"\"\"")
        print("    return default_question_prompt")

def main():
    """主函数"""
    print("=== Roleplay结果分析和优化建议 ===")
    
    # 分析结果
    analysis_results = analyze_roleplay_results()
    
    # 保存分析结果
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    analysis_file = f'data/llm_responses_roleplay/analysis_results_{timestamp}.json'
    
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\\n分析结果已保存到: {analysis_file}")

if __name__ == "__main__":
    import time
    main()
