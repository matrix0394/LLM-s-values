"""
IVS问题特殊处理器
统一处理Y002和Y003等复杂问题的转换逻辑
"""

import re
from typing import Tuple, List, Dict, Any, Optional


class IVSQuestionProcessor:
    """IVS问题统一处理器"""
    
    # Y002物质主义倾向映射
    Y002_MATERIALIST_MAPPING = {
        # (第一选择, 第二选择): 倾向值
        # 1: 维护国家秩序, 2: 民众参与政府决策, 3: 对抗通胀, 4: 保护言论自由
        
        # 物质主义 (Materialist) - 选择1和3
        (1, 3): 1,  # 秩序 + 通胀
        (3, 1): 1,  # 通胀 + 秩序
        
        # 后物质主义 (Postmaterialist) - 选择2和4
        (2, 4): 3,  # 参与 + 自由
        (4, 2): 3,  # 自由 + 参与
        
        # 混合 (Mixed) - 其他组合
        (1, 2): 2, (2, 1): 2,  # 秩序 + 参与
        (1, 4): 2, (4, 1): 2,  # 秩序 + 自由
        (2, 3): 2, (3, 2): 2,  # 参与 + 通胀
        (3, 4): 2, (4, 3): 2,  # 通胀 + 自由
    }
    
    @classmethod
    def process_y002(cls, first_choice: int, second_choice: int) -> int:
        """处理Y002回答，返回物质主义倾向值
        
        Args:
            first_choice: 第一选择 (1-4)
            second_choice: 第二选择 (1-4)
            
        Returns:
            1: 物质主义 (Materialist)
            2: 混合 (Mixed)  
            3: 后物质主义 (Postmaterialist)
        """
        if first_choice < 1 or first_choice > 4 or second_choice < 1 or second_choice > 4:
            return 2  # 默认为混合
            
        return cls.Y002_MATERIALIST_MAPPING.get((first_choice, second_choice), 2)
    
    @classmethod
    def process_y003(cls, selected_values: List[int]) -> Dict[str, Any]:
        """处理Y003回答，返回传统vs世俗理性价值观相关数据
        
        Args:
            selected_values: 选择的价值观列表 (1-11)
            
        Returns:
            包含各种转换结果的字典
        """
        # 将选择转换为布尔列表
        bool_list = [i in selected_values for i in range(1, 12)]
        # 映射True为1，False为2
        scores = [1 if selected else 2 for selected in bool_list]
        
        # 映射到具体的价值观维度
        value_mapping = {
            "q7_good_manners": scores[0],      # 礼貌
            "q8_independence": scores[1],       # 独立性
            "q9_hard_work": scores[2],         # 努力工作
            "q10_responsibility": scores[3],    # 责任感
            "q11_imagination": scores[4],       # 想象力
            "q12_tolerance": scores[5],         # 宽容和尊重
            "q13_thrift": scores[6],           # 节俭
            "q14_determination": scores[7],     # 决心毅力
            "q15_religious_faith": scores[8],   # 宗教信仰
            "q16_unselfishness": scores[9],    # 不自私
            "q17_obedience": scores[10],       # 服从
        }
        
        # 计算传统vs世俗理性价值观分数
        # 传统价值观：宗教信仰(q15) + 服从(q17)
        # 世俗理性价值观：独立性(q8) + 决心毅力(q14)
        traditional_score = value_mapping["q15_religious_faith"] + value_mapping["q17_obedience"]
        secular_rational_score = value_mapping["q8_independence"] + value_mapping["q14_determination"]
        
        # 计算最终的Y003分数 (传统 - 世俗理性)
        y003_score = traditional_score - secular_rational_score
        
        return {
            "selected_values": selected_values,
            "value_mapping": value_mapping,
            "traditional_score": traditional_score,
            "secular_rational_score": secular_rational_score,
            "y003_score": y003_score,
            "binary_encoding": {f"Y003_{i}": (1 if i in selected_values else 0) for i in range(1, 12)}
        }
    
    @classmethod
    def process_single_choice(cls, question_id: str, value: int) -> Dict[str, Any]:
        """处理单选题
        
        Args:
            question_id: 问题ID (如 'A008', 'F063')
            value: 选择值
            
        Returns:
            处理结果字典
        """
        return {
            "question_id": question_id,
            "raw_value": value,
            "processed_value": value,
            "valid": True
        }
    
    @classmethod
    def parse_response_text(cls, response_text: str, question_id: str) -> Optional[str]:
        """统一的响应文本解析方法
        
        Args:
            response_text: 原始响应文本
            question_id: 问题ID
            
        Returns:
            解析后的响应字符串，如果无效则返回None
        """
        if not response_text:
            return None
        
        # 清理回答文本
        response = response_text.strip().lower()
        
        # 提取数字
        numbers = re.findall(r'\d+', response)
        
        if not numbers:
            return None
        
        # 根据问题类型验证回答
        if question_id == "Y002":
            # 双选题，需要2个数字
            if len(numbers) >= 2:
                return f"{numbers[0]} {numbers[1]}"
        elif question_id == "Y003":
            # 多选题，最多5个数字
            if len(numbers) <= 5:
                return " ".join(numbers[:5])
        else:
            # 单选题，只需要1个数字
            return numbers[0]
        
        return None
    
    @classmethod
    def validate_and_process_response(cls, response_text: str, question_id: str) -> Dict[str, Any]:
        """统一的响应验证和处理方法
        
        Args:
            response_text: 原始响应文本
            question_id: 问题ID
            
        Returns:
            包含处理结果的字典
        """
        result = {
            "question_id": question_id,
            "raw_response": response_text,
            "processed_response": None,
            "numeric_value": None,
            "standardized_value": None,
            "valid": False
        }
        
        # 解析响应文本
        processed_response = cls.parse_response_text(response_text, question_id)
        if not processed_response:
            return result
        
        result["processed_response"] = processed_response
        
        try:
            if question_id == "Y002":
                # Y002双选题处理
                values = [int(x.strip()) for x in processed_response.split()]
                if len(values) == 2 and all(1 <= v <= 4 for v in values):
                    result["valid"] = True
                    result["numeric_value"] = values
                    # 标准化为第一个选择的值
                    result["standardized_value"] = (values[0] - 1) / 3
                    # 计算物质主义倾向
                    result["materialist_score"] = cls.process_y002(values[0], values[1])
            
            elif question_id == "Y003":
                # Y003多选题处理
                values = [int(x.strip()) for x in processed_response.split()]
                if 1 <= len(values) <= 5 and all(1 <= v <= 11 for v in values):
                    result["valid"] = True
                    result["numeric_value"] = values
                    # 标准化为选择数量
                    result["standardized_value"] = (len(values) - 1) / 4
                    # 计算详细的Y003分析
                    y003_analysis = cls.process_y003(values)
                    result.update(y003_analysis)
            
            else:
                # 单选题处理
                value = int(processed_response.strip())
                result["valid"] = True
                result["numeric_value"] = value
                result["standardized_value"] = value  # 单选题可能需要根据具体量表标准化
        
        except (ValueError, AttributeError) as e:
            print(f"处理问题 {question_id} 的回答时出错: {e}")
        
        return result
