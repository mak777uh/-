# X81 — prescribe the spectrum instead of mixing patterns: does heredity fall with the *share* of a second peak, or with its wavelength?

**Why.** X79 and X80 both failed for the same reason: mixing two patterns moves the dominant scale and the modulation amplitude
together, and even with the amplitude normalised the two-peak check cannot tell "a little of the second scale" from "equal parts"
(X80: 5/5 worlds two-peaked at `w = 0.25` and at `w = 0.50`, 0/5 at `w = 0.75`). The measurement question — is shallow memory about
*mixedness* or about *which wavelength wins* — has not been asked with a manipulation that separates them.

This series prescribes the **spectrum** directly. The runner gains `--spectrum-share`: the dominant peak stays at
`--hetero-scale` (q = g/scale = 8, 12.0 cells), the second sits at `--hetero-scale2` (q = 11, 8.7 cells), and the flag is the
prescribed **power ratio** of the second peak to the first. Both waves are products of unit sines and cosines with phases drawn per
world from a private generator, the composite is amplitude-normalised exactly as in X80, and at `share = 0` the phases are zero, so
the pattern is the old single-scale one.

**Anchors, already run (02.11, before this plan was committed).**
- `share = 0` against the flags-off path at 400 steps, seed 171, `F = 0.030`: `series`, `uid_pairs`, `uid_outcomes` and `summary`
  **identical**, i.e. bit-for-bit.
- the new branch at `share = 0.5` twice with the same seed: `check_determinism.py` — **deterministic**.

## 1. Manipulation is connected

Cells differ only in `--spectrum-share` (and one cell in `--hetero-scale2`). Connectedness is checked by the field itself: for every
world the saved field at 6000 is spectrally analysed and the **measured** share is
`P(q2) / (P(q1) + P(q2))` with `q1 ∈ [7.5, 8.5]`, `q2 ∈ [10.5, 11.5]` (and `q2 ∈ [13.5, 14.5]` for the fourth cell). The cell's
median measured share must land within **0.15** of the prescribed share, else the cell is void. This is the check X78/X79/X80 did
not have: it does not ask "are there two peaks" but "did the second peak arrive in the strength I asked for".

## 2. Positive control fires (numeric)

The `share = 0` cell is a re-run of the single-scale reference, so it must reproduce it. **The control fires if** the pooled `rho1`
lands in **[0.45, 0.56]** and the pooled half-life in **[1.30, 1.70]** divisions (X74's single-scale 0.030 cell: 0.507 and 1.47;
X78b's reference arm: 0.498 and 1.47; X78's mismatched arm reached 1.88 at a different inflow and is outside this band). **If the
control does not fire, the series is void** — not "inconclusive" — because then the reference cell is not the reference.

## 3. Readout exists and varies

Same depth readout as X73–X80: `uid_pairs` at 50-step logging, Spearman of ancestor on descendant peak area at lags 1–3,
cross-lineage shuffle p95, `lambda` fitted **per world** and aggregated by **median** (the X80 finding), with the pooled value printed
beside it. `rho1` is the **primary level**, the half-life is a secondary derived quantity: it is a ratio, and at five worlds the pooled
and per-world versions disagreed in sign, so it may not carry a claim alone.

## 4. Sensitivity arithmetic

- `rho1` across worlds at this inflow: sd ≈ 0.06 (X80: 0.266–0.590 within cells) to 0.10 (X76 at 0.033: 0.224–0.561).
- 10 worlds per cell → SE of a cell mean ≈ 0.019–0.032. A difference of **0.10** is 3σ at the pessimistic sd;
  a difference of 0.05 is not resolvable at 10 worlds and will not be claimed.
- Power: 800–1 500 lag-1 pairs per cell (X80 cells gave 665–981 at five worlds), far above the 400-pair floor.
- Cost: 4 cells × 10 worlds = 40 runs at ~95 s ≈ **65 minutes** of one GPU lane.

## 5. Refusal rule (registered before the run)

**Void** if any cell has <10 components, <400 lag-1 pairs, a median measured share more than 0.15 from its prescribed value, or if the
`share = 0` control fails §2.

**Graded in share (mixedness)** if `rho1` is monotone decreasing across measured share (`0 < 0.5 < 1.0`), the drop from share 0 to
share 1.0 is **>= 0.05**, and at least **8 of 10** worlds at share 1.0 sit below the share-0 cell's median `rho1`.

**Any second peak, not its share** if share 1.0 and share 0.5 are both at least 0.05 below share 0 and within 0.03 of each other.

**Wavelength matters** if the two share-1.0 cells (q2 = 11 and q2 = 14) differ by **>= 0.05** in `rho1` while both sit below share 0.

Anything else is **inconclusive**, printed in full. The half-life may be quoted only alongside the per-world median and range, and only
if at least 7 of 10 worlds are fittable in that cell.

## Design summary

| factor | value |
|---|---|
| inflow | `F = 0.030`, `k = 0.06` (single-scale memory 1.47, band-free) |
| pattern | prescribed spectrum, amplitude-normalised; `--hetero-scale 12.0` (q = 8) |
| cells | `share 0`; `share 0.5` (q2 = 11); `share 1.0` (q2 = 11); `share 1.0` (q2 = 14, `--hetero-scale2 6.857`) |
| phase | drawn per world from `default_rng(seed*1000003 + 17)`; zero when share = 0 |
| worlds | 10 per cell, `--init-jitter`, seeds 181–190 |
| grid, step, horizon | 96, `dt = 1.0`, 6000 |
| logging | components every **50** steps; field at 6000 |
| artifact | `morphogenesis/experiments/L1_field/x81_s{0,05,10}_q{11,14}_s181-190.json`, aggregate `l1_field_x81_spectrum.json` |

## Checklist before the series

- [x] connected (hashes differ; the flag changes the pattern)
- [x] anchor: `share = 0` bit-for-bit against the flags-off path; new branch deterministic
- [x] positive control fires (numeric band, §2)
- [x] readout exists and varies (same readout as X73–X80)
- [x] sensitivity computed (§4)
- [x] refusal rule written, with the failure of X80's tie encoded as a numeric deviation bound

## Status

Registered 2026-11-02 04:00 MSK, before the series. Forty runs, ~65 minutes.

доска: принято 0, отклонено 0, отложено 0.
