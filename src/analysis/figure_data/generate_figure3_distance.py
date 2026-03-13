#!/usr/bin/env python3
"""
图3数据：东方主义distance地图 - 中东和东亚
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
    print("图3数据：东方主义distance地图 - 中东和东亚")
    print("="*60)
    
    df = load_distance_data()
    
    # 中东和东亚国家
    middle_east = ['Egypt', 'Iraq', 'Jordan', 'Kuwait', 'Lebanon', 'Libya', 
                  'Palestine', 'Qatar', 'Yemen', 'Algeria', 'Morocco', 'Tunisia']
    east_asia = ['China', 'Japan', 'Korea', 'Taiwan', 'Macao']
    
    # 筛选
    df_me = df[df['country'].isin(middle_east)]
    df_ea = df[df['country'].isin(east_asia)]
    
    # 按国家求平均
    me_avg = df_me.groupby('country').agg({
        'native_distance': 'mean',
        'en_distance': 'mean',
        'advantage': 'mean'
    }).reset_index()
    me_avg.columns = ['country', 'native_distance_mean', 'en_distance_mean', 'advantage_mean']
    
    ea_avg = df_ea.groupby('country').agg({
        'native_distance': 'mean',
        'en_distance': 'mean',
        'advantage': 'mean'
    }).reset_index()
    ea_avg.columns = ['country', 'native_distance_mean', 'en_distance_mean', 'advantage_mean']
    
    print(f"\n中东: {len(me_avg)}个国家")
    print(me_avg.to_string(index=False))
    
    print(f"\n东亚: {len(ea_avg)}个国家")
    print(ea_avg.to_string(index=False))
    
    # 保存
    output_dir = f'{PROJECT_ROOT}/results/figures'
    os.makedirs(output_dir, exist_ok=True)
    
    me_avg.to_csv(f'{output_dir}/figure3_middle_east_distance.csv', index=False)
    ea_avg.to_csv(f'{output_dir}/figure3_east_asia_distance.csv', index=False)
    
    print(f"\n已保存:")
    print(f"  - {output_dir}/figure3_middle_east_distance.csv")
    print(f"  - {output_dir}/figure3_east_asia_distance.csv")


if __name__ == '__main__':
    main()
