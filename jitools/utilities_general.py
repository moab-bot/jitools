from __future__ import annotations
import math
from fractions import Fraction
from functools import reduce

def tuple_to_fraction(t: tuple[int, int]) -> Fraction:
    f = Fraction(t[0], t[1])
    return(f)

def tuples_to_fractions(l: list[tuple[int, int]]) -> list[Fraction]:
    output = [tuple_to_fraction(x) for x in l]
    return(output)

def flop(lists: list[list]) -> list[list]:
    """Transpose a list-of-lists (rows→columns), truncating to the shortest row."""
    final = []
    lens = []
    for l in lists:
        lens.append(len(l))
    leng = min(lens)
    for i in range(leng):
        k = []
        for l in lists:
          k.append(l[i])
        final.append(k)
    return(final)

def lcm(list_of_integers: list[int]) -> int:
    output = reduce(lambda x, y: x * y // math.gcd(x, y), list_of_integers)
    return(output)

def convert_data_to_readable_string(d, precision: int = 5, prefix: str | bool = False, suffix: str | bool = False) -> str:
    """Format d as a string, rounding floats to precision decimal places."""
    if isinstance(d, float):
        formatted_string = str(round(d, precision))
    else:
        formatted_string = str(d)
    if prefix:
        formatted_string = prefix + formatted_string
    if suffix:
        formatted_string = formatted_string + suffix
    return(formatted_string)
