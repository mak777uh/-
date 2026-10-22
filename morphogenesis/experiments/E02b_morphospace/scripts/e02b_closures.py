"""E02b closures: H-CH-2, H-CH-3, H-CH-4 и H-AB-2 за один inference-прогон.

Протокол зафиксирован до запуска:
`reports/2026-10-21-e02b-closures-plan.md`. Здесь только исполнение.

Что считается (без обучения, на замороженных чекпоинтах):

H-CH-2  нужны ли конкретные скрытые каналы: обнуление одиночных каналов 2..14 и
        шести групп при целой видимой текстуре; критерий — хотя бы одна группа
        роняет same_pattern ниже 11/12 у struct_2.
H-CH-3  возвращается ли ориентация при visible_zeroed: лучшее из 8 преобразований
        D4 обязано быть тождественным в >= 11/12 повторов.
H-CH-4  необходимо ли хотя бы одно из двух состояний: all_but_alive_zeroed
        (visible=0, hidden=0, alive цел); критерий — same_pattern < 11/12.
H-AB-2  асимметрия структурная, а не массовая: 12 пар «левое/правое» с
        выровненной удалённой массой (допуск 0.01 доли живых клеток); критерий —
        знак разности IoU одинаков в >= 11/12 пар.

Правила общие: живость по alive >= 0.05, same_pattern = бинарный IoU >= 0.5,
порог знаковости 11/12, прототип собран каноническим путём (EMA стресса из
чекпоинта, а не обнулённая). Строки пишутся инкрементально в JSONL.

Запуск — только через лаунчер, чтобы в журнале была пара start/finish:

    python run_exploratory.py \\
      --script experiments/E02b_morphospace/scripts/e02b_closures.py \\
      --experiment E02b_closures
"""
import json
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
OUT = EXP / "closures_exploratory.json"
ROWS = EXP / "closures_rows.jsonl"
DEVICE = e02b._device_from_arg("auto")
STEPS = 2000
EVERY = 50
REPEATS = 12
DEAD_ALIVE = 0.05
SIGN_MIN = 11
IOU_MIN = 0.5
SIZE = 64

VIS = config.VISIBLE_CHANNEL
ALIV = config.ALIVE_CHANNEL
HIDDEN = [c for c in range(config.N_CHANNELS) if c not in (VIS, ALIV)]

MODELS = [
    ("WP4_R-9_s2000_seed42", 35, "struct_2", True, 0),
    ("WP4_R-9_s2000_seed101", 5, "struct_1", True, 1),
    ("untrained_current_arch", 0, "struct_1", False, 2),
]

SINGLES = [f"single_{c}" for c in range(2, 15)]
GROUPS = {
    "g_2_7": list(range(2, 8)),
    "g_8_14": list(range(8, 15)),
    "g_2_4": [2, 3, 4],
    "g_5_7": [5, 6, 7],
    "g_8_10": [8, 9, 10],
    "g_11_14": [11, 12, 13, 14],
}
CONDITIONS_CH2 = ["none"] + SINGLES + list(GROUPS)

# --- загрузка центроидов замороженной переписи --------------------------------
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


def binary_of(state):
    return e02b._state_arrays(state)[1]


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


def dihedral_masks(a):
    """8 преобразований D4; индекс 0 — тождественное."""
    out = []
    cur = a
    for _ in range(4):
        out.append(cur)
        out.append(np.fliplr(cur))
        cur = np.rot90(cur)
    return out


def best_dihedral_index(a, b):
    """Индекс преобразования a, дающего максимальный IoU с b."""
    masks = dihedral_masks(a)
    ious = [iou(m, b) for m in masks]
    idx = int(np.argmax(ious))
    return idx, float(ious[idx]), [round(v, 4) for v in ious]


def build_prototype(family, proto_seed, is_trained):
    """Канонический прототип: для обученных — через `_prototype_state`."""
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
        final, _points, _traj, _elapsed = e02b.rollout(model, start, STEPS, EVERY)
        return model, final
    final, model, _run = e02b._prototype_state(spec, proto_seed, STEPS, EVERY, DEVICE)
    return model, final


def zero_channels(state, channels, zero_visible=False):
    out = state.clone()
    if zero_visible:
        out[:, VIS] = 0.0
    for c in channels:
        out[:, c] = 0.0
    return out


def run_rollout(model, proto_stress, host, p_seed):
    """Одна развёртка 2000 шагов; возвращает класс, живость, IoU, D4-индекс."""
    gen = config.create_deterministic_generator(p_seed)
    model.set_generator(gen)
    model.stress_ema.copy_(proto_stress)
    model._noise_cache = {}
    model._noise_seq = 0
    model.begin_segment()
    state = host
    for step in range(1, STEPS + 1):
        with torch.no_grad():
            state = model(state)
    desc, cid = classify(state)
    return {
        "assigned_class": names.get(cid, "outlier"),
        "alive_fraction": float(desc["alive_fraction"]),
        "final_class": names.get(cid, "outlier"),
        "binary": binary_of(state),
    }


def summarize(rows, key="same_pattern"):
    n = len(rows)
    return {
        "n": n,
        "same_pattern": sum(1 for r in rows if r[key]),
        "alive": sum(1 for r in rows if r["alive_fraction"] >= DEAD_ALIVE),
        "classes": dict(Counter(r["final_class"] for r in rows)),
        "mean_iou": round(float(np.mean([r["iou"] for r in rows])), 4) if rows else 0.0,
    }


def emit(row):
    with open(ROWS, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


result = {
    "schema_version": 1,
    "experiment": "E02b_morphospace",
    "kind": "exploratory_closures",
    "protocol": "reports/2026-10-21-e02b-closures-plan.md",
    "note": (
        "H-CH-2 (одиночные каналы 2..14 и 6 групп), H-CH-3 (ориентация при "
        "visible_zeroed), H-CH-4 (all_but_alive_zeroed), H-AB-2 (12 пар с "
        "выровненной массой); без обучения"
    ),
    "device": str(DEVICE),
    "steps": STEPS,
    "repeats": REPEATS,
    "rules": {
        "same_pattern": f"бинарный IoU >= {IOU_MIN}",
        "significance": f">= {SIGN_MIN} из {REPEATS}",
        "alive": f"alive_fraction >= {DEAD_ALIVE}",
        "prototype": "канонический путь _prototype_state (EMA стресса из чекпоинта)",
    },
    "models": [],
}

# =============================== H-CH-2/3/4 ==================================
PROTO_BY_FAMILY = {}
for family, proto_seed, expected_class, is_trained, model_idx in MODELS:
    model, proto_state = build_prototype(family, proto_seed, is_trained)
    try:
        proto_desc, proto_cid = classify(proto_state)
        proto_class = names.get(proto_cid, "outlier")
        proto_binary = binary_of(proto_state)
        proto_stress = model.stress_ema.detach().clone()
        proto_alive = float(proto_desc["alive_fraction"])
        PROTO_BY_FAMILY[family] = {
            "proto_class": proto_class,
            "proto_seed": proto_seed,
            "proto_alive": proto_alive,
            "proto_binary": proto_binary,
        }
        print(
            f"[closures] {family}: прототип seed={proto_seed} класс={proto_class} "
            f"(ожидался {expected_class}) alive={proto_alive:.3f}",
            flush=True,
        )

        entry = {
            "family": family,
            "proto_seed": proto_seed,
            "expected_class": expected_class,
            "proto_class": proto_class,
            "proto_alive": round(proto_alive, 4),
            "ch2": {},
            "ch3": None,
            "ch4": None,
            "ab2": None,
        }

        # --- H-CH-2: одиночные каналы и группы
        for cond_idx, cond in enumerate(CONDITIONS_CH2):
            if cond == "none":
                channels, zero_visible = [], False
            elif cond.startswith("single_"):
                channels, zero_visible = [int(cond.split("_")[1])], False
            else:
                channels, zero_visible = GROUPS[cond], False
            rows = []
            for rep in range(REPEATS):
                host = zero_channels(proto_state, channels, zero_visible)
                p_seed = 100000 + model_idx * 10000 + cond_idx * 100 + rep
                out = run_rollout(model, proto_stress, host, p_seed)
                row = {
                    "section": "H-CH-2",
                    "family": family,
                    "condition": cond,
                    "channels": channels,
                    "rep": rep,
                    "p_seed": p_seed,
                    "final_class": out["final_class"],
                    "alive_fraction": out["alive_fraction"],
                    "iou": iou(out["binary"], proto_binary),
                }
                row["same_pattern"] = bool(row["iou"] >= IOU_MIN)
                row["class_retained"] = bool(
                    row["final_class"] == proto_class and row["alive_fraction"] >= DEAD_ALIVE
                )
                emit(row)
                rows.append(row)
            entry["ch2"][cond] = summarize(rows)
            print(
                f"[closures] {family} H-CH-2 {cond:9s} same_pattern="
                f"{entry['ch2'][cond]['same_pattern']}/{REPEATS}",
                flush=True,
            )

        # --- H-CH-3: ориентация при обнулённой видимой текстуре
        rows = []
        for rep in range(REPEATS):
            host = zero_channels(proto_state, [], zero_visible=True)
            p_seed = 300000 + model_idx * 10000 + rep
            out = run_rollout(model, proto_stress, host, p_seed)
            idx, diag_iou, all_ious = best_dihedral_index(out["binary"], proto_binary)
            row = {
                "section": "H-CH-3",
                "family": family,
                "condition": "visible_zeroed",
                "rep": rep,
                "p_seed": p_seed,
                "final_class": out["final_class"],
                "alive_fraction": out["alive_fraction"],
                "iou": iou(out["binary"], proto_binary),
                "best_d4_index": idx,
                "best_d4_iou": diag_iou,
                "d4_ious": all_ious,
            }
            row["same_pattern"] = bool(diag_iou >= IOU_MIN)
            row["same_orientation"] = bool(idx == 0 and diag_iou >= IOU_MIN)
            emit(row)
            rows.append(row)
        entry["ch3"] = {
            "n": len(rows),
            "identity_orientation": sum(1 for r in rows if r["same_orientation"]),
            "same_pattern_dihedral": sum(1 for r in rows if r["same_pattern"]),
            "d4_histogram": dict(Counter(int(r["best_d4_index"]) for r in rows)),
            "mean_iou": round(float(np.mean([r["best_d4_iou"] for r in rows])), 4),
        }
        print(
            f"[closures] {family} H-CH-3 identity="
            f"{entry['ch3']['identity_orientation']}/{REPEATS} "
            f"d4={entry['ch3']['d4_histogram']}",
            flush=True,
        )

        # --- H-CH-4: видимое и скрытое обнулены, alive цел
        rows = []
        for rep in range(REPEATS):
            host = zero_channels(proto_state, HIDDEN, zero_visible=True)
            p_seed = 400000 + model_idx * 10000 + rep
            out = run_rollout(model, proto_stress, host, p_seed)
            row = {
                "section": "H-CH-4",
                "family": family,
                "condition": "all_but_alive_zeroed",
                "rep": rep,
                "p_seed": p_seed,
                "final_class": out["final_class"],
                "alive_fraction": out["alive_fraction"],
                "iou": iou(out["binary"], proto_binary),
            }
            row["same_pattern"] = bool(row["iou"] >= IOU_MIN)
            emit(row)
            rows.append(row)
        entry["ch4"] = summarize(rows)
        print(
            f"[closures] {family} H-CH-4 same_pattern="
            f"{entry['ch4']['same_pattern']}/{REPEATS} "
            f"alive={entry['ch4']['alive']}/{REPEATS}",
            flush=True,
        )

        result["models"].append(entry)
    finally:
        del model

# =============================== H-AB-2 ======================================
FAMILY = "WP4_R-9_s2000_seed42"
proto = PROTO_BY_FAMILY.get(FAMILY)
if proto is None:
    raise SystemExit("[closures] нет прототипа struct_2 — H-AB-2 невозможен")

# Прототип для H-AB-2 берём заново, чтобы не зависеть от порядка секций.
model42, proto_state42 = build_prototype(FAMILY, 35, True)
proto_desc42, proto_cid42 = classify(proto_state42)
proto_class42 = names.get(proto_cid42, "outlier")
proto_binary42 = binary_of(proto_state42)
proto_stress42 = model42.stress_ema.detach().clone()

live42 = np.asarray(proto_binary42).astype(bool)
total_live42 = int(live42.sum())
cum42 = np.concatenate([[0], np.cumsum(live42.sum(axis=0).astype(int))])

AB2_TARGETS = [round(0.15 + 0.03 * i, 2) for i in range(12)]
TOL = 0.01
pairs = []
ab2_rows = []
for pair_idx, q in enumerate(AB2_TARGETS):
    # левое повреждение: [0, c); правое: [c2, SIZE)
    c_left = int(np.argmin(np.abs(cum42 / total_live42 - q)))
    removed_left = cum42[c_left]
    # правое: удалить из правого края столько же живых клеток
    best_c2, best_gap = None, 10**9
    for c2 in range(1, SIZE):
        removed_right = total_live42 - cum42[c2]
        gap = abs(removed_right - removed_left)
        if gap < best_gap:
            best_c2, best_gap = c2, gap
    removed_right = total_live42 - cum42[best_c2]
    frac_left, frac_right = removed_left / total_live42, removed_right / total_live42
    is_valid = abs(frac_left - frac_right) <= TOL and 0.10 <= frac_left <= 0.55
    pair = {
        "pair": pair_idx,
        "target_q": q,
        "c_left": c_left,
        "c_right": best_c2,
        "removed_fraction_left": round(float(frac_left), 4),
        "removed_fraction_right": round(float(frac_right), 4),
        "mass_gap": round(float(abs(frac_left - frac_right)), 4),
        "valid": bool(is_valid),
        "iou_left": None,
        "iou_right": None,
        "diff": None,
    }
    if is_valid:
        for side, col in (("left", c_left), ("right", best_c2)):
            host = proto_state42.clone()
            if side == "left":
                host[:, :, :, :col] = 0.0
            else:
                host[:, :, :, col:] = 0.0
            p_seed = 500000 + pair_idx * 10 + (0 if side == "left" else 1)
            out = run_rollout(model42, proto_stress42, host, p_seed)
            value = iou(out["binary"], proto_binary42)
            row = {
                "section": "H-AB-2",
                "family": FAMILY,
                "pair": pair_idx,
                "side": side,
                "cut_column": col,
                "removed_fraction": round(float(frac_left if side == "left" else frac_right), 4),
                "p_seed": p_seed,
                "final_class": out["final_class"],
                "alive_fraction": out["alive_fraction"],
                "iou": value,
            }
            row["same_pattern"] = bool(value >= IOU_MIN)
            emit(row)
            ab2_rows.append(row)
            pair[f"iou_{side}"] = round(float(value), 4)
        pair["diff"] = round(pair["iou_left"] - pair["iou_right"], 4)
        print(
            f"[closures] H-AB-2 пара {pair_idx} q={q} c=({c_left},{best_c2}) "
            f"IoU=({pair['iou_left']:.3f},{pair['iou_right']:.3f}) diff={pair['diff']:+.3f}",
            flush=True,
        )
    pairs.append(pair)

valid_pairs = [p for p in pairs if p["valid"]]
signs = [1 if p["diff"] > 0 else (-1 if p["diff"] < 0 else 0) for p in valid_pairs]
dominant = Counter(signs).most_common(1)[0] if signs else (0, 0)
mean_diff = float(np.mean([p["diff"] for p in valid_pairs])) if valid_pairs else 0.0
ab2 = {
    "family": FAMILY,
    "proto_class": proto_class42,
    "pairs": pairs,
    "n_valid": len(valid_pairs),
    "sign_counts": {str(k): v for k, v in Counter(signs).items()},
    "dominant_sign": dominant[0],
    "dominant_count": dominant[1],
    "sign_consistent": bool(dominant[1] >= SIGN_MIN),
    "mean_diff": round(mean_diff, 4),
    "criterion": f"знак разности одинаков в >= {SIGN_MIN} из {REPEATS} валидных пар",
    "verdict": (
        "confirmed_structural_asymmetry"
        if dominant[1] >= SIGN_MIN
        else "refuted_asymmetry_is_mass"
    ),
}
for entry in result["models"]:
    if entry["family"] == FAMILY:
        entry["ab2"] = ab2
print(
    f"[closures] H-AB-2 вердикт: {ab2['verdict']} "
    f"(знак {ab2['sign_counts']}, средняя разность {ab2['mean_diff']:+.3f}, "
    f"валидных пар {ab2['n_valid']})",
    flush=True,
)

out_path = OUT
out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"[closures] записан {out_path}", flush=True)
