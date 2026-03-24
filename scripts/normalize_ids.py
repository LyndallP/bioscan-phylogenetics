#!/usr/bin/env python3
"""
Normalize BOLD BIN identifiers in FASTA files and Newick trees.

Removes the colon from BOLD BIN format so that
    Species|BOLD:ACP1705|ProcessID
becomes
    Species|BOLDACP1705|ProcessID

This makes tip labels consistent between IQ-TREE output (which drops the
colon) and FASTA files (which retain it), allowing EPA-ng to match them.

Usage:
  python normalize_ids.py <input_file> <output_file>

Works on both FASTA (.fasta / .fa) and Newick tree files (.treefile / .nwk).
"""

import re
import sys

COLON_BOLD = re.compile(r'BOLD:([A-Z0-9]+)')


def normalize(text: str) -> str:
    return COLON_BOLD.sub(r'BOLD\1', text)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f'Usage: {sys.argv[0]} <input_file> <output_file>')
        sys.exit(1)

    in_path, out_path = sys.argv[1], sys.argv[2]

    with open(in_path) as fh:
        content = fh.read()

    normalized = normalize(content)
    changed = content.count('BOLD:') - normalized.count('BOLD:')

    with open(out_path, 'w') as fh:
        fh.write(normalized)

    print(f'Normalized {changed} BOLD: occurrences -> {out_path}')
