#!/usr/bin/env python3
"""
Add categorical bootstrap support column for easier Taxonium searching
Since Taxonium doesn't support > < operators, we create text categories
"""

import pandas as pd

print("=" * 80)
print("ADDING CATEGORICAL BOOTSTRAP SUPPORT COLUMN")
print("=" * 80)

# Load metadata
df = pd.read_csv('/mnt/user-data/uploads/sciaridae_metadata_FINAL_WITH_IMAGES.tsv', sep='\t')
print(f"\nLoaded {len(df):,} specimens")

# ============================================================================
# CREATE CATEGORICAL BOOTSTRAP COLUMN
# ============================================================================

print("\n1. Creating bootstrap support categories...")

def categorize_bootstrap(bootstrap):
    """
    Categorize bootstrap support values into searchable text categories
    
    Categories:
    - Very High (95-100): Excellent support
    - High (80-94): Strong support
    - Moderate (50-79): Moderate support
    - Low (0-49): Weak support
    - None: No parent node (root or missing)
    """
    if pd.isna(bootstrap):
        return ''
    
    try:
        bs = float(bootstrap)
        if bs >= 95:
            return 'Very High (95-100)'
        elif bs >= 80:
            return 'High (80-94)'
        elif bs >= 50:
            return 'Moderate (50-79)'
        else:
            return 'Low (0-49)'
    except:
        return ''

df['bootstrap_support'] = df['parent_bootstrap'].apply(categorize_bootstrap)

# Count categories
print("\n  Bootstrap support categories:")
category_counts = df['bootstrap_support'].value_counts()
for cat, count in category_counts.items():
    print(f"    {cat}: {count:,}")

# ============================================================================
# REORDER COLUMNS - Put bootstrap_support after parent_bootstrap
# ============================================================================

print("\n2. Reordering columns...")

cols = df.columns.tolist()

# Remove bootstrap_support from wherever it is
if 'bootstrap_support' in cols:
    cols.remove('bootstrap_support')

# Insert after parent_bootstrap
if 'parent_bootstrap' in cols:
    bootstrap_idx = cols.index('parent_bootstrap')
    cols.insert(bootstrap_idx + 1, 'bootstrap_support')

df = df[cols]

print("  ✓ bootstrap_support placed after parent_bootstrap")

# ============================================================================
# SAVE FINAL METADATA
# ============================================================================

output_file = '/mnt/user-data/outputs/sciaridae_metadata_WITH_BOOTSTRAP_CATEGORIES.tsv'
df.to_csv(output_file, sep='\t', index=False)

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print(f"\n✓ Added bootstrap_support column")
print(f"✓ {len(df):,} specimens")
print(f"✓ {len(df.columns)} columns total")

print("\n" + "=" * 80)
print("HOW TO USE IN TAXONIUM")
print("=" * 80)

print("\nNow you can search in Taxonium using text searches:")
print("\n  Search examples:")
print("    bootstrap_support:Very High")
print("    bootstrap_support:High")
print("    bootstrap_support:Moderate")
print("    bootstrap_support:Low")
print("\n  Color by:")
print("    Select 'Color by' → bootstrap_support")
print("    Tree will be colored by support strength!")

print("\n" + "=" * 80)
print("CATEGORY DEFINITIONS")
print("=" * 80)

print("\nVery High (95-100):")
print("  Excellent phylogenetic support")
print("  Very confident in this relationship")

print("\nHigh (80-94):")
print("  Strong support")
print("  Confident in this relationship")

print("\nModerate (50-79):")
print("  Moderate support")
print("  Some uncertainty")

print("\nLow (0-49):")
print("  Weak support")
print("  Considerable uncertainty")

print(f"\n✓ Saved to: {output_file}")

# Show examples
print("\n" + "=" * 80)
print("EXAMPLE SPECIMENS")
print("=" * 80)

# Show one from each category
for cat in ['Very High (95-100)', 'High (80-94)', 'Moderate (50-79)', 'Low (0-49)']:
    examples = df[df['bootstrap_support'] == cat]
    if len(examples) > 0:
        ex = examples.iloc[0]
        print(f"\n{cat}:")
        print(f"  Species: {ex['species']}")
        print(f"  Bootstrap: {ex['parent_bootstrap']}")

print("\n" + "=" * 80 + "\n")
