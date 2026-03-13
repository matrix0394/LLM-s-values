# Supporting Information (SI) Outline

## SI Appendix Structure

### SI Materials and Methods

#### S1. Detailed Model Specifications
**Table S1**: Complete list of 21 LLMs with specifications
- Model name and version
- Developer/organization
- Parameter count (where available)
- API access date range
- Temperature setting (0.1 for all)
- Context window size
- Training data cutoff date (where disclosed)

#### S2. Country and Language Selection
**Table S2**: Complete country-language mapping
- 66 countries evaluated
- Official language(s) for each country
- Cultural region classification (8 regions)
- Number of models tested per country
- Total roleplay sessions per country

**Figure S1**: Geographic distribution of evaluated countries
- World map showing 66 countries color-coded by cultural region
- Indicates which countries have multiple official languages

#### S3. World Values Survey Question Details
**Table S3**: Ten WVS questions used in study
- Question ID (e.g., A008, F063)
- Full question text in English
- Response scale and options
- Theoretical dimension (PC1 or PC2)
- Factor loading on each dimension

**Table S4**: Question translations
- All 10 questions translated into 13 languages
- Translation methodology (professional translators + back-translation validation)
- Language-specific adaptations (if any)

#### S4. Response Quality Control Details
**Table S5**: Response validation statistics
- Valid response rate by model (should be >95%)
- Invalid response rate by question type
- Retry success rate (% of initially invalid responses recovered)
- Reasons for invalid responses (format errors, refusals, out-of-range values)

**Figure S2**: Response quality by model and language
- Heatmap showing valid response rate for 21 models × 13 languages
- Identifies any systematic quality issues

#### S5. PCA Methodology Validation
**Figure S3**: PCA validation on IVS ground-truth data
- Scree plot showing variance explained by first 10 components
- Biplot showing question loadings on PC1 and PC2
- Comparison with published Inglehart-Welzel map

**Table S6**: PCA model parameters
- Loading matrix C (10×2)
- Standardization parameters (means and SDs for each question)
- Varimax rotation matrix
- Rescaling coefficients (PC1: 1.81x + 0.38; PC2: 1.61x - 0.01)
- Variance explained by PC1 and PC2

**Figure S4**: Validation of fixed PCA approach
- Comparison of coordinates when PCA is refit vs. using fixed model
- Demonstrates coordinate stability across conditions

### SI Results

#### S6. Complete Statistical Results
**Table S7**: Full results for all 48 non-English-native countries
- Country name
- Native language(s)
- Cultural region
- Mean English advantage (%)
- Standard error
- t-statistic
- p-value
- Cohen's d
- 95% confidence interval
- Number of models tested

**Table S8**: Results by cultural region
- Regional aggregation of Table S7
- Includes Bonferroni-corrected p-values for multiple comparisons

#### S7. Model-Specific Results
**Table S9**: English advantage by model
- Each of 21 models as rows
- Mean English advantage across all non-English-native countries
- Standard deviation
- Minimum and maximum values
- Number of countries tested

**Figure S5**: Model-specific English advantage distributions
- Box plots showing distribution of English advantage for each model
- Identifies models with highest/lowest Orientalism

#### S8. Robustness Checks
**Table S10**: Robustness check results
- Comparison of parametric (t-test) vs. nonparametric (Wilcoxon) tests
- Results with and without outliers
- Binomial sign test results
- Sensitivity to different distance metrics (Euclidean vs. Manhattan vs. Mahalanobis)

**Figure S6**: Outlier analysis
- Scatter plots showing cultural distances with outliers highlighted
- Demonstrates that results are robust to outlier removal

#### S9. Additional Visualizations
**Figure S7**: Complete cultural map with all entities
- Scatter plot showing IVS countries (gray), LLM intrinsic positions (Stage 1, colored by origin), and LLM roleplay positions (Stage 3, colored by language)
- Demonstrates overall distribution of cultural representations

**Figure S8**: Language family analysis
- Phylogenetic tree of 13 languages with English advantage mapped onto branches
- Tests whether linguistic distance from English predicts Orientalism

**Figure S9**: Model size analysis
- English advantage for Islamic countries by model parameter count
- Tests whether larger models show more or less Orientalism

**Figure S10**: Temporal analysis (if applicable)
- English advantage by model release date
- Tests whether newer models show reduced Orientalism

### SI Discussion

#### S10. Alternative Explanations
**Text**: Discussion of alternative explanations for observed patterns
- Linguistic complexity hypothesis (Arabic script, morphology)
- Translation quality hypothesis (errors in native-language prompts)
- Cultural distance hypothesis (models better at representing culturally proximate societies)
- Evidence for and against each alternative

#### S11. Ethical Considerations
**Text**: Discussion of ethical implications
- Potential harms of digital Orientalism
- Responsibilities of AI developers
- Recommendations for users in non-Western countries
- Limitations of our study in capturing all forms of cultural bias

### SI References
Complete bibliography for all citations in SI Appendix

---

## SI Data Availability

### Data Files to Include
1. **country_scores_pca.json**: Ground-truth IVS coordinates for 109 countries
2. **llm_pca_entity_scores.pkl**: Stage 1 intrinsic model positions
3. **roleplay_ml_pca_entity_scores_latest.pkl**: Stage 3 roleplay positions (778 entities)
4. **distances_detailed.xlsx**: Complete distance calculations for all model-country-language combinations
5. **english_advantage_average.xlsx**: Aggregated English advantage by country

### Code Availability
- GitHub repository with all analysis scripts
- Jupyter notebooks for reproducing figures
- PCA analysis pipeline
- Statistical analysis scripts

### Model Access
- API endpoints and versions for all 21 models
- Exact prompts used for each language
- Temperature and other hyperparameter settings

---

## Estimated SI Length
- **Text**: ~3,000 words
- **Tables**: 10 tables
- **Figures**: 10 figures
- **Total pages**: ~15-20 pages (PNAS SI format)

---

## Key SI Highlights for Main Text

When referencing SI in main text, use format: "(SI Appendix, Table S1)" or "(SI Appendix, Fig. S3)"

Main text should reference:
- Table S1 (model specifications) in Methods
- Table S2 (country-language mapping) in Methods
- Table S3 (WVS questions) in Methods
- Table S4 (response quality) in Methods
- Figure S3 (PCA validation) in Methods
- Table S7 (complete country results) in Results
- Figure S4 (model × region heatmap) in Results
- Table S10 (robustness checks) in Results
