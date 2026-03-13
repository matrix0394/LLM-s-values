"""
只更新Excel中的数据值，不修改格式
"""

import json
from openpyxl import load_workbook

print("="*80)
print("更新Excel数据（不改格式）")
print("="*80)
print()

# 读取JSON数据
with open(r"e:\Code\value of LLM\LLM's values\results\analysis\language\语言覆盖汇报数据.json", 'r', encoding='utf-8') as f:
    data = json.load(f)

# 加载现有Excel文件
excel_path = r"e:\Code\value of LLM\LLM's values\results\analysis\language\语言覆盖统计.xlsx"
try:
    wb = load_workbook(excel_path)
    print(f"✅ 已加载Excel文件: 语言覆盖统计.xlsx")
except FileNotFoundError:
    print(f"❌ 文件不存在，将创建新文件")
    print(f"   请先关闭Excel文件，然后运行: python analysis\\languages\\add_population_to_report.py")
    exit(1)

# 1. 更新"总览"工作表
ws = wb['总览']
print("\n更新【总览】工作表...")

# 找到并更新统计卡片的值
# 第一行统计卡片在第3-4行
# 第二行统计卡片（人口数据）在第5-6行

# 总人口(百万) - 通常在第5行第1列
ws.cell(6, 1).value = f"{data['report_metadata']['total_population_million']:,.1f}"
print(f"  - 总人口: {data['report_metadata']['total_population_million']:.1f}百万")

# 已覆盖人口(百万) - 第5行第3列
ws.cell(6, 3).value = f"{data['report_metadata']['covered_population_million']:,.1f}"
print(f"  - 已覆盖人口: {data['report_metadata']['covered_population_million']:.1f}百万")

# 未覆盖人口(百万) - 第5行第5列  
ws.cell(6, 5).value = f"{data['report_metadata']['uncovered_population_million']:,.1f}"
print(f"  - 未覆盖人口: {data['report_metadata']['uncovered_population_million']:.1f}百万")

# 人口覆盖率 - 第5行第7列
ws.cell(6, 7).value = data['report_metadata']['population_coverage_rate']
print(f"  - 人口覆盖率: {data['report_metadata']['population_coverage_rate']}")

# 2. 更新"已覆盖国家"工作表
ws = wb['已覆盖国家']
print("\n更新【已覆盖国家】工作表...")

# 按国家数降序排列语言
lang_list = []
for lang_en, lang_data in data['covered_by_language'].items():
    lang_list.append((lang_en, lang_data, lang_data['country_count']))
lang_list.sort(key=lambda x: x[2], reverse=True)

# 从第3行开始更新数据
row = 3
updated_countries = 0
for lang_en, lang_data, _ in lang_list:
    countries = sorted(lang_data['countries'], key=lambda x: x['name_en'])
    
    for i, country in enumerate(countries):
        if i == 0:
            # 更新语言信息（第1-4列）
            ws.cell(row, 1).value = lang_en
            ws.cell(row, 2).value = lang_data['language_name_zh']
            ws.cell(row, 3).value = lang_data['country_count']
            ws.cell(row, 4).value = lang_data['percentage']
        
        # 更新国家信息（第5-8列）
        ws.cell(row, 5).value = country['name_en']
        ws.cell(row, 6).value = country['name_zh']
        ws.cell(row, 7).value = f"{country['population_million']:.1f}"
        ws.cell(row, 8).value = country['cultural_region']
        
        row += 1
        updated_countries += 1

print(f"  - 已更新 {updated_countries} 个国家的数据")

# 3. 更新"未覆盖国家"工作表
ws = wb['未覆盖国家']
print("\n更新【未覆盖国家】工作表...")

# 从第3行开始更新数据
row = 3
updated_uncovered = 0
for lang_data in data['uncovered_by_language']:
    for i, country in enumerate(lang_data['countries']):
        if i == 0:
            # 更新语言信息（第1-6列）
            ws.cell(row, 1).value = lang_data['language']
            ws.cell(row, 2).value = lang_data['language_zh']
            ws.cell(row, 3).value = lang_data['language_code']
            ws.cell(row, 4).value = lang_data['country_count']
            ws.cell(row, 5).value = f"{lang_data['total_population_million']:.1f}"
            ws.cell(row, 6).value = lang_data.get('note', '')
        
        # 更新国家信息（第7-10列）
        ws.cell(row, 7).value = country['name_en']
        ws.cell(row, 8).value = country['name_zh']
        ws.cell(row, 9).value = f"{country['population_million']:.1f}"
        ws.cell(row, 10).value = country['cultural_region']
        
        row += 1
        updated_uncovered += 1

print(f"  - 已更新 {updated_uncovered} 个未覆盖国家的数据")

# 保存Excel
wb.save(excel_path)

print()
print("="*80)
print("✅ Excel数据更新完成！")
print("="*80)
print()
print(f"📁 文件: {excel_path}")
print()
print("💡 更新内容:")
print(f"  - 总人口: {data['report_metadata']['total_population_million']:.1f}百万 ({data['report_metadata']['total_population_million']/1000:.2f}十亿)")
print(f"  - 人口覆盖率: {data['report_metadata']['population_coverage_rate']}")
print(f"  - 已覆盖国家: {updated_countries}个")
print(f"  - 未覆盖国家: {updated_uncovered}个")
print()
print("📝 说明: 只更新了数据值，保留了所有格式设置")
print()
