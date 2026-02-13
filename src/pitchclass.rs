use pyo3::prelude::*;

fn semitone_guard(semitones: i8) -> PyResult<()> {
    if semitones < -11 || semitones > 11 {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "by_semitones must be within the range (-11)-11",
        ));
    }
    Ok(())
}

fn pc_guard(pc: i8) -> PyResult<()> {
    if pc < 0 || pc > 11 {
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
