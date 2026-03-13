"""
Utility functions for Study 4: Colonial History Analysis

This module provides helper functions for analyzing colonial history effects
on LLM cultural representations, including:
- English advantage calculation
- Cultural distance calculation
- Colonial history mapping
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, List, Optional


# ============================================================================
# Colonial History Mapping
# ============================================================================

COLONIAL_HISTORY = {
    # East Asia
    'Hong Kong': {
        'colonizer': 'British',
        'colonial_lang': 'en-native',
        'native_lang': 'zh-cn',
        'colonial': True
    },
    'Macao': {
        'colonizer': 'Portuguese',
        'colonial_lang': 'pt',
        'native_lang': 'zh-cn',
        'colonial': True
    },
    'China': {
        'colonizer': None,
        'colonial_lang': 'en',
        'native_lang': 'zh-cn',
        'colonial': False
    },
    'Japan': {
        'colonizer': None,
        'colonial_lang': 'en',
        'native_lang': 'ja',
        'colonial': False
    },
    'Korea, Republic of': {
        'colonizer': None,
        'colonial_lang': 'en',
        'native_lang': 'ko',
        'colonial': False
    },
    
    # Latin America - Spanish
    'Argentina': {
        'colonizer': 'Spanish',
        'colonial_lang': 'es',
        'native_lang': 'es',
        'colonial': True
    },
    'Bolivia': {
        'colonizer': 'Spanish',
        'colonial_lang': 'es',
        'native_lang': 'es',
        'colonial': True
    },
    'Chile': {
        'colonizer': 'Spanish',
        'colonial_lang': 'es',
        'native_lang': 'es',
        'colonial': True
    },
    'Colombia': {
        'colonizer': 'Spanish',
        'colonial_lang': 'es',
        'native_lang': 'es',
        'colonial': True
    },
    'Ecuador': {
        'colonizer': 'Spanish',
        'colonial_lang': 'es',
        'native_lang': 'es',
        'colonial': True
    },
    'Guatemala': {
        'colonizer': 'Spanish',
        'colonial_lang': 'es',
        'native_lang': 'es',
        'colonial': True
    },
    'Mexico': {
        'colonizer': 'Spanish',
        'colonial_lang': 'es',
        'native_lang': 'es',
        'colonial': True
    },
    'Nicaragua': {
        'colonizer': 'Spanish',
        'colonial_lang': 'es',
        'native_lang': 'es',
        'colonial': True
    },
    'Peru': {
        'colonizer': 'Spanish',
        'colonial_lang': 'es',
        'native_lang': 'es',
        'colonial': True
    },
    'Uruguay': {
        'colonizer': 'Spanish',
        'colonial_lang': 'es',
        'native_lang': 'es',
        'colonial': True
    },
    'Venezuela': {
        'colonizer': 'Spanish',
        'colonial_lang': 'es',
        'native_lang': 'es',
        'colonial': True
    },
    
    # Latin America - Portuguese
    'Brazil': {
        'colonizer': 'Portuguese',
        'colonial_lang': 'pt',
        'native_lang': 'pt',
        'colonial': True
    },
    
    # Latin America - French
    'Haiti': {
        'colonizer': 'French',
        'colonial_lang': 'fr',
        'native_lang': 'fr',
        'colonial': True
    },
    
    # Africa - British (Note: these countries only have en-native data)
    'Kenya': {
        'colonizer': 'British',
        'colonial_lang': 'en-native',
        'native_lang': None,
        'colonial': True
    },
    'Nigeria': {
        'colonizer': 'British',
        'colonial_lang': 'en-native',
        'native_lang': None,
        'colonial': True
    },
    'Ghana': {
        'colonizer': 'British',
        'colonial_lang': 'en-native',
        'native_lang': None,
        'colonial': True
    },
    'South Africa': {
        'colonizer': 'British',
        'colonial_lang': 'en-native',
        'native_lang': None,
        'colonial': True
    },
    'Zimbabwe': {
        'colonizer': 'British',
        'colonial_lang': 'en-native',
        'native_lang': None,
        'colonial': True
    },
    'Zambia': {
        'colonizer': 'British',
        'colonial_lang': 'en-native',
        'native_lang': None,
        'colonial': True
    },
    
    # Africa - Non-British
    'Ethiopia': {
        'colonizer': None,
        'colonial_lang': None,
        'native_lang': 'am',  # Amharic
        'colonial': False
    },
    'Morocco': {
        'colonizer': 'French',
        'colonial_lang': 'fr',
        'native_lang': 'ar',
        'colonial': True
    },
    'Algeria': {
        'colonizer': 'French',
        'colonial_lang': 'fr',
        'native_lang': 'ar',
        'colonial': True
    },
}


# ============================================================================
# Cultural Distance Calculation
# ============================================================================

def calculate_cultural_distance(
    llm_pc1: float,
    llm_pc2: float,
    ivs_pc1: float,
    ivs_pc2: float
) -> float:
    """
    Calculate Euclidean distance between LLM and IVS PCA coordinates.
    
    Args:
        llm_pc1: LLM's first principal component
        llm_pc2: LLM's second principal component
        ivs_pc1: IVS ground truth first principal component
        ivs_pc2: IVS ground truth second principal component
    
    Returns:
        Euclidean distance between the two points
    
    Examples:
        >>> calculate_cultural_distance(0.0, 0.0, 1.0, 1.0)
        1.4142135623730951
        >>> calculate_cultural_distance(1.0, 1.0, 1.0, 1.0)
        0.0
    """
    return np.sqrt((llm_pc1 - ivs_pc1)**2 + (llm_pc2 - ivs_pc2)**2)


def add_cultural_distance_column(
    df: pd.DataFrame,
    ivs_dict: Dict[str, Tuple[float, float]]
) -> pd.DataFrame:
    """
    Add cultural distance column to dataframe.
    
    Args:
        df: DataFrame with columns 'country', 'PC1', 'PC2'
        ivs_dict: Dictionary mapping country names to (PC1, PC2) tuples
    
    Returns:
        DataFrame with added 'cultural_distance' column
    """
    def calc_distance(row):
        if row['country'] in ivs_dict:
            ivs_pc1, ivs_pc2 = ivs_dict[row['country']]
            return calculate_cultural_distance(
                row['PC1'], row['PC2'],
                ivs_pc1, ivs_pc2
            )
        return np.nan
    
    df = df.copy()
    df['cultural_distance'] = df.apply(calc_distance, axis=1)
    return df


# ============================================================================
# English Advantage Calculation
# ============================================================================

def calculate_english_advantage(
    df: pd.DataFrame,
    country: str,
    native_lang: str,
    english_lang: str = 'en'
) -> Dict[str, float]:
    """
    Calculate English advantage for a country.
    
    English advantage is defined as the percentage improvement in cultural
    distance when using English versus native language:
    
        English Advantage (%) = 100 × (Distance_native - Distance_english) / Distance_native
    
    Positive values indicate English produces better cultural alignment.
    
    Args:
        df: DataFrame with columns 'country', 'language', 'cultural_distance', 'model_name'
        country: Country name
        native_lang: Native language code (e.g., 'zh-cn', 'es', 'ja')
        english_lang: English language code (default: 'en', can be 'en-native')
    
    Returns:
        Dictionary with:
            - english_advantage: Percentage improvement (positive = English better)
            - english_distance: Mean cultural distance in English
            - native_distance: Mean cultural distance in native language
            - n_models: Number of models used in calculation
            - english_distances: List of individual English distances
            - native_distances: List of individual native distances
    
    Raises:
        ValueError: If country has no data or insufficient language data
    
    Examples:
        >>> df = pd.DataFrame({
        ...     'country': ['China', 'China', 'China', 'China'],
        ...     'language': ['en', 'en', 'zh-cn', 'zh-cn'],
        ...     'cultural_distance': [0.5, 0.6, 0.8, 0.9],
        ...     'model_name': ['model1', 'model2', 'model1', 'model2']
        ... })
        >>> result = calculate_english_advantage(df, 'China', 'zh-cn')
        >>> result['english_advantage'] > 0  # English is better
        True
    """
    # Filter data for this country
    country_data = df[df['country'] == country].copy()
    
    if len(country_data) == 0:
        raise ValueError(f"No data found for country: {country}")
    
    # Collect distances by model
    english_distances = []
    native_distances = []
    
    for model in country_data['model_name'].unique():
        model_data = country_data[country_data['model_name'] == model]
        
        # Get English distance (try both 'en' and 'en-native')
        en_data = model_data[model_data['language'].isin([english_lang, 'en', 'en-native'])]
        en_dist = en_data['cultural_distance'].dropna()
        
        # Get native language distance
        native_data = model_data[model_data['language'] == native_lang]
        native_dist = native_data['cultural_distance'].dropna()
        
        # Only include if both languages have data
        if len(en_dist) > 0 and len(native_dist) > 0:
            english_distances.append(en_dist.iloc[0])
            native_distances.append(native_dist.iloc[0])
    
    if len(english_distances) == 0:
        raise ValueError(
            f"Insufficient data for {country}: need both English and {native_lang} data"
        )
    
    english_distances = np.array(english_distances)
    native_distances = np.array(native_distances)
    
    # Calculate means
    english_mean = english_distances.mean()
    native_mean = native_distances.mean()
    
    # Calculate English advantage
    # Positive = English better (smaller distance)
    # Negative = Native better (smaller distance)
    if native_mean != 0:
        english_advantage = 100 * (native_mean - english_mean) / native_mean
    else:
        english_advantage = 0.0
    
    return {
        'english_advantage': english_advantage,
        'english_distance': english_mean,
        'native_distance': native_mean,
        'n_models': len(english_distances),
        'english_distances': english_distances.tolist(),
        'native_distances': native_distances.tolist()
    }


def calculate_portuguese_advantage(
    df: pd.DataFrame,
    country: str,
    native_lang: str,
    portuguese_lang: str = 'pt'
) -> Dict[str, float]:
    """
    Calculate Portuguese advantage for a country (analogous to English advantage).
    
    Portuguese advantage is defined as:
    
        Portuguese Advantage (%) = 100 × (Distance_native - Distance_portuguese) / Distance_native
    
    This is specifically for Macao analysis.
    
    Args:
        df: DataFrame with columns 'country', 'language', 'cultural_distance', 'model_name'
        country: Country name (typically 'Macao')
        native_lang: Native language code (e.g., 'zh-cn')
        portuguese_lang: Portuguese language code (default: 'pt')
    
    Returns:
        Dictionary with same structure as calculate_english_advantage
    """
    # Filter data for this country
    country_data = df[df['country'] == country].copy()
    
    if len(country_data) == 0:
        raise ValueError(f"No data found for country: {country}")
    
    # Collect distances by model
    portuguese_distances = []
    native_distances = []
    
    for model in country_data['model_name'].unique():
        model_data = country_data[country_data['model_name'] == model]
        
        # Get Portuguese distance
        pt_data = model_data[model_data['language'] == portuguese_lang]
        pt_dist = pt_data['cultural_distance'].dropna()
        
        # Get native language distance
        native_data = model_data[model_data['language'] == native_lang]
        native_dist = native_data['cultural_distance'].dropna()
        
        # Only include if both languages have data
        if len(pt_dist) > 0 and len(native_dist) > 0:
            portuguese_distances.append(pt_dist.iloc[0])
            native_distances.append(native_dist.iloc[0])
    
    if len(portuguese_distances) == 0:
        raise ValueError(
            f"Insufficient data for {country}: need both Portuguese and {native_lang} data"
        )
    
    portuguese_distances = np.array(portuguese_distances)
    native_distances = np.array(native_distances)
    
    # Calculate means
    portuguese_mean = portuguese_distances.mean()
    native_mean = native_distances.mean()
    
    # Calculate Portuguese advantage
    if native_mean != 0:
        portuguese_advantage = 100 * (native_mean - portuguese_mean) / native_mean
    else:
        portuguese_advantage = 0.0
    
    return {
        'portuguese_advantage': portuguese_advantage,
        'portuguese_distance': portuguese_mean,
        'native_distance': native_mean,
        'n_models': len(portuguese_distances),
        'portuguese_distances': portuguese_distances.tolist(),
        'native_distances': native_distances.tolist()
    }


# ============================================================================
# Data Loading Helpers
# ============================================================================

def load_ivs_coordinates(filepath: str) -> Dict[str, Tuple[float, float]]:
    """
    Load IVS ground truth coordinates from CSV file.
    
    Args:
        filepath: Path to IVS PCA coordinates CSV file
    
    Returns:
        Dictionary mapping country names to (PC1, PC2) tuples
    
    Examples:
        >>> ivs_dict = load_ivs_coordinates('SI/pca/Table_S5_IVS_PCA_coordinates.csv')
        >>> 'China' in ivs_dict
        True
        >>> len(ivs_dict['China'])
        2
    """
    ivs_df = pd.read_csv(filepath)
    return dict(zip(ivs_df['country'], zip(ivs_df['PC1'], ivs_df['PC2'])))


def filter_low_quality_models(
    df: pd.DataFrame,
    exclude_models: List[str]
) -> pd.DataFrame:
    """
    Filter out low-quality models from the dataset.
    
    Args:
        df: DataFrame with 'model_name' column
        exclude_models: List of model names to exclude
    
    Returns:
        Filtered DataFrame
    
    Examples:
        >>> df = pd.DataFrame({'model_name': ['good', 'bad', 'good']})
        >>> filtered = filter_low_quality_models(df, ['bad'])
        >>> len(filtered)
        2
    """
    return df[~df['model_name'].isin(exclude_models)].copy()



# ============================================================================
# Load Pre-computed Data
# ============================================================================

def load_precomputed_advantage_data(
    filepath: str = 'results/analysis/stage0_vs_stage3/english_advantage_average.csv'
) -> pd.DataFrame:
    """
    Load pre-computed English advantage data.
    
    This function loads the English advantage data that was pre-computed
    by the orientalism analysis pipeline. This avoids re-computing distances
    and advantages from scratch.
    
    Args:
        filepath: Path to the pre-computed advantage CSV file
    
    Returns:
        DataFrame with columns:
            - country: Country name
            - native_language: Native language code
            - english_advantage: Percentage advantage of English
            - (other columns as available)
    
    Examples:
        >>> df = load_precomputed_advantage_data()
        >>> hk = df[df['country'] == 'Hong Kong']
        >>> print(hk['english_advantage'].mean())
    """
    import os
    
    # Try CSV first, then Excel
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
    else:
        excel_path = filepath.replace('.csv', '.xlsx')
        if os.path.exists(excel_path):
            df = pd.read_excel(excel_path)
        else:
            raise FileNotFoundError(f"Could not find advantage data at {filepath} or {excel_path}")
    
    return df


def get_country_advantage(
    advantage_df: pd.DataFrame,
    country: str,
    native_lang: str = None
) -> float:
    """
    Get English advantage for a specific country and language.
    
    Args:
        advantage_df: DataFrame from load_precomputed_advantage_data()
        country: Country name
        native_lang: Native language code (optional, if None returns first match)
    
    Returns:
        English advantage percentage
    
    Raises:
        ValueError: If country not found
    """
    country_data = advantage_df[advantage_df['country'].str.contains(country, case=False, na=False)]
    
    if len(country_data) == 0:
        raise ValueError(f"Country not found: {country}")
    
    if native_lang is not None:
        country_data = country_data[country_data['native_language'] == native_lang]
        if len(country_data) == 0:
            raise ValueError(f"Language {native_lang} not found for {country}")
    
    return country_data['english_advantage'].iloc[0]
