"""E02b carriers-2: видимый канал (H-CH-7) и дозу-ответ асимметрии (H-AB-5).

Протокол зафиксирован до запуска: `reports/2026-10-22-carriers2-plan.md`.

H-CH-7  visible=0 + гейт живости открыт (alive=+8 везде), hidden целы:
        возвращается ли тело? Критерий: контроль none держит тело >= 11/12;
        если при visible_zeroed_alive_open body_iou < 0.5 в >= 11/12 — видимый
        канал необходим; если >= 0.5 в >= 11/12 — форму несёт скрытое состояние.
H-AB-5  новые 12 пар с выровненной массой при q = 0.50-0.70; предсказание,
        записанное заранее: знак d = IoU_left - IoU_right отрицателен,
        медиана d <= -0.60.

Строки пишутся в JSONL инкрементально.
"""
import json
import sys
import time
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
OUT = EXP / "carriers2_exploratory.json"
ROWS = EXP / "carriers2_rows.jsonl"
DEVICE = e02b._device_from_arg("auto")
STEPS = 2000
EVERY = 50
REPEATS = 12
DEAD_ALIVE = 0.05
IOU_MIN = 0.5
SIGN_MIN = 11
ALIVE_OPEN = 8.0
MASS_TOL = 0.01
SIZE = 64

VIS = config.VISIBLE_CHANNEL
ALIV = config.ALIVE_CHANNEL
HIDDEN = [c for c in range(config.N_CHANNELS) if c not in (VIS, ALIV)]

MODELS = [
    ("WP4_R-9_s2000_seed42", 35, "struct_2", True, 0),
    ("untrained_current_arch", 0, "struct_1", False, 1),
]
CONDITIONS = ["none", "visible_zeroed_alive_open"]
AB5_TARGETS = [round(0.50 + 0.018 * i, 3) for i in range(12)]  # 0.500..0.698

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
    alive, binary, visible, _stress, _alpha = e02b._state_arrays(state)
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


def build_prototype(family, proto_seed, is_trained):
    spec = e02b.load_checkpoint_specs(
        families=[family], include_untrained=not is_trained
    )[0]
    if not is_trained:
        torch.manual_seed(42)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(42)
        model, _ = e02b.build_model(spec, DEVICE)
        e02b.prepare_model(model, proto_seed)
        start = e02b.init_state(
            batch_size=1,
            channels=config.N_CHANNELS,
            grid_size=config.GRID_SIZE,
            device=DEVICE,
            generator=model.generator,
        )
        final, _p, _t, _e = e02b.rollout(model, start, STEPS, EVERY)
        return model, final
    final, model, _run = e02b._prototype_state(spec, proto_seed, STEPS, EVERY, DEVICE)
    return model, final


def apply_condition(proto_state, condition):
    out = proto_state.clone()
    if condition == "none":
        return out
    if condition == "visible_zeroed_alive_open":
        out[:, VIS] = 0.0
        out[:, ALIV] = ALIVE_OPEN
        return out
    raise ValueError(condition)


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
    alive, binary, visible = arrays(state)
    return desc, cid, alive, binary, visible


def emit(row):
    with open(ROWS, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


result = {
    "schema_version": 1,
    "experiment": "E02b_morphospace",
    "kind": "exploratory_carriers2",
    "protocol": "reports/2026-10-22-carriers2-plan.md",
    "note": (
        "H-CH-7: visible=0 + alive=+8 везде, hidden целы; H-AB-5: новые 12 пар "
        "с выровненной массой при q=0.50-0.70, предсказание медианы <= -0.60"
    ),
    "device": str(DEVICE),
    "steps": STEPS,
    "repeats": REPEATS,
    "rules": {
        "same_pattern": f"IoU >= {IOU_MIN}",
        "significance": f">= {SIGN_MIN} из {REPEATS}",
        "mass_tolerance": MASS_TOL,
        "ab5_prediction": "знак -1 и медиана d <= -0.60",
    },
    "models": [],
}

# =============================== H-CH-7 ======================================
PROTO_STATE = {}
PROTO_STRESS = {}
for family, proto_seed, expected_class, is_trained, model_idx in MODELS:
    model, proto_state = build_prototype(family, proto_seed, is_trained)
    try:
        proto_desc, proto_cid = classify(proto_state)
        proto_class = names.get(proto_cid, "outlier")
        proto_alive, proto_binary, proto_visible = arrays(proto_state)
        proto_stress = model.stress_ema.detach().clone()
        PROTO_STATE[family] = proto_state
        PROTO_STRESS[family] = proto_stress
        entry = {
            "family": family,
            "proto_seed": proto_seed,
            "expected_class": expected_class,
            "proto_class": proto_class,
            "proto_body_pixels": int(np.asarray(proto_binary).sum()),
            "ch7": {},
            "ab5": None,
        }
        print(
            f"[carriers2] {family}: прототип {proto_class} (ожидался {expected_class})",
            flush=True,
        )
        for cond_idx, cond in enumerate(CONDITIONS):
            rows = []
            for rep in range(REPEATS):
                host = apply_condition(proto_state, cond)
                p_seed = 800000 + model_idx * 10000 + cond_idx * 100 + rep
                desc, cid, alive, binary, visible = run_rollout(
                    model, proto_stress, host, p_seed
                )
                row = {
                    "section": "H-CH-7",
                    "family": family,
                    "condition": cond,
                    "rep": rep,
                    "p_seed": p_seed,
                    "final_class": names.get(cid, "outlier"),
                    "alive_fraction": float(desc["alive_fraction"]),
                    "body_iou": iou(binary, proto_binary),
                }
                row["body_returned"] = bool(row["body_iou"] >= IOU_MIN)
                emit(row)
                rows.append(row)
            entry["ch7"][cond] = {
                "n": len(rows),
                "body_returned": sum(1 for r in rows if r["body_returned"]),
                "alive": sum(1 for r in rows if r["alive_fraction"] >= DEAD_ALIVE),
                "classes": dict(Counter(r["final_class"] for r in rows)),
                "mean_body_iou": round(float(np.mean([r["body_iou"] for r in rows])), 4),
            }
            st = entry["ch7"][cond]
            print(
                f"[carriers2] {family} {cond:28s} тело {st['body_returned']}/{REPEATS} "
                f"(IoU {st['mean_body_iou']:.3f}), классы {st['classes']}",
                flush=True,
            )
        result["models"].append(entry)
    finally:
        del model

# =============================== H-AB-5 ======================================
FAMILY = "WP4_R-9_s2000_seed42"
model, proto_state = build_prototype(FAMILY, 35, True)
try:
    proto_desc, proto_cid = classify(proto_state)
    proto_class = names.get(proto_cid, "outlier")
    proto_alive, proto_binary, _pv = arrays(proto_state)
    proto_stress = model.stress_ema.detach().clone()
    live = np.asarray(proto_binary).astype(bool)
    total = int(live.sum())
    cum = np.concatenate([[0], np.cumsum(live.sum(axis=0).astype(int))])

    pairs, ab5_rows = [], []
    for idx, q in enumerate(AB5_TARGETS):
        c_left = int(np.argmin(np.abs(cum / total - q)))
        removed_left = cum[c_left]
        best_c2, best_gap = None, 10**9
        for c2 in range(1, SIZE):
            removed_right = total - cum[c2]
            gap = abs(removed_right - removed_left)
            if gap < best_gap:
                best_c2, best_gap = c2, gap
        removed_right = total - cum[best_c2]
        f_l, f_r = removed_left / total, removed_right / total
        is_valid = abs(f_l - f_r) <= MASS_TOL and 0.45 <= f_l <= 0.75
        pair = {
            "pair": idx,
            "target_q": q,
            "c_left": c_left,
            "c_right": best_c2,
            "removed_fraction_left": round(float(f_l), 4),
            "removed_fraction_right": round(float(f_r), 4),
            "mass_gap": round(float(abs(f_l - f_r)), 4),
            "valid": bool(is_valid),
            "iou_left": None,
            "iou_right": None,
            "diff": None,
        }
        if is_valid:
            for side, col in (("left", c_left), ("right", best_c2)):
                host = proto_state.clone()
                if side == "left":
                    host[:, :, :, :col] = 0.0
                else:
                    host[:, :, :, col:] = 0.0
                p_seed = 900000 + idx * 10 + (0 if side == "left" else 1)
                desc, cid, alive, binary, _v = run_rollout(
                    model, proto_stress, host, p_seed
                )
                value = iou(binary, proto_binary)
                row = {
                    "section": "H-AB-5",
                    "family": FAMILY,
                    "pair": idx,
                    "side": side,
                    "cut_column": col,
                    "removed_fraction": round(float(f_l if side == "left" else f_r), 4),
                    "p_seed": p_seed,
                    "final_class": names.get(cid, "outlier"),
                    "alive_fraction": float(desc["alive_fraction"]),
                    "iou": value,
                }
                row["same_pattern"] = bool(value >= IOU_MIN)
                emit(row)
                ab5_rows.append(row)
                pair[f"iou_{side}"] = round(float(value), 4)
            pair["diff"] = round(pair["iou_left"] - pair["iou_right"], 4)
            print(
                f"[carriers2] H-AB-5 пара {idx} q={q} c=({c_left},{best_c2}) "
                f"diff={pair['diff']:+.3f}",
                flush=True,
            )
        pairs.append(pair)

    valid_pairs = [p for p in pairs if p["valid"]]
    diffs = [p["diff"] for p in valid_pairs]
    signs = [1 if d > 0 else (-1 if d < 0 else 0) for d in diffs]
    median = float(np.median(diffs)) if diffs else 0.0
    sign_ok = bool(signs) and Counter(signs).most_common(1)[0][1] >= SIGN_MIN and -1 in Counter(signs)
    median_ok = median <= -0.60
    ab5 = {
        "family": FAMILY,
        "proto_class": proto_class,
        "pairs": pairs,
        "n_valid": len(valid_pairs),
        "sign_counts": {str(k): v for k, v in Counter(signs).items()},
        "median_diff": round(median, 4),
        "prediction": "знак -1 и медиана d <= -0.60",
        "sign_ok": sign_ok,
        "median_ok": median_ok,
        "verdict": (
            "confirmed_dose_response" if (sign_ok and median_ok) else "not_confirmed"
        ),
    }
    result["models"].append(
        {
            "family": FAMILY,
            "section": "H-AB-5",
            "proto_class": proto_class,
            "ab5": ab5,
        }
    )
    print(
        f"[carriers2] H-AB-5: медиана {median:+.3f}, знаки {ab5['sign_counts']}, "
        f"валидных пар {len(valid_pairs)} -> {ab5['verdict']}",
        flush=True,
    )
finally:
    del model

# =============================== вердикты ====================================
ch7_verdict = {"applicable": False, "reason": "нет модели struct_2"}
struct2 = next(
    (m for m in result["models"]
     if m.get("family") == "WP4_R-9_s2000_seed42" and m.get("ch7")),
    None,
)
if struct2:
    none_st = struct2["ch7"]["none"]
    open_st = struct2["ch7"]["visible_zeroed_alive_open"]
    if none_st["body_returned"] < SIGN_MIN:
        ch7_verdict = {
            "applicable": False,
            "reason": f"контроль none держит тело {none_st['body_returned']}/{REPEATS}",
        }
    elif open_st["body_returned"] >= SIGN_MIN:
        ch7_verdict = {
            "applicable": True,
            "verdict": "refuted_visible_not_necessary",
            "reason": (
                f"без видимого канала тело возвращается {open_st['body_returned']}/{REPEATS} — "
                "форму несёт скрытое состояние"
            ),
        }
    elif (REPEATS - open_st["body_returned"]) >= SIGN_MIN:
        ch7_verdict = {
            "applicable": True,
            "verdict": "confirmed_visible_necessary",
            "reason": (
                f"без видимого канала тело возвращается лишь {open_st['body_returned']}/{REPEATS}"
            ),
        }
    else:
        ch7_verdict = {
            "applicable": True,
            "verdict": "inconclusive",
            "reason": f"промежуточный результат: {open_st['body_returned']}/{REPEATS}",
        }
result["verdict_ch7"] = ch7_verdict
result["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"[carriers2] H-CH-7 вердикт: {ch7_verdict}", flush=True)
print(f"[carriers2] записан {OUT}", flush=True)
