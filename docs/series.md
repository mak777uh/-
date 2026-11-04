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
| **3** | [030 — The gap between surfaces, not the body size, switches fusion](../articles/030-the-gap-between-surfaces-decides-fusion.md), **v1.1** | X158 (the ~10-cell crossing), X184–X187 (the local inflow at the seeded sites, and its sign flip at the largest bodies), X190–X193 (the bridge over sites, and the two phase censuses), X194 (how many worlds a pool holds), X195/X196 (the sign sweep and the gap-versus-size correction), X197 (the deviance drop against the unit of observation) | **prepared, not deposited.** Package `_exports/030-gap-switches-fusion-v1.1.zip`; waiting only on the owner's go |
| **4** | 030 **v1.2** (in progress) | X198: the fusion share as a curve in the gap (five gaps at radius 4, three at radius 6, 1152 worlds) | **running**; pre-registration `reports/2026-11-05-x198-gap-curve-plan.md` |
| **5** | **031** — the corridor at contact and what it forecasts | X171, X172, X174, X175, X176 (the corridor and the forecast at an unrun supply), X177, X178, X179 (the band's upper edge, the radius-6 cliff, the full two-body crossing table), X180, X181 (how much between-family dispersion is real), X183 (the local reading that orders the rate ladder), X188/X189 (nucleation identity and the bridge by local inflow) | **not written.** Named as the next article in 030's section 8; tracked as the queue item `ART031_corridor` |

## The gap this map makes visible

The experiments that have run and closed but are described to an outside reader **nowhere** — neither in the published 029
v2.0, nor in the un-deposited 029 v2.1, nor in 030 — are:

| block | experiments | where it is today |
|---|---|---|
| shape heredity and the geometry of the crossing before the census line | X156, X157, X159, X160 | reports and `docs/world-design.md` sections only |
| local-scale heredity and the memory of the medium | X162, X162b | reports and plan sections only |
| the reversibility of a merge (and its control) | X167, X167b | reports and plan sections only |
| the inflow-corrected crossing and the ten-seed gap-11 check | X168c, X168d | reports and plan sections only |
| the corridor, the forecast, the edge, the cliff, the crossing table, dispersion | X171–X183 | reports and plan sections only; this is article 031 |
| nucleation identity and the bridge read by local inflow | X188, X189 | reports and plan sections only |

Two consequences, stated plainly. First, the published record is **not** the whole path: the outward sequence jumps from the
aggregates up to X155 (step 1) to the census line (step 3), and step 2 — which is written and checked — has not been
deposited. Second, 030 is *logically* the continuation of 029: it needs the mixing length, the definition of a body, and the
distinction between a run and a world, all of which 029 supplies; and 029 supplies them for a reader of that article alone,
which is why 030 restates its own definitions instead of assuming them.

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
