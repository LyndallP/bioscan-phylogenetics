#!/usr/bin/env python3
"""
Create comprehensive metadata for full BIN placement approach.
"""

import pandas as pd
import json
import os

print("="*60)
print("CREATING FULL PLACEMENT METADATA")
print("="*60)

# Load placement validation results
print("\n1. Loading placement validation results...")
validation = pd.read_csv('data/output/placement_validation_results.csv')
print(f"   Loaded {len(validation)} BIN representatives")

# Load BIOSCAN data
print("\n2. Loading BIOSCAN data...")
bioscan = pd.read_csv(os.path.expanduser('~/Desktop/Taxonium/phylogenies/Sciaridae/sciaridae_bioscan.csv'))
specimen_counts = bioscan.groupby('bold_bin_uri').size().reset_index(name='bioscan_specimens')
print(f"   Specimen counts for {len(specimen_counts)} BINs")

# Load UKSI data
print("\n3. Loading UKSI data...")
uksi = pd.read_csv(os.path.expanduser('~/Desktop/Taxonium/phylogenies/Sciaridae/sciaridae_uksi.csv'))
uksi_species = set(uksi['species_binomial'].dropna())
print(f"   {len(uksi_species)} species in UKSI")

# Load BAGS grade data
print("\n4. Loading BAGS grade data...")
with open(os.path.expanduser('~/Desktop/Taxonium/phylogenies/Sciaridae/curation_data.json'), 'r') as f:
    curation_json = json.load(f)

# Parse nested genera structure
bin_grades = {}
species_grades = {}

for genus, genus_data in curation_json.get('genera', {}).items():
    # Process all grade categories
    for grade_category, entries in genus_data.items():
        if not isinstance(entries, list):
            continue
            
        for entry in entries:
            species = entry.get('species')
            bins = entry.get('bins', [])
            grade = entry.get('grade')
            n_bins = len(bins)
            
            # Store by BIN
            for bin_uri in bins:
                if bin_uri and bin_uri.startswith('BOLD:'):
                    bin_grades[bin_uri] = {
                        'grade': grade,
                        'species': species,
                        'n_bins_for_species': n_bins,
                        'all_bins': ', '.join(bins)
                    }
            
            # Store by species
            if species and species not in species_grades:
                species_grades[species] = {
                    'grade': grade,
                    'n_bins_for_species': n_bins,
                    'all_bins': ', '.join(bins)
                }

print(f"   BAGS grades for {len(bin_grades)} BINs, {len(species_grades)} species")

# Merge data
print("\n5. Merging all data sources...")
metadata = validation.copy()

# Add specimen counts
metadata = metadata.merge(specimen_counts, on='bold_bin_uri', how='left')
metadata['bioscan_specimens'] = metadata['bioscan_specimens'].fillna(0).astype(int)

# Add UKSI membership
metadata['species_clean'] = metadata['bold_species'].fillna('Unknown').str.replace('_', ' ')
metadata['in_uksi'] = metadata['species_clean'].isin(uksi_species)

# Add BAGS grades
def get_bags_info(row):
    if row['bold_bin_uri'] in bin_grades:
        return bin_grades[row['bold_bin_uri']]
    elif row['species_clean'] in species_grades:
        return species_grades[row['species_clean']]
    else:
        return {
            'grade': 'Unknown',
            'species': row['species_clean'],
            'n_bins_for_species': 1,
            'all_bins': row['bold_bin_uri']
        }

bags_info = metadata.apply(get_bags_info, axis=1, result_type='expand')
metadata = pd.concat([metadata, bags_info], axis=1)

# Create descriptive columns
print("\n6. Creating descriptive metadata...")

def assign_category(row):
    if row['bioscan_specimens'] > 0:
        return 'BIOSCAN_collected' if row['in_uksi'] else 'Not_in_UKSI'
    else:
        return 'UKSI_no_specimens' if row['in_uksi'] else 'Europe_reference'

metadata['category'] = metadata.apply(assign_category, axis=1)
metadata['geography'] = metadata['in_uksi'].map({True: 'UK', False: 'Europe_or_worldwide'})

def describe_bin_issue(row):
    if row['grade'] == 'C':
        return f"split_across_{row['n_bins_for_species']}_BINs"
    elif row['grade'] == 'E':
        return "shares_BIN_with_other_species"
    elif row['grade'] in ['A', 'B', 'D']:
        return 'clean'
    return 'unknown'

metadata['bin_quality_issue'] = metadata.apply(describe_bin_issue, axis=1)

def interpret_placement(row):
    if row['placement_quality'] == 'Low':
        return 'polytomy_low_confidence' if row['placement_type'] == 'validation' else 'novel_low_confidence'
    return row['placement_quality'].lower() + '_confidence'

metadata['placement_interpretation'] = metadata.apply(interpret_placement, axis=1)

metadata['needs_attention'] = (
    ((metadata['category'] == 'Not_in_UKSI') & (metadata['bioscan_specimens'] > 0)) |
    ((metadata['placement_quality'] == 'Low') & (metadata['bioscan_specimens'] > 100))
)

metadata['name'] = (metadata['bold_bin_uri'].str.replace('BOLD:', 'BOLD') + '|' + 
                   metadata['bold_species'].fillna('Unknown_species') + '|' + 
                   metadata['bold_processid'])

# Add polytomy
print("\n7. Adding polytomy...")
polytomy = pd.DataFrame([{
    'name': 'Xylosciara_betulae|no_BIN|polytomy',
    'bold_bin_uri': 'no_BIN',
    'bold_species': 'Xylosciara betulae',
    'placement_type': 'polytomy',
    'placement_quality': 'no_molecular_data',
    'placement_interpretation': 'polytomy_no_molecular_data',
    'bioscan_specimens': 0,
    'in_uksi': True,
    'grade': 'Unknown',
    'category': 'UKSI_no_specimens',
    'geography': 'UK',
    'bin_quality_issue': 'no_molecular_data',
    'needs_attention': False,
    'n_bins_for_species': 0
}])

metadata = pd.concat([metadata, polytomy], ignore_index=True)

# Select final columns
print("\n8. Selecting final columns...")
final_metadata = metadata[[
    'name', 'bold_bin_uri', 'bold_species', 'category', 'geography',
    'placement_type', 'placement_quality', 'placement_interpretation', 'placement_lwr',
    'grade', 'bin_quality_issue', 'n_bins_for_species', 'all_bins',
    'in_uksi', 'bioscan_specimens', 'needs_attention'
]].rename(columns={
    'bold_bin_uri': 'bin',
    'bold_species': 'species',
    'grade': 'bags_grade',
    'placement_lwr': 'epa_lwr_score'
})

output_file = 'data/output/sciaridae_taxonium_metadata_fullplacement.tsv'
final_metadata.to_csv(output_file, sep='\t', index=False)

print(f"\n✓ Metadata saved: {output_file}")
print(f"  Total rows: {len(final_metadata)}")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print("\nPlacement types:")
print(final_metadata['placement_type'].value_counts())
print("\nCategories:")
print(final_metadata['category'].value_counts())
print("\n✓ COMPLETE!")
