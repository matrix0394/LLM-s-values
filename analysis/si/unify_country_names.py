"""
Unify country names across IVS and LLM PCA coordinate files.

This script standardizes country names so that:
1. IVS data country names match roleplay data country names
2. All figures can correctly find country coordinates for gold stars
"""

import pandas as pd
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
pca_dir = project_root / 'SI' / 'pca'

# Country name mapping: IVS name -> Standard name (matching roleplay data)
COUNTRY_NAME_MAP = {
    'Bolivia (Plurinational State of)': 'Bolivia',
    'Korea (the Republic of)': 'Korea, Republic of',
    'Russian Federation (the)': 'Russian Federation',
    'Palestine, State of': 'Palestine',
    'Taiwan (Province of China)': 'Taiwan, Province of China',
    'Philippines (the)': 'Philippines',
    'Netherlands (the)': 'Netherlands',
    'Iran (Islamic Republic of)': 'Iran',
    'Moldova (the Republic of)': 'Moldova',
    'United Kingdom of Great Britain and Northern Ireland (the)': 'United Kingdom',
    'United States of America (the)': 'United States of America',
    'Venezuela (Bolivarian Republic of)': 'Venezuela',
}

def unify_ivs_names():
    """Update IVS data to use standardized country names."""
    ivs_path = pca_dir / 'Table_S5_IVS_PCA_coordinates.csv'
    
    # Read IVS data
    ivs_df = pd.read_csv(ivs_path)
    print(f"Loaded IVS data: {len(ivs_df)} rows")
    
    # Apply name mapping
    changes = []
    for old_name, new_name in COUNTRY_NAME_MAP.items():
        mask = ivs_df['country'] == old_name
        if mask.any():
            ivs_df.loc[mask, 'country'] = new_name
            changes.append(f"  {old_name} -> {new_name}")
    
    if changes:
        print("Applied name changes:")
        for c in changes:
            print(c)
    else:
        print("No changes needed")
    
    # Save updated data
    ivs_df.to_csv(ivs_path, index=False)
    print(f"Saved updated IVS data to {ivs_path}")
    
    return ivs_df

def verify_matching():
    """Verify that country names now match between IVS and roleplay data."""
    ivs_df = pd.read_csv(pca_dir / 'Table_S5_IVS_PCA_coordinates.csv')
    rp_df = pd.read_csv(pca_dir / 'Table_S7_LLM_roleplay_PCA_coordinates.csv')
    
    ivs_countries = set(ivs_df['country'].unique())
    rp_countries = set(rp_df['country'].unique())
    
    # Countries in roleplay but not in IVS
    missing_in_ivs = rp_countries - ivs_countries
    
    print(f"\nVerification:")
    print(f"  IVS countries: {len(ivs_countries)}")
    print(f"  Roleplay countries: {len(rp_countries)}")
    print(f"  Matching: {len(rp_countries & ivs_countries)}")
    
    if missing_in_ivs:
        print(f"\n  ⚠️ Countries in roleplay but not in IVS ({len(missing_in_ivs)}):")
        for c in sorted(missing_in_ivs):
            print(f"    - {c}")
    else:
        print("\n  ✅ All roleplay countries have matching IVS data!")

def main():
    print("=" * 60)
    print("Unifying Country Names in PCA Data")
    print("=" * 60)
    print()
    
    unify_ivs_names()
    verify_matching()
    
    print()
    print("=" * 60)
    print("Done!")
    print("=" * 60)

if __name__ == '__main__':
    main()
