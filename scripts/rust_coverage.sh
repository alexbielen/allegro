#!/usr/bin/env bash
# LLVM source-based coverage for the PyO3 native extension while running pytest.
#
# Requires: rustup component add llvm-tools-preview
#
# Usage (from repo root):
#   ./scripts/rust_coverage.sh [pytest-args...]
#
# Summary prints to stdout; HTML report: target/rust-coverage/html/index.html
#
set -euo pipefail

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

echo "Building instrumented extension (maturin develop, debug)..."
uv run maturin develop

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
