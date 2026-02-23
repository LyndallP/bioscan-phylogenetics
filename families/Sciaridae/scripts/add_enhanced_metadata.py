#!/usr/bin/env python3
"""Add geography, DTOL fields, and dataset column"""

import pandas as pd

# Load basic metadata
df = pd.read_csv('data/output/sciaridae_basic_metadata.tsv', sep='\t')

print(f"Loaded {len(df)} rows")

# Add dataset column
df['dataset'] = df['placement_type'].map({
    'bioscan': 'BIOSCAN',
    'dtol': 'DTOL',
    'reference': 'Reference',
    'polytomy': ''
})

# Add DTOL-specific columns
df['tolid'] = ''
df['assembly_status'] = ''
df['genome_status'] = ''

# For DTOL specimens, extract tolid
dtol_rows = df['placement_type'] == 'dtol'
df.loc[dtol_rows, 'tolid'] = df.loc[dtol_rows, 'name'].str.split('|').str[1]
df.loc[dtol_rows, 'assembly_status'] = '62_lr_asm'
df.loc[dtol_rows, 'genome_status'] = '62_lr_asm'

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
df.to_csv('data/output/sciaridae_metadata_enhanced.tsv', sep='\t', index=False)

print(f"✓ Enhanced metadata: {len(df)} rows, {len(df.columns)} columns")
print(f"\nDataset breakdown:")
print(df['dataset'].value_counts())

print(f"\n✓ Saved: sciaridae_metadata_enhanced.tsv")
print(f"\nNext step: Run fetch_bold_countries.R to add geography from BOLD")
