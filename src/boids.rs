//! Boids flocking simulation types and rules.
//!
//! See `src/specs/boids.md` for the full specification.

use glam::Vec3;
use pyo3::prelude::*;

use crate::py_stub::{gen_stub_pyclass, gen_stub_pyfunction, gen_stub_pymethods};
use pyo3::pyfunction;
use crate::error::require;

/// ``Dimensions`` describes the axis-bounded bounding box that contains the
/// flock. The bounds are used by ``Universe`` to steer boids back toward the
/// interior when they move outside coordinates.
///
/// Parameters:
///     x_min (float):
///         Minimum x coordinate.
///     x_max (float):
///         Maximum x coordinate.
///     y_min (float):
///         Minimum y coordinate.
///     y_max (float):
///         Maximum y coordinate.
///     z_min (float):
///         Minimum z coordinate.
///     z_max (float):
///         Maximum z coordinate.
///
/// Attributes:
///     x_min (float):
///         Minimum x coordinate.
///     x_max (float):
///         Maximum x coordinate.
///     y_min (float):
///         Minimum y coordinate.
///     y_max (float):
///         Maximum y coordinate.
///     z_min (float):
///         Minimum z coordinate.
///     z_max (float):
///         Maximum z coordinate.
///
/// Raises:
///     ValueError: If any minimum is greater than or equal to its maximum
///     (e.g. x_min >= x_max).
///
/// Examples:
///     >>> dims = Dimensions(-500.0, 500.0, -500.0, 500.0, -500.0, 500.0)
#[gen_stub_pyclass]
#[pyclass]
#[derive(Debug, Clone)]
pub struct Dimensions {
    #[pyo3(get, set)]
    pub x_min: f32,
    #[pyo3(get, set)]
    pub x_max: f32,
    #[pyo3(get, set)]
    pub y_min: f32,
    #[pyo3(get, set)]
    pub y_max: f32,
    #[pyo3(get, set)]
    pub z_min: f32,
    #[pyo3(get, set)]
    pub z_max: f32,
}

#[gen_stub_pymethods]
#[pymethods]
impl Dimensions {
    #[new]
    #[pyo3(signature = (x_min, x_max, y_min, y_max, z_min, z_max))]
    fn new(
        x_min: f32,
        x_max: f32,
        y_min: f32,
        y_max: f32,
        z_min: f32,
        z_max: f32,
    ) -> PyResult<Self> {
        require(x_min < x_max, "x_min must be less than x_max")?;
        require(y_min < y_max, "y_min must be less than y_max")?;
        require(z_min < z_max, "z_min must be less than z_max")?;
        Ok(Self {
            x_min,
            x_max,
            y_min,
            y_max,
            z_min,
            z_max,
        })
    }
}

/// Represent a boids simulation and its rule parameters.
///
/// ``Universe`` stores the flock, the world bounds, and the parameters that
/// control cohesion, separation, alignment, boundary steering, and optional
/// speed limiting.
///
/// Call ``step()`` to advance the simulation by one discrete time step.
///
/// Parameters:
///     flock (list[Boid]):
///         Initial flock of boids.
///     dimensions (Dimensions):
///         World bounds for the simulation.
///     cohesion_factor (float):
///         Strength of cohesion. Higher values pull boids more strongly toward
///         the perceived center of mass of the flock.
///     separation_distance (float):
///         Distance threshold used for separation. Boids closer than this
///         distance push away from one another.
///     alignment_factor (float):
///         Strength of alignment. Higher values steer boids more strongly
///         toward the perceived average flock velocity.
///     bound_steer (float):
///         Fixed steering amount applied when a boid crosses a world boundary.
///     speed_limit (float, optional):
///         Maximum allowed speed magnitude. If ``None``, no speed limit is
///         applied.
///
/// Notes:
///     The simulation applies the following updates in order:
///
///     1. Fly towards perceived center of mass
///     2. Move away from close by objects
///     3. Match perceived speed of flock
///     4. Bound position
///     5. Limit velocity
///     6. Update position
///
/// Examples:
///     >>> dims = Dimensions(-500.0, 500.0, -500.0, 500.0, -500.0, 500.0)
///     >>> flock = [Boid([0.0, 0.0, 0.0], [1.0, 0.0, 0.0]), Boid([100.0, 0.0, 0.0], [0.0, 0.0, 0.0])]
///     >>> universe = Universe(
///     ...     flock,
///     ...     dims,
///     ...     cohesion_factor=0.01,
///     ...     separation_distance=100.0,
///     ...     alignment_factor=0.125,
///     ...     bound_steer=10.0,
///     ...     speed_limit=10.0,
///     ... )
#[gen_stub_pyclass]
#[pyclass]
pub struct Universe {
    flock: Vec<Boid>,
    dimensions: Dimensions,
    cohesion_factor: f32,
    separation_distance: f32,
    alignment_factor: f32,
    bound_steer: f32,
    speed_limit: Option<f32>,
}

#[gen_stub_pymethods]
#[pymethods]
impl Universe {
    #[new]
    #[pyo3(signature = (flock, dimensions, cohesion_factor, separation_distance, alignment_factor, bound_steer, speed_limit=None))]
    fn new(
        flock: Vec<Boid>,
        dimensions: Dimensions,
        cohesion_factor: f32,
        separation_distance: f32,
        alignment_factor: f32,
        bound_steer: f32,
        speed_limit: Option<f32>,
    ) -> PyResult<Self> {
        Ok(Self {
            flock,
            dimensions,
            cohesion_factor,
            separation_distance,
            alignment_factor,
            bound_steer,
            speed_limit,
        })
    }

    /// Advance the flock by one time step.
    ///
    /// This method applies the boids rules to every boid in the universe,
    /// updates velocities, then updates positions using the new velocities.
    /// The updated flock is returned as a new list of ``Boid`` objects.
    ///
    /// Returns:
    ///     list[Boid]:
    ///         The updated flock after one simulation step.
    ///
    /// Notes:
    ///     Each boid is updated using the current flock state and the
    ///     universe parameters. Positions are advanced by adding the updated
    ///     velocity to the current position.
    ///
    /// Examples:
    ///     >>> updated_flock = universe.step()
    ///     >>> first_boid = updated_flock[0]
    ///     >>> first_boid.position()
    fn step(&mut self) -> PyResult<Vec<Boid>> {
        let n = self.flock.len();
        for i in 0..n {
            let rule_1_offset = self.fly_towards_perceived_center_of_mass(i);
            let rule_2_offset = self.move_away_from_close_by_objects(i);
            let rule_3_offset = self.match_perceived_speed_of_flock(i);
            let bound_position_offset = self.bound_position(i);
            let limit_velocity_offset = self.limit_velocity(i);
            let boid = &mut self.flock[i];
            boid.velocity += rule_1_offset
                + rule_2_offset
                + rule_3_offset
                + bound_position_offset
                + limit_velocity_offset;
            boid.position += boid.velocity;
        }
        Ok(self.flock.clone())
    }
}

impl Universe {
    /// Return the cohesion offset for a boid.
    ///
    /// Cohesion steers the boid toward the perceived center of mass of the
    /// other boids in the flock.
    fn fly_towards_perceived_center_of_mass(&self, index: usize) -> Vec3 {
        let n = self.flock.len();
        if n <= 1 {
            return Vec3::ZERO;
        }
        let mut sum = Vec3::ZERO;
        for (j, boid) in self.flock.iter().enumerate() {
            if j != index {
                sum += boid.position;
            }
        }
        let count = (n - 1) as f32;
        let perceived_center_of_mass = sum / count;
        let p_i = self.flock[index].position;
        (perceived_center_of_mass - p_i) * self.cohesion_factor
    }

    /// Return the separation offset for a boid.
    ///
    /// Separation steers the boid away from nearby boids that are closer than
    /// ``separation_distance``.
    fn move_away_from_close_by_objects(&self, index: usize) -> Vec3 {
        let n = self.flock.len();
        if n <= 1 {
            return Vec3::ZERO;
        }

        let p_i = self.flock[index].position;
        let mut separation_offset = Vec3::ZERO;
        let threshold_sq = self.separation_distance * self.separation_distance;

        for (j, boid) in self.flock.iter().enumerate() {
            if j != index {
                let offset = boid.position - p_i;
                if offset.length_squared() < threshold_sq {
                    separation_offset -= offset;
                }
            }
        }

        separation_offset
    }

    /// Return the alignment offset for a boid.
    ///
    /// Alignment steers the boid toward the perceived average velocity of the
    /// other boids in the flock.
    fn match_perceived_speed_of_flock(&self, index: usize) -> Vec3 {
        let n = self.flock.len();
        if n <= 1 {
            return Vec3::ZERO;
        }

        let mut sum = Vec3::ZERO;
        for (j, boid) in self.flock.iter().enumerate() {
            if j != index {
                sum += boid.velocity;
            }
        }

        let count = (n - 1) as f32;
        let perceived_velocity = sum / count;
        let v_i = self.flock[index].velocity;
        (perceived_velocity - v_i) * self.alignment_factor
    }

    /// Return the velocity correction needed to enforce the speed limit.
    ///
    /// If ``speed_limit`` is set and the boid is moving faster than that
    /// limit, this returns the offset needed to scale the velocity back to
    /// the allowed magnitude. Otherwise, it returns zero.
    fn limit_velocity(&self, index: usize) -> Vec3 {
        let Some(limit) = self.speed_limit else {
            return Vec3::ZERO;
        };

        let v = self.flock[index].velocity;
        let speed_sq = v.length_squared();
        if speed_sq == 0.0 {
            return Vec3::ZERO;
        }

        let limit_sq = limit * limit;
        if speed_sq <= limit_sq {
            return Vec3::ZERO;
        }

        let speed = speed_sq.sqrt();
        let scale = limit / speed;
        v * scale - v
    }

    /// Return the boundary steering offset for a boid.
    ///
    /// When a boid lies outside the world bounds, this applies a fixed steer
    /// back toward the interior along any axis that exceeds the allowed range.
    fn bound_position(&self, index: usize) -> Vec3 {
        let mut steer = Vec3::ZERO;
        let p = self.flock[index].position;

        if p.x < self.dimensions.x_min {
            steer.x += self.bound_steer;
        } else if p.x > self.dimensions.x_max {
            steer.x -= self.bound_steer;
        }

        if p.y < self.dimensions.y_min {
            steer.y += self.bound_steer;
        } else if p.y > self.dimensions.y_max {
            steer.y -= self.bound_steer;
        }

        if p.z < self.dimensions.z_min {
            steer.z += self.bound_steer;
        } else if p.z > self.dimensions.z_max {
            steer.z -= self.bound_steer;
        }

        steer
    }
}

/// Represent a single boid in the flock.
///
/// A ``Boid`` stores a 3D position and a 3D velocity.
///
/// Parameters:
///     position (list[float]):
///         Initial position as ``[x, y, z]``. Must contain exactly 3 elements.
///     velocity (list[float]):
///         Initial velocity as ``[vx, vy, vz]``. Must contain exactly 3 elements.
///
/// Raises:
///     ValueError:
///         If ``position`` does not contain exactly 3 elements.
///     ValueError:
///         If ``velocity`` does not contain exactly 3 elements.
///
/// Examples:
///     >>> boid = Boid([0.0, 0.0, 0.0], [1.0, 0.0, 0.0])
///     >>> boid.position()
///     (0.0, 0.0, 0.0)
///     >>> boid.velocity()
///     (1.0, 0.0, 0.0)
#[gen_stub_pyclass]
#[pyclass]
#[derive(Clone)]
pub struct Boid {
    pub position: Vec3,
    pub velocity: Vec3,
}

#[gen_stub_pymethods]
#[pymethods]
impl Boid {
    #[new]
    #[pyo3(signature = (position, velocity))]
    fn new(position: Vec<f32>, velocity: Vec<f32>) -> PyResult<Self> {
        if position.len() != 3 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "position must have exactly 3 elements (x, y, z)",
            ));
        }
        if velocity.len() != 3 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "velocity must have exactly 3 elements (vx, vy, vz)",
            ));
        }
        Ok(Self {
            position: Vec3::new(position[0], position[1], position[2]),
            velocity: Vec3::new(velocity[0], velocity[1], velocity[2]),
        })
    }

    /// Return the boid position as ``(x, y, z)``.
    ///
    /// Returns:
    ///     tuple[float, float, float]:
    ///         The current position.
    fn position(&self) -> (f32, f32, f32) {
        (self.position.x, self.position.y, self.position.z)
    }

    /// Return the boid velocity as ``(vx, vy, vz)``.
    ///
    /// Returns:
    ///     tuple[float, float, float]:
    ///         The current velocity.
    fn velocity(&self) -> (f32, f32, f32) {
        (self.velocity.x, self.velocity.y, self.velocity.z)
    }
}

impl Boid {
    /// Create a boid with a random in-bounds position and zero velocity.
    ///
    /// This helper is used internally by
    /// ``create_boids_with_random_positions()``.
    pub fn new_with_random_position(dimensions: &Dimensions) -> Self {
        let position = Vec3::new(
            rand::random_range(dimensions.x_min..=dimensions.x_max),
            rand::random_range(dimensions.y_min..=dimensions.y_max),
            rand::random_range(dimensions.z_min..=dimensions.z_max),
        );
        let velocity = Vec3::ZERO;
        Self { position, velocity }
    }
}

/// Create boids with random positions inside the given dimensions.
///
/// This is a convenience function for initializing a flock. Each boid is
/// placed uniformly at random within the bounding box defined by
/// ``dimensions`` and starts with zero velocity.
///
/// Parameters:
///     flock_size (int):
///         Number of boids to create.
///     dimensions (Dimensions):
///         World bounds used to generate initial positions.
///
/// Returns:
///     list[Boid]:
///         A list of boids with random in-bounds positions and zero velocity.
///
/// Examples:
///     >>> dims = Dimensions(-100.0, 100.0, -100.0, 100.0, -100.0, 100.0)
///     >>> flock = create_boids_with_random_positions(10, dims)
///     >>> len(flock)
///     10
#[gen_stub_pyfunction]
#[pyfunction]
#[pyo3(signature = (flock_size, dimensions))]
pub fn create_boids_with_random_positions(
    flock_size: usize,
    dimensions: &Bound<'_, Dimensions>,
) -> PyResult<Vec<Boid>> {
    let dims = dimensions.borrow().clone();
    Ok((0..flock_size)
        .map(|_| Boid::new_with_random_position(&dims))
        .collect())
}
