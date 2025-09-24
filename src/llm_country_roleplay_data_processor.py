"""
LLM国家角色扮演数据处理模块
模仿llm_data_processor的功能，仅进行数据格式整理，不合并真实国家数据
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
class ProcessedCountryRoleplayResponse:
    """处理后的国家角色扮演回答数据"""
    model_name: str
    country_name: str
    cultural_region: str
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
    Y002_materialist: Optional[int] = None
    Y003_values: Optional[List[int]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            'model_name': self.model_name,
            'country_name': self.country_name,
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
            for i in range(1, 12):
                result[f'Y003_{i}'] = 1 if i in self.Y003_values else 0
        else:
            for i in range(1, 12):
                result[f'Y003_{i}'] = 0
                
        return result


class Y002Processor:
    """Y002问题特殊处理器"""
    
    MATERIALIST_MAPPING = {
        (1, 3): 1, (3, 1): 1,  # 物质主义
        (2, 4): 3, (4, 2): 3,  # 后物质主义
        (1, 2): 2, (2, 1): 2,  # 混合
        (1, 4): 2, (4, 1): 2,
        (2, 3): 2, (3, 2): 2,
        (3, 4): 2, (4, 3): 2,
    }
    
    @classmethod
    def process_y002(cls, first_choice: int, second_choice: int) -> int:
        return cls.MATERIALIST_MAPPING.get((first_choice, second_choice), 2)


class LLMCountryRoleplayDataProcessor:
    """LLM国家角色扮演数据处理器 - 仅格式整理版本"""
    
    def __init__(self, data_dir: str = None):
        """初始化处理器"""
        if data_dir is None:
            current_dir = Path(__file__).parent
            self.data_dir = current_dir.parent / 'data'
        else:
            self.data_dir = Path(data_dir)
        
        self.processed_data = []
        self.models_config = self._load_models_config()
    
    def _load_models_config(self) -> Dict[str, Any]:
        """加载模型配置"""
        config_path = self.data_dir.parent / 'config' / 'llm_models.json'
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载模型配置失败: {e}")
            return {}
    
    def _get_cultural_region(self, country_name: str) -> str:
        """获取国家的文化区域"""
        # 这里可以根据需要实现文化区域映射逻辑
        # 暂时返回默认值
        return "Unknown"
    
    def load_roleplay_responses(self) -> List[Dict[str, Any]]:
        """加载角色扮演回答数据 - 支持pkl格式，包括子目录"""
        responses_dir = self.data_dir / 'llm_responses_roleplay'
        all_responses = []
        
        if not responses_dir.exists():
            print(f"角色扮演数据目录不存在: {responses_dir}")
            return all_responses
        
        # 递归查找所有pkl文件（包括子目录）
        pkl_files = list(responses_dir.rglob('*.pkl'))
        
        if pkl_files:
            print(f"找到 {len(pkl_files)} 个pkl文件")
            for file_path in pkl_files:
                try:
                    # 跳过旧格式的汇总文件
                    if file_path.name in ['country_roleplay_responses.pkl', 'country_roleplay_detailed_20250921_205404.pkl']:
                        print(f"跳过旧格式文件: {file_path.name}")
                        continue
                        
                    with open(file_path, 'rb') as f:
                        data = pickle.load(f)
                        if isinstance(data, list):
                            all_responses.extend(data)
                        elif isinstance(data, dict):
                            # 检查是否是新格式的单个结果文件
                            if len(data) == 1 and any('_as_' in key for key in data.keys()):
                                # 新格式：{"model_as_country": [responses]}
                                for key, responses in data.items():
                                    if isinstance(responses, list):
                                        all_responses.extend(responses)
                            else:
                                all_responses.append(data)
                        else:
                            # 如果是DataFrame，转换为字典列表
                            if hasattr(data, 'to_dict'):
                                if hasattr(data, 'iterrows'):
                                    # 是DataFrame
                                    for _, row in data.iterrows():
                                        all_responses.append(row.to_dict())
                                else:
                                    # 是Series或其他有to_dict方法的对象
                                    all_responses.append(data.to_dict())
                    print(f"加载pkl文件: {file_path.relative_to(responses_dir)}")
                except Exception as e:
                    print(f"加载pkl文件失败 {file_path}: {e}")
        else:
            # 如果没有pkl文件，尝试加载json文件作为备选
            json_files = list(responses_dir.rglob('*.json'))
            print(f"未找到pkl文件，尝试加载 {len(json_files)} 个json文件")
            
            for file_path in json_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            all_responses.extend(data)
                        else:
                            all_responses.append(data)
                except Exception as e:
                    print(f"加载json文件失败 {file_path}: {e}")
        
        print(f"总共加载了 {len(all_responses)} 条回答数据")
        return all_responses
    
    def process_roleplay_responses(self, responses: List[Dict[str, Any]]) -> List[ProcessedCountryRoleplayResponse]:
        """处理角色扮演回答数据"""
        processed_responses = []
        
        # 按模型和国家分组
        grouped_data = {}
        for response in responses:
            model_name = response.get('model_name', 'Unknown')
            country_name = response.get('country_name', 'Unknown')
            key = (model_name, country_name)
            
            if key not in grouped_data:
                grouped_data[key] = []
            grouped_data[key].append(response)
        
        # 处理每个组合
        for (model_name, country_name), group_responses in grouped_data.items():
            cultural_region = self._get_cultural_region(country_name)
            
            processed = ProcessedCountryRoleplayResponse(
                model_name=model_name,
                country_name=country_name,
                cultural_region=cultural_region
            )
            
            # 处理每个问题的回答
            for response in group_responses:
                question_id = response.get('question_id')
                answer = response.get('response')
                
                if not response.get('is_valid', False):
                    continue
                
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
                        try:
                            first, second = int(answer[0]), int(answer[1])
                            if 1 <= first <= 4 and 1 <= second <= 4 and first != second:
                                processed.Y002_first = first
                                processed.Y002_second = second
                                processed.Y002_materialist = Y002Processor.process_y002(first, second)
                            else:
                                print(f"Y002回答值无效: {answer}")
                        except (ValueError, TypeError):
                            print(f"Y002回答格式错误: {answer}")
                elif question_id == 'Y003':
                    if isinstance(answer, (tuple, list)):
                        processed.Y003_values = list(answer)
                    elif isinstance(answer, int):
                        processed.Y003_values = [answer]
            
            processed_responses.append(processed)
        
        return processed_responses
    
    def create_ivs_compatible_dataframe(self) -> pd.DataFrame:
        """创建IVS兼容格式的DataFrame - 仅角色扮演数据"""
        # 加载并处理角色扮演数据
        roleplay_data = self.load_roleplay_responses()
        processed_responses = self.process_roleplay_responses(roleplay_data)
        
        if not processed_responses:
            print("没有找到有效的角色扮演数据")
            return pd.DataFrame()
        
        # 转换为DataFrame
        data_dicts = [response.to_dict() for response in processed_responses]
        df = pd.DataFrame(data_dicts)
        
        # 创建IVS兼容格式
        ivs_compatible = pd.DataFrame()
        
        # 添加元数据列
        ivs_compatible['year'] = 2025
        ivs_compatible['country_code'] = df['country_name']  # 使用国家名作为代码
        ivs_compatible['weight'] = 1.0
        ivs_compatible['cultural_region'] = df['cultural_region']
        ivs_compatible['model_name'] = df['model_name']
        ivs_compatible['data_source'] = 'llm_roleplay'
        
        # 添加IVS问题列
        ivs_questions = ['A008', 'A165', 'E018', 'E025', 'F063', 'F118', 'F120', 'G006']
        for q in ivs_questions:
            if q in df.columns:
                ivs_compatible[q] = df[q]
        
        # 处理Y002 - 使用物质主义倾向值
        if 'Y002_materialist' in df.columns:
            ivs_compatible['Y002'] = df['Y002_materialist']
        
        # 处理Y003 - 选择最重要的一个值作为代表
        def get_primary_y003_value(row):
            for i in range(1, 12):
                if row.get(f'Y003_{i}', 0) == 1:
                    return i
            return np.nan
        
        ivs_compatible['Y003'] = df.apply(get_primary_y003_value, axis=1)
        
        print(f"创建IVS兼容格式数据: {len(ivs_compatible)} 条记录")
        # 数据质量检查和改进
        print(f"原始数据形状: {ivs_compatible.shape}")
        
        # 检查每列的缺失值情况
        missing_stats = ivs_compatible.isnull().sum()
        print("缺失值统计:")
        for col, missing_count in missing_stats.items():
            if missing_count > 0:
                print(f"  {col}: {missing_count}/{len(ivs_compatible)} ({missing_count/len(ivs_compatible)*100:.1f}%)")
        
        # 移除缺失值过多的行（少于6个有效问题回答）
        ivs_questions = ['A008', 'A165', 'E018', 'E025', 'F063', 'F118', 'F120', 'G006', 'Y002', 'Y003']
        available_questions = [q for q in ivs_questions if q in ivs_compatible.columns]
        
        # 计算每行有效回答数
        valid_answers_per_row = ivs_compatible[available_questions].notna().sum(axis=1)
        
        # 保留至少有6个有效回答的行
        before_filter = len(ivs_compatible)
        ivs_compatible = ivs_compatible[valid_answers_per_row >= 6]
        after_filter = len(ivs_compatible)
        
        print(f"过滤后数据形状: {ivs_compatible.shape}")
        print(f"移除了 {before_filter - after_filter} 行数据质量不足的记录")
        
        # 检查是否还有足够的数据进行PCA
        if len(ivs_compatible) < 10:
            print("警告：数据量不足，可能无法进行有效的PCA分析")
        
        return ivs_compatible
    
    def save_processed_data(self, output_path: str = None):
        """保存处理后的数据"""
        if output_path is None:
            output_path = self.data_dir / 'llm_roleplay_processed_responses.pkl'
        
        # 创建IVS兼容格式数据
        ivs_data = self.create_ivs_compatible_dataframe()
        
        if not ivs_data.empty:
            ivs_data.to_pickle(output_path)
            print(f"处理后的数据已保存到: {output_path}")
            
            # 同时保存原始格式
            raw_output_path = str(output_path).replace('.pkl', '_raw.pkl')
            roleplay_data = self.load_roleplay_responses()
            processed_responses = self.process_roleplay_responses(roleplay_data)
            if processed_responses:
                data_dicts = [response.to_dict() for response in processed_responses]
                raw_df = pd.DataFrame(data_dicts)
                raw_df.to_pickle(raw_output_path)
                print(f"原始格式数据已保存到: {raw_output_path}")
        else:
            print("没有数据需要保存")
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """获取数据摘要统计"""
        ivs_data = self.create_ivs_compatible_dataframe()
        
        if ivs_data.empty:
            return {"message": "没有可用数据"}
        
        stats = {
            "total_records": len(ivs_data),
            "unique_countries": ivs_data['country_code'].nunique(),
            "unique_models": ivs_data['model_name'].nunique(),
            "countries_by_region": ivs_data['cultural_region'].value_counts().to_dict(),
            "models_distribution": ivs_data['model_name'].value_counts().to_dict(),
            "response_completeness": {}
        }
        
        # 计算每个问题的回答完整性
        ivs_questions = ['A008', 'A165', 'E018', 'E025', 'F063', 'F118', 'F120', 'G006', 'Y002', 'Y003']
        for q in ivs_questions:
            if q in ivs_data.columns:
                valid_responses = ivs_data[q].notna().sum()
                stats["response_completeness"][q] = f"{valid_responses}/{len(ivs_data)}"
        
        return stats
    
    def save_batch_results(self, batch_size: int = 50):
        """批量保存结果，避免单个文件过大"""
        ivs_data = self.create_ivs_compatible_dataframe()
        
        if ivs_data.empty:
            return
        
        # 按国家分组
        country_groups = ivs_data.groupby('country_code')
        
        batch_num = 0
        current_batch = []
        
        for country_code, group in country_groups:
            current_batch.append(group)
            
            if len(current_batch) >= batch_size:
                # 保存当前批次
                batch_data = pd.concat(current_batch, ignore_index=True)
                batch_file = self.data_dir / f'roleplay_batch_{batch_num:03d}.pkl'
                batch_data.to_pickle(batch_file)
                
                print(f"保存批次 {batch_num}: {len(batch_data)} 条记录到 {batch_file}")
                
                # 重置批次
                current_batch = []
                batch_num += 1
        
        # 保存剩余数据
        if current_batch:
            batch_data = pd.concat(current_batch, ignore_index=True)
            batch_file = self.data_dir / f'roleplay_batch_{batch_num:03d}.pkl'
            batch_data.to_pickle(batch_file)
            print(f"保存最后批次 {batch_num}: {len(batch_data)} 条记录")


if __name__ == "__main__":
    # 测试代码
    processor = LLMCountryRoleplayDataProcessor()
    
    print("处理LLM国家角色扮演数据...")
    
    # 创建IVS兼容格式数据（仅角色扮演数据）
    ivs_data = processor.create_ivs_compatible_dataframe()
    
    if not ivs_data.empty:
        print(f"\n处理了 {len(ivs_data)} 条角色扮演数据")
        
        # 显示数据预览
        print("\n数据预览:")
        preview_columns = ['country_code', 'cultural_region', 'model_name', 'A008', 'A165', 'Y002']
        available_columns = [col for col in preview_columns if col in ivs_data.columns]
        print(ivs_data[available_columns].head())
        
        # 显示统计信息
        stats = processor.get_summary_statistics()
        print("\n数据统计:")
        for key, value in stats.items():
            print(f"{key}: {value}")
        
        # 保存数据
        processor.save_processed_data()
    else:
        print("没有找到有效数据")