"""
图2：数据处理与计算方法流程图 - 重新设计版本
采用清晰的左右布局，避免箭头穿过不相关的框
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle, Polygon
import numpy as np
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 9
plt.rcParams['font.family'] = 'sans-serif'

# 创建输出目录
output_dir = 'results/analysis/visualization'
os.makedirs(output_dir, exist_ok=True)


def draw_data_processing_flow():
    """图2：数据处理与计算方法流程图 - 清晰的左中右布局"""
    fig, ax = plt.subplots(figsize=(20, 12))
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # 标题
    ax.text(10, 11.5, '数据处理与计算方法流程', ha='center', va='center',
            fontsize=16, fontweight='bold')
    
    # ==================== 左侧：数据输入 ====================
    # WVS数据
    wvs_box = FancyBboxPatch((0.5, 8.5), 3.5, 1.5, boxstyle="round,pad=0.15",
                             edgecolor='#0277BD', facecolor='#B3E5FC', linewidth=2.5)
    ax.add_patch(wvs_box)
    ax.text(2.25, 9.6, 'WVS数据集', ha='center', fontsize=10, fontweight='bold')
    ax.text(2.25, 9.2, '109个国家/地区', ha='center', fontsize=8)
    ax.text(2.25, 8.8, '10个核心题目', ha='center', fontsize=8, style='italic')
    
    # 模型数据
    model_box = FancyBboxPatch((0.5, 6.5), 3.5, 1.5, boxstyle="round,pad=0.15",
                               edgecolor='#388E3C', facecolor='#C8E6C9', linewidth=2.5)
    ax.add_patch(model_box)
    ax.text(2.25, 7.6, '模型测试数据', ha='center', fontsize=10, fontweight='bold')
    ax.text(2.25, 7.2, 'Stage1/2/3', ha='center', fontsize=8)
    ax.text(2.25, 6.8, '多模型×多场景', ha='center', fontsize=8, style='italic')
    
    # 汇聚箭头到中间 - 箭头头部刚好停在框边界外
    # 第一个框左边界在x=5.5，箭头头部长度约0.2，所以终点设为5.3
    arrow1 = FancyArrowPatch((4, 9.25), (5.3, 8.2), arrowstyle='->', 
                            mutation_scale=15, linewidth=1.8, color='#546E7A', zorder=10)
    ax.add_patch(arrow1)
    arrow2 = FancyArrowPatch((4, 7.25), (5.3, 7.8), arrowstyle='->', 
                            mutation_scale=15, linewidth=1.8, color='#546E7A', zorder=10)
    ax.add_patch(arrow2)
    
    # ==================== 中间：处理流程（垂直排列）====================
    process_x = 5.5
    
    # 1. 数据合并
    box1 = FancyBboxPatch((process_x, 7.5), 4, 1, boxstyle="round,pad=0.1",
                          edgecolor='#F57C00', facecolor='#FFE0B2', linewidth=2)
    ax.add_patch(box1)
    ax.text(process_x + 2, 8.2, '① 数据合并与对齐', ha='center', fontsize=9, fontweight='bold')
    ax.text(process_x + 2, 7.8, '整合WVS与模型数据', ha='center', fontsize=7.5, style='italic')
    
    arrow_down1 = FancyArrowPatch((process_x + 2, 7.5), (process_x + 2, 7.1),
                                 arrowstyle='->', mutation_scale=14, linewidth=1.8, color='#546E7A')
    ax.add_patch(arrow_down1)
    
    # 2. PPCA填补
    box2 = FancyBboxPatch((process_x, 6.1), 4, 1, boxstyle="round,pad=0.1",
                          edgecolor='#F9A825', facecolor='#FFF9C4', linewidth=2)
    ax.add_patch(box2)
    ax.text(process_x + 2, 6.8, '② PPCA填补缺失值', ha='center', fontsize=9, fontweight='bold')
    ax.text(process_x + 2, 6.4, '处理数据完整性', ha='center', fontsize=7.5, style='italic')
    
    arrow_down2 = FancyArrowPatch((process_x + 2, 6.1), (process_x + 2, 5.7),
                                 arrowstyle='->', mutation_scale=14, linewidth=1.8, color='#546E7A')
    ax.add_patch(arrow_down2)
    
    # 3. 标准化
    box3 = FancyBboxPatch((process_x, 4.7), 4, 1, boxstyle="round,pad=0.1",
                          edgecolor='#6A1B9A', facecolor='#E1BEE7', linewidth=2)
    ax.add_patch(box3)
    ax.text(process_x + 2, 5.4, '③ 标准化处理', ha='center', fontsize=9, fontweight='bold')
    ax.text(process_x + 2, 5.0, 'μ=0, σ=1', ha='center', fontsize=7.5, style='italic')
    
    arrow_down3 = FancyArrowPatch((process_x + 2, 4.7), (process_x + 2, 4.3),
                                 arrowstyle='->', mutation_scale=14, linewidth=1.8, color='#546E7A')
    ax.add_patch(arrow_down3)
    
    # 4. PPCA降维
    box4 = FancyBboxPatch((process_x, 3.3), 4, 1, boxstyle="round,pad=0.1",
                          edgecolor='#6A1B9A', facecolor='#F3E5F5', linewidth=2)
    ax.add_patch(box4)
    ax.text(process_x + 2, 4.0, '④ PPCA降维（自实现）', ha='center', fontsize=9, fontweight='bold')
    ax.text(process_x + 2, 3.6, 'n维 → 2维 (PC1, PC2)', ha='center', fontsize=7.5, style='italic')
    
    # 右侧说明
    ax.text(10.2, 4.0, 'PC1: 生存-自我表达', ha='left', fontsize=7.5, color='#666')
    ax.text(10.2, 3.6, 'PC2: 传统-现代', ha='left', fontsize=7.5, color='#666')
    
    arrow_down4 = FancyArrowPatch((process_x + 2, 3.3), (process_x + 2, 2.9),
                                 arrowstyle='->', mutation_scale=14, linewidth=1.8, color='#546E7A')
    ax.add_patch(arrow_down4)
    
    # 5. Varimax旋转
    box5 = FancyBboxPatch((process_x, 1.9), 4, 1, boxstyle="round,pad=0.1",
                          edgecolor='#6A1B9A', facecolor='#E1BEE7', linewidth=2)
    ax.add_patch(box5)
    ax.text(process_x + 2, 2.6, '⑤ Varimax旋转', ha='center', fontsize=9, fontweight='bold')
    ax.text(process_x + 2, 2.2, '增强可解释性', ha='center', fontsize=7.5, style='italic')
    
    # 右侧说明
    ax.text(10.2, 2.4, '对齐理论维度', ha='left', fontsize=7.5, color='#666')
    
    arrow_down5 = FancyArrowPatch((process_x + 2, 1.9), (process_x + 2, 1.5),
                                 arrowstyle='->', mutation_scale=14, linewidth=1.8, color='#546E7A')
    ax.add_patch(arrow_down5)
    
    # 6. 坐标投影
    box6 = FancyBboxPatch((process_x, 0.5), 4, 1, boxstyle="round,pad=0.1",
                          edgecolor='#1976D2', facecolor='#E3F2FD', linewidth=2)
    ax.add_patch(box6)
    ax.text(process_x + 2, 1.2, '⑥ 坐标投影', ha='center', fontsize=9, fontweight='bold')
    ax.text(process_x + 2, 0.8, '映射到2D文化空间', ha='center', fontsize=7.5, style='italic')
    
    # ==================== 右上：文化坐标空间可视化 ====================
    coord_box = FancyBboxPatch((12, 7), 7, 4, boxstyle="round,pad=0.15",
                               edgecolor='#1976D2', facecolor='#E3F2FD', linewidth=2.5)
    ax.add_patch(coord_box)
    ax.text(15.5, 10.7, '文化坐标空间', ha='center', fontsize=11, fontweight='bold', color='#0D47A1')
    
    # 绘制坐标轴
    ax.plot([13, 18], [8.5, 8.5], 'k-', linewidth=1.5, color='#666')
    ax.plot([15.5, 15.5], [7.3, 9.7], 'k-', linewidth=1.5, color='#666')
    ax.text(18.2, 8.5, 'PC1', ha='left', fontsize=8, color='#666', fontweight='bold')
    ax.text(15.5, 10, 'PC2', ha='center', fontsize=8, color='#666', fontweight='bold')
    
    # 示意点
    np.random.seed(42)
    points_x = np.random.normal(15.5, 0.8, 20)
    points_y = np.random.normal(8.5, 0.8, 20)
    ax.scatter(points_x, points_y, s=40, c='#1976D2', alpha=0.6, edgecolors='#0D47A1', linewidths=1.5)
    
    ax.text(15.5, 7.5, '投影后的文化坐标', ha='center', fontsize=8, style='italic', color='#666')
    
    # 从处理流程到坐标空间的箭头（不穿过其他框）
    # 坐标空间框左边界在x=12，箭头头部长度约0.2，所以终点设为11.8
    arrow_to_coord = FancyArrowPatch((9.5, 1), (11.8, 8.5),
                                    arrowstyle='->', mutation_scale=15, 
                                    linewidth=1.8, color='#1976D2',
                                    connectionstyle="arc3,rad=0.25", zorder=10)
    ax.add_patch(arrow_to_coord)
    
    # ==================== 右下：分析计算 ====================
    # 文化距离计算
    dist_box = FancyBboxPatch((12, 4.5), 3.5, 2, boxstyle="round,pad=0.15",
                              edgecolor='#C62828', facecolor='#FFCDD2', linewidth=2.5)
    ax.add_patch(dist_box)
    ax.text(13.75, 6.2, '文化距离计算', ha='center', fontsize=10, fontweight='bold', color='#B71C1C')
    ax.text(13.75, 5.8, '欧氏距离公式：', ha='center', fontsize=8)
    ax.text(13.75, 5.4, 'd = √[(x₁-x₂)²+(y₁-y₂)²]', ha='center', fontsize=7.5, 
           family='monospace', color='#C62828')
    ax.text(13.75, 4.9, '量化模型与真实位置差异', ha='center', fontsize=7, style='italic', color='#666')
    
    # 英语优势计算
    adv_box = FancyBboxPatch((15.8, 4.5), 3.5, 2, boxstyle="round,pad=0.15",
                             edgecolor='#C62828', facecolor='#FFCDD2', linewidth=2.5)
    ax.add_patch(adv_box)
    ax.text(17.55, 6.2, '英语优势计算', ha='center', fontsize=10, fontweight='bold', color='#B71C1C')
    ax.text(17.55, 5.8, '配对比较方法：', ha='center', fontsize=8)
    ax.text(17.55, 5.4, 'Adv = (d_n - d_e) / d_n', ha='center', fontsize=7.5, 
           family='monospace', color='#C62828')
    ax.text(17.55, 4.9, '控制模型能力差异', ha='center', fontsize=7, style='italic', color='#666')
    
    # 从坐标空间底部到分析框顶部的箭头 - 对称设计
    # 分析框顶部在y=6.5，箭头头部长度约0.15，所以终点设为6.65
    # 左侧箭头垂直向下
    arrow_to_dist = FancyArrowPatch((13.75, 7), (13.75, 6.65),
                                   arrowstyle='->', mutation_scale=14, 
                                   linewidth=1.8, color='#C62828', zorder=10)
    ax.add_patch(arrow_to_dist)
    # 右侧箭头也垂直向下，保持对称
    arrow_to_adv = FancyArrowPatch((17.55, 7), (17.55, 6.65),
                                  arrowstyle='->', mutation_scale=14, 
                                  linewidth=1.8, color='#C62828', zorder=10)
    ax.add_patch(arrow_to_adv)
    
    # ==================== 底部：输出 ====================
    # 汇聚箭头，输出框顶部在y=2.8，箭头头部长度约0.15，所以终点设为2.95
    arrow_out1 = FancyArrowPatch((13.75, 4.5), (14.5, 2.95),
                                arrowstyle='->', mutation_scale=14, 
                                linewidth=1.8, color='#E91E63', zorder=10)
    ax.add_patch(arrow_out1)
    arrow_out2 = FancyArrowPatch((17.55, 4.5), (16.5, 2.95),
                                arrowstyle='->', mutation_scale=14, 
                                linewidth=1.8, color='#E91E63', zorder=10)
    ax.add_patch(arrow_out2)
    
    output_box = FancyBboxPatch((12, 0.5), 7, 2.3, boxstyle="round,pad=0.15",
                                edgecolor='#E91E63', facecolor='#FCE4EC', linewidth=2.5)
    ax.add_patch(output_box)
    ax.text(15.5, 2.5, '可视化与统计分析', ha='center', fontsize=11, fontweight='bold', color='#880E4F')
    ax.text(15.5, 2.0, '生成文化地图、梯度图、分布图等研究成果', ha='center', fontsize=8.5, color='#C2185B')
    ax.text(15.5, 1.5, '定量结论与理论解释', ha='center', fontsize=8.5, color='#C2185B')
    ax.text(15.5, 0.9, '支撑研究发现与学术贡献', ha='center', fontsize=7.5, style='italic', color='#666')
    
    # ==================== 添加图例 ====================
    legend_elements = [
        mpatches.Patch(facecolor='#B3E5FC', edgecolor='#0277BD', label='数据输入'),
        mpatches.Patch(facecolor='#FFE0B2', edgecolor='#F57C00', label='预处理'),
        mpatches.Patch(facecolor='#E1BEE7', edgecolor='#6A1B9A', label='降维分析'),
        mpatches.Patch(facecolor='#E3F2FD', edgecolor='#1976D2', label='坐标投影'),
        mpatches.Patch(facecolor='#FFCDD2', edgecolor='#C62828', label='计算分析'),
        mpatches.Patch(facecolor='#FCE4EC', edgecolor='#E91E63', label='输出结果')
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=9, 
             framealpha=0.95, edgecolor='#666', ncol=3)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/fig2_data_processing_flow.png', dpi=300, bbox_inches='tight')
    print(f'✓ 图2已保存: {output_dir}/fig2_data_processing_flow.png')
    plt.close()


if __name__ == '__main__':
    print('开始生成图2...\n')
    draw_data_processing_flow()
    print('\n✓ 图表生成完成！')
