# X77: the patch never had any power — neighbour sizes do not predict a daughter's size at all

**Date:** 2026-11-02, 03:20 MSK. **Experiment:** X77 (patch control for the size memory; re-analysis, no new runs).
**Preregistration:** `reports/2026-11-02-x77-patch-plan.md`.
**Artifacts:** `morphogenesis/experiments/E09_pond/l1_field_x77_patch.json`.

## Result — void as a discriminator, and the reason is the result

| dataset | events | median patch size | ρ(parent, daughter) | ρ(**patch mean**, daughter) | ρ(nearest non-parent, daughter) |
|---|---|---|---|---|---|
| X72c (primary) | 1 566 | 2 | **0.409** | **0.010** | 0.038 |
| X70r (replication) | 779 | 2 | **0.438** | **0.007** | 0.067 |

The registered rule required the control to have power — `ρ(patch_mean, daughter) ≥ 0.20` — before the parent's coefficient could
be read. It does not: the local mean area of non-ancestor structures is **statistically unrelated** to the daughter's size
(0.010 and 0.007, i.e. the null value to two decimals), and the median patch in a 12-cell radius holds only **two** structures.
By the rule the test is **void as a discriminator**, and both the pooled coefficient (0.422 [0.326, 0.531] in X72c, 0.441
[0.288, 0.602] in X70r) and its survival are uninterpretable: a regressor that carries no information about the outcome cannot
absorb anything.

## What the void nevertheless establishes

This is the rare case where a failed control is itself the finding. Two readings of X70 were possible after its nearest-neighbour
control: (a) the parent is just a member of a local patch whose overall size determines the daughter, and the nearest neighbour
was a poor proxy for that patch; (b) the parent is special. **Reading (a) is now excluded by measurement**, not by argument: the
patch — every non-ancestor within one wavelength — has a correlation with the daughter of 0.01. Neighbour sizes are unrelated to
a structure's size in this world; the parent's 0.41 is not "the patch, better measured".

With X70's local-field test (the field's own `v` at the daughter's birth predicts her area at −0.022, and the parent's at 0.111)
the two available families of confounds are now both measured and both rejected: **neighbour sizes and local field richness do not
predict a structure's size; her parent does.**

## What remains unmeasured

- The patch radius was fixed at 12 cells. A much larger patch (say 24 cells) would contain more structures and might acquire
  power; the present test says nothing about scales beyond about one wavelength.
- "Patch" here is a mean of *structures*, not of the field. The field-level control exists in X70 and is separate.
- The void rule is strict: a patch that predicts nothing cannot be used as a confound, but it also cannot be used as evidence
  *for* the parent. The positive statement stays where it was — X70's own numbers.

## What follows

- For the write-up, this closes the "common environment" objection in its two measurable forms. The remaining objection is
  conceptual (the daughter inherits the parent's *position*, and position correlates with everything), and against that the only
  defence is the one already in place: the surrogate is drawn at the same position and does not work.
- A larger-radius patch is a cheap follow-up if a reviewer asks; it is a ten-line change to `RADIUS` in the script and one run.
