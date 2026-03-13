"""
大模型回答数据处理模块
类似8-llm-collate的功能，整合和处理各模型的回答数据
"""

import pandas as pd
import numpy as np
import os
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import json
from src.base.ivs_question_processor import IVSQuestionProcessor


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


class LLMDataProcessor:
    """大模型数据处理器"""
    
    def __init__(self, data_dir: str = None, config_path: str = None):
        """初始化数据处理器
        
        Args:
            data_dir: 数据目录路径
            config_path: 模型配置文件路径
        """
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'models', 'llm_models.json')
            
        self.data_dir = Path(data_dir)
        self.config_path = Path(config_path)
        
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
        models = self.models_config.get("models", {})
        if model_id in models:
            return models[model_id].get("region", "Unknown")
        return "Unknown"
    
    def load_all_responses(self) -> List[pd.DataFrame]:
        """加载所有模型的回答数据（从独立文件加载）"""
        all_dataframes = []
        
        # 从interview_raw目录加载所有独立模型文件
        interview_raw_dir = self.data_dir / "llm_values" / "interview_raw"
        if interview_raw_dir.exists():
            # 只加载独立模型文件（排除合并文件）
            individual_files = [f for f in interview_raw_dir.glob("*.pkl") 
                               if not f.name.startswith("llm_interview_raw_")]
            
            if not individual_files:
                print(f"⚠️ 未找到独立模型文件")
                return all_dataframes
            
            print(f"🔍 找到 {len(individual_files)} 个独立模型文件")
            
            for file_path in individual_files:
                try:
                    with open(file_path, 'rb') as f:
                        data = pickle.load(f)
                    
                    # 独立文件格式：直接是单个模型的数据
                    if isinstance(data, dict):
                        model_name = data.get('model_name', data.get('model', ''))
                        if not model_name:
                            print(f"⚠️ {file_path.name}: 无法识别模型名称")
                            continue
                        
                        # 转换为DataFrame格式
                        rows = []
                        for response in data.get('responses', []):
                            if isinstance(response, dict):
                                rows.append({
                                    'model_name': model_name,
                                    'question_id': response.get('question_id'),
                                    'response': (response.get('final_response') or 
                                               response.get('processed_response') or 
                                               response.get('response')),
                                    'is_valid': response.get('is_valid', True),
                                    'source_file': file_path.name
                                })
                        
                        if rows:
                            df = pd.DataFrame(rows)
                            all_dataframes.append(df)
                            print(f"   ✅ {model_name}: {len(rows)} 条回答")
                        else:
                            print(f"   ⚠️ {model_name}: 无有效回答")
                            
                except Exception as e:
                    print(f"   ❌ {file_path.name}: 加载失败 - {e}")
                    continue
        
        if all_dataframes:
            print(f"\n📊 总计加载: {len(all_dataframes)} 个模型")
        else:
            print(f"\n⚠️ 未加载到任何数据")
        
        return all_dataframes
    
    def process_single_model_responses(self, df: pd.DataFrame) -> Optional[ProcessedResponse]:
        """处理单个模型的回答数据
        
        Args:
            df: 包含模型回答的DataFrame
            
        Returns:
            ProcessedResponse或None（如果有效回答数<6则返回None）
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
        
        # 统计有效回答数
        valid_count = 0
        
        # 处理每个问题的回答
        for _, row in df.iterrows():
            if not row.get('is_valid', False):
                continue  # 跳过无效回答
                
            question_id = row['question_id']
            response = row['response']
            
            if question_id == 'A008':
                result.A008 = response
                valid_count += 1
            elif question_id == 'A165':
                result.A165 = response
                valid_count += 1
            elif question_id == 'E018':
                result.E018 = response
                valid_count += 1
            elif question_id == 'E025':
                result.E025 = response
                valid_count += 1
            elif question_id == 'F063':
                result.F063 = response
                valid_count += 1
            elif question_id == 'F118':
                result.F118 = response
                valid_count += 1
            elif question_id == 'F120':
                result.F120 = response
                valid_count += 1
            elif question_id == 'G006':
                result.G006 = response
                valid_count += 1
            elif question_id == 'Y002':
                if isinstance(response, (tuple, list)) and len(response) == 2:
                    result.Y002_first = response[0]
                    result.Y002_second = response[1]
                    # 计算物质主义倾向
                    result.Y002_materialist = IVSQuestionProcessor.process_y002(response[0], response[1])
                    valid_count += 1
            elif question_id == 'Y003':
                if isinstance(response, (tuple, list)):
                    result.Y003_values = list(response)
                    valid_count += 1
                elif isinstance(response, int):
                    result.Y003_values = [response]
                    valid_count += 1
        
        # 🔧 筛选：只保留有效回答数≥6的模型
        if valid_count < 6:
            print(f"⚠️ {model_name}: 有效回答数不足 ({valid_count}/10)，已过滤")
            return None
        
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
        
        # 添加元数据列（与Stage0格式对应）
        ivs_compatible['year'] = [2025] * len(processed_df)  # 2025表示当前年份
        ivs_compatible['country_code'] = processed_df['model_name']  # 使用模型名作为标识
        ivs_compatible['weight'] = [1.0] * len(processed_df)  # 统一权重
        ivs_compatible['model_region'] = processed_df['model_region']  # LLM特有字段
        
        # 添加IVS问题列
        ivs_questions = ['A008', 'A165', 'E018', 'E025', 'F063', 'F118', 'F120', 'G006']
        for q in ivs_questions:
            ivs_compatible[q] = processed_df[q]
        
        # 处理Y002 - 使用物质主义倾向值
        ivs_compatible['Y002'] = processed_df['Y002_materialist']
        
        # 处理Y003 - 使用IVSQuestionProcessor计算传统vs世俗理性分数
        def get_y003_score(row):
            """计算Y003的分数（与IVS处理一致）"""
            # 收集被选中的选项
            selected_values = []
            for i in range(1, 12):
                if row.get(f'Y003_{i}', 0) == 1:
                    selected_values.append(i)
            
            if not selected_values:
                return np.nan
            
            # 使用IVSQuestionProcessor计算分数（与Stage0一致）
            result = IVSQuestionProcessor.process_y003(selected_values)
            return result["y003_score"]  # 返回计算分数，不是选项编号
        
        ivs_compatible['Y003'] = processed_df.apply(get_y003_score, axis=1)
        
        return ivs_compatible
    
    def save_processed_data(self, output_path: str = None) -> Optional[str]:
        """
        保存处理后的数据为标准IVS格式
        
        Args:
            output_path: 输出文件路径（可选）
        
        Returns:
            保存的文件路径，如果保存失败则返回None
        """
        if output_path is None:
            # Stage1专用路径：data/llm_values/，带时间戳
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            llm_values_dir = self.data_dir / 'llm_values'
            llm_values_dir.mkdir(parents=True, exist_ok=True)
            output_path = llm_values_dir / f'llm_processed_responses_ivs_format_{timestamp}.pkl'
        
        # 只保存IVS兼容格式（标准格式）
        ivs_compatible = self.create_ivs_compatible_dataframe()
        
        if not ivs_compatible.empty:
            # 保存带时间戳的版本
            ivs_compatible.to_pickle(output_path)
            print(f"✅ LLM数据已保存（IVS标准格式）: {output_path}")
            print(f"   - 模型数量: {len(ivs_compatible)}")
            print(f"   - 数据格式与Stage0的valid_data.pkl一致")
            
            # 同时保存JSON格式（便于查看）
            json_path = str(output_path).replace('.pkl', '.json')
            ivs_compatible.to_json(json_path, orient='records', indent=2)
            print(f"   - JSON格式: {json_path}")
            
            # 同时保存标准文件名版本（不带时间戳，用于后续步骤）
            llm_values_dir = self.data_dir / 'llm_values'
            standard_path = llm_values_dir / 'llm_values_ivs_format.pkl'
            ivs_compatible.to_pickle(standard_path)
            standard_json_path = llm_values_dir / 'llm_values_ivs_format.json'
            ivs_compatible.to_json(standard_json_path, orient='records', indent=2)
            print(f"   - 标准路径: {standard_path}")
            
            return str(standard_path)
        else:
            print("⚠️ 没有数据需要保存")
            return None
    
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
    processor = LLMDataProcessor()
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