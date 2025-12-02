#!/usr/bin/env python3
"""
完整的Roleplay English分析运行脚本
包含访谈功能和数据分析可视化

功能模块：
1. 访谈功能：支持109个国家，7个模型的角色扮演访谈
2. 数据处理：处理访谈结果为IVS格式
3. PCA分析：进行主成分分析
4. 可视化：生成文化地图和分析图表

数据存储规则：
- 访谈原始数据 -> data/roleplay_English/llm_responses_roleplay/
- 处理后数据和PCA计算结果 -> data/roleplay_English/
- 输出图片和文化坐标数据 -> results/roleplay_English/
"""

import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
import json
import time

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# 导入所需模块
from src.roleplay_English.llm_country_roleplay_interview import LLMCountryRoleplayInterview
from src.roleplay_English.llm_country_roleplay_data_processor import LLMCountryRoleplayDataProcessor
from src.roleplay_English.llm_country_roleplay_pca_analysis import LLMCountryRoleplayPCAAnalyzer
from src.roleplay_English.llm_country_roleplay_visualization import LLMCountryRoleplayVisualizer


class RoleplayEnglishAnalysisRunner:
    """Roleplay English完整分析运行器"""
    
    def __init__(self, project_root=None):
        if project_root is None:
            self.project_root = Path(__file__).parent.parent.parent
        else:
            self.project_root = Path(project_root)
        
        # 设置路径
        self.data_path = self.project_root / "data" / "roleplay_English"
        self.results_path = self.project_root / "results" / "roleplay_English"
        self.roleplay_responses_path = self.data_path / "llm_responses_roleplay"
        self.config_path = self.project_root / "config"
        
        # 确保目录存在
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.results_path.mkdir(parents=True, exist_ok=True)
        self.roleplay_responses_path.mkdir(parents=True, exist_ok=True)
        
        # 加载配置数据
        self.cultural_regions = self._load_cultural_regions()
        self.available_models = self._get_available_models()
        
        print(f"🏠 项目根目录: {self.project_root}")
        print(f"📁 Roleplay数据目录: {self.data_path}")
        print(f"📁 结果目录: {self.results_path}")
        print(f"📁 Roleplay回答目录: {self.roleplay_responses_path}")
        print(f"🤖 可用模型: {len(self.available_models)} 个")
        print(f"🌍 文化区域: {len(self.cultural_regions)} 个")
    
    def _load_cultural_regions(self):
        """加载文化区域配置"""
        try:
            cultural_regions_path = self.config_path / "cultural_regions.json"
            with open(cultural_regions_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('cultural_regions', {})
        except Exception as e:
            print(f"警告: 加载文化区域配置失败: {e}")
            return {}
    
    def _get_available_models(self):
        """获取可用的模型列表"""
        try:
            # 创建临时访谈对象获取可用模型
            temp_interview = LLMCountryRoleplayInterview(data_path=str(self.project_root / "data"))
            available_models = [name for name in temp_interview.model_configs.keys() 
                              if name in temp_interview.api_keys]
            return available_models
        except Exception as e:
            print(f"警告: 获取可用模型失败: {e}")
            return []
    
    def _get_test_countries_by_region(self):
        """获取每个文化区域的测试国家（每个区域1个国家）"""
        test_countries_by_region = {
            "African-Islamic": "Egypt",
            "Confucian": "China", 
            "Latin America": "Brazil",
            "Protestant Europe": "Germany",
            "Catholic Europe": "France",
            "English-Speaking": "United States",
            "Orthodox Europe": "Russian Federation",
            "West & South Asia": "India"
        }
        return test_countries_by_region
    
    def _get_stage3_test_countries(self):
        """获取Stage 3使用的测试国家（新提示词测试）
        
        注意：
        1. 使用Stage 2的国家名称格式（与cultural_regions.json一致）
        2. 小规模测试：3个国家，重复3次
        """
        # 小规模测试：3个国家（2个非英语 + 1个英语母语）
        test_countries = [
            "China",
            "Spain",
            "United States"
            # 完整测试时改为10个国家：
            # "China", "Singapore",
            # "Russian Federation",
            # "Mexico", "Argentina",
            # "Spain",
            # "Egypt", "Morocco",
            # "United States", "United Kingdom"
        ]
        
        return test_countries
    
    def _get_all_countries(self):
        """获取所有109个国家"""
        all_countries = []
        for region_data in self.cultural_regions.values():
            all_countries.extend(region_data.get('countries', []))
        return sorted(list(set(all_countries)))
    
    def _analyze_roleplay_data(self, data: pd.DataFrame) -> dict:
        """分析角色扮演数据"""
        try:
            analysis = {
                'total_entities': len(data),
                'data_sources': {},
                'models': {},
                'cultural_regions': {},
                'pca_statistics': {}
            }
            
            # 数据源分布
            if 'data_source' in data.columns:
                analysis['data_sources'] = data['data_source'].value_counts().to_dict()
            
            # 模型分布
            if 'model_name' in data.columns:
                roleplay_data = data[data['data_source'] == 'llm_roleplay'] if 'data_source' in data.columns else data
                if len(roleplay_data) > 0:
                    analysis['models'] = roleplay_data['model_name'].value_counts().to_dict()
            
            # 文化区域分布
            if 'Cultural Region' in data.columns:
                analysis['cultural_regions'] = data['Cultural Region'].value_counts().to_dict()
            
            # PCA统计
            if 'PC1_rescaled' in data.columns and 'PC2_rescaled' in data.columns:
                analysis['pca_statistics'] = {
                    'pc1_range': [float(data['PC1_rescaled'].min()), float(data['PC1_rescaled'].max())],
                    'pc2_range': [float(data['PC2_rescaled'].min()), float(data['PC2_rescaled'].max())],
                    'pc1_mean': float(data['PC1_rescaled'].mean()),
                    'pc2_mean': float(data['PC2_rescaled'].mean())
                }
            
            return analysis
            
        except Exception as e:
            print(f"⚠️ 数据分析失败: {e}")
            return {'error': str(e)}

    def step1_interview(self, test_mode=True, force_restart=False, consensus_count=5):
        """步骤1: 角色扮演访谈"""
        print("\n" + "="*60)
        print("🎭 步骤1: 角色扮演访谈")
        print("="*60)
        
        if not self.available_models:
            print("❌ 没有可用的模型，请检查API密钥配置")
            return False
        
        # 选择国家和模型
        if test_mode:
            print("🧪 测试模式：使用3个国家（China, Spain, United States）")
            countries = self._get_stage3_test_countries()
            print(f"   • 儒家文化圈: China")
            print(f"   • 天主教欧洲: Spain")
            print(f"   • 英语母语国家: United States")
            print(f"   • 总计: {len(countries)} 个国家，覆盖3个文化区域")
        else:
            print("🌍 完整模式：使用所有109个国家")
            countries = self._get_all_countries()
            print(f"总国家数: {len(countries)}")
        
        models = self.available_models
        print(f"使用模型: {models}")
        print(f"总任务数: {len(models)} × {len(countries)} = {len(models) * len(countries)}")
        
        # 创建访谈对象
        try:
            interview = LLMCountryRoleplayInterview(
                repeat_count=1,
                data_path=str(self.project_root / "data"),
                consensus_count=consensus_count
            )
            
            if consensus_count > 1:
                print(f"🔄 启用多次提问取众数功能：每个问题提问 {consensus_count} 次")
        except Exception as e:
            print(f"❌ 创建访谈对象失败: {e}")
            return False
        
        # 检查是否有现有结果（断点续传）
        if not force_restart:
            print("\n🔍 检查现有访谈结果...")
            existing_results = self._check_existing_interview_results(models, countries)
            if existing_results:
                print(f"✅ 发现现有结果: {existing_results['completed_tasks']}/{existing_results['total_tasks']} 个任务已完成")
                
                if existing_results['completed_tasks'] == existing_results['total_tasks']:
                    print("🎉 所有访谈任务已完成，跳过访谈步骤")
                    return True
                
                # 询问是否继续未完成的任务
                remaining_tasks = existing_results['total_tasks'] - existing_results['completed_tasks']
                print(f"📋 剩余任务: {remaining_tasks} 个")
                
                continue_choice = input("是否继续未完成的访谈任务？(y/n，默认y): ").strip().lower()
                if continue_choice in ['n', 'no', '否']:
                    print("⏭️ 跳过访谈步骤")
                    return True
        
        # 开始访谈
        print(f"\n🚀 开始角色扮演访谈...")
        print(f"⏰ 开始时间: {datetime.now()}")
        
        try:
            # 使用并发访谈（统一接口）
            results = interview.batch_interview(
                model_names=models,
                entities=countries,
                max_workers=3  # 控制并发数避免API限制，1为串行，>1为并行
            )
            
            if results and results.get('successful_tasks', 0) > 0:
                print(f"\n✅ 访谈完成!")
                print(f"📊 成功率: {results['successful_tasks']}/{results['total_tasks']} = {results['successful_tasks']/results['total_tasks']*100:.1f}%")
                print(f"⏰ 完成时间: {datetime.now()}")
                
                # 保存访谈结果
                self._save_interview_summary(results)
                return True
            else:
                print("❌ 访谈失败，没有获得有效结果")
                return False
                
        except KeyboardInterrupt:
            print("\n⏹️ 用户中断访谈")
            print("💾 已完成的结果已自动保存，可以稍后继续")
            return False
        except Exception as e:
            print(f"❌ 访谈过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _check_existing_interview_results(self, models, countries):
        """检查现有的访谈结果"""
        try:
            completed_tasks = 0
            total_tasks = len(models) * len(countries)
            
            # 检查llm_responses_roleplay目录中的文件
            if self.roleplay_responses_path.exists():
                for model in models:
                    for country in countries:
                        # 查找对应的结果文件
                        pattern = f"*{model}*{country}*.pkl"
                        matching_files = list(self.roleplay_responses_path.glob(pattern))
                        if matching_files:
                            completed_tasks += 1
            
            return {
                'completed_tasks': completed_tasks,
                'total_tasks': total_tasks,
                'completion_rate': completed_tasks / total_tasks if total_tasks > 0 else 0
            }
        except Exception as e:
            print(f"检查现有结果时出错: {e}")
            return None
    
    def _save_interview_summary(self, results):
        """保存访谈汇总信息"""
        try:
            summary = {
                'timestamp': datetime.now().isoformat(),
                'total_tasks': results.get('total_tasks', 0),
                'successful_tasks': results.get('successful_tasks', 0),
                'success_rate': results.get('successful_tasks', 0) / results.get('total_tasks', 1),
                'models_used': len(results.get('results', {})),
                'countries_interviewed': sum(len(countries) for countries in results.get('results', {}).values())
            }
            
            summary_path = self.roleplay_responses_path / "interview_summary.json"
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            print(f"📋 访谈汇总已保存到: {summary_path}")
            
        except Exception as e:
            print(f"保存访谈汇总失败: {e}")

    def step2_data_processing(self):
        """步骤2: 数据处理"""
        print("\n" + "="*60)
        print("🔄 步骤2: 处理访谈数据")
        print("="*60)
        
        try:
            # 创建数据处理器，使用正确的配置路径
            processor = LLMCountryRoleplayDataProcessor(
                data_dir=str(self.data_path),
                config_path=str(self.config_path / "llm_models.json")
            )
            
            # 检查是否有访谈数据需要处理
            raw_files = list(self.roleplay_responses_path.glob("*.pkl"))
            if not raw_files:
                print("❌ 未找到访谈数据文件，请先完成访谈步骤")
                return False
            
            print(f"📁 找到 {len(raw_files)} 个访谈数据文件")
            
            # 处理数据（包含与IVS数据的合并）
            print("🔄 开始处理访谈数据...")
            processed_data = processor.save_processed_data(merge_with_ivs=True)
            
            if processed_data is not None and len(processed_data) > 0:
                print(f"✅ 数据处理完成！处理了 {len(processed_data)} 条记录")
                
                # 检查是否包含IVS数据
                if 'data_source' in processed_data.columns:
                    ivs_count = len(processed_data[processed_data['data_source'] == 'IVS'])
                    roleplay_count = len(processed_data[processed_data['data_source'] == 'llm_roleplay'])
                    print(f"   📊 数据构成: IVS数据 {ivs_count} 条, 角色扮演数据 {roleplay_count} 条")
                
                return True
            else:
                print("❌ 数据处理失败")
                return False
            
        except Exception as e:
            print(f"❌ 数据处理过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def step3_pca_analysis(self):
        """步骤3: PCA分析"""
        print("\n" + "="*60)
        print("📊 步骤3: PCA分析")
        print("="*60)
        
        try:
            # 创建PCA分析器，传入项目data根目录
            # 分析器会自动在 data/country_values 中查找IVS数据
            # 在 data/roleplay_English 中查找角色扮演数据
            analyzer = LLMCountryRoleplayPCAAnalyzer(
                data_path=str(self.project_root / "data")
            )
            
            # 检查处理后的数据（查找最新文件）
            latest_file = self.data_path / "llm_roleplay_processed_responses_latest.pkl"
            ivs_files = list(self.data_path.glob("llm_roleplay_processed_responses_ivs_format_*.pkl"))
            processed_files = list(self.data_path.glob("llm_roleplay_processed_responses_*.pkl"))
            
            if not (latest_file.exists() or ivs_files or processed_files):
                print("❌ 未找到处理后的数据文件，请先完成数据处理步骤")
                return False
            
            print("✅ 找到处理后的数据文件")
            
            print("🔄 开始PCA分析...")
            
            # 执行PCA分析
            pca_results = analyzer.run_roleplay_analysis()
            
            if pca_results is not None and not pca_results.empty:
                print("✅ PCA分析完成！")
                print(f"📊 生成了 {len(pca_results)} 个实体的PCA分数")
                
                # 使用新的保存方法保存到roleplay_English目录
                analyzer.save_results(pca_results, prefix="roleplay_pca")
                
                # 设置选定的数据文件为最新的结果
                latest_file = analyzer.roleplay_data_path / "roleplay_pca_entity_scores_latest.pkl"
                if latest_file.exists():
                    self.selected_data_file = latest_file
                
                return True
            else:
                print("❌ PCA分析失败")
                return False
                
        except Exception as e:
            print(f"❌ PCA分析过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
            return False

    def step4_check_data(self):
        """步骤4: 检查现有数据"""
        print("\n" + "="*60)
        print("📊 步骤4: 检查现有Roleplay数据")
        print("="*60)
        
        # 检查已处理的数据文件
        # 优先查找最新的PCA结果文件
        print("🔍 查找最新的PCA结果文件...")
        
        # 1. 优先使用最新的PCA结果文件
        latest_pca_file = self.data_path / "roleplay_pca_entity_scores_latest.pkl"
        if latest_pca_file.exists():
            self.selected_data_file = latest_pca_file
            print(f"✅ 找到最新PCA结果文件: {self.selected_data_file}")
        else:
            # 2. 查找带时间戳的PCA结果文件（最新的）
            pca_files = list(self.data_path.glob("roleplay_pca_entity_scores_*.pkl"))
            if pca_files:
                latest_pca_timestamped = max(pca_files, key=lambda x: x.stat().st_mtime)
                self.selected_data_file = latest_pca_timestamped
                print(f"✅ 找到带时间戳的PCA结果文件: {self.selected_data_file}")
            else:
                # 3. 回退到旧的固定文件名
                fallback_files = [
                    self.data_path / "roleplay_entity_scores_pca.pkl",
                    self.roleplay_responses_path / "final_processed_roleplay_data.pkl",
                    self.data_path / "llm_roleplay_processed_responses_ivs_format.pkl"
                ]
                
                available_files = []
                for file_path in fallback_files:
                    if file_path.exists():
                        available_files.append(file_path)
                        print(f"✅ 找到回退数据文件: {file_path}")
                
                if not available_files:
                    print("❌ 未找到任何可用的roleplay数据文件")
                    return False
                
                self.selected_data_file = available_files[0]
                print(f"🎯 使用回退数据文件: {self.selected_data_file}")
        
        print(f"🎯 最终选择的数据文件: {self.selected_data_file}")
        
        # 检查数据内容
        try:
            data = pd.read_pickle(self.selected_data_file)
            print(f"\n📊 数据概览:")
            print(f"数据形状: {data.shape}")
            print(f"列名: {list(data.columns)}")
            
            if 'model_name' in data.columns:
                unique_models = data['model_name'].dropna().unique()
                unique_models = sorted([str(model) for model in unique_models if model is not None])
                print(f"包含的模型数量: {len(unique_models)}")
                print(f"模型列表: {unique_models}")
            
            if 'country_name' in data.columns:
                unique_countries = len(data['country_name'].unique())
                print(f"模仿的国家数量: {unique_countries}")
            elif 'country_code' in data.columns:
                unique_countries = len(data['country_code'].unique())
                print(f"模仿的国家数量: {unique_countries}")
            
            if 'data_source' in data.columns:
                print(f"数据源分布:")
                print(data['data_source'].value_counts())
            
            # 检查是否有PCA坐标
            has_pca = 'PC1_rescaled' in data.columns and 'PC2_rescaled' in data.columns
            print(f"包含PCA坐标: {'是' if has_pca else '否'}")
            
            return True
            
        except Exception as e:
            print(f"❌ 读取数据文件失败: {e}")
            return False
    
    def step5_visualization(self):
        """步骤5: 可视化"""
        print("\n" + "="*60)
        print("🎨 步骤5: 可视化")
        print("="*60)
        
        try:
            # 初始化可视化器
            print("\n1️⃣ 初始化可视化器...")
            visualizer = LLMCountryRoleplayVisualizer(
                data_path=str(self.data_path),
                results_path=str(self.results_path)
            )
            
            # 加载数据
            print("\n2️⃣ 加载数据...")
            
            # 如果没有选定的数据文件，尝试找到最新的PCA结果
            if not hasattr(self, 'selected_data_file') or not self.selected_data_file:
                # 优先使用最新的PCA结果文件
                latest_pca_file = self.data_path / "roleplay_pca_entity_scores_latest.pkl"
                if latest_pca_file.exists():
                    self.selected_data_file = latest_pca_file
                    print(f"📁 找到最新PCA结果文件: {self.selected_data_file.name}")
                else:
                    # 查找带时间戳的PCA结果文件（最新的）
                    pca_files = list(self.data_path.glob("roleplay_pca_entity_scores_*.pkl"))
                    if pca_files:
                        latest_pca_timestamped = max(pca_files, key=lambda x: x.stat().st_mtime)
                        self.selected_data_file = latest_pca_timestamped
                        print(f"📁 找到带时间戳PCA结果文件: {self.selected_data_file.name}")
                    else:
                        # 回退到旧文件
                        candidate_files = [
                            self.data_path / "roleplay_entity_scores_pca_fixed.pkl",
                            self.data_path / "roleplay_entity_scores_pca.pkl", 
                            self.data_path / "roleplay_pca_results.pkl",
                        ]
                        
                        for candidate_file in candidate_files:
                            if candidate_file.exists():
                                self.selected_data_file = candidate_file
                                print(f"📁 找到回退PCA结果文件: {self.selected_data_file.name}")
                                break
                
                if not hasattr(self, 'selected_data_file') or not self.selected_data_file:
                    print("❌ 未找到任何PCA结果文件，请先运行PCA分析")
                    return False
            
            data = pd.read_pickle(self.selected_data_file)
            print(f"✅ 成功加载数据: {len(data)} 个实体")
            
            # 检查数据是否包含PCA坐标
            if 'PC1_rescaled' not in data.columns or 'PC2_rescaled' not in data.columns:
                print("⚠️ 数据中缺少PCA坐标，无法进行可视化")
                return False
            
            # 使用可视化器的完整可视化流程
            print("\n3️⃣ 运行完整可视化流程...")
            visualizer.run_full_visualization(data=data)
            print(f"✅ 可视化完成，结果保存到: {visualizer.roleplay_results_path}")
            
            # 生成基础文化地图
            print("\n4️⃣ 生成基础文化地图...")
            basic_map_path = self.results_path / "roleplay_cultural_map.png"
            visualizer.plot_basic_cultural_map(data, title="Roleplay Cultural Map", save_path=str(basic_map_path))
            print(f"✅ 基础文化地图已保存到: {basic_map_path}")
            
            # 创建简单的准确性分析
            print("\n5️⃣ 分析角色扮演数据...")
            accuracy_analysis = self._analyze_roleplay_data(data)
            
            # 保存准确性分析结果
            accuracy_analysis_path = self.results_path / "roleplay_accuracy_analysis.json"
            with open(accuracy_analysis_path, 'w', encoding='utf-8') as f:
                json.dump(accuracy_analysis, f, indent=2, ensure_ascii=False)
            print(f"✅ 角色扮演准确性分析已保存到: {accuracy_analysis_path}")
            
            # 生成汇总统计
            print("\n6️⃣ 生成汇总统计...")
            summary_stats = {
                'total_entities': len(data),
                'pc1_range': [float(data['PC1_rescaled'].min()), float(data['PC1_rescaled'].max())],
                'pc2_range': [float(data['PC2_rescaled'].min()), float(data['PC2_rescaled'].max())]
            }
            
            if 'data_source' in data.columns:
                summary_stats['entities_by_source'] = data['data_source'].value_counts().to_dict()
            
            if 'model_name' in data.columns:
                roleplay_data = data[data['data_source'] == 'llm_roleplay'] if 'data_source' in data.columns else data
                if len(roleplay_data) > 0:
                    summary_stats['models'] = roleplay_data['model_name'].value_counts().to_dict()
            
            # 保存汇总统计到文件
            summary_path = self.results_path / "summary_statistics.txt"
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write("Roleplay English Analysis Summary\n")
                f.write("="*50 + "\n\n")
                f.write(f"Total entities: {summary_stats['total_entities']}\n\n")
                
                if 'entities_by_source' in summary_stats:
                    f.write("Entities by Data Source:\n")
                    for source, count in summary_stats['entities_by_source'].items():
                        f.write(f"  {source}: {count}\n")
                    f.write("\n")
                
                if 'models' in summary_stats:
                    f.write("Roleplay Models:\n")
                    for model, count in summary_stats['models'].items():
                        f.write(f"  {model}: {count}\n")
                    f.write("\n")
                
                f.write("Principal Component Statistics:\n")
                f.write(f"PC1 range: [{summary_stats['pc1_range'][0]:.2f}, {summary_stats['pc1_range'][1]:.2f}]\n")
                f.write(f"PC2 range: [{summary_stats['pc2_range'][0]:.2f}, {summary_stats['pc2_range'][1]:.2f}]\n\n")
                
                f.write("Accuracy Analysis:\n")
                f.write(str(accuracy_analysis))
            
            print(f"✅ 汇总统计已保存到: {summary_path}")
            
            # 保存文化坐标数据到results目录
            cultural_coordinates_path = self.results_path / "roleplay_cultural_coordinates.json"
            data.to_json(cultural_coordinates_path, orient='records', indent=2)
            print(f"✅ 文化坐标数据已保存到: {cultural_coordinates_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ 可视化失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def step6_distance_analysis(self):
        """步骤6: 距离分析"""
        print("\n" + "="*60)
        print("📏 步骤6: 文化距离分析")
        print("="*60)
        
        try:
            # 创建PCA分析器
            print("\n1️⃣ 初始化PCA分析器...")
            analyzer = LLMCountryRoleplayPCAAnalyzer(
                data_path=str(self.project_root / "data")
            )
            
            # 加载PCA结果
            print("\n2️⃣ 加载PCA结果...")
            latest_pca_file = self.data_path / "roleplay_pca_entity_scores_latest.pkl"
            
            if not latest_pca_file.exists():
                # 查找带时间戳的PCA结果文件
                pca_files = list(self.data_path.glob("roleplay_pca_entity_scores_*.pkl"))
                if pca_files:
                    latest_pca_file = max(pca_files, key=lambda x: x.stat().st_mtime)
                else:
                    print("❌ 未找到PCA结果文件，请先运行PCA分析")
                    return False
            
            entity_scores = pd.read_pickle(latest_pca_file)
            print(f"✅ 成功加载PCA结果: {len(entity_scores)} 个实体")
            
            # 计算距离
            print("\n3️⃣ 计算文化距离...")
            distance_df = analyzer.calculate_distances(entity_scores)
            
            if distance_df.empty:
                print("❌ 距离计算失败")
                return False
            
            # 保存距离分析结果
            print("\n4️⃣ 保存距离分析结果...")
            saved_path = analyzer.save_distances(distance_df)
            
            print(f"\n✅ 距离分析完成!")
            print(f"📊 计算了 {len(distance_df)} 个距离值")
            print(f"💾 结果已保存到: {saved_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ 距离分析失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_complete_analysis(self, test_mode=True, force_restart=False, skip_interview=False, consensus_count=5):
        """运行完整分析流程"""
        print("🚀 开始Roleplay English完整分析流程...")
        print(f"⏰ 开始时间: {datetime.now()}")
        
        success_steps = []
        
        # 步骤1: 角色扮演访谈（可选跳过）
        if not skip_interview:
            if self.step1_interview(test_mode=test_mode, force_restart=force_restart, consensus_count=consensus_count):
                success_steps.append("角色扮演访谈")
            else:
                print("❌ 访谈失败，但继续后续步骤")
        else:
            print("⏭️ 跳过访谈步骤")
        
        # 步骤2: 数据处理
        if self.step2_data_processing():
            success_steps.append("数据处理")
        else:
            print("❌ 数据处理失败，但继续后续步骤")
        
        # 步骤3: PCA分析
        if self.step3_pca_analysis():
            success_steps.append("PCA分析")
        else:
            print("❌ PCA分析失败，但继续后续步骤")
        
        # 步骤4: 检查现有数据
        if self.step4_check_data():
            success_steps.append("数据检查")
        else:
            print("❌ 数据检查失败，停止分析")
            return False
        
        # 步骤5: 可视化
        if self.step5_visualization():
            success_steps.append("可视化")
        else:
            print("❌ 可视化失败")
        
        # 步骤6: 距离分析
        if self.step6_distance_analysis():
            success_steps.append("距离分析")
        else:
            print("❌ 距离分析失败")
        
        # 总结
        print("\n" + "="*60)
        print("🎉 Roleplay English分析完成!")
        print("="*60)
        print(f"✅ 成功完成的步骤: {', '.join(success_steps)}")
        print(f"📁 数据文件位置: {self.data_path}")
        print(f"📁 结果文件位置: {self.results_path}")
        print(f"⏰ 完成时间: {datetime.now()}")
        
        # 显示生成的文件
        print("\n📋 生成的文件:")
        
        # 结果文件
        result_files = [
            "roleplay_cultural_map.png", "model_comparison.png",
            "roleplay_accuracy_analysis.json", "summary_statistics.txt", 
            "roleplay_cultural_coordinates.json"
        ]
        print("\n🎨 结果文件 (results/roleplay_English/):")
        for file_name in result_files:
            file_path = self.results_path / file_name
            if file_path.exists():
                print(f"  ✅ {file_name}")
            else:
                print(f"  ❌ {file_name}")
        
        return len(success_steps) >= 1


def main():
    """主函数"""
    
    print("\n" + "="*70)
    print("🎭 Stage2: Roleplay English 分析系统")
    print("="*70)
    print("\n请选择要执行的操作：")
    print("\n1️⃣  重新全部访谈 (所有109个国家，所有模型)")
    print("2️⃣  测试小规模访谈 (3个国家：China/Spain/USA，所有模型)")
    print("3️⃣  只分析现有数据 (数据处理 → PCA → 可视化)")
    print("0️⃣  退出")
    print("\n" + "="*70)
    
    try:
        # 创建分析运行器
        runner = RoleplayEnglishAnalysisRunner()
        
        while True:
            try:
                choice = input("\n请输入选项 (0-3): ").strip()
                
                if choice == '0':
                    print("👋 退出程序")
                    return 0
                elif choice in ['1', '2', '3']:
                    break
                else:
                    print("❌ 无效选项，请输入 0-3")
            except (KeyboardInterrupt, EOFError):
                print("\n\n👋 用户取消，退出程序")
                return 0
        
        # 处理选项1: 重新全部访谈
        if choice == '1':
            print("\n🚀 选项1: 重新全部访谈")
            print("  - 109个国家")
            print("  - 7个模型")
            print("  - 共识轮数: 3轮")
            print("  - 然后自动运行 数据处理 → PCA → 可视化")
            
            confirm = input("\n确认执行? (y/n): ").strip().lower()
            if confirm != 'y':
                print("❌ 已取消")
                return 0
            
            success = runner.run_complete_analysis(
                test_mode=False,  # 完整模式
                force_restart=True,  # 强制重新开始
                skip_interview=False,
                consensus_count=3
            )
        
        # 处理选项2: 测试小规模访谈
        elif choice == '2':
            print("\n🧪 选项2: 测试小规模访谈")
            print("  - 3个国家: China, Spain, United States")
            print("  - 7个模型")
            print("  - 共识轮数: 3轮")
            print("  - 然后自动运行 数据处理 → PCA → 可视化")
            
            confirm = input("\n确认执行? (y/n): ").strip().lower()
            if confirm != 'y':
                print("❌ 已取消")
                return 0
            
            success = runner.run_complete_analysis(
                test_mode=True,  # 测试模式
                force_restart=True,  # 强制重新开始
                skip_interview=False,
                consensus_count=3
            )
        
        # 处理选项3: 只分析现有数据
        elif choice == '3':
            print("\n📊 选项3: 只分析现有数据")
            print("  - 跳过访谈步骤")
            print("  - 运行: 数据处理 → PCA → 可视化")
            
            confirm = input("\n确认执行? (y/n): ").strip().lower()
            if confirm != 'y':
                print("❌ 已取消")
                return 0
            
            success = runner.run_complete_analysis(
                test_mode=True,  # 使用test_mode（不影响分析）
                force_restart=False,
                skip_interview=True,  # 跳过访谈
                consensus_count=3
            )
        
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