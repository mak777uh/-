r"""E02b asymmetry-sides: правая половина детерминирована, левая — нет (H-AB-9).

Протокол заморожен до запуска: `reports/2026-10-22-asymmetry-sides-plan.md`.

Наблюдение из [H-AB-8]: при c=(40,24) правая половина даёт IoU 0.66-0.74
(std 0.010-0.025), левая — 0.11-0.77 (std 0.104-0.203). Здесь прямая проверка
на 24 сида на сторону: правая детерминирована (один исход), левая многовариантна.

Критерий до прогона (все три):
  1) std(body_iou) справа <= 0.05;
  2) std(body_iou) слева >= 3 * std(справа);
  3) класс struct_2 справа >= 22/24.

Запуск (из корня, через обёртку с журналом):

    python morphogenesis/run_exploratory.py \
        morphogenesis/experiments/E02b_morphospace/scripts/e02b_asymmetry_sides.py

CPU-дым (не результат):

    E02B_SIDES_STEPS=20 E02B_SIDES_REPEATS=2 E02B_SIDES_DEVICE=cpu \
    python .../e02b_asymmetry_sides.py --smoke
"""
import json
import os
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve()
EXP = HERE.parents[1]
sys.path.insert(0, str(HERE.parents[3]))
import e02b_morphospace as e02b  # noqa: E402

torch = e02b.torch
config = e02b.config
np = e02b.np

CENSUS = EXP / "census.json"
OUT = EXP / "asymmetry_sides_exploratory.json"
ROWS = EXP / "asymmetry_sides_rows.jsonl"
SMOKE_ROWS = EXP / "asymmetry_sides_smoke_rows.jsonl"
DEVICE = e02b._device_from_arg(os.environ.get("E02B_SIDES_DEVICE", "auto"))
STEPS = int(os.environ.get("E02B_SIDES_STEPS", 2000))
EVERY = 50
REPEATS = int(os.environ.get("E02B_SIDES_REPEATS", 24))
SMOKE = "--smoke" in sys.argv

DEAD_ALIVE = 0.05
IOU_MIN = 0.5
STD_RIGHT_MAX = 0.05
LEFT_TO_RIGHT = 3.0
STRUCT2_MIN_RIGHT = 22
FAMILY = "WP4_R-9_s2000_seed42"
PROTO_SEED = 35
GEOMETRY = (40, 24)

if SMOKE:
    OUT = EXP / "asymmetry_sides_smoke.json"
    ROWS = SMOKE_ROWS

census = json.load(open(CENSUS, encoding="utf-8"))
cl = census["clustering"]
mean = np.asarray(cl["scaler_mean"])
std = np.asarray(cl["scaler_std"])
valid = cl["labels_valid"]
by_cluster = {int(c): [] for c in valid}
for r in census["runs"]:
    if r.get("is_control"):
        continue
    cid = int(r["cluster"])
    if cid in by_cluster:
        by_cluster[int(cid)].append(e02b.descriptor_vector(r["final"]))
centroids = np.vstack([np.asarray(by_cluster[int(c)]).mean(axis=0) for c in valid])
centroids = (centroids - mean) / std
names = {int(c): str(n) for c, n in zip(valid, cl["class_names"], strict=True)}


def arrays(state):
    alive, binary, visible, _s, _a = e02b._state_arrays(state)
    return np.asarray(alive), np.asarray(binary), np.asarray(visible)


def classify(state):
    d = e02b.describe_state(state)
    cid = int(
        e02b.assign_to_clusters(
            e02b.descriptor_vector(d).reshape(1, -1), mean, std, centroids, valid
        )[0]
    )
    return d, cid


def iou(a, b):
    u = np.logical_or(a, b).sum()
    return float(np.logical_and(a, b).sum() / u) if u else 1.0


def build_prototype():
    spec = e02b.load_checkpoint_specs(families=[FAMILY], include_untrained=False)[0]
    final, model, _run = e02b._prototype_state(spec, PROTO_SEED, STEPS, EVERY, DEVICE)
    return model, final


def apply_cut(proto_state, side, col):
    host = proto_state.clone()
    if side == "left":
        host[:, :, :, :col] = 0.0
    else:
        host[:, :, :, col:] = 0.0
    return host


def run_rollout(model, proto_stress, host, p_seed):
    gen = config.create_deterministic_generator(p_seed)
    model.set_generator(gen)
    model.stress_ema.copy_(proto_stress)
    model._noise_cache = {}
    model._noise_seq = 0
    model.begin_segment()
    state = host
    for _ in range(STEPS):
        with torch.no_grad():
            state = model(state)
    desc, cid = classify(state)
    alive, binary, _visible = arrays(state)
    return desc, cid, alive, binary


def emit(row):
    with open(ROWS, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def side_stats(rows):
    values = [r["body_iou"] for r in rows]
    classes = Counter(r["final_class"] for r in rows)
    return {
        "n": len(rows),
        "mean_iou": round(float(np.mean(values)), 4),
        "std_iou": round(float(np.std(values, ddof=1)) if len(values) > 1 else 0.0, 4),
        "min_iou": round(float(min(values)), 4),
        "max_iou": round(float(max(values)), 4),
        "median_iou": round(float(np.median(values)), 4),
        "struct_2": classes.get("struct_2", 0),
        "class_counts": dict(classes),
        "alive": sum(1 for r in rows if r["alive_fraction"] >= DEAD_ALIVE),
        "body_returned": sum(1 for r in rows if r["body_iou"] >= IOU_MIN),
    }


def main():
    import time

    started = time.time()
    model, proto_state = build_prototype()
    try:
        _pd, proto_cid = classify(proto_state)
        proto_class = names.get(proto_cid, "outlier")
        _pa, proto_binary, _pv = arrays(proto_state)
        proto_stress = model.stress_ema.detach().clone()
        c_left, c_right = GEOMETRY
        print(
            f"[sides] прототип {proto_class}; геометрия {GEOMETRY}; "
            f"{REPEATS} сидов на сторону, {STEPS} шагов",
            flush=True,
        )
        per_side = {}
        for side, col, base in (("left", c_left, 996100), ("right", c_right, 996900)):
            rows = []
            for rep in range(REPEATS):
                host = apply_cut(proto_state, side, col)
                p_seed = base + rep
                desc, cid, alive, binary = run_rollout(model, proto_stress, host, p_seed)
                row = {
                    "section": "H-AB-9",
                    "family": FAMILY,
                    "side": side,
                    "cut_column": col,
                    "rep": rep,
                    "p_seed": p_seed,
                    "final_class": names.get(cid, "outlier"),
                    "alive_fraction": float(desc["alive_fraction"]),
                    "body_iou": iou(binary, proto_binary),
                }
                row["body_returned"] = bool(row["body_iou"] >= IOU_MIN)
                emit(row)
                rows.append(row)
            stats = side_stats(rows)
            per_side[side] = stats
            print(
                f"[sides] {side:5s}: IoU {stats['min_iou']:.3f}-{stats['max_iou']:.3f} "
                f"mean {stats['mean_iou']:.3f} std {stats['std_iou']:.3f}; "
                f"struct_2 {stats['struct_2']}/{stats['n']}; классы {stats['class_counts']}",
                flush=True,
            )

        left, right = per_side["left"], per_side["right"]
        cond1 = right["std_iou"] <= STD_RIGHT_MAX
        cond2 = left["std_iou"] >= LEFT_TO_RIGHT * right["std_iou"] if right["std_iou"] else False
        cond3 = right["struct_2"] >= STRUCT2_MIN_RIGHT
        failed = [
            name
            for name, ok in (
                ("cond1_right_std", cond1),
                ("cond2_left_vs_right_std", cond2),
                ("cond3_right_struct2", cond3),
            )
            if not ok
        ]
        payload = {
            "schema_version": 1,
            "experiment": "E02b_morphospace",
            "kind": "exploratory_asymmetry_sides",
            "protocol": "reports/2026-10-22-asymmetry-sides-plan.md",
            "family": FAMILY,
            "proto_seed": PROTO_SEED,
            "proto_class": proto_class,
            "geometry": list(GEOMETRY),
            "steps": STEPS,
            "repeats_per_side": REPEATS,
            "criterion": (
                f"std(right) <= {STD_RIGHT_MAX}; std(left) >= {LEFT_TO_RIGHT} * std(right); "
                f"struct_2 справа >= {STRUCT2_MIN_RIGHT}/{REPEATS}"
            ),
            "sides": per_side,
            "conditions": {
                "cond1_right_std": cond1,
                "cond2_left_vs_right_std": cond2,
                "cond3_right_struct2": cond3,
            },
            "failed_conditions": failed,
            "verdict": "H-AB-9_confirmed" if not failed else "H-AB-9_refuted",
            "wall_seconds": round(time.time() - started, 1),
        }
        OUT.write_text(
            json.dumps(payload if not SMOKE else {"smoke": True, **payload}, ensure_ascii=False, indent=2)
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(
            f"[sides] условия: {payload['conditions']} -> {payload['verdict']}",
            flush=True,
        )
        print(f"[sides] записано: {OUT} ({payload['wall_seconds']} c)", flush=True)
        return 0
    finally:
        del model


if __name__ == "__main__":
    raise SystemExit(main())
