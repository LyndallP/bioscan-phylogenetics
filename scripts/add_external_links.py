#!/usr/bin/env python3
"""
Add external database links and derived columns to placement metadata.

Creates:
  - geography_broad   : broad biogeographic region from geography (country)
  - family            : family name (passed as --family argument)
  - species_in_GOAT   : bool, whether species is present in GOAT
  - GBIF              : markdown link to GBIF species search
  - GOAT              : markdown link to GOAT taxon page (only if species_in_GOAT)
  - NBN               : markdown link to NBN Atlas species page
  - TOLQC             : markdown link to TOLQC page (DTOL specimens only)
  - BLAST             : markdown link to NCBI BLAST search by processid
  - BOLD_BIN          : markdown link to BOLD BIN cluster page
  - BOLD_Specimen     : markdown link to BOLD specimen record
  - BOLD_BIOSCAN      : markdown link to all BIOSCAN specimens for the BIN

Also renames:
  - all_bins          -> all_bins_for_species
  - bioscan_specimens -> Bioscan specimen count

Usage:
  python add_external_links.py <input.tsv> <output.tsv> --family Sciaridae [--skip-goat]

  The bioscan CSV is auto-detected at families/{Family}/input/bioscan_{family}.csv.
  Override with --bioscan-csv if it lives elsewhere.
"""

import argparse
import urllib.parse
import sys
import pandas as pd
import requests

# ---------------------------------------------------------------------------
# Geography broad mapping
# ---------------------------------------------------------------------------
GEOGRAPHY_BROAD_MAP = {
    # British Isles
    'United Kingdom': 'British Isles',
    'Ireland': 'British Isles',
    # Scandinavia
    'Norway': 'Scandinavia',
    'Sweden': 'Scandinavia',
    'Denmark': 'Scandinavia',
    'Finland': 'Scandinavia',
    'Iceland': 'Scandinavia',
    # Western Europe
    'Germany': 'Western Europe',
    'France': 'Western Europe',
    'Belgium': 'Western Europe',
    'Netherlands': 'Western Europe',
    'Luxembourg': 'Western Europe',
    'Switzerland': 'Western Europe',
    'Austria': 'Western Europe',
    'Liechtenstein': 'Western Europe',
    # Eastern Europe
    'Poland': 'Eastern Europe',
    'Czechia': 'Eastern Europe',
    'Czech Republic': 'Eastern Europe',
    'Slovakia': 'Eastern Europe',
    'Hungary': 'Eastern Europe',
    'Romania': 'Eastern Europe',
    'Bulgaria': 'Eastern Europe',
    'Moldova': 'Eastern Europe',
    'Ukraine': 'Eastern Europe',
    'Belarus': 'Eastern Europe',
    'Russia': 'Eastern Europe',
    'Georgia': 'Eastern Europe',
    'Armenia': 'Eastern Europe',
    'Azerbaijan': 'Eastern Europe',
    'Estonia': 'Eastern Europe',
    'Latvia': 'Eastern Europe',
    'Lithuania': 'Eastern Europe',
    # Southern Europe
    'Spain': 'Southern Europe',
    'Portugal': 'Southern Europe',
    'Italy': 'Southern Europe',
    'Greece': 'Southern Europe',
    'Croatia': 'Southern Europe',
    'Slovenia': 'Southern Europe',
    'Serbia': 'Southern Europe',
    'Bosnia and Herzegovina': 'Southern Europe',
    'Montenegro': 'Southern Europe',
    'Albania': 'Southern Europe',
    'North Macedonia': 'Southern Europe',
    'Kosovo': 'Southern Europe',
    'Malta': 'Southern Europe',
    'Cyprus': 'Southern Europe',
    'Turkey': 'Southern Europe',
    'Israel': 'Southern Europe',
    'Lebanon': 'Southern Europe',
    'Iran': 'Southern Europe',
    # North America
    'Canada': 'North America',
    'United States': 'North America',
    'Mexico': 'North America',
    # Central America / Caribbean
    'Guatemala': 'Central America',
    'Costa Rica': 'Central America',
    'Panama': 'Central America',
    'Cuba': 'Caribbean',
    'Puerto Rico': 'Caribbean',
    # South America
    'Brazil': 'South America',
    'Argentina': 'South America',
    'Colombia': 'South America',
    'Peru': 'South America',
    'Chile': 'South America',
    'Venezuela': 'South America',
    'Ecuador': 'South America',
    'Bolivia': 'South America',
    # East Asia
    'China': 'East Asia',
    'South Korea': 'East Asia',
    'Japan': 'East Asia',
    'Taiwan': 'East Asia',
    'Mongolia': 'East Asia',
    # South Asia
    'India': 'South Asia',
    'Pakistan': 'South Asia',
    'Bangladesh': 'South Asia',
    'Nepal': 'South Asia',
    'Sri Lanka': 'South Asia',
    # Southeast Asia
    'Thailand': 'Southeast Asia',
    'Vietnam': 'Southeast Asia',
    'Indonesia': 'Southeast Asia',
    'Malaysia': 'Southeast Asia',
    'Philippines': 'Southeast Asia',
    'Cambodia': 'Southeast Asia',
    'Myanmar': 'Southeast Asia',
    # Middle East
    'Saudi Arabia': 'Middle East',
    'United Arab Emirates': 'Middle East',
    'Jordan': 'Middle East',
    'Iraq': 'Middle East',
    'Kuwait': 'Middle East',
    'Qatar': 'Middle East',
    # Africa
    'South Africa': 'Africa',
    'Kenya': 'Africa',
    'Ethiopia': 'Africa',
    'Morocco': 'Africa',
    'Egypt': 'Africa',
    'Nigeria': 'Africa',
    'Tanzania': 'Africa',
    'Uganda': 'Africa',
    'Cameroon': 'Africa',
    'Mozambique': 'Africa',
    'Madagascar': 'Africa',
    # Oceania
    'Australia': 'Oceania',
    'New Zealand': 'Oceania',
    'Papua New Guinea': 'Oceania',
}


# ---------------------------------------------------------------------------
# Link helper
# ---------------------------------------------------------------------------
def make_markdown_link(url, text):
    if not url or pd.isna(url):
        return ''
    return f"[{text}]({url})"


def make_gbif_link(row):
    sp = str(row.get('species', '') or '')
    if not sp or sp in ('Unknown', 'Unidentified', 'nan', ''):
        return ''
    url = f"https://www.gbif.org/species/search?q={urllib.parse.quote(sp)}"
    return make_markdown_link(url, "🌍 GBIF map")


def make_goat_link(row):
    if not row.get('species_in_GOAT', False):
        return ''
    sp = str(row.get('species', '') or '')
    if not sp or sp in ('Unknown', 'Unidentified', 'nan', ''):
        return ''
    url = (
        f"https://goat.genomehubs.org/search?result=taxon&taxonomy=ncbi"
        f"&query=tax_name%28{urllib.parse.quote(sp)}%29"
    )
    return make_markdown_link(url, "🐐 GOAT")


def make_nbn_link(row):
    sp = str(row.get('species', '') or '')
    if not sp or sp in ('Unknown', 'Unidentified', 'nan', ''):
        return ''
    url = f"https://species.nbnatlas.org/species/{urllib.parse.quote(sp)}"
    return make_markdown_link(url, "🇬🇧 NBN Atlas")


def make_tolqc_link(row):
    if str(row.get('dataset', '') or '') != 'DTOL':
        return ''
    sp = str(row.get('species', '') or '')
    if not sp:
        return ''
    url = f"https://tolqc.cog.sanger.ac.uk/darwin/insects/{sp.replace(' ', '_')}/"
    return make_markdown_link(url, "🌳 TOLQC")


def make_blast_link(row):
    seq = str(row.get('bold_nuc', '') or '')
    if not seq or seq in ('nan', ''):
        return ''
    url = (
        f"https://blast.ncbi.nlm.nih.gov/Blast.cgi"
        f"?PROGRAM=blastn&PAGE_TYPE=BlastSearch&QUERY={seq}"
    )
    return make_markdown_link(url, "🧬 NCBI BLAST")


def make_bold_bin_link(row):
    b = str(row.get('bin', '') or '')
    if not b or b in ('no_BIN', 'nan', ''):
        return ''
    url = f"http://www.boldsystems.org/index.php/Public_BarcodeCluster?clusteruri={b}"
    return make_markdown_link(url, "🔷 BIN")


def make_bold_specimen_link(row):
    pid = str(row.get('processid', '') or '')
    if not pid or pid in ('nan', ''):
        return ''
    url = f"https://portal.boldsystems.org/result?query={pid}[ids]"
    return make_markdown_link(url, "🔬 Specimen")


def make_bold_bioscan_link(row):
    b = str(row.get('bin', '') or '')
    if not b or b in ('no_BIN', 'nan', ''):
        return ''
    url = (
        f'https://portal.boldsystems.org/result'
        f'?query={b}[bin],%22Wellcome%20Sanger%20Institute%22[inst]'
    )
    return make_markdown_link(url, "🪰 BIOSCAN")


# ---------------------------------------------------------------------------
# GOAT presence check
# ---------------------------------------------------------------------------
def check_goat_presence_batch(species_list):
    """Check GOAT presence for a list of unique species. Returns dict species->bool."""
    results = {}
    total = len(species_list)
    for i, sp in enumerate(species_list, 1):
        if not sp or pd.isna(sp) or str(sp) in ('Unknown', 'Unidentified', 'nan', ''):
            results[sp] = False
            continue
        print(f"  Checking GOAT {i}/{total}: {sp}", end='\r')
        url = f"https://goat.genomehubs.org/api/v2/search?query=tax_name({urllib.parse.quote(str(sp))})"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                results[sp] = len(data.get('results', [])) > 0
            else:
                results[sp] = False
        except Exception:
            results[sp] = False
    print()
    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Add geography_broad, species_in_GOAT, and external link columns"
    )
    parser.add_argument("input", help="Input metadata TSV")
    parser.add_argument("output", help="Output metadata TSV")
    parser.add_argument("--family", required=True, help="Family name (e.g. Sciaridae)")
    parser.add_argument(
        "--bioscan-csv",
        help="Path to bioscan_{family}.csv. If omitted, defaults to "
             "families/{Family}/input/bioscan_{family_lower}.csv"
    )
    parser.add_argument(
        "--skip-goat", action="store_true",
        help="Skip GOAT API check (sets species_in_GOAT=False for all rows)"
    )
    args = parser.parse_args()

    # Auto-detect bioscan CSV from standard location if not explicitly given
    import os
    bioscan_csv_path = args.bioscan_csv
    if not bioscan_csv_path:
        family_lower = args.family.lower()
        bioscan_csv_path = f"families/{args.family}/input/bioscan_{family_lower}.csv"

    print("=" * 70)
    print("ADDING EXTERNAL LINKS AND DERIVED COLUMNS")
    print("=" * 70)

    df = pd.read_csv(args.input, sep='\t')
    print(f"\nLoaded {len(df):,} rows, {len(df.columns)} columns")

    # ------------------------------------------------------------------
    # Rename columns to match target schema
    # ------------------------------------------------------------------
    print("\n1. Renaming columns to match target schema...")
    rename_map = {}
    if 'all_bins' in df.columns and 'all_bins_for_species' not in df.columns:
        rename_map['all_bins'] = 'all_bins_for_species'
    if 'bioscan_specimens' in df.columns and 'Bioscan specimen count' not in df.columns:
        rename_map['bioscan_specimens'] = 'Bioscan specimen count'
    if rename_map:
        df = df.rename(columns=rename_map)
        for old, new in rename_map.items():
            print(f"   {old} -> {new}")

    # ------------------------------------------------------------------
    # Restore BOLD: colon in BIN columns (stripped by 03_clean_alignment.py
    # because colons are Newick branch-length separators)
    # ------------------------------------------------------------------
    print("\n2. Restoring BOLD: colon in BIN columns...")
    for col in ('bin', 'all_bins_for_species', 'all_bins'):
        if col in df.columns:
            df[col] = df[col].astype(str).replace('nan', '')
            before = df[col].str.contains('BOLD:', na=False).sum()
            df[col] = df[col].str.replace(r'\bBOLD(?!:)', 'BOLD:', regex=True)
            after = df[col].str.contains('BOLD:', na=False).sum()
            print(f"   {col}: {after - before:,} values restored")

    # ------------------------------------------------------------------
    # Bioscan specimen count + bold_nuc from bioscan CSV
    # ------------------------------------------------------------------
    if os.path.exists(bioscan_csv_path):
        print(f"\n3. Loading bioscan CSV: {bioscan_csv_path}")
        bioscan = pd.read_csv(bioscan_csv_path)
        print(f"   {len(bioscan):,} rows loaded")

        # Bioscan specimen count: number of rows per BIN in the bioscan CSV
        bin_counts = (
            bioscan.groupby('bold_bin_uri').size()
            .reset_index(name='Bioscan specimen count')
        )
        # Restore BOLD: colon in the CSV's BIN column to match our restored values
        bin_counts['bold_bin_uri'] = bin_counts['bold_bin_uri'].str.replace(
            r'\bBOLD(?!:)', 'BOLD:', regex=True
        )
        df = df.merge(
            bin_counts, left_on='bin', right_on='bold_bin_uri', how='left'
        )
        df = df.drop(columns=['bold_bin_uri'])
        df['Bioscan specimen count'] = df['Bioscan specimen count'].fillna(0).astype(int)
        filled = (df['Bioscan specimen count'] > 0).sum()
        print(f"   Bioscan specimen count: {filled:,} rows with count > 0")

        # bold_nuc: join per-specimen sequence for BLAST links
        if 'bold_nuc' in bioscan.columns and 'processid' in df.columns:
            nuc_map = bioscan.set_index('bold_processid')['bold_nuc'].to_dict()
            df['bold_nuc'] = df['processid'].map(nuc_map)
            blast_ready = df['bold_nuc'].notna().sum()
            print(f"   bold_nuc sequences: {blast_ready:,} matched")
    else:
        print(f"\n3. Bioscan CSV not found at {bioscan_csv_path}; Bioscan specimen count and BLAST links will be empty")
        if 'Bioscan specimen count' not in df.columns:
            df['Bioscan specimen count'] = 0

    # ------------------------------------------------------------------
    # Add family column
    # ------------------------------------------------------------------
    print(f"\n4. Adding family column: {args.family}")
    df['family'] = args.family

    # ------------------------------------------------------------------
    # geography_broad
    # ------------------------------------------------------------------
    print("\n5. Creating geography_broad column...")
    df['geography_broad'] = df['geography'].map(GEOGRAPHY_BROAD_MAP).fillna('Other')
    unmapped = df[df['geography_broad'] == 'Other']['geography'].dropna().unique()
    unmapped = [v for v in unmapped if v not in ('', 'Unknown', 'nan')]
    if unmapped:
        print(f"   Unmapped countries (assigned 'Other'): {sorted(unmapped)}")
    broad_counts = df['geography_broad'].value_counts()
    for region, count in broad_counts.items():
        print(f"   {region}: {count:,}")

    # ------------------------------------------------------------------
    # species_in_GOAT
    # ------------------------------------------------------------------
    if args.skip_goat:
        print("\n6. Skipping GOAT check (--skip-goat)")
        df['species_in_GOAT'] = False
    else:
        print("\n6. Checking GOAT presence (per unique species)...")
        unique_species = df['species'].dropna().unique().tolist()
        print(f"   {len(unique_species):,} unique species to check")
        goat_map = check_goat_presence_batch(unique_species)
        df['species_in_GOAT'] = df['species'].map(goat_map).fillna(False)
        in_goat = df['species_in_GOAT'].sum()
        print(f"   {in_goat:,} rows with species found in GOAT")

    # ------------------------------------------------------------------
    # External link columns
    # ------------------------------------------------------------------
    print("\n7. Creating external link columns...")

    df['GBIF'] = df.apply(make_gbif_link, axis=1)
    print(f"   GBIF: {(df['GBIF'] != '').sum():,} links")

    df['GOAT'] = df.apply(make_goat_link, axis=1)
    print(f"   GOAT: {(df['GOAT'] != '').sum():,} links")

    df['NBN'] = df.apply(make_nbn_link, axis=1)
    print(f"   NBN: {(df['NBN'] != '').sum():,} links")

    df['TOLQC'] = df.apply(make_tolqc_link, axis=1)
    print(f"   TOLQC: {(df['TOLQC'] != '').sum():,} links (DTOL only)")

    df['BLAST'] = df.apply(make_blast_link, axis=1)
    print(f"   BLAST: {(df['BLAST'] != '').sum():,} links")

    df['BOLD_BIN'] = df.apply(make_bold_bin_link, axis=1)
    print(f"   BOLD_BIN: {(df['BOLD_BIN'] != '').sum():,} links")

    df['BOLD_Specimen'] = df.apply(make_bold_specimen_link, axis=1)
    print(f"   BOLD_Specimen: {(df['BOLD_Specimen'] != '').sum():,} links")

    df['BOLD_BIOSCAN'] = df.apply(make_bold_bioscan_link, axis=1)
    print(f"   BOLD_BIOSCAN: {(df['BOLD_BIOSCAN'] != '').sum():,} links")

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------
    df.to_csv(args.output, sep='\t', index=False)

    print(f"\n✓ Saved {len(df):,} rows, {len(df.columns)} columns to: {args.output}")
    print(f"  Columns added: family, geography_broad, species_in_GOAT,")
    print(f"                 GBIF, GOAT, NBN, TOLQC, BLAST,")
    print(f"                 BOLD_BIN, BOLD_Specimen, BOLD_BIOSCAN")
    if rename_map:
        print(f"  Columns renamed: {', '.join(f'{k}->{v}' for k, v in rename_map.items())}")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
