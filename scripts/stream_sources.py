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
    "system": _system,
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
