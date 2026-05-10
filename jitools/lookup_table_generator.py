from __future__ import annotations
import csv
import math
import multiprocessing
import time
from itertools import combinations


HI_PRIMES = [11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]


def _seven_chars(exp7: int) -> int:
    a = abs(exp7)
    return a // 2 + a % 2


def _hi_combos(max_chars: int) -> list[list[tuple[int, int]]]:
    n = len(HI_PRIMES)
    result: list[list[tuple[int, int]]] = [[]]

    if max_chars >= 1:
        for i in range(n):
            for exp in range(1, max_chars + 1):
                for sign in (1, -1):
                    result.append([(i, sign * exp)])

    if max_chars >= 2:
        for i, j in combinations(range(n), 2):
            for e1 in range(1, max_chars):
                for e2 in range(1, max_chars - e1 + 1):
                    for s1 in (1, -1):
                        for s2 in (1, -1):
                            result.append([(i, s1 * e1), (j, s2 * e2)])

    if max_chars >= 3:
        for i, j, k in combinations(range(n), 3):
            for s1 in (1, -1):
                for s2 in (1, -1):
                    for s3 in (1, -1):
                        result.append([(i, s1), (j, s2), (k, s3)])

    return result


def build_templates(max_chars: int) -> list[tuple[int, list[tuple[int, int]]]]:
    templates = []
    for exp7 in range(-6, 7):
        chars_7 = _seven_chars(exp7)
        if chars_7 > max_chars:
            continue
        for hi in _hi_combos(max_chars - chars_7):
            templates.append((exp7, hi))
    return templates


def _process_chunk(args: tuple) -> list[tuple[list[int], float]]:
    from jitools import Pitch

    template_chunk, prime5_range, prime3_range, max_symbols = args
    seen: dict[int, tuple[list[int], float]] = {}

    for exp7, hi in template_chunk:
        for exp5 in prime5_range:
            for exp3 in prime3_range:
                monzo = [0] * 15
                monzo[1] = exp3
                monzo[2] = exp5
                monzo[3] = exp7
                for idx, exp in hi:
                    monzo[4 + idx] = exp

                p = Pitch(p=monzo)
                if p.accidental_string == "undefined":
                    continue
                if isinstance(p.num_symbols, str) or p.num_symbols > max_symbols:
                    continue

                pc = p.distance_in_cents_from_reference % 1200.0
                key = round(pc * 1_000_000)
                if key not in seen:
                    seen[key] = (list(p.normalized_monzo), pc)

    return list(seen.values())


def generate_enharmonic_lookup_table(
        max_symbols: int = 3,
        max_prime_3: int = 70,
        max_prime_5: int = 4,
        output_path: str | None = None,
        workers: int | None = None,
        verbose: bool = False) -> list[tuple[list[int], float]]:
    """Generate a table of JI intervals with valid HEJI2 notation.

    Parameters
    ----------
    max_symbols : int
        Maximum number of accidental characters (default 3).
    max_prime_3 : int
        Search bound for the prime-3 exponent; range is ±max_prime_3.
    max_prime_5 : int
        Search bound for the prime-5 exponent; range is ±max_prime_5.
    output_path : str or None
        If provided, write results to a CSV file at this path.
    workers : int or None
        Number of worker processes. Defaults to cpu_count - 1. Pass workers=1
        to disable multiprocessing entirely, which is useful in Jupyter notebooks,
        frozen/embedded environments, or anywhere subprocess spawning is unreliable.
    verbose : bool
        Print progress to stdout.

    Returns
    -------
    list of (monzo, pitch_class_height_in_cents) pairs, sorted by pitch class.
    """
    if workers is None:
        workers = max(1, multiprocessing.cpu_count() - 1)

    prime3_range = list(range(-max_prime_3, max_prime_3 + 1))
    prime5_range = list(range(-max_prime_5, max_prime_5 + 1))

    templates = build_templates(max_chars=max_symbols - 1)
    total = len(templates) * len(prime5_range) * len(prime3_range)

    if verbose:
        print(f"  {len(templates):,} templates, {total:,} candidates, {workers} workers")

    chunk_size = max(1, math.ceil(len(templates) / workers))
    chunks = [templates[i:i + chunk_size]
              for i in range(0, len(templates), chunk_size)]
    args = [(chunk, prime5_range, prime3_range, max_symbols) for chunk in chunks]

    t0 = time.time()
    if workers == 1:
        chunk_results = [_process_chunk(arg) for arg in args]
    else:
        with multiprocessing.Pool(processes=workers) as pool:
            chunk_results = pool.map(_process_chunk, args)

    merged: dict[int, tuple[list[int], float]] = {}
    for chunk in chunk_results:
        for monzo, pc in chunk:
            key = round(pc * 1_000_000)
            if key not in merged:
                merged[key] = (monzo, pc)

    results = sorted(merged.values(), key=lambda x: x[1])

    if verbose:
        print(f"  {len(results):,} entries in {time.time() - t0:.1f}s")

    if output_path is not None:
        with open(output_path, "w", newline="") as f:
            writer = csv.writer(f)
            for monzo, pc in results:
                writer.writerow([str(monzo), pc])

    return results
