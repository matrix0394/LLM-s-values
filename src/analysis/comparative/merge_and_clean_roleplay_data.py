#!/usr/bin/env python3
"""
清理重复/无效文件并重新合并角色扮演数据
1. 删除 valid_responses=0 的无效文件
2. 从单独文件合并，模型名规范化为 config 中的正式 key
3. 去重：(model, country, language) 保留 valid_responses 最高的
4. 保存新 roleplay_results_ml_*.pkl
5. 运行数据处理和 PCA
"""

import sys
import json
import pickle
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

data_dir = project_root / "data" / "roleplay_multilingual" / "llm_responses_roleplay_ml"


def load_model_config():
    """加载模型配置，构建 short_name -> canonical 映射"""
    with open(project_root / "config" / "models" / "llm_models.json") as f:
        cfg = json.load(f)
    models = cfg.get("models", {})
    canonical_keys = set(models.keys())
    short_to_canonical = {}
    for key in canonical_keys:
        short = key.split("/")[-1]
        short_to_canonical[short] = key
    return canonical_keys, short_to_canonical


def normalize_model(model: str, short_to_canonical: dict, canonical_keys: set) -> str:
    """将模型名规范化为 config 中的正式 key"""
    if model in canonical_keys:
        return model
    short = model.split("/")[-1]
    return short_to_canonical.get(short, model)


def collect_all_individual_files():
    """收集根目录和子目录下的所有访谈文件"""
    files = []
    files.extend(data_dir.glob("*_*_*.pkl"))
    files.extend(data_dir.glob("*_*_*.json"))
    for subdir in data_dir.iterdir():
        if subdir.is_dir():
            files.extend(subdir.glob("*.pkl"))
            files.extend(subdir.glob("*.json"))
    return [f for f in files if not f.name.startswith("roleplay_results_ml_")]


def main():
    print("=" * 60)
    print("🔄 清理并重新合并角色扮演数据")
    print("=" * 60)
    
    canonical_keys, short_to_canonical = load_model_config()
    print(f"\n✅ 加载模型配置: {len(canonical_keys)} 个模型")
    
    all_files = collect_all_individual_files()
    print(f"📂 找到 {len(all_files)} 个单独访谈文件")
    
    # 第一遍：加载所有文件，找出无效的并删除
    to_delete = []
    all_results = []  # (file, result, model_norm, vr)
    
    for f in all_files:
        try:
            if f.suffix == ".pkl":
                with open(f, "rb") as fp:
                    data = pickle.load(fp)
            else:
                with open(f, "r", encoding="utf-8") as fp:
                    data = json.load(fp)
            
            if not isinstance(data, dict):
                continue
            
            model = data.get("model") or data.get("model_name", "")
            country_raw = data.get("country", "")
            country = country_raw.get("name") if isinstance(country_raw, dict) else country_raw
            language = data.get("language", "")
            vr = data.get("valid_responses", 0)
            
            if not model or not country:
                continue
            
            model_norm = normalize_model(model, short_to_canonical, canonical_keys)
            
            if vr == 0:
                to_delete.append(f)
                continue
            
            all_results.append((f, data, model_norm, vr))
            
        except Exception as e:
            print(f"⚠️ 跳过 {f.name}: {e}")
    
    # 删除无效文件
    print(f"\n🗑️ 删除 {len(to_delete)} 个无效文件 (valid_responses=0)...")
    deleted = 0
    for f in to_delete:
        try:
            if f.exists():
                f.unlink()
                deleted += 1
        except Exception as e:
            print(f"   删除失败 {f.name}: {e}")
    print(f"   已删除 {deleted} 个文件")
    
    # 第二遍：去重，每个 (model_norm, country, language) 保留 vr 最高、时间戳最新的
    best = {}  # (model, country, lang) -> result
    for _f, data, model_norm, vr in all_results:
        country_raw = data.get("country", "")
        country = country_raw.get("name") if isinstance(country_raw, dict) else country_raw
        language = data.get("language", "")
        key = (model_norm, country, language)
        
        data["model"] = model_norm  # 统一为规范名
        data["model_name"] = model_norm
        
        if key not in best or vr > best[key][1]:
            best[key] = (data, vr)
        elif vr == best[key][1]:
            ts_new = data.get("timestamp", "")
            ts_old = best[key][0].get("timestamp", "")
            if ts_new > ts_old:
                best[key] = (data, vr)
    
    results = [r[0] for r in best.values()]
    print(f"\n📊 去重后: {len(results)} 条唯一记录")
    
    # 统计12国法语
    targets = [("Algeria", "fr"), ("Egypt", "fr"), ("Iraq", "fr"), ("Jordan", "fr"),
               ("Kuwait", "fr"), ("Lebanon", "fr"), ("Libya", "fr"), ("Morocco", "fr"),
               ("Palestine", "fr"), ("Qatar", "fr"), ("Tunisia", "fr"), ("Yemen", "fr")]
    for c, l in targets:
        n = sum(1 for r in results if r.get("country") == c and r.get("language") == l)
        print(f"   {c} {l}: {n} 个模型")
    
    # 备份旧合并文件
    old_merged = list(data_dir.glob("roleplay_results_ml_*.pkl"))
    if old_merged:
        latest = max(old_merged, key=lambda x: x.stat().st_mtime)
        backup = latest.with_name(latest.stem + "_backup_before_merge.pkl")
        shutil.copy2(latest, backup)
        print(f"\n📦 已备份: {backup.name}")
    
    # 保存新合并文件
    merged = {
        "experiment_type": "multilingual_roleplay",
        "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "total_tasks": len(results),
        "successful_tasks": len([r for r in results if r.get("valid_responses", 0) > 0]),
        "results": results,
    }
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_pkl = data_dir / f"roleplay_results_ml_{ts}.pkl"
    with open(out_pkl, "wb") as f:
        pickle.dump(merged, f)
    print(f"✅ 新合并文件: {out_pkl.name}")
    
    # 运行数据处理和 PCA
    print("\n" + "=" * 60)
    print("🔄 运行数据处理和 PCA 流程...")
    print("=" * 60)
    
    from src.roleplay_multilingual.multilingual_roleplay_data_processor import MultilingualRoleplayDataProcessor
    from src.run.run_roleplay_multilingual_analysis_clean import RoleplayMultilingualAnalysisRunner
    
    processor = MultilingualRoleplayDataProcessor(data_path=str(project_root / "data"))
    processor.raw_data_dir = data_dir
    
    # 使用新合并文件进行完整处理
    processor.process_multilingual_data(results_file=str(out_pkl))
    
    # 运行 PCA
    runner = RoleplayMultilingualAnalysisRunner(project_root=str(project_root))
    if not runner.step2_pca_analysis():
        print("\n❌ PCA 执行失败")
    else:
        print("\n✅ 数据处理和 PCA 完成")
    
    # 运行 ar/fr/en 三语对比分析
    print("\n" + "=" * 60)
    print("🔄 运行 Arabic vs French vs English 三语对比分析...")
    print("=" * 60)
    import subprocess
    subprocess.run([sys.executable, str(project_root / "analyze_french_vs_arabic.py")], check=False)
    subprocess.run([sys.executable, str(project_root / "analyze_french_supplementary.py")], check=False)


if __name__ == "__main__":
    main()
