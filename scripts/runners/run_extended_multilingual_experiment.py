#!/usr/bin/env python3
"""
扩展多语言文化价值实验脚本
=================================

实验目标: 使用更多模型和国家比较LLM用英文vs本国语言模仿各国时的文化价值表达差异

实验配置:
- 模型: 7个 (除Claude外所有模型)
- 国家: 19个 (4种语言各选多个国家)
- 语言: 英文 + 本国语言 (中文/俄语/西班牙语/阿拉伯语)

实验流程:
1. 数据收集: 英文+本国语言 → 提问LLM模仿各国 → 得到问答结果
2. PCA分析: 所有数据(真实国家+英文LLM+本国语言LLM)一起做PCA
3. 文化地图: 在同一个PCA空间中绘制文化坐标图
4. 距离计算: 
   - 英文LLM ↔ 真实国家距离
   - 本国语言LLM ↔ 真实国家距离
   - 比较哪种语言模仿效果更好
"""

import sys
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter
import time
import threading
import warnings
warnings.filterwarnings('ignore')

# 添加项目路径
sys.path.append('.')

from src.roleplay.llm_country_roleplay_interview import LLMCountryRoleplayInterview
from src.base.base_pca_analyzer import BasePCAAnalyzer
from src.llm_analysis.llm_questionnaire import IVSQuestions


class ExtendedMultilingualExperiment:
    """扩展多语言实验类"""
    
    def __init__(self):
        self.data_path = Path("data")
        self.results_dir = Path("data/results/extended_multilingual_experiment")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # 实验配置
        self.config = {
            "models": [
                "openai/gpt-4o-mini",
                "google/gemini-2.0-flash-001",
                "meta-llama/llama-3.3-70b-instruct",
                "deepseek/deepseek-chat-v3-0324",
                "qwen/qwq-32b",
                "mistralai/mistral-nemo"
            ],
            "temperature": 0.1,
            "max_tokens": 50,
            "repeat_count": 3,  # 基于稳定性分析优化到3次采样
            "max_workers": 4,  # 并行工作线程数
            "batch_size": 10,  # 每批处理的问题数
            "use_majority_vote": True,  # 使用众数投票
            # 扩展的国家-语言对应关系
            "country_language_pairs": {
                # 中文国家
                "China": {"native": "zh-cn", "native_name": "中文"},
                "Taiwan": {"native": "zh-cn", "native_name": "中文"},
                "Hong Kong": {"native": "zh-cn", "native_name": "中文"},
                "Macao": {"native": "zh-cn", "native_name": "中文"},
                # 俄语国家
                "Russian Federation": {"native": "ru", "native_name": "俄语"},
                "Belarus": {"native": "ru", "native_name": "俄语"},
                "Kazakhstan": {"native": "ru", "native_name": "俄语"},
                "Ukraine": {"native": "ru", "native_name": "俄语"},
                "Kyrgyzstan": {"native": "ru", "native_name": "俄语"},
                # 西班牙语国家
                "Spain": {"native": "es", "native_name": "西班牙语"},
                "Mexico": {"native": "es", "native_name": "西班牙语"},
                "Argentina": {"native": "es", "native_name": "西班牙语"},
                "Colombia": {"native": "es", "native_name": "西班牙语"},
                "Peru": {"native": "es", "native_name": "西班牙语"},
                # 阿拉伯语国家
                "Egypt": {"native": "ar", "native_name": "阿拉伯语"},
                "Saudi Arabia": {"native": "ar", "native_name": "阿拉伯语"},
                "Iraq": {"native": "ar", "native_name": "阿拉伯语"},
                "Algeria": {"native": "ar", "native_name": "阿拉伯语"},
                "Morocco": {"native": "ar", "native_name": "阿拉伯语"}
            }
        }
        
        # 加载问题
        self.questions = IVSQuestions()
        self.question_ids = ['A008', 'A165', 'E018', 'E025', 'F063', 'F118', 'F120', 'G006', 'Y002', 'Y003']
        
        # 加载多语言问题
        with open('config/multilingual_questions_complete.json', 'r', encoding='utf-8') as f:
            self.multilingual_questions = json.load(f)
    
    def _estimate_cost_and_time(self) -> Dict[str, Any]:
        """估算实验的耗时和费用"""
        
        # 基础参数
        num_countries = len(self.config["country_language_pairs"])
        num_models = len(self.config["models"])
        num_languages = 2  # 英文 + 本国语言
        num_questions = len(self.question_ids)
        repeat_count = self.config["repeat_count"]
        max_workers = self.config["max_workers"]
        
        # 计算总API调用次数
        total_api_calls = num_countries * num_models * num_languages * num_questions * repeat_count
        
        # 估算时间（基于经验值）
        avg_api_time = 2.0  # 平均每次API调用2秒（包括网络延迟）
        parallel_factor = min(max_workers, total_api_calls) / total_api_calls
        estimated_time_seconds = (total_api_calls * avg_api_time) * (1 - parallel_factor * 0.7)  # 并行效率约70%
        
        # 转换时间格式
        hours = int(estimated_time_seconds // 3600)
        minutes = int((estimated_time_seconds % 3600) // 60)
        seconds = int(estimated_time_seconds % 60)
        
        # 估算费用（基于不同模型的定价）
        model_costs = {
            "openai/gpt-4o-mini": {"input": 0.00015, "output": 0.0006},  # per 1K tokens
            "google/gemini-2.0-flash-001": {"input": 0.000075, "output": 0.0003},
            "meta-llama/llama-3.3-70b-instruct": {"input": 0.0009, "output": 0.0009},
            "deepseek/deepseek-chat-v3-0324": {"input": 0.00014, "output": 0.00028},
            "qwen/qwq-32b": {"input": 0.0009, "output": 0.0009},
            "mistralai/mistral-nemo": {"input": 0.0003, "output": 0.0003}
        }
        
        # 估算token使用量
        avg_input_tokens = 150  # 系统提示 + 问题
        avg_output_tokens = 20  # 简短回答
        
        total_cost = 0
        model_costs_breakdown = {}
        
        for model in self.config["models"]:
            if model in model_costs:
                model_api_calls = num_countries * num_languages * num_questions * repeat_count
                input_cost = (model_api_calls * avg_input_tokens / 1000) * model_costs[model]["input"]
                output_cost = (model_api_calls * avg_output_tokens / 1000) * model_costs[model]["output"]
                model_total = input_cost + output_cost
                total_cost += model_total
                model_costs_breakdown[model] = model_total
            else:
                # 未知模型使用平均价格
                avg_cost = 0.0005
                model_api_calls = num_countries * num_languages * num_questions * repeat_count
                model_total = (model_api_calls * (avg_input_tokens + avg_output_tokens) / 1000) * avg_cost
                total_cost += model_total
                model_costs_breakdown[model] = model_total
        
        return {
            "total_api_calls": total_api_calls,
            "estimated_time": {
                "seconds": estimated_time_seconds,
                "formatted": f"{hours}小时{minutes}分钟{seconds}秒" if hours > 0 else f"{minutes}分钟{seconds}秒"
            },
            "estimated_cost": {
                "total_usd": total_cost,
                "total_cny": total_cost * 7.2,  # 假设汇率1:7.2
                "breakdown": model_costs_breakdown
            },
            "experiment_scale": {
                "countries": num_countries,
                "models": num_models,
                "languages": num_languages,
                "questions": num_questions,
                "repeat_count": repeat_count,
                "parallel_workers": max_workers
            }
        }
    
    def _print_cost_estimate_and_confirm(self) -> bool:
        """打印费用估算并询问是否继续"""
        
        estimate = self._estimate_cost_and_time()
        
        print("\n" + "="*60)
        print("💰 实验费用和时间估算")
        print("="*60)
        
        # 实验规模
        scale = estimate["experiment_scale"]
        print(f"📊 实验规模:")
        print(f"   • 测试国家: {scale['countries']} 个")
        print(f"   • 测试模型: {scale['models']} 个")
        print(f"   • 语言类型: {scale['languages']} 种 (英文 + 本国语言)")
        print(f"   • 问题数量: {scale['questions']} 个")
        print(f"   • 重复采样: {scale['repeat_count']} 次")
        print(f"   • 并行线程: {scale['parallel_workers']} 个")
        
        # API调用
        print(f"\n🔄 API调用:")
        print(f"   • 总调用次数: {estimate['total_api_calls']:,} 次")
        print(f"   • 计算公式: {scale['countries']} × {scale['models']} × {scale['languages']} × {scale['questions']} × {scale['repeat_count']}")
        
        # 时间估算
        print(f"\n⏱️ 预计耗时:")
        print(f"   • 估算时间: {estimate['estimated_time']['formatted']}")
        print(f"   • 说明: 已考虑 {scale['parallel_workers']} 线程并行处理的加速效果")
        
        # 费用估算
        cost = estimate["estimated_cost"]
        print(f"\n💵 预计费用:")
        print(f"   • 总费用: ${cost['total_usd']:.2f} USD (约 ¥{cost['total_cny']:.2f} CNY)")
        
        # 按模型分解费用
        print(f"\n📋 各模型费用明细:")
        for model, model_cost in cost["breakdown"].items():
            percentage = (model_cost / cost['total_usd']) * 100
            print(f"   • {model}: ${model_cost:.3f} ({percentage:.1f}%)")
        
        # 风险提示
        print(f"\n⚠️ 重要提示:")
        print(f"   • 以上为估算值，实际费用可能因网络、重试等因素有所差异")
        print(f"   • 建议确保API账户有足够余额")
        print(f"   • 可以使用 --existing 参数仅分析已有数据")
        print(f"   • 优化模式会增加 {scale['repeat_count']}x 的API调用和费用")
        
        print("="*60)
        
        # 询问是否继续
        while True:
            try:
                user_input = input("🤔 是否继续运行实验? (y/n/详情): ").strip().lower()
                if user_input in ['y', 'yes', '是', 'ok']:
                    return True
                elif user_input in ['n', 'no', '否', 'cancel']:
                    return False
                elif user_input in ['详情', 'detail', 'd', 'details']:
                    self._print_detailed_breakdown(estimate)
                    continue
                else:
                    print("请输入 y(继续) 或 n(取消) 或 '详情'(查看详细信息)")
            except KeyboardInterrupt:
                print("\n❌ 用户取消操作")
                return False
    
    def _print_detailed_breakdown(self, estimate: Dict):
        """打印详细的费用和时间分解"""
        
        print("\n" + "-"*50)
        print("📊 详细分解")
        print("-"*50)
        
        scale = estimate["experiment_scale"]
        
        # 每个国家的详细信息
        print(f"🏛️ 每个国家的处理:")
        calls_per_country = scale['models'] * scale['languages'] * scale['questions'] * scale['repeat_count']
        time_per_country = calls_per_country * 2.0 / scale['parallel_workers']  # 考虑并行
        cost_per_country = estimate['estimated_cost']['total_usd'] / scale['countries']
        
        print(f"   • API调用: {calls_per_country} 次")
        print(f"   • 预计时间: {time_per_country/60:.1f} 分钟")
        print(f"   • 预计费用: ${cost_per_country:.3f}")
        
        # 每个模型的详细信息
        print(f"\n🤖 每个模型的处理:")
        calls_per_model = scale['countries'] * scale['languages'] * scale['questions'] * scale['repeat_count']
        time_per_model = calls_per_model * 2.0 / scale['parallel_workers']
        
        print(f"   • API调用: {calls_per_model} 次")
        print(f"   • 预计时间: {time_per_model/60:.1f} 分钟")
        
        # 优化效果
        print(f"\n🚀 并行优化效果:")
        serial_time = estimate['total_api_calls'] * 2.0
        parallel_time = estimate['estimated_time']['seconds']
        speedup = serial_time / parallel_time
        
        print(f"   • 串行时间: {serial_time/3600:.1f} 小时")
        print(f"   • 并行时间: {parallel_time/3600:.1f} 小时")
        print(f"   • 加速比: {speedup:.1f}x")
        
        print("-"*50)
    
    def run_experiment(self, use_existing_data: bool = False) -> Dict[str, Any]:
        """运行完整实验"""
        print("🎯 扩展多语言文化价值实验")
        print("=" * 50)
        
        # 如果不是使用现有数据，则进行费用估算和确认
        if not use_existing_data:
            if not self._print_cost_estimate_and_confirm():
                print("❌ 用户取消实验")
                return {"status": "cancelled", "message": "用户取消实验"}
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 显示实验规模
        total_countries = len(self.config["country_language_pairs"])
        total_models = len(self.config["models"])
        total_calls = total_countries * total_models * 2 * self.config["repeat_count"] * len(self.question_ids)
        
        print(f"📊 实验规模:")
        print(f"   - 测试国家: {total_countries} 个")
        print(f"   - 测试模型: {total_models} 个")
        print(f"   - 语言类型: 2 种 (英文 + 本国语言)")
        print(f"   - 重复次数: {self.config['repeat_count']} 次")
        print(f"   - 问题数量: {len(self.question_ids)} 个")
        print(f"   - 预计API调用: {total_calls} 次")
        
        # 步骤1: 收集数据
        if use_existing_data:
            print("\n📂 使用现有数据...")
            interview_data = self._load_existing_data()
        else:
            print(f"\n📋 步骤1: 收集LLM访谈数据")
            interview_data = self._collect_interview_data()
            
            # 保存数据
            data_file = self.results_dir / f"interview_data_{timestamp}.json"
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(interview_data, f, ensure_ascii=False, indent=2)
            print(f"💾 数据已保存: {data_file}")
        
        # 步骤2: 统一PCA分析
        print(f"\n📊 步骤2: 统一PCA分析")
        pca_results = self._perform_unified_pca(interview_data)
        
        # 步骤3: 绘制文化地图
        print(f"\n🗺️ 步骤3: 绘制文化地图")
        map_file = self._create_cultural_map(pca_results, timestamp)
        
        # 步骤4: 距离对比分析
        print(f"\n📏 步骤4: 距离对比分析")
        distance_analysis = self._analyze_distances(pca_results)
        
        # 步骤5: 模型对比分析
        print(f"\n🤖 步骤5: 模型对比分析")
        model_analysis = self._analyze_model_performance(pca_results)
        
        # 步骤6: 生成分析报告
        print(f"\n📋 步骤6: 生成分析报告")
        report = self._generate_report(interview_data, pca_results, distance_analysis, 
                                     model_analysis, map_file, timestamp)
        
        print(f"\n✅ 实验完成!")
        print(f"📁 结果目录: {self.results_dir}")
        print(f"🗺️ 文化地图: {map_file}")
        print(f"📋 分析报告: {self.results_dir / f'analysis_report_{timestamp}.json'}")
        
        return {
            "report_file": str(self.results_dir / f"analysis_report_{timestamp}.json"),
            "map_file": map_file,
            "pca_file": str(self.results_dir / f"pca_results_{timestamp}.pkl"),
            "interview_file": str(self.results_dir / f"interview_data_{timestamp}.json")
        }
    
    def _collect_interview_data(self) -> Dict[str, Any]:
        """收集访谈数据"""
        
        interview_data = {}
        
        total_countries = len(self.config["country_language_pairs"])
        
        for i, (country, lang_config) in enumerate(self.config["country_language_pairs"].items(), 1):
            print(f"\n🏛️ 访谈国家 ({i}/{total_countries}): {country}")
            
            country_data = {}
            
            # 英文访谈（使用优化方法）
            print(f"   🇺🇸 英文访谈...")
            country_data["english"] = self._interview_country_optimized(country, "english", "English")
            
            # 本国语言访谈（使用优化方法）
            native_lang = lang_config["native"]
            native_name = lang_config["native_name"]
            print(f"   🌍 {native_name}访谈...")
            country_data["native"] = self._interview_country_optimized(country, native_lang, native_name)
            
            interview_data[country] = country_data
        
        return interview_data
    
    def _interview_country(self, country: str, language: str, language_name: str) -> Dict[str, Any]:
        """访谈特定国家的特定语言"""
        import os
        import time
        from openai import OpenAI
        
        # 加载模型配置
        config_path = Path('config/llm_models.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            model_config = json.load(f)
        
        results = {}
        
        for model in self.config["models"]:
            model_results = []
            
            # 获取模型配置
            if model not in model_config['models']:
                print(f"      ❌ 模型 {model} 配置未找到")
                continue
                
            model_info = model_config['models'][model]
            api_key = os.getenv(model_info.get('api_key', 'OPENROUTER_API_KEY'))
            
            if not api_key:
                print(f"      ❌ 模型 {model} API密钥未设置")
                continue
            
            # 创建客户端
            client = OpenAI(
                api_key=api_key,
                base_url=model_info.get('base_url', 'https://openrouter.ai/api/v1')
            )
            
            for repeat in range(self.config["repeat_count"]):
                print(f"      🤖 {model} (第{repeat+1}次)")
                
                repeat_responses = {}
                
                for question_id in self.question_ids:
                    # 获取问题文本
                    if language == "en":
                        question_text = self.questions.get_question_text(question_id)
                    else:
                        question_text = self.multilingual_questions["languages"][language]["questions"][question_id]["question"]
                    
                    # 构建系统提示词
                    system_prompt = self._build_system_prompt(country, language)
                    
                    # 调用API
                    try:
                        response = client.chat.completions.create(
                            model=model,  # 直接使用模型名
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": question_text}
                            ],
                            temperature=self.config["temperature"],
                            max_tokens=self.config["max_tokens"]
                        )
                        
                        raw_response = response.choices[0].message.content.strip()
                        repeat_responses[question_id] = raw_response
                        print(f"        {question_id}: {raw_response}")
                        
                    except Exception as e:
                        print(f"        ❌ 问题 {question_id} 失败: {e}")
                        repeat_responses[question_id] = None
                    
                    # 简单延迟
                    time.sleep(0.5)
                
                model_results.append({
                    "repeat": repeat + 1,
                    "responses": repeat_responses
                })
            
            results[model] = model_results
        
        return results
    
    def _interview_country_optimized(self, country: str, language: str, language_name: str) -> Dict[str, Any]:
        """优化的访谈方法：支持多次采样、批量处理和并行执行"""
        import os
        import time
        from openai import OpenAI
        
        print(f"    🚀 开始优化访谈: {country} ({language_name})")
        
        # 加载模型配置
        config_path = Path('config/llm_models.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            model_config = json.load(f)
        
        results = {}
        
        # 按模型批量处理（一个模型问完所有问题再换模型）
        for model in self.config["models"]:
            print(f"      🤖 处理模型: {model}")
            
            # 获取模型配置
            if model not in model_config['models']:
                print(f"        ❌ 模型 {model} 配置未找到")
                continue
            
            model_info = model_config['models'][model]
            
            # 并行处理多次采样
            model_results = self._parallel_sample_model(
                model, model_info, country, language, language_name
            )
            
            if model_results:
                # 使用众数投票聚合结果
                if self.config.get("use_majority_vote", True):
                    aggregated_result = self._aggregate_responses_with_majority_vote(model_results)
                    results[model] = [{
                        'timestamp': datetime.now().isoformat(),
                        'responses': aggregated_result,
                        'sample_count': len(model_results),
                        'aggregation_method': 'majority_vote'
                    }]
                else:
                    results[model] = model_results
                
                print(f"        ✅ 完成 {len(model_results)} 次采样，已聚合")
            else:
                print(f"        ❌ 模型 {model} 访谈失败")
        
        return results
    
    def _parallel_sample_model(self, model: str, model_info: Dict, country: str, 
                              language: str, language_name: str) -> List[Dict]:
        """并行执行多次采样"""
        
        # 创建多个采样任务
        sample_tasks = []
        for sample_idx in range(self.config["repeat_count"]):
            sample_tasks.append({
                'sample_idx': sample_idx,
                'model': model,
                'model_info': model_info,
                'country': country,
                'language': language,
                'language_name': language_name
            })
        
        # 并行执行采样
        results = []
        with ThreadPoolExecutor(max_workers=self.config["max_workers"]) as executor:
            # 提交所有任务
            future_to_task = {
                executor.submit(self._execute_single_sample, task): task 
                for task in sample_tasks
            }
            
            # 收集结果
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                        print(f"        ✓ 采样 {task['sample_idx']+1} 完成")
                    else:
                        print(f"        ✗ 采样 {task['sample_idx']+1} 失败")
                except Exception as e:
                    print(f"        ✗ 采样 {task['sample_idx']+1} 异常: {e}")
        
        return results
    
    def _execute_single_sample(self, task: Dict) -> Optional[Dict]:
        """执行单次采样"""
        import os
        import time
        from openai import OpenAI
        
        model = task['model']
        model_info = task['model_info']
        country = task['country']
        language = task['language']
        language_name = task['language_name']
        sample_idx = task['sample_idx']
        
        try:
            # 初始化客户端
            if model_info['provider'] == 'openai':
                client = OpenAI(
                    api_key=os.getenv('OPENAI_API_KEY'),
                    base_url=model_info.get('base_url')
                )
            elif model_info['provider'] == 'openrouter':
                client = OpenAI(
                    api_key=os.getenv('OPENROUTER_API_KEY'),
                    base_url="https://openrouter.ai/api/v1"
                )
            else:
                print(f"          ❌ 不支持的提供商: {model_info['provider']}")
                return None
            
            # 构建系统提示
            system_prompt = self._build_system_prompt(country, language)
            
            # 批量处理所有问题
            responses = {}
            for question_id in self.question_ids:
                try:
                    # 获取问题文本
                    if language == "english":
                        question_text = self.questions.get_question_text(question_id, "en")
                    else:
                        question_text = self.multilingual_questions.get(question_id, {}).get(language, "")
                    
                    if not question_text:
                        print(f"          ⚠️ 问题 {question_id} 在 {language} 中未找到")
                        continue
                    
                    # 调用API
                    response = client.chat.completions.create(
                        model=model_info['model_name'],
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": question_text}
                        ],
                        temperature=self.config.get("temperature", 0.1),
                        max_tokens=self.config.get("max_tokens", 50)
                    )
                    
                    responses[question_id] = response.choices[0].message.content.strip()
                    
                    # 添加小延迟避免API限制
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"          ❌ 问题 {question_id} 失败: {e}")
                    responses[question_id] = None
            
            return {
                'sample_idx': sample_idx,
                'timestamp': datetime.now().isoformat(),
                'responses': responses,
                'model': model,
                'country': country,
                'language': language
            }
            
        except Exception as e:
            print(f"          ❌ 采样 {sample_idx+1} 整体失败: {e}")
            return None
    
    def _aggregate_responses_with_majority_vote(self, model_results: List[Dict]) -> Dict[str, Any]:
        """使用众数投票聚合多次采样的结果"""
        if not model_results:
            return {}
        
        # 收集所有回答
        all_responses = {}
        for result in model_results:
            for question_id, response in result['responses'].items():
                if response is not None:
                    if question_id not in all_responses:
                        all_responses[question_id] = []
                    all_responses[question_id].append(response)
        
        # 对每个问题使用众数投票
        aggregated = {}
        for question_id, responses in all_responses.items():
            if not responses:
                continue
            
            if question_id in ['Y002', 'Y003']:
                # 复杂问题：先标准化再投票
                normalized_responses = []
                for resp in responses:
                    try:
                        if question_id == 'Y002':
                            parts = str(resp).strip().split()
                            if len(parts) >= 2:
                                first_choice = int(parts[0])
                                second_choice = int(parts[1])
                                normalized_responses.append(f"{first_choice} {second_choice}")
                        elif question_id == 'Y003':
                            parts = str(resp).strip().split()
                            selected_values = [int(p) for p in parts if p.isdigit()]
                            if selected_values:
                                normalized_responses.append(' '.join(map(str, sorted(selected_values))))
                    except:
                        continue
                
                if normalized_responses:
                    # 使用众数
                    counter = Counter(normalized_responses)
                    most_common = counter.most_common(1)[0][0]
                    aggregated[question_id] = most_common
            else:
                # 简单问题：直接投票
                try:
                    # 尝试提取数字进行投票
                    numeric_responses = []
                    for resp in responses:
                        import re
                        numbers = re.findall(r'\d+', str(resp))
                        if numbers:
                            numeric_responses.append(int(numbers[0]))
                    
                    if numeric_responses:
                        counter = Counter(numeric_responses)
                        most_common = counter.most_common(1)[0][0]
                        aggregated[question_id] = most_common
                except:
                    # 如果数字提取失败，使用原始文本投票
                    counter = Counter(responses)
                    most_common = counter.most_common(1)[0][0]
                    aggregated[question_id] = most_common
        
        return aggregated
    
    def _build_system_prompt(self, country: str, language: str) -> str:
        """构建多语言系统提示"""
        
        if language == "english":
            return f"""You are roleplaying as a typical citizen from {country}. Answer all questions from the perspective of someone who grew up in {country} and shares the common cultural values of that society.

Please follow these guidelines:
- Answer each question with a genuine, considered response
- Choose the option that best reflects your cultural values and beliefs
- Respond as a real person from {country} would

Response format:
- Single choice questions: respond with ONE number only
- Y002 (two choices): respond with TWO numbers separated by space
- Y003 (multiple choices): respond with 1-5 numbers separated by spaces

Please provide meaningful answers that reflect your cultural perspective."""
        
        elif language == "zh-cn":
            return f"""你正在扮演一个来自{country}的典型公民。请从一个在{country}长大并分享该社会共同文化价值观的人的角度来回答所有问题。

请遵循以下指导原则：
- 用真诚、深思熟虑的回答来回答每个问题
- 选择最能反映你的文化价值观和信念的选项
- 像一个真正的{country}人那样回答

回答格式：
- 单选题：只回答一个数字
- Y002（两选题）：回答两个数字，用空格分隔
- Y003（多选题）：回答1-5个数字，用空格分隔

请提供能反映你文化观点的有意义的答案。"""
        
        elif language == "ru":
            return f"""Вы играете роль типичного гражданина из {country}. Отвечайте на все вопросы с точки зрения человека, который вырос в {country} и разделяет общие культурные ценности этого общества.

Пожалуйста, следуйте этим рекомендациям:
- Отвечайте на каждый вопрос искренне и обдуманно
- Выбирайте вариант, который лучше всего отражает ваши культурные ценности и убеждения
- Отвечайте так, как ответил бы настоящий житель {country}

Формат ответа:
- Вопросы с одним выбором: отвечайте ТОЛЬКО одной цифрой
- Y002 (два выбора): отвечайте двумя цифрами через пробел
- Y003 (множественный выбор): отвечайте 1-5 цифрами через пробелы

Пожалуйста, давайте содержательные ответы, отражающие вашу культурную перспективу."""
        
        elif language == "es":
            return f"""Estás interpretando el papel de un ciudadano típico de {country}. Responde todas las preguntas desde la perspectiva de alguien que creció en {country} y comparte los valores culturales comunes de esa sociedad.

Por favor, sigue estas pautas:
- Responde cada pregunta con una respuesta genuina y reflexiva
- Elige la opción que mejor refleje tus valores culturales y creencias
- Responde como lo haría una persona real de {country}

Formato de respuesta:
- Preguntas de opción única: responde con UN número solamente
- Y002 (dos opciones): responde con DOS números separados por espacio
- Y003 (opciones múltiples): responde con 1-5 números separados por espacios

Por favor, proporciona respuestas significativas que reflejen tu perspectiva cultural."""
        
        elif language == "ar":
            return f"""أنت تلعب دور مواطن نموذجي من {country}. أجب على جميع الأسئلة من منظور شخص نشأ في {country} ويشارك القيم الثقافية المشتركة لذلك المجتمع.

يرجى اتباع هذه الإرشادات:
- أجب على كل سؤال بإجابة صادقة ومدروسة
- اختر الخيار الذي يعكس بشكل أفضل قيمك الثقافية ومعتقداتك
- أجب كما يجيب شخص حقيقي من {country}

تنسيق الإجابة:
- أسئلة الاختيار الواحد: أجب برقم واحد فقط
- Y002 (خياران): أجب برقمين مفصولين بمسافة
- Y003 (خيارات متعددة): أجب بـ 1-5 أرقام مفصولة بمسافات

يرجى تقديم إجابات ذات معنى تعكس منظورك الثقافي."""
        
        else:
            # 默认使用英文
            return f"""You are roleplaying as a typical citizen from {country}. Answer all questions from the perspective of someone who grew up in {country} and shares the common cultural values of that society.

Please follow these guidelines:
- Answer each question with a genuine, considered response
- Choose the option that best reflects your cultural values and beliefs
- Respond as a real person from {country} would

Response format:
- Single choice questions: respond with ONE number only
- Y002 (two choices): respond with TWO numbers separated by space
- Y003 (multiple choices): respond with 1-5 numbers separated by spaces

Please provide meaningful answers that reflect your cultural perspective."""
    
    def _perform_unified_pca(self, interview_data: Dict[str, Any]) -> pd.DataFrame:
        """执行统一PCA分析"""
        
        # 转换LLM数据为标准格式
        llm_data = self._convert_llm_data_to_standard_format(interview_data)
        
        # 创建PCA分析器
        class UnifiedPCAAnalyzer(BasePCAAnalyzer):
            def __init__(self, llm_data: pd.DataFrame):
                super().__init__(data_path="data")
                self.llm_data = llm_data
                # 加载IVS数据
                self.load_base_data()
            
            def load_additional_data(self) -> pd.DataFrame:
                return self.llm_data
            
            def combine_data(self) -> pd.DataFrame:
                # 加载并预处理IVS数据
                ivs_data = self.prepare_ivs_data()
                
                # 添加数据源标识
                ivs_data['data_source'] = 'IVS'
                
                # 确保IVS数据有LLM数据的元数据列
                for col in ['model', 'language_type', 'country_name']:
                    if col not in ivs_data.columns:
                        ivs_data[col] = ''
                
                # 合并数据
                combined_data = pd.concat([ivs_data, self.llm_data], ignore_index=True)
                
                print(f"📊 数据合并完成:")
                print(f"   - IVS数据: {len(ivs_data)} 行")
                print(f"   - LLM数据: {len(self.llm_data)} 行")
                print(f"   - 总计: {len(combined_data)} 行")
                
                return combined_data
            
            def calculate_entity_scores(self, group_by: List[str] = None) -> pd.DataFrame:
                """重写实体分数计算，保留元信息"""
                if self.pca_results is None:
                    raise ValueError("请先执行PCA分析")
                
                if group_by is None:
                    group_by = ['country_code', 'data_source'] if 'data_source' in self.pca_results.columns else ['country_code']
                
                print(f"🔍 使用分组键: {group_by}")
                
                # 计算分组平均分数
                entity_scores = self.pca_results.groupby(group_by)[
                    ['PC1_rescaled', 'PC2_rescaled']
                ].mean().reset_index()
                
                # 保留元数据 - 从pca_results中获取每个分组的第一个值
                metadata_cols = ['model', 'language_type', 'country_name']
                for col in metadata_cols:
                    if col in self.pca_results.columns:
                        metadata = self.pca_results.groupby(group_by)[col].first().reset_index()
                        entity_scores = entity_scores.merge(metadata[group_by + [col]], on=group_by, how='left')
                
                # 合并国家代码信息
                if self.country_codes is not None:
                    # 确保数据类型一致
                    entity_scores['country_code'] = entity_scores['country_code'].astype(str)
                    country_codes_copy = self.country_codes.copy()
                    country_codes_copy['Numeric'] = country_codes_copy['Numeric'].astype(str)
                    
                    # 清理country_code中的.0后缀（如果存在）
                    entity_scores['country_code_clean'] = entity_scores['country_code'].str.replace('.0', '', regex=False)
                    
                    entity_scores = entity_scores.merge(
                        country_codes_copy, 
                        left_on='country_code_clean', 
                        right_on='Numeric', 
                        how='left'
                    )
                    
                    # 删除临时列
                    entity_scores = entity_scores.drop('country_code_clean', axis=1)
                
                print(f"📈 计算了 {len(entity_scores)} 个实体的分数")
                return entity_scores
            
            def run_full_analysis(self) -> pd.DataFrame:
                """重写完整分析流程，确保保留元信息"""
                # 1. 合并数据
                self.combined_data = self.combine_data()
                
                # 2. 执行PCA分析
                pca_results = self.perform_pca_analysis(self.combined_data)
                
                # 3. 计算实体分数（保留元信息）
                entity_scores = self.calculate_entity_scores()
                
                # 4. 保存结果
                self.save_results(entity_scores)
                
                return entity_scores
        
        # 执行PCA
        analyzer = UnifiedPCAAnalyzer(llm_data)
        pca_results = analyzer.run_full_analysis()
        
        # 检测并过滤异常数据
        pca_results_filtered = self._filter_outlier_data(pca_results)
        
        # 保存JSON格式的PCA结果
        self._save_pca_results_json(pca_results_filtered)
        
        return pca_results_filtered
    
    def _convert_llm_data_to_standard_format(self, interview_data: Dict[str, Any]) -> pd.DataFrame:
        """将LLM访谈数据转换为标准格式"""
        from src.base.ivs_question_processor import IVSQuestionProcessor
        
        rows = []
        
        for country, country_data in interview_data.items():
            # 获取国家代码
            country_code = self._get_country_code(country)
            
            for lang_type, lang_data in country_data.items():  # english, native
                for model, model_results in lang_data.items():
                    
                    # 聚合多次重复的结果
                    aggregated_responses = self._aggregate_responses(model_results)
                    
                    if aggregated_responses:
                        # 创建数据行
                        row = {
                            'country_code': country_code,
                            'country_name': country,
                            'model': model,
                            'language_type': lang_type,
                            'data_source': f'{country}_{lang_type}_{model}',
                            'year': 2024,
                            'weight': 1.0
                        }
                        
                        # 添加问题回答
                        row.update(aggregated_responses)
                        rows.append(row)
        
        df = pd.DataFrame(rows)
        print(f"✅ LLM数据转换完成: {len(df)} 行")
        
        return df
    
    def _aggregate_responses(self, model_results: List[Dict]) -> Dict[str, float]:
        """聚合多次重复的回答"""
        from src.base.ivs_question_processor import IVSQuestionProcessor
        
        # 收集所有回答
        all_responses = {}
        for result in model_results:
            for question_id, response in result["responses"].items():
                if response is not None:
                    if question_id not in all_responses:
                        all_responses[question_id] = []
                    all_responses[question_id].append(response)
        
        # 处理每个问题的回答
        processor = IVSQuestionProcessor()
        aggregated = {}
        
        for question_id, responses in all_responses.items():
            if not responses:
                continue
            
            # 处理Y002和Y003特殊情况
            if question_id == 'Y002':
                # Y002: 选择两个最重要的目标
                processed_responses = []
                for resp in responses:
                    try:
                        # 解析回答，期望格式如 "1 3" 或 "2 4"
                        parts = str(resp).strip().split()
                        if len(parts) >= 2:
                            first_choice = int(parts[0])
                            second_choice = int(parts[1])
                            # 计算Y002分数：第一选择*2 + 第二选择*1
                            y002_score = first_choice * 2 + second_choice * 1
                            processed_responses.append(y002_score)
                    except:
                        continue
                
                if processed_responses:
                    aggregated['Y002'] = np.mean(processed_responses)
                    aggregated['y002_score'] = aggregated['Y002']
            
            elif question_id == 'Y003':
                # Y003: 选择最多5个重要品质
                processed_responses = []
                for resp in responses:
                    try:
                        # 解析回答，期望格式如 "1 3 4 6 8"
                        parts = str(resp).strip().split()
                        selected_values = [int(p) for p in parts if p.isdigit()]
                        # 计算Y003分数：所选项目的平均值
                        if selected_values:
                            y003_score = np.mean(selected_values)
                            processed_responses.append(y003_score)
                    except:
                        continue
                
                if processed_responses:
                    aggregated['Y003'] = np.mean(processed_responses)
                    aggregated['y003_score'] = aggregated['Y003']
            
            else:
                # 其他问题：直接取数值平均
                processed_responses = []
                for resp in responses:
                    try:
                        # 尝试提取数字
                        import re
                        numbers = re.findall(r'\d+', str(resp))
                        if numbers:
                            processed_responses.append(int(numbers[0]))
                    except:
                        continue
                
                if processed_responses:
                    aggregated[question_id] = np.mean(processed_responses)
        
        return aggregated
    
    def _get_country_code(self, country_name: str) -> int:
        """获取国家代码"""
        # 国家名称到代码的映射
        country_codes = {
            "China": 156,
            "Taiwan": 158,
            "Hong Kong": 344,
            "Macao": 446,
            "Russian Federation": 643,
            "Belarus": 112,
            "Kazakhstan": 398,
            "Ukraine": 804,
            "Kyrgyzstan": 417,
            "Spain": 724,
            "Mexico": 484,
            "Argentina": 32,
            "Colombia": 170,
            "Peru": 604,
            "Egypt": 818,
            "Saudi Arabia": 682,
            "Iraq": 368,
            "Algeria": 12,
            "Morocco": 504
        }
        
        return country_codes.get(country_name, 999)  # 默认代码
    
    def _create_cultural_map(self, pca_results: pd.DataFrame, timestamp: str) -> str:
        """创建文化地图"""
        
        plt.figure(figsize=(24, 16))
        
        # 分离IVS和LLM数据用于绘制
        ivs_data = pca_results[pca_results['data_source'] == 'IVS']
        llm_data = pca_results[pca_results['data_source'] != 'IVS']
        
        # 定义文化区域颜色
        cultural_region_colors = {
            'African-Islamic': '#cc79a7',
            'South Asia': '#56b4e9',
            'West & South Asia': '#f0e442',
            'Latin America': '#999999',
            'Confucian': '#e69f00',
            'Baltic': '#0072b2',
            'Protestant Europe': '#d55e00',
            'Catholic Europe': '#e69f00',
            'English-Speaking': '#009e73',
            'Orthodox Europe': '#0072b2'
        }
        
        # 绘制真实国家（按文化区域着色）
        if 'Cultural Region' in ivs_data.columns:
            for region, color in cultural_region_colors.items():
                region_data = ivs_data[ivs_data['Cultural Region'] == region]
                if len(region_data) > 0:
                    plt.scatter(region_data['PC1_rescaled'], region_data['PC2_rescaled'], 
                               c=color, s=25, alpha=0.6, label=f'{region}',
                               marker='o', edgecolors='white', linewidth=0.5)
        else:
            # 如果没有文化区域信息，使用灰色
            plt.scatter(ivs_data['PC1_rescaled'], ivs_data['PC2_rescaled'], 
                       c='lightgray', s=30, alpha=0.6, label='Real Countries (IVS)')
        
        # 为测试国家添加特殊标记和标签
        # 使用更多颜色来区分更多国家
        import matplotlib.cm as cm
        countries = list(self.config["country_language_pairs"].keys())
        colors = cm.tab20(np.linspace(0, 1, len(countries)))
        country_colors = dict(zip(countries, colors))
        
        for country in countries:
            color = country_colors[country]
            
            # 找到对应的真实国家位置（使用国家名称映射）
            country_name_mapping = {
                "Taiwan": "Taiwan (Province of China)",
                "Russian Federation": "Russian Federation (the)",
                "Saudi Arabia": None,  # IVS中不存在
            }
            ivs_country_name = country_name_mapping.get(country, country)
            
            if ivs_country_name is None:
                real_country = pd.DataFrame()  # 空DataFrame
            else:
                real_country = ivs_data[ivs_data['Country'] == ivs_country_name]
            if len(real_country) > 0:
                real_x = real_country['PC1_rescaled'].iloc[0]
                real_y = real_country['PC2_rescaled'].iloc[0]
                
                # 绘制真实国家（大星形，黑色边框）
                plt.scatter(real_x, real_y, c=[color], s=300, marker='*', 
                           edgecolors='black', linewidth=2, alpha=0.9,
                           label=f'{country} (Real)' if country == countries[0] else "")
                
                # 添加国家名标签
                plt.annotate(country, (real_x, real_y), xytext=(10, 10), 
                           textcoords='offset points', fontsize=8, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor=color, alpha=0.7))
            
            # 找到该国家的LLM数据并绘制
            country_llm = llm_data[llm_data['data_source'].str.startswith(country)]
            
            if len(country_llm) > 0:
                # 分离英文和本国语言数据
                english_data = country_llm[country_llm['data_source'].str.contains('_english_')]
                native_data = country_llm[country_llm['data_source'].str.contains('_native_')]
                
                # 绘制英文数据（圆形）
                if len(english_data) > 0:
                    plt.scatter(english_data['PC1_rescaled'], english_data['PC2_rescaled'],
                               c=[color], s=80, marker='o', alpha=0.8, 
                               label=f'{country} (English)' if country == countries[0] else "",
                               edgecolors='white', linewidth=1)
                
                # 绘制本国语言数据（三角形）
                if len(native_data) > 0:
                    plt.scatter(native_data['PC1_rescaled'], native_data['PC2_rescaled'],
                               c=[color], s=80, marker='^', alpha=0.8,
                               label=f'{country} (Native)' if country == countries[0] else "",
                               edgecolors='white', linewidth=1)
                
                # 连线显示距离（如果有真实国家数据）
                if len(real_country) > 0:
                    for _, llm_point in country_llm.iterrows():
                        plt.plot([real_x, llm_point['PC1_rescaled']], 
                               [real_y, llm_point['PC2_rescaled']], 
                               color=color, alpha=0.2, linestyle='--', linewidth=0.5)
        
        plt.xlabel('PC1 (Cultural Dimension 1)', fontsize=14)
        plt.ylabel('PC2 (Cultural Dimension 2)', fontsize=14)
        plt.title('Extended Multilingual Cultural Value Comparison\n(19 Countries, 6 Models, Real vs LLM Responses)', 
                 fontsize=16, fontweight='bold')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
        plt.grid(True, alpha=0.3)
        
        # 添加说明
        info_text = f"""
实验配置:
• 测试国家: {len(self.config['country_language_pairs'])} 个
• 测试模型: {len(self.config['models'])} 个  
• 重复次数: {self.config['repeat_count']} 次
• 总PCA实体: {len(pca_results)} 个
        """
        plt.text(0.02, 0.02, info_text, transform=plt.gca().transAxes, 
                verticalalignment='bottom', fontsize=10, 
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        # 保存图片
        map_file = self.results_dir / f"cultural_map_{timestamp}.png"
        plt.tight_layout()
        plt.savefig(map_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"🗺️ 文化地图已保存: {map_file}")
        
        # 创建交互式HTML地图
        html_file = self._create_interactive_map(pca_results, timestamp)
        
        return str(map_file)
    
    def _create_interactive_map(self, pca_results: pd.DataFrame, timestamp: str) -> str:
        """创建交互式HTML文化地图（使用Plotly Python API）"""
        import plotly.graph_objects as go
        
        html_file = self.results_dir / f"cultural_map_interactive_{timestamp}.html"
        
        # 分离数据
        ivs_data = pca_results[pca_results['data_source'] == 'IVS']
        llm_data = pca_results[pca_results['data_source'] != 'IVS']
        
        # 创建figure
        fig = go.Figure()
        
        # 优化的文化区域颜色（更容易区分）
        cultural_colors = {
            'African-Islamic': '#E91E63',      # 粉红色
            'South Asia': '#9C27B0',            # 紫色
            'West & South Asia': '#FF9800',     # 橙色
            'Latin America': '#4CAF50',         # 绿色
            'Confucian': '#DC143C',             # 深红色（Crimson）
            'Baltic': '#00BCD4',                # 青色
            'Protestant Europe': '#2196F3',     # 蓝色
            'Catholic Europe': '#8B4513',       # 棕色（SaddleBrown）
            'English-Speaking': '#32CD32',      # 亮绿色（LimeGreen）
            'Orthodox Europe': '#673AB7'        # 深紫色
        }
        
        # 获取被测试的国家列表
        tested_countries = set()
        if len(llm_data) > 0:
            llm_data_temp = llm_data.copy()
            llm_data_temp['country_name'] = llm_data_temp['data_source'].str.split('_').str[0]
            tested_countries = set(llm_data_temp['country_name'].unique())
        
        # 国家名称映射（IVS中的名称）
        country_name_mapping = {
            "Taiwan": "Taiwan (Province of China)",
            "Russian Federation": "Russian Federation (the)",
            "Saudi Arabia": None,
        }
        
        # 反向映射
        reverse_mapping = {v: k for k, v in country_name_mapping.items() if v is not None}
        
        # 添加真实国家数据（按文化区域）
        if len(ivs_data) > 0 and 'Cultural Region' in ivs_data.columns:
            for region in ivs_data['Cultural Region'].unique():
                if pd.notna(region):
                    region_data = ivs_data[ivs_data['Cultural Region'] == region].copy()
                    if len(region_data) > 0:
                        # 判断每个国家是否被测试
                        region_data['is_tested'] = region_data['Country'].apply(
                            lambda x: reverse_mapping.get(x, x) in tested_countries
                        )
                        
                        # 分别处理被测试和未被测试的国家
                        tested = region_data[region_data['is_tested']]
                        not_tested = region_data[~region_data['is_tested']]
                        
                        # 被测试的国家用星形
                        if len(tested) > 0:
                            fig.add_trace(go.Scatter(
                                x=tested['PC1_rescaled'],
                                y=tested['PC2_rescaled'],
                                mode='markers',
                                name=f'{region} (tested)',
                                text=tested['Country'],
                                marker=dict(
                                    color=cultural_colors.get(region, '#808080'),
                                    size=14,
                                    symbol='star',
                                    line=dict(color='black', width=1.5)
                                ),
                                hovertemplate='<b>%{text}</b><br>Region: ' + region + '<br>Type: Real (Tested)<br>PC1: %{x:.3f}<br>PC2: %{y:.3f}<extra></extra>',
                                legendgroup=region
                            ))
                        
                        # 未被测试的国家用X标记
                        if len(not_tested) > 0:
                            fig.add_trace(go.Scatter(
                                x=not_tested['PC1_rescaled'],
                                y=not_tested['PC2_rescaled'],
                                mode='markers',
                                name=f'{region}',
                                text=not_tested['Country'],
                                marker=dict(
                                    color=cultural_colors.get(region, '#808080'),
                                    size=8,
                                    symbol='x',  # 改用X标记
                                    line=dict(color=cultural_colors.get(region, '#808080'), width=2),
                                    opacity=0.7
                                ),
                                hovertemplate='<b>%{text}</b><br>Region: ' + region + '<br>Type: Real<br>PC1: %{x:.3f}<br>PC2: %{y:.3f}<extra></extra>',
                                legendgroup=region,
                                showlegend=False
                            ))
        
        # 模型标记符号映射（英文用实心，本国语言用空心）
        model_symbols = {
            'openai/gpt-4o-mini': ('circle', 'circle-open'),
            'google/gemini-2.0-flash-001': ('square', 'square-open'),
            'meta-llama/llama-3.3-70b-instruct': ('diamond', 'diamond-open'),
            'deepseek/deepseek-chat-v3-0324': ('triangle-up', 'triangle-up-open'),
            'qwen/qwq-32b': ('pentagon', 'pentagon-open'),
            'mistralai/mistral-nemo': ('hexagon', 'hexagon-open')
        }
        
        # 模型颜色
        model_colors = {
            'openai/gpt-4o-mini': '#FF6B6B',
            'google/gemini-2.0-flash-001': '#4ECDC4',
            'meta-llama/llama-3.3-70b-instruct': '#45B7D1',
            'deepseek/deepseek-chat-v3-0324': '#FFA07A',
            'qwen/qwq-32b': '#98D8C8',
            'mistralai/mistral-nemo': '#F7DC6F'
        }
        
        # 添加LLM数据 - 按模型分组
        if len(llm_data) > 0:
            llm_data = llm_data.copy()
            llm_data['country_name'] = llm_data['data_source'].str.split('_').str[0]
            llm_data['language_type'] = llm_data['data_source'].str.split('_').str[1]
            llm_data['model_name'] = llm_data['data_source'].str.split('_').str[2]
            
            for model in self.config["models"]:
                model_data = llm_data[llm_data['model_name'] == model]
                if len(model_data) == 0:
                    continue
                
                # 获取模型的符号
                symbols = model_symbols.get(model, ('circle', 'circle-open'))
                color = model_colors.get(model, '#999999')
                model_short_name = model.split('/')[-1]
                
                # 英文数据（实心符号）
                english_data = model_data[model_data['language_type'] == 'english']
                if len(english_data) > 0:
                    hover_text = [f"{row['country_name']} ({model_short_name})" for _, row in english_data.iterrows()]
                    fig.add_trace(go.Scatter(
                        x=english_data['PC1_rescaled'],
                        y=english_data['PC2_rescaled'],
                        mode='markers',
                        name=f'{model_short_name} (EN)',
                        text=hover_text,
                        marker=dict(
                            color=color,
                            size=10,
                            symbol=symbols[0],  # 实心
                            line=dict(color='white', width=1)
                        ),
                        hovertemplate='<b>%{text}</b><br>Language: English<br>PC1: %{x:.3f}<br>PC2: %{y:.3f}<extra></extra>',
                        legendgroup=model
                    ))
                
                # 本国语言数据（空心符号）
                native_data = model_data[model_data['language_type'] == 'native']
                if len(native_data) > 0:
                    hover_text = [f"{row['country_name']} ({model_short_name})" for _, row in native_data.iterrows()]
                    fig.add_trace(go.Scatter(
                        x=native_data['PC1_rescaled'],
                        y=native_data['PC2_rescaled'],
                        mode='markers',
                        name=f'{model_short_name} (Native)',
                        text=hover_text,
                        marker=dict(
                            color=color,
                            size=10,
                            symbol=symbols[1],  # 空心
                            line=dict(color=color, width=2)
                        ),
                        hovertemplate='<b>%{text}</b><br>Language: Native<br>PC1: %{x:.3f}<br>PC2: %{y:.3f}<extra></extra>',
                        legendgroup=model,
                        showlegend=True
                    ))
        
        # 设置布局
        fig.update_layout(
            title=dict(
                text='Interactive Cultural Values Map: Real Countries vs LLM Responses<br>' +
                     '<sub>⭐ = Tested Real Countries, ✕ = Other Real Countries | Each model has unique shape | Filled = English, Hollow = Native Language</sub>',
                x=0.5,
                font=dict(size=16, family='Arial')
            ),
            xaxis_title='PC1 (Cultural Dimension 1)',
            yaxis_title='PC2 (Cultural Dimension 2)',
            width=1600,
            height=1000,
            hovermode='closest',
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.01,
                font=dict(size=10)
            ),
            margin=dict(r=250, l=50, t=100, b=50),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        # 添加网格
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        
        # 保存HTML文件
        fig.write_html(html_file)
        
        print(f"🌐 交互式地图已保存: {html_file}")
        return str(html_file)
    
    def _save_pca_results_json(self, pca_results: pd.DataFrame) -> str:
        """保存PCA结果为JSON格式，便于查看和分析"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = self.results_dir / f"pca_results_{timestamp}.json"
        
        # 分离数据
        ivs_data = pca_results[pca_results['data_source'] == 'IVS']
        llm_data = pca_results[pca_results['data_source'] != 'IVS']
        
        # 国家名称映射
        country_name_mapping = {
            "Taiwan": "Taiwan (Province of China)",
            "Russian Federation": "Russian Federation (the)",
            "Saudi Arabia": None,
        }
        
        # 构建结构化数据
        results = {
            "metadata": {
                "timestamp": timestamp,
                "total_entities": len(pca_results),
                "real_countries": len(ivs_data),
                "llm_responses": len(llm_data),
                "experiment_config": {
                    "countries": len(self.config["country_language_pairs"]),
                    "models": len(self.config["models"]),
                    "repeat_count": self.config["repeat_count"]
                }
            },
            "real_countries": [],
            "llm_responses": [],
            "country_comparisons": []
        }
        
        # 添加真实国家数据
        for _, row in ivs_data.iterrows():
            country_data = {
                "country": row.get('Country', ''),
                "country_code": row.get('country_code', ''),
                "cultural_region": row.get('Cultural Region', ''),
                "coordinates": {
                    "PC1": float(row['PC1_rescaled']),
                    "PC2": float(row['PC2_rescaled'])
                }
            }
            results["real_countries"].append(country_data)
        
        # 添加LLM数据
        for _, row in llm_data.iterrows():
            # 解析data_source
            parts = row['data_source'].split('_')
            if len(parts) >= 3:
                country_name = parts[0]
                language_type = parts[1]
                model_name = parts[2]
                
                llm_response = {
                    "data_source": row['data_source'],
                    "country": country_name,
                    "language_type": language_type,
                    "model": model_name,
                    "coordinates": {
                        "PC1": float(row['PC1_rescaled']),
                        "PC2": float(row['PC2_rescaled'])
                    }
                }
                results["llm_responses"].append(llm_response)
        
        # 添加国家对比数据（包含距离信息）
        for country in self.config["country_language_pairs"].keys():
            # 获取真实国家数据
            ivs_country_name = country_name_mapping.get(country, country)
            if ivs_country_name is None:
                continue
                
            real_country = ivs_data[ivs_data['Country'] == ivs_country_name]
            if len(real_country) == 0:
                continue
            
            real_coords = {
                "PC1": float(real_country['PC1_rescaled'].iloc[0]),
                "PC2": float(real_country['PC2_rescaled'].iloc[0])
            }
            
            # 获取该国家的LLM数据
            country_llm = llm_data[llm_data['data_source'].str.startswith(country + '_')]
            
            english_responses = []
            native_responses = []
            
            for _, llm_row in country_llm.iterrows():
                parts = llm_row['data_source'].split('_')
                if len(parts) >= 3:
                    language_type = parts[1]
                    model_name = parts[2]
                    
                    llm_coords = {
                        "PC1": float(llm_row['PC1_rescaled']),
                        "PC2": float(llm_row['PC2_rescaled'])
                    }
                    
                    # 计算距离
                    distance = np.sqrt((llm_coords["PC1"] - real_coords["PC1"])**2 + 
                                     (llm_coords["PC2"] - real_coords["PC2"])**2)
                    
                    response_data = {
                        "model": model_name,
                        "coordinates": llm_coords,
                        "distance_to_real": float(distance)
                    }
                    
                    if language_type == 'english':
                        english_responses.append(response_data)
                    elif language_type == 'native':
                        native_responses.append(response_data)
            
            # 计算平均距离
            avg_english_distance = np.mean([r["distance_to_real"] for r in english_responses]) if english_responses else float('inf')
            avg_native_distance = np.mean([r["distance_to_real"] for r in native_responses]) if native_responses else float('inf')
            
            # 确定获胜者
            if avg_english_distance < avg_native_distance:
                winner = "English"
            elif avg_native_distance < avg_english_distance:
                winner = "Native"
            else:
                winner = "Tie"
            
            country_comparison = {
                "country": country,
                "real_country_name": ivs_country_name,
                "real_coordinates": real_coords,
                "english_responses": english_responses,
                "native_responses": native_responses,
                "summary": {
                    "avg_english_distance": float(avg_english_distance),
                    "avg_native_distance": float(avg_native_distance),
                    "winner": winner,
                    "english_count": len(english_responses),
                    "native_count": len(native_responses)
                }
            }
            results["country_comparisons"].append(country_comparison)
        
        # 保存JSON文件
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"📄 PCA结果JSON已保存: {json_file}")
        return str(json_file)
    
    def _filter_outlier_data(self, pca_results: pd.DataFrame) -> pd.DataFrame:
        """过滤异常的LLM数据点"""
        
        # 分离数据
        ivs_data = pca_results[pca_results['data_source'] == 'IVS']
        llm_data = pca_results[pca_results['data_source'] != 'IVS']
        
        print(f"🔍 数据过滤前: IVS={len(ivs_data)}, LLM={len(llm_data)}")
        
        # 计算IVS数据的正常范围（用于定义异常阈值）
        ivs_pc1_range = (ivs_data['PC1_rescaled'].min(), ivs_data['PC1_rescaled'].max())
        ivs_pc2_range = (ivs_data['PC2_rescaled'].min(), ivs_data['PC2_rescaled'].max())
        
        # 扩展阈值范围（允许一定的合理偏差）
        pc1_margin = (ivs_pc1_range[1] - ivs_pc1_range[0]) * 0.5  # 50%的边距
        pc2_margin = (ivs_pc2_range[1] - ivs_pc2_range[0]) * 0.5
        
        pc1_threshold = (ivs_pc1_range[0] - pc1_margin, ivs_pc1_range[1] + pc1_margin)
        pc2_threshold = (ivs_pc2_range[0] - pc2_margin, ivs_pc2_range[1] + pc2_margin)
        
        print(f"📊 IVS数据范围: PC1=[{ivs_pc1_range[0]:.3f}, {ivs_pc1_range[1]:.3f}], PC2=[{ivs_pc2_range[0]:.3f}, {ivs_pc2_range[1]:.3f}]")
        print(f"📊 过滤阈值: PC1=[{pc1_threshold[0]:.3f}, {pc1_threshold[1]:.3f}], PC2=[{pc2_threshold[0]:.3f}, {pc2_threshold[1]:.3f}]")
        
        # 识别异常数据
        outliers = llm_data[
            (llm_data['PC1_rescaled'] < pc1_threshold[0]) | 
            (llm_data['PC1_rescaled'] > pc1_threshold[1]) |
            (llm_data['PC2_rescaled'] < pc2_threshold[0]) | 
            (llm_data['PC2_rescaled'] > pc2_threshold[1])
        ]
        
        # 保留正常数据
        normal_llm = llm_data[
            (llm_data['PC1_rescaled'] >= pc1_threshold[0]) & 
            (llm_data['PC1_rescaled'] <= pc1_threshold[1]) &
            (llm_data['PC2_rescaled'] >= pc2_threshold[0]) & 
            (llm_data['PC2_rescaled'] <= pc2_threshold[1])
        ]
        
        print(f"⚠️ 发现异常数据: {len(outliers)} 个")
        print(f"✅ 保留正常数据: {len(normal_llm)} 个")
        
        if len(outliers) > 0:
            print(f"🔍 异常数据详情:")
            # 按模型统计异常数据
            outlier_models = {}
            for _, row in outliers.iterrows():
                parts = row['data_source'].split('_')
                if len(parts) >= 3:
                    model = parts[2]
                    if model not in outlier_models:
                        outlier_models[model] = 0
                    outlier_models[model] += 1
            
            for model, count in sorted(outlier_models.items(), key=lambda x: x[1], reverse=True):
                print(f"   {model}: {count} 个异常点")
        
        # 合并过滤后的数据
        filtered_results = pd.concat([ivs_data, normal_llm], ignore_index=True)
        
        print(f"🔍 数据过滤后: 总计={len(filtered_results)} (IVS={len(ivs_data)}, LLM={len(normal_llm)})")
        
        return filtered_results
    
    def _analyze_distances(self, pca_results: pd.DataFrame) -> Dict[str, Any]:
        """分析距离 - 完整版本"""
        
        # 分离数据
        ivs_data = pca_results[pca_results['data_source'] == 'IVS']
        llm_data = pca_results[pca_results['data_source'] != 'IVS']
        
        # 国家名称映射 - 处理IVS中的特殊命名
        country_name_mapping = {
            "Taiwan": "Taiwan (Province of China)",
            "Russian Federation": "Russian Federation (the)",
            "Saudi Arabia": None,  # IVS中不存在
        }
        
        distance_analysis = {}
        
        for country in self.config["country_language_pairs"].keys():
            print(f"\n📏 分析 {country}:")
            
            # 获取IVS中的实际国家名称
            ivs_country_name = country_name_mapping.get(country, country)
            
            if ivs_country_name is None:
                print(f"   ⚠️ {country} 在IVS数据中不存在")
                continue
            
            # 找到真实国家位置
            real_country = ivs_data[ivs_data['Country'] == ivs_country_name]
            if len(real_country) == 0:
                print(f"   ⚠️ 未找到 {country} 的真实数据 (查找名称: {ivs_country_name})")
                continue
            
            real_x = real_country['PC1_rescaled'].iloc[0]
            real_y = real_country['PC2_rescaled'].iloc[0]
            
            print(f"   🎯 真实位置: PC1={real_x:.6f}, PC2={real_y:.6f}")
            
            # 找到该国家的LLM数据
            country_llm = llm_data[llm_data['data_source'].str.startswith(country)]
            
            print(f"   📊 找到 {len(country_llm)} 个LLM数据点")
            
            english_distances = []
            native_distances = []
            
            for _, row in country_llm.iterrows():
                llm_x = row['PC1_rescaled']
                llm_y = row['PC2_rescaled']
                distance = np.sqrt((llm_x - real_x)**2 + (llm_y - real_y)**2)
                
                # 从data_source中提取语言类型
                data_source = row.get('data_source', '')
                if '_english_' in data_source:
                    lang_type = 'english'
                    english_distances.append(distance)
                elif '_native_' in data_source:
                    lang_type = 'native'
                    native_distances.append(distance)
                else:
                    lang_type = 'unknown'
                
                # 提取模型名
                parts = data_source.split('_')
                model = parts[-1] if len(parts) > 2 else 'unknown'
                
                print(f"   🤖 {model} ({lang_type}): PC1={llm_x:.6f}, PC2={llm_y:.6f}, 距离={distance:.6f}")
            
            # 计算平均距离
            avg_english = np.mean(english_distances) if english_distances else float('inf')
            avg_native = np.mean(native_distances) if native_distances else float('inf')
            
            print(f"   📊 汇总:")
            print(f"      英文平均距离: {avg_english:.6f} ({len(english_distances)} 个数据点)")
            print(f"      本国语言平均距离: {avg_native:.6f} ({len(native_distances)} 个数据点)")
            print(f"      差距: {abs(avg_english - avg_native):.6f}")
            
            if avg_english < avg_native:
                print(f"      🏆 英文更接近真实国家 (差距: {avg_native - avg_english:.6f})")
                winner = "English"
            elif avg_native < avg_english:
                print(f"      🏆 本国语言更接近真实国家 (差距: {avg_english - avg_native:.6f})")
                winner = "Native"
            else:
                print(f"      🤝 两种语言距离相等")
                winner = "Tie"
            
            distance_analysis[country] = {
                "real_position": {"PC1": real_x, "PC2": real_y},
                "english_distances": english_distances,
                "native_distances": native_distances,
                "avg_english_distance": avg_english,
                "avg_native_distance": avg_native,
                "winner": winner,
                "difference": abs(avg_english - avg_native)
            }
        
        return distance_analysis
    
    def _analyze_model_performance(self, pca_results: pd.DataFrame) -> Dict[str, Any]:
        """分析模型表现"""
        
        # 分离数据
        ivs_data = pca_results[pca_results['data_source'] == 'IVS']
        llm_data = pca_results[pca_results['data_source'] != 'IVS']
        
        # 国家名称映射
        country_name_mapping = {
            "Taiwan": "Taiwan (Province of China)",
            "Russian Federation": "Russian Federation (the)",
            "Saudi Arabia": None,  # IVS中不存在
        }
        
        model_analysis = {}
        
        for model in self.config["models"]:
            print(f"\n🤖 分析模型: {model}")
            
            model_english_distances = []
            model_native_distances = []
            
            for country in self.config["country_language_pairs"].keys():
                # 获取IVS中的实际国家名称
                ivs_country_name = country_name_mapping.get(country, country)
                if ivs_country_name is None:
                    continue
                
                # 找到真实国家位置
                real_country = ivs_data[ivs_data['Country'] == ivs_country_name]
                if len(real_country) == 0:
                    continue
                    
                real_x = real_country['PC1_rescaled'].iloc[0]
                real_y = real_country['PC2_rescaled'].iloc[0]
                
                # 找到该模型对该国家的数据
                model_data = llm_data[llm_data['data_source'].str.contains(model.replace('/', '/'))]
                country_model_data = model_data[model_data['data_source'].str.startswith(country)]
                
                english_data = country_model_data[country_model_data['data_source'].str.contains('_english_')]
                native_data = country_model_data[country_model_data['data_source'].str.contains('_native_')]
                
                # 计算距离
                if len(english_data) > 0:
                    eng_x = english_data['PC1_rescaled'].iloc[0]
                    eng_y = english_data['PC2_rescaled'].iloc[0]
                    eng_distance = np.sqrt((eng_x - real_x)**2 + (eng_y - real_y)**2)
                    model_english_distances.append(eng_distance)
                
                if len(native_data) > 0:
                    nat_x = native_data['PC1_rescaled'].iloc[0]
                    nat_y = native_data['PC2_rescaled'].iloc[0]
                    nat_distance = np.sqrt((nat_x - real_x)**2 + (nat_y - real_y)**2)
                    model_native_distances.append(nat_distance)
            
            # 计算该模型的总体表现
            avg_english = np.mean(model_english_distances) if model_english_distances else float('inf')
            avg_native = np.mean(model_native_distances) if model_native_distances else float('inf')
            
            model_analysis[model] = {
                'avg_english_distance': avg_english,
                'avg_native_distance': avg_native,
                'english_distances': model_english_distances,
                'native_distances': model_native_distances,
                'countries_count': len(model_english_distances)
            }
            
            print(f"   📊 总体表现:")
            print(f"      平均英文距离: {avg_english:.3f}")
            print(f"      平均本国语言距离: {avg_native:.3f}")
            
            if avg_english < avg_native:
                print(f"      🏆 该模型英文表现更好")
            elif avg_native < avg_english:
                print(f"      🏆 该模型本国语言表现更好")
            else:
                print(f"      🤝 该模型两种语言表现相当")
        
        return model_analysis
    
    def _generate_report(self, interview_data: Dict, pca_results: pd.DataFrame, 
                        distance_analysis: Dict, model_analysis: Dict, 
                        map_file: str, timestamp: str) -> Dict[str, Any]:
        """生成分析报告"""
        
        report = {
            "experiment_info": {
                "title": "扩展多语言文化价值实验",
                "timestamp": timestamp,
                "config": self.config
            },
            "data_summary": {
                "countries_tested": list(self.config["country_language_pairs"].keys()),
                "models_tested": self.config["models"],
                "total_pca_entities": len(pca_results),
                "ivs_countries": len(pca_results[pca_results['data_source'] == 'IVS']),
                "llm_data_points": len(pca_results[pca_results['data_source'] != 'IVS'])
            },
            "distance_analysis": distance_analysis,
            "model_analysis": model_analysis,
            "key_findings": [],
            "files_generated": {
                "cultural_map": map_file,
                "pca_results": str(self.results_dir / f"pca_results_{timestamp}.pkl"),
                "interview_data": str(self.results_dir / f"interview_data_{timestamp}.json")
            }
        }
        
        # 统计获胜情况
        english_wins = sum(1 for analysis in distance_analysis.values() if analysis.get("winner") == "English")
        native_wins = sum(1 for analysis in distance_analysis.values() if analysis.get("winner") == "Native")
        ties = sum(1 for analysis in distance_analysis.values() if analysis.get("winner") == "Tie")
        
        # 模型排名（只有在有有效数据时才排名）
        valid_models = [m for m in self.config["models"] if model_analysis[m]['avg_english_distance'] != float('inf')]
        english_ranking = sorted(valid_models, key=lambda m: model_analysis[m]['avg_english_distance']) if valid_models else []
        native_ranking = sorted(valid_models, key=lambda m: model_analysis[m]['avg_native_distance']) if valid_models else []
        
        # 安全的百分比计算
        total_analyzed = len(distance_analysis)
        english_pct = (english_wins/total_analyzed*100) if total_analyzed > 0 else 0
        native_pct = (native_wins/total_analyzed*100) if total_analyzed > 0 else 0
        ties_pct = (ties/total_analyzed*100) if total_analyzed > 0 else 0
        
        report["key_findings"] = [
            f"测试了 {len(self.config['country_language_pairs'])} 个国家的语言对比",
            f"使用了 {len(self.config['models'])} 个不同的LLM模型",
            f"成功分析了 {total_analyzed} 个国家 (其中 {len(self.config['country_language_pairs']) - total_analyzed} 个国家在IVS中缺失)",
            f"英文获胜: {english_wins} 个国家 ({english_pct:.1f}%)",
            f"本国语言获胜: {native_wins} 个国家 ({native_pct:.1f}%)",
            f"平局: {ties} 个国家 ({ties_pct:.1f}%)",
            f"英文表现最佳模型: {english_ranking[0] if english_ranking else '无有效数据'}",
            f"本国语言表现最佳模型: {native_ranking[0] if native_ranking else '无有效数据'}",
            f"PCA空间包含 {report['data_summary']['ivs_countries']} 个真实国家和 {report['data_summary']['llm_data_points']} 个LLM数据点"
        ]
        
        # 保存报告
        report_file = self.results_dir / f"analysis_report_{timestamp}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            # 转换numpy类型
            def convert_numpy(obj):
                if isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                return obj
            
            def deep_convert(obj):
                if isinstance(obj, dict):
                    return {k: deep_convert(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [deep_convert(v) for v in obj]
                else:
                    return convert_numpy(obj)
            
            converted_report = deep_convert(report)
            json.dump(converted_report, f, ensure_ascii=False, indent=2)
        
        # 保存PCA结果
        pca_file = self.results_dir / f"pca_results_{timestamp}.pkl"
        pca_results.to_pickle(pca_file)
        
        print(f"📋 分析报告已保存: {report_file}")
        
        return report
    
    def _load_existing_data(self) -> Dict[str, Any]:
        """加载现有数据"""
        # 查找最新的数据文件
        data_files = list(self.results_dir.glob("interview_data_*.json"))
        if not data_files:
            raise FileNotFoundError("未找到现有的访谈数据文件")
        
        latest_file = max(data_files, key=lambda x: x.stat().st_mtime)
        print(f"📂 加载数据文件: {latest_file}")
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            return json.load(f)


def main():
    """主函数"""
    import sys
    
    print("🎯 扩展多语言文化价值实验")
    print("=" * 50)
    print()
    print("实验目标: 使用更多模型和国家比较LLM用英文vs本国语言模仿各国时的文化价值表达差异")
    print()
    
    experiment = ExtendedMultilingualExperiment()
    
    # 支持命令行参数（精确匹配）
    use_existing = "--existing" in sys.argv
    use_optimized = "--optimized" in sys.argv or "--opt" in sys.argv  # 支持简写
    run_full = "--full" in sys.argv
    
    if use_optimized:
        print("🚀 选择: 优化模式 (3次采样 + 并行处理 + 众数投票)")
        print("   📊 基于稳定性分析: 80%一致性，3次采样足够稳定")
        experiment.config["repeat_count"] = 3
        experiment.config["use_majority_vote"] = True
        experiment.config["max_workers"] = 4
    
    if run_full or use_optimized:
        print("选择: 运行完整实验")
        results = experiment.run_experiment(use_existing_data=False)
    elif use_existing:
        print("选择: 仅分析现有数据")
        try:
            results = experiment.run_experiment(use_existing_data=True)
        except FileNotFoundError as e:
            print(f"❌ {e}")
            print("将运行完整实验...")
            results = experiment.run_experiment(use_existing_data=False)
    else:
        print("选择: 仅分析现有数据")
        try:
            results = experiment.run_experiment(use_existing_data=True)
        except FileNotFoundError as e:
            print(f"❌ {e}")
            print("将运行完整实验...")
            results = experiment.run_experiment(use_existing_data=False)
    
    # 显示结果摘要
    print("\n" + "="*50)
    print("📊 实验结果摘要")
    print("="*50)
    
    # 读取报告文件显示关键发现
    try:
        with open(results["report_file"], 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        for finding in report["key_findings"]:
            print(f"• {finding}")
        
        print(f"\n📁 结果文件:")
        for file_type, file_path in report["files_generated"].items():
            print(f"  {file_type}: {file_path}")
    except Exception as e:
        print(f"无法读取报告: {e}")


if __name__ == "__main__":
    main()
