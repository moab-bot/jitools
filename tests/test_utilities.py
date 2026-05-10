import fractions
import math
import pytest
from jitools import utilities_general, utilities_music


# ── utilities_general ─────────────────────────────────────────────────────────

class TestTupleToFraction:
    def test_basic(self):
        assert utilities_general.tuple_to_fraction((3, 2)) == fractions.Fraction(3, 2)

    def test_reduces(self):
        assert utilities_general.tuple_to_fraction((4, 8)) == fractions.Fraction(1, 2)

    def test_unison(self):
        assert utilities_general.tuple_to_fraction((1, 1)) == fractions.Fraction(1, 1)


class TestTuplesToFractions:
    def test_converts_list(self):
        result = utilities_general.tuples_to_fractions([(1, 1), (3, 2), (5, 4)])
        assert result == [
            fractions.Fraction(1, 1),
            fractions.Fraction(3, 2),
            fractions.Fraction(5, 4),
        ]

    def test_empty_list(self):
        assert utilities_general.tuples_to_fractions([]) == []


class TestLcm:
    @pytest.mark.parametrize("lst,expected", [
        ([4, 6],       12),
        ([3, 5, 7],   105),
        ([1, 1],        1),
        ([12, 8],      24),
        ([6],           6),
    ])
    def test_known_values(self, lst, expected):
        assert utilities_general.lcm(lst) == expected


class TestFlop:
    def test_square_matrix(self):
        assert utilities_general.flop([[1, 2], [3, 4]]) == [[1, 3], [2, 4]]

    def test_rectangular(self):
        assert utilities_general.flop([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]]

    def test_uneven_truncates_to_min_length(self):
        assert utilities_general.flop([[1, 2], [3, 4, 5]]) == [[1, 3], [2, 4]]


class TestConvertDataToReadableString:
    def test_float_rounded_to_precision(self):
        s = utilities_general.convert_data_to_readable_string(1.23456789, precision=3)
        assert s == "1.235"

    def test_fraction_not_rounded(self):
        f = fractions.Fraction(3, 2)
        assert utilities_general.convert_data_to_readable_string(f) == "3/2"

    def test_integer_not_rounded(self):
        assert utilities_general.convert_data_to_readable_string(42) == "42"

    def test_prefix(self):
        s = utilities_general.convert_data_to_readable_string(440.0, prefix="~")
        assert s.startswith("~")

    def test_suffix(self):
        s = utilities_general.convert_data_to_readable_string(440.0, suffix=" Hz")
        assert s.endswith(" Hz")

    def test_prefix_and_suffix(self):
        s = utilities_general.convert_data_to_readable_string(440.0, prefix="[", suffix="]")
        assert s.startswith("[") and s.endswith("]")


# ── utilities_music ───────────────────────────────────────────────────────────

class TestCpsMidi:
    def test_reference_pitch(self):
        assert utilities_music.cpsmidi(440.0, 440.0, 69) == pytest.approx(69.0)

    def test_octave_up(self):
        assert utilities_music.cpsmidi(880.0, 440.0, 69) == pytest.approx(81.0)

    def test_octave_down(self):
        assert utilities_music.cpsmidi(220.0, 440.0, 69) == pytest.approx(57.0)

    def test_perfect_fifth(self):
        expected = 69 + 12 * math.log2(3 / 2)
        assert utilities_music.cpsmidi(660.0, 440.0, 69) == pytest.approx(expected)


class TestMidiCps:
    def test_reference_pitch(self):
        assert utilities_music.midicps(69, 69, 440.0) == pytest.approx(440.0)

    def test_octave_up(self):
        assert utilities_music.midicps(81, 69, 440.0) == pytest.approx(880.0)

    def test_roundtrip(self):
        freq = 550.0
        keynum = utilities_music.cpsmidi(freq, 440.0, 69)
        assert utilities_music.midicps(keynum, 69, 440.0) == pytest.approx(freq)
