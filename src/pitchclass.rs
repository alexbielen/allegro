use pyo3::prelude::*;

use crate::forte_lookup::forte_for_normal_form;
use crate::utils::has_unique_elements;

/// Unordered set of distinct pitch classes (0–11), up to 12 elements.
/// `pcs` is stored sorted ascending.
#[pyclass]
#[derive(Clone)]
pub struct PitchClassSet {
    pub pcs: Vec<i8>,
}

#[pymethods]
impl PitchClassSet {
    #[new]
    #[pyo3(signature = (pitch_classes))]
    fn new(pitch_classes: Vec<i8>) -> PyResult<Self> {
        if pitch_classes.len() > 12 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "at most 12 pitch classes allowed",
            ));
        }

        if !has_unique_elements(&pitch_classes) {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "pitch classes must be unique",
            ));
        }

        for &pc in &pitch_classes {
            pc_guard(pc)?;
        }

        Ok(Self { pcs: pitch_classes })
    }

    fn normal_form(&self) -> Vec<i8> {
        get_normal_form(&sorted_pitch_classes(&self.pcs))
    }

    /// Rahn prime form (`src/specs/pitchclass.md`): normal order of `S`, transpose to 0;
    /// normal order of `I₀(S)`, transpose to 0; take the lexicographically smaller row
    /// (more compact to the left).
    fn prime_form(&self) -> Vec<i8> {
        let sorted = sorted_pitch_classes(&self.pcs);
        let nf = get_normal_form(&sorted);
        let mut inverted: Vec<i8> = sorted.iter().copied().map(invert_pc).collect();
        inverted.sort_unstable();
        let nf_inv = get_normal_form(&inverted);
        let prime_from_set = transpose_prime_to_zero(&nf);
        let prime_from_inv = transpose_prime_to_zero(&nf_inv);
        std::cmp::min(prime_from_set, prime_from_inv)
    }

    fn forte_num(&self) -> PyResult<String> {
        let nf = self.normal_form();
        forte_for_normal_form(&nf)
            .map(str::to_string)
            .ok_or_else(|| {
                pyo3::exceptions::PyValueError::new_err("normal form not found in Forte catalog")
            })
    }
}

fn sorted_pitch_classes(pcs: &[i8]) -> Vec<i8> {
    let mut v = pcs.to_vec();
    v.sort_unstable();
    v
}

/// Normal form from sorted distinct pitch classes (`src/specs/pitchclass.md`).
fn get_normal_form(sorted_pcs: &[i8]) -> Vec<i8> {
    let n = sorted_pcs.len();
    match n {
        0 => vec![],
        1 => vec![sorted_pcs[0].rem_euclid(12)],
        _ => std::iter::once(get_rotations(sorted_pcs))
            .map(get_candidates)
            .map(|candidates| break_ties(candidates, n))
            .map(|winners| {
                wrap_pitch_classes_line(
                    winners
                        .first()
                        .expect("at least one rotation survives tie-breaking"),
                )
            })
            .next()
            .expect("once() always yields one item"),
    }
}

/// Transpose a normal-order row so the first pitch class is 0 (`p - p₀` mod 12).
fn transpose_prime_to_zero(line: &[i8]) -> Vec<i8> {
    if line.is_empty() {
        return vec![];
    }
    let t = line[0];
    line.iter().map(|&p| (p - t).rem_euclid(12)).collect()
}

/// All cyclic rotations as linear pitch rows (`src/specs/pitchclass.md`).
///
/// `sorted_pcs` must have length ≥ 2.
fn get_rotations(sorted_pcs: &[i8]) -> Vec<Vec<i8>> {
    let n = sorted_pcs.len();
    (0..n).map(|i| rotation(sorted_pcs, i)).collect()
}

/// One rotation: pivot `start` splits `sorted_pcs` — suffix in base octave, prefix raised by +12.
fn rotation(sorted_pcs: &[i8], start: usize) -> Vec<i8> {
    let mut out: Vec<i8> = sorted_pcs[start..].to_vec();
    out.extend(sorted_pcs[..start].iter().map(|&p| p + 12));
    out
}

/// Step 1 — keep rotations with minimal total span `r[n-1] - r[0]`.
fn get_candidates(rotations: Vec<Vec<i8>>) -> Vec<Vec<i8>> {
    let n = rotations[0].len();
    let min_span = rotations
        .iter()
        .map(|r| r[n - 1] - r[0])
        .min()
        .expect("non-empty rotations");
    rotations
        .into_iter()
        .filter(|r| r[n - 1] - r[0] == min_span)
        .collect()
}

/// Step 2 — if several rotations tie, narrow using `r[n-i] - r[0]` for `i = 2..=n` (Python `r[-i]`).
fn break_ties(mut candidates: Vec<Vec<i8>>, n: usize) -> Vec<Vec<i8>> {
    if candidates.len() <= 1 {
        return candidates;
    }
    for i in 2..=n {
        let min_inner = candidates
            .iter()
            .map(|r| r[n - i] - r[0])
            .min()
            .expect("non-empty candidates");
        candidates.retain(|r| r[n - i] - r[0] == min_inner);
        if candidates.len() == 1 {
            break;
        }
    }
    candidates
}

/// Map linear pitches back to canonical pitch-class integers (`p % 12`, Euclidean modulus).
fn wrap_pitch_classes_line(line: &[i8]) -> Vec<i8> {
    line.iter().map(|&p| p.rem_euclid(12)).collect()
}

fn semitone_guard(semitones: i8) -> PyResult<()> {
    if !(-11..=11).contains(&semitones) {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "by_semitones must be within the range (-11)-11",
        ));
    }
    Ok(())
}

fn pc_guard(pc: i8) -> PyResult<()> {
    if !(0..=11).contains(&pc) {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "pc must be within the range 0-11",
        ));
    }
    Ok(())
}

#[inline]
fn wrap_pc_0_11(mut x: i8) -> i8 {
    // x is in a small range (for transpose: -11..=22)
    if x < 0 {
        x += 12;
    } else if x >= 12 {
        x -= 12;
    }
    x
}

#[inline]
fn invert_pc(pc: i8) -> i8 {
    // (12 - pc) mod 12, but pc is 0..=11
    if pc == 0 { 0 } else { 12 - pc }
}

/// Invert a pitch class around 0.
///
/// This computes the inversion of a pitch class by subtracting it from 12
/// and wrapping the result modulo 12.
///
/// Args:
///     pc (int): The pitch class to invert.
///         Must be an integer in the range 0–11.
///
/// Returns:
///     int: The inverted pitch class, wrapped to the range 0–11.
///
/// Raises:
///     ValueError: If ``pc`` is not in the range 0–11.
///
/// Notes:
///     This function uses an i8 under the hood. While it will raise an exception
///     if the input is outside the range 0–11, you will get an OverflowError results if
///     the input is outside the range of an i8 (i.e. -128 to 127).
///
#[pyfunction]
#[pyo3(signature = (pc))]
pub fn invert(pc: i8) -> PyResult<i8> {
    pc_guard(pc)?;
    Ok(invert_pc(pc))
}

/// Transpose a pitch class by a given number of semitones.
///
/// The pitch class is shifted by the given number of semitones and the
/// result is wrapped modulo 12.
///
/// Args:
///     by_semitones (int): The number of semitones to transpose by.
///         Must be in the range -11 to 11.
///     pc (int): The pitch class to transpose.
///         Must be an integer in the range 0–11.
///
/// Returns:
///     int: The transposed pitch class, wrapped to the range 0–11.
///
/// Raises:
///     ValueError: If ``by_semitones`` is outside the range -11 to 11.
///     ValueError: If ``pc`` is not in the range 0–11.
///
#[pyfunction]
#[pyo3(signature = (by_semitones, pc))]
pub fn transpose(by_semitones: i8, pc: i8) -> PyResult<i8> {
    semitone_guard(by_semitones)?;
    pc_guard(pc)?;
    Ok(wrap_pc_0_11(by_semitones + pc))
}

#[pyfunction]
#[pyo3(signature = (by_semitones, ordered_set))]
pub fn transpose_ordered_set(by_semitones: i8, ordered_set: Vec<i8>) -> PyResult<Vec<i8>> {
    semitone_guard(by_semitones)?;

    let mut out = Vec::with_capacity(ordered_set.len());
    for &pc in &ordered_set {
        pc_guard(pc)?;
        out.push(wrap_pc_0_11(pc + by_semitones));
    }
    Ok(out)
}

#[pyfunction]
#[pyo3(signature = (ordered_set))]
pub fn invert_ordered_set(ordered_set: Vec<i8>) -> PyResult<Vec<i8>> {
    let mut out = Vec::with_capacity(ordered_set.len());
    for &pc in &ordered_set {
        pc_guard(pc)?;
        out.push(invert_pc(pc));
    }
    Ok(out)
}
