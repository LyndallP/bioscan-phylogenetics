#!/usr/bin/env python3
"""
Integrate BOLD country data into Sciaridae metadata.
Adds geography and in_uksi columns to existing metadata.
"""

import pandas as pd
import re

print("=" * 60)
print("INTEGRATING COUNTRY DATA INTO SCIARIDAE METADATA")
print("=" * 60)

# 1. Load existing metadata
print("\n1. Loading existing metadata...")
metadata = pd.read_csv('data/output/sciaridae_metadata_enhanced.tsv', sep='\t')
print(f"   Loaded {len(metadata):,} rows")

# 2. Load BOLD country data
print("\n2. Loading BOLD country data...")
bold_countries = pd.read_csv('data/reference_tree_bold_countries.tsv', sep='\t')
print(f"   Loaded {len(bold_countries):,} specimens with country data")

# 3. Load UKSI Sciaridae list
print("\n3. Loading UKSI species list...")
uksi = pd.read_csv('uksi_sciaridae_full.tsv', sep='\t', low_memory=False)
uksi_species = set(uksi['species'].dropna().unique())
print(f"   UKSI contains {len(uksi_species):,} unique Sciaridae species")

# 4. Extract processid from tip names
print("\n4. Extracting process IDs from tip names...")
def extract_processid(tip_name):
    """Extract processid from tip format: Species|BIN|ProcessID"""
    parts = tip_name.split('|')
    if len(parts) >= 3:
        return parts[2]
    return None

metadata['processid_extracted'] = metadata['name'].apply(extract_processid)

# 5. Merge country data
print("\n5. Merging country data...")
metadata = metadata.merge(
    bold_countries[['processid', 'country_ocean', 'province_state']],
    left_on='processid_extracted',
    right_on='processid',
    how='left'
)

# 6. Add geography column
print("\n6. Creating geography column...")
def assign_geography(row):
    """Assign geography based on placement type and country data"""
    # For reference tree specimens, use BOLD country data
    if row['placement_type'] == 'reference_tree':
        if pd.notna(row['country_ocean']):
            return row['country_ocean']
        else:
            return 'Unknown'
    
    # For validation/novel placements (BIOSCAN specimens), mark as UK
    elif row['placement_type'] in ['validation', 'novel']:
        return 'United Kingdom'  # BIOSCAN UK specimens
    
    # For polytomy (no molecular data)
    elif row['placement_type'] == 'polytomy':
        return 'Unknown'
    
    return 'Unknown'

metadata['geography'] = metadata.apply(assign_geography, axis=1)

# 7. Add in_uksi column
print("\n7. Creating in_uksi column...")
metadata['in_uksi'] = metadata['species'].isin(uksi_species)

# 8. Reorganize columns for final metadata
print("\n8. Organizing final columns...")
final_columns = [
    'name',
    'bin',
    'species',
    'processid',
    'category',
    'geography',
    'in_uksi',
    'placement_type',
    'placement_quality',
    'placement_interpretation',
    'epa_lwr_score',
    'bags_grade',
    'bin_quality_issue',
    'n_bins_for_species',
    'all_bins',
    'bioscan_specimens',
    'needs_attention'
]

# Keep only columns that exist
final_columns = [col for col in final_columns if col in metadata.columns]
metadata_final = metadata[final_columns]

# 9. Save final metadata
output_file = 'data/output/sciaridae_taxonium_metadata_COMPLETE.tsv'
metadata_final.to_csv(output_file, sep='\t', index=False)

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

print(f"\nTotal rows: {len(metadata_final):,}")
print(f"\nGeography breakdown:")
geo_counts = metadata_final['geography'].value_counts()
for geo, count in geo_counts.head(10).items():
    print(f"  {geo}: {count:,}")

print(f"\nUKSI membership:")
uksi_counts = metadata_final['in_uksi'].value_counts()
for status, count in uksi_counts.items():
    print(f"  {'In UKSI' if status else 'Not in UKSI'}: {count:,}")

print(f"\nPlacement types:")
placement_counts = metadata_final['placement_type'].value_counts()
for ptype, count in placement_counts.items():
    print(f"  {ptype}: {count:,}")

print(f"\n✓ Final metadata saved to: {output_file}")
print(f"\n{'=' * 60}\n")
