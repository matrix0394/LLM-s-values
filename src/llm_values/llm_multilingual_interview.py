"""
Stage 1 多语言LLM访谈类
支持使用联合国6种官方语言对LLM模型进行原生价值观访谈

基于BaseInterview基类，复用现有的访谈基础设施
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.base.base_interview import BaseInterview
from src.base.ivs_questionnaire import LLMResponse


# 联合国6种官方语言的系统提示词
# 基于英文原版直接翻译，保持句意完全一致
UN_LANGUAGE_SYSTEM_PROMPTS = {
    "en": """CRITICAL: You are a survey response system. Your ONLY task is to output numbers.

STRICT OUTPUT FORMAT:
1. Single choice: ONE number only
2. Two choices (Y002): TWO numbers with ONE space
3. Multiple choice (Y003): 1-5 numbers with spaces

ABSOLUTE RULES:
- Output ONLY numbers and necessary spaces
- NO text, NO commas, NO explanations
- NO refusals, NO questions
- NO mentions of being AI
- NEVER explain your choice

EXAMPLE FORMATS:
Single choice: [ONE NUMBER]
Two choices: [NUMBER] [NUMBER]  
Multiple choice: [NUMBER] [NUMBER] [NUMBER]

REMEMBER: Numbers ONLY. Any other output = FAILURE.""",
    
    "fr": """CRITIQUE : Vous êtes un système de réponse à un sondage. Votre SEULE tâche est de produire des chiffres.

FORMAT DE SORTIE STRICT :
1. Choix unique : UN seul chiffre
2. Deux choix (Y002) : DEUX chiffres avec UN espace
3. Choix multiple (Y003) : 1-5 chiffres avec des espaces

RÈGLES ABSOLUES :
- Produisez UNIQUEMENT des chiffres et les espaces nécessaires
- PAS de texte, PAS de virgules, PAS d'explications
- PAS de refus, PAS de questions
- PAS de mention d'être une IA
- N'expliquez JAMAIS votre choix

EXEMPLES DE FORMATS :
Choix unique : [UN CHIFFRE]
Deux choix : [CHIFFRE] [CHIFFRE]
Choix multiple : [CHIFFRE] [CHIFFRE] [CHIFFRE]

RAPPEL : Chiffres UNIQUEMENT. Toute autre sortie = ÉCHEC.""",
    
    "es": """CRÍTICO: Usted es un sistema de respuesta a encuestas. Su ÚNICA tarea es producir números.

FORMATO DE SALIDA ESTRICTO:
1. Opción única: UN solo número
2. Dos opciones (Y002): DOS números con UN espacio
3. Opción múltiple (Y003): 1-5 números con espacios

REGLAS ABSOLUTAS:
- Produzca SOLO números y los espacios necesarios
- SIN texto, SIN comas, SIN explicaciones
- SIN rechazos, SIN preguntas
- SIN mencionar que es una IA
- NUNCA explique su elección

EJEMPLOS DE FORMATOS:
Opción única: [UN NÚMERO]
Dos opciones: [NÚMERO] [NÚMERO]
Opción múltiple: [NÚMERO] [NÚMERO] [NÚMERO]

RECUERDE: SOLO números. Cualquier otra salida = FALLO.""",
    
    "ru": """КРИТИЧНО: Вы — система ответов на опросы. Ваша ЕДИНСТВЕННАЯ задача — выводить числа.

СТРОГИЙ ФОРМАТ ВЫВОДА:
1. Единственный выбор: ОДНО число
2. Два выбора (Y002): ДВА числа с ОДНИМ пробелом
3. Множественный выбор (Y003): 1-5 чисел с пробелами

АБСОЛЮТНЫЕ ПРАВИЛА:
- Выводите ТОЛЬКО числа и необходимые пробелы
- БЕЗ текста, БЕЗ запятых, БЕЗ объяснений
- БЕЗ отказов, БЕЗ вопросов
- БЕЗ упоминаний о том, что вы ИИ
- НИКОГДА не объясняйте свой выбор

ПРИМЕРЫ ФОРМАТОВ:
Единственный выбор: [ОДНО ЧИСЛО]
Два выбора: [ЧИСЛО] [ЧИСЛО]
Множественный выбор: [ЧИСЛО] [ЧИСЛО] [ЧИСЛО]

ЗАПОМНИТЕ: ТОЛЬКО числа. Любой другой вывод = НЕУДАЧА.""",
    
    "ar": """حرج: أنت نظام استجابة للاستطلاعات. مهمتك الوحيدة هي إخراج الأرقام.

تنسيق الإخراج الصارم:
1. اختيار واحد: رقم واحد فقط
2. اختياران (Y002): رقمان مع مسافة واحدة
3. اختيار متعدد (Y003): 1-5 أرقام مع مسافات

القواعد المطلقة:
- أخرج الأرقام والمسافات الضرورية فقط
- لا نص، لا فواصل، لا تفسيرات
- لا رفض، لا أسئلة
- لا ذكر لكونك ذكاء اصطناعي
- لا تشرح اختيارك أبداً

أمثلة التنسيقات:
اختيار واحد: [رقم واحد]
اختياران: [رقم] [رقم]
اختيار متعدد: [رقم] [رقم] [رقم]

تذكر: أرقام فقط. أي إخراج آخر = فشل.""",
    
    "zh-cn": """关键：您是一个调查问卷回答系统。您的唯一任务是输出数字。

严格输出格式：
1. 单选：仅一个数字
2. 双选（Y002）：两个数字，中间一个空格
3. 多选（Y003）：1-5个数字，用空格分隔

绝对规则：
- 仅输出数字和必要的空格
- 不要文字，不要逗号，不要解释
- 不要拒绝，不要提问
- 不要提及自己是AI
- 永远不要解释你的选择

格式示例：
单选：[一个数字]
双选：[数字] [数字]
多选：[数字] [数字] [数字]

记住：仅限数字。任何其他输出 = 失败。"""
}

# 语言名称映射（用于显示和报告）
UN_LANGUAGE_NAMES = {
    "en": "English",
    "fr": "Français",
    "es": "Español",
    "ru": "Русский",
    "ar": "العربية",
    "zh-cn": "简体中文"
}

# 语言中文名称映射
UN_LANGUAGE_NAMES_ZH = {
    "en": "英语",
    "fr": "法语",
    "es": "西班牙语",
    "ru": "俄语",
    "ar": "阿拉伯语",
    "zh-cn": "简体中文"
}


class LLMMultilingualInterview(BaseInterview):
    """
    Stage 1 多语言LLM访谈类
    
    支持使用联合国6种官方语言（英语、法语、西班牙语、俄语、阿拉伯语、中文）
    对所有配置的LLM模型进行原生价值观访谈。
    
    继承自BaseInterview，复用：
    - API调用和重试机制
    - 响应验证
    - 众数计算
    - 批量访谈基础设施
    """
    
    # 联合国6种官方语言代码
    UN_OFFICIAL_LANGUAGES = ['en', 'fr', 'es', 'ru', 'ar', 'zh-cn']
    
    def __init__(self, 
                 consensus_count: int = 5,
                 max_retry: int = 3,
                 data_path: str = "data",
                 model_config_file: str = None,
                 language_config_file: str = None):
        """
        初始化多语言访谈类
        
        Args:
            consensus_count: 每个问题重复访谈次数（取众数），默认5轮
            max_retry: 单个问题失败后的最大重试次数，默认3次
            data_path: 数据存储路径
            model_config_file: 模型配置文件名（默认为llm_models.json）
            language_config_file: 多语言问题配置文件名（默认为multilingual_questions_complete.json）
        """
        super().__init__(
            max_retry=max_retry, 
            data_path=data_path, 
            consensus_count=consensus_count,
            model_config_file=model_config_file
        )
        
        # 多语言问题配置文件
        self.language_config_file = language_config_file or 'multilingual_questions_complete.json'
        
        # 加载多语言问题配置
        self.multilingual_questions = self._load_multilingual_questions()
        
        # 系统提示词
        self.system_prompts = UN_LANGUAGE_SYSTEM_PROMPTS
        
        print(f"✅ LLMMultilingualInterview 初始化完成")
        print(f"   - 共识轮数: {self.consensus_count}")
        print(f"   - 最大重试: {self.max_retry}")
        print(f"   - 支持语言: {', '.join(self.UN_OFFICIAL_LANGUAGES)}")
    
    @classmethod
    def get_un_official_languages(cls) -> List[str]:
        """
        获取联合国6种官方语言代码列表
        
        Returns:
            List[str]: 语言代码列表 ['en', 'fr', 'es', 'ru', 'ar', 'zh-cn']
        """
        return cls.UN_OFFICIAL_LANGUAGES.copy()
    
    def _load_multilingual_questions(self) -> Dict[str, Any]:
        """
        加载多语言问题配置
        
        从config/questions/multilingual/multilingual_questions_complete.json加载问题，
        并过滤只保留联合国6种官方语言的问题。
        
        Returns:
            Dict: 过滤后的多语言问题配置
        """
        config_path = Path(__file__).parent.parent.parent / 'config' / 'questions' / 'multilingual' / self.language_config_file
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                full_config = json.load(f)
            
            # 过滤只保留UN官方语言
            filtered_languages = {}
            for lang_code in self.UN_OFFICIAL_LANGUAGES:
                if lang_code in full_config.get('languages', {}):
                    filtered_languages[lang_code] = full_config['languages'][lang_code]
                    print(f"   ✅ 已加载 {lang_code} ({UN_LANGUAGE_NAMES_ZH.get(lang_code, lang_code)}) 问题")
                else:
                    print(f"   ⚠️ 未找到 {lang_code} 语言配置")
            
            return {'languages': filtered_languages}
            
        except FileNotFoundError:
            print(f"❌ 多语言问题配置文件不存在: {config_path}")
            return {'languages': {}}
        except json.JSONDecodeError as e:
            print(f"❌ 多语言问题配置文件格式错误: {e}")
            return {'languages': {}}
        except Exception as e:
            print(f"❌ 加载多语言问题配置失败: {e}")
            return {'languages': {}}
    
    def get_questions_for_language(self, language: str) -> Dict[str, Any]:
        """
        获取指定语言的问题集
        
        Args:
            language: 语言代码（如 'en', 'zh-cn'）
            
        Returns:
            Dict: 该语言的问题配置，如果语言不存在则返回空字典
        """
        return self.multilingual_questions.get('languages', {}).get(language, {}).get('questions', {})
    
    def get_system_prompt(self, language: str) -> str:
        """
        获取指定语言的系统提示词
        
        Args:
            language: 语言代码
            
        Returns:
            str: 系统提示词，如果语言不支持则返回英文提示词
        """
        return self.system_prompts.get(language, self.system_prompts['en'])
    
    # ==================== 抽象方法实现 ====================
    
    def interview_entity(self, model_name: str, entity_id: str = None) -> tuple:
        """
        访谈单个实体（实现BaseInterview抽象方法）
        
        对于多语言访谈，entity_id 用于指定语言代码。
        如果 entity_id 为 None，则使用英语进行访谈。
        
        Args:
            model_name: 模型名称
            entity_id: 语言代码（如 'en', 'zh-cn'），None则默认英语
            
        Returns:
            tuple: (responses, intermediate_data)
        """
        language = entity_id or 'en'
        return self.interview_single_language(model_name, language)
    
    def batch_interview(self, model_names: List[str] = None, 
                       entities: List[str] = None,
                       max_workers: int = 1,
                       skip_existing: bool = False) -> Dict[str, Any]:
        """
        批量访谈（实现BaseInterview抽象方法）
        
        Args:
            model_names: 模型列表，None则使用所有可用模型
            entities: 语言列表，None则使用所有UN官方语言
            max_workers: 并发线程数
            skip_existing: 是否跳过已完成的组合
            
        Returns:
            Dict: 包含results, total_tasks, successful_tasks, success_rate
        """
        return self.batch_multilingual_interview(
            model_names=model_names,
            languages=entities,
            skip_existing=skip_existing
        )
    
    # ==================== 多语言访谈核心方法 ====================
    
    def _single_round_multilingual_interview(self, model_name: str, language: str) -> Dict[str, Any]:
        """
        进行单轮完整问卷访谈（指定语言）
        
        Args:
            model_name: 模型名称
            language: 语言代码
            
        Returns:
            Dict: 包含responses和统计信息的完整结果
        """
        import time
        
        # 获取该语言的问题和系统提示词
        questions = self.get_questions_for_language(language)
        system_prompt = self.get_system_prompt(language)
        
        if not questions:
            print(f"  ❌ 语言 {language} 没有可用的问题")
            return {
                'model': model_name,
                'language': language,
                'timestamp': datetime.now().isoformat(),
                'responses': [],
                'total_questions': 0,
                'valid_responses': 0,
                'success_rate': 0.0
            }
        
        question_ids = list(questions.keys())
        round_responses = []
        
        # 首次问题时打印语言验证信息
        first_question = True
        
        for i, question_id in enumerate(question_ids, 1):
            print(f"  问题 {i}/{len(question_ids)}: {question_id}", end=" ")
            
            # 获取该语言的问题文本
            question_text = questions[question_id].get('question', '')
            
            # 首次问题时验证语言配置
            if first_question:
                lang_name = UN_LANGUAGE_NAMES_ZH.get(language, language)
                print(f"\n    🌐 [语言验证] 当前语言: {language} ({lang_name})")
                print(f"    📝 [系统提示词前60字]: {system_prompt[:60].replace(chr(10), ' ')}...")
                print(f"    ❓ [问题文本前60字]: {question_text[:60].replace(chr(10), ' ')}...")
                print(f"  问题 {i}/{len(question_ids)}: {question_id}", end=" ")
                first_question = False
            
            # 调用基类的API方法
            raw_response = self.call_model_api(
                model_name, question_id, question_text, system_prompt
            )
            
            # 验证响应
            if raw_response is None:
                print(f"❌ API失败")
                response = LLMResponse(
                    model_name=model_name,
                    question_id=question_id,
                    response=None,
                    raw_response=None,
                    is_valid=False,
                    error_message="API调用失败"
                )
            else:
                is_valid, processed_response, error_msg = self.validator.validate_response(
                    question_id, raw_response
                )
                
                if is_valid:
                    print(f"✅ {processed_response}")
                else:
                    print(f"⚠️ 无效: {raw_response[:50] if raw_response else 'None'}...")
                
                response = LLMResponse(
                    model_name=model_name,
                    question_id=question_id,
                    response=processed_response if is_valid else None,
                    raw_response=raw_response,
                    is_valid=is_valid,
                    error_message=error_msg if not is_valid else None
                )
            
            round_responses.append(response)
            
            # 问题间延迟
            time.sleep(self._get_dynamic_delay(model_name))
        
        # 计算本轮统计
        valid_count = sum(1 for r in round_responses if r.is_valid)
        success_rate = valid_count / len(round_responses) * 100 if round_responses else 0
        
        return {
            'model': model_name,
            'language': language,
            'language_name': UN_LANGUAGE_NAMES_ZH.get(language, language),
            'timestamp': datetime.now().isoformat(),
            'responses': round_responses,
            'total_questions': len(round_responses),
            'valid_responses': valid_count,
            'success_rate': success_rate
        }
    
    def _multi_round_multilingual_interview(self, model_name: str, language: str) -> tuple:
        """
        多轮访谈取众数（指定语言）
        
        Args:
            model_name: 模型名称
            language: 语言代码
            
        Returns:
            tuple: (consensus_results, intermediate_data)
        """
        import time
        from collections import Counter
        
        lang_name = UN_LANGUAGE_NAMES_ZH.get(language, language)
        print(f"🔄 进行 {self.consensus_count} 轮完整问卷访谈（{lang_name}，取众数）...")
        
        questions = self.get_questions_for_language(language)
        if not questions:
            print(f"  ❌ 语言 {language} 没有可用的问题")
            return [], {}
        
        question_ids = list(questions.keys())
        all_rounds = []
        
        # 进行多轮完整访谈
        for round_num in range(self.consensus_count):
            print(f"\n┌{'─'*78}┐")
            print(f"│ 🔄 第 {round_num + 1}/{self.consensus_count} 轮 [{lang_name}] 问卷访谈" + " " * (78 - 25 - len(f"{round_num + 1}/{self.consensus_count}") - len(lang_name)) + "│")
            print(f"└{'─'*78}┘")
            
            round_result = self._single_round_multilingual_interview(model_name, language)
            round_result['round_id'] = round_num + 1
            all_rounds.append(round_result)
            
            print(f"✅ 第 {round_num + 1} 轮完成 - 成功率: {round_result['success_rate']:.0f}%")
            
            # 轮次间稍长延迟
            if round_num < self.consensus_count - 1:
                print(f"  ⏳ 休息片刻...")
                time.sleep(self._get_dynamic_delay(model_name) * 2)
        
        # 计算每个问题的众数
        print(f"\n{'='*80}")
        print(f"📊 计算众数 - 汇总 {self.consensus_count} 轮回答 [{lang_name}]")
        print(f"{'='*80}")
        
        consensus_results = []
        consistency_stats = {}
        
        for i, question_id in enumerate(question_ids):
            # 收集该问题在所有轮次中的回答
            question_responses = [round_data['responses'][i] for round_data in all_rounds]
            
            # 使用基类的众数计算方法
            consensus_response = self._calculate_consensus(question_responses, question_id)
            consensus_results.append(consensus_response)
            
            # 计算一致性
            valid_responses = [r.response for r in question_responses if r.is_valid]
            hashable_responses = [tuple(r) if isinstance(r, list) else r for r in valid_responses]
            response_counts = Counter(hashable_responses)
            most_common = response_counts.most_common(1)[0] if response_counts else (None, 0)
            
            response_dist = {str(k): v for k, v in response_counts.items()}
            
            consistency_stats[question_id] = {
                'consensus_value': consensus_response.response,
                'consensus_count': most_common[1],
                'total_valid': len(valid_responses),
                'consistency_rate': most_common[1] / len(valid_responses) if valid_responses else 0,
                'response_distribution': response_dist
            }
            
            print(f"  {question_id}: {consensus_response.response} "
                  f"(一致性: {consistency_stats[question_id]['consistency_rate']:.1%})")
        
        # 构建中间数据
        serializable_rounds = []
        for round_data in all_rounds:
            serializable_round = {
                'round_id': round_data.get('round_id'),
                'language': round_data.get('language'),
                'success_rate': round_data.get('success_rate'),
                'responses': [
                    {
                        'question_id': r.question_id,
                        'raw_response': r.raw_response,
                        'processed_response': r.response,
                        'is_valid': r.is_valid,
                        'error_message': r.error_message
                    } for r in round_data.get('responses', [])
                ]
            }
            serializable_rounds.append(serializable_round)
        
        intermediate_data = {
            'consensus_count': self.consensus_count,
            'language': language,
            'language_name': lang_name,
            'all_rounds': serializable_rounds,
            'consistency_stats': consistency_stats,
            'overall_consistency': sum(s['consistency_rate'] for s in consistency_stats.values()) / len(consistency_stats) if consistency_stats else 0
        }
        
        print(f"📊 总体一致性: {intermediate_data['overall_consistency']:.1%}")
        
        return consensus_results, intermediate_data
    
    def interview_single_language(self, model_name: str, language: str) -> tuple:
        """
        对单个模型进行单一语言的访谈
        
        根据 consensus_count 决定是单轮还是多轮访谈。
        
        Args:
            model_name: 模型名称
            language: 语言代码
            
        Returns:
            tuple: (responses, intermediate_data)
        """
        lang_name = UN_LANGUAGE_NAMES_ZH.get(language, language)
        print(f"\n=== 访谈模型: {model_name} [{lang_name}] ===")
        
        # 检查模型是否可用
        if model_name not in self.api_keys:
            print(f"跳过模型 {model_name}: API密钥未设置")
            return [], {}
        
        # 检查语言是否支持
        if language not in self.UN_OFFICIAL_LANGUAGES:
            print(f"跳过语言 {language}: 不是UN官方语言")
            return [], {}
        
        # 根据 consensus_count 决定访谈模式
        if self.consensus_count > 1:
            print(f"采用多轮访谈模式：{self.consensus_count} 轮完整问卷，每个问题取众数")
            return self._multi_round_multilingual_interview(model_name, language)
        else:
            print(f"采用单轮访谈模式")
            round_result = self._single_round_multilingual_interview(model_name, language)
            return round_result['responses'], {}
    
    def interview_model_multilingual(self, model_name: str) -> Dict[str, Any]:
        """
        对单个模型进行所有语言的访谈
        
        Args:
            model_name: 模型名称
            
        Returns:
            Dict: 按语言组织的访谈结果
        """
        print(f"\n{'='*80}")
        print(f"🌍 开始多语言访谈: {model_name}")
        print(f"   语言: {', '.join(self.UN_OFFICIAL_LANGUAGES)}")
        print(f"{'='*80}")
        
        results = {}
        
        for language in self.UN_OFFICIAL_LANGUAGES:
            lang_name = UN_LANGUAGE_NAMES_ZH.get(language, language)
            print(f"\n📝 开始 {lang_name} ({language}) 访谈...")
            
            responses, intermediate_data = self.interview_single_language(model_name, language)
            
            if responses:
                results[language] = {
                    'model_name': model_name,
                    'language': language,
                    'language_name': lang_name,
                    'responses': responses,
                    'intermediate_data': intermediate_data,
                    'valid_responses': sum(1 for r in responses if r.is_valid),
                    'total_questions': len(responses)
                }
                
                # 保存单个结果
                self.save_individual_result(model_name, language, results[language])
                
                print(f"✅ {lang_name} 访谈完成: {results[language]['valid_responses']}/{results[language]['total_questions']} 有效")
            else:
                print(f"❌ {lang_name} 访谈失败")
        
        return results
    
    def batch_multilingual_interview(self, 
                                     model_names: List[str] = None,
                                     languages: List[str] = None,
                                     skip_existing: bool = False) -> Dict[str, Any]:
        """
        批量多语言访谈
        
        Args:
            model_names: 模型列表，None则使用所有可用模型
            languages: 语言列表，None则使用所有UN官方语言
            skip_existing: 是否跳过已完成的模型-语言组合
            
        Returns:
            Dict: 包含results, total_tasks, successful_tasks, success_rate
        """
        # 确定模型列表
        if model_names is None:
            model_names = [name for name in self.model_configs.keys() 
                          if name in self.api_keys]
        
        # 确定语言列表
        if languages is None:
            languages = self.UN_OFFICIAL_LANGUAGES.copy()
        
        # 加载已有数据（如果启用跳过功能）
        existing_combinations = set()
        if skip_existing:
            print(f"\n📂 检查已有访谈数据...")
            existing_combinations = self._load_existing_multilingual_data(
                self.data_path / "llm_interviews" / "intrinsic" / "interview_raw"
            )
            if existing_combinations:
                print(f"✅ 发现 {len(existing_combinations)} 个已完成的模型-语言组合")
        
        # 生成任务列表
        tasks = []
        for model_name in model_names:
            for language in languages:
                combination = f"{model_name}_{language}"
                if skip_existing and combination in existing_combinations:
                    print(f"  ⏭️ 跳过: {model_name} [{language}]")
                    continue
                tasks.append({
                    'model_name': model_name,
                    'language': language
                })
        
        print(f"\n📊 任务统计:")
        print(f"   - 总模型数: {len(model_names)}")
        print(f"   - 总语言数: {len(languages)}")
        print(f"   - 待访谈组合: {len(tasks)}")
        
        if not tasks:
            print(f"\n✅ 所有组合都已完成，无需进行新的访谈")
            return {
                'results': {},
                'total_tasks': 0,
                'successful_tasks': 0,
                'success_rate': 1.0
            }
        
        # 执行访谈
        results = {}
        successful_tasks = 0
        
        for i, task in enumerate(tasks, 1):
            model_name = task['model_name']
            language = task['language']
            lang_name = UN_LANGUAGE_NAMES_ZH.get(language, language)
            
            print(f"\n{'='*80}")
            print(f"📝 任务 {i}/{len(tasks)}: {model_name} [{lang_name}]")
            print(f"{'='*80}")
            
            responses, intermediate_data = self.interview_single_language(model_name, language)
            
            if responses:
                result_key = f"{model_name}_{language}"
                result_data = {
                    'model_name': model_name,
                    'language': language,
                    'language_name': lang_name,
                    'responses': responses,
                    'intermediate_data': intermediate_data,
                    'valid_responses': sum(1 for r in responses if r.is_valid),
                    'total_questions': len(responses)
                }
                results[result_key] = result_data
                successful_tasks += 1
                
                # 保存单个结果
                self.save_individual_result(model_name, language, result_data)
                
                print(f"✅ 完成: {result_data['valid_responses']}/{result_data['total_questions']} 有效")
            else:
                print(f"❌ 失败")
        
        return {
            'results': results,
            'total_tasks': len(tasks),
            'successful_tasks': successful_tasks,
            'success_rate': successful_tasks / len(tasks) if tasks else 0
        }
    
    # ==================== 数据保存和加载方法 ====================
    
    def save_individual_result(self, model_name: str, language: str, 
                               result: Dict[str, Any]) -> str:
        """
        保存单个模型-语言组合的结果
        
        Args:
            model_name: 模型名称
            language: 语言代码
            result: 访谈结果
            
        Returns:
            str: 保存的文件路径
        """
        import pickle
        
        # 确保输出目录存在
        output_dir = self.data_path / "llm_interviews" / "intrinsic" / "interview_raw"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建安全的文件名
        safe_model_name = model_name.replace('/', '_').replace('\\', '_').replace(':', '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 构建保存数据
        save_data = {
            'entity_id': f"llm_{safe_model_name}_{language}",
            'model_name': model_name,
            'language': language,
            'language_name': result.get('language_name', UN_LANGUAGE_NAMES_ZH.get(language, language)),
            'timestamp': datetime.now().isoformat(),
            'consensus_count': self.consensus_count,
            'total_questions': result.get('total_questions', 0),
            'valid_responses': result.get('valid_responses', 0),
            'success_rate': result.get('valid_responses', 0) / result.get('total_questions', 1) * 100 if result.get('total_questions', 0) > 0 else 0,
            'responses': []
        }
        
        # 转换responses
        for resp in result.get('responses', []):
            if hasattr(resp, 'question_id'):
                # LLMResponse对象
                save_data['responses'].append({
                    'question_id': resp.question_id,
                    'raw_response': resp.raw_response,
                    'processed_response': resp.response,
                    'is_valid': resp.is_valid,
                    'error_message': resp.error_message
                })
            elif isinstance(resp, dict):
                # 已经是字典
                save_data['responses'].append(resp)
        
        # 添加中间数据
        if result.get('intermediate_data'):
            save_data['intermediate_data'] = result['intermediate_data']
        
        # 保存JSON
        json_file = output_dir / f"{safe_model_name}_{language}_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        # 保存PKL
        pkl_file = output_dir / f"{safe_model_name}_{language}_{timestamp}.pkl"
        with open(pkl_file, 'wb') as f:
            pickle.dump(save_data, f)
        
        print(f"💾 已保存: {safe_model_name}_{language}_{timestamp}.json")
        
        return str(json_file)
    
    def _load_existing_multilingual_data(self, data_dir: Path) -> set:
        """
        加载已有的多语言访谈数据，返回已完成的模型-语言组合
        
        Args:
            data_dir: 数据目录
            
        Returns:
            set: 已完成的组合集合，格式为 {model_name}_{language}
        """
        completed_combinations = set()
        
        if not data_dir.exists():
            return completed_combinations
        
        import pickle
        
        # 查找所有包含语言代码的文件
        for pkl_file in data_dir.glob("*.pkl"):
            try:
                # 跳过合并文件
                if pkl_file.name.startswith("llm_interview_raw_"):
                    continue
                
                with open(pkl_file, 'rb') as f:
                    data = pickle.load(f)
                
                model_name = data.get('model_name', '')
                language = data.get('language', '')
                
                if model_name and language:
                    combination = f"{model_name}_{language}"
                    completed_combinations.add(combination)
                    
            except Exception as e:
                print(f"  ⚠️ 加载失败 {pkl_file.name}: {e}")
        
        return completed_combinations
    
    def _merge_multilingual_results(self, existing_data: Dict[str, Any], 
                                      new_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        合并已有数据和新访谈结果，确保无重复
        
        合并规则：
        1. 已有数据优先保留（不会被新数据覆盖）
        2. 新数据中不存在于已有数据的条目会被添加
        3. 结果集中每个 model-language 组合只出现一次
        
        键格式为 {model_name}_{language}，例如 "gpt-4o_zh-cn"
        
        Args:
            existing_data: 已有数据字典，键为 model_language 组合
            new_results: 新的访谈结果字典，键为 model_language 组合
            
        Returns:
            Dict[str, Any]: 合并后的数据，无重复的 model-language 组合
            
        Example:
            >>> existing = {"gpt-4o_en": {...}, "gpt-4o_fr": {...}}
            >>> new = {"gpt-4o_fr": {...}, "gpt-4o_es": {...}}
            >>> merged = self._merge_multilingual_results(existing, new)
            >>> # merged = {"gpt-4o_en": {...}, "gpt-4o_fr": {...}, "gpt-4o_es": {...}}
            >>> # Note: gpt-4o_fr keeps the existing data, not overwritten
        """
        # Handle None or empty inputs
        if existing_data is None:
            existing_data = {}
        if new_results is None:
            new_results = {}
        
        # Start with a copy of existing data to preserve it
        merged = existing_data.copy()
        
        # Add only new entries that don't already exist
        # This ensures no duplicates and existing data is preserved
        for key, value in new_results.items():
            if key not in merged:
                merged[key] = value
        
        return merged


def main():
    """测试多语言访谈类初始化"""
    print("🔄 测试 LLMMultilingualInterview 初始化...")
    
    # 创建访谈对象
    interview = LLMMultilingualInterview(consensus_count=5)
    
    # 显示支持的语言
    print(f"\n支持的UN官方语言:")
    for lang in interview.get_un_official_languages():
        name_zh = UN_LANGUAGE_NAMES_ZH.get(lang, lang)
        name = UN_LANGUAGE_NAMES.get(lang, lang)
        questions = interview.get_questions_for_language(lang)
        print(f"  - {lang}: {name_zh} ({name}) - {len(questions)} 个问题")
    
    # 显示可用模型
    available_models = [name for name in interview.model_configs.keys() 
                       if name in interview.api_keys]
    print(f"\n可用模型: {len(available_models)} 个")
    for model in available_models[:5]:  # 只显示前5个
        print(f"  - {model}")
    if len(available_models) > 5:
        print(f"  ... 还有 {len(available_models) - 5} 个模型")
    
    print("\n✅ 初始化测试完成！")


if __name__ == "__main__":
    main()
