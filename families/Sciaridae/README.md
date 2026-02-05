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
