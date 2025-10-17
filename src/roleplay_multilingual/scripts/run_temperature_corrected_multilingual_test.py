#!/usr/bin/env python3
"""
修正温度参数的多语言测试
确保与英文系统使用相同的温度策略
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

from typing import Dict, List, Optional, Any
from src.multilingual.multilingual_roleplay_interview import MultilingualRoleplayInterview
from src.multilingual.multilingual_roleplay_data_processor import MultilingualRoleplayDataProcessor
from src.multilingual.unified_multilingual_pca_analysis import UnifiedMultilingualPCAAnalysis


class TemperatureCorrectedMultilingualTest:
    """修正温度参数的多语言测试"""
    
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
        self.results_dir = Path("data/results/temperature_corrected_multilingual")
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def ask_question_with_temperature_strategy(self, model_name: str, country: str, language: str, question_id: str, max_attempts: int = 5) -> Dict[str, Any]:
        """使用与英文系统相同的温度策略提问"""
        question_data = self.interviewer.multilingual_config["languages"][language]["questions"].get(question_id)
        if not question_data:
            return {
                "question_id": question_id,
                "country": country,
                "language": language,
                "model": model_name,
                "success": False,
                "error": f"Question {question_id} not found for language {language}",
                "raw_response": None,
                "processed_response": None
            }
        
        system_prompt = self.interviewer._create_multilingual_system_prompt(country, language)
        
        # 使用与英文系统相同的重试和温度策略
        for attempt in range(max_attempts):
            try:
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question_data["question"]}
                ]
                
                # 使用与英文系统相同的动态温度策略
                temperature = 0.3 + (attempt * 0.2)  # 0.3, 0.5, 0.7, 0.9, 1.1
                
                # 调用API - 传递temperature参数
                response_text = self.interviewer._call_model_api(
                    model_name, 
                    messages, 
                    max_tokens=100, 
                    timeout=30,
                    temperature=temperature
                )
                
                if response_text:
                    # 处理和验证回答
                    processed_response = self.interviewer._process_response(response_text, question_id)
                    if processed_response:
                        return {
                            "question_id": question_id,
                            "country": country,
                            "language": language,
                            "model": model_name,
                            "success": True,
                            "attempt": attempt + 1,
                            "temperature": temperature,
                            "raw_response": response_text,
                            "processed_response": processed_response
                        }
                
                # 如果处理失败，记录并重试
                print(f"    尝试 {attempt + 1}: 回答无效，重试... (temperature={temperature})")
                
            except Exception as e:
                print(f"    尝试 {attempt + 1} 失败: {e}")
                continue
        
        # 所有尝试都失败
        return {
            "question_id": question_id,
            "country": country,
            "language": language,
            "model": model_name,
            "success": False,
            "error": f"All {max_attempts} attempts failed",
            "raw_response": None,
            "processed_response": None
        }
    
    def interview_country_with_temperature_correction(self, model_name: str, country: str, language: str) -> Dict[str, Any]:
        """使用修正温度策略的国家访谈"""
        print(f"🌍 开始访谈: {model_name} -> {country} ({language})")
        
        questions = self.interviewer.multilingual_config["languages"][language]["questions"]
        responses = []
        valid_responses = 0
        
        for i, question_id in enumerate(questions.keys(), 1):
            print(f"  问题 {i}/{len(questions)}: {question_id}")
            
            result = self.ask_question_with_temperature_strategy(
                model_name, country, language, question_id
            )
            
            if result["success"]:
                valid_responses += 1
                print(f"    ✅ 成功 (尝试{result['attempt']}, temp={result['temperature']:.1f}): {result['processed_response']}")
            else:
                print(f"    ❌ 失败: {result.get('error', 'Unknown error')}")
            
            responses.append(result)
            time.sleep(1)  # API限制
        
        success_rate = (valid_responses / len(questions)) * 100
        print(f"  📊 成功率: {success_rate:.1f}% ({valid_responses}/{len(questions)})")
        
        return {
            "model": model_name,
            "country": country,
            "language": language,
            "responses": responses,
            "success_rate": success_rate,
            "valid_responses": valid_responses,
            "total_questions": len(questions),
            "timestamp": datetime.now().isoformat()
        }
    
    def run_temperature_corrected_test(self):
        """运行温度修正测试"""
        print("🌡️ 开始温度修正的多语言测试...")
        print("📋 使用与英文系统相同的温度策略: 0.3 -> 0.5 -> 0.7 -> 0.9 -> 1.1")
        
        all_results = []
        total_tasks = len(self.test_countries) * len(self.test_models)
        completed_tasks = 0
        
        for language, country in self.test_countries.items():
            print(f"\n🏳️ 处理语言: {language} ({country})")
            
            for model in self.test_models:
                model_short = model.split('/')[-1]
                print(f"   🤖 使用模型: {model_short}")
                
                try:
                    result = self.interview_country_with_temperature_correction(
                        model_name=model,
                        country=country,
                        language=language
                    )
                    
                    all_results.append(result)
                    completed_tasks += 1
                    
                    print(f"   ✅ 完成 ({completed_tasks}/{total_tasks}) - 成功率: {result['success_rate']:.1f}%")
                    
                except Exception as e:
                    print(f"   ❌ 访谈失败: {e}")
                    completed_tasks += 1
                    continue
        
        # 保存结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_data = {
            "timestamp": timestamp,
            "experiment_type": "temperature_corrected_multilingual",
            "experiment_config": {
                "temperature_strategy": "0.3 + (attempt * 0.2)",
                "max_attempts": 5,
                "countries": self.test_countries,
                "models": self.test_models,
                "total_calls": total_tasks
            },
            "results": all_results,
            "summary": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "overall_success_rate": sum(r.get('success_rate', 0) for r in all_results) / len(all_results) if all_results else 0
            }
        }
        
        # 保存到文件
        results_file = self.results_dir / f"temperature_corrected_interviews_{timestamp}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 结果已保存: {results_file}")
        return results_data


def main():
    """主函数"""
    print("🚀 启动温度修正的多语言测试")
    
    # 检查API密钥
    if not os.getenv('OPENROUTER_API_KEY'):
        print("❌ 请设置 OPENROUTER_API_KEY 环境变量")
        return
    
    # 运行测试
    tester = TemperatureCorrectedMultilingualTest()
    result = tester.run_temperature_corrected_test()
    
    print("\n🎉 温度修正测试完成！")
    print(f"📊 总体成功率: {result['summary']['overall_success_rate']:.1f}%")
    
    # 运行统一PCA分析
    print("\n🔬 开始统一PCA分析...")
    try:
        pca_analyzer = UnifiedMultilingualPCAAnalysis()
        pca_results = pca_analyzer.run_complete_analysis()
        print("✅ PCA分析完成")
    except Exception as e:
        print(f"❌ PCA分析失败: {e}")


if __name__ == "__main__":
    main()
