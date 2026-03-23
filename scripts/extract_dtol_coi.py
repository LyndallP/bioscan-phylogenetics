#!/usr/bin/env python3
"""
Extract COI barcodes from DTOL genome assemblies.
This script:
1. Handles FASTA files with multiple COI sequences of varying lengths
2. Selects the sequence with the highest read count (from 'seqs=' in header)
3. Checks orientation against reference sequences
4. Reverse complements if needed
5. Outputs correctly oriented, single-best-sequence FASTA
Usage:
    python extract_dtol_coi.py --dtol-dir /path/to/dtol/barcodes \
                               --reference /path/to/reference_alignment.fasta \
                               --species-list species_tolid_mapping.tsv \
                               --output dtol_coi_sequences.fasta
"""
import argparse
from Bio import SeqIO
from Bio.Seq import Seq
import os
import re
import sys


def load_reference_sequences(ref_file):
    """Load reference sequences for orientation checking.

    Returns dict: {genus_species: first_100bp_uppercase}
    """
    ref_seqs = {}
    for rec in SeqIO.parse(ref_file, 'fasta'):
        genus_species = '_'.join(rec.id.split('|')[0].split('_')[:2])
        if genus_species not in ref_seqs:
            # Get first 100bp, remove gaps, uppercase
            ref_seqs[genus_species] = str(rec.seq).replace('-', '')[:100].upper()
    return ref_seqs


def select_best_sequence(records):
    """Select sequence with highest read count from multiple sequences.

    Parses 'seqs=N' from FASTA description to find most abundant.
    Returns (best_record, read_count)
    """
    best_rec = None
    best_count = 0

    for rec in records:
        # Extract read count from description (e.g., 'seqs=4463')
        match = re.search(r'seqs=(\d+)', rec.description)
        count = int(match.group(1)) if match else 0

        if count > best_count:
            best_count = count
            best_rec = rec

    return best_rec, best_count


def check_orientation(seq, ref_seq):
    """Check if sequence needs reverse complementing.

    Compares first 50bp to reference.
    Returns: (corrected_sequence, orientation_status)
    """
    seq_forward = str(seq).upper()
    seq_revcomp = str(Seq(seq_forward).reverse_complement())

    # Score matches in first 50bp
    compare_len = min(50, len(seq_forward), len(ref_seq))
    fwd_match = sum(1 for i in range(compare_len)
                    if i < len(ref_seq) and seq_forward[i] == ref_seq[i])
    rev_match = sum(1 for i in range(compare_len)
                    if i < len(ref_seq) and seq_revcomp[i] == ref_seq[i])

    if rev_match > fwd_match:
        return seq_revcomp, "REVERSE_COMPLEMENT"
    else:
        return seq_forward, "FORWARD"


def main():
    parser = argparse.ArgumentParser(
        description='Extract and orient COI sequences from DTOL assemblies'
    )
    parser.add_argument('--dtol-dir', required=True,
                        help='Directory containing DTOL barcode FASTA files')
    parser.add_argument('--reference', required=True,
                        help='Reference alignment FASTA for orientation checking')
    parser.add_argument('--species-list', required=True,
                        help='TSV mapping ToLID to species (columns: tolid, species)')
    parser.add_argument('--output', required=True,
                        help='Output FASTA file for corrected sequences')
    parser.add_argument('--family', default=None,
                        help='Family name to filter files (optional)')

    args = parser.parse_args()

    print("=" * 80)
    print("DTOL COI EXTRACTION AND ORIENTATION")
    print("=" * 80)

    # Load reference sequences
    print(f"\nLoading reference sequences from: {args.reference}")
    ref_seqs = load_reference_sequences(args.reference)
    print(f"  ✓ Loaded {len(ref_seqs)} reference species")

    # Load species mapping
    print(f"\nLoading species mapping from: {args.species_list}")
    import pandas as pd
    species_map = pd.read_csv(args.species_list, sep='\t')
    tolid_to_species = dict(zip(species_map['tolid'], species_map['species']))
    print(f"  ✓ Loaded {len(tolid_to_species)} specimens")

    # Process each DTOL specimen
    print(f"\nProcessing DTOL files from: {args.dtol_dir}\n")

    output_sequences = []
    processed_count = 0
    skipped_count = 0

    for tolid, species_name in tolid_to_species.items():
        genus_species = species_name.replace(' ', '_')

        # Find file for this ToLID
        matching_files = [f for f in os.listdir(args.dtol_dir)
                          if tolid in f and f.endswith('.fa')]

        if not matching_files:
            print(f"⚠️  {species_name} ({tolid}): No file found")
            skipped_count += 1
            continue

        filename = matching_files[0]
        filepath = os.path.join(args.dtol_dir, filename)

        print(f"{species_name} ({tolid}):")

        # Load all sequences from file
        records = list(SeqIO.parse(filepath, 'fasta'))
        print(f"  Found {len(records)} sequences in file")

        # Select best sequence by read count
        best_rec, read_count = select_best_sequence(records)

        if best_rec is None:
            print(f"  ⚠️  No valid sequences (all had 0 reads)")
            skipped_count += 1
            continue

        print(f"  Selected sequence with {read_count} reads")
        print(f"  Length: {len(best_rec.seq)} bp")

        # Check and correct orientation
        if genus_species in ref_seqs:
            corrected_seq, orientation = check_orientation(
                best_rec.seq, ref_seqs[genus_species]
            )
            if orientation == "REVERSE_COMPLEMENT":
                print(f"  ⚠️  Reverse complemented")
            else:
                print(f"  ✓  Orientation correct")
        else:
            print(f"  ?  No reference found - using forward orientation")
            corrected_seq = str(best_rec.seq).upper()
            orientation = "NO_REFERENCE"

        # Create output record with standardized header
        # Format: Species_name|DTOL|ToLID
        output_rec = SeqIO.SeqRecord(
            Seq(corrected_seq),
            id=f"{genus_species}|DTOL|{tolid}",
            description=f"reads={read_count} orientation={orientation}"
        )
        output_sequences.append(output_rec)
        processed_count += 1
        print()

    # Write output
    print("=" * 80)
    SeqIO.write(output_sequences, args.output, 'fasta')
    print(f"✓ Wrote {len(output_sequences)} sequences to: {args.output}")
    print(f"  Processed: {processed_count}")
    print(f"  Skipped: {skipped_count}")
    print("=" * 80)


if __name__ == '__main__':
    main()
