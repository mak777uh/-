"""E02b clusters-3: минимальная группа скрытых каналов (H-CH-8) и форма кривой
асимметрии (H-AB-6).

Протокол зафиксирован до запуска: `reports/2026-10-22-clusters3-plan.md`.

H-CH-8  visible=0, alive=+8, остаётся одна группа скрытых каналов:
        group_a_only (2..7 целы, 8..14 нули) и group_b_only (8..14 целы,
        2..7 нули). Критерий: body_iou >= 0.5 в >= 11/12 хотя бы для одной
        группы при работающем контроле none.
H-AB-6  11 плотных пар q=0.55..0.65 с выровненной массой; предсказание до
        прогона: все d < 0 и max|d| в [0.58, 0.68].
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
OUT = EXP / "clusters3_exploratory.json"
ROWS = EXP / "clusters3_rows.jsonl"
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
GROUP_A = [2, 3, 4, 5, 6, 7]
GROUP_B = [8, 9, 10, 11, 12, 13, 14]

MODELS = [
    ("WP4_R-9_s2000_seed42", 35, "struct_2", True, 0),
    ("untrained_current_arch", 0, "struct_1", False, 1),
]
CONDITIONS = ["none", "group_a_only", "group_b_only"]
AB6_TARGETS = [round(0.55 + 0.01 * i, 3) for i in range(11)]  # 0.55..0.65

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
    out[:, VIS] = 0.0
    out[:, ALIV] = ALIVE_OPEN
    if condition == "group_a_only":
        for c in GROUP_B:
            out[:, c] = 0.0
        return out
    if condition == "group_b_only":
        for c in GROUP_A:
            out[:, c] = 0.0
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
    "kind": "exploratory_clusters3",
    "protocol": "reports/2026-10-22-clusters3-plan.md",
    "note": (
        "H-CH-8: visible=0 + alive=+8, остаётся одна группа скрытых каналов "
        "(2..7 или 8..14); H-AB-6: 11 плотных пар q=0.55..0.65, предсказание "
        "max|d| в [0.58, 0.68]"
    ),
    "device": str(DEVICE),
    "steps": STEPS,
    "repeats": REPEATS,
    "rules": {
        "same_pattern": f"IoU >= {IOU_MIN}",
        "significance": f">= {SIGN_MIN} из {REPEATS}",
        "mass_tolerance": MASS_TOL,
        "ab6_prediction": "все d < 0 и max|d| в [0.58, 0.68]",
    },
    "models": [],
}

for family, proto_seed, expected_class, is_trained, model_idx in MODELS:
    model, proto_state = build_prototype(family, proto_seed, is_trained)
    try:
        proto_desc, proto_cid = classify(proto_state)
        proto_class = names.get(proto_cid, "outlier")
        proto_alive, proto_binary, _pv = arrays(proto_state)
        proto_stress = model.stress_ema.detach().clone()
        entry = {
            "family": family,
            "proto_seed": proto_seed,
            "expected_class": expected_class,
            "proto_class": proto_class,
            "proto_body_pixels": int(np.asarray(proto_binary).sum()),
            "ch8": {},
            "ab6": None,
        }
        print(
            f"[clusters3] {family}: прототип {proto_class} (ожидался {expected_class})",
            flush=True,
        )
        for cond_idx, cond in enumerate(CONDITIONS):
            rows = []
            for rep in range(REPEATS):
                host = apply_condition(proto_state, cond)
                p_seed = 910000 + model_idx * 10000 + cond_idx * 100 + rep
                desc, cid, alive, binary, _v = run_rollout(
                    model, proto_stress, host, p_seed
                )
                row = {
                    "section": "H-CH-8",
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
            entry["ch8"][cond] = {
                "n": len(rows),
                "body_returned": sum(1 for r in rows if r["body_returned"]),
                "alive": sum(1 for r in rows if r["alive_fraction"] >= DEAD_ALIVE),
                "classes": dict(Counter(r["final_class"] for r in rows)),
                "mean_body_iou": round(float(np.mean([r["body_iou"] for r in rows])), 4),
            }
            st = entry["ch8"][cond]
            print(
                f"[clusters3] {family} {cond:14s} тело {st['body_returned']}/{REPEATS} "
                f"(IoU {st['mean_body_iou']:.3f}), классы {st['classes']}",
                flush=True,
            )
        result["models"].append(entry)
    finally:
        del model

# =============================== H-AB-6 ======================================
FAMILY = "WP4_R-9_s2000_seed42"
model, proto_state = build_prototype(FAMILY, 35, True)
try:
    proto_desc, proto_cid = classify(proto_state)
    proto_class = names.get(proto_cid, "outlier")
    _pa, proto_binary, _pv = arrays(proto_state)
    proto_stress = model.stress_ema.detach().clone()
    live = np.asarray(proto_binary).astype(bool)
    total = int(live.sum())
    cum = np.concatenate([[0], np.cumsum(live.sum(axis=0).astype(int))])

    pairs = []
    for idx, q in enumerate(AB6_TARGETS):
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
        is_valid = abs(f_l - f_r) <= MASS_TOL and 0.50 <= f_l <= 0.70
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
                p_seed = 950000 + idx * 10 + (0 if side == "left" else 1)
                desc, cid, alive, binary, _v = run_rollout(
                    model, proto_stress, host, p_seed
                )
                value = iou(binary, proto_binary)
                row = {
                    "section": "H-AB-6",
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
                pair[f"iou_{side}"] = round(float(value), 4)
            pair["diff"] = round(pair["iou_left"] - pair["iou_right"], 4)
            print(
                f"[clusters3] H-AB-6 пара {idx} q={q} c=({c_left},{best_c2}) "
                f"diff={pair['diff']:+.3f}",
                flush=True,
            )
        pairs.append(pair)

    valid_pairs = [p for p in pairs if p["valid"]]
    diffs = [p["diff"] for p in valid_pairs]
    abs_max = max((abs(d) for d in diffs), default=0.0)
    all_negative = bool(diffs) and all(d < 0 for d in diffs)
    in_range = 0.58 <= abs_max <= 0.68
    ab6 = {
        "family": FAMILY,
        "proto_class": proto_class,
        "pairs": pairs,
        "n_valid": len(valid_pairs),
        "diffs": diffs,
        "max_abs_diff": round(float(abs_max), 4),
        "all_negative": all_negative,
        "prediction": "все d < 0 и max|d| в [0.58, 0.68]",
        "verdict": (
            "confirmed_hump" if (all_negative and in_range) else "not_confirmed"
        ),
    }
    result["models"].append(
        {"family": FAMILY, "section": "H-AB-6", "proto_class": proto_class, "ab6": ab6}
    )
    print(
        f"[clusters3] H-AB-6: max|d|={abs_max:.3f}, все отрицательны={all_negative}, "
        f"валидных {len(valid_pairs)} -> {ab6['verdict']}",
        flush=True,
    )
finally:
    del model

# =============================== вердикты ====================================
struct2 = next(
    (m for m in result["models"]
     if m.get("family") == "WP4_R-9_s2000_seed42" and m.get("ch8")),
    None,
)
ch8 = {"applicable": False, "reason": "нет модели struct_2"}
if struct2:
    none_st = struct2["ch8"]["none"]
    a_st = struct2["ch8"]["group_a_only"]
    b_st = struct2["ch8"]["group_b_only"]
    if none_st["body_returned"] < SIGN_MIN:
        ch8 = {"applicable": False, "reason": f"контроль none {none_st['body_returned']}/{REPEATS}"}
    else:
        groups_ok = [
            name for name, st in (("group_a_2_7", a_st), ("group_b_8_14", b_st))
            if st["body_returned"] >= SIGN_MIN
        ]
        if groups_ok:
            ch8 = {
                "applicable": True,
                "verdict": "confirmed_single_group_sufficient",
                "sufficient_groups": groups_ok,
                "reason": "одна группа скрытых каналов реконструирует тело: " + ", ".join(groups_ok),
            }
        else:
            ch8 = {
                "applicable": True,
                "verdict": "refuted_single_group_insufficient",
                "sufficient_groups": [],
                "reason": (
                    f"группы дали {a_st['body_returned']}/{REPEATS} и "
                    f"{b_st['body_returned']}/{REPEATS} — нужен весь скрытый набор"
                ),
            }
result["verdict_ch8"] = ch8
result["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"[clusters3] H-CH-8 вердикт: {ch8}", flush=True)
print(f"[clusters3] записан {OUT}", flush=True)
