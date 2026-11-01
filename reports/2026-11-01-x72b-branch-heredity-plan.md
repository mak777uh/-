# X72b — branch heredity at the multistability boundary, with a readout that is supposed to work

**Why a rerun.** X72 tried to answer this from the X70 replication worlds and returned a **void**: the stand-in (distance to
the nearest neighbour) never tracked the wavelength, so its concordance numbers mean nothing
(`reports/2026-11-01-x72-branch-readout-void.md`). The contract rule added the same evening says a proxy must move with what
it stands for. This series measures the branch **directly** instead: the radial spectrum of the field inside a window around
the structure, from fields written every 50 steps so the parent's and the daughter's branches come from the same transient.

**Question.** At `F = 0.035`, `k = 0.06` — the cell where X71 found two wavelengths, 12.0 and 8.73 cells — does a daughter's
local wavelength agree with her own parent's more often than with a non-parent structure at the same distance?

## 1. Manipulation is connected

There is no manipulation on the world in this series; the "manipulation" is the readout itself, so the connectedness check is
that the two branches exist in these data: the distribution of local wavelengths must split into two clusters of at least
25 % of the structures each (X71 measured 12.0 and 8.73 cells at this inflow). If it does not split, the branch variable
does not exist and the series is void — it cannot claim heredity of something that is not there.

## 2. Positive control fires

Two controls, both before the concordance is read.

1. **The local measure tracks the global one.** For every snapshot, the global peak position (radial spectrum of the whole
   field) is regressed against the median local wavelength of that snapshot; the correlation must be **≥ 0.5** and the
   spread of local wavelengths must exceed the 3.3-cell gap between the branches. This is the control X72 lacked: if the local
   measure does not move with the global wavelength, no concordance number computed from it is admissible.
2. **Both classes are populated**, as above (≥ 25 % each).

## 3. Readout exists and varies

Per structure and per snapshot, a 48×48 window centred on its centroid (periodic wrap), its radial power spectrum, and the
peak position `q_win`; the local wavelength is `48/q_win` cells. Per division event (`uid_pairs`, birth from
`uid_outcomes.first`), the parent's branch comes from the last snapshot **before** the birth and the daughter's from the first
snapshot **at or after** it — with fields every 50 steps, the gap is at most 50 steps, so both are read within one transient.

Statistic: **concordance** — the fraction of classified events in which parent and daughter share a branch. The branch split
is the same as X72's, `>= 10.4` cells, fixed in advance and not tuned.

## 4. Sensitivity arithmetic

Five worlds at ~175 division events each; the measured X70 rate gives ~150 classifiable events per world. With a 60/40
split between branches, chance concordance is `0.6² + 0.4² = 0.52`; a difference of **0.15** between the parent's and the
surrogate's concordance is detectable per world at a 95 % binomial band of about ±0.08. That 0.15 is the criterion, the same
one X72 registered, so the two attempts are comparable.

The surrogate is the non-parent structure **present at the daughter's snapshot** whose centroid is nearest to the daughter's.
It is spatially adjacent by construction, so it measures local coherence rather than heredity; it is used only as the null,
and its own value is reported, never interpreted as a result.

## 5. Refusal rule

**Void** if fewer than three of five worlds have ≥ 100 classifiable events, or if the local measure fails control 1
(correlation < 0.5 or local spread ≤ 3.3 cells), or if one branch holds > 75 % of events. **Supports branch heredity** if
parent concordance exceeds the surrogate's by **≥ 0.15** in the pooled pattern arm and in **≥ 4 of 5 worlds**, and exceeds
the p95 of a within-world permutation of parent branches (2000 draws). **Not supported** if the pooled difference is ≤ 0 or
fewer than two worlds reach +0.15. Anything else is **inconclusive** with the numbers reported.

## Checklist before the series

- [x] connected (hashes differ)
- [x] positive control fires
- [x] readout exists and varies
- [x] sensitivity computed
- [x] refusal rule written

The two controls in §1–§2 are the ones X72 passed by accident and this series cannot: the local spectrum is the quantity
itself, not a stand-in, and its tracking of the global peak is measured, not assumed.

## Design summary

| factor | value |
|---|---|
| inflow | `F = 0.035`, `k = 0.06` (the X71 boundary cell) |
| arms | heterogeneous only (`amp 0.5`, static unit signal); homogeneous cannot hold two branches here |
| worlds | 5, `--init-jitter`, seeds 171–175 |
| grid, step, horizon | 96, `dt = 1.0`, 6000 |
| logging | components every 50 steps, **fields every 50 steps** (`_x72_fields/`, not committed) |
| readout | 48-cell window spectrum → local wavelength; branch at 10.4 cells |
| statistics | concordance, nearest-distance surrogate, within-world permutation null |
| artifact | `morphogenesis/experiments/L1_field/x72b_pattern_s171-175.json`, aggregate `l1_field_x72b_branch.json` |

## Status

Registered 2026-11-01 20:15 MSK, before the series. Five runs, ~15 minutes.
