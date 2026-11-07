# 034: What a signal should change — the place, the time, or the rules

- **Type:** research article (short format, one result)
- **Version:** v1.0
- **Date:** 2026-11-07
- **Status:** draft; ready for the publisher checklist
- **Authors:** Ilya Vladimirov
- **Previous article of the series:** [033](033-selection-exists-but-a-heritable-trait-does-not-ride-it.md)
- **Artifacts:** `morphogenesis/experiments/E09_pond/s89_e14b_20seeds.json`

## The line this article continues

Article 033 ended with a negative: a heritable trait does not ride the selection this world contains, because
with the trait costing nothing the shift is −0.00002. That result points at a prior question about signals.
The earlier articles tested only one way a signal can act — it tells the cell **where** the food is — and it
paid only when it predicted the food early enough, and then only weakly (+0.012). But a signal could act in
other ways. This article asks which way pays: the **place** (where the food is), the **time** (how much food,
everywhere), or the **rules** (what the cell itself pays).

**Keywords:** signal, environment, agent-based model, immobile agents, rules versus map

## 1. Design

**Cells do not move.** They are planted in the poor centre of the grid — position (16,16), where the resource
is 0.2 against 1.0 in the three rich patches. The planting position and the zone class are written into
every row of the artifact.

**Equal dose.** Every arm adds the same total resource per step (57.6–57.8 units across the arms), so the arms
differ only in how the signal distributes or modulates it.

| arm | what the signal does |
|---|---|
| `none` | nothing — the control |
| `local` | food appears **only** at the wave crest (the signal says **where**) |
| `wave` | food appears **everywhere**, the amount following the wave (the signal says **when**) |
| `rule` | the food is untouched; the signal **lowers the cell's upkeep** (the signal changes the **rules**) |
| `ab` | both the place and the amount |

Twenty seeds, 600 steps. R1 (mean deaths ≥ 10 and mean living ≥ 10) holds in **20 of 20** runs per arm.

## 2. Result

| arm | favourable share (window 5) | paired difference | seeds positive |
|---|---|---|---|
| `none` | 0.093 | — | — |
| `local` | 0.105 | +0.0117 | 14/20 |
| `wave` | 0.101 | +0.0080 | 11/20 |
| **`rule`** | **0.145** | **+0.0512** | **18/20** |
| `ab` | 0.111 | +0.0172 | 15/20 |

**The signal that changes the rules is four times stronger than the signal that says where**, and eighteen of
twenty seeds agree. The signal that says *when* is indistinguishable from noise (11/20).

## 3. Why

An immobile cell cannot act on a map. Knowing that the food is two cells away is worth nothing if the cell
cannot go there. What it can use is a change in **its own** terms: if the signal makes its upkeep cheaper, the
benefit applies wherever the cell happens to stand.

This agrees with the selection measurements of article 033: a cell's fate is set by its **energy** (+0.154
survival differential) and its **age** (+0.113), not by whether it stands in a rich zone (+0.041). A signal
that touches energy directly therefore has the largest lever available.

## 4. What this does not show

- It does not show that "rules" beat "place" in every world — only in a world of **immobile** cells planted in
  a **poor** zone. With mobile cells the picture may reverse, and that is the obvious next test.
- It does not give a mechanism: the effect is measured, not derived.
- It tests **one** strength of the rule signal (0.05 energy per step). Whether the effect grows with strength
  has not been measured.

## 5. Where we move next

- **The mobility axis.** The same five arms with cells that can move: if "place" overtakes "rules" once the
  cell can act on a map, the explanation in §3 is confirmed.
- **The strength axis.** Three strengths of the rule signal, to see whether the effect is monotone.

## 6. Reproducibility

The artifact `s89_e14b_20seeds.json` holds all 100 rows; the script is
`morphogenesis/scripts/s87_e14_what_signal_changes.py`. Runs were on CPU with one thread. R1 is true in every
run. Every number in §2 is machine-checked against the artifact by `scripts/check_article_034_numbers.py`.

## Authorship and automation

This article was written by AI agents working in a continuous research loop, with periodic feedback from a
human operator. The experiments were designed, run and verified by the agents; the operator set the research
direction and approved the publication format. Every number in the text is machine-checked against the
deposited artifacts.
