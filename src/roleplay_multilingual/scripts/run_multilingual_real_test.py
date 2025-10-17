#!/usr/bin/env python3
"""
多语言角色扮演真实测试脚本
测试4个国家，2个模型，每个问题3遍
与真实国家文化坐标和英文结果进行对比
"""

import sys
import os
import json
import pickle
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import time

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from src.multilingual.multilingual_roleplay_interview import MultilingualRoleplayInterview
from src.multilingual.multilingual_roleplay_data_processor import MultilingualRoleplayDataProcessor
from src.multilingual.multilingual_roleplay_pca_analysis import MultilingualRoleplayPCAAnalysis


class MultilingualTestExperiment:
    """多语言测试实验类"""
    
    def __init__(self):
        self.interviewer = MultilingualRoleplayInterview()
        self.data_processor = MultilingualRoleplayDataProcessor()
        self.pca_analyzer = MultilingualRoleplayPCAAnalysis()
        
        # 测试配置
        self.test_countries = {
            "zh-cn": "China",
            "ru": "Russian Federation", 
            "es-la": "Mexico",
            "ar": "Egypt"
        }
        
        # 选择2个模型（除了Claude）
        self.test_models = [
            "openai/gpt-4o-mini",
            "google/gemini-2.0-flash-001"
        ]
        
        self.repeat_count = 3  # 每个问题问3遍
        
        # 结果目录
        self.results_dir = Path("data/results/multilingual_test")
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def load_real_country_coordinates(self):
        """加载真实国家的文化坐标"""
        print("加载真实国家文化坐标...")
        
        # 尝试多个可能的文件路径
        possible_files = [
            "data/processed/country_scores_pca.pkl",
            "data/country_scores_pca.pkl",
            "data/processed/country_scores_pca.json",
            "data/country_scores_pca.json"
        ]
        
        real_coords = {}
        
        for file_path in possible_files:
            if Path(file_path).exists():
                print(f"找到真实坐标文件: {file_path}")
                
                if file_path.endswith('.pkl'):
                    with open(file_path, 'rb') as f:
                        data = pickle.load(f)
                else:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                
                # 提取目标国家的坐标
                for country in self.test_countries.values():
                    if country in data:
                        coords = data[country]
                        if isinstance(coords, dict):
                            real_coords[country] = {
                                'pc1': coords.get('pc1', coords.get('PC1', 0)),
                                'pc2': coords.get('pc2', coords.get('PC2', 0))
                            }
                        elif isinstance(coords, (list, tuple)) and len(coords) >= 2:
                            real_coords[country] = {
                                'pc1': coords[0],
                                'pc2': coords[1]
                            }
                
                break
        
        if not real_coords:
            print("警告: 未找到真实国家坐标数据")
            # 使用Inglehart-Welzel地图的近似坐标作为参考
            real_coords = {
                "China": {'pc1': -0.5, 'pc2': 0.3},
                "Russian Federation": {'pc1': 0.8, 'pc2': -0.5},
                "Mexico": {'pc1': -0.8, 'pc2': -0.3},
                "Egypt": {'pc1': -1.2, 'pc2': -0.8}
            }
            print("使用Inglehart-Welzel地图参考坐标")
        
        print(f"加载了 {len(real_coords)} 个国家的真实坐标")
        for country, coords in real_coords.items():
            print(f"  {country}: PC1={coords['pc1']:.3f}, PC2={coords['pc2']:.3f}")
        
        return real_coords
    
    def load_english_roleplay_coordinates(self):
        """加载英文角色扮演的文化坐标"""
        print("加载英文角色扮演坐标...")
        
        # 查找英文角色扮演的PCA结果
        possible_files = [
            "data/results/llm_responses_roleplay/roleplay_pca_results.pkl",
            "data/roleplay_pca_results.pkl",
            "data/results/roleplay_pca_results.pkl"
        ]
        
        english_coords = {}
        
        for file_path in possible_files:
            if Path(file_path).exists():
                print(f"找到英文角色扮演坐标文件: {file_path}")
                
                with open(file_path, 'rb') as f:
                    data = pickle.load(f)
                
                # 提取目标国家和模型的坐标
                if isinstance(data, pd.DataFrame):
                    df = data
                elif isinstance(data, dict) and 'results_df' in data:
                    df = data['results_df']
                else:
                    print("英文坐标数据格式不识别")
                    continue
                
                # 筛选目标国家和模型
                for country in self.test_countries.values():
                    for model in self.test_models:
                        # 尝试不同的匹配方式
                        country_matches = df['country'].str.contains(country, case=False, na=False)
                        model_matches = df['model'].str.contains(model.split('/')[-1], case=False, na=False)
                        
                        matched_rows = df[country_matches & model_matches]
                        
                        if len(matched_rows) > 0:
                            row = matched_rows.iloc[0]
                            key = f"{model}_{country}"
                            english_coords[key] = {
                                'pc1': row.get('PC1', row.get('pc1', 0)),
                                'pc2': row.get('PC2', row.get('pc2', 0))
                            }
                
                break
        
        if not english_coords:
            print("警告: 未找到英文角色扮演坐标，将在实验后进行对比")
        else:
            print(f"加载了 {len(english_coords)} 个英文角色扮演坐标")
            for key, coords in english_coords.items():
                print(f"  {key}: PC1={coords['pc1']:.3f}, PC2={coords['pc2']:.3f}")
        
        return english_coords
    
    def run_multilingual_interviews(self):
        """运行多语言访谈"""
        print("\\n=== 开始多语言角色扮演访谈 ===")
        print(f"测试配置:")
        print(f"  国家: {list(self.test_countries.values())}")
        print(f"  模型: {self.test_models}")
        print(f"  重复次数: {self.repeat_count}")
        
        all_results = []
        total_tasks = len(self.test_countries) * len(self.test_models) * self.repeat_count
        completed_tasks = 0
        
        for language, country in self.test_countries.items():
            for model in self.test_models:
                for repeat in range(self.repeat_count):
                    print(f"\\n进行访谈: {model} -> {country} ({language}) [第{repeat+1}次]")
                    
                    try:
                        result = self.interviewer.interview_country_multilingual(
                            model_name=model,
                            country=country,
                            language=language
                        )
                        
                        # 添加重复次数标识
                        result['repeat_id'] = repeat + 1
                        result['task_id'] = f"{model}_{country}_{language}_{repeat+1}"
                        
                        all_results.append(result)
                        completed_tasks += 1
                        
                        print(f"✅ 完成 ({completed_tasks}/{total_tasks}) - 成功率: {result['success_rate']:.1f}%")
                        
                        # 添加延迟避免API限制
                        time.sleep(2)
                        
                    except Exception as e:
                        print(f"❌ 访谈失败: {e}")
                        completed_tasks += 1
                        continue
        
        # 保存原始结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        raw_results = {
            "timestamp": timestamp,
            "experiment_config": {
                "countries": self.test_countries,
                "models": self.test_models,
                "repeat_count": self.repeat_count
            },
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "results": all_results
        }
        
        raw_file = self.results_dir / f"multilingual_test_raw_{timestamp}.json"
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(raw_results, f, ensure_ascii=False, indent=2)
        
        print(f"\\n原始结果已保存: {raw_file}")
        return raw_results, str(raw_file)
    
    def process_and_analyze_results(self, raw_results_file):
        """处理和分析结果"""
        print("\\n=== 处理和分析结果 ===")
        
        # 1. 数据处理
        print("1. 处理访谈数据...")
        processing_result = self.data_processor.process_multilingual_data(raw_results_file)
        
        # 2. PCA分析
        print("2. 执行PCA分析...")
        pca_result = self.pca_analyzer.run_complete_analysis()
        
        return processing_result, pca_result
    
    def calculate_distances(self, multilingual_coords, real_coords, english_coords):
        """计算文化坐标距离"""
        print("\\n=== 计算文化坐标距离 ===")
        
        distance_results = {
            "multilingual_vs_real": {},
            "english_vs_real": {},
            "multilingual_vs_english": {},
            "summary": {}
        }
        
        # 计算多语言结果与真实坐标的距离
        for index, row in multilingual_coords.iterrows():
            country = row['country']
            model = row['model']
            language = row['language']
            
            if country in real_coords:
                real_pc1 = real_coords[country]['pc1']
                real_pc2 = real_coords[country]['pc2']
                
                ml_pc1 = row['PC1']
                ml_pc2 = row['PC2']
                
                if not (pd.isna(ml_pc1) or pd.isna(ml_pc2)):
                    distance = np.sqrt((ml_pc1 - real_pc1)**2 + (ml_pc2 - real_pc2)**2)
                    
                    key = f"{model}_{country}_{language}"
                    distance_results["multilingual_vs_real"][key] = {
                        "distance": distance,
                        "multilingual": {"pc1": ml_pc1, "pc2": ml_pc2},
                        "real": {"pc1": real_pc1, "pc2": real_pc2},
                        "model": model,
                        "country": country,
                        "language": language
                    }
        
        # 计算英文结果与真实坐标的距离
        for key, eng_coords in english_coords.items():
            model, country = key.split('_', 1)
            
            if country in real_coords:
                real_pc1 = real_coords[country]['pc1']
                real_pc2 = real_coords[country]['pc2']
                
                eng_pc1 = eng_coords['pc1']
                eng_pc2 = eng_coords['pc2']
                
                distance = np.sqrt((eng_pc1 - real_pc1)**2 + (eng_pc2 - real_pc2)**2)
                
                distance_results["english_vs_real"][key] = {
                    "distance": distance,
                    "english": {"pc1": eng_pc1, "pc2": eng_pc2},
                    "real": {"pc1": real_pc1, "pc2": real_pc2},
                    "model": model,
                    "country": country
                }
        
        # 计算多语言与英文结果的距离
        for ml_key, ml_data in distance_results["multilingual_vs_real"].items():
            model = ml_data["model"]
            country = ml_data["country"]
            eng_key = f"{model}_{country}"
            
            if eng_key in english_coords:
                ml_pc1 = ml_data["multilingual"]["pc1"]
                ml_pc2 = ml_data["multilingual"]["pc2"]
                eng_pc1 = english_coords[eng_key]["pc1"]
                eng_pc2 = english_coords[eng_key]["pc2"]
                
                distance = np.sqrt((ml_pc1 - eng_pc1)**2 + (ml_pc2 - eng_pc2)**2)
                
                distance_results["multilingual_vs_english"][ml_key] = {
                    "distance": distance,
                    "multilingual": {"pc1": ml_pc1, "pc2": ml_pc2},
                    "english": {"pc1": eng_pc1, "pc2": eng_pc2}
                }
        
        # 生成摘要统计
        if distance_results["multilingual_vs_real"]:
            ml_distances = [d["distance"] for d in distance_results["multilingual_vs_real"].values()]
            distance_results["summary"]["multilingual_vs_real"] = {
                "mean_distance": np.mean(ml_distances),
                "std_distance": np.std(ml_distances),
                "min_distance": np.min(ml_distances),
                "max_distance": np.max(ml_distances),
                "count": len(ml_distances)
            }
        
        if distance_results["english_vs_real"]:
            eng_distances = [d["distance"] for d in distance_results["english_vs_real"].values()]
            distance_results["summary"]["english_vs_real"] = {
                "mean_distance": np.mean(eng_distances),
                "std_distance": np.std(eng_distances),
                "min_distance": np.min(eng_distances),
                "max_distance": np.max(eng_distances),
                "count": len(eng_distances)
            }
        
        return distance_results
    
    def generate_comparison_report(self, distance_results, processing_result, pca_result):
        """生成对比报告"""
        print("\\n=== 生成对比报告 ===")
        
        report = {
            "experiment_summary": {
                "timestamp": datetime.now().isoformat(),
                "test_countries": self.test_countries,
                "test_models": self.test_models,
                "repeat_count": self.repeat_count,
                "total_samples": len(pca_result['results_df']) if 'results_df' in pca_result else 0
            },
            "distance_analysis": distance_results,
            "performance_comparison": {},
            "key_findings": [],
            "recommendations": []
        }
        
        # 性能对比分析
        ml_summary = distance_results["summary"].get("multilingual_vs_real", {})
        eng_summary = distance_results["summary"].get("english_vs_real", {})
        
        if ml_summary and eng_summary:
            ml_mean = ml_summary["mean_distance"]
            eng_mean = eng_summary["mean_distance"]
            
            report["performance_comparison"] = {
                "multilingual_mean_distance": ml_mean,
                "english_mean_distance": eng_mean,
                "improvement": eng_mean - ml_mean,
                "improvement_percentage": ((eng_mean - ml_mean) / eng_mean * 100) if eng_mean > 0 else 0,
                "better_method": "multilingual" if ml_mean < eng_mean else "english"
            }
            
            # 关键发现
            if ml_mean < eng_mean:
                report["key_findings"].append(
                    f"多语言方法表现更好，平均距离减少 {eng_mean - ml_mean:.3f} ({((eng_mean - ml_mean) / eng_mean * 100):.1f}%)"
                )
            else:
                report["key_findings"].append(
                    f"英文方法表现更好，多语言方法距离增加 {ml_mean - eng_mean:.3f} ({((ml_mean - eng_mean) / eng_mean * 100):.1f}%)"
                )
        
        # 按语言分析
        language_performance = {}
        for key, data in distance_results["multilingual_vs_real"].items():
            language = data["language"]
            if language not in language_performance:
                language_performance[language] = []
            language_performance[language].append(data["distance"])
        
        for language, distances in language_performance.items():
            report["key_findings"].append(
                f"{language}: 平均距离 {np.mean(distances):.3f} (样本数: {len(distances)})"
            )
        
        # 按模型分析
        model_performance = {}
        for key, data in distance_results["multilingual_vs_real"].items():
            model = data["model"]
            if model not in model_performance:
                model_performance[model] = []
            model_performance[model].append(data["distance"])
        
        for model, distances in model_performance.items():
            report["key_findings"].append(
                f"{model}: 平均距离 {np.mean(distances):.3f} (样本数: {len(distances)})"
            )
        
        # 建议
        report["recommendations"] = [
            "基于实验结果，建议采用表现更好的方法进行大规模实验",
            "对表现较差的语言-模型组合进行prompt优化",
            "扩大样本量以提高统计显著性",
            "考虑加入更多语言和模型进行对比"
        ]
        
        return report
    
    def save_results(self, distance_results, report):
        """保存结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存距离分析结果
        distance_file = self.results_dir / f"distance_analysis_{timestamp}.json"
        with open(distance_file, 'w', encoding='utf-8') as f:
            json.dump(distance_results, f, ensure_ascii=False, indent=2, default=str)
        
        # 保存对比报告
        report_file = self.results_dir / f"comparison_report_{timestamp}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"结果已保存:")
        print(f"  距离分析: {distance_file}")
        print(f"  对比报告: {report_file}")
        
        return distance_file, report_file
    
    def run_complete_experiment(self):
        """运行完整实验"""
        print("🧪 多语言角色扮演真实测试实验")
        print("=" * 60)
        
        try:
            # 1. 加载基准数据
            real_coords = self.load_real_country_coordinates()
            english_coords = self.load_english_roleplay_coordinates()
            
            # 2. 运行多语言访谈
            raw_results, raw_file = self.run_multilingual_interviews()
            
            # 3. 处理和分析结果
            processing_result, pca_result = self.process_and_analyze_results(raw_file)
            
            # 4. 计算距离
            multilingual_coords = pca_result['results_df']
            distance_results = self.calculate_distances(
                multilingual_coords, real_coords, english_coords
            )
            
            # 5. 生成对比报告
            report = self.generate_comparison_report(
                distance_results, processing_result, pca_result
            )
            
            # 6. 保存结果
            distance_file, report_file = self.save_results(distance_results, report)
            
            # 7. 显示结果摘要
            self.print_results_summary(report)
            
            return {
                "success": True,
                "distance_file": distance_file,
                "report_file": report_file,
                "report": report
            }
            
        except Exception as e:
            print(f"❌ 实验失败: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    def print_results_summary(self, report):
        """打印结果摘要"""
        print("\\n" + "=" * 60)
        print("🎯 实验结果摘要")
        print("=" * 60)
        
        # 实验配置
        config = report["experiment_summary"]
        print(f"测试国家: {list(config['test_countries'].values())}")
        print(f"测试模型: {config['test_models']}")
        print(f"重复次数: {config['repeat_count']}")
        print(f"总样本数: {config['total_samples']}")
        
        # 性能对比
        if "performance_comparison" in report:
            perf = report["performance_comparison"]
            print(f"\\n📊 性能对比:")
            print(f"  多语言平均距离: {perf['multilingual_mean_distance']:.3f}")
            print(f"  英文平均距离: {perf['english_mean_distance']:.3f}")
            print(f"  改进幅度: {perf['improvement']:.3f} ({perf['improvement_percentage']:.1f}%)")
            print(f"  更好的方法: {perf['better_method']}")
        
        # 关键发现
        print(f"\\n🔍 关键发现:")
        for finding in report["key_findings"]:
            print(f"  • {finding}")
        
        print("\\n✅ 实验完成！详细结果请查看保存的文件。")


def main():
    """主函数"""
    experiment = MultilingualTestExperiment()
    
    # 检查API密钥
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        return
    
    print("⚠️  注意: 这将进行真实的API调用，可能产生费用")
    response = input("是否继续? (y/n): ").lower().strip()
    
    if response != 'y':
        print("实验已取消")
        return
    
    # 运行实验
    result = experiment.run_complete_experiment()
    
    if result["success"]:
        print("\\n🎉 实验成功完成！")
    else:
        print(f"\\n❌ 实验失败: {result['error']}")


if __name__ == "__main__":
    main()







