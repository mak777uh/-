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
