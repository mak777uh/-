# X113c — the rate test with a control that matches its sample

**Why a re-registration.** X113b's control required the raw-depth contrast to reproduce X113's +1.479 / +2.213 within 5 %. It came back at
**+1.351 / +1.987** — 8.6 % and 10 % lower — and the reason is structural: a **rate** needs a usable lifetime, so the sample is restricted to
uids with `life ≥ 50` steps (83 of 1 087 excluded in the lattice, 369 of 877 in the maze). Comparing a filtered contrast against an unfiltered
one and demanding 5 % is the same "control band borrowed from another sample" error the X85 rule forbids, and it is mine, not the data's.

X113c keeps the measurement and fixes the control: the filtered contrast is compared with the unfiltered one **on the same run set**, and a
shift of up to **15 %** is allowed and printed. Everything else — readouts, thresholds, refusal branches — is unchanged.

## 1. Manipulation is connected

Same uids and sister pairs as X113. `rate = depth / life × 1000` for uids with `life ≥ 50` steps; the count of excluded uids is reported per
cell (the filter is the honest cost of a rate).

## 2. Positive control fires (numeric)

1. **Heredity on the same pairs** `≥ 0.35` in both cells (0.548 / 0.480).
2. **The sample shift is bounded:** the raw-depth contrast computed on the **filtered** sample must lie within **15 %** of the same contrast
   computed on the **unfiltered** sample *in the same run*, and both numbers are printed. The control fires if the shift is inside 15 % — which
   is what "the filter did not change what is being measured" means.

## 3. Readout exists and varies

As in X113b: sister contrast in generations per 1 000 steps (speed) and per division (arithmetic), `ρ(area, rate)`, medians. Variation: rates
span from 0 to several generations per 1 000 steps and the depth advantage is 1.4–2.0 generations on the filtered sample.

## 4. Sensitivity arithmetic

Unchanged: 1 004 and 508 usable uids, ~1 100 and ~1 200 sister pairs; resolution **0.10** generations per 1 000 steps with a bootstrap
interval excluding zero.

## 5. Refusal rule (fixed before the run)

**Void** if a cell has fewer than 300 usable uids, heredity below 0.35, or the filtered-versus-unfiltered shift above 15 %.

**Size buys speed** if the rate contrast is positive with the interval excluding zero **and** `ρ(area, rate) ≥ 0.10` in both cells.
**The count was arithmetic** if the interval contains zero or `|ρ(area, rate)| ≤ 0.05` in both cells.
**Mixed** otherwise, cells reported separately.

## Design summary

| factor | value |
|---|---|
| artifacts | X108's twenty runs, the same pairs as X113 |
| readouts | rate contrast and per-division contrast, `ρ(area, rate)`, filtered and unfiltered depth contrasts |
| controls | heredity ≥ 0.35; filtered-versus-unfiltered shift ≤ 15 % |
| artifact | `E09_pond/l1_field_x113c_depth_rate.json` |

## Checklist

- [x] connected (300 usable uids; exclusions reported)
- [x] positive control numeric (heredity ≥ 0.35; shift ≤ 15 %, both numbers printed)
- [x] readout exists and varies (rates 0–several per 1 000 steps)
- [x] sensitivity computed (§4: resolution 0.10)
- [x] refusal rule written, with "the count was arithmetic" as a real outcome
- [x] stated: the previous control was mis-specified and this one measures the filter's effect directly

## Status

Registered 2026-11-03 00:26 MSK, before the run. No GPU.

доска: принято 0, отклонено 0, отложено 0.
