# Sciaridae Phylogeny - Modular EPA-ng Workflow

## 🧬 Data Integration Pipeline
```
Reference Tree (Ben)     BIOSCAN UK          DTOL Genomes
    802 tips          →  13,806 specimens  →  6 assemblies
                         ↓                      ↓
                      Select reps          Extract COI
                      (347 unique)         (orientation-corrected)
                         ↓                      ↓
                      ─────────────────────────
                              ↓
                         Align to ref
                         (MAFFT --add)
                              ↓
                      EPA-ng Placement
                    (single combined run)
                              ↓
                         Final Tree
                      1,156 tips total
                              ↓
                      Add Metadata
                 (geography, links, bootstrap)
                              ↓
                         TAXONIUM
```

## ✨ Key Features
- **Modular**: Each dataset aligned separately, placed together
- **No duplicates**: Representative selection excluded reference ProcessIDs
- **Quality control**: Fixed sequence orientation (idCorForc3), validated placements
- **Rich metadata**: BOLD geography, BLAST/GBIF/NBN/DTOL linkouts, bootstrap support
- **Interactive**: Color by genus/geography/quality, filter by confidence

**Result**: 802 reference + 347 BIOSCAN + 6 DTOL + 1 polytomy = **1,156 tips**
