#!/usr/bin/env python3
"""
Add subfamily column to Sciaridae metadata based on genus
Uses classification from Shin et al. (2012) molecular phylogeny

Note: For other families, create a family-specific equivalent of this script
with the appropriate genus→subfamily mapping for that family.
"""

import sys
import pandas as pd

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <input_metadata.tsv> <output_metadata.tsv>")
    sys.exit(1)

# Load metadata
df = pd.read_csv(sys.argv[1], sep='\t')

# Extract genus from species column if not already present
if 'genus' not in df.columns:
    df['genus'] = df['species'].str.split().str[0]

print("=" * 80)
print("ADDING SUBFAMILY COLUMN")
print("=" * 80)

# Subfamily mapping based on Shin et al. (2012) and subsequent literature
# NOTE: Many genera are non-monophyletic, so this is approximate!

SUBFAMILY_MAP = {
    # Sciarinae (largest subfamily - most common genera)
    'Bradysia': 'Sciarinae',
    'Corynoptera': 'Sciarinae',
    'Lycoriella': 'Sciarinae',
    'Leptosciarella': 'Sciarinae',
    'Phytosciara': 'Sciarinae',
    'Scatopsciara': 'Sciarinae',
    'Schwenckfeldina': 'Sciarinae',
    'Sciara': 'Sciarinae',
    'Scythropochroa': 'Sciarinae',
    'Cratyna': 'Cratyninae',  # Cratyninae (small, polyphyletic)
    'Pseudolycoriella': 'Pseudolycoriella group',  # Unplaced genus group
    'Megalosphys': 'Megalosphyinae',  # Megalosphyinae
    'Chaetosciara': 'Chaetosciara group',  # Chaetosciara group
    'Epidapus': 'Sciarinae',
    'Sciaridae': 'Sciarinae',  # Generic family-level records → default to Sciarinae
    'Plastosciara': 'Sciarinae',
    'Zygoneura': 'Sciarinae',
}

print(f"\nMapping {len(SUBFAMILY_MAP)} genera to subfamilies")

# Create subfamily column
def assign_subfamily(genus):
    """Assign subfamily based on genus"""
    if pd.isna(genus) or genus == '':
        return 'Unknown'
    
    # Direct lookup
    if genus in SUBFAMILY_MAP:
        return SUBFAMILY_MAP[genus]
    
    # If not in map, mark as Sciarinae (most likely) with uncertainty
    return 'Sciarinae (inferred)'

df['subfamily'] = df['genus'].apply(assign_subfamily)

# Count subfamilies
print("\nSubfamily distribution:")
subfamily_counts = df['subfamily'].value_counts()
for subfamily, count in subfamily_counts.items():
    print(f"  {subfamily}: {count:,}")

# Insert subfamily after family
cols = df.columns.tolist()
if 'subfamily' in cols:
    cols.remove('subfamily')
if 'family' in cols:
    family_idx = cols.index('family')
    cols.insert(family_idx + 1, 'subfamily')
else:
    # If no family column, add at end
    cols.append('subfamily')

df = df[cols]

# Save
output_file = sys.argv[2]
df.to_csv(output_file, sep='\t', index=False)

print(f"\n✓ Saved to: {output_file}")

# Show examples
print("\n" + "=" * 80)
print("EXAMPLE ASSIGNMENTS")
print("=" * 80)

for subfamily in subfamily_counts.index[:5]:
    examples = df[df['subfamily'] == subfamily].head(3)
    print(f"\n{subfamily}:")
    for _, row in examples.iterrows():
        species = row['species'] if pd.notna(row['species']) else 'Unknown'
        print(f"  {row['genus']} {species}")

print("\n" + "=" * 80)
print("NOTES")
print("=" * 80)
print("""
1. Classification based on Shin et al. (2012) molecular phylogeny
2. Many genera (Bradysia, Corynoptera, Leptosciarella) are non-monophyletic
3. Subfamily Cratyninae is polyphyletic
4. Unknown genera assigned as "Sciarinae (inferred)" - most common subfamily
5. For publication, cite: Shin et al. (2012) Molecular Ecology 21(18): 4673-4686

⚠️  Subfamily classification in Sciaridae is taxonomically unstable!
    Use with caution and check recent literature for updates.
""")

print("=" * 80 + "\n")
