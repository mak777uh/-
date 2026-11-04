# X168 — Does the crossing move with the inflow rate? (pre-registration, 04.11)

**Status:** pre-registered, not yet run.

## 1. Manipulation is connected

The crossing measured in §4.1 — "contact at about two cells" — was measured at one inflow rate, `F` = 0.030. If the crossing
is a property of the medium's **turnover** (how fast the field is replenished between the bodies), then changing `F` should
move it, and the number would be an artefact of one parameter rather than a length of the medium. This is the parameter the
whole line treats as central, so the crossing's dependence on it is worth one series.

Two arms, `F` = 0.026 and `F` = 0.036, at two surface gaps, 8 and 11, five seeds each (18 runs of 2 000 steps). Gap 8 is where
the pair fuses 5/5 at `F` = 0.030 and gap 11 is just past the crossing (2 of 15 at `F` = 0.030), so a shift in `F` shows up as a
change of share at gap 11 while gap 8 guards against a broken configuration.

Viability was probed before the design: at `F` = 0.020 the field dies (0 components at step 400), at `F` = 0.026 five bodies
were alive and dividing, at `F` = 0.040 one body survived with no divisions by step 400. The two arms sit inside the viable
window, and the probe is recorded because the window is narrow.

## 2. Positive control fires

At gap 8 the pair must fuse in at least 4 of 5 runs **in both arms** — otherwise the arm is not the same world and the
comparison is void. The control fires if the gap-8 share is ≥ 0.8 in each arm.

## 3. Readout exists and varies

The readout is the fusion share at gap 11, which must differ from the gap-8 share (otherwise the readout does not
discriminate), and the gap at the last two-body step, which must vary (standard deviation ≥ 0.2 cells within an arm).

## 4. Sensitivity arithmetic

At `F` = 0.030, gap 11 fuses in 2 of 15 runs (0.13). A turnover that halved the bridge's growth time would move that share by
roughly the change at gap 10 (0.47 at `F` = 0.030), i.e. it would be visible as a share of 0/5 against 3/5 at gap 11 — a
difference of three events. With five seeds only a shift of that size is detectable: this item screens for a large effect and
will report "no detectable dependence" rather than "no dependence" if the shares are close.

## 5. Refusal rule

If either arm's gap-8 control fails, the item reports the design failure and stops. If both gap-11 shares are equal (0/5 or
5/5 in both arms), the item records "no detectable dependence of the crossing on `F` in this window" and says explicitly that
the test could not see a small one. If the shares differ by three or more events, the crossing moves with `F` and the number
in §4.1 becomes a value at one inflow rate.

## 6. What would kill it

A gap-11 share that is the same in both arms kills the hypothesis that turnover sets the crossing — the length would then be a
property of the reaction-diffusion lengths rather than of the flow, which is a cleaner physical statement and would be worth
saying. A crossing that moves with `F` kills the present formulation of §4.1 and requires it to be written as a curve.

## 7. Implementation notes

Runner `scripts/x168_series.py` (two `F` arms × two gaps × five seeds, 2 000 steps each), analysis
`scripts/x168_analyse.py` (fusion share per arm and gap, gap at the last two-body step). Aggregate
`morphogenesis/experiments/E09_pond/l1_field_x168_inflow.json`. Cost about 20 minutes.
