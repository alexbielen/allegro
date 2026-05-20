use pyo3::prelude::*;

mod boids;
mod error;
mod forte_lookup;
mod midi;
mod numbers;
mod physical;
mod pitchclass;
mod quadratic;
mod voicing;
mod time;
mod utils;

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
    m.add_function(wrap_pyfunction!(pitchclass::interval_class, m)?)?;
    m.add_class::<pitchclass::PitchClassSet>()?;

    // voicing module (voicing.rs)
    m.add_class::<voicing::Voicing>()?;
    m.add_class::<voicing::DistanceMode>()?;
    m.add_class::<voicing::VoiceLeading>()?;
    m.add_function(wrap_pyfunction!(voicing::voicings_from_pc_set, m)?)?;
    m.add_function(wrap_pyfunction!(voicing::voicings_from_pc_set_in_keynum_range, m)?)?;
    m.add_function(wrap_pyfunction!(voicing::voicings_from_pc_set_within_span, m)?)?;

    // midi module (midi.rs)
    m.add_class::<midi::Pitch>()?;
    m.add_function(wrap_pyfunction!(midi::keynum_to_pitch, m)?)?;

    // time module (time.rs)
    m.add_function(wrap_pyfunction!(time::bpm_to_seconds, m)?)?;
    m.add_function(wrap_pyfunction!(time::rhythm_to_seconds, m)?)?;

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
