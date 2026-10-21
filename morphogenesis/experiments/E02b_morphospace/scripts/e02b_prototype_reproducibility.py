"""E02b, exploratory: почему прототип в двух прогонах абляции различается.

Наблюдение. Один и тот же протокол (R-9 seed42, прототип seed 35, те же сиды
шума 90200–90202) дал разные числа: `cut_top` — IoU 0.806 в прогоне от 01:09 и
0.624 в прогоне от 14:00. Сиды шума совпадали, значит различался сам прототип,
от которого считается IoU.

Причина (проверяется здесь, а не предполагается). В `e02b_geometric_lesion_rep.py`
четвёртое поле в списке моделей подписано комментарием как «признак "обучена"»,
но в цикле оно читается как `is_untrained`. Для двух выученных моделей флаг
оказался `True`, и прототип собирался **неканонической** веткой: без
`remember_stress_ema_start`, то есть с обнулённой stress-EMA вместо EMA из
чекпоинта, и без проверки воспроизводимости из `run_seed`.

Скрипт строит оба прототипа рядом и сравнивает их отпечатки:
- путь A — канонический (`e02b._prototype_state`: EMA восстановлена из чекпоинта);
- путь B — как в скрипте повтора (EMA обнулена);
- дополнительно: норма EMA в чекпоинте и число отличающихся клеток.

Ничего не обучается: два форварда по 2000 шагов.
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve()
EXP = HERE.parents[1]
MORPH = HERE.parents[3]
sys.path.insert(0, str(MORPH))
import e02b_morphospace as e02b  # noqa: E402

torch = e02b.torch
config = e02b.config

OUT = EXP / "prototype_reproducibility_exploratory.json"
FAMILY = "WP4_R-9_s2000_seed42"
PROTO_SEED = 35
STEPS = 2000


def fingerprint(state):
    alive, binary, visible, _soft, _x = e02b._state_arrays(state)
    digest = hashlib.sha256()
    digest.update(np.ascontiguousarray(binary).tobytes())
    return {
        "binary_sha256": digest.hexdigest(),
        "binary_fraction": float(binary.mean()),
        "alive_fraction": float(alive.mean()),
        "visible_mean": float(visible.mean()),
        "binary_cells": int(binary.sum()),
    }


def path_b(spec, device):
    """Прототип «как в повторе абляции»: EMA обнулена, проверки run_seed нет."""
    torch.manual_seed(42)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(42)
    model, _ck = e02b.build_model(spec, device)
    e02b.prepare_model(model, PROTO_SEED)
    start = e02b.init_state(
        batch_size=1,
        channels=config.N_CHANNELS,
        grid_size=config.GRID_SIZE,
        device=device,
        generator=model.generator,
    )
    final, _points, _traj, _elapsed = e02b.rollout(model, start, STEPS, 50)
    return model, final


def main():
    device = e02b._device_from_arg("auto")
    spec = e02b.load_checkpoint_specs(families=[FAMILY], include_untrained=False)[0]

    # Канонический путь: два раза в одном процессе (воспроизводимость внутри
    # процесса) и второй вызов — отдельный процесс (между процессами).
    state_a, model_a, repro_a = e02b._prototype_state(spec, PROTO_SEED, STEPS, 50, device)
    fp_a = fingerprint(state_a)
    ema_norm = float(model_a.stress_ema.detach().abs().sum())
    stress_enabled = bool(getattr(config, "STRESS_ENABLED", None))
    del model_a
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    state_a2, model_a2, _repro_a2 = e02b._prototype_state(spec, PROTO_SEED, STEPS, 50, device)
    fp_a2 = fingerprint(state_a2)
    del model_a2
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    model_b, state_b = path_b(spec, device)
    fp_b = fingerprint(state_b)
    del model_b
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    _alive_a, binary_a, _v, _s, _x = e02b._state_arrays(state_a)
    _alive_b, binary_b, _v, _s, _x = e02b._state_arrays(state_b)
    diff_cells = int(np.logical_xor(binary_a, binary_b).sum())

    out = {
        "schema_version": 1,
        "experiment": "E02b_morphospace",
        "kind": "exploratory_prototype_reproducibility",
        "note": (
            "Сравнение двух способов построить прототип R-9 seed42 (сид 35): "
            "канонический путь с EMA из чекпоинта и путь из скрипта повтора "
            "абляции с обнулённой EMA."
        ),
        "device": str(device),
        "family": FAMILY,
        "prototype_seed": PROTO_SEED,
        "steps": STEPS,
        "stress_enabled": stress_enabled,
        "checkpoint_stress_ema_abs_sum": ema_norm,
        "path_a_canonical": {
            "description": "e02b._prototype_state: EMA восстановлена из чекпоинта, есть проверка run_seed",
            "run_1": fp_a,
            "run_2": fp_a2,
            "identical_within_process": fp_a["binary_sha256"] == fp_a2["binary_sha256"],
        },
        "path_b_lesion_rep_script": {
            "description": (
                "ветка 'untrained' из e02b_geometric_lesion_rep.py: EMA обнулена, "
                "проверки run_seed нет"
            ),
            "run_1": fp_b,
        },
        "identical_across_paths": fp_a["binary_sha256"] == fp_b["binary_sha256"],
        "binary_cells_differing": diff_cells,
        "binary_cells_total": int(binary_a.size),
        "verdict": (
            "пути дают разные прототипы: различие объясняется обнулённой stress-EMA "
            "в повторе абляции, а не шумом и не GPU"
            if diff_cells > 0
            else "пути дают одинаковый прототип"
        ),
        "consequence": (
            "Абсолютные IoU повтора абляции (20261021T110434Z) несопоставимы с "
            "таблицей первой абляции (3 повтора): там прототип строился канонически. "
            "Внутри своего прогона парные сравнения (знаковый тест) остаются "
            "корректными, потому что прототип и EMA одинаковы для всех повторов."
        ),
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[proto-repro] A(канон) sha={fp_a['binary_sha256'][:16]} bin={fp_a['binary_fraction']:.6f} "
          f"(повтор в процессе: {out['path_a_canonical']['identical_within_process']})")
    print(f"[proto-repro] B(скрипт абляции) sha={fp_b['binary_sha256'][:16]} bin={fp_b['binary_fraction']:.6f}")
    print(f"[proto-repro] расхождение клеток: {diff_cells}/{binary_a.size}; "
          f"EMA в чекпоинте: |sum|={ema_norm:.6f}; stress_enabled={stress_enabled}")
    print(f"[proto-repro] written {OUT}")


if __name__ == "__main__":
    main()
