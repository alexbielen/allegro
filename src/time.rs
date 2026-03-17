use fraction::{GenericFraction, ToPrimitive};
use pyo3::prelude::*;

type Rhythm = GenericFraction<i16>;

#[pyfunction]
#[pyo3(signature = (bpm))]
pub fn bpm_to_seconds(bpm: f64) -> f64 {
    bpm_to_seconds_impl(bpm)
}

fn bpm_to_seconds_impl(bpm: f64) -> f64 {
    60.0 / bpm
}

fn rhythm_to_seconds_impl(rhy: Rhythm, bpm: f64) -> f64 {
    let rhy_f64 = rhy
        .to_f64()
        .expect("Rhythm value could not be represented as f64");
    rhy_f64 * 4.0 * bpm_to_seconds_impl(bpm)
}

#[pyfunction]
#[pyo3(signature = (num, den, bpm))]
pub fn rhythm_to_seconds(num: i16, den: i16, bpm: f64) -> f64 {
    let rhy = Rhythm::new(num, den);
    rhythm_to_seconds_impl(rhy, bpm)
}
