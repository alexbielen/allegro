from allegro.physical import bouncing_ball, CommonBallElasticity

import pytest


def find_first_zero_index(result):
    return next((i for i, (h, t) in enumerate(result) if h == 0.0), None)


class TestBouncingBallBehavior:

    def test_returns_height_time_tuples(self):
        result = bouncing_ball(
            height=5.0,
            velocity=0.0,
            gravity=None,
            elasticity=0.8,
            samples_per_second=50.0,
            max_time=1.0,
        )
        assert len(result) >= 1
        for h, t in result:
            assert isinstance(h, float)
            assert isinstance(t, float)
            assert h >= 0.0
            assert t >= 0.0

    def test_first_point_initial_height_at_zero_time(self):
        result = bouncing_ball(10.0, 0.0, None, 0.8, 100.0, 0.5)
        assert result[0][0] == pytest.approx(10.0, abs=1e-9)
        assert result[0][1] == 0.0

    def test_that_second_point_is_higher_with_positive_velocity(self):
        result = bouncing_ball(10.0, 1.0, None, 0.8, 100.0, 0.5)
        assert result[1][0] > result[0][0]

    def test_that_second_point_is_lower_with_zero_velocity(self):
        result = bouncing_ball(10.0, 0.0, None, 0.8, 100.0, 0.5)
        assert result[1][0] < result[0][0]

    def test_that_second_point_is_lower_with_negative_velocity(self):
        result = bouncing_ball(10.0, -1.0, None, 0.8, 100.0, 0.5)
        assert result[1][0] < result[0][0]

    def test_that_ball_stays_at_rest_on_ground_with_elasticity_zero(self):
        result = bouncing_ball(10.0, 0.0, None, 0.0, 100.0, 10)
        zero_index = next((i for i, (h, t) in enumerate(result) if h == 0.0), None)

        assert zero_index is not None

        for i in range(zero_index, len(result)):
            assert result[i][0] == 0.0

    def test_that_smaller_elasticity_results_in_smaller_bounces(self):
        basketball = bouncing_ball(
            10.0, 0.0, None, CommonBallElasticity.Basketball, 100.0, 10
        )
        baseball = bouncing_ball(
            10.0, 0.0, None, CommonBallElasticity.Baseball, 100.0, 10
        )

        basketball_zero_index = find_first_zero_index(basketball)
        baseball_zero_index = find_first_zero_index(baseball)

        assert basketball_zero_index is not None
        assert baseball_zero_index is not None

        basketball_max = max(basketball[basketball_zero_index:])
        baseball_max = max(baseball[baseball_zero_index:])

        assert basketball_max > baseball_max


class TestBouncingBallErrors:
    def test_raises_on_invalid_height(self):
        with pytest.raises(ValueError):
            bouncing_ball(-1.0, 0.0, None, 0.8, 100.0, 0.5)

    def test_raises_on_invalid_velocity(self):
        with pytest.raises(ValueError):
            bouncing_ball(10.0, float("nan"), None, 0.8, 100.0, 0.5)
        with pytest.raises(ValueError):
            bouncing_ball(10.0, float("inf"), None, 0.8, 100.0, 0.5)
        with pytest.raises(ValueError):
            bouncing_ball(10.0, float("-inf"), None, 0.8, 100.0, 0.5)

    def test_raises_on_invalid_elasticity(self):
        with pytest.raises(ValueError):
            bouncing_ball(10.0, 0.0, None, -0.1, 100.0, 0.5)
        with pytest.raises(ValueError):
            bouncing_ball(10.0, 0.0, None, 1.5, 100.0, 0.5)

    def test_raises_on_invalid_gravity(self):
        with pytest.raises(ValueError):
            bouncing_ball(10.0, 0.0, -1.0, 0.8, 100.0, 0.5)

    def test_raises_on_invalid_samples_per_second(self):
        with pytest.raises(ValueError):
            bouncing_ball(10.0, 0.0, None, 0.8, 0.0, 0.5)
        with pytest.raises(ValueError):
            bouncing_ball(10.0, 0.0, None, 0.8, -10.0, 0.5)

    def test_raises_on_invalid_max_time(self):
        with pytest.raises(ValueError):
            bouncing_ball(10.0, 0.0, None, 0.8, 100.0, 0.0)
