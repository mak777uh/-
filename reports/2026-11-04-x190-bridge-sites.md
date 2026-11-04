# X190 — the bridge with the sample made of sites (04.11)

**Question.** X189 made the bridge a candidate mechanism for the law's sign flip at the largest bodies (contact-moment bridge ratio
0.383 cold → 0.181 warm at radius 6, −0.202 against a bar of 0.05) but its sample was **seeds on the same lattice site**: two distinct
cold sites against one warm, and within that one warm site the ratio spanned 0.0073–0.3992. This item re-measures the same quantity
with the sample the manipulation actually has — **five distinct sites per level**, three seeds each, 30 runs. Preregistration
`reports/2026-11-04-x190-bridge-sites-plan.md`; readout unchanged from X189 (midpoint bridge over the radius-10 ring peak, at the last
saved slice on which the bodies are still separate).

**Result: the difference survives at the site level, and the seeds turn out to be clones.**

| arm | level | `F_local` over its sites | fused | contact ratio over 5 sites | site means |
|---|---|---:|---:|---:|---|
| radius 6 gap 9 | cold | 0.0162 | 15 of 15 | 0.36295 | [0.184, 0.192, 0.473, 0.473, 0.492] |
| radius 6 gap 9 | warm | 0.0300 | 6 of 15 | 0.19346 | [0.138, 0.138, 0.138, 0.154, 0.399] |
| radius 3 gap 10 | cold | 0.0187 | 0 of 15 | 0.24629 | [0.187, 0.187, 0.286, 0.286, 0.286] |
| radius 3 gap 10 | warm | 0.0300 | 9 of 15 | 0.31715 | [0.266, 0.266, 0.316, 0.334, 0.404] |

At radius 6 the warm-minus-cold difference over sites is **-0.16949** (registered bar −0.05), and the order is
almost complete: four of the five warm sites lie below **every** cold site, whose lowest is 0.184. The exact Mann-Whitney
one-sided test on the five site means gives **p = 0.0159**. At radius 3 warmth moves the ratio the other way again
(+0.07086, p = 0.9246), which is what the outcome does there too (3 of 5 sites fused against 0 of 5).

**The registered within-site-spread check failed, and that is a finding about the design, not a gap.** The three seeds of a site give
*identical* contact ratios — within-site sd is **0.0** at all 20 sites — because at `eps = 0` the seed enters the run only through the
initial condition. Same-site seeds are therefore **one world repeated**, and every seed-level group in X187–X189 had at most one or two
distinct worlds: X187's radius-6 Fisher p of 0.39, X189's single replicated radius-3 site, and X187's "six seeds" per group all
inherit that. The unit of replication in this line is the **site**, not the seed, and the retest had to be built on sites to make any
statement about it.

**So the mechanism now stands as follows.** A warm site thins the bridge between two large bodies enough that a touched pair separates
again (radius 6: -0.16949 over sites, p = 0.0159, four of five warm sites below the coldest), while at the small size warmth
makes the bridge slightly thicker and the pair coalesces more. X188 ruled out the other obvious mechanism — extra bodies appearing
around the pair. What is *not* claimed: that the bridge is the only cause, that the relation is a dose-response in `F_local` (the two
levels are two site populations, not a swept variable), or that anything finer than about 0.1 in ratio is resolved by five sites.

**Next hypotheses.** (1) A six-level site sweep of `F_local` at the largest radius, to see whether the bridge ratio is monotone in
the inflow or turns over near the band's edge — the current design has two populations and cannot tell a threshold from a slope.
(2) Whether the same thinning explains X186's own radius-6 exception (its gap-7 and gap-9 cells) when those cells are re-read per
site rather than per run. (3) The clone finding generalises: any item in this line that varied *seeds* at fixed geometry has to be
re-read as one or two worlds, starting with X187's Fisher p. Artifact:
`morphogenesis/experiments/E09_pond/l1_field_x190_bridge_sites.json`.
