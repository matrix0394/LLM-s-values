"""
统一的文化地图可视化基类
消除多个可视化模块的重复代码

重构版本 - 2025.11.01
- 修复文化区域颜色重复问题
- 为7个LLM模型分配独特且差异明显的颜色
- 建立Stage1-3统一的颜色方案
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
        
        # 标准文化区域颜色映射（8个标准区域，来自cultural_regions.json）
        # 颜色选择原则：差异明显，易于区分，色盲友好
        self.cultural_region_colors = {
            # 欧洲区域 - 蓝橙系
            'Orthodox Europe': '#0072b2',      # 深蓝
            'Catholic Europe': '#e69f00',      # 橙色
            'Protestant Europe': '#d55e00',    # 深橙红
            
            # 英语区域 - 绿色
            'English-Speaking': '#009e73',     # 青绿色
            
            # 亚洲区域
            'Confucian': '#cc0000',            # 鲜红色
            'West & South Asia': '#f0e442',    # 黄色
            
            # 非洲和伊斯兰区域 - 粉色
            'African-Islamic': '#cc79a7',      # 粉红色
            'Africa-Islamic': '#cc79a7',       # 兼容命名（同一区域）
            
            # 拉美区域 - 灰色
            'Latin America': '#7f7f7f',        # 中灰色
            
            # 特殊标记
            'AI Model': '#ff1493',             # 深粉（AI模型通用）
            'Unknown': '#cccccc'               # 浅灰
        }
        
        # LLM模型颜色映射（7个模型，颜色差异明显）
        # 基于模型来源地区选择颜色主题
        self.llm_model_colors = {
            # 美国模型 - 红蓝系
            'openai/gpt-4o-mini': '#ff4444',           # 鲜红
            'GPT': '#ff4444',                          # 简称映射
            'gpt': '#ff4444',                          # 小写映射
            
            'anthropic/claude-3.7-sonnet': '#00bfff',  # 深天蓝
            'Claude': '#00bfff',
            'claude': '#00bfff',
            
            'google/gemini-2.0-flash-001': '#4285f4',  # Google蓝
            'Gemini': '#4285f4',
            'gemini': '#4285f4',
            
            'meta-llama/llama-3.3-70b-instruct': '#8b4513', # 棕色
            'LLaMA': '#8b4513',
            'llama': '#8b4513',
            
            # 中国模型 - 暖色系
            'deepseek/deepseek-chat-v3-0324': '#ff6b35',   # 橙红
            'DeepSeek': '#ff6b35',
            'deepseek': '#ff6b35',
            
            'qwen/qwq-32b': '#ffaa00',                 # 金橙
            'QWen': '#ffaa00',
            'qwen': '#ffaa00',
            
            # 欧洲模型 - 紫色系
            'mistralai/mistral-nemo': '#9370db',       # 中紫
            'Mistral': '#9370db',
            'mistral': '#9370db',
            
            # 通用LLM标记
            'LLM': '#ff1493',
            'Model': '#ff1493'
        }
        
        # 合并所有颜色映射
        self.extended_colors = self._generate_extended_colors()
    
    def _generate_extended_colors(self) -> Dict[str, str]:
        """生成扩展的颜色映射"""
        # 合并文化区域和LLM模型颜色
        extended = {}
        extended.update(self.cultural_region_colors)
        extended.update(self.llm_model_colors)
        
        # 添加备用颜色
        backup_colors = {
            'backup_1': '#2ca02c',
            'backup_2': '#bcbd22',
            'backup_3': '#17becf',
            'backup_4': '#8c564b',
            'backup_5': '#e377c2'
        }
        extended.update(backup_colors)
        
        return extended
    
    @abstractmethod
    def load_data(self) -> pd.DataFrame:
        """加载数据 - 子类实现"""
        pass
    
    def get_color_for_region(self, region: str) -> str:
        """获取区域对应的颜色（智能匹配）
        
        Args:
            region: 区域名称或模型名称
            
        Returns:
            颜色代码
        """
        if not region or pd.isna(region):
            return '#cccccc'
        
        region_str = str(region).strip()
        
        # 直接匹配
        if region_str in self.extended_colors:
            return self.extended_colors[region_str]
        
        # 模糊匹配LLM模型名称
        region_lower = region_str.lower()
        for key in self.llm_model_colors.keys():
            if key.lower() in region_lower or region_lower in key.lower():
                return self.llm_model_colors[key]
        
        # 默认颜色
        return '#cccccc'
    
    def get_color_for_model(self, model_name: str) -> str:
        """专门为LLM模型获取颜色（更精确的匹配）
        
        Args:
            model_name: 模型完整名称或简称
            
        Returns:
            颜色代码
        """
        if not model_name or pd.isna(model_name):
            return self.llm_model_colors.get('LLM', '#ff1493')
        
        model_str = str(model_name).strip()
        
        # 直接匹配
        if model_str in self.llm_model_colors:
            return self.llm_model_colors[model_str]
        
        # 按优先级匹配关键词
        model_lower = model_str.lower()
        
        # 精确匹配模型族
        model_patterns = [
            ('gpt', '#ff4444'),
            ('claude', '#00bfff'),
            ('gemini', '#4285f4'),
            ('llama', '#8b4513'),
            ('deepseek', '#ff6b35'),
            ('qwen', '#ffaa00'),
            ('mistral', '#9370db'),
        ]
        
        for pattern, color in model_patterns:
            if pattern in model_lower:
                return color
        
        # 默认LLM颜色
        return self.llm_model_colors.get('LLM', '#ff1493')
    
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
