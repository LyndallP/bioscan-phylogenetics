# NOVEL PLACEMENT LWR SCORES - FIXED! ✅

## Problem Identified

The 23 "Novel placement" specimens had **empty EPA-ng LWR scores** in the metadata, which meant they were being categorized as "Novel placement" instead of receiving proper High/Good/Moderate support categories based on their actual placement confidence.

## Root Cause

The LWR scores **DID exist** in the EPA-ng output file (`epa_result.jplace`), but there was a **name format mismatch** between the metadata and the jplace file:

- **Metadata format**: `Unknown_species|BOLDAER2788|WOXF3244-25`
- **jplace format**: `BOLDAER2788|Unknown_species|WOXF3244-25`

The BOLD ID and genus name positions were swapped, preventing automatic matching during metadata creation.

## Solution

Created `fix_novel_lwr_scores.py` which:

1. **Extracted all 395 LWR scores** from the jplace file
2. **Matched specimens by BOLD ID** (invariant part of the name)
3. **Updated the 23 Novel specimens** with their correct LWR scores
4. **Recalculated "Node support / Placement"** categories based on LWR thresholds
5. **Added placement interpretations** explaining the confidence level

## Results

### Novel Placement Distribution

**BEFORE FIX:**
- Novel placement: 23 specimens (100%)
- All lacked LWR scores and support categories

**AFTER FIX:**
- **High (0.90-1.00)**: 13 specimens (57%) - Confident placements
- **Good (0.75-0.89)**: 1 specimen (4%) - Good placement
- **Moderate to Low (0-0.74)**: 9 specimens (39%) - Uncertain placements

### Example Specimens

**High confidence placements (LWR ≥ 0.90):**
- `Unknown_species|BOLDAER2788|WOXF3244-25`: LWR = 0.9999
- `Unknown_species|BOLDAHG0008|RRNW21550-25`: LWR = 0.9999
- `Bradysia_polonica|BOLDAHE4699|RRNW21811-25`: LWR = 1.0
- `Sciara_hemerobioides|BOLDAHE3912|HLNR4712-24`: LWR = 1.0

**Moderate/uncertain placements (LWR < 0.75):**
- `Unknown_species|BOLDAHD7297|LUHW1091-25`: LWR = 0.37
- `Unknown_species|BOLDAHE3922|NSBE1314-25`: LWR = 0.34
- `Unknown_species|BOLDAHE4422|JHGS7583-25`: LWR = 0.38

These lower-confidence placements may need:
- Additional sequencing data
- Manual verification of placement
- Morphological confirmation

## Final Dataset Statistics

### Complete "Node support / Placement" Breakdown (All 1,156 specimens)

| Category | Count | Percentage |
|----------|-------|------------|
| **High (0.90-1.00)** | 927 | 80.2% |
| **Good (0.75-0.89)** | 68 | 5.9% |
| **Moderate to Low (0-0.74)** | 138 | 11.9% |
| **No support data** | 23 | 2.0% |

**Total**: 1,156 specimens with support information

The 23 "No support data" specimens are reference tree nodes that lack bootstrap values (not Novel placements).

## Files Created

1. **`sciaridae_metadata_FIXED_LWR.tsv`** - Updated metadata with corrected LWR scores
2. **`fix_novel_lwr_scores.py`** - Reproducible script for the fix
3. **`epa_lwr_scores_extracted.tsv`** - All 395 LWR scores from jplace file
4. **`NOVEL_LWR_FIX_SUMMARY.md`** - This summary document

## Impact on Taxonium Visualization

### BEFORE:
- Users couldn't assess Novel placement quality
- All 23 Novel specimens showed as "Novel placement" category
- No way to filter by placement confidence

### AFTER:
- **Search by confidence**: `Node support / Placement:High (0.90-1.00)`
- **Color by support**: Now includes Novel specimens in the color scheme
- **Filter uncertain placements**: `Node support / Placement:Moderate to Low (0-0.74)`
- **Complete coverage**: ALL 1,133 placed specimens now have support categories

## Technical Details

### EPA-ng Placement Info

From `epa_info.log`:
- **Query sequences**: 395 specimens (BIOSCAN + Novel)
- **Reference tree**: 802 taxa
- **Model**: GTR+Γ (4 categories, α = 0.387)
- **Placement time**: <1 second

### LWR Score Interpretation

| LWR Range | Category | Interpretation |
|-----------|----------|----------------|
| 0.90 - 1.00 | High | Very confident placement |
| 0.75 - 0.89 | Good | Good placement confidence |
| 0.50 - 0.74 | Moderate | Uncertain, needs review |
| 0.00 - 0.49 | Low | Highly uncertain placement |

## Next Steps

For the 9 Novel specimens with moderate/low confidence (LWR < 0.75):

1. **Review placement** - Check where they landed in the tree
2. **Morphological verification** - If specimens available
3. **Additional sequencing** - Consider longer sequences or additional markers
4. **Flag for taxonomic review** - May represent divergent/misidentified specimens

## Command to Regenerate Tree

Use the corrected metadata file:

```bash
newick_to_taxonium \
  --input sciaridae_tree.nwk \
  --metadata sciaridae_metadata_FIXED_LWR.tsv \
  --output sciaridae.jsonl.gz \
  --key_column name \
  --columns "subfamily,genus,species,ThumbnailURL,bin,category,placement_type,placement_interpretation,epa_lwr_score,all_bins_for_species,bin_status,in_uksi,Bioscan specimen count,geography,geography_broad,GBIF,BOLD_BIN,BOLD_Specimen,BOLD_BIOSCAN,species_in_GOAT,GOAT,NBN,TOLQC,BLAST,processid,sts_specimen.id,parent_bootstrap,Node support / Placement,dataset,tolid,assembly_status,genome_status,family" \
  --config_json taxonium_config_comprehensive.json
```

---

**Status**: ✅ COMPLETE - All Novel placements now have LWR scores and proper support categories!
