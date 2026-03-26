#!/usr/bin/env python3
"""
Filter bioscan_all.tsv to a single family and write a CSV to the family input folder.

Reads a combined BIOSCAN TSV covering all families, filters rows where the
'family' column matches the requested family name (case-insensitive),
and writes the result as CSV to:

    families/{Family}/input/bioscan_{family_lower}.csv

Also writes a BIN count file from the FULL unfiltered dataset:

    families/{Family}/input/bioscan_bin_counts.csv

This is used by add_external_links.py to count BIOSCAN specimens per BIN
across all families (not just the target family).

NOTE: Uses line-by-line parsing rather than pandas read_csv to avoid silent
row loss. The TSV has free-text fields (notes, collection_notes, verbatim_*)
that may contain embedded tab characters. pandas on_bad_lines='skip' would
silently discard the entire row when it sees an unexpected tab; since the
columns we need (processid, sampleid, bin_uri, family, species, nuc) are at
early indices (0–66) those rows would be incorrectly dropped.

Usage:
  python scripts/filter_bioscan.py bioscan_all.tsv --family Sciaridae

  Output path is auto-derived. Override with --output if needed.
"""

import argparse
import os
import sys
import pandas as pd

# Only these columns are used by downstream scripts.
# Extracting only these avoids carrying 80 unused columns.
KEEP_COLS = ['processid', 'sampleid', 'bin_uri', 'family', 'species', 'nuc']

parser = argparse.ArgumentParser(
    description="Filter bioscan_all.tsv to a single family"
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
counts_path  = os.path.join(os.path.dirname(output_path), 'bioscan_bin_counts.csv')

print("=" * 60)
print("FILTERING BIOSCAN TSV BY FAMILY")
print("=" * 60)
print(f"\n  Input:  {args.input}")
print(f"  Family: {args.family}")
print(f"  Output: {output_path}")
print(f"  Counts: {counts_path}")

# ---------------------------------------------------------------------------
# Line-by-line parsing
#
# The bioscan_all.tsv has free-text fields (e.g. notes at column 34,
# collection_notes at 45, several verbatim_* fields at 80-85) that may
# contain embedded tab characters. pandas C parser treats these as extra
# fields and on_bad_lines='skip' silently drops the entire row.
#
# The columns we need are all at early, safe indices:
#   processid=0, sampleid=1, bin_uri=7, family=17, species=21, nuc=66
#
# Reading line-by-line lets us extract those early columns correctly even
# when a later column has an embedded tab.
# ---------------------------------------------------------------------------
print(f"\n1. Parsing {args.input} line by line...")

all_bin_counts = {}   # bin_uri -> total count across all families
family_rows    = []   # rows matching the target family
total = bad = 0

try:
    fh = open(args.input, 'r', encoding='utf-8', errors='replace')
except FileNotFoundError:
    print(f"\nERROR: File not found: {args.input}")
    sys.exit(1)

with fh:
    header_line = fh.readline()
    if not header_line:
        print("ERROR: File is empty.")
        sys.exit(1)

    header = header_line.rstrip('\n').split('\t')
    col_idx = {col: i for i, col in enumerate(header)}
    n_cols  = len(header)

    # Verify required columns exist
    missing = [c for c in KEEP_COLS if c not in col_idx]
    if missing:
        print(f"\nERROR: Required columns not found in header: {missing}")
        print(f"  Available columns: {header[:30]} ...")
        sys.exit(1)

    fam_idx = col_idx['family']
    bin_idx = col_idx['bin_uri']

    for line in fh:
        total += 1
        parts = line.rstrip('\n').split('\t')

        # Count this row's BIN towards the all-family totals.
        # bin_uri is at index 7 — always safe even if later fields have tabs.
        if len(parts) > bin_idx:
            b = parts[bin_idx].strip()
            if b:
                all_bin_counts[b] = all_bin_counts.get(b, 0) + 1

        # family is at index 17 — also safe.
        if len(parts) <= fam_idx:
            bad += 1
            continue

        if parts[fam_idx].strip().lower() != family_lower:
            continue

        # Extract only the columns we need; use '' if index out of range
        # (can happen for nuc at index 66 if there are embedded tabs before it).
        row = {}
        for col in KEEP_COLS:
            idx = col_idx[col]
            row[col] = parts[idx].strip() if idx < len(parts) else ''
        family_rows.append(row)

    if total % 10000 != 0:  # print final count
        pass  # reported below

print(f"   {total:,} data lines read")
if bad:
    print(f"   {bad:,} lines skipped (fewer than {fam_idx + 1} fields — truncated rows)")
print(f"   {len(family_rows):,} rows matched family '{args.family}'")

if not family_rows:
    # Show available families from what we parsed
    print(f"\nWARNING: No rows matched family '{args.family}'.")
    print("  Check the family name. Common values appear in the 'family' column.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Build DataFrames
# ---------------------------------------------------------------------------
result = pd.DataFrame(family_rows, columns=KEEP_COLS)

bin_counts_df = pd.DataFrame(
    list(all_bin_counts.items()),
    columns=['bin_uri', 'bioscan_specimen_count']
).sort_values('bioscan_specimen_count', ascending=False)

# ---------------------------------------------------------------------------
# Save outputs
# ---------------------------------------------------------------------------
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# All-family BIN counts
bin_counts_df.to_csv(counts_path, index=False)
print(f"\n2. Saved all-family BIN counts: {counts_path}")
print(f"   {len(bin_counts_df):,} unique BINs across all families")

# Family-filtered CSV
result.to_csv(output_path, index=False)
print(f"\n3. Saved {len(result):,} rows to: {output_path}")
print(f"   Unique BINs:        {result['bin_uri'].nunique():,}")
print(f"   Unique process IDs: {result['processid'].nunique():,}")

print("\n" + "=" * 60 + "\n")
