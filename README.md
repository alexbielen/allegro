# Allegro

[![Build and Test](https://github.com/alexbielen/allegro/actions/workflows/build-and-test.yml/badge.svg)](https://github.com/alexbielen/allegro/actions/workflows/build-and-test.yml)

Allegro is a work-in-progress algorithmic music composition toolbox written in Python and Rust. This project aims to offer a Python-based UX experience, targeted to composers, with the speed of Rust.

### Name

"Allegro" is a common Italian tempo marking in music meaning "fast," "lively," and "bright" which the project aims to be.

### Development

Development environment dependencies are managed with nix, in the `flake.nix` file.

The Rust components are built with `maturin` and Python dependency and development management is handled by `uv`.

The project uses `pytest` for testing.

```bash
> nix develop
> uv run dev-build
```
