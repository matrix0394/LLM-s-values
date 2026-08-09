from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.orientalism_pipeline.cli import main
from src.orientalism_pipeline.client import GenerationResult, MockClient, OpenAICompatibleClient
from src.orientalism_pipeline.generate import GenerationConfig, run_generation
from src.orientalism_pipeline.prompts import (
    ANSWER_REQUIREMENTS,
    IDENTITY_TEMPLATES,
    PROMPT_TEMPLATE_VERSION,
    build_prompt,
)
from src.orientalism_pipeline.scenarios import (
    ScenarioValidationError,
    load_scenarios,
    validate_scenario,
)
from src.orientalism_pipeline.storage import JSONLStore, make_task_key


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCENARIO_FILE = PROJECT_ROOT / "config" / "scenarios" / "orientalism_phase1.json"
PHASE2A_SCENARIO_FILE = (
    PROJECT_ROOT / "config" / "scenarios" / "orientalism_phase2a.json"
)
PHASE2A_SMOKE_CONFIG = (
    PROJECT_ROOT
    / "config"
    / "experiments"
    / "orientalism_phase2a_soc_family_china_smoke.json"
)


def valid_scenario_data() -> dict:
    return {
        "scenario_id": "scenario-1",
        "domain": "social_values",
        "conflict": "family_responsibility_vs_individual_autonomy",
        "value_a": "family_responsibility",
        "value_b": "individual_autonomy",
        "country": "China",
        "translations": {"en": "English question", "zh": "中文问题"},
    }


def phase2a_data() -> dict:
    return json.loads(PHASE2A_SCENARIO_FILE.read_text(encoding="utf-8"))


def write_scenario_file(tmp_path: Path, data: dict) -> Path:
    path = tmp_path / "scenarios.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path


def phase1_config(**overrides) -> GenerationConfig:
    values = {
        "run_id": "test-run",
        "model": "mock-model",
        "base_url": "mock://offline",
        "api_key_env": "UNUSED_FOR_MOCK",
        "temperature": 0.4,
        "seed": 7,
        "repeats": 1,
        "timeout": 5,
        "max_retries": 0,
    }
    values.update(overrides)
    return GenerationConfig(**values)


def test_missing_scenario_field_is_rejected() -> None:
    data = valid_scenario_data()
    data.pop("conflict")

    with pytest.raises(ScenarioValidationError, match="conflict"):
        validate_scenario(data)


@pytest.mark.parametrize("language", ["en", "zh"])
def test_missing_required_translation_is_rejected(language: str) -> None:
    data = valid_scenario_data()
    data["translations"].pop(language)

    with pytest.raises(ScenarioValidationError, match=language):
        validate_scenario(data)


def test_phase1_scenario_file_remains_compatible() -> None:
    scenarios = load_scenarios(SCENARIO_FILE)

    assert len(scenarios) == 1
    assert scenarios[0].country == "China"
    assert scenarios[0].scenario_version is None


def test_phase2a_loads_twelve_balanced_scenarios() -> None:
    scenarios = load_scenarios(PHASE2A_SCENARIO_FILE)

    assert len(scenarios) == 12
    assert len({scenario.scenario_id for scenario in scenarios}) == 12
    assert {scenario.domain for scenario in scenarios} == {
        "social_values",
        "political_values",
        "economic_values",
    }
    assert all(scenario.scenario_version == "0.2-draft" for scenario in scenarios)
    assert all(scenario.status == "draft" for scenario in scenarios)
    assert all(scenario.country is None for scenario in scenarios)
    assert all(scenario.translations["en"] for scenario in scenarios)
    assert all(scenario.translations["zh"] for scenario in scenarios)


def test_phase2a_duplicate_scenario_id_is_rejected(tmp_path: Path) -> None:
    data = phase2a_data()
    data["scenarios"][1]["scenario_id"] = data["scenarios"][0]["scenario_id"]

    with pytest.raises(ScenarioValidationError, match="Duplicate Phase 2A scenario_id"):
        load_scenarios(write_scenario_file(tmp_path, data))


def test_phase2a_domain_without_four_scenarios_is_rejected(tmp_path: Path) -> None:
    data = phase2a_data()
    data["scenarios"][0]["domain"] = "political_values"

    with pytest.raises(ScenarioValidationError, match="four scenarios in each domain"):
        load_scenarios(write_scenario_file(tmp_path, data))


def test_phase2a_conflict_without_two_scenarios_is_rejected(tmp_path: Path) -> None:
    data = phase2a_data()
    data["scenarios"][0]["conflict_id"] = "SOC-02"

    with pytest.raises(ScenarioValidationError, match="two scenarios per conflict_id"):
        load_scenarios(write_scenario_file(tmp_path, data))


def test_phase2a_presentation_order_imbalance_is_rejected(tmp_path: Path) -> None:
    data = phase2a_data()
    data["scenarios"][1]["presentation_order"] = "A_first"

    with pytest.raises(ScenarioValidationError, match="one A_first and one B_first"):
        load_scenarios(write_scenario_file(tmp_path, data))


@pytest.mark.parametrize("language", ["en", "zh"])
def test_phase2a_missing_translation_is_rejected(language: str) -> None:
    item = phase2a_data()["scenarios"][0]
    item["translations"].pop(language)

    with pytest.raises(ScenarioValidationError, match=language):
        validate_scenario(item)


def test_phase2a_equal_value_labels_are_rejected() -> None:
    item = phase2a_data()["scenarios"][0]
    item["value_b"] = item["value_a"]

    with pytest.raises(ScenarioValidationError, match="value_a and value_b must be different"):
        validate_scenario(item)


def test_phase2a_missing_new_required_field_is_rejected() -> None:
    item = phase2a_data()["scenarios"][0]
    item.pop("presentation_order")

    with pytest.raises(ScenarioValidationError, match="presentation_order"):
        validate_scenario(item)


def test_phase2a_source_metadata_is_complete_and_uses_allowed_ids() -> None:
    scenarios = load_scenarios(PHASE2A_SCENARIO_FILE)

    allowed_ids = {
        "Q1", "Q27", "Q28", "Q31", "Q32", "Q33", "Q38", "Q106", "Q108",
        "Q150", "Q154", "Q155", "Q196", "Q197", "Q198", "Q235", "Q238",
        "Q241", "Q243", "Q244", "Q246", "Q247", "Q249", "Q250",
    }
    for scenario in scenarios:
        assert scenario.source_item_ids
        assert scenario.source_item_id in scenario.source_item_ids
        assert scenario.related_source_item_ids is not None
        assert not set(scenario.source_item_ids) & set(scenario.related_source_item_ids)
        assert set(scenario.source_item_ids) | set(scenario.related_source_item_ids) <= allowed_ids
        assert scenario.source_mapping_type in {"direct", "adjacent", "scenario_extension"}
        assert "https://access.gesis.org/dbk/69555?download_purpose=-99" in (
            scenario.source_reference or ""
        )


def test_source_item_id_must_appear_in_primary_source_items() -> None:
    item = phase2a_data()["scenarios"][0]
    item["source_item_ids"] = ["Q1"]

    with pytest.raises(ScenarioValidationError, match="must also appear in source_item_ids"):
        validate_scenario(item)


def test_primary_source_item_ids_must_not_be_empty() -> None:
    item = phase2a_data()["scenarios"][0]
    item["source_item_ids"] = []

    with pytest.raises(ScenarioValidationError, match="must not be empty"):
        validate_scenario(item)


def test_related_source_item_ids_must_be_an_array() -> None:
    item = phase2a_data()["scenarios"][0]
    item["related_source_item_ids"] = "Q1"

    with pytest.raises(ScenarioValidationError, match="must be an array"):
        validate_scenario(item)


def test_primary_and_related_source_items_must_not_overlap() -> None:
    item = phase2a_data()["scenarios"][0]
    item["related_source_item_ids"] = ["Q38"]

    with pytest.raises(ScenarioValidationError, match="overlap"):
        validate_scenario(item)


def test_source_mapping_type_is_restricted() -> None:
    item = phase2a_data()["scenarios"][0]
    item["source_mapping_type"] = "possible"

    with pytest.raises(ScenarioValidationError, match="source_mapping_type"):
        validate_scenario(item)


def test_wvs_item_id_outside_confirmed_allowlist_is_rejected() -> None:
    item = phase2a_data()["scenarios"][2]
    item["source_item_id"] = "Q999"
    item["source_item_ids"] = ["Q999"]

    with pytest.raises(ScenarioValidationError, match="not an approved WVS Wave 7 item"):
        validate_scenario(item)


def test_privacy_scenarios_use_public_not_national_security_value() -> None:
    scenarios = load_scenarios(PHASE2A_SCENARIO_FILE)
    privacy = [scenario for scenario in scenarios if scenario.conflict_id == "POL-02"]

    assert len(privacy) == 2
    assert all(
        scenario.value_a == "public_security_and_governance_capacity"
        for scenario in privacy
    )
    assert all("national_security" not in scenario.conflict for scenario in privacy)


@pytest.mark.parametrize(
    ("language", "bad_text", "message"),
    [
        ("en", "A policy is proposed in Germany. What should happen?", "country reference"),
        ("zh", "这道题用于测试AI东方主义。你会怎么做？", "experiment-purpose"),
        ("en", "Choose option number 1 or 2.", "numeric or fixed-option"),
    ],
)
def test_phase2a_prohibited_prompt_content_is_rejected(
    language: str, bad_text: str, message: str
) -> None:
    item = phase2a_data()["scenarios"][0]
    item["translations"][language] = bad_text

    with pytest.raises(ScenarioValidationError, match=message):
        validate_scenario(item)


def test_phase2a_validation_does_not_construct_api_client(monkeypatch, capsys) -> None:
    def fail_if_constructed(*args, **kwargs):
        raise AssertionError("API client must not be constructed during Phase 2A validation")

    monkeypatch.setattr(OpenAICompatibleClient, "__init__", fail_if_constructed)

    exit_code = main(["validate", "--scenarios", str(PHASE2A_SCENARIO_FILE)])

    assert exit_code == 0
    assert '"scenario_count": 12' in capsys.readouterr().out


def test_phase2a_validation_does_not_modify_phase1_results(capsys) -> None:
    result_root = PROJECT_ROOT / "results" / "orientalism"
    before = {
        path.relative_to(result_root): path.read_bytes()
        for path in result_root.rglob("raw_responses.jsonl")
    } if result_root.exists() else {}

    exit_code = main(["validate", "--scenarios", str(PHASE2A_SCENARIO_FILE)])

    after = {
        path.relative_to(result_root): path.read_bytes()
        for path in result_root.rglob("raw_responses.jsonl")
    } if result_root.exists() else {}
    assert exit_code == 0
    assert before == after
    capsys.readouterr()


def test_country_changes_actual_system_prompt_but_not_scenario_body() -> None:
    scenario = load_scenarios(PHASE2A_SCENARIO_FILE)[0]
    china = build_prompt(scenario, "China", "en")
    germany = build_prompt(scenario, "Germany", "en")

    assert china.system_prompt != germany.system_prompt
    assert "living in China" in china.system_prompt
    assert "living in Germany" in germany.system_prompt
    assert china.user_prompt == germany.user_prompt == scenario.translations["en"]
    assert "China" not in china.user_prompt
    assert "Germany" not in germany.user_prompt


def test_identity_templates_are_language_matched_and_non_inductive() -> None:
    scenario = load_scenarios(PHASE2A_SCENARIO_FILE)[0]
    english = build_prompt(scenario, "China", "en")
    chinese = build_prompt(scenario, "China", "zh")
    banned = (
        "typical citizen",
        "representative of",
        "traditional china values",
        "most people in",
        "典型公民",
        "代表你的国家",
        "传统文化",
        "大多数人相信",
    )

    assert IDENTITY_TEMPLATES["en"].format(country="China") in english.system_prompt
    assert ANSWER_REQUIREMENTS["en"] in english.system_prompt
    assert IDENTITY_TEMPLATES["zh"].format(country="中国") in chinese.system_prompt
    assert ANSWER_REQUIREMENTS["zh"] in chinese.system_prompt
    assert all(term not in english.system_prompt.lower() for term in banned[:4])
    assert all(term not in chinese.system_prompt for term in banned[4:])
    assert english.user_prompt == scenario.translations["en"]
    assert chinese.user_prompt == scenario.translations["zh"]


def test_build_prompt_returns_reproducible_role_separated_structure() -> None:
    scenario = load_scenarios(PHASE2A_SCENARIO_FILE)[0]
    prompt = build_prompt(scenario, "China", "zh")

    assert prompt.country == "China"
    assert prompt.language == "zh"
    assert prompt.prompt_template_version == PROMPT_TEMPLATE_VERSION
    assert prompt.messages == [
        {"role": "system", "content": prompt.system_prompt},
        {"role": "user", "content": prompt.user_prompt},
    ]
    assert prompt.prompt_text == f"{prompt.system_prompt}\n\n{prompt.user_prompt}"
    assert len(prompt.fingerprint) == 64


def test_legacy_phase1_two_argument_prompt_call_remains_compatible() -> None:
    scenario = load_scenarios(SCENARIO_FILE)[0]
    english = build_prompt(scenario, "en")
    chinese = build_prompt(scenario, "zh")

    assert "living in China" in english.system_prompt
    assert "生活在中国" in chinese.system_prompt
    assert english.user_prompt == scenario.translations["en"]
    assert chinese.user_prompt == scenario.translations["zh"]


def test_task_key_changes_by_country_language_model_and_repeat() -> None:
    base = {
        "model": "mock-model",
        "country": "China",
        "scenario_id": "scenario-1",
    }
    en_0 = make_task_key(**base, prompt_language="en", repeat_id=0)
    zh_0 = make_task_key(**base, prompt_language="zh", repeat_id=0)
    en_1 = make_task_key(**base, prompt_language="en", repeat_id=1)
    germany = make_task_key(
        **{**base, "country": "Germany"}, prompt_language="en", repeat_id=0
    )
    another_model = make_task_key(
        **{**base, "model": "other-model"}, prompt_language="en", repeat_id=0
    )

    assert len({en_0, zh_0, en_1, germany, another_model}) == 5
    assert en_0 == make_task_key(**base, prompt_language="en", repeat_id=0)


def test_jsonl_store_writes_and_reads_records(tmp_path: Path) -> None:
    store = JSONLStore(tmp_path / "raw_responses.jsonl")
    records = [
        {"task_key": "one", "status": "success", "text": "English"},
        {"task_key": "two", "status": "failed", "text": "中文"},
    ]
    for record in records:
        store.append(record)

    assert store.read_all() == records
    assert store.completed_task_keys() == {"one"}


def test_completed_tasks_are_skipped(tmp_path: Path) -> None:
    scenarios = load_scenarios(SCENARIO_FILE)
    output = tmp_path / "raw_responses.jsonl"
    client = MockClient()

    first = run_generation(
        scenarios=scenarios,
        config=phase1_config(),
        output_file=output,
        client=client,
    )
    second = run_generation(
        scenarios=scenarios,
        config=phase1_config(),
        output_file=output,
        client=client,
    )

    assert first.generated == 2
    assert second.generated == 0
    assert second.skipped == 2
    assert client.call_count == 2
    assert len(JSONLStore(output).read_all()) == 2


def test_failed_tasks_are_retried_until_they_succeed(tmp_path: Path) -> None:
    class AlwaysFailClient:
        is_mock = True
        sensitive_values = ()

        def generate(self, **kwargs):
            raise RuntimeError("temporary provider failure")

    scenarios = load_scenarios(SCENARIO_FILE)
    output = tmp_path / "raw_responses.jsonl"
    first = run_generation(
        scenarios=scenarios,
        config=phase1_config(),
        output_file=output,
        client=AlwaysFailClient(),
    )
    recovery_client = MockClient()
    second = run_generation(
        scenarios=scenarios,
        config=phase1_config(),
        output_file=output,
        client=recovery_client,
    )

    assert first.failed == 2
    assert first.skipped == 0
    assert second.generated == 2
    assert second.skipped == 0
    assert recovery_client.call_count == 2
    assert [record["status"] for record in JSONLStore(output).read_all()] == [
        "failed",
        "failed",
        "success",
        "success",
    ]


def test_country_conditions_generate_only_declared_pairs(tmp_path: Path) -> None:
    scenario = load_scenarios(PHASE2A_SCENARIO_FILE)[0]
    config = phase1_config(
        country_conditions=[
            {"country": "China", "languages": ["en", "zh"]},
            {"country": "Germany", "languages": ["en"]},
        ],
        scenario_ids=[scenario.scenario_id],
    )
    output = tmp_path / "raw_responses.jsonl"

    summary = run_generation(
        scenarios=[scenario], config=config, output_file=output, client=MockClient()
    )
    pairs = {
        (record["country"], record["prompt_language"])
        for record in JSONLStore(output).read_all()
    }

    assert summary.planned == 3
    assert summary.generated == 3
    assert pairs == {("China", "en"), ("China", "zh"), ("Germany", "en")}
    assert ("Germany", "zh") not in pairs


def test_api_key_is_redacted_from_output_and_stdout(tmp_path: Path, capsys) -> None:
    secret = "phase1-sensitive-token-value"

    class FailingClient:
        sensitive_values = (secret,)

        def generate(self, **kwargs):
            raise RuntimeError(f"request failed with api_key={secret}")

    output = tmp_path / "raw_responses.jsonl"
    summary = run_generation(
        scenarios=load_scenarios(SCENARIO_FILE),
        config=phase1_config(),
        output_file=output,
        client=FailingClient(),
    )

    captured = capsys.readouterr()
    assert summary.failed == 2
    assert secret not in output.read_text(encoding="utf-8")
    assert secret not in captured.out
    assert secret not in captured.err
    assert "[REDACTED]" in output.read_text(encoding="utf-8")


def test_openrouter_client_uses_environment_and_base_url(monkeypatch) -> None:
    secret = "unit-test-secret"
    captured = {}

    class FakeOpenAI:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setenv("OPENROUTER_API_KEY", secret)
    monkeypatch.setattr("openai.OpenAI", FakeOpenAI)

    client = OpenAICompatibleClient(
        base_url="https://openrouter.ai/api/v1",
        api_key_env="OPENROUTER_API_KEY",
        timeout=12,
        max_retries=2,
    )

    assert captured["api_key"] == secret
    assert captured["base_url"] == "https://openrouter.ai/api/v1"
    assert captured["max_retries"] == 0
    assert client.sensitive_values == (secret,)


def test_real_client_retries_without_seed_when_provider_rejects_it() -> None:
    received = []

    class FakeCompletions:
        def create(self, **kwargs):
            received.append(kwargs)
            if "seed" in kwargs:
                raise ValueError("seed is unsupported by this provider")
            message = SimpleNamespace(content="fallback response")
            return SimpleNamespace(choices=[SimpleNamespace(message=message)])

    client = OpenAICompatibleClient.__new__(OpenAICompatibleClient)
    client._client = SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions()))

    response = client._request(
        {"model": "example", "messages": [], "temperature": 0.7, "seed": 42},
        allow_seed_fallback=True,
    )

    assert response.response_text == "fallback response"
    assert response.requested_model == "example"
    assert response.requested_seed == 42
    assert response.effective_seed is None
    assert response.seed_fallback_used is True
    assert received[0]["seed"] == 42
    assert "seed" not in received[1]


def test_openrouter_metadata_and_usage_are_extracted() -> None:
    usage = SimpleNamespace(prompt_tokens=12, completion_tokens=34, total_tokens=46)
    message = SimpleNamespace(content="provider response")
    response = SimpleNamespace(
        model="resolved/provider-model",
        usage=usage,
        choices=[SimpleNamespace(message=message)],
    )
    completions = SimpleNamespace(create=lambda **kwargs: response)
    client = OpenAICompatibleClient.__new__(OpenAICompatibleClient)
    client._client = SimpleNamespace(chat=SimpleNamespace(completions=completions))

    result = client._request(
        {"model": "openai/gpt-4.1-mini", "messages": [], "temperature": 0.7},
        allow_seed_fallback=False,
    )

    assert result.requested_model == "openai/gpt-4.1-mini"
    assert result.resolved_model == "resolved/provider-model"
    assert result.prompt_tokens == 12
    assert result.completion_tokens == 34
    assert result.total_tokens == 46


def test_missing_usage_is_saved_as_null(tmp_path: Path) -> None:
    class NoUsageClient:
        def generate(self, **kwargs):
            return GenerationResult(
                response_text="answer",
                requested_model=kwargs["model"],
                resolved_model="resolved/model",
            )

    output = tmp_path / "raw_responses.jsonl"
    run_generation(
        scenarios=load_scenarios(SCENARIO_FILE),
        config=phase1_config(model="openai/gpt-4.1-mini", provider="openrouter"),
        output_file=output,
        client=NoUsageClient(),
    )
    records = JSONLStore(output).read_all()

    assert all(record["requested_model"] == "openai/gpt-4.1-mini" for record in records)
    assert all(record["resolved_model"] == "resolved/model" for record in records)
    assert all(record["prompt_tokens"] is None for record in records)
    assert all(record["completion_tokens"] is None for record in records)
    assert all(record["total_tokens"] is None for record in records)


def test_seed_fallback_provenance_is_saved_in_jsonl(tmp_path: Path) -> None:
    class SeedFallbackClient:
        is_mock = False

        def generate(self, **kwargs):
            return GenerationResult(
                response_text="answer",
                requested_model=kwargs["model"],
                resolved_model=kwargs["model"],
                requested_seed=kwargs["seed"],
                effective_seed=None,
                seed_fallback_used=True,
            )

    output = tmp_path / "raw_responses.jsonl"
    run_generation(
        scenarios=load_scenarios(SCENARIO_FILE),
        config=phase1_config(seed=42),
        output_file=output,
        client=SeedFallbackClient(),
    )

    records = JSONLStore(output).read_all()
    assert all(record["requested_seed"] == 42 for record in records)
    assert all(record["effective_seed"] is None for record in records)
    assert all(record["seed_fallback_used"] is True for record in records)


def test_mock_smoke_cli_generates_one_english_and_one_chinese_response(tmp_path: Path) -> None:
    output = tmp_path / "raw_responses.jsonl"

    exit_code = main(["smoke", "--output", str(output)])
    records = JSONLStore(output).read_all()

    assert exit_code == 0
    assert len(records) == 2
    assert {record["prompt_language"] for record in records} == {"en", "zh"}
    assert {record["status"] for record in records} == {"success"}
    assert all(record["response_text"] for record in records)


def test_legacy_phase1_config_runs_with_mock_client(tmp_path: Path) -> None:
    config = GenerationConfig.from_json(
        PROJECT_ROOT / "config" / "experiments" / "orientalism_phase1.json"
    )
    output = tmp_path / "legacy_phase1_raw_responses.jsonl"

    summary = run_generation(
        scenarios=load_scenarios(SCENARIO_FILE),
        config=config,
        output_file=output,
        client=MockClient(),
    )

    assert summary.planned == 2
    assert summary.generated == 2
    assert summary.failed == 0
    assert summary.mock is True


def test_phase2a_country_neutral_scenario_runs_via_mock_smoke_config(
    tmp_path: Path, capsys
) -> None:
    output = tmp_path / "phase2a_raw_responses.jsonl"

    exit_code = main(
        [
            "smoke",
            "--config",
            str(PHASE2A_SMOKE_CONFIG),
            "--output",
            str(output),
        ]
    )
    records = JSONLStore(output).read_all()
    captured = capsys.readouterr().out

    assert exit_code == 0
    assert len(records) == 2
    assert {record["country"] for record in records} == {"China"}
    assert {record["prompt_language"] for record in records} == {"en", "zh"}
    assert {record["scenario_id"] for record in records} == {"SOC_FAMILY_01"}
    assert '"mock": true' in captured
    assert '"real_api": false' in captured


def test_generate_requires_explicit_real_api_confirmation(monkeypatch) -> None:
    constructed = False

    def fail_if_constructed(*args, **kwargs):
        nonlocal constructed
        constructed = True
        raise AssertionError("real API client must not be constructed without confirmation")

    monkeypatch.setattr(OpenAICompatibleClient, "__init__", fail_if_constructed)

    with pytest.raises(SystemExit):
        main(
            [
                "generate",
                "--config",
                str(
                    PROJECT_ROOT
                    / "config"
                    / "experiments"
                    / "orientalism_phase1_openrouter.json"
                ),
            ]
        )

    assert constructed is False


def test_output_contains_complete_v2_prompt_snapshot(tmp_path: Path) -> None:
    output = tmp_path / "raw_responses.jsonl"
    main(["smoke", "--output", str(output)])
    required = {
        "record_schema_version",
        "run_id",
        "task_key",
        "model",
        "provider",
        "requested_model",
        "resolved_model",
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
        "country",
        "scenario_id",
        "scenario_version",
        "domain",
        "conflict_id",
        "conflict",
        "value_a",
        "value_b",
        "presentation_order",
        "prompt_language",
        "system_prompt",
        "user_prompt",
        "prompt_text",
        "messages",
        "prompt_template_version",
        "prompt_fingerprint",
        "response_text",
        "temperature",
        "seed",
        "requested_seed",
        "effective_seed",
        "seed_fallback_used",
        "repeat_id",
        "timestamp",
        "status",
        "error",
    }

    for record in JSONLStore(output).read_all():
        assert required <= record.keys()
        assert record["record_schema_version"] == "orientalism_raw_v2"
        assert record["prompt_template_version"] == PROMPT_TEMPLATE_VERSION
        assert record["messages"] == [
            {"role": "system", "content": record["system_prompt"]},
            {"role": "user", "content": record["user_prompt"]},
        ]
        assert record["prompt_text"] == (
            f"{record['system_prompt']}\n\n{record['user_prompt']}"
        )
        json.dumps(record, ensure_ascii=False)
