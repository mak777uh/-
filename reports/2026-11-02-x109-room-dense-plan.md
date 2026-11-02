# X109 — do the room results survive dense logging?

**Why.** X106 and X107 were measured on the sparse series (`x100`), where heredity was understated by a quarter in the maze cell
(X105: 0.384 → 0.480). X107's headline — *heredity is not a shared-room effect, the drop is 0.064 of 0.519* — is the line's answer to
the most obvious referee question, and it has only ever been measured on the sample that X105 showed to be compressed. If the room
correction grows with the sample, the answer changes.

**The question.** On the dense series (`x108`: the same twenty worlds as X105 with a field at every logged step), do the two room
readouts reproduce — the crowding coefficient of X106, and the drop in the parent–daughter coefficient when the room is partialled out
(X107)?

## 1. Manipulation is connected

Twelve runs of `x108` are not involved: this is analysis of the twenty runs X108 already produced (`x108_*`, seeds 301–310, two
inflows, `--sample-every 10`), using the same definitions as X106/X107 — the nearest non-ancestor peak at the structure's own peak
step, ancestors excluded by walking `uid_pairs` upward. Connectedness: at least **600 pairs** per cell with a non-ancestor peak
(X106's rules gave 1 834 and 800 on the sparse series; the dense series has more loggable pairs, not fewer).

## 2. Positive control fires (numeric)

Two controls, both required:

1. **Heredity on the kept pairs** must reproduce X108's excursion-set coefficient within **0.02** (0.548 at 0.030, 0.480 at 0.040) —
   the same pairs and the same definition must give the same number, and the control **fires if** that band holds in both cells.
2. **The room coordinate must still be a room:** `ρ(d_near, mother's area)` must be **≥ +0.20 in the lattice** and **≤ +0.15 in the
   maze** (X106: +0.397 and −0.038). A sign flip would make the coordinate incomparable.

## 3. Readout exists and varies

Per cell: `ρ(d_near, daughter area)`, `ρ(d_near, mother area)`, `ρ(d_near, lifetime)`, the parent–daughter coefficient before and after
partialling the mother's room, and the drop. Variation exists by construction: the sparse series spanned 0.322–0.397 for the two
crowding coefficients and the drop was 0.064.

## 4. Sensitivity arithmetic

1 951–2 211 pairs per cell, so the standard error of a coefficient is 0.021–0.023 and of a partial with one control slightly more. The
declared resolution is **0.10**, as in X107. A drop of 0.10 or more is a difference; anything smaller is called no difference, and the
dense-series drop is compared with the sparse one (0.064) rather than with zero.

## 5. Refusal rule (fixed before the run)

**Void** if a cell has fewer than 600 pairs, the heredity control misses its ±0.02 band, or the room control flips sign.

**The room result survives** if in both cells the drop is `≤ 0.10` and `ρ(d_near, daughter area)` keeps the sign it had on the sparse
series.
**The room result changes** if the drop in the lattice cell is `≥ 0.15` — then X107's 0.064 was a sparse-sample number and the claim
must be restated with the dense value.
**Mixed** otherwise, printed cell by cell.

## Design summary

| factor | value |
|---|---|
| artifacts | `x108_*` twenty runs (X105's worlds, a field at every logged step) |
| readouts | crowding coefficients and the room-partialled heredity, per cell |
| controls | heredity within ±0.02 of X108; room coefficient ≥ +0.20 lattice, ≤ +0.15 maze |
| artifact | `E09_pond/l1_field_x109_room_dense.json` |

## Checklist

- [x] connected (600 pairs, non-ancestor peak present, lifetime measurable)
- [x] positive controls numeric (heredity ±0.02 of X108; room sign and floor)
- [x] readout exists and varies (sparse spread 0.322–0.397, drop 0.064)
- [x] sensitivity computed (§4: SE 0.021–0.023, resolution 0.10)
- [x] refusal rule written, with "the room result changes" as a real outcome
- [x] no new runs: stated

## Status

Registered 2026-11-02 20:15 MSK, before the analysis. No GPU.

доска: принято 0, отклонено 0, отложено 0.
