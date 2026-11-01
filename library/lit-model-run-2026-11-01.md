# Harvest from the model run of 1 November: what is verified and what is not

Four model answers came back to our seven questions. This page records what I checked and what survived, **before** any of
it enters the corpus as a citation. The pattern of 31 October repeated itself at smaller scale: several DOIs resolved,
but to the **wrong paper**.

Every claim below was checked with `scripts/verify_references.py` against Crossref or DataCite, and the title in the
answer was compared with the title the DOI actually returns. A DOI that resolves is not a DOI that is correct.

---

## Corrected — the answer gave a DOI for a different paper

| claimed | what the DOI actually returns | correct identifier |
|---|---|---|
| Edelsbrunner, Letscher, Zomorodian, "Topological persistence and simplification", `10.1007/s004540010011` | *New Bounds on Crossing Numbers* | **`10.1007/s00454-002-2885-2`** (Discrete Comput Geom 28, 2002) |
| Chen & Ward, "Stability and dynamics of localized spot patterns in 2-D Gray–Scott", `10.1137/100801986` | *Convergence Analysis of a Galerkin Boundary Element Method* | **`10.1137/09077357x`** (SIAM J Appl Dyn Syst 10, 2011) |
| Reynolds, Pearson, Ponce-Dawson, "Local feedback instability and stationary inhomogeneous patterns", `10.1103/PhysRevLett.78.2489` | *Multiarmed Spirals in Excitable Media* | closest real work: **`10.1103/physreve.56.185`**, *Self-replicating spots in reaction-diffusion systems* (PRE 56, 1997) — the "local feedback instability" title was not found at all |
| Taylor et al., OEE workshop, `10.1162/ARTL_a_00205` | *Emergence of Signal-Based Self-Replication without Manual Design* | **`10.1162/artl_a_00291`**, *An Overview of Open-Ended Evolution* (Artificial Life, 2019) |

## Not found — do not cite

| claimed | status |
|---|---|
| Maška et al., segmentation benchmark, `10.1109/TIP.2014.2371994` | **404** at Crossref; title search returns unrelated work |
| Lai & Tél, *Transient Chaos*, `10.1007/978-3-642-10275-2` | **404** |
| Grimm et al., ODD update, `10.1016/j.ecolmodel.2020.109305` | **404**; the ODD second update is `10.18564/jasss.4259` (JASSS 23(2), 2020) |
| Munafò's U-Skate World | no DOI — a personal web resource, cited only as such |

## Verified and worth having

| work | DOI | why it matters to us |
|---|---|---|
| Ulman et al. 2017, *An objective comparison of cell-tracking algorithms* | `10.1038/nmeth.4473` | the culture of "what counts as a validated tracking rule" — Q4 |
| Jaqaman et al. 2008, *Robust single-particle tracking in live-cell time-lapse sequences* | `10.1038/nmeth.1237` | global association with explicit gap-closing, splits and merges — Q4 |
| Chalfoun et al. 2016, *Lineage mapper* | `10.1038/srep36984` | overlap-based association plus lineage events — Q4 |
| Edelsbrunner et al. 2002 (corrected) | `10.1007/s00454-002-2885-2` | persistence as threshold-free identity — Q3/Q4 |
| Cohen-Steiner, Edelsbrunner, Harer 2006, *Stability of persistence diagrams* | `10.1007/s00454-006-1276-5` | why persistence is stable and a fixed threshold is not |
| Peyré & Cuturi 2019, *Computational optimal transport* | `10.1561/2200000073` | matching masses across time, handles merges continuously |
| LeVeque 2007, *Finite difference methods* | `10.1137/1.9780898717839` | modified-equation reasoning for the `dt` effect — Q2 |
| McGough & Riley 2004, *Pattern formation in the Gray–Scott model* | `10.1016/S1468-1218(03)00020-8` | Gray–Scott numerics as such |
| Hastings et al. 2018, *Transient phenomena in ecology* | `10.1126/science.aat6412` | transient advantage as a legitimate object — Q1 |
| Morozov et al. 2024, *Long-living transients* | `10.1016/j.plrev.2024.11.004` | review of transient regimes — Q1 |
| Dorosz & Pleimling 2009 | `10.1103/PhysRevE.80.061114` | steady-state and transient properties in reaction–diffusion |
| Spector et al. 2025, *Persistent homology classifies parameter dependence in Turing systems* | `10.1007/s11538-025-01552-9` | topological classification of patterns — Q3/Q7 |
| Carlsson 2009, *Topology and data* | `10.1090/S0273-0979-09-01249-X` | TDA beyond counts |
| Muratov & Osipov 2001 | `10.1007/s100510170129` | spot replication and competition in Gray–Scott — Q7 |
| Cross & Hohenberg 1993 | `10.1103/RevModPhys.65.851` | pattern selection, transients, asymptotic states |
| Bedau et al. 2000 | `10.1162/106454600300103683` | the fourteen problems |
| Bedau 2024, *Kuhnian lessons* | `10.1162/artl_a_00428` | the field still wants shared exemplars — Q5 |
| Channon et al. 2024 editorial | `10.1162/artl_e_00445` | OEE special issue — Q5 |
| Hintze 2019 | `10.1162/artl_a_00289` | open-endedness as a definition artefact |
| Klügl 2008, validation for ABM | `10.1145/1363686.1363696` | V&V vocabulary adapted to agents — Q6 |
| Sargent 2013, verification and validation | `10.1057/jos.2012.20` | the general simulation vocabulary — Q6 |
| Grimm et al. 2020, ODD second update (corrected) | `10.18564/jasss.4259` | the description protocol we should borrow — Q6 |

## What the four answers agree on, and what we do about it

All four independently say the same three things, which is worth more than any single citation:

1. **No standard estimator exists** for "transient advantage in pattern count". We keep reporting both estimators and say
   that no convention exists — which is now a checked statement, not a guess.
2. **A fixed-threshold component count is a legitimate conditional observable, not a robust one.** The framing to use is
   `${β_0}$ of the excursion set at a declared threshold` — well defined, threshold-dependent. Novelty, if any, is in the
   experiment, not in noticing the fragility.
3. **Q4 is the weak link** and the fix is concrete: event-aware tracking, threshold and cadence sensitivity, lifetimes in
   physical time, and a persistence-based companion measure.

Two disagreements worth noting. One answer insists the `dt` effect is likely mostly a **sampling artefact** because our
snapshot cadence changes with `dt`; another argues it is a **modified-equation** effect (explicit Euler has effective
growth rate `ln(1+dt·σ)/dt`). These are distinguishable by experiment, and both are cheap to test on data we already
have: resample the `dt = 0.5` trajectory to every second snapshot and recompute.

## Second pass, 03:20: the eight that were left unverified

The first pass verified 22 and left the rest unchecked. Eight more were checked against Crossref by title, and the
claimed DOI compared with what the search actually returns — the check that caught four wrong DOIs the first time.

| work | claimed | verdict |
|---|---|---|
| *A theory of pattern formation for reaction–diffusion systems on temporal networks* | `10.1098/rspa.2020.0753` | **correct** (Proc. R. Soc. A, 2021) |
| *Numerical study of pattern formation in an extended Gray–Scott model* | `10.1016/j.cnsns.2010.09.002` | **correct** (Commun. Nonlinear Sci. Numer. Simul., 2011) |
| *Pattern Formation Beyond Turing: Physical Principles of Mass-Conserving Reaction–Diffusion Systems* | `10.1146/annurev-biophys-030822-031638` | **correct** (Annu. Rev. Biophys., 2026) |
| *Transients: the key to long-term ecological …* | `10.1016/j.tree.2003.09.007` | **DOI correct, title wrong in the answer**: the paper is "…long-term ecological **understanding**?", not "change" |
| *Computational Optimal Transport* | `10.1561/2200000073` | **correct**, and the search shows a second edition under `10.1561/9781680835519` (2019) — cite the one intended |
| *Finite Difference Methods for ODEs and PDEs* (LeVeque) | `10.1137/1.9780898717839` | **correct** (SIAM, 2007) |
| *Verifying and validating simulation models* (Sargent) | `10.1145/256562.256572` | **correct** (Winter Simulation Conference, 1996) |
| *Topological data analysis of zebrafish patterns* (McGuirl, Volkening & Sandstede) | `10.1073/pnas.1917763117` | **correct** (PNAS, 2020) |

Two are worth more than a line:

- **McGuirl et al. 2020** is the precedent that was missing from our corpus: topological summaries (persistence) used
  to classify *biological* pigment patterns, not a toy model. It is the strongest available answer to "has anyone
  actually done this on real patterns?", and it strengthens the case for a persistence companion to our counts.
- **Hastings 2004**, correctly cited, is the ecological statement that transients can dominate an observation window —
  the same argument as our §4.5, made twenty years earlier in another field, and therefore a citation rather than a
  discovery.

## Status

- 22 references verified in the first pass (4 corrected, 3 not found, 1 without a DOI by nature); **8 more verified in the
  second pass**, one with a wrong title and one with a second edition to disambiguate.
- Full texts added to the corpus where open: Jaqaman, Chalfoun, Spector; Woolley read in part.
- Reading proceeds one at a time, in the order set by `library/lit-reading-list.md`; the corpus currently has **no unread
  texts**.
