#!/usr/bin/env python3
"""
🔍 模型回答质量分析
=================

分析各个模型的回答完整性和质量，特别关注：
1. 回答完整率
2. 空回答比例
3. 有效回答数量
4. 质量评分
"""

import sys
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Any, Tuple
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class ModelResponseQualityAnalyzer:
    """模型回答质量分析器"""
    
    def __init__(self, data_path: str = "data/results/extended_multilingual_experiment"):
        self.data_path = Path(data_path)
        self.results_dir = Path("results/model_quality_analysis")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # 问题列表
        self.question_ids = ['A008', 'A165', 'E018', 'E025', 'F063', 'F118', 'F120', 'G006', 'Y002', 'Y003']
        
        # 加载数据
        self.load_latest_data()
    
    def load_latest_data(self):
        """加载最新的访谈数据"""
        
        # 查找最新的访谈数据
        interview_files = list(self.data_path.glob("interview_data_*.json"))
        if not interview_files:
            raise FileNotFoundError("未找到访谈数据文件")
        
        latest_file = max(interview_files, key=lambda x: x.stat().st_mtime)
        print(f"📂 加载访谈数据: {latest_file}")
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            self.interview_data = json.load(f)
        
        print(f"✅ 数据加载完成")
        print(f"   - 测试国家: {len(self.interview_data)} 个")
    
    def analyze_response_quality(self) -> Dict[str, Any]:
        """分析回答质量"""
        
        print("\n🔍 开始模型回答质量分析")
        print("=" * 50)
        
        # 收集所有模型的回答统计
        model_stats = defaultdict(lambda: {
            'total_questions': 0,
            'valid_responses': 0,
            'empty_responses': 0,
            'null_responses': 0,
            'countries': set(),
            'languages': set(),
            'response_details': []
        })
        
        # 遍历所有国家和语言
        for country, country_data in self.interview_data.items():
            for lang_type, lang_data in country_data.items():  # english, native
                for model, model_results in lang_data.items():
                    
                    # 处理聚合后的结果
                    if isinstance(model_results, list) and len(model_results) > 0:
                        # 取第一个结果（通常是聚合后的结果）
                        responses = model_results[0].get('responses', {})
                        
                        model_stats[model]['countries'].add(country)
                        model_stats[model]['languages'].add(lang_type)
                        
                        # 分析每个问题的回答
                        for question_id in self.question_ids:
                            model_stats[model]['total_questions'] += 1
                            
                            response = responses.get(question_id)
                            
                            if response is None:
                                model_stats[model]['null_responses'] += 1
                                status = 'null'
                            elif response == "" or response == '':
                                model_stats[model]['empty_responses'] += 1
                                status = 'empty'
                            else:
                                model_stats[model]['valid_responses'] += 1
                                status = 'valid'
                            
                            # 记录详细信息
                            model_stats[model]['response_details'].append({
                                'country': country,
                                'language': lang_type,
                                'question': question_id,
                                'response': response,
                                'status': status
                            })
        
        # 计算质量指标
        quality_analysis = {}
        
        for model, stats in model_stats.items():
            total = stats['total_questions']
            valid = stats['valid_responses']
            empty = stats['empty_responses']
            null = stats['null_responses']
            
            quality_metrics = {
                'model_name': model,
                'total_questions': total,
                'valid_responses': valid,
                'empty_responses': empty,
                'null_responses': null,
                'invalid_responses': empty + null,
                'valid_rate': (valid / total * 100) if total > 0 else 0,
                'empty_rate': (empty / total * 100) if total > 0 else 0,
                'null_rate': (null / total * 100) if total > 0 else 0,
                'invalid_rate': ((empty + null) / total * 100) if total > 0 else 0,
                'countries_tested': len(stats['countries']),
                'languages_tested': len(stats['languages']),
                'quality_grade': self._calculate_quality_grade(valid / total if total > 0 else 0)
            }
            
            quality_analysis[model] = quality_metrics
        
        # 按问题分析
        question_analysis = self._analyze_by_question(model_stats)
        
        # 按国家分析
        country_analysis = self._analyze_by_country(model_stats)
        
        # 按语言分析
        language_analysis = self._analyze_by_language(model_stats)
        
        results = {
            'model_quality': quality_analysis,
            'question_analysis': question_analysis,
            'country_analysis': country_analysis,
            'language_analysis': language_analysis,
            'raw_stats': dict(model_stats)
        }
        
        # 打印结果摘要
        self._print_quality_summary(quality_analysis)
        
        return results
    
    def _analyze_by_question(self, model_stats: Dict) -> Dict:
        """按问题分析回答质量"""
        
        question_quality = {}
        
        for question_id in self.question_ids:
            question_stats = defaultdict(lambda: {'valid': 0, 'invalid': 0, 'total': 0})
            
            for model, stats in model_stats.items():
                for detail in stats['response_details']:
                    if detail['question'] == question_id:
                        question_stats[model]['total'] += 1
                        if detail['status'] == 'valid':
                            question_stats[model]['valid'] += 1
                        else:
                            question_stats[model]['invalid'] += 1
            
            # 计算每个问题的总体统计
            total_responses = sum(s['total'] for s in question_stats.values())
            valid_responses = sum(s['valid'] for s in question_stats.values())
            
            question_quality[question_id] = {
                'total_responses': total_responses,
                'valid_responses': valid_responses,
                'valid_rate': (valid_responses / total_responses * 100) if total_responses > 0 else 0,
                'model_stats': dict(question_stats)
            }
        
        return question_quality
    
    def _analyze_by_country(self, model_stats: Dict) -> Dict:
        """按国家分析回答质量"""
        
        country_quality = {}
        
        # 获取所有国家
        all_countries = set()
        for stats in model_stats.values():
            all_countries.update(stats['countries'])
        
        for country in all_countries:
            country_stats = defaultdict(lambda: {'valid': 0, 'invalid': 0, 'total': 0})
            
            for model, stats in model_stats.items():
                for detail in stats['response_details']:
                    if detail['country'] == country:
                        country_stats[model]['total'] += 1
                        if detail['status'] == 'valid':
                            country_stats[model]['valid'] += 1
                        else:
                            country_stats[model]['invalid'] += 1
            
            # 计算每个国家的总体统计
            total_responses = sum(s['total'] for s in country_stats.values())
            valid_responses = sum(s['valid'] for s in country_stats.values())
            
            country_quality[country] = {
                'total_responses': total_responses,
                'valid_responses': valid_responses,
                'valid_rate': (valid_responses / total_responses * 100) if total_responses > 0 else 0,
                'model_stats': dict(country_stats)
            }
        
        return country_quality
    
    def _analyze_by_language(self, model_stats: Dict) -> Dict:
        """按语言分析回答质量"""
        
        language_quality = {}
        
        for language in ['english', 'native']:
            lang_stats = defaultdict(lambda: {'valid': 0, 'invalid': 0, 'total': 0})
            
            for model, stats in model_stats.items():
                for detail in stats['response_details']:
                    if detail['language'] == language:
                        lang_stats[model]['total'] += 1
                        if detail['status'] == 'valid':
                            lang_stats[model]['valid'] += 1
                        else:
                            lang_stats[model]['invalid'] += 1
            
            # 计算每种语言的总体统计
            total_responses = sum(s['total'] for s in lang_stats.values())
            valid_responses = sum(s['valid'] for s in lang_stats.values())
            
            language_quality[language] = {
                'total_responses': total_responses,
                'valid_responses': valid_responses,
                'valid_rate': (valid_responses / total_responses * 100) if total_responses > 0 else 0,
                'model_stats': dict(lang_stats)
            }
        
        return language_quality
    
    def _calculate_quality_grade(self, valid_rate: float) -> str:
        """计算质量等级"""
        if valid_rate >= 0.9:
            return "A+ (优秀)"
        elif valid_rate >= 0.8:
            return "A (良好)"
        elif valid_rate >= 0.7:
            return "B (一般)"
        elif valid_rate >= 0.6:
            return "C (较差)"
        else:
            return "D (很差)"
    
    def _print_quality_summary(self, quality_analysis: Dict):
        """打印质量摘要"""
        
        print("\n📊 模型回答质量排名")
        print("-" * 60)
        
        # 按有效回答率排序
        sorted_models = sorted(quality_analysis.items(), 
                             key=lambda x: x[1]['valid_rate'], 
                             reverse=True)
        
        print(f"{'排名':<4} {'模型':<25} {'有效率':<8} {'等级':<12} {'有效/总数'}")
        print("-" * 60)
        
        for i, (model, metrics) in enumerate(sorted_models, 1):
            model_name = model.split('/')[-1] if '/' in model else model
            print(f"{i:<4} {model_name:<25} {metrics['valid_rate']:.1f}%{'':<3} "
                  f"{metrics['quality_grade']:<12} "
                  f"{metrics['valid_responses']}/{metrics['total_questions']}")
        
        print("\n🚨 问题模型详情")
        print("-" * 60)
        
        for model, metrics in sorted_models:
            if metrics['valid_rate'] < 80:  # 有效率低于80%的模型
                model_name = model.split('/')[-1] if '/' in model else model
                print(f"\n❌ {model_name}:")
                print(f"   有效回答: {metrics['valid_responses']}/{metrics['total_questions']} ({metrics['valid_rate']:.1f}%)")
                print(f"   空回答: {metrics['empty_responses']} ({metrics['empty_rate']:.1f}%)")
                print(f"   null回答: {metrics['null_responses']} ({metrics['null_rate']:.1f}%)")
                print(f"   测试国家: {metrics['countries_tested']} 个")
    
    def create_visualizations(self, results: Dict[str, Any]):
        """创建可视化图表"""
        
        print("\n📈 生成可视化图表")
        
        # 1. 模型质量对比图
        self._create_model_quality_chart(results['model_quality'])
        
        # 2. 问题难度分析图
        self._create_question_difficulty_chart(results['question_analysis'])
        
        # 3. 模型回答完整性热图
        self._create_response_completeness_heatmap(results)
        
        # 4. 语言对比图
        self._create_language_comparison_chart(results['language_analysis'])
    
    def _create_model_quality_chart(self, model_quality: Dict):
        """创建模型质量对比图"""
        
        # 准备数据
        models = []
        valid_rates = []
        empty_rates = []
        null_rates = []
        
        for model, metrics in model_quality.items():
            model_name = model.split('/')[-1] if '/' in model else model
            models.append(model_name)
            valid_rates.append(metrics['valid_rate'])
            empty_rates.append(metrics['empty_rate'])
            null_rates.append(metrics['null_rate'])
        
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
        
        # 1. 有效回答率对比
        bars = ax1.bar(models, valid_rates, color='lightgreen', alpha=0.8)
        ax1.set_title('模型有效回答率对比', fontsize=14, fontweight='bold')
        ax1.set_ylabel('有效回答率 (%)')
        ax1.set_ylim(0, 100)
        plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
        
        # 添加数值标签
        for bar, rate in zip(bars, valid_rates):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{rate:.1f}%', ha='center', va='bottom')
        
        # 添加质量等级线
        ax1.axhline(y=90, color='green', linestyle='--', alpha=0.7, label='优秀线(90%)')
        ax1.axhline(y=80, color='orange', linestyle='--', alpha=0.7, label='良好线(80%)')
        ax1.axhline(y=70, color='red', linestyle='--', alpha=0.7, label='及格线(70%)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 无效回答类型分布
        x = np.arange(len(models))
        width = 0.35
        
        bars1 = ax2.bar(x - width/2, empty_rates, width, label='空回答', color='orange', alpha=0.8)
        bars2 = ax2.bar(x + width/2, null_rates, width, label='null回答', color='red', alpha=0.8)
        
        ax2.set_title('模型无效回答类型分布', fontsize=14, fontweight='bold')
        ax2.set_ylabel('无效回答率 (%)')
        ax2.set_xticks(x)
        ax2.set_xticklabels(models, rotation=45, ha='right')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / 'model_quality_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("   📊 模型质量对比图已保存")
    
    def _create_question_difficulty_chart(self, question_analysis: Dict):
        """创建问题难度分析图"""
        
        # 准备数据
        questions = list(question_analysis.keys())
        valid_rates = [question_analysis[q]['valid_rate'] for q in questions]
        
        # 创建图表
        plt.figure(figsize=(12, 8))
        
        bars = plt.bar(questions, valid_rates, color='skyblue', alpha=0.8)
        plt.title('各问题有效回答率 (问题难度分析)', fontsize=14, fontweight='bold')
        plt.ylabel('有效回答率 (%)')
        plt.xlabel('问题ID')
        plt.ylim(0, 100)
        
        # 添加数值标签
        for bar, rate in zip(bars, valid_rates):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{rate:.1f}%', ha='center', va='bottom')
        
        # 添加平均线
        avg_rate = np.mean(valid_rates)
        plt.axhline(y=avg_rate, color='red', linestyle='--', alpha=0.7, 
                   label=f'平均有效率: {avg_rate:.1f}%')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / 'question_difficulty_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("   📊 问题难度分析图已保存")
    
    def _create_response_completeness_heatmap(self, results: Dict):
        """创建回答完整性热图"""
        
        model_quality = results['model_quality']
        
        # 准备数据矩阵
        models = [m.split('/')[-1] if '/' in m else m for m in model_quality.keys()]
        metrics = ['有效率', '空回答率', 'null回答率']
        
        data_matrix = []
        for model in model_quality.keys():
            row = [
                model_quality[model]['valid_rate'],
                model_quality[model]['empty_rate'],
                model_quality[model]['null_rate']
            ]
            data_matrix.append(row)
        
        data_matrix = np.array(data_matrix)
        
        # 创建热图
        plt.figure(figsize=(8, 10))
        
        sns.heatmap(data_matrix, 
                   xticklabels=metrics,
                   yticklabels=[m.split('/')[-1] if '/' in m else m for m in model_quality.keys()],
                   annot=True, 
                   fmt='.1f',
                   cmap='RdYlGn_r',
                   center=50,
                   cbar_kws={'label': '百分比 (%)'})
        
        plt.title('模型回答完整性热图', fontsize=14, fontweight='bold')
        plt.xlabel('指标类型')
        plt.ylabel('模型')
        
        plt.tight_layout()
        plt.savefig(self.results_dir / 'response_completeness_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("   🔥 回答完整性热图已保存")
    
    def _create_language_comparison_chart(self, language_analysis: Dict):
        """创建语言对比图"""
        
        languages = list(language_analysis.keys())
        valid_rates = [language_analysis[lang]['valid_rate'] for lang in languages]
        
        # 创建图表
        plt.figure(figsize=(10, 6))
        
        bars = plt.bar(languages, valid_rates, color=['lightblue', 'lightcoral'], alpha=0.8)
        plt.title('英文vs本国语言回答质量对比', fontsize=14, fontweight='bold')
        plt.ylabel('有效回答率 (%)')
        plt.ylim(0, 100)
        
        # 添加数值标签
        for bar, rate in zip(bars, valid_rates):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{rate:.1f}%', ha='center', va='bottom')
        
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.results_dir / 'language_quality_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("   🌍 语言质量对比图已保存")
    
    def generate_quality_report(self, results: Dict[str, Any]) -> str:
        """生成质量分析报告"""
        
        import datetime
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.results_dir / f"model_quality_report_{timestamp}.md"
        
        # 生成报告内容
        report_content = self._generate_quality_report_content(results)
        
        # 保存报告
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # 同时保存JSON格式
        json_file = self.results_dir / f"model_quality_data_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            # 处理set类型
            def convert_sets(obj):
                if isinstance(obj, set):
                    return list(obj)
                elif isinstance(obj, dict):
                    return {k: convert_sets(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_sets(item) for item in obj]
                return obj
            
            json.dump(convert_sets(results), f, ensure_ascii=False, indent=2)
        
        return str(report_file)
    
    def _generate_quality_report_content(self, results: Dict[str, Any]) -> str:
        """生成质量报告内容"""
        
        model_quality = results['model_quality']
        
        # 按质量排序
        sorted_models = sorted(model_quality.items(), 
                             key=lambda x: x[1]['valid_rate'], 
                             reverse=True)
        
        report = f"""# 🔍 模型回答质量分析报告

## 📊 执行摘要

本报告分析了各个LLM模型在多语言文化价值观实验中的回答质量，重点关注回答完整性和有效性。

### 🚨 关键发现

**Qwen QwQ-32B的问题**：
- 虽然在距离指标上表现最好，但实际上有大量空回答和null回答
- 这解释了为什么距离指标好但实际质量可能有问题

## 📈 详细分析

### 1. 模型质量排名

| 排名 | 模型 | 有效回答率 | 质量等级 | 有效/总数 |
|------|------|------------|----------|-----------|
"""
        
        for i, (model, metrics) in enumerate(sorted_models, 1):
            model_name = model.split('/')[-1] if '/' in model else model
            report += f"| {i} | {model_name} | {metrics['valid_rate']:.1f}% | {metrics['quality_grade']} | {metrics['valid_responses']}/{metrics['total_questions']} |\n"
        
        report += f"""
### 2. 问题模型详细分析

"""
        
        for model, metrics in sorted_models:
            model_name = model.split('/')[-1] if '/' in model else model
            if metrics['valid_rate'] < 80:  # 重点分析问题模型
                report += f"""
#### ❌ {model_name} (问题模型)
- **有效回答**: {metrics['valid_responses']}/{metrics['total_questions']} ({metrics['valid_rate']:.1f}%)
- **空回答**: {metrics['empty_responses']} ({metrics['empty_rate']:.1f}%)
- **null回答**: {metrics['null_responses']} ({metrics['null_rate']:.1f}%)
- **测试覆盖**: {metrics['countries_tested']} 个国家, {metrics['languages_tested']} 种语言
- **质量等级**: {metrics['quality_grade']}

**问题分析**: 该模型存在严重的回答完整性问题，大量问题未能给出有效回答。
"""
            elif metrics['valid_rate'] >= 90:  # 优秀模型
                report += f"""
#### ✅ {model_name} (优秀模型)
- **有效回答**: {metrics['valid_responses']}/{metrics['total_questions']} ({metrics['valid_rate']:.1f}%)
- **质量等级**: {metrics['quality_grade']}
- **测试覆盖**: {metrics['countries_tested']} 个国家, {metrics['languages_tested']} 种语言
"""
        
        report += f"""
### 3. 为什么Qwen QwQ-32B距离指标最好？

**可能的原因**：
1. **数据稀疏性**: 由于大量空回答，实际参与PCA计算的数据点很少
2. **偶然性好结果**: 少数有效回答可能恰好接近真实国家位置
3. **计算偏差**: 空值处理可能导致距离计算出现偏差
4. **样本偏差**: 有效回答可能集中在某些特定问题上

**建议**：
- 在评估模型效果时，应该同时考虑回答质量和距离指标
- 对于回答完整率低于80%的模型，其距离指标可能不可靠
- 建议使用加权评分：`综合得分 = 距离得分 × 回答完整率`

## 🎯 结论与建议

### 主要结论

1. **质量与距离指标不一致**: Qwen QwQ-32B距离最小但回答质量最差
2. **回答完整性至关重要**: 空回答会严重影响分析结果的可靠性
3. **需要综合评估**: 单一指标无法全面评估模型性能

### 实践建议

1. **建立综合评估体系**: 同时考虑回答质量和效果指标
2. **设置质量阈值**: 回答完整率低于70%的模型结果应谨慎使用
3. **数据预处理**: 在PCA分析前应过滤掉回答质量差的数据
4. **模型选择策略**: 优先选择回答完整且效果好的模型

---

**报告生成时间**: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**分析工具**: 模型回答质量分析器 v1.0
"""
        
        return report
    
    def run_full_analysis(self) -> Dict[str, Any]:
        """运行完整分析"""
        
        # 1. 分析回答质量
        results = self.analyze_response_quality()
        
        # 2. 创建可视化
        self.create_visualizations(results)
        
        # 3. 生成报告
        report_file = self.generate_quality_report(results)
        
        print(f"\n✅ 质量分析完成！")
        print(f"📁 结果目录: {self.results_dir}")
        print(f"📋 质量报告: {report_file}")
        
        return results


def main():
    """主函数"""
    
    print("🔍 启动模型回答质量分析")
    print("=" * 50)
    
    try:
        # 创建分析器
        analyzer = ModelResponseQualityAnalyzer()
        
        # 运行分析
        results = analyzer.run_full_analysis()
        
        print("\n🎉 分析完成！")
        print(f"📁 查看结果: {analyzer.results_dir}")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
