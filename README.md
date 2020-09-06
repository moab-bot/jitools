## jitools - Python Utilities for JI

### Introduction

**jitools** is a Python-based set of utilities for **just intonation (JI)** pitch and pitch collection research and analysis. For the ambitious, it may also be incorporated into workflows for computer-assisted algorithmic composition.

**jitools** shares some functionalities with Thomas Nicholson's JavaScript-based online resource, the **[Plainsound Harmonic Space Calculator](https://www.plainsound.org/HEJI/)**.

**jitools** requires Python 3.8.5 or above.

### Just Intonation

JI is a musical model wherein the intervals between pitches are, as best as possible, tuned as small natural number frequency ratios. Aside from this basic tenet, there are no restrictions on the aesthetic or style of JI music. That said, music in JI often has certain tendencies that highlight or enable its very precise tuning.

JI has its own particular set of analytical concerns for composers, music theorists, and musicians. Many of these issues are well-described in the 2018 paper **"Fundamental Principles of Just Intonation and Microtonal Composition"** by Thomas Nicholson and Marc Sabat, which is available **[here](https://marsbat.space/pdfs/JI.pdf)**. This paper is essential reading for anyone interested in JI, and for anyone who wants to use or understand **jitools**.

### jitools - Installation

~$ sudo pip install jitools

### jitools.Pitch()

In JI, pitches are conceptualized as frequency ratios, which are often expressed as fractions, with respect to some known reference pitch. The known reference pitch is, by convention, known as **1/1**. Any frequency can serve as 1/1, its frequency just needs to be known. For example, if 1/1 is A4 = 440Hz, then the frequency of 3/2 would be 440 * 3/2, or 660Hz. But, if 1/1 is G4 = 392Hz, then the frequency of 3/2 would be 392 * 3/2, or 588Hz.

The most essential class in jitools is **jitools.Pitch()**. The principal argument of the class is ```p```, a tuple consisting of two positive integers that represent the proportions of a pitch's ratio. Since a ratio only has meaning with respect to a known reference pitch, when defining an instance of  **jitools.Pitch()**, the user may optionally define the letter-name pitch ```rp``` and frequency ```rf``` of 1/1. Otherwise, 1/1 is assumed to be A4 = 440Hz.

After defining an instance of **jitools.Pitch()** in terms of its ratio, the class automatically calculates many attributes relevant for JI analysis. These attributes are stored internally and can later be referred to by the user. Here are a few examples of such attributes:

```
>>> import jitools
>>> test_pitch = jitools.Pitch(p=(3, 2))
>>> test_pitch.freq
660.0
>>> test_pitch.keynum
76.01955000865388
>>> test_pitch.distance_in_cents_from_reference
701.955000865388
```
Here is the same information about 3/2, but with 1/1 defined as G4 = 392Hz:

```
>>> import jitools
>>> test_pitch = jitools.Pitch(p=(3, 2), rp="G4", rf=392)
>>> test_pitch.freq
588.0
>>> test_pitch.keynum
74.01955000865388
>>> test_pitch.distance_in_cents_from_reference
701.955000865388
```
JI pitches usually deviate from their nearest 12-TET counterparts by some number of **cents** (1 cent = 1/100 of a 12-TET semitone or 1/1200 of an octave), and knowing this information is useful for comparing JI pitches to their 12-TET counterparts:

```
>>> import jitools
>>> test_pitch = jitools.Pitch(p=(4, 7))
>>> test_pitch.letter_name_and_octave_and_cents
'B3 +31.17409'
```
### jitools.Pitch() - Notation
There are various methods for JI pitch notation, including **[Ben Johnston's well-known system](https://www.kylegann.com/BJNotation.html)** and **[Sagittal](http://sagittal.org/)** notation, among others. Perhaps the foremost JI pitch notation system in wide use today is the **[Extended Helmholtz-Ellis JI Pitch Notation (HEJI)](https://marsbat.space/pdfs/HEJI2legend+seriespdf)**, jointly developed by Marc Sabat and Wolfgang von Schweinitz in the early 2000s. 

In HEJI, each prime factor of a frequency ratio is denoted with a distinctive accidental glyph. These accidentals appear, alone or in various combinations, in front of letter-name notes on a conventional 5-line musical staff.

The HEJI font is available as a cross-platform free download **[here](https://marsbat.space/HEJI2_web_release.zip)**, and once installed the HEJI glyphs may be used with any modern music notation program. The download includes a font map that links each glyph to a different keyboard character, allowing the HEJI symbols (and combinations thereof) to be typed as text strings.

**jitools.Pitch()** handles the creation of these HEJI text strings, along with assigning the correct letter-name pitch, hastening the translation from ratio-based thinking to HEJI notation.

```
>>> import jitools
>>> test_pitch = jitools.Pitch(p=(25, 13))
>>> test_pitch.notation
('9t', 'G')
```
### jitools.Pitch() - Print and Write to File
Since attributes of **jitools.Pitch()** can be opaque and difficult to get at, detailed reports about a pitch's attributes can be printed to the console in an easy-to-read format, with a simple method:

```
>>> import jitools
>>> test_pitch = jitools.Pitch(p=(17, 11))
>>> test_pitch.print_info()

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

```
Such reports can also be written to txt files. By default files are written to the user's current working directory, although the ```output_directory``` and ```filename``` can also be customized by the user:

```
>>> import jitools
>>> test_pitch = jitools.Pitch(p=(17, 11))
>>> test_pitch.write_info_to_txt()
file written to /current/working/directory/pitch_info.txt
>>> test_pitch.write_info_to_txt(output_directory="/path/to/file", filename="myfile.txt")
file written to /path/to/file/myfile.txt
```
### jitools.Pitch() - Enharmonic Search
Another important functionality of **jitools.Pitch()** is **enharmonic search**. Enharmonics in JI are two rational pitches that are extremely close to each other in terms of pitch height -- generally within about 4 cents or less -- so close that the difference between their pitch heights cannot be perceived by ear, or at worst can barely be perceived in a harmonic context (see **[Nicholson/Sabat](https://marsbat.space/pdfs/JI.pdf)**, p. 16-19). 

Enharmonic assessment can be useful for a variety of purposes, particularly when dealing with more complex ratios that are unfamiliar, or cumbersome to notate and/or interpret.

In **jitools.Pitch()** enharmonic information may be generated and stored internally as a list:

```
>>> import jitools
>>> test_pitch = jitools.Pitch((711, 184))
>>> test_pitch.get_enharmonics()
[[Fraction(800, 207), 0.27053, 17.337343147274048, Fraction(6399, 6400)], [Fraction(2816, 729), -0.58462, 20.969206622964233, Fraction(518319, 518144)], [Fraction(11875, 3072), 0.64032, 25.12060239371419, Fraction(273024, 273125)], [Fraction(495, 128), 1.36911, 15.95128471496697, Fraction(1264, 1265)]]
```

As a list this information is a little opaque, so enharmonics information may also be printed to the console in a easy-to-read format, or written to txt or csv files:

```
>>> import jitools
>>> test_pitch = jitools.Pitch((711, 184))
>>> test_pitch.print_enharmonics_info()

ORIGINAL PITCH INFO
ratio: 711/184
monzo: [-3, 2, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
constituent primes: [2, 3, 23, 79]
frequency (Hz): 1700.21739
MIDI key number: 92.40173
distance from 1/1 (cents): 2340.17255
harmonic distance: 16.99727
Helmholtz-Ellis notation (text string, letter name): ('undefined', 'undefined')
12-ED2 pitch and cent deviation: G#/Ab6 +40.17255

ENHARMONIC SELECTION CRITERIA
tolerance (cents): 1.95
prime limit: 23
maximum number of HEJI symbols: 2
maximum mumber of candidates: 10
sorted by: tolerance
total number of qualifying candidates: 4

ENHARMONIC NO. 1
ratio: 800/207
monzo: [5, -2, 2, 0, 0, 0, 0, 0, -1]
constituent primes: [2, 3, 5, 23]
frequency (Hz): 1700.48309
MIDI key number: 92.40443
distance from 1/1 (cents): 2340.44308
harmonic distance: 17.33734
Helmholtz-Ellis notation (text string, letter name): ('6l', 'A')
12-ED2 pitch and cent deviation: G#/Ab6 +40.44308
melodic interval from 711/184: 6399:6400
enharmonic interval size (cents): +0.27053

ENHARMONIC NO. 2
ratio: 2816/729
monzo: [8, -6, 0, 0, 1]
constituent primes: [2, 3, 11]
frequency (Hz): 1699.64335
MIDI key number: 92.39588
distance from 1/1 (cents): 2339.58794
harmonic distance: 20.96921
Helmholtz-Ellis notation (text string, letter name): ('4e', 'A')
12-ED2 pitch and cent deviation: G#/Ab6 +39.58794
melodic interval from 711/184: 518319:518144
enharmonic interval size (cents): -0.58462

ENHARMONIC NO. 3
ratio: 11875/3072
monzo: [-10, -1, 4, 0, 0, 0, 0, 1]
constituent primes: [2, 3, 5, 19]
frequency (Hz): 1700.84635
MIDI key number: 92.40813
distance from 1/1 (cents): 2340.81287
harmonic distance: 25.1206
Helmholtz-Ellis notation (text string, letter name): ('/R', 'G')
12-ED2 pitch and cent deviation: G#/Ab6 +40.81287
melodic interval from 711/184: 273024:273125
enharmonic interval size (cents): +0.64032

ENHARMONIC NO. 4
ratio: 495/128
monzo: [-7, 2, 1, 0, 1]
constituent primes: [2, 3, 5, 11]
frequency (Hz): 1701.5625
MIDI key number: 92.41542
distance from 1/1 (cents): 2341.54166
harmonic distance: 15.95128
Helmholtz-Ellis notation (text string, letter name): ('4u', 'G')
12-ED2 pitch and cent deviation: G#/Ab6 +41.54166
melodic interval from 711/184: 1264:1265
enharmonic interval size (cents): +1.36911

>>> test_pitch.write_enharmonics_info_to_txt()
file written to /current/working/directory/enharmonic_candidates.txt
>>> test_pitch.write_enharmonics_info_to_csv()
file written to /current/working/directory/enharmonic_candidates.csv
```
Various constraints on an enharmonic search may be customized by the user, including:

*  ```tolerance```: how close the enharmonic must be to the original pitch, in cents (default = 1.95)
*  ```limit```: maximum prime factor allowed (default = 23)  
*  ```exclude_primes```: prime factors to be excluded, as a list (default = [])
*  ```max_symbols```: maximum number of HEJI symbols (default = 2)

The ```sort_by``` method of an enharmonic search can also be changed. The default is to sort by ```"tolerance"```, which orders the enharmonics by how closely they match the pitch height of the original pitch (enharmonic interval size). But, the results may also be sorted by ```"harmonic distance"```, a measure developed by James Tenney which generally correlates to interval/ratio simplicity. (See **[Nicholson/Sabat](https://marsbat.space/pdfs/JI.pdf)**, p. 26-28, for more information about harmonic distance and other metrics invented by Tenney.)

In the example below, the same original pitch, 711/184, is used as in the example above, but the tolerance and allowed prime factors are more restricted. This disqualifies all of the enharmonics returned in the previous example. Even so, increasing the maximum allowed number of HEJI symbols yields two new 3-symbol enharmonics. The enharmonics are sorted by harmonic distance, which in this case does not correlate to tolerance:

```
>>> import jitools
>>> test_pitch = jitools.Pitch((711, 184))
>>> test_pitch.print_enharmonics_info(tolerance=0.5, limit=17, exclude_primes=[7, 23], max_symbols=3, sort_by="harmonic distance")

ORIGINAL PITCH INFO
ratio: 711/184
monzo: [-3, 2, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
constituent primes: [2, 3, 23, 79]
frequency (Hz): 1700.21739
MIDI key number: 92.40173
distance from 1/1 (cents): 2340.17255
harmonic distance: 16.99727
Helmholtz-Ellis notation (text string, letter name): ('undefined', 'undefined')
12-ED2 pitch and cent deviation: G#/Ab6 +40.17255

ENHARMONIC SELECTION CRITERIA
tolerance (cents): 0.5
prime limit: 17
excluded primes: [7, 23]
maximum number of HEJI symbols: 3
maximum mumber of candidates: 10
sorted by: harmonic distance
total number of qualifying candidates: 2

ENHARMONIC NO. 1
ratio: 85/22
monzo: [-1, 0, 1, 0, -1, 0, 1]
constituent primes: [2, 5, 11, 17]
frequency (Hz): 1700.0
MIDI key number: 92.39951
distance from 1/1 (cents): 2339.95118
harmonic distance: 10.86882
Helmholtz-Ellis notation (text string, letter name): (':5U', 'G')
12-ED2 pitch and cent deviation: G#/Ab6 +39.95118
melodic interval from 711/184: 7821:7820
enharmonic interval size (cents): -0.22137

ENHARMONIC NO. 2
ratio: 8450/2187
monzo: [1, -7, 2, 0, 0, 2]
constituent primes: [2, 3, 5, 13]
frequency (Hz): 1700.04572
MIDI key number: 92.39998
distance from 1/1 (cents): 2339.99775
harmonic distance: 24.13947
Helmholtz-Ellis notation (text string, letter name): ('00t', 'A')
12-ED2 pitch and cent deviation: G#/Ab6 +39.99775
melodic interval from 711/184: 1554957:1554800
enharmonic interval size (cents): -0.17481
 
```
### jitools.PitchCollection()
The second essential class in jitools is **jitools.PitchCollection()**. In a nutshell, this class allows collections of **jitools.Pitch()** instances -- which can be regarded as chords, scales, or pitch aggregates -- to be collectively analyzed as a group.

Instead of a duple, **jitools.PitchCollection()** takes ```pc``` as its principal argument, which is a list of two-element duples, each of which represents a pitch ratio. As with **jitools.Pitch()**, a letter-name reference pitch ```rp``` and reference frequency ```rf``` may be optionally defined, or else A4 = 440Hz is assumed.

As with **jitools.Pitch()**, a **jitools.PitchCollection()** instance stores several important attributes about the pitch collection that may be directly referred to by the user:

```
>>> import jitools
>>> test_chord = jitools.PitchCollection([(1, 1), (5, 4), (3, 2)])
>>> test_chord.ratios
[Fraction(1, 1), Fraction(5, 4), Fraction(3, 2)]
>>> test_chord.freqs
[440.0, 550.0, 660.0]
>>> test_chord.keynums
[69.0, 72.86313713864834, 76.01955000865388]
>>> test_chord.intervals
[Fraction(6, 5), Fraction(5, 4), Fraction(3, 2)]
```
One may also print information about a pitch collection to the console in an easy-to-read format:

```
>>> import jitools
>>> test_chord = jitools.PitchCollection([(7, 8), (9, 7), (13, 8), (11, 6)])
>>> test_chord.print_info()

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

```
The above is the ```"basic"``` information about a pitch collection, which is the default information type returned when printing (or writing to txt, see below). Various other kinds of information can also be printed or written to txt:

```
>>> import jitools
>>> test_chord = jitools.PitchCollection([(7, 8), (9, 7), (13, 8), (11, 6)])
>>> test_chord.print_info("quantitative")

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

>>> test_chord.print_info("analytic")

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

>>> test_chord.print_info("normalized")

NORMALIZED INFO
ratios: ['9/7', '13/8', '7/4', '11/6']
frequencies (Hz): ['565.71429', '715.0', '770.0', '806.66667']
MIDI key numbers: ['73.35084', '77.40528', '78.68826', '79.49363']
Helmholtz-Ellis notations (text string, letter name): [('>v', 'C'), ('0v', 'F'), ('<', 'G'), ('4', 'G')]
12-ED2 pitch and cent deviations: ['C#/Db5 +35.0841', 'F5 +40.52766', 'G5 -31.17409', 'G5 +49.36294']
harmonic constellation: 216:273:294:308
sequential intervals: ['91/72', '14/13', '22/21']
inversion: ['9/7', '66/49', '132/91', '11/6']

>>> test_chord.print_info("inversion")

INVERSION INFO
ratios: ['7/8', '77/78', '539/432', '11/6']
frequencies (Hz): ['385.0', '434.35897', '548.98148', '806.66667']
MIDI key numbers: ['66.68826', '68.77661', '72.83105', '79.49363']
Helmholtz-Ellis notations (text string, letter name): [('<', 'G'), ('94<e', 'A'), ('4,e', 'D'), ('4', 'G')]
12-ED2 pitch and cent deviations: ['G4 -31.17409', 'A4 -22.33881', 'C#/Db5 -16.89525', 'G5 +49.36294']
harmonic constellation: 4914:5544:7007:10296
sequential intervals: ['44/39', '91/72', '72/49']
normalized ratios: ['539/432', '7/4', '11/6', '77/39']

>>> test_chord.print_info("resultants")

FIRST-ORDER DIFFERENCE TONES
ratios: ['5/24', '19/56', '23/56', '23/42', '3/4', '23/24']
tuneable ratios: ['5/24', '3/4']
frequencies (Hz): ['91.66667', '149.28571', '180.71429', '240.95238', '330.0', '421.66667']
MIDI key numbers: ['41.84359', '50.28687', '53.59448', '58.57493', '64.01955', '68.26319']
Helmholtz-Ellis notations (text string, letter name): [('u', 'F'), ('/>', 'D'), ('3>v', 'E'), ('3>v', 'A'), ('n', 'E'), ('3v', 'G')]
12-ED2 pitch and cent deviations: ['F#/Gb2 -15.64129', 'D3 +28.68711', 'F#/Gb3 -40.55156', 'B3 -42.50656', 'E4 +1.955', 'G#/Ab4 +26.31935']

FIRST-ORDER SUMMATION TONES
ratios: ['121/56', '5/2', '65/24', '163/56', '131/42', '83/24']
tuneable ratios: ['5/2', '65/24']
frequencies (Hz): ['950.71429', '1100.0', '1191.66667', '1280.71429', '1372.38095', '1521.66667']
MIDI key numbers: ['82.3381', '84.86314', '86.24886', '87.49648', '88.69327', '90.48092']
Helmholtz-Ellis notations (text string, letter name): [('44>', 'A'), ('u', 'C'), ('0u', 'D'), ('undefined', 'undefined'), ('undefined', 'undefined'), ('undefined', 'undefined')]
12-ED2 pitch and cent deviations: ['A#/Bb5 +33.80998', 'C#/Db6 -13.68629', 'D6 +24.88637', 'D#/Eb6 +49.64788', 'F6 -30.67331', 'F#/Gb6 +48.09232']

>>> test_chord.print_info("reference")

REFERENCE INFO
reference pitch (1/1): A4
reference key number: 69
reference frequency: 440.0 Hz

```

**jitools.PitchCollection()** information, as with **jitools.Pitch()** information, may be written to file, in this case as txt or csv:

```
>>> import jitools
>>> test_chord = jitools.PitchCollection([(9, 4), (15, 48), (21, 17)])
>>> test_chord.write_info_to_txt()
file written to /current/working/directory/pitch_collection_info.txt
>>> test_chord.write_info_to_csv()
file written to /current/working/directory/pitch_collection_info.csv
```

### State of the Project
I view this project as being in its infancy, and I intend continually refine the code and add more features/tools as time allows. Short-term, I am aware of the need for:

*  comprehensive documentation
*  tutorials and additional examples 
*  better explanation of the JI theory jargon