# X112 — void by its own control: areas measured off saved fields do not reproduce the logger's areas

**Plan:** [`2026-11-02-x112-cuts-dense-plan.md`](2026-11-02-x112-cuts-dense-plan.md) (21:36). **Aggregate:** none — the run is a void.
Analysis-only attempt on X108's dense fields; no GPU.

## What was attempted

Measure every structure's **area at 0.15, 0.20 and 0.25 on the frame where its genealogy was recorded**, using X108's saved fields, and
recompute the ladder and the specificity gap per cut. Identity would come from the 0.20 run; only the size definition would change — the
cheapest possible version of X99's cut sweep.

## Why it voided

The registered control required the 0.20 recomputation to reproduce X108's excursion-set coefficient within 0.02 (0.548 at 0.030,
0.480 at 0.040). It never did, under any anchoring scheme:

| anchoring of the structure on its frame | `ρ₁` at 0.030 / 0.040 (target 0.548 / 0.480) | pairs used |
|---|---|---|
| centroid pixel, `scipy` label (no wrap) | 0.771 / 0.397 | 588 / 584 |
| each uid at its own peak frame, `scipy` label | 0.521 / 0.397 | 1 495 / 653 |
| brightest pixel within a 5×5 window, periodic flood fill | 0.491 / 0.403 | 2 014 / 1 523 |
| brightest pixel of the structure found at a low cut of 0.10 | 0.410 / 0.361 | 1 859 / 1 161 |

The diagnosis is not a coding slip, it is a property of the objects:

1. **A centroid is not a place inside a structure.** uid 1 at `F = 0.030` has its centroid at `v = 0.035` while its ring peaks at 0.38 —
   the area-weighted centre of a crescent or a ring falls in the hole. Every anchoring rule that starts from the centroid therefore
   either finds nothing at 0.20 or jumps to a neighbouring structure.
2. **The logger's label wraps; `scipy.ndimage.label` does not.** Structures crossing the boundary are one object in the run and two in a
   naive relabelling. Implemented as a periodic flood fill after this was found (row 3), which raised coverage but not agreement.
3. **The low-cut anchor merges neighbours**: at `v > 0.10` neighbouring structures are often one blob, so its brightest pixel can belong
   to a different structure, and areas came out *smaller* than the logged ones (97 → 50 cells for uid 4).
4. **The pair set changes with coverage** — 588 to 2 014 pairs against X108's 2 211 — and `ρ₁` moves with it, which is the pooled-versus-
   subset problem this line has already been bitten by twice (X80, X91).

The control did its job: it stopped a cut comparison whose 0.20 baseline was not the same measurement as the published one.

## What this rules out, and what it leaves

**Ruled out:** a cut sweep can **not** be done by re-measuring saved fields. The identity of a structure lives in the logger's labeling
of a thresholded field; re-deriving an area at another threshold from the same frame changes *which pixels belong to which object*, not
just the size of one object. That is a real constraint on this line's analyses and it is now written down rather than discovered again
next time.

**Left standing:** X99 did the cut sweep the only way that works — **new runs at each threshold** (`--threshold 0.15 / 0.25`), so that
genealogies, areas and identities are all built at the cut under test. The same route is needed to ask whether the *ladder* and the
*specificity* move with the cut. That is X112b, registered as a series (twenty runs, one cell, two cuts) and not run tonight.

**Also left standing:** at `cut = 0.15` every scheme gave a *higher* `ρ₁` than at 0.20, and at 0.25 a *lower* one, in both cells — the
direction X99 found for the half-life. Four anchoring schemes agreeing on a direction is not a result, but it is the hypothesis X112b
should test, and it is written down before the runs.

## Caveats

- One box, one grid, one `k`; two cells.
- The four anchoring schemes are not independent: they share the frame set and the genealogy.
- No aggregate is written for a void; the numbers above are transcribed from the four runs of the script, which is committed.

## Next

- **X112b (registered, series):** twenty runs at `F = 0.030` — ten seeds × `--threshold 0.15` and `0.25`, X100's flags otherwise — then
  the same ladder and gap readouts, with X108's 0.548 as the 0.20 reference. Cost: about 35 minutes on the GPU lane.

доска: принято 0, отклонено 0, отложено 0.
