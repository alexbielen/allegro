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

Rahn Prime Form (oriented, Wikipedia/Forte A/B)

1. **Find the normal form**: Arrange the pitch classes in ascending order that creates the smallest interval between the first and last note (see `get_normal_form` above).
2. **Transpose to 0 (\(T_n\))**: Transpose the normal form so it starts on 0 (e.g., if the set is \([2, 4, 7]\), it becomes \([0, 2, 5]\)).

This yields the **oriented Rahn prime form** used in the Wikipedia *List of set classes* “Prime form” column, including A/B variants for asymmetrical sets:

- Asymmetrical sets preserve their inversional orientation (e.g. a major triad \([4, 8, 11]\) has prime form \([0, 4, 7]\) → `3-11B`; a minor triad \([3, 7, 10]\) has prime form \([0, 3, 7]\) → `3-11A`).
- Symmetrical sets (those inversionally equivalent to themselves) have the same prime form as their inversion, so no A/B distinction is needed.
