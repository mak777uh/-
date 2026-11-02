# X122 — the "cost of division" is the identity convention: a parent's uid is retired when it divides

**What was found, and it retires X119's headline.** X121's person-period table could not produce a non-zero daughter count for any row, and the diagnosis is not
a join bug:

| uid | first appearance | steps where it is present | its children appear |
|---|---|---|---|
| 1 | 1 | 1, 10, 20 … **210** | at **220** |
| 2 | 220 | 220, 230 … 330 | at 340 |
| 5 | 340 | 340, 350 … 490 | at 500 |

**A structure's uid ends exactly when it divides.** With `--split-new-uid` the daughter is a new uid — and the *parent* is not carried forward: the area it held is
taken by the children, and the parent's uid stops appearing in the log. So "number of daughters" and "own survival" are **anti-correlated by construction**: a
structure with daughters is, by the identity rule, a structure that was replaced.

## What this does to X119

X119 fitted `alive ~ log(area) + daughters` and reported `−0.429` (CI −0.509…−0.345) in the lattice, reading it as a cost of division, with age named as the
remaining confound. The sign is now explained without any biology: **dividing ends the uid**, so "more daughters" mechanically predicts "not present at the end
under that uid". The coefficient is a restatement of the identity convention.

X119's claim row is therefore **withdrawn as an artefact**, not merely hedged. X120's finding is unaffected in its own terms (divisions are early — that is a
statement about when splits happen, not about survival), and X115/X116 are unaffected because they measure the **subtree**, not the uid: "alive at the end" there
means "some descendant of that sister is present", which is not the same quantity.

## The quantity that was actually measured

`alive` for a uid means "**present and undivided** at the last step". That is a legitimate readout — it says how many structures reached the horizon without
splitting — but it is not survival in the demographic sense, and the daughter count cannot be its predictor.

Three readouts now have to be kept apart, and the line has been sloppy about it:

| readout | what it means | where used |
|---|---|---|
| `uid present at the end` | the structure did not divide away and did not die | X119, X121 (misread as survival) |
| `subtree alive at the end` | the lineage continues through at least one descendant | X115, X116 (correct for the question) |
| `generations reached` | how deep the lineage goes | X113, X114 |

## The rule this earns

**An identity convention is part of every survival readout.** When the tracker retires a parent at a split, "the parent survived" and "the parent divided" are
mutually exclusive states, and no regression of one on a count of the other can be interpreted as a cost. The analysis must state which of the three readouts it
uses, and a model that predicts a uid's presence must not carry a count of its divisions as a predictor.

## What survives of the night's consequence work

- **Size is inherited** (ρ₁, room-corrected values) — untouched.
- **Size is a lineage property across a generation** (X97/X97b) — untouched.
- **Size buys generations, faster** (X113/X114) — untouched; the readout is generations, not the uid.
- **Larger lineages persist more often** (X115/X116) — untouched; the readout is the subtree, and X116's halving on branch counts stands.
- **"Cost of division"** — withdrawn: the sign is the identity rule.

So the day ends with a positive consequence chain and one artefact caught before it reached the manuscript, which is the better outcome for both.

## Caveats

- The retirement of the parent is visible in the logs as a disappearance, not as an explicit "split" flag: the evidence is the exact coincidence of a child's
  first appearance with the parent's last, verified on three uids and consistent with the tracker's `--split-new-uid` implementation.
- If the intended convention was that the parent keeps its uid, then the tracker and the analyses disagree — worth a separate check, because every lineage
  statistic in this line would shift.
- One seed set, one box, the 0.20 cut.

доска: принято 0, отклонено 0, отложено 0.
