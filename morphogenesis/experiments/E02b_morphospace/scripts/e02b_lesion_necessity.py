"""E02b lesion-necessity: информативные каналы необходимы, инертные — нет (H-CH-10).

Протокол заморожен до запуска: `reports/2026-10-22-lesion-necessity-plan.md`.

Hypothesis (H-CH-10). В H-CH-9 тело `struct_2` вернулось из одного канала `{14}`
и из наборов {2,3,4} / {10–14}, но не из {6,7,8} и не из {8,9}. Если деление на
информативные (2–4, 10–14) и инертные (5–9) каналы верно, то взаимно
дополнительные условия должны различаться резко:

    informative_only  keep {2,3,4,10,11,12,13,14}  -> тело 12/12 (ожидание)
    inert_only        keep {5,6,7,8,9}             -> тело 0..3/12 (ожидание)

Критерий до прогона: `body(inert_only) <= body(informative_only) - 8/12` при
работающем контроле `none`.

Запуск (из корня, через обёртку с журналом):

    python morphogenesis/run_exploratory.py \
        morphogenesis/experiments/E02b_morphospace/scripts/e02b_lesion_necessity.py

Быстрая проверка на CPU (не результат):

    E02B_NEC_STEPS=20 E02B_NEC_REPEATS=1 E02B_NEC_DEVICE=cpu \
    python .../e02b_lesion_necessity.py --smoke
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
OUT = EXP / "lesion_necessity_exploratory.json"
ROWS = EXP / "lesion_necessity_rows.jsonl"
SMOKE_ROWS = EXP / "lesion_necessity_smoke_rows.jsonl"
DEVICE = e02b._device_from_arg(os.environ.get("E02B_NEC_DEVICE", "auto"))
STEPS = int(os.environ.get("E02B_NEC_STEPS", 2000))
EVERY = 50
REPEATS = int(os.environ.get("E02B_NEC_REPEATS", 12))
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

# Разбиение взято из H-CH-9 до этого прогона, а не подобрано по этому.
INFORMATIVE = (2, 3, 4, 10, 11, 12, 13, 14)
INERT = (5, 6, 7, 8, 9)
CONDITIONS = {
    "none": tuple(HIDDEN),
    "informative_only": INFORMATIVE,
    "inert_only": INERT,
}
if SMOKE:
    OUT = EXP / "lesion_necessity_smoke.json"
    ROWS = SMOKE_ROWS
    CONDITIONS = {"informative_only": INFORMATIVE}

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
        proto_desc, proto_cid = classify(proto_state)
        proto_class = names.get(proto_cid, "outlier")
        _pa, proto_binary, _pv = arrays(proto_state)
        proto_stress = model.stress_ema.detach().clone()
        print(
            f"[nec] прототип {proto_class}, {int(np.asarray(proto_binary).sum())} px; "
            f"условия {list(CONDITIONS)}; {REPEATS} повторов, {STEPS} шагов",
            flush=True,
        )
        results = {}
        for cond_idx, (name, keep) in enumerate(CONDITIONS.items()):
            rows = []
            for rep in range(REPEATS):
                host = apply_channels(proto_state, keep)
                p_seed = 980000 + cond_idx * 100 + rep
                desc, cid, alive, binary = run_rollout(model, proto_stress, host, p_seed)
                row = {
                    "section": "H-CH-10",
                    "family": FAMILY,
                    "condition": name,
                    "channels_kept": list(keep),
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
                "n": len(rows),
                "channels_kept": list(keep),
                "body_returned": sum(1 for r in rows if r["body_returned"]),
                "alive": sum(1 for r in rows if r["alive_fraction"] >= DEAD_ALIVE),
                "classes": dict(Counter(r["final_class"] for r in rows)),
                "mean_body_iou": round(float(np.mean([r["body_iou"] for r in rows])), 4),
            }
            results[name] = entry
            print(
                f"[nec] {name:16s} тело {entry['body_returned']}/{entry['n']} "
                f"(IoU {entry['mean_body_iou']:.3f}), классы {entry['classes']}",
                flush=True,
            )

        if SMOKE:
            payload = {"smoke": True, "conditions": results}
        else:
            none_ok = results["none"]["body_returned"]
            inf = results["informative_only"]["body_returned"]
            inert = results["inert_only"]["body_returned"]
            if none_ok < HITS_MIN:
                verdict = "invalid_none_control"
            elif inert <= inf - 8:
                verdict = "H-CH-10_confirmed"
            else:
                verdict = "H-CH-10_refuted"
            payload = {
                "schema_version": 1,
                "experiment": "E02b_morphospace",
                "kind": "exploratory_lesion_necessity",
                "protocol": "reports/2026-10-22-lesion-minimal-plan.md"
                            " -> reports/2026-10-22-lesion-necessity-plan.md",
                "family": FAMILY,
                "proto_seed": PROTO_SEED,
                "proto_class": proto_class,
                "proto_body_pixels": int(np.asarray(proto_binary).sum()),
                "steps": STEPS,
                "repeats": REPEATS,
                "device": str(DEVICE),
                "criterion": "body(inert_only) <= body(informative_only) - 8/12 "
                             "при none >= 11/12",
                "conditions": results,
                "verdict": verdict,
                "wall_seconds": round(time.time() - started, 1),
            }
        OUT.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(f"[nec] записано: {OUT} ({round(time.time() - started, 1)} c)", flush=True)
        if not SMOKE:
            print(f"[nec] вердикт: {payload['verdict']}", flush=True)
        return 0
    finally:
        del model


if __name__ == "__main__":
    raise SystemExit(main())
