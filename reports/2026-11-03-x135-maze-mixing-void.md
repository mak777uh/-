# X135 void — in the percolating cell the forcing replaces a seeded structure by step 1 290, so the seeded instrument cannot measure a mixing length there

**Plan:** [`2026-11-03-x135-maze-mixing-plan.md`](2026-11-03-x135-maze-mixing-plan.md) (08:55).
**Series:** stopped at 14 of 35 runs when the control failed; the five `SEP = 0` control runs are complete.

## What the control said

The plan's control 4 was: *a lone seeded disc must survive, otherwise the two-disc arms cannot be read as merging rather than dying.* It did not survive.

| control run (`SEP = 0`, one disc) | components at step 100 / 500 / 1000 / 3000 / 6000 | subtree of the seeded uid | last step with a member of it |
|---|---|---|---|
| seeds 601–605, all five identical | 1 / 2 / 7 / 6 / 6 | 33 uids | **1 290** |

The world is alive — six components and 47 % occupancy at step 6 000 — but **nothing of the seeded structure is left in it**: the lineage's last member disappears at step 1 290, and what persists afterwards is the pattern the forcing regenerates. At `F = 0.040` the spatial forcing (`--hetero-amp 0.5`) dominates the initial condition, which is the same lesson X96b taught about scale ("the inflow sets the pattern continuously and the environment ignores the initial condition") — here it applies to **identity**, not only to wavelength.

**Void by control 4.** The two-disc arms cannot distinguish "the lineages merged" from "the seed was overwritten", so no mixing length is measured in this cell.

## The second defect, found in the same control

The five control runs agree **to the digit** in every quantity above (33 uids, last step 1 290, identical component counts at every checkpoint), even though their trajectory hashes differ. The same holds for X134's arms: at every separation, all five seeds give the same merge step and the same subtree sizes. So the `--init-spots` branch, as first written, **placed the discs at fixed centres** and discarded the seed-dependent mask, leaving the seed with nothing to change that this readout can see.

That does not overturn X134's threshold — a deterministic fact about a forced world is still a fact, and the wall between 12 and 18 cells is one — but it does overturn the **replication language**: "10 of 10 seeds" was one world measured ten times. The probe is fixed (the pair is now placed at a seed-derived offset, separation preserved), anchored again key-by-key with the flag absent, and X134b re-runs the bracketing separations with the fix.

## What this leaves

- **X134's threshold stands** as a deterministic statement and is being replicated properly in X134b.
- **The maze has no seeded mixing length by this instrument.** Measuring it needs one of: seeding at a much lower forcing amplitude so the seeds dominate, a label that survives the forcing (a trait field), or an observational estimate from the body's own structure, which is what X128b–X130 already provide.
- The block's statement about the percolating cell does **not** rest on this run; it rests on the observational identity block, which is unaffected.

## Caveats

- Only the control arm is complete; the two-disc arms were stopped, so this report makes no claim about merging at any separation in the maze.
- The control is five copies of one world (the second defect), so "5/5 died" is really "1/1 died, measured five times".
- One inflow, one radius, one forcing amplitude.

доска: принято 0, отклонено 0, отложено 0.
