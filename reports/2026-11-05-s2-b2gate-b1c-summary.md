# S2 B2-gate probes + B1c/B2-lite summary, 05.11

Non-degenerate gradient+flip setup (proportional, lethal upkeep, 3 seeds unless noted), `move_ci` (drift along *current* gradient) + `alive_correct_share` (occupancy of favorable half, mapping flips with environment).

| mechanism | flip | correct after | move_ci after | alive/died | note |
|---|---|---:|---:|---:|---|
| baseline (no moves) | 200 | 0.412 | — | 393/4674 | P0 |
| pred-gate + gradpos, cost 0.03 | 200 | **0.547** (5 seeds) | **+0.320** | 454/1901 | B1/B1b best stable |
| pred-gate + gradpos, cost 0.01 | 200 | 0.524 | +0.282 | 570/755 | cheaper != better (crowding) |
| gradpos, drift | 150→200 | **0.594** | **+0.337** | 390/1657 | B1 |
| `gradpos_free` (dir - crowding) | 200 | 0.505 | +0.144 | 572/2035 | B1c: trades direction for spread → worse |
| `gradpos_improve` (only if res>=cur) | 200 | 0.512 | +0.116 | 257/5641 | B2-lite: blocks escape after flip, high mortality |
| random-gate(prob 0.3) + gradpos | 200 | 0.608 | +0.472 | **87/3736** | **R1-unstable/near-extinct** (seed 2 ends alive=4) — apparent recovery is attrition artifact, not healthy adaptation |
| random-gate(prob 0.7) + gradpos | 200 | 0.576 | +0.351 | 361/1549 | stable modest gain, still < control ~0.63; seed 3 extinct at end |

**Takeaway:** Directed drift is necessary and achieved (B1, CI>0 realigning after flip/drift), giving partial recovery above dispersal (~0.50) but **not** to the no-flip/control level (~0.63–0.68). Budget (B1b), simple anti-crowding (B1c), absolute resource filter (B2-lite), and gate-prob sweeps (with stability caveats) do **not** close the gap. The apparent 0.61 at p0.3 is not a valid win (near-extinction). Next high-impact moves (per plan, by mechanism change not waiting): **B2 persistence/run-tumble with temporal comparison** (keep course when signal improves, reorient when it falls; memory length under F-ADAPT, must not cling to old gradient), then if still bounded → **C heritable variation/selection** (tests “adaptive later” honestly) and **D transfer across environment families** (patches/noise/periodic). Artifacts in `morphogenesis/experiments/E09_pond/s2_*`.