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

## Registered criteria

- **C1 — the clone pairs exist and disagree.** In P1, at least 10 % of the worlds that received ≥2 runs disagree in their
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

- **R1:** if fewer than 20 worlds in P1 receive ≥2 runs, nothing is claimed from P1 and the item reports its own
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
