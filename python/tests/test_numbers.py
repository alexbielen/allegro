from allegro.numbers import fit, fit_list, FitMode, quantize
from hypothesis import assume, given, strategies as st


import math
import pytest
import random
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


@st.composite
def float_list_strategy(draw):
    lb, ub, _ = draw(float_range_strategy())
    nums = draw(
        st.lists(
            st.floats(
                min_value=MIN_FINITE,
                max_value=MAX_FINITE,
                allow_nan=False,
                allow_infinity=False,
                width=64,
            ),
            min_size=1000,
            max_size=1000,
        )
    )

    return lb, ub, nums


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


class TestFitList:
    def test_fit_list(self):
        assert fit_list(FitMode.Wrap, 0, 10, [12, 23, -12, -23]) == [2, 3, 8, 7]
        assert fit_list(FitMode.Reflect, 0, 10, [12, 23, -12, -23]) == [8, 3, 8, 3]
        assert fit_list(FitMode.Bounce, 0, 10, [12, 23, -12, -23]) == [8, 3, 2, 7]
        assert fit_list(FitMode.Clamp, 0, 10, [12, 23, -12, -23]) == [10, 10, 0, 0]

    def test_fit_list_empty(self):
        assert fit_list(FitMode.Wrap, 0, 10, []) == []
        assert fit_list(FitMode.Reflect, 0, 10, []) == []
        assert fit_list(FitMode.Bounce, 0, 10, []) == []
        assert fit_list(FitMode.Clamp, 0, 10, []) == []


class TestFitListPerformance:
    def run_fit_list_benchmark(
        self, benchmark, mode: FitMode, python_version: bool
    ) -> None:
        """Benchmark fit_list vs a pure-Python loop for a given mode."""
        lb, ub, _ = float_range_strategy().example()
        nums = [random.random() for _ in range(10000)]

        if python_version:

            def f(lb: float, ub: float, nums: list[float]) -> list[float]:
                return [fit(mode, lb, ub, num) for num in nums]

            # warm up
            f(lb, ub, nums)
            benchmark(f, lb, ub, nums)
        else:
            # warm up
            fit_list(mode, lb, ub, nums)
            benchmark(fit_list, mode, lb, ub, nums)

    def test_benchmark_fit_list_wrap_mode(self, benchmark):
        self.run_fit_list_benchmark(benchmark, FitMode.Wrap, python_version=False)

    def test_benchmark_fit_list_wrap_mode_in_python_performance(self, benchmark):
        self.run_fit_list_benchmark(benchmark, FitMode.Wrap, python_version=True)

    def test_benchmark_fit_list_reflect_mode(self, benchmark):
        self.run_fit_list_benchmark(benchmark, FitMode.Reflect, python_version=False)

    def test_benchmark_fit_list_reflect_mode_in_python_performance(self, benchmark):
        self.run_fit_list_benchmark(benchmark, FitMode.Reflect, python_version=True)

    def test_benchmark_fit_list_bounce_mode(self, benchmark):
        self.run_fit_list_benchmark(benchmark, FitMode.Bounce, python_version=False)

    def test_benchmark_fit_list_bounce_mode_in_python_performance(self, benchmark):
        self.run_fit_list_benchmark(benchmark, FitMode.Bounce, python_version=True)

    def test_benchmark_fit_list_clamp_mode(self, benchmark):
        self.run_fit_list_benchmark(benchmark, FitMode.Clamp, python_version=False)

    def test_benchmark_fit_list_clamp_mode_in_python_performance(self, benchmark):
        self.run_fit_list_benchmark(benchmark, FitMode.Clamp, python_version=True)


# --- quantize ---

finite_floats = st.floats(
    min_value=MIN_FINITE,
    max_value=MAX_FINITE,
    allow_nan=False,
    allow_infinity=False,
    width=64,
)

positive_finite = st.floats(
    min_value=2**-1074,  # subnormal ok, but not 0
    max_value=MAX_FINITE,
    allow_nan=False,
    allow_infinity=False,
    width=64,
)


def is_safe_quantize_pair(step: float, value: float) -> bool:
    """Mirror the Rust-side overflow guards for quantize."""
    if not math.isfinite(step) or step == 0.0:
        return False
    if not math.isfinite(value):
        return False

    max_f64 = sys.float_info.max
    abs_step = abs(step)
    abs_value = abs(value)

    # Division safe: for |step| < 1, require |value| <= max_f64 * |step|.
    # For |step| >= 1, division cannot overflow.
    if abs_step < 1.0 and abs_value > max_f64 * abs_step:
        return False

    # Multiplication safe: enforce |value| + 0.5 * |step| <= max_f64. Use
    # (max_f64 - abs_value) >= 0.5*step so we don't rely on max_f64 - 0.5*step
    # (which can round to max_f64 when near the limit).
    if (max_f64 - abs_value) < 0.5 * abs_step:
        return False

    return True


class TestQuantize:
    """Tests for quantize(step, value)."""

    def test_docstring_examples(self):
        assert quantize(1.0, 2.7) == 3.0
        assert quantize(1.0, 2.4) == 2.0
        assert quantize(1.0, 2.5) == 3.0
        assert quantize(0.5, -1.3) == -1.5
        assert math.isclose(quantize(0.3, 1.0), 0.9)

    def test_exact_steps_unchanged(self):
        assert quantize(1.0, 3.0) == 3.0
        assert quantize(0.5, 2.0) == 2.0
        assert quantize(0.25, -1.0) == -1.0

    def test_round_half_away_from_zero(self):
        assert quantize(1.0, 2.5) == 3.0
        assert quantize(1.0, -2.5) == -3.0

    @given(step=positive_finite, value=finite_floats)
    def test_result_is_multiple_of_step(self, step: float, value: float):
        assume(is_safe_quantize_pair(step, value))
        result = quantize(step, value)
        approx_multiple = round(value / step)
        assert math.isclose(result, approx_multiple * step)

    @given(step=positive_finite, value=finite_floats)
    def test_result_is_finite(self, step: float, value: float):
        assume(is_safe_quantize_pair(step, value))
        result = quantize(step, value)
        assert math.isfinite(result)

    def test_step_zero_raises(self):
        with pytest.raises(ValueError, match="finite and non-zero"):
            quantize(0.0, 1.0)

    def test_step_nan_raises(self):
        with pytest.raises(ValueError, match="finite and non-zero"):
            quantize(math.nan, 1.0)

    def test_step_inf_raises(self):
        with pytest.raises(ValueError, match="finite and non-zero"):
            quantize(math.inf, 1.0)

    def test_value_nan_raises(self):
        with pytest.raises(ValueError, match="value must be finite"):
            quantize(1.0, math.nan)

    def test_value_inf_raises(self):
        with pytest.raises(ValueError, match="value must be finite"):
            quantize(1.0, math.inf)

    def test_negative_step_allowed(self):
        # round(value/step)*step with step < 0 still gives a valid multiple
        assert quantize(-1.0, 2.7) == 3.0
        assert quantize(-0.5, -1.3) == -1.5

    def test_overflow_division_raises(self):
        # value/step overflows when step is tiny and value is large
        with pytest.raises(
            ValueError,
            match="outside the supported range",
        ):
            quantize(1e-308, 1e308)
