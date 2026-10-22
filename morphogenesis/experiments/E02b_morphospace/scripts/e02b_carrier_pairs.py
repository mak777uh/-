r"""E02b carrier-pairs: достаточна ли любая пара каналов внутри носителя (H-CH-12).

Протокол заморожен до запуска: `reports/2026-10-22-carrier-pairs-plan.md`.

Информативный набор {2,3,4,10,11,12,13,14} (H-CH-10) даёт 28 пар. H-CH-9
проверила три из них ({2,3}, {11,12}, {13,14}) — все 12/12. Здесь все 28:
оставить только два канала пары, остальное обнулить, 12 сидов на пару.

Критерий до прогона: подтверждена, если ВСЕ 28 пар дают тело >= 11/12 при
воспроизведении трёх контролей (12/12); опровергнута, если хоть одна пара
<= 10/12; недействительно, если контроль < 12/12.

Запуск (из корня, через обёртку с журналом):

    python morphogenesis/run_exploratory.py \
        morphogenesis/experiments/E02b_morphospace/scripts/e02b_carrier_pairs.py

CPU-дым (не результат):

    E02B_PAIRS_STEPS=20 E02B_PAIRS_REPEATS=1 E02B_PAIRS_DEVICE=cpu \
    python .../e02b_carrier_pairs.py --smoke
"""
import json
import os
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve()
EXP = HERE.parents[1]
sys.path.insert(0, str(HERE.parents[3]))
import e02b_morphospace as e02b  # noqa: E402

torch = e02b.torch
config = e02b.config
np = e02b.np

CENSUS = EXP / "census.json"
OUT = EXP / "carrier_pairs_exploratory.json"
ROWS = EXP / "carrier_pairs_rows.jsonl"
SMOKE_ROWS = EXP / "carrier_pairs_smoke_rows.jsonl"
DEVICE = e02b._device_from_arg(os.environ.get("E02B_PAIRS_DEVICE", "auto"))
STEPS = int(os.environ.get("E02B_PAIRS_STEPS", 2000))
EVERY = 50
REPEATS = int(os.environ.get("E02B_PAIRS_REPEATS", 12))
SMOKE = "--smoke" in sys.argv

DEAD_ALIVE = 0.05
IOU_MIN = 0.5
HITS_MIN = 11
ALIVE_OPEN = 8.0
FAMILY = "WP4_R-9_s2000_seed42"
PROTO_SEED = 35
VIS = config.VISIBLE_CHANNEL
ALIV = config.ALIVE_CHANNEL
HIDDEN = list(range(2, 15))
INFORMATIVE = (2, 3, 4, 10, 11, 12, 13, 14)
CONTROLS = {(2, 3), (11, 12), (13, 14)}  # уже измерены в H-CH-9

PAIRS = [tuple(sorted(p)) for p in combinations(sorted(INFORMATIVE), 2)]
if SMOKE:
    OUT = EXP / "carrier_pairs_smoke.json"
    ROWS = SMOKE_ROWS
    PAIRS = [(2, 3)]

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


def apply_channels(proto_state, keep):
    out = proto_state.clone()
    keep = set(int(c) for c in keep)
    out[:, VIS] = 0.0
    out[:, ALIV] = ALIVE_OPEN
    for c in HIDDEN:
        if c not in keep:
            out[:, c] = 0.0
    return out


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


def main():
    import time

    started = time.time()
    model, proto_state = build_prototype()
    try:
        _pd, proto_cid = classify(proto_state)
        proto_class = names.get(proto_cid, "outlier")
        _pa, proto_binary, _pv = arrays(proto_state)
        proto_stress = model.stress_ema.detach().clone()
        print(
            f"[pairs] прототип {proto_class}; {len(PAIRS)} пар, {REPEATS} сидов, {STEPS} шагов",
            flush=True,
        )
        results = {}
        for idx, pair in enumerate(PAIRS):
            rows = []
            for rep in range(REPEATS):
                host = apply_channels(proto_state, pair)
                p_seed = 997000 + idx * 100 + rep
                desc, cid, alive, binary = run_rollout(model, proto_stress, host, p_seed)
                row = {
                    "section": "H-CH-12",
                    "family": FAMILY,
                    "pair": list(pair),
                    "is_control": pair in CONTROLS,
                    "rep": rep,
                    "p_seed": p_seed,
                    "final_class": names.get(cid, "outlier"),
                    "alive_fraction": float(desc["alive_fraction"]),
                    "body_iou": iou(binary, proto_binary),
                }
                row["body_returned"] = bool(row["body_iou"] >= IOU_MIN)
                emit(row)
                rows.append(row)
            entry = {
                "pair": list(pair),
                "is_control": pair in CONTROLS,
                "n": len(rows),
                "body_returned": sum(1 for r in rows if r["body_returned"]),
                "alive": sum(1 for r in rows if r["alive_fraction"] >= DEAD_ALIVE),
                "classes": dict(Counter(r["final_class"] for r in rows)),
                "mean_body_iou": round(float(np.mean([r["body_iou"] for r in rows])), 4),
            }
            results[str(list(pair))] = entry
            print(
                f"[pairs] {str(list(pair)):12s} тело {entry['body_returned']}/{entry['n']} "
                f"(IoU {entry['mean_body_iou']:.3f}){' [контроль]' if entry['is_control'] else ''}",
                flush=True,
            )

        control_failures = [
            key for key, st in results.items() if st["is_control"] and st["body_returned"] < REPEATS
        ]
        weak = [key for key, st in results.items() if st["body_returned"] <= 10]
        if SMOKE:
            verdict = "smoke"
        elif control_failures:
            verdict = "invalid_controls"
        elif weak:
            verdict = "H-CH-12_refuted"
        else:
            verdict = "H-CH-12_confirmed"
        payload = {
            "schema_version": 1,
            "experiment": "E02b_morphospace",
            "kind": "exploratory_carrier_pairs",
            "protocol": "reports/2026-10-22-carrier-pairs-plan.md",
            "family": FAMILY,
            "proto_seed": PROTO_SEED,
            "proto_class": proto_class,
            "informative_set": list(INFORMATIVE),
            "n_pairs": len(PAIRS),
            "steps": STEPS,
            "repeats": REPEATS,
            "criterion": f"все пары >= {HITS_MIN}/{REPEATS} при контролях {REPEATS}/{REPEATS}",
            "pairs": results,
            "weak_pairs": weak,
            "control_failures": control_failures,
            "verdict": verdict,
            "wall_seconds": round(time.time() - started, 1),
        }
        OUT.write_text(
            json.dumps(payload if not SMOKE else {"smoke": True, **payload}, ensure_ascii=False, indent=2)
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(f"[pairs] вердикт: {verdict}; слабые пары: {weak}; контроли: {control_failures}", flush=True)
        print(f"[pairs] записано: {OUT} ({payload['wall_seconds']} c)", flush=True)
        return 0
    finally:
        del model


if __name__ == "__main__":
    raise SystemExit(main())
