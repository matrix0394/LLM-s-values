#!/usr/bin/env python3
"""
完整的LLM Values分析运行脚本
对所有模型进行价值观访谈、计算文化坐标并可视化

数据存储规则：
- 处理后的数据和PCA计算结果 -> data/llm_values/
- 输出图片和文化坐标数据 -> results/llm_values/
"""

import os
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
import json

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# 导入所需模块
from src.llm_values.llm_interview import LLMInterview
from src.llm_values.llm_pca_analysis import LLMPCAAnalyzer
from src.llm_values.llm_visualization import LLMCulturalMapVisualizer


class LLMValuesAnalysisRunner:
    """LLM Values完整分析运行器"""
    
    def __init__(self, project_root=None):
        if project_root is None:
            self.project_root = Path(__file__).parent.parent.parent
        else:
            self.project_root = Path(project_root)
        
        # 设置路径
        self.data_path = self.project_root / "data" / "llm_values"
        self.results_path = self.project_root / "results" / "llm_values"
        
        # 确保目录存在
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.results_path.mkdir(parents=True, exist_ok=True)
        
        print(f"🏠 项目根目录: {self.project_root}")
        print(f"📁 数据目录: {self.data_path}")
        print(f"📁 结果目录: {self.results_path}")
    
    def step1_llm_interview(self, force_rerun: bool = False):
        """步骤1: LLM访谈"""
        print("\n" + "="*60)
        print("📋 步骤1: LLM价值观访谈")
        print("="*60)
        
        # 检查是否已有访谈结果
        interview_file = self.data_path / "llm_responses" / "all_models_responses.pkl"
        
        if interview_file.exists() and not force_rerun:
            print(f"✅ 发现已有访谈结果: {interview_file}")
            
            # 检查数据质量
            try:
                existing_data = pd.read_pickle(interview_file)
                print(f"📊 现有数据: {existing_data.shape}")
                print(f"   模型数量: {existing_data['model_name'].nunique() if 'model_name' in existing_data.columns else '未知'}")
                print(f"   问题数量: {len([col for col in existing_data.columns if col.startswith(('A', 'C', 'E', 'F', 'G', 'Y'))])}")
                
                # 询问是否重新运行
                response = input("\n是否重新运行访谈？(y/N): ").strip().lower()
                if response not in ['y', 'yes']:
                    print("⏭️ 跳过访谈步骤")
                    return str(interview_file)
            except Exception as e:
                print(f"⚠️ 读取现有数据失败: {e}")
                print("🔄 将重新运行访谈")
        
        # 创建访谈对象
        print("🤖 初始化LLM访谈器...")
        interviewer = LLMInterview(repeat_count=1)  # 每个问题问1次
        
        # 获取可用模型
        available_models = [name for name in interviewer.model_configs.keys() if name in interviewer.api_keys]
        print(f"🔍 发现可用模型: {len(available_models)}个")
        for i, model in enumerate(available_models, 1):
            print(f"   {i}. {model}")
        
        if not available_models:
            print("❌ 没有可用的模型，请检查API密钥配置")
            return None
        
        # 进行批量访谈
        print(f"\n🚀 开始批量访谈 {len(available_models)} 个模型...")
        results = interviewer.batch_interview(available_models)
        
        if not results or not results.get('results'):
            print("❌ 访谈失败，没有获得有效结果")
            return None
        
        # 保存结果
        output_file = interviewer.save_results(results)
        print(f"\n✅ 访谈完成！")
        print(f"📊 成功率: {results['success_rate']:.1%} ({results['successful_tasks']}/{results['total_tasks']})")
        print(f"💾 结果保存至: {output_file}")
        
        return output_file
    
    def step2_data_processing(self, interview_file: str = None):
        """步骤2: 数据处理 - 将LLM响应转换为IVS格式"""
        print("\n" + "="*60)
        print("🔄 步骤2: LLM数据处理")
        print("="*60)
        
        # 如果没有指定访谈文件，尝试找到最新的
        if interview_file is None:
            interview_dir = self.data_path / "llm_responses"
            if interview_dir.exists():
                # 优先查找宽格式文件
                wide_files = list(interview_dir.glob("llm_interview_responses_wide_*.pkl"))
                if wide_files:
                    interview_file = max(wide_files, key=lambda x: x.stat().st_mtime)
                    print(f"🔍 使用最新的宽格式访谈文件: {interview_file}")
                else:
                    # 如果没有宽格式，查找旧格式
                    old_files = list(interview_dir.glob("all_models_responses_*.pkl"))
                    if old_files:
                        interview_file = max(old_files, key=lambda x: x.stat().st_mtime)
                        print(f"🔍 使用最新的访谈文件: {interview_file}")
                    else:
                        print("❌ 未找到访谈结果文件")
                        return None
        
        # 生成处理后数据的文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        processed_file = self.data_path / f"llm_processed_responses_ivs_format_{timestamp}.pkl"
        
        # 加载原始访谈数据
        print(f"📂 加载访谈数据: {interview_file}")
        try:
            raw_data = pd.read_pickle(interview_file)
            print(f"📊 原始数据: {raw_data.shape}")
        except Exception as e:
            print(f"❌ 加载访谈数据失败: {e}")
            return None
        
        # 数据处理：转换为IVS兼容格式
        print("🔄 转换数据为IVS兼容格式...")
        
        # 导入IVS问题处理器
        try:
            from src.base.ivs_question_processor import IVSQuestionProcessor
        except ImportError:
            print("⚠️ 无法导入IVSQuestionProcessor，使用简化处理")
            IVSQuestionProcessor = None
        
        processed_rows = []
        
        for idx, row in raw_data.iterrows():
            model_name = row['model_name']
            
            # 创建处理后的行
            processed_row = {
                'country_code': f"LLM_{idx+1:03d}",  # 为LLM创建虚拟国家代码
                'year': 2024,  # LLM数据使用2024年
                'data_source': 'LLM',
                'entity_type': 'llm',
                'model_name': model_name,
                'entity_id': model_name,
                'weight': 1.0  # LLM数据权重设为1
            }
            
            # 处理每个IVS问题（只有10个核心问题）
            ivs_questions = ['A008', 'A165', 'E018', 'E025', 'F063', 'F118', 'F120', 'G006', 'Y002', 'Y003']
            
            for question_id in ivs_questions:
                response = row.get(question_id)
                
                try:
                    if question_id == 'Y002' and IVSQuestionProcessor:
                        # Y002需要特殊处理
                        if isinstance(response, (list, tuple)) and len(response) == 2:
                            processed_row[question_id] = IVSQuestionProcessor.process_y002(response[0], response[1])
                        else:
                            processed_row[question_id] = None
                            
                    elif question_id == 'Y003' and IVSQuestionProcessor:
                        # Y003需要特殊处理
                        if isinstance(response, (list, tuple)) and len(response) > 0:
                            result = IVSQuestionProcessor.process_y003(list(response))
                            processed_row[question_id] = result.get("y003_score")
                        else:
                            processed_row[question_id] = None
                            
                    elif isinstance(response, (int, float)):
                        # 单选题直接使用
                        processed_row[question_id] = float(response)
                    elif isinstance(response, (list, tuple)) and len(response) > 0:
                        # 如果是列表但不是Y002/Y003，取第一个值
                        processed_row[question_id] = float(response[0])
                    else:
                        # 无效回答设为None
                        processed_row[question_id] = None
                        
                except Exception as e:
                    print(f"⚠️ 处理问题 {question_id} 失败: {e}")
                    processed_row[question_id] = None
            
            processed_rows.append(processed_row)
        
        # 转换为DataFrame
        processed_data = pd.DataFrame(processed_rows)
        
        # 不添加额外的问题列，只使用10个核心IVS问题
        print(f"✅ 处理完成，包含 {len(ivs_questions)} 个IVS问题")
        
        # 保存处理后的数据
        processed_data.to_pickle(processed_file)
        print(f"💾 处理后数据保存至: {processed_file}")
        print(f"📊 处理后数据: {processed_data.shape}")
        
        return str(processed_file)
    
    def step3_pca_analysis(self, processed_file: str = None):
        """步骤3: PCA分析"""
        print("\n" + "="*60)
        print("📊 步骤3: PCA分析")
        print("="*60)
        
        # 使用旧系统的LLM PCA分析器
        from src.llm_values.llm_pca_analysis import LLMPCAAnalyzer
        
        # 初始化分析器，传入正确的数据路径（需要指向包含IVS数据的路径）
        analyzer = LLMPCAAnalyzer(data_path=str(self.data_path.parent / "country_values"))
        
        # 手动设置LLM数据路径到我们的处理文件
        if processed_file:
            print(f"📂 手动加载LLM数据: {processed_file}")
            analyzer.llm_data = pd.read_pickle(processed_file)
            print(f"📊 LLM数据: {analyzer.llm_data.shape}")
            
            # 重写load_additional_data方法，直接返回我们的数据
            def custom_load_additional_data():
                return analyzer.llm_data
            analyzer.load_additional_data = custom_load_additional_data
            
            # 重写save_results方法，保存到正确的llm_values目录
            def custom_save_results(entity_scores=None, prefix="llm_pca"):
                """保存结果到llm_values目录"""
                # 保存PCA结果
                if analyzer.pca_results is not None:
                    pca_path = self.data_path / f"{prefix}_results.pkl"
                    analyzer.pca_results.to_pickle(pca_path)
                    print(f"💾 保存PCA结果到: {pca_path}")
                
                # 保存实体分数
                if entity_scores is not None:
                    scores_path = self.data_path / f"{prefix}_entity_scores.pkl"
                    entity_scores.to_pickle(scores_path)
                    print(f"💾 保存实体分数到: {scores_path}")
                    
                    # JSON格式
                    scores_json = self.data_path / f"{prefix}_entity_scores.json"
                    entity_scores.to_json(scores_json, orient='records', indent=2)
                    print(f"💾 保存JSON格式到: {scores_json}")
            
            analyzer.save_results = custom_save_results
        
        # 检查是否已有PCA结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pca_file = self.data_path / f"llm_pca_entity_scores_{timestamp}.pkl"
        
        # 运行完整的PCA分析
        print("🔄 运行PCA分析...")
        try:
            results = analyzer.run_full_analysis()
            
            if results is not None and hasattr(results, 'shape') and not results.empty:
                print("✅ PCA分析完成！")
                print(f"📊 结果形状: {results.shape}")
                
                # 保存到我们的数据目录（带时间戳）
                results.to_pickle(pca_file)
                print(f"💾 PCA结果保存至: {pca_file}")
                
                # 同时保存到标准位置（不带时间戳）
                standard_file = self.data_path / "llm_pca_entity_scores.pkl"
                results.to_pickle(standard_file)
                print(f"💾 标准PCA结果保存至: {standard_file}")
                
                return str(pca_file)
            elif hasattr(analyzer, 'entity_scores') and analyzer.entity_scores is not None:
                print("✅ PCA分析完成！")
                print(f"📊 实体分数形状: {analyzer.entity_scores.shape}")
                
                # 保存实体分数
                analyzer.entity_scores.to_pickle(pca_file)
                print(f"💾 实体分数保存至: {pca_file}")
                
                # 同时保存到标准位置
                standard_file = self.data_path / "llm_pca_entity_scores.pkl"
                analyzer.entity_scores.to_pickle(standard_file)
                print(f"💾 标准实体分数保存至: {standard_file}")
                
                return str(pca_file)
            else:
                print("❌ PCA分析失败")
                return None
                
        except Exception as e:
            print(f"❌ PCA分析出错: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def step4_visualization(self, pca_file: str = None):
        """步骤4: 可视化"""
        print("\n" + "="*60)
        print("🎨 步骤4: 文化地图可视化")
        print("="*60)
        
        # 使用旧系统的LLM可视化器
        from src.llm_values.llm_visualization import LLMCulturalMapVisualizer
        
        # 创建可视化器，传入正确的数据路径
        visualizer = LLMCulturalMapVisualizer(
            data_path=str(self.data_path.parent / "country_values"),  # 指向包含IVS数据的路径
            results_path=str(self.results_path)
        )
        
        try:
            # 生成所有可视化
            print("🎨 生成文化地图...")
            
            # 手动加载我们的PCA数据并生成可视化
            import pandas as pd
            import matplotlib.pyplot as plt
            import numpy as np
            
            pca_data = pd.read_pickle(pca_file)
            print(f"📊 加载PCA数据: {pca_data.shape}")
            
            # 分离IVS和LLM数据
            ivs_data = pca_data[pca_data['data_source'] == 'IVS']
            llm_data = pca_data[pca_data['data_source'] == 'LLM']
            
            print(f"🌍 真实国家数据: {len(ivs_data)}")
            print(f"🤖 LLM模型数据: {len(llm_data)}")
            
            # 创建完整的文化地图
            print("📊 生成完整的LLM vs 国家文化地图...")
            
            plt.figure(figsize=(16, 12))
            
            # 使用和roleplay_English完全一样的文化区域颜色
            cultural_region_colors = {
                'African-Islamic': '#cc79a7',
                'Orthodox Europe': '#0072b2',
                'Catholic Europe': '#e69f00',
                'Protestant Europe': '#d55e00',
                'English-Speaking': '#009e73',
                'Latin America': '#999999',
                'Confucian': '#e69f00',
                'West & South Asia': '#f0e442',
                'Unknown': '#cccccc'
            }
            
            # 绘制真实国家（按文化区域着色）
            if 'Cultural Region' in ivs_data.columns:
                for region, color in cultural_region_colors.items():
                    subset = ivs_data[ivs_data['Cultural Region'] == region]
                    if len(subset) > 0:
                        plt.scatter(subset['PC1_rescaled'], subset['PC2_rescaled'], 
                                   label=f'{region}', color=color, s=50, alpha=0.7, 
                                   marker='o', edgecolors='black', linewidth=0.5)
                        
                        # 添加国家标签（与roleplay_English保持一致的格式）
                        for _, row in subset.iterrows():
                            if pd.notna(row.get('Country')):
                                country_name = str(row['Country'])
                                # 对于伊斯兰国家使用斜体
                                if 'Islamic' in row and row['Islamic']:
                                    plt.text(row['PC1_rescaled'], row['PC2_rescaled'], country_name, 
                                            color=color, fontsize=8, fontstyle='italic', 
                                            ha='center', va='bottom', alpha=0.8)
                                else:
                                    plt.text(row['PC1_rescaled'], row['PC2_rescaled'], country_name, 
                                            color=color, fontsize=8, 
                                            ha='center', va='bottom', alpha=0.8)
            else:
                # 如果没有文化区域信息，用单一颜色
                plt.scatter(ivs_data['PC1_rescaled'], ivs_data['PC2_rescaled'], 
                           c='lightblue', alpha=0.6, s=50, label='Countries (IVS)', 
                           marker='o', edgecolors='black', linewidth=0.5)
            
            # 使用和roleplay_English一样的LLM颜色和格式
            llm_colors = {
                'anthropic': '#4ecdc4',    # 青色
                'openai': '#ff6b6b',       # 红色
                'google': '#45b7d1',       # 蓝色
                'meta-llama': '#96ceb4',   # 绿色
                'deepseek': '#a29bfe',     # 紫色
                'qwen': '#ffeaa7',         # 黄色
                'mistralai': '#fd79a8',    # 粉色
            }
            
            # 绘制LLM模型（使用和roleplay_English一样的格式）
            for _, row in llm_data.iterrows():
                model_name = row['model_name']
                provider = model_name.split('/')[0] if '/' in model_name else model_name.split('-')[0]
                color = llm_colors.get(provider, '#ff1493')
                
                # 使用圆形标记，与roleplay_English保持一致
                plt.scatter(row['PC1_rescaled'], row['PC2_rescaled'], 
                           color=color, s=100, alpha=0.8, marker='o', 
                           edgecolors='black', linewidth=1,
                           label=f"LLM: {model_name.split('/')[-1]}")
                
                # 添加模型标签
                plt.text(row['PC1_rescaled'], row['PC2_rescaled'], 
                        model_name.split('/')[-1], 
                        color='black', fontsize=8, fontweight='bold',
                        ha='center', va='bottom')
            
            # 设置图形属性（与roleplay_English保持一致）
            plt.xlabel('Survival vs. Self-Expression Values', fontsize=12)
            plt.ylabel('Traditional vs. Secular Values', fontsize=12)
            plt.title('Inglehart-Welzel Cultural Map', fontsize=14, fontweight='bold')
            
            # 添加网格和图例
            plt.grid(True, alpha=0.3)
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
            
            # 保存图形
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.results_path / f"llm_vs_countries_complete_{timestamp}.png"
            
            plt.tight_layout()
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"💾 完整文化地图保存至: {output_file}")
            
            saved_files = {'complete_cultural_map': str(output_file)}
            
            print("✅ 所有可视化完成！")
            
            return True
            
        except Exception as e:
            print(f"❌ 可视化出错: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def step5_summary_report(self):
        """步骤5: 生成总结报告"""
        print("\n" + "="*60)
        print("📋 步骤5: 生成分析报告")
        print("="*60)
        
        try:
            # 收集所有生成的文件
            generated_files = []
            
            # 数据文件
            data_files = [
                "llm_responses/all_models_responses_*.pkl",
                "llm_processed_responses_ivs_format.pkl",
                "llm_pca_entity_scores.pkl",
                "llm_pca_results.pkl"
            ]
            
            for pattern in data_files:
                files = list(self.data_path.glob(pattern))
                generated_files.extend([str(f.relative_to(self.project_root)) for f in files])
            
            # 结果文件
            result_files = list(self.results_path.glob("*"))
            generated_files.extend([str(f.relative_to(self.project_root)) for f in result_files])
            
            # 生成报告
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.results_path / f"llm_values_analysis_report_{timestamp}.md"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(f"# LLM Values Analysis Report\n\n")
                f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write(f"## 📊 分析概览\n\n")
                f.write(f"本报告包含了对所有可用大语言模型的文化价值观分析结果。\n\n")
                
                # 尝试加载和分析数据
                try:
                    pca_file = self.data_path / "llm_pca_entity_scores.pkl"
                    if pca_file.exists():
                        pca_data = pd.read_pickle(pca_file)
                        
                        f.write(f"### 🤖 模型统计\n\n")
                        if 'model_name' in pca_data.columns:
                            models = pca_data['model_name'].unique()
                            f.write(f"- **模型数量**: {len(models)}\n")
                            f.write(f"- **模型列表**:\n")
                            for model in sorted(models):
                                f.write(f"  - {model}\n")
                        
                        f.write(f"\n### 📈 数据统计\n\n")
                        f.write(f"- **实体数量**: {len(pca_data)}\n")
                        f.write(f"- **数据维度**: {pca_data.shape}\n")
                        
                        if 'PC1' in pca_data.columns and 'PC2' in pca_data.columns:
                            f.write(f"- **PC1范围**: {pca_data['PC1'].min():.3f} ~ {pca_data['PC1'].max():.3f}\n")
                            f.write(f"- **PC2范围**: {pca_data['PC2'].min():.3f} ~ {pca_data['PC2'].max():.3f}\n")
                
                except Exception as e:
                    f.write(f"⚠️ 无法加载PCA数据进行统计: {e}\n\n")
                
                f.write(f"\n## 📁 生成文件\n\n")
                f.write(f"本次分析共生成了 {len(generated_files)} 个文件：\n\n")
                
                for file_path in sorted(generated_files):
                    f.write(f"- `{file_path}`\n")
                
                f.write(f"\n## 🎯 主要结果\n\n")
                f.write(f"1. **LLM访谈数据**: 包含所有模型对IVS问题的回答\n")
                f.write(f"2. **PCA分析结果**: 模型在文化价值观空间中的坐标\n")
                f.write(f"3. **可视化图表**: 文化地图和对比分析图\n")
                f.write(f"4. **交互式地图**: 可交互的文化坐标可视化\n\n")
                
                f.write(f"## 📖 使用说明\n\n")
                f.write(f"- 查看 `results/llm_values/` 目录下的图片文件了解可视化结果\n")
                f.write(f"- 使用 `cultural_coordinates.json` 获取精确的坐标数据\n")
                f.write(f"- 打开 `cultural_map_interactive.html` 查看交互式地图\n\n")
            
            print(f"📋 分析报告已生成: {report_file}")
            return str(report_file)
            
        except Exception as e:
            print(f"❌ 生成报告失败: {e}")
            return None
    
    def run_full_analysis(self, force_rerun: bool = False):
        """运行完整的LLM Values分析流程"""
        print("🚀 LLM Values 完整分析流程")
        print("="*60)
        print("📋 分析步骤:")
        print("   1️⃣ LLM价值观访谈")
        print("   2️⃣ 数据处理转换") 
        print("   3️⃣ PCA文化坐标分析")
        print("   4️⃣ 文化地图可视化")
        print("   5️⃣ 生成分析报告")
        print()
        
        start_time = datetime.now()
        
        try:
            # 步骤1: LLM访谈
            interview_file = self.step1_llm_interview(force_rerun=force_rerun)
            if not interview_file:
                print("❌ 访谈步骤失败，终止分析")
                return False
            
            # 步骤2: 数据处理
            processed_file = self.step2_data_processing(interview_file)
            if not processed_file:
                print("❌ 数据处理步骤失败，终止分析")
                return False
            
            # 步骤3: PCA分析
            pca_file = self.step3_pca_analysis(processed_file)
            if not pca_file:
                print("❌ PCA分析步骤失败，终止分析")
                return False
            
            # 步骤4: 可视化
            viz_success = self.step4_visualization(pca_file)
            if not viz_success:
                print("❌ 可视化步骤失败，但继续生成报告")
            
            # 步骤5: 生成报告
            report_file = self.step5_summary_report()
            
            # 完成总结
            end_time = datetime.now()
            duration = end_time - start_time
            
            print("\n" + "="*60)
            print("🎉 LLM Values 分析完成！")
            print("="*60)
            print(f"⏱️ 总耗时: {duration}")
            print(f"📁 数据目录: {self.data_path}")
            print(f"📁 结果目录: {self.results_path}")
            if report_file:
                print(f"📋 分析报告: {report_file}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ 分析流程出错: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """主函数"""
    print("🤖 LLM Values Analysis Runner")
    print("="*60)
    
    # 创建分析运行器
    runner = LLMValuesAnalysisRunner()
    
    # 检查是否需要强制重新运行
    import argparse
    parser = argparse.ArgumentParser(description='LLM Values Analysis')
    parser.add_argument('--force', action='store_true', help='强制重新运行所有步骤')
    args = parser.parse_args()
    
    # 运行完整分析
    success = runner.run_full_analysis(force_rerun=args.force)
    
    if success:
        print("\n✅ 所有分析步骤完成！")
        print("🔍 请查看 results/llm_values/ 目录下的结果文件")
    else:
        print("\n❌ 分析过程中出现错误")
        sys.exit(1)


if __name__ == "__main__":
    main()
