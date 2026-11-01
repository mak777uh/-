# X29 closed by the instrument's own null: the selection differential is +0.148 where the trait can do nothing

**Date:** 2026-11-01, 20:30 MSK. **Item:** `X29_eas_flow_lenia` (queue), closed as *answered by failure of the instrument*.
**Artifacts:** `morphogenesis/experiments/L1_field/x37_{sel,null}_s171-180.json` (20 runs, now in git),
aggregate `morphogenesis/experiments/E09_pond/l1_field_x37_eas.json`.
**Meter:** `scripts/field_eas.py` (the Flow-Lenia EAS meter, written for X37/X39).

## Why this report exists

The audit of the open queue found `X29` marked `planned` with the note "the meter is written and the data are on disk, it
was never run". Both halves were partly wrong: the meter **had** been run on 31.10 and left a report in the scratch
directory, but nothing reached git, and the numbers it produced are a failure — which is why they were never written up.
Both are fixed here: the 20 run artifacts are copied into the repository, the meter is re-run on them (identical numbers),
and the result is recorded instead of forgotten.

## What the meter measures

For each run, the **selection differential** `S = mean(s at birth | survived to the end) − mean(s at birth | died
earlier)`. Unlike a shift of the mean trait, `S` is meant to be insensitive to the overall trend: if the trait is paid for,
the survivors entered the world with a different trait value than the dead.

The design has the right control by construction: an arm where the trait **cannot** affect anything (`beta = 0`, the shadow
run) and an arm where it can (`beta = 1.2`). If the meter works, `S ≈ 0` in the shadow arm.

## The numbers

| arm | runs | S median | positive | bootstrap 95 % |
|---|---|---|---|---|
| null (`beta = 0`) | 10 | **+0.148** | **10/10** | [+0.1405, +0.1545] |
| selection (`beta = 1.2`) | 10 | −0.060 | 0/4 | [−0.1516, −0.031] |

The shadow arm is not zero, it is **+0.148 with ten of ten runs positive and a tight interval that excludes zero**. So `S`
is measuring something that survives even when the trait is inert — most plausibly the coupling between the trait value and
the structure's size or birth timing, both of which determine how long it lives independently of any trait effect.

The selection arm's negative value is therefore uninterpretable: a meter that reports +0.148 under the null cannot support
−0.060 as evidence of selection in the opposite direction.

A second defect, independent of the first: each run has **two** uids in `uid_outcomes` (six alive, one dead in the
aggregate), i.e. `S` is computed from about seven events per run. Even a valid differential would have a standard error
larger than the effect.

## Verdict

**The meter is invalid as implemented, and X29 is closed by that failure, not by a series.** No claim about selection on the
trait is made from these data in either direction. The EAS part (type = bin of `s`, activity accumulated through area, Flow-
Lenia form) produces `types_present` and `max_share` but inherits the same small samples and is not reported as a result.

## What a valid version needs

1. **A null that is zero by construction.** Compute `S` inside strata matched on birth step and on the structure's area at
   birth, or randomise `s` at birth within a run and keep everything else. The external shadow run is not enough, because it
   shares the confound it is supposed to remove.
2. **Enough events.** Ten or more uids per run, and runs long enough that death is not the same as "did not exist yet".
3. **A separate statement for the two statistics.** `S` is a differential; EAS accumulation is a novelty measure. They can
   fail independently, and bundling them in one meter is what let a broken `S` sit unnoticed next to a plausible `EAS`.

## Provenance note

The runs carry `params` but no `git_commit` (the runner of 31.10 did not record one), so their provenance is the file dates
(31.10, 05:04–05:06) and the parameters written into each artifact: `beta` 1.2 vs 0, `eps` 0, 3000 steps, grid 96,
`dt` 1.0, threshold 0.2, `sample_every` 250, `mutation` 0. The artifacts are now committed so the numbers can be recomputed,
but they cannot be tied to a code commit and that is stated rather than papered over.
