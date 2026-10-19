"""

conftest.py — фиксация окружения для тестов (слой 0, §9.2 / §11).

Две проблемы, которые решаются здесь, иначе тесты врут:

1. Все пути в config.py относительные (CHECKPOINT_DIR="checkpoints" и т.д.), и

   прод-код обязан запускаться из каталога morphogenesis/. Если pytest запущен из

   корня репозитория, тесты писали артефакты в repo/memory, repo/outputs — так и

   появлялись «мусорные» каталоги в корне и расхождение с реальным прогоном.

2. Тесты вставляли путь пакета друг в друга 7 раз копипастой sys.path.insert;

   один conftest заменяет их все.

"""

import os

import sys

PKG_DIR = os.path.dirname(os.path.abspath(__file__))

if PKG_DIR not in sys.path:

    sys.path.insert(0, PKG_DIR)

# Импорты модулей проекта — только после того, как пакет в sys.path.

import config  # noqa: E402  (§9.2: config раньше torch)

# Относительные пути config обязаны резолвиться туда же, куда и в проде.

if os.path.abspath(os.getcwd()) != PKG_DIR:

    os.chdir(PKG_DIR)


def pytest_report_header():

    """Видно в выводе pytest: на каком железе и с какой верией спеки гоняли тесты."""

    import torch

    return [

        f"morphogenesis spec={config.SPEC_VERSION} {config.SPEC_REVISION}",

        f"torch={torch.__version__} device={config.DEVICE} "

        f"cuda_usable={config.CUDA_USABLE} n_devices={config.CUDA_DEVICE_COUNT}",

        f"cwd={os.getcwd()}",

    ]
