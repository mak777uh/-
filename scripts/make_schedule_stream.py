"""make_schedule_stream.py — кодирует расписание темпа в значения потока.

E3 (память/гистерезис). Мир считает `p_t = base * (1 + c * (2v_t - 1))`, поэтому нужный темп кодируется
значением `v = 0.5 + (p/base - 1) / (2c)`. Это позволяет задать расписание БЕЗ правки мира.

Проверка марковости: три пути, которые до шага 300 идут с разным темпом, а с 300-го — одинаково.
Если макроскопические наблюдаемые после 300 сходятся — система марковская на этом уровне; если нет —
история влияет, и "когда пришёл сигнал" имеет смысл.
"""
import argparse
import json
from pathlib import Path


def p_to_v(p: float, base: float, c: float) -> float:
    v = 0.5 + (p / base - 1.0) / (2.0 * c)
    return max(0.0, min(1.0, v))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--steps", type=int, default=900)
    ap.add_argument("--switch-at", type=int, default=300)
    ap.add_argument("--p-early", type=float, required=True, help="темп до переключения")
    ap.add_argument("--p-late", type=float, default=0.585, help="темп после переключения")
    ap.add_argument("--base", type=float, default=0.585)
    ap.add_argument("--c", type=float, default=0.6)
    args = ap.parse_args()

    v_early = p_to_v(args.p_early, args.base, args.c)
    v_late = p_to_v(args.p_late, args.base, args.c)
    vals = [v_early] * args.switch_at + [v_late] * (args.steps - args.switch_at)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "values": vals,
        "note": (f"расписание: p={args.p_early} до шага {args.switch_at}, затем p={args.p_late}; "
                 f"v_early={v_early:.4f}, v_late={v_late:.4f}"),
        "source": "synthetic_schedule",
    }, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"[schedule] {out}: p {args.p_early} -> {args.p_late} на шаге {args.switch_at} "
          f"(v {v_early:.3f} -> {v_late:.3f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
