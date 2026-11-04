# X168c — The crossing does not depend on the inflow rate (04.11)

**Question.** This is the corrected version of X168, which was withdrawn because it passed a surface gap to a flag that takes
a centre separation. The question stands: the crossing of §4.1 was measured at one inflow rate, `F` = 0.030, and if it is a
property of the medium's turnover it should move with `F`.

Pre-registration for the withdrawn version: [`2026-11-04-x168-inflow-crossing-plan.md`](2026-11-04-x168-inflow-crossing-plan.md);
its design is reused with the conversion corrected in one function, `sep_for(gap) = 2R + gap`. The analysis also carries the
withdrawal note in the aggregate.

Arms: `F` = 0.026, 0.030 and 0.036 at surface gaps 8, 10 and 11, five seeds each (961-965), 2 000 steps, separations 14, 16 and
17. A 6 000-step length control at `F` = 0.030 was meant to cover gaps 10 and 11; a filename collision in the runner kept only
the gap-10 half — recorded in the aggregate as `defect_note`, and it does not matter, as shown below.

## Result

| surface gap | `F` = 0.026 | `F` = 0.030 | `F` = 0.036 | X158 at `F` = 0.030 (6 000 steps) |
|---|---|---|---|---|
| 8 | 5/5 | 5/5 | 5/5 | 5/5 |
| 10 | 2/5 (40 %) | 2/5 (40 %) | 3/5 (60 %) | 7/15 (47 %) |
| 11 | 0/5 (0 %) | 1/5 (20 %) | 2/5 (40 %) | 2/15 (13 %) |

The gap-8 control fires at every rate, no run went extinct, and the separations recorded in the artifacts are 14, 16 and 17 —
the conversion is verifiably right this time.

**The crossing sits between 10 and 11 cells at every rate tested**, and the `F` = 0.030 row reproduces X158 closely (40 %
against 47 % at gap 10, 20 % against 13 % at gap 11) on a different seed set, a different run length and a different runner.
The 2 000-step and 6 000-step measurements agree, so the run length is not a confound.

**Verdict: no detectable dependence of the crossing on the inflow rate.** The gap-11 share does trend upward with `F`
(0 %, 20 %, 40 %), but with five seeds a spread of 40 % between the extremes is not separable from noise, and the item says so
rather than claiming a trend it cannot measure. The ten-cell crossing is a property of the reaction-diffusion pair, not of the
flow.

## What this restores and what it changes

§4.1's crossing stands as originally written, measured at `F` = 0.030 and now confirmed to hold at rates 13 % below and 20 %
above it. The withdrawn claim is not replaced by its opposite: the honest statement is that the crossing is **insensitive to
the inflow within the range tested**, which is a real result — a length that does not move when the source term changes by a
third is a length of the pattern-former, not of the source.

## Limits

Five seeds per cell place the crossing within a two-cell window and cannot see a moderate dependence: a share of 0 % against
40 % at gap 11 is exactly the size this design cannot resolve. The `F` range is narrow because the world leaves it quickly —
`F` = 0.020 dies, `F` = 0.040 barely divides — so "insensitive to the inflow" here means "insensitive across the range in which
this world lives", not a general statement. And one gap-11 length control is missing, though the short arm already matches the
long X158 value.

## What would kill it

Ten seeds per cell at gap 11 would resolve the 0/20/40 trend: if it survives, the crossing does depend on the rate and §4.1
needs the curve after all. A fine `F` sweep at a fixed gap of 11 (0.024 to 0.040, five points) would show whether the trend is
monotone or a threshold.

## Next hypotheses

1. **Ten seeds at gap 11** for the three rates — the only cell where the trend could become a measurement.
2. **A fine sweep** of `F` at gap 11 and gap 10 (`F` = 0.024, 0.027, 0.030, 0.033, 0.036, 0.039), to look for a threshold
   rather than a slope.
3. **Why it is insensitive**: measure the corridor field between the bodies at the moment of fusion in the low and high arms —
   if the corridor concentration at contact is the same in all three, the cell number is a consequence of that concentration
   and not of the source strength.
