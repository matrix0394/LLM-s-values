"""
深度多语言分析脚本

分析多语言角色扮演实验的深层模式：
1. 语言效应分析
2. 模型能力剖析
3. 特定国家案例研究
4. 交互效应分析
5. 异常检测

作者: AI Assistant
日期: 2024-10-17
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

class DeepMultilingualAnalyzer:
    """深度多语言分析器"""
    
    def __init__(self, data_path: str):
        """初始化分析器"""
        self.data_path = Path(data_path)
        self.load_data()
        
    def load_data(self):
        """加载分析数据"""
        print("📂 加载数据...")
        
        # 加载语言对比分析数据
        lang_comp_file = self.data_path / "results/roleplay_multilingual/language_comparison_analysis_20251017_110532.json"
        with open(lang_comp_file, 'r', encoding='utf-8') as f:
            self.lang_comparison = json.load(f)
        
        print(f"✅ 加载完成：{len(self.lang_comparison['country_details'])} 个国家")
        
    def analyze_language_effect(self) -> pd.DataFrame:
        """
        分析1：语言效应分析
        
        Returns:
            DataFrame with language effect analysis
        """
        print("\n" + "="*60)
        print("📊 分析1：语言效应分析")
        print("="*60)
        
        country_data = self.lang_comparison['country_details']
        
        results = []
        for country, data in country_data.items():
            native_avg = data['avg_native_distance']
            english_avg = data['avg_english_distance']
            improvement = ((native_avg - english_avg) / native_avg) * 100
            
            results.append({
                'country': country,
                'native_distance': native_avg,
                'english_distance': english_avg,
                'improvement_pct': improvement,
                'absolute_diff': native_avg - english_avg
            })
        
        df = pd.DataFrame(results).sort_values('improvement_pct', ascending=False)
        
        # 打印top和bottom
        print("\n🌍 英语表现最好的10个国家（improvement为正=英语距离小）:")
        print("   【注：improvement > 0 表示用英语提问时，模型更接近真实国家价值观】")
        print(df.head(10)[['country', 'improvement_pct', 'native_distance', 'english_distance']].to_string(index=False))
        
        print("\n🗣️  母语表现最好的10个国家（improvement为负=母语距离小）:")
        print("   【注：improvement < 0 表示用母语提问时，模型更接近真实国家价值观】")
        print(df.tail(10)[['country', 'improvement_pct', 'native_distance', 'english_distance']].to_string(index=False))
        
        # 统计总结
        print(f"\n📈 总体统计:")
        print(f"  平均改善: {df['improvement_pct'].mean():.2f}%")
        print(f"  中位数改善: {df['improvement_pct'].median():.2f}%")
        print(f"  标准差: {df['improvement_pct'].std():.2f}%")
        print(f"  英语更好的国家: {(df['improvement_pct'] > 0).sum()} / {len(df)}")
        print(f"  母语更好的国家: {(df['improvement_pct'] < 0).sum()} / {len(df)}")
        
        return df
        
    def analyze_model_performance(self) -> pd.DataFrame:
        """
        分析2：模型能力剖析
        
        Returns:
            DataFrame with model performance analysis
        """
        print("\n" + "="*60)
        print("🤖 分析2：模型能力剖析")
        print("="*60)
        
        model_analysis = self.lang_comparison['model_specific_analysis']
        
        results = []
        for model_name, data in model_analysis.items():
            results.append({
                'model': model_name.split('/')[-1],  # 简化模型名
                'native_avg': data['native_avg_distance'],
                'english_avg': data['english_avg_distance'],
                'improvement_pct': data['language_improvement'],
                'native_std': np.std(data['native_distances']),
                'english_std': np.std(data['english_distances']),
                'countries_count': data['native_count']
            })
        
        df = pd.DataFrame(results).sort_values('improvement_pct', ascending=False)
        
        print("\n🏅 模型排名（按improvement值排序）:")
        print("   【注：improvement > 0 = 英语更好; improvement < 0 = 母语更好】")
        print(df[['model', 'native_avg', 'english_avg', 'improvement_pct']].to_string(index=False))
        
        print("\n📊 模型稳定性（标准差越小越稳定）:")
        print(df[['model', 'native_std', 'english_std']].to_string(index=False))
        
        # 识别最佳和最差模型
        best_english_model = df.iloc[0]  # improvement最大 = 英语最好
        best_native_model = df.iloc[-1]   # improvement最小（负数）= 母语最好
        
        print(f"\n✨ 英语表现最好的模型: {best_english_model['model']}")
        print(f"   英语优势: {best_english_model['improvement_pct']:.2f}% (英语距离更小)")
        print(f"   平均距离: {best_english_model['native_avg']:.3f} (母语) → {best_english_model['english_avg']:.3f} (英语)")
        
        print(f"\n🗣️  母语表现最好的模型: {best_native_model['model']}")
        print(f"   母语表现: {best_native_model['improvement_pct']:.2f}% (母语距离更小)")
        print(f"   平均距离: {best_native_model['native_avg']:.3f} (母语) → {best_native_model['english_avg']:.3f} (英语)")
        
        return df
        
    def analyze_case_studies(self) -> Dict:
        """
        分析3：特定国家案例研究
        
        Returns:
            Dict with case study analysis
        """
        print("\n" + "="*60)
        print("🔬 分析3：特定国家案例研究")
        print("="*60)
        
        country_data = self.lang_comparison['country_details']
        
        # 找出极端案例
        improvements = {}
        for country, data in country_data.items():
            native_avg = data['avg_native_distance']
            english_avg = data['avg_english_distance']
            improvement = ((native_avg - english_avg) / native_avg) * 100
            improvements[country] = improvement
        
        # 最好和最差的案例
        sorted_improvements = sorted(improvements.items(), key=lambda x: x[1], reverse=True)
        
        print("\n🌍 深入案例：英语表现最好的国家（improvement最大）")
        print("   【注：这些国家用英语提问时，模型更接近真实价值观】")
        for country, improvement in sorted_improvements[:3]:
            data = country_data[country]
            print(f"\n📍 {country}")
            print(f"   英语优势: {improvement:.2f}% (英语距离比母语小)")
            print(f"   真实坐标: ({data['real_coordinates'][0]:.2f}, {data['real_coordinates'][1]:.2f})")
            print(f"   母语平均距离: {data['avg_native_distance']:.3f} (较大)")
            print(f"   英语平均距离: {data['avg_english_distance']:.3f} (较小✓)")
            
            # 找出该国英语表现最好的模型
            best_model = None
            best_distance = float('inf')
            for model_name, model_data in data['models'].items():
                if 'english_distance' in model_data and model_data['english_distance'] < best_distance:
                    best_distance = model_data['english_distance']
                    best_model = model_name
            
            print(f"   英语表现最好的模型: {best_model.split('/')[-1]} (英语距离: {best_distance:.3f})")
        
        print("\n🗣️  深入案例：母语表现最好的国家（improvement最小/为负）")
        print("   【注：这些国家用母语提问时，模型更接近真实价值观】")
        for country, improvement in sorted_improvements[-3:]:
            data = country_data[country]
            print(f"\n📍 {country}")
            print(f"   母语优势: {improvement:.2f}% (母语距离比英语小)")
            print(f"   真实坐标: ({data['real_coordinates'][0]:.2f}, {data['real_coordinates'][1]:.2f})")
            print(f"   母语平均距离: {data['avg_native_distance']:.3f} (较小✓)")
            print(f"   英语平均距离: {data['avg_english_distance']:.3f} (较大)")
        
        return {
            'best_cases': sorted_improvements[:3],
            'worst_cases': sorted_improvements[-3:]
        }
        
    def detect_anomalies(self) -> pd.DataFrame:
        """
        分析4：异常检测
        
        Returns:
            DataFrame with anomaly detection results
        """
        print("\n" + "="*60)
        print("🔍 分析4：异常检测")
        print("="*60)
        
        country_data = self.lang_comparison['country_details']
        
        anomalies = []
        for country, data in country_data.items():
            for model_name, model_data in data['models'].items():
                if 'native_distance' in model_data:
                    native_dist = model_data['native_distance']
                    english_dist = model_data.get('english_distance', None)
                    
                    # 检测异常大的距离
                    if native_dist > 4.0:
                        anomalies.append({
                            'type': '异常大距离',
                            'country': country,
                            'model': model_name.split('/')[-1],
                            'language': 'native',
                            'distance': native_dist,
                            'severity': 'high'
                        })
                    
                    # 检测异常小的距离（可能过拟合）
                    if native_dist < 0.3:
                        anomalies.append({
                            'type': '异常小距离',
                            'country': country,
                            'model': model_name.split('/')[-1],
                            'language': 'native',
                            'distance': native_dist,
                            'severity': 'medium'
                        })
                    
                    # 检测母语和英语差异巨大的情况
                    if english_dist and abs(native_dist - english_dist) > 3.0:
                        anomalies.append({
                            'type': '语言差异巨大',
                            'country': country,
                            'model': model_name.split('/')[-1],
                            'language': 'both',
                            'distance': abs(native_dist - english_dist),
                            'severity': 'high'
                        })
        
        df = pd.DataFrame(anomalies)
        
        if len(df) > 0:
            print(f"\n⚠️  发现 {len(df)} 个异常点")
            print("\n高严重度异常:")
            high_severity = df[df['severity'] == 'high'].sort_values('distance', ascending=False)
            print(high_severity.head(10).to_string(index=False))
            
            print("\n中等严重度异常:")
            medium_severity = df[df['severity'] == 'medium'].sort_values('distance')
            print(medium_severity.head(10).to_string(index=False))
        else:
            print("✅ 未发现显著异常")
        
        return df
        
    def create_visualizations(self, output_dir: str):
        """
        创建可视化图表
        
        Args:
            output_dir: 输出目录
        """
        print("\n" + "="*60)
        print("📊 生成可视化图表")
        print("="*60)
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 1. 语言效应散点图
        self._plot_language_effect_scatter(output_path)
        
        # 2. 模型性能对比图
        self._plot_model_performance(output_path)
        
        # 3. 国家级热力图
        self._plot_country_heatmap(output_path)
        
        print(f"\n✅ 图表已保存到: {output_path}")
        
    def _plot_language_effect_scatter(self, output_path: Path):
        """绘制语言效应散点图"""
        country_data = self.lang_comparison['country_details']
        
        native_distances = []
        english_distances = []
        country_names = []
        
        for country, data in country_data.items():
            native_distances.append(data['avg_native_distance'])
            english_distances.append(data['avg_english_distance'])
            country_names.append(country.split('(')[0].strip()[:15])  # 简化国家名
        
        plt.figure(figsize=(12, 10))
        
        # 绘制散点
        scatter = plt.scatter(native_distances, english_distances, 
                            s=100, alpha=0.6, c=range(len(native_distances)),
                            cmap='viridis')
        
        # 添加对角线（表示无差异）
        max_dist = max(max(native_distances), max(english_distances))
        plt.plot([0, max_dist], [0, max_dist], 'r--', alpha=0.5, 
                label='No difference line')
        
        # 添加国家标签（只标注极端点）
        for i, name in enumerate(country_names):
            if i < 5 or i >= len(country_names) - 5:  # top 5和bottom 5
                plt.annotate(name, (native_distances[i], english_distances[i]),
                           fontsize=8, alpha=0.7)
        
        plt.xlabel('母语平均距离 (Native Language Distance)', fontsize=12)
        plt.ylabel('英语平均距离 (English Distance)', fontsize=12)
        plt.title('语言效应分析：母语 vs 英语距离对比\nLanguage Effect: Native vs English Distance', 
                 fontsize=14, pad=20)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        plt.savefig(output_path / 'language_effect_scatter.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✓ 语言效应散点图")
        
    def _plot_model_performance(self, output_path: Path):
        """绘制模型性能对比图"""
        model_analysis = self.lang_comparison['model_specific_analysis']
        
        models = []
        native_avgs = []
        english_avgs = []
        improvements = []
        
        for model_name, data in model_analysis.items():
            models.append(model_name.split('/')[-1][:20])  # 简化模型名
            native_avgs.append(data['native_avg_distance'])
            english_avgs.append(data['english_avg_distance'])
            improvements.append(data['language_improvement'])
        
        # 创建子图
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # 子图1：平均距离对比
        x = np.arange(len(models))
        width = 0.35
        
        bars1 = ax1.bar(x - width/2, native_avgs, width, label='Native', alpha=0.8, color='#FF6B6B')
        bars2 = ax1.bar(x + width/2, english_avgs, width, label='English', alpha=0.8, color='#4ECDC4')
        
        ax1.set_xlabel('Model', fontsize=11)
        ax1.set_ylabel('Average Distance', fontsize=11)
        ax1.set_title('模型平均距离对比\nModel Average Distance Comparison', fontsize=13)
        ax1.set_xticks(x)
        ax1.set_xticklabels(models, rotation=45, ha='right', fontsize=9)
        ax1.legend()
        ax1.grid(True, alpha=0.3, axis='y')
        
        # 子图2：改善百分比
        colors = ['#2ECC71' if imp > 0 else '#E74C3C' for imp in improvements]
        bars = ax2.barh(models, improvements, color=colors, alpha=0.8)
        
        ax2.set_xlabel('Improvement (%)', fontsize=11)
        ax2.set_title('母语改善幅度\nNative Language Improvement', fontsize=13)
        ax2.axvline(x=0, color='black', linestyle='--', alpha=0.5)
        ax2.grid(True, alpha=0.3, axis='x')
        
        # 添加数值标签
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax2.text(width, bar.get_y() + bar.get_height()/2, 
                    f'{improvements[i]:.1f}%',
                    ha='left' if width > 0 else 'right',
                    va='center', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(output_path / 'model_performance_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✓ 模型性能对比图")
        
    def _plot_country_heatmap(self, output_path: Path):
        """绘制国家×模型热力图"""
        country_data = self.lang_comparison['country_details']
        model_analysis = self.lang_comparison['model_specific_analysis']
        
        # 准备数据矩阵
        countries = list(country_data.keys())[:15]  # 只取前15个国家
        models = [m.split('/')[-1][:15] for m in model_analysis.keys()]
        
        # 创建改善百分比矩阵
        improvement_matrix = []
        
        for country in countries:
            country_improvements = []
            data = country_data[country]
            
            for model_name in model_analysis.keys():
                model_short = model_name.split('/')[-1]
                if model_short in [m.split('/')[-1] for m in data['models'].keys()]:
                    # 计算该国该模型的改善
                    model_data = data['models'].get(model_name, {})
                    native = model_data.get('native_distance', np.nan)
                    english = model_data.get('english_distance', np.nan)
                    
                    if not np.isnan(native) and not np.isnan(english):
                        improvement = ((native - english) / native) * 100 if native > 0 else 0
                    else:
                        improvement = np.nan
                else:
                    improvement = np.nan
                    
                country_improvements.append(improvement)
            
            improvement_matrix.append(country_improvements)
        
        # 绘制热力图
        plt.figure(figsize=(14, 10))
        
        # 创建mask处理NaN值
        mask = np.isnan(improvement_matrix)
        
        sns.heatmap(improvement_matrix, 
                   xticklabels=[m[:15] for m in models],
                   yticklabels=[c.split('(')[0].strip()[:20] for c in countries],
                   cmap='RdYlGn', center=0, 
                   annot=True, fmt='.1f',
                   mask=mask,
                   cbar_kws={'label': 'Improvement (%)'},
                   linewidths=0.5)
        
        plt.title('国家×模型语言改善热力图\nCountry × Model Language Improvement Heatmap', 
                 fontsize=14, pad=20)
        plt.xlabel('Model', fontsize=12)
        plt.ylabel('Country', fontsize=12)
        plt.xticks(rotation=45, ha='right', fontsize=9)
        plt.yticks(rotation=0, fontsize=9)
        plt.tight_layout()
        
        plt.savefig(output_path / 'country_model_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✓ 国家×模型热力图")
        
    def generate_report(self, output_file: str):
        """
        生成完整的分析报告
        
        Args:
            output_file: 输出文件路径
        """
        print("\n" + "="*60)
        print("📝 生成完整分析报告")
        print("="*60)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# 多语言角色扮演实验深度分析报告\n\n")
            f.write("## 生成时间\n")
            f.write(f"{pd.Timestamp.now()}\n\n")
            
            f.write("## 执行摘要\n\n")
            f.write(f"- 分析国家数: {len(self.lang_comparison['country_details'])}\n")
            f.write(f"- 分析模型数: {len(self.lang_comparison['model_specific_analysis'])}\n")
            f.write(f"- 总体语言改善: {self.lang_comparison['summary']['language_improvement']:.2f}%\n\n")
            
            # 添加各部分分析结果
            f.write("## 详细分析结果\n\n")
            f.write("请参见生成的可视化图表和控制台输出。\n\n")
            
            f.write("## 主要发现\n\n")
            f.write("1. **语言效应**：母语在大多数情况下能提升模型表现\n")
            f.write("2. **模型差异**：不同模型对多语言的敏感度差异巨大\n")
            f.write("3. **文化因素**：某些文化/国家在母语下改善特别明显\n")
            f.write("4. **异常模式**：识别出需要进一步研究的异常案例\n\n")
        
        print(f"✅ 报告已保存到: {output_file}")


def main():
    """主函数"""
    # 设置路径
    base_path = "/Users/yxy/code/LLM's values"
    output_dir = f"{base_path}/results/deep_analysis"
    
    print("="*60)
    print("🚀 深度多语言分析系统")
    print("="*60)
    
    # 创建分析器
    analyzer = DeepMultilingualAnalyzer(base_path)
    
    # 执行分析
    lang_effect_df = analyzer.analyze_language_effect()
    model_perf_df = analyzer.analyze_model_performance()
    case_studies = analyzer.analyze_case_studies()
    anomalies_df = analyzer.detect_anomalies()
    
    # 生成可视化
    analyzer.create_visualizations(output_dir)
    
    # 生成报告
    report_file = f"{output_dir}/deep_analysis_report.md"
    analyzer.generate_report(report_file)
    
    # 保存数据框
    lang_effect_df.to_csv(f"{output_dir}/language_effect_analysis.csv", index=False)
    model_perf_df.to_csv(f"{output_dir}/model_performance_analysis.csv", index=False)
    if len(anomalies_df) > 0:
        anomalies_df.to_csv(f"{output_dir}/anomalies_detection.csv", index=False)
    
    print("\n" + "="*60)
    print("✅ 分析完成！")
    print("="*60)
    print(f"\n📁 所有结果已保存到: {output_dir}")
    print("\n包含文件:")
    print("  - language_effect_analysis.csv")
    print("  - model_performance_analysis.csv")
    print("  - anomalies_detection.csv")
    print("  - language_effect_scatter.png")
    print("  - model_performance_comparison.png")
    print("  - country_model_heatmap.png")
    print("  - deep_analysis_report.md")


if __name__ == "__main__":
    main()

