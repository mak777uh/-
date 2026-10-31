"""Тест закрепляет опубликованное утверждение о самомодели (X50, §10ds).

Зачем тест на агрегат, а не на код. Статья 028 v1.5.1 опубликована (DOI 10.5281/zenodo.23839898) с утверждением:
предиктивная зависимость для «своего» ресурса **исчезает**, когда действие организма на среду заблокировано.
Если агрегат когда-нибудь пересоберут и числа изменятся, это должно упасть здесь, а не обнаружиться читателем.

Проверяется:
  * агрегат существует и разбирается;
  * в обычном плече зависимость положительна и есть хотя бы у 8 из 10 сидов;
  * в «призраке» медиана равна нулю и положительных сидов нет;
  * вердикт записан и говорит именно об исчезновении.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AGG = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "ghost_matrix.json"


def _load() -> dict:
    assert AGG.is_file(), f"нет агрегата {AGG}"
    return json.loads(AGG.read_text(encoding="utf-8"))


def test_aggregate_shape() -> None:
    data = _load()
    assert data["kind"] == "ghost_control"
    assert "normal" in data["by_arm"] and "ghost" in data["by_arm"]
    assert data["by_arm"]["normal"]["under"]["n"] >= 8


def test_normal_arm_shows_dependence() -> None:
    under = _load()["by_arm"]["normal"]["under"]
    assert under["median"] > 0.01, under
    assert under["positive"] >= 8, under


def test_ghost_arm_shows_no_dependence() -> None:
    under = _load()["by_arm"]["ghost"]["under"]
    assert under["median"] == 0.0, under
    assert under["positive"] == 0, under


def test_empty_cells_never_predictive() -> None:
    arms = _load()["by_arm"]
    for arm in ("normal", "ghost"):
        empty = arms[arm].get("empty")
        if empty:
            assert empty["median"] == 0.0, (arm, empty)


def test_verdict_states_disappearance() -> None:
    verdict = _load().get("verdict") or ""
    assert "исчезла" in verdict, verdict
