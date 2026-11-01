# Decision rules from the four reviews

1 November 2026. Four independent literature reviews answered the seven questions of
[`../reports/2026-10-31-questions-next-run.md`](../reports/2026-10-31-questions-next-run.md). The references they
produced are harvested in [`lit-model-run-2026-11-01.md`](lit-model-run-2026-11-01.md), with every DOI checked and four
of them corrected. **This page keeps the other half**: the rules of procedure they agreed on, the checks they proposed,
and — where our own stored data can settle the question cheaper than any review — what we have already settled.

The reviews disagree on almost nothing that matters. All four say the same three things: no standard estimator exists
for "transient advantage in pattern count"; a fixed-threshold component count is a legitimate **conditional** observable
and not a robust one; and the weakest link is identity tracking. Everything below is written so that a future run can
apply it without re-reading forty pages of prose.

---

## 1. Four estimands, and the trap in each

The word "count" hides four different numbers. They are not interchangeable, and our own results differ under each.

| estimand | definition | what it answers | the trap |
|---|---|---|---|
| `C(t)` | components above threshold at physical time `t` | what the field looks like now | single snapshots have CV 0.78–0.93 in our runs; never quote one |
| window mean | mean of `C(t)` over a declared physical-time window | typical occupancy of the window | changes with window; early window carries the effect |
| time integral | `∫C dt`, or the sum over samples | accumulated component-time | not a rate; a longer run always scores higher |
| cumulative distinct structures | number of distinct `uid`s seen so far | structural turnover | depends entirely on the identity rule (§4) |

**Rule.** A published number names its estimand, its window and its sampling. "The contrast is +3.57" is incomplete;
"+3.57 over 7 snapshots at 1000 time units, every seed averaged first, medians of the per-seed means" is complete.

The reviews add a fourth warning that we had not formulated: **the field has no convention for any of these**, so we are
not failing to follow a standard — we are stating one. That is a methodological contribution only if we state it as such
and apply it consistently.

---

## 2. The `dt` gap: one explanation is now dead

The reviews proposed two explanations and disagreed about which dominates:

- **sampling / cadence** — the `dt = 0.5` run was saved twice as often per unit of physical time (25 snapshots at every
  250 time units, against 7 at every 1000), so more short-lived structures could be counted;
- **modified equation** — explicit Euler integrates a *different* system: for a mode with continuous growth rate `σ`,
  the discrete multiplier is `1 + dt·σ`, i.e. an effective rate `ln(1 + dt·σ)/dt`. The selected mode can shift, and with
  it the pattern.

This was testable on data already on disk, and it has been tested:
[`scripts/cadence_match.py`](../scripts/cadence_match.py) → `l1_field_cadence.json`.

| control | `dt = 1.0` | `dt = 0.5` |
|---|---|---|
| identical physical times, identical sample count (5 samples, `t ≥ 2000`) | **+4.20**, CI `[+1.4; +8.4]`, 9/10 seeds positive | **+0.40**, CI `[−2.4; +6.7]`, 5/10 seeds positive |
| same window, 6 samples (`t ≥ 1000`) | +4.17 | +1.00 |
| same window, 3 samples (`t ∈ 2000..4000`) | +4.67 | +0.17 |

**Verdict.** Cadence is not the explanation: at matched times, with the same estimator and the same number of samples,
the gap is as large as before. In the matched window the `dt = 0.5` contrast is not distinguishable from zero.

**And a self-correction that came with it.** The *magnitude* at `dt = 1.0` is placement-sensitive: +3.69 with 13
samples, +2.79 with 7, +1.00 with 4. The contrast decays with time, so a coarse quadrature weights the late
low-contrast part more heavily. The robust statement is therefore **the gap, not the number +3.57**. That sentence
belongs wherever +3.57 is quoted.

What survives is the modified-equation candidate — and it is still only a candidate. The discriminating test is a
different integrator (RK4 at the same physical time) or `dt = 0.25`: if the contrast converges towards the `dt = 0.5`
value, the effect is numerical; if it stays near the `dt = 1.0` value, it is a property of the discrete dynamics at
this step. Nothing cheaper settles it.

---

## 3. Threshold: from one number to a curve

The reviews converge on the same formulation, and it is better than ours: `β₀` of the **excursion set** at a declared
threshold is well defined, and its dependence on the threshold is not a defect but the object of study. Our percolation
result is exactly that dependence: at `v ≥ 0.20` one cluster holds 0.95 / 0.99 of the area; at `0.30` both worlds shatter
into ~30 pieces.

Two things we should copy from the literature rather than invent:

1. **Normalise the threshold by the field's own amplitude.** Spector et al. (2025) build their filtration in 20 steps
   between `min` and `max` of the solved field, not at absolute values. This makes patterns of different amplitude
   comparable, and it is the reason their classification survives near the boundary of the Turing space, where patterns
   have almost no contrast. Our absolute `0.20` / `0.30` cannot do that.
2. **Choose the noise cutoff from the data.** They plot the distribution of barcode lengths and cut at the minimum
   between the two dominant modes — not at an arbitrary minimum area. `B_1^u` had no such minimum, and they say so and
   keep those bars.

`β₀` alone cannot separate spots from stripes; `β₁` can (a stripe network has holes, a spot pattern has few). Our
morphology classes are currently assigned by eye to `β₀` counts. A `β₀`–`β₁` pair at two thresholds is cheap and would
make the class labels machine-checkable.

### The size floor, which we had never declared

The threshold fixes *which field values* count; the minimum area fixes *which pieces* count. We had never varied the
second, and it turns out to carry most of the result. Recomputed from the stored per-snapshot component areas
(`scripts/size_resolved_contrast.py`, `l1_field_size_resolved.json`):

| minimum area, cells | `dt = 1.0` | `dt = 0.5` |
|---|---|---|
| 1–8 | **+3.57** | +1.24 |
| 16 | +2.57 | +0.58 |
| 32 | +1.36 | +0.36 |
| 64 | +0.86 | +0.20 |
| 128 | **+0.07** | −0.30 |

The advantage lives in components of roughly 16–64 cells; above ~100 cells the two worlds are indistinguishable, and at
`dt = 0.5` the sign even turns over. The honest formulation is therefore "heterogeneous inflow multiplies **small**
components", not "doubles the number of patterns". A count without a size floor is as incomplete as a count without a
threshold — the same lesson as §3, one level down.

---

## 4. Identity of structures: the weakest link, and what is free

The lifetime contrast (median 57 steps heterogeneous, 4046 homogeneous) rests on one rule: a `uid` is inherited when the
overlap between consecutive snapshots is ≥ 0.5. Three reviews name this as the place where the claim is most likely to
break, and they are right — the rule has no precedent in the Gray–Scott literature. Overlap matching is standard in
**cell and particle tracking** (Jaqaman et al. 2008; Chalfoun et al. 2016), where it is always accompanied by explicit
split, merge and gap events. Ours is the one-stage greedy special case with none of that.

What can be checked without a new run, because the per-snapshot `areas` and per-`uid` peak sizes are stored:

| check | status | what it showed |
|---|---|---|
| minimum component area 1 / 2 / 4 / 8 … cells | **done** | the count contrast collapses between 64 and 128 cells (§3); the lifetime gap widens instead |
| largest-cluster share, per snapshot | **done** | hetero 0.817 against homog 0.925 — a scatter, not a pattern |
| lifetimes in physical time (`steps × dt`) | **not applicable** | `uid`s were tracked only at `dt = 1.0`, so the conversion changes nothing; cross-`dt` lifetimes need a new run |
| overlap threshold 0.3 / 0.5 / 0.7 | needs masks | whether identity is rule-dependent |
| event-aware lineage (split/merge/gap) | needs masks | whether the rule is even the right kind of object |
| persistence-based lifetime | needs fields, not masks | threshold-free birth/death |

**Pre-declared rule.** If the sign of the heterogeneous-minus-homogeneous lifetime difference flips under any remaining
check, no lifetime claim is made; the result is reported as "identity-rule dependent" and the number is withdrawn. The
size filter did not flip it — heterogeneous median 54 → 13 steps as the peak-area floor rises, homogeneous 3575 → 3575 —
so the rule still stands.

---

## 5. Scaling: what does not exist, and the surrogate that does

No paper in the reachable literature gives a law for the number of threshold components per unit area in Gray–Scott.
What exists is theory about *wavelength* — spot size and spacing are set by reaction and diffusion parameters, not by
domain size — and stability analysis of individual spots (Muratov & Osipov 2001; Chen & Ward 2011). So a count law is
ours to fail at, and the honest intermediate is a dimensionless density:

    N_norm = N · λ² / A,   λ = 2π / q_peak from the radial structure factor of v

If the heterogeneous/homogeneous contrast survives this normalisation, it is not a wavelength effect. If it vanishes, the
finding is that heterogeneous inflow changes *spacing*, not *number* — a different and still publishable statement. The
fields themselves are not stored (per-seed files keep component areas and counts, not the field), so this needs one
re-run that saves `v` at the snapshots it already takes. That is the cheapest way to convert the present caveat into a
result, and it should be the first run of the next series.

**Also from the reviews, and it matters for our grid:** Pearson (1993) checked `dt` 1.0 → 0.01 and grids 256 → 1024 in
the founding paper. We work at 96 and had never varied `dt` before 31 October. Whatever we conclude, the asymmetry is
stated in the methods.

**And boundary conditions are a third choice we never defended.** Woolley (2022) shows that the Turing bifurcation is a
pitchfork under zero-flux boundaries and **transcritical** under Dirichlet — generically, for two-species systems in 1D —
and that linear analysis cannot tell the two apart. Our grid is periodic, which is neither case: it is the third choice,
and it belongs in the methods next to `dt` and the grid rather than in a footnote.

---

## 6. Vocabulary: our gates are verification, not validation

The reviews agree that ABM/ALife has adapted V&V vocabulary and we should borrow it instead of inventing terms:

| our gate | standard name | what it can claim |
|---|---|---|
| anchor bit-for-bit, determinism | **code verification** | the code does what we think |
| `X56` `dt` sweep, grid comparison | **solution verification** | numerical error is bounded, or not |
| design gate §3d (connectivity, positive control, readout) | **conceptual-model / input validation** | the manipulation reaches the dynamics |
| contrast, percolation, lifetimes | **output verification** + sensitivity | the number is computed and is fragile where stated |
| §10 sections against other regimes | **corroboration** | consistency with independent evidence |
| a second implementation | **docking** (Axtell et al. 1996) | the result is not a property of our code |

`docs/design-checks.md` stays, but it is a project-specific fragment of this scheme, not a new standard. Nothing here
requires a claim stronger than "verification"; **validation** — correspondence with a target system — we cannot claim
for a Gray–Scott world at all, and should not try.

---

## 7. Quote-ready wording

Pre-declared, so that the next text does not improvise:

> We report two estimators of pattern abundance: the instantaneous count `C(t)` of connected components above a declared
> threshold, and its mean over a declared physical-time window. No field-wide convention exists for transient pattern
> abundance in Gray–Scott systems, so we state both, together with the window, the threshold and the sampling.

> The contrast between heterogeneous and homogeneous inflow is step-dependent. At `dt = 1.0` it reaches `+4.2` on
> matched physical times; at `dt = 0.5` it is `+0.4` and indistinguishable from zero. Sampling density does not account
> for the difference: on identical times and identical sample counts the gap remains. We therefore treat the `dt = 1.0`
> result as a property of this discrete system until convergence with a higher-order integrator is established.

> Lifetimes depend on the identity rule, the threshold and the snapshot cadence. We report them in physical time and
> give sensitivity to the rule; the `uid`-inheritance rule is an operational convention, not a unique definition of
> structure identity.

---

## 8. Order of work, cheapest first

| order | action | cost | what it buys |
|---|---|---|---|
| 1 | lifetimes in physical time + minimum-area sweep from stored `areas` | minutes | the two free identity checks of §4 |
| 2 | `β₀`–`β₁` at amplitude-relative thresholds on stored fields | needs one re-run with fields saved | §3, and machine-checkable morphology classes |
| 3 | structure factor, `N·λ²/A` | same re-run | §5, the one result that would survive the caveats |
| 4 | overlap 0.3 / 0.7 with masks | one re-run, masks saved | closes §4 or withdraws the lifetime claim |
| 5 | RK4 or `dt = 0.25` | one run per arm | separates modified equation from discrete dynamics |
| 6 | map `docs/design-checks.md` onto §6 vocabulary | writing only | positions the methods section |

Item 1 needs no run and no decision from anyone. Items 2–3 share one run and should not be split.

---

*References with checked DOIs: [`lit-model-run-2026-11-01.md`](lit-model-run-2026-11-01.md). Full texts in
[`corpus/texts/`](corpus/texts/), status in [`corpus/manifest.json`](corpus/manifest.json). The four reviews themselves
are quoted nowhere: their value was the agreement, and the agreement is compressed into the rules above.*
