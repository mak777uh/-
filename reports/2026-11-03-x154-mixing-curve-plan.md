# X154 — the mixing curve: is the width in the time measurable, or is it noise of ten seeds?

**Why.** X153 found the outcome and the time behave differently at the boundary: radius 6 at a surface gap of 7.5 cells
still coalesces in **10 of 10** seeds — as at 7 — but **two of those ten** dissolve at the later logged step (49 rather
than 39). That is either the edge of a real distribution (a transition with a width in the time even though it has none in
the outcome) or a two-in-ten accident. A single arm cannot tell the two apart. A curve can.

The curve is the fraction of "slow" coalescences as the gap moves through the boundary, with **ten seeds per arm** so the
denominators match:

| gap | separation | seeds before | needed |
|---|---|---|---|
| 6.5 | 18.5 | none | **10 new** (601–610) |
| 7.0 | 19.0 | 5 (X150: 601–605) | **5 new** (606–610) |
| 7.5 | 19.5 | 10 (X153: 601–610) | none |
| 8.0 | 20.0 | 5 (X150: 601–605) | **5 new** (606–610) |

Twenty new runs. The three existing arms are already committed, so the whole curve rests on the same readout
(`x142_analyse.world_row`) and the same logging density.

## 1. Manipulation is connected

Same probe (`--init-spots R:SEP`), same inflow `F = 0.030`, same 6 000 steps, dense logging every 10 steps, the same
tolerance-free readout. Only the separation moves, in half-cell steps inside one radius, so nothing but the gap and the
rasterised area differ between arms.

The rasterisation does differ — X153 showed a half-cell separation moves each disc by one cell (110 cells against 108 at a
gap of 7). That is measured per arm, printed, and treated as a confound of the same size in every arm rather than as a
manipulation of its own: the point of this series is the *trend* across four arms of one radius, not the difference
between two adjacent arms.

## 2. Positive control fires (numeric)

Five controls; **the control fires if** all hold:

1. **Ten coalescing-or-not seeds per arm** — the only denominator the fractions can use.
2. **Every dissolution time is a multiple of the 10-step logging quantum** (39, 49, 59 in practice). A time that is not a
   multiple means the logging broke and the arm is void.
3. **The rasterised area is recorded per arm** (first logged frame) and moves by at most 2 cells per disc across the four
   arms; a larger jump means the separation changed the disc, not only the gap.
4. **No arm ends empty** (occupancy ≥ 5 % at the last step) and every coalescing seed has a single component at its
   dissolution step.
5. **The two arms that overlap X153 and X150 reproduce them exactly** (gap 7.5: 10/10 with 8 at 39 and 2 at 49; gap 7.0:
   5/5 at 39; gap 8.0: 3/5). The curve is built partly from already-committed runs, so the overlap is where a stale
   artifact would show up.

## 3. Readout exists and varies

The fraction of slow coalescences is 0/5 at a gap of 7 and 2/10 at 7.5, and the coalescence fraction itself varies (10/10
at 7.5 against 3/5 at 8). Both readouts are known to vary, and both are reported for every arm.

## 4. Sensitivity arithmetic

Ten seeds per arm, four arms. With ten seeds the fraction is resolved to 0.1, and one seed moves it by 0.1; the smallest
difference this design can defend is **three seeds** (0.3). The declared minimal effect is therefore: a monotone rise of at
least 0.3 between the first and the last arm. Anything smaller is declared **below the resolution of the design** in
advance, not after the numbers.

## 5. Refusal rule (fixed before the run)

**Void** if any control in §2 fails.

The registered outcomes:

- **Real width**: the slow fraction rises monotonically (never falling by more than one seed) from 0/10 or 1/10 at a gap of
  6.5 to at least 0.7 at 8.0, with the interior arms in between and at least one interior value strictly between 0 and 1.
  Then the transition has a measurable width in the time while it has none in the outcome, and the width can be quoted as
  a number of cells.
- **Ten-seed noise**: the interior fractions do not order monotonically, or 7.5's 2/10 is not continued by 8.0 being higher
  than 7.0 by at least three seeds. Then X153's two slow seeds were the tail of a binary split, not a width, and the block
  says so and stops quoting a "mix".
- **The curve is a step in the time too**: 6.5, 7.0 and 7.5 all give the same slow fraction and 8.0 jumps to 1.0. Then the
  time has the same whole-cell threshold as the outcome and X153's two slow seeds are the sharp edge of it, which is a
  cleaner result than a width.
- **Contradiction**: any arm reproduces neither X153 nor X150 in the overlap (§2 control 5), or a gap of 6.5 coalesces
  *less* than 7.5. Then an artifact is stale or the readout is not monotone, and no curve is quoted until it is explained.

## Design summary

| factor | value |
|---|---|
| probe | `--init-spots 6.0:{18.5, 19.0, 20.0}` (gap 7.5 reused from X153) |
| runs | 20 new at `F = 0.030`: seeds 601–610 at 18.5, seeds 606–610 at 19.0, seeds 606–610 at 20.0 |
| readouts | class per seed, dissolution time, slow fraction among coalescing seeds, coalescing fraction, rasterised area |
| controls | ten seeds per arm, times on the 10-step grid, area moves ≤ 2 cells, nothing empty, overlap reproduces |
| artifact | `E09_pond/l1_field_x154_mixing.json` |

## Checklist

- [x] connected (the separation moves in half-cell steps inside one radius)
- [x] positive control numeric (times on the 10-step grid, area within 2 cells, overlap reproduces exactly)
- [x] readout exists and varies (0/5 at a gap of 7 against 2/10 at 7.5)
- [x] sensitivity computed (§4: three seeds, 0.3, declared in advance)
- [x] refusal rule written, with width / noise / step / contradiction as separate outcomes

## Status

Registered 2026-11-03 20:30 MSK, before the run. Light field runs, no training.
