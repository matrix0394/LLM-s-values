"""
LLM PCA分析器 
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

    EXPECTED_REFERENCE_COUNTRIES = 112
    EXPECTED_RESCALE_PARAMS = {
        'PC1': (1.81, 0.38),
        'PC2': (1.61, -0.01),
    }
    
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
            llm_dir = self.data_path / "llm_interviews" / "intrinsic"
            
            import glob
            pattern = str(llm_dir / "llm_processed_responses_ivs_format_*.pkl")
            matching_files = sorted(glob.glob(pattern), reverse=True)
            
            if matching_files:
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
        
        # 确俜ountry_code格式（添加LLM_前缀）
        llm_prepared['country_code'] = llm_prepared['country_code'].apply(
            lambda x: x if str(x).startswith('LLM_') else f'LLM_{x}'
        )
        
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
        
        return self._add_llm_identity_columns(entity_scores)

    def _add_llm_identity_columns(self, entity_scores: pd.DataFrame) -> pd.DataFrame:
        """Add stable model/language labels to aggregated LLM rows."""
        entity_scores = entity_scores.copy()
        entity_scores['is_llm'] = entity_scores['data_source'] == 'LLM'
        
        # 为LLM添加模型和语言信息。country_code 对每个多语言实体都是唯一的，
        # 例如 llm_google_gemma-3-4b-it_zh-cn。
        if 'is_llm' in entity_scores.columns:
            llm_rows = entity_scores['is_llm'] == True
            if llm_rows.any():
                llm_codes = entity_scores.loc[llm_rows, 'country_code'].astype(str)

                def extract_language(code: str) -> str:
                    for language in ['zh-cn', 'en', 'fr', 'es', 'ru', 'ar']:
                        if code.endswith(f'_{language}'):
                            return language
                    return 'en'

                def extract_model(code: str) -> str:
                    model = code[4:] if code.lower().startswith('llm_') else code
                    language = extract_language(code)
                    suffix = f'_{language}'
                    return model[:-len(suffix)] if model.endswith(suffix) else model

                entity_scores.loc[llm_rows, 'language'] = llm_codes.map(extract_language)

                if 'model_name' in entity_scores.columns:
                    entity_scores.loc[llm_rows, 'extracted_model'] = entity_scores.loc[
                        llm_rows, 'model_name'
                    ].fillna(llm_codes.map(extract_model))
                else:
                    entity_scores.loc[llm_rows, 'extracted_model'] = llm_codes.map(extract_model)

        return entity_scores
    
    def save_results(self, entity_scores=None, prefix="llm_pca"):
        """保存结果 - 保存到 data/llm_pca/intrinsic/ 目录"""
        output_dir = self.data_path / "llm_pca" / "intrinsic"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if self.pca_results is not None:
            pca_path = output_dir / f"{prefix}_results.pkl"
            self.pca_results.to_pickle(pca_path)
            print(f"💾 保存PCA结果到: {pca_path}")
        
        if entity_scores is not None:
            scores_path = output_dir / f"{prefix}_entity_scores.pkl"
            entity_scores.to_pickle(scores_path)
            print(f"💾 保存实体分数到: {scores_path}")
            
            scores_json = output_dir / f"{prefix}_entity_scores.json"
            entity_scores.to_json(scores_json, orient='records', indent=2)
            print(f"💾 保存JSON格式到: {scores_json}")

    def _validate_fixed_pca_model(self, pca_model: Dict[str, Any]) -> None:
        """Validate that the frozen model is the paper-compatible PPCA model."""
        required_keys = {
            'ppca_C', 'ppca_means', 'ppca_stds', 'rotation_matrix',
            'pc_rescale_params', 'question_ids',
        }
        missing = sorted(required_keys.difference(pca_model))
        if missing:
            raise ValueError(f"固定PCA模型缺少字段: {', '.join(missing)}")

        if list(pca_model['question_ids']) != self.iv_qns:
            raise ValueError("固定PCA模型的问题顺序与当前10题配置不一致")

        for component, expected in self.EXPECTED_RESCALE_PARAMS.items():
            actual = tuple(pca_model['pc_rescale_params'].get(component, ()))
            if len(actual) != 2 or not np.allclose(actual, expected):
                raise ValueError(
                    f"固定PCA模型的{component}缩放参数不一致: "
                    f"期望{expected}, 实际{actual}"
                )

    def _load_reference_country_scores(self) -> pd.DataFrame:
        """Load the lightweight, frozen 112-country paper reference table."""
        reference_path = self.data_path / "country_values" / "country_scores_pca.json"
        if not reference_path.exists():
            raise FileNotFoundError(f"正式国家坐标不存在: {reference_path}")

        country_scores = pd.read_json(reference_path)
        required_columns = {
            'country_code', 'data_source', 'PC1_rescaled', 'PC2_rescaled',
            'Cultural Region', 'Country',
        }
        missing = sorted(required_columns.difference(country_scores.columns))
        if missing:
            raise ValueError(f"正式国家坐标缺少字段: {', '.join(missing)}")

        country_count = country_scores['Country'].dropna().nunique()
        if country_count != self.EXPECTED_REFERENCE_COUNTRIES:
            raise ValueError(
                f"正式国家坐标应包含{self.EXPECTED_REFERENCE_COUNTRIES}个国家/地区，"
                f"当前为{country_count}个。请恢复交接包中的country_scores_pca.json"
            )

        country_scores = country_scores.copy()
        country_scores['data_source'] = 'IVS'
        country_scores['is_llm'] = False
        print(f"✅ 加载正式国家坐标: {reference_path}")
        print(f"   - 国家/地区数量: {country_count}")
        return country_scores
    
    def run_analysis_with_fixed_pca(self) -> pd.DataFrame:
        """使用固定的PCA模型运行分析（推荐方法）
        
        这个方法使用Stage0训练的PCA模型来转换Stage1的数据，
        确保所有坐标都在同一个坐标系中，使得距离计算有意义。
        
        Returns:
            实体分数DataFrame
        """
        print("\n" + "="*60)
        print("🔄 使用固定PCA模型进行Stage1分析（与Stage0坐标系一致）")
        print("="*60)
        
        # 1. 加载并校验交接包中的固定PCA模型和112国坐标。
        pca_model_path = self.data_path / 'country_values' / 'pca_model_fixed.pkl'
        if not pca_model_path.exists():
            raise FileNotFoundError(
                f"固定PCA模型不存在: {pca_model_path}\n"
                "请恢复交接包中的data/country_values/pca_model_fixed.pkl"
            )
        
        pca_model = self.load_pca_model(pca_model_path)
        self._validate_fixed_pca_model(pca_model)
        country_scores = self._load_reference_country_scores()
        
        # 2. 加载LLM数据
        print("\n📊 加载LLM数据...")
        llm_data = self.load_additional_data()
        if llm_data.empty:
            raise ValueError("LLM数据为空")
        
        llm_prepared = self._prepare_llm_data_for_pca(llm_data)
        print(f"   LLM数据: {len(llm_prepared)} 行")
        
        # 3. 只投影LLM。国家基准直接使用交接包中的固定坐标，避免本地
        # ivs_df.pkl来源不一致时污染论文基准。
        print("\n🔄 对LLM数据应用固定PCA...")
        llm_pca = self.transform_with_fixed_pca(llm_prepared, pca_model)
        llm_pca = self._add_metadata_to_pca_results(llm_pca, llm_prepared)
        llm_pca['data_source'] = 'LLM'
        llm_pca['Cultural Region'] = 'AI Model'

        # 4. 计算LLM实体分数。固定模式下输入已经是每个模型-语言一条记录，
        # 直接聚合即可，无需把AI实体送入国家代码匹配逻辑。
        self.pca_results = llm_pca
        print("\n📊 计算实体分数...")
        group_columns = [
            column for column in ['country_code', 'data_source', 'model_name', 'language']
            if column in self.pca_results.columns
        ]
        aggregations = {
            'PC1_rescaled': 'mean',
            'PC2_rescaled': 'mean',
            'Cultural Region': 'first',
        }
        llm_entity_scores = (
            self.pca_results
            .groupby(group_columns, dropna=False)
            .agg(aggregations)
            .reset_index()
        )
        llm_entity_scores = self._add_llm_identity_columns(llm_entity_scores)
        print(f"✅ LLM实体聚合完成: {len(llm_entity_scores)} 条记录")

        # 5. 拼接固定的112国坐标，形成可视化和论文分析统一输入。
        entity_scores = pd.concat(
            [country_scores, llm_entity_scores],
            ignore_index=True,
            sort=False,
        )
        print(f"✅ 合并正式基准: {len(country_scores)}个国家/地区 + "
              f"{len(llm_entity_scores)}条LLM记录 = {len(entity_scores)}个实体")

        # 6. 保存结果
        self.save_results(entity_scores)

        # 7. 打印摘要
        self.print_summary(entity_scores)
        
        return entity_scores
    
    def run_llm_analysis_for_runner(self, use_fixed_pca: bool = True) -> pd.DataFrame:
        """为run脚本运行LLM分析，返回实体分数DataFrame
        
        Args:
            use_fixed_pca: 是否使用固定的PCA模型（Stage0的模型），默认True
        """
        print("🚀 开始LLM价值观PCA分析...")
        
        if use_fixed_pca:
            # 【新方法】使用固定的PCA模型，确保坐标系一致
            entity_scores = self.run_analysis_with_fixed_pca()
        else:
            # 【旧方法】重新拟合PCA（不推荐，会导致坐标系变化）
            print("⚠️ 警告：使用重新拟合PCA模式，坐标系可能与Stage0不一致")
            entity_scores = super().run_full_analysis()
        
        print(f"✅ LLM PCA分析完成: {len(entity_scores)} 个实体")
        return entity_scores
    
    def print_summary(self, entity_scores=None):
        """打印分析结果摘要 - 增强LLM相关信息"""
        super().print_summary(entity_scores)
        
        if entity_scores is not None and 'is_llm' in entity_scores.columns:
            print("\n🤖 LLM vs 国家统计:")
            llm_count = entity_scores['is_llm'].sum()
            country_count = (~entity_scores['is_llm']).sum()
            print(f"   - LLM记录: {llm_count} 条")
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
        # 使用固定PCA模型运行分析（推荐，与Stage0坐标系一致）
        entity_scores = analyzer.run_llm_analysis_for_runner(use_fixed_pca=True)
        
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
