# X156 — is a shape measured from the field itself inherited? (closed 04.11.2026)

Status: closed. Pre-registration: `reports/2026-11-04-x156-shape-heredity-plan.md` (five design checks, written before
the series; one dated amendment, below). Aggregate: `morphogenesis/experiments/E09_pond/l1_field_x156_shape_heredity.json`
(`scripts/x156_analyse.py --write`), series `scripts/x156_series.py`, artifacts
`morphogenesis/experiments/L1_field/x156_shape_f030_s801..810.json` and `x156_shape_f040_s801..810.json`. Cost: 20 runs,
0.01 GPU-hours (CPU), about 35 minutes.

## The question, and why it is not the same question X155 answered

X155 closed the heredity of the **assigned** trait with a measurement and an ablation: the daughter-on-parent slope is
0.9837 [0.9680, 1.0002], the scatter equals the mutation parameter, and with mutation switched off the trait has no
variance at all. What is inherited there is what the tracking rule writes into the daughter. That closes the question for
`s` only.

A shape measured from the field is a different object: nobody writes it, it is computed from the pixels the medium
produces. If a daughter budded off a ridge inherits the ridge's elongation, the heredity is a property of the medium.
So: **is a shape trait measured from the field inherited across divisions, and with what fidelity?**

Traits, both read from the `v` field at every tenth step (`--shape-log`, an observer that draws no random numbers):

- **elongation** `e = sqrt(λ₁/λ₂)` from the second-moment matrix of the component's pixels (1 = round);
- **width** `w = 2·sqrt(λ₂)`, the minor-axis extent in cells.

Reference traits in the same runs: the assigned `s` (expected ≈ 0.98, the positive control) and **area** (expected ≈ 0.5,
because a daughter is part of its parent — the control that the readout can see a quantity transmitted *imperfectly*).

## Anchor and design checks

- **Anchor: passed.** The same command with and without `--shape-log` produces a bit-identical `series` after the two new
  keys are removed (81 of 81 rows; the two anchor artifacts are produced by the command in the reproduction section, and the comparison script removes the new keys before testing equality); the flag is off by default, so every existing
  series is unchanged.
- **1. Manipulation connected:** the intervention is the observer, and it is a pure function of the state; bit-identical
  above.
- **2. Positive control fires:** `s` slope 0.9959 [0.9790, 1.0126] (f030) and 0.9817 [0.9631, 1.0003] (f040) — inside the
  pre-registered [0.90, 1.05]. Area slope 0.4514 [0.4264, 0.4771] and 0.4481 [0.4193, 0.4723] — inside [0.35, 0.65], and
  within 0.01 of the geometric expectation 0.5.
- **3. Readout varies:** `sd(log elongation)` 0.739 (f030) and 0.524 (f040); `sd(log width)` 0.511 and 0.758. Pairs:
  2 249 (f030) and 1 862 (f040), of 2 256 and 1 869 edges.
- **4. Sensitivity:** with ≈2 000 clustered pairs the slope standard error is ≈0.03, so the 0.30 and 0.70 decision
  boundaries are far outside the noise — confirmed by the intervals below, whose widths are 0.06–0.13.
- **5. Refusal rule:** not triggered by any of its five conditions.

**Amendment 1 (dated 04.11, 02:05, after the first five runs and before the full analysis).** Elongation and width are
heavy-tailed (elongation median 1.28, p90 14.7, max 84.5 — a body in the lattice is often a long thin arc), so the primary
statistic is the slope on the **logarithm** of each shape trait, the elasticity of the daughter with respect to the
parent; raw slopes are reported alongside. Shape traits are defined only where the second moment is meaningful (area ≥ 10
cells, width ≥ 1 cell; 0.06 % of rows excluded). Why this is an amendment and not a choice hidden in the code: the
decision boundaries in the plan were set for a linear statistic.

## Result

**The medium does transmit shape, partially, and the habitat decides which aspect.**

| trait | f030 (lattice) | f040 (connected) |
|---|---|---|
| `s` (control) | 0.9959 [0.9790, 1.0126] | 0.9817 [0.9631, 1.0003] |
| area (control) | 0.4514 [0.4264, 0.4771] | 0.4481 [0.4193, 0.4723] |
| **log elongation** | **0.6074 [0.5399, 0.6785]** | 0.4260 [0.3585, 0.4924] |
| **log width** | 0.3384 [0.2877, 0.3850] | **0.6238 [0.5846, 0.6672]** |
| elongation, raw | 0.5328 [0.4443, 0.6352] | 0.7484 [0.6311, 0.8701] |
| width, raw | 0.3383 [0.2344, 0.4287] | 0.4735 [0.4338, 0.5151] |

Reading:

1. **Shape is not free of heredity, and it is not the tracker's heredity either.** All four log-shape slopes are between
   0.29 and 0.68, their shuffled-parent nulls are −0.001 to +0.002 with p = 0.001, and the partial slope given log area
   stays at 0.26–0.65, so this is not area in disguise. The assigned trait is transmitted at 0.98 in the same runs: the
   difference between 0.98 and 0.5 is the difference between a number the bookkeeping copies and a shape the medium has to
   reproduce.
2. **The aspect that is inherited swaps with the habitat.** In the lattice elongation is transmitted better than width
   (0.607 against 0.338, intervals disjoint); in the connected mass width is transmitted better than elongation (0.624
   against 0.426, intervals disjoint). The two habitats differ in the same trait by more than their intervals allow
   (elongation 0.607 against 0.426; width 0.338 against 0.624). In a lattice of round spots the ridge orientation is the
   thing a division can pass on; in a connected mass the local width of the labyrinth is.
3. **Nothing relaxes on the timescale we can see.** Reading the daughter 1, 2 or 3 logged steps after her first
   appearance moves the slope by at most 0.05 (log elongation f030: 0.607 → 0.579; log width f040: 0.624 → 0.571), below
   the pre-registered 0.10 that would have made "relaxes towards a typical shape" the reading. The value of the trait is
   set at birth, not restored afterwards.
4. **The level is about half.** Averaged over habitats, elongation 0.517 and width 0.481. A slope of 1 would mean the
   daughter is a scaled copy of the mother; 0.5 means she is, on average, halfway between her mother and the habitat's
   typical shape — the geometric control (area, 0.45) sits in the same place, which is what a part-of-a-parent relation
   looks like when the medium sets the scale.

## What this changes about X155

X155's sentence — "the only heritable character is one our own analysis writes into them" — is now too strong by one
clause. The correct statement: **the only *perfectly* heritable character is the one the bookkeeping writes; shape is
heritable at about half, in a direction the habitat chooses.** Both halves matter. The first is what a reader of
parent–daughter correlations needs to know (a correlation of 1.0 can be bookkeeping); the second is what makes this
medium's entities more than labels — a daughter really does resemble her mother's shape more than a random body's, and
which resemblance you see depends on where she grew.

## Limits

1. **Shape is thresholded.** The traits are computed from the component at `v > 0.2`; a different threshold moves the
   effective radius and therefore the gap of X157, and would move the shape slopes too. Not tested.
2. **Two habitats, twenty worlds.** The swap is a contrast between two populations of ten worlds; the intervals are
   disjoint, but a third habitat (a different `F`) would be needed to say whether the swap is a continuum or a switch.
3. **Log transform.** The primary statistic is a log slope chosen after seeing the tails (amendment 1). The raw slopes
   agree in sign and rough size but are more variable (0.53/0.75 for elongation), so the conclusion does not hinge on the
   transform.
4. **No mechanism.** Nothing here says *how* a daughter inherits her mother's elongation — a shared local supply pattern
   and the geometry of the split are both sufficient. The ablation that would separate them (an imposed supply pattern
   with a fixed orientation) is not run.
5. **One threshold for "daughter".** A pair is counted when the tracking rule assigns a new identifier; bodies that split
   below the area floor never enter the data.

## What would kill the claim

A third habitat in which both aspects give the same slope, or a re-run at threshold 0.1/0.3 in which the elongation and
width slopes converge, would reduce the result to "shape is heritable at about half, no structure". The swap needs one
more habitat to become a law rather than a contrast.

## Literature (board: accepted 1, rejected 0, deferred 0)

`library/hypotheses/shape-heredity-x156.md` — 12 verified sources. Size selection in Gray–Scott spots is well documented
(Pearson 1993, Science), quasi-equilibrium spot profiles with discrete stable widths exist (Chen & Ward 2011; Burke &
Knobloch 2006), fusion is described as discrete events with distance-dependent interaction (Purwins 2010; Bödeker 2004),
and heredity without replicators exists for composition (Segré 2000) and weakly for spot dynamical type (Takagi & Kaneko
2001). **No source measures parent–daughter elongation or width correlation in a pattern-forming medium, or the
relaxation of shape with daughter age** — so the level (about half) and the habitat-dependent direction are the new
content, and the null that size-triggered division explains it is only partly excluded (partial slopes given area).

## Next hypotheses

1. **A third habitat** (`F` = 0.035, mixed) decides whether the swap is a continuum or a switch; twenty runs, same cost.
2. **Threshold robustness** at 0.1 and 0.3, on a subset of ten worlds: if the swap survives, it is a property of the
   field and not of the mask.
3. **Supply anisotropy**: impose a supply pattern with a preferred orientation and ask whether the elongation slope rises
   above 0.6 when the medium has a direction — the cheapest test of "shared local supply" against "geometry of the split".
4. **Selection on shape**: is the daughter's shape correlated with her survival (X126's fate classes), i.e. is there
   selection on the heritable part? This is the question the whole X155/X156 pair was built to make askable.
