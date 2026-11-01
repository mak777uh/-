# Reading list: simulation artifacts, non-Platonic patterns, and what to do about them

Kept open as a running list (31.10.2026). Purpose: **to know what has already been done, so as not to re-derive it** —
and to avoid the mistake of citing what we have not read.

**Status legend.** `read` — full text read end-to-end. `partial` — abstract plus key sections. `verified` — exists in
a register, not read. `queued` — to read next. `unverified` — could not be confirmed in any register.

Every DOI below was checked against Crossref or DataCite with `scripts/verify_references.py`, not taken on trust.

---

## Read in full

| # | work | what it gave us |
|---|---|---|
| 1 | **Davis & Bongard (2022)**, *Step Size is a Consequential Parameter in Continuous Cellular Automata*, ALIFE 2022, DOI `10.1162/isal_a_00526`, arXiv `2205.12728` | **`dt` is consequential**: a glider is stable only in `dt ≈ 0.245–0.978`; another pattern only near `0.1` and then only pseudo-stably. Smaller `dt` is **not** more accurate — patterns vanish. Behaviour changes qualitatively (hop / meander / corkscrew). This changed the interpretation rule for our `X56`. |
| 2 | **Davis (2024)**, *Non-Platonic Autopoiesis of a Cellular Automaton Glider in Asymptotic Lenia*, ALIFE 2024, DOI `10.1162/isal_a_00786`, arXiv `2407.21086` | A glider lives at `Δt = 0.2` and **dies at 0.17 and 0.26**, with no clipping at all — a counterexample to the "fix" of 2023. Robustness must be tested **per pattern**, after the fix as well as before. |
| 3 | **Pilat, Suzuki & Arita (2012)**, *Dealing with Rounding Error Problems in Evolutionary Physical Simulation*, DOI `10.1007/s10015-012-0038-0` | Rounding makes fitness chaotic in initial position (10 000 steps: mean 96.4, sd 56.5); double precision does not rescue long runs. Remedies: identical initial positions, fitness designed against it, precision. |
| 4 | **Lehman et al. (2020)**, *The Surprising Creativity of Digital Evolution*, Artificial Life 26(2), DOI `10.1162/artl_a_00319` | The anecdote collection: the genre exists, but it is anecdotes, not a taxonomy. Usable only in its own sense. |

### Read in full, 1 November: the identity and topology block

Downloaded after the four reviews named Q4 as the weak link. Read one at a time, in this order.

| # | work | what it gave us |
|---|---|---|
| 4a | **Jaqaman et al. (2008)**, *Robust single-particle tracking in live-cell time-lapse sequences*, Nat Methods 5:695, DOI `10.1038/nmeth.1237` | **Two-stage linear assignment**, not greedy overlap: frame-to-frame linking first, then a second pass that closes gaps of up to several frames and explicitly models **merges and splits**. Our `uid` rule is the one-stage greedy special case, without gap closing and without any lineage event. This is the standard our rule is measured against, and it is a higher standard than "overlap ≥ 0.5". |
| 4b | **Chalfoun et al. (2016)**, *Lineage Mapper: a versatile cell and particle tracker*, Sci Rep 6:36984, DOI `10.1038/srep36984` | Segmentation-independent tracking: overlap **plus** object properties (size, position, intensity) for association, with divisions and fusions detected as events and clumps resolved. Shows that a tracker can be built so that identity decisions are *reported* rather than implicit — which is what our aggregate hides. |
| 4c | **Spector, Harrington & Gaffney (2025)**, *Persistent homology classifies parameter dependence of patterns in Turing systems*, Bull Math Biol 88:10, DOI `10.1007/s11538-025-01552-9` | The most useful methodological paper in the corpus. Three concrete transfers: (1) the filtration is **normalised by the field's own `min`/`max`** in 20 steps, so patterns of different amplitude are comparable — our absolute 0.20/0.30 cannot do that; (2) the noise cutoff is chosen from the **distribution of barcode lengths** (bimodality, cut at the minimum), not by an arbitrary minimum area; (3) the stability theorem (Cohen-Steiner et al. 2006) is used explicitly to argue that numerical error cannot move the classification — and they concede in the same breath that "our notion of convergence is restricted to computational convergence" and that some observed patterns may be transient. Their mesh rule is also explicit: simplices no larger than **half the smallest unstable wavelength**. |

## Read in part (abstract + the sections that matter)

| # | work | what it gave us |
|---|---|---|
| 5 | **Kojima & Ikegami (2023)**, *Implementation of Lenia as a Reaction-Diffusion System*, ALIFE 2023, DOI `10.1162/isal_a_00638`, arXiv `2305.13784` | Asymptotic Lenia is **timestep-independent** and equivalent to a kernel-based Turing model; it can be implemented as a reaction–diffusion system. The constructive answer: build a scheme whose continuum limit exists. |
| 6 | **Davis (2023)**, *Discretization-Dependent Dissolution of Gliders in (Dis)Continuous Systems: Non-Platonic Self-Organization*, DOI `10.54854/imi2023.01`, arXiv `2401.13111` | The general statement of **non-Platonic** patterns, including the **Gray–Scott** family (U-Skate World, Munafò 2014): gliders persist only under specific, sometimes coarse, discretisation. Also: spatial resolution and diffusion are **confounded** in Gray–Scott refinement — a trap we would otherwise fall into. |
| 7 | **Pearson (1993)**, *Complex Patterns in a Simple System*, Science 261(5118):189–192, DOI `10.1126/science.261.5118.189` — via Davis's account | **The founding Gray–Scott paper already checked this**: no qualitative difference for temporal step `1.0 → 0.01` and grids **256 → 1024**. Our grid is **96** — coarser than anything Pearson tested. Cited in Davis as the earliest discretisation check in this model family. |

## Verified, not yet read — queued

| # | work | why it is on the list |
|---|---|---|
| 8 | **Huberman & Glance (1993)**, PNAS 90(16):7716–7718, DOI `10.1073/pnas.90.16.7716` | An apparent spatial-cooperation result that depended on **synchronous updating**. The classic "artifact" dispute in our field's neighbourhood. |
| 9 | **Nowak, Bonhoeffer & May (1994)**, PNAS 91(11):4877–4881, DOI `10.1073/pnas.91.11.4877` — **read in full** | The reply that **narrowed rather than reversed** the claim: a regime `1.8 < b < 2` is update-sensitive, broader cooperation survives. The four-step pattern — concede the regime, show the result does not generalise, argue about which model represents the biology — is adopted for our own step-dependent contrast (§10dy). |
| 10 | **Darius & Rojas (1994)**, *"Simulated molecular evolution" or computer-generated artifacts?*, Biophys J 67(5):2120–2122, DOI `10.1016/S0006-3495(94)80695-2` | The statistical/semantic critique: optimising tiny differences in a fitted quality function is not evidence of improvement when the uncertainty is larger. |
| 11 | **Woolley (2022)**, *Boundary Conditions Cause Different Generic Bifurcation Structures in Turing Systems*, Bull Math Biol 84:101, DOI `10.1007/s11538-022-01055-x` — **read in part 1.11**: abstract, introduction, discussion, appendices; the numerical sections are not read | The Turing bifurcation is a **pitchfork** under zero-flux boundaries and **transcritical** under Dirichlet — generically, for two-species systems in 1D — and **linear analysis cannot see the difference**, which is where most application papers stop. The explicit methodological rule: a sensitivity analysis that varies only parameters is incomplete, **boundary conditions must be varied too**. Our grid is **periodic**, which is neither of their cases, so the *result* does not transfer; the *rule* does, and it puts "we chose periodic boundaries" in the methods next to "we chose `dt` and grid". |
| 12 | **Theiler et al. (1992)**, *Testing for nonlinearity in time series: the method of surrogate data*, Physica D 58:77–94, DOI `10.1016/0167-2789(92)90102-S` | The proper foundation for the surrogates we improvised. Rejecting a null is not proving adaptation. |
| 13 | **Rechtsteiner & Bedau (1999)**, *A Generic Neutral Model for Quantitative Comparison of Genotypic Evolutionary Activity*, LNCS 1674:109–118, DOI `10.1007/3-540-48304-7_17` | Neutral-model comparison for activity statistics — the ancestor of our `beta = 0` null arm. |
| 14 | **Axtell, Axelrod, Epstein & Cohen (1996)**, *Aligning simulation models*, CMOT 1(2):123–141, DOI `10.1007/BF01299065` | "Docking": independent reimplementation as a check on assumptions, not on biology. |
| 15 | **Wilson et al. (2014)**, *Best Practices for Scientific Computing*, PLoS Biol 12(1):e1001745, DOI `10.1371/journal.pbio.1001745` | Tests, review, version control — the cheap part of V&V. |
| 16 | **Sandve et al. (2013)**, *Ten Simple Rules for Reproducible Computational Research*, PLoS Comput Biol 9(10):e1003285, DOI `10.1371/journal.pcbi.1003285` | Provenance rules; we already follow most of them by accident. |
| 17 | **Oberkampf & Roy (2010)**, *Verification and Validation in Scientific Computing*, CUP, DOI `10.1017/cbo9780511760396` | The canon. Code verification vs solution verification vs validation. We reinvented the first three under other names. |
| 18 | **Naylor et al. (1967)**, *Verification of Computer Simulation Models*, Management Science 14(2):B-92, DOI `10.1287/mnsc.14.2.b92` | The problem was framed sixty years ago as philosophical and statistical. |
| 19 | **Morrison (2007)**, *Computer Simulation: The Cooperation between Experimenting and Modeling*, Phil Sci, DOI `10.1086/519029` | Why "just run it and look" is epistemically unsafe. |
| 20 | **Parker (2008)**, *Does matter really matter?*, Synthese, DOI `10.1007/s11229-008-9434-3` | Whether a simulation can be an experiment at all. |
| 21 | **Taylor et al. (2014)**, *The Past, Present, and Future of Artificial Life*, Front Robot AI, DOI `10.3389/frobt.2014.00008` | ALife has **no V&V tradition of its own** — which is why we had to borrow one. |
| 22 | **Mitchell, Crutchfield & Hraber (1993)**, *Revisiting the Edge of Chaos*, DOI `10.48550/arxiv.adap-org/9303003` | The cautionary classic: a famous story weakened when redone with better statistics. |
| 23 | **McGuirl, Volkening & Sandstede (2020)**, *Topological data analysis of zebrafish patterns*, PNAS 117(10):5113–5124, DOI `10.1073/pnas.1917763117` — verified 1.11, **queued** | The precedent our corpus was missing: persistence summaries used to classify **biological** pigment patterns, not a toy model. If anyone asks whether this method has been applied to real patterns, this is the answer, and it makes a persistence companion to our counts a normal thing to do rather than an exotic one. |

## Unverified — do not cite

From the original 19-item catalogue: "non-Platonic gliders, Davis 2024, *Innovations in Machine Intelligence*" as
described there, "From Roundoff to Heredity" (2026), "Tripping Over the Past" (2026), Bullock's "free-floating models"
as described, "Digital Evolution Exhibits Surprising Robustness", and Tierra parasites dated PNAS 2026. See
[`artifact-catalogue-assessment.md`](artifact-catalogue-assessment.md).

---

## What the list already tells us

1. **The question is older than the field we work in** — 1967 in management science, formalised as V&V by 2010.
2. **For continuous media the key concept is "non-Platonic"**: a pattern that exists in the simulation and not in the
   ideal. Our `X56` was designed before we knew the word.
3. **Refinement can destroy a real pattern**, so "it vanished at finer resolution" is a statement about the claim, not
   an admission of error.
4. **Pearson checked `dt` from 1.0 to 0.01 and grids 256–1024 in the founding paper.** We work at grid **96** and had
   never checked `dt` until `X56`. That asymmetry is the most uncomfortable line in this table, and it belongs in the
   methods section whatever `X56` returns.
5. **A fix does not end the question** (Davis 2024 against Kojima & Ikegami 2023).

---

## Corpus status (1.11, after the identity block)

The list above is backed by a searchable corpus: full texts in `library/corpus/texts/`, manifest in
`library/corpus/manifest.json`, search via `python scripts/lit_index.py --search "<query>"`.

| status | count | which |
|---|---|---|
| read in full | **9** | Davis & Bongard 2022, Davis 2023, Davis 2024, Pilat et al. 2012, Huberman & Glance 1993, Nowak et al. 1994, Jaqaman et al. 2008, Chalfoun et al. 2016, Spector et al. 2025 |
| partial | **6** | Kojima & Ikegami 2023, Woolley 2022, Taylor et al. 2014, Wilson et al. 2014, Sandve et al. 2013, Mitchell et al. 1993 |
| downloaded, unread | **0** | — |
| verified, not in corpus | 10 | Theiler 1992, Rechtsteiner & Bedau 1999, Axtell et al. 1996, Oberkampf & Roy 2010, Naylor 1967, Morrison 2007, Parker 2008, Darius & Rojas 1994, Hintze 2019, Cohen-Steiner 2006 |

**The search that found nothing, revisited.** On 31.10 the query `"tracking identity components lifetime"` returned only
incidental hits, and the conclusion written here was that our identity tracking had **no precedent in what we had read**.
That was true of what we had read, and false of the literature: tracking by overlap is standard practice in cell and
particle tracking (Jaqaman 2008, Chalfoun 2016), and persistent homology supplies a threshold-free notion of birth and
death (Spector 2025, Cohen-Steiner 2006). What remains true is narrower and still uncomfortable: **none of it is about
Gray–Scott components**, and none of it validates our one-stage rule. The precedent exists; it sets a higher bar than
ours, and it is a bar we have not met yet.

The operational consequences are collected in [`lit-decision-rules.md`](lit-decision-rules.md), together with the two
checks that could be done without a new run and what they found.

**L-042** (grid conventions) and **L-043** (component counting vs percolation) are partially answered by the same block:
percolation and excursion-set framing are established, so the fragility of a fixed-threshold count is a known property
rather than our discovery — the demonstration in this model family is what is ours.

