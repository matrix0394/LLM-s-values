#!/usr/bin/env python3
"""
修复Y002和Y003的数据处理问题
主要问题：
1. response字段解析错误，只取了第一个字符而不是完整的数字列表
2. Y002需要两个选择，Y003需要1-5个选择
3. 需要正确应用转换函数
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
import json
from typing import List, Tuple, Dict, Any
import pickle

# 将项目根目录添加到Python路径
sys.path.append(str(Path(__file__).parent))

def Y002_transform(ans: Tuple[int, int]) -> int:
    """Y002问题转换函数 - 物质主义倾向"""
    if len(ans) != 2:
        return -5
    
    q_154, q_155 = ans
    
    if q_154 < 0 or q_155 < 0 or q_154 > 4 or q_155 > 4:
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
    
    # 验证所有选择都在有效范围内
    if not all(1 <= choice <= 11 for choice in ans):
        return -5
    
    # 将选择转换为布尔列表
    bool_list = [i in ans for i in range(1, 12)]
    # 映射True为1，False为2
    scores = [1 if i else 2 for i in bool_list]
    
    qn_ans_dict = {
        "q7": scores[0],   # Good manners (1)
        "q8": scores[1],   # Independence (2)
        "q9": scores[2],   # Hard work (3)
        "q10": scores[3],  # Feeling of responsibility (4)
        "q11": scores[4],  # Imagination (5)
        "q12": scores[5],  # Tolerance and respect (6)
        "q13": scores[6],  # Thrift, saving money (7)
        "q14": scores[7],  # Determination, perseverance (8)
        "q15": scores[8],  # Religious faith (9)
        "q16": scores[9],  # Not being selfish (10)
        "q17": scores[10], # Obedience (11)
    }
    
    # 计算Y003分数：(宗教信仰 + 服从) - (独立 + 坚持)
    if (qn_ans_dict["q15"] >= 0 and qn_ans_dict["q17"] >= 0 and 
        qn_ans_dict["q8"] >= 0 and qn_ans_dict["q14"] >= 0):
        y003 = (qn_ans_dict["q15"] + qn_ans_dict["q17"]) - (qn_ans_dict["q8"] + qn_ans_dict["q14"])
        return y003
    else:
        return -5

def parse_raw_response(raw_response: str, question_id: str) -> List[int]:
    """正确解析原始响应"""
    if not raw_response or raw_response.strip() == "":
        return []
    
    try:
        raw = raw_response.strip()
        
        # 移除可能的括号
        raw = raw.strip('[](){}"\'')
        
        # 分割数字
        if ',' in raw:
            numbers = [int(x.strip()) for x in raw.split(',') if x.strip().isdigit()]
        elif ' ' in raw:
            numbers = [int(x.strip()) for x in raw.split() if x.strip().isdigit()]
        else:
            # 单个数字
            if raw.isdigit():
                numbers = [int(raw)]
            else:
                return []
        
        # 验证数字范围
        if question_id == 'Y002':
            # Y002需要恰好2个选择，每个在1-4范围内
            if len(numbers) == 2 and all(1 <= n <= 4 for n in numbers) and numbers[0] != numbers[1]:
                return numbers
        elif question_id == 'Y003':
            # Y003需要1-5个选择，每个在1-11范围内
            if 1 <= len(numbers) <= 5 and all(1 <= n <= 11 for n in numbers):
                return list(set(numbers))  # 去重
        
        return []
    except Exception as e:
        print(f"解析错误 {raw_response}: {e}")
        return []

def load_and_fix_roleplay_data():
    """重新加载并正确处理角色扮演数据"""
    print("=== 修复角色扮演数据中的Y002和Y003处理 ===")
    
    all_data = []
    roleplay_dir = Path("data/llm_responses_roleplay")
    
    # 统计信息
    total_files = 0
    y002_fixed = 0
    y003_fixed = 0
    y002_invalid = 0
    y003_invalid = 0
    
    # 遍历所有模型目录
    for model_dir in roleplay_dir.iterdir():
        if model_dir.is_dir() and not model_dir.name.startswith('.'):
            model_name = model_dir.name.replace('_', '/')
            print(f"处理模型: {model_name}")
            
            # 遍历该模型的所有国家文件
            for country_file in model_dir.glob("*.json"):
                if country_file.name.endswith('.json'):
                    country_name = country_file.stem.replace('_', ' ')
                    total_files += 1
                    
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
                        
                        # 处理所有回答
                        for response in responses:
                            if response and isinstance(response, dict):
                                question_id = response.get('question_id', '')
                                is_valid = response.get('is_valid', False)
                                
                                if not is_valid:
                                    continue
                                
                                if question_id == 'Y002':
                                    raw_response = response.get('raw_response')
                                    if raw_response:
                                        parsed_numbers = parse_raw_response(raw_response, 'Y002')
                                        if len(parsed_numbers) == 2:
                                            # 应用Y002转换函数
                                            transformed_value = Y002_transform(tuple(parsed_numbers))
                                            if transformed_value >= 0:
                                                record['Y002'] = transformed_value
                                                y002_fixed += 1
                                                print(f"    Y002: {raw_response} -> {parsed_numbers} -> {transformed_value}")
                                            else:
                                                record['Y002'] = None
                                                y002_invalid += 1
                                        else:
                                            record['Y002'] = None
                                            y002_invalid += 1
                                            print(f"    Y002: 无效格式 {raw_response}")
                                    else:
                                        record['Y002'] = None
                                
                                elif question_id == 'Y003':
                                    raw_response = response.get('raw_response')
                                    if raw_response:
                                        parsed_numbers = parse_raw_response(raw_response, 'Y003')
                                        if len(parsed_numbers) >= 1:
                                            # 应用Y003转换函数
                                            transformed_value = Y003_transform(parsed_numbers)
                                            if transformed_value >= -4:  # Y003允许负值
                                                record['Y003'] = transformed_value
                                                y003_fixed += 1
                                                print(f"    Y003: {raw_response} -> {parsed_numbers} -> {transformed_value}")
                                            else:
                                                record['Y003'] = None
                                                y003_invalid += 1
                                        else:
                                            record['Y003'] = None
                                            y003_invalid += 1
                                            print(f"    Y003: 无效格式 {raw_response}")
                                    else:
                                        record['Y003'] = None
                                
                                elif question_id in ['A008', 'A165', 'E018', 'E025', 'F063', 'F118', 'F120', 'G006']:
                                    # 处理其他问题
                                    response_value = response.get('response')
                                    if response_value is not None and response_value != "None":
                                        try:
                                            if isinstance(response_value, str):
                                                cleaned_value = response_value.strip('[](){}"\' ')
                                                if cleaned_value.replace('.', '').isdigit():
                                                    record[question_id] = float(cleaned_value)
                                                else:
                                                    record[question_id] = None
                                            else:
                                                record[question_id] = response_value
                                        except:
                                            record[question_id] = None
                        
                        all_data.append(record)
                        
                    except Exception as e:
                        print(f"  错误处理 {country_file}: {e}")
    
    print(f"\n=== 处理统计 ===")
    print(f"总文件数: {total_files}")
    print(f"Y002修复成功: {y002_fixed}")
    print(f"Y002无效: {y002_invalid}")
    print(f"Y003修复成功: {y003_fixed}")
    print(f"Y003无效: {y003_invalid}")
    
    df = pd.DataFrame(all_data)
    print(f"✅ 重新处理了 {len(df)} 条AI角色扮演数据")
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
                print(f"{col}: 范围 {valid_data.min()} 到 {valid_data.max()}")
                print(f"     唯一值: {sorted(valid_data.unique())}")
                print(f"     有效值数量: {len(valid_data)}")
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
    
    if valid_data_mask.sum() < 10:
        print("❌ 有效数据太少，无法进行PCA分析")
        return None
    
    # 使用有效数据
    complete_data = numeric_data[valid_data_mask].copy()
    
    # 填充剩余的缺失值（使用中位数）
    for col in available_questions:
        if complete_data[col].isnull().sum() > 0:
            median_val = complete_data[col].median()
            if not np.isnan(median_val):
                complete_data[col].fillna(median_val, inplace=True)
                print(f"  {col}: 使用中位数 {median_val} 填充缺失值")
    
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
        
        print(f"PC1_rescaled范围: {result_df['PC1_rescaled'].min():.3f} 到 {result_df['PC1_rescaled'].max():.3f}")
        print(f"PC2_rescaled范围: {result_df['PC2_rescaled'].min():.3f} 到 {result_df['PC2_rescaled'].max():.3f}")
        
        # 检查范围是否合理（应该在-5到10之间）
        pc1_range = result_df['PC1_rescaled'].max() - result_df['PC1_rescaled'].min()
        pc2_range = result_df['PC2_rescaled'].max() - result_df['PC2_rescaled'].min()
        
        if pc1_range > 15 or pc2_range > 15:
            print("⚠️  警告：PC范围仍然异常大，可能需要进一步检查数据")
        else:
            print("✅ PC范围看起来正常")
        
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
        print("步骤1: 重新加载并修复角色扮演数据...")
        ai_data = load_and_fix_roleplay_data()
        
        if ai_data.empty:
            print("❌ 没有AI角色扮演数据")
            return
        
        # 2. 执行修正后的PCA分析
        print("\n步骤2: 执行修正后的PCA分析...")
        result_df = perform_corrected_pca_analysis(ai_data)
        
        if result_df is not None:
            # 3. 保存结果
            print("\n步骤3: 保存修正后的结果...")
            output_path = "data/llm_responses_roleplay/correctly_fixed_y002_y003_pca_results.pkl"
            result_df.to_pickle(output_path)
            print(f"✅ 修正后的PCA结果已保存到: {output_path}")
            
            # 4. 显示结果摘要
            print(f"\n=== 修正后的分析结果摘要 ===")
            print(f"总记录数: {len(result_df)}")
            print(f"模型数: {result_df['model_name'].nunique()}")
            print(f"国家数: {result_df['country_name'].nunique()}")
            print(f"PC1_rescaled范围: {result_df['PC1_rescaled'].min():.3f} 到 {result_df['PC1_rescaled'].max():.3f}")
            print(f"PC2_rescaled范围: {result_df['PC2_rescaled'].min():.3f} 到 {result_df['PC2_rescaled'].max():.3f}")
            
            # 检查Y002和Y003的最终分布
            print(f"\n修正后的Y002和Y003最终分布:")
            for col in ['Y002', 'Y003']:
                if col in result_df.columns:
                    valid_data = result_df[col].dropna()
                    if len(valid_data) > 0:
                        print(f"{col}: 范围 {valid_data.min()} 到 {valid_data.max()}")
                        print(f"     唯一值: {sorted(valid_data.unique())}")
                        print(f"     分布: {valid_data.value_counts().sort_index().to_dict()}")
                    else:
                        print(f"{col}: 无有效值")
            
            print(f"\n🎉 Y002和Y003数据修正完成！")
            
            # 5. 与之前的结果对比
            try:
                old_file = "data/llm_responses_roleplay/fixed_y002_y003_pca_results.pkl"
                if os.path.exists(old_file):
                    old_df = pd.read_pickle(old_file)
                    print(f"\n=== 与之前结果的对比 ===")
                    print(f"之前PC1范围: {old_df['PC1_rescaled'].min():.3f} 到 {old_df['PC1_rescaled'].max():.3f}")
                    print(f"之前PC2范围: {old_df['PC2_rescaled'].min():.3f} 到 {old_df['PC2_rescaled'].max():.3f}")
                    print(f"现在PC1范围: {result_df['PC1_rescaled'].min():.3f} 到 {result_df['PC2_rescaled'].max():.3f}")
                    print(f"现在PC2范围: {result_df['PC2_rescaled'].min():.3f} 到 {result_df['PC2_rescaled'].max():.3f}")
                    
                    old_pc1_range = old_df['PC1_rescaled'].max() - old_df['PC1_rescaled'].min()
                    old_pc2_range = old_df['PC2_rescaled'].max() - old_df['PC2_rescaled'].min()
                    new_pc1_range = result_df['PC1_rescaled'].max() - result_df['PC1_rescaled'].min()
                    new_pc2_range = result_df['PC2_rescaled'].max() - result_df['PC2_rescaled'].min()
                    
                    print(f"PC1范围变化: {old_pc1_range:.3f} -> {new_pc1_range:.3f}")
                    print(f"PC2范围变化: {old_pc2_range:.3f} -> {new_pc2_range:.3f}")
            except Exception as e:
                print(f"对比失败: {e}")
            
        else:
            print("❌ PCA分析失败")
            
    except Exception as e:
        print(f"❌ 修正过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
