"""
LLM多语言文化地图可视化器
支持：
1. 按语言区分颜色/标记
2. 每个模型单独画图
3. 所有模型的多语言对比图
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib as mpl
import numpy as np
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# 配置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.llm_values.llm_visualization import LLMCulturalMapVisualizer

# 语言颜色映射
LANGUAGE_COLORS = {
    'en': '#1f77b4',      # 蓝色 - 英语
    'fr': '#ff7f0e',      # 橙色 - 法语
    'es': '#2ca02c',      # 绿色 - 西班牙语
    'ru': '#d62728',      # 红色 - 俄语
    'ar': '#9467bd',      # 紫色 - 阿拉伯语
    'zh-cn': '#e377c2',   # 粉色 - 中文
}

# 语言标记映射
LANGUAGE_MARKERS = {
    'en': 'o',      # 圆形
    'fr': 's',      # 方形
    'es': '^',      # 三角形
    'ru': 'D',      # 菱形
    'ar': 'p',      # 五边形
    'zh-cn': '*',   # 星形
}

# 语言名称映射（英文，避免字体问题）
LANGUAGE_NAMES = {
    'en': 'English',
    'fr': 'French',
    'es': 'Spanish',
    'ru': 'Russian',
    'ar': 'Arabic',
    'zh-cn': 'Chinese',
}

# 语言名称映射（英文简写，用于图表显示）
LANGUAGE_NAMES_EN = {
    'en': 'EN',
    'fr': 'FR',
    'es': 'ES',
    'ru': 'RU',
    'ar': 'AR',
    'zh-cn': 'ZH',
}


class LLMMultilingualVisualizer(LLMCulturalMapVisualizer):
    """LLM多语言文化地图可视化器"""
    
    def __init__(self, data_path: str = "data", results_path: str = "results"):
        """初始化多语言可视化器"""
        super().__init__(data_path, results_path)
        
        # 多语言专用结果目录
        self.multilingual_results_dir = Path(results_path) / "llm_values" / "multilingual"
        self.multilingual_results_dir.mkdir(parents=True, exist_ok=True)
        
        # 语言配置（使用英文避免字体问题）
        self.language_colors = LANGUAGE_COLORS
        self.language_markers = LANGUAGE_MARKERS
        self.language_names = LANGUAGE_NAMES
        self.language_names_en = LANGUAGE_NAMES_EN
    
    def load_multilingual_data(self) -> pd.DataFrame:
        """
        加载多语言PCA结果数据
        
        期望文件：data/llm_values/llm_pca_entity_scores.pkl
        需要包含 language 字段
        """
        data = self.load_data()
        
        # 检查是否有语言字段
        if 'language' not in data.columns:
            print("⚠️ 数据中没有 language 字段，尝试从 country_code 提取...")
            # 尝试从 country_code 提取语言（格式: LLM_llm_model_lang）
            if 'country_code' in data.columns:
                data['language'] = data['country_code'].apply(self._extract_language_from_country_code)
            elif 'entity_id' in data.columns:
                data['language'] = data['entity_id'].apply(self._extract_language_from_entity_id)
            else:
                data['language'] = 'en'  # 默认英语
        
        # 统计语言分布
        lang_counts = data['language'].value_counts()
        print(f"📊 语言分布:")
        for lang, count in lang_counts.items():
            lang_name = self.language_names.get(lang, lang)
            print(f"   - {lang} ({lang_name}): {count}")
        
        return data
    
    def _extract_language_from_country_code(self, country_code) -> str:
        """从 country_code 提取语言代码"""
        if not country_code or not isinstance(country_code, str):
            return 'en'
        
        # 格式: LLM_llm_model_language
        # 先检查 zh-cn（因为包含连字符）
        if country_code.endswith('_zh-cn'):
            return 'zh-cn'
        
        # 检查其他语言
        for lang in ['en', 'fr', 'es', 'ru', 'ar']:
            if country_code.endswith(f'_{lang}'):
                return lang
        
        return 'en'  # 默认英语
    
    def _extract_language_from_entity_id(self, entity_id: str) -> str:
        """从 entity_id 提取语言代码"""
        if not entity_id:
            return 'en'
        
        # 格式: llm_model_language 或 llm_model_en
        for lang in self.language_colors.keys():
            if f'_{lang}' in entity_id or entity_id.endswith(f'_{lang}'):
                return lang
        
        return 'en'  # 默认英语
    
    def _extract_model_name(self, row: pd.Series) -> str:
        """从数据行提取模型名称"""
        if 'model_name' in row.index and pd.notna(row['model_name']):
            return str(row['model_name'])
        elif 'extracted_model' in row.index and pd.notna(row['extracted_model']):
            return str(row['extracted_model'])
        elif 'entity_id' in row.index:
            # 从 entity_id 提取: llm_model_lang -> model
            entity_id = str(row['entity_id'])
            if entity_id.startswith('llm_'):
                parts = entity_id[4:].rsplit('_', 1)
                if len(parts) >= 1:
                    return parts[0]
        return "Unknown"
    
    def plot_all_models_by_language(self, data: pd.DataFrame = None,
                                    figsize: Tuple[int, int] = (16, 12),
                                    save_path: Optional[str] = None,
                                    show_countries: bool = True) -> plt.Figure:
        """
        绘制所有模型的多语言对比图（按语言着色）
        
        Args:
            data: 数据
            figsize: 图形大小
            save_path: 保存路径
            show_countries: 是否显示国家背景
        """
        if data is None:
            data = self.load_multilingual_data()
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # 分离LLM和国家数据
        country_data, llm_data = self._split_llm_and_country_data(data)
        
        # 绘制国家背景（淡化显示）
        if show_countries and not country_data.empty:
            for region, color in self.cultural_region_colors.items():
                subset = country_data[country_data['Cultural Region'] == region]
                if len(subset) > 0:
                    ax.scatter(subset['PC1_rescaled'], subset['PC2_rescaled'],
                              color=color, s=30, alpha=0.2, marker='.')
                    # 添加国家标签（淡化）
                    for _, row in subset.iterrows():
                        country_name = self._get_point_label(row)
                        if country_name:
                            ax.text(row['PC1_rescaled'], row['PC2_rescaled'], 
                                   country_name, color=color, fontsize=7, alpha=0.4)
        
        # 按语言绘制LLM数据
        if not llm_data.empty:
            for lang in self.language_colors.keys():
                lang_data = llm_data[llm_data['language'] == lang]
                if lang_data.empty:
                    continue
                
                color = self.language_colors[lang]
                marker = self.language_markers[lang]
                lang_name = self.language_names[lang]
                
                ax.scatter(lang_data['PC1_rescaled'], lang_data['PC2_rescaled'],
                          color=color, s=150, alpha=0.8, marker=marker,
                          edgecolors='black', linewidth=1,
                          label=f'{lang_name} ({lang})')
                
                # 添加模型标签
                for _, row in lang_data.iterrows():
                    model_name = self._extract_model_name(row)
                    ax.annotate(model_name, 
                               (row['PC1_rescaled'], row['PC2_rescaled']),
                               xytext=(5, 5), textcoords='offset points',
                               fontsize=8, color=color, alpha=0.8)
        
        ax.set_xlabel('Survival vs. Self-Expression Values', fontsize=12)
        ax.set_ylabel('Traditional vs. Secular Values', fontsize=12)
        ax.set_title('LLM Cultural Values by Interview Language', fontsize=14)
        ax.legend(loc='upper left', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        fig.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"📊 多语言对比图已保存: {save_path}")
        
        return fig
    
    def plot_single_model_languages(self, model_name: str,
                                    data: pd.DataFrame = None,
                                    figsize: Tuple[int, int] = (12, 10),
                                    save_path: Optional[str] = None,
                                    show_countries: bool = True) -> plt.Figure:
        """
        绘制单个模型在不同语言下的文化坐标
        
        Args:
            model_name: 模型名称
            data: 数据
            figsize: 图形大小
            save_path: 保存路径
            show_countries: 是否显示国家背景
        """
        if data is None:
            data = self.load_multilingual_data()
        
        # 分离数据
        country_data, llm_data = self._split_llm_and_country_data(data)
        
        # 筛选该模型的数据
        model_data = llm_data[llm_data.apply(
            lambda row: self._extract_model_name(row) == model_name, axis=1
        )]
        
        if model_data.empty:
            print(f"⚠️ 未找到模型 {model_name} 的数据")
            return plt.figure()
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # 绘制国家背景
        if show_countries and not country_data.empty:
            for region, color in self.cultural_region_colors.items():
                subset = country_data[country_data['Cultural Region'] == region]
                if len(subset) > 0:
                    ax.scatter(subset['PC1_rescaled'], subset['PC2_rescaled'],
                              color=color, s=30, alpha=0.15, marker='.')
                    for _, row in subset.iterrows():
                        country_name = self._get_point_label(row)
                        if country_name:
                            ax.text(row['PC1_rescaled'], row['PC2_rescaled'],
                                   country_name, color=color, fontsize=7, alpha=0.3)
        
        # 绘制该模型在不同语言下的点
        points = []
        for _, row in model_data.iterrows():
            lang = row.get('language', 'en')
            color = self.language_colors.get(lang, 'gray')
            marker = self.language_markers.get(lang, 'o')
            lang_name = self.language_names.get(lang, lang)
            
            x, y = row['PC1_rescaled'], row['PC2_rescaled']
            points.append((x, y, lang))
            
            ax.scatter(x, y, color=color, s=200, alpha=0.9, marker=marker,
                      edgecolors='black', linewidth=1.5,
                      label=f'{lang_name} ({lang})')
            
            # 添加语言标签
            ax.annotate(lang_name, (x, y), xytext=(8, 8), 
                       textcoords='offset points',
                       fontsize=10, fontweight='bold', color=color)
        
        # 连接不同语言的点（显示变化轨迹）
        if len(points) > 1:
            points_sorted = sorted(points, key=lambda p: list(self.language_colors.keys()).index(p[2]) 
                                  if p[2] in self.language_colors else 99)
            xs = [p[0] for p in points_sorted]
            ys = [p[1] for p in points_sorted]
            ax.plot(xs, ys, 'k--', alpha=0.3, linewidth=1)
        
        # 计算并显示语言间的最大距离
        if len(points) > 1:
            max_dist = 0
            for i, p1 in enumerate(points):
                for p2 in points[i+1:]:
                    dist = np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
                    if dist > max_dist:
                        max_dist = dist
            ax.text(0.02, 0.98, f'Max Language Distance: {max_dist:.3f}',
                   transform=ax.transAxes, fontsize=10,
                   verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        ax.set_xlabel('Survival vs. Self-Expression Values', fontsize=12)
        ax.set_ylabel('Traditional vs. Secular Values', fontsize=12)
        ax.set_title(f'Cultural Values of {model_name} by Language', fontsize=14)
        ax.legend(loc='upper left', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        fig.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"📊 {model_name} 多语言图已保存: {save_path}")
        
        return fig
    
    def plot_all_models_individual(self, data: pd.DataFrame = None,
                                   save_dir: Optional[str] = None) -> Dict[str, str]:
        """
        为每个模型生成单独的多语言对比图
        
        Args:
            data: 数据
            save_dir: 保存目录
            
        Returns:
            保存的文件路径字典
        """
        if data is None:
            data = self.load_multilingual_data()
        
        if save_dir is None:
            save_dir = self.multilingual_results_dir / "per_model"
        else:
            save_dir = Path(save_dir)
        
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # 获取所有模型名称
        _, llm_data = self._split_llm_and_country_data(data)
        model_names = llm_data.apply(self._extract_model_name, axis=1).unique()
        
        print(f"\n🎨 为 {len(model_names)} 个模型生成单独图表...")
        
        saved_files = {}
        for model_name in sorted(model_names):
            # 创建安全的文件名
            safe_name = model_name.replace('/', '_').replace('\\', '_').replace(':', '_')
            save_path = save_dir / f"{safe_name}_languages.png"
            
            fig = self.plot_single_model_languages(model_name, data, save_path=str(save_path))
            plt.close(fig)
            
            saved_files[model_name] = str(save_path)
            print(f"   ✅ {model_name}")
        
        return saved_files
    
    def plot_language_comparison_grid(self, data: pd.DataFrame = None,
                                      figsize: Tuple[int, int] = (20, 16),
                                      save_path: Optional[str] = None) -> plt.Figure:
        """
        绘制语言对比网格图（每种语言一个子图）
        
        Args:
            data: 数据
            figsize: 图形大小
            save_path: 保存路径
        """
        if data is None:
            data = self.load_multilingual_data()
        
        country_data, llm_data = self._split_llm_and_country_data(data)
        
        # 获取有数据的语言
        languages = [lang for lang in self.language_colors.keys() 
                    if lang in llm_data['language'].values]
        
        if not languages:
            print("⚠️ 没有多语言数据")
            return plt.figure()
        
        # 创建子图网格
        n_langs = len(languages)
        n_cols = min(3, n_langs)
        n_rows = (n_langs + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize, squeeze=False)
        axes = axes.flatten()
        
        for idx, lang in enumerate(languages):
            ax = axes[idx]
            lang_name = self.language_names.get(lang, lang)
            color = self.language_colors[lang]
            
            # 绘制国家背景
            if not country_data.empty:
                for region, reg_color in self.cultural_region_colors.items():
                    subset = country_data[country_data['Cultural Region'] == region]
                    if len(subset) > 0:
                        ax.scatter(subset['PC1_rescaled'], subset['PC2_rescaled'],
                                  color=reg_color, s=15, alpha=0.15, marker='.')
            
            # 绘制该语言的LLM数据
            lang_data = llm_data[llm_data['language'] == lang]
            ax.scatter(lang_data['PC1_rescaled'], lang_data['PC2_rescaled'],
                      color=color, s=100, alpha=0.8, marker=self.language_markers[lang],
                      edgecolors='black', linewidth=1)
            
            # 添加模型标签
            for _, row in lang_data.iterrows():
                model_name = self._extract_model_name(row)
                ax.annotate(model_name, (row['PC1_rescaled'], row['PC2_rescaled']),
                           xytext=(3, 3), textcoords='offset points',
                           fontsize=7, color=color)
            
            ax.set_title(f'{lang_name} ({lang})', fontsize=12, color=color, fontweight='bold')
            ax.set_xlabel('Survival-Expression', fontsize=9)
            ax.set_ylabel('Traditional-Secular', fontsize=9)
            ax.grid(True, alpha=0.3)
        
        # 隐藏多余的子图
        for idx in range(len(languages), len(axes)):
            axes[idx].set_visible(False)
        
        fig.suptitle('LLM Cultural Values by Interview Language', fontsize=16, y=1.02)
        fig.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"📊 语言对比网格图已保存: {save_path}")
        
        return fig
    
    def create_multilingual_dashboard(self, data: pd.DataFrame = None,
                                      save_dir: Optional[str] = None) -> Dict[str, str]:
        """
        创建完整的多语言可视化仪表板
        
        Args:
            data: 数据
            save_dir: 保存目录
            
        Returns:
            保存的文件路径字典
        """
        if data is None:
            data = self.load_multilingual_data()
        
        if save_dir is None:
            save_dir = self.multilingual_results_dir
        else:
            save_dir = Path(save_dir)
        
        save_dir.mkdir(parents=True, exist_ok=True)
        
        saved_files = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print(f"\n{'='*60}")
        print(f"🎨 创建多语言可视化仪表板")
        print(f"{'='*60}")
        print(f"📁 保存目录: {save_dir}")
        
        # 1. 所有模型按语言着色的总图
        print(f"\n1️⃣ 生成所有模型多语言对比图...")
        path1 = save_dir / f"all_models_by_language_{timestamp}.png"
        fig1 = self.plot_all_models_by_language(data, save_path=str(path1))
        saved_files['all_models_by_language'] = str(path1)
        plt.close(fig1)
        
        # 2. 语言对比网格图
        print(f"2️⃣ 生成语言对比网格图...")
        path2 = save_dir / f"language_comparison_grid_{timestamp}.png"
        fig2 = self.plot_language_comparison_grid(data, save_path=str(path2))
        saved_files['language_grid'] = str(path2)
        plt.close(fig2)
        
        # 3. 每个模型单独的图
        print(f"3️⃣ 生成每个模型的单独图表...")
        model_files = self.plot_all_models_individual(data, save_dir=save_dir / "per_model")
        saved_files['per_model'] = model_files
        
        print(f"\n{'='*60}")
        print(f"✅ 多语言可视化完成！")
        print(f"   - 总图: 2 个")
        print(f"   - 单模型图: {len(model_files)} 个")
        print(f"{'='*60}")
        
        return saved_files


def main():
    """主函数"""
    print("🔄 运行多语言可视化...")
    
    visualizer = LLMMultilingualVisualizer()
    
    try:
        saved_files = visualizer.create_multilingual_dashboard()
        
        print(f"\n🎉 可视化完成！")
        print("📊 生成的图形:")
        for name, path in saved_files.items():
            if isinstance(path, dict):
                print(f"   - {name}: {len(path)} 个文件")
            else:
                print(f"   - {name}: {path}")
        
        return saved_files
        
    except Exception as e:
        print(f"❌ 可视化失败: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
