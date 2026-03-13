# Implementation Plan

This plan breaks down the Study 4 colonial history analysis improvement into discrete, manageable coding tasks. Each task builds incrementally on previous steps.

## Task List

- [x] 1. Set up project structure and utility functions






  - Create `analysis/language/colonial_utils.py` with helper functions
  - Implement `calculate_english_advantage()` function
  - Implement `calculate_cultural_distance()` function
  - Add colonial history mapping dictionary
  - _Requirements: 3.1, 3.2_

- [ ]* 1.1 Write unit tests for utility functions
  - Test `calculate_english_advantage()` with known inputs
  - Test edge cases (zero distance, equal distances, missing data)
  - Test `calculate_cultural_distance()` calculation
  - _Requirements: 3.1_

- [x] 2. Implement data loading and validation


  - Create data loader in `analyze_colonial_history_v4.py`
  - Load PCA coordinates from CSV
  - Load IVS ground truth coordinates
  - Filter out low-quality models (llama-3.2-3b, qwen3-1.7b)
  - Calculate cultural distances for all observations
  - _Requirements: 3.1_

- [ ]* 2.1 Write unit tests for data loading
  - Test CSV parsing
  - Test model filtering
  - Test distance calculation integration
  - _Requirements: 3.1_


- [x] 3. Implement Experiment 4a: Hong Kong vs Macao comparison




  - Calculate Hong Kong's English advantage (en-native vs zh-cn)
  - Calculate Macao's Portuguese advantage (pt vs zh-cn)
  - Perform independent-samples t-test comparing the two advantages
  - Calculate Cohen's d effect size
  - Report results with 95% confidence intervals
  - _Requirements: 1.1, 1.2, 3.2, 5.1_

- [ ]* 3.1 Write property test for Experiment 4a
  - **Property 2: Statistical test appropriateness**
  - **Validates: Requirements 5.1**
  - Generate random two-group data, verify t-test produces valid p-value [0,1]

- [ ]* 3.2 Write unit tests for Experiment 4a
  - Test with synthetic Hong Kong and Macao data
  - Verify t-statistic calculation
  - Verify Cohen's d calculation
  - _Requirements: 1.1, 5.1_

- [x] 4. Implement Experiment 4b: Latin American language variants



  - Calculate English advantage for Spanish-speaking countries (n=11)
  - Calculate English advantage for Portuguese-speaking Brazil
  - Calculate English advantage for French-speaking Haiti
  - Perform one-way ANOVA across three groups
  - Perform Tukey HSD post-hoc pairwise comparisons
  - Calculate eta-squared effect size
  - Report significant finding (F=3.956, p=0.0204)
  - _Requirements: 5.1, 6.1, 6.2, 6.3_

- [ ]* 4.1 Write unit tests for Experiment 4b
  - Test ANOVA with synthetic three-group data
  - Test Tukey HSD pairwise comparisons
  - Verify eta-squared calculation
  - _Requirements: 5.1, 6.2_


- [x] 5. Handle Experiment 4c: African colonial history data limitation
  - Detect that British-colonized African countries lack native language data
  - Document this as a methodological limitation
  - Implement data availability check function
  - Generate limitation report explaining why analysis cannot proceed as designed
  - Suggest alternative interpretations in output
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ]* 5.1 Write property test for data limitation detection
  - **Property 5: Data availability validation**
  - **Validates: Requirements 2.1, 2.4**
  - For any African British-colonized country, verify detection of missing native language data

- [ ] 6. Implement regression analysis with control variables
  - Create control variables dataset (GDP, internet penetration, EF EPI, region)
  - Code colonial history as binary variables (British, French, Portuguese, Spanish)
  - Merge control data with English advantage data
  - Implement multiple linear regression using statsmodels
  - Calculate regression coefficients (β), standard errors, t-statistics, p-values
  - Calculate 95% confidence intervals for coefficients
  - Calculate R² and adjusted R²
  - Calculate incremental R² for colonial history variables
  - Check for multicollinearity (VIF < 10)
  - _Requirements: 5.2, 5.3_

- [ ]* 6.1 Write unit tests for regression analysis
  - Test regression with synthetic data
  - Test coefficient extraction
  - Test VIF calculation
  - Verify R² calculation
  - _Requirements: 5.2_


- [ ] 7. Implement mediation analysis (optional)
  - Check if Common Crawl data is available
  - If available: implement causal mediation analysis (Imai et al., 2010)
  - Calculate ACME (average causal mediation effect)
  - Calculate ADE (average direct effect)
  - Calculate proportion mediated
  - Use bootstrap for confidence intervals (1000 iterations)
  - If unavailable: document as future work in output
  - _Requirements: 5.4_

- [x] 8. Create visualization functions


  - Create `analysis/language/colonial_visualizations.py`
  - Implement `plot_east_asian_gradient()` - Hong Kong, Macao, China, Japan, Korea
  - Implement `plot_latin_america_variants()` - Spanish, Portuguese, French groups
  - Implement `plot_hk_macao_comparison()` - Side-by-side comparison
  - Implement `plot_regression_coefficients()` - Forest plot of β coefficients
  - Use consistent color scheme (red=English advantage, green=native advantage)
  - Add error bars (95% CI) to all plots
  - Add significance markers (* for p<0.05)
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ]* 8.1 Write property test for visualization data integrity
  - **Property 6: Visualization data integrity**
  - **Validates: Requirements 4.1, 4.2**
  - For any generated visualization, verify data points match statistical results


- [x] 9. Generate visualizations for all experiments


  - Generate Figure 1: East Asian colonial gradient (improved)
  - Generate Figure 2: Latin American language variants with ANOVA results
  - Generate Figure 3: Hong Kong vs Macao direct comparison
  - Generate Figure 4: Regression coefficients plot (if regression completed)
  - Save all figures to `results/analysis/colonial_history/`
  - _Requirements: 4.1, 4.2, 4.3_

- [ ] 10. Integrate with orientalism visualization
  - Extend `visualize_orientalism.py` to add colonial history markers
  - Annotate Hong Kong and Macao in East Asian gradient
  - Add colonial history overlay to geographic gradient chart
  - Generate Figure 5: Integrated orientalism + colonial history
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 11. Implement results reporting

  - Create formatted console output for all experiments
  - Report Experiment 4a: HK vs Macao with t-test, p-value, Cohen's d
  - Report Experiment 4b: Latin America with ANOVA, Tukey HSD, eta-squared
  - Report Experiment 4c: African limitation with explanation
  - Report regression results: coefficients, CIs, R², incremental R²
  - Report mediation results if available: ACME, ADE, proportion mediated
  - Save summary statistics to `results/analysis/colonial_history/summary_statistics.txt`
  - _Requirements: 5.5, 6.4, 6.5_

- [ ] 12. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.


- [x] 13. Documentation and final integration


  - Add docstrings to all functions
  - Add comments explaining key statistical decisions
  - Document differences from v3 in script header
  - Create README explaining how to run the analysis
  - Document data requirements and optional dependencies
  - _Requirements: All_

- [ ]* 13.1 Write integration tests
  - Test end-to-end Experiment 4a pipeline
  - Test end-to-end Experiment 4b pipeline
  - Test regression pipeline (if control data available)
  - Verify all output files are generated correctly

- [ ] 14. Final checkpoint - Verify all requirements met
  - Ensure all tests pass, ask the user if questions arise.
  - Review all 7 requirements are satisfied
  - Verify visualizations match orientalism style
  - Confirm statistical methods match methods document
  - Check that African limitation is properly documented

