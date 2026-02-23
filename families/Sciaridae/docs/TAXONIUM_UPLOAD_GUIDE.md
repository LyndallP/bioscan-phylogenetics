# 🎯 Sciaridae Taxonium Upload Guide

## 📁 Files Ready for Upload

**Main File to Upload:**
- `data/output/sciaridae_taxonium.jsonl.gz` (51 KB, 2,307 nodes)

**Upload to:** https://taxonium.org

---

## ✨ Features Included

### 1. **Custom Genus Colors** (14 genera with defined colors)
The JSONL includes custom colors for major genera - they'll appear automatically!

### 2. **External Links** (clickable when you select a node)
- **link_BLAST**: 954 sequences ready for NCBI BLAST search
- **link_GBIF**: 1,064 species → GBIF distribution maps
- **link_NBN**: 1,064 species → NBN Atlas UK records
- **link_BOLD**: 1,153 BINs → BOLD Systems pages
- **link_DTOL**: 6 genomes → Darwin Tree of Life portal

### 3. **Bootstrap Support**
- **parent_bootstrap**: 465 tips have parent node bootstrap values (0-100%)
- Mean bootstrap: 80.4% (excellent for COI!)

### 4. **Complete Metadata** (29 columns)
- Taxonomy: species, genus, family
- Geography: 11 countries (538 from UK)
- Data source: Reference/BIOSCAN/DTOL
- Placement quality: High/Medium/Low confidence
- EPA-ng scores: LWR values for all placements

---

## 🎨 Recommended Views in Taxonium

After uploading, try these visualizations by using the "Color by" dropdown:

### View 1: **Genus Diversity** ⭐
- Color by: `genus`
- Shows: 35 genera with custom colors for top 14
- **Best for:** Understanding genus-level diversity

### View 2: **Geographic Distribution**
- Color by: `geography`
- Shows: UK (538), Norway (154), Germany (137), +8 more countries
- **Best for:** Seeing where specimens were collected

### View 3: **Data Sources**
- Color by: `dataset`
- Shows: Reference (807), BIOSCAN (346), DTOL (6)
- **Best for:** Distinguishing different data contributions

### View 4: **Placement Confidence**
- Color by: `placement_quality`
- Shows: High/Medium/Low confidence placements
- **Best for:** Assessing EPA-ng placement reliability

### View 5: **Bootstrap Support**
- Color by: `parent_bootstrap`
- Shows: Phylogenetic confidence of parent nodes
- **Best for:** Finding well-supported clades

---

## 🔍 Useful Searches

Use the search box in Taxonium to filter:

### By Geography
- `geography:United Kingdom` - Just UK specimens (538)
- `geography:Norway` - Norwegian specimens (154)

### By Dataset
- `dataset:BIOSCAN` - UK BIOSCAN specimens (346)
- `dataset:DTOL` - Genome assemblies (6)
- `dataset:Reference` - Reference tree (807)

### By Quality
- `placement_quality:High` - High confidence placements
- `parent_bootstrap:>90` - Nodes with bootstrap >90%

### By Taxonomy
- `genus:Corynoptera` - All Corynoptera (240 specimens)
- `genus:Bradysia` - All Bradysia (225 specimens)

---

## 🔗 Clicking on External Links

When you click on any node in Taxonium, the right panel shows metadata including:

1. **link_BLAST** - Click to open NCBI BLAST with the sequence pre-loaded
2. **link_GBIF** - See species distribution maps
3. **link_NBN** - UK species occurrence records
4. **link_BOLD** - BIN page with all specimens in that BIN
5. **link_DTOL** - Genome assembly information (DTOL only)

---

## 📊 Tree Statistics

- **Total tips:** 1,156
  - Reference (Ben's tree): 802
  - BIOSCAN UK: 347 (346 after dedup)
  - DTOL genomes: 6
  - Polytomy: 1
- **Total nodes:** 2,307 (1,156 tips + 1,151 internal)
- **Genera represented:** 35
- **Countries:** 11
- **Mean bootstrap support:** 80.4%

---

## 🐛 Bug Fixed: idCorForc3

The tree includes the corrected version where **Corynoptera forcipata idCorForc3** was reverse complemented, reducing its pendant length from 0.294 to 0.018 - now clustering correctly with idCorForc1!

---

## 💡 Tips for Exploration

1. **Start broad:** Color by genus to see major groups
2. **Zoom in:** Click on clades of interest
3. **Check quality:** Use placement_quality to assess confidence
4. **Verify taxonomy:** Click BOLD links to see all specimens in a BIN
5. **Geographic patterns:** Color by geography to spot biogeographic clusters
6. **Bootstrap filtering:** Search for high-support nodes (>90%)
7. **Export views:** Use permalink feature to share specific views

---

## 📝 Notes on Duplicate Removal

During JSONL creation, 6 duplicate rows were found and removed:
- 2× Hemineurina_modesta|BOLDABY5735|GMGLM425-13
- 4× Scatopsciara_fritzi|BOLDACZ7992|SCINO499-15

These were artifacts from the metadata merge process. First occurrence kept for each.

---

**Ready to explore! Upload `sciaridae_taxonium.jsonl.gz` to https://taxonium.org** 🎉
