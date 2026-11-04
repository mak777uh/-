# X191 — is the bridge a dose–response in the local inflow? (pre-registration, 04.11)

**Status:** pre-registered, not yet run.

## 1. Manipulation is connected

X190 established that warmth thins the bridge between two large bodies at the moment of contact, over five distinct sites per level
(−0.169, exact Mann-Whitney p = 0.016, four of five warm site means below every cold one at radius 6 gap 9), and that the two levels
are two **populations of sites** rather than two values of a swept variable. The same runs showed that seeds are clones: at `eps = 0`
the seed enters only through the initial condition, so three seeds on one site are one world repeated. That fixes the design of the
next question — the bridge's shape in `F_local` can be read with **one seed per site** and five sites per level, spending the budget
on levels instead of on clones.

## 2. Positive control fires

The control fires if (a) each of the six registered levels is realised by **five distinct sites**, all inside ±0.0025 of its target
`F_local`, and each level's sites differ from its neighbour's by at least 0.003 in `F_local` (the level spacing, and the
manipulation), (b) the ring peak is at least 0.3 on the slices used, (c) at least **four of five** sites per level reach a saved
slice with two components, and (d) the seed used for a site is the same for every level (so that a site's position is not confounded
with the level — impossible in general, since the level IS a function of the site; instead, the sites of neighbouring levels are
drawn from the same jitter neighbourhood, and the aggregate reports the jitter distances between levels). Thresholds: 5, 0.0025,
0.003, 0.3, 4.

## 3. Readout exists and varies

Primary, and **registered this time rather than post hoc**: the **contact-moment bridge ratio** — the field value midway between the
two bodies, over the maximum of `v` inside a radius-10 disc around them, at the last saved slice on which the two bodies are still
separate. This is the reading X189 switched to after finding the registered tightest-slice summary contaminated by the initial
profile, and X190 used it as well; it is registered here. Secondary: the same ratio at fixed step 100, the minimum over the central
half of the segment, and the run's outcome (one component at any sample). Saved slices as before (40, 60, 80, 100, 140, 200, 300).

## 4. Sensitivity arithmetic, and the prediction

30 runs: one arm (radius 6 gap 9), **six levels** of `F_local` — 0.016, 0.021, 0.026, 0.031, 0.036, 0.041, which spans the achievable
band at the nominal rate 0.030 (0.015 to 0.045) with a spacing of 0.005 — five sites each, one seed per site. X190's site-level
spread was 0.14 (warm) and 0.16 (cold) with a level difference of 0.169, so the standard error of a six-point trend is about
0.15/√5 ≈ 0.067 per level and the total span of the trend (X190's slope projected over the band, ≈ 0.33) is about five standard
errors: the design can see **the trend**, not each step. Registered **before the run**:

- the level means of the bridge ratio fall **monotonically** in `F_local` allowing **at most one inversion** between adjacent levels,
  and the Spearman correlation over the 30 sites is **≤ −0.5**;
- the fusion share rises across the six levels allowing at most one inversion, and the top level's share is at least **0.6**;
- the site-level correlation between the bridge ratio and the run's outcome is **negative** with **|ρ| ≥ 0.5** (thinner bridge,
  less coalescence).

## 5. Refusal rule

If the level means have **two or more inversions** and the ratio rises at the top level, the item is recorded as **the bridge has a
window, not a monotone response** — the flip is then a threshold at the top of the inflow band rather than a continuation of the
trend, and that is a different statement about the law, to be written as such rather than as a failed dose–response. If the
correlation with the outcome is below 0.5 in magnitude, the item is recorded as **the bridge and the outcome come apart at the level
level** and X190's site-level result stands only as a two-population comparison. If fewer than four sites per level reach the contact
moment, the item is recorded as **not sensitive by construction** and the level targets are moved inward.

## 6. What would kill it

Five sites per level with a spread of ~0.15 cannot resolve single steps, so a "monotone" verdict is a statement about the six level
means and not about `F_local` continuously; the reports give every site value so the reader can see the spread rather than the
summary. The levels are populations of sites, so the design is still not a within-site sweep — no site can be both cold and warm,
because the level is a function of the position. And the top level may be unattainable in sufficient number: at `F_local` = 0.041 the
band is close to its ceiling (0.045), so the aggregate reports how many distinct sites exist within tolerance of each target before
the runs, and a level with fewer than five sites is dropped and said so.

## 7. Implementation notes

Runner `scripts/x191_site_sweep.py` (one arm, six levels, five sites each, one seed per site) with the same `--save-fields-at`
schedule into `_hourly/x191_fields/`. Analysis `scripts/x191_site_sweep_analyse.py` reuses the contact-moment measurement, reports
per-level means with every site value, the Spearman correlation over sites, the inversion count and the correlation between the
bridge and the outcome. Aggregate `morphogenesis/experiments/E09_pond/l1_field_x191_site_sweep.json`. Cost about three minutes of CPU
(30 runs, one seed per site now that seeds are known to be clones).

## 8. Amendment after the first run (04.11): the picker selected one phase five times

The first run used the picker of X190 lightly: one seed per site, first five distinct jitters per level. Its result is invalid as a
dose-response and why is instructive. At the level `F_local = 0.030` **all five sites give the identical contact ratio 0.39916**
(sd 0.0000), and at `F_local = 0.022` three of five give 0.44325 and two give ~0.01: the readout is not a function of the *jitter*
(distinct jitters were required) but of the **phase** — the position modulo the pattern's 12-cell period, which is what sets `G` and
therefore `F_local`. Five sites inside one narrow band of `F_local` are five draws from a small set of phase classes, and the early
seeds of a level land on the same class. So "five distinct sites" is not five independent draws for this readout, and the level means
of the first run — 0.363, 0.272, 0.167, 0.399, 0.032 with the 0.030 level rising above the trend — are a phase artefact.

The picker is therefore amended **before** the corrected run: a level's five sites must have **distinct phases** `(jx mod 12, jy mod
12)` as well as distinct jitters, and the aggregate reports each level's distinct phases and distinct ratios, so the effective
replication of a level is visible rather than assumed. Everything else — the readout, the bars, the five retained levels and the
refusal rules — is unchanged. The first run's numbers stay in the aggregate under `first_run_phase_artefact`, because a design flaw
found by running is part of the record.

This is X190's clone finding applied one level deeper: X190 required three *seeds* per site and found them to be one world; here
five *sites* per level turned out to be one phase. What the readout depends on is the phase, so the sample has to count phases.

