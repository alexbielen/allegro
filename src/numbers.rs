use pyo3::prelude::*;

use crate::py_stub::{gen_stub_pyclass_enum, gen_stub_pyfunction};

#[gen_stub_pyclass_enum]
#[pyclass]
#[derive(Clone, Copy, PartialEq)]
/// Strategy for fitting a number into a closed interval ``[min, max]``.
///
/// ``FitMode`` controls how values *outside* the interval are mapped back into it.
/// If a value is already within ``[min, max]``, it is returned unchanged.
///
/// Modes:
///     Wrap:
///         Treat the interval as a repeating cycle (periodic modulo behavior).
///         Values above ``max`` wrap around to ``min``; values below ``min`` wrap
///         around from the top.
///
///     Reflect:
///         Mirror values back into the interval by reflecting them off the nearest
///         boundary (coordinate-based reflection).
///
///     Bounce:
///         Interpret the value as "travel energy" across the interval.
///         ``num >= 0`` starts at ``min`` moving right; ``num < 0`` starts at ``max``
///         moving left; the value bounces off the boundaries until the energy is spent.
///
///     Clamp:
///         Pin values outside the interval to the nearest boundary.
///
/// Examples:
///     Using the interval ``[0, 10]``:
///
///     - ``Wrap``: ``15 -> 5``, ``25 -> 5``, ``-3 -> 7``
///     - ``Reflect``: ``12 -> 8``, ``23 -> 3``, ``-23 -> 7``
///     - ``Bounce``: ``12 -> 8``, ``23 -> 3``, ``-12 -> 2``, ``-23 -> 7``
///     - ``Clamp``: ``15 -> 10``, ``-3 -> 0``
///
/// Notes:
///     The public ``fit`` function also handles edge cases (non-finite values and
///     extremely large spans) by returning a safe in-range value.
pub enum FitMode {
    /// **Wrap** — Treat the range as a repeating cycle. Values above the upper bound
    /// wrap to the lower side, and values below the lower bound wrap to the upper side.
    ///
    /// Example with range [0, 10]: 15 → 5, 25 → 5, -3 → 7.
    #[pyo3(name = "Wrap")]
    Wrap,

    /// **Reflect** — Values outside the range are reflected back into the interval at
    /// the boundaries, as if mirrored in the walls of the range, instead of wrapping.
    ///
    /// Example with range [0, 10]: 12 → 8, 23 → 3, -23 → 7.
    #[pyo3(name = "Reflect")]
    Reflect,

    /// **Bounce** — Interpret the value as an amount of "energy" to travel
    /// within the range. `num >= 0` starts at the lower bound and moves right;
    /// `num < 0` starts at the upper bound and moves left, bouncing off the
    /// bounds until all energy is spent.
    ///
    /// Example with range [0, 10]: 12 → 8, 23 → 3, -12 → 2, -23 → 7.
    #[pyo3(name = "Bounce")]
    Bounce,

    /// **Clamp** — Values outside the range are pinned to the nearest bound. No wrapping
    /// or reflection; the result is always one of the two endpoints when outside.
    ///
    /// Example with range [0, 10]: 15 → 10, -3 → 0.
    #[pyo3(name = "Clamp")]
    Clamp,
}

/// Range and distance past the nearest bound, if `rem_euclid` / division is safe.
fn distance_past_bound_safe(min: f64, max: f64, num: f64) -> Option<(f64, f64)> {
    let range = max - min;
    let exceeded_bound = if num > max { max } else { min };
    let distance_past = num - exceeded_bound;
    if !range.is_finite() || !(distance_past / range).is_finite() {
        return None;
    }
    Some((range, distance_past))
}

/// Fold a distance along a span with reflection.
fn triangle_fold(distance_past_bound: f64, span: f64) -> f64 {
    let segment_index = (distance_past_bound / span).floor();
    let is_reflecting = (segment_index * 0.5).fract() != 0.0;
    let position_in_span = distance_past_bound.rem_euclid(span); // ∈ [0, span)
    if is_reflecting {
        span - position_in_span
    } else {
        position_in_span
    }
}

/// Maps an out-of-range value back into ``[min, max]``.
///
/// Implementors own the algorithm and the numerical-safety check for a single
/// fit mode. The orchestrator (`fit_with`) calls `fit_outside` only after
/// verifying that `num` is outside `[min, max]`, both bounds are finite, and
/// `max - min > 0`.
trait FitStrategy {
    /// Map `num` back into `[min, max]`. Returns `None` when the operation
    /// is not numerically safe (e.g. overflow); the orchestrator falls back
    /// to clamping in that case.
    fn fit_outside(&self, min: f64, max: f64, num: f64) -> Option<f64>;
}

struct WrapStrategy;

impl FitStrategy for WrapStrategy {
    fn fit_outside(&self, min: f64, max: f64, num: f64) -> Option<f64> {
        let (range, distance_past) = distance_past_bound_safe(min, max, num)?;
        Some(min + distance_past.rem_euclid(range))
    }
}

struct ReflectStrategy;

impl FitStrategy for ReflectStrategy {
    fn fit_outside(&self, min: f64, max: f64, num: f64) -> Option<f64> {
        let (range, distance_past) = distance_past_bound_safe(min, max, num)?;
        let offset = triangle_fold(distance_past.abs(), range);
        Some(if num > max { max - offset } else { min + offset })
    }
}

struct BounceStrategy;

impl FitStrategy for BounceStrategy {
    fn fit_outside(&self, min: f64, max: f64, num: f64) -> Option<f64> {
        let range = max - min;
        if !range.is_finite() || !(num.abs() / range).is_finite() {
            return None;
        }
        let offset = triangle_fold(num.abs(), range);
        Some(if num >= 0.0 { min + offset } else { max - offset })
    }
}

struct ClampStrategy;

impl FitStrategy for ClampStrategy {
    fn fit_outside(&self, min: f64, max: f64, num: f64) -> Option<f64> {
        Some(if num > max { max } else { min })
    }
}

impl FitMode {
    /// Single dispatch site mapping each `FitMode` to its strategy. Adding a
    /// new mode means a new struct + `impl FitStrategy` plus one line here;
    /// no other code in this module needs to change.
    fn strategy(&self) -> &'static dyn FitStrategy {
        match self {
            FitMode::Wrap => &WrapStrategy,
            FitMode::Reflect => &ReflectStrategy,
            FitMode::Bounce => &BounceStrategy,
            FitMode::Clamp => &ClampStrategy,
        }
    }
}

/// Validate inputs and delegate to a strategy. Mode-agnostic — adding a new
/// fit mode does not require touching this function.
fn fit_with(strategy: &dyn FitStrategy, min: f64, max: f64, num: f64) -> PyResult<f64> {
    if num >= min && num <= max {
        return Ok(num);
    }

    if !min.is_finite() || !max.is_finite() {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "min and max must be finite",
        ));
    }

    let range = max - min;
    if range <= 0.0 {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "range [lb, ub] must have positive width (lb < ub)",
        ));
    }

    let raw = strategy
        .fit_outside(min, max, num)
        .unwrap_or_else(|| num.clamp(min, max));
    // Clamp to [min, max] so FP rounding/underflow never violates the contract (e.g. when
    // range loses precision and reflect yields a value just outside the interval).
    Ok(raw.clamp(min, max))
}

#[gen_stub_pyfunction]
#[pyfunction]
#[pyo3(signature = (mode, min, max, num))]
/// Fit a number into the closed interval ``[min, max]`` using the given mode.
///
/// If ``num`` is already within ``[min, max]``, it is returned unchanged.
/// Otherwise, the chosen ``mode`` determines how values outside the interval are
/// mapped back into it.
///
/// Args:
///     mode (FitMode): The strategy used to map values into the interval.
///     min (float): The lower bound of the interval.
///     max (float): The upper bound of the interval.
///     num (float): The value to fit into the interval.
///
/// Returns:
///     float: A value within ``[min, max]``.
///
/// Raises:
///     ValueError: If ``max - min`` is not positive (i.e., ``min >= max``).
///     ValueError: If ``min`` or ``max`` are not finite.
///
/// Examples:
///     Using the interval ``[0, 10]``:
///
///     - ``Wrap``: ``fit(Wrap, 0, 10, 12) == 2``; ``fit(Wrap, 0, 10, -4) == 6``
///     - ``Reflect``: ``fit(Reflect, 0, 10, 12) == 8``; ``fit(Reflect, 0, 10, -4) == 4``
///     - ``Bounce``: ``fit(Bounce, 0, 10, 12) == 8``; ``fit(Bounce, 0, 10, -12) == 2``
///     - ``Clamp``: ``fit(Clamp, 0, 10, 12) == 10``; ``fit(Clamp, 0, 10, -4) == 0``
///
/// Notes:
///     - The interval is treated as *closed*: endpoints are included.
///     - Wrap and Reflect mode will revert to Clamp mode when the range between min and
///       max is not finite due to an overflow.
///     - Bounce mode will revert to Clamp mode when |num| / range is not finite due
///       to an overflow.
pub fn fit(mode: FitMode, min: f64, max: f64, num: f64) -> PyResult<f64> {
    fit_with(mode.strategy(), min, max, num)
}

#[gen_stub_pyfunction]
#[pyfunction]
#[pyo3(signature = (mode, min, max, nums))]
/// Fit a list of numbers into the closed interval ``[min, max]`` using the given mode.
///
/// Args:
///     mode (FitMode): The strategy used to map values into the interval.
///     min (float): The lower bound of the interval.
///     max (float): The upper bound of the interval.
///     nums (list of float): The values to fit into the interval.
///
/// Returns:
///     list of float: The fitted values.
///
/// Raises:
///     ValueError: If ``min`` or ``max`` are not finite.
///     ValueError: If ``max - min`` is not positive (i.e., ``min >= max``).
///     ValueError: If any of the values in ``nums`` are not finite.
pub fn fit_list(mode: FitMode, min: f64, max: f64, nums: Vec<f64>) -> PyResult<Vec<f64>> {
    let strategy = mode.strategy();
    nums.into_iter()
        .map(|num| fit_with(strategy, min, max, num))
        .collect()
}

#[gen_stub_pyfunction]
#[pyfunction]
#[pyo3(signature = (step, value))]
/// Quantize a value to the nearest multiple of ``step``.
///
/// Returns ``round(value / step) * step`` using IEEE-754 ``f64`` rounding
/// (round half away from zero).
///
/// Args:
///     step (float): The quantization step (grid size). Must be finite and non-zero.
///     value (float): The value to quantize.
///
/// Returns:
///     float: The quantized value.
///
/// Raises:
///     ValueError: If ``step`` is zero or not finite.
///     ValueError: If ``value`` is not finite.
///     ValueError: If ``step`` and ``value`` are such that quantization would
///         overflow ``f64``.
///
/// Notes:
///     For IEEE-754 ``f64``, quantization is guaranteed not to overflow when:
///
///     .. math::
///         |value| \le \min\bigl(\text{f64::MAX} \cdot |step|,\;
///                                  \text{f64::MAX} - 0.5\cdot|step|\bigr).
///
/// Examples:
///     ``quantize(1.0, 2.7) == 3.0``
///     ``quantize(1.0, 2.4) == 2.0``
///     ``quantize(1.0, 2.5) == 3.0``
///     ``quantize(0.5, -1.3) == -1.5``
///     ``quantize(0.3, 1.0) == math.isclose(0.9)``
pub fn quantize(step: f64, value: f64) -> PyResult<f64> {
    if !value.is_finite() {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "value must be finite",
        ));
    }
    if !step.is_finite() || step == 0.0 {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "step must be finite and non-zero",
        ));
    }

    let abs_step = step.abs();
    let abs_value = value.abs();
    let max = f64::MAX;

    // Division overflow: for |step| < 1, we can have |value / step| > f64::MAX.
    // For |step| >= 1, division cannot overflow because it shrinks the magnitude.
    let safe_div = abs_step >= 1.0 || abs_value <= max * abs_step;

    // Multiplication overflow: a sufficient bound is
    // |round(value / step) * step| <= |value| + 0.5 * |step|.
    // Enforce |value| + 0.5 * |step| <= f64::MAX. Use (max - abs_value) >= 0.5*step
    // so we never subtract a small value from max (which would round to max and
    // incorrectly allow values at the edge).
    let safe_mul = (max - abs_value) >= 0.5 * abs_step;

    if !safe_div || !safe_mul {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "value and step are outside the supported range for quantize (see notes)",
        ));
    }

    Ok((value / step).round() * step)
}
