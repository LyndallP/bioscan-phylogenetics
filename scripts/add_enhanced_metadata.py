#!/usr/bin/env python3
"""Add geography, DTOL fields, and dataset column"""

import sys
import pandas as pd

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <input_metadata.tsv> <output_metadata.tsv>")
    sys.exit(1)

# Load basic metadata
df = pd.read_csv(sys.argv[1], sep='\t')

print(f"Loaded {len(df)} rows")

# Add dataset column
df['dataset'] = df['placement_type'].map({
    'validation': 'BIOSCAN',
    'novel': 'BIOSCAN',
    'dtol': 'DTOL',
    'reference_tree': 'Reference',
    'polytomy': ''
})

# Add DTOL-specific columns
df['tolid'] = ''
df['assembly_status'] = ''
df['genome_status'] = ''

# For DTOL specimens, extract tolid
dtol_rows = df['placement_type'] == 'dtol'
df.loc[dtol_rows, 'tolid'] = df.loc[dtol_rows, 'name'].str.split('|').str[1]
df.loc[dtol_rows, 'assembly_status'] = ''
df.loc[dtol_rows, 'genome_status'] = ''

# For now, set geography as empty (will be filled by BOLD API script)
# But set UK for DTOL and polytomy
df.loc[dtol_rows, 'geography'] = 'United Kingdom'
df.loc[df['placement_type'] == 'polytomy', 'geography'] = 'United Kingdom'

# Reorder columns to match expected 20-column format
columns = ['name', 'bin', 'species', 'category', 'geography', 'in_uksi',
           'placement_type', 'placement_quality', 'placement_interpretation', 'epa_lwr_score',
           'bags_grade', 'bin_quality_issue', 'n_bins_for_species', 'all_bins',
           'bioscan_specimens', 'needs_attention',
           'tolid', 'assembly_status', 'genome_status', 'dataset']

df = df[columns]

# Save
df.to_csv(sys.argv[2], sep='\t', index=False)

print(f"✓ Enhanced metadata: {len(df)} rows, {len(df.columns)} columns")
print(f"\nDataset breakdown:")
print(df['dataset'].value_counts())

print(f"\n✓ Saved: {sys.argv[2]}")
print(f"\nNext step: Run fetch_bold_countries.R to add geography from BOLD")
