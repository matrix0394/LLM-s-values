#!/usr/bin/env python3
"""
Audit legacy digit-extraction parsing failures for Hong Kong multilingual runs.

Why this exists
---------------
The multilingual interview pipeline historically used a *legacy* parser that
extracts the first digit(s) from a model reply. If a model echoes the full
option list (e.g., "1. ... 2. ... 3. ... 4. ...") or repeats the scale
instructions ("Please use 1 to 10"), the legacy parser may incorrectly accept
"1" as the answer.

This script scans the saved interview JSON files for Hong Kong and reports
how often replies look "option-list-like" or otherwise ambiguous, which
indicates a high risk that the stored `processed_response` is a first-digit
artefact rather than an intended answer.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import pandas as pd


DATA_ROOT = Path("data/llm_interviews/multilingual/interview_raw")

TARGET_COUNTRY = "Hong Kong"
TARGET_LANGUAGES = ("en-native", "zh-hk", "zh-cn")

# The 10 IVS questions used in the HK smoke tests / pilot.
QUESTION_CONFIG: Dict[str, Dict[str, object]] = {
    "A008": {"type": "single", "scale": (1, 4)},
    "A165": {"type": "single", "scale": (1, 2)},
    "E018": {"type": "single", "scale": (1, 3)},
    "E025": {"type": "single", "scale": (1, 3)},
    "F063": {"type": "single", "scale": (1, 10)},
    "F118": {"type": "single", "scale": (1, 10)},
    "F120": {"type": "single", "scale": (1, 10)},
    "G006": {"type": "single", "scale": (1, 4)},
    "Y002": {"type": "multi", "scale": (1, 4), "choices": 2, "exact": True},
    "Y003": {"type": "multi", "scale": (1, 11), "choices": 5, "exact": False},
}


@dataclass(frozen=True)
class ParsedFilename:
    model: str
    country: str
    language: str


def parse_filename(path: Path) -> Optional[ParsedFilename]:
    # Example: gpt-4o_Hong Kong_zh-hk_20251212_200328_791.json
    parts = path.name.split("_")
    if len(parts) < 4:
        return None
    model, country, language = parts[0], parts[1], parts[2]
    return ParsedFilename(model=model, country=country, language=language)


def iter_hk_json_files(data_root: Path) -> Iterable[Path]:
    if not data_root.exists():
        return
    for model_dir in sorted(p for p in data_root.iterdir() if p.is_dir()):
        for path in sorted(model_dir.glob("*.json")):
            meta = parse_filename(path)
            if meta is None:
                continue
            if meta.country != TARGET_COUNTRY:
                continue
            if meta.language not in TARGET_LANGUAGES:
                continue
            yield path


def extract_round_responses(data: Dict[str, object]) -> Iterable[Tuple[int, Dict[str, object]]]:
    # The schema stores per-round raw+processed responses in intermediate_data.all_rounds.
    intermediate = data.get("intermediate_data") or {}
    rounds = intermediate.get("all_rounds") or []
    for round_item in rounds:
        try:
            round_id = int(round_item.get("round_id") or 0)
        except Exception:
            round_id = 0
        responses = round_item.get("responses") or []
        for resp in responses:
            yield round_id, resp


def _numbers_in_range(raw: str, lo: int, hi: int) -> List[int]:
    values: List[int] = []
    for token in re.findall(r"\d+", raw or ""):
        try:
            value = int(token)
        except Exception:
            continue
        if lo <= value <= hi:
            values.append(value)
    return values


def _line_start_options(raw: str, lo: int, hi: int) -> List[int]:
    # Stronger signal for "option list echo": multiple option numbers appear at line starts.
    hits = []
    for opt in range(lo, hi + 1):
        if re.search(rf"(?m)^\s*{opt}\s*(?:[.)]|$)", raw or ""):
            hits.append(opt)
    return hits


def analyze_single(raw: str, processed: Optional[str], lo: int, hi: int) -> Dict[str, object]:
    raw_s = (raw or "").strip()
    processed_s = None if processed is None else str(processed).strip()

    clean_numeric = bool(re.fullmatch(r"\d+", raw_s))
    clean_numeric_punct = bool(re.fullmatch(r"\d+\s*[.。]$", raw_s))
    is_clean = (clean_numeric or clean_numeric_punct)

    in_range_numbers = _numbers_in_range(raw_s, lo, hi)
    unique_in_range = sorted(set(in_range_numbers))
    line_start_opts = _line_start_options(raw_s, lo, hi)

    first_number = None
    all_numbers = re.findall(r"\d+", raw_s)
    if all_numbers:
        try:
            first_number = int(all_numbers[0])
        except Exception:
            first_number = None

    processed_int = None
    try:
        processed_int = int(processed_s) if processed_s is not None else None
    except Exception:
        processed_int = None

    # High-risk: looks like an option list or includes multiple in-range numbers,
    # yet a single processed digit was accepted (legacy behaviour).
    option_list_like = len(set(line_start_opts)) >= 2
    multi_in_range = len(unique_in_range) >= 2
    legacy_like = (processed_int is not None) and (not is_clean)

    # "Very likely wrong": option list-like and processed equals the first digit seen.
    very_likely_wrong = bool(option_list_like and processed_int is not None and first_number == processed_int)

    return {
        "is_clean_numeric": is_clean,
        "legacy_like_extraction": legacy_like,
        "in_range_unique_count": len(unique_in_range),
        "line_start_option_count": len(set(line_start_opts)),
        "option_list_like": option_list_like,
        "multi_in_range": multi_in_range,
        "very_likely_wrong": very_likely_wrong,
        "first_number": first_number,
        "unique_in_range_numbers": " ".join(str(x) for x in unique_in_range),
    }


def analyze_multi(
    raw: str,
    processed: Optional[str],
    lo: int,
    hi: int,
    choices: int,
    exact: bool,
) -> Dict[str, object]:
    raw_s = (raw or "").strip()
    processed_s = None if processed is None else str(processed).strip()

    # For multi-choice, "clean" means it is just numbers separated by spaces.
    is_clean = bool(re.fullmatch(r"\d+(?:\s+\d+)*", raw_s))

    # The legacy parser takes the first N digits from anywhere, which can be wrong if
    # the model echoed the full option list.
    in_range_numbers = _numbers_in_range(raw_s, lo, hi)
    unique_in_range = sorted(set(in_range_numbers))
    line_start_opts = _line_start_options(raw_s, lo, hi)
    option_list_like = len(set(line_start_opts)) >= 3  # be stricter for multi-choice

    processed_values: Optional[List[int]] = None
    if processed_s:
        try:
            processed_values = [int(x) for x in re.findall(r"\d+", processed_s)]
        except Exception:
            processed_values = None

    legacy_like = (processed_values is not None) and (not is_clean)

    expected_ok = False
    if processed_values is not None:
        if exact:
            expected_ok = len(processed_values) == choices
        else:
            expected_ok = 1 <= len(processed_values) <= choices
        expected_ok = expected_ok and all(lo <= v <= hi for v in processed_values)

    very_likely_wrong = bool(option_list_like and legacy_like and expected_ok)

    return {
        "is_clean_numeric": is_clean,
        "legacy_like_extraction": legacy_like,
        "in_range_unique_count": len(unique_in_range),
        "line_start_option_count": len(set(line_start_opts)),
        "option_list_like": option_list_like,
        "multi_in_range": len(unique_in_range) >= choices + 1,
        "very_likely_wrong": very_likely_wrong,
        "first_number": None,
        "unique_in_range_numbers": " ".join(str(x) for x in unique_in_range),
    }


def analyze_response(question_id: str, raw: str, processed: Optional[str]) -> Dict[str, object]:
    config = QUESTION_CONFIG.get(question_id)
    if not config:
        return {
            "is_clean_numeric": False,
            "legacy_like_extraction": False,
            "in_range_unique_count": 0,
            "line_start_option_count": 0,
            "option_list_like": False,
            "multi_in_range": False,
            "very_likely_wrong": False,
            "first_number": None,
            "unique_in_range_numbers": "",
        }

    lo, hi = config["scale"]
    if config["type"] == "single":
        return analyze_single(raw, processed, int(lo), int(hi))

    return analyze_multi(
        raw=raw,
        processed=processed,
        lo=int(lo),
        hi=int(hi),
        choices=int(config["choices"]),
        exact=bool(config.get("exact", False)),
    )


def main() -> None:
    rows: List[Dict[str, object]] = []

    for path in iter_hk_json_files(DATA_ROOT):
        meta = parse_filename(path)
        if meta is None:
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            # Some files may be malformed; skip to keep the audit robust.
            continue

        for round_id, resp in extract_round_responses(data):
            qid = str(resp.get("question_id") or "")
            if qid not in QUESTION_CONFIG:
                continue
            raw = str(resp.get("raw_response") or "")
            processed = resp.get("processed_response")
            analysis = analyze_response(qid, raw, processed if processed is not None else None)
            rows.append(
                {
                    "model": meta.model,
                    "language": meta.language,
                    "file": str(path),
                    "round_id": round_id,
                    "question_id": qid,
                    "processed_response": processed,
                    "raw_response": raw,
                    **analysis,
                }
            )

    if not rows:
        raise SystemExit("No Hong Kong interview rows found to audit.")

    df = pd.DataFrame(rows)
    out_dir = Path("analysis/outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_out = out_dir / "hk_legacy_parsing_audit_rows.csv"
    summary_out = out_dir / "hk_legacy_parsing_audit_summary.csv"

    df.to_csv(raw_out, index=False, encoding="utf-8-sig")

    summary = (
        df.groupby(["model", "language"], as_index=False)
        .agg(
            total=("question_id", "count"),
            clean_numeric=("is_clean_numeric", "sum"),
            legacy_like=("legacy_like_extraction", "sum"),
            option_list_like=("option_list_like", "sum"),
            very_likely_wrong=("very_likely_wrong", "sum"),
        )
        .assign(
            clean_rate=lambda x: x["clean_numeric"] / x["total"],
            legacy_like_rate=lambda x: x["legacy_like"] / x["total"],
            option_list_like_rate=lambda x: x["option_list_like"] / x["total"],
            very_likely_wrong_rate=lambda x: x["very_likely_wrong"] / x["total"],
        )
        .sort_values(["very_likely_wrong_rate", "option_list_like_rate", "legacy_like_rate"], ascending=False)
    )
    summary.to_csv(summary_out, index=False, encoding="utf-8-sig")

    print(f"Wrote row-level audit to: {raw_out}")
    print(f"Wrote model summary to: {summary_out}")
    print("\nTop 15 (by very_likely_wrong_rate):")
    display_cols = [
        "model",
        "language",
        "total",
        "clean_rate",
        "legacy_like_rate",
        "option_list_like_rate",
        "very_likely_wrong_rate",
    ]
    print(summary[display_cols].head(15).to_string(index=False))


if __name__ == "__main__":
    main()

