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
    Ok((12 - pc).rem_euclid(12))
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
    Ok((by_semitones + pc).rem_euclid(12))
}

/// Validate each pc in the set, then map `f` over it and collect. Shared by
/// transpose_ordered_set and invert_ordered_set.
fn map_ordered_set<F>(ordered_set: &[i8], f: F) -> PyResult<Vec<i8>>
where
    F: Fn(i8) -> PyResult<i8>,
{
    for pc in ordered_set {
        pc_guard(*pc)?;
    }
    ordered_set
        .iter()
        .map(|pc| f(*pc))
        .collect::<Result<Vec<i8>, PyErr>>()
}

#[pyfunction]
#[pyo3(signature = (by_semitones, ordered_set))]
pub fn transpose_ordered_set(by_semitones: i8, ordered_set: Vec<i8>) -> PyResult<Vec<i8>> {
    semitone_guard(by_semitones)?;
    map_ordered_set(&ordered_set, |pc| transpose(by_semitones, pc))
}

#[pyfunction]
#[pyo3(signature = (ordered_set))]
pub fn invert_ordered_set(ordered_set: Vec<i8>) -> PyResult<Vec<i8>> {
    map_ordered_set(&ordered_set, invert)
}
