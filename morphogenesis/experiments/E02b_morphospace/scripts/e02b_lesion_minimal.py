"""E02b lesion-minimal: минимальный носитель (H-CH-9) и дисперсия асимметрии
при фиксированной геометрии (H-AB-7).

Протокол заморожен до запуска: `reports/2026-10-22-lesion-minimal-plan.md`.
Прогон ничего не обучает: те же веса `WP4_R-9_s2000_seed42`, прототип
`proto_seed = 35`, 2000 шагов, только inference.

H-CH-9  visible=0, alive=+8, из скрытых каналов 2..14 остаётся набор размером
        1, 2 или 3 (16 наборов зафиксированы в плане). Критерий: `body_returned`
        (IoU >= 0.5) в >= 11/12 хотя бы для одного набора при работающем
        контроле `none` и untrained-контроле <= 1/12.
H-AB-7  две геометрии среза, по 12 независимых шумовых сидов на каждую:
        c=(40,24) и c=(38,26). Критерий: std(d) <= 0.05 — величина объясняется
        геометрией; > 0.10 — шум, кривые по q строить нельзя.

Семантика обнуления повторяет clusters-3 (`e02b_clusters3.py`): `visible = 0`,
`alive = +8`, и нулями становятся скрытые каналы 2..14 вне набора; канал 15 и
прочие не трогаются, иначе отличие от H-CH-8 было бы ещё и в наборе каналов.

Класс (`final_class`) считается описательно: центроиды пересобраны из
`census.json` тем же способом, что в clusters-3, — критерий на нём не строится.

Запуск (из корня, через обёртку с журналом):

    python morphogenesis/run_exploratory.py \
        morphogenesis/experiments/E02b_morphospace/scripts/e02b_lesion_minimal.py

Быстрая проверка сантехники на CPU (не результат):

    E02B_LESION_STEPS=50 E02B_LESION_REPEATS=1 E02B_LESION_DEVICE=cpu \
    E02B_LESION_ONLY=k3_678 python .../e02b_lesion_minimal.py
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
OUT = EXP / "lesion_minimal_exploratory.json"
ROWS = EXP / "lesion_minimal_rows.jsonl"
DEVICE = e02b._device_from_arg(os.environ.get("E02B_LESION_DEVICE", "auto"))
STEPS = int(os.environ.get("E02B_LESION_STEPS", 2000))
EVERY = 50
REPEATS = int(os.environ.get("E02B_LESION_REPEATS", 12))
ONLY = [x.strip() for x in os.environ.get("E02B_LESION_ONLY", "").split(",") if x.strip()]
SMOKE = bool(ONLY)
if SMOKE:
    # Проверка сантехники не должна перезаписывать будущий настоящий артефакт.
    OUT = EXP / "lesion_minimal_smoke.json"
    ROWS = EXP / "lesion_minimal_smoke_rows.jsonl"

DEAD_ALIVE = 0.05
IOU_MIN = 0.5
HITS_MIN = 11
ALIVE_OPEN = 8.0
SIZE = 64
FAMILY = "WP4_R-9_s2000_seed42"
PROTO_SEED = 35

VIS = config.VISIBLE_CHANNEL
ALIV = config.ALIVE_CHANNEL
HIDDEN = list(range(2, 15))  # 2..14 — то же множество, что GROUP_A + GROUP_B

# 16 наборов из плана: один канал из каждой половины, соседние пары и тройки
# из начала/середины/конца списка. Список зафиксирован до прогона.
CH9_SETS = {
    "k1_2": (2,),
    "k1_4": (4,),
    "k1_6": (6,),
    "k1_8": (8,),
    "k1_10": (10,),
    "k1_12": (12,),
    "k1_14": (14,),
    "k2_23": (2, 3),
    "k2_56": (5, 6),
    "k2_89": (8, 9),
    "k2_1112": (11, 12),
    "k2_1314": (13, 14),
    "k3_234": (2, 3, 4),
    "k3_678": (6, 7, 8),
    "k3_101112": (10, 11, 12),
    "k3_121314": (12, 13, 14),
}
CONTROL_SET = "k3_678"  # тот же набор для untrained-контроля
GEOMETRIES = [(40, 24), (38, 26)]  # (левый срез по столбцу, правый срез по столбцу)
AB7_MIN = 0.05
AB7_MAX = 0.10

# --- та же подготовка проекции, что в clusters-3 ------------------------------
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


def apply_channels(proto_state, keep):
    """visible=0, alive=+8, скрытые каналы 2..14 вне набора обнулены."""
    out = proto_state.clone()
    keep = set(int(c) for c in keep)
    out[:, VIS] = 0.0
    out[:, ALIV] = ALIVE_OPEN
    for c in HIDDEN:
        if c not in keep:
            out[:, c] = 0.0
    return out


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


def run_ch9():
    print(f"[lesion] H-CH-9: {FAMILY}, visible=0, alive=+{ALIVE_OPEN:g}, "
          f"{len(CH9_SETS)} наборов, {REPEATS} повторов, {STEPS} шагов", flush=True)
    model, proto_state = build_prototype(FAMILY, PROTO_SEED, True)
    try:
        proto_desc, proto_cid = classify(proto_state)
        proto_class = names.get(proto_cid, "outlier")
        _pa, proto_binary, _pv = arrays(proto_state)
        proto_stress = model.stress_ema.detach().clone()
        conditions = {}
        sets = [(k, v) for k, v in CH9_SETS.items() if not ONLY or k in ONLY]
        if not ONLY:
            sets = [("none", None)] + sets
        for cond_idx, (name, keep) in enumerate(sets):
            rows = []
            for rep in range(REPEATS):
                if keep is None:
                    host = proto_state.clone()
                else:
                    host = apply_channels(proto_state, keep)
                p_seed = 910000 + cond_idx * 100 + rep
                desc, cid, alive, binary = run_rollout(
                    model, proto_stress, host, p_seed
                )
                row = {
                    "section": "H-CH-9",
                    "family": FAMILY,
                    "condition": name,
                    "channels": list(keep) if keep else None,
                    "size": len(keep) if keep else 0,
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
                "size": rows[0]["size"],
                "channels": rows[0]["channels"],
                "body_returned": sum(1 for r in rows if r["body_returned"]),
                "alive": sum(1 for r in rows if r["alive_fraction"] >= DEAD_ALIVE),
                "classes": dict(Counter(r["final_class"] for r in rows)),
                "mean_body_iou": round(float(np.mean([r["body_iou"] for r in rows])), 4),
            }
            conditions[name] = entry
            print(
                f"[lesion] {name:12s} размер {entry['size']:d} тело "
                f"{entry['body_returned']}/{entry['n']} (IoU {entry['mean_body_iou']:.3f}), "
                f"классы {entry['classes']}",
                flush=True,
            )

        # untrained-контроль тем же набором: если он тоже возвращает тело,
        # метрика не различает обученное и необученное (условие вердикта).
        untrained = None
        if not SMOKE:
            t_model, t_proto = build_prototype("untrained_current_arch", 0, False)
            try:
                _td, _tc = classify(t_proto)
                _pa2, t_proto_binary, _pv2 = arrays(t_proto)
                t_stress = t_model.stress_ema.detach().clone()
                rows = []
                for rep in range(REPEATS):
                    host = apply_channels(t_proto, CH9_SETS[CONTROL_SET])
                    p_seed = 960000 + rep
                    desc, cid, alive, binary = run_rollout(
                        t_model, t_stress, host, p_seed
                    )
                    row = {
                        "section": "H-CH-9-untrained",
                        "family": "untrained_current_arch",
                        "condition": CONTROL_SET,
                        "channels": list(CH9_SETS[CONTROL_SET]),
                        "size": len(CH9_SETS[CONTROL_SET]),
                        "rep": rep,
                        "p_seed": p_seed,
                        "final_class": names.get(cid, "outlier"),
                        "alive_fraction": float(desc["alive_fraction"]),
                        "body_iou": iou(binary, t_proto_binary),
                    }
                    row["body_returned"] = bool(row["body_iou"] >= IOU_MIN)
                    emit(row)
                    rows.append(row)
                untrained = {
                    "n": len(rows),
                    "body_returned": sum(1 for r in rows if r["body_returned"]),
                    "alive": sum(1 for r in rows if r["alive_fraction"] >= DEAD_ALIVE),
                    "classes": dict(Counter(r["final_class"] for r in rows)),
                    "mean_body_iou": round(float(np.mean([r["body_iou"] for r in rows])), 4),
                }
                print(
                    f"[lesion] untrained {CONTROL_SET} тело "
                    f"{untrained['body_returned']}/{untrained['n']} "
                    f"(IoU {untrained['mean_body_iou']:.3f})",
                    flush=True,
                )
            finally:
                del t_model

        none_ok = conditions.get("none", {}).get("body_returned", REPEATS)
        hits = [
            name
            for name, st in conditions.items()
            if name != "none" and st["size"] <= 3 and st["body_returned"] >= HITS_MIN
        ]
        control_broken = none_ok < HITS_MIN
        metric_broken = bool(untrained) and untrained["body_returned"] > 1
        if control_broken:
            verdict = "invalid_none_control"
        elif metric_broken:
            verdict = "inconclusive_untrained_returns_body"
        elif hits:
            smallest = min(conditions[n]["size"] for n in hits)
            verdict = "H-CH-9_confirmed"
        else:
            verdict = "H-CH-9_refuted"
        threshold = (
            min(conditions[n]["size"] for n in hits) if hits else None
        )
        smallest_any = min(
            (st["size"] for n, st in conditions.items() if n != "none" and st["body_returned"] > 0),
            default=None,
        )
        ch9 = {
            "criterion": f"body_returned (IoU >= {IOU_MIN}) >= {HITS_MIN}/{REPEATS} "
                         f"хотя бы для одного набора размера <= 3",
            "none_body_returned": none_ok,
            "sufficient_sets": hits,
            "min_sufficient_size": threshold,
            "min_size_with_any_body": smallest_any,
            "untrained": untrained,
            "verdict": verdict,
            "conditions": conditions,
        }
        return {
            "family": FAMILY,
            "proto_seed": PROTO_SEED,
            "proto_class": proto_class,
            "proto_body_pixels": int(np.asarray(proto_binary).sum()),
            "ch9": ch9,
        }
    finally:
        del model


def run_ab7():
    print(f"[lesion] H-AB-7: геометрии {GEOMETRIES}, {REPEATS} шумовых сидов, "
          f"{STEPS} шагов", flush=True)
    model, proto_state = build_prototype(FAMILY, PROTO_SEED, True)
    try:
        proto_desc, proto_cid = classify(proto_state)
        _pa, proto_binary, _pv = arrays(proto_state)
        proto_stress = model.stress_ema.detach().clone()
        live = np.asarray(proto_binary).astype(bool)
        total = int(live.sum())
        cum = np.concatenate([[0], np.cumsum(live.sum(axis=0).astype(int))])
        out = {}
        for c_left, c_right in GEOMETRIES:
            key = f"c_{c_left}_{c_right}"
            f_l = float(cum[c_left]) / total if total else 0.0
            f_r = float(total - cum[c_right]) / total if total else 0.0
            pairs = []
            for rep in range(REPEATS):
                p_seed_l = 970000 + rep * 10
                p_seed_r = 970000 + rep * 10 + 1
                host_l = apply_cut(proto_state, "left", c_left)
                _d, _c, _a, bin_l = run_rollout(model, proto_stress, host_l, p_seed_l)
                host_r = apply_cut(proto_state, "right", c_right)
                _d2, _c2, _a2, bin_r = run_rollout(model, proto_stress, host_r, p_seed_r)
                iou_l = iou(bin_l, proto_binary)
                iou_r = iou(bin_r, proto_binary)
                d = iou_l - iou_r
                pairs.append({"rep": rep, "iou_left": round(iou_l, 4),
                              "iou_right": round(iou_r, 4), "diff": round(d, 4)})
                emit({
                    "section": "H-AB-7",
                    "family": FAMILY,
                    "geometry": [c_left, c_right],
                    "rep": rep,
                    "p_seed_left": p_seed_l,
                    "p_seed_right": p_seed_r,
                    "iou_left": round(iou_l, 4),
                    "iou_right": round(iou_r, 4),
                    "diff": round(d, 4),
                })
            diffs = [p["diff"] for p in pairs]
            sd = float(np.std(diffs, ddof=1)) if len(diffs) > 1 else 0.0
            entry = {
                "geometry": [c_left, c_right],
                "removed_fraction_left": round(float(f_l), 4),
                "removed_fraction_right": round(float(f_r), 4),
                "n": len(pairs),
                "mean_diff": round(float(np.mean(diffs)), 4),
                "std_diff": round(sd, 4),
                "min_diff": round(min(diffs), 4),
                "max_diff": round(max(diffs), 4),
                "n_negative": sum(1 for d in diffs if d < 0),
                "pairs": pairs,
            }
            if sd <= AB7_MIN:
                entry["verdict"] = "std_small_geometry_explains_magnitude"
            elif sd > AB7_MAX:
                entry["verdict"] = "std_large_noise_curve_forbidden"
            else:
                entry["verdict"] = "inconclusive"
            out[key] = entry
            print(
                f"[lesion] {key} mean(d)={entry['mean_diff']:+.3f} "
                f"std(d)={sd:.3f} отрицательных {entry['n_negative']}/{len(diffs)} "
                f"-> {entry['verdict']}",
                flush=True,
            )
        return {
            "criterion": f"std(d) <= {AB7_MIN} — геометрия; > {AB7_MAX} — шум",
            "geometries": out,
        }
    finally:
        del model


def main():
    started = None
    import time

    started = time.time()
    result = {
        "schema_version": 1,
        "experiment": "E02b_morphospace",
        "kind": "exploratory_lesion_minimal",
        "protocol": "reports/2026-10-22-lesion-minimal-plan.md",
        "steps": STEPS,
        "repeats": REPEATS,
        "device": str(DEVICE),
        "smoke": SMOKE,
        "ch9": None,
        "ab7": None,
    }
    if not ONLY:
        result["ch9"] = run_ch9()
        result["ab7"] = run_ab7()
    else:
        if any(k in CH9_SETS for k in ONLY):
            result["ch9"] = run_ch9()
        if "ab7" in ONLY:
            result["ab7"] = run_ab7()
    result["wall_seconds"] = round(time.time() - started, 1)
    OUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"[lesion] записано: {OUT} ({result['wall_seconds']} c)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
