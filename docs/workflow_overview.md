# UK Sciaridae Phylogenetic Analysis - Complete Workflow

## 📊 INPUT DATA SOURCES

### From BGE (European Reference Dataset)

1. **{FAMILY}.treefile** 
   - Phylogenetic tree with support values
   - Newick format with bootstrap values at nodes
   - Tip format: `Species_name|BIN|ProcessID`
   - Includes outgroup taxa

2. **{FAMILY}_aligned.fasta**
   - Pre-aligned COI sequences
   - Reference alignment for phylogenetic placement
   - MAFFT-aligned, quality checked

3. **tree_metadata.json**
   - Species-level BAGS quality grades
   - Grade counts and distributions
   - Monophyly analysis results

4. **curation_data.json**
   - Detailed BIN quality information per species
   - Species-BIN relationships
   - Grade assignments with justifications
   - BIN sharing information

### From UK Data

1. **{family}_bioscan.csv**
   - BIOSCAN UK specimen records
   - Columns needed:
     - `bold_processid`: BOLD process ID
     - `bold_bin_uri`: BIN identifier (format: `BOLD:AAA1234`)
     - `bold_class`, `bold_order`, `bold_family`: Taxonomy
     - `bold_genus`, `bold_species`: Species identification
     - `sts_COUNTRY_OF_COLLECTION`: Collection country
     - `sts_collection_locality`: Specific location
     - Additional collection metadata

2. **{family}_uksi.csv**
   - UK Species Inventory data
   - Columns needed:
     - `species_binomial`: Species name
     - `genus`: Genus name
     - `bin_uri_clean`: BIN identifier (if available)
     - `name_status`: Taxonomic status
     - `name_valid`: Boolean flag

---

## 🔬 STEP-BY-STEP WORKFLOW

### STEP 0: Environment Setup

**Install Required Software:**
```bash
# Create conda environment
conda create -n phylo -c bioconda raxml-ng epa-ng gappa python=3.9
conda activate phylo

# Install Python packages
pip install pandas ete3
```

**Prepare Directory Structure:**
```bash
cd families/{FAMILY}
mkdir -p data/input/{reference,bioscan,uksi}
mkdir -p data/output
mkdir -p logs
```

**Place Input Files:**
- Reference files → `data/input/reference/`
- BIOSCAN data → `data/input/bioscan/`
- UKSI data → `data/input/uksi/`

---

### STEP 1: Identify Sequences Needing Placement

**Goal:** Find UK BIOSCAN specimens not represented in European reference tree

**Method:**
```python
# Extract BINs from reference tree
tree_bins = extract_bins_from_tree(treefile)

# Extract BINs from BIOSCAN data
bioscan_bins = extract_bins_from_bioscan(bioscan_csv)

# Find BINs in BIOSCAN but not in tree
missing_bins = bioscan_bins - tree_bins
```

**Output:** List of BINs requiring phylogenetic placement

**Example Results (Sciaridae):**
- BIOSCAN BINs: 395
- Reference tree BINs: 588
- Missing BINs: 23 (need EPA-ng placement)

---

### STEP 2: Format Standardization

**Challenge:** Multiple format inconsistencies prevent EPA-ng from running

**2.1 Clean Alignment Headers**

**Problem:** Alignment has extra taxonomic information
```
>Species|BIN|ProcessID Ingroup|Genus_Species|Family
```

**Solution:**
```bash
sed 's/ Ingroup|.*$//' {FAMILY}_aligned.fasta > {FAMILY}_aligned_clean.fasta
```

**Result:**
```
>Species|BIN|ProcessID
```

**2.2 Remove Outgroups from Tree**

**Problem:** Outgroup taxa in tree but not in alignment

**Solution (using ete3):**
```python
from ete3 import Tree

# Load tree
tree = Tree("input.treefile", format=1)

# Find outgroup tips
outgroup_tips = [tip for tip in tree if tip.name.startswith("OUTGROUP")]

# Remove outgroups
tree.prune([tip for tip in tree if not tip.name.startswith("OUTGROUP")])

# Save cleaned tree
tree.write(format=1, outfile="output_ingroup.treefile")
```

**2.3 Standardize BIN Format**

**Problem:** Query sequences missing colons in BINs
- BIOSCAN format: `BOLD:ACU8309`
- Query format: `BOLDACU8309`

**Solution:**
```python
# Add colon after "BOLD" prefix
if bin_code.startswith('BOLD') and ':' not in bin_code:
    bin_uri = 'BOLD:' + bin_code[4:]
```

---

### STEP 3: Model Optimization

**Goal:** Optimize evolutionary model parameters on reference tree

**Why:** EPA-ng requires optimized GTR+G model parameters for accurate placement

**Method:**
```bash
raxml-ng --evaluate \
  --msa {FAMILY}_aligned_clean.fasta \
  --tree {FAMILY}_ingroup.treefile \
  --model GTR+G \
  --prefix {FAMILY}_model \
  --threads 2
```

**Output:** `{FAMILY}_model.raxml.bestModel`

Contains:
- Optimized substitution rates
- Base frequencies
- Gamma shape parameter (α)

**Example Output:**
```
Rate heterogeneity: GAMMA (4 cats, mean), alpha: 0.387161
Base frequencies (ML): 0.321329 0.185878 0.063396 0.429396
Substitution rates (ML): 0.679732 11.460511 1.510622 2.048009 7.033835 1.000000
```

**Time:** ~10-30 seconds (depending on tree size)

---

### STEP 4: EPA-ng Phylogenetic Placement

**Goal:** Place UK specimens onto European reference tree

**Why EPA-ng vs. Rebuilding Tree:**
- **Speed**: Minutes vs. hours
- **Preserves curation**: Keeps Benjamin's expert topology
- **Confidence metrics**: Provides LWR scores
- **Scalability**: Easy to add new specimens

**Method:**
```bash
epa-ng \
  --ref-msa {FAMILY}_aligned_clean.fasta \
  --tree {FAMILY}_ingroup.treefile \
  --query {FAMILY}_query_clean.fasta \
  --model {FAMILY}_model.raxml.bestModel \
  --outdir epa_results \
  --redo
```

**How EPA-ng Works:**
1. For each query sequence:
   - Tests placement at every branch in reference tree
   - Calculates likelihood for each position
   - Returns most likely placement(s)

2. Outputs:
   - Best placement position
   - **LWR (Like Weight Ratio)**: Confidence score
   - Alternative placements if ambiguous

**Interpreting LWR Scores:**

| LWR Score | Confidence | Interpretation | Action |
|-----------|------------|----------------|--------|
| ≥0.75 | High | Clear phylogenetic signal | Trust placement |
| 0.50-0.75 | Moderate | Some uncertainty | Acceptable but flag for review |
| <0.50 | Low | High uncertainty | Investigate: contamination, novel lineage, poor quality |

**Example Results (Sciaridae):**
- High confidence (≥0.75): 14 sequences
- Moderate (0.50-0.75): 3 sequences
- Low (<0.50): 6 sequences → Requires investigation

**Time:** Seconds to minutes (depends on query size)

---

### STEP 5: Tree Grafting

**Goal:** Create single tree with reference + placed sequences

**Method:**
```bash
gappa examine graft \
  --jplace-path epa_results/epa_result.jplace \
  --out-dir gappa_output \
  --name-prefix ""
```

**What gappa does:**
- Reads `.jplace` file (EPA-ng output)
- Inserts query sequences at their placement positions
- Creates standard Newick tree file

**Output:** `gappa_output/epa_result.newick`

**Result (Sciaridae):**
- 802 reference sequences
- +23 placed sequences
- = 825 total tips (before polytomy addition)

---

### STEP 6: Add Polytomy for Species Without Molecular Data

**Goal:** Include UKSI species lacking BIN/sequence data

**Why:** Complete taxonomic coverage for UK fauna

**Method:**
```python
from ete3 import Tree

# Load tree
tree = Tree("combined_tree.newick", format=1)

# Find appropriate genus clade
genus_tips = [leaf for leaf in tree if genus_name in leaf.name]

if genus_tips:
    # Get parent node (genus level)
    genus_node = genus_tips[0].up
    
    # Add new tip with zero branch length
    genus_node.add_child(
        name=f"{species_name}|no_BIN|polytomy",
        dist=0.0
    )
```

**Example (Sciaridae):**
- Species: *Xylosciara betulae* (in UKSI but no BIN)
- Placement: Added to *Xylosciara* genus clade
- Branch length: 0.0 (polytomy)
- Label: `Xylosciara_betulae|no_BIN|polytomy`

**Final Tree Size (Sciaridae):** 829 tips
- 802 reference
- 23 EPA-ng
- 3 outgroup
- 1 polytomy

---

### STEP 7: Comprehensive Metadata Integration

**Goal:** Create rich metadata for Taxonium visualization

**7.1 Data Sources to Integrate:**

1. **BIN Quality Grades** (from curation_data.json)
2. **BIOSCAN Specimen Counts** (from bioscan.csv)
3. **UKSI Membership** (from uksi.csv)
4. **BIN Sharing Information** (from curation_data.json)
5. **Species BIN Splitting** (from curation_data.json)
6. **Placement Quality** (from EPA-ng LWR scores)

**7.2 Matching Strategy:**

**CRITICAL: Match by BIN first, then species name**
```python
# Build BIN-level lookup (PRIMARY)
bin_info = {}  # BIN → {grade, species_list, issue}

# Build species-level lookup (FALLBACK)
species_info = {}  # species → {grade, n_bins, bin_list}

# For each tree tip, try:
def get_grade(row):
    # Try BIN first
    if row['bold_bin_uri'] in bin_info:
        return bin_info[row['bold_bin_uri']]['grade']
    # Fall back to species name
    species_clean = row['species'].replace('_', ' ')
    if species_clean in species_info:
        return species_info[species_clean]['grade']
    return 'Unknown'
```

**Why BIN-first?**
- Reference tree has many "Unidentified" or "sp." entries
- These can't match by species name
- But their BINs may have grade data

**7.3 Category Assignment:**
```python
def assign_category(row):
    if row['placement_method'] == 'reference_tree':
        if row['bioscan_specimens'] > 0:
            return 'BIN_collected_in_BIOSCAN'
        else:
            return 'Europe_reference'
    else:  # EPA-ng placements
        if row['bioscan_specimens'] > 0:
            if row['in_uksi']:
                return 'BIN_collected_in_BIOSCAN'
            else:
                return 'Not_in_UKSI'  # ATTENTION NEEDED!
        else:
            if row['in_uksi']:
                return 'UKSI_no_specimens'
            else:
                return 'Not_in_UKSI'
```

**Categories:**
- `BIN_collected_in_BIOSCAN`: UK specimens exist
- `Europe_reference`: No UK specimens
- `Not_in_UKSI`: Has specimens but not in UK species list → **Investigate!**
- `UKSI_no_specimens`: Known from UK but no specimens

**7.4 Attention Flags:**
```python
metadata['needs_attention'] = (
    (metadata['category'] == 'Not_in_UKSI') & 
    (metadata['bioscan_specimens'] > 0)
)
```

**What needs attention:**
- Species with UK specimens but NOT in UKSI
- Could be: new records, cryptic species, misidentifications, recent colonizers

**7.5 BIN Quality Descriptions:**
```python
def describe_bin_issue(row):
    if row['bags_grade'] == 'C':
        # Species split across multiple BINs
        mono = row['monophyletic']
        if mono == True:
            return f"split_across_{row['n_bins_for_species']}_BINs_monophyletic"
        elif mono == False:
            return f"split_across_{row['n_bins_for_species']}_BINs_paraphyletic"
        else:
            return f"split_across_{row['n_bins_for_species']}_BINs"
    
    elif row['bags_grade'] == 'E':
        # Multiple species share BIN
        n_other = len(row['other_species_in_bin'].split(', '))
        return f"shares_BIN_with_{n_other}_other_species"
    
    elif row['bags_grade'] in ['A', 'B', 'D']:
        return 'clean'
    
    else:
        return 'unknown'
```

**7.6 Final Metadata Columns (20 total):**

| Column | Description | Source |
|--------|-------------|--------|
| `name` | Tree tip label | Tree file |
| `species` | Species name | Parsed from tip |
| `bold_bin_uri` | BIN identifier | Parsed from tip |
| `category` | BIN_collected_in_BIOSCAN / Europe_reference / Not_in_UKSI | Logic |
| `geography` | UK / Europe_or_worldwide | UKSI membership |
| `placement_method` | reference_tree / EPA-ng / polytomy | Workflow |
| `placement_quality` | High/Moderate/Low confidence | EPA-ng LWR |
| `placement_confidence` | Numeric LWR score | EPA-ng |
| `bags_grade` | A/B/C/D/E/Unknown | curation_data.json |
| `n_bins_for_species` | Count of BINs | curation_data.json |
| `all_bins_for_species` | List of BINs | curation_data.json |
| `other_species_in_bin` | Species sharing BIN | curation_data.json |
| `monophyletic` | True/False for Grade C | tree_metadata.json |
| `bin_quality_issue` | Descriptive text | Derived |
| `in_uksi` | Boolean UK status | UKSI lookup |
| `bioscan_specimens` | Count of specimens | BIOSCAN aggregation |
| `dataset_bioscan` | Boolean | Specimen count > 0 |
| `dataset_dtol` | Boolean (placeholder) | Future |
| `dataset_goat` | Boolean (placeholder) | Future |
| `needs_attention` | Flag unexpected finds | Logic |

---

## 📈 FINAL OUTPUTS

### 1. Tree File: `{FAMILY}_final_tree.newick`

**Format:** Newick with branch lengths and bootstrap support

**Contents:**
- Reference sequences (from BGE)
- EPA-ng placements (UK specimens)
- Polytomies (species without molecular data)
- Outgroups (if retained for rooting)

**Tip label format:** `Species_name|BIN|ProcessID`

### 2. Metadata File: `{FAMILY}_taxonium_metadata.tsv`

**Format:** Tab-separated values

**Structure:**
- One row per tree tip
- 20 metadata columns
- Header row with column names

**Usage:** Upload to Taxonium.org along with tree file

---

## 🎨 VISUALIZATION IN TAXONIUM

### Upload Instructions

1. Go to https://taxonium.org/
2. Click "Upload"
3. Select:
   - Tree file: `{FAMILY}_final_tree.newick`
   - Metadata file: `{FAMILY}_taxonium_metadata.tsv`
4. Wait for processing (~30 seconds)

### Recommended Visualizations

**Color by Category:**
- 🟢 `BIN_collected_in_BIOSCAN` - UK specimens available
- ⚫ `Europe_reference` - No UK specimens
- 🔴 `Not_in_UKSI` - Unexpected UK finds!
- ⚪ `UKSI_no_specimens` - Known but uncollected

**Color by BAGS Grade:**
- **A/B**: Clean, high quality
- **C**: Species split across BINs (cryptic species candidates)
- **D**: Conflicts with other data
- **E**: Multiple species per BIN (taxonomy unclear)

**Color by Placement Quality:**
- **High confidence**: Reliable placements
- **Moderate**: Acceptable but flag for review
- **Low confidence**: Investigate!

### Useful Filters
```
# Only collected species
bioscan_specimens > 0

# Unexpected UK findings
needs_attention = TRUE

# Split species (cryptic candidates)
bags_grade = C

# Shared BINs (taxonomy issues)
bags_grade = E

# Low confidence placements
placement_quality = Low_confidence
```

### Search Examples
```
# Find specific BIN
bold_bin_uri:BOLD:AAA1234

# Find species
species:Bradysia paupera

# Multiple conditions
category:Not_in_UKSI AND bioscan_specimens:>10
```

---

## 🎯 INTERPRETING RESULTS

### High Priority Cases: Not_in_UKSI with Specimens

**Example (Sciaridae):**
- 265 specimens of *Unknown_species* (BIN BOLD:AHE4422)
  - Large specimen count → common species
  - Low placement confidence (0.38) → phylogenetic uncertainty
  - **Actions**: Morphological exam, re-sequence, expert consultation

- 1 specimen *Lycoriella acutostylia*
  - Named species not in UKSI
  - High placement confidence (0.996)
  - **Possible explanations**: New UK record, synonym, misidentification
  - **Actions**: Verify ID, check recent literature, examine voucher

### Grade C Species: BIN Splitting

**Interpretation depends on monophyly:**

**Monophyletic** (all sequences form one clade):
- Likely just BIN over-splitting
- Recent divergence or algorithm artifact
- **Low priority** for investigation

**Paraphyletic** (sequences don't form one clade):
- Strong evidence for cryptic species
- Requires taxonomic revision
- **High priority** for investigation

### Grade E BINs: BIN Sharing

**Multiple species in one BIN suggests:**
- Very recent divergence
- Incomplete lineage sorting
- Introgression/hybridization
- Morphological vs. molecular mismatch

**Actions:**
- Nuclear gene sequencing
- Morphological examination
- Examine geographic patterns

### Low Confidence Placements (LWR < 0.50)

**Possible causes:**
- Contamination
- Novel lineage not in reference tree
- Poor sequence quality
- Recombination or artifacts

**Actions:**
- Re-extract DNA and re-sequence
- Check for contaminants
- Morphological examination
- Try different markers (nuclear genes)

---

## 🔧 TROUBLESHOOTING

### Common Issues

**1. EPA-ng Error: "Invalid model name"**
- **Cause**: Model file missing or wrong format
- **Fix**: Re-run RAxML-ng model optimization

**2. EPA-ng Error: "Tree/alignment mismatch"**
- **Cause**: Sequence IDs don't match between tree and alignment
- **Fix**: Check for format differences, clean headers

**3. Low Placement Success Rate**
- **Cause**: Query sequences too divergent from reference
- **Fix**: Check if correct family, examine sequence quality

**4. Metadata Rows Don't Match Tree**
- **Cause**: Name format mismatch
- **Fix**: Use `clean_for_tree()` function on all names

**5. Many "Unknown" BAGS Grades**
- **Cause**: Matching only by species name (misses unidentified specimens)
- **Fix**: Match by BIN first, then species name

---

## 📚 REFERENCES

### Software

**Phylogenetic Placement:**
- EPA-ng: Barbera et al. (2019) Syst Biol 68(2):365-369
- gappa: Czech & Stamatakis (2019) Bioinformatics 35(16):2906-2907

**Model Optimization:**
- RAxML-ng: Kozlov et al. (2019) Bioinformatics 35(21):4453-4455

**Reference Tree Construction (BGE):**
- IQ-TREE2: Minh et al. (2020) Mol Biol Evol 37(5):1530-1534
- MAFFT: Katoh & Standley (2013) Mol Biol Evol 30(4):772-780

### Resources

**BGE Project:**
- GitHub: https://github.com/bge-barcoding/bold-library-curation
- Workflow: [BGE README](https://github.com/bge-barcoding/bold-library-curation/blob/main/workflow/README.md)

**BIOSCAN:**
- Website: https://bioscanproject.org/
- UK Project: [Contact for details]

**BOLD:**
- Website: http://www.boldsystems.org/
- BIN System: Ratnasingham & Hebert (2013) PLoS ONE 8(7):e66213

---

## 🔄 SCALING TO OTHER FAMILIES

### Preparation Checklist

- [ ] Contact collaborator for reference tree + alignment
- [ ] Extract family records from BIOSCAN database
- [ ] Get UKSI species list for family
- [ ] Create family directory: `families/{FAMILY}/`
- [ ] Copy input files to appropriate directories
- [ ] Edit family README with specific details

### Running Pipeline
```bash
cd families/{FAMILY}
bash ../../scripts/run_pipeline.sh {FAMILY}
```

### Post-Analysis

- [ ] Review EPA-ng placement quality
- [ ] Investigate cases flagged "needs attention"
- [ ] Document family-specific issues
- [ ] Update family README with results
- [ ] Commit to GitHub

### Expected Timeline (per family)

- Data preparation: 1-2 hours
- Pipeline execution: 30 minutes - 2 hours (depends on size)
- Results review: 2-4 hours
- Documentation: 1 hour

**Total: ~1 day per family** (assuming reference tree available)

---

**This workflow has been successfully applied to:**
- ✅ Sciaridae (829 tips, 13,806 specimens)

**Next families:**
- [ ] Chironomidae
- [ ] Tipulidae
- [ ] Additional Diptera families

---

**Document version**: 1.0  
**Last updated**: January 2025  
**Maintainer**: Lyndall Pereira
