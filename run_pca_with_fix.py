import sys
import numpy as np
import pandas as pd
import os
from pathlib import Path

# 全面的numpy兼容性修复
def fix_numpy_compatibility():
    """修复numpy版本兼容性问题"""
    print("=== 修复numpy版本兼容性 ===")
    
    # 检查当前numpy版本
    print(f"当前numpy版本: {np.__version__}")
    
    # 创建所有必要的别名
    try:
        import numpy.core as _core_module
        import numpy.core.numeric as _numeric_module
        import numpy.core.multiarray as _multiarray_module
        import numpy.core.umath as _umath_module
        
        # 创建别名
        sys.modules['numpy._core'] = _core_module
        sys.modules['numpy._core.numeric'] = _numeric_module
        sys.modules['numpy._core.multiarray'] = _multiarray_module
        sys.modules['numpy._core.umath'] = _umath_module
        
        print("✅ 所有numpy兼容性别名已创建")
        
    except ImportError as e:
        print(f"❌ 创建numpy别名失败: {e}")
        return False
    
    return True

# 应用修复
if not fix_numpy_compatibility():
    print("无法修复numpy兼容性，退出")
    sys.exit(1)

# 将项目根目录添加到Python路径
sys.path.append(str(Path('.').absolute()))

def run_pca_analysis():
    """运行PCA分析"""
    print("\n=== 开始PCA分析 ===")
    
    try:
        # 导入必要的模块
        from sklearn.decomposition import PCA
        from sklearn.preprocessing import StandardScaler
        from ppca import PPCA
        from factor_analyzer import Rotator
        
        print("✅ 所有模块导入成功")
        
        # 使用正确的数据路径
        data_path = 'data'
        
        # 加载数据
        ivs_df_path = os.path.join(data_path, 'ivs_df.pkl')
        ivs_df = pd.read_pickle(ivs_df_path)
        print(f'✅ 加载IVS数据: {ivs_df.shape}')
        
        # 定义列名
        meta_col = ['S003', 'S020']  # country_code, year
        weight_col = ['S017']  # weight
        iv_qns = ['A008', 'A165', 'E018', 'E025', 'F063', 'F118', 'F120', 'G006', 'Y002', 'Y003']
        
        # 选择所有需要的列
        all_columns = ['S003', 'S020', 'S017'] + iv_qns
        subset_ivs_df = ivs_df[all_columns].copy()
        
        # 重命名列
        subset_ivs_df = subset_ivs_df.rename(columns={'S020': 'year', 'S003': 'country_code', 'S017': 'weight'})
        
        # 过滤2005年及以后的数据
        subset_ivs_df = subset_ivs_df[subset_ivs_df['year'] >= 2005]
        
        # 使用完整的iv_qns列表进行dropna
        subset_ivs_df = subset_ivs_df.dropna(subset=iv_qns, thresh=6)
        
        print(f'✅ 过滤后数据: {subset_ivs_df.shape}')
        
        # 执行PCA分析
        print("开始PCA分析...")
        
        # 设置随机种子确保结果可重现
        np.random.seed(42)
        
        # 使用PPCA进行分析
        ppca = PPCA()
        ppca.fit(subset_ivs_df[iv_qns].to_numpy(), d=2, min_obs=1, verbose=True)
        
        # Transform the data
        principal_components = ppca.transform()
        
        # Apply varimax rotation to the loadings
        rotator = Rotator(method='varimax')
        rotated_components = rotator.fit_transform(principal_components)
        
        # Create new DataFrame with PPCA components
        ppca_df = pd.DataFrame(rotated_components, columns=["PC1", "PC2"])
        
        # Rescaling Principal Component Scores
        pc_rescale_params = {'PC1': (1.81, 0.38), 'PC2': (1.61, -0.01)}
        
        for pc, (scale, shift) in pc_rescale_params.items():
            ppca_df[f'{pc}_rescaled'] = ppca_df[pc] * scale + shift
        
        # 合并数据
        valid_data = pd.concat([subset_ivs_df.reset_index(drop=True), ppca_df], axis=1)
        
        print(f'✅ PCA分析完成: {valid_data.shape}')
        
        # 计算国家分数
        print("计算国家分数...")
        
        # 加载国家代码
        country_codes_path = os.path.join(data_path, 'country_codes.pkl')
        country_codes = pd.read_pickle(country_codes_path)
        
        # 计算加权平均分数
        country_scores = []
        
        for country_code in valid_data['country_code'].unique():
            country_data = valid_data[valid_data['country_code'] == country_code]
            
            # 使用权重计算加权平均
            weights = country_data['weight']
            pc1_weighted = np.average(country_data['PC1_rescaled'], weights=weights)
            pc2_weighted = np.average(country_data['PC2_rescaled'], weights=weights)
            
            # 获取国家信息
            country_info = country_codes[country_codes['Numeric'] == country_code]
            if not country_info.empty:
                country_name = country_info['Country'].iloc[0]
                cultural_region = country_info['Cultural Region'].iloc[0]
                is_islamic = country_info['Islamic'].iloc[0]
            else:
                country_name = f"Country_{country_code}"
                cultural_region = "Unknown"
                is_islamic = False
            
            country_scores.append({
                'Country': country_name,
                'country_code': country_code,
                'PC1_rescaled': pc1_weighted,
                'PC2_rescaled': pc2_weighted,
                'Cultural Region': cultural_region,
                'Islamic': is_islamic,
                'sample_size': len(country_data)
            })
        
        country_scores_df = pd.DataFrame(country_scores)
        
        print(f'✅ 国家分数计算完成: {country_scores_df.shape}')
        
        # 保存结果
        print("保存结果...")
        
        # 保存实体分数
        entity_scores_path = os.path.join(data_path, 'entity_scores_pca.pkl')
        valid_data.to_pickle(entity_scores_path)
        print(f'✅ 实体分数已保存: {entity_scores_path}')
        
        # 保存国家分数
        country_scores_path = os.path.join(data_path, 'country_scores_pca.pkl')
        country_scores_df.to_pickle(country_scores_path)
        print(f'✅ 国家分数已保存: {country_scores_path}')
        
        # 输出结果统计
        print(f"\n=== 最终结果统计 ===")
        print(f"实体分数数据形状: {valid_data.shape}")
        print(f"国家分数数据形状: {country_scores_df.shape}")
        print(f"PC1范围: [{country_scores_df['PC1_rescaled'].min():.2f}, {country_scores_df['PC1_rescaled'].max():.2f}]")
        print(f"PC2范围: [{country_scores_df['PC2_rescaled'].min():.2f}, {country_scores_df['PC2_rescaled'].max():.2f}]")
        print(f"文化区域分布:")
        print(country_scores_df['Cultural Region'].value_counts())
        
        return True
        
    except Exception as e:
        print(f"❌ PCA分析失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_pca_analysis()
    if success:
        print("\n🎉 PCA分析完成！")
    else:
        print("\n❌ PCA分析失败！")


