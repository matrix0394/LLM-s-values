"""
多语言大模型国家角色扮演访谈模块
让大模型使用本国语言模仿特定国家的文化背景回答IVS问题
"""

import os
import json
import time
import pickle
from datetime import datetime
from openai import OpenAI
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
from pathlib import Path
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import threading

# 导入基础模块
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.base.ivs_questionnaire import IVSQuestions, LLMResponse
from src.base.base_interview import BaseInterview
from src.base.ivs_question_processor import IVSQuestionProcessor
from src.utils.country_name_standardizer import CountryNameStandardizer


class MultilingualRoleplayInterview(BaseInterview):
    """多语言角色扮演访谈类"""
    
    def __init__(self, consensus_count: int = 1, max_retry: int = 3, data_path: str = "data", 
                 model_config_file: str = None, language_config_file: str = None):
        """
        Args:
            consensus_count: 每个完整问卷的重复次数（用于取众数），默认1次
            max_retry: 单个问题失败后的最大重试次数（默认3）
            data_path: 数据路径
            model_config_file: 自定义模型配置文件名（默认为llm_models.json）
            language_config_file: 自定义语言配置文件名（默认为multilingual_questions_complete.json）
        """
        # 调用父类构造函数（使用最新的参数）
        super().__init__(max_retry=max_retry, data_path=data_path, consensus_count=consensus_count,
                        model_config_file=model_config_file)
        
        # 保存语言配置文件名
        self.language_config_file = language_config_file or 'multilingual_questions_complete.json'
        
        # 初始化国家名称标准化器
        self.name_standardizer = CountryNameStandardizer()
        
        # 加载多语言特有配置
        self.multilingual_config = self._load_multilingual_config()
        self.countries_data = self._load_countries_data()
        self.cultural_regions = self._load_cultural_regions()
        
        # 多语言系统提示词模板 - 统一格式，简洁客观
        self.system_prompts = {
            "zh-cn": """您正在参与一项文化价值观调查。请基于您的文化背景和个人观点提供深思熟虑的回答。

关键回答规则：
- 只回答数字 - 不要任何文字、解释或确认
- 不要说"好的"、"我明白"或任何确认语
- 不要解释您的选择
- 立即只用数字回答

记住：只有数字，绝对不要其他任何文字。

重要提示：您正在扮演来自{country}的典型公民。
请从一个在{country}长大并分享该社会共同文化价值观的人的角度来回答所有问题。""",
            
            "ru": """Вы участвуете в опросе о культурных ценностях. Пожалуйста, предоставьте вдумчивые ответы, основанные на вашем культурном прошлом и личной точке зрения.

КРИТИЧЕСКИЕ ПРАВИЛА ОТВЕТА:
- ТОЛЬКО отвечайте числами - БЕЗ текста, БЕЗ объяснений, БЕЗ подтверждений
- НЕ говорите "Хорошо", "Понятно", или любое подтверждение
- НЕ объясняйте свой выбор
- НЕМЕДЛЕННО отвечайте ТОЛЬКО числом/числами

ЗАПОМНИТЕ: ТОЛЬКО ЧИСЛА. Никакого другого текста.

ВАЖНО: Вы играете роль типичного гражданина из {country}. 
Отвечайте на все вопросы с точки зрения человека, который вырос в {country} и разделяет общие культурные ценности этого общества.""",
            
            "es": """Está participando en una encuesta sobre valores culturales. Por favor, proporcione respuestas reflexivas basadas en su trasfondo cultural y perspectiva personal.

REGLAS CRÍTICAS DE RESPUESTA:
- SOLO responda con números - SIN texto, SIN explicaciones, SIN confirmaciones
- NO diga "Okay", "Entiendo", o cualquier confirmación
- NO explique sus elecciones
- Responda INMEDIATAMENTE solo con el/los número(s)

RECUERDE: SOLO NÚMEROS. Ningún otro texto.

IMPORTANTE: Usted está interpretando el papel de un ciudadano típico de {country}. 
Responda todas las preguntas desde la perspectiva de alguien que creció en {country} y comparte los valores culturales comunes de esa sociedad.""",
            
            "ar": """أنت تشارك في استطلاع حول القيم الثقافية. يرجى تقديم إجابات مدروسة بناءً على خلفيتك الثقافية ووجهة نظرك الشخصية.

قواعد الإجابة الحاسمة:
- أجب بالأرقام فقط - بدون نص، بدون تفسيرات، بدون تأكيدات
- لا تقل "حسناً"، "فهمت"، أو أي تأكيد
- لا تشرح اختياراتك
- أجب فوراً بالرقم/الأرقام فقط

تذكر: الأرقام فقط. لا نص آخر على الإطلاق.

مهم: أنت تلعب دور مواطن نموذجي من {country}. 
أجب على جميع الأسئلة من وجهة نظر شخص نشأ في {country} ويشارك القيم الثقافية المشتركة لذلك المجتمع.""",
            
            "en": """You are participating in a cultural values survey. Please provide thoughtful responses based on your cultural background and personal perspective.

CRITICAL RESPONSE RULES:
- ONLY respond with numbers - NO text, NO explanations, NO confirmations
- Do NOT say "Okay", "I understand", or any acknowledgment
- Do NOT explain your choices
- IMMEDIATELY answer with ONLY the number(s)

REMEMBER: NUMBERS ONLY. No other text whatsoever.

IMPORTANT: You are roleplaying as a typical citizen from {country}. 
Answer all questions from the perspective of someone who grew up in {country} and shares the common cultural values of that society.""",
            
            "en-native": """You are participating in a cultural values survey. Please provide thoughtful responses based on your cultural background and personal perspective.

CRITICAL RESPONSE RULES:
- ONLY respond with numbers - NO text, NO explanations, NO confirmations
- Do NOT say "Okay", "I understand", or any acknowledgment
- Do NOT explain your choices
- IMMEDIATELY answer with ONLY the number(s)

REMEMBER: NUMBERS ONLY. No other text whatsoever.

IMPORTANT: You are roleplaying as a typical citizen from {country}. 
Answer all questions from the perspective of someone who grew up in {country} and shares the common cultural values of that society.""",
            
            "zh-tw": """您正在參與一項文化價值觀調查。請基於您的文化背景和個人觀點提供深思熟慮的回答。

關鍵回答規則：
- 只回答數字 - 不要任何文字、解釋或確認
- 不要說「好的」、「我明白」或任何確認語
- 不要解釋您的選擇
- 立即只用數字回答

記住：只有數字，絕對不要其他任何文字。

重要提示：您正在扮演來自{country}的典型公民。
請從一個在{country}長大並分享該社會共同文化價值觀的人的角度來回答所有問題。""",
            
            "zh-hk": """您正在參與一項文化價值觀調查。請基於您的文化背景和個人觀點提供深思熟慮的回答。

關鍵回答規則：
- 只回答數字 - 不要任何文字、解釋或確認
- 不要說「好的」、「我明白」或任何確認語
- 不要解釋您的選擇
- 立即只用數字回答

記住：只有數字，絕對不要其他任何文字。

重要提示：您正在扮演來自{country}的典型公民。
請從一個在{country}長大並分享該社會共同文化價值觀的人的角度來回答所有問題。""",
            
            "ja": """あなたは文化的価値観に関する調査に参加しています。あなたの文化的背景と個人的な視点に基づいて、よく考えた回答を提供してください。

重要な回答ルール：
- 数字のみで回答してください - テキスト、説明、確認は不要です
- 「わかりました」「理解しました」などの確認は言わないでください
- 選択の理由を説明しないでください
- すぐに数字のみで回答してください

覚えておいてください：数字のみ。他のテキストは一切不要です。

重要：あなたは{country}の典型的な市民としての役割を演じています。
{country}で育ち、その社会の共通の文化的価値観を共有する人の視点からすべての質問に答えてください。""",
            
            "ko": """귀하는 문화적 가치관에 관한 설문조사에 참여하고 있습니다。귀하의 문화적 배경과 개인적 관점을 바탕으로 신중한 답변을 제공해 주십시오。

중요한 답변 규칙：
- 숫자만 답변하십시오 - 텍스트, 설명, 확인 불필요
- "알겠습니다", "이해했습니다" 등의 확인 말씀 하지 마십시오
- 선택 이유를 설명하지 마십시오
- 즉시 숫자만으로 답변하십시오

기억하십시오: 숫자만。다른 텍스트는 일체 불필요합니다。

중요: 귀하는 {country}의 전형적인 시민 역할을 하고 있습니다。
{country}에서 자라고 그 사회의 공통된 문화적 가치관을 공유하는 사람의 관점에서 모든 질문에 답변하십시오。""",
            
            "fr": """Vous participez à une enquête sur les valeurs culturelles. Veuillez fournir des réponses réfléchies basées sur votre contexte culturel et votre perspective personnelle.

RÈGLES CRITIQUES DE RÉPONSE :
- Répondez UNIQUEMENT avec des numéros - PAS de texte, PAS d'explications, PAS de confirmations
- NE dites PAS "D'accord", "Je comprends", ou toute confirmation
- N'expliquez PAS vos choix
- Répondez IMMÉDIATEMENT avec UNIQUEMENT le(s) numéro(s)

RAPPELEZ-VOUS : NUMÉROS UNIQUEMENT. Aucun autre texte.

IMPORTANT : Vous jouez le rôle d'un citoyen typique de {country}.
Répondez à toutes les questions du point de vue de quelqu'un qui a grandi en {country} et partage les valeurs culturelles communes de cette société.""",
            
            "de": """Sie nehmen an einer Umfrage zu kulturellen Werten teil. Bitte geben Sie durchdachte Antworten basierend auf Ihrem kulturellen Hintergrund und Ihrer persönlichen Perspektive.

KRITISCHE ANTWORTREGELN:
- Antworten Sie NUR mit Zahlen - KEIN Text, KEINE Erklärungen, KEINE Bestätigungen
- Sagen Sie NICHT "Okay", "Ich verstehe" oder irgendeine Bestätigung
- Erklären Sie NICHT Ihre Auswahl
- Antworten Sie SOFORT nur mit der/den Zahl(en)

DENKEN SIE DARAN: NUR ZAHLEN. Kein anderer Text.

WICHTIG: Sie spielen die Rolle eines typischen Bürgers aus {country}.
Beantworten Sie alle Fragen aus der Perspektive von jemandem, der in {country} aufgewachsen ist und die gemeinsamen kulturellen Werte dieser Gesellschaft teilt.""",
            
            "pt": """Você está participando de uma pesquisa sobre valores culturais. Por favor, forneça respostas ponderadas baseadas em seu contexto cultural e perspectiva pessoal.

REGRAS CRÍTICAS DE RESPOSTA:
- Responda APENAS com números - SEM texto, SEM explicações, SEM confirmações
- NÃO diga "Ok", "Entendo", ou qualquer confirmação
- NÃO explique suas escolhas
- Responda IMEDIATAMENTE apenas com o(s) número(s)

LEMBRE-SE: APENAS NÚMEROS. Nenhum outro texto.

IMPORTANTE: Você está interpretando o papel de um cidadão típico de {country}.
Responda todas as perguntas da perspectiva de alguém que cresceu em {country} e compartilha os valores culturais comuns dessa sociedade.""",
            
            "it": """Stai partecipando a un'indagine sui valori culturali. Si prega di fornire risposte ponderate basate sul proprio background culturale e sulla propria prospettiva personale.

REGOLE CRITICHE DI RISPOSTA:
- Rispondi SOLO con numeri - NESSUN testo, NESSUNA spiegazione, NESSUNA conferma
- NON dire "Ok", "Capisco", o qualsiasi conferma
- NON spiegare le tue scelte
- Rispondi IMMEDIATAMENTE solo con il/i numero/i

RICORDA: SOLO NUMERI. Nessun altro testo.

IMPORTANTE: Stai interpretando il ruolo di un cittadino tipico di {country}.
Rispondi a tutte le domande dal punto di vista di qualcuno che è cresciuto in {country} e condivide i valori culturali comuni di quella società."""
        }
    
    
    def _load_multilingual_config(self) -> Dict:
        """加载多语言配置"""
        # 使用自定义配置文件或默认配置文件
        config_path = Path(__file__).parent.parent.parent / 'config' / 'questions' / 'multilingual' / self.language_config_file
        
        if not config_path.exists():
            print(f"❌ 未找到完整配置文件: {config_path}")
            return {}
        
        with open(config_path, 'r', encoding='utf-8') as f:
            complete_config = json.load(f)
        
        # 检查是否有推荐配置（用于筛选国家）
        data_path = Path(self.data_path) if isinstance(self.data_path, str) else self.data_path
        recommended_config_path = data_path / "recommended_countries_for_multilingual.json"
        
        if recommended_config_path.exists():
            print(f"✅ 使用推荐配置筛选国家: {recommended_config_path}")
            with open(recommended_config_path, 'r', encoding='utf-8') as f:
                recommended_data = json.load(f)
            
            # 从推荐配置中提取要访谈的国家（按语言分组）
            selected_countries_by_lang = {}
            for lang_code, country_list in recommended_data.items():
                if lang_code != 'metadata' and isinstance(country_list, list):
                    selected_countries_by_lang[lang_code] = [c.get('name') for c in country_list]
            
            # 基于完整配置，只保留推荐的国家
            result = {"languages": {}}
            for lang_code in selected_countries_by_lang:
                if lang_code in complete_config.get("languages", {}):
                    # 保留问题数据，只筛选国家列表
                    result["languages"][lang_code] = {
                        "questions": complete_config["languages"][lang_code]["questions"],
                        "countries": selected_countries_by_lang[lang_code]
                    }
                    if "name" in complete_config["languages"][lang_code]:
                        result["languages"][lang_code]["name"] = complete_config["languages"][lang_code]["name"]
            
            print(f"📋 筛选后的语言: {list(result['languages'].keys())}")
            for lang, data in result["languages"].items():
                print(f"   {lang}: {len(data['countries'])} 个国家")
            
            return result
        else:
            # 没有推荐配置，使用完整配置
            print(f"⚠️ 使用完整配置（所有国家）")
            return complete_config
    
    def _load_countries_data(self) -> Dict:
        """加载国家数据"""
        # 统一从 config/country/ 目录加载
        config_country_path = Path(__file__).parent.parent.parent / "config" / "country" / "country_codes.pkl"
        
        if config_country_path.exists():
            with open(config_country_path, 'rb') as f:
                return pickle.load(f)
        
        print(f"⚠️ 未找到country_codes.pkl文件: {config_country_path}")
        return {}
    
    def _load_cultural_regions(self) -> Dict:
        """加载文化区域配置"""
        # 统一配置文件路径
        config_path = Path(__file__).parent.parent.parent / 'config' / 'country' / 'cultural_regions.json'
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        print(f"⚠️ 未找到cultural_regions.json文件: {config_path}")
        return {}
    
    def _create_roleplay_prompt(self, country: str, language: str) -> str:
        """创建角色扮演提示词"""
        # 直接使用统一的提示词模板，不添加详细的文化背景描述
        system_prompt = self.system_prompts.get(language, self.system_prompts["zh-cn"])
        
        # 调试输出：显示使用的语言和提示词前50个字符
        if language in self.system_prompts:
            print(f"  🌐 使用 {language} 提示词 | 前50字: {system_prompt[:50]}...")
        else:
            print(f"  ⚠️ 语言 {language} 未找到，使用默认 zh-cn 提示词")
        
        return system_prompt.format(country=country)
    
    
    
    
    def interview_country_multilingual_with_repeats(self, model_name: str, country: str, language: str) -> Dict[str, Any]:
        """对特定国家进行多语言访谈（整个问卷重复N次，最后取众数）"""
        # 简洁的开始提示（与Stage 2一致）
        print(f"🔄 进行 {self.consensus_count} 轮完整问卷访谈...")
        
        # 存储每一轮的完整访谈结果
        all_rounds = []
        
        # 重复进行N次完整问卷访谈
        for round_idx in range(self.consensus_count):
            print(f"\n┌{'─'*78}┐")
            print(f"│ 🔄 第 {round_idx + 1}/{self.consensus_count} 轮完整问卷访谈" + " " * (78 - 20 - len(f"{round_idx + 1}/{self.consensus_count}")) + "│")
            print(f"└{'─'*78}┘")
            
            # 进行一次完整的问卷访谈
            round_result = self.interview_country_multilingual(model_name, country, language)
            round_result['round_id'] = round_idx + 1
            all_rounds.append(round_result)
            
            print(f"✅ 第 {round_idx + 1} 轮完成 - 成功率: {round_result['success_rate']:.0f}%")
            
            # 轮次间短暂延迟
            if round_idx < self.consensus_count - 1:
                time.sleep(0.5)
        
        final_responses = self._aggregate_repeated_interviews(all_rounds)
        
        # 计算总体统计
        valid_count = sum(1 for r in final_responses if r['final_response'] is not None)
        avg_confidence = sum(r['confidence'] for r in final_responses) / len(final_responses) if final_responses else 0
        
        # 构建中间数据（统一格式）
        intermediate_data = {
            'consensus_count': self.consensus_count,  # 统一使用consensus_count
            'all_rounds': all_rounds,
            'overall_consistency': avg_confidence,  # 统一使用overall_consistency
            'consistency_stats': {}  # Stage 3暂时为空，可以后续补充
        }
        
        # 构建最终结果（统一格式）
        result = {
            "model": model_name,
            "country": country,
            "language": language,
            "timestamp": datetime.now().isoformat(),
            "total_questions": len(final_responses),
            "responses": final_responses,
            "intermediate_data": intermediate_data,  # 统一包在这里
            "valid_responses": valid_count,
            "success_rate": valid_count / len(final_responses) * 100 if final_responses else 0
        }
        
        return result
    
    def _aggregate_repeated_interviews(self, all_rounds: List[Dict]) -> List[Dict]:
        """聚合多轮访谈结果，计算每个问题的众数"""
        from collections import defaultdict, Counter
        
        # 按问题ID组织所有回答
        question_responses = defaultdict(lambda: {
            'question_id': None,
            'question': None,
            'scale': None,
            'dimension': None,
            'all_responses': [],
            'all_raw_responses': []
        })
        
        # 收集所有轮次的回答
        for round_data in all_rounds:
            for response in round_data['responses']:
                qid = response['question_id']
                question_responses[qid]['question_id'] = qid
                question_responses[qid]['question'] = response['question']
                question_responses[qid]['scale'] = response['scale']
                question_responses[qid]['dimension'] = response['dimension']
                question_responses[qid]['all_responses'].append(response['processed_response'])
                question_responses[qid]['all_raw_responses'].append(response['raw_response'])
        
        # 计算每个问题的众数
        final_responses = []
        for qid, data in question_responses.items():
            # 计算众数
            final_response, confidence = self._calculate_mode(data['all_responses'])
            
            # 统计回答分布
            valid_responses = [r for r in data['all_responses'] if r is not None]
            response_distribution = dict(Counter(valid_responses)) if valid_responses else {}
            
            # 打印每个问题的众数结果（带颜色标记）
            conf_emoji = "🟢" if confidence >= 0.8 else "🟡" if confidence >= 0.6 else "🔴"
            print(f"  {conf_emoji} {qid}: {data['all_responses']} → [{final_response}] (置信度: {confidence*100:.0f}%)")
            
            final_responses.append({
                'question_id': qid,
                'question': data['question'],
                'scale': data['scale'],
                'dimension': data['dimension'],
                'final_response': final_response,  # 最终众数结果
                'confidence': confidence,  # 置信度
                'all_responses': data['all_responses'],  # 所有轮次的处理后回答
                'all_raw_responses': data['all_raw_responses'],  # 所有轮次的原始回答
                'response_distribution': response_distribution,  # 回答分布
            })
        
        return final_responses
    
    def interview_country_multilingual(self, model_name: str, country: str, language: str) -> Dict[str, Any]:
        """对特定国家进行多语言访谈（单次完整问卷）"""
        # 获取该语言的问题
        questions = self.multilingual_config["languages"][language]["questions"]
        
        # 创建角色扮演提示词
        system_prompt = self._create_roleplay_prompt(country, language)
        
        responses = []
        valid_responses = 0
        
        question_items = list(questions.items())
        for idx, (question_id, question_data) in enumerate(question_items):
            try:
                # 调用API
                response_text = self.call_model_api(
                    model_name, 
                    question_id,
                    question_data["question"],
                    system_prompt=system_prompt,
                    max_tokens=100
                )
                
                # 组装完整的输出行（避免高并发时输出交织）
                output_line = f"  问题 {idx+1}/{len(question_items)}: {question_id} "
                
                if response_text:
                    processed_response = self._process_response(response_text, question_id)
                    
                    if processed_response:
                        valid_responses += 1
                        output_line += f"✅ {processed_response}"
                    else:
                        output_line += f"⚠️ 无效: {response_text.strip()}"
                    
                    # 一次性打印完整行（避免并发时被打断）
                    print(output_line)
                    
                    responses.append({
                        "question_id": question_id,
                        "question": question_data["question"],
                        "raw_response": response_text,
                        "processed_response": processed_response,
                        "scale": question_data["scale"],
                        "dimension": question_data["dimension"]
                    })
                else:
                    output_line += "❌ API失败 (详见上方错误信息)"
                    print(output_line)
                    
                    # 添加详细的失败记录
                    failure_info = {
                        "question_id": question_id,
                        "question": question_data["question"],
                        "raw_response": None,
                        "processed_response": None,
                        "scale": question_data["scale"],
                        "dimension": question_data["dimension"],
                        "failure_reason": "API call returned None - see console for details"
                    }
                    responses.append(failure_info)
                    
                    # 实时保存失败信息到临时文件
                    import json
                    from pathlib import Path
                    temp_dir = Path(self.data_path) / "temp_failures"
                    temp_dir.mkdir(exist_ok=True)
                    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                    temp_file = temp_dir / f"{model_name.replace('/', '_')}_{country}_{language}_{question_id}_{timestamp_str}.json"
                    with open(temp_file, 'w', encoding='utf-8') as f:
                        json.dump({
                            "model": model_name,
                            "country": country,
                            "language": language,
                            "question_id": question_id,
                            "question": question_data["question"],
                            "timestamp": datetime.now().isoformat(),
                            "note": "Check console output above for detailed error message from base_interview.py"
                        }, f, indent=2, ensure_ascii=False)
                    print(f"   💾 失败记录: {temp_file.name}")
                
                # 根据模型类型调整延迟
                if any(x in model_name.lower() for x in ['gpt', 'claude']):
                    time.sleep(0.2)
                else:
                    time.sleep(0.3)
                
            except Exception as e:
                print(f"  ❌ {question_id}: {e}")
                responses.append({
                    "question_id": question_id,
                    "question": question_data.get("question", ""),
                    "raw_response": None,
                    "processed_response": None,
                    "scale": question_data.get("scale", ""),
                    "dimension": question_data.get("dimension", ""),
                    "error": str(e)
                })
        
        result = {
            "model": model_name,
            "country": country,
            "language": language,
            "timestamp": datetime.now().isoformat(),
            "total_questions": len(questions),
            "valid_responses": valid_responses,
            "success_rate": valid_responses / len(questions) * 100 if questions else 0,
            "responses": responses
        }
        
        print(f"  ✅ 完成: {valid_responses}/{len(questions)}")
        return result
    
    def _calculate_mode(self, responses: List) -> Tuple[Any, float]:
        """计算众数及其置信度（支持列表类型，忽略顺序）"""
        from collections import Counter
        
        # 过滤掉None值
        valid_responses = [r for r in responses if r is not None]
        
        if not valid_responses:
            return None, 0.0
        
        # 检查是否是列表类型的回答（如Y002, Y003）
        # 如果是列表，需要标准化（排序）后再比较
        if valid_responses and isinstance(valid_responses[0], (list, tuple)):
            # 标准化：将列表转换为排序后的元组
            normalized_responses = [tuple(sorted(r)) if isinstance(r, (list, tuple)) else r 
                                   for r in valid_responses]
            
            # 统计标准化后的回答
            counter = Counter(normalized_responses)
            most_common_normalized, mode_count = counter.most_common(1)[0]
            
            # 找到对应的原始回答（保持原始顺序）
            mode_value = None
            for i, norm_resp in enumerate(normalized_responses):
                if norm_resp == most_common_normalized:
                    mode_value = valid_responses[i]
                    break
        else:
            # 单值回答：直接统计
            counter = Counter(valid_responses)
            most_common = counter.most_common(1)[0]
            mode_value = most_common[0]
            mode_count = most_common[1]
        
        # 计算置信度
        confidence = mode_count / len(valid_responses)
        
        return mode_value, confidence
    
    def _process_response(self, response_text: str, question_id: str) -> Optional[str]:
        """处理和验证回答 - 使用统一的处理器"""
        return IVSQuestionProcessor.parse_response_text(response_text, question_id)
    
    def _load_test_specific_config(self, test_type: str) -> Dict:
        """根据测试类型加载对应的配置"""
        project_root = Path(__file__).parent.parent.parent
        
        if test_type == "small_scale":
            config_path = project_root / "config" / "questions" / "multilingual" / "small_scale_test_config.json"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    test_config = config_data.get('small_scale_test_config', {})
                    print(f"✅ 加载小规模测试配置: {config_path.name}")
                    return test_config
        elif test_type == "comprehensive":
            config_path = project_root / "config" / "questions" / "multilingual" / "comprehensive_multilingual_config.json"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    test_config = config_data.get('comprehensive_test_config', {})
                    print(f"✅ 加载完整测试配置: {config_path.name}")
                    return test_config
        
        # 默认使用self.multilingual_config
        print(f"⚠️ 使用默认配置（所有国家）")
        return self.multilingual_config
    
    
    def _extract_country_name(self, country_data: Any) -> str:
        """
        从country字段中提取国家名称
        支持country是字符串或字典（包含name字段）的情况
        """
        if isinstance(country_data, dict):
            return country_data.get('name', str(country_data))
        elif isinstance(country_data, str):
            return country_data
        else:
            return str(country_data)
    
    def _load_existing_interview_data(self, data_dir: Path = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        加载所有已有的访谈数据
        只从独立文件加载（每个模型-国家-语言组合一个文件）
        
        Args:
            data_dir: 数据目录，默认为data/roleplay_multilingual/llm_responses_roleplay_ml
        
        Returns:
            Dict: { (model, country, language): [results...] } 格式的字典
        """
        if data_dir is None:
            project_root = Path(__file__).parent.parent.parent
            data_dir = project_root / "data" / "roleplay_multilingual" / "llm_responses_roleplay_ml"
        
        if not data_dir.exists():
            print(f"📂 数据目录不存在: {data_dir}")
            return {}
        
        import pickle
        
        # 查找所有独立文件（排除合并文件）
        # 独立文件格式: {model}_{country}_{language}_{timestamp}.pkl
        # 只从模型命名的子文件夹中读取（不搜索根目录）
        individual_pkl_files = []
        individual_json_files = []
        
        # 搜索模型子文件夹（一层深度）
        for subdir in data_dir.iterdir():
            if subdir.is_dir():
                individual_pkl_files.extend([f for f in subdir.glob("*.pkl") 
                                            if not f.name.startswith("roleplay_results_ml_")])
                individual_json_files.extend([f for f in subdir.glob("*.json") 
                                             if not f.name.startswith("roleplay_results_ml_")])
        
        # 优先使用pkl文件
        if individual_pkl_files:
            result_files = individual_pkl_files
            print(f"📂 发现 {len(individual_pkl_files)} 个独立 PKL 文件")
        elif individual_json_files:
            result_files = individual_json_files
            print(f"📂 发现 {len(individual_json_files)} 个独立 JSON 文件")
        else:
            print(f"📂 未找到已有的访谈数据文件")
            return {}
        
        existing_data = {}
        loaded_count = 0
        
        for result_file in result_files:
            try:
                # 根据文件类型加载数据
                if result_file.suffix == '.pkl':
                    with open(result_file, 'rb') as f:
                        result = pickle.load(f)
                else:
                    with open(result_file, 'r', encoding='utf-8') as f:
                        result = json.load(f)
                
                # 验证数据格式
                if not isinstance(result, dict):
                    continue
                
                # 提取模型、国家、语言
                model = result.get('model') or result.get('model_name', '')
                if not model:
                    print(f"   ⚠️ {result_file.name}: 缺少模型信息")
                    continue
                
                country_data = result.get('country')
                if not country_data:
                    print(f"   ⚠️ {result_file.name}: 缺少国家信息")
                    continue
                
                language = result.get('language', '')
                if not language:
                    print(f"   ⚠️ {result_file.name}: 缺少语言信息")
                    continue
                
                # 提取国家名称
                country = self._extract_country_name(country_data)
                
                # 检查是否有有效响应
                valid_responses = result.get('valid_responses', 0)
                if valid_responses == 0:
                    # 检查responses字段
                    responses = result.get('responses', [])
                    if isinstance(responses, list) and len(responses) > 0:
                        # 检查是否有有效的processed_response或final_response
                        valid_count = sum(1 for r in responses 
                                        if isinstance(r, dict) and 
                                        (r.get('processed_response') or r.get('final_response')))
                        if valid_count == 0:
                            print(f"   ⚠️ {model} | {country} | {language}: 无有效回答")
                            continue
                    else:
                        print(f"   ⚠️ {model} | {country} | {language}: 无有效回答")
                        continue
                
                # 创建键（使用模型、国家、语言的组合）
                key = (model, country, language)
                
                # 保存结果（每个独立文件只有一个结果）
                if key not in existing_data:
                    existing_data[key] = []
                
                existing_data[key].append(result)
                loaded_count += 1
                print(f"   ✅ {model} | {country} | {language}: {valid_responses}/10 有效回答")
                    
            except Exception as e:
                print(f"   ❌ {result_file.name}: 加载失败 - {e}")
                continue
        
        print(f"\n📊 总计加载: {len(existing_data)} 个任务组合，{loaded_count} 个结果")
        return existing_data
    
    
    def _merge_interview_results(self, existing_data: Dict, new_results: List[Dict]) -> Dict:
        """
        合并已有数据和新访谈结果（自动去重）
        
        Args:
            existing_data: 已有数据，格式为 {(model, country, language): [results...]}
            new_results: 新的访谈结果列表
        
        Returns:
            Dict: 合并后的数据，格式为 {results: [...]}
        """
        # 使用字典进行去重，key为(model, country, language)，value为最新的结果
        unique_results = {}
        
        # 添加已有数据 - 修复：对于每个key，只保留时间戳最新的一个result
        for (model, country, language), results in existing_data.items():
            key = (model, country, language)
            
            # 如果results是列表，找出时间戳最新的
            if isinstance(results, list):
                latest_result = None
                latest_timestamp = ''
                
                for result in results:
                    current_timestamp = result.get('timestamp', '')
                    if current_timestamp > latest_timestamp:
                        latest_timestamp = current_timestamp
                        latest_result = result
                
                if latest_result:
                    unique_results[key] = latest_result
            else:
                # 如果不是列表，直接使用（向后兼容）
                unique_results[key] = results
        
        # 添加新数据（新数据通常是最新的，会覆盖旧数据）
        for result in new_results:
            if result and result.get('valid_responses', 0) > 0:
                # 提取key
                model = result.get('model_name', result.get('model'))
                country_raw = result.get('country')
                if isinstance(country_raw, dict):
                    country = country_raw.get('name')
                else:
                    country = country_raw
                language = result.get('language')
                
                key = (model, country, language)
                
                # 比较时间戳，只有新数据更新时才覆盖
                if key in unique_results:
                    existing_timestamp = unique_results[key].get('timestamp', '')
                    current_timestamp = result.get('timestamp', '')
                    if current_timestamp > existing_timestamp:
                        unique_results[key] = result
                        print(f"   🔄 更新: {model.split('/')[-1]} | {country} | {language}")
                else:
                    unique_results[key] = result
                    print(f"   ✨ 新增: {model.split('/')[-1]} | {country} | {language}")
        
        all_results = list(unique_results.values())
        
        print(f"\n📊 合并结果统计:")
        print(f"   - 唯一组合数: {len(unique_results)}")
        print(f"   - 总记录数: {len(all_results)}")
        
        return {
            "experiment_type": "multilingual_roleplay",
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "total_tasks": len(all_results),
            "successful_tasks": len([r for r in all_results if r.get('valid_responses', 0) > 0]),
            "results": all_results
        }
    
    def run_multilingual_experiment(self, models: List[str] = None, max_workers: int = 4, repeat_count: int = 1, test_type: str = "standard", skip_existing: bool = True) -> Dict[str, Any]:
        """
        运行多语言实验（支持增量访谈）
        
        Args:
            models: 模型列表，None表示使用所有可用模型
            max_workers: 并发数
            repeat_count: 重复次数（已弃用，使用consensus_count）
            test_type: 测试类型
            skip_existing: 是否跳过已完成的访谈（默认True）
        
        Returns:
            Dict: 包含所有结果的数据字典（包括已有数据和新数据）
        """
        if models is None:
            # 从父类加载的配置中获取所有可用模型
            models = list(self.model_configs.keys())
            if not models:
                print("⚠️ 未找到可用模型，使用默认模型")
                models = ["openai/gpt-4o-mini", "anthropic/claude-3.7-sonnet"]
            print(f"🤖 使用所有可用模型: {len(models)} 个")
            for model in models:
                print(f"   - {model}")
        else:
            print(f"🤖 使用指定模型: {len(models)} 个")
        
        # 根据test_type动态加载配置
        config_to_use = self._load_test_specific_config(test_type)
        
        # 加载已有数据（如果启用跳过功能）
        existing_data = {}
        completed_tasks = set()
        if skip_existing:
            print(f"\n📂 检查已有访谈数据...")
            project_root = Path(__file__).parent.parent.parent
            data_dir = project_root / "data" / "roleplay_multilingual" / "llm_responses_roleplay_ml"
            existing_data = self._load_existing_interview_data(data_dir)
            completed_tasks = set(existing_data.keys())
            
            if completed_tasks:
                print(f"✅ 发现 {len(completed_tasks)} 个已完成的任务组合，将跳过这些任务")
                # 显示部分已完成的任务（最多显示10个）
                sample_tasks = list(completed_tasks)[:10]
                for model, country, language in sample_tasks:
                    print(f"   ⏭️  {model} | {country} | {language}")
                if len(completed_tasks) > 10:
                    print(f"   ... 还有 {len(completed_tasks) - 10} 个已完成的任务")
            else:
                print(f"📝 未发现已有数据，将进行全新访谈")
        
        # 准备所有可能的实验任务
        all_tasks = []
        for language, config in config_to_use["languages"].items():
            # 处理countries字段，通常是字符串列表，但也可能是字典列表
            countries = config.get("countries", [])
            for country_info in countries:
                # 提取国家名称
                if isinstance(country_info, dict):
                    # 如果是字典，提取name字段
                    country = country_info.get("name", str(country_info))
                elif isinstance(country_info, str):
                    # 如果是字符串，直接使用
                    country = country_info
                else:
                    # 其他情况，转换为字符串
                    country = str(country_info)
                
                for model in models:
                    all_tasks.append((model, country, language))
        
        # 过滤掉已完成的任务
        if skip_existing and completed_tasks:
            tasks = []
            skipped_count = 0
            for task in all_tasks:
                model, country, language = task
                if (model, country, language) in completed_tasks:
                    skipped_count += 1
                else:
                    tasks.append(task)
            
            print(f"\n📊 任务统计:")
            print(f"   - 总任务数: {len(all_tasks)}")
            print(f"   - 已完成: {skipped_count}")
            print(f"   - 待访谈: {len(tasks)}")
        else:
            tasks = all_tasks
            print(f"\n📊 总任务数: {len(tasks)}")
        
        # 如果没有待访谈的任务，直接返回已有数据
        if not tasks:
            print(f"\n✅ 所有任务都已完成，无需进行新的访谈")
            return self._merge_interview_results(existing_data, [])
        
        # 注释掉自动降低并发度的逻辑，使用用户指定的并发度
        # if self.repeat_count > 1 and max_workers > 2:
        #     max_workers = 2
        #     print(f"\n💡 检测到重复取众数模式 (repeat_count={self.repeat_count})")
        #     print(f"   自动调整并发度为 {max_workers} 以便清晰显示进度")
        
        print(f"\n准备运行 {len(tasks)} 个多语言访谈任务")
        print(f"并发度: {max_workers} (高并发模式)")
        if max_workers >= 10:
            print(f"⚡ 注意：高并发模式下输出会交织，但速度大幅提升")
        if self.consensus_count > 1:
            print(f"每个任务将重复 {self.consensus_count} 轮问卷")
            print(f"预计总API调用: {len(tasks)} × 10问题 × {self.consensus_count}轮 = {len(tasks) * 10 * self.consensus_count} 次\n")
        
        results = []
        completed = 0
        
        # 使用锁保护共享变量
        import threading
        progress_lock = threading.Lock()
        
        def run_single_interview(task):
            model, country, language = task
            try:
                # 打印任务标题（与Stage 2一致）
                print(f"\n{'='*60}")
                print(f"任务: {model} 扮演 {country} ({language})")
                print(f"{'='*60}")
                
                # 如果consensus_count > 1，使用重复访谈方法
                if self.consensus_count > 1:
                    result = self.interview_country_multilingual_with_repeats(model, country, language)
                else:
                    result = self.interview_country_multilingual(model, country, language)
                
                # 打印完成信息（与Stage 2一致）
                if result and result.get('valid_responses', 0) > 0:
                    print(f"✅ {model} 扮演 {country} ({language}) 完成: {result['valid_responses']} 个回答")
                    if result.get('intermediate_data'):
                        consistency = result['intermediate_data'].get('overall_consistency', 0)
                        print(f"   📊 一致性: {consistency:.1%}")
                    
                    # 🔧 立即保存单个结果（防止数据丢失）
                    try:
                        self._save_individual_result(model, country, language, result)
                    except Exception as save_error:
                        print(f"⚠️ 保存失败: {save_error}")
                else:
                    print(f"❌ {model} 扮演 {country} ({language}) 失败")
                
                return result
            except Exception as e:
                print(f"\n❌ 任务失败: {model} - {country} ({language}): {e}")
                return None
        
        # 使用线程池并发执行
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_task = {executor.submit(run_single_interview, task): task for task in tasks}
            
            for future in concurrent.futures.as_completed(future_to_task):
                result = future.result()
                if result:
                    results.append(result)
                
                with progress_lock:
                    completed += 1
                    # 显示整体进度（与Stage 2保持一致）
                    task = future_to_task[future]
                    model, country, language = task
                    progress_pct = completed / len(tasks) * 100
                    print(f"\n{'='*60}")
                    print(f"📊 整体进度: [{completed}/{len(tasks)}] ({progress_pct:.1f}%)")
                    print(f"{'='*60}")
        
        # 合并新旧数据
        print(f"\n📦 合并已有数据和新访谈结果...")
        merged_data = self._merge_interview_results(existing_data, results)
        
        # 保存结果 - 使用与Stage2一致的格式
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存到文件 - 使用与Stage2一致的目录和命名
        project_root = Path(__file__).parent.parent.parent
        output_dir = project_root / "data" / "roleplay_multilingual" / "llm_responses_roleplay_ml"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # JSON格式 - 与Stage2保持一致的命名
        json_file = output_dir / f"roleplay_results_ml_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=2)
        
        # PKL格式
        pkl_file = output_dir / f"roleplay_results_ml_{timestamp}.pkl"
        with open(pkl_file, 'wb') as f:
            pickle.dump(merged_data, f)
        
        print(f"\n{'='*60}")
        print(f"✅ 所有结果已保存:")
        print(f"   - 新完成任务: {len([r for r in results if r])}")
        print(f"   - 已有任务: {len(existing_data)}")
        print(f"   - 总任务数: {merged_data['total_tasks']}")
        print(f"   - 成功任务数: {merged_data['successful_tasks']}")
        print(f"  📁 目录: {output_dir}")
        print(f"  📄 JSON: roleplay_results_ml_{timestamp}.json")
        print(f"  📄 PKL: roleplay_results_ml_{timestamp}.pkl")
        print(f"{'='*60}")
        
        return merged_data
    
    def interview_entity(self, model_name: str, entity_id: str) -> Tuple[List[LLMResponse], Dict]:
        """
        访谈单个实体 - 多语言实现
        
        Args:
            model_name: 模型名称
            entity_id: 实体ID，格式为"country_language"（如"China_zh-cn"）
            
        Returns:
            Tuple[List[LLMResponse], Dict]: (回答列表, 中间数据)
        """
        # 解析entity_id
        if '_' in entity_id:
            country, language = entity_id.rsplit('_', 1)  # 从右侧分割，防止国家名包含下划线
        else:
            # 默认使用中文
            country, language = entity_id, 'zh-cn'
        
        # 如果启用共识模式，使用重复访谈
        if self.consensus_count > 1:
            result = self.interview_country_multilingual_with_repeats(model_name, country, language)
        else:
            result = self.interview_country_multilingual(model_name, country, language)
        
        # 转换为LLMResponse格式
        responses = []
        for response_data in result.get('responses', []):
            llm_response = LLMResponse(
                model_name=model_name,
                question_id=response_data['question_id'],
                response=response_data.get('processed_response'),
                raw_response=response_data.get('raw_response', ''),
                is_valid=response_data.get('processed_response') is not None
            )
            responses.append(llm_response)
        
        # 提取中间数据（如果有）
        intermediate_data = result.get('intermediate_data', {})
        
        return responses, intermediate_data
    
    def _save_individual_result(self, model_name: str, country: str, language: str, result: Dict) -> None:
        """保存单个访谈结果到独立文件（防止长时间任务崩溃丢失数据）"""
        try:
            # 创建保存目录
            project_root = Path(__file__).parent.parent.parent
            save_dir = project_root / "data" / "roleplay_multilingual" / "llm_responses_roleplay_ml"
            save_dir.mkdir(parents=True, exist_ok=True)
            
            # 构建文件名 - 使用模型_国家_语言_时间戳格式
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:19]  # 精确到毫秒
            model_short = model_name.split('/')[-1]  # 简化模型名
            filename = f"{model_short}_{country}_{language}_{timestamp}"
            
            # 保存JSON
            json_path = save_dir / f"{filename}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            # 保存PKL
            pkl_path = save_dir / f"{filename}.pkl"
            with open(pkl_path, 'wb') as f:
                pickle.dump(result, f)
            
            print(f"💾 已保存: {filename}.json")
            
        except Exception as e:
            print(f"⚠️ 保存单个结果失败: {e}")
    
    def _on_task_completed(self, model_name: str, entity_id: str, 
                          responses: List, intermediate_data: Dict = None):
        """
        任务完成钩子方法：每个任务完成后立即保存
        
        对于多语言访谈，entity_id格式为 "country_language"
        """
        # 解析entity_id
        if '_' in entity_id:
            country, language = entity_id.rsplit('_', 1)
        else:
            country, language = entity_id, 'unknown'
        
        # 如果responses为空，跳过保存
        if not responses:
            print(f"⚠️ 跳过保存（无有效响应）: {model_name} - {country} ({language})")
            return
        
        # 标准化国家名称（使用config/country_name_mapping.json）
        country_standardized = self.name_standardizer.standardize(country)
        if not country_standardized:
            country_standardized = country  # 如果标准化失败，使用原名称
        
        # 构建result字典（与interview_country_multilingual返回格式一致）
        result = {
            "model": model_name,
            "country": country_standardized,  # 使用标准化后的名称
            "country_original": country,  # 保留原始名称
            "language": language,
            "timestamp": datetime.now().isoformat(),
            "total_questions": len(responses) if responses else 0,
            "valid_responses": sum(1 for r in responses if r and hasattr(r, 'is_valid') and r.is_valid),
            "responses": []
        }
        
        # 转换responses
        for r in responses:
            if r and hasattr(r, 'question_id'):
                result["responses"].append({
                    "question_id": r.question_id,
                    "raw_response": r.raw_response,
                    "processed_response": r.response,
                    "is_valid": r.is_valid
                })
        
        # 添加中间数据
        if intermediate_data:
            result["intermediate_data"] = intermediate_data
            
            # 如果intermediate_data中有country字段，移除它（避免覆盖标准化的值）
            if "country" in result["intermediate_data"]:
                del result["intermediate_data"]["country"]
        
        # 确保标准化的字段不被覆盖
        result["country"] = country_standardized
        result["country_original"] = country
        
        # 即时保存
        self._save_individual_result(model_name, country, language, result)
    
    def batch_interview(self, model_names: List[str], entities: List[str] = None, max_workers: int = 4) -> Dict[str, Any]:
        """
        批量多语言角色扮演访谈（调用base的通用批量方法）
        
        Args:
            model_names: 模型列表
            entities: 实体列表（格式为"country_language"，如"China_zh-cn"）
                     如果为None，则从配置文件中自动生成所有语言-国家组合
            max_workers: 并发线程数，1表示串行，>1表示并行
            
        Returns:
            Dict: 包含results, total_tasks, successful_tasks, success_rate
        """
        # 如果未指定entities，则从配置生成所有语言-国家组合
        if entities is None:
            entities = []
            for language, config in self.multilingual_config["languages"].items():
                for country in config["countries"]:
                    entities.append(f"{country}_{language}")
        
        print(f"开始批量多语言角色扮演访谈:")
        print(f"  模型数量: {len(model_names)}")
        print(f"  语言-国家组合数量: {len(entities)}")
        print(f"  总任务数: {len(model_names) * len(entities)}")
        print(f"  并发模式: {'串行' if max_workers == 1 else f'并行 (max_workers={max_workers})'}")
        if self.consensus_count > 1:
            print(f"  共识模式: 每个任务重复{self.consensus_count}次取众数")
        
        # 构造tasks列表，调用base的通用批量方法
        tasks = [
            {'model_name': model, 'entity_id': entity}
            for model in model_names
            for entity in entities
        ]
        
        # 调用base实现的批量方法
        if max_workers == 1:
            return super()._batch_interview_sequential(tasks)
        else:
            return super()._batch_interview_concurrent(tasks, max_workers)
    


def main():
    """主函数"""
    print("=== 多语言角色扮演访谈系统 ===")
    
    # 创建访谈实例
    interviewer = MultilingualRoleplayInterview()
    
    # 运行实验
    models = ["openai/gpt-4o-mini"]  # 可以添加更多模型
    results = interviewer.run_multilingual_experiment(models=models, max_workers=2)
    
    print(f"\\n实验完成！")
    print(f"总任务数: {results['total_tasks']}")
    print(f"成功任务数: {results['successful_tasks']}")
    print(f"成功率: {results['successful_tasks']/results['total_tasks']*100:.1f}%")


if __name__ == "__main__":
    main()
