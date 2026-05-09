#!/usr/bin/env bash
# LLVM source-based coverage for the PyO3 native extension while running pytest.
#
# Requires: rustup component add llvm-tools-preview
#
# Usage (from repo root):
#   ./scripts/rust_coverage.sh [pytest-args...]
#
# If the build fails with "posix_spawn failed: Resource temporarily unavailable", lower
# parallelism:  CARGO_BUILD_JOBS=2 ./scripts/rust_coverage.sh
#
# Summary prints to stdout; HTML report: target/rust-coverage/html/index.html
#
# If you `source` this file, RUSTFLAGS / LLVM_PROFILE_FILE are restored on exit
# so your shell is not left in "coverage" mode (which can spawn default_*.profraw
# in the repo root the next time you run maturin/cargo without LLVM_PROFILE_FILE).
#
set -euo pipefail

_was_rustflags_set=0
[[ ${RUSTFLAGS+x} ]] && _was_rustflags_set=1
_saved_rustflags="${RUSTFLAGS-}"
_was_llvm_pf_set=0
[[ ${LLVM_PROFILE_FILE+x} ]] && _was_llvm_pf_set=1
_saved_llvm_profile_file="${LLVM_PROFILE_FILE-}"
_was_cargo_inc_set=0
[[ ${CARGO_INCREMENTAL+x} ]] && _was_cargo_inc_set=1
_saved_cargo_incremental="${CARGO_INCREMENTAL-}"

_restore_parent_env_if_sourced() {
	if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
		return 0
	fi
	if ((_was_rustflags_set)); then
		export RUSTFLAGS="$_saved_rustflags"
	else
		unset RUSTFLAGS
	fi
	if ((_was_llvm_pf_set)); then
		export LLVM_PROFILE_FILE="$_saved_llvm_profile_file"
	else
		unset LLVM_PROFILE_FILE
	fi
	if ((_was_cargo_inc_set)); then
		export CARGO_INCREMENTAL="$_saved_cargo_incremental"
	else
		unset CARGO_INCREMENTAL
	fi
}
trap _restore_parent_env_if_sourced EXIT

# Avoid sccache serving objects built without coverage instrumentation.
unset RUSTC_WRAPPER

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

HOST=$(rustc -vV | sed -n 's/^host: //p')
SYSROOT=$(rustc --print sysroot)
LLVM_BIN="$SYSROOT/lib/rustlib/$HOST/bin"
PROFDATA="$LLVM_BIN/llvm-profdata"
COV="$LLVM_BIN/llvm-cov"

if [[ ! -x "$PROFDATA" ]] || [[ ! -x "$COV" ]]; then
	echo "error: llvm-profdata/llvm-cov not found under $LLVM_BIN" >&2
	echo "Install with: rustup component add llvm-tools-preview" >&2
	exit 1
fi

export RUSTFLAGS="${RUSTFLAGS:--Cinstrument-coverage}"
export CARGO_INCREMENTAL="${CARGO_INCREMENTAL:-0}"

COV_DIR="$ROOT/target/rust-coverage"
mkdir -p "$COV_DIR"
rm -f "$COV_DIR"/*.profraw "$COV_DIR"/merged.profdata 2>/dev/null || true

# Set for the whole script (build + pytest). Otherwise instrumented build.rs /
# proc-macros run during `maturin develop` without LLVM_PROFILE_FILE and spill
# default_*.profraw into the repo root.
export LLVM_PROFILE_FILE="$COV_DIR/llvm-%p-%m.profraw"

# Instrumented builds link libprofiler_builtins and stress clang heavily; default -j (all
# CPUs) often triggers posix_spawn(EAGAIN) on macOS: "Resource temporarily unavailable".
export CARGO_BUILD_JOBS="${CARGO_BUILD_JOBS:-4}"

echo "Building instrumented extension (maturin develop, debug, jobs=${CARGO_BUILD_JOBS})..."
uv run maturin develop --jobs "$CARGO_BUILD_JOBS"

SO=$(uv run python -c "import allegro.allegro as m; print(m.__file__)")

echo "Running pytest (profiles still under $COV_DIR via LLVM_PROFILE_FILE) ..."
uv run pytest python/tests "$@"

shopt -s nullglob
profraws=("$COV_DIR"/*.profraw)
shopt -u nullglob

if [[ ${#profraws[@]} -eq 0 ]]; then
	echo "error: no .profraw files under $COV_DIR; tests may not have loaded the native extension." >&2
	exit 1
fi

echo "Merging ${#profraws[@]} raw profile(s)..."
"$PROFDATA" merge -sparse "${profraws[@]}" -o "$COV_DIR/merged.profdata"

IGNORE='(/\.cargo/registry|/rustc/)'

echo ""
echo "Rust coverage (summary):"
"$COV" report \
	--ignore-filename-regex="$IGNORE" \
	--instr-profile="$COV_DIR/merged.profdata" \
	--object "$SO"

HTML_OUT="$COV_DIR/html"
rm -rf "$HTML_OUT"
"$COV" show \
	--ignore-filename-regex="$IGNORE" \
	--instr-profile="$COV_DIR/merged.profdata" \
	--object "$SO" \
	--format=html \
	--output-dir="$HTML_OUT"

echo ""
echo "HTML report: file://$HTML_OUT/index.html"

# Rust coverage uses -Cinstrument-coverage; the installed .so must be replaced with a
# normal release build before you run pytest without LLVM_PROFILE_FILE (otherwise
# default_*.profraw can appear in cwd).
#
# `cargo build` has no --force flag — do not pass --cargo-extra-args="--force".
# Instead: drop coverage from the environment, remove only this crate's artifacts, then
# `maturin develop --release` (keeps compiled deps in target/; faster than rm -rf target).
echo ""
echo "Reinstalling non-instrumented release extension (cargo clean -p allegro; maturin develop --release)..."
unset RUSTFLAGS LLVM_PROFILE_FILE CARGO_INCREMENTAL
cargo clean -p allegro
uv run maturin develop --release --jobs "${CARGO_BUILD_JOBS:-4}"
