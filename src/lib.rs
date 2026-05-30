use pyo3::prelude::*;

use pyo3_stub_gen::{define_stub_info_gatherer, reexport_module_members};

mod boids;
mod py_stub;
mod error;
mod forte_lookup;
mod midi;
mod mnx;
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
    m.add_function(wrap_pyfunction!(pitchclass::satisfy_pc, m)?)?;
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

    // mnx module (mnx.rs)
    m.add_class::<mnx::NoteStep>()?;
    m.add_class::<mnx::NoteValueBase>()?;
    m.add_class::<mnx::ClefSign>()?;
    m.add_class::<mnx::BarlineType>()?;
    m.add_class::<mnx::MnxPitch>()?;
    m.add_class::<mnx::MnxNoteValue>()?;
    m.add_class::<mnx::MnxRest>()?;
    m.add_class::<mnx::MnxNote>()?;
    m.add_class::<mnx::MnxEvent>()?;
    m.add_class::<mnx::MnxSequence>()?;
    m.add_class::<mnx::MnxClef>()?;
    m.add_class::<mnx::MnxPositionedClef>()?;
    m.add_class::<mnx::MnxKeySignature>()?;
    m.add_class::<mnx::MnxTimeSignature>()?;
    m.add_class::<mnx::MnxBarline>()?;
    m.add_class::<mnx::MnxTempo>()?;
    m.add_class::<mnx::MnxMeasureGlobal>()?;
    m.add_class::<mnx::MnxGlobalData>()?;
    m.add_class::<mnx::MnxMetadata>()?;
    m.add_class::<mnx::MnxPartMeasure>()?;
    m.add_class::<mnx::MnxPart>()?;
    m.add_class::<mnx::MnxDocument>()?;

    Ok(())
}

// Namespace re-exports (generates `python/allegro/<name>/__init__.py` via `generate-init-py`).
reexport_module_members!(
    "allegro.pitchclass" from "allegro.allegro";
    "PitchClassSet",
    "interval_class",
    "invert",
    "invert_ordered_set",
    "satisfy_pc",
    "transpose",
    "transpose_ordered_set"
);
reexport_module_members!(
    "allegro.voicing" from "allegro.allegro";
    "DistanceMode",
    "VoiceLeading",
    "Voicing",
    "voicings_from_pc_set",
    "voicings_from_pc_set_in_keynum_range",
    "voicings_from_pc_set_within_span"
);
reexport_module_members!(
    "allegro.numbers" from "allegro.allegro";
    "FitMode",
    "fit",
    "fit_list",
    "quantize"
);
reexport_module_members!(
    "allegro.midi" from "allegro.allegro";
    "Pitch",
    "keynum_to_pitch"
);
reexport_module_members!(
    "allegro.boids" from "allegro.allegro";
    "Boid",
    "Dimensions",
    "Universe",
    "create_boids_with_random_positions"
);
reexport_module_members!(
    "allegro.quadratic" from "allegro.allegro";
    "quadratic_bouncing_ball"
);
reexport_module_members!(
    "allegro.mnx" from "allegro.allegro";
    "BarlineType",
    "ClefSign",
    "MnxBarline",
    "MnxClef",
    "MnxDocument",
    "MnxEvent",
    "MnxGlobalData",
    "MnxKeySignature",
    "MnxMeasureGlobal",
    "MnxMetadata",
    "MnxNote",
    "MnxNoteValue",
    "MnxPart",
    "MnxPartMeasure",
    "MnxPitch",
    "MnxPositionedClef",
    "MnxRest",
    "MnxSequence",
    "MnxTempo",
    "MnxTimeSignature",
    "NoteStep",
    "NoteValueBase"
);
define_stub_info_gatherer!(stub_info);
