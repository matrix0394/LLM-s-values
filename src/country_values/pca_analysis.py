"""
核心PCA分析器 - 使用新的统一架构
替换原有的 src/core/pca_analysis.py
"""

import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.base.base_pca_analyzer import BasePCAAnalyzer


class CorePCAAnalyzer(BasePCAAnalyzer):
    """核心PCA分析器 - 专门处理IVS数据的PCA分析"""
    
    def __init__(self, data_path: str = "data/country_values"):
        """初始化核心PCA分析器
        
        Args:
            data_path: 数据路径，默认为 data/country_values（Stage0数据所在目录）
        """
        super().__init__(data_path)
    
    def load_additional_data(self) -> pd.DataFrame:
        """加载额外数据 - 对于核心分析器，不需要额外数据"""
        return pd.DataFrame()
    
    def combine_data(self) -> pd.DataFrame:
        """合并数据 - 对于核心分析器，只使用IVS数据"""
        if self.ivs_df is None:
            raise ValueError("请先加载IVS数据")
        
        # 准备IVS数据
        self.combined_data = self.prepare_ivs_data()
        self.combined_data['data_source'] = 'IVS'
        
        # 使用base的统一方法处理country_code
        self.combined_data = self.prepare_country_codes_for_merge(self.combined_data)
        
        print(f"📊 准备IVS数据: {len(self.combined_data)} 行")
        return self.combined_data
    
    def calculate_country_scores(self) -> pd.DataFrame:
        """计算国家级别的平均分数 - 保持与原有接口兼容"""
        return self.calculate_entity_scores(['country_code'])
    
    def save_results(self, entity_scores=None, prefix="core_pca"):
        """保存结果 - 保持与原有文件名兼容"""
        # 保存为原有的文件名格式
        if self.pca_results is not None:
            # 保存为 valid_data.pkl (原有格式)
            valid_data_path = self.data_path / "valid_data.pkl"
            self.pca_results.to_pickle(valid_data_path)
            print(f"💾 保存valid_data到: {valid_data_path}")
        
        if entity_scores is not None:
            # 保存为 country_scores_pca.pkl (原有格式)
            country_scores_path = self.data_path / "country_scores_pca.pkl"
            entity_scores.to_pickle(country_scores_path)
            print(f"💾 保存country_scores_pca到: {country_scores_path}")
            
            # 同时保存JSON格式
            country_scores_json = self.data_path / "country_scores_pca.json"
            entity_scores.to_json(country_scores_json, orient='records', indent=2)
            print(f"💾 保存country_scores_pca.json到: {country_scores_json}")
        
        # 【新增】保存PCA模型供其他阶段使用
        if hasattr(self, 'ppca_model') and self.ppca_model is not None:
            pca_model_path = self.data_path / "pca_model_fixed.pkl"
            self.save_pca_model(pca_model_path)
            print(f"💾 保存固定PCA模型到: {pca_model_path}")


def main():
    """主函数 - 与原有main()函数保持兼容"""
    data_path = "data/country_values"
    
    print("🔄 使用新架构运行核心PCA分析...")
    
    # 创建分析器
    analyzer = CorePCAAnalyzer(data_path=data_path)
    
    try:
        # 运行完整分析
        country_scores = analyzer.run_full_analysis()
        
        print(f"\n🎉 核心PCA分析完成！")
        print(f"📊 生成了 {len(country_scores)} 个国家的PCA分数")
        
        # 输出与原有格式兼容的统计信息
        if 'PC1_rescaled' in country_scores.columns:
            print(f"PC1范围: [{country_scores['PC1_rescaled'].min():.2f}, {country_scores['PC1_rescaled'].max():.2f}]")
        if 'PC2_rescaled' in country_scores.columns:
            print(f"PC2范围: [{country_scores['PC2_rescaled'].min():.2f}, {country_scores['PC2_rescaled'].max():.2f}]")
        if 'Cultural Region' in country_scores.columns:
            print(f"\n文化区域分布:")
            print(country_scores['Cultural Region'].value_counts())
        
        return country_scores
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        raise


if __name__ == "__main__":
    main()
