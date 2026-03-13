#!/usr/bin/env python3
"""
验证PC1/PC2定义是否与WVS官方文化地图一致
"""

import json
import pandas as pd

def main():
    # 加载我们的IVS数据
    with open('data/country_values/country_scores_pca.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    df = pd.DataFrame(data)

    # 选择一些典型国家来验证
    # 根据WVS官方文化地图：
    # - 瑞典(Sweden)应该在右上角：高Self-Expression(高X), 高Secular(高Y)
    # - 美国(USA)应该在右侧中间：高Self-Expression(高X), 中等Secular
    # - 中国(China)应该在中间偏上：中等Self-Expression, 高Secular
    # - 约旦(Jordan)应该在左下角：低Self-Expression(低X), 低Secular(低Y)
    # - 日本(Japan)应该在中上：中等Self-Expression, 高Secular
    # - 德国(Germany)应该在右上：高Self-Expression, 高Secular
    # - 尼日利亚(Nigeria)应该在左下：低Self-Expression, 低Secular

    countries = ['Sweden', 'United States of America', 'China', 'Jordan', 'Japan', 'Germany', 'Nigeria', 'Brazil']

    print('=' * 80)
    print('验证PC1/PC2定义是否正确')
    print('=' * 80)
    print()
    print('我们数据中的坐标:')
    print('-' * 80)

    for country in countries:
        row = df[df['Country'] == country]
        if len(row) > 0:
            pc1 = row['PC1_rescaled'].values[0]
            pc2 = row['PC2_rescaled'].values[0]
            region = row['Cultural Region'].values[0]
            print(f'{country:35} | PC1={pc1:+.2f} | PC2={pc2:+.2f} | Region: {region}')
        else:
            print(f'{country:35} | NOT FOUND')

    print()
    print('=' * 80)
    print('WVS官方文化地图预期位置（参考）:')
    print('=' * 80)
    print('''
根据WVS官方Inglehart-Welzel文化地图:
- X轴: Survival ← → Self-Expression (左低右高)
- Y轴: Traditional ← → Secular-Rational (下低上高)

预期位置:
- Sweden:   右上角 (高Self-Expression ~4.5, 高Secular ~2.3)
- USA:      右侧中间 (高Self-Expression ~2.1, 中等Secular ~0.3)  
- China:    中间偏上 (中等 ~0, 高Secular ~0.7)
- Jordan:   左下角 (低Self-Expression ~-1.8, 低Secular ~-2.0)
- Japan:    中上 (中等Self-Expression ~1.7, 高Secular ~2.1)
- Germany:  右上 (高Self-Expression ~2.3, 高Secular ~1.8)
- Nigeria:  左下 (低Self-Expression ~-1.2, 低Secular ~-1.6)
- Brazil:   中间偏左下 (中等 ~0, 低Secular ~-0.4)
''')

    print('=' * 80)
    print('验证结论:')
    print('=' * 80)
    
    # 验证逻辑
    sweden = df[df['Country'] == 'Sweden']
    jordan = df[df['Country'] == 'Jordan']
    
    if len(sweden) > 0 and len(jordan) > 0:
        sweden_pc1 = sweden['PC1_rescaled'].values[0]
        sweden_pc2 = sweden['PC2_rescaled'].values[0]
        jordan_pc1 = jordan['PC1_rescaled'].values[0]
        jordan_pc2 = jordan['PC2_rescaled'].values[0]
        
        print(f'\n瑞典 vs 约旦 对比:')
        print(f'  瑞典: PC1={sweden_pc1:+.2f}, PC2={sweden_pc2:+.2f}')
        print(f'  约旦: PC1={jordan_pc1:+.2f}, PC2={jordan_pc2:+.2f}')
        
        # 瑞典应该比约旦的PC1和PC2都高
        if sweden_pc1 > jordan_pc1 and sweden_pc2 > jordan_pc2:
            print('\n✅ PC1/PC2定义正确!')
            print('   - PC1: 瑞典 > 约旦 (Self-Expression维度正确)')
            print('   - PC2: 瑞典 > 约旦 (Secular-Rational维度正确)')
        else:
            print('\n⚠️ 可能存在PC1/PC2定义问题!')
            if sweden_pc1 < jordan_pc1:
                print('   - PC1可能搞反了: 瑞典应该比约旦高')
            if sweden_pc2 < jordan_pc2:
                print('   - PC2可能搞反了: 瑞典应该比约旦高')

if __name__ == '__main__':
    main()
