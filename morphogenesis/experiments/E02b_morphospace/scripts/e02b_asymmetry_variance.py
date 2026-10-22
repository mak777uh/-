r"""E02b asymmetry-variance: откуда разброс величины асимметрии (H-AB-8).

Протокол заморожен до запуска: `reports/2026-10-22-asymmetry-variance-plan.md`.

H-AB-7 показала, что при фиксированной геометрии `std(d)` = 0.167 (c=40/24),
то есть величина асимметрии — шум. Вопрос H-AB-8: шум сидит в **конечном
состоянии** или в **динамике**? Если в динамике, `d` коррелирует с разницей
моментов восстановления `dt = t_body_left − t_body_right` (снимки каждые 25
шагов, порог IoU >= 0.5).

Критерий до прогона: подтверждена при |Spearman(d, dt)| >= 0.5 (n = 12);
опровергнута при меньшем.

Запуск (из корня, через обёртку с журналом):

    python morphogenesis/run_exploratory.py \
        morphogenesis/experiments/E02b_morphospace/scripts/e02b_asymmetry_variance.py

CPU-дым (не результат):

    E02B_VAR_STEPS=50 E02B_VAR_REPEATS=2 E02B_VAR_DEVICE=cpu \
    python .../e02b_asymmetry_variance.py --smoke
"""
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
EXP = HERE.parents[1]
sys.path.insert(0, str(HERE.parents[3]))
import e02b_morphospace as e02b  # noqa: E402

torch = e02b.torch
config = e02b.config
np = e02b.np

CENSUS = EXP / "census.json"
OUT = EXP / "asymmetry_variance_exploratory.json"
ROWS = EXP / "asymmetry_variance_rows.jsonl"
SMOKE_ROWS = EXP / "asymmetry_variance_smoke_rows.jsonl"
DEVICE = e02b._device_from_arg(os.environ.get("E02B_VAR_DEVICE", "auto"))
STEPS = int(os.environ.get("E02B_VAR_STEPS", 2000))
EVERY = 25
REPEATS = int(os.environ.get("E02B_VAR_REPEATS", 12))
SMOKE = "--smoke" in sys.argv

IOU_MIN = 0.5
FAMILY = "WP4_R-9_s2000_seed42"
PROTO_SEED = 35
GEOMETRY = (40, 24)  # левый срез по столбцу 40, правый по 24
SIZE = 64

if SMOKE:
    OUT = EXP / "asymmetry_variance_smoke.json"
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


def rollout_with_trace(model, proto_stress, host, p_seed, proto_binary):
    """Роллаут с проверкой IoU каждые EVERY шагов: возвращает (iou_final, t_body)."""
    gen = config.create_deterministic_generator(p_seed)
    model.set_generator(gen)
    model.stress_ema.copy_(proto_stress)
    model._noise_cache = {}
    model._noise_seq = 0
    model.begin_segment()
    state = host
    t_body = None
    step = 0
    while step < STEPS:
        for _ in range(min(EVERY, STEPS - step)):
            with torch.no_grad():
                state = model(state)
        step += EVERY
        _alive, binary, _visible = arrays(state)
        value = iou(binary, proto_binary)
        if t_body is None and value >= IOU_MIN:
            t_body = step
    _alive, binary, _visible = arrays(state)
    iou_final = iou(binary, proto_binary)
    return iou_final, t_body


def emit(row):
    with open(ROWS, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def spearman(a, b):
    """Spearman без scipy: ранги, затем Пирсон."""
    if len(a) < 3:
        return 0.0
    ra = np.argsort(np.argsort(np.asarray(a, dtype=float)))
    rb = np.argsort(np.argsort(np.asarray(b, dtype=float)))
    ra = ra - ra.mean()
    rb = rb - rb.mean()
    denom = float(np.sqrt((ra**2).sum() * (rb**2).sum()))
    return float((ra * rb).sum() / denom) if denom else 0.0


def main():
    import time

    started = time.time()
    model, proto_state = build_prototype()
    try:
        proto_desc, proto_cid = classify(proto_state)
        proto_class = names.get(proto_cid, "outlier")
        _pa, proto_binary, _pv = arrays(proto_state)
        proto_stress = model.stress_ema.detach().clone()
        c_left, c_right = GEOMETRY
        print(
            f"[var] прототип {proto_class}; геометрия {GEOMETRY}; {REPEATS} сидов, "
            f"{STEPS} шагов, снимок каждые {EVERY}",
            flush=True,
        )
        pairs = []
        for rep in range(REPEATS):
            p_seed_l = 995000 + rep * 10
            p_seed_r = 995000 + rep * 10 + 1
            host_l = apply_cut(proto_state, "left", c_left)
            iou_l, t_l = rollout_with_trace(model, proto_stress, host_l, p_seed_l, proto_binary)
            host_r = apply_cut(proto_state, "right", c_right)
            iou_r, t_r = rollout_with_trace(model, proto_stress, host_r, p_seed_r, proto_binary)
            marker = (STEPS // EVERY) + 1
            t_l_m = t_l if t_l is not None else marker
            t_r_m = t_r if t_r is not None else marker
            pair = {
                "rep": rep,
                "iou_left": round(iou_l, 4),
                "iou_right": round(iou_r, 4),
                "diff": round(iou_l - iou_r, 4),
                "t_body_left": t_l_m,
                "t_body_right": t_r_m,
                "dt": t_l_m - t_r_m,
                "left_recovered": t_l is not None,
                "right_recovered": t_r is not None,
            }
            pairs.append(pair)
            emit({"section": "H-AB-8", "geometry": list(GEOMETRY), **pair})
            print(
                f"[var] сид {rep:2d}: d={pair['diff']:+.3f} "
                f"t_left={t_l_m:2d} t_right={t_r_m:2d} dt={pair['dt']:+d}",
                flush=True,
            )

        diffs = [p["diff"] for p in pairs]
        dts = [p["dt"] for p in pairs]
        rho = spearman(diffs, dts)
        both = sum(1 for p in pairs if p["left_recovered"] and p["right_recovered"])
        payload = {
            "schema_version": 1,
            "experiment": "E02b_morphospace",
            "kind": "exploratory_asymmetry_variance",
            "protocol": "reports/2026-10-22-asymmetry-variance-plan.md",
            "family": FAMILY,
            "proto_seed": PROTO_SEED,
            "proto_class": proto_class,
            "geometry": list(GEOMETRY),
            "steps": STEPS,
            "snapshot_every": EVERY,
            "repeats": REPEATS,
            "criterion": "|Spearman(d, dt)| >= 0.5 при n = 12",
            "spearman_d_dt": round(rho, 4),
            "n_pairs": len(pairs),
            "n_both_recovered": both,
            "n_left_recovered": sum(1 for p in pairs if p["left_recovered"]),
            "n_right_recovered": sum(1 for p in pairs if p["right_recovered"]),
            "mean_diff": round(float(np.mean(diffs)), 4),
            "std_diff": round(float(np.std(diffs, ddof=1)), 4),
            "mean_dt": round(float(np.mean(dts)), 4),
            "pairs": pairs,
            "verdict": "H-AB-8_confirmed" if abs(rho) >= 0.5 else "H-AB-8_refuted",
            "wall_seconds": round(time.time() - started, 1),
        }
        OUT.write_text(
            json.dumps(payload if not SMOKE else {"smoke": True, **payload}, ensure_ascii=False, indent=2)
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(
            f"[var] rho={rho:+.3f} (n={len(pairs)}, оба восстановились {both}), "
            f"std(d)={payload['std_diff']:.3f} -> {payload['verdict']}",
            flush=True,
        )
        print(f"[var] записано: {OUT} ({payload['wall_seconds']} c)", flush=True)
        return 0
    finally:
        del model


if __name__ == "__main__":
    raise SystemExit(main())
