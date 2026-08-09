"""Non-interactive CLI for scenario validation and generation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .client import MockClient, OpenAICompatibleClient
from .generate import GenerationConfig, run_generation
from .scenarios import load_scenarios


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCENARIOS = PROJECT_ROOT / "config" / "scenarios" / "orientalism_phase1.json"
DEFAULT_SMOKE_OUTPUT = (
    PROJECT_ROOT / "results" / "orientalism" / "phase1_smoke" / "raw_responses.jsonl"
)


def _resolve_project_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def _add_generation_overrides(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--scenarios", help="Scenario JSON file")
    parser.add_argument("--output", help="Output raw_responses.jsonl path")
    parser.add_argument("--run-id")
    parser.add_argument("--model")
    parser.add_argument("--base-url")
    parser.add_argument("--api-key-env")
    parser.add_argument("--temperature", type=float)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--repeats", type=int)
    parser.add_argument("--timeout", type=float)
    parser.add_argument("--max-retries", type=int)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Open-ended value scenario pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="Validate bilingual scenario data")
    validate.add_argument("--scenarios", default=str(DEFAULT_SCENARIOS))

    smoke = subparsers.add_parser("smoke", help="Run an experiment with an offline mock")
    smoke.add_argument("--config", help="Optional mock experiment JSON config")
    _add_generation_overrides(smoke)

    generate = subparsers.add_parser(
        "generate", help="Run an explicitly confirmed real API experiment"
    )
    generate.add_argument("--config", required=True, help="Real API experiment JSON config")
    generate.add_argument(
        "--confirm-real-api",
        action="store_true",
        help="Required acknowledgement that this command may incur API charges",
    )
    _add_generation_overrides(generate)
    return parser


def _overrides(args: argparse.Namespace) -> dict:
    return {
        "run_id": args.run_id,
        "model": args.model,
        "base_url": args.base_url,
        "api_key_env": args.api_key_env,
        "temperature": args.temperature,
        "seed": args.seed,
        "repeats": args.repeats,
        "timeout": args.timeout,
        "max_retries": args.max_retries,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "validate":
        scenarios = load_scenarios(_resolve_project_path(args.scenarios))
        print(json.dumps({"valid": True, "scenario_count": len(scenarios)}, ensure_ascii=False))
        return 0

    if args.command == "smoke":
        if args.config:
            config = GenerationConfig.from_json(
                _resolve_project_path(args.config)
            ).with_overrides(**_overrides(args))
        else:
            config = GenerationConfig(
                run_id="orientalism_phase1_mock_smoke",
                model="mock-phase1",
                provider="mock",
                base_url="mock://offline",
                api_key_env="UNUSED_FOR_MOCK",
            ).with_overrides(**_overrides(args))
        scenario_path = _resolve_project_path(
            args.scenarios or config.scenario_file or DEFAULT_SCENARIOS
        )
        output_path = _resolve_project_path(
            args.output or config.output_file or DEFAULT_SMOKE_OUTPUT
        )
        client = MockClient()
    else:
        if not args.confirm_real_api:
            parser.error(
                "generate requires --confirm-real-api; no API client was created and no request was sent"
            )
        config = GenerationConfig.from_json(
            _resolve_project_path(args.config)
        ).with_overrides(**_overrides(args))
        scenario_path = _resolve_project_path(
            args.scenarios or config.scenario_file or DEFAULT_SCENARIOS
        )
        output_path = _resolve_project_path(
            args.output or config.output_file or "raw_responses.jsonl"
        )
        client = OpenAICompatibleClient(
            base_url=config.base_url,
            api_key_env=config.api_key_env,
            timeout=config.timeout,
            max_retries=config.max_retries,
            dotenv_path=str(PROJECT_ROOT / ".env"),
        )

    scenarios = load_scenarios(scenario_path)
    summary = run_generation(
        scenarios=scenarios,
        config=config,
        output_file=output_path,
        client=client,
    )
    print(json.dumps(summary.as_dict(), ensure_ascii=False))
    return 0 if summary.failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
