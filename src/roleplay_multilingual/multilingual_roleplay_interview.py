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
from src.llm_values.llm_questionnaire import IVSQuestions, LLMResponse
from src.base.base_interview import BaseInterview
from src.base.ivs_question_processor import IVSQuestionProcessor


class MultilingualRoleplayInterview(BaseInterview):
    """多语言角色扮演访谈类"""
    
    def __init__(self, repeat_count: int = 1, data_path: str = "../data"):
        # 调用父类构造函数
        super().__init__(repeat_count=repeat_count, data_path=data_path)
        
        # 加载多语言特有配置
        self.multilingual_config = self._load_multilingual_config()
        self.countries_data = self._load_countries_data()
        self.cultural_regions = self._load_cultural_regions()
        
        # 多语言系统提示词模板
        self.system_prompts = {
            "zh-cn": """您正在参与一项文化价值观调查。请基于您的文化背景和个人观点提供深思熟虑的回答。

请遵循以下指导原则：
- 根据您的文化价值观和信念，为每个问题提供真诚、经过深思熟虑的回答
- 选择最能反映您文化价值观和信念的选项
- 像来自您国家的真实人士一样回答

回答格式：
- 单选题：仅回答一个数字
- Y002（双选题）：回答两个用空格分隔的数字
- Y003（多选题）：回答1-5个用空格分隔的数字

请提供能反映您文化观点的有意义回答。""",
            
            "ru": """Вы участвуете в опросе о культурных ценностях. Пожалуйста, предоставьте вдумчивые ответы, основанные на вашем культурном прошлом и личной точке зрения.

Пожалуйста, следуйте этим рекомендациям:
- Отвечайте на каждый вопрос искренне и обдуманно
- Выбирайте вариант, который лучше всего отражает ваши культурные ценности и убеждения
- Отвечайте так, как ответил бы реальный человек из вашей страны

Формат ответа:
- Вопросы с одним выбором: отвечайте только одним числом
- Y002 (два выбора): отвечайте двумя числами, разделенными пробелом
- Y003 (множественный выбор): отвечайте 1-5 числами, разделенными пробелами

Пожалуйста, предоставьте содержательные ответы, отражающие вашу культурную точку зрения.""",
            
            "es-la": """Está participando en una encuesta sobre valores culturales. Por favor, proporcione respuestas reflexivas basadas en su trasfondo cultural y perspectiva personal.

Por favor siga estas pautas:
- Responda cada pregunta con una respuesta genuina y considerada
- Elija la opción que mejor refleje sus valores culturales y creencias
- Responda como lo haría una persona real de su país

Formato de respuesta:
- Preguntas de opción única: responda solo con UN número
- Y002 (dos opciones): responda con DOS números separados por espacio
- Y003 (opciones múltiples): responda con 1-5 números separados por espacios

Por favor proporcione respuestas significativas que reflejen su perspectiva cultural.""",
            
            "ar": """أنت تشارك في استطلاع حول القيم الثقافية. يرجى تقديم إجابات مدروسة بناءً على خلفيتك الثقافية ووجهة نظرك الشخصية.

يرجى اتباع هذه الإرشادات:
- أجب على كل سؤال بإجابة صادقة ومدروسة
- اختر الخيار الذي يعكس قيمك الثقافية ومعتقداتك بشكل أفضل
- أجب كما يجيب شخص حقيقي من بلدك

تنسيق الإجابة:
- أسئلة الاختيار الواحد: أجب برقم واحد فقط
- Y002 (خياران): أجب برقمين مفصولين بمسافة
- Y003 (خيارات متعددة): أجب بـ 1-5 أرقام مفصولة بمسافات

يرجى تقديم إجابات ذات معنى تعكس وجهة نظرك الثقافية."""
        }
    
    
    def _load_multilingual_config(self) -> Dict:
        """加载多语言配置"""
        # 尝试多个可能的路径
        possible_paths = [
            Path("../config/multilingual_questions_complete.json"),
            Path("config/multilingual_questions_complete.json"),
            Path("../../config/multilingual_questions_complete.json")
        ]
        
        for config_path in possible_paths:
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        
        print(f"警告: 未找到多语言配置文件，尝试过的路径: {[str(p) for p in possible_paths]}")
        return {}
    
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
    
    def _get_country_context(self, country: str, language: str) -> str:
        """获取国家文化背景描述"""
        # 根据语言返回不同的文化背景描述
        contexts = {
            "zh-cn": {
                "China": "您是一位来自中国的普通民众。中国是一个有着悠久历史和深厚文化传统的国家，重视集体主义、家庭观念、尊重权威和社会和谐。同时，现代中国也在快速发展和变化中。"
            },
            "ru": {
                "Russian Federation": "Вы обычный гражданин России. Россия - это страна с богатой историей и культурными традициями, которая ценит коллективизм, семейные ценности, уважение к власти и социальную стабильность."
            },
            "es-la": {
                "Mexico": "Usted es un ciudadano común de México. México es un país con rica historia y tradiciones culturales, que valora la familia, la comunidad, el respeto y las tradiciones religiosas.",
                "Argentina": "Usted es un ciudadano común de Argentina. Argentina es un país con fuerte identidad cultural, que valora la familia, la educación, el orgullo nacional y las tradiciones europeas.",
                "Colombia": "Usted es un ciudadano común de Colombia. Colombia es un país diverso con rica cultura, que valora la familia, la hospitalidad, las tradiciones religiosas y la comunidad."
            },
            "ar": {
                "Egypt": "أنت مواطن عادي من مصر. مصر بلد له تاريخ عريق وتقاليد ثقافية غنية، يقدر الأسرة والمجتمع والتقاليد الدينية والاحترام للسلطة.",
                "Jordan": "أنت مواطن عادي من الأردن. الأردن بلد يقدر التقاليد العربية والإسلامية، والأسرة، والضيافة، والاستقرار الاجتماعي.",
                "Morocco": "أنت مواطن عادي من المغرب. المغرب بلد له تراث ثقافي غني يجمع بين التقاليد العربية والأمازيغية والإسلامية، ويقدر الأسرة والمجتمع."
            }
        }
        
        return contexts.get(language, {}).get(country, f"您是来自{country}的普通民众。")
    
    def _create_roleplay_prompt(self, country: str, language: str) -> str:
        """创建角色扮演提示词"""
        system_prompt = self.system_prompts.get(language, self.system_prompts["zh-cn"])
        country_context = self._get_country_context(country, language)
        
        return f"{system_prompt}\n\n文化背景：{country_context}"
    
    
    
    
    def interview_country_multilingual(self, model_name: str, country: str, language: str) -> Dict[str, Any]:
        """对特定国家进行多语言访谈"""
        print(f"\n🎭 开始访谈: {model_name} 模拟 {country} ({language})")
        print("=" * 60)
        
        # 获取该语言的问题
        questions = self.multilingual_config["languages"][language]["questions"]
        
        # 创建角色扮演提示词
        system_prompt = self._create_roleplay_prompt(country, language)
        
        responses = []
        valid_responses = 0
        
        for question_id, question_data in questions.items():
            try:
                # 构建消息
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question_data["question"]}
                ]
                
                # 调用API - 使用基类方法
                response_text = self.call_model_api(
                    model_name, 
                    question_id,
                    question_data["question"],
                    system_prompt=system_prompt,
                    max_tokens=100, 
                    timeout=30
                )
                
                # 打印详细的问答过程 //by=>friday
                print(f"  📝 问题 {question_id}: {question_data['question'][:50]}...")
                
                if response_text:
                    # 处理和验证回答
                    processed_response = self._process_response(response_text, question_id)
                    
                    # 打印模型回答详情 //by=>friday
                    print(f"  🤖 原始回答: '{response_text.strip()}'")
                    print(f"  ✅ 处理后: '{processed_response}'" if processed_response else "  ❌ 处理失败")
                    
                    if processed_response:
                        valid_responses += 1
                    
                    responses.append({
                        "question_id": question_id,
                        "question": question_data["question"],
                        "raw_response": response_text,
                        "processed_response": processed_response,
                        "scale": question_data["scale"],
                        "dimension": question_data["dimension"]
                    })
                else:
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
                    time.sleep(0.3)  # 较快的模型
                else:
                    time.sleep(0.5)  # 其他模型保持现有延迟
                
            except Exception as e:
                print(f"问题 {question_id} 处理失败: {e}")
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
        
        # 打印访谈总结 //by=>friday
        print(f"\n📊 访谈总结:")
        print(f"  🎯 模型: {model_name}")
        print(f"  🌍 国家: {country}")
        print(f"  🗣️ 语言: {language}")
        print(f"  ✅ 成功率: {result['success_rate']:.1f}% ({valid_responses}/{len(questions)})")
        print("=" * 60)
        return result
    
    def _process_response(self, response_text: str, question_id: str) -> Optional[str]:
        """处理和验证回答 - 使用统一的处理器"""
        return IVSQuestionProcessor.parse_response_text(response_text, question_id)
    
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
    
    def run_multilingual_experiment(self, models: List[str] = None, max_workers: int = 4, repeat_count: int = 1, test_type: str = "standard") -> Dict[str, Any]:
        """运行多语言实验"""
        if models is None:
            # 从配置文件加载所有可用模型
            models = self._load_all_available_models()
            print(f"🤖 使用所有可用模型: {len(models)} 个")
            for model in models:
                print(f"   - {model}")
        else:
            print(f"🤖 使用指定模型: {len(models)} 个")
        
        # 准备实验任务
        tasks = []
        for language, config in self.multilingual_config["languages"].items():
            for country in config["countries"]:
                for model in models:
                    tasks.append((model, country, language))
        
        print(f"准备运行 {len(tasks)} 个多语言访谈任务")
        
        results = []
        completed = 0
        
        def run_single_interview(task):
            model, country, language = task
            try:
                result = self.interview_country_multilingual(model, country, language)
                return result
            except Exception as e:
                print(f"任务失败: {model} - {country} ({language}): {e}")
                return None
        
        # 使用线程池并发执行
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_task = {executor.submit(run_single_interview, task): task for task in tasks}
            
            for future in concurrent.futures.as_completed(future_to_task):
                result = future.result()
                if result:
                    results.append(result)
                completed += 1
                print(f"进度: {completed}/{len(tasks)} ({completed/len(tasks)*100:.1f}%)")
        
        # 保存结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 转换为run脚本期望的格式: {country: {language: {model: [responses...]}}}
        formatted_data = {}
        for result in results:
            if not result:
                continue
                
            country = result.get('country')
            language = result.get('language')
            model = result.get('model')
            
            if not all([country, language, model]):
                continue
            
            # 初始化嵌套结构
            if country not in formatted_data:
                formatted_data[country] = {}
            if language not in formatted_data[country]:
                formatted_data[country][language] = {}
            if model not in formatted_data[country][language]:
                formatted_data[country][language][model] = []
            
            # 添加结果
            formatted_data[country][language][model].append(result)
        
        # 保存到文件 - 使用绝对路径确保正确保存
        project_root = Path(__file__).parent.parent.parent  # 从src/roleplay_multilingual/回到项目根目录
        output_dir = project_root / "data" / "roleplay_multilingual"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # JSON格式 - 使用test_type区分不同测试的文件
        json_file = output_dir / f"interview_data_{test_type}_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(formatted_data, f, ensure_ascii=False, indent=2)
        
        # PKL格式
        pkl_file = output_dir / f"interview_data_{test_type}_{timestamp}.pkl"
        with open(pkl_file, 'wb') as f:
            pickle.dump(formatted_data, f)
        
        print(f"结果已保存到:")
        print(f"  JSON: {json_file}")
        print(f"  PKL: {pkl_file}")
        
        return formatted_data
    
    def interview_entity(self, model_name: str, entity_id: str) -> List[LLMResponse]:
        """访谈单个实体 - 多语言实现"""
        # 对于多语言访谈，entity_id格式为 "country_language"
        if '_' in entity_id:
            country, language = entity_id.split('_', 1)
        else:
            # 默认使用中文
            country, language = entity_id, 'zh-cn'
        
        # 进行多语言访谈
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
        
        return responses
    
    def batch_interview(self, model_names: List[str], entities: List[str]) -> Dict[str, Any]:
        """批量访谈 - 多语言实现"""
        # 使用现有的run_multilingual_experiment方法
        return self.run_multilingual_experiment(models=model_names, max_workers=4)


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
