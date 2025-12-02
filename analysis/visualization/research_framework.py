"""
研究框架图 - 学术严谨风格
展示整体研究框架，包括研究方法、技术路线、理论基础的有机整合
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Wedge, Arc, Rectangle
from matplotlib.path import Path
import matplotlib.patches as patches
import numpy as np
import os

# 设置中文字体和学术风格
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 9
plt.rcParams['font.family'] = 'sans-serif'

# 创建输出目录
output_dir = 'results/analysis/visualization'
os.makedirs(output_dir, exist_ok=True)


def draw_research_framework():
    """绘制研究框架整体图"""
    fig, ax = plt.subplots(figsize=(20, 14))
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 14)
    ax.axis('off')
    
    # ==================== 标题 ====================
    ax.text(10, 13.7, '大模型价值观评价研究框架', ha='center', va='center',
            fontsize=18, fontweight='bold')
    
    # ==================== 中心：研究核心 ====================
    # 中心圆
    center_x, center_y = 10, 7
    circle_outer = Circle((center_x, center_y), 1.5, facecolor='#1565C0', 
                          edgecolor='#0D47A1', linewidth=3, alpha=0.15)
    ax.add_patch(circle_outer)
    circle_inner = Circle((center_x, center_y), 1.2, facecolor='#1976D2', 
                          edgecolor='#0D47A1', linewidth=2, alpha=0.25)
    ax.add_patch(circle_inner)
    
    ax.text(center_x, center_y + 0.4, '大模型价值观', ha='center', va='center',
            fontsize=13, fontweight='bold', color='#0D47A1')
    ax.text(center_x, center_y, '跨文化评估', ha='center', va='center',
            fontsize=11, fontweight='bold', color='#1565C0')
    ax.text(center_x, center_y - 0.4, '与偏差分析', ha='center', va='center',
            fontsize=11, fontweight='bold', color='#1565C0')
    
    # ==================== 左侧：理论基础与数据来源 ====================
    # 理论基础框
    theory_box = FancyBboxPatch((0.3, 10), 4.5, 2.5, boxstyle="round,pad=0.15",
                                edgecolor='#6A1B9A', facecolor='#F3E5F5', 
                                linewidth=2.5, alpha=0.9)
    ax.add_patch(theory_box)
    ax.text(2.55, 12.2, '理论基础', ha='center', va='center',
            fontsize=12, fontweight='bold', color='#4A148C')
    
    theories = [
        'Inglehart-Welzel文化地图',
        'WVS价值观理论框架',
        '他者叙事理论',
        '跨文化比较方法论'
    ]
    for i, theory in enumerate(theories):
        ax.text(2.55, 11.5 - i*0.45, f'• {theory}', ha='center', va='center',
                fontsize=9, color='#4A148C')
    
    # 数据来源框
    data_box = FancyBboxPatch((0.3, 6), 4.5, 3.2, boxstyle="round,pad=0.15",
                              edgecolor='#0277BD', facecolor='#E1F5FE', 
                              linewidth=2.5, alpha=0.9)
    ax.add_patch(data_box)
    ax.text(2.55, 8.9, '数据来源', ha='center', va='center',
            fontsize=12, fontweight='bold', color='#01579B')
    
    # WVS数据
    wvs_rect = Rectangle((0.8, 7.8), 3.5, 0.8, facecolor='#B3E5FC', 
                         edgecolor='#0277BD', linewidth=1.5)
    ax.add_patch(wvs_rect)
    ax.text(2.55, 8.4, 'WVS数据集', ha='center', fontsize=10, fontweight='bold')
    ax.text(2.55, 8, '109个国家/地区 × 10个核心题目', ha='center', fontsize=8)
    
    # 模型数据
    model_rect = Rectangle((0.8, 6.5), 3.5, 1, facecolor='#C8E6C9', 
                           edgecolor='#388E3C', linewidth=1.5)
    ax.add_patch(model_rect)
    ax.text(2.55, 7.3, '大语言模型', ha='center', fontsize=10, fontweight='bold')
    ax.text(2.55, 6.95, '多个主流模型（当前10个）', ha='center', fontsize=8)
    ax.text(2.55, 6.65, '计划扩展至15-20个', ha='center', fontsize=7.5, style='italic')
    
    # 连接到中心的箭头 - 从理论基础框右侧到中心圆左侧
    arrow_theory = FancyArrowPatch((4.8, 11.25), (8.55, 7.75),
                                   arrowstyle='->', mutation_scale=20, 
                                   linewidth=2, color='#6A1B9A', 
                                   connectionstyle="arc3,rad=0.3")
    ax.add_patch(arrow_theory)
    ax.text(6.5, 9.8, '理论指导', ha='center', fontsize=9, 
            color='#6A1B9A', style='italic', rotation=-25)
    
    # 从数据来源框右侧到中心圆左侧
    arrow_data = FancyArrowPatch((4.8, 7.5), (8.55, 7.15),
                                arrowstyle='->', mutation_scale=20, 
                                linewidth=2, color='#0277BD')
    ax.add_patch(arrow_data)
    ax.text(6.5, 7.8, '数据输入', ha='center', fontsize=9, 
            color='#0277BD', style='italic')
    
    # ==================== 右侧：研究方法体系 ====================
    # 大框：y从9.5开始，高度3.5，所以范围是9.5到13.0
    method_box = FancyBboxPatch((15.2, 9.5), 4.5, 3.5, boxstyle="round,pad=0.15",
                                edgecolor='#D84315', facecolor='#FBE9E7', 
                                linewidth=2.5, alpha=0.9)
    ax.add_patch(method_box)
    ax.text(17.45, 12.7, '研究方法体系', ha='center', va='center',
            fontsize=12, fontweight='bold', color='#BF360C')
    
    methods = [
        ('问卷调查法', 'WVS标准化问卷\n多语言版本'),
        ('实验法', '三阶段对照实验\nStage0/1/2/3'),
        ('比较分析法', '横向/纵向/参照\n多维度对比'),
        ('统计分析法', 'PPCA降维分析\n距离与优势计算')
    ]
    
    # 小框高度0.5，4个小框总高度2.0，间距3个×0.75=2.25，总共4.25
    # 大框内容区域：9.5+0.2(padding)到12.7-0.2=12.5，高度约3.0
    # 起始位置：12.5 - 0.3(顶部留白) = 12.2
    box_height = 0.5
    spacing = 0.75
    start_y = 12.0
    
    for i, (method, desc) in enumerate(methods):
        y_pos = start_y - i * spacing
        # 方法标签 - 确保在大框内（9.7到12.5之间）
        method_label = Rectangle((15.6, y_pos - box_height/2), 1.5, box_height, 
                                facecolor='#FFCCBC', edgecolor='#D84315', linewidth=1.5)
        ax.add_patch(method_label)
        ax.text(16.35, y_pos, method, ha='center', va='center',
                fontsize=9, fontweight='bold', color='#BF360C')
        
        # 描述文字
        ax.text(18.0, y_pos, desc, ha='left', va='center',
                fontsize=7.5, color='#5D4037')
    
    # 从研究方法体系框左侧到中心圆右侧
    arrow_method = FancyArrowPatch((15.2, 10.8), (11.45, 7.75),
                                  arrowstyle='->', mutation_scale=20, 
                                  linewidth=2, color='#D84315',
                                  connectionstyle="arc3,rad=-0.3")
    ax.add_patch(arrow_method)
    ax.text(13.5, 9.5, '方法支撑', ha='center', fontsize=9, 
            color='#D84315', style='italic', rotation=25)
    
    # ==================== 底部：技术路线（时间轴形式）====================
    # 背景框
    timeline_box = FancyBboxPatch((0.3, 0.3), 14.4, 4.5, boxstyle="round,pad=0.15",
                                  edgecolor='#455A64', facecolor='#ECEFF1', 
                                  linewidth=2.5, alpha=0.9)
    ax.add_patch(timeline_box)
    ax.text(7.5, 4.5, '技术路线与实施阶段', ha='center', va='center',
            fontsize=12, fontweight='bold', color='#263238')
    
    # 时间轴主线
    ax.plot([1.5, 13.5], [3.5, 3.5], 'k-', linewidth=3, color='#546E7A')
    
    # 四个阶段
    stages = [
        {
            'name': 'Stage0',
            'title': '基准构建',
            'x': 2.5,
            'color': '#7986CB',
            'content': ['PPCA预处理', '构建文化坐标系', '确定真实位置'],
            'icon': '◆'
        },
        {
            'name': 'Stage1',
            'title': '基线测量',
            'x': 5.5,
            'color': '#4DB6AC',
            'content': ['模型直接回答', '测量价值观原点', '建立参照基线'],
            'icon': '●'
        },
        {
            'name': 'Stage2',
            'title': '全球文化模仿',
            'x': 8.5,
            'color': '#FFB74D',
            'content': ['109国家/地区', '英语环境测试', '识别系统性偏差'],
            'icon': '■'
        },
        {
            'name': 'Stage3',
            'title': '跨语言对照',
            'x': 11.5,
            'color': '#E57373',
            'content': ['多国家/地区', '英语+母语对比', '量化语言效应'],
            'icon': '▲'
        }
    ]
    
    for stage in stages:
        # 时间轴节点
        circle = Circle((stage['x'], 3.5), 0.25, facecolor=stage['color'], 
                       edgecolor='#263238', linewidth=2.5, zorder=10)
        ax.add_patch(circle)
        ax.text(stage['x'], 3.5, stage['icon'], ha='center', va='center',
                fontsize=12, color='white', fontweight='bold', zorder=11)
        
        # 阶段框
        stage_box = FancyBboxPatch((stage['x'] - 1.2, 1), 2.4, 2,
                                   boxstyle="round,pad=0.1",
                                   edgecolor=stage['color'], 
                                   facecolor='white',
                                   linewidth=2, alpha=0.95)
        ax.add_patch(stage_box)
        
        # 阶段名称
        ax.text(stage['x'], 2.7, stage['name'], ha='center', va='center',
                fontsize=10, fontweight='bold', color=stage['color'])
        ax.text(stage['x'], 2.4, stage['title'], ha='center', va='center',
                fontsize=9, fontweight='bold', color='#263238')
        
        # 内容
        for i, content in enumerate(stage['content']):
            ax.text(stage['x'], 2 - i*0.3, content, ha='center', va='center',
                    fontsize=7.5, color='#455A64')
        
        # 连接线到时间轴
        ax.plot([stage['x'], stage['x']], [3, 3.25], 'k-', 
                linewidth=2, color=stage['color'])
    
    # 从中心圆下方到技术路线框上边界
    arrow_to_timeline = FancyArrowPatch((10, 5.55), (10, 4.85),
                                       arrowstyle='->', mutation_scale=20, 
                                       linewidth=2, color='#546E7A')
    ax.add_patch(arrow_to_timeline)
    ax.text(10.5, 5.2, '实施路径', ha='left', fontsize=9, 
            color='#546E7A', style='italic')
    
    # ==================== 右下：研究输出 ====================
    output_box = FancyBboxPatch((15.2, 0.3), 4.5, 4.2, boxstyle="round,pad=0.15",
                                edgecolor='#C2185B', facecolor='#FCE4EC', 
                                linewidth=2.5, alpha=0.9)
    ax.add_patch(output_box)
    ax.text(17.45, 4.2, '研究输出', ha='center', va='center',
            fontsize=12, fontweight='bold', color='#880E4F')
    
    outputs = [
        '全球文化偏差地图',
        '语言效应梯度分析',
        '模型价值观基线分布',
        '东亚殖民地-本土梯度',
        '定量结论与理论解释'
    ]
    
    for i, output in enumerate(outputs):
        y_pos = 3.6 - i * 0.6
        ax.text(15.6, y_pos, f'▸', ha='left', va='center',
                fontsize=12, color='#C2185B', fontweight='bold')
        ax.text(16, y_pos, output, ha='left', va='center',
                fontsize=8.5, color='#880E4F')
    
    # 从技术路线框右边界到研究输出框左边界
    arrow_to_output = FancyArrowPatch((14.75, 2.5), (15.2, 2.5),
                                     arrowstyle='->', mutation_scale=20, 
                                     linewidth=2, color='#C2185B')
    ax.add_patch(arrow_to_output)
    
    # ==================== 顶部：研究目标 ====================
    goal_box = FancyBboxPatch((6, 12.5), 8, 0.8, boxstyle="round,pad=0.1",
                              edgecolor='#F57C00', facecolor='#FFF3E0', 
                              linewidth=2, alpha=0.95)
    ax.add_patch(goal_box)
    ax.text(10, 12.9, '研究目标：系统评估大语言模型的文化价值观表征能力与偏差模式', 
            ha='center', va='center', fontsize=10, fontweight='bold', color='#E65100')
    
    # 从研究目标框下边界到中心圆上方
    arrow_goal = FancyArrowPatch((10, 12.5), (10, 8.45),
                                arrowstyle='->', mutation_scale=20, 
                                linewidth=2, color='#F57C00', linestyle='--')
    ax.add_patch(arrow_goal)
    
    # ==================== 添加图例 ====================
    legend_elements = [
        mpatches.Patch(facecolor='#F3E5F5', edgecolor='#6A1B9A', label='理论基础'),
        mpatches.Patch(facecolor='#E1F5FE', edgecolor='#0277BD', label='数据来源'),
        mpatches.Patch(facecolor='#FBE9E7', edgecolor='#D84315', label='研究方法'),
        mpatches.Patch(facecolor='#ECEFF1', edgecolor='#455A64', label='技术路线'),
        mpatches.Patch(facecolor='#FCE4EC', edgecolor='#C2185B', label='研究输出')
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=9, 
             framealpha=0.95, edgecolor='#666', fancybox=True)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/fig1_research_framework.png', dpi=300, bbox_inches='tight')
    print(f'✓ 研究框架图已保存: {output_dir}/fig1_research_framework.png')
    plt.close()


if __name__ == '__main__':
    print('开始生成研究框架图...\n')
    draw_research_framework()
    print('\n✓ 图表生成完成！')
