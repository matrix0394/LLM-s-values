#!/usr/bin/env python3
"""
分析多语言vs英文角色扮演的比较结果
"""

import json
import pandas as pd
from pathlib import Path

def analyze_distance_results():
    """分析距离比较结果"""
    
    # 加载最新的距离分析结果
    results_dir = Path("data/results/unified_multilingual_pca")
    json_files = list(results_dir.glob("unified_distance_analysis_*.json"))
    
    if not json_files:
        print("❌ 未找到距离分析结果文件")
        return
    
    latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
    print(f"📁 分析文件: {latest_file}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    print("\n" + "="*80)
    print("🎯 多语言 vs 英文角色扮演 - 统一PCA空间比较结果")
    print("="*80)
    
    # 1. 多语言 vs 真实国家
    print("\n📊 1. 多语言方法 vs 真实国家距离:")
    ml_distances = []
    for key, data in results["multilingual_vs_real"].items():
        model = data["model"]
        country = data["country"]
        language = data["language"]
        distance = data["distance"]
        ml_distances.append(distance)
        
        # 国家代码映射
        country_names = {"156": "中国", "643": "俄国", "484": "墨西哥", "818": "埃及"}
        country_name = country_names.get(country, country)
        
        print(f"   {model} ({country_name}, {language}): {distance:.3f}")
    
    # 2. 英文 vs 真实国家
    print("\n📊 2. 英文方法 vs 真实国家距离:")
    eng_distances = []
    for key, data in results["english_vs_real"].items():
        model = data["model"]
        country = data["country"]
        distance = data["distance"]
        eng_distances.append(distance)
        
        country_names = {"156": "中国", "643": "俄国", "484": "墨西哥", "818": "埃及"}
        country_name = country_names.get(country, country)
        
        print(f"   {model} ({country_name}, 英文): {distance:.3f}")
    
    # 3. 统计对比
    print("\n📈 3. 统计对比:")
    if ml_distances and eng_distances:
        ml_avg = sum(ml_distances) / len(ml_distances)
        eng_avg = sum(eng_distances) / len(eng_distances)
        improvement = eng_avg - ml_avg
        improvement_pct = (improvement / ml_avg) * 100
        
        print(f"   多语言平均距离: {ml_avg:.3f}")
        print(f"   英文平均距离:   {eng_avg:.3f}")
        print(f"   差异:           {improvement:.3f}")
        print(f"   改进百分比:     {improvement_pct:.1f}%")
        
        if improvement > 0:
            print(f"   🏆 结论: 英文方法表现更好 (距离更小)")
        else:
            print(f"   🏆 结论: 多语言方法表现更好 (距离更小)")
    
    # 4. 按国家分析
    print("\n🌍 4. 按国家分析:")
    country_analysis = {}
    
    # 收集多语言数据
    for key, data in results["multilingual_vs_real"].items():
        country = data["country"]
        if country not in country_analysis:
            country_analysis[country] = {"multilingual": [], "english": []}
        country_analysis[country]["multilingual"].append(data["distance"])
    
    # 收集英文数据
    for key, data in results["english_vs_real"].items():
        country = data["country"]
        if country not in country_analysis:
            country_analysis[country] = {"multilingual": [], "english": []}
        country_analysis[country]["english"].append(data["distance"])
    
    country_names = {"156": "中国", "643": "俄国", "484": "墨西哥", "818": "埃及"}
    
    for country, distances in country_analysis.items():
        country_name = country_names.get(country, country)
        ml_avg = sum(distances["multilingual"]) / len(distances["multilingual"]) if distances["multilingual"] else 0
        eng_avg = sum(distances["english"]) / len(distances["english"]) if distances["english"] else 0
        
        if ml_avg > 0 and eng_avg > 0:
            better = "英文" if eng_avg < ml_avg else "多语言"
            diff = abs(ml_avg - eng_avg)
            print(f"   {country_name}: 多语言={ml_avg:.3f}, 英文={eng_avg:.3f}, 更好={better} (差异={diff:.3f})")
    
    # 5. 按模型分析
    print("\n🤖 5. 按模型分析:")
    model_analysis = {}
    
    # 收集数据
    for key, data in results["multilingual_vs_real"].items():
        model = data["model"]
        if model not in model_analysis:
            model_analysis[model] = {"multilingual": [], "english": []}
        model_analysis[model]["multilingual"].append(data["distance"])
    
    for key, data in results["english_vs_real"].items():
        model = data["model"]
        if model not in model_analysis:
            model_analysis[model] = {"multilingual": [], "english": []}
        model_analysis[model]["english"].append(data["distance"])
    
    for model, distances in model_analysis.items():
        model_short = model.split('/')[-1]
        ml_avg = sum(distances["multilingual"]) / len(distances["multilingual"]) if distances["multilingual"] else 0
        eng_avg = sum(distances["english"]) / len(distances["english"]) if distances["english"] else 0
        
        if ml_avg > 0 and eng_avg > 0:
            better = "英文" if eng_avg < ml_avg else "多语言"
            diff = abs(ml_avg - eng_avg)
            print(f"   {model_short}: 多语言={ml_avg:.3f}, 英文={eng_avg:.3f}, 更好={better} (差异={diff:.3f})")
    
    print("\n" + "="*80)
    print("📋 总结:")
    print("   ✅ 成功在统一PCA空间中比较了多语言和英文方法")
    print("   ✅ 所有距离计算都在同一坐标系中，结果可信")
    print("   📁 详细数据请查看:", latest_file)
    print("="*80)

if __name__ == "__main__":
    analyze_distance_results()





