"""
统一的PCA分析基类
消除项目中多个PCA分析类的重复代码
"""

import pandas as pd
import numpy as np
import os
from typing import List, Tuple, Optional, Dict, Any
from abc import ABC, abstractmethod
from src.country_values.ppca import PPCA
from factor_analyzer import Rotator
import pickle
from pathlib import Path


class BasePCAAnalyzer(ABC):
    """PCA分析基类 - 提供通用的PCA分析功能"""
    
    def __init__(self, data_path: str = "../data"):
        """初始化PCA分析器
        
        Args:
            data_path: 数据路径
        """
        self.data_path = Path(data_path)
        
        # IVS问题列表
        self.iv_qns = ["A008", "A165", "E018", "E025", "F063", "F118", "F120", "G006", "Y002", "Y003"]
        self.meta_col = ["S020", "S003"]  # year, country_code
        self.weights = ["S017"]
        
        # 主成分重新缩放参数（与旧代码完全一致）
        self.pc_rescale_params = {
            'PC1': (1.81, 0.38), 
            'PC2': (1.61, -0.01)
        }
        
        # 数据存储
        self.ivs_df = None
        self.country_codes = None
        self.combined_data = None
        self.pca_results = None
    
    def load_base_data(self) -> bool:
        """加载基础数据（IVS数据和国家代码）"""
        try:
            # 加载IVS数据
            ivs_path = self.data_path / "ivs_df.pkl"
            if ivs_path.exists():
                self.ivs_df = pd.read_pickle(ivs_path)
                print(f"✅ 加载IVS数据: {self.ivs_df.shape}")
            else:
                print(f"❌ IVS数据文件不存在: {ivs_path}")
                return False
            
            # 加载国家代码数据
            country_codes_path = self.data_path / "country_codes.pkl"
            if country_codes_path.exists():
                self.country_codes = pd.read_pickle(country_codes_path)
                print(f"✅ 加载国家代码: {self.country_codes.shape}")
            else:
                print(f"❌ 国家代码文件不存在: {country_codes_path}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ 加载基础数据失败: {e}")
            return False
    
    def prepare_ivs_data(self) -> pd.DataFrame:
        """准备IVS数据（标准化处理）"""
        if self.ivs_df is None:
            raise ValueError("请先加载IVS数据")
        
        # 选择需要的列
        all_columns = self.meta_col + self.weights + self.iv_qns
        subset_ivs_df = self.ivs_df[all_columns].copy()
        
        # 重命名列
        subset_ivs_df = subset_ivs_df.rename(columns={
            'S020': 'year', 
            'S003': 'country_code', 
            'S017': 'weight'
        })
        
        # 过滤2005年及以后的数据
        subset_ivs_df = subset_ivs_df[subset_ivs_df['year'] >= 2005]
        
        # 删除缺失值过多的行
        subset_ivs_df = subset_ivs_df.dropna(subset=self.iv_qns, thresh=6)
        
        return subset_ivs_df
    
    @abstractmethod
    def load_additional_data(self) -> pd.DataFrame:
        """加载额外数据（子类实现）
        
        Returns:
            额外数据的DataFrame
        """
        pass
    
    @abstractmethod
    def combine_data(self) -> pd.DataFrame:
        """合并数据（子类实现）
        
        Returns:
            合并后的数据DataFrame
        """
        pass
    
    def perform_pca_analysis(self, data: pd.DataFrame = None) -> pd.DataFrame:
        """执行PCA分析（通用实现）
        
        Args:
            data: 要分析的数据，如果为None则使用self.combined_data
            
        Returns:
            PCA分析结果
        """
        if data is None:
            if self.combined_data is None:
                raise ValueError("请先合并数据或提供数据参数")
            data = self.combined_data
        
        print("🔄 开始PCA分析...")
        
        # 设置随机种子确保结果可重现
        np.random.seed(42)
        
        # 准备PCA数据
        data_for_pca = data[self.iv_qns].to_numpy()
        
        # 检查数据有效性
        valid_rows = ~np.isnan(data_for_pca).all(axis=1)
        if not valid_rows.any():
            raise ValueError("没有有效的数据行用于PCA分析")
        
        print(f"📊 用于PCA的有效行数: {valid_rows.sum()}/{len(valid_rows)}")
        
        # 检查数据量是否足够进行PCA分析
        min_samples_required = max(3, data_for_pca.shape[1] // 10)  # 至少3个样本，或特征数的1/10
        if valid_rows.sum() < min_samples_required:
            print(f"⚠️ 数据量不足进行PCA分析: {valid_rows.sum()} < {min_samples_required}")
            print("   建议增加repeat_count或添加更多语言-国家对")
            
            # 返回空结果而不是崩溃
            return pd.DataFrame(columns=['PC1', 'PC2', 'country_code', 'country_name', 'data_source'])
        
        # 使用PPCA进行分析
        ppca = PPCA()
        ppca.fit(data_for_pca, d=2, min_obs=1, verbose=True)
        
        # 转换数据
        principal_components = ppca.transform()
        
        # 应用varimax旋转（完全按照旧代码逻辑）
        rotator = Rotator(method='varimax')
        rotated_components = rotator.fit_transform(principal_components)
        
        # 创建结果DataFrame
        ppca_df = pd.DataFrame(rotated_components, columns=["PC1", "PC2"])
        
        # 重新缩放主成分分数
        ppca_df['PC1_rescaled'] = (
            self.pc_rescale_params['PC1'][0] * ppca_df['PC1'] + 
            self.pc_rescale_params['PC1'][1]
        )
        ppca_df['PC2_rescaled'] = (
            self.pc_rescale_params['PC2'][0] * ppca_df['PC2'] + 
            self.pc_rescale_params['PC2'][1]
        )
        
        # 添加基本元数据（完全按照旧代码逻辑）
        ppca_df["country_code"] = data["country_code"].values
        if "year" in data.columns:
            ppca_df["year"] = data["year"].values
        
        # 添加其他可用的元数据
        for col in ["data_source", "model_name", "cultural_region", "language"]:
            if col in data.columns:
                ppca_df[col] = data[col].values
        
        # 合并国家元数据（修复数据类型不匹配问题）
        if self.country_codes is not None:
            # 确保country_code列的数据类型一致
            # 处理浮点数字符串格式（如'100.0' -> '100'）
            def clean_country_code(code):
                try:
                    if pd.isna(code):
                        return str(code)
                    # 转换为浮点数再转换为整数再转换为字符串
                    return str(int(float(str(code))))
                except (ValueError, TypeError):
                    return str(code)
            
            ppca_df['country_code_clean'] = ppca_df['country_code'].apply(clean_country_code)
            self.country_codes['Numeric_str'] = self.country_codes['Numeric'].astype(str)
            ppca_df = ppca_df.merge(self.country_codes, left_on='country_code_clean', right_on='Numeric_str', how='left')
            
            # 保留原始country_code列，添加清理后的作为备份
            ppca_df['country_code_original'] = ppca_df['country_code']
            ppca_df['country_code'] = ppca_df['country_code_clean']
        
        # 过滤掉无效的主成分分数
        self.pca_results = ppca_df.dropna(subset=['PC1_rescaled', 'PC2_rescaled'])
        
        print(f"✅ PCA分析完成: {len(self.pca_results)} 个有效观测值")
        return self.pca_results
    
    def calculate_entity_scores(self, group_by: List[str] = None) -> pd.DataFrame:
        """计算实体级别的平均分数
        
        Args:
            group_by: 分组列名列表，默认为['country_code']
            
        Returns:
            实体平均分数DataFrame
        """
        if self.pca_results is None:
            raise ValueError("请先执行PCA分析")
        
        if group_by is None:
            group_by = ['country_code']
        
        # 添加data_source到分组列中（如果存在且不在group_by中）
        if 'data_source' in self.pca_results.columns and 'data_source' not in group_by:
            group_by = group_by + ['data_source']
        
        # 计算分组平均分数，同时保留其他重要列
        agg_dict = {
            'PC1_rescaled': 'mean',
            'PC2_rescaled': 'mean'
        }
        
        # 分别处理IVS和非IVS数据（包括Roleplay和Multilingual）
        if 'data_source' in self.pca_results.columns:
            ivs_data = self.pca_results[self.pca_results['data_source'] == 'IVS']
            non_ivs_data = self.pca_results[self.pca_results['data_source'] != 'IVS']
            
            entity_scores_list = []
            
            # 处理IVS数据（按原来的方式分组）
            if len(ivs_data) > 0:
                ivs_group_by = [col for col in group_by if col in ivs_data.columns]
                ivs_agg_dict = {k: v for k, v in agg_dict.items() if k in ivs_data.columns}
                
                # 添加其他列的聚合方式
                for col in ['cultural_region']:
                    if col in ivs_data.columns and col not in ivs_group_by:
                        ivs_agg_dict[col] = 'first'
                
                ivs_scores = ivs_data.groupby(ivs_group_by).agg(ivs_agg_dict).reset_index()
                entity_scores_list.append(ivs_scores)
            
            # 处理非IVS数据（包含model_name和language分组）
            if len(non_ivs_data) > 0:
                non_ivs_group_by = group_by.copy()
                if 'model_name' in non_ivs_data.columns and 'model_name' not in non_ivs_group_by:
                    non_ivs_group_by.append('model_name')
                if 'language' in non_ivs_data.columns and 'language' not in non_ivs_group_by:
                    non_ivs_group_by.append('language')
                
                non_ivs_agg_dict = {k: v for k, v in agg_dict.items() if k in non_ivs_data.columns}
                
                # 添加其他列的聚合方式
                for col in ['cultural_region']:
                    if col in non_ivs_data.columns and col not in non_ivs_group_by:
                        non_ivs_agg_dict[col] = 'first'
                
                non_ivs_scores = non_ivs_data.groupby(non_ivs_group_by).agg(non_ivs_agg_dict).reset_index()
                entity_scores_list.append(non_ivs_scores)
            
            # 合并结果
            if entity_scores_list:
                entity_scores = pd.concat(entity_scores_list, ignore_index=True)
            else:
                entity_scores = pd.DataFrame()
        else:
            # 原来的逻辑（没有data_source列的情况）
            entity_scores = self.pca_results.groupby(group_by).agg(agg_dict).reset_index()
        
        # 合并元数据（处理不同的匹配方式）
        if self.country_codes is not None:
            # 尝试按数字代码匹配
            try:
                entity_scores['country_code_num'] = pd.to_numeric(entity_scores['country_code'], errors='coerce')
                numeric_matches = entity_scores.merge(
                    self.country_codes, 
                    left_on='country_code_num', 
                    right_on='Numeric', 
                    how='left'
                )
                # 如果有成功的数字匹配，使用它们
                if not numeric_matches['Country'].isna().all():
                    entity_scores = numeric_matches
                else:
                    # 否则尝试按国家名称匹配
                    entity_scores = entity_scores.merge(
                        self.country_codes, 
                        left_on='country_code', 
                        right_on='Country', 
                        how='left'
                    )
            except:
                # 如果数字转换失败，直接按名称匹配
                entity_scores = entity_scores.merge(
                    self.country_codes, 
                    left_on='country_code', 
                    right_on='Country', 
                    how='left'
                )
            
            # 保留所有实体，包括无法匹配的（roleplay数据）
            # entity_scores = entity_scores.dropna(subset=['Numeric'])  # 注释掉这行
        
        print(f"📈 计算了 {len(entity_scores)} 个实体的分数")
        return entity_scores
    
    def save_results(self, entity_scores: pd.DataFrame = None, prefix: str = "pca"):
        """保存分析结果
        
        Args:
            entity_scores: 实体分数数据
            prefix: 文件名前缀
        """
        # 保存PCA结果
        if self.pca_results is not None:
            pca_path = self.data_path / f"{prefix}_results.pkl"
            self.pca_results.to_pickle(pca_path)
            print(f"💾 保存PCA结果到: {pca_path}")
        
        # 保存实体分数
        if entity_scores is not None:
            scores_path = self.data_path / f"{prefix}_entity_scores.pkl"
            entity_scores.to_pickle(scores_path)
            print(f"💾 保存实体分数到: {scores_path}")
    
    def print_summary(self, entity_scores: pd.DataFrame = None):
        """打印分析结果摘要
        
        Args:
            entity_scores: 实体分数数据
        """
        print("\n" + "="*50)
        print("📊 PCA分析结果摘要")
        print("="*50)
        
        if self.pca_results is not None:
            print(f"总观测值数量: {len(self.pca_results)}")
            print(f"PC1范围: [{self.pca_results['PC1_rescaled'].min():.2f}, {self.pca_results['PC1_rescaled'].max():.2f}]")
            print(f"PC2范围: [{self.pca_results['PC2_rescaled'].min():.2f}, {self.pca_results['PC2_rescaled'].max():.2f}]")
        
        if entity_scores is not None:
            print(f"实体数量: {len(entity_scores)}")
            
            # 统计不同类型的实体
            if 'data_source' in entity_scores.columns:
                print("\n数据源分布:")
                print(entity_scores['data_source'].value_counts())
            
            if 'Cultural Region' in entity_scores.columns:
                print("\n文化区域分布:")
                print(entity_scores['Cultural Region'].value_counts())
    
    def run_full_analysis(self) -> pd.DataFrame:
        """运行完整的分析流程
        
        Returns:
            最终的实体分数DataFrame
        """
        print("🚀 开始完整PCA分析流程...")
        
        # 1. 加载基础数据
        if not self.load_base_data():
            raise ValueError("加载基础数据失败")
        
        # 2. 加载额外数据
        additional_data = self.load_additional_data()
        
        # 3. 合并数据
        combined_data = self.combine_data()
        
        # 4. 执行PCA分析
        pca_results = self.perform_pca_analysis(combined_data)
        
        # 5. 计算实体分数
        entity_scores = self.calculate_entity_scores()
        
        # 6. 保存结果
        self.save_results(entity_scores)
        
        # 7. 打印摘要
        self.print_summary(entity_scores)
        
        print("✅ 完整分析流程完成!")
        return entity_scores
