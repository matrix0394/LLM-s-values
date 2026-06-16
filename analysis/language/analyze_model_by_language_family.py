#!/usr/bin/env python3
"""
分析不同模型在不同语系上的英语优势差异
直接使用cultural_distance_analysis.csv中的数据
"""
import pandas as pd
import numpy as np
from pathlib import Path

# 输出目录
OUTPUT_DIR = Path('results/analysis/language_family_analysis')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 正确的语系分类（基于语言学）
LANG_TO_FAMILY = {
    'ar': '闪米特语系',
    'zh-cn': '汉藏语系',
    'zh-tw': '汉藏语系',
    'zh-hk': '汉藏语系',
    'ja': '日本语系',
    'ko': '韩语系',
    'ru': '斯拉夫语系',
    'es': '罗曼语系',
    'fr': '罗曼语系',
    'it': '罗曼语系',
    'pt': '罗曼语系',
    'de': '日耳曼语系',
}

# 模型来源国
MODEL_TO_COUNTRY = {
    'gpt-4o': '美国',
    'gpt-4o-mini': '美国',
    'gpt-5.1': '美国',
    'claude-3-7-sonnet-20250219': '美国',
    'claude-sonnet-4.5': '美国',
    'gemini-2.5-flash': '美国',
    'gemini-2.5-pro': '美国',
    'gemini-3-pro-preview': '美国',
    'gemma-3-4b-it': '美国',
    'deepseek-chat': '中国',
    'deepseek-chat-v3.1': '中国',
    'qwen3-max': '中国',
    'doubao-1-5-pro-32k-250115': '中国',
    'kimi-k2': '中国',
    'mistral-medium-3.1': '法国',
    'mistral-nemo': '法国',
    'llama-3.2-3b-instruct': '美国',
    'llama-3.3-70b-instruct': '美国',
    'grok-4.1-fast': '美国',
    'phi-3-mini-128k-instruct': '美国',
}

# 中国模型列表
CHINESE_MODELS = ['deepseek-chat', 'deepseek-chat-v3.1', 'qwen3-max', 'doubao-1-5-pro-32k-250115', 'kimi-k2']

# 开源/闭源模型分类
OPEN_SOURCE_MODELS = [
    'llama-3.2-3b-instruct',
    'llama-3.3-70b-instruct',
    'mistral-nemo',
    'phi-3-mini-128k-instruct',
    'gemma-3-4b-it',
    'deepseek-chat',
    'deepseek-chat-v3.1',
    'qwen3-max',
]

CLOSED_SOURCE_MODELS = [
    'gpt-4o',
    'gpt-4o-mini',
    'gpt-5.1',
    'claude-3-7-sonnet-20250219',
    'claude-sonnet-4.5',
    'gemini-2.5-flash',
    'gemini-2.5-pro',
    'gemini-3-pro-preview',
    'mistral-medium-3.1',
    'doubao-1-5-pro-32k-250115',
    'kimi-k2',
    'grok-4.1-fast',
]


def load_data():
    """加载数据"""
    df = pd.read_csv('results/roleplay_multilingual/cultural_distance_analysis.csv')
    
    # 排除低质量模型
    bad_models = ['qwen3-1.7b']
    df = df[~df['model'].isin(bad_models)]
    
    return df


def analyze_model_by_family(df):
    """分析每个模型在每个语系上的英语优势
    
    方法：
    1. 对于每个模型和每个语系
    2. 找出该语系对应的所有语言的数据
    3. 对每条记录，找到同一国家同一模型的英语数据
    4. 计算配对的英语优势
    """
    print("\n" + "=" * 80)
    print("📊 各模型在不同语系上的英语优势分析")
    print("=" * 80)
    
    # 排除英语母语国家
    non_english = df[~df['is_english_native_country']].copy()
    
    results = []
    
    # 获取所有模型
    models = sorted(non_english['model'].unique())
    families = ['闪米特语系', '斯拉夫语系', '汉藏语系', '罗曼语系', '日耳曼语系']
    
    for model in models:
        model_data = non_english[non_english['model'] == model]
        
        for family in families:
            # 获取该语系对应的语言列表
            family_langs = [lang for lang, fam in LANG_TO_FAMILY.items() if fam == family]
            
            # 找出使用该语系语言的所有记录（官方语言数据）
            native_records = model_data[model_data['language'].isin(family_langs)]
            
            if len(native_records) == 0:
                continue
            
            # 收集配对数据
            paired = []
            
            for _, native_row in native_records.iterrows():
                country = native_row['country']
                native_lang = native_row['language']
                native_dist = native_row['cultural_distance']
                
                # 找同一国家同一模型的英语数据
                english_row = model_data[
                    (model_data['country'] == country) & 
                    (model_data['is_english'] == True)
                ]
                
                if len(english_row) > 0:
                    english_dist = english_row['cultural_distance'].iloc[0]
                    paired.append({
                        'country': country,
                        'native_lang': native_lang,
                        'native_dist': native_dist,
                        'english_dist': english_dist
                    })
            
            if len(paired) == 0:
                continue
            
            paired_df = pd.DataFrame(paired)
            
            # 计算平均距离
            native_mean = paired_df['native_dist'].mean()
            english_mean = paired_df['english_dist'].mean()
            
            # 英语优势 = (官方语言距离 - 英语距离) / 官方语言距离 * 100%
            # 正值 = 英语更好（距离更小），负值 = 官方语言更好
            if native_mean > 0:
                english_advantage = (native_mean - english_mean) / native_mean * 100
            else:
                english_advantage = 0
            
            results.append({
                'model': model,
                'model_country': MODEL_TO_COUNTRY.get(model, 'Unknown'),
                'family': family,
                'n_pairs': len(paired),
                'native_mean': native_mean,
                'english_mean': english_mean,
                'english_advantage': english_advantage
            })
    
    results_df = pd.DataFrame(results)
    return results_df


def print_model_family_matrix(results_df):
    """打印模型-语系矩阵"""
    print("\n" + "=" * 80)
    print("📊 模型-语系英语优势矩阵")
    print("=" * 80)
    
    # 创建透视表
    pivot = results_df.pivot_table(
        index='model', 
        columns='family', 
        values='english_advantage',
        aggfunc='mean'
    )
    
    print("\n英语优势 (%):")
    print(pivot.round(1).to_string())
    
    return pivot


def analyze_by_model_origin(results_df):
    """按模型来源国分析"""
    print("\n" + "=" * 80)
    print("📊 按模型来源国分析")
    print("=" * 80)
    
    # 方法：先汇总所有配对的距离，再计算英语优势
    # 而不是对各模型的英语优势取平均
    
    print("\n按模型来源国和语系的英语优势（基于平均距离）:")
    for country in ['中国', '美国', '法国']:
        country_data = results_df[results_df['model_country'] == country]
        if len(country_data) == 0:
            continue
        print(f"\n{country}模型:")
        
        for family in ['闪米特语系', '斯拉夫语系', '汉藏语系', '罗曼语系', '日耳曼语系']:
            family_data = country_data[country_data['family'] == family]
            if len(family_data) == 0:
                continue
            
            # 用加权平均（按配对数加权）
            total_native = (family_data['native_mean'] * family_data['n_pairs']).sum()
            total_english = (family_data['english_mean'] * family_data['n_pairs']).sum()
            total_pairs = family_data['n_pairs'].sum()
            
            if total_pairs > 0:
                avg_native = total_native / total_pairs
                avg_english = total_english / total_pairs
                eng_adv = (avg_native - avg_english) / avg_native * 100
                print(f"  {family}: {eng_adv:+.1f}% (母语={avg_native:.2f}, 英语={avg_english:.2f}, n={total_pairs})")
    
    # 计算各来源国的整体英语优势
    print("\n按模型来源国的整体英语优势:")
    for country in ['中国', '美国', '法国']:
        country_data = results_df[results_df['model_country'] == country]
        if len(country_data) == 0:
            continue
        
        total_native = (country_data['native_mean'] * country_data['n_pairs']).sum()
        total_english = (country_data['english_mean'] * country_data['n_pairs']).sum()
        total_pairs = country_data['n_pairs'].sum()
        
        if total_pairs > 0:
            avg_native = total_native / total_pairs
            avg_english = total_english / total_pairs
            eng_adv = (avg_native - avg_english) / avg_native * 100
            print(f"  {country}: {eng_adv:+.1f}% (母语={avg_native:.2f}, 英语={avg_english:.2f})")
    
    return None


def print_chinese_models_hanzi(results_df):
    """打印中国模型在汉藏语系的表现"""
    print("\n" + "=" * 80)
    print("📊 中国模型在汉藏语系的表现")
    print("=" * 80)
    
    chinese_hanzi = results_df[
        (results_df['model'].isin(CHINESE_MODELS)) & 
        (results_df['family'] == '汉藏语系')
    ]
    
    if len(chinese_hanzi) > 0:
        print("\n中国模型在汉藏语系的表现（按官方语言距离排序）:")
        for _, row in chinese_hanzi.sort_values('native_mean').iterrows():
            print(f"  {row['model']}: 官方语言={row['native_mean']:.2f}, 英语={row['english_mean']:.2f}, 英语优势={row['english_advantage']:+.1f}%")
    else:
        print("  没有找到中国模型在汉藏语系的数据")
        # 调试：检查有哪些中国模型
        print("\n  调试信息:")
        print(f"  数据中的中国模型: {results_df[results_df['model'].isin(CHINESE_MODELS)]['model'].unique().tolist()}")
        print(f"  汉藏语系数据: {results_df[results_df['family'] == '汉藏语系']['model'].unique().tolist()}")


def debug_extreme_values(df, results_df):
    """调试极端值"""
    print("\n" + "=" * 80)
    print("📊 极端值调试")
    print("=" * 80)
    
    # 找出英语优势绝对值大于50%的记录
    extreme = results_df[abs(results_df['english_advantage']) > 50]
    
    if len(extreme) > 0:
        print(f"\n发现 {len(extreme)} 条极端值（|英语优势| > 50%）:")
        for _, row in extreme.iterrows():
            print(f"\n  {row['model']} - {row['family']}:")
            print(f"    官方语言平均距离: {row['native_mean']:.3f}")
            print(f"    英语平均距离: {row['english_mean']:.3f}")
            print(f"    英语优势: {row['english_advantage']:+.1f}%")
            print(f"    配对数: {row['n_pairs']}")


def analyze_open_vs_closed_source(df, results_df):
    """分析开源模型 vs 闭源模型的表现差异"""
    print("\n" + "=" * 80)
    print("📊 开源模型 vs 闭源模型对比分析")
    print("=" * 80)
    
    # 排除英语母语国家
    non_english = df[~df['is_english_native_country']].copy()
    
    # 为每个模型添加开源/闭源标签
    def get_source_type(model):
        if model in OPEN_SOURCE_MODELS:
            return '开源'
        elif model in CLOSED_SOURCE_MODELS:
            return '闭源'
        else:
            return '未知'
    
    results_df['source_type'] = results_df['model'].apply(get_source_type)
    
    # 1. 整体对比：平均文化距离
    print("\n1. 整体平均文化距离对比:")
    for source_type in ['开源', '闭源']:
        type_data = results_df[results_df['source_type'] == source_type]
        if len(type_data) == 0:
            continue
        
        # 加权平均
        total_native = (type_data['native_mean'] * type_data['n_pairs']).sum()
        total_english = (type_data['english_mean'] * type_data['n_pairs']).sum()
        total_pairs = type_data['n_pairs'].sum()
        
        if total_pairs > 0:
            avg_native = total_native / total_pairs
            avg_english = total_english / total_pairs
            avg_overall = (avg_native + avg_english) / 2
            eng_adv = (avg_native - avg_english) / avg_native * 100
            
            models_in_type = type_data['model'].unique()
            print(f"\n  {source_type}模型 ({len(models_in_type)}个):")
            print(f"    平均文化距离: {avg_overall:.2f}")
            print(f"    母语距离: {avg_native:.2f}, 英语距离: {avg_english:.2f}")
            print(f"    英语优势: {eng_adv:+.1f}%")
            print(f"    模型: {', '.join(sorted(models_in_type))}")
    
    # 2. 按语系对比
    print("\n2. 各语系英语优势对比:")
    families = ['闪米特语系', '斯拉夫语系', '汉藏语系', '罗曼语系', '日耳曼语系']
    
    comparison_data = []
    for family in families:
        row = {'语系': family}
        for source_type in ['开源', '闭源']:
            type_family_data = results_df[
                (results_df['source_type'] == source_type) & 
                (results_df['family'] == family)
            ]
            if len(type_family_data) > 0:
                total_native = (type_family_data['native_mean'] * type_family_data['n_pairs']).sum()
                total_english = (type_family_data['english_mean'] * type_family_data['n_pairs']).sum()
                total_pairs = type_family_data['n_pairs'].sum()
                
                if total_pairs > 0:
                    avg_native = total_native / total_pairs
                    avg_english = total_english / total_pairs
                    eng_adv = (avg_native - avg_english) / avg_native * 100
                    row[f'{source_type}_英语优势'] = eng_adv
                    row[f'{source_type}_样本数'] = total_pairs
        comparison_data.append(row)
    
    comparison_df = pd.DataFrame(comparison_data)
    print("\n  语系          开源英语优势  闭源英语优势  差异")
    print("  " + "-" * 50)
    for _, row in comparison_df.iterrows():
        open_adv = row.get('开源_英语优势', float('nan'))
        closed_adv = row.get('闭源_英语优势', float('nan'))
        diff = open_adv - closed_adv if not (pd.isna(open_adv) or pd.isna(closed_adv)) else float('nan')
        
        open_str = f"{open_adv:+.1f}%" if not pd.isna(open_adv) else "N/A"
        closed_str = f"{closed_adv:+.1f}%" if not pd.isna(closed_adv) else "N/A"
        diff_str = f"{diff:+.1f}%" if not pd.isna(diff) else "N/A"
        
        print(f"  {row['语系']:<10} {open_str:>12} {closed_str:>12} {diff_str:>8}")
    
    # 3. 单个模型排名
    print("\n3. 模型整体表现排名（按平均文化距离）:")
    model_stats = []
    for model in results_df['model'].unique():
        model_data = results_df[results_df['model'] == model]
        total_native = (model_data['native_mean'] * model_data['n_pairs']).sum()
        total_english = (model_data['english_mean'] * model_data['n_pairs']).sum()
        total_pairs = model_data['n_pairs'].sum()
        
        if total_pairs > 0:
            avg_native = total_native / total_pairs
            avg_english = total_english / total_pairs
            avg_overall = (avg_native + avg_english) / 2
            eng_adv = (avg_native - avg_english) / avg_native * 100
            source_type = get_source_type(model)
            
            model_stats.append({
                'model': model,
                'source_type': source_type,
                'avg_distance': avg_overall,
                'english_advantage': eng_adv,
                'n_pairs': total_pairs
            })
    
    model_stats_df = pd.DataFrame(model_stats).sort_values('avg_distance')
    
    print("\n  排名  模型                          类型    平均距离  英语优势")
    print("  " + "-" * 65)
    for i, (_, row) in enumerate(model_stats_df.iterrows(), 1):
        marker = "🟢" if row['source_type'] == '开源' else "🔵"
        print(f"  {i:>2}.  {row['model']:<28} {marker}{row['source_type']:<4} {row['avg_distance']:>6.2f}   {row['english_advantage']:+.1f}%")
    
    # 4. 统计汇总
    print("\n4. 统计汇总:")
    open_models = model_stats_df[model_stats_df['source_type'] == '开源']
    closed_models = model_stats_df[model_stats_df['source_type'] == '闭源']
    
    if len(open_models) > 0 and len(closed_models) > 0:
        print(f"\n  开源模型 ({len(open_models)}个):")
        print(f"    平均距离: {open_models['avg_distance'].mean():.2f} (标准差: {open_models['avg_distance'].std():.2f})")
        print(f"    最佳: {open_models.iloc[0]['model']} ({open_models.iloc[0]['avg_distance']:.2f})")
        print(f"    最差: {open_models.iloc[-1]['model']} ({open_models.iloc[-1]['avg_distance']:.2f})")
        
        print(f"\n  闭源模型 ({len(closed_models)}个):")
        print(f"    平均距离: {closed_models['avg_distance'].mean():.2f} (标准差: {closed_models['avg_distance'].std():.2f})")
        print(f"    最佳: {closed_models.iloc[0]['model']} ({closed_models.iloc[0]['avg_distance']:.2f})")
        print(f"    最差: {closed_models.iloc[-1]['model']} ({closed_models.iloc[-1]['avg_distance']:.2f})")
        
        # 差异分析
        diff = open_models['avg_distance'].mean() - closed_models['avg_distance'].mean()
        print(f"\n  差异分析:")
        print(f"    开源 vs 闭源平均距离差: {diff:+.2f}")
        if diff > 0:
            print(f"    结论: 闭源模型平均表现更好（距离更小）")
        else:
            print(f"    结论: 开源模型平均表现更好（距离更小）")
    
    return model_stats_df


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("模型-语系交叉分析")
    print("=" * 80)
    
    # 加载数据
    df = load_data()
    print(f"\n✅ 加载数据: {len(df)} 条记录")
    print(f"   模型数: {df['model'].nunique()}")
    print(f"   模型列表: {sorted(df['model'].unique())}")
    
    # 检查中国模型是否在数据中
    print(f"\n   中国模型检查:")
    for model in CHINESE_MODELS:
        count = len(df[df['model'] == model])
        print(f"     {model}: {count} 条记录")
    
    # 分析
    results_df = analyze_model_by_family(df)
    
    # 打印矩阵
    pivot = print_model_family_matrix(results_df)
    
    # 按来源国分析
    analyze_by_model_origin(results_df)
    
    # 中国模型在汉藏语系的表现
    print_chinese_models_hanzi(results_df)
    
    # 调试极端值
    debug_extreme_values(df, results_df)
    
    # 保存结果
    results_df.to_csv(OUTPUT_DIR / 'model_by_family_analysis.csv', index=False)
    pivot.to_csv(OUTPUT_DIR / 'model_family_matrix.csv')
    
    print(f"\n✅ 结果已保存到: {OUTPUT_DIR}")
    print("=" * 80)


if __name__ == '__main__':
    main()
