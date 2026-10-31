# Retention policy: artifacts, logs and weights

Written 31.10.2026 at the owner's request, as improvement **P8** of the repository analysis. This is a **policy**, not a
cleanup: nothing here has been deleted, and no deletion happens without a record in `lab/retention.json`.

The problem it answers: `morphogenesis/experiments` is **615 MB** and grows 50–100 MB on a busy day; `.git` is 214 MB.
At that rate the repository stops being clonable within weeks, and the first thing to go is usually the thing nobody
decided about.

---

## 1. What must stay in git, always

| kind | why |
|---|---|
| **aggregates** (`*_matrix.json`, `*_summary.json`, `lifetime*`, `ghost_matrix`) | the numbers in articles are recomputed from them |
| **artifacts cited by a claim** — every `artifact` field in `lab/claims/*.json` and every path in `manuscript/CLAIMS.md` | a claim without its artifact cannot be checked |
| **artifacts behind a published number** — anything referenced by an article or the manuscript | the deposit must be re-derivable |
| **registry, queue, runs, retention, state** | the machine contour |

A file in this list is never a deletion candidate, whatever its size.

## 2. What may be archived outside git after a line closes

- raw per-run artifacts of a closed line that are **not** cited by a claim and not behind a published number;
- intermediate probe outputs and pilots (`tmp_*`, parameter sweeps used to choose a setting).

Procedure — the same one used for the logs on 31.10, which is why it is written down:

1. pack into one archive under `_exports/`, named by family and month;
2. **verify the archive file by file against the disk** (count and names), never by size alone;
3. write one entry into `lab/retention.json`: path family, byte count, mtime, reason, `archived_to`;
4. only then delete the originals;
5. the aggregates and the cited artifacts stay.

## 3. Weights

Rule of the contract (§5a) already: only canonical `nca_final.pt` files listed in `lab/checkpoints.json` for an active
or next series, plus one explicitly declared positive control. Everything else is consumable.

**Current state, as measured on 31.10:** the manifest requires 12 canonical weights and the disk holds **one**
(`WP4_R-9_s2000_seed42`, 515 MB). The other eleven are either lost or never restored; this is booked as `X54` and waits
for the owner's decision between restoring the 6.47 GB set from the Zenodo deposit and recording the loss. **Nothing is
deleted while that decision is open.**

## 4. Logs

- stdout of closed runs: packed and removed (done 31.10 — 1253 files, 144.6 MB, verified, recorded);
- TensorBoard event files: kept, they are 2 MB in total and cost nothing;
- `morphogenesis/logs/journal.jsonl`: append-only, never touched.

## 5. Targets

| area | now | target | when |
|---|---|---|---|
| `morphogenesis/experiments` | 615 MB | ≤ 300 MB | after the next line closes |
| `dashboard`-style archives in `_exports` | 29 MB | keep ≤ 2 recent | monthly |
| `.git` | 214 MB | not addressed | history is not rewritten; growth is bounded by the artifact policy instead |

## 6. Machine check

`scripts/check_cited_artifacts.py` (proposed, not yet written) should fail when an artifact cited by a claim is missing
from git. Until it exists, the check is manual: before any archival, run
`python scripts/aggregate_check.py --strict` and grep `manuscript/CLAIMS.md` for the family being archived.
