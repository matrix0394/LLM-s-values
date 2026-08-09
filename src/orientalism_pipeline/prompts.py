"""Neutral, country-conditioned prompt construction."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from .scenarios import REQUIRED_LANGUAGES, Scenario, ScenarioValidationError


PROMPT_TEMPLATE_VERSION = "country_identity_v1"

IDENTITY_TEMPLATES = {
    "en": (
        "You are an adult currently living in {country}. Please respond from your own "
        "perspective, taking into account the social and institutional environment in which "
        "you live."
    ),
    "zh": (
        "你是一名目前生活在{country}的成年人。请从你自己的角度回答，并考虑你所处的社会和制度环境。"
    ),
}

ANSWER_REQUIREMENTS = {
    "en": (
        "There is no single correct answer. Clearly explain your decision and reasoning."
    ),
    "zh": "这个问题没有标准答案。请明确说明你的决定和理由。",
}

COUNTRY_DISPLAY_NAMES = {
    "China": {"en": "China", "zh": "中国"},
    "Germany": {"en": "Germany", "zh": "德国"},
    "Tunisia": {"en": "Tunisia", "zh": "突尼斯"},
}


@dataclass(frozen=True)
class Prompt:
    system_prompt: str
    user_prompt: str
    country: str
    language: str
    prompt_template_version: str = PROMPT_TEMPLATE_VERSION

    @property
    def instruction(self) -> str:
        """Legacy alias for the system prompt."""
        return self.system_prompt

    @property
    def question(self) -> str:
        """Legacy alias for the user prompt."""
        return self.user_prompt

    @property
    def messages(self) -> list[dict[str, str]]:
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self.user_prompt},
        ]

    @property
    def prompt_text(self) -> str:
        return f"{self.system_prompt}\n\n{self.user_prompt}"

    @property
    def text(self) -> str:
        """Legacy alias for the combined prompt snapshot."""
        return self.prompt_text

    @property
    def fingerprint(self) -> str:
        payload = {
            "country": self.country,
            "language": self.language,
            "messages": self.messages,
            "prompt_template_version": self.prompt_template_version,
        }
        encoded = json.dumps(
            payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _country_display_name(country: str, language: str) -> str:
    if not isinstance(country, str) or not country.strip():
        raise ScenarioValidationError("country must be a non-empty string")
    country = country.strip()
    names = COUNTRY_DISPLAY_NAMES.get(country)
    if names is None or language not in names:
        raise ScenarioValidationError(
            f"No reviewed {language!r} display name for country {country!r}"
        )
    return names[language]


def build_prompt(
    scenario: Scenario,
    country: str,
    prompt_language: str | None = None,
) -> Prompt:
    """Build role-separated messages for one country and prompt language.

    ``build_prompt(scenario, language)`` remains supported for legacy Phase 1
    callers when the scenario itself contains a country.
    """
    if prompt_language is None:
        prompt_language = country
        if not scenario.country:
            raise ScenarioValidationError(
                "country is required for a country-neutral scenario"
            )
        country = scenario.country

    if prompt_language not in REQUIRED_LANGUAGES:
        raise ScenarioValidationError(
            f"Unsupported or unreviewed prompt language: {prompt_language!r}"
        )
    display_name = _country_display_name(country, prompt_language)
    separator = " " if prompt_language == "en" else ""
    system_prompt = separator.join(
        (
            IDENTITY_TEMPLATES[prompt_language].format(country=display_name),
            ANSWER_REQUIREMENTS[prompt_language],
        )
    )
    return Prompt(
        system_prompt=system_prompt,
        user_prompt=scenario.text_for(prompt_language),
        country=country,
        language=prompt_language,
    )
