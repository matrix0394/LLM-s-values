"""
生成开题答辩 PPT 第三部分（研究方案设计）用的专用图：
- 图3：PPCA 与统一文化坐标示意（对应 3.2）
- 图4：文化距离与英语优势示意（对应 3.3）

风格参照 research_framework.py 和 data_flow_v3.py，走学术海报风。
"""

import os

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import matplotlib.patches as mpatches
import numpy as np

# 全局风格设置（与现有脚本保持一致）
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 9
plt.rcParams["font.family"] = "sans-serif"

OUTPUT_DIR = "results/analysis/visualization"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def draw_data_pipeline_ppt_figure():
    """图2：数据来源与处理流程示意（用于 3.1）"""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_xlim(0, 6)
    ax.set_ylim(-0.3, 6.3)  # 上下各留一点空白，避免箭头被裁剪
    ax.axis("off")

    ax.text(3, 5.8, "数据来源与处理流程", ha="center", va="center",
            fontsize=14, fontweight="bold")

    # 四个纵向步骤
    steps = [
        ("Step 1", "WVS原始数据\n109国 × 10题"),
        ("Step 2", "LLM文本回答\nStage1/2/3"),
        ("Step 3", "统一编码\n对齐到10个核心题目"),
        ("Step 4", "合并矩阵 & 质控\n6/10题门槛 + 异常值剔除"),
    ]

    y_start = 4.5
    box_h = 0.5
    gap = 0.7

    for i, (title, desc) in enumerate(steps):
        y = y_start - i * (box_h + gap)
        box_width = 2.0  # 明显缩窄蓝色文本框
        x0 = 3.0 - box_width / 2  # 居中放置
        box = FancyBboxPatch((x0, y - box_h / 2), box_width, box_h,
                             boxstyle="round,pad=0.15",
                             edgecolor="#607D8B", facecolor="#E3F2FD", linewidth=1.8)
        ax.add_patch(box)
        ax.text(3.0, y + 0.17, title, ha="center", va="center",
                fontsize=11, fontweight="bold", color="#37474F")
        ax.text(3.0, y - 0.16, desc, ha="center", va="center",
                fontsize=9.2, color="#455A64")

        # 箭头（最后一步下面不画），起点/终点都与文本框留出一点距离
        if i < len(steps) - 1:
            next_y = y_start - (i + 1) * (box_h + gap)
            margin = 0.05
            start_y = y - box_h / 2 - margin       # 略低于当前框底边
            end_y = next_y + box_h / 2 + margin    # 略高于下一框顶边
            arrow = FancyArrowPatch(
                (3.0, start_y),
                (3.0, end_y),
                arrowstyle="->", mutation_scale=14,
                linewidth=1.6, color="#B0BEC5",
            )
            ax.add_patch(arrow)

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "fig2_data_pipeline_ppt.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    print(f"✓ 图2已保存: {out_path}")
    plt.close()


def draw_ppca_ppt_figure():
    """图3：PPCA 与统一文化坐标示意（用于 3.2）"""
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 7)
    ax.axis("off")

    # 标题
    ax.text(7, 6.6, "价值观计算方法", ha="center", va="center",
            fontsize=14, fontweight="bold")

    # 左侧：数据矩阵 X
    box_x = FancyBboxPatch((0.7, 2.2), 3.5, 2.6, boxstyle="round,pad=0.15",
                            edgecolor="#0277BD", facecolor="#E1F5FE", linewidth=2)
    ax.add_patch(box_x)
    ax.text(2.45, 4.4, "数据矩阵 X", ha="center", fontsize=11, fontweight="bold",
            color="#01579B")
    ax.text(2.45, 3.9, "人类国家 + 模型样本", ha="center", fontsize=9, color="#01579B")
    ax.text(2.45, 3.4, "N 个样本 × 10 个核心题目", ha="center", fontsize=8)

    # 矩阵格子示意（在大框内居中）
    cell_w, cell_h = 0.4, 0.4
    gap = 0.45
    n_rows, n_cols = 5, 4
    grid_w = n_cols * gap
    grid_h = n_rows * gap
    base_x = 0.7 + (3.5 - grid_w) / 2  # 在 box_x 内水平居中
    base_y = 2.2 + (2.6 - grid_h) / 2  # 在 box_x 内垂直居中
    for i in range(n_rows):
        for j in range(n_cols):
            ax.add_patch(
                FancyBboxPatch((base_x + gap * j, base_y + gap * i), cell_w, cell_h,
                               boxstyle="round,pad=0.02", edgecolor="#81D4FA",
                               facecolor="#FFFFFF", linewidth=0.8)
            )

    # 中间：PPCA 模型方程
    mid_x = 6.8
    eq_box = FancyBboxPatch((5.0, 2.1), 3.6, 2.8, boxstyle="round,pad=0.15",
                             edgecolor="#6A1B9A", facecolor="#F3E5F5", linewidth=2)
    ax.add_patch(eq_box)
    ax.text(mid_x, 4.5, "PPCA 模型", ha="center", fontsize=11, fontweight="bold",
            color="#4A148C")

    ax.text(mid_x, 3.9, "X = C Z + μ + ε", ha="center",
            fontsize=11, fontweight="bold", family="Times New Roman")
    ax.text(mid_x, 3.4, "Z ~ N(0, I),  ε ~ N(0, σ²I)", ha="center",
            fontsize=9, family="Times New Roman")
    ax.text(mid_x, 2.8, "在概率框架下建模，处理缺失值并提取二维潜在因子 (PC1, PC2)",
            ha="center", fontsize=8.5, color="#4A148C")

    # 左 → 中 箭头
    arrow_lm = FancyArrowPatch((4.2, 3.5), (5.0, 3.5), arrowstyle="->",
                               mutation_scale=18, linewidth=2, color="#455A64")
    ax.add_patch(arrow_lm)

    # 右侧：二维文化坐标
    right_x, right_y = 10.0, 2.0
    coord_box = FancyBboxPatch((right_x, right_y), 3.3, 3.6, boxstyle="round,pad=0.15",
                               edgecolor="#1976D2", facecolor="#E3F2FD", linewidth=2)
    ax.add_patch(coord_box)
    ax.text(right_x + 1.65, right_y + 3.4, "统一文化坐标", ha="center", fontsize=11,
            fontweight="bold", color="#0D47A1")

    # 绘制坐标轴
    ax.plot([right_x + 0.6, right_x + 2.9], [right_y + 1.3, right_y + 1.3],
            "-", linewidth=1.2, color="#455A64")
    ax.plot([right_x + 1.65, right_x + 1.65], [right_y + 0.5, right_y + 2.8],
            "-", linewidth=1.2, color="#455A64")
    ax.text(right_x + 2.95, right_y + 1.3, "PC1", ha="left", fontsize=8,
            color="#455A64", fontweight="bold")
    ax.text(right_x + 1.65, right_y + 2.9, "PC2", ha="center", fontsize=8,
            color="#455A64", fontweight="bold")

    # 轴含义（文字直接说明映射关系，避免视觉混淆）
    ax.text(right_x + 1.65, right_y + 0.6,
            "PC1: 生存 → 自我表达", ha="center", fontsize=7.5, color="#616161")
    ax.text(right_x + 0.6, right_y + 2.45,
            "PC2: 传统 → 世俗理性", ha="left", fontsize=7.5, color="#616161")

    # 随机点作为国家和模型输出示意
    np.random.seed(0)
    xs = np.random.normal(right_x + 1.4, 0.4, 10)
    ys = np.random.normal(right_y + 1.5, 0.4, 10)
    ax.scatter(xs, ys, s=25, c="#1976D2", alpha=0.6,
               edgecolors="#0D47A1", linewidths=1)
    ax.text(right_x + 1.65, right_y + 1.05, "投影后的国家/模型坐标",
            ha="center", fontsize=7.5, color="#455A64", style="italic")

    # 中 → 右 箭头
    arrow_mr = FancyArrowPatch((8.6, 3.5), (right_x, 3.5), arrowstyle="->",
                               mutation_scale=18, linewidth=2, color="#455A64")
    ax.add_patch(arrow_mr)

    # 图例
    legend_elements = [
        mpatches.Patch(facecolor="#E1F5FE", edgecolor="#0277BD", label="数据矩阵 X"),
        mpatches.Patch(facecolor="#F3E5F5", edgecolor="#6A1B9A", label="PPCA 模型"),
        mpatches.Patch(facecolor="#E3F2FD", edgecolor="#1976D2", label="统一文化坐标")
    ]
    ax.legend(handles=legend_elements, loc="lower left", fontsize=8,
              framealpha=0.95, edgecolor="#666", fancybox=True)

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "fig3_ppca_ppt.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    print(f"✓ 图3已保存: {out_path}")
    plt.close()


def draw_metrics_ppt_figure():
    """图4：文化距离与英语优势示意（用于 3.3）"""
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.set_xlim(-2.5, 2.5)
    ax.set_ylim(-2.0, 2.5)
    ax.axis("off")

    # 标题
    ax.text(0, 2.3, "文化距离与英语优势示例", ha="center", va="center",
            fontsize=14, fontweight="bold")

    # 坐标轴
    ax.plot([-2, 2], [0, 0], "-", linewidth=1.2, color="#616161")
    ax.plot([0, 0], [-1.5, 2], "-", linewidth=1.2, color="#616161")
    ax.text(2.1, 0, "PC1", ha="left", fontsize=8, color="#424242", fontweight="bold")
    ax.text(0, 2.05, "PC2", ha="center", fontsize=8, color="#424242", fontweight="bold")

    # 三个点：真实国家 / 母语输出 / 英语输出
    real = np.array([0.2, 0.4])
    native = np.array([-0.8, -0.2])
    english = np.array([0.9, -0.1])

    ax.scatter(*real, s=70, c="#D32F2F", edgecolors="#B71C1C", linewidths=1.5, zorder=5)
    ax.text(real[0] + 0.05, real[1] + 0.05, "真实国家", fontsize=8.5,
            color="#B71C1C")

    ax.scatter(*native, s=60, c="#4CAF50", edgecolors="#2E7D32", linewidths=1.2, zorder=5)
    ax.text(native[0] - 0.05, native[1] - 0.15, "母语模仿", fontsize=8.5,
            ha="right", color="#2E7D32")

    ax.scatter(*english, s=60, c="#1976D2", edgecolors="#0D47A1", linewidths=1.2, zorder=5)
    ax.text(english[0] + 0.05, english[1] - 0.15, "英语模仿", fontsize=8.5,
            ha="left", color="#0D47A1")

    # 文化距离线段
    def draw_distance(p_from, p_to, label, dy):
        ax.plot([p_from[0], p_to[0]], [p_from[1], p_to[1]],
                linestyle="--", linewidth=1.4, color="#9E9E9E")
        mid = (p_from + p_to) / 2
        ax.text(mid[0], mid[1] + dy, label, fontsize=8,
                ha="center", va="center", color="#424242")

    draw_distance(real, native, "d_native", 0.12)
    draw_distance(real, english, "d_english", -0.18)

    # 底部公式框
    formula_box = FancyBboxPatch((-2.3, -1.45), 4.6, 0.9, boxstyle="round,pad=0.15",
                                 edgecolor="#C62828", facecolor="#FFEBEE", linewidth=2)
    ax.add_patch(formula_box)
    ax.text(0, -1.0,
            "d(A,B) = √[(PC1_A − PC1_B)² + (PC2_A − PC2_B)²]",
            ha="center", fontsize=9, family="Times New Roman", color="#C62828")
    ax.text(0, -1.3,
            "Adv = (d_native − d_english) / d_native",
            ha="center", fontsize=9, family="Times New Roman", color="#C62828")

    # 右下角：英语优势直观说明
    ax.text(1.1, 1.6, "若 d_english < d_native → Adv > 0\n英语回答更接近真实国家",
            ha="left", fontsize=8, color="#455A64")

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "fig4_metrics_ppt.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    print(f"✓ 图4已保存: {out_path}")
    plt.close()


if __name__ == "__main__":
    print("开始生成 PPT 方法部分图...")
    draw_data_pipeline_ppt_figure()
    draw_ppca_ppt_figure()
    draw_metrics_ppt_figure()
    print("✓ 所有图已生成，保存在 results/analysis/visualization 目录下。")
