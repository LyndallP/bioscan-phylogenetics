#!/usr/bin/env python3
"""
Robust BOLD v5 API fetcher with retry logic and rate limiting.
Handles 503 errors and ensures all specimens are retrieved.

Usage:
    python scripts/09_fetch_bold_v5_robust.py <processid_file> <output_file> --api-key <key>
"""

import requests
import pandas as pd
import time
import sys
from io import StringIO

def fetch_batch_with_retry(batch, api_key, max_retries=5):
    """
    Fetch a batch with exponential backoff on failures.
    
    Args:
        batch: List of process IDs
        api_key: BOLD API key
        max_retries: Maximum retry attempts
    
    Returns:
        List of specimen records or None on failure
    """
    query_string = ";".join([f"ids:processid:{pid}" for pid in batch])
    
    for attempt in range(max_retries):
        try:
            # Step 1: Get query token
            query_response = requests.get(
                "https://portal.boldsystems.org/api/query",
                params={"query": query_string, "extent": "full"},
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=30
            )
            
            if query_response.status_code == 422:
                # Unprocessable - these IDs might not exist
                return None
            
            if query_response.status_code != 200:
                if query_response.status_code == 503:
                    # Server overloaded - wait longer
                    wait_time = 10 * (2 ** attempt)  # Exponential backoff
                    print(f"503 error, waiting {wait_time}s...", end=" ", flush=True)
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"Query error {query_response.status_code}", end=" ", flush=True)
                    return None
            
            query_data = query_response.json()
            query_id = query_data.get('query_id')
            
            if not query_id:
                return None
            
            # Step 2: Download data
            download_response = requests.get(
                f"https://portal.boldsystems.org/api/documents/{query_id}/download",
                params={"format": "tsv"},
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=60
            )
            
            if download_response.status_code == 503:
                wait_time = 10 * (2 ** attempt)
                print(f"503 error, waiting {wait_time}s...", end=" ", flush=True)
                time.sleep(wait_time)
                continue
            
            if download_response.status_code != 200:
                return None
            
            # Parse TSV
            df = pd.read_csv(StringIO(download_response.text), sep='\t')
            
            results = []
            for _, row in df.iterrows():
                results.append({
                    'processid': row.get('processid'),
                    'country_ocean': row.get('country/ocean'),
                    'province_state': row.get('province/state'),
                    'species': row.get('species'),
                    'bin_uri': row.get('bin_uri'),
                    'lat': row.get('lat'),
                    'lon': row.get('lon')
                })
            
            return results
            
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 5 * (2 ** attempt)
                print(f"Error (retry {attempt+1}/{max_retries})...", end=" ", flush=True)
                time.sleep(wait_time)
            else:
                print(f"Failed after {max_retries} attempts: {e}", end=" ", flush=True)
                return None
    
    return None

def main():
    if len(sys.argv) < 5 or '--api-key' not in sys.argv:
        print("Usage: python 09_fetch_bold_v5_robust.py <processid_file> <output_file> --api-key <key>")
        sys.exit(1)
    
    processid_file = sys.argv[1]
    output_file = sys.argv[2]
    api_key_idx = sys.argv.index('--api-key') + 1
    api_key = sys.argv[api_key_idx]
    
    batch_size = 5  # Conservative batch size
    base_delay = 3  # 3 seconds between successful batches
    
    print(f"\n=== BOLD v5 Robust Fetcher ===")
    print(f"Input: {processid_file}")
    print(f"Output: {output_file}")
    print(f"Batch size: {batch_size}, Base delay: {base_delay}s\n")
    
    # Load process IDs
    with open(processid_file, 'r') as f:
        processids = [line.strip() for line in f if line.strip()]
    
    print(f"Total specimens: {len(processids)}")
    
    # Split into batches
    batches = [processids[i:i+batch_size] for i in range(0, len(processids), batch_size)]
    print(f"Batches: {len(batches)}\n")
    
    all_results = []
    
    for i, batch in enumerate(batches, 1):
        print(f"Batch {i}/{len(batches)} ({len(batch)} IDs)...", end=" ", flush=True)
        
        results = fetch_batch_with_retry(batch, api_key)
        
        if results:
            all_results.extend(results)
            print(f"✓ Got {len(results)} specimens")
        else:
            print(f"✗ Failed")
        
        # Rate limiting between batches
        if i < len(batches):
            time.sleep(base_delay)
    
    # Save results
    if len(all_results) > 0:
        df = pd.DataFrame(all_results)
        df.to_csv(output_file, sep='\t', index=False)
        
        print(f"\n=== Summary ===")
        print(f"Successfully retrieved: {len(df)}/{len(processids)} specimens")
        print(f"With country data: {df['country_ocean'].notna().sum()}")
        print(f"\nTop countries:")
        print(df['country_ocean'].value_counts().head(15))
        print(f"\n✓ Saved to: {output_file}")
    else:
        print("\n⚠ No results retrieved")

if __name__ == '__main__':
    main()
