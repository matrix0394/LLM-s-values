#!/usr/bin/env python3
"""
可视化roleplay分析结果
"""

import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def create_visualizations():
    """创建可视化图表"""
    
    # 加载分析结果
    with open('results/roleplay_analysis_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 创建图表
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Roleplay回答分析结果', fontsize=16, fontweight='bold')
    
    # 1. 问题难度分析
    question_data = data['question_difficulty']
    questions = [q['question_id'] for q in question_data]
    ones_rates = [q['ones_rate'] for q in question_data]
    
    bars1 = ax1.bar(questions, ones_rates, color='red', alpha=0.7)
    ax1.set_title('各问题回答"1"的比例', fontsize=12, fontweight='bold')
    ax1.set_xlabel('问题ID')
    ax1.set_ylabel('回答"1"的比例 (%)')
    ax1.tick_params(axis='x', rotation=45)
    
    # 添加数值标签
    for bar, rate in zip(bars1, ones_rates):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{rate:.1f}%', ha='center', va='bottom', fontsize=8)
    
    # 2. 国家难度分析（前15个）
    country_data = data['country_difficulty'][:15]
    countries = [c['country'] for c in country_data]
    country_ones_rates = [c['ones_rate'] for c in country_data]
    
    bars2 = ax2.barh(countries, country_ones_rates, color='orange', alpha=0.7)
    ax2.set_title('各国家回答"1"的比例（前15个）', fontsize=12, fontweight='bold')
    ax2.set_xlabel('回答"1"的比例 (%)')
    ax2.set_ylabel('国家')
    
    # 添加数值标签
    for bar, rate in zip(bars2, country_ones_rates):
        width = bar.get_width()
        ax2.text(width + 1, bar.get_y() + bar.get_height()/2.,
                f'{rate:.1f}%', ha='left', va='center', fontsize=8)
    
    # 3. 模型表现对比
    model_data = data['model_stats']
    models = list(model_data.keys())
    model_ones_rates = [model_data[model]['ones'] / model_data[model]['total'] * 100 for model in models]
    
    bars3 = ax3.bar(models, model_ones_rates, color=['blue', 'green'], alpha=0.7)
    ax3.set_title('模型表现对比', fontsize=12, fontweight='bold')
    ax3.set_xlabel('模型')
    ax3.set_ylabel('回答"1"的比例 (%)')
    ax3.tick_params(axis='x', rotation=45)
    
    # 添加数值标签
    for bar, rate in zip(bars3, model_ones_rates):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{rate:.1f}%', ha='center', va='bottom', fontsize=10)
    
    # 4. 问题类型分布
    question_types = {
        '政治相关': ['E018', 'E025'],
        '宗教相关': ['A165', 'F063'],
        '性别相关': ['G006'],
        '生活相关': ['A008', 'F118', 'F120'],
        '教育相关': ['Y002', 'Y003']
    }
    
    type_rates = []
    type_labels = []
    for type_name, q_ids in question_types.items():
        type_questions = [q for q in question_data if q['question_id'] in q_ids]
        if type_questions:
            avg_rate = sum(q['ones_rate'] for q in type_questions) / len(type_questions)
            type_rates.append(avg_rate)
            type_labels.append(type_name)
    
    bars4 = ax4.bar(type_labels, type_rates, color=['purple', 'brown', 'pink', 'cyan', 'yellow'], alpha=0.7)
    ax4.set_title('问题类型平均难度', fontsize=12, fontweight='bold')
    ax4.set_xlabel('问题类型')
    ax4.set_ylabel('平均回答"1"的比例 (%)')
    ax4.tick_params(axis='x', rotation=45)
    
    # 添加数值标签
    for bar, rate in zip(bars4, type_rates):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{rate:.1f}%', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('results/roleplay_analysis_visualization.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("可视化图表已保存到: results/roleplay_analysis_visualization.png")

if __name__ == "__main__":
    create_visualizations()
