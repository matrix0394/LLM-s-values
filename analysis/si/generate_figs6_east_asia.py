#!/usr/bin/env python3
"""Generate FigS5: East Asia Analysis. Data source: SI/pca/ (self-contained)"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import warnings
warnings.filterwarnings('ignore')

from si_config import FIGURES_DIR, load_ivs_data, load_roleplay_data, save_figure

plt.rcParams.update({'font.family': 'Arial', 'font.size': 10, 'figure.dpi': 300})

# =============================================================================
# Unified Color Palette (same base as S4/S5)
# =============================================================================
COLOR_RED = '#E74C3C'     # Red
COLOR_GREEN = '#27AE60'   # Green
COLOR_BLUE = '#3498DB'    # Blue
COLOR_ORANGE = '#F39C12'  # Orange
COLOR_PURPLE = '#9B59B6'  # Purple
COLOR_CYAN = '#1ABC9C'    # Cyan
COLOR_GRAY = '#95A5A6'    # Gray

EA = {'Hong Kong': 'Hong Kong', 'Taiwan, Province of China': 'Taiwan', 'China': 'China',
      'Japan': 'Japan', 'Korea, Republic of': 'South Korea', 'Macao': 'Macao', 'Singapore': 'Singapore'}

# Country colors - 7 distinct colors for 7 regions
COL = {
    'China': COLOR_RED,
    'Hong Kong': COLOR_ORANGE,
    'Taiwan, Province of China': COLOR_PURPLE,
    'Japan': COLOR_BLUE,
    'Korea, Republic of': COLOR_GREEN,
    'Macao': COLOR_CYAN,
    'Singapore': COLOR_GRAY
}
MRK = {'zh-cn': 's', 'zh-tw': '^', 'zh-hk': 'v', 'ja': 'D', 'ko': 'p', 'pt': 'h', 'en': 'o'}
LNG = {'zh-cn': 'Chinese (Simplified)', 'zh-tw': 'Chinese (Traditional)', 'zh-hk': 'Cantonese',
       'ja': 'Japanese', 'ko': 'Korean', 'pt': 'Portuguese', 'en': 'English', 'en-native': 'English (native)'}

def compute_east_asia_data(ivs_df, roleplay_df):
    ivs_lk = ivs_df.set_index('country')[['PC1', 'PC2', 'cultural_region']].to_dict('index')
    res = []
    for _, r in roleplay_df.iterrows():
        c = r['country']
        if c not in EA and not any(k in c for k in EA): continue
        if c not in ivs_lk: continue
        iv = ivs_lk[c]
        d = np.sqrt((r['PC1'] - iv['PC1'])**2 + (r['PC2'] - iv['PC2'])**2)
        res.append({'model_name': r['model_name'], 'country': c, 'language': r['language'],
                   'llm_PC1': r['PC1'], 'llm_PC2': r['PC2'], 'real_PC1': iv['PC1'], 'real_PC2': iv['PC2'],
                   'cultural_region': iv['cultural_region'], 'distance': d})
    ea_d = pd.DataFrame(res)
    if len(ea_d) == 0: return pd.DataFrame(), pd.DataFrame()
    la = ea_d.groupby(['country', 'language'])['distance'].mean().reset_index()
    adv = []
    for c in la['country'].unique():
        cd = la[la['country'] == c]
        en = cd[cd['language'].isin(['en', 'en-native'])]
        if len(en) == 0: continue
        en_d = en['distance'].min()
        nat = cd[~cd['language'].isin(['en', 'en-native'])]
        if len(nat) == 0: continue
        nr = nat.loc[nat['distance'].idxmin()]
        nd, nl = nr['distance'], nr['language']
        a = ((nd - en_d) / nd) * 100 if nd > 0 else 0
        adv.append({'country': c, 'native_language': nl, 'en_distance': en_d, 'native_distance': nd, 'english_advantage': a})
    ea_a = pd.DataFrame(adv)
    print(f"East Asia: {len(ea_d)} rows, {ea_d['country'].nunique()} countries")
    return ea_d, ea_a


def rm_out(df, cols=['llm_PC1', 'llm_PC2'], n=2.5):
    d = df.copy()
    for c in cols:
        if c not in d.columns: continue
        m, s = d[c].mean(), d[c].std()
        d = d[(d[c] >= m - n * s) & (d[c] <= m + n * s)]
    return d

def gen_s6a(ea_d, od):
    print("Generating FigS5A...")
    if len(ea_d) == 0: print("  No data"); return
    ea = rm_out(ea_d)
    fig, ax = plt.subplots(figsize=(14, 12))
    for c in ea['country'].unique():
        cd = ea[ea['country'] == c]
        ax.scatter(cd['llm_PC1'], cd['llm_PC2'], c=COL.get(c, COLOR_GRAY), alpha=0.15, s=30)
    rl = ea.groupby('country')[['real_PC1', 'real_PC2']].first().reset_index()
    for _, r in rl.iterrows():
        c, cl = r['country'], COL.get(r['country'], COLOR_GRAY)
        ax.scatter(r['real_PC1'], r['real_PC2'], c=cl, s=300, marker='*', edgecolors='black', linewidths=1.5, zorder=10)
        ax.annotate(EA.get(c, c), (r['real_PC1'], r['real_PC2']), xytext=(8, 8), textcoords='offset points',
                   fontsize=11, fontweight='bold', color=cl, bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    for c in ea['country'].unique():
        cd = ea[ea['country'] == c]
        if len(cd) == 0: continue
        cl, rp1, rp2 = COL.get(c, COLOR_GRAY), cd['real_PC1'].iloc[0], cd['real_PC2'].iloc[0]
        la = cd.groupby('language').agg({'llm_PC1': 'mean', 'llm_PC2': 'mean'}).reset_index()
        for _, lr in la.iterrows():
            l, lp1, lp2 = lr['language'], lr['llm_PC1'], lr['llm_PC2']
            ax.plot([rp1, lp1], [rp2, lp2], '--', color=cl, alpha=0.6, linewidth=1.5)
            ax.scatter(lp1, lp2, c=cl, s=120, marker=MRK.get(l, 'o'), edgecolors='black', linewidths=1, zorder=8)
            ax.annotate(LNG.get(l, l), (lp1, lp2), xytext=(5, 5), textcoords='offset points',
                       fontsize=8, color=cl, fontweight='bold', bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))
    ax.set_xlabel('PC1: Survival - Self-Expression', fontsize=13, fontweight='bold')
    ax.set_ylabel('PC2: Traditional - Secular-Rational', fontsize=13, fontweight='bold')
    ax.set_title('FigS5A: East Asia Cultural Coordinate Trajectory', fontsize=14, fontweight='bold', pad=20)
    ax.axhline(0, color='gray', linestyle='-', linewidth=0.5, alpha=0.5)
    ax.axvline(0, color='gray', linestyle='-', linewidth=0.5, alpha=0.5)
    ax.grid(True, alpha=0.3, linestyle='--')
    cleg = [Line2D([0], [0], marker='*', color='w', markerfacecolor=cl, markersize=15, markeredgecolor='black',
                   label=EA.get(c, c)) for c, cl in COL.items() if c in ea['country'].unique()]
    lleg = [Line2D([0], [0], marker=m, color='w', markerfacecolor='gray', markersize=10, markeredgecolor='black',
                   label=LNG.get(l, l)) for l, m in MRK.items() if l in ea['language'].unique()]
    if cleg: ax.add_artist(ax.legend(handles=cleg, loc='upper left', title='Country/Region', fontsize=9))
    if lleg: ax.legend(handles=lleg, loc='lower right', title='Language', fontsize=9)
    plt.tight_layout()
    save_figure(fig, od / 'FigS5A_east_asia_trajectory')
    print("  ✅ Saved: FigS5A_east_asia_trajectory")


def gen_s6b(ea_d, od):
    print("Generating FigS5B...")
    if len(ea_d) == 0: print("  No data"); return
    dl = ea_d.groupby(['country', 'language'])['distance'].mean().reset_index()
    fig, ax = plt.subplots(figsize=(14, 8))
    cs, ls = sorted(ea_d['country'].unique()), sorted(ea_d['language'].unique())
    x, w = np.arange(len(cs)), 0.8 / len(ls)
    cls = plt.cm.tab10(np.linspace(0, 1, len(ls)))
    for i, l in enumerate(ls):
        ld = dl[dl['language'] == l]
        d = [ld[ld['country'] == c]['distance'].values[0] if c in ld['country'].values else 0 for c in cs]
        ax.bar(x + i * w - w * len(ls) / 2, d, w, label=LNG.get(l, l), color=cls[i], alpha=0.8, edgecolor='black', linewidth=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels([EA.get(c, c.replace(', Province of China', '')) for c in cs], rotation=15, ha='right')
    ax.set_ylabel('Cultural Distance', fontsize=12)
    ax.set_xlabel('Country/Region', fontsize=12)
    ax.set_title('FigS5B: East Asia Cultural Distance by Language\n(Lower = Better imitation)', fontsize=14, fontweight='bold', pad=15)
    ax.legend(title='Language', loc='upper right', fontsize=8)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    save_figure(fig, od / 'FigS5B_east_asia_distance_comparison')
    print("  ✅ Saved: FigS5B_east_asia_distance_comparison")

def gen_s6c(ea_a, od):
    print("Generating FigS5C...")
    if len(ea_a) == 0: print("  No data"); return
    ea = ea_a.sort_values('english_advantage', ascending=False)
    fig, ax = plt.subplots(figsize=(12, 8))
    lbs = [f"{EA.get(r['country'], r['country'][:25])}\n({LNG.get(r['native_language'], r['native_language'])})" for _, r in ea.iterrows()]
    # Color by English advantage level using unified palette
    cls = [COLOR_RED if x > 20 else COLOR_ORANGE if x > 10 else COLOR_GREEN if x > 0 else COLOR_BLUE for x in ea['english_advantage']]
    bars = ax.barh(range(len(ea)), ea['english_advantage'], color=cls, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax.set_yticks(range(len(ea)))
    ax.set_yticklabels(lbs, fontsize=10)
    ax.set_xlabel('English Advantage (%)', fontsize=12, fontweight='bold')
    ax.set_title('FigS5C: East Asia English Advantage Gradient\n(All models averaged)', fontsize=14, fontweight='bold', pad=20)
    ax.axvline(0, color='black', linestyle='-', linewidth=1)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.invert_yaxis()
    for i, (b, v) in enumerate(zip(bars, ea['english_advantage'])):
        ax.text(v + 1, i, f'{v:+.1f}%', va='center', fontsize=10, fontweight='bold')
    leg = [mpatches.Patch(facecolor=COLOR_RED, alpha=0.8, label='Strong (>20%)'),
           mpatches.Patch(facecolor=COLOR_ORANGE, alpha=0.8, label='Medium (10-20%)'),
           mpatches.Patch(facecolor=COLOR_GREEN, alpha=0.8, label='Weak (0-10%)'),
           mpatches.Patch(facecolor=COLOR_BLUE, alpha=0.8, label='Native Advantage (<0%)')]
    ax.legend(handles=leg, loc='lower right', fontsize=9)
    plt.tight_layout()
    save_figure(fig, od / 'FigS5C_east_asia_english_gradient')
    print("  ✅ Saved: FigS5C_east_asia_english_gradient")

def main():
    print("=" * 60)
    print("Generating FigS5: East Asia Analysis")
    print("Data source: SI/pca/ (self-contained)")
    print("=" * 60)
    od = FIGURES_DIR / 'S5_East_Asia_analysis'
    od.mkdir(parents=True, exist_ok=True)
    print("\nLoading data from SI/pca...")
    ivs, rp = load_ivs_data(), load_roleplay_data()
    print(f"  IVS: {len(ivs)} countries, Roleplay: {len(rp)} records")
    print("\nComputing East Asia data...")
    ea_d, ea_a = compute_east_asia_data(ivs, rp)
    print("\nGenerating figures...")
    gen_s6a(ea_d, od)
    gen_s6b(ea_d, od)
    gen_s6c(ea_a, od)
    print("\n" + "=" * 60)
    print(f"✅ All FigS5 figures saved to: {od}")
    print("=" * 60)

if __name__ == '__main__':
    main()
