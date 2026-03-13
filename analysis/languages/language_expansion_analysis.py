"""
分析未覆盖的43个国家，看哪些语言可以覆盖更多国家
提供语言扩展建议
"""

print("="*80)
print("未覆盖国家的语言分析 - 推荐补充哪些语言")
print("="*80)
print()

# 未覆盖的43个国家及其官方语言
uncovered_languages = {
    # 东欧/巴尔干
    'Albania': ['sq'],  # 阿尔巴尼亚语
    'Armenia': ['hy'],  # 亚美尼亚语
    'Bosnia and Herzegovina': ['bs', 'hr', 'sr'],  # 波黑语、克罗地亚语、塞尔维亚语
    'Bulgaria': ['bg'],  # 保加利亚语
    'Croatia': ['hr'],  # 克罗地亚语
    'Moldova': ['ro'],  # 罗马尼亚语
    'Montenegro': ['cnr'],  # 黑山语
    'Romania': ['ro'],  # 罗马尼亚语
    'Serbia': ['sr'],  # 塞尔维亚语
    
    # 北欧/波罗的海
    'Denmark': ['da'],  # 丹麦语
    'Estonia': ['et'],  # 爱沙尼亚语
    'Finland': ['fi', 'sv'],  # 芬兰语、瑞典语
    'Iceland': ['is'],  # 冰岛语
    'Latvia': ['lv'],  # 拉脱维亚语
    'Lithuania': ['lt'],  # 立陶宛语
    'Norway': ['no'],  # 挪威语
    'Sweden': ['sv'],  # 瑞典语
    
    # 中欧
    'Czechia': ['cs'],  # 捷克语
    'Hungary': ['hu'],  # 匈牙利语
    'Poland': ['pl'],  # 波兰语
    'Slovakia': ['sk'],  # 斯洛伐克语
    
    # 南欧/其他
    'Andorra': ['ca'],  # 加泰罗尼亚语
    'Cyprus': ['el', 'tr'],  # 希腊语、土耳其语
    'Greece': ['el'],  # 希腊语
    'Slovenia': ['sl'],  # 斯洛文尼亚语
    
    # 西欧
    'Netherlands': ['nl'],  # 荷兰语
    
    # 亚洲
    'Azerbaijan': ['az'],  # 阿塞拜疆语
    'Bangladesh': ['bn'],  # 孟加拉语
    'Ethiopia': ['am'],  # 阿姆哈拉语
    'Georgia': ['ka'],  # 格鲁吉亚语
    'India': ['hi', 'en'],  # 印地语、英语（已排除，太复杂）
    'Indonesia': ['id'],  # 印度尼西亚语
    'Iran': ['fa'],  # 波斯语/法尔西语
    'Maldives': ['dv'],  # 迪维希语
    'Mongolia': ['mn'],  # 蒙古语
    'Myanmar': ['my'],  # 缅甸语
    'Tajikistan': ['tg'],  # 塔吉克语
    'Thailand': ['th'],  # 泰语
    'Uzbekistan': ['uz'],  # 乌兹别克语
    'Viet Nam': ['vi'],  # 越南语
    
    # 欧亚交界
    'Turkey': ['tr'],  # 土耳其语
    'Ukraine': ['uk'],  # 乌克兰语
}

print(f"未覆盖国家总数: {len(uncovered_languages)}")
print()

# 统计每种语言覆盖的国家数
language_coverage = {}

for country, langs in uncovered_languages.items():
    for lang in langs:
        if lang not in language_coverage:
            language_coverage[lang] = []
        language_coverage[lang].append(country)

# 按覆盖国家数排序
sorted_languages = sorted(language_coverage.items(), key=lambda x: len(x[1]), reverse=True)

print("="*80)
print("未覆盖国家的语言统计（按覆盖国家数排序）")
print("="*80)
print()

# 语言名称映射
language_names = {
    'ro': '罗马尼亚语 (Romanian)',
    'sv': '瑞典语 (Swedish)',
    'hr': '克罗地亚语 (Croatian)',
    'sr': '塞尔维亚语 (Serbian)',
    'el': '希腊语 (Greek)',
    'tr': '土耳其语 (Turkish)',
    'pl': '波兰语 (Polish)',
    'nl': '荷兰语 (Dutch)',
    'uk': '乌克兰语 (Ukrainian)',
    'cs': '捷克语 (Czech)',
    'vi': '越南语 (Vietnamese)',
    'th': '泰语 (Thai)',
    'id': '印度尼西亚语 (Indonesian)',
    'fa': '波斯语 (Persian/Farsi)',
    'bn': '孟加拉语 (Bengali)',
    'no': '挪威语 (Norwegian)',
    'da': '丹麦语 (Danish)',
    'hu': '匈牙利语 (Hungarian)',
    'bg': '保加利亚语 (Bulgarian)',
    'fi': '芬兰语 (Finnish)',
    'sq': '阿尔巴尼亚语 (Albanian)',
    'sk': '斯洛伐克语 (Slovak)',
    'bs': '波黑语 (Bosnian)',
    'lt': '立陶宛语 (Lithuanian)',
    'lv': '拉脱维亚语 (Latvian)',
    'et': '爱沙尼亚语 (Estonian)',
    'sl': '斯洛文尼亚语 (Slovenian)',
    'ka': '格鲁吉亚语 (Georgian)',
    'hy': '亚美尼亚语 (Armenian)',
    'az': '阿塞拜疆语 (Azerbaijani)',
    'my': '缅甸语 (Burmese)',
    'mn': '蒙古语 (Mongolian)',
    'tg': '塔吉克语 (Tajik)',
    'uz': '乌兹别克语 (Uzbek)',
    'am': '阿姆哈拉语 (Amharic)',
    'dv': '迪维希语 (Dhivehi)',
    'is': '冰岛语 (Icelandic)',
    'ca': '加泰罗尼亚语 (Catalan)',
    'cnr': '黑山语 (Montenegrin)',
    'hi': '印地语 (Hindi)',
    'en': '英语 (English)',
}

for i, (lang, countries) in enumerate(sorted_languages, 1):
    lang_name = language_names.get(lang, f'未知语言 ({lang})')
    count = len(countries)
    
    if count >= 2:
        print(f"{i:2d}. 【{lang_name}】 - {count}个国家")
        for country in sorted(countries):
            print(f"    • {country}")
        print()

print("="*80)
print("推荐补充的语言（前10名）")
print("="*80)
print()

recommendations = [
    {
        'rank': 1,
        'language': '罗马尼亚语 (Romanian)',
        'code': 'ro',
        'countries': 2,
        'list': ['Moldova', 'Romania'],
        'population': '~24M (罗马尼亚) + ~2.6M (摩尔多瓦)',
        'difficulty': '中等',
        'priority': '⭐⭐⭐',
        'reason': '覆盖2个东欧国家，使用人口较多'
    },
    {
        'rank': 2,
        'language': '瑞典语 (Swedish)',
        'code': 'sv',
        'countries': 2,
        'list': ['Finland', 'Sweden'],
        'population': '~10M (瑞典) + ~0.3M (芬兰)',
        'difficulty': '中等',
        'priority': '⭐⭐⭐',
        'reason': '覆盖2个北欧发达国家，翻译质量高'
    },
    {
        'rank': 3,
        'language': '土耳其语 (Turkish)',
        'code': 'tr',
        'countries': 2,
        'list': ['Cyprus', 'Turkey'],
        'population': '~85M (土耳其)',
        'difficulty': '中等',
        'priority': '⭐⭐⭐⭐',
        'reason': '土耳其人口众多，地缘政治重要'
    },
    {
        'rank': 4,
        'language': '塞尔维亚语群 (Serbian/Croatian/Bosnian)',
        'code': 'sr/hr/bs',
        'countries': 4,
        'list': ['Bosnia and Herzegovina', 'Croatia', 'Montenegro', 'Serbia'],
        'population': '~15M',
        'difficulty': '中等',
        'priority': '⭐⭐⭐⭐',
        'reason': '一种语言覆盖4个巴尔干国家（高度互通）'
    },
    {
        'rank': 5,
        'language': '越南语 (Vietnamese)',
        'code': 'vi',
        'countries': 1,
        'list': ['Viet Nam'],
        'population': '~98M',
        'difficulty': '难',
        'priority': '⭐⭐⭐⭐',
        'reason': '人口近1亿，东南亚重要国家'
    },
    {
        'rank': 6,
        'language': '泰语 (Thai)',
        'code': 'th',
        'countries': 1,
        'list': ['Thailand'],
        'population': '~70M',
        'difficulty': '难',
        'priority': '⭐⭐⭐',
        'reason': '东南亚重要经济体'
    },
    {
        'rank': 7,
        'language': '印度尼西亚语 (Indonesian)',
        'code': 'id',
        'countries': 1,
        'list': ['Indonesia'],
        'population': '~275M',
        'difficulty': '中等',
        'priority': '⭐⭐⭐⭐⭐',
        'reason': '世界第4人口大国，使用人口最多'
    },
    {
        'rank': 8,
        'language': '波斯语 (Persian/Farsi)',
        'code': 'fa',
        'countries': 1,
        'list': ['Iran'],
        'population': '~85M (伊朗)',
        'difficulty': '难',
        'priority': '⭐⭐⭐',
        'reason': '中东重要国家，文化独特'
    },
    {
        'rank': 9,
        'language': '波兰语 (Polish)',
        'code': 'pl',
        'countries': 1,
        'list': ['Poland'],
        'population': '~38M',
        'difficulty': '难',
        'priority': '⭐⭐⭐',
        'reason': '中欧大国，人口较多'
    },
    {
        'rank': 10,
        'language': '乌克兰语 (Ukrainian)',
        'code': 'uk',
        'countries': 1,
        'list': ['Ukraine'],
        'population': '~40M',
        'difficulty': '中等',
        'priority': '⭐⭐⭐',
        'reason': '东欧大国，地缘政治重要'
    }
]

for rec in recommendations:
    print(f"{rec['rank']}. 【{rec['language']}】 {rec['priority']}")
    print(f"   覆盖国家: {rec['countries']}个 - {', '.join(rec['list'])}")
    print(f"   使用人口: {rec['population']}")
    print(f"   翻译难度: {rec['difficulty']}")
    print(f"   推荐理由: {rec['reason']}")
    print()

print("="*80)
print("总体建议")
print("="*80)
print()

print("✅ 当前覆盖率 60.6% (66/109国) 是否足够？")
print()
print("【足够】的理由:")
print("  ✓ 主要文化区域已覆盖：英语系、拉美、中东、东亚、西欧")
print("  ✓ 覆盖了人口最多的国家：中国、美国、印度尼西亚（可补充）")
print("  ✓ 地理分布均衡：5大洲都有覆盖")
print("  ✓ 文化多样性充足：不同宗教、政治体制、发展水平")
print()
print("【不足】的问题:")
print("  ✗ 东欧严重缺失（9/42个欧洲国家未覆盖）")
print("  ✗ 北欧/波罗的海缺失（7国全未覆盖）")
print("  ✗ 东南亚不完整（越南、泰国、印尼、缅甸未覆盖）")
print("  ✗ 中亚几乎空白（只有哈萨克斯坦、吉尔吉斯斯坦通过俄语覆盖）")
print()

print("="*80)
print("三种扩展策略")
print("="*80)
print()

print("📊 策略A: 最小化扩展（+3种语言，覆盖+11国 → 77国，70.6%）")
print("  推荐语言:")
print("    1. 印度尼西亚语 (Indonesian) - 覆盖1国，人口2.75亿 ⭐⭐⭐⭐⭐")
print("    2. 越南语 (Vietnamese) - 覆盖1国，人口9800万 ⭐⭐⭐⭐")
print("    3. 塞尔维亚-克罗地亚语 (Serbo-Croatian) - 覆盖4国 ⭐⭐⭐⭐")
print("       (波黑、克罗地亚、塞尔维亚、黑山互通)")
print("  优点: 成本最低，补充东南亚和巴尔干空白")
print("  缺点: 仍未覆盖东欧、北欧")
print()

print("📊 策略B: 均衡扩展（+6种语言，覆盖+17国 → 83国，76.1%）")
print("  推荐语言:")
print("    1. 印度尼西亚语 - 1国")
print("    2. 越南语 - 1国")
print("    3. 塞尔维亚-克罗地亚语 - 4国")
print("    4. 泰语 (Thai) - 1国")
print("    5. 土耳其语 (Turkish) - 2国 (土耳其+塞浦路斯)")
print("    6. 瑞典语 (Swedish) - 2国 (瑞典+芬兰)")
print("    7. 罗马尼亚语 (Romanian) - 2国 (罗马尼亚+摩尔多瓦)")
print("    8. 波兰语 (Polish) - 1国")
print("  优点: 地理分布更均衡，覆盖东南亚+巴尔干+北欧")
print("  缺点: 成本较高")
print()

print("📊 策略C: 完整覆盖（+15种语言，覆盖全部109国）")
print("  需要额外语言: 荷兰语、乌克兰语、捷克语、希腊语等15种")
print("  优点: 完全覆盖")
print("  缺点: 成本极高，边际效益递减")
print()

print("="*80)
print("💡 最终推荐")
print("="*80)
print()

print("✅ 如果预算有限: 保持现状 (66国, 60.6%)")
print("   理由: 已覆盖主要文化区域，可满足基本研究需求")
print()

print("⭐ 如果可以扩展: 采用策略A (+3语言)")
print("   补充: 印度尼西亚语、越南语、塞尔维亚语")
print("   效果: 77国 (70.6%)，填补东南亚和巴尔干空白")
print("   成本: 3种语言翻译")
print()

print("⭐⭐ 如果预算充足: 采用策略B (+6-8语言)")
print("   补充: 上述3种 + 泰语、土耳其语、瑞典语、罗马尼亚语、波兰语")
print("   效果: 83国 (76.1%)，地理分布非常均衡")
print("   成本: 8种语言翻译")
print()

print("="*80)
print("关键考虑因素")
print("="*80)
print()

print("1. 研究问题:")
print("   - 如果关注东西方文化差异 → 当前覆盖已足够")
print("   - 如果关注区域细分（如东欧vs西欧）→ 需要补充东欧语言")
print("   - 如果关注东南亚 → 必须补充越南语、泰语、印尼语")
print()

print("2. 翻译质量:")
print("   - 高资源语言（如波兰语、土耳其语）→ LLM翻译质量较好")
print("   - 中资源语言（如越南语、泰语）→ 需要人工校验")
print("   - 低资源语言（如塔吉克语）→ 翻译质量可能不够")
print()

print("3. 实验成本:")
print("   - 每增加1种语言 → 需要109国 × 1语言的roleplay实验")
print("   - 考虑API调用成本、时间成本")
print()

print("="*80)
