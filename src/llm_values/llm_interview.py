"""
新的LLM访谈类 - 基于BaseInterview
替换原有的复杂LLMInterview类
"""

import sys
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.base.base_interview import BaseInterview
from src.llm_values.llm_questionnaire import LLMResponse


class LLMInterview(BaseInterview):
    """LLM访谈类 - 继承基类，专注于基础LLM访谈"""
    
    def __init__(self, repeat_count: int = 5):
        """
        Args:
            repeat_count: 每个完整问卷的重复次数（用于取众数），默认5次
        """
        super().__init__(repeat_count=1)  # 基类的重试次数固定为1，避免混淆
        self.consensus_count = repeat_count  # 用于取众数的重复次数
        
        # IVS问题列表
        self.iv_qns = ["A008", "A165", "E018", "E025", "F063", "F118", "F120", "G006", "Y002", "Y003"]
        
        # LLM访谈的专用系统提示词 - 强制性、技术导向
        self.system_prompt = """CRITICAL: You are a survey response system. Your ONLY task is to output numbers.

STRICT OUTPUT FORMAT:
1. Single choice: ONE number only
2. Two choices (Y002): TWO numbers with ONE space
3. Multiple choice (Y003): 1-5 numbers with spaces

ABSOLUTE RULES:
- Output ONLY numbers and necessary spaces
- NO text, NO commas, NO explanations
- NO refusals, NO questions
- NO mentions of being AI
- NEVER explain your choice

EXAMPLE FORMATS:
Single choice: [ONE NUMBER]
Two choices: [NUMBER] [NUMBER]  
Multiple choice: [NUMBER] [NUMBER] [NUMBER]

REMEMBER: Numbers ONLY. Any other output = FAILURE."""
    
    def _calculate_consensus(self, responses: List[LLMResponse], question_id: str) -> LLMResponse:
        """计算多个回答的众数"""
        from collections import Counter
        
        # 提取有效回答
        valid_responses = [r.response for r in responses if r.is_valid and r.response is not None]
        
        if not valid_responses:
            # 如果所有尝试都失败，返回带有错误信息的无效响应
            print(f"  ⚠️ {question_id}: 所有{len(responses)}次尝试都失败")
            return responses[0]  # 返回第一个回答（即使无效）
        
        # 根据问题类型处理众数计算
        if question_id in ['Y002', 'Y003']:
            # 对于复杂问题，将回答转换为字符串进行比较
            response_strings = [str(resp) for resp in valid_responses]
            most_common_str, count = Counter(response_strings).most_common(1)[0]
            
            # 找到对应的原始回答
            consensus_value = None
            for i, resp_str in enumerate(response_strings):
                if resp_str == most_common_str:
                    consensus_value = valid_responses[i]
                    break
        else:
            # 对于单选题，直接计算众数
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
    
    def _multi_round_interview(self, model_name: str) -> List[LLMResponse]:
        """多轮访谈取众数"""
        print(f"🔄 进行 {self.consensus_count} 轮完整问卷访谈（取众数）...")
        
        question_ids = list(self.questions.get_all_questions().keys())
        all_rounds_responses = []  # 存储所有轮次的回答
        
        # 进行多轮完整访谈
        for round_num in range(self.consensus_count):
            print(f"\n📋 第 {round_num + 1}/{self.consensus_count} 轮访谈:")
            round_responses = []
            
            for i, question_id in enumerate(question_ids, 1):
                print(f"  问题 {i}/{len(question_ids)}: {question_id}", end=" ")
                
                response = self.ask_question_with_retry(model_name, question_id, self.system_prompt)
                
                if response.raw_response is None:
                    print(f"❌ API失败，使用None占位")
                    # 不要直接返回空，而是记录失败但继续
                    # 如果所有轮次都失败才放弃整个模型
                
                if response.is_valid:
                    print(f"✅ {response.response}")
                else:
                    print(f"⚠️ 无效: {response.raw_response}")
                
                round_responses.append(response)
                
                # 问题间延迟
                import time
                time.sleep(self._get_dynamic_delay(model_name))
            
            all_rounds_responses.append(round_responses)
            
            # 轮次间稍长延迟
            if round_num < self.consensus_count - 1:
                print(f"  ⏳ 第{round_num + 1}轮完成，休息片刻...")
                import time
                time.sleep(self._get_dynamic_delay(model_name) * 2)
        
        # 计算每个问题的众数
        print(f"\n🧮 计算 {len(question_ids)} 个问题的众数...")
        consensus_results = []
        
        for i, question_id in enumerate(question_ids):
            # 收集该问题在所有轮次中的回答
            question_responses = [round_resp[i] for round_resp in all_rounds_responses]
            
            # 计算众数
            consensus_response = self._calculate_consensus(question_responses, question_id)
            consensus_results.append(consensus_response)
            
            valid_count = len([r for r in question_responses if r.is_valid])
            print(f"  {question_id}: {consensus_response.response} (来自{valid_count}个有效回答)")
        
        return consensus_results
    
    def interview_entity(self, model_name: str, entity_id: str = None) -> List[LLMResponse]:
        """访谈单个模型"""
        print(f"\n=== 访谈模型: {model_name} ===")
        
        if model_name not in self.api_keys:
            print(f"跳过模型 {model_name}: API密钥未设置")
            return []
        
        # 根据 consensus_count 决定是单轮还是多轮访谈
        if self.consensus_count > 1:
            print(f"采用多轮访谈模式：{self.consensus_count} 轮完整问卷，每个问题取众数")
            return self._multi_round_interview(model_name)
        else:
            # 单轮访谈模式
            print(f"采用单轮访谈模式")
            results = []
            question_ids = list(self.questions.get_all_questions().keys())
            
            for i, question_id in enumerate(question_ids, 1):
                print(f"  问题 {i}/{len(question_ids)}: {question_id}")
                
                # 使用基类的统一方法，传入LLM专用的系统提示词
                response = self.ask_question_with_retry(model_name, question_id, self.system_prompt)
                
                if response.raw_response is None:
                    print(f"  跳过模型 {model_name}（API调用失败）")
                    return []
                
                if response.is_valid:
                    print(f"    最终回答: {response.raw_response} -> {response.response}")
                else:
                    print(f"    无效回答: {response.raw_response} ({response.error_message})")
                
                results.append(response)
                
                # 使用基类的动态延迟
                import time
                time.sleep(self._get_dynamic_delay(model_name))
            
            return results
    
    def batch_interview(self, model_names: List[str] = None) -> Dict[str, Any]:
        """批量访谈多个模型"""
        if model_names is None:
            model_names = [name for name in self.model_configs.keys() if name in self.api_keys]
        
        print(f"开始批量访谈，模型数量: {len(model_names)}")
        
        results = {}
        successful_tasks = 0
        total_tasks = 0
        
        for model_name in model_names:
            print(f"\n{'='*50}")
            print(f"访谈模型: {model_name}")
            print(f"{'='*50}")
            
            model_results = self.interview_entity(model_name)
            total_tasks += 1
            
            if model_results:
                results[model_name] = model_results
                successful_tasks += 1
                print(f"✅ 模型 {model_name} 访谈完成: {len(model_results)} 个回答")
            else:
                print(f"❌ 模型 {model_name} 访谈失败")
        
        # 返回符合期望格式的结果
        return {
            'results': results,
            'total_tasks': total_tasks,
            'successful_tasks': successful_tasks,
            'success_rate': successful_tasks / total_tasks if total_tasks > 0 else 0
        }
    
    def save_results(self, results: Dict[str, Any], output_dir: str = None) -> str:
        """保存LLM访谈结果 - 专门为LLM values分析优化"""
        if output_dir is None:
            output_dir = self.data_path / "llm_values" / "llm_responses"  # 使用独立目录
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 转换结果为DataFrame格式
        if 'results' in results:
            all_responses = []
            
            for model_name, model_results in results['results'].items():
                for response in model_results:
                    # 将LLMResponse对象转换为字典
                    if hasattr(response, '__dict__'):
                        response_dict = response.__dict__.copy()
                    else:
                        response_dict = response
                    
                    # 确保有model_name
                    response_dict['model_name'] = model_name
                    all_responses.append(response_dict)
            
            if all_responses:
                # 转换为DataFrame（长格式）
                df_long = pd.DataFrame(all_responses)
                
                # 保存长格式数据（原始格式）
                long_file = output_path / f"llm_interview_responses_long_{timestamp}.pkl"
                df_long.to_pickle(long_file)
                
                # 转换为宽格式：每行一个模型，每列一个问题
                if 'question_id' in df_long.columns and 'response' in df_long.columns:
                    pivot_df = df_long.pivot_table(
                        index='model_name', 
                        columns='question_id', 
                        values='response', 
                        aggfunc='first'
                    ).reset_index()
                    
                    # 添加必要的元数据列
                    pivot_df['data_source'] = 'LLM'
                    pivot_df['entity_id'] = pivot_df['model_name']
                    
                    # 保存宽格式数据（用于后续PCA分析）
                    wide_file = output_path / f"llm_interview_responses_wide_{timestamp}.pkl"
                    pivot_df.to_pickle(wide_file)
                    
                    print(f"✅ LLM访谈结果已保存:")
                    print(f"   📊 长格式数据: {long_file}")
                    print(f"   📊 宽格式数据: {wide_file}")
                    print(f"   📈 数据形状: {pivot_df.shape}")
                    print(f"   🤖 包含模型: {list(pivot_df['model_name'])}")
                    print(f"   ❓ 包含问题: {[col for col in pivot_df.columns if col in self.iv_qns]}")
                    
                    return str(wide_file)  # 返回宽格式文件路径
        
        # 如果转换失败，使用基类方法
        return super().save_results(results, output_dir)


def main():
    """主函数 - 测试新架构"""
    print("🔄 使用新架构运行LLM访谈...")
    
    # 创建访谈对象 - 默认5次重复取众数
    interview = LLMInterview(repeat_count=5)
    
    # 显示可用模型
    available_models = [name for name in interview.model_configs.keys() if name in interview.api_keys]
    print(f"可用模型: {available_models}")
    
    if not available_models:
        print("没有可用的模型，请检查API密钥配置")
        return
    
    # 进行批量访谈（测试一个模型）
    test_models = available_models[:1] if available_models else []
    results = interview.batch_interview(test_models)
    
    # 保存结果
    if results:
        output_file = interview.save_results(results)
        print(f"\n✅ 新架构LLM访谈完成！")
        print(f"📊 访谈了 {len(results)} 个模型")
        print(f"💾 结果保存至: {output_file}")
    else:
        print("没有获得有效结果")


if __name__ == "__main__":
    main()
