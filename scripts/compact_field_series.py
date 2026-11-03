"""compact_field_series.py — keep the derivable part of a dense-logging series in git.

Dense logging (`--sample-every 10`) costs ~2.4 MB per run against ~1 MB for the 50-step series, because every logged step carries its
component list. Twenty runs are 49 MB, and the repository's rule is that GitHub is thin memory, not storage. Every analysis in this
line reads exactly five things from a run: `params`, `uid_pairs`, and per logged step the components' `uid`/`area`/`cx`/`cy`. This
script writes that projection next to the run and leaves the full log on the lab machine, with the source's sha256 in the header so a
reader can tell the derivative from the original.

The saved fields (`_x105_fields/*.npy`) are not committed either, exactly as for `_x100_fields`; analyses that need them (X101/X102)
are re-run locally, which the aggregate records.

    python scripts/compact_field_series.py --pattern "x105_*.json" --write
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"

KEEP_PARAMS = ("F", "seed", "steps", "grid", "dt", "Du", "Dv", "k", "eps", "hetero_scale", "hetero_period", "hetero_amp",
               "sample_every", "threshold", "freq_dep", "beta", "s_ref", "mutation", "overlap", "split_new_uid",
               "init_pattern_cells", "init_pattern_fill", "init_pattern_binary")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def compact(path: Path, keep_extra: tuple[str, ...] = ()) -> dict:
    d = json.loads(path.read_text(encoding="utf-8"))
    params = d.get("params") or {}
    series = []
    for row in d.get("series") or []:
        if keep_extra:
            comps = []
            for c in (row.get("components_log") or []):
                item = {"uid": int(c["uid"]), "area": c.get("area"),
                        "cx": None if c.get("cx") is None else round(float(c["cx"]), 1),
                        "cy": None if c.get("cy") is None else round(float(c["cy"]), 1)}
                for key in keep_extra:
                    if key in c:
                        item[key] = None if c[key] is None else round(float(c[key]), 4)
                comps.append(item)
        else:
            comps = [[int(c["uid"]), c.get("area"),
                      None if c.get("cx") is None else round(float(c["cx"]), 1),
                      None if c.get("cy") is None else round(float(c["cy"]), 1)]
                     for c in (row.get("components_log") or [])]
        series.append([int(row.get("step") or 0), comps])
    return {
        "kind": "l1_field_run_compact",
        "model": d.get("model"),
        "source": path.name,
        "source_sha256": sha256(path),
        "note": ("projection of the full run: params, uid_pairs and per logged step "
                 + ("[uid, area, cx, cy" + "".join(f", {k}" for k in keep_extra) + "] as objects"
                    if keep_extra else "[uid, area, cx, cy]")
                 + " with positions rounded to 0.1 cell. Everything the field line's log-only analyses read is here; the "
                 "full log and the saved fields stay on the lab machine."),
        "params": {k: params[k] for k in KEEP_PARAMS if k in params},
        "uid_pairs": d.get("uid_pairs") or [],
        "series": series,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="compact a dense-logging series for git")
    ap.add_argument("--pattern", default="x105_*.json")
    ap.add_argument("--keep-dicts", default="",
                    help="comma-separated extra component keys to keep, with the components left as objects "
                         "(needed by a series whose analysis reads a computed shape)")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    files = sorted(p for p in L1.glob(args.pattern) if not p.name.endswith(".compact.json")
                   and "series_index" not in p.name)
    keep_extra = tuple(k.strip() for k in args.keep_dicts.split(",") if k.strip())
    written = 0
    for path in files:
        out = path.with_name(path.stem + ".compact.json")
        payload = compact(path, keep_extra)
        size = len(json.dumps(payload, ensure_ascii=False))
        if args.write:
            out.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
            written += 1
        print(f"{path.name}: {path.stat().st_size / 1e6:.2f} MB -> {size / 1e6:.2f} MB ({size / path.stat().st_size:.0%})")
    if args.write:
        print(f"[compact] written {written} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
