# Taxonium View Links for Sciaridae Phylogeny

Upload `sciaridae_taxonium.jsonl.gz` to https://taxonium.org

Then use these URLs for different views (replace BASE_URL with your Taxonium URL):

## View 1: Genus Diversity
**Focus:** See genus-level diversity with custom colors
```
BASE_URL&colorBy=genus
```

## View 2: Geographic Distribution  
**Focus:** Where specimens were collected
```
BASE_URL&colorBy=geography
```

## View 3: Data Sources
**Focus:** Reference vs BIOSCAN vs DTOL
```
BASE_URL&colorBy=dataset
```

## View 4: Placement Confidence
**Focus:** Quality of EPA-ng placements
```
BASE_URL&colorBy=placement_quality
```

## View 5: Bootstrap Support
**Focus:** Phylogenetic confidence of parent nodes
```
BASE_URL&colorBy=parent_bootstrap
```

## View 6: UK BIOSCAN Specimens Only
**Focus:** Just the UK BIOSCAN data
```
BASE_URL&search=geography:United_Kingdom&colorBy=genus
```

## View 7: DTOL Genomes
**Focus:** Genome-sequenced specimens
```
BASE_URL&search=dataset:DTOL&colorBy=genus
```

## View 8: High Confidence + High Support
**Focus:** Well-placed specimens in well-supported clades
```
BASE_URL&search=placement_quality:High,parent_bootstrap:>90&colorBy=genus
```

