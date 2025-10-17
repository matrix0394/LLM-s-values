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
from src.roleplay.llm_country_roleplay_data_processor import LLMCountryRoleplayDataProcessor


class LLMCountryRoleplayPCAAnalyzer(BasePCAAnalyzer):
    """LLM国家角色扮演PCA分析器 - 继承基类，专注于角色扮演数据分析"""
    
    def __init__(self, data_path: str = "data"):
        """初始化角色扮演PCA分析器"""
        super().__init__(data_path)
        
        # 初始化角色扮演数据处理器
        self.data_processor = LLMCountryRoleplayDataProcessor(data_dir=str(self.data_path))
        self.roleplay_data = None
    
    def load_additional_data(self) -> pd.DataFrame:
        """加载角色扮演数据"""
        try:
            # 尝试加载已处理的角色扮演数据
            roleplay_paths = [
                self.data_path / "processed" / "llm_roleplay_processed_responses_ivs_format.pkl",
                self.data_path / "llm_roleplay_processed_responses_ivs_format.pkl",
                self.data_path / "llm_responses_roleplay" / "processed_responses.pkl"
            ]
            
            for roleplay_path in roleplay_paths:
                if roleplay_path.exists():
                    self.roleplay_data = pd.read_pickle(roleplay_path)
                    print(f"✅ 加载角色扮演数据: {roleplay_path} - {self.roleplay_data.shape}")
                    return self.roleplay_data
            
            print("⚠️ 未找到已处理的角色扮演数据，将使用数据处理器处理原始数据")
            print("尝试的路径:")
            for path in roleplay_paths:
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
    
    def combine_data(self) -> pd.DataFrame:
        """合并IVS数据和角色扮演数据"""
        # 加载角色扮演数据
        additional_data = self.load_additional_data()
        
        if additional_data.empty:
            print("⚠️ 角色扮演数据为空，仅使用IVS数据")
            return self.ivs_df.copy()
        
        try:
            # 确保数据类型一致
            ivs_data_copy = self.ivs_df.copy()
            roleplay_data_copy = additional_data.copy()
            
            # 添加数据源标识
            ivs_data_copy['data_source'] = 'IVS'
            roleplay_data_copy['data_source'] = 'Roleplay'
            
            # 确保两个数据集有相同的列
            common_columns = set(ivs_data_copy.columns) & set(roleplay_data_copy.columns)
            
            # 添加缺失的列
            for col in ivs_data_copy.columns:
                if col not in roleplay_data_copy.columns:
                    roleplay_data_copy[col] = np.nan
            
            for col in roleplay_data_copy.columns:
                if col not in ivs_data_copy.columns:
                    ivs_data_copy[col] = np.nan
            
            # 合并数据
            combined_data = pd.concat([
                ivs_data_copy[roleplay_data_copy.columns], 
                roleplay_data_copy
            ], ignore_index=True)
            
            print(f"📊 数据合并完成:")
            print(f"   - 总计: {len(combined_data)} 行")
            print(f"   - IVS数据: {len(ivs_data_copy)} 行")
            print(f"   - 角色扮演数据: {len(roleplay_data_copy)} 行")
            
            return combined_data
            
        except Exception as e:
            print(f"❌ 数据合并失败: {e}")
            return self.ivs_df.copy()
    
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
