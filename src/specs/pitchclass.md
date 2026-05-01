# Normal form

Reference for `PitchClassSet::normal_form` in Rust (`pitchclass.rs`: `get_normal_form`, helpers `rotation` / `wrap_pitch_classes_line`).

Python’s `p % 12` on negative values uses “floor” modulus; Rust uses Euclidean remainder `p.rem_euclid(12)` so both match for integer pitch lines used here (`p >= -11` effectively never negative in our pipeline).

## Python

```python
def get_normal_form(pcs):
    """Calculates the normal form of a pitch class set."""
    pcs = sorted(list(set(p % 12 for p in pcs)))
    n = len(pcs)
    rotations = [pcs[i:] + [p + 12 for p in pcs[:i]] for i in range(n)]

    # 1. Minimize total span
    spans = [r[-1] - r[0] for r in rotations]
    min_span = min(spans)
    candidates = [r for i, r in enumerate(rotations) if spans[i] == min_span]

    if len(candidates) == 1:
        return [p % 12 for p in candidates[0]]

    # 2. Break ties by minimizing span from 1st to (n-1)th, (n-2)th, etc.
    for i in range(2, n + 1):
        spans = [r[-i] - r[0] for r in candidates]
        min_span = min(spans)
        candidates = [r for j, r in enumerate(candidates) if spans[j] == min_span]
        if len(candidates) == 1:
            break

    return [p % 12 for p in candidates[0]]
```

## Rust (matching structure)

Rust keeps the same steps: build `rotations`, filter by `r[n-1] - r[0]`, optionally narrow with `r[n - i] - r[0]` for `i in 2..=n`, then map each coordinate with `rem_euclid(12)`. Empty set yields `[]`; a single pc yields `[pc.rem_euclid(12)]` (same idea as `% 12` for non-negative pcs).
