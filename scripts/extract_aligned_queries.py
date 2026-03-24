#!/usr/bin/env python3
"""
Extract query sequences from a combined reference+query aligned FASTA.
Used after: mafft --add query.fasta --keeplength reference.fasta > combined.fasta

Identifies query sequences by matching the process ID (the 3rd |-delimited
field in the header), not the full header string. This is robust to BIN format
differences between files: the reference MSA uses BOLD:xxx (colon) while
write_fasta() outputs BOLDxxx (no colon), so full-header matching would
incorrectly include or exclude sequences. The process ID is format-independent
and unambiguously identifies whether a sequence belongs to the reference tree.

Usage:
  python extract_aligned_queries.py <combined_aligned.fasta> <original_query.fasta> <output.fasta>
"""
import sys
from Bio import SeqIO


def processid_from_description(description):
    """Return the process ID (3rd |-delimited field) from a FASTA header."""
    parts = description.split('|')
    return parts[-1] if len(parts) >= 3 else description


if len(sys.argv) != 4:
    print(f"Usage: {sys.argv[0]} <combined_aligned.fasta> <original_query.fasta> <output.fasta>")
    sys.exit(1)

combined_fasta  = sys.argv[1]
query_ids_fasta = sys.argv[2]
output_fasta    = sys.argv[3]

# Collect query process IDs from the original unaligned file.
# Using processid (not full description) makes the match format-independent:
# BOLD:xxx and BOLDxxx headers with the same processid are treated as the same.
query_processids = set()
for rec in SeqIO.parse(query_ids_fasta, 'fasta'):
    query_processids.add(processid_from_description(rec.description))

count = 0
with open(output_fasta, 'w') as out:
    for rec in SeqIO.parse(combined_fasta, 'fasta'):
        if processid_from_description(rec.description) in query_processids:
            out.write(f'>{rec.description}\n{str(rec.seq)}\n')
            count += 1

if count == 0:
    print("WARNING: no sequences extracted — check that headers match between files")
    sys.exit(1)

print(f"Extracted {count} aligned query sequences -> {output_fasta}")
