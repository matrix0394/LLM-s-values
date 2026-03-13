"""
将人口数据添加到汇报材料中
1. 更新JSON数据
2. 重新生成Excel（只更新数据，不改格式）
3. 重新生成HTML
"""

import json
import os
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# 人口数据（单位：百万，2024年估计）
population_data = {
    'Australia': 26.6, 'Canada': 39.7, 'Ghana': 33.5, 'Hong Kong': 7.5, 'Ireland': 5.2,
    'Kenya': 55.1, 'Malaysia': 34.3, 'Malta': 0.5, 'New Zealand': 5.2, 'Nigeria': 223.8,
    'Pakistan': 240.5, 'Philippines': 117.3, 'Puerto Rico': 3.2, 'Rwanda': 14.1, 'Singapore': 6.0,
    'South Africa': 60.4, 'Trinidad and Tobago': 1.5, 'United Kingdom': 67.7, 'United States': 341.8,
    'Zambia': 20.6, 'Zimbabwe': 16.7, 'Argentina': 46.2, 'Bolivia': 12.4, 'Chile': 19.6,
    'Colombia': 52.1, 'Ecuador': 18.2, 'Guatemala': 17.1, 'Mexico': 128.5, 'Nicaragua': 7.0,
    'Peru': 34.4, 'Spain': 47.4, 'Uruguay': 3.4, 'Venezuela': 28.8, 'Algeria': 45.6,
    'Egypt': 112.7, 'Iraq': 45.5, 'Jordan': 11.3, 'Kuwait': 4.3, 'Lebanon': 5.5,
    'Libya': 6.9, 'Morocco': 37.8, 'Palestine': 5.5, 'Qatar': 2.7, 'Tunisia': 12.5,
    'Yemen': 34.5, 'Belgium': 11.7, 'Burkina Faso': 23.3, 'France': 64.8, 'Haiti': 11.7,
    'Luxembourg': 0.7, 'Mali': 23.3, 'Switzerland': 8.8, 'Austria': 9.0, 'Germany': 83.3,
    'Belarus': 9.1, 'Kazakhstan': 19.6, 'Kyrgyzstan': 7.0, 'Russia': 144.4, 'China': 1425.7,
    'Macao': 0.7, 'Brazil': 216.4, 'Portugal': 10.3, 'Italy': 58.9, 'Japan': 123.3,
    'Korea': 51.7, 'Taiwan': 23.6, 'Albania': 2.8, 'Andorra': 0.08, 'Armenia': 2.8,
    'Azerbaijan': 10.4, 'Bangladesh': 173.6, 'Bosnia and Herzegovina': 3.2, 'Bulgaria': 6.4,
    'Croatia': 3.9, 'Cyprus': 1.3, 'Czechia': 10.5, 'Denmark': 5.9, 'Estonia': 1.4,
    'Ethiopia': 126.5, 'Finland': 5.6, 'Georgia': 3.7, 'Greece': 10.3, 'Hungary': 9.6,
    'Iceland': 0.4, 'India': 1428.6, 'Indonesia': 277.5, 'Iran': 89.2, 'Latvia': 1.8,
    'Lithuania': 2.7, 'Maldives': 0.5, 'Moldova': 3.0, 'Mongolia': 3.4, 'Montenegro': 0.6,
    'Myanmar': 54.6, 'Netherlands': 17.6, 'Norway': 5.5, 'Poland': 37.7, 'North Macedonia': 2.1,
    'Romania': 19.0, 'Serbia': 6.7, 'Slovakia': 5.4, 'Slovenia': 2.1, 'Sweden': 10.5,
    'Tajikistan': 10.1, 'Thailand': 71.8, 'Turkey': 85.8, 'Ukraine': 37.0, 'Uzbekistan': 35.2,
    'Viet Nam': 98.9
}

def normalize_country_name(name):
    """标准化国家名称"""
    # 优先使用精确匹配，然后才使用模糊匹配
    name_mapping = {
        'Korea': 'Korea',
        'South Korea': 'Korea',
        'Russia': 'Russia',
        'Russian Federation': 'Russia',
    }
    
    if name in name_mapping:
        return name_mapping[name]
    elif 'United Kingdom' in name:
        return 'United Kingdom'
    elif 'United States' in name:
        return 'United States'
    elif 'Korea' in name and 'North' not in name:
        return 'Korea'
    elif 'Philippines' in name:
        return 'Philippines'
    elif 'Bolivia' in name:
        return 'Bolivia'
    elif 'Venezuela' in name:
        return 'Venezuela'
    elif 'Iran' in name:
        return 'Iran'
    elif 'Moldova' in name:
        return 'Moldova'
    elif 'North Macedonia' in name:
        return 'North Macedonia'
    elif 'Taiwan' in name:
        return 'Taiwan'
    return name

print("="*80)
print("添加人口数据到汇报材料")
print("="*80)
print()

# 1. 读取并更新JSON数据
with open(r"e:\Code\value of LLM\LLM's values\results\analysis\language\语言覆盖汇报数据.json", 'r', encoding='utf-8') as f:
    data = json.load(f)

# 添加人口数据到已覆盖国家
total_covered_pop = 0
unique_covered = set()

for lang_en, lang_data in data['covered_by_language'].items():
    lang_pop = 0
    for country in lang_data['countries']:
        country_name = normalize_country_name(country['name_en'])
        pop = population_data.get(country_name, 0)
        country['population_million'] = pop
        
        if country_name not in unique_covered:
            total_covered_pop += pop
            unique_covered.add(country_name)
        lang_pop += pop
    
    lang_data['total_population_million'] = round(lang_pop, 1)

# 添加人口数据到未覆盖国家
total_uncovered_pop = 0
unique_uncovered = set()

for lang_data in data['uncovered_by_language']:
    lang_pop = 0
    for country in lang_data['countries']:
        country_name = normalize_country_name(country['name_en'])
        pop = population_data.get(country_name, 0)
        country['population_million'] = pop
        
        if country_name not in unique_uncovered:
            total_uncovered_pop += pop
            unique_uncovered.add(country_name)
        lang_pop += pop
    
    lang_data['total_population_million'] = round(lang_pop, 1)

# 更新元数据
total_pop = total_covered_pop + total_uncovered_pop
pop_coverage_rate = (total_covered_pop / total_pop) * 100

data['report_metadata']['total_population_million'] = round(total_pop, 1)
data['report_metadata']['covered_population_million'] = round(total_covered_pop, 1)
data['report_metadata']['uncovered_population_million'] = round(total_uncovered_pop, 1)
data['report_metadata']['population_coverage_rate'] = f"{pop_coverage_rate:.1f}%"
data['report_metadata']['population_data_source'] = "Wikipedia (2024)"
data['report_metadata']['population_data_url'] = "https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population"

# 保存更新的JSON
with open(r"e:\Code\value of LLM\LLM's values\results\analysis\language\语言覆盖汇报数据.json", 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ JSON数据已更新（添加人口字段）")
print(f"   总人口：{total_pop:.1f}百万")
print(f"   已覆盖人口：{total_covered_pop:.1f}百万")
print(f"   人口覆盖率：{pop_coverage_rate:.1f}%")
print()

# 2. 生成新的Excel文件
wb = Workbook()

# 定义样式
COLORS = {
    'header': '4472C4',
    'subheader': '5B9BD5',
    'success': '70AD47',
    'warning': 'FF6B6B',
    'light_blue': 'DEEBF7',
    'light_green': 'E2EFDA',
}

title_font = Font(name='微软雅黑', size=16, bold=True, color='FFFFFF')
header_font = Font(name='微软雅黑', size=12, bold=True, color='FFFFFF')
subheader_font = Font(name='微软雅黑', size=11, bold=True)
normal_font = Font(name='微软雅黑', size=10)

header_fill = PatternFill(start_color=COLORS['header'], end_color=COLORS['header'], fill_type='solid')
success_fill = PatternFill(start_color=COLORS['success'], end_color=COLORS['success'], fill_type='solid')
warning_fill = PatternFill(start_color=COLORS['warning'], end_color=COLORS['warning'], fill_type='solid')
light_fill = PatternFill(start_color=COLORS['light_blue'], end_color=COLORS['light_blue'], fill_type='solid')

center_align = Alignment(horizontal='center', vertical='center', wrap_text=True)
left_align = Alignment(horizontal='left', vertical='center', wrap_text=True)
right_align = Alignment(horizontal='right', vertical='center')

thin_border = Border(
    left=Side(style='thin'), right=Side(style='thin'),
    top=Side(style='thin'), bottom=Side(style='thin')
)

# 工作表1: 总览
ws_summary = wb.active
ws_summary.title = "总览"

ws_summary.merge_cells('A1:G1')
ws_summary['A1'] = data['report_metadata']['title']
ws_summary['A1'].font = title_font
ws_summary['A1'].fill = header_fill
ws_summary['A1'].alignment = center_align
ws_summary.row_dimensions[1].height = 30

# 统计卡片（两行）
stats_row1 = [
    ('WVS总国家数', data['report_metadata']['total_countries']),
    ('已覆盖国家', data['report_metadata']['covered_countries']),
    ('未覆盖国家', data['report_metadata']['uncovered_countries']),
    ('国家覆盖率', data['report_metadata']['coverage_rate']),
]

stats_row2 = [
    ('总人口(百万)', f"{data['report_metadata']['total_population_million']:,.1f}"),
    ('已覆盖人口(百万)', f"{data['report_metadata']['covered_population_million']:,.1f}"),
    ('未覆盖人口(百万)', f"{data['report_metadata']['uncovered_population_million']:,.1f}"),
    ('人口覆盖率', data['report_metadata']['population_coverage_rate']),
]

row = 3
for stats in [stats_row1, stats_row2]:
    for i, (label, value) in enumerate(stats):
        col = i * 2 + 1
        
        cell_label = ws_summary.cell(row, col)
        cell_value = ws_summary.cell(row+1, col)
        
        ws_summary.merge_cells(start_row=row, start_column=col, end_row=row, end_column=col+1)
        ws_summary.merge_cells(start_row=row+1, start_column=col, end_row=row+1, end_column=col+1)
        
        cell_label.value = label
        cell_label.font = subheader_font
        cell_label.alignment = center_align
        cell_label.fill = light_fill
        cell_label.border = thin_border
        
        cell_value.value = str(value)
        cell_value.font = Font(name='微软雅黑', size=16, bold=True, color=COLORS['header'])
        cell_value.alignment = center_align
        if '覆盖率' in label or '已覆盖' in label:
            cell_value.fill = PatternFill(start_color=COLORS['light_green'], end_color=COLORS['light_green'], fill_type='solid')
        else:
            cell_value.fill = light_fill
        cell_value.border = thin_border
        
        ws_summary.row_dimensions[row].height = 25
        ws_summary.row_dimensions[row+1].height = 35
    
    row += 3

for col in range(1, 9):
    ws_summary.column_dimensions[get_column_letter(col)].width = 13

print("✅ 工作表 '总览' 创建完成")

# 工作表2: 已覆盖国家
ws_covered = wb.create_sheet("已覆盖国家")

ws_covered.merge_cells('A1:H1')
ws_covered['A1'] = f"已覆盖国家详细列表 (66国, {total_covered_pop:.1f}百万人口)"
ws_covered['A1'].font = title_font
ws_covered['A1'].fill = header_fill
ws_covered['A1'].alignment = center_align
ws_covered.row_dimensions[1].height = 30

headers = ['语言(英文)', '语言(中文)', '国家数', '占比', '国家(英文)', '国家(中文)', '人口(百万)', '文化区域']
for col, header in enumerate(headers, 1):
    cell = ws_covered.cell(2, col)
    cell.value = header
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = center_align
    cell.border = thin_border

ws_covered.row_dimensions[2].height = 25

# 数据（按国家数降序排序语言）
lang_list = []
for lang_en, lang_data in data['covered_by_language'].items():
    lang_list.append((lang_en, lang_data, lang_data['country_count']))

lang_list.sort(key=lambda x: x[2], reverse=True)

row = 3
for lang_en, lang_data, _ in lang_list:
    countries = sorted(lang_data['countries'], key=lambda x: x['name_en'])
    
    for i, country in enumerate(countries):
        if i == 0:
            for col in range(1, 5):
                cell = ws_covered.cell(row, col)
                if len(countries) > 1:
                    ws_covered.merge_cells(start_row=row, start_column=col, end_row=row+len(countries)-1, end_column=col)
                cell.font = subheader_font
                cell.alignment = center_align
                cell.fill = light_fill
                cell.border = thin_border
            
            ws_covered.cell(row, 1).value = lang_en
            ws_covered.cell(row, 2).value = lang_data['language_name_zh']
            ws_covered.cell(row, 3).value = lang_data['country_count']
            ws_covered.cell(row, 4).value = lang_data['percentage']
        
        ws_covered.cell(row, 5).value = country['name_en']
        ws_covered.cell(row, 5).font = normal_font
        ws_covered.cell(row, 5).alignment = left_align
        ws_covered.cell(row, 5).border = thin_border
        
        ws_covered.cell(row, 6).value = country['name_zh']
        ws_covered.cell(row, 6).font = normal_font
        ws_covered.cell(row, 6).alignment = left_align
        ws_covered.cell(row, 6).border = thin_border
        
        ws_covered.cell(row, 7).value = country['population_million']
        ws_covered.cell(row, 7).font = normal_font
        ws_covered.cell(row, 7).alignment = right_align
        ws_covered.cell(row, 7).border = thin_border
        ws_covered.cell(row, 7).number_format = '#,##0.0'
        
        ws_covered.cell(row, 8).value = country['cultural_region']
        ws_covered.cell(row, 8).font = normal_font
        ws_covered.cell(row, 8).alignment = center_align
        ws_covered.cell(row, 8).border = thin_border
        
        ws_covered.row_dimensions[row].height = 20
        row += 1

ws_covered.column_dimensions['A'].width = 25
ws_covered.column_dimensions['B'].width = 15
ws_covered.column_dimensions['C'].width = 10
ws_covered.column_dimensions['D'].width = 10
ws_covered.column_dimensions['E'].width = 30
ws_covered.column_dimensions['F'].width = 20
ws_covered.column_dimensions['G'].width = 13
ws_covered.column_dimensions['H'].width = 20

ws_covered.freeze_panes = 'A3'

print("✅ 工作表 '已覆盖国家' 创建完成")

# 工作表3: 未覆盖国家
ws_uncovered = wb.create_sheet("未覆盖国家")

ws_uncovered.merge_cells('A1:I1')
ws_uncovered['A1'] = f"未覆盖国家详细列表 (43国, {total_uncovered_pop:.1f}百万人口)"
ws_uncovered['A1'].font = title_font
ws_uncovered['A1'].fill = warning_fill
ws_uncovered['A1'].alignment = center_align
ws_uncovered.row_dimensions[1].height = 30

headers = ['语言(英文)', '语言(中文)', '代码', '国家数', '备注', '国家(英文)', '国家(中文)', '人口(百万)', '文化区域']
for col, header in enumerate(headers, 1):
    cell = ws_uncovered.cell(2, col)
    cell.value = header
    cell.font = header_font
    cell.fill = warning_fill
    cell.alignment = center_align
    cell.border = thin_border

ws_uncovered.row_dimensions[2].height = 25

row = 3
for lang_data in data['uncovered_by_language']:
    countries = lang_data['countries']
    
    for i, country in enumerate(countries):
        if i == 0:
            for col in range(1, 6):
                cell = ws_uncovered.cell(row, col)
                if len(countries) > 1:
                    ws_uncovered.merge_cells(start_row=row, start_column=col, end_row=row+len(countries)-1, end_column=col)
                cell.font = subheader_font
                cell.alignment = center_align if col <= 4 else left_align
                if lang_data['country_count'] >= 2:
                    cell.fill = PatternFill(start_color='FFE6E6', end_color='FFE6E6', fill_type='solid')
                else:
                    cell.fill = PatternFill(start_color='FFF5E6', end_color='FFF5E6', fill_type='solid')
                cell.border = thin_border
            
            ws_uncovered.cell(row, 1).value = lang_data['language']
            ws_uncovered.cell(row, 2).value = lang_data['language_zh']
            ws_uncovered.cell(row, 3).value = lang_data['language_code']
            ws_uncovered.cell(row, 4).value = lang_data['country_count']
            ws_uncovered.cell(row, 5).value = lang_data.get('note', '')
            ws_uncovered.cell(row, 5).font = Font(name='微软雅黑', size=9, italic=True, color='666666')
        
        ws_uncovered.cell(row, 6).value = country['name_en']
        ws_uncovered.cell(row, 6).font = normal_font
        ws_uncovered.cell(row, 6).alignment = left_align
        ws_uncovered.cell(row, 6).border = thin_border
        
        ws_uncovered.cell(row, 7).value = country['name_zh']
        ws_uncovered.cell(row, 7).font = normal_font
        ws_uncovered.cell(row, 7).alignment = left_align
        ws_uncovered.cell(row, 7).border = thin_border
        
        ws_uncovered.cell(row, 8).value = country['population_million']
        ws_uncovered.cell(row, 8).font = normal_font
        ws_uncovered.cell(row, 8).alignment = right_align
        ws_uncovered.cell(row, 8).border = thin_border
        ws_uncovered.cell(row, 8).number_format = '#,##0.0'
        
        ws_uncovered.cell(row, 9).value = country['cultural_region']
        ws_uncovered.cell(row, 9).font = normal_font
        ws_uncovered.cell(row, 9).alignment = center_align
        ws_uncovered.cell(row, 9).border = thin_border
        
        ws_uncovered.row_dimensions[row].height = 20
        row += 1

ws_uncovered.column_dimensions['A'].width = 28
ws_uncovered.column_dimensions['B'].width = 18
ws_uncovered.column_dimensions['C'].width = 10
ws_uncovered.column_dimensions['D'].width = 10
ws_uncovered.column_dimensions['E'].width = 35
ws_uncovered.column_dimensions['F'].width = 28
ws_uncovered.column_dimensions['G'].width = 18
ws_uncovered.column_dimensions['H'].width = 13
ws_uncovered.column_dimensions['I'].width = 20

ws_uncovered.freeze_panes = 'A3'

print("✅ 工作表 '未覆盖国家' 创建完成")

# 保存Excel
output_path = r"e:\Code\value of LLM\LLM's values\results\analysis\language\语言覆盖统计.xlsx"
wb.save(output_path)

print()
print("="*80)
print("✅ 所有文件更新完成！")
print("="*80)
print()
print(f"📁 文件位置: {output_path}")
print()
print(f"📊 新增内容:")
print(f"  ✅ 每个国家的人口（百万）")
print(f"  ✅ 总人口覆盖率：{pop_coverage_rate:.1f}%")
print(f"  ✅ 按人口排序语言")
print()
print(f"💡 关键数据:")
print(f"  - 109国总人口：{total_pop:,.1f}百万 ({total_pop/1000:.2f}十亿)")
print(f"  - 66国已覆盖：{total_covered_pop:,.1f}百万 ({total_covered_pop/1000:.2f}十亿)")
print(f"  - 43国未覆盖：{total_uncovered_pop:,.1f}百万 ({total_uncovered_pop/1000:.2f}十亿)")
print(f"  - 国家覆盖率：60.6%")
print(f"  - 人口覆盖率：{pop_coverage_rate:.1f}% 🎉")
print()
