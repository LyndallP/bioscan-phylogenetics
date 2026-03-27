#!/usr/bin/env bash
# =============================================================================
# run_other_batch.sh — Run pipeline for all non-Diptera families and push results
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
#   bash scripts/run_other_batch.sh
#
# Run from repo root. Requires git and all pipeline dependencies.
# Families with missing input files are skipped (logged to other_batch_skipped.log).
# =============================================================================

set -uo pipefail   # Note: no -e so one family failure doesn't abort the batch

REPO_ROOT="$(pwd)"
FEATURE_BRANCH="claude/audit-bioscan-scripts-9Nd2A"
MAIN_BRANCH="main"
SKIP_LOG="${REPO_ROOT}/other_batch_skipped.log"
DONE_LOG="${REPO_ROOT}/other_batch_done.log"

FAMILIES=(
    Talitridae
    Arcitalitridae
    Gammaridae
    Theridiidae
    Tetragnathidae
    Philodromidae
    Linyphiidae
    Thomisidae
    Lycosidae
    Clubionidae
    Araneidae
    Dictynidae
    Anyphaenidae
    Salticidae
    Lathyidae
    Amaurobiidae
    Hahniidae
    Oonopidae
    Pisauridae
    Cheiracanthiidae
    Mimetidae
    Agelenidae
    Gnaphosidae
    Bovidae
    Balanidae
    Elminiidae
    Ectobiidae
    Acartiidae
    Scirtidae
    Cantharidae
    Coccinellidae
    Leiodidae
    Brentidae
    Staphylinidae
    Cerambycidae
    Chrysomelidae
    Elateridae
    Scraptiidae
    Melyridae
    Latridiidae
    Curculionidae
    Cryptophagidae
    Nitidulidae
    Ptinidae
    Oedemeridae
    Carabidae
    Throscidae
    Eucnemidae
    Lampyridae
    Scarabaeidae
    Dascillidae
    Phalacridae
    Phloiophilidae
    Byturidae
    Corylophidae
    Ciidae
    Biphyllidae
    Attelabidae
    Salpingidae
    Monotomidae
    Sphindidae
    Ptiliidae
    Cleridae
    Erotylidae
    Helophoridae
    Mordellidae
    Lymexylidae
    Kateretidae
    Melandryidae
    Endomychidae
    Hydraenidae
    Tenebrionidae
    Anthicidae
    Dytiscidae
    Silvanidae
    Dryopidae
    Mycetophagidae
    Dermestidae
    Hydrophilidae
    Buprestidae
    Anthribidae
    Zopheridae
    Heteroceridae
    Clambidae
    Cerylonidae
    Noteridae
    Gyrinidae
    Hydrochidae
    Pyrochroidae
    Forficulidae
    Spongiphoridae
    Tomoceridae
    Entomobryidae
    Orchesellidae
    Lepidocyrtidae
    Isotomidae
    Baetidae
    Heptageniidae
    Ephemerellidae
    Leptophlebiidae
    Caenidae
    Schendylidae
    Glomeridae
    Aphididae
    Cixiidae
    Cicadellidae
    Anthocoridae
    Miridae
    Aphalaridae
    Triozidae
    Cydnidae
    Aphrophoridae
    Delphacidae
    Microphysidae
    Aleyrodidae
    Nabidae
    Rhyparochromidae
    Acanthosomatidae
    Lygaeidae
    Pentatomidae
    Issidae
    Reduviidae
    Liviidae
    Psyllidae
    Berytidae
    Adelgidae
    Phylloxeridae
    Tingidae
    Pseudococcidae
    Diaspididae
    Saldidae
    Corixidae
    Rhopalidae
    Heterogastridae
    Coreidae
    Membracidae
    Blissidae
    Artheneidae
    Cercopidae
    Piesmatidae
    Coccoidea_incertae_sedis
    Scutelleridae
    Cymidae
    Micronectidae
    Pleidae
    Oxycarenidae
    Tenthredinidae
    Braconidae
    Diapriidae
    Ichneumonidae
    Platygastridae
    Aphelinidae
    Eulophidae
    Mymaridae
    Megaspilidae
    Figitidae
    Pteromalidae
    Proctotrupidae
    Scelionidae
    Encyrtidae
    Apidae
    Cynipidae
    Formicidae
    Crabronidae
    Bethylidae
    Dryinidae
    Andrenidae
    Pompilidae
    Bembicidae
    Torymidae
    Eurytomidae
    Vespidae
    Ceraphronidae
    Chalcidoidea_incertae_sedis
    Systasidae
    Pirenidae
    Heloridae
    Eupelmidae
    Pemphredonidae
    Halictidae
    Cleonymidae
    Myrmosidae
    Colletidae
    Eunotidae
    Xyelidae
    Ismaridae
    Ceidae
    Trichogrammatidae
    Perilampidae
    Embolemidae
    Mellinidae
    Cephidae
    Spalangiidae
    Tetracampidae
    Ormyridae
    Signiphoridae
    Tiphiidae
    Chrysididae
    Argidae
    Psenidae
    Diprionidae
    Heptamelidae
    Megachilidae
    Philanthidae
    Gasteruptiidae
    Megastigmidae
    Diplolepididae
    Philosciidae
    Porcellionidae
    Trichoniscidae
    Armadillidiidae
    Ixodidae
    Nemasomatidae
    Julidae
    Coleophoridae
    Nepticulidae
    Choreutidae
    Adelidae
    Blastobasidae
    Hepialidae
    Noctuidae
    Tortricidae
    Micropterigidae
    Argyresthiidae
    Crambidae
    Geometridae
    Elachistidae
    Gracillariidae
    Heliozelidae
    Depressariidae
    Gelechiidae
    Tischeriidae
    Momphidae
    Yponomeutidae
    Nymphalidae
    Pyralidae
    Ypsolophidae
    Plutellidae
    Glyphipterigidae
    Epermeniidae
    Oecophoridae
    Psychidae
    Autostichidae
    Cosmopterigidae
    Erebidae
    Pieridae
    Incurvariidae
    Drepanidae
    Schreckensteiniidae
    Lyonetiidae
    Tineidae
    Lycaenidae
    Eriocraniidae
    Opostegidae
    Pterophoridae
    Alucitidae
    Hesperiidae
    Bucculatricidae
    Lypusidae
    Batrachedridae
    Prodoxidae
    Praydidae
    Roeslerstammiidae
    Sesiidae
    Zygaenidae
    Nolidae
    Bedelliidae
    Cossidae
    Scythropiidae
    Notodontidae
    Mantidae
    Panorpidae
    Sialidae
    Parasitidae
    Laelapidae
    Melicharidae
    Phytoseiidae
    Ascidae
    Macrochelidae
    Halolaelapidae
    Blattisociidae
    Mysidae
    Coniopterygidae
    Hemerobiidae
    Chrysopidae
    Sisyridae
    Aeshnidae
    Coenagrionidae
    Sclerosomatidae
    Phalangiidae
    Nemastomatidae
    Acrididae
    Tettigoniidae
    Nemouridae
    Chloroperlidae
    Leuctridae
    Taeniopterygidae
    Perlodidae
    Hypogastruridae
    Neanuridae
    Onychiuridae
    Polydesmidae
    Polyxenidae
    Neobisiidae
    Chthoniidae
    Ectopsocidae
    Stenopsocidae
    Caeciliusidae
    Trichopsocidae
    Psocidae
    Trogiidae
    Paracaeciliidae
    Peripsocidae
    Amphipsocidae
    Liposcelididae
    Elipsocidae
    Lachesillidae
    Mesopsocidae
    Philotarsidae
    Raphidiidae
    Sphaerulariidae
    Euzetidae
    Crotoniidae
    Oribatellidae
    Damaeidae
    Achipteriidae
    Carabodidae
    Eremaeidae
    Acaridae
    Cepheusidae
    Chamobatidae
    Peloppiidae
    Hydrozetidae
    Phthiracaridae
    Nothridae
    Humerobatidae
    Ceratozetidae
    Liacaridae
    Elenchidae
    Halictophagidae
    Dicyrtomidae
    Bourletiellidae
    Katiannidae
    Sminthuridae
    Sminthurididae
    Thripidae
    Aeolothripidae
    Phlaeothripidae
    Melanthripidae
    Hydroptilidae
    Limnephilidae
    Leptoceridae
    Psychomyiidae
    Philopotamidae
    Goeridae
    Glossosomatidae
    Beraeidae
    Polycentropodidae
    Rhyacophilidae
    Apataniidae
    Brachycentridae
    Hydropsychidae
    Lepidostomatidae
    Sericostomatidae
    Phryganeidae
    Ecnomidae
    Molannidae
    Anystidae
    Bdellidae
    Microtrombidiidae
    Eupodidae
    Scutacaridae
    Calyptostomatidae
    Labidostommatidae
    Erythraeidae
    Sperchontidae
    Pionidae
    Hygrobatidae
    Unionicolidae
    Trombidiidae
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

# Fetch latest main (no feature branch pull — avoids rebase conflicts on index.html)
log "Fetching latest from $MAIN_BRANCH..."
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

    # Skip if already uploaded to data/ on remote main
    git fetch origin "$MAIN_BRANCH" --quiet 2>/dev/null || true
    if git cat-file -e "origin/${MAIN_BRANCH}:${DATA_DIR}/${FAMILY_LOWER}_metadata_FINAL.tsv" 2>/dev/null; then
        log "$FAMILY already in data/ on origin/main — skipping pipeline, re-checking push..."
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

    if ! git checkout "$MAIN_BRANCH" 2>/dev/null; then
        log "WARNING: could not checkout $MAIN_BRANCH for $FAMILY — restoring state"
        git stash pop 2>/dev/null || true
        git update-index --skip-worktree scripts/run_family_pipeline.sh
        skip "$FAMILY — failed to switch to $MAIN_BRANCH (data files safe in $DATA_DIR)"
        continue
    fi

    # Pull with rebase, auto-resolving index.html conflicts
    if ! git pull --rebase origin "$MAIN_BRANCH" 2>/dev/null; then
        while git status 2>/dev/null | grep -qE "rebase in progress|REBASE_HEAD"; do
            git checkout --ours index.html 2>/dev/null || true
            git add index.html 2>/dev/null || true
            git rebase --continue 2>/dev/null || git rebase --skip 2>/dev/null || break
        done
    fi

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
