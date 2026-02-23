#!/usr/bin/env python3
import pandas as pd

# Load the metadata that has wrong geography
df = pd.read_csv('data/output/sciaridae_metadata_enhanced.tsv', sep='\t')

# Load BOLD countries
bold = pd.read_csv('data/reference_tree_bold_countries.tsv', sep='\t')

# Extract processid from names
df['processid_extracted'] = df['name'].str.split('|').str[2]

# Merge with BOLD data
df = df.merge(
    bold[['processid', 'country_ocean']],
    left_on='processid_extracted',
    right_on='processid',
    how='left'
)

# Fix geography based on NEW placement types
def fix_geography(row):
    if row['placement_type'] == 'reference':
        return row['country_ocean'] if pd.notna(row['country_ocean']) else 'Unknown'
    elif row['placement_type'] == 'bioscan':
        return 'United Kingdom'
    elif row['placement_type'] == 'dtol':
        return 'United Kingdom'
    elif row['placement_type'] == 'polytomy':
        return 'United Kingdom'
    return 'Unknown'

df['geography'] = df.apply(fix_geography, axis=1)

# Drop temp columns
df = df.drop(columns=['processid_extracted', 'processid', 'country_ocean'], errors='ignore')

# Save
df.to_csv('data/output/sciaridae_taxonium_metadata_COMPLETE.tsv', sep='\t', index=False)

print(f"✓ Fixed metadata: {len(df)} rows")
print(f"\nGeography breakdown:")
print(df['geography'].value_counts().head(10))
