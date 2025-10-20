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
    
    
    
    
    def interview_country_multilingual_with_repeats(self, model_name: str, country: str, language: str) -> Dict[str, Any]:
        """对特定国家进行多语言访谈（整个问卷重复N次，最后取众数）"""
        print(f"\n" + "="*80)
        print(f"🎭 开始重复访谈任务")
        print(f"="*80)
        print(f"📋 配置:")
        print(f"   • 模型: {model_name}")
        print(f"   • 国家: {country}")
        print(f"   • 语言: {language}")
        print(f"   • 重复次数: {self.repeat_count}")
        print(f"   • 问题数: 10")
        print("="*80)
        
        # 存储每一轮的完整访谈结果
        all_rounds = []
        
        # 重复进行N次完整问卷访谈
        for round_idx in range(self.repeat_count):
            print(f"\n┌{'─'*78}┐")
            print(f"│ 🔄 第 {round_idx + 1}/{self.repeat_count} 轮完整问卷访谈" + " " * (78 - 20 - len(f"{round_idx + 1}/{self.repeat_count}")) + "│")
            print(f"└{'─'*78}┘")
            
            # 进行一次完整的问卷访谈
            round_result = self.interview_country_multilingual(model_name, country, language)
            round_result['round_id'] = round_idx + 1
            all_rounds.append(round_result)
            
            print(f"✅ 第 {round_idx + 1} 轮完成 - 成功率: {round_result['success_rate']:.0f}%")
            
            # 轮次间短暂延迟
            if round_idx < self.repeat_count - 1:
                time.sleep(0.5)
        
        # 计算每个问题的众数
        print(f"\n{'='*80}")
        print(f"📊 计算众数 - 汇总 {self.repeat_count} 轮回答")
        print(f"{'='*80}")
        
        final_responses = self._aggregate_repeated_interviews(all_rounds)
        
        # 构建最终结果
        result = {
            "model": model_name,
            "country": country,
            "language": language,
            "timestamp": datetime.now().isoformat(),
            "repeat_count": self.repeat_count,
            "total_questions": len(final_responses),
            "responses": final_responses,
            "all_rounds": all_rounds,  # 保存所有轮次的完整数据
        }
        
        # 计算总体统计
        valid_count = sum(1 for r in final_responses if r['final_response'] is not None)
        avg_confidence = sum(r['confidence'] for r in final_responses) / len(final_responses) if final_responses else 0
        
        result['valid_responses'] = valid_count
        result['success_rate'] = valid_count / len(final_responses) * 100 if final_responses else 0
        result['average_confidence'] = avg_confidence
        
        # 打印最终总结
        print(f"\n{'='*80}")
        print(f"✅ 重复访谈完成")
        print(f"{'='*80}")
        print(f"📋 结果汇总:")
        print(f"   🎯 模型: {model_name}")
        print(f"   🌍 国家: {country}")
        print(f"   🗣️ 语言: {language}")
        print(f"   🔄 完成轮次: {self.repeat_count}")
        print(f"   ✅ 最终成功率: {result['success_rate']:.1f}% ({valid_count}/{len(final_responses)})")
        print(f"   📊 平均置信度: {avg_confidence*100:.1f}%")
        
        # 显示置信度分布
        high_conf = sum(1 for r in final_responses if r['confidence'] >= 0.8)
        med_conf = sum(1 for r in final_responses if 0.6 <= r['confidence'] < 0.8)
        low_conf = sum(1 for r in final_responses if r['confidence'] < 0.6)
        print(f"\n   置信度分布:")
        print(f"     • 高 (≥80%): {high_conf} 个问题")
        print(f"     • 中 (60-80%): {med_conf} 个问题")
        print(f"     • 低 (<60%): {low_conf} 个问题")
        print("=" * 80)
        
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
        
        for question_id, question_data in questions.items():
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
                
                print(f"  📝 {question_id}: ", end='')
                
                if response_text:
                    processed_response = self._process_response(response_text, question_id)
                    print(f"'{response_text.strip()}' → '{processed_response}'")
                    
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
                    print(f"❌ 无回答")
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
                # 如果repeat_count > 1，使用重复访谈方法
                if self.repeat_count > 1:
                    result = self.interview_country_multilingual_with_repeats(model, country, language)
                else:
                    result = self.interview_country_multilingual(model, country, language)
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
                    task = future_to_task[future]
                    model, country, language = task
                    print(f"\n{'🟢' if result else '🔴'} 进度: [{completed}/{len(tasks)}] ({completed/len(tasks)*100:.1f}%) - {model}/{country}/{language}")
        
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
