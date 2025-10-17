"""
控制变量的多语言对比实验
确保问答、计算、PCA条件完全一致，只有语言不同
"""

import os
import json
import pickle
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import threading

# 导入基础模块
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.base.base_interview import BaseInterview
from src.base.base_pca_analyzer import BasePCAAnalyzer
from src.base.base_cultural_map_visualizer import BaseCulturalMapVisualizer
from src.base.ivs_question_processor import IVSQuestionProcessor
from src.llm_analysis.llm_questionnaire import IVSQuestions, LLMResponse


class ControlledMultilingualExperiment:
    """控制变量的多语言对比实验"""
    
    def __init__(self, data_path: str = "data"):
        self.data_path = Path(data_path)
        self.results_dir = self.data_path / "results" / "controlled_multilingual_experiment"
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # 实验配置
        self.experiment_config = self._load_experiment_config()
        self.target_countries = self._get_target_countries()
        
        print(f"💰 使用经济模型配置:")
        for model in self.experiment_config["models"]:
            print(f"   - {model}")
        
        # 创建子组件
        self.analyzer = ControlledMultilingualPCA(data_path=str(data_path))
        self.visualizer = ControlledMultilingualVisualization(data_path=str(data_path))
        
        print(f"🎯 控制变量多语言实验初始化完成")
        print(f"   目标国家: {len(self.target_countries)} 个")
        print(f"   支持语言: {list(self.experiment_config['languages'].keys())}")
    
    def _load_experiment_config(self) -> Dict:
        """加载实验配置 - 基于实际可用的语言"""
        config = {
            "languages": {
                "en": {
                    "name": "English", 
                    "system_prompt_template": """You are participating in a cultural values survey. Please provide thoughtful responses based on your cultural background and personal views.

Please follow these guidelines:
- Provide sincere, thoughtful answers to each question based on your cultural values and beliefs
- Choose the option that best reflects your cultural values and beliefs
- Answer as a real person from your country would

Response format:
- Single choice: Answer with only one number
- Y002 (dual choice): Answer with two numbers separated by space
- Y003 (multiple choice): Answer with 1-5 numbers separated by spaces

You are a typical citizen of {country}. {country_context}""",
                    "country_contexts": {
                        "China": "China is a country with a long history and deep cultural traditions, valuing collectivism, family values, respect for authority, and social harmony.",
                        "Russian Federation": "Russia is a country with rich history and cultural traditions, valuing collectivism, family values, respect for authority, and social stability.",
                        "Mexico": "Mexico is a country with rich history and cultural traditions, valuing family, community, respect, and religious traditions.",
                        "Egypt": "Egypt is a country with ancient history and rich cultural traditions, valuing family, community, religious traditions, and respect for authority."
                    }
                },
                "zh-cn": {
                    "name": "中文",
                    "system_prompt_template": """您正在参与一项文化价值观调查。请基于您的文化背景和个人观点提供深思熟虑的回答。

请遵循以下指导原则：
- 根据您的文化价值观和信念，为每个问题提供真诚、经过深思熟虑的回答
- 选择最能反映您文化价值观和信念的选项
- 像来自您国家的真实人士一样回答

回答格式：
- 单选题：仅回答一个数字
- Y002（双选题）：回答两个用空格分隔的数字
- Y003（多选题）：回答1-5个用空格分隔的数字

您是{country}的一位普通民众。{country_context}""",
                    "country_contexts": {
                        "China": "中国是一个有着悠久历史和深厚文化传统的国家，重视集体主义、家庭观念、尊重权威和社会和谐。"
                    }
                },
                "ru": {
                    "name": "Русский",
                    "system_prompt_template": """Вы участвуете в опросе о культурных ценностях. Пожалуйста, предоставьте продуманные ответы, основанные на вашем культурном происхождении и личных взглядах.

Пожалуйста, следуйте этим рекомендациям:
- Предоставляйте искренние, продуманные ответы на каждый вопрос, основанные на ваших культурных ценностях и убеждениях
- Выбирайте вариант, который лучше всего отражает ваши культурные ценности и убеждения
- Отвечайте как настоящий человек из вашей страны

Формат ответа:
- Одиночный выбор: отвечайте только одним числом
- Y002 (двойной выбор): отвечайте двумя числами, разделенными пробелом
- Y003 (множественный выбор): отвечайте 1-5 числами, разделенными пробелами

Вы обычный гражданин {country}. {country_context}""",
                    "country_contexts": {
                        "Russian Federation": "Россия - это страна с богатой историей и культурными традициями, которая ценит коллективизм, семейные ценности, уважение к власти и социальную стабильность."
                    }
                },
                "es": {
                    "name": "Español",
                    "system_prompt_template": """Está participando en una encuesta sobre valores culturales. Por favor, proporcione respuestas reflexivas basadas en su trasfondo cultural y puntos de vista personales.

Por favor, siga estas pautas:
- Proporcione respuestas sinceras y reflexivas a cada pregunta basadas en sus valores culturales y creencias
- Elija la opción que mejor refleje sus valores culturales y creencias
- Responda como lo haría una persona real de su país

Formato de respuesta:
- Opción única: responda solo con un número
- Y002 (opción doble): responda con dos números separados por espacio
- Y003 (opción múltiple): responda con 1-5 números separados por espacios

Usted es un ciudadano común de {country}. {country_context}""",
                    "country_contexts": {
                        "Mexico": "México es un país con rica historia y tradiciones culturales, que valora la familia, la comunidad, el respeto y las tradiciones religiosas."
                    }
                },
                "ar": {
                    "name": "العربية",
                    "system_prompt_template": """أنت تشارك في استطلاع حول القيم الثقافية. يرجى تقديم إجابات مدروسة بناءً على خلفيتك الثقافية ووجهات نظرك الشخصية.

يرجى اتباع هذه الإرشادات:
- قدم إجابات صادقة ومدروسة لكل سؤال بناءً على قيمك الثقافية ومعتقداتك
- اختر الخيار الذي يعكس بشكل أفضل قيمك الثقافية ومعتقداتك
- أجب كما يجيب شخص حقيقي من بلدك

تنسيق الإجابة:
- اختيار واحد: أجب برقم واحد فقط
- Y002 (اختيار مزدوج): أجب برقمين مفصولين بمسافة
- Y003 (اختيار متعدد): أجب بـ 1-5 أرقام مفصولة بمسافات

أنت مواطن عادي من {country}. {country_context}""",
                    "country_contexts": {
                        "Egypt": "مصر بلد له تاريخ عريق وتقاليد ثقافية غنية، يقدر الأسرة والمجتمع والتقاليد الدينية واحترام السلطة."
                    }
                }
            },
            "target_countries": [
                "China", "Russian Federation", "Mexico", "Egypt"
            ],
            "models": [
                "openai/gpt-4o-mini",
                "deepseek/deepseek-chat-v3-0324",
                "google/gemini-2.0-flash-001"
            ],
            "repeat_count": 1,  # 每个条件重复3次
            "temperature": 0.1,  # 固定温度
            "max_tokens": 50    # 固定最大token数
        }
        return config
    
    def _get_target_countries(self) -> List[str]:
        """获取目标国家列表"""
        return self.experiment_config["target_countries"]
    
    def run_controlled_experiment(self) -> Dict[str, Any]:
        """运行控制变量实验"""
        print("🚀 开始控制变量多语言实验")
        print("=" * 60)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 第一步：收集所有语言的访谈数据
        print("📋 第一步：收集多语言访谈数据")
        
        # 检查是否有检查点文件
        checkpoint_file = self.results_dir / f"checkpoint_interviews_{timestamp}.json"
        if checkpoint_file.exists():
            print(f"📂 发现检查点文件，加载已有数据...")
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                interview_results = json.load(f)
        else:
            interview_results = self._collect_multilingual_interviews()
            
            # 保存检查点
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(interview_results, f, ensure_ascii=False, indent=2)
            print(f"💾 访谈数据已保存检查点: {checkpoint_file}")
        
        # 第二步：统一处理和分析数据
        print("\n📊 第二步：统一数据处理和PCA分析")
        analysis_results = self._perform_unified_analysis(interview_results)
        
        # 第三步：对比可视化
        print("\n📈 第三步：生成对比可视化")
        visualization_results = self._create_comparison_visualizations(analysis_results)
        
        # 第四步：生成实验报告
        print("\n📝 第四步：生成实验报告")
        experiment_report = self._generate_experiment_report(
            interview_results, analysis_results, visualization_results
        )
        
        # 保存完整实验结果
        results = {
            "timestamp": timestamp,
            "experiment_config": self.experiment_config,
            "interview_results": interview_results,
            "analysis_results": analysis_results,
            "visualization_results": visualization_results,
            "experiment_report": experiment_report
        }
        
        results_file = self.results_dir / f"controlled_experiment_{timestamp}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 控制变量实验完成！结果保存至: {results_file}")
        return results
    
    def _collect_multilingual_interviews(self) -> Dict[str, Any]:
        """收集多语言访谈数据 - 基于语言-国家对"""
        results = {}
        
        # 检查配置类型
        if "language_country_pairs" in self.experiment_config:
            # 新的语言-国家对配置
            pairs = self.experiment_config["language_country_pairs"]
            print(f"\n🌍 收集 {len(pairs)} 个语言-国家对的数据...")
            
            for language, country in pairs:
                pair_key = f"{language}_{country}"
                print(f"\n🎯 收集 {language} 语言访谈 {country}...")
                
                # 创建专门的访谈器
                language_interviewer = ControlledLanguageInterview(
                    language=language,
                    config=self.experiment_config,
                    data_path=str(self.data_path)
                )
                
                # 只访谈指定的国家
                country_results = language_interviewer.interview_single_country(country)
                if country_results:
                    results[pair_key] = {country: country_results}
                    print(f"✅ {language}-{country} 数据收集完成")
                else:
                    print(f"❌ {language}-{country} 数据收集失败")
        
        else:
            # 原有的全语言配置（向后兼容）
            for language in self.experiment_config["languages"]:
                print(f"\n🌍 收集 {language} 语言数据...")
                
                language_interviewer = ControlledLanguageInterview(
                    language=language,
                    config=self.experiment_config,
                    data_path=str(self.data_path)
                )
                
                language_results = language_interviewer.interview_all_countries()
                results[language] = language_results
                
                print(f"✅ {language} 语言数据收集完成: {len(language_results)} 个国家")
        
        return results
    
    def _perform_unified_analysis(self, interview_results: Dict) -> Dict[str, Any]:
        """执行统一的PCA分析"""
        # 将所有语言的数据转换为统一格式
        unified_data = self._convert_to_unified_format(interview_results)
        
        # 合并所有语言的数据进行统一PCA分析
        all_multilingual_data = []
        for language, data in unified_data.items():
            print(f"✅ {language} 数据转换完成: {len(data)} 行")
            all_multilingual_data.append(data)
        
        if not all_multilingual_data:
            print("❌ 没有有效的多语言数据")
            return {}
        
        # 合并所有语言数据
        combined_multilingual_data = pd.concat(all_multilingual_data, ignore_index=True)
        print(f"📊 合并所有语言数据: {len(combined_multilingual_data)} 行")
        
        # 创建临时数据文件
        temp_file = self.results_dir / f"temp_all_multilingual_data.pkl"
        combined_multilingual_data.to_pickle(temp_file)
        
        # 执行统一的PCA分析
        analyzer = ControlledMultilingualPCA(data_path=str(self.data_path))
        analyzer.temp_data_file = temp_file
        
        print("🔬 执行统一PCA分析（包含所有语言数据）...")
        pca_results = analyzer.run_full_analysis()
        
        # 清理临时文件
        temp_file.unlink()
        
        # 为每种语言提取结果（基于统一的PCA分析）
        language_results = {}
        for language in unified_data.keys():
            # 从统一PCA结果中提取该语言的坐标
            language_coordinates = analyzer._extract_language_coordinates(pca_results, language)
            
            language_results[language] = {
                "language": language,
                "pca_results": pca_results,  # 所有语言共享同一个PCA结果
                "pca_coordinates": language_coordinates,
                "analysis_summary": analyzer._create_analysis_summary(pca_results, language)
            }
        
        return language_results
    
    def _convert_to_unified_format(self, interview_results: Dict) -> Dict[str, pd.DataFrame]:
        """将访谈结果转换为统一的数据格式，按照旧脚本的逻辑聚合数据"""
        unified_data = {}
        
        for language, language_results in interview_results.items():
            rows = []
            
            for country, country_data in language_results.items():
                for model, model_responses in country_data.items():
                    # 聚合同一模型的多次回答
                    aggregated_responses = self._aggregate_model_responses(model_responses)
                    
                    if aggregated_responses:
                        # 创建一行数据代表这个国家-语言-模型组合
                        row = {
                            'country_code': self._get_country_code(country),
                            'country_name': country,
                            'model': model,
                            'language': language,
                            'data_source': f'{language}_{model}_{country}',  # 按照语言-模型-国家格式命名
                            'year': 2024  # LLM数据使用2024年
                        }
                        
                        # 添加聚合后的问题回答
                        row.update(aggregated_responses)
                        rows.append(row)
            
            if rows:
                unified_data[language] = pd.DataFrame(rows)
                print(f"✅ {language} 数据转换完成: {len(rows)} 行 (聚合后)")
        
        return unified_data
    
    def _aggregate_model_responses(self, model_responses: List[Dict]) -> Optional[Dict]:
        """聚合同一模型的多次回答，计算平均值或众数"""
        if not model_responses:
            return None
        
        # 收集所有问题的回答
        question_responses = {}
        
        for response_data in model_responses:
            responses = response_data.get('responses', {})
            for question_id, response_text in responses.items():
                if question_id not in question_responses:
                    question_responses[question_id] = []
                question_responses[question_id].append(response_text)
        
        # 聚合每个问题的回答
        aggregated = {}
        
        for question_id, responses in question_responses.items():
            if question_id in ['Y002', 'Y003']:
                # 复杂问题：处理后取平均值
                processed_values = []
                for response_text in responses:
                    processed = IVSQuestionProcessor.validate_and_process_response(
                        response_text, question_id
                    )
                    
                    if question_id == 'Y002':
                        value = processed.get('materialist_score')
                    elif question_id == 'Y003':
                        value = processed.get('y003_score')
                    
                    if value is not None and not np.isnan(value):
                        processed_values.append(value)
                
                if processed_values:
                    aggregated[question_id] = np.mean(processed_values)
                else:
                    aggregated[question_id] = np.nan
            else:
                # 单选题：取众数或平均值
                numeric_responses = []
                for response_text in responses:
                    try:
                        value = float(response_text)
                        numeric_responses.append(value)
                    except (ValueError, TypeError):
                        continue
                
                if numeric_responses:
                    # 对于单选题，取众数；如果没有众数，取平均值
                    from collections import Counter
                    counts = Counter(numeric_responses)
                    if counts:
                        most_common = counts.most_common(1)[0]
                        if most_common[1] > 1:  # 有众数
                            aggregated[question_id] = most_common[0]
                        else:  # 没有众数，取平均值
                            aggregated[question_id] = np.mean(numeric_responses)
                    else:
                        aggregated[question_id] = np.nan
                else:
                    aggregated[question_id] = np.nan
        
        return aggregated
    
    def _process_single_response(self, response_data: Dict, country: str, 
                                model: str, language: str) -> Optional[Dict]:
        """处理单个响应数据"""
        try:
            row = {
                'country_code': self._get_country_code(country),
                'country_name': country,
                'model': model,
                'language': language,
                'data_source': f'{language}_roleplay'
            }
            
            # 处理每个问题的响应
            for question_id, response_text in response_data.get('responses', {}).items():
                if question_id in ['Y002', 'Y003']:
                    # 使用统一的问题处理器
                    processed = IVSQuestionProcessor.validate_and_process_response(
                        response_text, question_id
                    )
                    
                    if question_id == 'Y002':
                        row[question_id] = processed.get('materialist_score', np.nan)
                    elif question_id == 'Y003':
                        # 使用主要值
                        row[question_id] = processed.get('primary_value', np.nan)
                else:
                    # 单选题直接转换
                    try:
                        row[question_id] = float(response_text.strip())
                    except (ValueError, AttributeError):
                        row[question_id] = np.nan
            
            return row
            
        except Exception as e:
            print(f"⚠️ 处理响应时出错: {e}")
            return None
    
    def _get_country_code(self, country_name: str) -> str:
        """获取国家代码"""
        # 简化的国家代码映射 - 基于实际支持的语言-国家对
        country_code_map = {
            "China": "156",
            "Russian Federation": "643", 
            "Mexico": "484",
            "Egypt": "818"
        }
        return country_code_map.get(country_name, "999")
    
    def _create_comparison_visualizations(self, analysis_results: Dict) -> Dict[str, Any]:
        """创建对比可视化"""
        print("🎨 创建语言对比可视化...")
        
        # 使用可视化器创建对比图表
        viz_results = self.visualizer.create_language_comparison_plots(analysis_results)
        
        return viz_results
    
    def _generate_experiment_report(self, interview_results: Dict, 
                                  analysis_results: Dict, 
                                  visualization_results: Dict) -> Dict[str, Any]:
        """生成实验报告"""
        report = {
            "experiment_summary": {
                "total_languages": len(interview_results),
                "total_countries": len(self.target_countries),
                "total_models": len(self.experiment_config["models"]),
                "total_responses": sum(
                    len(country_data) * len(model_data) * self.experiment_config["repeat_count"]
                    for lang_data in interview_results.values()
                    for country_data in lang_data.values()
                    for model_data in country_data.values()
                )
            },
            "language_comparison": self._analyze_language_differences(analysis_results),
            "consistency_analysis": self._analyze_cross_language_consistency(analysis_results),
            "cultural_preservation": self._analyze_cultural_preservation(analysis_results),
            "distance_to_real_countries": self._analyze_distance_to_real_countries(analysis_results)
        }
        
        return report
    
    def _analyze_language_differences(self, analysis_results: Dict) -> Dict[str, Any]:
        """分析语言差异"""
        # 比较不同语言下同一国家的PCA坐标差异
        differences = {}
        
        # 提取每种语言的PCA结果
        language_coords = {}
        for language, results in analysis_results.items():
            if 'pca_coordinates' in results:
                language_coords[language] = results['pca_coordinates']
        
        # 计算语言间的差异
        languages = list(language_coords.keys())
        for i, lang1 in enumerate(languages):
            for lang2 in languages[i+1:]:
                diff_key = f"{lang1}_vs_{lang2}"
                differences[diff_key] = self._calculate_coordinate_differences(
                    language_coords[lang1], language_coords[lang2]
                )
        
        return differences
    
    def _calculate_coordinate_differences(self, coords1: Dict, coords2: Dict) -> Dict[str, float]:
        """计算坐标差异"""
        common_countries = set(coords1.keys()) & set(coords2.keys())
        
        if not common_countries:
            return {"mean_distance": 0, "max_distance": 0, "countries_compared": 0}
        
        distances = []
        for country in common_countries:
            pc1_diff = coords1[country]['PC1'] - coords2[country]['PC1']
            pc2_diff = coords1[country]['PC2'] - coords2[country]['PC2']
            distance = np.sqrt(pc1_diff**2 + pc2_diff**2)
            distances.append(distance)
        
        return {
            "mean_distance": np.mean(distances),
            "max_distance": np.max(distances),
            "min_distance": np.min(distances),
            "std_distance": np.std(distances),
            "countries_compared": len(common_countries)
        }
    
    def _analyze_cross_language_consistency(self, analysis_results: Dict) -> Dict[str, Any]:
        """分析跨语言一致性"""
        consistency = {
            "overall_consistency": 0,
            "country_consistency": {},
            "question_consistency": {}
        }
        
        # 分析每个国家在不同语言下的一致性
        for country in self.target_countries:
            country_consistency = self._calculate_country_consistency(
                analysis_results, country
            )
            consistency["country_consistency"][country] = country_consistency
        
        return consistency
    
    def _calculate_country_consistency(self, analysis_results: Dict, country: str) -> Dict[str, float]:
        """计算单个国家的跨语言一致性"""
        # 提取该国家在所有语言下的响应
        country_responses = {}
        
        for language, results in analysis_results.items():
            if 'raw_responses' in results and country in results['raw_responses']:
                country_responses[language] = results['raw_responses'][country]
        
        if len(country_responses) < 2:
            return {"consistency_score": 0, "languages_compared": len(country_responses)}
        
        # 计算响应一致性（简化版本）
        consistency_scores = []
        languages = list(country_responses.keys())
        
        for i, lang1 in enumerate(languages):
            for lang2 in languages[i+1:]:
                score = self._compare_response_patterns(
                    country_responses[lang1], country_responses[lang2]
                )
                consistency_scores.append(score)
        
        return {
            "consistency_score": np.mean(consistency_scores) if consistency_scores else 0,
            "languages_compared": len(country_responses)
        }
    
    def _compare_response_patterns(self, responses1: Dict, responses2: Dict) -> float:
        """比较两组响应的模式相似性"""
        common_questions = set(responses1.keys()) & set(responses2.keys())
        
        if not common_questions:
            return 0
        
        matches = 0
        total = 0
        
        for question in common_questions:
            try:
                val1 = float(responses1[question])
                val2 = float(responses2[question])
                
                # 计算相对差异
                if val1 == val2:
                    matches += 1
                elif abs(val1 - val2) <= 1:  # 允许1个单位的差异
                    matches += 0.5
                
                total += 1
            except (ValueError, TypeError):
                continue
        
        return matches / total if total > 0 else 0
    
    def _analyze_cultural_preservation(self, analysis_results: Dict) -> Dict[str, Any]:
        """分析文化特征保持情况"""
        preservation = {
            "cultural_distinctiveness": {},
            "language_effect_strength": 0
        }
        
        # 分析每种语言是否保持了文化特征
        for language in analysis_results:
            distinctiveness = self._calculate_cultural_distinctiveness(
                analysis_results[language]
            )
            preservation["cultural_distinctiveness"][language] = distinctiveness
        
        return preservation
    
    def _calculate_cultural_distinctiveness(self, language_results: Dict) -> Dict[str, float]:
        """计算文化区分度"""
        # 简化的文化区分度计算
        if 'pca_coordinates' not in language_results:
            return {"distinctiveness_score": 0}
        
        coords = language_results['pca_coordinates']
        
        # 计算国家间的平均距离作为区分度指标
        countries = list(coords.keys())
        distances = []
        
        for i, country1 in enumerate(countries):
            for country2 in countries[i+1:]:
                pc1_diff = coords[country1]['PC1'] - coords[country2]['PC1']
                pc2_diff = coords[country1]['PC2'] - coords[country2]['PC2']
                distance = np.sqrt(pc1_diff**2 + pc2_diff**2)
                distances.append(distance)
        
        return {
            "distinctiveness_score": np.mean(distances) if distances else 0,
            "countries_analyzed": len(countries)
        }
    
    def _analyze_distance_to_real_countries(self, analysis_results: Dict) -> Dict[str, Any]:
        """分析LLM模仿效果与真实国家的距离对比"""
        print("🔍 分析语言模仿效果与真实国家的距离...")
        
        # 加载真实国家的IVS数据作为基准
        try:
            analyzer = ControlledMultilingualPCA(data_path=str(self.data_path))
            if not analyzer.load_base_data():
                print("  ⚠️ 无法加载真实国家数据")
                return {}
            
            # 获取真实国家的PCA坐标
            real_country_results = analyzer.perform_pca_analysis(analyzer.prepare_ivs_data())
            real_coordinates = analyzer._extract_coordinates(real_country_results)
            
            print(f"  📍 真实国家基准: {len(real_coordinates)} 个国家")
            
            distance_analysis = {}
            
            # 对每种语言分析
            for language, lang_results in analysis_results.items():
                llm_coordinates = lang_results.get('pca_coordinates', {})
                
                language_distances = {}
                
                # 计算每个国家的LLM模仿效果与真实国家的距离
                for country_name in llm_coordinates.keys():
                    if country_name in real_coordinates:
                        try:
                            llm_coord = llm_coordinates[country_name]
                            real_coord = real_coordinates[country_name]
                            
                            if isinstance(llm_coord, dict) and isinstance(real_coord, dict):
                                pc1_diff = llm_coord.get('PC1', 0) - real_coord.get('PC1', 0)
                                pc2_diff = llm_coord.get('PC2', 0) - real_coord.get('PC2', 0)
                                distance = np.sqrt(pc1_diff**2 + pc2_diff**2)
                                
                                language_distances[country_name] = {
                                    'distance': float(distance),
                                    'llm_position': llm_coord,
                                    'real_position': real_coord,
                                    'pc1_diff': float(pc1_diff),
                                    'pc2_diff': float(pc2_diff)
                                }
                        except (KeyError, TypeError) as e:
                            print(f"  ⚠️ 计算{country_name}距离时出错: {e}")
                            continue
                
                if language_distances:
                    # 计算统计指标
                    distances = [d['distance'] for d in language_distances.values()]
                    distance_analysis[language] = {
                        'country_distances': language_distances,
                        'average_distance': float(np.mean(distances)),
                        'min_distance': float(np.min(distances)),
                        'max_distance': float(np.max(distances)),
                        'std_distance': float(np.std(distances)),
                        'total_countries': len(language_distances)
                    }
                    
                    print(f"  📊 {language}: 平均距离 {distance_analysis[language]['average_distance']:.3f} ({len(language_distances)}个国家)")
            
            # 特别分析：英文 vs 本国语言的模仿效果对比
            native_vs_english_analysis = self._analyze_native_vs_english_performance(
                distance_analysis, analysis_results
            )
            
            # 比较不同语言的模仿效果
            if len(distance_analysis) >= 2:
                languages = list(distance_analysis.keys())
                comparison = {}
                
                for i, lang1 in enumerate(languages):
                    for lang2 in languages[i+1:]:
                        avg_dist1 = distance_analysis[lang1]['average_distance']
                        avg_dist2 = distance_analysis[lang2]['average_distance']
                        
                        better_language = lang1 if avg_dist1 < avg_dist2 else lang2
                        improvement = abs(avg_dist1 - avg_dist2)
                        
                        comparison[f"{lang1}_vs_{lang2}"] = {
                            'better_language': better_language,
                            'improvement': float(improvement),
                            'improvement_percentage': float(improvement / max(avg_dist1, avg_dist2) * 100)
                        }
                
                distance_analysis['language_comparison'] = comparison
            
            # 添加本国语言vs英文的特别分析
            distance_analysis['native_vs_english_analysis'] = native_vs_english_analysis
            
            return distance_analysis
            
        except Exception as e:
            print(f"  ❌ 距离分析失败: {e}")
            return {}
    
    def _analyze_native_vs_english_performance(self, distance_analysis: Dict, analysis_results: Dict) -> Dict[str, Any]:
        """分析本国语言vs英文的模仿效果对比"""
        print("  🎯 分析本国语言 vs 英文模仿效果...")
        
        # 定义语言-国家对应关系
        language_country_mapping = {
            'zh-cn': 'China',
            'ru': 'Russian Federation', 
            'es': 'Mexico',
            'ar': 'Egypt'
        }
        
        native_vs_english = {}
        
        # 检查是否有英文数据
        if 'en' not in distance_analysis:
            print("    ⚠️ 缺少英文基准数据")
            return {}
        
        english_distances = distance_analysis['en']['country_distances']
        
        for native_lang, target_country in language_country_mapping.items():
            if native_lang in distance_analysis:
                native_distances = distance_analysis[native_lang]['country_distances']
                
                # 检查该国家是否在两种语言的数据中都存在
                if target_country in english_distances and target_country in native_distances:
                    english_dist = english_distances[target_country]['distance']
                    native_dist = native_distances[target_country]['distance']
                    
                    # 计算改进效果
                    improvement = english_dist - native_dist
                    improvement_percentage = (improvement / english_dist * 100) if english_dist > 0 else 0
                    
                    better_language = native_lang if native_dist < english_dist else 'en'
                    
                    native_vs_english[f"{native_lang}_{target_country}"] = {
                        'target_country': target_country,
                        'native_language': native_lang,
                        'english_distance': float(english_dist),
                        'native_distance': float(native_dist),
                        'improvement': float(improvement),
                        'improvement_percentage': float(improvement_percentage),
                        'better_language': better_language,
                        'native_better': native_dist < english_dist
                    }
                    
                    status = "✅ 更好" if native_dist < english_dist else "❌ 更差"
                    print(f"    📍 {target_country} ({native_lang}): 英文距离={english_dist:.3f}, 本国语言距离={native_dist:.3f} {status}")
        
        # 计算总体统计
        if native_vs_english:
            improvements = [data['improvement'] for data in native_vs_english.values()]
            native_better_count = sum(1 for data in native_vs_english.values() if data['native_better'])
            total_comparisons = len(native_vs_english)
            
            summary = {
                'total_comparisons': total_comparisons,
                'native_better_count': native_better_count,
                'native_better_percentage': float(native_better_count / total_comparisons * 100),
                'average_improvement': float(np.mean(improvements)),
                'median_improvement': float(np.median(improvements)),
                'std_improvement': float(np.std(improvements))
            }
            
            native_vs_english['summary'] = summary
            
            print(f"  📊 总体结果: {native_better_count}/{total_comparisons} 个国家的本国语言表现更好 ({summary['native_better_percentage']:.1f}%)")
            print(f"  📈 平均改进: {summary['average_improvement']:.3f}")
        
        return native_vs_english


class ControlledLanguageInterview(BaseInterview):
    """特定语言的控制访谈"""
    
    def __init__(self, language: str, config: Dict, data_path: str = "data"):
        super().__init__(repeat_count=config["repeat_count"], data_path=data_path)
        self.language = language
        self.config = config
        self.language_config = config["languages"][language]
    
    def interview_all_countries(self) -> Dict[str, Any]:
        """访谈所有目标国家"""
        results = {}
        total_interviews = len(self.config["target_countries"]) * len(self.config["models"]) * self.config["repeat_count"]
        completed_interviews = 0
        
        for country in self.config["target_countries"]:
            print(f"  🏛️ 访谈 {country} ({self.language})")
            country_results = {}
            
            for model in self.config["models"]:
                model_responses = []
                
                for repeat in range(self.config["repeat_count"]):
                    completed_interviews += 1
                    progress = (completed_interviews / total_interviews) * 100
                    print(f"    🤖 {model} - 第 {repeat+1} 次 [{progress:.1f}%]")
                    
                    try:
                        response = self._interview_country_model(country, model)
                        if response:
                            model_responses.append(response)
                            print(f"    ✅ 成功收集 {len(response.get('responses', {}))} 个响应")
                        else:
                            print(f"    ⚠️ 未收集到响应")
                    except Exception as e:
                        print(f"    ❌ 访谈出错: {e}")
                        continue
                    
                    # 添加延迟避免API限制
                    import time
                    time.sleep(self.config.get("delay_between_calls", 1.0))
                
                if model_responses:
                    country_results[model] = model_responses
                    print(f"    📊 {model}: 收集到 {len(model_responses)} 个完整响应")
            
            if country_results:
                results[country] = country_results
                print(f"  ✅ {country} 完成: {len(country_results)} 个模型")
            else:
                print(f"  ❌ {country} 失败: 未收集到任何响应")
        
        return results
    
    def interview_single_country(self, country: str) -> Dict[str, Any]:
        """访谈单个国家"""
        print(f"  🏛️ 访谈 {country} ({self.language})")
        country_results = {}
        
        total_interviews = len(self.config["models"]) * self.config["repeat_count"]
        completed_interviews = 0
        
        for model in self.config["models"]:
            model_responses = []
            
            for repeat in range(self.config["repeat_count"]):
                completed_interviews += 1
                progress = (completed_interviews / total_interviews) * 100
                print(f"    🤖 {model} - 第 {repeat+1} 次 [{progress:.1f}%]")
                
                try:
                    response = self._interview_country_model(country, model)
                    if response:
                        model_responses.append(response)
                        print(f"    ✅ 成功收集 {len(response.get('responses', {}))} 个响应")
                    else:
                        print(f"    ⚠️ 未收集到响应")
                except Exception as e:
                    print(f"    ❌ 访谈出错: {e}")
                    continue
                
                # 添加延迟避免API限制
                import time
                time.sleep(self.config.get("delay_between_calls", 1.0))
            
            if model_responses:
                country_results[model] = model_responses
                print(f"    📊 {model}: 收集到 {len(model_responses)} 个完整响应")
        
        if country_results:
            print(f"  ✅ {country} 完成: {len(country_results)} 个模型")
        else:
            print(f"  ❌ {country} 失败: 未收集到任何响应")
        
        return country_results
    
    def _load_multilingual_questions(self) -> Dict:
        """加载多语言问题配置"""
        try:
            # 尝试加载完整的多语言问题配置
            config_path = Path("config/multilingual_questions_complete.json")
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ 加载多语言问题配置失败: {e}")
        
        return {"languages": {}}
    
    def _interview_country_model(self, country: str, model: str) -> Optional[Dict]:
        """访谈特定国家和模型"""
        try:
            # 构建系统提示词
            country_context = self.language_config["country_contexts"].get(
                country, f"{country} 的文化背景"
            )
            
            system_prompt = self.language_config["system_prompt_template"].format(
                country=country,
                country_context=country_context
            )
            
            # 收集所有问题的响应
            responses = {}
            
            # 加载多语言问题配置
            multilingual_questions = self._load_multilingual_questions()
            
            for question_id in self.questions.get_question_ids():
                # 优先使用多语言配置中的问题文本
                if (self.language in multilingual_questions.get("languages", {}) and 
                    question_id in multilingual_questions["languages"][self.language].get("questions", {})):
                    question_data = multilingual_questions["languages"][self.language]["questions"][question_id]
                    question_text = question_data.get("question", "") if isinstance(question_data, dict) else str(question_data)
                else:
                    # 回退到默认问题文本
                    question_text = self.questions.get_question_text(question_id)
                
                # 调用API
                response = self.call_model_api(
                    model_name=model,
                    question_id=question_id,
                    question_text=question_text,
                    system_prompt=system_prompt,
                    temperature=self.config["temperature"],
                    max_tokens=self.config["max_tokens"]
                )
                
                if response:
                    responses[question_id] = response.strip()
                else:
                    responses[question_id] = ""
            
            return {
                "country": country,
                "model": model,
                "language": self.language,
                "system_prompt": system_prompt,
                "responses": responses,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"    ❌ 访谈失败: {e}")
            return None
    
    def interview_entity(self, model_name: str, entity_id: str) -> List[LLMResponse]:
        """实现基类抽象方法"""
        # 这里entity_id是国家名
        result = self._interview_country_model(entity_id, model_name)
        if result:
            responses = []
            for question_id, response_text in result["responses"].items():
                llm_response = LLMResponse(
                    model_name=model_name,
                    response=response_text,
                    question_id=question_id,
                    entity_id=entity_id,
                    timestamp=result["timestamp"]
                )
                responses.append(llm_response)
            return responses
        return []
    
    def batch_interview(self, model_names: List[str], entities: List[str]) -> Dict[str, Any]:
        """实现基类抽象方法"""
        results = {}
        for entity in entities:
            entity_results = {}
            for model in model_names:
                responses = self.interview_entity(model, entity)
                if responses:
                    entity_results[model] = responses
            if entity_results:
                results[entity] = entity_results
        return results


class ControlledMultilingualPCA(BasePCAAnalyzer):
    """控制变量的多语言PCA分析"""
    
    def __init__(self, data_path: str = "data"):
        super().__init__(data_path=data_path)
        self.temp_data_file = None
        
        # 加载基础数据（IVS数据和国家代码）
        if not self.load_base_data():
            print("⚠️ 基础数据加载失败，PCA分析可能无法正常进行")
    
    def load_additional_data(self) -> pd.DataFrame:
        """加载额外数据"""
        if self.temp_data_file and self.temp_data_file.exists():
            return pd.read_pickle(self.temp_data_file)
        return pd.DataFrame()
    
    def combine_data(self) -> pd.DataFrame:
        """合并IVS数据和多语言数据"""
        additional_data = self.load_additional_data()
        if additional_data.empty:
            print("⚠️ 多语言数据为空，仅使用IVS数据")
            return self.ivs_df.copy()
        
        try:
            # 使用预处理的IVS数据（重要！）
            ivs_data_copy = self.prepare_ivs_data()
            multilingual_data_copy = additional_data.copy()
            
            print(f"📊 IVS数据预处理:")
            print(f"   - 原始数据: {len(self.ivs_df)} 行")
            print(f"   - 预处理后: {len(ivs_data_copy)} 行")
            
            # 添加数据源标识
            ivs_data_copy['data_source'] = 'IVS'
            # 保持多语言数据的原始data_source（已经是语言_模型_国家格式）
            # multilingual_data_copy['data_source'] = 'Multilingual'  # 注释掉这行，保持原始格式
            
            # 高效的列对齐 - 使用reindex避免逐列添加
            all_columns = list(set(ivs_data_copy.columns) | set(multilingual_data_copy.columns))
            
            # 重新索引以对齐列，自动填充缺失列为NaN
            ivs_aligned = ivs_data_copy.reindex(columns=all_columns)
            multilingual_aligned = multilingual_data_copy.reindex(columns=all_columns)
            
            # 合并数据
            combined_data = pd.concat([
                ivs_aligned, 
                multilingual_aligned
            ], ignore_index=True)
            
            print(f"📊 数据合并完成:")
            print(f"   - 总计: {len(combined_data)} 行")
            print(f"   - IVS数据: {len(ivs_data_copy)} 行")
            print(f"   - 多语言数据: {len(multilingual_data_copy)} 行")
            
            return combined_data
            
        except Exception as e:
            print(f"❌ 数据合并失败: {e}")
            if self.ivs_df is not None:
                return self.prepare_ivs_data()
            else:
                return pd.DataFrame()
    
    def calculate_entity_scores(self, group_by: List[str] = None) -> pd.DataFrame:
        """计算实体分数 - 重写以支持多语言数据分组"""
        if group_by is None:
            # 对于多语言数据，每个data_source都应该是独立的实体
            # 同时保留country_code以便后续处理
            group_by = ['country_code', 'data_source']
        
        return super().calculate_entity_scores(group_by)
    
    def run_language_specific_analysis(self, language: str) -> Dict[str, Any]:
        """运行特定语言的分析"""
        print(f"🔬 执行 {language} 语言的PCA分析...")
        
        # 运行完整分析
        pca_results = self.run_full_analysis()
        
        # 添加语言特定信息
        results = {
            "language": language,
            "pca_results": pca_results,
            "pca_coordinates": self._extract_coordinates(pca_results),
            "analysis_summary": self._create_analysis_summary(pca_results, language)
        }
        
        return results
    
    def _extract_coordinates(self, pca_results: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """提取PCA坐标 - 支持多语言数据的坐标提取"""
        coordinates = {}
        
        # 检查可用的列名
        pc1_col = 'PC1_rescaled' if 'PC1_rescaled' in pca_results.columns else 'PC1'
        pc2_col = 'PC2_rescaled' if 'PC2_rescaled' in pca_results.columns else 'PC2'
        
        for _, row in pca_results.iterrows():
            country_name = row.get('Country', row.get('country_name', 'Unknown'))
            
            # 跳过无效的国家名
            if pd.isna(country_name) or country_name == 'Unknown' or str(country_name).lower() == 'nan':
                continue
            
            # 为多语言数据创建唯一标识符
            data_source = row.get('data_source', 'IVS')
            model = row.get('model', '')
            
            # 判断是否为LLM数据（数据源不是'IVS'且包含下划线）
            is_llm_data = data_source != 'IVS' and '_' in str(data_source)
            
            if is_llm_data:
                # 对于LLM数据，直接使用数据源作为键（已经是语言_模型_国家格式）
                key = str(data_source)
            else:
                # 对于IVS数据，直接使用国家名
                key = str(country_name)
                
            coordinates[key] = {
                'PC1': float(row.get(pc1_col, 0)),
                'PC2': float(row.get(pc2_col, 0)),
                'country': str(country_name),
                'data_source': data_source,
                'model': model,
                'is_llm': is_llm_data
            }
        
        return coordinates
    
    def _extract_language_coordinates(self, pca_results: pd.DataFrame, language: str) -> Dict[str, Dict[str, float]]:
        """从统一PCA结果中提取特定语言的坐标"""
        coordinates = {}
        
        # 检查可用的列名
        pc1_col = 'PC1_rescaled' if 'PC1_rescaled' in pca_results.columns else 'PC1'
        pc2_col = 'PC2_rescaled' if 'PC2_rescaled' in pca_results.columns else 'PC2'
        
        for _, row in pca_results.iterrows():
            country_name = row.get('Country', row.get('country_name', 'Unknown'))
            data_source = row.get('data_source', 'IVS')
            
            # 跳过无效的国家名
            if pd.isna(country_name) or country_name == 'Unknown' or str(country_name).lower() == 'nan':
                continue
            
            # 包含IVS数据和该语言的LLM数据
            is_ivs_data = data_source == 'IVS'
            is_target_language = data_source.startswith(f'{language}_')
            
            if is_ivs_data or is_target_language:
                # 判断是否为LLM数据
                is_llm_data = not is_ivs_data and '_' in str(data_source)
                
                if is_llm_data:
                    # 对于LLM数据，使用数据源作为键
                    key = str(data_source)
                else:
                    # 对于IVS数据，使用国家名作为键
                    key = str(country_name)
                    
                coordinates[key] = {
                    'PC1': float(row.get(pc1_col, 0)),
                    'PC2': float(row.get(pc2_col, 0)),
                    'country': str(country_name),
                    'data_source': data_source,
                    'model': row.get('model', ''),
                    'is_llm': is_llm_data
                }
        
        return coordinates
    
    def _create_analysis_summary(self, pca_results: pd.DataFrame, language: str) -> Dict[str, Any]:
        """创建分析摘要"""
        # 检查可用的列名
        pc1_col = 'PC1_rescaled' if 'PC1_rescaled' in pca_results.columns else 'PC1'
        pc2_col = 'PC2_rescaled' if 'PC2_rescaled' in pca_results.columns else 'PC2'
        
        return {
            "language": language,
            "total_entities": len(pca_results),
            "pc1_range": [float(pca_results[pc1_col].min()), float(pca_results[pc1_col].max())],
            "pc2_range": [float(pca_results[pc2_col].min()), float(pca_results[pc2_col].max())],
            "analysis_timestamp": datetime.now().isoformat(),
            "columns_used": {"pc1": pc1_col, "pc2": pc2_col}
        }


class ControlledMultilingualVisualization(BaseCulturalMapVisualizer):
    """控制变量的多语言可视化"""
    
    def __init__(self, data_path: str = "data"):
        super().__init__(data_path=data_path)
        self.results_dir = self.data_path / "results" / "controlled_multilingual_experiment"
    
    def load_data(self) -> Optional[pd.DataFrame]:
        """加载数据"""
        # 这个方法在对比可视化中不直接使用
        return None
    
    def create_language_comparison_plots(self, analysis_results: Dict) -> Dict[str, Any]:
        """创建语言对比图表"""
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        plt.style.use('default')
        
        # 1. 创建多语言PCA对比图
        comparison_plot = self._create_multilingual_pca_comparison(analysis_results)
        
        # 2. 创建语言差异热图
        difference_heatmap = self._create_language_difference_heatmap(analysis_results)
        
        # 3. 创建一致性分析图
        consistency_plot = self._create_consistency_analysis_plot(analysis_results)
        
        return {
            "multilingual_pca_comparison": comparison_plot,
            "language_difference_heatmap": difference_heatmap,
            "consistency_analysis": consistency_plot
        }
    
    def _create_multilingual_pca_comparison(self, analysis_results: Dict) -> str:
        """创建多语言PCA对比图"""
        import matplotlib.pyplot as plt
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()
        
        languages = list(analysis_results.keys())
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown']
        
        for i, language in enumerate(languages):
            if i >= len(axes):
                break
                
            ax = axes[i]
            coords = analysis_results[language].get('pca_coordinates', {})
            
            if coords:
                countries = list(coords.keys())
                pc1_values = []
                pc2_values = []
                
                # 安全地提取坐标值
                for country in countries:
                    coord = coords[country]
                    if isinstance(coord, dict):
                        pc1_values.append(coord.get('PC1', 0))
                        pc2_values.append(coord.get('PC2', 0))
                    else:
                        print(f"  ⚠️ 跳过无效坐标格式: {country} ({type(coord)})")
                        continue
                
                # 只有在有有效数据时才绘制
                if pc1_values and pc2_values and len(pc1_values) == len(pc2_values):
                    ax.scatter(pc1_values, pc2_values, c=colors[i % len(colors)], 
                              alpha=0.7, s=100, label=language)
                    
                    # 添加国家标签（只为有效坐标添加）
                    valid_countries = []
                    for country in countries:
                        coord = coords[country]
                        if isinstance(coord, dict):
                            valid_countries.append(country)
                    
                    # 确保标签数量与坐标数量匹配
                    for j, country in enumerate(valid_countries):
                        if j < len(pc1_values) and j < len(pc2_values):
                            try:
                                ax.annotate(country[:3], (pc1_values[j], pc2_values[j]), 
                                          xytext=(5, 5), textcoords='offset points', fontsize=8)
                            except (TypeError, IndexError) as e:
                                print(f"  ⚠️ 标签添加失败 ({country}): {e}")
                                continue
                else:
                    print(f"  ⚠️ {language}: 无有效坐标数据")
            
            ax.set_xlabel('PC1')
            ax.set_ylabel('PC2')
            ax.set_title(f'{language} Language')
            ax.grid(True, alpha=0.3)
            ax.legend()
        
        # 隐藏多余的子图
        for i in range(len(languages), len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        
        # 保存图表
        plot_file = self.results_dir / "multilingual_pca_comparison.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(plot_file)
    
    def _create_language_difference_heatmap(self, analysis_results: Dict) -> str:
        """创建语言差异热图"""
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        languages = list(analysis_results.keys())
        n_langs = len(languages)
        
        # 检查是否有足够的数据
        if n_langs < 2:
            print("  ⚠️ 语言数量不足，跳过热图生成")
            return ""
        
        # 计算语言间距离矩阵
        distance_matrix = np.zeros((n_langs, n_langs))
        
        for i, lang1 in enumerate(languages):
            for j, lang2 in enumerate(languages):
                if i != j:
                    coords1 = analysis_results[lang1].get('pca_coordinates', {})
                    coords2 = analysis_results[lang2].get('pca_coordinates', {})
                    
                    distance = self._calculate_language_distance(coords1, coords2)
                    distance_matrix[i, j] = distance
        
        # 检查距离矩阵是否有有效数据
        if distance_matrix.size == 0 or np.all(distance_matrix == 0):
            print("  ⚠️ 距离矩阵为空或全零，跳过热图生成")
            return ""
        
        # 创建热图
        plt.figure(figsize=(10, 8))
        sns.heatmap(distance_matrix, 
                   xticklabels=languages, 
                   yticklabels=languages,
                   annot=True, 
                   fmt='.3f',
                   cmap='YlOrRd',
                   cbar_kws={'label': 'Average Distance'})
        
        plt.title('Language Difference Heatmap\n(Average PCA Coordinate Distance)')
        plt.tight_layout()
        
        # 保存图表
        plot_file = self.results_dir / "language_difference_heatmap.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(plot_file)
    
    def _calculate_language_distance(self, coords1: Dict, coords2: Dict) -> float:
        """计算两种语言间的平均距离"""
        common_countries = set(coords1.keys()) & set(coords2.keys())
        
        if not common_countries:
            return 0
        
        distances = []
        for country in common_countries:
            try:
                # 确保坐标是字典格式
                coord1 = coords1[country]
                coord2 = coords2[country]
                
                # 如果坐标不是字典，跳过
                if not isinstance(coord1, dict) or not isinstance(coord2, dict):
                    print(f"  ⚠️ 跳过无效坐标格式: {country}")
                    continue
                
                pc1_diff = coord1.get('PC1', 0) - coord2.get('PC1', 0)
                pc2_diff = coord1.get('PC2', 0) - coord2.get('PC2', 0)
                distance = np.sqrt(pc1_diff**2 + pc2_diff**2)
                distances.append(distance)
            except (KeyError, TypeError) as e:
                print(f"  ⚠️ 计算距离时出错 ({country}): {e}")
                continue
        
        return np.mean(distances) if distances else 0
    
    def _create_consistency_analysis_plot(self, analysis_results: Dict) -> str:
        """创建一致性分析图"""
        import matplotlib.pyplot as plt
        
        # 计算每个国家的跨语言一致性
        countries = set()
        for lang_results in analysis_results.values():
            countries.update(lang_results.get('pca_coordinates', {}).keys())
        
        # 过滤掉NaN值和无效的国家名
        valid_countries = []
        for country in countries:
            if isinstance(country, str) and country.strip() and country.lower() != 'nan':
                valid_countries.append(country)
        
        countries = sorted(valid_countries)
        consistency_scores = []
        
        for country in countries:
            # 收集该国家在所有语言下的坐标
            country_coords = []
            for lang_results in analysis_results.values():
                coords = lang_results.get('pca_coordinates', {})
                if country in coords:
                    country_coords.append([coords[country]['PC1'], coords[country]['PC2']])
            
            if len(country_coords) > 1:
                # 计算坐标的标准差作为一致性指标
                coords_array = np.array(country_coords)
                consistency = np.mean(np.std(coords_array, axis=0))
                consistency_scores.append(consistency)
            else:
                consistency_scores.append(0)
        
        # 创建条形图
        plt.figure(figsize=(12, 8))
        bars = plt.bar(range(len(countries)), consistency_scores)
        
        # 颜色编码：一致性越高（数值越小）颜色越绿
        max_score = max(consistency_scores) if consistency_scores else 1
        for i, bar in enumerate(bars):
            # 避免除零错误
            if max_score > 0:
                normalized_score = consistency_scores[i] / max_score
            else:
                normalized_score = 0
            color = plt.cm.RdYlGn(1 - normalized_score)  # 反转颜色映射
            bar.set_color(color)
        
        plt.xlabel('Countries')
        plt.ylabel('Inconsistency Score (Lower is Better)')
        plt.title('Cross-Language Consistency Analysis\n(PCA Coordinate Variability)')
        plt.xticks(range(len(countries)), countries, rotation=45, ha='right')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # 保存图表
        plot_file = self.results_dir / "consistency_analysis.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(plot_file)


def main():
    """主函数"""
    print("🎯 控制变量多语言对比实验")
    print("=" * 60)
    
    # 创建实验实例
    experiment = ControlledMultilingualExperiment()
    
    # 运行完整实验
    results = experiment.run_controlled_experiment()
    
    print("\n📊 实验结果摘要:")
    print(f"   - 测试语言: {len(results['interview_results'])} 种")
    print(f"   - 测试国家: {len(results['experiment_config']['target_countries'])} 个")
    print(f"   - 使用模型: {len(results['experiment_config']['models'])} 个")
    print(f"   - 重复次数: {results['experiment_config']['repeat_count']} 次")
    
    return results


if __name__ == "__main__":
    main()
