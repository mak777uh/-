# Project Morphogenesis

Обновлено: 2026-10-29

A research bench for **morphogenesis in neural cellular automata (NCA)** — and, more recently, for a
narrower and harder question: **which conditions let a reproducing lineage persist in a digital
environment at all**.

The repository is not a demo. Every number in the manuscript is traceable to a run artifact, every
claim carries an explicit evidence type, and every experiment is pre-registered before it is run.
Negative results are published on equal terms, and the list of things we have *ruled out* is kept as
a first-class document ([`docs/eliminations.md`](docs/eliminations.md)).

**Language note.** The scientific record (manuscript, reports, world design, articles) is written in
Russian. This README is the English entry point for reviewers and collaborators; the machine-checked
experiment ledger below is bilingual by design.

---

## 1. Research question

We ask what a *minimal* digital world can support. The concrete object is a 32×32 pond with cells
that carry energy, age, damage and a membrane; resources regenerate locally; a frozen NCA rule
decides growth, division and death. Nothing is trained during a run.

The question we are working on now is not "can we produce life-like images". It is:

> **Under which environmental and organisational conditions does a lineage persist, coexist, and
> become subject to selection?**

That question is decomposed into a ladder of conditions — information, heritable variability,
environmental inheritance, coexistence, selection — each with its own minimal viable demonstration
and stop rule.

## 2. What is established

Short statements, each backed by artifacts listed in the ledger and in `manuscript/CLAIMS.md`.

**The learned rule is not conservative.** Started on an empty field, the frozen rule lights up all
1024 cells on step 1 (1023 grown cells), independent of initial resource and income: the live channel
has a positive bias. This is machine-checked as an invariant together with an *ignition gate* option,
and the gate is proven to keep an empty field empty at every step (Lean, `formal/Ignition.lean`,
4 theorems; Python analogue in the test suite).

**Founding is not the barrier.** In the gated world a colony is founded from a **single cell in
50/50 runs** (N = 1…20 cells × 10 seeds): median final population 586 (N=1) to 687 (N=20). Founder
size affects colony size (~17%), not the fact of founding.

**Invasion does not work.** A rare lineage injected into a resident colony dies in **0/10** runs in
all placement arms (into the resident / into a gap), with either merge rule, and at dose 20. Letting
minority types survive merging (`merge=keep`) gives **2/10**, and the survivors hold only
**0.18–0.30%** of the population — a trace, not coexistence.

**Four candidate mechanisms were eliminated by measurement**, not by argument: founder size (dose 20
→ 0/10; one patch reached 36% of the population and still died); merge overwriting (2/10 without it);
lineage bookkeeping (a corrected logger changed nothing: 2 lineages with ≥2 cells vs 18–23 under
neutral drift); resource shortage at the injection point (14/15 runs land on a depleted spot, and the
single run that landed on a full one, 0.9811, also died).

**Heritable variability works; selection is not yet measurable.** Heritable tag novelty appears from
mutation rate m ≥ 0.05 (10/10 seeds; novelty 14.7 per run; population unaffected — variation is free).
Environmental memory survives 1.3–2.4 generations, satisfying the *necessary* condition of
environmental inheritance; its *sufficiency* (does the next cohort benefit?) is **not** established —
two versions of that test were structurally insensitive and are reported as such. Selection itself is
blocked by architecture: reproduction in this world is colony-level budding, so a cell-level tag is
not a unit of reproduction and has no path to offspring.

## 3. What is ruled out

The registry of eliminated hypotheses is kept with artifact references and "what would revive it":
[`docs/eliminations.md`](docs/eliminations.md). Examples: the ring as an attractor (E02), asynchronous
updates, perceptual noise, five rule-learning schemes, smooth environmental drift, the dose-response
test at random placement, the "trivial radial bubble" reading of `struct_2`, plus the four mechanisms
above.

## 4. How the numbers can be trusted

1. **Pre-registration.** Every experiment has a plan with criteria committed *before* the run
   (`reports/*-plan.md`), including the branch structure of possible outcomes.
2. **Sensitivity arithmetic before launch.** Any A/B experiment must show the arithmetic that creates
   the difference (for energy experiments: break-even `own* = spent/(4·b)` and where the field sits
   relative to it). Two early series were insensitive *by construction*; both are reported as "the
   test did not reach the effect", never as "there is no effect".
3. **Seed anchors.** Each code change is validated by re-running a pinned reference run and comparing
   **bit-for-bit**. A diagnostic probe that consumed the RNG once shifted the world; the anchor caught
   it within 90 seconds.
4. **Artifact chain.** Raw run artifacts → aggregates → `manuscript/SUPPLEMENT.md` with `sha256` of
   every artifact → CI re-derives manuscript numbers from artifacts. Manifests (`lab/runs/*.json`)
   record command, commit, seed and environment for every run.
5. **Typed claims.** `manuscript/CLAIMS.md` records for each claim the evidence kind
   (`proof` / `test` / `statistics` / `observation` / `judgment`), its assumptions, what remains to be
   established, and the strongest wording the manuscript may use. A linter enforces the schema and
   that cited artifacts exist.
6. **Formal invariants.** Budget conservation, closure and the ignition gate are formalised in Lean
   (`formal/`: 17 hypotheses, 31 theorems), each with a Python analogue; `skipped` in CI is never
   reported as `proven`.
7. **CI.** Contract validation, README/manuscript consistency, claim lint, artifact hashes, section
   references and a portability canary run on every push; a nightly job re-derives aggregates.

## 5. Repository map

| path | what lives there |
|---|---|
| `morphogenesis/` | experiment code, tests, per-run artifacts (`experiments/`), canonical journal |
| `manuscript/` | the accumulating paper: `paper.md`, `CLAIMS.md`, `CHANGELOG.md`, `SUPPLEMENT.md` |
| `docs/` | world design (`world-design.md` §10 pond line), decision log, eliminations, formal method |
| `reports/` | pre-registrations, experiment cards, figures |
| `articles/` | one self-contained story per closed result (in Russian) |
| `library/` | literature notes with DOIs, methods and "code/data" blocks |
| `lab/` | machine contour: state, registry, queue, locks, run manifests, `STATUS.md` |
| `formal/` | Lean hypotheses (**F-ID**) with "what would refute it" in each file header |
| `scripts/` | `lab.py` (contract), `claims_lint.py`, `verify.py`, aggregators, artifact hashing |

## 6. Verifying this repository

```bash
python scripts/lab.py validate    # contract: registry ↔ README ledger ↔ manuscript map
python scripts/claims_lint.py     # evidence type, assumptions, artifact existence
make verify                       # everything above + section refs + Lean without sorry/admit
cd morphogenesis && python -m pytest -q tests    # 612 tests
```

No GPU is required for any of the above; GPU runs are only needed to produce new artifacts.

## 7. Scope and limits

- **No claim about life, consciousness or intelligence.** The allowed formulation is a class of
  observed behaviour and its boundaries. This is a contract rule, not modesty.
- **Small n.** Most experiments use 5–10 seeds per arm; results are reported as counts with Wilson
  intervals and ranges, not as p-values. A single run is labelled `observation` and cannot carry a
  strong wording.
- **Frozen rule.** The agent does not learn during a run; adaptation claims are limited to
  environment-facing mechanisms.
- **Modified worlds are named.** The ignition-gate series is a *different modification* of the world
  and is never compared numerically with the ungated series.

## 8. Experiment ledger (machine-checked)

Ids and statuses are **generated** from `lab/registry.json` by `python scripts/make_ledger.py --sync`
(checked by `--check` and by `python scripts/lab.py validate`); do not edit ids or statuses by hand.
The descriptive columns — period, question, outcome, evidence — stay hand-written.

<!-- ledger:start -->
| id | status | period | question | outcome | evidence |
| --- | --- | --- | --- | --- | --- |
| E01_criticality | closed | 18.10 | criticality and the primordial soup | historical series, outside the current program | [results](morphogenesis/experiments/E01_criticality/results.json) |
| E02_pattern | closed | 20.10 | the ring as a target | **negative:** the ring is not an attractor; layer-1 gate 0/5; reaching and holding are different regimes | [report](reports/2026-10-20-e02-pattern.md) · [article](articles/002-pochemu-kolco-ne-stalo-attraktorom.md) |
| WP4_R9 | closed | 20.10 | 5 R-9 seeds, reach/hold probe | sweep closed, WP4 gate not passed; Wilcoxon on 5 pairs gives p ≥ 0.0625 | [status](reports/2026-10-20-wp4-status.md) |
| E02b_morphospace | closed | 20–21.10 | census of the morphospace | **rich map:** 832 rollouts, 573/704 death/uniformity; `struct_2` learned candidate, `struct_1` architectural confound | [results](reports/2026-10-20-e02b-results.md) · [article](articles/005-chto-perepis-nashla-v-morfoprostranstve.md) |
| E02c_replication | closed | 21.10 | replication of R-9 on seeds 142/242/342 | **negative:** 0/3 new seeds give `struct_2`; seed142 → `struct_1`, 242/342 → `uniform_dark`; control seed42 → `struct_2` 64/64 | [results](reports/2026-10-21-e02c-results.md) · [article](articles/006-replikaciya-r9-struct2-ne-vosproizvelsya.md) |
| E02c_seed42_repro | closed | 21.10 | retrain seed 42 with frozen code | **reproduced:** weights bitwise equal; census `struct_2` 64/64 (stability 58/64) — class reproducible from the seed, not from the recipe | [results](reports/2026-10-21-e02c-seed42-repro-results.md) · [article](articles/007-struct2-vosproizvoditsya-iz-sida-no-ne-iz-recepta.md) |
| E02b_closures | closed | 21.10 | channels, body, asymmetry (inference only) | **mixed:** orientation returns 12/12; asymmetry −0.225 at matched mass; hidden-channel redundancy refuted | [results](reports/2026-10-21-e02b-closures-results.md) · [article](articles/008-izbytochnost-kanalov-telo-i-strukturnaya-asimmetriya.md) |
| E02c_seed_decomposition | closed | 22.10 | seed = init vs data order | **not separable:** init42/data101 → `uniform_dark` 64/64; init101/data42 → `struct_1` 64/64; `struct_2` zero in both | [results](reports/2026-10-22-e02c-seed-decomposition-results.md) · [article](articles/009-odin-seed-eto-dva-faktora.md) |
| E02b_alive_open | closed | 22.10 | open liveness gate | **refuted:** body returns 12/12 (IoU 0.821 vs 0.864); carriers are mutual; asymmetry grows with damage (ρ = −0.71) | [results](reports/2026-10-22-alive-open-results.md) · [article](articles/010-telo-i-tekstura-vosstanavlivayut-drug-druga.md) |
| E02b_carriers2 | closed | 22.10 | carrier of form and asymmetry dose-response | **mixed:** without the visible channel the body still returns 12/12 (IoU 0.809); sign −1 12/12 but median −0.354 vs predicted ≤ −0.60 | [results](reports/2026-10-22-carriers2-results.md) · [article](articles/011-formu-neset-skrytoe-sostoyanie.md) |
| E02b_clusters3 | closed | 22.10 | clustering of hidden channels | **mixed:** any half of the hidden channels carries the body (H-CH-8 confirmed) | [results](reports/2026-10-22-clusters3-results.md) · [article](articles/012-izbytochnost-i-nestabilnaya-asimmetriya.md) |
| E02c_colab_repro | closed | 22.10 | reproduction on a different stack (T4) | **not reproduced:** T4 gives `uniform_dark` 64/64 instead of `struct_2` | [results](reports/2026-10-22-colab-t4-repro-results.md) · [article](articles/013-odin-sid-raznye-steki-raznye-klassy.md) |
| E02c_seed_grid | closed | 22.10 | does initialisation 42 hold structure | **refuted in favour of the class:** initialisation 42 holds the structure across data orders | [results](reports/2026-10-22-e02c-seed-grid-results.md) · [article](articles/014-inicializaciya-42-derzhit-strukturu.md) |
| E02b_lesion_minimal | closed | 22.10 | minimal lesion | **mixed:** body returns from a single channel plus noise (H-CH-9) | [results](reports/2026-10-22-lesion-minimal-results.md) · [article](articles/015-odin-kanal-i-shum-asimmetrii.md) |
| E02b_lesion_necessity | closed | 22.10 | necessity of the carrier set | **confirmed:** the `informative_only` set {2,3,4,10–14} is sufficient | [results](reports/2026-10-22-lesion-necessity-results.md) · [article](articles/016-nositel-eto-podmnozhestvo-kanalov.md) |
| E02b_lesion_core | closed | 22.10 | core within the carrier set | **refuted:** removing any single channel of the set changes nothing — full mutual replaceability | [results](reports/2026-10-22-lesion-core-results.md) · [article](articles/017-vnutri-nositelya-polnaia-vzaimozameniaemost.md) |
| E02b_asymmetry_variance | closed | 22.10 | variance of asymmetry onset | **inconclusive:** the body threshold is reached on the first snapshot | [results](reports/2026-10-22-asymmetry-variance-results.md) |
| E02b_asymmetry_variance_retry | closed | 22.10 | retry with plateau time | **refuted:** ρ(d, t_plateau) = +0.434 against threshold 0.5 | [results](reports/2026-10-22-asymmetry-variance-retry-results.md) · [article](articles/018-pravaia-polovina-determinirovana.md) |
| E02b_asymmetry_sides | closed | 22.10 | left vs right half | **confirmed:** the right half reproduces (IoU 0.613–0.745) | [results](reports/2026-10-22-asymmetry-sides-results.md) · [article](articles/019-pravaia-vosstanavlivaetsia-vosproizvodimo.md) |
| E02b_left_outcomes | closed | 22.10 | left half outcomes | **refuted:** the left side is a continuum, not a class | [results](reports/2026-10-22-left-outcomes-results.md) · [article](articles/020-levaia-storona-kontinuum.md) |
| E02b_carrier_pairs | closed | 22.10 | carrier pairs | **refuted:** 11 of 28 pairs do not give a body | [results](reports/2026-10-22-carrier-pairs-results.md) · [article](articles/021-nositel-eto-kombinacii.md) |
| E02b_carrier_ch13 | closed | 22.10 | single channel {3} | **confirmed:** {3} alone gives a body 12/12 (IoU 0.839) | [results](reports/2026-10-22-carrier-ch13-results.md) · [article](articles/021-nositel-eto-kombinacii.md) |
| E02b_carrier_ch15 | closed | 22.10 | six channels without {3,14} | **refuted:** they still give a body 12/12 | [results](reports/2026-10-22-carrier-ch15-results.md) · [article](articles/021-nositel-eto-kombinacii.md) |
| E03_injury, E04_topology, E05_aging, E06_narration, E07_control_ablation | not started | — | historical entry points | outside the current program | [registry](lab/registry.json) |
| E08_precision_horizon | running | 23.10– | class as a phase of the trajectory | TF32 gives `uniform_dark` → `struct_2` along the trajectory; the horizon must be stated with any class claim | [research map](docs/research-map.md) · [protocol](docs/protocol.md) |
| E09_pond | running | 23.10– | conditions for a lineage in the pond world | a lineage becomes a unit of selection **only with cell-level budding** (`I_obs` 0.5614 vs null 0.0621, 10/10 seeds); pair-level budding (same tag and any tag) behaves like the colony world — one lineage, **not evaluable**; transfer beyond bodies (`R1`) keeps only "one against many" (10/10, p = 0.001), not monotonicity (6/10) or magnitude (1.765 vs 12–50); the price of a trait is a **direction, not a magnitude**: sign holds (17/20, p = 0.0013) but the Fisher-mean criterion fails (centre −0.453, 95 % CI [−0.635, −0.223]) and adding seeds **weakened** the effect (new −0.336 vs old −0.604); the environment is **not inherited**: with exact neighbour control the death-site residual is **−0.0093** (5/10, p = 0.62) and the occupancy share is set by the **number of live 4-neighbours** (0.744 → 0.881) | [world design](docs/world-design.md), [eliminations](docs/eliminations.md), [registry](lab/registry.json) | The trait-price magnitude stays undetermined **by construction**: the one lever that could raise the lineage count (a quota on the share of the world a single lineage may hold) was tested — 3 arms × 10 seeds — and it does not add lineages (median 4.0 → 5.0 → 4.0 against a target of ≥12, max 9 in 30 runs) while it flips the sign of the price (−0.656 → −0.272 → +0.315); the stop rule fired and the lever is closed (§10bf). The magnitude is not claimed by statistics either: Fisher-z mean over 25 runs is −0.453 with CI [−0.635, −0.223], so the upper bound stays above −0.3 and the pre-registered criterion fails; the first block of 8 runs gave −0.604 and the next 12 gave −0.336, i.e. the earlier estimate was biased high (§10bg). A pre-registered confirmation (30 fresh seeds, s = 0.05) fixes the magnitude at rho = -0.374 with 95% CI [-0.396, -0.266]: the price is reliably negative but the pre-registered bar of 0.3 is **not** met (upper bound 0.266), so the claim is closed, not extended. A check of the 'first block overestimates' idea failed inside this very series: seeds 111-125 gave -0.268 while 126-140 gave -0.402 (Spearman of seed index vs rho = -0.430), so block estimates are unstable in both directions (§10bi). The price turns out to be **channel-specific**: with the same trait routed to update frequency (investment held equal) the correlation vanishes — median rho +0.055, Fisher centre +0.001, CI [-0.080, +0.082], 29 lineages, rho computable in 20/20 runs. So the measured -0.37 belongs to the investment channel, not to the trait as such (§10bj). Coexistence turns out to need **desynchronisation**, not punishment: lowering the update probability alone (no trait, no mortality) raises effective lineages 1.52 → 2.95 → 6.05 (3.99×, bar ≥3), lineages with data 6 → 13 → 17, monotone in 19/19 paired seeds, pop_time 0.749 of control — more than the mortality lever (4.25) delivers, and without killing anything (§10bk). The two coexistence levers **amplify** each other rather than saturate: with both on, effective lineages reach 26.06 and 31 lineages with data, versus 16.3 predicted by a product of effects; log-scale interaction +0.445, 95% CI [+0.350, +0.566], positive in 17/19 paired seeds (§10bl). A live input from the real world was tested two ways: routed into energy it does **nothing** (the world is space-limited: a 10x change of income leaves pop_time at 100-107 %), while routed into the **update rhythm** it moves the organisation, and how much depends on the source's amplitude (a microphone recording with 85 % silence gives 9.25 effective lineages vs 1.65 in the control, the near-constant network latency gives 2.62). (§10bm). On a 1800-step horizon all three modes reach a plateau, but at three different levels: synchronous 1.30 effective lineages, asynchrony 2.00, both mechanisms 8.80 (medians of 5 seeds, non-overlapping spreads); the peak at step 600 is far higher (25.8) than the plateau, so the earlier headline numbers describe a slice, not a regime (§10bn). A surrogate test killed our own claim: with the mean update probability equalised at 0.454, the real microphone recording (8.22 effective lineages) is indistinguishable from a **constant** probability (7.21), and from phase-randomised (6.27) and shuffled (6.80) surrogates - so what we called 'contact with the world' is the average tempo, not the signal's structure (§10bo). An invasion pilot (8-cell invader vs ten neutral sentinels, 3 seeds x 2 arms) found **no signal**: one lineage's fate at 8 starting cells ranges from extinction to a 3x sweep, the invader does not stand out from the sentinels, and the arms do not differ; the design itself cannot separate coexistence from delayed exclusion yet (§10bp). With **equal cohorts** (10 invaders vs 10 sentinels of 8 cells each) there is no invasion advantage in either arm: invaders survive 22 % vs 30 % (control) and 28 % vs 32 % (asynchrony), and produce fewer descendants; so the diversity plateau is **not** maintained by rare-lineage recovery (§10bq). A 'fertile patch' experiment settled the owner's question: making reproduction easier in 11 % of the field does **not** attract life - the share of cells inside (11.1 %) equals the area share, and lineages stay local either way (median over-representation x3.3 without any treatment), because the binding constraint is free space, not willingness to divide (§10br). The frozen **individuation criterion** (contrast in an independent field >= 25 %, persistence, multiplication) is passed by the continuum field (food inside depleted 42-45 %) and **failed by the pond** (energy contrast 0.94-1.15 in 3 seeds): pond colonies are labels, not bounded structures (§10bs). **Object ablation** (an agent with no NCA rule, no mass threshold and no spore budding) reproduces both main results: the population stays pinned to capacity across a 4x income range (1024/1024 at 0.20, 0.10 and 0.05, collapse at 0.02) and diversity peaks at an intermediate tempo (q1 2.16 / 5.82 / 4.46 / 3.88 for p = 1.0 / 0.7 / 0.5 / 0.3). The space-limit claim therefore survives the change of carrier, with an explicit boundary: it holds above an income threshold (§10bt). **Hysteresis test**: three paths are sent through different tempos up to step 300 and identical tempo afterwards; compared at matched population the diversity contrast is -3.57 / -2.01 / +1.43 (sign flips, spread ~2.5), so the world is **Markovian at the macro level** - at this resolution *when* a signal arrives adds nothing to *what* it is (§10bu). A **second and third independent field** (age; damage is unusable as a ratio because the field is sparse and integer) confirm the first: contrast stays 0.94-1.15 for energy and 0.68-1.56 for age, so the pond's colonies have no boundary in either (§10bs-addendum). **Sensitivity gradient**: with the input tempo matched, final diversity is flat across c = 0…0.8 (q1 4.23 / 3.31 / 4.10 / 4.09 / 4.15), and a constant-tempo control at the same *realized* rate shows that fluctuating coupling only speeds up colonisation (554 vs 76 cells at step 300, 613 vs 617 at 600) - coupling changes the path, not the destination (§10bv). **Inheritance in the field**: a passive composition field raises between-structure variety threefold (sd 0.0067 vs 0.0022) but produces no directional shift, because in Gray-Scott the composition is regenerated from v each step instead of being carried - nothing to inherit (§10bw). **Tracked components**: with post-hoc component tracking the composition becomes heritable (parent-daughter r = 0.97) and between-structure variety grows sixfold (0.62 vs 0.105), but there is still no directional shift (0.935 vs 0.957): fast growth is not an unambiguous advantage because it depletes food (§10bx). **Survival channel**: composition affecting decay instead of growth produces real selection (mean s rises 0.957 → 1.294 at beta = 0.2, heritability 0.87) but drives **fixation** - one structure remains. Both worlds now agree: diversity does not grow with selection strength, it grows with environmental heterogeneity (§10by). **Frequency-dependent survival** stops fixation (1 → 2 structures), keeps composition variance (0.12-0.26) and prevents runaway selection (s 0.98-1.17 vs 1.26-1.29). The L1-L3 ladder in the continuum field is now complete: emergence, boundary, inheritance (r = 0.97), variation, selection, weak coexistence (§10bz). **Grain scale**: slowly changing heterogeneity beats frozen heterogeneity - 10 coexisting structures at a 3000-step pattern period vs 6 static and 2 at 300 steps; fast flicker gives the smallest composition variance (0.058). This explains why the raw 4 Hz hardware signal never showed an effect: to the world it is a fast signal (§10cc). **Slow envelope**: the raw hardware signal collapses coexistence to 1 structure, but its smoothed envelope (30-100 sample window, one switch per run) restores **4**; static conditions still win with 6. This explains all three earlier negative results with one cause - the signal was always faster than the world lives (§10cd). With **six seeds** the static and envelope arms turn out indistinguishable (medians 4 vs 6, CV 0.93 and 0.78, distributions fully overlapping); only the raw signal (1-2 structures) is reliably lower. Structure count is a noisy metric - same lesson as the step-300 slice (§10cd-addendum). **Recounted with the stable metric** (time-integrated component count): heterogeneity doubles coexistence (2.86 homogeneous vs 4.1-7.1), static beats any variation (7.14 vs 3.9-4.7), but the raw and envelope signals are indistinguishable (4.14 vs 4.43) - so the signal carries nothing beyond heterogeneity, and the earlier 'envelope restores' claim is retracted (§10ce). **Caution on the word coexistence**: the invasion-growth instrument (first attempt) is invalid - the seeded patch merges with resident structures and the lineage flag covers 64 % of the field. Until the type-based instrument is built, 'coexistence' in this line means 'simultaneous presence', not the strict sense (§10cf). **Division of labour between the two worlds**: the continuum field can show emergence, boundary, inheritance and selection but **cannot** measure strict invasion (components merge), while the pond can measure invasion with cohorts but has stipulated cells. Claims about emergence come from the field, claims about coexistence from the pond (§10cf-addendum-2). **A buffer that rewards the winner destroys coexistence**: environment memory amplifying inflow where a structure already was collapses 8.86 -> 1.00 (static) and 6.00 -> 0.14 (fluctuating), CV 0. Chesson's storage effect rescues rare types in bad phases instead of rewarding incumbents (§10cg). **Both buffer signs give monopoly**: feeding the fading gives 0.14 as well, so the inflow channel itself is unusable for a storage effect - a multiplicative boost always accumulates somewhere. Buffering must act on mortality, not inflow (§10cg-addendum). **Important caveat: component count measures occupancy, not diversity.** It is hump-shaped in occupancy (0 / 3 / 2 / 1 components at <30 / 30-60 / 60-90 / >90 % filling), so all comparisons in this line need an occupancy-matched control before they can be read as statements about niches (§10ch). **Cross-world mirror attempt failed for a principled reason**: in the pond food is not the limiting factor (space is, E2), so food heterogeneity cannot change coexistence; matching by ceiling does not match consumption (0.232 vs 0.084 experienced resource) because life itself redefines how much it gets. The field result must be mirrored with **space** heterogeneity, not food (§10cj). **The pond is too permissive to measure coexistence in its working regime**: invasion succeeds in 7-10 of 10 cohort lines in every arm, so everything coexists and the measure does not discriminate; a spatial patch even lowers survival slightly (9 to 8) while its sham control reproduces the control exactly. Before testing heterogeneity we need a regime where exclusion happens (§10ck). **The transfer did not happen**: in an exclusion regime (income 0.06, invasion fails for 4 of 10 lines) a spatial patch produces no change at all (median 6 in every arm, sham reproduces control), so diversity in the pond is governed by tempo while in the field it is governed by the spatial structure of inflow (§10cm). **Matched-inflow heterogeneity points the right way but is confounded**: with mean inflow equalised (base 0.5, rich 7.33, 15x contrast) the patch arm raises invader survival (median 8 -> 9) yet lowers occupancy (610 -> 555 cells) and leaves more uneaten food, so the effect may be lower density rather than niches (§10cn). **Live loop closed but the channel saturated**: baseline load 0.60 rose to 1.00 with four parallel worlds and the world heard a constant 100.0 (210 samples at 4 Hz). Our share was about 40 %, so the validity condition was met, yet a saturated channel carries no information - the loop needs total load at most 0.85 (§10cp). **Live loop instrument is not assembled yet**: the `system` source is a constant 100.0 stub, and although a working `self` source was added (0.0 idle, 0.064 single-thread, 0.495 with torch) and a real `__call__` defect was fixed, inside run_pond the live source still collects 0 samples because the world creates a second instance. E5 cannot be run until that wiring is fixed (§10cp-addendum). **Live loop closes but the world does not see itself**: a working self-source fed 1500 values and the footprint reached 0.53, yet population (4 to 621 cells) correlates with the signal at only +0.078 with no lag structure - the signal reflects torch threading, not world state (§10cq). **Three diversity metrics agree in order but the magnitude is small**: q=0 2/6/10/2, q=1 1.04/1.56/1.76/1.23, q=2 1.01/1.24/1.25/1.11 for homogeneous/static/period-3000/period-300, so the ordering is metric-independent while q=2 about 1.2 means one dominant structure plus fragments rather than six equal coexisters (§10cr). **Live loop, valid run**: with the repaired system source (load 0.17 idle, 0.667 with four worlds, our share 74 %) population correlates with the signal at -0.667 raw and -0.574 detrended, but only -0.007 on first differences - the apparent coupling is a shared slow shape, not causation at step scale (§10cs). **The dispersion gate has a boundary**: after three refinements (excluding dispersion indices, denominators and parameters, correlations and means near zero) 8 findings remain, but a machine cannot tell whether a claim rests on a level or on a sign - that is a property of the statement. It stays a warning in make health (§10ct). **The static-versus-varying claim is RETRACTED at n=20**: static 6.29 vs period-300 6.14, difference 0.14, bootstrap CI [-1.64; 3.71], Mann-Whitney z=0.92. The morning result of 7.14 vs 3.9-4.7 was 3-6-seed noise. What survives is only that heterogeneity beats homogeneity (§10cv). **Slow-varying heterogeneity is also indistinguishable from static at n=20** (both medians 6.29, bootstrap CI [-2.21; 3.29]), so of the line's quantitative claims only heterogeneity-beats-homogeneity remains, and it too needs n=20 before it can stand (§10cv-addendum). **What survives at n=20: heterogeneity roughly doubles the component count** - 6.29 static vs 3.07 homogeneous, difference 3.21, bootstrap CI [1.57; 6.00], Mann-Whitney z=4.23. The fact of heterogeneity matters, its regime does not (§10cw). **On grid 128 the direction reproduces but significance is marginal**: 5.86 vs 3.57, difference 2.29, bootstrap CI [-1.00; 6.71], Mann-Whitney z=2.04 at n=10, so the claim is supported on two grids by direction yet established only on grid 96 (§10cx).
| E10_formal | running | 24.10– | formal invariants of the world | 17 hypotheses / 31 theorems in Lean without `sorry`: ignition gate, budget and closure invariants | [formal method](docs/formal-method.md) · [inventory](lab/formal.json) |
<!-- ledger:end -->

## 9. Current status and how to follow the work

- Live status of the laboratory (what runs, what waits for a decision, what we deliberately do not
  do): [`lab/STATUS.md`](lab/STATUS.md).
- Decisions with reasons, including rejected proposals: [`docs/decision-log.md`](docs/decision-log.md).
- What has been eliminated and what would revive it: [`docs/eliminations.md`](docs/eliminations.md).

## 10. Citing and contacting

**Preprint.** A standalone preprint summarising this stage is archived at [10.5281/zenodo.23733719](https://doi.org/10.5281/zenodo.23733719) (v1.2; v1.1: 10.5281/zenodo.23694918; v1.0: 10.5281/zenodo.23669738) (concept DOI [10.5281/zenodo.23669737](https://doi.org/10.5281/zenodo.23669737); 14 pages, four figures, LaTeX source included; not peer reviewed).

**Release v1.2 (preparing):** measured price −0.374 with CI [−0.396, −0.266], the price belongs to the
investment channel, two coexistence levers that amplify each other, four recorded prediction failures.
Publication instructions: [`docs/release-v1.2.md`](docs/release-v1.2.md).

**Deposits.** The code, reports and journal are archived with a DOI
([10.5281/zenodo.23733477](https://doi.org/10.5281/zenodo.23733477); concept DOI
[10.5281/zenodo.23571609](https://doi.org/10.5281/zenodo.23571609)). The canonical weights are
a separate dataset record (`10.5281/zenodo.23654174`, 12 checkpoints + service files, 6.03 GB). The per-run artifacts behind preprint v1.2 are a dataset record of their own ([10.5281/zenodo.23734077](https://doi.org/10.5281/zenodo.23734077), 130 files, 10.1 MB) — see [`docs/deposit.md`](docs/deposit.md)
for what is inside each record and how to verify the checksums. Citation metadata is in
[`CITATION.cff`](CITATION.cff).


The manuscript is a living document (`manuscript/paper.md`, versioned in `manuscript/CHANGELOG.md`);
it is not submitted anywhere, and no external publication is made without the owner's explicit
approval. For any number, cite the artifact path from the ledger or from `manuscript/SUPPLEMENT.md` —
every figure there carries a `sha256` of its source file.
