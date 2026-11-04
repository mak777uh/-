# STATUS — canonical flow of attention

One file, one place that says what is actually in work. Machine state lives in `lab/state.json`, the log in
`_hourly/log.md`, numbers in artifacts. The Russian sections below the line are **history** and are not rewritten; the top
part is kept current (new text in English — decision of 31.10).

**Updated:** 2026-11-05, 00:55 MSK.

## Where we are, in one page (asked for in plain language on 04.11)

**Nothing is running and no lock is held.** `lab/state.json` reports `active_runs: 0`; the items below are analysis over
committed projections or short CPU series that have finished.

**On the "see the living" plan (`docs/plan-alive.md`, stages P0–P4) we are at P0, and the lab never claims life** — the
contract allows only "an observable class of behaviour and its boundaries", so progress is scored by rulers, not by words.

| stage | what it needs | where we are |
|---|---|---|
| **P0** deadly price + behaviour metric | an error must have a price, then survival has to differ between the right and wrong zone, before and after the environment flips | the **price exists** (503 alive and 0 deaths before; 59 deaths and 50 alive with the deadly cost, richness bias 1.39), the **metric is the open part** |
| **P1** lifetime plasticity | one internal prediction updated by its error, modulating behaviour | not started; Lean's `F-ADAPT` already bounds when it can matter (learning must be faster than dying) |
| **P2** family of environments + transfer | train/select in one environment, test in three others | not started |
| **P3** meta-learning | learning speed itself under selection | not started |
| **P4** multi-level individuality | components with identity over time, group reproduction | where the field line has been working; it now has facts, one law and its boundary |

**What today's field line added to P4** (items X180–X187, all closed, sections 10io–10iv of the `docs/world-design.md` index):
the rate a run "has" is not the nominal rate but the **local inflow at the sites where the
pair was seeded**, which organises the block's whole rate ladder (AUC 0.866, 0.895 within a nominal level, against 0.587 nominal
and 0.215 for the midpoint reading); two pre-registered controls moved that variable instead of observing it (X182 falls
1.00 → 0.00, X184 rises 0.00 → 1.00, z = +4.638) and are one law because the bodies are 120° apart in the pattern; the crossing
table collapses in the same variable, and the radius-6 cliff survives a site audit; and **the law's sign flips at the largest
bodies**, which reproduces under selection (X187: +0.67 at radius 3, −0.33 at radius 6) with its mechanism **untested**. The
honest negatives are part of this map: heredity through divisions is a notation rather than a ratchet (X161), a merge reappears
in place and is not distinguishable from a blob (X167), and what a blob passes to its daughters is the field's shape rather than
its own history (X170).

**So, in one sentence:** the environment now charges for error, the ruler is being calibrated (P0 unclosed), the learning stages
have not begun, and "signs of life" so far means one predictable law of contact with a honestly drawn boundary — not a claim that
we have seen something alive.

## Running now

**X198 — the fusion share as a function of the surface-to-surface gap** (eight arms, 1152 worlds, claimed before its
pre-registration `reports/2026-11-05-x198-gap-curve-plan.md`): five gaps at radius 4 (8, 9, 10, 11, 12) and three at radius 6
(8, 9, 10), so the switch X196 found with three arms becomes a curve, and the size shift becomes a curve-to-curve comparison at
matched gaps. Registered before the run: the share is monotone in the gap, one neighbouring pair differs by at least 0.4 (which
locates the transition between adjacent gaps, finer than X196 could), the radius-6 curve is not to the right of the radius-4 one
and is higher by at least 0.10 somewhere, the phase still decides the bridge in every arm, and the re-run arms reproduce their
committed values (0.00 / 0.40 / 0.96) within ±0.05.

**Article 030 is finished as v2.0 and stopped at the boundary.** On 05.11 the owner asked whether the continuation after the
published step could be a single article and then confirmed it; the article was enlarged in place from the census-line edition
to **one article for the whole path after the published 029 v2.0** (X156–X197). It now carries the line it continues (the
published DOI), six falsifiable questions instead of four, and its results in nine subsections: the distance the medium uses
and the crossing it makes (the surfaces touch at a median of 1.93 cells, an upper bound with the threshold's lower bound at
0.7, with the crossing one cell wide at 10/10/9 and unmoved by the inflow rate), what a daughter keeps (0.5167 elongation,
0.4811 width) and what it does not (the discrete state is re-drawn; a merge divides after 25 steps against 40), the corridor
at contact (0.479/0.4918/0.4701) with the cliff at its edge (10 of 30 against 3 of 10), the full crossing table (57 cells,
772 runs) whose dispersion is the phase of the medium at the colder body (mean point-biserial −0.552, z −7.807; AUC 0.8656
against 0.5874 nominal and 0.2149 midpoint), the bridge at a fixed supply (slope 6.09, z 5.8) with the opposite sign at a
smaller body, and the unit of observation. Two readings are **withdrawn** in the text and in `docs/eliminations.md`: X168 as
a units artefact and X188 because its observable contains the outcome; §9 lists six places where a report's prose disagrees
with the stored field, with the artifact quoted in each. Eight figures and `tables.json` come from
`scripts/make_article_030_figures.py`; **138 needles** are gated by `scripts/check_article_030_numbers.py --ci` (it now
normalises whitespace, so a needle spans a line break); the PDF is rebuilt; the deposit package is
`_exports/030-gap-switches-fusion-v2.0.zip`; the added numbers are independently reviewed in
`lab/reviews/2026-11-05-030-v20-numbers.md`; the sequence is mapped in `docs/series.md`, and the two queue items that would
have made separate articles of the corridor block and of 029 v2.1 are marked **superseded**. **Nothing has gone outward.**

## Closed on 04.11 — the fusion and heredity block (field line)

Thirteen items, in the order they were run. Each has a report, an aggregate and a row in the README ledger; the section
numbers are in `docs/plan/10d-field-metrics-and-form.md` (10hv–10id).

| what | verdict | where |
|---|---|---|
| **X164** unequal pairs | an (3, 6) pair fuses 5/5 at surface gaps 4, 6 and 8 and 2/5 at 10, so the **size ratio does not move the crossing**; the contact gap rises with the initial gap (1.84 / 2.21 / 2.60 / 4.38) | §10hw, `reports/2026-11-04-x164-asymmetric-pairs.md` |
| **X165** three bodies | a row of three coalesces 5/5, 1/5, 0/5 at gaps 8, 10, 12 — the **square of the pairwise share** (22 %), so the length is **additive per contact** | §10hy, `-x165-three-bodies.md` |
| **X161** discrete traits | division order −0.163 and lifespan 0.101, both **inside** their shuffled-parent nulls, area 0.546 as the control: a digital medium gives a **notation, not a ratchet**; fertility is untestable by construction | §10hz, `-x161-discrete-heredity.md` |
| **X162b** neighbour decay | a neighbour's trait decays with distance over **one body radius**, faster than the trait's own spread | §10hu, `-x162b-neighbour-decay.md` |
| **X166** one-step threshold | the contact gap's residual window shrinks from 1.3 cells to **0.06** while the spread stays at 2.07, so "about two cells" is a **band by right** (1 to 5 across arms), not a sampling artefact | §10hx, `-x166-one-step.md` |
| **X167 / X167b** reversibility | eight fusions re-divide in place (median 25 steps, area ratio 0.867, offset 1.25 cells) but sit **1.12 sd** from a single body's growth phase: reversible, and **not distinguishable from a blob** | §10hv, `-x167-reversibility-exploratory.md`, `-x167b-reversibility.md` |
| **X168** inflow, first attempt | **withdrawn**: the gap was passed as a centre separation, so every arm fused and the "dependence" was an artefact; the withdrawal is kept as a section and the incident is recorded | §10ia, `-x168-inflow-crossing.md`, `docs/incidents.md` §15 |
| **X168c** corrected | the crossing between ten and eleven cells reproduces at `F` = 0.026 / 0.030 / 0.036 | §10ib, `-x168c-inflow-corrected.md` |
| **X168d** ten seeds | gap-11 shares 0/10, 1/10, 3/10; the extreme contrast gives Fisher **p = 0.21**, so the **trend was noise** and the insensitivity is measured rather than power-limited | §10id, `-x168d-gap11.md` |
| **X169** the seam | the pre-registered probe **failed its own control** (the single body reads 0.047 against a 0.9 floor, because a cross-section is a ring); auxiliary and not pre-registered: the merged body is a **dumbbell**, waist ratio 0.36, and the field dies inside 300 steps | §10ic, `-x169-seam.md` |
| **X156 / X162 / X160** | already closed earlier in the block: shape heritable at about half, the local-scale slope inside its null once area is partialled out | see the README ledger |

**One sentence the block earned, corrected at the end of it:** everything the fusion work measured about *size and
geometry* is the **medium's** length rather than the pair's — the same ten-cell crossing for a body twice the size, for an
unequal pair, per contact in a row of three — while the **source** does move it: at gap 10, fifteen seeds per rate, the fusion
share rises 4/15 → 7/15 → 10/15 as the inflow rises (Cochran–Armitage z = 2.20, one-sided p = 0.014) and the field between the
bodies at contact is less filled the stronger the source (0.52 / 0.48 / 0.39 of the body peak). X170 measured that in the last
hour of the block, against the block's own expectation, and it withdrew a sentence this page had already printed. What a blob
passes to its daughters is still the field's shape and not its own history.

**The one question it could not close:** whether a merge keeps the two bodies' structure. Components cannot say (any
elongated blob divides at its ends), and the field probe built to say it needs a world whose pattern outlives the merge.

## Closed on 03.11 — the identity block (field line)

The consequence chain was re-derived from its own definitions, and its vocabulary was repaired four times over. What the
block now says, in the order it was established:

| what | verdict | where |
|---|---|---|
| **X124** coherence audit | **void by its own control**, and the void named two vocabulary contradictions: "rate" differed sixfold between runs, "generation time" appeared as a raw difference and as a share | §10gs, `reports/2026-11-03-x124-coherence-void.md` |
| **X125** definitions | **void by its control**; its diagnosis corrected X124 — the rate gap is a **sample filter** (both generation times ≥ 50 steps), not the weighting | §10gs, `-x125-definitions-void.md` |
| **X125b** filter printed | **void on a pair floor**, and decisive as a diagnostic: with the filter the rate reproduces X113c **to three decimals** (6.056 / 18.96) and the maze's number rests on **638 of 1 195** pairs | §10gs, `-x125b-statistics-void.md` |
| **X125c** ties | contradiction **retired**: 22 % of pairs are ties, and with X93's rule the fractions are **0.526** (0.493–0.557) and **0.388** (0.356–0.419), X93's values inside both intervals | §10gs, `-x125c-ties.md` |
| **X126** third cell | **mixed and informative**: the generation clock is a **gradient** (below-floor share 16 → 30 → 47 %), lineage depth is a **threshold** (+1.479 → +1.416 → **+2.213**, a jump only at percolation), rate accelerates, and end-survival **reverses** (+0.2496 → +0.2984 → +0.1372) | §10gt, `-x126-third-cell.md` |
| **X127** absorption | **void by its dichotomy** (no registered outcome fired) and it found that neither "lethal" nor "homogenising" is the right question | §10gu, `-x127-absorption.md` |
| **X128** kinship | **void by its controls**, and it took X127's magnitude with it: both summed the budget over the **world** while classifying a **local** event | §10gv, `-x128-kinship-void.md` |
| **X128b** local budget | absorption is about **half** of all endings (55.3 / 47.8 / 48.4 %), isolated deaths **31 %** in the lattice, real vanishings **10.5 → 21.7 → 27.4 %** (55 → 302 events), and the absorber changes family: **87 % kin** in the lattice, **62 % strangers** in the maze | §10gv, `-x128b-local.md` |
| **X129** who is next door | the planned distance match **degenerated** (100 % of absorptions are contact events) and the degeneracy is the finding: at identical geometry the one neighbour is a sibling 87.2 % of the time in the lattice and a stranger 62 % in the body — **the lattice segregates lineages, percolation mixes them** | §10gw, `-x129-geometry.md` |
| **X130** re-merge clock | sisters **rarely** merge back (18.4 % of 1 142 pairs, 82 % censored) and **fast** when they do (median 80 steps); birth separation decides it by a factor of two | §10gx, `-x130-remerge.md` |
| **X131** world level | the death fates and the kinship separate habitats at the world level (**vanished +0.178**, **kin −0.443**), the **survival contrast does not** (−0.077, CI −0.166…+0.012): 17 σ at the pair level, unresolved at the world level, power price **30–40 worlds** | §10gy, `-x131-worlds.md` |

**One sentence the block earned:** across three habitats a lineage's ending is usually the loss of its **name**, not of its
cells; the lattice keeps families spatially apart and the percolating body mixes them; and the habitat that maximises
generations is not the one where a lineage survives.

## Open questions this block handed forward

- **X132** (running) — whether thirty worlds resolve the survival contrast; the outcome is pre-declared as
  resolved / below resolution / contradicted.
- **X133** — pool the ten worlds with a world random effect, to see how much of the within-world survival effect survives
  the world-level variance (cheap, no new runs).
- **X134** — what makes the survival contrast swing between 0.09 and 0.30 across seeds; if it is the number of live
  structures at the horizon, that is a state variable to control in every later design.
- **Owner decisions still open:** X54 (12 canonical weights or a recorded absence), v1.7 of article 028, the host's disk
  (≈7.4 GB free — heavy runs stay off), permission for the 514 MB canonical weight and for moving `.venv` (4.8 GB).

## Closed on 01.11 (field line)

| what | verdict | where |
|---|---|---|
| X58-lite grid 128 | **withdrawn**: the code has no `dx`, so 96→128 at `dt = 0.5` changed the domain, not the resolution | §10ed, `reports/2026-11-01-x58-lite-grid128-result.md` |
| X59 amplitude dose | divisions 308 → 79 → 21 at amp 0.5 / 0.25 / 0.1, factor 14.7, 5/5 worlds | §10ef |
| X60 field topology | β₁ excess +9.0 (10/10) at t = 2000, gone by 6000 | §10ea |
| X61l long horizon | the excess fades, no persistent selection | §10eg |
| X62 / X63 / X64 / X65 / X66 / X67 | correlation length, scale sweep, refinement, grid-120 bracket, full grid map, doubled box | §10eh–§10em |
| X68 identity rules | **replicated** on five real worlds: lifetime reversal 5/5 at loose overlap, 4/5 at medium, **5/5 the other way at strict** | §10en, `reports/2026-11-01-x68-identity-replicated.md` |
| X70 size heredity | **real, pair-specific, partial**: 0.42–0.57 over five real worlds, nearest-distance surrogate −0.003, partial 0.545 | §10ep, `reports/2026-11-01-x70-spatial-control-result.md` |
| method | a seed replicates nothing if the world ignores it (β = 0 geometry is seed-independent); gate `check_seed_replication.py` | `docs/design-checks.md` |
| hygiene | board 94/94 closed, CI green, three Linux-only gate defects fixed | `_hourly/log.md` |

## Closed on 02.11 (field line)

| what | verdict | where |
|---|---|---|
| X74 rate | half-life depends on the inflow **non-monotonically**: 1.47 / 0.73 / 1.61 at `F = 0.030 / 0.035 / 0.040`, lag-1 flat at 0.475–0.507 | §10ey |
| X75 edges | inconclusive by the registered rule: 0.037 shallow (0.56), 0.033 out of its control band | §10ez |
| X76 replication | the 0.033 cell is ordinary at ten worlds (ρ₁ 0.447), so the five cells are **two levels** | §10fa |
| X77 patch control | **void as a discriminator**: patch mean predicts a daughter at 0.01 (median patch = 2 structures) — the common-environment reading is excluded *by measurement* | §10fb |
| X78 causal | **void**: the matched-scale arm has one component per world, so the manipulation changed the regime, not the scale | §10fc |
| X78b two scales | imposed second scale shortens memory 1.47 → 1.03 (1.43×) while lag-1 stays 0.498; right direction, third of the band effect | §10fd |
| X79 mix sweep | confounded **by construction**: `Var(G) = (1−w)² + w²` is minimal at `w = 0.5`, so weight and amplitude moved together | §10fe |
| X80 dip test | **void by manipulation reach**: the registered rule fired slope, but measured as a power share all three cells carry a second peak of 0.18–0.34, so the sweep compared three near-identical spectra (the 0/5 two-peak figure was a local-maximum artefact and is withdrawn) | §10ff, `reports/2026-11-02-x80-correction-two-peak.md` |
| the ruler | **half-life is aggregation-dependent**: pooled and per-world median disagree in *sign* on X80 (0.86/1.18/1.25 against 1.04/0.52/1.16), and the band contrast is 2.01×/2.58× pooled but 1.37×/1.91× per-world median; at `F = 0.033` only 7 of 10 worlds are fittable | §10ff, claims 296–298 |
| X84 angular re-read | **one period, two symmetries**: X71's "12.0 vs 8.73 cells" are the stripe axis and the checkerboard forcing diagonal landing in one radial bin; `q'` = 5–9 (10.7–19.2 cells) in all 35 forced worlds and never 11, while the symmetry `s` rises 0.38 → 0.92 with inflow (ρ = 0.687). X71b's flatness is the forcing's, X71c's "band" is a smooth crossover | §10fg, claims 298–299 |
| X82 reach | **void by its own control**: the radial share of a single-scale world is 0.304 where the plan required below 0.15, because the forcing line sits inside the window. The angular readout on 25 fields: `q'` = 6–9 in every cell (a second line at 16× the power moves no period), and an in-band second line breaks the symmetry lock (0.603 → 0.324) while an off-band one does not (0.710) | §10fh |
| X85 symmetry × memory | **void by its control**, and that is the finding: `--sample-every` decides how often trait mutations fire, so X71 (1000) and X85 (50) are different regimes and the borrowed band was invalid (verified: same seed, different logging, fields differ by 0.365). Within the 50-step regime `s` = 0.40 / 0.67 / 0.87 and memory has no partial correlation with it (0.00) | §10fi, `docs/design-checks.md` |
| X86 symmetry curve | **placed**: `s` = 0.421 / 0.674 / 0.848 at 0.025 / 0.030 / 0.035, twenty worlds each, SE 0.025–0.036, control fired (gap 0.427); the 0.030 cell reproduces X85's 0.671 to 0.003. The secondary heredity readout does **not exist** without `--split-new-uid` (0 pairs, 4–7 uids) | §10fj, claims 301–302 |
| X87 memory × symmetry | **answered, no**: twenty worlds per inflow give within-cell ρ(ρ₁, `s`) = −0.05 / −0.26 / −0.21 and a partial correlation controlling inflow of −0.10; orientation does not carry the memory. Only a negative association stronger than ~0.3 is excluded | §10fk, claims 303–304 |
| X88 percolating arm | **the U is real**: per-world half-life 2.08 at 0.040 and 1.60 at 0.045 against 1.07 at 0.035; at 0.050 heredity is **undefined** (one component in 20/20 worlds, six pairs). The direction of §10fa is restored, its values are not (inside 1.07–1.16, outside 1.82–2.08) | §10fl, claims 305–306 |
| X89 lineage edge | **graded disappearance**: pairs per world 31.8 / 13.0 / 6.0 / 2.0 / 1.0 / 0.3 across 0.045…0.050, factor 2.4 per half-step, no 10× step; every world is one component with β₁ > 0 from 0.046 and still divides, so what fades is the rate | §10fm, claim 307 |
| X90 trickle | **void by its own control** (median 0 events at 0.050 over 12 000 steps), and the descriptive shape is a **transient, not a rate**: at 0.048 the count does not grow with the horizon, at 0.049 it doubles, at 0.050 it is zero. Statement for the text: above 0.049 the medium stops dividing *in practice* | §10fn |
| X98 threshold | **void, and the reason is a category error**: `q'` and `s` come from the continuous field and have no threshold, so masking it produced four different statistics; the memory numbers *do* depend on the cut and were left untested | §10fr |
| X99 cut dependence | the half-life map is **definition-bound**: 0.77 / 1.16 / 2.26 at cuts 0.15 / 0.20 / 0.25 for `F = 0.030`, 1.84 / 2.08 / 0.69 for 0.040 — the ordering between inflows **reverses** at 0.25, so every half-life is quoted with its estimator and its cut | §10fs, claim 313 |
| X100 core vs skirt | heredity lives in the **skirt**: 0.531 / 0.384 (threshold area) against 0.176 / 0.058 (basin at half the local maximum) on the same pairs | §10ft, claim 314 |
| X101 ladder | three definitions, one monotone ladder: 0.531 / 0.384 → 0.300 / 0.174 → 0.176 / 0.058; heredity is strongest where the definition is an excursion set | §10fu, claim 315 |
| X102 specificity | the **gap** is definition-bound too: 0.312 / 0.215 → 0.017 / −0.010, and the degeneracy check clears it (mother in the daughter's basin 0.398 / 0.187 against a stranger's 0.132 / 0.081) | §10fv, claim 316 |
| X103–X103d position | two voids (a coverage denominator that counted 622 unloggable pairs; a selection control that caught the basin losing the 54 boundary mothers, whose daughters are the large ones), then the answer: distance predicts nothing in the lattice (−0.008) and −0.367 in the maze (10/10 worlds), the mother's area keeps its coefficient (0.570 / 0.552), and stranger peaks carry the opposite sign — **maternal**, plus an unasked-for **crowding** term (+0.358, 10/10) in the lattice | §10fw |
| X105 dense logging | **both registered verdicts fired**: structural loss 0.353 → 0.088 at 0.040, maternal decay −0.329 (10/10) and crowding +0.367 (10/10) robust — and the maze heredity was **underestimated**, 0.384 → **0.480** | §10fy, claim 317 |
| X106 room | the crowding coordinate is a property of the **place**, not the lineage: it predicts the mother's own area (+0.397) better than her daughter's (+0.322), and nothing in the maze (0.114 / −0.038) | §10fx, claim 318 |
| X107 shared room | **heredity is not a shared-room effect**: controlling the mother's room costs 0.064 of 0.519, both rooms 0.094; room-adjusted values 0.455 / 0.395 now travel beside the raw ones | §10fx, claim 319 |

**The headline changed.** "Multistability between two wavelengths at `F = 0.035`" is withdrawn: the medium has one preferred scale
(~12 cells, the same with and without forcing) and a symmetry coordinate that follows the inflow. The environment can set the
**orientation** of the pattern; it cannot move the **scale**. Everything X78b–X82 did by imposing a second wavelength was moving the
forcing line, which is why the weights did so little — the field's morphology never followed.

**And the heredity picture is now a map, not a number.** Memory is a function of place: 1.82 / 1.16 / 1.07 / 2.08 / 1.60 divisions at
0.025 / 0.030 / 0.035 / 0.040 / 0.045 (U-shaped, minimum at the band's edge), the medium stops dividing in practice above 0.049, and the
one coordinate the environment controls — orientation — carries none of it. For the life question the two conditions are now measurable
separately: a medium must **hold** a state longer than a generation and **produce** generations at all.


Note on X80's three numbers: they were measured on cells whose *realised* spectra differ by less than the noise (shares 0.27–0.31,
0.18–0.23, 0.27–0.34), so they are a statement about the composite at three weights, not a graded trend.

The estimator note is the one with teeth: every half-life we published (X74, X76, X78b, X79) is **pooled**, and pooling is a
choice that was never declared. The direction of the band survives it; the size does not.


## Deliberately not doing in this block

- **X163 (a Lamarckian rule).** It is the one item left in the queue and it is the wrong next experiment: the trait `s` is
  read from the field (`comp_s` is the mean of the trait channel over a component's cells), so "copy the parent's trait to the
  daughter" is not a manipulation of the world but a rewrite of the readout. Making it real needs a rule that writes into the
  daughter's *cells*, and that is a `world/` edit with its own anchor — not a thing to bolt on at the end of a block.
- **The seam in the pond regime.** It is the right follow-up to X169, and it needs a world whose pattern outlives the merge;
  the field line's pattern is gone in 300 steps. Designing that world is a block of its own.
- **Any outward step.** Nothing was published, no tag moved, no deposit changed. The publication decisions stay where they
  were.

## The last hour: a review that changed a claim

An independent reviewer recomputed X168d from its sixty raw runs and found the table exact but the inference wrong, plus a
script bug (`difference` subtracted flow values instead of shares, which made the "trend is real" branch unreachable for any
data), a power claim of 80 % where the exact figure is 15 %, and an ordered-trend test at p = 0.052 rather than the extreme
pair's p = 0.21. Then X170, run for a different purpose, produced fifteen seeds per rate at gap 10 and showed the crossing
**does** move with the source. Both corrections are in the reports, the claims table (with a retraction row rather than a
deletion), the article and the README.

The general lesson, for the next block: **a negative at the cell where the effect is marginal is not a negative about the
effect.** X168d was correctly powered to say "nothing here" and was read as "nothing anywhere"; the cost was one sentence in
the paper, corrected within the hour by a reviewer and a by-product of an unrelated run. Keep the reviewer in the loop before
a sentence that strong is written, not after.

## Waiting for the owner — three items, all small

1. **Which deposit goes out first.** 029 v2.1 (written and checked, adds X161–X170) and 030 v2.0 (one article for everything
   after the published 029 v2.0, package built) are both prepared and neither has gone anywhere. The choice is the owner's:
   deposit 029 v2.1 as a new version of the same record `23933440` and then 030 as a new record, or let 030 carry the path
   alone. Licence defaults to CC BY 4.0; the author list is settled (Ilya Vladimirov). Cost once approved: minutes.
1. **X54, canonical weights:** the snapshot is honest now (`ready 1 / missing 11`, `weights_tracked: false`), but the choice
   remains: (a) restore the 12 `nca_final.pt` from Zenodo `10.5281/zenodo.23654174` (6.47 GB), or (b) record the local
   absence in `docs/deposit.md` and drop the 12-file requirement. Option (b) costs 15 minutes and unblocks the retention
   policy; option (a) is only needed if E02b is to be reproduced locally.
2. **v1.7 of article 028:** v1.6 was **published** on 31.10 at 23:45 (DOI `10.5281/zenodo.23844978`), so "inserts before
   upload" no longer exists as a category. Two things remain: the published files still call themselves v1.5.1 and link
   `23839898` (a two-line header fix), and the two prepared inserts (the count is a count of *small* components; lifetimes
   belong to the trait channel) would go into v1.7. Publication is outward-facing, so it is the owner's call; ~60 minutes.

## Queued compute, not waiting on anyone

- **the mixedness channel that actually reaches** (the open problem after X82): inflow modulation admits an imposed second scale
  only as a shoulder of about a third, so "two preferred scales of comparable strength" is not reachable through `hetero_G`. The
  candidates are (a) impose the second scale in the initial condition rather than in the inflow, (b) a second species with its own
  diffusion length, (c) a spatially varying `F` (X52's design) instead of a temporal-spectral one. Decide after X82's transfer
  function is in hand; do not build a heredity design on a channel with a 0.3 ceiling.
- **X58 at grid 192** (the real refinement): `Du = 0.64`, `Dv = 0.32`, `dt = 0.375` (stability `dt·Du = 0.24 ≤ 0.25`),
  16 000 steps, 10 runs, ~2 GPU-hours. Criterion: peak position at 12 units.
- **X57 stationarity:** one 30 000-unit arm at `dt = 1.0`, 10 seeds, ~2 GPU-hours.
- **X31 equivalence:** the rule is implemented in `claim_comparator.py`; the 60-seed series is missing, ~1 GPU-hour.
- **X29:** `scripts/field_eas.py` (Flow-Lenia meter) has never been run; the `x37_sel`/`x37_null` data are on disk. No GPU.
- **X35:** six published claim rows sit at `наблюдение` only because nobody matched their numbers to aggregates that already
  exist (`v8_matrix.json`, `frequency_start_control.json`, five `w2bud_*` manifests). One hour, no GPU.
- **X3:** the claims gate checks that an artifact exists, not that its value matches; add the expected-value column.
- **X69:** 15-seed dose confirmation, registered, paused (`reports/2026-11-01-x69-dose-15-seeds-plan.md`).

## No longer waiting (stale entries removed)

- **A (`freq_dep > 0`)** — the quota arm was approved, run and closed negative on 27.10 (§10bf: lineages with data 4.0 → 5.0 →
  4.0 against a target of ≥12, sign of the price flipped); the price magnitude was closed by §10bg/§10bh. Nothing waits.
- **Preprint v1.1/v1.2** — v1.2 has been live since 28.10 (`10.5281/zenodo.23733719`); only the optional arXiv endorsement
  step remains, and `_hourly/grants/ИНСТРУКЦИЯ-ОТПРАВКА.md` is out of date rather than blocking.
- **Provenance gaps** — of the 93 references to lost `_hourly/` artifacts, **66 exist one directory up** (the gate scans
  `repo/_hourly` only), 13 can be re-pointed to committed aggregates, 3 are filename drift, 11 are gone for good.

## Deliberately not doing (unchanged)

- New pilots on the same price construction (14 manoeuvres gave the answer: at most 9 lineages).
- A third explanation of the price magnitude (two were tested and withdrawn).
- Rewriting old series for cosmetics; re-running insensitive tests under new names.
- Editing `world/` or `config.py` while a series runs.
- Publishing anything outward without the owner's explicit "ok".

## Lessons that still bind (pointers)

| # | class | rule |
|---|---|---|
| 7 | a series taken across four code commits | the indicator is `git_code_commit`, not `git_dirty`; `check_series_homogeneity.py` |
| 8 | `print` into a closed pipe killed a run | the artifact is written **before** printing; the fix is checked by deliberately breaking it |
| 9 | a series mixed by parameters invisible in `config` | parameters come from the preregistration, not from the previous script |
| 10 | 01.11 | a seed is replication only if it changes the world — `docs/design-checks.md` |

## How to check the state

```bash
python scripts/lab.py validate      # contract
python scripts/claims_lint.py       # claims matrix: basis kind, assumptions, artifacts
make verify                         # everything, with per-step time budgets
python scripts/lab_health.py --full --github   # single entry point: gates, CI, queues, series, disk
```

---

# История (не переписывается)

## Что закрыто за ночь 26→27.10

1. **Единица размножения — четыре конструкции** (§4i, §10az/§10ba): колония **0/10**, пара «своей» метки **2/10**, пара
   «любых» меток **1/10**, клетка **10/10**. В первых трёх линия с данными одна, поэтому они помечены **«не оценивается»**,
   а не «отбора нет». Утверждение сузилось до **«ровно одна клетка»**; объяснение «порог в родстве внутри единицы»
   опровергнуто нашими же данными.
2. **Цена признака** (§4i, §10bd): знак устойчив (**8/8**, p = 0.0039), величина **не определена** (медиана −0.478, ДИ
   [−0.797, −0.177], порог −0.3 внутри). Причина — **ограничение конструкции**: 14 маневров дают максимум **9 линий**
   против нужных ≥12 (доминирующая линия занимает 69–90 %). Серия не запускалась — это записано как свойство мира.
3. **Отклик закрыт двумя величинами** (§10ax): независимая от `w` величина даёт медиану **0.018** (5/10), `ρ(признак, w)` —
   **+0.518** (8/10), знак совпадает в **3/10** ⇒ кажущийся отклик — свойство определения `w`.
4. **Наследование среды закрыто механизмом** (§4j, §10be): пересъёмка 20 прогонов **одним `git_code_commit`**
   (`248e01d`), фильтр «свободная компонента ≥15»: `legacy > adjacency_exact` в **5/10**, медиана **−0.0092**, p = 0.62.
   Остаток +0.12 → +0.014 → **−0.0092** исчез; место занимает тот, у кого больше живых 4-соседей (0.744 → 0.881).
   **Уточнение:** память среды при этом есть — избыток живёт 2–4 поколения; опровергнуто наследование **по линии**, а не
   память среды вообще.
5. **Перенос вне тел** (§4j.1, §10bb/§10bc): `k = 1 > k = 2` в **10/10** (p = 0.001), `k = 2` против `k = 8` — **6/10**,
   величина 1.765 против 12–50. Объяснение «геометрия усиливает отбор» проверено и **снято**.
6. **Препринт опубликован** (Zenodo, v1.0 `23669738`, v1.1 `23694918`, v1.2 `23733719`); статья 028 v1.6 —
   `23844978`.

## Уроки ночи (разборы — `docs/incidents.md` §7–9, правило — `AGENTS.md` §3c)

| # | класс | правило |
|---|---|---|
| 7 | серия снята на четырёх коммитах кода | индикатор — `git_code_commit`, а не `git_dirty`; гейт `check_series_homogeneity.py` + реестр `lab/homogeneity.json` |
| 8 | `print` в закрытый пайп убивал прогон (и PowerShell `*>>` — тоже пайп) | артефакт пишется **до** печати, `_safe_print` везде, фикс проверять **намеренной поломкой** |
| 9 | серия смешана по параметрам, невидимым в `config` | параметры берутся из **пре-регистрации исполнителя**, а не из прошлого скрипта; сверка на одном сиде до серии |

Плюс два собственных промаха ведущего, записанных явно: предсказание «+0.005…+0.02» для просторной зоны **не
подтвердилось** (−0.0092), потому что опиралось на отозванную серию; и 17 прогонов были запущены скопированным старым
`POND_ARGS` (три флага отсутствовали, а в `config` они не видны).

## Красное, которое оставлено осознанно (26.10)

- **Гейт «замечания библиотеки»: 1 замечание new висит больше дня.** Библиотекарь написал **58 новых разделов**
  (`library/answers.md`), из них прочитаны и разобраны три ключевых (§37, §38, §39). `library_inbox --ack` отказывается
  закрывать без `--force`, а ставить `--force`, не прочитав 55 разделов, — ровно то «зелёное, которое врёт», с чем мы
  воюем. *(На 01.11 доска 94/94 закрыта; строка оставлена как история правила.)*

## 29.10 — вечер: итог дня

**Закрыто:** E1, E1b (критерий индивидуации — пруд не проходит), E2 (абляция объекта — вывод устоял с границей), E3
(гистерезиса нет), E4 (связь даёт скорость, не прирост), E6a (критерий был неустойчив к сетке), E6b (пассивная примесь не
наследуется), X5 (вердикт E1 не зависит от фона).

**Не выжили три вывода:** преимущество инвазии, гистерезис, оптимум чувствительности.

**Два правила метода:** сравнивать на срезе 600 (CV 0.3), контраст против локального кольца.

**Осторожно:** срез 300 хаотичен (CV до 0.80). Любое число, взятое до 600 шагов, публиковать только с CV.
## Constraint (03.11, 00:45) — the host disk is nearly full, and it is not the repository

Free space on C: fell from 2.4 GB to **1.2 GB** during the evening and is still falling, while the repository's own footprint is stable: 0.89 GB of
derived archives were deleted tonight (field .npy archives and dense logs whose compact projections are in git; recorded in lab/retention.json),
and no large file inside the workspace has been written in the last twenty minutes. The remaining consumers are the virtualenv (4.8 GB), the
canonical E02b weight (514 MB) and tracked artifacts — none of them mine to remove.

Consequences while this holds: **no heavy series** (the policy's own < 10 GB rule), analysis-only work continues, and commits stay small. If the
free space keeps dropping, the host itself needs attention — the lab can free at most a few hundred more megabytes from its own derived files.

**Disk:** 13.0 GB free on 04.11 22:00 - above the 10 GB floor for heavy runs, but the field line's five
sweeps this evening wrote their slices locally (all gitignored, ~40 MB each). Nothing needs owner attention yet; the next heavy series
should not start below 10 GB.
