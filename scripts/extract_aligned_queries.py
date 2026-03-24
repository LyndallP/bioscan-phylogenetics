#!/usr/bin/env python3
"""
Extract query sequences from a combined reference+query aligned FASTA.
Used after: mafft --add query.fasta --keeplength reference.fasta > combined.fasta

Usage:
  python extract_aligned_queries.py <combined_aligned.fasta> <original_query.fasta> <output.fasta>
"""
import sys
from Bio import SeqIO

if len(sys.argv) != 4:
    print(f"Usage: {sys.argv[0]} <combined_aligned.fasta> <original_query.fasta> <output.fasta>")
    sys.exit(1)

combined_fasta  = sys.argv[1]
query_ids_fasta = sys.argv[2]
output_fasta    = sys.argv[3]

# Collect query sequence IDs from the original unaligned file
query_ids = set()
for rec in SeqIO.parse(query_ids_fasta, 'fasta'):
    query_ids.add(rec.description)

count = 0
with open(output_fasta, 'w') as out:
    for rec in SeqIO.parse(combined_fasta, 'fasta'):
        if rec.description in query_ids:
            out.write(f'>{rec.description}\n{str(rec.seq)}\n')
            count += 1

if count == 0:
    print("WARNING: no sequences extracted — check that headers match between files")
    sys.exit(1)

print(f"Extracted {count} aligned query sequences -> {output_fasta}")
