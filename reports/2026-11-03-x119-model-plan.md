# X119 — post-hoc record, not a pre-registration

**This file is not a preregistration and must not be read as one.** X119 was run without a plan: the script `scripts/x119_analyse.py` was written and executed in
one step, and only afterwards did the report and the links need the plan file that this line's discipline requires. Writing a plan now and dating it before the
run would be a forgery of the record; what follows is the analysis as it was actually performed, so that the numbers can be reproduced and so that the breach
is written down where the next reader will find it.

## Why it happened

X118 voided by design, and the replacement question — does the daughter count matter at fixed size — looked like a small delta on an existing script. It was
not: it introduced a new model (`alive ~ log(area) + daughters`), a new estimator (linear probability with a world-level bootstrap) and a new confound (age).
Any of those would have justified a registration. The rule exists precisely for the case "this is only a small extension".

## What the analysis actually did (the criteria the run applied)

1. **Connected:** every uid with a positive peak area in the twenty X108 runs — 2 257 in the lattice and 1 993 in the maze; leaves are included, unlike X113's
   depth analysis, because here the question is the structure's own survival.
2. **Controls:** heredity on the same pairs `≥ 0.35` (measured 0.548 / 0.480) — the only control the run had.
3. **Readout:** OLS coefficients of `alive ~ 1 + log(area) + daughters`, with 500 bootstrap draws resampling **worlds**, and intervals from the 2.5/97.5
   percentiles. Reported: both coefficients with intervals, the alive rate and the mean daughter count.
4. **Resolution would have been:** the bootstrap interval excluding zero, with the caveat that the maze alive rate is 3 % — the criteria the report applied.
5. **A refusal rule there was none.** The script has a void branch for too few uids, low heredity or a failed fit, but no registered statement of what would
   count as "cost of division" versus "age". That omission is exactly what the missing plan cost: the age confound was named in the report only because it was
   noticed while writing it, not because a rule demanded the check.

## What the run found

Area `+0.363` (CI 0.258–0.468) and daughters `−0.429` (CI −0.509 to −0.345) in the lattice; `+0.052` and `−0.051` in the maze. Full discussion, including the
age confound, is in [`2026-11-03-x118-x119-daughters-cost.md`](2026-11-03-x118-x119-daughters-cost.md).

## The consequence for the claim

The CLAIMS row for X119 carries the caveat that **age is not controlled**. It also carries, in its basis, the fact that the analysis was **not preregistered**
— a number from an unregistered model is weaker evidence than the same number from a registered one, and the line's own rule says so.

## The rule that this breach confirms

`docs/design-checks.md` already says a preregistration names five sections before the run. X119 shows the failure mode it was written against: an analysis
that "is just an extension" is exactly the one that skips the step, and the step is what would have forced the age control to be registered rather than noticed.

## Status

Written 2026-11-03 02:00 MSK, **after** the run it describes. X120 — the age control — is registered properly and has not been run.

доска: принято 0, отклонено 0, отложено 0.
