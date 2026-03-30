#!/usr/bin/env python3
"""
add_global_columns.py — Add in_uk, in_dataset, and taxonium_link columns to
data/Arthropoda_global/arthropoda_global_metadata_FINAL.tsv.

Run from the repo root after placing the metadata file there:

    python add_global_columns.py

Re-running the script is safe — the three columns are overwritten each time,
so it stays consistent if new per-family datasets are added to data/.

Column definitions
------------------
in_uk          True/False — family is present in the UK according to the
               ORDER_FAMILIES mapping in generate_index.py.
in_dataset     Dataset name(s) if the family has a complete tree + metadata
               folder under data/.  Currently "BIOSCAN" for any folder present;
               empty string if the family has not been processed yet.
               Comma-separated if a family ever appears in multiple datasets
               (e.g. "BIOSCAN; DTOL").
taxonium_link  Markdown link "[🌳 Open tree](https://taxonium.org/…)" pointing
               to the per-family Taxonium tree, or empty if not in any dataset.
"""

import csv
import sys
from pathlib import Path

# Pull constants and helpers from generate_index.py (repo root)
sys.path.insert(0, str(Path(__file__).parent))
from generate_index import ORDER_FAMILIES, taxonium_url, DATA_DIR  # noqa: E402

GLOBAL_FAMILY = "Arthropoda_global"
META_FILE = DATA_DIR / GLOBAL_FAMILY / "arthropoda_global_metadata_FINAL.tsv"

# Flat set of all UK families from generate_index.ORDER_FAMILIES
UK_FAMILIES = {fam for families in ORDER_FAMILIES.values() for fam in families}


def get_family_datasets():
    """Return {family: dataset_label} for all data/{Family}/ folders that have
    the expected tree + metadata pair.  Currently all such folders are BIOSCAN.
    """
    result = {}
    if not DATA_DIR.exists():
        return result
    for subdir in sorted(DATA_DIR.iterdir()):
        if not subdir.is_dir() or subdir.name == GLOBAL_FAMILY:
            continue
        fam = subdir.name
        if (subdir / f"{fam}_final_tree.newick").exists() and \
           (subdir / f"{fam.lower()}_metadata_FINAL.tsv").exists():
            result[fam] = "BIOSCAN"
    return result


def main():
    if not META_FILE.exists():
        sys.exit(
            f"Error: {META_FILE} not found.\n"
            f"Place the file at data/{GLOBAL_FAMILY}/arthropoda_global_metadata_FINAL.tsv "
            "and re-run."
        )

    with open(META_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        rows = list(reader)
        fieldnames = list(reader.fieldnames)

    if not rows:
        sys.exit("Error: metadata file is empty.")

    family_datasets = get_family_datasets()

    # Append new columns if they don't already exist
    for col in ("in_uk", "in_dataset", "taxonium_link"):
        if col not in fieldnames:
            fieldnames.append(col)

    for row in rows:
        family = row.get("Family", "").strip()
        row["in_uk"] = str(family in UK_FAMILIES)
        dataset = family_datasets.get(family, "")
        row["in_dataset"] = dataset
        row["taxonium_link"] = (
            f"[🌳 Open tree]({taxonium_url(family)})" if dataset else ""
        )

    with open(META_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)

    in_uk_count = sum(1 for r in rows if r["in_uk"] == "True")
    in_dataset_count = sum(1 for r in rows if r["in_dataset"])
    print(f"Updated {META_FILE}")
    print(f"  Rows processed : {len(rows)}")
    print(f"  UK families    : {in_uk_count}")
    print(f"  In dataset     : {in_dataset_count}")


if __name__ == "__main__":
    main()
