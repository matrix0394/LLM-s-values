# Design Document: Study 4 Colonial History Analysis Improvement

## Overview

This design addresses the methodological issues in the current Study 4 implementation and implements the three-level analysis framework described in `paper_pnas_methods_v2.md`. The key improvements are:

1. **Separate Hong Kong and Macao analysis** instead of averaging them together
2. **Use correct statistical comparison** (English advantage, not absolute distance)
3. **Implement three-level analysis**: direct comparison, regression with controls, mediation analysis
4. **Handle African data limitations** (British-colonized countries lack native language data)
5. **Properly report Latin American significant finding** (F=3.956, p=0.0204)

## Architecture

### High-Level Design

```
Input Data (CSV)
    ↓
Data Loading & Validation
    ↓
English Advantage Calculation
    ↓
Three Analysis Levels:
    1. Direct Group Comparisons
    2. Regression Analysis (with controls)
    3. Mediation Analysis (optional)
    ↓
Visualization Generation
    ↓
Results Output (console + figures)
```

### Key Components

1. **Data Loader**: Load PCA coordinates and calculate cultural distances
2. **English Advantage Calculator**: Compute relative improvement metrics
3. **Statistical Analyzer**: Implement three-level analysis framework
4. **Visualization Generator**: Create figures matching orientalism style
5. **Results Reporter**: Format and output statistical results



## Components and Interfaces

### 1. Data Loader Component

**Purpose**: Load and validate input data from CSV files.

**Interface**:
```python
def load_pca_data(filepath: str, exclude_models: List[str]) -> pd.DataFrame:
    """Load LLM roleplay PCA coordinates and filter out low-quality models."""
    
def load_ivs_coordinates(filepath: str) -> Dict[str, Tuple[float, float]]:
    """Load IVS ground truth coordinates for cultural distance calculation."""
    
def calculate_cultural_distance(row: pd.Series, ivs_dict: Dict) -> float:
    """Calculate Euclidean distance between LLM and IVS coordinates."""
```

**Data Schema**:
- Input: `SI/pca/Table_S7_LLM_roleplay_PCA_coordinates.csv`
- Columns: model_name, country, language, PC1, PC2
- Output: DataFrame with added `cultural_distance` column

### 2. English Advantage Calculator

**Purpose**: Compute English advantage metric for each country.

**Interface**:
```python
def calculate_english_advantage(
    df: pd.DataFrame, 
    country: str, 
    native_lang: str,
    english_lang: str = 'en'
) -> Dict[str, float]:
    """
    Calculate English advantage for a country.
    
    Returns:
        {
            'english_advantage': float,  # Percentage
            'english_distance': float,
            'native_distance': float,
            'n_models': int
        }
    """
```

**Formula**:
```
English Advantage (%) = 100 × (Distance_native - Distance_english) / Distance_native
```

Positive values indicate English produces better cultural alignment.



### 3. Statistical Analyzer Component

**Purpose**: Implement three-level analysis framework.

#### Level 1: Direct Group Comparisons

**Experiment 4a: Hong Kong vs Macao**
```python
def analyze_hk_macao_comparison(df: pd.DataFrame) -> Dict:
    """
    Compare Hong Kong's English advantage with Macao's Portuguese advantage.
    
    Returns:
        {
            'hk_english_advantage': float,
            'macao_portuguese_advantage': float,
            't_statistic': float,
            'p_value': float,
            'cohens_d': float,
            'n_hk': int,
            'n_macao': int
        }
    """
```

**Experiment 4b: Latin American Language Variants**
```python
def analyze_latin_america_variants(df: pd.DataFrame) -> Dict:
    """
    Compare English advantage across Spanish, Portuguese, French countries.
    
    Returns:
        {
            'spanish_advantage': float,
            'portuguese_advantage': float,
            'french_advantage': float,
            'f_statistic': float,
            'p_value': float,
            'eta_squared': float,
            'tukey_results': List[Tuple]  # Pairwise comparisons
        }
    """
```

**Experiment 4c: African Colonial History**
```python
def analyze_african_colonial_history(df: pd.DataFrame) -> Dict:
    """
    Compare English advantage between British-colonized and non-colonized African countries.
    
    Note: British-colonized countries (Kenya, Nigeria, etc.) only have en-native data,
    so we cannot compute English advantage. This analysis has data limitations.
    
    Returns:
        {
            'status': 'data_limitation',
            'reason': str,
            'alternative_analysis': Optional[Dict]
        }
    """
```



#### Level 2: Regression Analysis with Controls

**Purpose**: Test whether colonial history predicts English advantage after controlling for confounds.

**Interface**:
```python
def perform_regression_analysis(
    df: pd.DataFrame,
    control_data: pd.DataFrame  # GDP, internet, EF EPI, region
) -> Dict:
    """
    Multiple linear regression: English Advantage ~ Colonial History + Controls
    
    Predictors:
        - british_colonial: binary (0/1)
        - french_colonial: binary (0/1)
        - portuguese_colonial: binary (0/1)
        - spanish_colonial: binary (0/1)
        - log_gdp_per_capita: continuous
        - internet_penetration: continuous (%)
        - english_proficiency: continuous (EF EPI score)
        - region_dummies: categorical fixed effects
    
    Returns:
        {
            'coefficients': Dict[str, float],  # β for each predictor
            'std_errors': Dict[str, float],
            't_statistics': Dict[str, float],
            'p_values': Dict[str, float],
            'confidence_intervals': Dict[str, Tuple[float, float]],
            'r_squared': float,
            'adjusted_r_squared': float,
            'incremental_r_squared': Dict[str, float]  # R² contribution
        }
    """
```

**Control Variables Data Sources**:
- GDP per capita: World Bank 2023 data
- Internet penetration: ITU 2023 data
- English proficiency: EF EPI 2023 scores
- Geographic regions: From existing `country_codes.json`

**Implementation Notes**:
- Use `statsmodels.api.OLS` for regression
- Standardize continuous predictors for interpretability
- Check for multicollinearity (VIF < 10)
- Report both unstandardized and standardized coefficients



#### Level 3: Mediation Analysis

**Purpose**: Test whether colonial history effects are mediated by contemporary English usage.

**Interface**:
```python
def perform_mediation_analysis(
    df: pd.DataFrame,
    mediator_data: pd.DataFrame  # English content proportion from Common Crawl
) -> Dict:
    """
    Causal mediation analysis (Imai et al., 2010).
    
    Model:
        Colonial History → English Usage → English Advantage
                        ↘ (direct effect) ↗
    
    Returns:
        {
            'acme': float,  # Average Causal Mediation Effect
            'acme_ci': Tuple[float, float],  # 95% CI
            'ade': float,   # Average Direct Effect
            'ade_ci': Tuple[float, float],
            'total_effect': float,
            'proportion_mediated': float,
            'interpretation': str
        }
    """
```

**Implementation Notes**:
- Use `mediation` package or implement bootstrap-based approach
- Mediator: Proportion of internet content in English (Common Crawl)
- If Common Crawl data unavailable, acknowledge as future work
- Bootstrap 1000 iterations for confidence intervals

**Interpretation**:
- Large ACME / small ADE → Colonial effects operate through contemporary usage
- Small ACME / large ADE → Persistent colonial legacy independent of current usage



## Data Models

### Country Colonial History Mapping

```python
COLONIAL_HISTORY = {
    # East Asia
    'Hong Kong': {'colonizer': 'British', 'colonial_lang': 'en-native', 'native_lang': 'zh-cn'},
    'Macao': {'colonizer': 'Portuguese', 'colonial_lang': 'pt', 'native_lang': 'zh-cn'},
    
    # Latin America - Spanish
    'Argentina': {'colonizer': 'Spanish', 'colonial_lang': 'es', 'native_lang': 'es'},
    'Bolivia': {'colonizer': 'Spanish', 'colonial_lang': 'es', 'native_lang': 'es'},
    'Chile': {'colonizer': 'Spanish', 'colonial_lang': 'es', 'native_lang': 'es'},
    'Colombia': {'colonizer': 'Spanish', 'colonial_lang': 'es', 'native_lang': 'es'},
    'Ecuador': {'colonizer': 'Spanish', 'colonial_lang': 'es', 'native_lang': 'es'},
    'Guatemala': {'colonizer': 'Spanish', 'colonial_lang': 'es', 'native_lang': 'es'},
    'Mexico': {'colonizer': 'Spanish', 'colonial_lang': 'es', 'native_lang': 'es'},
    'Nicaragua': {'colonizer': 'Spanish', 'colonial_lang': 'es', 'native_lang': 'es'},
    'Peru': {'colonizer': 'Spanish', 'colonial_lang': 'es', 'native_lang': 'es'},
    'Uruguay': {'colonizer': 'Spanish', 'colonial_lang': 'es', 'native_lang': 'es'},
    'Venezuela': {'colonizer': 'Spanish', 'colonial_lang': 'es', 'native_lang': 'es'},
    
    # Latin America - Portuguese
    'Brazil': {'colonizer': 'Portuguese', 'colonial_lang': 'pt', 'native_lang': 'pt'},
    
    # Latin America - French
    'Haiti': {'colonizer': 'French', 'colonial_lang': 'fr', 'native_lang': 'fr'},
    
    # Africa - British (Note: these countries only have en-native data)
    'Kenya': {'colonizer': 'British', 'colonial_lang': 'en-native', 'native_lang': None},
    'Nigeria': {'colonizer': 'British', 'colonial_lang': 'en-native', 'native_lang': None},
    'Ghana': {'colonizer': 'British', 'colonial_lang': 'en-native', 'native_lang': None},
    'South Africa': {'colonizer': 'British', 'colonial_lang': 'en-native', 'native_lang': None},
    'Zimbabwe': {'colonizer': 'British', 'colonial_lang': 'en-native', 'native_lang': None},
    'Zambia': {'colonizer': 'British', 'colonial_lang': 'en-native', 'native_lang': None},
    
    # Africa - Non-British
    'Ethiopia': {'colonizer': None, 'colonial_lang': None, 'native_lang': 'am'},  # Amharic
    'Morocco': {'colonizer': 'French', 'colonial_lang': 'fr', 'native_lang': 'ar'},
    'Algeria': {'colonizer': 'French', 'colonial_lang': 'fr', 'native_lang': 'ar'},
}
```

### Results Data Structure

```python
@dataclass
class ExperimentResult:
    experiment_name: str
    group_comparisons: Dict[str, GroupStats]
    statistical_test: StatisticalTest
    effect_size: EffectSize
    visualization_path: Optional[str]
    
@dataclass
class GroupStats:
    group_name: str
    mean: float
    std: float
    se: float
    ci_lower: float
    ci_upper: float
    n: int
    
@dataclass
class StatisticalTest:
    test_type: str  # 't-test', 'ANOVA', 'regression'
    statistic: float
    p_value: float
    df: Union[int, Tuple[int, int]]
    
@dataclass
class EffectSize:
    measure: str  # 'cohens_d', 'eta_squared'
    value: float
    interpretation: str  # 'small', 'medium', 'large'
```



## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: English advantage calculation consistency

*For any* country with both English and native language data, calculating English advantage twice with the same data should produce identical results.

**Validates: Requirements 3.1**

### Property 2: Statistical test appropriateness

*For any* two-group comparison with independent samples, using independent-samples t-test should produce valid p-values between 0 and 1.

**Validates: Requirements 5.1**

### Property 3: Effect size bounds

*For any* Cohen's d calculation, the absolute value should be non-negative and typically less than 5 (extreme values indicate data issues).

**Validates: Requirements 5.3**

### Property 4: Regression coefficient consistency

*For any* regression model, adding control variables should not cause colonial history coefficients to become undefined or infinite.

**Validates: Requirements 5.2**

### Property 5: Data availability validation

*For any* country in the African British-colonized group, attempting to calculate English advantage should detect the absence of native language data and return appropriate error/limitation status.

**Validates: Requirements 2.1, 2.4**

### Property 6: Visualization data integrity

*For any* generated visualization, the data points displayed should exactly match the statistical analysis results (no data transformation errors).

**Validates: Requirements 4.1, 4.2**



## Error Handling

### Data Validation Errors

1. **Missing Language Data**
   - Error: Country lacks required native language or English data
   - Handling: Skip country with warning, document in limitations
   - Example: African British-colonized countries

2. **Insufficient Sample Size**
   - Error: Fewer than 3 models for a country-language combination
   - Handling: Flag as unreliable, report with caveat

3. **Invalid Distance Values**
   - Error: Cultural distance is negative or NaN
   - Handling: Exclude observation, log warning

### Statistical Analysis Errors

1. **Regression Singularity**
   - Error: Perfect multicollinearity in predictors
   - Handling: Remove redundant predictors, report VIF values

2. **Non-convergence**
   - Error: Mediation analysis bootstrap fails to converge
   - Handling: Increase iterations, simplify model, or skip mediation

3. **Assumption Violations**
   - Error: Normality or homoscedasticity violated
   - Handling: Report non-parametric alternatives (Mann-Whitney U)

### Visualization Errors

1. **Missing Data Points**
   - Error: Country has no data for visualization
   - Handling: Exclude from plot, note in caption

2. **Extreme Outliers**
   - Error: Values exceed plot bounds
   - Handling: Adjust axis limits or use log scale



## Testing Strategy

### Unit Tests

1. **English Advantage Calculation**
   - Test with known input/output pairs
   - Test edge cases (zero distance, equal distances)
   - Test with missing data

2. **Statistical Functions**
   - Test t-test with synthetic data
   - Test ANOVA with known F-statistic
   - Test Cohen's d calculation

3. **Data Loading**
   - Test CSV parsing
   - Test data filtering (exclude bad models)
   - Test distance calculation

### Integration Tests

1. **End-to-End Experiment 4a**
   - Load real data
   - Calculate Hong Kong and Macao advantages
   - Perform t-test
   - Generate visualization
   - Verify output format

2. **End-to-End Experiment 4b**
   - Load Latin American data
   - Calculate advantages by colonial language
   - Perform ANOVA and Tukey HSD
   - Verify significant result (p=0.0204)

3. **Regression Pipeline**
   - Load control variables
   - Merge with English advantage data
   - Run regression
   - Verify coefficient signs and significance

### Property-Based Tests

These tests will use random data generation to verify universal properties:

1. **Property 1 Test**: Generate random distance pairs, calculate advantage twice, verify equality
2. **Property 2 Test**: Generate random two-group data, verify t-test p-value in [0,1]
3. **Property 5 Test**: For any African British-colonized country, verify data limitation detection



## Visualization Design

### Figure 1: East Asian Colonial Gradient (Improved)

**Purpose**: Show Hong Kong and Macao separately in East Asian context.

**Design**:
- Horizontal bar chart
- Countries: Hong Kong, Macao, China, Japan, Korea
- X-axis: English advantage (%)
- Color scheme: Red (English advantage), Green (native advantage)
- Annotations: Colonial history markers for HK and Macao
- Error bars: 95% confidence intervals

**Style**: Match `visualize_orientalism.py` East Asia gradient

### Figure 2: Latin American Language Variants

**Purpose**: Show significant differences across colonial languages.

**Design**:
- Grouped bar chart with error bars
- Groups: Spanish (n=11), Portuguese (n=1), French (n=1)
- Y-axis: English advantage (%)
- Significance markers: * for p<0.05
- Annotations: ANOVA F-statistic and p-value

**Key Finding**: Highlight Haiti (French) significantly higher than Spanish countries

### Figure 3: Hong Kong vs Macao Direct Comparison

**Purpose**: Visualize the natural experiment comparing colonial languages.

**Design**:
- Side-by-side bar chart
- Left: Hong Kong English advantage
- Right: Macao Portuguese advantage
- Error bars: 95% CI
- Statistical annotation: t-statistic, p-value, Cohen's d

### Figure 4: Regression Coefficients Plot

**Purpose**: Show colonial history effects after controlling for confounds.

**Design**:
- Forest plot style
- Y-axis: Predictor variables (British, French, Portuguese, Spanish colonial history)
- X-axis: Standardized regression coefficients (β)
- Error bars: 95% confidence intervals
- Vertical line at zero
- Significance markers

### Figure 5: Integration with Orientalism Analysis

**Purpose**: Show how colonial history fits into broader geographic gradient.

**Design**:
- Enhanced version of orientalism gradient chart
- Overlay colonial history markers (different shapes/colors)
- Highlight Hong Kong, Macao, Haiti with annotations
- Show how colonial history modulates regional patterns

**Implementation**: Extend `visualize_orientalism.py` functions



## Implementation Notes

### Dependencies

```python
# Core
import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import ttest_ind, f_oneway
import statsmodels.api as sm
from statsmodels.stats.multicomp import pairwise_tukeyhsd

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns

# Optional (for mediation)
# from mediation import CausalMediation
```

### File Structure

```
analysis/language/
├── analyze_colonial_history_v4.py          # Main analysis script
├── colonial_utils.py                       # Utility functions
│   ├── calculate_english_advantage()
│   ├── perform_ttest()
│   ├── perform_anova()
│   └── perform_regression()
└── colonial_visualizations.py              # Visualization functions
    ├── plot_east_asian_gradient()
    ├── plot_latin_america_variants()
    ├── plot_hk_macao_comparison()
    └── plot_regression_coefficients()

results/analysis/colonial_history/
├── experiment_4a_hk_macao.png
├── experiment_4b_latin_america.png
├── experiment_4c_african_limitation.txt
├── regression_results.csv
└── summary_statistics.txt
```

### Key Decisions

1. **African Analysis**: Document as data limitation rather than force incorrect analysis
2. **Regression Controls**: Start with available data (GDP, region), add others if feasible
3. **Mediation Analysis**: Mark as optional/future work if Common Crawl data unavailable
4. **Visualization Priority**: Focus on Experiments 4a and 4b (significant findings)

### Performance Considerations

- Data loading: ~1-2 seconds for CSV files
- Statistical analysis: <1 second per experiment
- Visualization generation: ~2-3 seconds per figure
- Total runtime: <30 seconds for complete analysis

### Backward Compatibility

- Keep `analyze_colonial_history_v3.py` for reference
- New script `analyze_colonial_history_v4.py` implements corrected methods
- Document differences in comments

