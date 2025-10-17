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
from src.roleplay_multilingual.multilingual_roleplay_pca_analysis import MultilingualRoleplayPCAAnalysis
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
        
        print(f"🏠 项目根目录: {self.project_root}")
        print(f"📁 Multilingual数据目录: {self.data_path}")
        print(f"📁 结果目录: {self.results_path}")
        print(f"📁 Country Values数据目录: {self.country_values_data_path}")
        print(f"📁 English Roleplay数据目录: {self.roleplay_english_data_path}")
    
    def step0_multilingual_interview(self):
        """步骤0: 多语言角色扮演访谈"""
        print("\n" + "="*60)
        print("🎤 步骤0: 多语言角色扮演访谈")
        print("="*60)
        
        try:
            # 导入多语言访谈模块
            from src.roleplay_multilingual.multilingual_roleplay_interview import MultilingualRoleplayInterview
            
            # 初始化访谈器
            interviewer = MultilingualRoleplayInterview(data_path=str(self.data_path))
            
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
            
            # 获取推荐的国家列表（用于多语言访谈）
            recommended_countries_file = self.data_path / "recommended_countries_for_multilingual.json"
            
            # 默认国家列表作为备用
            default_countries = [
                'China', 'Russian Federation', 'Mexico', 'Egypt'  # 对应多语言支持的国家
            ]
            
            # 尝试读取推荐国家配置文件
            try:
                if recommended_countries_file.exists():
                    with open(recommended_countries_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if not content:
                            raise ValueError("配置文件为空")
                        recommended_data = json.loads(content)
                    
                    # 从新的配置格式中提取国家列表
                    countries_to_interview = []
                    if isinstance(recommended_data, dict):
                        # 新格式：按语言分组
                        for lang, country_list in recommended_data.items():
                            if lang != 'metadata' and isinstance(country_list, list):
                                for country_info in country_list:
                                    if isinstance(country_info, dict) and 'name' in country_info:
                                        country_name = country_info['name']
                                        if country_name not in countries_to_interview:
                                            countries_to_interview.append(country_name)
                    
                    # 如果没有提取到国家，尝试旧格式
                    if not countries_to_interview:
                        countries_to_interview = recommended_data.get('countries', default_countries)
                    
                    print(f"✅ 成功加载推荐国家列表: {len(countries_to_interview)} 个国家")
                    print(f"📋 国家列表: {', '.join(countries_to_interview)}")
                    
                else:
                    print("📋 推荐国家配置文件不存在，使用默认配置")
                    countries_to_interview = default_countries
                    
            except (json.JSONDecodeError, ValueError, UnicodeDecodeError) as e:
                print(f"❌ 推荐国家配置文件损坏: {e}")
                print("📋 使用默认国家列表")
                countries_to_interview = default_countries
                
                # 备份损坏的文件
                if recommended_countries_file.exists():
                    backup_file = recommended_countries_file.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
                    try:
                        recommended_countries_file.rename(backup_file)
                        print(f"💾 损坏文件已备份为: {backup_file.name}")
                    except Exception:
                        print("⚠️ 无法备份损坏文件")
                
            except Exception as e:
                print(f"❌ 读取推荐国家配置时发生未知错误: {e}")
                print("📋 使用默认国家列表")
                countries_to_interview = default_countries
            
            print(f"🎯 将访谈 {len(countries_to_interview)} 个国家")
            
            # 执行批量访谈
            print(f"\n🎯 开始批量多语言访谈...")
            
            # 验证访谈器是否正确初始化
            if not hasattr(interviewer, 'run_multilingual_experiment'):
                print("❌ 访谈器缺少 run_multilingual_experiment 方法")
                return False
            
            try:
                # 使用现有的run_multilingual_experiment方法
                interview_results = interviewer.run_multilingual_experiment(
                    models=None,  # 使用所有可用模型
                    max_workers=3  # 并发数
                )
            except Exception as e:
                print(f"❌ 访谈过程中发生错误: {e}")
                print("🔄 尝试使用单线程模式重新访谈...")
                try:
                    interview_results = interviewer.run_multilingual_experiment(
                        models=None,
                        max_workers=1  # 单线程模式
                    )
                except Exception as e2:
                    print(f"❌ 单线程访谈也失败: {e2}")
                    import traceback
                    traceback.print_exc()
                    return False
            
            if interview_results and interview_results.get('results'):
                print(f"✅ 多语言访谈完成!")
                print(f"📊 访谈统计:")
                print(f"   - 总任务数: {interview_results.get('total_tasks', 0)}")
                print(f"   - 成功任务数: {interview_results.get('successful_tasks', 0)}")
                success_rate = interview_results.get('successful_tasks', 0) / max(interview_results.get('total_tasks', 1), 1)
                print(f"   - 成功率: {success_rate:.1%}")
                print(f"   - 使用的模型: {interview_results.get('models', [])}")
                print(f"   - 支持的语言: {interview_results.get('languages', [])}")
                
                # 保存访谈结果到我们的数据目录
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                results_file = self.data_path / f"interview_data_{timestamp}.json"
                
                # 重新格式化结果以符合现有数据结构
                # 格式: {country: {language: {model: [responses...]}}}
                formatted_results = {}
                
                # 转换results格式为现有的层级结构
                results_list = interview_results.get('results', [])
                print(f"🔄 处理 {len(results_list)} 个访谈结果...")
                
                # 调试：显示第一个结果的结构
                if results_list:
                    first_result = results_list[0]
                    print(f"🔍 调试 - 第一个结果的字段: {list(first_result.keys()) if isinstance(first_result, dict) else type(first_result)}")
                    if isinstance(first_result, dict):
                        print(f"🔍 调试 - model字段值: {first_result.get('model', 'NOT_FOUND')}")
                        print(f"🔍 调试 - model_name字段值: {first_result.get('model_name', 'NOT_FOUND')}")
                
                processed_count = 0
                error_count = 0
                
                for i, result in enumerate(interview_results.get('results', [])):
                    try:
                        if result and 'responses' in result:
                            # 尝试多种可能的字段名
                            model_name = result.get('model_name') or result.get('model', 'unknown')
                            country = result.get('country', 'unknown')
                            language = result.get('language', 'unknown')
                            
                            # 验证必要字段
                            if model_name == 'unknown' or country == 'unknown' or language == 'unknown':
                                print(f"⚠️ 第 {i+1} 个结果缺少必要信息: model={model_name}, country={country}, language={language}")
                                error_count += 1
                                continue
                            
                            # 确保国家层级存在
                            if country not in formatted_results:
                                formatted_results[country] = {}
                            
                            # 确保语言层级存在
                            if language not in formatted_results[country]:
                                formatted_results[country][language] = {}
                            
                            # 确保模型层级存在
                            if model_name not in formatted_results[country][language]:
                                formatted_results[country][language][model_name] = []
                            
                            # 添加响应数据，格式与现有数据一致
                            response_entry = {
                                'repeat': len(formatted_results[country][language][model_name]) + 1,
                                'responses': result.get('responses', {})
                            }
                            formatted_results[country][language][model_name].append(response_entry)
                            processed_count += 1
                            
                            # 显示处理进度
                            if (processed_count) % 20 == 0:
                                print(f"   处理进度: {processed_count} 个结果已处理")
                        else:
                            print(f"⚠️ 第 {i+1} 个结果格式无效")
                            error_count += 1
                            
                    except Exception as e:
                        print(f"❌ 处理第 {i+1} 个结果时出错: {e}")
                        error_count += 1
                        continue
                
                print(f"📊 处理完成: {processed_count} 个成功, {error_count} 个错误")
                
                # 验证格式化结果
                if not formatted_results:
                    print("❌ 没有有效的访谈结果可保存")
                    return False
                
                # 统计结果
                total_countries = len(formatted_results)
                total_entries = sum(
                    len(responses)
                    for country_data in formatted_results.values()
                    for lang_data in country_data.values()
                    for responses in lang_data.values()
                )
                
                print(f"📊 最终统计:")
                print(f"   - 国家数量: {total_countries}")
                print(f"   - 总访谈条目: {total_entries}")
                
                # 保存访谈结果，带错误处理
                try:
                    with open(results_file, 'w', encoding='utf-8') as f:
                        json.dump(formatted_results, f, indent=2, ensure_ascii=False)
                    
                    # 验证保存的文件
                    if results_file.exists():
                        file_size = results_file.stat().st_size
                        print(f"💾 访谈结果已保存到: {results_file.name}")
                        print(f"📁 文件大小: {file_size:,} 字节")
                        
                        # 验证文件内容
                        try:
                            with open(results_file, 'r', encoding='utf-8') as f:
                                saved_data = json.load(f)
                            saved_countries = len(saved_data)
                            print(f"✅ 文件验证成功: {saved_countries} 个国家的数据")
                        except Exception as e:
                            print(f"⚠️ 文件验证失败: {e}")
                    else:
                        print("❌ 文件保存失败：文件不存在")
                        return False
                    
                    return True
                    
                except Exception as e:
                    print(f"❌ 保存访谈结果时发生错误: {e}")
                    
                    # 尝试保存到备用位置
                    try:
                        backup_file = self.data_path / f"interview_data_backup_{timestamp}.json"
                        with open(backup_file, 'w', encoding='utf-8') as f:
                            json.dump(formatted_results, f, indent=2, ensure_ascii=False)
                        print(f"💾 已保存到备用文件: {backup_file.name}")
                        return True
                    except Exception as e2:
                        print(f"❌ 备用保存也失败: {e2}")
                        return False
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
                config_path="comprehensive_multilingual_config.json"
            )
            
            # 运行测试
            results = tester.run_comprehensive_test(max_workers=3)
            
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
                config_path="small_scale_test_config.json"
            )
            
            # 运行小规模测试
            results = tester.run_comprehensive_test(max_workers=2)
            
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
        
        # 查找多语言问答数据文件
        if test_type:
            # 查找特定类型的访谈数据
            interview_data_files = list(self.data_path.glob(f"interview_data_{test_type}_*.json"))
        else:
            # 查找所有访谈数据
            interview_data_files = list(self.data_path.glob("interview_data_*.json"))
        
        if not interview_data_files:
            print(f"❌ 多语言问答数据文件不存在")
            print(f"请先运行步骤0进行多语言访谈，或确保 {self.data_path} 目录下有 interview_data_*.json 文件")
            return False
        
        # 使用最新的数据文件
        interview_data_file = max(interview_data_files, key=lambda x: x.stat().st_mtime)
        from datetime import datetime as dt
        print(f"📁 找到 {len(interview_data_files)} 个访谈数据文件")
        print(f"📁 使用最新文件: {interview_data_file.name}")
        print(f"📁 文件时间: {dt.fromtimestamp(interview_data_file.stat().st_mtime)}")
        
        try:
            # 初始化数据处理器
            processor = MultilingualRoleplayDataProcessor(data_path=str(self.data_path))
            
            # 查找已有的处理后数据文件（根据测试类型）
            if test_type:
                # 查找特定测试类型的处理文件
                processed_data_files = list(self.data_path.glob(f"multilingual_roleplay_processed_responses_ivs_format_{test_type}_*.pkl"))
                if not processed_data_files:
                    # 如果没有找到特定类型的，查找通用的
                    processed_data_files = list(self.data_path.glob("multilingual_roleplay_processed_responses_ivs_format_*.pkl"))
            else:
                processed_data_files = list(self.data_path.glob("multilingual_roleplay_processed_responses_ivs_format_*.pkl"))
            
            # 检查是否需要重新处理
            need_reprocess = True
            if processed_data_files:
                # 使用最新的处理文件
                latest_processed_file = max(processed_data_files, key=lambda x: x.stat().st_mtime)
                processed_data = pd.read_pickle(latest_processed_file)
                
                print(f"✅ 发现 {len(processed_data_files)} 个已处理数据文件")
                print(f"✅ 使用最新文件: {latest_processed_file.name}")
                print(f"✅ 数据行数: {len(processed_data)}")
                
                # 检查处理文件是否比访谈文件新
                processed_time = latest_processed_file.stat().st_mtime
                interview_time = interview_data_file.stat().st_mtime
                
                from datetime import datetime
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
            
            if need_reprocess:
                # 处理原始数据
                print("📊 处理原始多语言roleplay数据...")
                processed_data = processor.process_multilingual_data_to_ivs_format(str(interview_data_file))
                print(f"✅ 处理后数据: {len(processed_data)} 行")
                
                # 保存处理后的数据（带时间戳和测试类型）
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                type_suffix = f"_{test_type}" if test_type else ""
                processed_file = self.data_path / f"multilingual_roleplay_processed_responses_ivs_format{type_suffix}_{timestamp}.pkl"
                processed_data.to_pickle(processed_file)
                print(f"💾 处理后数据已保存: {processed_file.name}")
                print(f"🔗 对应访谈文件: {interview_data_file.name}")
            
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
            required_files = [
                self.country_values_data_path / "ivs_df.pkl",
                self.country_values_data_path / "country_codes.pkl"
            ]
            
            for file_path in required_files:
                if not file_path.exists():
                    print(f"❌ 缺少必要文件: {file_path}")
                    return False
            
            # 查找最新的处理后数据文件（根据测试类型）
            if test_type:
                processed_files = list(self.data_path.glob(f"multilingual_roleplay_processed_responses_ivs_format_{test_type}_*.pkl"))
                if not processed_files:
                    # 如果没有找到特定类型的，查找通用的但要确保数据匹配
                    processed_files = list(self.data_path.glob("multilingual_roleplay_processed_responses_ivs_format_*.pkl"))
                    print(f"⚠️ 未找到{test_type}特定的处理文件，使用通用处理文件")
            else:
                processed_files = list(self.data_path.glob("multilingual_roleplay_processed_responses_ivs_format_*.pkl"))
            if not processed_files:
                print(f"❌ 未找到处理后的数据文件")
                print(f"请先运行步骤1进行数据处理")
                return False
            
            latest_processed_file = max(processed_files, key=lambda x: x.stat().st_mtime)
            print(f"📁 使用最新处理文件: {latest_processed_file.name}")
            
            # 使用多语言PCA分析器
            print("\n1️⃣ 初始化多语言PCA分析器...")
            analyzer = MultilingualRoleplayPCAAnalysis(data_path=str(self.country_values_data_path))
            
            # 设置多语言数据路径
            analyzer.multilingual_data_path = self.data_path
            
            # 运行完整分析
            print("\n2️⃣ 运行多语言+IVS联合PCA分析...")
            entity_scores = analyzer.run_multilingual_analysis_for_runner()
            
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
            
            # 修复国家名称匹配问题
            print("\n3️⃣ 修复国家名称匹配...")
            entity_scores_fixed = self._fix_country_names(entity_scores)
            
            # 保存修复后的结果（带时间戳）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            type_suffix = f"_{test_type}" if test_type else ""
            entity_scores_path = self.data_path / f"multilingual_entity_scores_pca_fixed{type_suffix}_{timestamp}.pkl"
            entity_scores_fixed.to_pickle(entity_scores_path)
            print(f"💾 保存修复后的实体分数到: {entity_scores_path.name}")
            
            # 同时保存JSON格式
            entity_scores_json_path = self.data_path / f"multilingual_entity_scores_pca_fixed{type_suffix}_{timestamp}.json"
            entity_scores_fixed.to_json(entity_scores_json_path, orient='records', indent=2)
            print(f"💾 保存修复后的实体分数JSON到: {entity_scores_json_path.name}")
            
            # 保存最新文件路径供后续步骤使用
            self._latest_pca_file = str(entity_scores_path)
            
            return True
            
        except Exception as e:
            print(f"❌ 多语言+IVS联合PCA分析失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _fix_country_names(self, entity_scores):
        """修复国家名称匹配问题"""
        print("🔧 修复IVS数据的国家名称匹配...")
        
        # 加载国家代码数据
        country_codes = pd.read_pickle(self.country_values_data_path / "country_codes.pkl")
        
        # 分离数据
        ivs_data = entity_scores[entity_scores['data_source'] == 'IVS'].copy()
        multilingual_data = entity_scores[entity_scores['data_source'] == 'Multilingual'].copy()
        
        if len(ivs_data) > 0:
            # 确保数据类型匹配
            ivs_data['country_code_int'] = pd.to_numeric(ivs_data['country_code'], errors='coerce')
            country_codes['Numeric_int'] = pd.to_numeric(country_codes['Numeric'], errors='coerce')
            
            # 重新合并，确保获取正确的国家名称
            ivs_fixed = ivs_data.merge(
                country_codes[['Numeric_int', 'Country', 'Cultural Region']], 
                left_on='country_code_int', 
                right_on='Numeric_int', 
                how='left',
                suffixes=('_old', '')
            )
            
            # 清理列名，保留需要的列
            columns_to_keep = ['country_code', 'data_source', 'PC1_rescaled', 'PC2_rescaled', 
                               'Country', 'Cultural Region']
            ivs_final = ivs_fixed[columns_to_keep].copy()
            
            print(f"✅ 修复了 {ivs_final['Country'].notna().sum()}/{len(ivs_final)} 个国家名称")
        else:
            ivs_final = ivs_data
        
        # 重新组合完整数据
        if len(multilingual_data) > 0:
            # 检查多语言数据中实际存在的列
            available_columns = ['country_code', 'data_source', 'PC1_rescaled', 'PC2_rescaled']
            if 'model_name' in multilingual_data.columns:
                available_columns.append('model_name')
            if 'language' in multilingual_data.columns:
                available_columns.append('language')
            
            multilingual_final = multilingual_data[available_columns].copy()
            entity_scores_final = pd.concat([ivs_final, multilingual_final], ignore_index=True)
        else:
            entity_scores_final = ivs_final
        
        return entity_scores_final
    
    def step3_language_comparison_analysis(self, test_type: str = None):
        """步骤3: 英文vs本国语言效果对比分析"""
        print("\n" + "="*60)
        print("🌐 步骤3: 英文vs本国语言效果对比分析")
        print("="*60)
        
        try:
            # 查找最新的多语言PCA结果文件
            if test_type:
                multilingual_files = list(self.data_path.glob(f"multilingual_entity_scores_pca_fixed_{test_type}_*.pkl"))
            else:
                multilingual_files = list(self.data_path.glob("multilingual_entity_scores_pca_fixed_*.pkl"))
            if not multilingual_files:
                print(f"❌ 未找到多语言PCA结果文件")
                print(f"请先运行步骤2进行PCA分析")
                return False
            
            multilingual_path = max(multilingual_files, key=lambda x: x.stat().st_mtime)
            print(f"📁 使用最新多语言PCA文件: {multilingual_path.name}")
            
            print("\n1️⃣ 加载多语言数据...")
            multilingual_scores = pd.read_pickle(multilingual_path)
            
            print(f"✅ 多语言数据: {len(multilingual_scores)} 个实体")
            
            # 分离真实国家数据作为基准
            print("\n2️⃣ 准备基准数据...")
            real_countries = multilingual_scores[multilingual_scores['data_source'] == 'IVS'].copy()
            multilingual_roleplay = multilingual_scores[multilingual_scores['data_source'] == 'Multilingual'].copy()
            
            # 从多语言数据中分离英文和非英文部分
            multilingual_english = multilingual_roleplay[multilingual_roleplay['language'] == 'en'].copy()
            multilingual_native = multilingual_roleplay[multilingual_roleplay['language'] != 'en'].copy()
            
            print(f"   真实国家: {len(real_countries)} 个")
            print(f"   多语言roleplay总计: {len(multilingual_roleplay)} 个")
            print(f"     - 英文部分: {len(multilingual_english)} 个")
            print(f"     - 本国语言部分: {len(multilingual_native)} 个")
            
            # 执行距离对比分析
            print("\n3️⃣ 执行距离对比分析...")
            comparison_results = self._calculate_language_distance_comparison(
                real_countries, multilingual_native, multilingual_english
            )
            
            # 保存对比结果（带时间戳）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            comparison_path = self.results_path / f"language_comparison_analysis_{timestamp}.json"
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
    
    def _calculate_language_distance_comparison(self, real_countries, multilingual_native, multilingual_english):
        """计算英文vs本国语言的距离对比（仅对比多语言数据中的两种语言）"""
        print("📏 计算距离对比...")
        
        comparison_results = {
            'summary': {},
            'country_details': {},
            'model_performance': {},
            'language_effectiveness': {},
            'model_specific_analysis': {}  # 新增：每个模型的详细分析
        }
        
        # 使用传入的分离后数据
        native_data = multilingual_native
        english_data = multilingual_english
        
        print(f"📊 本国语言数据: {len(native_data)} 个实体")
        print(f"📊 英文数据: {len(english_data)} 个实体")
        
        # 为真实国家建立查找字典（使用Country列）
        real_country_coords = {}
        for _, row in real_countries.iterrows():
            country_name = row.get('Country', 'Unknown')
            if pd.notna(country_name) and country_name != 'Unknown':
                real_country_coords[country_name] = (row['PC1_rescaled'], row['PC2_rescaled'])
        
        print(f"📊 真实国家数量: {len(real_country_coords)}")
        
        # 获取多语言数据中的国家列表（合并本国语言和英文数据）
        all_multilingual_data = pd.concat([native_data, english_data], ignore_index=True)
        multilingual_countries = set(all_multilingual_data['country_code'].dropna().unique())
        print(f"📊 多语言数据覆盖的国家: {len(multilingual_countries)}")
        
        # 找到可以匹配的国家
        matchable_countries = real_country_coords.keys() & multilingual_countries
        print(f"📊 可匹配的国家数量: {len(matchable_countries)}")
        print(f"📊 可匹配的国家: {sorted(list(matchable_countries))}")
        
        # 按国家分组计算距离
        country_comparisons = {}
        for country_name in matchable_countries:
            real_coords = real_country_coords[country_name]
            country_results = {
                'real_coordinates': real_coords,
                'native_distances': [],
                'english_distances': [],
                'models': {}
            }
            
            # 计算本国语言距离
            country_native = native_data[native_data['country_code'] == country_name]
            for _, row in country_native.iterrows():
                model_coords = (row['PC1_rescaled'], row['PC2_rescaled'])
                distance = euclidean(real_coords, model_coords)
                country_results['native_distances'].append(distance)
                
                model_name = row.get('model_name', 'Unknown')
                if model_name not in country_results['models']:
                    country_results['models'][model_name] = {}
                country_results['models'][model_name]['native_distance'] = distance
            
            # 计算英文距离
            country_english = english_data[english_data['country_code'] == country_name]
            for _, row in country_english.iterrows():
                model_coords = (row['PC1_rescaled'], row['PC2_rescaled'])
                distance = euclidean(real_coords, model_coords)
                country_results['english_distances'].append(distance)
                
                model_name = row.get('model_name', 'Unknown')
                if model_name not in country_results['models']:
                    country_results['models'][model_name] = {}
                country_results['models'][model_name]['english_distance'] = distance
            
            # 计算平均距离
            country_results['avg_native_distance'] = np.mean(country_results['native_distances']) if country_results['native_distances'] else None
            country_results['avg_english_distance'] = np.mean(country_results['english_distances']) if country_results['english_distances'] else None
            
            country_comparisons[country_name] = country_results
        
        # 汇总统计
        all_native_distances = []
        all_english_distances = []
        
        for country_data in country_comparisons.values():
            if country_data['native_distances']:
                all_native_distances.extend(country_data['native_distances'])
            if country_data['english_distances']:
                all_english_distances.extend(country_data['english_distances'])
        
        comparison_results['summary'] = {
            'total_countries_analyzed': len(country_comparisons),
            'native_language_avg_distance': float(np.mean(all_native_distances)) if all_native_distances else None,
            'english_language_avg_distance': float(np.mean(all_english_distances)) if all_english_distances else None,
            'language_improvement': None
        }
        
        # 计算改进百分比（负值表示本国语言更好，正值表示英文更好）
        if comparison_results['summary']['native_language_avg_distance'] and comparison_results['summary']['english_language_avg_distance']:
            native_avg = comparison_results['summary']['native_language_avg_distance']
            english_avg = comparison_results['summary']['english_language_avg_distance']
            # 计算英文相对于本国语言的改进百分比
            improvement = ((native_avg - english_avg) / native_avg) * 100
            comparison_results['summary']['language_improvement'] = float(improvement)
        
        comparison_results['country_details'] = country_comparisons
        
        # 新增：按模型分析语言效果
        print("\n📊 按模型分析语言效果...")
        model_analysis = self._analyze_model_specific_language_performance(
            native_data, english_data, real_country_coords, matchable_countries
        )
        comparison_results['model_specific_analysis'] = model_analysis
        
        # 输出统计信息
        print(f"✅ 分析了 {len(country_comparisons)} 个国家")
        if comparison_results['summary']['native_language_avg_distance']:
            print(f"📊 本国语言平均距离: {comparison_results['summary']['native_language_avg_distance']:.3f}")
        if comparison_results['summary']['english_language_avg_distance']:
            print(f"📊 英文平均距离: {comparison_results['summary']['english_language_avg_distance']:.3f}")
        if comparison_results['summary']['language_improvement']:
            improvement = comparison_results['summary']['language_improvement']
            if improvement > 0:
                print(f"📊 英文比本国语言好 {improvement:.1f}%")
            else:
                print(f"📊 本国语言比英文好 {-improvement:.1f}%")
        
        # 输出每个模型的分析结果
        print(f"\n🤖 各模型语言效果对比:")
        for model_name, model_stats in model_analysis.items():
            if model_stats['native_avg_distance'] and model_stats['english_avg_distance']:
                native_avg = model_stats['native_avg_distance']
                english_avg = model_stats['english_avg_distance']
                improvement = ((native_avg - english_avg) / native_avg) * 100
                
                print(f"   {model_name.split('/')[-1]}:")
                print(f"     本国语言: {native_avg:.3f}, 英文: {english_avg:.3f}")
                if improvement > 0:
                    print(f"     → 英文效果更好 ({improvement:.1f}%)")
                else:
                    print(f"     → 本国语言效果更好 ({-improvement:.1f}%)")
        
        return comparison_results
    
    def _analyze_model_specific_language_performance(self, native_data, english_data, real_country_coords, matchable_countries):
        """分析每个模型的语言效果对比"""
        model_analysis = {}
        
        # 获取所有模型
        all_models = set()
        if 'model_name' in native_data.columns:
            all_models.update(native_data['model_name'].dropna().unique())
        if 'model_name' in english_data.columns:
            all_models.update(english_data['model_name'].dropna().unique())
        
        for model_name in all_models:
            model_stats = {
                'model_name': model_name,
                'native_distances': [],
                'english_distances': [],
                'native_avg_distance': None,
                'english_avg_distance': None,
                'language_improvement': None,
                'countries_analyzed': [],
                'native_count': 0,
                'english_count': 0
            }
            
            # 分析该模型在每个国家的表现
            for country_name in matchable_countries:
                real_coords = real_country_coords[country_name]
                
                # 本国语言数据
                model_native = native_data[
                    (native_data['country_code'] == country_name) & 
                    (native_data['model_name'] == model_name)
                ]
                
                for _, row in model_native.iterrows():
                    model_coords = (row['PC1_rescaled'], row['PC2_rescaled'])
                    distance = euclidean(real_coords, model_coords)
                    model_stats['native_distances'].append(distance)
                    model_stats['native_count'] += 1
                
                # 英文数据
                model_english = english_data[
                    (english_data['country_code'] == country_name) & 
                    (english_data['model_name'] == model_name)
                ]
                
                for _, row in model_english.iterrows():
                    model_coords = (row['PC1_rescaled'], row['PC2_rescaled'])
                    distance = euclidean(real_coords, model_coords)
                    model_stats['english_distances'].append(distance)
                    model_stats['english_count'] += 1
                
                # 如果该模型在这个国家有数据，记录
                if len(model_native) > 0 or len(model_english) > 0:
                    model_stats['countries_analyzed'].append(country_name)
            
            # 计算平均距离
            if model_stats['native_distances']:
                model_stats['native_avg_distance'] = float(np.mean(model_stats['native_distances']))
            if model_stats['english_distances']:
                model_stats['english_avg_distance'] = float(np.mean(model_stats['english_distances']))
            
            # 计算改进百分比
            if model_stats['native_avg_distance'] and model_stats['english_avg_distance']:
                native_avg = model_stats['native_avg_distance']
                english_avg = model_stats['english_avg_distance']
                improvement = ((native_avg - english_avg) / native_avg) * 100
                model_stats['language_improvement'] = float(improvement)
            
            model_analysis[model_name] = model_stats
        
        return model_analysis
    
    def _generate_language_comparison_visualization(self, comparison_results):
        """生成语言对比可视化"""
        print("🎨 生成语言对比可视化...")
        
        # 1. 生成距离对比柱状图
        self._plot_distance_comparison_bar(comparison_results)
        
        # 2. 生成国家级别的详细对比
        self._plot_country_level_comparison(comparison_results)
        
        # 3. 生成交互式对比图
        self._plot_interactive_language_comparison(comparison_results)
        
        # 4. 新增：生成每个模型的语言效果对比图
        self._plot_model_specific_language_comparison(comparison_results)
    
    def _plot_distance_comparison_bar(self, comparison_results):
        """绘制距离对比柱状图"""
        summary = comparison_results['summary']
        
        distances = []
        labels = []
        colors = []
        
        if summary['native_language_avg_distance']:
            distances.append(summary['native_language_avg_distance'])
            labels.append('Native Language')
            colors.append('#2E8B57')  # 深绿色
        
        if summary['english_language_avg_distance']:
            distances.append(summary['english_language_avg_distance'])
            labels.append('English Language')
            colors.append('#4169E1')  # 皇家蓝
        
        if not distances:
            print("⚠️ 没有足够的数据生成距离对比图")
            return
        
        plt.figure(figsize=(12, 8))
        bars = plt.bar(labels, distances, color=colors, alpha=0.8, edgecolor='black', linewidth=1)
        
        # 添加数值标签
        for bar, distance in zip(bars, distances):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{distance:.3f}', ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        plt.title('Language Effectiveness Comparison\n(Lower Distance = Better Performance)', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.ylabel('Average Distance to Real Countries', fontsize=14, fontweight='bold')
        plt.xlabel('Language Type', fontsize=14, fontweight='bold')
        
        # 添加改进百分比注释
        if summary['language_improvement']:
            improvement = summary['language_improvement']
            if improvement > 0:
                text = f'English is {improvement:.1f}% better'
                color = 'lightblue'
            else:
                text = f'Native is {-improvement:.1f}% better'
                color = 'lightgreen'
            
            plt.text(0.5, max(distances) * 0.8, text, 
                    transform=plt.gca().transAxes, ha='center', fontsize=12,
                    bbox=dict(boxstyle='round,pad=0.5', facecolor=color, alpha=0.7))
        
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        
        # 保存图片（带时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = self.results_path / f"language_distance_comparison_{timestamp}.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"✅ 距离对比图已保存到: {save_path.name}")
    
    def _plot_country_level_comparison(self, comparison_results):
        """绘制国家级别的详细对比"""
        country_details = comparison_results['country_details']
        
        # 准备数据
        countries = []
        native_distances = []
        english_distances = []
        
        for country, data in country_details.items():
            if data['avg_native_distance'] or data['avg_english_distance']:
                countries.append(country)
                native_distances.append(data['avg_native_distance'] or 0)
                english_distances.append(data['avg_english_distance'] or 0)
        
        if not countries:
            print("⚠️ 没有足够的数据生成国家级别对比图")
            return
        
        # 限制显示前15个国家（避免图表过于拥挤）
        if len(countries) > 15:
            countries = countries[:15]
            native_distances = native_distances[:15]
            english_distances = english_distances[:15]
        
        x = np.arange(len(countries))
        width = 0.35
        
        plt.figure(figsize=(16, 10))
        
        plt.bar(x - width/2, native_distances, width, label='Native Language', 
               color='#2E8B57', alpha=0.8, edgecolor='black', linewidth=0.5)
        plt.bar(x + width/2, english_distances, width, label='English Language', 
               color='#4169E1', alpha=0.8, edgecolor='black', linewidth=0.5)
        
        plt.title('Country-Level Language Effectiveness Comparison', fontsize=16, fontweight='bold', pad=20)
        plt.ylabel('Average Distance to Real Country', fontsize=14, fontweight='bold')
        plt.xlabel('Countries', fontsize=14, fontweight='bold')
        plt.xticks(x, countries, rotation=45, ha='right')
        plt.legend(fontsize=12)
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        
        # 保存图片（带时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = self.results_path / f"country_level_language_comparison_{timestamp}.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"✅ 国家级别对比图已保存到: {save_path.name}")
    
    def _plot_interactive_language_comparison(self, comparison_results):
        """生成交互式语言对比图"""
        if not PLOTLY_AVAILABLE:
            print("⚠️ plotly未安装，跳过交互式图表生成")
            return
        
        country_details = comparison_results['country_details']
        
        # 准备数据
        countries = []
        native_distances = []
        english_distances = []
        
        for country, data in country_details.items():
            countries.append(country)
            native_distances.append(data['avg_native_distance'])
            english_distances.append(data['avg_english_distance'])
        
        # 创建交互式图表
        fig = go.Figure()
        
        # 添加本国语言数据
        fig.add_trace(go.Bar(
            name='Native Language',
            x=countries,
            y=native_distances,
            marker_color='#2E8B57',
            opacity=0.8,
            hovertemplate='<b>%{x}</b><br>Native Language Distance: %{y:.3f}<extra></extra>'
        ))
        
        # 添加英文数据
        fig.add_trace(go.Bar(
            name='English Language',
            x=countries,
            y=english_distances,
            marker_color='#4169E1',
            opacity=0.8,
            hovertemplate='<b>%{x}</b><br>English Distance: %{y:.3f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(
                text='<b>Interactive Language Effectiveness Comparison</b><br><sub>Lower Distance = Better Performance</sub>',
                x=0.5,
                font=dict(size=18)
            ),
            xaxis=dict(
                title='<b>Countries</b>',
                titlefont=dict(size=14),
                tickangle=45
            ),
            yaxis=dict(
                title='<b>Average Distance to Real Country</b>',
                titlefont=dict(size=14)
            ),
            barmode='group',
            width=1200,
            height=700,
            showlegend=True,
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='center',
                x=0.5
            ),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        # 保存HTML文件（带时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_path = self.results_path / f"interactive_language_comparison_{timestamp}.html"
        fig.write_html(html_path)
        print(f"✅ 交互式语言对比图已保存到: {html_path.name}")
    
    def _plot_model_specific_language_comparison(self, comparison_results):
        """绘制每个模型的语言效果对比图"""
        model_analysis = comparison_results.get('model_specific_analysis', {})
        
        if not model_analysis:
            print("⚠️ 没有模型特定分析数据，跳过模型对比图")
            return
        
        # 准备数据
        models = []
        native_distances = []
        english_distances = []
        improvements = []
        
        for model_name, stats in model_analysis.items():
            if stats['native_avg_distance'] and stats['english_avg_distance']:
                models.append(model_name.split('/')[-1])  # 使用简短名称
                native_distances.append(stats['native_avg_distance'])
                english_distances.append(stats['english_avg_distance'])
                improvements.append(stats['language_improvement'])
        
        if not models:
            print("⚠️ 没有足够的数据生成模型对比图")
            return
        
        # 1. 生成静态对比图
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
        
        # 左图：距离对比
        x = np.arange(len(models))
        width = 0.35
        
        bars1 = ax1.bar(x - width/2, native_distances, width, label='Native Language', 
                       color='#2E8B57', alpha=0.8, edgecolor='black')
        bars2 = ax1.bar(x + width/2, english_distances, width, label='English Language', 
                       color='#4169E1', alpha=0.8, edgecolor='black')
        
        # 添加数值标签
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{height:.3f}', ha='center', va='bottom', fontsize=10)
        
        for bar in bars2:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{height:.3f}', ha='center', va='bottom', fontsize=10)
        
        ax1.set_xlabel('Models', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Average Distance to Real Countries', fontsize=12, fontweight='bold')
        ax1.set_title('Model-Specific Language Performance Comparison\n(Lower Distance = Better Performance)', 
                     fontsize=14, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(models, rotation=45, ha='right')
        ax1.legend()
        ax1.grid(True, alpha=0.3, axis='y')
        
        # 右图：改进百分比
        colors = ['#2E8B57' if imp < 0 else '#4169E1' for imp in improvements]
        bars3 = ax2.bar(models, improvements, color=colors, alpha=0.8, edgecolor='black')
        
        # 添加数值标签
        for bar, imp in zip(bars3, improvements):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + (0.5 if height > 0 else -0.5),
                    f'{imp:.1f}%', ha='center', va='bottom' if height > 0 else 'top', fontsize=10)
        
        ax2.set_xlabel('Models', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Language Improvement (%)', fontsize=12, fontweight='bold')
        ax2.set_title('Language Effectiveness Improvement by Model\n(Positive = English Better, Negative = Native Better)', 
                     fontsize=14, fontweight='bold')
        ax2.set_xticklabels(models, rotation=45, ha='right')
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        ax2.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        # 保存静态图（带时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = self.results_path / f"model_specific_language_comparison_{timestamp}.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"✅ 模型语言对比图已保存到: {save_path.name}")
        
        # 2. 生成交互式对比图
        if PLOTLY_AVAILABLE:
            self._plot_interactive_model_comparison(model_analysis)
    
    def _plot_interactive_model_comparison(self, model_analysis):
        """生成交互式模型对比图"""
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        # 准备数据
        models = []
        native_distances = []
        english_distances = []
        improvements = []
        native_counts = []
        english_counts = []
        
        for model_name, stats in model_analysis.items():
            if stats['native_avg_distance'] and stats['english_avg_distance']:
                models.append(model_name.split('/')[-1])
                native_distances.append(stats['native_avg_distance'])
                english_distances.append(stats['english_avg_distance'])
                improvements.append(stats['language_improvement'])
                native_counts.append(stats['native_count'])
                english_counts.append(stats['english_count'])
        
        # 创建子图
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Distance Comparison by Model', 'Language Improvement by Model'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # 左图：距离对比
        fig.add_trace(
            go.Bar(
                name='Native Language',
                x=models,
                y=native_distances,
                marker_color='#2E8B57',
                opacity=0.8,
                hovertemplate='<b>%{x}</b><br>Native Distance: %{y:.3f}<br>Count: %{customdata}<extra></extra>',
                customdata=native_counts
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(
                name='English Language',
                x=models,
                y=english_distances,
                marker_color='#4169E1',
                opacity=0.8,
                hovertemplate='<b>%{x}</b><br>English Distance: %{y:.3f}<br>Count: %{customdata}<extra></extra>',
                customdata=english_counts
            ),
            row=1, col=1
        )
        
        # 右图：改进百分比
        colors = ['#2E8B57' if imp < 0 else '#4169E1' for imp in improvements]
        fig.add_trace(
            go.Bar(
                name='Language Improvement',
                x=models,
                y=improvements,
                marker_color=colors,
                opacity=0.8,
                hovertemplate='<b>%{x}</b><br>Improvement: %{y:.1f}%<br>' +
                             '<i>Positive = English Better<br>Negative = Native Better</i><extra></extra>',
                showlegend=False
            ),
            row=1, col=2
        )
        
        # 更新布局
        fig.update_layout(
            title=dict(
                text='<b>Model-Specific Language Performance Analysis</b>',
                x=0.5,
                font=dict(size=18)
            ),
            barmode='group',
            width=1400,
            height=600,
            showlegend=True
        )
        
        fig.update_xaxes(title_text="Models", row=1, col=1, tickangle=45)
        fig.update_yaxes(title_text="Average Distance", row=1, col=1)
        fig.update_xaxes(title_text="Models", row=1, col=2, tickangle=45)
        fig.update_yaxes(title_text="Improvement (%)", row=1, col=2)
        
        # 添加零线
        fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5, row=1, col=2)
        
        # 保存HTML文件（带时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_path = self.results_path / f"interactive_model_language_comparison_{timestamp}.html"
        fig.write_html(html_path)
        print(f"✅ 交互式模型语言对比图已保存到: {html_path.name}")
    
    def step4_visualization(self, test_type: str = None):
        """步骤4: 综合可视化"""
        print("\n" + "="*60)
        print("🎨 步骤4: 综合可视化")
        print("="*60)
        
        try:
            # 查找最新的修复后PCA结果文件
            if test_type:
                pca_files = list(self.data_path.glob(f"multilingual_entity_scores_pca_fixed_{test_type}_*.pkl"))
            else:
                pca_files = list(self.data_path.glob("multilingual_entity_scores_pca_fixed_*.pkl"))
            if not pca_files:
                print(f"❌ 未找到修复后的PCA结果文件")
                print(f"请先运行步骤2进行PCA分析")
                return False
            
            entity_scores_path = max(pca_files, key=lambda x: x.stat().st_mtime)
            print(f"📁 使用最新PCA文件: {entity_scores_path.name}")
            
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
            static_map_path = self.results_path / f"multilingual_cultural_map_corrected{type_suffix}_{timestamp}.png"
            self._generate_corrected_static_map(entity_scores, static_map_path)
            print(f"✅ 修正后的静态文化地图已保存到: {static_map_path.name}")
            
            # 生成修正后的交互式HTML地图
            print("\n3️⃣ 生成修正后的交互式HTML地图...")
            interactive_map_path = self.results_path / f"multilingual_cultural_map_interactive_fixed{type_suffix}_{timestamp}.html"
            self._generate_corrected_interactive_map(entity_scores, interactive_map_path)
            print(f"✅ 修正后的交互式地图已保存到: {interactive_map_path.name}")
            
            # 初始化可视化器（用于其他图表）
            print("\n4️⃣ 生成其他分析图表...")
            visualizer = MultilingualRoleplayVisualizer(
                data_path=str(self.data_path),
                results_path=str(self.results_path)
            )
            
            # 生成语言对比图
            language_comparison_path = self.results_path / f"language_model_comparison_{timestamp}.png"
            visualizer.plot_language_comparison(data=entity_scores, save_path=str(language_comparison_path))
            print(f"✅ 语言对比图已保存到: {language_comparison_path.name}")
            
            # 分析多语言准确性
            print("\n5️⃣ 生成多语言统计...")
            accuracy_analysis = {
                'timestamp': timestamp,
                'total_entities': len(entity_scores),
                'multilingual_entities': len(multilingual_data),
                'ivs_entities': len(ivs_data),
                'pc1_range': [float(entity_scores['PC1_rescaled'].min()), float(entity_scores['PC1_rescaled'].max())],
                'pc2_range': [float(entity_scores['PC2_rescaled'].min()), float(entity_scores['PC2_rescaled'].max())]
            }
            
            # 保存准确性分析结果
            accuracy_analysis_path = self.results_path / f"multilingual_accuracy_analysis_{timestamp}.json"
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
            summary_path = self.results_path / f"summary_statistics_{timestamp}.txt"
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
            
            # 保存文化坐标数据到results目录
            cultural_coordinates_path = self.results_path / f"multilingual_cultural_coordinates_{timestamp}.json"
            entity_scores.to_json(cultural_coordinates_path, orient='records', indent=2)
            print(f"✅ 文化坐标数据已保存到: {cultural_coordinates_path.name}")
            
            return True
            
        except Exception as e:
            print(f"❌ 可视化失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _generate_corrected_static_map(self, entity_scores, save_path):
        """生成修正后的静态文化地图"""
        # 分离数据
        ivs_data = entity_scores[entity_scores['data_source'] == 'IVS']
        multilingual_data = entity_scores[entity_scores['data_source'] == 'Multilingual']
        
        # 设置图形样式
        plt.style.use('default')
        fig, ax = plt.subplots(1, 1, figsize=(18, 14))
        
        # 文化区域颜色映射（与llm_values保持一致）
        cultural_region_colors = {
            'African-Islamic': '#cc79a7',
            'Orthodox Europe': '#0072b2', 
            'Catholic Europe': '#e69f00',
            'Latin America': '#999999',
            'West & South Asia': '#f0e442',
            'Confucian': '#d55e00',
            'Protestant Europe': '#56b4e9',
            'English-Speaking': '#009e73'
        }
        
        # 绘制IVS国家（背景）
        if len(ivs_data) > 0 and 'Cultural Region' in ivs_data.columns:
            regions = ivs_data['Cultural Region'].dropna().unique()
            
            for region in regions:
                if region in cultural_region_colors:
                    region_data = ivs_data[ivs_data['Cultural Region'] == region]
                    ax.scatter(
                        region_data['PC1_rescaled'], 
                        region_data['PC2_rescaled'],
                        c=cultural_region_colors[region], 
                        alpha=0.7, 
                        s=80, 
                        label=f'{region} (Countries)',
                        marker='o',
                        edgecolors='white',
                        linewidth=1
                    )
        
        # 绘制多语言数据（前景）- 按模型和语言分组
        if len(multilingual_data) > 0 and 'model_name' in multilingual_data.columns and 'language' in multilingual_data.columns:
            # 获取所有模型和语言
            models = sorted(multilingual_data['model_name'].dropna().unique())
            languages = sorted(multilingual_data['language'].dropna().unique())
            
            # 模型颜色映射
            model_colors = {
                'deepseek/deepseek-chat-v3-0324': '#E74C3C',
                'google/gemini-2.0-flash-001': '#3498DB', 
                'meta-llama/llama-3.3-70b-instruct': '#9B59B6',
                'mistralai/mistral-nemo': '#F39C12',
                'openai/gpt-4o-mini': '#2ECC71',
                'qwen/qwq-32b': '#E67E22'
            }
            
            # 语言标记映射
            language_markers = {'english': 'o', 'native': 'D'}
            
            for model in models:
                model_short = model.split('/')[-1] if '/' in model else model
                model_color = model_colors.get(model, '#95A5A6')
                
                for lang in languages:
                    model_lang_data = multilingual_data[
                        (multilingual_data['model_name'] == model) & 
                        (multilingual_data['language'] == lang)
                    ]
                    
                    if len(model_lang_data) > 0:
                        # 根据语言调整透明度和大小
                        alpha = 0.8 if lang == 'english' else 0.6
                        size = 60 if lang == 'english' else 40
                        
                        # 改进的重复坐标处理：全局检测并添加偏移
                        coords_data = model_lang_data[['PC1_rescaled', 'PC2_rescaled']].copy()
                        
                        import numpy as np
                        
                        # 为每个数据点检查全局重复情况
                        for idx in coords_data.index:
                            current_x = round(coords_data.loc[idx, 'PC1_rescaled'], 6)
                            current_y = round(coords_data.loc[idx, 'PC2_rescaled'], 6)
                            
                            # 检查与所有多语言数据的重复情况
                            global_duplicates = multilingual_data[
                                (multilingual_data['PC1_rescaled'].round(6) == current_x) & 
                                (multilingual_data['PC2_rescaled'].round(6) == current_y)
                            ]
                            
                            if len(global_duplicates) > 1:
                                # 使用基于数据点信息的确定性偏移
                                current_row = model_lang_data.loc[idx]
                                
                                # 创建唯一标识符用于确定性偏移
                                identifier = f"{current_row['country_code']}_{current_row['model_name']}_{current_row['language']}"
                                hash_val = hash(identifier) % 1000
                                
                                # 使用更大的偏移量和圆形分布
                                offset_factor = 0.15  # 增加偏移量使点更明显分离
                                angle = (hash_val * 137.5) % 360  # 黄金角度分布
                                
                                offset_x = offset_factor * np.cos(np.radians(angle))
                                offset_y = offset_factor * np.sin(np.radians(angle))
                                
                                coords_data.loc[idx, 'PC1_rescaled'] += offset_x
                                coords_data.loc[idx, 'PC2_rescaled'] += offset_y
                        
                        ax.scatter(
                            coords_data['PC1_rescaled'], 
                            coords_data['PC2_rescaled'],
                            c=model_color, 
                            alpha=alpha, 
                            s=size, 
                            label=f'{model_short} ({lang.title()})',
                            marker=language_markers.get(lang, 'o'),
                            edgecolors='black',
                            linewidth=0.8
                        )
        
        # 修正坐标轴标签（按照llm_values的正确设置）
        ax.set_xlabel('PC1: Survival vs Self-Expression Values', fontsize=16, fontweight='bold')
        ax.set_ylabel('PC2: Traditional vs Secular-Rational Values', fontsize=16, fontweight='bold')
        ax.set_title('Cultural Values Map: Multilingual LLM Roleplay vs Real Countries\\n(Inglehart-Welzel Framework)', 
                     fontsize=20, fontweight='bold', pad=25)
        
        # 添加网格和坐标轴
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.4, linewidth=1)
        ax.axvline(x=0, color='black', linestyle='-', alpha=0.4, linewidth=1)
        
        # 添加象限标签（修正后的标签）
        quadrant_style = dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8, edgecolor='gray')
        ax.text(0.02, 0.98, 'Self-Expression\\n& Secular-Rational', 
                transform=ax.transAxes, fontsize=12, ha='left', va='top', bbox=quadrant_style)
        ax.text(0.02, 0.02, 'Survival\\n& Secular-Rational', 
                transform=ax.transAxes, fontsize=12, ha='left', va='bottom', bbox=quadrant_style)
        ax.text(0.98, 0.98, 'Self-Expression\\n& Traditional', 
                transform=ax.transAxes, fontsize=12, ha='right', va='top', bbox=quadrant_style)
        ax.text(0.98, 0.02, 'Survival\\n& Traditional', 
                transform=ax.transAxes, fontsize=12, ha='right', va='bottom', bbox=quadrant_style)
        
        # 添加图例
        legend = ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=10, 
                           title='Cultural Regions & Languages', title_fontsize=12,
                           frameon=True, fancybox=True, shadow=True)
        legend.get_frame().set_facecolor('white')
        legend.get_frame().set_alpha(0.95)
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图片
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
    
    def _generate_corrected_interactive_map(self, entity_scores, save_path):
        """生成修正后的交互式HTML地图"""
        if not PLOTLY_AVAILABLE:
            print("⚠️ plotly未安装，跳过交互式地图生成")
            return
        # 分离数据
        ivs_data = entity_scores[entity_scores['data_source'] == 'IVS']
        multilingual_data = entity_scores[entity_scores['data_source'] == 'Multilingual']
        
        # 创建交互式图表
        fig = go.Figure()
        
        # 文化区域颜色映射
        cultural_region_colors = {
            'African-Islamic': '#cc79a7',
            'Orthodox Europe': '#0072b2', 
            'Catholic Europe': '#e69f00',
            'Latin America': '#999999',
            'West & South Asia': '#f0e442',
            'Confucian': '#d55e00',
            'Protestant Europe': '#56b4e9',
            'English-Speaking': '#009e73'
        }
        
        # 添加文化区域分组标题
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=0, color='rgba(0,0,0,0)'),
            name='<b>🌍 Cultural Regions (Real Countries)</b>',
            showlegend=True,
            hoverinfo='skip'
        ))
        
        # 添加IVS国家数据
        if len(ivs_data) > 0 and 'Cultural Region' in ivs_data.columns:
            regions = sorted(ivs_data['Cultural Region'].dropna().unique())
            
            for region in regions:
                if region in cultural_region_colors:
                    region_data = ivs_data[ivs_data['Cultural Region'] == region]
                    
                    # 创建hover文本
                    hover_text = []
                    for _, row in region_data.iterrows():
                        country_name = row.get('Country', 'Unknown')
                        if pd.isna(country_name):
                            country_name = f'Country {row.get("country_code", "Unknown")}'
                        
                        hover_text.append(
                            f'<b>{country_name}</b><br>' +
                            f'Region: {region}<br>' +
                            f'PC1 (Survival↔Self-Expression): {row["PC1_rescaled"]:.2f}<br>' +
                            f'PC2 (Traditional↔Secular): {row["PC2_rescaled"]:.2f}<br>' +
                            f'Source: Real Country (IVS)'
                        )
                    
                    fig.add_trace(go.Scatter(
                        x=region_data['PC1_rescaled'],
                        y=region_data['PC2_rescaled'],
                        mode='markers',
                        marker=dict(
                            color=cultural_region_colors[region],
                            size=12,
                            opacity=0.8,
                            line=dict(width=1, color='white'),
                            symbol='circle'
                        ),
                        name=f'  • {region} ({len(region_data)})',
                        text=hover_text,
                        hovertemplate='%{text}<extra></extra>',
                    ))
        
        # 添加多语言分组标题
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=0, color='rgba(0,0,0,0)'),
            name='<b>🌐 Multilingual LLM (Roleplay)</b>',
            showlegend=True,
            hoverinfo='skip'
        ))
        
        # 添加多语言数据 - 按模型和语言分组
        if len(multilingual_data) > 0 and 'model_name' in multilingual_data.columns and 'language' in multilingual_data.columns:
            # 获取所有模型和语言
            models = sorted(multilingual_data['model_name'].dropna().unique())
            languages = sorted(multilingual_data['language'].dropna().unique())
            
            # 模型颜色映射
            model_colors = {
                'deepseek/deepseek-chat-v3-0324': '#E74C3C',
                'google/gemini-2.0-flash-001': '#3498DB', 
                'meta-llama/llama-3.3-70b-instruct': '#9B59B6',
                'mistralai/mistral-nemo': '#F39C12',
                'openai/gpt-4o-mini': '#2ECC71',
                'qwen/qwq-32b': '#E67E22'
            }
            
            # 语言符号映射
            language_symbols = {'english': 'circle', 'native': 'diamond'}
            
            for model in models:
                model_short = model.split('/')[-1] if '/' in model else model
                model_color = model_colors.get(model, '#95A5A6')
                
                for lang in languages:
                    model_lang_data = multilingual_data[
                        (multilingual_data['model_name'] == model) & 
                        (multilingual_data['language'] == lang)
                    ]
                    
                    if len(model_lang_data) > 0:
                        # 创建hover文本
                        hover_text = []
                        for _, row in model_lang_data.iterrows():
                            country_name = row.get('country_code', 'Unknown')
                            
                            hover_text.append(
                                f'<b>{country_name}</b><br>' +
                                f'Model: {model_short}<br>' +
                                f'Language: {lang.title()}<br>' +
                                f'PC1 (Survival↔Self-Expression): {row["PC1_rescaled"]:.2f}<br>' +
                                f'PC2 (Traditional↔Secular): {row["PC2_rescaled"]:.2f}<br>' +
                                f'Source: Multilingual LLM'
                            )
                        
                        # 根据语言调整透明度
                        opacity = 0.8 if lang == 'english' else 0.6
                        size = 8 if lang == 'english' else 6
                        
                        # 改进的重复坐标处理：全局检测并添加偏移
                        coords_data = model_lang_data[['PC1_rescaled', 'PC2_rescaled']].copy()
                        
                        import numpy as np
                        
                        # 为每个数据点检查全局重复情况
                        for idx in coords_data.index:
                            current_x = round(coords_data.loc[idx, 'PC1_rescaled'], 6)
                            current_y = round(coords_data.loc[idx, 'PC2_rescaled'], 6)
                            
                            # 检查与所有多语言数据的重复情况
                            global_duplicates = multilingual_data[
                                (multilingual_data['PC1_rescaled'].round(6) == current_x) & 
                                (multilingual_data['PC2_rescaled'].round(6) == current_y)
                            ]
                            
                            if len(global_duplicates) > 1:
                                # 使用基于数据点信息的确定性偏移
                                current_row = model_lang_data.loc[idx]
                                
                                # 创建唯一标识符用于确定性偏移
                                identifier = f"{current_row['country_code']}_{current_row['model_name']}_{current_row['language']}"
                                hash_val = hash(identifier) % 1000
                                
                                # 使用更大的偏移量和圆形分布
                                offset_factor = 0.15  # 增加偏移量使点更明显分离
                                angle = (hash_val * 137.5) % 360  # 黄金角度分布
                                
                                offset_x = offset_factor * np.cos(np.radians(angle))
                                offset_y = offset_factor * np.sin(np.radians(angle))
                                
                                coords_data.loc[idx, 'PC1_rescaled'] += offset_x
                                coords_data.loc[idx, 'PC2_rescaled'] += offset_y
                        
                        fig.add_trace(go.Scatter(
                            x=coords_data['PC1_rescaled'],
                            y=coords_data['PC2_rescaled'],
                            mode='markers',
                            marker=dict(
                                color=model_color,
                                size=size,
                                opacity=opacity,
                                symbol=language_symbols.get(lang, 'circle'),
                                line=dict(width=1, color='black')
                            ),
                            name=f'  🤖 {model_short} ({lang.title()}) ({len(model_lang_data)})',
                            text=hover_text,
                            hovertemplate='%{text}<extra></extra>',
                        ))
        
        # 添加坐标轴线
        fig.add_hline(y=0, line_dash='dash', line_color='gray', opacity=0.5)
        fig.add_vline(x=0, line_dash='dash', line_color='gray', opacity=0.5)
        
        # 设置布局
        fig.update_layout(
            title=dict(
                text='<b>Cultural Values Map: Multilingual LLM Roleplay vs Real Countries</b><br>' +
                     '<sub>Inglehart-Welzel Framework • Independent Legend Control</sub>',
                x=0.5,
                font=dict(size=20)
            ),
            xaxis=dict(
                title='<b>PC1: Survival vs Self-Expression Values</b>',
                titlefont=dict(size=14),
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray'
            ),
            yaxis=dict(
                title='<b>PC2: Traditional vs Secular-Rational Values</b>',
                titlefont=dict(size=14),
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray'
            ),
            width=1500,
            height=900,
            showlegend=True,
            legend=dict(
                orientation='v',
                yanchor='top',
                y=1,
                xanchor='left',
                x=1.02,
                font=dict(size=11),
                bgcolor='rgba(255,255,255,0.95)',
                bordercolor='gray',
                borderwidth=1,
                itemsizing='constant'
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(r=300)
        )
        
        # 添加象限注释
        annotations = [
            dict(x=0.02, y=0.98, xref='paper', yref='paper',
                 text='<b>Self-Expression<br>& Secular-Rational</b>',
                 showarrow=False, font=dict(size=12), 
                 bgcolor='rgba(255,255,255,0.8)', bordercolor='gray'),
            dict(x=0.02, y=0.02, xref='paper', yref='paper',
                 text='<b>Survival<br>& Secular-Rational</b>',
                 showarrow=False, font=dict(size=12),
                 bgcolor='rgba(255,255,255,0.8)', bordercolor='gray'),
            dict(x=0.75, y=0.98, xref='paper', yref='paper',
                 text='<b>Self-Expression<br>& Traditional</b>',
                 showarrow=False, font=dict(size=12),
                 bgcolor='rgba(255,255,255,0.8)', bordercolor='gray'),
            dict(x=0.75, y=0.02, xref='paper', yref='paper',
                 text='<b>Survival<br>& Traditional</b>',
                 showarrow=False, font=dict(size=12),
                 bgcolor='rgba(255,255,255,0.8)', bordercolor='gray')
        ]
        
        fig.update_layout(annotations=annotations)
        
        # 保存HTML文件
        fig.write_html(save_path)
    
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
        """运行全面测试并完成整个分析流程"""
        try:
            print("🚀 开始全面测试 (7模型×27国家×5语言×5重复)")
            
            # 估算成本和时间 - 基于新的配置
            # 54个语言-国家组合 (5+6+8+8+27) × 7模型 × 10问题 × 5重复
            total_calls = 54 * 7 * 10 * 5  # 语言-国家组合×模型×问题×重复
            estimated_cost = total_calls * 0.01  # 估算每次调用成本
            estimated_hours = total_calls / 1000  # 估算时间（小时，考虑并发）
            
            print(f"📊 预估统计:")
            print(f"   - 语言-国家组合: 54个 (中文5+俄语6+西语8+阿语8+英文27)")
            print(f"   - 独特国家数量: 27个")
            print(f"   - 总API调用: {total_calls:,}")
            print(f"   - 预估费用: ${estimated_cost:.2f}")
            print(f"   - 预估时间: {estimated_hours:.1f}-{estimated_hours*1.2:.1f}小时 (并发执行)")
            
            confirm = input("\n确认继续? (y/N): ").strip().lower()
            if confirm != 'y':
                print("❌ 用户取消")
                return False
            
            # 运行访谈
            if self._run_multilingual_interview_with_config("comprehensive"):
                # 继续后续步骤
                return self._run_full_analysis_pipeline("comprehensive")
            else:
                return False
                
        except Exception as e:
            print(f"❌ 全面测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _run_small_scale_test_with_full_pipeline(self):
        """运行小规模测试并完成整个分析流程"""
        try:
            print("🧪 开始小规模测试 (3模型×3国家×4语言×3重复)")
            
            # 估算成本和时间 - 修正为正确的问题数量
            # 小规模: 3国家 × 4语言 = 12个语言-国家组合
            total_calls = 12 * 3 * 10 * 3  # 语言-国家组合×模型×问题×重复
            estimated_cost = total_calls * 0.01  # 估算每次调用成本
            estimated_hours = total_calls / 1000  # 估算时间（小时，考虑并发）
            
            print(f"📊 预估统计:")
            print(f"   - 语言-国家组合: 12个 (3国家 × 4语言)")
            print(f"   - 总API调用: {total_calls:,}")
            print(f"   - 预估费用: ${estimated_cost:.2f}")
            print(f"   - 预估时间: {estimated_hours:.1f}-{estimated_hours*1.2:.1f}小时 (并发执行)")
            
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
                config_path = self.project_root / "comprehensive_multilingual_config.json"
                if config_path.exists():
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                    
                    config = config_data['comprehensive_test_config']
                    
                    # 从配置中提取所有国家
                    countries = set()
                    languages = list(config['languages'].keys())
                    
                    for lang_code, lang_data in config['languages'].items():
                        for country_info in lang_data['countries']:
                            countries.add(country_info['name'])
                    
                    countries = sorted(list(countries))  # 转为排序列表
                    models = config['models']
                    repeat_count = config['repeat_count']
                    
                    print(f"✅ 从配置文件加载参数:")
                    print(f"   - 独特国家: {len(countries)}个")
                    print(f"   - 语言: {len(languages)}个 ({', '.join(languages)})")
                    print(f"   - 模型: {len(models)}个")
                    
                else:
                    print(f"⚠️ 配置文件不存在: {config_path}")
                    print(f"使用默认配置")
                    # 默认配置
                    countries = ["China", "Russian Federation (the)", "Spain", "Egypt"]
                    models = ["openai/gpt-4o-mini", "google/gemini-2.0-flash-001", "anthropic/claude-3.7-sonnet", 
                             "deepseek/deepseek-chat-v3-0324", "qwen/qwq-32b", "meta-llama/llama-3.3-70b-instruct", 
                             "mistralai/mistral-nemo"]
                    languages = ["zh-cn", "ru", "es", "ar", "en"]
                    repeat_count = 5
                    
            elif config_type == "small_scale":
                # 小规模测试使用简化配置
                countries = ["China", "Russian Federation (the)", "Spain"]
                models = ["openai/gpt-4o-mini", "deepseek/deepseek-chat-v3-0324", "google/gemini-2.0-flash-001"]
                languages = ["zh-cn", "ru", "es", "en"]
                repeat_count = 3
            else:
                print(f"❌ 未知配置类型: {config_type}")
                return False
            
            print(f"🎯 访谈配置:")
            print(f"   - 国家: {len(countries)} 个")
            print(f"   - 模型: {len(models)} 个")
            print(f"   - 语言: {len(languages)} 个")
            print(f"   - 重复次数: {repeat_count}")
            
            # 创建访谈器
            interviewer = MultilingualRoleplayInterview()
            
            # 生成任务列表
            tasks = []
            for country in countries:
                for language in languages:
                    for model in models:
                        tasks.append((model, country, language))
            
            print(f"📋 总任务数: {len(tasks)}")
            
            # 运行访谈
            results = interviewer.run_multilingual_experiment(
                models=models, 
                max_workers=4, 
                repeat_count=repeat_count,
                test_type=config_type
            )
            
            if results:
                print("✅ 访谈完成")
                return True
            else:
                print("❌ 访谈失败")
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
    
    print("🌐 Roleplay Multilingual Analysis Runner")
    print("=" * 60)
    
    print("请选择运行模式:")
    print("  1. 全面测试 (7模型×27国家×5语言×5重复) - 完整流程")
    print("  2. 小规模测试 (3模型×3国家×4语言×3重复) - 快速验证")
    print("  3. 处理现有数据 (跳过访谈，直接处理→PCA→可视化)")
    
    try:
        choice = input("\n请输入选择 (1-3): ").strip()
        
        # 创建分析运行器
        runner = RoleplayMultilingualAnalysisRunner()
        success = False
        
        if choice == "1":
            print("\n🚀 执行全面测试...")
            success = runner._run_comprehensive_test_with_full_pipeline()
            
        elif choice == "2":
            print("\n🧪 执行小规模测试...")
            success = runner._run_small_scale_test_with_full_pipeline()
            
        elif choice == "3":
            print("\n📊 处理现有数据...")
            success = runner._run_data_processing_pipeline()
            
        else:
            print("❌ 无效选择")
            return 1
        
        if success:
            print("\n🎊 选择的分析步骤成功完成!")
            return 0
        else:
            print("\n⚠️ 分析步骤失败，请检查错误信息")
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
