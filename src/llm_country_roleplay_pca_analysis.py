"""
LLM国家角色扮演PCA分析模块
参考llm_pca_analysis的功能，处理llm_country_roleplay_data_processor得到的数据
"""

import pandas as pd
import numpy as np
import os
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path
from ppca import PPCA
from factor_analyzer import Rotator
import pickle

# 导入数据处理器
from llm_country_roleplay_data_processor import LLMCountryRoleplayDataProcessor


class LLMCountryRoleplayPCAAnalyzer:
    """LLM国家角色扮演PCA分析器"""
    
    def __init__(self, data_dir: str = None):
        """初始化分析器
        
        Args:
            data_dir: 数据目录路径
        """
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        
        self.data_dir = Path(data_dir)
        
        # IVS问题列表
        self.iv_qns = ["A008", "A165", "E018", "E025", "F063", "F118", "F120", "G006", "Y002", "Y003"]
        
        # 主成分重新缩放参数（与原始分析保持一致）
        self.pc_rescale_params = {'PC1': (1.81, 0.38), 'PC2': (1.61, -0.01)}
        
        # 数据存储
        self.ivs_df = None
        self.country_codes = None
        self.roleplay_data = None
        self.combined_data = None
        self.pca_results = None
        
        # 初始化数据处理器
        self.data_processor = LLMCountryRoleplayDataProcessor(data_dir=str(self.data_dir))
    
    def load_ivs_data(self) -> bool:
        """加载IVS基础数据"""
        try:
            # 加载IVS数据
            ivs_path = self.data_dir / "ivs_df.pkl"
            if ivs_path.exists():
                self.ivs_df = pd.read_pickle(ivs_path)
                print(f"加载IVS数据: {self.ivs_df.shape}")
            else:
                print("警告：未找到IVS数据，将仅使用角色扮演数据")
                self.ivs_df = pd.DataFrame()
            
            # 加载国家代码数据
            country_codes_path = self.data_dir / "country_codes.pkl"
            if country_codes_path.exists():
                self.country_codes = pd.read_pickle(country_codes_path)
                print(f"加载国家代码数据: {self.country_codes.shape}")
            else:
                print("警告：未找到国家代码数据")
                self.country_codes = pd.DataFrame()
            
            return True
        except Exception as e:
            print(f"加载数据失败: {e}")
            return False
    
    def load_roleplay_data(self) -> pd.DataFrame:
        """加载角色扮演数据"""
        try:
            # 使用数据处理器创建IVS兼容格式的数据
            roleplay_data = self.data_processor.create_ivs_compatible_dataframe()
            
            if roleplay_data.empty:
                print("警告：未找到角色扮演数据")
                return pd.DataFrame()
            
            print(f"加载角色扮演数据: {roleplay_data.shape}")
            
            # 确保数据格式正确
            required_columns = ['year', 'country_code', 'weight', 'model_name', 'model_region', 'cultural_region'] + self.iv_qns
            missing_columns = [col for col in required_columns if col not in roleplay_data.columns]
            
            if missing_columns:
                print(f"警告：角色扮演数据缺少列: {missing_columns}")
                # 为缺少的列添加默认值
                for col in missing_columns:
                    if col in self.iv_qns:
                        roleplay_data[col] = np.nan
                    elif col == 'weight':
                        roleplay_data[col] = 1.0
                    elif col == 'year':
                        roleplay_data[col] = 2025
            
            # 过滤掉没有足够问题回答的行
            roleplay_data = roleplay_data.dropna(subset=self.iv_qns, thresh=6)
            print(f"过滤后的角色扮演数据: {roleplay_data.shape}")
            
            return roleplay_data
            
        except Exception as e:
            print(f"加载角色扮演数据失败: {e}")
            return pd.DataFrame()
    
    def prepare_ivs_data(self) -> pd.DataFrame:
        """准备IVS数据（如果可用）"""
        if self.ivs_df is None or self.ivs_df.empty:
            return pd.DataFrame()
        
        try:
            # 选择需要的列
            meta_col = ["S020", "S003"]  # 年份和国家代码
            weights = ["S017"]  # 权重
            
            subset_ivs_df = self.ivs_df[meta_col + weights + self.iv_qns].copy()
            
            # 重命名列
            subset_ivs_df = subset_ivs_df.rename(columns={
                'S020': 'year', 
                'S003': 'country_code', 
                'S017': 'weight'
            })
            
            # 过滤2005年及以后的数据
            subset_ivs_df = subset_ivs_df[subset_ivs_df["year"] >= 2005]
            
            # 至少需要6个问题的答案
            subset_ivs_df = subset_ivs_df.dropna(subset=self.iv_qns, thresh=6)
            
            # 添加标识列
            subset_ivs_df['data_source'] = 'ivs'
            subset_ivs_df['model_name'] = None
            subset_ivs_df['model_region'] = None
            subset_ivs_df['cultural_region'] = None
            
            print(f"准备IVS数据: {subset_ivs_df.shape}")
            return subset_ivs_df
            
        except Exception as e:
            print(f"准备IVS数据失败: {e}")
            return pd.DataFrame()
    
    def create_combined_country_codes(self, roleplay_data: pd.DataFrame) -> pd.DataFrame:
        """创建合并的国家代码表"""
        # 从角色扮演数据中提取唯一的模型-国家组合
        roleplay_entities = roleplay_data[['country_code', 'model_name', 'model_region', 'cultural_region']].drop_duplicates()
        
        # 为每个角色扮演实体创建唯一代码
        if not self.country_codes.empty:
            max_code = self.country_codes['Numeric'].max()
        else:
            max_code = 1000
        
        # 创建角色扮演实体的元数据
        roleplay_meta = []
        for idx, row in roleplay_entities.iterrows():
            entity_name = f"{row['model_name']}_as_{row['country_code']}"
            roleplay_meta.append({
                'Country': entity_name,
                'Numeric': max_code + idx + 1,
                'Cultural Region': row['cultural_region'],
                'model_name': row['model_name'],
                'model_region': row['model_region'],
                'data_source': 'llm_roleplay',
                'is_roleplay': True
            })
        
        roleplay_meta_df = pd.DataFrame(roleplay_meta)
        
        # 更新角色扮演数据的country_code
        entity_mapping = dict(zip(
            roleplay_entities.apply(lambda x: f"{x['model_name']}_as_{x['country_code']}", axis=1),
            roleplay_meta_df['Numeric']
        ))
        
        roleplay_data['entity_key'] = roleplay_data.apply(
            lambda x: f"{x['model_name']}_as_{x['country_code']}", axis=1
        )
        roleplay_data['country_code'] = roleplay_data['entity_key'].map(entity_mapping)
        
        # 合并国家代码表
        if not self.country_codes.empty:
            # 为原始国家代码添加标识列
            original_codes = self.country_codes.copy()
            original_codes['is_roleplay'] = False
            original_codes['data_source'] = 'ivs'
            original_codes['model_name'] = None
            original_codes['model_region'] = None
            
            combined_codes = pd.concat([original_codes, roleplay_meta_df], ignore_index=True)
        else:
            combined_codes = roleplay_meta_df
        
        return combined_codes, roleplay_data
    
    def combine_data(self) -> pd.DataFrame:
        """合并所有数据"""
        # 加载角色扮演数据
        roleplay_data = self.load_roleplay_data()
        
        if roleplay_data.empty:
            raise ValueError("没有找到角色扮演数据")
        
        # 创建合并的国家代码表
        combined_codes, updated_roleplay_data = self.create_combined_country_codes(roleplay_data)
        self.country_codes = combined_codes
        
        # 准备IVS数据（如果可用）
        ivs_data = self.prepare_ivs_data()
        
        # 合并数据
        if not ivs_data.empty:
            # 确保两个数据集有相同的列
            common_columns = ['year', 'country_code', 'weight', 'data_source', 'model_name', 'model_region', 'cultural_region'] + self.iv_qns
            
            # 为IVS数据添加缺失的列
            for col in common_columns:
                if col not in ivs_data.columns:
                    if col in ['model_name', 'model_region', 'cultural_region']:
                        ivs_data[col] = None
                    elif col == 'data_source':
                        ivs_data[col] = 'ivs'
            
            # 为角色扮演数据添加缺失的列
            for col in common_columns:
                if col not in updated_roleplay_data.columns:
                    if col == 'data_source':
                        updated_roleplay_data[col] = 'llm_roleplay'
            
            self.combined_data = pd.concat([
                ivs_data[common_columns], 
                updated_roleplay_data[common_columns]
            ], ignore_index=True)
            
            print(f"合并数据: IVS {len(ivs_data)} + 角色扮演 {len(updated_roleplay_data)} = 总计 {len(self.combined_data)}")
        else:
            self.combined_data = updated_roleplay_data
            print(f"仅使用角色扮演数据: {len(self.combined_data)}")
        
        return self.combined_data
    
    def perform_pca_analysis(self) -> pd.DataFrame:
        """执行PCA分析"""
        if self.combined_data is None:
            raise ValueError("请先合并数据")
        
        print("开始PCA分析...")
        
        # 设置随机种子
        np.random.seed(42)
        
        # 准备PCA数据
        data_for_pca = self.combined_data[self.iv_qns].to_numpy()
        
        # 检查数据有效性
        valid_rows = ~np.isnan(data_for_pca).all(axis=1)
        if not valid_rows.any():
            raise ValueError("没有有效的数据行用于PCA分析")
        
        print(f"用于PCA的有效行数: {valid_rows.sum()}/{len(valid_rows)}")
        
        # 使用PPCA进行分析
        ppca = PPCA()
        ppca.fit(data_for_pca, d=2, min_obs=1, verbose=True)
        
        # 转换数据
        principal_components = ppca.transform()
        
        # 应用varimax旋转
        rotator = Rotator(method='varimax')
        rotated_components = rotator.fit_transform(principal_components)
        
        # 创建结果DataFrame
        ppca_df = pd.DataFrame(rotated_components, columns=["PC1", "PC2"])
        
        # 重新缩放主成分分数
        ppca_df['PC1_rescaled'] = (self.pc_rescale_params['PC1'][0] * ppca_df['PC1'] + 
                                  self.pc_rescale_params['PC1'][1])
        ppca_df['PC2_rescaled'] = (self.pc_rescale_params['PC2'][0] * ppca_df['PC2'] + 
                                  self.pc_rescale_params['PC2'][1])
        
        # 添加元数据
        ppca_df["country_code"] = self.combined_data["country_code"].values
        ppca_df["year"] = self.combined_data["year"].values
        ppca_df["data_source"] = self.combined_data["data_source"].values
        
        # 合并国家元数据
        ppca_df = ppca_df.merge(
            self.country_codes, 
            left_on='country_code', 
            right_on='Numeric', 
            how='left'
        )
        
        # 过滤掉无效的主成分分数
        self.pca_results = ppca_df.dropna(subset=['PC1_rescaled', 'PC2_rescaled'])
        
        print(f"PCA分析完成，有效观测数: {len(self.pca_results)}")
        return self.pca_results
    
    def calculate_entity_scores(self) -> pd.DataFrame:
        """计算实体级别的平均分数"""
        if self.pca_results is None:
            raise ValueError("请先执行PCA分析")
        
        # 按country_code分组计算平均分数
        entity_scores = self.pca_results.groupby('country_code')[[
            'PC1_rescaled', 'PC2_rescaled'
        ]].mean().reset_index()
        
        # 合并元数据
        entity_scores = entity_scores.merge(
            self.country_codes, 
            left_on='country_code', 
            right_on='Numeric', 
            how='left'
        )
        
        # 删除无法匹配的实体
        entity_scores = entity_scores.dropna(subset=['Numeric'])
        
        print(f"计算了 {len(entity_scores)} 个实体的分数")
        
        # 统计信息
        if 'is_roleplay' in entity_scores.columns:
            roleplay_entities = entity_scores[entity_scores['is_roleplay'] == True]
            real_countries = entity_scores[entity_scores['is_roleplay'] == False]
            
            print(f"角色扮演实体: {len(roleplay_entities)}, 真实国家: {len(real_countries)}")
        
        return entity_scores
    
    def save_results(self, entity_scores: pd.DataFrame):
        """保存分析结果"""
        try:
            # 保存详细PCA结果
            if self.pca_results is not None:
                pca_results_path = self.data_dir / "roleplay_pca_results.pkl"
                self.pca_results.to_pickle(pca_results_path)
                print(f"保存PCA结果到: {pca_results_path}")
            
            # 保存实体分数
            entity_scores_path = self.data_dir / "roleplay_entity_scores_pca.pkl"
            entity_scores.to_pickle(entity_scores_path)
            print(f"保存实体分数到: {entity_scores_path}")
            
            # 保存更新的国家代码
            if self.country_codes is not None:
                country_codes_path = self.data_dir / "country_codes_with_roleplay.pkl"
                self.country_codes.to_pickle(country_codes_path)
                print(f"保存更新的国家代码到: {country_codes_path}")
                
        except Exception as e:
            print(f"保存结果失败: {e}")
    
    def get_summary_statistics(self, entity_scores: pd.DataFrame) -> Dict[str, Any]:
        """获取分析结果统计"""
        stats = {
            "total_entities": len(entity_scores),
            "pc1_range": [entity_scores['PC1_rescaled'].min(), entity_scores['PC1_rescaled'].max()],
            "pc2_range": [entity_scores['PC2_rescaled'].min(), entity_scores['PC2_rescaled'].max()]
        }
        
        if 'is_roleplay' in entity_scores.columns:
            roleplay_count = len(entity_scores[entity_scores['is_roleplay'] == True])
            real_count = len(entity_scores[entity_scores['is_roleplay'] == False])
            stats["roleplay_entities"] = roleplay_count
            stats["real_countries"] = real_count
        
        if 'Cultural Region' in entity_scores.columns:
            stats["cultural_region_distribution"] = entity_scores['Cultural Region'].value_counts().to_dict()
        
        if 'model_region' in entity_scores.columns:
            model_regions = entity_scores[entity_scores['is_roleplay'] == True]['model_region'].value_counts().to_dict()
            stats["model_region_distribution"] = model_regions
        
        return stats
    
    def run_full_analysis(self) -> pd.DataFrame:
        """运行完整的分析流程"""
        print("=== 开始LLM国家角色扮演PCA分析 ===")
        
        try:
            # 1. 加载基础数据
            if not self.load_ivs_data():
                print("警告：基础数据加载失败，继续使用角色扮演数据")
            
            # 2. 合并数据
            combined_data = self.combine_data()
            
            # 3. 执行PCA分析
            pca_results = self.perform_pca_analysis()
            
            # 4. 计算实体分数
            entity_scores = self.calculate_entity_scores()
            
            # 5. 保存结果
            self.save_results(entity_scores)
            
            # 6. 输出统计信息
            stats = self.get_summary_statistics(entity_scores)
            self._print_summary(stats)
            
            return entity_scores
            
        except Exception as e:
            print(f"分析过程中出错: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _print_summary(self, stats: Dict[str, Any]):
        """打印分析结果摘要"""
        print("\n=== 分析结果摘要 ===")
        print(f"总实体数: {stats.get('total_entities', 0)}")
        
        if 'roleplay_entities' in stats:
            print(f"角色扮演实体: {stats['roleplay_entities']}")
        
        if 'real_countries' in stats:
            print(f"真实国家: {stats['real_countries']}")
        
        if 'pc1_range' in stats:
            pc1_min, pc1_max = stats['pc1_range']
            print(f"PC1范围: [{pc1_min:.2f}, {pc1_max:.2f}]")
        
        if 'pc2_range' in stats:
            pc2_min, pc2_max = stats['pc2_range']
            print(f"PC2范围: [{pc2_min:.2f}, {pc2_max:.2f}]")
        
        if 'cultural_region_distribution' in stats:
            print("\n文化区域分布:")
            for region, count in stats['cultural_region_distribution'].items():
                print(f"  {region}: {count}")
        
        if 'model_region_distribution' in stats:
            print("\n模型区域分布:")
            for region, count in stats['model_region_distribution'].items():
                print(f"  {region}: {count}")


def main():
    """主函数"""
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    
    # 创建分析器
    analyzer = LLMCountryRoleplayPCAAnalyzer(data_dir=data_dir)
    
    try:
        # 运行完整分析
        entity_scores = analyzer.run_full_analysis()
        
        print("\n=== 分析成功完成 ===")
        return entity_scores
        
    except Exception as e:
        print(f"分析失败: {e}")
        return None


if __name__ == "__main__":
    main()
