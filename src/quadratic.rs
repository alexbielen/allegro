use pyo3::prelude::*;

use crate::py_stub::gen_stub_pyfunction;

use crate::error::require;

/// Standard Earth surface gravity in m/s².
const EARTH_GRAVITY: f64 = 9.80665;

/// Default maximum simulation time in seconds when `max_time` is None.
const DEFAULT_MAX_TIME: f64 = 10.0;

/// Compute time until next ground impact from a parabolic segment.
/// h(t) = h0 + v0*t - 0.5*g*t^2 = 0  =>  t = (v0 + sqrt(v0^2 + 2*g*h0)) / g
fn time_to_impact(h0: f64, v0: f64, g: f64) -> Option<f64> {
    let disc = v0 * v0 + 2.0 * g * h0;
    if disc < 0.0 {
        return None;
    }
    let t = (v0 + disc.sqrt()) / g;
    if t > 0.0 && t.is_finite() {
        Some(t)
    } else {
        None
    }
}

/// Height at time `dt` from segment start: h(dt) = h0 + v0*dt - 0.5*g*dt^2
fn height_at(h0: f64, v0: f64, g: f64, dt: f64) -> f64 {
    (h0 + v0 * dt - 0.5 * g * dt * dt).max(0.0)
}

#[gen_stub_pyfunction]
#[pyfunction]
#[pyo3(signature = (height, velocity, gravity=None, elasticity=1.0, samples_per_second=100.0, max_time=None))]
/// Simulate a bouncing ball and return sampled (height, time) points.
///
/// Physics: vertical motion with gravity; at each ground impact the vertical
/// velocity is multiplied by ``-elasticity`` (coefficient of restitution).
///
/// Args:
///     height (float): Initial height in meters (>= 0).
///     velocity (float): Initial vertical velocity in m/s (positive = up).
///     gravity (float | None): Gravitational acceleration in m/s²; None uses Earth default (9.80665).
///     elasticity (float): Coefficient of restitution in [0, 1] (1 = perfectly elastic).
///     samples_per_second (float): Sampling rate in Hz (must be > 0).
///     max_time (float | None): Simulation end time in seconds; None uses default (10.0).
///
/// Returns:
///     list[tuple[float, float]]: List of (height, time) tuples at uniform time steps.
///
/// Raises:
///     ValueError: If height < 0, samples_per_second <= 0, max_time <= 0, or elasticity not in [0, 1].
pub fn quadratic_bouncing_ball(
    height: f64,
    velocity: f64,
    gravity: Option<f64>,
    elasticity: f64,
    samples_per_second: f64,
    max_time: Option<f64>,
) -> PyResult<Vec<(f64, f64)>> {
    let g = gravity.unwrap_or(EARTH_GRAVITY);
    let end_time = max_time.unwrap_or(DEFAULT_MAX_TIME);

    require(
        height.is_finite() && height >= 0.0,
        "height must be finite and >= 0",
    )?;
    require(
        samples_per_second.is_finite() && samples_per_second > 0.0,
        "samples_per_second must be finite and > 0",
    )?;
    require(
        end_time.is_finite() && end_time > 0.0,
        "max_time must be finite and > 0",
    )?;
    require(
        elasticity.is_finite() && (0.0..=1.0).contains(&elasticity),
        "elasticity must be in [0, 1]",
    )?;
    require(g.is_finite() && g > 0.0, "gravity must be finite and > 0")?;

    let dt = 1.0 / samples_per_second;
    let mut out: Vec<(f64, f64)> = Vec::new();

    let (mut seg_t0, mut seg_h0, mut seg_v0) = if height == 0.0 && velocity <= 0.0 {
        // At ground with downward/zero velocity: immediate bounce
        (0.0, 0.0, -elasticity * velocity)
    } else {
        (0.0, height, velocity)
    };

    while seg_t0 < end_time {
        let impact_dt = time_to_impact(seg_h0, seg_v0, g);
        let segment_end_t = match impact_dt {
            Some(t) if seg_t0 + t <= end_time => seg_t0 + t,
            Some(_t) => {
                // Impact is after end_time; sample up to end_time only
                let mut t_sample = seg_t0;
                while t_sample <= end_time {
                    let local_dt = t_sample - seg_t0;
                    let h = height_at(seg_h0, seg_v0, g, local_dt);
                    out.push((h, t_sample));
                    t_sample += dt;
                }
                break;
            }
            None => {
                // No impact (e.g. going up forever); sample to end_time
                let mut t_sample = seg_t0;
                while t_sample <= end_time {
                    let local_dt = t_sample - seg_t0;
                    let h = height_at(seg_h0, seg_v0, g, local_dt);
                    out.push((h, t_sample));
                    t_sample += dt;
                }
                break;
            }
        };

        // Sample from seg_t0 up to (but not past) segment_end_t at dt steps
        let mut t_sample = seg_t0;
        while t_sample < segment_end_t {
            let local_dt = t_sample - seg_t0;
            let h = height_at(seg_h0, seg_v0, g, local_dt);
            out.push((h, t_sample));
            t_sample += dt;
        }

        let impact_dt = segment_end_t - seg_t0;
        let v_at_impact = seg_v0 - g * impact_dt;
        seg_v0 = -elasticity * v_at_impact;
        if seg_v0 <= 0.0 {
            // Ball stops (elasticity 0 or low); sample rest at height 0 to end_time
            let mut t_sample = segment_end_t;
            while t_sample <= end_time {
                out.push((0.0, t_sample));
                t_sample += dt;
            }
            break;
        }
        seg_t0 = segment_end_t;
        seg_h0 = 0.0;
    }

    Ok(out)
}
