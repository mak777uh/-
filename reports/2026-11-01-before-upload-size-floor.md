# Before the upload: one improvement, and what it costs

1 November 2026, 00:35. Written after the package for v1.6 was built and after two checks on stored snapshots
([`2026-11-01-free-checks-cadence-and-size.md`](2026-11-01-free-checks-cadence-and-size.md)) changed what we know about
the headline number.

**The uploaded text is not wrong.** "Roughly twice as many components" is what the count gives at threshold `v ≥ 0.2`
with no size floor. What the checks add is *what those components are*: at `dt = 1.0` the contrast is unchanged down to
8 cells, `+1.36` at 32, `+0.86` at 64 and `+0.07` at 128. Above ~100 cells the two worlds are indistinguishable.

Two things follow, and neither is a correction of a false statement:

1. The doubling is a doubling of **small** components (16–64 cells), not of durable structures. The durable-structure
   result (1.3 vs 1.2 per run) is unaffected and agrees with this.
2. `+3.57` is cadence-dependent: at 13 / 7 / 4 snapshots it is `+3.69 / +2.79 / +1.00`. The gap between `dt` values is
   robust (at matched physical times, `+4.20` against `+0.40`); the absolute number is a property of the estimator.

## The insert, if we apply it

In §4.5, after the paragraph on the step dependence and the plateau, add:

> The extra components are also **small**. Counted with no minimum size the contrast is +3.57 at `dt = 1.0`; excluding
> components below 32 cells it is +1.36, below 64 cells +0.86, and below 128 cells +0.07, so above roughly a hundred
> cells the two worlds are indistinguishable. Heterogeneous inflow multiplies small, short-lived pieces; it does not
> add durable structures, whose numbers are the same in both worlds (1.3 against 1.2 per run). The absolute magnitude
> is also a property of the sampling: with 13, 7 and 4 snapshots it is +3.69, +2.79 and +1.00, while the gap between
> `dt` values survives when both runs are sampled at the same physical times.

Correspondingly, in the abstract, "roughly twice as many components" → "roughly twice as many **small** components".

## What applying it costs

| step | time | risk |
|---|---|---|
| edit EN §4.5 and the abstract, RU §4.5 | 10 min | the single-specification gate names the release by date, so no version conflict |
| add the new numbers to `scripts/check_article_numbers.py`, re-run it | 10 min | the gate will fail until the aggregate is cited, which is the point |
| rebuild `_exports/logs-2026-11-01.zip`, recompute the content hash, update §1 of the publisher instructions | 5 min | the archive contains the article, so the hash changes and the old hash in the instructions becomes wrong if not updated |

Roughly half an hour of work, and the archive hash in the instructions must be replaced in the same commit — a stale
hash there is worse than no note.

## The decision, stated plainly

- **Apply, then upload.** Better text; half an hour; the instructions and the hash change.
- **Upload as is, correct in v1.7.** The text is not false; the refinement arrives with the next release, which will
  also carry `X57`/`X58` and the tracking sensitivity.

The laboratory's own record argues for applying: the v1.6 release exists because a sentence was published that the data
did not support, and the cost of that was a full correction cycle. This is the cheaper version of the same situation,
caught before the upload rather than after.

**This is the owner's call, not the agent's**, because it changes the scope of the central claim rather than fixing an
error — the one thing the contract reserves (§3).
