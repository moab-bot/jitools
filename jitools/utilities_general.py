import math
from fractions import Fraction
from functools import reduce

def tuple_to_fraction(t):
    f = Fraction(t[0], t[1])
    return(f)

def tuples_to_fractions(l):
    output = [tuple_to_fraction(x) for x in l]
    return(output)

def flop(lists):
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

def lcm(list_of_integers):
    output = reduce(lambda x, y: x * y // math.gcd(x, y), list_of_integers)
    return(output)

def convert_data_to_readable_string(d, precision = 5, prefix = False, suffix = False):
    if isinstance(d, float):
        formatted_string = str(round(d, precision))
    else:
        formatted_string = str(d)
    if prefix:
        formatted_string = prefix + formatted_string
    if suffix:
        formatted_string = formatted_string + suffix
    return(formatted_string)