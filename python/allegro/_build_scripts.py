"""Development helper: build Rust extension and run tests. Used by the dev-build script."""

import subprocess
import sys
from pathlib import Path

from rich import print


def run_clippy(root: Path) -> None:
    subprocess.run(
        ["cargo", "clippy", "--", "-D", "warnings"],
        cwd=root,
        check=True,
    )


def run_pytest(
    root: Path,
    verbose: bool = False,
    skip_benchmark: bool = False,
    benchmark_only: bool = False,
) -> None:
    args = []

    if skip_benchmark and benchmark_only:
        raise ValueError("Cannot skip benchmarks and run benchmark-only tests at the same time")

    if verbose:
        args.append("-v")
    if skip_benchmark:
        args.append("--benchmark-skip")
    if benchmark_only:
        args.append("-k")
        args.append("benchmark")
        args.append("--benchmark-only")

    subprocess.run(
        [sys.executable, "-m", "pytest", *args, "python/tests"],
        cwd=root,
        check=True,
    )


def run_maturin_develop(root: Path, optimize: bool = False) -> None:
    subprocess.run(
        [sys.executable, "-m", "maturin", "develop", "--release" if optimize else ""],
        cwd=root,
        check=True,
    )


def find_project_root(root: Path) -> Path:
    for p in [root, *root.parents]:
        if (p / "pyproject.toml").exists() and (p / "Cargo.toml").exists():
            return p
    else:
        sys.exit("dev-build must be run from the allegro repo (directory with pyproject.toml and Cargo.toml)")


def build_and_test() -> None:
    # print Building Allegro with music notes icon
    print("[bold green]Building Allegro[/bold green] [music]🎵[/music]")
    root = Path.cwd()
    root = find_project_root(root)
    run_clippy(root)
    run_maturin_develop(root, optimize=True)
    run_pytest(root, skip_benchmark=True, verbose=True)


def run_benchmarks() -> None:
    root = Path.cwd()
    root = find_project_root(root)
    run_pytest(root, benchmark_only=True, verbose=True)


def main() -> None:
    build_and_test()
