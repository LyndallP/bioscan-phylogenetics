#!/usr/bin/env python3
"""
Add BAGS-derived metadata columns from the family gap analysis CSV.

Populates:
  - bags_grade          : A/B/C/D/E quality grade from BAGS
  - bin_quality_issue   : description derived from bags_grade
  - n_bins_for_species  : number of BINs for this species in the gap analysis
  - all_bins            : semicolon-separated list of BINs for this species
  - needs_attention     : True if category==Not_in_UKSI or placement_quality==Low
  - synonym             : True if the match was via a synonym rather than the
                          primary taxon_name or BIN

Matching priority (per metadata row):
  1. BIN  — metadata 'bin' found in gap analysis 'bin_uris' (any of the
             semicolon-separated values)
  2. Name — metadata 'species' matches gap analysis 'taxon_name' exactly
  3. Synonym — metadata 'species' found in gap analysis 'synonyms' field
               (semicolon-separated; any entry)

Usage:
  python scripts/add_bags_metadata.py \\
      families/{Family}/output/metadata_03_country.tsv \\
      families/{Family}/input/{family}_gap_analysis.csv \\
      families/{Family}/output/metadata_03b_bags.tsv
"""

import sys
import pandas as pd

if len(sys.argv) != 4:
    print(f"Usage: {sys.argv[0]} <metadata.tsv> <gap_analysis.csv> <output.tsv>")
    sys.exit(1)

metadata_path, gap_path, output_path = sys.argv[1], sys.argv[2], sys.argv[3]

print("=" * 60)
print("ADDING BAGS METADATA FROM GAP ANALYSIS CSV")
print("=" * 60)

# ---------------------------------------------------------------------------
# Load inputs
# ---------------------------------------------------------------------------
print(f"\n1. Loading metadata: {metadata_path}")
metadata = pd.read_csv(metadata_path, sep='\t')
print(f"   {len(metadata):,} rows")

print(f"\n2. Loading gap analysis: {gap_path}")
gap = pd.read_csv(gap_path, low_memory=False)
print(f"   {len(gap):,} species rows")

# ---------------------------------------------------------------------------
# Build lookup tables from gap analysis
# ---------------------------------------------------------------------------
print("\n3. Building lookup tables...")

# BIN → gap row index  (one BIN can map to exactly one species row)
bin_to_idx = {}
for idx, row in gap.iterrows():
    raw = str(row.get('bin_uris', '') or '')
    if not raw or raw == 'nan':
        continue
    for b in raw.split(';'):
        b = b.strip()
        if b:
            bin_to_idx[b] = idx

# taxon_name → gap row index
name_to_idx = {}
for idx, row in gap.iterrows():
    name = str(row.get('taxon_name', '') or '').strip()
    if name and name != 'nan':
        name_to_idx[name] = idx

# synonym → gap row index  (split each synonyms cell by ';')
synonym_to_idx = {}
for idx, row in gap.iterrows():
    raw = str(row.get('synonyms', '') or '')
    if not raw or raw == 'nan':
        continue
    for syn in raw.split(';'):
        syn = syn.strip()
        if syn:
            synonym_to_idx[syn] = idx

print(f"   {len(bin_to_idx):,} BIN entries")
print(f"   {len(name_to_idx):,} taxon_name entries")
print(f"   {len(synonym_to_idx):,} synonym entries")

# ---------------------------------------------------------------------------
# Helper: derive bin_quality_issue from bags_grade + n_bins
# ---------------------------------------------------------------------------
def derive_bin_quality_issue(bags_grade, n_bins):
    g = str(bags_grade).strip().upper()
    if g == 'C':
        return f"split_across_{n_bins}_BINs"
    elif g == 'E':
        return "shares_BIN_with_other_species"
    elif g in ('A', 'B', 'D'):
        return "clean"
    return "unknown"

# ---------------------------------------------------------------------------
# Match each metadata row and populate fields
# ---------------------------------------------------------------------------
print("\n4. Matching metadata rows to gap analysis...")

bags_grades       = []
bin_quality_issues = []
n_bins_list       = []
all_bins_list     = []
synonym_flags     = []

matched_by_bin  = 0
matched_by_name = 0
matched_by_syn  = 0
unmatched       = 0

for _, row in metadata.iterrows():
    bin_val     = str(row.get('bin', '') or '').strip()
    species_val = str(row.get('species', '') or '').strip()

    gap_idx  = None
    is_syn   = False

    # Priority 1: BIN match
    if bin_val and bin_val not in ('no_BIN', 'nan', ''):
        gap_idx = bin_to_idx.get(bin_val)
        if gap_idx is not None:
            matched_by_bin += 1

    # Priority 2: exact taxon_name match
    if gap_idx is None and species_val and species_val not in ('nan', ''):
        gap_idx = name_to_idx.get(species_val)
        if gap_idx is not None:
            matched_by_name += 1

    # Priority 3: synonym match
    if gap_idx is None and species_val and species_val not in ('nan', ''):
        gap_idx = synonym_to_idx.get(species_val)
        if gap_idx is not None:
            matched_by_syn += 1
            is_syn = True

    if gap_idx is None:
        unmatched += 1
        bags_grades.append('')
        bin_quality_issues.append('')
        n_bins_list.append('')
        all_bins_list.append('')
        synonym_flags.append(False)
        continue

    gap_row   = gap.loc[gap_idx]
    grade     = str(gap_row.get('bags_grade', '') or '').strip()
    raw_bins  = str(gap_row.get('bin_uris', '') or '').strip()

    if raw_bins == 'nan':
        raw_bins = ''

    bins      = [b.strip() for b in raw_bins.split(';') if b.strip()] if raw_bins else []
    n         = len(bins)

    bags_grades.append(grade)
    bin_quality_issues.append(derive_bin_quality_issue(grade, n))
    n_bins_list.append(n if n > 0 else '')
    all_bins_list.append('; '.join(bins) if bins else '')
    synonym_flags.append(is_syn)

print(f"   Matched by BIN:      {matched_by_bin:,}")
print(f"   Matched by name:     {matched_by_name:,}")
print(f"   Matched by synonym:  {matched_by_syn:,}")
print(f"   Unmatched:           {unmatched:,}")

# ---------------------------------------------------------------------------
# Write columns into metadata (overwrite the empty placeholders)
# ---------------------------------------------------------------------------
metadata['bags_grade']       = bags_grades
metadata['bin_quality_issue'] = bin_quality_issues
metadata['n_bins_for_species'] = n_bins_list
metadata['all_bins']         = all_bins_list
metadata['synonym']          = synonym_flags

# needs_attention: flag rows that warrant manual review
metadata['needs_attention'] = (
    (metadata['category'] == 'Not_in_UKSI') |
    (metadata['placement_quality'] == 'Low')
)

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
metadata.to_csv(output_path, sep='\t', index=False)

print(f"\n5. Summary of populated fields:")
print(f"   bags_grade non-empty:        {(metadata['bags_grade'] != '').sum():,}")
print(f"   bin_quality_issue non-empty: {(metadata['bin_quality_issue'] != '').sum():,}")
print(f"   n_bins_for_species non-empty:{(metadata['n_bins_for_species'] != '').sum():,}")
print(f"   all_bins non-empty:          {(metadata['all_bins'] != '').sum():,}")
print(f"   synonym == True:             {metadata['synonym'].sum():,}")
print(f"   needs_attention == True:     {metadata['needs_attention'].sum():,}")
if (metadata['bags_grade'] != '').sum() > 0:
    print(f"\n   bags_grade distribution:")
    for g, c in metadata['bags_grade'].value_counts().items():
        print(f"     {g}: {c:,}")

print(f"\n✓ Saved {len(metadata):,} rows to: {output_path}")
print("=" * 60 + "\n")
