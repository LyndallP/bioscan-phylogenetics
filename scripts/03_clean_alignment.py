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

# Write using record.id (the first whitespace-delimited token from the FASTA
# header) rather than record.description (the full header line).
#
# The reference alignment has extra annotation after the sequence ID:
#   >Bradysia_pratincola|BOLDACP1705|NORSC1832-17 Ingroup|Bradysia ...|Sciaridae
#
# IQ-TREE uses only the first whitespace-delimited token as the Newick tip
# label. EPA-ng must match tree tips against MSA IDs exactly, so we must also
# write only the first token — record.id — stripping the annotation.
#
# We also normalise BOLD: → BOLD because IQ-TREE strips the colon (it is a
# Newick branch-length separator) from tip labels.
n_bold_fixed = 0
with open(output_file, 'w') as out:
    for record in cleaned:
        seq_id = record.id
        normalised = seq_id.replace('BOLD:', 'BOLD')
        if normalised != seq_id:
            n_bold_fixed += 1
        out.write(f'>{normalised}\n{str(record.seq)}\n')

if n_bold_fixed:
    print(f"Normalised BOLD: → BOLD in {n_bold_fixed} sequence header(s)")
else:
    print("BOLD ID format: already normalised (no BOLD: found)")
print(f"\nOutput: {len(cleaned)} sequences → {output_file}")
