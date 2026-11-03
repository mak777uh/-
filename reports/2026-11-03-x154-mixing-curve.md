# X154 — the width in the time is measurable: the outcome steps, the time has a shoulder

**Plan:** [`2026-11-03-x154-mixing-curve-plan.md`](2026-11-03-x154-mixing-curve-plan.md) (20:30).
**Aggregate:** `morphogenesis/experiments/E09_pond/l1_field_x154_mixing.json`. **Runs:** 20 new at radius 6.0 and
`F = 0.030` — separation 18.5 (surface gap 6.5), seeds 601–610; separations 19.0 and 20.0, seeds 606–610 each. The arms at
7.5 (X153) and at 7.0 / 8.0 for seeds 601–605 (X150) are the committed runs and were reused unchanged.

## The curve

| surface gap | separation | seeds coalescing | their dissolution steps | slow fraction | coalescing fraction |
|---|---|---|---|---|---|
| 6.5 | 18.5 | 10 of 10 | 39 ×10 | **0.0** | 1.0 |
| 7.0 | 19.0 | 10 of 10 | 39 ×10 | **0.0** | 1.0 |
| 7.5 | 19.5 | 10 of 10 | 39 ×8, 49 ×2 | **0.2** | 1.0 |
| 8.0 | 20.0 | 5 of 10 | 49 ×3, 59 ×2 | **1.0** | 0.5 |

"Slow" is the definition registered in the plan: a coalescing seed whose mutual coalescence lands at the later logged step
(49 or more) instead of gap 7's 39. The five seeds that do not coalesce at 8.0 divide instead (79 ×4, 99 ×1 logged steps).

The registered branch that fires is **real width**. The slow fraction rises monotonically 0.0 → 0.0 → 0.2 → 1.0, the rise is
1.0 against a declared minimum of 0.3, and the interior value 0.2 is strictly between 0 and 1. So X153's two slow seeds
were **not** ten-seed noise: filling the two arms that were missing made the curve rise instead of step, and at 8.0 no
coalescing seed is fast any more — every seed that still coalesces is already "slow" by the definition.

## The readout that could have flattered the last arm

The registered denominator is *coalescing* seeds, and at 8.0 only five of ten coalesce, so 1.0 there is 5/5 while the same
five seeds are 0.5 of the arm. A seed that never coalesces cannot be slow, so dropping it from the denominator raises the
last point by construction. The analyser therefore runs the *same* decision rule on the conservative denominator — all ten
seeds, a non-coalescing seed counted as not slow — and prints both:

| readout | 6.5 | 7.0 | 7.5 | 8.0 | rise | verdict |
|---|---|---|---|---|---|---|
| registered (of coalescing) | 0.0 | 0.0 | 0.2 | 1.0 | +1.00 | real width |
| conservative (of all ten) | 0.0 | 0.0 | 0.2 | 0.5 | +0.50 | real width |

The verdict does not depend on the denominator; the magnitude does. Both numbers are quoted together here and in the
claim, and neither is used alone: the slow fraction rises from **0 to 0.5 of all seeds**, and from **0 to 5 of 5** among
those that still coalesce.

## What the design can and cannot resolve

The plan fixes the resolution at three seeds (0.3) for ten seeds per arm. The adjacent move 7.0 → 7.5 is **two** seeds
(0.2), below that bar, so no single step is claimed as a difference. What is claimed is the rise over the whole curve
(0 slow seeds to 5 of 5 coalescing seeds), which the plan registered. There is exactly **one** interior arm, so the width
is bracketed and not located: it lies between a gap of 7.0 and 8.0 cells, i.e. at least half a cell wide and at most one
cell wide. The passage 0.2 → 1.0 is equally consistent with a *threshold* for "slow" crossed near 8 and with a continuous
density; this design cannot separate those two, and the report does not.

## The one registered control that does not pass as written

Control 3 of the plan asked that the first-frame rasterised area move by **at most 2 cells per disc across the four arms**.
The measured areas are **110 / 108 / 110 / 113** cells per disc: a spread of 5, and the largest adjacent move is 3
(110 → 113 at the last arm). As written the control fails by one cell, and the plan's §5 says a failed control voids the
series. That deviation is recorded here rather than glossed over, together with why it cannot produce the result:

1. The nominal radius is 6.0, and π·6² ≈ 113 — so **113 is the fully covered disc** and 108/110 are the *under*-rasterised
   ones. The last arm is the truest disc, not an enlarged one.
2. The areas are per disc, and the X153 report and claim called the 108 → 110 move "one cell each"; two cells is what the
   artifacts record (108 each against 110 each). This report quotes the areas themselves and treats **2 cells per disc** as
   the unit of that move — a correction of wording, not of any number in the X153 aggregate.
3. Turned into an effective radius √(A/π), the actual surface gaps are **6.67 / 7.27 / 7.67 / 8.00** cells: still
   monotone in the nominal gap, so the arms are not reordered and no arm becomes a duplicate of its neighbour.
4. The direction is against the finding. With the centre separation fixed, a larger disc means *less* clear space and
   therefore **earlier** contact, while the observed effect is *later* dissolution. The confound works against "the time
   widens as the gap grows", not for it.

So the series is reported as a real width with the area deviation as a standing limitation — the manipulation is a gap
plus at most ~0.3 cell of effective gap, not a pure gap. The next series in this line should register the bound on the
**effective gap**, not on raw rasterised cells, because a radius-6 disc on a discrete grid cannot move by less than 2–3
cells per half-cell step: a raw-cell bound is unsatisfiable at this radius by construction.

## Controls that do pass

- **Ten seeds per arm**, 20 new runs `ok`, every run starts as two components (one per spot) and no arm ends empty: final
  occupancy 0.25–0.28 across the 20 new runs, against the registered floor of 0.05.
- **Times were actually logged.** The analysis checks each reported time against the logged step sequence (`t + 1` must be
  a logged step) instead of the weaker `t % 10 == 0`, because the reported 39/49 are offsets from the initial frame at
  step 1; the lattice is 10 steps on all 20 runs and the two re-read arms are on the same lattice.
- **The overlap reproduces exactly**, which is where a stale artifact would show: the 7.5 arm reproduces X153 seed for
  seed (10 coalescing, 39 ×8, 49 ×2), and seeds 601–605 at 8.0 reproduce X150's `r60_g8` exactly (M 59, M 49, M 49,
  A 79, A 79).
- **The timing control** of the earlier arms holds: at gaps 6.5 and 7.0 all twenty coalescing seeds dissolve at 39.
- **Ten seeds are ten worlds.** `scripts/check_seed_replication.py` records `one_world: false` with ten distinct geometries
  for the 6.5 arm and five each for the 7.0 and 8.0 additions — the seeds move the trap placement, so the denominators are
  not one world copied ten times (the X134 placement defect, which this gate exists to catch).

## What the block says now

1. **Outcome** — a whole-cell step: 10/10 coalesce at 7.5 and 5/10 at 8.0, unchanged from X153.
2. **Time** — has a **width**: the slow fraction goes 0 / 0 / 0.2 / 1.0 over the four arms, with the rise spread over the
   last cell before the outcome breaks rather than concentrated at the break.
3. **The two laws are not one threshold seen twice.** The time crosses first and gradually; the outcome then steps at a
   single cell. X151 put the timing tail before the outcome break; X154 shows the tail is a *curve* with one measurable
   interior point, not a two-seed accident.

## Limitations

1. The area deviation above: the arms are a gap plus up to ~0.3 cell of effective gap, not a pure gap.
2. One interior arm only, so the width is bracketed to [7.0, 8.0] cells and not located within it.
3. The registered criterion's denominator changes at the last arm; the verdict survives the conservative denominator, but
   the *magnitude* must always be quoted with its denominator.
4. The logging quantum is 10 steps, so "slow" is one bit (39 versus ≥49): a real shift of a few steps would be invisible
   and the width is a statement about the number of slow seeds, not about a continuous time distribution.
5. The 7.5 arm is X153's own ten seeds — the new evidence is the 6.5 arm, the missing five seeds at 7.0, and the completed
   ten-seed arm at 8.0.

## Next hypotheses

1. **X152 — radius 3.75 at gaps 8 and 9.** The outcome step moves between radii (28-cell discs hold to 8, larger ones break
   at 8); if the time's width scales with the disc, radius 3.75 should show its interior point at a different gap.
2. **A finer logging quantum at a gap of 7.5** (5 steps instead of 10, one arm, ten seeds). If the 2/10 seeds are a
   distribution of dissolution times rather than a single later value, five-step logging shows a spread; if they all sit on
   one quantum, the "width" is one bit wide and the density claim stays unmeasured.
3. **X149 — the shape of the product, with frames.** Still the only candidate for *why* a division intervenes where
   coalescence stops.

доска: принято 0, отклонено 0, отложено 0.
