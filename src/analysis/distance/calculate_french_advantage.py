#!/usr/bin/env python3
"""
Script 3: French Advantage for 12 Arabic Countries
Compares cultural distance when LLMs use Arabic vs French for 12 Arab countries.

    advantage(%) = (d_arabic - d_french) / d_arabic * 100

Positive => French gets closer to IVS truth (French advantage).

Because French interview data is not yet included in the standard PCA pipeline,
this script loads raw French interviews, converts them to IVS format, and
projects them through the fixed PCA model alongside Arabic data.

Input:
    - data/llm_pca/multilingual/roleplay_ml_pca_entity_scores_latest.pkl  (has Arabic PCA scores)
    - data/llm_interviews/multilingual/interview_raw/*/  (raw French JSON files)
    - data/country_values/pca_model_fixed.pkl
    - data/country_values/country_scores_pca.json

Output:
    - results/analysis/french_advantage_12_arab_countries.csv
    - results/analysis/french_advantage_summary.csv
"""

import sys
import json
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.base.ivs_question_processor import IVSQuestionProcessor

EXCLUDED_MODELS = ['qwen3-1.7b']

ARABIC_COUNTRIES_12 = [
    'Algeria', 'Egypt', 'Iraq', 'Jordan', 'Kuwait', 'Lebanon',
    'Libya', 'Morocco', 'Palestine', 'Qatar', 'Tunisia', 'Yemen',
]

IV_QNS = ['A008', 'A165', 'E018', 'E025', 'F063', 'F118', 'F120', 'G006', 'Y002', 'Y003']


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


def load_pca_model() -> dict:
    path = PROJECT_ROOT / 'data' / 'country_values' / 'pca_model_fixed.pkl'
    with open(path, 'rb') as f:
        return pickle.load(f)


def transform_with_pca(data: pd.DataFrame, pca_model: dict) -> tuple:
    """Apply the fixed PCA model to produce rescaled PC1, PC2 for each row."""
    ppca_C = pca_model['ppca_C']
    ppca_means = pca_model['ppca_means']
    ppca_stds = pca_model['ppca_stds']
    rotation_matrix = pca_model['rotation_matrix']
    pc_rescale = pca_model['pc_rescale_params']

    raw = data[IV_QNS].to_numpy(dtype=float)
    standardized = (raw - ppca_means) / ppca_stds
    standardized = np.nan_to_num(standardized, nan=0.0)

    pcs = standardized @ ppca_C
    rotated = pcs @ rotation_matrix

    pc1 = pc_rescale['PC1'][0] * rotated[:, 0] + pc_rescale['PC1'][1]
    pc2 = pc_rescale['PC2'][0] * rotated[:, 1] + pc_rescale['PC2'][1]
    return pc1, pc2


def load_arabic_from_pca() -> pd.DataFrame:
    """Load Arabic data for the 12 countries from existing PCA entity scores."""
    path = PROJECT_ROOT / 'data' / 'llm_pca' / 'multilingual' / 'roleplay_ml_pca_entity_scores_latest.pkl'
    df = pd.read_pickle(path)
    df = df[df['data_source'] != 'IVS'].copy()
    df = df[df['language'] == 'ar']
    df = df[df['Country'].isin(ARABIC_COUNTRIES_12)]
    df = df[~df['model_name'].isin(EXCLUDED_MODELS)]
    print(f"Arabic PCA entries (12 countries): {len(df)}")
    return df


def load_french_raw_interviews() -> pd.DataFrame:
    """
    Load and process raw French interview JSON files for the 12 Arab countries.
    Returns a DataFrame with IV_QNS columns ready for PCA projection.
    """
    raw_dir = PROJECT_ROOT / 'data' / 'llm_interviews' / 'multilingual' / 'interview_raw'
    processor = IVSQuestionProcessor()

    all_rows = []
    seen_keys = set()

    for model_dir in sorted(raw_dir.iterdir()):
        if not model_dir.is_dir():
            continue

        folder_name = model_dir.name

        if folder_name in EXCLUDED_MODELS:
            continue

        for jf in model_dir.glob('*_fr_*.json'):
            try:
                with open(jf, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except (json.JSONDecodeError, OSError):
                continue

            country = data.get('country', '')
            if country not in ARABIC_COUNTRIES_12:
                continue

            key = (folder_name, country, jf.name)
            if key in seen_keys:
                continue
            seen_keys.add(key)

            row = {'country': country, 'model_name': folder_name, 'language': 'fr'}
            for q in IV_QNS:
                row[q] = np.nan

            for resp in data.get('responses', []):
                qid = resp.get('question_id', '')
                if qid not in IV_QNS:
                    continue

                raw_answer = resp.get('final_response') or resp.get('processed_response', '')
                if not raw_answer:
                    continue

                result = processor.validate_and_process_response(str(raw_answer), qid)
                if not result['valid']:
                    continue

                if qid == 'Y002' and 'materialist_score' in result:
                    row[qid] = result['materialist_score']
                elif qid == 'Y003' and 'y003_score' in result:
                    row[qid] = result['y003_score']
                else:
                    row[qid] = result['numeric_value']

            all_rows.append(row)

    df = pd.DataFrame(all_rows)
    print(f"French raw interviews loaded: {len(df)} entries from {df['model_name'].nunique()} models")

    if not df.empty:
        print(f"  Countries: {sorted(df['country'].unique())}")

    return df


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
        fr_c = fr_pca[fr_pca['country'] == country]

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
    print("French Advantage — 12 Arabic Countries")
    print("=" * 70)

    ivs_coords = load_ivs_coordinates()
    pca_model = load_pca_model()

    # Arabic data from existing PCA results
    ar_pca = load_arabic_from_pca()

    # French data: load raw, process, project through PCA
    fr_raw = load_french_raw_interviews()
    if fr_raw.empty:
        print("No French interview data found. Exiting.")
        return

    print("\nProjecting French data through fixed PCA model...")
    pc1, pc2 = transform_with_pca(fr_raw, pca_model)
    fr_raw['PC1_rescaled'] = pc1
    fr_raw['PC2_rescaled'] = pc2

    # Aggregate per (model, country) to get entity-level scores
    fr_pca = fr_raw.groupby(['model_name', 'country']).agg({
        'PC1_rescaled': 'mean',
        'PC2_rescaled': 'mean',
        'language': 'first',
    }).reset_index()
    print(f"French entity-level entries: {len(fr_pca)}")

    # Calculate
    results = calculate_french_advantage(ar_pca, fr_pca, ivs_coords)
    print(f"\nFrench advantage entries: {len(results)}")

    if results.empty:
        print("No paired Arabic-French data found.")
        return

    # Summary
    overall_adv = (
        (results['d_arabic'].mean() - results['d_french'].mean()) /
        results['d_arabic'].mean() * 100
    )
    print(f"Overall French advantage: {overall_adv:+.1f}%")
    print(f"Countries: {results['country'].nunique()}, Models: {results['model_name'].nunique()}")

    print(f"\nPer country:")
    for country, g in results.groupby('country'):
        c_adv = (g['d_arabic'].mean() - g['d_french'].mean()) / g['d_arabic'].mean() * 100
        print(f"  {country:15s}  d_ar={g['d_arabic'].mean():.3f}  d_fr={g['d_french'].mean():.3f}  "
              f"advantage={c_adv:+.1f}%  n_models={len(g)}")

    # Save
    out_dir = PROJECT_ROOT / 'results' / 'analysis'
    out_dir.mkdir(parents=True, exist_ok=True)

    csv_path = out_dir / 'french_advantage_12_arab_countries.csv'
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
