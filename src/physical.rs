use pyo3::prelude::*;

use crate::py_stub::gen_stub_pyfunction;

use crate::error::require;

/// Standard Earth surface gravity in m/s².
const EARTH_GRAVITY: f64 = 9.80665;

/// Default maximum simulation time in seconds when `max_time` is None.
const DEFAULT_MAX_TIME: f64 = 10.0;

/// Generate a bouncing-ball curve sampled at regular time intervals.
///
/// This function returns a list of ``(height, time)`` pairs describing vertical
/// motion under constant gravity. When the ball hits the ground, it bounces back up with a velocity
/// scaled by the `elasticity` parameter. Very small rebounds are suppressed so the ball settles to rest.
///
/// Parameters:
///     height (float):
///         Initial height. Must be finite and ``>= 0``.
///     velocity (float):
///         Initial vertical velocity. Positive values move upward; negative
///         values move downward. Must be finite.
///     gravity (float, optional):
///         Gravitational acceleration (positive). If ``None``, standard Earth
///         gravity (9.80665 m/s²) is used.
///     elasticity (float, default=1.0):
///         Coefficient of restitution in ``[0, 1]``. Controls how much velocity
///         is retained after each impact. ``1.0`` is perfectly elastic (no decay) so
///         the ball would bounce without losing energy, similar to an LFO, where as
///         ``0.0`` removes all energy at the first impact.
///     samples_per_second (float, default=100.0):
///         Sampling rate in Hz. Must be finite and ``> 0``.
///     max_time (float, optional):
///         Maximum duration in seconds. Must be finite and ``> 0``. If ``None``,
///         a default duration is used.
///
/// Returns:
///     list[tuple[float, float]]:
///         Samples of ``(height, time)``. Heights are guaranteed to be
///         non-negative. Times increase according to the sampling rate from ``0`` up to
///         ``max_time``.
///
/// Raises:
///     ValueError:
///         If any argument is non-finite, or if any constraint is violated:
///
///         - ``height < 0``
///         - ``gravity <= 0``
///         - ``elasticity`` not between 0 and 1 `
///         - ``samples_per_second <= 0``
///         - ``max_time <= 0``
///
/// Notes:
///     The output is computed using a semi-implicit (symplectic) Euler method.
///     This produces stable, predictable curves suitable for control and
///     modulation.
///
/// Examples:
///     Basic usage (default gravity, perfectly elastic):
///
///     >>> samples = bouncing_ball(height=1.0, velocity=0.0)
///
///     A decaying gesture:
///
///     >>> samples = bouncing_ball(height=1.0, velocity=0.0, elasticity=0.8, max_time=3.0)
///
///     Slower motion under reduced gravity:
///
///     >>> samples = bouncing_ball(height=1.0, velocity=0.0, gravity=1.62, max_time=5.0)
#[gen_stub_pyfunction]
#[pyfunction]
#[pyo3(signature = (height, velocity, gravity=None, elasticity=1.0, samples_per_second=100.0, max_time=None))]
pub fn bouncing_ball(
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
    require(velocity.is_finite(), "velocity must be finite")?;
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

    // Time step between samples.
    let dt = 1.0 / samples_per_second;

    // Output samples.
    let mut out: Vec<(f64, f64)> = Vec::new();

    // Current simulation state.
    let mut t = 0.0;
    let mut h = height;
    let mut v = velocity;

    // A small "sleep" threshold to avoid micro-bounces.
    let sleep_speed = 1e-6;

    while t <= end_time {
        // Record current state at this sample time.
        out.push((h.max(0.0), t));

        // If we're resting on the ground and not moving upward, the ball can stay asleep.
        if h == 0.0 && v.abs() <= sleep_speed {
            // Just advance time; state remains at rest.
            t += dt;
            continue;
        }

        // Semi-implicit Euler
        // 1) update velocity from acceleration
        v -= g * dt;

        // 2) update position from new velocity
        h += v * dt;

        // If we're on the ground and moving downward, apply restitution impulse
        // (covers both the impact case above and the exact-on-ground case).
        if h <= 0.0 && v < 0.0 {
            h = 0.0;
            v *= -elasticity;
            if v.abs() <= sleep_speed {
                v = 0.0;
            }
        }

        // Advance time.
        t += dt;
    }

    Ok(out)
}
