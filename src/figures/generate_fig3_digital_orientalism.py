#!/usr/bin/env python3
"""Generate Figure 3: Digital Orientalism and Colonial Legacies.

Four-panel figure (A-D) for the main paper:
  A: Geographic gradient of EA from Near Orient -> Far Orient
  B: East Asia 6-entity stratification (colonial/geopolitical context)
  C: Sub-Saharan Africa (British colonies PC2 bias + French colonies EA)
  D: Latin America by colonial language

Data sources:
  - data/country_values/country_scores_pca.json
  - data/llm_pca/multilingual/roleplay_ml_pca_entity_scores_latest.pkl
  - results/analysis/study4_colonial_legacies.json
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / 'docs' / '论文草稿' / 'tex' / 'figures'
ANALYSIS_DIR = PROJECT_ROOT / 'results' / 'analysis'
MODEL_NAME_MAP = {
    'anthropic/claude-sonnet-4.5': 'claude-sonnet-4.5',
    'deepseek/deepseek-chat-v3.1': 'deepseek-chat-v3.1',
    'google/gemini-2.5-flash': 'gemini-2.5-flash',
    'google/gemini-2.5-pro': 'gemini-2.5-pro',
    'google/gemini-3-pro-preview': 'gemini-3-pro-preview',
    'google/gemma-3-4b-it': 'gemma-3-4b-it',
    'meta-llama/llama-3.2-3b-instruct': 'llama-3.2-3b-instruct',
    'meta-llama/llama-3.3-70b-instruct': 'llama-3.3-70b-instruct',
    'microsoft/phi-3-mini-128k-instruct': 'phi-3-mini-128k-instruct',
    'mistralai/mistral-medium-3.1': 'mistral-medium-3.1',
    'mistralai/mistral-nemo': 'mistral-nemo',
    'openai/gpt-5.1': 'gpt-5.1',
    'qwen/qwen3-max': 'qwen3-max',
    'qwen/qwq-32b': 'qwq-32b',
    'x-ai/grok-4.1-fast': 'grok-4.1-fast',
    'z-ai/glm-4.6': 'glm-4.6',
}
EXCLUDED_MODELS = {'qwen3-1.7b', 'glm-4.6', 'qwq-32b'}

REGION_COLORS = {
    'Middle East': '#E74C3C',
    'African-Islamic': '#E74C3C',
    'Confucian': '#3498DB',
}

COLONIAL_COLORS = {
    'UK': '#1A5276',
    'US': '#2E86C1',
    'JP': '#E67E22',
    'PT': '#27AE60',
    'Autonomous': '#7F8C8D',
}


def euclidean(a_pc1, a_pc2, b_pc1, b_pc2) -> float:
    return float(np.sqrt((a_pc1 - b_pc1) ** 2 + (a_pc2 - b_pc2) ** 2))


def load_ivs_coordinates() -> dict:
    """Load the latest IVS/WVS benchmark coordinates."""
    path = PROJECT_ROOT / 'data' / 'country_values' / 'country_scores_pca.json'
    with open(path, encoding='utf-8') as f:
        data = json.load(f)

    coords = {}
    for item in data:
        country = item.get('Country')
        pc1 = item.get('PC1_rescaled')
        pc2 = item.get('PC2_rescaled')
        if country and pc1 is not None and pc2 is not None:
            coords[country] = {
                'PC1': float(pc1),
                'PC2': float(pc2),
            }
    return coords


def compute_panel_a_data() -> pd.DataFrame:
    """Compute panel A directly from the latest unified multilingual PCA data."""
    ivs = load_ivs_coordinates()
    roleplay_path = PROJECT_ROOT / 'data' / 'llm_pca' / 'multilingual' / 'roleplay_ml_pca_entity_scores_latest.pkl'
    roleplay = pd.read_pickle(roleplay_path)
    roleplay['model_name'] = roleplay['model_name'].map(lambda x: MODEL_NAME_MAP.get(x, x))
    roleplay = roleplay[roleplay['data_source'] != 'IVS'].copy()
    roleplay = roleplay[~roleplay['model_name'].isin(EXCLUDED_MODELS)].copy()

    middle_east = [
        'Algeria', 'Egypt', 'Iraq', 'Jordan', 'Kuwait', 'Lebanon',
        'Libya', 'Morocco', 'Palestine', 'Qatar', 'Tunisia', 'Yemen',
    ]
    east_asia = [
        'China', 'Japan', 'Korea, Republic of',
        'Taiwan, Province of China', 'Hong Kong', 'Macao',
    ]
    native_lang_map = {
        'Algeria': 'ar', 'Egypt': 'ar', 'Iraq': 'ar', 'Jordan': 'ar',
        'Kuwait': 'ar', 'Lebanon': 'ar', 'Libya': 'ar', 'Morocco': 'ar',
        'Palestine': 'ar', 'Qatar': 'ar', 'Tunisia': 'ar', 'Yemen': 'ar',
        'China': 'zh-cn', 'Japan': 'ja', 'Korea, Republic of': 'ko',
        'Taiwan, Province of China': 'zh-tw', 'Hong Kong': 'zh-hk',
        'Macao': 'pt',
    }

    rows = []
    for country in middle_east + east_asia:
        if country not in ivs:
            continue

        country_rows = roleplay[roleplay['Country'] == country]
        en_rows = country_rows[country_rows['language'].isin(['en', 'en-native'])]
        native_lang = native_lang_map[country]
        native_rows = country_rows[country_rows['language'] == native_lang]
        if en_rows.empty or native_rows.empty:
            continue

        d_en_list, d_native_list = [], []
        for model in native_rows['model_name'].unique():
            en_model = en_rows[en_rows['model_name'] == model]
            native_model = native_rows[native_rows['model_name'] == model]
            if en_model.empty or native_model.empty:
                continue

            ivs_country = ivs[country]
            d_en_list.append(
                euclidean(
                    en_model['PC1_rescaled'].mean(),
                    en_model['PC2_rescaled'].mean(),
                    ivs_country['PC1'],
                    ivs_country['PC2'],
                )
            )
            d_native_list.append(
                euclidean(
                    native_model['PC1_rescaled'].mean(),
                    native_model['PC2_rescaled'].mean(),
                    ivs_country['PC1'],
                    ivs_country['PC2'],
                )
            )

        if not d_en_list:
            continue

        mean_d_en = float(np.mean(d_en_list))
        mean_d_native = float(np.mean(d_native_list))
        advantage = (mean_d_native - mean_d_en) / mean_d_native * 100 if mean_d_native > 0 else 0.0
        rows.append({
            'country': country,
            'cultural_region': 'Middle East' if country in middle_east else 'Confucian',
            'native_language': native_lang,
            'native_distance_mean': mean_d_native,
            'en_distance_mean': mean_d_en,
            'advantage_mean': advantage,
            'n_models': len(d_en_list),
        })

    return pd.DataFrame(rows)


def load_data():
    """Load all data files needed for Figure 3 from current analysis outputs."""
    geo_df = compute_panel_a_data()
    study4_json = ANALYSIS_DIR / 'study4_colonial_legacies.json'
    with open(study4_json) as f:
        study4 = json.load(f)
    return geo_df, study4


def set_style():
    """Set publication-quality matplotlib style."""
    plt.rcParams.update({
        'font.family': 'Helvetica',
        'font.size': 8,
        'axes.labelsize': 9,
        'axes.titlesize': 10,
        'xtick.labelsize': 7,
        'ytick.labelsize': 7,
        'legend.fontsize': 7,
        'pdf.fonttype': 42,
        'ps.fonttype': 42,
        'axes.linewidth': 0.6,
        'figure.facecolor': 'white',
        'axes.facecolor': '#FAFAFA',
        'xtick.major.width': 0.5,
        'ytick.major.width': 0.5,
        'xtick.direction': 'in',
        'ytick.direction': 'in',
    })


def panel_a(ax, geo_df):
    """Panel A: Geographic gradient from Near Orient to Far Orient."""
    geo_df = geo_df.sort_values('advantage_mean', ascending=False)

    colors = [REGION_COLORS.get(r, '#95A5A6') for r in geo_df['cultural_region']]

    bars = ax.barh(range(len(geo_df)), geo_df['advantage_mean'], color=colors,
                   edgecolor='white', linewidth=0.3, height=0.7)

    country_labels = geo_df['country'].str.replace(', Province of China', '')
    country_labels = country_labels.str.replace(', Republic of', '')
    ax.set_yticks(range(len(geo_df)))
    ax.set_yticklabels(country_labels, fontsize=6.5)
    ax.invert_yaxis()
    ax.set_xlabel('English Advantage (%)')
    ax.axvline(x=0, color='black', linewidth=0.5, linestyle='-')
    ax.set_title('A', fontweight='bold', loc='left', fontsize=12)

    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#E74C3C', label='Middle East (Near Orient)'),
        Patch(facecolor='#3498DB', label='Confucian (Far Orient)'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', framealpha=0.9, fontsize=6)


def panel_b(ax, study4):
    """Panel B: East Asia 6-entity stratification."""
    conf = study4['confucian_stratification']

    entities = ['Taiwan', 'Hong Kong', 'Japan', 'South Korea', 'China', 'Macao']
    eas = [conf[e]['mean_ea_pct'] for e in entities]

    contexts = [
        'US post-war\nintegration',
        'British colony\n1842–1997',
        'US alliance\npost-1950s',
        'US alliance\npost-1950s',
        'Autonomous\nmodernization',
        'Portuguese colony\n1557–1999',
    ]

    bar_colors = ['#2E86C1', '#1A5276', '#2E86C1', '#2E86C1', '#7F8C8D', '#27AE60']

    bars = ax.bar(range(len(entities)), eas, color=bar_colors,
                  edgecolor='white', linewidth=0.5, width=0.65)

    ax.set_xticks(range(len(entities)))
    ax.set_xticklabels(entities, fontsize=7, rotation=25, ha='right')

    for i, (bar, ctx) in enumerate(zip(bars, contexts)):
        y = bar.get_height()
        va = 'bottom' if y >= 0 else 'top'
        offset = 0.5 if y >= 0 else -0.5
        ax.text(bar.get_x() + bar.get_width() / 2, y + offset, ctx,
                ha='center', va=va, fontsize=5, color='#555555', style='italic')

    ax.axhline(y=0, color='black', linewidth=0.5)
    ax.set_ylabel('English Advantage (%)')
    ax.set_title('B', fontweight='bold', loc='left', fontsize=12)


def panel_c(ax, study4):
    """Panel C: Sub-Saharan Africa — British (PC2 bias) + French (EA)."""
    british = study4['africa_british']['per_country']
    french = study4['africa_french']['per_country']

    b_sorted = sorted(british.items(), key=lambda x: x[1]['mean_pc2_bias'], reverse=True)
    b_countries = [c for c, _ in b_sorted]
    b_values = [v['mean_pc2_bias'] for _, v in b_sorted]

    f_countries = list(french.keys())
    f_values = [french[c]['mean_ea_pct'] for c in f_countries]

    x = list(range(len(b_countries)))
    ax.bar(x, b_values, color='#1A5276', edgecolor='white',
           linewidth=0.5, width=0.6, label='British colonies\n(PC2 Secular bias)')

    gap = len(b_countries) + 1
    x_f = [gap + i for i in range(len(f_countries))]
    ax.bar(x_f, f_values, color='#E74C3C', edgecolor='white',
           linewidth=0.5, width=0.6, label='French colonies\n(English Adv. %)')

    all_x = x + x_f
    all_labels = b_countries + f_countries
    ax.set_xticks(all_x)
    ax.set_xticklabels(all_labels, fontsize=6.5, rotation=30, ha='right')

    ax.axhline(y=0, color='black', linewidth=0.5)
    ax.set_ylabel('Bias / EA (%)')
    ax.set_title('C', fontweight='bold', loc='left', fontsize=12)

    agg_b = study4['africa_british']['aggregate_mean_bias']
    p_b = study4['africa_british']['t_test']['p']
    agg_f = study4['africa_french']['aggregate_mean_ea_pct']
    p_f = study4['africa_french']['t_test']['p']

    ax.text(np.mean(x), max(b_values) + 0.8,
            f'Mean = {agg_b:.2f}, p = {p_b:.3f}',
            ha='center', fontsize=6, color='#1A5276', fontstyle='italic')
    ax.text(np.mean(x_f), max(f_values) + 0.8,
            f'Mean = {agg_f:.1f}%, p = {p_f:.3f}',
            ha='center', fontsize=6, color='#E74C3C', fontstyle='italic')

    ax.legend(loc='center left', fontsize=6, framealpha=0.9)


def panel_d(ax, study4):
    """Panel D: Latin America by colonial language."""
    spanish = study4['latin_america']['spanish_colonies']['per_country']
    brazil_ea = study4['latin_america']['brazil']['mean_ea_pct']
    haiti_ea = study4['latin_america']['haiti']['mean_ea_pct']

    sp_sorted = sorted(spanish.items(), key=lambda x: x[1], reverse=True)
    countries = [c for c, _ in sp_sorted] + ['Brazil', 'Haiti']
    values = [v for _, v in sp_sorted] + [brazil_ea, haiti_ea]
    colors = ['#F39C12'] * len(sp_sorted) + ['#27AE60', '#8E44AD']

    bars = ax.barh(range(len(countries)), values, color=colors,
                   edgecolor='white', linewidth=0.3, height=0.65)

    ax.set_yticks(range(len(countries)))
    ax.set_yticklabels(countries, fontsize=6.5)
    ax.invert_yaxis()
    ax.axvline(x=0, color='black', linewidth=0.5)
    ax.set_xlabel('English Advantage (%)')
    ax.set_title('D', fontweight='bold', loc='left', fontsize=12)

    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#F39C12', label='Spanish colonies'),
        Patch(facecolor='#27AE60', label='Portuguese (Brazil)'),
        Patch(facecolor='#8E44AD', label='French (Haiti)'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', framealpha=0.9, fontsize=6)


def main():
    set_style()
    geo_df, study4 = load_data()

    fig = plt.figure(figsize=(16, 10))
    gs = gridspec.GridSpec(2, 2, hspace=0.35, wspace=0.30,
                           left=0.06, right=0.97, top=0.96, bottom=0.06)

    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, 0])
    ax_d = fig.add_subplot(gs[1, 1])

    panel_a(ax_a, geo_df)
    panel_b(ax_b, study4)
    panel_c(ax_c, study4)
    panel_d(ax_d, study4)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / 'Figure3.png'
    fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Saved: {output_path}")

    sm_path = PROJECT_ROOT / 'Supplementary Materials' / 'figures' / 'Figure3.png'
    fig.savefig(sm_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Saved: {sm_path}")

    plt.close()
    print("Figure 3 generated successfully.")


if __name__ == '__main__':
    main()
