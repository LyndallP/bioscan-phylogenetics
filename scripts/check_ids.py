#!/usr/bin/env python3
"""
Diagnose ID mismatches between a reference tree and reference MSA.

Reads all tip labels from a Newick tree (using ete3) and all sequence IDs
from a FASTA, then reports which IDs are missing from each side, and prints
a sample from each file so you can see the actual format in use.

Usage:
  python scripts/check_ids.py <tree_file> <fasta_file>

Example:
  python scripts/check_ids.py \
      families/Sciaridae/input/Sciaridae_no_outgroup.treefile \
      families/Sciaridae/input/Sciaridae_aligned_clean.fasta
"""
import sys
from ete3 import Tree


def extract_tree_tips(tree_file):
    """Return set of leaf names from a Newick tree using ete3."""
    tree = Tree(tree_file, format=1)
    return {leaf.name for leaf in tree}

def extract_fasta_ids(fasta_file):
    ids = set()
    headers_with_spaces = []
    with open(fasta_file) as f:
        for line in f:
            if line.startswith('>'):
                full_header = line[1:].strip()
                # EPA-ng (like most tools) uses only the first whitespace-delimited
                # token as the sequence ID — match that behaviour here.
                seq_id = full_header.split()[0]
                if seq_id != full_header:
                    headers_with_spaces.append(full_header)
                ids.add(seq_id)
    if headers_with_spaces:
        print(f"WARNING: {len(headers_with_spaces)} FASTA headers contain spaces — "
              f"EPA-ng will truncate the ID at the first space")
        print(f"  Example: {repr(headers_with_spaces[0])}")
        print(f"  EPA-ng ID would be: {repr(headers_with_spaces[0].split()[0])}")
        print()
    return ids

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f'Usage: {sys.argv[0]} <tree_file> <fasta_file>')
        sys.exit(1)

    tree_file, fasta_file = sys.argv[1], sys.argv[2]

    print(f'Tree:  {tree_file}')
    print(f'FASTA: {fasta_file}')
    print()

    tree_tips = extract_tree_tips(tree_file)
    fasta_ids = extract_fasta_ids(fasta_file)

    print(f'Tree tips:     {len(tree_tips)}')
    print(f'FASTA entries: {len(fasta_ids)}')
    print()

    # Sample IDs from each to reveal actual format
    sample_tree = sorted(tree_tips)[:5]
    sample_fasta = sorted(fasta_ids)[:5]
    print('Sample tree tips:')
    for t in sample_tree:
        print(f'  {repr(t)}')
    print('Sample FASTA IDs:')
    for f in sample_fasta:
        print(f'  {repr(f)}')
    print()

    # Check for BOLD: (with colon) in either file
    tree_with_colon  = [t for t in tree_tips  if 'BOLD:' in t]
    fasta_with_colon = [f for f in fasta_ids if 'BOLD:' in f]
    if tree_with_colon:
        print(f'WARNING: {len(tree_with_colon)} tree tips still contain "BOLD:" — tree needs normalizing')
    if fasta_with_colon:
        print(f'WARNING: {len(fasta_with_colon)} FASTA IDs still contain "BOLD:" — MSA needs normalizing')
    if not tree_with_colon and not fasta_with_colon:
        print('BOLD: format: OK — no colons found in either file')
    print()

    # Find actual mismatches
    in_tree_not_fasta = tree_tips - fasta_ids
    in_fasta_not_tree = fasta_ids - tree_tips

    if not in_tree_not_fasta and not in_fasta_not_tree:
        print('RESULT: All IDs match — tree and MSA are compatible')
    else:
        if in_tree_not_fasta:
            print(f'Tree tips NOT in FASTA ({len(in_tree_not_fasta)} total):')
            for t in sorted(in_tree_not_fasta)[:10]:
                print(f'  {repr(t)}')
            if len(in_tree_not_fasta) > 10:
                print(f'  ... and {len(in_tree_not_fasta)-10} more')
        if in_fasta_not_tree:
            print(f'\nFASTA IDs NOT in tree ({len(in_fasta_not_tree)} total):')
            for f in sorted(in_fasta_not_tree)[:10]:
                print(f'  {repr(f)}')
            if len(in_fasta_not_tree) > 10:
                print(f'  ... and {len(in_fasta_not_tree)-10} more')
