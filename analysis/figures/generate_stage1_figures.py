#!/usr/bin/env python3
"""
生成Stage1分析图表 - 支持中文显示
生成以下图表:
1. stage1_consistency_bar.png - 各问题一致性柱状图
2. stage1_diversity_bar.png - 各问题多样性柱状图
3. stage1_response_heatmap.png - 模型回答热力图
"""

import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import pandas as pd
import pickle
import seaborn as sns
from pathlib import Path
from collections import Counter

# 设置中文字体 - Windows
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 如果上面的字体不工作，尝试使用英文
USE_ENGLISH = True  # 设置为True使用英文标签

# 输出目录
output_dir = Path('results/stage1_analysis')
output_dir.mkdir(parents=True, exist_ok=True)

# 问题信息 (基于WVS官网定义)
QUESTION_INFO = {
    'A008': {'cn': '幸福感', 'en': 'Happiness', 'scale': '1-4'},
    'A165': {'cn': '人际信任', 'en': 'Trust', 'scale': '1-2'},
    'E018': {'cn': '权威尊重', 'en': 'Authority Respect', 'scale': '1-3'},
    'E025': {'cn': '签署请愿', 'en': 'Signing Petition', 'scale': '1-3'},
    'F063': {'cn': '上帝重要性', 'en': 'God Importance', 'scale': '1-10'},
    'F118': {'cn': '同性恋可接受度', 'en': 'Homosexuality', 'scale': '1-10'},
    'F120': {'cn': '堕胎可接受度', 'en': 'Abortion', 'scale': '1-10'},
    'G006': {'cn': '国家自豪感', 'en': 'National Pride', 'scale': '1-4'},
    'Y002': {'cn': '后物质主义指数', 'en': 'Post-Materialist Index', 'scale': 'multi'},
    'Y003': {'cn': '自主性指数', 'en': 'Autonomy Index', 'scale': 'multi'},
}

def load_stage1_data():
    """加载Stage1数据"""
    data_dir = Path("data/llm_values/interview_raw")
    
    if not data_dir.exists():
        print(f"⚠️ 数据目录不存在: {data_dir}")
        return {}
    
    individual_files = [f for f in data_dir.glob("*.pkl") 
                       if not f.name.startswith("llm_interview_raw_")]
    
    models_data = {}
    for file_path in individual_files:
        try:
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
            model_name = data.get('model_name', '')
            if model_name:
                models_data[model_name] = data
        except Exception as e:
            print(f"⚠️ 加载失败 {file_path}: {e}")
    
    return models_data

def extract_responses(model_data):
    """提取模型的回答"""
    responses = {}
    for r in model_data.get('responses', []):
        qid = r.get('question_id')
        answer = r.get('final_response') or r.get('processed_response') or r.get('response')
        responses[qid] = answer
    return responses

def calculate_consistency_diversity(models_data):
    """计算每个问题的一致性和多样性"""
    all_responses = {}
    for model_name, model_data in models_data.items():
        all_responses[model_name] = extract_responses(model_data)
    
    question_ids = ['A008', 'A165', 'E018', 'E025', 'F063', 'F118', 'F120', 'G006', 'Y002', 'Y003']
    
    results = []
    for qid in question_ids:
        values = []
        for model, responses in all_responses.items():
            if qid in responses and responses[qid] is not None:
                val = responses[qid]
                if isinstance(val, list):
                    val = tuple(sorted(val))
                values.append(val)
        
        if values:
            counter = Counter(values)
            most_common_count = counter.most_common(1)[0][1]
            consistency = most_common_count / len(values) * 100
            unique_count = len(counter)
            diversity = unique_count / len(values) * 100
        else:
            consistency = 0
            diversity = 0
            unique_count = 0
        
        results.append({
            'question_id': qid,
            'question_name': QUESTION_INFO[qid]['en'] if USE_ENGLISH else QUESTION_INFO[qid]['cn'],
            'consistency': consistency,
            'diversity': diversity,
            'unique_count': unique_count,
            'total_responses': len(values)
        })
    
    return pd.DataFrame(results), all_responses

def create_consistency_bar(df):
    """生成一致性柱状图"""
    print("生成一致性柱状图...")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    colors = ['#27AE60' if x >= 70 else '#F39C12' if x >= 50 else '#E74C3C' 
              for x in df['consistency']]
    
    bars = ax.bar(range(len(df)), df['consistency'], color=colors, 
                  edgecolor='black', linewidth=1.5, alpha=0.8)
    
    ax.set_xticks(range(len(df)))
    ax.set_xticklabels(df['question_name'], rotation=45, ha='right', fontsize=10)
    ax.set_ylabel('Consistency (%)' if USE_ENGLISH else '一致性 (%)', fontsize=12)
    ax.set_xlabel('Question' if USE_ENGLISH else '问题', fontsize=12)
    ax.set_title('Stage1: Model Response Consistency by Question' if USE_ENGLISH else 
                 'Stage1: 各问题模型回答一致性', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.axhline(50, color='gray', linestyle='--', alpha=0.5, label='50% threshold')
    ax.grid(axis='y', alpha=0.3)
    
    # 添加数值标签
    for bar, val in zip(bars, df['consistency']):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
               f'{val:.0f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'stage1_consistency_bar.png', dpi=300, bbox_inches='tight')
    print(f"✅ 保存: stage1_consistency_bar.png")
    plt.close()

def create_diversity_bar(df):
    """生成多样性柱状图"""
    print("生成多样性柱状图...")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    colors = ['#E74C3C' if x >= 50 else '#F39C12' if x >= 30 else '#27AE60' 
              for x in df['diversity']]
    
    bars = ax.bar(range(len(df)), df['diversity'], color=colors,
                  edgecolor='black', linewidth=1.5, alpha=0.8)
    
    ax.set_xticks(range(len(df)))
    ax.set_xticklabels(df['question_name'], rotation=45, ha='right', fontsize=10)
    ax.set_ylabel('Diversity (%)' if USE_ENGLISH else '多样性 (%)', fontsize=12)
    ax.set_xlabel('Question' if USE_ENGLISH else '问题', fontsize=12)
    ax.set_title('Stage1: Model Response Diversity by Question' if USE_ENGLISH else
                 'Stage1: 各问题模型回答多样性', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.grid(axis='y', alpha=0.3)
    
    # 添加数值标签
    for bar, val in zip(bars, df['diversity']):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
               f'{val:.0f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'stage1_diversity_bar.png', dpi=300, bbox_inches='tight')
    print(f"✅ 保存: stage1_diversity_bar.png")
    plt.close()

def create_response_heatmap(all_responses):
    """生成模型回答热力图"""
    print("生成模型回答热力图...")
    
    question_ids = ['A008', 'A165', 'E018', 'E025', 'F063', 'F118', 'F120', 'G006']
    question_names = [QUESTION_INFO[qid]['en'] if USE_ENGLISH else QUESTION_INFO[qid]['cn'] 
                      for qid in question_ids]
    
    # 构建数据矩阵
    models = sorted(all_responses.keys())
    data_matrix = []
    
    for model in models:
        row = []
        for qid in question_ids:
            val = all_responses[model].get(qid)
            if val is not None and not isinstance(val, list):
                row.append(float(val))
            else:
                row.append(np.nan)
        data_matrix.append(row)
    
    df_heatmap = pd.DataFrame(data_matrix, index=models, columns=question_names)
    
    # 标准化每列到0-1范围
    df_normalized = df_heatmap.copy()
    for col in df_normalized.columns:
        col_min = df_normalized[col].min()
        col_max = df_normalized[col].max()
        if col_max > col_min:
            df_normalized[col] = (df_normalized[col] - col_min) / (col_max - col_min)
    
    fig, ax = plt.subplots(figsize=(14, 10))
    
    sns.heatmap(df_normalized, annot=df_heatmap, fmt='.0f', cmap='RdYlGn_r',
                linewidths=0.5, ax=ax, cbar_kws={'label': 'Normalized Value'})
    
    ax.set_title('Stage1: Model Response Heatmap (Normalized)' if USE_ENGLISH else
                 'Stage1: 模型回答热力图（标准化）', fontsize=14, fontweight='bold')
    ax.set_xlabel('Question' if USE_ENGLISH else '问题', fontsize=12)
    ax.set_ylabel('Model' if USE_ENGLISH else '模型', fontsize=12)
    
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'stage1_response_heatmap.png', dpi=300, bbox_inches='tight')
    print(f"✅ 保存: stage1_response_heatmap.png")
    plt.close()

def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("Stage1 分析图表生成")
    print("=" * 80)
    
    # 加载数据
    models_data = load_stage1_data()
    print(f"✅ 加载了 {len(models_data)} 个模型的数据")
    
    if len(models_data) == 0:
        print("⚠️ 没有找到Stage1数据，无法生成图表")
        return
    
    # 计算一致性和多样性
    df, all_responses = calculate_consistency_diversity(models_data)
    
    print("\n问题一致性统计:")
    print(df[['question_name', 'consistency', 'diversity', 'unique_count']].to_string(index=False))
    
    # 生成图表
    create_consistency_bar(df)
    create_diversity_bar(df)
    create_response_heatmap(all_responses)
    
    print(f"\n✅ 所有图表已保存到: {output_dir}")
    print("=" * 80)

if __name__ == '__main__':
    main()
