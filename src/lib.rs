use pyo3::prelude::*;

mod error;
mod numbers;
mod physical;
mod pitchclass;
mod quadratic;

/// A Python module implemented in Rust.
#[pymodule]
fn allegro(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // numbers module (number.rs)
    m.add_function(wrap_pyfunction!(numbers::fit, m)?)?;
    m.add_class::<numbers::FitMode>()?;

    // physical module (physical.rs)
    m.add_function(wrap_pyfunction!(physical::bouncing_ball, m)?)?;

    // quadratic module (quadratic.rs)
    m.add_function(wrap_pyfunction!(quadratic::quadratic_bouncing_ball, m)?)?;

    // pitch class module (pitchclass.rs)
    m.add_function(wrap_pyfunction!(pitchclass::transpose, m)?)?;
    m.add_function(wrap_pyfunction!(pitchclass::invert, m)?)?;
    m.add_function(wrap_pyfunction!(pitchclass::transpose_ordered_set, m)?)?;
    m.add_function(wrap_pyfunction!(pitchclass::invert_ordered_set, m)?)?;

    Ok(())
}
