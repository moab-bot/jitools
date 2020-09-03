import ast
import csv
import fractions
import math
import os
from . import utilities_general, utilities_music, prime_list, constants

LONG_LIST_OF_PRIMES = prime_list.PrimeList(2**24) #if this value is too low there will be errors when trying to factor very large numbers
DEFAULT_MONZO_PRIMES = prime_list.PrimeList(48).primes #all primes up to 47 by default

class Pitch():

    def __init__(
        self,
        p = (1, 1),
        rp = "A4",
        rf = 440.0,
        precision = 5):
        self.reference_pitch = rp
        self.reference_freq = rf
        self.precision = precision
        self._vector_primes = DEFAULT_MONZO_PRIMES
        self.rk_and_fo = self._reference_keynum_and_fund_offset_from_pitch_letter_name_and_octave()
        self.reference_keynum = self.rk_and_fo[0]
        self._fund_offset = self.rk_and_fo[1]
        if isinstance(p, fractions.Fraction):
            self.ratio = p
            self.monzo = self._monzo_from_ratio()
        elif isinstance(p, list):
            self.monzo = self._trim_monzo(p)
            self.ratio = self._ratio_from_monzo()
        elif isinstance(p, tuple):
            self.ratio = utilities_general.tuple_to_fraction(p)
            self.monzo = self._monzo_from_ratio()
        self.constituent_primes = self._constituent_primes()
        self.freq = self._freq()
        self.keynum = self._keynum()
        self.keynum_class = self.keynum % 12
        self.distance_in_cents_from_reference = self._distance_in_cents_from_reference()
        self.notation = self._notation()
        self.accidental_string = self.notation[0]
        self.letter_name = self.notation[1]
        self.letter_name_and_octave_and_cents = self._letter_name_and_octave_and_cents()
        self.complement = self._complement()
        self.normalized_ratio = self._normalized_ratio(self.ratio)
        self.normalized_monzo = self._normalized_monzo(self.monzo)
        self.normalized_complement = self._normalized_ratio(self.complement)
        if self.accidental_string != "undefined":
            self.num_symbols = len(self.accidental_string)
        else:
            self.num_symbols = "undefined"
        self.harmonic_distance = self._harmonic_distance(self.monzo)
        self.normalized_harmonic_distance = self._harmonic_distance(self.normalized_monzo)
        self.pitch_info = self._pitch_info()

    def create_strings_for_print_and_txt(self, variety = "basic"):
        basic_info_strings = [
            "",
            "BASIC INFO",
            "ratio: " + str(self.ratio),
            "monzo: " + str(self.monzo),
            "constituent primes: " + str(self.constituent_primes),
            "frequency (Hz): " + utilities_general.convert_data_to_readable_string(self.freq, precision = self.precision),
            "MIDI key number: " + utilities_general.convert_data_to_readable_string(self.keynum, precision = self.precision),
            "distance from 1/1 (cents): " + utilities_general.convert_data_to_readable_string(self.distance_in_cents_from_reference, precision = self.precision),
            "harmonic distance: " + utilities_general.convert_data_to_readable_string(self.harmonic_distance, precision = self.precision),
            "Helmholtz-Ellis notation (text string, letter name): " + str((self.accidental_string, self.letter_name)),
            "12-ED2 pitch and cent deviation: " + str(self.letter_name_and_octave_and_cents),
            ""]
        normalized_info_strings = [
            "",
            "NORMALIZED INFO",
            "normalized ratio: " + str(self.normalized_ratio),
            "normalized monzo: " + str(self.normalized_monzo),
            "MIDI key number class: " + utilities_general.convert_data_to_readable_string(self.keynum_class, precision = self.precision),
            "normalized complement: " + str(self.normalized_complement),
            "normalized harmonic distance: " + utilities_general.convert_data_to_readable_string(self.normalized_harmonic_distance, precision = self.precision),
            ""]
        reference_info_strings = [
            "",
            "REFERENCE INFO",
            "reference pitch (1/1): " + str(self.reference_pitch),
            "reference key number: " + utilities_general.convert_data_to_readable_string(self.reference_keynum, precision = self.precision),
            "reference frequency: " + utilities_general.convert_data_to_readable_string(self.reference_freq, precision = self.precision, suffix = " Hz"),
            ""]
        if variety == "basic":
            output = basic_info_strings
        elif variety == "normalized":
            output = normalized_info_strings
        elif variety == "reference":
            output = reference_info_strings
        elif variety == "all":
            output = basic_info_strings + normalized_info_strings[1:] + reference_info_strings[1:]
        return(output)

    def get_enharmonics(
        self, 
        tolerance = 1.95, 
        limit = 23, 
        exclude_primes = [], 
        max_symbols = 2, 
        max_hd = 30, 
        max_candidates = 10, 
        sort_by = "tolerance"):

        possible_enharmonics = []
        fund_offset = self._fund_offset
        vector_primes = self._vector_primes
        reference_pc_height = Pitch(p = self.normalized_monzo, rp = self.reference_pitch, rf = self.reference_freq).distance_in_cents_from_reference % 1200.0
        path_to_lookup_table = constants.RESOURCES_DIRECTORY + "/enharmonic_lookup_table.csv"
        with open(path_to_lookup_table, newline="") as f:
            reader = csv.reader(f)
            data = list(reader)
        min_candidate_pc_height = (reference_pc_height - tolerance) % 1200.0
        max_candidate_pc_height = (reference_pc_height + tolerance) % 1200.0
        starting_index_orientation = False
        if min_candidate_pc_height > max_candidate_pc_height:
            index_of_candidate = 0
            starting_index_orientation = "within tolerance"
        else:
            index_of_candidate = round((min_candidate_pc_height / 1200.0) * len(data))
        candidate_data = data[index_of_candidate]
        candidate_pc_height = ast.literal_eval(candidate_data[1])
        if not starting_index_orientation:
            if candidate_pc_height <= reference_pc_height:
                starting_index_orientation = "ascend only"
            elif candidate_pc_height >= reference_pc_height:
                starting_index_orientation = "descend only"
            else:
                starting_index_orientation = "within tolerance"
                        
        def get_enharmonics_from_span(orientation):
            nonlocal candidate_pc_height
            nonlocal index_of_candidate
            nonlocal min_candidate_pc_height
            nonlocal max_candidate_pc_height
                    
            if orientation == "ascend":
                def while_condition():
                    nonlocal candidate_pc_height
                    nonlocal max_candidate_pc_height
                    return(candidate_pc_height <= max_candidate_pc_height)
                incr_value = 1
                def break_condition():
                    nonlocal candidate_pc_height
                    nonlocal max_candidate_pc_height
                    return(candidate_pc_height > max_candidate_pc_height)
            else:
                def while_condition():
                    nonlocal candidate_pc_height
                    nonlocal min_candidate_pc_height
                    return(candidate_pc_height >= min_candidate_pc_height)
                incr_value = -1
                def break_condition():
                    nonlocal candidate_pc_height
                    nonlocal min_candidate_pc_height
                    return(candidate_pc_height < min_candidate_pc_height)
                        
            if max_candidate_pc_height < min_candidate_pc_height:
                def range_condition():
                    nonlocal candidate_pc_height
                    nonlocal min_candidate_pc_height
                    nonlocal max_candidate_pc_height
                    return( ((candidate_pc_height - 1200.0) <= max_candidate_pc_height and candidate_pc_height >= min_candidate_pc_height) or (candidate_pc_height <= max_candidate_pc_height and (candidate_pc_height + 1200.0) >= min_candidate_pc_height))
            else:
                def range_condition():
                    nonlocal candidate_pc_height
                    nonlocal min_candidate_pc_height
                    nonlocal max_candidate_pc_height
                    return(candidate_pc_height <= max_candidate_pc_height and candidate_pc_height >= min_candidate_pc_height)
                    
            while while_condition():
                candidate_data = data[index_of_candidate]
                candidate_pc_height = ast.literal_eval(candidate_data[1])
                if range_condition():
                    limit_ok = True
                    candidate_monzo = ast.literal_eval(candidate_data[0])
                    max_prime_index = vector_primes.index(limit)
                    for i in range(max_prime_index + 1, len(candidate_monzo)):
                        if candidate_monzo[i] != 0:
                            limit_ok = False
                    forbidden_prime_indices = [vector_primes.index(i) for i in exclude_primes]
                    for i in forbidden_prime_indices:
                        if candidate_monzo[i] != 0:
                            limit_ok = False
                    if limit_ok:
                        if abs(candidate_pc_height - reference_pc_height) > tolerance:
                            if candidate_pc_height > reference_pc_height:
                                candidate_monzo[0] = candidate_monzo[0] - 1
                            else:
                                candidate_monzo[0] = candidate_monzo[0] + 1
                        candidate_original_octave_difference = round((self.distance_in_cents_from_reference - reference_pc_height) / 1200)
                        candidate_monzo[0] = candidate_monzo[0] + candidate_original_octave_difference
                        candidate_pci = Pitch(p = candidate_monzo, rp = self.reference_pitch, rf = self.reference_freq)
                        if candidate_pci.ratio != self.ratio:
                            candidate_hd = candidate_pci.harmonic_distance
                            if candidate_hd <= max_hd:
                                candidate_num_symbols = candidate_pci.num_symbols
                                enharmonic_difference = round(candidate_pci.distance_in_cents_from_reference - self.distance_in_cents_from_reference, self.precision)
                                if candidate_num_symbols <= max_symbols:
                                    formatted_candidate = [candidate_pci.ratio, enharmonic_difference, candidate_hd, abs(enharmonic_difference)]
                                    possible_enharmonics.append(formatted_candidate)
                index_of_candidate = index_of_candidate + incr_value
                if break_condition():                                               
                    break

        if starting_index_orientation == "ascend only":
            get_enharmonics_from_span("ascend")
        elif starting_index_orientation == "descend only":
            get_enharmonics_from_span("descend")
        if starting_index_orientation == "within tolerance":
            ascending_index = index_of_candidate + 0
            index_of_candidate -= 1
            if index_of_candidate == 0:
                candidate_pc_height = 1200.0
            else:
                candidate_data = data[index_of_candidate]
                candidate_pc_height = ast.literal_eval(candidate_data[1])
            get_enharmonics_from_span("descend")
            index_of_candidate = ascending_index
            candidate_data = data[index_of_candidate]
            candidate_pc_height = ast.literal_eval(candidate_data[1])
            get_enharmonics_from_span("ascend")
        if len(possible_enharmonics) > 0:
            if sort_by == "harmonic distance":
                possible_enharmonics.sort(key=lambda x: x[3])
                possible_enharmonics.sort(key=lambda x: x[2])
            else:
                possible_enharmonics.sort(key=lambda x: x[2])
                possible_enharmonics.sort(key=lambda x: x[3])
        possible_enharmonics = possible_enharmonics[:max_candidates]
        if len(possible_enharmonics) > 0:
            for x in possible_enharmonics:
                x[3] =  self.ratio / x[0]
        return(possible_enharmonics)
        
    def print_info(self, variety = "basic"):
        strings_to_print = self.create_strings_for_print_and_txt(variety = variety)
        for x in strings_to_print:
            print(x)

    def print_enharmonics_info(
        self, 
        tolerance = 1.95, 
        limit = 23, 
        exclude_primes = [], 
        max_symbols = 2, 
        max_hd = 30, 
        max_candidates = 10, 
        sort_by = "tolerance"):
        enharmonics_info = self.get_enharmonics(
            tolerance = tolerance, 
            limit = limit, 
            exclude_primes = exclude_primes, 
            max_symbols = max_symbols, 
            max_hd = max_hd, 
            max_candidates = max_candidates, 
            sort_by = sort_by)
        num_enharmonics = len(enharmonics_info)
        header_strings = self._create_strings_for_enharmonics_header(
                tolerance = tolerance,
                limit = limit,
                exclude_primes = exclude_primes,
                max_symbols = max_symbols,
                max_hd = max_hd,
                max_candidates = max_candidates,
                sort_by = sort_by,
                num_qualified_candidates = num_enharmonics)
        print("")
        for x in header_strings:
            print(x)
        print("")
        if num_enharmonics > 0:
            enharmonics_strings = self._create_strings_for_enharmonics_info(enharmonics_info)
            for x in enharmonics_strings:
                print(x)

    def transpose(self, interval):
        new_ratio = self.ratio * Pitch(p = interval).ratio 
        self.update(p = new_ratio)

    def update(self, p = False, rp = False, rf = False, precision = False):
        if not p:
            p = self.monzo
        if not rp:
            rp = self.reference_pitch
        if not rf:
            rf = self.reference_freq
        if not precision:
            precision = self.precision
        self.__init__(p = p, rp = rp, rf = rf, precision = precision)

    def write_enharmonics_info_to_csv(
        self, 
        tolerance = 1.95, 
        limit = 23, 
        exclude_primes = [], 
        max_symbols = 2, 
        max_hd = 30, 
        max_candidates = 10, 
        sort_by = "tolerance",
        output_directory = False,
        filename = "enharmonic_candidates.csv"):
        enharmonics_info = self.get_enharmonics(
            tolerance = tolerance, 
            limit = limit, 
            exclude_primes = exclude_primes, 
            max_symbols = max_symbols, 
            max_hd = max_hd, 
            max_candidates = max_candidates, 
            sort_by = sort_by)
        num_enharmonics = len(enharmonics_info)
        header_strings = self._create_strings_for_enharmonics_header(
            tolerance = tolerance,
            limit = limit,
            exclude_primes = exclude_primes,
            max_symbols = max_symbols,
            max_hd = max_hd,
            max_candidates = max_candidates,
            sort_by = sort_by,
            num_qualified_candidates = num_enharmonics)
        formatted_header = []
        for x in header_strings:
            formatted_header.append([" ", x])
        formatted_header.append(" ")
        final_info = formatted_header
        if output_directory == False:
            output_directory = os.getcwd()
        path_to_write_file = output_directory + "/" + filename
        if num_enharmonics > 0:
            data_types = [
                "", 
                "ratio", 
                "monzo", 
                "freq (Hz)", 
                "keynum", 
                "primes", 
                "hd", 
                "HEJI", 
                "12-ED2", 
                "mel. ratio", 
                "enh. size (cents)"]
            count = 0
            processed_info = []
            for x in enharmonics_info:
                count += 1
                ratio = x[0]
                delta = x[1]
                ei = x[3]
                enharmonic_ici = Pitch(
                    p = (ratio.numerator, ratio.denominator), 
                    rp = self.reference_pitch, 
                    rf = self.reference_freq, 
                    precision = self.precision)
                stats_to_be_added = [count,
                    "'" + str(enharmonic_ici.ratio) + "'",
                    str(enharmonic_ici.monzo),
                    utilities_general.convert_data_to_readable_string(enharmonic_ici.freq, precision = self.precision),
                    utilities_general.convert_data_to_readable_string(enharmonic_ici.keynum, precision = self.precision),
                    str(enharmonic_ici.constituent_primes),
                    utilities_general.convert_data_to_readable_string(enharmonic_ici.harmonic_distance, precision = self.precision),
                    str(enharmonic_ici.notation),
                    "'" + str(enharmonic_ici.letter_name_and_octave_and_cents) + "'",
                    str(self._fraction_to_proportional_ratio_string(ei)),
                    str(delta)]
                processed_info.append(stats_to_be_added)
            final_info = formatted_header + [data_types] + processed_info
            with open(path_to_write_file, "w") as output:
                writer = csv.writer(output, lineterminator='\n')
                writer.writerows(final_info)
        print("file written to " + path_to_write_file)

    def write_enharmonics_info_to_txt(
        self, 
        tolerance = 1.95, 
        limit = 23, 
        exclude_primes = [], 
        max_symbols = 2, 
        max_hd = 30, 
        max_candidates = 10, 
        sort_by = "tolerance",
        output_directory = False,
        filename = "enharmonic_candidates.txt"):
        enharmonics_info = self.get_enharmonics(
            tolerance = tolerance, 
            limit = limit, 
            exclude_primes = exclude_primes, 
            max_symbols = max_symbols, 
            max_hd = max_hd, 
            max_candidates = max_candidates, 
            sort_by = sort_by)
        num_enharmonics = len(enharmonics_info)
        header_strings = self._create_strings_for_enharmonics_header(
            tolerance = tolerance,
            limit = limit,
            exclude_primes = exclude_primes,
            max_symbols = max_symbols,
            max_hd = max_hd,
            max_candidates = max_candidates,
            sort_by = sort_by,
            num_qualified_candidates = num_enharmonics)
        if output_directory == False:
            output_directory = os.getcwd()
        path_to_write_file = output_directory + "/" + filename
        with open(path_to_write_file, "w") as output:
            for x in header_strings:
                output.write(x + "\n")
            output.write(" \n")
            if num_enharmonics > 0:
                enharmonics_strings = self._create_strings_for_enharmonics_info(enharmonics_info)
                for x in enharmonics_strings:
                    output.write(x + "\n")
        print("file written to " + path_to_write_file)

    def write_info_to_txt(self, variety = "all", output_directory = False, filename = "pitch_info.txt"):
        strings_to_write = self.create_strings_for_print_and_txt(variety = variety)
        if output_directory == False:
            output_directory = os.getcwd()
        path_to_write_file = output_directory + "/" + filename
        with open(path_to_write_file, "w") as output:
            for x in strings_to_write:
                output.write(x + "\n")
        print("file written to " + path_to_write_file)

    def _complement(self):
        complement = 2 / self.ratio
        return(complement)

    def _constituent_primes(self):
        monzo = self.monzo
        vector_primes = self._vector_primes
        vector_primes = self._lengthen_vector_primes(monzo, vector_primes)
        constituent_primes = []
        for i, x in enumerate(monzo):
            if abs(x) > 0:
                constituent_primes.append(vector_primes[i])
        return(constituent_primes)

    def _create_strings_for_enharmonics_header(
        self, 
        tolerance = 1.95, 
        limit = 23, 
        exclude_primes = [], 
        max_symbols = 2, 
        max_hd = 30, 
        max_candidates = 10, 
        sort_by = "tolerance",
        num_qualified_candidates = 0):

        def excluded_primes_string():
            output = []
            if len(exclude_primes) > 0:
                output.append("excluded primes: " + str(exclude_primes))
            return(output)
                    
        header_strings = ["ORIGINAL PITCH INFO"] + self.create_strings_for_print_and_txt(variety = "basic")[2:] + [
            "ENHARMONIC SELECTION CRITERIA", 
            "tolerance (cents): " + utilities_general.convert_data_to_readable_string(tolerance, precision = 5),
            "prime limit: " + str(limit) ] + excluded_primes_string() + ["maximum number of HEJI symbols: " + str(max_symbols),
            "maximum mumber of candidates: " + str(max_candidates),
            "sorted by: " + str(sort_by),
            "total number of qualifying candidates: " + str(num_qualified_candidates)]
                    
        return(header_strings)

    def _create_strings_for_enharmonics_info(self, enharmonics_info):
        enharmonics_info_strings = []
        for i, x in enumerate(enharmonics_info):
            count = i + 1
            ratio = x[0]
            delta = x[1]
            if delta > 0:
                delta = "+" + str(delta)
            else:
                delta = str(delta)
            ei = x[3]
            enharmonics_info_strings.append("ENHARMONIC NO. " + str(count))
            enharmonic_ici = Pitch(p = (ratio.numerator, ratio.denominator), rp = self.reference_pitch, rf = self.reference_freq, precision = self.precision)
            enharmonic_info_strings = enharmonic_ici.create_strings_for_print_and_txt(variety = "basic")[2:][:-1]
            for x in enharmonic_info_strings:
                enharmonics_info_strings.append(x)
            enharmonics_info_strings.append("melodic interval from " + str(self.ratio) + ": " + self._fraction_to_proportional_ratio_string(ei))
            enharmonics_info_strings.append("enharmonic interval size (cents): " + str(delta))
            enharmonics_info_strings.append("")
        return(enharmonics_info_strings)

    def _distance_in_cents_from_reference(self):
        distance_in_cents_from_reference = (self.keynum - self.reference_keynum) * 100
        return(distance_in_cents_from_reference)

    def _fraction_to_proportional_ratio_string(self, f):
        return(str(f.numerator) + ":" + str(f.denominator))

    def _freq(self):
        freq = float(self.reference_freq * self.ratio)
        return(freq)

    def _harmonic_distance(self, monzo):
        vector_primes = self._vector_primes
        vector_primes = self._lengthen_vector_primes(monzo, vector_primes)
        harmonic_distance = 0
        for i in range(0, len(monzo)):
            current_prime = vector_primes[i]
            current_exponent = abs(monzo[i])
            current_hd = current_exponent * math.log2(current_prime)
            harmonic_distance += current_hd
        return(harmonic_distance)

    def _keynum(self):
        keynum = utilities_music.cpsmidi(self.freq, 
            ref_freq = self.reference_freq, 
            ref_keynum = self.reference_keynum)
        return(keynum) 

    def _letter_name_and_octave_and_cents(self):
        pitch_class_letter_name_index = math.floor(self.keynum_class)
        pitch_octave = int(divmod(self.keynum, 12)[0] - 1)
        pitch_cents = self.keynum_class % 1
        if (1 - pitch_cents) < pitch_cents:
            pitch_cents = 1 - pitch_cents
            cents_sign = "-"
            pitch_class_letter_name_index += 1
        else:
            cents_sign = "+"
        pitch_class_letter_name_index = int(pitch_class_letter_name_index) % 12
        pitch_class_letter_name_strings = ["C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B"]
        pitch_class_letter_name = pitch_class_letter_name_strings[pitch_class_letter_name_index]
        return(pitch_class_letter_name + str(pitch_octave) + " " + cents_sign + str(round(pitch_cents * 100, self.precision)))

    def _lengthen_vector_primes(self, monzo, vector_primes):
        if len(monzo) > len(vector_primes):
            x = vector_primes[-1:][0]
            while len(vector_primes) < len(monzo):
                vector_primes = prime_list.PrimeList(max_val = x + 1).primes
                x += 1
                if len(vector_primes) >= len(monzo):
                    break
        return(vector_primes)

    def _monzo_from_ratio(self):
        if self.ratio == fractions.Fraction(1, 1):
            monzo = [0] * len(self._vector_primes)
        else:              
            numerators = LONG_LIST_OF_PRIMES.factors(self.ratio.numerator)
            denominators = LONG_LIST_OF_PRIMES.factors(self.ratio.denominator)
            max_default_prime = self._vector_primes[-1:][0]
            all_primes = []
            for x in numerators + denominators:
                all_primes.append(x[0])
            max_prime_in_ratio = max(all_primes)
            if max_prime_in_ratio > max_default_prime:
                self._vector_primes = prime_list.PrimeList(max_val = max_prime_in_ratio + 1).primes
            monzo = []
            for i in range(0, len(self._vector_primes)):
                monzo.append(0)
            for x in numerators:
                for i in range(0, len(self._vector_primes)):
                    current_prime = self._vector_primes[i]
                    if x[0] == current_prime:
                        monzo[i] += x[1]
            for x in denominators:
                for i in range(0, len(self._vector_primes)):
                    current_prime = self._vector_primes[i]
                    if x[0] == current_prime:
                        monzo[i] -= x[1]
        trimmed_monzo = self._trim_monzo(monzo)
        return(trimmed_monzo)

    def _normalized_monzo(self, monzo):
        ratio = self.ratio
        normalized_monzo = [] + monzo
        while (ratio.numerator - ratio.denominator) < 0:
            normalized_monzo[0] += 1
            ratio = Pitch(p = normalized_monzo).ratio
            if (ratio.numerator - ratio.denominator) >= 0:
                break
        while (ratio.numerator - ratio.denominator) >= ratio.denominator:
            normalized_monzo[0] -= 1
            ratio = Pitch(p = normalized_monzo).ratio
            if (ratio.numerator - ratio.denominator) < ratio.denominator:
                break                
        return(normalized_monzo)

    def _normalized_ratio(self, ratio):
        num = ratio.numerator
        den = ratio.denominator
        condition = num / den < 1
        while condition:
            num = num * 2
            condition = num / den < 1
        condition = num / den >= 2
        while condition:
            den = den * 2
            condition = num / den >= 2
        normalized_ratio = fractions.Fraction(num, den)
        return(normalized_ratio)
        
    def _normalized_harmonic_distance(self):
        normalized_harmonic_distance = Pitch(p = self.normalized_monzo)._harmonic_distance()
        return(normalized_harmonic_distance)

    def _notation(self):
        fund_offset = self._fund_offset
        monzo = self.monzo
        vector_primes = self._vector_primes
        vector_primes = self._lengthen_vector_primes(monzo, vector_primes)
        accidental_undefined = False
        letter_name_undefined = False
        net_3 = 0 + fund_offset # keep track of how many P5s we are moving at all times
        syntonic_arrows = 0
        accidental_characters = []
        for i in range(0, len(monzo)):
            current_prime = vector_primes[i]
            current_exp = monzo[i]
            if current_prime == 3:
                net_3 += current_exp
            elif current_prime == 5:
                net_3 += 4 * current_exp
                syntonic_arrows += current_exp
                if abs(syntonic_arrows) > 4:
                    accidental_undefined = True
            elif current_prime == 7:
                net_3 -= 2 * current_exp
                double_seven, single_seven = divmod(abs(current_exp), 2)
                if current_exp > 0:
                    for _ in range(single_seven):
                        accidental_characters.append("<")
                    for _ in range(double_seven):
                        accidental_characters.append(",")
                elif current_exp < 0:
                    for _ in range(single_seven):
                        accidental_characters.append(">")
                    for _ in range(double_seven):
                        accidental_characters.append(".")
            elif current_prime > 47:
                accidental_undefined = True
                letter_name_undefined = True
            remaining_prime_adjustments = [
                [11, -1, ["4", "5"]],
                [13, 3, ["0", "9"]],
                [17, 7, [":", ";"]],
                [19, -3, ["/", "*"]],
                [23, 6, ["3", "6"]],
                [29, -2, ["2", "7"]],
                [31, 0, ["1", "8"]],
                [37, 2, ["á", "à"]],
                [41, 4, ["+", "-"]],
                [43, -1, ["é", "è"]],
                [47, 6, ["í", "ì"]]]
            for x in remaining_prime_adjustments:
                if current_prime == x[0]:
                    exp_adj = x[1]
                    pos_str = x[2][0]
                    neg_str = x[2][1]
                    net_3 = net_3 + (exp_adj * current_exp)
                    if current_exp > 0:
                        for _ in range(current_exp):
                            accidental_characters.append(pos_str)
                    elif current_exp < 0:
                        for _ in range(abs(current_exp)):
                            accidental_characters.append(neg_str)

        def add_5_limit_sign(acc_chars):
            for i, acc_char in enumerate(acc_chars):
                if syntonic_arrows == i - 4:
                    if abs(net_3) < 4:
                        if syntonic_arrows == 0 and len(accidental_characters) == 0:
                            accidental_characters.insert(0, acc_char)
                        elif syntonic_arrows != 0:
                            accidental_characters.insert(0, acc_char)
                    else:
                        accidental_characters.insert(0, acc_char)
            return()

        if abs(net_3) < 4:
            add_5_limit_sign(["N", "q", "p", "o", "n", "m", "l", "k", "M"])
        elif abs(net_3) > 3 and abs(net_3) < 11:
            if net_3 > 0:
                add_5_limit_sign(["P", "y", "x", "w", "v", "u", "t", "s", "O"])
            else:
                add_5_limit_sign(["L", "h", "g", "f", "e", "d", "c", "b", "K"])
        elif abs(net_3) > 10:
            if net_3 > 0:
                add_5_limit_sign(["Q", "Y", "X", "W", "V", "U", "T", "S", "R"])
            else:
                add_5_limit_sign(["J", "H", "G", "F", "E", "D", "C", "B", "I"])
        excess_3_beyond_doublesharps_and_flats = abs(net_3) - 17
        if excess_3_beyond_doublesharps_and_flats > 0:
            num_excess_signs = math.ceil(excess_3_beyond_doublesharps_and_flats / 7)
            double_three, single_three = divmod(num_excess_signs, 2)
            if net_3 > 0:
                for _ in range(single_three):
                    accidental_characters.insert(1, "v")
                for _ in range(double_three):
                    accidental_characters.insert(1, "V")
            elif net_3 < 0:
                for _ in range(single_three):
                    accidental_characters.insert(1, "e")
                for _ in range(double_three):
                    accidental_characters.insert(1, "E")
        accidental_characters = list(reversed(accidental_characters))
        accidental_string = ""
        letter_names = ["D", "A", "E", "B", "F", "C", "G"]
        if letter_name_undefined:
            letter_name = "undefined"
        else:
            letter_name = letter_names[net_3 % 7]
        if accidental_undefined:
            accidental_string = "undefined"
        else:
            for x in accidental_characters:
                accidental_string += x
        return((accidental_string, letter_name))

    def _pitch_info(self):
        basic_info = [
            self.ratio,
            self.monzo,
            self.constituent_primes,
            self.freq,
            self.keynum,
            self.distance_in_cents_from_reference,
            self.harmonic_distance,
            (self.accidental_string, self.letter_name),
            self.letter_name_and_octave_and_cents]
        normalized_info = [
            self.normalized_ratio,
            self.normalized_monzo,
            self.keynum_class,
            self.normalized_complement,
            self.normalized_harmonic_distance]
        reference_info = [
            self.reference_pitch,
            self.reference_keynum,
            self.reference_freq]
        return([basic_info, normalized_info, reference_info])

    def _ratio_from_monzo(self):
        monzo = self.monzo
        vector_primes = self._vector_primes
        vector_primes = self._lengthen_vector_primes(monzo, vector_primes)
        numerator = 1
        denominator = 1
        for i in range(0, len(monzo)):
            current_prime = vector_primes[i]
            current_exp = monzo[i]
            if current_exp > 0:
                numerator = numerator * (current_prime ** current_exp)
            if current_exp < 0:
                denominator = denominator * (current_prime ** abs(current_exp))
        ratio = utilities_general.tuple_to_fraction((numerator, denominator))
        return(ratio)

    def _reference_keynum_and_fund_offset_from_pitch_letter_name_and_octave(self):
        rp_string = str(self.reference_pitch) + ""
        possible_letter_names = ["F", "C", "G", "D", "A", "E", "B"]
        possible_keynum_classes = [5, 0, 7, 2, 9, 4, 11]
        letter_name = False
        octave_number = False
        output = False
        fund_offset = 0
        if rp_string[0] in possible_letter_names:
            letter_name = rp_string[0]
            keynum_class = possible_keynum_classes[possible_letter_names.index(letter_name)]
            fund_offset = possible_letter_names.index(letter_name) - 3
            rp_string = rp_string[1:]
        if letter_name is not False and len(rp_string) > 0:
            if rp_string[-1].isdigit():
                octave_number = int(rp_string[-1])
                if len(rp_string) > 1 and rp_string[-2] == "-":
                    octave_number = octave_number * -1
                    rp_string = rp_string[:-1]
                rp_string = rp_string[:-1]
                for x in rp_string:
                    if x == "#":
                        fund_offset += 7
                        keynum_class += 1
                    elif x == "x":
                        fund_offset += 14
                        keynum_class += 2
                    elif x == "b":
                        fund_offset -= 7
                        keynum_class -= 1
                keynum = 12 + (12 * octave_number) + keynum_class
                output = [keynum, fund_offset]
        return(output)

    def _trim_monzo(self, monzo):
        index_of_highest_nonzero_exponent = 0
        for i, x in enumerate(monzo):
            if abs(x) > 0:
                index_of_highest_nonzero_exponent = i
        trimmed_monzo = monzo[:index_of_highest_nonzero_exponent + 1]
        return(trimmed_monzo)