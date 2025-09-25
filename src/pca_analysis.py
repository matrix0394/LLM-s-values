import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import os
from ppca import PPCA  # 改为绝对导入
from factor_analyzer import Rotator

class PCAAnalyzer:
    def __init__(self, data_path="../data"):
        self.data_path = data_path
        self.valid_data = None
        self.country_scores_pca = None
    
    def load_country_codes(self):
        """
        加载国家代码数据
        """
        try:
            country_codes_path = os.path.join(self.data_path, "country_codes.pkl")
            country_codes = pd.read_pickle(country_codes_path)
            return country_codes
        except FileNotFoundError:
            print(f"Warning: country_codes.pkl not found at {country_codes_path}")
            return None
    
    def perform_pca_analysis(self, data, iv_qns):
        """
        执行PCA分析
        完全模仿参考项目7-pca-db.ipynb的实现
        """
        print("Starting PCA analysis...")
        
        # 设置随机种子确保结果可重现
        np.random.seed(42)
        
        # 使用PPCA进行分析（完全按照参考项目）
        ppca = PPCA()
        ppca.fit(data[iv_qns].to_numpy(), d=2, min_obs=1, verbose=True)
        # Transform the data
        principal_components = ppca.transform()
        
        # Apply varimax rotation to the loadings (the principal components)
        rotator = Rotator(method='varimax')
        rotated_components = rotator.fit_transform(principal_components)
        
        # Create new Dataframe with PPCA components - 使用principal_components（与7-pca-db.ipynb一致）
        ppca_df = pd.DataFrame(rotated_components, columns=["PC1", "PC2"])
        
        # Step 5: Rescaling Principal Component Scores
        ppca_df['PC1_rescaled'] = 1.81 * ppca_df['PC1'] + 0.38
        ppca_df['PC2_rescaled'] = 1.61 * ppca_df['PC2'] - 0.01
        
        # Add country code
        ppca_df["country_code"] = data["country_code"].values
        
        # Merge with country metadata
        country_codes = self.load_country_codes()
        if country_codes is not None:
            ppca_df = ppca_df.merge(country_codes, left_on='country_code', right_on='Numeric', how='left')
        
        # Filter out countries with undefined principal component scores
        self.valid_data = ppca_df.dropna(subset=['PC1_rescaled', 'PC2_rescaled'])
        
        # Save the dataframe (模仿参考项目)
        self.valid_data.to_pickle(os.path.join(self.data_path, "valid_data.pkl"))
        
        print(f"PCA analysis completed. {len(self.valid_data)} valid observations.")
        return self.valid_data
    
    def calculate_country_scores(self):
        """
        计算国家级别的平均分数
        完全模仿参考项目的实现
        """
        if self.valid_data is None:
            raise ValueError("Please perform PCA analysis first")
        
        # 计算国家级别的平均分数
        country_mean_scores = self.valid_data.groupby('country_code')[['PC1_rescaled', 'PC2_rescaled']].mean().reset_index()
        
        # 合并国家代码和元数据（完全模仿参考项目）
        country_codes = self.load_country_codes()
        if country_codes is not None:
            # 使用参考项目的合并逻辑
            country_scores_pca = country_mean_scores.merge(country_codes, left_on='country_code', right_on='Numeric', how='left')
            # 删除无法匹配的国家
            country_scores_pca = country_scores_pca.dropna(subset=['Numeric'])
            self.country_scores_pca = country_scores_pca
        else:
            self.country_scores_pca = country_mean_scores
        
        print(f"Country scores calculated for {len(self.country_scores_pca)} countries.")
        
        return self.country_scores_pca
    
    def save_results(self):
        """
        保存分析结果
        """
        if self.valid_data is not None:
            valid_data_path = os.path.join(self.data_path, "valid_data.pkl")
            self.valid_data.to_pickle(valid_data_path)
            print(f"Saved valid_data to {valid_data_path}")
        
        if self.country_scores_pca is not None:
            country_scores_path = os.path.join(self.data_path, "country_scores_pca.pkl")
            self.country_scores_pca.to_pickle(country_scores_path)
            print(f"Saved country_scores_pca to {country_scores_path}")

def main():
    data_path = "../data"
    
    # 加载数据
    ivs_df_path = os.path.join(data_path, "ivs_df.pkl")
    ivs_df = pd.read_pickle(ivs_df_path)
    print(f"Loaded IVS data: {ivs_df.shape}")
    
    # 定义列名（完全模仿参考项目）
    meta_col = ['S003', 'S020']  # country_code, year
    weight_col = ['S017']  # weight
    # 关键修改1：使用完整的iv_qns进行过滤，不检查列是否存在
    iv_qns = ['A008', 'A165', 'E018', 'E025', 'F063', 'F118', 'F120', 'G006', 'Y002', 'Y003']
    
    # 选择所有需要的列（假设都存在）
    all_columns = ['S003', 'S020', 'S017'] + iv_qns
    subset_ivs_df = ivs_df[all_columns].copy()
    
    # 重命名列
    subset_ivs_df = subset_ivs_df.rename(columns={'S020': 'year', 'S003': 'country_code', 'S017': 'weight'})
    
    # 过滤2005年及以后的数据
    subset_ivs_df = subset_ivs_df[subset_ivs_df['year'] >= 2005]
    
    # 关键修改2：使用完整的iv_qns列表进行dropna
    subset_ivs_df = subset_ivs_df.dropna(subset=iv_qns, thresh=6)
    
    # 执行PCA分析
    analyzer = PCAAnalyzer(data_path=data_path)
    valid_data = analyzer.perform_pca_analysis(subset_ivs_df, iv_qns)  # 传递完整的iv_qns
    
    # 计算国家分数
    country_scores = analyzer.calculate_country_scores()
    
    # 保存结果
    analyzer.save_results()
    
    # 输出结果统计
    if analyzer.country_scores_pca is not None:
        print(f"\n=== 最终结果统计 ===")
        print(f"国家分数数据形状: {analyzer.country_scores_pca.shape}")
        print(f"列名: {list(analyzer.country_scores_pca.columns)}")
        if 'PC1_rescaled' in analyzer.country_scores_pca.columns:
            print(f"PC1范围: [{analyzer.country_scores_pca['PC1_rescaled'].min():.2f}, {analyzer.country_scores_pca['PC1_rescaled'].max():.2f}]")
        if 'PC2_rescaled' in analyzer.country_scores_pca.columns:
            print(f"PC2范围: [{analyzer.country_scores_pca['PC2_rescaled'].min():.2f}, {analyzer.country_scores_pca['PC2_rescaled'].max():.2f}]")
        if 'Cultural Region' in analyzer.country_scores_pca.columns:
            print(f"文化区域分布:")
            print(analyzer.country_scores_pca['Cultural Region'].value_counts())

if __name__ == "__main__":
    main()