use pyo3::prelude::*;

mod numbers;

/// A Python module implemented in Rust.
#[pymodule]
fn allegro(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(numbers::sum_as_string, m)?)?;
    m.add_function(wrap_pyfunction!(numbers::fit, m)?)?;
    m.add_class::<numbers::FitMode>()?;
    Ok(())
}
