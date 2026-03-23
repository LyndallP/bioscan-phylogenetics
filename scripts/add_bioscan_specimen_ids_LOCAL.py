#!/usr/bin/env python3
"""
Add sts_specimen.id from BIOSCAN data and create Sanger image URLs
RUN THIS ON YOUR MAC in the directory with the metadata file

Usage:
  python3 add_bioscan_specimen_ids_LOCAL.py
"""

import sys
import pandas as pd
import os

if len(sys.argv) != 4:
    print(f"Usage: {sys.argv[0]} <bioscan_data.tsv> <input_metadata.tsv> <output_metadata.tsv>")
    sys.exit(1)

print("=" * 80)
print("ADDING BIOSCAN SPECIMEN IDs AND IMAGE URLs")
print("=" * 80)

# ============================================================================
# 1. LOAD ORIGINAL BIOSCAN DATA
# ============================================================================

print("\n1. Loading original BIOSCAN data...")
bioscan_file = sys.argv[1]

try:
    bioscan_data = pd.read_csv(bioscan_file, sep='\t')
    print(f"   ✓ Loaded {len(bioscan_data):,} BIOSCAN records")
    
    # Check for required columns
    required_cols = ['sts_specimen.id', 'bold_processid']
    missing = [col for col in required_cols if col not in bioscan_data.columns]
    
    if missing:
        print(f"\n   ERROR: Missing columns: {missing}")
        print(f"   Available columns: {list(bioscan_data.columns[:10])}")
        exit(1)
        
    print(f"   ✓ Found required columns")
    
    # Create lookup dictionary: bold_processid -> sts_specimen.id
    specimen_lookup = dict(zip(bioscan_data['bold_processid'], bioscan_data['sts_specimen.id']))
    print(f"   ✓ Created lookup for {len(specimen_lookup):,} processids")
    
except FileNotFoundError:
    print(f"\n   ERROR: File not found: {bioscan_file}")
    print(f"   Please check the file path")
    exit(1)
except Exception as e:
    print(f"\n   ERROR: {e}")
    exit(1)

# ============================================================================
# 2. LOAD CURRENT METADATA (from Downloads folder)
# ============================================================================

print("\n2. Loading current metadata...")

metadata_file = sys.argv[2]
df = pd.read_csv(metadata_file, sep='\t')
print(f"   ✓ Loaded {len(df):,} specimens from {os.path.basename(metadata_file)}")

# ============================================================================
# 3. EXTRACT PROCESSID FROM TIP NAMES AND MATCH
# ============================================================================

print("\n3. Matching to BIOSCAN data...")

def extract_processid_from_name(name):
    """Extract processid from tip name: Species|BIN|ProcessID"""
    if pd.isna(name):
        return None
    parts = name.split('|')
    if len(parts) >= 3:
        return parts[2]
    return None

# Extract processid from name if not already present
if 'processid' not in df.columns:
    df['processid'] = df['name'].apply(extract_processid_from_name)

# Look up sts_specimen.id using processid
df['sts_specimen.id'] = df['processid'].map(specimen_lookup)

matched_count = df['sts_specimen.id'].notna().sum()
bioscan_count = (df['dataset'] == 'BIOSCAN').sum()

print(f"   ✓ Matched {matched_count:,} specimens to BIOSCAN data")
print(f"   Total BIOSCAN specimens in tree: {bioscan_count:,}")

if matched_count < bioscan_count:
    print(f"   ⚠ {bioscan_count - matched_count:,} BIOSCAN specimens missing sts_specimen.id")

# ============================================================================
# 4. CREATE SANGER IMAGE URLs
# ============================================================================

print("\n4. Creating Sanger image URLs...")

def create_sanger_thumbnail_url(row):
    """
    Create Sanger image URL using sts_specimen.id
    Format: https://tol-bioscan-images.cog.sanger.ac.uk/processed_images/{sts_specimen.id}.jpg
    """
    if pd.isna(row['sts_specimen.id']):
        return ''
    
    # Only for BIOSCAN specimens
    if row['dataset'] != 'BIOSCAN':
        return ''
    
    return f"https://tol-bioscan-images.cog.sanger.ac.uk/processed_images/{row['sts_specimen.id']}.jpg"

df['ThumbnailURL'] = df.apply(create_sanger_thumbnail_url, axis=1)

thumbnail_count = (df['ThumbnailURL'] != '').sum()
print(f"   ✓ Created {thumbnail_count:,} Sanger image URLs")

# ============================================================================
# 5. REORDER COLUMNS
# ============================================================================

print("\n5. Reordering columns...")

# Get current columns
cols = df.columns.tolist()

# Remove ThumbnailURL and sts_specimen.id to reposition them
for col in ['ThumbnailURL', 'sts_specimen.id']:
    if col in cols:
        cols.remove(col)

# Remove old specimen_id if present
if 'specimen_id' in cols:
    cols.remove('specimen_id')

# Insert ThumbnailURL after species
species_idx = cols.index('species') if 'species' in cols else 3
cols.insert(species_idx + 1, 'ThumbnailURL')

# Insert sts_specimen.id after processid
if 'processid' in cols:
    processid_idx = cols.index('processid')
    cols.insert(processid_idx + 1, 'sts_specimen.id')

df = df[cols]

print("   ✓ Reordered columns")

# ============================================================================
# 6. SAVE FINAL METADATA
# ============================================================================

output_file = sys.argv[3]
df.to_csv(output_file, sep='\t', index=False)

print("\n" + "=" * 80)
print("SUCCESS!")
print("=" * 80)

print(f"\n✓ BIOSCAN specimen IDs added: {matched_count:,}")
print(f"✓ Sanger image URLs created: {thumbnail_count:,}")
print(f"\n✓ Saved to: {output_file}")
print(f"  Rows: {len(df):,}")
print(f"  Columns: {len(df.columns)}")

# Show breakdown
print("\n" + "=" * 80)
print("BREAKDOWN BY DATASET")
print("=" * 80)

for dataset in sorted(df['dataset'].dropna().unique()):
    dataset_df = df[df['dataset'] == dataset]
    has_id = dataset_df['sts_specimen.id'].notna().sum()
    has_image = (dataset_df['ThumbnailURL'] != '').sum()
    print(f"\n{dataset}:")
    print(f"  Total specimens: {len(dataset_df):,}")
    print(f"  With sts_specimen.id: {has_id:,}")
    print(f"  With image URL: {has_image:,}")

# Show examples
print("\n" + "=" * 80)
print("EXAMPLE BIOSCAN SPECIMENS WITH IMAGES")
print("=" * 80)

examples = df[(df['ThumbnailURL'] != '') & (df['sts_specimen.id'].notna())].head(3)

if len(examples) > 0:
    for idx, row in examples.iterrows():
        print(f"\n{row['species']}")
        print(f"  ProcessID: {row['processid']}")
        print(f"  sts_specimen.id: {row['sts_specimen.id']}")
        print(f"  Image URL: {row['ThumbnailURL']}")
else:
    print("\nNo BIOSCAN specimens with images found")

print("\n" + "=" * 80)
print("NEXT STEPS")
print("=" * 80)
print(f"\n1. File saved to: {output_file}")
print("2. Upload this file to Taxonium along with your tree")
print("3. Taxonium will display thumbnails from the ThumbnailURL column")
print("\n✓ Done!")

print("\n" + "=" * 80 + "\n")
