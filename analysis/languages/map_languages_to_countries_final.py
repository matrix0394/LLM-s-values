"""
基于country_values中的WVS数据重新分析
这才是正确的数据源
"""

import json

# 定义我们拥有的13种语言
OUR_LANGUAGES = {
    'English': ['en'],
    'Spanish': ['es'],
    'Arabic': ['ar'],
    'Russian': ['ru'],
    'Portuguese': ['pt'],
    'Japanese': ['ja'],
    'Korean': ['ko'],
    'French': ['fr'],
    'German': ['de'],
    'Italian': ['it'],
    'Chinese (Simplified)': ['zh'],
    'Chinese (Traditional - Hong Kong)': ['zh-HK'],
    'Chinese (Traditional - Taiwan)': ['zh-TW']
}

# 基于维基百科的各国官方语言
COUNTRY_LANGUAGES_WIKI = {
    'Albania': ['sq'],
    'Algeria': ['ar'],
    'Andorra': ['ca'],
    'Argentina': ['es'],
    'Armenia': ['hy'],
    'Australia': ['en'],
    'Austria': ['de'],
    'Azerbaijan': ['az'],
    'Bangladesh': ['bn'],
    'Belarus': ['be', 'ru'],
    'Belgium': ['nl', 'fr', 'de'],
    'Bolivia (Plurinational State of)': ['es'],
    'Bosnia and Herzegovina': ['bs', 'hr', 'sr'],
    'Brazil': ['pt'],
    'Bulgaria': ['bg'],
    'Burkina Faso': ['fr'],
    'Canada': ['en', 'fr'],
    'Chile': ['es'],
    'China': ['zh'],
    'Colombia': ['es'],
    'Croatia': ['hr'],
    'Cyprus': ['el', 'tr'],
    'Czechia': ['cs'],
    'Denmark': ['da'],
    'Ecuador': ['es'],
    'Egypt': ['ar'],
    'Estonia': ['et'],
    'Ethiopia': ['am'],
    'Finland': ['fi', 'sv'],
    'France': ['fr'],
    'Georgia': ['ka'],
    'Germany': ['de'],
    'Ghana': ['en'],
    'Greece': ['el'],
    'Guatemala': ['es'],
    'Haiti': ['fr', 'ht'],
    'Hong Kong': ['zh', 'zh-HK', 'en'],  # 中文（普通话+粤语）和英文都是官方语言
    'Hungary': ['hu'],
    'Iceland': ['is'],
    # 'India': ['hi', 'en'],  # 印度有22种官方语言，语言情况极其复杂，实验参考价值有限，故排除
    'Indonesia': ['id'],
    'Iran (Islamic Republic of)': ['fa'],
    'Iraq': ['ar'],
    'Ireland': ['en', 'ga'],
    'Italy': ['it'],
    'Japan': ['ja'],
    'Jordan': ['ar'],
    'Kazakhstan': ['kk', 'ru'],
    'Kenya': ['en', 'sw'],
    'Korea (the Republic of)': ['ko'],
    'Kuwait': ['ar'],
    'Kyrgyzstan': ['ky', 'ru'],
    'Latvia': ['lv'],
    'Lebanon': ['ar'],  # 只有阿拉伯语是官方语言，法语虽广泛使用但非官方
    'Libya': ['ar'],
    'Lithuania': ['lt'],
    'Luxembourg': ['lb', 'fr', 'de'],
    'Macao': ['zh', 'pt'],
    'Malaysia': ['ms', 'en'],  # 马来语是主要官方语言，英语在Sabah和Sarawak州是官方语言，且所有联邦法律必须用马来语和英语颁布
    'Maldives': ['dv'],
    'Mali': ['fr'],
    'Malta': ['mt', 'en'],
    'Mexico': ['es'],
    'Moldova (the Republic of)': ['ro'],
    'Mongolia': ['mn'],
    'Montenegro': ['cnr'],  # 黑山语（Montenegrin）是官方语言
    'Morocco': ['ar'],
    'Myanmar': ['my'],
    'Netherlands (the)': ['nl'],
    'New Zealand': ['en', 'mi'],
    'Nicaragua': ['es'],
    'Nigeria': ['en'],
    'Norway': ['no'],
    'Pakistan': ['ur', 'en'],
    'Palestine, State of': ['ar'],
    'Peru': ['es'],
    'Philippines (the)': ['en', 'tl'],
    'Poland': ['pl'],
    'Portugal': ['pt'],
    'Puerto Rico': ['es', 'en'],
    'Qatar': ['ar'],
    'Republic of North Macedonia': ['mk'],
    'Romania': ['ro'],
    'Russian Federation (the)': ['ru'],
    'Rwanda': ['rw', 'en', 'fr'],
    'Serbia': ['sr'],
    'Singapore': ['en', 'zh', 'ms', 'ta'],
    'Slovakia': ['sk'],
    'Slovenia': ['sl'],
    'South Africa': ['en', 'af', 'zu', 'xh'],
    'Spain': ['es'],
    'Sweden': ['sv'],
    'Switzerland': ['de', 'fr', 'it'],
    'Taiwan (Province of China)': ['zh-TW'],
    'Tajikistan': ['tg'],  # 只有塔吉克语是官方语言，俄语虽广泛使用但2009年后非官方
    'Thailand': ['th'],
    'Trinidad and Tobago': ['en'],
    'Tunisia': ['ar'],
    'Turkey': ['tr'],
    'Ukraine': ['uk'],
    'United Kingdom of Great Britain and Northern Ireland (the)': ['en'],
    'United States of America (the)': ['en'],
    'Uruguay': ['es'],
    'Uzbekistan': ['uz'],  # 只有乌兹别克语是官方语言，俄语虽广泛使用但非官方
    'Venezuela (Bolivarian Republic of)': ['es'],
    'Viet Nam': ['vi'],
    'Yemen': ['ar'],
    'Zambia': ['en'],
    'Zimbabwe': ['en']
}

def analyze_language_coverage():
    """基于country_values中的WVS数据分析语言覆盖"""
    
    # 读取country_values中的数据
    with open(r"e:\Code\value of LLM\LLM's values\data\country_values\country_scores_pca.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 提取所有有效国家（排除Country为null的）
    countries_wvs = []
    for item in data:
        if item.get('Country') and item['Country'] != 'null':
            countries_wvs.append(item['Country'])
    
    countries_wvs = sorted(set(countries_wvs))
    
    print(f"WVS country_values中的国家总数: {len(countries_wvs)}\n")
    
    # 为每种语言映射国家
    language_mapping = {}
    
    for lang_name, lang_codes in OUR_LANGUAGES.items():
        matched_countries = []
        
        for country in countries_wvs:
            if country in COUNTRY_LANGUAGES_WIKI:
                country_langs = COUNTRY_LANGUAGES_WIKI[country]
                if any(code in country_langs for code in lang_codes):
                    matched_countries.append(country)
        
        language_mapping[lang_name] = matched_countries
    
    # 打印结果
    print("=" * 80)
    print("13种语言在WVS国家中的对应关系")
    print("=" * 80)
    
    total_covered = set()
    
    for lang_name, countries in sorted(language_mapping.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"\n【{lang_name}】 - 对应 {len(countries)} 个国家:")
        for i, country in enumerate(countries, 1):
            print(f"  {i}. {country}")
        total_covered.update(countries)
    
    # 统计
    print("\n" + "=" * 80)
    print(f"总计覆盖国家数: {len(total_covered)} / {len(countries_wvs)}")
    print(f"覆盖率: {len(total_covered) / len(countries_wvs) * 100:.1f}%")
    
    # 未覆盖国家
    uncovered = set(countries_wvs) - total_covered
    if uncovered:
        print(f"\n未覆盖的国家 ({len(uncovered)}个):")
        for i, country in enumerate(sorted(uncovered), 1):
            official_lang = COUNTRY_LANGUAGES_WIKI.get(country, ['未知'])
            print(f"  {i}. {country} (官方语言: {', '.join(official_lang)})")
    
    # 保存结果
    output = {
        'source': 'WVS country_values (country_scores_pca.json)',
        'total_countries': len(countries_wvs),
        'covered_countries': len(total_covered),
        'coverage_rate': round(len(total_covered) / len(countries_wvs) * 100, 2),
        'languages': language_mapping,
        'uncovered_countries': sorted(list(uncovered)),
        'all_wvs_countries': countries_wvs
    }
    
    output_path = r"e:\Code\value of LLM\LLM's values\results\analysis\language\语言覆盖数据.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到: {output_path}")
    
    return output

if __name__ == '__main__':
    analyze_language_coverage()
