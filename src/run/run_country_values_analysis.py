#!/usr/bin/env python3
"""
完整的Country Values分析运行脚本
从最开始的数据处理到PCA分析再到可视化的完整流程

数据存储规则：
- 处理后的数据和PCA计算结果 -> data/country_values/
- 输出图片和文化坐标数据 -> results/country_values/
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
from src.country_values.data_processing import DataProcessor
from src.country_values.pca_analysis import CorePCAAnalyzer
from src.country_values.visualization import CulturalMapVisualizer


class CountryValuesAnalysisRunner:
    """Country Values完整分析运行器"""
    
    def __init__(self, project_root=None):
        if project_root is None:
            self.project_root = Path(__file__).parent.parent.parent
        else:
            self.project_root = Path(project_root)
        
        # 设置路径
        self.data_path = self.project_root / "data" / "country_values"
        self.results_path = self.project_root / "results" / "country_values"
        self.raw_data_path = self.project_root / "data" / "raw"
        
        # 确保目录存在
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.results_path.mkdir(parents=True, exist_ok=True)
        
        print(f"🏠 项目根目录: {self.project_root}")
        print(f"📁 数据目录: {self.data_path}")
        print(f"📁 结果目录: {self.results_path}")
    
    def step1_data_processing(self):
        """步骤1: 数据处理"""
        print("\n" + "="*60)
        print("📊 步骤1: 数据处理")
        print("="*60)
        
        # 检查原始数据文件是否存在
        ivs_file = self.raw_data_path / "Integrated_values_surveys_1981-2022.sav"
        if not ivs_file.exists():
            print(f"❌ 原始数据文件不存在: {ivs_file}")
            print("请确保原始数据文件位于 data/raw/ 目录下")
            return False
        
        # 初始化数据处理器
        processor = DataProcessor(data_path=str(self.data_path))
        
        try:
            # 1. 加载IVS数据
            print("\n1️⃣ 加载IVS数据...")
            ivs_df = processor.load_ivs_data(str(ivs_file))
            print(f"✅ 成功加载数据: {len(ivs_df)} 行, {len(ivs_df.columns)} 列")
            
            # 2. 创建country_codes.pkl（如果不存在）
            # 统一保存到 config/country/ 目录
            print("\n2️⃣ 检查并创建country_codes.pkl...")
            config_country_path = self.project_root / "config" / "country" / "country_codes.pkl"
            if not config_country_path.exists():
                country_codes = processor.create_country_codes()
                print(f"✅ 创建了country_codes.pkl，包含 {len(country_codes)} 个国家")
            else:
                print("✅ country_codes.pkl 已存在于 config/country/")
            
            # 3. 获取过滤后的数据
            print("\n3️⃣ 获取过滤后的数据...")
            filtered_data = processor.get_filtered_data()
            print(f"✅ 过滤后数据: {len(filtered_data)} 行")
            
            # 4. 保存数据
            print("\n4️⃣ 保存数据...")
            processor.save_data()
            print("✅ 数据保存完成")
            
            # 5. 显示数据概览
            print("\n5️⃣ 数据概览:")
            print(f"原始数据形状: {ivs_df.shape}")
            print(f"过滤后数据形状: {filtered_data.shape}")
            unique_countries = sorted(filtered_data['country_code'].unique())
            print(f"包含的国家数量: {len(unique_countries)}")
            print(f"国家代码: {unique_countries}")
            
            return True
            
        except Exception as e:
            print(f"❌ 数据处理失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def step2_pca_analysis(self):
        """步骤2: PCA分析"""
        print("\n" + "="*60)
        print("🔬 步骤2: PCA分析")
        print("="*60)
        
        try:
            # 检查必要的数据文件
            # country_codes.pkl 统一放在 config/country/ 目录
            config_country_path = self.project_root / "config" / "country" / "country_codes.pkl"
            required_files = [
                self.data_path / "ivs_df.pkl",
                config_country_path,  # 统一从 config/country/ 检查
                self.data_path / "valid_data.pkl"
            ]
            
            for file_path in required_files:
                if not file_path.exists():
                    print(f"❌ 缺少必要文件: {file_path}")
                    return False
            
            # 使用新的PCA分析器
            print("\n1️⃣ 初始化PCA分析器...")
            analyzer = CorePCAAnalyzer(data_path=str(self.data_path))
            
            # 运行完整分析
            print("\n2️⃣ 运行PCA分析...")
            country_scores = analyzer.run_full_analysis()
            
            print(f"\n✅ PCA分析完成！")
            print(f"📊 生成了 {len(country_scores)} 个国家的PCA分数")
            
            # 输出统计信息
            if 'PC1_rescaled' in country_scores.columns:
                print(f"PC1范围: [{country_scores['PC1_rescaled'].min():.2f}, {country_scores['PC1_rescaled'].max():.2f}]")
            if 'PC2_rescaled' in country_scores.columns:
                print(f"PC2范围: [{country_scores['PC2_rescaled'].min():.2f}, {country_scores['PC2_rescaled'].max():.2f}]")
            if 'Cultural Region' in country_scores.columns:
                print(f"\n文化区域分布:")
                print(country_scores['Cultural Region'].value_counts())
            
            return True
            
        except Exception as e:
            print(f"❌ PCA分析失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def step3_visualization(self):
        """步骤3: 可视化"""
        print("\n" + "="*60)
        print("🎨 步骤3: 可视化")
        print("="*60)
        
        try:
            # 检查PCA结果文件
            country_scores_path = self.data_path / "country_scores_pca.pkl"
            if not country_scores_path.exists():
                print(f"❌ PCA结果文件不存在: {country_scores_path}")
                return False
            
            # 初始化可视化器
            print("\n1️⃣ 初始化可视化器...")
            visualizer = CulturalMapVisualizer(data_path=str(self.data_path))
            
            # 加载国家分数数据
            print("\n2️⃣ 加载国家分数数据...")
            country_scores_pca = visualizer.load_country_scores()
            print(f"✅ 成功加载国家分数数据: {len(country_scores_pca)} 个国家")
            
            # 绘制文化地图
            print("\n3️⃣ 绘制文化地图...")
            cultural_map_path = self.results_path / "cultural_map.png"
            visualizer.plot_cultural_map(save_path=str(cultural_map_path))
            print(f"✅ 文化地图已保存到: {cultural_map_path}")
            
            # 绘制决策边界
            print("\n4️⃣ 绘制决策边界...")
            decision_boundary_path = self.results_path / "decision_boundary.png"
            visualizer.plot_decision_boundary(save_path=str(decision_boundary_path))
            print(f"✅ 决策边界图已保存到: {decision_boundary_path}")
            
            # 生成汇总统计
            print("\n5️⃣ 生成汇总统计...")
            summary_stats = visualizer.create_summary_statistics()
            
            # 保存汇总统计到文件
            summary_path = self.results_path / "summary_statistics.txt"
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write("Country Values Analysis Summary\n")
                f.write("="*50 + "\n\n")
                f.write(f"Total countries: {len(country_scores_pca)}\n\n")
                
                if 'Cultural Region' in country_scores_pca.columns:
                    f.write("Countries by Cultural Region:\n")
                    region_counts = country_scores_pca['Cultural Region'].value_counts()
                    for region, count in region_counts.items():
                        f.write(f"  {region}: {count}\n")
                    f.write("\n")
                
                f.write("Principal Component Statistics:\n")
                f.write(f"PC1 range: [{country_scores_pca['PC1_rescaled'].min():.2f}, {country_scores_pca['PC1_rescaled'].max():.2f}]\n")
                f.write(f"PC2 range: [{country_scores_pca['PC2_rescaled'].min():.2f}, {country_scores_pca['PC2_rescaled'].max():.2f}]\n\n")
                
                f.write("Detailed Statistics:\n")
                f.write(str(summary_stats))
            
            print(f"✅ 汇总统计已保存到: {summary_path}")
            
            # 保存文化坐标数据到results目录
            cultural_coordinates_path = self.results_path / "cultural_coordinates.json"
            country_scores_pca.to_json(cultural_coordinates_path, orient='records', indent=2)
            print(f"✅ 文化坐标数据已保存到: {cultural_coordinates_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ 可视化失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_complete_analysis(self):
        """运行完整分析流程"""
        print("🚀 开始Country Values完整分析流程...")
        print(f"⏰ 开始时间: {datetime.now()}")
        
        success_steps = []
        
        # 步骤1: 数据处理
        if self.step1_data_processing():
            success_steps.append("数据处理")
        else:
            print("❌ 数据处理失败，停止分析")
            return False
        
        # 步骤2: PCA分析
        if self.step2_pca_analysis():
            success_steps.append("PCA分析")
        else:
            print("❌ PCA分析失败，停止分析")
            return False
        
        # 步骤3: 可视化
        if self.step3_visualization():
            success_steps.append("可视化")
        else:
            print("❌ 可视化失败，但前面步骤成功")
        
        # 总结
        print("\n" + "="*60)
        print("🎉 Country Values分析完成!")
        print("="*60)
        print(f"✅ 成功完成的步骤: {', '.join(success_steps)}")
        print(f"📁 数据文件位置: {self.data_path}")
        print(f"📁 结果文件位置: {self.results_path}")
        print(f"⏰ 完成时间: {datetime.now()}")
        
        # 显示生成的文件
        print("\n📋 生成的文件:")
        
        # 数据文件
        data_files = [
            "ivs_df.pkl", "variable_view.pkl", "valid_data.pkl", 
            "country_codes.pkl", "country_scores_pca.pkl", "country_scores_pca.json"
        ]
        print("\n📊 数据文件 (data/country_values/):")
        for file_name in data_files:
            file_path = self.data_path / file_name
            if file_path.exists():
                print(f"  ✅ {file_name}")
            else:
                print(f"  ❌ {file_name}")
        
        # 结果文件
        result_files = [
            "cultural_map.png", "decision_boundary.png", 
            "summary_statistics.txt", "cultural_coordinates.json"
        ]
        print("\n🎨 结果文件 (results/country_values/):")
        for file_name in result_files:
            file_path = self.results_path / file_name
            if file_path.exists():
                print(f"  ✅ {file_name}")
            else:
                print(f"  ❌ {file_name}")
        
        return len(success_steps) == 3


def main():
    """主函数"""
    
    print("🌍 Country Values Analysis Runner")
    print("=" * 60)
    
    try:
        # 创建分析运行器
        runner = CountryValuesAnalysisRunner()
        
        # 运行完整分析
        success = runner.run_complete_analysis()
        
        if success:
            print("\n🎊 所有分析步骤都成功完成!")
            return 0
        else:
            print("\n⚠️ 部分分析步骤失败，请检查错误信息")
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
