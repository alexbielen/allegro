from allegro.numbers import fit, FitMode
from hypothesis import given, strategies as st
import sys
import math


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


class TestFitWrapMode:

    def test_returns_original_value_when_inside_range(self):
        assert fit(FitMode.Wrap, 0, 10, 0) == 0
        assert fit(FitMode.Wrap, 0, 10, 1) == 1
        assert fit(FitMode.Wrap, 0, 10, 10) == 10
        assert fit(FitMode.Wrap, 2, 4, 3) == 3
        assert fit(FitMode.Wrap, -10, 0, -10) == -10
        assert fit(FitMode.Wrap, -10, 0, 0) == 0
        assert fit(FitMode.Wrap, -10, 0, -3) == -3
        assert fit(FitMode.Wrap, -100, -39, -44) == -44
        assert fit(FitMode.Wrap, -4, -2, -3) == -3

    def test_returns_wrapped_value_when_outside_range(self):
        assert fit(FitMode.Wrap, 0, 10, 12) == 2
        assert fit(FitMode.Wrap, 0, 10, 25) == 5
        assert fit(FitMode.Wrap, 0, 10, -4) == 6
        assert fit(FitMode.Wrap, 0, 10, -16) == 4
        assert fit(FitMode.Wrap, 0, 10, -53) == 7
        assert fit(FitMode.Wrap, 1, 5, 11) == 3

    @given(float_range_strategy())
    def test_that_the_result_is_always_within_the_range(
        self, tup: tuple[float, float, float]
    ):
        lb, ub, num = tup
        result = fit(FitMode.Wrap, lb, ub, num)
        assert lb <= result <= ub


class TestFitReflectMode:
    def test_returns_original_value_when_inside_range(self):
        assert fit(FitMode.Reflect, 0, 10, 0) == 0
        assert fit(FitMode.Reflect, 0, 10, 1) == 1
        assert fit(FitMode.Reflect, 0, 10, 10) == 10
        assert fit(FitMode.Reflect, 2, 4, 3) == 3

    def test_returns_reflected_value_when_outside_range(self):
        assert fit(FitMode.Reflect, 0, 10, 12) == 8
        assert fit(FitMode.Reflect, 0, 10, 23) == 3


def test_fit_reflect():
    assert fit(FitMode.Reflect, 0, 10, 12) == 8
    assert fit(FitMode.Reflect, 0, 10, 23) == 3
    assert fit(FitMode.Reflect, 0, 10, 33) == 7
    assert fit(FitMode.Reflect, 0, 10, -4) == 4
    assert fit(FitMode.Reflect, 0, 10, -23) == 3
    assert fit(FitMode.Reflect, 4, 9, 11) == 7
    assert fit(FitMode.Reflect, 4, 9, 1) == 7


def test_fit_bounce():
    assert fit(FitMode.Bounce, 0, 10, 12) == 8
    assert fit(FitMode.Bounce, 0, 10, 23) == 3
    assert fit(FitMode.Bounce, 0, 10, -12) == 2
    assert fit(FitMode.Bounce, 0, 10, -23) == 7
    assert fit(FitMode.Bounce, 4, 9, 11) == 5
    assert fit(FitMode.Bounce, 4, 9, -1) == 8


def test_fit_clamp():
    assert fit(FitMode.Clamp, 0, 10, 12) == 10
    assert fit(FitMode.Clamp, 0, 10, -4) == 0
