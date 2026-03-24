#!/usr/bin/env python3
"""
Remove outgroup sequences from a reference alignment FASTA.

The raw IQ-TREE alignment (e.g. Sciaridae_aligned.fasta) contains outgroup
sequences whose headers start with "OUTGROUP". This script strips them out to
produce the clean alignment used by EPA-ng and extract_dtol_coi.py.

Usage:
    python 03_clean_alignment.py <input_aligned.fasta> <output_clean.fasta>

Example:
    python scripts/03_clean_alignment.py Sciaridae_aligned.fasta Sciaridae_aligned_clean.fasta
"""

import sys
from Bio import SeqIO

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <input_aligned.fasta> <output_clean.fasta>")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

records = list(SeqIO.parse(input_file, 'fasta'))
print(f"Input: {len(records)} sequences")

ingroup = [r for r in records if not r.id.startswith("OUTGROUP")]
outgroup = [r for r in records if r.id.startswith("OUTGROUP")]

print(f"Outgroup sequences removed: {len(outgroup)}")
for r in outgroup:
    print(f"  {r.id}")

SeqIO.write(ingroup, output_file, 'fasta')
print(f"Output: {len(ingroup)} sequences → {output_file}")
