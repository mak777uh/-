# X168 — WITHDRAWN: the gap was passed in the wrong units (04.11)

**Status: withdrawn before publication. The number it reported was an artefact of my own parameter conversion, not a
property of the medium.**

## What the item claimed, and why it was wrong

X168 reported that the fusion crossing moves with the inflow rate: a pair at a "surface gap of 11" fused 5/5 at `F` = 0.026
and `F` = 0.036 against 2/15 at `F` = 0.030, which looked like a minimum near 0.030.

The cause is a units error. `field_track.py --init-spots R:SEP` takes the **centre separation**: the two discs are placed at
`cx ± SEP/2`, so the surface gap is `SEP − 2R`. X158's own runner converts correctly (`(3.0, 10, 16)`: radius 3, surface gap
10, separation 16). X168 passed the surface gap itself — `--init-spots 3:11` is a centre separation of 11, i.e. a **surface
gap of 5**, and `3:12` and `3:14` were surface gaps of 6 and 8. Every one of those pairs fuses, as a pair at a surface gap of
5, 6 or 8 must at `F` = 0.030. The apparent difference between "gap 11" and the X158 baseline was the difference between a
gap of 5 and a gap of 11.

X168b, the pre-registered follow-up, ran the same wrong conversion and therefore fused 5/5 at every one of its gaps up to a
"12" that was really a 6. Its pre-registered refusal rule fired — "if the matched baseline fuses at gap 11 in 3/5 or more, the
contrast is an artefact" — and it refused to report. The refusal rule did its job: the artefact was caught by the design that
was meant to catch it, one item later.

## What is withdrawn

Everything in the X168 report: the non-monotone dependence on the inflow rate, the "minimum near 0.030", the "both a lower and
a higher inflow push the crossing outward", and the amendment to §4.1 that said the crossing must name its inflow rate. The
CLAIMS row is retracted by an appended row, not deleted, and the world-design section is marked withdrawn rather than
removed.

## What is not affected

- **X164** (unequal pairs) converted correctly: its runner computes `sep = r1 + r2 + gap` before calling `--init-spots`.
- **X165** (three bodies) uses `--init-row N:R:GAP`, whose implementation computes `sep = 2R + GAP`.
- **X166** passed explicit `(radius, gap, sep)` triples, with `sep = 2R + gap`.
- **X158, X159** likewise carried explicit triples, so the crossing of §4.1 — ten cells at `F` = 0.030 — stands.

## Why this got as far as a report

The report was written from the analysis output without a units check between the caller and the callee, and the two
conventions (`--init-spots R:SEP` = centre separation, `--init-row N:R:GAP` = surface gap) coexist in the same script with no
guard. The fix is in the code, not only in the prose: `scripts/field_track.py` now warns when `--init-spots` is given a
separation smaller than `2R` (an overlapping pair) and `scripts/x168c_series.py` computes the separation in one function with
the conversion in its name. The incident is recorded in [`docs/incidents.md`](../docs/incidents.md) §15.

## What replaces it

`X168c` runs the same question with the conversion made explicit: `F` in (0.026, 0.030, 0.036) at surface gaps 8, 10 and 11,
five seeds, 2 000 steps, plus a 6 000-step length control at `F` = 0.030 and gaps 10 and 11 so the short arms can be compared
with the X158 baseline at the same length. Its report replaces this one.
