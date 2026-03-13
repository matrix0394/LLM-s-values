#!/usr/bin/env python3
"""
Script 1: Cultural Distance Calculation
Computes Euclidean distance between LLM roleplay/intrinsic coordinates and IVS real coordinates
for all model-country-language combinations.

Input:
    - data/llm_pca/multilingual/roleplay_ml_pca_entity_scores_latest.pkl
    - data/llm_pca/intrinsic/llm_pca_entity_scores.pkl  (optional)
    - data/country_values/country_scores_pca.json

Output:
    - results/analysis/cultural_distance_all.csv
    - results/analysis/cultural_distance_all.json
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
    """Load IVS real-country mean PCA coordinates."""
    json_path = PROJECT_ROOT / 'data' / 'country_values' / 'country_scores_pca.json'
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)

    coords = {}
    for item in data:
        country = item.get('Country')
        pc1, pc2 = item.get('PC1_rescaled'), item.get('PC2_rescaled')
        if country and pc1 is not None and pc2 is not None:
            coords[country] = {
                'PC1': float(pc1), 'PC2': float(pc2),
                'cultural_region': item.get('Cultural Region', ''),
                'is_islamic': item.get('Islamic', False),
            }
    print(f"Loaded IVS coordinates: {len(coords)} countries")
    return coords


def load_pca_data(source: str) -> pd.DataFrame:
    """Load PCA entity scores for a given source ('multilingual' or 'intrinsic')."""
    if source == 'multilingual':
        path = PROJECT_ROOT / 'data' / 'llm_pca' / 'multilingual' / 'roleplay_ml_pca_entity_scores_latest.pkl'
    else:
        path = PROJECT_ROOT / 'data' / 'llm_pca' / 'intrinsic' / 'llm_pca_entity_scores.pkl'

    if not path.exists():
        print(f"  [{source}] PCA file not found: {path}")
        return pd.DataFrame()

    df = pd.read_pickle(path)
    df = df[df['data_source'] != 'IVS'].copy()
    print(f"  [{source}] Loaded {len(df)} LLM entries")
    return df


def match_country(country, ivs_coords: dict) -> Optional[str]:
    if not isinstance(country, str) or not country:
        return None
    if country in ivs_coords:
        return country
    cl = country.lower().strip()
    for name in ivs_coords:
        if name.lower().strip() == cl:
            return name
    return None


def calculate_distances(llm_df: pd.DataFrame, ivs_coords: dict, source_label: str) -> pd.DataFrame:
    """Euclidean distance between each LLM entry and matched IVS country."""
    rows = []
    for _, row in llm_df.iterrows():
        model = row.get('model_name', '')
        country = row.get('Country') or row.get('country', '')
        language = row.get('language', '')
        pc1, pc2 = row.get('PC1_rescaled'), row.get('PC2_rescaled')

        if pd.isna(pc1) or pd.isna(pc2) or not country or model in EXCLUDED_MODELS:
            continue

        matched = match_country(country, ivs_coords)
        if matched is None:
            continue

        ivs = ivs_coords[matched]
        dist = np.sqrt((pc1 - ivs['PC1'])**2 + (pc2 - ivs['PC2'])**2)

        rows.append({
            'model_name': model,
            'country': matched,
            'language': language,
            'cultural_region': ivs['cultural_region'],
            'is_islamic': ivs['is_islamic'],
            'llm_pc1': float(pc1),
            'llm_pc2': float(pc2),
            'ivs_pc1': ivs['PC1'],
            'ivs_pc2': ivs['PC2'],
            'cultural_distance': float(dist),
            'source': source_label,
        })
    return pd.DataFrame(rows)


def summarize(df: pd.DataFrame):
    print(f"\n{'=' * 60}")
    print(f"Total: {len(df)} entries, {df['model_name'].nunique()} models, "
          f"{df['country'].nunique()} countries, {df['language'].nunique()} languages")
    print(f"Mean distance: {df['cultural_distance'].mean():.3f}, "
          f"Median: {df['cultural_distance'].median():.3f}")

    print(f"\nBy cultural region:")
    for region, g in df.groupby('cultural_region'):
        print(f"  {region:30s} mean={g['cultural_distance'].mean():.3f}  n={len(g)}")

    print(f"\nBy language:")
    for lang, g in df.groupby('language'):
        print(f"  {lang:12s} mean={g['cultural_distance'].mean():.3f}  n={len(g)}")


def main():
    print("=" * 70)
    print("Cultural Distance Calculation — All Languages")
    print("=" * 70)

    ivs_coords = load_ivs_coordinates()
    parts = []

    for source in ['multilingual', 'intrinsic']:
        df = load_pca_data(source)
        if not df.empty:
            d = calculate_distances(df, ivs_coords, source)
            parts.append(d)
            print(f"  {source}: {len(d)} distance rows")

    if not parts:
        print("No distance data computed.")
        return

    all_dist = pd.concat(parts, ignore_index=True)
    summarize(all_dist)

    out_dir = PROJECT_ROOT / 'results' / 'analysis'
    out_dir.mkdir(parents=True, exist_ok=True)

    csv_path = out_dir / 'cultural_distance_all.csv'
    all_dist.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"\nSaved: {csv_path}")

    json_path = out_dir / 'cultural_distance_all.json'
    all_dist.to_json(json_path, orient='records', indent=2, force_ascii=False)
    print(f"Saved: {json_path}")

    return all_dist


if __name__ == '__main__':
    main()
