"""Verify that README command outputs match what the library actually produces."""
import io
import sys
import jitools

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

# ── jitools.Pitch() attributes ─────────────────────────────────────────────────

p = jitools.Pitch(p=(3, 2))
check("Pitch(3,2).freq",                      str(p.freq),                          "660.0")
check("Pitch(3,2).keynum",                    str(p.keynum),                        "76.01955000865388")
check("Pitch(3,2).distance_in_cents",         str(p.distance_in_cents_from_reference), "701.955000865388")

p = jitools.Pitch(p=(3, 2), rp="G4", rf=392)
check("Pitch(3,2,G4).freq",                   str(p.freq),                          "588.0")
check("Pitch(3,2,G4).keynum",                 str(p.keynum),                        "74.01955000865388")
check("Pitch(3,2,G4).distance_in_cents",      str(p.distance_in_cents_from_reference), "701.955000865388")

p = jitools.Pitch(p=(4, 7))
check("Pitch(4,7).letter_name_and_octave_and_cents", p.letter_name_and_octave_and_cents, "B3 +31.17409")

p = jitools.Pitch(p=(25, 13))
check("Pitch(25,13).notation",                str(p.notation),                      "('9t', 'G')")

# ── Pitch.print_info() ─────────────────────────────────────────────────────────

expected_pitch_print = """\

BASIC INFO
ratio: 17/11
monzo: [0, 0, 0, 0, -1, 0, 1]
constituent primes: [11, 17]
frequency (Hz): 680.0
MIDI key number: 76.53637
distance from 1/1 (cents): 753.63747
harmonic distance: 7.54689
Helmholtz-Ellis notation (text string, letter name): (':5v', 'E')
12-ED2 pitch and cent deviation: F5 -46.36253

"""
check("Pitch(17,11).print_info()",
      capture(lambda: jitools.Pitch(p=(17, 11)).print_info()),
      expected_pitch_print)

# ── PitchCollection() attributes ──────────────────────────────────────────────

chord = jitools.PitchCollection([(1, 1), (5, 4), (3, 2)])
check("PC([1,5/4,3/2]).ratios",    str(chord.ratios),   "[Fraction(1, 1), Fraction(5, 4), Fraction(3, 2)]")
check("PC([1,5/4,3/2]).freqs",     str(chord.freqs),    "[440.0, 550.0, 660.0]")
check("PC([1,5/4,3/2]).keynums",   str(chord.keynums),  "[69.0, 72.86313713864834, 76.01955000865388]")
check("PC([1,5/4,3/2]).intervals", str(chord.intervals),"[Fraction(6, 5), Fraction(5, 4), Fraction(3, 2)]")

# ── PitchCollection.print_info() ── basic ─────────────────────────────────────

chord2 = jitools.PitchCollection([(7, 8), (9, 7), (13, 8), (11, 6)])

expected_basic = """\

BASIC INFO
ratios: ['7/8', '9/7', '13/8', '11/6']
frequencies (Hz): ['385.0', '565.71429', '715.0', '806.66667']
MIDI key numbers: ['66.68826', '73.35084', '77.40528', '79.49363']
Helmholtz-Ellis notations (text string, letter name): [('<', 'G'), ('>v', 'C'), ('0v', 'F'), ('4', 'G')]
12-ED2 pitch and cent deviations: ['G4 -31.17409', 'C#/Db5 +35.0841', 'F5 +40.52766', 'G5 +49.36294']
harmonic constellation: 147:216:273:308
sequential intervals: ['72/49', '91/72', '44/39']
normalized ratios: ['9/7', '13/8', '7/4', '11/6']
inversion: ['7/8', '77/78', '539/432', '11/6']

"""
check("PC print_info() basic", capture(lambda: chord2.print_info()), expected_basic)

# ── quantitative ──────────────────────────────────────────────────────────────

expected_quant = """\

QUANTITATIVE INFO
average ratio: 59/42
minimum ratio: 7/8
maximum ratio: 11/6
ratio span: 44/21
average frequency (Hz): 618.09524
minimum frequency (Hz): 385.0
maximum frequency (Hz): 806.66667
frequency span (Hz): 421.66667
average MIDI key number: 74.88391
minimum MIDI key number: 66.68826
maximum MIDI key number: 79.49363
MIDI key number span: 12.80537
span in cents: 1280.53704

"""
check("PC print_info('quantitative')", capture(lambda: chord2.print_info("quantitative")), expected_quant)

# ── analytic ──────────────────────────────────────────────────────────────────

expected_analytic = """\

ANALYTIC INFO
all intervals: ['44/39', '91/72', '77/54', '72/49', '13/7', '44/21']
tuneable intervals: ['13/7']
periodicity pitch (Hz): 2.61905
least common partial (of periodicity pitch): 1513512
least common partial frequency (Hz): 3963960.0
constituent primes: [2, 3, 7, 11, 13]
harmonic distance sum: 24.52947
average harmonic distance: 6.13237
harmonic intersection: 4391/252252 (0.01741)
harmonic disjunction: 247861/252252 (0.98259)

"""
check("PC print_info('analytic')", capture(lambda: chord2.print_info("analytic")), expected_analytic)

# ── normalized ────────────────────────────────────────────────────────────────

expected_normalized = """\

NORMALIZED INFO
ratios: ['9/7', '13/8', '7/4', '11/6']
frequencies (Hz): ['565.71429', '715.0', '770.0', '806.66667']
MIDI key numbers: ['73.35084', '77.40528', '78.68826', '79.49363']
Helmholtz-Ellis notations (text string, letter name): [('>v', 'C'), ('0v', 'F'), ('<', 'G'), ('4', 'G')]
12-ED2 pitch and cent deviations: ['C#/Db5 +35.0841', 'F5 +40.52766', 'G5 -31.17409', 'G5 +49.36294']
harmonic constellation: 216:273:294:308
sequential intervals: ['91/72', '14/13', '22/21']
inversion: ['9/7', '66/49', '132/91', '11/6']

"""
check("PC print_info('normalized')", capture(lambda: chord2.print_info("normalized")), expected_normalized)

# ── inversion ─────────────────────────────────────────────────────────────────

expected_inversion = """\

INVERSION INFO
ratios: ['7/8', '77/78', '539/432', '11/6']
frequencies (Hz): ['385.0', '434.35897', '548.98148', '806.66667']
MIDI key numbers: ['66.68826', '68.77661', '72.83105', '79.49363']
Helmholtz-Ellis notations (text string, letter name): [('<', 'G'), ('94<e', 'A'), ('4,e', 'D'), ('4', 'G')]
12-ED2 pitch and cent deviations: ['G4 -31.17409', 'A4 -22.33881', 'C#/Db5 -16.89525', 'G5 +49.36294']
harmonic constellation: 4914:5544:7007:10296
sequential intervals: ['44/39', '91/72', '72/49']
normalized ratios: ['539/432', '7/4', '11/6', '77/39']

"""
check("PC print_info('inversion')", capture(lambda: chord2.print_info("inversion")), expected_inversion)

# ── resultants ────────────────────────────────────────────────────────────────

expected_resultants = """\

FIRST-ORDER DIFFERENCE TONES
ratios: ['5/24', '19/56', '23/56', '23/42', '3/4', '23/24']
tuneable ratios (vs. any ratio from original chord): ['5/24', '3/4']
frequencies (Hz): ['91.66667', '149.28571', '180.71429', '240.95238', '330.0', '421.66667']
MIDI key numbers: ['41.84359', '50.28687', '53.59448', '58.57493', '64.01955', '68.26319']
Helmholtz-Ellis notations (text string, letter name): [('u', 'F'), ('/>', 'D'), ('3>v', 'E'), ('3>v', 'A'), ('n', 'E'), ('3v', 'G')]
12-ED2 pitch and cent deviations: ['F#/Gb2 -15.64129', 'D3 +28.68711', 'F#/Gb3 -40.55156', 'B3 -42.50656', 'E4 +1.955', 'G#/Ab4 +26.31935']

FIRST-ORDER SUMMATION TONES
ratios: ['121/56', '5/2', '65/24', '163/56', '131/42', '83/24']
tuneable ratios (vs. any ratio from original chord): ['5/2', '65/24']
frequencies (Hz): ['950.71429', '1100.0', '1191.66667', '1280.71429', '1372.38095', '1521.66667']
MIDI key numbers: ['82.3381', '84.86314', '86.24886', '87.49648', '88.69327', '90.48092']
Helmholtz-Ellis notations (text string, letter name): [('44>', 'A'), ('u', 'C'), ('0u', 'D'), ('undefined', 'undefined'), ('undefined', 'undefined'), ('undefined', 'undefined')]
12-ED2 pitch and cent deviations: ['A#/Bb5 +33.80998', 'C#/Db6 -13.68629', 'D6 +24.88637', 'D#/Eb6 +49.64788', 'F6 -30.67331', 'F#/Gb6 +48.09232']

"""
check("PC print_info('resultants')", capture(lambda: chord2.print_info("resultants")), expected_resultants)

# ── reference ─────────────────────────────────────────────────────────────────

expected_reference = """\

REFERENCE INFO
reference pitch (1/1): A4
reference key number: 69
reference frequency: 440.0 Hz

"""
check("PC print_info('reference')", capture(lambda: chord2.print_info("reference")), expected_reference)

# ── summary ───────────────────────────────────────────────────────────────────

print()
if failures:
    print(f"  {len(failures)} failure(s): {', '.join(failures)}")
else:
    print("  All checks passed.")
