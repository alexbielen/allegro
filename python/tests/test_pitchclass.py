import random
from math import comb
from typing import ClassVar

import pytest
from hypothesis import given
from hypothesis import strategies as st

from music21 import chord

from allegro.pitchclass import (
    PitchClassSet,
    interval_class,
    invert,
    invert_ordered_set,
    satisfy_pc,
    transpose,
    transpose_ordered_set,
)


FORTE_RAHN_DISAGREEMENTS = [
            "5-20A",
            "5-20B",
            "5-32B",
            "6-29",
            "6-31A",
            "6-31B",
            "6-44B",
            "7-18A",
            "7-18B",
            "7-20A",
            "7-20B",
            "8-22B",
            "8-26",
            "8-27B",
            "9-7B",
            "9-8B",
            "9-11B",
        ]


@st.composite
def pc_strategy(draw):
    return draw(st.integers(min_value=0, max_value=11))


@st.composite
def pitch_class_set_strategy(draw):
    # no duplicates
    return draw(st.lists(pc_strategy(), min_size=0, max_size=12, unique=True))

@st.composite
def by_semitones_strategy(draw):
    return draw(st.integers(min_value=-11, max_value=11))


@st.composite
def below_range_strategy(draw):
    return draw(st.integers(min_value=-128, max_value=-12))


@st.composite
def above_range_strategy(draw):
    return draw(st.integers(min_value=12, max_value=127))


@st.composite
def ordered_set_strategy(draw):
    return draw(st.lists(pc_strategy(), min_size=0, max_size=12))


class TestTranspose:
    def test_returns_transposed_value(self):
        assert transpose(1, 0) == 1
        assert transpose(0, 11) == 11
        assert transpose(-1, 10) == 9
        assert transpose(-6, 11) == 5
        assert transpose(1, 3) == 4
        assert transpose(-11, 0) == 1

    @given(pc_strategy())
    def test_returns_original_value_when_inside_range(self, pc: int):
        assert transpose(0, pc) == pc

    # test that exceptions are raised when the input is outside the range
    @given(below_range_strategy())
    def test_raises_exception_when_outside_range(self, pc: int):
        with pytest.raises(ValueError):
            transpose(1, pc)


class TestInvert:
    @given(pc_strategy())
    def test_returns_inverted_value(self, pc: int):
        if pc == 0:
            assert invert(pc) == 0
        else:
            assert invert(pc) == 12 - pc

    # test that exceptions are raised when the input is outside the range
    @given(below_range_strategy())
    def test_raises_exception_when_below_range(self, pc: int):
        with pytest.raises(ValueError):
            invert(pc)

    @given(above_range_strategy())
    def test_raises_exception_when_above_range(self, pc: int):
        with pytest.raises(ValueError):
            invert(pc)


class TestTransposeOrderedSet:
    def test_returns_transposed_values(self):
        assert transpose_ordered_set(1, [0, 1, 4, 7]) == [1, 2, 5, 8]
        assert transpose_ordered_set(6, [0, 1, 5, 7]) == [6, 7, 11, 1]

    def test_that_empty_set_returns_empty_set(self):
        assert transpose_ordered_set(1, []) == []

    @given(
        st.integers(min_value=-11, max_value=11),
        st.lists(pc_strategy(), min_size=0, max_size=12),
    )
    def test_no_output_value_higher_than_11_or_lower_than_0(self, by_semitones: int, ordered_set: list[int]):
        result = transpose_ordered_set(by_semitones, ordered_set)
        assert all(0 <= pc <= 11 for pc in result)

    @given(
        st.integers(min_value=-11, max_value=11),
        st.lists(pc_strategy(), min_size=0, max_size=12),
    )
    def test_that_the_result_is_the_same_length_as_the_input_set(self, by_semitones: int, ordered_set: list[int]):
        result = transpose_ordered_set(by_semitones, ordered_set)
        assert len(result) == len(ordered_set)

    # test that errors are raised when the input is outside the range
    @given(st.integers(min_value=-24, max_value=-12))
    def test_raises_exception_when_by_semitones_is_outside_range(self, by_semitones: int):
        with pytest.raises(ValueError):
            transpose_ordered_set(by_semitones, [0, 1, 4, 7])

    @given(st.lists(st.integers(min_value=-12, max_value=-1), min_size=1, max_size=12))
    def test_raises_exception_when_ordered_set_contains_values_outside_range(self, ordered_set: list[int]):
        with pytest.raises(ValueError):
            transpose_ordered_set(1, ordered_set)


class TestInvertOrderedSet:
    def test_returns_inverted_values(self):
        assert invert_ordered_set([0, 1, 4, 7]) == [0, 11, 8, 5]
        assert invert_ordered_set([0, 1, 5, 10]) == [0, 11, 7, 2]

    def test_that_empty_set_returns_empty_set(self):
        assert invert_ordered_set([]) == []

    @given(ordered_set_strategy())
    def test_no_output_value_higher_than_11_or_lower_than_0(self, ordered_set: list[int]):
        result = invert_ordered_set(ordered_set)
        assert all(0 <= pc <= 11 for pc in result)

    @given(ordered_set_strategy())
    def test_that_the_result_is_the_same_length_as_the_input_set(self, ordered_set: list[int]):
        result = invert_ordered_set(ordered_set)
        assert len(result) == len(ordered_set)


class TestOrderedSetBenchmarks:
    """Benchmarks for ordered_set functions. Run with: pytest --benchmark-only tests/test_pitchclass.py -k Benchmark"""

    ORDERED_SET: ClassVar[list[int]] = [random.randint(0, 11) for _ in range(10_000)]

    def test_benchmark_transpose_ordered_set(self, benchmark):
        by_semitones = 3
        # warm up
        transpose_ordered_set(by_semitones, self.ORDERED_SET)
        benchmark(transpose_ordered_set, by_semitones, self.ORDERED_SET)

    def test_benchmark_invert_ordered_set(self, benchmark):
        ordered_set = self.ORDERED_SET

        # warm up
        invert_ordered_set(ordered_set)
        benchmark(invert_ordered_set, ordered_set)

    def test_benchmark_transpose_ordered_set_in_python_performance(self, benchmark):
        by_semitones = 3

        def f(by_semitones, ordered_set):
            return [transpose(by_semitones, pc) for pc in ordered_set]

        benchmark(f, by_semitones, self.ORDERED_SET)

    def test_benchmark_transpose_ordered_set_in_pure_python_performance(self, benchmark):
        by_semitones = 3

        def py_transpose(by_semitones, pc):
            return (by_semitones + pc) % 12

        def f(by_semitones, ordered_set):
            return [py_transpose(by_semitones, pc) for pc in ordered_set]

        benchmark(f, by_semitones, self.ORDERED_SET)

    def test_benchmark_invert_ordered_set_in_python_performance(self, benchmark):

        def f(ordered_set):
            return [invert(pc) for pc in ordered_set]

        benchmark(f, self.ORDERED_SET)


class TestPitchClassSet:
    """Normal form follows `src/specs/pitchclass.md` (rotation + `% 12`)."""

    def test_pitch_classes_empty_and_order(self):
        assert PitchClassSet([]).pitch_classes == []
        assert PitchClassSet([7, 0, 11]).pitch_classes == [7, 0, 11]

    def test_pitch_classes_returns_independent_copy(self):
        s = PitchClassSet([0, 4, 7])
        pcs = s.pitch_classes
        pcs.append(99)
        assert s.pitch_classes == [0, 4, 7]

    def test_transpose_by_identity(self):
        s = PitchClassSet([0, 4, 7])
        t = s.transpose_by(0)
        assert t.pitch_classes == [0, 4, 7]
        assert s.pitch_classes == [0, 4, 7]

    def test_transpose_by_wraps_mod_twelve(self):
        s = PitchClassSet([10, 11, 0])
        assert s.transpose_by(3).pitch_classes == [1, 2, 3]
        assert s.transpose_by(-2).pitch_classes == [8, 9, 10]

    def test_transpose_by_does_not_mutate_original(self):
        s = PitchClassSet([1, 5, 9])
        _ = s.transpose_by(4)
        assert s.pitch_classes == [1, 5, 9]

    def test_transpose_by_out_of_range_raises(self):
        s = PitchClassSet([0])
        with pytest.raises(ValueError, match="by_semitones"):
            s.transpose_by(-12)
        with pytest.raises(ValueError, match="by_semitones"):
            s.transpose_by(12)

    @given(pitch_class_set_strategy(), by_semitones_strategy())
    def test_transpose_by_matches_elementwise_transpose(self, pcs_list, tn):
        s = PitchClassSet(pcs_list)
        assert s.transpose_by(tn).pitch_classes == [
            transpose(tn, pc) for pc in s.pitch_classes
        ]

    def test_empty_set_normal_form(self):
        assert PitchClassSet([]).normal_form == []

    def test_singleton_normal_form(self):
        assert PitchClassSet([5]).normal_form == [5]

    def test_normal_form_spec_0_2_10(self):
        """Tightest span rotation ends with `{10,12,14}` mapped by `% 12`."""
        s = PitchClassSet([0, 2, 10])
        assert s.normal_form == [10, 0, 2]

    def test_major_triad_normal_form(self):
        assert PitchClassSet([0, 4, 7]).normal_form == [0, 4, 7]

    def test_minor_triad_normal_form(self):
        assert PitchClassSet([0, 3, 7]).normal_form == [0, 3, 7]

    def test_diatonic_normal_form_matches_spec_rotation(self):
        s = PitchClassSet([0, 2, 4, 5, 7, 9, 11])
        assert s.normal_form == [11, 0, 2, 4, 5, 7, 9]

    def test_prime_form_triads_and_transpose(self):
        # Normal form T0 preserves orientation; major/minor get distinct prime forms.
        assert PitchClassSet([0, 4, 7]).prime_form == [0, 4, 7]
        assert PitchClassSet([0, 3, 7]).prime_form == [0, 3, 7]
        # A transposed major triad such as [4, 8, 11] also reduces to [0, 4, 7].
        assert PitchClassSet([4, 8, 11]).prime_form == [0, 4, 7]
        assert PitchClassSet([0, 2, 10]).prime_form == [0, 2, 4]

    def test_prime_form_cluster_0_2_3(self):
        # Cluster [0,2,3] is 3-2B in the Wikipedia listing, with oriented prime form [0,2,3].
        assert PitchClassSet([0, 2, 3]).prime_form == [0, 2, 3]

    def test_forte_num_matches_wikipedia_rahn_prime_column(self):
        # Major/minor triads share set class 3-11 but have distinct A/B prime forms.
        assert PitchClassSet([0, 3, 7]).forte_num == "3-11A"
        assert PitchClassSet([0, 4, 7]).forte_num == "3-11B"
        assert PitchClassSet([4, 8, 11]).forte_num == "3-11B"
        assert PitchClassSet([0, 1, 2, 3, 4, 5]).forte_num == "6-1"

    def test_forte_num_edge_cardinalities(self):
        assert PitchClassSet([]).forte_num == "0-1"
        assert PitchClassSet([9]).forte_num == "1-1"
        assert PitchClassSet(list(range(12))).forte_num == "12-1"

    def test_interval_class_vector_empty_and_singleton(self):
        assert PitchClassSet([]).interval_vector == [0, 0, 0, 0, 0, 0]
        assert PitchClassSet([3]).interval_vector == [0, 0, 0, 0, 0, 0]

    def test_interval_class_vector_tetrachord_0123(self):
        # 4-1 chromatic: six pairs with ic1×3, ic2×2, ic3×1
        assert PitchClassSet([0, 1, 2, 3]).interval_vector == [3, 2, 1, 0, 0, 0]

    def test_interval_class_vector_triad(self):
        # <001110> in order ic1..ic6
        assert PitchClassSet([0, 4, 7]).interval_vector == [0, 0, 1, 1, 1, 0]

    def test_interval_class_vector_includes_complement_intervals(self):
        # 0 and 11 -> directed 11 -> ic1
        assert PitchClassSet([0, 11]).interval_vector == [1, 0, 0, 0, 0, 0]

    def test_count_common_tones_under_tn_identity(self):
        assert PitchClassSet([]).count_common_tones_under_tn(0) == 0
        assert PitchClassSet([5]).count_common_tones_under_tn(0) == 1
        assert PitchClassSet([0, 4, 7]).count_common_tones_under_tn(0) == 3
        assert PitchClassSet([0, 4, 7]).count_common_tones_under_tn(12) == 3

    def test_count_common_tones_under_tn_set_class_027(self):
        # (027): one ic2 pair, two ic5 pairs — Open Music Theory common-tones examples
        s = PitchClassSet([0, 2, 7])
        assert s.interval_vector == [0, 1, 0, 0, 2, 0]
        assert s.count_common_tones_under_tn(2) == 1
        assert s.count_common_tones_under_tn(10) == 1
        assert s.count_common_tones_under_tn(5) == 2
        assert s.count_common_tones_under_tn(7) == 2
        assert s.count_common_tones_under_tn(1) == 0

    def test_count_common_tones_under_tn_tritone_doubling(self):
        # ic6 count 1 → T6 retains twice that many common tones (cf. (016) in Open Music Theory)
        s = PitchClassSet([0, 1, 6])
        iv = s.interval_vector
        assert iv == [1, 0, 0, 0, 1, 1]
        assert s.count_common_tones_under_tn(6) == 2 * iv[5]
        assert s.count_common_tones_under_tn(6) == 2
        assert s.count_common_tones_under_tn(1) == iv[0]

    def test_duplicate_raises(self):
        with pytest.raises(ValueError, match="unique"):
            PitchClassSet([0, 0, 1])

    def test_out_of_range_raises(self):
        with pytest.raises(ValueError, match="0"):
            PitchClassSet([12])


class TestPitchClassSetSubsets:
    """Tests for `PitchClassSet.subsets()` (powerset of the pitch-class set)."""

    def test_empty_set_has_one_subset(self):
        result = PitchClassSet([]).subsets()
        assert len(result) == 1
        assert result[0].pitch_classes == []

    def test_empty_set_min_size_positive_returns_empty(self):
        assert PitchClassSet([]).subsets(1) == []
        assert PitchClassSet([]).subsets(3) == []

    def test_singleton_has_empty_and_self(self):
        result = PitchClassSet([5]).subsets()
        as_tuples = {tuple(s.pitch_classes) for s in result}
        assert as_tuples == {(), (5,)}

    def test_pair_has_four_subsets(self):
        result = PitchClassSet([0, 7]).subsets()
        as_tuples = {tuple(s.pitch_classes) for s in result}
        assert as_tuples == {(), (0,), (7,), (0, 7)}

    def test_triad_returns_all_eight_subsets(self):
        # Powerset of [0, 4, 7]. Order within each subset matches input order
        # (the implementation iterates indices 0..n with a bitmask).
        result = PitchClassSet([0, 4, 7]).subsets()
        as_tuples = {tuple(s.pitch_classes) for s in result}
        assert as_tuples == {
            (),
            (0,),
            (4,),
            (7,),
            (0, 4),
            (0, 7),
            (4, 7),
            (0, 4, 7),
        }

    def test_min_size_three_triad_only_full_set(self):
        subs = PitchClassSet([0, 4, 7]).subsets(min_size=3)
        assert len(subs) == 1
        assert subs[0].pitch_classes == [0, 4, 7]

    def test_min_size_two_on_triad(self):
        as_tuples = {tuple(s.pitch_classes) for s in PitchClassSet([0, 4, 7]).subsets(2)}
        assert as_tuples == {(0, 4), (0, 7), (4, 7), (0, 4, 7)}

    def test_min_size_one_on_triad_excludes_empty(self):
        as_tuples = {tuple(s.pitch_classes) for s in PitchClassSet([0, 4, 7]).subsets(1)}
        assert () not in as_tuples
        assert len(as_tuples) == 7

    def test_min_size_exceeds_len_returns_empty(self):
        assert PitchClassSet([0, 1]).subsets(3) == []

    def test_min_size_zero_same_as_omitted(self):
        s = PitchClassSet([0, 7])
        assert {tuple(x.pitch_classes) for x in s.subsets()} == {
            tuple(x.pitch_classes) for x in s.subsets(0)
        }

    def test_negative_min_size_raises_overflow_error(self):
        # PyO3 maps min_size to Rust usize; negative Python ints fail at conversion.
        s = PitchClassSet([0, 7])
        with pytest.raises(OverflowError, match="negative int"):
            s.subsets(-1)

    def test_returns_pitch_class_set_instances(self):
        result = PitchClassSet([0, 1, 2]).subsets()
        assert all(isinstance(s, PitchClassSet) for s in result)

    def test_full_chromatic_returns_4096_subsets(self):
        # 2**12 = 4096; checks the largest valid input doesn't overflow or trim.
        result = PitchClassSet(list(range(12))).subsets()
        assert len(result) == 4096

    @given(pitch_class_set_strategy())
    def test_subset_count_is_power_of_two(self, pcs_list: list[int]):
        s = PitchClassSet(pcs_list)
        assert len(s.subsets()) == 2 ** len(pcs_list)

    @given(pitch_class_set_strategy())
    def test_each_subset_is_contained_in_original(self, pcs_list: list[int]):
        s = PitchClassSet(pcs_list)
        original = set(pcs_list)
        for sub in s.subsets():
            assert set(sub.pitch_classes).issubset(original)

    @given(pitch_class_set_strategy())
    def test_all_subsets_are_unique(self, pcs_list: list[int]):
        s = PitchClassSet(pcs_list)
        as_tuples = [tuple(sub.pitch_classes) for sub in s.subsets()]
        assert len(set(as_tuples)) == len(as_tuples)

    @given(pitch_class_set_strategy())
    def test_empty_and_full_subsets_are_always_present(self, pcs_list: list[int]):
        s = PitchClassSet(pcs_list)
        as_tuples = {tuple(sub.pitch_classes) for sub in s.subsets()}
        assert () in as_tuples
        assert tuple(pcs_list) in as_tuples

    @given(pitch_class_set_strategy(), st.integers(min_value=0, max_value=12))
    def test_min_size_each_result_has_at_least_k_members(self, pcs_list: list[int], min_size: int):
        for sub in PitchClassSet(pcs_list).subsets(min_size):
            assert len(sub.pitch_classes) >= min_size

    @given(pitch_class_set_strategy(), st.integers(min_value=0, max_value=12))
    def test_min_size_count_matches_binomial_tail(self, pcs_list: list[int], min_size: int):
        n = len(pcs_list)
        expected = sum(comb(n, k) for k in range(min_size, n + 1))
        assert len(PitchClassSet(pcs_list).subsets(min_size)) == expected


class TestIntervalClass:
    def test_unison_and_octave_equivalence(self):
        assert interval_class(0) == 0
        assert interval_class(12) == 0

    def test_mod_twelve(self):
        assert interval_class(13) == interval_class(1) == 1
        assert interval_class(-1) == interval_class(11) == 1

    def test_tritone(self):
        assert interval_class(6) == 6


class TestPitchClassSetIntervalVectorConsistencyWithMusic21:
    @given(pitch_class_set_strategy())
    def test_matches_music21(self, pitch_class_set: list[int]):
        m21_chord = chord.Chord(pitch_class_set)
        assert PitchClassSet(pitch_class_set).interval_vector == list(m21_chord.intervalVector)


class TestPitchClassSetNormalFormConsistencyWithMusic21:
    @given(pitch_class_set_strategy())
    def test_consistency_with_music21(self, pitch_class_set: list[int]):

        m21_chord = chord.Chord(pitch_class_set)

        if pitch_class_set and m21_chord.forteClass in FORTE_RAHN_DISAGREEMENTS:
            print(f"Forte Rahn disagreement: {m21_chord.forteClass} for {pitch_class_set}")
        else:
            assert PitchClassSet(pitch_class_set).normal_form == m21_chord.normalOrder 


class TestPitchClassSetPrimeFormConsistencyWithMusic21:
    @given(pitch_class_set_strategy())
    def test_consistency_with_music21(self, pitch_class_set: list[int]):

        m21_chord = chord.Chord(pitch_class_set)

        if pitch_class_set and m21_chord.forteClass in FORTE_RAHN_DISAGREEMENTS:
            print(f"Forte Rahn disagreement: {m21_chord.forteClass} for {pitch_class_set}")
            return

        # music21's primeForm follows Rahn's lexicographically minimal convention,
        # which collapses some asymmetrical A/B pairs (e.g. major/minor triads)
        # to a single representative. Our implementation preserves oriented
        # normal form T0, matching the Wikipedia/Forte A/B columns instead.
        # Skip sets whose inversion has a different oriented normal form.
        pcs = PitchClassSet(pitch_class_set)
        prime = pcs.prime_form
        inv_prime = PitchClassSet([invert(pc) for pc in pitch_class_set]).prime_form
        if prime != inv_prime:
            return

        assert prime == m21_chord.primeForm


class TestPitchClassSetNormalFormBenchmark:
    """Benchmarks for normal form functions. Run with: pytest --benchmark-only tests/test_pitchclass.py -k Benchmark"""


    def test_benchmark_normal_form(self, benchmark):

        pcs = pitch_class_set_strategy().example()


        s = PitchClassSet(pcs)
        # warm up
        _ = s.normal_form
        benchmark(lambda: s.normal_form)

    def test_benchmark_normal_order_music21(self, benchmark):
        pcs = pitch_class_set_strategy().example()

        def f(pcs):
            return chord.Chord(pcs).normalOrder

        # warm up
        f(pcs)
        benchmark(f, pcs)


class TestSatisfyPc:
    def test_examples_trichord_and_tetrachord(self):
        assert satisfy_pc("3-11B", [4, 8]) == [[11]]
        assert satisfy_pc("4-20", [0, 8]) == [[1, 5], [3, 7]]

    def test_empty_partial_returns_all_transpositions(self):
        # 3-11B has prime form [0, 4, 7]; all 12 transpositions are valid.
        results = satisfy_pc("3-11B", [])
        assert len(results) == 12
        for missing in results:
            assert len(missing) == 3
            pcs = PitchClassSet(missing)
            assert pcs.forte_num == "3-11B"

    def test_round_trip_completions_match_forte(self):
        partial = [4, 8]
        forte = "3-11B"
        for missing in satisfy_pc(forte, partial):
            pcs = PitchClassSet(sorted(set(partial + missing)))
            assert pcs.forte_num == forte

    def test_unknown_forte_raises(self):
        with pytest.raises(ValueError):
            satisfy_pc("not-a-forte", [0])

    def test_duplicate_partial_raises(self):
        with pytest.raises(ValueError, match="unique"):
            satisfy_pc("3-11B", [4, 4])

    def test_out_of_range_partial_raises(self):
        with pytest.raises(ValueError):
            satisfy_pc("3-11B", [12])

    def test_impossible_partial_returns_empty(self):
        assert satisfy_pc("3-11B", [0, 1]) == []

    def test_already_complete_returns_empty(self):
        assert satisfy_pc("3-11B", [4, 8, 11]) == []