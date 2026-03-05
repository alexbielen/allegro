"""Tests for the boids flocking simulation (Universe, Dimensions, Boid).

Aligned with src/specs/boids.md and the current Rust implementation in src/boids.rs.
"""

import math

import pytest

from allegro.boids import (
    Boid,
    Dimensions,
    Universe,
    create_boids_with_random_positions,
)


def _dims(size: float = 500.0) -> Dimensions:
    """World bounds centered at origin. Dimensions(x_min, x_max, y_min, y_max, z_min, z_max)."""
    return Dimensions(-size, size, -size, size, -size, size)


def _vec_length(x: float, y: float, z: float) -> float:
    return math.sqrt(x * x + y * y + z * z)


def _make_universe(
    flock: list,
    dimensions: Dimensions,
    *,
    cohesion_factor: float = 0.01,
    separation_distance: float = 100.0,
    alignment_factor: float = 0.125,
    bound_steer: float = 10.0,
    speed_limit: float | None = None,
) -> Universe:
    """Build Universe with current API: (flock, dimensions, ...)."""
    return Universe(
        flock,
        dimensions,
        cohesion_factor,
        separation_distance,
        alignment_factor,
        bound_steer,
        speed_limit,
    )


class TestUniverseStep:
    """Basic step() behavior and return shape."""

    def test_step_returns_list_of_boids(self) -> None:
        flock = [
            Boid([0.0, 0.0, 0.0], [0.0, 0.0, 0.0]),
            Boid([1.0, 0.0, 0.0], [0.0, 0.0, 0.0]),
        ]
        universe = _make_universe(flock, _dims())
        result = universe.step()
        assert len(result) == 2
        for b in result:
            p = b.position()
            v = b.velocity()
            assert len(p) == 3 and all(isinstance(x, (int, float)) for x in p)
            assert len(v) == 3 and all(isinstance(x, (int, float)) for x in v)

    def test_step_updates_positions(self) -> None:
        flock = [Boid([0.0, 0.0, 0.0], [1.0, 0.0, 0.0])]
        universe = _make_universe(flock, _dims())
        result = universe.step()
        assert result[0].position() == pytest.approx((1.0, 0.0, 0.0), abs=1e-5)


class TestCohesion:
    """Rule 1: boids steer toward perceived center of mass of neighbors."""

    def test_two_boids_with_zero_velocity_move_toward_each_other(self) -> None:
        # Cohesion sanity check (spec): two boids at known positions, zero initial
        # velocity; after one step they move slightly toward each other.
        # Use separation_distance smaller than initial gap so separation doesn't
        # apply (separation only pushes when distance < separation_distance).
        flock = [
            Boid([0.0, 0.0, 0.0], [0.0, 0.0, 0.0]),
            Boid([100.0, 0.0, 0.0], [0.0, 0.0, 0.0]),
        ]
        universe = _make_universe(
            flock,
            _dims(),
            cohesion_factor=0.01,
            separation_distance=10.0,  # < 100 so separation is inactive
            alignment_factor=0.0,
        )

        initial_distance = _vec_length(
            flock[0].position()[0] - flock[1].position()[0],
            flock[0].position()[1] - flock[1].position()[1],
            flock[0].position()[2] - flock[1].position()[2],
        )
        result = universe.step()
        new_distance = _vec_length(
            result[0].position()[0] - result[1].position()[0],
            result[0].position()[1] - result[1].position()[1],
            result[0].position()[2] - result[1].position()[2],
        )
        assert new_distance < initial_distance

class TestSeparation:
    """Rule 2: boids steer away from close neighbors."""

    def test_two_close_boids_move_apart(self) -> None:
        # Separation sanity check (spec): two boids very close; after one step they move apart.
        flock = [
            Boid([0.0, 0.0, 0.0], [0.0, 0.0, 0.0]),
            Boid([5.0, 0.0, 0.0], [0.0, 0.0, 0.0]),
        ]
        universe = _make_universe(
            flock,
            _dims(),
            cohesion_factor=0.001,
            separation_distance=50.0,
            alignment_factor=0.0,
        )
        initial_distance = 5.0
        result = universe.step()
        p0 = result[0].position()
        p1 = result[1].position()
        new_distance = _vec_length(p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
        assert new_distance > initial_distance


class TestAlignment:
    """Rule 3: boids try to match velocity with near boids."""

    def test_stationary_boid_aligns_toward_flock_velocity_over_steps(self) -> None:
        # Alignment sanity check (spec): one boid stationary, rest moving in same
        # direction; stationary boid's velocity rotates toward flock velocity.
        flock = [
            Boid([0.0, 0.0, 0.0], [0.0, 0.0, 0.0]),
            Boid([50.0, 0.0, 0.0], [10.0, 0.0, 0.0]),
            Boid([100.0, 0.0, 0.0], [10.0, 0.0, 0.0]),
        ]
        universe = _make_universe(
            flock,
            _dims(),
            cohesion_factor=0.01,
            separation_distance=200.0,
            alignment_factor=0.125,
        )
        # After several steps, boid 0 should have positive x velocity (aligning with flock).
        for _ in range(20):
            result = universe.step()
        v0 = result[0].velocity()
        assert v0[0] > 0.0


class TestSpeedLimit:
    """Speed limiting clamps velocity magnitude."""

    def test_velocity_magnitude_never_exceeds_speed_limit(self) -> None:
        # Speed limit (spec): scenario where raw rules would exceed speed_limit;
        # final speed must be clamped.
        flock = [Boid([0.0, 0.0, 0.0], [100.0, 0.0, 0.0])]
        universe = _make_universe(
            flock,
            _dims(),
            cohesion_factor=0.0,
            separation_distance=1000.0,
            alignment_factor=0.0,
            speed_limit=10.0,
        )
        result = universe.step()
        v = result[0].velocity()
        speed = _vec_length(v[0], v[1], v[2])
        assert speed == pytest.approx(10.0, abs=1e-4)


class TestBounds:
    """Soft world bounds steer boids back inward."""

    def test_boid_outside_bounds_is_steered_inward_over_steps(self) -> None:
        # Bounds (spec): boid outside Dimensions is steered inward over several steps.
        dims = Dimensions(-100.0, 100.0, -100.0, 100.0, -100.0, 100.0)
        flock = [Boid([-150.0, 0.0, 0.0], [0.0, 0.0, 0.0])]
        universe = _make_universe(
            flock,
            dims,
            cohesion_factor=0.0,
            separation_distance=1000.0,
            alignment_factor=0.0,
        )
        result = universe.step()
        x_after_one = result[0].position()[0]
        # bound_steer adds +10 to vx when x < x_min, so position becomes -150 + 10 = -140
        assert x_after_one > -150.0
        assert x_after_one == pytest.approx(-140.0, abs=1e-4)


class TestCreateBoidsWithRandomPositions:
    """Helper to create a flock of boids randomly placed within Dimensions."""

    def test_returns_flock_of_requested_size(self) -> None:
        dims = _dims(100.0)
        flock = create_boids_with_random_positions(10, dims)
        assert len(flock) == 10
        for b in flock:
            p = b.position()
            v = b.velocity()
            assert len(p) == 3 and len(v) == 3
            assert v == pytest.approx((0.0, 0.0, 0.0), abs=1e-9)

    def test_positions_within_dimensions(self) -> None:
        dims = _dims(50.0)
        flock = create_boids_with_random_positions(20, dims)
        for b in flock:
            x, y, z = b.position()
            assert -50.0 <= x <= 50.0
            assert -50.0 <= y <= 50.0
            assert -50.0 <= z <= 50.0


class TestDimensionsValidation:
    """Dimensions requires min < max for each axis."""

    def test_valid_dimensions_construct(self) -> None:
        dims = Dimensions(-500.0, 500.0, -500.0, 500.0, -500.0, 500.0)
        assert dims.x_min < dims.x_max and dims.y_min < dims.y_max and dims.z_min < dims.z_max

    def test_x_min_ge_x_max_raises(self) -> None:
        with pytest.raises(ValueError, match="x_min must be less than x_max"):
            Dimensions(500.0, -500.0, -500.0, 500.0, -500.0, 500.0)
        with pytest.raises(ValueError, match="x_min must be less than x_max"):
            Dimensions(0.0, 0.0, -500.0, 500.0, -500.0, 500.0)

    def test_y_min_ge_y_max_raises(self) -> None:
        with pytest.raises(ValueError, match="y_min must be less than y_max"):
            Dimensions(-500.0, 500.0, 500.0, -500.0, -500.0, 500.0)

    def test_z_min_ge_z_max_raises(self) -> None:
        with pytest.raises(ValueError, match="z_min must be less than z_max"):
            Dimensions(-500.0, 500.0, -500.0, 500.0, 0.0, 0.0)
