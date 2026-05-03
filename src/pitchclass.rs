use pyo3::prelude::*;

use crate::forte_lookup::forte_for_prime_form;
use crate::utils::has_unique_elements;

/// Unordered set of distinct pitch classes.
///
/// `PitchClassSet` represents a set-class-style collection of pitch classes,
/// where each pitch class must be unique and in the range 0–11.
///
/// Args:
///     pitch_classes (list[int]): The pitch classes in the set.
///         Each value must be unique and in the range 0–11.
///         At most 12 pitch classes are allowed.
///
/// Raises:
///     ValueError: If more than 12 pitch classes are provided.
///     ValueError: If any pitch class is duplicated.
///     ValueError: If any pitch class is outside the range 0–11.
///
/// Notes:
///     Although this type represents an unordered set, the current input order
///     is preserved internally. Methods that require sorted pitch classes sort
///     internally before computing their results.
#[pyclass]
#[derive(Clone)]
pub struct PitchClassSet {
    pub pcs: Vec<i8>,
}

#[pymethods]
impl PitchClassSet {
    /// Create a new pitch-class set.
    ///
    /// Args:
    ///     pitch_classes (list[int]): The pitch classes in the set.
    ///         Each value must be unique and in the range 0–11.
    ///         At most 12 pitch classes are allowed.
    ///
    /// Returns:
    ///     PitchClassSet: A new pitch-class set.
    ///
    /// Raises:
    ///     ValueError: If more than 12 pitch classes are provided.
    ///     ValueError: If any pitch class is duplicated.
    ///     ValueError: If any pitch class is outside the range 0–11.
    #[new]
    #[pyo3(signature = (pitch_classes))]
    fn new(pitch_classes: Vec<i8>) -> PyResult<Self> {
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

    /// Compute the normal form of the pitch-class set.
    ///
    /// The normal form is the most “compact” ordering of the set when treated as
    /// an ascending scale within a single octave.
    ///
    /// Algorithm:
    ///     1. Generate all cyclic rotations of the sorted pitch classes. Each
    ///        rotation is interpreted as an ascending pitch sequence (wrapping
    ///        earlier elements up an octave).
    ///
    ///     2. Select the rotation(s) with the smallest total span:
    ///        (last_pitch - first_pitch).
    ///
    ///     3. If multiple candidates remain, break ties by comparing intervals
    ///        from the left:
    ///            - Then (second-to-last - first), if still tied,
    ///            - Then (third-to-last - first), and so on
    ///        Keep only the most “left-packed” (most compact toward the beginning).
    ///
    ///     4. If a tie still remains, choose the ordering whose first pitch class
    ///        is smallest.
    ///
    ///     5. Finally, wrap all pitches modulo 12 to return pitch classes.
    ///
    /// Returns:
    ///     list[int]: The normal form of the set as pitch classes in the range 0–11.
    ///
    /// Notes:
    ///     This implementation follows the standard post-tonal theory definition
    ///     (Rahn/Straus style) and corresponds to the algorithm described in
    ///     `src/specs/pitchclass.md`.
    fn normal_form(&self) -> Vec<i8> {
        get_normal_form(&sorted_pitch_classes(&self.pcs))
    }

    /// Compute the Rahn prime form of the pitch-class set.
    ///
    /// This computes the normal form of the set and the normal form of its
    /// inversion, transposes both so that they begin on 0, and returns the
    /// lexicographically smaller result.
    ///
    /// Returns:
    ///     list[int]: The prime form of the set as pitch classes in the range 0–11.
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

    /// Look up the Forte number for the pitch-class set.
    ///
    /// The set is converted to Rahn prime form and then matched against the Forte
    /// catalog.
    ///
    /// Returns:
    ///     str: The Forte number for the set.
    ///
    /// Raises:
    ///     ValueError: If the prime form is not found in the Forte catalog.
    fn forte_num(&self) -> PyResult<String> {
        let prime = self.prime_form();
        forte_for_prime_form(&prime)
            .map(str::to_string)
            .ok_or_else(|| {
                pyo3::exceptions::PyValueError::new_err(
                    "prime form not found in Forte catalog (expected Wikipedia/Rahn prime column)",
                )
            })
    }

    /// Return the **interval-class vector** (six counts, Forte style).
    ///
    /// For every unordered pair of distinct pitch classes, form the smaller
    /// pitch interval in semitones (1..=11), map it to an interval class
    /// 1..=6, and increment the count at index ``ic - 1``.
    fn interval_vector(&self) -> Vec<i8> {
        interval_class_vector(&self.pcs)
    }
}

fn sorted_pitch_classes(pcs: &[i8]) -> Vec<i8> {
    let mut v = pcs.to_vec();
    v.sort_unstable();
    v
}

/// Counts of interval classes 1..=6 for all unordered pairs in the set.
fn interval_class_vector(pcs: &[i8]) -> Vec<i8> {
    let sorted = sorted_pitch_classes(pcs);
    let n = sorted.len();
    let mut counts = [0i8; 6];
    for i in 0..n {
        for j in (i + 1)..n {
            let d = sorted[j] - sorted[i];
            let ic = semitones_to_interval_class(d);
            counts[(ic - 1) as usize] += 1;
        }
    }
    counts.to_vec()
}

/// Map a pitch interval in semitones (1..=11) to its interval class (1..=6).
#[inline]
fn semitones_to_interval_class(d: i8) -> i8 {
    debug_assert!((1..=11).contains(&d));
    if d > 6 { 12 - d } else { d }
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

/// Transpose an ordered pitch-class row by a given number of semitones.
///
/// Each pitch class in the ordered set is shifted by the given number of
/// semitones, preserving the order of the input row. Results are wrapped
/// modulo 12.
///
/// Args:
///     by_semitones (int): The number of semitones to transpose by.
///         Must be in the range -11 to 11.
///     ordered_set (list[int]): The ordered pitch classes to transpose.
///         Each pitch class must be in the range 0–11.
///
/// Returns:
///     list[int]: The transposed ordered set, with each pitch class wrapped
///     to the range 0–11.
///
/// Raises:
///     ValueError: If ``by_semitones`` is outside the range -11 to 11.
///     ValueError: If any pitch class is outside the range 0–11.
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

/// Invert an ordered pitch-class row around 0.
///
/// Each pitch class in the ordered set is inverted by subtracting it from 12
/// and wrapping the result modulo 12. The order of the input row is preserved.
///
/// Args:
///     ordered_set (list[int]): The ordered pitch classes to invert.
///         Each pitch class must be in the range 0–11.
///
/// Returns:
///     list[int]: The inverted ordered set, with each pitch class wrapped to
///     the range 0–11.
///
/// Raises:
///     ValueError: If any pitch class is outside the range 0–11.
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

/// Map a pitch interval (in semitones, any representative mod 12) to interval class 0–6.
///
/// ``0`` means unison/octave (interval ≡ 0 mod 12); classes ``1``–``6`` are the usual
/// interval classes for distinct pitch classes.
#[pyfunction]
#[pyo3(signature = (interval))]
pub fn interval_class(interval: i8) -> PyResult<i8> {
    let d = interval.rem_euclid(12);
    if d == 0 {
        return Ok(0);
    }
    Ok(semitones_to_interval_class(d))
}
