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

Rahn Prime Form Calculation Steps

Find the Normal Order: Arrange the pitch classes in ascending order that creates the smallest interval between the first and last note.

Transpose to 0 (\(T\_{n}\)): Transpose the normal order so it starts on 0 (e.g., if the set is \([2, 4, 7]\), it becomes \([0, 2, 5]\)).

Invert and Rearrange (\(T\_{n}I\)): Invert the set (replace each number \(x\) with \(12-x\), or \(0-x\)), put it into normal order, and transpose it to start on 0.

Compare and Choose: Compare the results of Step 2 and Step 3. Select the version that is most compact on the left side.Note: If both are equally packed, choose the one with smaller intervals at the beginning.
