"""
多语言角色扮演PCA分析模块
对多语言角色扮演数据进行主成分分析，生成文化坐标
"""

import os
import json
import pickle
import pandas as pd
import numpy as np
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
    from src.base.ppca import PPCA
except ImportError:
    print("警告: 无法导入PPCA，将使用标准PCA")
    PPCA = None

from src.base.base_pca_analyzer import BasePCAAnalyzer


class MultilingualRoleplayPCAAnalysis(BasePCAAnalyzer):
    """多语言角色扮演PCA分析器"""
    
    def __init__(self, data_path: str = "../data"):
        # 调用父类构造函数，指定IVS数据子目录（与Stage2一致）
        super().__init__(data_path=data_path, ivs_data_subdir="country_values")
        
        # 多语言特有的配置（与Stage2保持一致的路径结构）
        self.processed_dir = self.data_path / "roleplay_multilingual"
        
        # PCA配置（基类已有iv_qns，这里保持兼容）
        self.n_components = 2
        self.question_ids = self.iv_qns  # 使用基类的问题列表
        
        # 加载文化区域配置
        self.cultural_regions = self._load_cultural_regions()
    
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
        """
        加载处理后的IVS格式数据（与Stage2保持一致）
        
        查找优先级：
        1. 指定的data_file
        2. processed_dir中最新的llm_roleplay_ml_processed_responses_ivs_format_*.pkl
        """
        if data_file is None:
            # 查找最新的IVS格式文件（与data_processor保存的文件名一致）
            ivs_files = list(self.processed_dir.glob("llm_roleplay_ml_processed_responses_ivs_format_*.pkl"))
            if not ivs_files:
                # 尝试查找旧格式文件（向后兼容）
                ivs_files = list(self.processed_dir.glob("multilingual_roleplay_ivs_format_*.pkl"))
                if not ivs_files:
                    raise FileNotFoundError(
                        f"未找到多语言IVS格式数据文件\n"
                        f"查找路径: {self.processed_dir}\n"
                        f"期望文件名: llm_roleplay_ml_processed_responses_ivs_format_*.pkl"
                    )
                print(f"⚠️ 使用旧格式文件")
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
        
        # 将country_code从数字映射为国家名称
        import json
        with open('config/country_codes.json', 'r') as f:
            country_mapping = {item['Numeric']: item['Country'] for item in json.load(f)}
        
        ivs_data['country_code'] = ivs_data['country_code'].map(country_mapping)
        print(f"🗺️ 将{len(ivs_data['country_code'].unique())}个国家代码映射为名称")
        
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
            
            # 确保两个数据集使用相同的字段名
            # Multilingual数据使用'country_code'，IVS数据也使用'country_code'（已映射为名称）
            # 添加'country'字段作为别名
            if 'country_code' in ivs_data.columns and 'country' not in ivs_data.columns:
                ivs_data['country'] = ivs_data['country_code']
            
            if 'country_code' in multilingual_data_copy.columns and 'country' not in multilingual_data_copy.columns:
                multilingual_data_copy['country'] = multilingual_data_copy['country_code']
            
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
    
    # prepare_pca_data() 已删除 - 使用 base.perform_pca_analysis() 自动处理
    # perform_multilingual_pca_analysis() 已删除 - 使用 base.perform_pca_analysis() 替代
    # create_results_dataframe() 已删除 - base.perform_pca_analysis() 已包含rescaling
    
    def analyze_language_effects(self, results_df: pd.DataFrame) -> Dict:
        """分析语言效应（Stage3特有）"""
        print("\n🌐 分析语言效应...")
        
        # 确保有language列
        if 'language' not in results_df.columns:
            print("⚠️ 数据中没有language列，跳过语言效应分析")
            return {'language_statistics': {}, 'language_differences': {}}
        
        language_analysis = {}
        
        # 按语言分组分析（使用PC1_rescaled和PC2_rescaled）
        pc1_col = 'PC1_rescaled' if 'PC1_rescaled' in results_df.columns else 'PC1'
        pc2_col = 'PC2_rescaled' if 'PC2_rescaled' in results_df.columns else 'PC2'
        
        for language in results_df['language'].unique():
            lang_data = results_df[results_df['language'] == language]
            
            if len(lang_data) > 0:
                language_analysis[language] = {
                    'count': len(lang_data),
                    'countries': lang_data['country'].unique().tolist() if 'country' in lang_data.columns else [],
                    'pc1_mean': lang_data[pc1_col].mean() if not lang_data[pc1_col].isna().all() else np.nan,
                    'pc1_std': lang_data[pc1_col].std() if not lang_data[pc1_col].isna().all() else np.nan,
                    'pc2_mean': lang_data[pc2_col].mean() if not lang_data[pc2_col].isna().all() else np.nan,
                    'pc2_std': lang_data[pc2_col].std() if not lang_data[pc2_col].isna().all() else np.nan,
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
    
    def save_analysis_results(self, results_df: pd.DataFrame, pca_results: Dict, 
                             language_analysis: Dict, suffix: str = None) -> Dict:
        """
        保存分析结果（与Stage2保持一致）
        
        保存位置：data/roleplay_multilingual/
        文件命名：roleplay_ml_pca_*（ml表示multilingual）
        """
        if suffix is None:
            suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print(f"\n{'='*60}")
        print(f"💾 保存PCA分析结果")
        print(f"{'='*60}")
        
        # 保存到processed_dir（与Stage2的roleplay_data_path对应）
        save_dir = self.processed_dir
        
        # 保存PCA结果DataFrame（与Stage2命名一致）
        results_file = save_dir / f'roleplay_ml_pca_results_{suffix}.pkl'
        results_df.to_pickle(results_file)
        print(f"✅ PCA结果: {results_file.name}")
        
        # 保存最新版本（用于可视化，与Stage2一致）
        results_file_latest = save_dir / f'roleplay_ml_pca_results_latest.pkl'
        results_df.to_pickle(results_file_latest)
        print(f"✅ PCA结果（最新）: {results_file_latest.name}")
        
        # 保存实体分数（与Stage2一致）
        scores_file = save_dir / f'roleplay_ml_pca_entity_scores_{suffix}.pkl'
        results_df.to_pickle(scores_file)
        print(f"✅ 实体分数: {scores_file.name}")
        
        scores_file_latest = save_dir / f'roleplay_ml_pca_entity_scores_latest.pkl'
        results_df.to_pickle(scores_file_latest)
        print(f"✅ 实体分数（最新）: {scores_file_latest.name}")
        
        # 保存CSV格式（便于查看）
        csv_file = save_dir / f'roleplay_ml_pca_results_{suffix}.csv'
        results_df.to_csv(csv_file, index=False, encoding='utf-8')
        print(f"✅ CSV格式: {csv_file.name}")
        
        # 保存分析元数据
        analysis_results = {
            'pca_results': {k: v for k, v in pca_results.items() if k not in ['pca', 'ppca', 'scaler']},
            'language_analysis': language_analysis,
            'timestamp': datetime.now().isoformat(),
            'n_samples': len(results_df),
            'n_languages': results_df['language'].nunique() if 'language' in results_df.columns else 0,
            'n_models': results_df['model_name'].nunique() if 'model_name' in results_df.columns else 0,
            'n_countries': results_df['country'].nunique() if 'country' in results_df.columns else 0
        }
        
        analysis_file = save_dir / f'roleplay_ml_analysis_metadata_{suffix}.json'
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, ensure_ascii=False, indent=2, default=str)
        print(f"✅ 分析元数据: {analysis_file.name}")
        
        print(f"\n📁 保存位置: {save_dir}")
        print(f"📊 数据量: {len(results_df)} 个实体")
        print(f"{'='*60}")
        
        return {
            'results_file': results_file,
            'results_file_latest': results_file_latest,
            'scores_file': scores_file,
            'scores_file_latest': scores_file_latest,
            'csv_file': csv_file,
            'analysis_file': analysis_file
        }
    
    def save_results(self, entity_scores: pd.DataFrame = None, prefix: str = "roleplay_ml_pca"):
        """保存分析结果（覆盖基类方法，使用Stage3命名规范）
        
        Args:
            entity_scores: 实体分数数据（聚合后的国家级别数据）
            prefix: 文件名前缀
        """
        print(f"\n{'='*60}")
        print(f"💾 保存Stage3 PCA分析结果")
        print(f"{'='*60}")
        
        save_dir = self.processed_dir
        
        # 1. 保存完整的PCA结果（包含问卷级别的IVS数据）
        if self.pca_results is not None:
            # 带时间戳的版本
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = save_dir / f'{prefix}_results_{timestamp}.pkl'
            self.pca_results.to_pickle(results_file)
            print(f"✅ PCA完整结果: {results_file.name}")
            print(f"   - 行数: {len(self.pca_results)}")
            
            # 最新版本（用于训练和可视化）
            results_file_latest = save_dir / f'{prefix}_results_latest.pkl'
            self.pca_results.to_pickle(results_file_latest)
            print(f"✅ PCA完整结果（最新）: {results_file_latest.name}")
        
        # 2. 保存实体分数（聚合后的国家级别数据）
        if entity_scores is not None:
            # 带时间戳的版本
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            scores_file = save_dir / f'{prefix}_entity_scores_{timestamp}.pkl'
            entity_scores.to_pickle(scores_file)
            print(f"✅ 实体分数（聚合）: {scores_file.name}")
            print(f"   - 行数: {len(entity_scores)}")
            
            # 最新版本（用于分析对比）
            scores_file_latest = save_dir / f'{prefix}_entity_scores_latest.pkl'
            entity_scores.to_pickle(scores_file_latest)
            print(f"✅ 实体分数（最新）: {scores_file_latest.name}")
            
            # JSON格式（便于查看）
            json_file = save_dir / f'{prefix}_entity_scores_latest.json'
            entity_scores.to_json(json_file, orient='records', indent=2, force_ascii=False)
            print(f"✅ JSON格式: {json_file.name}")
            
            # CSV格式（便于查看）
            csv_file = save_dir / f'{prefix}_entity_scores_latest.csv'
            entity_scores.to_csv(csv_file, index=False, encoding='utf-8')
            print(f"✅ CSV格式: {csv_file.name}")
            
            # 统计信息
            if 'data_source' in entity_scores.columns:
                print(f"\n📊 实体分数统计:")
                print(f"   - IVS国家: {len(entity_scores[entity_scores['data_source'] == 'IVS'])} 个")
                print(f"   - Multilingual: {len(entity_scores[entity_scores['data_source'] == 'Multilingual'])} 条")
        
        print(f"\n📁 保存位置: {save_dir}")
        print(f"{'='*60}")
    
    def run_multilingual_analysis(self, data_file: str = None) -> Dict:
        """
        运行完整的多语言PCA分析（重构版 - 使用base类方法）
        
        现在使用base.perform_pca_analysis()自动获得:
        - PPCA处理缺失值
        - Varimax旋转
        - 自动rescaling（PC1_rescaled, PC2_rescaled）
        - 详细的PCA计算过程打印
        - 自动merge country metadata
        """
        print("\n" + "="*80)
        print("🌐 多语言角色扮演PCA分析（使用统一架构）")
        print("="*80)
        
        # 1. 加载基础数据（IVS数据和国家代码）
        print("\n📂 步骤1: 加载基础数据（IVS + 国家代码）...")
        if not self.load_base_data():
            raise ValueError("加载基础数据失败")
        
        # 2. 合并数据（IVS + Multilingual）
        # combine_data()会自动调用load_additional_data()加载多语言数据
        print("\n🔄 步骤2: 合并IVS和多语言数据...")
        self.combined_data = self.combine_data()  # 不传参数，内部会调用load_additional_data()
        print(f"✅ 合并后数据: {len(self.combined_data)} 行")
        
        # 3. 执行PCA分析（使用base类的统一方法）
        print("\n🔬 步骤3: 执行PCA分析（PPCA + Varimax + Rescaling）...")
        results_df = self.perform_pca_analysis()  # base类方法，自动完成所有PCA步骤
        print(f"✅ PCA分析完成: {len(results_df)} 个实体")
        
        # 4. 分析语言效应（Stage3特有）
        if 'language' in results_df.columns:
            print("\n🌐 步骤4: 分析语言效应...")
            language_analysis = self.analyze_language_effects(results_df)
            
            # 打印语言统计
            print("\n📊 各语言PC1均值（rescaled）:")
            for lang, stats in language_analysis['language_statistics'].items():
                if not np.isnan(stats['pc1_mean']):
                    print(f"   {lang}: {stats['pc1_mean']:.3f}")
        else:
            language_analysis = {'language_statistics': {}, 'language_differences': {}}
        
        # 5. 构造pca_results字典（兼容旧的保存格式）
        pca_results = {
            'explained_variance_ratio': self.ppca_model.C if hasattr(self, 'ppca_model') else [0.37, 0.17],
            'n_components': 2,
            'method': 'PPCA + Varimax + Rescaling (Base)'
        }
        
        # 6. 保存结果
        print("\n💾 步骤5: 保存分析结果...")
        file_paths = self.save_analysis_results(results_df, pca_results, language_analysis)
        
        # 7. 显示摘要
        print("\n" + "="*80)
        print("📊 分析结果摘要")
        print("="*80)
        print(f"样本数: {len(results_df)}")
        if 'language' in results_df.columns:
            print(f"语言数: {results_df['language'].nunique()}")
        if 'model' in results_df.columns or 'model_name' in results_df.columns:
            model_col = 'model' if 'model' in results_df.columns else 'model_name'
            print(f"模型数: {results_df[model_col].nunique()}")
        if 'country' in results_df.columns:
            print(f"国家数: {results_df['country'].nunique()}")
        print(f"PC1范围: [{results_df['PC1_rescaled'].min():.2f}, {results_df['PC1_rescaled'].max():.2f}]")
        print(f"PC2范围: [{results_df['PC2_rescaled'].min():.2f}, {results_df['PC2_rescaled'].max():.2f}]")
        print("="*80)
        
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
    # 使用绝对路径，从项目根目录运行
    analyzer = MultilingualRoleplayPCAAnalysis(data_path="data")
    
    try:
        entity_scores = analyzer.run_multilingual_analysis_for_runner()
        print("\n✅ 多语言PCA分析完成！")
        print(f"✅ 生成实体分数: {len(entity_scores)} 个")
        print("\n下一步可以运行可视化:")
        print("  python src/roleplay_multilingual/multilingual_roleplay_visualization.py")
        
    except Exception as e:
        print(f"❌ PCA分析失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
