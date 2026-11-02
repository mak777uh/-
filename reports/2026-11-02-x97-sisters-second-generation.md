# X97 — the sister advantage does reach the second generation, and it grows there

**Plan:** [`2026-11-02-x97-sisters-second-generation-plan.md`](2026-11-02-x97-sisters-second-generation-plan.md) (23:50).
**Aggregate:** `l1_field_x97_sisters_second_generation.json`. Analysis of X108's dense logs (`--split-new-uid`), no new runs.

## What was asked

X93 measured sisters in one generation: the larger sister lives longer by +0.050 at `F = 0.025` (z 4.7), +0.082 at 0.030, nothing at 0.035,
and the maze reverses it (0.401, z −8.9). Whether that is a property of a **lineage** or of a single structure is decided one generation
later: do the larger sister's **granddaughters** also do better?

## Numbers

Paired per sister pair (both branches must produce at least one granddaughter); area in cells.

| cell | sister pairs | heredity ρ₁ (control) | first generation: larger − smaller | second generation: granddaughters' difference | bootstrap 95 % CI | z |
|---|---|---|---|---|---|---|
| 0.030 | 282 | 0.548 ✓ | **+4.94** (z 2.43) | **+12.90** | **[10.11, 15.80]** | **8.84** |
| 0.040 | 186 | 0.480 ✓ | **+88.06** (z 2.12) | **+170.91** | **[127.9, 228.9]** | **6.69** |

Both controls fired: heredity on the same worlds is 0.548 / 0.480 (the levels this line has measured since X100), and the first-generation
difference reproduces X93's *sign* with z ≥ 2 in the lattice cell.

Registered verdict: **the sister advantage persists into the second generation** — the interval excludes zero in both cells, and the
difference is *larger* than in the first generation (+12.9 against +4.9 in the lattice; +170.9 against +88.1 in the maze, almost double).

## How far this can be read

The result is real and it is the first two-generation statement in the field line. It is also **exactly what size heredity predicts**: a
daughter inherits about half her mother's deviation (ρ₁ ≈ 0.5), so a larger sister should have larger daughters and therefore larger
granddaughters, and the paired difference should not vanish. What the numbers add beyond that expectation is the **direction of the
change**: the advantage grows rather than decays, in both cells, which heredity alone does not require (a 0.5 coefficient would typically
shrink a difference from one generation to the next).

That growth needs a mechanism and has two candidates, neither tested:

1. **Branching compounds size** — a larger structure has more cells that can divide, so her line branches more, and the granddaughters'
   mean is pulled up by the number of branches rather than by their individual size.
2. **A genuine lineage effect** — the larger sister's line is in a better place or holds a better excursion, and the advantage accumulates.

What would separate them: comparing the *median* granddaughter (insensitive to the number of branches) with the *mean*, and counting
granddaughters per branch. If the median difference is much smaller than the mean, candidate 1 dominates.

So the honest sentence for the manuscript is: **the sister difference is inherited across a generation in size terms, and it grows; whether
that is a lineage advantage or an arithmetic consequence of branching is not yet known.** This is a heredity result, not a selection result,
and it is explicitly not evidence that size pays — X92/X111 already showed the consequence side sits at the noise floor.

## Caveats

- The granddaughter filter cuts the sample: 282 and 186 sister pairs survive out of the sisters X108 carries.
- Two cells only (0.030, 0.040); the 0.025 and 0.035 cells of X93 have no dense counterpart.
- The first-generation readout here is **area difference**, not X93's lifetime-share difference: the control was registered as "sign with
  z ≥ 2", and it passed, but the two numbers are not interchangeable.
- Areas are threshold-0.20 excursion areas on the dense series; X99/X112b put a cut correction of about a tenth on such numbers.
- One seed set (301–310) and one box.

## Next

- **The mean-versus-median test is registered as the immediate follow-up** (it costs one analysis run on the same logs and separates
  branching arithmetic from a lineage effect). If the median difference holds, the stronger statement becomes available.

доска: принято 0, отклонено 0, отложено 0.
