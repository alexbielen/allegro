# Boids

This document defines a Boids flocking system, implemented in Rust and exposed in Python.
The intent is to closely follow Conrad Parker’s Boids pseudocode (itself
derived from Reynolds’ original work) while providing a clear API.

- `Universe`: simulation parameters and a function that returns the latest step.
- `Dimensions`: world bounds.
- `Boid`: a single bird-like agent with position and velocity.

Rust is responsible for the heavy numerical work. We'll generally take a Rust-first approach, with the end product accesible in Python.

---

## Conceptual model

We simulate a flock of agents (“boids”). Each `Boid` has:

- A position vector \(p = (x, y, z)\)
- A velocity vector \(v = (vx, vy, vz)\)

At each time step, every boid updates its velocity according to three rules:

1. **Cohesion** – Boids try to fly towards the center of mass of neighboring boids
2. **Separation** – Boids try to keep a small distance away from other objects (including other boids).
3. **Speed** – Boids try to match velocity with near boids.

After applying these adjustments, we:

- Apply a **speed limit**.
- Apply **world bounds**.
- Update the position using the new velocity.

The implementation here is intentionally close to Conrad Parker’s pseudocode, but
organized around explicit types and methods so that it is easy to test and evolve.

---

## High-level structure

The simulation loop conceptually looks like:

```text
initialise_positions()

LOOP
    draw_boids()
    move_all_boids_to_new_positions()
END LOOP
```

In this repository, the equivalent responsibilities are:

- **Initialization** happens through Rust code that constructs a `Universe`, given a dimension objects, and other input parameters. This creates the initial set of `Boids` which start in random positions within the bounds provided in `Dimensions`.
- **Drawing** is left to the caller (e.g. matplotlib, a game engine, etc.).
- **Movement** is performed by `Universe.step()`, which advances the entire
  flock by one time step.

---

## Data model

### Dimensions

`Dimensions` describes the size of the 3D world that the boids live in. This is a simple data container passed into a `Universe` constructor.

fields:

- `x_min`, `x_max`
- `y_min`, `y_max`
- `z_min`, `z_max`

### Boid

`Boid` represents a single agent in the flock. It is a Rust struct.

fields:

- `pub position: Vec3[f64, f64, f64]`
- `velocity: Vec3[f64, f64, f64]`

There is an impl block that exposes methods that correspond directly to the three rules.

Methods:

- `fn fly_towards_perceived_center_of_mass(self, universe: Universe)`
- `fn move_away_from_close_by_objects(universe: Universe)`
- `fn match_perceived_speed_of_flock(universe: Universe)`
- `fn limit_velocity(universe: Universe)`
- `fn bound_position(universe: Universe)`
- `pub fn move_to_new_position(universe: Universe)`

### Initializing a set of boids

It can be useful to get a set number of boids that are randomly placed in a set of `Dimensions`.

`fn create_boids(flock_size: int, Dimensions)`

### Universe

`Universe` holds global simulation parameters and the flock of boids.

Conceptual fields:

- `flock: List[Boids]`
- `dimensions: Dimensions`
- `cohesion_factor: float` – how strongly rule 1 pulls toward the perceived center
  (e.g. \(1/100\)).
- `separation_distance: float` – distance threshold for rule 2 (e.g. 100.0).
- `alignment_factor: float` – how strongly velocities are steered toward the
  perceived flock velocity (e.g. $1/8$).
- `bound_steer`: how strongly to push boids back into the world when they cross a boundary (e.g. 10 units of velocity back toward the center).
- `speed_limit: float | None` – optional maximum speed magnitude.

Key method:

- `Universe.step()`

which advances the entire system by one discrete time step.

---

## Rules in detail

### Rule 1 – cohesion (fly towards perceived center of mass)

Intuition: each boid steers a little bit toward the flock’s center of mass.

For a given boid \(i\):

1. Compute the average position of all _other_ boids:

   $$
   pc = \frac{1}{N-1} \sum_{j \neq i} p_j
   $$

2. Compute a steering vector toward that perceived center, scaled down:

   $$
   v_1 = \frac{pc - p_i}{\text{movement\_factor}}
   $$

   where `movement_factor` is typically 100.0. Equivalent in this case to

   $$
   v_1 = (pc - pi) * 0.01
   $$

3. Add this to the velocity:

   $$
   v_i \mathrel{+}= v_1
   $$

In Rust, `fn fly_towards_perceived_center_of_mass(universe)` should
add this $v_1$ term to the boid’s velocity.

### Rule 2 – separation (move away from close neighbors)

Intuition: boids should not crowd each other. If another boid comes within a
certain distance, push them apart.

For a given boid $i$:

1. Initialize a displacement vector $c = (0, 0, 0)$.
2. For each other boid $j$:
   - If $\|p_j - p_i\| < \text{distance\_unit}$ (e.g. 100.0):
     - Subtract the displacement:

       $$
       c \mathrel{-}= (p_j - p_i)
       $$

3. Add $c$ to the velocity:

   $$
   v_i \mathrel{+}= c
   $$

For efficiency purposes with the `glam` library, we're doing

$$
\|p_j - p_i\|^2 < \text{distance\_unit}^2
$$

In Rust, `fn move_away_from_close_by_objects(universe)` should
compute this contribution and update the velocity accordingly.

### Rule 3 – speed (match perceived flock velocity)

Intuition: boids try to align their velocity with that of their neighbors.

For a given boid $i$:

1. Compute the perceived average velocity of all _other_ boids:

   $$
   pv = \frac{1}{N-1} \sum_{j \neq i} v_j
   $$

2. Compute the steering adjustment:

   $$
   v_3 = \frac{pv - v_i}{\text{velocity\_factor}}
   $$

   where `velocity_factor` is typically 8.0 (i.e. “about an eighth” of the
   difference).

3. Add this to the velocity:

   $$
   v_i \mathrel{+}= v_3
   $$

In Rust, `fn match_perceived_speed_of_flock(universe)` should apply
this correction.

---

## Speed limiting

To prevent boids from accelerating out of control, we clamp the magnitude of the velocity vector to at most `speed_limit` (if provided).

For each boid:

1. Compute the speed:

   $$
   s = \|v_i\|
   $$

2. If `speed_limit` is set and $s > \text{speed\_limit}$:
   - Rescale:

     $$
     v_i \leftarrow v_i \cdot \frac{\text{speed\_limit}}{s}
     $$

In Rust this logic belongs in `fn limit_velocity(universe)`.

---

## World bounds (soft bounding box)

We model the simulation world as an axis-aligned bounding box, specified by
`Dimensions`. When a boid moves outside this box, we nudge it back in with a
fixed steering amount from the universe parameters (`bound_steer`).

For each coordinate axis:

- If `position.x < x_min`, then increase `velocity.x` by `bound_steer`.
- If `position.x > x_max`, then decrease `velocity.x` by `bound_steer`.
- Similarly for `y` and `z` with `y_min`, `y_max`, `z_min`, and `z_max`.

This does not teleport boids; it simply biases their velocity back toward
the interior. The result is a soft, “bouncy” world boundary.

In Rust this is written in `fn bound_position(universe)`.

---

## Per-step update order

The order of updates per time step is important to match the classic Boids
behavior.

For each simulation step:

1. For every boid $i$, compute the three rules using the current
   positions and velocities:
   - Cohesion (`fly_towards_perceived_center_of_mass`)
   - Separation (`move_away_from_close_by_objects`)
   - Speed (`match_perceived_speed_of_flock`)
2. Apply bounds (`bound_position`).
3. Apply speed limit (`limit_velocity`).
4. Update positions:

   $$
   p_i \leftarrow p_i + v_i
   $$

At the Rust API level, this is expressed as:

- `Boid.move_to_new_position(universe)` performs steps 1–4 for a single boid.
- `Universe.step()` iterates and updates all boids in
  one pass.

---

## Python API expectations

While the exact module layout can evolve, this spec expects something along
the following lines from the Python side:

```python
from allegro.boids import Universe, Dimensions, Boid

dims = Dimensions(
    x_min=-500.0, x_max=500.0,
    y_min=-500.0, y_max=500.0,
    z_min=-500.0, z_max=500.0,
)

universe = Universe(
    dimensions=dims,
    flock_size=15,
    cohesion_factor=1.0 / 100.0,
    separation_distance=100.0,
    alignment_factor=1.0 / 8.0,
    speed_limit=10.0,
    bound_steer=10.0,
)

for _ in range(1000):
    step = universe.step()
    boid = step[0]
    boid.position # (x, y, z)
    type(boid) # Boid etc. etc.

    # draw or log boid positions here
```

The Rust side should implement the heavy computation needed by `Universe.step()`
and be tested against small, deterministic examples to ensure it matches the
rules laid out above.

---

## Testing guidelines

To be confident that the Rust + Python implementation obeys this spec, add
tests that:

- **Cohesion sanity check**: with two boids starting at known positions and
  zero initial velocity, verify that they move slightly toward each other after
  one step.
- **Separation sanity check**: with two boids starting very close together,
  verify that they move apart after one step.
- **Alignment sanity check**: with one boid stationary and the rest moving in
  the same direction, verify that the stationary boid’s velocity rotates toward
  the flock’s velocity over multiple steps.
- **Speed limit**: construct a scenario where the raw rule contributions would
  exceed `speed_limit` and verify that the final speed is clamped.
- **Bounds**: start a boid outside of `Dimensions` and verify that it is steered
  inward over several steps.

These tests should be written in Python, using the public `Universe`,
`Dimensions`, and `Boid` APIs.

---

## Summary

This spec defines:

- A **3D Boids model** with explicit `Boid`, `Dimensions`, and `Universe` types.
- The three classic rules (cohesion, separation, alignment) plus **speed
  limiting** and **soft world bounds**.
- A **Python-first API** backed by Rust for performance.

The implementation in this repository should treat this document as the
authoritative reference for behavior and naming.
