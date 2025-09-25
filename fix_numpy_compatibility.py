import sys
import numpy as np

# 创建numpy兼容性补丁
def fix_numpy_compatibility():
    """修复numpy版本兼容性问题"""
    print("=== 修复numpy版本兼容性 ===")
    
    # 检查当前numpy版本
    print(f"当前numpy版本: {np.__version__}")
    
    # 如果numpy._core.numeric不存在，创建别名
    try:
        import numpy._core.numeric
        print("numpy._core.numeric已存在，无需修复")
    except ImportError:
        print("numpy._core.numeric不存在，创建兼容性别名...")
        
        # 创建numpy._core模块的别名
        import numpy.core as _core_module
        sys.modules['numpy._core'] = _core_module
        
        # 创建numpy._core.numeric的别名
        import numpy.core.numeric as _numeric_module
        sys.modules['numpy._core.numeric'] = _numeric_module
        
        print("✅ 兼容性别名已创建")

def test_pickle_loading():
    """测试pickle文件加载"""
    import pandas as pd
    import os
    
    print("\n=== 测试pickle文件加载 ===")
    
    test_files = [
        'data/ivs_df.pkl',
        'data/country_codes.pkl',
        'data/valid_data.pkl',
        'data/country_scores_pca.pkl'
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            try:
                data = pd.read_pickle(file_path)
                print(f"✅ {file_path}: 正常加载，形状 {data.shape}")
            except Exception as e:
                print(f"❌ {file_path}: 加载失败 - {e}")
        else:
            print(f"⚠️  {file_path}: 文件不存在")

if __name__ == "__main__":
    fix_numpy_compatibility()
    test_pickle_loading()


