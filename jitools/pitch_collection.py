import csv
import fractions
import math
import os
from functools import reduce
from itertools import combinations, product
from . import pitch, utilities_general, utilities_music, constants


class PitchCollection():

    def __init__(
        self,
        pc = [(1, 1), (2, 1)],
        rp = "A4",
        rf = 440.0,
        tuneable_intervals = constants.SABAT_SCHWEINITZ_TUNEABLE_INTERVALS,
        precision = 5):
        self.pc_raw = list(dict.fromkeys(pc))
        self.reference_pitch = rp
        self.reference_freq = rf
        self.precision = precision
        self.tuneable_intervals = utilities_general.tuples_to_fractions(tuneable_intervals)
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
            self.harmonic_disjunction = 1 - self.harmonic_intersection

    def print_info(self, variety = "basic"):
        strings_to_print = self._create_strings_for_print_and_txt(variety = variety)
        for x in strings_to_print:
            print(x)

    def sort_by(self, sort_by = "ratios"):
        parameter_index_pairs = [
            ["ratios", 1], 
            ["keynum classes", 5], 
            ["normalized ratios", 10], 
            ["harmonic distances", 11], 
            ["normalized harmonic distances", 14]]
        if sort_by == "reset":
            self.info_by_pitch = self._info_by_pitch(self.pc_raw)
        else:
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

    def transpose(self, interval):
        transposition_ratio = pitch.Pitch(p = interval).ratio
        transposed_pitches = [x * transposition_ratio for x in self.ratios]
        self.update(pc = transposed_pitches)

    def update(
        self, 
        pc = False, 
        rp = False, 
        rf = False, 
        tuneable_intervals = False, 
        precision = False):
        if not rp:
            rp = self.reference_pitch
        if not rf:
            rf = self.reference_freq
        if not pc:
            pc = self.pc_raw
        if not tuneable_intervals:
            tuneable_intervals = self.tuneable_intervals
        if not precision:
            precision = self.precision
        self.__init__(
            pc = pc, 
            rp = rp, 
            rf = rf, 
            tuneable_intervals = tuneable_intervals, 
            precision = precision)    

    def write_info_to_csv(self, output_directory = False, filename = "pitch_collection_info.csv"):
        final_info = []
        if output_directory == False:
            output_directory = os.getcwd()
        path_to_write_file = output_directory + "/" + filename
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
        print("file written to " + path_to_write_file)

    def write_info_to_txt(self, variety = "all", output_directory = False, filename = "pitch_collection_info.txt"):
        strings_to_write = self._create_strings_for_print_and_txt(variety = variety)
        if output_directory == False:
            output_directory = os.getcwd()
        path_to_write_file = output_directory + "/" + filename
        with open(path_to_write_file, "w") as output:
            for x in strings_to_write:
                output.write(x + "\n")
        print("file written to " + path_to_write_file)

    def _create_strings_for_print_and_txt(self, variety = "basic"):
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
            "average ratio: " + str(self.avg_ratio),
            "minimum ratio: " + str(self.minimum_ratio),
            "maximum ratio: " + str(self.maximum_ratio),
            "ratio span: " + str(self.ratio_span),
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
            "harmonic intersection: " + str(self.harmonic_intersection) + " (" + str(round(float(self.harmonic_intersection), self.precision)) + ")",
            "harmonic disjunction: " + str(self.harmonic_disjunction) + " (" + str(round(float(self.harmonic_disjunction), self.precision)) + ")",
            ""]

        if variety == "normalized" or variety == "all":
            normalized_ci = PitchCollection(pc = self.normalized_ratios, 
                rp = self.reference_pitch, 
                rf = self.reference_freq,
                precision = self.precision)
            normalized_info_strings = normalized_ci._create_strings_for_print_and_txt(variety = "basic")
            del normalized_info_strings[-3]
            normalized_info_strings[1] = "NORMALIZED INFO"

        if variety == "inversion" or variety == "all":
            inversion_ci = PitchCollection(pc = self.inversion, 
                rp = self.reference_pitch, 
                rf = self.reference_freq,
                precision = self.precision)
            inversion_info_strings = inversion_ci._create_strings_for_print_and_txt(variety = "basic")
            del inversion_info_strings[-2]
            inversion_info_strings[1] = "INVERSION INFO"

        if variety == "resultants" or variety == "all":
            difference_tones_ci = PitchCollection(
                pc = self.difference_tones, 
                rp = self.reference_pitch, 
                rf = self.reference_freq,
                precision = self.precision)
            difference_tones_info_strings = difference_tones_ci._create_strings_for_print_and_txt(variety = "basic")
            difference_tones_info_strings[1] = "FIRST-ORDER DIFFERENCE TONES"
            tuneable_difference_tones_strings = "tuneable ratios: " + str([utilities_general.convert_data_to_readable_string(x) for x in self.tuneable_difference_tones])
            difference_tones_info_strings = difference_tones_info_strings[:3] + [tuneable_difference_tones_strings] + difference_tones_info_strings[3:][:-5] + [""]
            summation_tones_ci = PitchCollection(
                pc = self.summation_tones, 
                rp = self.reference_pitch, 
                rf = self.reference_freq,
                precision = self.precision)
            summation_tones_info_strings = summation_tones_ci._create_strings_for_print_and_txt(variety = "basic")
            summation_tones_info_strings[1] = "FIRST-ORDER SUMMATION TONES"
            tuneable_summation_tones_strings = "tuneable ratios: " + str([utilities_general.convert_data_to_readable_string(x) for x in self.tuneable_summation_tones])
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

    def _harmonic_intersection(self):
        harmonics = list(set(self.harmonics))
        harmonics_length = len(harmonics)
        harmonics = [ int(h / reduce(math.gcd, harmonics)) for h in harmonics ]
        output = fractions.Fraction(0, 1)
        for i in range(1, harmonics_length + 1):
            combos = combinations(harmonics, i)
            if i % 2 == 0:
                new_values = [ [-1, utilities_general.lcm(c)] for c in combos ]
            else:
                new_values = [ [1, utilities_general.lcm(c)] for c in combos ]
            for nv in new_values:
                output = output + fractions.Fraction(nv[0], nv[1])
        return(output)

    def _harmonics(self, ratios):
        ratio_multiplier = reduce(fractions.gcd,(ratios)).denominator
        harmonics = [int(x * ratio_multiplier) for x in ratios]
        return(harmonics)

    def _harmonics_to_proportional_ratio_string(self, harmonics):
        output = ""
        for i, h in enumerate(harmonics):
            output = output + str(h)
            if i < (len(harmonics) - 1):
                output = output + ":"
        return(output)

    def _hd_sum(self):
        hd_sum = sum(self.harmonic_distances)
        return(hd_sum)

    def _info_by_parameter(self):
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

    def _info_by_pitch(self, pc):
        ratios = []
        pc_processed = []
        output = []
        for p in pc:
            pci = pitch.Pitch(p = p,
                rp = self.reference_pitch, 
                rf = self.reference_freq)
            if isinstance(pci.rk_and_fo, str) == False:
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

    def _intervals_and_resultant_tones(self):
        data = []
        for i, y in enumerate([lambda x: tuple(x), lambda x: x[0] / x[1], lambda x: x[0] - x[1], lambda x: x[0] + x[1]]):
            raw_pitch_info = [ y(sorted(x, reverse=True)) for x in list(combinations(self.ratios[::-1], 2)) ]
            data.append(sorted(list(dict.fromkeys(raw_pitch_info))))
            intervals = []
            if i == 1:
                pitch_pairs = data[0]
                intervals = data[1]
            elif i > 1:
                pitch_pairs = list(product(self.ratios, list(dict.fromkeys(raw_pitch_info))))
                intervals = [x[0] / x[1] for x in pitch_pairs]
            tuneable_intervals = []
            tuneable_resultant_tones = []
            tuneable_pitch_pairs = []
            non_tuneable_intervals = []
            non_tuneable_resultant_tones = []
            non_tuneable_pitch_pairs = []
            for y in intervals:
                if self._is_tuneable(y):
                    tuneable_intervals.append(y)
                    tpp = []
                    for pp in pitch_pairs:
                        if pp[0] / pp[1] == y:
                            if i == 1:
                                tpp.append(pp)
                            else:
                                tuneable_resultant_tones.append(pp[1])
                                tuneable_resultant_tones = sorted(list(dict.fromkeys(tuneable_resultant_tones)))
                            if i == 1:
                                tuneable_pitch_pairs.append(tpp)
                else:
                    non_tuneable_intervals.append(y)
                    ntpp = []
                    for pp in pitch_pairs:
                        if pp[0] / pp[1] == y:
                            if i == 1:
                                ntpp.append(pp)
                                non_tuneable_resultant_tones.append(pp[1])
                            else:
                                non_tuneable_resultant_tones.append(pp[1])
                                non_tuneable_resultant_tones = sorted(list(dict.fromkeys(non_tuneable_resultant_tones)))
                            if i == 1:
                                non_tuneable_pitch_pairs.append(ntpp)
            if i == 1:
                data.append([tuneable_intervals, tuneable_pitch_pairs, non_tuneable_intervals, non_tuneable_pitch_pairs])
            elif i > 1:
                for x in non_tuneable_resultant_tones:
                    if x in tuneable_resultant_tones:
                        non_tuneable_resultant_tones.remove(x)
                for tct in tuneable_resultant_tones:
                    tpp = []
                    for pp in pitch_pairs:
                        if tct == pp[1] and self._is_tuneable(pp[0] / pp[1]):
                            tpp.append(pp)
                    tuneable_pitch_pairs.append(tpp)
                for ntct in non_tuneable_resultant_tones:
                    ntpp = []
                    for pp in pitch_pairs:
                        if ntct == pp [1] and self._is_tuneable(pp[0] / pp[1]) == False:
                            ntpp.append(pp)
                    non_tuneable_pitch_pairs.append(ntpp)
                data.append([tuneable_resultant_tones, tuneable_pitch_pairs, non_tuneable_resultant_tones, non_tuneable_pitch_pairs])
        return(data[1:])

    def _intervals_sequential(self):
        intervals_sequential = [ self.ratios[n] / self.ratios[n - 1] for n in range(1,len(self.ratios)) ]
        return(intervals_sequential)

    def _inversion(self):
        ratios = self.ratios
        inverted_intervals = [ ratios[n - 1] / ratios[n] for n in range(1,len(ratios))]
        inversion = [ratios[-1]]
        for x in inverted_intervals:
            inversion.append(inversion[-1] * x)
        min_inversion = min(inversion)
        correction = fractions.Fraction(min(ratios), min(inversion))
        transposed_inversion = [x * correction for x in inversion]
        return(sorted(transposed_inversion))

    def _is_tuneable(self, ratio):
        is_tuneable = False
        if ratio in self.tuneable_intervals:
            is_tuneable = True
        return(is_tuneable) 

    def _least_common_partial(self):
        least_common_partial = utilities_general.lcm(self.harmonics)
        least_common_partial_freq = least_common_partial * self.periodicity_pitch
        return([least_common_partial, least_common_partial_freq])

    def _pc_plus_resultant_tones(self):
        composite_pc = list(dict.fromkeys(sorted(self.ratios + self.difference_tones + self.summation_tones)))
        return(composite_pc)

    def _periodicity_pitch(self):
        lowest_harmonic = min(self.harmonics)
        lowest_freq = min(self.freqs)
        periodicity_pitch = lowest_freq / lowest_harmonic
        return(periodicity_pitch)