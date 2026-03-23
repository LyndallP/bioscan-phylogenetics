#!/usr/bin/env python3
"""Create metadata from final tree with EPA-ng placement info"""

import sys
import pandas as pd
import json
from Bio import Phylo

if len(sys.argv) != 4:
    print(f"Usage: {sys.argv[0]} <tree.newick> <epa_result.jplace> <output.tsv>")
    sys.exit(1)

# Load tree
tree = Phylo.read(sys.argv[1], 'newick')
tree_tips = {t.name: t for t in tree.get_terminals()}

# Load jplace for EPA scores
with open(sys.argv[2], 'r') as f:
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

# Build set of BINs present in reference tree tips (not placed queries)
# Used to distinguish 'validation' (BIN already in tree) from 'novel' (new BIN)
reference_bins = set()
for tip_name in tree_tips:
    if tip_name not in placement_scores:
        parts = tip_name.split('|')
        if len(parts) >= 2:
            candidate = parts[0] if parts[0].startswith('BOLD') else parts[1]
            reference_bins.add(candidate)

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
        
        # Check if placed query or reference tree sequence
        if name in placement_scores:
            bin_val = row.get('bin', '')
            row['placement_type'] = 'validation' if bin_val in reference_bins else 'novel'
            lwr = placement_scores[name]
            row['epa_lwr_score'] = lwr
            if lwr >= 0.90:
                row['placement_quality'] = 'High'
            elif lwr >= 0.75:
                row['placement_quality'] = 'Good'
            else:
                row['placement_quality'] = 'Moderate to Low'
        else:
            row['placement_type'] = 'reference_tree'
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
df.to_csv(sys.argv[3], sep='\t', index=False)
print(f"✓ Created basic metadata: {len(df)} rows")
print(f"  Reference tree: {(df['placement_type'] == 'reference_tree').sum()}")
print(f"  Validation (BIN in tree): {(df['placement_type'] == 'validation').sum()}")
print(f"  Novel (new BIN): {(df['placement_type'] == 'novel').sum()}")
print(f"  DTOL: {(df['placement_type'] == 'dtol').sum()}")
print(f"  Polytomy: {(df['placement_type'] == 'polytomy').sum()}")
