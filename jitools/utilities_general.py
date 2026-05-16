from __future__ import annotations
import math
from fractions import Fraction

def tuple_to_fraction(t: tuple[int, int]) -> Fraction:
    f = Fraction(t[0], t[1])
    return f

def tuples_to_fractions(tuples: list[tuple[int, int]]) -> list[Fraction]:
    output = [tuple_to_fraction(x) for x in tuples]
    return output

def flop(lists: list[list]) -> list[list]:
    """Transpose a list-of-lists (rows→columns), truncating to the shortest row."""
    final = []
    lens = []
    for row in lists:
        lens.append(len(row))
    leng = min(lens)
    for i in range(leng):
        col = []
        for row in lists:
            col.append(row[i])
        final.append(col)
    return final

def convert_data_to_readable_string(d: int | float | Fraction, precision: int = 5, prefix: str | None = None, suffix: str | None = None) -> str:
    """Format d as a string, rounding floats to precision decimal places."""
    if isinstance(d, float):
        formatted_string = str(round(d, precision))
    elif isinstance(d, Fraction):
        formatted_string = f"{d.numerator}/{d.denominator}"
    else:
        formatted_string = str(d)
    if prefix is not None:
        formatted_string = prefix + formatted_string
    if suffix is not None:
        formatted_string = formatted_string + suffix
    return formatted_string
