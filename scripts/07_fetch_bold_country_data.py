#!/usr/bin/env python3
"""
Fetch specimen country data from BOLD API (v4, XML format).
Generic script for any family - processes a list of processids.

Usage:
    python scripts/07_fetch_bold_country_data.py <processid_file> <output_file> [--batch-size 50]
"""

import requests
import pandas as pd
import xml.etree.ElementTree as ET
import time
import sys
from pathlib import Path

def fetch_bold_specimens(processids, batch_size=50):
    """
    Fetch specimen data from BOLD v4 API in batches.
    
    Args:
        processids: List of process IDs to query
        batch_size: Number of IDs per API request
    
    Returns:
        DataFrame with processid, country_ocean, and other metadata
    """
    base_url = "http://v4.boldsystems.org/index.php/API_Public/specimen"
    all_results = []
    
    # Split into batches
    batches = [processids[i:i+batch_size] for i in range(0, len(processids), batch_size)]
    
    print(f"Fetching {len(processids)} specimens in {len(batches)} batches of {batch_size}")
    
    for i, batch in enumerate(batches, 1):
        # Join processids with pipe separator
        ids_param = "|".join(batch)
        
        try:
            print(f"  Batch {i}/{len(batches)}: {len(batch)} specimens...", end=" ")
            response = requests.get(
                base_url,
                params={"ids": ids_param},
                timeout=30
            )
            
            if response.status_code == 200:
                # Parse XML response
                root = ET.fromstring(response.text)
                batch_count = 0
                
                for record in root.findall('record'):
                    pid = record.find('processid')
                    pid = pid.text if pid is not None else None
                    
                    # Extract BIN
                    bin_elem = record.find('bin_uri')
                    bin_uri = bin_elem.text if bin_elem is not None and bin_elem.text else None
                    
                    # Extract country from collection_event
                    country = None
                    province = None
                    collection = record.find('.//collection_event')
                    if collection is not None:
                        country_elem = collection.find('country')
                        if country_elem is not None:
                            country = country_elem.text
                        province_elem = collection.find('province_state')
                        if province_elem is not None:
                            province = province_elem.text
                    
                    # Extract species identification
                    species = None
                    taxonomy = record.find('.//taxonomy')
                    if taxonomy is not None:
                        id_elem = taxonomy.find('identification')
                        if id_elem is not None:
                            species = id_elem.text
                    
                    # Extract coordinates
                    lat = None
                    lon = None
                    coords = record.find('.//collection_event')
                    if coords is not None:
                        lat_elem = coords.find('lat')
                        lon_elem = coords.find('lon')
                        if lat_elem is not None:
                            lat = lat_elem.text
                        if lon_elem is not None:
                            lon = lon_elem.text
                    
                    all_results.append({
                        'processid': pid,
                        'country_ocean': country,
                        'province_state': province,
                        'species': species,
                        'bin_uri': bin_uri,
                        'lat': lat,
                        'lon': lon
                    })
                    batch_count += 1
                
                print(f"✓ {batch_count} specimens")
            else:
                print(f"✗ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Rate limiting: wait between batches
        if i < len(batches):
            time.sleep(0.5)
    
    return pd.DataFrame(all_results)

def main():
    if len(sys.argv) < 3:
        print("Usage: python 07_fetch_bold_country_data.py <processid_file> <output_file> [--batch-size 50]")
        sys.exit(1)
    
    processid_file = sys.argv[1]
    output_file = sys.argv[2]
    batch_size = 50
    
    # Parse optional batch size
    if len(sys.argv) > 3 and sys.argv[3] == '--batch-size':
        batch_size = int(sys.argv[4])
    
    # Load process IDs
    print(f"\n=== BOLD API Country Data Fetcher (v4, XML) ===")
    print(f"Input: {processid_file}")
    print(f"Output: {output_file}")
    print(f"Batch size: {batch_size}\n")
    
    with open(processid_file, 'r') as f:
        processids = [line.strip() for line in f if line.strip()]
    
    print(f"Loaded {len(processids)} process IDs")
    
    # Fetch data
    results = fetch_bold_specimens(processids, batch_size=batch_size)
    
    # Save results
    if len(results) > 0:
        results.to_csv(output_file, sep='\t', index=False)
        print(f"\n✓ Saved {len(results)} records to: {output_file}")
        
        # Summary
        print(f"\n=== Summary ===")
        print(f"Records retrieved: {len(results)}/{len(processids)}")
        print(f"With country data: {results['country_ocean'].notna().sum()}")
        print(f"\nTop countries:")
        print(results['country_ocean'].value_counts().head(10))
    else:
        print("\n⚠ No results retrieved")

if __name__ == '__main__':
    main()
