"""3D visualization for the Rust-backed boids simulation.

Run this module directly to see a basic flocking animation:

    python -m allegro.examples.boids

This example uses ``matplotlib`` for a lightweight 3D scatter plot animation.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, List, Optional

from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  - side-effect import
import typer

from allegro.boids import (
    Boid,
    Dimensions,
    Universe,
    create_boids_with_random_positions,
)


@dataclass
class BoidsConfig:
    """Configuration for the demo universe."""
    flock_size: int = 150
    world_extent: float = 500.0
    cohesion_factor: float = 0.003
    separation_distance: float = 20.0
    alignment_factor: float = 0.05
    bound_steer: float = 2.0
    speed_limit: float | None = 12.0


class Mode(str, Enum):
    BASIC = "basic"
    LOOSE = "loose"
    MURMURATION = "murmuration"
    BALANCED = "balanced"


BASIC_CONFIG = BoidsConfig()


LOOSE_CONFIG = BoidsConfig(
    flock_size = 150,
    world_extent = 500.0,
    cohesion_factor = 0.002,
    separation_distance = 25.0,
    alignment_factor = 0.04,
    bound_steer = 1.5,
    speed_limit = 10.0,
)

MURMURATION_CONFIG = BoidsConfig(
    flock_size = 150,
    world_extent = 500.0,
    cohesion_factor = 0.005,
    separation_distance = 15.0,
    alignment_factor = 0.07,
    bound_steer = 2.0,
    speed_limit = 11.0,
)

BALANCED_CONFIG = BoidsConfig(
    flock_size = 150,
    world_extent = 500.0,
    cohesion_factor = 0.003,
    separation_distance = 20.0,
    alignment_factor = 0.05,
    bound_steer = 2.0,
    speed_limit = 12.0,
)


MODES: dict[Mode, BoidsConfig] = {
    Mode.BASIC: BASIC_CONFIG,
    Mode.LOOSE: LOOSE_CONFIG,
    Mode.MURMURATION: MURMURATION_CONFIG,
    Mode.BALANCED: BALANCED_CONFIG,
}


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
    ax.set_title(f"Boids")

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


def main(
    mode: Optional[Mode] = typer.Option(
        None,
        "--mode",
        help="Preset configuration: basic, loose, murmuration, or balanced.",
    ),
    flock_size: Optional[int] = typer.Option(
        None,
        "--flock-size",
        help="Number of boids in the simulation.",
    ),
    world_extent: Optional[float] = typer.Option(
        None,
        "--world-extent",
        help="Half-size of the cubic world bounds.",
    ),
    cohesion_factor: Optional[float] = typer.Option(
        None,
        "--cohesion-factor",
        help="Cohesion factor for boid flocking.",
    ),
    separation_distance: Optional[float] = typer.Option(
        None,
        "--separation-distance",
        help="Minimum separation distance between boids.",
    ),
    alignment_factor: Optional[float] = typer.Option(
        None,
        "--alignment-factor",
        help="Alignment factor for boid velocities.",
    ),
    bound_steer: Optional[float] = typer.Option(
        None,
        "--bound-steer",
        help="Steering strength keeping boids within bounds.",
    ),
    speed_limit: Optional[float] = typer.Option(
        None,
        "--speed-limit",
        help="Maximum boid speed.",
    ),
    interval_ms: int = typer.Option(
        30,
        "--interval-ms",
        help="Animation frame interval in milliseconds.",
    ),
) -> None:
    """Entry point for the boids visualization."""
    config_values = {
        "flock_size": flock_size,
        "world_extent": world_extent,
        "cohesion_factor": cohesion_factor,
        "separation_distance": separation_distance,
        "alignment_factor": alignment_factor,
        "bound_steer": bound_steer,
        "speed_limit": speed_limit,
    }

    if mode:
        # Use preset mode, no individual config values allowed.
        extra = [name for name, value in config_values.items() if value]
        if extra:
            typer.echo(f"Error: When using --mode you may not also specify: {', '.join(sorted(extra))}", err=True)
            raise typer.Exit(code=1)
        cfg = MODES[mode]
    else:
        # Full custom config, all values must be provided.
        missing = [name for name, value in config_values.items() if not value]
        if missing:
            typer.echo(f"Error: When not using --mode you must provide all of:\n  {', '.join(sorted(missing))}", err=True)
            raise typer.Exit(code=1)

        cfg = BoidsConfig(
            flock_size=flock_size,  
            world_extent=world_extent,  
            cohesion_factor=cohesion_factor,  
            separation_distance=separation_distance,  
            alignment_factor=alignment_factor,  
            bound_steer=bound_steer,  
            speed_limit=speed_limit,  
        )

    run_animation(cfg, interval_ms=interval_ms)


if __name__ == "__main__":
    typer.run(main)

