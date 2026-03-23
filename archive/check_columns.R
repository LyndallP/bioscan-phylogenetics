library(BOLDconnectR)

bold.apikey("7F5D2DB4-BEA4-4307-B765-81F9AA3F0618")
processids <- readLines("reference_tree_all_processids.txt")

specimen_data <- bold.fetch(get_by = "processid", identifiers = processids)

# Show column names
cat("Available columns:\n")
print(names(specimen_data))
