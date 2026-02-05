# Reference Tree Construction

## Overview

Reference phylogenies are produced by the **Biodiversity Genomics Europe (BGE)** project as part of their iBOL Europe barcoding initiative.

**Source**: [BGE BOLD Library Curation GitHub](https://github.com/bge-barcoding/bold-library-curation/)

---

## Methodology

### 1. Sequence Collection

**Source**: BOLD (Barcode of Life Database)
- Download all public records for target family
- Filter for COI-5P marker gene
- Quality control:
  - Minimum length: 500bp
  - Maximum ambiguous bases: 1%
  - Remove duplicates by process ID

### 2. Sequence Alignment

**Tool**: MAFFT v7  
**Strategy**: `--auto` (automatically selects best algorithm based on dataset size)
- Small datasets (<200 seqs): L-INS-i (accurate, slow)
- Large datasets (>200 seqs): FFT-NS-i (fast)

**Post-processing**:
- Trim to standard COI barcode region
- Remove poorly aligned sequences
- Manual inspection of alignment quality

### 3. Phylogenetic Inference

**Tool**: IQ-TREE 2  
**Model selection**: ModelFinder (automatic)
- Tests 286 DNA substitution models
- Selects best model by BIC (Bayesian Information Criterion)
- Typically selects: GTR+G or GTR+I+G

**Tree search**:
- 1000 ultrafast bootstrap replicates (UFBoot)
- SH-aLRT (Shimodaira-Hasegawa approximate likelihood ratio test)
- Default search parameters

**Bootstrap support**:
- Values at nodes = ultrafast bootstrap percentage (0-100)
- **Interpretation**:
  - ≥95: Very strong support (unambiguous)
  - 80-95: Strong support (reliable)
  - 70-80: Moderate support (acceptable but check alternatives)
  - <70: Weak support (topology uncertain)

### 4. Outgroup Selection

Outgroups chosen from:
- Same order but different family (for family-level trees)
- Phylogenetically appropriate based on known relationships
- 2-3 outgroup taxa per tree

### 5. BIN Quality Analysis (BAGS System)

**BAGS = BIN Assignment Grade System**

Each BIN is graded based on:
- Species-BIN concordance
- Monophyly in phylogenetic tree
- Geographic coherence
- Morphological validation (when available)

**Grade Definitions**:

| Grade | Criteria | Interpretation |
|-------|----------|----------------|
| **A** | 1 species, 1 BIN, monophyletic | High quality, reliable |
| **B** | 1 species, 1 BIN, paraphyletic | May indicate sampling gaps |
| **C** | 1 species, multiple BINs | Potential cryptic species or over-splitting |
| **D** | 1 species, 1 BIN, conflicts with other data | Needs expert review |
| **E** | Multiple species, 1 BIN | Recent divergence or under-splitting |

**Grade C - Monophyly Analysis**:
For species split across multiple BINs, test if the species is:
- **Monophyletic**: All sequences form one clade (likely just BIN artifact)
- **Paraphyletic**: Sequences don't form one clade (likely cryptic species)

### 6. Metadata Curation

Each tree includes:
- `tree_metadata.json`: BAGS grades, species counts, monophyly data
- `curation_data.json`: Detailed BIN-species relationships
- PDF checklist: Visual summary for expert review

---

## Tree File Format

**Format**: Newick  
**Tip labels**: `Species_name|BIN_code|ProcessID`
- Example: `Bradysia_paupera|BOLDACC1234|GBMIN12345-17`

**Node labels**: Bootstrap support values (0-100)

**Branch lengths**: Substitutions per site (from maximum likelihood inference)

---

## Data Quality

### Advantages of BGE Reference Trees

1. **Expert Curation**: Years of taxonomic expertise
2. **Quality Control**: Multiple filtering steps
3. **Bootstrap Support**: Quantified confidence in topology
4. **BAGS Grades**: Pre-identified taxonomic issues
5. **Regular Updates**: Trees updated as new data available

### Limitations

1. **Sampling bias**: European specimens overrepresented
2. **Taxonomy**: Follows BOLD taxonomy (may differ from other authorities)
3. **Missing species**: Not all described species have barcodes
4. **BIN assignments**: BOLD BINs are algorithmic, not taxonomic

---

## Using BGE Trees in This Project - bioscan-phylogenetics

### Why We Use EPA-ng Instead of Rebuilding

1. **Preserves Expertise**: BGE curation represents years of work
2. **Maintains Comparability**: All families use consistent framework
3. **Speed**: Placement takes minutes vs. hours for rebuilding
4. **Quality Metrics**: EPA-ng provides placement confidence (LWR scores)

### Integration Workflow

1. Download BGE reference tree + alignment for family
2. Place UK specimens using EPA-ng
3. Merge BGE metadata (BAGS grades) with UK specimen data
4. Create comprehensive metadata for visualization

---

## Citation

When using BGE reference trees, please cite:
- BGE Project: [Biodiversity Genomics Europe](https://github.com/bge-barcoding/bold-library-curation)
- IQ-TREE: Minh et al. (2020) Mol Biol Evol 37(5):1530-1534
- MAFFT: Katoh & Standley (2013) Mol Biol Evol 30(4):772-780

## Contact

**BGE GitHub**: https://github.com/bge-barcoding/bold-library-curation

---

**For family-specific tree construction details**, see `families/{FAMILY}/README.md`
