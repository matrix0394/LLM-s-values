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
    
    def step1_data_processing(self):
        """步骤1: 多语言Roleplay数据处理"""
        print("\n" + "="*60)
        print("📊 步骤1: 多语言Roleplay数据处理")
        print("="*60)
        
        # 查找多语言问答数据文件
        interview_data_files = list(self.data_path.glob("interview_data_*.json"))
        
        if not interview_data_files:
            print(f"❌ 多语言问答数据文件不存在")
            print(f"请确保 {self.data_path} 目录下有 interview_data_*.json 文件")
            return False
        
        # 使用最新的数据文件
        interview_data_file = max(interview_data_files, key=lambda x: x.stat().st_mtime)
        print(f"📁 使用数据文件: {interview_data_file}")
        
        try:
            # 初始化数据处理器
            processor = MultilingualRoleplayDataProcessor(data_path=str(self.data_path))
            
            # 检查是否已有处理后的数据
            processed_data_path = self.data_path / "multilingual_roleplay_processed_responses_ivs_format.pkl"
            if processed_data_path.exists():
                processed_data = pd.read_pickle(processed_data_path)
                print(f"✅ 发现已处理的数据: {len(processed_data)} 行")
                # 如果数据为空或过少，重新处理
                if len(processed_data) < 10:
                    print("📊 数据过少，重新处理原始多语言roleplay数据...")
                    processed_data = processor.process_multilingual_data_to_ivs_format(str(interview_data_file))
                    print(f"✅ 重新处理后数据: {len(processed_data)} 行")
            else:
                # 处理原始数据
                print("📊 处理原始多语言roleplay数据...")
                processed_data = processor.process_multilingual_data_to_ivs_format(str(interview_data_file))
                print(f"✅ 处理后数据: {len(processed_data)} 行")
            
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
    
    def step2_pca_analysis(self):
        """步骤2: 多语言Roleplay+IVS联合PCA分析"""
        print("\n" + "="*60)
        print("🔬 步骤2: 多语言Roleplay+IVS联合PCA分析")
        print("="*60)
        
        try:
            # 检查必要的数据文件
            required_files = [
                self.country_values_data_path / "ivs_df.pkl",
                self.country_values_data_path / "country_codes.pkl",
                self.data_path / "multilingual_roleplay_processed_responses_ivs_format.pkl"
            ]
            
            for file_path in required_files:
                if not file_path.exists():
                    print(f"❌ 缺少必要文件: {file_path}")
                    return False
            
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
            
            # 保存修复后的结果
            entity_scores_path = self.data_path / "multilingual_entity_scores_pca_fixed.pkl"
            entity_scores_fixed.to_pickle(entity_scores_path)
            print(f"💾 保存修复后的实体分数到: {entity_scores_path}")
            
            # 同时保存JSON格式
            entity_scores_json_path = self.data_path / "multilingual_entity_scores_pca_fixed.json"
            entity_scores_fixed.to_json(entity_scores_json_path, orient='records', indent=2)
            print(f"💾 保存修复后的实体分数JSON到: {entity_scores_json_path}")
            
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
    
    def step3_language_comparison_analysis(self):
        """步骤3: 英文vs本国语言效果对比分析"""
        print("\n" + "="*60)
        print("🌐 步骤3: 英文vs本国语言效果对比分析")
        print("="*60)
        
        try:
            # 加载多语言数据
            multilingual_path = self.data_path / "multilingual_entity_scores_pca_fixed.pkl"
            if not multilingual_path.exists():
                print(f"❌ 多语言PCA结果文件不存在: {multilingual_path}")
                return False
            
            # 加载英文roleplay数据
            english_path = self.roleplay_english_data_path / "roleplay_entity_scores_pca_fixed.pkl"
            if not english_path.exists():
                print(f"❌ 英文roleplay PCA结果文件不存在: {english_path}")
                return False
            
            print("\n1️⃣ 加载数据...")
            multilingual_scores = pd.read_pickle(multilingual_path)
            english_scores = pd.read_pickle(english_path)
            
            print(f"✅ 多语言数据: {len(multilingual_scores)} 个实体")
            print(f"✅ 英文数据: {len(english_scores)} 个实体")
            
            # 分离真实国家数据作为基准
            print("\n2️⃣ 准备基准数据...")
            real_countries = multilingual_scores[multilingual_scores['data_source'] == 'IVS'].copy()
            multilingual_roleplay = multilingual_scores[multilingual_scores['data_source'] == 'Multilingual'].copy()
            english_roleplay = english_scores[english_scores['data_source'] == 'Roleplay'].copy()
            
            print(f"   真实国家: {len(real_countries)} 个")
            print(f"   多语言roleplay: {len(multilingual_roleplay)} 个")
            print(f"   英文roleplay: {len(english_roleplay)} 个")
            
            # 执行距离对比分析
            print("\n3️⃣ 执行距离对比分析...")
            comparison_results = self._calculate_language_distance_comparison(
                real_countries, multilingual_roleplay, english_roleplay
            )
            
            # 保存对比结果
            comparison_path = self.results_path / "language_comparison_analysis.json"
            with open(comparison_path, 'w', encoding='utf-8') as f:
                json.dump(comparison_results, f, indent=2, ensure_ascii=False)
            print(f"💾 语言对比分析结果已保存到: {comparison_path}")
            
            # 生成对比可视化
            print("\n4️⃣ 生成对比可视化...")
            self._generate_language_comparison_visualization(comparison_results)
            
            return True
            
        except Exception as e:
            print(f"❌ 语言对比分析失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _calculate_language_distance_comparison(self, real_countries, multilingual_roleplay, english_roleplay):
        """计算英文vs本国语言的距离对比（仅对比多语言数据中的两种语言）"""
        print("📏 计算距离对比...")
        
        comparison_results = {
            'summary': {},
            'country_details': {},
            'model_performance': {},
            'language_effectiveness': {},
            'model_specific_analysis': {}  # 新增：每个模型的详细分析
        }
        
        # 处理多语言数据，分离英文和本国语言
        if 'language' in multilingual_roleplay.columns:
            native_data = multilingual_roleplay[multilingual_roleplay['language'] == 'native']
            english_data = multilingual_roleplay[multilingual_roleplay['language'] == 'english']
        else:
            print("❌ 多语言数据中没有language列，无法进行语言对比")
            return comparison_results
        
        print(f"📊 本国语言数据: {len(native_data)} 个实体")
        print(f"📊 英文数据: {len(english_data)} 个实体")
        
        # 为真实国家建立查找字典（使用Country列）
        real_country_coords = {}
        for _, row in real_countries.iterrows():
            country_name = row.get('Country', 'Unknown')
            if pd.notna(country_name) and country_name != 'Unknown':
                real_country_coords[country_name] = (row['PC1_rescaled'], row['PC2_rescaled'])
        
        print(f"📊 真实国家数量: {len(real_country_coords)}")
        
        # 获取多语言数据中的国家列表
        multilingual_countries = set(multilingual_roleplay['country_code'].dropna().unique())
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
        
        # 保存图片
        save_path = self.results_path / "language_distance_comparison.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"✅ 距离对比图已保存到: {save_path}")
    
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
        
        # 保存图片
        save_path = self.results_path / "country_level_language_comparison.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"✅ 国家级别对比图已保存到: {save_path}")
    
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
        
        # 保存HTML文件
        html_path = self.results_path / "interactive_language_comparison.html"
        fig.write_html(html_path)
        print(f"✅ 交互式语言对比图已保存到: {html_path}")
    
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
        
        # 保存静态图
        save_path = self.results_path / "model_specific_language_comparison.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        print(f"✅ 模型语言对比图已保存到: {save_path}")
        
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
        
        # 保存HTML文件
        html_path = self.results_path / "interactive_model_language_comparison.html"
        fig.write_html(html_path)
        print(f"✅ 交互式模型语言对比图已保存到: {html_path}")
    
    def step4_visualization(self):
        """步骤4: 综合可视化"""
        print("\n" + "="*60)
        print("🎨 步骤4: 综合可视化")
        print("="*60)
        
        try:
            # 检查修复后的PCA结果文件
            entity_scores_path = self.data_path / "multilingual_entity_scores_pca_fixed.pkl"
            if not entity_scores_path.exists():
                print(f"❌ 修复后的PCA结果文件不存在: {entity_scores_path}")
                return False
            
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
            static_map_path = self.results_path / "multilingual_cultural_map_corrected.png"
            self._generate_corrected_static_map(entity_scores, static_map_path)
            print(f"✅ 修正后的静态文化地图已保存到: {static_map_path}")
            
            # 生成修正后的交互式HTML地图
            print("\n3️⃣ 生成修正后的交互式HTML地图...")
            interactive_map_path = self.results_path / "multilingual_cultural_map_interactive_fixed.html"
            self._generate_corrected_interactive_map(entity_scores, interactive_map_path)
            print(f"✅ 修正后的交互式地图已保存到: {interactive_map_path}")
            
            # 初始化可视化器（用于其他图表）
            print("\n4️⃣ 生成其他分析图表...")
            visualizer = MultilingualRoleplayVisualizer(
                data_path=str(self.data_path),
                results_path=str(self.results_path)
            )
            
            # 生成语言对比图
            language_comparison_path = self.results_path / "language_model_comparison.png"
            visualizer.plot_language_comparison(data=entity_scores, save_path=str(language_comparison_path))
            print(f"✅ 语言对比图已保存到: {language_comparison_path}")
            
            # 分析多语言准确性
            print("\n5️⃣ 生成多语言统计...")
            accuracy_analysis = {
                'total_entities': len(entity_scores),
                'multilingual_entities': len(multilingual_data),
                'ivs_entities': len(ivs_data),
                'pc1_range': [float(entity_scores['PC1_rescaled'].min()), float(entity_scores['PC1_rescaled'].max())],
                'pc2_range': [float(entity_scores['PC2_rescaled'].min()), float(entity_scores['PC2_rescaled'].max())]
            }
            
            # 保存准确性分析结果
            accuracy_analysis_path = self.results_path / "multilingual_accuracy_analysis.json"
            with open(accuracy_analysis_path, 'w', encoding='utf-8') as f:
                json.dump(accuracy_analysis, f, indent=2, ensure_ascii=False)
            print(f"✅ 多语言准确性分析已保存到: {accuracy_analysis_path}")
            
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
            summary_path = self.results_path / "summary_statistics.txt"
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
            
            print(f"✅ 汇总统计已保存到: {summary_path}")
            
            # 保存文化坐标数据到results目录
            cultural_coordinates_path = self.results_path / "multilingual_cultural_coordinates.json"
            entity_scores.to_json(cultural_coordinates_path, orient='records', indent=2)
            print(f"✅ 文化坐标数据已保存到: {cultural_coordinates_path}")
            
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
                        
                        ax.scatter(
                            model_lang_data['PC1_rescaled'], 
                            model_lang_data['PC2_rescaled'],
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
                        
                        fig.add_trace(go.Scatter(
                            x=model_lang_data['PC1_rescaled'],
                            y=model_lang_data['PC2_rescaled'],
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
    
    def run_complete_analysis(self):
        """运行完整分析流程"""
        print("🚀 开始Roleplay Multilingual完整分析流程...")
        print(f"⏰ 开始时间: {datetime.now()}")
        
        success_steps = []
        
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
        
        # 数据文件
        data_files = [
            "multilingual_roleplay_processed_responses_ivs_format.pkl",
            "multilingual_entity_scores_pca_fixed.pkl", 
            "multilingual_entity_scores_pca_fixed.json"
        ]
        print("\n📊 数据文件 (data/roleplay_multilingual/):")
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


def main():
    """主函数"""
    
    print("🌐 Roleplay Multilingual Analysis Runner")
    print("=" * 60)
    
    try:
        # 创建分析运行器
        runner = RoleplayMultilingualAnalysisRunner()
        
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
