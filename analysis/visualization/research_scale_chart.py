"""
生成研究规模图表
展示Stage 0-3各阶段的研究规模
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 创建图表
fig, ax = plt.subplots(figsize=(14, 6))

# 定义各阶段数据
stages = ['Stage 0\n文化坐标系基准', 'Stage 1\n模型价值观基线', 'Stage 2\n全球文化模仿', 'Stage 3\n多语言对比']
colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']

# 各阶段的关键指标
stage_data = {
    'Stage 0': {
        '国家/地区': 109,
        '数据来源': 'WVS Wave 7',
        '问题数': 10,
        '维度': 2
    },
    'Stage 1': {
        '测试模型': 10,
        '问题数': 10,
        '测试次数': '5次/模型',
        '数据点': 50
    },
    'Stage 2': {
        '国家/地区': 109,
        '测试模型': 10,
        '语言': '英语',
        '数据点': '~1090'
    },
    'Stage 3': {
        '国家/地区': 34,
        '测试模型': 10,
        '语言数': 10,
        '配对数据': 669
    }
}

# 绘制四个阶段的柱状图
x_pos = np.arange(len(stages))
bar_width = 0.6

# 为每个阶段创建一个矩形框
for i, (stage, color) in enumerate(zip(stages, colors)):
    # 绘制主要矩形
    rect = mpatches.FancyBboxPatch(
        (i - bar_width/2, 0), bar_width, 5,
        boxstyle="round,pad=0.1",
        facecolor=color,
        edgecolor='black',
        linewidth=2,
        alpha=0.7
    )
    ax.add_patch(rect)
    
    # 添加阶段标题
    ax.text(i, 4.5, stage.split('\n')[0], 
            ha='center', va='center', fontsize=14, fontweight='bold', color='white')
    ax.text(i, 3.8, stage.split('\n')[1], 
            ha='center', va='center', fontsize=11, color='white')
    
    # 添加关键指标
    stage_key = stage.split('\n')[0]
    data = stage_data[stage_key]
    y_pos = 2.8
    for key, value in data.items():
        ax.text(i, y_pos, f'{key}: {value}',
                ha='center', va='center', fontsize=9, color='white')
        y_pos -= 0.5

# 添加箭头连接各阶段
arrow_props = dict(arrowstyle='->', lw=3, color='#34495e')
for i in range(len(stages) - 1):
    ax.annotate('', xy=(i + 1 - bar_width/2, 2.5), xytext=(i + bar_width/2, 2.5),
                arrowprops=arrow_props)

# 设置图表属性
ax.set_xlim(-0.8, len(stages) - 0.2)
ax.set_ylim(0, 5.5)
ax.axis('off')

# 添加标题
plt.title('四阶段递进式研究设计：当前研究规模', 
          fontsize=18, fontweight='bold', pad=20)

# 添加底部说明
info_text = '当前进展：Stage 0-1 已完成 | Stage 2 已完成主体 | Stage 3 进行中（已完成34国家/地区）\n后续扩展：Stage 2 扩展至更多国家 | Stage 3 扩展至50+国家/地区、15+语言'
plt.figtext(0.5, 0.02, info_text, ha='center', fontsize=10, 
            style='italic', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

plt.tight_layout()

# 保存图表
output_path = 'e:/Code/value of LLM/LLM\'s values/results/analysis/visualization/research_scale_chart.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
print(f"研究规模图表已保存至: {output_path}")

plt.show()
