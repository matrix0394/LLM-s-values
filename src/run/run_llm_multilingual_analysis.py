#!/usr/bin/env python3
"""
Stage1: LLM Multilingual Values 完整分析运行脚本
对所有模型使用联合国6种官方语言进行价值观访谈、计算文化坐标并可视化

支持命令行参数:
  --models: 指定要测试的模型列表
  --languages: 指定要使用的语言列表
  --skip-existing: 跳过已完成的模型-语言组合
  --force: 强制重新运行访谈
  --consensus-count: 每个问题的重复次数（默认5）
  --step: 运行特定步骤
  --skip: 跳过指定的步骤
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# 导入所需模块
from src.llm_values.llm_multilingual_interview import LLMMultilingualInterview, UN_LANGUAGE_NAMES_ZH
from src.llm_values.llm_multilingual_data_processor import LLMMultilingualDataProcessor


class LLMMultilingualAnalysisRunner:
    """LLM多语言价值观分析运行器"""
    
    # 联合国6种官方语言
    UN_OFFICIAL_LANGUAGES = ['en', 'fr', 'es', 'ru', 'ar', 'zh-cn']
    
    def __init__(self, project_root=None):
        """
        初始化运行器
        
        Args:
            project_root: 项目根目录路径
        """
        if project_root is None:
            self.project_root = Path(__file__).parent.parent.parent
        else:
            self.project_root = Path(project_root)
        
        # 使用标准路径
        self.data_path = self.project_root / "data"
        self.results_path = self.project_root / "results"
        self.config_path = self.project_root / "config"
        
        # 确保目录存在
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.results_path.mkdir(parents=True, exist_ok=True)
        
        print(f"🏠 项目根目录: {self.project_root}")
        print(f"📁 数据目录: {self.data_path}")
        print(f"📁 结果目录: {self.results_path}")
    
    def get_available_models(self) -> list:
        """获取可用的模型列表"""
        import json
        config_file = self.config_path / 'models' / 'llm_models.json'
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return list(config.get('models', {}).keys())
        except Exception as e:
            print(f"⚠️ 加载模型配置失败: {e}")
            return []
    
    def step1_multilingual_interview(self, 
                                     model_names: list = None,
                                     languages: list = None,
                                     skip_existing: bool = False,
                                     force_rerun: bool = False,
                                     consensus_count: int = 5) -> dict:
        """
        步骤1: 多语言LLM访谈
        
        Args:
            model_names: 要测试的模型列表，None表示全部模型
            languages: 要使用的语言列表，None表示全部UN官方语言
            skip_existing: 是否跳过已完成的模型-语言组合
            force_rerun: 是否强制重新运行
            consensus_count: 每个问题的重复次数
        
        Returns:
            访谈结果字典
        """
        print("\n" + "="*80)
        print("📋 步骤1: 多语言LLM价值观访谈")
        print("="*80)
        
        # 确定语言列表
        if languages is None:
            languages = self.UN_OFFICIAL_LANGUAGES.copy()
        
        # 验证语言
        valid_languages = [lang for lang in languages if lang in self.UN_OFFICIAL_LANGUAGES]
        if not valid_languages:
            print(f"❌ 没有有效的语言: {languages}")
            print(f"   支持的语言: {self.UN_OFFICIAL_LANGUAGES}")
            return None
        
        print(f"\n🌍 访谈语言: {len(valid_languages)} 种")
        for lang in valid_languages:
            print(f"   - {lang}: {UN_LANGUAGE_NAMES_ZH.get(lang, lang)}")
        
        # 创建访谈对象
        print(f"\n🤖 初始化多语言访谈器（consensus_count={consensus_count}）...")
        interviewer = LLMMultilingualInterview(
            consensus_count=consensus_count,
            data_path=str(self.data_path)
        )
        
        # 获取可用模型
        available_models = [
            name for name in interviewer.model_configs.keys() 
            if name in interviewer.api_keys
        ]
        
        # 如果指定了模型列表，只使用指定的模型
        if model_names:
            available_models = [m for m in model_names if m in available_models]
            if not available_models:
                print(f"❌ 指定的模型都不可用: {model_names}")
                print("提示：请检查模型名称和API密钥配置")
                return None
            print(f"\n🎯 使用指定模型: {len(available_models)} 个")
        else:
            print(f"\n🔍 发现可用模型: {len(available_models)} 个")
        
        if not available_models:
            print("❌ 没有可用的模型，请检查API密钥配置")
            return None
        
        for i, model in enumerate(available_models, 1):
            region = interviewer.model_configs[model].get('region', 'Unknown')
            print(f"   {i}. {model} ({region})")
        
        # 计算任务数量
        total_combinations = len(available_models) * len(valid_languages)
        print(f"\n📊 任务统计:")
        print(f"   - 模型数量: {len(available_models)}")
        print(f"   - 语言数量: {len(valid_languages)}")
        print(f"   - 总组合数: {total_combinations}")
        print(f"   - 每组合轮数: {consensus_count}")
        print(f"   - 跳过已完成: {'是' if skip_existing else '否'}")
        
        if not skip_existing:
            print(f"   - 预计API调用: {total_combinations * 10 * consensus_count}")
        
        # 进行批量访谈
        print(f"\n🚀 开始批量多语言访谈...")
        results = interviewer.batch_multilingual_interview(
            model_names=available_models,
            languages=valid_languages,
            skip_existing=skip_existing
        )
        
        if not results or not results.get('results'):
            print("⚠️ 访谈完成，但没有新的结果")
            return results
        
        print(f"\n✅ 访谈完成！")
        print(f"📊 统计:")
        print(f"   - 成功率: {results['success_rate']:.1%}")
        print(f"   - 成功任务: {results['successful_tasks']}/{results['total_tasks']}")
        
        return results
    
    def step2_data_processing(self) -> dict:
        """
        步骤2: 数据处理 - 转换为IVS标准格式
        
        Returns:
            处理结果字典
        """
        print("\n" + "="*80)
        print("🔄 步骤2: 多语言数据处理")
        print("="*80)
        
        print("📦 使用LLMMultilingualDataProcessor处理数据...")
        
        # 创建处理器
        processor = LLMMultilingualDataProcessor(data_path=str(self.data_path))
        
        # 加载原始数据
        raw_results = processor.load_raw_results()
        
        if not raw_results:
            print("❌ 没有找到原始访谈数据")
            return None
        
        # 转换为IVS格式
        processed_data = processor.convert_to_ivs_format()
        
        if processed_data.empty:
            print("❌ 数据转换失败")
            return None
        
        # 保存处理后的数据
        json_file, pkl_file = processor.save_processed_results()
        
        print(f"\n✅ 数据处理完成！")
        print(f"📊 处理后数据:")
        print(f"   - 记录数量: {len(processed_data)}")
        print(f"   - 列数: {len(processed_data.columns)}")
        print(f"💾 保存至:")
        print(f"   - JSON: {json_file}")
        print(f"   - Pickle: {pkl_file}")
        
        return {
            'processed_data': processed_data,
            'json_file': json_file,
            'pkl_file': pkl_file
        }
    
    def step3_pca_analysis(self, use_fixed_pca: bool = True):
        """
        步骤3: PCA分析
        
        Args:
            use_fixed_pca: 是否使用固定的PCA模型（Stage0的模型）
        
        Returns:
            PCA结果DataFrame
        """
        print("\n" + "="*80)
        print("📊 步骤3: PCA分析")
        print("="*80)
        
        # 创建处理器
        processor = LLMMultilingualDataProcessor(data_path=str(self.data_path))
        
        # 加载并处理数据
        raw_results = processor.load_raw_results()
        if not raw_results:
            print("❌ 没有找到原始数据")
            return None
        
        processor.convert_to_ivs_format()
        
        # 运行PCA分析
        print(f"\n🔄 运行PCA分析（use_fixed_pca={use_fixed_pca}）...")
        entity_scores = processor.run_pca_analysis(use_fixed_pca=use_fixed_pca)
        
        if entity_scores is None or entity_scores.empty:
            print("❌ PCA分析失败")
            return None
        
        print(f"\n✅ PCA分析完成！")
        print(f"📊 结果统计:")
        print(f"   - 总实体数: {len(entity_scores)}")
        
        if 'PC1_rescaled' in entity_scores.columns:
            print(f"   - PC1范围: [{entity_scores['PC1_rescaled'].min():.2f}, {entity_scores['PC1_rescaled'].max():.2f}]")
        if 'PC2_rescaled' in entity_scores.columns:
            print(f"   - PC2范围: [{entity_scores['PC2_rescaled'].min():.2f}, {entity_scores['PC2_rescaled'].max():.2f}]")
        
        return entity_scores
    
    def step4_generate_report(self):
        """
        步骤4: 生成汇总报告
        
        Returns:
            报告字典
        """
        print("\n" + "="*80)
        print("📈 步骤4: 生成汇总报告")
        print("="*80)
        
        # 创建处理器
        processor = LLMMultilingualDataProcessor(data_path=str(self.data_path))
        
        # 加载并处理数据
        raw_results = processor.load_raw_results()
        if not raw_results:
            print("❌ 没有找到原始数据")
            return None
        
        processor.convert_to_ivs_format()
        
        # 生成报告
        report = processor.generate_summary_report()
        
        if not report:
            print("❌ 报告生成失败")
            return None
        
        # 保存报告
        report_file = processor.save_summary_report(report)
        
        print(f"\n✅ 报告生成完成！")
        print(f"📊 报告内容:")
        print(f"   - 模型数量: {len(report.get('models', {}))}")
        print(f"   - 语言数量: {len(report.get('language_summary', {}))}")
        print(f"   - 跨语言比较: {len(report.get('cross_language_comparison', []))} 组")
        print(f"💾 保存至: {report_file}")
        
        return report
    
    def step5_visualization(self):
        """
        步骤5: 可视化
        
        生成文化地图和各种分析图表
        确保输出与现有可视化工具兼容
        
        Returns:
            保存的图表文件路径字典
        """
        print("\n" + "="*80)
        print("📈 步骤5: 可视化")
        print("="*80)
        
        all_saved_files = {}
        
        # 5.1 基础可视化
        try:
            from src.llm_values.llm_visualization import LLMCulturalMapVisualizer
            
            print("\n🎨 5.1 基础可视化...")
            
            visualizer = LLMCulturalMapVisualizer(
                data_path=str(self.data_path),
                results_path=str(self.results_path)
            )
            
            saved_files = visualizer.create_llm_dashboard()
            all_saved_files['basic'] = saved_files
            
            print(f"✅ 基础可视化完成: {len(saved_files)} 个图表")
            
        except Exception as e:
            print(f"⚠️ 基础可视化失败: {e}")
        
        # 5.2 多语言可视化
        try:
            from src.llm_values.llm_multilingual_visualization import LLMMultilingualVisualizer
            
            print("\n🌍 5.2 多语言可视化...")
            print("   - 按语言区分的总图")
            print("   - 语言对比网格图")
            print("   - 每个模型的单独图表")
            
            ml_visualizer = LLMMultilingualVisualizer(
                data_path=str(self.data_path),
                results_path=str(self.results_path)
            )
            
            ml_saved_files = ml_visualizer.create_multilingual_dashboard()
            all_saved_files['multilingual'] = ml_saved_files
            
            # 统计生成的图表数量
            total_ml = 2  # 总图 + 网格图
            if 'per_model' in ml_saved_files and isinstance(ml_saved_files['per_model'], dict):
                total_ml += len(ml_saved_files['per_model'])
            
            print(f"✅ 多语言可视化完成: {total_ml} 个图表")
            
        except Exception as e:
            print(f"⚠️ 多语言可视化失败: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"\n✅ 可视化全部完成！")
        return all_saved_files
    
    def run_full_analysis(self,
                          model_names: list = None,
                          languages: list = None,
                          skip_existing: bool = False,
                          force_interview: bool = False,
                          consensus_count: int = 5,
                          skip_steps: list = None,
                          run_pca: bool = True,
                          run_visualization: bool = True):
        """
        运行完整分析流程
        
        Args:
            model_names: 要测试的模型列表
            languages: 要使用的语言列表
            skip_existing: 是否跳过已完成的组合
            force_interview: 是否强制重新运行访谈
            consensus_count: 每个问题的重复次数
            skip_steps: 要跳过的步骤列表
            run_pca: 是否运行PCA分析
            run_visualization: 是否运行可视化
        
        Returns:
            包含所有结果的字典
        """
        if skip_steps is None:
            skip_steps = []
        
        print("\n" + "="*80)
        print("🚀 Stage1: LLM Multilingual Values 完整分析流程")
        print("="*80)
        print(f"⚙️ 配置:")
        print(f"   - consensus_count: {consensus_count}")
        print(f"   - skip_existing: {skip_existing}")
        print(f"   - force_interview: {force_interview}")
        print(f"   - model_names: {model_names if model_names else '全部'}")
        print(f"   - languages: {languages if languages else '全部UN官方语言'}")
        print(f"   - skip_steps: {skip_steps if skip_steps else '无'}")
        print(f"   - run_pca: {run_pca}")
        print(f"   - run_visualization: {run_visualization}")
        
        results = {}
        
        try:
            # 步骤1: 访谈
            if 'interview' not in skip_steps:
                interview_result = self.step1_multilingual_interview(
                    model_names=model_names,
                    languages=languages,
                    skip_existing=skip_existing,
                    force_rerun=force_interview,
                    consensus_count=consensus_count
                )
                results['interview_result'] = interview_result
            else:
                print("\n⏭️ 跳过步骤1: 访谈")
            
            # 步骤2: 数据处理
            if 'process' not in skip_steps:
                process_result = self.step2_data_processing()
                if not process_result:
                    print("⚠️ 数据处理失败，但继续执行")
                results['process_result'] = process_result
            else:
                print("\n⏭️ 跳过步骤2: 数据处理")
            
            # 步骤3: PCA分析
            if 'pca' not in skip_steps and run_pca:
                entity_scores = self.step3_pca_analysis()
                results['entity_scores'] = entity_scores
            else:
                print("\n⏭️ 跳过步骤3: PCA分析")
            
            # 步骤4: 生成报告
            if 'report' not in skip_steps:
                report = self.step4_generate_report()
                results['report'] = report
            else:
                print("\n⏭️ 跳过步骤4: 生成报告")
            
            # 步骤5: 可视化
            if 'visualize' not in skip_steps and run_visualization:
                visualizations = self.step5_visualization()
                results['visualizations'] = visualizations
            else:
                print("\n⏭️ 跳过步骤5: 可视化")
            
            # 完成
            print("\n" + "="*80)
            print("🎉 Stage1多语言分析流程完成！")
            print("="*80)
            
            return results
            
        except Exception as e:
            print(f"\n❌ 分析过程中出现错误: {e}")
            import traceback
            traceback.print_exc()
            return None


def interactive_menu(runner: LLMMultilingualAnalysisRunner):
    """交互式菜单"""
    print("\n" + "="*70)
    print("🌍 Stage1: LLM Multilingual Values 分析系统")
    print("="*70)
    print("\n请选择要执行的操作：")
    print("\n1️⃣  完整多语言访谈 (所有模型，所有语言)")
    print("2️⃣  增量访谈 (跳过已完成的组合)")
    print("3️⃣  指定模型和语言访谈")
    print("4️⃣  只处理现有数据 (数据处理 + PCA + 报告 + 可视化)")
    print("5️⃣  只生成报告")
    print("6️⃣  只运行可视化")
    print("0️⃣  退出")
    print("\n" + "="*70)
    
    while True:
        try:
            choice = input("\n请输入选项 (0-6): ").strip()
            
            if choice == '0':
                print("👋 退出程序")
                return
            elif choice == '1':
                # 完整多语言访谈
                print("\n🚀 选项1: 完整多语言访谈")
                print("  - 访谈所有配置的模型")
                print("  - 使用所有6种UN官方语言")
                print("  - 共识轮数: 5轮")
                
                confirm = input("\n确认执行? (y/n): ").strip().lower()
                if confirm == 'y':
                    runner.run_full_analysis(
                        skip_existing=False,
                        consensus_count=5
                    )
                return
                
            elif choice == '2':
                # 增量访谈
                print("\n🔄 选项2: 增量访谈")
                print("  - 自动检测已完成的模型-语言组合")
                print("  - 只访谈未完成的组合")
                
                confirm = input("\n确认执行? (y/n): ").strip().lower()
                if confirm == 'y':
                    runner.run_full_analysis(
                        skip_existing=True,
                        consensus_count=5
                    )
                return
                
            elif choice == '3':
                # 指定模型和语言
                print("\n🎯 选项3: 指定模型和语言访谈")
                
                # 显示可用模型
                available_models = runner.get_available_models()
                print("\n可用模型:")
                model_map = {}
                for i, model in enumerate(available_models, 1):
                    print(f"  {i}. {model}")
                    model_map[str(i)] = model
                
                model_input = input("\n选择模型（逗号分隔，如1,2,3，回车=全部）: ").strip()
                if model_input:
                    model_input = model_input.replace('，', ',')
                    selected_models = [model_map[c.strip()] for c in model_input.split(',') 
                                      if c.strip() in model_map]
                else:
                    selected_models = None
                
                # 显示可用语言
                print("\n可用语言:")
                lang_map = {}
                for i, lang in enumerate(runner.UN_OFFICIAL_LANGUAGES, 1):
                    print(f"  {i}. {lang}: {UN_LANGUAGE_NAMES_ZH.get(lang, lang)}")
                    lang_map[str(i)] = lang
                
                lang_input = input("\n选择语言（逗号分隔，如1,2,3，回车=全部）: ").strip()
                if lang_input:
                    lang_input = lang_input.replace('，', ',')
                    selected_languages = [lang_map[c.strip()] for c in lang_input.split(',') 
                                         if c.strip() in lang_map]
                else:
                    selected_languages = None
                
                # 共识轮数
                consensus_input = input("\n共识轮数（回车=5）: ").strip()
                consensus_count = int(consensus_input) if consensus_input else 5
                
                print(f"\n已选择:")
                print(f"  - 模型: {selected_models if selected_models else '全部'}")
                print(f"  - 语言: {selected_languages if selected_languages else '全部'}")
                print(f"  - 共识轮数: {consensus_count}")
                
                confirm = input("\n确认执行? (y/n): ").strip().lower()
                if confirm == 'y':
                    runner.run_full_analysis(
                        model_names=selected_models,
                        languages=selected_languages,
                        skip_existing=True,
                        consensus_count=consensus_count
                    )
                return
                
            elif choice == '4':
                # 只处理现有数据
                print("\n📊 选项4: 只处理现有数据")
                print("  - 跳过访谈步骤")
                print("  - 运行: 数据处理 → PCA → 报告 → 可视化")
                
                confirm = input("\n确认执行? (y/n): ").strip().lower()
                if confirm == 'y':
                    runner.run_full_analysis(skip_steps=['interview'])
                return
                
            elif choice == '5':
                # 只生成报告
                print("\n📈 选项5: 只生成报告")
                
                confirm = input("\n确认执行? (y/n): ").strip().lower()
                if confirm == 'y':
                    runner.step4_generate_report()
                return
                
            elif choice == '6':
                # 只运行可视化
                print("\n🎨 选项6: 只运行可视化")
                
                confirm = input("\n确认执行? (y/n): ").strip().lower()
                if confirm == 'y':
                    runner.step5_visualization()
                return
                
            else:
                print("❌ 无效选项，请输入 0-6")
                
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 用户取消，退出程序")
            return


def main():
    """主函数 - 支持命令行参数和交互式菜单"""
    parser = argparse.ArgumentParser(
        description='Stage1: LLM Multilingual Values 完整分析',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 交互式菜单模式（推荐）
  python run_llm_multilingual_analysis.py
  
  # 命令行模式 - 完整访谈
  python run_llm_multilingual_analysis.py --force
  
  # 命令行模式 - 增量访谈
  python run_llm_multilingual_analysis.py --skip-existing
  
  # 命令行模式 - 指定模型和语言
  python run_llm_multilingual_analysis.py --models gpt-4o claude-3-opus --languages en zh-cn fr
  
  # 命令行模式 - 只处理现有数据
  python run_llm_multilingual_analysis.py --skip interview
  
  # 命令行模式 - 运行特定步骤
  python run_llm_multilingual_analysis.py --step process
  
  # 命令行模式 - 只运行可视化
  python run_llm_multilingual_analysis.py --step visualize
        """
    )
    
    parser.add_argument('--models', nargs='+', 
                       help='指定要测试的模型列表')
    parser.add_argument('--languages', nargs='+',
                       help='指定要使用的语言列表 (en, fr, es, ru, ar, zh-cn)')
    parser.add_argument('--skip-existing', action='store_true',
                       help='跳过已完成的模型-语言组合')
    parser.add_argument('--force', action='store_true',
                       help='强制重新运行访谈')
    parser.add_argument('--consensus-count', type=int, default=5,
                       help='每个问题的重复次数（默认5）')
    parser.add_argument('--step', 
                       choices=['interview', 'process', 'pca', 'report', 'visualize', 'all'],
                       help='运行特定步骤')
    parser.add_argument('--skip', nargs='+',
                       choices=['interview', 'process', 'pca', 'report', 'visualize'],
                       help='跳过指定的步骤')
    parser.add_argument('--no-pca', action='store_true',
                       help='不运行PCA分析')
    parser.add_argument('--no-visualize', action='store_true',
                       help='不运行可视化')
    parser.add_argument('--interactive', action='store_true',
                       help='使用交互式菜单')
    
    args = parser.parse_args()
    
    # 创建运行器
    runner = LLMMultilingualAnalysisRunner()
    
    # 判断是否使用交互式模式
    use_interactive = args.interactive or (
        not args.step and 
        not args.force and 
        not args.skip and 
        not args.models and 
        not args.languages and
        not args.skip_existing
    )
    
    if use_interactive:
        # 交互式菜单模式
        interactive_menu(runner)
    else:
        # 命令行模式
        if args.step:
            # 运行特定步骤
            if args.step == 'interview':
                runner.step1_multilingual_interview(
                    model_names=args.models,
                    languages=args.languages,
                    skip_existing=args.skip_existing,
                    force_rerun=args.force,
                    consensus_count=args.consensus_count
                )
            elif args.step == 'process':
                runner.step2_data_processing()
            elif args.step == 'pca':
                runner.step3_pca_analysis()
            elif args.step == 'report':
                runner.step4_generate_report()
            elif args.step == 'visualize':
                runner.step5_visualization()
            elif args.step == 'all':
                runner.run_full_analysis(
                    model_names=args.models,
                    languages=args.languages,
                    skip_existing=args.skip_existing,
                    force_interview=args.force,
                    consensus_count=args.consensus_count,
                    skip_steps=args.skip if args.skip else [],
                    run_pca=not args.no_pca,
                    run_visualization=not args.no_visualize
                )
        else:
            # 运行完整流程
            runner.run_full_analysis(
                model_names=args.models,
                languages=args.languages,
                skip_existing=args.skip_existing,
                force_interview=args.force,
                consensus_count=args.consensus_count,
                skip_steps=args.skip if args.skip else [],
                run_pca=not args.no_pca,
                run_visualization=not args.no_visualize
            )


if __name__ == "__main__":
    main()
