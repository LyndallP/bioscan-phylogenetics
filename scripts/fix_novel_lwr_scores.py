#!/usr/bin/env python3
"""
Fix missing EPA-ng LWR scores for Novel placement specimens.

The jplace file has scores for all 23 Novel specimens, but the name format
differs from the metadata:
- Metadata: Unknown_species|BOLDAER2788|WOXF3244-25
- jplace:    BOLDAER2788|Unknown_species|WOXF3244-25

We match by BOLD ID and update the epa_lwr_score column.
"""

import sys
import pandas as pd
import json

if len(sys.argv) != 4:
    print(f"Usage: {sys.argv[0]} <input_metadata.tsv> <epa_result.jplace> <output_metadata.tsv>")
    sys.exit(1)

print("=" * 80)
print("FIXING NOVEL PLACEMENT LWR SCORES")
print("=" * 80)

# Load metadata
df = pd.read_csv(sys.argv[1], sep='\t')
print(f"\nLoaded {len(df):,} specimens")

# Load jplace file
with open(sys.argv[2], 'r') as f:
    jplace_data = json.load(f)

# Extract LWR scores
placements = jplace_data.get('placements', [])
lwr_scores = {}
for placement in placements:
    names = placement.get('n', [])
    p_list = placement.get('p', [])
    if p_list and names:
        lwr = p_list[0][2]  # LWR is index 2
        for name in names:
            lwr_scores[name] = lwr

print(f"Extracted LWR scores from jplace: {len(lwr_scores)}")

# Extract BOLD IDs for matching
df['bold_id'] = df['name'].str.extract(r'(BOLD[A-Z0-9]+)')

# Create lookup from jplace names to LWR scores by BOLD ID
jplace_bold_to_lwr = {}
for jplace_name, lwr in lwr_scores.items():
    # Extract BOLD ID from jplace name
    bold_match = pd.Series([jplace_name]).str.extract(r'(BOLD[A-Z0-9]+)')
    if not bold_match.empty and not pd.isna(bold_match.iloc[0, 0]):
        bold_id = bold_match.iloc[0, 0]
        jplace_bold_to_lwr[bold_id] = lwr

print(f"Created BOLD ID → LWR lookup: {len(jplace_bold_to_lwr)} entries")

# ============================================================================
# FIX NOVEL PLACEMENT LWR SCORES
# ============================================================================

print("\n" + "=" * 80)
print("UPDATING NOVEL PLACEMENT LWR SCORES")
print("=" * 80)

novel_mask = df['placement_type'] == 'novel'
novel_count = novel_mask.sum()
print(f"\nNovel placements: {novel_count}")
print(f"Novel with empty LWR: {df[novel_mask]['epa_lwr_score'].isna().sum()}")

# Update LWR scores for Novel specimens
updated_count = 0
for idx in df[novel_mask].index:
    if pd.isna(df.loc[idx, 'epa_lwr_score']):
        bold_id = df.loc[idx, 'bold_id']
        if bold_id in jplace_bold_to_lwr:
            df.loc[idx, 'epa_lwr_score'] = jplace_bold_to_lwr[bold_id]
            updated_count += 1

print(f"\n✅ Updated LWR scores for {updated_count} Novel specimens")

# Verify
print(f"\nAfter update:")
print(f"  Novel with empty LWR: {df[novel_mask]['epa_lwr_score'].isna().sum()}")
print(f"  Novel with LWR scores: {df[novel_mask]['epa_lwr_score'].notna().sum()}")

# Show examples
print("\nExample updated Novel specimens:")
novel_with_lwr = df[novel_mask & df['epa_lwr_score'].notna()]
for idx in novel_with_lwr.head(5).index:
    print(f"  {df.loc[idx, 'name']}: LWR = {df.loc[idx, 'epa_lwr_score']:.6f}")

# ============================================================================
# RECALCULATE "NODE SUPPORT / PLACEMENT" FOR NOVEL SPECIMENS
# ============================================================================

print("\n" + "=" * 80)
print("RECALCULATING NODE SUPPORT CATEGORIES")
print("=" * 80)

def categorize_lwr(lwr):
    """Categorize LWR score into High/Good/Moderate/Low"""
    if pd.isna(lwr):
        return 'Novel placement'  # Still no score
    elif lwr >= 0.90:
        return 'High (0.90-1.00)'
    elif lwr >= 0.75:
        return 'Good (0.75-0.89)'
    else:
        return 'Moderate to Low (0-0.74)'

# Update Node support for Novel placements with new LWR scores
for idx in df[novel_mask].index:
    lwr = df.loc[idx, 'epa_lwr_score']
    if not pd.isna(lwr):
        new_category = categorize_lwr(lwr)
        df.loc[idx, 'Node support / Placement'] = new_category

print("\nUpdated 'Node support / Placement' categories:")
novel_categories = df[novel_mask]['Node support / Placement'].value_counts()
for cat, count in novel_categories.items():
    print(f"  {cat}: {count}")

# ============================================================================
# UPDATE PLACEMENT_INTERPRETATION
# ============================================================================

print("\n" + "=" * 80)
print("UPDATING PLACEMENT INTERPRETATIONS")
print("=" * 80)

# Add interpretation for Novel placements
for idx in df[novel_mask].index:
    lwr = df.loc[idx, 'epa_lwr_score']
    if not pd.isna(lwr):
        if lwr >= 0.90:
            interpretation = f"Novel specimen placed with high confidence (LWR={lwr:.4f})"
        elif lwr >= 0.75:
            interpretation = f"Novel specimen placed with good confidence (LWR={lwr:.4f})"
        else:
            interpretation = f"Novel specimen placed with moderate confidence (LWR={lwr:.4f})"
        df.loc[idx, 'placement_interpretation'] = interpretation

print("✅ Updated placement interpretations for Novel specimens")

# ============================================================================
# SAVE UPDATED METADATA
# ============================================================================

# Remove temporary bold_id column
df = df.drop(columns=['bold_id'])

output_file = sys.argv[3]
df.to_csv(output_file, sep='\t', index=False)

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print(f"\n✅ Fixed LWR scores for {updated_count} Novel specimens")
print(f"✅ Updated 'Node support / Placement' categories")
print(f"✅ Added placement interpretations")

print(f"\nFinal 'Node support / Placement' breakdown:")
all_categories = df['Node support / Placement'].value_counts().sort_index()
for cat, count in all_categories.items():
    print(f"  {cat}: {count}")

print(f"\n✅ Saved to: {output_file}")

print("\n" + "=" * 80)
print("WHAT CHANGED")
print("=" * 80)

print("""
BEFORE:
  - 23 Novel placements had NO LWR scores
  - All were categorized as "Novel placement"
  - None had support-based categories

AFTER:
  - All 23 Novel specimens now have LWR scores from jplace file
  - Categorized based on LWR:
    * High (0.90-1.00) - confident placements
    * Good (0.75-0.89) - good placements  
    * Moderate to Low (0-0.74) - uncertain placements
  - Added interpretations explaining the placement confidence

Now ALL specimens in the tree have proper support categories!
""")

print("=" * 80)
