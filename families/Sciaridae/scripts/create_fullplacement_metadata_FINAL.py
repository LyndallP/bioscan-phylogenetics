#!/usr/bin/env python3
"""Create metadata from final tree with EPA-ng placement info"""

import pandas as pd
import json
from Bio import Phylo

# Load tree
tree = Phylo.read('data/output/sciaridae_FINAL.newick', 'newick')
tree_tips = {t.name: t for t in tree.get_terminals()}

# Load jplace for EPA scores
with open('epa_final/epa_result.jplace', 'r') as f:
    jplace = json.load(f)

# Create placement lookup - CONVERT SPACES TO UNDERSCORES!
placement_scores = {}
for placement in jplace['placements']:
    for name in placement['n']:
        # Get LWR (likelihood weight ratio)
        lwr = placement['p'][0][2]
        # Convert spaces to underscores to match tree format
        name_fixed = name.replace(' ', '_')
        placement_scores[name_fixed] = lwr

print(f"Loaded {len(placement_scores)} placement scores")

# Create metadata
metadata = []
for name in tree_tips:
    row = {'name': name}
    
    # Parse name format
    parts = name.split('|')
    
    # Check if DTOL
    if '|id' in name:
        row['bin'] = ''
        row['species'] = parts[0].replace('_', ' ')
        row['placement_type'] = 'dtol'
        row['category'] = ''
    # Check if polytomy
    elif 'polytomy' in name:
        row['bin'] = 'no_BIN'
        row['species'] = parts[0].replace('_', ' ')
        row['placement_type'] = 'polytomy'
        row['category'] = 'UKSI_no_specimens'
    # BIOSCAN or reference
    elif len(parts) >= 3:
        # Could be Species|BIN|ProcessID or BIN|Species|ProcessID
        if parts[0].startswith('BOLD'):
            # BIN|Species|ProcessID
            row['bin'] = parts[0]
            row['species'] = parts[1].replace('_', ' ')
        else:
            # Species|BIN|ProcessID
            row['species'] = parts[0].replace('_', ' ')
            row['bin'] = parts[1]
        
        # Check if placed query or reference
        if name in placement_scores:
            row['placement_type'] = 'bioscan'
            lwr = placement_scores[name]
            row['epa_lwr_score'] = lwr
            if lwr >= 0.75:
                row['placement_quality'] = 'High'
            elif lwr >= 0.5:
                row['placement_quality'] = 'Medium'
            else:
                row['placement_quality'] = 'Low'
        else:
            row['placement_type'] = 'reference'
            row['epa_lwr_score'] = ''
            row['placement_quality'] = ''
        
        row['category'] = ''
    
    # Add empty columns for now
    row['geography'] = ''
    row['placement_interpretation'] = ''
    row['bags_grade'] = ''
    row['bin_quality_issue'] = ''
    row['n_bins_for_species'] = ''
    row['all_bins'] = ''
    row['in_uksi'] = ''
    row['bioscan_specimens'] = ''
    row['needs_attention'] = ''
    
    metadata.append(row)

# Create DataFrame
df = pd.DataFrame(metadata)

# Reorder columns
columns = ['name', 'bin', 'species', 'category', 'geography', 'placement_type', 
           'placement_quality', 'placement_interpretation', 'epa_lwr_score',
           'bags_grade', 'bin_quality_issue', 'n_bins_for_species', 'all_bins',
           'in_uksi', 'bioscan_specimens', 'needs_attention']

df = df[columns]

# Save
df.to_csv('data/output/sciaridae_basic_metadata.tsv', sep='\t', index=False)
print(f"✓ Created basic metadata: {len(df)} rows")
print(f"  Reference: {(df['placement_type'] == 'reference').sum()}")
print(f"  BIOSCAN: {(df['placement_type'] == 'bioscan').sum()}")
print(f"  DTOL: {(df['placement_type'] == 'dtol').sum()}")
print(f"  Polytomy: {(df['placement_type'] == 'polytomy').sum()}")
