#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "multilingual_questions_json"
OUTPUT_DIR = BASE_DIR / "multilingual_questions_docs"
UNICODE_OUTPUT = OUTPUT_DIR / "multilingual_questions_all_languages_unicode.tex"
SAFE_OUTPUT = OUTPUT_DIR / "multilingual_questions_all_languages_safe.tex"

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
    "de": "German",
    "es": "Spanish",
    "fr": "French",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "pt": "Portuguese",
    "ru": "Russian",
    "zh-cn": "Chinese (Simplified)",
}

LATIN_SAFE_MAP = {
    "À": r"\`{A}",
    "Á": r"\'{A}",
    "Â": r"\^{A}",
    "Ã": r"\~{A}",
    "Ä": r"\"{A}",
    "Å": r"\r{A}",
    "Æ": r"\AE{}",
    "Ç": r"\c{C}",
    "È": r"\`{E}",
    "É": r"\'{E}",
    "Ê": r"\^{E}",
    "Ë": r"\"{E}",
    "Ì": r"\`{I}",
    "Í": r"\'{I}",
    "Î": r"\^{I}",
    "Ï": r"\"{I}",
    "Ñ": r"\~{N}",
    "Ò": r"\`{O}",
    "Ó": r"\'{O}",
    "Ô": r"\^{O}",
    "Õ": r"\~{O}",
    "Ö": r"\"{O}",
    "Ø": r"\O{}",
    "Ù": r"\`{U}",
    "Ú": r"\'{U}",
    "Û": r"\^{U}",
    "Ü": r"\"{U}",
    "Ý": r"\'{Y}",
    "ß": r"\ss{}",
    "à": r"\`{a}",
    "á": r"\'{a}",
    "â": r"\^{a}",
    "ã": r"\~{a}",
    "ä": r"\"{a}",
    "å": r"\r{a}",
    "æ": r"\ae{}",
    "ç": r"\c{c}",
    "è": r"\`{e}",
    "é": r"\'{e}",
    "ê": r"\^{e}",
    "ë": r"\"{e}",
    "ì": r"\`{i}",
    "í": r"\'{i}",
    "î": r"\^{i}",
    "ï": r"\"{i}",
    "ñ": r"\~{n}",
    "ò": r"\`{o}",
    "ó": r"\'{o}",
    "ô": r"\^{o}",
    "õ": r"\~{o}",
    "ö": r"\"{o}",
    "ø": r"\o{}",
    "ù": r"\`{u}",
    "ú": r"\'{u}",
    "û": r"\^{u}",
    "ü": r"\"{u}",
    "ý": r"\'{y}",
    "ÿ": r"\"{y}",
    "Œ": r"\OE{}",
    "œ": r"\oe{}",
}

UNICODE_PUNCT_MAP = {
    "\u00a0": " ",
    "\u202f": " ",
    "\u2009": " ",
    '"': "'",
    "\u2018": "'",
    "\u2019": "'",
    "\u201b": "'",
    "\u2032": "'",
    "\u201c": "`",
    "\u201d": "'",
    "\u201e": "`",
    "\u00ab": "`",
    "\u00bb": "'",
    "\u300c": "`",
    "\u300d": "'",
    "\u300e": "`",
    "\u300f": "'",
    "\u2013": "--",
    "\u2014": "---",
    "\u2212": "-",
    "\u2026": r"\ldots{}",
    "\u00bf": r"\textquestiondown{}",
    "\u00a1": r"\textexclamdown{}",
}


def normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\n", " ")
    return re.sub(r"\s+", " ", text).strip()


def escape_latex(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


def latex_safe_text(text: str, language_code: str) -> str:
    text = normalize_whitespace(text)
    text = escape_latex(text)
    for src, dst in UNICODE_PUNCT_MAP.items():
        text = text.replace(src, dst)

    if language_code in {"de", "es", "fr", "it", "pt"}:
        for src, dst in LATIN_SAFE_MAP.items():
            text = text.replace(src, dst)

    return text


def unicode_text(text: str) -> str:
    return normalize_whitespace(text)


def render_item(code: str, entry: dict[str, str] | None, language_code: str, safe: bool) -> str:
    label = ITEM_LABELS[code]
    if entry is None:
        return (
            rf"\item[\textbf{{{code}}}] \emph{{{label}}} "
            rf"\textbf{{[Missing in source JSON for {language_code}]}}"
        )

    question = entry["question"]
    rendered_question = latex_safe_text(question, language_code) if safe else unicode_text(question)
    return rf"\item[\textbf{{{code}}}] \emph{{{label}}} ``{rendered_question}''"


def render_language_block(language_code: str, data: dict[str, dict[str, str]], safe: bool) -> str:
    language_name = LANGUAGE_NAMES.get(language_code, language_code)
    lines = [
        rf"\section*{{{language_name}}}",
        rf"% Source: multilingual_questions_json/questions_{language_code}.json",
        r"\begin{enumerate}",
    ]
    for code in QUESTION_ORDER:
        lines.append(render_item(code, data.get(code), language_code, safe))
    lines.append(r"\end{enumerate}")
    return "\n".join(lines)


def document_header(safe: bool) -> list[str]:
    header = [
        "% Auto-generated by generate_multilingual_question_tex.py",
    ]
    if safe:
        header.extend(
            [
                "% Safe version: converts problematic punctuation and western accented letters",
                "% into LaTeX-friendly forms where possible.",
                "% Recommended packages: \\usepackage[T1]{fontenc} \\usepackage{textcomp}",
                "% Arabic, Cyrillic, CJK sections still contain Unicode and are best compiled with XeLaTeX or LuaLaTeX.",
            ]
        )
    else:
        header.extend(
            [
                "% Unicode version: preserves original localized characters from the JSON files.",
                "% Recommended compiler: XeLaTeX or LuaLaTeX.",
            ]
        )
    return header


def build_document(safe: bool) -> str:
    header = document_header(safe)
    blocks = []
    for path in sorted(INPUT_DIR.glob("questions_*.json")):
        language_code = path.stem.removeprefix("questions_")
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        blocks.append(render_language_block(language_code, data, safe=safe))

    return "\n\n".join(header + [""] + blocks) + "\n"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    UNICODE_OUTPUT.write_text(build_document(safe=False), encoding="utf-8")
    SAFE_OUTPUT.write_text(build_document(safe=True), encoding="utf-8")
    for path in sorted(INPUT_DIR.glob("questions_*.json")):
        language_code = path.stem.removeprefix("questions_")
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)

        unicode_path = OUTPUT_DIR / f"{path.stem}_unicode.tex"
        safe_path = OUTPUT_DIR / f"{path.stem}_safe.tex"
        unicode_body = "\n\n".join(document_header(False) + ["", render_language_block(language_code, data, safe=False)]) + "\n"
        safe_body = "\n\n".join(document_header(True) + ["", render_language_block(language_code, data, safe=True)]) + "\n"
        unicode_path.write_text(unicode_body, encoding="utf-8")
        safe_path.write_text(safe_body, encoding="utf-8")

    print(f"Wrote {UNICODE_OUTPUT}")
    print(f"Wrote {SAFE_OUTPUT}")


if __name__ == "__main__":
    main()
