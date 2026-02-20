use pyo3::prelude::*;

pub fn require(ok: bool, msg: &'static str) -> PyResult<()> {
    if ok {
        Ok(())
    } else {
        Err(pyo3::exceptions::PyValueError::new_err(msg))
    }
}
