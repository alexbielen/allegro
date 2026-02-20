"""Physical namespace: bouncing ball and related utilities."""

from .allegro import bouncing_ball


class CommonBallElasticity:
    """Estimated "coefficient of restitution" for common ball types. Use as value for elasticity parameter."""

    Baseball = 0.5
    Basketball = 0.85
    Billiards = 0.5
    Bowling = 0.3
    FoamBall = 0.30
    Golf = 0.4
    Perfect = 1.0
    PingPongBall = 0.92
    Soccer = 0.6
    SuperBall = 0.95
    Tennis = 0.75


__all__ = [
    "CommonBallElasticity",
    "bouncing_ball",
]
