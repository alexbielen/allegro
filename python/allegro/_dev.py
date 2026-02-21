"""Development helper: build Rust extension and run tests. Used by the dev-build script."""

from pathlib import Path
import subprocess
import sys


def main() -> None:
    # Find project root (directory containing pyproject.toml).
    root = Path.cwd()
    for p in [root, *root.parents]:
        if (p / "pyproject.toml").exists() and (p / "Cargo.toml").exists():
            root = p
            break
    else:
        sys.exit(
            "dev-build must be run from the allegro repo (directory with pyproject.toml and Cargo.toml)"
        )
    subprocess.run(
        [sys.executable, "-m", "maturin", "develop", "--release"],
        cwd=root,
        check=True,
    )
    subprocess.run(
        [sys.executable, "-m", "pytest", "-v", "python/tests"],
        cwd=root,
        check=True,
    )


if __name__ == "__main__":
    main()
