from allegro.pitchclass import transpose, invert
from hypothesis import given, strategies as st

import pytest


@st.composite
def pc_strategy(draw):
    return draw(st.integers(min_value=0, max_value=11))


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
    @given(st.integers(min_value=-12, max_value=-1))
    def test_raises_exception_when_outside_range(self, pc: int):
        with pytest.raises(ValueError):
            transpose(1, pc)


class TestInvert:
    def test_returns_inverted_value(self):
        assert invert(11) == 1
        assert invert(10) == 2
        assert invert(9) == 3
        assert invert(8) == 4
        assert invert(7) == 5
        assert invert(6) == 6
        assert invert(5) == 7
        assert invert(4) == 8
        assert invert(3) == 9
        assert invert(2) == 10
        assert invert(1) == 11
        assert invert(0) == 0

    # test that exceptions are raised when the input is outside the range
    @given(st.integers(min_value=-12, max_value=-1))
    def test_raises_exception_when_below_range(self, pc: int):
        with pytest.raises(ValueError):
            invert(pc)

    @given(st.integers(min_value=12, max_value=23))
    def test_raises_exception_when_above_range(self, pc: int):
        with pytest.raises(ValueError):
            invert(pc)
