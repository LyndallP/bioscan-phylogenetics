# BIOSCAN Phylogenetics

Workflow for integrating UK BIOSCAN arthropod specimens with European reference phylogenies using EPA-ng (Evolutionary Placement Algorithm).

## Overview

This project places UK BIOSCAN specimens onto expert-curated European reference trees, enabling:
- Rapid integration of new specimens without rebuilding entire phylogenies
- Leveraging existing taxonomic expertise from European datasets
- Identifying potential new UK records, cryptic species, and taxonomic issues
- Consistent framework for cross-border biodiversity assessment

## Status

### Completed Families

| Family | Tree Tips | BIOSCAN Specimens | Unique BINs | Status | Notable Findings |
|--------|-----------|-------------------|-------------|--------|------------------|
| **Sciaridae** | 829 | 13,806 | 395 | ✅ Complete | 15 cases need attention (potential new UK records) |

### In Progress

- [ ] Chironomidae
- [ ] Tipulidae
- [ ] Other Diptera families

## Methodology

### Core Workflow

1. **Format Standardization** - Clean alignment headers, remove outgroups, standardize BIN format
2. **Model Optimization** (RAxML-ng) - Optimize GTR+G parameters on reference tree
3. **Phylogenetic Placement** (EPA-ng) - Place UK specimens onto European reference tree
4. **Tree Grafting** (gappa) - Combine reference + placed sequences into single tree
5. **Metadata Integration** - Merge BIOSCAN data, add BIN quality grades, flag cases needing attention

### Why EPA-ng Instead of Tree Rebuilding?

- **Speed**: Minutes vs. hours/days
- **Expertise**: Preserves expert curation in reference trees
- **Confidence**: Provides LWR scores (placement reliability)
- **Scalability**: Easy to add new specimens as they're sequenced
- **Comparability**: All families use same reference framework

## Requirements

### Software
- [RAxML-ng](https://github.com/amkozlov/raxml-ng) (≥1.0)
- [EPA-ng](https://github.com/Pbdas/epa-ng) (≥0.3.8)
- [gappa](https://github.com/lczech/gappa) (≥0.8.0)
- Python 3.7+ with pandas, ete3

### Installation (via conda)
```bash
conda create -n phylo -c bioconda raxml-ng epa-ng gappa python=3.9
conda activate phylo
pip install pandas ete3
```

## Quick Start
```bash
cd families/{FAMILY}
bash ../../scripts/run_pipeline.sh {FAMILY}
```

See `families/Sciaridae/README.md` for detailed example.

## Repository Structure
```
bioscan-phylogenetics/
├── README.md
├── docs/                    # Detailed documentation
├── scripts/                 # Analysis scripts
├── families/
│   ├── Sciaridae/          # Completed analysis
│   └── template/           # Template for new families
└── .gitignore
```

## Citation

If using this workflow, please cite:
- EPA-ng: Barbera et al. (2019) Syst Biol 68(2):365-369
- RAxML-ng: Kozlov et al. (2019) Bioinformatics 35(21):4453-4455
- gappa: Czech & Stamatakis (2019) Bioinformatics 35(16):2906-2907

## Contact

Lyndall Pereira  
[Your Email/Institution]

---

**Last updated**: 2025-01-27
