#!/usr/bin/env python3
"""
Generate language distribution visualization for PPT
Shows all 14 languages with their average PC1 values
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Set up paths
RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'results', 'analysis', 'stage0_vs_stage3')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'results', 'analysis', 'visualization')

def main():
    # Load detailed distance data
    df = pd.read_csv(os.path.join(RESULTS_DIR, 'distances_detailed.csv'))
    
    # Calculate average PC1 by language
    language_stats = df.groupby('language').agg({
        'llm_PC1': 'mean',
        'llm_PC2': 'mean',
        'distance': 'mean'
    }).reset_index()
    
    # Sort by PC1 (secular -> traditional)
    language_stats = language_stats.sort_values('llm_PC1', ascending=False)
    
    # Language name mapping
    lang_names = {
        'de': '德语 German',
        'it': '意大利语 Italian',
        'zh-tw': '繁体中文 Traditional Chinese',
        'en': '英语 English',
        'en-native': '英语(母语国) English (Native)',
        'fr': '法语 French',
        'pt': '葡萄牙语 Portuguese',
        'ja': '日语 Japanese',
        'es': '西班牙语 Spanish',
        'zh-hk': '粤语 Cantonese',
        'zh-cn': '简体中文 Simplified Chinese',
        'ko': '韩语 Korean',
        'ru': '俄语 Russian',
        'ar': '阿拉伯语 Arabic'
    }
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Colors based on PC1 value (gradient from green to red)
    colors = []
    for pc1 in language_stats['llm_PC1']:
        if pc1 > 3:
            colors.append('#27ae60')  # Green - most secular
        elif pc1 > 2:
            colors.append('#3498db')  # Blue - secular
        elif pc1 > 1:
            colors.append('#9b59b6')  # Purple - slightly secular
        elif pc1 > 0:
            colors.append('#f39c12')  # Orange - neutral
        elif pc1 > -1:
            colors.append('#e67e22')  # Dark orange - slightly traditional
        else:
            colors.append('#e74c3c')  # Red - most traditional
    
    # Create horizontal bar chart
    y_pos = np.arange(len(language_stats))
    bars = ax.barh(y_pos, language_stats['llm_PC1'], color=colors, edgecolor='white', linewidth=0.5)
    
    # Add value labels
    for i, (bar, pc1) in enumerate(zip(bars, language_stats['llm_PC1'])):
        if pc1 >= 0:
            ax.text(pc1 + 0.1, bar.get_y() + bar.get_height()/2, f'{pc1:.2f}', 
                   va='center', ha='left', fontsize=11, fontweight='bold')
        else:
            ax.text(pc1 - 0.1, bar.get_y() + bar.get_height()/2, f'{pc1:.2f}', 
                   va='center', ha='right', fontsize=11, fontweight='bold')
    
    # Set y-axis labels
    y_labels = [lang_names.get(lang, lang) for lang in language_stats['language']]
    ax.set_yticks(y_pos)
    ax.set_yticklabels(y_labels, fontsize=11)
    
    # Add vertical line at 0
    ax.axvline(x=0, color='gray', linestyle='--', linewidth=1, alpha=0.7)
    
    # Labels and title
    ax.set_xlabel('PC1: Survival ← → Self-Expression', fontsize=12, fontweight='bold')
    ax.set_title('Language Distribution on Cultural Map (PC1 Dimension)\n14 Languages Average Position', 
                fontsize=14, fontweight='bold', pad=15)
    
    # Add legend
    legend_elements = [
        plt.Rectangle((0,0),1,1, facecolor='#27ae60', label='Most Secular (>3)'),
        plt.Rectangle((0,0),1,1, facecolor='#3498db', label='Secular (2-3)'),
        plt.Rectangle((0,0),1,1, facecolor='#9b59b6', label='Slightly Secular (1-2)'),
        plt.Rectangle((0,0),1,1, facecolor='#f39c12', label='Neutral (0-1)'),
        plt.Rectangle((0,0),1,1, facecolor='#e67e22', label='Slightly Traditional (-1-0)'),
        plt.Rectangle((0,0),1,1, facecolor='#e74c3c', label='Most Traditional (<-1)')
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=9)
    
    # Grid
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.set_xlim(-3, 6)
    
    plt.tight_layout()
    
    # Save
    output_path = os.path.join(OUTPUT_DIR, 'language_distribution_pc1.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"✅ Saved: {output_path}")
    
    # Print stats for reference
    print("\n" + "="*60)
    print("Language PC1 Statistics (for PPT reference)")
    print("="*60)
    for _, row in language_stats.iterrows():
        lang = row['language']
        pc1 = row['llm_PC1']
        name = lang_names.get(lang, lang)
        print(f"{name}: PC1 = {pc1:.2f}")
    
    plt.close()

if __name__ == '__main__':
    main()
