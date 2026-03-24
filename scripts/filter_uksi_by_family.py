#!/usr/bin/env python3
"""
Filter a full arthropod UKSI gap-analysis CSV to a single family.

The ``filtered_gap_analysis.csv`` produced by the BIOSCAN gap-analysis
workflow covers all arthropod families.  This script filters it to one
family and writes the result to a new CSV that can be passed as ``--uksi``
to ``integrate_country_metadata.py``.

Usage::
    python scripts/filter_uksi_by_family.py \\
        filtered_gap_analysis.csv \\
        sciaridae_gap_analysis.csv \\
        --family Sciaridae

    # Auto-detect family column and show available values:
    python scripts/filter_uksi_by_family.py filtered_gap_analysis.csv --list-families

Required output columns (for downstream UKSI membership checks):
  taxon_name, species_status
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path
import pandas as pd

# Candidate column names for the taxonomic family field
_FAMILY_COLUMN_CANDIDATES = ["family", "Family", "FAMILY", "taxon_family"]

# Required columns in the output
_REQUIRED_OUTPUT_COLUMNS = {"taxon_name", "species_status"}


def _detect_family_column(df: pd.DataFrame) -> str | None:
    """Return the name of the family column, or None if not found."""
    for candidate in _FAMILY_COLUMN_CANDIDATES:
        if candidate in df.columns:
            return candidate
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Filter a UKSI gap-analysis CSV to a single family.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "input_csv",
        type=Path,
        help="Full arthropod gap-analysis CSV (e.g. filtered_gap_analysis.csv)",
    )
    parser.add_argument(
        "output_csv",
        type=Path,
        nargs="?",
        help="Output filtered CSV path (required unless --list-families is used)",
    )
    parser.add_argument(
        "--family",
        required=False,
        default=None,
        help="Family name to filter to (e.g. Sciaridae)",
    )
    parser.add_argument(
        "--family-col",
        default=None,
        help=(
            "Name of the family column in the input CSV. "
            "Auto-detected if not provided."
        ),
    )
    parser.add_argument(
        "--list-families",
        action="store_true",
        help="Print all unique family values found in the CSV and exit",
    )
    args = parser.parse_args(argv)

    if not args.input_csv.exists():
        print(f"ERROR: Input CSV not found: {args.input_csv}", file=sys.stderr)
        return 1

    print(f"Reading: {args.input_csv}", file=sys.stderr)
    df = pd.read_csv(args.input_csv, dtype=str)
    print(f"  {len(df)} rows, columns: {list(df.columns)}", file=sys.stderr)

    # Detect or validate the family column
    family_col = args.family_col or _detect_family_column(df)

    if args.list_families:
        if family_col is None:
            print(
                "ERROR: Could not auto-detect a family column. "
                f"Expected one of: {_FAMILY_COLUMN_CANDIDATES}. "
                f"Actual columns: {list(df.columns)}",
                file=sys.stderr,
            )
            return 1
        families = sorted(df[family_col].dropna().unique())
        print(f"Family column: '{family_col}'")
        print(f"{len(families)} unique families:")
        for f in families:
            print(f"  {f}")
        return 0

    if args.output_csv is None:
        print("ERROR: output_csv is required (or use --list-families)", file=sys.stderr)
        return 1

    if args.family is None:
        print("ERROR: --family is required (or use --list-families to see options)", file=sys.stderr)
        return 1

    if family_col is None:
        print(
            f"ERROR: Could not auto-detect family column. "
            f"Expected one of: {_FAMILY_COLUMN_CANDIDATES}.\n"
            f"Actual columns: {list(df.columns)}\n"
            f"Use --family-col to specify the column name explicitly.",
            file=sys.stderr,
        )
        return 1

    # Filter
    mask = df[family_col].str.strip() == args.family.strip()
    filtered = df[mask].reset_index(drop=True)
    print(
        f"Filtered to family '{args.family}': {len(filtered)} rows "
        f"(from {len(df)} total).",
        file=sys.stderr,
    )

    if filtered.empty:
        print(
            f"WARNING: No rows matched family '{args.family}'. "
            f"Use --list-families to see available values.",
            file=sys.stderr,
        )

    # Validate required output columns
    missing = _REQUIRED_OUTPUT_COLUMNS - set(filtered.columns)
    if missing:
        print(
            f"ERROR: Filtered CSV is missing required columns: "
            f"{sorted(missing)}",
            file=sys.stderr,
        )
        return 1

    # Write output
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    filtered.to_csv(args.output_csv, index=False)
    print(f"Written: {args.output_csv}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
