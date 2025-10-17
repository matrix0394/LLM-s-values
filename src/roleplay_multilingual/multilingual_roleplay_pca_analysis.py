"""
多语言角色扮演PCA分析模块
对多语言角色扮演数据进行主成分分析，生成文化坐标
"""

import os
import json
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# 添加项目路径
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from src.core.ppca import PPCA
except ImportError:
    print("警告: 无法导入PPCA，将使用标准PCA")
    PPCA = None

from src.base.base_pca_analyzer import BasePCAAnalyzer


class MultilingualRoleplayPCAAnalysis(BasePCAAnalyzer):
    """多语言角色扮演PCA分析器"""
    
    def __init__(self, data_path: str = "../data"):
        # 调用父类构造函数
        super().__init__(data_path=data_path)
        
        # 多语言特有的配置
        self.processed_dir = self.data_path / "processed"
        self.results_dir = self.data_path / "results" / "multilingual_pca"
        
        # 确保目录存在
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # PCA配置（基类已有iv_qns，这里保持兼容）
        self.n_components = 2
        self.question_ids = self.iv_qns  # 使用基类的问题列表
        
        # 加载文化区域配置
        self.cultural_regions = self._load_cultural_regions()
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
    
    def _load_cultural_regions(self) -> Dict:
        """加载文化区域配置"""
        possible_paths = [
            Path("config/cultural_regions.json"),
            Path("../config/cultural_regions.json"),
            Path("../../config/cultural_regions.json")
        ]
        
        for config_path in possible_paths:
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        
        print("警告: 未找到文化区域配置文件")
        return {}
    
    def load_additional_data(self) -> pd.DataFrame:
        """加载额外数据（多语言角色扮演数据）- 实现基类抽象方法"""
        return self.load_processed_data()
    
    def load_processed_data(self, data_file: str = None) -> pd.DataFrame:
        """加载处理后的IVS格式数据"""
        if data_file is None:
            # 尝试多个可能的路径
            possible_paths = [
                self.data_path / "multilingual_roleplay_processed_responses_ivs_format.pkl",
                getattr(self, 'multilingual_data_path', None) and Path(self.multilingual_data_path) / "multilingual_roleplay_processed_responses_ivs_format.pkl",
                self.processed_dir / "multilingual_roleplay_processed_responses_ivs_format.pkl"
            ]
            
            # 过滤掉None值并查找存在的文件
            for path in filter(None, possible_paths):
                if path.exists():
                    data_file = path
                    break
            else:
                # 如果都没找到，查找最新的IVS格式文件
                ivs_files = list(self.processed_dir.glob("multilingual_roleplay_ivs_format_*.pkl"))
                if not ivs_files:
                    raise FileNotFoundError(f"未找到多语言IVS格式数据文件，查找路径: {[str(p) for p in possible_paths if p]}")
                data_file = max(ivs_files, key=lambda x: x.stat().st_mtime)
        else:
            data_file = Path(data_file)
        
        print(f"加载数据文件: {data_file}")
        
        with open(data_file, 'rb') as f:
            return pickle.load(f)
    
    def combine_data(self) -> pd.DataFrame:
        """合并数据（多语言实现）- 实现基类抽象方法，应用数据质量筛选"""
        # 准备IVS数据（应用标准筛选）
        ivs_data = self.prepare_ivs_data()
        ivs_data['data_source'] = 'IVS'
        
        # 加载多语言数据
        multilingual_data = self.load_additional_data()
        
        if multilingual_data.empty:
            print("⚠️ 多语言数据为空，仅使用IVS数据")
            return ivs_data
        
        try:
            # 处理多语言数据 - 应用相同的筛选标准
            multilingual_data_copy = multilingual_data.copy()
            multilingual_data_copy['data_source'] = 'Multilingual'
            
            # 关键修复：对多语言数据应用相同的筛选逻辑
            print(f"🔄 对多语言数据应用数据质量筛选...")
            print(f"   筛选前: {len(multilingual_data_copy)} 行")
            
            # 1. 确保有足够的IVS问题回答（至少6个）
            multilingual_data_copy = multilingual_data_copy.dropna(subset=self.iv_qns, thresh=6)
            print(f"   thresh=6筛选后: {len(multilingual_data_copy)} 行")
            
            # 2. 移除所有IVS问题都为NaN的行
            valid_ivs_mask = multilingual_data_copy[self.iv_qns].notna().any(axis=1)
            multilingual_data_copy = multilingual_data_copy[valid_ivs_mask]
            print(f"   移除全NaN行后: {len(multilingual_data_copy)} 行")
            
            # 3. 检查数据质量
            for col in self.iv_qns:
                if col in multilingual_data_copy.columns:
                    # 移除异常值（超出合理范围）
                    if col in ['A008', 'A165', 'E018', 'E025']:
                        # 1-4范围
                        mask = (multilingual_data_copy[col] >= 1) & (multilingual_data_copy[col] <= 4)
                        multilingual_data_copy.loc[~mask, col] = np.nan
                    elif col in ['F063', 'F118', 'F120', 'G006']:
                        # 1-10范围
                        mask = (multilingual_data_copy[col] >= 1) & (multilingual_data_copy[col] <= 10)
                        multilingual_data_copy.loc[~mask, col] = np.nan
                    elif col in ['Y002', 'Y003']:
                        # 特殊处理，保持原值
                        pass
            
            # 再次应用thresh=6筛选（清理异常值后）
            multilingual_data_copy = multilingual_data_copy.dropna(subset=self.iv_qns, thresh=6)
            print(f"   最终有效数据: {len(multilingual_data_copy)} 行")
            
            if len(multilingual_data_copy) == 0:
                print("⚠️ 多语言数据筛选后为空，仅使用IVS数据")
                return ivs_data
            
            # 高效的列对齐
            all_columns = list(set(ivs_data.columns) | set(multilingual_data_copy.columns))
            
            # 重新索引以对齐列
            ivs_aligned = ivs_data.reindex(columns=all_columns)
            multilingual_aligned = multilingual_data_copy.reindex(columns=all_columns)
            
            # 合并数据
            combined_data = pd.concat([
                ivs_aligned, 
                multilingual_aligned
            ], ignore_index=True)
            
            # 最终数据质量检查
            print(f"📊 数据合并完成:")
            print(f"   - 总计: {len(combined_data)} 行")
            print(f"   - IVS数据: {len(ivs_data)} 行")
            print(f"   - 多语言数据: {len(multilingual_data_copy)} 行")
            
            # 检查合并后的数据质量
            numeric_cols = [col for col in self.iv_qns if col in combined_data.columns]
            if numeric_cols:
                valid_data_per_col = combined_data[numeric_cols].notna().sum()
                print(f"   每列有效数据量: {dict(valid_data_per_col)}")
            
            return combined_data
            
        except Exception as e:
            print(f"❌ 数据合并失败: {e}")
            return multilingual_data.copy()
    
    def prepare_pca_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, np.ndarray, List[str]]:
        """准备PCA分析数据"""
        print("准备PCA分析数据...")
        
        # 选择用于PCA的问题列
        pca_columns = [col for col in self.question_ids if col in df.columns]
        print(f"用于PCA的问题: {pca_columns}")
        
        # 提取数据矩阵
        X = df[pca_columns].values
        
        # 检查数据质量
        print(f"数据形状: {X.shape}")
        print(f"缺失值数量: {np.isnan(X).sum()}")
        
        # 创建实体标签
        entity_labels = []
        for _, row in df.iterrows():
            label = f"{row['model']}_{row['country']}_{row['language']}"
            entity_labels.append(label)
        
        return df[['entity_id', 'model', 'country', 'language'] + pca_columns], X, entity_labels
    
    def perform_multilingual_pca_analysis(self, X: np.ndarray, use_ppca: bool = True) -> Tuple[np.ndarray, PCA, Dict]:
        """执行多语言特有的PCA分析"""
        print(f"执行PCA分析 (使用PPCA: {use_ppca and PPCA is not None})...")
        
        pca_results = {}
        
        if use_ppca and PPCA is not None and np.isnan(X).any():
            print("使用PPCA处理缺失数据...")
            # 使用PPCA处理缺失数据
            try:
                ppca = PPCA()
                X_filled = ppca.fit_transform(X, d=self.n_components)
            except Exception as e:
                print(f"PPCA失败，使用标准PCA: {e}")
                use_ppca = False
            
            if not use_ppca:
                # 使用标准PCA处理缺失数据
                print("使用标准PCA...")
                # 删除包含缺失值的行
                valid_mask = ~np.isnan(X).any(axis=1)
                X_clean = X[valid_mask]
                
                if len(X_clean) == 0:
                    raise ValueError("所有数据都包含缺失值，无法进行PCA分析")
                
                print(f"有效数据行数: {len(X_clean)}/{len(X)}")
                
                # 标准化
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X_clean)
                
                # PCA
                pca = PCA(n_components=self.n_components)
                pca_coords_clean = pca.fit_transform(X_scaled)
                
                # 为所有数据创建坐标（缺失数据用NaN填充）
                pca_coords = np.full((len(X), self.n_components), np.nan)
                pca_coords[valid_mask] = pca_coords_clean
                
                pca_results['method'] = 'StandardPCA'
                pca_results['valid_mask'] = valid_mask
                pca_results['scaler'] = scaler
            else:
                # 使用填充后的数据进行标准PCA
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X_filled)
                
                pca = PCA(n_components=self.n_components)
                pca_coords = pca.fit_transform(X_scaled)
                
                pca_results['method'] = 'PPCA + StandardPCA'
                pca_results['ppca'] = ppca
                pca_results['scaler'] = scaler
            
        else:
            print("使用标准PCA...")
            # 删除包含缺失值的行
            valid_mask = ~np.isnan(X).any(axis=1)
            X_clean = X[valid_mask]
            
            if len(X_clean) == 0:
                raise ValueError("所有数据都包含缺失值，无法进行PCA分析")
            
            print(f"有效数据行数: {len(X_clean)}/{len(X)}")
            
            # 标准化
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X_clean)
            
            # PCA
            pca = PCA(n_components=self.n_components)
            pca_coords_clean = pca.fit_transform(X_scaled)
            
            # 为所有数据创建坐标（缺失数据用NaN填充）
            pca_coords = np.full((len(X), self.n_components), np.nan)
            pca_coords[valid_mask] = pca_coords_clean
            
            pca_results['method'] = 'StandardPCA'
            pca_results['valid_mask'] = valid_mask
            pca_results['scaler'] = scaler
        
        # 保存PCA信息
        pca_results['pca'] = pca
        pca_results['explained_variance_ratio'] = pca.explained_variance_ratio_
        pca_results['components'] = pca.components_
        pca_results['n_components'] = self.n_components
        
        print(f"解释方差比例: {pca.explained_variance_ratio_}")
        print(f"累计解释方差: {pca.explained_variance_ratio_.sum():.3f}")
        
        return pca_coords, pca, pca_results
    
    def create_results_dataframe(self, df: pd.DataFrame, pca_coords: np.ndarray, entity_labels: List[str]) -> pd.DataFrame:
        """创建包含PCA结果的DataFrame"""
        results_df = df.copy()
        
        # 添加PCA坐标
        results_df['PC1'] = pca_coords[:, 0]
        results_df['PC2'] = pca_coords[:, 1]
        results_df['entity_label'] = entity_labels
        
        # 添加文化区域信息
        results_df['cultural_region'] = results_df['country'].map(
            self.cultural_regions.get('country_cultural_mapping', {})
        )
        
        # 添加语言家族信息
        language_families = {
            'zh-cn': '汉藏语系',
            'ru': '印欧语系',
            'es-la': '印欧语系',
            'ar': '闪含语系'
        }
        results_df['language_family'] = results_df['language'].map(language_families)
        
        return results_df
    
    def analyze_language_effects(self, results_df: pd.DataFrame) -> Dict:
        """分析语言效应"""
        print("分析语言效应...")
        
        language_analysis = {}
        
        # 按语言分组分析
        for language in results_df['language'].unique():
            lang_data = results_df[results_df['language'] == language]
            
            if len(lang_data) > 0:
                language_analysis[language] = {
                    'count': len(lang_data),
                    'countries': lang_data['country'].unique().tolist(),
                    'pc1_mean': lang_data['PC1'].mean() if not lang_data['PC1'].isna().all() else np.nan,
                    'pc1_std': lang_data['PC1'].std() if not lang_data['PC1'].isna().all() else np.nan,
                    'pc2_mean': lang_data['PC2'].mean() if not lang_data['PC2'].isna().all() else np.nan,
                    'pc2_std': lang_data['PC2'].std() if not lang_data['PC2'].isna().all() else np.nan,
                }
        
        # 计算语言间差异
        language_differences = {}
        languages = list(language_analysis.keys())
        
        for i, lang1 in enumerate(languages):
            for lang2 in languages[i+1:]:
                if (not np.isnan(language_analysis[lang1]['pc1_mean']) and 
                    not np.isnan(language_analysis[lang2]['pc1_mean'])):
                    
                    pc1_diff = abs(language_analysis[lang1]['pc1_mean'] - language_analysis[lang2]['pc1_mean'])
                    pc2_diff = abs(language_analysis[lang1]['pc2_mean'] - language_analysis[lang2]['pc2_mean'])
                    
                    language_differences[f"{lang1}_vs_{lang2}"] = {
                        'pc1_difference': pc1_diff,
                        'pc2_difference': pc2_diff,
                        'euclidean_distance': np.sqrt(pc1_diff**2 + pc2_diff**2)
                    }
        
        return {
            'language_statistics': language_analysis,
            'language_differences': language_differences
        }
    
    def create_visualizations(self, results_df: pd.DataFrame, pca_results: Dict, language_analysis: Dict, suffix: str = None):
        """创建可视化图表"""
        if suffix is None:
            suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("创建可视化图表...")
        
        # 设置图表样式
        plt.style.use('default')
        
        # 1. 多语言文化地图
        self._plot_multilingual_cultural_map(results_df, suffix)
        
        # 2. 语言对比图
        self._plot_language_comparison(results_df, suffix)
        
        # 3. 模型对比图
        self._plot_model_comparison(results_df, suffix)
        
        # 4. PCA载荷图
        self._plot_pca_loadings(pca_results, suffix)
        
        # 5. 解释方差图
        self._plot_explained_variance(pca_results, suffix)
        
        print("可视化图表创建完成")
    
    def _plot_multilingual_cultural_map(self, results_df: pd.DataFrame, suffix: str):
        """绘制多语言文化地图"""
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        
        # 为每种语言设置不同颜色
        language_colors = {
            'zh-cn': '#FF6B6B',
            'ru': '#4ECDC4', 
            'es-la': '#45B7D1',
            'ar': '#FFA07A'
        }
        
        # 绘制每种语言的点
        for language in results_df['language'].unique():
            lang_data = results_df[results_df['language'] == language]
            valid_data = lang_data.dropna(subset=['PC1', 'PC2'])
            
            if len(valid_data) > 0:
                ax.scatter(valid_data['PC1'], valid_data['PC2'], 
                          c=language_colors.get(language, 'gray'),
                          label=language, s=100, alpha=0.7)
                
                # 添加国家标签
                for _, row in valid_data.iterrows():
                    ax.annotate(row['country'][:3], 
                               (row['PC1'], row['PC2']),
                               xytext=(5, 5), textcoords='offset points',
                               fontsize=8, alpha=0.8)
        
        ax.set_xlabel('PC1 (传统 vs 世俗理性价值观)')
        ax.set_ylabel('PC2 (生存 vs 自我表达价值观)')
        ax.set_title('多语言角色扮演文化地图')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / f'multilingual_cultural_map_{suffix}.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_language_comparison(self, results_df: pd.DataFrame, suffix: str):
        """绘制语言对比图"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # PC1对比
        language_pc1 = []
        language_labels = []
        
        for language in results_df['language'].unique():
            lang_data = results_df[results_df['language'] == language]
            valid_pc1 = lang_data['PC1'].dropna()
            
            if len(valid_pc1) > 0:
                language_pc1.extend(valid_pc1.tolist())
                language_labels.extend([language] * len(valid_pc1))
        
        if language_pc1:
            pc1_df = pd.DataFrame({'Language': language_labels, 'PC1': language_pc1})
            sns.boxplot(data=pc1_df, x='Language', y='PC1', ax=ax1)
            ax1.set_title('PC1 按语言分布')
            ax1.set_ylabel('PC1 (传统 vs 世俗理性)')
        
        # PC2对比
        language_pc2 = []
        language_labels2 = []
        
        for language in results_df['language'].unique():
            lang_data = results_df[results_df['language'] == language]
            valid_pc2 = lang_data['PC2'].dropna()
            
            if len(valid_pc2) > 0:
                language_pc2.extend(valid_pc2.tolist())
                language_labels2.extend([language] * len(valid_pc2))
        
        if language_pc2:
            pc2_df = pd.DataFrame({'Language': language_labels2, 'PC2': language_pc2})
            sns.boxplot(data=pc2_df, x='Language', y='PC2', ax=ax2)
            ax2.set_title('PC2 按语言分布')
            ax2.set_ylabel('PC2 (生存 vs 自我表达)')
        
        plt.tight_layout()
        plt.savefig(self.results_dir / f'language_comparison_{suffix}.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_model_comparison(self, results_df: pd.DataFrame, suffix: str):
        """绘制模型对比图"""
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        
        # 为每个模型设置不同形状
        model_markers = {
            'openai/gpt-4o-mini': 'o',
            'google/gemini-2.0-flash-001': 's',
            'anthropic/claude-3.7-sonnet': '^',
            'meta-llama/llama-3.3-70b-instruct': 'D',
            'deepseek/deepseek-chat-v3-0324': 'v',
            'qwen/qwq-32b': 'p',
            'mistralai/mistral-nemo:free': '*'
        }
        
        for model in results_df['model'].unique():
            model_data = results_df[results_df['model'] == model]
            valid_data = model_data.dropna(subset=['PC1', 'PC2'])
            
            if len(valid_data) > 0:
                marker = model_markers.get(model, 'o')
                ax.scatter(valid_data['PC1'], valid_data['PC2'],
                          marker=marker, s=100, alpha=0.7,
                          label=model.split('/')[-1])
        
        ax.set_xlabel('PC1 (传统 vs 世俗理性价值观)')
        ax.set_ylabel('PC2 (生存 vs 自我表达价值观)')
        ax.set_title('多语言角色扮演 - 模型对比')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / f'model_comparison_{suffix}.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_pca_loadings(self, pca_results: Dict, suffix: str):
        """绘制PCA载荷图"""
        fig, ax = plt.subplots(1, 1, figsize=(10, 8))
        
        components = pca_results['components']
        
        # 绘制载荷向量
        for i, question_id in enumerate(self.question_ids):
            if i < components.shape[1]:
                ax.arrow(0, 0, components[0, i], components[1, i],
                        head_width=0.02, head_length=0.02, fc='red', ec='red')
                ax.text(components[0, i] * 1.1, components[1, i] * 1.1,
                       question_id, fontsize=10, ha='center', va='center')
        
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
        ax.set_xlabel(f'PC1 ({pca_results["explained_variance_ratio"][0]:.1%})')
        ax.set_ylabel(f'PC2 ({pca_results["explained_variance_ratio"][1]:.1%})')
        ax.set_title('PCA载荷图 - 多语言角色扮演')
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / f'pca_loadings_{suffix}.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_explained_variance(self, pca_results: Dict, suffix: str):
        """绘制解释方差图"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # 解释方差比例
        variance_ratio = pca_results['explained_variance_ratio']
        ax1.bar(range(1, len(variance_ratio) + 1), variance_ratio)
        ax1.set_xlabel('主成分')
        ax1.set_ylabel('解释方差比例')
        ax1.set_title('各主成分解释方差比例')
        
        # 累计解释方差
        cumsum_variance = np.cumsum(variance_ratio)
        ax2.plot(range(1, len(cumsum_variance) + 1), cumsum_variance, 'bo-')
        ax2.set_xlabel('主成分数量')
        ax2.set_ylabel('累计解释方差比例')
        ax2.set_title('累计解释方差比例')
        ax2.set_ylim(0, 1)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / f'explained_variance_{suffix}.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
    
    def save_analysis_results(self, results_df: pd.DataFrame, pca_results: Dict, 
                             language_analysis: Dict, suffix: str = None) -> Dict:
        """保存分析结果"""
        if suffix is None:
            suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存结果DataFrame
        results_file = self.results_dir / f'multilingual_pca_results_{suffix}.pkl'
        with open(results_file, 'wb') as f:
            pickle.dump(results_df, f)
        
        # 保存CSV格式
        csv_file = self.results_dir / f'multilingual_pca_results_{suffix}.csv'
        results_df.to_csv(csv_file, index=False, encoding='utf-8')
        
        # 保存分析结果
        analysis_results = {
            'pca_results': {k: v for k, v in pca_results.items() if k not in ['pca', 'ppca', 'scaler']},
            'language_analysis': language_analysis,
            'timestamp': datetime.now().isoformat(),
            'n_samples': len(results_df),
            'n_languages': results_df['language'].nunique(),
            'n_models': results_df['model'].nunique(),
            'n_countries': results_df['country'].nunique()
        }
        
        analysis_file = self.results_dir / f'multilingual_analysis_results_{suffix}.json'
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"分析结果已保存:")
        print(f"  PCA结果: {results_file}")
        print(f"  CSV格式: {csv_file}")
        print(f"  分析报告: {analysis_file}")
        
        return {
            'results_file': results_file,
            'csv_file': csv_file,
            'analysis_file': analysis_file
        }
    
    def run_multilingual_analysis(self, data_file: str = None) -> Dict:
        """运行完整的多语言PCA分析"""
        print("=== 多语言角色扮演PCA分析 ===")
        
        # 1. 加载数据
        print("1. 加载处理后的数据...")
        df = self.load_processed_data(data_file)
        
        # 2. 准备PCA数据
        print("2. 准备PCA分析数据...")
        pca_df, X, entity_labels = self.prepare_pca_data(df)
        
        # 3. 执行PCA分析
        print("3. 执行PCA分析...")
        pca_coords, pca, pca_results = self.perform_multilingual_pca_analysis(X)
        
        # 4. 创建结果DataFrame
        print("4. 创建结果DataFrame...")
        results_df = self.create_results_dataframe(pca_df, pca_coords, entity_labels)
        
        # 5. 分析语言效应
        print("5. 分析语言效应...")
        language_analysis = self.analyze_language_effects(results_df)
        
        # 6. 创建可视化
        print("6. 创建可视化图表...")
        self.create_visualizations(results_df, pca_results, language_analysis)
        
        # 7. 保存结果
        print("7. 保存分析结果...")
        file_paths = self.save_analysis_results(results_df, pca_results, language_analysis)
        
        # 8. 显示摘要
        print("\\n=== 分析结果摘要 ===")
        print(f"样本数: {len(results_df)}")
        print(f"语言数: {results_df['language'].nunique()}")
        print(f"模型数: {results_df['model'].nunique()}")
        print(f"国家数: {results_df['country'].nunique()}")
        print(f"解释方差: PC1={pca_results['explained_variance_ratio'][0]:.1%}, PC2={pca_results['explained_variance_ratio'][1]:.1%}")
        
        print("\\n各语言PC1均值:")
        for lang, stats in language_analysis['language_statistics'].items():
            if not np.isnan(stats['pc1_mean']):
                print(f"  {lang}: {stats['pc1_mean']:.3f}")
        
        return {
            'results_df': results_df,
            'pca_results': pca_results,
            'language_analysis': language_analysis,
            'file_paths': file_paths
        }
    
    def run_multilingual_analysis_for_runner(self) -> pd.DataFrame:
        """为run脚本运行多语言分析，返回实体分数DataFrame"""
        print("🚀 开始多语言角色扮演PCA分析...")
        
        # 使用基类的方法运行完整分析
        entity_scores = super().run_full_analysis()
        
        print(f"✅ 多语言PCA分析完成: {len(entity_scores)} 个实体")
        return entity_scores


def main():
    """主函数"""
    analyzer = MultilingualRoleplayPCAAnalysis()
    
    try:
        result = analyzer.run_complete_analysis()
        print("\\n✅ 多语言PCA分析完成！")
        print("\\n下一步可以运行可视化:")
        print("  python src/roleplay/multilingual_roleplay_visualization.py")
        
    except Exception as e:
        print(f"❌ PCA分析失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
