# X156 — is a shape measured from the field itself inherited? (pre-registration, 04.11.2026)

Status: planned, written **before** the series. Owner: `lead`. Cost: about 0.01 GPU-hours (twenty runs, CPU-capable,
20–25 s each).

## Question

X155 closed the field line's heredity question with a measurement and one uncomfortable sentence: the daughter-on-parent
slope of the tracked trait is 0.9837 [0.9680, 1.0002] *because the tracking rule writes the trait into the daughter*,
and with the rule's noise ablated the trait has no variance at all. What is inherited, in other words, is a number that
the bookkeeping copies; nothing in the chemistry carries it.

That closes the question only for the trait we chose. A pattern-forming medium plausibly transmits **shape**: a daughter
budded off a ridge inherits the ridge's orientation and width before anything else about it is decided. Shape is not
written by the tracker — it is computed from the field — so a heredity measurement on shape is a measurement of the
medium and not of our bookkeeping.

Question: **is a shape trait measured from the field inherited across divisions in this medium, and if so with what
fidelity?**

## Observable

Two per-component traits, computed from the `v` field at each logging step, with the component's own pixels:

- **elongation** `e = sqrt(λ₁/λ₂)`, from the two eigenvalues of the second-moment matrix of the component's pixel
  coordinates. `e = 1` for a round body, larger for a ridge; dimensionless.
- **width** `w = 2·sqrt(λ₂)`, the minor-axis extent in cells — a length, directly comparable to the medium's 12-cell
  wavelength.

Both are pure functions of the field, computed after the step, using no random numbers: the observer cannot perturb the
trajectory (checked by the anchor, §1 below).

Reference traits in the **same runs**, with known expectations from X155 and from the division geometry:

- **`s`** — the assigned trait, expected slope ≈ 0.98: the positive control that the reconstruction works.
- **area** — a daughter is a part of its parent, expected slope ≈ 0.5: the control that the readout can see a
  transmitted quantity that is *not* copied perfectly.

## Design

Twenty runs: two habitats (`F` = 0.030 spots, `F` = 0.040 connected) × ten seeds, 6 000 steps, `--sample-every 10`,
`--split-new-uid`, all other flags as in the production configuration (`scripts/x108_series.py`). Seeds 801–810, so no
seed is reused from another series.

Pairs are reconstructed exactly as in X155: a split gives both daughters new identifiers, so a parent is read at its last
logged step before the daughter's first logged step, and the daughter at her first. Pairs are grouped by parent uid for
the bootstrap (2 000 resamples), and the shuffled-parent null permutes parents within a world (1 000 permutations).

Slopes are estimated for each trait with the daughter as the response; a partial slope given `log area` separates shape
from size; and the slope is estimated separately by **daughter age** — the number of logging steps between the daughter's
first appearance and the step at which she is read (1, 2, 3+) — because a transmitted shape that relaxes towards the
medium's typical shape will show a slope that decays with age, while a copied number will not.

## 1. Manipulation is connected

The intervention is the observer, not the world: the same command line with `--shape-log` added to a reference run must
produce a **bit-identical** `series` (all fields except the new `shape` block), because the observer is a pure function
of the state and draws no random numbers. Checked with `python scripts/check_determinism.py` on the two artifacts, and
the new flag is off by default so every existing series is unaffected.

Failing this check stops the series: an observer that changes the world would make every number below uninterpretable.

## 2. Positive control fires (numeric)

In the new runs the assigned trait `s` must reproduce X155. The control **fires if** the daughter-on-parent slope falls inside the pre-registered band `[0.90, 1.05]` in both habitats — a threshold, not a sign test. The reconstruction code is the same, so a deviation means the new artifacts were produced under a different configuration than intended.

Second control, same runs: **area slope in `[0.35, 0.65]`**, centred on the geometric expectation 0.5, and it fires if the interval contains 0.5. A slope near 1
here would mean the pairs are being formed from the wrong step (a daughter compared with itself), and a slope near 0
would mean the readout cannot see transmission at all.

## 3. Readout exists and varies

`elongation` and `width` must have between-component standard deviation above `0.03` and `0.3 cells` respectively in every
world, and the pair count per habitat must exceed 200. Measured on the pilot world before the series; reported in the
aggregate as `readout_sd` with the observed range.

## 4. Sensitivity arithmetic

From the pilot: `sd(elongation)` ≈ 0.15 and `sd(width)` ≈ 0.9 cells (to be confirmed and recorded before the series).
With n ≈ 2 000 pairs clustered in ≈ 10 worlds, the standard error of a slope is of order `sd/(sqrt(n)·sd_parent)` ≈
0.01, so any slope above 0.1 is distinguishable from zero and the decision boundaries below (0.3 and 0.7) are far outside
the noise. If the pilot gives `sd(elongation) < 0.05`, the trait is too uniform to measure and the series is not run: it
would be insensitive by construction.

## 5. Refusal rule (fixed before the run)

The series is declared **VOID** and nothing is published if any of these holds:

- the anchor (§1) is not bit-identical;
- the `s` control (§2) leaves `[0.90, 1.05]`;
- the area control (§2) leaves `[0.35, 0.65]`;
- `sd(elongation) < 0.05` or fewer than 200 pairs per habitat (§3);
- more than 5 % of runs fail.

## Decision table (fixed before the data)

Read **elongation** first, then `width`; the `s` and area controls decide whether the reading is admissible.

| outcome | reading |
|---|---|
| elongation slope ≥ 0.70 with the shuffled null below 0.30 | **SHAPE IS INHERITED** — the medium transmits shape nearly as faithfully as the rule transmits `s`; heredity in this medium is not only bookkeeping, and X155's conclusion must be narrowed to the assigned trait |
| 0.30 ≤ slope < 0.70, and the slope decays as the daughter ages | **SHAPE RELAXES** — shape is partially inherited and then relaxes towards the medium's typical shape; the relaxation rate is the new number |
| 0.30 ≤ slope < 0.70, and the slope does not depend on the daughter's age | **SHAPE IS WEAKLY TRANSMITTED** — a real but noisy transmission with no measurable relaxation |
| slope < 0.30, or the shuffled null reaches the observed slope | **SHAPE IS NOT INHERITED** — the only heritable thing in this medium is what the tracker writes; X155's conclusion extends from `s` to any field-measured shape |
| any condition of §5 | **VOID** |

## What would make this uninteresting

A slope near 1 for elongation would be interesting only if the partial slope given area stays high — otherwise the
"shape" being transmitted is just "big bodies have big daughters", which is the area result in disguise. The report must
therefore quote the partial slope, not only the marginal one.

## After the run

Report in `reports/2026-11-04-x156-shape-heredity.md`, aggregate in
`morphogenesis/experiments/E09_pond/l1_field_x156_shape_heredity.json`, a §4k.5 fragment in the manuscript, a row in the
README ledger and in `docs/plan/10d-field-metrics-and-form.md`, a CLAIMS row, and — if the outcome is one of the first
three rows — a §4.8 in `articles/029` as v2.1. The next hypotheses are written there, not here.
