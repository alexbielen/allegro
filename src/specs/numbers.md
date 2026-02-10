# Numbers

## fit

### Reflect

The **Reflect** mode treats `num` as a coordinate on the number line. If it lies outside the
range, it is reflected back into \[min, max] by reflecting at the nearest bound and
continuing with the remaining offset.

For the interval \[0, 10]:

- `12 → 8` — 2 past 10, so move 2 units back from 10 → 8.
- `23 → 3` — 13 past 10: go 10 to reach 0, then 3 more into the interval → 3.
- `33 → 7` — 23 past 10; after full round‑trips the remainder is 3, so we end 3 back from 10 → 7.
- `-4 → 4` — 4 below 0: reflect 4 units into the interval from 0 → 4.
- `-23 → 3` — 23 below 0: reduce modulo a double-width period to an effective offset of 3 from 0 → 3.

Conceptually, you can imagine sliding the point along the line and reflecting it whenever it
crosses `min` or `max`, until it comes to rest inside the interval.

### Bounce

The **Bounce** mode instead treats the **magnitude** of `num` as an amount of \"energy\" (distance)
to travel, and the **sign** of `num` as the starting side:

- If `num > 0`, start at `min` and move **right** (increasing).
- If `num < 0`, start at `max` and move **left** (decreasing).

Whenever the moving point hits `min` or `max`, it bounces and reverses direction, continuing until
all energy is spent.

For the interval \[0, 10]:

- `12 → 8` — start at 0, go right 10 to hit 10, bounce, 2 back to 8.
- `23 → 3` — 0→10 (10), 10→0 (10), 0→3 (3) → 3.
- `-12 → 2` — start at 10, go left 10 to hit 0, remaining 2, go right to 2.
- `-23 → 7` — 10→0 (10), 0→10 (10), now heading left from 10 with remaining 3 → 7.

#### Bounce algorithm

Given `num`, `min`, `max` with `width = max - min > 0`:

1. Let `energy = abs(num)`.
2. Let `width = max - min` and `period = 2 * width` (one full round‑trip).
3. Reduce the energy into a single period:
   - `r = energy mod period`, so `r ∈ [0, 2 * width)`.
4. Convert this to an **unoriented offset** in \[0, width]:
   - If `r ≤ width`: `offset = r` (first leg of the trip).
   - Else: `offset = 2 * width - r` (on the way back).
5. Map the offset to an actual position, based on the sign of `num`:
   - If `num > 0`: `result = min + offset`.
   - If `num < 0`: `result = max - offset`.

This gives the same results as the examples above while avoiding an explicit loop over multiple
bounces.
