#!/usr/bin/env python3
"""
Clean a reference alignment FASTA for use with EPA-ng and MAFFT.

Does three things in one pass:
  1. Removes outgroup sequences (headers starting with "OUTGROUP")
  2. Uppercases all sequences and replaces non-ATCGN characters with N
     (MAFFT rejects lowercase letters and ambiguity codes such as 'e')
  3. Normalises BOLD BIN identifiers: BOLD:XXXXXX → BOLDXXXXXX
     IQ-TREE strips the colon from tip labels (: is a Newick branch-length
     separator), so the cleaned alignment must use the same colon-free format
     to match the tree for EPA-ng placement.

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

# Write manually to normalise headers so they match IQ-TREE Newick tip labels.
#
# IQ-TREE does two things to FASTA headers when writing Newick:
#   1. Replaces spaces with underscores (space is whitespace, which terminates
#      the sequence name in FASTA; IQ-TREE joins the full name with '_').
#   2. Drops colons from BOLD: identifiers (: is a Newick branch-length separator).
#
# EPA-ng requires tree tip labels to match MSA sequence IDs exactly, so we
# apply the same two transforms here.
n_bold_fixed = 0
n_space_fixed = 0
with open(output_file, 'w') as out:
    for record in cleaned:
        header = record.description
        normalised = header.replace('BOLD:', 'BOLD')
        if normalised != header:
            n_bold_fixed += 1
        normalised2 = normalised.replace(' ', '_')
        if normalised2 != normalised:
            n_space_fixed += 1
        out.write(f'>{normalised2}\n{str(record.seq)}\n')

if n_bold_fixed:
    print(f"Normalised BOLD: → BOLD in {n_bold_fixed} sequence header(s)")
else:
    print("BOLD ID format: already normalised (no BOLD: found)")
if n_space_fixed:
    print(f"Replaced spaces with underscores in {n_space_fixed} sequence header(s)")
print(f"\nOutput: {len(cleaned)} sequences → {output_file}")
