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
        super().__init__(data_path)
        
        # 设置roleplay专用的保存路径
        self.roleplay_data_path = Path(data_path) / "roleplay_English"
        self.roleplay_data_path.mkdir(exist_ok=True)
        
        # 初始化角色扮演数据处理器
        self.data_processor = LLMCountryRoleplayDataProcessor(data_dir=str(self.roleplay_data_path))
        self.roleplay_data = None
    
    def load_additional_data(self) -> pd.DataFrame:
        """加载角色扮演数据（优先使用最新的带时间戳文件）"""
        try:
            # 查找最新的带时间戳文件
            print("🔍 查找最新的角色扮演数据文件...")
            
            # 1. 优先查找最新版本文件
            latest_file = self.roleplay_data_path / "llm_roleplay_processed_responses_latest.pkl"
            if latest_file.exists():
                self.roleplay_data = pd.read_pickle(latest_file)
                print(f"✅ 加载最新角色扮演数据: {latest_file.name} - {self.roleplay_data.shape}")
                return self.roleplay_data
            
            # 2. 查找带时间戳的IVS格式文件（最新的）
            ivs_files = list(self.roleplay_data_path.glob("llm_roleplay_processed_responses_ivs_format_*.pkl"))
            if ivs_files:
                latest_ivs_file = max(ivs_files, key=lambda x: x.stat().st_mtime)
                self.roleplay_data = pd.read_pickle(latest_ivs_file)
                print(f"✅ 加载带时间戳的IVS格式数据: {latest_ivs_file.name} - {self.roleplay_data.shape}")
                return self.roleplay_data
            
            # 3. 查找带时间戳的原始处理文件（最新的）
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
            
            # 1. 确保有足够的IVS问题回答（至少6个）
            data_filtered = data.dropna(subset=self.iv_qns, thresh=6)
            print(f"   thresh=6筛选后: {len(data_filtered)} 行")
            
            # 2. 移除所有IVS问题都为NaN的行
            valid_ivs_mask = data_filtered[self.iv_qns].notna().any(axis=1)
            data_filtered = data_filtered[valid_ivs_mask]
            print(f"   移除全NaN行后: {len(data_filtered)} 行")
            
            # 3. 数据范围检查和异常值清理
            for col in self.iv_qns:
                if col in data_filtered.columns:
                    # 移除异常值（超出合理范围）
                    if col in ['A008', 'A165', 'E018', 'E025']:
                        # 1-4范围
                        mask = (data_filtered[col] >= 1) & (data_filtered[col] <= 4)
                        data_filtered.loc[~mask, col] = np.nan
                    elif col in ['F063', 'F118', 'F120', 'G006']:
                        # 1-10范围
                        mask = (data_filtered[col] >= 1) & (data_filtered[col] <= 10)
                        data_filtered.loc[~mask, col] = np.nan
                    elif col in ['Y002', 'Y003']:
                        # Y002: 1-3, Y003: 1-3 (修复异常值)
                        mask = (data_filtered[col] >= 1) & (data_filtered[col] <= 3)
                        data_filtered.loc[~mask, col] = np.nan
            
            # 4. 再次应用thresh=6筛选（清理异常值后）
            data_filtered = data_filtered.dropna(subset=self.iv_qns, thresh=6)
            print(f"   异常值清理后: {len(data_filtered)} 行")
            
            # 5. 最终检查：移除所有IVS问题都为NaN的行
            final_mask = data_filtered[self.iv_qns].notna().any(axis=1)
            data_filtered = data_filtered[final_mask]
            print(f"   最终有效数据: {len(data_filtered)} 行")
            
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
            # 处理角色扮演数据 - 应用相同的筛选标准
            roleplay_data_copy = additional_data.copy()
            roleplay_data_copy['data_source'] = 'Roleplay'
            
            # 关键修复：对roleplay数据应用相同的筛选逻辑
            print(f"🔄 对roleplay数据应用数据质量筛选...")
            print(f"   筛选前: {len(roleplay_data_copy)} 行")
            
            # 1. 确保有足够的IVS问题回答（至少6个）
            roleplay_data_copy = roleplay_data_copy.dropna(subset=self.iv_qns, thresh=6)
            print(f"   thresh=6筛选后: {len(roleplay_data_copy)} 行")
            
            # 2. 移除所有IVS问题都为NaN的行
            valid_ivs_mask = roleplay_data_copy[self.iv_qns].notna().any(axis=1)
            roleplay_data_copy = roleplay_data_copy[valid_ivs_mask]
            print(f"   移除全NaN行后: {len(roleplay_data_copy)} 行")
            
            # 3. 检查数据质量
            for col in self.iv_qns:
                if col in roleplay_data_copy.columns:
                    # 移除异常值（超出合理范围）
                    if col in ['A008', 'A165', 'E018', 'E025']:
                        # 1-4范围
                        mask = (roleplay_data_copy[col] >= 1) & (roleplay_data_copy[col] <= 4)
                        roleplay_data_copy.loc[~mask, col] = np.nan
                    elif col in ['F063', 'F118', 'F120', 'G006']:
                        # 1-10范围
                        mask = (roleplay_data_copy[col] >= 1) & (roleplay_data_copy[col] <= 10)
                        roleplay_data_copy.loc[~mask, col] = np.nan
                    elif col in ['Y002', 'Y003']:
                        # 特殊处理，保持原值
                        pass
            
            # 再次应用thresh=6筛选（清理异常值后）
            roleplay_data_copy = roleplay_data_copy.dropna(subset=self.iv_qns, thresh=6)
            print(f"   最终有效数据: {len(roleplay_data_copy)} 行")
            
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
        roleplay_data = entity_scores[entity_scores['data_source'] == 'Roleplay'] if 'data_source' in entity_scores.columns else pd.DataFrame()
        
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
