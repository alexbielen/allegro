import pytest

from allegro.quadratic import quadratic_bouncing_ball

# TODO: These tests might be crap -- need to rewrite them.


class TestQuadraticBouncingBall:
    def test_first_point_is_initial_height_at_time_zero(self):
        height, velocity = 10.0, 0.0
        result = quadratic_bouncing_ball(
            height=height,
            velocity=velocity,
            gravity=None,
            elasticity=0.8,
            samples_per_second=100.0,
            max_time=1.0,
        )
        assert len(result) >= 1
        x, y = result[0]
        assert x == pytest.approx(height, abs=1e-9)
        assert y == 0.0

    def test_sampling_time_steps_match_samples_per_second(self):
        samples_per_second = 50.0
        result = quadratic_bouncing_ball(5.0, 0.0, None, 0.9, samples_per_second, 0.5)
        assert len(result) >= 2
        dt_expected = 1.0 / samples_per_second
        for i in range(1, len(result)):
            _, t_prev = result[i - 1]
            _, t_curr = result[i]
            assert t_curr - t_prev == pytest.approx(dt_expected, abs=1e-12)

    def test_elasticity_zero_ball_stops_after_first_bounce(self):
        # Drop from 2m; after first impact elasticity 0 => height stays 0
        result = quadratic_bouncing_ball(2.0, 0.0, 10.0, 0.0, 100.0, 2.0)
        assert len(result) >= 1
        # Find first time we hit ground (height 0), then all subsequent heights should be 0
        hit_ground_idx = None
        for i, (x, _) in enumerate(result):
            if x <= 0.0:
                hit_ground_idx = i
                break
        if hit_ground_idx is not None:
            for i in range(hit_ground_idx, len(result)):
                assert result[i][0] == pytest.approx(0.0, abs=1e-9)

    def test_output_tuples_are_height_time(self):
        result = quadratic_bouncing_ball(1.0, 0.0, None, 1.0, 10.0, 0.5)
        for pt in result:
            x, y = pt
            assert isinstance(x, float)
            assert isinstance(y, float)
            assert x >= 0.0
            assert y >= 0.0


class TestBouncingBallErrors:
    def test_raises_on_invalid_height(self):
        with pytest.raises(ValueError):
            quadratic_bouncing_ball(-1.0, 0.0, None, 1.0, 10.0, 1.0)

    def test_raises_on_invalid_samples_per_second(self):
        with pytest.raises(ValueError):
            quadratic_bouncing_ball(1.0, 0.0, None, 1.0, 0.0, 1.0)
        with pytest.raises(ValueError):
            quadratic_bouncing_ball(1.0, 0.0, None, 1.0, -10.0, 1.0)

    def test_raises_on_invalid_max_time(self):
        with pytest.raises(ValueError):
            quadratic_bouncing_ball(1.0, 0.0, None, 1.0, 10.0, 0.0)
        with pytest.raises(ValueError):
            quadratic_bouncing_ball(1.0, 0.0, None, 1.0, 10.0, -1.0)

    def test_raises_on_invalid_elasticity(self):
        with pytest.raises(ValueError):
            quadratic_bouncing_ball(1.0, 0.0, None, -0.1, 10.0, 1.0)
        with pytest.raises(ValueError):
            quadratic_bouncing_ball(1.0, 0.0, None, 1.5, 10.0, 1.0)

    def test_raises_on_invalid_gravity(self):
        with pytest.raises(ValueError):
            quadratic_bouncing_ball(1.0, 0.0, -1.0, 1.0, 10.0, 1.0)
