use pyo3::prelude::*;

use crate::pitchclass::PitchClassSet;

/// MIDI key number for a pitch class at scientific octave (C4 = octave 4 → 60).
fn midi_at_octave(pc: i8, octave: i32) -> i32 {
    12 * (octave + 1) + i32::from(pc)
}

/// Ascending semitone distance from one pitch class to another (1–11 for distinct PCs).
fn ascending_pc_interval(from: i8, to: i8) -> i32 {
    i32::from((to - from).rem_euclid(12))
}

/// Build MIDI notes for one permutation, anchoring ``anchor_pc`` at ``anchor_midi``.
fn voicing_from_permutation(permutation: &[i8], anchor_pc: i8, anchor_midi: i32) -> Vec<i32> {
    let n = permutation.len();
    let mut notes = vec![0i32; n];
    let anchor_index = permutation
        .iter()
        .position(|&pc| pc == anchor_pc)
        .expect("anchor_pc must appear in permutation");
    notes[anchor_index] = anchor_midi;

    for i in (0..anchor_index).rev() {
        let interval = ascending_pc_interval(permutation[i], permutation[i + 1]);
        notes[i] = notes[i + 1] - interval;
    }
    for i in anchor_index + 1..n {
        let interval = ascending_pc_interval(permutation[i - 1], permutation[i]);
        notes[i] = notes[i - 1] + interval;
    }
    notes
}

/// All permutations of ``items`` (order matters; ``n!`` results).
fn permutations(items: &[i8]) -> Vec<Vec<i8>> {
    let n = items.len();
    if n == 0 {
        return vec![vec![]];
    }
    let mut out = Vec::new();
    let mut perm = items.to_vec();
    let mut c = vec![0usize; n];
    out.push(perm.clone());
    let mut i = 0;
    while i < n {
        if c[i] < i {
            if i % 2 == 0 {
                perm.swap(0, i);
            } else {
                perm.swap(c[i], i);
            }
            out.push(perm.clone());
            c[i] += 1;
            i = 0;
        } else {
            c[i] = 0;
            i += 1;
        }
    }
    out
}

#[pyclass]
#[derive(Clone)]
/// A specific arrangement of pitches as MIDI key numbers.
pub struct Voicing {
    notes: Vec<i32>,
}

#[pymethods]
impl Voicing {
    /// Create a voicing from an explicit list of MIDI key numbers.
    #[new]
    fn new(notes: Vec<i32>) -> Self {
        Self { notes }
    }

    /// MIDI key numbers in voice order.
    #[getter]
    fn notes(&self) -> Vec<i32> {
        self.notes.clone()
    }

    /// All pairwise semitone distances between notes, sorted ascending.
    #[getter]
    fn all_intervals(&self) -> Vec<i32> {
        let mut intervals = Vec::new();
        let n = self.notes.len();
        for i in 0..n {
            for j in i + 1..n {
                intervals.push((self.notes[i] - self.notes[j]).abs());
            }
        }
        intervals.sort_unstable();
        intervals
    }

    /// Semitone distances between adjacent notes in voice order.
    #[getter]
    fn adjacent_intervals(&self) -> Vec<i32> {
        self.notes
            .windows(2)
            .map(|w| (w[1] - w[0]).abs())
            .collect()
    }

    /// Span from lowest to highest note (semitones).
    #[getter]
    fn span(&self) -> i32 {
        let min = self.notes.iter().copied().min().unwrap_or(0);
        let max = self.notes.iter().copied().max().unwrap_or(0);
        max - min
    }

    /// Distance to another voicing using the given mode.
    #[pyo3(signature = (other, mode = DistanceMode::SumAbs))]
    fn distance_to(&self, other: &Voicing, mode: DistanceMode) -> PyResult<i32> {
        if self.notes.len() != other.notes.len() {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "voicings must have the same number of voices",
            ));
        }
        match mode {
            DistanceMode::SumAbs => Ok(self
                .notes
                .iter()
                .zip(&other.notes)
                .map(|(a, b)| (a - b).abs())
                .sum()),
        }
    }
}

#[pyclass]
#[derive(Clone, Copy, PartialEq, Eq, Default)]
/// Strategy for measuring distance between two voicings.
pub enum DistanceMode {
    /// Sum of absolute semitone differences, voice by voice.
    #[pyo3(name = "SumAbs")]
    #[default]
    SumAbs,
}

/// Reserved for future voice-leading path search between chords.
#[pyclass]
pub struct VoiceLeading {}

#[pymethods]
impl VoiceLeading {
    #[new]
    fn new() -> Self {
        Self {}
    }
}

/// Enumerate all voicings of a pitch-class set at a given register.
///
/// The first pitch class in ``pcs`` (input order) is placed at ``octave``
/// (default 4, e.g. C4 = MIDI 60 when that pitch class is 0). Each permutation
/// of the set is realized by walking ascending pitch-class steps along the order.
#[pyfunction]
#[pyo3(signature = (pcs, octave = 4))]
pub fn voicings_from_pc_set(pcs: &PitchClassSet, octave: i32) -> PyResult<Vec<Voicing>> {
    if pcs.pcs.is_empty() {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "pitch-class set must not be empty",
        ));
    }
    let anchor_pc = pcs.pcs[0];
    let anchor_midi = midi_at_octave(anchor_pc, octave);
    let perms = permutations(&pcs.pcs);
    Ok(perms
        .into_iter()
        .map(|perm| Voicing {
            notes: voicing_from_permutation(&perm, anchor_pc, anchor_midi),
        })
        .collect())
}
