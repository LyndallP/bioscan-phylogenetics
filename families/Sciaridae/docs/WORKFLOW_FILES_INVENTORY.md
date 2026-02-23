# Sciaridae Phylogeny - Complete File Inventory

## 📁 Directory Structure
```
Sciaridae/
├── data/
│   ├── reference/          # Ben's original reference data (CONSTANT)
│   ├── queries/            # Query sequences to be placed
│   ├── output/             # All outputs from analysis
│   └── config/             # Configuration files
├── scripts/                # Analysis scripts
├── epa_results/            # EPA-ng output
└── docs/                   # Documentation
```

---

## 🔵 CONSTANT INPUT FILES (Never Change)

### Reference Tree & Alignment (from Ben)
- **Location:** `/Users/lp20/Desktop/Taxonium/phylogenies/Sciaridae/`
- Files:
  - `Sciaridae_ingroup.treefile` (802 tips, bootstrap values)
  - `Sciaridae_aligned_clean.fasta` (805 sequences, 950bp alignment)
  - `sciaridae_taxonium_metadata.tsv` (Ben's original metadata with UKSI/BAGS)

### UK Species Inventory
- `uksi_sciaridae_full.tsv` - UKSI species list with BOLD data
- `uksi_sciaridae_processids.txt` - ProcessIDs in UKSI

---

## 🟢 VARIABLE INPUT FILES (Update When New Data Available)

### BIOSCAN UK Data
- **Source:** BIOSCAN UK project releases
- **Current:** `UKBOL_bioscan_selected.tsv` (365,280 specimens)
- **Update frequency:** As new batches released

### DTOL Genome Assemblies
- **Source:** Darwin Tree of Life releases
- **Current:** 6 Sciaridae genomes (Feb 2025)
- Files needed:
  - Assembly FASTAs from DTOL portal
  - Metadata (tolid, species, assembly_status)
- **Update frequency:** As new genomes published

---

## 🔧 ANALYSIS SCRIPTS (Modular Workflow)

### Step 1: Select BIOSCAN Representatives
**Script:** `scripts/06_select_bin_representatives.py`
**Purpose:** Choose 1 representative per BIN from BIOSCAN data
**Inputs:**
  - BIOSCAN data (TSV)
  - Reference tree (to exclude existing specimens)
**Outputs:**
  - `data/output/sciaridae_all_representatives.fasta`
  - `data/output/sciaridae_all_representatives_info.csv`
**Key features:**
  - Quality scoring (sequence length, BAGS grade)
  - Excludes ProcessIDs already in reference
  - BIN-level deduplication

### Step 2: Extract DTOL COI Barcodes
**Script:** `scripts/extract_dtol_coi.py` (TO BE CREATED)
**Purpose:** Extract COI from DTOL assemblies, check orientation
**Inputs:**
  - DTOL assembly FASTAs
  - Reference alignment (for orientation check)
**Outputs:**
  - `data/output/dtol_sciaridae_FIXED.fasta`
  - `data/output/dtol_metadata.tsv`
**Key features:**
  - Uses BLAST to find COI
  - Checks orientation vs reference
  - Records tolid, assembly status

### Step 3: Align Query Sequences
**Script:** `scripts/align_queries.sh`
**Purpose:** Align queries to reference alignment
**Command:**
```bash
# BIOSCAN
mafft --add data/queries/bioscan_representatives.fasta \
      --keeplength reference.fasta > bioscan_aligned.fasta

# DTOL  
mafft --add data/queries/dtol_sciaridae.fasta \
      --keeplength reference.fasta > dtol_aligned.fasta
```
**Outputs:**
  - `data/queries/bioscan_representatives_aligned.fasta`
  - `data/queries/dtol_sciaridae_aligned.fasta`

### Step 4: Combine and Run EPA-ng
**Script:** `scripts/run_epa_placement.sh`
**Purpose:** Phylogenetic placement of all queries
**Commands:**
```bash
# Combine queries
cat bioscan_aligned.fasta dtol_aligned.fasta > all_queries.fasta

# EPA-ng placement
epa-ng --ref-msa reference.fasta \
       --tree reference.tree \
       --query all_queries.fasta \
       --model GTR+G
```
**Outputs:**
  - `epa_results/epa_result.jplace`

### Step 5: Convert to Newick
**Script:** `scripts/convert_to_newick.sh`
**Purpose:** Convert jplace to Newick tree
**Command:**
```bash
gappa examine graft \
      --jplace-path epa_result.jplace \
      --out-dir output/
```
**Outputs:**
  - `data/output/sciaridae_placed.newick`

### Step 6: Add Polytomy for Missing Species
**Script:** `scripts/add_polytomy.py`
**Purpose:** Add species without barcodes
**Output:**
  - `data/output/sciaridae_FINAL_v2.newick`

### Step 7: Create Metadata
**Script:** `scripts/create_metadata_COMPLETE.py` (TO BE CREATED/UPDATED)
**Purpose:** Generate complete Taxonium metadata
**Inputs:**
  - Final tree
  - jplace file (for LWR scores)
  - BIOSCAN data
  - DTOL metadata
  - UKSI data
  - Ben's metadata (for BAGS/in_uksi)
  - BOLD API (for geography)
**Outputs:**
  - `data/output/sciaridae_metadata_UPLOAD.tsv`
**Key features:**
  - Extracts parent bootstrap from tree
  - Creates markdown clickable links
  - Merges all metadata sources
  - Generates genus/family from species

### Step 8: Create Config
**Script:** `scripts/create_taxonium_config.py`
**Purpose:** Generate Taxonium config JSON
**Output:**
  - `data/output/taxonium_config_FINAL.json`
**Features:**
  - Custom genus color mapping
  - Display field selection
  - Custom field names

---

## 📤 FINAL OUTPUT FILES (Upload to Taxonium)

### For Taxonium Upload
1. **Tree:** `data/output/sciaridae_tree.nwk.gz` (22 KB)
2. **Metadata:** `data/output/sciaridae_metadata_UPLOAD.tsv.gz` (131 KB)
3. **Config:** `data/output/taxonium_config_FINAL.json` (1.8 KB)

### Metadata Columns (29 total)
- name, strain, bin, species, genus, family
- category, geography, in_uksi
- placement_type, placement_quality, placement_interpretation
- epa_lwr_score, bags_grade
- bin_quality_issue, n_bins_for_species, all_bins
- bioscan_specimens, needs_attention
- parent_bootstrap
- tolid, assembly_status, genome_status, dataset
- processid
- GBIF, BOLD_BIN, BOLD_Specimen, NBN, BLAST, DTOL (markdown links)

---

## 🔄 MODULAR UPDATE WORKFLOW

### When BIOSCAN Data Updates
```bash
# 1. Get new BIOSCAN data
# 2. Re-run representative selection
python scripts/06_select_bin_representatives.py

# 3. Align new representatives
mafft --add new_reps.fasta --keeplength reference.fasta > aligned.fasta

# 4. Combine with DTOL queries (unchanged)
cat bioscan_aligned.fasta dtol_aligned.fasta > all_queries.fasta

# 5. Re-run EPA-ng
epa-ng --ref-msa reference.fasta --tree reference.tree --query all_queries.fasta

# 6. Regenerate metadata
python scripts/create_metadata_COMPLETE.py

# 7. Upload to Taxonium
```

### When DTOL Data Updates
```bash
# 1. Extract COI from new genomes
python scripts/extract_dtol_coi.py

# 2. Check orientation, align
mafft --add dtol_new.fasta --keeplength reference.fasta > dtol_aligned.fasta

# 3. Combine with BIOSCAN queries (unchanged)
cat bioscan_aligned.fasta dtol_aligned.fasta > all_queries.fasta

# 4. Re-run EPA-ng
epa-ng --ref-msa reference.fasta --tree reference.tree --query all_queries.fasta

# 5. Regenerate metadata
python scripts/create_metadata_COMPLETE.py

# 6. Upload to Taxonium
```

---

## 📊 KEY STATISTICS (Current Analysis)

- **Total tips:** 1,156
  - Reference: 802
  - BIOSCAN: 347
  - DTOL: 6
  - Polytomy: 1
- **Genera:** 34
- **Countries:** 11 (538 from UK)
- **Mean bootstrap:** 80.4%
- **UK species (UKSI):** 678

---

## 🐛 IMPORTANT FIXES APPLIED

1. **idCorForc3 orientation** - Required reverse complement
2. **Duplicate ProcessIDs** - Stale representative selection fixed
3. **Space vs underscore** - Jplace naming mismatch
4. **Geography integration** - BOLD API column name fix
5. **UKSI data merge** - Restored from Ben's metadata
6. **DTOL links** - Updated to TOLQC format
7. **Markdown links** - Created clickable links for all databases

---

## 📝 DOCUMENTATION FILES

- `WORKFLOW_COMPLETE_SUMMARY.md` - Full analysis documentation
- `FINAL_TREE_SUMMARY.md` - Tree statistics and features
- `EPA_NG_EXPLAINED.md` - EPA-ng methodology
- `WORKFLOW_SLIDE.md` - One-slide workflow summary
- `TAXONIUM_UPLOAD_GUIDE.md` - Upload instructions
- `WORKFLOW_FILES_INVENTORY.md` - This file

---

## 🔍 SCRIPTS TO CREATE/UPDATE FOR GITHUB

### Missing Scripts (Need to Create):
1. `scripts/extract_dtol_coi.py` - DTOL barcode extraction
2. `scripts/create_metadata_COMPLETE.py` - Complete metadata pipeline
3. `scripts/create_taxonium_config.py` - Config generation

### Existing Scripts (Already Good):
1. `scripts/06_select_bin_representatives.py` - Representative selection

---

## 💾 GIT COMMIT CHECKLIST

### Files to Commit:
- [ ] All scripts in `scripts/`
- [ ] Documentation in root directory
- [ ] Example config file
- [ ] README.md with workflow overview
- [ ] .gitignore (exclude large data files)

### Files to .gitignore:
- [ ] `data/output/*` (outputs regenerated)
- [ ] `epa_results/*` (intermediate files)
- [ ] `*.fasta` (large sequence files)
- [ ] `*.newick` (large trees)
- [ ] `*.gz` (compressed outputs)

### Keep in Git:
- [ ] Scripts
- [ ] Documentation
- [ ] Small reference files (<1MB)
- [ ] Example config JSONs
