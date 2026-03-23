#!/usr/bin/env Rscript
library(BOLDconnectR)
library(dplyr)

# Set API key
bold.apikey("7F5D2DB4-BEA4-4307-B765-81F9AA3F0618")

# Load process IDs
processids <- readLines("reference_tree_all_processids.txt")
cat(sprintf("Fetching BOLD data for %d specimens...\n\n", length(processids)))

cat("Querying BOLD API (this will take several minutes)...\n")

specimen_data <- bold.fetch(get_by = "processid", 
                           identifiers = processids)

cat(sprintf("\n✓ Retrieved %d records\n\n", nrow(specimen_data)))

# Extract relevant fields (use correct column names with periods)
results <- specimen_data %>%
  select(
    processid = processid,
    country_ocean = country.ocean,      # Note: period not underscore
    province_state = province.state,    # Note: period not underscore
    species = identification,
    bin_uri = bin_uri,
    coord = coord
  )

# Save results
write.table(results, 
            "data/reference_tree_bold_countries.tsv",
            sep = "\t",
            row.names = FALSE,
            quote = FALSE)

# Summary
cat("=== Summary ===\n")
cat(sprintf("Specimens retrieved: %d/%d\n", nrow(results), length(processids)))
cat(sprintf("With country data: %d\n", sum(!is.na(results$country_ocean))))

cat("\nTop countries:\n")
country_counts <- sort(table(results$country_ocean), decreasing = TRUE)
print(head(country_counts, 15))

cat(sprintf("\n✓ Saved to: data/reference_tree_bold_countries.tsv\n"))
