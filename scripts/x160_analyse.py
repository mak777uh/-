"""x160_analyse.py — X160: does a mortality buffer on an external signal hold diversity?

Reads the per-run artifacts of the three arms and compares clonal_fraction and survival at the end of the run, with the
const arm as the null. Refuses to report if the active arms never fired the buffer.

Writes morphogenesis/experiments/E09_pond/x160_memory/x160_memory.json (the aggregate the runner also writes; this script
rebuilds it with the analysis block).
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "x160_memory"
ARMS = ("const", "real", "surrogate")
TAU = 300


def load(arm: str) -> list[dict]:
    rows = []
    for f in sorted(DIR.glob(f"x160_{arm}_t{TAU}_s*.json")):
        if "_stream_" in f.name:
            continue
        art = json.loads(f.read_text(encoding="utf-8"))
        s = art.get("summary") or {}
        fin = s.get("final") or {}
        rows.append({
            "seed": s.get("seed", f.stem),
            "alive": fin.get("alive_cells"),
            "clonal": s.get("clonal_fraction"),
            "kills": s.get("killed_by_memory", 0),
            "calls": s.get("memory_calls", 0),
            "dev": s.get("memory_dev_mean"),
            "prob": s.get("memory_prob_mean"),
            "pop_time": s.get("pop_time"),
        })
    return rows


def summarise(rows: list[dict]) -> dict:
    clonal = [r["clonal"] for r in rows if r["clonal"] is not None]
    alive = [r["alive"] or 0 for r in rows]
    return {
        "runs": len(rows),
        "survived": sum(1 for a in alive if a > 0),
        "alive_median": statistics.median(alive) if alive else None,
        "clonal_median": statistics.median(clonal) if clonal else None,
        "clonal_mean": round(statistics.fmean(clonal), 4) if clonal else None,
        "clonal_n": len(clonal),
        "kills_total": sum(r["kills"] or 0 for r in rows),
        "calls_total": sum(r["calls"] or 0 for r in rows),
        "dev_mean": round(statistics.fmean([r["dev"] for r in rows if r["dev"] is not None]), 4)
        if any(r["dev"] is not None for r in rows) else None,
    }


def main() -> int:
    by_arm = {arm: summarise(load(arm)) for arm in ARMS}
    base = by_arm["const"]
    for arm in ("real", "surrogate"):
        a = by_arm[arm]
        a["clonal_gain"] = (round((a["clonal_mean"] or 0) - (base["clonal_mean"] or 0), 4)
                            if a["clonal_mean"] is not None and base["clonal_mean"] is not None else None)
    fired = by_arm["real"]["kills_total"] > 0 and by_arm["surrogate"]["kills_total"] > 0
    gains = [by_arm["real"].get("clonal_gain"), by_arm["surrogate"].get("clonal_gain")]
    if not fired:
        verdict = ("NOT REPORTABLE: the buffer never killed a cell in the active arms, so the manipulation did not reach "
                   "the dynamics.")
    elif any(g is not None and g > 0.05 for g in gains):
        verdict = ("THE BUFFER HOLDS DIVERSITY: at least one active arm keeps clonal_fraction above the const null by more "
                   f"than 0.05 ({gains[0]} real, {gains[1]} surrogate).")
    else:
        verdict = ("THE BUFFER DOES NOT HOLD DIVERSITY: with the buffer firing, the active arms finish at or below the "
                   f"const null (clonal gain {gains[0]} real, {gains[1]} surrogate), so the signal's structure does not "
                   "rescue diversity through mortality.")
    agg = {"kind": "x160_mortality_buffer", "tau": TAU, "arms": by_arm,
           "controls": {"buffer_fired": fired},
           "verdict": verdict}
    p = DIR / "x160_memory.json"
    old = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    old["analysis"] = agg
    p.write_text(json.dumps(old, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    for arm, s in by_arm.items():
        print(f"[x160] {arm:9s} runs {s['runs']} survived {s['survived']} alive_med {s['alive_median']} "
              f"clonal {s['clonal_mean']} kills {s['kills_total']} dev {s['dev_mean']} gain {s.get('clonal_gain')}")
    print(f"[x160] verdict: {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
