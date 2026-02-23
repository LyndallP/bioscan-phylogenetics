# Sciaridae Phylogenetic Analysis

Modular EPA-ng workflow for integrating BIOSCAN UK specimens and DTOL genomes into a reference phylogeny for interactive visualization in Taxonium.

## 📊 Overview

This pipeline places new COI barcode sequences onto an existing reference phylogeny using EPA-ng (Evolutionary Placement Algorithm), creating an interactive tree with clickable database links.

**Current tree:** 1,156 specimens
- 802 reference specimens (Ben's tree)
- 347 BIOSCAN UK representatives
- 6 DTOL genome assemblies  
- 1 polytomy (missing barcode species)

## 🔧 Requirements

### Software
- Python 3.9+
  - BioPython
  - pandas
  - requests
- MAFFT (alignment)
- EPA-ng (phylogenetic placement)
- gappa (jplace conversion)
- taxoniumtools (JSONL conversion, optional)

### Install
```bash
# Python packages
pip install biopython pandas requests

# MAFFT
conda install -c bioconda mafft

# EPA-ng
conda install -c bioconda epa-ng

# gappa
conda install -c bioconda gappa
```

## 📁 Directory Structure
```
Sciaridae/
├── data/
│   ├── reference/          # Ben's reference tree (constant)
│   ├── queries/            # Sequences to place
│   ├── output/             # Final outputs
│   └── config/             # Configs
├── scripts/                # Analysis scripts
├── epa_results/            # EPA-ng outputs
└── docs/                   # Documentation
```

## 🚀 Workflow

### Full Pipeline (First Time)
```bash
# 1. Select BIOSCAN representatives
python scripts/06_select_bin_representatives.py \
    --bioscan UKBOL_bioscan_selected.tsv \
    --reference data/reference/Sciaridae_ingroup.treefile \
    --output data/queries/sciaridae_representatives.fasta

# 2. Extract DTOL COI barcodes
python scripts/extract_dtol_coi.py \
    --dtol-dir /path/to/dtol/assemblies \
    --output data/queries/dtol_sciaridae.fasta

# 3. Align queries to reference
bash scripts/02_align_queries.sh

# 4. Run EPA-ng placement
bash scripts/03_run_epa_placement.sh

# 5. Generate metadata
python scripts/create_metadata_COMPLETE.py \
    --tree data/output/sciaridae_FINAL_v2.newick \
    --jplace epa_results/epa_result.jplace \
    --fullplacement data/output/sciaridae_taxonium_metadata_fullplacement.tsv \
    --ben-metadata /path/to/ben/sciaridae_taxonium_metadata.tsv \
    --dtol-metadata data/output/dtol_metadata.tsv \
    --output data/output/sciaridae_metadata_UPLOAD.tsv

# 6. Create Taxonium config
python scripts/create_taxonium_config.py \
    --metadata data/output/sciaridae_metadata_UPLOAD.tsv \
    --output data/output/taxonium_config_FINAL.json

# 7. Upload to Taxonium!
# Upload: sciaridae_tree.nwk.gz + sciaridae_metadata_UPLOAD.tsv.gz
```

### Update When BIOSCAN Data Changes
```bash
# Re-run steps 1, 3-6
python scripts/06_select_bin_representatives.py ...
bash scripts/02_align_queries.sh
bash scripts/03_run_epa_placement.sh
python scripts/create_metadata_COMPLETE.py ...
```

### Update When DTOL Data Changes
```bash
# Re-run steps 2-6
python scripts/extract_dtol_coi.py ...
bash scripts/02_align_queries.sh
bash scripts/03_run_epa_placement.sh
python scripts/create_metadata_COMPLETE.py ...
```

## 📤 Outputs

### For Taxonium
- `sciaridae_tree.nwk.gz` - Newick tree with bootstrap
- `sciaridae_metadata_UPLOAD.tsv.gz` - Complete metadata
- `taxonium_config_FINAL.json` - Custom colors/config

Upload to: https://taxonium.org

## 🎨 Features

- **Clickable links:** GBIF, BOLD, NBN Atlas, NCBI BLAST, DTOL
- **Custom colors:** 20 vivid colors for major genera
- **Metadata:** 29 columns including geography, bootstrap, placement quality
- **Modular:** Update BIOSCAN or DTOL independently

## 📝 Key Scripts

| Script | Purpose |
|--------|---------|
| `06_select_bin_representatives.py` | Choose 1 rep/BIN from BIOSCAN |
| `extract_dtol_coi.py` | Extract COI from genomes |
| `02_align_queries.sh` | MAFFT alignment |
| `03_run_epa_placement.sh` | EPA-ng placement |
| `create_metadata_COMPLETE.py` | Generate metadata |
| `create_taxonium_config.py` | Taxonium config |

## 🐛 Important Fixes

- **DTOL orientation:** Check forward vs reverse complement
- **Duplicate ProcessIDs:** Exclude reference specimens
- **Geography:** Pull from BOLD API, not stale files
- **UKSI/BAGS:** Merge from Ben's metadata
- **Markdown links:** Format `[text](url)` for clickability

## 📚 Documentation

See `docs/` for:
- `WORKFLOW_COMPLETE_SUMMARY.md` - Detailed workflow
- `EPA_NG_EXPLAINED.md` - Methodology
- `WORKFLOW_FILES_INVENTORY.md` - Complete file list

## 🤝 Citation

If using this workflow, please cite:
- EPA-ng: Barbera et al. (2019)
- gappa: Czech et al. (2020)
- Taxonium: Sanderson (2022)

## 📧 Contact

Questions? Open an issue or contact the maintainers.
