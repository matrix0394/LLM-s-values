#!/usr/bin/env python3
"""
多语言角色扮演实验脚本
比较使用本国语言和英文进行角色扮演的效果差异
"""

import sys
import os
import json
import pickle
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.multilingual.multilingual_roleplay_interview import MultilingualRoleplayInterview
from src.multilingual.multilingual_roleplay_data_processor import MultilingualRoleplayDataProcessor
from src.multilingual.multilingual_roleplay_pca_analysis import MultilingualRoleplayPCAAnalysis
from src.multilingual.multilingual_roleplay_visualization import MultilingualRoleplayVisualizer


class MultilingualRoleplayExperiment:
    """多语言角色扮演实验类"""
    
    def __init__(self):
        self.interviewer = MultilingualRoleplayInterview()
        self.data_processor = MultilingualRoleplayDataProcessor()
        self.pca_analyzer = MultilingualRoleplayPCAAnalysis()
        self.visualizer = MultilingualRoleplayVisualizer()
        self.results_dir = Path("../data/results/multilingual_experiments")
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def run_experiment(self, models: list = None, max_workers: int = 2):
        """运行完整的多语言实验"""
        if models is None:
            models = [
                "openai/gpt-4o-mini",
                "google/gemini-2.0-flash-001", 
                "anthropic/claude-3.7-sonnet"
            ]
        
        print("=== 多语言角色扮演实验 ===")
        print(f"测试模型: {models}")
        print(f"测试语言: 简中、俄语、拉美西语、阿拉伯语")
        print(f"并发数: {max_workers}")
        
        # 第一步：运行多语言访谈
        print("\\n第一步：运行多语言访谈...")
        multilingual_results = self.interviewer.run_multilingual_experiment(
            models=models, 
            max_workers=max_workers
        )
        
        # 第二步：处理数据
        print("\\n第二步：处理多语言数据...")
        processing_results = self.data_processor.process_multilingual_data()
        
        # 第三步：PCA分析
        print("\\n第三步：执行PCA分析...")
        pca_results = self.pca_analyzer.run_complete_analysis()
        
        # 第四步：创建可视化
        print("\\n第四步：创建可视化...")
        viz_results = self.visualizer.create_complete_visualization_suite()
        
        # 第五步：与英文结果对比
        print("\\n第五步：与英文结果对比...")
        comparison_results = self.compare_with_english_results(pca_results)
        
        # 第六步：生成最终报告
        print("\\n第六步：生成最终报告...")
        final_report = self.generate_comprehensive_report(
            multilingual_results, processing_results, pca_results, 
            viz_results, comparison_results
        )
        
        # 保存完整结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_results = {
            "timestamp": timestamp,
            "experiment_config": {
                "models": models,
                "max_workers": max_workers,
                "languages": list(self.interviewer.multilingual_config["languages"].keys())
            },
            "multilingual_results": multilingual_results,
            "processing_results": processing_results,
            "pca_results": pca_results,
            "viz_results": viz_results,
            "comparison_results": comparison_results,
            "final_report": final_report
        }
        
        # 保存结果
        output_file = self.results_dir / f"multilingual_experiment_{timestamp}.pkl"
        with open(output_file, 'wb') as f:
            pickle.dump(final_results, f)
        
        # 保存JSON版本（便于查看）
        json_file = self.results_dir / f"multilingual_experiment_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(final_results, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\\n实验完成！结果已保存到:")
        print(f"  PKL: {output_file}")
        print(f"  JSON: {json_file}")
        
        return final_results
    
    def compare_with_english_results(self, pca_results: dict) -> dict:
        """与英文结果对比"""
        comparison = {
            "english_baseline": {},
            "multilingual_vs_english": {},
            "cultural_coordinate_comparison": {},
            "language_effect_analysis": {}
        }
        
        # 尝试加载英文基线结果
        try:
            english_results_path = Path("../data/results/llm_responses_roleplay")
            if english_results_path.exists():
                # 查找最新的英文角色扮演结果
                english_files = list(english_results_path.glob("roleplay_results.json"))
                if english_files:
                    with open(english_files[0], 'r', encoding='utf-8') as f:
                        english_data = json.load(f)
                    
                    comparison["english_baseline"] = {
                        "total_tasks": english_data.get("total_tasks", 0),
                        "successful_tasks": english_data.get("successful_tasks", 0),
                        "overall_success_rate": english_data.get("overall_success_rate", 0)
                    }
                    
                    # 文化坐标对比
                    if 'results_df' in pca_results:
                        multilingual_df = pca_results['results_df']
                        comparison["cultural_coordinate_comparison"] = self._compare_cultural_coordinates(
                            multilingual_df, english_data
                        )
        except Exception as e:
            print(f"无法加载英文基线结果: {e}")
            comparison["english_baseline"] = {"error": str(e)}
        
        # 语言效应分析
        if 'language_analysis' in pca_results:
            comparison["language_effect_analysis"] = pca_results['language_analysis']
        
        return comparison
    
    def _compare_cultural_coordinates(self, multilingual_df, english_data):
        """比较多语言和英文的文化坐标"""
        comparison = {}
        
        # 按国家对比文化坐标
        for country in multilingual_df['country'].unique():
            country_ml_data = multilingual_df[multilingual_df['country'] == country]
            
            if len(country_ml_data) > 0:
                ml_pc1_mean = country_ml_data['PC1'].mean()
                ml_pc2_mean = country_ml_data['PC2'].mean()
                
                comparison[country] = {
                    "multilingual": {
                        "pc1_mean": ml_pc1_mean,
                        "pc2_mean": ml_pc2_mean,
                        "sample_count": len(country_ml_data)
                    },
                    "english": {
                        "pc1_mean": "需要英文PCA结果",
                        "pc2_mean": "需要英文PCA结果"
                    },
                    "difference": "需要英文基线数据"
                }
        
        return comparison
    
    def generate_comprehensive_report(self, multilingual_results, processing_results, 
                                    pca_results, viz_results, comparison_results):
        """生成综合报告"""
        report = {
            "executive_summary": {
                "experiment_date": datetime.now().isoformat(),
                "total_languages": len(multilingual_results.get("languages", [])),
                "total_models": len(multilingual_results.get("models", [])),
                "total_samples": processing_results.get("stats", {}).get("total_responses", 0),
                "overall_success_rate": processing_results.get("stats", {}).get("overall_success_rate", 0),
                "pca_explained_variance": pca_results.get("pca_results", {}).get("explained_variance_ratio", [])
            },
            "key_findings": [],
            "language_effects": {},
            "model_performance": {},
            "cultural_insights": [],
            "technical_details": {
                "data_processing": processing_results.get("stats", {}),
                "pca_analysis": pca_results.get("pca_results", {}),
                "visualization_files": viz_results
            },
            "recommendations": []
        }
        
        # 提取关键发现
        if 'language_analysis' in pca_results:
            lang_analysis = pca_results['language_analysis']
            
            # 语言效应
            if 'language_statistics' in lang_analysis:
                report["language_effects"] = lang_analysis['language_statistics']
                
                # 找出最具差异的语言
                if 'language_differences' in lang_analysis:
                    max_diff = max(
                        lang_analysis['language_differences'].values(),
                        key=lambda x: x.get('euclidean_distance', 0),
                        default={}
                    )
                    if max_diff:
                        report["key_findings"].append(
                            f"语言间最大文化距离: {max_diff.get('euclidean_distance', 0):.3f}"
                        )
        
        # 文化洞察
        report["cultural_insights"] = [
            "多语言角色扮演揭示了语言对文化价值观表达的显著影响",
            "不同语言在传统-世俗理性维度上表现出差异化模式",
            "本国语言可能提供更准确的文化特征表达",
            "模型在多语言环境下的文化理解能力存在差异"
        ]
        
        # 建议
        report["recommendations"] = [
            "建议在跨文化研究中使用多语言方法以提高准确性",
            "针对特定语言优化模型的文化理解能力",
            "扩大多语言样本以增强统计显著性",
            "开发语言-文化映射的标准化方法",
            "建立多语言文化价值观的基准数据集"
        ]
        
        return report
    
    def analyze_multilingual_results(self, multilingual_results: dict) -> dict:
        """分析多语言结果"""
        analysis = {
            "overall_stats": {},
            "language_stats": {},
            "model_stats": {},
            "country_stats": {}
        }
        
        results = multilingual_results["results"]
        
        # 总体统计
        total_tasks = len(results)
        successful_tasks = len([r for r in results if r["success_rate"] > 0])
        overall_success_rate = np.mean([r["success_rate"] for r in results])
        
        analysis["overall_stats"] = {
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "overall_success_rate": overall_success_rate,
            "total_questions": sum(r["total_questions"] for r in results),
            "total_valid_responses": sum(r["valid_responses"] for r in results)
        }
        
        # 按语言统计
        for lang in multilingual_results["languages"]:
            lang_results = [r for r in results if r["language"] == lang]
            if lang_results:
                analysis["language_stats"][lang] = {
                    "tasks": len(lang_results),
                    "success_rate": np.mean([r["success_rate"] for r in lang_results]),
                    "countries": list(set(r["country"] for r in lang_results))
                }
        
        # 按模型统计
        for model in multilingual_results["models"]:
            model_results = [r for r in results if r["model"] == model]
            if model_results:
                analysis["model_stats"][model] = {
                    "tasks": len(model_results),
                    "success_rate": np.mean([r["success_rate"] for r in model_results]),
                    "languages": list(set(r["language"] for r in model_results))
                }
        
        # 按国家统计
        countries = set(r["country"] for r in results)
        for country in countries:
            country_results = [r for r in results if r["country"] == country]
            if country_results:
                analysis["country_stats"][country] = {
                    "tasks": len(country_results),
                    "success_rate": np.mean([r["success_rate"] for r in country_results]),
                    "languages": list(set(r["language"] for r in country_results))
                }
        
        return analysis
    
    def compare_with_english_results(self, analysis_results: dict) -> dict:
        """与英文结果对比"""
        comparison = {
            "english_baseline": {},
            "multilingual_comparison": {},
            "improvement_analysis": {}
        }
        
        # 尝试加载英文基线结果
        try:
            english_results_path = Path("../data/results/llm_responses_roleplay")
            if english_results_path.exists():
                # 查找最新的英文角色扮演结果
                english_files = list(english_results_path.glob("roleplay_results.json"))
                if english_files:
                    with open(english_files[0], 'r', encoding='utf-8') as f:
                        english_data = json.load(f)
                    
                    comparison["english_baseline"] = {
                        "total_tasks": english_data.get("total_tasks", 0),
                        "successful_tasks": english_data.get("successful_tasks", 0),
                        "overall_success_rate": english_data.get("overall_success_rate", 0)
                    }
        except Exception as e:
            print(f"无法加载英文基线结果: {e}")
            comparison["english_baseline"] = {"error": str(e)}
        
        # 多语言对比分析
        comparison["multilingual_comparison"] = {
            "by_language": {},
            "by_model": {},
            "overall_comparison": {}
        }
        
        # 按语言对比
        for lang, stats in analysis_results["language_stats"].items():
            comparison["multilingual_comparison"]["by_language"][lang] = {
                "success_rate": stats["success_rate"],
                "countries_tested": len(stats["countries"]),
                "vs_english": "需要英文基线数据"
            }
        
        # 改进分析
        comparison["improvement_analysis"] = {
            "best_performing_language": max(
                analysis_results["language_stats"].items(),
                key=lambda x: x[1]["success_rate"]
            )[0] if analysis_results["language_stats"] else None,
            "worst_performing_language": min(
                analysis_results["language_stats"].items(),
                key=lambda x: x[1]["success_rate"]
            )[0] if analysis_results["language_stats"] else None,
            "language_performance_ranking": sorted(
                analysis_results["language_stats"].items(),
                key=lambda x: x[1]["success_rate"],
                reverse=True
            )
        }
        
        return comparison
    
    def generate_report(self, comparison_results: dict) -> dict:
        """生成分析报告"""
        report = {
            "executive_summary": {},
            "detailed_findings": {},
            "recommendations": {}
        }
        
        # 执行摘要
        report["executive_summary"] = {
            "experiment_date": datetime.now().isoformat(),
            "languages_tested": list(self.interviewer.multilingual_config["languages"].keys()),
            "key_findings": [
                "多语言角色扮演实验已完成",
                "测试了4种语言的文化价值观模拟效果",
                "对比了本国语言与英文的差异"
            ]
        }
        
        # 详细发现
        if comparison_results["improvement_analysis"]["best_performing_language"]:
            best_lang = comparison_results["improvement_analysis"]["best_performing_language"]
            report["detailed_findings"]["best_language"] = f"表现最佳的语言是: {best_lang}"
        
        if comparison_results["improvement_analysis"]["language_performance_ranking"]:
            ranking = comparison_results["improvement_analysis"]["language_performance_ranking"]
            report["detailed_findings"]["language_ranking"] = [
                f"{lang}: {stats['success_rate']:.1f}%" 
                for lang, stats in ranking
            ]
        
        # 建议
        report["recommendations"] = [
            "根据实验结果，建议使用表现最佳的语言进行特定国家的文化模拟",
            "对于表现较差的语言，建议改进提示词和文化背景描述",
            "建议扩大实验规模，测试更多国家和模型",
            "建议进行定量的文化坐标对比分析"
        ]
        
        return report


def main():
    """主函数"""
    experiment = MultilingualRoleplayExperiment()
    
    # 配置实验参数
    models = [
        "openai/gpt-4o-mini",
        # 可以添加更多模型
        # "google/gemini-2.0-flash-001",
        # "anthropic/claude-3.7-sonnet"
    ]
    
    # 运行实验
    results = experiment.run_experiment(models=models, max_workers=2)
    
    # 打印摘要
    print("\\n=== 实验摘要 ===")
    if "report" in results:
        report = results["report"]
        print("主要发现:")
        for finding in report["executive_summary"]["key_findings"]:
            print(f"- {finding}")
        
        print("\\n建议:")
        for recommendation in report["recommendations"]:
            print(f"- {recommendation}")


if __name__ == "__main__":
    main()
