"""Verify that Jupyter notebook cell outputs match what the library actually produces."""
import io
import sys
from fractions import Fraction
from jitools import Pitch, PitchCollection

PASS = "\033[32mPASS\033[0m"
FAIL = "\033[31mFAIL\033[0m"
failures = []

def check(label, actual, expected):
    if actual == expected:
        print(f"{PASS}  {label}")
    else:
        print(f"{FAIL}  {label}")
        for i, (a, e) in enumerate(zip(actual.splitlines(), expected.splitlines())):
            if a != e:
                print(f"       line {i+1}: got    {a!r}")
                print(f"               expect {e!r}")
        if len(actual.splitlines()) != len(expected.splitlines()):
            print(f"       line count: got {len(actual.splitlines())}, expected {len(expected.splitlines())}")
        failures.append(label)

def capture(fn):
    buf = io.StringIO()
    sys.stdout = buf
    fn()
    sys.stdout = sys.__stdout__
    return buf.getvalue()

# ── Section 1: Creating a Pitch ───────────────────────────────────────────────

p = Pitch(p=(3, 2))
check("Pitch(3,2) ratio/freq/cents",
      f"{p.ratio}\n{p.freq}\n{p.distance_in_cents_from_reference}",
      "3/2\n660.0\n701.955000865388")

p = Pitch(p=Fraction(7, 4))
check("Pitch(Fraction(7,4)) ratio", str(p.ratio), "7/4")

p = Pitch(p=[-1, 1])
p2 = Pitch(p=[-2, 0, 1])
check("Pitch from monzo",
      f"{p.ratio}\n{p.monzo}\n{p2.ratio}",
      "3/2\n[-1, 1]\n5/4")

# ── Section 2: Inspecting pitch properties ────────────────────────────────────

p = Pitch(p=(7, 4))
check("Pitch(7,4) properties", capture(lambda: (
    print("ratio:              ", p.ratio),
    print("monzo:              ", p.monzo),
    print("constituent primes: ", p.constituent_primes),
    print("freq (Hz):          ", round(p.freq, 3)),
    print("MIDI key number:    ", round(p.keynum, 3)),
    print("cents from ref:     ", round(p.distance_in_cents_from_reference, 4)),
    print("harmonic distance:  ", round(p.harmonic_distance, 4)),
)), """\
ratio:               7/4
monzo:               [-2, 0, 0, 1]
constituent primes:  [2, 7]
freq (Hz):           770.0
MIDI key number:     78.688
cents from ref:      968.8259
harmonic distance:   4.8074
""")

check("Pitch(7,4) HEJI2 notation", capture(lambda: (
    print("accidental string:  ", p.accidental_string),
    print("letter name:        ", p.letter_name),
    print("num symbols:        ", p.num_symbols),
    print("letter+octave+cents:", p.letter_name_and_octave_and_cents),
)), """\
accidental string:   <
letter name:         G
num symbols:         1
letter+octave+cents: G5 -31.17409
""")

p = Pitch(p=(1, 3))
check("Pitch(1,3) normalized", capture(lambda: (
    print("ratio:             ", p.ratio),
    print("normalized ratio:  ", p.normalized_ratio),
    print("normalized monzo:  ", p.normalized_monzo),
)), """\
ratio:              1/3
normalized ratio:   4/3
normalized monzo:   [2, -1]
""")

check("Pitch(5,4) print_info()",
      capture(lambda: Pitch(p=(5, 4)).print_info()),
      """\

BASIC INFO
ratio: 5/4
monzo: [-2, 0, 1]
constituent primes: [2, 5]
frequency (Hz): 550.0
MIDI key number: 72.86314
distance from 1/1 (cents): 386.31371
harmonic distance: 4.32193
Helmholtz-Ellis notation (text string, letter name): ('u', 'C')
12-ED2 pitch and cent deviation: C#/Db5 -13.68629

""")

# ── Section 3: PitchCollection ────────────────────────────────────────────────

triad = PitchCollection(pc=[(1, 1), (5, 4), (3, 2)])

check("triad basic attributes", capture(lambda: (
    print("ratios:              ", [str(r) for r in triad.ratios]),
    print("constituent primes:  ", triad.constituent_primes),
    print("harmonics:           ", triad.harmonics),
    print("least common partial:", triad.least_common_partial),
    print("periodicity pitch:   ", round(triad.periodicity_pitch, 2), "Hz"),
    print("HD sum:              ", round(triad.hd_sum, 4)),
    print("HD average:          ", round(triad.hd_avg, 4)),
)), """\
ratios:               ['1', '5/4', '3/2']
constituent primes:   [2, 3, 5]
harmonics:            [4, 5, 6]
least common partial: 60
periodicity pitch:    110.0 Hz
HD sum:               6.9069
HD average:           2.3023
""")

check("triad intervals", capture(lambda: (
    print("all intervals:"),
    [print(" ", i) for i in triad.intervals],
    print("\ntuneable intervals (Sabat-Schweinitz):"),
    [print(" ", i) for i in triad.tuneable_intervals],
)), """\
all intervals:
  6/5
  5/4
  3/2

tuneable intervals (Sabat-Schweinitz):
  6/5
  5/4
  3/2
""")

check("triad resultant tones", capture(lambda: (
    print("difference tones:         ", [str(r) for r in triad.difference_tones]),
    print("tuneable difference tones:", [str(r) for r in triad.tuneable_difference_tones]),
    print("summation tones:          ", [str(r) for r in triad.summation_tones]),
)), """\
difference tones:          ['1/4', '1/2']
tuneable difference tones: ['1/4', '1/2']
summation tones:           ['9/4', '5/2', '11/4']
""")

check("triad HEJI notations",
      capture(lambda: [print(f"  {letter}  {acc}") for acc, letter in triad.notations]),
      "  A  n\n  C  u\n  E  n\n")

check("triad print_info()",
      capture(lambda: triad.print_info()),
      """\

BASIC INFO
ratios: ['1/1', '5/4', '3/2']
frequencies (Hz): ['440.0', '550.0', '660.0']
MIDI key numbers: ['69.0', '72.86314', '76.01955']
Helmholtz-Ellis notations (text string, letter name): [('n', 'A'), ('u', 'C'), ('n', 'E')]
12-ED2 pitch and cent deviations: ['A4 +0.0', 'C#/Db5 -13.68629', 'E5 +1.955']
harmonic constellation: 4:5:6
sequential intervals: ['5/4', '6/5']
normalized ratios: ['1/1', '5/4', '3/2']
inversion: ['1/1', '6/5', '3/2']

""")

seventh = PitchCollection(pc=[(1, 1), (5, 4), (3, 2), (7, 4)])
check("seventh chord attributes", capture(lambda: (
    print("harmonics:    ", seventh.harmonics),
    print("HD sum:       ", round(seventh.hd_sum, 4)),
    print("constituent:  ", seventh.constituent_primes),
)), """\
harmonics:     [4, 5, 6, 7]
HD sum:        11.7142
constituent:   [2, 3, 5, 7]
""")

# ── sort_by ───────────────────────────────────────────────────────────────────

col = PitchCollection(pc=[(3, 2), (1, 1), (5, 4)])
before = [str(r) for r in col.ratios]
col.sort_by("ratios")
after = [str(r) for r in col.ratios]
check("sort_by ratios",
      f"before sort: {before}\nafter sort:  {after}",
      "before sort: ['1', '5/4', '3/2']\nafter sort:  ['1', '5/4', '3/2']")

# ── transpose ─────────────────────────────────────────────────────────────────

col = PitchCollection(pc=[(1, 1), (5, 4), (3, 2)])
before = [str(r) for r in col.ratios]
col.transpose((2, 3))
after = [str(r) for r in col.ratios]
check("transpose down a fifth",
      f"before transpose: {before}\nafter transpose:  {after}",
      "before transpose: ['1', '5/4', '3/2']\nafter transpose:  ['2/3', '5/6', '1']")

# ── update ────────────────────────────────────────────────────────────────────

p = Pitch(p=(3, 2))
r1 = str(p.ratio)
p.update(p=(5, 4))
r2 = str(p.ratio)
check("Pitch.update()", f"{r1}\n{r2}", "3/2\n5/4")

# ── Section 4: Reference pitch ────────────────────────────────────────────────

p = Pitch(p=(3, 2), rp="C4", rf=261.63)
check("Pitch with C4 reference", capture(lambda: (
    print("freq:   ", round(p.freq, 2), "Hz"),
    print("letter: ", p.letter_name),
    print("cents:  ", round(p.distance_in_cents_from_reference, 2)),
)), """\
freq:    392.44 Hz
letter:  G
cents:   701.96
""")

col = PitchCollection(pc=[(1, 1), (5, 4), (3, 2)], rp="C4", rf=261.63)
check("PitchCollection with C4 reference",
      capture(lambda: print("freqs:", [round(f, 2) for f in col.freqs])),
      "freqs: [261.63, 327.04, 392.44]\n")

# ── Summary ───────────────────────────────────────────────────────────────────

print()
if failures:
    print(f"  {len(failures)} failure(s): {', '.join(failures)}")
else:
    print("  All checks passed.")
