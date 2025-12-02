#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Verify that all 'valid' responses actually have valid content."""

import sys
import pickle
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))


def check_stage1_responses():
    """Check if Stage1 valid responses actually have valid content."""
    print("\n" + "="*80)
    print("STAGE 1: Checking Response Content")
    print("="*80)
    
    pkl_path = PROJECT_ROOT / "data" / "llm_values" / "interview_raw" / "llm_interview_raw_latest.pkl"
    with open(pkl_path, 'rb') as f:
        data = pickle.load(f)
    
    results = data.get('results', [])
    
    for r in results:
        model = r.get('model_name', '?')
        responses = r.get('responses', [])
        
        invalid_but_counted = []
        for resp in responses:
            if isinstance(resp, dict):
                is_valid = resp.get('is_valid', False)
                # Check BOTH fields
                response_val = resp.get('response')
                processed_val = resp.get('processed_response')
                qid = resp.get('question_id', '?')
                
                # Check if marked valid but has no actual value
                if is_valid and processed_val is None:
                    invalid_but_counted.append((qid, response_val, processed_val))
        
        if invalid_but_counted:
            print(f"⚠️  {model}: {len(invalid_but_counted)} responses marked valid but have None processed_response:")
            for qid, resp, proc in invalid_but_counted[:3]:  # Show first 3
                print(f"    - {qid}: response={resp}, processed_response={proc}")
        else:
            print(f"✅ {model}: All valid responses have actual values")


def check_stage3_final_responses():
    """Check Stage3 final_response values."""
    print("\n" + "="*80)
    print("STAGE 3: Checking Final Response Content")
    print("="*80)
    
    json_path = PROJECT_ROOT / "data" / "roleplay_multilingual" / "llm_responses_roleplay_ml" / "roleplay_results_ml_latest.json"
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = data.get('results', [])
    
    suspicious_entries = []
    
    for entry in results:
        model = entry.get('model', '?')
        country = entry.get('country', {})
        if isinstance(country, dict):
            country = country.get('name', '?')
        language = entry.get('language', '?')
        
        responses = entry.get('responses', [])
        
        # Check each response
        none_count = 0
        suspicious_responses = []
        
        for r in responses:
            final_resp = r.get('final_response')
            all_resps = r.get('all_responses', [])
            qid = r.get('question_id', '?')
            
            # If final_response is None but counted as valid
            if final_resp is None:
                none_count += 1
            
            # Check if final_response is set but all attempts were None
            if final_resp is not None and all(x is None for x in all_resps):
                suspicious_responses.append({
                    'qid': qid,
                    'final': final_resp,
                    'all': all_resps
                })
        
        if none_count > 0 or suspicious_responses:
            suspicious_entries.append({
                'model': model,
                'country': country,
                'language': language,
                'none_count': none_count,
                'suspicious': suspicious_responses
            })
    
    if suspicious_entries:
        print(f"⚠️  Found {len(suspicious_entries)} suspicious entries:\n")
        for e in suspicious_entries[:10]:  # Show first 10
            print(f"  {e['model']} → {e['country']} ({e['language']})")
            if e['none_count'] > 0:
                print(f"    - {e['none_count']} responses with final_response=None")
            if e['suspicious']:
                print(f"    - {len(e['suspicious'])} responses where final != None but all attempts were None:")
                for s in e['suspicious'][:3]:
                    print(f"      • {s['qid']}: final={s['final']}, all={s['all']}")
            print()
    else:
        print("✅ All entries look correct!")


if __name__ == "__main__":
    check_stage1_responses()
    check_stage3_final_responses()
    
    print("\n" + "="*80)
    print("✅ VERIFICATION COMPLETE")
    print("="*80)
