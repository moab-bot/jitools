from __future__ import annotations
import csv
import fractions
import math
import os
from functools import reduce
from itertools import combinations, product
from . import pitch, utilities_general, utilities_music, constants


class PitchCollection():
    """A collection of just-intonation pitches with interval and harmonic analysis."""

    def __init__(
        self,
        pc: list[tuple[int, int] | fractions.Fraction] = [(1, 1), (2, 1)],
        rp: str = "A4",
        rf: float = 440.0,
        ti: list[tuple[int, int]] | None = None,
        precision: int = 5,
        _allow_single_pitch: bool = False) -> None:
        """
        Args:
            pc: List of pitches as (numerator, denominator) tuples or Fractions.
            rp: Letter-name of the reference pitch (1/1), e.g. "A4" or "C4". Defaults to "A4".
            rf: Frequency of the reference pitch in Hz. Defaults to 440.0.
            ti: Tuneable intervals as a list of (numerator, denominator) tuples.
                Defaults to the Sabat-Schweinitz tuneable interval list.
            precision: Decimal places used for floating-point display. Defaults to 5.
        """
        if not isinstance(pc, list):
            raise TypeError(f"pc must be a list of pitch tuples, got {type(pc).__name__!r}")
        if not _allow_single_pitch and len(pc) < 2:
            raise ValueError(f"pc must contain at least 2 pitches, got {len(pc)}")
        if ti is None:
            ti = constants.SABAT_SCHWEINITZ_TUNEABLE_INTERVALS
        self.pc_raw = []
        [self.pc_raw.append(x) for x in pc if x not in self.pc_raw]
        self.reference_pitch = rp
        self.reference_freq = rf
        self.precision = precision
        self.allowed_tuneable_intervals_as_tuples = ti
        self.allowed_tuneable_intervals = utilities_general.tuples_to_fractions(self.allowed_tuneable_intervals_as_tuples)
        self._tuneable_set = set(self.allowed_tuneable_intervals)
        self.info_by_pitch = self._info_by_pitch(self.pc_raw)
        if isinstance(self.info_by_pitch, list):
            self.sort_by(sort_by="ratios")
            intervals_and_resultant_tones = self._intervals_and_resultant_tones()
            self.intervals = intervals_and_resultant_tones[0]
            self.tuneable_intervals = intervals_and_resultant_tones[1][0]
            self.tuneable_pitch_pairs = intervals_and_resultant_tones[1][1]
            self.non_tuneable_intervals = intervals_and_resultant_tones[1][2]
            self.non_tuneable_pitch_pairs = intervals_and_resultant_tones[1][3]
            self.difference_tones = intervals_and_resultant_tones[2]
            self.tuneable_difference_tones = intervals_and_resultant_tones[3][0]
            self.tuneable_difference_tone_pitch_pairs = intervals_and_resultant_tones[3][1]
            self.non_tuneable_difference_tones = intervals_and_resultant_tones[3][2]
            self.non_tuneable_difference_tone_pitch_pairs = intervals_and_resultant_tones[3][3]
            self.summation_tones = intervals_and_resultant_tones[4]
            self.tuneable_summation_tones = intervals_and_resultant_tones[5][0]
            self.tuneable_summation_tone_pitch_pairs = intervals_and_resultant_tones[5][1]
            self.non_tuneable_summation_tones = intervals_and_resultant_tones[5][2]
            self.non_tuneable_summation_tone_pitch_pairs = intervals_and_resultant_tones[5][3]
            self.pc_plus_resultant_tones = self._pc_plus_resultant_tones()
            self.pc_plus_resultant_tones_as_harmonics = self._harmonics(self.pc_plus_resultant_tones)

            self.inversion = self._inversion()
            self.inversion_harmonics = self._harmonics(self.inversion)
            self.intervals_sequential = self._intervals_sequential()
                
            self.avg_ratio = sum(self.ratios) / len(self.ratios)
            self.avg_freq = sum(self.freqs) / len(self.freqs)
            self.avg_keynum = utilities_music.cpsmidi(self.avg_freq, self.reference_freq, self.reference_keynum)
            self.minimum_ratio = min(self.ratios)
            self.minimum_freq = min(self.freqs)
            self.minimum_keynum = min(self.keynums)
            self.maximum_ratio = max(self.ratios)
            self.maximum_freq = max(self.freqs)
            self.maximum_keynum = max(self.keynums)
            self.ratio_span = self.maximum_ratio / self.minimum_ratio
            self.freq_span = self.maximum_freq - self.minimum_freq
            self.keynum_span = self.maximum_keynum - self.minimum_keynum
            self.cents_span = self.keynum_span * 100
                
            self.harmonics = self._harmonics(self.ratios)
            self.periodicity_pitch = self._periodicity_pitch()
            self.least_common_partial = self._least_common_partial()[0]
            self.least_common_partial_freq = self._least_common_partial()[1]
            self.constituent_primes = sorted(list(dict.fromkeys([p for lop in self.constituent_primes_by_pitch for p in lop])))
            self.hd_sum = self._hd_sum()
            self.hd_avg = self.hd_sum / len(self.pc_raw)
            self.harmonic_intersection = self._harmonic_intersection()
            self.harmonic_disjunction = (
                None if self.harmonic_intersection is None
                else 1 - self.harmonic_intersection
            )

    def print_info(self, variety: str = "basic") -> None:
        """Print a formatted report of collection attributes.

        Args:
            variety: One of "basic", "quantitative", "analytic", "normalized",
                     "inversion", "resultants", "reference", or "all".
        """
        strings_to_print = self._create_strings_for_print_and_txt(variety = variety)
        for x in strings_to_print:
            print(x)

    def sort_by(self, sort_by: str = "ratios") -> None:
        """Re-sort pitches by a named parameter and update all derived attributes."""
        parameter_index_pairs = [
            ["ratios", 1], 
            ["keynum classes", 5], 
            ["normalized ratios", 10], 
            ["harmonic distances", 13], 
            ["normalized harmonic distances", 14]]
        sort_by_index = -1
        for pip in parameter_index_pairs:
            if pip[0] == sort_by:
                sort_by_index = pip[1]
        self.info_by_pitch.sort(key=lambda x: x[sort_by_index])
        self._info_by_parameter()
        self.inversion = self._inversion()
        self.intervals_sequential = self._intervals_sequential()
        if sort_by_index < 0:
            raise ValueError("cannot sort by this parameter")

    def transpose(self, interval: tuple[int, int] | fractions.Fraction) -> None:
        """Transpose all pitches by the given interval ratio."""
        transposition_ratio = pitch.Pitch(p = interval).ratio
        transposed_pitches = [x * transposition_ratio for x in self.ratios]
        self.update(pc = transposed_pitches)

    def update(
        self,
        pc: list | None = None,
        rp: str | None = None,
        rf: float | None = None,
        ti: list | None = None,
        precision: int | None = None) -> None:
        """Re-initialize with updated parameters, preserving any omitted values."""
        if rp is None:
            rp = self.reference_pitch
        if rf is None:
            rf = self.reference_freq
        if pc is None:
            pc = self.pc_raw
        if ti is None:
            ti = self.allowed_tuneable_intervals_as_tuples
        if precision is None:
            precision = self.precision
        self.__init__(
            pc = pc, 
            rp = rp,
            rf = rf, 
            ti = ti, 
            precision = precision)

    def write_info_to_csv(self, output_path: str = "pitch_collection_info.csv", verbose: bool = False) -> None:
        """Write pitch collection data to a CSV file.

        Args:
            output_path: Path to the output file (default "pitch_collection_info.csv",
                written to the current working directory). Supports ~ expansion.
            verbose: If True, print the path of the written file (default False).
        """
        final_info = []
        path_to_write_file = os.path.expanduser(output_path)
        data_types = [
            "", 
            "harm.", 
            "ratio", 
            "monzo", 
            "freq (Hz)", 
            "keynum", 
            "keynum cl.", 
            "primes", 
            "hd", 
            "HEJI", 
            "12-ED2"]
        count = 0
        processed_info = []
        for x in self.info_by_pitch:
            count += 1
            harm = x[0]
            ratio = x[1]
            monzo = x[2]
            freq = x[3]
            keynum = x[4]
            keynum_class = x[5]
            primes = x[7]
            harmonic_distance = x[13]
            notation = x[8]
            letter_name_and_octave_and_cents = x[9]
            stats_to_be_added = [
                count,
                str(harm),
                "'" + str(ratio) + "'",
                str(monzo),
                utilities_general.convert_data_to_readable_string(freq, precision = self.precision),
                utilities_general.convert_data_to_readable_string(keynum, precision = self.precision),
                utilities_general.convert_data_to_readable_string(keynum_class, precision = self.precision),
                str(primes),
                utilities_general.convert_data_to_readable_string(harmonic_distance, precision = self.precision),
                str(notation),
                "'" + str(letter_name_and_octave_and_cents) + "'"]
            processed_info.append(stats_to_be_added)
        final_info = [data_types] + processed_info
        with open(path_to_write_file, "w") as output:
            writer = csv.writer(output, lineterminator='\n')
            writer.writerows(final_info)
        if verbose:
            print("file written to " + path_to_write_file)

    def write_info_to_txt(self, variety: str = "all", output_path: str = "pitch_collection_info.txt", verbose: bool = False) -> None:
        """Write a formatted pitch collection report to a text file.

        Args:
            variety: One of "basic", "quantitative", "analytic", "normalized",
                     "inversion", "resultants", "reference", or "all" (default).
            output_path: Path to the output file (default "pitch_collection_info.txt",
                written to the current working directory). Supports ~ expansion.
            verbose: If True, print the path of the written file (default False).
        """
        strings_to_write = self._create_strings_for_print_and_txt(variety = variety)
        path_to_write_file = os.path.expanduser(output_path)
        with open(path_to_write_file, "w") as output:
            for x in strings_to_write:
                output.write(x + "\n")
        if verbose:
            print("file written to " + path_to_write_file)

    def _create_strings_for_print_and_txt(self, variety: str = "basic") -> list[str]:
        basic_info_strings = [
            "",
            "BASIC INFO",
            "ratios: " + str([utilities_general.convert_data_to_readable_string(x) for x in self.ratios]),
            "frequencies (Hz): " + str([utilities_general.convert_data_to_readable_string(x, precision = self.precision) for x in self.freqs]),
            "MIDI key numbers: " + str([utilities_general.convert_data_to_readable_string(x, precision = self.precision) for x in self.keynums]),
            "Helmholtz-Ellis notations (text string, letter name): " + str(self.notations),
            "12-ED2 pitch and cent deviations: " + str(self.letter_names_and_octave_and_cents),
            "harmonic constellation: " + self._harmonics_to_proportional_ratio_string(self.harmonics),
            "sequential intervals: " + str([utilities_general.convert_data_to_readable_string(x) for x in self.intervals_sequential]),
            "normalized ratios: " + str([utilities_general.convert_data_to_readable_string(x) for x in self.normalized_ratios]),
            "inversion: " + str([utilities_general.convert_data_to_readable_string(x) for x in self.inversion]),
            ""]
        
        quantitative_info_strings = [
            "",
            "QUANTITATIVE INFO",
            "average ratio: " + utilities_general.convert_data_to_readable_string(self.avg_ratio),
            "minimum ratio: " + utilities_general.convert_data_to_readable_string(self.minimum_ratio),
            "maximum ratio: " + utilities_general.convert_data_to_readable_string(self.maximum_ratio),
            "ratio span: " + utilities_general.convert_data_to_readable_string(self.ratio_span),
            "average frequency (Hz): " + utilities_general.convert_data_to_readable_string(self.avg_freq, precision = self.precision),
            "minimum frequency (Hz): " + utilities_general.convert_data_to_readable_string(self.minimum_freq, precision = self.precision),
            "maximum frequency (Hz): " + utilities_general.convert_data_to_readable_string(self.maximum_freq, precision = self.precision),
            "frequency span (Hz): " + utilities_general.convert_data_to_readable_string(self.freq_span, precision = self.precision),
            "average MIDI key number: " + utilities_general.convert_data_to_readable_string(self.avg_keynum, precision = self.precision),
            "minimum MIDI key number: " + utilities_general.convert_data_to_readable_string(self.minimum_keynum, precision = self.precision),
            "maximum MIDI key number: " + utilities_general.convert_data_to_readable_string(self.maximum_keynum, precision = self.precision),
            "MIDI key number span: " + utilities_general.convert_data_to_readable_string(self.keynum_span, precision = self.precision),
            "span in cents: " + utilities_general.convert_data_to_readable_string(self.cents_span, precision = self.precision),
            ""]
        
        analytic_info_strings = [
            "",
            "ANALYTIC INFO",
            "all intervals: " + str([utilities_general.convert_data_to_readable_string(x) for x in self.intervals]),
            "tuneable intervals: " + str([utilities_general.convert_data_to_readable_string(x) for x in self.tuneable_intervals]),
            "periodicity pitch (Hz): " + utilities_general.convert_data_to_readable_string(self.periodicity_pitch, precision = self.precision),
            "least common partial (of periodicity pitch): " + str(self.least_common_partial),
            "least common partial frequency (Hz): " + utilities_general.convert_data_to_readable_string(self.least_common_partial_freq, precision = self.precision),
            "constituent primes: " + str(self.constituent_primes),
            "harmonic distance sum: " + str(round(self.hd_sum, self.precision)),
            "average harmonic distance: " + str(round(self.hd_avg, self.precision)),
            "harmonic intersection: " + (
                "N/A (more than 24 independent harmonics)"
                if self.harmonic_intersection is None else
                utilities_general.convert_data_to_readable_string(self.harmonic_intersection)
                + " (" + str(round(float(self.harmonic_intersection), self.precision)) + ")"
            ),
            "harmonic disjunction: " + (
                "N/A (more than 24 independent harmonics)"
                if self.harmonic_disjunction is None else
                utilities_general.convert_data_to_readable_string(self.harmonic_disjunction)
                + " (" + str(round(float(self.harmonic_disjunction), self.precision)) + ")"
            ),
            ""]

        if variety == "normalized" or variety == "all":
            normalized_ci = PitchCollection(pc = self.normalized_ratios,
                rp = self.reference_pitch,
                rf = self.reference_freq,
                precision = self.precision,
                _allow_single_pitch = True)
            normalized_info_strings = normalized_ci._create_strings_for_print_and_txt(variety = "basic")
            del normalized_info_strings[-3]
            normalized_info_strings[1] = "NORMALIZED INFO"

        if variety == "inversion" or variety == "all":
            inversion_ci = PitchCollection(pc = self.inversion,
                rp = self.reference_pitch,
                rf = self.reference_freq,
                precision = self.precision,
                _allow_single_pitch = True)
            inversion_info_strings = inversion_ci._create_strings_for_print_and_txt(variety = "basic")
            del inversion_info_strings[-2]
            inversion_info_strings[1] = "INVERSION INFO"

        if variety == "resultants" or variety == "all":
            difference_tones_ci = PitchCollection(
                pc = self.difference_tones,
                rp = self.reference_pitch,
                rf = self.reference_freq,
                precision = self.precision,
                _allow_single_pitch = True)
            difference_tones_info_strings = difference_tones_ci._create_strings_for_print_and_txt(variety = "basic")
            difference_tones_info_strings[1] = "FIRST-ORDER DIFFERENCE TONES"
            tuneable_difference_tones_strings = "tuneable ratios (vs. any ratio from original chord): " + str([utilities_general.convert_data_to_readable_string(x) for x in self.tuneable_difference_tones])
            difference_tones_info_strings = difference_tones_info_strings[:3] + [tuneable_difference_tones_strings] + difference_tones_info_strings[3:][:-5] + [""]
            summation_tones_ci = PitchCollection(
                pc = self.summation_tones,
                rp = self.reference_pitch,
                rf = self.reference_freq,
                precision = self.precision,
                _allow_single_pitch = True)
            summation_tones_info_strings = summation_tones_ci._create_strings_for_print_and_txt(variety = "basic")
            summation_tones_info_strings[1] = "FIRST-ORDER SUMMATION TONES"
            tuneable_summation_tones_strings = "tuneable ratios (vs. any ratio from original chord): " + str([utilities_general.convert_data_to_readable_string(x) for x in self.tuneable_summation_tones])
            summation_tones_info_strings = summation_tones_info_strings[:3] + [tuneable_summation_tones_strings] + summation_tones_info_strings[3:][:-5] + [""]
            resultant_tones_info_strings = difference_tones_info_strings + summation_tones_info_strings[1:]
        
        reference_info_strings = pitch.Pitch(
            rp = self.reference_pitch,
            rf = self.reference_freq,
            precision = self.precision).create_strings_for_print_and_txt(variety = "reference")

        if variety == "basic":
            output = basic_info_strings
        elif variety == "quantitative":
            output = quantitative_info_strings
        elif variety == "analytic":
            output = analytic_info_strings
        elif variety == "normalized":
            output = normalized_info_strings
        elif variety == "inversion":
            output = inversion_info_strings
        elif variety == "resultants":
            output = resultant_tones_info_strings
        elif variety == "reference":
            output = reference_info_strings
        elif variety == "all":
            output = basic_info_strings + quantitative_info_strings[1:] + analytic_info_strings[1:] + normalized_info_strings[1:] + inversion_info_strings[1:] + resultant_tones_info_strings[1:] + reference_info_strings[1:]
        return(output)

    def _harmonic_intersection(self) -> fractions.Fraction | None:
        """Return the harmonic intersection via inclusion-exclusion over the harmonic series.

        Applies an antichain filter first: if harmonic h_j is a multiple of h_i,
        its contribution is subsumed by h_i and it can be removed without changing
        the result. Returns None if the effective harmonic count after filtering
        exceeds 24, since 2^n inclusion-exclusion would be impractical.
        """
        harmonics = list(set(self.harmonics))
        harmonics = [int(h / reduce(math.gcd, harmonics)) for h in harmonics]
        # Remove any h that is a strict multiple of another h in the list
        harmonics = [h for h in harmonics
                     if not any(h % other == 0 and h != other for other in harmonics)]
        if len(harmonics) > 24:
            return None
        num, den = 0, 1
        for i in range(1, len(harmonics) + 1):
            sign = 1 if i % 2 != 0 else -1
            for c in combinations(harmonics, i):
                l = math.lcm(*c)
                g = math.gcd(den, l)
                new_den = den // g * l
                num = num * (new_den // den) + sign * (new_den // l)
                den = new_den
                g2 = math.gcd(abs(num), den)
                if g2 > 1:
                    num //= g2
                    den //= g2
        return fractions.Fraction(num, den)

    def _harmonics(self, ratios: list[fractions.Fraction]) -> list[int]:
        """Return the integer harmonic series representation of the given ratios."""
        ratio_denominators = [x.denominator for x in ratios]
        ratio_multiplier = reduce(math.lcm, ratio_denominators)
        harmonics = [int(x * ratio_multiplier) for x in ratios]
        return(harmonics)

    def _harmonics_to_proportional_ratio_string(self, harmonics: list[int]) -> str:
        """Return harmonics formatted as 'a:b:c:...'."""
        output = ""
        for i, h in enumerate(harmonics):
            output = output + str(h)
            if i < (len(harmonics) - 1):
                output = output + ":"
        return(output)

    def _hd_sum(self) -> float:
        hd_sum = sum(self.harmonic_distances)
        return(hd_sum)

    def _info_by_parameter(self) -> list[list]:
        """Transpose self.info_by_pitch and populate all per-parameter attribute lists."""
        info_by_parameter = utilities_general.flop(self.info_by_pitch)
        self.ratios = info_by_parameter[1]
        self.monzos = info_by_parameter[2]
        self.freqs = info_by_parameter[3]
        self.keynums = info_by_parameter[4]
        self.keynum_classes = info_by_parameter[5]
        self.distances_from_reference = info_by_parameter[6]
        self.constituent_primes_by_pitch = info_by_parameter[7]
        self.notations = info_by_parameter[8]
        self.letter_names_and_octave_and_cents = info_by_parameter[9]
        self.normalized_ratios = list(dict.fromkeys(sorted(info_by_parameter[10])))
        self.normalized_monzos = info_by_parameter[11]
        self.nums_symbols = info_by_parameter[12]
        self.harmonic_distances = info_by_parameter[13]
        self.normalized_harmonic_distances = info_by_parameter[14]
        return(info_by_parameter)

    def _info_by_pitch(self, pc: list) -> list[list]:
        """Return a list of attribute vectors, one per pitch."""
        ratios = []
        pc_processed = []
        output = []
        for p in pc:
            pci = pitch.Pitch(p = p,
                rp = self.reference_pitch,
                rf = self.reference_freq,
                precision = self.precision)
            if isinstance(pci.rk_and_fo, list):
                ratios.append(pci.ratio)
                pc_processed.append([pci.ratio, 
                    pci.monzo, 
                    pci.freq, 
                    pci.keynum, 
                    pci.keynum_class, 
                    pci.distance_in_cents_from_reference,
                    pci.constituent_primes, 
                    pci.notation, 
                    pci.letter_name_and_octave_and_cents, 
                    pci.normalized_ratio, 
                    pci.normalized_monzo, 
                    pci.num_symbols, 
                    pci.harmonic_distance, 
                    pci.normalized_harmonic_distance])
                self.reference_keynum = pci.reference_keynum
            else:
                pc_processed = pci.rk_and_fo
        harmonics = self._harmonics(ratios)
        for h, p in zip(harmonics, pc_processed):
            output.append([h] + p)
        return(output)

    def _intervals_and_resultant_tones(self) -> list[list]:
        """Return intervals, tuneable/non-tuneable splits, difference tones, and summation tones."""
        pairs = sorted(dict.fromkeys(
            tuple(sorted(x, reverse=True)) for x in combinations(self.ratios[::-1], 2)
        ))

        # Build interval→pairs index in one O(n²) pass instead of nested O(n⁴) loops
        pairs_by_interval = {}
        for pp in pairs:
            r = pp[0] / pp[1]
            if r not in pairs_by_interval:
                pairs_by_interval[r] = []
            pairs_by_interval[r].append(pp)

        unique_intervals = sorted(pairs_by_interval)
        tuneable_intervals, tuneable_pitch_pairs = [], []
        non_tuneable_intervals, non_tuneable_pitch_pairs = [], []
        for interval in unique_intervals:
            if self._is_tuneable(interval):
                tuneable_intervals.append(interval)
                tuneable_pitch_pairs.append(pairs_by_interval[interval])
            else:
                non_tuneable_intervals.append(interval)
                non_tuneable_pitch_pairs.append(pairs_by_interval[interval])

        interval_splits = [tuneable_intervals, tuneable_pitch_pairs,
                           non_tuneable_intervals, non_tuneable_pitch_pairs]

        # Difference and summation tones — build tone→pairs index in one pass
        resultant_results = []
        for compute_tone in (lambda a, b: a - b, lambda a, b: a + b):
            unique_tones = sorted(dict.fromkeys(
                compute_tone(pp[0], pp[1]) for pp in pairs
            ))

            pairs_by_tone = {t: [] for t in unique_tones}
            tuneable_tone_set = set()
            for pitch_ratio in self.ratios:
                for tone in unique_tones:
                    pairs_by_tone[tone].append((pitch_ratio, tone))
                    if self._is_tuneable(pitch_ratio / tone):
                        tuneable_tone_set.add(tone)

            tuneable_tones = sorted(tuneable_tone_set)
            non_tuneable_tones = sorted(t for t in unique_tones if t not in tuneable_tone_set)

            tuneable_pp = [
                [pp for pp in pairs_by_tone[t] if self._is_tuneable(pp[0] / pp[1])]
                for t in tuneable_tones
            ]
            non_tuneable_pp = [
                [pp for pp in pairs_by_tone[t] if not self._is_tuneable(pp[0] / pp[1])]
                for t in non_tuneable_tones
            ]
            resultant_results.append((unique_tones, tuneable_tones, tuneable_pp,
                                      non_tuneable_tones, non_tuneable_pp))

        diffs,  t_diffs,  t_diff_pp,  nt_diffs,  nt_diff_pp  = resultant_results[0]
        sums,   t_sums,   t_sum_pp,   nt_sums,   nt_sum_pp   = resultant_results[1]

        return [
            unique_intervals,
            interval_splits,
            diffs,
            [t_diffs, t_diff_pp, nt_diffs, nt_diff_pp],
            sums,
            [t_sums, t_sum_pp, nt_sums, nt_sum_pp],
        ]

    def _intervals_sequential(self) -> list[fractions.Fraction]:
        """Return the ascending interval between each consecutive pair of sorted pitches."""
        intervals_sequential = [ self.ratios[n] / self.ratios[n - 1] for n in range(1,len(self.ratios)) ]
        return(intervals_sequential)

    def _inversion(self) -> list[fractions.Fraction]:
        """Return the melodic inversion, transposed to start on the lowest pitch."""
        ratios = self.ratios
        inverted_intervals = [ ratios[n - 1] / ratios[n] for n in range(1,len(ratios))]
        inversion = [ratios[-1]]
        for x in inverted_intervals:
            inversion.append(inversion[-1] * x)
        min_inversion = min(inversion)
        correction = fractions.Fraction(min(ratios), min(inversion))
        transposed_inversion = [x * correction for x in inversion]
        return(sorted(transposed_inversion))

    def _is_tuneable(self, ratio: fractions.Fraction) -> bool:
        return ratio in self._tuneable_set

    def _least_common_partial(self) -> list[int | float]:
        """Return [least_common_partial_integer, least_common_partial_freq_in_hz]."""
        least_common_partial = utilities_general.lcm(self.harmonics)
        least_common_partial_freq = least_common_partial * self.periodicity_pitch
        return([least_common_partial, least_common_partial_freq])

    def _pc_plus_resultant_tones(self) -> list[fractions.Fraction]:
        composite_pc = list(dict.fromkeys(sorted(self.ratios + self.difference_tones + self.summation_tones)))
        return(composite_pc)

    def _periodicity_pitch(self) -> float:
        """Return the fundamental frequency implied by the harmonic series of the collection."""
        lowest_harmonic = min(self.harmonics)
        lowest_freq = min(self.freqs)
        periodicity_pitch = lowest_freq / lowest_harmonic
        return(periodicity_pitch)