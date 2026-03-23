#!/usr/bin/env python3
"""
Create unified "Node support / Placement" column combining:
- Bootstrap support (for reference tree nodes)
- EPA-ng LWR scores (for placed BIOSCAN/DTOL specimens)

This gives every specimen a searchable support category!
"""

import sys
import pandas as pd

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <input_metadata.tsv> <output_metadata.tsv>")
    sys.exit(1)

print("=" * 80)
print("CREATING UNIFIED NODE SUPPORT / PLACEMENT COLUMN")
print("=" * 80)

# Load metadata
df = pd.read_csv(sys.argv[1], sep='\t')
print(f"\nLoaded {len(df):,} specimens")

# ============================================================================
# CREATE UNIFIED SUPPORT COLUMN
# ============================================================================

print("\n1. Creating unified support categories...")

def create_unified_support(row):
    """
    Create unified support category using:
    1. Bootstrap for reference tree nodes (placement_type = reference_tree)
    2. LWR score for placed specimens (placement_type = validation)
    3. Novel for newly placed specimens without reference
    
    Categories based on commonly used thresholds:
    Bootstrap: 95+ = Very High, 80-94 = High, 50-79 = Moderate, 0-49 = Low
    LWR: 0.99+ = Very High, 0.95-0.989 = High, 0.75-0.949 = Moderate, <0.75 = Low
    
    Returns searchable text like:
    - "Very High (Bootstrap 100)"
    - "High (LWR 0.98)"
    - "Novel placement"
    """
    
    placement_type = row.get('placement_type', '')
    
    # Reference tree nodes - use bootstrap
    if placement_type == 'reference_tree':
        bootstrap = row.get('parent_bootstrap')
        if pd.isna(bootstrap):
            return 'Reference (no bootstrap)'
        
        bs = float(bootstrap)
        if bs >= 95:
            return 'Very High (Bootstrap)'
        elif bs >= 80:
            return 'High (Bootstrap)'
        elif bs >= 50:
            return 'Moderate (Bootstrap)'
        else:
            return 'Low (Bootstrap)'
    
    # Validation placements (BIOSCAN, DTOL) - use LWR
    elif placement_type == 'validation':
        lwr = row.get('epa_lwr_score')
        if pd.isna(lwr):
            return 'Placed (no LWR score)'
        
        lwr_val = float(lwr)
        if lwr_val >= 0.99:
            return 'Very High (LWR)'
        elif lwr_val >= 0.95:
            return 'High (LWR)'
        elif lwr_val >= 0.75:
            return 'Moderate (LWR)'
        else:
            return 'Low (LWR)'
    
    # Novel placements
    elif placement_type == 'novel':
        return 'Novel placement'
    
    # Fallback
    else:
        return 'Unknown'

df['Node support / Placement'] = df.apply(create_unified_support, axis=1)

# Count categories
print("\n  Support categories created:")
category_counts = df['Node support / Placement'].value_counts()
for cat, count in category_counts.items():
    print(f"    {cat}: {count:,}")

# ============================================================================
# REORDER COLUMNS
# ============================================================================

print("\n2. Reordering columns...")

cols = df.columns.tolist()

# Remove the new column
if 'Node support / Placement' in cols:
    cols.remove('Node support / Placement')

# Insert after bootstrap_support
if 'bootstrap_support' in cols:
    bootstrap_idx = cols.index('bootstrap_support')
    cols.insert(bootstrap_idx + 1, 'Node support / Placement')
else:
    # If bootstrap_support doesn't exist, put after parent_bootstrap
    if 'parent_bootstrap' in cols:
        bootstrap_idx = cols.index('parent_bootstrap')
        cols.insert(bootstrap_idx + 1, 'Node support / Placement')

df = df[cols]

print("  ✓ 'Node support / Placement' column added")

# ============================================================================
# SAVE FINAL METADATA
# ============================================================================

output_file = sys.argv[2]
df.to_csv(output_file, sep='\t', index=False)

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print(f"\n✓ Created unified 'Node support / Placement' column")
print(f"✓ {len(df):,} specimens")
print(f"✓ {len(df.columns)} columns total")

print("\n" + "=" * 80)
print("HOW TO USE IN TAXONIUM")
print("=" * 80)

print("\nSearch examples:")
print("  Node support / Placement:Very High (Bootstrap)")
print("  Node support / Placement:Very High (LWR)")
print("  Node support / Placement:High")
print("  Node support / Placement:Novel placement")

print("\nColor by:")
print("  Select 'Color by' → 'Node support / Placement'")
print("  Now ALL specimens get colored by their support!")
print("    - Reference tree nodes: colored by bootstrap")
print("    - BIOSCAN/DTOL: colored by EPA-ng LWR score")
print("    - Novel placements: distinct color")

print("\n" + "=" * 80)
print("CATEGORY BREAKDOWN BY SOURCE")
print("=" * 80)

print("\nReference tree nodes (bootstrap-based):")
ref_df = df[df['placement_type'] == 'reference_tree']
for cat in sorted(ref_df['Node support / Placement'].unique()):
    count = (ref_df['Node support / Placement'] == cat).sum()
    print(f"  {cat}: {count:,}")

print("\nPlaced specimens (LWR-based):")
placed_df = df[df['placement_type'] == 'validation']
for cat in sorted(placed_df['Node support / Placement'].unique()):
    count = (placed_df['Node support / Placement'] == cat).sum()
    print(f"  {cat}: {count:,}")

print("\nNovel placements:")
novel_df = df[df['placement_type'] == 'novel']
for cat in sorted(novel_df['Node support / Placement'].unique()):
    count = (novel_df['Node support / Placement'] == cat).sum()
    print(f"  {cat}: {count:,}")

print("\n" + "=" * 80)
print("SUPPORT THRESHOLDS")
print("=" * 80)

print("\nBootstrap (reference tree):")
print("  Very High: ≥95")
print("  High: 80-94")
print("  Moderate: 50-79")
print("  Low: <50")

print("\nLWR (EPA-ng placements):")
print("  Very High: ≥0.99")
print("  High: 0.95-0.989")
print("  Moderate: 0.75-0.949")
print("  Low: <0.75")

print(f"\n✓ Saved to: {output_file}")

# Show examples
print("\n" + "=" * 80)
print("EXAMPLE SPECIMENS")
print("=" * 80)

# Show examples from each main category
for cat in ['Very High (Bootstrap)', 'Very High (LWR)', 'Novel placement']:
    examples = df[df['Node support / Placement'] == cat]
    if len(examples) > 0:
        ex = examples.iloc[0]
        print(f"\n{cat}:")
        print(f"  Species: {ex['species']}")
        print(f"  Dataset: {ex['dataset']}")
        if 'Bootstrap' in cat:
            print(f"  Bootstrap value: {ex['parent_bootstrap']}")
        elif 'LWR' in cat:
            print(f"  LWR score: {ex['epa_lwr_score']}")

print("\n" + "=" * 80)
print("✅ FINAL METADATA READY FOR TAXONIUM!")
print("=" * 80)
print("\nThis file combines:")
print("  ✓ BIOSCAN specimen images (ThumbnailURL)")
print("  ✓ External links with icons")
print("  ✓ Readable category labels")
print("  ✓ Unified node support for ALL specimens")
print("\nUpload sciaridae_metadata_FINAL_COMPLETE.tsv to Taxonium!")

print("\n" + "=" * 80 + "\n")
