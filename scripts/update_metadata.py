#!/usr/bin/env python3
"""
Update Sciaridae metadata with:
1. Split Unknown/Unidentified in category
2. Rename other_bins_for_species -> all_bins_for_species
3. Add bin_status column
4. Update in_uksi values for Unknown/Unidentified
5. Add geography_broad biogeographic regions
"""

import sys
import pandas as pd

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <input_metadata.tsv> <output_metadata.tsv>")
    sys.exit(1)

# Load metadata
print("Loading metadata...")
df = pd.read_csv(sys.argv[1], sep='\t')
print(f"Loaded {len(df)} specimens")

# ============================================================================
# 1. UPDATE CATEGORY - Split Unknown/Unidentified
# ============================================================================
print("\n1. Updating category column...")

def update_category(row):
    """Update category to split Unknown/Unidentified"""
    genus = row['genus']
    name = row['name']
    current_category = row['category']
    
    # Check both genus and name for Unknown/Unidentified
    is_unknown = (genus == 'Unknown') or (name.startswith('Unknown'))
    is_unidentified = (genus == 'Unidentified') or (name.startswith('Unidentified'))
    
    if is_unknown and current_category == "Not in UKSI and BIOSCAN collected":
        return "Unknown (in reference, not BIOSCAN)"
    elif is_unidentified and current_category == "Not in UKSI and BIOSCAN collected":
        return "Unidentified (in BIOSCAN)"
    else:
        # Keep existing category for identified species
        return current_category

df['category'] = df.apply(update_category, axis=1)

print("Category value counts:")
print(df['category'].value_counts())

# ============================================================================
# 2. RENAME other_bins_for_species -> all_bins_for_species
# ============================================================================
print("\n2. Renaming other_bins_for_species to all_bins_for_species...")
df.rename(columns={'other_bins_for_species': 'all_bins_for_species'}, inplace=True)

# ============================================================================
# 3. ADD bin_status COLUMN
# ============================================================================
print("\n3. Creating bin_status column...")

# First, analyze BINs across all rows
bin_species_map = {}  # bin -> set of species
for idx, row in df.iterrows():
    bin_val = row['bin']
    species = row['species']
    
    if pd.notna(bin_val) and bin_val != '':
        if bin_val not in bin_species_map:
            bin_species_map[bin_val] = set()
        if pd.notna(species) and species != '':
            bin_species_map[bin_val].add(species)

# Count species per BIN
bin_species_count = {bin_val: len(species_set) for bin_val, species_set in bin_species_map.items()}

def get_bin_status(row):
    """Determine bin status based on BIN and species relationships"""
    bin_val = row['bin']
    all_bins = row['all_bins_for_species']
    
    statuses = []
    
    # Check if multiple BINs for this species
    if pd.notna(all_bins) and all_bins != '':
        bins_list = [b.strip() for b in all_bins.split(',')]
        if len(bins_list) > 1:
            statuses.append("Multiple BINs for species")
    
    # Check if other species share this BIN
    if pd.notna(bin_val) and bin_val in bin_species_count:
        if bin_species_count[bin_val] > 1:
            statuses.append("Other species share this BIN")
    
    # If neither condition met
    if len(statuses) == 0:
        return "Clean species-BIN match"
    else:
        return "; ".join(statuses)

df['bin_status'] = df.apply(get_bin_status, axis=1)

print("BIN status value counts:")
print(df['bin_status'].value_counts())

# ============================================================================
# 4. UPDATE in_uksi COLUMN - Add Unknown/Unidentified values
# ============================================================================
print("\n4. Updating in_uksi column...")

def update_in_uksi(row):
    """Update in_uksi to include Unknown/Unidentified values"""
    genus = row['genus']
    name = row['name']
    current_uksi = row['in_uksi']
    
    # Check both genus and name for Unknown/Unidentified
    is_unknown = (genus == 'Unknown') or (name.startswith('Unknown'))
    is_unidentified = (genus == 'Unidentified') or (name.startswith('Unidentified'))
    
    if is_unknown:
        return "Unknown in reference"
    elif is_unidentified:
        return "Unidentified in BIOSCAN"
    else:
        # Keep existing TRUE/FALSE for identified species
        return current_uksi

df['in_uksi'] = df.apply(update_in_uksi, axis=1)

print("in_uksi value counts:")
print(df['in_uksi'].value_counts())

# ============================================================================
# 5. ADD geography_broad COLUMN - Biogeographic regions
# ============================================================================
print("\n5. Creating geography_broad column...")

# Biogeographic region mapping
geography_broad_map = {
    # British Isles
    'United Kingdom': 'British Isles',
    
    # Scandinavia
    'Norway': 'Scandinavia',
    'Sweden': 'Scandinavia',
    'Denmark': 'Scandinavia',
    'Finland': 'Scandinavia',
    
    # Western Europe
    'Germany': 'Western Europe',
    'France': 'Western Europe',
    'Belgium': 'Western Europe',
    'Switzerland': 'Western Europe',
    'Austria': 'Western Europe',
    
    # Eastern Europe
    'Poland': 'Eastern Europe',
    'Czechia': 'Eastern Europe',
    'Bulgaria': 'Eastern Europe',
    'Georgia': 'Eastern Europe',
    
    # Southern Europe
    'Portugal': 'Southern Europe',
    'Israel': 'Southern Europe',
    'Lebanon': 'Southern Europe',
    'Iran': 'Southern Europe',
    
    # North America
    'Canada': 'North America',
    'United States': 'North America',
    'Puerto Rico': 'North America',
    'Greenland': 'North America',
    
    # East Asia
    'China': 'East Asia',
    'South Korea': 'East Asia',
    'Japan': 'East Asia',
    'Thailand': 'East Asia',
    'Vietnam': 'East Asia',
    'Cambodia': 'East Asia',
    'Bangladesh': 'East Asia',
    
    # South America
    'Colombia': 'South America',
    'Argentina': 'South America',
    'Costa Rica': 'South America',
    
    # Africa (including Pakistan which is sometimes grouped with Middle East)
    'South Africa': 'Africa',
    'Ghana': 'Africa',
    'Pakistan': 'South Asia',  # Actually South Asia, not Africa
    
    # Oceania
    'Australia': 'Oceania',
    'New Zealand': 'Oceania',
    
    # Unknown
    'Unknown': 'Unknown'
}

df['geography_broad'] = df['geography'].map(geography_broad_map)

# Check for any unmapped values
unmapped = df[df['geography_broad'].isna()]['geography'].unique()
if len(unmapped) > 0:
    print(f"WARNING: Unmapped geography values: {unmapped}")
    # Fill with the original value
    df.loc[df['geography_broad'].isna(), 'geography_broad'] = df.loc[df['geography_broad'].isna(), 'geography']

print("Geography broad value counts:")
print(df['geography_broad'].value_counts().sort_values(ascending=False))

# ============================================================================
# SAVE UPDATED METADATA
# ============================================================================
print("\n" + "="*80)
print("Saving updated metadata...")

# Get column order - insert new columns in logical positions
columns = df.columns.tolist()

# Move geography_broad after geography
geo_idx = columns.index('geography')
columns.remove('geography_broad')
columns.insert(geo_idx + 1, 'geography_broad')

# Move bin_status after all_bins_for_species
bins_idx = columns.index('all_bins_for_species')
columns.remove('bin_status')
columns.insert(bins_idx + 1, 'bin_status')

df = df[columns]

output_file = sys.argv[2]
df.to_csv(output_file, sep='\t', index=False)

print(f"✅ Saved to: {output_file}")
print(f"✅ Total specimens: {len(df)}")
print(f"✅ Total columns: {len(df.columns)}")

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================
print("\n" + "="*80)
print("SUMMARY OF CHANGES")
print("="*80)

print("\n📊 CATEGORY BREAKDOWN:")
print(df['category'].value_counts().sort_index())

print("\n📊 BIN STATUS BREAKDOWN:")
print(df['bin_status'].value_counts())

print("\n📊 IN UKSI BREAKDOWN:")
print(df['in_uksi'].value_counts())

print("\n📊 GEOGRAPHY BROAD BREAKDOWN:")
print(df['geography_broad'].value_counts().sort_values(ascending=False))

print("\n✅ All updates complete!")
