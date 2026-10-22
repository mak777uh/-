"""E02c: декомпозиция тренировочного сида (H-E02C-5).

Один «сид» в этих прогонах задаёт сразу три вещи: инициализацию весов,
начальное поле/пул и порядок обучающих сэмплов и шума. Этот скрипт разводит
первый фактор (`init_seed`) и второй (`data_seed`).

Два прогона протокола (`reports/2026-10-22-e02c-seed-decomposition-plan.md`):

    A: init_seed=42,  data_seed=101
    B: init_seed=101, data_seed=42

Контракт:
- overrides — из `wp4_ablations.ARMS["R-9"]` (тот же рецепт, что E02c);
- `config.CHECKPOINT_DIR` временно указывает на
  `checkpoints/E02c_seeddec_init<init>_data<data>`;
- в `finally` восстанавливаются каталог и overrides;
- `stop_on_collapse=False`, 2000 шагов, batch 8, цель ring;
- после финиша проверяется `nca_final.pt`, печатается размер и sha256.

Смоук (без обучения, ~1 мин):

    python e02c_seed_decomposition.py --smoke

Проверяет три вещи:
1. регрессия: `seed=42` и `init_seed=42, data_seed=42` дают побитово равные веса
   на коротком горизонте;
2. факторы действительно разные: хэш начальных весов при init=42 и init=101
   различается, порядок первых батчей при data=42 и data=101 различается;
3. раскладка маршрутизирует факторы: при init=42/data=101 веса совпадают с
   init=42, а батчи — с data=101.
"""
import argparse
import hashlib
import os
import sys

# §9.2: config обязан импортироваться раньше torch.
import config

import torch

from nca_core import NeuralCellularAutomaton
from train import train
from wp4_ablations import ARMS, _apply

RUNS = {
    "A": {"init_seed": 42, "data_seed": 101},
    "B": {"init_seed": 101, "data_seed": 42},
}


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def state_dict_hash(model: NeuralCellularAutomaton) -> str:
    h = hashlib.sha256()
    for key, value in model.state_dict().items():
        h.update(key.encode("utf-8"))
        h.update(value.detach().cpu().numpy().tobytes())
    return h.hexdigest()


def initial_state_hash(init_seed: int) -> str:
    """Хэш весов сразу после инициализации (без обучения)."""
    config.set_seed(init_seed)
    fresh = NeuralCellularAutomaton(channels=config.N_CHANNELS)
    return state_dict_hash(fresh)


def first_batch_indices(data_seed: int, n_batches: int = 8):
    """Индексы первых выборок из пула при заданном сиде данных.

    `StatePool.sample()` возвращает (state, index) — один индекс за вызов;
    последовательность индексов и есть «порядок данных».
    """
    from nca_core import StatePool

    gen = config.create_deterministic_generator(data_seed)
    pool = StatePool(
        size=config.TRAIN_SAMPLE_POOL_SIZE,
        device=torch.device("cpu"),
        generator=gen,
        batch_size=config.TRAIN_BATCH_SIZE,
    )
    return [int(pool.sample()[1]) for _ in range(n_batches)]


def _train_once(init_seed: int, data_seed: int, steps: int, experiment_id: str,
                checkpoint_dir: str) -> str:
    description, overrides = ARMS["R-9"]
    original = config.CHECKPOINT_DIR
    restore = _apply(overrides)
    config.CHECKPOINT_DIR = checkpoint_dir
    os.makedirs(checkpoint_dir, exist_ok=True)
    try:
        train(
            experiment_id=experiment_id,
            seed=init_seed,
            init_seed=init_seed,
            data_seed=data_seed,
            max_steps=steps,
            stop_on_collapse=False,
        )
    finally:
        config.CHECKPOINT_DIR = original
        restore()
    final = os.path.join(checkpoint_dir, "nca_final.pt")
    if not os.path.exists(final):
        raise SystemExit(f"[seeddec] ОШИБКА: нет {final}")
    return final


def smoke() -> int:
    """Три проверки протокола. Возвращает 0, если все сошлись."""
    import tempfile

    problems = []

    # 2. Факторы действительно разные.
    init42 = initial_state_hash(42)
    init101 = initial_state_hash(101)
    if init42 == init101:
        problems.append("init_seed не влияет на веса: хэши init=42 и init=101 совпали")

    batch42 = first_batch_indices(42)
    batch101 = first_batch_indices(101)
    if batch42 == batch101:
        problems.append("data_seed не влияет на порядок батчей: data=42 и data=101 совпали")

    # 1. Регрессия: None-дефолты эквивалентны явной раскладке.
    with tempfile.TemporaryDirectory() as tmp:
        steps = 5
        d1 = os.path.join(tmp, "plain")
        d2 = os.path.join(tmp, "explicit")
        f1 = _train_once(42, 42, steps, "seeddec_smoke_plain", d1)
        f2 = _train_once(42, 42, steps, "seeddec_smoke_explicit", d2)
        w1 = torch.load(f1, map_location="cpu", weights_only=False)["model_state_dict"]
        w2 = torch.load(f2, map_location="cpu", weights_only=False)["model_state_dict"]
        if not all(torch.equal(w1[k], w2[k]) for k in w1):
            problems.append("регрессия: seed=42 и init=data=42 дали разные веса")

    # 3. Маршрутизация: init=42/data=101 — веса от 42, батчи от 101.
    routed_batches = first_batch_indices(RUNS["A"]["data_seed"])
    if routed_batches != batch101:
        problems.append("раскладка A не маршрутизирует data_seed в порядок батчей")

    print("[seeddec] init hash 42:", init42[:16], "| 101:", init101[:16])
    print("[seeddec] порядок данных 42:", batch42[:6], "| 101:", batch101[:6])
    if problems:
        for item in problems:
            print("[seeddec] ПРОВАЛ:", item, file=sys.stderr)
        return 3
    print("[seeddec] смоук пройден: факторы разделяются, регрессии нет")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="E02c: декомпозиция тренировочного сида")
    ap.add_argument("--run", choices=sorted(RUNS), help="A (init 42/data 101) или B (init 101/data 42)")
    ap.add_argument("--steps", type=int, default=2000)
    ap.add_argument("--smoke", action="store_true", help="три проверки без обучения")
    ap.add_argument("--dry-run", action="store_true", help="только применить overrides")
    args = ap.parse_args(argv)

    if args.smoke:
        return smoke()

    if not args.run:
        raise SystemExit("нужен --run A|B или --smoke")
    layout = RUNS[args.run]
    experiment_id = f"E02c_seeddec_init{layout['init_seed']}_data{layout['data_seed']}"
    target_dir = os.path.join(config.CHECKPOINT_DIR, experiment_id)

    print(f"[seeddec] run={args.run} init_seed={layout['init_seed']} "
          f"data_seed={layout['data_seed']} experiment_id={experiment_id}")
    if args.dry_run:
        _, overrides = ARMS["R-9"]
        restore = _apply(overrides)
        try:
            print(f"[seeddec] dry-run: RETENTION_ENABLED={config.RETENTION_ENABLED} "
                  f"LOSS_WEIGHTS={config.LOSS_WEIGHTS}")
        finally:
            restore()
        return 0

    final = _train_once(layout["init_seed"], layout["data_seed"], args.steps,
                        experiment_id, target_dir)
    size = os.path.getsize(final)
    print(f"[seeddec] final={final} size={size} sha256={sha256_file(final)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
