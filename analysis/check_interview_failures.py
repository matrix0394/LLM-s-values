#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Quick check for interview failures across all stages."""

import sys
import pickle
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

def check_stage1():
    """Check Stage1 LLM values interview data."""
    print("\n" + "="*80)
    print("STAGE 1: LLM Self Values")
    print("="*80)
    
    pkl_path = PROJECT_ROOT / "data" / "llm_values" / "interview_raw" / "llm_interview_raw_latest.pkl"
    if not pkl_path.exists():
        print("File not found!")
        return
    
    with open(pkl_path, 'rb') as f:
        data = pickle.load(f)
    
    results = data.get('results', [])
    print(f"Total models: {len(results)}")
    
    for r in results:
        model = r.get('model_name', '?')
        valid = r.get('valid_responses', 0)
        total = r.get('total_questions', 0)
        rate = r.get('success_rate', 0)
        
        status = "✅" if rate == 100 else "⚠️"
        print(f"  {status} {model}: {valid}/{total} ({rate:.1f}%)")
        
        # Check if there are any invalid responses
        if rate < 100:
            responses = r.get('responses', [])
            for resp in responses:
                if isinstance(resp, dict):
                    is_valid = resp.get('is_valid', False)
                    if not is_valid:
                        print(f"      ❌ {resp.get('question_id')}: {resp.get('error_message')}")


def check_stage2():
    """Check Stage2 English roleplay data."""
    print("\n" + "="*80)
    print("STAGE 2: English Roleplay")
    print("="*80)
    
    pkl_path = PROJECT_ROOT / "data" / "roleplay_English" / "llm_responses_roleplay" / "roleplay_results_20251101_220625.pkl"
    if not pkl_path.exists():
        print("File not found!")
        return
    
    data = None
    try:
        with open(pkl_path, 'rb') as f:
            data = pickle.load(f)
    except (ModuleNotFoundError, AttributeError) as e:
        print(f"⚠️ PKL failed ({e}), trying JSON...")
        json_path = pkl_path.with_suffix('.json')
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            print("No JSON fallback!")
            return
    
    results = data.get('results', []) if isinstance(data, dict) else data
    print(f"Total entries: {len(results)}")
    
    failed_entries = []
    for entry in results:
        model = entry.get('model', '?')
        country = entry.get('country', '?')
        valid = entry.get('valid_responses', 0)
        total = entry.get('total_questions', 0)
        rate = entry.get('success_rate', 0)
        
        if rate < 100:
            failed_entries.append((model, country, valid, total, rate))
    
    if failed_entries:
        print(f"Found {len(failed_entries)} entries with failures:")
        for model, country, valid, total, rate in failed_entries[:20]:  # Show first 20
            print(f"  ⚠️ {model} → {country}: {valid}/{total} ({rate:.1f}%)")
    else:
        print("✅ All entries have 100% success rate!")


def check_stage3():
    """Check Stage3 multilingual roleplay data."""
    print("\n" + "="*80)
    print("STAGE 3: Multilingual Roleplay")
    print("="*80)
    
    pkl_path = PROJECT_ROOT / "data" / "roleplay_multilingual" / "llm_responses_roleplay_ml" / "roleplay_results_ml_latest.pkl"
    if not pkl_path.exists():
        print("File not found!")
        return
    
    data = None
    try:
        with open(pkl_path, 'rb') as f:
            data = pickle.load(f)
    except (ModuleNotFoundError, AttributeError) as e:
        print(f"⚠️ PKL failed ({e}), trying JSON...")
        json_path = pkl_path.with_suffix('.json')
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            print("No JSON fallback!")
            return
    
    results = data.get('results', []) if isinstance(data, dict) else data
    print(f"Total entries: {len(results)}")
    
    # Sample first few entries to check structure
    if results:
        print("\n📋 Sample entry structure:")
        first = results[0]
        print(f"  Keys: {list(first.keys())}")
        print(f"  Model: {first.get('model', '?')}")
        print(f"  Country: {first.get('country', '?')}")
        print(f"  Language: {first.get('language', '?')}")
        print(f"  Valid responses: {first.get('valid_responses', '?')}")
        print(f"  Total questions: {first.get('total_questions', '?')}")
        
        # Check response structure
        responses = first.get('responses', [])
        if responses:
            print(f"\n📋 Sample response structure:")
            r = responses[0]
            if isinstance(r, dict):
                print(f"  Keys: {list(r.keys())}")
                print(f"  Has 'final_response': {'final_response' in r}")
                print(f"  Has 'processed_response': {'processed_response' in r}")
                print(f"  Has 'raw_response': {'raw_response' in r}")
    
    # Count failures
    failed_entries = []
    for entry in results:
        model = entry.get('model', '?')
        country = entry.get('country', '?')
        language = entry.get('language', '?')
        valid = entry.get('valid_responses', 0)
        total = entry.get('total_questions', 0)
        
        if valid < total:
            rate = valid / total * 100 if total > 0 else 0
            failed_entries.append((model, country, language, valid, total, rate))
    
    if failed_entries:
        print(f"\n⚠️ Found {len(failed_entries)} entries with failures:")
        for model, country, lang, valid, total, rate in failed_entries[:20]:
            print(f"  {model} → {country} ({lang}): {valid}/{total} ({rate:.1f}%)")
    else:
        print("\n✅ All entries have 100% success rate!")


if __name__ == "__main__":
    check_stage1()
    check_stage2()
    check_stage3()
    
    print("\n" + "="*80)
    print("✅ ANALYSIS COMPLETE")
    print("="*80)
