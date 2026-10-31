# Catalogue of simulator artifacts: what actually exists

Received 31.10.2026 as a list of 19 documented cases where simulation artifacts were mistaken for biology or
adaptation. Prepared by a language model. **The list was checked against the publisher registries** — Crossref for
journals and conferences, DataCite for repositories — with `scripts/verify_references.py`, because the web-search
plugin was unavailable (authentication error) while the machine's own network worked fine.

Result: **6 of the 12 checkable items exist** (several with wrong years), **6 do not exist in any register**. That
split is itself the finding: a catalogue about artifacts mistaken for results contained artifacts mistaken for
references.

---

## Verified in the registries — citable after reading the paper

| # | item | what the registry says | the list claimed |
|---|---|---|---|
| 1, 2, 3, 10 | simulator exploits, force overflow, Q*bert, fitness loopholes | **Lehman et al.**, *The Surprising Creativity of Digital Evolution*, **Artificial Life 26(2), 2020**, DOI `10.1162/artl_a_00319`; earlier version: ALife 2018, DOI `10.1162/isal_a_00016` | correct in substance; the anecdotes are recognisable from this work |
| 5 | reality gap in evolutionary robotics | *The Influence of Robot Traits and Evolutionary Dynamics on the Reality Gap*, IEEE TCDS, DOI `10.1109/tcds.2021.3112236`, **2023** | "IEEE 2021" — **year wrong** |
| 6 | evolutionary constraints under climate change | *Evolutionary constraints mediate extinction risk under climate change*, **Ecology Letters 2023**, DOI `10.1111/ele.14173` | "2024" — **year wrong**; and the title is not about "undeclared methodological artifacts in performance functions" |
| 7 | mutation-operator bias | *Are Artificial Mutation Biases Unnatural?*, LNCS, **1999**, DOI `10.1007/3-540-48304-7_11` | "Bristol" — it is a book chapter, and it is **27 years old** |
| 9 | rounding error in physical simulation changing fitness | *Dealing with rounding error problems in evolutionary physical simulation*, **Artificial Life and Robotics 2012**, DOI `10.1007/s10015-012-0038-0` | **exact** |
| 11 | reward tampering | *Reward tampering and evolutionary computation: a study of concrete AI-safety problems*, **GPEM 2023**, DOI `10.1007/s10710-023-09456-0` | **exact** |
| 19 | "simulated molecular evolution" as artifacts | *"Simulated molecular evolution" or computer-generated artifacts?*, **Biophysical Journal 1994**, DOI `10.1016/s0006-3495(94)80695-2` | **exact** |

## Not found in any register — do not cite

| # | item | status |
|---|---|---|
| 4 | "non-Platonic gliders", Davis 2024, *Innovations in Machine Intelligence* | **not found.** Only generic automata literature. The *phenomenon* (patterns depending on discretisation) is real; this citation is not. |
| 8 | "From Roundoff to Heredity", Zenodo 2026 | **not found** in DataCite. |
| 12 | "Tripping Over the Past", Hall of Fame, 2026 | **not found.** |
| 13 | Tierra parasites attributed to **PNAS 2026** | **not found**, and wrong by thirty years: Tierra's parasites are Ray's 1990s work. |
| 14 | Bullock, "free-floating models" | **not found** as described. |
| 18 | *Digital Evolution Exhibits Surprising Robustness…* | **not found.** |
| 15–17 | monoculture penalty, interpolation artifact, mass-conservation clamp | **community self-reports, not publications** — the list says so, and they must stay that way |

**The pattern in the six misses:** all are recent (2026), all have plausible-sounding titles and venues, and none
exists. That is the signature of invented references, and it is precisely the failure this lab's rules exist to
prevent.

---

## What this changes

**1. Nothing about our numbers.** The article stands on its own artifacts.

**2. One citation is safe and valuable.** Lehman et al. (2020, DOI `10.1162/artl_a_00319`) is the standard reference
for "the simulator is part of the result", and it is verified. If we place our seven retractions in a genre, this is
the work to cite.

**3. Two things to state in the article regardless**, both prompted by the *phenomenon* behind item 4 (not its
citation):

- our **integrator, time step, grid and boundary conditions** — the article gives the equations but not the scheme
  (`laplacian` by four neighbours, `dt = 1.0`, `Du = 0.16`, `Dv = 0.08`, periodic boundaries, grid 96/128). In a
  continuous automaton a pattern can depend on these, so they belong in the methods;
- that the percolation result is **threshold-dependent by construction** — we say it, but now with a reason to say it
  louder.

**4. It is the best argument yet for the design gate.** Items 1–3, 7, 8, 11 are all cases where the manipulated
variable was not what the author thought. That is the same failure we hit five times in one day, and the same one
`check_design.py` now refuses.

**5. A method, not a complaint.** "Search is unavailable" was not the end of the matter: Crossref and DataCite answer
direct HTTP queries, and `scripts/verify_references.py` turns reference checking into a command. Six invented
references were caught in one run.

---

## Status

- material is in `library/`, not in any article;
- queue item `X55_verify_artifact_catalogue` tracks reading the six verified papers and deciding what, if anything,
  they change;
- the six verified DOIs may be cited **after** the paper itself is read, not before.
