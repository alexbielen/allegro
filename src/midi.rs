use pyo3::prelude::*;

use crate::py_stub::{gen_stub_pyclass, gen_stub_pyfunction, gen_stub_pymethods};

const PITCH_CLASS_NAMES: [&str; 12] = [
    "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B",
];

/// A concrete pitch identified by a MIDI key number.
#[gen_stub_pyclass]
#[pyclass]
#[derive(Clone, Copy)]
pub struct Pitch {
    keynum: i32,
}

impl Pitch {
    fn scientific_name(keynum: i32) -> String {
        let pc = keynum.rem_euclid(12) as usize;
        let octave = keynum.div_euclid(12) - 1;
        format!("{}{}", PITCH_CLASS_NAMES[pc], octave)
    }
}

#[gen_stub_pymethods]
#[pymethods]
impl Pitch {
    /// Scientific pitch notation (e.g. ``'C4'`` for MIDI key number 60).
    #[getter]
    fn name(&self) -> String {
        Self::scientific_name(self.keynum)
    }

    /// MIDI key number for this pitch.
    #[getter]
    fn keynum(&self) -> i32 {
        self.keynum
    }
}

/// Build a :class:`Pitch` from a MIDI key number.
#[gen_stub_pyfunction]
#[pyfunction]
#[pyo3(signature = (keynum))]
pub fn keynum_to_pitch(keynum: i32) -> Pitch {
    Pitch { keynum }
}
