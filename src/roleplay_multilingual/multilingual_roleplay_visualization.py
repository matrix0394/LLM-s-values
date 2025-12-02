"""
多语言角色扮演可视化模块
创建多语言角色扮演结果的高级可视化
"""

import os
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
from typing import Dict, List, Optional, Any, Tuple
import warnings
warnings.filterwarnings('ignore')

# 添加项目路径
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.base.base_cultural_map_visualizer import BaseCulturalMapVisualizer


class MultilingualRoleplayVisualizer(BaseCulturalMapVisualizer):
    """多语言角色扮演可视化器"""
    
    def __init__(self, data_path: str = "data", results_path: str = "results"):
        """初始化多语言角色扮演可视化器（与Stage2保持一致）"""
        super().__init__(data_path=data_path, results_path=results_path)
        
        # 创建多语言角色扮演专用的结果子目录（统一命名为roleplay_ml_dashboard，与Stage2结构一致）
        # self.results_path已经是results/roleplay_multilingual，不要再嵌套
        self.roleplay_results_path = self.results_path / "roleplay_ml_dashboard"
        self.roleplay_results_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 可视化保存路径: {self.roleplay_results_path}")
        
        # 📊 统一的可视化格式标准（继承自base，与Stage2一致）
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
        
        self.model_colors = {
            'openai/gpt-4o-mini': '#1f77b4',
            'google/gemini-2.0-flash-001': '#ff7f0e', 
            'anthropic/claude-3.7-sonnet': '#2ca02c',
            'meta-llama/llama-3.3-70b-instruct': '#d62728',
            'deepseek/deepseek-chat-v3-0324': '#9467bd',
            'qwen/qwq-32b': '#8c564b',
            'mistralai/mistral-nemo:free': '#e377c2'
        }
        
        # 将多语言颜色合并到扩展颜色中
        self.extended_colors.update(self.language_colors)
        self.extended_colors.update(self.model_colors)
        
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
        加载PCA分析结果（从标准路径，与Stage2保持一致）
        
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
        """加载分析元数据（与PCA分析模块保持一致）"""
        if analysis_file is None:
            # 从processed_dir加载最新的分析元数据（与pca_analysis保存路径一致）
            roleplay_dir = self.data_path / "roleplay_multilingual"
            analysis_files = list(roleplay_dir.glob("roleplay_ml_analysis_metadata_*.json"))
            if not analysis_files:
                print("⚠️ 未找到分析元数据文件")
                return {}
            analysis_file = max(analysis_files, key=lambda x: x.stat().st_mtime)
        else:
            analysis_file = Path(analysis_file)
        
        print(f"✅ 加载分析元数据: {analysis_file.name}")
        
        with open(analysis_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    

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
        if 'language_analysis' in analysis_results:
            lang_stats = analysis_results['language_analysis']['language_statistics']
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
        
        ax1.set_xlabel('PC1 (传统 vs 世俗理性)')
        ax1.set_ylabel('PC2 (生存 vs 自我表达)')
        ax1.set_title('多语言文化地图')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 语言效应分析
        if 'language_analysis' in analysis_results:
            lang_stats = analysis_results['language_analysis']['language_statistics']
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
        
        ax3.set_xlabel('PC1 (传统 vs 世俗理性)')
        ax3.set_ylabel('PC2 (生存 vs 自我表达)')
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
            if 'language_analysis' in analysis_results:
                lang_diffs = analysis_results['language_analysis'].get('language_differences', {})
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
    
    def plot_language_comparison(self, data: pd.DataFrame = None, save_path: str = None):
        """绘制语言对比图"""
        if data is None:
            data = self.load_data()
        
        if data.empty:
            print("⚠️ 数据为空，无法绘制语言对比图。")
            return
        
        # 分离多语言数据
        multilingual_data = data[data['data_source'] == 'Multilingual']
        
        if len(multilingual_data) == 0:
            print("⚠️ 没有多语言数据，无法绘制语言对比图。")
            return
        
        plt.figure(figsize=(14, 10))
        
        # 按语言分组绘制
        if 'language' in multilingual_data.columns:
            languages = multilingual_data['language'].dropna().unique()
            language_colors = {'english': '#FF4500', 'native': '#32CD32'}
            
            for lang in languages:
                lang_data = multilingual_data[multilingual_data['language'] == lang]
                plt.scatter(
                    lang_data['PC1_rescaled'], 
                    lang_data['PC2_rescaled'],
                    c=language_colors.get(lang, '#800080'),
                    alpha=0.7,
                    s=80,
                    label=f'{lang.title()} Language ({len(lang_data)})',
                    edgecolors='black',
                    linewidth=0.5
                )
        
        # 添加坐标轴线
        plt.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        plt.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
        
        plt.xlabel('PC1: Survival vs Self-Expression Values', fontsize=14, fontweight='bold')
        plt.ylabel('PC2: Traditional vs Secular-Rational Values', fontsize=14, fontweight='bold')
        plt.title('Multilingual Language Comparison\n(Inglehart-Welzel Framework)', 
                 fontsize=16, fontweight='bold', pad=20)
        
        plt.legend(fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
            print(f"✅ 语言对比图已保存到: {save_path}")
        
        plt.close()


def main():
    """主函数"""
    visualizer = MultilingualRoleplayVisualizer()
    
    try:
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







