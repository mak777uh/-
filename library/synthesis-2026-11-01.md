# The elephant after one night: what the field line now says about conditions for life

1 November 2026, 08:40. Written between two runs, after four campaigns in one night (20 + 30 + 20 + 10 + 15 + 5 runs).
This is not a report of results — each of those has its own page — but the shape they make together, which changed twice
during the night and is now stable enough to state.

---

## 1. What was actually established

| finding | evidence | status |
|---|---|---|
| Heterogeneous inflow **delays wavelength selection at 96 cells** | homogeneous selects q = 8, λ = 12 units (45 % of low-q power); heterogeneous stays broadband on 96, entropy 2.19–2.25 | **withdrawn as a claim about the medium**: at a correctly scaled 144 grid the heterogeneous arm selects too (normalised entropy 0.61 against 0.90 on 96) — see §10ej |
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
