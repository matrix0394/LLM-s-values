"""
统一的访谈基类
消除不同interview类之间的代码重复
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
from abc import ABC, abstractmethod

# 🔧 只从.env文件加载环境变量，完全忽略系统环境变量
_ENV_VARS = {}  # 存储.env文件中的变量
try:
    from dotenv import dotenv_values
    # 从项目根目录加载.env文件
    project_root = Path(__file__).parent.parent.parent
    env_path = project_root / '.env'
    if env_path.exists():
        # 使用dotenv_values直接读取.env文件，不污染os.environ
        _ENV_VARS = dotenv_values(env_path)
        print(f"✅ 已加载.env文件: {env_path}")
        print(f"   📝 加载的密钥: {', '.join([k for k in _ENV_VARS.keys() if 'KEY' in k])}")
    else:
        print(f"⚠️ 未找到.env文件: {env_path}")
except ImportError:
    print("⚠️ 未安装python-dotenv")
    print("   提示: pip install python-dotenv")

# 导入基础模块 - 避免循环导入，直接导入
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.base.ivs_questionnaire import IVSQuestions, LLMResponse, ResponseValidator


class BaseInterview(ABC):
    """访谈基类 - 统一技术功能，业务逻辑由子类实现"""
    
    def __init__(self, max_retry: int = 3, data_path: str = "data", 
                 consensus_count: int = 1, model_config_file: str = None):
        """
        Args:
            max_retry: 单个问题失败后的最大重试次数（默认3次）
            data_path: 数据路径
            consensus_count: 多轮访谈的轮数（1=单次访谈，5=5轮访谈取众数）
            model_config_file: 自定义模型配置文件名（默认为llm_models.json）
        """
        self.questions = IVSQuestions()
        self.validator = ResponseValidator()
        self.model_config_file = model_config_file or 'llm_models.json'
        self.model_configs = self._load_model_configs()
        self.api_keys = self._load_api_keys()
        self.max_retry = max_retry  # 单个问题的重试次数
        self.consensus_count = consensus_count  # 完整问卷的访谈轮数
        self.data_path = Path(data_path)
    
    def _load_model_configs(self) -> Dict[str, Dict[str, str]]:
        """从配置文件加载模型配置"""
        # 统一配置文件路径，支持自定义配置文件
        config_path = Path(__file__).parent.parent.parent / 'config' / 'models' / self.model_config_file
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('models', {})
        except Exception as e:
            print(f"加载模型配置失败: {e}")
            return {}
    
    def _load_api_keys(self) -> Dict[str, str]:
        """从.env文件加载API密钥（完全不使用系统环境变量）"""
        api_keys = {}
        for model_name, config in self.model_configs.items():
            api_key_name = config.get('api_key', 'OPENROUTER_API_KEY')
            # 🔧 只从_ENV_VARS读取，完全不使用os.getenv()
            api_key = _ENV_VARS.get(api_key_name)
            if api_key:
                api_keys[model_name] = api_key
                print(f"   ✅ {model_name}: 使用.env中的 {api_key_name}")
            else:
                print(f"   ⚠️ {model_name}: .env文件中未找到 {api_key_name}")
        return api_keys
    
    def get_client(self, model_name: str) -> OpenAI:
        """创建OpenAI客户端 - 统一客户端管理"""
        if model_name not in self.model_configs:
            raise ValueError(f"未知模型: {model_name}")
        
        config = self.model_configs[model_name]
        api_key = self.api_keys.get(model_name)
        
        if not api_key:
            raise ValueError(f"模型 {model_name} 的API密钥未设置")
        
        # 小型模型（llama-3.2-3b、qwen3-1.7b等）可能响应较慢，需要更长timeout
        # 默认timeout=60秒，小型模型增加到120秒
        timeout = 120.0 if any(x in model_name.lower() for x in ['llama-3.2', 'qwen3-1.7b', 'qwen-1.5', 'phi']) else 60.0
        
        return OpenAI(
            api_key=api_key,
            base_url=config.get('base_url', 'https://api.openai.com/v1'),
            timeout=timeout  # 设置请求超时时间
        )
    
    def _get_format_hint(self, question_id: str, attempt: int = 0, language: str = "en") -> str:
        """生成格式提示 - 支持多语言"""
        # 多语言格式提示模板
        format_hints = {
            "zh-cn": {
                "Y002": "\n\n格式：回答两个不同的数字，用空格分隔（例如：'1 3'）。两个数字必须不同。",
                "Y003": "\n\n格式：回答1-5个数字（从1-11中选），用空格分隔（例如：'2 4 6 8 10'）。",
                "single": "\n\n格式：只回答一个数字（例如：'3'）。",
                "retry": "\n\n第{attempt}次尝试：请只提供数字，不要文字。"
            },
            "en": {
                "Y002": "\n\nFormat: Respond with exactly 2 DIFFERENT numbers separated by space (e.g., '1 3'). The two numbers must be different.",
                "Y003": "\n\nFormat: Respond with 1-5 numbers (from 1-11) separated by spaces (e.g., '2 4 6 8 10').",
                "single": "\n\nFormat: Respond with ONE number only (e.g., '3').",
                "retry": "\n\nAttempt {attempt}: Please provide ONLY numbers, no text."
            },
            "ru": {
                "Y002": "\n\nФормат: Ответьте ДВУМЯ РАЗНЫМИ числами, разделенными пробелом (например: '1 3'). Два числа должны быть разными.",
                "Y003": "\n\nФормат: Ответьте 1-5 числами (от 1 до 11), разделенными пробелами (например: '2 4 6 8 10').",
                "single": "\n\nФормат: Ответьте ОДНИМ числом (например: '3').",
                "retry": "\n\nПопытка {attempt}: Пожалуйста, предоставьте ТОЛЬКО числа, без текста."
            },
            "es": {
                "Y002": "\n\nFormato: Responda con exactamente 2 números DIFERENTES separados por espacio (ej: '1 3'). Los dos números deben ser diferentes.",
                "Y003": "\n\nFormato: Responda con 1-5 números (del 1 al 11) separados por espacios (ej: '2 4 6 8 10').",
                "single": "\n\nFormato: Responda con UN solo número (ej: '3').",
                "retry": "\n\nIntento {attempt}: Por favor, proporcione SOLO números, sin texto."
            },
            "ar": {
                "Y002": "\n\nالتنسيق: أجب برقمين مختلفين مفصولين بمسافة (مثال: '1 3'). يجب أن يكون الرقمان مختلفين.",
                "Y003": "\n\nالتنسيق: أجب بـ 1-5 أرقام (من 1 إلى 11) مفصولة بمسافات (مثال: '2 4 6 8 10').",
                "single": "\n\nالتنسيق: أجب برقم واحد فقط (مثال: '3').",
                "retry": "\n\nالمحاولة {attempt}: يرجى تقديم الأرقام فقط، بدون نص."
            },
            "fr": {
                "Y002": "\n\nFormat: Répondez avec exactement 2 numéros DIFFÉRENTS séparés par un espace (ex: '1 3'). Les deux numéros doivent être différents.",
                "Y003": "\n\nFormat: Répondez avec 1-5 numéros (de 1 à 11) séparés par des espaces (ex: '2 4 6 8 10').",
                "single": "\n\nFormat: Répondez avec UN seul numéro (ex: '3').",
                "retry": "\n\nTentative {attempt}: Veuillez fournir UNIQUEMENT des numéros, sans texte."
            },
            "de": {
                "Y002": "\n\nFormat: Antworten Sie mit genau 2 VERSCHIEDENEN Zahlen, getrennt durch Leerzeichen (z.B.: '1 3'). Die zwei Zahlen müssen unterschiedlich sein.",
                "Y003": "\n\nFormat: Antworten Sie mit 1-5 Zahlen (von 1 bis 11), getrennt durch Leerzeichen (z.B.: '2 4 6 8 10').",
                "single": "\n\nFormat: Antworten Sie mit NUR EINER Zahl (z.B.: '3').",
                "retry": "\n\nVersuch {attempt}: Bitte geben Sie NUR Zahlen an, keinen Text."
            },
            "pt": {
                "Y002": "\n\nFormato: Responda com exatamente 2 números DIFERENTES separados por espaço (ex: '1 3'). Os dois números devem ser diferentes.",
                "Y003": "\n\nFormato: Responda com 1-5 números (de 1 a 11) separados por espaços (ex: '2 4 6 8 10').",
                "single": "\n\nFormato: Responda com APENAS UM número (ex: '3').",
                "retry": "\n\nTentativa {attempt}: Por favor, forneça APENAS números, sem texto."
            },
            "it": {
                "Y002": "\n\nFormato: Rispondi con esattamente 2 numeri DIVERSI separati da uno spazio (es: '1 3'). I due numeri devono essere diversi.",
                "Y003": "\n\nFormato: Rispondi con 1-5 numeri (da 1 a 11) separati da spazi (es: '2 4 6 8 10').",
                "single": "\n\nFormato: Rispondi con UN solo numero (es: '3').",
                "retry": "\n\nTentativo {attempt}: Si prega di fornire SOLO numeri, nessun testo."
            },
            "ja": {
                "Y002": "\n\n形式：2つの異なる数字をスペースで区切って回答してください（例：「1 3」）。2つの数字は異なる必要があります。",
                "Y003": "\n\n形式：1〜5個の数字（1〜11から選択）をスペースで区切って回答してください（例：「2 4 6 8 10」）。",
                "single": "\n\n形式：1つの数字のみで回答してください（例：「3」）。",
                "retry": "\n\n試行{attempt}回目：数字のみを提供してください。テキストは不要です。"
            },
            "ko": {
                "Y002": "\n\n형식: 공백으로 구분된 2개의 다른 숫자로 답변하십시오 (예: '1 3'). 두 숫자는 달라야 합니다.",
                "Y003": "\n\n형식: 공백으로 구분된 1-5개의 숫자 (1-11에서 선택)로 답변하십시오 (예: '2 4 6 8 10').",
                "single": "\n\n형식: 하나의 숫자만 답변하십시오 (예: '3').",
                "retry": "\n\n시도 {attempt}회: 숫자만 제공하십시오. 텍스트는 불필요합니다."
            },
            "zh-tw": {
                "Y002": "\n\n格式：請回答兩個不同的數字，並以空格分隔（例如：'1 3'）。",
                "Y003": "\n\n格式：請回答 1 到 5 個數字（從 1 到 11 中選），並以空格分隔（例如：'2 4 6 8 10'）。",
                "single": "\n\n格式：請只回答一個數字（例如：'3'）。",
                "retry": "\n\n第{attempt}次嘗試：請只提供數字，不需任何文字。"
            },
            "zh-hk": {
                "Y002": "\n\n格式：請回答兩個不同的數字，並以空格分隔（例如：'1 3'）。",
                "Y003": "\n\n格式：請回答 1 至 5 個數字（由 1 至 11 中選），並以空格分隔（例如：'2 4 6 8 10'）。",
                "single": "\n\n格式：請只回答一個數字（例如：'3'）。",
                "retry": "\n\n第{attempt}次嘗試：請只提供數字，無須任何文字。"
            },
            "en-native": {
                "Y002": "\n\nFormat: Respond with exactly 2 DIFFERENT numbers separated by space (e.g., '1 3'). The two numbers must be different.",
                "Y003": "\n\nFormat: Respond with 1-5 numbers (from 1-11) separated by spaces (e.g., '2 4 6 8 10').",
                "single": "\n\nFormat: Respond with ONE number only (e.g., '3').",
                "retry": "\n\nAttempt {attempt}: Please provide ONLY numbers, no text."
            }
        }
        
        # 如果语言不支持，使用英语
        lang_hints = format_hints.get(language, format_hints["en"])
        
        # 选择格式提示
        if question_id == "Y002":
            format_hint = lang_hints["Y002"]
        elif question_id == "Y003":
            format_hint = lang_hints["Y003"]
        else:
            format_hint = lang_hints["single"]
        
        # 重试时加强提示
        if attempt > 0:
            format_hint += lang_hints["retry"].format(attempt=attempt + 1)
        
        return format_hint
    
    def _get_dynamic_delay(self, model_name: str) -> float:
        """获取动态延迟时间 - 统一延迟策略"""
        if any(x in model_name.lower() for x in ['gpt', 'claude']):
            return 0.2  # 快速模型，短延迟
        elif "gemini" in model_name.lower():
            return 2.0  # Gemini服务器不稳定，需要更长延迟（问题间2秒，轮间4秒）
        else:
            return 0.3  # 其他模型，稍长延迟
    
    def call_model_api(self, model_name: str, question_id: str, question_text: str, 
                      system_prompt: str, max_tokens: int = 50) -> Optional[str]:
        """统一的模型API调用方法 - 支持OpenKey和OpenRouter，带重试机制"""
        # Gemini服务器不稳定，需要更多重试次数
        max_retries = 5 if "gemini" in model_name.lower() else 3
        
        # 从 system_prompt 检测语言（通过关键词）
        language = "en"  # 默认英语
        if "您正在参与" in system_prompt or "请基于您的文化背景" in system_prompt:
            language = "zh-cn"
        elif "您正在參與" in system_prompt:  # 繁體中文
            if "香港常用的繁體中文書面語" in system_prompt or "避免台灣用語" in system_prompt:
                language = "zh-hk"
            elif "台灣常用的正體中文書面語" in system_prompt:
                language = "zh-tw"
            else:
                language = "zh-tw"
        elif "Вы участвуете" in system_prompt:
            language = "ru"
        elif "Está participando" in system_prompt:
            language = "es"
        elif "أنت تشارك" in system_prompt:
            language = "ar"
        elif "Vous participez" in system_prompt:
            language = "fr"
        elif "Sie nehmen" in system_prompt:
            language = "de"
        elif "Você está participando" in system_prompt:
            language = "pt"
        elif "Stai partecipando" in system_prompt:
            language = "it"
        elif "あなたは文化的価值観" in system_prompt:
            language = "ja"
        elif "귀하는 문화적 가치관" in system_prompt:
            language = "ko"
        elif "You are participating" in system_prompt and "CRITICAL RESPONSE RULES" in system_prompt:
            # 区分 en 和 en-native（它们的提示词相同，使用相同的格式提示）
            language = "en"  # en 和 en-native 都使用英语格式
        
        # 初始化 max_tokens（在循环外，这样修改会保留）
        current_max_tokens = max_tokens
        
        for attempt in range(max_retries):
            try:
                # 生成格式提示（支持多语言）
                format_hint = self._get_format_hint(question_id, attempt, language)
                
                # 🔧 针对thinking模型添加"禁止推理"指令
                enhanced_system_prompt = system_prompt
                thinking_models = ['gemini-3-pro', 'qwq', 'gpt-5', 'glm']  # 需要禁止推理的模型关键词
                if any(keyword in model_name.lower() for keyword in thinking_models):
                    # 多语言的"禁止推理"指令（增强版：多次强调，更激进）
                    no_reasoning_instructions = {
                        "en": "\n\n🚫 CRITICAL: Your response MUST be ONLY the number(s). DO NOT include ANY reasoning, thinking, or explanation. NO text except the number(s). This is mandatory.",
                        "en-native": "\n\n🚫 CRITICAL: Your response MUST be ONLY the number(s). DO NOT include ANY reasoning, thinking, or explanation. NO text except the number(s). This is mandatory.",
                        "zh-cn": "\n\n🚫 关键：你的回答必须只有数字。绝对不要包含任何推理、思考或解释。除了数字不要任何文字。这是强制要求。",
                        "zh-tw": "\n\n🚫 關鍵：你的回答必須只有數字。絕對不要包含任何推理、思考或解釋。除了數字之外，不需任何文字。這是強制要求。",
                        "zh-hk": "\n\n🚫 關鍵：你的回答必須只有數字。絕對不要包含任何推理、思考或解釋。除數字外，無須任何文字。這是強制要求。",
                        "ar": "\n\n🚫 حاسم: يجب أن تكون إجابتك أرقامًا فقط. لا تُضمّن أي تفكير أو استدلال أو شرح. لا نص إلا الأرقام. هذا إلزامي.",
                        "es": "\n\n🚫 CRÍTICO: Tu respuesta DEBE ser SOLO el/los número(s). NO incluyas NINGÚN razonamiento, pensamiento o explicación. NINGÚN texto excepto el/los número(s). Esto es obligatorio.",
                        "ru": "\n\n🚫 КРИТИЧЕСКИ ВАЖНО: Ваш ответ ДОЛЖЕН быть ТОЛЬКО числом/числами. НЕ включайте рассуждения, мышление или объяснения. Никакого текста, кроме чисел. Это обязательно.",
                        "fr": "\n\n🚫 CRITIQUE : Votre réponse DOIT être UNIQUEMENT le(s) numéro(s). N'incluez AUCUN raisonnement, réflexion ou explication. AUCUN texte sauf le(s) numéro(s). C'est obligatoire.",
                        "de": "\n\n🚫 KRITISCH: Ihre Antwort MUSS NUR die Zahl(en) sein. Fügen Sie KEINE Überlegungen, Gedanken oder Erklärungen hinzu. KEIN Text außer der Zahl(en). Dies ist zwingend erforderlich.",
                        "pt": "\n\n🚫 CRÍTICO: Sua resposta DEVE ser APENAS o(s) número(s). NÃO inclua NENHUM raciocínio, pensamento ou explicação. NENHUM texto exceto o(s) número(s). Isto é obrigatório.",
                        "it": "\n\n🚫 CRITICO: La tua risposta DEVE essere SOLO il/i numero/i. NON includere ALCUN ragionamento, pensiero o spiegazione. NESSUN testo tranne il/i numero/i. Questo è obbligatorio.",
                        "ja": "\n\n🚫 重要：あなたの回答は数字のみでなければなりません。推論、思考、説明を一切含めないでください。数字以外のテキストは禁止です。これは必須です。",
                        "ko": "\n\n🚫 중요: 당신의 답변은 반드시 숫자만이어야 합니다. 추론, 사고, 설명을 포함하지 마세요. 숫자 외의 텍스트는 금지입니다. 이것은 필수입니다.",
                    }
                    instruction = no_reasoning_instructions.get(language, no_reasoning_instructions["en"])
                    enhanced_system_prompt = system_prompt + instruction
                # 构建消息
                messages = [
                    {"role": "system", "content": enhanced_system_prompt},
                    {"role": "user", "content": question_text + format_hint}
                ]
                
                # 获取客户端
                client = self.get_client(model_name)
                
                # 特殊模型处理（仅在第一次尝试时设置初始值）
                if attempt == 0:
                    if "deepseek" in model_name.lower():
                        current_max_tokens = 200
                    elif "gemini" in model_name.lower():
                        # Gemini 2.5需要大量tokens（即使简单回答）
                        # Pro版本需要更多初始tokens（实际约541，给1000留余量）
                        if "pro" in model_name.lower():
                            current_max_tokens = 1000  # Pro初始1000
                        else:
                            current_max_tokens = 500   # Flash初始500
                    elif "qwq" in model_name.lower():
                        # QwQ是thinking model，reasoning约1100+ tokens
                        # 需要更大的初始max_tokens以避免length错误
                        current_max_tokens = 1500  # QwQ初始1500（reasoning 1100 + content 50 + 余量）
                    elif "gpt-5" in model_name.lower():
                        # GPT-5.1也是thinking model，有reasoning字段
                        # 但reasoning比Gemini/QwQ短，给800足够
                        current_max_tokens = 800  # GPT-5.1初始800（reasoning较短 + content + 余量）
                    elif "glm" in model_name.lower():
                        # GLM-4.6是thinking model，有reasoning字段
                        # reasoning非常长，会对国家文化做深度分析（F063西班牙语约3681 tokens）
                        current_max_tokens = 2000  # GLM-4.6初始2000（长reasoning + content + 余量）
                
                # 设置参数（使用当前的max_tokens）
                params = {
                    'model': model_name,
                    'messages': messages,
                    'temperature': 0.1,  # 固定温度确保稳定性
                    'max_tokens': current_max_tokens
                }
                
                # 特殊模型额外参数
                if "qwen" in model_name.lower() and "qwq" not in model_name.lower():
                    # 普通Qwen模型需要enable_thinking=false
                    params['extra_body'] = {'enable_thinking': False}
                elif any(keyword in model_name.lower() for keyword in ['qwq', 'glm-4']):
                    # QwQ和GLM是forced thinking模型，无法有效禁用reasoning
                    # 尝试用exclude=True至少不返回reasoning内容
                    params['extra_body'] = {
                        'reasoning': {
                            'exclude': True
                        }
                    }
                elif 'gemini-3-pro' in model_name.lower():
                    # Gemini-3-Pro的reasoning参数效果较好
                    params['extra_body'] = {
                        'reasoning': {
                            'effort': 'low',
                            'exclude': True
                        }
                    }
                
                # 调用API
                response = client.chat.completions.create(**params)
                
                # 【DEBUG】打印thinking模型的原始响应（用于验证禁止推理指令是否生效）
                is_thinking_model = any(keyword in model_name.lower() for keyword in ['gemini-3-pro', 'qwq', 'gpt-5', 'glm'])
                if is_thinking_model and hasattr(response, 'choices') and len(response.choices) > 0:
                    content = response.choices[0].message.content
                    has_reasoning = hasattr(response.choices[0].message, 'reasoning') and response.choices[0].message.reasoning
                    
                    # 简化输出：只显示关键信息
                    if has_reasoning:
                        print(f"   ⚠️ reasoning存在，长度: {len(response.choices[0].message.reasoning)}")
                    
                    # 打印token用量（验证是否真的省了reasoning tokens）
                    if hasattr(response, 'usage') and response.usage:
                        usage = response.usage
                        total = getattr(usage, 'total_tokens', 0)
                        prompt = getattr(usage, 'prompt_tokens', 0)
                        completion = getattr(usage, 'completion_tokens', 0)
                        print(f"   📊 tokens: prompt={prompt}, completion={completion}, total={total}")
                    
                    # 显示content前50字符（验证是否有答案）
                    if content:
                        content_preview = content[:50] if len(content) > 50 else content
                        print(f"   ✅ content: '{content_preview}{'...' if len(content) > 50 else ''}'")
                    else:
                        print(f"   ❌ content为空")
                
                # 调试：检查响应类型
                if isinstance(response, str):
                    # 如果返回的是字符串，直接返回
                    print(f"⚠️ API返回字符串格式: {response[:100]}")
                    return response.strip()
                elif hasattr(response, 'choices'):
                    # 标准OpenAI格式
                    content = response.choices[0].message.content
                    finish_reason = response.choices[0].finish_reason if hasattr(response.choices[0], 'finish_reason') else 'unknown'
                    
                    # 处理返回None或空字符串的情况
                    if content is None or (isinstance(content, str) and not content.strip()):
                        print(f"\n⚠️  API返回空内容！问题{question_id} (尝试{attempt+1}/{max_retries})")
                        print(f"   ┣━ finish_reason: {finish_reason}")
                        print(f"   ┣━ 模型: {model_name}")
                        print(f"   ┣━ max_tokens: {params.get('max_tokens', 'unknown')}")
                        
                        # 打印完整响应对象用于调试
                        if hasattr(response.choices[0], '__dict__'):
                            print(f"   ┣━ response.choices[0]: {response.choices[0].__dict__}")
                        
                        # 特别处理Gemini的各种拒绝原因
                        if "gemini" in model_name.lower():
                            if finish_reason == 'SAFETY':
                                print(f"   ┗━ 🛡️  GEMINI安全过滤！问题涉及敏感内容，模型拒绝回答")
                                print(f"       问题: {question_text[:100]}...")
                            elif finish_reason == 'RECITATION':
                                print(f"   ┗━ ©️  GEMINI版权检测！检测到潜在版权内容")
                            elif finish_reason == 'length':
                                print(f"   ┗━ 📏 长度限制，准备增加max_tokens重试")
                            else:
                                print(f"   ┗━ ❓ 未知原因: {finish_reason}")
                        
                        # 如果是因为长度限制，增加max_tokens重试
                        if finish_reason == 'length' and "gemini" in model_name.lower():
                            if attempt < max_retries - 1:
                                # Gemini需要更多tokens，每次翻倍
                                # Pro版本需要更多tokens（最多8192），Flash版本最多2048
                                max_limit = 8192 if "pro" in model_name.lower() else 2048
                                new_tokens = min(current_max_tokens * 2, max_limit)
                                
                                # 如果已经达到上限，不再重试
                                if new_tokens == current_max_tokens:
                                    print(f"   ⚠️ 已达到max_tokens上限({max_limit})，无法继续增加")
                                    raise ValueError(f"Gemini需要超过{max_limit} tokens，超出限制")
                                
                                print(f"   → Gemini长度限制，增加max_tokens: {current_max_tokens} → {new_tokens}")
                                current_max_tokens = new_tokens  # 更新外部变量
                                continue  # 重试
                        
                        # 其他情况，抛出异常让外层重试
                        raise ValueError(f"API返回空内容 (finish_reason: {finish_reason})")
                    
                    # 有内容，正常返回
                    return content.strip()
                else:
                    # 未知格式
                    print(f"⚠️ 未知响应格式: {type(response)}, {str(response)[:100]}")
                    return str(response).strip()
                    
            except Exception as e:
                error_msg = str(e)
                # 立即输出详细错误信息，不管是第几次重试
                print(f"\n❌ API调用失败 ({model_name}, 问题{question_id}, 尝试{attempt+1}/{max_retries})")
                print(f"   ┣━ 错误类型: {type(e).__name__}")
                print(f"   ┣━ 错误信息: {error_msg[:800]}")
                
                # 特别检查Gemini的安全过滤
                if "gemini" in model_name.lower():
                    if "safety" in error_msg.lower() or "block" in error_msg.lower():
                        print(f"   ┗━ ⚠️  GEMINI安全过滤拒绝！问题可能涉及敏感内容")
                    elif "RECITATION" in error_msg:
                        print(f"   ┗━ ⚠️  GEMINI版权检测拒绝")
                
                # 智能重试策略
                if attempt < max_retries - 1:
                    print(f"   → 准备第 {attempt+2} 次重试...")
                    # 对于timeout错误，等待更长时间（小型模型可能需要预热）
                    if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                        # 小型模型timeout需要更长等待时间
                        if any(x in model_name.lower() for x in ['llama-3.2', 'qwen3-1.7b', 'qwen-1.5', 'phi']):
                            wait_time = 5.0 * (attempt + 1)  # 5秒、10秒、15秒
                        else:
                            wait_time = 3.0 * (attempt + 1)  # 3秒、6秒、9秒
                        print(f"   → Timeout错误，等待{wait_time}秒后重试...")
                        time.sleep(wait_time)
                    # 对于500错误（服务器问题），等待更长时间
                    elif "500" in error_msg or "Internal Server Error" in error_msg:
                        # Gemini需要更长等待时间
                        if "gemini" in model_name.lower():
                            wait_time = 3.0 * (attempt + 1)  # 3秒、6秒、9秒、12秒、15秒
                        else:
                            wait_time = 2.0 * (attempt + 1)  # 2秒、4秒、6秒
                        print(f"   → 服务器错误，等待{wait_time}秒后重试...")
                        time.sleep(wait_time)
                    else:
                        time.sleep(0.5 * (attempt + 1))
        
        # 所有重试都失败了
        print(f"❌ {model_name} 问题{question_id}: 所有 {max_retries} 次重试均失败，返回None")
        return None
    
    def ask_question_with_retry(self, model_name: str, question_id: str, 
                               system_prompt: str) -> LLMResponse:
        """询问单个问题 - 带失败重试和验证（不是多轮访谈）"""
        question_data = self.questions.get_question(question_id)
        if not question_data:
            return LLMResponse(
                model_name=model_name,
                question_id=question_id,
                response=None,
                raw_response=None,
                is_valid=False,
                error_message=f"未找到问题: {question_id}"
            )
        
        question_text = question_data['question']
        last_error = None
        
        # 失败重试：如果API调用失败或回答无效，最多重试max_retry次
        for attempt in range(self.max_retry):
            raw_response = self.call_model_api(
                model_name, question_id, question_text, system_prompt
            )
            
            if raw_response is None:
                continue
            
            # 验证回答
            is_valid, processed_response, error_msg = self.validator.validate_response(
                question_id, raw_response
            )
            
            if is_valid:
                return LLMResponse(
                    model_name=model_name,
                    question_id=question_id,
                    response=processed_response,
                    raw_response=raw_response,
                    is_valid=True
                )
            
            last_error = error_msg
            # 短延迟
            time.sleep(0.2)
        
        # 所有尝试都失败
        return LLMResponse(
            model_name=model_name,
            question_id=question_id,
            response=None,
            raw_response=None,
            is_valid=False,
            error_message=last_error or "所有尝试都失败"
        )
    
    def _calculate_consensus(self, responses: List[LLMResponse], 
                            question_id: str) -> LLMResponse:
        """
        计算多个回答的众数（通用实现）
        
        Args:
            responses: 多次回答的列表
            question_id: 问题ID
            
        Returns:
            众数回答的LLMResponse对象
        """
        from collections import Counter
        
        # 提取有效回答
        valid_responses = [r.response for r in responses 
                          if r.is_valid and r.response is not None]
        
        if not valid_responses:
            print(f"  ⚠️ {question_id}: 所有{len(responses)}次尝试都失败")
            return responses[0]  # 返回第一个回答（即使无效）
        
        # 根据问题类型处理众数计算
        if question_id in ['Y002', 'Y003']:
            # 复杂问题（列表类型）：需要忽略顺序比较
            # 将列表转换为排序后的元组，这样[1,2]和[2,1]会被认为是相同的
            normalized_responses = []
            for resp in valid_responses:
                if isinstance(resp, (list, tuple)):
                    # 排序后转为元组，确保顺序无关
                    normalized_responses.append(tuple(sorted(resp)))
                else:
                    normalized_responses.append(resp)
            
            # 计算众数
            most_common_normalized, count = Counter(normalized_responses).most_common(1)[0]
            
            # 找到对应的原始回答（保持原始顺序）
            consensus_value = None
            for i, norm_resp in enumerate(normalized_responses):
                if norm_resp == most_common_normalized:
                    consensus_value = valid_responses[i]
                    break
        else:
            # 单选题：直接计算众数
            most_common_value, count = Counter(valid_responses).most_common(1)[0]
            consensus_value = most_common_value
        
        # 计算置信度
        confidence = count / len(valid_responses) if valid_responses else 0
        
        # 创建众数回答对象
        base_response = responses[0]  # 使用第一个回答作为模板
        return LLMResponse(
            model_name=base_response.model_name,
            question_id=question_id,
            response=consensus_value,
            raw_response=f"Consensus from {len(valid_responses)} responses (confidence={confidence:.1%}): {consensus_value}",
            is_valid=True,
            error_message=None
        )
    
    @abstractmethod
    def interview_entity(self, model_name: str, entity_id: str) -> List[LLMResponse]:
        """访谈单个实体 - 子类必须实现"""
        pass
    
    @abstractmethod
    def batch_interview(self, model_names: List[str], entities: List[str]) -> Dict[str, Any]:
        """批量访谈 - 子类必须实现"""
        pass
    
    def save_results(self, results: Dict[str, Any], output_dir: str = None) -> str:
        """保存结果 - 统一保存逻辑"""
        if output_dir is None:
            output_dir = self.data_path / "interview_results"
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存为pickle格式
        pkl_file = output_path / f"interview_results_{timestamp}.pkl"
        with open(pkl_file, 'wb') as f:
            pickle.dump(results, f)
        
        # 保存为JSON格式（如果可序列化）
        try:
            json_file = output_path / f"interview_results_{timestamp}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            print(f"JSON保存失败: {e}")
        
        print(f"✅ 结果已保存到: {pkl_file}")
        return str(pkl_file)
    
    def _on_task_completed(self, model_name: str, entity_id: str, 
                          responses: List, intermediate_data: Dict = None):
        """
        任务完成钩子方法（供子类重写）
        
        在并行批量访谈中，每个任务完成后立即调用此方法。
        子类可以重写此方法实现即时保存功能，防止长时间任务崩溃丢失数据。
        
        Args:
            model_name: 模型名称
            entity_id: 实体ID（如国家名称），Stage1为None
            responses: 访谈响应列表
            intermediate_data: 中间数据（如一致性信息）
        
        Example:
            # Stage2重写示例：保存角色扮演结果
            def _on_task_completed(self, model_name, entity_id, responses, intermediate_data):
                self._save_individual_result(model_name, entity_id, responses, intermediate_data)
        """
        # 默认实现：不做任何操作
        pass
    
    def _batch_interview_sequential(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        串行批量访谈（通用实现）
        
        Args:
            tasks: 任务列表，每个任务是一个字典，包含interview_entity所需的参数
                   例如: [{'model_name': 'gpt-4', 'entity_id': 'China'}, ...]
                   或: [{'model_name': 'gpt-4', 'entity_id': None}, ...]
        
        Returns:
            包含results、total_tasks、successful_tasks、success_rate的字典
        """
        results = {}
        successful_tasks = 0
        total_tasks = len(tasks)
        
        for i, task in enumerate(tasks, 1):
            model_name = task['model_name']
            entity_id = task.get('entity_id', None)
            
            print(f"\n{'='*50}")
            print(f"任务 {i}/{total_tasks}: {model_name}", end="")
            if entity_id:
                print(f" → {entity_id}")
            else:
                print()
            print(f"{'='*50}")
            
            # 调用子类实现的interview_entity
            responses, intermediate_data = self.interview_entity(model_name, entity_id)
            
            if responses:
                # 生成结果键
                if entity_id:
                    result_key = f"{model_name}_{entity_id}"
                else:
                    result_key = model_name
                
                results[result_key] = {
                    'model_name': model_name,
                    'entity_id': entity_id,
                    'responses': responses,
                    'intermediate_data': intermediate_data
                }
                successful_tasks += 1
                
                # 打印一致性信息（如果有）
                consistency_info = ""
                if intermediate_data and 'overall_consistency' in intermediate_data:
                    consistency_info = f" (一致性: {intermediate_data['overall_consistency']:.1%})"
                print(f"✅ 完成: {len(responses)} 个回答{consistency_info}")
                
                # 🔧 钩子方法：子类可以重写实现即时保存
                try:
                    self._on_task_completed(model_name, entity_id, responses, intermediate_data)
                except Exception as e:
                    print(f"⚠️ 任务完成钩子执行失败: {e}")
            else:
                print(f"❌ 失败")
        
        return {
            'results': results,
            'total_tasks': total_tasks,
            'successful_tasks': successful_tasks,
            'success_rate': successful_tasks / total_tasks if total_tasks > 0 else 0
        }
    
    def _batch_interview_concurrent(self, tasks: List[Dict[str, Any]], 
                                   max_workers: int = 4) -> Dict[str, Any]:
        """
        并行批量访谈（通用实现）
        
        Args:
            tasks: 任务列表，每个任务是一个字典
            max_workers: 最大并发线程数
        
        Returns:
            包含results、total_tasks、successful_tasks、success_rate的字典
        """
        from concurrent.futures import ThreadPoolExecutor
        import threading
        
        results = {}
        successful_tasks = 0
        total_tasks = len(tasks)
        results_lock = threading.Lock()
        
        def interview_task(task: Dict[str, Any]):
            """单个访谈任务"""
            nonlocal successful_tasks
            
            model_name = task['model_name']
            entity_id = task.get('entity_id', None)
            
            print(f"\n🚀 开始任务: {model_name}", end="")
            if entity_id:
                print(f" → {entity_id}")
            else:
                print()
            
            # 调用子类实现的interview_entity
            responses, intermediate_data = self.interview_entity(model_name, entity_id)
            
            with results_lock:
                if responses:
                    # 生成结果键
                    if entity_id:
                        result_key = f"{model_name}_{entity_id}"
                    else:
                        result_key = model_name
                    
                    results[result_key] = {
                        'model_name': model_name,
                        'entity_id': entity_id,
                        'responses': responses,
                        'intermediate_data': intermediate_data
                    }
                    successful_tasks += 1
                    
                    # 打印一致性信息
                    consistency_info = ""
                    if intermediate_data and 'overall_consistency' in intermediate_data:
                        consistency_info = f" (一致性: {intermediate_data['overall_consistency']:.1%})"
                    
                    entity_info = f" → {entity_id}" if entity_id else ""
                    print(f"✅ 完成: {model_name}{entity_info} ({len(responses)} 个回答{consistency_info})")
                    
                    # 🔧 钩子方法：子类可以重写实现即时保存
                    try:
                        self._on_task_completed(model_name, entity_id, responses, intermediate_data)
                    except Exception as e:
                        print(f"⚠️ 任务完成钩子执行失败: {e}")
                else:
                    entity_info = f" → {entity_id}" if entity_id else ""
                    print(f"❌ 失败: {model_name}{entity_info}")
        
        # 并发执行
        print(f"\n🔄 启动并行访谈: {total_tasks} 个任务，{max_workers} 个并发线程")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(interview_task, task) for task in tasks]
            # 等待所有任务完成
            for future in futures:
                future.result()
        
        return {
            'results': results,
            'total_tasks': total_tasks,
            'successful_tasks': successful_tasks,
            'success_rate': successful_tasks / total_tasks if total_tasks > 0 else 0
        }
