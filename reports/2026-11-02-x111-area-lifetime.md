# X111 / X111b — the area–lifetime relation is at the null's edge, and the logging density does not move it

**Plans:** [`2026-11-02-x111-area-lifetime-plan.md`](2026-11-02-x111-area-lifetime-plan.md) (20:35, **voided**),
[`2026-11-02-x111b-area-lifetime-plan.md`](2026-11-02-x111b-area-lifetime-plan.md) (20:37, the corrected comparison).
**Aggregate:** `l1_field_x111b_area_lifetime.json`. Log-only analysis of four series; no GPU.

## X111 voided on its own control, and the reason was a transcription error in the plan

X111 required the recomputation to reproduce X92's `+0.191` at 0.030 and `−0.041` at 0.040. It gave `+0.077` and `+0.021`. The cause is
in **this line's own record**: X92's corrected table (CLAIMS 312) reads **+0.191 / +0.067 / −0.041 / −0.046** for the cells
**0.025 / 0.030 / 0.035 / 0.040**, and the plan took the 0.025 and 0.035 values for the 0.030 and 0.040 cells. Recomputing on X92's own
series with the same code gives **+0.069** and **−0.042**, i.e. X92's values to within 0.004: the code was right and the reference was
mis-assigned.

X111b fixes the reference and, more importantly, fixes what the control is measured **on**: X92's own worlds (`x85`+`x87` for 0.030,
`x88` for 0.040), not the `x100` series. Comparing `x100` against X92 would have been exactly the borrowed-control-band error the X85
rule forbids.

## The comparison

| cell | X92 (its own worlds) | recomputed on X92's worlds | `x100` sparse (50-step) | `x108` dense (10-step) | null p95 (x100 / x108) |
|---|---|---|---|---|---|
| 0.030 | +0.067 | **+0.069** | +0.077 | +0.049 | 0.042 / 0.041 |
| 0.040 | −0.046 | **−0.042** | +0.021 | −0.039 | 0.047 / 0.041 |

Registered verdict: **the sign is set by the sample, not the density.** The two series disagree in sign at 0.040 (+0.021 against
−0.039) with deltas of −0.028 and −0.060, both inside the declared resolution of 0.10 — and **every coefficient in the `x100`/`x108`
comparison sits inside its own shuffle null** (0.041–0.047).

What the table says, in order of how much it can be trusted:

1. **The re-measurement of X92 reproduces X92** (+0.069 vs +0.067, −0.042 vs −0.046). That is a code-and-record check, and it passes.
2. **On X92's own worlds the coefficient is above its null** (0.069 and 0.042 against nulls of 0.029–0.032) — barely, but above.
3. **On the X100/X108 samples it is not**: 0.077, 0.049, 0.021, −0.039 against nulls of 0.041–0.047. Two of the four are below their
   null, one is at it, one just above.
4. **The logging density moves nothing** that can be attributed to it: the deltas are smaller than the nulls, and the dense series was
   never a twin of the sparse one (`--sample-every` is physical, so no sparse twin of these worlds exists).

## What this means for the line

X92's headline — "size is not a currency in this medium; the tempting correlation is mechanical" — survives, but its support is
weaker than the numbers looked: the live coefficient is **6–8 %** of variance explained at best (ρ ≈ 0.07), and on two of the four
samples here it does not clear a shuffle null of 0.04. The honest formulation is "no consequence of size has been demonstrated above
the noise floor of this estimator", not "size does not pay" — the latter claims a measured zero, which this analysis does not provide.

That also settles the practical question X92 raised: a sibling design (X93) trying to detect a 0.05-sized effect with this readout
would need samples where the null is below 0.02, i.e. about four times more structures than the current series carry.

## Caveats

- Two cells only (0.030, 0.040), because the dense series covers those; X92's other four cells have no dense counterpart.
- The shuffles are within-cell and 1 000 deep, so their 95th percentile has ~10 % sampling error of its own.
- Lifetimes are `last − first + 1` on logged steps; the dense series resolves them five times more finely, which is the variable the
  analysis wanted to move and could not isolate.

## Next

- The queue's field-line items that remain viable are X97 (siblings, second generation — needs runs) and a specificity-at-a-second-cut
  series (needs runs across thresholds). Both are registered as *conditional*: neither is worth ~1 GPU-hour until the current block's
  reports are read down.
- X110 (`γ_cell`) is running and will say how far each cell sits from its own boundary.

доска: принято 0, отклонено 0, отложено 0.
