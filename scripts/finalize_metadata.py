#!/usr/bin/env python3
"""
Final metadata updates:
1. Remove bootstrap_support column (redundant)
2. Update Node support / Placement categories to:
   - High (0.90-1.00)
   - Good (0.75-0.89)
   - Moderate to Low (0-0.74)
"""

import sys
import pandas as pd

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <input_metadata.tsv> <output_metadata.tsv>")
    sys.exit(1)

print("=" * 80)
print("UPDATING NODE SUPPORT CATEGORIES")
print("=" * 80)

# Load metadata
df = pd.read_csv(sys.argv[1], sep='\t')
print(f"\nLoaded {len(df):,} specimens")
print(f"Current columns: {len(df.columns)}")

# ============================================================================
# UPDATE NODE SUPPORT CATEGORIES
# ============================================================================

print("\n1. Updating support categories...")

def create_support_category(row):
    """
    Unified support categories for all specimens:
    
    For reference tree nodes (bootstrap):
    - High (0.90-1.00): Bootstrap 90-100
    - Good (0.75-0.89): Bootstrap 75-89
    - Moderate to Low (0-0.74): Bootstrap 0-74
    
    For placed specimens (LWR):
    - High (0.90-1.00): LWR 0.90-1.00
    - Good (0.75-0.89): LWR 0.75-0.89
    - Moderate to Low (0-0.74): LWR 0-0.74
    
    Special cases:
    - Novel placement (no reference match)
    - No support data available
    """
    
    placement_type = row.get('placement_type', '')
    
    # Reference tree nodes - use bootstrap
    if placement_type == 'reference_tree':
        bootstrap = row.get('parent_bootstrap')
        if pd.isna(bootstrap):
            return 'No support data'
        
        bs = float(bootstrap)
        if bs >= 90:
            return 'High (0.90-1.00)'
        elif bs >= 75:
            return 'Good (0.75-0.89)'
        else:
            return 'Moderate to Low (0-0.74)'
    
    # Validation placements (BIOSCAN, DTOL) - use LWR
    elif placement_type == 'validation':
        lwr = row.get('epa_lwr_score')
        if pd.isna(lwr):
            return 'No support data'
        
        lwr_val = float(lwr)
        if lwr_val >= 0.90:
            return 'High (0.90-1.00)'
        elif lwr_val >= 0.75:
            return 'Good (0.75-0.89)'
        else:
            return 'Moderate to Low (0-0.74)'
    
    # Novel placements
    elif placement_type == 'novel':
        return 'Novel placement'
    
    # Fallback
    else:
        return 'No support data'

df['Node support / Placement'] = df.apply(create_support_category, axis=1)

# Count new categories
print("\n  Updated categories:")
category_counts = df['Node support / Placement'].value_counts()
for cat, count in category_counts.items():
    print(f"    {cat}: {count:,}")

# ============================================================================
# CATEGORY
# ============================================================================

print("\n2. Computing category...")

bioscan_count = pd.to_numeric(df.get('Bioscan specimen count', 0), errors='coerce').fillna(0)
in_uksi = df.get('in_uksi', False).fillna(False).astype(bool)

def assign_category(row):
    pt = row.get('placement_type', '')
    if pt == 'polytomy':
        return 'UKSI_no_specimens'
    if pt == 'dtol':
        return 'DTOL'
    # BIOSCAN and reference tree rows
    count = pd.to_numeric(row.get('Bioscan specimen count', 0), errors='coerce') or 0
    uksi  = bool(row.get('in_uksi', False))
    if count > 0:
        return 'BIOSCAN_collected' if uksi else 'Not_in_UKSI'
    else:
        return 'UKSI_no_specimens' if uksi else 'Europe_reference'

df['category'] = df.apply(assign_category, axis=1)
print(f"   category distribution:")
for cat, count in df['category'].value_counts().items():
    print(f"     {cat}: {count:,}")

# ============================================================================
# NEEDS_ATTENTION
# ============================================================================

print("\n3. Computing needs_attention...")

df['needs_attention'] = (
    (df['category'] == 'Not_in_UKSI') |
    (df['placement_quality'] == 'Moderate to Low')
)

needs_count = df['needs_attention'].sum()
print(f"   {needs_count:,} rows flagged as needs_attention")

# ============================================================================
# REMOVE BOOTSTRAP_SUPPORT COLUMN
# ============================================================================

print("\n4. Removing unused columns...")

to_drop = ['bootstrap_support', 'placement_interpretation', 'bold_nuc']
dropped = [c for c in to_drop if c in df.columns]
if dropped:
    df = df.drop(columns=dropped)
    for c in dropped:
        print(f"  ✓ Removed {c}")
else:
    print("  (no columns to remove)")

# n_bins_for_species: pandas reads mixed numeric/empty columns as float (3.0).
# Convert to integer string so it displays as 3, not 3.0.
if 'n_bins_for_species' in df.columns:
    df['n_bins_for_species'] = df['n_bins_for_species'].apply(
        lambda x: '' if (pd.isna(x) or str(x).strip() in ('', 'nan')) else str(int(float(x)))
    )

print(f"\n  Final column count: {len(df.columns)}")

# ============================================================================
# SAVE FINAL METADATA
# ============================================================================

output_file = sys.argv[2]
df.to_csv(output_file, sep='\t', index=False)

print("\n" + "=" * 80)
print("SUMMARY BY SOURCE")
print("=" * 80)

print("\nReference tree nodes (bootstrap):")
ref_df = df[df['placement_type'] == 'reference_tree']
for cat in ['High (0.90-1.00)', 'Good (0.75-0.89)', 'Moderate to Low (0-0.74)', 'No support data']:
    count = (ref_df['Node support / Placement'] == cat).sum()
    if count > 0:
        print(f"  {cat}: {count:,}")

print("\nPlaced specimens - BIOSCAN/DTOL (LWR):")
placed_df = df[df['placement_type'] == 'validation']
for cat in ['High (0.90-1.00)', 'Good (0.75-0.89)', 'Moderate to Low (0-0.74)', 'No support data']:
    count = (placed_df['Node support / Placement'] == cat).sum()
    if count > 0:
        print(f"  {cat}: {count:,}")

print("\nNovel placements:")
novel_count = (df['Node support / Placement'] == 'Novel placement').sum()
print(f"  Novel placement: {novel_count:,}")

print("\n" + "=" * 80)
print("FINAL METADATA STRUCTURE")
print("=" * 80)

print(f"\n✓ Total specimens: {len(df):,}")
print(f"✓ Total columns: {len(df.columns)}")
print(f"✓ Removed: bootstrap_support (redundant)")
print(f"✓ Updated: Node support / Placement (3 clear categories)")

print("\n" + "=" * 80)
print("TAXONIUM USAGE")
print("=" * 80)

print("\nColor by support:")
print("  Color by → Node support / Placement")
print("  Colors:")
print("    • High (0.90-1.00) - Strong confidence")
print("    • Good (0.75-0.89) - Good confidence")
print("    • Moderate to Low (0-0.74) - Needs review")
print("    • Novel placement - Unique specimens")

print("\nSearch examples:")
print("  Node support / Placement:High")
print("  Node support / Placement:Moderate to Low")
print("  Node support / Placement:Novel placement")

print(f"\n✓ Saved to: {output_file}")
print("\n" + "=" * 80 + "\n")
