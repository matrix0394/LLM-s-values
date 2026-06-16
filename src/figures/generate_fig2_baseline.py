"""
Generate Figure 2: LLM Intrinsic Values by Language (20 models x 6 languages).

Layout: 2x3 grid with shared axes. Each panel shows 20 labeled model points
on the WVS cultural map with SVM region fills (WVS official style).

Nature Communications style:
  - Shared x/y axes to eliminate redundant tick labels
  - Dual legend: model markers + WVS cultural zone patches
  - Directional axis labels with arrows
  - Clean, low-clutter label styling

Input:  results/paper_data/figure2_baseline_20models.csv
        SI/pca/Table_S5_IVS_PCA_coordinates.csv
Output: results/figures/paper/Fig2_baseline_intrinsic_values.{png,pdf}
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'analysis' / 'si'))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

from si_config import (
    load_ivs_data, get_global_axis_limits,
    save_figure, LANGUAGE_NAMES, REGION_COLORS,
)

plt.rcParams.update({
    'font.family': 'Helvetica',
    'font.size': 9,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
    'axes.linewidth': 0.6,
    'axes.facecolor': '#F8F8F8',
    'figure.facecolor': 'white',
    'xtick.major.width': 0.5,
    'ytick.major.width': 0.5,
    'xtick.major.size': 3,
    'ytick.major.size': 3,
    'xtick.direction': 'in',
    'ytick.direction': 'in',
})

OUTPUT_DIR = PROJECT_ROOT / 'results' / 'figures' / 'paper'
BASELINE_DATA_PATH = PROJECT_ROOT / 'results' / 'paper_data' / 'figure2_baseline_20models.csv'
LANGUAGES_ORDER = ['ar', 'en', 'es', 'fr', 'ru', 'zh-cn']

# WVS official map inspired colors — more saturated than si_config defaults
WVS_REGION_COLORS = {
    'Confucian':         '#E8872E',  # warm orange
    'Protestant Europe': '#D4C826',  # golden yellow
    'Latin America':     '#18A48C',  # teal
    'Catholic Europe':   '#2EAD56',  # vivid green
    'English-Speaking':  '#C8C830',  # yellow-green
    'African-Islamic':   '#8C8C8C',  # medium gray
    'West & South Asia': '#C46A2C',  # burnt orange
    'Orthodox Europe':   '#4878A8',  # steel blue
    'Other':             '#B0B0B0',
    'Baltic':            '#88A0C0',
}

# ── 20 individual model colors — maximally distinct, vivid ──────────────
# Grouped by vendor with tonal variation within each vendor family.
MODEL_DISPLAY = {
    # OpenAI — blues
    'gpt-4o':                     {'short': 'GPT-4o',              'color': '#0D47A1'},
    'gpt-4o-mini':                {'short': 'GPT-4o-mini',         'color': '#1976D2'},
    'gpt-5.1':                    {'short': 'GPT-5.1',             'color': '#42A5F5'},
    # Anthropic — reds
    'claude-3-7-sonnet-20250219': {'short': 'Claude-3.7-Sonnet',   'color': '#B71C1C'},
    'claude-sonnet-4.5':          {'short': 'Claude-Sonnet-4.5',   'color': '#E53935'},
    # Google — greens
    'gemini-2.5-flash':           {'short': 'Gemini-2.5-Flash',    'color': '#1B5E20'},
    'gemini-2.5-pro':             {'short': 'Gemini-2.5-Pro',      'color': '#2E7D32'},
    'gemini-3-pro-preview':       {'short': 'Gemini-3-Pro',        'color': '#43A047'},
    'gemma-3-4b-it':              {'short': 'Gemma-3-4B',          'color': '#66BB6A'},
    # Meta — orange
    'llama-3.2-3b-instruct':      {'short': 'LLaMA-3.2-3B',       'color': '#E65100'},
    'llama-3.3-70b-instruct':     {'short': 'LLaMA-3.3-70B',      'color': '#FB8C00'},
    # Mistral — purple
    'mistral-medium-3.1':         {'short': 'Mistral-Medium',      'color': '#6A1B9A'},
    'mistral-nemo':               {'short': 'Mistral-Nemo',        'color': '#AB47BC'},
    # DeepSeek — cyan
    'deepseek-chat':              {'short': 'DeepSeek-V3',         'color': '#006064'},
    'deepseek-chat-v3.1':         {'short': 'DeepSeek-V3.1',       'color': '#00ACC1'},
    # Others — distinct singles
    'qwen3-max':                  {'short': 'Qwen3-Max',           'color': '#F9A825'},
    'doubao-1-5-pro-32k-250115':  {'short': 'Doubao-1.5-Pro',      'color': '#AD1457'},
    'kimi-k2':                    {'short': 'Kimi-K2',             'color': '#795548'},
    'phi-3-mini-128k-instruct':   {'short': 'Phi-3-Mini',          'color': '#558B2F'},
    'grok-4.1-fast':              {'short': 'Grok-4.1',            'color': '#37474F'},
}

MODEL_TO_VENDOR = {
    'gpt-4o': 'OpenAI', 'gpt-4o-mini': 'OpenAI', 'gpt-5.1': 'OpenAI',
    'claude-3-7-sonnet-20250219': 'Anthropic', 'claude-sonnet-4.5': 'Anthropic',
    'gemini-2.5-flash': 'Google', 'gemini-2.5-pro': 'Google',
    'gemini-3-pro-preview': 'Google', 'gemma-3-4b-it': 'Google',
    'llama-3.2-3b-instruct': 'Meta', 'llama-3.3-70b-instruct': 'Meta',
    'mistral-medium-3.1': 'Mistral', 'mistral-nemo': 'Mistral',
    'deepseek-chat': 'DeepSeek', 'deepseek-chat-v3.1': 'DeepSeek',
    'qwen3-max': 'Other', 'doubao-1-5-pro-32k-250115': 'Other',
    'kimi-k2': 'Other', 'phi-3-mini-128k-instruct': 'Other',
    'grok-4.1-fast': 'Other',
}

VENDOR_MARKERS = {
    'OpenAI': 'o', 'Anthropic': 's', 'Google': '^', 'Meta': 'D',
    'Mistral': 'v', 'DeepSeek': 'P', 'Other': 'h',
}


def plot_ivs_bold_background(ax, ivs_data):
    """Bold SVM region fills + country dots, WVS official-map style."""
    try:
        from boundary_utils_ml import generate_ml_boundaries, plot_decision_boundaries_masked

        excluded_regions = {'Other', 'Baltic'}
        regions = sorted([r for r in ivs_data['cultural_region'].unique()
                          if r not in excluded_regions and not (r != r)])

        ml_data = ivs_data[ivs_data['cultural_region'].isin(regions)].copy()
        ml_data = ml_data[['PC1', 'PC2', 'cultural_region']].dropna()

        clf, le, xx, yy = generate_ml_boundaries(
            ml_data, WVS_REGION_COLORS, method='svm', resolution=250)

        plot_decision_boundaries_masked(
            ax, clf, le, xx, yy, ml_data, WVS_REGION_COLORS,
            alpha=0.45, mask_padding=0.6)
    except Exception:
        pass

    for region in ivs_data['cultural_region'].dropna().unique():
        subset = ivs_data[ivs_data['cultural_region'] == region]
        color = WVS_REGION_COLORS.get(region, '#CCCCCC')
        ax.scatter(subset['PC1'], subset['PC2'],
                   c=color, s=14, marker='o', alpha=0.40,
                   edgecolors='none', zorder=1)


def plot_panel(ax, language, baseline_data, ivs_data, xlim, ylim,
               panel_label=None):
    """One language panel with bold background + individually labeled models."""
    plot_ivs_bold_background(ax, ivs_data)

    lang_data = baseline_data[baseline_data['language'] == language]

    texts = []
    for model in lang_data['model_name'].unique():
        subset = lang_data[lang_data['model_name'] == model]
        info = MODEL_DISPLAY.get(model, {'short': model[:8], 'color': '#555555'})
        vendor = MODEL_TO_VENDOR.get(model, 'Other')
        marker = VENDOR_MARKERS.get(vendor, 'o')
        x, y = subset['PC1'].values[0], subset['PC2'].values[0]

        ax.scatter(x, y, c=info['color'], s=55, marker=marker,
                   alpha=0.95, edgecolors='white', linewidths=0.5, zorder=4)

        texts.append((x, y, info['short'], info['color']))

    import matplotlib.patheffects as pe
    stroke = [pe.withStroke(linewidth=1.2, foreground='white')]
    try:
        from adjustText import adjust_text
        txt_objs = []
        for x, y, label, color in texts:
            t = ax.text(x, y, label, fontsize=5.5,
                        color=color, ha='center', va='bottom', zorder=5,
                        path_effects=stroke)
            txt_objs.append(t)
        adjust_text(txt_objs, ax=ax,
                    arrowprops=dict(arrowstyle='-', color='#999999',
                                    lw=0.4, alpha=0.6),
                    expand_points=(1.5, 1.5), expand_text=(1.2, 1.2),
                    force_points=(0.4, 0.4), force_text=(0.4, 0.4),
                    lim=600)
    except ImportError:
        for x, y, label, color in texts:
            ax.annotate(label, (x, y), fontsize=5.5,
                        color=color, ha='center', va='bottom',
                        xytext=(0, 3), textcoords='offset points', zorder=5,
                        path_effects=stroke)

    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.axhline(y=0, color='#CCCCCC', linestyle='--', linewidth=0.4, zorder=0)
    ax.axvline(x=0, color='#CCCCCC', linestyle='--', linewidth=0.4, zorder=0)

    for spine in ax.spines.values():
        spine.set_color('#555555')
        spine.set_linewidth(0.6)

    lang_name = LANGUAGE_NAMES.get(language, language)
    ax.set_title(lang_name, fontsize=13, fontweight='bold', pad=6, color='#1a1a1a')

    if panel_label:
        ax.text(-0.05, 1.08, panel_label, transform=ax.transAxes,
                fontsize=15, fontweight='bold', va='top', ha='right',
                color='#000000')


def make_model_legend(models):
    """Create legend with every model individually listed."""
    vendor_order = ['OpenAI', 'Anthropic', 'Google', 'Meta',
                    'Mistral', 'DeepSeek', 'Other']
    handles = []
    added = set()
    for vendor in vendor_order:
        for model in models:
            if MODEL_TO_VENDOR.get(model) != vendor or model in added:
                continue
            added.add(model)
            info = MODEL_DISPLAY.get(model, {'short': model[:10], 'color': '#555'})
            marker = VENDOR_MARKERS.get(vendor, 'o')
            handles.append(Line2D(
                [0], [0], marker=marker, color='none',
                markerfacecolor=info['color'], markersize=6,
                markeredgecolor='white', markeredgewidth=0.4,
                label=info['short']))
    return handles


def main():
    print("=" * 60)
    print("Generating Figure 2: LLM Baseline Values by Language (Nature Comms Style)")
    print("=" * 60)

    ivs_data = load_ivs_data()

    # Load baseline from the correct paper_data source (not SI Table_S6)
    baseline_data = pd.read_csv(BASELINE_DATA_PATH)
    print(f"Loaded baseline data from: {BASELINE_DATA_PATH}")

    baseline_data['model_name'] = baseline_data['model_name'].apply(
        lambda x: x.split('/')[-1] if '/' in x else x)
    EXCLUDED_MODELS = {'qwen3-1.7b', 'glm-4.6', 'qwq-32b'}
    baseline_data = baseline_data[
        baseline_data['language'].isin(LANGUAGES_ORDER) &
        ~baseline_data['model_name'].isin(EXCLUDED_MODELS)
    ].copy()

    print(f"IVS: {len(ivs_data)} countries")
    print(f"Baseline: {len(baseline_data)} records, "
          f"{baseline_data['model_name'].nunique()} models, "
          f"{baseline_data['language'].nunique()} languages")

    xlim, ylim = get_global_axis_limits(ivs_data, baseline_data)

    # Shared axes: eliminate redundant tick labels on interior panels
    fig, axes = plt.subplots(2, 3, figsize=(15, 8),
                              sharex=True, sharey=True,
                              gridspec_kw={'wspace': 0.08, 'hspace': 0.15})
    axes_flat = axes.flatten()
    panel_labels = ['A', 'B', 'C', 'D', 'E', 'F']

    for i, lang in enumerate(LANGUAGES_ORDER):
        plot_panel(axes_flat[i], lang, baseline_data, ivs_data, xlim, ylim,
                   panel_label=panel_labels[i])

    for i in range(len(LANGUAGES_ORDER), len(axes_flat)):
        axes_flat[i].set_visible(False)

    # ── Dual legend: Models (upper-right) + WVS Cultural Zones (lower-right) ──
    models = sorted(baseline_data['model_name'].unique())
    model_handles = make_model_legend(models)

    region_handles = [
        mpatches.Patch(color=color, label=region, alpha=0.45)
        for region, color in WVS_REGION_COLORS.items()
        if region not in {'Other', 'Baltic'}
    ]

    legend_font = {'family': 'Helvetica', 'size': 7.5}
    title_font = {'family': 'Helvetica', 'size': 9, 'weight': 'bold'}

    leg1 = fig.legend(
        handles=model_handles, loc='upper right',
        prop=legend_font, frameon=True, framealpha=0.95,
        edgecolor='#AAAAAA', title='LLM Models', title_fontproperties=title_font,
        bbox_to_anchor=(0.98, 0.95), labelspacing=0.4,
        handletextpad=0.4, borderpad=0.6)

    leg2 = fig.legend(
        handles=region_handles, loc='upper right',
        prop=legend_font, frameon=True, framealpha=0.95,
        edgecolor='#AAAAAA', title='WVS Cultural Regions', title_fontproperties=title_font,
        bbox_to_anchor=(0.98, 0.38), labelspacing=0.4,
        handletextpad=0.4, borderpad=0.6)

    fig.add_artist(leg1)

    fig.text(0.44, 0.02,
             r'$\longleftarrow$ Survival Values'
             r'          Self-Expression Values $\longrightarrow$',
             ha='center', fontsize=12, fontweight='bold', color='#1a1a1a')
    fig.text(0.02, 0.5,
             r'$\longleftarrow$ Traditional Values'
             r'          Secular-Rational Values $\longrightarrow$',
             va='center', rotation='vertical', fontsize=12,
             fontweight='bold', color='#1a1a1a')

    fig.subplots_adjust(left=0.06, right=0.84, bottom=0.08, top=0.94)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_base = OUTPUT_DIR / 'Fig2_baseline_intrinsic_values'
    out_base.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_base.with_suffix('.png'), dpi=600, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    fig.savefig(out_base.with_suffix('.pdf'), bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)

    print(f"\nSaved: {out_base.with_suffix('.png')}")
    print(f"Saved: {out_base.with_suffix('.pdf')}")

    print("\n--- Language Summary ---")
    for lang in LANGUAGES_ORDER:
        ld = baseline_data[baseline_data['language'] == lang]
        name = LANGUAGE_NAMES.get(lang, lang)
        print(f"  {name:>20s}: PC1={ld['PC1'].mean():.2f} +/- {ld['PC1'].std():.2f}, "
              f"PC2={ld['PC2'].mean():.2f} +/- {ld['PC2'].std():.2f}")

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == '__main__':
    main()
