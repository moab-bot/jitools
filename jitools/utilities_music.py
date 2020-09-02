from math import log2

def cpsmidi(freq, ref_freq = 440, ref_keynum = 69):
    keynum = ref_keynum + 12 * log2(freq / ref_freq)
    return(keynum)

def midicps(keynum, ref_keynum = 69, ref_freq = 440):
    freq = 2**((keynum - ref_keynum) / 12) * ref_freq
    return(freq)