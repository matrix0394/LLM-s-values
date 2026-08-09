"""OpenAI-compatible and mock clients for open-ended answer generation."""

from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass
from typing import Protocol


class MissingAPIKeyError(RuntimeError):
    """Raised when a real API run has no configured secret."""


class GenerationClient(Protocol):
    def generate(
        self,
        *,
        model: str,
        instruction: str,
        question: str,
        temperature: float,
        seed: int | None,
    ) -> "GenerationResult":
        """Generate one open-ended response."""


@dataclass(frozen=True)
class GenerationResult:
    """Provider-neutral response text and optional routing/usage metadata."""

    response_text: str
    requested_model: str
    resolved_model: str | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    requested_seed: int | None = None
    effective_seed: int | None = None
    seed_fallback_used: bool = False


def redact_sensitive(value: object, secrets: tuple[str, ...] = ()) -> str:
    """Remove known secrets and common bearer/API-key forms from an error string."""
    text = str(value)
    for secret in secrets:
        if secret:
            text = text.replace(secret, "[REDACTED]")
    text = re.sub(r"(?i)(authorization\s*[:=]\s*bearer\s+)[^\s,;]+", r"\1[REDACTED]", text)
    text = re.sub(r"(?i)(api[_-]?key\s*[:=]\s*)[^\s,;]+", r"\1[REDACTED]", text)
    text = re.sub(r"\bsk-[A-Za-z0-9_-]{8,}\b", "[REDACTED]", text)
    return text


@dataclass
class MockClient:
    """Deterministic, offline client used by tests and smoke runs."""

    call_count: int = 0
    is_mock: bool = True

    def generate(
        self,
        *,
        model: str,
        instruction: str,
        question: str,
        temperature: float,
        seed: int | None,
    ) -> GenerationResult:
        self.call_count += 1
        if any("\u4e00" <= char <= "\u9fff" for char in question):
            response_text = (
                "我会先和父母充分沟通，了解他们需要陪伴和照顾的实际程度，同时评估外地工作的长期机会。"
                "如果照护可以通过定期回家、共同安排或其他支持解决，我会接受工作并承担持续的家庭责任；"
                "如果父母确实缺少替代照护，我会重新协商入职时间或寻找更接近家乡的机会。"
            )
        else:
            response_text = (
                "I would first discuss my parents' practical care needs and the long-term value of the offer. "
                "If regular visits and shared support could meet those needs, I would take the job while keeping "
                "clear family commitments. If no adequate care alternative existed, I would negotiate the start "
                "date or look for a comparable opportunity closer to home."
            )
        return GenerationResult(
            response_text=response_text,
            requested_model=model,
            resolved_model=model,
            requested_seed=seed,
            effective_seed=seed,
            seed_fallback_used=False,
        )


class OpenAICompatibleClient:
    """Small OpenAI-compatible client with retry and optional seed fallback."""

    is_mock = False

    def __init__(
        self,
        *,
        base_url: str,
        api_key_env: str,
        timeout: float,
        max_retries: int,
        dotenv_path: str | None = None,
    ) -> None:
        api_key = os.environ.get(api_key_env)
        if not api_key:
            try:
                from dotenv import load_dotenv

                load_dotenv(dotenv_path=dotenv_path, override=False)
            except ImportError:
                pass
            api_key = os.environ.get(api_key_env)
        if not api_key:
            raise MissingAPIKeyError(
                f"API key environment variable {api_key_env!r} is not set"
            )

        from openai import OpenAI

        self._api_key = api_key
        # The pipeline owns retry behavior so the SDK must not add hidden retries.
        self._client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=0,
        )
        self._max_retries = max_retries

    @property
    def sensitive_values(self) -> tuple[str, ...]:
        return (self._api_key,)

    @staticmethod
    def _seed_is_unsupported(error: Exception) -> bool:
        message = str(error).lower()
        return "seed" in message and any(
            marker in message
            for marker in (
                "unsupported",
                "not supported",
                "does not support",
                "not permitted",
                "unknown",
                "unrecognized",
                "extra inputs",
                "unexpected keyword",
            )
        )

    @staticmethod
    def _response_field(value: object, field: str) -> object | None:
        if isinstance(value, dict):
            return value.get(field)
        return getattr(value, field, None)

    def _request(self, params: dict, *, allow_seed_fallback: bool) -> GenerationResult:
        requested_seed = params.get("seed")
        effective_seed = requested_seed
        seed_fallback_used = False
        try:
            response = self._client.chat.completions.create(**params)
        except Exception as exc:
            if allow_seed_fallback and "seed" in params and self._seed_is_unsupported(exc):
                without_seed = dict(params)
                without_seed.pop("seed", None)
                response = self._client.chat.completions.create(**without_seed)
                effective_seed = None
                seed_fallback_used = True
            else:
                raise
        content = response.choices[0].message.content
        if not content or not content.strip():
            raise RuntimeError("API returned an empty response")
        usage = self._response_field(response, "usage")
        return GenerationResult(
            response_text=content.strip(),
            requested_model=str(params["model"]),
            resolved_model=self._response_field(response, "model"),
            prompt_tokens=self._response_field(usage, "prompt_tokens"),
            completion_tokens=self._response_field(usage, "completion_tokens"),
            total_tokens=self._response_field(usage, "total_tokens"),
            requested_seed=requested_seed,
            effective_seed=effective_seed,
            seed_fallback_used=seed_fallback_used,
        )

    def generate(
        self,
        *,
        model: str,
        instruction: str,
        question: str,
        temperature: float,
        seed: int | None,
    ) -> GenerationResult:
        params = {
            "model": model,
            "messages": [
                {"role": "system", "content": instruction},
                {"role": "user", "content": question},
            ],
            "temperature": temperature,
        }
        if seed is not None:
            params["seed"] = seed

        last_error: Exception | None = None
        for attempt in range(self._max_retries + 1):
            try:
                return self._request(params, allow_seed_fallback=seed is not None)
            except Exception as exc:
                last_error = exc
                if attempt < self._max_retries:
                    time.sleep(min(2**attempt, 8))
        sanitized = redact_sensitive(last_error, self.sensitive_values)
        raise RuntimeError(sanitized) from None
