# Sciaridae Metadata Update Summary

## ✅ All Updates Complete!

**New file created**: `sciaridae_metadata_UPDATED.tsv`
- **Total specimens**: 1,156 (unchanged)
- **Total columns**: 34 (was 32, added 2 new columns)

---

## 📋 Changes Made

### 1. ✅ **Category Column** - Split Unknown/Unidentified

**OLD categories** (4 total):
- In UKSI and BIOSCAN collected
- In UKSI and not BIOSCAN collected
- Not in UKSI and BIOSCAN collected (included Unknown + Unidentified)
- Europe only (reference species)

**NEW categories** (6 total):
- In UKSI and BIOSCAN collected: **561 specimens**
- In UKSI and not BIOSCAN collected: **382 specimens**
- **Unidentified (in BIOSCAN)**: **76 specimens** ⭐ NEW
- **Unknown (in reference, not BIOSCAN)**: **71 specimens** ⭐ NEW
- Europe only (reference species): **34 specimens**
- Not in UKSI and BIOSCAN collected: **32 specimens** (identified species only)

**Logic used:**
- Checks both `genus` column AND `name` column for "Unknown" or "Unidentified"
- "Unknown" → reference specimens
- "Unidentified" → BIOSCAN specimens

---

### 2. ✅ **BIN Column Renamed**

**OLD**: `other_bins_for_species`
**NEW**: `all_bins_for_species`

This better reflects that it includes the current BIN itself, not just "other" BINs.

---

### 3. ✅ **NEW Column: bin_status**

Added at position 11 (right after `all_bins_for_species`)

**Values**:
- **"Multiple BINs for species"**: 569 specimens
  - Species with more than one BIN (species-level taxonomic complexity)
  
- **"Clean species-BIN match"**: 458 specimens
  - Single BIN, single species (ideal 1:1 match)
  
- **"Multiple BINs for species; Other species share this BIN"**: 66 specimens
  - Both conditions true (complex taxonomic situation)
  
- **"Other species share this BIN"**: 63 specimens
  - Multiple species assigned to same BIN (possible misidentification or cryptic species)

**Logic**:
- Counts distinct species per BIN across entire dataset
- Counts BINs per species from `all_bins_for_species` field
- Combines both statuses when applicable (separated by semicolon)

---

### 4. ✅ **in_uksi Column** - Updated Values

**OLD** (2 values):
- TRUE
- FALSE

**NEW** (4 values):
- **True**: 872 specimens (identified species in UKSI)
- **Unknown in reference**: 142 specimens ⭐ NEW
- **Unidentified in BIOSCAN**: 96 specimens ⭐ NEW
- **False**: 36 specimens (identified species not in UKSI)

**Logic**: Same check as category (genus + name columns)

---

### 5. ✅ **NEW Column: geography_broad**

Added at position 15 (right after `geography`)

**Biogeographic regions** (12 total):

| Region | Count | Countries Included |
|--------|-------|-------------------|
| **British Isles** | 538 | United Kingdom |
| **Scandinavia** | 203 | Norway, Sweden, Denmark, Finland |
| **Western Europe** | 177 | Germany, France, Belgium, Switzerland, Austria |
| **North America** | 118 | Canada, United States, Puerto Rico, Greenland |
| **East Asia** | 43 | China, South Korea, Japan, Thailand, Vietnam, Cambodia, Bangladesh |
| **Eastern Europe** | 35 | Poland, Czechia, Bulgaria, Georgia |
| **Africa** | 10 | South Africa, Ghana |
| **Unknown** | 8 | Unknown |
| **Oceania** | 8 | Australia, New Zealand |
| **Southern Europe** | 7 | Portugal, Israel, Lebanon, Iran |
| **South America** | 5 | Colombia, Argentina, Costa Rica |
| **South Asia** | 4 | Pakistan |

---

## 📊 Column Summary

**Total: 34 columns** (in order):

1. name
2. genus
3. species
4. ThumbnailURL
5. bin
6. **category** ✏️ UPDATED
7. placement_type
8. placement_interpretation
9. epa_lwr_score
10. **all_bins_for_species** ✏️ RENAMED (was: other_bins_for_species)
11. **bin_status** ⭐ NEW
12. **in_uksi** ✏️ UPDATED
13. Bioscan specimen count
14. geography
15. **geography_broad** ⭐ NEW
16. GBIF
17. BOLD_BIN
18. BOLD_Specimen
19. BOLD_BIOSCAN
20. species_in_GOAT
21. GOAT
22. NBN
23. TOLQC
24. BLAST
25. processid
26. sts_specimen.id
27. parent_bootstrap
28. Node support / Placement
29. dataset
30. tolid
31. assembly_status
32. genome_status
33. family
34. subfamily

---

## 🎨 New Color Schemes Available

With these new columns, you can now create views colored by:

### **category** (6 colors)
- In UKSI and BIOSCAN collected
- In UKSI and not BIOSCAN collected
- Unidentified (in BIOSCAN)
- Unknown (in reference, not BIOSCAN)
- Europe only (reference species)
- Not in UKSI and BIOSCAN collected

### **bin_status** (4 colors)
- Clean species-BIN match (ideal!)
- Multiple BINs for species (taxonomic complexity)
- Other species share this BIN (possible issues)
- Both conditions (needs review)

### **in_uksi** (4 colors)
- True (in UKSI)
- False (not in UKSI)
- Unknown in reference
- Unidentified in BIOSCAN

### **geography_broad** (12 colors)
- British Isles, Scandinavia, Western Europe, etc.

---

## 🔍 Example Use Cases

### **Quality Control View**
Color by: `bin_status`
Preset search: "Other species share this BIN" (potential misidentifications)

### **Geographic Bioregions**
Color by: `geography_broad`
Preset searches for each major region

### **Taxonomic Status View**
Color by: `category`
Shows identified vs. unknown vs. unidentified at a glance

### **UKSI Coverage**
Color by: `in_uksi`
Highlights gaps in UK species inventory

---

## 📁 Files Created

1. **`sciaridae_metadata_UPDATED.tsv`** - Updated metadata (34 columns, 1,156 specimens)
2. **`update_metadata.py`** - Python script used to make updates (reproducible)
3. **`METADATA_UPDATE_SUMMARY.md`** - This document

---

## ✅ Verification

All changes verified:
- ✅ Unknown specimens correctly categorized (71 specimens)
- ✅ Unidentified specimens correctly categorized (76 specimens)
- ✅ BIN status correctly calculated (569 multi-BIN, 63 shared-BIN, 66 both)
- ✅ in_uksi values updated (142 Unknown, 96 Unidentified)
- ✅ Geography broad regions mapped (12 biogeographic regions)
- ✅ Column order logical (new columns next to related columns)
- ✅ All 1,156 specimens retained

---

## 🚀 Next Steps

**Ready to use!** You can now:

1. Fill out `CONFIG_TEMPLATE_FILL_THIS_OUT.md` with your desired tree views
2. I'll generate config files using the NEW metadata columns
3. Create multiple JSONL files, each showing different aspects of the data

**New view possibilities:**
- BIN quality control (color by `bin_status`)
- Biogeographic distribution (color by `geography_broad`)
- Taxonomic identification status (color by `category`)
- UKSI coverage gaps (color by `in_uksi`)

Let me know which views you want to create! 🌳
