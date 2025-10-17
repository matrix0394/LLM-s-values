"""
简化的LLM PCA分析器
专门处理LLM+IVS数据的联合分析
"""

import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.base.base_pca_analyzer import BasePCAAnalyzer


class SimplifiedLLMPCAAnalyzer(BasePCAAnalyzer):
    """简化的LLM PCA分析器"""
    
    def __init__(self, country_values_data_path: str = "data/country_values", llm_data_path: str = "data/llm_values"):
        """初始化LLM PCA分析器
        
        Args:
            country_values_data_path: IVS数据路径
            llm_data_path: LLM数据路径
        """
        super().__init__(country_values_data_path)
        self.llm_data_path = Path(llm_data_path)
        self.llm_data = None
    
    def load_additional_data(self) -> pd.DataFrame:
        """加载LLM数据"""
        try:
            # 尝试加载处理后的LLM数据
            llm_processed_path = self.llm_data_path / "llm_processed_responses_ivs_format.pkl"
            
            if llm_processed_path.exists():
                self.llm_data = pd.read_pickle(llm_processed_path)
                print(f"✅ 加载LLM数据: {llm_processed_path} - {self.llm_data.shape}")
                return self.llm_data
            else:
                print(f"❌ LLM数据文件不存在: {llm_processed_path}")
                return pd.DataFrame()
        
        except Exception as e:
            print(f"❌ 加载LLM数据失败: {e}")
            return pd.DataFrame()
    
    def combine_data(self) -> pd.DataFrame:
        """合并IVS和LLM数据"""
        if self.ivs_df is None:
            raise ValueError("请先加载IVS数据")
        
        # 准备IVS数据
        ivs_data = self.prepare_ivs_data()
        ivs_data['data_source'] = 'IVS'
        ivs_data['entity_type'] = 'country'
        
        print(f"📊 准备IVS数据: {len(ivs_data)} 行")
        
        # 如果有LLM数据，则合并
        if self.llm_data is not None and len(self.llm_data) > 0:
            # 准备LLM数据
            llm_data = self.prepare_llm_data()
            
            # 合并数据
            self.combined_data = pd.concat([ivs_data, llm_data], ignore_index=True)
            print(f"📊 合并后数据: {len(self.combined_data)} 行 (IVS: {len(ivs_data)}, LLM: {len(llm_data)})")
        else:
            print("⚠️ 没有LLM数据，仅使用IVS数据")
            self.combined_data = ivs_data
        
        return self.combined_data
    
    def prepare_llm_data(self) -> pd.DataFrame:
        """准备LLM数据用于PCA分析"""
        if self.llm_data is None:
            return pd.DataFrame()
        
        llm_prepared = self.llm_data.copy()
        
        # 确保必要的列存在
        if 'data_source' not in llm_prepared.columns:
            llm_prepared['data_source'] = 'LLM'
        if 'entity_type' not in llm_prepared.columns:
            llm_prepared['entity_type'] = 'llm'
        
        # 为LLM创建虚拟的country_code
        if 'country_code' not in llm_prepared.columns:
            llm_prepared['country_code'] = llm_prepared['model_code']
        
        # 确保所有IVS问题列都存在
        for question in self.iv_qns:
            if question not in llm_prepared.columns:
                llm_prepared[question] = np.nan
        
        print(f"📊 准备LLM数据: {len(llm_prepared)} 行")
        return llm_prepared
    
    def calculate_entity_scores(self, group_by: List[str] = None) -> pd.DataFrame:
        """计算实体级别的平均分数"""
        if self.pca_results is None:
            raise ValueError("请先执行PCA分析")
        
        if group_by is None:
            # 对于LLM+IVS数据，我们需要按不同的方式分组
            # IVS数据按country_code分组，LLM数据按model_name分组
            ivs_results = self.pca_results[self.pca_results['data_source'] == 'IVS']
            llm_results = self.pca_results[self.pca_results['data_source'] == 'LLM']
            
            entity_scores_list = []
            
            # 处理IVS数据（按国家分组）
            if len(ivs_results) > 0:
                ivs_scores = ivs_results.groupby(['country_code'])[
                    ['PC1_rescaled', 'PC2_rescaled']
                ].mean().reset_index()
                ivs_scores['data_source'] = 'IVS'
                ivs_scores['entity_type'] = 'country'
                entity_scores_list.append(ivs_scores)
            
            # 处理LLM数据（按模型分组）
            if len(llm_results) > 0:
                llm_scores = llm_results.groupby(['model_name'])[
                    ['PC1_rescaled', 'PC2_rescaled']
                ].mean().reset_index()
                llm_scores['data_source'] = 'LLM'
                llm_scores['entity_type'] = 'llm'
                # 为LLM添加country_code列（使用model_name）
                llm_scores['country_code'] = llm_scores['model_name']
                entity_scores_list.append(llm_scores)
            
            # 合并所有实体分数
            if entity_scores_list:
                entity_scores = pd.concat(entity_scores_list, ignore_index=True)
            else:
                entity_scores = pd.DataFrame()
        else:
            # 使用指定的分组方式
            entity_scores = self.pca_results.groupby(group_by)[
                ['PC1_rescaled', 'PC2_rescaled']
            ].mean().reset_index()
        
        # 合并国家元数据（仅对IVS数据）
        if self.country_codes is not None and len(entity_scores) > 0:
            ivs_entities = entity_scores[entity_scores['data_source'] == 'IVS'].copy()
            llm_entities = entity_scores[entity_scores['data_source'] == 'LLM'].copy()
            
            if len(ivs_entities) > 0:
                ivs_entities = ivs_entities.merge(
                    self.country_codes, 
                    left_on='country_code', 
                    right_on='Numeric', 
                    how='left'
                )
                # 删除无法匹配的国家
                ivs_entities = ivs_entities.dropna(subset=['Numeric'])
            
            # 重新合并
            entity_scores_list = []
            if len(ivs_entities) > 0:
                entity_scores_list.append(ivs_entities)
            if len(llm_entities) > 0:
                entity_scores_list.append(llm_entities)
            
            if entity_scores_list:
                entity_scores = pd.concat(entity_scores_list, ignore_index=True)
        
        print(f"📈 计算了 {len(entity_scores)} 个实体的分数")
        return entity_scores
    
    def save_results(self, entity_scores: pd.DataFrame = None, prefix: str = "llm_pca"):
        """保存分析结果"""
        # 保存PCA结果
        if self.pca_results is not None:
            pca_path = self.llm_data_path / f"{prefix}_results.pkl"
            self.pca_results.to_pickle(pca_path)
            print(f"💾 保存PCA结果到: {pca_path}")
        
        # 保存实体分数
        if entity_scores is not None:
            scores_path = self.llm_data_path / f"{prefix}_entity_scores.pkl"
            entity_scores.to_pickle(scores_path)
            print(f"💾 保存实体分数到: {scores_path}")
            
            # 同时保存JSON格式
            scores_json_path = self.llm_data_path / f"{prefix}_entity_scores.json"
            entity_scores.to_json(scores_json_path, orient='records', indent=2)
            print(f"💾 保存实体分数JSON到: {scores_json_path}")


def main():
    """主函数 - 测试LLM PCA分析器"""
    analyzer = SimplifiedLLMPCAAnalyzer()
    
    try:
        # 运行完整分析
        print("🚀 开始LLM+IVS联合PCA分析...")
        entity_scores = analyzer.run_full_analysis()
        
        print(f"✅ 分析完成！生成了 {len(entity_scores)} 个实体的分数")
        
        # 显示统计信息
        if 'data_source' in entity_scores.columns:
            print("\n数据源分布:")
            print(entity_scores['data_source'].value_counts())
        
        if 'model_name' in entity_scores.columns:
            llm_data = entity_scores[entity_scores['data_source'] == 'LLM']
            if len(llm_data) > 0:
                print("\nLLM模型分布:")
                print(llm_data['model_name'].value_counts())
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()