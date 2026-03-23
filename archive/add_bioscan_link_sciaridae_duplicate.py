#!/usr/bin/env python3
"""
Add BOLD BIOSCAN Specimens link to metadata
Links to all BIOSCAN specimens within a BIN from Wellcome Sanger Institute
"""

import pandas as pd
import urllib.parse

print("=" * 80)
print("ADDING BOLD BIOSCAN SPECIMENS LINK")
print("=" * 80)

# Load metadata
df = pd.read_csv('/mnt/project/sciaridae_metadata_UPLOAD.tsv', sep='\t')
print(f"\nLoaded {len(df):,} specimens")

def make_markdown_link(url, text):
    """Create markdown link: [text](url)"""
    if url == '' or pd.isna(url):
        return ''
    return f"[{text}]({url})"

def make_bold_bioscan_link(row):
    """
    Create link to BOLD portal showing all BIOSCAN specimens for this BIN
    Example: https://portal.boldsystems.org/result?query=BOLD:ACP5952[bin],%22Wellcome%20Sanger%20Institute%22[inst]
    """
    if pd.isna(row['bin']) or row['bin'] in ['', 'no_BIN']:
        return ''
    
    # Build the query: BIN and institution
    # URL encode the institution name
    institution = "Wellcome Sanger Institute"
    query = f'{row["bin"]}[bin],"{institution}"[inst]'
    
    # Create the full URL
    url = f"https://portal.boldsystems.org/result?query={query}"
    
    return make_markdown_link(url, "🔬 BIOSCAN")

# Create the new link column
print("\nCreating BOLD BIOSCAN specimens links...")
df['BOLD_BIOSCAN'] = df.apply(make_bold_bioscan_link, axis=1)

# Count how many links were created
bioscan_links = (df['BOLD_BIOSCAN'] != '').sum()
print(f"Created {bioscan_links:,} BOLD BIOSCAN links")

# Find the position to insert the new column (after BOLD_Specimen)
if 'BOLD_Specimen' in df.columns:
    cols = df.columns.tolist()
    specimen_idx = cols.index('BOLD_Specimen')
    # Reorder: insert BOLD_BIOSCAN after BOLD_Specimen
    new_cols = cols[:specimen_idx+1] + ['BOLD_BIOSCAN'] + [c for c in cols[specimen_idx+1:] if c != 'BOLD_BIOSCAN']
    df = df[new_cols]
    print("Inserted BOLD_BIOSCAN column after BOLD_Specimen")

# Save
output_file = '/mnt/user-data/outputs/sciaridae_metadata_with_bioscan_link.tsv'
df.to_csv(output_file, sep='\t', index=False)

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"\nTotal specimens: {len(df):,}")
print(f"BOLD BIOSCAN links created: {bioscan_links:,}")
print(f"\nNew column added: BOLD_BIOSCAN")
print(f"  Links to: All BIOSCAN specimens for each BIN at Wellcome Sanger Institute")
print(f"\nOutput saved to: {output_file}")

# Show examples
print("\n" + "=" * 80)
print("EXAMPLE LINKS")
print("=" * 80)

examples = df[df['BOLD_BIOSCAN'] != ''].head(3)
for idx, row in examples.iterrows():
    print(f"\n{row['name']}")
    print(f"  BIN: {row['bin']}")
    print(f"  Link: {row['BOLD_BIOSCAN']}")
    # Show the actual URL
    if '[' in row['BOLD_BIOSCAN']:
        url_start = row['BOLD_BIOSCAN'].index('(') + 1
        url_end = row['BOLD_BIOSCAN'].index(')')
        print(f"  URL: {row['BOLD_BIOSCAN'][url_start:url_end]}")

print("\n" + "=" * 80 + "\n")
