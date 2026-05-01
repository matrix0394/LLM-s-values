#!/usr/bin/env python3
"""
Arabic vs French vs English 三语对比分析
对 Algeria, Lebanon, Morocco, Tunisia 计算：
- D_ar, D_fr, D_en：各语言与 IVS 真实国家坐标的欧氏距离
- French adv = (D_ar - D_fr) / D_ar × 100%
- English adv = (D_ar - D_en) / D_ar × 100%
正值表示该二语更接近 IVS

数据来源：cultural_distance_analysis.csv（与论文图表方法完全一致）
- LLM坐标：roleplay_ml_pca_results_latest.pkl（固定PCA模型空间）
- IVS坐标：country_scores_pca.json（Stage0 PCA，同一坐标系）
- 模型池：各语言独立（非配对），与论文 stage0_vs_stage3 方法一致

输出保存至 data/roleplay_multilingual/ 和 results/roleplay_multilingual/
"""

import sys
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

COUNTRIES = ["Algeria", "Egypt", "Iraq", "Jordan", "Kuwait", "Lebanon", "Libya", "Morocco", "Palestine", "Qatar", "Tunisia", "Yemen"]
LANGUAGES = ["ar", "fr", "en"]


def main():
    print("\n" + "=" * 70)
    print("Arabic vs French vs English 三语对比分析")
    print("方法：与论文 cultural_distance_analysis.csv 完全一致（非配对）")
    print("=" * 70)

    # 读取论文标准数据源
    ca_path = RESULTS_DIR / "cultural_distance_analysis.csv"
    if not ca_path.exists():
        print(f"\n❌ 未找到: {ca_path}")
        print("请先运行主分析流程生成 cultural_distance_analysis.csv")
        sys.exit(1)

    df = pd.read_csv(ca_path)
    rename_map = {}
    if "Country" in df.columns:
        rename_map["Country"] = "country"
    if "model_name" in df.columns:
        rename_map["model_name"] = "model"
    if "distance" in df.columns:
        rename_map["distance"] = "cultural_distance"
    if rename_map:
        df = df.rename(columns=rename_map)
    df = df[df["country"].isin(COUNTRIES)]
    print(f"\n📊 加载数据: {len(df)} 条记录，国家={sorted(df['country'].unique())}")
    print(f"📊 IVS坐标来源: country_scores_pca.json (stage0 PCA)  [列: stage0_pc1/pc2]")
    print(f"📊 LLM坐标来源: roleplay_ml_pca_results_latest.pkl      [列: stage3_pc1/pc2]")

    # === 1. 各语言模型数量统计 ===
    print("\n--- 各国各语言模型数量 ---")
    for country in COUNTRIES:
        sub = df[df["country"] == country]
        for lang in LANGUAGES:
            n = len(sub[sub["language"] == lang])
            models = set(sub[sub["language"] == lang]["model"])
            print(f"  {country} {lang}: {n} 个模型")

    # === 2. 按国家汇总（非配对，与论文一致）===
    print("\n--- 按国家汇总（非配对平均） ---")
    summary_country = []
    all_country_stats = {}

    for country in COUNTRIES:
        sub = df[df["country"] == country]

        ar_dists = sub[sub["language"] == "ar"]["cultural_distance"].values
        fr_dists = sub[sub["language"] == "fr"]["cultural_distance"].values
        en_dists = sub[sub["language"] == "en"]["cultural_distance"].values

        d_ar = np.mean(ar_dists)
        d_fr = np.mean(fr_dists)
        d_en = np.mean(en_dists)

        fr_adv = (d_ar - d_fr) / d_ar * 100
        en_adv = (d_ar - d_en) / d_ar * 100

        # 配对（仅 ar∩fr）子集的统计检验
        ar_models = set(sub[sub["language"] == "ar"]["model"])
        fr_models = set(sub[sub["language"] == "fr"]["model"])
        en_models = set(sub[sub["language"] == "en"]["model"])
        paired_ar_fr = ar_models & fr_models
        paired_all = ar_models & fr_models & en_models

        # 配对 delta 用于 t-test
        ar_by_m = sub[sub["language"] == "ar"].set_index("model")["cultural_distance"]
        fr_by_m = sub[sub["language"] == "fr"].set_index("model")["cultural_distance"]
        en_by_m = sub[sub["language"] == "en"].set_index("model")["cultural_distance"]

        delta_fr = (ar_by_m.reindex(paired_ar_fr) - fr_by_m.reindex(paired_ar_fr)).dropna()
        delta_en_full = (ar_by_m.reindex(ar_models & en_models) - en_by_m.reindex(ar_models & en_models)).dropna()

        t_fr, p_fr = stats.ttest_1samp(delta_fr, 0) if len(delta_fr) > 1 else (np.nan, np.nan)
        t_en, p_en = stats.ttest_1samp(delta_en_full, 0) if len(delta_en_full) > 1 else (np.nan, np.nan)
        cd_fr = np.mean(delta_fr) / np.std(delta_fr) if np.std(delta_fr) > 0 else 0
        cd_en = np.mean(delta_en_full) / np.std(delta_en_full) if np.std(delta_en_full) > 0 else 0

        print(f"\n{country}:")
        print(f"  ar={len(ar_dists)}模型  fr={len(fr_dists)}模型  en={len(en_dists)}模型")
        print(f"  D_ar={d_ar:.3f} ± {np.std(ar_dists):.3f}")
        print(f"  D_fr={d_fr:.3f} ± {np.std(fr_dists):.3f}")
        print(f"  D_en={d_en:.3f} ± {np.std(en_dists):.3f}")
        print(f"  French优势: {fr_adv:+.1f}%  (配对t检验: t={t_fr:.2f} p={p_fr:.4f} d={cd_fr:.2f}  正值={np.sum(delta_fr>0)}/{len(delta_fr)})")
        print(f"  English优势: {en_adv:+.1f}%  (配对t检验: t={t_en:.2f} p={p_en:.4f} d={cd_en:.2f}  正值={np.sum(delta_en_full>0)}/{len(delta_en_full)})")

        all_country_stats[country] = {
            "ar_dists": ar_dists, "fr_dists": fr_dists, "en_dists": en_dists,
            "delta_fr": delta_fr.values, "delta_en": delta_en_full.values,
        }

        summary_country.append({
            "country": country,
            "n_ar": len(ar_dists),
            "n_fr": len(fr_dists),
            "n_en": len(en_dists),
            "n_paired_ar_fr": len(paired_ar_fr),
            "D_ar_mean": d_ar,
            "D_ar_std": np.std(ar_dists),
            "D_fr_mean": d_fr,
            "D_fr_std": np.std(fr_dists),
            "D_en_mean": d_en,
            "D_en_std": np.std(en_dists),
            "french_adv_pct": fr_adv,
            "english_adv_pct": en_adv,
            "french_t": t_fr,
            "french_p": p_fr,
            "french_cohens_d": cd_fr,
            "french_n_positive": int(np.sum(delta_fr > 0)),
            "english_t": t_en,
            "english_p": p_en,
            "english_cohens_d": cd_en,
            "english_n_positive": int(np.sum(delta_en_full > 0)),
        })

    # === 3. 四国合并总体汇总 ===
    all_ar = np.concatenate([s["ar_dists"] for s in all_country_stats.values()])
    all_fr = np.concatenate([s["fr_dists"] for s in all_country_stats.values()])
    all_en = np.concatenate([s["en_dists"] for s in all_country_stats.values()])
    all_delta_fr = np.concatenate([s["delta_fr"] for s in all_country_stats.values()])
    all_delta_en = np.concatenate([s["delta_en"] for s in all_country_stats.values()])

    d_ar_all = np.mean(all_ar)
    d_fr_all = np.mean(all_fr)
    d_en_all = np.mean(all_en)
    fr_adv_all = (d_ar_all - d_fr_all) / d_ar_all * 100
    en_adv_all = (d_ar_all - d_en_all) / d_ar_all * 100

    t_fr_all, p_fr_all = stats.ttest_1samp(all_delta_fr, 0)
    t_en_all, p_en_all = stats.ttest_1samp(all_delta_en, 0)

    print("\n" + "=" * 50)
    print("【总体】四国合并")
    print(f"  D_ar={d_ar_all:.3f}  D_fr={d_fr_all:.3f}  D_en={d_en_all:.3f}")
    print(f"  French优势: {fr_adv_all:+.1f}%  t={t_fr_all:.2f} p={p_fr_all:.4f}  正值={np.sum(all_delta_fr>0)}/{len(all_delta_fr)}")
    print(f"  English优势: {en_adv_all:+.1f}%  t={t_en_all:.2f} p={p_en_all:.4f}  正值={np.sum(all_delta_en>0)}/{len(all_delta_en)}")

    summary_overall = {
        "scope": "4countries_combined",
        "n_ar_observations": len(all_ar),
        "n_fr_observations": len(all_fr),
        "n_en_observations": len(all_en),
        "D_ar_mean": d_ar_all,
        "D_fr_mean": d_fr_all,
        "D_en_mean": d_en_all,
        "french_adv_pct": fr_adv_all,
        "english_adv_pct": en_adv_all,
        "french_t": t_fr_all,
        "french_p": p_fr_all,
        "french_n_positive": int(np.sum(all_delta_fr > 0)),
        "english_t": t_en_all,
        "english_p": p_en_all,
        "english_n_positive": int(np.sum(all_delta_en > 0)),
    }

    # === 4. 保存结果 ===
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d")

    def save_both(df_or_dict, fname, desc):
        out = pd.DataFrame([df_or_dict]) if isinstance(df_or_dict, dict) else df_or_dict
        if out.empty:
            return
        latest_name = fname.replace(f"_{ts}.", "_latest.")
        for base_dir in [DATA_DIR, RESULTS_DIR]:
            out.to_csv(base_dir / fname, index=False)
            out.to_csv(base_dir / latest_name, index=False)
        print(f"💾 {desc}: {fname} & {latest_name}")

    df_summary = pd.DataFrame(summary_country)
    save_both(df_summary, f"{PREFIX}_summary_by_country_{ts}.csv", "按国家汇总")
    save_both(summary_overall, f"{PREFIX}_summary_overall_{ts}.csv", "总体汇总")

    # 兼容旧版
    legacy = df_summary[["country", "D_ar_mean", "D_fr_mean", "french_adv_pct", "n_paired_ar_fr",
                          "french_n_positive", "french_p", "french_cohens_d"]].copy()
    legacy.columns = ["country", "D_ar_mean", "D_fr_mean", "french_adv_mean", "n_models",
                      "n_positive", "p_value", "cohens_d"]
    for d in [DATA_DIR, RESULTS_DIR]:
        legacy.to_csv(d / "french_vs_arabic_summary.csv", index=False)
    print(f"💾 兼容旧版: french_vs_arabic_summary.csv")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
