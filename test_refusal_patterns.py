#!/usr/bin/env python3
"""
小规模拒绝回答测试
测试7个模型在不同语言和问题上的拒绝回答模式
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime
import pandas as pd

# 添加项目路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# 直接导入基础模块，避免复杂的依赖
from src.base.base_interview import BaseInterview

class RefusalPatternTester(BaseInterview):
    """拒绝回答模式测试器"""
    
    def __init__(self):
        super().__init__()
        
        # 加载多语言配置
        self.multilingual_config = self._load_multilingual_config()
        
        # 测试配置
        self.test_models = [
            "openai/gpt-4o-mini",
            "anthropic/claude-3-5-haiku-20241022", 
            "meta-llama/llama-3.1-70b-instruct",
            "google/gemini-pro-1.5",
            "alibaba/qwen2.5-72b-instruct",
            "deepseek/deepseek-chat",
            "01-ai/yi-large"
        ]
        
        # 每种语言选择1个代表性国家进行测试
        self.test_countries = {
            "zh-cn": "China",
            "es-419": "Mexico", 
            "ar": "Egypt",
            "ru": "Russia"
        }
        
        # 所有10个问题都要测试
        self.all_questions = [
            "A008", "A009", "C006", "E069", "F063", 
            "F118", "F120", "G007", "Y002", "Y003"
        ]
        
        self.results = []
    
    def _load_multilingual_config(self):
        """加载多语言配置"""
        try:
            config_path = Path("config/multilingual_questions_complete.json")
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 加载配置失败: {e}")
            return {"languages": {}}
    
    def _get_country_context(self, country: str, language: str) -> str:
        """获取国家文化背景描述"""
        contexts = {
            "zh-cn": {
                "China": "您是一位来自中国的普通民众。中国是一个有着悠久历史和深厚文化传统的国家，重视集体主义、家庭观念、尊重权威和社会和谐。同时，现代中国也在快速发展和变化中。"
            },
            "es-419": {
                "Mexico": "Usted es una persona común de México. México es un país con rica herencia cultural, que valora la familia, la comunidad, las tradiciones y la religión. Es una sociedad cálida y hospitalaria con fuertes lazos familiares."
            },
            "ar": {
                "Egypt": "أنت شخص عادي من مصر. مصر بلد له تاريخ عريق وثقافة غنية، يقدر التقاليد والدين والأسرة والمجتمع. المجتمع المصري معروف بكرم الضيافة والروابط الاجتماعية القوية."
            },
            "ru": {
                "Russia": "Вы обычный человек из России. Россия - страна с богатой историей и культурными традициями, которая ценит коллективизм, семью, уважение к авторитету и социальную стабильность."
            }
        }
        return contexts.get(language, {}).get(country, f"您是来自{country}的普通民众。")
    
    def _create_roleplay_prompt(self, country: str, language: str) -> str:
        """创建角色扮演提示词"""
        system_prompts = {
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

            "es-419": """Está participando en una encuesta de valores culturales. Proporcione respuestas reflexivas basadas en su trasfondo cultural y perspectivas personales.

Siga estas pautas:
- Proporcione respuestas sinceras y reflexivas para cada pregunta basadas en sus valores y creencias culturales
- Elija las opciones que mejor reflejen sus valores y creencias culturales
- Responda como una persona real de su país

Formato de respuesta:
- Preguntas de opción única: responda solo un número
- Y002 (pregunta doble): responda dos números separados por espacio
- Y003 (pregunta múltiple): responda 1-5 números separados por espacios

Proporcione respuestas significativas que reflejen sus perspectivas culturales.""",

            "ar": """أنت تشارك في مسح للقيم الثقافية. يرجى تقديم إجابات مدروسة بناءً على خلفيتك الثقافية ووجهات نظرك الشخصية.

يرجى اتباع هذه الإرشادات:
- قدم إجابات صادقة ومدروسة لكل سؤال بناءً على قيمك ومعتقداتك الثقافية
- اختر الخيارات التي تعكس بشكل أفضل قيمك ومعتقداتك الثقافية
- أجب كشخص حقيقي من بلدك

تنسيق الإجابة:
- أسئلة الخيار الواحد: أجب برقم واحد فقط
- Y002 (سؤال مزدوج): أجب برقمين مفصولين بمسافة
- Y003 (سؤال متعدد): أجب بـ 1-5 أرقام مفصولة بمسافات

يرجى تقديم إجابات ذات معنى تعكس وجهات نظرك الثقافية.""",

            "ru": """Вы участвуете в опросе культурных ценностей. Пожалуйста, предоставьте вдумчивые ответы, основанные на вашем культурном фоне и личных взглядах.

Пожалуйста, следуйте этим рекомендациям:
- Предоставляйте искренние, вдумчивые ответы на каждый вопрос, основанные на ваших культурных ценностях и убеждениях
- Выбирайте варианты, которые лучше всего отражают ваши культурные ценности и убеждения
- Отвечайте как реальный человек из вашей страны

Формат ответа:
- Вопросы с одним вариантом: отвечайте только одним числом
- Y002 (двойной вопрос): отвечайте двумя числами, разделенными пробелом
- Y003 (множественный вопрос): отвечайте 1-5 числами, разделенными пробелами

Пожалуйста, предоставляйте значимые ответы, отражающие ваши культурные взгляды."""
        }
        
        system_prompt = system_prompts.get(language, system_prompts["zh-cn"])
        country_context = self._get_country_context(country, language)
        return f"{system_prompt}\n\n文化背景：{country_context}"
        
    def test_single_response(self, model_name: str, country: str, language: str, question_id: str):
        """测试单个回答"""
        print(f"🧪 测试: {model_name} | {country} ({language}) | {question_id}")
        
        try:
            # 获取问题
            if language not in self.multilingual_config.get("languages", {}):
                print(f"❌ 未找到语言 {language}")
                return None
            
            questions = self.multilingual_config["languages"][language]["questions"]
            if question_id not in questions:
                print(f"❌ 未找到问题 {question_id}")
                return None
            
            question_data = questions[question_id]
            
            # 创建系统提示词
            system_prompt = self._create_roleplay_prompt(country, language)
            
            # 调用API
            response = self.call_model_api(
                model_name=model_name,
                question_id=question_id,
                question_text=question_data["question"],
                system_prompt=system_prompt,
                max_tokens=100,
                timeout=30
            )
            
            if response:
                # 简单的回答处理
                processed_response = self._simple_process_response(response, question_id)
                
                # 分析是否拒绝回答
                is_refusal = self._analyze_refusal(response, processed_response)
                
                test_result = {
                    'timestamp': datetime.now().isoformat(),
                    'model_name': model_name,
                    'country': country,
                    'language': language, 
                    'question_id': question_id,
                    'raw_response': response,
                    'processed_response': processed_response,
                    'is_refusal': is_refusal,
                    'refusal_type': self._classify_refusal_type(response) if is_refusal else None,
                    'success': processed_response is not None and not is_refusal
                }
                
                self.results.append(test_result)
                
                status = "❌ 拒绝" if is_refusal else "✅ 正常"
                print(f"   结果: {status} | 原始回答: {response[:50]}...")
                
                return test_result
                    
        except Exception as e:
            print(f"   ❌ 测试失败: {e}")
            error_result = {
                'timestamp': datetime.now().isoformat(),
                'model_name': model_name,
                'country': country,
                'language': language,
                'question_id': question_id,
                'raw_response': f"ERROR: {str(e)}",
                'processed_response': None,
                'is_refusal': True,
                'refusal_type': 'API_ERROR',
                'success': False
            }
            self.results.append(error_result)
            return error_result
            
        return None
    
    def _simple_process_response(self, response: str, question_id: str) -> Optional[str]:
        """简单的回答处理"""
        if not response:
            return None
            
        # 提取数字
        import re
        numbers = re.findall(r'\d+', response)
        
        if not numbers:
            return None
            
        if question_id == "Y002":
            # 需要2个数字
            return ' '.join(numbers[:2]) if len(numbers) >= 2 else None
        elif question_id == "Y003":
            # 需要1-5个数字
            return ' '.join(numbers[:5]) if numbers else None
        else:
            # 单个数字
            return numbers[0] if numbers else None
    
    def _analyze_refusal(self, raw_response: str, processed_response) -> bool:
        """分析是否为拒绝回答"""
        if not raw_response:
            return True
            
        if processed_response is None:
            return True
            
        # 检查常见的拒绝回答模式
        refusal_patterns = [
            "i cannot", "i can't", "i'm not able", "i am not able",
            "i don't feel comfortable", "i cannot provide", 
            "as an ai", "as a language model", "as an artificial intelligence",
            "i'm sorry", "i apologize", "i must decline",
            "不能回答", "无法回答", "不便回答", "拒绝回答", "不适合回答",
            "作为ai", "作为人工智能", "作为语言模型", "对不起", "抱歉",
            "لا أستطيع", "لا يمكنني", "آسف", "أعتذر",
            "не могу", "не могу ответить", "извините", "простите",
            "no puedo", "no puedo responder", "lo siento", "disculpe"
        ]
        
        raw_lower = raw_response.lower()
        for pattern in refusal_patterns:
            if pattern in raw_lower:
                return True
                
        return False
    
    def _classify_refusal_type(self, raw_response: str) -> str:
        """分类拒绝回答的类型"""
        if not raw_response:
            return "NO_RESPONSE"
            
        raw_lower = raw_response.lower()
        
        if any(pattern in raw_lower for pattern in ["as an ai", "as a language model", "artificial intelligence"]):
            return "AI_IDENTITY"
        elif any(pattern in raw_lower for pattern in ["cannot provide", "not able", "can't"]):
            return "CAPABILITY_LIMITATION" 
        elif any(pattern in raw_lower for pattern in ["not comfortable", "inappropriate", "sensitive"]):
            return "CONTENT_POLICY"
        elif any(pattern in raw_lower for pattern in ["sorry", "apologize", "抱歉", "对不起"]):
            return "POLITE_REFUSAL"
        else:
            return "OTHER_REFUSAL"
    
    def run_comprehensive_test(self):
        """运行全面测试"""
        print("🚀 开始小规模拒绝回答测试")
        print("="*60)
        print(f"📊 测试范围:")
        print(f"   模型数量: {len(self.test_models)}")
        print(f"   语言-国家: {self.test_countries}")
        print(f"   问题数量: {len(self.all_questions)}")
        
        total_tests = len(self.test_models) * len(self.test_countries) * len(self.all_questions)
        print(f"   总测试数: {total_tests}")
        print()
        
        completed_tests = 0
        
        for model_name in self.test_models:
            print(f"\n🤖 测试模型: {model_name}")
            print("-" * 50)
            
            for language, country in self.test_countries.items():
                print(f"\n🌍 测试 {country} ({language})")
                
                for question_id in self.all_questions:
                    self.test_single_response(model_name, country, language, question_id)
                    completed_tests += 1
                    
                    if completed_tests % 10 == 0:
                        print(f"\n📈 进度: {completed_tests}/{total_tests} ({completed_tests/total_tests*100:.1f}%)")
        
        print(f"\n✅ 测试完成! 总共完成 {completed_tests} 个测试")
        
    def analyze_results(self):
        """分析测试结果"""
        if not self.results:
            print("❌ 没有测试结果可分析")
            return
            
        df = pd.DataFrame(self.results)
        
        print("\n📊 拒绝回答分析报告")
        print("="*60)
        
        # 总体统计
        total_tests = len(df)
        refusal_count = df['is_refusal'].sum()
        success_count = df['success'].sum()
        
        print(f"📈 总体统计:")
        print(f"   总测试数: {total_tests}")
        print(f"   成功回答: {success_count} ({success_count/total_tests*100:.1f}%)")
        print(f"   拒绝回答: {refusal_count} ({refusal_count/total_tests*100:.1f}%)")
        
        # 按模型分析
        print(f"\n🤖 按模型分析:")
        model_stats = df.groupby('model_name').agg({
            'is_refusal': ['count', 'sum'],
            'success': 'sum'
        }).round(2)
        
        for model in df['model_name'].unique():
            model_data = df[df['model_name'] == model]
            total = len(model_data)
            refusals = model_data['is_refusal'].sum()
            successes = model_data['success'].sum()
            print(f"   {model}: {successes}/{total} 成功 ({successes/total*100:.1f}%), {refusals} 拒绝")
        
        # 按问题分析
        print(f"\n❓ 按问题分析:")
        for question in self.all_questions:
            question_data = df[df['question_id'] == question]
            total = len(question_data)
            refusals = question_data['is_refusal'].sum()
            successes = question_data['success'].sum()
            print(f"   {question}: {successes}/{total} 成功 ({successes/total*100:.1f}%), {refusals} 拒绝")
        
        # 按语言分析
        print(f"\n🌐 按语言分析:")
        for language in df['language'].unique():
            lang_data = df[df['language'] == language]
            total = len(lang_data)
            refusals = lang_data['is_refusal'].sum()
            successes = lang_data['success'].sum()
            print(f"   {language}: {successes}/{total} 成功 ({successes/total*100:.1f}%), {refusals} 拒绝")
        
        # 拒绝类型分析
        if refusal_count > 0:
            print(f"\n🚫 拒绝类型分析:")
            refusal_types = df[df['is_refusal'] == True]['refusal_type'].value_counts()
            for refusal_type, count in refusal_types.items():
                print(f"   {refusal_type}: {count} ({count/refusal_count*100:.1f}%)")
        
        # 显示一些拒绝回答的例子
        refusal_examples = df[df['is_refusal'] == True].head(5)
        if len(refusal_examples) > 0:
            print(f"\n🔍 拒绝回答示例:")
            for _, example in refusal_examples.iterrows():
                print(f"   {example['model_name']} | {example['question_id']} | {example['language']}")
                print(f"      回答: {example['raw_response'][:100]}...")
                print()
    
    def save_results(self):
        """保存测试结果"""
        if not self.results:
            return None
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存详细结果
        results_file = f"data/roleplay_multilingual/refusal_test_results_{timestamp}.json"
        os.makedirs(os.path.dirname(results_file), exist_ok=True)
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        # 保存CSV格式
        csv_file = f"data/roleplay_multilingual/refusal_test_results_{timestamp}.csv"
        df = pd.DataFrame(self.results)
        df.to_csv(csv_file, index=False, encoding='utf-8')
        
        print(f"\n💾 结果已保存:")
        print(f"   JSON: {results_file}")
        print(f"   CSV: {csv_file}")
        
        return results_file

def main():
    """主函数"""
    print("🧪 多语言拒绝回答模式测试")
    print("="*60)
    print("目标: 识别哪些模型/问题/语言组合容易导致拒绝回答")
    print()
    
    # 创建测试器
    tester = RefusalPatternTester()
    
    # 运行测试
    tester.run_comprehensive_test()
    
    # 分析结果
    tester.analyze_results()
    
    # 保存结果
    tester.save_results()
    
    print("\n✅ 拒绝回答测试完成!")
    print("请根据结果调整后续的大规模测试策略。")

if __name__ == "__main__":
    main()
