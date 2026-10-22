r"""E02b left-outcomes: дискретны ли левые исходы восстановления (H-AB-10).

Протокол заморожен до запуска: `reports/2026-10-22-left-outcomes-plan.md`.

H-AB-8: левая половина при c=(40,24) даёт IoU 0.11-0.77, правая 0.66-0.74.
Здесь проверяется форма распределения левых исходов: 60 сидов слева и 24 справа.

Критерий до прогона: подтверждена, если в гистограмме body_iou левой стороны
(20 бинов на [0,1]) найдутся два локальных максимума с бином-провалом между ними
(счёт <= 50% меньшего максимума) и оба максимума содержат >= 6 развёрток;
опровергнута иначе.

Запуск (из корня, через обёртку с журналом):

    python morphogenesis/run_exploratory.py \
        morphogenesis/experiments/E02b_morphospace/scripts/e02b_left_outcomes.py

CPU-дым (не результат):

    E02B_LEFT_STEPS=20 E02B_LEFT_REPEATS=3 E02B_LEFT_DEVICE=cpu \
    python .../e02b_left_outcomes.py --smoke
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
OUT = EXP / "left_outcomes_exploratory.json"
ROWS = EXP / "left_outcomes_rows.jsonl"
SMOKE_ROWS = EXP / "left_outcomes_smoke_rows.jsonl"
DEVICE = e02b._device_from_arg(os.environ.get("E02B_LEFT_DEVICE", "auto"))
STEPS = int(os.environ.get("E02B_LEFT_STEPS", 2000))
EVERY = 50
LEFT_REPEATS = int(os.environ.get("E02B_LEFT_REPEATS", 60))
RIGHT_REPEATS = max(2, LEFT_REPEATS // 2 - 6)
SMOKE = "--smoke" in sys.argv

DEAD_ALIVE = 0.05
IOU_MIN = 0.5
BINS = 20
PEAK_MIN = 6
TROUGH_RATIO = 0.5
FAMILY = "WP4_R-9_s2000_seed42"
PROTO_SEED = 35
GEOMETRY = (40, 24)

if SMOKE:
    OUT = EXP / "left_outcomes_smoke.json"
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


def histogram(values, bins=BINS):
    edges = np.linspace(0.0, 1.0, bins + 1)
    counts, _ = np.histogram(values, bins=edges)
    return [int(x) for x in counts], [round(float(x), 4) for x in edges]


def find_trough(counts, peak_min=PEAK_MIN, ratio=TROUGH_RATIO):
    """Два локальных максимума с провалом между ними (формальное правило)."""
    peaks = [
        i
        for i in range(1, len(counts) - 1)
        if counts[i] > counts[i - 1] and counts[i] > counts[i + 1] and counts[i] >= peak_min
    ]
    for a_idx in range(len(peaks)):
        for b_idx in range(a_idx + 1, len(peaks)):
            a, b = peaks[a_idx], peaks[b_idx]
            if b - a < 2:
                continue
            between = counts[a + 1 : b]
            trough = min(between) if between else None
            if trough is not None and trough <= ratio * min(counts[a], counts[b]):
                return {
                    "peak_bins": [a, b],
                    "peak_counts": [counts[a], counts[b]],
                    "trough_bin": a + 1 + int(np.argmin(between)),
                    "trough_count": int(trough),
                }
    return None


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
            f"[left] прототип {proto_class}; {LEFT_REPEATS} сидов слева, "
            f"{RIGHT_REPEATS} справа, {STEPS} шагов",
            flush=True,
        )
        per_side = {}
        for side, col, count, base in (
            ("left", c_left, LEFT_REPEATS, 998000),
            ("right", c_right, RIGHT_REPEATS, 998900),
        ):
            rows = []
            for rep in range(count):
                host = apply_cut(proto_state, side, col)
                p_seed = base + rep
                desc, cid, alive, binary = run_rollout(model, proto_stress, host, p_seed)
                row = {
                    "section": "H-AB-10",
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
            values = [r["body_iou"] for r in rows]
            classes = Counter(r["final_class"] for r in rows)
            per_side[side] = {
                "n": len(values),
                "mean_iou": round(float(np.mean(values)), 4),
                "std_iou": round(float(np.std(values, ddof=1)) if len(values) > 1 else 0.0, 4),
                "min_iou": round(float(min(values)), 4),
                "max_iou": round(float(max(values)), 4),
                "struct_2": classes.get("struct_2", 0),
                "class_counts": dict(classes),
                "body_returned": sum(1 for r in rows if r["body_returned"]),
                "histogram": histogram(values)[0],
            }
            print(
                f"[left] {side:5s}: IoU {per_side[side]['min_iou']:.3f}-{per_side[side]['max_iou']:.3f}, "
                f"std {per_side[side]['std_iou']:.3f}, struct_2 {per_side[side]['struct_2']}/{len(values)}",
                flush=True,
            )
            print(f"[left] {side:5s} hist {per_side[side]['histogram']}", flush=True)

        # Гистограмма левой стороны уже посчитана и лежит в per_side.
        left_hist = per_side["left"]["histogram"]
        edges = [round(float(x), 4) for x in np.linspace(0.0, 1.0, BINS + 1)]
        trough = find_trough(left_hist)
        verdict = "H-AB-10_confirmed" if trough else "H-AB-10_refuted"

        payload = {
            "schema_version": 1,
            "experiment": "E02b_morphospace",
            "kind": "exploratory_left_outcomes",
            "protocol": "reports/2026-10-22-left-outcomes-plan.md",
            "family": FAMILY,
            "proto_seed": PROTO_SEED,
            "proto_class": proto_class,
            "geometry": list(GEOMETRY),
            "steps": STEPS,
            "bins": BINS,
            "criterion": (
                f"два пика >= {PEAK_MIN} с провалом <= {TROUGH_RATIO:g} меньшего пика "
                "между ними"
            ),
            "sides": per_side,
            "left_histogram_edges": edges,
            "trough": trough,
            "verdict": verdict,
            "wall_seconds": round(time.time() - started, 1),
        }
        OUT.write_text(
            json.dumps(payload if not SMOKE else {"smoke": True, **payload}, ensure_ascii=False, indent=2)
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(f"[left] провал: {trough} -> {verdict}", flush=True)
        print(f"[left] записано: {OUT} ({payload['wall_seconds']} c)", flush=True)
        return 0
    finally:
        del model


if __name__ == "__main__":
    raise SystemExit(main())
