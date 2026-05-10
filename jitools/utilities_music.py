from __future__ import annotations
from math import log2

def cpsmidi(freq: float, ref_freq: float = 440, ref_keynum: float = 69) -> float:
    keynum = ref_keynum + 12 * log2(freq / ref_freq)
    return(keynum)

def midicps(keynum: float, ref_keynum: float = 69, ref_freq: float = 440) -> float:
    freq = 2**((keynum - ref_keynum) / 12) * ref_freq
    return(freq)
