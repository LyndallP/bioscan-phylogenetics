# CORRECT Git Commit Instructions - NO DATA FILES IN GIT

## ✅ Best Practice: Keep Data Files Outside Git

Data files (TSV files) should NOT be committed to Git because:
- They're large (1.3-1.7MB each)
- They change frequently
- Git is for code/scripts/documentation, not data
- Use Zenodo/Figshare/institutional repository for data

## Files to Commit (9 files - NO .tsv data files)

### 📝 Documentation (4 files)
```bash
git add CHANGELOG_COMPLETE.md
git add FINAL_COMMIT_INSTRUCTIONS.md
git add UNKNOWN_VS_UNIDENTIFIED.md
git add METADATA_RESTORATION_SUMMARY.md
```

### 🐍 Scripts (4 files)
```bash
git add restore_bioscan_metadata.py
git add add_bioscan_link.py
git add verify_restoration.py
git add add_bioscan_specimen_ids_LOCAL.py
```

### 📚 Small Reference File (1 file - only 366 bytes)
```bash
git add category_guide.tsv  # Tiny reference file, OK to include
```

## What to Do With Data Files

### Option 1: Upload to Zenodo/Figshare (Recommended)

1. **Create a data release:**
   - Upload `sciaridae_metadata_FINAL_WITH_IMAGES.tsv` to Zenodo
   - Get DOI (e.g., `10.5281/zenodo.12345678`)
   - Update README with download link

2. **In your README.md:**
   ```markdown
   ## Data Files
   
   Download the final metadata file:
   - **sciaridae_metadata_FINAL_WITH_IMAGES.tsv** (1.7MB)
     - DOI: 10.5281/zenodo.12345678
     - Direct link: [https://zenodo.org/...]
   
   This file contains:
   - 1,156 specimens with 30 columns
   - 346 BIOSCAN specimens with Sanger image URLs
   - All external links with icons
   - Ready for Taxonium upload
   ```

### Option 2: GitHub Releases (Good Alternative)

1. **Create a GitHub Release:**
   ```bash
   # After committing scripts/docs
   git tag -a v1.0.0 -m "Sciaridae metadata with BIOSCAN images"
   git push origin v1.0.0
   ```

2. **On GitHub:**
   - Go to "Releases"
   - Click "Create a new release"
   - Attach `sciaridae_metadata_FINAL_WITH_IMAGES.tsv` as binary asset
   - Users download from Releases page

### Option 3: Git LFS (If You Must Use Git)

Only if institutional policy requires Git:

```bash
# Install Git LFS
git lfs install

# Track TSV files
git lfs track "*.tsv"
git add .gitattributes

# Now add data files
git add sciaridae_metadata_FINAL_WITH_IMAGES.tsv
```

**Note:** GitHub has 1GB LFS limit for free accounts

## Recommended .gitignore

Create/update `.gitignore`:

```bash
cat > .gitignore << 'EOF'
# Large data files (host on Zenodo/Figshare instead)
*.tsv
!category_guide.tsv  # Exception: tiny reference file

# Except keep category guide (tiny)
# All other TSV files should be downloaded from data repository

# Original BIOSCAN data
UKBOL_bioscan_selected.tsv
*_bioscan_selected.tsv

# Intermediate files
*_CLEAN.tsv
*_REFINED.tsv
*_v2.tsv
*_RESTORED.tsv

# Python cache
__pycache__/
*.pyc
*.pyo

# OS files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes

# R files
.Rhistory
.RData
.Rproj.user

# Temporary files
*.tmp
*.log
EOF
```

## Correct Commit Command

```bash
cd ~/bioscan-phylogenetics

# Add documentation
git add CHANGELOG_COMPLETE.md
git add FINAL_COMMIT_INSTRUCTIONS.md
git add UNKNOWN_VS_UNIDENTIFIED.md
git add METADATA_RESTORATION_SUMMARY.md

# Add scripts
git add restore_bioscan_metadata.py
git add add_bioscan_link.py
git add verify_restoration.py
git add add_bioscan_specimen_ids_LOCAL.py

# Add small reference file only
git add category_guide.tsv

# Add .gitignore
git add .gitignore

# Commit
git commit -m "Add BIOSCAN image integration workflow and documentation

Scripts for metadata improvement:
- restore_bioscan_metadata.py - Restore 346 BIOSCAN specimens
- add_bioscan_link.py - Add BIOSCAN portal links
- verify_restoration.py - Validation and statistics
- add_bioscan_specimen_ids_LOCAL.py - Integrate Sanger images

Complete 7-step workflow:
1. Metadata restoration (346 specimens, 100% recovery)
2. BIOSCAN portal links (717 conditional links)
3. Metadata streamlining (removed 5 redundant columns)
4. External links with icons (🪰🌍🐐🔷🌳)
5. Readable category labels
6. Conditional link display
7. Sanger image integration via sts_specimen.id

Documentation:
- CHANGELOG_COMPLETE.md - Full workflow documentation
- UNKNOWN_VS_UNIDENTIFIED.md - Terminology explanation
- METADATA_RESTORATION_SUMMARY.md - Detailed restoration notes
- category_guide.tsv - Category reference (366 bytes)

Data files NOT included in Git:
- Download from [Zenodo DOI] or GitHub Releases
- sciaridae_metadata_FINAL_WITH_IMAGES.tsv (1.7MB)
  * 1,156 specimens, 30 columns
  * 346 BIOSCAN images with ThumbnailURL
  * 512 specimens with sts_specimen.id
  * Ready for Taxonium upload

See CHANGELOG_COMPLETE.md for complete documentation."

# Push
git push origin main
```

## Update Your README.md

Add this section to your README:

```markdown
## Data Files

Metadata files are hosted separately from Git due to size:

### Download Links

**Final Metadata (Ready for Taxonium):**
- `sciaridae_metadata_FINAL_WITH_IMAGES.tsv` (1.7MB)
  - [Download from Zenodo](DOI_LINK_HERE) or
  - [Download from GitHub Releases](RELEASE_LINK_HERE)

**Contains:**
- 1,156 specimens with 30 metadata columns
- 346 BIOSCAN specimens with Sanger image URLs
- 512 specimens with sts_specimen.id
- All external links with icons (🪰🌍🐐🔷🌳)
- Readable category labels
- Conditional link display

**Alternative (without images):**
- `sciaridae_metadata_FINAL_v3.tsv` (1.6MB)
  - Same as above but without image URLs
  - Run `add_bioscan_specimen_ids_LOCAL.py` to add images

## Usage

1. Download metadata file from link above
2. Upload to Taxonium with tree file
3. Images display automatically from ThumbnailURL column

## Reproducing Metadata

To regenerate the metadata from scratch:

```bash
# 1. Restore BIOSCAN metadata
python3 restore_bioscan_metadata.py

# 2. Add BIOSCAN portal links
python3 add_bioscan_link.py

# 3. Add images (requires UKBOL_bioscan_selected.tsv locally)
python3 add_bioscan_specimen_ids_LOCAL.py
```

See CHANGELOG_COMPLETE.md for detailed workflow.
```

## File Storage Recommendations

| File Type | Size | Storage | Version Control |
|-----------|------|---------|----------------|
| Scripts (.py) | <10KB | Git | ✅ Yes |
| Documentation (.md) | <50KB | Git | ✅ Yes |
| Small reference (category_guide.tsv) | 366B | Git | ✅ Yes |
| **Metadata (.tsv)** | **1.3-1.7MB** | **Zenodo/Figshare** | ❌ No |
| Original BIOSCAN data | 254MB | Local only | ❌ No |
| Tree files (.nwk) | <100KB | Git or Zenodo | ⚠️ Either |

## Summary

✅ **Commit to Git:**
- Scripts (4 files)
- Documentation (4 files)
- category_guide.tsv (tiny reference)

❌ **Do NOT commit to Git:**
- sciaridae_metadata_FINAL_WITH_IMAGES.tsv (1.7MB)
- sciaridae_metadata_FINAL_v3.tsv (1.6MB)
- Any other large TSV files

📦 **Host Elsewhere:**
- Zenodo (recommended - gets DOI)
- Figshare (alternative)
- GitHub Releases (OK for small datasets)
- Institutional repository

This keeps your Git repo clean, fast, and focused on code/documentation while making data properly citable! 🎉
