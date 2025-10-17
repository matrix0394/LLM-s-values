"""
大模型国家角色扮演访谈模块
让大模型模仿特定国家的文化背景回答IVS问题
基于llm_interview.py进行扩展
"""

import os
import json
import time
import pickle
from datetime import datetime
from openai import OpenAI
from src.llm_analysis.llm_questionnaire import IVSQuestions, LLMResponse
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
from pathlib import Path
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import threading


class LLMCountryRoleplayInterview:
    """大模型国家角色扮演访谈类"""
    
    def __init__(self, repeat_count: int = 1, data_path: str = "../data"):
        self.questions = IVSQuestions()
        self.model_configs = self._load_model_configs()
        self.api_keys = self._load_api_keys()
        self.repeat_count = repeat_count
        self.data_path = data_path
        
        # 加载国家和文化区域数据
        self.countries_data = self._load_countries_data()
        self.cultural_regions = self._load_cultural_regions()
        
        # 改进的系统prompt，避免触发内容过滤
        self.base_system_prompt = """You are participating in a cultural values survey. Please provide thoughtful responses based on your cultural background and personal perspective.

Please follow these guidelines:
- Answer each question with a genuine, considered response
- Choose the option that best reflects your cultural values and beliefs
- Respond as a real person from your country would

Response format:
- Single choice questions: respond with ONE number only
- Y002 (two choices): respond with TWO numbers separated by space
- Y003 (multiple choices): respond with 1-5 numbers separated by spaces

Please provide meaningful answers that reflect your cultural perspective."""
    
    def _load_model_configs(self) -> Dict[str, Dict[str, str]]:
        """从配置文件加载模型配置"""
        # 修正配置文件路径 - 配置在项目根目录的config下
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'llm_models.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('models', {})
        except Exception as e:
            print(f"加载模型配置失败: {e}")
            return {}
    
    def _load_api_keys(self) -> Dict[str, str]:
        """从环境变量加载API密钥"""
        api_keys = {}
        for model_name, config in self.model_configs.items():
            api_key_name = config.get("api_key", "OPENROUTER_API_KEY")
            api_key_value = os.getenv(api_key_name)
            if api_key_value:
                api_keys[model_name] = api_key_value
            else:
                print(f"警告: 环境变量 {api_key_name} 未设置，模型 {model_name} 将无法使用")
        return api_keys
    
    def _load_countries_data(self) -> pd.DataFrame:
        """加载国家数据"""
        try:
            # 修正路径 - 数据在项目根目录的data下
            country_codes_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "processed", "country_codes.pkl")
            if os.path.exists(country_codes_path):
                return pd.read_pickle(country_codes_path)
            else:
                print(f"警告: 未找到国家数据文件 {country_codes_path}")
                return pd.DataFrame()
        except Exception as e:
            print(f"加载国家数据失败: {e}")
            return pd.DataFrame()
    
    def _load_cultural_regions(self) -> Dict[str, Any]:
        """加载文化区域配置"""
        try:
            # 修正路径 - 配置在项目根目录的config下
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'cultural_regions.json')
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载文化区域配置失败: {e}")
            return {"cultural_regions": {}}
    
    def get_all_countries(self) -> List[str]:
        """获取所有有真实价值观数据的国家列表（109个国家）"""
        try:
            # 只从country_scores_pca.pkl获取有真实数据的国家
            country_scores_path = os.path.join(self.data_path, "country_scores_pca.pkl")
            if os.path.exists(country_scores_path):
                country_scores_df = pd.read_pickle(country_scores_path)
                if 'Country' in country_scores_df.columns:
                    countries = country_scores_df['Country'].dropna().unique().tolist()
                    print(f"从country_scores_pca.pkl加载了 {len(countries)} 个有真实数据的国家")
                    return sorted(countries)
                else:
                    print("警告: country_scores_pca.pkl中没有'Country'列")
                    return []
            else:
                print(f"警告: 未找到country_scores_pca.pkl文件: {country_scores_path}")
                return []
        except Exception as e:
            print(f"加载国家数据失败: {e}")
            return []
    
    def get_country_region(self, country_name: str) -> str:
        """获取国家所属的文化区域"""
        # 首先从国家数据中查找
        if not self.countries_data.empty and 'Country' in self.countries_data.columns:
            country_row = self.countries_data[self.countries_data['Country'] == country_name]
            if not country_row.empty and 'Cultural Region' in country_row.columns:
                region = country_row['Cultural Region'].iloc[0]
                if pd.notna(region):
                    return region
        
        # 从文化区域配置中查找
        for region_name, region_data in self.cultural_regions.get('cultural_regions', {}).items():
            if country_name in region_data.get('countries', []):
                return region_name
        
        return "Unknown"
    
    def create_country_roleplay_prompt(self, country_name: str) -> str:
        """为特定国家创建角色扮演系统提示词 - 改进版"""
        region = self.get_country_region(country_name)
        
        # 获取区域描述
        region_description = ""
        if region != "Unknown":
            region_info = self.cultural_regions.get('cultural_regions', {}).get(region, {})
            region_description = region_info.get('description', f"Countries in the {region} cultural region")
        
        # 根据文化区域添加特定的文化特征描述
        cultural_characteristics = self._get_cultural_characteristics(region)
        
        # 随机选择身份确定的prompt，增加多样性
        identity_prompts = self._get_identity_prompts(country_name, region, cultural_characteristics)
        selected_prompt = identity_prompts[hash(country_name) % len(identity_prompts)]
        
        roleplay_prompt = f"""{selected_prompt}

You are responding to a cultural values survey. Answer based on how a typical person from {country_name} would respond, considering the cultural values, beliefs, and attitudes common in your country.

{self.base_system_prompt}"""
        
        return roleplay_prompt
    
    def _get_cultural_characteristics(self, region: str) -> str:
        """根据文化区域获取文化特征描述"""
        characteristics_map = {
            "African-Islamic": "Strong community values, respect for authority, traditional family structures, religious influence",
            "Confucian": "Emphasis on harmony, respect for hierarchy, education, family obligations, social stability",
            "Latin America": "Strong family bonds, religious influence, community orientation, respect for authority",
            "Protestant Europe": "Individualism, secular values, gender equality, environmental consciousness, social tolerance",
            "Catholic Europe": "Traditional values, family importance, religious influence, social solidarity",
            "English-Speaking": "Individualism, personal freedom, achievement orientation, pragmatism, social mobility",
            "Orthodox Europe": "Traditional values, respect for authority, community orientation, religious influence",
            "West & South Asia": "Strong family values, respect for elders, religious influence, community orientation"
        }
        return characteristics_map.get(region, "Traditional values, community orientation, respect for authority")
    
    def _get_identity_prompts(self, country_name: str, region: str, cultural_characteristics: str) -> List[str]:
        """获取多种身份确定的prompt，增加多样性"""
        # 根据国家名称生成不同的年龄，确保同一国家使用相同年龄
        age = 25 + (hash(country_name) % 30)  # 年龄范围：25-54岁
        
        identity_prompts = [
            # 基础身份描述 - 强调真实性和代表性
            f"You are a {age}-year-old citizen born and raised in {country_name}. You have lived in {country_name} your entire life and deeply understand the cultural values, traditions, and social norms of your country. As someone from the {region} cultural region, you naturally embody these values: {cultural_characteristics}. You are participating in this survey to share your genuine cultural perspective.",
            
            # 职业身份 - 强调教育背景和文化理解
            f"You are a {age}-year-old teacher from {country_name}. You were born and educated in {country_name}, and you have spent your life teaching and understanding the cultural values of your society. Your perspective represents the {region} cultural region, where these values are deeply rooted: {cultural_characteristics}. You are committed to providing authentic answers that reflect your cultural background.",
            
            # 家庭身份 - 强调传统价值观
            f"You are a {age}-year-old parent from {country_name}. You were born in {country_name} and have raised your family there, deeply understanding the traditional values and cultural norms of your country. Your perspective embodies the {region} cultural region's values: {cultural_characteristics}. You want to share your genuine cultural perspective in this survey.",
            
            # 社区身份 - 强调社会参与
            f"You are a {age}-year-old active community member from {country_name}. You have been living in {country_name} since birth and are deeply involved in your local community, understanding the social and cultural dynamics of your country. Your views represent the {region} cultural region: {cultural_characteristics}. You are eager to provide thoughtful answers based on your cultural experience.",
            
            # 工作身份 - 强调社会经验
            f"You are a {age}-year-old office worker from {country_name}. You were born in {country_name} and have worked there your entire career, experiencing the social and cultural environment firsthand. Your perspective reflects the {region} cultural region's values: {cultural_characteristics}. You are determined to give meaningful answers that represent your cultural background.",
            
            # 专业人士身份 - 强调深度理解
            f"You are a {age}-year-old professional from {country_name}. You were born, educated, and have built your career in {country_name}, giving you deep insight into your country's cultural values and social norms. Your perspective embodies the {region} cultural region: {cultural_characteristics}. You are committed to providing authentic responses that reflect your cultural understanding.",
            
            # 邻居身份 - 强调日常文化体验
            f"You are a {age}-year-old neighbor from {country_name}. You have lived in {country_name} all your life and have experienced the daily cultural practices and social interactions that shape your worldview. Your perspective represents the {region} cultural region: {cultural_characteristics}. You want to share your genuine cultural insights in this survey.",
            
            # 朋友身份 - 强调人际关系和文化理解
            f"You are a {age}-year-old friend from {country_name}. You have lived in {country_name} since birth and have built meaningful relationships within your cultural community. Your perspective reflects the {region} cultural region's values: {cultural_characteristics}. You are enthusiastic about providing thoughtful answers based on your cultural experience.",
            
            # 同事身份 - 强调工作文化
            f"You are a {age}-year-old colleague from {country_name}. You were born in {country_name} and have worked there throughout your career, understanding the professional and cultural environment of your country. Your views embody the {region} cultural region: {cultural_characteristics}. You are determined to give meaningful answers that represent your cultural background.",
            
            # 居民身份 - 强调本土经验
            f"You are a {age}-year-old lifelong resident of {country_name}. You have never lived anywhere else and have a deep, authentic understanding of your country's culture, values, and social norms. Your perspective represents the {region} cultural region: {cultural_characteristics}. You are committed to providing genuine answers that reflect your cultural identity.",
            
            # 文化传承者身份 - 强调文化传承
            f"You are a {age}-year-old cultural bearer from {country_name}. You were born and raised in {country_name}, and you actively participate in preserving and passing on your country's cultural traditions and values. Your perspective embodies the {region} cultural region: {cultural_characteristics}. You are passionate about sharing your authentic cultural perspective in this survey.",
            
            # 社会观察者身份 - 强调社会理解
            f"You are a {age}-year-old social observer from {country_name}. You have lived in {country_name} your entire life and have developed a keen understanding of your country's social dynamics and cultural values through observation and participation. Your perspective reflects the {region} cultural region: {cultural_characteristics}. You are eager to provide insightful answers based on your cultural understanding.",
        ]
        
        return identity_prompts
    
    def get_client(self, model_name: str) -> OpenAI:
        """获取OpenAI客户端"""
        if model_name not in self.model_configs:
            raise ValueError(f"不支持的模型: {model_name}")
        
        config = self.model_configs[model_name]
        api_key = self.api_keys.get(model_name)
        
        if not api_key:
            raise ValueError(f"模型 {model_name} 的API密钥未设置")
        
        return OpenAI(
            api_key=api_key,
            base_url=config.get("base_url", "https://api.openai.com/v1")
        )
    
    def call_model_api_improved(self, model_name: str, question_id: str, question_text: str, system_prompt: str) -> Optional[str]:
        """改进的模型API调用方法 - 参照标准LLM模块"""
        try:
            client = self.get_client(model_name)
            
            # 增强的重试机制 - 最多5次重试
            max_retries = 5
            for attempt in range(max_retries):
                try:
                    # 根据问题类型添加格式提示
                    format_hint = ""
                    if question_id == "Y002":
                        format_hint = "\n\nPlease respond with exactly 2 numbers separated by space."
                    elif question_id == "Y003":
                        format_hint = "\n\nPlease respond with 1-5 numbers separated by spaces."
                    
                    # 在重试时加强提示
                    if attempt > 0:
                        format_hint += f"\n\nThis is attempt {attempt + 1}. Please provide a genuine numerical answer that reflects your cultural perspective. Choose the option that best represents your values."
                    
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": question_text + format_hint}
                    ]
                    
                    # 特殊模型处理
                    max_tokens = 50
                    # 在重试时使用更高的温度来鼓励更多样化的回答
                    temperature = 0.3 + (attempt * 0.2)  # 0.3, 0.5, 0.7, 0.9, 1.1
                    
                    # 对deepseek模型使用更大的max_tokens
                    if "deepseek" in model_name.lower():
                        max_tokens = 500
                        
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        timeout=60  # 增加超时时间
                    )
                    
                    # 处理deepseek的特殊响应格式
                    if "deepseek" in model_name.lower():
                        # 尝试从reasoning_content中提取数字
                        message = response.choices[0].message
                        content = message.content or ""
                        if hasattr(message, 'reasoning_content') and message.reasoning_content:
                            # 如果content为空但有reasoning_content，尝试从reasoning中提取数字
                            if not content.strip():
                                import re
                                # 提取所有数字序列
                                numbers = re.findall(r'\b\d+(?:\s+\d+)*\b', message.reasoning_content)
                                if numbers:
                                    # 使用最后出现的数字序列作为答案
                                    content = numbers[-1]
                    else:
                        content = response.choices[0].message.content
                        
                    if content:
                        content = content.strip()
                        
                        # 检测拒绝回答的模式（移除默认值检测）
                        refusal_patterns = [
                            "i am an ai", "i'm an ai", "as an ai", "language model",
                            "cannot roleplay", "can't roleplay", "i cannot", "i can't",
                            "refuse to", "unable to answer", "不能回答", "无法回答",
                            "i don't", "i do not", "i won't", "i will not",
                            "i'm not sure", "i don't know", "i'm uncertain",
                            "i cannot provide", "i can't provide", "i cannot give",
                            "i'm unable to", "i cannot answer", "i can't answer",
                            "i cannot respond", "i can't respond", "i cannot reply",
                            "i'm not able to", "i cannot help", "i can't help"
                        ]
                        
                        # 只检查是否是拒绝回答，不检查默认值
                        is_refusal = any(pattern in content.lower() for pattern in refusal_patterns)
                        
                        if not is_refusal:
                            return content
                        elif attempt == max_retries - 1:
                            # 最后一次尝试失败时返回None
                            return None
                    
                except Exception as e:
                    if attempt == max_retries - 1:
                        print(f"    API调用失败: {e}")
                        return None
                    time.sleep(1)  # 重试前等待
            
            return None  # 不造答案，返回None
            
        except Exception as e:
            print(f"    API调用失败: {e}")
            return None
    
    def ask_question_roleplay(self, model_name: str, country_name: str, question_id: str) -> LLMResponse:
        """让模型以特定国家角色回答问题 - 改进版，支持多次回答取众数"""
        question_text = self.questionnaire.questions.get_question(question_id)
        if not question_text:
            return LLMResponse(
                model_name=f"{model_name}_as_{country_name}",
                question_id=question_id,
                response=None,
                raw_response="",
                is_valid=False,
                error_message=f"未知问题ID: {question_id}"
            )
        
        # 创建国家特定的系统提示词
        system_prompt = self.create_country_roleplay_prompt(country_name)
        
        # 多次调用API获取更稳定的回答
        responses = []
        for i in range(self.repeat_count):
            raw_response = self.call_model_api_improved(model_name, question_id, question_text, system_prompt)
            if raw_response:
                responses.append(raw_response)
            # 根据模型类型调整延迟
            if any(x in model_name.lower() for x in ['gpt', 'claude']):
                time.sleep(0.3)  # 较快的模型
            else:
                time.sleep(0.5)  # 其他模型保持现有延迟
        
        if not responses:
            return LLMResponse(
                model_name=f"{model_name}_as_{country_name}",
                question_id=question_id,
                response=None,
                raw_response=None,
                is_valid=False,
                error_message="API调用失败"
            )
        
        # 使用众数作为最终回答
        final_response = self.get_mode_response(responses)
        
        # 如果没有有效的众数回答，返回失败
        if final_response is None:
            return LLMResponse(
                model_name=f"{model_name}_as_{country_name}",
                question_id=question_id,
                response=None,
                raw_response=None,
                is_valid=False,
                error_message="无法获得有效的众数回答"
            )
        
        # 验证回答
        from src.llm_analysis.llm_questionnaire import ResponseValidator
        validator = ResponseValidator()
        is_valid, parsed_response, error_msg = validator.validate_response(question_id, final_response)
        
        return LLMResponse(
            model_name=f"{model_name}_as_{country_name}",
            question_id=question_id,
            response=parsed_response,
            raw_response=final_response,
            is_valid=is_valid,
            error_message=error_msg if not is_valid else None
        )
    
    def get_mode_response(self, responses: List[str]) -> str:
        """计算多次回答的众数"""
        from collections import Counter
        
        valid_responses = [r for r in responses if r and r.strip()]
        
        if not valid_responses:
            return None  # 没有有效回答时返回None，不造答案
        
        counter = Counter(valid_responses)
        most_common = counter.most_common(1)
        
        if most_common:
            return most_common[0][0]
        else:
            return valid_responses[0]
    
    
    def interview_model_as_country(self, model_name: str, country_name: str) -> List[LLMResponse]:
        """让模型以特定国家身份接受访谈"""
        print(f"\n=== {model_name} 模仿 {country_name} 的访谈 ===")
        region = self.get_country_region(country_name)
        print(f"文化区域: {region}")
        
        if self.repeat_count > 1:
            print(f"每个问题重复 {self.repeat_count} 次，取众数")
        
        if model_name not in self.api_keys:
            print(f"跳过模型 {model_name}: API密钥未设置")
            return []
        
        results = []
        question_ids = list(self.questionnaire.questions.get_all_questions().keys())
        
        for i, question_id in enumerate(question_ids, 1):
            print(f"  问题 {i}/{len(question_ids)}: {question_id}")
            
            # 使用角色扮演版本的提问方法
            response = self.ask_question_roleplay(model_name, country_name, question_id)
            
            if response.raw_response is None:
                print(f"  跳过 {model_name} 模仿 {country_name}（API调用失败）")
                return []
            
            if response.is_valid:
                print(f"    最终回答: {response.raw_response} -> {response.response}")
            else:
                print(f"    无效回答: {response.raw_response} ({response.error_message})")
            
            results.append(response)
            
            # 添加延迟避免API限制
            time.sleep(0.5)
        
        return results
    
    def batch_country_roleplay_interview_parallel_optimized(self, model_names: List[str] = None,
                                                       countries: List[str] = None, 
                                                       max_countries: int = None,
                                                       max_workers: int = 3) -> Dict[str, List[LLMResponse]]:
        """并行批量进行国家角色扮演访谈，带实时保存优化"""
        if model_names is None:
            model_names = list(self.model_configs.keys())
        
        if countries is None:
            countries = self.get_all_countries()
        
        if max_countries and len(countries) > max_countries:
            countries = countries[:max_countries]
        
        print(f"开始并行批量国家角色扮演访谈（优化版）")
        print(f"模型列表: {model_names}")
        print(f"国家数量: {len(countries)}")
        print(f"并行线程数: {max_workers}")
        print(f"预计任务数: {len(model_names) * len(countries)}")
        
        all_results = {}
        results_lock = threading.Lock()  # 线程安全锁
        
        def process_single_country(model_name: str, country_name: str) -> Tuple[str, str, List[LLMResponse]]:
            """处理单个国家的访谈"""
            try:
                print(f"\n🚀 开始: {model_name} 模仿 {country_name}")
                results = self.interview_model_as_country(model_name, country_name)
                
                if results:
                    # 立即保存结果
                    entity_key = f"{model_name}_as_{country_name}"
                    single_result = {entity_key: results}
                    
                    # 修复参数顺序
                    self._save_intermediate_results_optimized_v2(model_name, country_name, single_result)
                    
                    valid_count = sum(1 for r in results if r.is_valid)
                    print(f"✅ 完成并保存: {entity_key} ({valid_count}/{len(results)} 有效)")
                    
                    return model_name, country_name, results
                else:
                    print(f"❌ 失败: {model_name} 模仿 {country_name}")
                    return model_name, country_name, None
                    
            except Exception as e:
                print(f"💥 异常: {model_name} 模仿 {country_name} - {str(e)}")
                return model_name, country_name, None
        
        # 创建任务列表
        tasks = []
        for model_name in model_names:
            if model_name not in self.api_keys:
                print(f"⚠️  跳过模型 {model_name}: API密钥未设置")
                continue
            for country_name in countries:
                tasks.append((model_name, country_name))
        
        print(f"\n📋 实际任务数: {len(tasks)}")
        
        # 并行执行任务
        completed_count = 0
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_task = {
                executor.submit(process_single_country, model_name, country_name): (model_name, country_name)
                for model_name, country_name in tasks
            }
            
            # 处理完成的任务
            for future in concurrent.futures.as_completed(future_to_task):
                model_name, country_name = future_to_task[future]
                try:
                    model_name_result, country_name_result, results = future.result()
                    
                    if results:
                        with results_lock:
                            entity_key = f"{model_name_result}_as_{country_name_result}"
                            all_results[entity_key] = results
                            completed_count += 1
                            
                        print(f"📊 进度: {completed_count}/{len(tasks)} 完成 ({completed_count/len(tasks)*100:.1f}%)")
                        
                except Exception as exc:
                    print(f"💥 任务异常: {model_name}_as_{country_name} - {exc}")
        
        print(f"\n🎉 所有任务完成！总共完成 {len(all_results)} 个角色扮演")
        return all_results
    
    def _save_intermediate_results_optimized_v2(self, model_name, country_name, results):
        """
        保存中间结果的优化版本，统一文件夹结构，简化文件名
        """
        try:
            # 处理模型名称中的特殊字符，统一文件夹命名规则
            safe_model_name = model_name.replace('/', '_').replace(':', '_').replace('-', '_')
            safe_country_name = country_name.replace(' ', '_').replace('&', 'and')
            
            # 提取简化的模型名称（去掉供应商前缀）
            def get_simplified_model_name(full_model_name):
                # 处理带供应商前缀的模型名
                if '/' in full_model_name:
                    # 提取供应商后的模型名
                    simplified = full_model_name.split('/')[-1]
                else:
                    simplified = full_model_name
                
                # 处理特殊情况
                if ':' in simplified:
                    simplified = simplified.replace(':', '-')
                
                return simplified
            
            simplified_model_name = get_simplified_model_name(model_name)
            
            # 创建统一的分层目录结构: data/llm_responses_roleplay/roleplay_intermediate_modelname/
            output_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                'data', 'llm_responses_roleplay', 
                f'roleplay_intermediate_{safe_model_name}'
            )
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 保存详细回答（使用简化的文件名格式）- 修复：使用safe_country_name
            detailed_file = os.path.join(output_dir, f"{simplified_model_name}_{safe_country_name}.pkl")
            
            # 转换为可序列化的格式
            serializable_results = {}
            for key, responses in results.items():
                serializable_results[key] = [
                    {
                        'model_name': resp.model_name,
                        'question_id': resp.question_id,
                        'response': resp.response,
                        'raw_response': resp.raw_response,
                        'is_valid': resp.is_valid,
                        'error_message': resp.error_message
                    }
                    for resp in responses
                ]
            
            # 保存详细数据
            with open(detailed_file, 'wb') as f:
                pickle.dump(serializable_results, f)
            
            # 保存摘要统计（可选）
            summary_file = os.path.join(output_dir, f"{safe_country_name}_summary_{timestamp}.json")
            summary_data = {
                'model_name': model_name,
                'simplified_model_name': simplified_model_name,
                'country_name': country_name,
                'timestamp': timestamp,
                'total_questions': sum(len(resp_list) for resp_list in results.values()),
                'valid_responses': sum(1 for resp_list in results.values() for resp in resp_list if resp.is_valid),
                'completion_time': datetime.now().isoformat()
            }
            
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 已保存 {model_name} 模仿 {country_name} 的结果到: {detailed_file}")
            
        except Exception as e:
            print(f"❌ 保存结果时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def check_existing_results(self, model_name: str, country_name: str) -> bool:
        """检查指定模型和国家的结果是否已存在"""
        try:
            # 使用与保存函数相同的逻辑
            safe_model_name = model_name.replace('/', '_').replace(':', '_').replace('-', '_')
            safe_country_name = country_name.replace(' ', '_').replace('&', 'and')
            
            # 提取简化的模型名称（与保存函数保持一致）
            def get_simplified_model_name(full_model_name):
                if '/' in full_model_name:
                    simplified = full_model_name.split('/')[-1]
                else:
                    simplified = full_model_name
                
                if ':' in simplified:
                    simplified = simplified.replace(':', '-')
                
                return simplified
            
            simplified_model_name = get_simplified_model_name(model_name)
            
            # 构建文件路径
            output_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                'data', 'llm_responses_roleplay', 
                f'roleplay_intermediate_{safe_model_name}'
            )
            
            # 检查简化文件名格式的文件
            detailed_file = os.path.join(output_dir, f"{simplified_model_name}_{safe_country_name}.pkl")
            
            return os.path.exists(detailed_file)
            
        except Exception as e:
            print(f"检查现有结果时出错: {e}")
            return False
    
    def get_completion_status(self, model_names: List[str], countries: List[str]) -> Dict[str, Dict[str, bool]]:
        """获取所有任务的完成状态"""
        status = {}
        
        for model_name in model_names:
            status[model_name] = {}
            for country_name in countries:
                status[model_name][country_name] = self.check_existing_results(model_name, country_name)
        
        return status
    
    def print_completion_summary(self, status: Dict[str, Dict[str, bool]], model_names: List[str], countries: List[str]):
        """打印完成状态摘要"""
        total_tasks = len(model_names) * len(countries)
        completed_tasks = sum(1 for model in status.values() for completed in model.values() if completed)
        remaining_tasks = total_tasks - completed_tasks
        
        print(f"\n📊 任务完成状态摘要:")
        print(f"总任务数: {total_tasks}")
        print(f"已完成: {completed_tasks} ({completed_tasks/total_tasks*100:.1f}%)")
        print(f"待完成: {remaining_tasks} ({remaining_tasks/total_tasks*100:.1f}%)")
        
        if completed_tasks > 0:
            print(f"\n✅ 已完成的任务:")
            for model_name in model_names:
                completed_countries = [country for country, is_done in status[model_name].items() if is_done]
                if completed_countries:
                    print(f"  {model_name}: {len(completed_countries)} 个国家 ({', '.join(completed_countries[:3])}{'...' if len(completed_countries) > 3 else ''})")
        
        if remaining_tasks > 0:
            print(f"\n⏳ 待完成的任务:")
            for model_name in model_names:
                remaining_countries = [country for country, is_done in status[model_name].items() if not is_done]
                if remaining_countries:
                    print(f"  {model_name}: {len(remaining_countries)} 个国家 ({', '.join(remaining_countries[:3])}{'...' if len(remaining_countries) > 3 else ''})")
    
    def batch_country_roleplay_interview_with_resume(self, model_names: List[str] = None,
                                                countries: List[str] = None, 
                                                max_countries: int = None,
                                                max_workers: int = 3,
                                                force_restart: bool = False) -> Dict[str, List[LLMResponse]]:
        """支持断点续传的并行批量国家角色扮演访谈"""
        if model_names is None:
            model_names = list(self.model_configs.keys())
        
        if countries is None:
            countries = self.get_all_countries()
        
        if max_countries and len(countries) > max_countries:
            countries = countries[:max_countries]
        
        # 过滤有API密钥的模型
        available_models = [name for name in model_names if name in self.api_keys]
        if not available_models:
            print("❌ 没有可用的模型")
            return {}
        
        print(f"🚀 开始支持断点续传的并行批量访谈")
        print(f"模型列表: {available_models}")
        print(f"国家数量: {len(countries)}")
        print(f"并行线程数: {max_workers}")
        print(f"强制重新开始: {force_restart}")
        
        # 检查完成状态
        if not force_restart:
            completion_status = self.get_completion_status(available_models, countries)
            self.print_completion_summary(completion_status, available_models, countries)
            
            # 创建待处理任务列表
            pending_tasks = []
            for model_name in available_models:
                for country_name in countries:
                    if not completion_status[model_name][country_name]:
                        pending_tasks.append((model_name, country_name))
            
            if not pending_tasks:
                print("🎉 所有任务都已完成！")
                # 加载现有结果
                return self.load_existing_results(available_models, countries)
            
            print(f"\n⏳ 需要处理 {len(pending_tasks)} 个待完成任务")
            
            # 询问用户是否继续
            user_input = input("\n是否继续处理待完成的任务？(y/n): ").strip().lower()
            if user_input not in ['y', 'yes', '是', '继续']:
                print("❌ 用户取消操作")
                return {}
        else:
            # 强制重新开始，创建所有任务
            pending_tasks = [(model_name, country_name) 
                            for model_name in available_models 
                            for country_name in countries]
            print(f"🔄 强制重新开始，将处理 {len(pending_tasks)} 个任务")
        
        all_results = {}
        results_lock = threading.Lock()
        
        def process_single_country_with_check(model_name: str, country_name: str) -> Tuple[str, str, List[LLMResponse]]:
            """处理单个国家的访谈（带重复检查）"""
            try:
                # 再次检查是否已完成（防止并发重复）
                if not force_restart and self.check_existing_results(model_name, country_name):
                    print(f"⏭️  跳过已完成: {model_name} 模仿 {country_name}")
                    return model_name, country_name, None
                
                print(f"🚀 开始处理: {model_name} 模仿 {country_name}")
                results = self.interview_model_as_country(model_name, country_name)
                
                if results:
                    # 立即保存结果
                    entity_key = f"{model_name}_as_{country_name}"
                    single_result = {entity_key: results}
                    
                    # 修复参数顺序
                    self._save_intermediate_results_optimized_v2(model_name, country_name, single_result)
                    
                    valid_count = sum(1 for r in results if r.is_valid)
                    print(f"✅ 完成并保存: {entity_key} ({valid_count}/{len(results)} 有效)")
                    
                    return model_name, country_name, results
                else:
                    print(f"❌ 失败: {model_name} 模仿 {country_name}")
                    return model_name, country_name, None
                    
            except Exception as e:
                print(f"💥 异常: {model_name} 模仿 {country_name} - {str(e)}")
                return model_name, country_name, None
        
        # 并行执行待处理任务
        completed_count = 0
        failed_count = 0
        
        print(f"\n🔄 开始并行处理 {len(pending_tasks)} 个任务...")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有待处理任务
            future_to_task = {
                executor.submit(process_single_country_with_check, model_name, country_name): (model_name, country_name)
                for model_name, country_name in pending_tasks
            }
            
            # 处理完成的任务
            for future in concurrent.futures.as_completed(future_to_task):
                model_name, country_name = future_to_task[future]
                try:
                    model_name_result, country_name_result, results = future.result()
                    
                    if results:
                        with results_lock:
                            entity_key = f"{model_name_result}_as_{country_name_result}"
                            all_results[entity_key] = results
                            completed_count += 1
                    else:
                        failed_count += 1
                                
                        total_processed = completed_count + failed_count
                        print(f"📊 进度: {total_processed}/{len(pending_tasks)} ({total_processed/len(pending_tasks)*100:.1f}%) | 成功: {completed_count} | 失败: {failed_count}")
                            
                except Exception as exc:
                    failed_count += 1
                    print(f"💥 任务异常: {model_name}_as_{country_name} - {exc}")
        
        # 加载所有现有结果（包括之前完成的）
        print(f"\n📂 加载所有现有结果...")
        final_results = self.load_existing_results(available_models, countries)
        
        print(f"\n🎉 处理完成！")
        print(f"本次新完成: {completed_count} 个任务")
        print(f"本次失败: {failed_count} 个任务")
        print(f"总共加载: {len(final_results)} 个结果")
        
        return final_results
    
    def load_existing_results(self, model_names: List[str], countries: List[str]) -> Dict[str, List[LLMResponse]]:
        """加载所有现有的结果文件"""
        all_results = {}
        
        for model_name in model_names:
            for country_name in countries:
                if self.check_existing_results(model_name, country_name):
                    try:
                        # 尝试加载结果
                        safe_model_name = model_name.replace('/', '_').replace(':', '_').replace('-', '_')
                        
                        # 新格式路径
                        folder_path = os.path.join(
                            os.path.dirname(os.path.dirname(__file__)), 
                            'data', 'llm_responses_roleplay', 
                            f'roleplay_intermediate_{safe_model_name}'
                        )
                        new_format_file = os.path.join(folder_path, f"{model_name}_{country_name}.pkl")
                        
                        # 旧格式路径
                        old_format_file = os.path.join(
                            os.path.dirname(os.path.dirname(__file__)), 
                            'data', 'llm_responses_roleplay', 
                            f'roleplay_intermediate_{model_name}_{country_name}.pkl'
                        )
                        
                        file_to_load = new_format_file if os.path.exists(new_format_file) else old_format_file
                        
                        with open(file_to_load, 'rb') as f:
                            data = pickle.load(f)
                            
                        # 转换为LLMResponse对象
                        for key, responses_data in data.items():
                            if isinstance(responses_data[0], dict):  # 序列化格式
                                responses = [
                                    LLMResponse(
                                        model_name=resp_data['model_name'],
                                        question_id=resp_data['question_id'],
                                        response=resp_data['response'],
                                        raw_response=resp_data['raw_response'],
                                        is_valid=resp_data['is_valid'],
                                        error_message=resp_data.get('error_message')
                                    )
                                    for resp_data in responses_data
                                ]
                            else:  # 已经是LLMResponse对象
                                responses = responses_data
                            
                            all_results[key] = responses
                            
                    except Exception as e:
                        print(f"⚠️  加载 {model_name}_{country_name} 结果失败: {e}")
        
        return all_results
    
# 修改main函数
def main():
    """主函数 - 支持断点续传的角色扮演访谈"""
    print("🚀 开始大模型国家角色扮演访谈（支持断点续传）...")
    
    roleplay_interview = LLMCountryRoleplayInterview(
        repeat_count=1,
        data_path="../data"
    )
    
    # 定义典型国家
    selected_countries_by_region = {
        "African-Islamic": ["Egypt", "Nigeria"],
        "Confucian": ["China", "Japan"],
        "Latin America": ["Brazil", "Mexico"],
        "Protestant Europe": ["Germany", "Sweden"],
        "Catholic Europe": ["France", "Italy"],
        "English-Speaking": ["United States", "United Kingdom"],
        "Orthodox Europe": ["Russian Federation", "Greece"],
        "West & South Asia": ["India", "Turkey"]
    }
    
    selected_countries = []
    for region, countries in selected_countries_by_region.items():
        selected_countries.extend(countries)
        print(f"{region}: {', '.join(countries)}")
    
    available_models = [name for name in roleplay_interview.model_configs.keys() 
                        if name in roleplay_interview.api_keys]
    
    print(f"\n可用模型: {available_models}")
    print(f"选定国家: {selected_countries}")
    
    if not available_models or not selected_countries:
        print("❌ 没有可用的模型或国家数据")
        return
    
    # 询问是否强制重新开始
    force_restart = False
    restart_input = input("\n是否强制重新开始所有任务？(y/n，默认n): ").strip().lower()
    if restart_input in ['y', 'yes', '是']:
        force_restart = True
    
    # 使用支持断点续传的版本
    results = roleplay_interview.batch_country_roleplay_interview_with_resume(
        model_names=available_models[-3:-1],
        countries=selected_countries,
        max_workers=3,  # 可调整并发数
        force_restart=force_restart
    )
    
    if results:
        print(f"\n🎉 最终结果: 共 {len(results)} 个角色扮演数据")
        
        # 按文化区域统计
        print("\n📊 各文化区域结果统计:")
        for region, countries in selected_countries_by_region.items():
            region_results = [r for r in results.keys() if any(country in r for country in countries)]
            print(f"{region}: {len(region_results)} 个结果")
        
        return results
    else:
        print("❌ 没有任何结果")
        return None


if __name__ == "__main__":
    main()