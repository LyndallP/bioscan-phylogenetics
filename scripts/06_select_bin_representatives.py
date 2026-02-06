#!/usr/bin/env python3
"""
Select one representative sequence per BIN for phylogenetic placement.
Prioritizes longest, highest quality sequences.
"""

import pandas as pd
import sys
import re

def select_representatives(bioscan_file, tree_file, output_fasta):
    """
    Select one representative per BIN from BIOSCAN data.
    """
    print(f"Loading BIOSCAN data: {bioscan_file}")
    bioscan = pd.read_csv(bioscan_file)
    
    print(f"Total BIOSCAN records: {len(bioscan)}")
    print(f"Unique BINs: {bioscan['bold_bin_uri'].nunique()}")
    
    # Calculate sequence quality metrics
    bioscan['seq_length'] = bioscan['bold_nuc'].fillna('').str.len()
    bioscan['n_ambiguous'] = bioscan['bold_nuc'].fillna('').str.count('N')
    bioscan['quality_score'] = bioscan['seq_length'] - (bioscan['n_ambiguous'] * 10)
    
    # Select best sequence per BIN
    representatives = bioscan.sort_values(
        'quality_score', ascending=False
    ).groupby('bold_bin_uri').first().reset_index()
    
    print(f"\nSelected {len(representatives)} representatives")
    
    # Load tree and extract BINs
    print(f"Loading tree: {tree_file}")
    with open(tree_file, 'r') as f:
        tree_content = f.read()
    
    # Extract BINs from tree (format: Species|BOLDABC1234|ProcessID)
    # Pattern matches BOLD followed by letters and numbers (no colon in tree)
    tree_bin_pattern = r'\|BOLD([A-Z]{3}\d{4})\|'
    tree_bins_raw = re.findall(tree_bin_pattern, tree_content)
    
    # Add BOLD: prefix to match BIOSCAN format
    tree_bins = set([f"BOLD:{bin_code}" for bin_code in tree_bins_raw])
    
    print(f"BINs extracted from tree: {len(tree_bins)}")
    print(f"Sample tree BINs: {list(tree_bins)[:5]}")
    
    # Check BIOSCAN BIN format
    print(f"Sample BIOSCAN BINs: {representatives['bold_bin_uri'].head().tolist()}")
    
    # Mark which representatives are in tree vs. not
    representatives['in_reference_tree'] = representatives['bold_bin_uri'].isin(tree_bins)
    representatives['placement_type'] = representatives['in_reference_tree'].map({
        True: 'validation',
        False: 'novel'
    })
    
    n_validation = (representatives['in_reference_tree'] == True).sum()
    n_novel = (representatives['in_reference_tree'] == False).sum()
    
    print(f"\nPlacement types:")
    print(f"  Validation (BIN in tree): {n_validation}")
    print(f"  Novel (BIN not in tree): {n_novel}")
    
    # Write FASTA
    print(f"\nWriting representatives to: {output_fasta}")
    with open(output_fasta, 'w') as f:
        for idx, row in representatives.iterrows():
            # Format: BIN|species|processID (remove colon for tree compatibility)
            bin_clean = row['bold_bin_uri'].replace('BOLD:', 'BOLD')
            species = row.get('bold_species', 'Unknown_species')
            if pd.isna(species) or species == '':
                species = 'Unknown_species'
            process_id = row['bold_processid']
            
            header = f">{species}|{bin_clean}|{process_id}"
            sequence = row['bold_nuc']
            
            f.write(f"{header}\n{sequence}\n")
    
    # Save representative info
    info_file = output_fasta.replace('.fasta', '_info.csv')
    representatives[['bold_bin_uri', 'bold_processid', 'bold_species', 
                     'seq_length', 'quality_score', 'in_reference_tree', 
                     'placement_type']].to_csv(info_file, index=False)
    print(f"Representative info saved to: {info_file}")
    
    print("\n✓ Representative selection complete!")

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python 06_select_bin_representatives.py <bioscan.csv> <tree.newick> <output.fasta>")
        sys.exit(1)
    
    select_representatives(sys.argv[1], sys.argv[2], sys.argv[3])
