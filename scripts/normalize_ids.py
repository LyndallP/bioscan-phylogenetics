#!/usr/bin/env python3
"""
Normalize sequence IDs to match between tree and alignment.
Converts BOLD:XXXXXX to BOLDXXXXXX format.
"""
import sys
import re
def normalize_id(seq_id):
    """Remove colon from BOLD: format"""
    return seq_id.replace('BOLD:', 'BOLD')
if __name__ == "__main__":
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    changes = 0
    with open(input_file) as f, open(output_file, 'w') as out:
        for line in f:
            if line.startswith('>'):
                # Normalize FASTA header
                seq_id = line[1:].strip()
                normalized = normalize_id(seq_id)
                if normalized != seq_id:
                    changes += 1
                out.write(f'>{normalized}\n')
            elif line.strip().startswith('(') or '(' in line:
                # Normalize Newick tree
                normalized = normalize_id(line)
                if normalized != line:
                    changes += 1
                out.write(normalized)
            else:
                out.write(line)

    print(f"Normalized {input_file} -> {output_file}  ({changes} IDs changed)")
    if changes == 0:
        print("  WARNING: 0 changes made — file may already be normalized or have unexpected format")
