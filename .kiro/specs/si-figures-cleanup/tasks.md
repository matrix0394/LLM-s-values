# Implementation Plan

- [x] 1. 数据时效性检查与刷新






  - [x] 1.1 检查PCA数据文件日期，确认Table_S5, S6, S7是否为最新

    - 验证SI/pca/目录下的CSV文件修改日期
    - _Requirements: 6.1_
  - [x] 1.2 检查并重新生成stage0_vs_stage3分析数据


    - 运行analysis/stage0_vs_stage3_distance.py
    - 确保distances_detailed.csv和english_advantage_average.csv是最新的
    - _Requirements: 6.3_
  - [ ]* 1.3 检查cultural_distance_analysis.csv是否需要更新
    - 比较文件日期与PCA数据日期
    - _Requirements: 6.2_

- [x] 2. 创建S4-S8生成脚本包装器





  - [x] 2.1 创建generate_figs4_response.py


    - 包装analysis/generate_modal_profile_figures.py
    - 输出到SI/figures/S4_Model_response_analysis/
    - 使用si_config.py的样式配置
    - _Requirements: 4.1, 5.1, 5.2_
  - [x] 2.2 创建generate_figs5_english_advantage.py


    - 包装analysis/generate_publication_figures.py的fig1, fig2函数
    - 输出到SI/figures/S5_English_advantage_analysis/
    - _Requirements: 4.2, 5.1_
  - [x] 2.3 创建generate_figs6_orientalism.py


    - 包装analysis/visualize_orientalism.py
    - 输出到SI/figures/S6_Orientalism_analysis/
    - _Requirements: 4.3, 5.1_


  - [x] 2.4 创建generate_figs7_east_asia.py





    - 包装analysis/visualize_orientalism.py的东亚相关函数
    - 生成S7A, S7B, S7C三张图


    - 输出到SI/figures/S7_East_Asia_analysis/
    - _Requirements: 4.4, 5.1_
  - [x] 2.5 创建generate_figs8_model_analysis.py


    - 包装analysis/generate_publication_figures.py的fig3, fig5函数
    - 仅生成S8A和S8C（排除重复的S8B和S8D）
    - 输出到SI/figures/S8_Model_analysis/
    - _Requirements: 4.5, 5.1_
  - [x] 2.6 创建generate_figs_summary.py





    - 包装scripts/generate_si_figures.py的summary函数
    - 输出到SI/figures/summary/
    - _Requirements: 4.6, 5.1_

- [x] 3. Checkpoint - 确保所有脚本可运行





  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. 重新生成所有S4-S8图片





  - [x] 4.1 运行generate_figs4_response.py生成S4图片


    - 验证输出4张图片：S4A, S4B, S4C, S4D
    - _Requirements: 4.1_
  - [x] 4.2 运行generate_figs5_english_advantage.py生成S5图片


    - 验证输出2张图片：S5A, S5B (或S5C)
    - _Requirements: 4.2_
  - [x] 4.3 运行generate_figs6_orientalism.py生成S6图片


    - 验证输出3张图片：S6A, S6B (或S6C), S6D (或其他)
    - _Requirements: 4.3_
  - [x] 4.4 运行generate_figs7_east_asia.py生成S7图片


    - 验证输出3张图片：S7A, S7B, S7C
    - _Requirements: 4.4_
  - [x] 4.5 运行generate_figs8_model_analysis.py生成S8图片


    - 验证输出2张图片：S8A, S8C（不包含S8B和S8D）
    - _Requirements: 4.5_

  - [x] 4.6 运行generate_figs_summary.py生成summary图片

    - 验证输出6张图片：Sx1-Sx6
    - _Requirements: 4.6_

- [x] 5. 删除冗余图片






  - [x] 5.1 删除S8B_heatmap_model_language（与Sx3重复）

    - 删除SI/figures/S8_Model_analysis/FigS8B_heatmap_model_language.*
    - _Requirements: 3.1_

  - [x] 5.2 删除S8D_consistency_distribution（与Sx6重复）

    - 删除SI/figures/S8_Model_analysis/FigS8D_consistency_distribution.*
    - _Requirements: 3.3_

- [x] 6. 更新文档





  - [x] 6.1 更新SI/figures/README.md


    - 更新目录结构
    - 更新脚本映射表
    - 添加新脚本的说明
    - _Requirements: 7.1, 7.2_
  - [x] 6.2 更新PNAS_RECOMMENDED_FIGURES.md


    - 移除对S8B和S8D的引用
    - 确认S7保留3张图
    - _Requirements: 7.3_
  - [x] 6.3 更新PNAS_SI_FINAL_STRUCTURE.md


    - 更新最终图片数量统计
    - 更新脚本列表
    - _Requirements: 7.4_

- [x] 7. Final Checkpoint - 验证所有图片和文档







  - Ensure all tests pass, ask the user if questions arise.
