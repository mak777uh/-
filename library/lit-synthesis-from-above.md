# The elephant from above

31.10.2026, after reading nine works in full or in their essential parts. This is the view from a distance: not what each
paper says, but what the whole shape tells us about our own work.

---

## 1. There are two literatures, and we were looking in the wrong one

**The first** is a scattering of striking cases inside our field: digital evolution exploiting bugs (Lehman 2020), a
cooperation result that vanished under asynchronous updating (Huberman & Glance 1993), gliders that dissolve when the
simulation gets better (Davis 2022, 2023, 2024), rounding that leaks into fitness (Pilat 2012), clipping that creates
timestep dependence (Kojima & Ikegami 2023). It has **no unified name and no review**. Its cases share one shape: a
surprising result that turns out to depend on a detail nobody varied.

**The second** is a discipline, sixty years old, with a canon: **verification and validation** of computational models
(Naylor et al. 1967; Oberkampf & Roy 2010). It already distinguishes exactly the failure classes we hit:

| V&V class | what it is | our instance |
|---|---|---|
| code verification | the code does not do what we think | `X46`: three arms, one dynamics |
| solution verification | numerical error is large enough to matter | `X56`, running now, first time ever |
| model formulation | the model cannot produce the phenomenon | uninhabitable pond, `b = 0.002` |
| analysis artifact | the statistic manufactures the effect | differenced mutual information |
| observation error | the sampling is not what we think | "1.67 cells" from the last snapshot |
| domain of validity | the claim exceeds what was tested | "the regime does not matter" at n = 20 |

We were not short of methods. **We were short of names**, and so we rediscovered five of them the hard way, in one day.

## 2. The most important sentence in the whole set

> "What would be considered systematic error in simulating billiard ball trajectories is essential for self-organization
> by some CA patterns." — Davis & Bongard 2022

This inverts the intuition every physicist carries into simulation: that finer is truer. For a class of patterns it is
not. The pattern **is** the discretisation, and refining it removes the pattern rather than the error.

That is why the useful question is never "is this an artifact?" but: **which object is my claim about** — this scheme at
this resolution, or a continuum ideal? Most of the failures in the first literature are not wrong simulations; they are
claims that silently changed object.

## 3. The uncomfortable fact about our own setup

Pearson's founding paper (1993, *Science* 261:189–192) reports that he checked **time steps from 1.0 to 0.01 and grids
from 256 to 1024** and found no qualitative difference in his spot regime.

We work at **grid 96**, below anything he tested, and we had **never varied `dt`** until this evening.

That is not a scandal — small grids are legitimate if the claim is about the discrete system. But it means that for
weeks our numbers carried an implicit continuum interpretation that was never tested at the resolution where the
founding paper did test it. Whatever `X56` returns, that sentence belongs in the methods section.

## 4. What actually fails most often is not the physics

Looking across the cases, the physics almost never lies. What lies is:

1. **the measure** — fitness that leaks rounding (Pilat), a component counter that measures fraying (us), a mutual
   information that manufactures lag (us);
2. **the definition** — "open-endedness" satisfied by a trivial system (Hintze 2019);
3. **the update rule** — cooperation that exists only under a global clock (Huberman & Glance 1993);
4. **the claim boundary** — a statement about a continuum that was only ever observed on a grid.

Only one of the four is numerical. **Three are about what we chose to call the thing.**

This is, uncomfortably, the summary of our own line: the physics in our world was never wrong. The counter was wrong,
the measure was wrong, and the claim was broader than the test.

## 5. The three rules I would keep from all of this

**Rule 1 — name the object.** Every claim states the scheme it belongs to: `dt`, grid, Laplacian, boundaries. If it is
about the discrete system, say so; never let "the model shows" stand in for "the continuum contains".

**Rule 2 — vary the thing you did not choose.** The detail that produces the surprise is almost always the one held
fixed. Our five failures: `dt`, sampling rate, connectivity of the manipulation, the readout field, the differencing.
None of them were choices we had defended; they were defaults.

**Rule 3 — a fix is a hypothesis, not a result.** Davis 2024 is a counterexample to the fix of 2023. When we remove a
suspected mechanism (clipping, a coupling, an income coefficient), the next step is not "solved" but "measured again".

## 6. What I would tell the owner in three sentences

The field has been here before, and it wrote the discipline down: verify the code, verify the solution, state the domain,
keep negative controls. Our line's weakness was never the world — it was the observables and the boundaries of the
claims, which is also exactly what the percolation and lifetime results say. The one test the founding paper of our
model performed and we never did is now running (`X56`), and its outcome is publishable in all three directions.

## 7. What is still unread, and what I will not claim

Fourteen works on the list remain `verified` but unread — including Nowak et al. 1994, which is the model for **how to
report a partial artifact** (a narrowed claim rather than a retraction), and Woolley 2022 on boundaries, which matters
because our grid is periodic. They are queued, not cited.

---

*Sources with DOIs: [`lit-reading-list.md`](lit-reading-list.md). The questions this reading raised for external
models: [`../reports/2026-10-31-questions-discretisation.md`](../reports/2026-10-31-questions-discretisation.md).*
