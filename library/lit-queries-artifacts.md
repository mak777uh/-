# Query: what has already been done about simulation artifacts mistaken for biology

Written 31.10.2026 for passing to external models or search engines. The purpose is **not** to collect impressive
references but to find out what the field has already established, so that we do not re-derive it — and to see the
elephant: whether this is a recognised category of failure with known countermeasures, or a scattering of anecdotes.

---

## The request (paste this)

> Find **real, published** work about cases where a **simulation artifact was mistaken for a biological or evolutionary
> result**. I need to know what the field has already established and what countermeasures are documented.
>
> For every item return exactly these fields:
> 1. full citation, with **DOI**;
> 2. **year** and venue;
> 3. one sentence: what was mistaken for what (artifact → interpretation);
> 4. what the authors propose as a **check** against it;
> 5. link to a **free full text** if one exists (publisher page, arXiv, PMC, Zenodo).
>
> **Rules.** If you cannot give a DOI, say "not found" for that item — do not fill the gap with a plausible title. Do
> not infer a paper from a blog post. Do not include 2025–2026 items unless you can give their DOI. Prefer work that
> names the mechanism (numerical, coding, statistical, conceptual) over work that merely complains.

---

## Search queries, by subgenre

Each line can be pasted into Crossref, OpenAlex, Google Scholar or arXiv. Exact phrases in quotes work best.

**A. Simulator and code exploits**

```
"Surprising Creativity of Digital Evolution"
evolutionary algorithm "exploited" bug simulator
"reward hacking" OR "fitness loophole" evolutionary computation
"reward tampering" evolutionary computation
digital evolution "unintended solutions"
```

**B. Numerical artifacts — the closest to our own case**

```
"rounding error" "evolutionary" simulation fitness
"numerical artifact" reaction-diffusion pattern
"non-platonic" computation cellular automata
"discretization artifact" pattern formation simulation
"floating point" "artificial life" artifact
"integration step" "Gray-Scott" pattern artifact
```

**C. Statistical and methodological artifacts**

```
"pseudo-replication" simulation ecology
"methodological artifact" individual-based model
"simulation artifact" "statistical" ecology
"reproducibility" "artificial life" simulation
"we reanalysed" simulation result reversed
```

**D. Conceptual critiques of the field**

```
"artificial life" critique "not alive"
"open-ended evolution" criticism measure
"digital evolution" "surprising" robustness instruction set
"simulated molecular evolution" "computer-generated artifacts"
"are artificial mutation biases unnatural"
"free-floating model" simulation critique
```

**E. Countermeasures — what people actually do about it**

```
"code review" simulation science "sanity check"
"independent reimplementation" simulation result
"surrogate data" test simulation artifact
"negative control" simulation artifact
"ablation" simulator artifact
```

---

## How to check the answers yourself, without any plugin

Every model answer must be verified against a register. These endpoints answer over plain HTTP and need no key:

```
Crossref  (journals, conferences):
https://api.crossref.org/works?query.bibliographic=<TITLE>&rows=3&select=DOI,title,container-title,issued,author

DataCite  (Zenodo, Dryad, repositories):
https://api.datacite.org/dois?page[size]=3&query=<TITLE>

OpenAlex  (abstract + free full-text link):
https://api.openalex.org/works/https://doi.org/<DOI>?select=title,publication_year,cited_by_count,best_oa_location,abstract_inverted_index
```

In this repository the same check is one command:

```
python scripts/verify_references.py --query "<title>"
python scripts/literature_harvest.py --queries library/lit-queries-artifacts.txt --rows 10 --out docs/lit-artifacts.json
```

**Warning from our own experience (31.10):** a 19-item catalogue produced this way contained **six references that do
not exist** — every one of them dated 2026 — and **two real papers described wrongly**. Existence is half the check;
the abstract is the other half.

---

## What we specifically want to learn

Answer these five questions, each with citations or with "no known work":

1. **Is "artifact mistaken for adaptation" a named category** with a review, or only anecdotes?
2. **Which numerical artifacts are documented** for continuous media specifically — time step, discretisation,
   rounding, boundary conditions — and how were they detected?
3. **What countermeasures are standard**, and which of them are cheap enough for a small lab: independent
   reimplementation, negative controls, surrogate data, code audit, parameter-perturbation tests?
4. **Has anyone shown a published ALife or evolutionary result to be an artifact** after the fact? What happened to the
   claim?
5. **Is there a known case where the artifact and the real effect were separated** — and how?

## What we will do with the answers

| if the answer is | we |
|---|---|
| a review exists | cite it and stop re-deriving the taxonomy |
| countermeasures are documented | adopt the cheap ones as gates, and say which we do not |
| a published result was overturned | read how, and copy the procedure that caught it |
| nothing exists for continuous media | our percolation/lifetime finding gains a methodological framing, and we say so carefully |
