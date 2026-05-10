#!/usr/bin/env python3
"""
Generate jitools/resources/enharmonic_lookup_table.csv.

The table contains all JI intervals with valid HEJI2 notation up to MAX_SYMBOLS
accidental characters, sorted by pitch class height in cents.

Run from the project root:
    python3 scripts/generate_lookup_table.py
"""
from __future__ import annotations
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from jitools import generate_enharmonic_lookup_table
from jitools.constants import RESOURCES_DIRECTORY

MAX_SYMBOLS = 3
MAX_PRIME_3 = 70
MAX_PRIME_5 = 4

if __name__ == "__main__":
    output_path = os.path.join(RESOURCES_DIRECTORY, "enharmonic_lookup_table.csv")
    print(f"Generating lookup table "
          f"(MAX_SYMBOLS={MAX_SYMBOLS}, "
          f"prime-3 range ±{MAX_PRIME_3}, prime-5 range ±{MAX_PRIME_5})...")
    results = generate_enharmonic_lookup_table(
        max_symbols=MAX_SYMBOLS,
        max_prime_3=MAX_PRIME_3,
        max_prime_5=MAX_PRIME_5,
        output_path=output_path,
        verbose=True)
    print(f"Done: {len(results):,} entries.")
    print(f"Written to {output_path}")
