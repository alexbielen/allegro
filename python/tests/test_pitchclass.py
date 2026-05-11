import random
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
        # Compare normal-order candidates after each is transposed to 0 (spec); major/minor
        # share one inverted form so both canonicalize to [0, 3, 7].
        assert PitchClassSet([0, 4, 7]).prime_form == [0, 3, 7]
        assert PitchClassSet([0, 3, 7]).prime_form == [0, 3, 7]
        assert PitchClassSet([0, 2, 10]).prime_form == [0, 2, 4]

    def test_prime_form_cluster_0_2_3(self):
        assert PitchClassSet([0, 2, 3]).prime_form == [0, 1, 3]

    def test_forte_num_matches_wikipedia_rahn_prime_column(self):
        # Major/minor triads share set class 3-11 (minor prime form [0,3,7] on Wikipedia).
        assert PitchClassSet([0, 4, 7]).forte_num == "3-11A"
        assert PitchClassSet([0, 3, 7]).forte_num == "3-11A"
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
        else:
            assert PitchClassSet(pitch_class_set).prime_form == m21_chord.primeForm 


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