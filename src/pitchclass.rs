use pyo3::prelude::*;

use crate::forte_lookup::{forte_for_prime_form, prime_form_for_forte_num};
use crate::py_stub::{gen_stub_pyclass, gen_stub_pyfunction, gen_stub_pymethods};
use crate::utils::has_unique_elements;

// ============ PitchClass primitive ============

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, PartialOrd, Ord)]
struct PitchClass(i8);

impl PitchClass {
    fn try_new(pc: i8) -> PyResult<Self> {
        crate::error::require((0..=11).contains(&pc), "pc must be within the range 0-11")?;
        Ok(Self(pc))
    }

    fn raw(self) -> i8 {
        self.0
    }

    fn invert(self) -> Self {
        Self((-self.0).rem_euclid(12))
    }

    fn transpose(self, semitones: i8) -> Self {
        Self((self.0 + semitones).rem_euclid(12))
    }
}

fn validate_semitones(s: i8) -> PyResult<()> {
    crate::error::require(
        (-11..=11).contains(&s),
        "by_semitones must be within the range (-11)-11",
    )
}

// ============ PitchClassSet (PyO3 class) ============

/// A collection of distinct pitch classes.
///
/// `PitchClassSet` represents a collection of distinct pitch classes,
/// where each pitch class must be unique and in the range 0–11.
///
/// Notes:
///     Although this type represents an unordered set, the current input order
///     is preserved internally. Methods that require sorted pitch classes sort
///     internally before computing their results.
#[gen_stub_pyclass]
#[pyclass]
#[derive(Clone)]
pub struct PitchClassSet {
    pcs: Vec<PitchClass>,
}

impl PitchClassSet {
    pub(crate) fn is_empty(&self) -> bool {
        self.pcs.is_empty()
    }

    pub(crate) fn pcs_i8(&self) -> Vec<i8> {
        self.pcs.iter().copied().map(PitchClass::raw).collect()
    }

    pub(crate) fn first_pc_i8(&self) -> Option<i8> {
        self.pcs.first().map(|pc| pc.raw())
    }
}

#[gen_stub_pymethods]
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
    fn new(pitch_classes: Vec<i8>) -> PyResult<Self> {
        crate::error::require(
            has_unique_elements(&pitch_classes),
            "pitch classes must be unique",
        )?;
        let pcs = pitch_classes
            .into_iter()
            .map(PitchClass::try_new)
            .collect::<PyResult<Vec<_>>>()?;
        Ok(Self { pcs })
    }

    /// Get the pitch classes in this set.
    ///
    /// The returned list contains the pitch classes currently stored by the set.
    /// Values are represented as integers modulo 12, where 0 is C, 1 is C♯/D♭,
    /// and so on.
    ///
    /// Returns:
    ///     list[int]: The pitch classes in the set.
    ///
    /// Example:
    ///     >>> pcs.pitch_classes
    ///     [0, 2, 4, 7]
    #[getter]
    fn pitch_classes(&self) -> Vec<i8> {
        self.pcs_i8()
    }

    /// Compute the normal form of the pitch-class set.
    ///
    /// The normal form is the most "compact" ordering of the set when treated as
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
    ///        Keep only the most "left-packed" (most compact toward the beginning).
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
    #[getter]
    fn normal_form(&self) -> Vec<i8> {
        normal_form(&sorted_pcs_i8(&self.pcs))
    }

    /// Compute the Rahn prime form of the pitch-class set.
    ///
    /// This computes the normal form of the set, then transposes it so that it
    /// begins on 0. For asymmetrical sets, this preserves the orientation of
    /// the set (as in the Wikipedia/Forte A/B columns) rather than collapsing
    /// inversionally related forms to a single Rahn lexicographic minimum.
    ///
    /// Returns:
    ///     list[int]: The prime form of the set as pitch classes in the range 0–11.
    #[getter]
    fn prime_form(&self) -> Vec<i8> {
        let sorted = sorted_pcs_i8(&self.pcs);
        transposed_normal_form(&sorted)
    }

    /// Look up the Forte number for the pitch-class set.
    ///
    /// The set is converted to its oriented Rahn prime form (normal form T0,
    /// preserving inversional orientation) and then matched against the Forte
    /// catalog (Wikipedia/Rahn prime column, including A/B variants).
    ///
    /// Returns:
    ///     str: The Forte number for the set.
    ///
    /// Raises:
    ///     ValueError: If the prime form is not found in the Forte catalog.
    #[getter]
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

    /// Compute the Forte interval-class vector for this pitch-class set.
    ///
    /// The interval-class vector is a six-element count of the unordered pitch-class
    /// intervals present in the set. For each unordered pair of distinct pitch
    /// classes, the smaller directed interval is computed modulo 12, mapped to an
    /// interval class from 1 through 6, and counted at index `ic - 1`.
    ///
    /// Returns:
    ///     list[int]: The interval vector of a pitch-class set, where each position
    ///     corresponds to interval classes 1 through 6.
    ///
    /// Example:
    ///     >>> pcs.interval_vector
    ///     [0, 0, 1, 1, 1, 0]
    #[getter]
    fn interval_vector(&self) -> Vec<i8> {
        interval_class_vector(&self.pcs_i8())
    }

    /// Generate all subsets of the pitch-class set.
    ///
    /// Args:
    ///     min_size (int, optional): Only include subsets with at least this many pitch classes.
    ///         Defaults to ``0`` (full powerset). Any value greater than the number of pitch classes
    ///         in the set will return an empty list.
    ///
    /// Throws:
    ///     OverflowError: If ``min_size`` is negative.
    ///
    /// Returns:
    ///     list[PitchClassSet]: Subsets of the pitch-class set whose length is at least ``min_size``.
    #[pyo3(signature = (min_size = 0))]
    fn subsets(&self, min_size: usize) -> Vec<Self> {
        let n = self.pcs.len();
        (0..(1usize << n))
            .filter(|i| i.count_ones() as usize >= min_size)
            .map(|i| {
                let pcs = self
                    .pcs
                    .iter()
                    .enumerate()
                    .filter(|(j, _)| i & (1usize << j) != 0)
                    .map(|(_, &pc)| pc)
                    .collect();
                Self { pcs }
            })
            .collect()
    }

    /// Count how many pitch classes are shared between this set and its transposition by ``tn``
    /// semitones (``Tn``, mod 12).
    ///
    /// For ``tn ≡ 0 (mod 12)``, no pitches change, so the count is the cardinality
    /// of the set.
    ///
    /// Otherwise the we use the values in the set's interval-class vector and look up the value
    /// according to the interval class of tn.
    ///
    /// For example, if tn is 10, then the interval class is 2, so we look up the
    /// value at index ``1`` in the interval-class vector (i.e. ``iv[1]``).
    /// (It's at index 1, because we don't store interval class 0 in the interval-class vector.)
    ///
    /// Under **tritone** transposition, i.e. ``Tn6``, common tones are **twice** the entry in
    /// the interval-class vector.
    /// See Open Music Theory, "Common Tones under Transposition"
    /// (<https://openmusictheory.github.io/commonTonesUnderTransposition.html>).
    ///
    /// Args:
    ///     tn (int): Transposition level in semitones (any integer -128..=127; reduced mod 12).
    ///
    /// Returns:
    ///     int: Number of common pitch classes between pitch-class set and its transposition by ``tn``.
    fn count_common_tones_under_tn(&self, tn: i8) -> i8 {
        let n = tn.rem_euclid(12);
        if n == 0 {
            return self.pcs.len() as i8;
        }
        let iv = interval_class_vector(&self.pcs_i8());
        let ic = semitones_to_ic(n);
        let mut count = iv[(ic - 1) as usize];
        if n == 6 {
            count *= 2;
        }
        count
    }

    /// Transpose the pitch-class set by a given number of semitones.
    ///
    /// The pitch-class set is transposed by the given number of semitones and the
    /// result is wrapped modulo 12.
    ///
    /// Args:
    ///     tn (int): The number of semitones to transpose by.
    ///         Must be in the range -11 to 11.
    ///
    /// Returns:
    ///     PitchClassSet: The transposed pitch-class set.
    ///
    /// Raises:
    ///     ValueError: If ``tn`` is outside the range -11 to 11.
    ///
    /// Example:
    ///     >>> pcs.transpose_by(1)
    ///     PitchClassSet([1, 3, 5, 8])
    fn transpose_by(&self, tn: i8) -> PyResult<Self> {
        validate_semitones(tn)?;
        Ok(Self {
            pcs: self.pcs.iter().map(|&pc| pc.transpose(tn)).collect(),
        })
    }

    /// Return the chromatic complement of this pitch-class set.
    ///
    /// The complement contains every pitch class in the range 0–11 that is not
    /// in this set. The result is returned in ascending order.
    ///
    /// Returns:
    ///     PitchClassSet: The complement within the twelve pitch classes.
    ///
    /// Example:
    ///     >>> PitchClassSet([0, 1, 2, 3]).complement().forte_num
    ///     '8-1'
    fn complement(&self) -> Self {
        let present: std::collections::HashSet<i8> = self.pcs.iter().map(|pc| pc.raw()).collect();
        let pcs = (0..=11)
            .filter(|pc| !present.contains(pc))
            .map(PitchClass)
            .collect();
        Self { pcs }
    }
}

// ============ Normal form / prime form ============

fn sorted_pcs_i8(pcs: &[PitchClass]) -> Vec<i8> {
    let mut v: Vec<i8> = pcs.iter().copied().map(PitchClass::raw).collect();
    v.sort_unstable();
    v
}

/// Normal form, then transpose so the first pitch class is 0.
fn transposed_normal_form(sorted_pcs: &[i8]) -> Vec<i8> {
    transpose_to_zero(&normal_form(sorted_pcs))
}

/// Transpose a normal-order row so the first pitch class is 0 (`p - p₀` mod 12).
fn transpose_to_zero(line: &[i8]) -> Vec<i8> {
    if line.is_empty() {
        return vec![];
    }
    let t = line[0];
    line.iter().map(|&p| (p - t).rem_euclid(12)).collect()
}

/// Normal form from sorted distinct pitch classes (`src/specs/pitchclass.md`).
fn normal_form(sorted_pcs: &[i8]) -> Vec<i8> {
    match sorted_pcs.len() {
        0 => vec![],
        1 => vec![sorted_pcs[0].rem_euclid(12)],
        n => {
            let rotations = build_rotations(sorted_pcs);
            let candidates = trim_to_min_span(rotations);
            let winners = break_ties(candidates, n);
            wrap_line_to_pcs(
                winners
                    .first()
                    .expect("at least one rotation survives tie-breaking"),
            )
        }
    }
}

/// All cyclic rotations as linear pitch rows (`src/specs/pitchclass.md`).
///
/// `sorted_pcs` must have length ≥ 2.
fn build_rotations(sorted_pcs: &[i8]) -> Vec<Vec<i8>> {
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
fn trim_to_min_span(rotations: Vec<Vec<i8>>) -> Vec<Vec<i8>> {
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
fn wrap_line_to_pcs(line: &[i8]) -> Vec<i8> {
    line.iter().map(|&p| p.rem_euclid(12)).collect()
}

// ============ Interval-class vector & common tones ============

/// Map a pitch interval (in semitones, any representative mod 12) to interval class 0–6.
///
/// `0` means unison/octave (interval ≡ 0 mod 12); classes `1`–`6` are the usual interval classes.
fn semitones_to_ic(semitones: i8) -> i8 {
    let d = semitones.rem_euclid(12);
    if d == 0 {
        0
    } else if d > 6 {
        12 - d
    } else {
        d
    }
}

/// Counts of interval classes 1..=6 for all unordered pairs in the set.
fn interval_class_vector(pcs: &[i8]) -> Vec<i8> {
    let mut sorted = pcs.to_vec();
    sorted.sort_unstable();
    let n = sorted.len();
    let mut counts = [0i8; 6];
    for i in 0..n {
        for j in (i + 1)..n {
            let d = sorted[j] - sorted[i];
            let ic = semitones_to_ic(d);
            counts[(ic - 1) as usize] += 1;
        }
    }
    counts.to_vec()
}

// ============ Free pyfunctions ============

fn map_ordered_set<F: Fn(PitchClass) -> PitchClass>(set: &[i8], f: F) -> PyResult<Vec<i8>> {
    set.iter()
        .map(|&pc| PitchClass::try_new(pc).map(|p| f(p).raw()))
        .collect()
}

fn satisfy_pc_for_forte(forte_num: &str, partial: &[i8]) -> PyResult<Vec<Vec<i8>>> {
    crate::error::require(has_unique_elements(partial), "pitch classes must be unique")?;
    let mut validated_partial = Vec::with_capacity(partial.len());
    for &pc in partial {
        validated_partial.push(PitchClass::try_new(pc)?.raw());
    }

    let prime = prime_form_for_forte_num(forte_num).ok_or_else(|| {
        pyo3::exceptions::PyValueError::new_err(
            "Forte number not found in catalog (expected Wikipedia/Rahn prime column)",
        )
    })?;

    use std::collections::{BTreeSet, HashSet};

    let partial_set: HashSet<i8> = validated_partial.iter().copied().collect();
    let mut solutions: BTreeSet<Vec<i8>> = BTreeSet::new();

    for t in 0..12 {
        let transposed: Vec<i8> = prime.iter().map(|&p| (p + t).rem_euclid(12)).collect();
        let transposed_set: HashSet<i8> = transposed.iter().copied().collect();

        if partial_set.is_subset(&transposed_set) {
            let missing: Vec<i8> = transposed_set.difference(&partial_set).copied().collect();
            if !missing.is_empty() {
                let mut missing_sorted = missing;
                missing_sorted.sort_unstable();
                solutions.insert(missing_sorted);
            }
        }
    }

    Ok(solutions.into_iter().collect())
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
#[gen_stub_pyfunction]
#[pyfunction]
#[pyo3(signature = (pc))]
pub fn invert(pc: i8) -> PyResult<i8> {
    Ok(PitchClass::try_new(pc)?.invert().raw())
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
#[gen_stub_pyfunction]
#[pyfunction]
#[pyo3(signature = (by_semitones, pc))]
pub fn transpose(by_semitones: i8, pc: i8) -> PyResult<i8> {
    validate_semitones(by_semitones)?;
    Ok(PitchClass::try_new(pc)?.transpose(by_semitones).raw())
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
#[gen_stub_pyfunction]
#[pyfunction]
#[pyo3(signature = (by_semitones, ordered_set))]
pub fn transpose_ordered_set(by_semitones: i8, ordered_set: Vec<i8>) -> PyResult<Vec<i8>> {
    validate_semitones(by_semitones)?;
    map_ordered_set(&ordered_set, |pc| pc.transpose(by_semitones))
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
#[gen_stub_pyfunction]
#[pyfunction]
#[pyo3(signature = (ordered_set))]
pub fn invert_ordered_set(ordered_set: Vec<i8>) -> PyResult<Vec<i8>> {
    map_ordered_set(&ordered_set, PitchClass::invert)
}

/// Map a pitch interval (in semitones, any representative mod 12) to interval class 0–6.
///
/// ``0`` means unison/octave (interval ≡ 0 mod 12); classes ``1``–``6`` are the usual
/// interval classes for distinct pitch classes.
#[gen_stub_pyfunction]
#[pyfunction]
#[pyo3(signature = (interval))]
pub fn interval_class(interval: i8) -> i8 {
    semitones_to_ic(interval)
}

/// Find pitch-class completions for a Forte set class.
///
/// Given a Forte number (e.g. ``"3-11B"``) and a list of distinct pitch classes,
/// this function returns all distinct ways to **add** pitch classes so that the
/// resulting set has that Forte number (using the same catalog as
/// :py:meth:`allegro.pitchclass.PitchClassSet.forte_num`).
///
/// The function enumerates all 12 transpositions of the set's Rahn prime form and
/// keeps those transpositions that contain the given partial set. For each such
/// transposition it returns the sorted list of *missing* pitch classes. Results
/// are de-duplicated and returned in lexicographic order.
///
/// Args:
///     forte_num (str): Forte number label (e.g. ``"3-11B"``).
///     pitch_classes (list[int]): Partial pitch-class collection, each 0–11 and unique.
///
/// Returns:
///     list[list[int]]: Each inner list is a sorted collection of pitch classes
///         that can be added so that ``pitch_classes + missing`` has Forte number
///         ``forte_num``. Returns an empty list if there are no such completions
///         (including when the partial set already realizes the set class).
///
/// Raises:
///     ValueError: If ``forte_num`` is not found in the Forte catalog.
///     ValueError: If any pitch class is outside 0–11 or duplicated.
#[gen_stub_pyfunction]
#[pyfunction]
#[pyo3(signature = (forte_num, pitch_classes))]
pub fn satisfy_pc(forte_num: &str, pitch_classes: Vec<i8>) -> PyResult<Vec<Vec<i8>>> {
    satisfy_pc_for_forte(forte_num, &pitch_classes)
}
