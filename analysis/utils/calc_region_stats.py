#!/usr/bin/env python3
"""计算各文化区域的英语优势统计"""
import pandas as pd

df = pd.read_csv('results/analysis/stage0_vs_stage3/english_advantage_average.csv')
print('各文化区域英语优势统计：')
print('='*60)
region_stats = df.groupby('cultural_region')['english_advantage'].agg(['mean', 'std', 'count'])
region_stats = region_stats.sort_values('mean', ascending=False)
for region, row in region_stats.iterrows():
    print(f'{region:20s}: {row["mean"]:+.1f}% (n={int(row["count"])})')
