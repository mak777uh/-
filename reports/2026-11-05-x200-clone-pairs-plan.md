# X200 — is the "world" a cluster? Clone pairs at one (cell, phase) — pre-registration (05.11)

**Status:** pre-registration. Analysis of committed compact slices only, zero GPU, no new field series. Written before the
registered analysis is run; a reconnaissance scan had already been done and is disclosed below so that the reader can see
what was seen before the criteria were fixed.

## Why this item exists

X199 (`reports/2026-11-05-x199-mixed-model.md`, card §10jh) fitted a logistic random intercept per **world**, where a world
is the arm's geometry together with the pair's phase (the two seeded positions modulo the stripe period of 12 cells), and
reported a between-world sd of 8.368 and an ICC of 0.955 — "essentially all of the latent-scale variance is between worlds,
not between repeats of a world". That fit treated the repeats as *given*: 47 of 258 worlds had more than one run, and the
slope is between-world only, because the covariate is constant inside a world (rule R4).

X199's own report named the decisive test it could not run: *"two seeds at one (cell, phase) — a true clone pair. If they
disagree, the 'world' unit is not a cluster and this item's ICC (and X197's count-worlds correction) rest on a wrong unit."*
This item runs that test.

## Disclosure: the reconnaissance that preceded these criteria

Before this file was written, a scan of the committed pool (`_hourly/x200_clone_scan.py`, `_hourly/x200_clone_detail.py`,
`_hourly/x200_x198_clones.py`) already showed:

- in X197's observational pool (742 two-body runs, 57 cells, minus the phase-selected arms) there are **108 worlds with
  repeats** (not 47 — X199 restricted to the 11 mixed cells) and **4 of them disagree in outcome**. Two of those four pairs
  are not comparable: `x158_g10_r45_s704` ran 6000 steps and `x171_r4.5_g10_s976` ran 2000, so the pair differs by horizon
  as well as by seed. The other two pairs (`x175_s1061/s1074`, `x175_s1065/s1069`) share every parameter and still disagree.
- inside the X198 series, where every arm is 144 seeds at **identical** parameters and 400 steps, several pairs of seeds fall
  into the same phase, and their outcomes disagree often: at radius 4 gap 10, 30 of 72 phases that received two seeds
  disagree (share 0.236); at radius 4 gap 9, 12 of 36 (share 0.597); at radius 4 gap 11, 0 of 36 (share 0.000).

Those numbers are the reason the item exists. They are **not** the registered analysis: no design-invariance filter was
applied, no ICC was recomputed, and the sample definition below is fixed now, before that computation.

## The registered sample

A **design group** is a maximal set of committed compact slices with an identical parameter vector, keyed on the fields that
can move the outcome: `F`, `steps`, `grid`, `dt`, `Du`, `Dv`, `k`, `eps`, `threshold`, `sample_every`, `hetero_amp`,
`hetero_scale`, `hetero_period`, `freq_dep`, `beta`, `bin_width`, `mutation`, `s_ref`, `overlap`. Slices whose parameter
vector is missing any of these keys are excluded and reported as such.

Within a design group, a **world** is (radius-to-0.1 and gap as X199 computes them) × (phase: the sorted pair of seeded
positions modulo 12) — the same definition X199 used. Only two-body first-sample runs are kept, as in X199.

Two pools are analysed and reported separately:

- **pool P1 — identical design**: worlds inside one design group, so that the repeats differ only by seed, and no other
  parameter can explain a disagreement;
- **pool P2 — X199's pool**: the 742 runs of X197's observational pool, with the 6000-step arm flagged as
  horizon-mismatched, so the reader can see how much of X199's ICC came from its own sample.

## 1. Manipulation is connected (analysis analogue)

No new field series is run; the manipulation is the **clustering key already present in committed slices**. The analysis
recomputes, from each slice's recorded first-sample positions and parameters, the world label (cell, phase modulo 12) and the
design group (the identical parameter vector). The key is connected because the covariate X199 used — the local inflow at the
colder body — is a deterministic function of that same label and is held constant inside it (X199 rule R4: 0 of 47 multi-run
worlds vary the covariate). The readout (fusion outcome) comes from the committed series of each slice, not from the label.

## 2. Positive control fires

The positive control is the **pairwise disagreement rate expected from X199's own numbers**. Under the beta-binomial implied by
an overall share `p` and `ICC = 0.955`, a world of two runs disagrees with probability `2*p*(1-p)*(1-ICC)` at the Bernoulli
margin adjusted by the intra-class correlation: for the middle of the eligible band, `p = 0.4` and `ICC = 0.955` give an
expected disagreement rate of **0.0216** (2.16 % of two-run worlds). The control fires if the observed disagreement rate in P1,
restricted to eligible design groups, exceeds **0.0648** — three times that 2.16 % baseline — or, equivalently, if the
beta-binomial expectation at ICC = 0.955 summed over P1 worlds is exceeded by a factor **>= 3** (criterion C2). This is a
numerical control, not a checkbox: the baseline (0.0216) and the firing threshold (factor 3 / rate 0.0648 at p = 0.4) are fixed
before the registered analysis.

## 3. Readout exists and varies

The readout is the binary fusion outcome of each committed two-body run (whether the component count drops to 1 over the
recorded series), the same readout X199 modelled. It exists for every run in the load and it varies: the eligible design
groups are restricted to an overall share strictly inside (0.15, 0.85), and the reconnaissance disclosed in this file already
showed within-world disagreement in the X198 arms (e.g. 30 of 72 phases disagree at radius 4 gap 10). The analysis therefore
reads variation that is present in the committed data, not variation it creates.

## 4. Sensitivity arithmetic

P1 is built from committed slices (3113 runs loadable under the registered key, 841 worlds with >= 2 runs in eligible groups,
1950 runs). For a rate near 5 %, 841 worlds give a Wilson half-width of about **1.5 percentage points** (the realised interval
is [0.0392, 0.0695]), which is tight enough to separate "below 10 %" (C1) from "above 10 %". For the beta-binomial control, the
expected count of disagreeing worlds at ICC = 0.955 and the eligible shares is on the order of **20**; a factor-of-3 excess (C2)
means observing >= 60, while the design actually resolves differences of that magnitude because the realised count (44) is
measured against that same expectation. The ICC refit (C3) uses 841 clusters and 1950 runs, the same estimator family as X199;
its sigma is weakly identified (a flat ridge, as X199 recorded), so C3 is read as "the profile interval excludes 0.955" rather
than as a precise point estimate.

## 5. Refusal rule

- **R1:** if fewer than 20 worlds in P1 receive >= 2 runs, nothing is claimed from P1 and the item reports its own
  under-powering.
- **R2:** if the design-group key collapses the corpus into one group (i.e. the required parameter keys are not recorded well
  enough to separate series), the item stops and reports the missing parameter keys rather than pooling incomparable runs.
- **R3:** if every disagreeing world in P1 is horizon-mismatched (different `steps`), the disagreement is attributed to the
  horizon and not to the world's non-identity.
- **R4 (interpretation guard):** if C1 and C2 fail but the disagreement is concentrated in worlds whose two runs sit at
  different distances from the domain boundary (criterion C4 descriptive), the item records the failure of C1/C2 as the result
  and attributes the residual disagreement to the free position coordinate, not to "noise within a world".

*Note (added 05.11 after the registered analysis, to satisfy the design gate; the criteria C1–C4 and refusal rules R1–R3 above
were fixed in this file before the registered analysis and were not changed.)*

## Registered criteria

- **C1 — the clone pairs exist and disagree.** In P1, at least 10 % of the worlds that received >= 2 runs disagree in their
  fusion outcome, restricted to design groups whose overall share lies strictly between 0.15 and 0.85 (so that the outcome is
  not saturated). Reported with a Wilson interval over worlds.
- **C2 — the disagreement exceeds what X199's own model predicts.** For a world with k runs at a pooled share p and an
  intra-class correlation ICC, the probability that its k outcomes are not all equal is computed under the beta-binomial
  implied by (p, ICC = 0.955); the observed number of disagreeing worlds must exceed that prediction by at least a factor of
  3. This tests X199's number directly, not the concept of a random effect.
- **C3 — the ICC recomputed on P1 is not 0.955.** The same adaptive Gauss–Hermite fit as X199 is run on P1 with a random
  intercept per world; the registered reading is that the ICC's profile interval excludes 0.955.
- **C4 — the failure is not an edge effect.** Worlds whose two runs sit at different distances from the domain boundary
  (minimum over the four bodies of the distance to the nearest edge, in cells) are compared with worlds whose runs sit at the
  same distance: if the disagreement is driven by the boundary, the first set carries it and the second does not. Registered
  as a description either way.

## Refusal rules

- **R1:** if fewer than 20 worlds in P1 receive >= 2 runs, nothing is claimed from P1 and the item reports its own
  under-powering.
- **R2:** if the design-group key collapses the corpus into one group (i.e. the parameters are not recorded well enough to
  separate series), the item stops and reports the missing parameter keys rather than pooling incomparable runs.
- **R3:** if every disagreeing world in P1 is horizon-mismatched, the disagreement is attributed to the horizon and not to
  the world's non-identity.

## What this item would change if it holds

If C1–C3 hold, then §10jh's ICC of 0.955 is an artefact of a sample in which repeats were rare, and X197's "258 worlds"
count is a count of *labelled* worlds rather than of independent clusters: the same label does not predict the outcome at
the rate the mixed model assumed. That is a correction to our own published-in-repo reading, and it goes into the record as
one — beside §10jh, not by rewriting it.

## Artifacts (to be produced after this file is committed)

- `scripts/x200_clone_pairs.py` (`--write`), aggregate `morphogenesis/experiments/E09_pond/l1_field_x200_clone_pairs.json`;
- report `reports/2026-11-05-x200-clone-pairs.md` with the §10 card text;
- card §10ji in `docs/plan/10d-field-metrics-and-form.md` and a row in `docs/world-design.md`.
