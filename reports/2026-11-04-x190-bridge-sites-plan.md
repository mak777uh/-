# X190 — the bridge with the sample made of sites, not seeds (pre-registration, 04.11)

**Status:** pre-registered, not yet run.

## 1. Manipulation is connected

X189 made the bridge between two large bodies a candidate mechanism for the local-inflow law's sign flip: at the last slice on
which the pieces are still separate, the bridge ratio fell from 0.383 (cold site) to 0.181 (warm site) at radius 6 gap 9, a
difference of −0.202 against a registered bar of 0.05, while it rose +0.090 at radius 3. But X189's caveat is structural and not
statistical: **the manipulation is the lattice site, so seeds on the same site are the same world**. Radius 6 had two distinct cold
sites against one warm, radius 3 one replicated site per level, and within the single warm radius-6 site the ratio spanned 0.0073 to
0.3992 — as wide as the between-group difference. This item replaces the sample: **five distinct sites per level**, three seeds per
site.

The site list exists in advance: the lattice of the pattern has a finite set of distinct values, and X187/X189 already showed which
sites the two levels select. Sites are enumerated from the same arithmetic, so no new physics is introduced.

## 2. Positive control fires

The control fires if (a) the **distinct-site count is at least 5 per level** and each level's sites differ from the other level's
by at least 0.008 in `F_local` (that is the manipulation), (b) each site is realised by **3 seeds**, and the three seeds of a site
produce the same `F_local` to 0.0025 but are not required to produce the same ratio (that is the point of the retest), (c) the
radius-10 ring peak is at least 0.3 in every usable slice, and (d) at least **3 of 5 sites per level** reach a saved slice with two
components, so a level's mean is a mean over sites. Thresholds: 5, 0.008, 3, 0.3, 3.

## 3. Readout exists and varies

The readout of X189 is kept, unchanged: the bridge ratio is the field value midway between the two bodies divided by the maximum of
`v` inside a radius-10 disc around them, read on the **last saved slice on which the two bodies are still separate** (the contact
moment). Saved slices as in X189 (steps 40, 60, 80, 100, 140, 200, 300). The registered tightest-slice summary is **not** used: X189
showed it lands on step 40, the seed-independent initial profile, in 9 of 12 runs.

Two extras are registered because they are what a site-level sample makes possible: the ratio at a **fixed step** (step 100, chosen
because it is the most frequent contact step in X189) and the **within-site spread** (the standard deviation of the three seeds'
ratios, averaged over the five sites of a level). The readout is required to vary within a site; a level whose within-site spread
is zero has been replicated by accident and that site is reported.

## 4. Sensitivity arithmetic, and the prediction

30 runs (2 arms × 2 levels × 5 sites × 3 seeds), 400 steps, up to 7 saved slices each; X189's measured effect at radius 6 was
−0.202 with a within-site spread reaching 0.13-0.19, so a design resolved at the site level needs at least 4-5 sites per level to
place that difference outside the within-site spread, which is why the bar on **sites** is 5. Registered **before the run**:

- **radius 6 gap 9, level means over five sites (paired by site, since each site contributes three seeds to its own level):** the
  warm level's contact-moment bridge ratio is at least **0.05 lower** than the cold level's — the same bar as X189, now over sites;
- the **within-site spread averaged over the five sites is at least 0.02**, i.e. the seeds of one site do not collapse to a point;
- the radius-3 arm is measured and reported but **no directional prediction is registered for it**, because X189's prediction there
  was refuted (warmth moved the ratio the other way) and re-using that wording after seeing it fail would be a post-hoc choice.

## 5. Refusal rule

If the radius-6 site-level difference is below 0.05, the item is recorded as **the bridge difference does not survive the site-level
sample** and X189's candidate mechanism is withdrawn: the flip then has no measured mechanism from either the bodies around the pair
(X188) or the bridge (X189, X190), and the line records that as the boundary of the current law rather than opening another probe.
If the within-site spread is below 0.02, the item is recorded as **the seeds of a site are the same world** and X189's radius-6
difference stays an observation about sites with the seed-level uncertainty removed — a weaker but honest statement. If fewer than
three sites per level reach the contact moment, the item is recorded as **not sensitive by construction** and the site list is
rebuilt before any claim.

## 6. What would kill it

Sites are chosen by `F_local`, which is a function of the site, so the two levels are two sets of lattice positions and not a
continuously varied manipulation: this is a comparison of site populations, and the inference is about those populations, not about
a dose-response curve. The arms differ in radius as well as in level (radius 3 gap 10 against radius 6 gap 9), exactly as in
X187-X189, so a level effect at radius 6 is a difference between the cold and warm *populations* at that radius and never a
within-radius contrast. And 30 runs give five sites per level: enough to place a 0.2 effect against a 0.15 spread, not enough to
resolve anything smaller than about 0.1, so the bars above are the resolution of this design and nothing finer is claimed.

## 7. Implementation notes

Runner `scripts/x190_bridge_sites.py` enumerates sites from the same `G`/`F_local` arithmetic as X187/X189, picks the five sites
closest to each level's target (0.017 cold, 0.030 warm) per arm, and runs three seeds per site with the same `--save-fields-at`
schedule into `_hourly/x190_fields/`. Analysis `scripts/x190_bridge_sites_analyse.py` reuses X189's measurement (ring peak, contact
moment, midpoint bridge, current centres) and reports per-site and per-level statistics plus the within-site spread. Aggregate
`morphogenesis/experiments/E09_pond/l1_field_x190_bridge_sites.json`. Cost about five minutes of CPU.
