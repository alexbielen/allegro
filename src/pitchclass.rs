use pyo3::prelude::*;

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
