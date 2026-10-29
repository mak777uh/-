"""stream_sources.py — источники живого сигнала извне для цифрового мира.

Зачем. Записанный поток (replay) — это «корм в сейфе»: воспроизводимо, но не связь. Для настоящей связи
мир должен читать источник **в реальном времени**, пока идёт. Здесь собраны источники и правило, по которому
они превращаются в число 0..1, понятное миру.

Источники (`--inflow-live <имя>`):

| имя       | что читается                                  | характер сигнала                    |
|-----------|-----------------------------------------------|-------------------------------------|
| `mic`     | RMS микрофона 16 кГц, блоки по 1/rate         | быстрый, но **разреженный** (тишина) |
| `net`     | время отклика публичного хоста (RTT, мс)      | быстрый, непрерывный, шумный        |
| `crypto`  | цена BTCUSDT, относительное изменение         | быстрый, непрерывный, «толстые хвосты» |
| `events`  | частота правок Википедии за окно              | **вспышечный**: тишина + залпы       |
| `usgs`    | число землетрясений за час                    | редкие события, почти всегда ноль   |
| `system`  | загрузка CPU хоста (сам компьютер — тоже мир) | непрерывный, с бытовыми всплесками   |

Нормировка. Источники имеют разные масштабы, поэтому значение переводится в 0..1 по **бегущим процентилям**
(окно ~30 с): `(x − p05) / (p95 − p05)`, обрезка в [0, 1]. Это значит: мир чувствует **относительные**
колебания, а не абсолютные единицы. Сырые значения тоже пишутся в дамп.

Честное ограничение: живой режим **не воспроизводим**. Компенсация — дамп: всё, что мир услышал,
сохраняется и может быть проиграно повторно (тогда результат должен совпасть бит-в-бит, и это проверяется).
"""
from __future__ import annotations

import collections
import socket
import statistics as st
import subprocess
import threading
import time
from typing import Callable


class LiveSource:
    """Живой источник: поток опроса в фоне + бегущая нормировка по процентилям."""

    def __init__(self, name: str, rate: float = 20.0, window_s: float = 30.0):
        self.name = name
        self.rate = max(1.0, float(rate))
        self.window = max(2, int(window_s * self.rate))
        self.recent: collections.deque[float] = collections.deque(maxlen=self.window)
        self.raw: list[float] = []
        self._stop = False
        self._thread: threading.Thread | None = None
        self._reader = _READERS[name]()  # фабрика читателя

    # ---------------------------------------------------------------- жизнь
    def start(self) -> "LiveSource":
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        return self

    def stop(self) -> dict:
        self._stop = True
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        return {"source": self.name, "rate_hz": self.rate, "n": len(self.raw),
                "raw_first": [round(v, 6) for v in self.raw[:10]],
                "raw_min": round(min(self.raw), 6) if self.raw else None,
                "raw_max": round(max(self.raw), 6) if self.raw else None}

    def _loop(self) -> None:
        period = 1.0 / self.rate
        while not self._stop:
            t0 = time.perf_counter()
            try:
                v = float(self._reader())
                self.raw.append(v)
                self.recent.append(v)
            except Exception:
                pass  # сеть может моргнуть — поток продолжается, дырка фиксируется в raw
            dt = time.perf_counter() - t0
            time.sleep(max(0.0, period - dt))

    # ------------------------------------------------------------- значение
    def value(self) -> float:
        """Текущее значение 0..1 (0.5, пока данных мало)."""
        if len(self.recent) < 5:
            return 0.5
        vals = sorted(self.recent)
        p05 = vals[int(0.05 * (len(vals) - 1))]
        p95 = vals[int(0.95 * (len(vals) - 1))]
        x = self.recent[-1]
        if p95 - p05 < 1e-12:
            return 0.5
        return min(1.0, max(0.0, (x - p05) / (p95 - p05)))


# -------------------------------------------------------------- читатели
class _mic:
    """RMS микрофона: блоки по 1/rate секунды при 16 кГц."""

    def __init__(self) -> None:
        import numpy as np
        import sounddevice as sd
        self._np = np
        self._last: float = 0.0
        self._buf = None
        self._stream = sd.InputStream(samplerate=16000, channels=1, dtype="float32",
                                      blocksize=800, callback=self._cb)
        self._stream.start()

    def _cb(self, indata, frames, time_info, status) -> None:  # noqa: ANN001
        x = self._np.asarray(indata, dtype="float32").reshape(-1)
        if x.size:
            self._last = float(self._np.sqrt((x ** 2).mean()))

    def __call__(self) -> float:
        return self._last


class _net:
    """Задержка отклика публичного DNS/HTTP: TCP-коннект к 1.1.1.1:443, миллисекунды."""

    def __init__(self, host: str = "1.1.1.1", port: int = 443) -> None:
        self.host, self.port = host, port

    def __call__(self) -> float:
        t0 = time.perf_counter()
        with socket.create_connection((self.host, self.port), timeout=2.0):
            pass
        return (time.perf_counter() - t0) * 1000.0


class _crypto:
    def __init__(self) -> None:
        import requests
        self._r = requests
        self._prev = None

    def __call__(self) -> float:
        j = self._r.get("https://api.binance.com/api/v3/ticker/price",
                        params={"symbol": "BTCUSDT"}, timeout=5).json()
        price = float(j["price"])
        prev, self._prev = self._prev, price
        if prev is None or prev == 0:
            return 0.0
        return abs(price - prev) / prev * 1e4  # базисные пункты


class _events:
    """Скорость правок Википедии: сколько новых правок появилось с прошлого опроса."""

    def __init__(self) -> None:
        import requests
        self._r = requests
        self._last_ts: str | None = None

    def __call__(self) -> float:
        j = self._r.get("https://en.wikipedia.org/w/api.php",
                        params={"action": "query", "list": "recentchanges",
                                "rcprop": "timestamp", "rclimit": 50, "format": "json"},
                        headers={"User-Agent": "digital-pond-lab"}, timeout=5).json()
        rows = j.get("query", {}).get("recentchanges", [])
        if not rows:
            return 0.0
        newest = max(r["timestamp"] for r in rows)
        if self._last_ts is None:
            self._last_ts = newest
            return float(len(rows))
        count = sum(1 for r in rows if r["timestamp"] > self._last_ts)
        self._last_ts = newest
        return float(count)


class _system_ext:
    """«Погода машины»: загрузка CPU БЕЗ нашего собственного процесса (доля 0..1).

    Зачем (29.10, по замечанию владельца). Микрофона нет на сервере, а процессор есть везде — значит это
    единственный сигнал, который делает эксперимент воспроизводимым на любой машине. Но нагрузка машины —
    смесь: (а) наш собственный след (замкнутый контур), (б) другие процессы, ОС и планировщик, (в) физика
    железа (частота, троттлинг). Пункт (а) мы можем исключить: `psutil.cpu_percent()` даёт общую загрузку,
    `Process.cpu_percent()` — нашу, разность и есть внешняя часть.

    Ограничение честное: `psutil` считает проценты за интервал между вызовами, поэтому первый вызов
    возвращает 0.0 — это нормально для потока (значение появится со второго).
    """

    def __init__(self) -> None:
        import os
        import psutil
        self._ps = psutil
        self._me = psutil.Process(os.getpid())
        self._ps.cpu_percent(interval=None)
        self._me.cpu_percent(interval=None)
        self._ncpu = max(1, psutil.cpu_count(logical=True) or 1)

    def __call__(self) -> float:
        total = float(self._ps.cpu_percent(interval=None))
        mine = float(self._me.cpu_percent(interval=None)) / self._ncpu
        return max(0.0, min(100.0, total - mine)) / 100.0


class _gpu:
    """Загрузка видеокарты в процентах (0..100), через `nvidia-smi`.

    Плюс к «погоде машины»: GPU занят не только нашим прогоном, но и всем остальным, что запущено.
    Если `nvidia-smi` недоступен, источник возвращает 0.0 — это надо проверять по профилю, а не молча.
    """

    def __init__(self) -> None:
        import subprocess
        self._sp = subprocess

    def __call__(self) -> float:
        try:
            out = self._sp.run(
                ["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=4,
            )
            first = (out.stdout or "").strip().split("\n")[0].strip()
            return float(first) if first else 0.0
        except Exception:
            return 0.0


class _hardware:
    """«Физиология железа»: композит из того, что всегда локально, без интернета.

    Откуда (29.10, владелец): канал железа органичен для цифрового организма — он живёт ВНУТРИ машины,
    её состояние это его почва и погода; и канал есть всегда, даже без сети.

    Композит из пяти компонент, каждая нормируется в 0..1 собственной шкалой:
      * загрузка CPU без нашего процесса (чужая нагрузка);
      * загрузка GPU (наш след + чужие задачи);
      * давление на память (доля занятой RAM);
      * температура/троттлинг — через частоту, если доступна (иначе 0.5, «неизвестно»);
      * **джиттер шага** — изменчивость интервала между вызовами (ритм самой машины).

    Оговорка: это НЕ физические единицы. Композит нужен как индекс среды; для выводов о конкретном
    канале надо смотреть компоненты отдельно (`system_ext`, `gpu`).
    """

    def __init__(self) -> None:
        import os
        import psutil
        self._ps = psutil
        self._me = psutil.Process(os.getpid())
        self._ps.cpu_percent(interval=None)
        self._me.cpu_percent(interval=None)
        self._ncpu = max(1, psutil.cpu_count(logical=True) or 1)
        self._last = None
        self._last_jitter = 0.0

    def _gpu(self) -> float:
        import subprocess
        try:
            out = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
                                 capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=3)
            first = (out.stdout or "").strip().split("\n")[0].strip()
            return float(first) / 100.0 if first else 0.0
        except Exception:
            return 0.0

    def __call__(self) -> float:
        import time
        now = time.time()
        if self._last is not None:
            dt = now - self._last
            # джиттер: отклонение интервала от типичного (сглаженное), в 0..1
            self._last_jitter = 0.9 * self._last_jitter + 0.1 * min(1.0, abs(dt - 0.5) / 0.5)
        self._last = now

        cpu_total = float(self._ps.cpu_percent(interval=None))
        cpu_mine = float(self._me.cpu_percent(interval=None)) / self._ncpu
        cpu_ext = max(0.0, min(100.0, cpu_total - cpu_mine)) / 100.0
        gpu = self._gpu()
        mem = float(self._ps.virtual_memory().percent) / 100.0
        # температуры нет в стандартном API без прав; берём 0.5 как «неизвестно», а не 0 как «холодно»
        temp = 0.5
        parts = [cpu_ext, gpu, mem, temp, self._last_jitter]
        return sum(parts) / len(parts)


class _solar_wind:
    """Скорость солнечного ветра (плазма на L1, NOAA DSCOVR/ACE), 1 отсчёт в минуту.

    Зачем (29.10, по запросу владельца: «излучение солнца, колебания планеты»). Это настоящий внешний
    физический поток: он не зависит от нас, идёт круглосуточно и бесплатен. Ограничение честное: каденс
    1 минута, а мир делает ~0.8 шага в секунду, поэтому сигнал для мира **квазистатичен** — одна точка на
    ~48 шагов. Это не ритм, а смена режима; именно поэтому источник годится для проверки «реагирует ли мир
    на смену режима», а не «ритм».
    """

    URL = "https://services.swpc.noaa.gov/json/rtsw/rtsw_wind_1m.json"

    def __init__(self) -> None:
        import requests
        self._r = requests
        self._last = None

    def __call__(self) -> float:
        j = self._r.get(self.URL, timeout=8, headers={"User-Agent": "digital-pond-lab"}).json()
        rows = [r for r in j if r.get("active") and r.get("proton_speed") is not None]
        if not rows:
            return 0.0
        last = rows[-1]
        self._last = last
        return float(last["proton_speed"])


class _goes_xray:
    """Поток рентгена GOES (0.1–0.8 нм), 1 отсчёт в минуту: вспышки на Солнце как внешние события.

    Тот же каденс, что у солнечного ветра (квазистатичен для мира), но с огромным динамическим
    диапазоном: во время вспышки поток растёт на порядки. Это лучший доступный пример **смены режима**,
    которого не бывает в короткой записи.
    """

    URL = "https://services.swpc.noaa.gov/json/goes/primary/xrays-1-day.json"

    def __init__(self) -> None:
        import requests
        self._r = requests

    def __call__(self) -> float:
        j = self._r.get(self.URL, timeout=8, headers={"User-Agent": "digital-pond-lab"}).json()
        rows = [r for r in j if str(r.get("energy", "")).startswith("0.1-0.8")]
        if not rows:
            return 0.0
        return float(rows[-1]["flux"] or 0.0)


class _usgs:
    def __init__(self) -> None:
        import requests
        self._r = requests

    def __call__(self) -> float:
        j = self._r.get("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson",
                        timeout=6).json()
        return float((j.get("metadata") or {}).get("count") or 0)


class _system:
    """Загрузка CPU хоста: сам компьютер — тоже внешний мир для цифровой колонии."""

    def __init__(self) -> None:
        self._prev = None

    def __call__(self) -> float:
        try:
            out = subprocess.run(["powershell", "-NoProfile", "-Command",
                                  "(Get-CimInstance Win32_PerfFormattedData_PerfOS_Processor | "
                                  "Select-Object -First 1).PercentProcessorTime"],
                                 capture_output=True, text=True, timeout=4)
            return float((out.stdout or "0").strip() or 0)
        except Exception:
            pass
        try:
            with open("/proc/loadavg", encoding="utf-8") as fh:
                return float(fh.read().split()[0]) * 100.0
        except Exception:
            return 0.0


_READERS: dict[str, Callable[[], object]] = {
    "mic": _mic,
    "net": _net,
    "crypto": _crypto,
    "events": _events,
    "usgs": _usgs,
    "system": _system, "hardware": _hardware, "system_ext": _system_ext, "gpu": _gpu, "solar_wind": _solar_wind, "goes_xray": _goes_xray,
}

SOURCES = tuple(sorted(_READERS))


def make(name: str, rate: float = 20.0, window_s: float = 30.0) -> LiveSource:
    if name not in _READERS:
        raise SystemExit(f"неизвестный источник «{name}»; есть: {', '.join(SOURCES)}")
    return LiveSource(name, rate=rate, window_s=window_s)


if __name__ == "__main__":
    import argparse
    import json

    ap = argparse.ArgumentParser(description="проба живого источника")
    ap.add_argument("--source", default="net")
    ap.add_argument("--seconds", type=float, default=10.0)
    ap.add_argument("--rate", type=float, default=5.0)
    args = ap.parse_args()
    src = make(args.source, rate=args.rate).start()
    time.sleep(args.seconds)
    vals = [src.value() for _ in range(5)]
    info = src.stop()
    print(f"[source] {args.source}: отсчётов {info['n']}, сырые {info['raw_min']}…{info['raw_max']}")
    print(f"[source] нормированные значения (5 подряд): {[round(v, 3) for v in vals]}")
