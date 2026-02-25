use pyo3::prelude::*;

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

/// Fold a distance along a span with reflection
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

    let exceeded_bound = if num > max { max } else { min };
    let distance_past = num - exceeded_bound;

    // rem_euclid and triangle_fold divide by range; when the quotient overflows we get nan.
    let wrap_reflect_rem_safe = range.is_finite() && (distance_past / range).is_finite();
    let bounce_rem_safe = range.is_finite() && (num.abs() / range).is_finite();

    let raw = match mode {
        FitMode::Wrap => wrap_reflect_rem_safe.then(|| min + distance_past.rem_euclid(range)),

        FitMode::Reflect => wrap_reflect_rem_safe.then(|| {
            let offset = triangle_fold(distance_past.abs(), range);
            if num > max {
                max - offset
            } else {
                min + offset
            }
        }),

        FitMode::Bounce => bounce_rem_safe.then(|| {
            let offset = triangle_fold(num.abs(), range);
            if num >= 0.0 {
                min + offset
            } else {
                max - offset
            }
        }),

        FitMode::Clamp => Some(exceeded_bound),
    };

    let result = raw.unwrap_or_else(|| num.clamp(min, max));
    // Clamp to [min, max] so FP rounding/underflow never violates the contract (e.g. when
    // range loses precision and reflect yields a value just outside the interval).
    Ok(result.clamp(min, max))
}

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
    // Enforce |value| + 0.5 * |step| <= f64::MAX, written in a form that avoids
    // overflow in the check itself.
    let safe_mul = abs_value <= max - 0.5 * abs_step;

    if !safe_div || !safe_mul {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "value and step are outside the supported range for quantize (see notes)",
        ));
    }

    Ok((value / step).round() * step)
}
