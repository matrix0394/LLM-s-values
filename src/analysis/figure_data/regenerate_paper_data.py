#!/usr/bin/env python3
"""
Regenerate all paper_data files for the 4 main figures.

Figure 1: 4 choropleth maps — LLM English PC1/PC2 (20-model mean) + WVS PC1/PC2
          for all countries that have both LLM roleplay and WVS data.
Figure 2: 6 languages × 20 models intrinsic/baseline PCA coordinates.
Figure 3: Digital orientalism — distance data for Middle East + East Asia.
Figure 4: Colonial legacies — distance data for Sub-Saharan Africa + Latin America.
          Sub-Saharan Africa includes 6 British colonies + 2 French colonies = 8 countries.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

PAPER_DATA_DIR = PROJECT_ROOT / "results" / "paper_data"
PAPER_DATA_DIR.mkdir(parents=True, exist_ok=True)

EXCLUDED_MODELS = {"qwen3-1.7b", "glm-4.6", "qwq-32b",
                   "z-ai/glm-4.6", "qwen/qwq-32b", "qwen3-1.7b"}

MODEL_NAME_MAP = {
    "anthropic/claude-sonnet-4.5": "claude-sonnet-4.5",
    "deepseek/deepseek-chat-v3.1": "deepseek-chat-v3.1",
    "google/gemini-2.5-flash": "gemini-2.5-flash",
    "google/gemini-2.5-pro": "gemini-2.5-pro",
    "google/gemini-3-pro-preview": "gemini-3-pro-preview",
    "google/gemma-3-4b-it": "gemma-3-4b-it",
    "meta-llama/llama-3.2-3b-instruct": "llama-3.2-3b-instruct",
    "meta-llama/llama-3.3-70b-instruct": "llama-3.3-70b-instruct",
    "microsoft/phi-3-mini-128k-instruct": "phi-3-mini-128k-instruct",
    "mistralai/mistral-medium-3.1": "mistral-medium-3.1",
    "mistralai/mistral-nemo": "mistral-nemo",
    "openai/gpt-5.1": "gpt-5.1",
    "qwen/qwen3-max": "qwen3-max",
    "x-ai/grok-4.1-fast": "grok-4.1-fast",
}

EN_NATIVE_COUNTRIES = {
    "Australia", "Canada", "Ghana", "Ireland", "Kenya",
    "Malaysia", "Malta", "New Zealand", "Nigeria", "Pakistan",
    "Philippines", "Puerto Rico", "Rwanda", "Singapore",
    "South Africa", "Trinidad and Tobago", "United Kingdom",
    "United States of America", "Zambia", "Zimbabwe",
}


def normalize_model_name(name):
    return MODEL_NAME_MAP.get(name, name)


def is_excluded(model_name):
    raw = model_name
    normed = normalize_model_name(model_name)
    return raw in EXCLUDED_MODELS or normed in EXCLUDED_MODELS


def load_ivs_coordinates():
    path = PROJECT_ROOT / "data" / "country_values" / "country_scores_pca.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    coords = {}
    for item in data:
        c = item.get("Country")
        pc1, pc2 = item.get("PC1_rescaled"), item.get("PC2_rescaled")
        if c and pc1 is not None and pc2 is not None:
            coords[c] = {
                "PC1": float(pc1), "PC2": float(pc2),
                "cultural_region": item.get("Cultural Region", ""),
                "is_islamic": item.get("Islamic", False),
            }
    return coords


def euclidean(a1, a2, b1, b2):
    return float(np.sqrt((a1 - b1) ** 2 + (a2 - b2) ** 2))


# =========================================================================
# Figure 1: Choropleth maps — LLM English PC1/PC2 + WVS PC1/PC2
# =========================================================================

def generate_figure1():
    print("=" * 60)
    print("Figure 1: LLM English roleplay PC1/PC2 + WVS PC1/PC2")
    print("=" * 60)

    roleplay = pd.read_csv(
        PROJECT_ROOT / "SI" / "pca" / "Table_S7_LLM_roleplay_PCA_coordinates.csv"
    )
    roleplay["model_name"] = roleplay["model_name"].map(
        lambda x: normalize_model_name(x)
    )
    roleplay = roleplay[~roleplay["model_name"].apply(is_excluded)]

    en_df = roleplay[roleplay["language"].isin(["en", "en-native"])].copy()
    countries_with_en = set(en_df[en_df["language"] == "en"]["country"].unique())
    en_df = en_df[
        ~((en_df["language"] == "en-native") & en_df["country"].isin(countries_with_en))
    ]

    country_means = en_df.groupby("country").agg(
        LLM_EN_PC1=("PC1", "mean"),
        LLM_EN_PC2=("PC2", "mean"),
    ).reset_index()

    ivs = load_ivs_coordinates()
    ivs_df = pd.DataFrame([
        {"country": c, "WVS_PC1": v["PC1"], "WVS_PC2": v["PC2"],
         "cultural_region": v["cultural_region"],
         "is_islamic": int(v["is_islamic"])}
        for c, v in ivs.items()
    ])

    merged = country_means.merge(ivs_df, on="country", how="inner")
    merged = merged.sort_values(["cultural_region", "country"])

    n_models = en_df["model_name"].nunique()
    print(f"  Models: {n_models}")
    print(f"  Countries with LLM English data: {len(country_means)}")
    print(f"  Countries with WVS data: {len(ivs_df)}")
    print(f"  Matched countries: {len(merged)}")
    print(f"  Cultural regions: {merged['cultural_region'].value_counts().to_dict()}")

    for col in ["LLM_EN_PC1", "LLM_EN_PC2", "WVS_PC1", "WVS_PC2"]:
        merged[col] = merged[col].round(3)

    out = PAPER_DATA_DIR / f"figure1_data_{len(merged)}countries.csv"
    merged.to_csv(out, index=False)
    print(f"  Saved: {out}")

    old_66 = PAPER_DATA_DIR / "figure1_data_66countries.csv"
    if old_66.exists() and out.name != old_66.name:
        old_66.unlink()
        print(f"  Removed outdated: {old_66.name}")

    return merged


# =========================================================================
# Figure 2: 6 languages × 20 models intrinsic baseline
# =========================================================================

def generate_figure2():
    print("\n" + "=" * 60)
    print("Figure 2: 6 languages × 20 models baseline PCA")
    print("=" * 60)

    df = pd.read_csv(
        PROJECT_ROOT / "SI" / "pca" / "Table_S6_LLM_baseline_PCA_coordinates.csv"
    )
    df["model_name"] = df["model_name"].map(lambda x: normalize_model_name(x))
    df = df[~df["model_name"].apply(is_excluded)]

    languages = sorted(df["language"].unique())
    n_models = df["model_name"].nunique()
    models = sorted(df["model_name"].unique())

    print(f"  Models: {n_models}")
    print(f"  Languages: {languages}")
    print(f"  Total records: {len(df)}")

    out_detail = PAPER_DATA_DIR / "figure2_baseline_20models.csv"
    df_out = df[["model_name", "language", "PC1", "PC2"]].copy()
    df_out = df_out.sort_values(["language", "model_name"])
    df_out.to_csv(out_detail, index=False)
    print(f"  Saved detail: {out_detail}")

    lang_names = {
        "ar": "Arabic", "zh-cn": "Chinese", "en": "English",
        "fr": "French", "ru": "Russian", "es": "Spanish",
    }
    lang_stats = df.groupby("language").agg(
        PC1_mean=("PC1", "mean"), PC1_std=("PC1", "std"),
        PC2_mean=("PC2", "mean"), PC2_std=("PC2", "std"),
        n_models=("model_name", "nunique"),
    ).reset_index()
    lang_stats["language_name"] = lang_stats["language"].map(lang_names)
    for col in ["PC1_mean", "PC1_std", "PC2_mean", "PC2_std"]:
        lang_stats[col] = lang_stats[col].round(3)

    out_summary = PAPER_DATA_DIR / "figure2_language_summary.csv"
    lang_stats.to_csv(out_summary, index=False)
    print(f"  Saved summary: {out_summary}")

    return df_out


# =========================================================================
# Figure 3: Digital orientalism — Middle East + East Asia distance
# =========================================================================

def generate_figure3():
    print("\n" + "=" * 60)
    print("Figure 3: Digital Orientalism — Middle East + East Asia distance")
    print("=" * 60)

    ivs = load_ivs_coordinates()
    roleplay = pd.read_csv(
        PROJECT_ROOT / "SI" / "pca" / "Table_S7_LLM_roleplay_PCA_coordinates.csv"
    )
    roleplay["model_name"] = roleplay["model_name"].map(lambda x: normalize_model_name(x))
    roleplay = roleplay[~roleplay["model_name"].apply(is_excluded)]
    roleplay = roleplay[roleplay["data_source"] == "LLM"]

    middle_east = [
        "Algeria", "Egypt", "Iraq", "Jordan", "Kuwait", "Lebanon",
        "Libya", "Morocco", "Palestine", "Qatar", "Tunisia", "Yemen",
    ]
    east_asia = [
        "China", "Japan", "Korea, Republic of",
        "Taiwan, Province of China", "Hong Kong", "Macao",
    ]
    all_countries = middle_east + east_asia

    native_lang_map = {
        "Algeria": "ar", "Egypt": "ar", "Iraq": "ar", "Jordan": "ar",
        "Kuwait": "ar", "Lebanon": "ar", "Libya": "ar", "Morocco": "ar",
        "Palestine": "ar", "Qatar": "ar", "Tunisia": "ar", "Yemen": "ar",
        "China": "zh-cn", "Japan": "ja", "Korea, Republic of": "ko",
        "Taiwan, Province of China": "zh-tw", "Hong Kong": "zh-hk",
        "Macao": "pt",
    }

    rows = []
    for country in all_countries:
        if country not in ivs:
            print(f"  WARNING: {country} not in IVS coordinates, skipping")
            continue
        ivs_c = ivs[country]
        native_lang = native_lang_map.get(country)
        if not native_lang:
            continue

        c_data = roleplay[roleplay["country"] == country]
        en_data = c_data[c_data["language"].isin(["en", "en-native"])]
        nat_data = c_data[c_data["language"] == native_lang]

        if en_data.empty or nat_data.empty:
            print(f"  WARNING: {country} missing en or {native_lang} data")
            continue

        d_en_list, d_nat_list = [], []
        for model in nat_data["model_name"].unique():
            en_m = en_data[en_data["model_name"] == model]
            nat_m = nat_data[nat_data["model_name"] == model]
            if en_m.empty or nat_m.empty:
                continue
            d_en = euclidean(en_m["PC1"].mean(), en_m["PC2"].mean(), ivs_c["PC1"], ivs_c["PC2"])
            d_nat = euclidean(nat_m["PC1"].mean(), nat_m["PC2"].mean(), ivs_c["PC1"], ivs_c["PC2"])
            d_en_list.append(d_en)
            d_nat_list.append(d_nat)

        if not d_en_list:
            continue

        region = "Middle East" if country in middle_east else "Confucian"
        mean_d_en = np.mean(d_en_list)
        mean_d_nat = np.mean(d_nat_list)
        advantage = (mean_d_nat - mean_d_en) / mean_d_nat * 100 if mean_d_nat > 0 else 0

        rows.append({
            "country": country,
            "cultural_region": region,
            "native_language": native_lang,
            "native_distance_mean": round(mean_d_nat, 4),
            "en_distance_mean": round(mean_d_en, 4),
            "advantage_mean": round(advantage, 4),
            "n_models": len(d_en_list),
        })

    df = pd.DataFrame(rows)
    out = PAPER_DATA_DIR / "figure3_digital_orientalism.csv"
    df.to_csv(out, index=False)
    print(f"  Countries: {len(df)}")
    print(f"    Middle East: {len(df[df['cultural_region'] == 'Middle East'])}")
    print(f"    Confucian: {len(df[df['cultural_region'] == 'Confucian'])}")
    print(f"  Saved: {out}")
    return df


# =========================================================================
# Figure 4: Colonial legacies — Sub-Saharan Africa + Latin America
# =========================================================================

def generate_figure4():
    print("\n" + "=" * 60)
    print("Figure 4: Colonial Legacies — Sub-Saharan Africa + Latin America")
    print("=" * 60)

    ivs = load_ivs_coordinates()
    roleplay = pd.read_csv(
        PROJECT_ROOT / "SI" / "pca" / "Table_S7_LLM_roleplay_PCA_coordinates.csv"
    )
    roleplay["model_name"] = roleplay["model_name"].map(lambda x: normalize_model_name(x))
    roleplay = roleplay[~roleplay["model_name"].apply(is_excluded)]
    roleplay = roleplay[roleplay["data_source"] == "LLM"]

    # Sub-Saharan Africa: 6 British colonies + 2 French colonies
    africa_british = ["Kenya", "Nigeria", "Ghana", "South Africa", "Zimbabwe", "Zambia"]
    africa_french = ["Mali", "Burkina Faso"]

    # Latin America
    latam_spanish = [
        "Argentina", "Bolivia", "Chile", "Colombia", "Ecuador",
        "Guatemala", "Mexico", "Nicaragua", "Peru", "Uruguay", "Venezuela",
    ]
    latam_portuguese = ["Brazil"]
    latam_french = ["Haiti"]

    # Confucian
    confucian = [
        "China", "Japan", "Korea, Republic of",
        "Taiwan, Province of China", "Hong Kong", "Macao",
    ]

    native_lang_map = {
        "Kenya": "en", "Nigeria": "en", "Ghana": "en",
        "South Africa": "en", "Zimbabwe": "en", "Zambia": "en",
        "Mali": "fr", "Burkina Faso": "fr",
        "Argentina": "es", "Bolivia": "es", "Chile": "es",
        "Colombia": "es", "Ecuador": "es", "Guatemala": "es",
        "Mexico": "es", "Nicaragua": "es", "Peru": "es",
        "Uruguay": "es", "Venezuela": "es",
        "Brazil": "pt", "Haiti": "fr",
        "China": "zh-cn", "Japan": "ja", "Korea, Republic of": "ko",
        "Taiwan, Province of China": "zh-tw", "Hong Kong": "zh-hk",
        "Macao": "pt",
    }

    colonial_power_map = {
        "Kenya": "UK", "Nigeria": "UK", "Ghana": "UK",
        "South Africa": "UK", "Zimbabwe": "UK", "Zambia": "UK",
        "Mali": "FR", "Burkina Faso": "FR",
        "Argentina": "ES", "Bolivia": "ES", "Chile": "ES",
        "Colombia": "ES", "Ecuador": "ES", "Guatemala": "ES",
        "Mexico": "ES", "Nicaragua": "ES", "Peru": "ES",
        "Uruguay": "ES", "Venezuela": "ES",
        "Brazil": "PT", "Haiti": "FR",
        "China": "JP", "Japan": "-", "Korea, Republic of": "JP",
        "Taiwan, Province of China": "JP", "Hong Kong": "UK",
        "Macao": "PT",
    }

    all_countries = (
        africa_british + africa_french +
        latam_spanish + latam_portuguese + latam_french +
        confucian
    )

    rows = []
    for country in all_countries:
        if country not in ivs:
            print(f"  WARNING: {country} not in IVS, skipping")
            continue
        ivs_c = ivs[country]
        native_lang = native_lang_map.get(country)

        c_data = roleplay[roleplay["country"] == country]

        # English data
        en_data = c_data[c_data["language"].isin(["en", "en-native"])]
        countries_with_en = set(
            c_data[c_data["language"] == "en"]["country"].unique()
        )
        en_data = en_data[
            ~((en_data["language"] == "en-native") & en_data["country"].isin(countries_with_en))
        ]

        # For English-native countries (British Africa), native IS English
        is_en_native = country in EN_NATIVE_COUNTRIES

        if is_en_native:
            # For English-native countries, we compute d_english only
            # (there's no separate "native" language to compare)
            d_en_list = []
            for model in en_data["model_name"].unique():
                en_m = en_data[en_data["model_name"] == model]
                if en_m.empty:
                    continue
                d_en = euclidean(
                    en_m["PC1"].mean(), en_m["PC2"].mean(),
                    ivs_c["PC1"], ivs_c["PC2"]
                )
                d_en_list.append(d_en)

            if not d_en_list:
                continue

            rows.append({
                "country": country,
                "cultural_region": _get_region(country, africa_british, africa_french,
                                               latam_spanish, latam_portuguese, latam_french, confucian),
                "native_language": native_lang,
                "colonial_power": colonial_power_map.get(country, ""),
                "native_distance_mean": round(np.mean(d_en_list), 4),
                "en_distance_mean": round(np.mean(d_en_list), 4),
                "advantage_mean": 0.0,
                "n_models": len(d_en_list),
                "is_en_native": True,
            })
        else:
            # Non-English-native: compute both native and English distances
            nat_data = c_data[c_data["language"] == native_lang]
            if en_data.empty or nat_data.empty:
                print(f"  WARNING: {country} missing en or {native_lang} data")
                continue

            d_en_list, d_nat_list = [], []
            for model in nat_data["model_name"].unique():
                en_m = en_data[en_data["model_name"] == model]
                nat_m = nat_data[nat_data["model_name"] == model]
                if en_m.empty or nat_m.empty:
                    continue
                d_en = euclidean(en_m["PC1"].mean(), en_m["PC2"].mean(), ivs_c["PC1"], ivs_c["PC2"])
                d_nat = euclidean(nat_m["PC1"].mean(), nat_m["PC2"].mean(), ivs_c["PC1"], ivs_c["PC2"])
                d_en_list.append(d_en)
                d_nat_list.append(d_nat)

            if not d_en_list:
                continue

            mean_d_en = np.mean(d_en_list)
            mean_d_nat = np.mean(d_nat_list)
            advantage = (mean_d_nat - mean_d_en) / mean_d_nat * 100 if mean_d_nat > 0 else 0

            rows.append({
                "country": country,
                "cultural_region": _get_region(country, africa_british, africa_french,
                                               latam_spanish, latam_portuguese, latam_french, confucian),
                "native_language": native_lang,
                "colonial_power": colonial_power_map.get(country, ""),
                "native_distance_mean": round(mean_d_nat, 4),
                "en_distance_mean": round(mean_d_en, 4),
                "advantage_mean": round(advantage, 4),
                "n_models": len(d_en_list),
                "is_en_native": False,
            })

    df = pd.DataFrame(rows)

    out = PAPER_DATA_DIR / "figure4_colonial_history.csv"
    df.to_csv(out, index=False)

    print(f"  Total countries: {len(df)}")
    for region in df["cultural_region"].unique():
        n = len(df[df["cultural_region"] == region])
        print(f"    {region}: {n}")
    print(f"  Saved: {out}")

    return df


def _get_region(country, africa_british, africa_french,
                latam_spanish, latam_portuguese, latam_french, confucian):
    if country in africa_british:
        return "Sub-Saharan Africa (British)"
    if country in africa_french:
        return "Sub-Saharan Africa (French)"
    if country in latam_spanish:
        return "Latin America (Spanish)"
    if country in latam_portuguese:
        return "Latin America (Portuguese)"
    if country in latam_french:
        return "Latin America (French)"
    if country in confucian:
        return "Confucian"
    return "Other"


# =========================================================================
# Main
# =========================================================================

def main():
    print("=" * 70)
    print("REGENERATE ALL PAPER DATA FILES")
    print("=" * 70)

    fig1 = generate_figure1()
    fig2 = generate_figure2()
    fig3 = generate_figure3()
    fig4 = generate_figure4()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Figure 1: {len(fig1)} countries (LLM EN PC1/PC2 + WVS PC1/PC2)")
    print(f"  Figure 2: {len(fig2)} records ({fig2['model_name'].nunique()} models × {fig2['language'].nunique()} languages)")
    print(f"  Figure 3: {len(fig3)} countries (Middle East + East Asia distance)")
    print(f"  Figure 4: {len(fig4)} countries (Sub-Saharan Africa + Latin America + Confucian)")
    print(f"\n  All files saved to: {PAPER_DATA_DIR}")


if __name__ == "__main__":
    main()
