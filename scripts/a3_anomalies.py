"""A3: find ANOMALIES in the corpus - series whose results depart from their peers.

For every artifact that carries a numeric outcome, this script groups artifacts by their `kind`
(so only comparable series are compared), computes the distribution of the outcome across the group,
and flags artifacts whose mean outcome lies far from the group median.

Two kinds of departure are reported:

  - `far`    : |mean - group median| > 3 x MAD (a robust z-score), i.e. the series behaves unlike its
               peers. This is either a real effect or a design bug - both worth seeing;
  - `single` : an artifact that is the ONLY one of its kind, so it cannot be compared at all (a
               coverage gap rather than an anomaly).

Read-only.
"""
from __future__ import annotations
import json
import pathlib
import statistics
import sys
from collections import defaultdict

REPO = pathlib.Path(__file__).resolve().parents[1]
POND = REPO / "morphogenesis" / "experiments" / "E09_pond"


def outcome_of(data):
    """A single comparable number per artifact: mean of the per-row outcome field."""
    rows = data.get("rows") or []
    vals = []
    for r in rows:
        if not isinstance(r, dict):
            continue
        for key in ("overall", "correct_share", "favourable_share", "alive_final",
                    "correct_share_after", "after_flip"):
            v = r.get(key)
            if isinstance(v, (int, float)):
                vals.append(float(v))
                break
    if not vals:
        s = data.get("summary")
        if isinstance(s, dict):
            for key in ("overall", "correct_share", "favourable_share"):
                v = s.get(key)
                if isinstance(v, (int, float)):
                    vals.append(float(v))
    return (sum(vals) / len(vals)) if vals else None


def main(argv=None) -> int:
    groups = defaultdict(list)
    for path in sorted(POND.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        kind = data.get("kind")
        if not kind:
            continue
        val = outcome_of(data)
        if val is None:
            continue
        groups[kind].append((path.name, val))

    print(f"[a3] kinds with a comparable outcome: {len(groups)}")
    anomalies, singletons = [], []
    for kind, items in sorted(groups.items()):
        if len(items) < 3:
            singletons.append((kind, [n for n, _ in items]))
            continue
        vals = [v for _, v in items]
        med = statistics.median(vals)
        mad = statistics.median([abs(v - med) for v in vals]) or 1e-9
        for name, v in items:
            z = (v - med) / (1.4826 * mad)
            if abs(z) > 3.0:
                anomalies.append({"kind": kind, "file": name, "value": round(v, 4),
                                  "group_median": round(med, 4), "robust_z": round(z, 2),
                                  "group_size": len(items)})

    print(f"[a3] anomalies (|robust z| > 3): {len(anomalies)}")
    for a in sorted(anomalies, key=lambda x: -abs(x["robust_z"]))[:20]:
        print(f"   {a['file']:44s} {a['value']:.3f} vs median {a['group_median']:.3f} "
              f"(z {a['robust_z']:+.1f}, n={a['group_size']}) [{a['kind']}]")

    print(f"\n[a3] kinds with fewer than 3 comparable artifacts (coverage gaps): {len(singletons)}")
    for kind, names in singletons[:15]:
        print(f"   {kind}: {names}")

    out = {"kind": "a3_anomalies", "anomalies": anomalies,
           "singletons": [{"kind": k, "files": n} for k, n in singletons],
           "groups": {k: len(v) for k, v in groups.items()}}
    with open(POND / "a3_anomalies.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(f"\n[a3] written {POND / 'a3_anomalies.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
