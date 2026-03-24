#!/usr/bin/env python3
"""
Clean a reference alignment FASTA for use with EPA-ng and MAFFT.

Does two things in one pass:
  1. Removes outgroup sequences (headers starting with "OUTGROUP")
  2. Uppercases all sequences and replaces non-ATCGN characters with N
     (MAFFT rejects lowercase letters and ambiguity codes such as 'e')

The raw alignment provided with the reference tree (e.g. Sciaridae_aligned.fasta)
may contain outgroup sequences and/or lowercase/ambiguous characters.
This script produces the clean version (e.g. Sciaridae_aligned_clean.fasta)
required by EPA-ng and extract_dtol_coi.py.

Usage:
    python scripts/03_clean_alignment.py <input_aligned.fasta> <output_clean.fasta>

Example:
    python scripts/03_clean_alignment.py Sciaridae_aligned.fasta Sciaridae_aligned_clean.fasta
"""

import sys
from Bio import SeqIO
from Bio.Seq import Seq

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <input_aligned.fasta> <output_clean.fasta>")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

records = list(SeqIO.parse(input_file, 'fasta'))
print(f"Input: {len(records)} sequences from {input_file}")

outgroup = [r for r in records if r.id.startswith("OUTGROUP")]
ingroup  = [r for r in records if not r.id.startswith("OUTGROUP")]

if outgroup:
    print(f"Removed {len(outgroup)} outgroup sequence(s):")
    for r in outgroup:
        print(f"  {r.id}")

# Uppercase and replace non-ATCGN characters with N
cleaned = []
n_replaced_total = 0
for record in ingroup:
    raw = str(record.seq).upper()
    clean_seq = ''.join(c if c in 'ATCGN-' else 'N' for c in raw)
    n_replaced = sum(1 for a, b in zip(raw, clean_seq) if a != b)
    if n_replaced:
        n_replaced_total += n_replaced
        print(f"  {record.id}: replaced {n_replaced} non-ATCGN character(s) with N")
    record.seq = Seq(clean_seq)
    cleaned.append(record)

if n_replaced_total == 0:
    print("No non-ATCGN characters found.")

SeqIO.write(cleaned, output_file, 'fasta')
print(f"\nOutput: {len(cleaned)} sequences → {output_file}")
