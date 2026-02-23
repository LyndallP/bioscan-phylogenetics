# Unknown vs. Unidentified Species in Sciaridae Metadata

## Summary

**"Unknown"** and **"Unidentified"** are used differently in the metadata:

- **Tip Name Field**: Always uses "Unknown_species" (with underscore)
- **Species Field**: Uses "Unidentified" (as the actual species designation)
- **Category Field**: Uses "Not_in_UKSI" or "Europe_reference"

## The Pattern

### For BIOSCAN Specimens (Missing Species ID)
```
Tip name:    Unknown_species|BOLDAGM6430|NBGW6381-23
Species:     Unidentified
Category:    Not_in_UKSI
Dataset:     BIOSCAN
```

### For Reference Specimens (Missing Species ID)
```
Tip name:    Unidentified|BOLDAGM6430|NBGW6381-23  
Species:     Unidentified
Category:    Not_in_UKSI (or Europe_reference)
Dataset:     Reference
```

## Why Two Different Terms?

### 1. **Tip Names** (tree labels)
- Use "Unknown_species" because:
  - Tree tip names cannot have spaces (Newick format limitation)
  - Need to be parseable as Species|BIN|ProcessID
  - Come from BOLD database export where unidentified specimens are labeled "Unknown species"

### 2. **Species Column** (metadata)
- Uses "Unidentified" because:
  - This is the standard taxonomic designation
  - More professional/formal than "Unknown"
  - Clearly indicates "not identified to species level"
  - Allows spaces in metadata fields

## Categories Explained

### **Not_in_UKSI**
- Species/specimen is NOT on the UK Species Inventory list
- Could be:
  - Novel/undescribed species
  - Non-UK species (vagrant, introduced)
  - Misidentification
  - Taxonomic issue
- **Has molecular data** (BIN assigned)

### **Europe_reference**
- Reference specimens from Europe (not UK)
- Not expected to be in UKSI
- Provides phylogenetic context
- Also "Unidentified" if species unknown

## Statistics from Current Tree

```
Category              Count
Not_in_UKSI           ~100+ specimens (unidentified BIOSCAN + reference)
Europe_reference      ~20 specimens (unidentified European reference)
```

### Breakdown by Dataset
```
BIOSCAN "Unidentified":    23 specimens (novel BINs, no reference)
Reference "Unidentified":  ~90 specimens (Europe + other regions)
```

## Why So Many "Unidentified"?

### BIOSCAN Specimens (23 specimens)
These are **novel BINs** where:
1. BIOSCAN UK collected the specimen
2. BIN has no reference specimens with species ID in BOLD
3. Likely represent:
   - Cryptic species
   - Undescribed species
   - Species not yet in BOLD database

### Reference Specimens (~90 specimens)
These specimens:
1. Came from European BOLD data
2. Were submitted without species-level ID
3. Provide phylogenetic context but need expert identification

## Restoration Process

When restoring missing metadata, the script:

1. Tries to match BIN to specimens with species IDs
2. If match found → copies species name
3. If no match found → remains "Unidentified"
4. Sets category based on:
   - `in_uksi` flag (True/False)
   - `dataset` (BIOSCAN vs Reference)

## Examples

### Successfully Restored
```
Before:  Unknown_species|BOLDADL7479|RRHP1314-24 → species: [empty]
After:   Unknown_species|BOLDADL7479|RRHP1314-24 → species: Corynoptera sp.
Reason:  BIN BOLD:ADL7479 had reference specimen with ID
```

### Remained Unidentified
```
Before:  Unknown_species|BOLDAGM6430|[processid] → species: [empty]
After:   Unknown_species|BOLDAGM6430|[processid] → species: Unidentified
Reason:  BIN BOLD:AGM6430 has no specimens with species ID (novel BIN)
```

## Taxonomic Priority

These "Unidentified" specimens are **high priority for expert identification** because:
1. **BIOSCAN "Unidentified"** = potential new UK records or new species
2. **Reference "Unidentified"** = phylogenetic gaps that could improve tree

## How to Find Them in Taxonium

```
Search: category:Not_in_UKSI
Search: species:Unidentified
Search: species:Unidentified AND dataset:BIOSCAN
```

## Recommendations

### For Publication
Use: **"Unidentified"** (formal taxonomic designation)

### For Casual Discussion
Both "unknown" and "unidentified" are acceptable

### In Tree Visualizations
The tip names will show "Unknown_species" (tree format requirement)
The metadata panel will show "Unidentified" (proper designation)

---

**Key Takeaway**: "Unknown_species" in tip names and "Unidentified" in the species field refer to the **same thing** - specimens that lack species-level identification. The different terms exist due to formatting requirements and taxonomic conventions.
