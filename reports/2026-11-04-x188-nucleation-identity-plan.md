# X188 — nucleation as an identity test, on the X187 runs (pre-registration, 04.11)

**Status:** pre-registered, not yet run.

## 1. Manipulation is connected

X187 manipulated the local inflow at the colder body (cold `F_local` ≈ 0.017, warm 0.030) in two arms and produced a designed
reproduction of the sign flip X186 had seen per cell: radius 3 gap 10 moves +0.67 (0 of 6 → 4 of 6), radius 6 gap 9 moves −0.33
(6 of 6 → 4 of 6). Its registered mechanism readout — "components other than the two seeded ones near the pair at the sample of
minimum count" — turned out to be the outcome restated (1 exactly when fused, 0 exactly when not, 24 of 24 runs), so nucleation
is **untested**, and the hypothesis on the table is unchanged: in this medium a **warm** site may nucleate bodies of its own, so
a large pair in a warm site never reaches one component.

The runs to answer it already exist: the component log of every X187 run carries a **uid** per component at every 10-step sample,
so a body that appears besides the pair can be identified by its identity rather than by its distance from a start position.

## 2. Positive control fires

The control fires if (a) the two seeded uids are present and distinct in the first sample of every run (24 of 24), (b) the count
of uids ever seen across a run exceeds the number of components at any single sample in at least 18 of 24 runs — otherwise the
log is not resolving births and the test is vacuous, (c) the two levels differ in `F_local` by at least 0.008 (registered in
X187 and achieved), and (d) at least three runs per group reach a sample with a single component, which is what makes "was there
anything besides the pair at that moment" meaningful. Thresholds: 24/24, 18/24, 0.008, three runs.

## 3. Readout exists and varies

Primary: at **fixed samples** (every 50 steps from step 50 to 2 000) and in a **fixed window** (the 24×24-cell box centred on the
pair's initial midpoint), the number of components whose uid is neither of the two seeded uids nor a uid that the seeded pair's
own component ever carried — i.e. bodies that are not the pair and not its continuation. Secondary: the same count over the whole
field, and the first sample at which such a body appears. The reference frame is the initial midpoint, and every count is
reported at that frame so no quantity depends on where the merged body has drifted to.

**Independence from the outcome is checked and reported**: the primary count must not be a function of whether the pair fused.
`scripts/x188_nucleation_identity.py` computes the cross-tabulation of counts against `fused` and writes it into the aggregate; if
every fused run and no unfused run had a count above zero (or the reverse), the readout is declared invalid and this item is
recorded as "no readout" rather than as a result.

## 4. Sensitivity arithmetic, and the prediction

24 runs (2 arms × 2 levels × 6), 301 samples each, 49 fixed samples per run at the primary grid; the window is 24 cells across so
a body within a body-radius or two of the pair is inside it. Registered **before the run**, from X186/X187:

- in the **radius 6** arm the warm level (the one that coalesces less) shows a **higher** mean count of non-pair bodies at the
  fixed samples than the cold level, and the difference is at least 0.5 bodies (its registered bar, chosen because the counts are
  small integers and six runs per level are few);
- in the **radius 3** arm the difference is **smaller in the same direction** (warm level shows more non-pair bodies) but does not
  reach 0.5, because there the warm level coalesces more;
- bodies appear **after** contact in the warm radius-6 group: the median first-appearance sample is later than the median sample
  of first contact, which is what "nucleated by the merge" would look like rather than "budded from the start".

## 5. Refusal rule

If the radius-6 warm level does not show at least 0.5 more non-pair bodies at fixed samples than its cold level, the item is
recorded as **the flip is not nucleation by identity either**, and the mechanism question is moved to the field level (a dense
dump of the inflow between the bodies) rather than to more component counting. If the two levels differ but the direction is the
same in both arms, the item is recorded as **nucleation is general, not size-specific** and X186's flip needs another cause. If
the primary count is a function of the outcome, the item is recorded as **no readout** and no claim about nucleation is made.

## 6. What would kill it

The uid bookkeeping is the whole test, so it is checked first: with `--split-new-uid`, a component that buds may inherit its
parent's uid, in which case a nucleated body that descends from the pair is invisible to this count and a positive result is a
floor rather than a measurement of all nucleation. The window is centred on the **initial** midpoint and the pair moves, so a
nucleated body that the pair carries along can leave the window; the count is therefore reported both inside and field-wide, and
a disagreement between the two is reported rather than resolved. And 24 runs with integer counts of 0–3 support a difference of
half a body at best: the bars are set at that scale and no claim is made below it.

## 7. Implementation notes

`scripts/x188_nucleation_identity.py` reads the same 24 committed compacts, recomputes each run's colder-body inflow from the
first sample, builds the set of uids the pair ever carries, counts non-pair bodies at the fixed samples inside the window and
field-wide, cross-tabulates against the outcome, and reports the two arms' levels side by side. Aggregate
`morphogenesis/experiments/E09_pond/l1_field_x188_nucleation_identity.json`. Cost under a minute of CPU; no new runs.

## 8. Pre-run amendment (04.11, before any analysis) — identity does not survive the events this item counts

Reading one committed run (`x187_r6_g9_cold_s40006`) shows why the uid test above cannot work as written: the two seeded bodies
carry uids 1 and 2, the merge leaves only uid 2 on the field, and the next sample already shows uids **3 and 4** — the medium
re-issues identities at division (`--split-new-uid`), so a body's uid is not a lineage. Tracing "the pair and its continuation" by
uid is therefore impossible, and the first claim of this item would have been vacuous: at the sample of minimum count the field
holds exactly one component, so "bodies besides the pair" has no content there by construction.

The test is replaced, before running it, by **spatial continuation tracking**, which asks the same question without identity:
at every fixed sample, match components to the previous sample's tracked pair by nearest centre within **4 cells** (a body moves
well under a cell per 10 steps here), treat the match as the pair's continuation, and count the components that are neither the
continuation nor inside 3 cells of it as **other bodies** — inside the 24-cell window around the pair's *current* centre, and
field-wide. The registered predictions, bars and refusal rule of sections 4-6 are unchanged in substance (warm radius-6 shows at
least 0.5 more other bodies in the window than cold radius-6; the same direction smaller at radius 3; the invalid-readout escape
still applies if the count turns out to be a function of the outcome), with "non-pair bodies by uid" read as "other bodies by
continuation" throughout. The independence cross-tabulation of section 3 is kept and now decides whether the new readout is
valid, exactly as it did for X187.

