# X80, corrected: the two-peak check counted local maxima, and the medium's spectrum hardly moved at all

**Date:** 2026-11-02, 03:55 MSK. **Corrects:** `reports/2026-11-02-x80-dip-estimator.md` (same day, 03:45), §10ff, claims 296–297.
**Why it is a separate file:** reports are not rewritten after the fact, so the correction is appended here and the earlier text stays
as it was written.

## What was wrong

The two-peak check in X80 (`scripts/x80_analyse.py`) asked whether the radial power profile had a **strict local maximum** in
`[6, 9]` and another in `[10, 13]`. A shoulder — a bin that is high but not higher than both neighbours — fails that test. At
`w = 0.75` the second family sits at q = 10 as a shoulder, so the cell was scored 0/5 and the sweep was read as
"mixed, mixed, single scale at 8.7 cells".

That reading was wrong. Measured as a **power share** over the same fields (`P2 / (P1 + P2)`, each family summed over `|k − q*| <= 1`
around its peak in the window), the fifteen X80 fields give:

| cell | realised share, five worlds | second-family peak | cells with share in [0.15, 0.85] |
|---|---|---|---|
| w = 0.25 | 0.27, 0.27, 0.31, 0.31, 0.31 | q = 11 in 5/5 | **5/5** |
| w = 0.50 | 0.23, 0.18, 0.23, 0.22, 0.22 | q = 11 in 5/5 | **5/5** |
| w = 0.75 | 0.27, 0.29, 0.27, 0.27, 0.34 | q = 10 in 5/5 | **5/5** |

All three cells carry a second peak with roughly a quarter to a third of the power. The sweep moved the **prescribed** composition
from "mostly 12-cell" to "mostly 8.7-cell" and the **realised** spectrum barely moved: 0.27–0.31, 0.18–0.23, 0.27–0.34.

## The pilot that exposed it

A pilot for the next series at prescribed power ratio 1.0 gave a realised share of **0.19**; at 4.0, **0.31**; at 16.0, **0.28**
(three runs, seed 181, `F = 0.030`). Sixteen times the power buys a shoulder of 0.3 and no more. The medium keeps its own preferred
scale; the imposed one is admitted only as a minority, whatever the prescription.

## What this does to the X80 verdict

- **"0/5 two-peaked at w = 0.75" is withdrawn.** It was a definition artefact, not a property of the world.
- The registered **positive control failure stands** (the `w = 0.25` wing gave 0.86 against a required 1.0), and it now reads as
  the same fact from the other side: no cell in that sweep was single-scale.
- The registered **"slope"** verdict is therefore not a slope across degrees of mixedness — it compares three spectrally
  near-identical cells (0.86, 1.18, 1.25 pooled; 1.04, 0.52, 1.16 per-world median). The honest verdict for X80 is **void by
  manipulation reach**: the cells differ by less than the noise in the quantity the design meant to vary.
- What survives, now stated correctly: **at `F = 0.030` the composite world carries a second peak of about 0.2–0.3 whatever the
  imposed weight, and both mixture cells are shorter-lived than the single-scale reference (0.86 and 1.18 pooled against 1.47)** —
  a statement about the composite, not about a graded mixture. It agrees with X78b (1.03) and X79's `w = 0.25` cell (0.76).

## The method lesson, which is the durable part

Two gates failed in the same direction today, and both failed *silently*:

1. A **peak count** passes on a tie (X80 plan, §1: "the middle cell must be the most two-peaked" — 5/5 against 5/5 passed it) and
   fails on a shoulder (this report). A count is not a manipulation check; a **share with a numeric tolerance** is.
2. The check was computed by a **different function** (strict local maxima in `x80_analyse.py`) from the quantity the claim then
   spoke about ("equal parts"). The contract already has a gate for this class — definitions versus implementations — and it only
   covers metrics that are registered as definitions. A design's manipulation check deserves the same treatment: one function, used
   by both the check and the claim, with the tolerance written before the run.

Both are now encoded: X82's preregistration fixes the share definition before the run and sets the control as "single scale must
read below 0.15", which a harmonic could not pass by accident.

## What is being done instead

`reports/2026-11-02-x82-reach-plan.md`: five cells (prescribed share 0 / 1 / 4 / 16 at q = 11, and 4 at q = 14), five worlds each,
measuring the transfer function from prescribed to realised share. That number decides whether a mixedness design is possible in
this world at all, and it is the sentence the next design has to respect.

доска: принято 0, отклонено 0, отложено 0.
