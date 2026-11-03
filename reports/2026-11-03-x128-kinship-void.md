# X128 void — the partner is mostly absent, and the absence exposes a flaw in X127's instrument

**Plan:** [`2026-11-03-x128-kinship-plan.md`](2026-11-03-x128-kinship-plan.md) (05:14).
**Aggregate:** `l1_field_x128_kinship.json`.
**Preceded by:** [X127](2026-11-03-x127-absorption.md).

## What it found

| cell | absorbed deaths | with a partner | partner coverage | diffuse share | kin share of partnered | siblings | unrelated |
|---|---|---|---|---|---|---|---|
| 0.030 | 443 | 121 | **27.3 %** | **72.7 %** | 83.5 % | 54.6 % | 16.5 % |
| 0.035 | 664 | 336 | 50.6 % | 49.4 % | 30.4 % | 9.8 % | 69.6 % |
| 0.040 | 834 | 573 | 68.7 % | 31.3 % | 32.5 % | 10.8 % | 67.5 % |

The registered controls fired and the run is **void** on three counts: partner coverage 0.27 / 0.51 / 0.69 against a floor of 0.80, diffuse shares 0.73 / 0.49 /
0.31 against a ceiling of 0.20, and the absorbed share missing X127's by 0.06 in every cell.

## The third failure is the important one

Control 1 required the absorbed share to reproduce X127 (84.5 / 78.7 / 75.7 %). This run got 90.6 / 83.8 / 78.8 %. The difference is mine: I added
`if growth <= 0: continue`, which drops every step at which the survivors' total area shrank, and with those steps go the deaths that occurred in them. A one-line
deviation from the parent run, caught by the control that existed for exactly that purpose. The lesson is the one already in `docs/design-checks.md` — a
recomputation must reproduce its parent before it adds anything — and it held.

## But the first two failures are not defects of the code, they are a defect of the *instrument*, and they reach back into X127

X127 classified a death as absorbed if **the survivors' total area in the whole world** grew by ≥ 50 % of the dead uid's area. In a world with twenty isolated spots
that test is almost always satisfied — some spot is always growing somewhere — so the lattice's "84.5 % absorbed" was measuring the world's net growth, not a
transfer into a neighbour. The same holds for "vanished": a spot dying while other spots shrink looks like a real vanishing.

The evidence is in this void's own numbers: **72.7 % of lattice absorptions have no single partner** (the growth is spread over the whole world), while in the maze,
where one body fills the field, the majority do have one. The instrument was secretly a **world-level** budget applied to a **local** event — the same class of error
the line wrote down twice tonight (a statistic without its unit; a filter without its denominator).

X127's numbers are therefore **not** withdrawn as arithmetic — they are what they say — but their **interpretation is**: "84.5 % of deaths are absorptions" is a
statement about the world's area book-keeping, not about cells being taken over by a neighbour. The claim that a lineage "dies by losing its name, not its cells"
needs the local test before it can stand.

## What is being amended

**X128b** re-runs both questions — the fate census of X127 and the kinship of X128 — with a **local** budget: for each death, the survivors are restricted to those
whose centroid lies within `r_dead + r_survivor + 2` cells of the dead centroid (adjacency at the logged resolution), and the growth is measured among those alone.
A death whose neighbourhood is empty is neither absorbed nor vanished: it is **isolated**, a fourth category that the lattice needs and the earlier instrument
could not express.

Predictions, stated before the run so the design can fail: isolated deaths should dominate the lattice, absorbed deaths should dominate the maze, and the shared
kin/unrelated contrast of this void (83 % kin against 32 %) should either survive the local restriction or disappear with the diffuse deaths that produced it.

## Caveats

- This void's own shares are computed on 27–69 % of the absorptions and are not comparable across cells; they are reported to show *why* the instrument failed,
  not as a measurement.
- The `growth <= 0` deviation means this run is not a replication of X127 even in its own terms; after X128b the absorbed share is compared to X127b, not to X127.

доска: принято 0, отклонено 0, отложено 0.
