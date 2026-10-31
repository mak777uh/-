# Catalogue of simulator artifacts: what the papers actually say

Received 31.10.2026 as a list of 19 documented cases where simulation artifacts were mistaken for biology or
adaptation. Prepared by a language model, unchecked.

Two rounds of checking were done, and the second matters more than the first:

1. **do the references exist** — via Crossref and DataCite with `scripts/verify_references.py`;
2. **do they say what the list claims** — via abstracts from OpenAlex (`_hourly/refs_abstracts.json`).

Result: **six of twelve references do not exist**, and of the six that do, **two say something else entirely**. A
catalogue about artifacts mistaken for results contained both kinds of artifact.

---

## Round 1 — existence

| # | item | register verdict |
|---|---|---|
| 1, 2, 3, 10 | simulator exploits, force overflow, Q*bert, fitness loopholes | **exist**: Lehman et al., *The Surprising Creativity of Digital Evolution*, **Artificial Life 26(2), 2020**, DOI `10.1162/artl_a_00319` (earlier: ALife 2018, `10.1162/isal_a_00016`) |
| 5 | reality gap | **exists**: DOI `10.1109/tcds.2021.3112236`, **2023** (list said 2021) |
| 6 | climate constraints | **exists**: DOI `10.1111/ele.14173`, **2023** (list said 2024) |
| 7 | mutation biases | **exists**: *Are Artificial Mutation Biases Unnatural?*, LNCS **1999**, DOI `10.1007/3-540-48304-7_11` |
| 9 | rounding error and fitness | **exists**: DOI `10.1007/s10015-012-0038-0`, 2012 |
| 11 | reward tampering | **exists**: DOI `10.1007/s10710-023-09456-0`, 2023 |
| 19 | "simulated molecular evolution or artifacts?" | **exists**: DOI `10.1016/s0006-3495(94)80695-2`, 1994 |
| 4, 8, 12, 14, 18 | non-Platonic gliders (Davis 2024); "From Roundoff to Heredity" (Zenodo 2026); "Tripping Over the Past" (2026); Bullock on free-floating models; "Digital Evolution Exhibits Surprising Robustness" | **do not exist** in either register — every one of them dated 2026 |
| 13 | Tierra parasites "PNAS 2026" | **does not exist** as described; Tierra's parasites are Ray's 1990s work |
| 15–17 | monoculture penalty, interpolation artifact, mass-conservation clamp | **community self-reports**, not publications — the list says so |

## Round 2 — content, by abstract

| # | what the abstract actually says | does it support the list's use? |
|---|---|---|
| 1, 2, 3, 10 | A collection of **anecdotes** from the evolutionary-computation and ALife communities about digital evolution surprising its researchers — including, but not limited to, exploiting simulator bugs. The abstract is about evolution's creativity, not about artifacts. | **Partly.** Usable as "such surprises are documented across the field". **Not** usable as "a paper about pattern dependence on discretisation" — which is how I first used it, wrongly, in §3.1. That citation has been removed from the article. |
| 5 | The reality gap **when morphology and controllers evolve together**; how robot morphology influences the gap. | **No.** It is about sim-to-real transfer, not about artifacts mistaken for biology. Irrelevant to us. |
| 6 | Genetic correlations constraining thermal adaptation to climate change, via individual-based simulations. | **No.** The list describes "undeclared methodological artifacts in performance functions". The paper is about **evolutionary constraints**, and the description is wrong. |
| 7 | No abstract available. Title is a conceptual question about mutation operators. | **Unverified in content**; unread. |
| 9 | No abstract available. Title is exactly "rounding error problems in evolutionary physical simulation". | **Plausible precedent** for "numerical detail changes the fitness", but unread and cited once. |
| 11 | Reward tampering: agents bypassing the intended objective; asks whether evolutionary algorithms can help ensure trustworthy solutions. | **Adjacent, not supporting.** It studies AI-safety of reward tampering rather than researchers mistaking an artifact for adaptation. |
| 19 | No abstract available. Title is the exact question, "simulated molecular evolution or computer-generated artifacts?". | **Plausible precedent** for the general worry; unread. |

---

## What is actually citable

**Nothing from this list enters the article except, at most, the Lehman et al. anecdote collection — and only in the
sense the abstract supports**: that digital evolution has repeatedly surprised researchers by finding unintended
solutions, which is a documented genre. It is not a citation for numerical sensitivity.

The three papers closest to our own failure mode (9, 19, and the 1999 mutation-bias piece) have **no abstracts in
OpenAlex** and have not been read. They go to the queue, not to the bibliography.

## The correction this forced on us

My first use of Lehman et al. in §3.1 was wrong: I cited it for "pattern dependence on the integrator", and the paper
is about evolution exploiting bugs. The sentence now states the numerical scheme plainly **without** a citation. The
scheme itself — explicit Euler, `dt = 1.0`, `Du = 0.16`, `Dv = 0.08`, four-neighbour Laplacian, periodic boundaries,
grids 96 and 128 — stays in the methods, because the reader needs it whether or not a citation supports it.

## Lessons worth keeping

1. **Existence is not content.** Six of twelve references were invented; two of the six real ones say something else.
   Checking a DOI is half the job.
2. **Recent dates are a tell.** Every invented reference was dated 2026.
3. **A catalogue of artifacts is not exempt from being an artifact.** The irony is not decorative; it is the same
   failure we spent a day finding in our own work.
4. **Check with tools, not with memory.** Crossref, DataCite and OpenAlex answer direct HTTP queries; the
   `verify_references.py` script turns this into one command and caught six fabrications in a single run.

## Status

Material lives in `library/`. Queue item `X55_verify_artifact_catalogue` covers reading papers 7, 9 and 19 in full and
deciding whether any of them changes our text. Until then there is nothing to cite here.
