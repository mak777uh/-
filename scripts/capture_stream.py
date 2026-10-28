"""capture_stream.py — запись настоящего потока из мира в артефакт.

Зачем. Гипотеза владельца: колония должна получать **реальный** поток данных извне (микрофон, сеть), а не
постоянную подпитку числом. Чтобы опыт был воспроизводим, поток записывается **один раз** в JSON
и дальше проигрывается из файла: тогда тот же файл и тот же сид дают тот же мир (иначе «эксперимент»
нельзя повторить, и это не эксперимент).

Источники:
  * `mic` — микрофон: RMS-огибающая 20 значений в секунду (по умолчанию 60 с);
  * `weather` — open-meteo (Москва по умолчанию), отсчёты раз в `--interval` секунд;
  * `crypto` — Binance `ticker/price` (BTCUSDT), отсчёты раз в `--interval` секунд.

Выход: `lab/streams/<источник>-<дата>.json` с полями `source`, `captured_at`, `rate_hz`, `values`
(нормированы в 0..1), `raw` (первые значения для глаза), `notes`.

Использование:
    python scripts/capture_stream.py --source mic --seconds 60 --out lab/streams/mic-2026-10-28.json
    python scripts/capture_stream.py --source weather --seconds 300 --interval 15 --out lab/streams/weather-2026-10-28.json
"""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def norm(values: list[float]) -> list[float]:
    lo, hi = min(values), max(values)
    if hi - lo < 1e-12:
        return [0.5 for _ in values]
    return [(v - lo) / (hi - lo) for v in values]


def capture_mic(seconds: float, rate_hz: float) -> tuple[list[float], str]:
    import numpy as np
    import sounddevice as sd
    fs = 16000
    frames = int(fs * seconds)
    rec = sd.rec(frames, samplerate=fs, channels=1, dtype="float32")
    sd.wait()
    x = rec.reshape(-1)
    win = max(1, int(fs / rate_hz))
    values = []
    for i in range(0, len(x) - win + 1, win):
        chunk = x[i:i + win]
        values.append(float(np.sqrt((chunk ** 2).mean())))
    note = f"микрофон, окно {win} отсчётов при {fs} Гц"
    return values, note


def capture_http(seconds: float, interval: float, kind: str) -> tuple[list[float], str]:
    import requests
    values, t0 = [], time.time()
    while time.time() - t0 < seconds:
        try:
            if kind == "weather":
                r = requests.get("https://api.open-meteo.com/v1/forecast",
                                 params={"latitude": 55.75, "longitude": 37.62,
                                         "current": "temperature_2m,wind_speed_10m,cloud_cover"},
                                 timeout=10).json().get("current") or {}
                v = float(r.get("temperature_2m") or 0.0) + 0.1 * float(r.get("wind_speed_10m") or 0.0)
                note = "open-meteo: температура + 0.1·ветер (Москва)"
            else:
                r = requests.get("https://api.binance.com/api/v3/ticker/price",
                                 params={"symbol": "BTCUSDT"}, timeout=10).json()
                v = float(r.get("price") or 0.0)
                note = "Binance BTCUSDT, цена"
            values.append(v)
        except Exception as exc:  # сеть может моргнуть — это часть честного потока
            values.append(values[-1] if values else 0.0)
            note = f"{kind} (сбой сети: {type(exc).__name__})"
        time.sleep(max(0.0, interval))
    return values, note


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--source", default="mic", choices=["mic", "weather", "crypto"])
    ap.add_argument("--seconds", type=float, default=60.0)
    ap.add_argument("--rate-hz", type=float, default=20.0, help="частота отсчётов для микрофона")
    ap.add_argument("--interval", type=float, default=15.0, help="интервал опроса для сети, секунды")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    if args.source == "mic":
        values, note = capture_mic(args.seconds, args.rate_hz)
        rate = args.rate_hz
    else:
        values, note = capture_http(args.seconds, args.interval, args.source)
        rate = 1.0 / args.interval

    payload = {
        "source": args.source,
        "captured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "seconds": args.seconds,
        "rate_hz": rate,
        "n": len(values),
        "notes": note,
        "values": [round(v, 6) for v in norm(values)],
        "raw_first": [round(v, 6) for v in values[:10]],
        "raw_min": round(min(values), 6),
        "raw_max": round(max(values), 6),
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"[capture] {args.source}: {len(values)} отсчётов, {note} → {out}")
    print(f"[capture] диапазон сырых значений: {payload['raw_min']} … {payload['raw_max']}, "
          f"частота {rate:.2f} Гц")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
