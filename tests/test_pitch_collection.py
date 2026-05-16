import fractions
import math
import pytest
from jitools.pitch_collection import PitchCollection


def make_pc(ratios, **kwargs):
    return PitchCollection(pc=ratios, **kwargs)


# ── initialization ────────────────────────────────────────────────────────────

class TestInit:
    def test_basic_construction(self):
        col = make_pc([(1, 1), (4, 3), (3, 2)])
        assert len(col.ratios) == 3

    def test_duplicates_are_removed(self):
        col = make_pc([(1, 1), (1, 1), (3, 2)])
        assert len(col.ratios) == 2

    def test_ratios_sorted_ascending_after_init(self):
        col = make_pc([(3, 2), (1, 1), (5, 4)])
        for i in range(len(col.ratios) - 1):
            assert col.ratios[i] <= col.ratios[i + 1]

    def test_default_reference(self):
        col = make_pc([(1, 1), (3, 2)])
        assert col.reference_pitch == "A4"
        assert col.reference_freq == 440.0

    def test_custom_reference_freq(self):
        col = make_pc([(1, 1), (3, 2)], rf=432.0)
        assert col.freqs[0] == pytest.approx(432.0)


# ── intervals ─────────────────────────────────────────────────────────────────

class TestIntervals:
    def test_two_pitches_one_interval(self):
        col = make_pc([(1, 1), (3, 2)])
        assert len(col.intervals) == 1
        assert col.intervals[0] == fractions.Fraction(3, 2)

    def test_three_pitches_three_intervals(self):
        col = make_pc([(1, 1), (5, 4), (3, 2)])
        assert len(col.intervals) == 3

    def test_known_intervals(self):
        # [1, 4/3, 3/2] → intervals: 4/3, 3/2, 9/8
        col = make_pc([(1, 1), (4, 3), (3, 2)])
        interval_set = set(col.intervals)
        assert fractions.Fraction(4, 3) in interval_set
        assert fractions.Fraction(3, 2) in interval_set
        assert fractions.Fraction(9, 8) in interval_set

    def test_sequential_intervals(self):
        col = make_pc([(1, 1), (4, 3), (3, 2)])
        seq = col.intervals_sequential
        assert len(seq) == 2
        assert seq[0] == fractions.Fraction(4, 3)
        assert seq[1] == fractions.Fraction(9, 8)


# ── resultant tones ───────────────────────────────────────────────────────────

class TestResultantTones:
    def test_difference_tone_two_pitches(self):
        # 3/2 - 1 = 1/2
        col = make_pc([(1, 1), (3, 2)])
        assert len(col.difference_tones) == 1
        assert col.difference_tones[0] == fractions.Fraction(1, 2)

    def test_summation_tone_two_pitches(self):
        # 3/2 + 1 = 5/2
        col = make_pc([(1, 1), (3, 2)])
        assert len(col.summation_tones) == 1
        assert col.summation_tones[0] == fractions.Fraction(5, 2)

    def test_pc_plus_resultant_tones_is_superset(self):
        col = make_pc([(1, 1), (3, 2)])
        combined = col.pc_plus_resultant_tones
        for r in col.ratios:
            assert r in combined


# ── harmonic analysis ─────────────────────────────────────────────────────────

class TestHarmonicAnalysis:
    def test_harmonics_two_pitches(self):
        col = make_pc([(1, 1), (3, 2)])
        # denom LCM = 2 → harmonics [2, 3]
        assert sorted(col.harmonics) == [2, 3]

    def test_harmonics_three_pitches(self):
        col = make_pc([(1, 1), (4, 3), (3, 2)])
        # denom LCM = 6 → harmonics [6, 8, 9]
        assert sorted(col.harmonics) == [6, 8, 9]

    def test_periodicity_pitch_two_pitches(self):
        col = make_pc([(1, 1), (3, 2)])
        # min_freq = 440 Hz, min_harmonic = 2 → 220 Hz
        assert col.periodicity_pitch == pytest.approx(220.0)

    def test_harmonic_intersection_is_fraction(self):
        col = make_pc([(1, 1), (3, 2)])
        assert isinstance(col.harmonic_intersection, fractions.Fraction)

    def test_harmonic_intersection_two_pitches(self):
        # Inclusion–exclusion on harmonics [2, 3]:
        # 1/2 + 1/3 - 1/6 = 2/3
        col = make_pc([(1, 1), (3, 2)])
        assert col.harmonic_intersection == fractions.Fraction(2, 3)

    def test_harmonic_intersection_three_pitches(self):
        # Inclusion–exclusion on harmonics [6, 8, 9]:
        # (1/6+1/8+1/9) - (1/24+1/18+1/72) + 1/72 = 11/36
        col = make_pc([(1, 1), (4, 3), (3, 2)])
        assert col.harmonic_intersection == fractions.Fraction(11, 36)

    def test_disjunction_complements_intersection(self):
        col = make_pc([(1, 1), (3, 2)])
        assert col.harmonic_intersection + col.harmonic_disjunction == fractions.Fraction(1, 1)

    def test_constituent_primes(self):
        col = make_pc([(1, 1), (4, 3), (3, 2)])
        assert col.constituent_primes == [2, 3]

    def test_hd_sum(self):
        col = make_pc([(1, 1), (3, 2)])
        expected = 0.0 + math.log2(2) + math.log2(3)
        assert col.hd_sum == pytest.approx(expected)

    def test_hd_avg(self):
        col = make_pc([(1, 1), (3, 2)])
        assert col.hd_avg == pytest.approx(col.hd_sum / 2)

    def test_least_common_partial(self):
        col = make_pc([(1, 1), (3, 2)])
        # harmonics [2, 3] → LCM = 6
        assert col.least_common_partial == 6
        assert col.least_common_partial_freq == pytest.approx(6 * col.periodicity_pitch)


# ── inversion ─────────────────────────────────────────────────────────────────

class TestInversion:
    def test_inversion_length(self):
        col = make_pc([(1, 1), (4, 3), (3, 2)])
        assert len(col.inversion) == 3

    def test_inversion_three_pitches(self):
        # [1, 4/3, 3/2] inverts to [1, 9/8, 3/2]
        col = make_pc([(1, 1), (4, 3), (3, 2)])
        assert sorted(col.inversion) == [
            fractions.Fraction(1, 1),
            fractions.Fraction(9, 8),
            fractions.Fraction(3, 2),
        ]

    def test_inversion_is_sorted(self):
        col = make_pc([(1, 1), (4, 3), (3, 2)])
        for i in range(len(col.inversion) - 1):
            assert col.inversion[i] <= col.inversion[i + 1]


# ── quantitative stats ────────────────────────────────────────────────────────

class TestQuantitativeStats:
    def test_min_max_ratio(self):
        col = make_pc([(1, 1), (4, 3), (3, 2)])
        assert col.minimum_ratio == fractions.Fraction(1, 1)
        assert col.maximum_ratio == fractions.Fraction(3, 2)

    def test_ratio_span(self):
        col = make_pc([(1, 1), (3, 2)])
        assert col.ratio_span == fractions.Fraction(3, 2)

    def test_cents_span(self):
        col = make_pc([(1, 1), (3, 2)])
        assert col.cents_span == pytest.approx(col.keynum_span * 100)


# ── sorting ───────────────────────────────────────────────────────────────────

class TestSortBy:
    def test_sort_by_ratios_ascending(self):
        col = make_pc([(3, 2), (1, 1), (5, 4)])
        col.sort_by("ratios")
        for i in range(len(col.ratios) - 1):
            assert col.ratios[i] <= col.ratios[i + 1]

    def test_sort_by_harmonic_distances(self):
        col = make_pc([(1, 1), (7, 4), (3, 2)])
        col.sort_by("harmonic distances")
        for i in range(len(col.harmonic_distances) - 1):
            assert col.harmonic_distances[i] <= col.harmonic_distances[i + 1]

    def test_sort_invalid_key_raises(self):
        col = make_pc([(1, 1), (3, 2)])
        with pytest.raises(ValueError):
            col.sort_by("not a valid key")


# ── transpose ─────────────────────────────────────────────────────────────────

class TestTranspose:
    def test_transpose_multiplies_all_ratios(self):
        col = make_pc([(1, 1), (3, 2)])
        col.transpose((2, 1))
        assert fractions.Fraction(2, 1) in col.ratios
        assert fractions.Fraction(3, 1) in col.ratios

    def test_transpose_preserves_interval_content(self):
        col_ref = make_pc([(1, 1), (3, 2)])
        original_intervals = set(col_ref.intervals)
        col = make_pc([(1, 1), (3, 2)])
        col.transpose((5, 4))
        assert set(col.intervals) == original_intervals


# ── tuneable / non-tuneable classification ───────────────────────────────────

class TestTuneableClassification:
    def test_known_tuneable_intervals(self):
        # 4/3 and 3/2 are both in SABAT_SCHWEINITZ_TUNEABLE_INTERVALS
        col = make_pc([(1, 1), (4, 3), (3, 2)])
        assert fractions.Fraction(4, 3) in col.tuneable_intervals
        assert fractions.Fraction(3, 2) in col.tuneable_intervals

    def test_known_non_tuneable_interval(self):
        # 9/8 is not in SABAT_SCHWEINITZ_TUNEABLE_INTERVALS
        col = make_pc([(1, 1), (4, 3), (3, 2)])
        assert fractions.Fraction(9, 8) in col.non_tuneable_intervals

    def test_tuneable_and_non_tuneable_partition_intervals(self):
        col = make_pc([(1, 1), (4, 3), (3, 2)])
        all_intervals = set(col.intervals)
        tuneable = set(col.tuneable_intervals)
        non_tuneable = set(col.non_tuneable_intervals)
        assert tuneable | non_tuneable == all_intervals
        assert tuneable & non_tuneable == set()

    def test_resultant_tones_partitioned(self):
        # Every difference tone is either tuneable or non-tuneable, not both
        col = make_pc([(1, 1), (3, 2)])
        tuneable = set(col.tuneable_difference_tones)
        non_tuneable = set(col.non_tuneable_difference_tones)
        assert tuneable & non_tuneable == set()
        assert tuneable | non_tuneable == set(col.difference_tones)


# ── file I/O ──────────────────────────────────────────────────────────────────

class TestFileIO:
    def test_write_info_to_txt_creates_file(self, tmp_path):
        col = make_pc([(1, 1), (3, 2)])
        col.write_info_to_txt(output_path=str(tmp_path / "pitch_collection_info.txt"))
        assert (tmp_path / "pitch_collection_info.txt").exists()

    def test_write_info_to_txt_content(self, tmp_path):
        col = make_pc([(1, 1), (3, 2)])
        col.write_info_to_txt(output_path=str(tmp_path / "pitch_collection_info.txt"))
        content = (tmp_path / "pitch_collection_info.txt").read_text()
        assert "BASIC INFO" in content
        assert "3/2" in content

    def test_write_info_to_txt_custom_filename(self, tmp_path):
        col = make_pc([(1, 1), (3, 2)])
        col.write_info_to_txt(output_path=str(tmp_path / "custom.txt"))
        assert (tmp_path / "custom.txt").exists()

    def test_write_info_to_csv_creates_file(self, tmp_path):
        col = make_pc([(1, 1), (3, 2)])
        col.write_info_to_csv(output_path=str(tmp_path / "pitch_collection_info.csv"))
        assert (tmp_path / "pitch_collection_info.csv").exists()

    def test_write_info_to_csv_content(self, tmp_path):
        col = make_pc([(1, 1), (3, 2)])
        col.write_info_to_csv(output_path=str(tmp_path / "pitch_collection_info.csv"))
        content = (tmp_path / "pitch_collection_info.csv").read_text()
        assert "ratio" in content
        assert "3/2" in content

    def test_write_info_to_csv_custom_filename(self, tmp_path):
        col = make_pc([(1, 1), (3, 2)])
        col.write_info_to_csv(output_path=str(tmp_path / "custom.csv"))
        assert (tmp_path / "custom.csv").exists()

    def test_write_info_to_txt_tilde_expansion(self, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))
        make_pc([(1, 1), (3, 2)]).write_info_to_txt(output_path="~/pc.txt")
        assert (tmp_path / "pc.txt").exists()

    def test_write_info_to_csv_tilde_expansion(self, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))
        make_pc([(1, 1), (3, 2)]).write_info_to_csv(output_path="~/pc.csv")
        assert (tmp_path / "pc.csv").exists()


# ── large pitch sets ──────────────────────────────────────────────────────────

class TestLargePitchSet:
    def test_ten_pitch_set_initializes(self):
        # Author notes performance concerns above ~12 pitches; 10 should be fine
        ratios = [(n, 1) for n in range(1, 11)]
        col = make_pc(ratios)
        assert len(col.ratios) == 10

    def test_ten_pitch_set_harmonic_analysis(self):
        ratios = [(n, 1) for n in range(1, 11)]
        col = make_pc(ratios)
        assert isinstance(col.harmonic_intersection, fractions.Fraction)
        assert col.harmonic_intersection + col.harmonic_disjunction == fractions.Fraction(1, 1)

    def test_ten_pitch_set_intervals(self):
        ratios = [(n, 1) for n in range(1, 11)]
        col = make_pc(ratios)
        # n*(n-1)/2 unique intervals for n pitches (before dedup)
        assert len(col.intervals) > 0


# ── input validation ─────────────────────────────────────────────────────────

class TestValidation:
    def test_non_list_raises(self):
        with pytest.raises(TypeError):
            PitchCollection("not a list")

    def test_empty_list_raises(self):
        with pytest.raises(ValueError):
            PitchCollection([])

    def test_single_pitch_raises(self):
        with pytest.raises(ValueError):
            PitchCollection([(1, 1)])

    def test_bad_rf_raises(self):
        with pytest.raises(ValueError):
            PitchCollection([(1, 1), (3, 2)], rf=0)

    def test_bad_rp_raises(self):
        with pytest.raises(ValueError):
            PitchCollection([(1, 1), (3, 2)], rp="Z9")


# ── harmonic intersection cap and antichain ───────────────────────────────────

class TestHarmonicIntersectionCapAndAntichain:
    def test_large_collection_intersection_is_none(self):
        # 25 distinct primes → 25 coprime harmonics > cap of 24 → None
        primes = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]
        col = make_pc([(p, 1) for p in primes])
        assert col.harmonic_intersection is None

    def test_large_collection_disjunction_is_none(self):
        primes = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]
        col = make_pc([(p, 1) for p in primes])
        assert col.harmonic_disjunction is None

    def test_print_info_handles_none(self, capsys):
        # print_info("analytic") must not raise when intersection is None
        primes = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]
        col = make_pc([(p, 1) for p in primes])
        col.print_info("analytic")
        out = capsys.readouterr().out
        assert "N/A" in out

    def test_harmonic_series_antichain_reduces_to_one(self):
        # Harmonics [1,2,...,10]: every h divides all multiples, antichain = {1}
        # → inclusion-exclusion on [1] alone → intersection = 1/1
        col = make_pc([(k, 1) for k in range(1, 11)])
        assert col.harmonic_intersection == fractions.Fraction(1, 1)

    def test_intersection_below_cap_is_fraction(self):
        # A collection that stays within the cap should still return a Fraction
        col = make_pc([(1, 1), (5, 4), (3, 2), (7, 4)])
        assert isinstance(col.harmonic_intersection, fractions.Fraction)


# ── update ────────────────────────────────────────────────────────────────────

class TestUpdate:
    def test_update_replaces_pitches(self):
        col = make_pc([(1, 1), (3, 2)])
        col.update(pc=[(1, 1), (5, 4), (3, 2)])
        assert len(col.ratios) == 3
        assert fractions.Fraction(5, 4) in col.ratios

    def test_update_preserves_reference_when_omitted(self):
        col = make_pc([(1, 1), (3, 2)], rp="C4")
        col.update(pc=[(1, 1), (5, 4)])
        assert col.reference_pitch == "C4"
