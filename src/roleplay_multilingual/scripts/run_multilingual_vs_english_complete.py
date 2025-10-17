#!/usr/bin/env python3
"""
多语言vs英文vs真实国家文化坐标对比实验
4个国家，2个模型，每个问题3遍，使用现有的基准数据
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


class MultilingualVsEnglishExperiment:
    """多语言vs英文对比实验类"""
    
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
        self.results_dir = Path("data/results/multilingual_vs_english_experiment")
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def load_real_country_coordinates(self):
        """加载真实国家的文化坐标"""
        print("📍 加载真实国家文化坐标...")
        
        real_coords_df = pd.read_pickle("data/processed/country_scores_pca.pkl")
        
        real_coords = {}
        for country in self.test_countries.values():
            matches = real_coords_df[real_coords_df['Country'].str.contains(country, case=False, na=False)]
            if len(matches) > 0:
                row = matches.iloc[0]
                real_coords[country] = {
                    'pc1': row['PC1_rescaled'],
                    'pc2': row['PC2_rescaled']
                }
        
        print(f"✅ 加载了 {len(real_coords)} 个国家的真实坐标:")
        for country, coords in real_coords.items():
            print(f"   {country}: PC1={coords['pc1']:.3f}, PC2={coords['pc2']:.3f}")
        
        return real_coords
    
    def load_english_roleplay_coordinates(self):
        """加载英文角色扮演的文化坐标"""
        print("\\n🇺🇸 加载英文角色扮演文化坐标...")
        
        english_pca_df = pd.read_pickle("data/results/llm_responses_roleplay/corrected_pca_results.pkl")
        
        english_coords = {}
        for country in self.test_countries.values():
            for model in self.test_models:
                model_short = model.split('/')[-1]
                
                # 筛选数据
                country_mask = english_pca_df['country_name'].str.contains(country, case=False, na=False)
                model_mask = english_pca_df['model_name'].str.contains(model_short, case=False, na=False)
                
                filtered_data = english_pca_df[country_mask & model_mask]
                
                if len(filtered_data) > 0:
                    row = filtered_data.iloc[0]
                    key = f"{model}_{country}"
                    english_coords[key] = {
                        'pc1': row['PC1'],
                        'pc2': row['PC2'],
                        'model': model,
                        'country': country
                    }
        
        print(f"✅ 加载了 {len(english_coords)} 个英文角色扮演坐标:")
        for key, coords in english_coords.items():
            model_name = key.split('_')[0].split('/')[-1]
            country_name = coords['country']
            print(f"   {model_name} - {country_name}: PC1={coords['pc1']:.3f}, PC2={coords['pc2']:.3f}")
        
        return english_coords
    
    def run_multilingual_interviews(self):
        """运行多语言访谈（调用真实API）"""
        print("\\n🌍 开始多语言角色扮演访谈...")
        print(f"📋 实验配置:")
        print(f"   国家: {list(self.test_countries.values())}")
        print(f"   模型: {[m.split('/')[-1] for m in self.test_models]}")
        print(f"   重复次数: {self.repeat_count}")
        print(f"   总API调用: {len(self.test_countries) * len(self.test_models) * self.repeat_count}")
        
        all_results = []
        total_tasks = len(self.test_countries) * len(self.test_models) * self.repeat_count
        completed_tasks = 0
        
        for language, country in self.test_countries.items():
            print(f"\\n🏳️ 处理语言: {language} ({country})")
            
            for model in self.test_models:
                model_short = model.split('/')[-1]
                print(f"\\n🤖 使用模型: {model_short}")
                
                for repeat in range(self.repeat_count):
                    print(f"   第 {repeat+1}/{self.repeat_count} 次访谈...")
                    
                    try:
                        result = self.interviewer.interview_country_multilingual(
                            model_name=model,
                            country=country,
                            language=language
                        )
                        
                        # 添加标识信息
                        result['repeat_id'] = repeat + 1
                        result['task_id'] = f"{model}_{country}_{language}_{repeat+1}"
                        result['experiment_timestamp'] = datetime.now().isoformat()
                        
                        all_results.append(result)
                        completed_tasks += 1
                        
                        print(f"   ✅ 完成 ({completed_tasks}/{total_tasks}) - 成功率: {result['success_rate']:.1f}%")
                        
                        # 添加延迟避免API限制
                        time.sleep(1)
                        
                    except Exception as e:
                        print(f"   ❌ 访谈失败: {e}")
                        completed_tasks += 1
                        continue
        
        # 保存原始访谈结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        raw_results = {
            "timestamp": timestamp,
            "experiment_type": "multilingual_vs_english",
            "experiment_config": {
                "countries": self.test_countries,
                "models": self.test_models,
                "repeat_count": self.repeat_count
            },
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "success_rate": completed_tasks / total_tasks * 100,
            "results": all_results
        }
        
        raw_file = self.results_dir / f"multilingual_interviews_{timestamp}.json"
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(raw_results, f, ensure_ascii=False, indent=2)
        
        print(f"\\n💾 原始访谈结果已保存: {raw_file}")
        print(f"📊 访谈完成率: {completed_tasks}/{total_tasks} ({completed_tasks/total_tasks*100:.1f}%)")
        
        return raw_results, str(raw_file)
    
    def process_multilingual_results(self, raw_results_file):
        """处理多语言访谈结果并计算PCA坐标"""
        print("\\n🔄 处理多语言访谈结果...")
        
        # 1. 数据处理
        print("1️⃣ 处理访谈数据...")
        processing_result = self.data_processor.process_multilingual_data(raw_results_file)
        
        # 2. PCA分析
        print("2️⃣ 执行PCA分析...")
        pca_result = self.pca_analyzer.run_complete_analysis()
        
        print(f"✅ 多语言数据处理完成:")
        print(f"   处理样本数: {processing_result['stats']['total_responses']}")
        print(f"   PCA样本数: {len(pca_result['results_df'])}")
        print(f"   解释方差: PC1={pca_result['pca_results']['explained_variance_ratio'][0]:.1%}, PC2={pca_result['pca_results']['explained_variance_ratio'][1]:.1%}")
        
        return processing_result, pca_result
    
    def calculate_distances(self, multilingual_coords, real_coords, english_coords):
        """计算各种文化坐标之间的距离"""
        print("\\n📏 计算文化坐标距离...")
        
        distance_results = {
            "multilingual_vs_real": {},
            "english_vs_real": {},
            "multilingual_vs_english": {},
            "summary_statistics": {}
        }
        
        # 1. 计算多语言结果与真实坐标的距离
        print("1️⃣ 多语言 vs 真实国家...")
        ml_distances = []
        for _, row in multilingual_coords.iterrows():
            country = row['country']
            model = row['model']
            language = row['language']
            
            if country in real_coords and not (pd.isna(row['PC1']) or pd.isna(row['PC2'])):
                real_pc1 = real_coords[country]['pc1']
                real_pc2 = real_coords[country]['pc2']
                
                ml_pc1 = row['PC1']
                ml_pc2 = row['PC2']
                
                distance = np.sqrt((ml_pc1 - real_pc1)**2 + (ml_pc2 - real_pc2)**2)
                ml_distances.append(distance)
                
                key = f"{model}_{country}_{language}"
                distance_results["multilingual_vs_real"][key] = {
                    "distance": distance,
                    "multilingual": {"pc1": ml_pc1, "pc2": ml_pc2},
                    "real": {"pc1": real_pc1, "pc2": real_pc2},
                    "model": model,
                    "country": country,
                    "language": language
                }
        
        # 2. 计算英文结果与真实坐标的距离
        print("2️⃣ 英文 vs 真实国家...")
        eng_distances = []
        for key, eng_coords in english_coords.items():
            country = eng_coords['country']
            model = eng_coords['model']
            
            if country in real_coords:
                real_pc1 = real_coords[country]['pc1']
                real_pc2 = real_coords[country]['pc2']
                
                eng_pc1 = eng_coords['pc1']
                eng_pc2 = eng_coords['pc2']
                
                distance = np.sqrt((eng_pc1 - real_pc1)**2 + (eng_pc2 - real_pc2)**2)
                eng_distances.append(distance)
                
                distance_results["english_vs_real"][key] = {
                    "distance": distance,
                    "english": {"pc1": eng_pc1, "pc2": eng_pc2},
                    "real": {"pc1": real_pc1, "pc2": real_pc2},
                    "model": model,
                    "country": country
                }
        
        # 3. 计算多语言与英文结果的距离
        print("3️⃣ 多语言 vs 英文...")
        ml_vs_eng_distances = []
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
                ml_vs_eng_distances.append(distance)
                
                distance_results["multilingual_vs_english"][ml_key] = {
                    "distance": distance,
                    "multilingual": {"pc1": ml_pc1, "pc2": ml_pc2},
                    "english": {"pc1": eng_pc1, "pc2": eng_pc2},
                    "model": model,
                    "country": country,
                    "language": ml_data["language"]
                }
        
        # 4. 生成统计摘要
        if ml_distances:
            distance_results["summary_statistics"]["multilingual_vs_real"] = {
                "mean_distance": np.mean(ml_distances),
                "std_distance": np.std(ml_distances),
                "min_distance": np.min(ml_distances),
                "max_distance": np.max(ml_distances),
                "count": len(ml_distances),
                "all_distances": ml_distances
            }
        
        if eng_distances:
            distance_results["summary_statistics"]["english_vs_real"] = {
                "mean_distance": np.mean(eng_distances),
                "std_distance": np.std(eng_distances),
                "min_distance": np.min(eng_distances),
                "max_distance": np.max(eng_distances),
                "count": len(eng_distances),
                "all_distances": eng_distances
            }
        
        if ml_vs_eng_distances:
            distance_results["summary_statistics"]["multilingual_vs_english"] = {
                "mean_distance": np.mean(ml_vs_eng_distances),
                "std_distance": np.std(ml_vs_eng_distances),
                "min_distance": np.min(ml_vs_eng_distances),
                "max_distance": np.max(ml_vs_eng_distances),
                "count": len(ml_vs_eng_distances),
                "all_distances": ml_vs_eng_distances
            }
        
        print(f"✅ 距离计算完成:")
        print(f"   多语言样本: {len(ml_distances)}")
        print(f"   英文样本: {len(eng_distances)}")
        print(f"   多语言vs英文: {len(ml_vs_eng_distances)}")
        
        return distance_results
    
    def generate_comprehensive_report(self, distance_results, processing_result, pca_result):
        """生成综合对比报告"""
        print("\\n📊 生成综合对比报告...")
        
        report = {
            "experiment_info": {
                "timestamp": datetime.now().isoformat(),
                "experiment_type": "multilingual_vs_english_vs_real",
                "test_countries": self.test_countries,
                "test_models": self.test_models,
                "repeat_count": self.repeat_count,
                "total_multilingual_samples": len(pca_result['results_df']) if 'results_df' in pca_result else 0
            },
            "distance_analysis": distance_results,
            "performance_comparison": {},
            "detailed_analysis": {},
            "key_findings": [],
            "statistical_summary": {},
            "recommendations": []
        }
        
        # 性能对比分析
        ml_stats = distance_results["summary_statistics"].get("multilingual_vs_real", {})
        eng_stats = distance_results["summary_statistics"].get("english_vs_real", {})
        
        if ml_stats and eng_stats:
            ml_mean = ml_stats["mean_distance"]
            eng_mean = eng_stats["mean_distance"]
            
            improvement = eng_mean - ml_mean
            improvement_pct = (improvement / eng_mean * 100) if eng_mean > 0 else 0
            
            report["performance_comparison"] = {
                "multilingual_mean_distance": ml_mean,
                "english_mean_distance": eng_mean,
                "improvement": improvement,
                "improvement_percentage": improvement_pct,
                "better_method": "multilingual" if ml_mean < eng_mean else "english",
                "effect_size": abs(improvement) / np.sqrt((ml_stats["std_distance"]**2 + eng_stats["std_distance"]**2) / 2) if ml_stats["std_distance"] > 0 and eng_stats["std_distance"] > 0 else 0
            }
            
            # 统计摘要
            report["statistical_summary"] = {
                "multilingual_stats": {
                    "mean": ml_mean,
                    "std": ml_stats["std_distance"],
                    "min": ml_stats["min_distance"],
                    "max": ml_stats["max_distance"],
                    "count": ml_stats["count"]
                },
                "english_stats": {
                    "mean": eng_mean,
                    "std": eng_stats["std_distance"],
                    "min": eng_stats["min_distance"],
                    "max": eng_stats["max_distance"],
                    "count": eng_stats["count"]
                }
            }
            
            # 关键发现
            if improvement > 0:
                report["key_findings"].append(
                    f"🎯 多语言方法表现更好：平均距离减少 {improvement:.3f} ({improvement_pct:.1f}%)"
                )
                report["key_findings"].append(
                    f"📈 效应大小: {report['performance_comparison']['effect_size']:.3f}"
                )
            else:
                report["key_findings"].append(
                    f"⚠️ 英文方法表现更好：多语言方法距离增加 {-improvement:.3f} ({-improvement_pct:.1f}%)"
                )
            
            report["key_findings"].append(f"🌍 多语言平均距离: {ml_mean:.3f} ± {ml_stats['std_distance']:.3f}")
            report["key_findings"].append(f"🇺🇸 英文平均距离: {eng_mean:.3f} ± {eng_stats['std_distance']:.3f}")
        
        # 按语言分析
        language_performance = {}
        for key, data in distance_results["multilingual_vs_real"].items():
            language = data["language"]
            if language not in language_performance:
                language_performance[language] = []
            language_performance[language].append(data["distance"])
        
        report["detailed_analysis"]["by_language"] = {}
        for language, distances in language_performance.items():
            avg_distance = np.mean(distances)
            std_distance = np.std(distances)
            report["detailed_analysis"]["by_language"][language] = {
                "mean_distance": avg_distance,
                "std_distance": std_distance,
                "count": len(distances)
            }
            report["key_findings"].append(
                f"🗣️ {language}: 平均距离 {avg_distance:.3f} ± {std_distance:.3f} (n={len(distances)})"
            )
        
        # 按模型分析
        model_performance = {}
        for key, data in distance_results["multilingual_vs_real"].items():
            model = data["model"].split('/')[-1]
            if model not in model_performance:
                model_performance[model] = []
            model_performance[model].append(data["distance"])
        
        report["detailed_analysis"]["by_model"] = {}
        for model, distances in model_performance.items():
            avg_distance = np.mean(distances)
            std_distance = np.std(distances)
            report["detailed_analysis"]["by_model"][model] = {
                "mean_distance": avg_distance,
                "std_distance": std_distance,
                "count": len(distances)
            }
            report["key_findings"].append(
                f"🤖 {model}: 平均距离 {avg_distance:.3f} ± {std_distance:.3f} (n={len(distances)})"
            )
        
        # 建议
        better_method = report["performance_comparison"].get("better_method", "unknown")
        if better_method == "multilingual":
            report["recommendations"] = [
                "✅ 建议在跨文化研究中优先使用多语言方法",
                "🔬 多语言方法在文化价值观模拟方面表现更准确",
                "📈 可以扩大实验规模进一步验证多语言优势",
                "🎯 重点关注表现最好的语言-模型组合",
                "📚 研究多语言优势的理论机制"
            ]
        else:
            report["recommendations"] = [
                "⚠️ 当前多语言方法仍需改进",
                "🔍 深入分析多语言方法表现不佳的原因",
                "📝 优化多语言提示词和文化背景描述",
                "🧪 尝试不同的多语言实现策略",
                "📊 增加样本量提高统计可靠性"
            ]
        
        return report
    
    def save_all_results(self, distance_results, report, processing_result, pca_result):
        """保存所有实验结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存距离分析结果
        distance_file = self.results_dir / f"distance_analysis_{timestamp}.json"
        with open(distance_file, 'w', encoding='utf-8') as f:
            json.dump(distance_results, f, ensure_ascii=False, indent=2, default=str)
        
        # 保存综合报告
        report_file = self.results_dir / f"comprehensive_report_{timestamp}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        # 保存PCA结果
        pca_file = self.results_dir / f"multilingual_pca_results_{timestamp}.pkl"
        with open(pca_file, 'wb') as f:
            pickle.dump(pca_result, f)
        
        print(f"\\n💾 所有结果已保存:")
        print(f"   📏 距离分析: {distance_file}")
        print(f"   📊 综合报告: {report_file}")
        print(f"   🔍 PCA结果: {pca_file}")
        
        return {
            "distance_file": distance_file,
            "report_file": report_file,
            "pca_file": pca_file
        }
    
    def print_final_summary(self, report):
        """打印最终实验摘要"""
        print("\\n" + "=" * 80)
        print("🎯 多语言 vs 英文 vs 真实国家 - 文化坐标对比实验结果")
        print("=" * 80)
        
        # 实验配置
        config = report["experiment_info"]
        print(f"📋 实验配置:")
        print(f"   测试国家: {list(config['test_countries'].values())}")
        print(f"   测试模型: {[m.split('/')[-1] for m in config['test_models']]}")
        print(f"   重复次数: {config['repeat_count']}")
        print(f"   多语言样本: {config['total_multilingual_samples']}")
        
        # 主要结果
        if "performance_comparison" in report:
            perf = report["performance_comparison"]
            print(f"\\n🏆 主要结果:")
            print(f"   多语言平均距离: {perf['multilingual_mean_distance']:.3f}")
            print(f"   英文平均距离: {perf['english_mean_distance']:.3f}")
            print(f"   改进幅度: {perf['improvement']:.3f} ({perf['improvement_percentage']:.1f}%)")
            print(f"   更好的方法: {perf['better_method']}")
            print(f"   效应大小: {perf['effect_size']:.3f}")
        
        # 关键发现
        print(f"\\n🔍 关键发现:")
        for finding in report["key_findings"][:8]:  # 显示前8个发现
            print(f"   {finding}")
        
        # 建议
        print(f"\\n💡 主要建议:")
        for rec in report["recommendations"][:3]:  # 显示前3个建议
            print(f"   {rec}")
        
        print("\\n✅ 实验完成！详细结果请查看保存的文件。")
    
    def run_complete_experiment(self):
        """运行完整的对比实验"""
        print("🧪 多语言 vs 英文 vs 真实国家文化坐标对比实验")
        print("=" * 80)
        print("📝 实验目标: 比较多语言角色扮演与英文角色扮演在文化价值观模拟准确性上的差异")
        print("=" * 80)
        
        try:
            # 1. 加载基准数据
            real_coords = self.load_real_country_coordinates()
            english_coords = self.load_english_roleplay_coordinates()
            
            # 2. 运行多语言访谈（真实API调用）
            raw_results, raw_file = self.run_multilingual_interviews()
            
            # 3. 处理多语言结果
            processing_result, pca_result = self.process_multilingual_results(raw_file)
            
            # 4. 计算所有距离
            multilingual_coords = pca_result['results_df']
            distance_results = self.calculate_distances(
                multilingual_coords, real_coords, english_coords
            )
            
            # 5. 生成综合报告
            report = self.generate_comprehensive_report(
                distance_results, processing_result, pca_result
            )
            
            # 6. 保存所有结果
            file_paths = self.save_all_results(
                distance_results, report, processing_result, pca_result
            )
            
            # 7. 显示最终摘要
            self.print_final_summary(report)
            
            return {
                "success": True,
                "file_paths": file_paths,
                "report": report,
                "summary": {
                    "multilingual_samples": len(multilingual_coords),
                    "english_samples": len(english_coords),
                    "real_countries": len(real_coords),
                    "better_method": report["performance_comparison"].get("better_method", "unknown")
                }
            }
            
        except Exception as e:
            print(f"❌ 实验失败: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}


def main():
    """主函数"""
    print("🚀 启动多语言vs英文文化坐标对比实验")
    
    # 检查API密钥
    if not os.getenv('OPENROUTER_API_KEY'):
        print("❌ 请设置 OPENROUTER_API_KEY 环境变量")
        print("   export OPENROUTER_API_KEY=your_api_key")
        return
    
    experiment = MultilingualVsEnglishExperiment()
    
    # 显示实验计划
    total_calls = len(experiment.test_countries) * len(experiment.test_models) * experiment.repeat_count
    print(f"\\n📊 实验计划:")
    print(f"   国家数: {len(experiment.test_countries)}")
    print(f"   模型数: {len(experiment.test_models)}")
    print(f"   重复次数: {experiment.repeat_count}")
    print(f"   总API调用: {total_calls}")
    print(f"   预计费用: ~${total_calls * 0.01:.2f} (估算)")
    
    print("\\n⚠️  注意: 这将进行真实的API调用，可能产生费用")
    response = input("是否继续实验? (y/n): ").lower().strip()
    
    if response != 'y':
        print("❌ 实验已取消")
        return
    
    # 运行实验
    print("\\n🎬 开始实验...")
    result = experiment.run_complete_experiment()
    
    if result["success"]:
        print("\\n🎉 实验成功完成！")
        print(f"\\n📁 结果文件:")
        for key, path in result["file_paths"].items():
            print(f"   {key}: {path}")
        
        summary = result["summary"]
        print(f"\\n📈 实验摘要:")
        print(f"   多语言样本: {summary['multilingual_samples']}")
        print(f"   英文样本: {summary['english_samples']}")
        print(f"   真实国家: {summary['real_countries']}")
        print(f"   更好的方法: {summary['better_method']}")
        
    else:
        print(f"\\n❌ 实验失败: {result['error']}")


if __name__ == "__main__":
    main()
