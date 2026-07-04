#!/usr/bin/env python3
"""
French Advantage for 12 Arabic-speaking countries (standalone copy of logic).

    advantage(%) = (d_arabic - d_french) / d_arabic * 100

Positive => French roleplay is closer to IVS than Arabic.

Canonical implementation (kept in sync): ``compute_french_advantage`` in
``src/run/run_paper_analysis.py``. Run the full paper pipeline with::

    python src/run/run_paper_analysis.py --study 3

Arabic AND French coordinates must come from the same file
``roleplay_ml_pca_entity_scores_latest.pkl`` (unified PCA). Do not re-project
French from raw JSON only — that desynchronises coordinates vs Arabic.

Input:
    - data/llm_pca/multilingual/roleplay_ml_pca_entity_scores_latest.pkl
    - data/country_values/country_scores_pca.json

Output:
    - results/analysis/french_advantage_12_arab_countries_standalone.csv
    - results/analysis/french_advantage_summary.csv
"""

import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

EXCLUDED_MODELS = ['qwen3-1.7b', 'glm-4.6', 'qwq-32b']

ARABIC_COUNTRIES_12 = [
    'Algeria', 'Egypt', 'Iraq', 'Jordan', 'Kuwait', 'Lebanon',
    'Libya', 'Morocco', 'Palestine', 'Qatar', 'Tunisia', 'Yemen',
]

def load_ivs_coordinates() -> dict:
    json_path = PROJECT_ROOT / 'data' / 'country_values' / 'country_scores_pca.json'
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)
    coords = {}
    for item in data:
        c = item.get('Country')
        pc1, pc2 = item.get('PC1_rescaled'), item.get('PC2_rescaled')
        if c and pc1 is not None and pc2 is not None:
            coords[c] = {
                'PC1': float(pc1), 'PC2': float(pc2),
                'cultural_region': item.get('Cultural Region', ''),
                'is_islamic': item.get('Islamic', False),
            }
    return coords


def load_roleplay_ar_fr_12() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Arabic and French rows for 12 countries from unified roleplay PCA pkl."""
    path = PROJECT_ROOT / 'data' / 'llm_pca' / 'multilingual' / 'roleplay_ml_pca_entity_scores_latest.pkl'
    df = pd.read_pickle(path)
    df = df[df['data_source'] != 'IVS'].copy()
    df = df[~df['model_name'].isin(EXCLUDED_MODELS)]
    df = df[df['model_name'].notna()]

    ar = df[(df['language'] == 'ar') & (df['Country'].isin(ARABIC_COUNTRIES_12))]
    fr = df[(df['language'] == 'fr') & (df['Country'].isin(ARABIC_COUNTRIES_12))]
    fr = fr[~fr['model_name'].astype(str).str.contains('phi-3', case=False, na=False)]
    print(f"Arabic PCA entries (12 countries): {len(ar)}")
    print(f"French PCA entries (12 countries): {len(fr)}")
    return ar, fr


def euclidean(pc1, pc2, ref1, ref2) -> float:
    return float(np.sqrt((pc1 - ref1)**2 + (pc2 - ref2)**2))


def calculate_french_advantage(
    ar_pca: pd.DataFrame, fr_pca: pd.DataFrame, ivs_coords: dict
) -> pd.DataFrame:
    """
    Per-model paired comparison for 12 Arab countries:
    compare d(Arabic, IVS) vs d(French, IVS).
    """
    rows = []

    for country in ARABIC_COUNTRIES_12:
        if country not in ivs_coords:
            print(f"  Skipping {country}: not in IVS")
            continue

        ivs = ivs_coords[country]
        ar_c = ar_pca[ar_pca['Country'] == country]
        fr_c = fr_pca[fr_pca['Country'] == country]

        for model in ar_c['model_name'].unique():
            ar_m = ar_c[ar_c['model_name'] == model]
            fr_m = fr_c[fr_c['model_name'] == model]

            if ar_m.empty or fr_m.empty:
                continue

            ar_pc1 = ar_m['PC1_rescaled'].mean()
            ar_pc2 = ar_m['PC2_rescaled'].mean()
            fr_pc1 = fr_m['PC1_rescaled'].mean()
            fr_pc2 = fr_m['PC2_rescaled'].mean()

            d_ar = euclidean(ar_pc1, ar_pc2, ivs['PC1'], ivs['PC2'])
            d_fr = euclidean(fr_pc1, fr_pc2, ivs['PC1'], ivs['PC2'])

            adv = (d_ar - d_fr) / d_ar * 100 if d_ar > 0 else 0.0

            rows.append({
                'country': country,
                'model_name': model,
                'cultural_region': ivs['cultural_region'],
                'ar_pc1': ar_pc1, 'ar_pc2': ar_pc2,
                'fr_pc1': fr_pc1, 'fr_pc2': fr_pc2,
                'ivs_pc1': ivs['PC1'], 'ivs_pc2': ivs['PC2'],
                'd_arabic': d_ar,
                'd_french': d_fr,
                'french_advantage_pct': adv,
            })

    return pd.DataFrame(rows)


def main():
    print("=" * 70)
    print("French Advantage — 12 Arabic Countries (unified PCA pkl)")
    print("=" * 70)

    ivs_coords = load_ivs_coordinates()
    ar_pca, fr_pca = load_roleplay_ar_fr_12()

    if fr_pca.empty:
        print("No French PCA rows. Exiting.")
        return

    results = calculate_french_advantage(ar_pca, fr_pca, ivs_coords)
    print(f"\nFrench advantage entries: {len(results)}")

    if results.empty:
        print("No paired Arabic-French data found.")
        return

    overall_adv = (
        (results['d_arabic'].mean() - results['d_french'].mean()) /
        results['d_arabic'].mean() * 100
    )
    med = float(np.median(results['french_advantage_pct'].values))
    print(f"Overall French advantage (grand-mean %): {overall_adv:+.1f}%")
    print(f"Median pairwise FA%: {med:+.1f}%")
    print(f"Countries: {results['country'].nunique()}, Models: {results['model_name'].nunique()}")

    print(f"\nPer country:")
    for country, g in results.groupby('country'):
        c_adv = (g['d_arabic'].mean() - g['d_french'].mean()) / g['d_arabic'].mean() * 100
        print(f"  {country:15s}  d_ar={g['d_arabic'].mean():.3f}  d_fr={g['d_french'].mean():.3f}  "
              f"advantage={c_adv:+.1f}%  n_models={len(g)}")

    out_dir = PROJECT_ROOT / 'results' / 'analysis'
    out_dir.mkdir(parents=True, exist_ok=True)

    csv_path = out_dir / 'french_advantage_12_arab_countries_standalone.csv'
    results.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"\nSaved: {csv_path}")

    # Summary table
    summary = results.groupby('country').agg(
        n_models=('model_name', 'nunique'),
        mean_d_arabic=('d_arabic', 'mean'),
        mean_d_french=('d_french', 'mean'),
        mean_advantage=('french_advantage_pct', 'mean'),
        median_advantage=('french_advantage_pct', 'median'),
    ).round(3)
    summary['country_advantage_pct'] = (
        (summary['mean_d_arabic'] - summary['mean_d_french']) /
        summary['mean_d_arabic'] * 100
    ).round(2)

    summary_path = out_dir / 'french_advantage_summary.csv'
    summary.to_csv(summary_path, encoding='utf-8')
    print(f"Saved: {summary_path}")

    return results


if __name__ == '__main__':
    main()
