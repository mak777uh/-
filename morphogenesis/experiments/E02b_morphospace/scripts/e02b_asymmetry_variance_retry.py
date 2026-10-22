r"""E02b asymmetry-variance retry: время выхода на плато (H-AB-8, пере-дизайн).

Протокол заморожен до запуска: `reports/2026-10-22-asymmetry-variance-retry-plan.md`.

Первый прогон выродился: порог тела IoU >= 0.5 достигается на первом-втором
снимке, `dt` = +25 у всех 12 пар. Здесь метрика другая — `t_plateau`: первый
снимок (каждые 10 шагов), после которого IoU меняется не больше чем на 0.02 до
конца прогона. Вопрос тот же: связан ли разброс `d` с разницей времён.

Критерий до прогона: подтверждена при |Spearman(d, dt_plateau)| >= 0.5 и
непустой дисперсии dt; опровергнута при непустой дисперсии и меньшем rho;
inconclusive, если dt_plateau снова константа.

Запуск (из корня, через обёртку с журналом):

    python morphogenesis/run_exploratory.py \
        morphogenesis/experiments/E02b_morphospace/scripts/e02b_asymmetry_variance_retry.py

CPU-дым (не результат):

    E02B_VARR_STEPS=400 E02B_VARR_REPEATS=2 E02B_VARR_DEVICE=cpu \
    python .../e02b_asymmetry_variance_retry.py --smoke
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
OUT = EXP / "asymmetry_variance_retry_exploratory.json"
ROWS = EXP / "asymmetry_variance_retry_rows.jsonl"
SMOKE_ROWS = EXP / "asymmetry_variance_retry_smoke_rows.jsonl"
DEVICE = e02b._device_from_arg(os.environ.get("E02B_VARR_DEVICE", "auto"))
STEPS = int(os.environ.get("E02B_VARR_STEPS", 2000))
EVERY = 10
REPEATS = int(os.environ.get("E02B_VARR_REPEATS", 12))
SMOKE = "--smoke" in sys.argv

PLATEAU_TOL = 0.02
FAMILY = "WP4_R-9_s2000_seed42"
PROTO_SEED = 35
GEOMETRY = (40, 24)

if SMOKE:
    OUT = EXP / "asymmetry_variance_retry_smoke.json"
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


def iou(a, b):
    u = np.logical_or(a, b).sum()
    return float(np.logical_and(a, b).sum() / u) if u else 1.0


def build_prototype():
    spec = e02b.load_checkpoint_specs(families=[FAMILY], include_untrained=False)[0]
    final, model, _run = e02b._prototype_state(spec, PROTO_SEED, STEPS, 50, DEVICE)
    return model, final


def apply_cut(proto_state, side, col):
    host = proto_state.clone()
    if side == "left":
        host[:, :, :, :col] = 0.0
    else:
        host[:, :, :, col:] = 0.0
    return host


def rollout_trace(model, proto_stress, host, p_seed, proto_binary):
    gen = config.create_deterministic_generator(p_seed)
    model.set_generator(gen)
    model.stress_ema.copy_(proto_stress)
    model._noise_cache = {}
    model._noise_seq = 0
    model.begin_segment()
    state = host
    trace = []
    step = 0
    while step < STEPS:
        for _ in range(min(EVERY, STEPS - step)):
            with torch.no_grad():
                state = model(state)
        step += EVERY
        _alive, binary, _visible = arrays(state)
        trace.append((step, iou(binary, proto_binary)))
    return trace


def plateau_step(trace):
    """Первый снимок, после которого IoU не уходит больше чем на PLATEAU_TOL."""
    values = [v for _s, v in trace]
    if not values:
        return None
    best = len(values) - 1
    lo = hi = values[-1]
    for i in range(len(values) - 2, -1, -1):
        lo = min(lo, values[i])
        hi = max(hi, values[i])
        if hi - lo <= PLATEAU_TOL:
            best = i
        else:
            break
    return trace[best][0]


def spearman(a, b):
    if len(a) < 3:
        return 0.0
    ra = np.argsort(np.argsort(np.asarray(a, dtype=float))).astype(float)
    rb = np.argsort(np.argsort(np.asarray(b, dtype=float))).astype(float)
    ra -= ra.mean()
    rb -= rb.mean()
    denom = float(np.sqrt((ra**2).sum() * (rb**2).sum()))
    return float((ra * rb).sum() / denom) if denom else 0.0


def emit(row):
    with open(ROWS, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def main():
    import time

    started = time.time()
    model, proto_state = build_prototype()
    try:
        proto_class = "unknown"
        _pa, proto_binary, _pv = arrays(proto_state)
        proto_stress = model.stress_ema.detach().clone()
        c_left, c_right = GEOMETRY
        print(
            f"[varr] геометрия {GEOMETRY}; {REPEATS} сидов, {STEPS} шагов, снимок каждые {EVERY}, "
            f"порог плато {PLATEAU_TOL}",
            flush=True,
        )
        pairs = []
        marker = (STEPS // EVERY) + 1
        for rep in range(REPEATS):
            p_seed_l = 996000 + rep * 10
            p_seed_r = 996000 + rep * 10 + 1
            trace_l = rollout_trace(
                model, proto_stress, apply_cut(proto_state, "left", c_left), p_seed_l, proto_binary
            )
            trace_r = rollout_trace(
                model, proto_stress, apply_cut(proto_state, "right", c_right), p_seed_r, proto_binary
            )
            iou_l = trace_l[-1][1]
            iou_r = trace_r[-1][1]
            tp_l = plateau_step(trace_l)
            tp_r = plateau_step(trace_r)
            pair = {
                "rep": rep,
                "iou_left": round(iou_l, 4),
                "iou_right": round(iou_r, 4),
                "diff": round(iou_l - iou_r, 4),
                "t_plateau_left": tp_l if tp_l is not None else marker * EVERY,
                "t_plateau_right": tp_r if tp_r is not None else marker * EVERY,
            }
            pair["dt_plateau"] = pair["t_plateau_left"] - pair["t_plateau_right"]
            pairs.append(pair)
            emit({"section": "H-AB-8-retry", "geometry": list(GEOMETRY), **pair})
            print(
                f"[varr] сид {rep:2d}: d={pair['diff']:+.3f} "
                f"tp_left={pair['t_plateau_left']:4d} tp_right={pair['t_plateau_right']:4d} "
                f"dt={pair['dt_plateau']:+d}",
                flush=True,
            )

        diffs = [p["diff"] for p in pairs]
        dts = [p["dt_plateau"] for p in pairs]
        sd = float(np.std(dts, ddof=1)) if len(dts) > 1 else 0.0
        rho = spearman(diffs, dts)
        if sd == 0.0:
            verdict = "H-AB-8_inconclusive"
        elif abs(rho) >= 0.5:
            verdict = "H-AB-8_confirmed"
        else:
            verdict = "H-AB-8_refuted"
        payload = {
            "schema_version": 1,
            "experiment": "E02b_morphospace",
            "kind": "exploratory_asymmetry_variance_retry",
            "protocol": "reports/2026-10-22-asymmetry-variance-retry-plan.md",
            "family": FAMILY,
            "proto_seed": PROTO_SEED,
            "geometry": list(GEOMETRY),
            "steps": STEPS,
            "snapshot_every": EVERY,
            "plateau_tol": PLATEAU_TOL,
            "repeats": REPEATS,
            "criterion": "|Spearman(d, dt_plateau)| >= 0.5 при непустой дисперсии dt",
            "spearman_d_dt": round(rho, 4),
            "std_dt": round(sd, 4),
            "mean_dt": round(float(np.mean(dts)), 4),
            "mean_diff": round(float(np.mean(diffs)), 4),
            "std_diff": round(float(np.std(diffs, ddof=1)), 4),
            "pairs": pairs,
            "verdict": verdict,
            "wall_seconds": round(time.time() - started, 1),
        }
        OUT.write_text(
            json.dumps(payload if not SMOKE else {"smoke": True, **payload}, ensure_ascii=False, indent=2)
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(
            f"[varr] rho={rho:+.3f} std(dt)={sd:.1f} std(d)={payload['std_diff']:.3f} -> {verdict}",
            flush=True,
        )
        print(f"[varr] записано: {OUT} ({payload['wall_seconds']} c)", flush=True)
        return 0
    finally:
        del model


if __name__ == "__main__":
    raise SystemExit(main())
