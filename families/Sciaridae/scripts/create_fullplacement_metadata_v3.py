#!/usr/bin/env python3
"""
Create comprehensive metadata for ALL tree tips (reference + placed + polytomy)
"""

import pandas as pd
import json
import os
import re

print("="*60)
print("CREATING COMPLETE METADATA")
print("="*60)

# Extract all tip names from tree
print("\n1. Extracting tree tips...")
with open('data/output/sciaridae_COMPLETE.newick', 'r') as f:
    tree_content = f.read()

# Extract all tip labels
tip_pattern = r'([A-Za-z_][^(),:\s]*):[\d.e-]+'
all_tips = re.findall(tip_pattern, tree_content)
print(f"   Found {len(all_tips)} tips in tree")

# Parse tip names into dataframe
tip_data = []
for tip in all_tips:
    parts = tip.split('|')
    if len(parts) >= 3:
        species = parts[0].replace('_', ' ')
        bin_code = parts[1]
        bin_uri = f"BOLD:{bin_code[4:]}" if bin_code.startswith('BOLD') and ':' not in bin_code else bin_code
        process_id = parts[2]
    else:
        species = tip
        bin_uri = 'unknown'
        process_id = 'unknown'
    
    tip_data.append({
        'name': tip,
        'species': species,
        'bin': bin_uri,
        'process_id': process_id
    })

all_metadata = pd.DataFrame(tip_data)
print(f"   Parsed {len(all_metadata)} tips")

# Load placement validation results
print("\n2. Loading placement validation...")
validation = pd.read_csv('data/output/placement_validation_results.csv')

# Merge validation data
all_metadata = all_metadata.merge(
    validation[['bold_bin_uri', 'placement_type', 'placement_quality', 'placement_lwr']],
    left_on='bin',
    right_on='bold_bin_uri',
    how='left'
)

# Fill missing placement data for reference tips
all_metadata['placement_type'] = all_metadata['placement_type'].fillna('reference_tree')
all_metadata['placement_quality'] = all_metadata['placement_quality'].fillna('reference')
all_metadata['placement_interpretation'] = all_metadata.apply(
    lambda row: 'reference' if row['placement_type'] == 'reference_tree' 
    else ('polytomy_no_molecular_data' if row['placement_type'] == 'polytomy'
    else f"{row['placement_quality'].lower()}_confidence"),
    axis=1
)

# Load BIOSCAN specimen counts
print("\n3. Loading BIOSCAN data...")
bioscan = pd.read_csv(os.path.expanduser('~/Desktop/Taxonium/phylogenies/Sciaridae/sciaridae_bioscan.csv'))
specimen_counts = bioscan.groupby('bold_bin_uri').size().reset_index(name='bioscan_specimens')

all_metadata = all_metadata.merge(specimen_counts, left_on='bin', right_on='bold_bin_uri', how='left')
all_metadata['bioscan_specimens'] = all_metadata['bioscan_specimens'].fillna(0).astype(int)

# Load UKSI
print("\n4. Loading UKSI...")
uksi = pd.read_csv(os.path.expanduser('~/Desktop/Taxonium/phylogenies/Sciaridae/sciaridae_uksi.csv'))
uksi_species = set(uksi['species_binomial'].dropna())
all_metadata['in_uksi'] = all_metadata['species'].isin(uksi_species)

# Load BAGS grades
print("\n5. Loading BAGS grades...")
with open(os.path.expanduser('~/Desktop/Taxonium/phylogenies/Sciaridae/curation_data.json'), 'r') as f:
    curation_json = json.load(f)

bin_grades = {}
species_grades = {}

for genus, genus_data in curation_json.get('genera', {}).items():
    for grade_category, entries in genus_data.items():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            species = entry.get('species')
            bins = entry.get('bins', [])
            grade = entry.get('grade')
            n_bins = len(bins)
            
            for bin_uri in bins:
                if bin_uri and bin_uri.startswith('BOLD:'):
                    bin_grades[bin_uri] = {
                        'grade': grade,
                        'n_bins_for_species': n_bins,
                        'all_bins': ', '.join(bins)
                    }
            
            if species and species not in species_grades:
                species_grades[species] = {
                    'grade': grade,
                    'n_bins_for_species': n_bins,
                    'all_bins': ', '.join(bins)
                }

print(f"   Loaded grades for {len(bin_grades)} BINs")

# Add BAGS info
def get_bags_info(row):
    if row['bin'] in bin_grades:
        return bin_grades[row['bin']]
    elif row['species'] in species_grades:
        return species_grades[row['species']]
    return {'grade': 'Unknown', 'n_bins_for_species': 1, 'all_bins': row['bin']}

bags_info = all_metadata.apply(get_bags_info, axis=1, result_type='expand')
all_metadata = pd.concat([all_metadata, bags_info], axis=1)

# Create descriptive fields
print("\n6. Creating descriptive fields...")

def assign_category(row):
    if row['bioscan_specimens'] > 0:
        return 'BIOSCAN_collected' if row['in_uksi'] else 'Not_in_UKSI'
    return 'UKSI_no_specimens' if row['in_uksi'] else 'Europe_reference'

all_metadata['category'] = all_metadata.apply(assign_category, axis=1)
all_metadata['geography'] = all_metadata['in_uksi'].map({True: 'UK', False: 'Europe_or_worldwide'})

def describe_bin_issue(row):
    if row['grade'] == 'C':
        return f"split_across_{row['n_bins_for_species']}_BINs"
    elif row['grade'] == 'E':
        return "shares_BIN_with_other_species"
    elif row['grade'] in ['A', 'B', 'D']:
        return 'clean'
    return 'unknown'

all_metadata['bin_quality_issue'] = all_metadata.apply(describe_bin_issue, axis=1)

all_metadata['needs_attention'] = (
    ((all_metadata['category'] == 'Not_in_UKSI') & (all_metadata['bioscan_specimens'] > 0)) |
    ((all_metadata['placement_quality'] == 'Low') & (all_metadata['bioscan_specimens'] > 100))
)

# Select final columns
final = all_metadata[[
    'name', 'bin', 'species', 'category', 'geography',
    'placement_type', 'placement_quality', 'placement_interpretation', 'placement_lwr',
    'grade', 'bin_quality_issue', 'n_bins_for_species', 'all_bins',
    'in_uksi', 'bioscan_specimens', 'needs_attention'
]].rename(columns={
    'grade': 'bags_grade',
    'placement_lwr': 'epa_lwr_score'
})

output_file = 'data/output/sciaridae_taxonium_metadata_fullplacement.tsv'
final.to_csv(output_file, sep='\t', index=False)

print(f"\n✓ Metadata saved: {output_file}")
print(f"  Total rows: {len(final)}")
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print("\nPlacement types:")
print(final['placement_type'].value_counts())
print("\nCategories:")
print(final['category'].value_counts())
print("\n✓ COMPLETE - Ready for Taxonium!")
