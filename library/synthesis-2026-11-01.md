# The elephant after one night: what the field line now says about conditions for life

1 November 2026, 08:40. Written between two runs, after four campaigns in one night (20 + 30 + 20 + 10 + 15 + 5 runs).
This is not a report of results — each of those has its own page — but the shape they make together, which changed twice
during the night and is now stable enough to state.

---

## 1. What was actually established

| finding | evidence | status |
|---|---|---|
| Heterogeneous inflow **delays wavelength selection at 96 cells** | homogeneous selects q = 8, λ = 12 units (45 % of low-q power); heterogeneous stays broadband on 96, entropy 2.19–2.25 | **holds on peak position across four grids** (96, 108, 120, 144 at `dt = 0.5`): the homogeneous arm peaks at 12 units wherever it patterns; the heterogeneous arm never does — it concentrates on the box scale. An earlier withdrawal based on concentration was itself withdrawn — see §10el |
| The advantage in component count is an **advantage in small, short-lived pieces** | contrast +3.57 falls to +1.36 at 32 cells, +0.07 at 128 cells | free re-analysis, 10 seeds |
| Heterogeneity produces a **transient perforated web** | β₁ +9.0 (10/10 seeds), survives matched occupancy (+5.5, 10/10) and every threshold tested | transient only; gone by t = 6000 |
| **Transmission follows geometry** | divisions 308 → 79 → 21 as inflow amplitude falls 0.5 → 0.25 → 0.1 (14.7×, 5/5 seeds), spectra sharpening in the same order | dose-response, five seeds |
| **Selection is easy, coexistence environmental** | survival channel drifts +0.48 (10/10) and +0.84 (9/10); without frequency dependence 9/10 seeds fixate into one structure | 10 seeds, artifacts in git |
| Heritability we measured is **mechanical** | Spearman(divisions, r) = +0.79; more division, higher fidelity | 24 runs |
| Niches **amplify** selection rather than enable it | drift +0.204 without niches against +0.835 with | one series, secondary endpoint |
| The seed reaches the field **only through the trait channel** | `beta = 0` arms give byte-identical component series across ten seeds | structural property |

Three of these were corrections of our own claims made hours earlier (the spectral reading, the heritability story, the
"environment decides diversity" sentence). That is the normal rate of error in this line, and the reason every claim above
names its window, its ruler and its seed count.

## 2. The sentence the night produced

> **In this medium, heterogeneity buys turnover at the cost of organisation.** A field with a heterogeneous inflow never
> selects a pattern wavelength; it fragments into small pieces, those pieces divide fifteen times more often than in a
> smooth world, and division is the only channel through which composition is inherited. So the same condition that
> destroys spatial regularity multiplies the events in which lineages could exist — and those lineages are, so far,
> copied rather than selected.

That is a statement about a digital medium, not about a counter, and it is the first one in this project that speaks to
the actual question: what does an environment have to be like for something life-like to have a foothold?

## 3. What it implies for "conditions for life"

Reading the results together, a candidate condition needs three things, and the medium supplies them unevenly:

| requirement | does heterogeneous inflow supply it? | evidence |
|---|---|---|
| **turnover** — structures appear and disappear fast enough for lineages to matter | **yes, strongly** | 308 divisions against 17.5; 18× |
| **heritable variation** — something is transmitted | **yes, but mechanically** | r = 0.97, imposed by the copy rule, not emergent |
| **coexistence** — diversity persists instead of one winner | **weakly** | frequency dependence keeps 2.5 structures against a control's 36 |
| durability of organisation | **no** | durable structures 1.3 against 1.2; large components indistinguishable |

So heterogeneity is a **turnover generator, not an organisation generator**. If life-like organisation requires structures
that persist long enough to accumulate change, an environment that only fragments is hostile to it — the very condition
that creates the events removes the objects that could carry a history.

That is a negative result of the useful kind: it says which environmental knob to turn next (something that slows turnover
without removing variation), and it says the trait channel alone will not do it.

## 4. What we now know about our own instruments

Three lessons that outlive the numbers:

1. **Every effect we have is a property of a window.** The count contrast, the hole excess, the wavelength selection — all
   are transients that decay. A claim without a window is a claim about an average that hides its own history.
2. **Two kinds of numerical dependence.** Dependence on the *scheme* (dt, grid, boundary conditions) must be declared as
   part of the regime. Dependence on the *ruler* (threshold, size floor, cadence, identity rule) must be shown as a curve.
   We spent a week learning to separate them; the distinction now appears in every report.
3. **A control with no seed variance is one sample.** The field world has no seed-dependent start, so `beta = 0` arms are
   deterministic. Stating this turned three "10 seeds" claims into "one field, ten trait realisations", which is what they
   always were.

## 5. What is genuinely open

- **Does the late concentration become selection?** Running now: 24 000 steps of the same world, four field snapshots.
- **Can turnover be slowed without losing variation?** The obvious knob is the inflow correlation length; the dose
  experiment says amplitude controls turnover monotonically, so a length sweep is the natural next axis.
- **Is there any channel where a trait pays without a matching cost?** Growth had a cost, survival did not; what else is
  there in this world — dispersal, adhesion, decay threshold — is an open design question.
- **Does anything here transfer to the pond line?** Both lines now say diversity comes from the environment; neither has
  shown a case where it comes from the organisms.

---

*Sources: the nine reports of 1 November in `reports/`, the plan sections §10ea–§10ef, and the aggregates under
`morphogenesis/experiments/E09_pond/`. Every number above is reproducible from a file in this repository — that was not
true yesterday for half of them.*

## Correction, 11:00 — the spectral claim is about the grid

The refinement run of 11:00 (X64) changed one row of the table above and, with it, the shape of the argument. The
heterogeneous world does not *prevent* wavelength selection; at 96 cells the pattern has only twelve cells per period and
the inflow modulation, which has the same period, destroys it. At 144 cells — same physical domain, diffusion rescaled
correctly — the heterogeneous arm selects a mode as the homogeneous one does.

This is the **non-Platonic** effect Davis describes, now measured in our own world: a pattern that exists at one
discretisation and not at another. The practical consequence is a rule for every spectral sentence in this project:
**name the grid**, or the sentence is about the instrument.

What the night's sentence becomes after this: heterogeneity buys turnover at the cost of organisation — the *turnover*
half is a count and is unaffected (X59's dose-response stands); the *organisation* half is grid-dependent, and the honest
version says so.

**And the topological half at the refined grid (11:15).** The same saved fields give β₁ at 144: the heterogeneous arm has
more loops at every snapshot (median excess +13 at physical time 2000, +12 at 6000) but the sign holds in only 4/5 and 3/5
seeds, against 10/10 at 96, and the occupancy control has not been run there. So the web is a hypothesis supported by two
grids, not a result — and the table row above should be read with that in mind.

## Final correction of the day, 13:10 — twice withdrawn, now restored

The spectral claim was withdrawn at 11:00 and restored at 13:10, and the reason matters more than the outcome: both the
original claim and its withdrawal were judged by **concentration** (share, entropy) while the sentence was always about
**position** (does the peak sit at the medium's wavelength). Once position is the readout, the picture is sharp and stable
across four grids: the homogeneous world picks 12 units wherever it patterns, the heterogeneous world never does.

Two lessons, both about instruments rather than physics:

1. **A summary number is not the claim.** Share and entropy compress a spectrum into one value and can make two very
   different spectra look alike.
2. **The right fix was a criterion, not a rerun.** X66 cost twenty runs, but the map was already there; what was missing was
   the quantity to read off it.

The row above is the corrected form. Everything else in this page — turnover, heritability, coexistence — is untouched by
this sequence.

## Last word on the spectrum, 13:50 — tested against two domain sizes

X67 doubled the domain with the cell size fixed. The homogeneous pattern stayed at twelve units (q = 16), and the
heterogeneous peak stayed at q = 1 — it moved with the box. So the heterogeneous concentration is **the domain**, not a
structure: that world has less organisation, not a different kind of it.

The spectral claim has now been tested against five grids (96, 108, 120, 144, 192 cells in the domain-size run) and two
domain sizes (96 and 192 units), with the time step held fixed where it matters. Its final form:

> Heterogeneous inflow suppresses the medium's twelve-unit pattern. What concentration the heterogeneous field shows is
> the box itself, so it is not alternative organisation but the absence of it.

## Where to go next, and what is deliberately not being done now

The day closed three questions and left three, and the order below is a judgement about cost rather than importance.

**1. Turnover, with a readout that can carry it.** X59's dose-response is the strongest evidence in the line (divisions
308 → 79 → 21 as amplitude falls, 5/5 seeds), and X63 showed why the correlation-length profile could not be resolved: the
count is heavy-tailed, with a tenfold spread between seeds inside one arm. The next experiment is not another scale sweep
but **more seeds at fewer points** — three scales, fifteen to twenty seeds each — with divisions per component per 1000
steps as the readout. That is about two hours of GPU and it would turn a hypothesis into a curve.

**2. Lifetimes and identity.** The weakest link in the published line has not moved all day: the median lifetimes (57
against 4046 steps) rest on the overlap rule, and the tracking literature we read says that rule is a convention, not a
standard. The fix was specified this morning and never executed: one run saving masks, then lifetimes under overlap
0.3 / 0.5 / 0.7, plus a persistence-based definition on the same fields. Until it runs, the lifetime contrast should be
quoted with its rule attached, exactly as the v1.6 text does.

**3. The publication decision.** The v1.6 package is built, checksummed and sitting on disk; the two-sentence insert about
small components is written and costed. That decision is the owner's and it has been open since the small hours.

**What is not being done, and why.** No further grid work on the spectrum: it has been tested against five resolutions and
two domain sizes and the answer stopped changing. No more reading: the corpus is at the point where the next useful text is
an implementation, not an argument. And no new "quick" run at the end of a long day — the two claims that went wrong today
both went wrong through a rushed criterion, not through a rushed measurement.

One rule from today is worth keeping above the rest: **a claim names the quantity it is about.** Twice this line judged a
sentence about *position* by a number that measured *concentration*, and once it judged a sentence about the medium by a
number that measured the box. Each time the measurement was fine and the reading was not.

## Correction, 14:35 — the lifetimes belong to the trait channel, not to the field

X68 varied the overlap cutoff that defines identity, and its own leak check killed the first design within one seed: the
rule cannot be varied in isolation, because composition is **carried per component, inherited with the identity, and paid
for in growth**. Change who inherits and you change the field.

In the neutral world where the rule is separable, the ordering reverses: heterogeneous components live **longer** (5999,
5044, 2607 steps at cutoffs 0.3, 0.5, 0.7) than homogeneous ones (4030, 1565, 1565) — the opposite of the published 57
against 4046, which was measured with the feedback on.

So the sentence is not "structures in a heterogeneous field are short-lived". It is: **a trait carried along lineages and
paying for its carrier's growth fragments the field into short-lived pieces**. The contrast is a property of the
two-channel world, and the field geometry alone produces the other sign.

This is the third claim today to change its object rather than its number, and the pattern is consistent: what looks like a
property of the medium keeps turning out to be a property of the measurement channel attached to it.

## Added 17:30 — the size-heredity question, and a defect the repair found

The afternoon's last experiment asked whether the medium itself carries heredity of form, with no copying rule imposed.
It does, but weakly, and testing it properly cost more than expected.

- **Heredity is real and belongs to the pair, not the place.** Over five genuinely different worlds a daughter's peak
  area correlates with her own parent's at 0.42–0.57 (mean 0.499), each above its own pairing null. The control the
  external answers demanded — a non-parent companion at the same distance — gives −0.003 against the observed 0.582, and
  the partial correlation controlling distance, crowding and two local field statistics is 0.545. So the parent is not
  just a proxy for a rich neighbourhood.
- **It is partial.** Slope 0.38–0.57: roughly half the parent's deviation is erased within one division. That is
  "limited heredity", not a lineage mechanism — enough for a memory of form one generation deep, not enough for
  cumulative evolution.
- **Richness modulates it instead of causing it.** Heredity is 0.18 in the driest third of the field and 0.63 in the
  richest, while the local environment does not predict the area itself. A rich neighbourhood lets the pair similarity
  show; it does not manufacture it.
- **The defect that made the first numbers wrong.** In a world without feedback (`beta = 0`) the seed does not move the
  geometry at all: the start is a fixed blob and the seed only feeds the trait channel. Five "seeds" were one universe
  copied five times, so the morning's 0.334 was a single draw and every "5/5 seeds" sentence about geometry was one
  observation. Fixed with `--init-jitter` (seed-dependent start position and radius, inert when off) and gated by
  `check_seed_replication.py`, which now measures per family whether the seeds actually produced different worlds. Blast
  radius: exactly the `beta = 0` arms; the amplitude dose, correlation length, scale sweep, grid map and transmission ratio
  all have genuinely distinct worlds behind them.

The general lesson, which is the day's most transferable finding: **replication is a property of the world, not of the
seed count.** A world that ignores its seed cannot be replicated by more seeds, and a null calibrated on copies is too
tight by roughly the square root of the number of copies.
