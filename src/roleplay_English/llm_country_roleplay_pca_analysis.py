"""
新的LLM国家角色扮演PCA分析器 - 基于BasePCAAnalyzer
替换原有的复杂LLMCountryRoleplayPCAAnalyzer类
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path
from typing import Dict, Any, List

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.base.base_pca_analyzer import BasePCAAnalyzer
from src.roleplay_English.llm_country_roleplay_data_processor import LLMCountryRoleplayDataProcessor


class LLMCountryRoleplayPCAAnalyzer(BasePCAAnalyzer):
    """LLM国家角色扮演PCA分析器 - 继承基类，专注于角色扮演数据分析"""
    
    def __init__(self, data_path: str = "data"):
        """初始化角色扮演PCA分析器"""
        # 传递ivs_data_subdir="country_values"以正确加载IVS数据
        super().__init__(data_path, ivs_data_subdir="country_values")
        
        # 设置roleplay专用的保存路径
        self.roleplay_data_path = Path(data_path) / "roleplay_English"
        self.roleplay_data_path.mkdir(exist_ok=True)
        
        # 初始化角色扮演数据处理器
        self.data_processor = LLMCountryRoleplayDataProcessor(data_dir=str(self.roleplay_data_path))
        self.roleplay_data = None
    
    def load_additional_data(self) -> pd.DataFrame:
        """加载角色扮演数据（优先使用IVS格式，用于PCA分析）"""
        try:
            # 查找最新的带时间戳文件
            print("🔍 查找最新的角色扮演数据文件...")
            
            # 1. 优先查找IVS格式最新版本文件（用于PCA分析）
            latest_ivs_file = self.roleplay_data_path / "llm_roleplay_processed_responses_ivs_format_latest.pkl"
            if latest_ivs_file.exists():
                self.roleplay_data = pd.read_pickle(latest_ivs_file)
                print(f"✅ 加载最新IVS格式数据: {latest_ivs_file.name} - {self.roleplay_data.shape}")
                return self.roleplay_data
            
            # 2. 查找带时间戳的IVS格式文件（最新的）
            ivs_files = list(self.roleplay_data_path.glob("llm_roleplay_processed_responses_ivs_format_*.pkl"))
            if ivs_files:
                latest_ivs_file = max(ivs_files, key=lambda x: x.stat().st_mtime)
                self.roleplay_data = pd.read_pickle(latest_ivs_file)
                print(f"✅ 加载带时间戳的IVS格式数据: {latest_ivs_file.name} - {self.roleplay_data.shape}")
                return self.roleplay_data
            
            # 3. 如果没有IVS格式，尝试加载原始格式（需要转换）
            latest_file = self.roleplay_data_path / "llm_roleplay_processed_responses_latest.pkl"
            if latest_file.exists():
                print(f"⚠️ 仅找到原始格式数据，需要IVS格式用于PCA分析")
                self.roleplay_data = pd.read_pickle(latest_file)
                print(f"   加载原始数据: {latest_file.name} - {self.roleplay_data.shape}")
                print(f"   建议：运行数据处理器生成IVS格式数据")
                return self.roleplay_data
            
            # 4. 查找带时间戳的原始处理文件（最新的）
            processed_files = list(self.roleplay_data_path.glob("llm_roleplay_processed_responses_*.pkl"))
            if processed_files:
                latest_processed_file = max(processed_files, key=lambda x: x.stat().st_mtime)
                self.roleplay_data = pd.read_pickle(latest_processed_file)
                print(f"✅ 加载带时间戳的处理数据: {latest_processed_file.name} - {self.roleplay_data.shape}")
                return self.roleplay_data
            
            # 4. 回退到旧的固定路径（兼容性）
            base_data_path = self.data_path.parent if self.data_path.name == 'country_values' else self.data_path
            fallback_paths = [
                base_data_path / "roleplay_English" / "llm_roleplay_processed_responses_ivs_format.pkl",
                self.data_path / "roleplay_English" / "llm_roleplay_processed_responses_ivs_format.pkl",
                self.data_path / "processed" / "llm_roleplay_processed_responses_ivs_format.pkl",
                self.data_path / "llm_roleplay_processed_responses_ivs_format.pkl"
            ]
            
            for roleplay_path in fallback_paths:
                if roleplay_path.exists():
                    self.roleplay_data = pd.read_pickle(roleplay_path)
                    print(f"✅ 加载兼容性角色扮演数据: {roleplay_path} - {self.roleplay_data.shape}")
                    return self.roleplay_data
            
            print("⚠️ 未找到已处理的角色扮演数据，将使用数据处理器处理原始数据")
            print("尝试的路径:")
            print(f"  - {latest_file}")
            for path in fallback_paths:
                print(f"  - {path}")
            
            # 如果没有找到已处理数据，尝试处理原始数据
            return self._process_raw_roleplay_data()
            
        except Exception as e:
            print(f"❌ 加载角色扮演数据失败: {e}")
            return pd.DataFrame()
    
    def _process_raw_roleplay_data(self) -> pd.DataFrame:
        """处理原始角色扮演数据"""
        try:
            print("🔄 开始处理原始角色扮演数据...")
            
            # 使用数据处理器处理原始数据
            processed_data = self.data_processor.process_all_responses()
            
            if processed_data is not None and len(processed_data) > 0:
                # 转换为IVS格式
                ivs_format_data = self.data_processor.create_ivs_format_data(processed_data)
                
                print(f"✅ 原始数据处理完成: {len(ivs_format_data)} 行")
                return ivs_format_data
            else:
                print("❌ 原始数据处理失败或无数据")
                return pd.DataFrame()
            
        except Exception as e:
            print(f"❌ 处理原始角色扮演数据失败: {e}")
            return pd.DataFrame()
    
    def _apply_data_quality_filters(self, data: pd.DataFrame) -> pd.DataFrame:
        """对数据应用质量筛选"""
        try:
            print(f"🔄 应用数据质量筛选...")
            print(f"   筛选前: {len(data)} 行")
            
            # 分别处理IVS和LLM数据
            ivs_data = data[data['data_source'] == 'IVS'].copy()
            llm_data = data[data['data_source'].isin(['llm_roleplay', 'Roleplay'])].copy()
            
            print(f"   IVS数据: {len(ivs_data)} 行, LLM数据: {len(llm_data)} 行")
            
            # IVS数据：thresh=6（允许NaN，PPCA可以处理均匀分布的4.2% NaN）
            ivs_filtered = ivs_data.dropna(subset=self.iv_qns, thresh=6)
            print(f"   IVS thresh=6后: {len(ivs_filtered)} 行")
            
            # LLM数据：必须完全回答（高度集中的NaN会导致Varimax失败）
            llm_filtered = llm_data.dropna(subset=self.iv_qns, thresh=6)
            print(f"   LLM thresh=6后: {len(llm_filtered)} 行")
            llm_filtered = llm_filtered.dropna(subset=self.iv_qns, how='any')
            print(f"   LLM完全回答后: {len(llm_filtered)} 行")
            
            # 合并
            data_filtered = pd.concat([ivs_filtered, llm_filtered], ignore_index=True)
            print(f"   合并后总数据: {len(data_filtered)} 行")
            
            # 注意：不做异常值清理，保持与参考项目一致
            
            return data_filtered
            
        except Exception as e:
            print(f"❌ 数据质量筛选失败: {e}")
            return data
    
    def combine_data(self) -> pd.DataFrame:
        """合并IVS数据和角色扮演数据 - 应用正确的数据筛选逻辑"""
        # 加载角色扮演数据
        additional_data = self.load_additional_data()
        
        if additional_data.empty:
            print("⚠️ 角色扮演数据为空，仅使用IVS数据")
            # 准备IVS数据（应用标准筛选）
            ivs_data = self.prepare_ivs_data()
            ivs_data['data_source'] = 'IVS'
            return ivs_data
        
        # 检查数据是否已经合并过（包含data_source列且有IVS和roleplay数据）
        if 'data_source' in additional_data.columns:
            data_sources = additional_data['data_source'].unique()
            if 'IVS' in data_sources and ('llm_roleplay' in data_sources or 'Roleplay' in data_sources):
                print("✅ 检测到数据已经合并过，应用数据质量筛选...")
                print(f"   筛选前数据源分布: {additional_data['data_source'].value_counts().to_dict()}")
                
                # 对合并后的数据应用质量筛选
                filtered_data = self._apply_data_quality_filters(additional_data)
                print(f"   筛选后数据源分布: {filtered_data['data_source'].value_counts().to_dict()}")
                return filtered_data
        
        try:
            # 准备IVS数据
            ivs_data = self.prepare_ivs_data()
            ivs_data['data_source'] = 'IVS'
            print(f"✅ 准备IVS数据: {len(ivs_data)} 行")
            
            # 处理角色扮演数据 - 应用相同的筛选标准
            roleplay_data_copy = additional_data.copy()
            roleplay_data_copy['data_source'] = 'Roleplay'
            
            # 关键修复：对roleplay数据应用相同的筛选逻辑
            print(f"🔄 对roleplay数据应用数据质量筛选...")
            print(f"   筛选前: {len(roleplay_data_copy)} 行")
            
            # 1. 确保有足够的IVS问题回答（至少6个）- 用于保存
            roleplay_data_copy = roleplay_data_copy.dropna(subset=self.iv_qns, thresh=6)
            print(f"   thresh=6筛选后: {len(roleplay_data_copy)} 行")
            
            # 2. PCA分析要求：LLM数据必须完全回答所有10个问题
            # 原因：LLM的NaN高度集中在某些列(E018:68%, G006:59%)，导致PPCA数值不稳定
            # 而IVS数据的NaN分布均匀(4.2%)，PPCA可以处理
            before_dropna = len(roleplay_data_copy)
            if before_dropna > 0:
                roleplay_data_copy = roleplay_data_copy.dropna(subset=self.iv_qns, how='any')
                retention_rate = len(roleplay_data_copy)/before_dropna*100 if before_dropna > 0 else 0
                print(f"   完全回答筛选后: {len(roleplay_data_copy)} 行 (保留 {retention_rate:.1f}%)")
            else:
                print(f"   ⚠️ thresh=6筛选后数据已为空，跳过完全回答筛选")
            
            # 注意：不做异常值清理，与参考项目保持一致，避免改变数据分布
            
            if len(roleplay_data_copy) == 0:
                print("⚠️ 角色扮演数据筛选后为空，仅使用IVS数据")
                return ivs_data
            
            # 高效的列对齐
            all_columns = list(set(ivs_data.columns) | set(roleplay_data_copy.columns))
            
            # 重新索引以对齐列
            ivs_aligned = ivs_data.reindex(columns=all_columns)
            roleplay_aligned = roleplay_data_copy.reindex(columns=all_columns)
            
            # 合并数据
            combined_data = pd.concat([
                ivs_aligned, 
                roleplay_aligned
            ], ignore_index=True)
            
            # 最终数据质量检查
            print(f"📊 数据合并完成:")
            print(f"   - 总计: {len(combined_data)} 行")
            print(f"   - IVS数据: {len(ivs_data)} 行")
            print(f"   - 角色扮演数据: {len(roleplay_data_copy)} 行")
            
            # 检查合并后的数据质量
            numeric_cols = [col for col in self.iv_qns if col in combined_data.columns]
            if numeric_cols:
                valid_data_per_col = combined_data[numeric_cols].notna().sum()
                print(f"   每列有效数据量: {dict(valid_data_per_col)}")
            
            return combined_data
                
        except Exception as e:
            print(f"❌ 数据合并失败: {e}")
            import traceback
            traceback.print_exc()
            return ivs_data
    
    def run_roleplay_analysis(self) -> pd.DataFrame:
        """运行完整的角色扮演PCA分析"""
        print("🚀 开始LLM国家角色扮演PCA分析...")
        
        try:
            # 使用基类的完整分析流程
            entity_scores = super().run_full_analysis()
            
            # 添加角色扮演特定的统计信息
            self._print_roleplay_statistics(entity_scores)
            
            return entity_scores
            
        except Exception as e:
            print(f"❌ 角色扮演PCA分析失败: {e}")
            raise
    
    def _print_roleplay_statistics(self, entity_scores: pd.DataFrame):
        """打印角色扮演特定的统计信息"""
        print(f"\n{'='*50}")
        print("📊 角色扮演PCA分析结果摘要")
        print(f"{'='*50}")
        
        if 'data_source' in entity_scores.columns:
            print("数据源分布:")
            source_counts = entity_scores['data_source'].value_counts()
            for source, count in source_counts.items():
                print(f"   {source}: {count} 个实体")
        
        # 角色扮演数据统计
        roleplay_data = entity_scores[entity_scores['data_source'] == 'llm_roleplay'] if 'data_source' in entity_scores.columns else pd.DataFrame()
        
        if not roleplay_data.empty:
            print(f"\n🎭 角色扮演数据统计:")
            print(f"   实体数量: {len(roleplay_data)}")
            print(f"   PC1范围: [{roleplay_data['PC1_rescaled'].min():.2f}, {roleplay_data['PC1_rescaled'].max():.2f}]")
            print(f"   PC2范围: [{roleplay_data['PC2_rescaled'].min():.2f}, {roleplay_data['PC2_rescaled'].max():.2f}]")
            
            if 'Cultural Region' in roleplay_data.columns:
                print(f"\n🌍 角色扮演文化区域分布:")
                region_counts = roleplay_data['Cultural Region'].value_counts()
                for region, count in region_counts.items():
                    if pd.notna(region):
                        print(f"   {region}: {count}")
    
    def save_results(self, entity_scores: pd.DataFrame, prefix: str = "roleplay_pca"):
        """保存PCA结果到roleplay_English目录
        
        Args:
            entity_scores: 实体分数数据
            prefix: 文件名前缀
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存PCA结果到roleplay_English目录
        if self.pca_results is not None:
            pca_path = self.roleplay_data_path / f"{prefix}_results_{timestamp}.pkl"
            self.pca_results.to_pickle(pca_path)
            print(f"💾 保存PCA结果到: {pca_path}")
        
        # 保存实体分数到roleplay_English目录
        if entity_scores is not None:
            scores_path = self.roleplay_data_path / f"{prefix}_entity_scores_{timestamp}.pkl"
            entity_scores.to_pickle(scores_path)
            print(f"💾 保存实体分数到: {scores_path}")
            
            # 同时保存一个不带时间戳的版本（用于可视化）
            scores_path_latest = self.roleplay_data_path / f"{prefix}_entity_scores_latest.pkl"
            entity_scores.to_pickle(scores_path_latest)
            print(f"💾 保存最新实体分数到: {scores_path_latest}")
        
        return entity_scores
    
    def calculate_distances(self, entity_scores: pd.DataFrame) -> pd.DataFrame:
        """计算LLM角色扮演结果与真实国家IVS数据的文化距离
        
        Args:
            entity_scores: PCA分析后的实体分数数据
            
        Returns:
            包含距离信息的DataFrame
        """
        print("\n" + "=" * 80)
        print("📏 计算文化距离：LLM角色扮演 vs 真实国家IVS数据")
        print("=" * 80)
        
        # 分离LLM角色扮演数据和真实IVS数据
        # 兼容两种data_source值: 'llm_roleplay'和'Roleplay'
        roleplay_data = entity_scores[entity_scores['data_source'].isin(['llm_roleplay', 'Roleplay'])].copy()
        ivs_data = entity_scores[entity_scores['data_source'] == 'IVS'].copy()
        
        if roleplay_data.empty:
            print("❌ 没有找到角色扮演数据")
            return pd.DataFrame()
        
        if ivs_data.empty:
            print("❌ 没有找到真实IVS数据作为基准")
            return pd.DataFrame()
        
        print(f"✅ 角色扮演数据: {len(roleplay_data)} 个实体")
        print(f"✅ 真实IVS数据: {len(ivs_data)} 个国家")
        
        # 构建真实国家的坐标字典（同时使用country_code和country_name作为key）
        real_country_coords = {}
        real_country_by_name = {}
        
        for _, row in ivs_data.iterrows():
            country_code = row.get('S003', row.get('country_code'))
            country_name = row.get('Country', '')
            coords = {
                'pc1': row['PC1_rescaled'],
                'pc2': row['PC2_rescaled'],
                'country_name': country_name
            }
            
            # 使用数字代码作为key
            if pd.notna(country_code):
                try:
                    code_str = str(int(float(country_code)))
                    real_country_coords[code_str] = coords
                except (ValueError, TypeError):
                    pass
            
            # 同时使用国家名称作为key
            if pd.notna(country_name):
                real_country_by_name[country_name] = coords
        
        print(f"📍 建立了 {len(real_country_coords)} 个真实国家的文化坐标基准")
        
        # 计算距离
        distance_results = []
        
        for _, roleplay_row in roleplay_data.iterrows():
            model_name = roleplay_row.get('model_name', roleplay_row.get('Model Name', ''))
            model_region = roleplay_row.get('model_region', roleplay_row.get('Model Region', ''))
            country_name_from_row = roleplay_row.get('country_name', roleplay_row.get('Country', ''))
            country_code_from_row = roleplay_row.get('country_code', roleplay_row.get('S003', ''))
            cultural_region = roleplay_row.get('cultural_region', roleplay_row.get('Cultural Region', ''))
            
            roleplay_pc1 = roleplay_row['PC1_rescaled']
            roleplay_pc2 = roleplay_row['PC2_rescaled']
            
            # 尝试找到对应的真实数据（先用数字代码，再用国家名称）
            real_coords = None
            match_key = None
            
            # 方法1: 尝试用数字代码匹配
            if pd.notna(country_code_from_row):
                try:
                    code_str = str(int(float(country_code_from_row)))
                    if code_str in real_country_coords:
                        real_coords = real_country_coords[code_str]
                        match_key = code_str
                except (ValueError, TypeError):
                    pass
            
            # 方法2: 如果数字代码没匹配上，尝试用国家名称匹配
            if not real_coords and pd.notna(country_code_from_row):
                # country_code可能是国家名称
                if str(country_code_from_row) in real_country_by_name:
                    real_coords = real_country_by_name[str(country_code_from_row)]
                    match_key = str(country_code_from_row)
            
            # 方法3: 用country_name字段匹配
            if not real_coords and pd.notna(country_name_from_row):
                if country_name_from_row in real_country_by_name:
                    real_coords = real_country_by_name[country_name_from_row]
                    match_key = country_name_from_row
            
            if real_coords:
                real_pc1 = real_coords['pc1']
                real_pc2 = real_coords['pc2']
                
                # 计算欧氏距离
                distance = np.sqrt(
                    (roleplay_pc1 - real_pc1)**2 + 
                    (roleplay_pc2 - real_pc2)**2
                )
                
                # 使用country_name_from_row或country_code_from_row作为显示的国家名称
                display_country_name = country_name_from_row if pd.notna(country_name_from_row) else str(country_code_from_row)
                real_country_name = real_coords['country_name']
                
                distance_results.append({
                    'model_name': model_name,
                    'model_region': model_region,
                    'roleplay_country': display_country_name,
                    'real_country': real_country_name,
                    'country_code': match_key,
                    'cultural_region': cultural_region,
                    'distance': distance,
                    'roleplay_pc1': roleplay_pc1,
                    'roleplay_pc2': roleplay_pc2,
                    'real_pc1': real_pc1,
                    'real_pc2': real_pc2
                })
        
        distance_df = pd.DataFrame(distance_results)
        
        if not distance_df.empty:
            print(f"\n✅ 计算了 {len(distance_df)} 个距离值")
            print(f"\n📊 距离统计:")
            print(f"   平均距离: {distance_df['distance'].mean():.3f}")
            print(f"   标准差: {distance_df['distance'].std():.3f}")
            print(f"   最小距离: {distance_df['distance'].min():.3f}")
            print(f"   最大距离: {distance_df['distance'].max():.3f}")
            
            # 按模型统计
            print(f"\n📊 按模型统计平均距离:")
            model_stats = distance_df.groupby('model_name')['distance'].agg(['mean', 'std', 'count'])
            for model_name, row in model_stats.iterrows():
                print(f"   {model_name}:")
                print(f"      平均距离: {row['mean']:.3f} ± {row['std']:.3f} (n={int(row['count'])})")
            
            # 按文化区域统计
            if 'cultural_region' in distance_df.columns:
                print(f"\n📊 按文化区域统计平均距离:")
                region_stats = distance_df.groupby('cultural_region')['distance'].agg(['mean', 'std', 'count'])
                for region, row in region_stats.iterrows():
                    if pd.notna(region):
                        print(f"   {region}:")
                        print(f"      平均距离: {row['mean']:.3f} ± {row['std']:.3f} (n={int(row['count'])})")
        else:
            print("❌ 没有计算出任何距离值")
        
        return distance_df
    
    def save_distances(self, distance_df: pd.DataFrame, prefix: str = "roleplay_distance"):
        """保存距离分析结果
        
        Args:
            distance_df: 距离分析结果DataFrame
            prefix: 文件名前缀
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存到roleplay_English数据目录
        data_csv_path = self.roleplay_data_path / f"{prefix}_analysis_{timestamp}.csv"
        distance_df.to_csv(data_csv_path, index=False)
        print(f"💾 保存距离分析到数据目录: {data_csv_path}")
        
        # 同时保存一个不带时间戳的版本
        data_csv_latest = self.roleplay_data_path / f"{prefix}_analysis_latest.csv"
        distance_df.to_csv(data_csv_latest, index=False)
        print(f"💾 保存最新距离分析: {data_csv_latest}")
        
        # 保存到results目录（用于报告和可视化）
        results_dir = self.data_path.parent / "results" / "roleplay_English"
        results_dir.mkdir(parents=True, exist_ok=True)
        
        results_csv_path = results_dir / f"{prefix}_analysis_{timestamp}.csv"
        distance_df.to_csv(results_csv_path, index=False)
        print(f"💾 保存距离分析到结果目录: {results_csv_path}")
        
        # 保存pkl格式（便于后续分析）
        data_pkl_path = self.roleplay_data_path / f"{prefix}_analysis_{timestamp}.pkl"
        distance_df.to_pickle(data_pkl_path)
        print(f"💾 保存距离分析PKL: {data_pkl_path}")
        
        return results_csv_path


def main():
    """主函数 - 测试新架构的角色扮演PCA分析"""
    print("🔄 使用新架构运行角色扮演PCA分析...")
    
    # 创建分析器
    analyzer = LLMCountryRoleplayPCAAnalyzer()
    
    try:
        # 运行完整分析
        entity_scores = analyzer.run_roleplay_analysis()
        
        print(f"\n✅ 新架构角色扮演PCA分析完成！")
        print(f"📊 生成了 {len(entity_scores)} 个实体的PCA分数")
        
        return entity_scores
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()
