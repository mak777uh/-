# Questions on discretisation and non-Platonic patterns — for a run through models

31.10.2026. Written after reading Davis & Bongard (2022), Davis (2024), Davis (2023), Kojima & Ikegami (2023) and Pilat
et al. (2012) in full. These are not questions about the literature's existence — that was checked against Crossref —
but about **what to do with our own numbers**, where reading the papers changed the question.

Context in one paragraph. We run a Gray–Scott world at `dt = 1.0`, four-neighbour Laplacian, periodic boundaries,
grids 96 and 128. Our headline claims are that heterogeneity of inflow roughly doubles the number of threshold
components while the number of durable structures stays equal (1.3 vs 1.2), that both regimes are one percolation
cluster, and that form does not transfer. We have just started varying `dt` for the first time (`X56`, `dt = 0.5` with
12 000 steps and `dt = 2.0` with 3000, keeping physical time fixed).

**Answer format wanted.** For each question: what is known, with DOI; what it implies for our numbers; and if the
answer is "not established", say so rather than filling the gap.

---

## Q1. Is grid 96 defensible for Gray–Scott, when the founding paper tested 256–1024?

Pearson (1993, *Science* 261:189–192, DOI `10.1126/science.261.5118.189`) reported **no qualitative difference** for
`dt` from 1.0 to 0.01 and grids from 256 to 1024. We work at 96 — below anything he tested.

- Is there a published convention for the minimum grid in Gray–Scott studies of spot patterns?
- Does the answer depend on the pattern regime (`F`, `k`)? Ours is the self-replicating spot regime.
- Is a coarse grid acceptable when the observable is a **count of threshold components**, or does that observable
  specifically require finer resolution than pattern morphology does?

## Q2. Does anyone use "number of connected components above a threshold" as a valid observable in this model family?

We found (via Davis 2023) that the field uses gliders, persistence and morphology. We have not found work that treats
the component count at a fixed threshold as a *biological* observable, and we argue it measures fraying rather than
bodies.

- Is there literature using percolation or persistent homology on Gray–Scott excursion sets? (We have found Joe 2016 on
  persistence landscapes and Spector et al. 2025 on Turing patterns — are there others?)
- Is there a standard statement of the form "the number of spots at a fixed threshold is not a well-defined observable"?
- If not, is our percolation framing a contribution or a rediscovery?

## Q3. Tracking identity by overlap: is there a standard, and is ours adequate?

We track structures by `uid` inherited when the overlap between snapshots is ≥ 0.5. This gives lifetimes (median 57
steps in the heterogeneous world, 4046 in the homogeneous one).

- Is overlap-based identity standard in continuous media, or is there a preferred method (watershed tracking, persistent
  homology of excursion sets, optimal transport)?
- How sensitive are lifetime distributions to the overlap threshold? Is a 0.5 threshold defensible?
- With `dt = 0.5` the number of snapshots doubles; does that change apparent lifetimes systematically, and is there a
  known correction?

## Q4. What is the right way to report a non-Platonic result?

Davis (2023, DOI `10.54854/imi2023.01`) names patterns that exist only under coarse discretisation "non-Platonic".
If our contrast survives `dt = 0.5` and `2.0`, we can say it is step-robust. If it does not:

- What is the accepted wording in the literature for "this effect exists in this scheme and not in the continuum limit"?
- Is there a convention for reporting the **range** of `dt` over which a claimed effect holds?
- Does anyone report a **negative** result of this kind — "our effect is non-Platonic" — and how is it received?

## Q5. Diffusion and resolution are confounded in Gray–Scott — how do people disentangle them?

Davis reports that in Gray–Scott refinement, changing spatial resolution also changes the effective diffusion, and
labels part of his own evidence "putative" for that reason.

- What is the standard procedure to refine space without changing the effective diffusion (rescale `Du`, `Dv` with
  `dx²`)?
- Does that procedure apply to a five-point Laplacian on a periodic grid?
- If we refine only `dt` and not `dx`, what exactly can we claim — and what can we not?

## Q6. Has anyone published a Gray–Scott or reaction–diffusion result that later turned out to be a discretisation
artifact?

We have found: Pearson's check (no difference), Munafò's U-Skate precision comparison (lower variance in double, else
qualitatively the same), Davis's glider dissolutions, and Kojima & Ikegami's clipping analysis. We have **not** found a
published *biological interpretation* of a Gray–Scott pattern later shown to be numerical.

- Does such a case exist, with the four elements: original claim, defect, procedure that found it, change of
  interpretation?
- If not, is the honest statement "no such case is documented", or "we did not find one"?

---

## What we will do with the answers

| answer | action |
|---|---|
| Q1: 96 is below convention | rerun the headline contrast at 256 before publishing anything further; state the grid limitation meanwhile |
| Q2: no prior work | frame the percolation result as a methodological note, carefully, with Joe 2016 and Spector 2025 cited |
| Q3: overlap tracking is non-standard | switch to a named method and report both |
| Q4: wording exists | adopt it; if not, we propose it explicitly |
| Q5: rescaling is standard | refine space *with* `dx²` rescaling of `Du`, `Dv` in the next series |
| Q6: no documented case | say so exactly, and do not imply we are correcting anyone |
