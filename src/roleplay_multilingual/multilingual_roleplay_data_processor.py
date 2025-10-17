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


class MultilingualRoleplayDataProcessor:
    """多语言角色扮演数据处理器"""
    
    def __init__(self, data_path: str = "../data"):
        self.data_path = Path(data_path)
        self.results_dir = self.data_path / "results" / "multilingual_roleplay"
        self.processed_dir = self.data_path / "processed"
        
        # 确保目录存在
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        # IVS问题列表
        self.iv_qns = ['A008', 'A165', 'E018', 'E025', 'F063', 'F118', 'F120', 'G006', 'Y002', 'Y003']
        
        # 加载配置
        self.multilingual_config = self._load_multilingual_config()
        self.question_mapping = self._create_question_mapping()
    
    def _load_multilingual_config(self) -> Dict:
        """加载多语言配置"""
        possible_paths = [
            Path("config/multilingual_questions_complete.json"),
            Path("../config/multilingual_questions_complete.json"),
            Path("../../config/multilingual_questions_complete.json")
        ]
        
        for config_path in possible_paths:
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        
        print("警告: 未找到多语言配置文件")
        return {}
    
    def _create_question_mapping(self) -> Dict:
        """创建问题ID到标准格式的映射"""
        return {
            "A008": {"type": "single", "scale": (1, 4), "reverse": False},
            "A165": {"type": "single", "scale": (1, 2), "reverse": False},
            "E018": {"type": "single", "scale": (1, 3), "reverse": False},
            "E025": {"type": "single", "scale": (1, 3), "reverse": False},
            "F063": {"type": "single", "scale": (1, 10), "reverse": False},
            "F118": {"type": "single", "scale": (1, 10), "reverse": False},
            "F120": {"type": "single", "scale": (1, 10), "reverse": False},
            "G006": {"type": "single", "scale": (1, 4), "reverse": False},
            "Y002": {"type": "multi", "options": 4, "choices": 2},
            "Y003": {"type": "multi", "options": 11, "choices": 5}
        }
    
    def load_multilingual_results(self, results_file: str = None) -> Dict:
        """加载多语言角色扮演结果"""
        if results_file is None:
            # 查找最新的结果文件
            result_files = list(self.results_dir.glob("multilingual_roleplay_*.json"))
            if not result_files:
                raise FileNotFoundError("未找到多语言角色扮演结果文件")
            results_file = max(result_files, key=lambda x: x.stat().st_mtime)
        else:
            results_file = Path(results_file)
        
        print(f"加载结果文件: {results_file}")
        
        with open(results_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def process_single_response(self, response: Dict) -> Dict:
        """处理单个回答"""
        processed = {
            "model": response.get("model", ""),
            "country": response.get("country", ""),
            "language": response.get("language", ""),
            "timestamp": response.get("timestamp", ""),
            "success_rate": response.get("success_rate", 0),
            "processed_answers": {}
        }
        
        # 处理每个问题的回答
        for resp in response.get("responses", []):
            question_id = resp.get("question_id", "")
            
            # 处理新格式（包含final_response）和旧格式（processed_response）
            if "final_response" in resp:
                # 新格式：多次重复取众数
                processed_response = resp.get("final_response", "")
                # 使用最后一次的原始回答作为代表
                all_responses = resp.get("all_responses", [])
                raw_response = ""
                if all_responses:
                    # 找到最后一个有效的原始回答
                    for attempt_resp in reversed(all_responses):
                        if attempt_resp.get("raw_response"):
                            raw_response = attempt_resp["raw_response"]
                            break
            else:
                # 旧格式：单次回答
                raw_response = resp.get("raw_response", "")
                processed_response = resp.get("processed_response", "")
            
            if question_id in self.question_mapping:
                processed_answer = self._process_answer(
                    question_id, processed_response, raw_response
                )
                processed["processed_answers"][question_id] = processed_answer
        
        return processed
    
    def _process_answer(self, question_id: str, processed_response: str, raw_response: str) -> Dict:
        """处理单个问题的回答"""
        question_info = self.question_mapping[question_id]
        
        result = {
            "question_id": question_id,
            "raw_response": raw_response,
            "processed_response": processed_response,
            "valid": False,
            "numeric_value": None,
            "standardized_value": None
        }
        
        if not processed_response:
            return result
        
        try:
            if question_info["type"] == "single":
                # 单选题处理
                value = int(processed_response.strip())
                min_val, max_val = question_info["scale"]
                
                if min_val <= value <= max_val:
                    result["valid"] = True
                    result["numeric_value"] = value
                    # 标准化到0-1区间
                    result["standardized_value"] = (value - min_val) / (max_val - min_val)
                    
                    # 如果需要反向编码
                    if question_info.get("reverse", False):
                        result["standardized_value"] = 1 - result["standardized_value"]
            
            elif question_info["type"] == "multi":
                # 多选题处理 - 使用统一的处理器
                if question_id in ["Y002", "Y003"]:
                    unified_result = IVSQuestionProcessor.validate_and_process_response(raw_response, question_id)
                    if unified_result["valid"]:
                        result["valid"] = True
                        result["numeric_value"] = unified_result["numeric_value"]
                        result["standardized_value"] = unified_result["standardized_value"]
                        # 保存额外的分析结果
                        if question_id == "Y002" and "materialist_score" in unified_result:
                            result["materialist_score"] = unified_result["materialist_score"]
                        elif question_id == "Y003":
                            # 保存Y003的详细分析结果
                            for key, value in unified_result.items():
                                if key not in ["question_id", "raw_response", "processed_response", "numeric_value", "standardized_value", "valid"]:
                                    result[key] = value
                else:
                    # 其他多选题的处理逻辑（如果有的话）
                    values = [int(x.strip()) for x in processed_response.split()]
                    result["valid"] = True
                    result["numeric_value"] = values
                    result["standardized_value"] = len(values)  # 简单处理
        
        except (ValueError, AttributeError) as e:
            print(f"处理问题 {question_id} 的回答时出错: {e}")
        
        return result
    
    def process_all_results(self, results_data: Dict) -> pd.DataFrame:
        """处理所有结果，转换为DataFrame格式"""
        processed_data = []
        
        for result in results_data.get("results", []):
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
            ivs_row = {
                # 基本信息
                "country_code": row["country"],  # 使用国家名作为代码
                "year": 2024,  # 多语言数据的年份
                "weight": 1.0,  # 权重
                "data_source": "multilingual_roleplay",
                "model_name": row["model"],
                "model_region": self._get_model_region(row["model"]),
                "cultural_region": self._get_cultural_region(row["country"]),
                "language": row["language"],
                "entity_id": f"{row['model']}_{row['country']}_{row['language']}"
            }
            
            # 添加标准化的问题答案
            for question_id in self.question_mapping.keys():
                standardized_col = f"{question_id}_standardized"
                valid_col = f"{question_id}_valid"
                
                if row[valid_col] and pd.notna(row[standardized_col]):
                    ivs_row[question_id] = row[standardized_col]
                else:
                    ivs_row[question_id] = np.nan
            
            ivs_data.append(ivs_row)
        
        return pd.DataFrame(ivs_data)
    
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
        cultural_mapping = {
            "China": "Confucian",
            "Russian Federation": "Orthodox Europe",
            "Mexico": "Latin America", 
            "Egypt": "African-Islamic"
        }
        return cultural_mapping.get(country, "Unknown")
    
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
        """保存处理后的数据"""
        if suffix is None:
            suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存原始处理数据
        processed_file = self.processed_dir / f"multilingual_roleplay_processed_{suffix}.pkl"
        with open(processed_file, 'wb') as f:
            pickle.dump(df, f)
        
        # 保存IVS格式数据
        ivs_file = self.processed_dir / f"multilingual_roleplay_ivs_format_{suffix}.pkl"
        with open(ivs_file, 'wb') as f:
            pickle.dump(ivs_df, f)
        
        # 保存CSV格式（便于查看）
        csv_file = self.processed_dir / f"multilingual_roleplay_processed_{suffix}.csv"
        df.to_csv(csv_file, index=False, encoding='utf-8')
        
        ivs_csv_file = self.processed_dir / f"multilingual_roleplay_ivs_format_{suffix}.csv"
        ivs_df.to_csv(ivs_csv_file, index=False, encoding='utf-8')
        
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
        
        # 1. 直接加载JSON文件
        if results_file is None:
            raise ValueError("必须提供结果文件路径")
        
        with open(results_file, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        print(f"✅ 加载了 {len(raw_data)} 个国家的数据")
        
        # 2. 转换数据结构并处理
        ivs_data = []
        total_responses = 0
        
        for country, country_data in raw_data.items():
            for language, lang_data in country_data.items():
                for model_name, model_responses in lang_data.items():
                    for response_data in model_responses:
                        if 'responses' in response_data:
                            # 创建IVS格式的行
                            ivs_row = {
                                'country_code': country,
                                'Country': country,  # 添加Country字段用于可视化
                                'model_name': model_name,
                                'language': language,
                                'data_source': 'Multilingual',
                                'year': 2024,
                                'weight': 1.0,
                                'Cultural Region': self._get_cultural_region(country)  # 添加文化区域
                            }
                            
                            # 添加IVS问题的回答
                            responses = response_data['responses']
                            
                            # 处理不同的responses格式
                            if isinstance(responses, dict):
                                # 旧格式：{question_id: answer}
                                response_items = responses.items()
                            elif isinstance(responses, list):
                                # 新格式：[{question_id: ..., processed_response: ...}, ...]
                                response_items = [(item['question_id'], item.get('processed_response', item.get('raw_response', ''))) 
                                                for item in responses if isinstance(item, dict) and 'question_id' in item]
                            else:
                                print(f"⚠️ 未知的responses格式: {type(responses)}")
                                continue
                            
                            for question_id, answer in response_items:
                                if question_id in self.iv_qns:  # 使用基类的问题列表
                                    # 处理答案
                                    if isinstance(answer, str) and answer.strip():
                                        try:
                                            # 尝试转换为数字
                                            if ' ' in answer:
                                                # 处理多选题（如Y002, Y003）
                                                numeric_value = float(answer.split()[0])
                                            else:
                                                numeric_value = float(answer)
                                            ivs_row[question_id] = numeric_value
                                        except ValueError:
                                            ivs_row[question_id] = np.nan
                                    else:
                                        ivs_row[question_id] = np.nan
                            
                            ivs_data.append(ivs_row)
                            total_responses += 1
        
        print(f"✅ 处理了 {total_responses} 个回答")
        
        # 3. 创建DataFrame
        ivs_df = pd.DataFrame(ivs_data)
        print(f"✅ 创建了 {len(ivs_df)} 个IVS格式记录")
        
        # 4. 保存处理后的数据
        output_path = self.data_path / "multilingual_roleplay_processed_responses_ivs_format.pkl"
        ivs_df.to_pickle(output_path)
        print(f"💾 保存IVS格式数据到: {output_path}")
        
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
