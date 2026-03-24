#!/usr/bin/env python3
"""
Add ThumbnailURL column to placement metadata using the BOLD CAOS API.

Fetches specimen images directly from BOLD for all specimens that have a
process ID (BIOSCAN, reference tree, DTOL where applicable).  No API key
required — uses the public CAOS endpoint:
  https://caos.boldsystems.org/api/images?processids=<ids>
  https://caos.boldsystems.org/api/objects/<objectid>

Taxonium renders images automatically when a ThumbnailURL column is present.

Usage:
    python scripts/add_bioscan_specimen_ids_LOCAL.py <input_metadata.tsv> <output_metadata.tsv>
"""

import sys
import json
import time
import urllib.request
import urllib.error
import pandas as pd
import os

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <input_metadata.tsv> <output_metadata.tsv>")
    sys.exit(1)

# BOLD CAOS API endpoints
CAOS_BASE_URL = "https://caos.boldsystems.org/api/images?processids="
CAOS_IMAGE_URL = "https://caos.boldsystems.org/api/objects/"
BATCH_SIZE = 100
URL_MAX_LEN = 7500
SLEEP_BETWEEN = 0.5  # seconds between batches

print("=" * 80)
print("ADDING BOLD THUMBNAIL URLs")
print("=" * 80)


def fetch_image_map(processids):
    """
    Query BOLD CAOS API for a list of process IDs.
    Returns dict: {processid: objectid} for those that have images.
    """
    sub_batches = []
    current = []
    current_len = 0
    for pid in processids:
        if current_len + len(pid) + 1 > URL_MAX_LEN and current:
            sub_batches.append(current)
            current = [pid]
            current_len = len(pid)
        else:
            current.append(pid)
            current_len += len(pid) + 1
    if current:
        sub_batches.append(current)

    image_map = {}
    for i, batch in enumerate(sub_batches):
        url = CAOS_BASE_URL + ",".join(batch)
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "bioscan-phylogenetics/1.0"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            for entry in data:
                pid = entry.get("processid")
                oid = entry.get("objectid")
                if pid and oid:
                    image_map[pid] = oid
        except urllib.error.HTTPError as e:
            print(f"   Warning: HTTP {e.code} on batch {i + 1}: {e.reason}")
        except urllib.error.URLError as e:
            print(f"   Warning: URL error on batch {i + 1}: {e.reason}")
        except json.JSONDecodeError as e:
            print(f"   Warning: JSON parse error on batch {i + 1}: {e}")
        time.sleep(SLEEP_BETWEEN)

    return image_map


# ============================================================================
# 1. LOAD METADATA
# ============================================================================

print(f"\n1. Loading metadata from: {sys.argv[1]}")
df = pd.read_csv(sys.argv[1], sep='\t')
print(f"   Loaded {len(df):,} specimens")

# ============================================================================
# 2. EXTRACT PROCESS IDs
# ============================================================================

print("\n2. Extracting process IDs from tip names...")

def extract_processid(name):
    """Extract processid from tip format: Species|BIN|ProcessID"""
    if pd.isna(name):
        return None
    parts = name.split('|')
    if len(parts) >= 3:
        return parts[2]
    return None

if 'processid' not in df.columns:
    df['processid'] = df['name'].apply(extract_processid)

processids = df['processid'].dropna().unique().tolist()
print(f"   Found {len(processids):,} unique process IDs")

# ============================================================================
# 3. FETCH THUMBNAILS FROM BOLD CAOS API
# ============================================================================

print(f"\n3. Querying BOLD CAOS API for thumbnail images...")
print(f"   Processing {len(processids):,} IDs in batches of {BATCH_SIZE}...")

image_map = fetch_image_map(processids)
print(f"   Found images for {len(image_map):,} / {len(processids):,} specimens")

# ============================================================================
# 4. ADD ThumbnailURL COLUMN
# ============================================================================

print("\n4. Adding ThumbnailURL column...")

df['ThumbnailURL'] = df['processid'].apply(
    lambda pid: f"{CAOS_IMAGE_URL}{image_map[pid]}" if pid in image_map else ''
)

thumbnail_count = (df['ThumbnailURL'] != '').sum()
print(f"   ThumbnailURL populated for {thumbnail_count:,} specimens")

# Dataset breakdown
if 'dataset' in df.columns:
    for dataset in sorted(df['dataset'].dropna().unique()):
        ds_df = df[df['dataset'] == dataset]
        has_thumb = (ds_df['ThumbnailURL'] != '').sum()
        print(f"   {dataset}: {has_thumb:,} / {len(ds_df):,} with thumbnail")

# ============================================================================
# 5. REORDER: put ThumbnailURL after species
# ============================================================================

cols = df.columns.tolist()
if 'ThumbnailURL' in cols:
    cols.remove('ThumbnailURL')
species_idx = cols.index('species') if 'species' in cols else 2
cols.insert(species_idx + 1, 'ThumbnailURL')
df = df[cols]

# ============================================================================
# 6. SAVE
# ============================================================================

output_file = sys.argv[2]
df.to_csv(output_file, sep='\t', index=False)

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"\n✓ ThumbnailURL added for {thumbnail_count:,} specimens")
print(f"✓ Image source: BOLD CAOS API (https://caos.boldsystems.org)")
print(f"✓ Saved to: {output_file}")
print(f"\nIn Taxonium: thumbnails appear automatically when clicking tips.")
print("\n" + "=" * 80 + "\n")
