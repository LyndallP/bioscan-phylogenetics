#!/usr/bin/env python3
"""
Fetch specimen country data from BOLD v5 API.
Uses the new portal.boldsystems.org API with query tokens.

Usage:
    python scripts/08_fetch_bold_v5_country_data.py <processid_file> <output_file> --api-key <key>
"""

import requests
import pandas as pd
import time
import sys
import json
from pathlib import Path

def query_bold_v5(processids, api_key, batch_size=20):
    """
    Query BOLD v5 API for specimen data.
    
    Args:
        processids: List of process IDs
        api_key: BOLD API key
        batch_size: Number of IDs per query (v5 can handle more)
    
    Returns:
        DataFrame with specimen data
    """
    all_results = []
    
    # Split into batches
    batches = [processids[i:i+batch_size] for i in range(0, len(processids), batch_size)]
    
    print(f"Querying {len(processids)} specimens in {len(batches)} batches of {batch_size}")
    
    for i, batch in enumerate(batches, 1):
        # Build query string: ids:processid:ID1;ids:processid:ID2;...
        query_parts = [f"ids:processid:{pid}" for pid in batch]
        query_string = ";".join(query_parts)
        
        try:
            print(f"  Batch {i}/{len(batches)}: {len(batch)} specimens...", end=" ", flush=True)
            
            # Get query token (skip preprocessor - it's optional)
            query_url = "https://portal.boldsystems.org/api/query"
            query_response = requests.get(
                query_url,
                params={
                    "query": query_string,
                    "extent": "full"  # Get all fields
                },
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=30
            )
            
            if query_response.status_code != 200:
                print(f"✗ Query failed: {query_response.status_code}")
                continue
            
            query_data = query_response.json()
            query_id = query_data.get('query_id')
            
            if not query_id:
                print(f"✗ No query_id returned")
                continue
            
            # Step 2: Download data
            download_url = f"https://portal.boldsystems.org/api/documents/{query_id}/download"
            download_response = requests.get(
                download_url,
                params={"format": "tsv"},  # TSV format
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=60
            )
            
            if download_response.status_code != 200:
                print(f"✗ Download failed: {download_response.status_code}")
                continue
            
            # Parse TSV response
            from io import StringIO
            df = pd.read_csv(StringIO(download_response.text), sep='\t')
            
            # Extract relevant fields
            for _, row in df.iterrows():
                all_results.append({
                    'processid': row.get('processid'),
                    'country_ocean': row.get('country/ocean'),
                    'province_state': row.get('province/state'),
                    'species': row.get('species'),
                    'bin_uri': row.get('bin_uri'),
                    'lat': row.get('lat'),
                    'lon': row.get('lon')
                })
            
            print(f"✓ {len(df)} specimens")
            
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Rate limiting
        if i < len(batches):
            time.sleep(1)
    
    return pd.DataFrame(all_results)

def main():
    if len(sys.argv) < 5 or '--api-key' not in sys.argv:
        print("Usage: python 08_fetch_bold_v5_country_data.py <processid_file> <output_file> --api-key <key>")
        sys.exit(1)
    
    processid_file = sys.argv[1]
    output_file = sys.argv[2]
    api_key_idx = sys.argv.index('--api-key') + 1
    api_key = sys.argv[api_key_idx]
    
    batch_size = 20  # Default
    if '--batch-size' in sys.argv:
        batch_size_idx = sys.argv.index('--batch-size') + 1
        batch_size = int(sys.argv[batch_size_idx])
    
    batch_size = 20  # Default
    if '--batch-size' in sys.argv:
        batch_size_idx = sys.argv.index('--batch-size') + 1
        batch_size = int(sys.argv[batch_size_idx])
    
    print(f"\n=== BOLD v5 API Country Data Fetcher ===")
    print(f"Input: {processid_file}")
    print(f"Output: {output_file}\n")
    
    # Load process IDs
    with open(processid_file, 'r') as f:
        processids = [line.strip() for line in f if line.strip()]
    
    print(f"Loaded {len(processids)} process IDs")
    
    # Fetch data
    results = query_bold_v5(processids, api_key, batch_size=batch_size)
    
    # Save results
    if len(results) > 0:
        results.to_csv(output_file, sep='\t', index=False)
        print(f"\n✓ Saved {len(results)} records to: {output_file}")
        
        # Summary
        print(f"\n=== Summary ===")
        print(f"Records retrieved: {len(results)}/{len(processids)}")
        print(f"With country data: {results['country_ocean'].notna().sum()}")
        print(f"\nTop countries:")
        print(results['country_ocean'].value_counts().head(15))
    else:
        print("\n⚠ No results retrieved")

if __name__ == '__main__':
    main()
