import matplotlib.pyplot as plt
import seaborn as sns

from allegro.physical import bouncing_ball


def plot_bouncing_ball(
    height: float = 10.0,
    velocity: float = 0.0,
    gravity: float | None = None,
    elasticity: float = 0.85,
    samples_per_second: float = 100.0,
    max_time: float = 5.0,
):
    """Run a bouncing-ball simulation and plot height vs time with seaborn."""

    points = bouncing_ball(height, velocity, gravity, elasticity, samples_per_second, max_time)
    times = [t for _, t in points]
    heights = [h for h, _ in points]

    sns.set_theme(style="darkgrid")
    _fig, ax = plt.subplots(figsize=(8, 4))
    sns.lineplot(x=times, y=heights, ax=ax)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Height (m)")
    ax.set_title("Bouncing ball")
    ax.set_ylim(bottom=0)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    plot_bouncing_ball(
        height=1.0,
        velocity=0.0,
        gravity=None,
        elasticity=0.75,
        samples_per_second=100.0,
        max_time=15.0,
    )
