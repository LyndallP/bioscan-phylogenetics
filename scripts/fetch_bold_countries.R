#!/usr/bin/env Rscript
library(BOLDconnectR)
library(dplyr)

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2) {
  cat("Usage: Rscript fetch_bold_countries.R <processids.txt> <output.tsv>\n")
  quit(status = 1)
}
input_processids <- args[1]
output_file <- args[2]

# Set API key from environment variable
api_key <- Sys.getenv("BOLD_API_KEY")
if (nchar(api_key) == 0) {
  stop("BOLD_API_KEY environment variable is not set")
}
bold.apikey(api_key)

# Load process IDs
processids <- readLines(input_processids)
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
            output_file,
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

cat(sprintf("\n✓ Saved to: %s\n", output_file))
