#!/usr/bin/env python3
"""
Restore missing metadata for BIOSCAN specimens by extracting BIN from tip names
and matching against specimens with complete metadata
"""

import sys
import pandas as pd
import re

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <input_metadata.tsv> <output_metadata.tsv>")
    sys.exit(1)

print("=" * 80)
print("RESTORING MISSING BIOSCAN METADATA")
print("=" * 80)

# Load current metadata
print("\n1. Loading current metadata...")
df = pd.read_csv(sys.argv[1], sep='\t')
print(f"   Total rows: {len(df):,}")

# Find BIOSCAN specimens with missing metadata
missing_mask = (df['dataset'] == 'BIOSCAN') & (df['bin'].isna() | (df['bin'] == ''))
print(f"   BIOSCAN specimens with missing BIN: {missing_mask.sum():,}")

# Extract BIN from tip names for specimens with missing BIN
def extract_bin_from_name(name):
    """Extract BIN from tip name format: Species|BIN|ProcessID
    BIN appears as BOLDACQ8733 in tip name but needs to be BOLD:ACQ8733 for matching
    """
    if pd.isna(name):
        return None
    parts = name.split('|')
    if len(parts) >= 2:
        # Second part should be the BIN (without BOLD: prefix in tip names)
        bin_candidate = parts[1]
        if bin_candidate.startswith('BOLD'):
            # Convert BOLDACQ8733 to BOLD:ACQ8733
            return 'BOLD:' + bin_candidate[4:]
    return None

print("\n2. Extracting BINs from tip names...")
df.loc[missing_mask, 'bin_extracted'] = df.loc[missing_mask, 'name'].apply(extract_bin_from_name)
successful_extractions = df.loc[missing_mask, 'bin_extracted'].notna().sum()
print(f"   Successfully extracted BIN from {successful_extractions:,} specimens")

# For each specimen with missing metadata, find a reference specimen with the same BIN
print("\n3. Matching specimens to reference data by BIN...")

# Create a lookup of complete metadata by BIN
complete_mask = (df['bin'].notna()) & (df['bin'] != '') & (df['bin'].str.startswith('BOLD:'))
bin_reference = df[complete_mask].groupby('bin').first()
print(f"   Created reference lookup with {len(bin_reference):,} unique BINs")

# Fields to restore
fields_to_restore = [
    'category', 'placement_type', 'placement_quality', 'placement_interpretation',
    'epa_lwr_score', 'bags_grade', 'bin_quality_issue', 'n_bins_for_species', 
    'all_bins', 'in_uksi', 'bioscan_specimens', 'needs_attention'
]

# Also restore species name from reference if current one is "Unknown_species"
restored_count = 0
partial_restore_count = 0

for idx in df[missing_mask].index:
    bin_extracted = df.at[idx, 'bin_extracted']
    
    if pd.notna(bin_extracted) and bin_extracted in bin_reference.index:
        # First, restore the BIN itself
        df.at[idx, 'bin'] = bin_extracted
        
        # Get reference metadata for this BIN
        ref = bin_reference.loc[bin_extracted]
        
        # Restore all fields
        for field in fields_to_restore:
            if field in ref.index and field in df.columns:
                df.at[idx, field] = ref[field]
        
        # If species is "Unknown_species" or "Unknown species", use reference species
        current_species = df.at[idx, 'species']
        if pd.isna(current_species) or current_species in ['Unknown_species', 'Unknown species', 'Unidentified']:
            if pd.notna(ref.get('species')):
                df.at[idx, 'species'] = ref['species']
        
        restored_count += 1
    elif pd.notna(bin_extracted):
        # BIN extracted but no reference found - still fill in what we can
        df.at[idx, 'bin'] = bin_extracted
        # Mark as novel placement since we don't have reference data
        df.at[idx, 'placement_type'] = 'novel'
        df.at[idx, 'category'] = 'BIOSCAN_collected'
        partial_restore_count += 1

print(f"   Fully restored metadata: {restored_count:,} specimens")
print(f"   Partially restored metadata: {partial_restore_count:,} specimens")

# Clean up temporary column
df.drop(columns=['bin_extracted'], inplace=True)

# Verify restoration
print("\n4. Verification...")
final_missing = (df['dataset'] == 'BIOSCAN') & (df['bin'].isna() | (df['bin'] == ''))
print(f"   BIOSCAN specimens still missing BIN: {final_missing.sum():,}")

bioscan_complete = (df['dataset'] == 'BIOSCAN') & (df['bin'].notna()) & (df['bin'] != '')
print(f"   BIOSCAN specimens with complete BIN: {bioscan_complete.sum():,}")

# Save restored metadata
output_file = sys.argv[2]
df.to_csv(output_file, sep='\t', index=False)

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"\nTotal specimens: {len(df):,}")
print(f"BIOSCAN specimens with restored metadata: {restored_count + partial_restore_count:,}")
print(f"  - Fully restored: {restored_count:,}")
print(f"  - Partially restored: {partial_restore_count:,}")
print(f"\nOutput saved to: {output_file}")

# Show example of restored data
if restored_count > 0:
    print("\n" + "=" * 80)
    print("SAMPLE RESTORED SPECIMENS")
    print("=" * 80)
    restored_examples = df[(df['dataset'] == 'BIOSCAN') & (df['bin'].notna()) & (df['bin'] != '')].head(3)
    for _, row in restored_examples.iterrows():
        print(f"\n{row['name']}")
        print(f"  BIN: {row['bin']}")
        print(f"  Species: {row['species']}")
        print(f"  Category: {row['category']}")
        print(f"  Placement: {row['placement_type']} ({row['placement_quality']})")

print("\n" + "=" * 80 + "\n")
