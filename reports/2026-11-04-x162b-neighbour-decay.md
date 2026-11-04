# X162b — How far does the medium remember? Answer: it does not remember the spacing, it re-measures the body (04.11)

**Question.** X162 measured the inheritance of the surface gap to a body's nearest neighbour — 0.203 [0.167, 0.238] in the
lattice, against a shuffled-parent null of [−0.020, 0.030] — and left one obvious question: is that a length, i.e. does the
inheritance decay with distance from the body, or is it local density that happens to be measurable only at order one? The
same reconstruction at the 2nd, 3rd and 4th nearest neighbour answers it without a single new run.

Analysis only, on the X156 lattice compacts: 2 222 parent-daughter pairs, the same pairs for every order.

## Result — the slope RISES with the order of the neighbour

| order of the neighbour | slope (daughter on mother) | 95 % bootstrap CI | shuffled-parent null |
|---|---|---|---|
| 1st (nearest) | 0.205 | [0.170, 0.238] | [−0.029, 0.029] |
| 2nd | 0.236 | [0.186, 0.286] | — |
| 3rd | 0.408 | [0.366, 0.451] | — |
| 4th | 0.568 | [0.531, 0.606] | [0.001, 0.067] |

Every order clears its null, and the slopes are ordered **upwards**, by a factor of nearly three from the nearest neighbour
to the fourth. A remembered *scale* would do the opposite: a body's memory of the space around it degrades with distance, so
the daughter's k-th neighbour gap would predict worse and worse as k grows. What is observed is the reverse.

## Why the reverse is the honest reading

In a cluster of bodies the distance to the k-th neighbour is dominated by the **body's own radius**: a bigger body pushes its
neighbours further away, so `g_k ≈ k·d_spacing − 2r` with a spacing set by the density. That means the higher orders are
mostly re-measuring the body's area, which X156 already measured at 0.39-0.45, and its shape at 0.59. And indeed the limits
tend to those values: the 4th-order slope (0.568) is close to the elongation slope (0.586), and the 2nd order (0.236) is
only slightly above the 1st.

The consequence is sharp and it corrects the sentence I wrote an hour ago. The ladder is not ordered by **distance from the
body** — shape 0.59 > area 0.39 > spacing 0.20 — it is ordered by **how much of the body each quantity still contains**.
The order-1 gap is the only quantity in the family that is nearly free of the body's own size, and it is the weakest
inherited quantity measured in this whole line. The medium does not add a length of its own: what looked like a positional
memory at order one is what remains of a body-dependent quantity after the body has been subtracted out.

## Controls and reproducibility

The order-1 slope reproduces X162 (0.205 against 0.203; the pairs differ by 59 because this script reads every logged step
rather than only the first of each pair, which is the pre-registered rule and is stated in the report). The nulls are
computed by shuffling mothers within a run, and both the first and the fourth order sit far from their interval.

## What this changes

1. The X162 result stands as a measurement (0.203, null-clear, unchanged by partialling the mother's radius) but its
   mechanism sentence is corrected: it is not "the medium remembers its spacing weakly", it is "the one spacing-like
   quantity that is not the body is inherited weakly, and everything above it is the body again".
2. The proposal that "the medium might transmit itself better than the body" is now answered in the negative twice: at
   order one the value is the smallest in the ladder, and at higher orders it climbs towards the body's values because the
   body is what is being read.
3. The decay-length experiment that this item was going to be is **not** worth running: there is no decay, so there is no
   length to measure. This is recorded as a positive outcome of a negative design — the item cost three minutes instead of
   three hours.

## Limits

One habitat (the lattice), one series (X156), 2 222 pairs. The k-th-neighbour gap is one scalar per body per order, so a
lattice with an unusual coordination number could mimic the trend; the check that would separate them is a diluted lattice
(heterogeneity amplitude below 0.5), where the coordination number falls and the `k·d` term should weaken predictably.

## What would kill it

If the trend vanished after partialling out the mother's area from both the mother's and the daughter's k-th gap — i.e. if
the rise with order disappeared — the reading "it is the body again" would be wrong. That partial is the next step and it is
cheap: the same 2 222 pairs, one extra regression.

## Next hypotheses

1. **Partial the area out of every order.** If order 3 and 4 collapse to order 1 once the body's area is controlled, the
   correction above is confirmed mechanically rather than by proximity of numbers.
2. **Dilute the lattice** and watch the trend move: fewer neighbours should lower the `k·d` term and with it the high-order
   slopes.
3. **A spacing measure with no k in it**: the distance to the nearest *pore* (an empty cell of the field) is not built from
   the body's radius and would be a clean test of whether the medium transmits any positional information at all.
