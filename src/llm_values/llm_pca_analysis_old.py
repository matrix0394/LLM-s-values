import pandas as pd
import numpy as np
import os
from typing import List, Tuple, Optional
from ppca import PPCA
from factor_analyzer import Rotator
import pickle
from src.base.ivs_question_processor import IVSQuestionProcessor

class LLMPCAAnalyzer:
    def __init__(self, data_path="../data"):
        self.data_path = data_path
        self.iv_qns = ["A008", "A165", "E018", "E025", "F063", "F118", "F120", "G006", "Y002", "Y003"]
        self.meta_col = ["S020", "S003"]
        self.weights = ["S017"]
        self.pc_rescale_params = {'PC1': (1.81, 0.38), 'PC2': (1.61, -0.01)}
        
        # 数据存储
        self.ivs_df = None
        self.country_codes = None
        self.llm_data = None
        self.combined_data = None
        self.pca_results = None
        
    def load_data(self):
        """加载IVS数据和国家代码数据"""
        try:
            # 加载IVS数据
            ivs_path = os.path.join(self.data_path, "ivs_df.pkl")
            self.ivs_df = pd.read_pickle(ivs_path)
            print(f"Loaded IVS data: {self.ivs_df.shape}")
            
            # 加载国家代码数据
            country_codes_path = os.path.join(self.data_path, "country_codes.pkl")
            self.country_codes = pd.read_pickle(country_codes_path)
            print(f"Loaded country codes: {self.country_codes.shape}")
            
            return True
        except FileNotFoundError as e:
            print(f"Error loading data: {e}")
            return False
    
    def Y002_transform(self, ans: Tuple[int, int]) -> int:
        """Y002问题转换函数 - 使用统一处理器"""
        return IVSQuestionProcessor.process_y002(ans[0], ans[1])
    
    def Y003_transform(self, ans: List[int]) -> int:
        """Y003问题转换函数 - 使用统一处理器"""
        result = IVSQuestionProcessor.process_y003(ans)
        return result["y003_score"]
    
    def collect_llm_data(self) -> pd.DataFrame:
        """收集和处理LLM数据"""
        # 直接读取合并后的all_models_responses.pkl文件
        all_models_path = os.path.join(self.data_path, "llm_responses", "all_models_responses.pkl")
        
        if not os.path.exists(all_models_path):
            print(f"Warning: all_models_responses.pkl not found at {all_models_path}")
            return pd.DataFrame()
        
        try:
            # 读取合并后的数据
            df = pd.read_pickle(all_models_path)
            print(f"Loaded LLM data from all_models_responses.pkl: {df.shape}")
        except Exception as e:
            print(f"Error reading all_models_responses.pkl: {e}")
            return pd.DataFrame()
        
        # 按模型分组并创建数据透视表
        result = []
        for name, group in df.groupby("model_name"):
            used_indices = set()
            while True:
                row = {"llm": name}
                all_questions_answered = True
                
                for question in self.iv_qns:
                    available_responses = group[
                        (group["question_id"] == question) & 
                        (~group.index.isin(used_indices))
                    ]
                    
                    if not available_responses.empty:
                        response = available_responses.head(1)
                        row[question] = response["response"].values[0]
                        used_indices.add(response.index[0])
                    else:
                        row[question] = None
                        all_questions_answered = False
                
                result.append(row)
                if not all_questions_answered:
                    break
        
        # 创建数据透视表
        pivot_df = pd.DataFrame(result)
        pivot_df = pivot_df.dropna(thresh=6)
        
        if pivot_df.empty:
            print("No valid LLM data after processing")
            return pd.DataFrame()
        
        # 转换Y002和Y003
        try:
            # 添加数据验证
            def safe_Y002_transform(value):
                if value is None or not isinstance(value, (tuple, list)) or len(value) != 2:
                    print(f"Invalid Y002 value: {value}")
                    return np.nan  # 返回NaN而不是默认值
                return self.Y002_transform(value)
            
            def safe_Y003_transform(value):
                if value is None or not isinstance(value, (list, tuple)):
                    print(f"Invalid Y003 value: {value}")
                    return np.nan  # 返回NaN而不是默认值
                return self.Y003_transform(value)
            
            pivot_df['Y002'] = pivot_df.apply(
                lambda row: safe_Y002_transform(row["Y002"]), axis=1
            ).astype("float64")
            
            pivot_df['Y003'] = pivot_df.apply(
                lambda row: safe_Y003_transform(row["Y003"]), axis=1
            ).astype("float64")
        except Exception as e:
            print(f"Error transforming Y002/Y003: {e}")
            # 不要直接返回空DataFrame，而是继续处理其他数据
            print("Continuing with available data...")

        # 继续处理可用的数据
        
        # 添加元数据
        pivot_df["year"] = 2025
        pivot_df["weight"] = 1.0
        
        print(f"Processed LLM data: {pivot_df.shape}")
        return pivot_df
    
    def prepare_llm_metadata(self, llm_data: pd.DataFrame) -> pd.DataFrame:
        """为LLM数据准备元数据"""
        if llm_data.empty:
            return pd.DataFrame()
        
        # 创建LLM元数据
        llm_meta = pd.DataFrame(llm_data["llm"].unique(), columns=["llm"])
        
        # 分配新的数字代码
        max_country_code = self.country_codes["Numeric"].max()
        llm_meta["Numeric"] = list(range(
            max_country_code + 10, 
            max_country_code + 10 + len(llm_meta)
        ))
        
        # 合并到LLM数据
        llm_data_with_codes = llm_data.merge(
            llm_meta, left_on="llm", right_on="llm", how="left"
        )
        llm_data_with_codes = llm_data_with_codes.rename(
            columns={"Numeric": "country_code"}
        )
        
        # 准备元数据以添加到country_codes
        llm_meta["Cultural Region"] = "AI Model"
        llm_meta = llm_meta.rename(columns={"llm": "Country"})
        llm_meta["Islamic"] = False
        llm_meta["llm"] = True
        
        return llm_data_with_codes, llm_meta
    
    def prepare_ivs_data(self) -> pd.DataFrame:
        """准备IVS数据"""
        # 选择需要的列
        subset_ivs_df = self.ivs_df[self.meta_col + self.weights + self.iv_qns].copy()
        
        # 重命名列
        subset_ivs_df = subset_ivs_df.rename(columns={
            'S020': 'year', 
            'S003': 'country_code', 
            'S017': 'weight'
        })
        
        # 过滤2005年及以后的数据
        subset_ivs_df = subset_ivs_df[subset_ivs_df["year"] >= 2005]
        
        # 至少需要6个问题的答案
        subset_ivs_df = subset_ivs_df.dropna(subset=self.iv_qns, thresh=6)
        
        print(f"Prepared IVS data: {subset_ivs_df.shape}")
        return subset_ivs_df
    
    def combine_data(self) -> pd.DataFrame:
        """合并IVS和LLM数据"""
        # 准备IVS数据
        ivs_data = self.prepare_ivs_data()
        
        # 收集LLM数据
        llm_data = self.collect_llm_data()
        
        if llm_data.empty:
            print("No LLM data available, using only IVS data")
            self.combined_data = ivs_data
            return ivs_data
        
        # 准备LLM元数据
        llm_data_with_codes, llm_meta = self.prepare_llm_metadata(llm_data)
        
        # 更新country_codes
        self.country_codes["llm"] = False
        self.country_codes["Chinese LLM"] = False
        self.country_codes = pd.concat([self.country_codes, llm_meta], ignore_index=True)
        
        # 合并数据
        self.combined_data = pd.concat([ivs_data, llm_data_with_codes], ignore_index=True)
        
        print(f"Combined data shape: {self.combined_data.shape}")
        print(f"Countries: {len(ivs_data)}, LLM responses: {len(llm_data_with_codes)}")
        
        return self.combined_data
    
    def perform_pca_analysis(self) -> pd.DataFrame:
        """执行PCA分析"""
        if self.combined_data is None:
            raise ValueError("Please combine data first")
        
        print("Starting PCA analysis...")
        
        # 设置随机种子
        np.random.seed(42)
        
        # 使用PPCA进行分析
        ppca = PPCA()
        data_for_pca = self.combined_data[self.iv_qns].to_numpy()
        
        # 拟合PPCA模型
        ppca.fit(data_for_pca, d=2, min_obs=1, verbose=True)
        
        # 转换数据
        principal_components = ppca.transform()
        
        # 应用varimax旋转
        rotator = Rotator(method='varimax')
        rotated_components = rotator.fit_transform(principal_components)
        
        # 创建结果DataFrame
        ppca_df = pd.DataFrame(rotated_components, columns=["PC1", "PC2"])
        
        # 重新缩放主成分分数
        ppca_df['PC1_rescaled'] = (self.pc_rescale_params['PC1'][0] * ppca_df['PC1'] + 
                                  self.pc_rescale_params['PC1'][1])
        ppca_df['PC2_rescaled'] = (self.pc_rescale_params['PC2'][0] * ppca_df['PC2'] + 
                                  self.pc_rescale_params['PC2'][1])
        
        # 添加国家代码和年份
        ppca_df["country_code"] = self.combined_data["country_code"].values
        ppca_df["year"] = self.combined_data["year"].values
        
        # 合并国家元数据
        ppca_df = ppca_df.merge(
            self.country_codes, 
            left_on='country_code', 
            right_on='Numeric', 
            how='left'
        )
        
        # 过滤掉无效的主成分分数
        self.pca_results = ppca_df.dropna(subset=['PC1_rescaled', 'PC2_rescaled'])
        
        print(f"PCA analysis completed. {len(self.pca_results)} valid observations.")
        return self.pca_results
    
    def calculate_entity_scores(self) -> pd.DataFrame:
        """计算实体级别的平均分数（国家和LLM）"""
        if self.pca_results is None:
            raise ValueError("Please perform PCA analysis first")
        
        # 按country_code分组计算平均分数
        entity_scores = self.pca_results.groupby('country_code')[[
            'PC1_rescaled', 'PC2_rescaled'
        ]].mean().reset_index()
        
        # 合并元数据
        entity_scores = entity_scores.merge(
            self.country_codes, 
            left_on='country_code', 
            right_on='Numeric', 
            how='left'
        )
        
        # 删除无法匹配的实体
        entity_scores = entity_scores.dropna(subset=['Numeric'])
        
        print(f"Entity scores calculated for {len(entity_scores)} entities.")
        
        # 统计信息
        countries = entity_scores[entity_scores['llm'] == False]
        llms = entity_scores[entity_scores['llm'] == True]
        
        print(f"Countries: {len(countries)}, LLM models: {len(llms)}")
        
        return entity_scores
    
    def save_results(self, entity_scores: pd.DataFrame):
        """保存分析结果"""
        # 保存详细结果
        if self.pca_results is not None:
            pca_results_path = os.path.join(self.data_path, "pca_results_with_llm.pkl")
            self.pca_results.to_pickle(pca_results_path)
            print(f"Saved PCA results to {pca_results_path}")
        
        # 保存实体分数
        entity_scores_path = os.path.join(self.data_path, "entity_scores_pca.pkl")
        entity_scores.to_pickle(entity_scores_path)
        print(f"Saved entity scores to {entity_scores_path}")
        
        # 保存更新的国家代码
        country_codes_path = os.path.join(self.data_path, "country_codes_with_llm.pkl")
        self.country_codes.to_pickle(country_codes_path)
        print(f"Saved updated country codes to {country_codes_path}")
    
    def run_full_analysis(self) -> pd.DataFrame:
        """运行完整的分析流程"""
        print("=== Starting LLM PCA Analysis ===")
        
        # 1. 加载数据
        if not self.load_data():
            raise ValueError("Failed to load required data")
        
        # 2. 合并数据
        combined_data = self.combine_data()
        
        # 3. 执行PCA分析
        pca_results = self.perform_pca_analysis()
        
        # 4. 计算实体分数
        entity_scores = self.calculate_entity_scores()
        
        # 5. 保存结果
        self.save_results(entity_scores)
        
        # 6. 输出统计信息
        self._print_summary(entity_scores)
        
        return entity_scores
    
    def _print_summary(self, entity_scores: pd.DataFrame):
        """打印分析结果摘要"""
        print("\n=== Analysis Summary ===")
        print(f"Total entities: {len(entity_scores)}")
        
        if 'llm' in entity_scores.columns:
            countries = entity_scores[entity_scores['llm'] == False]
            llms = entity_scores[entity_scores['llm'] == True]
            print(f"Countries: {len(countries)}")
            print(f"LLM models: {len(llms)}")
        
        if 'PC1_rescaled' in entity_scores.columns:
            print(f"PC1 range: [{entity_scores['PC1_rescaled'].min():.2f}, {entity_scores['PC1_rescaled'].max():.2f}]")
        
        if 'PC2_rescaled' in entity_scores.columns:
            print(f"PC2 range: [{entity_scores['PC2_rescaled'].min():.2f}, {entity_scores['PC2_rescaled'].max():.2f}]")
        
        if 'Cultural Region' in entity_scores.columns:
            print("\nCultural Region distribution:")
            print(entity_scores['Cultural Region'].value_counts())

def main():
    """主函数"""
    data_path = "../data"
    
    # 创建分析器
    analyzer = LLMPCAAnalyzer(data_path=data_path)
    
    try:
        # 运行完整分析
        entity_scores = analyzer.run_full_analysis()
        
        print("\n=== Analysis completed successfully ===")
        return entity_scores
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()