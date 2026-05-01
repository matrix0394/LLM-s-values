"""
分析Stage3的角色扮演效果
评估各模型模仿不同国家的表现是否到位
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import pickle
import json
from collections import defaultdict, Counter
import pandas as pd

# 国家的典型价值观特征（基于IVS真实数据）
COUNTRY_PROFILES = {
    'United States': {
        'region': 'English Speaking',
        'expected': {
            'F063': (5, 8, '宗教性中等偏高'),  # 美国相对重视宗教
            'F118': (6, 9, '同性恋接受度较高'),  # 美国较开放
            'F120': (5, 8, '堕胎接受度中等偏高'),
            'G006': (1, 2, '国家自豪感强'),  # 美国人通常很自豪
            'E018': (2, 3, '对权威态度中立偏反对'),
            'Y002': 'postmaterialist'  # 后物质主义
        }
    },
    'China': {
        'region': 'Confucian',
        'expected': {
            'F063': (1, 3, '宗教性低'),  # 中国不太重视宗教
            'F118': (2, 5, '同性恋接受度较低'),  # 相对保守
            'F120': (3, 6, '堕胎接受度中等'),
            'G006': (1, 2, '国家自豪感强'),
            'E018': (1, 2, '支持尊重权威'),  # 儒家文化
            'Y002': 'materialist'  # 物质主义
        }
    },
    'Argentina': {
        'region': 'Latin America',
        'expected': {
            'F063': (6, 9, '宗教性较高'),  # 拉美天主教文化
            'F118': (4, 7, '同性恋接受度中等'),
            'F120': (3, 6, '堕胎接受度中等偏低'),
            'G006': (1, 2, '国家自豪感强'),
            'E018': (1, 2, '支持尊重权威'),
            'Y002': 'mixed'
        }
    },
    'Albania': {
        'region': 'Orthodox Europe',
        'expected': {
            'F063': (5, 8, '宗教性中等'),
            'F118': (3, 6, '同性恋接受度中等偏低'),
            'F120': (3, 6, '堕胎接受度中等偏低'),
            'G006': (1, 2, '国家自豪感较强'),
            'E018': (1, 2, '支持尊重权威'),
            'Y002': 'materialist'
        }
    }
}

def load_stage3_data():
    """加载Stage3的所有角色扮演数据"""
    data_dir = Path("data/roleplay_multilingual/llm_responses_roleplay_ml")
    
    # 只加载独立文件
    individual_files = [f for f in data_dir.glob("*.pkl") 
                       if not f.name.startswith("roleplay_results_ml_")]
    
    print(f"🔍 找到 {len(individual_files)} 个Stage3独立文件")
    
    data_by_model = defaultdict(list)
    
    for file_path in individual_files:
        try:
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
            
            model = data.get('model') or data.get('model_name', '')
            country_data = data.get('country', {})
            language = data.get('language', '')
            
            # 提取国家名
            if isinstance(country_data, dict):
                country = country_data.get('name', '')
            else:
                country = str(country_data)
            
            if model and country:
                data_by_model[model].append({
                    'country': country,
                    'language': language,
                    'data': data,
                    'file': file_path.name
                })
        except Exception as e:
            print(f"❌ 加载失败 {file_path.name}: {e}")
    
    return data_by_model

def extract_responses(data):
    """提取回答"""
    responses = {}
    for r in data.get('responses', []):
        qid = r.get('question_id')
        answer = r.get('final_response') or r.get('processed_response') or r.get('response')
        responses[qid] = answer
    return responses

def check_roleplay_quality(model, country, language, responses):
    """检查角色扮演质量"""
    if country not in COUNTRY_PROFILES:
        return None, [], []
    
    profile = COUNTRY_PROFILES[country]
    expected = profile['expected']
    issues = []
    good_points = []
    
    # 检查关键问题
    for qid in expected.keys():
        if qid == 'Y002':
            continue  # Y002单独处理
        
        if qid in responses and responses[qid] is not None:
            actual = responses[qid]
            min_val, max_val, desc = expected[qid]
            
            if isinstance(actual, (int, float)):
                if min_val <= actual <= max_val:
                    good_points.append(f"{qid}={actual} ✅ {desc}")
                else:
                    issues.append(f"{qid}={actual} ⚠️ 不符合{desc}（期望{min_val}-{max_val}）")
    
    # 检查Y002价值观
    if 'Y002' in responses and responses['Y002'] is not None and 'Y002' in expected:
        y002_answer = responses['Y002']
        expected_type = expected['Y002']
        
        # 处理字符串格式 "1 3" 或列表格式 [1, 3]
        if isinstance(y002_answer, str):
            try:
                y002_list = [int(x) for x in y002_answer.split()]
            except:
                y002_list = []
        elif isinstance(y002_answer, list):
            y002_list = y002_answer
        else:
            y002_list = []
        
        if len(y002_list) == 2:
            materialist = set([1, 3])
            postmaterialist = set([2, 4])
            
            if set(y002_list) == materialist:
                actual_type = 'materialist'
            elif set(y002_list) == postmaterialist:
                actual_type = 'postmaterialist'
            else:
                actual_type = 'mixed'
            
            if expected_type == actual_type or expected_type == 'mixed':
                good_points.append(f"Y002={y002_list} ✅ {actual_type}")
            else:
                issues.append(f"Y002={y002_list} ⚠️ {actual_type}，期望{expected_type}")
    
    # 计算符合度
    total_checks = len(issues) + len(good_points)
    if total_checks > 0:
        accuracy = len(good_points) / total_checks
    else:
        accuracy = 0
    
    return accuracy, issues, good_points

def analyze_model_performance(model_name, tasks):
    """分析单个模型的表现"""
    print(f"\n{'='*80}")
    print(f"🤖 {model_name}")
    print(f"{'='*80}")
    print(f"任务数: {len(tasks)}")
    
    results = []
    
    for task in tasks:
        country = task['country']
        language = task['language']
        responses = extract_responses(task['data'])
        
        print(f"\n📍 {country} ({language})")
        print(f"{'─'*80}")
        
        # 显示关键回答
        key_questions = ['F063', 'F118', 'F120', 'G006', 'E018', 'Y002']
        print(f"关键回答:")
        for qid in key_questions:
            if qid in responses:
                print(f"   {qid}: {responses[qid]}")
        
        # 检查角色扮演质量
        accuracy, issues, good_points = check_roleplay_quality(
            model_name, country, language, responses
        )
        
        if accuracy is not None:
            print(f"\n角色扮演质量: {accuracy:.1%}")
            
            if good_points:
                print(f"✅ 符合预期:")
                for point in good_points[:3]:  # 只显示前3个
                    print(f"   • {point}")
            
            if issues:
                print(f"⚠️ 不符合预期:")
                for issue in issues:
                    print(f"   • {issue}")
            
            results.append({
                'country': country,
                'language': language,
                'accuracy': accuracy,
                'issues_count': len(issues)
            })
        else:
            print(f"ℹ️ 暂无此国家的基准数据")
    
    # 总结
    if results:
        avg_accuracy = sum(r['accuracy'] for r in results) / len(results)
        print(f"\n{'─'*80}")
        print(f"📊 {model_name} 总体表现:")
        print(f"   平均符合度: {avg_accuracy:.1%}")
        print(f"   最佳表现: {max(results, key=lambda x: x['accuracy'])['country']} ({max(r['accuracy'] for r in results):.1%})")
        print(f"   最差表现: {min(results, key=lambda x: x['accuracy'])['country']} ({min(r['accuracy'] for r in results):.1%})")
    
    return results

def compare_models(all_results):
    """对比所有模型的表现"""
    print(f"\n{'='*80}")
    print(f"📊 模型对比总结")
    print(f"{'='*80}")
    
    model_scores = {}
    for model, results in all_results.items():
        if results:
            avg = sum(r['accuracy'] for r in results) / len(results)
            model_scores[model] = avg
    
    # 排序
    sorted_models = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\n角色扮演能力排名:")
    for i, (model, score) in enumerate(sorted_models, 1):
        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "📌"
        print(f"{emoji} {i}. {model}: {score:.1%}")

def analyze_stage1_vs_stage3(model_name):
    """对比同一模型在Stage1和Stage3的回答差异"""
    print(f"\n{'='*80}")
    print(f"🔄 {model_name}: Stage1 vs Stage3 对比")
    print(f"{'='*80}")
    
    # 加载Stage1数据
    stage1_dir = Path("data/llm_values/interview_raw")
    stage1_files = [f for f in stage1_dir.glob(f"{model_name}*.pkl")]
    
    if not stage1_files:
        print(f"⚠️ 未找到Stage1数据")
        return
    
    with open(stage1_files[0], 'rb') as f:
        stage1_data = pickle.load(f)
    
    stage1_responses = extract_responses(stage1_data)
    
    # 加载Stage3数据
    stage3_dir = Path("data/roleplay_multilingual/llm_responses_roleplay_ml")
    stage3_files = [f for f in stage3_dir.glob(f"{model_name}*.pkl")]
    
    if not stage3_files:
        print(f"⚠️ 未找到Stage3数据")
        return
    
    print(f"\nStage1 (无角色) vs Stage3 (角色扮演) 回答对比:")
    print(f"{'─'*80}")
    
    # 对比每个国家
    for file_path in stage3_files[:4]:  # 只显示前4个
        with open(file_path, 'rb') as f:
            stage3_data = pickle.load(f)
        
        country_data = stage3_data.get('country', {})
        country = country_data.get('name', '') if isinstance(country_data, dict) else str(country_data)
        language = stage3_data.get('language', '')
        
        stage3_responses = extract_responses(stage3_data)
        
        print(f"\n📍 {country} ({language}):")
        
        key_questions = ['F063', 'F118', 'G006', 'Y002']
        for qid in key_questions:
            s1 = stage1_responses.get(qid, 'N/A')
            s3 = stage3_responses.get(qid, 'N/A')
            
            if s1 != s3:
                print(f"   {qid}: Stage1={s1} → Stage3={s3} {'✅ 有变化' if s1 != 'N/A' and s3 != 'N/A' else ''}")
            else:
                print(f"   {qid}: {s1} ⚠️ 无变化（角色扮演可能无效）")

def main():
    """主函数"""
    print("\n" + "="*80)
    print("🎭 Stage3: 角色扮演质量分析")
    print("="*80)
    
    # 加载数据
    data_by_model = load_stage3_data()
    
    print(f"\n✅ 加载了 {len(data_by_model)} 个模型的数据")
    for model, tasks in data_by_model.items():
        print(f"   • {model}: {len(tasks)} 个任务")
    
    # 分析每个模型
    all_results = {}
    for model, tasks in data_by_model.items():
        results = analyze_model_performance(model, tasks)
        all_results[model] = results
    
    # 对比模型
    compare_models(all_results)
    
    # Stage1 vs Stage3对比
    for model in data_by_model.keys():
        analyze_stage1_vs_stage3(model)
        break  # 只分析第一个模型作为示例
    
    print("\n" + "="*80)
    print("✅ 分析完成")
    print("="*80)

if __name__ == "__main__":
    main()
