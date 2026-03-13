"""
多语言角色扮演数据处理模块
处理多语言角色扮演的回答数据，转换为IVS格式
"""

import os
import json
import pickle
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import re
import sys

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.base.ivs_question_processor import IVSQuestionProcessor
from src.utils.country_name_standardizer import CountryNameStandardizer


class MultilingualRoleplayDataProcessor:
    """多语言角色扮演数据处理器"""
    
    def __init__(self, data_path: str = "data"):
        self.data_path = Path(data_path)
        self.raw_data_dir = self.data_path / "llm_interviews" / "multilingual" / "interview_raw"
        self.processed_dir = self.data_path / "llm_interviews" / "multilingual" / "processed"
        
        # 确保目录存在
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        # IVS问题列表
        self.iv_qns = ['A008', 'A165', 'E018', 'E025', 'F063', 'F118', 'F120', 'G006', 'Y002', 'Y003']
        
        # 加载配置
        self.multilingual_config = self._load_multilingual_config()
        # 使用统一的问题配置（从 IVSQuestionProcessor）
        self.question_mapping = IVSQuestionProcessor.QUESTION_CONFIG
        # 加载文化区域映射
        self.cultural_mapping = self._load_cultural_mapping()
        # 国家名称标准化器（用于获取数字代码）
        self.country_standardizer = CountryNameStandardizer()
    
    def _load_multilingual_config(self) -> Dict:
        """加载多语言配置"""
        # 统一配置文件路径
        config_path = Path(__file__).parent.parent.parent / 'config' / 'questions' / 'multilingual' / 'multilingual_questions_complete.json'
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        print(f"⚠️ 未找到多语言配置文件: {config_path}")
        return {}
    
    def _load_cultural_mapping(self) -> Dict:
        """加载文化区域映射"""
        config_path = Path(__file__).parent.parent.parent / 'config' / 'country' / 'cultural_regions.json'
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('country_cultural_mapping', {})
        except Exception as e:
            print(f"⚠️ 加载文化区域配置失败: {e}")
            return {}
    
    def load_multilingual_results(self, results_file: str = None) -> Dict:
        """
        加载多语言角色扮演结果
        支持两种方式：
        1. 从单独的JSON文件加载（新的batch_interview格式）
        2. 从汇总文件加载（旧格式）
        """
        if results_file is None:
            # 查找所有新格式文件，优先使用pkl格式（占用空间小）
            pkl_files = list(self.raw_data_dir.glob("roleplay_results_ml_*.pkl"))
            json_files = list(self.raw_data_dir.glob("roleplay_results_ml_*.json"))
            
            # 优先选择最新的pkl文件，如果没有pkl再选json
            if pkl_files:
                results_file = max(pkl_files, key=lambda x: x.stat().st_mtime)
                print(f"✅ 找到 PKL 格式文件（优先）: {results_file.name}")
            elif json_files:
                results_file = max(json_files, key=lambda x: x.stat().st_mtime)
                print(f"✅ 找到 JSON 格式文件: {results_file.name}")
            else:
                # 如果没有汇总文件，尝试从单独的JSON文件加载
                print("⚠️ 未找到汇总文件，尝试从单独的JSON文件加载...")
                return self._load_from_individual_files()
        else:
            results_file = Path(results_file)
        
        print(f"📂 加载结果文件: {results_file}")
        
        # 根据文件扩展名选择加载方式
        if results_file.suffix == '.pkl':
            with open(results_file, 'rb') as f:
                data = pickle.load(f)
        else:
            with open(results_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        
        # 验证数据格式
        if isinstance(data, dict) and 'results' in data:
            print(f"📊 加载了 {len(data.get('results', []))} 个结果")
        else:
            raise ValueError(f"不支持的数据格式，期望 {{results: [...]}}")
        
        return data
    
    def _load_from_individual_files(self) -> Dict:
        """从单独的JSON/PKL文件加载数据（支持从模型子文件夹加载）

        Deduplication strategy:
        - Each interview exists as both .json and .pkl; prefer .json to avoid
          pickle deserialization issues.
        - Multiple runs for the same (model, country, language) may exist with
          different timestamps; keep only the latest.
        """
        json_files = []
        pkl_files = []

        def _collect(directory):
            for f in directory.glob("*_*_*.json"):
                if not f.name.startswith("roleplay_results_ml_"):
                    json_files.append(f)
            for f in directory.glob("*_*_*.pkl"):
                if not f.name.startswith("roleplay_results_ml_"):
                    pkl_files.append(f)

        _collect(self.raw_data_dir)
        for subdir in self.raw_data_dir.iterdir():
            if subdir.is_dir():
                _collect(subdir)

        # Prefer JSON; only fall back to PKL for stems without a JSON counterpart
        json_stems = {f.stem for f in json_files}
        individual_files = list(json_files)
        for f in pkl_files:
            if f.stem not in json_stems:
                individual_files.append(f)

        if not individual_files:
            raise FileNotFoundError(
                f"未找到任何访谈数据文件\n查找路径: {self.raw_data_dir}\n（已搜索根目录和子文件夹）"
            )

        print(f"📂 找到 {len(individual_files)} 个单独的访谈文件 "
              f"(去除json/pkl重复后，原始 {len(json_files)+len(pkl_files)} 个)")

        # Parse all files and deduplicate by (model, country, language)
        unique_results: Dict[tuple, dict] = {}
        duplicates = 0

        for file_path in individual_files:
            try:
                if file_path.suffix == '.pkl':
                    import pickle
                    with open(file_path, 'rb') as f:
                        data = pickle.load(f)
                else:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                filename = file_path.stem
                parts = filename.split('_')

                timestamp_idx = -1
                for i, part in enumerate(parts):
                    if part.isdigit() and len(part) == 8:
                        timestamp_idx = i
                        break

                if timestamp_idx < 2:
                    continue

                model_country_lang = parts[:timestamp_idx]
                if len(model_country_lang) >= 3:
                    language = model_country_lang[-1]
                    country = model_country_lang[-2]
                    model = '_'.join(model_country_lang[:-2])
                elif len(model_country_lang) == 2:
                    country = model_country_lang[-1]
                    model = model_country_lang[0]
                    language = ''
                else:
                    continue

                # Build a sortable timestamp from filename parts
                ts_parts = parts[timestamp_idx:]
                file_timestamp = '_'.join(ts_parts)

                result = {
                    "model": model,
                    "country": country,
                    "language": language,
                    "timestamp": data.get("timestamp", file_timestamp),
                    "success_rate": data.get("success_rate", 1.0),
                    "responses": data.get("responses", []),
                    "_file_timestamp": file_timestamp,
                }

                key = (model, country, language)
                if key in unique_results:
                    duplicates += 1
                    # Keep the EARLIEST run to match original paper data
                    if file_timestamp < unique_results[key].get("_file_timestamp", ""):
                        unique_results[key] = result
                else:
                    unique_results[key] = result

            except Exception as e:
                print(f"⚠️ 跳过文件 {file_path.name}: {e}")
                continue

        print(f"🔄 去除了 {duplicates} 条重复记录（同一 model/country/language 的多次运行）")
        print(f"✅ 保留了 {len(unique_results)} 个唯一组合")

        results = []
        for r in unique_results.values():
            r.pop("_file_timestamp", None)
            results.append(r)

        return {"results": results}
    
    def process_single_response(self, response: Dict) -> Dict:
        """处理单个回答 - 支持新旧两种格式"""
        # 检测格式：新格式有entity_id，旧格式有country和language
        if "entity_id" in response:
            # 新格式：解析entity_id (格式: "Country_language")
            entity_id = response.get("entity_id", "")
            parts = entity_id.split("_", 1)  # 只分割一次
            country = parts[0] if len(parts) > 0 else ""
            language = parts[1] if len(parts) > 1 else ""
            model = response.get("model_name", "")
        else:
            # 旧格式：直接使用字段
            model = response.get("model", "")
            country = response.get("country", "")
            language = response.get("language", "")
        
        processed = {
            "model": model,
            "country": country,
            "language": language,
            "timestamp": response.get("timestamp", ""),
            "success_rate": response.get("success_rate", 1.0),
            "processed_answers": {}
        }
        
        # 处理每个问题的回答（统一格式）
        for resp in response.get("responses", []):
            question_id = resp.get("question_id", "")
            
            # Use final_response (majority vote across attempts) as the
            # canonical answer.  Fall back to processed_response, then to the
            # last element of all_responses.
            raw_response = str(resp.get("final_response") or resp.get("processed_response") or "")
            if not raw_response.strip():
                all_responses = resp.get("all_responses", [])
                if all_responses:
                    for attempt_resp in reversed(all_responses):
                        if isinstance(attempt_resp, str) and attempt_resp.strip():
                            raw_response = attempt_resp
                            break
                        elif isinstance(attempt_resp, dict) and attempt_resp.get("raw_response"):
                            raw_response = attempt_resp["raw_response"]
                            break
                else:
                    raw_response = resp.get("raw_response", "")
            
            if question_id in self.question_mapping:
                processed_answer = self._process_answer(
                    question_id, raw_response, raw_response
                )
                processed["processed_answers"][question_id] = processed_answer
        
        return processed
    
    def _process_answer(self, question_id: str, processed_response: str, raw_response: str) -> Dict:
        """处理单个问题的回答 - 使用统一的处理器"""
        # 直接使用 base 的统一处理器
        return IVSQuestionProcessor.validate_and_process_response(raw_response, question_id)
    
    def process_all_results(self, results_data: Dict) -> pd.DataFrame:
        """处理所有结果，转换为DataFrame格式"""
        processed_data = []
        
        # 处理results：可能是字典或列表
        results = results_data.get("results", [])
        if isinstance(results, dict):
            # 如果是字典，遍历值
            results_list = list(results.values())
        else:
            # 如果是列表，直接使用
            results_list = results
        
        for result in results_list:
            processed = self.process_single_response(result)
            
            # 创建一行数据
            row = {
                "model": processed["model"],
                "country": processed["country"],
                "language": processed["language"],
                "timestamp": processed["timestamp"],
                "success_rate": processed["success_rate"]
            }
            
            # 添加每个问题的答案
            for question_id in self.question_mapping.keys():
                if question_id in processed["processed_answers"]:
                    answer = processed["processed_answers"][question_id]
                    row[f"{question_id}_valid"] = answer["valid"]
                    row[f"{question_id}_numeric"] = answer["numeric_value"]
                    row[f"{question_id}_standardized"] = answer["standardized_value"]
                    row[f"{question_id}_raw"] = answer["raw_response"]
                else:
                    row[f"{question_id}_valid"] = False
                    row[f"{question_id}_numeric"] = None
                    row[f"{question_id}_standardized"] = None
                    row[f"{question_id}_raw"] = ""
            
            processed_data.append(row)
        
        return pd.DataFrame(processed_data)
    
    def create_ivs_format_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """创建IVS格式的数据，用于与真实国家数据合并PCA分析"""
        ivs_data = []
        
        for _, row in df.iterrows():
            country_name = row["country"]
            # 获取数字country_code（与Stage0保持一致）
            numeric_code = self.country_standardizer.get_numeric_code(country_name)
            if numeric_code is None:
                print(f"⚠️ 无法找到国家 '{country_name}' 的数字代码，跳过")
                continue
            
            ivs_row = {
                # 基本信息 - 使用数字代码作为country_code（与Stage0一致）
                "country_code": float(numeric_code),  # 使用数字代码，与Stage0格式一致
                "Country": country_name,  # 保留国家名称
                "year": 2025,  # 多语言数据的年份
                "weight": 1.0,  # 权重
                "data_source": "multilingual_roleplay",
                "model_name": row["model"],
                "model_region": self._get_model_region(row["model"]),
                "cultural_region": self._get_cultural_region(country_name),
                "language": row["language"],
                "entity_id": f"{row['model']}_{country_name}_{row['language']}"
            }
            
            # 添加问题答案（与Stage2保持一致）
            for question_id in self.question_mapping.keys():
                valid_col = f"{question_id}_valid"
                
                # 检查valid_col是否存在且为True
                is_valid = False
                if valid_col in row.index:
                    val = row[valid_col]
                    # 处理可能是数组或标量的情况
                    if isinstance(val, (list, np.ndarray)):
                        is_valid = bool(val[0]) if len(val) > 0 else False
                    else:
                        is_valid = bool(val)
                
                # Y002 → materialist_score (1=materialist, 2=mixed, 3=postmaterialist)
                # Y003 → y003_score (traditional − secular-rational, range -2..+2)
                # Recompute from raw response to match WVS IVS coding scheme.
                if question_id == 'Y002':
                    raw_col = f"{question_id}_raw"
                    if is_valid and raw_col in row.index and row[raw_col]:
                        try:
                            nums = [int(x) for x in str(row[raw_col]).split()]
                            if len(nums) >= 2:
                                ivs_row[question_id] = float(IVSQuestionProcessor.process_y002(nums[0], nums[1]))
                            else:
                                ivs_row[question_id] = np.nan
                        except (ValueError, TypeError):
                            ivs_row[question_id] = np.nan
                    else:
                        ivs_row[question_id] = np.nan
                elif question_id == 'Y003':
                    raw_col = f"{question_id}_raw"
                    if is_valid and raw_col in row.index and row[raw_col]:
                        try:
                            nums = [int(x) for x in str(row[raw_col]).split()]
                            result = IVSQuestionProcessor.process_y003(nums)
                            ivs_row[question_id] = float(result["y003_score"])
                        except (ValueError, TypeError):
                            ivs_row[question_id] = np.nan
                    else:
                        ivs_row[question_id] = np.nan
                else:
                    # 其他问题使用standardized值
                    standardized_col = f"{question_id}_standardized"
                    if is_valid and standardized_col in row.index:
                        std_val = row[standardized_col]
                        # 处理可能是数组的情况
                        if isinstance(std_val, (list, np.ndarray)):
                            std_val = std_val[0] if len(std_val) > 0 else np.nan
                        if pd.notna(std_val):
                            ivs_row[question_id] = std_val
                        else:
                            ivs_row[question_id] = np.nan
                    else:
                        ivs_row[question_id] = np.nan
            
            ivs_data.append(ivs_row)
        
        # 转换为DataFrame
        ivs_df = pd.DataFrame(ivs_data)
        
        # 🔧 筛选：至少需要6个问题的有效回答（与Stage0真实国家数据保持一致）
        iv_qns = ["A008", "A165", "E018", "E025", "F063", "F118", "F120", "G006", "Y002", "Y003"]
        original_count = len(ivs_df)
        ivs_df = ivs_df.dropna(subset=iv_qns, thresh=6)
        filtered_count = original_count - len(ivs_df)
        
        if filtered_count > 0:
            print(f"⚠️ 过滤了 {filtered_count} 个有效回答数<6的结果")
        
        return ivs_df
    
    def _get_model_region(self, model_name: str) -> str:
        """获取模型区域"""
        if "openai" in model_name.lower():
            return "US"
        elif "google" in model_name.lower():
            return "US"
        elif "anthropic" in model_name.lower():
            return "US"
        elif "deepseek" in model_name.lower() or "qwen" in model_name.lower():
            return "CN"
        elif "llama" in model_name.lower():
            return "US"
        elif "mistral" in model_name.lower():
            return "EU"
        else:
            return "Unknown"
    
    def _get_cultural_region(self, country: str) -> str:
        """获取文化区域"""
        return self.cultural_mapping.get(country, "Unknown")
    
    def calculate_statistics(self, df: pd.DataFrame) -> Dict:
        """计算统计信息"""
        stats = {
            "total_responses": len(df),
            "languages": df["language"].unique().tolist(),
            "models": df["model"].unique().tolist(),
            "countries": df["country"].unique().tolist(),
            "overall_success_rate": df["success_rate"].mean(),
            "question_validity": {},
            "language_stats": {},
            "model_stats": {},
            "country_stats": {}
        }
        
        # 问题有效性统计
        for question_id in self.question_mapping.keys():
            valid_col = f"{question_id}_valid"
            if valid_col in df.columns:
                stats["question_validity"][question_id] = {
                    "valid_count": df[valid_col].sum(),
                    "total_count": len(df),
                    "validity_rate": df[valid_col].mean()
                }
        
        # 按语言统计
        for language in stats["languages"]:
            lang_df = df[df["language"] == language]
            stats["language_stats"][language] = {
                "count": len(lang_df),
                "success_rate": lang_df["success_rate"].mean(),
                "countries": lang_df["country"].unique().tolist()
            }
        
        # 按模型统计
        for model in stats["models"]:
            model_df = df[df["model"] == model]
            stats["model_stats"][model] = {
                "count": len(model_df),
                "success_rate": model_df["success_rate"].mean(),
                "languages": model_df["language"].unique().tolist()
            }
        
        # 按国家统计
        for country in stats["countries"]:
            country_df = df[df["country"] == country]
            stats["country_stats"][country] = {
                "count": len(country_df),
                "success_rate": country_df["success_rate"].mean(),
                "language": country_df["language"].iloc[0] if len(country_df) > 0 else ""
            }
        
        return stats
    
    def save_processed_data(self, df: pd.DataFrame, ivs_df: pd.DataFrame, stats: Dict, suffix: str = None):
        """
        保存处理后的数据（与Stage2保持一致的命名规范）
        
        文件命名：
        - 处理后数据：llm_roleplay_ml_processed_responses_*.pkl
        - IVS格式数据：llm_roleplay_ml_processed_responses_ivs_format_*.pkl
        """
        if suffix is None:
            suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print(f"\n{'='*60}")
        print(f"💾 步骤3: 保存处理后的数据")
        print(f"{'='*60}")
        
        # 保存原始处理数据（与Stage2命名一致）
        processed_file = self.processed_dir / f"llm_roleplay_ml_processed_responses_{suffix}.pkl"
        with open(processed_file, 'wb') as f:
            pickle.dump(df, f)
        print(f"✅ 原始处理数据: {processed_file.name}")
        
        # 保存IVS格式数据（与Stage2命名一致）
        ivs_file = self.processed_dir / f"llm_roleplay_ml_processed_responses_ivs_format_{suffix}.pkl"
        with open(ivs_file, 'wb') as f:
            pickle.dump(ivs_df, f)
        print(f"✅ IVS格式数据: {ivs_file.name}")
        
        # 保存JSON格式（便于查看）
        ivs_json_file = self.processed_dir / f"llm_roleplay_ml_processed_responses_ivs_format_{suffix}.json"
        ivs_df.to_json(ivs_json_file, orient='records', indent=2, force_ascii=False)
        print(f"✅ IVS格式JSON: {ivs_json_file.name}")
        
        # 保存CSV格式（便于查看）
        csv_file = self.processed_dir / f"llm_roleplay_ml_processed_responses_{suffix}.csv"
        df.to_csv(csv_file, index=False, encoding='utf-8')
        print(f"✅ 原始处理CSV: {csv_file.name}")
        
        ivs_csv_file = self.processed_dir / f"llm_roleplay_ml_processed_responses_ivs_format_{suffix}.csv"
        ivs_df.to_csv(ivs_csv_file, index=False, encoding='utf-8')
        print(f"✅ IVS格式CSV: {ivs_csv_file.name}")
        
        print(f"\n📁 保存位置: {self.processed_dir}")
        print(f"📊 数据量: 原始 {len(df)} 行, IVS格式 {len(ivs_df)} 行")
        print(f"{'='*60}")
        
        # 保存统计信息
        stats_file = self.processed_dir / f"multilingual_roleplay_stats_{suffix}.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"数据处理完成，文件已保存:")
        print(f"  处理数据: {processed_file}")
        print(f"  IVS格式: {ivs_file}")
        print(f"  CSV格式: {csv_file}")
        print(f"  统计信息: {stats_file}")
        
        return {
            "processed_file": processed_file,
            "ivs_file": ivs_file,
            "csv_file": csv_file,
            "stats_file": stats_file
        }
    
    def process_multilingual_data(self, results_file: str = None) -> Dict:
        """完整的多语言数据处理流程"""
        print("=== 多语言角色扮演数据处理 ===")
        
        # 1. 加载原始结果
        print("1. 加载原始结果...")
        results_data = self.load_multilingual_results(results_file)
        
        # 2. 处理所有结果
        print("2. 处理回答数据...")
        df = self.process_all_results(results_data)
        print(f"   处理了 {len(df)} 个回答")
        
        # 3. 创建IVS格式数据
        print("3. 创建IVS格式数据...")
        ivs_df = self.create_ivs_format_data(df)
        print(f"   创建了 {len(ivs_df)} 个IVS格式记录")
        
        # 4. 计算统计信息
        print("4. 计算统计信息...")
        stats = self.calculate_statistics(df)
        
        # 5. 保存处理后的数据
        print("5. 保存处理后的数据...")
        file_paths = self.save_processed_data(df, ivs_df, stats)
        
        # 6. 显示统计摘要
        print("\\n=== 处理结果摘要 ===")
        print(f"总回答数: {stats['total_responses']}")
        print(f"语言数: {len(stats['languages'])}")
        print(f"模型数: {len(stats['models'])}")
        print(f"国家数: {len(stats['countries'])}")
        print(f"整体成功率: {stats['overall_success_rate']:.1f}%")
        
        print("\\n各语言表现:")
        for lang, lang_stats in stats["language_stats"].items():
            print(f"  {lang}: {lang_stats['success_rate']:.1f}% ({lang_stats['count']} 个回答)")
        
        return {
            "processed_df": df,
            "ivs_df": ivs_df,
            "stats": stats,
            "file_paths": file_paths
        }
    
    def process_multilingual_data_to_ivs_format(self, results_file: str = None) -> pd.DataFrame:
        """处理多语言数据并直接返回IVS格式的DataFrame"""
        print("📊 处理多语言数据到IVS格式...")
        
        # 1. 加载多语言结果数据（使用统一的加载方法）
        if results_file is None:
            # 自动查找最新的roleplay_results文件
            print("📂 自动查找最新的访谈结果...")
            results_data = self.load_multilingual_results()
        else:
            # 使用指定的文件
            print(f"📂 加载指定文件: {results_file}")
            with open(results_file, 'r', encoding='utf-8') as f:
                results_data = json.load(f)
        
        # 检查数据格式（只支持新格式）
        if isinstance(results_data, dict) and 'results' in results_data:
            # 新格式：{results: [...]}
            print(f"✅ 检测到新格式数据")
            return self._process_new_format_to_ivs(results_data)
        else:
            raise ValueError(f"不支持的数据格式，期望 {{results: [...]}}")
    
    def _process_new_format_to_ivs(self, results_data: Dict) -> pd.DataFrame:
        """处理新格式数据（{results: [...]）到IVS格式"""
        results_list = results_data.get('results', [])
        print(f"✅ 加载了 {len(results_list)} 个访谈结果")
        
        # 去重：对于同一个 (model, country, language) 组合，只保留最新的一条
        unique_results = {}
        duplicates = 0
        
        for result in results_list:
            model_name = result.get('model_name', result.get('model'))
            country_raw = result.get('country')
            if isinstance(country_raw, dict):
                country = country_raw.get('name')
            else:
                country = country_raw
            language = result.get('language')
            
            key = (model_name, country, language)
            
            if key in unique_results:
                # 已存在，比较时间戳，保留最新的
                existing_timestamp = unique_results[key].get('timestamp', '')
                current_timestamp = result.get('timestamp', '')
                if current_timestamp > existing_timestamp:
                    unique_results[key] = result
                duplicates += 1
            else:
                unique_results[key] = result
        
        print(f"🔄 去除了 {duplicates} 条重复记录")
        print(f"✅ 保留了 {len(unique_results)} 个唯一组合")
        
        ivs_data = []
        
        for result in unique_results.values():
            # 提取model_name（可能是'model_name'或'model'）
            model_name = result.get('model_name', result.get('model'))
            
            # 提取country（可能是字符串或字典）
            country_raw = result.get('country')
            if isinstance(country_raw, dict):
                country = country_raw.get('name')
            else:
                country = country_raw
            
            language = result.get('language')
            responses = result.get('responses', [])
            
            # 获取数字country_code（与Stage0保持一致）
            numeric_code = self.country_standardizer.get_numeric_code(country)
            if numeric_code is None:
                print(f"⚠️ 无法找到国家 '{country}' 的数字代码，跳过")
                continue
            
            # 创建IVS格式的行
            ivs_row = {
                'country_code': float(numeric_code),  # 使用数字代码，与Stage0格式一致
                'Country': country,  # 保留国家名称
                'model_name': model_name,
                'language': language,
                'data_source': 'Multilingual',
                'year': 2025,
                'weight': 1.0,
                'Cultural Region': self._get_cultural_region(country),
                'entity_id': f"{model_name}_{country}_{language}"
            }
            
            # 处理responses（使用统一处理器）
            if isinstance(responses, list):
                for item in responses:
                    if isinstance(item, dict) and 'question_id' in item:
                        question_id = item['question_id']
                        if question_id in self.iv_qns:
                            # 获取回答文本（优先使用 final_response）
                            answer = item.get('final_response') or item.get('processed_response', '')
                            
                            # 使用统一处理器验证和处理
                            result = IVSQuestionProcessor.validate_and_process_response(answer, question_id)
                            
                            if result["valid"]:
                                # 根据问题类型选择合适的值
                                if question_id == "Y002" and "materialist_score" in result:
                                    # Y002 使用物质主义倾向分数
                                    ivs_row[question_id] = result["materialist_score"]
                                elif question_id == "Y003" and "y003_score" in result:
                                    # Y003 使用计算的分数
                                    ivs_row[question_id] = result["y003_score"]
                                else:
                                    # 其他问题使用 numeric_value
                                    ivs_row[question_id] = result["numeric_value"]
                            else:
                                ivs_row[question_id] = np.nan
            else:
                print(f"⚠️ 不支持的responses格式: {type(responses)}")
            
            ivs_data.append(ivs_row)
        
        print(f"✅ 处理了 {len(ivs_data)} 个回答")
        
        # 创建DataFrame
        ivs_df = pd.DataFrame(ivs_data)
        print(f"✅ 创建了 {len(ivs_df)} 个IVS格式记录")
        
        # 添加字段别名以兼容PCA分析
        if 'model_name' in ivs_df.columns:
            ivs_df['model'] = ivs_df['model_name']
        if 'country_code' in ivs_df.columns:
            ivs_df['country'] = ivs_df['country_code']
        
        return ivs_df


def main():
    """主函数"""
    processor = MultilingualRoleplayDataProcessor()
    
    try:
        result = processor.process_multilingual_data()
        print("\\n✅ 多语言数据处理完成！")
        print("\\n下一步可以运行PCA分析:")
        print("  python src/roleplay/multilingual_roleplay_pca_analysis.py")
        
    except Exception as e:
        print(f"❌ 数据处理失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
