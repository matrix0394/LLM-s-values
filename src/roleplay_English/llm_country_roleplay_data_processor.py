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
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from src.base.ivs_question_processor import IVSQuestionProcessor


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
    Y003_processed: Optional[Dict] = None  # 存储完整的Y003处理结果
    
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
            'Y002_materialist': self.Y002_materialist,
            'Y002': self.Y002_materialist  # 直接添加Y002列（与IVS格式一致）
        }
        
        # 处理Y003的多个值 - 使用base中的统一方法
        if self.Y003_values:
            y003_result = IVSQuestionProcessor.process_y003(self.Y003_values)
            # 保存y003_score（这是PCA分析需要的）
            result['Y003'] = y003_result["y003_score"]
            # 同时保存二进制编码（用于调试和验证）
            for key, value in y003_result["binary_encoding"].items():
                result[key] = value
        else:
            # 如果没有Y003值，设置为NaN
            result['Y003'] = np.nan
            for i in range(1, 12):
                result[f'Y003_{i}'] = 0
                
        return result


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
            # 修正路径：config目录在项目根目录下
            # 从当前文件向上找到项目根目录
            current_path = Path(__file__).parent
            while current_path.name != "LLM's values" and current_path.parent != current_path:
                current_path = current_path.parent
            config_path = current_path / 'config' / 'models' / 'llm_models.json'
            
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
        # 修正路径：config目录在项目根目录下
        # 从data_dir向上找到项目根目录
        current_path = self.data_dir
        while current_path.name != "LLM's values" and current_path.parent != current_path:
            current_path = current_path.parent
        
        cultural_config_path = current_path / 'config' / 'country' / 'cultural_regions.json'
        try:
            with open(cultural_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('country_cultural_mapping', {})
        except Exception as e:
            print(f"加载文化区域配置失败: {e}")
            print(f"尝试的路径: {cultural_config_path}")
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
        # 查找带时间戳的文件（最新的）
        json_files = list(self.roleplay_responses_dir.glob('roleplay_results_*.json'))
        pkl_files = list(self.roleplay_responses_dir.glob('roleplay_results_*.pkl'))
        
        # 如果没有带时间戳的文件，尝试不带时间戳的文件
        if not json_files:
            json_files = [self.roleplay_responses_dir / 'roleplay_results.json']
        if not pkl_files:
            pkl_files = [self.roleplay_responses_dir / 'roleplay_results.pkl']
        
        # 选择最新的文件
        latest_json = None
        latest_pkl = None
        
        if json_files:
            existing_json = [f for f in json_files if f.exists()]
            if existing_json:
                latest_json = max(existing_json, key=lambda x: x.stat().st_mtime)
        
        if pkl_files:
            existing_pkl = [f for f in pkl_files if f.exists()]
            if existing_pkl:
                latest_pkl = max(existing_pkl, key=lambda x: x.stat().st_mtime)
        
        try:
            # 优先使用JSON文件，避免pkl文件的模块依赖问题
            if latest_json and latest_json.exists():
                print(f"📁 加载角色扮演结果: {latest_json.name}")
                with open(latest_json, 'r', encoding='utf-8') as f:
                    return json.load(f)
            elif latest_pkl and latest_pkl.exists():
                print(f"📁 加载角色扮演结果: {latest_pkl.name}")
                print("警告：pkl文件可能有模块依赖问题，建议使用JSON文件")
                with open(latest_pkl, 'rb') as f:
                    return pickle.load(f)
            else:
                print(f"未找到角色扮演结果文件: {self.roleplay_responses_dir}")
                return {}
        except Exception as e:
            print(f"加载角色扮演结果失败: {e}")
            # 如果JSON失败，尝试pkl
            if latest_pkl and latest_pkl.exists():
                try:
                    print("尝试加载pkl文件...")
                    with open(latest_pkl, 'rb') as f:
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
                        processed.Y002_materialist = IVSQuestionProcessor.process_y002(answer[0], answer[1])
                elif question_id == 'Y003':
                    if isinstance(answer, (tuple, list)):
                        processed.Y003_values = list(answer)
                    elif isinstance(answer, int):
                        processed.Y003_values = [answer]
                    
                    # 使用base中的统一Y003处理方法
                    if processed.Y003_values:
                        y003_result = IVSQuestionProcessor.process_y003(processed.Y003_values)
                        # 存储完整的处理结果以备后用
                        processed.Y003_processed = y003_result
            
            processed_responses.append(processed)
        
        print(f"处理完成，得到 {len(processed_responses)} 个处理后的响应")
        return processed_responses
    
    def process_all_roleplay_data(self, merge_with_ivs: bool = True) -> pd.DataFrame:
        """处理所有角色扮演数据，可选择是否与IVS数据合并
        
        Args:
            merge_with_ivs: 是否与真实IVS数据合并
            
        Returns:
            包含所有处理后数据的DataFrame（可能包含IVS数据）
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
            roleplay_df = pd.DataFrame(data_dicts)
            
            # 如果需要，与IVS数据合并
            if merge_with_ivs:
                print("🔄 合并角色扮演数据与真实IVS数据...")
                combined_df = self.merge_with_ivs_data(roleplay_df)
                return combined_df
            else:
                return roleplay_df
        else:
            return pd.DataFrame()
    
    def load_real_ivs_data(self) -> pd.DataFrame:
        """加载真实的IVS数据
        
        Returns:
            真实IVS数据的DataFrame
        """
        try:
            # 从项目根目录查找IVS数据
            current_path = self.data_dir
            while current_path.name != "LLM's values" and current_path.parent != current_path:
                current_path = current_path.parent
            
            ivs_data_path = current_path / "data" / "country_values" / "ivs_df.pkl"
            
            if ivs_data_path.exists():
                ivs_df = pd.read_pickle(ivs_data_path)
                print(f"✅ 加载真实IVS数据: {ivs_df.shape}")
                
                # 添加数据源标识
                ivs_df['data_source'] = 'IVS'
                
                return ivs_df
            else:
                print(f"❌ 未找到IVS数据文件: {ivs_data_path}")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"❌ 加载IVS数据失败: {e}")
            return pd.DataFrame()
    
    def merge_with_ivs_data(self, roleplay_df: pd.DataFrame) -> pd.DataFrame:
        """将角色扮演数据与真实IVS数据合并
        
        Args:
            roleplay_df: 处理后的角色扮演数据
            
        Returns:
            合并后的完整数据集
        """
        try:
            # 加载真实IVS数据
            ivs_df = self.load_real_ivs_data()
            
            if ivs_df.empty:
                print("⚠️ 无法加载IVS数据，只返回角色扮演数据")
                return roleplay_df
            
            # 为角色扮演数据添加数据源标识
            roleplay_df = roleplay_df.copy()
            roleplay_df['data_source'] = 'llm_roleplay'
            
            # 确保两个数据集有相同的列结构
            ivs_questions = ['A008', 'A165', 'E018', 'E025', 'F063', 'F118', 'F120', 'G006', 'Y002', 'Y003']
            
            # 选择IVS数据的相关列
            ivs_selected = ivs_df[['S020', 'S003'] + ivs_questions + ['data_source']].copy()
            ivs_selected = ivs_selected.rename(columns={'S020': 'year', 'S003': 'country_code'})
            
            # 过滤2005年及以后的数据
            ivs_selected = ivs_selected[ivs_selected['year'] >= 2005]
            
            # 选择角色扮演数据的相关列（检查列是否存在）
            roleplay_columns = ['model_name', 'data_source']
            
            # 添加元数据列（如果存在）
            metadata_cols = ['model_region', 'cultural_region']
            for col in metadata_cols:
                if col in roleplay_df.columns:
                    roleplay_columns.append(col)
            
            # 检查country_code列
            if 'country_code' in roleplay_df.columns:
                roleplay_columns.append('country_code')
            elif 'country_name' in roleplay_df.columns:
                roleplay_columns.append('country_name')
            
            # 检查IVS问题列
            available_questions = []
            for q in ivs_questions:
                if q in roleplay_df.columns:
                    # 如果Y003列已经存在（从to_dict()中计算好的），直接使用
                    available_questions.append(q)
                elif q == 'Y002' and 'Y002_materialist' in roleplay_df.columns:
                    # Y002特殊处理
                    available_questions.append('Y002_materialist')
                elif q == 'Y003' and 'Y003' not in roleplay_df.columns:
                    # Y003后备方案：如果Y003列不存在，包含所有二进制编码列用于重建
                    y003_cols = [col for col in roleplay_df.columns if col.startswith('Y003_')]
                    if y003_cols:
                        available_questions.extend(y003_cols)
            
            roleplay_columns.extend(available_questions)
            
            print(f"   📋 角色扮演数据可用列: {available_questions}")
            
            roleplay_selected = roleplay_df[roleplay_columns].copy()
            
            # 统一列名
            if 'country_name' in roleplay_selected.columns and 'country_code' not in roleplay_selected.columns:
                roleplay_selected = roleplay_selected.rename(columns={'country_name': 'country_code'})
            
            # Y002和Y003现在应该已经在to_dict()中计算好并保存了
            # 只需要处理后备方案：如果Y003列不存在，从二进制编码重建
            if 'Y003' not in roleplay_selected.columns:
                y003_cols = [col for col in roleplay_selected.columns if col.startswith('Y003_')]
                if y003_cols:
                    def calc_y003_score(row):
                        """从二进制编码计算Y003分数（后备方案）"""
                        selected = []
                        for col in y003_cols:
                            val = row[col] if col in row.index else 0
                            if pd.notna(val) and val == 1:
                                option_num = int(col.split('_')[1])
                                selected.append(option_num)
                        
                        if not selected:
                            return np.nan
                        
                        result = IVSQuestionProcessor.process_y003(selected)
                        return result["y003_score"]
                    
                    roleplay_selected['Y003'] = roleplay_selected.apply(calc_y003_score, axis=1)
                    roleplay_selected = roleplay_selected.drop(y003_cols, axis=1)
            else:
                # Y003列已存在，删除二进制编码列（如果有的话）
                y003_cols = [col for col in roleplay_selected.columns if col.startswith('Y003_')]
                if y003_cols:
                    roleplay_selected = roleplay_selected.drop(y003_cols, axis=1)
            
            # 确保所有IVS问题列都存在（缺失的用NaN填充）
            for q in ivs_questions:
                if q not in roleplay_selected.columns:
                    roleplay_selected[q] = pd.NA
            
            # 为了合并，需要统一列结构
            # 给IVS数据添加model_name列
            ivs_selected['model_name'] = 'Real_Country'
            
            # 给角色扮演数据添加year列
            roleplay_selected['year'] = 2025  # 使用当前年份
            
            # 合并数据
            combined_df = pd.concat([ivs_selected, roleplay_selected], ignore_index=True)
            
            print(f"✅ 数据合并完成:")
            print(f"   真实IVS数据: {len(ivs_selected)} 条")
            print(f"   角色扮演数据: {len(roleplay_selected)} 条")
            print(f"   合并后总计: {len(combined_df)} 条")
            
            return combined_df
            
        except Exception as e:
            print(f"❌ 数据合并失败: {e}")
            import traceback
            traceback.print_exc()
            return roleplay_df
    
    def create_ivs_compatible_dataframe(self, processed_df: pd.DataFrame = None) -> pd.DataFrame:
        """创建与IVS数据格式兼容的DataFrame（仅包含角色扮演数据）
        
        Args:
            processed_df: 可选的已处理数据，如果为None则重新加载处理
        
        Returns:
            与真实IVS数据格式兼容的DataFrame（仅角色扮演数据，不包含IVS）
        """
        # 如果没有传入数据，则重新加载处理（不合并IVS）
        if processed_df is None:
            processed_df = self.process_all_roleplay_data(merge_with_ivs=False)
        else:
            # 如果传入的是合并后的数据，只提取角色扮演部分
            if 'data_source' in processed_df.columns:
                processed_df = processed_df[processed_df['data_source'] == 'llm_roleplay'].copy()
                # 重置索引以避免索引不匹配问题
                processed_df = processed_df.reset_index(drop=True)
        
        if processed_df.empty:
            return pd.DataFrame()
        
        # 创建兼容格式的DataFrame（使用.values避免索引问题）
        ivs_compatible = pd.DataFrame()
        
        # 添加元数据列
        ivs_compatible['year'] = [2025] * len(processed_df)  # 使用当前年份
        
        # 智能处理country_code列（可能是country_name或country_code）
        if 'country_name' in processed_df.columns:
            ivs_compatible['country_code'] = processed_df['country_name'].values
        elif 'country_code' in processed_df.columns:
            ivs_compatible['country_code'] = processed_df['country_code'].values
        else:
            raise ValueError("processed_df中既没有country_name也没有country_code列")
        
        ivs_compatible['weight'] = [1.0] * len(processed_df)  # 统一权重
        
        # 智能处理可选的元数据列（使用.values避免索引问题）
        if 'model_name' in processed_df.columns:
            ivs_compatible['model_name'] = processed_df['model_name'].values
        else:
            ivs_compatible['model_name'] = 'Unknown'
        
        if 'model_region' in processed_df.columns:
            ivs_compatible['model_region'] = processed_df['model_region'].values
        else:
            print(f"   ⚠️ 警告：model_region列不存在，使用'Unknown'填充")
            ivs_compatible['model_region'] = 'Unknown'
        
        if 'cultural_region' in processed_df.columns:
            ivs_compatible['cultural_region'] = processed_df['cultural_region'].values
        else:
            print(f"   ⚠️ 警告：cultural_region列不存在，使用'Unknown'填充")
            ivs_compatible['cultural_region'] = 'Unknown'
        
        ivs_compatible['data_source'] = ['llm_roleplay'] * len(processed_df)
        
        # 添加IVS问题列（带安全检查，使用.values避免索引问题）
        ivs_questions = ['A008', 'A165', 'E018', 'E025', 'F063', 'F118', 'F120', 'G006']
        for q in ivs_questions:
            if q in processed_df.columns:
                ivs_compatible[q] = processed_df[q].values
            else:
                print(f"   ⚠️ 警告：{q}列不存在，使用NaN填充")
                ivs_compatible[q] = np.nan
        
        # 处理Y002 - 使用物质主义倾向值
        if 'Y002_materialist' in processed_df.columns:
            ivs_compatible['Y002'] = processed_df['Y002_materialist'].values
        elif 'Y002' in processed_df.columns:
            ivs_compatible['Y002'] = processed_df['Y002'].values
        else:
            print(f"   ⚠️ 警告：Y002和Y002_materialist列都不存在，使用NaN填充")
            ivs_compatible['Y002'] = np.nan
        
        # 处理Y003 - 优先使用已经计算好的Y003值（合并数据中已有）
        if 'Y003' in processed_df.columns:
            # 如果已经有Y003列（合并数据中），直接使用
            ivs_compatible['Y003'] = processed_df['Y003'].values
        elif 'Y003_processed' in processed_df.columns:
            # 否则尝试从Y003_processed提取
            def get_y003_score(row):
                y003_proc = row.get('Y003_processed')
                if pd.notna(y003_proc) and isinstance(y003_proc, dict):
                    return y003_proc.get('y003_score', np.nan)
                return np.nan
            ivs_compatible['Y003'] = processed_df.apply(get_y003_score, axis=1).values
        else:
            # 最后，尝试从二进制编码重建
            y003_cols = [col for col in processed_df.columns if col.startswith('Y003_')]
            if y003_cols:
                def calc_from_binary(row):
                    selected = [int(col.split('_')[1]) for col in y003_cols if row.get(col, 0) == 1]
                    if not selected:
                        return np.nan
                    result = IVSQuestionProcessor.process_y003(selected)
                    return result["y003_score"]
                ivs_compatible['Y003'] = processed_df.apply(calc_from_binary, axis=1).values
            else:
                print(f"   ⚠️ 警告：无法找到Y003相关数据，使用NaN填充")
                ivs_compatible['Y003'] = np.nan
        
        return ivs_compatible
    
    def save_processed_data(self, output_path: str = None, merge_with_ivs: bool = True):
        """保存处理后的数据（带时间戳）
        
        Args:
            output_path: 输出文件路径（如果为None，自动生成带时间戳的路径）
            merge_with_ivs: 是否与IVS数据合并
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if output_path is None:
            output_path = self.data_dir / f'llm_roleplay_processed_responses_{timestamp}.pkl'
        
        # 🔄 步骤1: 处理角色扮演数据（可选择是否与IVS合并）
        print(f"\n{'='*60}")
        print("📊 处理角色扮演数据")
        print(f"{'='*60}")
        processed_df = self.process_all_roleplay_data(merge_with_ivs=merge_with_ivs)
        
        if not processed_df.empty:
            # 💾 步骤2: 保存完整数据（含IVS或不含IVS，取决于merge_with_ivs参数）
            print(f"\n💾 保存处理后的完整数据...")
            processed_df.to_pickle(output_path)
            print(f"   ✅ 已保存到: {output_path}")
            
            latest_path = self.data_dir / 'llm_roleplay_processed_responses_latest.pkl'
            processed_df.to_pickle(latest_path)
            print(f"   ✅ 最新版本: {latest_path}")
            
            # 💾 步骤3: 创建并保存IVS兼容格式（传入已处理的数据，避免重复加载）
            print(f"\n🔄 创建IVS兼容格式...")
            ivs_compatible_df = self.create_ivs_compatible_dataframe(processed_df=processed_df)
            
            if not ivs_compatible_df.empty:
                ivs_path = self.data_dir / f'llm_roleplay_processed_responses_ivs_format_{timestamp}.pkl'
                ivs_compatible_df.to_pickle(ivs_path)
                print(f"   ✅ IVS格式已保存: {ivs_path}")
                print(f"   📋 包含列: {len(ivs_compatible_df.columns)} 个")
                if 'cultural_region' in ivs_compatible_df.columns:
                    print(f"   ✅ cultural_region 列已包含")
                
                # 保存IVS格式的最新版本
                ivs_latest_path = self.data_dir / 'llm_roleplay_processed_responses_ivs_format_latest.pkl'
                ivs_compatible_df.to_pickle(ivs_latest_path)
                print(f"   ✅ IVS格式最新版本: {ivs_latest_path}")
            
            print(f"\n{'='*60}")
            print("✅ 数据处理完成")
            print(f"{'='*60}\n")
            
            return processed_df
        else:
            print("❌ 没有数据需要保存")
            return None
    
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
