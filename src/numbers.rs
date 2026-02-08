use pyo3::prelude::*;

/// Formats the sum of two numbers as string.
#[pyfunction]
pub fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

#[pyclass]
#[derive(Clone, Copy, PartialEq)]
pub enum FitMode {
    /// **Wrap** — Treat the range as a repeating cycle. Values above the upper bound
    /// wrap to the lower side, and values below the lower bound wrap to the upper side.
    ///
    /// Example with range [0, 10]: 15 → 5, 25 → 5, -3 → 7.
    #[pyo3(name = "Wrap")]
    Wrap,
    /// **Reflect** — Values outside the range are reflected off the boundaries instead of
    /// wrapping. Like a ball bouncing off the walls of the interval.
    ///
    /// Example with range [0, 10]: 15 → 5, 25 → 5, -3 → 3.
    #[pyo3(name = "Reflect")]
    Reflect,
    /// **Clamp** — Values outside the range are pinned to the nearest bound. No wrapping
    /// or reflection; the result is always one of the two endpoints when outside.
    ///
    /// Example with range [0, 10]: 15 → 10, -3 → 0.
    #[pyo3(name = "Clamp")]
    Clamp,
}

/// Fit a number into the range [lb, ub] using the given mode.
///
/// If the number is already inside [lb, ub], it is returned unchanged. If lb > ub,
/// the bounds are swapped so the range is valid. Mode defaults to Wrap.
///
/// # Examples (range [0, 10])
///
/// - **Wrap**: 12 → 2, -4 → 6 (periodic wrap in both directions).
/// - **Reflect**: 12 → 8, -4 → 4 (bounce off the bounds).
/// - **Clamp**: 12 → 10, -4 → 0 (pin to nearest bound).
///
/// Raises `ValueError` if the range has zero or negative width (lb == ub after swapping).
#[pyfunction]
#[pyo3(signature = (num, lb, ub, mode=None))]
pub fn fit(num: f64, lb: f64, ub: f64, mode: Option<FitMode>) -> PyResult<f64> {
    let mode = mode.unwrap_or(FitMode::Wrap);
    let (lb, ub) = if lb > ub { (ub, lb) } else { (lb, ub) };

    if num >= lb && num <= ub {
        return Ok(num);
    }
    let boundary_width = ub - lb;
    if boundary_width <= 0.0 {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "range [lb, ub] must have positive width (lb < ub)",
        ));
    }
    let exceeded_bound = if num > ub { ub } else { lb };
    let excess = num - exceeded_bound;

    Ok(match mode {
        FitMode::Wrap => {
            if exceeded_bound == ub {
                // Above range: wrap from the lower bound.
                lb + excess.rem_euclid(boundary_width)
            } else {
                // Below range: wrap from the upper bound. Reduce distance below by width
                // and step left from ub (excess is negative, so -excess is distance below).
                let steps_below = (-excess).rem_euclid(boundary_width);
                ub - steps_below
            }
        }
        FitMode::Reflect => {
            let two_width = 2.0 * boundary_width;
            let excess_in_period = excess % two_width;
            let offset = if excess_in_period.abs() > boundary_width {
                if excess_in_period >= 0.0 {
                    excess_in_period - two_width
                } else {
                    excess_in_period + two_width
                }
            } else {
                -excess_in_period
            };
            exceeded_bound + offset
        }
        FitMode::Clamp => exceeded_bound,
    })
}
