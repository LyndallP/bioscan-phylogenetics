# 📤 How to Upload Sciaridae Tree to Taxonium

## Method: Upload Tree + Metadata Separately

Go to https://taxonium.org

### Step 1: Upload Tree
Drag and drop (or click to select):
- `data/output/sciaridae_tree.nwk.gz`

### Step 2: Upload Metadata
When prompted, drag and drop:
- `data/output/sciaridae_metadata.tsv.gz`

**OR**

Upload the uncompressed versions:
- `data/output/sciaridae_tree.nwk` (tree)
- `data/output/sciaridae_taxonium_metadata_FINAL.tsv` (metadata)

---

## ✅ What You'll Get

All 29 metadata columns including:
- **genus, species, family** - Taxonomy
- **geography** - Country data
- **dataset** - BIOSCAN/DTOL/Reference
- **placement_quality** - High/Medium/Low
- **epa_lwr_score** - Confidence scores
- **parent_bootstrap** - Node support values
- **link_BLAST** - NCBI BLAST links
- **link_GBIF** - Distribution maps
- **link_NBN** - UK records
- **link_BOLD** - BIN pages
- **link_DTOL** - Genome portals

---

## 🎨 Custom Colors via URL

After uploading, you can add custom genus colors by modifying the URL:

Add this parameter (URL-encoded):
```
&config={"colorMapping":{"Corynoptera":[230,25,75],"Bradysia":[60,180,75],"Scatopsciara":[255,225,25],"Leptosciarella":[0,130,200],"Cratyna":[245,130,48],"Trichosia":[145,30,180],"Lycoriella":[70,240,240],"Epidapus":[240,50,230],"Scythropochroa":[210,245,60],"Phytosciara":[250,190,212]}}
```

---

## 🔍 Recommended First Views

1. Color by **genus** - See taxonomic diversity
2. Color by **geography** - See collection locations  
3. Color by **dataset** - See data sources
4. Color by **parent_bootstrap** - See phylogenetic support
5. Color by **placement_quality** - See EPA-ng confidence

