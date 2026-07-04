#!/usr/bin/env python3
"""
法语分析补充：模型异质性、稳健性、Wilcoxon 检验
1. 按厂商分组比较 French/English adv
2. 排除极端模型后重算
3. Wilcoxon 符号秩检验（非参数）
"""

import sys
import json
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from scipy import stats

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

DATA_DIR = project_root / "data" / "roleplay_multilingual"
RESULTS_DIR = project_root / "results" / "roleplay_multilingual"
PREFIX = "roleplay_ml_ar_fr_en"


def load_ivs_coords():
    paths = [
        project_root / "SI" / "pca" / "Table_S5_IVS_PCA_coordinates.csv",
        project_root / "data" / "country_values" / "country_scores_pca.pkl",
    ]
    for p in paths:
        if not p.exists():
            continue
        if p.suffix == ".csv":
            csv_df = pd.read_csv(p)
            if "country" in csv_df.columns and "PC1" in csv_df.columns:
                return {str(row["country"]).strip(): (float(row["PC1"]), float(row["PC2"]))
                        for _, row in csv_df.iterrows()}
    raise FileNotFoundError("未找到 IVS 坐标")


def main():
    print("\n" + "=" * 70)
    print("法语分析补充：模型异质性、稳健性、Wilcoxon")
    print("=" * 70)

    # 加载数据
    df_scores = pickle.load(open(DATA_DIR / "roleplay_ml_pca_entity_scores_latest.pkl", "rb"))
    ivs_coords = load_ivs_coords()
    with open(project_root / "config" / "models" / "llm_models.json") as f:
        model_cfg = json.load(f)["models"]

    pc1_col = "PC1_rescaled" if "PC1_rescaled" in df_scores.columns else "PC1"
    pc2_col = "PC2_rescaled" if "PC2_rescaled" in df_scores.columns else "PC2"
    country_col = "Country" if "Country" in df_scores.columns else "country_code"
    countries = ["Algeria", "Egypt", "Iraq", "Jordan", "Kuwait", "Lebanon", "Libya", "Morocco", "Palestine", "Qatar", "Tunisia", "Yemen"]

    def dist(xy, r):
        return np.sqrt((xy[0] - r[0]) ** 2 + (xy[1] - r[1]) ** 2)

    # 构建 model -> provider 映射（支持 openai/gpt-5.1 和 gpt-4o 两种格式）
    model_to_provider = {}
    for key, val in model_cfg.items():
        model_to_provider[key] = val.get("provider", "Unknown")
        short = key.split("/")[-1]
        if short not in model_to_provider:
            model_to_provider[short] = val.get("provider", "Unknown")

    # 收集配对数据 (delta_fr, delta_en) 及 model
    df_detail = pd.read_csv(DATA_DIR / f"{PREFIX}_distances_latest.csv")
    df_by_model = pd.read_csv(DATA_DIR / f"{PREFIX}_by_model_latest.csv")

    models_full = df_by_model["model_name"].tolist()

    rows = []
    for c in countries:
        real = ivs_coords.get(c)
        if not real:
            continue
        for m in models_full:
            ar = df_detail[(df_detail["country"] == c) & (df_detail["language"] == "ar") & (df_detail["model_name"] == m)]
            fr = df_detail[(df_detail["country"] == c) & (df_detail["language"] == "fr") & (df_detail["model_name"] == m)]
            en = df_detail[(df_detail["country"] == c) & (df_detail["language"] == "en") & (df_detail["model_name"] == m)]
            if len(ar) and len(fr) and len(en):
                d_ar = ar["cultural_distance"].values[0]
                d_fr = fr["cultural_distance"].values[0]
                d_en = en["cultural_distance"].values[0]
                delta_fr = d_ar - d_fr
                delta_en = d_ar - d_en
                adv_fr = (delta_fr / d_ar) * 100
                adv_en = (delta_en / d_ar) * 100
                rows.append({
                    "country": c, "model_name": m,
                    "d_ar": d_ar, "d_fr": d_fr, "d_en": d_en,
                    "delta_fr": delta_fr, "delta_en": delta_en,
                    "french_adv": adv_fr, "english_adv": adv_en,
                    "provider": model_to_provider.get(m, model_to_provider.get(m.split("/")[-1], "Unknown")),
                })
    df_pair = pd.DataFrame(rows)

    all_delta_fr = df_pair["delta_fr"].values
    all_delta_en = df_pair["delta_en"].values
    d_ar_all = df_pair["d_ar"].values

    # ========== 1. 模型异质性：按厂商分组 ==========
    print("\n" + "=" * 50)
    print("1. 模型异质性：按厂商分组")
    print("=" * 50)

    provider_stats = []
    for prov in df_pair["provider"].unique():
        sub = df_pair[df_pair["provider"] == prov]
        models = sub["model_name"].unique()
        provider_stats.append({
            "provider": prov,
            "n_models": len(models),
            "n_obs": len(sub),
            "french_adv_mean": sub["french_adv"].mean(),
            "french_adv_std": sub["french_adv"].std(),
            "english_adv_mean": sub["english_adv"].mean(),
            "english_adv_std": sub["english_adv"].std(),
            "french_n_positive": (sub["delta_fr"] > 0).sum(),
            "english_n_positive": (sub["delta_en"] > 0).sum(),
        })
    df_provider = pd.DataFrame(provider_stats).sort_values("french_adv_mean", ascending=False)
    print(df_provider.to_string(index=False))

    # ========== 2. 稳健性：排除极端模型 ==========
    print("\n" + "=" * 50)
    print("2. 稳健性：排除极端模型 (|french_adv| > 50%)")
    print("=" * 50)

    extreme = df_by_model[df_by_model["french_adv_mean_pct"].abs() > 50]["model_name"].tolist()
    print(f"排除的极端模型: {[m.split('/')[-1] for m in extreme]}")

    df_pair_robust = df_pair[~df_pair["model_name"].isin(extreme)]
    n_robust = len(df_pair_robust["model_name"].unique())
    delta_fr_r = df_pair_robust["delta_fr"].values
    delta_en_r = df_pair_robust["delta_en"].values
    d_ar_r = df_pair_robust["d_ar"].values

    fr_adv_robust = np.mean((delta_fr_r / d_ar_r) * 100)
    en_adv_robust = np.mean((delta_en_r / d_ar_r) * 100)
    t_fr_r, p_fr_r = stats.ttest_1samp(delta_fr_r, 0)
    t_en_r, p_en_r = stats.ttest_1samp(delta_en_r, 0)

    print(f"  保留模型数: {n_robust}, 观测数: {len(df_pair_robust)}")
    print(f"  French adv:  {fr_adv_robust:.1f}%  t={t_fr_r:.2f} p={p_fr_r:.4f}")
    print(f"  English adv: {en_adv_robust:.1f}%  t={t_en_r:.2f} p={p_en_r:.4f}")

    # ========== 3. Wilcoxon 符号秩检验 ==========
    print("\n" + "=" * 50)
    print("3. Wilcoxon 符号秩检验（非参数）")
    print("=" * 50)

    w_fr, p_w_fr = stats.wilcoxon(all_delta_fr, alternative="two-sided")
    w_en, p_w_en = stats.wilcoxon(all_delta_en, alternative="two-sided")
    print(f"  全样本 (n={len(all_delta_fr)}):")
    print(f"    French:  Wilcoxon stat={w_fr:.0f}, p={p_w_fr:.4f}")
    print(f"    English: Wilcoxon stat={w_en:.0f}, p={p_w_en:.4f}")

    w_fr_r, p_w_fr_r = stats.wilcoxon(delta_fr_r, alternative="two-sided")
    w_en_r, p_w_en_r = stats.wilcoxon(delta_en_r, alternative="two-sided")
    print(f"  排除极端后 (n={len(delta_fr_r)}):")
    print(f"    French:  Wilcoxon stat={w_fr_r:.0f}, p={p_w_fr_r:.4f}")
    print(f"    English: Wilcoxon stat={w_en_r:.0f}, p={p_w_en_r:.4f}")

    # ========== 4. 保存结果 ==========
    ts = datetime.now().strftime("%Y%m%d")
    df_provider.to_csv(DATA_DIR / f"{PREFIX}_by_provider_{ts}.csv", index=False)
    df_provider.to_csv(RESULTS_DIR / f"{PREFIX}_by_provider_{ts}.csv", index=False)
    df_provider.to_csv(DATA_DIR / f"{PREFIX}_by_provider_latest.csv", index=False)
    df_provider.to_csv(RESULTS_DIR / f"{PREFIX}_by_provider_latest.csv", index=False)

    robustness = pd.DataFrame([{
        "analysis": "exclude_extreme",
        "n_models_excluded": len(extreme),
        "models_excluded": ";".join(extreme),
        "n_models_kept": n_robust,
        "n_obs": len(df_pair_robust),
        "french_adv_mean_pct": fr_adv_robust,
        "english_adv_mean_pct": en_adv_robust,
        "french_t": t_fr_r,
        "french_p": p_fr_r,
        "english_t": t_en_r,
        "english_p": p_en_r,
    }])
    robustness.to_csv(DATA_DIR / f"{PREFIX}_robustness_{ts}.csv", index=False)
    robustness.to_csv(RESULTS_DIR / f"{PREFIX}_robustness_{ts}.csv", index=False)

    wilcoxon_res = pd.DataFrame([
        {"test": "French_full", "n": len(all_delta_fr), "statistic": w_fr, "p_value": p_w_fr},
        {"test": "English_full", "n": len(all_delta_en), "statistic": w_en, "p_value": p_w_en},
        {"test": "French_robust", "n": len(delta_fr_r), "statistic": w_fr_r, "p_value": p_w_fr_r},
        {"test": "English_robust", "n": len(delta_en_r), "statistic": w_en_r, "p_value": p_w_en_r},
    ])
    wilcoxon_res.to_csv(DATA_DIR / f"{PREFIX}_wilcoxon_{ts}.csv", index=False)
    wilcoxon_res.to_csv(RESULTS_DIR / f"{PREFIX}_wilcoxon_{ts}.csv", index=False)

    print(f"\n💾 已保存: by_provider, robustness, wilcoxon -> data/ + results/")
    print("=" * 70)


if __name__ == "__main__":
    main()
