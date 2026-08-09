"""Execute country-conditioned open-ended generation experiments."""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .client import GenerationClient, GenerationResult, redact_sensitive
from .prompts import build_prompt
from .scenarios import REQUIRED_LANGUAGES, Scenario
from .storage import JSONLStore, make_task_key


RECORD_SCHEMA_VERSION = "orientalism_raw_v2"


@dataclass(frozen=True)
class GenerationConfig:
    run_id: str
    model: str
    base_url: str
    api_key_env: str
    provider: str | None = None
    temperature: float = 0.7
    seed: int | None = None
    repeats: int = 1
    timeout: float = 60.0
    max_retries: int = 3
    scenario_file: str | None = None
    output_file: str | None = None
    country_conditions: list[dict[str, Any]] | None = None
    countries: list[str] | None = None
    languages: list[str] | None = None
    scenario_ids: list[str] | None = None

    def __post_init__(self) -> None:
        for name in ("run_id", "model", "base_url", "api_key_env"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.repeats < 1:
            raise ValueError("repeats must be at least 1")
        if self.timeout <= 0:
            raise ValueError("timeout must be greater than 0")
        if self.max_retries < 0:
            raise ValueError("max_retries cannot be negative")
        if not 0 <= self.temperature <= 2:
            raise ValueError("temperature must be between 0 and 2")
        if self.provider is not None and not self.provider.strip():
            raise ValueError("provider must be a non-empty string when supplied")
        if self.languages is not None:
            self._validate_languages(self.languages, "languages")
        for name in ("countries", "scenario_ids"):
            value = getattr(self, name)
            if value is not None and (
                not value or not all(isinstance(item, str) and item.strip() for item in value)
            ):
                raise ValueError(f"{name} must contain non-empty strings")
        if self.country_conditions is not None:
            if not isinstance(self.country_conditions, list) or not self.country_conditions:
                raise ValueError("country_conditions must be a non-empty array")
            seen: set[tuple[str, str]] = set()
            for index, condition in enumerate(self.country_conditions):
                if not isinstance(condition, dict):
                    raise ValueError(f"country_conditions[{index}] must be an object")
                country = condition.get("country")
                if not isinstance(country, str) or not country.strip():
                    raise ValueError(
                        f"country_conditions[{index}].country must be a non-empty string"
                    )
                languages = condition.get("languages")
                self._validate_languages(
                    languages, f"country_conditions[{index}].languages"
                )
                for language in languages:
                    pair = (country.strip(), language)
                    if pair in seen:
                        raise ValueError(
                            f"duplicate country/language condition: {pair[0]} / {pair[1]}"
                        )
                    seen.add(pair)

    @staticmethod
    def _validate_languages(value: object, location: str) -> None:
        if not isinstance(value, list) or not value or not all(
            isinstance(item, str) and item.strip() for item in value
        ):
            raise ValueError(f"{location} must contain non-empty language strings")
        unsupported = sorted(set(value) - set(REQUIRED_LANGUAGES))
        if unsupported:
            raise ValueError(
                f"{location} contains unsupported or unreviewed languages: "
                f"{', '.join(unsupported)}"
            )

    @classmethod
    def from_json(cls, path: str | Path) -> "GenerationConfig":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("Experiment config must be a JSON object")
        return cls(**data)

    def with_overrides(self, **overrides: Any) -> "GenerationConfig":
        supplied = {key: value for key, value in overrides.items() if value is not None}
        return replace(self, **supplied)


@dataclass(frozen=True)
class GenerationSummary:
    planned: int
    generated: int
    failed: int
    skipped: int
    output_file: str
    mock: bool
    real_api: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "planned": self.planned,
            "generated": self.generated,
            "failed": self.failed,
            "skipped": self.skipped,
            "output_file": self.output_file,
            "mock": self.mock,
            "real_api": self.real_api,
        }


def _safe_error(error: Exception, client: GenerationClient) -> str:
    secrets = tuple(getattr(client, "sensitive_values", ()))
    return redact_sensitive(error, secrets)


def _country_language_pairs(
    scenario: Scenario, config: GenerationConfig
) -> list[tuple[str, str]]:
    if config.country_conditions is not None:
        return [
            (str(condition["country"]).strip(), language)
            for condition in config.country_conditions
            for language in condition["languages"]
        ]

    languages = config.languages or list(REQUIRED_LANGUAGES)
    if config.countries is not None:
        return [(country.strip(), language) for country in config.countries for language in languages]
    if scenario.country:
        return [(scenario.country, language) for language in languages]
    raise ValueError(
        "country-neutral scenarios require country_conditions or legacy countries in the config"
    )


def run_generation(
    *,
    scenarios: list[Scenario],
    config: GenerationConfig,
    output_file: str | Path,
    client: GenerationClient,
) -> GenerationSummary:
    """Generate every configured task and immediately persist each outcome."""
    store = JSONLStore(output_file)
    completed = store.completed_task_keys()
    generated = failed = skipped = 0
    selected_scenarios = [
        scenario
        for scenario in scenarios
        if config.scenario_ids is None or scenario.scenario_id in config.scenario_ids
    ]
    if not selected_scenarios:
        raise ValueError("experiment configuration selected no scenarios")

    tasks = [
        (scenario, country, language)
        for scenario in selected_scenarios
        for country, language in _country_language_pairs(scenario, config)
    ]
    planned = len(tasks) * config.repeats
    is_mock = bool(getattr(client, "is_mock", False))

    for scenario, country, language in tasks:
        prompt = build_prompt(scenario, country, language)
        for repeat_id in range(config.repeats):
            task_key = make_task_key(
                model=config.model,
                country=country,
                scenario_id=scenario.scenario_id,
                prompt_language=language,
                repeat_id=repeat_id,
                scenario_version=scenario.scenario_version,
                prompt_template_version=prompt.prompt_template_version,
                prompt_fingerprint=prompt.fingerprint,
            )
            if task_key in completed:
                skipped += 1
                continue

            record = {
                "record_schema_version": RECORD_SCHEMA_VERSION,
                "run_id": config.run_id,
                "task_key": task_key,
                "model": config.model,
                "provider": config.provider,
                "requested_model": config.model,
                "resolved_model": None,
                "prompt_tokens": None,
                "completion_tokens": None,
                "total_tokens": None,
                "country": country,
                "scenario_id": scenario.scenario_id,
                "scenario_version": scenario.scenario_version,
                "domain": scenario.domain,
                "conflict_id": scenario.conflict_id,
                "conflict": scenario.conflict,
                "value_a": scenario.value_a,
                "value_b": scenario.value_b,
                "presentation_order": scenario.presentation_order,
                "prompt_language": language,
                "system_prompt": prompt.system_prompt,
                "user_prompt": prompt.user_prompt,
                "prompt_text": prompt.prompt_text,
                "messages": prompt.messages,
                "prompt_template_version": prompt.prompt_template_version,
                "prompt_fingerprint": prompt.fingerprint,
                "temperature": config.temperature,
                "seed": config.seed,
                "requested_seed": config.seed,
                "effective_seed": config.seed,
                "seed_fallback_used": False,
                "repeat_id": repeat_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "failed",
                "error": None,
            }
            try:
                result = client.generate(
                    model=config.model,
                    instruction=prompt.system_prompt,
                    question=prompt.user_prompt,
                    temperature=config.temperature,
                    seed=config.seed,
                )
                if isinstance(result, str):
                    result = GenerationResult(
                        response_text=result,
                        requested_model=config.model,
                        requested_seed=config.seed,
                        effective_seed=config.seed,
                    )
                record["response_text"] = result.response_text
                record["requested_model"] = result.requested_model
                record["resolved_model"] = result.resolved_model
                record["prompt_tokens"] = result.prompt_tokens
                record["completion_tokens"] = result.completion_tokens
                record["total_tokens"] = result.total_tokens
                record["requested_seed"] = (
                    result.requested_seed
                    if result.requested_seed is not None
                    else config.seed
                )
                record["effective_seed"] = (
                    result.effective_seed
                    if result.effective_seed is not None or result.seed_fallback_used
                    else config.seed
                )
                record["seed_fallback_used"] = result.seed_fallback_used
                record["status"] = "success"
                generated += 1
                completed.add(task_key)
            except Exception as exc:
                record["response_text"] = None
                record["error"] = _safe_error(exc, client)
                failed += 1
            store.append(record)

    return GenerationSummary(
        planned=planned,
        generated=generated,
        failed=failed,
        skipped=skipped,
        output_file=str(Path(output_file)),
        mock=is_mock,
        real_api=not is_mock,
    )
