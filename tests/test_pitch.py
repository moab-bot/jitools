import ast
import csv
import fractions
import math
import pytest
from jitools import constants
from jitools.pitch import Pitch


# ── ground truth table ────────────────────────────────────────────────────────
# All values derived from first principles; reference A4 = 440 Hz (keynum 69).

PITCH_CASES = [
    {
        "id": "1/1",
        "input": (1, 1),
        "ratio": fractions.Fraction(1, 1),
        "monzo": [0],
        "freq": 440.0,
        "cents": 0.0,
        "hd": 0.0,
        "constituent_primes": [],
        "normalized_ratio": fractions.Fraction(1, 1),
        "complement": fractions.Fraction(2, 1),
    },
    {
        "id": "3/2",
        "input": (3, 2),
        "ratio": fractions.Fraction(3, 2),
        "monzo": [-1, 1],
        "freq": 660.0,
        "cents": 1200 * math.log2(3 / 2),
        "hd": math.log2(2) + math.log2(3),
        "constituent_primes": [2, 3],
        "normalized_ratio": fractions.Fraction(3, 2),
        "complement": fractions.Fraction(4, 3),
    },
    {
        "id": "4/3",
        "input": (4, 3),
        "ratio": fractions.Fraction(4, 3),
        "monzo": [2, -1],
        "freq": float(440 * fractions.Fraction(4, 3)),
        "cents": 1200 * math.log2(4 / 3),
        "hd": 2 * math.log2(2) + math.log2(3),
        "constituent_primes": [2, 3],
        "normalized_ratio": fractions.Fraction(4, 3),
        "complement": fractions.Fraction(3, 2),
    },
    {
        "id": "5/4",
        "input": (5, 4),
        "ratio": fractions.Fraction(5, 4),
        "monzo": [-2, 0, 1],
        "freq": 550.0,
        "cents": 1200 * math.log2(5 / 4),
        "hd": 2 * math.log2(2) + math.log2(5),
        "constituent_primes": [2, 5],
        "normalized_ratio": fractions.Fraction(5, 4),
        "complement": fractions.Fraction(8, 5),
    },
    {
        "id": "7/4",
        "input": (7, 4),
        "ratio": fractions.Fraction(7, 4),
        "monzo": [-2, 0, 0, 1],
        "freq": 770.0,
        "cents": 1200 * math.log2(7 / 4),
        "hd": 2 * math.log2(2) + math.log2(7),
        "constituent_primes": [2, 7],
        "normalized_ratio": fractions.Fraction(7, 4),
        "complement": fractions.Fraction(8, 7),
    },
]


# ── initialization ────────────────────────────────────────────────────────────

class TestPitchInitialization:
    def test_from_tuple(self):
        p = Pitch(p=(3, 2))
        assert p.ratio == fractions.Fraction(3, 2)

    def test_from_fraction(self):
        p = Pitch(p=fractions.Fraction(3, 2))
        assert p.ratio == fractions.Fraction(3, 2)

    def test_from_monzo(self):
        # [-1, 1] == 2^-1 * 3^1 == 3/2
        p = Pitch(p=[-1, 1])
        assert p.ratio == fractions.Fraction(3, 2)

    def test_all_three_forms_agree(self):
        assert (
            Pitch(p=(5, 4)).ratio
            == Pitch(p=fractions.Fraction(5, 4)).ratio
            == Pitch(p=[-2, 0, 1]).ratio
        )

    def test_default_reference_pitch(self):
        p = Pitch()
        assert p.reference_pitch == "A4"
        assert p.reference_freq == 440.0


# ── core properties ───────────────────────────────────────────────────────────

@pytest.mark.parametrize("case", PITCH_CASES, ids=[c["id"] for c in PITCH_CASES])
class TestPitchProperties:
    def test_ratio(self, case):
        assert Pitch(p=case["input"]).ratio == case["ratio"]

    def test_monzo(self, case):
        assert Pitch(p=case["input"]).monzo == case["monzo"]

    def test_constituent_primes(self, case):
        assert Pitch(p=case["input"]).constituent_primes == case["constituent_primes"]

    def test_freq(self, case):
        assert Pitch(p=case["input"]).freq == pytest.approx(case["freq"], rel=1e-9)

    def test_cents_from_reference(self, case):
        assert Pitch(p=case["input"]).distance_in_cents_from_reference == pytest.approx(
            case["cents"], abs=1e-6
        )

    def test_harmonic_distance(self, case):
        assert Pitch(p=case["input"]).harmonic_distance == pytest.approx(case["hd"], rel=1e-9)

    def test_normalized_ratio(self, case):
        assert Pitch(p=case["input"]).normalized_ratio == case["normalized_ratio"]

    def test_complement(self, case):
        assert Pitch(p=case["input"]).complement == case["complement"]


# ── normalization ─────────────────────────────────────────────────────────────

class TestNormalization:
    def test_ratio_below_one_shifts_up(self):
        # 1/2 → 1/1 (multiply by 2)
        assert Pitch(p=(1, 2)).normalized_ratio == fractions.Fraction(1, 1)

    def test_ratio_at_two_shifts_down(self):
        # 2/1 >= 2 → normalized to 1/1
        assert Pitch(p=(2, 1)).normalized_ratio == fractions.Fraction(1, 1)

    def test_ratio_above_two_shifts_down(self):
        # 3/1 → 3/2
        assert Pitch(p=(3, 1)).normalized_ratio == fractions.Fraction(3, 2)

    def test_already_normalized_unchanged(self):
        for t in [(3, 2), (5, 4), (7, 4), (4, 3)]:
            p = Pitch(p=t)
            assert 1 <= float(p.normalized_ratio) < 2

    def test_complement_of_fifth_is_fourth(self):
        assert Pitch(p=(3, 2)).complement == fractions.Fraction(4, 3)

    def test_complement_of_major_third_is_minor_sixth(self):
        assert Pitch(p=(5, 4)).complement == fractions.Fraction(8, 5)

    def test_normalized_harmonic_distance_leq_raw(self):
        # Bringing 1/4 to its normalized form should not increase HD
        p = Pitch(p=(1, 4))
        assert p.normalized_harmonic_distance <= p.harmonic_distance


# ── reference pitch parsing ───────────────────────────────────────────────────

REFERENCE_PITCH_CASES = [
    ("A4",  69,  1),
    ("C4",  60, -2),
    ("D4",  62,  0),
    ("E4",  64,  2),
    ("G4",  67, -1),
    ("C#4", 61,  5),
    ("Bb3", 58, -4),
]


@pytest.mark.parametrize("rp,expected_keynum,_", REFERENCE_PITCH_CASES)
def test_reference_keynum(rp, expected_keynum, _):
    p = Pitch(p=(1, 1), rp=rp)
    assert p.reference_keynum == expected_keynum


@pytest.mark.parametrize("rp,_,expected_fund_offset", REFERENCE_PITCH_CASES)
def test_reference_fund_offset(rp, _, expected_fund_offset):
    p = Pitch(p=(1, 1), rp=rp)
    assert p._fund_offset == expected_fund_offset


def test_invalid_reference_pitch_raises():
    with pytest.raises(ValueError):
        Pitch(p=(1, 1), rp="Z9")


# ── input validation ──────────────────────────────────────────────────────────

class TestValidation:
    def test_zero_numerator_raises(self):
        with pytest.raises(ValueError):
            Pitch(p=(0, 1))

    def test_zero_denominator_raises(self):
        with pytest.raises(ValueError):
            Pitch(p=(1, 0))

    def test_negative_numerator_raises(self):
        with pytest.raises(ValueError):
            Pitch(p=(-3, 2))

    def test_float_tuple_elements_raise(self):
        with pytest.raises(TypeError):
            Pitch(p=(1.5, 2))

    def test_wrong_tuple_length_raises(self):
        with pytest.raises(ValueError):
            Pitch(p=(1, 2, 3))

    def test_string_p_raises(self):
        with pytest.raises(TypeError):
            Pitch(p="3/2")

    def test_zero_rf_raises(self):
        with pytest.raises(ValueError):
            Pitch(p=(1, 1), rf=0)

    def test_negative_rf_raises(self):
        with pytest.raises(ValueError):
            Pitch(p=(1, 1), rf=-440)

    def test_negative_precision_raises(self):
        with pytest.raises(ValueError):
            Pitch(p=(1, 1), precision=-1)


# ── HEJI notation ─────────────────────────────────────────────────────────────

class TestNotation:
    # Letter names for simple Pythagorean intervals above A4.
    # Verified by the chain of perfect fifths: F-C-G-D-A-E-B
    @pytest.mark.parametrize("ratio,expected_letter", [
        ((1, 1), "A"),   # unison above A
        ((3, 2), "E"),   # perfect fifth: A→E
        ((4, 3), "D"),   # perfect fourth: A→D
        ((2, 3), "D"),   # downward fourth (same letter class)
        ((9, 8), "B"),   # Pythagorean major second: A→B
    ])
    def test_pythagorean_letter_names(self, ratio, expected_letter):
        p = Pitch(p=ratio, rp="A4")
        assert p.letter_name == expected_letter

    def test_notation_is_pair_of_strings(self):
        p = Pitch(p=(3, 2))
        assert isinstance(p.notation, tuple)
        assert len(p.notation) == 2
        assert all(isinstance(x, str) for x in p.notation)

    def test_letter_name_in_valid_set(self):
        valid = {"A", "B", "C", "D", "E", "F", "G"}
        for t in [(1, 1), (3, 2), (5, 4), (4, 3), (7, 4)]:
            p = Pitch(p=t, rp="A4")
            assert p.letter_name in valid

    def test_prime_above_47_is_undefined(self):
        # 53 is prime, > 47 → notation undefined
        p = Pitch(p=(53, 32))
        assert p.notation == ("undefined", "undefined")
        assert p.num_symbols == "undefined"


# ── harmonic distance ─────────────────────────────────────────────────────────

class TestHarmonicDistance:
    def test_unison_is_zero(self):
        assert Pitch(p=(1, 1)).harmonic_distance == 0.0

    def test_hd_increases_with_complexity(self):
        # Tenney HD: 3/2 < 5/4 < 7/4 (by log-product of n*d)
        hd_fifth = Pitch(p=(3, 2)).harmonic_distance
        hd_third = Pitch(p=(5, 4)).harmonic_distance
        hd_seventh = Pitch(p=(7, 4)).harmonic_distance
        assert hd_fifth < hd_third < hd_seventh

    def test_normalized_hd_leq_raw_hd(self):
        # Normalizing to [1,2) should not increase harmonic distance
        p = Pitch(p=(1, 4))
        assert p.normalized_harmonic_distance <= p.harmonic_distance


# ── update and transpose ──────────────────────────────────────────────────────

class TestUpdateAndTranspose:
    def test_transpose_stacks_ratios(self):
        p = Pitch(p=(3, 2))
        p.transpose((3, 2))
        assert p.ratio == fractions.Fraction(9, 4)

    def test_update_changes_ratio(self):
        p = Pitch(p=(1, 1))
        p.update(p=(3, 2))
        assert p.ratio == fractions.Fraction(3, 2)

    def test_update_changes_reference(self):
        p = Pitch(p=(1, 1), rp="A4")
        p.update(rp="C4")
        assert p.reference_pitch == "C4"
        assert p.reference_keynum == 60

    def test_update_preserves_unchanged_params(self):
        p = Pitch(p=(3, 2), rp="A4", rf=440.0)
        p.update(p=(5, 4))
        assert p.reference_pitch == "A4"
        assert p.reference_freq == 440.0


# ── notation: accidental strings ─────────────────────────────────────────────
# Expected values derived by tracing _notation() for each ratio with rp="A4"
# (fund_offset=1). Characters are HEJI font glyphs, not ASCII accidentals.
#
#  Pythagorean (no 5/7/11… adjustment):
#    net_3 in [-3,3]  → natural-range list, "n" = natural sign at syntonic_arrows=0
#  5-limit (syntonic_arrows ≠ 0, net_3 shifts by ±4 per arrow):
#    positive arrows  → sharp-range list ("u" = sharp+1 syntonic down, etc.)
#    negative arrows  → natural-range list ("o" = natural+1 syntonic up, etc.)
#  7-limit: "<" = 7-comma down, ">" = 7-comma up
#  11-limit: "4" = 11-limit raised (net_3 adj = -1 per exp)
#  13-limit: "0" symbol + sharp sign "v" when net_3 lands in sharp range

NOTATION_CASES = [
    # ── Pythagorean ──────────────────────────────────────────────────────────
    # net_3 = fund_offset(1) + 3-exponent
    ((1, 1),  "A4", "n",   "A"),  # net_3=1,  0 fifths from D → A
    ((3, 2),  "A4", "n",   "E"),  # net_3=2,  +1 fifth        → E
    ((4, 3),  "A4", "n",   "D"),  # net_3=0,  -1 fifth        → D
    ((9, 8),  "A4", "n",   "B"),  # net_3=3,  +2 fifths       → B
    # ── 5-limit ──────────────────────────────────────────────────────────────
    # 5^+1 shifts net_3 by +4 and syntonic_arrows by +1
    # 5/4: net_3=5 (sharp range), syntonic_arrows=1 → "u" = sharp + syntonic-down
    ((5, 4),  "A4", "u",   "C"),
    # 6/5: net_3=-2, syntonic_arrows=-1 → "o" = natural + syntonic-up
    ((6, 5),  "A4", "o",   "C"),
    # ── 7-limit ──────────────────────────────────────────────────────────────
    # 7^+1 shifts net_3 by -2 and appends "<"
    ((7, 4),  "A4", "<",   "G"),  # net_3=-1
    ((7, 6),  "A4", "<",   "C"),  # net_3=-2  (also -1 from prime-3)
    # ── 11-limit ─────────────────────────────────────────────────────────────
    # 11^+1: net_3 adj=-1, symbol "4"; net_3=0 → no 5-limit sign added
    ((11, 8), "A4", "4",   "D"),
    # ── 13-limit ─────────────────────────────────────────────────────────────
    # 13^+1: net_3 adj=+3, symbol "0"; net_3=4 (sharp range) → "v" inserted
    # reversed accidental_characters: ["v","0"] → "0v"
    ((13, 8), "A4", "0v",  "F"),
    # ── undefined: syntonic_arrows > 4 ───────────────────────────────────────
    # 5^5 / 2^10 = 3125/1024 → syntonic_arrows=5 → accidental_undefined=True
    ((3125, 1024), "A4", "undefined", "D"),
    # ── extreme Pythagorean: net_3 > 10 ──────────────────────────────────────
    # 3^11 / 2^17 = 177147/131072 → net_3=12 → double-sharp range, "V"
    ((177147, 131072), "A4", "V", "C"),
]


@pytest.mark.parametrize("ratio,rp,expected_acc,expected_letter", NOTATION_CASES)
def test_notation_accidental_string(ratio, rp, expected_acc, expected_letter):
    p = Pitch(p=ratio, rp=rp)
    assert p.accidental_string == expected_acc
    assert p.letter_name == expected_letter


# ── enharmonics ───────────────────────────────────────────────────────────────

class TestEnharmonics:
    """Tests that read the default 6.8 MB enharmonic lookup table shipped with the library."""

    def test_returns_list(self):
        result = Pitch(p=(81, 80)).get_enharmonics()
        assert isinstance(result, list)

    def test_entry_format(self):
        result = Pitch(p=(81, 80)).get_enharmonics()
        for entry in result:
            assert len(entry) == 4
            ratio, delta, hd, melodic = entry
            assert isinstance(ratio, fractions.Fraction)
            assert isinstance(delta, float)
            assert isinstance(hd, float)
            assert isinstance(melodic, fractions.Fraction)

    def test_all_within_tolerance(self):
        tol = 1.95
        result = Pitch(p=(81, 80)).get_enharmonics(tolerance=tol)
        for entry in result:
            assert abs(entry[1]) <= tol

    def test_max_candidates_respected(self):
        result = Pitch(p=(81, 80)).get_enharmonics(max_candidates=3)
        assert len(result) <= 3

    def test_empty_when_no_candidates(self):
        # Tolerance 0 and max_hd 0 → nothing qualifies
        result = Pitch(p=(3, 2)).get_enharmonics(tolerance=0.0, max_hd=0.0)
        assert result == []

    def test_excludes_original_ratio(self):
        p = Pitch(p=(81, 80))
        result = p.get_enharmonics()
        returned_ratios = [e[0] for e in result]
        assert p.ratio not in returned_ratios

    def test_lookup_table_accepts_path_string(self):
        bundled = constants.RESOURCES_DIRECTORY + "/enharmonic_lookup_table.csv"
        result_default = Pitch(p=(81, 80)).get_enharmonics()
        result_path = Pitch(p=(81, 80)).get_enharmonics(lookup_table=bundled)
        assert result_path == result_default

    def test_lookup_table_accepts_list(self):
        bundled = constants.RESOURCES_DIRECTORY + "/enharmonic_lookup_table.csv"
        with open(bundled, newline="") as f:
            table_as_list = [(ast.literal_eval(row[0]), float(row[1])) for row in csv.reader(f)]
        result_default = Pitch(p=(81, 80)).get_enharmonics()
        result_list = Pitch(p=(81, 80)).get_enharmonics(lookup_table=table_as_list)
        assert result_list == result_default


# ── file I/O ──────────────────────────────────────────────────────────────────

class TestFileIO:
    def test_write_info_to_txt_creates_file(self, tmp_path):
        Pitch(p=(3, 2)).write_info_to_txt(output_path=str(tmp_path / "pitch_info.txt"))
        assert (tmp_path / "pitch_info.txt").exists()

    def test_write_info_to_txt_tilde_expansion(self, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))
        Pitch(p=(3, 2)).write_info_to_txt(output_path="~/pitch_info.txt")
        assert (tmp_path / "pitch_info.txt").exists()

    def test_write_enharmonics_info_to_csv_tilde_expansion(self, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))
        Pitch(p=(81, 80)).write_enharmonics_info_to_csv(output_path="~/enh.csv")
        assert (tmp_path / "enh.csv").exists()

    def test_write_enharmonics_info_to_txt_tilde_expansion(self, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))
        Pitch(p=(81, 80)).write_enharmonics_info_to_txt(output_path="~/enh.txt")
        assert (tmp_path / "enh.txt").exists()

    def test_write_enharmonics_info_to_csv_no_leading_space(self, tmp_path):
        path = str(tmp_path / "enh.csv")
        Pitch(p=(81, 80)).write_enharmonics_info_to_csv(output_path=path)
        with open(path, newline="") as f:
            first_line = f.readline()
        assert first_line.startswith(",")
