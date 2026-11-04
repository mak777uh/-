# X161 — Is a discrete trait inherited? Division order and fertility (pre-registration, 04.11)

**Status:** pre-registered, not yet run.

## 1. Manipulation is connected

Everything measured so far is continuous: area, elongation, log width, spacing. Digital substrates, however, inherit in
**discrete** units — a lineage tree is a set of integers, and a trait that is inherently discrete cannot be diluted the way a
continuous one can. If a discrete state is inherited, the ratchet that keeps it is the mechanism a digital medium has and a
physical one does not, which is exactly why it is worth measuring rather than assuming.

This item reads the lineage trees that the runs already produce. Every field-track artifact carries `uid_pairs` (parent →
child edges) and `uid_outcomes` (each uid's first and last logged step, its peak area and its score at birth), so a tree is
already there; nothing new is run. The traits are:

- **division order** — the number of children a body produces at a division (2, 3, …): an integer, and the trait most obviously
  discrete;
- **fertility** — whether a body divides at all (1/0): the binary state that a ratchet would protect;
- **lifespan** — the number of logged steps a body survives: a count, discrete but quasi-continuous.

## 2. Positive control fires

The positive control is the continuous quantity measured on the same trees: **peak area**, whose parent-daughter slope is
known from X156 (0.39-0.45 between matched pairs). The positive control fires if the area
slope computed from these trees lies in [0.2, 0.7]; otherwise the trees are not the same objects the rest of the line measured
and the item stops. This is the check that the lineage
reconstruction (via `uid_pairs`) agrees with the positional reconstruction used everywhere else.

## 3. Readout exists and varies

Division order must vary (not every division producing two children, and not every body having the same number of
children); fertility must vary (some bodies sterile); lifespan must vary. Specifically: at least three distinct division
orders must occur across the trees, and at least 10 % of bodies must be sterile. If all divisions produce the same number of
children, the trait does not exist in this world and the item says so — it does not look for another trait until it finds a
varying one.

## 4. Sensitivity arithmetic

The trees give several hundred divisions per run (the ten X167b single runs carry 143 edges each in a 3 000-step run), so
the parent-daughter pairs number in the thousands, and a correlation of 0.1 is detectable at that count. The positive
control anchors the scale: the area slope of 0.39-0.45 corresponds to a correlation of roughly 0.6-0.7, so a discrete trait
whose transmission is comparable would show a correlation of at least 0.2 and be visible; a correlation of 0.05 or less
would mean the discrete state is re-drawn at every division.

## 5. Refusal rule

If the positive control does not reproduce the area slope, the item reports the reconstruction failure and stops, because
every number downstream would be measured on different objects than the rest of the line. If division order does not vary
(§3), the item records "this world has no discrete division trait" — a fact about the medium, not a failure. If the discrete
traits correlate with their parents no better than the shuffled-parent null, the item is recorded as **the discrete state is
re-drawn at every division: in this medium, integers are no more heritable than real numbers, and the digital ratchet that
the literature promises does not exist here.**

## 6. What would kill it

A division-order correlation that clears its null would be a positive and would change the paper's answer to "what does a
division transmit": a discrete state would be the first structure that survives with no dilution at all. A fertility
correlation that clears the null while the area control holds would be the stronger form of the same finding — a binary
state inherited intact.

## 7. Implementation notes

Analysis `scripts/x161_discrete.py` on the X167b single-body logs (ten runs, 3 000 steps, 143 edges each) plus the X158
compacts where present; lineage tree built from `uid_pairs`, traits from `uid_outcomes`, parent-daughter pairs formed per
edge, shuffled-parent null by permuting parents among children within a run. Aggregate
`morphogenesis/experiments/E09_pond/l1_field_x161_discrete.json`. Cost: analysis only.
