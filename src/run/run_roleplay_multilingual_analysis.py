#!/usr/bin/env python3
"""
完整的Roleplay Multilingual分析运行脚本
从多语言角色扮演回答数据处理到PCA分析再到可视化的完整流程
包含英文vs本国语言的效果对比分析

数据存储规则：
- 处理后的数据和PCA计算结果 -> data/roleplay_multilingual/
- 输出图片和文化坐标数据 -> results/roleplay_multilingual/
"""

import os
import sys
import copy
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
import json
import matplotlib.pyplot as plt
from typing import Dict, Any
try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    print("⚠️ 警告: plotly未安装，将跳过交互式图表生成")
    PLOTLY_AVAILABLE = False
    go = None
    px = None

from scipy.spatial.distance import euclidean

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# 导入所需模块
from src.roleplay_multilingual.multilingual_roleplay_data_processor import MultilingualRoleplayDataProcessor
from src.roleplay_multilingual.multilingual_roleplay_pca_analysis import MultilingualRoleplayPCAAnalysis, LanguageComparisonAnalyzer
from src.roleplay_multilingual.multilingual_roleplay_visualization import MultilingualRoleplayVisualizer


class RoleplayMultilingualAnalysisRunner:
    """Roleplay Multilingual完整分析运行器"""
    
    def __init__(self, project_root=None):
        if project_root is None:
            self.project_root = Path(__file__).parent.parent.parent
        else:
            self.project_root = Path(project_root)
        
        # 设置路径
        self.data_path = self.project_root / "data" / "roleplay_multilingual"
        self.results_path = self.project_root / "results" / "roleplay_multilingual"
        self.country_values_data_path = self.project_root / "data" / "country_values"
        self.roleplay_english_data_path = self.project_root / "data" / "roleplay_English"
        
        # 确保目录存在
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.results_path.mkdir(parents=True, exist_ok=True)
        
        # 初始化可视化器实例（复用于所有可视化方法，从base继承颜色映射）
        self.visualizer = MultilingualRoleplayVisualizer(
            data_path=str(self.project_root / "data"),
            results_path=str(self.results_path)
        )
        self.cultural_region_colors = self.visualizer.cultural_region_colors
        self.llm_model_colors = self.visualizer.llm_model_colors
        
        # 初始化语言对比分析器
        self.language_analyzer = LanguageComparisonAnalyzer()
        
        print(f"🏠 项目根目录: {self.project_root}")
        print(f"📁 Multilingual数据目录: {self.data_path}")
        print(f"📁 结果目录: {self.results_path}")
        print(f"📁 Country Values数据目录: {self.country_values_data_path}")
        print(f"📁 English Roleplay数据目录: {self.roleplay_english_data_path}")
    
    def _load_countries_from_config(self, config_file: Path, default_countries: list) -> list:
        """从配置文件加载国家列表"""
        try:
            if not config_file.exists():
                print("📋 配置文件不存在，使用默认国家列表")
                return default_countries
            
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    print("⚠️ 配置文件为空，使用默认国家列表")
                    return default_countries
                recommended_data = json.loads(content)
            
            # 提取国家列表
            countries = []
            if isinstance(recommended_data, dict):
                for lang, country_list in recommended_data.items():
                    if lang != 'metadata' and isinstance(country_list, list):
                        for country_info in country_list:
                            if isinstance(country_info, dict) and 'name' in country_info:
                                country_name = country_info['name']
                                if country_name not in countries:
                                    countries.append(country_name)
            
            if not countries:
                countries = recommended_data.get('countries', default_countries)
            
            print(f"✅ 成功加载推荐国家列表: {len(countries)} 个国家")
            return countries
            
        except Exception as e:
            print(f"⚠️ 加载配置文件失败: {e}")
            return default_countries
    
    def step0_multilingual_interview(self):
        """步骤0: 多语言角色扮演访谈"""
        print("\n" + "="*60)
        print("🎤 步骤0: 多语言角色扮演访谈")
        print("="*60)
        
        try:
            # 导入多语言访谈模块
            from src.roleplay_multilingual.multilingual_roleplay_interview import MultilingualRoleplayInterview
            
            # 初始化访谈器（每个问题重复2次取众数 - 小规模测试）
            interviewer = MultilingualRoleplayInterview(consensus_count=2, data_path=str(self.data_path))
            
            # 检查是否已有访谈数据
            existing_files = list(self.data_path.glob("interview_data_*.json"))
            if existing_files:
                latest_file = max(existing_files, key=lambda x: x.stat().st_mtime)
                print(f"✅ 发现已有访谈数据: {latest_file}")
                
                # 检查数据完整性
                with open(latest_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                
                # 检查数据格式并统计
                if isinstance(existing_data, dict) and any(isinstance(v, dict) for v in existing_data.values()):
                    # 新格式: {country: {language: {model: [responses...]}}}
                    total_countries = len(existing_data)
                    total_entries = 0
                    for country_data in existing_data.values():
                        if isinstance(country_data, dict):
                            for language_data in country_data.values():
                                if isinstance(language_data, dict):
                                    for model_responses in language_data.values():
                                        if isinstance(model_responses, list):
                                            total_entries += len(model_responses)
                    
                    print(f"📊 现有访谈数据统计:")
                    print(f"   - 国家数量: {total_countries}")
                    print(f"   - 总访谈条目: {total_entries}")
                else:
                    # 旧格式: {responses: {...}}
                    total_entries = len(existing_data.get('responses', {}))
                    print(f"📊 现有访谈条目: {total_entries}")
                
                # 如果有任何数据，询问用户选择
                if total_entries > 0:
                    print("💡 发现充足的访谈数据")
                    print("请选择操作:")
                    print("  1. 使用现有数据，跳过访谈")
                    print("  2. 重新进行访谈（会生成新的时间戳文件）")
                    print("  3. 进行全面测试（每语言3国家，所有模型，每问题5次重复取众数）")
                    
                    while True:
                        try:
                            choice = input("请输入选择 (1, 2 或 3): ").strip()
                            if choice == "1":
                                print("✅ 选择使用现有数据，跳过访谈步骤")
                                return True
                            elif choice == "2":
                                print("🔄 选择重新访谈，将生成新的数据文件")
                                break
                            elif choice == "3":
                                print("🚀 选择全面测试，将进行大规模访谈")
                                return self._run_comprehensive_test()
                            else:
                                print("❌ 无效选择，请输入 1, 2 或 3")
                        except (EOFError, KeyboardInterrupt):
                            print("\n⏹️ 用户取消，使用现有数据")
                            return True
            
            print("\n🚀 开始多语言角色扮演访谈...")
            
            # 默认国家列表 - 使用完整配置（32个国家）
            # 配置来自 config/questions/multilingual/multilingual_questions_complete.json
            default_countries = [
                'China', 'United States'  # 最小默认集合
            ]
            
            # 从配置文件加载国家列表
            config_file = self.project_root / "config" / "questions" / "multilingual" / "multilingual_questions_complete.json"
            countries_to_interview = self._load_countries_from_config(config_file, default_countries)
            
            print(f"🎯 将访谈 {len(countries_to_interview)} 个国家")
            
            # 执行批量访谈
            print(f"\n🎯 开始批量多语言访谈...")
            
            try:
                # 使用现有的run_multilingual_experiment方法（启用增量访谈）
                interview_results = interviewer.run_multilingual_experiment(
                    models=None,  # 使用所有可用模型
                    max_workers=8,  # 高并发模式（加快速度）
                    skip_existing=True  # 启用增量访谈，跳过已完成的访谈
                )
            except Exception as e:
                print(f"❌ 访谈过程中发生错误: {e}")
                print("🔄 尝试使用单线程模式重新访谈...")
                try:
                    interview_results = interviewer.run_multilingual_experiment(
                        models=None,
                        max_workers=1,  # 单线程模式
                        skip_existing=True  # 启用增量访谈
                    )
                except Exception as e2:
                    print(f"❌ 单线程访谈也失败: {e2}")
                    import traceback
                    traceback.print_exc()
                    return False
            
            # 关键修复：检查返回结果的结构
            # run_multilingual_experiment返回的数据已经保存到文件了
            # 只要有total_tasks > 0就说明有数据
            if interview_results and interview_results.get('total_tasks', 0) > 0:
                print(f"✅ 多语言访谈完成!")
                print(f"📊 访谈统计:")
                print(f"   - 总任务数: {interview_results.get('total_tasks', 0)}")
                print(f"   - 成功任务数: {interview_results.get('successful_tasks', 0)}")
                success_rate = interview_results.get('successful_tasks', 0) / max(interview_results.get('total_tasks', 1), 1)
                print(f"   - 成功率: {success_rate:.1%}")
                
                # 数据已经由访谈器保存到PKL和JSON文件了
                # 不需要再次保存，直接返回True继续后续步骤
                print(f"💾 访谈数据已自动保存到: data/roleplay_multilingual/llm_responses_roleplay_ml/")
                print(f"✅ 跳过重复保存，继续后续步骤...")
                return True
            else:
                print(f"❌ 多语言访谈失败或无结果")
                print("💡 可能的原因:")
                print("   - API密钥问题")
                print("   - 网络连接问题") 
                print("   - 模型配置问题")
                print("   - 访谈器初始化问题")
                print("   - 推荐国家配置问题")
                
                # 检查是否有现有数据可以使用
                existing_files = list(self.data_path.glob("interview_data_*.json"))
                if existing_files:
                    print(f"💡 发现 {len(existing_files)} 个现有访谈文件，可以继续后续步骤")
                
                return False
                
        except Exception as e:
            print(f"❌ 多语言访谈失败: {e}")
            import traceback
            traceback.print_exc()
            
            # 检查是否有现有数据可以使用
            existing_files = list(self.data_path.glob("interview_data_*.json"))
            if existing_files:
                print(f"💡 虽然访谈失败，但发现 {len(existing_files)} 个现有访谈文件")
                print("❌ 多语言访谈失败，但可能已有数据，继续后续步骤")
            else:
                print("❌ 访谈失败且无现有数据，无法继续")
            
            return False
    
    def _run_comprehensive_test(self) -> bool:
        """运行全面测试"""
        try:
            print("\n" + "="*60)
            print("🚀 启动全面多语言测试")
            print("="*60)
            
            # 导入全面测试模块
            from src.roleplay_multilingual.comprehensive_multilingual_test import ComprehensiveMultilingualTest
            
            # 创建测试实例
            tester = ComprehensiveMultilingualTest(
                config_path="config/questions/multilingual/comprehensive_multilingual_config.json"
            )
            
            # 运行测试（使用高并发加快速度）
            results = tester.run_comprehensive_test(max_workers=8)
            
            if results and results.get('results'):
                print("✅ 全面测试完成，数据已保存")
                
                # 将结果转换为标准格式以便后续处理
                self._convert_comprehensive_results_to_standard_format(results)
                
                print("\n🔄 全面测试完成，继续执行后续分析步骤...")
                return True  # 返回True表示访谈步骤成功，继续后续步骤
            else:
                print("❌ 全面测试失败或被取消")
                return False
                
        except Exception as e:
            print(f"❌ 全面测试执行失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _run_small_scale_test(self) -> bool:
        """运行小规模验证测试"""
        try:
            print("\n" + "="*60)
            print("🧪 启动小规模验证测试")
            print("="*60)
            
            # 导入小规模测试模块
            from src.roleplay_multilingual.comprehensive_multilingual_test import ComprehensiveMultilingualTest
            
            # 创建测试实例（使用小规模配置）
            tester = ComprehensiveMultilingualTest(
                config_path="config/questions/multilingual/small_scale_test_config.json"
            )
            
            # 运行小规模测试（适度并发）
            results = tester.run_comprehensive_test(max_workers=8)
            
            if results and results.get('results'):
                print("✅ 小规模测试完成，数据已保存")
                
                # 将结果转换为标准格式以便后续处理
                self._convert_comprehensive_results_to_standard_format(results)
                
                print("\n🔄 小规模测试完成，继续执行后续分析步骤...")
                
                # 继续执行后续步骤
                print("\n🔄 继续执行数据处理...")
                if self.step1_data_processing():
                    print("\n🔄 继续执行PCA分析...")
                    if self.step2_pca_analysis():
                        print("\n🔄 继续执行可视化...")
                        return self.step3_language_comparison_analysis()
                
                return False
            else:
                print("❌ 小规模测试失败或被取消")
                return False
                
        except Exception as e:
            print(f"❌ 小规模测试执行失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _convert_latest_roleplay_results_to_standard_format(self) -> None:
        """将最新的roleplay_results转换为标准interview_data格式"""
        try:
            # 查找最新的roleplay_results文件（优先使用pkl，占用空间小）
            results_dir = self.data_path / "llm_responses_roleplay_ml"
            
            # 优先pkl，然后json
            pkl_files = list(results_dir.glob("roleplay_results_ml_*.pkl"))
            json_files = list(results_dir.glob("roleplay_results_ml_*.json"))
            
            latest_file = None
            if pkl_files:
                latest_file = max(pkl_files, key=lambda x: x.stat().st_mtime)
                print(f"✅ 优先使用 PKL 文件: {latest_file.name}")
            elif json_files:
                latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
            
            if not latest_file:
                print("⚠️ 未找到roleplay_results文件，跳过转换")
                return
            
            print(f"📂 加载: {latest_file.name}")
            
            # 加载数据
            if latest_file.suffix == '.pkl':
                with open(latest_file, 'rb') as f:
                    import pickle
                    data = pickle.load(f)
            else:
                with open(latest_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            
            # 提取results列表
            results_list = data.get('results', [])
            if not results_list:
                print("⚠️ 数据为空，跳过转换")
                return
            
            # 转换为interview_data格式
            interview_data = {}
            for result in results_list:
                model = result.get('model_name')
                country = result.get('country')
                language = result.get('language')
                responses = result.get('responses', [])
                
                # 初始化嵌套结构
                if country not in interview_data:
                    interview_data[country] = {}
                if language not in interview_data[country]:
                    interview_data[country][language] = {}
                if model not in interview_data[country][language]:
                    interview_data[country][language][model] = []
                
                # 添加回答
                interview_data[country][language][model].append(result)
            
            # 保存为interview_data格式
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.data_path / f"interview_data_{timestamp}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(interview_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 已转换并保存: {output_file.name}")
            print(f"   包含 {len(results_list)} 个访谈结果")
            
        except Exception as e:
            print(f"⚠️ 转换失败: {e}")
            import traceback
            traceback.print_exc()
    
    def _convert_comprehensive_results_to_standard_format(self, comprehensive_results: Dict) -> None:
        """将全面测试结果转换为标准格式"""
        try:
            print("\n🔄 转换全面测试结果为标准格式...")
            
            # 提取结果数据
            results_data = comprehensive_results.get('results', [])
            timestamp = comprehensive_results.get('timestamp', datetime.now().strftime("%Y%m%d_%H%M%S"))
            
            # 转换为标准的interview_data格式
            standard_format = {}
            
            for result in results_data:
                if not result.get('success', False):
                    continue
                
                country = result['country']
                language = result['language']
                model = result['model']
                
                # 初始化嵌套结构
                if country not in standard_format:
                    standard_format[country] = {}
                if language not in standard_format[country]:
                    standard_format[country][language] = {}
                if model not in standard_format[country][language]:
                    standard_format[country][language][model] = []
                
                # 添加处理后的回答（众数结果）
                response_entry = {
                    "model_name": model,
                    "country": country,
                    "language": language,
                    "responses": result.get('responses', []),
                    "overall_confidence": result.get('overall_confidence', 0),
                    "majority_stats": result.get('majority_stats', {}),
                    "timestamp": result.get('timestamp'),
                    "is_comprehensive_test": True,
                    "repeat_count": comprehensive_results.get('experiment_config', {}).get('repeat_count', 5)
                }
                
                standard_format[country][language][model].append(response_entry)
            
            # 保存为标准格式
            output_file = self.data_path / f"interview_data_{timestamp}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(standard_format, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 标准格式数据已保存: {output_file.name}")
            
        except Exception as e:
            print(f"⚠️ 格式转换失败: {e}")
            # 不影响主流程，继续执行
    
    def step1_data_processing(self, test_type: str = None):
        """步骤1: 多语言Roleplay数据处理"""
        print("\n" + "="*60)
        print("📊 步骤1: 多语言Roleplay数据处理")
        print("="*60)
        
        try:
            # 初始化数据处理器（传入data/目录，不是data/roleplay_multilingual）
            data_root = self.project_root / "data"
            processor = MultilingualRoleplayDataProcessor(data_path=str(data_root))
            
            # 数据处理器会自动查找最新的roleplay_results_ml_*.pkl或*.json文件
            # 不需要手动查找interview_data文件
            
            # 查找已有的处理后数据文件（根据测试类型，使用新的命名规则）
            if test_type:
                # 查找特定测试类型的处理文件
                processed_data_files = list(self.data_path.glob(f"llm_roleplay_ml_processed_responses_ivs_format_{test_type}_*.pkl"))
                if not processed_data_files:
                    # 如果没有找到特定类型的，查找通用的
                    processed_data_files = list(self.data_path.glob("llm_roleplay_ml_processed_responses_ivs_format_*.pkl"))
                if not processed_data_files:
                    # 兼容旧的命名规则
                    processed_data_files = list(self.data_path.glob("multilingual_roleplay_processed_responses_ivs_format_*.pkl"))
                    if processed_data_files:
                        print("⚠️ 发现旧格式文件，建议重新处理数据")
            else:
                processed_data_files = list(self.data_path.glob("llm_roleplay_ml_processed_responses_ivs_format_*.pkl"))
                if not processed_data_files:
                    # 兼容旧的命名规则
                    processed_data_files = list(self.data_path.glob("multilingual_roleplay_processed_responses_ivs_format_*.pkl"))
                    if processed_data_files:
                        print("⚠️ 发现旧格式文件，建议重新处理数据")
            
            # 检查是否需要重新处理
            need_reprocess = True
            latest_result_file = None  # 初始化变量
            
            if processed_data_files:
                # 使用最新的处理文件
                latest_processed_file = max(processed_data_files, key=lambda x: x.stat().st_mtime)
                processed_data = pd.read_pickle(latest_processed_file)
                
                print(f"✅ 发现 {len(processed_data_files)} 个已处理数据文件")
                print(f"✅ 使用最新文件: {latest_processed_file.name}")
                print(f"✅ 数据行数: {len(processed_data)}")
                
                # 查找最新的roleplay_results文件（优先使用pkl文件）
                results_dir = self.data_path / "llm_responses_roleplay_ml"
                pkl_files = list(results_dir.glob("roleplay_results_ml_*.pkl"))
                json_files = list(results_dir.glob("roleplay_results_ml_*.json"))
                
                latest_result_file = None
                # 优先选择最新的pkl，如果没有pkl再选json
                if pkl_files:
                    latest_result_file = max(pkl_files, key=lambda x: x.stat().st_mtime)
                    print(f"✅ 优先使用 PKL 文件进行增量检测")
                elif json_files:
                    latest_result_file = max(json_files, key=lambda x: x.stat().st_mtime)
                    print(f"⚠️ 使用 JSON 文件（建议使用 PKL）")
                
                if latest_result_file:
                    # 检查处理文件是否比访谈文件新
                    processed_time = latest_processed_file.stat().st_mtime
                    interview_time = latest_result_file.stat().st_mtime
                    
                    processed_dt = datetime.fromtimestamp(processed_time)
                    interview_dt = datetime.fromtimestamp(interview_time)
                    
                    print(f"📅 处理文件时间: {processed_dt}")
                    print(f"📅 访谈文件时间: {interview_dt}")
                    
                    if processed_time > interview_time and len(processed_data) >= 10:
                        print("💡 处理文件比访谈文件新，且数据充足")
                        need_reprocess = False
                    else:
                        if processed_time <= interview_time:
                            print("⚠️ 访谈文件更新，需要重新处理")
                        if len(processed_data) < 10:
                            print("⚠️ 处理文件数据不足，需要重新处理")
                        need_reprocess = True
                else:
                    print("⚠️ 未找到访谈文件，使用已有处理数据")
                    need_reprocess = False
            
            if need_reprocess:
                # 处理原始数据
                print("📊 处理原始多语言roleplay数据...")
                # 数据处理器会自动查找最新的roleplay_results_ml文件
                processed_data = processor.process_multilingual_data_to_ivs_format()
                print(f"✅ 处理后数据: {len(processed_data)} 行")
                
                # 保存处理后的数据（使用新的命名规则）
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                type_suffix = f"_{test_type}" if test_type else ""
                processed_file = self.data_path / f"llm_roleplay_ml_processed_responses_ivs_format{type_suffix}_{timestamp}.pkl"
                processed_data.to_pickle(processed_file)
                # 同时保存_latest副本
                latest_file = self.data_path / f"llm_roleplay_ml_processed_responses_ivs_format_latest.pkl"
                processed_data.to_pickle(latest_file)
                print(f"💾 处理后数据已保存: {processed_file.name}")
                print(f"💾 最新副本已保存: {latest_file.name}")
                if latest_result_file:
                    print(f"🔗 对应访谈文件: {latest_result_file.name}")
            
            # 显示数据概览
            print("\n📊 数据概览:")
            print(f"处理后数据形状: {processed_data.shape}")
            
            if 'model_name' in processed_data.columns:
                unique_models = sorted(processed_data['model_name'].unique())
                print(f"包含的模型数量: {len(unique_models)}")
                print(f"模型列表: {unique_models}")
            
            if 'country_code' in processed_data.columns:
                unique_countries = len(processed_data['country_code'].unique())
                print(f"模仿的国家数量: {unique_countries}")
            
            if 'language' in processed_data.columns:
                print(f"语言分布:")
                print(processed_data['language'].value_counts())
            
            if 'data_source' in processed_data.columns:
                print(f"数据源分布:")
                print(processed_data['data_source'].value_counts())
            
            return True
            
        except Exception as e:
            print(f"❌ 多语言Roleplay数据处理失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def step2_pca_analysis(self, test_type: str = None):
        """步骤2: 多语言Roleplay+IVS联合PCA分析"""
        print("\n" + "="*60)
        print("🔬 步骤2: 多语言Roleplay+IVS联合PCA分析")
        print("="*60)
        
        try:
            # 检查必要的数据文件
            # country_codes.pkl 统一放在 config/country/ 目录
            from pathlib import Path
            config_country_path = self.project_root / "config" / "country" / "country_codes.pkl"
            required_files = [
                self.country_values_data_path / "ivs_df.pkl",
                config_country_path  # 统一从 config/country/ 加载
            ]
            
            for file_path in required_files:
                if not file_path.exists():
                    print(f"❌ 缺少必要文件: {file_path}")
                    return False
            
            # 查找最新的处理后数据文件（根据测试类型，使用新的命名规则）
            if test_type:
                processed_files = list(self.data_path.glob(f"llm_roleplay_ml_processed_responses_ivs_format_{test_type}_*.pkl"))
                if not processed_files:
                    # 如果没有找到特定类型的，查找通用的但要确保数据匹配
                    processed_files = list(self.data_path.glob("llm_roleplay_ml_processed_responses_ivs_format_*.pkl"))
                    print(f"⚠️ 未找到{test_type}特定的处理文件，使用通用处理文件")
                if not processed_files:
                    # 兼容旧的命名规则
                    processed_files = list(self.data_path.glob("multilingual_roleplay_processed_responses_ivs_format_*.pkl"))
                    if processed_files:
                        print(f"⚠️ 发现旧格式文件，建议重新处理数据")
            else:
                processed_files = list(self.data_path.glob("llm_roleplay_ml_processed_responses_ivs_format_*.pkl"))
                if not processed_files:
                    # 兼容旧的命名规则
                    processed_files = list(self.data_path.glob("multilingual_roleplay_processed_responses_ivs_format_*.pkl"))
                    if processed_files:
                        print(f"⚠️ 发现旧格式文件，建议重新处理数据")
            if not processed_files:
                print(f"❌ 未找到处理后的数据文件")
                print(f"请先运行步骤1进行数据处理")
                return False
            
            latest_processed_file = max(processed_files, key=lambda x: x.stat().st_mtime)
            print(f"📁 使用最新处理文件: {latest_processed_file.name}")
            
            # 使用多语言PCA分析器（传递data根目录，内部会自动加载IVS数据）
            print("\n1️⃣ 初始化多语言PCA分析器...")
            analyzer = MultilingualRoleplayPCAAnalysis(
                data_path=str(self.project_root / "data")  # 传递总的data路径
            )
            
            # 运行完整分析（使用新的方法，会正确保存聚合后的实体分数）
            print("\n2️⃣ 运行多语言+IVS联合PCA分析...")
            entity_scores = analyzer.run_multilingual_analysis_for_runner()
            
            # entity_scores 已经是聚合后的实体级别数据
            # 包含：IVS国家（109个）+ Multilingual（669条）
            
            print(f"\n✅ 多语言+IVS联合PCA分析完成！")
            print(f"📊 生成了 {len(entity_scores)} 个实体的PCA分数")
            
            # 输出统计信息
            if 'PC1_rescaled' in entity_scores.columns:
                print(f"PC1范围: [{entity_scores['PC1_rescaled'].min():.2f}, {entity_scores['PC1_rescaled'].max():.2f}]")
            if 'PC2_rescaled' in entity_scores.columns:
                print(f"PC2范围: [{entity_scores['PC2_rescaled'].min():.2f}, {entity_scores['PC2_rescaled'].max():.2f}]")
            
            # 统计不同类型的实体
            if 'data_source' in entity_scores.columns:
                print(f"\n数据源分布:")
                print(entity_scores['data_source'].value_counts())
            
            if 'language' in entity_scores.columns:
                multilingual_data = entity_scores[entity_scores['data_source'] == 'Multilingual']
                if len(multilingual_data) > 0:
                    print(f"\n多语言数据语言分布:")
                    print(multilingual_data['language'].value_counts())
            
            if 'model_name' in entity_scores.columns:
                multilingual_data = entity_scores[entity_scores['data_source'] == 'Multilingual']
                if len(multilingual_data) > 0:
                    print(f"\n多语言模型分布:")
                    print(multilingual_data['model_name'].value_counts())
            
            # PCA分析模块已经完成了所有处理（包括country names和cultural regions）
            # 检查数据完整性
            print("\n3️⃣ 检查数据完整性...")
            if 'Country' in entity_scores.columns:
                valid_countries = entity_scores['Country'].notna().sum()
                total_countries = len(entity_scores[entity_scores['data_source'] == 'IVS'])
                print(f"✅ 国家名称: {valid_countries}/{total_countries} 个有效")
            
            if 'Cultural Region' in entity_scores.columns:
                valid_regions = entity_scores['Cultural Region'].notna().sum()
                print(f"✅ 文化区域: {valid_regions}/{len(entity_scores)} 个有效")
            
            # PCA结果已由分析模块保存，无需重复保存
            print(f"\n✅ PCA结果已保存到 data/roleplay_multilingual/ 目录")
            
            return True
            
        except Exception as e:
            print(f"❌ 多语言+IVS联合PCA分析失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def step3_language_comparison_analysis(self, test_type: str = None):
        """步骤3: 英文vs本国语言效果对比分析"""
        print("\n" + "="*60)
        print("🌐 步骤3: 英文vs本国语言效果对比分析")
        print("="*60)
        
        # 创建dashboard目录（与Stage2一致）
        dashboard_path = self.results_path / "roleplay_ml_dashboard"
        dashboard_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 可视化保存到: {dashboard_path}")
        
        try:
            # 查找最新的多语言PCA结果文件
            # 优先使用_latest.pkl（最可靠）
            latest_file = self.data_path / "roleplay_ml_pca_entity_scores_latest.pkl"
            if latest_file.exists():
                multilingual_path = latest_file
                print(f"📁 使用最新PCA文件: {multilingual_path.name}")
            else:
                # 回退：查找新格式的带时间戳文件（不使用test_type过滤）
                multilingual_files = list(self.data_path.glob("roleplay_ml_pca_entity_scores_*.pkl"))
                if not multilingual_files:
                    # 最后回退：兼容旧格式
                    multilingual_files = list(self.data_path.glob("multilingual_entity_scores_pca_fixed_*.pkl"))
                    if multilingual_files:
                        print("⚠️ 使用旧格式PCA文件，建议重新运行PCA分析")
                
                if not multilingual_files:
                    print(f"❌ 未找到多语言PCA结果文件")
                    print(f"请先运行步骤2进行PCA分析")
                    return False
                
                multilingual_path = max(multilingual_files, key=lambda x: x.stat().st_mtime)
                print(f"📁 使用最新PCA文件: {multilingual_path.name}")
            
            # 显示文件时间，帮助验证是否是最新的
            file_time = datetime.fromtimestamp(multilingual_path.stat().st_mtime)
            print(f"   文件时间: {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            print("\n1️⃣ 加载多语言数据...")
            multilingual_scores = pd.read_pickle(multilingual_path)
            
            print(f"✅ 多语言数据: {len(multilingual_scores)} 个实体")
            
            # 分离真实国家数据作为基准
            print("\n2️⃣ 准备基准数据...")
            real_countries = multilingual_scores[multilingual_scores['data_source'] == 'IVS'].copy()
            multilingual_roleplay = multilingual_scores[multilingual_scores['data_source'] == 'Multilingual'].copy()
            
            # 从多语言数据中分离三种类型
            multilingual_en_native = multilingual_roleplay[multilingual_roleplay['language'] == 'en-native'].copy()  # 英语母语国家
            multilingual_english = multilingual_roleplay[multilingual_roleplay['language'] == 'en'].copy()  # 非英语国家用英语
            # 本国语言（排除en和en-native）
            multilingual_native = multilingual_roleplay[
                (multilingual_roleplay['language'] != 'en') & 
                (multilingual_roleplay['language'] != 'en-native')
            ].copy()
            
            print(f"   真实国家: {len(real_countries)} 个")
            print(f"   多语言roleplay总计: {len(multilingual_roleplay)} 个")
            print(f"     - 英语母语国家(en-native): {len(multilingual_en_native)} 个")
            print(f"     - 非英语国家用英文(en): {len(multilingual_english)} 个")
            print(f"     - 本国语言部分: {len(multilingual_native)} 个")
            
            # 执行距离对比分析（包含三种语言类型）
            print("\n3️⃣ 执行距离对比分析（en-native vs en vs native）...")
            comparison_results = self.language_analyzer.calculate_language_distance_comparison(
                real_countries, multilingual_native, multilingual_english, multilingual_en_native
            )
            
            # 保存对比结果到dashboard（带时间戳）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            comparison_path = dashboard_path / f"language_comparison_analysis_{timestamp}.json"
            with open(comparison_path, 'w', encoding='utf-8') as f:
                json.dump(comparison_results, f, indent=2, ensure_ascii=False)
            print(f"💾 语言对比分析结果已保存到: {comparison_path.name}")
            
            # 保存最新文件路径供后续使用
            self._latest_comparison_file = str(comparison_path)
            
            # 生成对比可视化
            print("\n4️⃣ 生成对比可视化...")
            self._generate_language_comparison_visualization(comparison_results)
            
            return True
            
        except Exception as e:
            print(f"❌ 语言对比分析失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _generate_language_comparison_visualization(self, comparison_results):
        """生成语言对比可视化"""
        print("🎨 生成语言对比可视化...")
        
        # 使用类实例的可视化器
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dashboard_path = self.results_path / "roleplay_ml_dashboard"
        dashboard_path.mkdir(parents=True, exist_ok=True)
        
        # 1. 生成距离对比柱状图（使用visualization模块）
        save_path = dashboard_path / f"language_distance_comparison_{timestamp}.png"
        self.visualizer.plot_language_distance_comparison(comparison_results, str(save_path))
        
        # 2. 生成国家级别的详细对比（使用visualization模块）
        save_path = dashboard_path / f"country_level_language_comparison_{timestamp}.png"
        self.visualizer.plot_country_level_language_comparison(comparison_results, str(save_path))
        
        # 3. 生成交互式对比图（使用visualization模块）
        save_path = dashboard_path / f"interactive_language_comparison_{timestamp}.html"
        self.visualizer.plot_interactive_language_comparison(comparison_results, str(save_path))
        
        # 4. 生成每个模型的语言效果对比图（使用visualization模块）
        save_path = dashboard_path / f"model_specific_language_comparison_{timestamp}.png"
        self.visualizer.plot_model_language_comparison(comparison_results, str(save_path))
        
        # 5. 生成交互式模型对比图（使用visualization模块）
        model_analysis = comparison_results.get('model_specific_analysis', {})
        if model_analysis:
            save_path = dashboard_path / f"interactive_model_language_comparison_{timestamp}.html"
            self.visualizer.plot_interactive_model_comparison(model_analysis, str(save_path))
    
    def step4_visualization(self, test_type: str = None):
        """步骤4: 综合可视化"""
        print("\n" + "="*60)
        print("🎨 步骤4: 综合可视化")
        print("="*60)
        
        # 创建dashboard目录（与Stage2一致）
        dashboard_path = self.results_path / "roleplay_ml_dashboard"
        dashboard_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 可视化保存到: {dashboard_path}")
        
        try:
            # 查找最新的PCA结果文件
            # 优先使用_latest.pkl（最可靠）
            latest_file = self.data_path / "roleplay_ml_pca_entity_scores_latest.pkl"
            if latest_file.exists():
                entity_scores_path = latest_file
                print(f"📁 使用最新PCA文件: {entity_scores_path.name}")
            else:
                # 回退：查找新格式的带时间戳文件（不使用test_type过滤）
                pca_files = list(self.data_path.glob("roleplay_ml_pca_entity_scores_*.pkl"))
                if not pca_files:
                    # 最后回退：兼容旧格式
                    pca_files = list(self.data_path.glob("multilingual_entity_scores_pca_fixed_*.pkl"))
                    if pca_files:
                        print("⚠️ 发现旧格式PCA文件，建议重新运行PCA分析")
                
                if not pca_files:
                    print(f"❌ 未找到PCA结果文件")
                    print(f"请先运行步骤2进行PCA分析")
                    return False
                
                entity_scores_path = max(pca_files, key=lambda x: x.stat().st_mtime)
                print(f"📁 使用最新PCA文件: {entity_scores_path.name}")
            
            # 显示文件时间，帮助验证是否是最新的
            file_time = datetime.fromtimestamp(entity_scores_path.stat().st_mtime)
            print(f"   文件时间: {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 加载修复后的实体分数数据
            print("\n1️⃣ 加载修复后的实体分数数据...")
            entity_scores = pd.read_pickle(entity_scores_path)
            print(f"✅ 成功加载实体分数数据: {len(entity_scores)} 个实体")
            
            # 验证数据质量
            ivs_data = entity_scores[entity_scores['data_source'] == 'IVS']
            multilingual_data = entity_scores[entity_scores['data_source'] == 'Multilingual']
            print(f"   - IVS国家: {len(ivs_data)} 个")
            print(f"   - 多语言实体: {len(multilingual_data)} 个")
            if len(ivs_data) > 0 and 'Country' in ivs_data.columns:
                print(f"   - 有效国家名称: {ivs_data['Country'].notna().sum()}/{len(ivs_data)}")
            
            # 生成修正后的高质量静态文化地图
            print("\n2️⃣ 生成修正后的静态文化地图...")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            type_suffix = f"_{test_type}" if test_type else ""
            
            # 使用类实例的可视化器生成地图
            static_map_path = dashboard_path / f"multilingual_cultural_map_{timestamp}.png"
            self.visualizer.generate_cultural_map_static(entity_scores, str(static_map_path))
            print(f"✅ 修正后的静态文化地图已保存到: {static_map_path.name}")
            
            # 生成修正后的交互式HTML地图（使用visualization模块）
            print("\n3️⃣ 生成修正后的交互式HTML地图...")
            interactive_map_path = dashboard_path / f"multilingual_cultural_map_interactive_fixed{type_suffix}_{timestamp}.html"
            self.visualizer.generate_cultural_map_interactive(entity_scores, str(interactive_map_path))
            
            # 分析多语言准确性
            print("\n4️⃣ 生成多语言统计...")
            accuracy_analysis = {
                'timestamp': timestamp,
                'total_entities': len(entity_scores),
                'multilingual_entities': len(multilingual_data),
                'ivs_entities': len(ivs_data),
                'pc1_range': [float(entity_scores['PC1_rescaled'].min()), float(entity_scores['PC1_rescaled'].max())],
                'pc2_range': [float(entity_scores['PC2_rescaled'].min()), float(entity_scores['PC2_rescaled'].max())]
            }
            
            # 保存准确性分析结果
            accuracy_analysis_path = dashboard_path / f"multilingual_accuracy_analysis_{timestamp}.json"
            with open(accuracy_analysis_path, 'w', encoding='utf-8') as f:
                json.dump(accuracy_analysis, f, indent=2, ensure_ascii=False)
            print(f"✅ 多语言准确性分析已保存到: {accuracy_analysis_path.name}")
            
            # 生成汇总统计
            print("\n6️⃣ 生成汇总统计...")
            summary_stats = {
                'total_entities': len(entity_scores),
                'ivs_countries': len(ivs_data),
                'multilingual_entries': len(multilingual_data),
                'pc1_range': [entity_scores['PC1_rescaled'].min(), entity_scores['PC2_rescaled'].max()],
                'pc2_range': [entity_scores['PC2_rescaled'].min(), entity_scores['PC2_rescaled'].max()]
            }
            
            # 保存汇总统计到文件
            summary_path = dashboard_path / f"summary_statistics_{timestamp}.txt"
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write("Roleplay Multilingual Analysis Summary\n")
                f.write("="*50 + "\n\n")
                f.write(f"Total entities: {summary_stats['total_entities']}\n\n")
                
                if 'data_source' in entity_scores.columns:
                    f.write("Entities by Data Source:\n")
                    source_counts = entity_scores['data_source'].value_counts()
                    for source, count in source_counts.items():
                        f.write(f"  {source}: {count}\n")
                    f.write("\n")
                
                if 'language' in entity_scores.columns:
                    multilingual_data = entity_scores[entity_scores['data_source'] == 'Multilingual']
                    if len(multilingual_data) > 0:
                        f.write("Language Distribution:\n")
                        lang_counts = multilingual_data['language'].value_counts()
                        for lang, count in lang_counts.items():
                            f.write(f"  {lang}: {count}\n")
                        f.write("\n")
                
                if 'model_name' in entity_scores.columns:
                    multilingual_data = entity_scores[entity_scores['data_source'] == 'Multilingual']
                    if len(multilingual_data) > 0:
                        f.write("Multilingual Models:\n")
                        model_counts = multilingual_data['model_name'].value_counts()
                        for model, count in model_counts.items():
                            f.write(f"  {model}: {count}\n")
                        f.write("\n")
                
                f.write("Principal Component Statistics:\n")
                f.write(f"PC1 range: [{summary_stats['pc1_range'][0]:.2f}, {summary_stats['pc1_range'][1]:.2f}]\n")
                f.write(f"PC2 range: [{summary_stats['pc2_range'][0]:.2f}, {summary_stats['pc2_range'][1]:.2f}]\n\n")
                
                f.write("Accuracy Analysis:\n")
                f.write(str(accuracy_analysis))
            
            print(f"✅ 汇总统计已保存到: {summary_path.name}")
            
            # 保存文化坐标数据到dashboard目录
            cultural_coordinates_path = dashboard_path / f"multilingual_cultural_coordinates_{timestamp}.json"
            entity_scores.to_json(cultural_coordinates_path, orient='records', indent=2)
            print(f"✅ 文化坐标数据已保存到: {cultural_coordinates_path.name}")
            
            return True
            
        except Exception as e:
            print(f"❌ 可视化失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_complete_analysis(self, skip_interview=False):
        """运行完整分析流程"""
        print("🚀 开始Roleplay Multilingual完整分析流程...")
        print(f"⏰ 开始时间: {datetime.now()}")
        
        success_steps = []
        
        # 步骤0: 多语言角色扮演访谈（可选）
        if not skip_interview:
            print("\n💡 提示: 如果已有访谈数据，可以跳过访谈步骤")
            if self.step0_multilingual_interview():
                success_steps.append("多语言角色扮演访谈")
            else:
                print("❌ 多语言访谈失败，但可能已有数据，继续后续步骤")
        else:
            print("⏭️ 跳过访谈步骤，使用现有数据")
        
        # 步骤1: 多语言数据处理
        if self.step1_data_processing():
            success_steps.append("多语言数据处理")
        
        # 步骤2: PCA分析
        if self.step2_pca_analysis():
            success_steps.append("PCA分析")
        
        # 步骤3: 英文vs本国语言对比分析
        if self.step3_language_comparison():
            success_steps.append("英文vs本国语言对比分析")
        
        # 步骤4: 综合可视化
        if self.step4_visualization():
            success_steps.append("综合可视化")
        
        # 打印完成总结
        print("\n" + "="*60)
        print("🎉 Roleplay Multilingual分析完成!")
        print("="*60)
        print(f"✅ 成功完成的步骤: {', '.join(success_steps)}")
        print(f"📁 数据文件位置: {self.data_path}")
        print(f"📁 结果文件位置: {self.results_path}")
        print(f"⏰ 完成时间: {datetime.now()}")
        
        # 显示生成的文件
        print("\n📋 生成的文件:")
        
        # 访谈数据文件
        interview_files = list(self.data_path.glob("interview_data_*.json"))
        if interview_files:
            print("\n🎤 访谈数据文件 (data/roleplay_multilingual/):")
            for file_path in sorted(interview_files, key=lambda x: x.stat().st_mtime, reverse=True)[:3]:
                print(f"  ✅ {file_path.name}")
        
        # 数据文件
        data_files = [
            "multilingual_roleplay_processed_responses_ivs_format.pkl",
            "multilingual_entity_scores_pca_fixed.pkl", 
            "multilingual_entity_scores_pca_fixed.json"
        ]
        print("\n📊 处理后数据文件 (data/roleplay_multilingual/):")
        for file_name in data_files:
            file_path = self.data_path / file_name
            if file_path.exists():
                print(f"  ✅ {file_name}")
            else:
                print(f"  ❌ {file_name}")
        
        # 结果文件
        result_files = [
            "multilingual_cultural_map_corrected.png", 
            "multilingual_cultural_map_interactive_fixed.html",
            "language_distance_comparison.png",
            "country_level_language_comparison.png",
            "interactive_language_comparison.html",
            "language_comparison_analysis.json",
            "language_model_comparison.png",
            "multilingual_accuracy_analysis.json", 
            "summary_statistics.txt", 
            "multilingual_cultural_coordinates.json"
        ]
        print("\n🎨 结果文件 (results/roleplay_multilingual/):")
        for file_name in result_files:
            file_path = self.results_path / file_name
            if file_path.exists():
                print(f"  ✅ {file_name}")
            else:
                print(f"  ❌ {file_name}")
        
        return len(success_steps) >= 3
    
    def run_interview_only(self):
        """仅运行访谈步骤"""
        print("🎤 仅运行多语言角色扮演访谈...")
        print(f"⏰ 开始时间: {datetime.now()}")
        
        success = self.step0_multilingual_interview()
        
        print("\n" + "="*60)
        if success:
            print("✅ 多语言访谈成功完成!")
        else:
            print("❌ 多语言访谈失败!")
        print("="*60)
        print(f"⏰ 完成时间: {datetime.now()}")
        
        return success
    
    def _run_small_scale_test_with_full_pipeline(self):
        """运行小规模测试并完成整个分析流程"""
        try:
            # 动态读取配置文件
            config_path = self.project_root / "config" / "questions" / "multilingual" / "small_scale_test_config.json"
            
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                test_config = config_data.get('small_scale_test', {})
                
                models = test_config.get('models', [])
                countries_config = test_config.get('countries', [])
                consensus_count = test_config.get('consensus_count', 3)
                
                # 计算语言-国家组合数
                language_country_pairs = []
                for country_info in countries_config:
                    country = country_info.get('country', '')
                    languages = country_info.get('languages', [])
                    for lang in languages:
                        language_country_pairs.append(f"{country}({lang})")
                
                num_pairs = len(language_country_pairs)
                num_models = len(models)
                
                print(f"🧪 开始小规模测试 ({num_models}模型×{num_pairs}语言组合×{consensus_count}重复)")
                print(f"   配置: {', '.join(language_country_pairs)}")
            else:
                # 使用默认配置
                num_pairs = 9
                num_models = 3
                consensus_count = 3
                print(f"⚠️ 配置文件不存在: {config_path}")
                print("🧪 开始小规模测试 (3模型×5国家×各语言组合×3重复，使用默认配置)")
                print("   国家：Egypt(阿语+英), China(中文+英), Mexico(西语+英), Russia(俄语+英), USA(英)")
            
            # 动态计算统计
            total_tasks = num_pairs * num_models
            total_calls = total_tasks * 10 * consensus_count
            estimated_cost = total_calls * 0.0006
            estimated_hours_min = (total_tasks / 8) * (10 / 60)
            estimated_hours_max = (total_tasks / 8) * (20 / 60)
            
            print(f"\n📊 预估统计:")
            print(f"   - 语言-国家组合: {num_pairs}个")
            print(f"   - 模型数量: {num_models}个")
            print(f"   - 总任务数: {total_tasks}个 ({num_pairs}组合 × {num_models}模型)")
            print(f"   - 共识轮数: {consensus_count}轮/任务")
            print(f"   - 总API调用: {total_calls:,}次 ({total_tasks}任务 × 10问题 × {consensus_count}轮)")
            print(f"   - 预估费用: ${estimated_cost:.2f} (混合模型平均价)")
            print(f"   - 预估时间: {estimated_hours_min:.1f}-{estimated_hours_max:.1f}小时 (并发8)")
            
            confirm = input("\n确认继续? (y/N): ").strip().lower()
            if confirm != 'y':
                print("❌ 用户取消")
                return False
            
            # 运行访谈
            if self._run_multilingual_interview_with_config("small_scale"):
                # 继续后续步骤
                return self._run_full_analysis_pipeline("small_scale")
            else:
                return False
                
        except Exception as e:
            print(f"❌ 小规模测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def step4_visualization(self, test_type: str = None):
        """步骤4: 综合可视化"""
        print("\n" + "="*60)
        print("🎨 步骤4: 综合可视化")
        print("="*60)
        
        # 创建dashboard目录（与Stage2一致）
        dashboard_path = self.results_path / "roleplay_ml_dashboard"
        dashboard_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 可视化保存到: {dashboard_path}")
        
        try:
            # 查找最新的PCA结果文件
            # 优先使用_latest.pkl（最可靠）
            latest_file = self.data_path / "roleplay_ml_pca_entity_scores_latest.pkl"
            if latest_file.exists():
                entity_scores_path = latest_file
                print(f"📁 使用最新PCA文件: {entity_scores_path.name}")
            else:
                # 回退：查找新格式的带时间戳文件（不使用test_type过滤）
                pca_files = list(self.data_path.glob("roleplay_ml_pca_entity_scores_*.pkl"))
                if not pca_files:
                    # 最后回退：兼容旧格式
                    pca_files = list(self.data_path.glob("multilingual_entity_scores_pca_fixed_*.pkl"))
                    if pca_files:
                        print("⚠️ 发现旧格式PCA文件，建议重新运行PCA分析")
                
                if not pca_files:
                    print(f"❌ 未找到PCA结果文件")
                    print(f"请先运行步骤2进行PCA分析")
                    return False
                
                entity_scores_path = max(pca_files, key=lambda x: x.stat().st_mtime)
                print(f"📁 使用最新PCA文件: {entity_scores_path.name}")
            
            # 显示文件时间，帮助验证是否是最新的
            file_time = datetime.fromtimestamp(entity_scores_path.stat().st_mtime)
            print(f"   文件时间: {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 加载修复后的实体分数数据
            print("\n1️⃣ 加载修复后的实体分数数据...")
            entity_scores = pd.read_pickle(entity_scores_path)
            print(f"✅ 成功加载实体分数数据: {len(entity_scores)} 个实体")
            
            # 验证数据质量
            ivs_data = entity_scores[entity_scores['data_source'] == 'IVS']
            multilingual_data = entity_scores[entity_scores['data_source'] == 'Multilingual']
            print(f"   - IVS国家: {len(ivs_data)} 个")
            print(f"   - 多语言实体: {len(multilingual_data)} 个")
            if len(ivs_data) > 0 and 'Country' in ivs_data.columns:
                print(f"   - 有效国家名称: {ivs_data['Country'].notna().sum()}/{len(ivs_data)}")
            
            # 生成修正后的高质量静态文化地图
            print("\n2️⃣ 生成修正后的静态文化地图...")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            type_suffix = f"_{test_type}" if test_type else ""
            # 使用类实例的可视化器生成地图
            static_map_path = dashboard_path / f"multilingual_cultural_map_{timestamp}.png"
            self.visualizer.generate_cultural_map_static(entity_scores, str(static_map_path))
            print(f"✅ 修正后的静态文化地图已保存到: {static_map_path.name}")
            
            # 生成修正后的交互式HTML地图（使用visualization模块）
            print("\n3️⃣ 生成修正后的交互式HTML地图...")
            interactive_map_path = dashboard_path / f"multilingual_cultural_map_interactive_fixed{type_suffix}_{timestamp}.html"
            self.visualizer.generate_cultural_map_interactive(entity_scores, str(interactive_map_path))
            
            # 分析多语言准确性
            print("\n4️⃣ 生成多语言统计...")
            accuracy_analysis = {
                'timestamp': timestamp,
                'total_entities': len(entity_scores),
                'multilingual_entities': len(multilingual_data),
                'ivs_entities': len(ivs_data),
                'pc1_range': [float(entity_scores['PC1_rescaled'].min()), float(entity_scores['PC1_rescaled'].max())],
                'pc2_range': [float(entity_scores['PC2_rescaled'].min()), float(entity_scores['PC2_rescaled'].max())]
            }
            
            # 保存准确性分析结果
            accuracy_analysis_path = dashboard_path / f"multilingual_accuracy_analysis_{timestamp}.json"
            with open(accuracy_analysis_path, 'w', encoding='utf-8') as f:
                json.dump(accuracy_analysis, f, indent=2, ensure_ascii=False)
            print(f"✅ 多语言准确性分析已保存到: {accuracy_analysis_path.name}")
            
            # 生成汇总统计
            print("\n6️⃣ 生成汇总统计...")
            summary_stats = {
                'total_entities': len(entity_scores),
                'ivs_countries': len(ivs_data),
                'multilingual_entries': len(multilingual_data),
                'pc1_range': [entity_scores['PC1_rescaled'].min(), entity_scores['PC2_rescaled'].max()],
                'pc2_range': [entity_scores['PC2_rescaled'].min(), entity_scores['PC2_rescaled'].max()]
            }
            
            # 保存汇总统计到文件
            summary_path = dashboard_path / f"summary_statistics_{timestamp}.txt"
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write("Roleplay Multilingual Analysis Summary\n")
                f.write("="*50 + "\n\n")
                f.write(f"Total entities: {summary_stats['total_entities']}\n\n")
                
                if 'data_source' in entity_scores.columns:
                    f.write("Entities by Data Source:\n")
                    source_counts = entity_scores['data_source'].value_counts()
                    for source, count in source_counts.items():
                        f.write(f"  {source}: {count}\n")
                    f.write("\n")
                
                if 'language' in entity_scores.columns:
                    multilingual_data = entity_scores[entity_scores['data_source'] == 'Multilingual']
                    if len(multilingual_data) > 0:
                        f.write("Language Distribution:\n")
                        lang_counts = multilingual_data['language'].value_counts()
                        for lang, count in lang_counts.items():
                            f.write(f"  {lang}: {count}\n")
                        f.write("\n")
                
                if 'model_name' in entity_scores.columns:
                    multilingual_data = entity_scores[entity_scores['data_source'] == 'Multilingual']
                    if len(multilingual_data) > 0:
                        f.write("Multilingual Models:\n")
                        model_counts = multilingual_data['model_name'].value_counts()
                        for model, count in model_counts.items():
                            f.write(f"  {model}: {count}\n")
                        f.write("\n")
                
                f.write("Principal Component Statistics:\n")
                f.write(f"PC1 range: [{summary_stats['pc1_range'][0]:.2f}, {summary_stats['pc1_range'][1]:.2f}]\n")
                f.write(f"PC2 range: [{summary_stats['pc2_range'][0]:.2f}, {summary_stats['pc2_range'][1]:.2f}]\n\n")
                
                f.write("Accuracy Analysis:\n")
                f.write(str(accuracy_analysis))
            
            print(f"✅ 汇总统计已保存到: {summary_path.name}")
            
            # 保存文化坐标数据到dashboard目录
            cultural_coordinates_path = dashboard_path / f"multilingual_cultural_coordinates_{timestamp}.json"
            entity_scores.to_json(cultural_coordinates_path, orient='records', indent=2)
            print(f"✅ 文化坐标数据已保存到: {cultural_coordinates_path.name}")
            
            return True
            
        except Exception as e:
            print(f"❌ 可视化失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_complete_analysis(self, skip_interview=False):
        """运行完整分析流程"""
        print("🚀 开始Roleplay Multilingual完整分析流程...")
        print(f"⏰ 开始时间: {datetime.now()}")
        
        success_steps = []
        
        # 步骤0: 多语言角色扮演访谈（可选）
        if not skip_interview:
            print("\n💡 提示: 如果已有访谈数据，可以跳过访谈步骤")
            if self.step0_multilingual_interview():
                success_steps.append("多语言角色扮演访谈")
            else:
                print("❌ 多语言访谈失败，但可能已有数据，继续后续步骤")
        else:
            print("⏭️ 跳过访谈步骤，使用现有数据")
        
        # 步骤1: 多语言数据处理
        if self.step1_data_processing():
            success_steps.append("多语言数据处理")
        else:
            print("❌ 多语言数据处理失败，停止分析")
            return False
        
        # 步骤2: 多语言+IVS联合PCA分析
        if self.step2_pca_analysis():
            success_steps.append("多语言+IVS联合PCA分析")
        else:
            print("❌ 多语言+IVS联合PCA分析失败，停止分析")
            return False
        
        # 步骤3: 英文vs本国语言效果对比分析
        if self.step3_language_comparison_analysis():
            success_steps.append("语言效果对比分析")
        else:
            print("❌ 语言效果对比分析失败，但继续其他步骤")
        
        # 步骤4: 综合可视化
        if self.step4_visualization():
            success_steps.append("综合可视化")
        else:
            print("❌ 综合可视化失败，但前面步骤成功")
        
        # 总结
        print("\n" + "="*60)
        print("🎉 Roleplay Multilingual分析完成!")
        print("="*60)
        print(f"✅ 成功完成的步骤: {', '.join(success_steps)}")
        print(f"📁 数据文件位置: {self.data_path}")
        print(f"📁 结果文件位置: {self.results_path}")
        print(f"⏰ 完成时间: {datetime.now()}")
        
        # 显示生成的文件
        print("\n📋 生成的文件:")
        
        # 访谈数据文件
        interview_files = list(self.data_path.glob("interview_data_*.json"))
        if interview_files:
            print("\n🎤 访谈数据文件 (data/roleplay_multilingual/):")
            for file_path in sorted(interview_files, key=lambda x: x.stat().st_mtime, reverse=True)[:3]:
                print(f"  ✅ {file_path.name}")
        
        # 数据文件
        data_files = [
            "multilingual_roleplay_processed_responses_ivs_format.pkl",
            "multilingual_entity_scores_pca_fixed.pkl", 
            "multilingual_entity_scores_pca_fixed.json"
        ]
        print("\n📊 处理后数据文件 (data/roleplay_multilingual/):")
        for file_name in data_files:
            file_path = self.data_path / file_name
            if file_path.exists():
                print(f"  ✅ {file_name}")
            else:
                print(f"  ❌ {file_name}")
        
        # 结果文件
        result_files = [
            "multilingual_cultural_map_corrected.png", 
            "multilingual_cultural_map_interactive_fixed.html",
            "language_distance_comparison.png",
            "country_level_language_comparison.png",
            "interactive_language_comparison.html",
            "language_comparison_analysis.json",
            "language_model_comparison.png",
            "multilingual_accuracy_analysis.json", 
            "summary_statistics.txt", 
            "multilingual_cultural_coordinates.json"
        ]
        print("\n🎨 结果文件 (results/roleplay_multilingual/):")
        for file_name in result_files:
            file_path = self.results_path / file_name
            if file_path.exists():
                print(f"  ✅ {file_name}")
            else:
                print(f"  ❌ {file_name}")
        
        return len(success_steps) >= 3
    
    def run_interview_only(self):
        """仅运行访谈步骤"""
        print("🎤 仅运行多语言角色扮演访谈...")
        print(f"⏰ 开始时间: {datetime.now()}")
        
        success = self.step0_multilingual_interview()
        
        print("\n" + "="*60)
        if success:
            print("🎉 多语言访谈完成!")
        else:
            print("❌ 多语言访谈失败!")
        print("="*60)
        print(f"⏰ 完成时间: {datetime.now()}")
        
        return success
    
    def _run_comprehensive_test_with_full_pipeline(self):
        """使用配置文件运行测试并完成整个分析流程"""
        try:
            from src.roleplay_multilingual.multilingual_roleplay_interview import MultilingualRoleplayInterview
            
            # 询问使用哪个语言配置文件
            print("\n选择语言配置文件:")
            print("  1. multilingual_questions_complete.json (完整配置，所有语言所有国家)")
            print("  2. multilingual_questions_test.json (测试配置，每个语言1个国家)")
            
            lang_config_choice = input("\n请选择 (1-2，默认1): ").strip() or "1"
            
            lang_config_files = {
                "1": "multilingual_questions_complete.json",
                "2": "multilingual_questions_test.json"
            }
            
            lang_config_file = lang_config_files.get(lang_config_choice, "multilingual_questions_complete.json")
            print(f"✅ 使用语言配置文件: {lang_config_file}")
            
            # 统一使用选择的配置文件
            config_path = self.project_root / "config" / "questions" / "multilingual" / lang_config_file
            if not config_path.exists():
                print(f"❌ 找不到配置文件: {config_path}")
                return False
            
            with open(config_path, 'r', encoding='utf-8') as f:
                try:
                    config_data = json.load(f)
                except json.JSONDecodeError as e:
                    print(f"❌ 配置文件解析失败: {e}")
                    return False
            
            languages_config = config_data.get("languages")
            if not languages_config:
                print("❌ 配置文件不包含 'languages' 字段")
                return False
            
            # 询问使用哪个模型配置文件
            print("\n选择模型配置文件:")
            print("  1. llm_models.json (所有22个模型)")
            print("  2. llm_models_fix_all.json (所有6个有问题的模型)")
            print("  3. llm_models_fix_gemini.json (只修复gemini-3-pro-preview)")
            print("  4. llm_models_healthy.json (15个100%成功率模型)")
            print("  5. llm_models_test_3_cheap.json (第1批: gpt-4o-mini/deepseek-chat/kimi-k2)")
            print("  6. llm_models_test_3_batch2.json (第2批: 6个便宜健康模型)")
            
            config_choice = input("\n请选择 (1-6，默认1): ").strip() or "1"
            
            model_config_files = {
                "1": "llm_models.json",
                "2": "llm_models_fix_all.json",
                "3": "llm_models_fix_gemini.json",
                "4": "llm_models_healthy.json",
                "5": "llm_models_test_3_cheap.json",
                "6": "llm_models_test_3_batch2.json"
            }
            
            model_config_file = model_config_files.get(config_choice, "llm_models.json")
            print(f"✅ 使用配置文件: {model_config_file}")
            
            # 计算统计信息
            interviewer = MultilingualRoleplayInterview(
                consensus_count=5, 
                data_path=str(self.data_path),
                model_config_file=model_config_file,
                language_config_file=lang_config_file
            )
            # 从interviewer的model_configs获取所有可用模型
            available_models = list(interviewer.model_configs.keys())
            if not available_models:
                print("⚠️ 未找到可用模型")
                return False
            
            # 统计语言-国家对
            language_country_pairs = 0
            unique_countries = set()
            for lang_code, lang_cfg in languages_config.items():
                country_entries = lang_cfg.get("countries", [])
                for entry in country_entries:
                    country_name = entry.get("name") if isinstance(entry, dict) else entry
                    if country_name:
                        language_country_pairs += 1
                        unique_countries.add(country_name)
            
            total_countries = len(unique_countries)
            total_models = len(available_models)
            repeat_count = 5  # 默认5轮共识
            
            print(f"🚀 开始全面测试")
            print(f"   - 语言配置: {lang_config_file}")
            print(f"   - 模型配置: {model_config_file}")
            print(f"   - 语言数量: {len(languages_config)}种")
            print(f"   - 国家数量: {total_countries}个")
            print(f"   - 模型数量: {total_models}个")
            
            questions_per_interview = 10
            total_tasks = language_country_pairs * total_models
            total_calls = total_tasks * questions_per_interview * repeat_count
            estimated_cost = total_calls * 0.0006  # 平均每次$0.0006（混合模型价格）
            estimated_hours_min = (total_tasks / 8) * (10 / 60)  # 快速场景
            estimated_hours_max = (total_tasks / 8) * (20 / 60)  # 慢速场景
            
            print(f"\n📊 预估统计:")
            print(f"   - 语言-国家对: {language_country_pairs}个")
            print(f"   - 独特国家数量: {total_countries}个")
            print(f"   - 模型数量: {total_models}个")
            print(f"   - 共识轮数: {repeat_count}次/问题")
            print(f"   - 总任务数: {total_tasks}个 (语言-国家对×模型)")
            print(f"   - 总访谈次数: {total_tasks * repeat_count:,}次")
            print(f"   - 总API调用: {total_calls:,}次")
            print(f"   - 预估费用: ${estimated_cost:.2f} (混合模型平均价)")
            print(f"   - 预估时间: {estimated_hours_min:.1f}-{estimated_hours_max:.1f}小时 (并发8)")
            
            confirm = input("\n确认继续? (y/N): ").strip().lower()
            if confirm != 'y':
                print("❌ 用户取消")
                return False
            
            # 使用 run_multilingual_experiment 运行全面访谈
            print("\n" + "="*70)
            print("🚀 开始全面访谈...")
            print("="*70)
            
            results = interviewer.run_multilingual_experiment(
                models=available_models,
                max_workers=8,
                repeat_count=repeat_count,
                test_type="comprehensive",
                skip_existing=False  # 全面测试：不跳过已有数据
            )
            
            # 修复：检查正确的字段名
            if not results or results.get('total_tasks', 0) == 0:
                print("❌ 访谈失败或无结果")
                return False
            
            print(f"\n✅ 访谈完成！")
            print(f"   - 总任务数: {results.get('total_tasks', 0)}")
            print(f"   - 成功任务数: {results.get('successful_tasks', 0)}")
            
            # 继续后续分析步骤
            return self._run_full_analysis_pipeline("comprehensive")
                
        except Exception as e:
            print(f"❌ 全面测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _run_incremental_languages_with_full_pipeline(self):
        """仅针对配置中缺失的语言-国家组合执行增量访谈并运行完整分析"""
        try:
            from src.roleplay_multilingual.multilingual_roleplay_interview import MultilingualRoleplayInterview
            
            config_path = self.project_root / "config" / "questions" / "multilingual" / "multilingual_questions_complete.json"
            if not config_path.exists():
                print(f"❌ 找不到配置文件: {config_path}")
                return False
            
            with open(config_path, 'r', encoding='utf-8') as f:
                try:
                    config_data = json.load(f)
                except json.JSONDecodeError as e:
                    print(f"❌ 配置文件解析失败: {e}")
                    return False
            
            languages_config = config_data.get("languages")
            if not languages_config:
                print("❌ 配置文件不包含 'languages' 字段，无法执行增量访谈")
                return False
            
            interviewer = MultilingualRoleplayInterview(consensus_count=5, data_path=str(self.data_path))
            # 从interviewer的model_configs获取所有可用模型
            available_models = list(interviewer.model_configs.keys())
            if not available_models:
                print("⚠️ 未找到可用模型")
                return False
            
            completed_task_keys = set()
            latest_results_file = self._get_latest_roleplay_results_file()
            if latest_results_file:
                print(f"📁 使用最新访谈文件确定已完成组合: {latest_results_file.name}")
                completed_task_keys = self._extract_completed_pairs_from_file(latest_results_file)
                print(f"   - 已完成组合: {len(completed_task_keys)} 个 (模型-国家-语言)")
            else:
                print("⚠️ 未找到历史访谈结果文件，视为全部组合缺失")
            
            def extract_country_name(entry):
                if isinstance(entry, dict):
                    return entry.get("name")
                return entry
            
            # 计算每个模型缺失的国家/语言组合
            missing_by_model = {}
            for model in available_models:
                for lang_code, lang_cfg in languages_config.items():
                    country_entries = lang_cfg.get("countries", [])
                    for entry in country_entries:
                        country_name = extract_country_name(entry)
                        if not country_name:
                            continue
                        if (model, country_name, lang_code) not in completed_task_keys:
                            missing_by_model.setdefault(model, {}).setdefault(lang_code, []).append(country_name)
            
            # 清理空模型
            missing_by_model = {
                model: {lang: countries for lang, countries in lang_map.items() if countries}
                for model, lang_map in missing_by_model.items()
                if any(lang_map.values())
            }
            
            if not missing_by_model:
                print("✅ 所有模型的国家/语言组合都已存在访谈数据。")
                run_analysis = input("是否直接运行分析流程 (y/N): ").strip().lower()
                if run_analysis == 'y':
                    return self._run_full_analysis_pipeline()
                return True
            
            total_missing = sum(len(countries) for lang_map in missing_by_model.values() for countries in lang_map.values())
            unique_countries = sorted({
                country
                for lang_map in missing_by_model.values()
                for countries in lang_map.values()
                for country in countries
            })
            missing_models = list(missing_by_model.keys())
            
            print("\n" + "="*60)
            print("🆕 增量访谈计划（仅补齐缺失的模型/国家/语言）")
            print("="*60)
            print(f"   • 缺失模型数量: {len(missing_models)} 个")
            print(f"   • 缺失国家/语言组合: {total_missing} 个 ({', '.join(unique_countries)})")
            print("="*60)
            for model, lang_map in missing_by_model.items():
                print(f"   ▶ 模型 {model}:")
                for lang_code, countries in lang_map.items():
                    print(f"      - {lang_code}: {', '.join(countries)}")
            print("="*60)
            
            confirm = input("确认执行增量访谈并运行完整分析流程？(y/N): ").strip().lower()
            if confirm != 'y':
                print("❌ 已取消")
                return False
            
            original_config = interviewer.multilingual_config
            
            for model_name, lang_map in missing_by_model.items():
                filtered_languages = {}
                for lang_code, country_names in lang_map.items():
                    lang_cfg = original_config.get("languages", {}).get(lang_code)
                    if not lang_cfg:
                        continue
                    new_lang_cfg = copy.deepcopy(lang_cfg)
                    filtered_countries = []
                    for entry in lang_cfg.get("countries", []):
                        country_name = extract_country_name(entry)
                        if country_name in country_names:
                            filtered_countries.append(copy.deepcopy(entry))
                    if filtered_countries:
                        new_lang_cfg["countries"] = filtered_countries
                        filtered_languages[lang_code] = new_lang_cfg
                
                if not filtered_languages:
                    continue
                
                print("\n" + "-"*60)
                print(f"🚀 开始增量访谈: 模型 {model_name}")
                for lang_code, lang_cfg in filtered_languages.items():
                    countries = [extract_country_name(entry) for entry in lang_cfg.get("countries", [])]
                    print(f"   - {lang_code}: {', '.join(countries)}")
                
                try:
                    temp_config = copy.deepcopy(original_config)
                    temp_config["languages"] = filtered_languages
                    interviewer.multilingual_config = temp_config
                    
                    results = interviewer.run_multilingual_experiment(
                        models=[model_name],
                        max_workers=8,
                        skip_existing=True
                    )
                    
                    # 修复：检查正确的字段
                    if not results or results.get('total_tasks', 0) == 0:
                        print(f"   ❌ 模型 {model_name} 访谈失败或无结果")
                    else:
                        print(f"   ✅ 模型 {model_name} 访谈完成")
                        print(f"      - 总任务数: {results.get('total_tasks', 0)}")
                        print(f"      - 成功任务数: {results.get('successful_tasks', 0)}")
                finally:
                    interviewer.multilingual_config = original_config
            
            print("\n✅ 所有缺失模型的增量访谈已完成，开始运行分析流程...")
            return self._run_full_analysis_pipeline()
        
        except Exception as e:
            print(f"❌ 增量访谈流程失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _get_latest_roleplay_results_file(self):
        """获取最新的 roleplay_results_ml 文件，优先使用 pkl 格式（占用空间小）"""
        responses_dir = self.project_root / "data" / "roleplay_multilingual" / "llm_responses_roleplay_ml"
        if not responses_dir.exists():
            return None
        # 优先查找 pkl 文件，没有 pkl 时才用 json
        pkl_files = list(responses_dir.glob("roleplay_results_ml_*.pkl"))
        if pkl_files:
            return max(pkl_files, key=lambda x: x.stat().st_mtime)
        
        json_files = list(responses_dir.glob("roleplay_results_ml_*.json"))
        if json_files:
            return max(json_files, key=lambda x: x.stat().st_mtime)
        
        return None

    def _extract_completed_pairs_from_file(self, file_path: Path):
        """从指定结果文件提取 (model, country, language) 组合"""
        completed_pairs = set()
        try:
            # 根据文件扩展名选择读取方式
            if file_path.suffix == '.pkl':
                import pickle
                with open(file_path, 'rb') as f:
                    data = pickle.load(f)
            else:  # .json
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
        except Exception as e:
            print(f"⚠️ 无法读取 {file_path.name}: {e}")
            return completed_pairs
        
        def normalize(value):
            if isinstance(value, dict):
                return value.get('name') or value.get('country') or value.get('code')
            return value

        def add_pair(model, country, language):
            model_name = normalize(model)
            country_name = normalize(country)
            language_code = normalize(language)
            if model_name and country_name and language_code:
                completed_pairs.add((model_name, country_name, language_code))
        
        if isinstance(data, dict) and 'results' in data:
            for item in data.get('results', []):
                add_pair(item.get('model'), item.get('country'), item.get('language'))
        elif isinstance(data, dict):
            # 兼容 interview_data_* 格式
            for country, lang_dict in data.items():
                if isinstance(lang_dict, dict):
                    for language, model_map in lang_dict.items():
                        if isinstance(model_map, dict):
                            for model in model_map.keys():
                                add_pair(model, country, language)
                        else:
                            add_pair(None, country, language)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    add_pair(item.get('model'), item.get('country'), item.get('language'))
        
        return completed_pairs
    
    def _run_data_processing_pipeline(self):
        """仅运行数据处理流程（跳过访谈）"""
        try:
            print("📊 开始数据处理流程...")
            return self._run_full_analysis_pipeline()
        except Exception as e:
            print(f"❌ 数据处理流程失败: {e}")
            return False
    
    def _run_multilingual_interview_with_config(self, config_type: str):
        """根据配置类型运行多语言访谈"""
        try:
            from src.roleplay_multilingual.multilingual_roleplay_interview import MultilingualRoleplayInterview
            import json
            
            # 从配置文件加载参数
            if config_type == "comprehensive":
                # 加载 comprehensive_multilingual_config.json
                config_path = self.project_root / "config" / "questions" / "multilingual" / "comprehensive_multilingual_config.json"
                if config_path.exists():
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                    
                    test_config = config_data.get('comprehensive_test_config', {})
                    repeat_count = test_config.get('repeat_count', 5)
                    models = test_config.get('models', [])
                    
                    # 从配置中提取国家
                    # 配置格式：languages -> {language_code: {countries: [{...}]}}
                    countries = []
                    languages = test_config.get('languages', {})
                    for lang_code, lang_config in languages.items():
                        country_list = lang_config.get('countries', [])
                        for country_info in country_list:
                            country_name = country_info.get('name')
                            if country_name and country_name not in countries:
                                countries.append(country_name)
                    
                    print(f"✅ 从配置文件加载参数:")
                    print(f"   - 独特国家: {len(countries)}个")
                    print(f"   - 模型: {len(models)}个")
                    print(f"   - 共识轮数: {repeat_count}轮")
                    
                else:
                    print(f"⚠️ 配置文件不存在: {config_path}")
                    print(f"使用默认配置（完整测试）")
                    # 默认配置（完整测试）
                    repeat_count = 5
                    countries = ["China", "United States"]  # 实际应该有32个
                    models = ["openai/gpt-4o-mini", "openai/gpt-4o", "openai/gpt-4-turbo",
                             "anthropic/claude-3.5-sonnet", "anthropic/claude-3-opus",
                             "google/gemini-2.0-flash-exp", "google/gemini-2.0-flash-thinking-exp"]
                    repeat_count = 2
                    
            elif config_type == "small_scale":
                # 加载 config/small_scale_test_config.json
                config_path = self.project_root / "config" / "questions" / "multilingual" / "small_scale_test_config.json"
                if config_path.exists():
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                    
                    # 正确的键名是 "small_scale_test"
                    test_config = config_data.get('small_scale_test', {})
                    repeat_count = test_config.get('consensus_count', 5)
                    models = test_config.get('models', [])
                    
                    # 从配置中提取国家和语言组合
                    countries = []
                    language_country_pairs = []
                    country_configs = test_config.get('countries', [])
                    
                    for country_info in country_configs:
                        country_name = country_info.get('country')
                        languages = country_info.get('languages', [])
                        if country_name:
                            if country_name not in countries:
                                countries.append(country_name)
                            for lang in languages:
                                language_country_pairs.append(f"{country_name}({lang})")
                    
                    print(f"✅ 从配置文件加载参数:")
                    print(f"   - 独特国家: {len(countries)}个 ({', '.join(countries)})")
                    print(f"   - 语言-国家组合: {len(language_country_pairs)}个 ({', '.join(language_country_pairs)})")
                    print(f"   - 模型: {len(models)}个 ({', '.join(models)})")
                    print(f"   - 共识轮数: {repeat_count}轮")
                    
                else:
                    print(f"⚠️ 配置文件不存在: {config_path}")
                    print(f"使用默认配置（小规模测试）")
                    # 默认配置（小规模测试）
                    countries = ["China", "Egypt", "Mexico", "Russian Federation", "United States of America"]
                    models = ["openai/gpt-4o-mini", "deepseek/deepseek-chat-v3-0324", "google/gemini-2.0-flash-001"]
                    repeat_count = 3
                    language_country_pairs = []
            else:
                print(f"❌ 未知配置类型: {config_type}")
                return False
            
            print(f"🎯 访谈配置:")
            print(f"   - 国家: {len(countries)} 个 ({', '.join(countries)})")
            print(f"   - 模型: {len(models)} 个")
            print(f"   - 共识轮数: {repeat_count}")
            
            # 🔥 关键：对于small_scale，需要创建临时配置文件
            if config_type == "small_scale" and 'language_country_pairs' in locals() and len(language_country_pairs) > 0:
                # 将small_scale配置转换为访谈器期望的格式
                import json
                temp_config = {
                    "languages": {}
                }
                
                for pair in language_country_pairs:
                    # 解析 "China(zh-cn)" 格式
                    if '(' in pair and ')' in pair:
                        country = pair.split('(')[0]
                        lang = pair.split('(')[1].rstrip(')')
                        
                        if lang not in temp_config["languages"]:
                            temp_config["languages"][lang] = {"countries": []}
                        
                        # 添加国家信息
                        temp_config["languages"][lang]["countries"].append({
                            'name': country,
                            'code': country.lower().replace(' ', '_')
                        })
                
                # 保存临时配置文件到项目根目录
                temp_config_path = self.project_root / "config" / "questions" / "multilingual" / "small_scale_test_config.json"
                with open(temp_config_path, 'w', encoding='utf-8') as f:
                    json.dump({"small_scale_test_config": temp_config}, f, indent=2, ensure_ascii=False)
                print(f"✅ 已创建临时配置文件: {temp_config_path}")
            
            # 创建访谈器（传入consensus_count）
            interviewer = MultilingualRoleplayInterview(
                consensus_count=repeat_count,
                data_path=str(self.data_path)
            )
            
            print(f"🚀 使用配置文件运行访谈...")
            
            # 计算实际的语言-国家组合数
            # 优先使用从配置文件读取的值，否则从interviewer的multilingual_config读取
            num_language_country_pairs = 0
            if 'language_country_pairs' in locals() and isinstance(language_country_pairs, list):
                num_language_country_pairs = len(language_country_pairs)
            elif hasattr(interviewer, 'multilingual_config') and interviewer.multilingual_config:
                for lang_code, lang_data in interviewer.multilingual_config.items():
                    if isinstance(lang_data, list):
                        num_language_country_pairs += len(lang_data)
            
            # 动态计算任务统计
            if num_language_country_pairs > 0:
                total_tasks = num_language_country_pairs * len(models)
                total_calls = total_tasks * 10 * repeat_count
                estimated_cost = total_calls * 0.0006
                estimated_hours_min = (total_tasks / 8) * (10 / 60)
                estimated_hours_max = (total_tasks / 8) * (20 / 60)
                
                print(f"\n📊 动态任务统计:")
                print(f"   - 语言-国家组合: {num_language_country_pairs}个")
                print(f"   - 模型数量: {len(models)}个")
                print(f"   - 总任务数: {total_tasks}个 ({num_language_country_pairs}组合 × {len(models)}模型)")
                print(f"   - 共识轮数: {repeat_count}轮/任务")
                print(f"   - 总API调用: {total_calls:,}次 ({total_tasks}任务 × 10问题 × {repeat_count}轮)")
                print(f"   - 预估费用: ${estimated_cost:.2f}")
                print(f"   - 预估时间: {estimated_hours_min:.1f}-{estimated_hours_max:.1f}小时 (并发8)\n")
            
            # 运行多语言实验（会自动从配置文件读取国家和语言配置）
            results = interviewer.run_multilingual_experiment(
                models=models,
                max_workers=8,  # 高并发模式（加快速度）
                test_type=config_type
            )
            
            # 修复：检查正确的字段
            if results and results.get('total_tasks', 0) > 0:
                print("✅ 访谈完成")
                print(f"   - 总任务数: {results.get('total_tasks', 0)}")
                print(f"   - 成功任务数: {results.get('successful_tasks', 0)}")
                return True
            else:
                print("❌ 访谈失败或无结果")
                return False
                
        except Exception as e:
            print(f"❌ 访谈执行失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _run_full_analysis_pipeline(self, test_type: str = None):
        """运行完整的分析流程（数据处理→PCA→可视化）"""
        try:
            print("\n🔄 开始数据处理...")
            if not self.step1_data_processing(test_type):
                print("❌ 数据处理失败")
                return False
            
            print("\n🔄 开始PCA分析...")
            if not self.step2_pca_analysis(test_type):
                print("❌ PCA分析失败")
                return False
            
            print("\n🔄 开始语言对比分析...")
            if not self.step3_language_comparison_analysis(test_type):
                print("❌ 语言对比分析失败")
                return False
            
            print("\n🔄 开始文化地图可视化...")
            if not self.step4_visualization(test_type):
                print("❌ 文化地图可视化失败")
                return False
            
            print("\n✅ 完整分析流程成功完成！")
            return True
            
        except Exception as e:
            print(f"❌ 分析流程失败: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """主函数"""
    
    # 读取small_scale配置以显示准确信息
    from pathlib import Path
    project_root = Path(__file__).parent.parent.parent
    small_scale_config_path = project_root / "config" / "questions" / "multilingual" / "small_scale_test_config.json"
    
    small_scale_desc = "测试小规模访谈 (根据配置文件动态调整)"
    small_scale_details = []
    
    if small_scale_config_path.exists():
        try:
            with open(small_scale_config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            test_config = config_data.get('small_scale_test', {})
            
            models = test_config.get('models', [])
            countries_config = test_config.get('countries', [])
            consensus_count = test_config.get('consensus_count', 3)
            
            # 提取国家和语言信息
            country_lang_pairs = []
            for country_info in countries_config:
                country = country_info.get('country', '')
                languages = country_info.get('languages', [])
                if languages:
                    lang_str = '+'.join(languages)
                    country_lang_pairs.append(f"{country}({lang_str})")
            
            small_scale_desc = f"测试小规模访谈 ({len(models)}模型×{len(country_lang_pairs)}组合)"
            small_scale_details = [
                f"• 模型: {', '.join([m.split('/')[-1] if '/' in m else m for m in models])}",
                f"• 国家-语言组合: {', '.join(country_lang_pairs)}",
                f"• 共识轮数: {consensus_count}轮"
            ]
        except Exception as e:
            small_scale_details = [
                "• ⚠️ 配置文件读取失败，将使用默认配置",
                "• 模型：GPT-4o-mini, DeepSeek, Gemini",
                "• 国家：Egypt(阿拉伯语+英语), China(中文+英语), Mexico(西班牙语+英语), Russia(俄语+英语), USA(英语)"
            ]
    else:
        small_scale_details = [
            "• ⚠️ 配置文件不存在，将使用默认配置",
            "• 模型：GPT-4o-mini, DeepSeek, Gemini",
            "• 国家：Egypt(阿拉伯语+英语), China(中文+英语), Mexico(西班牙语+英语), Russia(俄语+英语), USA(英语)"
        ]
    
    print("\n" + "="*70)
    print("🌐 Stage3: Roleplay Multilingual 分析系统")
    print("="*70)
    print("\n请选择要执行的操作：")
    print("\n1️⃣  全面测试（读取 multilingual_questions_complete.json）")
    print("     • 使用配置文件中的所有语言和国家")
    print("     • 使用 llm_models.json 中的所有模型")
    print("     • 共识轮数: 3轮")
    print("     • 不跳过已有数据（完全重新访谈）")
    print(f"\n2️⃣  {small_scale_desc}")
    for detail in small_scale_details:
        print(f"     {detail}")
    print("\n3️⃣  只分析现有数据 (数据处理 → PCA → 可视化)")
    print("\n4️⃣  增量访谈：根据配置补齐缺失语言/国家")
    print("     • 自动检测 data/roleplay_multilingual/llm_responses_roleplay_ml/ 中已有组合")
    print("     • 只访谈 config/questions/multilingual/multilingual_questions_complete.json 中尚未出现的国家/语言")
    print("     • 完成后立即运行 数据处理 → PCA → 可视化")
    print("\n0️⃣  退出")
    print("\n" + "="*70)
    
    try:
        # 创建分析运行器
        runner = RoleplayMultilingualAnalysisRunner()
        
        while True:
            try:
                choice = input("\n请输入选项 (0-4): ").strip()
                
                if choice == '0':
                    print("👋 退出程序")
                    return 0
                elif choice in ['1', '2', '3', '4']:
                    break
                else:
                    print("❌ 无效选项，请输入 0-4")
            except (KeyboardInterrupt, EOFError):
                print("\n\n👋 用户取消，退出程序")
                return 0
        
        success = False
        
        # 处理选项1: 重新全部访谈
        if choice == '1':
            print("\n🚀 选项1: 全面测试（读取配置文件）")
            print("  - 正在读取配置...")
            
            # 直接调用方法，它会显示详细的配置信息和成本估算
            success = runner._run_comprehensive_test_with_full_pipeline()
        
        # 处理选项2: 测试小规模访谈
        elif choice == '2':
            print(f"\n🧪 选项2: {small_scale_desc}")
            for detail in small_scale_details:
                print(f"  {detail.replace('•', '-')}")
            print("  - 然后自动运行 数据处理 → PCA → 可视化")
            
            confirm = input("\n确认执行? (y/n): ").strip().lower()
            if confirm != 'y':
                print("❌ 已取消")
                return 0
            
            success = runner._run_small_scale_test_with_full_pipeline()
        
        # 处理选项3: 只分析现有数据
        elif choice == '3':
            print("\n📊 选项3: 只分析现有数据")
            print("  - 跳过访谈步骤")
            print("  - 运行: 数据处理 → PCA → 可视化")
            
            confirm = input("\n确认执行? (y/n): ").strip().lower()
            if confirm != 'y':
                print("❌ 已取消")
                return 0
            
            success = runner._run_data_processing_pipeline()
        
        # 处理选项4: 只访谈缺失的国家/语言
        elif choice == '4':
            print("\n🆕 选项4: 增量访谈（仅补齐缺失的国家/语言）")
            print("  - 自动比对 config/questions/multilingual/multilingual_questions_complete.json 与现有访谈数据")
            print("  - 跳过所有已经有结果的国家/语言组合")
            print("  - 访谈完成后立即运行 数据处理 → PCA → 可视化")
            
            confirm = input("\n确认执行? (y/n): ").strip().lower()
            if confirm != 'y':
                print("❌ 已取消")
                return 0
            
            success = runner._run_incremental_languages_with_full_pipeline()
        
        if success:
            print("\n🎊 分析完成!")
            return 0
        else:
            print("\n⚠️ 分析失败，请检查错误信息")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断分析")
        return 1
    except Exception as e:
        print(f"\n💥 分析过程中发生未预期错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
