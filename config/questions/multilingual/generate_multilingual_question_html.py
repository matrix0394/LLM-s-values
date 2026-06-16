#!/usr/bin/env python3
from __future__ import annotations

import html
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


def arabic_question_block(code: str, question: str) -> str:
    return f"""
<div class="question-block ar-block">
  <div class="label-line"><span class="code">{html.escape(code)}</span> <span class="label">{html.escape(ITEM_LABELS[code])}</span></div>
  <div class="ar-text" dir="rtl" lang="ar">{html.escape(normalize(question))}</div>
</div>""".strip()


def generic_question_block(code: str, question: str) -> str:
    return f"""
<div class="question-block">
  <p><span class="code">{html.escape(code)}</span> <span class="label">{html.escape(ITEM_LABELS[code])}</span> "{html.escape(normalize(question))}"</p>
</div>""".strip()


def render_language_section(language_code: str, questions: dict) -> str:
    blocks = []
    for code in QUESTION_ORDER:
        entry = questions.get(code)
        question = entry["question"] if entry else "[Missing in source]"
        if language_code == "ar":
            blocks.append(arabic_question_block(code, question))
        else:
            blocks.append(generic_question_block(code, question))
    return f"""
<section class="language-section {'arabic-section' if language_code == 'ar' else ''}">
  <h1>{html.escape(LANGUAGE_NAMES[language_code])}</h1>
  {''.join(blocks)}
</section>""".strip()


def html_document(sections: list[str], title: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    @page {{
      size: letter;
      margin: 0.72in 0.78in 0.72in 0.78in;
    }}
    body {{
      margin: 0 auto;
      max-width: 7.04in;
      padding: 0;
      color: #111;
      background: #fff;
      font-family: "Times New Roman", "Songti SC", "PMingLiU", serif;
      line-height: 1.5;
      font-size: 10.5pt;
    }}
    h1 {{
      font-size: 13pt;
      font-weight: 700;
      margin: 0 0 10pt;
      page-break-after: avoid;
      break-after: avoid-page;
    }}
    .language-section {{
      margin: 0;
      page-break-after: always;
      page-break-before: auto;
      page-break-inside: auto;
      break-after: page;
      break-before: auto;
      break-inside: auto;
    }}
    .language-section:last-child {{
      page-break-after: auto;
      break-after: auto;
    }}
    .question-block {{
      margin: 0 0 7pt;
    }}
    .question-block p, .label-line, .ar-text {{
      margin: 0;
    }}
    .code {{
      font-weight: 700;
    }}
    .label {{
      font-style: italic;
      margin-left: 4pt;
    }}
    .ar-block {{
      margin-bottom: 9pt;
    }}
    .label-line {{
      direction: ltr;
      text-align: left;
      margin-bottom: 2pt;
      font-family: "Times New Roman", serif;
      font-size: 10.5pt;
      line-height: 1.2;
    }}
    .ar-text {{
      direction: rtl;
      text-align: right;
      unicode-bidi: plaintext;
      font-family: "Geeza Pro", "Arial Unicode MS", "Arial", sans-serif;
      font-size: 11.5pt;
      line-height: 1.55;
    }}
    .print-page-number {{
      display: none;
    }}
    @media print {{
      body {{
        margin: 0;
        max-width: none;
        font-size: 10.5pt;
      }}
      h1 {{
        font-size: 13pt;
      }}
      .print-page-number {{
        display: block;
        position: fixed;
        left: 0;
        right: 0;
        bottom: 0.2in;
        text-align: center;
        font-family: "Times New Roman", serif;
        font-size: 9pt;
      }}
      .print-page-number::after {{
        content: counter(page);
      }}
      .ar-text {{
        font-size: 11.5pt;
      }}
    }}
  </style>
</head>
<body>
<div class="print-page-number"></div>
{''.join(sections)}
</body>
</html>
"""


def main() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    ar_section = render_language_section("ar", load_language("ar"))
    ar_path = DOCS_DIR / "questions_ar.html"
    ar_path.write_text(html_document([ar_section], "Arabic Questions"), encoding="utf-8")
    print(f"Wrote {ar_path}")

    selected = ["ar", "ru", "zh-cn", "zh-tw", "zh-hk"]
    sections = [render_language_section(code, load_language(code)) for code in selected]
    combined_path = DOCS_DIR / "questions_selected_languages_combined.html"
    combined_path.write_text(html_document(sections, "Selected Language Questions"), encoding="utf-8")
    print(f"Wrote {combined_path}")


if __name__ == "__main__":
    main()
