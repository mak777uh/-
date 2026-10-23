"""E02c: репликация тренировочного сида R-9 (H-E02C-1).

Запускает один тренировочный сид R-9 по тому же рецепту, что WP4, но с
отдельным `experiment_id` (`E02c_R-9_s<steps>_seed<seed>`) и отдельным
каталогом чекпоинтов. Обёртка нужна потому, что `wp4_ablations.run_arm`
жёстко подставляет префикс `WP4_` и не позволяет получить `E02c_*`.

Контракт:
- overrides берутся из `wp4_ablations.ARMS["R-9"]` (тот же рецепт, без
  «улучшений»);
- `config.CHECKPOINT_DIR` временно указывает на
  `checkpoints/E02c_R-9_s<steps>_seed<seed>`;
- в `finally` восстанавливаются и `CHECKPOINT_DIR`, и все overrides;
- `stop_on_collapse=False` — нужен полный профиль траектории, как в WP4;
- по завершении проверяется наличие `nca_final.pt`, печатается размер и
  sha256; при отсутствии — exit 2.

Запуск (из корня, через лабораторный контур):

    python scripts/lab.py run \
      --experiment E02c_R-9_s2000_seed142 \
      --experiment-id E02c --arm R-9 --seed 142 --steps 2000 \
      --owner lead \
      -- .venv/Scripts/python.exe e02c_replication.py --seed 142 --steps 2000

Smoke без обучения:

    python e02c_replication.py --seed 142 --steps 20 --dry-run
"""
import argparse
import hashlib
import os
import sys

# §9.2: config обязан импортироваться раньше torch.
import config

from train import train
from wp4_ablations import ARMS, _apply


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="E02c: репликация тренировочного сида R-9")
    ap.add_argument("--seed", type=int, required=True, help="тренировочный сид (142/242/342)")
    ap.add_argument("--steps", type=int, default=2000, help="число шагов обучения")
    ap.add_argument("--arm", default="R-9", choices=sorted(ARMS))
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="только применить/проверить overrides и каталоги, без обучения",
    )
    ap.add_argument(
        "--experiment-id",
        default=None,
        help=(
            "переопределить имя каталога чекпоинта. Нужно, когда один и тот же "
            "рецепт и сид прогоняются в двух численных режимах (например TF32 и "
            "FP32): без переопределения второй прогон писал бы в тот же каталог "
            "и затирал первый. По умолчанию имя как раньше: E02c_<arm>_s<steps>_seed<seed>"
        ),
    )
    ap.add_argument(
        "--save-interval",
        type=int,
        default=None,
        help=(
            "интервал сохранения промежуточных чекпоинтов (nca_iter_*.pt). "
            "Переопределяет config.TRAIN_SAVE_INTERVAL только на время прогона: "
            "дефолт не меняется. Нужен для плотного горизонта (окна struct_2 "
            "шириной около тысячи шагов не видны при интервале 1000)."
        ),
    )
    args = ap.parse_args(argv)

    if args.arm != "R-9":
        raise SystemExit("E02c заморожен на плече R-9; другое плечо — новая серия")

    description, overrides = ARMS[args.arm]
    experiment_id = args.experiment_id or f"E02c_{args.arm}_s{args.steps}_seed{args.seed}"
    original_ckpt = config.CHECKPOINT_DIR
    target_dir = os.path.join(original_ckpt, experiment_id)

    print(f"[e02c] experiment_id={experiment_id}")
    print(f"[e02c] arm={args.arm}: {description}")
    print(f"[e02c] overrides={overrides}")
    print(f"[e02c] checkpoint_dir={target_dir}")

    restore = _apply(overrides)
    original_save_interval = config.TRAIN_SAVE_INTERVAL
    if args.save_interval is not None:
        if args.save_interval <= 0:
            raise SystemExit("--save-interval должен быть положительным")
        config.TRAIN_SAVE_INTERVAL = int(args.save_interval)
        print(f"[e02c] save_interval={args.save_interval} (дефолт был {original_save_interval})")
    config.CHECKPOINT_DIR = target_dir
    os.makedirs(target_dir, exist_ok=True)
    try:
        if args.dry_run:
            # Проверяем, что overrides реально применились и что ключи совпадают
            # с рецептом WP4; обучение не запускаем.
            print(f"[e02c] dry-run: RETENTION_ENABLED={config.RETENTION_ENABLED}")
            print(f"[e02c] dry-run: LOSS_WEIGHTS={config.LOSS_WEIGHTS}")
            return 0
        train(
            experiment_id=experiment_id,
            seed=args.seed,
            max_steps=args.steps,
            stop_on_collapse=False,
        )
    finally:
        config.CHECKPOINT_DIR = original_ckpt
        config.TRAIN_SAVE_INTERVAL = original_save_interval
        restore()

    final_path = os.path.join(original_ckpt, experiment_id, "nca_final.pt")
    if not os.path.exists(final_path):
        print(f"[e02c] ОШИБКА: нет финального чекпоинта {final_path}", file=sys.stderr)
        return 2
    size = os.path.getsize(final_path)
    print(f"[e02c] final={final_path} size={size} sha256={sha256_file(final_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
