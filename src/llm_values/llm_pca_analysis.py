"""
LLM PCA分析器 - 使用新的统一架构
替换原有的 src/llm_analysis/llm_pca_analysis.py
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
from src.base.ivs_question_processor import IVSQuestionProcessor


class LLMPCAAnalyzer(BasePCAAnalyzer):
    """LLM PCA分析器 - 继承基类，专注于LLM+IVS数据的联合分析"""
    
    def __init__(self, data_path: str = "data"):
        """
        初始化LLM PCA分析器
        
        Args:
            data_path: 数据根目录
        
        自动配置：
        - IVS数据从 data/country_values/ 加载（Stage0的输出）
        - LLM数据从 data/ 加载（Stage1的输出）
        """
        # 调用父类init，指定从country_values子目录加载Stage0数据
        super().__init__(data_path, ivs_data_subdir="country_values")
        self.llm_data = None
    
    def load_additional_data(self) -> pd.DataFrame:
        """
        加载LLM数据（标准路径，与Stage0一致）
        
        期望格式：data/llm_values_ivs_format.pkl
        - 每行一个模型
        - 列：country_code(model_name), year, weight, model_region, A008-G006, Y002, Y003
        - 由llm_data_processor.py生成
        """
        try:
            # Stage1专用路径：data/llm_values/
            llm_dir = self.data_path / "llm_values"
            
            # 查找最新的处理后数据文件
            import glob
            pattern = str(llm_dir / "llm_processed_responses_ivs_format_*.pkl")
            matching_files = sorted(glob.glob(pattern), reverse=True)
            
            if matching_files:
                from pathlib import Path
                llm_path = Path(matching_files[0])  # 最新的文件
                self.llm_data = pd.read_pickle(llm_path)
                print(f"✅ 加载LLM数据: {llm_path.name}")
                print(f"   - 路径: {llm_path}")
                print(f"   - 模型数量: {len(self.llm_data)}")
                print(f"   - 数据格式: IVS标准格式（与Stage0一致）")
                return self.llm_data
            else:
                print(f"⚠️ 未找到LLM数据文件")
                print(f"   查找路径: {llm_dir}")
                print(f"   期望文件: llm_processed_responses_ivs_format_*.pkl")
                print(f"   提示：请运行 llm_data_processor.py 生成数据")
                return pd.DataFrame()
        
        except Exception as e:
            print(f"❌ 加载LLM数据失败: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
        
    def _prepare_llm_data_for_pca(self, llm_data: pd.DataFrame) -> pd.DataFrame:
        """
        准备LLM数据用于PCA（数据已经是IVS标准格式）
        
        llm_data已经包含：
        - country_code (模型名称)
        - year, weight, model_region
        - A008-G006, Y002, Y003 (已处理)
        
        只需添加data_source和model_name标识
        """
        print(f"🔄 准备 {len(llm_data)} 条LLM数据用于PCA...")
        
        llm_prepared = llm_data.copy()
        
        # 添加数据源标识
        llm_prepared['data_source'] = 'LLM'
        
        # 添加Cultural Region标识（用于可视化）
        llm_prepared['Cultural Region'] = 'AI Model'
        
        # 如果没有model_name列，从country_code提取
        if 'model_name' not in llm_prepared.columns:
            llm_prepared['model_name'] = llm_prepared['country_code']
        
        # 确保country_code格式（如果需要加LLM_前缀）
        if not llm_prepared['country_code'].iloc[0].startswith('LLM_'):
            llm_prepared['country_code'] = 'LLM_' + llm_prepared['country_code'].astype(str)
        
        print(f"✅ LLM数据准备完成: {len(llm_prepared)} 行")
        print(f"   - 数据已是IVS标准格式，无需额外处理")
        print(f"   - Cultural Region已设置为 'AI Model'")
        return llm_prepared
    
    def combine_data(self) -> pd.DataFrame:
        """合并IVS数据和LLM数据（都是标准IVS格式）"""
        # 准备IVS数据
        ivs_data = self.prepare_ivs_data()
        ivs_data['data_source'] = 'IVS'
        ivs_data['model_name'] = None
        
        # 使用base的统一方法处理country_code（与Stage0一致）✅
        ivs_data = self.prepare_country_codes_for_merge(ivs_data)
        
        data_parts = [ivs_data]
        
        # 准备LLM数据（已经是IVS标准格式）
        if self.llm_data is not None and not self.llm_data.empty:
            llm_prepared = self._prepare_llm_data_for_pca(self.llm_data)
            if not llm_prepared.empty:
                # LLM数据也进行标准化处理（保持一致性）
                llm_prepared = self.prepare_country_codes_for_merge(llm_prepared)
                data_parts.append(llm_prepared)
        
        # 合并数据
        self.combined_data = pd.concat(data_parts, ignore_index=True)
        
        print(f"📊 数据合并完成:")
        print(f"   - 总计: {len(self.combined_data)} 行")
        print(f"   - IVS数据: {len(ivs_data)} 行")
        if len(data_parts) > 1:
            llm_count = len(self.combined_data[self.combined_data['data_source'] == 'LLM'])
            print(f"   - LLM数据: {llm_count} 行")
        
        return self.combined_data
    
    def calculate_entity_scores(self, group_by=None) -> pd.DataFrame:
        """计算实体分数 - 支持LLM和国家的分组"""
        if group_by is None:
            # 按数据源和标识符分组
            group_by = ['country_code', 'data_source']
        
        entity_scores = super().calculate_entity_scores(group_by)
        
        # 添加有用的标识列
        entity_scores['is_llm'] = entity_scores['data_source'] == 'LLM'
        
        # 为LLM添加模型信息
        if 'is_llm' in entity_scores.columns:
            llm_rows = entity_scores['is_llm'] == True
            if llm_rows.any():
                # 从country_code中提取模型名称
                entity_scores.loc[llm_rows, 'extracted_model'] = entity_scores.loc[llm_rows, 'country_code'].str.replace('LLM_', '')
        
        return entity_scores
    
    def save_results(self, entity_scores=None, prefix="llm_pca"):
        """保存结果 - 保存到Stage1专用的data/llm_values/子目录"""
        # Stage1专用保存目录
        llm_data_dir = self.data_path / "llm_values"
        llm_data_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存PCA结果到Stage1目录
        if self.pca_results is not None:
            pca_path = llm_data_dir / f"{prefix}_results.pkl"
            self.pca_results.to_pickle(pca_path)
            print(f"💾 保存PCA结果到: {pca_path}")
        
        # 保存实体分数到Stage1目录
        if entity_scores is not None:
            scores_path = llm_data_dir / f"{prefix}_entity_scores.pkl"
            entity_scores.to_pickle(scores_path)
            print(f"💾 保存实体分数到: {scores_path}")
            
            # JSON格式（也保存到Stage1目录）
            scores_json = llm_data_dir / f"{prefix}_entity_scores.json"
            entity_scores.to_json(scores_json, orient='records', indent=2)
            print(f"💾 保存JSON格式到: {scores_json}")
    
    def print_summary(self, entity_scores=None):
        """打印分析结果摘要 - 增强LLM相关信息"""
        super().print_summary(entity_scores)
        
        if entity_scores is not None and 'is_llm' in entity_scores.columns:
            print("\n🤖 LLM vs 国家统计:")
            llm_count = entity_scores['is_llm'].sum()
            country_count = (~entity_scores['is_llm']).sum()
            print(f"   - LLM模型: {llm_count} 个")
            print(f"   - 国家: {country_count} 个")
            
            if llm_count > 0:
                llm_data = entity_scores[entity_scores['is_llm'] == True]
                print(f"\n🎯 LLM PC分数范围:")
                print(f"   - PC1: [{llm_data['PC1_rescaled'].min():.2f}, {llm_data['PC1_rescaled'].max():.2f}]")
                print(f"   - PC2: [{llm_data['PC2_rescaled'].min():.2f}, {llm_data['PC2_rescaled'].max():.2f}]")


def main():
    """主函数 - 运行LLM PCA分析"""
    data_path = "data"
    
    print("🔄 使用新架构运行LLM PCA分析...")
    
    # 创建分析器
    analyzer = LLMPCAAnalyzer(data_path=data_path)
    
    try:
        # 运行完整分析
        entity_scores = analyzer.run_full_analysis()
        
        print(f"\n🎉 LLM PCA分析完成！")
        print(f"📊 生成了 {len(entity_scores)} 个实体的PCA分数")
        
        return entity_scores
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
