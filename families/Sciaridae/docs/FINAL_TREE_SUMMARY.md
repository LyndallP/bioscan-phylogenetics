# Sciaridae Phylogeny - Final Version (v2)

**Date:** February 10, 2026  
**Status:** ✅ COMPLETE AND READY FOR TAXONIUM

---

## 🎯 Final Tree Statistics

### Composition
- **Total tips:** 1,156
  - Reference (Ben's tree): 802
  - BIOSCAN UK: 347
  - DTOL genomes: 6
  - Polytomy: 1

### Taxonomy
- **Genera:** 35
- **Species:** ~400+
- **Family:** Sciaridae

### Node Support (Reference Tree)
- **Mean bootstrap:** 80.4%
- **Median bootstrap:** 90.8%
- **Very high (≥95%):** 296 nodes (37.3%)
- **High (80-94%):** 253 nodes (31.9%)
- **Good phylogenetic signal!**

---

## 📁 Files for Taxonium Upload

**Tree:** `data/output/sciaridae_FINAL_v2.newick` (1,156 tips, with bootstrap values)  
**Metadata:** `data/output/sciaridae_taxonium_metadata_COMPLETE.tsv` (1,160 rows, 22 columns)

**Upload to:** https://taxonium.org

---

## 🎨 Visualization Features in Taxonium

### Color by Taxonomy
- **genus** - 35 genera (Corynoptera, Bradysia, etc.)
- **family** - All Sciaridae
- **species** - ~400 species

### Color by Data Source
- **dataset** - BIOSCAN / DTOL / Reference
- **geography** - UK, Norway, Germany, etc.

### Color by Quality
- **placement_quality** - High/Medium/Low (EPA-ng confidence)
- **epa_lwr_score** - 0-1 (for BIOSCAN + DTOL specimens)

### Node Support
- Bootstrap values visible on internal nodes (0-100%)
- Can filter/search for well-supported clades

---

## 🐛 Critical Bug Fixed: idCorForc3

**Problem:** Corynoptera forcipata specimen idCorForc3 had extremely long branch (pendant length 0.294)

**Investigation:**
1. Compared to idCorForc1 (same species, normal branch)
2. Checked both forward and reverse complement orientations
3. Alignment scores showed reverse complement was MORE similar to idCorForc1

**Solution:** Reverse complemented idCorForc3

**Result:**
- **Before:** Pendant length 0.294, LWR 1.0 (long branch despite high confidence!)
- **After:** Pendant length 0.018, LWR 1.0 (normal branch, high confidence)
- **Fixed!** Now clusters correctly with idCorForc1

**Lesson:** Even with high EPA-ng confidence (LWR), check pendant length - very long branches indicate sequence problems!

---

## 📊 Metadata Columns (22 total)

1. **name** - Tip label
2. **bin** - BOLD BIN code
3. **species** - Species name
4. **genus** - Genus (extracted from species) ✨ NEW
5. **family** - Family (all Sciaridae) ✨ NEW
6. **category** - Classification category
7. **geography** - Country from BOLD API
8. **in_uksi** - UK Species Inventory membership
9. **placement_type** - reference/bioscan/dtol/polytomy
10. **placement_quality** - High/Medium/Low
11. **placement_interpretation** - Notes
12. **epa_lwr_score** - EPA-ng likelihood weight ratio
13. **bags_grade** - BAGS quality grade
14. **bin_quality_issue** - BIN quality flags
15. **n_bins_for_species** - Number of BINs per species
16. **all_bins** - All BINs for species
17. **bioscan_specimens** - Number of specimens
18. **needs_attention** - Flagged for review
19. **tolid** - DTOL Tree of Life ID
20. **assembly_status** - Genome assembly status
21. **genome_status** - Genome status
22. **dataset** - BIOSCAN/DTOL/Reference

---

## 🔬 Workflow Applied

1. ✅ Selected BIOSCAN representatives (347) - excluded reference ProcessIDs
2. ✅ Aligned to 950bp reference
3. ✅ Added DTOL sequences (6) - orientation corrected
4. ✅ Combined queries (353 total)
5. ✅ EPA-ng placement on reference (802 tips)
6. ✅ Added polytomy (1 species without molecular data)
7. ✅ Generated metadata with geography from BOLD
8. ✅ Added taxonomy columns (genus, family)
9. ✅ Fixed idCorForc3 orientation bug
10. ✅ Re-ran EPA-ng with corrected sequences

**Result:** Clean tree, no duplicates, proper orientation, complete metadata!

---

## 🎓 Key Findings

### BIOSCAN Coverage
- 347 UK specimens representing 324 validation + 23 novel BINs
- Zero ProcessID overlap with reference (bug fixed!)
- All placements have LWR scores for confidence assessment

### DTOL Integration
- 6 genome assemblies successfully integrated
- 5/6 high confidence placements (LWR = 1.0)
- 1/6 required orientation correction (idCorForc3)
- All now have normal branch lengths

### Geographic Distribution
- UK: 538 specimens (BIOSCAN + some reference)
- Norway: 154 (reference)
- Germany: 137 (reference)
- Canada: 106 (reference)
- 10+ other countries

### Genus Diversity
- 35 genera identified
- Top genera: Corynoptera (240), Bradysia (225)
- Can assess genus monophyly in Taxonium

---

## 🚀 Next Steps

1. **Upload to Taxonium** - Visualize and explore
2. **Check genus monophyly** - Are genera clustering properly?
3. **Identify taxonomic issues** - Look for paraphyletic groups
4. **Validation analysis** - Do BIOSCAN specimens cluster with reference?
5. **Geographic patterns** - Any biogeographic signal?
6. **Apply to other families** - Use same workflow for other Sciaroidea

---

## 📝 Reproducibility

All scripts and data are in:
`~/Desktop/Taxonium/phylogenies/bioscan-phylogenetics/families/Sciaridae/`

Key scripts:
- `06_select_bin_representatives.py` - Specimen selection
- `create_fullplacement_metadata_FINAL.py` - Metadata generation
- `fix_geography.py` - Geography integration
- Workflow documented in `WORKFLOW_COMPLETE_SUMMARY.md`

---

**Tree is ready for scientific analysis! 🎉**
