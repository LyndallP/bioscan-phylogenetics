#!/usr/bin/env Rscript
library(BOLDconnectR)
library(dplyr)

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2) {
  cat("Usage: Rscript fetch_bold_countries.R <metadata.tsv> <output.tsv>\n")
  cat("  metadata.tsv : output of add_enhanced_metadata.py (has 'name' column)\n")
  quit(status = 1)
}
input_metadata <- args[1]
output_file    <- args[2]

# Set API key from environment variable
api_key <- Sys.getenv("BOLD_API_KEY")
if (nchar(api_key) == 0) {
  stop("BOLD_API_KEY environment variable is not set")
}
bold.apikey(api_key)

# Load metadata TSV and extract process IDs from the name column.
# Tip format: Species|BIN|ProcessID  (or Species|no_BIN|polytomy for polytomies)
metadata <- read.table(input_metadata, sep = "\t", header = TRUE,
                       quote = "", comment.char = "", stringsAsFactors = FALSE)

extract_processid <- function(name) {
  parts <- strsplit(name, "\\|")[[1]]
  if (length(parts) >= 3) parts[3] else NA_character_
}

all_ids <- sapply(metadata$name, extract_processid, USE.NAMES = FALSE)
# Drop polytomy placeholders and NAs
processids <- unique(all_ids[!is.na(all_ids) & all_ids != "polytomy"])

cat(sprintf("Fetching BOLD data for %d unique process IDs...\n\n", length(processids)))

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
