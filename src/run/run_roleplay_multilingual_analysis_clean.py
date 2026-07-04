#!/usr/bin/env python3
"""
完整的Roleplay Multilingual分析运行脚本
从多语言角色扮演回答数据处理到PCA分析再到可视化的完整流程

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
from typing import Dict, Any
from dataclasses import asdict, is_dataclass

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# 导入所需模块
from src.roleplay_multilingual.multilingual_roleplay_data_processor import MultilingualRoleplayDataProcessor
from src.roleplay_multilingual.multilingual_roleplay_pca_analysis import MultilingualRoleplayPCAAnalysis
from src.roleplay_multilingual.multilingual_roleplay_visualization import MultilingualRoleplayVisualizer


def convert_to_serializable(obj):
    """将对象转换为可JSON序列化的格式"""
    if is_dataclass(obj):
        return asdict(obj)
    elif isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_serializable(item) for item in obj]
    else:
        return obj


class RoleplayMultilingualAnalysisRunner:
    """Roleplay Multilingual完整分析运行器"""
    
    def __init__(self, project_root=None):
        """初始化运行器"""
        if project_root is None:
            self.project_root = Path(__file__).parent.parent.parent
        else:
            self.project_root = Path(project_root)
        
        # 设置路径
        self.data_path = self.project_root / "data" / "llm_interviews" / "multilingual"
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
    
    # ==================== 配置读取函数 ====================
    
    def _get_config_stats(self):
        """读取配置文件，获取模型、国家、语言等统计信息"""
        stats = {
            'total_models': 0,
            'total_countries': 0,
            'total_languages': 0,
            'language_country_pairs': 0,
            'english_only_countries': 0,
            'bilingual_countries': 0,
            'models_list': [],
            'consensus_count': 5
        }
        
        try:
            # 读取模型配置
            models_config_file = self.project_root / "config" / "models" / "llm_models.json"
            if models_config_file.exists():
                with open(models_config_file, 'r', encoding='utf-8') as f:
                    models_config = json.load(f)
                    stats['total_models'] = len(models_config.get('models', {}))
                    stats['models_list'] = list(models_config.get('models', {}).keys())
            
            # 读取多语言配置
            multilingual_config_file = self.project_root / "config" / "questions" / "multilingual" / "multilingual_questions_complete.json"
            if multilingual_config_file.exists():
                with open(multilingual_config_file, 'r', encoding='utf-8') as f:
                    multilingual_config = json.load(f)
                    
                    # 统计语言
                    languages = multilingual_config.get('languages', {})
                    stats['total_languages'] = len(languages)
                    
                    # 统计国家和语言-国家对
                    countries_set = set()
                    language_country_pairs = 0
                    english_only = 0
                    bilingual = 0
                    
                    for lang_code, lang_info in languages.items():
                        lang_countries = lang_info.get('countries', [])
                        countries_set.update(lang_countries)
                        language_country_pairs += len(lang_countries)
                    
                    stats['total_countries'] = len(countries_set)
                    stats['language_country_pairs'] = language_country_pairs
                    
                    # 统计英语母语国家和双语国家
                    # 英语母语国家：只在en中出现
                    # 双语国家：在en和其他语言中都出现
                    en_countries = set(languages.get('en', {}).get('countries', []))
                    other_countries = set()
                    for lang_code, lang_info in languages.items():
                        if lang_code != 'en':
                            other_countries.update(lang_info.get('countries', []))
                    
                    stats['english_only_countries'] = len(en_countries - other_countries)
                    stats['bilingual_countries'] = len(en_countries & other_countries)
            
            # 尝试读取comprehensive配置中的共识轮数
            comprehensive_config_file = self.project_root / "config" / "questions" / "multilingual" / "comprehensive_multilingual_config.json"
            if comprehensive_config_file.exists():
                with open(comprehensive_config_file, 'r', encoding='utf-8') as f:
                    comprehensive_config = json.load(f)
                    stats['consensus_count'] = comprehensive_config.get('comprehensive_test_config', {}).get('repeat_count', 5)
        
        except Exception as e:
            print(f"⚠️ 读取配置文件时出错: {e}")
        
        return stats
    
    # ==================== 核心流程函数 ====================
    
    def step0_multilingual_interview(self):
        """步骤0: 多语言角色扮演访谈"""
        print("\n" + "="*60)
        print("🎤 步骤0: 多语言角色扮演访谈")
        print("="*60)
        
        try:
            # 导入多语言访谈模块
            from src.roleplay_multilingual.multilingual_roleplay_interview import MultilingualRoleplayInterview
            
            # 初始化访谈器
            interviewer = MultilingualRoleplayInterview(consensus_count=2, data_path=str(self.data_path))
            
            # 检查是否已有访谈数据
            existing_files = list(self.data_path.glob("interview_data_*.json"))
            if existing_files:
                latest_file = max(existing_files, key=lambda x: x.stat().st_mtime)
                print(f"✅ 发现已有访谈数据: {latest_file}")
                
                # 询问用户是否使用现有数据
                print("\n请选择:")
                print("1. 使用现有数据")
                print("2. 重新进行访谈")
                
                # 动态显示全面测试规模
                config_stats = self._get_config_stats()
                print(f"3. 运行全面测试（{config_stats['total_countries']}国家×{config_stats['total_models']}模型×{config_stats['consensus_count']}轮）")
                
                choice = input("\n请输入选项 (1/2/3): ").strip()
                
                if choice == '1':
                    print("✅ 使用现有访谈数据")
                    return True
                elif choice == '3':
                    print("🚀 开始全面测试...")
                    return self._run_comprehensive_test()
            
            # 加载推荐国家列表
            config_file = self.project_root / "config" / "questions" / "multilingual" / "multilingual_questions_complete.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                recommended_countries = config.get('recommended_countries', [])
            else:
                recommended_countries = []
            
            # 运行访谈
            print(f"\n🎯 推荐访谈国家: {len(recommended_countries)}个")
            
            # 获取所有模型
            models_config_file = self.project_root / "config" / "models" / "llm_models.json"
            with open(models_config_file, 'r', encoding='utf-8') as f:
                models_config = json.load(f)
            model_names = list(models_config.get('models', {}).keys())
            
            # 转换为entities格式: "country_language"
            entities = []
            for country_info in recommended_countries:
                country = country_info.get('country')
                languages = country_info.get('languages', [])
                for lang in languages:
                    entities.append(f"{country}_{lang}")
            
            print(f"📊 任务统计: {len(model_names)}个模型 × {len(entities)}个语言-国家对")
            
            results = interviewer.batch_interview(
                model_names=model_names,
                entities=entities,
                max_workers=4
            )
            
            if not results or results.get('successful_tasks', 0) == 0:
                print("⚠️ 并发访谈失败，尝试单线程模式...")
                results = interviewer.batch_interview(
                    model_names=model_names,
                    entities=entities,
                    max_workers=1
                )
            
            # 保存结果
            if results:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = self.data_path / f"interview_data_{timestamp}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(convert_to_serializable(results), f, indent=2, ensure_ascii=False)
                print(f"✅ 访谈结果已保存: {output_file}")
                return True
            else:
                print("❌ 访谈失败")
                return False
                
        except Exception as e:
            print(f"❌ 多语言访谈失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def step1_data_processing(self, test_type: str = None):
        """步骤1: 多语言Roleplay数据处理"""
        print("\n" + "="*60)
        print("📊 步骤1: 多语言Roleplay数据处理")
        print("="*60)
        
        try:
            # 初始化数据处理器
            data_root = str(self.project_root / "data")
            processor = MultilingualRoleplayDataProcessor(data_path=data_root)
            
            # 查找最新的访谈数据文件（优先使用新格式）
            interview_files = list(self.data_path.glob("interview_data_*.json"))
            results_file = None
            
            if interview_files:
                latest_interview = max(interview_files, key=lambda x: x.stat().st_mtime)
                print(f"✅ 发现最新访谈数据: {latest_interview.name}")
                results_file = str(latest_interview)
            else:
                print("⚠️ 未找到新的访谈数据，将使用旧数据")
            
            # 查找最新的处理后数据（在processed子目录中）
            processed_dir = self.data_path / "processed"
            processed_files = list(processed_dir.glob("llm_roleplay_ml_processed_responses_ivs_format_*.pkl")) if processed_dir.exists() else []
            if processed_files:
                latest_file = max(processed_files, key=lambda x: x.stat().st_mtime)
                print(f"✅ 发现已处理数据: {latest_file.name}")
                
                choice = input("\n是否重新处理数据? (y/n): ").strip().lower()
                if choice != 'y':
                    print("✅ 使用现有处理数据")
                    return True
            
            # 处理数据（指定使用最新的访谈数据文件）
            print("\n开始处理多语言Roleplay数据...")
            processor.process_multilingual_data(results_file=results_file)
            
            print(f"\n✅ 多语言Roleplay数据处理完成！")
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
            
            # 查找最新的处理后数据文件
            processed_files = list(self.data_path.glob("llm_roleplay_ml_processed_responses_ivs_format_*.pkl"))
            if not processed_files:
                print(f"❌ 未找到处理后的数据文件")
                print(f"请先运行步骤1进行数据处理")
                return False
            
            latest_processed_file = max(processed_files, key=lambda x: x.stat().st_mtime)
            print(f"📁 使用最新处理文件: {latest_processed_file.name}")
            
            # 使用多语言PCA分析器
            print("\n1️⃣ 初始化多语言PCA分析器...")
            analyzer = MultilingualRoleplayPCAAnalysis(
                data_path=str(self.project_root / "data")
            )
            
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
            
            return True
            
        except Exception as e:
            print(f"❌ 多语言+IVS联合PCA分析失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def step3_language_comparison_analysis(self, test_type: str = None):
        """步骤3: 语言对比分析（使用可视化器模块）"""
        print("\n" + "="*60)
        print("🌐 步骤3: 语言对比分析")
        print("="*60)
        
        try:
            # 使用可视化器创建完整的分析套件
            print("\n1️⃣ 初始化可视化器...")
            visualizer = MultilingualRoleplayVisualizer(
                data_path=str(self.project_root / "data"),
                results_path=str(self.results_path)
            )
            
            # 创建完整的可视化套件
            print("\n2️⃣ 创建完整的可视化套件...")
            result = visualizer.create_complete_visualization_suite()
            
            print(f"\n✅ 语言对比分析完成！")
            print(f"\n📊 生成的可视化文件:")
            for key, path in result.items():
                print(f"   - {key}: {Path(path).name}")
            
            # 打印索引页面路径
            if 'index_file' in result:
                print(f"\n🌐 打开主页面查看结果:")
                print(f"   {result['index_file']}")
            
            return True
            
        except Exception as e:
            print(f"❌ 语言对比分析失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def step4_visualization(self, test_type: str = None):
        """步骤4: 综合可视化"""
        print("\n" + "="*60)
        print("🎨 步骤4: 综合可视化")
        print("="*60)
        
        # 创建dashboard目录
        dashboard_path = self.results_path / "roleplay_ml_dashboard"
        dashboard_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 可视化保存到: {dashboard_path}")
        
        try:
            # 查找最新的PCA结果文件
            latest_file = self.data_path / "roleplay_ml_pca_entity_scores_latest.pkl"
            if latest_file.exists():
                entity_scores_path = latest_file
                print(f"📁 使用最新PCA文件: {entity_scores_path.name}")
            else:
                pca_files = list(self.data_path.glob("roleplay_ml_pca_entity_scores_*.pkl"))
                if not pca_files:
                    print(f"❌ 未找到PCA结果文件")
                    print(f"请先运行步骤2进行PCA分析")
                    return False
                
                entity_scores_path = max(pca_files, key=lambda x: x.stat().st_mtime)
                print(f"📁 使用最新PCA文件: {entity_scores_path.name}")
            
            # 显示文件时间
            file_time = datetime.fromtimestamp(entity_scores_path.stat().st_mtime)
            print(f"   文件时间: {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 加载数据
            print("\n1️⃣ 加载实体分数数据...")
            entity_scores = pd.read_pickle(entity_scores_path)
            print(f"✅ 成功加载实体分数数据: {len(entity_scores)} 个实体")
            
            # 使用可视化器创建完整的可视化套件（包含所有地图和图表）
            print("\n2️⃣ 使用可视化器创建完整套件...")
            visualizer = MultilingualRoleplayVisualizer(
                data_path=str(self.project_root / "data"),
                results_path=str(self.results_path)
            )
            
            # 创建完整的可视化套件（包含所有图表和地图，已包含IVS聚合修复）
            viz_result = visualizer.create_complete_visualization_suite()
            
            print(f"\n✅ 可视化套件创建完成！")
            print(f"📊 生成的文件:")
            for key, path in viz_result.items():
                print(f"   - {key}: {Path(path).name}")
            
            return True
            
        except Exception as e:
            print(f"❌ 可视化失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # ==================== 主流程控制函数 ====================
    
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
        
        # 步骤3: 语言对比分析
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
    
    # ==================== 测试流程函数 ====================
    
    def _run_comprehensive_test_with_full_pipeline(self):
        """使用配置文件运行测试并完成整个分析流程"""
        try:
            # 使用comprehensive_multilingual_config.json配置
            config_file = self.project_root / "config" / "questions" / "multilingual" / "comprehensive_multilingual_config.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                test_config = config.get('comprehensive_test_config', {})
                task_calc = test_config.get('task_calculation', {})
                language_country_pairs = task_calc.get('total_language_country_pairs', 59)
                total_countries = task_calc.get('total_countries', 32)
                total_models = task_calc.get('total_models', 7)
                repeat_count = test_config.get('repeat_count', 5)
            else:
                # 默认值（完整测试）
                language_country_pairs = 59
                total_countries = 32
                total_models = 7
                repeat_count = 5
            
            config_stats = self._get_config_stats()
            print(f"🚀 开始完整测试 ({config_stats['total_countries']}国家×{config_stats['total_models']}模型×{config_stats['consensus_count']}轮)")
            print(f"   - {config_stats['bilingual_countries']}个非英语国家（各自母语+英语）")
            print(f"   - {config_stats['english_only_countries']}个英语母语国家（仅英语）")
            
            questions_per_interview = 10
            total_questions = language_country_pairs * total_models * repeat_count * questions_per_interview
            
            print(f"\n📊 任务统计:")
            print(f"   语言-国家对: {language_country_pairs}")
            print(f"   模型数: {total_models}")
            print(f"   共识轮数: {repeat_count}")
            print(f"   每次访谈问题数: {questions_per_interview}")
            print(f"   总问题数: {total_questions:,}")
            
            # 运行访谈
            if self._run_multilingual_interview_with_config('comprehensive'):
                print("\n✅ 全面测试访谈完成，开始运行分析流程...")
                return self._run_full_analysis_pipeline()
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
            print("🧪 开始小规模测试 (3模型×5国家×各语言组合×3重复)")
            print("   - 模型：GPT-4o-mini, DeepSeek, Gemini")
            print("   - 国家：Egypt, China, Mexico, Russia, USA")
            
            # 运行访谈
            if self._run_multilingual_interview_with_config('small_scale'):
                print("\n✅ 小规模测试访谈完成，开始运行分析流程...")
                return self._run_full_analysis_pipeline('small_scale')
            else:
                return False
                
        except Exception as e:
            print(f"❌ 小规模测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _run_incremental_languages_with_full_pipeline(self):
        """增量访谈：根据配置补齐缺失语言/国家"""
        try:
            print("🆕 开始增量访谈（仅补齐缺失的国家/语言）")
            
            # 加载配置文件
            config_file = self.project_root / "config" / "questions" / "multilingual" / "multilingual_questions_complete.json"
            if not config_file.exists():
                print(f"❌ 配置文件不存在: {config_file}")
                return False
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 获取所有应该访谈的国家-语言对
            all_pairs = set()
            for country_info in config.get('recommended_countries', []):
                country = country_info.get('country')
                languages = country_info.get('languages', [])
                for lang in languages:
                    all_pairs.add((country, lang))
            
            print(f"📋 配置文件中定义的国家-语言对: {len(all_pairs)}")
            
            # 获取已完成的国家-语言对
            latest_file = self._get_latest_roleplay_results_file()
            if latest_file:
                completed_pairs = self._extract_completed_pairs_from_file(latest_file)
                print(f"✅ 已完成的国家-语言对: {len(completed_pairs)}")
            else:
                completed_pairs = set()
                print("⚠️ 未找到已有访谈数据")
            
            # 计算缺失的对
            missing_pairs = all_pairs - completed_pairs
            
            if not missing_pairs:
                print("✅ 所有国家-语言对都已完成，无需增量访谈")
                print("\n✅ 直接运行分析流程...")
                return self._run_full_analysis_pipeline()
            
            print(f"\n🎯 需要补齐的国家-语言对: {len(missing_pairs)}")
            
            # 运行增量访谈
            from src.roleplay_multilingual.multilingual_roleplay_interview import MultilingualRoleplayInterview
            interviewer = MultilingualRoleplayInterview(consensus_count=5, data_path=str(self.data_path))
            
            # 构建增量访谈的国家列表
            incremental_countries = []
            for country, lang in missing_pairs:
                incremental_countries.append({
                    'country': country,
                    'languages': [lang]
                })
            
            # 获取所有模型
            models_config_file = self.project_root / "config" / "models" / "llm_models.json"
            with open(models_config_file, 'r', encoding='utf-8') as f:
                models_config = json.load(f)
            model_names = list(models_config.get('models', {}).keys())
            
            # 转换为entities格式
            entities = []
            for country_info in incremental_countries:
                country = country_info.get('country')
                languages = country_info.get('languages', [])
                for lang in languages:
                    entities.append(f"{country}_{lang}")
            
            # 运行访谈
            results = interviewer.batch_interview(
                model_names=model_names,
                entities=entities,
                max_workers=4
            )
            
            if results:
                # 保存结果
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = self.data_path / f"interview_data_incremental_{timestamp}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(convert_to_serializable(results), f, indent=2, ensure_ascii=False)
                print(f"✅ 增量访谈结果已保存: {output_file}")
                
                print("\n✅ 所有缺失模型的增量访谈已完成，开始运行分析流程...")
                return self._run_full_analysis_pipeline()
            else:
                print("❌ 增量访谈失败")
                return False
        
        except Exception as e:
            print(f"❌ 增量访谈流程失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _run_chinese_variant_test_with_full_pipeline(self):
        """运行中文变体测试（繁体vs简体）"""
        try:
            print("🔬 开始中文变体测试（繁体中文 vs 简体中文）")
            print("   - 测试地区：香港(zh-hk)、台湾(zh-tw)、澳门(zh-hk)")
            print("   - 对比基准：大陆简体中文(zh-cn)")
            print("   - 7个模型，共识轮数: 5轮")
            
            # 定义中文变体测试的国家列表
            chinese_variants = [
                {'country': 'Hong Kong', 'languages': ['zh-hk']},
                {'country': 'Taiwan', 'languages': ['zh-tw']},
                {'country': 'Macau', 'languages': ['zh-hk']}
            ]
            
            # 运行访谈
            from src.roleplay_multilingual.multilingual_roleplay_interview import MultilingualRoleplayInterview
            interviewer = MultilingualRoleplayInterview(consensus_count=5, data_path=str(self.data_path))
            
            # 获取所有模型
            models_config_file = self.project_root / "config" / "models" / "llm_models.json"
            with open(models_config_file, 'r', encoding='utf-8') as f:
                models_config = json.load(f)
            model_names = list(models_config.get('models', {}).keys())
            
            # 转换为entities格式
            entities = []
            for country_info in chinese_variants:
                country = country_info.get('country')
                languages = country_info.get('languages', [])
                for lang in languages:
                    entities.append(f"{country}_{lang}")
            
            results = interviewer.batch_interview(
                model_names=model_names,
                entities=entities,
                max_workers=4
            )
            
            if results:
                # 保存结果
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = self.data_path / f"interview_data_chinese_variants_{timestamp}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(convert_to_serializable(results), f, indent=2, ensure_ascii=False)
                print(f"✅ 中文变体测试结果已保存: {output_file}")
                
                print("\n✅ 中文变体测试完成，开始运行完整分析流程...")
                return self._run_full_analysis_pipeline('chinese_variants')
            else:
                print("❌ 中文变体测试失败")
                return False
            
        except Exception as e:
            print(f"❌ 中文变体测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # ==================== 辅助流程函数 ====================
    
    def _run_data_processing_pipeline(self):
        """运行数据处理流程（跳过访谈）"""
        try:
            print("📊 开始数据处理流程...")
            return self._run_full_analysis_pipeline()
        except Exception as e:
            print(f"❌ 数据处理流程失败: {e}")
            return False
    
    def _run_multilingual_interview_with_config(self, config_type: str):
        """使用配置文件运行多语言访谈"""
        try:
            from src.roleplay_multilingual.multilingual_roleplay_interview import MultilingualRoleplayInterview
            
            # 加载配置
            if config_type == 'comprehensive':
                config_file = self.project_root / "config" / "questions" / "multilingual" / "comprehensive_multilingual_config.json"
                consensus_count = 5
            elif config_type == 'small_scale':
                config_file = self.project_root / "config" / "small_scale_test_config.json"
                consensus_count = 3
            else:
                print(f"❌ 未知的配置类型: {config_type}")
                return False
            
            if not config_file.exists():
                print(f"❌ 配置文件不存在: {config_file}")
                return False
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 获取国家列表
            if config_type == 'comprehensive':
                country_list = config.get('comprehensive_test_config', {}).get('countries', [])
            elif config_type == 'small_scale':
                country_list = config.get('small_scale_test', {}).get('countries', [])
            
            print(f"📋 配置文件: {config_file.name}")
            print(f"🌍 国家数量: {len(country_list)}")
            print(f"🔄 共识轮数: {consensus_count}")
            
            # 初始化访谈器
            interviewer = MultilingualRoleplayInterview(
                consensus_count=consensus_count,
                data_path=str(self.data_path)
            )
            
            # 获取模型列表
            if config_type == 'small_scale':
                # 小规模测试使用配置中指定的模型
                model_names = config.get('small_scale_test', {}).get('models', [])
            else:
                # 全面测试使用所有模型
                models_config_file = self.project_root / "config" / "models" / "llm_models.json"
                with open(models_config_file, 'r', encoding='utf-8') as f:
                    models_config = json.load(f)
                model_names = list(models_config.get('models', {}).keys())
            
            # 转换为entities格式
            entities = []
            for country_info in country_list:
                country = country_info.get('country')
                languages = country_info.get('languages', [])
                for lang in languages:
                    entities.append(f"{country}_{lang}")
            
            print(f"📊 任务统计: {len(model_names)}个模型 × {len(entities)}个语言-国家对 = {len(model_names) * len(entities)}个任务")
            
            # 运行访谈
            print("\n🚀 开始批量访谈...")
            results = interviewer.batch_interview(
                model_names=model_names,
                entities=entities,
                max_workers=4
            )
            
            if not results or results.get('successful_tasks', 0) == 0:
                print("⚠️ 并发访谈失败，尝试单线程模式...")
                results = interviewer.batch_interview(
                    model_names=model_names,
                    entities=entities,
                    max_workers=1
                )
            
            if results:
                # 保存结果
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = self.data_path / f"interview_data_{config_type}_{timestamp}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(convert_to_serializable(results), f, indent=2, ensure_ascii=False)
                print(f"✅ 访谈结果已保存: {output_file}")
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
        """运行完整分析流程（数据处理 → PCA → 可视化）"""
        try:
            print("\n" + "="*60)
            print("🔄 开始完整分析流程（数据处理 → PCA → 可视化）")
            print("="*60)
            
            # 步骤1: 数据处理
            if not self.step1_data_processing(test_type):
                return False
            
            # 步骤2: PCA分析
            if not self.step2_pca_analysis(test_type):
                return False
            
            # 步骤3: 语言对比分析
            self.step3_language_comparison_analysis(test_type)
            
            # 步骤4: 可视化
            self.step4_visualization(test_type)
            
            print("\n✅ 完整分析流程成功完成！")
            return True
            
        except Exception as e:
            print(f"❌ 分析流程失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # ==================== 工具函数 ====================
    
    def _get_latest_roleplay_results_file(self):
        """获取最新的roleplay结果文件"""
        # 查找interview_data文件
        interview_files = list(self.data_path.glob("interview_data_*.json"))
        if interview_files:
            return max(interview_files, key=lambda x: x.stat().st_mtime)
        return None
    
    def _extract_completed_pairs_from_file(self, file_path: Path):
        """从文件中提取已完成的国家-语言对"""
        completed_pairs = set()
        
        try:
            # 读取文件
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
        
        # 提取国家-语言对
        if isinstance(data, dict):
            for country, country_data in data.items():
                if isinstance(country_data, dict):
                    for language in country_data.keys():
                        completed_pairs.add((country, language))
        
        return completed_pairs
    
    def _run_comprehensive_test(self) -> bool:
        """运行全面测试（旧版，保留用于兼容）"""
        try:
            from src.roleplay_multilingual.multilingual_roleplay_interview import MultilingualRoleplayInterview
            
            # 加载配置
            config_file = self.project_root / "config" / "questions" / "multilingual" / "comprehensive_multilingual_config.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                country_list = config.get('comprehensive_test_config', {}).get('countries', [])
            else:
                print("❌ 未找到comprehensive_multilingual_config.json")
                return False
            
            # 获取所有模型
            models_config_file = self.project_root / "config" / "models" / "llm_models.json"
            with open(models_config_file, 'r', encoding='utf-8') as f:
                models_config = json.load(f)
            model_names = list(models_config.get('models', {}).keys())
            
            # 转换为entities格式
            entities = []
            for country_info in country_list:
                country = country_info.get('country')
                languages = country_info.get('languages', [])
                for lang in languages:
                    entities.append(f"{country}_{lang}")
            
            # 运行访谈
            interviewer = MultilingualRoleplayInterview(consensus_count=5, data_path=str(self.data_path))
            results = interviewer.batch_interview(
                model_names=model_names,
                entities=entities,
                max_workers=4
            )
            
            if results:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = self.data_path / f"interview_data_comprehensive_{timestamp}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(convert_to_serializable(results), f, indent=2, ensure_ascii=False)
                print(f"✅ 全面测试结果已保存: {output_file}")
                return True
            else:
                print("❌ 全面测试失败")
                return False
                
        except Exception as e:
            print(f"❌ 全面测试执行失败: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """主函数"""
    
    print("\n" + "="*70)
    print("🌐 Stage3: Roleplay Multilingual 分析系统")
    print("="*70)
    
    # 创建临时runner实例以读取配置
    temp_runner = RoleplayMultilingualAnalysisRunner()
    config_stats = temp_runner._get_config_stats()
    
    print("\n请选择要执行的操作：")
    print(f"\n1️⃣  重新全部访谈 ({config_stats['total_countries']}国家×{config_stats['total_models']}模型×{config_stats['consensus_count']}轮，完整测试)")
    print(f"     • {config_stats['bilingual_countries']}个非英语国家（各自母语+英语）")
    print(f"     • {config_stats['english_only_countries']}个英语母语国家（仅英语）")
    print(f"     • {config_stats['total_models']}个模型，共识轮数: {config_stats['consensus_count']}轮")
    print(f"     • 总计: {config_stats['language_country_pairs']}个语言-国家对")
    print("\n2️⃣  测试小规模访谈 (3模型×5国家×各语言组合，快速验证)")
    print("     • 模型：GPT-4o-mini, DeepSeek, Gemini")
    print("     • 国家：Egypt(阿拉伯语+英语), China(中文+英语), Mexico(西班牙语+英语),")
    print("            Russia(俄语+英语), USA(英语)")
    print("     • 共识轮数: 3轮")
    print("\n3️⃣  只分析现有数据 (数据处理 → PCA → 可视化)")
    print(f"\n4️⃣  【他者理论验证】测试中文变体 (繁体中文 vs 简体中文)")
    print("     • 测试地区：香港(zh-hk繁体)、台湾(zh-tw繁体)、澳门(zh-hk繁体)")
    print(f"     • {config_stats['total_models']}个模型，共识轮数: {config_stats['consensus_count']}轮")
    print("     • 完成后合并到现有数据并重新分析")
    print("\n5️⃣  增量访谈：根据配置补齐缺失语言/国家")
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
                choice = input("\n请输入选项 (0-5): ").strip()
                
                if choice == '0':
                    print("👋 退出程序")
                    return 0
                elif choice in ['1', '2', '3', '4', '5']:
                    break
                else:
                    print("❌ 无效选项，请输入 0-5")
            except (KeyboardInterrupt, EOFError):
                print("\n\n👋 用户取消，退出程序")
                return 0
        
        success = False
        
        # 处理选项1: 重新全部访谈
        if choice == '1':
            config_stats = runner._get_config_stats()
            print(f"\n🚀 选项1: 重新全部访谈（{config_stats['total_countries']}国家×{config_stats['total_models']}模型×{config_stats['consensus_count']}轮）")
            print(f"\n📊 预计任务量:")
            print(f"   • 语言-国家对: {config_stats['language_country_pairs']}")
            print(f"   • 模型数: {config_stats['total_models']}")
            print(f"   • 共识轮数: {config_stats['consensus_count']}")
            questions_per_interview = 10
            total_questions = config_stats['language_country_pairs'] * config_stats['total_models'] * config_stats['consensus_count'] * questions_per_interview
            print(f"   • 总问题数: {total_questions:,}")
            confirm = input("\n确认执行? (y/n): ").strip().lower()
            if confirm != 'y':
                print("❌ 已取消")
                return 0
            success = runner._run_comprehensive_test_with_full_pipeline()
        
        # 处理选项2: 测试小规模访谈
        elif choice == '2':
            print("\n🧪 选项2: 测试小规模访谈")
            confirm = input("\n确认执行? (y/n): ").strip().lower()
            if confirm != 'y':
                print("❌ 已取消")
                return 0
            success = runner._run_small_scale_test_with_full_pipeline()
        
        # 处理选项3: 只分析现有数据
        elif choice == '3':
            print("\n📊 选项3: 只分析现有数据")
            confirm = input("\n确认执行? (y/n): ").strip().lower()
            if confirm != 'y':
                print("❌ 已取消")
                return 0
            success = runner._run_data_processing_pipeline()
        
        # 处理选项4: 中文变体测试
        elif choice == '4':
            print("\n🔬 选项4: 【他者理论验证】测试中文变体")
            confirm = input("\n确认执行? (y/n): ").strip().lower()
            if confirm != 'y':
                print("❌ 已取消")
                return 0
            success = runner._run_chinese_variant_test_with_full_pipeline()
        
        # 处理选项5: 增量访谈
        elif choice == '5':
            print("\n🆕 选项5: 增量访谈（仅补齐缺失的国家/语言）")
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
