"""
多语言角色扮演可视化模块
创建多语言角色扮演结果的高级可视化
"""

import json
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple
import warnings
warnings.filterwarnings('ignore')

# 添加项目路径
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.base.base_cultural_map_visualizer import BaseCulturalMapVisualizer


class MultilingualRoleplayVisualizer(BaseCulturalMapVisualizer):
    """多语言角色扮演可视化器"""
    
    def __init__(self, data_path: str = "data", results_path: str = "results"):
        """初始化多语言角色扮演可视化器"""
        super().__init__(data_path=data_path, results_path=results_path)
        
        # 创建多语言角色扮演专用的结果子目录
        # self.results_path已经是results/roleplay_multilingual，不要再嵌套
        self.roleplay_results_path = self.results_path / "roleplay_ml_dashboard"
        self.roleplay_results_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 可视化保存路径: {self.roleplay_results_path}")
        
        # 📊 统一的可视化格式标准（继承自base）
        # matplotlib格式
        self.REAL_COUNTRY_SIZE = 50      # 真实国家点大小（base标准）
        self.REAL_COUNTRY_ALPHA = 0.7    # 真实国家透明度（base标准）
        self.ROLEPLAY_SIZE = 100         # 角色扮演点大小
        self.ROLEPLAY_ALPHA = 0.8        # 角色扮演透明度
        
        # plotly格式（HTML交互式图表）
        self.PLOTLY_REAL_SIZE = 8        # 真实国家点大小
        self.PLOTLY_REAL_OPACITY = 0.7   # 真实国家透明度（与base一致）
        self.PLOTLY_ROLEPLAY_SIZE = 12   # 角色扮演点大小
        self.PLOTLY_ROLEPLAY_OPACITY = 0.8  # 角色扮演透明度
        
        # 多语言特有的颜色方案
        self.language_colors = {
            'zh-cn': '#FF6B6B',  # 红色 - 中文
            'ru': '#4ECDC4',     # 青色 - 俄语  
            'es-la': '#45B7D1',  # 蓝色 - 拉美西语
            'ar': '#FFA07A'      # 橙色 - 阿拉伯语
        }
        
        # 将多语言颜色合并到扩展颜色中（模型颜色已在基类中定义）
        self.extended_colors.update(self.language_colors)
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 设置样式
        sns.set_style("whitegrid")
    
    def load_data(self) -> pd.DataFrame:
        """加载数据 - 实现基类抽象方法"""
        return self.load_pca_results()
    
    def load_pca_results(self, results_file: str = None) -> pd.DataFrame:
        """
        加载PCA分析结果
        
        标准路径：data/roleplay_multilingual/roleplay_ml_pca_entity_scores_latest.pkl
        """
        if results_file is None:
            # 标准路径：data/roleplay_multilingual/
            roleplay_dir = self.data_path / "roleplay_multilingual"
            
            data_paths = [
                # 1. 优先：最新版本（标准路径）
                roleplay_dir / "roleplay_ml_pca_entity_scores_latest.pkl",
                # 2. 带时间戳的最新文件
                *sorted(roleplay_dir.glob("roleplay_ml_pca_entity_scores_*.pkl"), 
                       key=lambda x: x.stat().st_mtime, reverse=True),
                # 3. 兼容旧路径
                *sorted(roleplay_dir.glob("multilingual_pca_results_*.pkl"),
                       key=lambda x: x.stat().st_mtime, reverse=True)
            ]
            
            for data_path in data_paths:
                if data_path.exists():
                    data = pd.read_pickle(data_path)
                    print(f"✅ 加载多语言角色扮演数据: {data_path.name} - {data.shape}")
                    return data
            
            raise FileNotFoundError(
                f"未找到多语言角色扮演PCA数据文件\n"
                f"期望路径: {roleplay_dir / 'roleplay_ml_pca_entity_scores_latest.pkl'}\n"
                f"请先运行PCA分析生成数据"
            )
        else:
            results_file = Path(results_file)
            print(f"加载PCA结果: {results_file}")
            return pd.read_pickle(results_file)
    
    def load_analysis_results(self, analysis_file: str = None) -> Dict:
        """加载语言分析结果"""
        if analysis_file is None:
            roleplay_dir = self.data_path / "roleplay_multilingual"
            analysis_file = roleplay_dir / "roleplay_ml_language_analysis_latest.json"
            
            if not analysis_file.exists():
                print("⚠️ 未找到语言分析文件，返回空结果")
                return {'language_statistics': {}, 'language_differences': {}}
        else:
            analysis_file = Path(analysis_file)
        
        print(f"✅ 加载语言分析结果: {analysis_file.name}")
        
        try:
            with open(analysis_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ 加载语言分析失败: {e}")
            return {'language_statistics': {}, 'language_differences': {}}
    

    def prepare_visualization_data(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """准备可视化数据，分离真实国家和多语言角色扮演数据"""
        # 分离真实国家数据和多语言数据
        if 'data_source' in data.columns:
            real_countries = data[data['data_source'] == 'IVS'].copy()
            multilingual_data = data[data['data_source'] == 'Multilingual'].copy()
        else:
            # 如果没有data_source列，尝试其他方法区分
            real_countries = data[~data.get('model', '').notna()].copy()
            multilingual_data = data[data.get('model', '').notna()].copy()
        
        # 🔥 关键修复：聚合IVS数据（按国家取平均，避免多个年份的重复）
        if len(real_countries) > 0:
            print(f"   聚合前IVS数据: {len(real_countries)} 行")
            # 按Country或country_code聚合
            group_col = 'Country' if 'Country' in real_countries.columns else 'country_code'
            if group_col in real_countries.columns:
                # 确定要聚合的列
                agg_dict = {
                    'PC1_rescaled': 'mean',
                    'PC2_rescaled': 'mean',
                    'data_source': 'first'
                }
                # 如果有Cultural Region列，也聚合它
                if 'Cultural Region' in real_countries.columns:
                    agg_dict['Cultural Region'] = 'first'
                
                real_countries = real_countries.groupby(group_col).agg(agg_dict).reset_index()
                print(f"   聚合后IVS数据: {len(real_countries)} 个国家")
        
        print(f"📊 数据分离完成:")
        print(f"   - 真实国家 (IVS): {len(real_countries)} 个")
        print(f"   - 多语言角色扮演: {len(multilingual_data)} 个")
        
        return real_countries, multilingual_data


    def create_interactive_cultural_map(self, df: pd.DataFrame, suffix: str = None) -> str:
        """创建交互式文化地图（包含IVS真实数据）"""
        if suffix is None:
            suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("创建交互式文化地图...")
        
        # 分离IVS真实数据和多语言数据
        real_countries, multilingual_data = self.prepare_visualization_data(df)
        
        # 创建交互式图表
        fig = go.Figure()
        
        # 1. 添加IVS真实国家数据（背景）
        if not real_countries.empty and 'PC1_rescaled' in real_countries.columns:
            # 按文化区域分组显示
            if 'Cultural Region' in real_countries.columns:
                for region in real_countries['Cultural Region'].unique():
                    if pd.isna(region):
                        continue
                    subset = real_countries[real_countries['Cultural Region'] == region]
                    color = self.cultural_region_colors.get(region, '#cccccc')
                    
                    fig.add_trace(go.Scatter(
                        x=subset['PC1_rescaled'],
                        y=subset['PC2_rescaled'],
                        mode='markers',
                        name=f'{region} (Real Countries)',
                        marker=dict(
                            color=color,
                            size=self.PLOTLY_REAL_SIZE,  # 使用统一格式常量
                            opacity=self.PLOTLY_REAL_OPACITY  # 使用统一格式常量
                        ),
                        hovertemplate=(
                            '<b>%{text}</b><br>' +
                            f'Cultural Region: {region}<br>' +
                            'Type: Real Country<br>' +
                            'PC1: %{x:.3f}<br>' +
                            'PC2: %{y:.3f}<br>' +
                            '<extra></extra>'
                        ),
                        text=subset.get('Country', subset.get('country', '')),
                        showlegend=True,
                        legendgroup='IVS'
                    ))
            else:
                # 没有文化区域信息，统一显示
                fig.add_trace(go.Scatter(
                    x=real_countries['PC1_rescaled'],
                    y=real_countries['PC2_rescaled'],
                    mode='markers',
                    name='Real Countries',
                    marker=dict(
                        color='#cccccc',
                        size=8,
                        opacity=0.7
                    ),
                    hovertemplate=(
                        '<b>%{text}</b><br>' +
                        'Type: Real Country<br>' +
                        'PC1: %{x:.3f}<br>' +
                        'PC2: %{y:.3f}<br>' +
                        '<extra></extra>'
                    ),
                    text=real_countries.get('Country', real_countries.get('country', '')),
                    showlegend=True
                ))
        
        # 2. 添加多语言角色扮演数据（前景）
        if not multilingual_data.empty:
            valid_ml = multilingual_data.dropna(subset=['PC1', 'PC2'])
            
            # 按语言分组显示
            if 'language' in valid_ml.columns:
                for language in valid_ml['language'].unique():
                    subset = valid_ml[valid_ml['language'] == language]
                    color = self.language_colors.get(language, '#999999')
                    
                    fig.add_trace(go.Scatter(
                        x=subset['PC1'],
                        y=subset['PC2'],
                        mode='markers',
                        name=f'Language: {language}',
                        marker=dict(
                            color=color,
                            size=self.PLOTLY_ROLEPLAY_SIZE,  # 使用统一格式常量
                            opacity=self.PLOTLY_ROLEPLAY_OPACITY,  # 使用统一格式常量
                            line=dict(width=1, color='white')
                        ),
                        hovertemplate=(
                            '<b>%{text}</b><br>' +
                            f'Language: {language}<br>' +
                            'Model: %{customdata[0]}<br>' +
                            'Country: %{customdata[1]}<br>' +
                            'PC1: %{x:.3f}<br>' +
                            'PC2: %{y:.3f}<br>' +
                            '<extra></extra>'
                        ),
                        text=subset.apply(lambda r: f"{r.get('model', 'Unknown')}-{r.get('country', 'Unknown')}", axis=1),
                        customdata=subset[['model', 'country']].values if 'model' in subset.columns and 'country' in subset.columns else None,
                        showlegend=True,
                        legendgroup='Multilingual'
                    ))
        
        # 设置布局
        fig.update_layout(
            title="Inglehart-Welzel Cultural Map: Stage 3 (Multilingual Roleplay with IVS Real Data)",
            xaxis_title="Survival vs. Self-Expression Values (PC1)",
            yaxis_title="Traditional vs. Secular-Rational Values (PC2)",
            hovermode='closest',
            template='plotly_white',
            width=1200,
            height=800,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=1.01
            )
        )
        
        # 保存到统一的dashboard目录（与Stage2一致）
        output_file = self.roleplay_results_path / f"multilingual_cultural_map_{suffix}.html"
        fig.write_html(str(output_file))
        print(f"✅ 交互式文化地图已保存: {output_file.name}")
        
        return str(output_file)

    def create_language_comparison_dashboard(self, df: pd.DataFrame, analysis_results: Dict, suffix: str = None) -> str:
        """创建语言对比仪表板"""
        if suffix is None:
            suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("创建语言对比仪表板...")
        
        # 创建子图
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('PC1分布对比', 'PC2分布对比', '语言距离热图', '模型-语言矩阵'),
            specs=[[{"type": "box"}, {"type": "box"}],
                   [{"type": "heatmap"}, {"type": "scatter"}]]
        )
        
        # 1. PC1分布对比
        valid_df = df.dropna(subset=['PC1', 'PC2'])
        for language in valid_df['language'].unique():
            lang_data = valid_df[valid_df['language'] == language]
            fig.add_trace(
                go.Box(y=lang_data['PC1'], name=language, 
                      marker_color=self.language_colors.get(language, 'gray')),
                row=1, col=1
            )
        
        # 2. PC2分布对比
        for language in valid_df['language'].unique():
            lang_data = valid_df[valid_df['language'] == language]
            fig.add_trace(
                go.Box(y=lang_data['PC2'], name=language, 
                      marker_color=self.language_colors.get(language, 'gray'),
                      showlegend=False),
                row=1, col=2
            )
        
        # 3. 语言距离热图
        if 'language_statistics' in analysis_results:
            lang_stats = analysis_results['language_statistics']
            languages = list(lang_stats.keys())
            
            # 创建距离矩阵
            distance_matrix = np.zeros((len(languages), len(languages)))
            for i, lang1 in enumerate(languages):
                for j, lang2 in enumerate(languages):
                    if i != j and not np.isnan(lang_stats[lang1]['pc1_mean']) and not np.isnan(lang_stats[lang2]['pc1_mean']):
                        pc1_diff = abs(lang_stats[lang1]['pc1_mean'] - lang_stats[lang2]['pc1_mean'])
                        pc2_diff = abs(lang_stats[lang1]['pc2_mean'] - lang_stats[lang2]['pc2_mean'])
                        distance_matrix[i, j] = np.sqrt(pc1_diff**2 + pc2_diff**2)
            
            fig.add_trace(
                go.Heatmap(z=distance_matrix, x=languages, y=languages,
                          colorscale='Viridis', showscale=True),
                row=2, col=1
            )
        
        # 4. 模型-语言散点图
        for model in valid_df['model'].unique():
            model_data = valid_df[valid_df['model'] == model]
            fig.add_trace(
                go.Scatter(x=model_data['PC1'], y=model_data['PC2'],
                          mode='markers', name=model.split('/')[-1],
                          marker=dict(size=8, opacity=0.6),
                          showlegend=False),
                row=2, col=2
            )
        
        fig.update_layout(
            title='多语言角色扮演分析仪表板',
            height=800,
            showlegend=True
        )
        
        # 保存仪表板
        output_file = self.roleplay_results_path / f'multilingual_comparison_dashboard_{suffix}.html'
        fig.write_html(str(output_file))
        
        print(f"语言对比仪表板已保存: {output_file}")
        return str(output_file)
    
    def create_model_performance_analysis(self, df: pd.DataFrame, suffix: str = None) -> str:
        """创建模型性能分析"""
        if suffix is None:
            suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("创建模型性能分析...")
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('模型成功率对比', '模型-语言组合热图', '模型PCA分布', '语言覆盖情况'),
            specs=[[{"type": "bar"}, {"type": "heatmap"}],
                   [{"type": "scatter"}, {"type": "bar"}]]
        )
        
        # 1. 模型成功率对比
        if 'success_rate' in df.columns:
            model_success = df.groupby('model')['success_rate'].mean().sort_values(ascending=False)
            
            fig.add_trace(
                go.Bar(x=model_success.index, y=model_success.values,
                      name='成功率', marker_color='lightblue'),
                row=1, col=1
            )
        
        # 2. 模型-语言组合热图
        model_lang_matrix = df.groupby(['model', 'language']).size().unstack(fill_value=0)
        
        fig.add_trace(
            go.Heatmap(z=model_lang_matrix.values,
                      x=model_lang_matrix.columns,
                      y=model_lang_matrix.index,
                      colorscale='Blues'),
            row=1, col=2
        )
        
        # 3. 模型PCA分布
        valid_df = df.dropna(subset=['PC1', 'PC2'])
        for model in valid_df['model'].unique():
            model_data = valid_df[valid_df['model'] == model]
            fig.add_trace(
                go.Scatter(x=model_data['PC1'], y=model_data['PC2'],
                          mode='markers', name=model.split('/')[-1],
                          marker=dict(size=8, 
                                    color=self.model_colors.get(model, 'gray'),
                                    opacity=0.6)),
                row=2, col=1
            )
        
        # 4. 语言覆盖情况
        lang_coverage = df.groupby('language').size()
        
        fig.add_trace(
            go.Bar(x=lang_coverage.index, y=lang_coverage.values,
                  name='样本数', marker_color='lightgreen'),
            row=2, col=2
        )
        
        fig.update_layout(
            title='模型性能分析',
            height=800,
            showlegend=True
        )
        
        # 保存分析图
        output_file = self.roleplay_results_path / f'model_performance_analysis_{suffix}.html'
        fig.write_html(str(output_file))
        
        print(f"模型性能分析已保存: {output_file}")
        return str(output_file)
    
    def create_static_summary_plots(self, df: pd.DataFrame, analysis_results: Dict, suffix: str = None):
        """创建静态摘要图表"""
        if suffix is None:
            suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("创建静态摘要图表...")
        
        # 1. 综合文化地图
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 按语言着色的文化地图
        valid_df = df.dropna(subset=['PC1', 'PC2'])
        for language in valid_df['language'].unique():
            lang_data = valid_df[valid_df['language'] == language]
            ax1.scatter(lang_data['PC1'], lang_data['PC2'],
                       c=self.language_colors.get(language, 'gray'),
                       label=language, s=100, alpha=0.7)
            
            # 添加国家标签
            for _, row in lang_data.iterrows():
                ax1.annotate(row['country'][:3], 
                           (row['PC1'], row['PC2']),
                           xytext=(3, 3), textcoords='offset points',
                           fontsize=8, alpha=0.8)
        
        ax1.set_xlabel('PC1 (生存 vs 自我表达)')
        ax1.set_ylabel('PC2 (传统 vs 世俗理性)')
        ax1.set_title('多语言文化地图')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 语言效应分析
        if 'language_statistics' in analysis_results:
            lang_stats = analysis_results['language_statistics']
            languages = []
            pc1_means = []
            pc1_stds = []
            
            for lang, stats in lang_stats.items():
                if not np.isnan(stats['pc1_mean']):
                    languages.append(lang)
                    pc1_means.append(stats['pc1_mean'])
                    pc1_stds.append(stats['pc1_std'])
            
            if languages:
                ax2.bar(languages, pc1_means, yerr=pc1_stds, capsize=5,
                       color=[self.language_colors.get(lang, 'gray') for lang in languages],
                       alpha=0.7)
                ax2.set_ylabel('PC1 均值')
                ax2.set_title('各语言PC1均值对比')
                ax2.tick_params(axis='x', rotation=45)
        
        # 模型分布
        for model in valid_df['model'].unique():
            model_data = valid_df[valid_df['model'] == model]
            ax3.scatter(model_data['PC1'], model_data['PC2'],
                       label=model.split('/')[-1], s=60, alpha=0.6)
        
        ax3.set_xlabel('PC1 (生存 vs 自我表达)')
        ax3.set_ylabel('PC2 (传统 vs 世俗理性)')
        ax3.set_title('模型分布对比')
        ax3.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax3.grid(True, alpha=0.3)
        
        # 样本统计
        stats_data = {
            '语言数': df['language'].nunique(),
            '模型数': df['model'].nunique(),
            '国家数': df['country'].nunique(),
            '总样本': len(df)
        }
        
        ax4.bar(stats_data.keys(), stats_data.values(), 
               color=['skyblue', 'lightgreen', 'lightcoral', 'gold'])
        ax4.set_ylabel('数量')
        ax4.set_title('数据统计摘要')
        
        plt.tight_layout()
        plt.savefig(self.roleplay_results_path / f'multilingual_summary_{suffix}.png',
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"静态摘要图表已保存")
    
    def generate_analysis_report(self, df: pd.DataFrame, analysis_results: Dict, suffix: str = None) -> str:
        """生成分析报告"""
        if suffix is None:
            suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("生成分析报告...")
        
        report = {
            "title": "多语言角色扮演分析报告",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_samples": len(df),
                "languages": df['language'].nunique(),
                "models": df['model'].nunique(),
                "countries": df['country'].nunique(),
                "valid_pca_samples": len(df.dropna(subset=['PC1', 'PC2']))
            },
            "language_analysis": {},
            "model_analysis": {},
            "key_findings": [],
            "recommendations": []
        }
        
        # 语言分析
        for language in df['language'].unique():
            lang_data = df[df['language'] == language]
            valid_lang_data = lang_data.dropna(subset=['PC1', 'PC2'])
            
            report["language_analysis"][language] = {
                "sample_count": len(lang_data),
                "valid_samples": len(valid_lang_data),
                "countries": lang_data['country'].unique().tolist(),
                "pc1_mean": valid_lang_data['PC1'].mean() if len(valid_lang_data) > 0 else np.nan,
                "pc2_mean": valid_lang_data['PC2'].mean() if len(valid_lang_data) > 0 else np.nan,
                "success_rate": lang_data['success_rate'].mean() if 'success_rate' in lang_data else np.nan
            }
        
        # 模型分析
        for model in df['model'].unique():
            model_data = df[df['model'] == model]
            valid_model_data = model_data.dropna(subset=['PC1', 'PC2'])
            
            report["model_analysis"][model] = {
                "sample_count": len(model_data),
                "valid_samples": len(valid_model_data),
                "languages": model_data['language'].unique().tolist(),
                "success_rate": model_data['success_rate'].mean() if 'success_rate' in model_data else np.nan
            }
        
        # 关键发现
        valid_df = df.dropna(subset=['PC1', 'PC2'])
        if len(valid_df) > 0:
            # 语言差异分析
            if 'language_differences' in analysis_results:
                lang_diffs = analysis_results.get('language_differences', {})
                if lang_diffs:
                    max_diff = max(lang_diffs.values(), key=lambda x: x['euclidean_distance'])
                    max_diff_pair = max(lang_diffs.keys(), key=lambda x: lang_diffs[x]['euclidean_distance'])
                    
                    report["key_findings"].append(
                        f"语言间最大文化距离: {max_diff_pair} (距离: {max_diff['euclidean_distance']:.3f})"
                    )
            
            # PC1和PC2的分布范围
            pc1_range = valid_df['PC1'].max() - valid_df['PC1'].min()
            pc2_range = valid_df['PC2'].max() - valid_df['PC2'].min()
            
            report["key_findings"].extend([
                f"PC1分布范围: {pc1_range:.3f}",
                f"PC2分布范围: {pc2_range:.3f}",
                f"数据完整性: {len(valid_df)/len(df)*100:.1f}%"
            ])
        
        # 建议
        report["recommendations"] = [
            "基于语言差异，建议重点关注文化距离较大的语言对",
            "对于成功率较低的模型-语言组合，建议优化提示词",
            "扩大样本量以提高统计显著性",
            "进行与英文基线的定量对比分析"
        ]
        
        # 保存报告
        report_file = self.roleplay_results_path / f'multilingual_analysis_report_{suffix}.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"分析报告已保存: {report_file}")
        return str(report_file)
    
    def create_complete_visualization_suite(self, results_file: str = None, analysis_file: str = None) -> Dict:
        """创建完整的可视化套件"""
        print("=== 多语言角色扮演可视化套件 ===")
        
        # 1. 加载数据
        print("1. 加载PCA结果...")
        df = self.load_pca_results(results_file)
        
        print("2. 加载分析结果...")
        analysis_results = self.load_analysis_results(analysis_file)
        
        # 3. 创建可视化
        suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("3. 创建交互式文化地图...")
        cultural_map = self.create_interactive_cultural_map(df, suffix)
        
        print("4. 创建语言对比仪表板...")
        comparison_dashboard = self.create_language_comparison_dashboard(df, analysis_results, suffix)
        
        print("5. 创建模型性能分析...")
        model_analysis = self.create_model_performance_analysis(df, suffix)
        
        print("6. 创建静态摘要图表...")
        self.create_static_summary_plots(df, analysis_results, suffix)
        
        print("7. 生成分析报告...")
        analysis_report = self.generate_analysis_report(df, analysis_results, suffix)
        
        # 8. 创建索引页面
        print("8. 创建可视化索引...")
        index_file = self._create_visualization_index(suffix, {
            'cultural_map': cultural_map,
            'comparison_dashboard': comparison_dashboard,
            'model_analysis': model_analysis,
            'analysis_report': analysis_report
        })
        
        print("\\n=== 可视化套件创建完成 ===")
        print(f"可视化文件保存在: {self.roleplay_results_path}")
        print(f"主页面: {index_file}")
        
        return {
            'index_file': index_file,
            'cultural_map': cultural_map,
            'comparison_dashboard': comparison_dashboard,
            'model_analysis': model_analysis,
            'analysis_report': analysis_report,
            'viz_directory': str(self.roleplay_results_path)
        }
    
    def _create_visualization_index(self, suffix: str, file_paths: Dict) -> str:
        """创建可视化索引页面"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>多语言角色扮演分析可视化</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #333; }}
                h2 {{ color: #666; }}
                .card {{ 
                    border: 1px solid #ddd; 
                    border-radius: 8px; 
                    padding: 20px; 
                    margin: 20px 0; 
                    background-color: #f9f9f9;
                }}
                .link {{ 
                    display: inline-block; 
                    padding: 10px 20px; 
                    background-color: #007bff; 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 5px; 
                    margin: 5px;
                }}
                .link:hover {{ background-color: #0056b3; }}
            </style>
        </head>
        <body>
            <h1>多语言角色扮演分析可视化</h1>
            <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <div class="card">
                <h2>📊 交互式可视化</h2>
                <a href="{Path(file_paths['cultural_map']).name}" class="link">文化地图</a>
                <a href="{Path(file_paths['comparison_dashboard']).name}" class="link">语言对比仪表板</a>
                <a href="{Path(file_paths['model_analysis']).name}" class="link">模型性能分析</a>
            </div>
            
            <div class="card">
                <h2>📈 静态图表</h2>
                <img src="multilingual_summary_{suffix}.png" alt="多语言摘要" style="max-width: 100%; height: auto;">
            </div>
            
            <div class="card">
                <h2>📋 分析报告</h2>
                <a href="{Path(file_paths['analysis_report']).name}" class="link">查看详细报告</a>
            </div>
            
            <div class="card">
                <h2>🔍 主要发现</h2>
                <ul>
                    <li>多语言角色扮演展现了不同的文化价值观模式</li>
                    <li>语言对文化价值观的表达有显著影响</li>
                    <li>不同模型在多语言环境下表现各异</li>
                    <li>本国语言可能提供更准确的文化模拟</li>
                </ul>
            </div>
        </body>
        </html>
        """
        
        index_file = self.roleplay_results_path / f'multilingual_visualization_index_{suffix}.html'
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(index_file)
    
    def apply_duplicate_coordinate_offset(self, coords_data: pd.DataFrame, 
                                         multilingual_data: pd.DataFrame,
                                         identifier_cols: list) -> pd.DataFrame:
        """
        应用坐标偏移以避免重复坐标重叠
        
        当多个数据点具有相同的坐标时，使用确定性偏移算法将它们分散开，
        使用黄金角度分布确保点均匀分布在圆周上。
        
        Parameters:
        -----------
        coords_data : pd.DataFrame
            包含PC1_rescaled和PC2_rescaled的数据框
        multilingual_data : pd.DataFrame
            全局多语言数据，用于检测重复坐标
        identifier_cols : list
            用于生成唯一标识符的列名列表，例如：['country_code', 'model_name', 'language']
            
        Returns:
        --------
        pd.DataFrame
            应用偏移后的坐标数据
            
        Examples:
        ---------
        >>> coords_data = visualizer.apply_duplicate_coordinate_offset(
        ...     coords_data=model_lang_data[['PC1_rescaled', 'PC2_rescaled']].copy(),
        ...     multilingual_data=multilingual_data,
        ...     identifier_cols=['country_code', 'model_name', 'language']
        ... )
        """
        coords_data = coords_data.copy()
        
        for idx in coords_data.index:
            current_x = round(coords_data.loc[idx, 'PC1_rescaled'], 6)
            current_y = round(coords_data.loc[idx, 'PC2_rescaled'], 6)
            
            # 检查与所有多语言数据的重复情况
            global_duplicates = multilingual_data[
                (multilingual_data['PC1_rescaled'].round(6) == current_x) & 
                (multilingual_data['PC2_rescaled'].round(6) == current_y)
            ]
            
            if len(global_duplicates) > 1:
                # 使用基于数据点信息的确定性偏移
                # 从原始数据中获取当前行（coords_data可能只包含坐标列）
                current_row = multilingual_data.loc[idx] if idx in multilingual_data.index else None
                
                if current_row is not None:
                    # 创建唯一标识符用于确定性偏移
                    identifier = '_'.join(str(current_row[col]) for col in identifier_cols if col in current_row.index)
                    hash_val = hash(identifier) % 1000
                    
                    # 使用更大的偏移量和圆形分布
                    offset_factor = 0.15  # 增加偏移量使点更明显分离
                    angle = (hash_val * 137.5) % 360  # 黄金角度分布
                    
                    offset_x = offset_factor * np.cos(np.radians(angle))
                    offset_y = offset_factor * np.sin(np.radians(angle))
                    
                    coords_data.loc[idx, 'PC1_rescaled'] += offset_x
                    coords_data.loc[idx, 'PC2_rescaled'] += offset_y
        
        return coords_data
    
    def generate_cultural_map_static(self, entity_scores: pd.DataFrame, save_path: str):
        """
        生成静态文化地图（matplotlib）
        
        Parameters:
        -----------
        entity_scores : pd.DataFrame
            包含IVS和Multilingual数据的实体分数
        save_path : str
            保存路径
        """
        print("🎨 生成静态文化地图...")
        
        # 分离数据
        ivs_data = entity_scores[entity_scores['data_source'] == 'IVS'].copy()
        multilingual_data = entity_scores[entity_scores['data_source'] == 'Multilingual'].copy()
        
        # 聚合IVS数据（按国家取平均，避免多个年份的重复）
        if len(ivs_data) > 0:
            print(f"   聚合前IVS数据: {len(ivs_data)} 行")
            group_col = 'Country' if 'Country' in ivs_data.columns else 'country_code'
            ivs_data = ivs_data.groupby(group_col).agg({
                'PC1_rescaled': 'mean',
                'PC2_rescaled': 'mean',
                'Cultural Region': 'first',
                'data_source': 'first'
            }).reset_index()
            print(f"   聚合后IVS数据: {len(ivs_data)} 个国家")
        
        # 设置图形样式
        plt.style.use('default')
        fig, ax = plt.subplots(1, 1, figsize=(18, 14))
        
        # 绘制IVS国家（背景）
        if len(ivs_data) > 0 and 'Cultural Region' in ivs_data.columns:
            regions = ivs_data['Cultural Region'].dropna().unique()
            
            for region in regions:
                if region in self.cultural_region_colors:
                    region_data = ivs_data[ivs_data['Cultural Region'] == region]
                    ax.scatter(
                        region_data['PC1_rescaled'], 
                        region_data['PC2_rescaled'],
                        c=self.cultural_region_colors[region], 
                        alpha=0.7, 
                        s=80, 
                        label=f'{region} ({len(region_data)} countries)',
                        marker='o',
                        edgecolors='white',
                        linewidth=1
                    )
        
        # 绘制多语言数据（前景）
        if len(multilingual_data) > 0 and 'model_name' in multilingual_data.columns and 'language' in multilingual_data.columns:
            print(f"   多语言数据: {len(multilingual_data)} 个实体")
            models = sorted(multilingual_data['model_name'].dropna().unique())
            languages = sorted(multilingual_data['language'].dropna().unique())
            print(f"   模型数: {len(models)}, 语言数: {len(languages)}")
            
            # 语言标记映射
            language_markers = {'english': 'o', 'native': 'D'}
            
            for model in models:
                model_short = model.split('/')[-1] if '/' in model else model
                model_color = self.llm_model_colors.get(model, '#95A5A6')
                
                for lang in languages:
                    model_lang_data = multilingual_data[
                        (multilingual_data['model_name'] == model) & 
                        (multilingual_data['language'] == lang)
                    ]
                    
                    if len(model_lang_data) > 0:
                        # 根据语言调整透明度和大小
                        alpha = 0.8 if lang == 'english' else 0.6
                        size = 60 if lang == 'english' else 40
                        
                        # 应用坐标偏移避免重叠
                        coords_data = self.apply_duplicate_coordinate_offset(
                            coords_data=model_lang_data[['PC1_rescaled', 'PC2_rescaled']].copy(),
                            multilingual_data=multilingual_data,
                            identifier_cols=['country_code', 'model_name', 'language']
                        )
                        
                        ax.scatter(
                            coords_data['PC1_rescaled'], 
                            coords_data['PC2_rescaled'],
                            c=model_color, 
                            alpha=alpha, 
                            s=size, 
                            label=f'{model_short} ({lang.title()})',
                            marker=language_markers.get(lang, 'o'),
                            edgecolors='black',
                            linewidth=0.8
                        )
        
        # 设置坐标轴标签
        ax.set_xlabel('PC1: Survival vs Self-Expression Values', fontsize=16, fontweight='bold')
        ax.set_ylabel('PC2: Traditional vs Secular-Rational Values', fontsize=16, fontweight='bold')
        ax.set_title('Cultural Values Map: Multilingual LLM Roleplay vs Real Countries\n(Inglehart-Welzel Framework)', 
                     fontsize=20, fontweight='bold', pad=25)
        
        # 添加网格和坐标轴
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.4, linewidth=1)
        ax.axvline(x=0, color='black', linestyle='-', alpha=0.4, linewidth=1)
        
        # 添加象限标签
        quadrant_style = dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8, edgecolor='gray')
        ax.text(0.02, 0.98, 'Self-Expression\n& Secular-Rational', 
                transform=ax.transAxes, fontsize=12, ha='left', va='top', bbox=quadrant_style)
        ax.text(0.02, 0.02, 'Survival\n& Secular-Rational', 
                transform=ax.transAxes, fontsize=12, ha='left', va='bottom', bbox=quadrant_style)
        ax.text(0.98, 0.98, 'Self-Expression\n& Traditional', 
                transform=ax.transAxes, fontsize=12, ha='right', va='top', bbox=quadrant_style)
        ax.text(0.98, 0.02, 'Survival\n& Traditional', 
                transform=ax.transAxes, fontsize=12, ha='right', va='bottom', bbox=quadrant_style)
        
        # 添加图例
        legend = ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=10, 
                           title='Cultural Regions & Languages', title_fontsize=12,
                           frameon=True, fancybox=True, shadow=True)
        legend.get_frame().set_facecolor('white')
        legend.get_frame().set_alpha(0.95)
        
        # 调整布局并保存
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"✅ 静态文化地图已保存: {save_path}")
    
    def generate_cultural_map_interactive(self, entity_scores: pd.DataFrame, save_path: str):
        """
        生成交互式文化地图（plotly HTML）
        
        Parameters:
        -----------
        entity_scores : pd.DataFrame
            包含IVS和Multilingual数据的实体分数
        save_path : str
            保存路径
        """
        try:
            import plotly.graph_objects as go
        except ImportError:
            print("⚠️ plotly未安装，跳过交互式地图生成")
            return
        
        print("🎨 生成交互式文化地图...")
        
        # 分离数据
        ivs_data = entity_scores[entity_scores['data_source'] == 'IVS'].copy()
        multilingual_data = entity_scores[entity_scores['data_source'] == 'Multilingual'].copy()
        
        # 聚合IVS数据
        if len(ivs_data) > 0:
            print(f"   聚合前IVS数据: {len(ivs_data)} 行")
            group_col = 'Country' if 'Country' in ivs_data.columns else 'country_code'
            ivs_data = ivs_data.groupby(group_col).agg({
                'PC1_rescaled': 'mean',
                'PC2_rescaled': 'mean',
                'Cultural Region': 'first',
                'data_source': 'first'
            }).reset_index()
            print(f"   聚合后IVS数据: {len(ivs_data)} 个国家")
        
        # 创建交互式图表
        fig = go.Figure()
        
        # 添加文化区域分组标题
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=0, color='rgba(0,0,0,0)'),
            name='<b>🌍 Cultural Regions (Real Countries)</b>',
            showlegend=True,
            hoverinfo='skip'
        ))
        
        # 添加IVS国家数据
        if len(ivs_data) > 0 and 'Cultural Region' in ivs_data.columns:
            regions = sorted(ivs_data['Cultural Region'].dropna().unique())
            
            for region in regions:
                if region in self.cultural_region_colors:
                    region_data = ivs_data[ivs_data['Cultural Region'] == region]
                    
                    # 创建hover文本
                    hover_text = []
                    for _, row in region_data.iterrows():
                        country_name = row.get('Country', 'Unknown')
                        if pd.isna(country_name):
                            country_name = f'Country {row.get("country_code", "Unknown")}'
                        
                        hover_text.append(
                            f'<b>{country_name}</b><br>' +
                            f'Region: {region}<br>' +
                            f'PC1 (Survival↔Self-Expression): {row["PC1_rescaled"]:.2f}<br>' +
                            f'PC2 (Traditional↔Secular): {row["PC2_rescaled"]:.2f}<br>' +
                            f'Source: Real Country (IVS)'
                        )
                    
                    fig.add_trace(go.Scatter(
                        x=region_data['PC1_rescaled'],
                        y=region_data['PC2_rescaled'],
                        mode='markers',
                        marker=dict(
                            color=self.cultural_region_colors[region],
                            size=12,
                            opacity=0.8,
                            line=dict(width=1, color='white'),
                            symbol='circle'
                        ),
                        name=f'  • {region} ({len(region_data)})',
                        text=hover_text,
                        hovertemplate='%{text}<extra></extra>',
                    ))
        
        # 添加多语言分组标题
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=0, color='rgba(0,0,0,0)'),
            name='<b>🌐 Multilingual LLM (Roleplay)</b>',
            showlegend=True,
            hoverinfo='skip'
        ))
        
        # 添加多语言数据
        if len(multilingual_data) > 0 and 'model_name' in multilingual_data.columns and 'language' in multilingual_data.columns:
            models = sorted(multilingual_data['model_name'].dropna().unique())
            languages = sorted(multilingual_data['language'].dropna().unique())
            
            # 语言符号映射
            language_symbols = {'english': 'circle', 'native': 'diamond'}
            
            for model in models:
                model_short = model.split('/')[-1] if '/' in model else model
                model_color = self.llm_model_colors.get(model, '#95A5A6')
                
                for lang in languages:
                    model_lang_data = multilingual_data[
                        (multilingual_data['model_name'] == model) & 
                        (multilingual_data['language'] == lang)
                    ]
                    
                    if len(model_lang_data) > 0:
                        # 创建hover文本
                        hover_text = []
                        for _, row in model_lang_data.iterrows():
                            country_name = row.get('country_code', 'Unknown')
                            
                            hover_text.append(
                                f'<b>{country_name}</b><br>' +
                                f'Model: {model_short}<br>' +
                                f'Language: {lang.title()}<br>' +
                                f'PC1 (Survival↔Self-Expression): {row["PC1_rescaled"]:.2f}<br>' +
                                f'PC2 (Traditional↔Secular): {row["PC2_rescaled"]:.2f}<br>' +
                                f'Source: Multilingual LLM'
                            )
                        
                        # 根据语言调整透明度
                        opacity = 0.8 if lang == 'english' else 0.6
                        size = 8 if lang == 'english' else 6
                        
                        # 应用坐标偏移避免重叠
                        coords_data = self.apply_duplicate_coordinate_offset(
                            coords_data=model_lang_data[['PC1_rescaled', 'PC2_rescaled']].copy(),
                            multilingual_data=multilingual_data,
                            identifier_cols=['country_code', 'model_name', 'language']
                        )
                        
                        fig.add_trace(go.Scatter(
                            x=coords_data['PC1_rescaled'],
                            y=coords_data['PC2_rescaled'],
                            mode='markers',
                            marker=dict(
                                color=model_color,
                                size=size,
                                opacity=opacity,
                                symbol=language_symbols.get(lang, 'circle'),
                                line=dict(width=1, color='black')
                            ),
                            name=f'  🤖 {model_short} ({lang.title()}) ({len(model_lang_data)})',
                            text=hover_text,
                            hovertemplate='%{text}<extra></extra>',
                        ))
        
        # 添加坐标轴线
        fig.add_hline(y=0, line_dash='dash', line_color='gray', opacity=0.5)
        fig.add_vline(x=0, line_dash='dash', line_color='gray', opacity=0.5)
        
        # 设置布局
        fig.update_layout(
            title=dict(
                text='<b>Cultural Values Map: Multilingual LLM Roleplay vs Real Countries</b><br>' +
                     '<sub>Inglehart-Welzel Framework • Independent Legend Control</sub>',
                x=0.5,
                font=dict(size=20)
            ),
            xaxis=dict(
                title='<b>PC1: Survival vs Self-Expression Values</b>',
                titlefont=dict(size=14),
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray'
            ),
            yaxis=dict(
                title='<b>PC2: Traditional vs Secular-Rational Values</b>',
                titlefont=dict(size=14),
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray'
            ),
            width=1500,
            height=900,
            showlegend=True,
            legend=dict(
                orientation='v',
                yanchor='top',
                y=1,
                xanchor='left',
                x=1.02,
                font=dict(size=11),
                bgcolor='rgba(255,255,255,0.95)',
                bordercolor='gray',
                borderwidth=1,
                itemsizing='constant'
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(r=300)
        )
        
        # 添加象限注释
        annotations = [
            dict(x=0.02, y=0.98, xref='paper', yref='paper',
                 text='<b>Self-Expression<br>& Secular-Rational</b>',
                 showarrow=False, font=dict(size=12), 
                 bgcolor='rgba(255,255,255,0.8)', bordercolor='gray'),
            dict(x=0.02, y=0.02, xref='paper', yref='paper',
                 text='<b>Survival<br>& Secular-Rational</b>',
                 showarrow=False, font=dict(size=12),
                 bgcolor='rgba(255,255,255,0.8)', bordercolor='gray'),
            dict(x=0.75, y=0.98, xref='paper', yref='paper',
                 text='<b>Self-Expression<br>& Traditional</b>',
                 showarrow=False, font=dict(size=12),
                 bgcolor='rgba(255,255,255,0.8)', bordercolor='gray'),
            dict(x=0.75, y=0.02, xref='paper', yref='paper',
                 text='<b>Survival<br>& Traditional</b>',
                 showarrow=False, font=dict(size=12),
                 bgcolor='rgba(255,255,255,0.8)', bordercolor='gray')
        ]
        
        fig.update_layout(annotations=annotations)
        
        # 保存HTML文件
        fig.write_html(save_path)
        print(f"✅ 交互式文化地图已保存: {save_path}")
    
    def plot_language_distance_comparison(self, comparison_results: dict, save_path: str = None):
        """
        绘制语言距离对比柱状图
        
        Parameters:
        -----------
        comparison_results : dict
            语言对比分析结果，包含summary字段
        save_path : str, optional
            保存路径，如果为None则使用默认路径
        """
        from datetime import datetime
        
        summary = comparison_results['summary']
        
        distances = []
        labels = []
        colors = []
        
        if summary['native_language_avg_distance']:
            distances.append(summary['native_language_avg_distance'])
            labels.append('Native Language')
            colors.append('#2E8B57')  # 深绿色
        
        if summary['english_language_avg_distance']:
            distances.append(summary['english_language_avg_distance'])
            labels.append('English Language')
            colors.append('#4169E1')  # 皇家蓝
        
        if not distances:
            print("⚠️ 没有足够的数据生成距离对比图")
            return
        
        plt.figure(figsize=(12, 8))
        bars = plt.bar(labels, distances, color=colors, alpha=0.8, edgecolor='black', linewidth=1)
        
        # 添加数值标签
        for bar, distance in zip(bars, distances):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{distance:.3f}', ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        plt.title('Language Effectiveness Comparison\n(Lower Distance = Better Performance)', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.ylabel('Average Distance to Real Countries', fontsize=14, fontweight='bold')
        plt.xlabel('Language Type', fontsize=14, fontweight='bold')
        
        # 添加改进百分比注释
        if summary['language_improvement']:
            improvement = summary['language_improvement']
            if improvement > 0:
                text = f'English is {improvement:.1f}% better'
                color = 'lightblue'
            else:
                text = f'Native is {-improvement:.1f}% better'
                color = 'lightgreen'
            
            plt.text(0.5, max(distances) * 0.8, text, 
                    transform=plt.gca().transAxes, ha='center', fontsize=12,
                    bbox=dict(boxstyle='round,pad=0.5', facecolor=color, alpha=0.7))
        
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        
        # 保存图片
        if save_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = self.roleplay_results_path / f"language_distance_comparison_{timestamp}.png"
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"✅ 距离对比图已保存: {save_path}")
    
    def plot_country_level_language_comparison(self, comparison_results: dict, save_path: str = None):
        """
        绘制国家级别的语言对比图
        
        Parameters:
        -----------
        comparison_results : dict
            语言对比分析结果
        save_path : str, optional
            保存路径
        """
        from datetime import datetime
        
        country_details = comparison_results['country_details']
        
        # 准备数据
        countries = []
        native_distances = []
        english_distances = []
        
        for country, data in country_details.items():
            if data['avg_native_distance'] or data['avg_english_distance']:
                countries.append(country)
                native_distances.append(data['avg_native_distance'] or 0)
                english_distances.append(data['avg_english_distance'] or 0)
        
        if not countries:
            print("⚠️ 没有足够的数据生成国家级别对比图")
            return
        
        # 限制显示前15个国家
        if len(countries) > 15:
            countries = countries[:15]
            native_distances = native_distances[:15]
            english_distances = english_distances[:15]
        
        x = np.arange(len(countries))
        width = 0.35
        
        plt.figure(figsize=(16, 10))
        
        plt.bar(x - width/2, native_distances, width, label='Native Language', 
               color='#2E8B57', alpha=0.8, edgecolor='black', linewidth=0.5)
        plt.bar(x + width/2, english_distances, width, label='English Language', 
               color='#4169E1', alpha=0.8, edgecolor='black', linewidth=0.5)
        
        plt.title('Country-Level Language Effectiveness Comparison', fontsize=16, fontweight='bold', pad=20)
        plt.ylabel('Average Distance to Real Country', fontsize=14, fontweight='bold')
        plt.xlabel('Countries', fontsize=14, fontweight='bold')
        plt.xticks(x, countries, rotation=45, ha='right')
        plt.legend(fontsize=12)
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        
        # 保存图片
        if save_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = self.roleplay_results_path / f"country_level_language_comparison_{timestamp}.png"
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"✅ 国家级别对比图已保存: {save_path}")
    
    def plot_interactive_language_comparison(self, comparison_results: dict, save_path: str = None):
        """
        生成交互式语言对比图
        
        Parameters:
        -----------
        comparison_results : dict
            语言对比分析结果
        save_path : str, optional
            保存路径
        """
        try:
            import plotly.graph_objects as go
        except ImportError:
            print("⚠️ plotly未安装，跳过交互式图表生成")
            return
        
        from datetime import datetime
        
        country_details = comparison_results['country_details']
        
        # 准备数据
        countries = []
        native_distances = []
        english_distances = []
        
        for country, data in country_details.items():
            countries.append(country)
            native_distances.append(data['avg_native_distance'])
            english_distances.append(data['avg_english_distance'])
        
        # 创建交互式图表
        fig = go.Figure()
        
        # 添加本国语言数据
        fig.add_trace(go.Bar(
            name='Native Language',
            x=countries,
            y=native_distances,
            marker_color='#2E8B57',
            opacity=0.8,
            hovertemplate='<b>%{x}</b><br>Native Language Distance: %{y:.3f}<extra></extra>'
        ))
        
        # 添加英文数据
        fig.add_trace(go.Bar(
            name='English Language',
            x=countries,
            y=english_distances,
            marker_color='#4169E1',
            opacity=0.8,
            hovertemplate='<b>%{x}</b><br>English Distance: %{y:.3f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(
                text='<b>Interactive Language Effectiveness Comparison</b><br><sub>Lower Distance = Better Performance</sub>',
                x=0.5,
                font=dict(size=18)
            ),
            xaxis=dict(
                title='<b>Countries</b>',
                titlefont=dict(size=14),
                tickangle=45
            ),
            yaxis=dict(
                title='<b>Average Distance to Real Country</b>',
                titlefont=dict(size=14)
            ),
            barmode='group',
            width=1200,
            height=700,
            showlegend=True,
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='center',
                x=0.5
            ),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        # 保存HTML文件
        if save_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = self.roleplay_results_path / f"interactive_language_comparison_{timestamp}.html"
        
        fig.write_html(save_path)
        print(f"✅ 交互式语言对比图已保存: {save_path}")
    
    def plot_model_language_comparison(self, comparison_results: dict, save_path: str = None):
        """
        绘制每个模型的语言效果对比图（双子图）
        
        Parameters:
        -----------
        comparison_results : dict
            语言对比分析结果，包含model_specific_analysis字段
        save_path : str, optional
            保存路径
        """
        from datetime import datetime
        
        model_analysis = comparison_results.get('model_specific_analysis', {})
        
        if not model_analysis:
            print("⚠️ 没有模型特定分析数据，跳过模型对比图")
            return
        
        # 准备数据
        models = []
        native_distances = []
        english_distances = []
        improvements = []
        
        for model_name, stats in model_analysis.items():
            if stats['native_avg_distance'] and stats['english_avg_distance']:
                models.append(model_name.split('/')[-1])  # 使用简短名称
                native_distances.append(stats['native_avg_distance'])
                english_distances.append(stats['english_avg_distance'])
                improvements.append(stats['language_improvement'])
        
        if not models:
            print("⚠️ 没有足够的数据生成模型对比图")
            return
        
        # 生成静态对比图
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
        
        # 左图：距离对比
        x = np.arange(len(models))
        width = 0.35
        
        bars1 = ax1.bar(x - width/2, native_distances, width, label='Native Language', 
                       color='#2E8B57', alpha=0.8, edgecolor='black')
        bars2 = ax1.bar(x + width/2, english_distances, width, label='English Language', 
                       color='#4169E1', alpha=0.8, edgecolor='black')
        
        # 添加数值标签
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{height:.3f}', ha='center', va='bottom', fontsize=10)
        
        for bar in bars2:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{height:.3f}', ha='center', va='bottom', fontsize=10)
        
        ax1.set_xlabel('Models', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Average Distance to Real Countries', fontsize=12, fontweight='bold')
        ax1.set_title('Model-Specific Language Performance Comparison\n(Lower Distance = Better Performance)', 
                     fontsize=14, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(models, rotation=45, ha='right')
        ax1.legend()
        ax1.grid(True, alpha=0.3, axis='y')
        
        # 右图：改进百分比
        colors = ['#2E8B57' if imp < 0 else '#4169E1' for imp in improvements]
        bars3 = ax2.bar(models, improvements, color=colors, alpha=0.8, edgecolor='black')
        
        # 添加数值标签
        for bar, imp in zip(bars3, improvements):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + (0.5 if height > 0 else -0.5),
                    f'{imp:.1f}%', ha='center', va='bottom' if height > 0 else 'top', fontsize=10)
        
        ax2.set_xlabel('Models', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Language Improvement (%)', fontsize=12, fontweight='bold')
        ax2.set_title('Language Effectiveness Improvement by Model\n(Positive = English Better, Negative = Native Better)', 
                     fontsize=14, fontweight='bold')
        ax2.set_xticklabels(models, rotation=45, ha='right')
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        ax2.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        # 保存静态图
        if save_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = self.roleplay_results_path / f"model_specific_language_comparison_{timestamp}.png"
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"✅ 模型语言对比图已保存: {save_path}")
    
    def plot_interactive_model_comparison(self, model_analysis: dict, save_path: str = None):
        """
        生成交互式模型对比图（plotly子图）
        
        Parameters:
        -----------
        model_analysis : dict
            模型特定分析结果
        save_path : str, optional
            保存路径
        """
        try:
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
        except ImportError:
            print("⚠️ plotly未安装，跳过交互式图表生成")
            return
        
        from datetime import datetime
        
        # 准备数据
        models = []
        native_distances = []
        english_distances = []
        improvements = []
        native_counts = []
        english_counts = []
        
        for model_name, stats in model_analysis.items():
            if stats['native_avg_distance'] and stats['english_avg_distance']:
                models.append(model_name.split('/')[-1])
                native_distances.append(stats['native_avg_distance'])
                english_distances.append(stats['english_avg_distance'])
                improvements.append(stats['language_improvement'])
                native_counts.append(stats['native_count'])
                english_counts.append(stats['english_count'])
        
        # 创建子图
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Distance Comparison by Model', 'Language Improvement by Model'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # 左图：距离对比
        fig.add_trace(
            go.Bar(
                name='Native Language',
                x=models,
                y=native_distances,
                marker_color='#2E8B57',
                opacity=0.8,
                hovertemplate='<b>%{x}</b><br>Native Distance: %{y:.3f}<br>Count: %{customdata}<extra></extra>',
                customdata=native_counts
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(
                name='English Language',
                x=models,
                y=english_distances,
                marker_color='#4169E1',
                opacity=0.8,
                hovertemplate='<b>%{x}</b><br>English Distance: %{y:.3f}<br>Count: %{customdata}<extra></extra>',
                customdata=english_counts
            ),
            row=1, col=1
        )
        
        # 右图：改进百分比
        colors = ['#2E8B57' if imp < 0 else '#4169E1' for imp in improvements]
        fig.add_trace(
            go.Bar(
                name='Language Improvement',
                x=models,
                y=improvements,
                marker_color=colors,
                opacity=0.8,
                hovertemplate='<b>%{x}</b><br>Improvement: %{y:.1f}%<br>' +
                             '<i>Positive = English Better<br>Negative = Native Better</i><extra></extra>',
                showlegend=False
            ),
            row=1, col=2
        )
        
        # 更新布局
        fig.update_layout(
            title=dict(
                text='<b>Model-Specific Language Performance Analysis</b>',
                x=0.5,
                font=dict(size=18)
            ),
            barmode='group',
            width=1400,
            height=600,
            showlegend=True
        )
        
        fig.update_xaxes(title_text="Models", row=1, col=1, tickangle=45)
        fig.update_yaxes(title_text="Average Distance", row=1, col=1)
        fig.update_xaxes(title_text="Models", row=1, col=2, tickangle=45)
        fig.update_yaxes(title_text="Improvement (%)", row=1, col=2)
        
        # 添加零线
        fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5, row=1, col=2)
        
        # 保存HTML文件
        if save_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = self.roleplay_results_path / f"interactive_model_language_comparison_{timestamp}.html"
        
        fig.write_html(save_path)
        print(f"✅ 交互式模型语言对比图已保存: {save_path}")


def main():
    """主函数 - 创建完整的多语言可视化套件"""
    print("🎨 多语言角色扮演可视化器")
    print("="*60)
    
    try:
        # 创建可视化器
        visualizer = MultilingualRoleplayVisualizer()
        
        # 创建完整的可视化套件
        result = visualizer.create_complete_visualization_suite()
        print("\\n✅ 多语言可视化套件创建完成！")
        print(f"\\n🌐 打开主页面查看结果:")
        print(f"  {result['index_file']}")
        
    except Exception as e:
        print(f"❌ 可视化创建失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
