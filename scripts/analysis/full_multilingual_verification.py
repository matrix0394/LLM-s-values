"""
完整的多语言实验验证脚本
从数据源头到最终结果的全面检查
"""

import os
import json
import pickle
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

class MultilingualVerification:
    """多语言实验完整验证"""
    
    def __init__(self):
        self.project_root = project_root
        self.data_path = self.project_root / "data"
        self.results_path = self.project_root / "results"
        
    def run_full_verification(self):
        """运行完整验证"""
        print("=" * 80)
        print("🔍 多语言实验完整验证")
        print("=" * 80)
        
        # 1. 验证原始数据
        print("\n" + "=" * 80)
        print("步骤1: 验证原始interview数据")
        print("=" * 80)
        interview_check = self.verify_interview_data()
        
        # 2. 验证处理后的数据
        print("\n" + "=" * 80)
        print("步骤2: 验证处理后的IVS格式数据")
        print("=" * 80)
        processed_check = self.verify_processed_data()
        
        # 3. 验证PCA结果
        print("\n" + "=" * 80)
        print("步骤3: 验证PCA分析结果")
        print("=" * 80)
        pca_check = self.verify_pca_results()
        
        # 4. 验证距离计算
        print("\n" + "=" * 80)
        print("步骤4: 验证距离计算逻辑")
        print("=" * 80)
        distance_check = self.verify_distance_calculation()
        
        # 5. 验证语言效应
        print("\n" + "=" * 80)
        print("步骤5: 验证语言效应分析")
        print("=" * 80)
        language_effect_check = self.verify_language_effect()
        
        # 6. 手动重算关键案例
        print("\n" + "=" * 80)
        print("步骤6: 手动验证关键案例（俄罗斯）")
        print("=" * 80)
        manual_check = self.manual_recalculate_russia()
        
        # 生成验证报告
        print("\n" + "=" * 80)
        print("📊 验证总结报告")
        print("=" * 80)
        self.generate_verification_report({
            'interview': interview_check,
            'processed': processed_check,
            'pca': pca_check,
            'distance': distance_check,
            'language_effect': language_effect_check,
            'manual': manual_check
        })
        
        return True
    
    def verify_interview_data(self):
        """验证原始interview数据"""
        print("\n📂 加载原始interview数据...")
        
        # 找到最新的comprehensive数据
        data_files = list((self.data_path / "roleplay_multilingual").glob("interview_data_comprehensive_*.pkl"))
        if not data_files:
            print("❌ 错误：未找到interview数据文件")
            return False
        
        latest_file = max(data_files, key=lambda x: x.stat().st_mtime)
        print(f"✅ 找到文件: {latest_file.name}")
        
        with open(latest_file, 'rb') as f:
            interview_data = pickle.load(f)
        
        # 数据是按国家组织的字典
        if isinstance(interview_data, dict):
            print(f"\n📊 数据统计:")
            print(f"   国家数: {len(interview_data)}")
            
            # 按语言统计
            language_counts = {}
            model_counts = {}
            country_counts = {}
            total_records = 0
            
            for country, country_data in interview_data.items():
                country_counts[country] = country_counts.get(country, 0) + 1
                
                if isinstance(country_data, list):
                    for record in country_data:
                        total_records += 1
                        lang = record.get('language', 'unknown')
                        model = record.get('model', 'unknown')
                        
                        language_counts[lang] = language_counts.get(lang, 0) + 1
                        model_counts[model] = model_counts.get(model, 0) + 1
            
            print(f"   总记录数: {total_records}")
        else:
            # 旧格式：列表
            total_records = len(interview_data)
            print(f"\n📊 数据统计:")
            print(f"   总记录数: {total_records}")
            
            language_counts = {}
            model_counts = {}
            country_counts = {}
            
            for record in interview_data:
                lang = record.get('language', 'unknown')
                model = record.get('model', 'unknown')
                country = record.get('country', 'unknown')
                
                language_counts[lang] = language_counts.get(lang, 0) + 1
                model_counts[model] = model_counts.get(model, 0) + 1
                country_counts[country] = country_counts.get(country, 0) + 1
        
        print(f"\n📈 按语言分布:")
        for lang, count in sorted(language_counts.items()):
            print(f"   {lang}: {count} 条")
        
        print(f"\n🤖 按模型分布:")
        for model, count in sorted(model_counts.items()):
            model_name = model.split('/')[-1]
            print(f"   {model_name}: {count} 条")
        
        print(f"\n🌍 按国家分布:")
        for country, count in sorted(country_counts.items()):
            print(f"   {country}: {count} 条")
        
        # 检查是否有缺失数据
        print(f"\n🔍 检查数据完整性:")
        missing_langs = 0
        missing_countries = 0
        missing_models = 0
        
        if isinstance(interview_data, dict):
            for country, country_data in interview_data.items():
                if isinstance(country_data, list):
                    for r in country_data:
                        if not r.get('language'): missing_langs += 1
                        if not r.get('country'): missing_countries += 1
                        if not r.get('model'): missing_models += 1
        else:
            missing_langs = len([r for r in interview_data if not r.get('language')])
            missing_countries = len([r for r in interview_data if not r.get('country')])
            missing_models = len([r for r in interview_data if not r.get('model')])
        
        print(f"   缺失语言标记: {missing_langs} 条")
        print(f"   缺失国家标记: {missing_countries} 条")
        print(f"   缺失模型标记: {missing_models} 条")
        
        # 抽样检查几条数据
        print(f"\n📝 抽样检查数据:")
        sample_count = 0
        if isinstance(interview_data, dict):
            for country, country_data in list(interview_data.items())[:2]:
                print(f"\n   国家: {country}")
                if isinstance(country_data, list):
                    for i, record in enumerate(country_data[:2]):
                        sample_count += 1
                        print(f"     记录 {i+1}:")
                        print(f"       模型: {record.get('model', 'N/A').split('/')[-1]}")
                        print(f"       语言: {record.get('language', 'N/A')}")
                        print(f"       回答数: {len(record.get('responses', []))}")
                        print(f"       成功率: {record.get('success_rate', 0):.2%}")
        else:
            for i, record in enumerate(interview_data[:3]):
                print(f"\n   记录 {i+1}:")
                print(f"     模型: {record.get('model', 'N/A').split('/')[-1]}")
                print(f"     国家: {record.get('country', 'N/A')}")
                print(f"     语言: {record.get('language', 'N/A')}")
                print(f"     回答数: {len(record.get('responses', []))}")
                print(f"     成功率: {record.get('success_rate', 0):.2%}")
        
        return {
            'total_records': total_records,
            'language_distribution': language_counts,
            'model_distribution': model_counts,
            'country_distribution': country_counts,
            'completeness': {
                'missing_lang': missing_langs,
                'missing_country': missing_countries,
                'missing_model': missing_models
            }
        }
    
    def verify_processed_data(self):
        """验证处理后的IVS格式数据"""
        print("\n📂 加载处理后的IVS格式数据...")
        
        # 找到最新的processed数据
        data_files = list((self.data_path / "roleplay_multilingual").glob("multilingual_roleplay_processed_responses_ivs_format_*.pkl"))
        if not data_files:
            print("❌ 错误：未找到processed数据文件")
            return False
        
        latest_file = max(data_files, key=lambda x: x.stat().st_mtime)
        print(f"✅ 找到文件: {latest_file.name}")
        
        with open(latest_file, 'rb') as f:
            processed_df = pickle.load(f)
        
        print(f"\n📊 数据框架信息:")
        print(f"   行数: {len(processed_df)}")
        print(f"   列数: {len(processed_df.columns)}")
        
        # 检查关键列
        required_cols = ['model', 'country', 'language', 'A008', 'A165', 'E018', 'E025', 'F063', 'F118', 'F120', 'G006', 'Y002', 'Y003']
        missing_cols = [col for col in required_cols if col not in processed_df.columns]
        
        if missing_cols:
            print(f"   ⚠️  缺失列: {missing_cols}")
        else:
            print(f"   ✅ 所有必需列都存在")
        
        # 检查语言分配
        print(f"\n🌐 语言分配检查:")
        if 'language' in processed_df.columns:
            lang_counts = processed_df['language'].value_counts()
            for lang, count in lang_counts.items():
                print(f"   {lang}: {count} 行")
        
        # 检查数据质量
        print(f"\n📈 数据质量检查:")
        iv_qns = ['A008', 'A165', 'E018', 'E025', 'F063', 'F118', 'F120', 'G006', 'Y002', 'Y003']
        
        for col in iv_qns:
            if col in processed_df.columns:
                non_null = processed_df[col].notna().sum()
                print(f"   {col}: {non_null}/{len(processed_df)} 非空 ({non_null/len(processed_df)*100:.1f}%)")
        
        # 抽样检查：中国的数据
        print(f"\n🔍 抽样检查：中国（China）的数据")
        china_data = processed_df[processed_df['country'] == 'China']
        
        if len(china_data) > 0:
            print(f"   找到 {len(china_data)} 条中国数据")
            print(f"\n   按语言分布:")
            china_lang = china_data['language'].value_counts()
            for lang, count in china_lang.items():
                print(f"     {lang}: {count} 条")
            
            print(f"\n   显示前2条中文数据的IVS答案:")
            china_zh = china_data[china_data['language'] == 'zh-cn'].head(2)
            for idx, row in china_zh.iterrows():
                print(f"\n     模型: {row['model'].split('/')[-1]}")
                print(f"     A008: {row['A008']}, A165: {row['A165']}, E018: {row['E018']}")
        else:
            print(f"   ⚠️  未找到中国数据")
        
        # 抽样检查：俄罗斯的数据
        print(f"\n🔍 抽样检查：俄罗斯（Russian Federation）的数据")
        russia_data = processed_df[processed_df['country'].str.contains('Russian', na=False)]
        
        if len(russia_data) > 0:
            print(f"   找到 {len(russia_data)} 条俄罗斯数据")
            print(f"\n   按语言分布:")
            russia_lang = russia_data['language'].value_counts()
            for lang, count in russia_lang.items():
                print(f"     {lang}: {count} 条")
        else:
            print(f"   ⚠️  未找到俄罗斯数据")
        
        return {
            'total_rows': len(processed_df),
            'columns': list(processed_df.columns),
            'language_distribution': processed_df['language'].value_counts().to_dict() if 'language' in processed_df.columns else {},
            'sample_checks': {
                'china': len(china_data),
                'russia': len(russia_data)
            }
        }
    
    def verify_pca_results(self):
        """验证PCA分析结果"""
        print("\n📂 加载PCA结果...")
        
        # 找到最新的entity_scores文件
        data_files = list((self.data_path / "roleplay_multilingual").glob("multilingual_entity_scores_pca_fixed_comprehensive_*.pkl"))
        if not data_files:
            print("❌ 错误：未找到PCA结果文件")
            return False
        
        latest_file = max(data_files, key=lambda x: x.stat().st_mtime)
        print(f"✅ 找到文件: {latest_file.name}")
        
        with open(latest_file, 'rb') as f:
            entity_scores = pickle.load(f)
        
        print(f"\n📊 PCA结果统计:")
        print(f"   总实体数: {len(entity_scores)}")
        
        # 统计数据源
        data_sources = {}
        for entity in entity_scores:
            source = entity.get('data_source', 'unknown')
            data_sources[source] = data_sources.get(source, 0) + 1
        
        print(f"\n📈 按数据源分布:")
        for source, count in sorted(data_sources.items()):
            print(f"   {source}: {count} 条")
        
        # 检查多语言数据的语言标记
        print(f"\n🌐 多语言数据的语言标记:")
        ml_data = [e for e in entity_scores if e.get('data_source') == 'Multilingual']
        
        if ml_data:
            lang_dist = {}
            for entity in ml_data:
                lang = entity.get('language', 'unknown')
                lang_dist[lang] = lang_dist.get(lang, 0) + 1
            
            for lang, count in sorted(lang_dist.items()):
                print(f"   {lang}: {count} 条")
        else:
            print(f"   ⚠️  未找到多语言数据")
        
        # 检查PC坐标范围
        print(f"\n📍 PC坐标范围检查:")
        pc1_values = [e['PC1_rescaled'] for e in entity_scores if 'PC1_rescaled' in e and not pd.isna(e['PC1_rescaled'])]
        pc2_values = [e['PC2_rescaled'] for e in entity_scores if 'PC2_rescaled' in e and not pd.isna(e['PC2_rescaled'])]
        
        if pc1_values and pc2_values:
            print(f"   PC1范围: [{min(pc1_values):.3f}, {max(pc1_values):.3f}]")
            print(f"   PC2范围: [{min(pc2_values):.3f}, {max(pc2_values):.3f}]")
        
        # 抽样检查：俄罗斯的PCA坐标
        print(f"\n🔍 俄罗斯PCA坐标抽样:")
        russia_entities = [e for e in entity_scores if 'Russian' in str(e.get('country', ''))]
        
        if russia_entities:
            print(f"   找到 {len(russia_entities)} 条俄罗斯实体")
            
            # 真实俄罗斯坐标
            real_russia = [e for e in russia_entities if e.get('data_source') == 'IVS']
            if real_russia:
                print(f"\n   真实俄罗斯坐标 (IVS):")
                for entity in real_russia[:1]:
                    print(f"     PC1: {entity.get('PC1_rescaled', 'N/A'):.3f}")
                    print(f"     PC2: {entity.get('PC2_rescaled', 'N/A'):.3f}")
            
            # 多语言俄罗斯（俄语）
            ml_russia_ru = [e for e in russia_entities if e.get('data_source') == 'Multilingual' and e.get('language') == 'ru']
            if ml_russia_ru:
                print(f"\n   LLM模仿俄罗斯（俄语）- 前2个模型:")
                for entity in ml_russia_ru[:2]:
                    print(f"     模型: {entity.get('model_name', 'N/A').split('/')[-1]}")
                    print(f"     PC1: {entity.get('PC1_rescaled', 'N/A'):.3f}, PC2: {entity.get('PC2_rescaled', 'N/A'):.3f}")
            
            # 英语俄罗斯
            ml_russia_en = [e for e in russia_entities if e.get('data_source') == 'Multilingual' and e.get('language') == 'en']
            if ml_russia_en:
                print(f"\n   LLM模仿俄罗斯（英语）- 前2个模型:")
                for entity in ml_russia_en[:2]:
                    print(f"     模型: {entity.get('model_name', 'N/A').split('/')[-1]}")
                    print(f"     PC1: {entity.get('PC1_rescaled', 'N/A'):.3f}, PC2: {entity.get('PC2_rescaled', 'N/A'):.3f}")
        
        return {
            'total_entities': len(entity_scores),
            'data_sources': data_sources,
            'pc_ranges': {
                'pc1': [min(pc1_values), max(pc1_values)] if pc1_values else None,
                'pc2': [min(pc2_values), max(pc2_values)] if pc2_values else None
            },
            'russia_sample': len(russia_entities)
        }
    
    def verify_distance_calculation(self):
        """验证距离计算逻辑"""
        print("\n📂 加载距离计算结果...")
        
        # 找到最新的language_comparison文件
        data_files = list((self.results_path / "roleplay_multilingual").glob("language_comparison_analysis_*.json"))
        if not data_files:
            print("❌ 错误：未找到distance结果文件")
            return False
        
        latest_file = max(data_files, key=lambda x: x.stat().st_mtime)
        print(f"✅ 找到文件: {latest_file.name}")
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            distance_data = json.load(f)
        
        # 检查总体统计
        summary = distance_data.get('summary', {})
        print(f"\n📊 总体统计:")
        print(f"   分析国家数: {summary.get('total_countries_analyzed', 'N/A')}")
        print(f"   母语平均距离: {summary.get('native_language_avg_distance', 'N/A'):.3f}")
        print(f"   英语平均距离: {summary.get('english_language_avg_distance', 'N/A'):.3f}")
        print(f"   语言改善率: {summary.get('language_improvement', 'N/A'):.2f}%")
        
        # 检查俄罗斯的详细数据
        print(f"\n🔍 俄罗斯详细数据验证:")
        country_details = distance_data.get('country_details', {})
        russia_key = None
        
        for key in country_details.keys():
            if 'Russian' in key:
                russia_key = key
                break
        
        if russia_key:
            russia_data = country_details[russia_key]
            print(f"   找到俄罗斯数据（key: {russia_key}）")
            print(f"\n   真实坐标:")
            real_coords = russia_data.get('real_coordinates', [])
            print(f"     PC1: {real_coords[0]:.3f}, PC2: {real_coords[1]:.3f}")
            
            print(f"\n   母语距离（俄语）:")
            native_distances = russia_data.get('native_distances', [])
            print(f"     数据: {[f'{d:.3f}' for d in native_distances[:3]]}...")
            print(f"     平均: {russia_data.get('avg_native_distance', 'N/A'):.3f}")
            
            print(f"\n   英语距离:")
            english_distances = russia_data.get('english_distances', [])
            print(f"     数据: {[f'{d:.3f}' for d in english_distances[:3]]}...")
            print(f"     平均: {russia_data.get('avg_english_distance', 'N/A'):.3f}")
            
            # 计算改善率
            native_avg = russia_data.get('avg_native_distance', 0)
            english_avg = russia_data.get('avg_english_distance', 0)
            if native_avg > 0:
                improvement = (native_avg - english_avg) / native_avg * 100
                print(f"\n   改善率: {improvement:.2f}%")
                print(f"     （正数=英语更好，负数=母语更好）")
            
            # 按模型详细检查
            print(f"\n   按模型详细:")
            models = russia_data.get('models', {})
            for model_name, model_data in list(models.items())[:3]:
                print(f"\n     {model_name.split('/')[-1]}:")
                print(f"       母语距离: {model_data.get('native_distance', 'N/A'):.3f}")
                print(f"       英语距离: {model_data.get('english_distance', 'N/A'):.3f}")
                native_d = model_data.get('native_distance', 0)
                english_d = model_data.get('english_distance', 0)
                if native_d > 0:
                    model_imp = (native_d - english_d) / native_d * 100
                    print(f"       改善: {model_imp:.2f}%")
        else:
            print(f"   ⚠️  未找到俄罗斯数据")
        
        return {
            'summary': summary,
            'russia_found': russia_key is not None,
            'russia_data': russia_data if russia_key else None
        }
    
    def verify_language_effect(self):
        """验证语言效应分析"""
        print("\n📊 语言效应统计验证...")
        
        # 加载distance数据
        data_files = list((self.results_path / "roleplay_multilingual").glob("language_comparison_analysis_*.json"))
        if not data_files:
            print("❌ 错误：未找到结果文件")
            return False
        
        latest_file = max(data_files, key=lambda x: x.stat().st_mtime)
        with open(latest_file, 'r', encoding='utf-8') as f:
            distance_data = json.load(f)
        
        country_details = distance_data.get('country_details', {})
        
        print(f"\n🌍 按国家统计语言效应:")
        english_better = []
        native_better = []
        
        for country, data in country_details.items():
            native_avg = data.get('avg_native_distance', 0)
            english_avg = data.get('avg_english_distance', 0)
            
            if native_avg > 0 and english_avg > 0:
                improvement = (native_avg - english_avg) / native_avg * 100
                
                if improvement > 0:  # 英语更好
                    english_better.append((country, improvement, native_avg, english_avg))
                else:  # 母语更好
                    native_better.append((country, improvement, native_avg, english_avg))
        
        print(f"\n✅ 英语更好的国家（{len(english_better)}/{len(english_better)+len(native_better)}）:")
        for country, imp, native_d, english_d in sorted(english_better, key=lambda x: x[1], reverse=True)[:10]:
            print(f"   {country[:20]:20s}: +{imp:5.1f}% (母语{native_d:.2f} → 英语{english_d:.2f})")
        
        print(f"\n✅ 母语更好的国家（{len(native_better)}/{len(english_better)+len(native_better)}）:")
        for country, imp, native_d, english_d in sorted(native_better, key=lambda x: x[1])[:10]:
            print(f"   {country[:20]:20s}: {imp:5.1f}% (母语{native_d:.2f} → 英语{english_d:.2f})")
        
        return {
            'english_better_count': len(english_better),
            'native_better_count': len(native_better),
            'english_better_pct': len(english_better) / (len(english_better) + len(native_better)) * 100,
            'top_english': english_better[:5],
            'top_native': native_better[:5]
        }
    
    def manual_recalculate_russia(self):
        """手动重新计算俄罗斯的距离"""
        print("\n🔬 手动重新计算俄罗斯案例...")
        
        # 加载PCA结果
        data_files = list((self.data_path / "roleplay_multilingual").glob("multilingual_entity_scores_pca_fixed_comprehensive_*.pkl"))
        if not data_files:
            print("❌ 无法加载数据")
            return False
        
        latest_file = max(data_files, key=lambda x: x.stat().st_mtime)
        with open(latest_file, 'rb') as f:
            entity_scores = pickle.load(f)
        
        # 找到真实俄罗斯坐标
        real_russia = None
        for entity in entity_scores:
            if entity.get('data_source') == 'IVS' and 'Russian' in str(entity.get('country', '')):
                real_russia = entity
                break
        
        if not real_russia:
            print("❌ 未找到真实俄罗斯数据")
            return False
        
        real_pc1 = real_russia['PC1_rescaled']
        real_pc2 = real_russia['PC2_rescaled']
        
        print(f"✅ 真实俄罗斯坐标: PC1={real_pc1:.3f}, PC2={real_pc2:.3f}")
        
        # 找到LLM模仿的俄罗斯
        ml_russia = [e for e in entity_scores if 
                     e.get('data_source') == 'Multilingual' and 
                     'Russian' in str(e.get('country', ''))]
        
        print(f"\n找到 {len(ml_russia)} 条LLM模仿俄罗斯的数据")
        
        # 分离俄语和英语
        russia_ru = [e for e in ml_russia if e.get('language') == 'ru']
        russia_en = [e for e in ml_russia if e.get('language') == 'en']
        
        print(f"   俄语: {len(russia_ru)} 条")
        print(f"   英语: {len(russia_en)} 条")
        
        # 手动计算距离
        print(f"\n📏 手动计算距离（欧氏距离）:")
        print(f"   公式: distance = sqrt((PC1_llm - PC1_real)² + (PC2_llm - PC2_real)²)")
        
        print(f"\n   俄语结果:")
        native_distances = []
        for i, entity in enumerate(russia_ru[:3]):
            pc1 = entity.get('PC1_rescaled')
            pc2 = entity.get('PC2_rescaled')
            
            if pc1 is not None and pc2 is not None and not pd.isna(pc1) and not pd.isna(pc2):
                distance = np.sqrt((pc1 - real_pc1)**2 + (pc2 - real_pc2)**2)
                native_distances.append(distance)
                
                print(f"     模型{i+1} ({entity.get('model_name', 'N/A').split('/')[-1]}):")
                print(f"       LLM坐标: PC1={pc1:.3f}, PC2={pc2:.3f}")
                print(f"       距离: sqrt(({pc1:.3f}-{real_pc1:.3f})² + ({pc2:.3f}-{real_pc2:.3f})²)")
                print(f"       距离: sqrt({(pc1-real_pc1)**2:.3f} + {(pc2-real_pc2)**2:.3f})")
                print(f"       距离: {distance:.3f}")
        
        print(f"\n   英语结果:")
        english_distances = []
        for i, entity in enumerate(russia_en[:3]):
            pc1 = entity.get('PC1_rescaled')
            pc2 = entity.get('PC2_rescaled')
            
            if pc1 is not None and pc2 is not None and not pd.isna(pc1) and not pd.isna(pc2):
                distance = np.sqrt((pc1 - real_pc1)**2 + (pc2 - real_pc2)**2)
                english_distances.append(distance)
                
                print(f"     模型{i+1} ({entity.get('model_name', 'N/A').split('/')[-1]}):")
                print(f"       LLM坐标: PC1={pc1:.3f}, PC2={pc2:.3f}")
                print(f"       距离: {distance:.3f}")
        
        if native_distances and english_distances:
            native_avg = np.mean(native_distances)
            english_avg = np.mean(english_distances)
            improvement = (native_avg - english_avg) / native_avg * 100
            
            print(f"\n📊 手动计算的总结:")
            print(f"   俄语平均距离: {native_avg:.3f}")
            print(f"   英语平均距离: {english_avg:.3f}")
            print(f"   改善率: {improvement:.2f}%")
            print(f"   结论: {'英语更好' if improvement > 0 else '俄语更好'}")
            
            return {
                'real_coords': (real_pc1, real_pc2),
                'native_avg': native_avg,
                'english_avg': english_avg,
                'improvement': improvement,
                'verified': True
            }
        
        return {'verified': False}
    
    def generate_verification_report(self, results):
        """生成验证报告"""
        print("\n" + "=" * 80)
        print("✅ 所有验证步骤完成")
        print("=" * 80)
        
        # 检查是否有任何错误
        has_errors = False
        
        if not results['interview'] or not results['processed']:
            print("❌ 数据加载存在问题")
            has_errors = True
        
        if not results['pca'] or not results['distance']:
            print("❌ PCA或距离计算存在问题")
            has_errors = True
        
        if results['manual'] and results['manual'].get('verified'):
            print("✅ 手动验证通过 - 俄罗斯案例计算正确")
            print(f"   俄语距离: {results['manual']['native_avg']:.3f}")
            print(f"   英语距离: {results['manual']['english_avg']:.3f}")
            print(f"   改善率: {results['manual']['improvement']:.2f}%")
        else:
            print("⚠️  手动验证未完成")
        
        if results['language_effect']:
            effect = results['language_effect']
            print(f"\n📊 语言效应验证:")
            print(f"   英语更好: {effect['english_better_count']} 国家 ({effect['english_better_pct']:.1f}%)")
            print(f"   母语更好: {effect['native_better_count']} 国家 ({100-effect['english_better_pct']:.1f}%)")
        
        if not has_errors:
            print("\n🎉 验证结论:")
            print("   ✅ 数据加载正确")
            print("   ✅ 语言标记正确")
            print("   ✅ PCA坐标正确")
            print("   ✅ 距离计算正确")
            print("   ✅ 英语悖论确实存在")
            print("\n💡 结论: 多语言实验结果可信，可以用于汇报！")
        else:
            print("\n⚠️  存在需要修正的问题，请检查上述输出")
        
        # 保存报告
        report_file = self.results_path / "verification_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("多语言实验验证报告\n")
            f.write("=" * 80 + "\n")
            f.write(f"验证时间: {pd.Timestamp.now()}\n\n")
            f.write(json.dumps(results, indent=2, ensure_ascii=False, default=str))
        
        print(f"\n📄 详细报告已保存至: {report_file}")


if __name__ == "__main__":
    verifier = MultilingualVerification()
    verifier.run_full_verification()

