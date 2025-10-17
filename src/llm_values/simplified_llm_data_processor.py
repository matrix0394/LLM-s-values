"""
简化的LLM数据处理器
专门处理data/llm_values/llm_responses中的数据
"""

import pandas as pd
import numpy as np
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any


class SimplifiedLLMDataProcessor:
    """简化的LLM数据处理器"""
    
    def __init__(self, data_path: str = "data/llm_values"):
        """初始化数据处理器"""
        self.data_path = Path(data_path)
        self.llm_responses_path = self.data_path / "llm_responses"
        
        # IVS问题列表
        self.iv_qns = ["A008", "A165", "E018", "E025", "F063", "F118", "F120", "G006", "Y002", "Y003"]
        
        print(f"📁 数据路径: {self.data_path}")
        print(f"📁 LLM回答路径: {self.llm_responses_path}")
    
    def load_llm_responses(self) -> pd.DataFrame:
        """加载LLM回答数据"""
        all_models_path = self.llm_responses_path / "all_models_responses.pkl"
        
        if all_models_path.exists():
            print(f"📊 从 {all_models_path} 加载数据")
            return pd.read_pickle(all_models_path)
        else:
            raise FileNotFoundError(f"LLM回答数据文件不存在: {all_models_path}")
    
    def process_llm_responses_to_ivs_format(self) -> pd.DataFrame:
        """将LLM回答数据转换为IVS格式"""
        # 加载原始数据
        llm_responses = self.load_llm_responses()
        
        print(f"📊 原始数据形状: {llm_responses.shape}")
        print(f"📊 列名: {list(llm_responses.columns)}")
        
        # 转换为透视表格式，每个模型一行，每个问题一列
        pivot_data = llm_responses.pivot_table(
            index='model_name',
            columns='question_id', 
            values='response',
            aggfunc='first'
        ).reset_index()
        
        print(f"📊 透视后数据形状: {pivot_data.shape}")
        print(f"📊 透视后列名: {list(pivot_data.columns)}")
        
        # 重命名列，确保与IVS格式一致
        pivot_data = pivot_data.rename(columns={'model_name': 'model_name'})
        
        # 添加必要的元数据列
        pivot_data['data_source'] = 'LLM'
        pivot_data['entity_type'] = 'llm'
        
        # 添加年份（使用当前年份）
        pivot_data['year'] = 2024
        
        # 添加权重（LLM数据权重设为1）
        pivot_data['weight'] = 1.0
        
        # 为每个模型分配一个唯一的代码
        pivot_data['model_code'] = range(1000, 1000 + len(pivot_data))
        
        # 确保所有IVS问题列都存在，并转换数据类型
        for question in self.iv_qns:
            if question not in pivot_data.columns:
                pivot_data[question] = np.nan
            else:
                # 处理特殊问题Y002和Y003
                if question == 'Y002':
                    # Y002应该是单个数值，如果是列表则取第一个
                    pivot_data[question] = pivot_data[question].apply(
                        lambda x: x[0] if isinstance(x, list) and len(x) > 0 else x
                    )
                elif question == 'Y003':
                    # Y003应该是单个数值，如果是列表则取第一个
                    pivot_data[question] = pivot_data[question].apply(
                        lambda x: x[0] if isinstance(x, list) and len(x) > 0 else x
                    )
                
                # 转换为数值类型
                pivot_data[question] = pd.to_numeric(pivot_data[question], errors='coerce')
        
        print(f"✅ 处理后数据形状: {pivot_data.shape}")
        return pivot_data
    
    def create_model_mapping(self) -> Dict[str, Dict[str, Any]]:
        """创建模型映射"""
        llm_responses = self.load_llm_responses()
        unique_models = llm_responses['model_name'].unique()
        
        model_mapping = {}
        for i, model in enumerate(unique_models):
            # 简化模型名称
            simplified_name = model.split('/')[-1] if '/' in model else model
            
            # 根据模型名称推断区域
            region = 'US'  # 默认
            if any(x in model.lower() for x in ['qwen', 'deepseek', 'baidu']):
                region = 'CN'
            elif 'mistral' in model.lower():
                region = 'EU'
            
            model_mapping[simplified_name] = {
                'model_code': f'LLM_{i+1:03d}',
                'model_name': simplified_name,
                'region': region,
                'display_name': simplified_name,
                'entity_type': 'llm'
            }
        
        return model_mapping
    
    def save_processed_data(self):
        """保存处理后的数据"""
        # 处理数据
        processed_data = self.process_llm_responses_to_ivs_format()
        model_mapping = self.create_model_mapping()
        
        # 保存处理后的数据
        processed_data_path = self.data_path / "llm_processed_responses_ivs_format.pkl"
        processed_data.to_pickle(processed_data_path)
        print(f"💾 保存处理后数据到: {processed_data_path}")
        
        # 保存模型映射
        model_mapping_path = self.data_path / "llm_model_mapping.json"
        with open(model_mapping_path, 'w', encoding='utf-8') as f:
            json.dump(model_mapping, f, indent=2, ensure_ascii=False)
        print(f"💾 保存模型映射到: {model_mapping_path}")
        
        # 保存模型映射为pkl格式
        model_mapping_pkl_path = self.data_path / "llm_model_mapping.pkl"
        pd.DataFrame.from_dict(model_mapping, orient='index').to_pickle(model_mapping_pkl_path)
        print(f"💾 保存模型映射pkl到: {model_mapping_pkl_path}")
        
        # 创建模型代码文件
        model_codes = pd.DataFrame([
            {'model_name': info['model_name'], 'model_code': info['model_code'], 'region': info['region']}
            for info in model_mapping.values()
        ])
        model_codes_path = self.data_path / "llm_model_codes.pkl"
        model_codes.to_pickle(model_codes_path)
        print(f"💾 保存模型代码到: {model_codes_path}")
        
        return processed_data, model_mapping


def main():
    """主函数 - 测试数据处理器"""
    processor = SimplifiedLLMDataProcessor()
    
    try:
        # 测试加载数据
        llm_responses = processor.load_llm_responses()
        print(f"✅ 成功加载LLM回答数据: {llm_responses.shape}")
        
        # 测试处理数据
        processed_data = processor.process_llm_responses_to_ivs_format()
        print(f"✅ 成功处理数据: {processed_data.shape}")
        
        # 测试创建模型映射
        model_mapping = processor.create_model_mapping()
        print(f"✅ 成功创建模型映射: {len(model_mapping)} 个模型")
        
        # 保存数据
        processor.save_processed_data()
        print("✅ 数据保存完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
