"""Независимая проверка артефактов E02b после переписи (без доверия harness-полям)."""
import json
import math
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve()
EXP = HERE.parents[1]
ROOT = HERE.parents[4]
CENSUS = EXP / "census.json"
PERT = EXP / "perturbations.json"
INDEX = ROOT / "lab" / "checkpoints.json"

errors = []
warnings = []


def check(cond, msg):
    if cond:
        print("OK  ", msg)
    else:
        print("FAIL", msg)
        errors.append(msg)


def finite(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            finite(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            finite(v, f"{path}[{i}]")
    elif isinstance(obj, float) and not math.isfinite(obj):
        errors.append(f"nonfinite {path} = {obj!r}")


census = json.load(open(CENSUS, encoding="utf-8"))
pert = json.load(open(PERT, encoding="utf-8"))
index = json.load(open(INDEX, encoding="utf-8"))

families = [c["family"] for c in census["checkpoints"]]
runs = census["runs"]
check(census.get("full_protocol") is True, "full_protocol=true")
check(census.get("hypotheses_evaluated") is True, "hypotheses_evaluated=true")
check(census.get("seeds") == list(range(64)), "seeds=0..63")
check(census.get("steps") == 2000 and census.get("snapshot_every") == 50, "steps=2000, every=50")
check(str(census.get("device")).startswith("cuda"), f"device={census.get('device')}")
check(len(families) == 13, f"13 чекпоинтов (12 канон + untrained): {len(families)}")
check(len(runs) == 13 * 64, f"13x64=832 прогона: {len(runs)}")
finite(census)

by_family = defaultdict(list)
for r in runs:
    by_family[r["family"]].append(r)
check(set(by_family) == set(families), "все семейства присутствуют в runs")
for fam, rs in by_family.items():
    check(len(rs) == 64, f"{fam}: 64 прогона")
    check(sorted(r["seed"] for r in rs) == list(range(64)), f"{fam}: сиды 0..63")
    for r in rs:
        steps = [p["step"] for p in r["trajectory"]]
        ok_steps = steps == list(range(50, 2001, 50))
        if not ok_steps:
            errors.append(f"{fam} seed {r['seed']}: траектория {steps[:3]}..{steps[-3:]}")
    check(all(r["is_control"] is False for r in rs), f"{fam}: не контроль") if fam not in (
        "WP4_H-P1_s2000_seed42",
        "untrained_current_arch",
    ) else check(all(r["is_control"] is True for r in rs), f"{fam}: контроль помечен")

# sha256 из lab/checkpoints.json
index_by_family = {e["family"]: e for e in index["entries"] if e.get("kind") == "final"}
for c in census["checkpoints"]:
    if c["family"] == "untrained_current_arch":
        check(c["path"] is None and c["sha256"] is None, "untrained без файла и sha")
        continue
    e = index_by_family.get(c["family"])
    check(e is not None, f"{c['family']}: есть в индексе")
    if e:
        check(c["sha256"] == e.get("sha256"), f"{c['family']}: sha совпадает")

controls = [r for r in runs if r["is_control"]]
check(len(controls) == 2 * 64, f"контролей 128: {len(controls)}")

# Кластеризация: все прогоны получили метку; контроли не среди «обученных» классов
cl = census["clustering"]
check(cl is not None and cl.get("k", 0) >= 1, f"Ward k={cl.get('k') if cl else None}")
valid = set(cl["labels_valid"]) if cl else set()
for r in runs:
    if r["cluster"] not in valid and r["cluster"] != -1:
        errors.append(f"метка {r['cluster']} вне labels_valid у {r['family']} seed {r['seed']}")
check(not errors, "все метки кластеров корректны")
for r in controls:
    if r["cluster"] == -1:
        warnings.append(f"контроль {r['family']} seed {r['seed']} — выброс")

# H1 независимо: >=80% сидов семейства в одном структурном классе,
# устойчивость >=0.8, медиана alive 0.05..0.80, класс не смерть/однородность
h1_expected = []
struct_max_expected = {}
for fam in families:
    if fam in ("WP4_H-P1_s2000_seed42", "untrained_current_arch"):
        continue
    group = by_family[fam]
    for cid in sorted({r["cluster"] for r in group if r["cluster"] >= 0}):
        members = [r for r in group if r["cluster"] == cid]
        sem = members[0]["semantic"]
        if sem != "structured":
            continue
        frac = len(members) / len(group)
        stable = sum(1 for r in members if r["stability_last_quarter"] >= 0.8) / len(members)
        alive = sorted(r["final"]["alive_fraction"] for r in members)
        med = alive[len(alive) // 2] if len(alive) % 2 else 0.5 * (alive[len(alive) // 2 - 1] + alive[len(alive) // 2])
        struct_max_expected[fam] = max(struct_max_expected.get(fam, 0.0), frac)
        if frac >= 0.8 and stable >= 0.8 and 0.05 <= med <= 0.80:
            h1_expected.append((fam, cid, round(frac, 4), round(stable, 4), round(med, 4)))
h1 = census["hypotheses"]["H1"]
check(len(h1["candidates"]) == len(h1_expected), f"H1 candidates={len(h1['candidates'])} (ожидалось {len(h1_expected)})")
got = sorted((c["family"], c["cluster"], round(c["fraction_of_starts"], 4), round(c["stable_fraction"], 4), round(c["alive_fraction_median"], 4)) for c in h1["candidates"])
check(got == sorted(h1_expected), f"H1 candidates совпадают: {h1_expected}")
check(h1["evaluated_runs"] == 11 * 64, f"H1 evaluated_runs={h1['evaluated_runs']} (ожидалось 704)")

# смерть/однородность
analysis = [r for r in runs if not r["is_control"]]
death = [r for r in analysis if r["semantic"] in ("death", "uniform_dark", "uniform_bright")]
check(h1["death_or_uniform_fraction"] == len(death) / len(analysis), "доля death/uniform сходится")
check(abs(len(death) / len(analysis) - h1["death_or_uniform_fraction"]) < 1e-12, "death fraction точна")

# H2 независимо
r11 = [r for r in runs if r["family"].startswith("WP4_R-11")]
structural = set(census["structural_labels"])
final_death = sum(1 for r in r11 if r["semantic"] in ("death", "uniform_dark", "uniform_bright"))
any_struct = sum(1 for r in r11 if any(v in structural for v in r["trajectory_cluster"]))
if final_death / len(r11) >= 0.8 and any_struct / len(r11) >= 0.5:
    st = "supported"
elif final_death / len(r11) <= 0.2:
    st = "refuted"
else:
    st = "mixed"
check(census["hypotheses"]["H2"]["status"] == st, f"H2 status={st}")

# H3 независимо
rows20 = [o for o in pert["outcomes"] if o.get("perturbation") == "amputation" and abs(float(o.get("fraction", 0)) - 0.2) < 1e-9]
h3 = pert["h3"]
check(len(pert["outcomes"]) == 30 * len(pert["prototypes"]), f"возмущений {len(pert['outcomes'])} = 30×{len(pert['prototypes'])}")
check(len(rows20) == 5 * len(pert["prototypes"]), f"ампутаций 20% {len(rows20)}")
by_cls = defaultdict(list)
for o in rows20:
    by_cls[o["cluster"]].append(o)
for cid, rows in by_cls.items():
    rec = sum(1 for o in rows if o.get("returned_same_class")) / len(rows)
    check(abs(h3["by_class"][str(cid)]["recovery_fraction"] - rec) < 1e-12, f"H3 класс {cid} recovery={rec:.3f}")
check(all(len(by_cls[cid]) == 15 for cid in by_cls), "H3 по 15 повторов на класс")
check(all(p["family"] != "untrained_current_arch" for p in pert["prototypes"]), "untrained не прототип")
check(all(p["family"] != "WP4_H-P1_s2000_seed42" for p in pert["prototypes"]), "H-P1 не прототип")

# outcome
out = census["outcome"]
max_repro = max(h1["struct_max_fraction_by_family"].values(), default=0.0)
max_rec = h3.get("max_recovery_fraction") if h3.get("by_class") else None
if len(death) / len(analysis) >= 0.95:
    exp = "empty_map"
elif max_rec is not None and max_rec >= 0.5 and len(structural) >= 2 and max_repro >= 0.8:
    exp = "rich_map"
elif max_repro >= 0.8 and max_rec is not None and max_rec < 0.2:
    exp = "geometry_without_life"
else:
    exp = "mixed"
check(out["outcome"] == exp, f"outcome={exp}")

print("\n=== СВОДКА ===")
print("families", len(families), "runs", len(runs), "controls", len(controls))
print("clusters", cl["k"], "sizes", cl["sizes"], "silhouette", cl.get("silhouette"), "dbscan_ari", cl["dbscan"].get("ari_vs_ward"))
print("death/uniform", len(death), "/", len(analysis), "=", round(len(death) / len(analysis), 3))
print("struct_max", {k: round(v, 3) for k, v in h1["struct_max_fraction_by_family"].items()})
print("H1", h1["supported"], h1["refuted"], "H2", census["hypotheses"]["H2"]["status"])
print("H3", {k: (v["n"], round(v["recovery_fraction"], 3)) for k, v in h3.get("by_class", {}).items()})
print("outcome", out["outcome"], "|", out["reason"])
print("errors", len(errors), "warnings", len(warnings))
for w in warnings[:10]:
    print("WARN", w)
