#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "multilingual_questions_docs"
JSON_DIR = BASE_DIR / "multilingual_questions_json"
COMPLETE_JSON = BASE_DIR / "multilingual_questions_complete.json"

QUESTION_ORDER = [
    "A008",
    "A165",
    "E018",
    "E025",
    "F063",
    "F118",
    "F120",
    "G006",
    "Y002",
    "Y003",
]

ITEM_LABELS = {
    "A008": "Feeling of happiness.",
    "A165": "Most people can be trusted.",
    "E018": "Greater respect for authority.",
    "E025": "Political action: signing a petition.",
    "F063": "How important is God in your life.",
    "F118": "Justifiable: homosexuality.",
    "F120": "Justifiable: abortion.",
    "G006": "How proud of nationality.",
    "Y002": "Post-Materialist index (4-item).",
    "Y003": "Autonomy Index.",
}

LANGUAGE_NAMES = {
    "ar": "Arabic",
    "ru": "Russian",
    "zh-cn": "Chinese Simplified",
    "zh-tw": "Chinese Traditional (Taiwan)",
    "zh-hk": "Cantonese (Hong Kong)",
}

def normalize(text: str) -> str:
    return " ".join(text.replace("\r", "\n").replace("\n", " ").split())


def load_standard_language(language_code: str) -> dict:
    path = JSON_DIR / f"questions_{language_code}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_complete_language(language_code: str) -> dict:
    data = json.loads(COMPLETE_JSON.read_text(encoding="utf-8"))
    lang = data["languages"][language_code]
    out = {}
    for code, entry in lang["questions"].items():
        out[code] = {
            "question": entry["question"],
            "scale": entry["scale"],
        }
    return out


def load_language(language_code: str) -> dict:
    if language_code in {"zh-tw", "zh-hk"}:
        return load_complete_language(language_code)
    return load_standard_language(language_code)


def render_markdown(language_code: str, questions: dict) -> str:
    title = LANGUAGE_NAMES[language_code]
    lines = [f"# {title}", ""]
    for code in QUESTION_ORDER:
        entry = questions.get(code)
        label = ITEM_LABELS[code]
        if entry is None:
            lines.append(f"**{code}** *{label}* [Missing in source]")
            lines.append("")
            continue
        lines.append(f'**{code}** *{label}* "{normalize(entry["question"])}"')
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    targets = ["ar", "ru", "zh-cn", "zh-tw", "zh-hk"]
    for language_code in targets:
        questions = load_language(language_code)
        output = DOCS_DIR / f"questions_{language_code}_doc.md"
        output.write_text(render_markdown(language_code, questions), encoding="utf-8")
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
