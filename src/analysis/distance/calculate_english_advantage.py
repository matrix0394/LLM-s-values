#!/usr/bin/env python3
"""
Script 2: English Advantage Calculation
For every non-English-native country, compares the cultural distance when an LLM
uses English vs the country's native language.

    advantage(%) = (d_native - d_english) / d_native * 100

Positive value => English gets closer to IVS truth (English advantage).
Negative value => native language gets closer (native advantage).

Input:
    - data/llm_pca/multilingual/roleplay_ml_pca_entity_scores_latest.pkl
    - data/country_values/country_scores_pca.json

Output:
    - results/analysis/english_advantage_all_countries.csv
    - results/analysis/english_advantage_summary_by_region.csv
"""

import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

EXCLUDED_MODELS = ['qwen3-1.7b']

EN_NATIVE_COUNTRIES = [
    'Australia', 'Canada', 'Ghana', 'Ireland', 'Kenya',
    'Malaysia', 'Malta', 'New Zealand', 'Nigeria', 'Pakistan',
    'Philippines', 'Puerto Rico', 'Rwanda', 'Singapore',
    'South Africa', 'Trinidad and Tobago', 'United Kingdom',
    'United States of America', 'Zambia', 'Zimbabwe',
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


def load_roleplay_pca() -> pd.DataFrame:
    path = PROJECT_ROOT / 'data' / 'llm_pca' / 'multilingual' / 'roleplay_ml_pca_entity_scores_latest.pkl'
    df = pd.read_pickle(path)
    df = df[df['data_source'] != 'IVS'].copy()
    df = df[~df['model_name'].isin(EXCLUDED_MODELS)]
    return df


def match_country(country: str, ivs_coords: dict) -> Optional[str]:
    if country in ivs_coords:
        return country
    cl = country.lower().strip()
    for name in ivs_coords:
        if name.lower().strip() == cl:
            return name
    return None


def euclidean(pc1, pc2, ref_pc1, ref_pc2) -> float:
    return float(np.sqrt((pc1 - ref_pc1)**2 + (pc2 - ref_pc2)**2))


def calculate_english_advantage(df: pd.DataFrame, ivs_coords: dict) -> pd.DataFrame:
    """
    Per-model paired comparison: for each (model, country), compare
    d(native_lang, IVS) vs d(english, IVS).
    """
    # Exclude English-native countries
    df = df[~df['Country'].isin(EN_NATIVE_COUNTRIES)].copy()

    en_df = df[df['language'].isin(['en', 'en-native'])]
    native_df = df[~df['language'].isin(['en', 'en-native'])]

    if en_df.empty or native_df.empty:
        return pd.DataFrame()

    rows = []
    for country in native_df['Country'].dropna().unique():
        matched = match_country(country, ivs_coords)
        if matched is None:
            continue

        ivs = ivs_coords[matched]

        country_en = en_df[en_df['Country'] == country]
        country_nat = native_df[native_df['Country'] == country]

        native_langs = country_nat['language'].unique()

        for native_lang in native_langs:
            nat_lang_df = country_nat[country_nat['language'] == native_lang]

            for model in nat_lang_df['model_name'].unique():
                nat_m = nat_lang_df[nat_lang_df['model_name'] == model]
                en_m = country_en[country_en['model_name'] == model]

                if nat_m.empty or en_m.empty:
                    continue

                nat_pc1 = nat_m['PC1_rescaled'].mean()
                nat_pc2 = nat_m['PC2_rescaled'].mean()
                en_pc1 = en_m['PC1_rescaled'].mean()
                en_pc2 = en_m['PC2_rescaled'].mean()

                d_native = euclidean(nat_pc1, nat_pc2, ivs['PC1'], ivs['PC2'])
                d_en = euclidean(en_pc1, en_pc2, ivs['PC1'], ivs['PC2'])

                adv = (d_native - d_en) / d_native * 100 if d_native > 0 else 0.0

                rows.append({
                    'country': matched,
                    'native_language': native_lang,
                    'model_name': model,
                    'cultural_region': ivs['cultural_region'],
                    'is_islamic': ivs['is_islamic'],
                    'native_pc1': nat_pc1, 'native_pc2': nat_pc2,
                    'en_pc1': en_pc1, 'en_pc2': en_pc2,
                    'ivs_pc1': ivs['PC1'], 'ivs_pc2': ivs['PC2'],
                    'd_native': d_native,
                    'd_english': d_en,
                    'english_advantage_pct': adv,
                })

    return pd.DataFrame(rows)


def summarize_by_country(results: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate English advantage per country using the paper's method:
    avg distances across models first, then compute advantage from averages.
    """
    if results.empty:
        return pd.DataFrame()

    country_summary = results.groupby(['country', 'native_language', 'cultural_region', 'is_islamic']).agg(
        n_models=('model_name', 'nunique'),
        mean_d_native=('d_native', 'mean'),
        mean_d_english=('d_english', 'mean'),
    ).reset_index()

    country_summary['english_advantage_pct'] = (
        (country_summary['mean_d_native'] - country_summary['mean_d_english']) /
        country_summary['mean_d_native'] * 100
    )
    return country_summary.sort_values('english_advantage_pct', ascending=False)


def summarize_by_region(results: pd.DataFrame) -> pd.DataFrame:
    """Aggregate English advantage by cultural region using the paper's method."""
    if results.empty:
        return pd.DataFrame()

    summary = results.groupby('cultural_region').agg(
        n_entries=('english_advantage_pct', 'count'),
        n_countries=('country', 'nunique'),
        n_models=('model_name', 'nunique'),
        mean_d_native=('d_native', 'mean'),
        mean_d_english=('d_english', 'mean'),
    ).round(3)

    summary['region_advantage_pct'] = (
        (summary['mean_d_native'] - summary['mean_d_english']) /
        summary['mean_d_native'] * 100
    ).round(2)

    return summary.sort_values('region_advantage_pct', ascending=False)


def main():
    print("=" * 70)
    print("English Advantage Calculation — Non-English-Native Countries")
    print("=" * 70)

    ivs_coords = load_ivs_coordinates()
    print(f"IVS countries: {len(ivs_coords)}")

    df = load_roleplay_pca()
    print(f"Roleplay entries: {len(df)}, models: {df['model_name'].nunique()}, "
          f"countries: {df['Country'].dropna().nunique()}")

    results = calculate_english_advantage(df, ivs_coords)
    print(f"\nPer-model entries: {len(results)}")

    if results.empty:
        print("No results computed.")
        return

    # Country-level summary (paper's method: avg distances first, then advantage)
    country_summary = summarize_by_country(results)

    overall_adv = (
        (results['d_native'].mean() - results['d_english'].mean()) /
        results['d_native'].mean() * 100
    )
    print(f"Overall English advantage: {overall_adv:+.1f}%")
    print(f"Countries: {results['country'].nunique()}, Models: {results['model_name'].nunique()}")

    print(f"\nPer country (paper method: avg distances, then advantage):")
    for _, r in country_summary.iterrows():
        print(f"  {r['country']:<25s} d_nat={r['mean_d_native']:.3f}  d_en={r['mean_d_english']:.3f}  "
              f"adv={r['english_advantage_pct']:+.1f}%  n={int(r['n_models'])}")

    region_summary = summarize_by_region(results)
    print(f"\nBy cultural region:")
    print(region_summary[['n_countries', 'mean_d_native', 'mean_d_english', 'region_advantage_pct']].to_string())

    out_dir = PROJECT_ROOT / 'results' / 'analysis'
    out_dir.mkdir(parents=True, exist_ok=True)

    # Per-model detail
    csv_path = out_dir / 'english_advantage_all_countries.csv'
    results.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"\nSaved: {csv_path}")

    # Country summary
    country_path = out_dir / 'english_advantage_by_country.csv'
    country_summary.to_csv(country_path, index=False, encoding='utf-8')
    print(f"Saved: {country_path}")

    # Region summary
    summary_path = out_dir / 'english_advantage_summary_by_region.csv'
    region_summary.to_csv(summary_path, encoding='utf-8')
    print(f"Saved: {summary_path}")

    return results


if __name__ == '__main__':
    main()
