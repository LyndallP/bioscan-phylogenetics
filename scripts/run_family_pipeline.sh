#!/usr/bin/env bash
# =============================================================================
# run_family_pipeline.sh — Full pipeline from raw inputs to Taxonium-ready TSV
#
# Runs all steps (0–15) for a given family. Skips DTOL (Step 4) and subfamily
# (Step 13, Sciaridae-only). Set configuration variables below before running.
#
# Usage:
#   bash scripts/run_family_pipeline.sh --family Empididae [--skip-goat]
#
# Run from repo root. All paths are relative to repo root.
# =============================================================================

set -euo pipefail

# =============================================================================
# CONFIGURATION — edit these paths before running
# =============================================================================
BIOSCAN_ALL_TSV="bioscan_all.tsv"           # All-family BIOSCAN TSV (repo root)
GAP_ANALYSIS_CSV="filtered_gap_analysis.csv" # Full arthropod UKSI gap analysis

# BOLD API key for fetching country data (Step 9)
# export BOLD_API_KEY="your_key_here"
# =============================================================================

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------
FAMILY=""
SKIP_GOAT=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --family)   FAMILY="$2"; shift 2 ;;
        --skip-goat) SKIP_GOAT="--skip-goat"; shift ;;
        *) echo "Unknown argument: $1"; exit 1 ;;
    esac
done

if [[ -z "$FAMILY" ]]; then
    echo "ERROR: --family is required"
    echo "Usage: bash scripts/run_family_pipeline.sh --family Empididae [--skip-goat]"
    exit 1
fi

FAMILY_LOWER=$(echo "$FAMILY" | tr '[:upper:]' '[:lower:]')
FAM_DIR="families/${FAMILY}"
INPUT_DIR="${FAM_DIR}/input"
OUTPUT_DIR="${FAM_DIR}/output"
EPA_DIR="${FAM_DIR}/epa_output"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
LOG_FILE="${FAM_DIR}/${FAMILY_LOWER}_pipeline.log"

log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $*"
    echo "$msg"
    echo "$msg" >> "$LOG_FILE"
}

step() {
    echo ""
    echo "============================================================"
    log "STEP $*"
    echo "============================================================"
}

die() {
    log "ERROR: $*"
    exit 1
}

check_file() {
    [[ -f "$1" ]] || die "Required file not found: $1"
}

check_tool() {
    command -v "$1" &>/dev/null || die "Required tool not found: $1 (is it installed and on PATH?)"
}

# ---------------------------------------------------------------------------
# Pre-flight checks
# ---------------------------------------------------------------------------
step "0a — Pre-flight checks"

check_tool python3
check_tool mafft
check_tool epa-ng
check_tool gappa
check_tool Rscript

check_file "$BIOSCAN_ALL_TSV"
check_file "$GAP_ANALYSIS_CSV"

# Original reference files (may be at family root before input/ is created)
ORIG_TREEFILE="${FAM_DIR}/${FAMILY}.treefile"
ORIG_ALIGNED="${FAM_DIR}/${FAMILY}_aligned.fasta"

[[ -f "$ORIG_TREEFILE" || -f "${INPUT_DIR}/${FAMILY}.treefile" ]] || \
    die "Treefile not found at ${ORIG_TREEFILE} or ${INPUT_DIR}/${FAMILY}.treefile"
[[ -f "$ORIG_ALIGNED" || -f "${INPUT_DIR}/${FAMILY}_aligned.fasta" ]] || \
    die "Aligned FASTA not found at ${ORIG_ALIGNED} or ${INPUT_DIR}/${FAMILY}_aligned.fasta"

log "All pre-flight checks passed for family: ${FAMILY}"

# ---------------------------------------------------------------------------
# Create directory structure
# ---------------------------------------------------------------------------
step "0b — Creating directory structure"

mkdir -p "$INPUT_DIR" "$OUTPUT_DIR" "$EPA_DIR"
log "Directories: $INPUT_DIR  $OUTPUT_DIR  $EPA_DIR"

# Copy reference files into input/ if not already there
if [[ ! -f "${INPUT_DIR}/${FAMILY}.treefile" && -f "$ORIG_TREEFILE" ]]; then
    cp "$ORIG_TREEFILE" "${INPUT_DIR}/${FAMILY}.treefile"
    log "Copied ${FAMILY}.treefile → input/"
fi
if [[ ! -f "${INPUT_DIR}/${FAMILY}_aligned.fasta" && -f "$ORIG_ALIGNED" ]]; then
    cp "$ORIG_ALIGNED" "${INPUT_DIR}/${FAMILY}_aligned.fasta"
    log "Copied ${FAMILY}_aligned.fasta → input/"
fi

# ---------------------------------------------------------------------------
# Step 0 — Filter BIOSCAN data to family
# ---------------------------------------------------------------------------
step "0 — Filter BIOSCAN data to family"

BIOSCAN_CSV="${INPUT_DIR}/bioscan_${FAMILY_LOWER}.csv"

if [[ -f "$BIOSCAN_CSV" ]]; then
    log "Bioscan CSV already exists, skipping: $BIOSCAN_CSV"
else
    python3 scripts/filter_bioscan.py \
        "$BIOSCAN_ALL_TSV" \
        --family "$FAMILY" 2>&1 | tee -a "$LOG_FILE"
    check_file "$BIOSCAN_CSV"
    log "Bioscan CSV created: $BIOSCAN_CSV"
fi

# ---------------------------------------------------------------------------
# Step 1 — Prepare reference tree (remove outgroups)
# ---------------------------------------------------------------------------
step "1 — Prepare reference tree"

TREE_NO_OG="${INPUT_DIR}/${FAMILY}_no_outgroup.treefile"

python3 scripts/02_tree_preparation.py \
    "${INPUT_DIR}/${FAMILY}.treefile" \
    "$TREE_NO_OG" 2>&1 | tee -a "$LOG_FILE"

check_file "$TREE_NO_OG"
log "Reference tree prepared: $TREE_NO_OG"

# ---------------------------------------------------------------------------
# Step 2 — Clean reference alignment
# ---------------------------------------------------------------------------
step "2 — Clean reference alignment"

ALIGNED_CLEAN="${INPUT_DIR}/${FAMILY}_aligned_clean.fasta"

python3 scripts/03_clean_alignment.py \
    "${INPUT_DIR}/${FAMILY}_aligned.fasta" \
    "$ALIGNED_CLEAN" 2>&1 | tee -a "$LOG_FILE"

check_file "$ALIGNED_CLEAN"
log "Alignment cleaned: $ALIGNED_CLEAN"

# ---------------------------------------------------------------------------
# Step 3 — Select best BIOSCAN representative per BIN
# ---------------------------------------------------------------------------
step "3 — Select BIOSCAN representatives per BIN"

BIOSCAN_REPS="${INPUT_DIR}/bioscan_representatives.fasta"

python3 scripts/06_select_bin_representatives.py \
    "$BIOSCAN_CSV" \
    "$TREE_NO_OG" \
    "$BIOSCAN_REPS" 2>&1 | tee -a "$LOG_FILE"

check_file "$BIOSCAN_REPS"
log "Representatives selected: $BIOSCAN_REPS"

# ---------------------------------------------------------------------------
# Step 4 — (DTOL skipped — no DTOL sequences for this run)
# Use bioscan_representatives.fasta directly as query_sequences.fasta
# ---------------------------------------------------------------------------
step "4 — Preparing query sequences (no DTOL)"

QUERY_SEQS="${INPUT_DIR}/query_sequences.fasta"
cp "$BIOSCAN_REPS" "$QUERY_SEQS"
log "query_sequences.fasta = bioscan_representatives.fasta (no DTOL)"

# ---------------------------------------------------------------------------
# Step 4b — Align query sequences to reference alignment (MAFFT)
# ---------------------------------------------------------------------------
step "4b — Align query sequences with MAFFT --add --keeplength"

TEMP_COMBINED="${INPUT_DIR}/temp_combined_aligned.fasta"
QUERY_ALIGNED="${INPUT_DIR}/query_sequences_aligned.fasta"

mafft \
    --add "$QUERY_SEQS" \
    --keeplength \
    "$ALIGNED_CLEAN" \
    > "$TEMP_COMBINED" 2>&1 | tee -a "$LOG_FILE" || true

check_file "$TEMP_COMBINED"

# Extract only query sequences from combined output
FAM="$FAMILY" python3 -c "
import os, sys
from Bio import SeqIO

fam = os.environ['FAM']
query_file = f'families/{fam}/input/query_sequences.fasta'
combined_file = f'families/{fam}/input/temp_combined_aligned.fasta'
out_file = f'families/{fam}/input/query_sequences_aligned.fasta'

query_ids = {r.id for r in SeqIO.parse(query_file, 'fasta')}
count = 0
with open(out_file, 'w') as out:
    for r in SeqIO.parse(combined_file, 'fasta'):
        if r.id in query_ids:
            out.write(f'>{r.description}\n{str(r.seq)}\n')
            count += 1
print(f'Extracted {count} aligned query sequences')
" 2>&1 | tee -a "$LOG_FILE"

check_file "$QUERY_ALIGNED"
log "Query sequences aligned: $QUERY_ALIGNED"

# ---------------------------------------------------------------------------
# Step 5 — Place query sequences with EPA-ng
# (ID normalisation is handled by 03_clean_alignment.py and
#  06_select_bin_representatives.py — no separate step needed)
# ---------------------------------------------------------------------------
step "5 — EPA-ng placement"

epa-ng \
    --tree "$TREE_NO_OG" \
    --ref-msa "$ALIGNED_CLEAN" \
    --query "$QUERY_ALIGNED" \
    --outdir "$EPA_DIR" \
    --model GTR+G \
    --redo 2>&1 | tee -a "$LOG_FILE"

check_file "${EPA_DIR}/epa_result.jplace"
log "EPA-ng placement complete: ${EPA_DIR}/epa_result.jplace"

# ---------------------------------------------------------------------------
# Step 6 — Graft placements onto tree with gappa
# ---------------------------------------------------------------------------
step "6 — Graft placements with gappa"

gappa examine graft \
    --jplace-path "${EPA_DIR}/epa_result.jplace" \
    --allow-file-overwriting \
    --out-dir "$EPA_DIR" 2>&1 | tee -a "$LOG_FILE"

check_file "${EPA_DIR}/epa_result.newick"

FINAL_TREE="${OUTPUT_DIR}/${FAMILY}_final_tree.newick"
mv "${EPA_DIR}/epa_result.newick" "$FINAL_TREE"
log "Final tree: $FINAL_TREE"

# ---------------------------------------------------------------------------
# Step 7 — Create base metadata
# ---------------------------------------------------------------------------
step "7 — Create base metadata"

META_01="${OUTPUT_DIR}/metadata_01_base.tsv"

python3 scripts/create_fullplacement_metadata_FINAL.py \
    "$FINAL_TREE" \
    "${EPA_DIR}/epa_result.jplace" \
    "$META_01" 2>&1 | tee -a "$LOG_FILE"

check_file "$META_01"
log "Base metadata: $META_01"

# ---------------------------------------------------------------------------
# Step 8 — Add DTOL enrichment (dataset, tolid, assembly_status)
# ---------------------------------------------------------------------------
step "8 — Add DTOL enrichment metadata"

META_02="${OUTPUT_DIR}/metadata_02_enhanced.tsv"

python3 scripts/add_enhanced_metadata.py \
    "$META_01" \
    "$META_02" 2>&1 | tee -a "$LOG_FILE"

check_file "$META_02"
log "Enhanced metadata: $META_02"

# ---------------------------------------------------------------------------
# Step 9 — Fetch BOLD country data (R)
# ---------------------------------------------------------------------------
step "9 — Fetch BOLD country data"

BOLD_COUNTRIES="${OUTPUT_DIR}/bold_countries.tsv"

Rscript scripts/fetch_bold_countries.R \
    "$META_02" \
    "$BOLD_COUNTRIES" 2>&1 | tee -a "$LOG_FILE"

check_file "$BOLD_COUNTRIES"
log "BOLD countries: $BOLD_COUNTRIES"

# ---------------------------------------------------------------------------
# Step 10 — Filter UKSI gap analysis to family
# ---------------------------------------------------------------------------
step "10 — Filter UKSI gap analysis to family"

GAP_ANALYSIS_FAMILY="${INPUT_DIR}/${FAMILY_LOWER}_gap_analysis.csv"

python3 scripts/filter_uksi_by_family.py \
    "$GAP_ANALYSIS_CSV" \
    "$GAP_ANALYSIS_FAMILY" \
    --family "$FAMILY" 2>&1 | tee -a "$LOG_FILE"

check_file "$GAP_ANALYSIS_FAMILY"
log "Family gap analysis: $GAP_ANALYSIS_FAMILY"

# ---------------------------------------------------------------------------
# Step 11 — Integrate country data and UKSI membership
# ---------------------------------------------------------------------------
step "11 — Integrate country data and UKSI membership"

META_03="${OUTPUT_DIR}/metadata_03_country.tsv"

python3 scripts/integrate_country_metadata.py \
    --metadata "$META_02" \
    --bold-countries "$BOLD_COUNTRIES" \
    --uksi "$GAP_ANALYSIS_FAMILY" \
    --output "$META_03" 2>&1 | tee -a "$LOG_FILE"

check_file "$META_03"
log "Country-integrated metadata: $META_03"

# ---------------------------------------------------------------------------
# Step 11b — Add BAGS metadata from gap analysis
# ---------------------------------------------------------------------------
step "11b — Add BAGS metadata"

META_03B="${OUTPUT_DIR}/metadata_03b_bags.tsv"

python3 scripts/add_bags_metadata.py \
    "$META_03" \
    "$GAP_ANALYSIS_FAMILY" \
    "$META_03B" 2>&1 | tee -a "$LOG_FILE"

check_file "$META_03B"
log "BAGS metadata: $META_03B"

# ---------------------------------------------------------------------------
# Step 12 — Add BIOSCAN specimen IDs and thumbnails
# ---------------------------------------------------------------------------
step "12 — Add BIOSCAN specimen IDs and thumbnails"

META_04="${OUTPUT_DIR}/metadata_04_thumbnails.tsv"

python3 scripts/add_bioscan_specimen_ids_LOCAL.py \
    "$META_03B" \
    "$META_04" 2>&1 | tee -a "$LOG_FILE"

check_file "$META_04"
log "Thumbnail metadata: $META_04"

# ---------------------------------------------------------------------------
# Step 13 — Subfamily (Sciaridae only — skipped for ${FAMILY})
# ---------------------------------------------------------------------------
step "13 — Subfamily step (skipped — not applicable for ${FAMILY})"
META_PRELINKS="$META_04"
log "Step 13 skipped. Using $META_PRELINKS as input to Step 14."

# ---------------------------------------------------------------------------
# Step 14 — Add external links, geography_broad, GOAT, family
# ---------------------------------------------------------------------------
step "14 — Add external links and derived columns"

META_06="${OUTPUT_DIR}/metadata_06_links.tsv"

python3 scripts/add_external_links.py \
    "$META_PRELINKS" \
    "$META_06" \
    --family "$FAMILY" \
    ${SKIP_GOAT} 2>&1 | tee -a "$LOG_FILE"

check_file "$META_06"
log "Links metadata: $META_06"

# ---------------------------------------------------------------------------
# Step 15 — Finalize: node support, category, needs_attention
# ---------------------------------------------------------------------------
step "15 — Finalize metadata"

FINAL_META="${OUTPUT_DIR}/${FAMILY_LOWER}_metadata_FINAL.tsv"

python3 scripts/finalize_metadata.py \
    "$META_06" \
    "$FINAL_META" 2>&1 | tee -a "$LOG_FILE"

check_file "$FINAL_META"
log "Final metadata: $FINAL_META"

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
echo ""
echo "============================================================"
log "PIPELINE COMPLETE for ${FAMILY}"
echo "============================================================"
echo ""
echo "  Final tree:     $FINAL_TREE"
echo "  Final metadata: $FINAL_META"
echo "  Log:            $LOG_FILE"
echo ""
