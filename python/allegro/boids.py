"""Boids flocking simulation: Universe, Dimensions, Boid (Rust-backed)."""

from .allegro import (
    Boid,
    Dimensions,
    Universe,
    create_boids_with_random_positions,
)

__all__ = [
    "Boid",
    "Dimensions",
    "Universe",
    "create_boids_with_random_positions",
]
