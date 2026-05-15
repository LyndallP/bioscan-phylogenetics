# Sharing Trees via Taxonium

Taxonium is an interactive phylogenetic tree viewer. Each family tree in this
project is pre-linked via the GitHub Pages index, but you can also share custom
URLs or run a local/private instance.

---

## Three ways to share a tree

### 1. Upload files to a public URL (recommended for sharing)

Host your Newick tree and metadata TSV on any CORS-enabled server, then
construct a Taxonium URL from the direct download links.

Good hosting options:
- **Zenodo** — permanent, citable, CORS enabled; get a DOI
- **Figshare** — similar to Zenodo
- **GitHub** — use `raw.githubusercontent.com` links
- **Dropbox** — change `?dl=0` to `?dl=1` in the share URL

Once files are hosted:
```
https://taxonium.org/?treeUrl=TREE_URL&metadataUrl=METADATA_URL
```

Example:
```
https://taxonium.org/?treeUrl=https://zenodo.org/record/12345/files/sciaridae_tree.nwk.gz&metadataUrl=https://zenodo.org/record/12345/files/sciaridae_metadata_FINAL.tsv.gz
```

Benefits: anyone clicks the link and explores immediately — no file downloads
required, and Taxonium encodes all URL parameters so searches and colour
settings can be shared too.

---

### 2. Local files (personal use only)

1. Go to [taxonium.org](https://taxonium.org)
2. Drag and drop your `{Family}_final_tree.newick` and
   `{family}_metadata_FINAL.tsv`
3. Explore interactively

Limitation: each user must download the files; no shareable link.

---

### 3. Self-hosted backend (advanced, large trees)

Convert the tree to JSONL format and run a Docker backend:

```bash
pip install taxoniumtools

newick_to_taxonium \
  --input {Family}_final_tree.newick \
  --metadata {family}_metadata_FINAL.tsv \
  --output {family}.jsonl.gz \
  --config_json config.json

docker run -p 80:80 \
  -v "/path/to/{family}.jsonl.gz:/mnt/data/{family}.jsonl.gz" \
  -e "DATA_FILE=/mnt/data/{family}.jsonl.gz" \
  theosanderson/taxonium_backend:master
```

Then connect Taxonium to your backend:
```
https://taxonium.org?backend=http://localhost:80
```

---

## URL parameter reference

| Parameter | Purpose | Example |
|-----------|---------|---------|
| `treeUrl` | Direct link to tree file (`.nwk` or `.nwk.gz`) | `https://zenodo.org/.../tree.nwk.gz` |
| `metadataUrl` | Direct link to metadata TSV (`.tsv` or `.tsv.gz`) | `https://zenodo.org/.../metadata.tsv.gz` |
| `colorBy` | Auto-colour on load by this metadata field | `Node%20support%20/%20Placement` |
| `search` | Pre-set a search | `genus:Bradysia` |

---

## Colour mapping for placement quality

The `Node support / Placement` metadata column uses these values (defined in
`scripts/finalize_metadata.py`):

| Value | Meaning | Suggested RGB |
|-------|---------|---------------|
| `High (0.90–1.00)` | Strong bootstrap or LWR support | `[34, 139, 34]` — forest green |
| `Moderate (0.75–0.89)` | Moderate support | `[255, 215, 0]` — gold |
| `Low (0–0.74)` | Weak support | `[255, 69, 0]` — red-orange |
| `Novel placement` | BIN not represented in reference tree | `[138, 43, 226]` — violet |

To apply colours via URL, append a `config` parameter (JSON-encoded):
```
&config={"colorMapping":{"High (0.90-1.00)":[34,139,34],"Moderate (0.75-0.89)":[255,215,0],"Low (0-0.74)":[255,69,0],"Novel placement":[138,43,226]}}
```

The `config.json` at the repository root contains the same mapping and is used
by `newick_to_taxonium` when converting to JSONL.

---

## Troubleshooting

**Tree does not load**
- Confirm the URL is a direct download link, not a landing page
- Verify CORS is enabled on the hosting server (Zenodo/GitHub are fine; some
  institutional servers block CORS)

**Colours do not apply**
- The `colorMapping` keys must match the metadata values exactly (including
  spaces and em-dashes)
- Use RGB format: `[R, G, B]`

**Cannot share a link**
- Files must be on a publicly accessible server
- Encode spaces and special characters in URL parameters (`%20` for space)

---

## Resources

- [Taxonium documentation](https://docs.taxonium.org)
- [Taxonium GitHub](https://github.com/theosanderson/taxonium)
