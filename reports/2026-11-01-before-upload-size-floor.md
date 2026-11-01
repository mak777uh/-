# Before the upload: two inserts, and what they cost

1 November 2026, 14:40. This note replaces the single-insert version written at 00:35. Since then the day produced a
second qualification, and the package is still unuploaded, so both can go in together.

**Nothing published is wrong.** Both inserts qualify what a number *means*, not what it says. The count really is larger in
the heterogeneous world; the lifetimes really are 57 against 4046 in the design that produced them.

---

## Insert 1 — the count is a count of small components

§4.5, after the step-dependence paragraph. Measured at 00:20 (`2026-11-01-free-checks-cadence-and-size.md`):

> The extra components are also **small**. Counted with no minimum size the contrast is +3.57 at `dt = 1.0`; excluding
> components below 32 cells it is +1.36, below 64 cells +0.86, and below 128 cells +0.07, so above roughly a hundred
> cells the two worlds are indistinguishable. Heterogeneous inflow multiplies small, short-lived pieces; it does not add
> durable structures, whose numbers are the same in both worlds (1.3 against 1.2 per run).

Abstract: "roughly twice as many components" → "roughly twice as many **small** components".

## Insert 2 — the lifetimes belong to the trait channel

§4.5, immediately after the lifetime table. Measured at 14:35 (`2026-11-01-x68-identity-rule-result.md`, §10en):

> These lifetimes belong to the design in which each structure carries a composition that is inherited at division and
> modifies its growth. With that channel switched off — same geometry, same seeds, same identity rule — the ordering
> reverses: heterogeneous components live **longer** (medians 5999 / 5044 / 2607 steps at overlap cutoffs 0.3 / 0.5 / 0.7)
> than homogeneous ones (4030 / 1565 / 1565). The contrast is therefore a property of the feedback channel, not of the
> spatial organisation alone, and the overlap cutoff is part of the definition rather than a detail: raising it from 0.3
> to 0.7 shortens the median by a factor of 2.3.

This one also earns a change in the sentence that follows the table: "the entire increase in the component count comes
from short-lived structures" stays true, but it should read as being about *this* design.

## What is *not* needed

- **No spectral insert.** The article makes no claim about wavelengths or structure factors, so the day's grid work
  (X60–X67) does not touch it. That work belongs to the next paper, and it is already written up.
- **No change to the durable-structure result** (1.3 against 1.2): both inserts strengthen the same reading rather than
  contradicting it.

## What applying it costs

| step | time | risk |
|---|---|---|
| edit EN §4.5, the abstract, RU §4.5 | 15 min | the single-specification gate names releases by date, so no version conflict |
| add the new numbers to `scripts/check_article_numbers.py` | 15 min | the gate will fail until the aggregates are cited, which is the point |
| rebuild `_exports/logs-2026-11-01.zip`, recompute the hash, update §1 of the publisher instructions | 10 min | the archive contains the article, so the old hash in the instructions becomes wrong if not replaced in the same commit |

About forty minutes, and the hash in the instructions must be replaced in the same commit — a stale hash there is worse
than no note.

## The decision

- **Apply both, then upload.** Better text, forty minutes, hash and instructions change together.
- **Upload v1.6 as built, carry both to v1.7.** The text is not false; the qualifications arrive with the next release,
  which will also carry the spectral work and the turnover curve.

The record argues for applying: v1.6 exists because a sentence was published that the data did not support, and the cost
of that was a full correction cycle. Both inserts are the same kind of thing caught earlier, and the second one —
lifetimes belonging to the trait channel — is the sort of qualification a reviewer would otherwise extract by asking a
single question.

**This is the owner's call**, because it changes the scope of the central claims rather than fixing an error (§3).
