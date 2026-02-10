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

/// Fit a number into the range [lb, ub] using the given mode.
///
/// If the number is already inside [lb, ub], it is returned unchanged. If lb > ub,
/// the bounds are swapped so the range is valid. Mode defaults to Wrap.
///
/// # Examples (range [0, 10])
///
/// - **Wrap**: 12 → 2, -4 → 6 (periodic wrap in both directions).
/// - **Reflect**: 12 → 8, -4 → 6 (coordinate-based reflection off the bounds).
/// - **Bounce**: 12 → 8, -12 → 2 (energy-based bounce from min/max).
/// - **Clamp**: 12 → 10, -4 → 0 (pin to nearest bound).
///
/// Raises `ValueError` if the range has zero or negative width (lb == ub after swapping).
#[pyfunction]
#[pyo3(signature = (mode, min, max, num))]
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
        FitMode::Wrap => (num - min).rem_euclid(range) + min,
        FitMode::Reflect => {
            // Treat `num` as a coordinate and map it back into
            // [min, max] by reflecting at the nearest bound with the remaining offset.
            let two_range = 2.0 * range;
            let value = (num - exceeded_bound) % two_range;
            let offset = if value.abs() > range {
                if value >= 0.0 {
                    value - two_range
                } else {
                    value + two_range
                }
            } else {
                -value
            };

            exceeded_bound + offset
        }
        FitMode::Bounce => {
            // Treat the magnitude of `num` as energy, and its sign as direction:
            // if num >= 0: start at min and move right
            // if num < 0: start at max and move left.
            // One round trip (min→max→min or max→min→max) consumes 2 * range energy.
            let energy = num.abs();
            let period = 2.0 * range;
            let r = energy.rem_euclid(period);
            let offset = if r <= range { r } else { 2.0 * range - r };

            if num >= 0.0 {
                min + offset
            } else {
                max - offset
            }
        }
        FitMode::Clamp => exceeded_bound,
    })
}
