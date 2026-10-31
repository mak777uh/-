# Two free checks before the upload: cadence and size

1 November 2026, 00:20. Four independent literature reviews of the seven questions agreed that the strongest
objections to our heterogeneity result are (a) the `dt = 0.5` run was sampled more often per unit of physical time, and
(b) "more components" may mean "more debris". Both objections are answerable from snapshots already on disk, without a
single new run. They have been answered, and one of the answers changes how the headline number should be read.

Nothing here is a new experiment. Both are re-analyses of `morphogenesis/experiments/L1_field/` and both are
reproducible with one command each.

---

## 1. Cadence does not explain the `dt` gap

`scripts/cadence_match.py` → `l1_field_cadence.json`.

The `dt = 0.5` run was saved every 500 steps (250 time units, 25 snapshots); the `dt = 1.0` baseline every 1000 steps
(1000 time units, 7 snapshots). The control is to keep only physical times present in both, and average over the same
number of samples in both, so that cadence, window and sample count are identical and only `dt` differs.

| window | `dt = 1.0` | `dt = 0.5` |
|---|---|---|
| `t ≥ 1000`, 6 samples | **+4.17** | +1.00 |
| `t ≥ 2000`, 5 samples | **+4.20**, CI `[+1.4; +8.4]`, 9/10 seeds positive | **+0.40**, CI `[−2.4; +6.7]`, 5/10 seeds positive |
| `t ∈ 2000..4000`, 3 samples | +4.67 | +0.17 |

The two `dt = 1.0` baselines (`x17`, 12 000 steps; `x18`, 6 000 steps) give identical numbers on their common window, so
the estimator is stable enough for the comparison to mean something. **At matched times the gap is as large as before,
and in the matched window the `dt = 0.5` contrast is not distinguishable from zero.** The sampling explanation is dead.

**What the same run also shows, and we have to say it.** The magnitude at `dt = 1.0` is placement-sensitive: +3.69 with
13 samples, +2.79 with 7, +1.00 with 4. The contrast decays with time, so a coarse quadrature puts more weight on the
late, low-contrast part. The robust statement is therefore **the gap, not the number +3.57**: +3.57 is a property of
this estimator at this cadence. That does not weaken the published qualification — it sharpens it.

## 2. The advantage is an advantage in small structures

`scripts/size_resolved_contrast.py` → `l1_field_size_resolved.json`.

Every snapshot records the area of every component, so the count can be recomputed while ignoring components below a
size. If the contrast were a property of the pattern it would survive; if it were fragmentation it would collapse.

| minimum area, cells | `dt = 1.0` contrast | seeds positive | `dt = 0.5` contrast |
|---|---|---|---|
| 1–8 | **+3.57** | 10/10 | +1.24 |
| 16 | +2.57 | 10/10 | +0.58 |
| 32 | +1.36 | 8/10 | +0.36 |
| 64 | +0.86 | 8/10 | +0.20 |
| 128 | **+0.07** | 4/10 | −0.30 |
| 256 | 0.00 | 5/10 | −0.28 |

The homogeneous world is one dominant cluster (largest share 0.925 of the thresholded area); the heterogeneous world is
a scatter (0.817). The count is carried by pieces in the 16–64 cell range, and at 128 cells the two worlds are
statistically indistinguishable.

Lifetimes, filtered the same way (`x23`, peak area per `uid`), agree rather than disagree: the heterogeneous median
falls from 54 steps to 13 as the peak-size threshold rises, while the homogeneous median stays at 3575. The lifetime gap
**widens** with the filter. Read together: heterogeneous inflow multiplies small, short-lived pieces; it does not add
durable structures.

## 3. What this changes

**The claim.** "Heterogeneous inflow doubles the number of components" becomes "heterogeneous inflow multiplies the
number of **small** components (16–64 cells); above ~100 cells the two worlds are indistinguishable". The second is
narrower, survives the size control, and is the version a reviewer cannot dissolve by asking what a component is.

**The estimand.** +3.57 must be quoted with its cadence (7 snapshots at 1000 time units) and with the size floor
(every component, none excluded). Both are now measured, not assumed.

**What it does not touch.** The durable-structure result (1.3 vs 1.2 per run) is unaffected: it was already a count of
long-lived structures, and it agrees with this reading.

## 4. What it does not settle

| question | why it is still open | what would settle it |
|---|---|---|
| mechanism of the `dt` gap | cadence is excluded; modified equation vs. genuinely different discrete dynamics both remain | RK4 at the same physical time, or `dt = 0.25` |
| the overlap rule itself | needs masks, which are not stored | one re-run saving masks, overlap 0.3/0.5/0.7 |
| threshold-free topology | needs fields, which are not stored | one re-run saving `v` at the snapshots it already takes |
| wavelength normalisation | same | same re-run, plus a structure factor |

`X58` (grid convergence with `Du → Du/Δx²`) and `X57` (30 000 units to see whether the plateau reaches zero) are
unchanged and still queued.

## 5. Artifacts

- `scripts/cadence_match.py`, `morphogenesis/experiments/E09_pond/l1_field_cadence.json`
- `scripts/size_resolved_contrast.py`, `morphogenesis/experiments/E09_pond/l1_field_size_resolved.json`
- library: [`lit-decision-rules.md`](../library/lit-decision-rules.md) §2 and §4 carry these numbers
- the four reviews that proposed the checks: [`lit-model-run-2026-11-01.md`](../library/lit-model-run-2026-11-01.md)

## Next hypotheses

1. **If** the size-resolved claim is right, **then** a run that saves fields should show that the heterogeneous world's
   small components are *spatially clustered* near inflow minima, not uniformly scattered. Prediction: the two-point
   correlation of component centres has a shorter correlation length than in the homogeneous world.
2. **If** the `dt` gap is a modified-equation effect, **then** RK4 at `dt = 1.0` should land near the `dt = 0.5` value;
   **if** it is discrete dynamics, RK4 will stay near +4.
3. **If** small pieces are fragments of larger structures, **then** adding masks and tracking splits should show that
   most small `uid`s have a parent that was at least 4× their peak area.
