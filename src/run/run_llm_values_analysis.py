#!/usr/bin/env python3
"""
Stage1: LLM Values 完整分析运行脚本
对所有模型进行价值观访谈、计算文化坐标并可视化

简化版本 - 使用标准化的数据处理流程
"""

import os
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# 导入所需模块
from src.llm_values.llm_interview import LLMInterview
from src.llm_values.llm_data_processor import LLMDataProcessor
from src.llm_values.llm_pca_analysis import LLMPCAAnalyzer
from src.llm_values.llm_visualization import LLMCulturalMapVisualizer


class LLMValuesAnalysisRunner:
    """LLM Values完整分析运行器（简化版）"""
    
    def __init__(self, project_root=None):
        if project_root is None:
            self.project_root = Path(__file__).parent.parent.parent
        else:
            self.project_root = Path(project_root)
        
        # 使用标准路径（与Stage0一致）
        self.data_path = self.project_root / "data"
        self.results_path = self.project_root / "results" / "llm_values"
        
        # 确保目录存在
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.results_path.mkdir(parents=True, exist_ok=True)
        
        print(f"🏠 项目根目录: {self.project_root}")
        print(f"📁 数据目录: {self.data_path}")
        print(f"📁 结果目录: {self.results_path}")
    
    def step1_llm_interview(self, force_rerun: bool = False, consensus_count: int = 5, 
                           model_names: list = None, skip_existing: bool = False):
        """
        步骤1: LLM访谈
        
        Args:
            force_rerun: 是否强制重新运行
            consensus_count: 每个问题的重复次数（取众数）
            model_names: 要测试的模型列表，None表示全部模型
            skip_existing: 是否跳过已完成的模型（增量访谈）
        
        Returns:
            访谈结果文件路径
        """
        print("\n" + "="*80)
        print("📋 步骤1: LLM价值观访谈")
        print("="*80)
        
        # 检查是否已有访谈结果
        interview_pattern = self.data_path / "llm_values" / "raw_interview_*.pkl"
        existing_files = list(self.data_path.glob("llm_values/raw_interview_*.pkl"))
        
        if existing_files and not force_rerun:
            latest_file = max(existing_files, key=lambda x: x.stat().st_mtime)
            print(f"✅ 发现已有访谈结果: {latest_file}")
            
            # 检查数据质量
            try:
                import json
                json_file = str(latest_file).replace('.pkl', '.json')
                if Path(json_file).exists():
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                        metadata = data.get('metadata', {})
                        results = data.get('results', [])
                        
                        print(f"📊 现有数据:")
                        print(f"   - 模型数量: {metadata.get('total_entities', 0)}")
                        print(f"   - 问题数量: {metadata.get('total_questions', 0)}")
                        print(f"   - 时间戳: {metadata.get('timestamp', '未知')}")
                        print(f"   - 轮数: {metadata.get('consensus_count', 1)}")
                
                # 询问是否重新运行
                response = input("\n是否重新运行访谈？(y/N): ").strip().lower()
                if response not in ['y', 'yes']:
                    print("⏭️ 跳过访谈步骤，使用现有数据")
                    return str(latest_file)
            except Exception as e:
                print(f"⚠️ 读取现有数据失败: {e}")
                print("🔄 将重新运行访谈")
        
        # 创建访谈对象
        print(f"\n🤖 初始化LLM访谈器（consensus_count={consensus_count}）...")
        interviewer = LLMInterview(
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
            print(f"\n🎯 使用指定模型: {len(available_models)}个")
        else:
            print(f"\n🔍 发现可用模型: {len(available_models)}个")
        
        if not available_models:
            print("❌ 没有可用的模型，请检查API密钥配置")
            print("提示：需要在环境变量中设置相应的API密钥")
            return None
        
        for i, model in enumerate(available_models, 1):
            region = interviewer.model_configs[model].get('region', 'Unknown')
            print(f"   {i}. {model} ({region})")
        
        # 进行批量访谈
        print(f"\n🚀 开始批量访谈...")
        print(f"   - 模型数量: {len(available_models)}")
        print(f"   - 每模型轮数: {consensus_count}")
        print(f"   - 增量访谈: {'是' if skip_existing else '否'}")
        if not skip_existing:
            print(f"   - 总API调用: {len(available_models) * 10 * consensus_count}")
        
        results = interviewer.batch_interview(
            model_names=available_models,
            max_workers=1,  # 串行执行（避免API限流）
            skip_existing=skip_existing  # 传递skip_existing参数
        )
        
        if not results or not results.get('results'):
            print("❌ 访谈失败，没有获得有效结果")
            return None
        
        # 保存结果（使用统一格式）
        print(f"\n💾 保存访谈结果...")
        output_file = interviewer.save_results(
            results, 
            use_unified_format=True
        )
        
        print(f"\n✅ 访谈完成！")
        print(f"📊 统计:")
        print(f"   - 成功率: {results['success_rate']:.1%}")
        print(f"   - 成功任务: {results['successful_tasks']}/{results['total_tasks']}")
        print(f"💾 结果保存至: {output_file}")
        
        return output_file
    
    def step2_data_processing(self):
        """
        步骤2: 数据处理 - 转换为IVS标准格式
        
        使用llm_data_processor.py统一处理
        
        Returns:
            处理后的数据文件路径
        """
        print("\n" + "="*80)
        print("🔄 步骤2: LLM数据处理")
        print("="*80)
        
        print("📦 使用LLMDataProcessor处理数据...")
        
        # 创建处理器
        processor = LLMDataProcessor(data_dir=str(self.data_path))
        
        # 处理并保存为IVS标准格式（返回保存的文件路径）
        print("🔄 转换为IVS标准格式...")
        output_file = processor.save_processed_data()
        
        if output_file and Path(output_file).exists():
            # 验证数据
            data = pd.read_pickle(output_file)
            print(f"\n✅ 数据处理完成！")
            print(f"📊 处理后数据:")
            print(f"   - 模型数量: {len(data)}")
            print(f"   - 列数: {len(data.columns)}")
            print(f"   - IVS问题: A008-G006, Y002, Y003")
            print(f"   - 格式: 与Stage0的valid_data.pkl一致")
            print(f"💾 保存至: {output_file}")
            return str(output_file)
        else:
            print("❌ 数据处理失败")
            return None
    
    def step3_pca_analysis(self):
        """
        步骤3: PCA分析
        
        使用llm_pca_analysis.py进行PCA计算
        自动加载IVS数据和LLM数据
        
        Returns:
            PCA结果DataFrame
        """
        print("\n" + "="*80)
        print("📊 步骤3: PCA分析")
        print("="*80)
        
        print("📈 初始化LLMPCAAnalyzer...")
        
        # 创建分析器（使用标准路径）
        analyzer = LLMPCAAnalyzer(data_path=str(self.data_path))
        
        print("🔄 运行完整PCA分析...")
        print("   1. 加载IVS数据（Stage0）")
        print("   2. 加载LLM数据（Stage1）")
        print("   3. 合并数据")
        print("   4. 执行PCA计算")
        print("   5. 计算实体分数")
        print("   6. 保存结果")
        
        # 运行完整分析
        entity_scores = analyzer.run_full_analysis()
        
        if entity_scores is None or entity_scores.empty:
            print("❌ PCA分析失败")
            return None
        
        print(f"\n✅ PCA分析完成！")
        print(f"📊 结果统计:")
        print(f"   - 总实体数: {len(entity_scores)}")
        
        if 'is_llm' in entity_scores.columns:
            llm_count = entity_scores['is_llm'].sum()
            country_count = (~entity_scores['is_llm']).sum()
            print(f"   - LLM模型: {llm_count} 个")
            print(f"   - 真实国家: {country_count} 个")
        
        if 'PC1_rescaled' in entity_scores.columns:
            print(f"   - PC1范围: [{entity_scores['PC1_rescaled'].min():.2f}, {entity_scores['PC1_rescaled'].max():.2f}]")
            print(f"   - PC2范围: [{entity_scores['PC2_rescaled'].min():.2f}, {entity_scores['PC2_rescaled'].max():.2f}]")
        
        print(f"💾 结果保存至: {self.data_path}/llm_pca_entity_scores.pkl")
        
        return entity_scores
    
    def step4_visualization(self):
        """
        步骤4: 可视化
        
        生成文化地图和各种分析图表
        
        Returns:
            保存的图表文件路径字典
        """
        print("\n" + "="*80)
        print("📈 步骤4: 可视化")
        print("="*80)
        
        print("🎨 初始化可视化器...")
        
        # 创建可视化器
        visualizer = LLMCulturalMapVisualizer(
            data_path=str(self.data_path),
            results_path=str(self.results_path)
        )
        
        print("🎨 创建可视化仪表板...")
        print("   - 文化地图（LLM + 真实国家）")
        print("   - LLM vs 国家对比图")
        print("   - 模型对比分析")
        
        # 创建仪表板
        saved_files = visualizer.create_llm_dashboard()
        
        print(f"\n✅ 可视化完成！")
        print(f"📊 生成的图表: {len(saved_files)}个")
        for name, path in saved_files.items():
            print(f"   - {name}: {path}")
        
        return saved_files
    
    def run_full_analysis(self, force_interview: bool = False, 
                         consensus_count: int = 5,
                         skip_steps: list = None,
                         model_names: list = None,
                         skip_existing: bool = False):
        """
        运行完整分析流程
        
        Args:
            force_interview: 是否强制重新运行访谈
            consensus_count: 每个问题的重复次数
            skip_steps: 要跳过的步骤列表（如['interview', 'process']）
            model_names: 要测试的模型列表，None表示全部模型
            skip_existing: 是否跳过已完成的模型（增量访谈）
        
        Returns:
            包含所有结果的字典
        """
        if skip_steps is None:
            skip_steps = []
        
        print("\n" + "="*80)
        print("🚀 Stage1: LLM Values 完整分析流程")
        print("="*80)
        print(f"⚙️ 配置:")
        print(f"   - consensus_count: {consensus_count}")
        print(f"   - force_interview: {force_interview}")
        print(f"   - skip_existing: {skip_existing}")
        print(f"   - model_names: {model_names if model_names else '全部'}")
        print(f"   - skip_steps: {skip_steps if skip_steps else '无'}")
        
        results = {}
        
        try:
            # 步骤1: 访谈
            if 'interview' not in skip_steps:
                interview_result = self.step1_llm_interview(
                    force_rerun=force_interview,
                    consensus_count=consensus_count,
                    model_names=model_names,
                    skip_existing=skip_existing
                )
                
                if not interview_result:
                    print("❌ 访谈失败，终止分析")
                    return None
                
                results['interview_result'] = interview_result
            else:
                print("\n⏭️ 跳过步骤1: 访谈")
            
            # 步骤2: 数据处理
            if 'process' not in skip_steps:
                processed_file = self.step2_data_processing()
                if not processed_file:
                    print("❌ 数据处理失败，终止分析")
                    return None
                results['processed_file'] = processed_file
            else:
                print("\n⏭️ 跳过步骤2: 数据处理")
            
            # 步骤3: PCA分析
            if 'pca' not in skip_steps:
                entity_scores = self.step3_pca_analysis()
                
                if entity_scores is None:
                    print("❌ PCA分析失败，终止分析")
                    return None
                
                results['entity_scores'] = entity_scores
            else:
                print("\n⏭️ 跳过步骤3: PCA分析")
            
            # 步骤4: 可视化
            if 'visualize' not in skip_steps:
                visualizations = self.step4_visualization()
                results['visualizations'] = visualizations
            else:
                print("\n⏭️ 跳过步骤4: 可视化")
            
            # 完成
            print("\n" + "="*80)
            print("🎉 Stage1完整分析流程成功完成！")
            print("="*80)
            print(f"📊 生成的文件:")
            for key, value in results.items():
                if isinstance(value, dict):
                    print(f"   {key}: {len(value)} 个文件")
                else:
                    print(f"   {key}: {value}")
            
            return results
            
        except Exception as e:
            print(f"\n❌ 分析过程中出现错误: {e}")
            import traceback
            traceback.print_exc()
            return None


def interactive_menu():
    """交互式菜单"""
    print("\n" + "="*70)
    print("🎯 Stage1: LLM Values 分析系统")
    print("="*70)
    print("\n请选择要执行的操作：")
    print("\n1️⃣  重新全部访谈 (所有模型，完整访谈)")
    print("2️⃣  访谈新模型 (与旧数据合并计算)")
    print("3️⃣  测试小规模访谈 (2个模型，3轮共识)")
    print("4️⃣  只分析现有数据 (PCA + 可视化)")
    print("0️⃣  退出")
    print("\n" + "="*70)
    
    while True:
        try:
            choice = input("\n请输入选项 (0-4): ").strip()
            
            if choice == '0':
                print("👋 退出程序")
                return
            elif choice in ['1', '2', '3', '4']:
                return choice
            else:
                print("❌ 无效选项，请输入 0-4")
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 用户取消，退出程序")
            return None


def main():
    """主函数 - 支持命令行参数和交互式菜单"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Stage1: LLM Values完整分析',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 交互式菜单模式（推荐）
  python run_llm_values_analysis.py
  
  # 命令行模式 - 强制重新访谈
  python run_llm_values_analysis.py --force-interview
  
  # 命令行模式 - 只运行特定步骤
  python run_llm_values_analysis.py --step pca
  
  # 命令行模式 - 跳过某些步骤
  python run_llm_values_analysis.py --skip interview process
        """
    )
    
    parser.add_argument('--force-interview', action='store_true', 
                       help='强制重新运行访谈')
    parser.add_argument('--consensus-count', type=int, default=5,
                       help='每个问题的重复次数（默认5）')
    parser.add_argument('--step', 
                       choices=['interview', 'process', 'pca', 'visualize', 'all'],
                       help='运行特定步骤')
    parser.add_argument('--skip', nargs='+',
                       choices=['interview', 'process', 'pca', 'visualize'],
                       help='跳过指定的步骤')
    parser.add_argument('--interactive', action='store_true',
                       help='使用交互式菜单')
    
    args = parser.parse_args()
    
    # 创建运行器
    runner = LLMValuesAnalysisRunner()
    
    # 判断是否使用交互式模式
    use_interactive = args.interactive or (not args.step and not args.force_interview and not args.skip)
    
    if use_interactive:
        # 交互式菜单模式
        choice = interactive_menu()
        
        if choice == '1':
            # 选项1: 重新全部访谈
            print("\n🚀 选项1: 重新全部访谈")
            print("  - 访谈所有配置的模型")
            print("  - 共识轮数: 5轮")
            print("  - 然后自动运行 数据处理 → PCA → 可视化")
            
            confirm = input("\n确认执行? (y/n): ").strip().lower()
            if confirm == 'y':
                runner.run_full_analysis(
                    force_interview=True,
                    consensus_count=5,
                    skip_steps=[]
                )
            else:
                print("❌ 已取消")
        
        elif choice == '2':
            # 选项2: 访谈新模型，与旧数据合并
            print("\n🔄 选项2: 访谈新模型，与旧数据合并")
            print("  - 自动检测已完成的模型")
            print("  - 只访谈新增的模型")
            print("  - 与旧数据自动合并")
            print("  - 共识轮数: 5轮")
            print("  - 然后自动运行 数据处理 → PCA → 可视化")
            
            # 从config动态加载模型列表
            import json
            config_path = runner.project_root / 'config' / 'llm_models.json'
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                available_models_list = list(config.get('models', {}).keys())
            except Exception as e:
                print(f"❌ 加载模型配置失败: {e}")
                return
            
            # 让用户选择要测试的新模型
            print("\n可用模型:")
            model_map = {}
            for i, model in enumerate(available_models_list, 1):
                print(f"  {i}. {model}")
                model_map[str(i)] = model
            
            print(f"\n  提示: 可以输入多个模型编号（例如: 5,6,7 或 5，6，7），或直接回车访谈所有未完成的模型")
            
            model_choice = input("\n选择要测试的新模型（直接回车=所有）: ").strip()
            
            try:
                if model_choice:
                    # 用户指定了模型（支持中英文逗号）
                    model_choice = model_choice.replace('，', ',')  # 中文逗号转英文
                    selected = [model_map[c.strip()] for c in model_choice.split(',') if c.strip() in model_map]
                    if not selected:
                        print("❌ 没有选择有效的模型")
                        return
                    
                    print(f"\n已选择模型:")
                    for m in selected:
                        print(f"  - {m}")
                    
                    confirm = input("\n确认执行? (y/n): ").strip().lower()
                    if confirm == 'y':
                        runner.run_full_analysis(
                            force_interview=False,
                            consensus_count=5,
                            model_names=selected,
                            skip_existing=True,  # 启用增量访谈
                            skip_steps=[]
                        )
                    else:
                        print("❌ 已取消")
                else:
                    # 用户没有指定，访谈所有未完成的模型
                    print("\n将访谈所有未完成的模型（自动检测）")
                    confirm = input("\n确认执行? (y/n): ").strip().lower()
                    if confirm == 'y':
                        runner.run_full_analysis(
                            force_interview=False,
                            consensus_count=5,
                            model_names=None,  # 所有模型
                            skip_existing=True,  # 启用增量访谈
                            skip_steps=[]
                        )
                    else:
                        print("❌ 已取消")
            except Exception as e:
                print(f"❌ 输入错误: {e}")
        
        elif choice == '3':
            # 选项3: 测试小规模访谈
            print("\n🧪 选项3: 测试小规模访谈")
            print("  - 只访谈2个模型进行测试")
            print("  - 共识轮数: 3轮")
            
            # 从config动态加载模型列表
            import json
            config_path = runner.project_root / 'config' / 'llm_models.json'
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                available_models_list = list(config.get('models', {}).keys())
            except Exception as e:
                print(f"❌ 加载模型配置失败: {e}")
                return
            
            # 让用户选择模型
            print("\n可用模型:")
            model_map = {}
            for i, model in enumerate(available_models_list, 1):
                print(f"  {i}. {model}")
                model_map[str(i)] = model
            
            print("\n  提示: 输入2个模型编号（用逗号分隔，例如: 1,5 或 1，5）")
            
            model_choice = input("\n选择模型: ").strip()
            
            try:
                # 支持中英文逗号
                model_choice = model_choice.replace('，', ',')  # 中文逗号转英文
                selected = [model_map[c.strip()] for c in model_choice.split(',') if c.strip() in model_map]
                if len(selected) != 2:
                    print("❌ 请选择恰好2个模型")
                    return
                
                print(f"\n已选择模型:")
                for m in selected:
                    print(f"  - {m}")
                
                confirm = input("\n确认执行? (y/n): ").strip().lower()
                if confirm == 'y':
                    runner.run_full_analysis(
                        force_interview=True,
                        consensus_count=3,
                        model_names=selected,
                        skip_steps=[]
                    )
                else:
                    print("❌ 已取消")
            except Exception as e:
                print(f"❌ 输入错误: {e}")
        
        elif choice == '4':
            # 选项4: 只分析现有数据
            print("\n📊 选项4: 只分析现有数据")
            print("  - 跳过访谈步骤")
            print("  - 运行: 数据处理 → PCA → 可视化")
            
            confirm = input("\n确认执行? (y/n): ").strip().lower()
            if confirm == 'y':
                runner.run_full_analysis(
                    force_interview=False,
                    skip_steps=['interview']
                )
            else:
                print("❌ 已取消")
        
        elif choice is None:
            return
    
    else:
        # 命令行模式（保持原有逻辑）
        if args.step:
            if args.step == 'interview':
                runner.step1_llm_interview(
                    force_rerun=args.force_interview,
                    consensus_count=args.consensus_count
                )
            elif args.step == 'process':
                runner.step2_data_processing()
            elif args.step == 'pca':
                runner.step3_pca_analysis()
            elif args.step == 'visualize':
                runner.step4_visualization()
        else:
            runner.run_full_analysis(
                force_interview=args.force_interview,
                consensus_count=args.consensus_count,
                skip_steps=args.skip if args.skip else []
            )


if __name__ == "__main__":
    main()
