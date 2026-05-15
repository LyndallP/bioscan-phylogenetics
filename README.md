# BIOSCAN Phylogenetics

> Integrates UK BIOSCAN specimens with [BGE Project](https://github.com/bge-barcoding/bold-library-curation) reference phylogenies

Workflow for integrating UK BIOSCAN arthropod specimens with European reference phylogenies using EPA-ng (Evolutionary Placement Algorithm). Trees and metadata for all completed families are browsable via the **[GitHub Pages index](https://lyndallp.github.io/bioscan-phylogenetics/)**.

## Overview

This project places UK BIOSCAN specimens onto expert-curated European reference trees, enabling:
- Rapid integration of new specimens without rebuilding entire phylogenies
- Leveraging existing taxonomic expertise from European datasets
- Identifying potential new UK records, cryptic species, and taxonomic issues
- Consistent framework for cross-border biodiversity assessment

## Status

426 arthropod families are complete and available via the [interactive index](https://lyndallp.github.io/bioscan-phylogenetics/). Each family entry links directly to its Taxonium tree.

## Methodology

### Core Workflow

1. **Format Standardisation** — Clean alignment headers, remove outgroups, standardise BIN format
2. **Model Optimisation** (RAxML-ng) — Optimise GTR+G parameters on reference tree
3. **BIOSCAN Sequence Selection** — Select one representative per BIN for placement (see below)
4. **Phylogenetic Placement** (EPA-ng) — Place UK specimens onto European reference tree
5. **Tree Grafting** (gappa) — Combine reference + placed sequences into single tree
6. **Metadata Integration** — Merge BIOSCAN data, add BIN quality grades, flag cases needing attention

### BIOSCAN Sequence Selection

Because placing every BIOSCAN specimen individually would be redundant, the pipeline selects **one representative sequence per BIN** (Barcode Index Number) for EPA-ng placement. The full set of BIOSCAN specimens for that BIN is then represented in the metadata by their shared BIN node in the tree.

Selection is performed by `scripts/06_select_bin_representatives.py`:

1. **Exclude specimens already in the reference tree** — any BIOSCAN process ID that appears in the BGE reference tree tip labels is removed from consideration, since it is already placed.
2. **Score remaining sequences** — each sequence is assigned a quality score:
   ```
   quality_score = sequence_length − (count_of_N_bases × 10)
   ```
   This favours longer sequences and penalises ambiguous bases heavily (each N subtracts 10 from the score).
3. **Select the top-scoring sequence per BIN** — sequences are sorted by quality score (descending) and grouped by `bin_uri`; the highest-scoring sequence is taken as the representative. Where two sequences have identical scores, the one appearing first in the source BIOSCAN file is chosen.

The representative's process ID is used as the tree tip label. All other BIOSCAN specimens sharing that BIN are linked to the same node in the metadata.

### Why EPA-ng Instead of Tree Rebuilding?

- **Speed**: Minutes vs. hours/days
- **Expertise**: Preserves expert curation in reference trees
- **Confidence**: Provides LWR scores (placement reliability)
- **Scalability**: Easy to add new specimens as they are sequenced
- **Comparability**: All families use the same reference framework

## Reference Trees

### Source

Reference phylogenies are curated by the **Biodiversity Genomics Europe (BGE)** project:
- **GitHub**: https://github.com/bge-barcoding/bold-library-curation
- **Workflow Documentation**: [BGE README](https://github.com/bge-barcoding/bold-library-curation/blob/main/workflow/README.md)

### Tree Construction (Summary)

BGE reference trees use:
- **Sequences**: Downloaded from BOLD database, quality filtered
- **Alignment**: MAFFT (--auto strategy)
- **Phylogenetic inference**:
  - IQ-TREE2 with ModelFinder
  - 1000 ultrafast bootstrap replicates
  - SH-aLRT branch support
- **Node support**:
  - Values at nodes represent **ultrafast bootstrap support** (0–100)
  - ≥95: Very strong support
  - 80–95: Strong support
  - 70–80: Moderate support
  - <70: Weak support

### BAGS Quality Grades

Each BIN is assigned a quality grade based on concordance analysis:
- **Grade A**: Single BIN, single species, monophyletic (high quality)
- **Grade B**: Single BIN, single species, paraphyletic (sampling gaps)
- **Grade C**: Multiple BINs, single species (potential cryptic species)
- **Grade D**: Single BIN, single species, conflicts with other data
- **Grade E**: Single BIN, multiple species (recent divergence)

See [`docs/reference_trees.md`](docs/reference_trees.md) for complete BGE methodology.

## Requirements

### Software
- [RAxML-ng](https://github.com/amkozlov/raxml-ng) (≥1.0)
- [EPA-ng](https://github.com/Pbdas/epa-ng) (≥0.3.8)
- [gappa](https://github.com/lczech/gappa) (≥0.8.0)
- Python 3.7+ with pandas, ete3

### Installation (via conda)
```bash
conda create -n phylo -c bioconda raxml-ng epa-ng gappa mafft hmmer python=3.9
conda activate phylo
pip install pandas biopython ete3 requests
```

## Quick Start
```bash
bash scripts/run_family_pipeline.sh --family {FAMILY}
```

See [`docs/pipeline.md`](docs/pipeline.md) for the full 15-step guide and [`families/Sciaridae/README.md`](families/Sciaridae/README.md) for a worked example.

## Repository Structure
```
bioscan-phylogenetics/
├── README.md
├── generate_index.py            # Builds GitHub Pages index from data/
├── add_global_columns.py        # Enriches global Arthropoda metadata
├── config.json                  # Taxonium colour configuration
├── category_guide.tsv           # Reference for specimen category values
├── docs/
│   ├── pipeline.md              # Full 15-step pipeline guide
│   ├── reference_trees.md       # BGE methodology details
│   ├── taxonium_sharing.md      # How to share and customise Taxonium links
│   └── workflow_overview.md     # Detailed workflow with diagrams
├── scripts/                     # All pipeline scripts
│   ├── run_family_pipeline.sh   # Main pipeline orchestrator (15 steps)
│   ├── run_diptera_batch.sh     # Batch runner for all Diptera families
│   ├── run_other_batch.sh       # Batch runner for all non-Diptera families
│   └── *.py                     # Individual step scripts (steps 0–15)
├── families/
│   ├── Sciaridae/               # Completed analysis with full documentation
│   └── template/                # Template for new families
├── data/                        # Output trees and metadata (426 families)
│   └── {Family}/
│       ├── {Family}_final_tree.newick
│       └── {family}_metadata_FINAL.tsv
└── .github/workflows/
    └── generate_pages.yml       # Auto-regenerates index.html on push
```

## Citation

### This Workflow
If using this workflow, please cite:
- EPA-ng: Barbera et al. (2019) Syst Biol 68(2):365–369
- RAxML-ng: Kozlov et al. (2019) Bioinformatics 35(21):4453–4455
- gappa: Czech & Stamatakis (2019) Bioinformatics 35(16):2906–2907

### BGE Reference Trees
When using BGE reference trees, please cite:
- BGE Project: https://github.com/bge-barcoding/bold-library-curation
- IQ-TREE2: Minh et al. (2020) Mol Biol Evol 37(5):1530–1534
- MAFFT: Katoh & Standley (2013) Mol Biol Evol 30(4):772–780

### Global Arthropoda Tree
The global Arthropoda synthesis tree is based on:
- Alhalabi et al. (2026) — family-level arthropod synthesis phylogeny (Zenodo)

## Contact

Lyndall Pereira

---

**Last updated**: 2026-05-15
