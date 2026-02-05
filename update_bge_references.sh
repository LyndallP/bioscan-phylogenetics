#!/bin/bash

# ============================================================================
# Update Repository with BGE Reference Information
# ============================================================================

set -e  # Exit on error

echo "Updating repository with BGE reference information..."

# Backup existing files
echo "Creating backups..."
cp README.md README.md.backup
if [ -f families/Sciaridae/README.md ]; then
    cp families/Sciaridae/README.md families/Sciaridae/README.md.backup
fi

# ============================================================================
# 1. Create detailed reference trees documentation
# ============================================================================

echo "Creating docs/reference_trees.md..."

cat > docs/reference_trees.md << 'DOCEOF'
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
DOCEOF

# ============================================================================
# 2. Update main README.md - Add BGE link at top and Reference Trees section
# ============================================================================

echo "Updating main README.md..."

# Create new README with BGE reference added
cat > README.md << 'READMEEOF'
# BIOSCAN Phylogenetics

> Integrates UK BIOSCAN specimens with [BGE Project](https://github.com/bge-barcoding/bold-library-curation) reference phylogenies

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

## Reference Trees

### Source

Reference phylogenies are curated by the **Biodiversity Genomics Europe (BGE)** project:
- **GitHub**: https://github.com/bge-barcoding/bold-library-curation
- **Workflow Documentation**: [BGE README](https://github.com/bge-barcoding/bold-library-curation/blob/main/workflow/README.md)
- **Contact**: See BGE repository

### Tree Construction (Summary)

BGE reference trees use:
- **Sequences**: Downloaded from BOLD database, quality filtered
- **Alignment**: MAFFT (--auto strategy)
- **Phylogenetic inference**: 
  - IQ-TREE2 with ModelFinder
  - 1000 ultrafast bootstrap replicates
  - SH-aLRT branch support
- **Node support**: 
  - Values at nodes represent **ultrafast bootstrap support** (0-100)
  - ≥95: Very strong support
  - 80-95: Strong support
  - 70-80: Moderate support
  - <70: Weak support

### BAGS Quality Grades

Each BIN is assigned a quality grade based on concordance analysis:
- **Grade A**: Single BIN, single species, monophyletic (high quality)
- **Grade B**: Single BIN, single species, paraphyletic (sampling gaps)
- **Grade C**: Multiple BINs, single species (potential cryptic species)
- **Grade D**: Single BIN, single species, conflicts with other data
- **Grade E**: Single BIN, multiple species (recent divergence)

**See** [`docs/reference_trees.md`](docs/reference_trees.md) for complete BGE methodology.

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
├── docs/
│   ├── reference_trees.md    # BGE methodology details
│   └── workflow_overview.md  # Detailed workflow
├── scripts/                  # Analysis scripts
├── families/
│   ├── Sciaridae/           # Completed analysis
│   └── template/            # Template for new families
└── .gitignore
```

## Citation

### This Workflow
If using this workflow, please cite:
- EPA-ng: Barbera et al. (2019) Syst Biol 68(2):365-369
- RAxML-ng: Kozlov et al. (2019) Bioinformatics 35(21):4453-4455
- gappa: Czech & Stamatakis (2019) Bioinformatics 35(16):2906-2907

### BGE Reference Trees
When using BGE reference trees, please cite:
- BGE Project: https://github.com/bge-barcoding/bold-library-curation
- IQ-TREE2: Minh et al. (2020) Mol Biol Evol 37(5):1530-1534
- MAFFT: Katoh & Standley (2013) Mol Biol Evol 30(4):772-780

## Contact

Lyndall Pereira  
[Your Email/Institution]

---

**Last updated**: 2025-01-27
READMEEOF

# ============================================================================
# 3. Create/Update Sciaridae README
# ============================================================================

echo "Updating families/Sciaridae/README.md..."

cat > families/Sciaridae/README.md << 'SCIAREOF'
# Sciaridae Analysis

## Status: ✅ Complete

## Reference Tree Details

**Source**: BGE Project (Biodiversity Genomics Europe)  
**Contributor**: Benjamin  
**Sequences**: 802 ingroup Sciaridae + 3 outgroup taxa  
**Date generated**: December 2024  
**IQ-TREE model**: GTR+F+I+G4 (selected by ModelFinder)  
**Bootstrap replicates**: 1000 (ultrafast bootstrap)  
**Average bootstrap support**: ~87% (strong overall support)

**Node support distribution**:
- High support (≥95): ~65% of nodes
- Strong support (80-95): ~22% of nodes
- Moderate/weak (<80): ~13% of nodes

**BAGS Quality Grades** (from BGE curation):
- Grade A: 80 BINs
- Grade B: 24 BINs
- Grade C: 318 BINs (species split across multiple BINs)
- Grade D: 18 BINs
- Grade E: 254 BINs (multiple species per BIN)

**See** [`docs/reference_trees.md`](../../docs/reference_trees.md) for full BGE methodology.

---

## UK Data Inputs

**BIOSCAN UK Data**:
- 13,806 specimens
- 395 unique BINs
- Collection period: 2023-2025
- Geographic coverage: England, Scotland, Wales

**UKSI Data**:
- 300 UK Sciaridae species
- 299 with BIN assignments
- 1 without molecular data (Xylosciara betulae - added as polytomy)

---

## Analysis Results

### Tree Composition

**Final tree: 829 tips**
- 802 BGE reference sequences
- 23 UK specimens placed via EPA-ng
- 3 outgroup taxa (retained for rooting)
- 1 polytomy (Xylosciara betulae)

### EPA-ng Placements

**23 UK specimens** placed phylogenetically:
- **High confidence (LWR ≥ 0.75)**: 14 sequences
- **Moderate confidence (LWR 0.50-0.75)**: 3 sequences
- **Low confidence (LWR < 0.50)**: 6 sequences

Low confidence placements require further investigation (potential contamination, novel lineages, or poor sequence quality).

### Specimen Coverage

- **402 tree tips** have UK BIOSCAN specimens (48.5% of tree)
- **411 tree tips** are European reference only (no UK specimens)
- **15 tree tips** flagged as "needs attention" (Not in UKSI but has specimens)

---

## Key Findings

### Cases Needing Attention (15 total)

**High Priority**:
1. **Unknown_species (BIN BOLD:AHE4422)**: 265 specimens
   - Largest unknown group
   - Low placement confidence (LWR = 0.38)
   - Likely cryptic species complex or misidentification
   - **Action**: Morphological examination, re-sequencing

2. **Lycoriella acutostylia**: 1 specimen
   - Named species NOT in UKSI
   - High placement confidence (LWR = 0.996)
   - **Possible explanations**: New UK record, taxonomic synonym, misidentification
   - **Action**: Verify identification, check recent literature

**Medium Priority**:
- 13 other Unknown_species with 1-2 specimens each
- Various confidence levels (LWR 0.34-1.00)
- May represent rare species or identification issues

### BIN Quality Issues

**Grade C (318 tips)**: Species split across multiple BINs
- May indicate cryptic species complexes
- Requires monophyly testing (data currently unavailable)

**Grade E (107 tips with BIN sharing)**: Multiple species per BIN
- Recent divergence or taxonomic uncertainty
- Examples: Multiple Bradysia species sharing BINs

---

## Outputs

**Location**: `data/output/`

### Files for Taxonium Visualization

1. **sciaridae_final_tree.newick**
   - Complete phylogenetic tree
   - 829 tips with branch lengths
   - Bootstrap support at nodes

2. **sciaridae_taxonium_metadata.tsv**
   - 829 rows (one per tree tip)
   - 20 metadata columns including:
     - BIN identifiers and quality grades
     - Specimen counts per BIN
     - Placement confidence scores
     - Geographic information
     - Flags for cases needing attention

### Visualization Recommendations

**Color by**:
- `category`: BIOSCAN_collected vs Europe_reference vs Not_in_UKSI
- `bags_grade`: A/B (clean) vs C (split) vs E (shared)
- `needs_attention`: Highlight unexpected findings

**Filter by**:
- `bioscan_specimens > 0`: Only collected species
- `placement_quality = Low_confidence`: Review placements
- `bin_quality_issue`: Identify taxonomic issues

---

## Issues Encountered & Solutions

### Format Incompatibilities
**Problem**: Alignment headers had extra taxonomic info preventing EPA-ng from running  
**Solution**: Used `sed` to strip extra text: `sed 's/ Ingroup|.*$//'`

### Outgroup Mismatch
**Problem**: Tree contained outgroups not in alignment  
**Solution**: Removed outgroups with `ete3` before EPA-ng placement

### BIN Format Inconsistency
**Problem**: Query BINs missing colons (BOLDACU8309 vs BOLD:ACU8309)  
**Solution**: Added colon programmatically: `'BOLD:' + bin_code[4:]`

### BAGS Grade Matching
**Problem**: Initial species name matching missed 140 sequences  
**Solution**: Match by BIN first, then fall back to species name

---

## Future Improvements

- [ ] Extract monophyly data for Grade C species (currently unavailable)
- [ ] Add actual collection geography (currently uses UKSI membership as proxy)
- [ ] Integrate DTOL/GOAT genome-derived sequences
- [ ] Investigate BOLD:AHE4422 specimens (265 specimens, low confidence)
- [ ] Validate Lycoriella acutostylia UK record

---

## References

**BGE Reference Tree**:
- Source: https://github.com/bge-barcoding/bold-library-curation
- Generated: December 2024
- Contact: Benjamin (see BGE repository)

**This Analysis**:
- Date completed: January 2025
- Analyst: Lyndall Pereira
SCIAREOF

# ============================================================================
# Done!
# ============================================================================

echo ""
echo "✓ Updates complete!"
echo ""
echo "Files modified:"
echo "  - README.md (added BGE reference section)"
echo "  - docs/reference_trees.md (created detailed documentation)"
echo "  - families/Sciaridae/README.md (added reference tree details)"
echo ""
echo "Backups created:"
echo "  - README.md.backup"
if [ -f families/Sciaridae/README.md.backup ]; then
    echo "  - families/Sciaridae/README.md.backup"
fi
echo ""
echo "Next steps:"
echo "  1. Review the changes: git diff"
echo "  2. If satisfied: git add . && git commit -m 'Add BGE reference documentation'"
echo "  3. Push to GitHub: git push"
