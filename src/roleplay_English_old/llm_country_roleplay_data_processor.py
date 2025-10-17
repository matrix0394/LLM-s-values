"""
LLM国家角色扮演数据处理模块
参考llm_data_processor的功能，处理llm_responses_roleplay中的roleplay_results.pkl文件
"""

import pandas as pd
import numpy as np
import os
import pickle
import json
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ProcessedRoleplayResponse:
    """处理后的角色扮演回答数据"""
    model_name: str
    country_name: str
    model_region: str  # 模型本身的区域（如US、CN、EU）
    cultural_region: str  # 模仿国家的文化区域
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
            'country_name': self.country_name,
            'model_region': self.model_region,
            'cultural_region': self.cultural_region,
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


class LLMCountryRoleplayDataProcessor:
    """LLM国家角色扮演数据处理器"""
    
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
        self.roleplay_responses_dir = self.data_dir / 'llm_responses_roleplay'
        
        # 确保目录存在
        self.roleplay_responses_dir.mkdir(exist_ok=True)
        
        # 加载配置
        self.models_config = self._load_models_config()
        self.cultural_regions = self._load_cultural_regions()
        
        # 存储处理后的数据
        self.processed_data: List[ProcessedRoleplayResponse] = []
    
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
    
    def _load_cultural_regions(self) -> Dict[str, str]:
        """加载文化区域映射"""
        cultural_config_path = self.data_dir.parent / 'config' / 'cultural_regions.json'
        try:
            with open(cultural_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('country_cultural_mapping', {})
        except Exception as e:
            print(f"加载文化区域配置失败: {e}")
            return {}
    
    def _get_model_region(self, model_id: str) -> str:
        """获取模型所属地区"""
        # 清理模型名称
        clean_model_id = model_id.replace('_as_', '/').split('_as_')[0]
        
        # 检查模型配置结构
        models_config = self.models_config.get("models", {})
        
        # 如果配置结构是 {model_name: {config...}}
        if clean_model_id in models_config:
            model_config = models_config[clean_model_id]
            if isinstance(model_config, dict):
                return model_config.get("region", "Unknown")
        
        # 如果配置结构是 {category: {model_name: {config...}}}
        for category_name, models in models_config.items():
            if isinstance(models, dict):
                if clean_model_id in models:
                    model_config = models[clean_model_id]
                    if isinstance(model_config, dict):
                        return model_config.get("region", "Unknown")
                # 也检查带下划线的版本
                underscore_model = clean_model_id.replace('/', '_')
                if underscore_model in models:
                    model_config = models[underscore_model]
                    if isinstance(model_config, dict):
                        return model_config.get("region", "Unknown")
        
        return "Unknown"
    
    def _get_cultural_region(self, country_name: str) -> str:
        """获取国家的文化区域"""
        return self.cultural_regions.get(country_name, "Unknown")
    
    def _parse_llm_response_string(self, response_str: str) -> Dict[str, Any]:
        """解析LLMResponse字符串格式
        
        Args:
            response_str: 形如 "LLMResponse(model_name='...', question_id='...', ...)" 的字符串
            
        Returns:
            解析后的字典
        """
        # 使用正则表达式解析
        pattern = r"LLMResponse\((.+)\)"
        match = re.match(pattern, response_str)
        
        if not match:
            return {}
        
        params_str = match.group(1)
        
        # 解析参数
        result = {}
        
        # 解析各个参数
        patterns = {
            'model_name': r"model_name='([^']*)'",
            'question_id': r"question_id='([^']*)'",
            'raw_response': r"raw_response='([^']*)'",
            'is_valid': r"is_valid=(True|False)",
            'error_message': r"error_message=('([^']*)'|None)"
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, params_str)
            if match:
                if key == 'is_valid':
                    result[key] = match.group(1) == 'True'
                elif key == 'error_message':
                    result[key] = None if match.group(1) == 'None' else match.group(2)
                else:
                    result[key] = match.group(1)
        
        # 特殊处理response字段
        response_pattern = r"response=(\[.*?\]|\d+|None)"
        response_match = re.search(response_pattern, params_str)
        if response_match:
            response_value = response_match.group(1)
            if response_value == 'None':
                result['response'] = None
            elif response_value.startswith('['):
                # 解析列表格式
                try:
                    # 简单的列表解析
                    numbers = re.findall(r'\d+', response_value)
                    result['response'] = [int(n) for n in numbers]
                except:
                    result['response'] = None
            else:
                try:
                    result['response'] = int(response_value)
                except:
                    result['response'] = None
        
        return result
    
    def load_roleplay_results(self) -> Dict[str, Any]:
        """加载角色扮演结果数据
        
        Returns:
            包含所有角色扮演结果的字典
        """
        # 优先使用JSON文件，避免pkl文件的模块依赖问题
        json_path = self.roleplay_responses_dir / 'roleplay_results.json'
        pkl_path = self.roleplay_responses_dir / 'roleplay_results.pkl'
        
        try:
            if json_path.exists():
                with open(json_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            elif pkl_path.exists():
                print("警告：pkl文件可能有模块依赖问题，建议使用JSON文件")
                with open(pkl_path, 'rb') as f:
                    return pickle.load(f)
            else:
                print(f"未找到角色扮演结果文件: {json_path} 或 {pkl_path}")
                return {}
        except Exception as e:
            print(f"加载角色扮演结果失败: {e}")
            # 如果JSON失败，尝试pkl
            if json_path.exists() and pkl_path.exists():
                try:
                    print("尝试加载pkl文件...")
                    with open(pkl_path, 'rb') as f:
                        return pickle.load(f)
                except Exception as e2:
                    print(f"pkl文件也加载失败: {e2}")
            return {}
    
    def process_roleplay_results(self, results_data: Dict[str, Any]) -> List[ProcessedRoleplayResponse]:
        """处理角色扮演结果数据
        
        Args:
            results_data: 从roleplay_results.pkl加载的数据
            
        Returns:
            处理后的响应列表
        """
        processed_responses = []
        
        if 'results' not in results_data:
            print("数据中未找到'results'字段")
            return processed_responses
        
        results = results_data['results']
        print(f"开始处理 {len(results)} 个角色扮演结果")
        
        for result in results:
            model_name = result.get('model', 'Unknown')
            country_name = result.get('country', 'Unknown')
            responses = result.get('responses', [])
            
            # 获取区域信息
            model_region = self._get_model_region(model_name)
            cultural_region = self._get_cultural_region(country_name)
            
            # 创建处理结果对象
            processed = ProcessedRoleplayResponse(
                model_name=model_name,
                country_name=country_name,
                model_region=model_region,
                cultural_region=cultural_region
            )
            
            # 处理每个回答
            for response_str in responses:
                if isinstance(response_str, str):
                    # 解析字符串格式的回答
                    response_data = self._parse_llm_response_string(response_str)
                else:
                    # 如果已经是字典格式
                    response_data = response_str
                
                if not response_data.get('is_valid', False):
                    continue  # 跳过无效回答
                
                question_id = response_data.get('question_id')
                answer = response_data.get('response')
                
                if question_id == 'A008':
                    processed.A008 = answer
                elif question_id == 'A165':
                    processed.A165 = answer
                elif question_id == 'E018':
                    processed.E018 = answer
                elif question_id == 'E025':
                    processed.E025 = answer
                elif question_id == 'F063':
                    processed.F063 = answer
                elif question_id == 'F118':
                    processed.F118 = answer
                elif question_id == 'F120':
                    processed.F120 = answer
                elif question_id == 'G006':
                    processed.G006 = answer
                elif question_id == 'Y002':
                    if isinstance(answer, (tuple, list)) and len(answer) == 2:
                        processed.Y002_first = answer[0]
                        processed.Y002_second = answer[1]
                        # 计算物质主义倾向
                        processed.Y002_materialist = Y002Processor.process_y002(answer[0], answer[1])
                elif question_id == 'Y003':
                    if isinstance(answer, (tuple, list)):
                        processed.Y003_values = list(answer)
                    elif isinstance(answer, int):
                        processed.Y003_values = [answer]
            
            processed_responses.append(processed)
        
        print(f"处理完成，得到 {len(processed_responses)} 个处理后的响应")
        return processed_responses
    
    def process_all_roleplay_data(self) -> pd.DataFrame:
        """处理所有角色扮演数据
        
        Returns:
            包含所有处理后数据的DataFrame
        """
        self.processed_data = []
        
        # 加载角色扮演结果
        results_data = self.load_roleplay_results()
        
        if not results_data:
            print("未找到角色扮演数据")
            return pd.DataFrame()
        
        # 处理数据
        self.processed_data = self.process_roleplay_results(results_data)
        
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
        processed_df = self.process_all_roleplay_data()
        
        if processed_df.empty:
            return pd.DataFrame()
        
        # 创建兼容格式的DataFrame
        ivs_compatible = pd.DataFrame()
        
        # 添加元数据列
        ivs_compatible['year'] = [2025] * len(processed_df)  # 使用当前年份
        ivs_compatible['country_code'] = processed_df['country_name']  # 使用国家名作为代码
        ivs_compatible['weight'] = [1.0] * len(processed_df)  # 统一权重
        ivs_compatible['model_name'] = processed_df['model_name']
        ivs_compatible['model_region'] = processed_df['model_region']
        ivs_compatible['cultural_region'] = processed_df['cultural_region']
        ivs_compatible['data_source'] = ['llm_roleplay'] * len(processed_df)
        
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
            output_path = self.data_dir / 'llm_roleplay_processed_responses.pkl'
        
        processed_df = self.process_all_roleplay_data()
        
        if not processed_df.empty:
            processed_df.to_pickle(output_path)
            print(f"处理后的角色扮演数据已保存到: {output_path}")
            
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
        processed_df = self.process_all_roleplay_data()
        
        if processed_df.empty:
            return {"message": "没有可用数据"}
        
        stats = {
            "total_responses": len(processed_df),
            "unique_models": processed_df['model_name'].nunique(),
            "unique_countries": processed_df['country_name'].nunique(),
            "models_by_region": processed_df['model_region'].value_counts().to_dict(),
            "countries_by_cultural_region": processed_df['cultural_region'].value_counts().to_dict(),
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
    processor = LLMCountryRoleplayDataProcessor()
    print("处理角色扮演数据...")
    processed_df = processor.process_all_roleplay_data()
    
    print(f"处理了 {len(processed_df)} 条角色扮演数据")
    
    # 显示处理结果
    if not processed_df.empty:
        print("\n处理后的数据样例:")
        print(processed_df[['model_name', 'country_name', 'model_region', 'cultural_region', 'A008', 'A165', 'Y002_materialist']].head())
        
        # 创建IVS兼容格式
        ivs_df = processor.create_ivs_compatible_dataframe()
        print("\nIVS兼容格式数据样例:")
        print(ivs_df[['model_name', 'country_code', 'model_region', 'cultural_region', 'A008', 'A165', 'Y002']].head())
        
        print("\n关键统计信息:")
        print(f"模型本身区域分布 (model_region): {processed_df['model_region'].value_counts().to_dict()}")
        print(f"模仿国家文化区域分布 (cultural_region): {processed_df['cultural_region'].value_counts().to_dict()}")
        
        # 显示统计信息
        stats = processor.get_summary_statistics()
        print("\n完整数据统计:")
        for key, value in stats.items():
            print(f"{key}: {value}")
        
        # 保存数据
        processor.save_processed_data()
    else:
        print("没有找到有效数据")
