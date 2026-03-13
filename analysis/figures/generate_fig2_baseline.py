"""
Generate Figure 2: LLM Intrinsic Values by Language (20 models x 6 languages).

Layout: 2x3 grid, one panel per language. Each panel shows 20 model points
(color = model) on the WVS cultural map with SVM decision boundaries.

Matches the style of SI FigS2-A2 (generate_figs2_baseline.py).

Font: Helvetica.

Input:  SI/pca/Table_S6_LLM_baseline_PCA_coordinates.csv
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
from matplotlib.lines import Line2D

from si_config import (
    load_ivs_data, load_baseline_data, get_global_axis_limits,
    plot_ivs_background, save_figure, get_model_color, get_short_model_name,
    REGION_COLORS, MODEL_COLORS, LANGUAGE_NAMES,
    POINT_SIZE_MEDIUM, ALPHA_BG,
    FONT_SIZE_AXIS_LABEL, FONT_SIZE_SUBTITLE,
)

plt.rcParams.update({
    'font.family': 'Helvetica',
    'font.size': 9,
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
})

OUTPUT_DIR = PROJECT_ROOT / 'results' / 'figures' / 'paper'
LANGUAGES_ORDER = ['ar', 'en', 'es', 'fr', 'ru', 'zh-cn']


def plot_panel(ax, language, baseline_data, ivs_data, xlim, ylim):
    """One language panel: SVM boundaries + IVS bg + per-model colored points."""
    plot_ivs_background(ax, ivs_data, alpha=ALPHA_BG)

    lang_data = baseline_data[baseline_data['language'] == language]

    for model in lang_data['model_name'].unique():
        subset = lang_data[lang_data['model_name'] == model]
        color = get_model_color(model)
        ax.scatter(subset['PC1'], subset['PC2'],
                   c=color, s=POINT_SIZE_MEDIUM, marker='o', alpha=0.9,
                   edgecolors='black', linewidths=0.8, zorder=3)

    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.5, alpha=0.3, zorder=0)
    ax.axvline(x=0, color='gray', linestyle='--', linewidth=0.5, alpha=0.3, zorder=0)
    ax.tick_params(labelsize=7)

    lang_name = LANGUAGE_NAMES.get(language, language)
    ax.set_title(lang_name, fontsize=9, pad=3)


def create_model_legend(models):
    handles = []
    for model in sorted(models):
        color = get_model_color(model)
        short_name = get_short_model_name(model)
        handles.append(Line2D([0], [0], marker='o', color='w',
                              markerfacecolor=color, markersize=8,
                              markeredgecolor='black', markeredgewidth=0.6,
                              label=short_name))
    return handles


def main():
    print("=" * 60)
    print("Generating Figure 2: LLM Baseline Values by Language")
    print("=" * 60)

    ivs_data = load_ivs_data()
    baseline_data = load_baseline_data()

    # Strip vendor prefix, filter to 6 core languages and 20 paper models
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

    n_cols = 3
    n_rows = 2
    fig, axes = plt.subplots(n_rows, n_cols,
                              figsize=(n_cols * 4, n_rows * 3.5))
    axes_flat = axes.flatten()

    for i, lang in enumerate(LANGUAGES_ORDER):
        plot_panel(axes_flat[i], lang, baseline_data, ivs_data, xlim, ylim)

    for i in range(len(LANGUAGES_ORDER), len(axes_flat)):
        axes_flat[i].set_visible(False)

    models = baseline_data['model_name'].unique()
    legend_handles = create_model_legend(models)
    fig.legend(handles=legend_handles, loc='center right',
               fontsize=7, framealpha=0.95, title='Model',
               bbox_to_anchor=(1.15, 0.5))

    fig.text(0.5, 0.02, 'Survival - Self-Expression',
             ha='center', fontsize=FONT_SIZE_AXIS_LABEL)
    fig.text(0.02, 0.5, 'Traditional - Secular-Rational',
             va='center', rotation='vertical', fontsize=FONT_SIZE_AXIS_LABEL)

    plt.tight_layout(rect=[0.03, 0.05, 0.88, 0.98])

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_base = OUTPUT_DIR / 'Fig2_baseline_intrinsic_values'
    save_figure(fig, out_base)

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
