#!/usr/bin/env python3
"""
Add BAGS-derived metadata columns from the family gap analysis CSV.

Populates:
  - bags_grade          : A/B/C/D/E quality grade from BAGS
  - bin_quality_issue   : description derived from bags_grade
  - n_bins_for_species  : number of BINs for this species in the gap analysis
  - all_bins            : semicolon-separated list of BINs for this species
  - UKSI_name_match     : how the species was matched:
                            ''           - matched by BIN (no name lookup needed)
                            'accepted'   - matched via taxon_name column
                            'synonym'    - matched via synonyms column
                            'other name' - matched via other_names column
  - taxon_version_key   : UKSI taxon_version_key from the matched gap analysis row

Matching priority (per metadata row):
  1. BIN       — metadata 'bin' found in gap analysis 'bin_uris'
                 (any semicolon-separated value)
  2. accepted  — metadata 'species' == gap analysis 'taxon_name'
  3. synonym   — metadata 'species' found in gap analysis 'synonyms'
                 (semicolon-separated)
  4. other name— metadata 'species' found in gap analysis 'other_names'
                 (semicolon-separated)

needs_attention is NOT set here — computed in finalize_metadata.py (Step 15)
once all columns including Bioscan specimen count are available.

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
# Build lookup tables
# ---------------------------------------------------------------------------
print("\n3. Building lookup tables...")

# Normalise bin values in the metadata to BOLD: format before matching
# (colon is stripped by 03_clean_alignment.py for Newick compatibility;
#  it is not restored until add_external_links.py, so we do it here too)
if 'bin' in metadata.columns:
    metadata['bin'] = (
        metadata['bin'].astype(str)
        .str.replace(r'\bBOLD(?!:)', 'BOLD:', regex=True)
        .replace('nan', '')
    )

def split_semicolon(val):
    """Split a semicolon-separated string, stripping whitespace."""
    raw = str(val or '').strip()
    if not raw or raw == 'nan':
        return []
    return [v.strip() for v in raw.split(';') if v.strip()]

# BIN → gap row index (bin_uris is semicolon-separated; each BIN maps to one row)
bin_to_idx = {}
for idx, row in gap.iterrows():
    for b in split_semicolon(row.get('bin_uris', '')):
        bin_to_idx[b] = idx

# taxon_name → gap row index
name_to_idx = {}
for idx, row in gap.iterrows():
    name = str(row.get('taxon_name', '') or '').strip()
    if name and name != 'nan':
        name_to_idx[name] = idx

# synonyms → gap row index
synonym_to_idx = {}
for idx, row in gap.iterrows():
    for syn in split_semicolon(row.get('synonyms', '')):
        synonym_to_idx[syn] = idx

# other_names → gap row index
other_name_to_idx = {}
for idx, row in gap.iterrows():
    for other in split_semicolon(row.get('other_names', '')):
        other_name_to_idx[other] = idx

print(f"   {len(bin_to_idx):,} BIN entries")
print(f"   {len(name_to_idx):,} taxon_name entries")
print(f"   {len(synonym_to_idx):,} synonym entries")
print(f"   {len(other_name_to_idx):,} other_name entries")

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
# Match each metadata row
# ---------------------------------------------------------------------------
print("\n4. Matching metadata rows to gap analysis...")

bags_grades         = []
bin_quality_issues  = []
n_bins_list         = []
all_bins_list       = []
uksi_name_matches   = []
taxon_version_keys  = []

matched_by_bin       = 0
matched_by_name      = 0
matched_by_synonym   = 0
matched_by_othername = 0
unmatched            = 0

for _, row in metadata.iterrows():
    bin_val     = str(row.get('bin', '') or '').strip()
    species_val = str(row.get('species', '') or '').strip()

    gap_idx    = None
    match_type = ''   # '', 'accepted', 'synonym', 'other name'

    # Priority 1: BIN match
    if bin_val and bin_val not in ('no_BIN', 'nan', ''):
        gap_idx = bin_to_idx.get(bin_val)
        if gap_idx is not None:
            matched_by_bin += 1
            match_type = ''

    # Priority 2: taxon_name match
    if gap_idx is None and species_val and species_val not in ('nan', ''):
        gap_idx = name_to_idx.get(species_val)
        if gap_idx is not None:
            matched_by_name += 1
            match_type = 'accepted'

    # Priority 3: synonym match
    if gap_idx is None and species_val and species_val not in ('nan', ''):
        gap_idx = synonym_to_idx.get(species_val)
        if gap_idx is not None:
            matched_by_synonym += 1
            match_type = 'synonym'

    # Priority 4: other_names match
    if gap_idx is None and species_val and species_val not in ('nan', ''):
        gap_idx = other_name_to_idx.get(species_val)
        if gap_idx is not None:
            matched_by_othername += 1
            match_type = 'other name'

    if gap_idx is None:
        unmatched += 1
        bags_grades.append('')
        bin_quality_issues.append('')
        n_bins_list.append('')
        all_bins_list.append('')
        uksi_name_matches.append('')
        taxon_version_keys.append('')
        continue

    gap_row = gap.loc[gap_idx]
    grade   = str(gap_row.get('bags_grade', '') or '').strip()
    tvk     = str(gap_row.get('taxon_version_key', '') or '').strip()
    if tvk == 'nan':
        tvk = ''

    raw_bins = str(gap_row.get('bin_uris', '') or '').strip()
    bins     = split_semicolon(raw_bins)
    n        = len(bins)

    bags_grades.append(grade)
    bin_quality_issues.append(derive_bin_quality_issue(grade, n))
    n_bins_list.append(n if n > 0 else '')
    all_bins_list.append('; '.join(bins) if bins else '')
    uksi_name_matches.append(match_type)
    taxon_version_keys.append(tvk)

print(f"   Matched by BIN:        {matched_by_bin:,}")
print(f"   Matched by taxon_name: {matched_by_name:,}")
print(f"   Matched by synonym:    {matched_by_synonym:,}")
print(f"   Matched by other_name: {matched_by_othername:,}")
print(f"   Unmatched:             {unmatched:,}")

# ---------------------------------------------------------------------------
# Write columns into metadata (overwrite the empty placeholders)
# ---------------------------------------------------------------------------
metadata['bags_grade']        = bags_grades
metadata['bin_quality_issue'] = bin_quality_issues
metadata['n_bins_for_species'] = n_bins_list
metadata['all_bins']          = all_bins_list
metadata['UKSI_name_match']   = uksi_name_matches
metadata['taxon_version_key'] = taxon_version_keys

# needs_attention is computed in finalize_metadata.py (Step 15)

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
metadata.to_csv(output_path, sep='\t', index=False)

print(f"\n5. Summary of populated fields:")
print(f"   bags_grade non-empty:        {(metadata['bags_grade'] != '').sum():,}")
print(f"   bin_quality_issue non-empty: {(metadata['bin_quality_issue'] != '').sum():,}")
print(f"   n_bins_for_species non-empty:{(metadata['n_bins_for_species'] != '').sum():,}")
print(f"   all_bins non-empty:          {(metadata['all_bins'] != '').sum():,}")
print(f"   taxon_version_key non-empty: {(metadata['taxon_version_key'] != '').sum():,}")
if (metadata['bags_grade'] != '').sum() > 0:
    print(f"\n   bags_grade distribution:")
    for g, c in metadata['bags_grade'].value_counts().items():
        print(f"     {g}: {c:,}")
print(f"\n   UKSI_name_match distribution:")
print(f"     BIN match:  {matched_by_bin:,}")
print(f"     accepted:   {matched_by_name:,}")
print(f"     synonym:    {matched_by_synonym:,}")
print(f"     other name: {matched_by_othername:,}")
print(f"     unmatched:  {unmatched:,}")

print(f"\n✓ Saved {len(metadata):,} rows to: {output_path}")
print("=" * 60 + "\n")
