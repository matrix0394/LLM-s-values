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
        """初始化LLM PCA分析器"""
        super().__init__(data_path)
        self.llm_data = None
    
    def load_additional_data(self) -> pd.DataFrame:
        """加载LLM数据"""
        try:
            # 尝试多个可能的LLM数据路径
            llm_paths = [
                self.data_path / "llm_responses" / "all_models_responses.pkl",
                self.data_path / "processed" / "llm_processed_responses_ivs_format.pkl", 
                self.data_path / "models" / "llm_processed_responses.pkl",
                self.data_path / "archive" / "backup_numpy_problem_files" / "llm_processed_responses_ivs_format.pkl"
            ]
            
            for llm_path in llm_paths:
                if llm_path.exists():
                    self.llm_data = pd.read_pickle(llm_path)
                    print(f"✅ 加载LLM数据: {llm_path} - {self.llm_data.shape}")
                    return self.llm_data
            
            print("⚠️ 未找到LLM数据文件，将仅使用IVS数据")
            print("尝试的路径:")
            for path in llm_paths:
                print(f"  - {path}")
            return pd.DataFrame()
        
        except Exception as e:
            print(f"❌ 加载LLM数据失败: {e}")
            return pd.DataFrame()
        
    def _process_llm_responses(self, llm_data: pd.DataFrame) -> pd.DataFrame:
        """处理LLM回答数据，转换为PCA可用格式"""
        processed_data = []
        
        print(f"🔄 处理 {len(llm_data)} 条LLM数据...")
        
        for idx, row in llm_data.iterrows():
            # 获取模型名称
            model_name = row.get('model_name', row.get('model', f'model_{idx}'))
            
            processed_row = {
                'country_code': f"LLM_{model_name}",  # 为LLM创建虚拟国家代码
                'year': 2024,  # LLM数据使用2024年
                'data_source': 'LLM',
                'model_name': model_name,
                'weight': 1.0  # LLM数据权重设为1
            }
            
            # 处理每个IVS问题
            for question_id in self.iv_qns:
                response = row.get(question_id)
                
                try:
                    if question_id == 'Y002':
                        if isinstance(response, (list, tuple)) and len(response) == 2:
                            # Y002使用物质主义倾向值
                            processed_row[question_id] = IVSQuestionProcessor.process_y002(response[0], response[1])
                        else:
                            processed_row[question_id] = None
                            
                    elif question_id == 'Y003':
                        if isinstance(response, (list, tuple)) and len(response) > 0:
                            # Y003使用传统vs世俗理性分数
                            result = IVSQuestionProcessor.process_y003(list(response))
                            processed_row[question_id] = result["y003_score"]
                        else:
                            processed_row[question_id] = None
                            
                    elif isinstance(response, (int, float)):
                        # 单选题直接使用
                        processed_row[question_id] = float(response)
                    else:
                        # 无效回答设为NaN
                        processed_row[question_id] = None
                        
                except Exception as e:
                    print(f"⚠️ 处理 {model_name} 的 {question_id} 问题时出错: {e}")
                    processed_row[question_id] = None
            
            processed_data.append(processed_row)
        
        result_df = pd.DataFrame(processed_data)
        print(f"✅ LLM数据处理完成: {len(result_df)} 行")
        return result_df
    
    def combine_data(self) -> pd.DataFrame:
        """合并IVS数据和LLM数据"""
        # 准备IVS数据
        ivs_data = self.prepare_ivs_data()
        ivs_data['data_source'] = 'IVS'
        ivs_data['model_name'] = None
        ivs_data['country_code'] = ivs_data['country_code'].astype(str)  # 确保为字符串类型
        
        data_parts = [ivs_data]
        
        # 处理LLM数据
        if self.llm_data is not None and not self.llm_data.empty:
            llm_processed = self._process_llm_responses(self.llm_data)
            if not llm_processed.empty:
                data_parts.append(llm_processed)
        
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
        """保存结果 - 使用LLM特定的文件名"""
        # 保存PCA结果
        if self.pca_results is not None:
            pca_path = self.data_path / f"{prefix}_results.pkl"
            self.pca_results.to_pickle(pca_path)
            print(f"💾 保存PCA结果到: {pca_path}")
            
            # 同时保存为原有格式以保持兼容性
            if prefix == "llm_pca":
                legacy_path = self.data_path / "pca_results_with_llm.pkl"
                self.pca_results.to_pickle(legacy_path)
                print(f"💾 保存兼容格式到: {legacy_path}")
        
        # 保存实体分数
        if entity_scores is not None:
            scores_path = self.data_path / f"{prefix}_entity_scores.pkl"
            entity_scores.to_pickle(scores_path)
            print(f"💾 保存实体分数到: {scores_path}")
            
            # JSON格式
            scores_json = self.data_path / f"{prefix}_entity_scores.json"
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
