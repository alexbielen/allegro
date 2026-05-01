import random
from typing import ClassVar

import pytest
from hypothesis import given
from hypothesis import strategies as st

from allegro.pitchclass import (
    PitchClassSet,
    invert,
    invert_ordered_set,
    transpose,
    transpose_ordered_set,
)


@st.composite
def pc_strategy(draw):
    return draw(st.integers(min_value=0, max_value=11))


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
        assert PitchClassSet([]).normal_form() == []

    def test_singleton_normal_form(self):
        assert PitchClassSet([5]).normal_form() == [5]

    def test_normal_form_spec_0_2_10(self):
        """Tightest span rotation ends with `{10,12,14}` mapped by `% 12`."""
        s = PitchClassSet([0, 2, 10])
        assert s.normal_form() == [10, 0, 2]

    def test_major_triad_normal_form(self):
        assert PitchClassSet([0, 4, 7]).normal_form() == [0, 4, 7]

    def test_minor_triad_normal_form(self):
        assert PitchClassSet([0, 3, 7]).normal_form() == [0, 3, 7]

    def test_diatonic_normal_form_matches_spec_rotation(self):
        s = PitchClassSet([0, 2, 4, 5, 7, 9, 11])
        assert s.normal_form() == [11, 0, 2, 4, 5, 7, 9]

    def test_duplicate_raises(self):
        with pytest.raises(ValueError, match="unique"):
            PitchClassSet([0, 0, 1])

    def test_out_of_range_raises(self):
        with pytest.raises(ValueError, match="0"):
            PitchClassSet([12])
