# Shape heredity in Gray–Scott blobs: what the literature supports (2026-11-04)

Scope: one literature note for X156; no simulations, no other file touched. Only corpus documents with status
`read` / `partial` are cited. `verify_references.py` has no DOI mode (its `--help` offers `--query`), so it was
used as a title search; each DOI was then confirmed at `api.crossref.org/works/{DOI}`.

## Question

A Gray–Scott blob in a dish with uneven supply splits, merges and dies. The lab's earlier series showed that
the only heritable number was one the analysis software copied from parent to daughter (slope 0.98, residual
equal to the mutation parameter; with copying noise off, no variance). X156 asks a different question: is a
trait computed from the field itself — elongation and minor-axis width from second moments of the blob's
pixels — inherited across division, and does a daughter relax towards a typical shape as it ages? "Inherited"
must be separated from size selection and from determination by the local environment.

## What the literature already says
1. **Pearson 1993**, *Complex Patterns in a Simple System*, Science 261:189–192,
   [10.1126/science.261.5118.189](https://doi.org/10.1126/science.261.5118.189). `[abstract]`
   Shows spots growing until a critical size, then dividing in two; in an overcrowded region all spots decay
   into the uniform background. **Bearing:** supports a size threshold (size selection) and density-dependent
   death; contradicts continuous inheritance of size, since the daughter's size is set by the division
   threshold, not copied. Silent on elongation and minor-axis width.
2. **Chen & Ward 2011**, *The Stability and Dynamics of Localized Spot Patterns in the Two-Dimensional
   Gray–Scott Model*, SIAM J. Appl. Dyn. Syst. 10:582–666,
   [10.1137/09077357X](https://doi.org/10.1137/09077357X). `[abstract]`
   Constructs quasi-equilibrium multi-spot patterns with slow collective coordinates and identifies three
   instability mechanisms: self-replication, oscillation and annihilation. **Bearing:** a spot has a
   quasi-equilibrium profile and discrete instability modes, so "typical shape" is meaningful; silent on
   parent–daughter morphological correlation.
3. **Burke & Knobloch 2006**, *Localized states in the generalized Swift–Hohenberg equation*, Phys. Rev. E
   73:056211, [10.1103/PhysRevE.73.056211](https://doi.org/10.1103/PhysRevE.73.056211). `[abstract]`
   Shows many stable localized states organised by homoclinic snaking, tracks how the solution changes as it
   grows in extent, determines stability, and simulates evolution after a state loses stability.
   **Bearing:** supports selection of discrete widths (a weak "attractor of size"), not a measured relaxation
   time and not inheritance.
4. **Gandhi, Zelnik & Knobloch 2018**, *Spatially localized structures in the Gray–Scott model*, Phil.
   Trans. R. Soc. A 376:20170375, [10.1098/rsta.2017.0375](https://doi.org/10.1098/rsta.2017.0375). `[abstract]`
   Finds localized Gray–Scott states from a subcritical Turing instability, from folds of periodic Turing
   states, and from the uniform-state fold; the branches interconnect. **Bearing:** supports multistability
   of localized structures in Gray–Scott itself; one-dimensional, and silent on heredity.
5. **Purwins, Bödeker & Amiranashvili 2010**, *Dissipative solitons*, Adv. Phys. 59:485–701,
   [10.1080/00018732.2010.498228](https://doi.org/10.1080/00018732.2010.498228). `[abstract]`
   Reviews particle-like localized structures that are robust under interaction and are alternatively
   generated or annihilated as a whole. **Bearing:** supports fusion/annihilation as discrete events rather
   than gradual blending; the abstract gives no characteristic merging distance.
6. **Bödeker, Liehr, Frank, Friedrich & Purwins 2004**, *Measuring the interaction law of dissipative
   solitons*, New J. Phys. 6:62, [10.1088/1367-2630/6/1/062](https://doi.org/10.1088/1367-2630/6/1/062).
   `[abstract]` Measures the interaction law from experimental time series; its sign alternates with
   distance, matching oscillatory decaying tails, and transient molecules and clusters form. **Bearing:**
   supports distance-dependent attraction/repulsion with preferred separations; no single merging distance
   for Gray–Scott spots.
7. **Takagi & Kaneko 2001**, *Differentiation and replication of spots in a reaction-diffusion system with
   many chemicals*, Europhys. Lett. 56:145–151,
   [10.1209/epl/i2001-00500-3](https://doi.org/10.1209/epl/i2001-00500-3). `[abstract]`
   Extends Gray–Scott with many chemicals and classifies replication of homogeneous spots, replication of
   oscillatory spots, and differentiation from multipotent spots into spots with different fixed-point
   dynamics. **Bearing:** the closest precedent for a heritable "trait" here, but the trait is
   chemical/dynamical type, not geometry; no morphological measurements are reported.
8. **Segré, Ben-Eli & Lancet 2000**, *Compositional genomes: Prebiotic information transfer in mutually
   catalytic noncovalent assemblies*, PNAS 97:4112–4117,
   [10.1073/pnas.97.8.4112](https://doi.org/10.1073/pnas.97.8.4112). `[abstract]`
   Models mutually catalytic molecular assemblies and shows growth, splitting, homeostasis and
   compositionally biased information transfer without a template replicator. **Bearing:** the clearest
   conceptual precedent for heredity without replicators (compositional inheritance); chemical, not
   geometric, and silent on spots.
9. **Spector, Harrington & Gaffney 2025**, *Persistent Homology Classifies Parameter Dependence of Patterns in
   Turing Systems*, Bull. Math. Biol. 88,
   [10.1007/s11538-025-01552-9](https://doi.org/10.1007/s11538-025-01552-9). `[corpus: read]`
   Derives CIMA parameter intervals where stripe and spot solutions are stable, and clusters pattern topology
   across the Turing space. **Bearing:** supports the null that shape class is selected by local parameters,
   not history; silent on inheritance.
10. **Woolley 2022**, *Boundary Conditions Cause Different Generic Bifurcation Structures in Turing Systems*,
    Bull. Math. Biol. 84:101, [10.1007/s11538-022-01055-x](https://doi.org/10.1007/s11538-022-01055-x).
    `[corpus: partial]` Shows the Turing bifurcation is a pitchfork under zero-flux but generically
    transcritical under fixed boundary conditions. **Bearing:** supports the environment/boundary explanation
    and warns that a "typical shape" may be a boundary artefact.
11. **Chalfoun et al. 2016**, *Lineage mapper: A versatile cell and particle tracker*, Sci. Rep. 6:36984,
    [10.1038/srep36984](https://doi.org/10.1038/srep36984). `[corpus: read]` Tracks divisions and fusions;
    its mitosis indicators include mother-cell roundness, daughter size similarity and daughter aspect-ratio
    similarity, and daughter cells are stated to have similar size and shape. **Bearing:** morphological
    parent–daughter correlation is measurable and treated as a biological prior in cells; it is a detection
    rule, not a measured heritability, and does not establish the effect for reaction–diffusion spots.
12. **Jaqaman et al. 2008**, *Robust single-particle tracking in live-cell time-lapse sequences*, Nat.
    Methods 5:695–702, [10.1038/nmeth.1237](https://doi.org/10.1038/nmeth.1237). `[corpus: read]` Treats
    merge and split as explicit event classes with distance/overlap costs in a two-stage linker.
    **Bearing:** supplies the event ontology for division and fusion; silent on a physical merge distance.

## What is genuinely open

- No source measures parent–daughter **elongation** or **minor-axis** correlation for Gray–Scott or CIMA
  spots; the nearest case is cell lineage tracking, not a pattern-forming system. No source measures
  **relaxation of a daughter's shape with age** — snaking gives stable widths, not a relaxation time.
- No source states a **characteristic merging distance** for Gray–Scott spots: crowding-induced decay
  (Pearson) and distance-dependent soliton interaction (Bödeker) are different mechanisms, not one claim.
- Literal "shape memory" (a stored geometric set point) was not found; the literature has multistability,
  thresholds and parameter selection instead. Heredity without replicators is argued for **composition**
  (Segré) and, weakly, for **dynamical type** (Takagi), not for a geometric trait of a blob.

## What our experiment would add

- The first measurement of morphological heritability across divisions here: regress daughter elongation and
  minor-axis width on the parent, controlling for parent size, daughter age and local supply; the earlier
  software-trait result (slope 0.98; residual = mutation parameter) is the benchmark, not a literature claim.
- A three-way discrimination: local determination (no partial correlation); inherited shape with noise
  (nonzero slope, residual variance below total); attractor (correlation decays with daughter age).
- A distribution of merge/annihilation event distances, to decide whether death is density-driven or pairwise.
- Two nulls the literature makes necessary: shuffled parent–daughter pairing, and a size-matched null,
  because symmetric splitting creates geometric correlation with no transfer of information.

## What would falsify the "shape is inherited" reading

- Partial parent–daughter correlation indistinguishable from zero after controlling for parent size, daughter
  age and local supply; or a daughter elongation distribution independent of the parent (slope 0).
- Correlation decaying with daughter age on a timescale shorter than the division interval — shape is then an
  attractor, not an inherited trait.
- Shape variance fully accounted for by local parameters or boundary conditions (Spector; Woolley).
- The observed correlation reproduced by shuffled pairing or by the geometry of symmetric splitting alone.

## Sources checked and rejected

- **Lee, McCormick, Pearson & Swinney 1994**, *Experimental observation of self-replicating spots in a
  reaction–diffusion system*, Nature 369:215–218,
  [10.1038/369215a0](https://doi.org/10.1038/369215a0) — metadata verified; full text behind an
  identity/paywall redirect, no abstract retrievable. **Rejected for content**: metadata only.
- **Reynolds, Pearson & Ponce-Dawson 1994**, *Dynamics of self-replicating patterns in reaction diffusion
  systems*, Phys. Rev. Lett. 72:2797–2800,
  [10.1103/PhysRevLett.72.2797](https://doi.org/10.1103/PhysRevLett.72.2797) — verified; 1D analog only.
- **Munafo 2014**, arXiv:1501.01990 — preprint, not peer-reviewed, not in the corpus; skipped.
  **Pearson 2026**, arXiv:2610.27235, on Markov blankets around Gray–Scott spots — preprint; skipped.
- **Nánay 2009**, *Replication without replicators*, Synthese,
  [10.1007/s11229-009-9702-x](https://doi.org/10.1007/s11229-009-9702-x) — DOI verified, no accessible
  abstract or text; not cited.
- "Memory of shape / hysteresis in Turing patterns" returned only shape-memory alloys and materials papers,
  no reaction–diffusion source. Reported as a null result, not as evidence.

## Search record

- Corpus (`lit_index.py --search`): "spot splitting", "self-replication spots", "relaxation spot size",
  "attractor spot radius", "elongation" (0 hits), "second moment shape", "fusion coalescence", "merge
  distance", "shape inheritance", "morphological correlation parent daughter", "Gray-Scott", "Pearson",
  "annihilation" (0 hits), "snaking localized", "Turing", "mother daughter", "size inheritance",
  "compositional", "self-replicat", "snapshot attractor", "spot". Manifest: 15 documents, 9 `read`,
  6 `partial`, 0 `unread`.
- Crossref (`verify_references.py --query`, then `api.crossref.org/works/{DOI}`): the title queries above plus
  "Dissipative solitons Purwins interaction", "compositional inheritance mutually catalytic assemblies",
  "localized states generalized Swift-Hohenberg", "stable localized spots Gray-Scott model radius",
  "self-replication spots CIMA reaction", "daughter spot size parent spot reaction-diffusion", "relaxation of
  spot shape reaction-diffusion". Net: 12 cited sources verified (metadata + abstract or corpus text);
  1 further DOI verified but rejected.
