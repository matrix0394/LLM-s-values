"""
大模型回答数据处理模块
类似8-llm-collate的功能，整合和处理各模型的回答数据
"""

import pandas as pd
import numpy as np
import os
import glob
import pickle
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class ProcessedResponse:
    """处理后的回答数据"""
    model_name: str
    model_region: str
    A008: Optional[int] = None
    A165: Optional[int] = None
    E018: Optional[int] = None
    E025: Optional[int] = None
    F063: Optional[int] = None
    F118: Optional[int] = None
    F120: Optional[int] = None
    G006: Optional[int] = None
    Y002_first: Optional[int] = None
    Y002_second: Optional[int] = None
    Y002_materialist: Optional[int] = None  # 物质主义倾向
    Y003_values: Optional[List[int]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            'model_name': self.model_name,
            'model_region': self.model_region,
            'A008': self.A008,
            'A165': self.A165,
            'E018': self.E018,
            'E025': self.E025,
            'F063': self.F063,
            'F118': self.F118,
            'F120': self.F120,
            'G006': self.G006,
            'Y002_first': self.Y002_first,
            'Y002_second': self.Y002_second,
            'Y002_materialist': self.Y002_materialist
        }
        
        # 处理Y003的多个值
        if self.Y003_values:
            for i in range(1, 12):  # Y003有11个选项
                result[f'Y003_{i}'] = 1 if i in self.Y003_values else 0
        else:
            for i in range(1, 12):
                result[f'Y003_{i}'] = 0
                
        return result


class Y002Processor:
    """Y002问题特殊处理器
    
    根据参考项目8-llm-collate中的说明：
    Y002问题的回答需要映射为物质主义/后物质主义倾向
    """
    
    # 物质主义倾向映射
    MATERIALIST_MAPPING = {
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
        
        Returns:
            1: 物质主义 (Materialist)
            2: 混合 (Mixed)
            3: 后物质主义 (Postmaterialist)
        """
        return cls.MATERIALIST_MAPPING.get((first_choice, second_choice), 2)


class LLMDataProcessor:
    """大模型数据处理器"""
    
    def __init__(self, data_dir: str = None, config_path: str = None):
        """初始化数据处理器
        
        Args:
            data_dir: 数据目录路径
            config_path: 模型配置文件路径
        """
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'llm_models.json')
            
        self.data_dir = Path(data_dir)
        self.config_path = Path(config_path)
        self.llm_responses_dir = self.data_dir / 'llm_responses'
        
        # 确保目录存在
        self.llm_responses_dir.mkdir(exist_ok=True)
        
        # 加载模型配置
        self.models_config = self._load_models_config()
        
        # 存储处理后的数据
        self.processed_data: List[ProcessedResponse] = []
    
    def _load_models_config(self) -> Dict:
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
    
    def _get_model_region(self, model_id: str) -> str:
        """获取模型所属地区"""
        for category_name, models in self.models_config.get("models", {}).items():
            if model_id in models:
                return models[model_id].get("region", "Unknown")
        return "Unknown"
    
    def load_model_responses(self, model_id: str) -> Optional[pd.DataFrame]:
        """加载指定模型的回答数据
        
        Args:
            model_id: 模型ID
            
        Returns:
            DataFrame或None
        """
        # 尝试多种文件格式
        possible_files = [
            self.llm_responses_dir / f"{model_id}_responses.pkl",
            self.llm_responses_dir / f"{model_id}_responses.csv",
            self.llm_responses_dir / f"{model_id}.pkl",
            self.llm_responses_dir / f"{model_id}.csv"
        ]
        
        for file_path in possible_files:
            if file_path.exists():
                try:
                    if file_path.suffix == '.pkl':
                        return pd.read_pickle(file_path)
                    elif file_path.suffix == '.csv':
                        return pd.read_csv(file_path)
                except Exception as e:
                    print(f"加载文件失败 {file_path}: {e}")
                    continue
        
        print(f"未找到模型 {model_id} 的回答文件")
        return None
    
    def load_all_responses(self) -> List[pd.DataFrame]:
        """加载所有模型的回答数据"""
        all_dataframes = []
        
        # 获取所有pickle和csv文件
        pkl_files = list(self.llm_responses_dir.glob("*.pkl"))
        csv_files = list(self.llm_responses_dir.glob("*.csv"))
        
        all_files = pkl_files + csv_files
        
        for file_path in all_files:
            try:
                if file_path.suffix == '.pkl':
                    df = pd.read_pickle(file_path)
                elif file_path.suffix == '.csv':
                    df = pd.read_csv(file_path)
                else:
                    continue
                    
                # 添加文件来源信息
                df['source_file'] = file_path.name
                all_dataframes.append(df)
                
            except Exception as e:
                print(f"加载文件失败 {file_path}: {e}")
                continue
        
        return all_dataframes
    
    def process_single_model_responses(self, df: pd.DataFrame) -> Optional[ProcessedResponse]:
        """处理单个模型的回答数据
        
        Args:
            df: 包含模型回答的DataFrame
            
        Returns:
            ProcessedResponse或None
        """
        if df.empty:
            return None
        
        # 获取模型名称
        model_name = df['model_name'].iloc[0] if 'model_name' in df.columns else "Unknown"
        model_region = self._get_model_region(model_name)
        
        # 创建处理结果对象
        result = ProcessedResponse(
            model_name=model_name,
            model_region=model_region
        )
        
        # 处理每个问题的回答
        for _, row in df.iterrows():
            if not row.get('is_valid', False):
                continue  # 跳过无效回答
                
            question_id = row['question_id']
            response = row['response']
            
            if question_id == 'A008':
                result.A008 = response
            elif question_id == 'A165':
                result.A165 = response
            elif question_id == 'E018':
                result.E018 = response
            elif question_id == 'E025':
                result.E025 = response
            elif question_id == 'F063':
                result.F063 = response
            elif question_id == 'F118':
                result.F118 = response
            elif question_id == 'F120':
                result.F120 = response
            elif question_id == 'G006':
                result.G006 = response
            elif question_id == 'Y002':
                if isinstance(response, (tuple, list)) and len(response) == 2:
                    result.Y002_first = response[0]
                    result.Y002_second = response[1]
                    # 计算物质主义倾向
                    result.Y002_materialist = Y002Processor.process_y002(response[0], response[1])
            elif question_id == 'Y003':
                if isinstance(response, (tuple, list)):
                    result.Y003_values = list(response)
                elif isinstance(response, int):
                    result.Y003_values = [response]
        
        return result
    
    def process_all_models(self) -> pd.DataFrame:
        """处理所有模型的回答数据
        
        Returns:
            包含所有处理后数据的DataFrame
        """
        self.processed_data = []
        
        # 加载所有回答数据
        all_dfs = self.load_all_responses()
        
        if not all_dfs:
            print("未找到任何回答数据文件")
            return pd.DataFrame()
        
        # 合并所有DataFrame
        combined_df = pd.concat(all_dfs, ignore_index=True)
        
        # 按模型分组处理
        for model_name in combined_df['model_name'].unique():
            model_df = combined_df[combined_df['model_name'] == model_name]
            processed = self.process_single_model_responses(model_df)
            
            if processed:
                self.processed_data.append(processed)
        
        # 转换为DataFrame
        if self.processed_data:
            data_dicts = [item.to_dict() for item in self.processed_data]
            return pd.DataFrame(data_dicts)
        else:
            return pd.DataFrame()
    
    def create_ivs_compatible_dataframe(self) -> pd.DataFrame:
        """创建与IVS数据格式兼容的DataFrame
        
        Returns:
            与真实IVS数据格式兼容的DataFrame
        """
        processed_df = self.process_all_models()
        
        if processed_df.empty:
            return pd.DataFrame()
        
        # 创建兼容格式的DataFrame
        ivs_compatible = pd.DataFrame()
        
        # 添加元数据列
        ivs_compatible['year'] = 2025  # 使用当前年份
        ivs_compatible['country_code'] = processed_df['model_name']  # 使用模型名作为"国家"代码
        ivs_compatible['weight'] = 1.0  # 统一权重
        ivs_compatible['model_region'] = processed_df['model_region']
        
        # 添加IVS问题列
        ivs_questions = ['A008', 'A165', 'E018', 'E025', 'F063', 'F118', 'F120', 'G006']
        for q in ivs_questions:
            ivs_compatible[q] = processed_df[q]
        
        # 处理Y002 - 使用物质主义倾向值
        ivs_compatible['Y002'] = processed_df['Y002_materialist']
        
        # 处理Y003 - 选择最重要的一个值作为代表
        def get_primary_y003_value(row):
            for i in range(1, 12):
                if row.get(f'Y003_{i}', 0) == 1:
                    return i
            return np.nan
        
        ivs_compatible['Y003'] = processed_df.apply(get_primary_y003_value, axis=1)
        
        return ivs_compatible
    
    def save_processed_data(self, output_path: str = None):
        """保存处理后的数据
        
        Args:
            output_path: 输出文件路径
        """
        if output_path is None:
            output_path = self.data_dir / 'llm_processed_responses.pkl'
        
        processed_df = self.process_all_models()
        
        if not processed_df.empty:
            processed_df.to_pickle(output_path)
            print(f"处理后的数据已保存到: {output_path}")
            
            # 同时保存IVS兼容格式
            ivs_compatible = self.create_ivs_compatible_dataframe()
            ivs_path = str(output_path).replace('.pkl', '_ivs_format.pkl')
            ivs_compatible.to_pickle(ivs_path)
            print(f"IVS兼容格式数据已保存到: {ivs_path}")
        else:
            print("没有数据需要保存")
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """获取数据摘要统计
        
        Returns:
            包含统计信息的字典
        """
        processed_df = self.process_all_models()
        
        if processed_df.empty:
            return {"message": "没有可用数据"}
        
        stats = {
            "total_models": len(processed_df),
            "models_by_region": processed_df['model_region'].value_counts().to_dict(),
            "response_completeness": {},
            "y002_materialist_distribution": processed_df['Y002_materialist'].value_counts().to_dict() if 'Y002_materialist' in processed_df.columns else {}
        }
        
        # 计算每个问题的回答完整性
        ivs_questions = ['A008', 'A165', 'E018', 'E025', 'F063', 'F118', 'F120', 'G006']
        for q in ivs_questions:
            if q in processed_df.columns:
                valid_responses = processed_df[q].notna().sum()
                stats["response_completeness"][q] = f"{valid_responses}/{len(processed_df)}"
        
        return stats
    
    

if __name__ == "__main__":
    # 测试代码
    processor = LLMDataProcessor()
    
    # 注释掉模拟数据创建
    # print("创建模拟数据...")
    # processor.create_mock_data_for_testing()
    
    # 直接处理现有的真实数据
    print("处理现有LLM回答数据...")
    processed_df = processor.process_all_models()
    
    print(f"处理了 {len(processed_df)} 个模型的数据")
    
    # 显示处理结果
    if not processed_df.empty:
        print("\n处理后的数据:")
        print(processed_df[['model_name', 'model_region', 'A008', 'A165', 'Y002_materialist']].head())
        
        # 创建IVS兼容格式
        ivs_df = processor.create_ivs_compatible_dataframe()
        print("\nIVS兼容格式数据:")
        print(ivs_df[['country_code', 'model_region', 'A008', 'A165', 'Y002']].head())
        
        # 显示统计信息
        stats = processor.get_summary_statistics()
        print("\n数据统计:")
        for key, value in stats.items():
            print(f"{key}: {value}")
        
        # 保存数据
        processor.save_processed_data()
    else:
        print("没有找到有效数据")