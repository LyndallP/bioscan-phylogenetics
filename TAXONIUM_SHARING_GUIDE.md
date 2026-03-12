# Taxonium Sharing and Custom Colors Guide

## 📤 How to Share Your Taxonium Tree

There are **3 ways** to share your Sciaridae tree with others:

### Option 1: Upload Files to Public URL (Recommended for Sharing)

**Requirements:**
- Host your files on a server that allows CORS (Cross-Origin Resource Sharing)
- Good options: Zenodo, Figshare, GitHub, Dropbox (public), Google Drive (public)

**Steps:**
1. Upload your files to a public location:
   - `sciaridae_tree.nwk` (or .nwk.gz)
   - `sciaridae_metadata_FINAL_UPLOAD.tsv` (or .tsv.gz)

2. Get the direct download URLs (important!)
   - **Zenodo**: Use the direct file link (ends in the filename)
   - **GitHub**: Use raw.githubusercontent.com links
   - **Figshare**: Use the direct download link
   - **Dropbox**: Change `?dl=0` to `?dl=1` at end of URL

3. Create your Taxonium URL:
   ```
   https://taxonium.org/?treeUrl=TREE_URL&metadataUrl=METADATA_URL
   ```

**Example:**
```
https://taxonium.org/?treeUrl=https://zenodo.org/record/12345/files/sciaridae_tree.nwk.gz&metadataUrl=https://zenodo.org/record/12345/files/sciaridae_metadata_FINAL_UPLOAD.tsv.gz
```

**✅ Benefits:**
- Anyone can click the link and view your tree
- No file downloads required
- Taxonium encodes the URL parameters so you can share searches and colors too!

---

### Option 2: Local Files (For Personal Use)

**Steps:**
1. Go to https://taxonium.org
2. Drag and drop your files:
   - `sciaridae_tree.nwk`
   - `sciaridae_metadata_FINAL_UPLOAD.tsv`
3. Explore!

**⚠️ Limitations:**
- Files must be downloaded by each user
- Cannot share a direct link
- Good for personal exploration

---

### Option 3: Deploy Your Own Taxonium Backend (Advanced)

For very large trees or institutional use, you can deploy a Taxonium backend server.

**Requirements:**
- Docker installed
- Your tree in JSONL format (convert with `newick_to_taxonium`)

**Quick Start:**
```bash
# Convert tree to JSONL format
pip install taxoniumtools
newick_to_taxonium \
  --input sciaridae_tree.nwk \
  --metadata sciaridae_metadata_FINAL_UPLOAD.tsv \
  --output sciaridae.jsonl.gz \
  --config_json taxonium_config_support_colors.json

# Run Docker backend
docker run -p 80:80 \
  -v "/path/to/sciaridae.jsonl.gz:/mnt/data/sciaridae.jsonl.gz" \
  -e "DATA_FILE=/mnt/data/sciaridae.jsonl.gz" \
  -e "CONFIG_JSON=taxonium_config_support_colors.json" \
  theosanderson/taxonium_backend:master

# Access at: http://localhost:80
# Or connect to Taxonium: https://taxonium.org?backend=http://localhost:80
```

---

## 🎨 Custom Colors for Node Support

### Method 1: URL Parameter (Quick & Easy)

Add color mapping directly to your URL:

```
https://taxonium.org/?treeUrl=YOUR_TREE_URL&metadataUrl=YOUR_METADATA_URL&config={"colorMapping":{"High (0.90-1.00)":[34,139,34],"Good (0.75-0.89)":[255,215,0],"Moderate to Low (0-0.74)":[255,69,0],"Novel placement":[138,43,226]}}
```

**Color Codes (RGB):**
- **High (0.90-1.00)**: `[34, 139, 34]` - Forest Green
- **Good (0.75-0.89)**: `[255, 215, 0]` - Gold
- **Moderate to Low (0-0.74)**: `[255, 69, 0]` - Red-Orange
- **Novel placement**: `[138, 43, 226]` - Blue-Violet
- **No support data**: `[128, 128, 128]` - Gray

---

### Method 2: Config JSON File (For JSONL Conversion)

Use the provided `taxonium_config_support_colors.json` when converting:

```bash
newick_to_taxonium \
  --input sciaridae_tree.nwk \
  --metadata sciaridae_metadata_FINAL_UPLOAD.tsv \
  --output sciaridae.jsonl.gz \
  --config_json taxonium_config_support_colors.json
```

**Config file contents:**
```json
{
  "colorMapping": {
    "High (0.90-1.00)": [34, 139, 34],
    "Good (0.75-0.89)": [255, 215, 0],
    "Moderate to Low (0-0.74)": [255, 69, 0],
    "Novel placement": [138, 43, 226],
    "No support data": [128, 128, 128]
  }
}
```

---

## 🔗 Complete Shareable Link Example

Here's a complete URL with custom colors and the tree colored by support:

```
https://taxonium.org/?treeUrl=https://zenodo.org/record/12345/files/sciaridae_tree.nwk.gz&metadataUrl=https://zenodo.org/record/12345/files/sciaridae_metadata_FINAL_UPLOAD.tsv.gz&config={"colorMapping":{"High (0.90-1.00)":[34,139,34],"Good (0.75-0.89)":[255,215,0],"Moderate to Low (0-0.74)":[255,69,0],"Novel placement":[138,43,226]}}&colorBy=Node%20support%20/%20Placement
```

**This URL:**
- ✅ Loads the tree and metadata from Zenodo
- ✅ Applies custom colors to support categories
- ✅ Automatically colors the tree by "Node support / Placement"
- ✅ Can be shared with anyone!

---

## 🎯 Best Practice Workflow

### For Public Sharing:

1. **Upload to Zenodo (Recommended)**
   - Get a DOI for your data
   - Permanent, citable storage
   - CORS enabled by default

2. **Create shareable link:**
   ```
   https://taxonium.org/?treeUrl=ZENODO_TREE_URL&metadataUrl=ZENODO_METADATA_URL&config={"colorMapping":{...}}&colorBy=Node%20support%20/%20Placement
   ```

3. **Share the link in:**
   - Your paper (supplementary materials)
   - GitHub README
   - Twitter/social media
   - Email to collaborators

### For GitHub README:

Add a nice button to your README:

```markdown
## 🌳 Explore the Sciaridae Phylogeny

[![Explore in Taxonium](https://img.shields.io/badge/Explore-Taxonium-green)](https://taxonium.org/?treeUrl=YOUR_URL&metadataUrl=YOUR_URL&config={...})

Click the button above to explore our interactive Sciaridae phylogenetic tree with:
- 1,156 specimens (346 BIOSCAN, 6 DTOL, 804 references)
- Bootstrap support for reference tree nodes
- EPA-ng LWR scores for placed specimens
- Clickable links to GBIF, BOLD, NBN Atlas, GOAT, and more
- Specimen images from BIOSCAN UK

**Color legend:**
- 🟢 High (0.90-1.00) - Strong phylogenetic support
- 🟡 Good (0.75-0.89) - Good support
- 🟠 Moderate to Low (0-0.74) - Review needed
- 🟣 Novel placement - Unique specimens
```

---

## 📋 URL Parameter Reference

| Parameter | Purpose | Example |
|-----------|---------|---------|
| `treeUrl` | Direct link to tree file | `https://zenodo.org/.../tree.nwk.gz` |
| `metadataUrl` | Direct link to metadata | `https://zenodo.org/.../metadata.tsv.gz` |
| `config` | Custom colors & settings | `{"colorMapping":{...}}` |
| `colorBy` | Auto-color by field | `Node%20support%20/%20Placement` |
| `search` | Pre-set search | `genus:Bradysia` |

---

## 🎨 Custom Color Reference

RGB color format: `[Red, Green, Blue]` where each value is 0-255

**Suggested color palettes:**

### Traffic Light (Current):
- High: `[34, 139, 34]` - Green
- Good: `[255, 215, 0]` - Gold  
- Low: `[255, 69, 0]` - Red-Orange

### Blue Scale:
- High: `[0, 0, 139]` - Dark Blue
- Good: `[30, 144, 255]` - Dodger Blue
- Low: `[173, 216, 230]` - Light Blue

### Viridis-inspired:
- High: `[68, 1, 84]` - Purple
- Good: `[59, 82, 139]` - Blue
- Low: `[33, 145, 140]` - Teal

**To change colors:**
1. Edit `taxonium_config_support_colors.json`
2. Replace RGB values
3. Re-upload or update URL parameter

---

## ✅ Final Checklist

Before sharing your tree:

- [ ] Files uploaded to CORS-enabled server (Zenodo/Figshare/GitHub)
- [ ] Direct download URLs obtained (not landing pages!)
- [ ] Config JSON created with custom colors
- [ ] Test the URL yourself first
- [ ] Add URL to paper/README/documentation
- [ ] Consider adding DOI from Zenodo for citability

---

## 🆘 Troubleshooting

**Problem:** Tree doesn't load
- ✅ Check URLs are direct download links (not landing pages)
- ✅ Verify CORS is enabled on your server
- ✅ Test files load in browser directly

**Problem:** Colors don't apply
- ✅ Check colorMapping matches metadata values exactly
- ✅ Use RGB format: `[R, G, B]`
- ✅ Ensure JSON is properly formatted (no trailing commas)

**Problem:** Can't share link
- ✅ Files must be on public server
- ✅ Use URL encoding for special characters (e.g., spaces = `%20`)

---

## 📚 Additional Resources

- **Taxonium Documentation**: https://docs.taxonium.org
- **Taxonium GitHub**: https://github.com/theosanderson/taxonium
- **Example Cov2Tree**: https://cov2tree.org (see their config for reference)

---

**Your tree is ready to share with the world! 🌳✨**
