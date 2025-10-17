#!/usr/bin/env python3
"""
简化的PCA分析，直接使用roleplay数据
"""

import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path

# 添加src目录到路径
sys.path.append('src')

def load_roleplay_data():
    """加载roleplay数据"""
    try:
        # 尝试加载我们刚才生成的pkl文件
        pkl_path = "data/llm_responses_roleplay/llm_roleplay_processed_responses.pkl"
        if os.path.exists(pkl_path):
            df = pd.read_pickle(pkl_path)
            print(f"✅ 从pkl文件加载了 {len(df)} 条记录")
            return df
    except Exception as e:
        print(f"❌ 无法加载pkl文件: {e}")
    
    # 如果pkl失败，尝试从JSON加载
    try:
        import json
        json_path = "data/llm_responses_roleplay/roleplay_results.json"
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 处理results数组
            results = data.get('results', [])
            processed_records = []
            
            for record in results:
                model = record.get('model', '')
                country = record.get('country', '')
                responses = record.get('responses', [])
                
                # 创建基础记录
                processed_record = {
                    'model_name': model,
                    'country_name': country,
                    'cultural_region': 'AI Roleplay',
                    'roleplay': True
                }
                
                # 处理回答 - responses是LLMResponse对象的字符串表示
                for response_str in responses:
                    if response_str and isinstance(response_str, str):
                        # 解析LLMResponse字符串
                        try:
                            # 提取question_id和response值
                            import re
                            question_match = re.search(r"question_id='([^']+)'", response_str)
                            response_match = re.search(r"response=([^,)]+)", response_str)
                            is_valid_match = re.search(r"is_valid=([^,)]+)", response_str)
                            
                            if question_match and response_match and is_valid_match:
                                question_id = question_match.group(1)
                                response_value = response_match.group(1)
                                is_valid = is_valid_match.group(1) == 'True'
                                
                                # 只处理有效的回答
                                if is_valid and response_value != 'None':
                                    try:
                                        # 清理和转换响应值
                                        response_value = response_value.strip()
                                        
                                        # 处理Y002和Y003的多选回答（如"[1, 3]"或"1 3"）
                                        if question_id in ['Y002', 'Y003']:
                                            # 提取数字并计算平均值
                                            import re
                                            numbers = re.findall(r'\d+', response_value)
                                            if numbers:
                                                # 对于多选，使用第一个数字作为代表值
                                                processed_record[question_id] = int(numbers[0])
                                            else:
                                                continue
                                        else:
                                            # 单选问题
                                            if response_value.isdigit():
                                                processed_record[question_id] = int(response_value)
                                            else:
                                                # 尝试提取第一个数字
                                                numbers = re.findall(r'\d+', response_value)
                                                if numbers:
                                                    processed_record[question_id] = int(numbers[0])
                                                else:
                                                    continue
                                    except:
                                        continue
                        except Exception as e:
                            continue
                
                processed_records.append(processed_record)
            
            df = pd.DataFrame(processed_records)
            print(f"✅ 从JSON文件加载了 {len(df)} 条记录")
            return df
    except Exception as e:
        print(f"❌ 无法加载JSON文件: {e}")
    
    return pd.DataFrame()

def perform_simple_pca(df):
    """执行简单的PCA分析"""
    if df.empty:
        print("❌ 没有数据可供分析")
        return None
    
    print(f"\n=== 开始PCA分析 ===")
    print(f"数据形状: {df.shape}")
    print(f"列名: {list(df.columns)}")
    
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
    
    # 处理缺失值
    print(f"缺失值统计:")
    for col in available_questions:
        missing = numeric_data[col].isnull().sum()
        print(f"  {col}: {missing}/{len(numeric_data)} ({missing/len(numeric_data)*100:.1f}%)")
    
    # 移除有缺失值的行
    complete_data = numeric_data.dropna()
    print(f"完整数据行数: {len(complete_data)}")
    
    if len(complete_data) < 2:
        print("❌ 完整数据太少，无法进行PCA分析")
        return None
    
    # 执行PCA
    try:
        from sklearn.decomposition import PCA
        from sklearn.preprocessing import StandardScaler
        
        # 标准化数据
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(complete_data)
        
        # PCA分析
        pca = PCA(n_components=2)
        pca_result = pca.fit_transform(scaled_data)
        
        print(f"✅ PCA分析完成")
        print(f"解释方差比: PC1={pca.explained_variance_ratio_[0]:.3f}, PC2={pca.explained_variance_ratio_[1]:.3f}")
        print(f"累计解释方差: {pca.explained_variance_ratio_.sum():.3f}")
        
        # 创建结果DataFrame
        result_df = df.loc[complete_data.index].copy()
        result_df['PC1'] = pca_result[:, 0]
        result_df['PC2'] = pca_result[:, 1]
        
        # 重新缩放PC分数（使用Inglehart-Welzel的缩放参数）
        pc1_rescaled = (result_df['PC1'] * 1.81) + 0.38
        pc2_rescaled = (result_df['PC2'] * 1.61) - 0.01
        
        result_df['PC1_rescaled'] = pc1_rescaled
        result_df['PC2_rescaled'] = pc2_rescaled
        
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
    print("=== 简化的Roleplay PCA分析 ===")
    
    # 1. 加载数据
    print("\n1. 加载roleplay数据...")
    df = load_roleplay_data()
    
    if df.empty:
        print("❌ 无法加载数据，退出")
        return
    
    # 2. 执行PCA分析
    print("\n2. 执行PCA分析...")
    result_df = perform_simple_pca(df)
    
    if result_df is not None:
        # 3. 保存结果
        print("\n3. 保存结果...")
        output_path = "data/llm_responses_roleplay/simple_pca_results.pkl"
        result_df.to_pickle(output_path)
        print(f"✅ PCA结果已保存到: {output_path}")
        
        # 4. 显示结果摘要
        print(f"\n=== 分析结果摘要 ===")
        print(f"总记录数: {len(result_df)}")
        print(f"模型数: {result_df['model_name'].nunique()}")
        print(f"国家数: {result_df['country_name'].nunique()}")
        print(f"PC1范围: {result_df['PC1_rescaled'].min():.3f} 到 {result_df['PC1_rescaled'].max():.3f}")
        print(f"PC2范围: {result_df['PC2_rescaled'].min():.3f} 到 {result_df['PC2_rescaled'].max():.3f}")
        
        print(f"\n前5条记录:")
        print(result_df[['model_name', 'country_name', 'PC1_rescaled', 'PC2_rescaled']].head())
        
    else:
        print("❌ PCA分析失败")

if __name__ == "__main__":
    main()
