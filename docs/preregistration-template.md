# Preregistration template — five things before a series runs

Copy this file, fill every `REQUIRED` field, and run `python scripts/check_design.py --prereg <file> --ci`.
If any of the five fails, the series is not run. It is recorded instead as **insensitive by construction**, with the
failing item named.

Why this template exists (31.10.2026): five designs of the field line were invalid, three of them for the same reason —
the manipulated variable never reached the dynamics. Roughly 110 runs produced nothing. The rules below are the checks
that would have caught each of them in minutes.

---

## 1. Manipulation is connected — REQUIRED

Two runs, identical in everything except the manipulation, must produce **different dynamics**.

    python scripts/check_design.py --pair <on.json> <off.json> --key series[].components

- **Record the two hashes here:** `on = …`, `off = …`
- **They must differ.** If they are equal, the manipulation changes a label, not the world.

*Caught by this item:* `X46` — `lead0`, `lead20` and `lead40` had identical dynamics (`efd3ee56dc8e`), because the
sensor coupling was zero and the lead changed only a recorded field.

## 2. Positive control fires — REQUIRED

The arm in which the effect **must** be strong has to show it, with an observed size, not a promise.

- **Control arm:** …
- **Observed effect:** … (units, with the number from a run)
- **Threshold that counts as "fires":** …

If the control does not fire, the experiment cannot produce a difference and is not run.

*Caught by this item:* `X49` — pulses fired in the `periodic` arm and the phase still showed nothing (0.00 components,
0.00 divisions), so the whole omission design was a null by construction.

## 3. Readout exists and varies — REQUIRED

The behaviour being measured must be recorded **per slice** and must not be constant.

    python scripts/check_design.py --readout <run.json> --key series[].components

- **Readout name:** …
- **Field in the artifact:** …
- **Observed variance:** …

*Caught by this item:* `X49` again — `splits` was `None` in every slice (and later, `born` was 0 in a run with 1469
living cells, because growth happens by cells moving rather than dividing).

## 4. Sensitivity arithmetic — REQUIRED

Written **before** the criterion:

- **baseline** (median of the readout) = …
- **sd** between seeds = …
- **effect worth detecting** = … (absolute and relative)
- **seeds needed** at α = 0.05, power 0.8 = …
- **CV of the baseline** = … — if above 0.3, the readout needs a paired design or a stronger effect

*Caught by this item:* `X53` — growth has CV = 0.333, so an unpaired design would need 174 seeds for a 10 % effect;
the design was changed to paired before any run.

## 5. Refusal rule — REQUIRED

Name, in advance, the outcomes under which this experiment will be declared worthless rather than negative:

1. …
2. …

---

## Design summary

| element | value |
|---|---|
| world and settings | |
| arms | |
| window | |
| readout | |
| seeds | |
| criterion | |

## Status

- [ ] 1. connected (hashes differ)
- [ ] 2. positive control fires
- [ ] 3. readout exists and varies
- [ ] 4. sensitivity computed
- [ ] 5. refusal rule written

**Not run until all five are ticked.**
