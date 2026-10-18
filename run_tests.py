"""

run_tests.py — локальный «CI» для одного человека (замена GitHub Actions).

Запуск из корня репозитория:

    python run_tests.py            # pytest + smoke_test
    python run_tests.py --quick    # только pytest

Все пути в config.py относительны, поэтому рабочим каталогом обязан быть
morphogenesis/ (спека §11, §23).

[v5.6-EXP FINAL] Rev.11

"""

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(ROOT, "morphogenesis")


def run(cmd, cwd):
    print("\n$ " + " ".join(cmd), flush=True)
    return subprocess.call(cmd, cwd=cwd)


def main():
    quick = "--quick" in sys.argv
    python = sys.executable

    # Тесты: cwd=morphogenesis, чтобы top-level импорты (config, nca_core, ...) работали
    # без установки пакета и без sys.path.insert в тестах.
    rc = run([python, "-m", "pytest", "-q", "tests"], cwd=PKG)
    if rc != 0:
        print("ПРОВАЛ: pytest", flush=True)
        return rc

    if quick:
        return 0

    rc = run([python, "smoke_test.py"], cwd=PKG)
    if rc != 0:
        print("ПРОВАЛ: smoke_test", flush=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())
