#!/usr/bin/env python3
"""
Add DTOL specimens to Sciaridae phylogenetic tree.

Complete workflow:
1. Extract DTOL barcode sequences (FIRST sequence only from each file)
2. Clean sequences (uppercase, ATCGN only)
3. Align DTOL sequences separately
4. Place with EPA-ng
5. Create metadata
"""

import argparse
import pandas as pd
import os
import subprocess
from Bio import SeqIO

parser = argparse.ArgumentParser(description="Add DTOL specimens to Sciaridae phylogenetic tree")
parser.add_argument("--dtol-metadata", required=True, help="DTOL metadata Excel file (tolid_sciaridae_portal.xlsx)")
parser.add_argument("--barcodes-dir", required=True, help="Directory containing DTOL barcode FASTA files")
parser.add_argument("--ref-alignment", required=True, help="Reference alignment FASTA (Sciaridae_aligned_clean.fasta)")
parser.add_argument("--ref-tree", required=True, help="Reference tree file (Sciaridae.treefile)")
args = parser.parse_args()

print("=" * 70)
print("ADDING DTOL SPECIMENS TO SCIARIDAE TREE")
print("=" * 70)

# Paths
DTOL_METADATA = args.dtol_metadata
DTOL_BARCODES_DIR = args.barcodes_dir
REFERENCE_ALIGNMENT = args.ref_alignment
REFERENCE_TREE = args.ref_tree

# Output files
DTOL_FASTA_RAW = 'data/output/dtol_sciaridae_raw.fasta'
DTOL_FASTA_CLEAN = 'data/output/dtol_sciaridae_clean.fasta'
DTOL_ALIGNED = 'data/output/dtol_sciaridae_aligned.fasta'
DTOL_PLACEMENT = 'data/output/dtol_placement_results.jplace'

# ============================================================================
# STEP 1: Extract DTOL sequences (FIRST sequence only from each file)
# ============================================================================
print("\n1. Extracting DTOL sequences...")

dtol_meta = pd.read_excel(DTOL_METADATA)
print(f"   Found {len(dtol_meta)} DTOL specimens")

sequences_raw = []
for idx, row in dtol_meta.iterrows():
    tolid = row['ToLID']
    species = row['Scientific Name'].replace(' ', '_')
    
    # Find barcode file
    barcode_files = [f for f in os.listdir(DTOL_BARCODES_DIR) if tolid in f]
    
    if not barcode_files:
        print(f"   ⚠️  No barcode file for {species} ({tolid})")
        continue
    
    barcode_file = os.path.join(DTOL_BARCODES_DIR, barcode_files[0])
    
    # Read ONLY THE FIRST sequence using BioPython
    with open(barcode_file, 'r') as f:
        records = list(SeqIO.parse(f, 'fasta'))
        if len(records) == 0:
            print(f"   ⚠️  No sequences in {barcode_files[0]}")
            continue
        
        # Take only the first sequence
        first_seq = str(records[0].seq)
        
        if len(records) > 1:
            print(f"   ⚠️  {species} ({tolid}): Multiple sequences in file, using first only")
    
    # Create new header: Species|TOLID
    new_header = f">{species}|{tolid}"
    sequences_raw.append((new_header, first_seq))
    print(f"   ✓ {species} ({tolid}): {len(first_seq)} bp")

# Write raw FASTA
with open(DTOL_FASTA_RAW, 'w') as f:
    for header, seq in sequences_raw:
        f.write(f"{header}\n{seq}\n")

print(f"   ✓ Saved {len(sequences_raw)} raw sequences to: {DTOL_FASTA_RAW}")

# ============================================================================
# STEP 2: Clean sequences (uppercase, ATCGN only)
# ============================================================================
print("\n2. Cleaning sequences...")

with open(DTOL_FASTA_RAW, 'r') as f_in, open(DTOL_FASTA_CLEAN, 'w') as f_out:
    for record in SeqIO.parse(f_in, 'fasta'):
        # Convert to uppercase and replace any non-ATCGN with N
        clean_seq = str(record.seq).upper()
        clean_seq = ''.join([c if c in 'ATCGN' else 'N' for c in clean_seq])
        f_out.write(f">{record.id}\n{clean_seq}\n")

print(f"   ✓ Cleaned sequences saved to: {DTOL_FASTA_CLEAN}")

# ============================================================================
# STEP 3: Align DTOL sequences
# ============================================================================
print("\n3. Aligning DTOL sequences...")

# First: align to reference using --addfragments
temp_combined = 'data/output/dtol_combined_temp.fasta'

cmd = [
    'mafft',
    '--addfragments', DTOL_FASTA_CLEAN,
    '--thread', '4',
    REFERENCE_ALIGNMENT
]

print(f"   Running MAFFT --addfragments...")
with open(temp_combined, 'w') as outf:
    result = subprocess.run(cmd, stdout=outf, stderr=subprocess.PIPE, text=True)

if result.returncode != 0:
    print(f"   ✗ Alignment failed: {result.stderr}")
    exit(1)

# Extract only DTOL sequences from combined alignment
dtol_ids = ['idBraNiti1', 'idCorForc1', 'idCorForc3', 'idPhyFlap3', 'idSchCarb1', 'idSciHeme3']
with open(DTOL_ALIGNED, 'w') as out:
    for record in SeqIO.parse(temp_combined, 'fasta'):
        if any(tolid in record.id for tolid in dtol_ids):
            SeqIO.write(record, out, 'fasta')

result = type('obj', (object,), {'returncode': 0})()  # Fake success result

if result.returncode == 0:
    print(f"   ✓ Alignment complete: {DTOL_ALIGNED}")
else:
    print(f"   ✗ Alignment failed: {result.stderr}")
    exit(1)

# ============================================================================
# STEP 4: Place with EPA-ng
# ============================================================================
print("\n4. Placing DTOL sequences with EPA-ng...")

# Create EPA-ng output directory
os.makedirs('epa_dtol', exist_ok=True)

cmd = [
    'epa-ng',
    '--ref-msa', REFERENCE_ALIGNMENT,
    '--tree', REFERENCE_TREE,
    '--query', DTOL_ALIGNED,
    '--outdir', 'epa_dtol',
    '--model', 'GTR+G',
    '--redo'
]

print(f"   Running EPA-ng...")
result = subprocess.run(cmd, capture_output=True, text=True)

if result.returncode == 0:
    print(f"   ✓ Placement complete")
    subprocess.run(['cp', 'epa_dtol/epa_result.jplace', DTOL_PLACEMENT])
    
    # Parse placement results
    print("\n   Placement summary:")
    import json
    with open(DTOL_PLACEMENT, 'r') as f:
        jplace = json.load(f)
        for placement in jplace['placements']:
            name = placement['n'][0]
            lwr = placement['p'][0][2]  # likelihood weight ratio
            quality = "High" if lwr >= 0.75 else "Medium" if lwr >= 0.5 else "Low"
            print(f"     {name}: LWR = {lwr:.4f} ({quality})")
else:
    print(f"   ✗ Placement failed:")
    print(result.stderr)
    exit(1)

# ============================================================================
# STEP 5: Create DTOL metadata
# ============================================================================
print("\n5. Creating DTOL metadata...")

dtol_metadata_rows = []
for idx, row in dtol_meta.iterrows():
    tolid = row['ToLID']
    species = row['Scientific Name'].replace(' ', '_')
    
    dtol_metadata_rows.append({
        'name': f"{species}|{tolid}",
        'tolid': tolid,
        'species': row['Scientific Name'],
        'assembly_status': row['Assembly Status'],
        'genome_status': row['Genome Status'],
        'placement_type': 'dtol',
        'geography': 'United Kingdom',
        'in_uksi': True,
        'dataset': 'DTOL'
    })

dtol_metadata = pd.DataFrame(dtol_metadata_rows)
dtol_metadata.to_csv('data/output/dtol_metadata.tsv', sep='\t', index=False)

print(f"   ✓ Created metadata for {len(dtol_metadata)} DTOL specimens")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"\n✓ Processed {len(sequences_raw)} DTOL specimens")

print(f"\nDTOL specimens:")
for idx, row in dtol_meta.iterrows():
    print(f"  - {row['Scientific Name']} ({row['ToLID']})")

print(f"\nFiles created:")
print(f"  1. Raw sequences: {DTOL_FASTA_RAW}")
print(f"  2. Clean sequences: {DTOL_FASTA_CLEAN}")
print(f"  3. Aligned sequences: {DTOL_ALIGNED}")
print(f"  4. EPA-ng placements: {DTOL_PLACEMENT}")
print(f"  5. Metadata: data/output/dtol_metadata.tsv")

print(f"\n✓ DTOL sequences ready for tree integration")
print("\n" + "=" * 70 + "\n")
