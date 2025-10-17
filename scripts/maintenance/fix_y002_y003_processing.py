import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
import json
from typing import List, Tuple

# 将项目根目录添加到Python路径
sys.path.append(str(Path(__file__).parent))

def Y002_transform(ans: Tuple[int, int]) -> int:
    """Y002问题转换函数 - 物质主义倾向"""
    if len(ans) != 2:
        return -5
    
    q_154, q_155 = ans
    
    if q_154 < 0 or q_155 < 0:
        return -5
    if (q_154 == 1 and q_155 == 3) or (q_154 == 3 and q_155 == 1):
        return 1  # Materialist
    if (q_154 == 2 and q_155 == 4) or (q_154 == 4 and q_155 == 2):
        return 3  # Postmaterialist
    return 2  # Mixed

def Y003_transform(ans: List[int]) -> int:
    """Y003问题转换函数 - 传统vs世俗理性价值观"""
    if not ans or len(ans) == 0:
        return -5
    
    # 将选择转换为布尔列表
    bool_list = [i in ans for i in range(1, 12)]
    # 映射True为1，False为2
    scores = [1 if i else 2 for i in bool_list]
    
    qn_ans_dict = {
        "q7": scores[0],   # Good manners
        "q8": scores[1],   # Independence
        "q9": scores[2],   # Hard work
        "q10": scores[3],  # Feeling of responsibility
        "q11": scores[4],  # Imagination
        "q12": scores[5],  # Tolerance and respect
        "q13": scores[6],  # Thrift, saving money
        "q14": scores[7],  # Determination, perseverance
        "q15": scores[8],  # Religious faith
        "q16": scores[9],  # Not being selfish
        "q17": scores[10], # Obedience
    }
    
    # 计算Y003分数
    if (qn_ans_dict["q15"] >= 0 and qn_ans_dict["q17"] >= 0 and 
        qn_ans_dict["q8"] >= 0 and qn_ans_dict["q14"] >= 0):
        y003 = (qn_ans_dict["q15"] + qn_ans_dict["q17"]) - (qn_ans_dict["q8"] + qn_ans_dict["q14"])
    else:
        y003 = -5
    
    return y003

def load_and_fix_ai_data():
    """重新加载AI数据并正确处理Y002和Y003"""
    print("=== 重新加载AI数据并修复Y002和Y003 ===")
    
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
                    y002_raw = None
                    y003_raw = None
                    
                    for response in responses:
                        if response and isinstance(response, dict):
                            question_id = response.get('question_id', '')
                            raw_response = response.get('raw_response')
                            is_valid = response.get('is_valid', False)
                            
                            if question_id == 'Y002' and is_valid and raw_response:
                                y002_raw = raw_response
                            elif question_id == 'Y003' and is_valid and raw_response:
                                y003_raw = raw_response
                            elif question_id and is_valid:
                                # 处理其他问题
                                response_value = response.get('response')
                                if response_value is not None:
                                    if response_value == "None" or response_value == "null":
                                        record[question_id] = None
                                    else:
                                        try:
                                            if isinstance(response_value, str):
                                                cleaned_value = response_value.strip('[](){}')
                                                record[question_id] = float(cleaned_value)
                                            else:
                                                record[question_id] = response_value
                                        except (ValueError, TypeError):
                                            record[question_id] = None
                    
                    # 处理Y002
                    if y002_raw:
                        try:
                            # 解析Y002：应该是两个数字
                            if ' ' in y002_raw:
                                numbers = [int(x.strip()) for x in y002_raw.strip().split()]
                            elif ',' in y002_raw:
                                numbers = [int(x.strip()) for x in y002_raw.strip().split(',')]
                            else:
                                numbers = [int(y002_raw.strip())]
                            
                            if len(numbers) == 2 and all(1 <= n <= 4 for n in numbers):
                                # 应用Y002转换函数
                                transformed_value = Y002_transform(tuple(numbers))
                                record['Y002'] = transformed_value if transformed_value >= 0 else None
                                print(f"    Y002: {y002_raw} -> {numbers} -> {transformed_value}")
                            else:
                                record['Y002'] = None
                                print(f"    Y002: 无效格式 {y002_raw}")
                        except Exception as e:
                            record['Y002'] = None
                            print(f"    Y002: 解析错误 {y002_raw}: {e}")
                    else:
                        record['Y002'] = None
                    
                    # 处理Y003
                    if y003_raw:
                        try:
                            # 解析Y003：应该是1-5个数字
                            if ' ' in y003_raw:
                                numbers = [int(x.strip()) for x in y003_raw.strip().split()]
                            elif ',' in y003_raw:
                                numbers = [int(x.strip()) for x in y003_raw.strip().split(',')]
                            else:
                                numbers = [int(y003_raw.strip())]
                            
                            if 1 <= len(numbers) <= 5 and all(1 <= n <= 11 for n in numbers):
                                # 应用Y003转换函数
                                transformed_value = Y003_transform(numbers)
                                record['Y003'] = transformed_value if transformed_value >= -4 else None  # 允许负值但不允许-5
                                print(f"    Y003: {y003_raw} -> {numbers} -> {transformed_value}")
                            else:
                                record['Y003'] = None
                                print(f"    Y003: 无效格式 {y003_raw}")
                        except Exception as e:
                            record['Y003'] = None
                            print(f"    Y003: 解析错误 {y003_raw}: {e}")
                    else:
                        record['Y003'] = None
                    
                    all_data.append(record)
                    
                except Exception as e:
                    print(f"  错误处理 {country_file}: {e}")
    
    df = pd.DataFrame(all_data)
    print(f"✅ 重新加载了 {len(df)} 条AI角色扮演数据")
    return df

def perform_corrected_pca_analysis(df):
    """使用修正后的数据进行PCA分析"""
    print("\n=== 使用修正后的Y002/Y003数据进行PCA分析 ===")
    
    if df.empty:
        print("❌ 没有数据可供分析")
        return None
    
    print(f"数据形状: {df.shape}")
    
    # 定义IVS问题
    ivs_questions = ['A008', 'A165', 'E018', 'E025', 'F063', 'F118', 'F120', 'G006', 'Y002', 'Y003']
    
    # 检查哪些问题在数据中
    available_questions = [q for q in ivs_questions if q in df.columns]
    print(f"可用的IVS问题: {available_questions}")
    
    # 提取数值数据
    numeric_data = df[available_questions].copy()
    
    # 检查Y002和Y003的修正结果
    print(f"\n修正后的Y002和Y003分布:")
    for col in ['Y002', 'Y003']:
        if col in numeric_data.columns:
            valid_data = numeric_data[col].dropna()
            if len(valid_data) > 0:
                print(f"{col}: 范围 {valid_data.min()} 到 {valid_data.max()}, 唯一值: {sorted(valid_data.unique())}")
            else:
                print(f"{col}: 无有效值")
    
    # 处理缺失值统计
    print(f"\n缺失值统计:")
    for col in available_questions:
        missing = numeric_data[col].isnull().sum()
        print(f"  {col}: {missing}/{len(numeric_data)} ({missing/len(numeric_data)*100:.1f}%)")
    
    # 使用6个以上问题有回答就算有效的规则
    valid_counts = numeric_data.count(axis=1)
    valid_data_mask = valid_counts >= 6
    
    print(f"\n有效数据行数: {valid_data_mask.sum()}")
    print(f"有效数据比例: {valid_data_mask.sum()}/{len(numeric_data)} ({valid_data_mask.sum()/len(numeric_data)*100:.1f}%)")
    
    if valid_data_mask.sum() < 2:
        print("❌ 有效数据太少，无法进行PCA分析")
        return None
    
    # 使用有效数据
    complete_data = numeric_data[valid_data_mask]
    
    # 执行PCA
    try:
        from ppca import PPCA
        from factor_analyzer import Rotator
        
        print("使用PPCA进行分析...")
        
        # 设置随机种子确保结果可重现
        np.random.seed(42)
        
        # 使用PPCA进行分析
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
        
        # 重新缩放PC分数
        result_df['PC1_rescaled'] = 1.81 * result_df['PC1'] + 0.38
        result_df['PC2_rescaled'] = 1.61 * result_df['PC2'] - 0.01
        
        print(f"PC1范围: {result_df['PC1_rescaled'].min():.3f} 到 {result_df['PC1_rescaled'].max():.3f}")
        print(f"PC2范围: {result_df['PC2_rescaled'].min():.3f} 到 {result_df['PC2_rescaled'].max():.3f}")
        
        return result_df
        
    except Exception as e:
        print(f"❌ PCA分析失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """主函数"""
    print("=== 修复Y002和Y003的数据处理 ===")
    
    try:
        # 1. 重新加载并修复AI数据
        ai_data = load_and_fix_ai_data()
        
        if ai_data.empty:
            print("❌ 没有AI角色扮演数据")
            return
        
        # 2. 执行修正后的PCA分析
        result_df = perform_corrected_pca_analysis(ai_data)
        
        if result_df is not None:
            # 3. 保存结果
            print("\n=== 保存修正后的结果 ===")
            output_path = "data/llm_responses_roleplay/fixed_y002_y003_pca_results.pkl"
            result_df.to_pickle(output_path)
            print(f"✅ 修正后的PCA结果已保存到: {output_path}")
            
            # 4. 显示结果摘要
            print(f"\n=== 修正后的分析结果摘要 ===")
            print(f"总记录数: {len(result_df)}")
            print(f"模型数: {result_df['model_name'].nunique()}")
            print(f"国家数: {result_df['country_name'].nunique()}")
            print(f"PC1范围: {result_df['PC1_rescaled'].min():.3f} 到 {result_df['PC1_rescaled'].max():.3f}")
            print(f"PC2范围: {result_df['PC2_rescaled'].min():.3f} 到 {result_df['PC2_rescaled'].max():.3f}")
            
            # 检查Y002和Y003的最终分布
            print(f"\n修正后的Y002和Y003最终分布:")
            for col in ['Y002', 'Y003']:
                if col in result_df.columns:
                    valid_data = result_df[col].dropna()
                    if len(valid_data) > 0:
                        print(f"{col}: 范围 {valid_data.min()} 到 {valid_data.max()}, 唯一值: {sorted(valid_data.unique())}")
                    else:
                        print(f"{col}: 无有效值")
            
            print(f"\n🎉 Y002和Y003数据修正完成！")
            
        else:
            print("❌ PCA分析失败")
            
    except Exception as e:
        print(f"❌ 修正过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
