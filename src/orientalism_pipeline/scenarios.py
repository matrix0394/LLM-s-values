"""Load and validate open-ended multilingual value scenarios."""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


COMMON_REQUIRED_FIELDS = (
    "scenario_id",
    "domain",
    "conflict",
    "value_a",
    "value_b",
    "translations",
)
PHASE1_REQUIRED_FIELDS = COMMON_REQUIRED_FIELDS + ("country",)
PHASE2A_REQUIRED_FIELDS = COMMON_REQUIRED_FIELDS + (
    "scenario_version",
    "conflict_id",
    "presentation_order",
    "source_framework",
    "source_construct",
    "source_item_id",
    "source_item_ids",
    "related_source_item_ids",
    "source_mapping_type",
    "source_reference",
    "status",
    "notes",
)
REQUIRED_LANGUAGES = ("en", "zh")
PHASE2A_DOMAINS = {
    "social_values": 4,
    "political_values": 4,
    "economic_values": 4,
}
PHASE2A_CONFLICT_IDS = {
    "SOC-01",
    "SOC-02",
    "POL-01",
    "POL-02",
    "ECO-01",
    "ECO-02",
}
PRESENTATION_ORDERS = {"A_first", "B_first"}
SOURCE_MAPPING_TYPES = {"direct", "adjacent", "scenario_extension"}
ALLOWED_WVS_WAVE7_SOURCE_ITEMS = {
    "Q1",
    "Q27",
    "Q28",
    "Q31",
    "Q32",
    "Q33",
    "Q38",
    "Q106",
    "Q108",
    "Q150",
    "Q154",
    "Q155",
    "Q196",
    "Q197",
    "Q198",
    "Q235",
    "Q238",
    "Q241",
    "Q243",
    "Q244",
    "Q246",
    "Q247",
    "Q249",
    "Q250",
    # Variable-style IDs explicitly retained as provisional adjacent mappings
    # for review candidates. They are not inferred by the validator.
    "Y002",
    "Y003",
}
SOURCE_PLACEHOLDER_TERMS = ("待核验", "可能对应", "pending verification")

# This is intentionally a narrow safeguard, not a claim that natural-language
# quality or every possible country name can be decided automatically.
PROHIBITED_COUNTRY_TERMS = (
    "China",
    "Chinese",
    "Germany",
    "German",
    "Tunisia",
    "Tunisian",
    "United States",
    "American",
    "United Kingdom",
    "British",
    "中国",
    "中国人",
    "德国",
    "德国人",
    "突尼斯",
    "美国",
    "英国",
)
PROHIBITED_PURPOSE_TERMS = (
    "AI Orientalism",
    "Orientalism",
    "LLM Judge",
    "World Values Survey",
    "WVS",
    "AI东方主义",
    "东方主义",
    "文化偏见",
)
NUMERIC_RESPONSE_PATTERNS = (
    re.compile(r"\b(?:choose|select|reply|respond)\b.{0,40}\b(?:number|option|score)\b", re.I),
    re.compile(r"(?:选择|回答|回复).{0,20}(?:数字|编号|选项)"),
    re.compile(r"(?:打分|评分|固定选项|只需回答数字)"),
)


class ScenarioValidationError(ValueError):
    """Raised when scenario data cannot support the requested experiment."""


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    domain: str
    conflict: str
    value_a: str
    value_b: str
    translations: Mapping[str, str]
    country: str | None = None
    scenario_version: str | None = None
    conflict_id: str | None = None
    presentation_order: str | None = None
    source_framework: str | None = None
    source_construct: str | None = None
    source_item_id: str | None = None
    source_item_ids: tuple[str, ...] | None = None
    related_source_item_ids: tuple[str, ...] | None = None
    source_mapping_type: str | None = None
    source_reference: str | None = None
    status: str | None = None
    notes: str | None = None

    @property
    def is_phase2a(self) -> bool:
        return self.scenario_version is not None

    def text_for(self, language: str) -> str:
        try:
            return self.translations[language]
        except KeyError as exc:
            raise ScenarioValidationError(
                f"Scenario {self.scenario_id!r} has no {language!r} translation"
            ) from exc


def _require_nonempty_string(data: Mapping[str, Any], field: str, location: str) -> str:
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ScenarioValidationError(f"{location}: field {field!r} must be a non-empty string")
    return value.strip()


def _is_phase2a_data(data: Mapping[str, Any]) -> bool:
    phase2_only_fields = set(PHASE2A_REQUIRED_FIELDS) - set(PHASE1_REQUIRED_FIELDS)
    return any(field in data for field in phase2_only_fields)


def _require_source_item_list(
    data: Mapping[str, Any], field: str, location: str, *, allow_empty: bool
) -> tuple[str, ...]:
    value = data.get(field)
    if not isinstance(value, list):
        raise ScenarioValidationError(f"{location}: field {field!r} must be an array")
    if not allow_empty and not value:
        raise ScenarioValidationError(f"{location}: field {field!r} must not be empty")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise ScenarioValidationError(
            f"{location}: field {field!r} must contain only non-empty strings"
        )
    normalized = tuple(item.strip() for item in value)
    if len(set(normalized)) != len(normalized):
        raise ScenarioValidationError(f"{location}: field {field!r} must not contain duplicates")
    invalid = sorted(set(normalized) - ALLOWED_WVS_WAVE7_SOURCE_ITEMS)
    if invalid:
        raise ScenarioValidationError(
            f"{location}: field {field!r} contains unapproved WVS item IDs: {', '.join(invalid)}"
        )
    return normalized


def _find_term(text: str, terms: tuple[str, ...]) -> str | None:
    for term in terms:
        if term.isascii():
            if re.search(rf"\b{re.escape(term)}\b", text, re.I):
                return term
        elif term in text:
            return term
    return None


def _validate_phase2a_text(text: str, location: str) -> None:
    country_term = _find_term(text, PROHIBITED_COUNTRY_TERMS)
    if country_term:
        raise ScenarioValidationError(
            f"{location}: contains prohibited country reference {country_term!r}"
        )

    purpose_term = _find_term(text, PROHIBITED_PURPOSE_TERMS)
    if purpose_term:
        raise ScenarioValidationError(
            f"{location}: contains prohibited experiment-purpose term {purpose_term!r}"
        )

    if any(pattern.search(text) for pattern in NUMERIC_RESPONSE_PATTERNS):
        raise ScenarioValidationError(f"{location}: appears to require a numeric or fixed-option answer")


def validate_scenario(data: Mapping[str, Any], index: int = 0) -> Scenario:
    """Validate one raw scenario mapping and return its normalized representation."""
    if not isinstance(data, Mapping):
        raise ScenarioValidationError(f"Scenario at index {index} must be an object")

    location = f"Scenario at index {index}"
    is_phase2a = _is_phase2a_data(data)
    required_fields = PHASE2A_REQUIRED_FIELDS if is_phase2a else PHASE1_REQUIRED_FIELDS
    missing = [field for field in required_fields if field not in data]
    if missing:
        raise ScenarioValidationError(f"{location} is missing required fields: {', '.join(missing)}")

    translations = data["translations"]
    if not isinstance(translations, Mapping):
        raise ScenarioValidationError(f"{location}: 'translations' must be an object")

    missing_languages = [lang for lang in REQUIRED_LANGUAGES if lang not in translations]
    if missing_languages:
        raise ScenarioValidationError(
            f"{location}: translations are missing required languages: {', '.join(missing_languages)}"
        )

    normalized_translations = {
        language: _require_nonempty_string(translations, language, f"{location}.translations")
        for language in REQUIRED_LANGUAGES
    }
    value_a = _require_nonempty_string(data, "value_a", location)
    value_b = _require_nonempty_string(data, "value_b", location)
    if value_a.casefold() == value_b.casefold():
        raise ScenarioValidationError(f"{location}: value_a and value_b must be different")

    phase2_values: dict[str, str | None] = {
        "scenario_version": None,
        "conflict_id": None,
        "presentation_order": None,
        "source_framework": None,
        "source_construct": None,
        "source_item_id": None,
        "source_item_ids": None,
        "related_source_item_ids": None,
        "source_mapping_type": None,
        "source_reference": None,
        "status": None,
        "notes": None,
    }
    if is_phase2a:
        for language, text in normalized_translations.items():
            _validate_phase2a_text(text, f"{location}.translations.{language}")

        presentation_order = _require_nonempty_string(data, "presentation_order", location)
        if presentation_order not in PRESENTATION_ORDERS:
            raise ScenarioValidationError(
                f"{location}: presentation_order must be one of {sorted(PRESENTATION_ORDERS)}"
            )

        raw_source_item_id = data.get("source_item_id")
        if raw_source_item_id is not None and (
            not isinstance(raw_source_item_id, str) or not raw_source_item_id.strip()
        ):
            raise ScenarioValidationError(
                f"{location}: source_item_id must be a non-empty string or null"
            )
        source_item_id = (
            raw_source_item_id.strip() if isinstance(raw_source_item_id, str) else None
        )
        if source_item_id is not None and source_item_id not in ALLOWED_WVS_WAVE7_SOURCE_ITEMS:
            raise ScenarioValidationError(
                f"{location}: source_item_id {source_item_id!r} is not an approved WVS Wave 7 item"
            )
        source_item_ids = _require_source_item_list(
            data, "source_item_ids", location, allow_empty=source_item_id is None
        )
        related_source_item_ids = _require_source_item_list(
            data, "related_source_item_ids", location, allow_empty=True
        )
        if source_item_id is not None and source_item_id not in source_item_ids:
            raise ScenarioValidationError(
                f"{location}: source_item_id must also appear in source_item_ids"
            )
        if source_item_id is None and source_item_ids:
            raise ScenarioValidationError(
                f"{location}: source_item_ids must be empty when source_item_id is null"
            )
        overlap = sorted(set(source_item_ids) & set(related_source_item_ids))
        if overlap:
            raise ScenarioValidationError(
                f"{location}: primary and related source item IDs overlap: {', '.join(overlap)}"
            )

        source_mapping_type = _require_nonempty_string(data, "source_mapping_type", location)
        if source_mapping_type not in SOURCE_MAPPING_TYPES:
            raise ScenarioValidationError(
                f"{location}: source_mapping_type must be one of {sorted(SOURCE_MAPPING_TYPES)}"
            )

        source_reference = _require_nonempty_string(data, "source_reference", location)
        phase2_values = {
            "scenario_version": _require_nonempty_string(data, "scenario_version", location),
            "conflict_id": _require_nonempty_string(data, "conflict_id", location),
            "presentation_order": presentation_order,
            "source_framework": _require_nonempty_string(data, "source_framework", location),
            "source_construct": _require_nonempty_string(data, "source_construct", location),
            "source_item_id": source_item_id,
            "source_item_ids": source_item_ids,
            "related_source_item_ids": related_source_item_ids,
            "source_mapping_type": source_mapping_type,
            "source_reference": source_reference,
            "status": _require_nonempty_string(data, "status", location),
            "notes": _require_nonempty_string(data, "notes", location),
        }

    return Scenario(
        scenario_id=_require_nonempty_string(data, "scenario_id", location),
        domain=_require_nonempty_string(data, "domain", location),
        conflict=_require_nonempty_string(data, "conflict", location),
        value_a=value_a,
        value_b=value_b,
        translations=normalized_translations,
        country=None if is_phase2a else _require_nonempty_string(data, "country", location),
        **phase2_values,
    )


def _validate_phase2a_collection(scenarios: list[Scenario]) -> None:
    scenario_ids = [scenario.scenario_id for scenario in scenarios]
    duplicate_ids = sorted(
        scenario_id for scenario_id, count in Counter(scenario_ids).items() if count > 1
    )
    if duplicate_ids:
        raise ScenarioValidationError(
            f"Duplicate Phase 2A scenario_id values: {', '.join(duplicate_ids)}"
        )

    domain_counts = Counter(scenario.domain for scenario in scenarios)
    if domain_counts != Counter(PHASE2A_DOMAINS):
        raise ScenarioValidationError(
            f"Phase 2A requires exactly four scenarios in each domain; got {dict(domain_counts)}"
        )

    conflict_counts = Counter(scenario.conflict_id for scenario in scenarios)
    expected_conflicts = Counter({conflict_id: 2 for conflict_id in PHASE2A_CONFLICT_IDS})
    if conflict_counts != expected_conflicts:
        raise ScenarioValidationError(
            f"Phase 2A requires exactly two scenarios per conflict_id; got {dict(conflict_counts)}"
        )

    if len(scenarios) != 12:
        raise ScenarioValidationError(f"Phase 2A requires exactly 12 scenarios; got {len(scenarios)}")

    for conflict_id in sorted(PHASE2A_CONFLICT_IDS):
        order_counts = Counter(
            scenario.presentation_order
            for scenario in scenarios
            if scenario.conflict_id == conflict_id
        )
        if order_counts != Counter({"A_first": 1, "B_first": 1}):
            raise ScenarioValidationError(
                f"Conflict {conflict_id} must contain one A_first and one B_first scenario; "
                f"got {dict(order_counts)}"
            )


def load_scenarios(path: str | Path) -> list[Scenario]:
    """Load a JSON scenario file and validate either Phase 1 or Phase 2A data."""
    scenario_path = Path(path)
    try:
        raw = json.loads(scenario_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ScenarioValidationError(f"Scenario file not found: {scenario_path}") from exc
    except json.JSONDecodeError as exc:
        raise ScenarioValidationError(f"Invalid JSON in {scenario_path}: {exc.msg}") from exc

    raw_scenarios = raw.get("scenarios") if isinstance(raw, Mapping) else raw
    if not isinstance(raw_scenarios, list) or not raw_scenarios:
        raise ScenarioValidationError("Scenario file must contain a non-empty 'scenarios' list")

    scenarios = [validate_scenario(item, index) for index, item in enumerate(raw_scenarios)]
    if all(scenario.is_phase2a for scenario in scenarios):
        _validate_phase2a_collection(scenarios)
        return scenarios
    if any(scenario.is_phase2a for scenario in scenarios):
        raise ScenarioValidationError("Scenario file cannot mix Phase 1 and Phase 2A records")

    identities: set[tuple[str, str | None]] = set()
    for scenario in scenarios:
        identity = (scenario.scenario_id, scenario.country)
        if identity in identities:
            raise ScenarioValidationError(
                f"Duplicate scenario_id/country pair: {scenario.scenario_id!r}, {scenario.country!r}"
            )
        identities.add(identity)
    return scenarios
