# Metadata Improvements - February 22-23, 2026

## Summary
Comprehensive metadata cleanup and enhancement for Sciaridae phylogenetic tree visualization in Taxonium. Restored missing BIOSCAN metadata, added specimen images from Sanger system, improved readability with human-friendly labels, and created proper external links with icons.

## Complete Workflow

### Step 1: Metadata Restoration (346 BIOSCAN specimens)
**Problem:** 346 BIOSCAN specimens (30% of total) were missing critical metadata after merge operations.

**Script:** `restore_bioscan_metadata.py`

**Process:**
1. Extract BINs from tip names (format: `Species|BOLDXXXXXXX|ProcessID`)
2. Convert format: `BOLDXXXXXXX` → `BOLD:XXXXXXX` (metadata uses colon)
3. Create reference lookup dictionary indexed by BIN
4. Match specimens to references by BIN
5. Copy all metadata fields from reference specimens

**Results:**
- ✅ 323 fully restored (had reference specimens with same BIN)
- ✅ 23 partially restored as "Unidentified" (novel BINs without reference)
- ✅ 100% of BIOSCAN specimens now have complete metadata

**Verification:** `verify_restoration.py`

### Step 2: BIOSCAN Portal Links
**Script:** `add_bioscan_link.py`

**Purpose:** Add links to view all BIOSCAN specimens per BIN at Wellcome Sanger Institute

**Implementation:**
- URL format: `https://portal.boldsystems.org/result?query=BOLD:ACY6390[bin],%22Wellcome%20Sanger%20Institute%22[inst]`
- Proper URL encoding (%22 for quotes, %20 for spaces)
- Markdown format: `[All BIOSCAN specimens](URL)`
- Conditional: Only shows when `Bioscan specimen count > 0`

**Results:**
- Created 717 links (only for specimens with BIOSCAN count > 0)
- Not created for 439 specimens without BIOSCAN data

### Step 3: Metadata Streamlining
**Script:** `clean_metadata.py`

**Removed confusing/redundant columns:**
- ❌ `bags_grade` - Confusing (E and C both present for same specimen)
- ❌ `bin_quality_issue` - Verbose, redundant with bags_grade
- ❌ `n_bins_for_species` - Just a number, less useful than full list
- ❌ `needs_attention` - Can be derived from category
- ❌ `placement_quality` - Redundant with placement_interpretation

**Renamed for clarity:**
- `all_bins` → `other_bins_for_species`
- `bioscan_specimens` → `Bioscan specimen count`

**Output:** `sciaridae_metadata_CLEAN.tsv`

### Step 4: External Link Refinement
**Script:** `refine_metadata.py`

**Improvements:**
1. Renamed column headers for clarity
2. Made BIOSCAN link conditional (only if count > 0)
3. Renamed BOLD Specimen link text
4. Fixed DTOL links to use TOLQC format
5. Added GOAT links (conditional)
6. Improved GBIF links to go directly to species page
7. Reordered columns (genus before species)

**TOLQC URL format:** `https://tolqc.cog.sanger.ac.uk/darwin/insects/Species_name/`

**Output:** `sciaridae_metadata_REFINED.tsv`

### Step 5: Category Label Improvements
**Script:** `improve_metadata_simple.py`

**Old labels** (cryptic):
- `BIOSCAN_collected`
- `UKSI_no_specimens`
- `Not_in_UKSI`
- `Europe_reference`

**New labels** (human-readable):
- ✅ `In UKSI and BIOSCAN collected` (561 specimens)
- ✅ `In UKSI and not BIOSCAN collected` (382 specimens)
- ⚠️ `Not in UKSI and BIOSCAN collected` (179 specimens) - **needs attention**
- ℹ️ `Europe only (reference species)` (34 specimens)

**Added column:** `species_in_GOAT` (TRUE/FALSE)
- TRUE: 842 specimens (identified to species level, excluding "sp." designations)
- FALSE: 314 specimens (unidentified or genus-level only)

**Output:** `sciaridae_metadata_FINAL_v2.tsv`

### Step 6: Add Icons to Links
**Script:** `add_icons.py` (intermediate) → integrated into final workflow

**Icons added:**
- 🪰 **BOLD Specimen**: "This specimen"
- 🌍 **GBIF**: "GBIF map"
- 🐐 **GOAT**: "GOAT"
- 🔷 **BOLD BIN**: "BOLD BIN detail"
- 🌳 **TOLQC**: "TOLQC"
- 🇬🇧 **NBN**: (already had icon)
- 🧬 **BLAST**: (already had icon)

**Made all links conditional:**
- BOLD_BIOSCAN: Only when `Bioscan specimen count > 0` (717 specimens)
- GOAT: Only when `species_in_GOAT == TRUE` (842 specimens)
- GBIF: Only for identified species (993 specimens)
- TOLQC: Only for DTOL specimens (6 specimens)

**Output:** `sciaridae_metadata_FINAL_v3.tsv`

### Step 7: BIOSCAN Specimen Images (Critical!)
**Problem:** Need to add Sanger image thumbnails, but processid ≠ specimen ID

**Solution:** Match to original BIOSCAN data to get `sts_specimen.id`

**Why this is needed:**
- Tree tip names contain: `Species|BIN|ProcessID` (e.g., `HIRW1685-23`)
- ProcessID is the **BOLD identifier**
- Sanger images use: `sts_specimen.id` (e.g., `HIRW_001_G10`)
- Must match `bold_processid` → `sts_specimen.id` from original BIOSCAN data

**Script:** `add_bioscan_specimen_ids_LOCAL.py` ⭐ **MUST RUN LOCALLY**

**Process:**
1. Load original BIOSCAN data: `/Users/lp20/Desktop/Taxonium/UKBOL_bioscan_selected.tsv` (254MB)
2. Extract columns: `bold_processid`, `sts_specimen.id`
3. Create lookup dictionary: `bold_processid` → `sts_specimen.id`
4. Extract processid from tree tip names
5. Look up `sts_specimen.id` for each BIOSCAN specimen
6. Create Sanger image URLs: `https://tol-bioscan-images.cog.sanger.ac.uk/processed_images/{sts_specimen.id}.jpg`

**Columns added:**
- `sts_specimen.id` - Sanger specimen identifier (e.g., "HIRW_001_G10")
- `ThumbnailURL` - Sanger image URL (automatically displayed by Taxonium)

**Expected results:**
- ~334-346 BIOSCAN specimens will get `sts_specimen.id` values
- ~334-346 image URLs will be created
- Reference specimens (DTOL, Europe) will have empty ThumbnailURL

**Output:** `sciaridae_metadata_FINAL_WITH_IMAGES.tsv` (created locally by user)

## Files for GitHub Commit

### 📝 Documentation (4 files)
1. **CHANGELOG_2026-02-22.md** - This file - complete workflow documentation
2. **UNKNOWN_VS_UNIDENTIFIED.md** - Explains "Unknown_species" vs "Unidentified"
3. **category_guide.tsv** - Category meanings quick reference
4. **METADATA_RESTORATION_SUMMARY.md** - Detailed restoration documentation

### 🐍 Scripts (4 files)
5. **restore_bioscan_metadata.py** - Restore missing BIOSCAN metadata by BIN matching
6. **add_bioscan_link.py** - Add BIOSCAN portal links with proper URL encoding
7. **verify_restoration.py** - Verify restoration was successful
8. **add_bioscan_specimen_ids_LOCAL.py** ⭐ - Add specimen IDs and create image URLs (RUN LOCALLY)

### 📊 Metadata Files (1 file)
9. **sciaridae_metadata_FINAL_v3.tsv** - Final metadata ready for local image script

## Final Metadata Structure (28 columns → 30 after local script)

### Core Identification
1. `name` - Tree tip label
2. `genus` - Genus name
3. `species` - Species name
4. `ThumbnailURL` - Sanger image URL ⭐ (added by local script)

### Classification
5. `bin` - BOLD BIN code
6. `category` - Human-readable category label
7. `in_uksi` - On UK Species Inventory (TRUE/FALSE)
8. `geography` - Collection geography

### Placement Information
9. `placement_type` - reference/validation/novel
10. `placement_interpretation` - Detailed notes
11. `epa_lwr_score` - EPA-ng likelihood weight ratio
12. `other_bins_for_species` - List of other BINs for this species

### BIOSCAN Data
13. `Bioscan specimen count` - Number of specimens in BOLD database
14. `species_in_GOAT` - In GOAT database (TRUE/FALSE)

### External Links (all with icons, conditionally displayed)
15. `GBIF` - 🌍 GBIF map (993 links)
16. `BOLD_BIN` - 🔷 BOLD BIN detail (1,149 links)
17. `BOLD_Specimen` - 🪰 This specimen (1,133 links)
18. `BOLD_BIOSCAN` - All BIOSCAN specimens (717 links - conditional)
19. `GOAT` - 🐐 GOAT (842 links - conditional)
20. `NBN` - 🇬🇧 NBN Atlas (993 links)
21. `TOLQC` - 🌳 TOLQC (6 links - DTOL only)
22. `BLAST` - 🧬 NCBI BLAST (1,156 links)

### Technical Fields
23. `processid` - BOLD process ID
24. `sts_specimen.id` - Sanger specimen ID ⭐ (added by local script)
25. `parent_bootstrap` - Bootstrap support
26. `dataset` - BIOSCAN/Reference/DTOL
27. `tolid` - Tree of Life ID (DTOL only)
28. `assembly_status` - Genome assembly status (DTOL)
29. `genome_status` - Genome status (DTOL)
30. `family` - Family name

## Category Meanings

### In UKSI and BIOSCAN collected (561 specimens)
- ✅ Species IS on UK Species Inventory checklist
- ✅ Collected by BIOSCAN UK
- **Action:** None - expected UK species

### In UKSI and not BIOSCAN collected (382 specimens)
- ✅ Species IS on UK Species Inventory checklist
- ❌ NO BIOSCAN specimens (reference data only)
- **Purpose:** Phylogenetic context

### Not in UKSI and BIOSCAN collected (179 specimens) ⚠️
- ❌ Species NOT on UK Species Inventory checklist
- ✅ Collected by BIOSCAN UK
- **Action:** NEEDS VERIFICATION
- **Could be:**
  - New UK record (exciting!)
  - Misidentification (needs correction)
  - Non-native/introduced species
  - Vagrant (occasional visitor)
  - Taxonomic changes (species name updated)

### Europe only (reference species) (34 specimens)
- European reference specimens
- Not expected in UK
- **Purpose:** Phylogenetic context

## Key Technical Details

### BIN Format Conversion
- **Tip names:** `BOLDXXXXXXX` (no colon)
- **Metadata:** `BOLD:XXXXXXX` (with colon)
- Always convert when matching!

### Specimen ID vs ProcessID
- **ProcessID:** BOLD identifier (e.g., `HIRW1685-23`)
- **sts_specimen.id:** Sanger identifier (e.g., `HIRW_001_G10`)
- **Critical:** Sanger images use specimen ID, NOT processid!

### ThumbnailURL in Taxonium
- Column name: `ThumbnailURL` (case-sensitive!)
- Taxonium auto-detects and displays images
- URL itself is hidden from user interface
- Only the image appears in specimen panel

## Usage Instructions

### For Immediate Taxonium Upload (Without Images)
**Use:** `sciaridae_metadata_FINAL_v3.tsv`
- Has all improvements: icons, readable categories, conditional links
- Missing: Specimen images

### To Add BIOSCAN Specimen Images
**Required steps:**
1. Download `add_bioscan_specimen_ids_LOCAL.py` from GitHub
2. Download `sciaridae_metadata_FINAL_v3.tsv` to ~/Downloads/
3. Ensure BIOSCAN data at: `/Users/lp20/Desktop/Taxonium/UKBOL_bioscan_selected.tsv`
4. Run: `cd ~/Downloads && python3 add_bioscan_specimen_ids_LOCAL.py`
5. Output: `~/Downloads/sciaridae_metadata_FINAL_WITH_IMAGES.tsv`
6. Upload to Taxonium with tree

## Statistics

### Overall Coverage
- **Total specimens:** 1,156
- **BIOSCAN specimens:** 346 (will have images after local script)
- **Reference specimens:** 777
- **DTOL specimens:** 6

### Links Created (all conditional)
| Link Type | Count | Condition |
|-----------|-------|-----------|
| BOLD Specimen 🪰 | 1,133 | Has processid |
| GBIF map 🌍 | 993 | Identified species |
| GOAT 🐐 | 842 | In GOAT database |
| BOLD BIN detail 🔷 | 1,149 | Has BIN |
| All BIOSCAN specimens | 717 | Count > 0 |
| TOLQC 🌳 | 6 | DTOL only |
| NBN Atlas 🇬🇧 | 993 | Has species |
| BLAST 🧬 | 1,156 | All specimens |

### Metadata Completeness
- ✅ 100% have complete metadata (after restoration)
- ✅ 100% have readable category labels
- ✅ 100% have conditional external links
- ⏳ 30% will have images (after running local script)

## Important Notes

### Why Local Script is Required
- Original BIOSCAN file is 254MB (too large for cloud processing)
- Contains ~100,000+ specimens across all families
- Need to match `bold_processid` → `sts_specimen.id` from this file
- Script runs efficiently on local Mac (takes ~30 seconds)

### Image URL Format
```
https://tol-bioscan-images.cog.sanger.ac.uk/processed_images/HIRW_001_G10.jpg
```
- Uses `sts_specimen.id` NOT processid
- Format verified with Sanger developer (Andrew Varley)
- Images are processed and ready at this URL

### BOLD Images NOT Possible
- BOLD stores images in unpredictable cloud URLs
- Example: `https://caos.boldsystems.org/api/objects/caos-cloud.linode-us-ord-1.23_257.5527df04-fe4e-462e-9913-34a4a2cab421.jpg`
- Cannot generate programmatically from ProcessID
- Solution: Use Sanger BIOSCAN images instead ✅

## Next Steps After GitHub Commit

1. ✅ Clone repository
2. ✅ Run `add_bioscan_specimen_ids_LOCAL.py` to add images
3. ✅ Upload tree + metadata to Taxonium
4. ✅ Verify all links work
5. ✅ Verify images display correctly
6. ✅ Test search and filtering features
7. ✅ Share with collaborators!

## Lessons Learned

### Data Integration
- Always verify no data loss after merge operations
- Use left joins with explicit fill strategies
- Add diagnostic outputs (count records before/after)
- Create checkpoint files after major steps

### URL Encoding
- Use `urllib.parse.quote()` for proper encoding
- Test URLs in browser before committing
- Different APIs need different encoding strategies

### Column Naming
- Spaces in column names are OK for Taxonium
- Make labels human-readable, not code-friendly
- Icons in labels work great! 🎉

### File Size Management
- Git has limits (~100MB per file)
- Use Git LFS for large files if needed
- Keep raw data (254MB BIOSCAN file) outside repository
- Provide clear paths in scripts for local data

## Credits

- Metadata restoration: Automated BIN matching algorithm
- Category improvements: User feedback on readability
- Image integration: Sanger BIOSCAN team (Andrew Varley)
- Icon selection: Unicode emoji standards
- URL encoding: Python urllib.parse library
