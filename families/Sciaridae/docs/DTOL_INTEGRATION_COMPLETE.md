# DTOL Integration Complete - Sciaridae

## Final Outputs

**For Taxonium Upload:**
- **Tree**: `data/output/sciaridae_COMPLETE.newick` (1,204 tips)
- **Metadata**: `data/output/sciaridae_taxonium_metadata_fullplacement.tsv` (1,204 rows)

## Tree Composition

- **Reference sequences**: 802 (from BGE)
- **BIOSCAN specimens**: 395 (UK collections)
- **DTOL specimens**: 6 (genome assemblies)
- **Polytomy**: 1 (Xylosciara betulae - no molecular data)
- **TOTAL**: 1,204 tips

## DTOL Specimens Added

All 6 DTOL specimens successfully integrated:
1. Bradysia nitidicollis (idBraNiti1) - High confidence
2. Corynoptera forcipata (idCorForc1) - High confidence  
3. Corynoptera forcipata (idCorForc3) - High confidence
4. Phytosciara flavipes (idPhyFlap3) - Low confidence
5. Schwenckfeldina carbonaria (idSchCarb1) - High confidence
6. Sciara hemerobioides (idSciHeme3) - High confidence

## Modular Workflow Established

**Key Innovation**: Datasets can be added independently!

### Workflow Structure:
```
1. Reference (CONSTANT):
   - Alignment: Sciaridae_aligned_clean.fasta (805 seqs, 950bp)
   - Tree: Sciaridae_ingroup.treefile (802 tips)

2. For each dataset:
   - Extract raw sequences
   - Align to reference with: mafft --add --keeplength
   - Save as: data/queries/{dataset}_query.fasta

3. To update tree:
   - Combine all query files: cat queries/*.fasta > all_queries.fasta
   - Run EPA-ng once: places all specimens simultaneously
   - Use gappa to convert .jplace → .newick
   - Add polytomies as final step

4. Generate metadata:
   - Run create_fullplacement_metadata_v3.py
   - Automatically handles all tree tips
```

### Files Created:
- `data/queries/bioscan_query.fasta` (395 seqs, 950bp)
- `data/queries/dtol_query.fasta` (6 seqs, 950bp)
- `data/queries/all_queries.fasta` (401 seqs combined)
- `epa_combined/epa_result.jplace` (EPA-ng output)
- `data/output/sciaridae_COMPLETE.newick` (final tree)

## Key Lessons

1. **BIOSCAN sequences were already aligned** to 950bp in the original workflow
2. **DTOL sequences needed orientation correction** - 4/6 were reverse complemented
3. **Query files can be concatenated** because they're all aligned to same width
4. **EPA-ng only needs to run once** with combined queries (fast!)
5. **Metadata script handles name format automatically** - no manual fixes needed

## Reproducibility

To add another dataset (e.g., GOAT genomes):
```bash
# 1. Align new sequences
mafft --add new_sequences.fasta \
      --keeplength \
      /path/to/Sciaridae_aligned_clean.fasta \
      > data/queries/goat_query.fasta

# 2. Combine with existing
cat data/queries/*.fasta > data/queries/all_queries.fasta

# 3. Place all
epa-ng --ref-msa Sciaridae_aligned_clean.fasta \
       --tree Sciaridae_ingroup.treefile \
       --query data/queries/all_queries.fasta \
       --outdir epa_combined \
       --model GTR+G \
       --redo

# 4. Create tree
gappa examine graft \
      --jplace-path epa_combined/epa_result.jplace \
      --out-dir epa_combined

# 5. Add polytomies (if any)
# 6. Generate metadata
python3 create_fullplacement_metadata_v3.py
```

## Date Completed
February 10, 2026

## Next Steps
- Upload to Taxonium for visualization
- Apply workflow to other families
- Document as template for future integrations
