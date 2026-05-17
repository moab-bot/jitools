# Changelog

## 1.1.1 (2026-05-16)

### Breaking changes
- `Pitch.write_info_to_txt`, `Pitch.write_enharmonics_info_to_txt`, `Pitch.write_enharmonics_info_to_csv`,
  `PitchCollection.write_info_to_txt`, and `PitchCollection.write_info_to_csv`: the `output_directory`
  and `filename` parameters have been replaced with a single `output_path` parameter (e.g.
  `output_path="~/Desktop/myfile.txt"`), consistent with `generate_enharmonic_lookup_table` and
  standard Python file I/O conventions.
- All five write methods now default to silent output. Pass `verbose=True` to print the path of the
  written file.
- `Pitch.get_enharmonics`, `Pitch.print_enharmonics_info`, `Pitch.write_enharmonics_info_to_csv`,
  and `Pitch.write_enharmonics_info_to_txt`: the `lookup_table_path` parameter has been renamed to
  `lookup_table` and now accepts either a file path (`str`) or the list returned by
  `generate_enharmonic_lookup_table()`, allowing the generated table to be passed directly without
  a round-trip through disk.

### Bug fixes
- All write methods now correctly expand `~` in `output_path` (e.g. `"~/Desktop/myfile.txt"`).
- `Pitch.get_enharmonics` (and the methods that call it) now correctly expand `~` in `lookup_table`
  when a file path string is provided.
- `Pitch.write_enharmonics_info_to_csv`: when the search returns zero candidates, no file is written;
  `verbose=True` no longer incorrectly prints "file written to ..." in that case.

### New features
- `Pitch` and `PitchCollection` now have a `__repr__` method, so evaluating an instance
  in the console returns a readable representation (e.g. `Pitch(4/7)`,
  `PitchCollection([1/1, 5/4, 3/2])`) rather than the default Python object address.
- `jitools.__version__` is now available after `import jitools`, returning the installed package version.

### Other changes
- `generate_enharmonic_lookup_table`: `output_path` now defaults to `"jitools_lookup_table.csv"`
  (written to the current working directory); `verbose` now defaults to `True`. Previously
  `output_path` defaulted to `None` (no file written), but since a saved file is required to use
  the result with any enharmonic method, a default path was added.
- `PitchCollection.print_info` and `PitchCollection.write_info_to_txt`: the `tuneable ratios:` label
  in difference and summation tone sections is now `tuneable ratios (vs. any ratio from original chord):`
  to clarify that tuneability is assessed relative to the original chord pitches, not the resultant
  tones themselves.
- `generate_enharmonic_lookup_table` no longer requires a separate import; it is available directly
  as `jitools.generate_enharmonic_lookup_table` after `import jitools`.
- `setup.py`: added `project_urls` (Source, Bug Tracker, Changelog), `keywords`, and classifiers
  for Development Status, Intended Audience, and Topic.
- Test suite: removed the `slow` marker — all 229 tests now run by default in under 1 second.
- Added `tests/verify_readme.py` and `tests/verify_notebook.py`: scripts that verify all non-slow
  command outputs shown in the README and Jupyter tutorial match the library's actual output.

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
