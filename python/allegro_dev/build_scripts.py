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


def run_stub_gen(root: Path) -> None:
    subprocess.run(
        ["cargo", "run", "--bin", "stub_gen"],
        cwd=root,
        check=True,
    )


def check_stubs_up_to_date(root: Path) -> None:
    """Regenerate stubs / namespace __init__ files and fail if committed files drift."""
    run_stub_gen(root)
    result = subprocess.run(
        ["git", "diff", "--exit-code", "--", "python/allegro"],
        cwd=root,
    )
    if result.returncode != 0:
        raise SystemExit(
            "Generated Python API files under python/allegro are out of date; run "
            "`cargo run --bin stub_gen` and commit the result"
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
    cmd = [sys.executable, "-m", "maturin", "develop"]
    if optimize:
        cmd.append("--release")
    subprocess.run(
        cmd,
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
    print("[bold green]Building Allegro[/bold green] [music]🎵[/music]")
    root = Path.cwd()
    root = find_project_root(root)
    run_stub_gen(root)
    run_clippy(root)
    run_maturin_develop(root, optimize=True)
    run_pytest(root, skip_benchmark=True, verbose=True)


def run_benchmarks() -> None:
    root = Path.cwd()
    root = find_project_root(root)
    run_pytest(root, benchmark_only=True, verbose=True)


def main() -> None:
    build_and_test()
