"""
LLM分析模块
提供大模型访谈、问题管理、回答验证等核心功能
"""

# 导出核心类，简化外部导入
from .llm_questionnaire import LLMResponse, IVSQuestions, ResponseValidator
# 注意：LLMInterview 因为依赖base模块，请直接导入避免循环依赖
# from .llm_interview import LLMInterview

__all__ = [
    'LLMResponse',
    'IVSQuestions', 
    'ResponseValidator',
    # 'LLMInterview'  # 请直接从 src.llm_analysis.llm_interview 导入
]
