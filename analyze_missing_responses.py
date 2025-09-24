import pandas as pd
import pickle
import json
from pathlib import Path
from typing import Dict, List, Set, Any
import os

def load_questions_config():
    """加载问题配置"""
    config_path = Path('config/ivs_questions.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config['ivs_questions']

def get_all_models_and_countries():
    """获取所有模型和国家列表"""
    responses_dir = Path('data/llm_responses_roleplay')
    models = set()
    countries = set()
    
    # 遍历所有子目录
    for subdir in responses_dir.iterdir():
        if subdir.is_dir() and subdir.name.startswith('roleplay_intermediate_'):
            # 从目录名提取模型名
            model_name = subdir.name.replace('roleplay_intermediate_', '').replace('_', '-')
            models.add(model_name)
            
            # 从pkl文件名提取国家名
            for pkl_file in subdir.glob('*.pkl'):
                if '_' in pkl_file.stem:
                    country = pkl_file.stem.split('_', 1)[1]
                    countries.add(country)
    
    return sorted(models), sorted(countries)

def analyze_missing_responses():
    """分析缺失的回答"""
    # 加载配置
    questions_config = load_questions_config()
    question_codes = list(questions_config.keys())
    
    # 获取所有模型和国家
    all_models, all_countries = get_all_models_and_countries()
    
    print(f"发现 {len(all_models)} 个模型: {all_models}")
    print(f"发现 {len(all_countries)} 个国家: {all_countries}")
    print(f"需要分析 {len(question_codes)} 个问题: {question_codes}")
    
    # 存储缺失数据
    missing_data = []
    response_summary = {}
    
    responses_dir = Path('data/llm_responses_roleplay')
    
    # 遍历所有模型目录
    for subdir in responses_dir.iterdir():
        if not (subdir.is_dir() and subdir.name.startswith('roleplay_intermediate_')):
            continue
            
        model_name = subdir.name.replace('roleplay_intermediate_', '').replace('_', '-')
        
        # 遍历该模型的所有国家文件
        for country in all_countries:
            pkl_files = list(subdir.glob(f'*_{country}.pkl'))
            
            if not pkl_files:
                # 整个国家的数据都缺失
                for question_code in question_codes:
                    missing_data.append({
                        'model': model_name,
                        'country': country,
                        'question': question_code,
                        'question_text': questions_config[question_code]['question'][:50] + '...',
                        'status': '文件不存在'
                    })
                continue
            
            # 加载pkl文件分析具体问题
            pkl_file = pkl_files[0]
            try:
                with open(pkl_file, 'rb') as f:
                    data = pickle.load(f)
                
                # 分析每个问题的回答情况
                for question_code in question_codes:
                    has_response = False
                    response_value = None
                    
                    if isinstance(data, dict):
                        # 遍历字典中的所有值（应该是列表）
                        for key, responses in data.items():
                            if isinstance(responses, list):
                                for response_item in responses:
                                    if isinstance(response_item, dict):
                                        # 检查question_id字段是否匹配
                                        if response_item.get('question_id') == question_code:
                                            response_value = response_item.get('response')
                                            is_valid = response_item.get('is_valid', False)
                                            # 检查回答是否有效
                                            if (response_value is not None and 
                                                str(response_value).strip() != '' and 
                                                is_valid):
                                                has_response = True
                                                break
                                if has_response:
                                    break
                    
                    # 记录结果
                    key = f"{model_name}_{country}"
                    if key not in response_summary:
                        response_summary[key] = {'model': model_name, 'country': country}
                    
                    if has_response:
                        response_summary[key][question_code] = '✓'
                    else:
                        response_summary[key][question_code] = '✗'
                        missing_data.append({
                            'model': model_name,
                            'country': country,
                            'question': question_code,
                            'question_text': questions_config[question_code]['question'][:50] + '...',
                            'status': '无回答或回答为空'
                        })
                        
            except Exception as e:
                print(f"加载文件失败 {pkl_file}: {e}")
                for question_code in question_codes:
                    missing_data.append({
                        'model': model_name,
                        'country': country,
                        'question': question_code,
                        'question_text': questions_config[question_code]['question'][:50] + '...',
                        'status': f'文件读取错误: {str(e)[:30]}'
                    })
    
    return missing_data, response_summary, question_codes

def create_summary_tables(missing_data, response_summary, question_codes):
    """创建汇总表格"""
    
    # 1. 缺失回答详细表
    missing_df = pd.DataFrame(missing_data)
    
    # 2. 模型-国家回答情况矩阵
    summary_df = pd.DataFrame(list(response_summary.values()))
    if not summary_df.empty:
        summary_df = summary_df.set_index(['model', 'country'])
    
    # 3. 按模型统计缺失情况
    if not missing_df.empty:
        model_missing_stats = missing_df.groupby('model').agg({
            'question': 'count',
            'country': 'nunique'
        }).rename(columns={'question': '缺失问题数', 'country': '涉及国家数'})
    else:
        model_missing_stats = pd.DataFrame()
    
    # 4. 按国家统计缺失情况
    if not missing_df.empty:
        country_missing_stats = missing_df.groupby('country').agg({
            'question': 'count',
            'model': 'nunique'
        }).rename(columns={'question': '缺失问题数', 'model': '涉及模型数'})
    else:
        country_missing_stats = pd.DataFrame()
    
    # 5. 按问题统计缺失情况
    if not missing_df.empty:
        question_missing_stats = missing_df.groupby('question').agg({
            'model': 'nunique',
            'country': 'nunique'
        }).rename(columns={'model': '涉及模型数', 'country': '涉及国家数'})
        question_missing_stats['缺失总数'] = missing_df.groupby('question').size()
    else:
        question_missing_stats = pd.DataFrame()
    
    # 6. 新增：每个模型对每个国家的无效回答次数表
    model_country_missing = pd.DataFrame()
    if not missing_df.empty:
        # 创建模型-国家的缺失次数透视表
        model_country_missing = missing_df.groupby(['model', 'country']).size().reset_index(name='无效回答次数')
        
        # 创建完整的模型-国家组合表（包括没有缺失的组合）
        all_models, all_countries = get_all_models_and_countries()
        full_combinations = pd.MultiIndex.from_product([all_models, all_countries], names=['model', 'country']).to_frame(index=False)
        
        # 合并数据，填充0表示没有缺失
        model_country_missing = full_combinations.merge(model_country_missing, on=['model', 'country'], how='left')
        model_country_missing['无效回答次数'] = model_country_missing['无效回答次数'].fillna(0).astype(int)
        
        # 创建透视表格式（模型为行，国家为列）
        model_country_pivot = model_country_missing.pivot(index='model', columns='country', values='无效回答次数')
        
        # 添加汇总列
        model_country_pivot['总计'] = model_country_pivot.sum(axis=1)
        
        # 添加汇总行
        total_row = model_country_pivot.sum(axis=0)
        total_row.name = '总计'
        model_country_pivot = pd.concat([model_country_pivot, total_row.to_frame().T])
    
    return {
        'missing_details': missing_df,
        'response_matrix': summary_df,
        'model_stats': model_missing_stats,
        'country_stats': country_missing_stats,
        'question_stats': question_missing_stats,
        'model_country_missing': model_country_missing if not missing_df.empty else pd.DataFrame(),
        'model_country_pivot': model_country_pivot if not missing_df.empty else pd.DataFrame()
    }

def save_results(tables):
    """保存结果到文件"""
    output_dir = Path('results')
    output_dir.mkdir(exist_ok=True)
    
    # 保存到Excel文件
    excel_path = output_dir / 'missing_responses_analysis.xlsx'
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        if not tables['missing_details'].empty:
            tables['missing_details'].to_excel(writer, sheet_name='缺失详情', index=False)
        if not tables['response_matrix'].empty:
            tables['response_matrix'].to_excel(writer, sheet_name='回答矩阵')
        if not tables['model_stats'].empty:
            tables['model_stats'].to_excel(writer, sheet_name='模型统计')
        if not tables['country_stats'].empty:
            tables['country_stats'].to_excel(writer, sheet_name='国家统计')
        if not tables['question_stats'].empty:
            tables['question_stats'].to_excel(writer, sheet_name='问题统计')
        # 新增的表格
        if not tables['model_country_missing'].empty:
            tables['model_country_missing'].to_excel(writer, sheet_name='模型国家缺失明细', index=False)
        if not tables['model_country_pivot'].empty:
            tables['model_country_pivot'].to_excel(writer, sheet_name='模型国家缺失矩阵')
    
    print(f"结果已保存到: {excel_path}")
    
    # 保存到CSV文件
    if not tables['missing_details'].empty:
        csv_path = output_dir / 'missing_responses_details.csv'
        tables['missing_details'].to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"详细结果已保存到: {csv_path}")
    
    # 保存模型-国家缺失矩阵到单独的CSV
    if not tables['model_country_pivot'].empty:
        pivot_csv_path = output_dir / 'model_country_missing_matrix.csv'
        tables['model_country_pivot'].to_csv(pivot_csv_path, encoding='utf-8-sig')
        print(f"模型-国家缺失矩阵已保存到: {pivot_csv_path}")

def print_summary(tables):
    """打印汇总信息"""
    print("\n=== 缺失回答分析汇总 ===")
    
    if not tables['missing_details'].empty:
        total_missing = len(tables['missing_details'])
        print(f"总缺失回答数: {total_missing}")
        
        print("\n=== 按模型统计 ===")
        print(tables['model_stats'])
        
        print("\n=== 按国家统计 ===")
        print(tables['country_stats'])
        
        print("\n=== 按问题统计 ===")
        print(tables['question_stats'])
        
        print("\n=== 缺失最多的前10个组合 ===")
        top_missing = tables['missing_details'].groupby(['model', 'country']).size().sort_values(ascending=False).head(10)
        print(top_missing)
        
        # 新增：显示模型-国家缺失矩阵
        if not tables['model_country_pivot'].empty:
            print("\n=== 模型-国家无效回答次数矩阵 ===")
            print(tables['model_country_pivot'])
    else:
        print("没有发现缺失的回答！")

def main():
    """主函数"""
    print("开始分析缺失回答...")
    
    # 分析缺失回答
    missing_data, response_summary, question_codes = analyze_missing_responses()
    
    # 创建汇总表格
    tables = create_summary_tables(missing_data, response_summary, question_codes)
    
    # 打印汇总信息
    print_summary(tables)
    
    # 保存结果
    save_results(tables)
    
    print("\n分析完成！")

if __name__ == "__main__":
    main()