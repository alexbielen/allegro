from allegro.numbers import fit, FitMode
from hypothesis import given, strategies as st

import math
import pytest
import sys


MIN_FINITE = -sys.float_info.max

# because we will potentially bump ub in the
# nextafter call below, we need to be sure that
# MAX_FINITE is one representable float below the actual max
towards_zero = 0.0
MAX_FINITE = math.nextafter(sys.float_info.max, towards_zero)


@st.composite
def float_range_strategy(draw):
    a = draw(
        st.floats(
            min_value=MIN_FINITE,
            max_value=MAX_FINITE,
            allow_nan=False,
            allow_infinity=False,
            width=64,
        )
    )
    b = draw(
        st.floats(
            min_value=MIN_FINITE,
            max_value=MAX_FINITE,
            allow_nan=False,
            allow_infinity=False,
            width=64,
        )
    )

    lb, ub = (a, b) if a < b else (b, a)

    # If equal, force a strictly larger ub (still finite due to MAX_FINITE cap above)
    if lb == ub:
        ub = math.nextafter(lb, math.inf)

    num = draw(
        st.floats(
            min_value=MIN_FINITE,
            max_value=MAX_FINITE,
            allow_nan=False,
            allow_infinity=False,
            width=64,
        )
    )

    return lb, ub, num


class TestFit:
    ALL_MODES = [FitMode.Wrap, FitMode.Reflect, FitMode.Bounce, FitMode.Clamp]

    @pytest.mark.parametrize("mode", ALL_MODES)
    @given(float_range_strategy())
    def test_that_the_result_is_always_within_the_range(
        self, mode: FitMode, tup: tuple[float, float, float]
    ):
        lb, ub, num = tup
        result = fit(mode, lb, ub, num)
        assert lb <= result <= ub

    @pytest.mark.parametrize("mode", ALL_MODES)
    @given(float_range_strategy())
    def test_returns_original_value_when_inside_range(
        self, mode: FitMode, tup: tuple[float, float, float]
    ):
        sorted_values = sorted(tup)
        lb, num, ub = sorted_values
        result = fit(mode, lb, ub, num)
        assert result == num

    @pytest.mark.parametrize("mode", ALL_MODES)
    @given(float_range_strategy())
    def test_that_the_result_is_never_nan_or_infinity(
        self, mode: FitMode, tup: tuple[float, float, float]
    ):
        result = fit(mode, *tup)
        assert not math.isnan(result)
        assert not math.isinf(result)


class TestFitWrapMode:
    def test_returns_wrapped_value_when_outside_range(self):
        assert fit(FitMode.Wrap, 0, 10, 12) == 2
        assert fit(FitMode.Wrap, 0, 10, 25) == 5
        assert fit(FitMode.Wrap, 0, 10, -4) == 6
        assert fit(FitMode.Wrap, 0, 10, -16) == 4
        assert fit(FitMode.Wrap, 0, 10, -53) == 7
        assert fit(FitMode.Wrap, 1, 5, 11) == 3


class TestFitReflectMode:
    def test_returns_reflected_value_when_outside_range(self):
        assert fit(FitMode.Reflect, 0, 10, 12) == 8
        assert fit(FitMode.Reflect, 0, 10, 23) == 3
        assert fit(FitMode.Reflect, 0, 10, 33) == 7
        assert fit(FitMode.Reflect, 0, 10, -4) == 4
        assert fit(FitMode.Reflect, 0, 10, -23) == 3
        assert fit(FitMode.Reflect, 4, 9, 11) == 7
        assert fit(FitMode.Reflect, 4, 9, 1) == 7


class TestFitBounceMode:
    def test_returns_bounced_value_when_outside_range(self):
        assert fit(FitMode.Bounce, 0, 10, 12) == 8
        assert fit(FitMode.Bounce, 0, 10, 23) == 3
        assert fit(FitMode.Bounce, 0, 10, -12) == 2
        assert fit(FitMode.Bounce, 0, 10, -23) == 7
        assert fit(FitMode.Bounce, 4, 9, 11) == 5
        assert fit(FitMode.Bounce, 4, 9, -1) == 8


class TestFitClampMode:

    @given(float_range_strategy())
    def test_fit_clamp(self, tup: tuple[float, float, float]):
        lb, ub, num = tup
        result = fit(FitMode.Clamp, lb, ub, num)
        if num > ub:
            assert result == ub
        elif num < lb:
            assert result == lb
        else:
            assert lb <= result <= ub
