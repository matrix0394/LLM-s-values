import sys
import numpy as np
import pandas as pd
import os
from pathlib import Path

# 修复numpy兼容性问题
def fix_numpy_compatibility():
    """修复numpy版本兼容性问题"""
    try:
        import numpy._core.numeric
        print("numpy._core.numeric已存在")
    except ImportError:
        print("创建numpy兼容性别名...")
        import numpy.core as _core_module
        import numpy.core.numeric as _numeric_module
        sys.modules['numpy._core'] = _core_module
        sys.modules['numpy._core.numeric'] = _numeric_module
        print("✅ 兼容性别名已创建")

# 应用修复
fix_numpy_compatibility()

# 将项目根目录添加到Python路径
sys.path.append(str(Path(__file__).parent))

def regenerate_ivs_data():
    """重新生成IVS数据文件"""
    print("\n=== 重新生成IVS数据文件 ===")
    
    try:
        from src.data_processing import DataProcessor
        
        processor = DataProcessor()
        
        print("1. 加载IVS数据...")
        ivs_df = processor.load_ivs_data()
        
        # 保存为新的pickle文件
        output_path = "data/ivs_df_fixed.pkl"
        ivs_df.to_pickle(output_path)
        print(f"✅ 新的IVS数据已保存: {output_path}")
        
        # 测试加载
        test_data = pd.read_pickle(output_path)
        print(f"✅ 测试加载成功: {test_data.shape}")
        
        return ivs_df
        
    except Exception as e:
        print(f"❌ 重新生成IVS数据失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def regenerate_country_codes():
    """重新生成国家代码文件"""
    print("\n=== 重新生成国家代码文件 ===")
    
    try:
        from src.data_processing import DataProcessor
        
        processor = DataProcessor()
        
        print("1. 创建国家代码...")
        country_codes = processor.create_country_codes()
        
        # 保存为新的pickle文件
        output_path = "data/country_codes_fixed.pkl"
        country_codes.to_pickle(output_path)
        print(f"✅ 新的国家代码已保存: {output_path}")
        
        # 测试加载
        test_data = pd.read_pickle(output_path)
        print(f"✅ 测试加载成功: {test_data.shape}")
        
        return country_codes
        
    except Exception as e:
        print(f"❌ 重新生成国家代码失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def regenerate_valid_data():
    """重新生成有效数据文件"""
    print("\n=== 重新生成有效数据文件 ===")
    
    try:
        from src.data_processing import DataProcessor
        
        processor = DataProcessor()
        
        print("1. 加载IVS数据...")
        ivs_df = processor.load_ivs_data()
        
        print("2. 获取过滤后的数据...")
        valid_data = processor.get_filtered_data()
        
        # 保存为新的pickle文件
        output_path = "data/valid_data_fixed.pkl"
        valid_data.to_pickle(output_path)
        print(f"✅ 新的有效数据已保存: {output_path}")
        
        # 测试加载
        test_data = pd.read_pickle(output_path)
        print(f"✅ 测试加载成功: {test_data.shape}")
        
        return valid_data
        
    except Exception as e:
        print(f"❌ 重新生成有效数据失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def replace_files():
    """替换旧文件"""
    print("\n=== 替换文件 ===")
    
    replacements = {
        "data/ivs_df_fixed.pkl": "data/ivs_df.pkl",
        "data/country_codes_fixed.pkl": "data/country_codes.pkl",
        "data/valid_data_fixed.pkl": "data/valid_data.pkl"
    }
    
    for new_file, old_file in replacements.items():
        if os.path.exists(new_file):
            if os.path.exists(old_file):
                # 备份旧文件
                backup_file = old_file.replace('.pkl', '_backup.pkl')
                os.rename(old_file, backup_file)
                print(f"✅ 已备份: {old_file} -> {backup_file}")
            
            # 替换文件
            os.rename(new_file, old_file)
            print(f"✅ 已替换: {new_file} -> {old_file}")
        else:
            print(f"⚠️  {new_file} 不存在，跳过替换")

def main():
    """主函数"""
    print("=== 开始重新生成文件（带numpy兼容性修复）===")
    
    # 重新生成各个文件
    country_codes = regenerate_country_codes()
    if country_codes is None:
        print("❌ 无法继续，国家代码生成失败")
        return
    
    ivs_df = regenerate_ivs_data()
    if ivs_df is None:
        print("❌ 无法继续，IVS数据生成失败")
        return
    
    valid_data = regenerate_valid_data()
    if valid_data is None:
        print("❌ 无法继续，有效数据生成失败")
        return
    
    # 替换文件
    replace_files()
    
    print("\n🎉 文件重新生成完成！")

if __name__ == "__main__":
    main()


