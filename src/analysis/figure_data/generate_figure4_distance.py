#!/usr/bin/env python3
"""
图4数据：撒哈拉以南非洲和拉丁美洲distance地图
英语和母语的距离数据
"""

import pandas as pd
import os

PROJECT_ROOT = '/Users/yxy/code/LLM\'s values/LLM\'s values'


def load_distance_data():
    """加载distance数据"""
    df = pd.read_csv(f'{PROJECT_ROOT}/results/analysis/french_advantage/english_advantage_all_countries.csv')
    return df


def main():
    print("="*60)
    print("图4数据：distance地图 - 撒哈拉以南非洲和拉丁美洲")
    print("="*60)
    
    df = load_distance_data()
    
    # 北非和拉丁美洲（在数据中的国家）
    north_africa = ['Algeria', 'Morocco', 'Tunisia', 'Libya', 'Egypt']
    latin_america = ['Mexico', 'Colombia', 'Argentina', 'Brazil', 'Chile', 
                    'Peru', 'Venezuela', 'Ecuador', 'Guatemala', 'Bolivia',
                    'Nicaragua', 'Uruguay']
    
    # 筛选并计算国家平均
    df_na = df[df['country'].isin(north_africa)]
    df_la = df[df['country'].isin(latin_america)]
    
    # 按国家求平均
    na_avg = df_na.groupby('country').agg({
        'native_distance': 'mean',
        'en_distance': 'mean',
        'advantage': 'mean'
    }).reset_index()
    na_avg.columns = ['country', 'native_distance_mean', 'en_distance_mean', 'advantage_mean']
    
    la_avg = df_la.groupby('country').agg({
        'native_distance': 'mean',
        'en_distance': 'mean',
        'advantage': 'mean'
    }).reset_index()
    la_avg.columns = ['country', 'native_distance_mean', 'en_distance_mean', 'advantage_mean']
    
    print(f"\n北非（阿拉伯伊斯兰）: {len(na_avg)}个国家")
    print(na_avg.to_string(index=False))
    
    print(f"\n拉丁美洲: {len(la_avg)}个国家")
    print(la_avg.to_string(index=False))
    
    # 保存
    output_dir = f'{PROJECT_ROOT}/results/figures'
    os.makedirs(output_dir, exist_ok=True)
    
    na_avg.to_csv(f'{output_dir}/figure4_north_africa_distance.csv', index=False)
    la_avg.to_csv(f'{output_dir}/figure4_latin_america_distance.csv', index=False)
    
    print(f"\n已保存:")
    print(f"  - {output_dir}/figure4_north_africa_distance.csv")
    print(f"  - {output_dir}/figure4_latin_america_distance.csv")


if __name__ == '__main__':
    main()
