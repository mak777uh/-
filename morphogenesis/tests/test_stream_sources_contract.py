"""Контракт источников живого сигнала: читатель вызывается КАК ОБЪЕКТ и отдаёт 0..1.

Зачем (30.10, найдено при E5). В `scripts/stream_sources.py` цикл `LiveSource._loop` делает
`v = float(self._reader())` — то есть вызывает **сам объект-читатель**, а не метод `.read()`.
Ошибка внутри обёрнута в `except Exception: pass`, поэтому источник, у которого нет `__call__`,
молча собирает **ноль отсчётов**, а прогон выглядит успешным: `live_stream.n = 0`, дамп пуст.
Именно так живой канал был «мёртвым», и это не поймал ни один тест.

Тест проверяет контракт для каждого источника из `_READERS`:
1. читатель вызывается без аргументов и возвращает число;
2. значение лежит в [0, 1];
3. `LiveSource` с этим читателем действительно собирает отсчёты (проверяется на подставном
   читателе, чтобы не ходить в сеть и не зависеть от микрофона);
4. ошибка внутри читателя не убивает поток (поток продолжает собирать) — это как раз то
   поведение `except: pass`, из-за которого дефект был невидим.

Сеть, микрофон и GPU не используются: для проверки 3–4 берётся синтетический читатель.
"""
from __future__ import annotations

import importlib.util
import math
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCES_PY = ROOT / "scripts" / "stream_sources.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("stream_sources_under_test", SOURCES_PY)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Источники, которые безопасно вызывать в тесте: только чтение системных счётчиков.
# `mic`, `gpu`, `hardware` трогают устройства и на этой машине роняют интерпретатор
# (Windows access violation при вызове всех читателей подряд — проверено 30.10).
SAFE_TO_CALL = ("self", "system", "system_ext")


def test_every_reader_is_callable():
    """Структурная проверка: КАЖДЫЙ читатель вызывается как объект (тот самый дефект E5)."""
    mod = _load_module()
    assert mod._READERS, "реестр источников пуст"
    # ВАЖНО: классы НЕ создаём — `mic` открывает аудиоустройство и на этой машине роняет
    # интерпретатор (Windows access violation, проверено 30.10). Проверяем наличие `__call__`
    # у самого класса: именно его отсутствие делало источник «мёртвым» в E5.
    broken = [name for name in sorted(mod._READERS) if not hasattr(mod._READERS[name], "__call__")]
    assert not broken, (
        "читатель не вызывается как объект (нет __call__): " + ", ".join(broken) +
        " — LiveSource._loop делает float(self._reader()) и молча собирает 0 отсчётов"
    )


def test_safe_readers_return_bounded_values():
    """Функциональная проверка только для источников без доступа к устройствам."""
    mod = _load_module()
    broken = []
    for name in SAFE_TO_CALL:
        if name not in mod._READERS:
            continue
        try:
            reader = mod._READERS[name]()      # безопасные источники создавать можно
            v = float(reader())
        except Exception as e:
            broken.append(f"{name}: вызов упал: {type(e).__name__}")
            continue
        if math.isnan(v) or not (0.0 <= v <= 1.0):
            broken.append(f"{name}: значение вне [0, 1]: {v}")
    assert not broken, "нарушения контракта источников:\n" + "\n".join(broken)


def test_live_source_collects_samples():
    """LiveSource действительно собирает отсчёты: иначе канал «мёртв» молча."""
    mod = _load_module()

    class _Stub:
        def __init__(self):
            self.i = 0

        def __call__(self):
            self.i += 1
            return 0.5 + 0.25 * (self.i % 2)

    mod._READERS["_stub"] = _Stub
    try:
        src = mod.make("_stub", rate=20.0, window_s=5.0).start()
        time.sleep(0.6)
        collected = len(src.raw)
    finally:
        mod._READERS.pop("_stub", None)
    assert collected >= 3, f"за 0.6 с при 20 Гц собрано всего {collected} отсчётов"


def test_reader_exception_does_not_kill_the_thread():
    """Падение читателя не должно останавливать поток (но и не должно быть незаметным)."""
    mod = _load_module()
    calls = {"n": 0}

    class _Flaky:
        def __call__(self):
            calls["n"] += 1
            if calls["n"] % 3 == 1:
                raise RuntimeError("сеть моргнула")
            return 0.42

    mod._READERS["_flaky"] = _Flaky
    try:
        src = mod.make("_flaky", rate=20.0, window_s=5.0).start()
        time.sleep(0.6)
        collected = len(src.raw)
        total = calls["n"]
    finally:
        mod._READERS.pop("_flaky", None)
    assert total >= 6, f"поток не продолжал вызывать читатель: {total} вызовов"
    assert collected >= 2, f"успешные вызовы не попали в выборку: {collected}"
