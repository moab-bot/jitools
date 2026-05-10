import jitools
import math
import itertools
import random
import fractions

base_intervals = list(itertools.combinations([45, 37, 29, 21, 13, 8, 5], 2))

for bi in base_intervals:
    pci = jitools.Pitch(bi)
    pci.get_enharmonics
    pci.print_info()