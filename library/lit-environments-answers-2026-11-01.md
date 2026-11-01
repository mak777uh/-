# What four answers to the environments-and-rules questions changed

1 November 2026, 15:45. Four independent answers to
[`../reports/2026-11-01-questions-environments-and-rules.md`](../reports/2026-11-01-questions-environments-and-rules.md).
This page keeps only what changes a design decision, plus the references that were checked. Prose that agreed with what we
already thought is not repeated.

---

## 1. The objection that matters most, and it lands on our newest number

**A parent–daughter correlation in area is expected even with zero transmission**, because the daughter sits where the
parent was and shares the local inflow. All four answers said this in different words; one called it the common-environment
confound of quantitative genetics.

**Consequence:** X70's 0.334 (measured the same afternoon) exceeds a *pairing* null (p95 = 0.054) but has **not** been
tested against a *spatial* null. The control is a non-parent structure at the same separation and the same time. Until it
runs, the claim is "parent-specific signal exists, spatial control pending" — and this is now the first item of the plan,
not the last.

**Update, 17:20 the same day — the objection was tested and the claim survived it, at a different number.** The control
ran three ways (nearest-distance surrogate inside distance bins, occupancy tertiles, and the local field itself as both
stratum and covariate). Observed 0.582 against a surrogate of −0.003, partial 0.545, and heredity is weak in the driest
third of the field and strong in the richest — the environment modulates it but does not predict the area, so the common-
environment confound is measured and rejected. Running the control also exposed a defect in the run itself: in a `beta = 0`
world the seeds do not move the geometry, so the original five seeds were one world copied five times and 0.334 was one
draw of the starting blob. Over five genuinely different worlds the coefficient is 0.499 (0.42–0.57), and the pairing
null is 0.11–0.13, not 0.054.

## 2. Hysteresis: two different things wear the same name

Three answers converged: a hysteresis **threshold in the detector** (appear above θ_hi, vanish below θ_lo) changes our
counts and lifetimes but not the physics — the structure is still gone as far as the PDE is concerned. Real dormancy needs
a **slow state variable**, e.g. `dw/dt = a·v − δ·w` with reseeding where `v` is low.

**Consequence:** the cheap version is still worth doing (it converts "vanish" into "wait" for our counts, one line), but it
is a **measurement change, not an inheritance channel**, and must be labelled that way in any report.

## 3. Q7 — nobody found a falsifier either

All four answers failed to find a two-species reaction–diffusion system with no imposed genotype that transmits a
lineage-level property across generations with measured fidelity. The most plausible falsifier any of them proposed is
**multistability of morphology**: parameter regions where several stable spot sizes coexist, so a daughter inherits the
parent's attractor. That is "limited heredity" in Szathmáry's sense — the category our X70 result belongs to (originally
"a third of the deviation survives"; after the repair, about half, with slopes 0.38–0.57).

One answer cited a **recent Gray–Scott Markov-blanket paper** reporting that a flux-defined claim failed under the tested
estimators. If it exists, it is the closest published relative of our negative result and must be read before we state
ours.

## 4. References checked

| claim | reference | DOI |
|---|---|---|
| compositional genomes, the primary modelling paper | Segré, Ben-Eli & Lancet (2000), PNAS 97(8):4112 | **`10.1073/pnas.97.8.4112`** — verified |
| memory physically encoded in a living flow network | Kramar & Alim (2021), PNAS | **`10.1073/pnas.2007815118`** — verified |
| trail evaporation controls collective choice | Nicolis & Deneubourg (1999) | not yet checked |
| multistability as limited heredity | Szathmáry & Maynard Smith (1997); Szathmáry (2006) | not yet checked |
| the Gray–Scott Markov-blanket failure | arXiv `2610.27235` | **not verified** — fetch before citing |

Two answers disagreed about whether the "fidelity versus division interval" claim is established: one presented it as a
measured result, another as unverified. It stays a lead.

## 5. What the answers would have us do, in order

1. **Spatial null for X70** — cheap, and it may remove the only positive heredity signal we have.
2. **Detector hysteresis**, labelled as a measurement change; then, if it earns its keep, a slow dormancy field.
3. **Habitat field with a reciprocal-transplant test** rather than a free choice of coupling strength: remove the parent,
   keep the field, seed a daughter into old versus fresh habitat, and require the effect to exceed inflow noise.
4. **Multistability scan** of (F, k) before building any third species — if several stable morphologies coexist, limited
   heredity is a property of the medium and the scan is its evidence.
5. Only then a third species for compositional heredity, where the measured quantity is fidelity as a function of the
   division interval.

One answer's warning belongs at the top of that list rather than in a footnote: **before adding fields, check whether the
existing medium already produces the appearance of inheritance.** That is exactly what X70's missing control is for.
