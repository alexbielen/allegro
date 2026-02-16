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

fn triangle_fold(distance_past_bound: f64, span: f64) -> Option<f64> {
    if !(distance_past_bound.is_finite() && span.is_finite()) || span <= 0.0 {
        return None;
    }

    // calculates the number of spans travelled
    let segment_index = (distance_past_bound / span).floor();

    // checks if the number of spans travelled is even or odd in a floating point safe way
    let is_reflecting = (segment_index * 0.5).fract() != 0.0;

    let position_in_span = distance_past_bound.rem_euclid(span); // ∈ [0, span)

    Some(if is_reflecting {
        span - position_in_span
    } else {
        position_in_span
    })
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
///     - For extremely large spans or non-finite intermediate values, the
///       implementation may fall back to clamping to guarantee an in-range result.
pub fn fit(mode: FitMode, min: f64, max: f64, num: f64) -> PyResult<f64> {
    // If the number is already in the range, return it unchanged.
    if num >= min && num <= max {
        return Ok(num);
    }

    let range = max - min;
    if range <= 0.0 {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "range [lb, ub] must have positive width (lb < ub)",
        ));
    }

    let exceeded_bound = if num > max { max } else { min };

    Ok(match mode {
        FitMode::Wrap => {
            if !range.is_finite() {
                num.clamp(min, max)
            } else if num > max {
                let distance_from_max = num - max;
                let wrapped_offset = distance_from_max.rem_euclid(range);
                min + wrapped_offset
            } else {
                let distance_from_min = num - min;

                if distance_from_min.is_finite() {
                    min + distance_from_min.rem_euclid(range)
                } else {
                    num.clamp(min, max)
                }
            }
        }

        FitMode::Reflect => {
            if !range.is_finite() {
                num.clamp(min, max)
            } else {
                let distance_past_bound = (num - exceeded_bound).abs();

                match triangle_fold(distance_past_bound, range) {
                    Some(offset) => {
                        if num > max {
                            max - offset
                        } else {
                            min + offset
                        }
                    }
                    None => num.clamp(min, max),
                }
            }
        }

        FitMode::Bounce => {
            if !range.is_finite() {
                num.clamp(min, max)
            } else {
                let energy = num.abs();

                match triangle_fold(energy, range) {
                    Some(offset) => {
                        if num >= 0.0 {
                            min + offset
                        } else {
                            max - offset
                        }
                    }
                    None => num.clamp(min, max),
                }
            }
        }

        FitMode::Clamp => exceeded_bound,
    })
}
