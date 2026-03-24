#!/usr/bin/env python3
"""
Filter the full UKSI gap analysis to a single insect family.

Input:  filtered_gap_analysis.csv  — full UK Species Inventory with BOLD gap
        analysis (all families). Key columns:
            taxon_name    — valid species name
            synonyms      — alternative names
            other_names   — invalid/extra names
            bin_uris      — BOLD BINs matched to this species
            species_status — molecular data availability:
                             BLACK = no molecular data (needs polytomy node)
                             other values = molecular data present
            order_name    — taxonomic order
            family_name   — taxonomic family (used to filter)

Output: <family>_gap_analysis.csv — family-filtered subset, used for:
            - UKSI species membership checks (integrate_country_metadata.py)
            - Identifying polytomy candidates (BLACK status species)

Usage:
    python filter_uksi_by_family.py <filtered_gap_analysis.csv> <family_name> <output.csv>

Example:
    python scripts/filter_uksi_by_family.py filtered_gap_analysis.csv Sciaridae sciaridae_gap_analysis.csv
"""

import sys
import pandas as pd

if len(sys.argv) != 4:
    print(f"Usage: {sys.argv[0]} <filtered_gap_analysis.csv> <family_name> <output.csv>")
    sys.exit(1)

input_file = sys.argv[1]
family_name = sys.argv[2]
output_file = sys.argv[3]

print(f"Loading: {input_file}")
df = pd.read_csv(input_file, low_memory=False)
print(f"  Total species: {len(df):,}")

# Filter to the requested family
family_df = df[df['family_name'].str.lower() == family_name.lower()].copy()
print(f"  {family_name} species: {len(family_df):,}")

if len(family_df) == 0:
    available = sorted(df['family_name'].dropna().unique())
    print(f"\nERROR: Family '{family_name}' not found.")
    print(f"Available families (sample): {available[:20]}")
    sys.exit(1)

# Report species_status breakdown
print(f"\nSpecies status breakdown:")
for status, count in family_df['species_status'].value_counts().items():
    print(f"  {status}: {count:,}")

# Identify polytomy candidates (BLACK = no molecular data)
black = family_df[family_df['species_status'] == 'BLACK']
print(f"\nPolytomy candidates (BLACK status, no molecular data): {len(black):,}")
if len(black) > 0:
    print("  These species will need polytomy nodes in the tree.")
    for _, row in black.head(5).iterrows():
        print(f"    {row['taxon_name']}")
    if len(black) > 5:
        print(f"    ... and {len(black) - 5} more")

# Save
family_df.to_csv(output_file, index=False)
print(f"\n✓ Saved {len(family_df):,} species to: {output_file}")
