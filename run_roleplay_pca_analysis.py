import sys
import os
from pathlib import Path

# 将项目根目录添加到Python路径
sys.path.append(str(Path(__file__).parent))

from src.llm_country_roleplay_pca_analysis import LLMCountryRoleplayPCAAnalyzer

def main():
    """主函数，运行完整的Roleplay PCA分析"""
    print("=== 开始运行Roleplay PCA分析 ===")
    
    # 初始化分析器
    analyzer = LLMCountryRoleplayPCAAnalyzer()
    
    try:
        # 运行完整分析
        print("\n运行完整的PCA分析...")
        results = analyzer.run_full_analysis()
        
        if not results.empty:
            print(f"\n✅ PCA分析完成！")
            print(f"结果数据形状: {results.shape}")
            print(f"列名: {list(results.columns)}")
            
            # 显示基本统计
            if 'PC1_rescaled' in results.columns and 'PC2_rescaled' in results.columns:
                print(f"\nPC1范围: {results['PC1_rescaled'].min():.3f} 到 {results['PC1_rescaled'].max():.3f}")
                print(f"PC2范围: {results['PC2_rescaled'].min():.3f} 到 {results['PC2_rescaled'].max():.3f}")
            
            # 显示数据来源分布
            if 'roleplay' in results.columns:
                roleplay_count = results['roleplay'].sum()
                real_count = len(results) - roleplay_count
                print(f"\n数据分布:")
                print(f"  真实国家数据: {real_count}")
                print(f"  AI角色扮演数据: {roleplay_count}")
            elif 'model_name' in results.columns:
                print(f"\n模型分布:")
                model_counts = results['model_name'].value_counts()
                for model, count in model_counts.items():
                    print(f"  {model}: {count}")
            
            print(f"\n生成的文件:")
            print(f"  - data/llm_responses_roleplay/roleplay_entity_scores_pca.pkl")
            print(f"  - data/llm_responses_roleplay/roleplay_entity_scores_pca.csv")
            
        else:
            print("❌ PCA分析失败，没有生成结果")
            
    except Exception as e:
        print(f"❌ PCA分析过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()