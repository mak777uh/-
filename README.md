# Project Morphogenesis

A computational bench that asks **under what conditions an organisation maintains itself**, rather than
what shape it takes. "Living" here is a process: holding a boundary costs energy, an error ends the
trajectory, luck is passed to the next generation. The centre of the work is therefore **the environment
and its parameters**, not the pattern.

> Focus as of 2026-10-23: the morphology line (`struct_2` and shape classes) is **stopped**. It produced
> three transferable lessons — a class is a phase of a trajectory, the model has a measurable signature,
> a shape is held by the price of maintaining it — and is closed with that. This is not a loss: in that
> world there was no metabolism, so there was nothing to test "life" with. History and results are not
> rewritten: [`docs/path.md`](docs/path.md),
> [`reports/2026-10-23-window-and-topology.md`](reports/2026-10-23-window-and-topology.md). The current
> programme is [`docs/plan-alive.md`](docs/plan-alive.md).

The project has been through five turns, all preserved as a path: **goal** (the ring did not become an
attractor) → **map** (a census of what the system generates by itself) → **replication** (the class does
not reproduce on new seeds) → **phase** (the class depends on the training horizon) → **environment** (we
look for the conditions of self-maintenance, not for a shape).

## What we look for

Not "does a pattern appear", but: which parameters of the environment make a self-maintaining
organisation possible at all, how expensive the boundary is, and what kills the trajectory. A negative
result is a result here, and the lab keeps it as one.

## How the bench is built

The core is `nca_core.py` (perception layer, stress, alive mask taken from the state before the update,
morphogens); `topology.py` and `topo_proxy.py` hold the invariants and a symmetric Chamfer distance;
`train.py` implements truncated BPTT, a state pool, NaN/OOM guards and atomic checkpoints. Censuses and
replication live in `e02b_morphospace.py` and `e02c_replication.py`; `cognition/` is an observation tool,
not a scientific question.

Determinism rules (import order, local generators, a pre-run gate) are in [`AGENTS.md`](AGENTS.md). The
single source of truth for the mechanics is
[`docs/spec/MORPHOGENESIS_v5.6_Rev11.md`](docs/spec/MORPHOGENESIS_v5.6_Rev11.md).

## The claims rule (why this repository is unusual)

A manuscript may only say what the evidence licenses, and the evidence is tracked mechanically:

- [`manuscript/CLAIMS.md`](manuscript/CLAIMS.md) — a claims matrix: **no row, no claim**. Each row carries
  a status (confirmed / refuted / open / forbidden), a closed report or artifact as proof, the section
  it belongs to, and the **maximum admissible wording**. A stronger wording counts as an error even if it
  sounds more scientific;
- results are never rewritten silently: a changed result adds a new row with a date and a link
  ([`manuscript/CHANGELOG.md`](manuscript/CHANGELOG.md));
- [`docs/formal-method.md`](docs/formal-method.md) — rules for the third instrument. Every formal
  hypothesis has an id (`F-<area>-<n>`), a formulation written **before** the check together with "what
  would refute it", a link to the code it protects, and a Python analogue that tests the same property
  on concrete numbers (or a stated reason why no such test exists). If Lean is not installed, CI reports
  a **skip**, never a pass.

## Manuscript

[`manuscript/`](manuscript/README.md) — the future publication, its claims matrix, changelog and
supplement. An English abstract draft is in
[`manuscript/ABSTRACT.md`](manuscript/ABSTRACT.md).

## Experiment journal

[`reports/`](reports/README.md) holds experiment cards; [`articles/`](articles/README.md) long texts;
[`library/`](library/README.md) the publication index, the NCA lineage and notes. The machine side is
[`AGENTS.md`](AGENTS.md), [`lab/registry.json`](lab/registry.json), [`lab/state.json`](lab/state.json),
[`lab/runs/`](lab/runs/).

**If the README and the registry disagree, the registry wins.** The README is corrected, never bent to
match.

## Repository structure

In short: `morphogenesis/` — bench and artifacts; `lab/` — the machine circuit; `docs/` — contract and
specifications; `reports/` and `articles/` — texts; `library/` — sources. The full tree is in
[`docs/README.md`](docs/README.md).

## Two entry points

- **Human:** `reports/` (experiment cards), `articles/` (long texts), `library/` (publication index,
  NCA lineage, notes), `manuscript/` (the publication).
- **Machine:** `AGENTS.md`, `lab/registry.json`, `lab/state.json`, `lab/runs/`.

## Install

Python 3.11+ (verified on 3.13.11); for training, a CUDA build of torch.

```bash
git clone https://github.com/mak777uh/-.git morphogenesis-repo
cd morphogenesis-repo
python -m venv .venv
.venv/Scripts/python.exe -m pip install -U pip
# CPU (tests and diagnostics):
.venv/Scripts/python.exe -m pip install -r requirements.txt
# GPU (training) — RTX 3070 8 GB is the reference card:
.venv/Scripts/python.exe -m pip install -r requirements-gpu.txt
```

## Quick start

```bash
# from morphogenesis/
python -m pytest -q
# from the repository root
python lab.py validate
```

## Tests and CI

500+ tests run on CPU in CI, plus a canary run of the world (determinism by seed, counter consistency)
and a nightly full pass. GitHub Actions is the third machine of the laboratory, next to the local CPU and
GPU: it has no GPU, so training and long series run locally, while CI catches platform differences. See
[`docs/ci-resources.md`](docs/ci-resources.md) for what runs where and why.

## Journal rules

One experiment, one card; a verdict is written only when there is an artifact; "open" stays open until
evidence appears; a failed hypothesis is recorded with the same care as a successful one. The full rules
are in [`lab/README.md`](lab/README.md).

## Licence

See [`LICENSE`](LICENSE).
