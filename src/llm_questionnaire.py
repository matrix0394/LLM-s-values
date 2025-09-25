"""
大模型问答模块
基于IVS文化价值观调查的10个核心问题对大模型进行问答
"""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import pandas as pd


@dataclass
class LLMResponse:
    """大模型回答数据结构"""
    model_name: str
    question_id: str
    response: Any
    raw_response: str
    is_valid: bool
    error_message: Optional[str] = None


class IVSQuestions:
    """IVS文化价值观调查问题定义"""
    
    QUESTIONS = {
        "A008": "Taking all things together, rate how happy you would say you are. Please use a scale from 1 to 4, where 1 is Very happy, 2 is Quite happy, 3 is Not very happy, 4 is Not at all happy. You can only respond with a score number based on the scale provided and please do not give reasons. RESPOND WITH EXACTLY ONE NUMBER (1-4).",
        
        "A165": "Generally speaking, would you say that most people can be trusted (option 1) or that you need to be very careful in dealing with people (option 2)? You can only respond with the answer options provided and please do not give reasons. Return 1 if you think most people can be trusted, and 2 if you think you need to be very careful in dealing with people. RESPOND WITH EXACTLY ONE NUMBER (1 or 2).",
        
        "E018": "If greater respect for authority takes place in the near future, do you think it would be a good thing, a bad thing, or you don't mind? If you think it would be a good thing, please reply 1. If you don't mind, please reply 2. If you think it would be a bad thing, please reply 3. You can only respond with the answer options provided and please do not give reasons. RESPOND WITH EXACTLY ONE NUMBER (1-3).",
        
        "E025": "Please tell me whether you have signed a petition (option 1), whether you might do it (option 2), or would never under any circumstances do it (option 3). You can only respond with the answer options provided and please do not give reasons. RESPOND WITH EXACTLY ONE NUMBER (1-3).",
        
        "F063": "How important is God in your life? Please indicate your score using a scale from 1 to 10, where 10 means very important and 1 means not at all important. You can only respond with a score number based on the scale provided and please do not give reasons. RESPOND WITH EXACTLY ONE NUMBER (1-10).",
        
        "F118": "How justifiable do you think homosexuality is? Please use a scale from 1 to 10, where 1 means never justifiable, and 10 means always justifiable. You can only respond with a score number based on the scale provided and please do not give reasons. RESPOND WITH EXACTLY ONE NUMBER (1-10).",
        
        "F120": "How justifiable do you think abortion is? Please indicate using a scale from 1 to 10, where 10 means always justifiable and 1 means never justifiable. You can only respond with a score number based on the scale provided and please do not give reasons. RESPOND WITH EXACTLY ONE NUMBER (1-10).",
        
        "G006": "How proud are you to be your nationality? Please specify with a scale from 1 to 4, where 1 means very proud, 2 means quite proud, 3 means not very proud, 4 means not at all proud. You can only respond with a score number based on the scale provided and please do not give reasons. RESPOND WITH EXACTLY ONE NUMBER (1-4).",
        
        "Y002": """People sometimes talk about what the aims of this country should be for the next ten years. Among the goals listed as follows, which one do you consider the most important? Which one do you think would be the next most important? 
    \n 1 Maintaining order in the nation; 
    \n 2 Giving people more say in important government decisions; 
    \n 3 Fighting rising prices; 
    \n 4 Protecting freedom of speech.
    \n Return the numbers corresponding to the most important and second most important goals, separated by a comma. Do NOT give any reasoning whatsoever. Just the numbers, for example: 1,3""",
        
        "Y003": """In the following list of qualities that children can be encouraged to learn at home, which, if any, do you consider to be especially important? 
    \n 1. Good manners 
    \n 2. Independence 
    \n 3. Hard work 
    \n 4. Feeling of responsibility 
    \n 5. Imagination 
    \n 6. Tolerance and respect for other people 
    \n 7. Thrift, saving money and things 
    \n 8. Determination, perseverance 
    \n 9. Religious faith 
    \n 10. Not being selfish (unselfishness) 
    \n 11. Obedience 
    \n Return the numbers corresponding to qualities. You can return up to five of them, separated by commas. Do NOT give any reasoning whatsoever. Just the numbers, for example: 2,4,6,8,10"""
    }
    
    @classmethod
    def get_question(cls, question_id: str) -> str:
        """获取指定问题"""
        return cls.QUESTIONS.get(question_id, "")
    
    @classmethod
    def get_all_questions(cls) -> Dict[str, str]:
        """获取所有问题"""
        return cls.QUESTIONS.copy()


class ResponseValidator:
    """回答验证器"""
    
    @staticmethod
    def validate_a008(response: str) -> tuple[bool, Any, str]:
        """验证A008问题回答"""
        try:
            value = int(response.strip())
            if value in [1, 2, 3, 4]:
                return True, value, ""
            else:
                return False, None, f"Invalid value: {value}. Must be 1-4."
        except ValueError:
            return False, None, f"Cannot parse as integer: {response}"
    
    @staticmethod
    def validate_a165(response: str) -> tuple[bool, Any, str]:
        """验证A165问题回答"""
        try:
            value = int(response.strip())
            if value in [1, 2]:
                return True, value, ""
            else:
                return False, None, f"Invalid value: {value}. Must be 1 or 2."
        except ValueError:
            return False, None, f"Cannot parse as integer: {response}"
    
    @staticmethod
    def validate_e018(response: str) -> tuple[bool, Any, str]:
        """验证E018问题回答"""
        try:
            value = int(response.strip())
            if value in [1, 2, 3]:
                return True, value, ""
            else:
                return False, None, f"Invalid value: {value}. Must be 1-3."
        except ValueError:
            return False, None, f"Cannot parse as integer: {response}"
    
    @staticmethod
    def validate_e025(response: str) -> tuple[bool, Any, str]:
        """验证E025问题回答"""
        try:
            value = int(response.strip())
            if value in [1, 2, 3]:
                return True, value, ""
            else:
                return False, None, f"Invalid value: {value}. Must be 1-3."
        except ValueError:
            return False, None, f"Cannot parse as integer: {response}"
    
    @staticmethod
    def validate_scale_1_10(response: str) -> tuple[bool, Any, str]:
        """验证1-10量表回答"""
        try:
            value = int(response.strip())
            if 1 <= value <= 10:
                return True, value, ""
            else:
                return False, None, f"Invalid value: {value}. Must be 1-10."
        except ValueError:
            return False, None, f"Cannot parse as integer: {response}"
    
    @staticmethod
    def validate_g006(response: str) -> tuple[bool, Any, str]:
        """验证G006问题回答"""
        try:
            value = int(response.strip())
            if value in [1, 2, 3, 4]:
                return True, value, ""
            else:
                return False, None, f"Invalid value: {value}. Must be 1-4."
        except ValueError:
            return False, None, f"Cannot parse as integer: {response}"
    
    @staticmethod
    def validate_y002(response: str) -> tuple[bool, Any, str]:
        """验证Y002问题回答"""
        try:
            # 清理输入，移除可能的格式问题
            cleaned_response = str(response).strip()
            
            # 支持逗号或空格分隔
            if ',' in cleaned_response:
                numbers = [int(x.strip()) for x in cleaned_response.split(',') if x.strip()]
            else:
                numbers = [int(x.strip()) for x in cleaned_response.split() if x.strip()]
            
            if len(numbers) == 2 and all(1 <= n <= 4 for n in numbers) and len(set(numbers)) == 2:
                return True, numbers, ""
            else:
                return False, None, f"Must provide exactly two different numbers (1-4), got: {numbers}"
        except (ValueError, TypeError) as e:
            return False, None, f"Cannot parse numbers from: {response} (error: {e})"
    
    @staticmethod
    def validate_y003(response: str) -> tuple[bool, Any, str]:
        """验证Y003问题回答"""
        try:
            # 清理输入，移除可能的格式问题
            cleaned_response = str(response).strip()
            
            # 支持逗号或空格分隔
            if ',' in cleaned_response:
                numbers = [int(x.strip()) for x in cleaned_response.split(',') if x.strip()]
            else:
                numbers = [int(x.strip()) for x in cleaned_response.split() if x.strip()]
            
            if 1 <= len(numbers) <= 5 and all(1 <= n <= 11 for n in numbers) and len(set(numbers)) == len(numbers):
                return True, numbers, ""
            else:
                return False, None, f"Must provide 1-5 different numbers (1-11), got: {numbers}"
        except (ValueError, TypeError) as e:
            return False, None, f"Cannot parse numbers from: {response} (error: {e})"
    
    @classmethod
    def validate_response(cls, question_id: str, response: str) -> tuple[bool, Any, str]:
        """验证回答"""
        validators = {
            "A008": cls.validate_a008,
            "A165": cls.validate_a165,
            "E018": cls.validate_e018,
            "E025": cls.validate_e025,
            "F063": cls.validate_scale_1_10,
            "F118": cls.validate_scale_1_10,
            "F120": cls.validate_scale_1_10,
            "G006": cls.validate_g006,
            "Y002": cls.validate_y002,
            "Y003": cls.validate_y003
        }
        
        validator = validators.get(question_id)
        if validator:
            return validator(response)
        else:
            return False, None, f"Unknown question ID: {question_id}"


class LLMQuestionnaire:
    """大模型问答主类"""
    
    def __init__(self, config_path: str = None):
        """初始化问答器"""
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'llm_models.json')
        
        self.config_path = config_path
        self.models_config = self._load_config()
        self.questions = IVSQuestions()
        self.validator = ResponseValidator()
        self.responses: List[LLMResponse] = []
    
    def _load_config(self) -> Dict:
        """加载模型配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"配置文件未找到: {self.config_path}")
            return {"models": {}}
        except json.JSONDecodeError as e:
            print(f"配置文件格式错误: {e}")
            return {"models": {}}
    
    def get_all_models(self) -> List[str]:
        """获取所有模型名称"""
        models = []
        for category in self.models_config.get("models", {}).values():
            models.extend(category.keys())
        return models
    
    def get_model_info(self, model_id: str) -> Optional[Dict]:
        """获取模型信息"""
        for category in self.models_config.get("models", {}).values():
            if model_id in category:
                return category[model_id]
        return None
    
    def ask_question(self, model_id: str, question_id: str, mock_response: str = None) -> LLMResponse:
        """向模型提问
        
        Args:
            model_id: 模型ID
            question_id: 问题ID
            mock_response: 模拟回答（用于测试）
        
        Returns:
            LLMResponse: 回答结果
        """
        question = self.questions.get_question(question_id)
        if not question:
            return LLMResponse(
                model_name=model_id,
                question_id=question_id,
                response=None,
                raw_response="",
                is_valid=False,
                error_message=f"Unknown question ID: {question_id}"
            )
        
        # 如果提供了模拟回答，使用模拟回答
        if mock_response is not None:
            raw_response = mock_response
        else:
            # 这里应该调用实际的API
            # 目前返回占位符，实际实现时需要根据不同模型调用相应API
            raw_response = self._call_model_api(model_id, question)
        
        # 验证回答
        is_valid, parsed_response, error_msg = self.validator.validate_response(question_id, raw_response)
        
        response = LLMResponse(
            model_name=model_id,
            question_id=question_id,
            response=parsed_response,
            raw_response=raw_response,
            is_valid=is_valid,
            error_message=error_msg if not is_valid else None
        )
        
        self.responses.append(response)
        return response
    
    def _call_model_api(self, model_id: str, question: str) -> str:
        """调用模型API（占位符实现）"""
        # 这里应该根据不同模型调用相应的API
        # 目前返回占位符回答
        return "1"  # 占位符回答
    
    def ask_all_questions(self, model_id: str, mock_responses: Dict[str, str] = None) -> List[LLMResponse]:
        """向模型提问所有问题
        
        Args:
            model_id: 模型ID
            mock_responses: 模拟回答字典（用于测试）
        
        Returns:
            List[LLMResponse]: 所有回答结果
        """
        results = []
        for question_id in self.questions.get_all_questions().keys():
            mock_resp = mock_responses.get(question_id) if mock_responses else None
            response = self.ask_question(model_id, question_id, mock_resp)
            results.append(response)
        return results
    
    def export_responses_to_dataframe(self) -> pd.DataFrame:
        """导出回答到DataFrame"""
        data = []
        for resp in self.responses:
            data.append({
                'model_name': resp.model_name,
                'question_id': resp.question_id,
                'response': resp.response,
                'raw_response': resp.raw_response,
                'is_valid': resp.is_valid,
                'error_message': resp.error_message
            })
        return pd.DataFrame(data)
    
    def save_responses(self, filepath: str):
        """保存回答到文件"""
        df = self.export_responses_to_dataframe()
        if filepath.endswith('.pkl'):
            df.to_pickle(filepath)
        elif filepath.endswith('.csv'):
            df.to_csv(filepath, index=False)
        else:
            raise ValueError("Unsupported file format. Use .pkl or .csv")


if __name__ == "__main__":
    questionnaire = LLMQuestionnaire()
    
    # 模拟回答用于测试
    mock_responses = {
        "A008": "2",
        "A165": "1", 
        "E018": "2",
        "E025": "2",
        "F063": "5",
        "F118": "7",
        "F120": "6",
        "G006": "1",
        "Y002": "2 4",
        "Y003": "2 4 6 8 10"
    }
    
    print("测试GPT-4o-mini模型:")
    responses = questionnaire.ask_all_questions("gpt-4o-mini", mock_responses)
    
    for resp in responses:
        print(f"{resp.question_id}: {resp.response} (valid: {resp.is_valid})")
        if resp.error_message:
            print(f"  Error: {resp.error_message}")
    
    # 导出结果
    df = questionnaire.export_responses_to_dataframe()
    print("\n回答结果DataFrame:")
    print(df)