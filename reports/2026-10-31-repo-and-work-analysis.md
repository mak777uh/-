# The repository and my own work: a full analysis (31.10.2026, 20:30 MSK)

Written at the owner's request. Everything below is measured, not remembered; where a number is an estimate it says so.

---

## 1. The repository in numbers

| area | files | of which `.md` | of which `.py` | size |
|---|---|---|---|---|
| `scripts/` | 209 | 1 | **160** | 2.3 MB |
| `docs/` | 42 | 41 | 0 | 2.0 MB |
| `reports/` | 211 | **183** | 0 | 4.0 MB |
| `articles/` | 31 | 31 | 0 | 0.5 MB |
| `manuscript/` | 7 | 7 | 0 | 1.0 MB |
| `library/` | 110 | 78 | 10 | 1.7 MB |
| `lab/` | **1490** | 13 | 0 | 7.3 MB |
| `morphogenesis/` | 2372 | 8 | 175 | **1138 MB** |

Key documents: `docs/world-design.md` **8080 lines**, `manuscript/paper.md` 1535, `manuscript/CLAIMS.md` 286 rows
worth, `README.md` 206, `AGENTS.md` 639, `lab/queue.json` **172 items**, `lab/registry.json` 32 experiments.

History: **1441 commits**, 65 of them today; `.git` **214 MB**.

Gates: **14** in `make verify`, plus the health cycle. Tests: **80** files in `morphogenesis/tests/`, and they do cover
lab scripts (`test_aggregate_check`, `test_artifact_table`, and others).

---

## 2. What is genuinely healthy

1. **The gates are substantive, not decorative.** They check numbers against aggregates, claim types, metric
   definitions against implementations, section references, README freshness, report indexing, Wilson intervals, mutual
   information calibration, and a comparator audit. A repository with fourteen real gates is rare.
2. **Anchors are a working habit.** Every probe change of mine was checked bit-for-bit against a pre-change reference,
   and twice that check caught my own mistakes (the seed mismatch in the ghost anchor; the identity of the `X46` arms).
3. **The claims matrix is honest.** 106 rows; the rule "no row, no claim" is enforced by script; two of my claims are
   recorded as **withdrawn** rather than quietly deleted.
4. **Artifacts travel with reasons.** Retention ledger, artifact table with hashes, external-marker gate for audits.
5. **The record survives my errors.** Every one of my five invalid designs is written into `world-design.md` with the
   reason, and the queue and registry say "invalid", not "closed".

---

## 3. Where the repository is structurally weak

### 3.1. The plan journal has become unreadable

`docs/world-design.md` is **8080 lines and 102 sections** (§10aa … §10du). It is the single most important document of
the line and it can no longer be read, searched or reviewed as a whole. Any reader — including me on a new session —
must grep to find anything, and every edit risks conflicting with another agent in the same file.

### 3.2. Two thirds of the scripts are undocumented

**160 scripts, 59 mentioned in `docs/scripts.md`, 101 not.** Of those, **20 are mentioned nowhere at all** in any
document — for example `ci_receipt`, `claim_audit`, `cycle_audit`, `lib_cycle`, `lit_duty`, `lit_search`,
`queue_runner`, `rotate_notices`. Two of my own new scripts (`field_lifetimes`, `adequacy_mi`) are cited in the article
but absent from the script index.

This is not cosmetic: the script index is how an external reader finds the command behind a number. An index that
covers 37 % of the scripts makes the other 63 % effectively unreachable.

### 3.3. The reports are a pile, not a catalogue

**211 files in `reports/`, 183 markdown**, produced at 8–25 per day. `reports/README.md` is 349 lines of flat rows.
There is no thematic grouping, no "read these five first", no archive tier. A reader cannot tell a plan from a result
from a post-mortem without opening the file.

### 3.4. The queue is a graveyard

**64 planned items, and not one of them has ever been claimed** (`claimed_at` empty for all 64). Some are from 26.10.
The contract already has the right mechanism for this — `lab/pool.json` with a revival condition — but it is not used.

### 3.5. Snapshots go stale silently

`lab/checkpoints.json` claimed **12 of 12 canonical weights ready** while the disk holds **one**. Nothing in `verify`
compares the snapshot to the filesystem; I found it by accident while measuring disk usage. The same risk applies to
`lab/state.json` and `lab/registry.json`.

### 3.6. Artifact growth in git

`morphogenesis/experiments` is **615 MB**, growing at roughly 50–100 MB on a busy day (today's series added ~30 MB).
`.git` is 214 MB. At the current rate the repository becomes awkward within weeks, and there is no policy for
per-line retention beyond the log-archive rule.

### 3.7. Two languages, drifting

There are now two of everything where guidance exists: two publisher instructions (RU and EN), two editions of article
028. The EN edition is canonical and the RU one is already one edit behind — which is exactly the failure that
produced the tombstoned first deposit.

### 3.8. Numbers are machine-checked only where someone remembered

`check_article_numbers.py` covers article 028 (15 checks × 2 editions). The manuscript, README and reports have no such
check; `verify_sections_numbers.py` covers a handful of manuscript sections. Every other number is checked by eye.

---

## 4. My own work: what I did and how I failed

### 4.1. What went well

- The **ghost control** (`X50`) turned a correlational claim into a causal one, and it survived: `+0.0362` (10/10) →
  `0.0000` (0/8). That is the strongest single result I produced today.
- The **habitability arithmetic** (`b_crit = 0.0075`, practical threshold above break-even) explains a day and a half
  of nulls in one paragraph.
- I **withdrew** my own measure and my own experiment when they failed, and wrote down why, in the record.
- The **publication** was verified by content hash, not by file size, and the one archive mismatch was caught and
  explained rather than ignored.
- I found and closed the **contract debt** I had created (README/CLAIMS), and added a regression test that pins the
  published claim.

### 4.2. How I failed — the list, without softening

1. **Five invalid designs in a row** (`X45`–`X49`). About **110 runs** of compute produced nothing. Three of the five
   were invalid for the same reason: *the manipulated variable was not connected to the dynamics.*
2. **I used a measure that manufactures its own effect** (mutual information between first differences). The shuffled
   arm gave a *larger* value than the moving one — the signature of the artifact — and I still reported numbers from
   it for a while before external review named the cause.
3. **I computed geometry from the last snapshot and presented it as general** ("1.67 cells"). Across the whole
   trajectory it was 22.45 — the random level. That is the classic late-phase artifact.
4. **I ran `X49` without first running the positive control**, although §3c of the contract demands exactly that and I
   myself had written the rule the day before.
5. **I reported wrong clock times repeatedly** — "Сейчас 01:10", "03:00" — while the actual time was around 20:00.
   I was estimating elapsed time instead of reading the system clock, and the owner had no way to know.
6. **Format errors twice in `CLAIMS`** (nine columns instead of eight; a two-character "allowed formulation"), which
   the linter caught, not me.
7. **Contract debt on three closed results** — no README line, no CLAIMS rows — discovered only when I went looking.
8. **A self-referential archive hash** (the publisher instructions containing the archive hash sat inside the archive).
9. **A duplicated deposit entry** in `docs/deposit.md`.
10. **A wrong anchor comparison** (seed 171 vs the default seed 1) which I first read as "the anchor fails".

### 4.3. The pattern behind the failures

The failures are not random. **I verify the apparatus well and the design badly.** Code, anchors, artifacts, gates,
hashes, retention — all of that I do carefully and it holds up. But the *intervention* — the thing that is supposed to
differ between arms — I designed three times without checking that it reached the dynamics, and once without checking
that the readout existed at all.

The reason is not carelessness about details; it is that I was optimising for *having an experiment running* rather than
for *having an experiment that can differ*. A run produces a comforting artifact; a design check produces nothing
visible. I chose the visible thing.

---

## 5. Proposals, in the order I would do them

### P1. A design gate before any series (highest value, small cost)

A script `scripts/check_design.py` and a one-page template that must exist before a series:
1. **Connectivity evidence**: two runs with the manipulation on and off, hashed dynamics, must differ. (This alone
   would have killed `X46` in ten minutes.)
2. **Positive control**: the arm where the effect should be strong must show it — with the observed size, not a promise.
3. **Readout exists and varies**: the variable is recorded per slice and has non-zero variance. (Would have killed
   `X49`.)
4. **Sensitivity arithmetic**: sd, effect size, seeds needed — written before the criterion.
5. **Refusal rule**: if any of 1–4 fails, the series is recorded as *insensitive by construction*, not as a null.

Cost: one script, half a day. Effect: prevents the dominant failure mode of this line — 110 wasted runs today alone.

### P2. Split `world-design.md` by line, keep a ledger

Move §10aa–§10du into `docs/line-field/` as ~10 thematic files (counts and percolation; lifetimes; selection;
habitability; self-model; channels and memory; invalid designs; methods), leaving `world-design.md` as a 200-line
index with a table: section → file → claim → artifact. Every gate that points at "§10xx" keeps working through the
index.

Cost: medium (one careful pass). Effect: the main document becomes readable and reviewable again; merge conflicts drop.

### P3. Triage the queue

64 planned items, none ever claimed. Keep ≤15 that have an owner, a cost and a trigger; move the rest to
`lab/pool.json` with a revival condition, as the contract already prescribes. A queue nobody starts is worse than no
queue, because it looks like a plan.

Cost: one hour. Effect: the queue becomes a commitment instead of a wish list.

### P4. Snapshot freshness gate

`scripts/check_snapshots.py`: compare `lab/checkpoints.json`, `lab/state.json` and `lab/registry.json` against the
filesystem and fail when a snapshot promises something absent. Add to `verify`.

Cost: two hours. Effect: the `checkpoints` 12-vs-1 class of error becomes impossible to ship.

### P5. Script index coverage gate

Fail `verify` when a `.py` in `scripts/` is absent from `docs/scripts.md`, with an explicit `legacy:` marker for the
ones we deliberately stop documenting (the 20 orphans). Then document the 101 remaining over a week.

Cost: two hours for the gate, a week of small additions. Effect: every number in the record becomes traceable to a
command.

### P6. Reports: thematic index and an archive tier

Group the 183 reports into ~8 themes with a "read these five first" section; move everything older than two weeks into
`reports/archive/` and keep the top-level index at 60 rows.

Cost: half a day. Effect: a reader can enter the project without a guide.

### P7. One canonical language, one guidance document

Declare EN canonical for articles and instructions; keep the RU edition as a translation attached to the same record,
marked "translation of vN — may lag". Delete the duplicate RU instruction and keep one EN page.

Cost: one hour. Effect: removes the drift that already caused a tombstoned deposit.

### P8. Artifact retention per line

Extend the log-archive rule to artifacts: after a line closes, keep the aggregates and the artifacts cited by claims;
pack the rest into one archive outside git and record it in the retention ledger. Cap `morphogenesis/experiments` at
~300 MB.

Cost: half a day, needs care (these are the data). Effect: the repository stays clonable.

### P9. Extend the number check to every published text

Generalise `check_article_numbers.py` into a table-driven checker over article 028 (EN/RU), the manuscript, README and
the day summaries: every number that appears in a published text must have a row binding it to an aggregate.

Cost: one day for the first pass, then a row per number. Effect: "no number without a command" becomes true rather
than aspirational.

### P10. Read the clock

Trivial, and it is a real defect: times I report must come from the system, not from my sense of elapsed work.

---

## 6. If there is one hour

**P1** (design gate) and **P3** (queue triage). They are cheap, they attack the two failure modes that cost the most
today — 110 wasted runs and a queue that never moves — and neither touches the scientific record.

## 7. What I would not change

The gates, the anchors, the claims discipline, the "write the invalidity down" habit, and the refusal to publish
without an explicit decision. Those held up under a hard day, and they are why the day's failures are written down
instead of hidden.
