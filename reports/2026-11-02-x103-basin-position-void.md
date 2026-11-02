# X103 — where in the mother's basin? A void, and the diagnosis is worth more than the run

**Plan:** [`2026-11-02-x103-basin-position-plan.md`](2026-11-02-x103-basin-position-plan.md) (registered 16:55 MSK, before the
analysis). **Aggregate:** `morphogenesis/experiments/E09_pond/l1_field_x103_basin_position.json`. Analysis of X100's stored
snapshots; no GPU, no new runs.

## Verdict

**Void by the registered coverage gate** — `F = 0.040` reached coverage **0.599** against the declared floor of 0.60, by a
thousandth. The gate fired exactly as written and the analysis is recorded as a void, not as a result.

The diagnosis is the useful part: the gate was counting the wrong denominator.

| inflow | ancestor–daughter pairs | of which both peaks are logged | usable | coverage | coverage among **loggable** pairs |
|---|---|---|---|---|---|
| 0.030 | 2 165 | 2 024 | 1 970 | 0.910 | **0.973** |
| 0.040 | 1 761 | 1 139 | 1 054 | 0.599 | **0.925** |

Of the 1 761 pairs at 0.040, **622 (35 %) have an ancestor or a daughter that was never logged at all** — the structure lived and
divided between two component-log samples. At this inflow the median lifetime is 89 steps (X92) and the logging interval is 50, so
short-lived structures are invisible by construction. The instrument itself was available for 92–97 % of the pairs that exist in
the logs; the registered denominator mixed "the instrument failed" with "the world never showed this structure".

**The rule earned:** a coverage gate must say *which* pairs its denominator contains. A gate whose denominator includes
structurally unobservable cases measures the logging resolution of the world, not the availability of the measurement — and it
voids a good analysis for the wrong reason. Written into `docs/design-checks.md`.

## The numbers, recorded as exploratory (no claim)

Same pairs, same definitions as X102; the positive control fired (the mother's excursion area still predicts the daughter's,
0.531 / 0.408 on these subsets, against 0.531 / 0.384 on the full samples).

| inflow | pairs used | median birth distance (cells) | median basin radius | born outside the basin | ρ(distance, daughter) | ρ(r, daughter) | ρ(mother area, daughter) | partial: area given distance | partial: distance given area |
|---|---|---|---|---|---|---|---|---|---|
| 0.030 | 1 970 | 4.82 | 9.9 | 0.201 | **−0.033** | −0.053 | 0.531 | **0.576** | −0.264 |
| 0.040 | 1 054 | 10.28 | 9.1 | 0.571 | **−0.340** | −0.304 | 0.408 | **0.574** | −0.537 |

Two readings survive, and they pull in opposite directions:

1. **The distance carries independent information** — and at 0.040 a lot of it: a daughter born farther from her mother's peak is
   smaller, `ρ = −0.34`, and the relation survives partialling out the mother's area (`−0.54`). At 0.030 the same coefficient is
   zero (−0.03). So *if* this is real, heredity is topographic only in the percolating cell, which is the cell where "distance from
   a peak" and "half-width of the labyrinth stripe" are nearly the same coordinate — the readout may be measuring the local width
   of the maze rather than the mother.
2. **The mother's area does not lose its power when the position is known** — it gains a little (0.531 → 0.576, 0.408 → 0.574).
   That is the opposite of the preregistered "topographic reading wins" condition, which required the area's coefficient to fall
   by 0.15. On this criterion the skirt reading is not refuted even in the cell where distance matters.

So the exploratory picture is *additive*, not substitutive: where a daughter is born adds a geometric term at the percolating
inflow, and does not replace the inherited excursion width at either inflow. That is a hypothesis for the re-registration below;
it is not a result, because the registered gate failed and because at 0.040 the predictor is confounded with the local stripe
width by construction.

## What is re-registered (X103b)

`reports/2026-11-02-x103b-basin-position-plan.md`, with three changes and nothing else:

1. **Denominator stated:** the gate is `coverage_logged ≥ 0.90`, i.e. the instrument's availability among pairs whose peaks exist
   in the logs; the structural loss is reported separately as a selection fact (**622 / 1 761 at 0.040**).
2. **Selection is measured, not assumed:** the dropped pairs are compared with the kept ones on mother area, daughter area and
   daughter lifetime (medians, and a two-sample rank test). If the kept subset is systematically the long-lived one, the report
   says which way the numbers are biased.
3. **The confound is named and addressed:** at 0.040 the primary predictor is the **normalized radius** `r = distance / R_basin`
   (already computed here: −0.053 and −0.304), and the absolute distance is reported as the secondary, because `r` divides out the
   basin's own scale.

## Caveats carried forward

- One box, one grid, one `k`, one excursion cut; the response is X100's threshold-0.20 area, so X99's cut sensitivity applies.
- The daughter's birth position is her centroid at her first logged appearance, and the mother's basin is taken at her own peak
  frame — the two frames differ. Positions are physical quantities (they survive a frame change), unlike the labels X102 had to
  correct; but a mother that has drifted between frames moves the origin of the measurement.
- Ten worlds per inflow.

## Design rules earned (added to `docs/design-checks.md`)

1. **A coverage gate names its denominator.** "Coverage" is meaningless without saying whether the denominator is all pairs, pairs
   with both peaks logged, or pairs with a usable instrument; the number differs by 30 points between the first two.
2. **A void's diagnosis is part of the void.** This one cost a run and produced a rule and a better re-registration; a report that
   only said "void by coverage" would have lost both.

## X103b: the denominator was not the last defect — the basin was

Re-registered as [`2026-11-02-x103b-basin-position-plan.md`](2026-11-02-x103b-basin-position-plan.md) with the denominator
changed to the instrument's availability (gate 0.90) and with a **selection control**: median daughter area, kept versus dropped,
must lie in [0.75, 1.33]. Aggregate: `l1_field_x103b_basin_position.json`.

It **voided again**, and for a reason worth keeping:

| inflow | usable | coverage among loggable pairs | median daughter area kept / dropped | ratio | verdict |
|---|---|---|---|---|---|
| 0.030 | 1 970 | 0.973 | 53.0 / 80.0 | **0.662** | void (selection) |
| 0.040 | 1 054 | 0.925 | 168.0 / 135.5 | 1.24 | passes selection, but the cell is not the one with the defect |

The 54 pairs lost at `F = 0.030` are pairs whose mother's peak pixel has **no drainage basin at all** (a mother on a ridge or in a
dead patch) — and their daughters are much larger than average. So the basin definition does not lose a random subset: it loses
the pairs whose mothers sit on structure boundaries, which are exactly the ones that produce large excursions. Selection ratios of
0.66 measured on 54 pairs are noisy, but the design cannot be rescued by arguing about the interval: the missing quantity is not
random, and the honest consequence is that **the question must be asked without the basin**.

That is X103c, and it answers the question — see
[`2026-11-02-x103cd-birth-distance.md`](2026-11-02-x103cd-birth-distance.md).

доска: принято 0, отклонено 0, отложено 0.
