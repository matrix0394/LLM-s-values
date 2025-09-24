import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import os
import glob
from typing import List, Tuple, Optional
from ppca import PPCA
from factor_analyzer import Rotator
import pickle

class LLMCountryRoleplayPCAAnalyzer:
    def __init__(self, data_path="../data"):
        self.data_path = data_path
        self.iv_qns = ["A008", "A165", "E018", "E025", "F063", "F118", "F120", "G006", "Y002", "Y003"]
        self.meta_col = ["S020", "S003"]
        self.weights = ["S017"]
        self.pc_rescale_params = {'PC1': (1.81, 0.38), 'PC2': (1.61, -0.01)}
        
        # 数据存储
        self.ivs_df = None
        self.country_codes = None
        self.roleplay_data = None
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
    
    def collect_roleplay_data(self) -> pd.DataFrame:
        """收集和处理角色扮演数据"""
        roleplay_path = os.path.join(self.data_path, "llm_roleplay_processed_responses.pkl")
        
        if not os.path.exists(roleplay_path):
            print(f"Warning: roleplay data not found at {roleplay_path}")
            return pd.DataFrame()
        
        try:
            df = pd.read_pickle(roleplay_path)
            print(f"Loaded roleplay data: {df.shape}")
            print(f"Roleplay data columns: {list(df.columns)}")
            if not df.empty:
                print(f"Sample data:\n{df.head(2)}")
            return df
        except Exception as e:
            print(f"Error loading roleplay data: {e}")
            return pd.DataFrame()
    
    def prepare_roleplay_metadata(self, roleplay_data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """准备角色扮演元数据"""
        if roleplay_data.empty:
            return pd.DataFrame(), pd.DataFrame()
        
        # 检查实际的列名并使用正确的列
        if 'model_name' in roleplay_data.columns and 'country_code' in roleplay_data.columns:
            # 使用 country_code 和 model_name
            unique_combinations = roleplay_data[['model_name', 'country_code']].drop_duplicates()
            model_col = 'model_name'
            country_col = 'country_code'
        else:
            print(f"Warning: Expected columns not found. Available columns: {list(roleplay_data.columns)}")
            return pd.DataFrame(), pd.DataFrame()
        
        # 为每个组合分配唯一的数字代码
        roleplay_meta = []
        roleplay_data_with_codes = roleplay_data.copy()
        
        # 从1000开始分配代码，避免与现有国家代码冲突
        start_code = 1000
        
        for idx, (_, row) in enumerate(unique_combinations.iterrows()):
            model = row[model_col]
            country = row[country_col]
            code = start_code + idx
            
            # 更新角色扮演数据中的country_code
            mask = (roleplay_data_with_codes[model_col] == model) & (roleplay_data_with_codes[country_col] == country)
            roleplay_data_with_codes.loc[mask, 'country_code'] = code
            
            # 创建元数据条目
            roleplay_meta.append({
                'Numeric': code,
                'Country': f"AI_{model}_as_{country}",
                'Alpha-3': f"AI{idx:02d}",
                'Cultural Region': 'AI_Roleplay',
                'roleplay': True
            })
        
        roleplay_meta_df = pd.DataFrame(roleplay_meta)
        return roleplay_data_with_codes, roleplay_meta_df
    
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
        """合并IVS和角色扮演数据"""
        # 准备IVS数据
        ivs_data = self.prepare_ivs_data()
        
        # 收集角色扮演数据
        roleplay_data = self.collect_roleplay_data()
        
        if roleplay_data.empty:
            print("No roleplay data available, using only IVS data")
            self.combined_data = ivs_data
            return ivs_data
        
        # 准备角色扮演元数据
        roleplay_data_with_codes, roleplay_meta = self.prepare_roleplay_metadata(roleplay_data)
        
        # 确保角色扮演数据有必要的列
        required_cols = ['country_code', 'year', 'weight'] + self.iv_qns
        for col in required_cols:
            if col not in roleplay_data_with_codes.columns:
                if col == 'year':
                    roleplay_data_with_codes[col] = 2025  # 默认年份
                elif col == 'weight':
                    roleplay_data_with_codes[col] = 1.0   # 默认权重
        
        # 选择相同的列
        roleplay_subset = roleplay_data_with_codes[required_cols]
        
        # 更新country_codes
        self.country_codes["roleplay"] = False
        self.country_codes = pd.concat([self.country_codes, roleplay_meta], ignore_index=True)
        
        # 合并数据
        self.combined_data = pd.concat([ivs_data, roleplay_subset], ignore_index=True)
        
        print(f"Combined data shape: {self.combined_data.shape}")
        print(f"Combined data columns: {list(self.combined_data.columns)}")
        
        return self.combined_data
    
    def perform_pca_analysis(self) -> pd.DataFrame:
        if self.combined_data is None:
            raise ValueError("Please combine data first")
        
        print("Starting PCA analysis...")
        
        # 数据质量检查
        data_for_pca = self.combined_data[self.iv_qns]
        
        print(f"PCA输入数据形状: {data_for_pca.shape}")
        print(f"NaN值统计: {data_for_pca.isnull().sum().sum()}")
        print(f"无穷大值统计: {np.isinf(data_for_pca.select_dtypes(include=[np.number])).sum().sum()}")
        
        # 检查方差为0的列
        numeric_data = data_for_pca.select_dtypes(include=[np.number])
        zero_var_cols = [col for col in numeric_data.columns if numeric_data[col].var() == 0]
        if zero_var_cols:
            print(f"警告：发现方差为0的列: {zero_var_cols}")
        
        # 检查数据矩阵的秩
        clean_data = data_for_pca.dropna()
        if len(clean_data) > 0:
            rank = np.linalg.matrix_rank(clean_data.select_dtypes(include=[np.number]))
            print(f"数据矩阵秩: {rank}/{clean_data.shape[1]}")
            
            if rank < min(clean_data.shape):
                print("警告：数据矩阵不满秩，可能导致SVD问题")
        
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
        ppca_df["weight"] = self.combined_data["weight"].values
        
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
        """计算实体级别的平均分数（国家和角色扮演模型）"""
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
        if 'roleplay' in entity_scores.columns:
            countries = entity_scores[entity_scores['roleplay'] == False]
            roleplays = entity_scores[entity_scores['roleplay'] == True]
            print(f"Countries: {len(countries)}, Roleplay models: {len(roleplays)}")
        
        return entity_scores
    
    def save_results(self, entity_scores: pd.DataFrame):
        """保存分析结果"""
        # 保存详细结果
        if self.pca_results is not None:
            pca_results_path = os.path.join(self.data_path, "roleplay_pca_results.pkl")
            self.pca_results.to_pickle(pca_results_path)
            print(f"Saved PCA results to {pca_results_path}")
        
        # 保存实体分数
        entity_scores_path = os.path.join(self.data_path, "roleplay_entity_scores_pca.pkl")
        entity_scores.to_pickle(entity_scores_path)
        print(f"Saved entity scores to {entity_scores_path}")
        
        # 保存更新的国家代码
        country_codes_path = os.path.join(self.data_path, "country_codes_with_roleplay.pkl")
        self.country_codes.to_pickle(country_codes_path)
        print(f"Saved updated country codes to {country_codes_path}")
    
    def run_full_analysis(self) -> pd.DataFrame:
        """运行完整的分析流程"""
        print("=== Starting Roleplay PCA Analysis ===")
        
        # 1. 加载数据
        if not self.load_data():
            raise ValueError("Failed to load required data")
        
        # 2. 合并数据
        combined_data = self.combine_data()
        
        # 3. 执行PCA分析
        pca_results = self.perform_pca_analysis()
        
        # 4. 计算实体分数（关键步骤！）
        entity_scores = self.calculate_entity_scores()
        
        # 5. 保存结果
        self.save_results(entity_scores)
        
        # 6. 输出统计信息
        self._print_summary(entity_scores)
        
        return entity_scores
    
    def _print_summary(self, entity_scores: pd.DataFrame):
        """打印分析结果摘要"""
        print("\n=== PCA Analysis Summary ===")
        print(f"Total entities: {len(entity_scores)}")
        
        if 'roleplay' in entity_scores.columns:
            countries = entity_scores[entity_scores['roleplay'] == False]
            roleplays = entity_scores[entity_scores['roleplay'] == True]
            print(f"Countries: {len(countries)}")
            print(f"Roleplay models: {len(roleplays)}")
        
        if 'PC1_rescaled' in entity_scores.columns:
            print(f"PC1 range: [{entity_scores['PC1_rescaled'].min():.2f}, {entity_scores['PC1_rescaled'].max():.2f}]")
            print(f"PC2 range: [{entity_scores['PC2_rescaled'].min():.2f}, {entity_scores['PC2_rescaled'].max():.2f}]")
        
        if 'Cultural Region' in entity_scores.columns:
            print("\nCultural Region distribution:")
            print(entity_scores['Cultural Region'].value_counts())

def main():
    """主函数"""
    try:
        analyzer = LLMCountryRoleplayPCAAnalyzer()
        entity_scores = analyzer.run_full_analysis()
        print("\nAnalysis completed successfully!")
        return entity_scores
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()