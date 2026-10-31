# Publisher instructions: the correction release of 1 November

Written 1 November 2026. Short page for whoever uploads. The laboratory-side reasoning is in
`reports/2026-10-31-v1.6-required-changes.md` (why the text changed) and `docs/deposit.md` (the deposit map).

---

## 0. What this version is, in one paragraph

The release of 31 October (DOI `10.5281/zenodo.23844978`) is published and correct. Three tests run on 31 October **qualified its main
number**: the heterogeneity contrast is not a steady-state doubling, it is a time integral that includes an early
transient, its magnitude depends on the time step (+3.57 at `dt = 1.0`, +1.24 at `dt = 0.5`), and the grid comparison in
the paper was never a refinement test. One sentence in §4.5 of the published text — "a steady state, not a transient" —
is now known to be wrong and is replaced.

This is a **correction of our own claim**, not a new paper. Everything else stays.

## 1. What to upload — three files

| file | what it is |
|---|---|
| `articles/028-field-without-stipulated-objects.md` | **English edition, v1.6** — the primary text, with the corrections |
| `articles/028-pole-bez-zadannyh-obektov.md` | Russian edition, v1.4 with the v1.6 qualification inserted |
| `_exports/logs-2026-11-01.zip` | data and code: 1745 files, 3 740 739 bytes |

**Archive checksum (must match):**

```
sha256 content hash: 3dcf860ab57b54f7a7a730f3ec3efdd1391e1df88b2de229fa3b2e578a3e31dd
```

Verify with:

```
python scripts/make_logs_bundle.py --verify logs-2026-11-01.zip
# expected: files 1745, broken 0, missing 0, content hash matches: True
```

The archive already contains the v1.6 article — checked inside the zip, not assumed.

## 2. How: a new version of the existing record

1. Open `https://zenodo.org/records/23839898`.
2. Press **New version** — this keeps the concept DOI `10.5281/zenodo.23839897` and the link to `10.5281/zenodo.23669737`.
3. Remove the three old files, upload the three from §1.
4. **Version number:** as in the article header — `1.6`. **Publication date:** `2026-11-01`.
5. Type: **Preprint**. Language: **English**.
6. License: **CC0 1.0** (unchanged).
7. Related identifier `10.5281/zenodo.23669737` (`isSupplementTo`) — keep.
8. Preview, then **save as draft** and show the owner before publishing.

## 3. Metadata (copy as is)

**Title:**
`A field without stipulated objects: how a component counter passed itself off as diversity`

**Author:** Vladimirov, Ilia Sergeevich (Владимиров Илья Сергеевич)

**Description:**

> Organisation in a digital medium, and its boundaries. In a continuous medium with no stipulated objects (the
> Gray–Scott model) organisation arises, inheritance and selection are measurable, but the number of "structures" turns
> out to measure the fraying of a single percolation cluster rather than a number of bodies. This version corrects our own
> main number: the heterogeneity contrast is not a steady-state doubling but a time integral that includes an early
> transient, and its magnitude depends on the numerical scheme — +3.57 components at `dt = 1.0`, +1.24 at `dt = 0.5`, with
> a plateau of +1.00 and 0.00 respectively. The grid comparison reported in earlier versions is relabelled as a change of
> scale, because in this model family resolution enters as a `1/Δx²` coefficient on diffusion. Unchanged and still
> standing: durable structures are equal in heterogeneous and homogeneous worlds (1.3 versus 1.2); form does not transfer
> (8–11 % keep their class, 50–67 % die) and no measured property predicts survival; the earlier nulls came from a world
> uninhabitable by a constant (income ceiling 0.008 against cost 0.03, break-even `b = 0.0075`), and in a habitable world
> a self-model evolves — confirmed by an intervention that severs the organism's action on the resource (+0.0362 in ten of
> ten runs falls to 0.0000 in none of eight). Seven of our own conclusions are retracted, two weakened, two rewritten, and
> now one number qualified by three tests. Every number is recomputed from its aggregate by a script in the archive.
> English edition of v1.4; the Russian original is included.

**Keywords:**
`artificial life; reaction-diffusion; Gray-Scott; percolation; individuality; selection; habitability; mutual information; discretisation; non-Platonic; reproducibility; negative results`

**Version note (Zenodo "Notes" field, optional but useful):**

> v1.6 corrects a sentence in §4.5 of v1.5.1 that described the heterogeneity contrast as a steady state. It is not: the
> contrast decays to a plateau and depends on the time step. See §10dv–§10dz of the line plan in the archive.

## 4. What changed since 1.5.1 — for the changelog line

| section | change |
|---|---|
| §4.5 | "roughly twice, and this is stable" → "larger, but the size belongs to the scheme and is not stationary", with the three qualifications and their numbers |
| §4.7 | the 128-grid result relabelled: a change of scale, not a refinement |
| §3.1 | added: grid 96 sits below the range tested by Pearson (1993), who checked `dt` 1.0→0.01 and grids 256–1024 |
| abstract | one sentence on the step dependence |
| Russian edition | same qualification inserted, so the two editions cannot drift |

## 5. Do not

- do not create a new record — this is a **new version** of `23839898`;
- do not change the license;
- do not modify the archive after upload;
- do not remove the Russian edition;
- do not publish without the owner's explicit "ok" — this is a correction of a published claim and he signs it.

## 6. Send back

1. The **version DOI** of v1.6.
2. The link.
3. Confirmation that three files are present and the license is CC0.

We will then put the DOI into `CITATION.cff`, both articles, `docs/deposit.md` and the README.
