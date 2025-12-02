#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Compute failure breakdown (api_failure / refusal / format_error) for Stage1/2/3.

This script is read-only: it loads existing result files and produces a summary CSV.
"""

import os
import re
import json
import pickle
from pathlib import Path
from typing import Dict, Any, List, Tuple
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))
DATA_DIR = PROJECT_ROOT / "data"


REFUSAL_KEYWORDS = [
    # English
    "as an ai", "as a language model", "i am an ai", "i\u2019m an ai", "cannot answer", "can't answer",
    "unable to", "refuse", "refusal",
    # Chinese
    "作为一个ai", "作為一個ai", "作为一个人工智能", "作為一個人工智能",
    "不能回答", "無法回答", "无法回答", "不方便回答", "拒绝回答", "拒絕回答",
]


def load_latest_file(directory: Path, pattern: str) -> Path | None:
    """Return the latest file in *directory* matching *pattern* (glob), or None."""
    if not directory.exists():
        return None
    files = list(directory.glob(pattern))
    if not files:
        return None
    return max(files, key=lambda p: p.stat().st_mtime)


def classify_failure_llmresponse(raw_response: Any, is_valid: bool, error_message: str | None) -> str:
    """Classify a single LLMResponse-style record into failure_type.

    Returns one of: "none", "api_failure", "refusal", "format_error".
    """
    # API failure: no raw_response and retry exhausted
    if raw_response is None:
        if error_message and "所有尝试都失败" in error_message:
            return "api_failure"
        # Fallback: treat None + invalid as API failure
        if not is_valid:
            return "api_failure"

    # Valid answer
    if is_valid:
        return "none"

    # Invalid but has text: distinguish refusal vs pure format error
    text = str(raw_response).lower() if raw_response is not None else ""
    if text:
        for kw in REFUSAL_KEYWORDS:
            if kw.lower() in text:
                return "refusal"

    return "format_error"


def classify_failure_multilingual(raw_response: Any, processed_response: Any) -> str:
    """Classify multilingual roleplay responses where we only have raw/processed_response."""
    if raw_response is None and processed_response is None:
        return "api_failure"
    if processed_response not in (None, "", []):
        return "none"

    text = str(raw_response).lower() if raw_response is not None else ""
    if text:
        for kw in REFUSAL_KEYWORDS:
            if kw.lower() in text:
                return "refusal"
    return "format_error"


def analyze_stage1_llm_values() -> pd.DataFrame:
    """Analyze Stage1 (LLM values) failure breakdown from unified interview_raw files."""
    src_dir = DATA_DIR / "llm_values" / "interview_raw"
    latest = load_latest_file(src_dir, "llm_interview_raw_*.pkl") or load_latest_file(src_dir, "llm_interview_raw_*.json")
    if not latest:
        print("⚠️  Stage1: No result files found, skipping.")
        return pd.DataFrame()

    data = None
    if latest.suffix == ".pkl":
        try:
            with latest.open("rb") as f:
                data = pickle.load(f)
        except (ModuleNotFoundError, AttributeError) as e:
            print(f"⚠️  Stage1: Failed to load PKL ({e}), trying JSON fallback...")
            # Try corresponding JSON file
            json_file = latest.with_suffix(".json")
            if json_file.exists():
                with json_file.open("r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                print(f"⚠️  Stage1: No JSON fallback found, skipping Stage1.")
                return pd.DataFrame()
    else:
        with latest.open("r", encoding="utf-8") as f:
            data = json.load(f)
    
    if not data:
        return pd.DataFrame()

    results = data.get("results", [])
    records: List[Dict[str, Any]] = []

    for entity in results:
        model_name = entity.get("model_name", "")
        entity_id = entity.get("entity_id", "")
        responses = entity.get("responses", [])

        for r in responses:
            # JSON 里是 dict；PKL 里可能是 LLMResponse 对象或已转成 dict
            if hasattr(r, "__dict__"):
                rd = r.__dict__
            else:
                rd = r
            raw_response = rd.get("raw_response")
            is_valid = bool(rd.get("is_valid", False))
            error_message = rd.get("error_message")
            failure_type = classify_failure_llmresponse(raw_response, is_valid, error_message)

            records.append({
                "stage": "stage1",
                "model_name": model_name,
                "entity_id": entity_id,
                "failure_type": failure_type,
            })

    return pd.DataFrame.from_records(records)


def analyze_stage2_roleplay_english() -> pd.DataFrame:
    """Analyze Stage2 (English roleplay) failure breakdown from roleplay_results files."""
    src_dir = DATA_DIR / "roleplay_English" / "llm_responses_roleplay"
    latest = load_latest_file(src_dir, "roleplay_results_*.pkl") or load_latest_file(src_dir, "roleplay_results_*.json")
    if not latest:
        print("⚠️  Stage2: No result files found, skipping.")
        return pd.DataFrame()

    data = None
    if latest.suffix == ".pkl":
        try:
            with latest.open("rb") as f:
                data = pickle.load(f)
        except (ModuleNotFoundError, AttributeError) as e:
            print(f"⚠️  Stage2: Failed to load PKL ({e}), trying JSON fallback...")
            json_file = latest.with_suffix(".json")
            if json_file.exists():
                with json_file.open("r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                print(f"⚠️  Stage2: No JSON fallback found, skipping Stage2.")
                return pd.DataFrame()
    else:
        with latest.open("r", encoding="utf-8") as f:
            data = json.load(f)
    
    if not data:
        return pd.DataFrame()

    results = data.get("results", []) if isinstance(data, dict) else data
    records: List[Dict[str, Any]] = []

    for entry in results:
        model_name = entry.get("model") or entry.get("model_name", "")
        country_raw = entry.get("country") or entry.get("country_name", "")
        # Extract country name if it's a dict
        if isinstance(country_raw, dict):
            country = country_raw.get("name", str(country_raw))
        else:
            country = str(country_raw) if country_raw else ""
        responses = entry.get("responses", [])

        for r in responses:
            # 可能是 LLMResponse 或 dict
            if hasattr(r, "__dict__"):
                rd = r.__dict__
            else:
                rd = r
            raw_response = rd.get("raw_response")
            is_valid = bool(rd.get("is_valid", False))
            error_message = rd.get("error_message")
            failure_type = classify_failure_llmresponse(raw_response, is_valid, error_message)

            records.append({
                "stage": "stage2",
                "model_name": model_name,
                "country": country,
                "failure_type": failure_type,
            })

    return pd.DataFrame.from_records(records)


def analyze_stage3_roleplay_multilingual() -> pd.DataFrame:
    """Analyze Stage3 (multilingual roleplay) failure breakdown from roleplay_results_ml files."""
    src_dir = DATA_DIR / "roleplay_multilingual" / "llm_responses_roleplay_ml"
    latest = load_latest_file(src_dir, "roleplay_results_ml_*.pkl") or load_latest_file(src_dir, "roleplay_results_ml_*.json")
    if not latest:
        print("⚠️  Stage3: No result files found, skipping.")
        return pd.DataFrame()

    data = None
    if latest.suffix == ".pkl":
        try:
            with latest.open("rb") as f:
                data = pickle.load(f)
        except (ModuleNotFoundError, AttributeError) as e:
            print(f"⚠️  Stage3: Failed to load PKL ({e}), trying JSON fallback...")
            json_file = latest.with_suffix(".json")
            if json_file.exists():
                with json_file.open("r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                print(f"⚠️  Stage3: No JSON fallback found, skipping Stage3.")
                return pd.DataFrame()
    else:
        with latest.open("r", encoding="utf-8") as f:
            data = json.load(f)
    
    if not data:
        return pd.DataFrame()

    results = data.get("results", []) if isinstance(data, dict) else data
    records: List[Dict[str, Any]] = []

    for entry in results:
        model_name = entry.get("model") or entry.get("model_name", "")
        country_raw = entry.get("country") or entry.get("country_name", "")
        # Extract country name if it's a dict
        if isinstance(country_raw, dict):
            country = country_raw.get("name", str(country_raw))
        else:
            country = str(country_raw) if country_raw else ""
        language = entry.get("language", "")
        responses = entry.get("responses", [])

        for r in responses:
            # multilingual responses are dicts
            raw_response = r.get("raw_response")
            processed_response = r.get("processed_response")
            failure_type = classify_failure_multilingual(raw_response, processed_response)

            records.append({
                "stage": "stage3",
                "model_name": model_name,
                "country": country,
                "language": language,
                "failure_type": failure_type,
            })

    return pd.DataFrame.from_records(records)


def main(output_csv: str | None = None):
    """Run all stage analyses and save a summarized CSV.

    The output CSV will have columns:
        stage, model_name, [entity/country/language], failure_type, count, rate
    """
    df_list = [
        analyze_stage1_llm_values(),
        analyze_stage2_roleplay_english(),
        analyze_stage3_roleplay_multilingual(),
    ]
    df = pd.concat([d for d in df_list if not d.empty], ignore_index=True) if any(not d.empty for d in df_list) else pd.DataFrame()

    if df.empty:
        print("No data found for any stage.")
        return

    # Compute counts per (stage, model, country/language, failure_type)
    group_cols = [c for c in ["stage", "model_name", "entity_id", "country", "language"] if c in df.columns]
    # entity_id may be NaN for some rows, we still include it in groupby
    summary = (
        df
        .groupby(group_cols + ["failure_type"], dropna=False)
        .size()
        .reset_index(name="count")
    )

    # Also compute total per group to get rates
    total = (
        summary
        .groupby(group_cols, dropna=False)["count"]
        .sum()
        .reset_index(name="total")
    )
    summary = summary.merge(total, on=group_cols, how="left")
    summary["rate"] = summary["count"] / summary["total"]

    if output_csv is None:
        output_csv = PROJECT_ROOT / "results" / "analysis" / "failure_breakdown_summary.csv"
    else:
        output_csv = Path(output_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(output_csv, index=False, encoding="utf-8-sig")

    print(f"Saved failure breakdown summary to: {output_csv}")


if __name__ == "__main__":
    main()
