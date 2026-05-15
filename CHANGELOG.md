# Changelog

## 1.0.0 (2026-05-14)

### Breaking changes
- Minimum Python version raised from 3.9 to 3.10.
- `Pitch.__init__` and `PitchCollection.__init__` now raise `ValueError` or `TypeError`
  for invalid inputs (previously produced cryptic internal errors or silent failures).

### New features
- `_harmonic_intersection`: antichain optimization reduces the inclusion-exclusion
  subset count for harmonic series and other divisibility-rich collections from 2^n
  to 2 (or close to it), making large collections fast in practice.
- `_harmonic_intersection`: returns `None` for collections with more than 24
  independent harmonics (after antichain filtering) rather than hanging; the
  `harmonic_intersection` and `harmonic_disjunction` attributes display
  `N/A (more than 24 independent harmonics)` in those cases.
- Docstrings added to all public methods: `Pitch.__init__`, `Pitch.get_enharmonics`,
  `Pitch.print_info`, `Pitch.print_enharmonics_info`, `Pitch.write_enharmonics_info_to_csv`,
  `Pitch.write_enharmonics_info_to_txt`, `Pitch.create_strings_for_print_and_txt`,
  `Pitch.write_info_to_txt`, `PitchCollection.__init__`, `PitchCollection.print_info`,
  `PitchCollection.write_info_to_csv`, `PitchCollection.write_info_to_txt`.

### Performance improvements
- `_harmonic_intersection`: replaced `Fraction` object creation in the
  inclusion-exclusion loop with integer numerator/denominator accumulation, and
  `reduce(lambda x,y: x*y//gcd(x,y), ...)` with `math.lcm(*c)` (C-level builtin,
  Python 3.10+). Combined speedup: ~5x.
- `_intervals_and_resultant_tones`: replaced an O(n^4) nested loop with an O(n^2)
  dict-based index. Speedup: ~17x at n=8, ~11x at n=12.
- `_is_tuneable`: replaced an O(183) list search with an O(1) set lookup.

### Other changes
- Added Python 3.10, 3.11, 3.12, 3.13 classifiers to `setup.py`.
- Improved README formatting: syntax-highlighted code blocks, inline code,
  table of contents, section hierarchy, trimmed output blocks.
- `jitools.PitchCollection()` section moved before Enharmonic Search in README
  to match the structure of the Jupyter tutorial.
- "Generating a Custom Lookup Table" section added to README.
- Jupyter notebook tutorial (`examples/jitools_tutorial.ipynb`) updated:
  ratio lists now display as `[str(r) for r in col.ratios]`; "Finding enharmonic
  equivalents" section reordered to appear before "Generating a custom lookup table".

## 0.3

- Initial public release.
