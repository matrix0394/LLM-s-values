"""
统一的文化地图可视化基类
消除多个可视化模块的重复代码
"""

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd
import numpy as np
from sklearn.svm import SVC
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from abc import ABC, abstractmethod


class BaseCulturalMapVisualizer(ABC):
    """文化地图可视化基类 - 提供通用的可视化功能"""
    
    def __init__(self, data_path: str = "data", results_path: str = "results"):
        """初始化可视化器
        
        Args:
            data_path: 数据路径
            results_path: 结果保存路径
        """
        self.data_path = Path(data_path)
        self.results_path = Path(results_path)
        self.results_path.mkdir(exist_ok=True)
        
        # 标准文化区域颜色映射
        self.cultural_region_colors = {
            'African-Islamic': '#cc79a7',
            'Africa-Islamic': '#cc79a7',  # 兼容两种命名
            'Orthodox Europe': '#0072b2',
            'Catholic Europe': '#e69f00',
            'Protestant Europe': '#d55e00',
            'English-Speaking': '#009e73',
            'Latin America': '#999999',
            'Confucian': '#e69f00',
            'West & South Asia': '#f0e442',
            'South Asia': '#56b4e9',
            'Baltic': '#0072b2',
            'Africa': '#cc79a7',
            'AI Model': '#ff1493',  # AI模型特殊颜色
            'Unknown': '#cccccc'
        }
        
        # 可扩展的颜色映射
        self.extended_colors = self._generate_extended_colors()
    
    def _generate_extended_colors(self) -> Dict[str, str]:
        """生成扩展的颜色映射"""
        # 为可能的新区域生成颜色
        extended = self.cultural_region_colors.copy()
        
        # 添加一些备用颜色
        backup_colors = [
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
            '#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc'
        ]
        
        # 为LLM相关的特殊标识添加颜色
        extended.update({
            'LLM': '#ff1493',
            'Model': '#ff1493',
            'GPT': '#ff6b6b',
            'Claude': '#4ecdc4',
            'Gemini': '#45b7d1',
            'LLaMA': '#96ceb4',
            'QWen': '#ffeaa7',
            'DeepSeek': '#a29bfe'
        })
        
        return extended
    
    @abstractmethod
    def load_data(self) -> pd.DataFrame:
        """加载数据 - 子类实现"""
        pass
    
    def get_color_for_region(self, region: str) -> str:
        """获取区域对应的颜色
        
        Args:
            region: 区域名称
            
        Returns:
            颜色代码
        """
        return self.extended_colors.get(region, '#cccccc')
    
    def plot_basic_cultural_map(self, data: pd.DataFrame, 
                               figsize: Tuple[int, int] = (14, 10),
                               title: str = "Inglehart-Welzel Cultural Map",
                               show_labels: bool = True,
                               save_path: Optional[str] = None) -> plt.Figure:
        """绘制基础文化地图
        
        Args:
            data: 包含PC1_rescaled, PC2_rescaled, Cultural Region等列的数据
            figsize: 图形大小
            title: 图标题
            show_labels: 是否显示标签
            save_path: 保存路径
            
        Returns:
            matplotlib Figure对象
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # 按文化区域绘制
        for region in data['Cultural Region'].unique():
            if pd.isna(region):
                continue
                
            subset = data[data['Cultural Region'] == region]
            color = self.get_color_for_region(region)
            
            # 绘制散点
            ax.scatter(subset['PC1_rescaled'], subset['PC2_rescaled'], 
                      label=region, color=color, s=50, alpha=0.7)
            
            # 添加标签
            if show_labels:
                for _, row in subset.iterrows():
                    label_text = self._get_point_label(row)
                    if label_text:
                        ax.text(row['PC1_rescaled'], row['PC2_rescaled'], 
                               label_text, color=color, fontsize=8, ha='center')
        
        # 设置图形属性
        ax.set_xlabel('Survival vs. Self-Expression Values')
        ax.set_ylabel('Traditional vs. Secular Values')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.tight_layout()
        
        # 保存图形
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"📊 文化地图已保存到: {save_path}")
        
        return fig
    
    def _get_point_label(self, row: pd.Series) -> str:
        """获取数据点的标签文本 - 子类可重写
        
        Args:
            row: 数据行
            
        Returns:
            标签文本
        """
        # 默认使用Country列，如果没有则使用索引
        if 'Country' in row.index:
            return str(row['Country'])
        elif 'model_name' in row.index:
            return str(row['model_name'])
        else:
            return ""
    
    def plot_decision_boundary(self, data: pd.DataFrame,
                              target_column: str = 'Cultural Region',
                              figsize: Tuple[int, int] = (14, 10),
                              save_path: Optional[str] = None) -> plt.Figure:
        """绘制决策边界
        
        Args:
            data: 数据
            target_column: 目标分类列
            figsize: 图形大小
            save_path: 保存路径
            
        Returns:
            matplotlib Figure对象
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # 准备数据
        X = data[['PC1_rescaled', 'PC2_rescaled']].values
        y = data[target_column].values
        
        # 训练SVM分类器
        svm = SVC(kernel='rbf', C=1.0, gamma='scale')
        svm.fit(X, y)
        
        # 创建网格
        h = 0.1
        x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
        y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
        xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                            np.arange(y_min, y_max, h))
        
        # 预测网格点
        Z = svm.predict(np.c_[xx.ravel(), yy.ravel()])
        Z = Z.reshape(xx.shape)
        
        # 绘制决策边界
        ax.contourf(xx, yy, Z, alpha=0.3, cmap=plt.cm.Set3)
        
        # 绘制数据点
        for region in data[target_column].unique():
            if pd.isna(region):
                continue
            subset = data[data[target_column] == region]
            color = self.get_color_for_region(region)
            ax.scatter(subset['PC1_rescaled'], subset['PC2_rescaled'], 
                      label=region, color=color, s=50, alpha=0.8)
        
        ax.set_xlabel('Survival vs. Self-Expression Values')
        ax.set_ylabel('Traditional vs. Secular Values')
        ax.set_title('Cultural Regions with Decision Boundaries')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"📊 决策边界图已保存到: {save_path}")
        
        return fig
    
    def create_comparison_plot(self, data: pd.DataFrame,
                              group_column: str,
                              figsize: Tuple[int, int] = (16, 12),
                              save_path: Optional[str] = None) -> plt.Figure:
        """创建对比图
        
        Args:
            data: 数据
            group_column: 分组列名
            figsize: 图形大小
            save_path: 保存路径
            
        Returns:
            matplotlib Figure对象
        """
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        
        # 子图1: 散点图
        ax1 = axes[0, 0]
        for group in data[group_column].unique():
            if pd.isna(group):
                continue
            subset = data[data[group_column] == group]
            color = self.get_color_for_region(str(group))
            ax1.scatter(subset['PC1_rescaled'], subset['PC2_rescaled'], 
                       label=group, color=color, alpha=0.7)
        ax1.set_title('Cultural Distribution')
        ax1.set_xlabel('PC1 (Survival vs. Self-Expression)')
        ax1.set_ylabel('PC2 (Traditional vs. Secular)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 子图2: PC1分布
        ax2 = axes[0, 1]
        for group in data[group_column].unique():
            if pd.isna(group):
                continue
            subset = data[data[group_column] == group]
            ax2.hist(subset['PC1_rescaled'], alpha=0.6, label=group, bins=15)
        ax2.set_title('PC1 Distribution')
        ax2.set_xlabel('PC1 Score')
        ax2.set_ylabel('Frequency')
        ax2.legend()
        
        # 子图3: PC2分布
        ax3 = axes[1, 0]
        for group in data[group_column].unique():
            if pd.isna(group):
                continue
            subset = data[data[group_column] == group]
            ax3.hist(subset['PC2_rescaled'], alpha=0.6, label=group, bins=15)
        ax3.set_title('PC2 Distribution')
        ax3.set_xlabel('PC2 Score')
        ax3.set_ylabel('Frequency')
        ax3.legend()
        
        # 子图4: 统计摘要
        ax4 = axes[1, 1]
        summary_data = data.groupby(group_column)[['PC1_rescaled', 'PC2_rescaled']].agg(['mean', 'std'])
        summary_data.plot(kind='bar', ax=ax4)
        ax4.set_title('Statistical Summary')
        ax4.set_ylabel('Score')
        ax4.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"📊 对比图已保存到: {save_path}")
        
        return fig
    
    def save_figure(self, fig: plt.Figure, filename: str, 
                   subfolder: str = None) -> str:
        """保存图形到结果目录
        
        Args:
            fig: matplotlib图形对象
            filename: 文件名
            subfolder: 子文件夹名
            
        Returns:
            保存的完整路径
        """
        if subfolder:
            save_dir = self.results_path / subfolder
            save_dir.mkdir(exist_ok=True)
        else:
            save_dir = self.results_path
        
        save_path = save_dir / filename
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"📊 图形已保存到: {save_path}")
        return str(save_path)
