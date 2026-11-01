# X70: size heredity is partial — a third of the deviation survives, two thirds regress

1 November 2026, 15:35. Ten runs. Preregistration:
[`2026-11-01-x70-size-heredity-plan.md`](2026-11-01-x70-size-heredity-plan.md), committed before the run.

The question was whether the medium carries heredity of its own, with no imposed copy rule. Two observer facts made it
answerable, both added today: daughters now get **their own identities** at a split (`--split-new-uid`, anchored
bit-for-bit with the flag off), and each division event records parent and daughter uids, whose **peak areas** are in
`uid_outcomes`.

## Result

| arm | division events | correlation | slope | shuffle null (p95) |
|---|---|---|---|---|
| heterogeneous | **925** | **0.334** | **0.335** | 0.054 |
| homogeneous | 100 | 0.294 | 0.262 | 0.159 |

**Two things are true at once, and they point in opposite directions.**

1. **The signal is parent-specific.** Shuffling parents among daughters inside the same run destroys the correlation
   (median ≈ 0.00, p95 = 0.054), so the 0.334 is not "all structures in this world have similar sizes". A daughter really
   does resemble *its own* parent more than a random one.
2. **But the inheritance is weak and mostly regressive.** A slope of 0.335 means a daughter inherits about **a third** of
   its parent's deviation from the mean size, and two thirds of that deviation is erased. The medium pulls structures back
   to its own preferred scale.

So the pre-declared bands say "sizes regress to the medium's scale" (corr < 0.5, slope < 0.5), while the same data also
say the medium does carry something. Both statements belong in the answer: **partial heredity, one generation, with strong
regression to the medium's scale.**

## The control that is missing, and why it matters

The shuffle null removes the *pairing* but not the *spatial adjacency*: parent and daughter sit next to each other and
share the local inflow field, so part of the 0.334 could be shared environment rather than transmission. All four model
answers to this morning's questions raised exactly this objection, and the right control is a **distance-matched
non-parent**: compare each daughter with an unrelated structure at the same separation and the same time, and report only
the excess over that baseline.

Until that runs, the claim is: **a parent-specific size signal exists and exceeds a pairing null; whether it survives a
spatial-adjacency control is untested.** That sentence is weaker than "the medium carries heredity" and stronger than
"there is none", and it is the honest one.

## What this does to the morning's question

This morning the question was whether a proper environment could give non-mechanical heredity. The answer so far: the
two-species medium gives **limited** heredity — one generation, one-third fidelity, no lineage beyond that without an
additional channel. That is the same "limited heredity" category the models pointed to (multistability of morphology),
and it is a real result rather than a null.

## Artifacts

`morphogenesis/experiments/L1_field/x70_{pattern,homog}_s{171..175}.json` (10 files, with `uid_pairs`, `size_pairs`,
`uid_outcomes`), aggregate `morphogenesis/experiments/E09_pond/l1_field_x70_size.json`. Scripts: `scripts/x70_series.py`,
`scripts/x70_analyse.py` (the shuffle null is `shuffle_null()` in the latter).

## Addendum, 15:55 — the spatial control ran, and it points against the signal while being too thin to settle it

The four answers to the morning's questions said the same thing: a parent–daughter correlation in area is expected even
with zero transmission, because the daughter sits where the parent was. The control is a **non-parent structure at the same
distance at the same time**; only the excess over that baseline is heredity-like.

It has now been run (`scripts/x70_spatial_null.py`, aggregate `l1_field_x70_spatial.json`): for each division event, the
parent–child distance is measured from the centroids, and a surrogate is drawn from structures present at the child's
birth whose distance to the child is within ±4 cells.

| arm | events matched | observed corr | surrogate corr (median, p95) | exceeds surrogate |
|---|---|---|---|---|
| heterogeneous | **50** of 925 | 0.104 | **0.640** (0.769) | **no** |
| homogeneous | 35 of 100 | 0.889 | degenerate (single surrogate) | not interpretable |

**Two things, and neither is a verdict.**

1. **The direction is against transmission.** On the events that could be distance-matched, a neighbouring non-parent
   correlates with the daughter *more* strongly (0.64) than the parent does (0.10). That is the common-environment
   confound behaving exactly as predicted.
2. **The control is far too thin to carry that conclusion.** Only **50 of 925** events survived the ±4-cell matching, and
   they are not a random subset: an event is matched only if a same-distance neighbour existed at the child's birth, which
   biases towards crowded, fragmenting regions — precisely where the geometry is least representative.

So the honest status of X70 is now **unresolved**, in a specific way: the pairing null says there is a parent-specific
signal, and the first spatial control says it may be the place, on 5 % of the data. Neither number deserves to be quoted as
the result.

**What the control needs before it can decide anything:** matching inside distance bins across the whole sample rather than
discarding unmatched events (a stratified comparison keeps all 925), and a second covariate — local occupancy in a small
window — because distance and crowding are confounded in this world. That is a half-hour of analysis on data already on
disk, and it is the first item for the next session.

The claim as it stands: **the two-species medium shows a parent-specific size correlation that exceeds a pairing null and
does not clearly survive the first, underpowered spatial control.** That is a weaker sentence than the one written before
this addendum, and it is the one that matches the evidence.
