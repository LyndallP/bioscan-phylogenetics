# BIOSCAN Phylogenetics Pipeline — Step-by-Step Guide

Complete pipeline for placing UK BIOSCAN specimens onto BGE reference trees
and producing an annotated metadata file for Taxonium visualisation.

---

## Required inputs

| File | Source | Notes |
|------|--------|-------|
| `{Family}.treefile` | BGE reference repo | Newick with bootstrap values; tips `Species\|BIN\|ProcessID` |
| `{Family}_aligned.fasta` | BGE reference repo | MAFFT-aligned COI reference sequences |
| `bioscan_{family}.fasta` | UK BIOSCAN data | BIOSCAN query sequences |
| `filtered_gap_analysis.csv` | UKSI (full arthropod) | Must contain columns `taxon_name` and `species_status` |
| DTOL FASTA files (optional) | Darwin Tree of Life | COI reads per specimen; only needed if adding DTOL sequences |

Set environment variable before running R scripts:
```bash
export BOLD_API_KEY="your_key_here"
```

---

## Pipeline steps

### Step 1 — Prepare the reference tree

Remove outgroup sequences from the reference tree (tips prefixed `OUTGROUP`).

```bash
python scripts/02_tree_preparation.py \
    families/{Family}/input/{Family}.treefile \
    families/{Family}/input/{Family}_no_outgroup.treefile
```

---

### Step 2 — Clean the reference alignment

Removes outgroup sequences, uppercases all bases, and replaces any non-ATCGN
characters with `N`. This prevents MAFFT "Illegal character" errors.

```bash
python scripts/03_clean_alignment.py \
    families/{Family}/input/{Family}_aligned.fasta \
    families/{Family}/input/{Family}_aligned_clean.fasta
```

---

### Step 3 — Select best BIOSCAN representative per BIN

Picks the highest-quality sequence per BIN (score = `seq_length − ambiguous×10`).
Classifies each BIN as `validation` (BIN in reference tree) or `novel` (new BIN).

```bash
python scripts/06_select_bin_representatives.py \
    bioscan_{family}.fasta \
    families/{Family}/input/{Family}_no_outgroup.treefile \
    families/{Family}/input/bioscan_representatives.fasta
```

---

### Step 4 (optional) — Add DTOL sequences

Extract COI from DTOL read files and add to query set.

```bash
python scripts/extract_dtol_coi.py \
    --reads-dir /path/to/dtol_reads/ \
    --reference families/{Family}/input/{Family}_aligned_clean.fasta \
    --output families/{Family}/input/dtol_{family}.fasta
```

Merge with BIOSCAN representatives if using DTOL:
```bash
cat families/{Family}/input/bioscan_representatives.fasta \
    families/{Family}/input/dtol_{family}.fasta \
    > families/{Family}/input/query_sequences.fasta
```

Otherwise use bioscan_representatives.fasta directly as query_sequences.fasta.

---

### Step 4b — Align query sequences to reference alignment (required)

EPA-ng v0.3.8 requires query sequences pre-aligned to the exact same column
width as the reference alignment. Use MAFFT `--add --keeplength` to insert
query sequences into the existing alignment without altering its column
structure, then extract just the query sequences with a Python one-liner:

```bash
# Add query sequences to reference alignment (keeps reference column width)
mafft --add families/{Family}/input/query_sequences.fasta \
      --keeplength \
      families/{Family}/input/{Family}_aligned_clean.fasta \
      > families/{Family}/input/temp_combined_aligned.fasta

# Extract only the query sequences from the combined output
python3 -c "
import os
from Bio import SeqIO
fam = os.environ['FAM']
qids = {r.id for r in SeqIO.parse(f'families/{fam}/input/query_sequences.fasta', 'fasta')}
count = 0
with open(f'families/{fam}/input/query_sequences_aligned.fasta', 'w') as out:
    for r in SeqIO.parse(f'families/{fam}/input/temp_combined_aligned.fasta', 'fasta'):
        if r.id in qids:
            out.write(f'>{r.description}\n{str(r.seq)}\n')
            count += 1
print(f'Extracted {count} sequences')
"
```

Notes:
- hmmalign is not suitable: it outputs only model match-state columns (~657)
  rather than the full reference alignment width (~950), causing EPA-ng to
  abort with a column mismatch error.
- `mafft --addfragments` is not suitable: it segfaults on macOS (miniforge)
  for inputs of this size.

---

### Step 4c — Normalize BOLD BIN identifiers (required)

IQ-TREE drops the colon from `BOLD:ACP1705` → `BOLDACP1705` in tree tip
labels, while FASTA files retain the colon. EPA-ng requires an exact match
between tree tips and alignment IDs, so normalize all three files:

```bash
python scripts/normalize_ids.py \
    families/{Family}/input/{Family}_aligned_clean.fasta \
    families/{Family}/input/{Family}_aligned_clean_norm.fasta

python scripts/normalize_ids.py \
    families/{Family}/input/{Family}_no_outgroup.treefile \
    families/{Family}/input/{Family}_no_outgroup_norm.treefile

python scripts/normalize_ids.py \
    families/{Family}/input/query_sequences_aligned.fasta \
    families/{Family}/input/query_sequences_aligned_norm.fasta
```

---

### Step 5 — Place query sequences with EPA-ng

Use the normalized files. Pass `--model GTR+G` explicitly (required when
providing pre-aligned query sequences):

```bash
epa-ng \
    --tree families/{Family}/input/{Family}_no_outgroup_norm.treefile \
    --ref-msa families/{Family}/input/{Family}_aligned_clean_norm.fasta \
    --query families/{Family}/input/query_sequences_aligned_norm.fasta \
    --outdir families/{Family}/epa_output/ \
    --model GTR+G \
    --redo
```

Note: `--model GTR+G` uses generic unoptimized parameters. For better accuracy,
evaluate model parameters with RAxML (`raxmlHPC -f e`) or IQ-TREE
(`iqtree2 -te`) and pass the resulting model file to `--model`.

Outputs: `epa_result.jplace`, `epa_info.log`

---

### Step 6 — Graft placements onto tree with gappa

```bash
gappa examine graft \
    --jplace-path families/{Family}/epa_output/epa_result.jplace \
    --allow-file-overwriting \
    --out-dir families/{Family}/epa_output/
```

Rename output to a consistent name (gappa names the file after the jplace, so
it will be `epa_result.newick`):
```bash
mv families/{Family}/epa_output/epa_result.newick \
   families/{Family}/output/{Family}_final_tree.newick
```

---

### Step 7 — Create base metadata

Reads the grafted tree and jplace file. Assigns `placement_type` (`reference_tree` /
`validation` / `novel` / `dtol` / `polytomy`), LWR score, placement quality, and
extracts `parent_bootstrap` from the reference tree's internal node confidence values.

```bash
python scripts/create_fullplacement_metadata_FINAL.py \
    families/{Family}/output/{family}_final_tree.newick \
    families/{Family}/epa_output/epa_result.jplace \
    families/{Family}/output/metadata_01_base.tsv
```

---

### Step 8 — Add DTOL enrichment (assembly status, tolid, dataset)

Adds `dataset` (`BIOSCAN` / `DTOL` / `Reference`), `tolid`, `assembly_status`,
and `genome_status` columns. For non-DTOL runs this still sets `dataset` correctly.

```bash
python scripts/add_enhanced_metadata.py \
    families/{Family}/output/metadata_01_base.tsv \
    families/{Family}/output/metadata_02_enhanced.tsv
```

---

### Step 9 — Fetch BOLD country data

Pulls `country_ocean` and `province_state` for all process IDs via BOLDconnectR.
Reads process IDs from the metadata file. Outputs a TSV used in step 10.

```bash
Rscript scripts/fetch_bold_countries.R \
    families/{Family}/output/metadata_02_enhanced.tsv \
    families/{Family}/output/bold_countries.tsv
```

---

### Step 10 — Filter UKSI gap analysis to family

Filters the full arthropod gap analysis CSV to the target family.

```bash
# List available families in the CSV
python scripts/filter_uksi_by_family.py filtered_gap_analysis.csv --list-families

# Filter to target family
python scripts/filter_uksi_by_family.py \
    filtered_gap_analysis.csv \
    families/{Family}/input/{family}_gap_analysis.csv \
    --family {Family}
```

---

### Step 11 — Integrate country data and UKSI membership

Merges BOLD country data, assigns `geography` per row, and sets `in_uksi`.
Preserves all existing columns from step 8.

```bash
python scripts/integrate_country_metadata.py \
    --metadata families/{Family}/output/metadata_02_enhanced.tsv \
    --bold-countries families/{Family}/output/bold_countries.tsv \
    --uksi families/{Family}/input/{family}_gap_analysis.csv \
    --output families/{Family}/output/metadata_03_country.tsv
```

---

### Step 11b — Add BAGS metadata from gap analysis

Populates `bags_grade`, `bin_quality_issue`, `n_bins_for_species`, `all_bins`,
`needs_attention`, and new `synonym` column by matching each row to the gap
analysis CSV. Matching priority: BIN → taxon_name → synonym.

```bash
python scripts/add_bags_metadata.py \
    families/{Family}/output/metadata_03_country.tsv \
    families/{Family}/input/{family}_gap_analysis.csv \
    families/{Family}/output/metadata_03b_bags.tsv
```

---

### Step 12 — Add BIOSCAN specimen IDs and thumbnails

Extracts process IDs from the `name` column and queries the BOLD CAOS API
for specimen images. Writes `ThumbnailURL` (renders in Taxonium).

```bash
python scripts/add_bioscan_specimen_ids_LOCAL.py \
    families/{Family}/output/metadata_03b_bags.tsv \
    families/{Family}/output/metadata_04_thumbnails.tsv
```

---

### Step 13 (Sciaridae only) — Add subfamily

Assigns subfamily from genus using the Sciaridae-specific lookup table.
Also derives `genus` from the first word of `species` if not already present.

```bash
python families/Sciaridae/scripts/add_subfamily.py \
    families/Sciaridae/output/metadata_04_thumbnails.tsv \
    families/Sciaridae/output/metadata_05_subfamily.tsv
```

For other families, skip or provide an equivalent script.

---

### Step 14 — Add external links, geography_broad, and family

Creates `geography_broad` (country → biogeographic region), checks `species_in_GOAT`
via the GOAT API, and generates markdown link columns for all external databases.
Also renames `all_bins` → `all_bins_for_species` and `bioscan_specimens` →
`Bioscan specimen count`. Adds `family` column.

Use `--skip-goat` to skip the API calls (faster; sets `species_in_GOAT=False`).

```bash
python scripts/add_external_links.py \
    families/{Family}/output/metadata_05_subfamily.tsv \
    families/{Family}/output/metadata_06_links.tsv \
    --family {Family} \
    --skip-goat
```

The bioscan CSV is auto-detected at `families/{Family}/input/bioscan_{family}.csv`.
Remove `--skip-goat` if you want GOAT API lookups (slower; requires internet).

---

### Step 15 — Finalize: Node support / Placement column

Adds `Node support / Placement` (text category for Taxonium colouring) from
`parent_bootstrap` (reference tree nodes) and `epa_lwr_score` (placed specimens).
Removes the redundant `bootstrap_support` column if present.

```bash
python scripts/finalize_metadata.py \
    families/{Family}/output/metadata_06_links.tsv \
    families/{Family}/output/{family}_metadata_FINAL.tsv
```

---

## Output columns (target schema)

| Column | Source step | Notes |
|--------|-------------|-------|
| `name` | 7 | Tip label from tree |
| `genus` | 13 | First word of species (Sciaridae) or equivalent |
| `species` | 7 | Parsed from tip label |
| `ThumbnailURL` | 12 | BOLD CAOS API image URL |
| `bin` | 7 | BOLD BIN identifier |
| `category` | 15 | `BIOSCAN_collected`, `Not_in_UKSI`, `UKSI_no_specimens`, `Europe_reference`, `DTOL` — computed in finalize from `in_uksi` + `Bioscan specimen count` |
| `placement_type` | 7 | `reference_tree` / `validation` / `novel` / `dtol` / `polytomy` |
| `placement_interpretation` | 7 | Placeholder — populated manually post-analysis |
| `epa_lwr_score` | 7 | EPA-ng likelihood weight ratio (placed specimens only) |
| `bags_grade` | 11b | BAGS quality grade (A/B/C/D/E) from gap analysis |
| `bin_quality_issue` | 11b | Derived from bags_grade: `clean`, `split_across_N_BINs`, `shares_BIN_with_other_species` |
| `n_bins_for_species` | 11b | Number of BINs for this species in the gap analysis |
| `all_bins_for_species` | 11b/14 | All BINs for the species; renamed from `all_bins` in step 14 |
| `needs_attention` | 15 | True if category==Not_in_UKSI or placement_quality==Low; computed last so all columns are available |
| `UKSI_name_match` | 11b | How the species matched: `''`=BIN match, `accepted`=taxon_name, `synonym`=synonyms column, `other name`=other_names column |
| `taxon_version_key` | 11b | UKSI taxon_version_key from the matched gap analysis row |
| `in_uksi` | 11 | Bool — species in UKSI gap analysis |
| `Bioscan specimen count` | 14 | Renamed from `bioscan_specimens` |
| `geography` | 11 | Country from BOLD country data |
| `geography_broad` | 14 | Biogeographic region (e.g. British Isles, Scandinavia) |
| `GBIF` | 14 | Markdown link to GBIF species search |
| `BOLD_BIN` | 14 | Markdown link to BOLD BIN cluster page |
| `BOLD_Specimen` | 14 | Markdown link to BOLD specimen record |
| `BOLD_BIOSCAN` | 14 | Markdown link to all BIOSCAN specimens for BIN |
| `species_in_GOAT` | 14 | Bool — species found in GOAT |
| `GOAT` | 14 | Markdown link to GOAT taxon page |
| `NBN` | 14 | Markdown link to NBN Atlas species page |
| `TOLQC` | 14 | Markdown link to TOLQC page (DTOL only) |
| `BLAST` | 14 | Markdown link to NCBI BLAST search |
| `processid` | 11/12 | BOLD process ID |
| `parent_bootstrap` | 7 | Bootstrap value of parent node (reference tree tips) |
| `Node support / Placement` | 15 | Text category for Taxonium colouring |
| `dataset` | 8 | `BIOSCAN` / `DTOL` / `Reference` |
| `tolid` | 8 | Darwin Tree of Life specimen ID (DTOL only) |
| `assembly_status` | 8 | Genome assembly status (DTOL only) |
| `genome_status` | 8 | Genome status (DTOL only) |
| `family` | 14 | Family name (from `--family` argument) |
| `subfamily` | 13 | Subfamily (Sciaridae-specific; extend for other families) |

**Columns dropped during audit:**
- `sts_specimen.id` — Sanger-internal ID, replaced by BOLD CAOS API thumbnails
- `bootstrap_support` — intermediate column removed by step 15 (`finalize_metadata.py`)

---

## Data file not in repo

`filtered_gap_analysis.csv` — Full arthropod UKSI gap analysis (too large for git).
Must be provided by the user. Required columns: `taxon_name`, `species_status`, and
a family column (auto-detected from `family`, `Family`, `FAMILY`, `taxon_family`).

---

## Adding a new family

1. Create `families/{NewFamily}/` directory structure (copy from `families/template/`)
2. Place BGE reference tree and alignment in `families/{NewFamily}/input/`
3. Run steps 1–2 to prepare tree and alignment
4. Obtain BIOSCAN sequences for the family; run steps 3–15
5. Step 13 (subfamily) requires a family-specific lookup table — either adapt
   `families/Sciaridae/scripts/add_subfamily.py` or skip if subfamily is not needed
