"""
IVS文化价值观调查核心组件
提供问题定义、回答验证等基础功能
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
    failure_type: Optional[str] = None


class IVSQuestions:
    """IVS文化价值观调查问题定义 - 从配置文件加载"""
    _questions_config: Dict = {}
    _config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'questions', 'ivs_questions.json')

    @classmethod
    def _load_config(cls):
        if not cls._questions_config:
            try:
                with open(cls._config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    cls._questions_config = config.get('ivs_questions', {})
                    print(f"✅ IVSQuestions: 从配置文件加载了 {len(cls._questions_config)} 个问题")
            except FileNotFoundError:
                print(f"❌ IVSQuestions: 配置文件未找到: {cls._config_path}")
            except json.JSONDecodeError as e:
                print(f"❌ IVSQuestions: 配置文件格式错误: {e}")

    @classmethod
    def get_question(cls, question_id: str) -> Dict[str, Any]:
        """获取指定问题及其元数据"""
        cls._load_config()
        return cls._questions_config.get(question_id, {})

    @classmethod
    def get_all_questions(cls) -> Dict[str, Dict[str, Any]]:
        """获取所有问题及其元数据"""
        cls._load_config()
        return cls._questions_config.copy()
    
    @classmethod
    def get_question_ids(cls) -> List[str]:
        """获取所有问题ID列表"""
        cls._load_config()
        return list(cls._questions_config.keys())
    
    @classmethod
    def get_question_text(cls, question_id: str) -> str:
        """获取指定问题的文本"""
        cls._load_config()
        question_data = cls._questions_config.get(question_id, {})
        return question_data.get('question', '')


class ResponseValidator:
    """回答验证器"""
    
    @staticmethod
    def validate_response(question_id: str, response: str) -> tuple[bool, Any, str]:
        """验证回答格式和内容"""
        if not response or not isinstance(response, str):
            return False, None, "回答为空或格式错误"
        
        response = response.strip()
        
        # 获取问题配置
        question_config = IVSQuestions.get_question(question_id)
        if not question_config:
            return False, None, f"未知问题ID: {question_id}"
        
        # 根据问题ID确定验证规则（使用硬编码规则，因为配置文件中没有标准化的类型字段）
        try:
            if question_id in ['A008', 'G006']:
                # 单选题：1-4 (A008: happiness, G006: national pride)
                value = int(response)
                if 1 <= value <= 4:
                    return True, value, ""
                else:
                    return False, None, f"单选题答案必须在1-4之间，得到: {value}"
            
            elif question_id in ['A165']:
                # 单选题：1-2 (A165: trust)
                value = int(response)
                if 1 <= value <= 2:
                    return True, value, ""
                else:
                    return False, None, f"单选题答案必须在1-2之间，得到: {value}"
                    
            elif question_id in ['E018', 'E025']:
                # 单选题：1-3 (E018: authority, E025: petition)
                value = int(response)
                if 1 <= value <= 3:
                    return True, value, ""
                else:
                    return False, None, f"单选题答案必须在1-3之间，得到: {value}"
                    
            elif question_id in ['F063', 'F118', 'F120']:
                # 单选题：1-10 (F063: God, F118: homosexuality, F120: abortion)
                value = int(response)
                if 1 <= value <= 10:
                    return True, value, ""
                else:
                    return False, None, f"单选题答案必须在1-10之间，得到: {value}"
                    
            elif question_id == 'Y002':
                # 双选题：从1-4中选2个 (国家目标：秩序/民主/物价/言论自由)
                parts = response.split()
                if len(parts) != 2:
                    return False, None, f"Y002需要恰好2个选项，得到 {len(parts)} 个"
                
                values = [int(part) for part in parts]
                for value in values:
                    if not (1 <= value <= 4):
                        return False, None, f"Y002选项必须在1-4之间，得到: {value}"
                
                return True, values, ""
                
            elif question_id == 'Y003':
                # 多选题：从1-11中选1-5个
                parts = response.split()
                if len(parts) < 1 or len(parts) > 5:
                    return False, None, f"Y003需要1-5个选项，得到 {len(parts)} 个"
                
                values = [int(part) for part in parts]
                for value in values:
                    if not (1 <= value <= 11):
                        return False, None, f"Y003选项必须在1-11之间，得到: {value}"
                
                return True, values, ""
                
            else:
                return False, None, f"未知问题ID: {question_id}"
                
        except ValueError as e:
            return False, None, f"数字格式错误: {e}"
        except Exception as e:
            return False, None, f"验证过程出错: {e}"