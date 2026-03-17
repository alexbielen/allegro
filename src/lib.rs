use pyo3::prelude::*;

mod boids;
mod error;
mod numbers;
mod physical;
mod pitchclass;
mod quadratic;
mod time;

/// A Python module implemented in Rust.
#[pymodule]
fn allegro(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // numbers module (number.rs)
    m.add_function(wrap_pyfunction!(numbers::fit, m)?)?;
    m.add_function(wrap_pyfunction!(numbers::fit_list, m)?)?;
    m.add_function(wrap_pyfunction!(numbers::quantize, m)?)?;
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

    // time module (time.rs)
    m.add_function(wrap_pyfunction!(time::bpm_to_seconds, m)?)?;

    // boids module (boids.rs)
    m.add_class::<boids::Dimensions>()?;
    m.add_class::<boids::Universe>()?;
    m.add_class::<boids::Boid>()?;
    m.add_function(wrap_pyfunction!(
        boids::create_boids_with_random_positions,
        m
    )?)?;

    Ok(())
}
