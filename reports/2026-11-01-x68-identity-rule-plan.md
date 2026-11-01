# X68 — the lifetime claim under a different identity rule

1 November 2026, 13:47. Preregistration before the run. This is the fix specified for the weakest link in the published
line, and it is the cheapest experiment left.

Every lifetime number this project has published — median 57 steps in the heterogeneous world against 4046 in the
homogeneous one — rests on one rule: a component inherits its `uid` when the overlap with the previous snapshot is **at
least 0.5 of the daughter's cells**. The tracking literature we read in the morning says overlap matching is a convention,
not a standard, and that the cutoff and the split/merge handling decide what an "identity" is. So the number should be
shown to survive its own rule.

`field_track.py` has carried `--overlap` since the beginning and it has never been varied. This run varies it.

## Design

Same world, same seeds, same everything as the X60 heterogeneous arm and its homogeneous control (`amp 0.5` or `0.0`,
`beta = 0.2`, `freq_dep = 1`, mutation 0.15, grid 96, `dt = 1.0`, 6000 steps). Two new identity rules:

- **loose**: `--overlap 0.3` (a daughter inherits if 30 % of its cells were the parent's),
- **strict**: `--overlap 0.7`.

The 0.5 arm already exists on disk (`x60_pattern_s*`, `x60_homog_s*`), so the comparison is three rules × two worlds × five
seeds, of which ten runs are new.

## Prediction, written before the data

A stricter rule breaks more lineages, so median lifetime should **fall** from 0.3 to 0.5 to 0.7 in **both** worlds. That
part is almost mechanical and is not the point.

The claim that matters is the **contrast**: the heterogeneous median is roughly two orders of magnitude below the
homogeneous one (57 against 4046). The prediction is that this ordering survives all three rules even as both numbers move
— i.e. **ratio > 2 at every rule**, with the ratio computed per seed and summarised over the five.

If the ordering flips at 0.3 or 0.7, the published lifetime contrast is a property of the rule and must be withdrawn.

## 1. Manipulation is connected

Only the identity rule changes; the field is identical by construction because `--overlap` is read by the observer, not by
the dynamics. That is the point and also the check: `components` and `areas` must be **identical** across the three rules
for the same seed. If they are not, the flag leaks into the simulation and the run is invalid.

## 2. Positive control fires

The known 0.5 arm must reproduce the published magnitudes: medians in the tens for the heterogeneous world and in the
thousands for the homogeneous one. If the new runs at 0.5 cannot be compared with the old ones (different schema), the
control is the old files themselves and the new arms are compared to them.

## 3. Readout exists and varies

`lifetimes.median_life_steps`, `n_uids`, `life_steps`, `peak_sizes`, plus `selection.splits` and `inheritability_r`. The
readout varies across worlds by two orders of magnitude, and should vary across rules by a factor.

## 4. Sensitivity arithmetic

Five seeds per cell of the design, paired by seed across rules. The claim is an **ordering** (hetero < homog) at each rule,
tested per seed: at least 4 of 5 seeds must show hetero median lifetime below homog for the claim to stand at that rule.
No p-values.

## 5. Refusal rule

Worthless, not negative, if:

1. `components` or `areas` differ between rules on the same seed (the flag leaked into the dynamics);
2. the strict rule leaves fewer than 3 uids in an arm (no distribution to take a median of);
3. the loose rule merges everything into one uid in most seeds (same problem from the other side).

## Design summary

| element | value |
|---|---|
| world | L1 field, grid 96, `dt = 1.0`, 6000 steps, `beta = 0.2`, `freq_dep = 1`, mutation 0.15, amp 0.5 (het) or 0.0 (homog) |
| rules | overlap 0.3, 0.5 (existing), 0.7 |
| seeds | 171–175 |
| criterion | per-seed ordering hetero < homog at each rule, ≥ 4/5 |
| cost | 20 new runs ≈ 30 min |
| artifacts | `morphogenesis/experiments/L1_field/x68_ov{03,07}_{pattern,homog}_s*.json` |

## Status

- [x] connected (observer-only flag; `components`/`areas` must be identical across rules — checked after the run)
- [x] positive control fires (the 0.5 arm is the published one)
- [x] readout exists and varies (57 against 4046 steps)
- [x] sensitivity computed (per-seed ordering, 4/5 rule)
- [x] refusal rule written (three conditions)

---

## Amendment, 14:05 — the check failed, and it found something better

The first run of the series was rejected by its own leak check: `components` at `--overlap 0.3` **differ** from the same
seed at 0.5. The flag is not observer-only in this world, and the reason is structural:

> composition is carried **per component**, inherited along the identity, and it modulates the local growth rate
> (`F_eff`). Change which daughter inherits which parent's composition and you change the field.

So the identity rule is part of the dynamics here, not a lens on it. That is a property of the world worth stating on its
own, and it makes the original design impossible: with feedback on, a difference in lifetimes between rules confounds the
rule with the trajectory.

**The redesign uses the regime where composition cannot feed back**: `--beta 0` and `--eps 0`, i.e. no survival and no
growth channel. There the field is identical across rules by construction — the leak check will verify it — and any
difference in median lifetime is the rule's doing alone. That is exactly the sensitivity question, asked in the only
regime where it is separable.

The published lifetimes (57 against 4046 steps) come from the feedback regime; this amendment does **not** re-measure them.
It measures the **rule's** effect on the identity statistics in a neutral world, which is the quantity needed to say
whether those lifetimes can be compared with anyone else's.

### Revised design

| element | value |
|---|---|
| world | L1 field, grid 96, `dt = 1.0`, 6000 steps, **`beta = 0`, `eps = 0`** (no feedback), mutation 0.15 |
| arms | heterogeneous (amp 0.5) and homogeneous (amp 0.0) |
| rules | overlap **0.3, 0.5, 0.7** — all three re-run, so the 0.5 arm is comparable |
| seeds | 171–175 |
| check | `components` identical across rules for the same seed and arm (the leak check that just failed) |
| criterion | per-seed ordering hetero < homog at each rule, ≥ 4/5; and the three rules' medians reported side by side |
| cost | 30 runs ≈ 40 min |
| artifacts | `morphogenesis/experiments/L1_field/x68_ov{03,05,07}_{pattern,homog}_s*.json` |

### What this amendment does not change

- The claim under test is still the ordering, not the magnitude.
- The 0.5 arm at `beta = 0.2` remains the published one; the new 0.5 arm at `beta = 0` is a different world and is labelled
  as such.

### Status after the amendment

- [x] connected — and the check that was meant to prove it instead disproved the original premise, which is why it was
  there
- [x] positive control fires (the neutral world must still produce uids; the leak check must pass)
- [x] readout exists and varies (57 against 4046 in the feedback world)
- [x] sensitivity computed (per-seed ordering, three rules)
- [x] refusal rule written (uids ⟨3⟩ or one uid in most seeds)
