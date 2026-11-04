# The series: one step, one article

This file is the map of the research history as it is written up for an outside reader. It exists because the articles are
steps of one sequence and the sequence is the point (owner's rule, 05.11: describe the steps and what we find, then take new
steps, then a new article). The map answers three questions: which step is described by which article, what each article covers
by experiment number, and what is published outward versus still inside the project.

**Nothing in this file is a result.** Results live in `reports/`, in the aggregates under
`morphogenesis/experiments/E09_pond/`, and in the articles; this is the index that keeps the articles connected.

## The shape of every article in this series (owner's formula, 05.11)

> "Last time we briefly found this and decided to check that; below are the results of those checks, and where we try to move
> next."

Every article in the series therefore has the same three movements, and a reader can enter at any of them:

1. **Last time.** One short section at the top: what the previous step found (with its DOI, once it has one), and the questions
   that left open.
2. **What we decided to check, and the results.** The pre-registered questions and the outcome of each one — including the ones
   that came out negative, and including a correction when the earlier reading turns out to be wrong.
3. **Where we move next.** What is running now, under which pre-registration, and what the following article will report. The
   next step becomes its own article; this one is not extended into it, so that it can still be read alone.

Each article restates the definitions it uses rather than pointing at an earlier article, which is why the definitions agree
without the reader having to reconstruct them.

## The steps so far

| step | article | covers (experiment numbers) | status outward |
|---|---|---|---|
| **1** | [029 — How lineages begin and end in a pattern-forming chemical medium](../articles/029-lineages-in-a-pattern-forming-field.md), **v2.0** | X96–X155: the mixing length (9 ± 1 cells), a fusion as a merger, the whole-cell step with a spread in the timing, the end of a lineage as the loss of a name, the habitat reversal, the measured heredity slope | **published**: Zenodo, 04.11.2026, DOI [10.5281/zenodo.23933440](https://doi.org/10.5281/zenodo.23933440); the deposited archive carries aggregates up to X155 |
| **2** | 029 **v2.1** (the same file in the repository) | adds X161 (discrete trait), X164 (unequal pairs), X165 (three bodies), X166 (contact threshold at one-step resolution), X168/X169 (crossing against inflow, and the seam), X170 (what a daughter inherits) | **prepared, not deposited.** The published version is v2.0; v2.1 exists only in the repository and must go out as a *new version of the same Zenodo record* |
| **3** | [030 — The gap between surfaces, not the body size, switches fusion](../articles/030-the-gap-between-surfaces-decides-fusion.md), **v2.0** | **one article for the whole path after the published step**: X156–X159 (shape heredity and the geometry of the contact), X158 (the ~10-cell crossing), X162/X162b (local-scale heredity and the neighbour order), X164–X170 (unequal pairs, three bodies, the one-step threshold, reversibility and its control, the inflow-corrected crossing, the seam, the corridor against the source), X171–X183 (the corridor, the forecast, the edge, the cliff, the crossing table, dispersion, the ladder), X184–X197 (the local inflow at the seeded sites and its sign flip, the bridge over sites, the two phase censuses, the pool count, the gap-versus-size correction, the deviance drop against the unit of observation), X188/X189 (nucleation identity, withdrawn, and the bridge by local inflow) | **prepared, not deposited.** The owner decided on 05.11 that the continuation is one enlarged article rather than four; package `_exports/030-gap-switches-fusion-v2.0.zip`; waiting only on the owner's go |
| **4** | 030 **v2.1** (in progress) | X198: the fusion share as a curve in the gap (five gaps at radius 4, three at radius 6, 1152 worlds) | **running**; pre-registration `reports/2026-11-05-x198-gap-curve-plan.md` |
| **5** | the next article, still unnamed | making the local reading **predictive rather than descriptive**: fit the corridor/inflow reading on part of the crossing table and forecast cells that were not part of the fit (named as the next article in 030's section 8) | **not written.** The corridor block is no longer a separate article: the queue item `ART031_corridor` is superseded and its experiments are described in 030 v2.0 |

## The gap this map made visible, and what closed it

Until 05.11 the experiments that had run and closed but were described to an outside reader **nowhere** — neither in the
published 029 v2.0, nor in the un-deposited 029 v2.1, nor in the then-narrow 030 — were:

| block | experiments | where it is today |
|---|---|---|
| shape heredity and the geometry of the crossing before the census line | X156, X157, X159, X160 | **written into 030 v2.0** §5.1–§5.2 |
| local-scale heredity and the memory of the medium | X162, X162b | **written into 030 v2.0** §5.2 |
| the reversibility of a merge (and its control) | X167, X167b | **written into 030 v2.0** §5.2 |
| the inflow-corrected crossing and the ten-seed gap-11 check | X168c, X168d | **written into 030 v2.0** §5.1, with X168 withdrawn |
| the corridor, the forecast, the edge, the cliff, the crossing table, dispersion | X171–X183 | **written into 030 v2.0** §5.6–§5.7 |
| nucleation identity and the bridge read by local inflow | X188, X189 | **written into 030 v2.0** §5.8, with X188 withdrawn |

Two consequences, stated plainly. First, the published record is still **not** the whole path: the outward sequence jumps from
the aggregates up to X155 (step 1) to whatever is deposited next, and step 2 — written and checked — has not been deposited.
The repository text no longer has a hole; the outward record does, and closing it is the owner's decision to make. Second, 030
is *logically* the continuation of 029: it needs the mixing length, the definition of a body, and the distinction between a run
and a world, all of which 029 supplies; and 029 supplies them for a reader of that article alone, which is why 030 restates its
own definitions instead of assuming them.

## What keeps the articles connected

1. **Each article restates what it needs.** No article assumes the reader has read the previous one; every term it uses is
   defined in it, and the definitions agree because the code and the aggregates are shared.
2. **Each article says which step it is.** 030's section 8 names step 4 (running) and step 5 (the next article); 029's v2.1
   change note says what it adds to v2.0.
3. **Each article cites the step before it by DOI**, not by a bare title, once that step has a DOI: 030 cites
   10.5281/zenodo.23933440 as the published previous step, and names the un-deposited v2.1 as part of the same record.
4. **The map is updated when a step changes status**, and it is the only place where the outward status of the whole series is
   read at once. A step that moves from "prepared" to "published" changes one row here and one line in `lab/notices.md`.

## Open outward decisions (owner only)

| decision | what it is | where it is tracked |
|---|---|---|
| deposit 029 v2.1 | a new version of the existing Zenodo record 23933440, carrying X161–X170 | queue `PUB029_v21` |
| deposit 030 v1.1 | a new Zenodo record, one author, CC BY 4.0, package ready | queue `PUB030_submission` |
| the licence and the author list for 030 | author given (Ilya Vladimirov); licence left at CC BY 4.0 by default | same item |
