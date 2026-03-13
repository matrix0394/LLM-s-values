#!/usr/bin/env python3
"""
按语系分层分析 - 使用正确的语言学分类
语系分类基于语言学标准，而非地理/文化分类
"""
import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

# 输出目录
OUTPUT_DIR = Path('results/analysis/language_family_analysis')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 正确的语系分类（基于语言学）
LANGUAGE_FAMILIES = {
    '日耳曼语系': {
        'languages': ['en', 'de'],
        'description': 'Germanic (印欧语系-日耳曼语族)',
        'countries_example': '德国、奥地利、瑞士(德语区)'
    },
    '罗曼语系': {
        'languages': ['es', 'fr', 'it', 'pt'],
        'description': 'Romance (印欧语系-罗曼语族)',
        'countries_example': '西班牙、法国、意大利、葡萄牙、拉美国家'
    },
    '斯拉夫语系': {
        'languages': ['ru'],
        'description': 'Slavic (印欧语系-斯拉夫语族)',
        'countries_example': '俄罗斯、乌克兰、白俄罗斯'
    },
    '闪米特语系': {
        'languages': ['ar'],
        'description': 'Semitic (亚非语系-闪米特语族)',
        'countries_example': '阿拉伯国家（埃及、沙特、约旦等）'
    },
    '汉藏语系': {
        'languages': ['zh-cn', 'zh-tw', 'zh-hk'],
        'description': 'Sino-Tibetan (汉藏语系-汉语族)',
        'countries_example': '中国大陆、台湾、香港、澳门'
    },
    '日本语系': {
        'languages': ['ja'],
        'description': 'Japonic (孤立语言)',
        'countries_example': '日本'
    },
    '韩语系': {
        'languages': ['ko'],
        'description': 'Koreanic (孤立语言)',
        'countries_example': '韩国'
    }
}

# 语言到语系的映射
LANG_TO_FAMILY = {}
for family, info in LANGUAGE_FAMILIES.items():
    for lang in info['languages']:
        LANG_TO_FAMILY[lang] = family


def load_data():
    """加载数据"""
    df = pd.read_csv('results/roleplay_multilingual/cultural_distance_analysis.csv')
    
    # 排除低质量模型
    bad_models = ['qwen3-1.7b']
    df = df[~df['model'].isin(bad_models)]
    
    return df


def analyze_by_language_family(df):
    """按语系分析英语优势"""
    print("\n" + "=" * 70)
    print("📊 按语系分析英语优势（使用正确的语言学分类）")
    print("=" * 70)
    
    # 排除英语母语国家
    non_english = df[~df['is_english_native_country']]
    
    results = []
    
    for family, info in LANGUAGE_FAMILIES.items():
        langs = info['languages']
        
        # 跳过英语（作为基准）
        if family == '日耳曼语系':
            # 日耳曼语系只分析德语，不包括英语
            langs = ['de']
        
        family_data = non_english[non_english['native_language'].isin(langs)]
        if len(family_data) == 0:
            continue
        
        # 收集配对数据
        paired = []
        for country in family_data['country'].unique():
            country_data = family_data[family_data['country'] == country]
            native_lang = country_data['native_language'].iloc[0]
            
            for model in country_data['model'].unique():
                model_data = country_data[country_data['model'] == model]
                native_dist = model_data[model_data['language'] == native_lang]['cultural_distance'].values
                english_dist = model_data[model_data['is_english']]['cultural_distance'].values
                
                if len(native_dist) > 0 and len(english_dist) > 0:
                    paired.append({
                        'country': country,
                        'model': model,
                        'native_lang': native_lang,
                        'native_dist': native_dist[0],
                        'english_dist': english_dist[0],
                        'diff': native_dist[0] - english_dist[0]  # 正值=英语更好
                    })
        
        if len(paired) < 5:
            print(f"\n⚠️ {family}: 样本数不足 ({len(paired)})")
            continue
        
        paired_df = pd.DataFrame(paired)
        native_arr = paired_df['native_dist'].values
        english_arr = paired_df['english_dist'].values
        diff = paired_df['diff'].values
        
        # 配对t检验
        t_stat, p_value = stats.ttest_rel(native_arr, english_arr)
        
        # 计算英语优势百分比
        english_advantage_pct = (native_arr.mean() - english_arr.mean()) / native_arr.mean() * 100
        
        # 显著性标记
        if p_value < 0.001:
            sig = "***"
        elif p_value < 0.01:
            sig = "**"
        elif p_value < 0.05:
            sig = "*"
        else:
            sig = ""
        
        eng_better_count = (diff > 0).sum()
        
        result = {
            'family': family,
            'description': info['description'],
            'languages': ', '.join(langs),
            'n_pairs': len(paired),
            'n_countries': paired_df['country'].nunique(),
            'native_mean': native_arr.mean(),
            'native_std': native_arr.std(),
            'english_mean': english_arr.mean(),
            'english_std': english_arr.std(),
            'diff_mean': diff.mean(),
            'english_advantage_pct': english_advantage_pct,
            'eng_better_count': eng_better_count,
            'eng_better_pct': eng_better_count / len(paired) * 100,
            't_stat': t_stat,
            'p_value': p_value,
            'significance': sig
        }
        results.append(result)
        
        # 打印结果
        print(f"\n{'='*50}")
        print(f"📌 {family} ({info['description']})")
        print(f"   语言: {', '.join(langs)}")
        print(f"   国家示例: {info['countries_example']}")
        print(f"{'='*50}")
        print(f"   配对数: {len(paired)} (来自 {paired_df['country'].nunique()} 个国家)")
        print(f"   官方语言距离: {native_arr.mean():.3f} ± {native_arr.std():.3f}")
        print(f"   英语距离: {english_arr.mean():.3f} ± {english_arr.std():.3f}")
        print(f"   英语优势: {english_advantage_pct:+.1f}%")
        print(f"   英语更好比例: {eng_better_count}/{len(paired)} ({eng_better_count/len(paired)*100:.1f}%)")
        print(f"   t检验: t={t_stat:.2f}, p={p_value:.4f} {sig}")
    
    return pd.DataFrame(results)


def create_summary_table(results_df):
    """创建汇总表格"""
    print("\n" + "=" * 70)
    print("📊 语系分析汇总表")
    print("=" * 70)
    
    # 按英语优势排序
    results_df = results_df.sort_values('english_advantage_pct', ascending=False)
    
    print(f"\n{'语系':<12} {'样本':<6} {'官方语言距离':<12} {'英语距离':<10} {'英语优势':<10} {'显著性':<8}")
    print("-" * 70)
    
    for _, row in results_df.iterrows():
        print(f"{row['family']:<12} {row['n_pairs']:<6} "
              f"{row['native_mean']:.2f}±{row['native_std']:.2f}    "
              f"{row['english_mean']:.2f}±{row['english_std']:.2f}  "
              f"{row['english_advantage_pct']:+.1f}%      "
              f"{row['significance']:<8}")
    
    print("-" * 70)
    print("显著性: *** p<0.001, ** p<0.01, * p<0.05")
    
    return results_df


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("语系分析 - 使用正确的语言学分类")
    print("=" * 70)
    
    # 打印语系分类说明
    print("\n📚 语系分类说明:")
    print("-" * 50)
    for family, info in LANGUAGE_FAMILIES.items():
        print(f"  {family}: {', '.join(info['languages'])} - {info['description']}")
    
    print("\n⚠️ 注意:")
    print("  - 日语和韩语是孤立语言，与汉语无亲缘关系")
    print("  - 英语和德语同属日耳曼语系，但英语作为基准不参与比较")
    print("  - 俄语属于斯拉夫语系，不是独立语系")
    
    # 加载数据
    df = load_data()
    print(f"\n✅ 加载数据: {len(df)} 条记录")
    
    # 按语系分析
    results_df = analyze_by_language_family(df)
    
    # 创建汇总表
    results_df = create_summary_table(results_df)
    
    # 保存结果
    results_df.to_csv(OUTPUT_DIR / 'language_family_analysis.csv', index=False)
    print(f"\n✅ 结果已保存到: {OUTPUT_DIR / 'language_family_analysis.csv'}")
    
    # 生成PPT用的简化表格
    print("\n" + "=" * 70)
    print("📊 PPT用表格（按英语优势排序）")
    print("=" * 70)
    print(f"\n| 语系 | 样本 | 官方语言距离 | 英语距离 | 英语优势 | 显著性 |")
    print("|------|------|-------------|---------|---------|--------|")
    for _, row in results_df.iterrows():
        print(f"| {row['family']} | {row['n_pairs']} | {row['native_mean']:.2f} | {row['english_mean']:.2f} | {row['english_advantage_pct']:+.1f}% | {row['significance']} |")
    
    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()
