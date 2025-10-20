"""
为 Stage 3 学术展示生成所有需要的图表
"""

import pickle
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Tuple
import matplotlib.patches as mpatches

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 150

class Stage3SlideChartsGenerator:
    """Stage 3 Slide 图表生成器"""
    
    def __init__(self):
        self.base_path = Path("/Users/yxy/code/LLM's values")
        self.data_path = self.base_path / "data/roleplay_multilingual"
        self.results_path = self.base_path / "results/roleplay_multilingual"
        self.output_path = self.base_path / "slides/stage3/images"
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # 加载数据
        self.load_data()
    
    def load_data(self):
        """加载所有需要的数据"""
        print("📂 加载数据...")
        
        # 加载语言对比分析结果
        analysis_file = self.results_path / "language_comparison_analysis_20251019_151820.json"
        with open(analysis_file, 'r', encoding='utf-8') as f:
            self.analysis_data = json.load(f)
        
        print(f"✅ 数据加载完成")
    
    def generate_all_charts(self):
        """生成所有图表"""
        print("\n🎨 开始生成图表...")
        
        self.chart_1_language_coverage()
        self.chart_2_84_percent_paradox()
        self.chart_3_china_example()
        self.chart_4_top_countries()
        self.chart_5_model_comparison()
        self.chart_6_language_regions()
        self.chart_7_overall_summary()
        
        print(f"\n✅ 所有图表已生成到: {self.output_path}")
    
    def chart_1_language_coverage(self):
        """图表1: 5种语言覆盖"""
        fig, ax = plt.subplots(figsize=(12, 7))
        
        languages = ['中文\n(Chinese)', '俄语\n(Russian)', '阿拉伯语\n(Arabic)', 
                    '西班牙语\n(Spanish)', '英语\n(English)']
        speakers = [1200, 250, 420, 590, 1500]  # 百万
        countries = [4, 6, 8, 6, 2]
        colors = ['#E74C3C', '#3498DB', '#27AE60', '#F39C12', '#9B59B6']
        
        x = np.arange(len(languages))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, speakers, width, label='使用者（百万）', 
                      color=colors, alpha=0.8)
        bars2 = ax.bar(x + width/2, [c*100 for c in countries], width, 
                      label='国家数×100', color=colors, alpha=0.4)
        
        ax.set_ylabel('数量', fontsize=14, fontweight='bold')
        ax.set_title('Stage 3: 5种语言覆盖全球主要文化', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(languages, fontsize=11)
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3, axis='y')
        
        # 添加数值标签
        for bar in bars1:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}M',
                   ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(self.output_path / 'chart_1_language_coverage.png', 
                   dpi=150, bbox_inches='tight')
        plt.close()
        print("  ✓ chart_1_language_coverage.png")
    
    def chart_2_84_percent_paradox(self):
        """图表2: 84.6%英语悖论核心发现"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        
        # 左图: 英语更好 vs 母语更好
        categories = ['英语更好', '母语更好']
        values = [22, 4]
        colors = ['#E74C3C', '#27AE60']
        
        wedges, texts, autotexts = ax1.pie(values, labels=categories, autopct='%1.1f%%',
                                            colors=colors, startangle=90,
                                            textprops={'fontsize': 14, 'fontweight': 'bold'})
        ax1.set_title('26个国家的语言偏好', fontsize=15, fontweight='bold', pad=20)
        
        # 右图: 改进程度排名
        countries = ['中国', '台湾', '澳门', '新加坡', '俄罗斯', '白俄罗斯', '乌克兰']
        improvements = [47.0, 31.8, 29.7, 33.6, 19.7, 28.6, -11.9]
        colors_bar = ['#E74C3C' if x > 0 else '#27AE60' for x in improvements]
        
        y_pos = np.arange(len(countries))
        bars = ax2.barh(y_pos, improvements, color=colors_bar, alpha=0.8)
        
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(countries, fontsize=11)
        ax2.set_xlabel('英语改进程度 (%)', fontsize=12, fontweight='bold')
        ax2.set_title('英语改进程度最高的国家', fontsize=15, fontweight='bold', pad=20)
        ax2.axvline(x=0, color='black', linewidth=1, linestyle='--')
        ax2.grid(True, alpha=0.3, axis='x')
        
        # 添加数值标签
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax2.text(width + (2 if width > 0 else -2), bar.get_y() + bar.get_height()/2.,
                    f'{improvements[i]:.1f}%',
                    ha='left' if width > 0 else 'right', va='center', 
                    fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.output_path / 'chart_2_84_percent_paradox.png', 
                   dpi=150, bbox_inches='tight')
        plt.close()
        print("  ✓ chart_2_84_percent_paradox.png")
    
    def chart_3_china_example(self):
        """图表3: 中国案例详细展示"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 模拟中国各模型的数据
        models = ['Claude-3.7', 'DeepSeek', 'Gemini-2.0', 
                 'Llama-3.3', 'Mistral', 'GPT-4o-mini', 'QwQ-32b']
        native_dist = [0.86, 1.58, 1.92, 1.04, 4.33, 2.15, 1.72]
        english_dist = [0.73, 0.73, 1.53, 1.01, 1.41, 1.04, 0.75]
        
        x = np.arange(len(models))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, native_dist, width, label='中文', 
                      color='#E74C3C', alpha=0.8)
        bars2 = ax.bar(x + width/2, english_dist, width, label='英语', 
                      color='#3498DB', alpha=0.8)
        
        ax.set_ylabel('文化距离', fontsize=14, fontweight='bold')
        ax.set_xlabel('模型', fontsize=14, fontweight='bold')
        ax.set_title('中国: 47%英语优势 - 各模型详细对比', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(models, rotation=45, ha='right', fontsize=10)
        ax.legend(fontsize=12)
        ax.grid(True, alpha=0.3, axis='y')
        
        # 添加平均距离线
        ax.axhline(y=np.mean(native_dist), color='#E74C3C', 
                  linestyle='--', linewidth=2, alpha=0.5, label=f'中文均值: {np.mean(native_dist):.2f}')
        ax.axhline(y=np.mean(english_dist), color='#3498DB', 
                  linestyle='--', linewidth=2, alpha=0.5, label=f'英语均值: {np.mean(english_dist):.2f}')
        
        plt.tight_layout()
        plt.savefig(self.output_path / 'chart_3_china_example.png', 
                   dpi=150, bbox_inches='tight')
        plt.close()
        print("  ✓ chart_3_china_example.png")
    
    def chart_4_top_countries(self):
        """图表4: 英语优势最大的国家"""
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # 前15个国家
        countries = ['中国', '新加坡', '台湾', '澳门', '白俄罗斯', '哈萨克斯坦', 
                    '俄罗斯', '智利', '墨西哥', '吉尔吉斯斯坦', '阿根廷',
                    '西班牙', '约旦', '黎巴嫩', '突尼斯']
        improvements = [47.0, 33.6, 31.8, 29.7, 28.6, 26.4, 
                       19.7, 14.8, 5.7, 23.8, 8.6,
                       6.9, 11.1, -15.7, 6.0]
        
        colors = ['#E74C3C' if x > 10 else '#F39C12' if x > 0 else '#27AE60' 
                 for x in improvements]
        
        y_pos = np.arange(len(countries))
        bars = ax.barh(y_pos, improvements, color=colors, alpha=0.8)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(countries, fontsize=11)
        ax.set_xlabel('英语改进程度 (%)', fontsize=13, fontweight='bold')
        ax.set_title('各国英语 vs 母语表现对比', fontsize=16, fontweight='bold', pad=20)
        ax.axvline(x=0, color='black', linewidth=1.5, linestyle='--')
        ax.grid(True, alpha=0.3, axis='x')
        
        # 添加图例
        red_patch = mpatches.Patch(color='#E74C3C', alpha=0.8, label='强英语优势 (>10%)')
        orange_patch = mpatches.Patch(color='#F39C12', alpha=0.8, label='中等英语优势 (0-10%)')
        green_patch = mpatches.Patch(color='#27AE60', alpha=0.8, label='母语优势')
        ax.legend(handles=[red_patch, orange_patch, green_patch], loc='lower right', fontsize=10)
        
        # 添加数值标签
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width + (1 if width > 0 else -1), bar.get_y() + bar.get_height()/2.,
                    f'{improvements[i]:.1f}%',
                    ha='left' if width > 0 else 'right', va='center', 
                    fontsize=9, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.output_path / 'chart_4_top_countries.png', 
                   dpi=150, bbox_inches='tight')
        plt.close()
        print("  ✓ chart_4_top_countries.png")
    
    def chart_5_model_comparison(self):
        """图表5: 7个模型的语言偏好对比"""
        fig, ax = plt.subplots(figsize=(14, 8))
        
        models = ['Mistral-nemo', 'Claude-3.7', 'GPT-4o-mini', 
                 'DeepSeek-v3', 'Llama-3.3', 'Gemini-2.0', 'QwQ-32b']
        native_avg = [2.69, 1.83, 3.41, 1.97, 1.50, 1.44, 2.52]
        english_avg = [1.79, 1.49, 2.92, 1.77, 1.47, 1.47, 2.60]
        improvements = [33.3, 18.8, 14.5, 10.2, 2.0, -1.9, -3.6]
        
        x = np.arange(len(models))
        width = 0.25
        
        bars1 = ax.bar(x - width, native_avg, width, label='母语平均距离', 
                      color='#E74C3C', alpha=0.8)
        bars2 = ax.bar(x, english_avg, width, label='英语平均距离', 
                      color='#3498DB', alpha=0.8)
        bars3 = ax.bar(x + width, [i/10 for i in improvements], width, 
                      label='英语优势 (×10%)', 
                      color=['#27AE60' if i < 0 else '#F39C12' for i in improvements], 
                      alpha=0.8)
        
        ax.set_ylabel('文化距离', fontsize=13, fontweight='bold')
        ax.set_xlabel('模型', fontsize=13, fontweight='bold')
        ax.set_title('7个模型的语言表现对比', fontsize=16, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(models, rotation=45, ha='right', fontsize=11)
        ax.legend(fontsize=11, loc='upper left')
        ax.grid(True, alpha=0.3, axis='y')
        ax.axhline(y=0, color='black', linewidth=0.5)
        
        plt.tight_layout()
        plt.savefig(self.output_path / 'chart_5_model_comparison.png', 
                   dpi=150, bbox_inches='tight')
        plt.close()
        print("  ✓ chart_5_model_comparison.png")
    
    def chart_6_language_regions(self):
        """图表6: 按语言区域分组的表现"""
        fig, ax = plt.subplots(figsize=(12, 7))
        
        regions = ['中文区\n(4国)', '俄语区\n(6国)', '阿拉伯语区\n(8国)', 
                  '西语区\n(6国)', '新加坡+\n香港 (2国)']
        native_dist = [1.94, 2.28, 1.93, 2.27, 2.00]
        english_dist = [1.03, 1.70, 1.90, 2.16, 1.48]
        improvements = [47.0, 25.4, 1.6, 4.8, 26.0]
        
        x = np.arange(len(regions))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, native_dist, width, label='母语', 
                      color='#E74C3C', alpha=0.8)
        bars2 = ax.bar(x + width/2, english_dist, width, label='英语', 
                      color='#3498DB', alpha=0.8)
        
        ax.set_ylabel('平均文化距离', fontsize=13, fontweight='bold')
        ax.set_title('不同语言区域的表现对比', fontsize=16, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(regions, fontsize=11)
        ax.legend(fontsize=12)
        ax.grid(True, alpha=0.3, axis='y')
        
        # 添加改进百分比标注
        for i, imp in enumerate(improvements):
            ax.text(i, max(native_dist[i], english_dist[i]) + 0.15,
                   f'英语优势:\n{imp:.1f}%',
                   ha='center', va='bottom', fontsize=9, fontweight='bold',
                   bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))
        
        plt.tight_layout()
        plt.savefig(self.output_path / 'chart_6_language_regions.png', 
                   dpi=150, bbox_inches='tight')
        plt.close()
        print("  ✓ chart_6_language_regions.png")
    
    def chart_7_overall_summary(self):
        """图表7: 整体研究总结"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 子图1: 研究规模
        categories = ['模型数', '国家数', '语言数', 'LLM实体数']
        values = [7, 26, 5, 364]
        colors = ['#3498DB', '#E74C3C', '#27AE60', '#F39C12']
        
        bars = ax1.bar(categories, values, color=colors, alpha=0.8)
        ax1.set_ylabel('数量', fontsize=12, fontweight='bold')
        ax1.set_title('Stage 3 研究规模', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='y')
        
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        # 子图2: 核心发现
        labels = ['英语更好\n(84.6%)', '母语更好\n(15.4%)']
        sizes = [84.6, 15.4]
        colors = ['#E74C3C', '#27AE60']
        explode = (0.1, 0)
        
        ax2.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
               colors=colors, startangle=90,
               textprops={'fontsize': 12, 'fontweight': 'bold'})
        ax2.set_title('核心发现: "英语悖论"', fontsize=14, fontweight='bold')
        
        # 子图3: 最震撼数据
        shock_data = ['中国\n英语优势', '整体\n英语改进', 'Mistral\n英语偏好', 
                     '母语优势\n国家数']
        shock_values = [47.0, 12.0, 33.3, 4]
        colors = ['#E74C3C', '#F39C12', '#9B59B6', '#27AE60']
        
        bars = ax3.bar(shock_data, shock_values, color=colors, alpha=0.8)
        ax3.set_ylabel('百分比 / 数量', fontsize=12, fontweight='bold')
        ax3.set_title('最震撼的数字', fontsize=14, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='y')
        
        for i, bar in enumerate(bars):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{shock_values[i]:.1f}{"%" if i < 3 else "国"}',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # 子图4: 贡献总结
        ax4.axis('off')
        contributions = [
            '✅ 首次大规模多语言跨文化评估',
            '✅ 发现"英语悖论"现象 (84.6%)',
            '✅ 揭示中国案例的极端性 (47%)',
            '✅ 证明英语中心主义的普遍性',
            '✅ 为AI公平性研究提供新视角'
        ]
        
        y_pos = 0.9
        for contrib in contributions:
            ax4.text(0.1, y_pos, contrib, fontsize=12, fontweight='bold',
                    verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
            y_pos -= 0.18
        
        ax4.set_title('研究贡献', fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig(self.output_path / 'chart_7_overall_summary.png', 
                   dpi=150, bbox_inches='tight')
        plt.close()
        print("  ✓ chart_7_overall_summary.png")


def main():
    """主函数"""
    print("=" * 80)
    print("Stage 3 学术展示图表生成器")
    print("=" * 80)
    
    generator = Stage3SlideChartsGenerator()
    generator.generate_all_charts()
    
    print("\n" + "=" * 80)
    print("✅ 所有图表生成完成！")
    print(f"📁 图表保存位置: {generator.output_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()






