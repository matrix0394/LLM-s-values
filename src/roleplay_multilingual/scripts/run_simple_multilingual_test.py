#!/usr/bin/env python3
"""
简化的多语言测试脚本
2个模型 × 4个国家 × 1次重复 = 8次API调用
然后进行统一PCA对比分析
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from src.multilingual.multilingual_roleplay_interview import MultilingualRoleplayInterview
from src.multilingual.multilingual_roleplay_data_processor import MultilingualRoleplayDataProcessor
from src.multilingual.unified_multilingual_pca_analysis import UnifiedMultilingualPCAAnalysis


class SimpleMultilingualTest:
    """简化的多语言测试"""
    
    def __init__(self):
        self.interviewer = MultilingualRoleplayInterview()
        self.data_processor = MultilingualRoleplayDataProcessor()
        self.pca_analyzer = UnifiedMultilingualPCAAnalysis()
        
        # 测试配置
        self.test_countries = {
            "zh-cn": "China",
            "ru": "Russian Federation", 
            "es-la": "Mexico",
            "ar": "Egypt"
        }
        
        # 选择2个模型
        self.test_models = [
            "openai/gpt-4o-mini",
            "google/gemini-2.0-flash-001"
        ]
        
        # 结果目录
        self.results_dir = Path("data/results/simple_multilingual_test")
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def run_multilingual_interviews(self):
        """运行多语言访谈"""
        print("🌍 开始简化多语言访谈测试...")
        print(f"📋 配置: 2个模型 × 4个国家 = 8次API调用")
        
        all_results = []
        total_tasks = len(self.test_countries) * len(self.test_models)
        completed_tasks = 0
        
        for language, country in self.test_countries.items():
            print(f"\\n🏳️ 处理语言: {language} ({country})")
            
            for model in self.test_models:
                model_short = model.split('/')[-1]
                print(f"   🤖 使用模型: {model_short}")
                
                try:
                    result = self.interviewer.interview_country_multilingual(
                        model_name=model,
                        country=country,
                        language=language
                    )
                    
                    # 添加标识信息
                    result['task_id'] = f"{model}_{country}_{language}"
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
            "experiment_type": "simple_multilingual_test",
            "experiment_config": {
                "countries": self.test_countries,
                "models": self.test_models,
                "total_calls": total_tasks
            },
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "success_rate": completed_tasks / total_tasks * 100,
            "results": all_results
        }
        
        raw_file = self.results_dir / f"simple_multilingual_interviews_{timestamp}.json"
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(raw_results, f, ensure_ascii=False, indent=2)
        
        print(f"\\n💾 原始访谈结果已保存: {raw_file}")
        print(f"📊 访谈完成率: {completed_tasks}/{total_tasks} ({completed_tasks/total_tasks*100:.1f}%)")
        
        return raw_results, str(raw_file)
    
    def process_and_analyze(self, raw_results_file):
        """处理数据并进行统一PCA分析"""
        print("\\n🔄 处理数据并进行统一PCA分析...")
        
        # 1. 处理多语言数据
        print("1️⃣ 处理多语言访谈数据...")
        processing_result = self.data_processor.process_multilingual_data(raw_results_file)
        
        # 2. 运行统一PCA分析
        print("2️⃣ 运行统一PCA分析...")
        pca_result = self.pca_analyzer.run_complete_unified_analysis()
        
        return processing_result, pca_result
    
    def generate_summary_report(self, processing_result, pca_result):
        """生成摘要报告"""
        print("\\n📊 生成摘要报告...")
        
        report = {
            "experiment_summary": {
                "timestamp": datetime.now().isoformat(),
                "type": "simple_multilingual_test",
                "countries": list(self.test_countries.values()),
                "models": [m.split('/')[-1] for m in self.test_models],
                "total_api_calls": len(self.test_countries) * len(self.test_models)
            },
            "data_processing": {
                "total_responses": processing_result['stats']['total_responses'],
                "success_rate": processing_result['stats']['overall_success_rate']
            },
            "pca_analysis": {},
            "distance_comparison": {},
            "key_findings": [],
            "conclusion": ""
        }
        
        # 提取PCA分析结果
        if pca_result["success"]:
            distance_results = pca_result["distance_results"]
            
            # 距离对比
            ml_stats = distance_results["summary_statistics"].get("multilingual_vs_real", {})
            eng_stats = distance_results["summary_statistics"].get("english_vs_real", {})
            
            if ml_stats and eng_stats:
                ml_mean = ml_stats["mean_distance"]
                eng_mean = eng_stats["mean_distance"]
                improvement = eng_mean - ml_mean
                improvement_pct = (improvement / eng_mean * 100) if eng_mean > 0 else 0
                
                report["distance_comparison"] = {
                    "multilingual_mean_distance": ml_mean,
                    "english_mean_distance": eng_mean,
                    "improvement": improvement,
                    "improvement_percentage": improvement_pct,
                    "better_method": "multilingual" if ml_mean < eng_mean else "english"
                }
                
                # 关键发现
                if improvement > 0:
                    report["key_findings"].append(
                        f"✅ 多语言方法表现更好：平均距离减少 {improvement:.3f} ({improvement_pct:.1f}%)"
                    )
                    report["conclusion"] = "在统一PCA空间中，多语言方法确实比英文方法更准确地模拟了文化价值观"
                else:
                    report["key_findings"].append(
                        f"⚠️ 英文方法仍表现更好：多语言方法距离增加 {-improvement:.3f} ({-improvement_pct:.1f}%)"
                    )
                    report["conclusion"] = "多语言方法需要进一步优化，可能在提示词或文化背景描述方面"
                
                report["key_findings"].append(f"多语言平均距离: {ml_mean:.3f}")
                report["key_findings"].append(f"英文平均距离: {eng_mean:.3f}")
        
        # 保存报告
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.results_dir / f"simple_test_summary_{timestamp}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"📋 摘要报告已保存: {report_file}")
        return report
    
    def print_final_results(self, report):
        """打印最终结果"""
        print("\\n" + "=" * 60)
        print("🎯 简化多语言测试结果")
        print("=" * 60)
        
        config = report["experiment_summary"]
        print(f"📋 实验配置:")
        print(f"   测试国家: {config['countries']}")
        print(f"   测试模型: {config['models']}")
        print(f"   API调用数: {config['total_api_calls']}")
        
        if "distance_comparison" in report and report["distance_comparison"]:
            comp = report["distance_comparison"]
            print(f"\\n📊 距离对比结果 (统一PCA空间):")
            print(f"   多语言平均距离: {comp['multilingual_mean_distance']:.3f}")
            print(f"   英文平均距离: {comp['english_mean_distance']:.3f}")
            print(f"   改进幅度: {comp['improvement']:.3f} ({comp['improvement_percentage']:.1f}%)")
            print(f"   更好的方法: {comp['better_method']}")
        
        print(f"\\n🔍 关键发现:")
        for finding in report["key_findings"]:
            print(f"   {finding}")
        
        if report["conclusion"]:
            print(f"\\n💡 结论:")
            print(f"   {report['conclusion']}")
        
        print("\\n✅ 简化测试完成！")
    
    def run_complete_test(self):
        """运行完整的简化测试"""
        print("🧪 简化多语言测试")
        print("=" * 60)
        
        try:
            # 1. 运行多语言访谈
            raw_results, raw_file = self.run_multilingual_interviews()
            
            # 2. 处理数据并分析
            processing_result, pca_result = self.process_and_analyze(raw_file)
            
            # 3. 生成摘要报告
            report = self.generate_summary_report(processing_result, pca_result)
            
            # 4. 显示最终结果
            self.print_final_results(report)
            
            return {
                "success": True,
                "report": report,
                "files": {
                    "raw_interviews": raw_file,
                    "results_dir": str(self.results_dir)
                }
            }
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}


def main():
    """主函数"""
    print("🚀 启动简化多语言测试")
    
    # 检查API密钥
    if not os.getenv('OPENROUTER_API_KEY'):
        print("❌ 请设置 OPENROUTER_API_KEY 环境变量")
        return
    
    # 运行测试
    tester = SimpleMultilingualTest()
    result = tester.run_complete_test()
    
    if result["success"]:
        print("\\n🎉 简化测试成功完成！")
        print(f"\\n📁 结果文件位置: {result['files']['results_dir']}")
    else:
        print(f"\\n❌ 测试失败: {result.get('error', '未知错误')}")


if __name__ == "__main__":
    main()







