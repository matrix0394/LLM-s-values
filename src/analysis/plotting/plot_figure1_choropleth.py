#!/usr/bin/env python3
"""
图1: 45个国家的英语角色扮演PC1值 (Choropleth地图)
使用plotly内置地图数据，无需shapefile
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

PROJECT_ROOT = Path("/Users/yxy/code/LLM's values/LLM's values")
OUTPUT_DIR = PROJECT_ROOT / 'results' / 'figures'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ===== 国家名称映射 (WVS -> ISO) =====
COUNTRY_TO_ISO = {
    'China': 'CHN', 'Taiwan, Province of China': 'TWN', 'Japan': 'JPN', 'Korea, Republic of': 'KOR',
    'Germany': 'DEU', 'France': 'FRA', 'Italy': 'ITA', 'Spain': 'ESP', 'Portugal': 'PRT',
    'Tunisia': 'TUN', 'Jordan': 'JOR', 'Palestine': 'PSE', 'Lebanon': 'LBN', 'Morocco': 'MAR',
    'Kuwait': 'KWT', 'Egypt': 'EGY', 'Iraq': 'IRQ', 'Algeria': 'DZA', 'Qatar': 'QAT', 
    'Yemen': 'YEM', 'Bahrain': 'BHR',
    'Hong Kong': 'HKG', 'Haiti': 'HTI', 'Bolivia': 'BOL', 'Mali': 'MLI', 'Switzerland': 'CHE',
    'Austria': 'AUT', 'Belgium': 'BEL', 'Luxembourg': 'LUX', 'Russia': 'RUS', 'Belarus': 'BLR',
    'Kyrgyzstan': 'KGZ', 'Kazakhstan': 'KAZ', 'Russian Federation': 'RUS',
    'Argentina': 'ARG', 'Chile': 'CHL', 'Colombia': 'COL', 'Ecuador': 'ECU', 'Guatemala': 'GTM',
    'Mexico': 'MEX', 'Nicaragua': 'NIC', 'Peru': 'PER', 'Uruguay': 'URY', 'Venezuela': 'VEN',
    'Brazil': 'BRA', 'Malaysia': 'MYS', 'Singapore': 'SGP', 'Philippines': 'PHL', 'Pakistan': 'PAK',
    'India': 'IND', 'Thailand': 'THA', 'Indonesia': 'IDN', 'Turkey': 'TUR', 'Poland': 'POL',
    'Netherlands': 'NLD', 'Sweden': 'SWE', 'Norway': 'NOR', 'Denmark': 'DNK', 'Finland': 'FIN',
    'Ireland': 'IRL', 'United Kingdom': 'GBR', 'United States of America': 'USA', 'Canada': 'CAN',
    'Australia': 'AUS', 'New Zealand': 'NZL', 'Nigeria': 'NGA', 'Ghana': 'GHA', 'Kenya': 'KEN',
    'South Africa': 'ZAF', 'Rwanda': 'RWA', 'Zambia': 'ZMB', 'Zimbabwe': 'ZWE', 'Trinidad and Tobago': 'TTO'
}

# 45个非英语国家
COUNTRIES_45 = [
    'China', 'Taiwan, Province of China', 'Japan', 'Korea, Republic of',
    'Germany', 'France', 'Italy', 'Spain', 'Portugal',
    'Tunisia', 'Jordan', 'Palestine', 'Lebanon', 'Morocco', 'Kuwait',
    'Egypt', 'Iraq', 'Algeria', 'Qatar', 'Yemen', 'Bahrain',
    'Hong Kong', 'Haiti', 'Bolivia', 'Mali', 'Switzerland',
    'Austria', 'Belgium', 'Luxembourg', 'Russia', 'Belarus',
    'Kyrgyzstan', 'Kazakhstan', 'Russian Federation',
    'Argentina', 'Chile', 'Colombia', 'Ecuador', 'Guatemala',
    'Mexico', 'Nicaragua', 'Peru', 'Uruguay', 'Venezuela',
    'Brazil', 'Malaysia'
]

def load_pca_data():
    """加载PCA坐标数据"""
    pca_file = PROJECT_ROOT / 'SI/pca/Table_S7_LLM_roleplay_PCA_coordinates.csv'
    df = pd.read_csv(pca_file)
    
    # 排除模型
    EXCLUDED = ['qwen3-1.7b', 'z-ai/glm-4.6', 'qwen/qwq-32b']
    df = df[~df['model_name'].isin(EXCLUDED)]
    
    return df

def calculate_pc1_per_country(pca_df):
    """计算每个国家的英语角色扮演PC1均值"""
    # 英语国家使用en-native，其他用en
    EN_NATIVE = ['Australia', 'Canada', 'Ghana', 'Ireland', 'Kenya',
                 'Malaysia', 'Malta', 'New Zealand', 'Nigeria', 'Pakistan',
                 'Philippines', 'Puerto Rico', 'Rwanda', 'Singapore',
                 'South Africa', 'Trinidad and Tobago', 'United Kingdom',
                 'United States of America', 'Zambia', 'Zimbabwe']
    
    results = []
    
    for country in COUNTRIES_45:
        # 确定英语类型
        en_lang = 'en-native' if country in EN_NATIVE else 'en'
        
        # 获取英语数据
        en_data = pca_df[(pca_df['country'] == country) & (pca_df['language'] == en_lang)]
        
        if len(en_data) > 0:
            pc1_mean = en_data['PC1'].mean()
            pc2_mean = en_data['PC2'].mean()
            results.append({
                'country': country,
                'iso_alpha': COUNTRY_TO_ISO.get(country, ''),
                'PC1': pc1_mean,
                'PC2': pc2_mean
            })
    
    return pd.DataFrame(results)


def plot_choropleth_map(pc1_df, output_dir):
    """绘制Choropleth地图 - PC1值热力图"""
    
    # 过滤有效数据
    valid_df = pc1_df[pc1_df['iso_alpha'] != ''].copy()
    
    print(f"有效国家数: {len(valid_df)}")
    print(f"PC1范围: {valid_df['PC1'].min():.2f} ~ {valid_df['PC1'].max():.2f}")
    
    # 绘制Choropleth地图
    fig = px.choropleth(
        valid_df,
        locations='iso_alpha',
        color='PC1',
        color_continuous_scale='RdBu_r',  # 红蓝配色
        range_color=[valid_df['PC1'].min(), valid_df['PC1'].max()],
        title='English Roleplay PC1 Values by Country (45 Non-English Speaking Countries)',
        labels={'PC1': 'PC1'},
        projection='natural earth'
    )
    
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor='gray',
            coastlinewidth=0.5,
            landcolor='lightgray',
            bgcolor='white'
        ),
        title_font_size=14,
        coloraxis_colorbar=dict(
            title='PC1',
            ticksuffix=''
        ),
        width=1200,
        height=700
    )
    
    # 保存 (HTML可交互，PNG需本地有kaleido)
    fig.write_html(output_dir / 'figure1_pc1_choropleth.html')
    try:
        fig.write_image(output_dir / 'figure1_pc1_choropleth.png', scale=2)
        fig.write_image(output_dir / 'figure1_pc1_choropleth.pdf')
    except Exception as e:
        print(f"⚠️ PNG/PDF导出需要kaleido: {e}")
        print(f"   HTML已保存，可在浏览器打开查看")
    
    print(f"✅ 保存: {output_dir}/figure1_pc1_choropleth.html")
    
    return fig


def main():
    print("=" * 60)
    print("生成图1: Choropleth地图 (英语PC1)")
    print("=" * 60)
    
    # 加载数据
    pca_df = load_pca_data()
    print(f"PCA数据: {len(pca_df)} 条记录")
    
    # 计算每个国家的PC1
    pc1_df = calculate_pc1_per_country(pca_df)
    print(f"国家数: {len(pc1_df)}")
    
    # 打印前几个
    print("\n前5个国家:")
    print(pc1_df.head())
    
    # 绘制地图
    plot_choropleth_map(pc1_df, OUTPUT_DIR)
    
    print("\n" + "=" * 60)
    print("完成!")
    print("=" * 60)


if __name__ == '__main__':
    main()
