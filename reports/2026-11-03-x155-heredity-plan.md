# X155 — is the field's heredity a number of the medium or of the copying rule?

Pre-registration. Registered 2026-11-03 23:45, **before** any analysis of the pairs and before the mutation-off arm.

**Queue item:** `X155_heredity_H2` (claimed by `lead`). **Cost:** 0.1 GPU-hour (two runs) plus CPU analysis.
**Why now:** the manuscript says in §4k that heredity in the field is *assigned, not emerged*, and the support for that
sentence is a correlation between division rate and the stored `inheritability_r` (Spearman +0.79, `reports/2026-11-01-heritability-is-mechanical.md`).
That is an argument about a correlation, not a measurement of heredity. The claim matrix has no row that could be
falsified by a heredity experiment, and every reviewer of the field line will ask for one.

## 1. Manipulation is connected

Two levers, and neither is a new world. (a) The **pairs**: `uid_pairs` and `components_log` are different columns of the same
artifact, so the reconstruction depends on the logger's own book-keeping, not on a new run. (b) The **mutation flag**: the
ablation arm changes `--mutation 0.15 → 0.0` and nothing else, and the anchor run (mutation unchanged, seed 301) must
reproduce `x108_f030_s301.json` key-by-key before the arm is read. If the anchor differs, the flag is not the only
difference and the arm is void — that is the connectivity check, and it is the reason the anchor is a run rather than an
assertion.

## 2. Positive control fires (numeric)

The control is the artifact's own coefficient, which is already published in `selection.inheritability_r` and therefore
cannot be moved by me. **The control fires if** the reconstructed per-world `r` reproduces it to |Δ| ≤ 0.02 in both cells.
That is a numeric, falsifiable check with a known answer: if the reconstruction reads a different number, the pairs are
wrong and no heredity result is reported. A second numeric control: the ablation must remove the trait's variance
(`s_sd_between_last = 0.0` in every run of the arm and ≥ 99 % of pairs exactly equal).

## 3. Readout exists and varies

`r` varies across worlds within a cell (0.815-0.960 at `F` = 0.030, 0.793-0.962 at 0.040), the slope varies (0.874-1.018),
and the horizon `H²` varies by an order of magnitude between worlds (0.00-0.30). So the readout is not saturated and not
constant; a null result would be visible as an interval covering zero, not as a flat column.

## 4. Sensitivity arithmetic

Pairs per world: 160-260; per cell, 176-216 reconstructed pairs with descendants. The expected residual is the mutation's
own `sigma = 0.15`, and with `n ≈ 2 000` the standard error of a slope is about `sigma / (sd_parent * sqrt(n))` ≈ 0.01.
So a slope of 0.95 and a slope of 1.00 are separable at this sample — the question is not underpowered, which is why a
two-run ablation is enough to settle the provenance. The shuffled-parent null has 1 000 permutations, so the smallest
attainable one-sided p is 0.001; that is printed next to the observed value rather than reported as "p < 0.01".

## 5. Refusal rule (fixed before the run)

The verdict table below **is** the refusal rule: no measurable heredity (slope CI covering zero, or the null not rejected,
or the validity control failing) and VOID (validity failing in more than one cell, or fewer than six of ten worlds
reconstructing pairs) are outcomes that end the question, not invitations to re-analyse. The degenerate ablation arm is
covered by the amendment at the end of this file, which states its fallback criterion and that it was written after the
data.

## Question

Three questions, in the order the numbers can answer them.

1. **Validity.** Can the parent–daughter pairs be reconstructed from the stored logs, and does the reconstruction
   reproduce the artifact's own `selection.inheritability_r`?
2. **Quantity.** What is the broad-sense heredity of the trait at the horizon — the share of between-structure variance
   in `s` that sits between lineages rather than within them — and how much of a daughter's deviation from its parent
   does the mutation rule explain?
3. **Provenance.** Does the measured heredity survive the controls that would make it a property of the medium rather
   than of the assignment in `field_track.py`?

## Sample (fixed now)

| series | worlds | why |
|---|---|---|
| `x108_f030_s301…310` | 10 | dense logs (field and components at every 10 steps), 6 000 steps, the series X101–X107 already used |
| `x108_f040_s301…310` | 10 | the maze cell, same seeds, so the comparison is paired |
| `x126_f035_s301…310` | 10 | replication in the third cell; **read only after the first two cells are analysed**, so it is a replication and not a third chance |

Nothing else. If a reconstruction fails on a run, that run is reported as dropped, with the reason, and not replaced.

## Estimators (fixed now)

1. **Pair reconstruction.** For each `(parent, daughter)` in `uid_pairs`, find the first logged step at which the
   daughter's uid appears in `components_log` and **both** uids are present; take `(s_parent, s_daughter)` at that step.
   This is a proxy for the split moment, displaced by at most one logging quantum (10 steps); the displacement is
   reported as a caveat, not corrected.
2. **Validity control.** Pearson `r` over the reconstructed pairs against the artifact's stored
   `selection.inheritability_r`. **Tolerance |Δ| ≤ 0.02**, because the stored value is computed at the exact split step
   and the reconstruction is not. A larger gap means the reconstruction is wrong and no heredity number is reported.
3. **Slope.** OLS of `s_daughter` on `s_parent`, per world; bootstrap 95 % CI over **parent uids** (clusters), 2 000
   resamples, pooled across worlds by seed.
4. **Shuffled-parent null.** Within each world, permute the parent values across pairs; 1 000 permutations; report the
   null mean and the one-sided empirical p for the observed slope.
5. **Division-rate partial.** The parent's number of daughters (its out-degree in `uid_pairs`) is a covariate; report
   the partial slope of `s_daughter` on `s_parent` given that count, with the same bootstrap.
6. **H² at the horizon.** At the last logged step, group components by lineage root (union-find over `uid_pairs`;
   merged bodies that appear under a new uid are their own roots, and that is stated). Report
   `H² = 1 − SS_within / SS_total` for `s`, i.e. the share of variance that is between lineages.
7. **Decomposition of the daughter's deviation.** `Var(s_daughter − s_parent)` against the mutation rule's own
   `sigma = 0.15`: if the residual variance is the rule's variance and nothing else, the heredity is the rule's.

## Phase 2 (the ablation arm)

Two runs at `F = 0.030`, seeds 301 and 302, the identical command of `scripts/x108_series.py` except `--mutation 0.0`,
plus **one anchor run** (seed 301, mutation unchanged) that must reproduce `x108_f030_s301.json` key-by-key. The anchor
is required because the flag is the only change and the point of the arm is that everything else is held.

## Decision rule (registered)

Report the numbers under all outcomes; the **verdict** is decided by this table, not by preference:

| verdict | criterion |
|---|---|
| **HEREDITY IS THE RULE** | `r` in the mutation-off arm ≥ 0.99 and its slope ≥ 0.95, while the mutation-on arm's residual variance is explained by `sigma` within a factor of two |
| **HEREDITY IS PARTLY THE MEDIUM** | the mutation-off arm is *not* near-perfect (`r` < 0.99 or slope < 0.95), and the mutation-on arm's slope survives the division-rate partial (CI off zero) and the shuffled-parent null (p < 0.05) |
| **NO MEASURABLE HEREDITY** | the slope's CI covers zero, or the shuffled-parent null is not rejected, or the validity control fails |
| **VOID** | the validity control fails on more than one cell, or fewer than six of ten worlds reconstruct pairs |

The last row is a real possibility and is written down so that it cannot be discovered after the fact as an excuse.

## What would change if the verdict is HEREDITY IS THE RULE

The manuscript's §4k sentence stays, but gains a number: the heredity coefficient is the rule's fidelity, `H²` at the
horizon is a statement about the *trait's* variance and not about transmission, and the line's heredity claim moves from
"assigned" (an assertion) to "measured, and assigned" (a result). No new physics, no new world.

## What would change if PARTLY THE MEDIUM

The manuscript's sentence is wrong in its strong form and must be replaced; the trait then has a transmissible component
that the assignment does not create, which would be the first positive heredity result of the line and would justify a
follow-up series. That outcome is the reason this pre-registration exists rather than an exploratory pass.

## Amendment, written after the data (2026-11-04 00:05)

The ablation arm did not behave as this plan assumed, and the difference is recorded here rather than absorbed silently.

The plan's row 1 criterion assumes the mutation-off arm has a coefficient: `r ≥ 0.99` and slope `≥ 0.95`. It has no coefficient
at all. With `--mutation 0.0` the trait is constant — `s = 1.0` in every component at every step, `s_sd_between_last = 0.0`, and
100 % of reconstructed pairs exactly equal — so `r` and the slope are undefined (zero variance in the denominator). The
registered criterion could not be evaluated as written.

The fallback, chosen now and labelled post hoc: the arm counts as the "near-perfect" limit if (a) the between-component sd at the
horizon is 0 in every run, (b) at least 99 % of reconstructed pairs are exactly equal, and (c) the mutation-on arm's residual sd
falls within a factor of two of the rule's `sigma`. All three hold (0.0 / 100 % / 0.1487 and 0.1495 against 0.15), so the
verdict in the report is **HEREDITY IS THE RULE** under the amended reading. No other criterion changed, and the amendment is
written before the verdict was entered into the aggregate's `verdict` block, but **after** the runs — it cannot be presented as
a pre-registration.

What this teaches the protocol: a "near-perfect" criterion must be written for the degenerate case, because the strongest form of
perfect transmission is a vanished variance, not a coefficient of one. `docs/design-checks.md` gains that rule.
