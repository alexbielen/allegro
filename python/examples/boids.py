"""3D visualization for the Rust-backed boids simulation.

Run this module directly to see a basic flocking animation:

    python -m allegro.examples.boids

This example uses ``matplotlib`` for a lightweight 3D scatter plot animation.
It deliberately keeps the rendering code simple so the focus stays on the
simulation API (``Universe``, ``Dimensions``, ``Boid``).
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Iterable, List

from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  - side-effect import

from allegro.boids import (
    Boid,
    Dimensions,
    Universe,
    create_boids_with_random_positions,
)


@dataclass
class BoidsConfig:
    """Configuration for the demo universe."""
    flock_size: int = 80
    world_extent: float = 500.0
    cohesion_factor: float = 0.003
    separation_distance: float = 20.0
    alignment_factor: float = 0.05
    bound_steer = 2.0
    speed_limit: float | None = 12.0


def make_universe(cfg: BoidsConfig) -> Universe:
    half = cfg.world_extent
    dims = Dimensions(-half, half, -half, half, -half, half)
    flock: List[Boid] = create_boids_with_random_positions(cfg.flock_size, dims)
    return Universe(
        flock,
        dims,
        cfg.cohesion_factor,
        cfg.separation_distance,
        cfg.alignment_factor,
        cfg.bound_steer,
        cfg.speed_limit,
    )


def extract_positions(flock: Iterable[Boid]) -> tuple[list[float], list[float], list[float]]:
    xs: list[float] = []
    ys: list[float] = []
    zs: list[float] = []
    for boid in flock:
        x, y, z = boid.position()
        xs.append(x)
        ys.append(y)
        zs.append(z)
    return xs, ys, zs


def update_boids(
    _frame: int,
    universe: Universe,
    scatter,
) -> list:
    """Advance the universe by one step and update the scatter plot."""
    new_flock = universe.step()
    xs_u, ys_u, zs_u = extract_positions(new_flock)
    scatter._offsets3d = (xs_u, ys_u, zs_u)  # type: ignore[attr-defined]
    return [scatter]


def run_animation(cfg: BoidsConfig, *, interval_ms: int = 30) -> None:
    universe = make_universe(cfg)

    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="3d")

    # Initial scatter setup.
    flock = universe.step()
    xs, ys, zs = extract_positions(flock)
    scatter = ax.scatter(xs, ys, zs, s=10, c="tab:blue", alpha=0.8)

    half = cfg.world_extent
    ax.set_xlim(-half, half)
    ax.set_ylim(-half, half)
    ax.set_zlim(-half, half)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title("Boids (3D Rust-backed simulation)")

    # Keep a strong reference to the animation object so it is not
    # garbage-collected before ``plt.show()`` has a chance to render it.
    anim = FuncAnimation(  # noqa: F841 - referenced for side effects
        fig,
        update_boids,
        fargs=(universe, scatter),
        interval=interval_ms,
        blit=False,
        cache_frame_data=False,
    )

    plt.tight_layout()
    plt.show()


def parse_args() -> BoidsConfig:
    parser = argparse.ArgumentParser(description="3D boids visualization demo.")
    parser.add_argument(
        "--flock-size",
        type=int,
        default=BoidsConfig.flock_size,
        help="Number of boids in the simulation (default: %(default)s).",
    )
    parser.add_argument(
        "--world-extent",
        type=float,
        default=BoidsConfig.world_extent,
        help="Half-size of the cubic world bounds (default: %(default)s).",
    )
    parser.add_argument(
        "--interval-ms",
        type=int,
        default=30,
        help="Animation frame interval in milliseconds (default: %(default)s).",
    )
    args = parser.parse_args()
    return BoidsConfig(
        flock_size=args.flock_size,
        world_extent=args.world_extent,
    )


def main() -> None:
    cfg = parse_args()
    run_animation(cfg)


if __name__ == "__main__":
    main()

