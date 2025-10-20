"""
改进的多语言角色扮演PCA分析模块
将真实国家数据、英文数据和多语言数据合并进行统一PCA分析
"""

import os
import json
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import warnings
warnings.filterwarnings('ignore')

# 添加项目路径
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from src.core.ppca import PPCA
    from factor_analyzer import Rotator
except ImportError:
    print("警告: 无法导入PPCA或Rotator，将使用标准PCA")
    PPCA = None
    Rotator = None

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from src.base.base_pca_analyzer import BasePCAAnalyzer


class UnifiedMultilingualPCAAnalysis(BasePCAAnalyzer):
    """统一的多语言PCA分析器 - 合并真实国家、英文和多语言数据"""
    
    def __init__(self, data_path: str = "data"):
        # 调用父类构造函数
        super().__init__(data_path=data_path)
        
        # 统一多语言特有的配置
        self.processed_dir = self.data_path / "processed"
        self.results_dir = self.data_path / "results" / "unified_multilingual_pca"
        
        # 确保目录存在
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载统一分析特有的数据（基类已有country_codes）
        self.cultural_regions = self._load_cultural_regions()
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
    
    def _load_cultural_regions(self) -> Dict:
        """加载文化区域配置"""
        possible_paths = [
            Path("config/cultural_regions.json"),
            Path("../config/cultural_regions.json"),
            Path("../../config/cultural_regions.json")
        ]
        
        for config_path in possible_paths:
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        
        print("警告: 未找到文化区域配置文件")
        return {}
    
    def load_additional_data(self) -> pd.DataFrame:
        """加载额外数据（统一多语言数据）- 实现基类抽象方法"""
        return self.combine_all_data()
    
    def combine_data(self) -> pd.DataFrame:
        """合并数据（统一实现）- 实现基类抽象方法"""
        return self.combine_all_data()
    
    def load_real_country_data(self) -> pd.DataFrame:
        """加载真实国家IVS数据"""
        print("📊 加载真实国家IVS数据...")
        
        # 加载原始IVS数据
        ivs_file = self.processed_dir / "ivs_df.pkl"
        if not ivs_file.exists():
            raise FileNotFoundError(f"未找到IVS数据文件: {ivs_file}")
        
        ivs_df = pd.read_pickle(ivs_file)
        print(f"原始IVS数据形状: {ivs_df.shape}")
        
        # 选择需要的列
        meta_col = ['S003', 'S020', 'S017']  # country_code, year, weight
        required_cols = meta_col + self.iv_qns
        
        # 检查列是否存在
        missing_cols = [col for col in required_cols if col not in ivs_df.columns]
        if missing_cols:
            print(f"警告: 缺少列 {missing_cols}")
            available_cols = [col for col in required_cols if col in ivs_df.columns]
            subset_ivs_df = ivs_df[available_cols].copy()
        else:
            subset_ivs_df = ivs_df[required_cols].copy()
        
        # 重命名列
        rename_dict = {'S020': 'year', 'S003': 'country_code', 'S017': 'weight'}
        subset_ivs_df = subset_ivs_df.rename(columns=rename_dict)
        
        # 过滤2005年及以后的数据
        if 'year' in subset_ivs_df.columns:
            subset_ivs_df = subset_ivs_df[subset_ivs_df['year'] >= 2005]
        
        # 至少需要6个问题的答案
        available_iv_qns = [col for col in self.iv_qns if col in subset_ivs_df.columns]
        subset_ivs_df = subset_ivs_df.dropna(subset=available_iv_qns, thresh=min(6, len(available_iv_qns)))
        
        # 添加数据源标识
        subset_ivs_df['data_source'] = 'real_country'
        subset_ivs_df['model_name'] = 'real'
        subset_ivs_df['language'] = 'real'
        
        print(f"处理后的真实国家数据: {subset_ivs_df.shape}")
        return subset_ivs_df
    
    def load_english_roleplay_data(self) -> pd.DataFrame:
        """加载英文角色扮演数据"""
        print("🇺🇸 加载英文角色扮演数据...")
        
        # 加载英文角色扮演的原始IVS格式数据
        english_file = self.processed_dir / "llm_roleplay_processed_responses_ivs_format.pkl"
        if not english_file.exists():
            print("警告: 未找到英文角色扮演数据")
            return pd.DataFrame()
        
        english_df = pd.read_pickle(english_file)
        print(f"英文角色扮演数据形状: {english_df.shape}")
        
        # 筛选目标国家和模型
        target_countries = ["China", "Russian Federation", "Mexico", "Egypt"]
        target_models = ["openai/gpt-4o-mini", "google/gemini-2.0-flash-001"]
        
        # 创建筛选条件
        country_mask = english_df['country_code'].isin(target_countries)
        model_mask = english_df['model_name'].str.contains('|'.join([m.split('/')[-1] for m in target_models]))
        
        filtered_english = english_df[country_mask & model_mask].copy()
        
        # 转换国家名称为数字代码
        if 'country_code' in filtered_english.columns:
            filtered_english['country_code'] = filtered_english['country_code'].apply(self._get_country_numeric_code)
        
        # 添加标识
        filtered_english['data_source'] = 'english_roleplay'
        filtered_english['language'] = 'en'
        
        print(f"筛选后的英文数据: {filtered_english.shape}")
        return filtered_english
    
    def load_multilingual_data(self) -> pd.DataFrame:
        """加载多语言数据"""
        print("🌍 加载多语言数据...")
        
        # 首先尝试加载已处理的IVS格式数据
        ml_files = list(self.processed_dir.glob("multilingual_roleplay_ivs_format_*.pkl"))
        if ml_files:
            latest_file = max(ml_files, key=lambda x: x.stat().st_mtime)
            multilingual_df = pd.read_pickle(latest_file)
            print(f"加载已处理的多语言数据: {multilingual_df.shape}")
            return multilingual_df
        
        # 如果没有已处理数据，尝试从原始访谈数据处理
        print("未找到已处理数据，尝试从原始访谈数据处理...")
        
        # 查找原始多语言访谈数据
        raw_ml_dirs = [
            self.data_path / "results" / "multilingual_vs_english_experiment",
            self.data_path / "results" / "simple_multilingual_test",
            self.data_path / "results" / "multilingual_roleplay"
        ]
        
        raw_files = []
        for dir_path in raw_ml_dirs:
            if dir_path.exists():
                raw_files.extend(list(dir_path.glob("*interviews*.json")))
                raw_files.extend(list(dir_path.glob("multilingual_roleplay*.json")))
        
        if not raw_files:
            print("警告: 未找到多语言原始数据")
            return pd.DataFrame()
        
        # 使用最新的原始数据文件
        latest_raw_file = max(raw_files, key=lambda x: x.stat().st_mtime)
        print(f"找到原始数据文件: {latest_raw_file}")
        
        # 处理原始数据
        multilingual_df = self._process_raw_multilingual_data(latest_raw_file)
        
        print(f"处理后的多语言数据形状: {multilingual_df.shape}")
        return multilingual_df
    
    def _process_raw_multilingual_data(self, raw_file: Path) -> pd.DataFrame:
        """处理原始多语言访谈数据"""
        print(f"处理原始多语言数据: {raw_file}")
        
        with open(raw_file, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        multilingual_data = []
        
        # 处理每个访谈结果
        for result in raw_data.get('results', []):
            # 将国家名称转换为数字代码
            country_name = result.get('country', '')
            country_code = self._get_country_numeric_code(country_name)
            
            # 基本信息
            ivs_row = {
                "country_code": country_code,
                "year": 2024,
                "weight": 1.0,
                "data_source": "multilingual_roleplay",
                "model_name": result.get('model', ''),
                "language": result.get('language', ''),
                "entity_id": f"{result.get('model', '')}_{country_name}_{result.get('language', '')}"
            }
            
            # 处理每个问题的回答
            for response in result.get('responses', []):
                question_id = response.get('question_id', '')
                processed_response = response.get('processed_response', '')
                
                if question_id in self.iv_qns:
                    # 转换为数值
                    numeric_value = self._convert_response_to_numeric(question_id, processed_response)
                    ivs_row[question_id] = numeric_value
            
            # 确保所有IVS问题列都存在
            for col in self.iv_qns:
                if col not in ivs_row:
                    ivs_row[col] = np.nan
            
            multilingual_data.append(ivs_row)
        
        return pd.DataFrame(multilingual_data)
    
    def _convert_response_to_numeric(self, question_id: str, response: str) -> float:
        """将回答转换为数值 - 使用与英文数据相同的标准化方式"""
        if not response or response.strip() == '':
            return np.nan
        
        try:
            if question_id in ["Y002", "Y003"]:
                # 多选题，使用原始值而不是标准化
                values = [int(x.strip()) for x in response.split()]
                if question_id == "Y002" and len(values) >= 2:
                    return float(values[0])  # 直接返回第一个选择
                elif question_id == "Y003" and len(values) >= 1:
                    return float(len(values))  # 返回选择数量
                else:
                    return np.nan
            else:
                # 单选题 - 直接返回原始数值，不进行标准化
                value = int(response.strip())
                return float(value)
        except:
            return np.nan
    
    def _get_country_numeric_code(self, country_name: str) -> str:
        """将国家名称转换为数字代码"""
        if not hasattr(self, 'country_codes') or self.country_codes.empty:
            return country_name
        
        # 直接匹配
        match = self.country_codes[self.country_codes['Country'] == country_name]
        if not match.empty:
            return str(match.iloc[0]['Numeric'])
        
        # 处理特殊情况 - 使用正确的数字代码
        name_mapping = {
            'China': '156',
            'Russian Federation': '643',  # 从上面的输出可以看到Russia是643
            'Egypt': '818',
            'Mexico': '484'
        }
        
        if country_name in name_mapping:
            return name_mapping[country_name]
        
        # 如果都找不到，返回原名称
        print(f"警告: 无法找到国家 '{country_name}' 的数字代码")
        return country_name
    
    def combine_all_data(self) -> pd.DataFrame:
        """合并所有数据"""
        print("\\n🔄 合并所有数据...")
        
        # 加载各类数据
        real_data = self.load_real_country_data()
        english_data = self.load_english_roleplay_data()
        multilingual_data = self.load_multilingual_data()
        
        all_datasets = []
        
        # 处理真实国家数据
        if not real_data.empty:
            # 确保有必要的列
            for col in ['country_code', 'year', 'weight', 'data_source']:
                if col not in real_data.columns:
                    if col == 'country_code':
                        real_data[col] = 'Unknown'
                    elif col == 'year':
                        real_data[col] = 2020
                    elif col == 'weight':
                        real_data[col] = 1.0
                    elif col == 'data_source':
                        real_data[col] = 'real_country'
            
            all_datasets.append(real_data)
            print(f"✅ 真实国家数据: {len(real_data)} 行")
        
        # 处理英文数据
        if not english_data.empty:
            # 标准化列名
            english_data_clean = english_data.copy()
            
            # 确保有必要的列
            required_cols = ['country_code', 'year', 'weight', 'data_source', 'model_name']
            for col in required_cols:
                if col not in english_data_clean.columns:
                    if col == 'year':
                        english_data_clean[col] = 2024
                    elif col == 'weight':
                        english_data_clean[col] = 1.0
                    elif col == 'data_source':
                        english_data_clean[col] = 'english_roleplay'
            
            all_datasets.append(english_data_clean)
            print(f"✅ 英文角色扮演数据: {len(english_data_clean)} 行")
        
        # 处理多语言数据
        if not multilingual_data.empty:
            # 标准化列名
            multilingual_data_clean = multilingual_data.copy()
            
            # 确保有必要的列
            required_cols = ['country_code', 'year', 'weight', 'data_source', 'model_name', 'language']
            for col in required_cols:
                if col not in multilingual_data_clean.columns:
                    if col == 'year':
                        multilingual_data_clean[col] = 2024
                    elif col == 'weight':
                        multilingual_data_clean[col] = 1.0
                    elif col == 'data_source':
                        multilingual_data_clean[col] = 'multilingual_roleplay'
            
            all_datasets.append(multilingual_data_clean)
            print(f"✅ 多语言角色扮演数据: {len(multilingual_data_clean)} 行")
        
        if not all_datasets:
            raise ValueError("没有找到任何有效数据")
        
        # 合并数据
        combined_data = pd.concat(all_datasets, ignore_index=True, sort=False)
        
        # 确保所有IVS问题列都存在
        for col in self.iv_qns:
            if col not in combined_data.columns:
                combined_data[col] = np.nan
        
        print(f"\\n✅ 合并完成: {combined_data.shape}")
        print(f"   数据源分布:")
        for source in combined_data['data_source'].value_counts().items():
            print(f"     {source[0]}: {source[1]} 行")
        
        self.combined_data = combined_data
        return combined_data
    
    def perform_unified_pca(self) -> pd.DataFrame:
        """执行统一PCA分析"""
        if not hasattr(self, 'combined_data') or self.combined_data is None:
            raise ValueError("请先合并数据")
        
        print("\\n🔍 执行统一PCA分析...")
        
        # 设置随机种子
        np.random.seed(42)
        
        # 准备PCA数据
        data_for_pca = self.combined_data[self.iv_qns].to_numpy()
        
        # 检查数据有效性
        valid_rows = ~np.isnan(data_for_pca).all(axis=1)
        if not valid_rows.any():
            raise ValueError("没有有效的数据行用于PCA分析")
        
        print(f"用于PCA的有效行数: {valid_rows.sum()}/{len(valid_rows)}")
        
        # 使用PPCA进行分析（如果可用）
        if PPCA is not None and Rotator is not None:
            print("使用PPCA + Varimax旋转...")
            ppca = PPCA()
            ppca.fit(data_for_pca, d=2, min_obs=1, verbose=True)
            
            # 转换数据
            principal_components = ppca.transform()
            
            # 应用varimax旋转
            rotator = Rotator(method='varimax')
            rotated_components = rotator.fit_transform(principal_components)
            
            # 创建结果DataFrame
            ppca_df = pd.DataFrame(rotated_components, columns=["PC1", "PC2"])
            
            method_used = "PPCA + Varimax"
            
        else:
            print("使用标准PCA...")
            # 删除包含缺失值的行
            clean_data = data_for_pca[valid_rows]
            
            # 标准化
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(clean_data)
            
            # PCA
            pca = PCA(n_components=2)
            pca_coords = pca.fit_transform(scaled_data)
            
            # 为所有数据创建坐标（缺失数据用NaN填充）
            full_coords = np.full((len(data_for_pca), 2), np.nan)
            full_coords[valid_rows] = pca_coords
            
            ppca_df = pd.DataFrame(full_coords, columns=["PC1", "PC2"])
            method_used = "StandardPCA"
        
        # 重新缩放主成分分数（与真实数据保持一致）
        ppca_df['PC1_rescaled'] = (self.pc_rescale_params['PC1'][0] * ppca_df['PC1'] + 
                                  self.pc_rescale_params['PC1'][1])
        ppca_df['PC2_rescaled'] = (self.pc_rescale_params['PC2'][0] * ppca_df['PC2'] + 
                                  self.pc_rescale_params['PC2'][1])
        
        # 添加元数据 - 确保关键列被保留
        metadata_cols = ['country_code', 'year', 'data_source', 'model_name', 'language']
        for col in metadata_cols:
            if col in self.combined_data.columns:
                ppca_df[col] = self.combined_data[col].values
                print(f"  ✅ 保留列: {col}")
            else:
                # 不设置默认值，让下游代码知道这列缺失
                print(f"  ⚠️ 缺失列: {col}")
        
        # 合并国家元数据
        if not self.country_codes.empty and 'Numeric' in self.country_codes.columns:
            # 确保数据类型匹配
            ppca_df['country_code'] = ppca_df['country_code'].astype(str)
            self.country_codes['Numeric'] = self.country_codes['Numeric'].astype(str)
            
            ppca_df = ppca_df.merge(
                self.country_codes, 
                left_on='country_code', 
                right_on='Numeric', 
                how='left'
            )
        
        # 过滤掉无效的主成分分数
        self.pca_results = ppca_df.dropna(subset=['PC1_rescaled', 'PC2_rescaled'])
        
        # 确保country_code列为字符串格式，去掉小数点
        if 'country_code' in self.pca_results.columns:
            self.pca_results['country_code'] = self.pca_results['country_code'].astype(str)
            # 去掉.0后缀（如156.0 -> 156）
            self.pca_results['country_code'] = self.pca_results['country_code'].str.replace('.0', '', regex=False)
        
        print(f"\\n✅ 统一PCA分析完成:")
        print(f"   方法: {method_used}")
        print(f"   有效样本: {len(self.pca_results)}/{len(ppca_df)}")
        
        # 显示各数据源的样本数
        print(f"   各数据源样本数:")
        for source in self.pca_results['data_source'].value_counts().items():
            print(f"     {source[0]}: {source[1]} 个")
        
        return self.pca_results
    
    def calculate_distances_unified(self) -> Dict:
        """在统一PCA空间中计算距离"""
        if not hasattr(self, 'pca_results') or self.pca_results is None:
            raise ValueError("请先执行PCA分析")
        
        print("\\n📏 在统一PCA空间中计算距离...")
        
        # 分离不同类型的数据
        real_data = self.pca_results[self.pca_results['data_source'] == 'real_country']
        english_data = self.pca_results[self.pca_results['data_source'] == 'english_roleplay']
        multilingual_data = self.pca_results[self.pca_results['data_source'] == 'multilingual_roleplay']
        
        print(f"数据分布: 真实={len(real_data)}, 英文={len(english_data)}, 多语言={len(multilingual_data)}")
        
        distance_results = {
            "multilingual_vs_real": {},
            "english_vs_real": {},
            "multilingual_vs_english": {},
            "summary_statistics": {}
        }
        
        # 1. 多语言 vs 真实国家
        ml_distances = []
        for _, ml_row in multilingual_data.iterrows():
            country = ml_row['country_code']
            
            # 找到对应的真实国家数据
            real_country = real_data[real_data['country_code'] == country]
            if len(real_country) > 0:
                # 使用平均值（如果有多个样本）
                real_pc1 = real_country['PC1_rescaled'].mean()
                real_pc2 = real_country['PC2_rescaled'].mean()
                
                ml_pc1 = ml_row['PC1_rescaled']
                ml_pc2 = ml_row['PC2_rescaled']
                
                distance = np.sqrt((ml_pc1 - real_pc1)**2 + (ml_pc2 - real_pc2)**2)
                ml_distances.append(distance)
                
                key = f"{ml_row['model_name']}_{country}_{ml_row['language']}"
                distance_results["multilingual_vs_real"][key] = {
                    "distance": distance,
                    "multilingual": {"pc1": ml_pc1, "pc2": ml_pc2},
                    "real": {"pc1": real_pc1, "pc2": real_pc2},
                    "model": ml_row['model_name'],
                    "country": country,
                    "language": ml_row['language']
                }
        
        # 2. 英文 vs 真实国家
        eng_distances = []
        for _, eng_row in english_data.iterrows():
            country = eng_row['country_code']
            
            # 找到对应的真实国家数据
            real_country = real_data[real_data['country_code'] == country]
            if len(real_country) > 0:
                real_pc1 = real_country['PC1_rescaled'].mean()
                real_pc2 = real_country['PC2_rescaled'].mean()
                
                eng_pc1 = eng_row['PC1_rescaled']
                eng_pc2 = eng_row['PC2_rescaled']
                
                distance = np.sqrt((eng_pc1 - real_pc1)**2 + (eng_pc2 - real_pc2)**2)
                eng_distances.append(distance)
                
                key = f"{eng_row['model_name']}_{country}"
                distance_results["english_vs_real"][key] = {
                    "distance": distance,
                    "english": {"pc1": eng_pc1, "pc2": eng_pc2},
                    "real": {"pc1": real_pc1, "pc2": real_pc2},
                    "model": eng_row['model_name'],
                    "country": country
                }
        
        # 3. 多语言 vs 英文
        ml_vs_eng_distances = []
        for _, ml_row in multilingual_data.iterrows():
            country = ml_row['country_code']
            model = ml_row['model_name']
            
            # 找到对应的英文数据
            eng_match = english_data[
                (english_data['country_code'] == country) & 
                (english_data['model_name'] == model)
            ]
            
            if len(eng_match) > 0:
                eng_row = eng_match.iloc[0]
                
                ml_pc1 = ml_row['PC1_rescaled']
                ml_pc2 = ml_row['PC2_rescaled']
                eng_pc1 = eng_row['PC1_rescaled']
                eng_pc2 = eng_row['PC2_rescaled']
                
                distance = np.sqrt((ml_pc1 - eng_pc1)**2 + (ml_pc2 - eng_pc2)**2)
                ml_vs_eng_distances.append(distance)
                
                key = f"{model}_{country}_{ml_row['language']}"
                distance_results["multilingual_vs_english"][key] = {
                    "distance": distance,
                    "multilingual": {"pc1": ml_pc1, "pc2": ml_pc2},
                    "english": {"pc1": eng_pc1, "pc2": eng_pc2},
                    "model": model,
                    "country": country,
                    "language": ml_row['language']
                }
        
        # 4. 统计摘要
        if ml_distances:
            distance_results["summary_statistics"]["multilingual_vs_real"] = {
                "mean_distance": np.mean(ml_distances),
                "std_distance": np.std(ml_distances),
                "min_distance": np.min(ml_distances),
                "max_distance": np.max(ml_distances),
                "count": len(ml_distances),
                "all_distances": ml_distances
            }
        
        if eng_distances:
            distance_results["summary_statistics"]["english_vs_real"] = {
                "mean_distance": np.mean(eng_distances),
                "std_distance": np.std(eng_distances),
                "min_distance": np.min(eng_distances),
                "max_distance": np.max(eng_distances),
                "count": len(eng_distances),
                "all_distances": eng_distances
            }
        
        if ml_vs_eng_distances:
            distance_results["summary_statistics"]["multilingual_vs_english"] = {
                "mean_distance": np.mean(ml_vs_eng_distances),
                "std_distance": np.std(ml_vs_eng_distances),
                "min_distance": np.min(ml_vs_eng_distances),
                "max_distance": np.max(ml_vs_eng_distances),
                "count": len(ml_vs_eng_distances),
                "all_distances": ml_vs_eng_distances
            }
        
        print(f"✅ 距离计算完成:")
        print(f"   多语言vs真实: {len(ml_distances)} 个比较")
        print(f"   英文vs真实: {len(eng_distances)} 个比较")
        print(f"   多语言vs英文: {len(ml_vs_eng_distances)} 个比较")
        
        return distance_results
    
    def create_unified_visualization(self, suffix: str = None):
        """创建统一PCA空间的可视化"""
        if suffix is None:
            suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("\\n📊 创建统一PCA空间可视化...")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # 颜色和标记设置
        colors = {
            'real_country': '#2E8B57',      # 深绿色
            'english_roleplay': '#4169E1',   # 蓝色
            'multilingual_roleplay': '#DC143C'  # 红色
        }
        
        markers = {
            'real_country': 'o',
            'english_roleplay': 's', 
            'multilingual_roleplay': '^'
        }
        
        # 图1：按数据源分类
        for source in self.pca_results['data_source'].unique():
            data = self.pca_results[self.pca_results['data_source'] == source]
            ax1.scatter(data['PC1_rescaled'], data['PC2_rescaled'],
                       c=colors.get(source, 'gray'), 
                       marker=markers.get(source, 'o'),
                       s=100, alpha=0.7, label=source)
        
        ax1.set_xlabel('PC1 (传统 vs 世俗理性价值观)')
        ax1.set_ylabel('PC2 (生存 vs 自我表达价值观)')
        ax1.set_title('统一PCA空间 - 按数据源分类')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 图2：多语言数据按语言分类
        ml_data = self.pca_results[self.pca_results['data_source'] == 'multilingual_roleplay']
        if not ml_data.empty:
            language_colors = {
                'zh-cn': '#FF6B6B',
                'ru': '#4ECDC4', 
                'es-la': '#45B7D1',
                'ar': '#FFA07A'
            }
            
            for language in ml_data['language'].unique():
                if language != 'Unknown':
                    lang_data = ml_data[ml_data['language'] == language]
                    ax2.scatter(lang_data['PC1_rescaled'], lang_data['PC2_rescaled'],
                               c=language_colors.get(language, 'gray'),
                               s=100, alpha=0.7, label=language)
        
        # 添加真实国家数据作为参考
        real_data = self.pca_results[self.pca_results['data_source'] == 'real_country']
        if not real_data.empty:
            ax2.scatter(real_data['PC1_rescaled'], real_data['PC2_rescaled'],
                       c='black', marker='*', s=200, alpha=0.8, label='真实国家')
        
        ax2.set_xlabel('PC1 (传统 vs 世俗理性价值观)')
        ax2.set_ylabel('PC2 (生存 vs 自我表达价值观)')
        ax2.set_title('统一PCA空间 - 多语言 vs 真实国家')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / f'unified_pca_visualization_{suffix}.png',
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ 可视化已保存")
    
    def save_unified_results(self, distance_results: Dict, suffix: str = None) -> Dict:
        """保存统一分析结果"""
        if suffix is None:
            suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存PCA结果
        pca_file = self.results_dir / f'unified_pca_results_{suffix}.pkl'
        with open(pca_file, 'wb') as f:
            pickle.dump(self.pca_results, f)
        
        # 保存CSV格式
        csv_file = self.results_dir / f'unified_pca_results_{suffix}.csv'
        self.pca_results.to_csv(csv_file, index=False, encoding='utf-8')
        
        # 保存距离分析结果
        distance_file = self.results_dir / f'unified_distance_analysis_{suffix}.json'
        with open(distance_file, 'w', encoding='utf-8') as f:
            json.dump(distance_results, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\\n💾 统一分析结果已保存:")
        print(f"   PCA结果: {pca_file}")
        print(f"   CSV格式: {csv_file}")
        print(f"   距离分析: {distance_file}")
        
        return {
            "pca_file": pca_file,
            "csv_file": csv_file,
            "distance_file": distance_file
        }
    
    def run_unified_analysis(self) -> Dict:
        """运行完整的统一分析"""
        print("🔬 统一多语言PCA分析")
        print("=" * 60)
        
        try:
            # 1. 合并所有数据
            combined_data = self.combine_all_data()
            
            # 2. 执行统一PCA
            pca_results = self.perform_unified_pca()
            
            # 3. 计算距离
            distance_results = self.calculate_distances_unified()
            
            # 4. 创建可视化
            self.create_unified_visualization()
            
            # 5. 保存结果
            file_paths = self.save_unified_results(distance_results)
            
            # 6. 生成摘要报告
            report = self.generate_unified_report(distance_results)
            
            print("\\n" + "=" * 60)
            print("🎯 统一分析结果摘要")
            print("=" * 60)
            
            # 显示主要结果
            ml_stats = distance_results["summary_statistics"].get("multilingual_vs_real", {})
            eng_stats = distance_results["summary_statistics"].get("english_vs_real", {})
            
            if ml_stats and eng_stats:
                ml_mean = ml_stats["mean_distance"]
                eng_mean = eng_stats["mean_distance"]
                improvement = eng_mean - ml_mean
                improvement_pct = (improvement / eng_mean * 100) if eng_mean > 0 else 0
                
                print(f"📊 距离对比 (统一PCA空间):")
                print(f"   多语言平均距离: {ml_mean:.3f}")
                print(f"   英文平均距离: {eng_mean:.3f}")
                print(f"   改进幅度: {improvement:.3f} ({improvement_pct:.1f}%)")
                print(f"   更好的方法: {'多语言' if ml_mean < eng_mean else '英文'}")
            
            print(f"\\n📁 结果文件: {self.results_dir}")
            
            return {
                "success": True,
                "pca_results": pca_results,
                "distance_results": distance_results,
                "file_paths": file_paths,
                "report": report
            }
            
        except Exception as e:
            print(f"❌ 统一分析失败: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    def generate_unified_report(self, distance_results: Dict) -> Dict:
        """生成统一分析报告"""
        report = {
            "analysis_type": "unified_multilingual_pca",
            "timestamp": datetime.now().isoformat(),
            "method": "统一PCA空间分析",
            "description": "将真实国家、英文角色扮演和多语言角色扮演数据合并在同一PCA空间中进行公平比较",
            "data_sources": {
                "real_country": len(self.pca_results[self.pca_results['data_source'] == 'real_country']),
                "english_roleplay": len(self.pca_results[self.pca_results['data_source'] == 'english_roleplay']),
                "multilingual_roleplay": len(self.pca_results[self.pca_results['data_source'] == 'multilingual_roleplay'])
            },
            "distance_analysis": distance_results,
            "key_findings": [],
            "recommendations": []
        }
        
        # 提取关键发现
        ml_stats = distance_results["summary_statistics"].get("multilingual_vs_real", {})
        eng_stats = distance_results["summary_statistics"].get("english_vs_real", {})
        
        if ml_stats and eng_stats:
            ml_mean = ml_stats["mean_distance"]
            eng_mean = eng_stats["mean_distance"]
            
            if ml_mean < eng_mean:
                report["key_findings"].append(
                    f"✅ 在统一PCA空间中，多语言方法表现更好，平均距离减少 {eng_mean - ml_mean:.3f}"
                )
                report["recommendations"].append("建议在跨文化研究中优先使用多语言方法")
            else:
                report["key_findings"].append(
                    f"⚠️ 在统一PCA空间中，英文方法仍表现更好，多语言方法需要进一步改进"
                )
                report["recommendations"].append("需要优化多语言提示词和文化背景描述")
        
        return report


def main():
    """主函数"""
    analyzer = UnifiedMultilingualPCAAnalysis()
    
    try:
        result = analyzer.run_complete_unified_analysis()
        
        if result["success"]:
            print("\\n✅ 统一多语言PCA分析完成！")
            print("\\n这是在统一PCA空间中的公平比较结果。")
        else:
            print(f"\\n❌ 分析失败: {result['error']}")
        
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
