#!/usr/bin/env bash
# =============================================================================
# run_diptera_batch.sh — Run pipeline for all Diptera families and push results
#
# For each family:
#   1. Runs run_family_pipeline.sh
#   2. Copies outputs to data/{Family}/
#   3. Commits and pushes to main
#   4. Switches back to feature branch
#
# Preserves local API key in run_family_pipeline.sh throughout via skip-worktree.
#
# Usage:
#   bash scripts/run_diptera_batch.sh
#
# Run from repo root. Requires git and all pipeline dependencies.
# Families with missing input files are skipped (logged to batch_skipped.log).
# =============================================================================

set -uo pipefail   # Note: no -e so one family failure doesn't abort the batch

REPO_ROOT="$(pwd)"
FEATURE_BRANCH="claude/audit-bioscan-scripts-9Nd2A"
MAIN_BRANCH="main"
SKIP_LOG="${REPO_ROOT}/batch_skipped.log"
DONE_LOG="${REPO_ROOT}/batch_done.log"

FAMILIES=(
    Acartophthalmidae
    Agromyzidae
    Anisopodidae
    Anthomyiidae
    Anthomyzidae
    Asilidae
    Asteiidae
    Atelestidae
    Bibionidae
    Bolitophilidae
    Bombyliidae
    Brachystomatidae
    Calliphoridae
    Camillidae
    Carnidae
    Ceratopogonidae
    Chamaemyiidae
    Chaoboridae
    Chloropidae
    Chyromyidae
    Clusiidae
    Conopidae
    Cryptochetidae
    Culicidae
    Cylindrotomidae
    Diadocidiidae
    Diastatidae
    Ditomyiidae
    Dixidae
    Dolichopodidae
    Drosophilidae
    Dryomyzidae
    Ephydridae
    Fanniidae
    Heleomyzidae
    Hippoboscidae
    Hybotidae
    Keroplatidae
    Lauxaniidae
    Limoniidae
    Lonchaeidae
    Lonchopteridae
    Micropezidae
    Milichiidae
    Muscidae
    Mycetophilidae
    Odiniidae
    Oestridae
    Opetiidae
    Opomyzidae
    Pallopteridae
    Pediciidae
    Periscelididae
    Phoridae
    Piophilidae
    Pipunculidae
    Platypezidae
    Platystomatidae
    Polleniidae
    Psilidae
    Psychodidae
    Ptychopteridae
    Rhagionidae
    Sarcophagidae
    Scathophagidae
    Scatopsidae
    Scenopinidae
    Sciomyzidae
    Sepsidae
    Simuliidae
    Sphaeroceridae
    Stratiomyidae
    Syrphidae
    Tabanidae
    Tachinidae
    Tephritidae
    Thaumaleidae
    Therevidae
    Tipulidae
    Trichoceridae
    Ulidiidae
    Xylomyidae
    Xylophagidae
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
log()  { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }
skip() { echo "[SKIP] $*" | tee -a "$SKIP_LOG"; }
done_fam() { echo "[DONE] $*" | tee -a "$DONE_LOG"; }

# ---------------------------------------------------------------------------
# Pre-flight: ensure we are on the feature branch and skip-worktree is set
# ---------------------------------------------------------------------------
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [[ "$CURRENT_BRANCH" != "$FEATURE_BRANCH" ]]; then
    echo "ERROR: must be on branch $FEATURE_BRANCH (currently on $CURRENT_BRANCH)"
    exit 1
fi

# Protect API key in run_family_pipeline.sh
git update-index --skip-worktree scripts/run_family_pipeline.sh 2>/dev/null || true

# Pull latest feature branch (stashing pipeline script first)
log "Pulling latest from $FEATURE_BRANCH..."
git update-index --no-skip-worktree scripts/run_family_pipeline.sh
git stash push -m "batch-api-key-stash" -- scripts/run_family_pipeline.sh 2>/dev/null || true
git pull origin "$FEATURE_BRANCH" || { echo "ERROR: git pull failed"; exit 1; }
git stash pop 2>/dev/null || true
git update-index --skip-worktree scripts/run_family_pipeline.sh

# Pull latest main
log "Pulling latest from $MAIN_BRANCH..."
git fetch origin "$MAIN_BRANCH"

> "$SKIP_LOG"
> "$DONE_LOG"

# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------
for FAMILY in "${FAMILIES[@]}"; do
    FAMILY_LOWER=$(echo "$FAMILY" | tr '[:upper:]' '[:lower:]')
    FAM_DIR="families/${FAMILY}"
    OUTPUT_DIR="${FAM_DIR}/output"
    FINAL_TREE="${OUTPUT_DIR}/${FAMILY}_final_tree.newick"
    FINAL_META="${OUTPUT_DIR}/${FAMILY_LOWER}_metadata_FINAL.tsv"
    DATA_DIR="data/${FAMILY}"

    echo ""
    echo "============================================================"
    log "Processing: $FAMILY"
    echo "============================================================"

    # Check input files exist
    TREEFILE=$(ls "${FAM_DIR}/${FAMILY}.treefile" "${FAM_DIR}/${FAMILY}.newick" 2>/dev/null | head -1)
    FASTA=$(ls "${FAM_DIR}/${FAMILY}_aligned.fasta" "${FAM_DIR}/${FAMILY}.fasta" 2>/dev/null | head -1)

    if [[ -z "$TREEFILE" ]]; then
        skip "$FAMILY — no treefile found in $FAM_DIR"
        continue
    fi
    if [[ -z "$FASTA" ]]; then
        skip "$FAMILY — no aligned fasta found in $FAM_DIR"
        continue
    fi

    # Skip if already uploaded to data/
    if [[ -f "${DATA_DIR}/${FAMILY_LOWER}_metadata_FINAL.tsv" ]]; then
        log "$FAMILY already in data/ — skipping pipeline, re-checking push..."
    else
        # Run pipeline
        log "Running pipeline for $FAMILY..."
        if ! bash scripts/run_family_pipeline.sh --family "$FAMILY"; then
            skip "$FAMILY — pipeline FAILED (see families/${FAMILY}/output/)"
            continue
        fi

        # Check outputs were produced
        if [[ ! -f "$FINAL_TREE" ]]; then
            skip "$FAMILY — pipeline finished but $FINAL_TREE not found"
            continue
        fi
        if [[ ! -f "$FINAL_META" ]]; then
            skip "$FAMILY — pipeline finished but $FINAL_META not found"
            continue
        fi

        # Copy to data/
        mkdir -p "$DATA_DIR"
        cp "$FINAL_TREE" "$DATA_DIR/"
        cp "$FINAL_META" "$DATA_DIR/"
        log "Copied outputs to $DATA_DIR/"
    fi

    # Commit and push to main
    log "Committing $FAMILY to $MAIN_BRANCH..."

    # Stash API key, switch to main
    git update-index --no-skip-worktree scripts/run_family_pipeline.sh
    git stash push -m "batch-api-key-stash" -- scripts/run_family_pipeline.sh 2>/dev/null || true

    git checkout "$MAIN_BRANCH"
    git pull --rebase origin "$MAIN_BRANCH"

    git add "$DATA_DIR/"
    if git diff --cached --quiet; then
        log "$FAMILY — nothing new to commit on $MAIN_BRANCH"
    else
        git commit -m "Add ${FAMILY} tree and metadata"
        git push origin "$MAIN_BRANCH"
        log "Pushed $FAMILY to $MAIN_BRANCH"
    fi

    # Switch back to feature branch, restore API key
    git checkout "$FEATURE_BRANCH"
    git stash pop 2>/dev/null || true
    git update-index --skip-worktree scripts/run_family_pipeline.sh

    done_fam "$FAMILY"

    # Brief pause to avoid hammering GitHub Actions
    sleep 5
done

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "============================================================"
log "BATCH COMPLETE"
echo "============================================================"
echo ""
echo "Completed families:"
cat "$DONE_LOG"
echo ""
echo "Skipped families:"
cat "$SKIP_LOG"
echo ""
echo "GitHub Actions will regenerate index.html for each push."
echo "Check: https://github.com/LyndallP/bioscan-phylogenetics/actions"
