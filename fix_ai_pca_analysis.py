import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
import json

# 将项目根目录添加到Python路径
sys.path.append(str(Path(__file__).parent))

def load_ai_roleplay_data():
    """从JSON文件加载AI角色扮演数据"""
    print("=== 加载AI角色扮演数据 ===")
    
    all_data = []
    roleplay_dir = Path("data/llm_responses_roleplay")
    
    # 遍历所有模型目录
    for model_dir in roleplay_dir.iterdir():
        if model_dir.is_dir() and not model_dir.name.startswith('.'):
            model_name = model_dir.name.replace('_', '/')
            print(f"处理模型: {model_name}")
            
            # 遍历该模型的所有国家文件
            for country_file in model_dir.glob("*.json"):
                country_name = country_file.stem.replace('_', ' ')
                
                try:
                    with open(country_file, 'r', encoding='utf-8') as f:
                        responses = json.load(f)
                    
                    # 创建基础记录
                    record = {
                        'model_name': model_name,
                        'country_name': country_name,
                        'cultural_region': 'AI Roleplay',
                        'roleplay': True
                    }
                    
                    # 处理回答
                    for response in responses:
                        if response and isinstance(response, dict):
                            question_id = response.get('question_id', '')
                            response_value = response.get('response')
                            if question_id and response_value is not None:
                                # 转换数据类型：字符串"None"转为None，其他转为数值
                                if response_value == "None" or response_value == "null":
                                    record[question_id] = None
                                else:
                                    try:
                                        # 尝试转换为数值
                                        if isinstance(response_value, str):
                                            # 清理字符串：移除方括号等特殊字符
                                            cleaned_value = response_value.strip('[](){}')
                                            record[question_id] = float(cleaned_value)
                                        else:
                                            record[question_id] = response_value
                                    except (ValueError, TypeError):
                                        # 如果转换失败，设为None
                                        record[question_id] = None
                    
                    all_data.append(record)
                    
                except Exception as e:
                    print(f"  错误处理 {country_file}: {e}")
    
    df = pd.DataFrame(all_data)
    print(f"✅ 加载了 {len(df)} 条AI角色扮演数据")
    return df

def perform_correct_pca_analysis(df):
    """使用与真实国家数据相同的PCA方法进行分析"""
    print("\n=== 使用正确的PCA方法进行分析 ===")
    
    if df.empty:
        print("❌ 没有数据可供分析")
        return None
    
    print(f"数据形状: {df.shape}")
    
    # 定义IVS问题
    ivs_questions = ['A008', 'A165', 'E018', 'E025', 'F063', 'F118', 'F120', 'G006', 'Y002', 'Y003']
    
    # 检查哪些问题在数据中
    available_questions = [q for q in ivs_questions if q in df.columns]
    print(f"可用的IVS问题: {available_questions}")
    
    if not available_questions:
        print("❌ 没有找到IVS问题数据")
        return None
    
    # 提取数值数据
    numeric_data = df[available_questions].copy()
    
    # 处理缺失值 - 不填充，只报告
    print(f"缺失值统计:")
    for col in available_questions:
        missing = numeric_data[col].isnull().sum()
        print(f"  {col}: {missing}/{len(numeric_data)} ({missing/len(numeric_data)*100:.1f}%)")
    
    # 使用与真实数据相同的规则：6个以上问题有回答就算有效
    print(f"使用与真实数据相同的规则：6个以上问题有回答就算有效")
    
    # 计算每行有效回答的数量
    valid_counts = numeric_data.count(axis=1)
    valid_data_mask = valid_counts >= 6
    
    print(f"有效数据行数: {valid_data_mask.sum()}")
    print(f"有效数据比例: {valid_data_mask.sum()}/{len(numeric_data)} ({valid_data_mask.sum()/len(numeric_data)*100:.1f}%)")
    
    if valid_data_mask.sum() < 2:
        print("❌ 有效数据太少，无法进行PCA分析")
        return None
    
    # 使用有效数据
    complete_data = numeric_data[valid_data_mask]
    
    # 执行PCA - 使用与真实数据相同的方法
    try:
        from ppca import PPCA
        from factor_analyzer import Rotator
        
        print("使用PPCA进行分析...")
        
        # 设置随机种子确保结果可重现
        np.random.seed(42)
        
        # 使用PPCA进行分析（与真实数据相同）
        ppca = PPCA()
        ppca.fit(complete_data.to_numpy(), d=2, min_obs=1, verbose=True)
        
        # Transform the data
        principal_components = ppca.transform()
        
        # Apply varimax rotation to the loadings
        rotator = Rotator(method='varimax')
        rotated_components = rotator.fit_transform(principal_components)
        
        print(f"✅ PPCA分析完成")
        
        # 创建结果DataFrame
        result_df = df.loc[complete_data.index].copy()
        result_df['PC1'] = rotated_components[:, 0]
        result_df['PC2'] = rotated_components[:, 1]
        
        # 重新缩放PC分数（使用与真实数据相同的缩放参数）
        result_df['PC1_rescaled'] = 1.81 * result_df['PC1'] + 0.38
        result_df['PC2_rescaled'] = 1.61 * result_df['PC2'] - 0.01
        
        print(f"PC1范围: {result_df['PC1_rescaled'].min():.3f} 到 {result_df['PC1_rescaled'].max():.3f}")
        print(f"PC2范围: {result_df['PC2_rescaled'].min():.3f} 到 {result_df['PC2_rescaled'].max():.3f}")
        
        return result_df
        
    except ImportError as e:
        print(f"❌ 缺少必要的库: {e}")
        return None
    except Exception as e:
        print(f"❌ PCA分析失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """主函数"""
    print("=== 修复AI角色扮演数据的PCA分析 ===")
    
    try:
        # 1. 加载AI角色扮演数据
        ai_data = load_ai_roleplay_data()
        
        if ai_data.empty:
            print("❌ 没有AI角色扮演数据")
            return
        
        # 2. 执行正确的PCA分析
        result_df = perform_correct_pca_analysis(ai_data)
        
        if result_df is not None:
            # 3. 保存结果
            print("\n=== 保存结果 ===")
            output_path = "data/llm_responses_roleplay/corrected_pca_results.pkl"
            result_df.to_pickle(output_path)
            print(f"✅ 修正后的PCA结果已保存到: {output_path}")
            
            # 4. 显示结果摘要
            print(f"\n=== 修正后的分析结果摘要 ===")
            print(f"总记录数: {len(result_df)}")
            print(f"模型数: {result_df['model_name'].nunique()}")
            print(f"国家数: {result_df['country_name'].nunique()}")
            print(f"PC1范围: {result_df['PC1_rescaled'].min():.3f} 到 {result_df['PC1_rescaled'].max():.3f}")
            print(f"PC2范围: {result_df['PC2_rescaled'].min():.3f} 到 {result_df['PC2_rescaled'].max():.3f}")
            
            print(f"\n模型分布:")
            for model in result_df['model_name'].unique():
                model_data = result_df[result_df['model_name'] == model]
                pc1_range = model_data['PC1_rescaled'].max() - model_data['PC1_rescaled'].min()
                pc2_range = model_data['PC2_rescaled'].max() - model_data['PC2_rescaled'].min()
                print(f"  {model}: {len(model_data)}个国家, PC1范围={pc1_range:.3f}, PC2范围={pc2_range:.3f}")
            
            print(f"\n🎉 AI角色扮演数据PCA分析修正完成！")
            print(f"现在PC坐标范围应该与真实国家数据一致（约-5到5之间）")
            
        else:
            print("❌ PCA分析失败")
            
    except Exception as e:
        print(f"❌ 修正过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
