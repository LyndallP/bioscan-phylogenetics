#!/usr/bin/env python3
"""
Filter bioscan_all.tsv to a single family and write a CSV to the family input folder.

Reads a combined BIOSCAN TSV covering all families, filters rows where the
'bold_family' column matches the requested family name (case-insensitive),
and writes the result as CSV to:

    families/{Family}/input/bioscan_{family_lower}.csv

This file is then used by:
  - scripts/06_select_bin_representatives.py  (Step 3)
  - scripts/add_external_links.py             (Step 14, auto-detected)

Usage:
  python scripts/filter_bioscan.py bioscan_all.tsv --family Sciaridae

  Output path is auto-derived. Override with --output if needed.
"""

import argparse
import os
import sys
import pandas as pd

parser = argparse.ArgumentParser(
    description="Filter bioscan_all.csv to a single family"
)
parser.add_argument("input", help="Path to bioscan_all.tsv")
parser.add_argument("--family", required=True, help="Family name (e.g. Sciaridae)")
parser.add_argument(
    "--output",
    help="Output CSV path. Defaults to families/{Family}/input/bioscan_{family_lower}.csv"
)
args = parser.parse_args()

family_lower = args.family.lower()
output_path  = args.output or f"families/{args.family}/input/bioscan_{family_lower}.csv"

print("=" * 60)
print("FILTERING BIOSCAN CSV BY FAMILY")
print("=" * 60)
print(f"\n  Input:  {args.input}")
print(f"  Family: {args.family}")
print(f"  Output: {output_path}")

# Load — some rows may have embedded tabs in free-text fields (e.g. notes);
# skip them rather than aborting.
print(f"\n1. Loading {args.input}...")
try:
    df = pd.read_csv(args.input, sep='\t', low_memory=False, on_bad_lines='skip')
except TypeError:
    # pandas < 1.3 uses the old parameter name
    df = pd.read_csv(args.input, sep='\t', low_memory=False, error_bad_lines=False)
print(f"   {len(df):,} total rows, {len(df.columns)} columns")

if 'family' not in df.columns:
    print(f"\nERROR: 'family' column not found. Available columns:")
    print(f"  {', '.join(df.columns.tolist())}")
    sys.exit(1)

# Filter
print(f"\n2. Filtering to family == '{args.family}' (case-insensitive)...")
mask   = df['family'].str.lower() == family_lower
result = df[mask].copy()
print(f"   {len(result):,} rows kept from {df['family'].nunique()} families")

if len(result) == 0:
    available = sorted(df['family'].dropna().unique().tolist())
    print(f"\nWARNING: No rows matched. Available families:")
    for f in available:
        print(f"   {f}")
    sys.exit(1)

# Ensure output directory exists
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# Save
result.to_csv(output_path, index=False)
print(f"\n3. Saved {len(result):,} rows to: {output_path}")

if 'bin_uri' in result.columns:
    print(f"   Unique BINs: {result['bin_uri'].nunique():,}")
if 'processid' in result.columns:
    print(f"   Unique process IDs: {result['processid'].nunique():,}")

print("\n" + "=" * 60 + "\n")
