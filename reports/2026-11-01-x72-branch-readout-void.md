# X72 void: the branch readout failed before the measurement could be made

**Date:** 2026-11-01, 20:05 MSK. **Experiment:** X72 (analysis of the X70 replication worlds, no new runs).
**Preregistration:** `reports/2026-11-01-x72-branch-heredity-plan.md` (committed before the script existed).
**Aggregate:** `morphogenesis/experiments/E09_pond/l1_field_x72_branch.json`.

## What was asked

X71 showed the medium is multistable at `F = 0.035`: two wavelengths, 12.0 and 8.73 cells, both present in every world of
that cell. If heredity at that point is discrete, a daughter should sit on her parent's **branch** more often than a
non-parent structure at the same distance does. The X70 replication worlds (`x70r_*`) were run at exactly that inflow, so
the question looked answerable from data already in git.

## What happened

The branch had to be read from the component log, and the log carries centroids but no local spectrum. The proxy was the
distance to the nearest neighbouring structure, with a fixed threshold of 10.4 cells between the two branches. The
pre-registered control for this proxy was simple: both classes must be populated, and the two branches are 12.0 and 8.73
cells apart, so the spacing had to move with the global peak position.

It does not. Across whole runs the median nearest-neighbour spacing sits at **11.0–11.5 cells** whether the global
wavelength is 12.0 cells or the field has become a labyrinth (peak at 8 bins, no single spot scale); the correlation between
median spacing and peak position is **−0.18**, and the spacing spread across a run is about **0.7 cells**, far below the
3.3-cell difference it would have to resolve. The proxy measures how densely structures are packed, not how large they are.

The numbers that the invalid proxy produced are recorded anyway, because they look like a result and would have been read as
one: parent–daughter branch concordance **0.517** (chance), surrogate concordance **0.904**, difference −0.387, shuffle p95
0.502, in all five worlds. Read naively, that says "no branch heredity, and the neighbourhood agrees with the daughter but
the parent does not". The correct reading is weaker and more useful: the surrogate is measured **at the same instant and in
the same patch** as the daughter, so its 0.90 is spatial autocorrelation of the proxy, while the parent is measured one
snapshot earlier — the two controls are not comparable, and neither number is about heredity.

## Verdict

**Void, not negative.** The instrument failed the control that the preregistration put in front of it (both classes
populated is necessary but not sufficient; the missing test was whether the proxy tracks the wavelength at all). No claim
about branch heredity is made in either direction.

## What the next attempt needs

1. **Local spectrum on the field, not spacing on the log.** The fields exist (`_x70r_fields`, every 200 steps); a 48-cell
   window around a structure gives peak positions with a bin of `48/λ ≈ 4–5.5`, which separates 12.0 from 8.73 cells by
   about 1.5 bins — marginal, so the window should be 64 cells where the box allows it. Better: a two-mode fit per patch,
   which uses the whole spectrum instead of its argmax.
2. **Fields every 50 steps, not every 200.** A branch read at birth needs a field close to the birth step; with 200-step
   spacing the parent's branch and the daughter's come from different transients.
3. **Prospective, not retrospective.** The plan already said a re-analysis of X70 cannot be as strong as the original
   experiment. Now there is a second reason: the component log was designed for identity, not for morphology, and this
   question needs the field.

## Lesson for the line

A re-analysis inherits the instrument of the original run. The preregistration's first control — "the branch variable must
exist in this data" — was written as "both classes populated", which the spacing proxy passed by accident (it splits
dense from sparse places). The control that would have caught it is the one added afterwards: **the proxy must move with
the quantity it stands for.** That belongs in `docs/design-checks.md` as a rule for every proxy readout, and it is the
reason this report exists: the void is cheap, the misreading would have been expensive.
