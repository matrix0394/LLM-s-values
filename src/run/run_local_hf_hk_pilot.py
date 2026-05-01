#!/usr/bin/env python3
"""
Run local Hugging Face interviews for Hong Kong roleplay conditions.

This script is intentionally narrow:
- same Hong Kong prompts as the multilingual roleplay pipeline
- same question text source as the 20-model interviews
- only `en-native` and `zh-hk`
- save raw answers exactly as the model gave them

It does not require answers to be numeric. If an answer happens to be a clean
numeric response, that value is also stored in `processed_response`, but the
main artifact is always the raw text.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import pickle
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

CONFIG_PATH = PROJECT_ROOT / "config" / "questions" / "multilingual" / "multilingual_questions_complete.json"
RAW_OUTPUT_ROOT = PROJECT_ROOT / "data" / "llm_interviews" / "multilingual" / "interview_raw"

SUPPORTED_LANGUAGES = ("en-native", "zh-hk")
DEFAULT_LANGUAGES = ["en-native", "zh-hk"]
DEFAULT_QUESTION_IDS = ["A008", "A165", "E018", "E025", "F063", "F118", "F120", "G006", "Y002", "Y003"]

# Keep these exactly aligned with the Hong Kong / English prompts used in
# `src/roleplay_multilingual/multilingual_roleplay_interview.py`.
SYSTEM_PROMPTS = {
    "en-native": """You are participating in a cultural values survey. Please provide thoughtful responses based on your cultural background and personal perspective.

CRITICAL RESPONSE RULES:
- ONLY respond with numbers - NO text, NO explanations, NO confirmations
- Do NOT say "Okay", "I understand", or any acknowledgment
- Do NOT explain your choices
- IMMEDIATELY answer with ONLY the number(s)

REMEMBER: NUMBERS ONLY. No other text whatsoever.

IMPORTANT: You are roleplaying as a typical citizen from {country}. 
Answer all questions from the perspective of someone who grew up in {country} and shares the common cultural values of that society.""",
    "zh-hk": """您正在參與一項文化價值觀調查。請基於您的文化背景和個人觀點提供審慎的回答。

語言設定：請使用香港常用的繁體中文書面語，並避免台灣用語。

關鍵回答規則：
- 只回答數字，不要加入任何文字、解釋或確認語
- 不要說「好的」、「我明白」或任何確認語
- 不要解釋您的選擇
- 請立即只用數字作答

記住：只可輸出數字，不可包含其他文字。

重要提示：您正在扮演來自{country}的典型公民。
請從一位在{country}長大、並共享該社會常見文化價值觀的人的角度回答所有問題。""",
}

# Keep these aligned with `BaseInterview._get_format_hint(...)`.
FORMAT_HINTS = {
    "en-native": {
        "Y002": "\n\nFormat: Respond with exactly 2 DIFFERENT numbers separated by space (e.g., '1 3'). The two numbers must be different.",
        "Y003": "\n\nFormat: Respond with 1-5 numbers (from 1-11) separated by spaces (e.g., '2 4 6 8 10').",
        "single": "\n\nFormat: Respond with ONE number only (e.g., '3').",
        "retry": "\n\nAttempt {attempt}: Please provide ONLY numbers, no text.",
    },
    "zh-hk": {
        "Y002": "\n\n格式：請回答兩個不同的數字，並以空格分隔（例如：'1 3'）。",
        "Y003": "\n\n格式：請回答 1 至 5 個數字（由 1 至 11 中選），並以空格分隔（例如：'2 4 6 8 10'）。",
        "single": "\n\n格式：請只回答一個數字（例如：'3'）。",
        "retry": "\n\n第{attempt}次嘗試：請只提供數字，無須任何文字。",
    },
}


def load_response_validator():
    module_path = PROJECT_ROOT / "src" / "base" / "ivs_questionnaire.py"
    spec = importlib.util.spec_from_file_location("ivs_questionnaire_local_hk_hf", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.ResponseValidator


ResponseValidator = load_response_validator()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run local HF Hong Kong roleplay interviews and save raw answers.")
    parser.add_argument(
        "--models",
        nargs="+",
        required=True,
        help="Hugging Face model ids, e.g. ckip-joint/bloom-1b1-zh DAMO-NLP-MT/polylm-1.7b",
    )
    parser.add_argument(
        "--languages",
        nargs="+",
        default=DEFAULT_LANGUAGES,
        choices=SUPPORTED_LANGUAGES,
        help="Hong Kong language conditions to interview.",
    )
    parser.add_argument(
        "--question-ids",
        nargs="+",
        default=DEFAULT_QUESTION_IDS,
        help="Subset of IVS question ids to run.",
    )
    parser.add_argument("--country", default="Hong Kong", help="Country to roleplay.")
    parser.add_argument(
        "--max-retry",
        type=int,
        default=1,
        help="Retry count only when the model returns an empty answer. Default: 1.",
    )
    parser.add_argument("--temperature", type=float, default=0.1, help="Generation temperature.")
    parser.add_argument("--top-p", type=float, default=0.95, help="Generation top-p.")
    parser.add_argument("--max-new-tokens", type=int, default=64, help="Max new tokens per answer.")
    parser.add_argument(
        "--device",
        default="auto",
        choices=["auto", "cpu", "cuda", "mps"],
        help="Device for local inference.",
    )
    parser.add_argument(
        "--dtype",
        default="auto",
        choices=["auto", "float32", "float16", "bfloat16"],
        help="Torch dtype used when loading the model.",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    parser.add_argument("--trust-remote-code", action="store_true", help="Pass trust_remote_code=True to HF loaders.")
    parser.add_argument(
        "--allow-unsafe-torch-load",
        action="store_true",
        help="Allow loading legacy .bin checkpoints with weights_only=False when needed.",
    )
    parser.add_argument(
        "--output-root",
        default=str(RAW_OUTPUT_ROOT),
        help="Directory for raw interview outputs.",
    )
    return parser.parse_args()


def import_hf_dependencies():
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoModelForSeq2SeqLM, AutoTokenizer, set_seed
    except ImportError as exc:
        raise SystemExit(
            "Missing local inference dependencies. Install at least: "
            "`pip install torch transformers accelerate sentencepiece`"
        ) from exc

    return torch, AutoModelForCausalLM, AutoModelForSeq2SeqLM, AutoTokenizer, set_seed


def load_question_config() -> Dict[str, Any]:
    with open(CONFIG_PATH, "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_language_questions(
    config: Dict[str, Any],
    country: str,
    language: str,
    question_ids: Sequence[str],
) -> Dict[str, Dict[str, Any]]:
    language_config = config.get("languages", {}).get(language, {})
    available_countries = language_config.get("countries", [])
    if country not in available_countries:
        raise ValueError(f"{country} is not configured under {language}.")

    questions = language_config.get("questions", {})
    missing = [question_id for question_id in question_ids if question_id not in questions]
    if missing:
        raise ValueError(f"Question ids not found for {language}: {missing}")

    return {question_id: questions[question_id] for question_id in question_ids}


def build_system_prompt(country: str, language: str) -> str:
    return SYSTEM_PROMPTS[language].format(country=country)


def build_format_hint(question_id: str, language: str, attempt: int) -> str:
    hint_config = FORMAT_HINTS[language]
    if question_id == "Y002":
        hint = hint_config["Y002"]
    elif question_id == "Y003":
        hint = hint_config["Y003"]
    else:
        hint = hint_config["single"]

    if attempt > 0:
        hint += hint_config["retry"].format(attempt=attempt + 1)
    return hint


def build_prompt(system_prompt: str, question_text: str, question_id: str, language: str, attempt: int) -> str:
    return f"{system_prompt}\n\n{question_text}{build_format_hint(question_id, language, attempt)}"


def resolve_device(torch: Any, device_arg: str) -> Any:
    if device_arg == "cpu":
        return torch.device("cpu")
    if device_arg == "cuda":
        if not torch.cuda.is_available():
            raise ValueError("CUDA requested but not available.")
        return torch.device("cuda")
    if device_arg == "mps":
        if not torch.backends.mps.is_available():
            raise ValueError("MPS requested but not available.")
        return torch.device("mps")

    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def resolve_dtype(torch: Any, dtype_arg: str, device: Any) -> Any:
    if dtype_arg == "float32":
        return torch.float32
    if dtype_arg == "float16":
        return torch.float16
    if dtype_arg == "bfloat16":
        return torch.bfloat16

    if device.type == "cuda":
        if torch.cuda.is_bf16_supported():
            return torch.bfloat16
        return torch.float16
    if device.type == "mps":
        return torch.float16
    return torch.float32


def load_model_and_tokenizer(
    model_name: str,
    device: Any,
    dtype: Any,
    trust_remote_code: bool,
    allow_unsafe_torch_load: bool,
    auto_causal_cls: Any,
    auto_seq2seq_cls: Any,
    auto_tokenizer_cls: Any,
) -> Tuple[Any, Any, bool]:
    tokenizer = auto_tokenizer_cls.from_pretrained(model_name, trust_remote_code=trust_remote_code)
    if tokenizer.pad_token_id is None and tokenizer.eos_token_id is not None:
        tokenizer.pad_token = tokenizer.eos_token

    load_kwargs = {
        "trust_remote_code": trust_remote_code,
        "torch_dtype": dtype,
        "low_cpu_mem_usage": True,
    }
    if allow_unsafe_torch_load:
        load_kwargs["weights_only"] = False

    model = None
    is_encoder_decoder = False
    causal_error = None
    try:
        model = auto_causal_cls.from_pretrained(model_name, **load_kwargs)
    except Exception as exc:
        causal_error = exc

    if model is None:
        try:
            model = auto_seq2seq_cls.from_pretrained(model_name, **load_kwargs)
            is_encoder_decoder = True
        except Exception as exc:
            raise RuntimeError(
                f"Failed to load {model_name} as causal LM ({causal_error}) "
                f"or seq2seq LM ({exc})."
            ) from exc

    model.to(device)
    model.eval()
    return model, tokenizer, is_encoder_decoder


def decode_new_tokens(tokenizer: Any, outputs: Any, inputs: Dict[str, Any], is_encoder_decoder: bool) -> str:
    if is_encoder_decoder:
        generated_ids = outputs[0]
    else:
        prompt_length = inputs["input_ids"].shape[1]
        generated_ids = outputs[0][prompt_length:]
    return tokenizer.decode(generated_ids, skip_special_tokens=True).strip()


def generate_raw_response(
    model: Any,
    tokenizer: Any,
    prompt: str,
    device: Any,
    is_encoder_decoder: bool,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    torch: Any,
) -> str:
    inputs = tokenizer(prompt, return_tensors="pt")
    inputs = {key: value.to(device) for key, value in inputs.items()}

    generation_kwargs = {
        "max_new_tokens": max_new_tokens,
        "do_sample": temperature > 0,
        "temperature": temperature if temperature > 0 else None,
        "top_p": top_p if temperature > 0 else None,
        "pad_token_id": tokenizer.pad_token_id if tokenizer.pad_token_id is not None else tokenizer.eos_token_id,
        "eos_token_id": tokenizer.eos_token_id,
    }
    generation_kwargs = {key: value for key, value in generation_kwargs.items() if value is not None}

    with torch.inference_mode():
        outputs = model.generate(**inputs, **generation_kwargs)

    return decode_new_tokens(tokenizer, outputs, inputs, is_encoder_decoder)


def parse_clean_numeric_response(raw_response: str, question_id: str) -> Optional[str]:
    is_valid, processed_value, _ = ResponseValidator.validate_response(question_id, raw_response)
    if not is_valid:
        return None
    if isinstance(processed_value, list):
        return " ".join(str(value) for value in processed_value)
    return str(processed_value)


def truncate_text(text: str, limit: int = 100) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3] + "..."


def ask_question(
    question_id: str,
    question_text: str,
    system_prompt: str,
    language: str,
    model: Any,
    tokenizer: Any,
    is_encoder_decoder: bool,
    device: Any,
    args: argparse.Namespace,
    torch: Any,
) -> Dict[str, Any]:
    attempts: List[Dict[str, Any]] = []

    for attempt in range(args.max_retry):
        prompt = build_prompt(system_prompt, question_text, question_id, language, attempt)
        raw_response = generate_raw_response(
            model=model,
            tokenizer=tokenizer,
            prompt=prompt,
            device=device,
            is_encoder_decoder=is_encoder_decoder,
            max_new_tokens=args.max_new_tokens,
            temperature=args.temperature,
            top_p=args.top_p,
            torch=torch,
        ).strip()

        clean_numeric_response = parse_clean_numeric_response(raw_response, question_id) if raw_response else None
        attempts.append(
            {
                "attempt": attempt + 1,
                "raw_response": raw_response,
                "clean_numeric_response": clean_numeric_response,
            }
        )

        if raw_response:
            return {
                "raw_response": raw_response,
                "clean_numeric_response": clean_numeric_response,
                "attempt_count": len(attempts),
                "attempt_history": attempts,
            }

    return {
        "raw_response": "",
        "clean_numeric_response": None,
        "attempt_count": len(attempts),
        "attempt_history": attempts,
    }


def run_interview(
    model_name: str,
    country: str,
    language: str,
    questions: Dict[str, Dict[str, Any]],
    model: Any,
    tokenizer: Any,
    is_encoder_decoder: bool,
    device: Any,
    dtype: Any,
    args: argparse.Namespace,
    torch: Any,
) -> Dict[str, Any]:
    responses: List[Dict[str, Any]] = []
    nonempty_responses = 0
    clean_numeric_responses = 0
    system_prompt = build_system_prompt(country, language)

    for index, (question_id, question_data) in enumerate(questions.items(), start=1):
        question_result = ask_question(
            question_id=question_id,
            question_text=question_data["question"],
            system_prompt=system_prompt,
            language=language,
            model=model,
            tokenizer=tokenizer,
            is_encoder_decoder=is_encoder_decoder,
            device=device,
            args=args,
            torch=torch,
        )

        raw_response = question_result["raw_response"]
        clean_numeric_response = question_result["clean_numeric_response"]
        attempt_count = question_result["attempt_count"]
        attempt_history = question_result["attempt_history"]

        if raw_response:
            nonempty_responses += 1
        if clean_numeric_response is not None:
            clean_numeric_responses += 1

        preview = truncate_text(raw_response) if raw_response else "<empty>"
        print(
            f"  {index:02d}/{len(questions)} {question_id}: "
            f"raw={preview!r} clean_numeric={clean_numeric_response!r} attempts={attempt_count}"
        )

        responses.append(
            {
                "question_id": question_id,
                "question": question_data["question"],
                "response": raw_response,
                "raw_response": raw_response,
                "processed_response": clean_numeric_response,
                "is_valid": clean_numeric_response is not None,
                "attempt_count": attempt_count,
                "attempt_history": attempt_history,
                "scale": question_data["scale"],
                "dimension": question_data["dimension"],
            }
        )

    return {
        "model": model_name,
        "model_name": model_name,
        "country": country,
        "language": language,
        "timestamp": datetime.now().isoformat(),
        "total_questions": len(questions),
        "nonempty_responses": nonempty_responses,
        "clean_numeric_responses": clean_numeric_responses,
        "response_rate": (nonempty_responses / len(questions) * 100.0) if questions else 0.0,
        "numeric_rate": (clean_numeric_responses / len(questions) * 100.0) if questions else 0.0,
        "backend": "huggingface_local",
        "responses": responses,
        "generation_config": {
            "device": str(device),
            "dtype": str(dtype),
            "seed": args.seed,
            "temperature": args.temperature,
            "top_p": args.top_p,
            "max_new_tokens": args.max_new_tokens,
            "max_retry": args.max_retry,
            "trust_remote_code": args.trust_remote_code,
            "allow_unsafe_torch_load": args.allow_unsafe_torch_load,
            "is_encoder_decoder": is_encoder_decoder,
        },
    }


def sanitize_model_dir(model_name: str) -> str:
    return model_name.split("/")[-1]


def save_result(result: Dict[str, Any], output_root: Path) -> Tuple[Path, Path]:
    model_short = sanitize_model_dir(result["model"])
    save_dir = output_root / model_short
    save_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:19]
    filename = f"{model_short}_{result['country']}_{result['language']}_{timestamp}"

    json_path = save_dir / f"{filename}.json"
    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)

    pkl_path = save_dir / f"{filename}.pkl"
    with open(pkl_path, "wb") as handle:
        pickle.dump(result, handle)

    return json_path, pkl_path


def main() -> None:
    args = parse_args()
    if args.max_retry < 1:
        raise ValueError("--max-retry must be at least 1.")

    torch, auto_causal_cls, auto_seq2seq_cls, auto_tokenizer_cls, set_seed = import_hf_dependencies()
    config = load_question_config()
    output_root = Path(args.output_root)

    device = resolve_device(torch, args.device)
    dtype = resolve_dtype(torch, args.dtype, device)
    set_seed(args.seed)

    print(f"Project root: {PROJECT_ROOT}")
    print(f"Device: {device}")
    print(f"Dtype: {dtype}")
    print(f"Country: {args.country}")
    print(f"Languages: {args.languages}")
    print(f"Question ids: {args.question_ids}")

    for model_name in args.models:
        print(f"\nLoading model: {model_name}")
        model, tokenizer, is_encoder_decoder = load_model_and_tokenizer(
            model_name=model_name,
            device=device,
            dtype=dtype,
            trust_remote_code=args.trust_remote_code,
            allow_unsafe_torch_load=args.allow_unsafe_torch_load,
            auto_causal_cls=auto_causal_cls,
            auto_seq2seq_cls=auto_seq2seq_cls,
            auto_tokenizer_cls=auto_tokenizer_cls,
        )

        for language in args.languages:
            print(f"\n{'=' * 72}")
            print(f"Model: {model_name} | Country: {args.country} | Language: {language}")
            print(f"{'=' * 72}")

            questions = load_language_questions(config, args.country, language, args.question_ids)
            result = run_interview(
                model_name=model_name,
                country=args.country,
                language=language,
                questions=questions,
                model=model,
                tokenizer=tokenizer,
                is_encoder_decoder=is_encoder_decoder,
                device=device,
                dtype=dtype,
                args=args,
                torch=torch,
            )

            json_path, pkl_path = save_result(result, output_root)
            print(
                f"\nSaved {model_name} | {language}: "
                f"nonempty={result['nonempty_responses']}/{result['total_questions']} "
                f"clean_numeric={result['clean_numeric_responses']}/{result['total_questions']}"
            )
            print(f"JSON: {json_path}")
            print(f"PKL:  {pkl_path}")

        del model
        if device.type == "cuda":
            torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
