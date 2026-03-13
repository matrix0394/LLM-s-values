"""
Stage 1 多语言访谈数据处理器

负责将多语言访谈结果转换为IVS格式并进行分析。
支持：
- 加载原始访谈结果
- 转换为IVS兼容格式
- 生成实体ID
- 保存处理后的结果（JSON和Pickle格式）
- 生成跨语言比较报告
"""

import sys
import json
import pickle
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import pandas as pd
import numpy as np

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.base.ivs_question_processor import IVSQuestionProcessor


# 语言名称映射
UN_LANGUAGE_NAMES_ZH = {
    "en": "英语",
    "fr": "法语",
    "es": "西班牙语",
    "ru": "俄语",
    "ar": "阿拉伯语",
    "zh-cn": "简体中文"
}


class LLMMultilingualDataProcessor:
    """
    Stage 1 多语言访谈数据处理器
    
    负责处理多语言访谈的原始结果，转换为IVS兼容格式，
    并与现有的PCA分析管道集成。
    """
    
    def __init__(self, data_path: str = "data"):
        """
        初始化数据处理器
        
        Args:
            data_path: 数据根目录路径
        """
        self.data_path = Path(data_path)
        self.raw_results: Dict[str, Any] = {}
        self.processed_data: pd.DataFrame = pd.DataFrame()
        
        print(f"✅ LLMMultilingualDataProcessor 初始化完成")
        print(f"   - 数据路径: {self.data_path}")
    
    def generate_entity_id(self, model_name: str, language: str) -> str:
        """
        生成实体ID
        
        格式: llm_{model_name}_{language}
        
        Args:
            model_name: 模型名称
            language: 语言代码
            
        Returns:
            str: 实体ID
        """
        # 清理模型名称中的特殊字符
        safe_model_name = model_name.replace('/', '_').replace('\\', '_').replace(':', '_')
        return f"llm_{safe_model_name}_{language}"
    
    def load_raw_results(self, data_dir: Path = None) -> Dict[str, Any]:
        """
        加载原始访谈结果
        
        从 data/llm_values/interview_raw/ 目录加载所有多语言访谈结果。
        多语言文件格式: {model_name}_{language}_{timestamp}.pkl
        
        Args:
            data_dir: 数据目录，默认为 data/llm_values/interview_raw/
            
        Returns:
            Dict: 按 model_language 组织的原始结果
        """
        if data_dir is None:
            data_dir = self.data_path / "llm_interviews" / "intrinsic" / "interview_raw"
        
        if not data_dir.exists():
            print(f"⚠️ 数据目录不存在: {data_dir}")
            return {}
        
        results = {}
        loaded_count = 0
        skipped_count = 0
        
        print(f"\n📂 加载原始访谈数据: {data_dir}")
        
        for pkl_file in sorted(data_dir.glob("*.pkl")):
            try:
                # 跳过合并文件
                if pkl_file.name.startswith("llm_interview_raw_"):
                    skipped_count += 1
                    continue
                
                with open(pkl_file, 'rb') as f:
                    data = pickle.load(f)
                
                model_name = data.get('model_name', '')
                language = data.get('language', '')
                
                # 只处理包含语言标识的多语言访谈结果
                if model_name and language:
                    key = f"{model_name}_{language}"
                    
                    # 如果已存在，保留较新的（基于时间戳）
                    if key in results:
                        existing_ts = results[key].get('timestamp', '')
                        new_ts = data.get('timestamp', '')
                        if new_ts > existing_ts:
                            results[key] = data
                            print(f"   🔄 更新: {key}")
                    else:
                        results[key] = data
                        loaded_count += 1
                        
            except Exception as e:
                print(f"   ⚠️ 加载失败 {pkl_file.name}: {e}")
        
        self.raw_results = results
        
        print(f"\n📊 加载统计:")
        print(f"   - 多语言访谈结果: {loaded_count} 个")
        print(f"   - 跳过合并文件: {skipped_count} 个")
        
        # 按模型和语言统计
        if results:
            models = set()
            languages = set()
            for key in results.keys():
                parts = key.rsplit('_', 1)
                if len(parts) == 2:
                    models.add(parts[0])
                    languages.add(parts[1])
            
            print(f"   - 模型数量: {len(models)}")
            print(f"   - 语言数量: {len(languages)}")
            print(f"   - 语言: {', '.join(sorted(languages))}")
        
        return results
    
    def convert_to_ivs_format(self, raw_results: Dict[str, Any] = None) -> pd.DataFrame:
        """
        转换为IVS兼容格式
        
        将原始访谈结果转换为与IVS数据格式兼容的DataFrame，
        以便进行PCA分析。
        
        Args:
            raw_results: 原始结果字典，None则使用已加载的数据
            
        Returns:
            pd.DataFrame: IVS兼容格式的数据
        """
        if raw_results is None:
            raw_results = self.raw_results
        
        if not raw_results:
            print("⚠️ 没有原始数据可转换")
            return pd.DataFrame()
        
        print(f"\n🔄 转换为IVS格式...")
        
        rows = []
        
        for key, data in raw_results.items():
            model_name = data.get('model_name', '')
            language = data.get('language', '')
            
            if not model_name or not language:
                continue
            
            # 创建基础行
            row = {
                'entity_id': self.generate_entity_id(model_name, language),
                'model_name': model_name,
                'language': language,
                'language_name': UN_LANGUAGE_NAMES_ZH.get(language, language),
                'country_code': self.generate_entity_id(model_name, language),  # 用于PCA
                'year': 2025,
                'weight': 1.0,
                'data_source': 'LLM_Multilingual',
                'Cultural Region': 'AI Model'
            }
            
            # 处理响应
            responses = data.get('responses', [])
            response_dict = {}
            
            for resp in responses:
                if isinstance(resp, dict):
                    question_id = resp.get('question_id', '')
                    # 优先使用 processed_response，其次是 response
                    value = resp.get('processed_response') or resp.get('response')
                    is_valid = resp.get('is_valid', False)
                    
                    if is_valid and value is not None:
                        response_dict[question_id] = value
            
            # 添加IVS问题列
            ivs_questions = ['A008', 'A165', 'E018', 'E025', 'F063', 'F118', 'F120', 'G006']
            for q in ivs_questions:
                row[q] = response_dict.get(q)
            
            # 处理Y002 - 计算物质主义倾向
            y002_value = response_dict.get('Y002')
            if isinstance(y002_value, (list, tuple)) and len(y002_value) == 2:
                row['Y002_first'] = y002_value[0]
                row['Y002_second'] = y002_value[1]
                row['Y002'] = IVSQuestionProcessor.process_y002(y002_value[0], y002_value[1])
            else:
                row['Y002_first'] = None
                row['Y002_second'] = None
                row['Y002'] = None
            
            # 处理Y003 - 计算传统vs世俗理性分数
            y003_value = response_dict.get('Y003')
            if isinstance(y003_value, (list, tuple)) and len(y003_value) > 0:
                row['Y003_values'] = list(y003_value)
                y003_result = IVSQuestionProcessor.process_y003(list(y003_value))
                row['Y003'] = y003_result.get('y003_score')
            elif isinstance(y003_value, int):
                row['Y003_values'] = [y003_value]
                y003_result = IVSQuestionProcessor.process_y003([y003_value])
                row['Y003'] = y003_result.get('y003_score')
            else:
                row['Y003_values'] = None
                row['Y003'] = None
            
            rows.append(row)
        
        self.processed_data = pd.DataFrame(rows)
        
        print(f"✅ 转换完成: {len(self.processed_data)} 条记录")
        
        # 统计有效响应
        if not self.processed_data.empty:
            valid_counts = {}
            for q in ivs_questions + ['Y002', 'Y003']:
                if q in self.processed_data.columns:
                    valid_counts[q] = self.processed_data[q].notna().sum()
            
            print(f"   - 有效响应统计:")
            for q, count in valid_counts.items():
                print(f"     {q}: {count}/{len(self.processed_data)}")
        
        return self.processed_data

    def save_processed_results(self, output_dir: Path = None, 
                               prefix: str = "multilingual") -> Tuple[str, str]:
        """
        保存处理后的结果（JSON和Pickle格式）
        
        Args:
            output_dir: 输出目录，默认为 data/llm_values/
            prefix: 文件名前缀
            
        Returns:
            Tuple[str, str]: (JSON文件路径, Pickle文件路径)
        """
        if self.processed_data.empty:
            print("⚠️ 没有数据可保存")
            return ("", "")
        
        if output_dir is None:
            output_dir = self.data_path / "llm_interviews" / "intrinsic"
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 准备保存的数据（转换为可序列化格式）
        save_df = self.processed_data.copy()
        
        # 处理Y003_values列（列表转字符串，便于JSON序列化）
        if 'Y003_values' in save_df.columns:
            save_df['Y003_values_str'] = save_df['Y003_values'].apply(
                lambda x: str(x) if x is not None else None
            )
        
        # 保存JSON格式
        json_file = output_dir / f"{prefix}_processed_{timestamp}.json"
        save_df.to_json(json_file, orient='records', indent=2, force_ascii=False)
        
        # 保存Pickle格式
        pkl_file = output_dir / f"{prefix}_processed_{timestamp}.pkl"
        self.processed_data.to_pickle(pkl_file)
        
        # 同时保存标准文件名版本（不带时间戳）
        standard_json = output_dir / f"{prefix}_ivs_format.json"
        standard_pkl = output_dir / f"{prefix}_ivs_format.pkl"
        save_df.to_json(standard_json, orient='records', indent=2, force_ascii=False)
        self.processed_data.to_pickle(standard_pkl)
        
        print(f"\n💾 保存处理后的数据:")
        print(f"   - JSON: {json_file}")
        print(f"   - Pickle: {pkl_file}")
        print(f"   - 标准JSON: {standard_json}")
        print(f"   - 标准Pickle: {standard_pkl}")
        
        return (str(json_file), str(pkl_file))
    
    def run_pca_analysis(self, use_fixed_pca: bool = True) -> pd.DataFrame:
        """
        运行PCA分析
        
        使用现有的LLMPCAAnalyzer类进行PCA分析，
        生成每个模型-语言组合的文化坐标。
        
        Args:
            use_fixed_pca: 是否使用固定的PCA模型（Stage0的模型）
            
        Returns:
            pd.DataFrame: 包含PCA坐标的实体分数
        """
        from src.llm_values.llm_pca_analysis import LLMPCAAnalyzer
        
        print(f"\n🔄 运行PCA分析...")
        
        # 确保有处理后的数据
        if self.processed_data.empty:
            print("⚠️ 没有处理后的数据，请先调用 convert_to_ivs_format()")
            return pd.DataFrame()
        
        # 保存临时数据供PCA分析器使用
        temp_dir = self.data_path / "llm_interviews" / "intrinsic"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存为PCA分析器期望的格式
        temp_file = temp_dir / "llm_processed_responses_ivs_format_temp.pkl"
        self.processed_data.to_pickle(temp_file)
        
        try:
            # 创建PCA分析器
            analyzer = LLMPCAAnalyzer(data_path=str(self.data_path))
            
            # 手动加载我们的数据
            analyzer.llm_data = self.processed_data
            
            if use_fixed_pca:
                # 使用固定PCA模型
                entity_scores = analyzer.run_analysis_with_fixed_pca()
            else:
                # 重新拟合PCA
                entity_scores = analyzer.run_full_analysis()
            
            # 添加语言信息到PCA结果
            if not entity_scores.empty and 'entity_id' in entity_scores.columns:
                # 从entity_id提取语言: llm_model_lang -> lang
                def extract_language(entity_id):
                    if not entity_id or not isinstance(entity_id, str):
                        return 'en'
                    for lang in ['zh-cn', 'en', 'fr', 'es', 'ru', 'ar']:
                        if entity_id.endswith(f'_{lang}'):
                            return lang
                    return 'en'
                
                def extract_model(entity_id):
                    if not entity_id or not isinstance(entity_id, str):
                        return ''
                    # llm_model_lang -> model
                    if entity_id.startswith('llm_'):
                        parts = entity_id[4:]  # 去掉 'llm_'
                        for lang in ['zh-cn', 'en', 'fr', 'es', 'ru', 'ar']:
                            if parts.endswith(f'_{lang}'):
                                return parts[:-len(f'_{lang}')]
                        return parts
                    return entity_id
                
                entity_scores['language'] = entity_scores['entity_id'].apply(extract_language)
                entity_scores['model_name'] = entity_scores['entity_id'].apply(extract_model)
                
                print(f"   - 语言分布: {entity_scores['language'].value_counts().to_dict()}")
            
            print(f"✅ PCA分析完成: {len(entity_scores)} 个实体")
            
            return entity_scores
            
        except Exception as e:
            print(f"❌ PCA分析失败: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
        finally:
            # 清理临时文件
            if temp_file.exists():
                temp_file.unlink()
    
    def generate_summary_report(self, entity_scores: pd.DataFrame = None) -> Dict[str, Any]:
        """
        生成跨语言比较报告
        
        为每个模型生成不同语言下的价值观比较报告。
        
        Args:
            entity_scores: PCA分析结果，None则使用处理后的数据
            
        Returns:
            Dict: 包含比较报告的字典
        """
        print(f"\n📊 生成跨语言比较报告...")
        
        # 使用处理后的数据
        data = self.processed_data if entity_scores is None else entity_scores
        
        if data.empty:
            print("⚠️ 没有数据可分析")
            return {}
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_records': len(data),
            'models': {},
            'language_summary': {},
            'cross_language_comparison': []
        }
        
        # 按模型分组
        if 'model_name' in data.columns:
            models = data['model_name'].unique()
            
            for model in models:
                model_data = data[data['model_name'] == model]
                languages = model_data['language'].unique() if 'language' in model_data.columns else []
                
                model_report = {
                    'model_name': model,
                    'languages_tested': list(languages),
                    'language_count': len(languages),
                    'responses_by_language': {}
                }
                
                # 每种语言的响应统计
                for lang in languages:
                    lang_data = model_data[model_data['language'] == lang]
                    
                    lang_stats = {
                        'language': lang,
                        'language_name': UN_LANGUAGE_NAMES_ZH.get(lang, lang),
                        'record_count': len(lang_data)
                    }
                    
                    # 添加IVS问题的值
                    ivs_questions = ['A008', 'A165', 'E018', 'E025', 'F063', 'F118', 'F120', 'G006', 'Y002', 'Y003']
                    for q in ivs_questions:
                        if q in lang_data.columns:
                            values = lang_data[q].dropna()
                            if len(values) > 0:
                                lang_stats[q] = {
                                    'value': values.iloc[0] if len(values) == 1 else values.tolist(),
                                    'valid': True
                                }
                            else:
                                lang_stats[q] = {'value': None, 'valid': False}
                    
                    # 添加PCA坐标（如果有）
                    if 'PC1_rescaled' in lang_data.columns:
                        lang_stats['PC1'] = lang_data['PC1_rescaled'].iloc[0] if len(lang_data) > 0 else None
                    if 'PC2_rescaled' in lang_data.columns:
                        lang_stats['PC2'] = lang_data['PC2_rescaled'].iloc[0] if len(lang_data) > 0 else None
                    
                    model_report['responses_by_language'][lang] = lang_stats
                
                report['models'][model] = model_report
        
        # 语言汇总统计
        if 'language' in data.columns:
            for lang in data['language'].unique():
                lang_data = data[data['language'] == lang]
                report['language_summary'][lang] = {
                    'language_name': UN_LANGUAGE_NAMES_ZH.get(lang, lang),
                    'model_count': len(lang_data['model_name'].unique()) if 'model_name' in lang_data.columns else 0,
                    'total_records': len(lang_data)
                }
        
        # 跨语言比较（计算同一模型不同语言间的差异）
        if 'model_name' in data.columns and 'language' in data.columns:
            for model in data['model_name'].unique():
                model_data = data[data['model_name'] == model]
                languages = model_data['language'].unique()
                
                if len(languages) > 1:
                    comparison = {
                        'model': model,
                        'languages': list(languages),
                        'value_differences': {}
                    }
                    
                    # 计算每个问题在不同语言间的差异
                    ivs_questions = ['A008', 'A165', 'E018', 'E025', 'F063', 'F118', 'F120', 'G006', 'Y002', 'Y003']
                    for q in ivs_questions:
                        if q in model_data.columns:
                            values = model_data.groupby('language')[q].first().dropna()
                            if len(values) > 1:
                                comparison['value_differences'][q] = {
                                    'values': values.to_dict(),
                                    'range': float(values.max() - values.min()) if values.dtype in ['int64', 'float64'] else None,
                                    'std': float(values.std()) if values.dtype in ['int64', 'float64'] else None
                                }
                    
                    report['cross_language_comparison'].append(comparison)
        
        print(f"✅ 报告生成完成")
        print(f"   - 模型数量: {len(report['models'])}")
        print(f"   - 语言数量: {len(report['language_summary'])}")
        print(f"   - 跨语言比较: {len(report['cross_language_comparison'])} 组")
        
        return report
    
    def save_summary_report(self, report: Dict[str, Any], output_dir: Path = None) -> str:
        """
        保存汇总报告
        
        Args:
            report: 报告字典
            output_dir: 输出目录
            
        Returns:
            str: 保存的文件路径
        """
        import numpy as np
        
        def convert_numpy_types(obj):
            """递归转换numpy类型为Python原生类型"""
            if isinstance(obj, dict):
                return {k: convert_numpy_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            elif isinstance(obj, (np.integer, np.int64, np.int32)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64, np.float32)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, np.bool_):
                return bool(obj)
            else:
                return obj
        
        if output_dir is None:
            output_dir = self.data_path / "llm_interviews" / "intrinsic"
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = output_dir / f"multilingual_summary_report_{timestamp}.json"
        
        # 转换numpy类型
        report_converted = convert_numpy_types(report)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_converted, f, ensure_ascii=False, indent=2)
        
        print(f"💾 报告已保存: {report_file}")
        
        return str(report_file)
    
    def run_full_pipeline(self, data_dir: Path = None, 
                          run_pca: bool = True,
                          use_fixed_pca: bool = True) -> Dict[str, Any]:
        """
        运行完整的数据处理管道
        
        1. 加载原始结果
        2. 转换为IVS格式
        3. 保存处理后的数据
        4. 运行PCA分析（可选）
        5. 生成汇总报告
        
        Args:
            data_dir: 数据目录
            run_pca: 是否运行PCA分析
            use_fixed_pca: 是否使用固定PCA模型
            
        Returns:
            Dict: 包含所有结果的字典
        """
        print("\n" + "="*60)
        print("🚀 运行多语言数据处理管道")
        print("="*60)
        
        results = {
            'raw_results': {},
            'processed_data': None,
            'entity_scores': None,
            'summary_report': None,
            'output_files': {}
        }
        
        # 1. 加载原始结果
        results['raw_results'] = self.load_raw_results(data_dir)
        
        if not results['raw_results']:
            print("❌ 没有找到原始数据")
            return results
        
        # 2. 转换为IVS格式
        results['processed_data'] = self.convert_to_ivs_format()
        
        if results['processed_data'].empty:
            print("❌ 数据转换失败")
            return results
        
        # 3. 保存处理后的数据
        json_file, pkl_file = self.save_processed_results()
        results['output_files']['processed_json'] = json_file
        results['output_files']['processed_pkl'] = pkl_file
        
        # 4. 运行PCA分析（可选）
        if run_pca:
            results['entity_scores'] = self.run_pca_analysis(use_fixed_pca)
        
        # 5. 生成汇总报告
        results['summary_report'] = self.generate_summary_report(results['entity_scores'])
        report_file = self.save_summary_report(results['summary_report'])
        results['output_files']['summary_report'] = report_file
        
        print("\n" + "="*60)
        print("✅ 多语言数据处理管道完成")
        print("="*60)
        
        return results


def main():
    """测试数据处理器"""
    print("🔄 测试 LLMMultilingualDataProcessor...")
    
    processor = LLMMultilingualDataProcessor(data_path="data")
    
    # 加载原始数据
    raw_results = processor.load_raw_results()
    
    if raw_results:
        # 转换为IVS格式
        processed_data = processor.convert_to_ivs_format()
        
        if not processed_data.empty:
            print(f"\n处理后的数据预览:")
            print(processed_data[['entity_id', 'model_name', 'language', 'A008', 'Y002']].head(10))
            
            # 保存数据
            processor.save_processed_results()
            
            # 生成报告
            report = processor.generate_summary_report()
            processor.save_summary_report(report)
    else:
        print("没有找到多语言访谈数据")
    
    print("\n✅ 测试完成！")


if __name__ == "__main__":
    main()
