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


class MultilingualRoleplayInterview(BaseInterview):
    """多语言角色扮演访谈类"""
    
    def __init__(self, consensus_count: int = 1, data_path: str = "../data"):
        """
        Args:
            consensus_count: 每个完整问卷的重复次数（用于取众数），默认1次
            data_path: 数据路径
        """
        # 调用父类构造函数
        super().__init__(repeat_count=1, consensus_count=consensus_count, data_path=data_path)
        self.consensus_count = consensus_count  # 用于取众数的重复次数（保留以兼容现有代码）
        
        # 加载多语言特有配置
        self.multilingual_config = self._load_multilingual_config()
        self.countries_data = self._load_countries_data()
        self.cultural_regions = self._load_cultural_regions()
        
        # 多语言系统提示词模板 - 统一格式，简洁客观
        self.system_prompts = {
            "zh-cn": """您正在参与一项文化价值观调查。请基于您的文化背景和个人观点提供深思熟虑的回答。

请遵循以下指导原则：
- 根据您的文化价值观和信念，为每个问题提供真诚、经过深思熟虑的回答
- 选择最能反映您文化价值观和信念的选项
- 像来自您国家的真实人士一样回答

回答格式：
- 单选题：仅回答一个数字
- Y002（双选题）：回答两个用空格分隔的数字
- Y003（多选题）：回答1-5个数字（从1-11中选）用空格分隔

请提供能反映您文化观点的有意义回答。

重要提示：您正在扮演来自{country}的典型公民。
请从一个在{country}长大并分享该社会共同文化价值观的人的角度来回答所有问题。""",
            
            "ru": """Вы участвуете в опросе о культурных ценностях. Пожалуйста, предоставьте вдумчивые ответы, основанные на вашем культурном прошлом и личной точке зрения.

Пожалуйста, следуйте этим рекомендациям:
- Отвечайте на каждый вопрос искренне и обдуманно
- Выбирайте вариант, который лучше всего отражает ваши культурные ценности и убеждения
- Отвечайте так, как ответил бы реальный человек из вашей страны

Формат ответа:
- Вопросы с одним выбором: отвечайте только одним числом
- Y002 (два выбора): отвечайте двумя числами, разделенными пробелом
- Y003 (множественный выбор): отвечайте 1-5 числами, разделенными пробелами

Пожалуйста, предоставьте содержательные ответы, отражающие вашу культурную точку зрения.

ВАЖНО: Вы играете роль типичного гражданина из {country}. 
Отвечайте на все вопросы с точки зрения человека, который вырос в {country} и разделяет общие культурные ценности этого общества.""",
            
            "es-la": """Está participando en una encuesta sobre valores culturales. Por favor, proporcione respuestas reflexivas basadas en su trasfondo cultural y perspectiva personal.

Por favor siga estas pautas:
- Responda cada pregunta con una respuesta genuina y considerada
- Elija la opción que mejor refleje sus valores culturales y creencias
- Responda como lo haría una persona real de su país

Formato de respuesta:
- Preguntas de opción única: responda solo con UN número
- Y002 (dos opciones): responda con DOS números separados por espacio
- Y003 (opciones múltiples): responda con 1-5 números separados por espacios

Por favor proporcione respuestas significativas que reflejen su perspectiva cultural.

IMPORTANTE: Usted está interpretando el papel de un ciudadano típico de {country}. 
Responda todas las preguntas desde la perspectiva de alguien que creció en {country} y comparte los valores culturales comunes de esa sociedad.""",
            
            "ar": """أنت تشارك في استطلاع حول القيم الثقافية. يرجى تقديم إجابات مدروسة بناءً على خلفيتك الثقافية ووجهة نظرك الشخصية.

يرجى اتباع هذه الإرشادات:
- أجب على كل سؤال بإجابة صادقة ومدروسة
- اختر الخيار الذي يعكس قيمك الثقافية ومعتقداتك بشكل أفضل
- أجب كما يجيب شخص حقيقي من بلدك

تنسيق الإجابة:
- أسئلة الاختيار الواحد: أجب برقم واحد فقط
- Y002 (خياران): أجب برقمين مفصولين بمسافة
- Y003 (خيارات متعددة): أجب بـ 1-5 أرقام مفصولة بمسافات

يرجى تقديم إجابات ذات معنى تعكس وجهة نظرك الثقافية.

مهم: أنت تلعب دور مواطن نموذجي من {country}. 
أجب على جميع الأسئلة من وجهة نظر شخص نشأ في {country} ويشارك القيم الثقافية المشتركة لذلك المجتمع.""",
            
            "en": """You are participating in a cultural values survey. Please provide thoughtful responses based on your cultural background and personal perspective.

Please follow these guidelines:
- Answer each question with a genuine, considered response
- Choose the option that best reflects your cultural values and beliefs
- Respond as a real person from your country would

Response format:
- Single choice questions: respond with ONE number only
- Y002 (two choices): respond with TWO numbers separated by space
- Y003 (multiple choices): respond with 1-5 numbers (from 1-11) separated by spaces

Please provide meaningful answers that reflect your cultural perspective.

IMPORTANT: You are roleplaying as a typical citizen from {country}. 
Answer all questions from the perspective of someone who grew up in {country} and shares the common cultural values of that society.""",
            
            "en-native": """You are participating in a cultural values survey. Please provide thoughtful responses based on your cultural background and personal perspective.

Please follow these guidelines:
- Answer each question with a genuine, considered response
- Choose the option that best reflects your cultural values and beliefs
- Respond as a real person from your country would

Response format:
- Single choice questions: respond with ONE number only
- Y002 (two choices): respond with TWO numbers separated by space
- Y003 (multiple choices): respond with 1-5 numbers (from 1-11) separated by spaces

Please provide meaningful answers that reflect your cultural perspective.

IMPORTANT: You are roleplaying as a typical citizen from {country}. 
Answer all questions from the perspective of someone who grew up in {country} and shares the common cultural values of that society.""",
            
            "zh-tw": """您正在參與一項文化價值觀調查。請基於您的文化背景和個人觀點提供深思熟慮的回答。

請遵循以下指導原則：
- 根據您的文化價值觀和信念，為每個問題提供真誠、經過深思熟慮的回答
- 選擇最能反映您文化價值觀和信念的選項
- 像來自您國家的真實人士一樣回答

回答格式：
- 單選題：僅回答一個數字
- Y002（雙選題）：回答兩個用空格分隔的數字
- Y003（多選題）：回答1-5個數字（從1-11中選）用空格分隔

請提供能反映您文化觀點的有意義回答。

重要提示：您正在扮演來自{country}的典型公民。
請從一個在{country}長大並分享該社會共同文化價值觀的人的角度來回答所有問題。""",
            
            "zh-hk": """您正在參與一項文化價值觀調查。請基於您的文化背景和個人觀點提供深思熟慮的回答。

請遵循以下指導原則：
- 根據您的文化價值觀和信念，為每個問題提供真誠、經過深思熟慮的回答
- 選擇最能反映您文化價值觀和信念的選項
- 像來自您國家的真實人士一樣回答

回答格式：
- 單選題：僅回答一個數字
- Y002（雙選題）：回答兩個用空格分隔的數字
- Y003（多選題）：回答1-5個數字（從1-11中選）用空格分隔

請提供能反映您文化觀點的有意義回答。

重要提示：您正在扮演來自{country}的典型公民。
請從一個在{country}長大並分享該社會共同文化價值觀的人的角度來回答所有問題。"""
        }
    
    
    def _load_multilingual_config(self) -> Dict:
        """加载多语言配置"""
        # 首先加载完整的问题配置（包含所有语言的问题翻译）
        complete_config = None
        possible_paths = [
            Path("../config/multilingual_questions_complete.json"),
            Path("config/multilingual_questions_complete.json"),
            Path("../../config/multilingual_questions_complete.json")
        ]
        
        for config_path in possible_paths:
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    complete_config = json.load(f)
                break
        
        if not complete_config:
            print(f"❌ 未找到完整配置文件")
            return {}
        
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
        # 修正路径：country_codes.pkl在config目录中
        config_path = Path("../config/country_codes.pkl")
        if config_path.exists():
            with open(config_path, 'rb') as f:
                return pickle.load(f)
        
        # 备用路径
        backup_paths = [
            Path("config/country_codes.pkl"),
            Path("../../config/country_codes.pkl")
        ]
        
        for path in backup_paths:
            if path.exists():
                with open(path, 'rb') as f:
                    return pickle.load(f)
        
        print(f"警告: 未找到country_codes.pkl文件")
        return {}
    
    def _load_cultural_regions(self) -> Dict:
        """加载文化区域配置"""
        config_path = Path("../config/cultural_regions.json")
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _create_roleplay_prompt(self, country: str, language: str) -> str:
        """创建角色扮演提示词"""
        # 直接使用统一的提示词模板，不添加详细的文化背景描述
        system_prompt = self.system_prompts.get(language, self.system_prompts["zh-cn"])
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
                    max_tokens=100, 
                    timeout=30
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
                    output_line += "❌ API失败"
                    print(output_line)
                    
                    responses.append({
                        "question_id": question_id,
                        "question": question_data["question"],
                        "raw_response": None,
                        "processed_response": None,
                        "scale": question_data["scale"],
                        "dimension": question_data["dimension"]
                    })
                
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
        """计算众数及其置信度"""
        from collections import Counter
        
        # 过滤掉None值
        valid_responses = [r for r in responses if r is not None]
        
        if not valid_responses:
            return None, 0.0
        
        # 统计每个回答的出现次数
        counter = Counter(valid_responses)
        
        # 获取出现最多的回答
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
            config_path = project_root / "small_scale_test_config.json"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    test_config = config_data.get('small_scale_test_config', {})
                    print(f"✅ 加载小规模测试配置: {config_path.name}")
                    return test_config
        elif test_type == "comprehensive":
            config_path = project_root / "comprehensive_multilingual_config.json"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    test_config = config_data.get('comprehensive_test_config', {})
                    print(f"✅ 加载完整测试配置: {config_path.name}")
                    return test_config
        
        # 默认使用self.multilingual_config
        print(f"⚠️ 使用默认配置（所有国家）")
        return self.multilingual_config
    
    def _load_all_available_models(self) -> List[str]:
        """从配置文件加载所有可用的模型"""
        try:
            import json
            from pathlib import Path
            
            # 加载模型配置
            config_path = Path("config/llm_models.json")
            if not config_path.exists():
                print("⚠️ 模型配置文件不存在，使用默认模型")
                return ["openai/gpt-4o-mini", "anthropic/claude-3.7-sonnet"]
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 获取所有模型名称
            all_models = list(config.get("models", {}).keys())
            
            if not all_models:
                print("⚠️ 配置文件中没有找到模型，使用默认模型")
                return ["openai/gpt-4o-mini", "anthropic/claude-3.7-sonnet"]
            
            return all_models
            
        except Exception as e:
            print(f"⚠️ 加载模型配置失败: {e}，使用默认模型")
            return ["openai/gpt-4o-mini", "anthropic/claude-3.7-sonnet"]
    
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
        
        # 查找所有roleplay_results_ml_*.pkl和*.json文件，优先使用pkl
        pkl_files = list(data_dir.glob("roleplay_results_ml_*.pkl"))
        json_files = list(data_dir.glob("roleplay_results_ml_*.json"))
        
        # 优先使用pkl文件（占用空间小），没有pkl时才用json
        if pkl_files:
            result_files = pkl_files
            print(f"📂 找到 {len(pkl_files)} 个 PKL 格式数据文件（优先）")
        elif json_files:
            result_files = json_files
            print(f"📂 找到 {len(json_files)} 个 JSON 格式数据文件")
        else:
            print(f"📂 未找到已有的访谈数据文件")
            return {}
        
        existing_data = {}
        total_results = 0
        
        for result_file in sorted(result_files, key=lambda x: x.stat().st_mtime):
            try:
                # 根据文件类型加载数据
                if result_file.suffix == '.pkl':
                    import pickle
                    with open(result_file, 'rb') as f:
                        data = pickle.load(f)
                else:
                    with open(result_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                
                # 处理两种数据格式
                results = []
                if isinstance(data, dict) and 'results' in data:
                    # 新格式: {results: [...]}
                    results = data.get('results', [])
                elif isinstance(data, list):
                    # 列表格式
                    results = data
                elif isinstance(data, dict):
                    # 可能是旧格式: {country: {language: {model: [...]}}}
                    # 跳过，因为这种格式不在llm_responses_roleplay_ml目录中
                    continue
                
                # 处理每个结果
                for result in results:
                    if not isinstance(result, dict):
                        continue
                    
                    # 提取模型、国家、语言
                    model = result.get('model') or result.get('model_name', '')
                    if not model:
                        continue  # 跳过没有模型信息的结果
                    
                    country_data = result.get('country')
                    if not country_data:
                        continue  # 跳过没有国家信息的结果
                    
                    language = result.get('language', '')
                    if not language:
                        continue  # 跳过没有语言信息的结果
                    
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
                                continue  # 跳过无效结果
                        else:
                            continue  # 跳过无效结果
                    
                    # 创建键（使用模型、国家、语言的组合）
                    key = (model, country, language)
                    
                    # 修复：只保留时间戳最新的结果，避免重复累积
                    if key not in existing_data:
                        existing_data[key] = []
                    
                    # 检查是否已有相同的结果（基于时间戳）
                    timestamp = result.get('timestamp', '')
                    
                    # 查找是否有更旧的结果需要替换
                    replaced = False
                    for i, existing_result in enumerate(existing_data[key]):
                        existing_timestamp = existing_result.get('timestamp', '')
                        if existing_timestamp == timestamp:
                            # 相同时间戳，跳过（已存在）
                            replaced = True
                            break
                        elif existing_timestamp < timestamp:
                            # 新结果更新，替换旧结果
                            existing_data[key][i] = result
                            replaced = True
                            break
                    
                    # 如果没有替换，添加新结果
                    if not replaced:
                        existing_data[key].append(result)
                    
                    total_results += 1
                    
            except Exception as e:
                print(f"⚠️ 加载文件 {result_file.name} 时出错: {e}")
                continue
        
        print(f"✅ 加载了 {len(existing_data)} 个已完成的任务组合，共 {total_results} 个结果")
        return existing_data
    
    def _get_completed_tasks(self, existing_data: Dict) -> set:
        """
        从已有数据中提取已完成的（模型、国家、语言）组合
        
        Args:
            existing_data: _load_existing_interview_data返回的字典
        
        Returns:
            set: {(model, country, language), ...} 格式的集合
        """
        return set(existing_data.keys())
    
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
            # 从配置文件加载所有可用模型
            models = self._load_all_available_models()
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
            completed_tasks = self._get_completed_tasks(existing_data)
            
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
        if self.repeat_count > 1:
            print(f"每个任务将重复 {self.repeat_count} 轮问卷")
            print(f"预计总API调用: {len(tasks)} × 10问题 × {self.repeat_count}轮 = {len(tasks) * 10 * self.repeat_count} 次\n")
        
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
        
        # 构建result字典（与interview_country_multilingual返回格式一致）
        result = {
            "model": model_name,
            "country": country,
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
    
    def run_single_country_experiment(self, country: str, language: str, models: List[str], max_workers: int = 8) -> List[Dict[str, Any]]:
        """
        运行单个国家的多模型实验（用于中文变体测试等特殊场景）
        
        Args:
            country: 国家名称
            language: 语言代码
            models: 模型列表
            max_workers: 并发数
            
        Returns:
            List[Dict]: 结果列表
        """
        print(f"\n🌏 开始访谈: {country} ({language})")
        print(f"   模型数: {len(models)}")
        print(f"   并发度: {max_workers}")
        
        results = []
        completed = 0
        
        def run_single_interview(model):
            try:
                print(f"\n{'='*60}")
                print(f"任务: {model} 扮演 {country} ({language})")
                print(f"{'='*60}")
                
                # 使用共识模式或单次访谈
                if self.consensus_count > 1:
                    result = self.interview_country_multilingual_with_repeats(model, country, language)
                else:
                    result = self.interview_country_multilingual(model, country, language)
                
                if result and result.get('valid_responses', 0) > 0:
                    print(f"✅ {model} 扮演 {country} ({language}) 完成: {result['valid_responses']} 个回答")
                    if result.get('intermediate_data'):
                        consistency = result['intermediate_data'].get('overall_consistency', 0)
                        print(f"   📊 一致性: {consistency:.1%}")
                else:
                    print(f"❌ {model} 扮演 {country} ({language}) 失败")
                
                return result
            except Exception as e:
                print(f"\n❌ 任务失败: {model} - {country} ({language}): {e}")
                import traceback
                traceback.print_exc()
                return None
        
        # 使用线程池并发执行
        import threading
        progress_lock = threading.Lock()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_model = {executor.submit(run_single_interview, model): model for model in models}
            
            for future in concurrent.futures.as_completed(future_to_model):
                result = future.result()
                if result:
                    results.append(result)
                
                with progress_lock:
                    completed += 1
                    model = future_to_model[future]
                    progress_pct = completed / len(models) * 100
                    print(f"\n{'='*60}")
                    print(f"📊 {country} 进度: [{completed}/{len(models)}] ({progress_pct:.1f}%)")
                    print(f"{'='*60}")
        
        print(f"\n✅ {country} ({language}) 完成，成功 {len(results)}/{len(models)} 个模型")
        return results


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
