# X118 / X119 — matching could not separate size from daughters, so a model did: more daughters, less survival

**Plans:** [`2026-11-03-x118-mediator-plan.md`](2026-11-03-x118-mediator-plan.md) (01:46, **void**),
[`2026-11-03-x119-post-hoc-record.md`](2026-11-03-x119-post-hoc-record.md) (01:52).
**Aggregates:** `l1_field_x118_mediator.json` (void), `l1_field_x119_model.json`.

## X118 voided by design, and the diagnosis is a property of the medium

Matching requires sister pairs with near-equal **area** and different **daughter counts**. That subset is nearly empty: **22 pairs** in the lattice and **17**
in the maze, with the closest pairs still ~8 % apart in area (ratios 0.919 / 0.906, outside the registered [0.95, 1.05] band even after widening).

The reason is structural: sisters resemble each other in size (that is the heredity this line has measured all day), and daughter count itself rises with
size, so the two conditions fight over the same tail. **Size and daughter count are not separable by matching inside sister pairs** — a property of the
medium, not bad luck, and worth recording as such.

## X119: the same question, answered by a model

Instead of matching, pool every uid and fit `alive ~ log(area) + daughters`, with a world-level bootstrap (500 draws). The whole cloud is used, and each
coefficient is estimated with the other held fixed statistically.

| cell | uids | alive at the end | heredity | area coefficient | 95 % CI | **daughters coefficient** | 95 % CI |
|---|---|---|---|---|---|---|---|
| 0.030 | 2 257 | 29.2 % | 0.548 ✓ | **+0.363** | [0.258, 0.468] | **−0.429** | **[-0.509, -0.345]** |
| 0.040 | 1 993 | 3.0 % | 0.480 ✓ | **+0.052** | [0.043, 0.062] | **−0.051** | **[-0.061, -0.043]** |

Both coefficients exclude zero in both cells, and they point in **opposite directions**:

- **size helps survival** at fixed daughter count (positive, large in the lattice);
- **having more daughters hurts the parent's own survival** at fixed size (negative, and in the lattice nearly as large as the size effect).

That is a **cost of division**, and it is the first time this line has seen one. It also explains why X115's raw survival advantage looked so large and why
X116 halved it: the two channels run against each other, and a raw comparison of big versus small sisters nets them together.

## The confound that must be named before this is a claim

**Age.** A structure that has produced many daughters has usually lived longer, and a longer-lived structure has had more time either to survive to the
horizon (alive) or to die before it (not alive). If mortality is hazard-like, older structures are *less* likely to be present at the end for reasons that
have nothing to do with division. The model controls area, not age.

So the honest statement is: **at fixed size, more daughters predicts lower survival; whether that is a cost of division or the age of the structure is not
separated here.** Age is measured on these logs (`first` appearance), so the control is analysis-only and is registered as X120.

## What changes in the day's picture

The consequence story is now two-signed rather than one-signed:

| channel | direction | status |
|---|---|---|
| size → own survival | **+** | measured, model-controlled for daughters |
| daughters → own survival | **−** | measured, model-controlled for size; age is the open confound |
| size → lineage survival (X115/X116) | **+** on the raw contrast, halves when daughters are matched | partly arithmetic |

A medium where being large helps you persist and dividing a lot hurts you is a coherent ecology, and it is the first thing this line has measured that looks
like one.

## Caveats

- The maze's alive rate is 3 %, so its coefficients are small in absolute terms and rest on few survivors; the lattice is the informative cell.
- OLS on a binary outcome is a linear probability model: coefficients are interpretable as percentage-point shifts, but they can leave [0, 1] at the
  extremes and the bootstrap is over worlds, not over the coefficient's sampling distribution.
- "Alive" is the uid's **own** presence at the last step, not its subtree's — deliberately, because X115 already covers the subtree.
- One seed set, one box, the 0.20 cut.

## Next

- **X120 (registered):** add `age` (first appearance) to the model. If the daughters coefficient survives, it is a cost of division; if it collapses, the
  negative sign was age and X119's headline becomes "old structures are less likely to be alive at the end", which is not a consequence of division at all.

доска: принято 0, отклонено 0, отложено 0.
