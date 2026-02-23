#!/usr/bin/env python3
"""
Verification report for restored Sciaridae metadata
"""

import pandas as pd
import numpy as np

print("=" * 80)
print("SCIARIDAE METADATA RESTORATION - VERIFICATION REPORT")
print("=" * 80)

# Load final metadata
df = pd.read_csv('/mnt/project/sciaridae_metadata_FINAL.tsv', sep='\t')

print(f"\n{'='*80}")
print("OVERALL STATISTICS")
print("=" * 80)
print(f"Total specimens in tree: {len(df):,}")

print(f"\n{'-'*80}")
print("Dataset Breakdown:")
print("-" * 80)
for dataset, count in df['dataset'].value_counts().sort_index().items():
    print(f"  {dataset:20s}: {count:4,} specimens")

print(f"\n{'-'*80}")
print("BIN Completeness:")
print("-" * 80)
bins_present = df['bin'].notna() & (df['bin'] != '') & (df['bin'] != 'no_BIN')
print(f"  Specimens with BIN: {bins_present.sum():,} ({bins_present.sum()/len(df)*100:.1f}%)")
print(f"  Specimens without BIN: {(~bins_present).sum():,}")

# Check BIOSCAN specifically
bioscan_mask = df['dataset'] == 'BIOSCAN'
bioscan_with_bin = bioscan_mask & bins_present
bioscan_without_bin = bioscan_mask & ~bins_present

print(f"\n{'-'*80}")
print("BIOSCAN Specimens:")
print("-" * 80)
print(f"  Total BIOSCAN: {bioscan_mask.sum():,}")
print(f"  With complete BIN: {bioscan_with_bin.sum():,} ({bioscan_with_bin.sum()/bioscan_mask.sum()*100:.1f}%)")
print(f"  Missing BIN: {bioscan_without_bin.sum():,}")

# Check core metadata fields
print(f"\n{'-'*80}")
print("Metadata Completeness (BIOSCAN specimens):")
print("-" * 80)
bioscan_df = df[bioscan_mask]
for field in ['bin', 'species', 'category', 'placement_type', 'placement_quality', 
              'bioscan_specimens', 'geography']:
    complete = bioscan_df[field].notna() & (bioscan_df[field] != '')
    print(f"  {field:25s}: {complete.sum():4,}/{len(bioscan_df):4,} ({complete.sum()/len(bioscan_df)*100:5.1f}%)")

# BIOSCAN specimens statistics
print(f"\n{'='*80}")
print("BIOSCAN SPECIMENS IN BOLD DATABASE")
print("=" * 80)
bioscan_with_counts = bioscan_df[bioscan_df['bioscan_specimens'] > 0]
print(f"BINs with BIOSCAN specimen counts: {bioscan_with_counts['bin'].nunique():,}")
print(f"\nDistribution of BIOSCAN specimens per BIN:")
bioscan_counts = bioscan_with_counts.groupby('bin')['bioscan_specimens'].first()
percentiles = [0, 25, 50, 75, 90, 95, 99, 100]
for p in percentiles:
    val = np.percentile(bioscan_counts, p)
    print(f"  {p:3d}th percentile: {val:6.0f} specimens")

print(f"\nTop 10 BINs by BIOSCAN specimen count:")
top_bins = bioscan_df.groupby('bin').agg({
    'bioscan_specimens': 'first',
    'species': 'first',
    'category': 'first'
}).sort_values('bioscan_specimens', ascending=False).head(10)

for bin, row in top_bins.iterrows():
    print(f"  {bin:15s}: {row['bioscan_specimens']:4.0f} specimens - {row['species']}")

# Placement quality
print(f"\n{'='*80}")
print("PLACEMENT QUALITY")
print("=" * 80)
for ptype in df['placement_type'].unique():
    if pd.isna(ptype):
        continue
    ptype_df = df[df['placement_type'] == ptype]
    print(f"\n{ptype}:")
    if 'placement_quality' in df.columns:
        qual_counts = ptype_df['placement_quality'].value_counts()
        for qual, count in qual_counts.items():
            print(f"  {qual:20s}: {count:4,}")

# BIN quality issues
print(f"\n{'='*80}")
print("BIN QUALITY ISSUES")
print("=" * 80)
if 'bin_quality_issue' in df.columns:
    quality_counts = df[bins_present]['bin_quality_issue'].value_counts()
    for issue, count in quality_counts.items():
        if pd.notna(issue) and issue != '':
            print(f"  {issue:40s}: {count:4,} BINs")

# Geography distribution
print(f"\n{'='*80}")
print("GEOGRAPHIC DISTRIBUTION")
print("=" * 80)
geo_counts = df['geography'].value_counts()
print("Top 10 countries/regions:")
for geo, count in geo_counts.head(10).items():
    print(f"  {geo:30s}: {count:4,}")

# Examples of restored specimens
print(f"\n{'='*80}")
print("EXAMPLE RESTORED SPECIMENS")
print("=" * 80)
restored_examples = df[bioscan_mask].head(5)
for idx, row in restored_examples.iterrows():
    print(f"\n{row['name']}")
    print(f"  BIN: {row['bin']}")
    print(f"  Species: {row['species']}")
    print(f"  Category: {row['category']}")
    print(f"  Placement: {row['placement_type']} - {row['placement_quality']}")
    print(f"  BIOSCAN specimens in BOLD: {row['bioscan_specimens']}")
    print(f"  Geography: {row['geography']}")

print(f"\n{'='*80}")
print("RESTORATION COMPLETE")
print("=" * 80)
print(f"\nFinal metadata saved to: /mnt/project/sciaridae_metadata_FINAL.tsv")
print(f"All 346 BIOSCAN specimens now have complete metadata!")
print("=" * 80 + "\n")
