# Three threads checked: heredity of dividing structures, Betti labels, periodic boundaries

1 November 2026, 04:00. Three targeted searches, run because each one could change what we do next rather than decorate a
paragraph. All DOIs below were checked against Crossref by title; the ones that resolved are marked, and one claim is
marked unverified because its title does not resolve.

The short answer: **two threads are settled as "build our own, on a published basis", one thread is not settled and
turns out to be more fragile than it looked at 03:20 — because our own heritability measurement is partly mechanical.**

---

## 1. Heredity and lineages of dividing structures

**Searched:** self-replicating spots heredity, spot-tail inheritance, lineage selection in spatially extended systems,
compositional heredity in compartments.

**Found.**

| work | status | what it actually establishes |
|---|---|---|
| Froese, Virgo & Ikegami (2014), *Motility at the Origin of Life: Its Characterization and a Model*, Artificial Life 20(1):55 | DOI **verified**: `10.1162/artl_a_00096` | Reaction–diffusion spots with a "tail" pass the tail to daughters at division; tailed spots out-persist plain ones and the population changes. **Heritable difference and selection are already demonstrated qualitatively in this model family.** |
| Chen & Ward (2011), *Stability and dynamics of localized spot patterns in 2D Gray–Scott* | verified earlier: `10.1137/09077357x` | Spot self-replication, oscillation and annihilation as a dynamical repertoire. Division itself is old news. |
| *Spatiotemporal chaos of self-replicating spots* (PRL 99, 2007) | DOI **verified**: `10.1103/physrevlett.99.214102` | Births, divisions and deaths of spots treated as a branching process. Statistics of the population, not of lineages. |
| Matsubara et al. (2022), *Robustness of compositional heredity to growth and division dynamics of prebiotic compartments* | **not found** by title at Crossref — **do not cite** | As reported to us: compositional fidelity survives only if the interval between divisions stays below a critical threshold. That would be the closest quantitative prior art. Until it resolves, it is a lead, not a citation. |

**Verdict.** Spot heredity and spot selection exist qualitatively; a lineage-resolved **quantitative** heritability
measured across a fragmentation regime was not found. So the thread is not a repeat — but it is also not yet ours, and
the reason is in §4.

## 2. Betti numbers as morphology labels

**Searched:** Betti numbers / persistent homology classifying spots, stripes and labyrinths.

**Found.** There is no canonical convention "β₁ > 0 ⇒ stripes". The closest published basis is Spector, Harrington &
Gaffney (2025), `10.1007/s11538-025-01552-9`, who cluster CIMA and Schnakenberg solutions by 2-Wasserstein distance
between barcodes in degrees 0 and 1 and recover regions that they *label* spots / stripes / labyrinths. Their labels are
assigned after clustering, not derived from β₁. Joe (2016, thesis) does persistence landscapes on Gray–Scott snapshots,
which is the only Gray–Scott-specific precedent we have.

**Decision.** Use β₀–β₁ as operational features, adopt the spots/stripes/labyrinths vocabulary so the result is readable
by others, and state explicitly that a single stripe on a torus can have β₁ ≥ 1 by periodicity — so β₁ alone cannot name
the morphology. The naming rule is ours and is declared, not borrowed.

## 3. Periodic boundaries

**Searched:** periodic boundary conditions and the Turing bifurcation structure.

**Found.** Woolley (2022), `10.1007/s11538-022-01055-x`: generic pitchfork under zero-flux, generic transcritical under
Dirichlet — for two-species systems in 1D. Nothing establishes the corresponding statement for periodic boundaries; the
paper itself only notes that some Neumann solutions can be continued periodically under extra symmetry conditions.

**Decision.** Methods sentence: we use periodic boundaries (a torus); the Neumann/Dirichlet result does not transfer; we
do not claim a bifurcation type and report the observed modal structure. This is a boundary of applicability, stated, not
a gap we fill.

## 4. What the search forced us to notice about our own number

Before writing any of this up we checked the x23 artifact for the relation the compartment literature predicts:
**does more frequent division cost fidelity?** Across 24 runs with both quantities recorded, Spearman(splits,
`inheritability_r`) = **+0.79** — the sign is the *opposite* of a dilution trade-off. Within the heterogeneous arm the
correlation is flat (0.970 → 0.975 between the low- and high-division halves); within the homogeneous arm it rises
(0.733 → 0.829).

That is not a discovery about heredity. It is a property of the instrument: in `field_track.py` a daughter **copies** the
parent's composition with a fixed mutation, so fidelity is set by the copy rule, and frequent division *prevents drift*
by re-copying before a lineage wanders. The measured `r` therefore cannot be read as an emergent fidelity of the medium.

**Consequence for the plan.** The "fragmentation manufactures lineages" claim must be restated before it is tested:
what the world manufactures is **copy events**, not (yet) selectable variation. The experiment that would make it a
claim is the one already specified as `S1`: does the mean composition drift relative to the `eps = 0` control, with
`I_obs > I_null(95 %)`. Until that runs, the honest sentence is: *heterogeneous inflow multiplies divisions and
parent–child events; whether that supports selection is untested, and the measured heritability is largely mechanical.*

---

*Sources: [`lit-model-run-2026-11-01.md`](lit-model-run-2026-11-01.md) for the verified reference list, [`corpus/`](corpus/)
for full texts. The mechanical-heritability check is reproducible with the x23 artifacts and the numbers above.*
