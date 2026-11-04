# X168 — The crossing moves with the inflow rate, and not monotonically (04.11)

**Question.** The crossing of §4.1 — "contact at about two cells" — was measured at one inflow rate, `F` = 0.030, the parameter
the whole line treats as central. If the crossing is a property of the medium's turnover, changing `F` should move it, and the
number would be a value at one rate rather than a length of the medium.

Pre-registration: [`2026-11-04-x168-inflow-crossing-plan.md`](2026-11-04-x168-inflow-crossing-plan.md). Two arms, `F` = 0.026
and `F` = 0.036, at surface gaps 8 and 11, five seeds each (20 runs, 2 000 steps). Viability was probed first: `F` = 0.020
dies (0 components by step 400), `F` = 0.026 keeps five bodies alive and dividing, `F` = 0.040 leaves one body with no
divisions by step 400 — the window is narrow and the arms sit inside it.

## Result

| arm | gap 8 | gap 11 |
|---|---|---|
| `F` = 0.026 | 5/5 fused | **5/5 fused** |
| `F` = 0.036 | 5/5 fused | **5/5 fused** |
| `F` = 0.030 (X158, for comparison) | 5/5 | **2/15 (13 %)** |

The gap-8 control fires in both arms, no run went extinct, and the readout varies (the gap at the last two-body step has a
standard deviation of 4.15 cells across runs).

**The gap-11 pair fuses in 100 % of runs at both new inflow rates, against 13 % at `F` = 0.030.** Both a 13 % lower and a 20 %
higher inflow push the crossing past eleven cells — the two arms agree with each other and disagree with the baseline, which is
the signature of a **minimum near 0.030** rather than of a monotone trend.

**Verdict: the crossing moves with the inflow rate, non-monotonically.** The "about two cells" of §4.1 is a value at one
inflow rate; at 0.026 and at 0.036 the crossing lies beyond eleven cells. This design shows the direction and not the new
position — both arms fused at gap 11, so their crossings are not located, only bounded from below.

## What this changes

§4.1 cannot say "the medium tolerates contact at about two cells" without naming the inflow rate. The honest form is: at
`F` = 0.030 the crossing is ten cells and the contact tolerance about two; at rates 13 % below and 20 % above it, the crossing
moves outward past eleven. The fusion block's other results (X164, X165, X166) were all measured at 0.030 and inherit the same
qualification, which is now written into §10ia and flagged in §4.1.

## Limits — and they are large

The design brackets nothing: with both arms at 100 % at gap 11, the crossing could be at 12 or at 20 in each, and the
"minimum near 0.030" is inferred from two points that both sit on the far side. A non-monotone result with two arms is weak:
the honest reading is "the crossing is sensitive to `F` and not in a way one arm pair can map", and the shape (a minimum) is a
hypothesis this item raises, not one it establishes. The X158 baseline at gap 11 (2 of 15) is a different seed set and a
different run length (6 000 steps against 2 000), which is a real confound: fusion at gap 11 may also depend on run length if
slow approaches eventually succeed.

## What would kill it

Bracketing at gaps 12, 14 and 16 at both new rates would either locate the crossings (confirming the outward move) or show
that the gap-11 fusions are the slow-approach tail and that the crossing is unchanged — the second outcome would reinstate the
original number. A rerun of `F` = 0.030 at 2 000 steps with seeds 961-965 would remove the run-length confound and is the
first thing to do.

## Next hypotheses

1. **Brackets at 12, 14, 16** for both new rates, five seeds each, and a matched `F` = 0.030 arm at 2 000 steps and the same
   seeds — the confound-free version of this item.
2. **The minimum as a prediction**: if the crossing has a minimum at 0.030, a fine sweep of `F` from 0.024 to 0.040 at a fixed
   gap of 11 should show a dip; that is a sharper test than endpoints.
3. **Why a minimum**: at low inflow the bridge builds faster than it is consumed, at high inflow the bodies grow more slowly and
   so approach longer — two mechanisms pulling in the same direction at opposite ends of the range, which is testable by
   measuring the time to fusion in each arm.
