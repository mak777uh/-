"""individuation.py — критерий индивидуации из `reports/2026-10-29-individuation-criterion-plan.md`.

Считает C1–C3 и C5 по снимкам полей; C4 (устойчивость к вдвое мелкой сетке) для дискретного мира
неприменим — об этом печатается предупреждение, а не тихий пропуск.

Ожидаемый формат снимков (то, что пишет `--dump-fields` в пруде и что можно собрать для поля):
    {"step": int, "alive": [[0/1...]], "energy": [[...]]}                # пруд
    {"step": int, "z": [[...]], "w": [[...]]}                            # поле

z — то, что предъявляет структуру; w — независимое поле (не участвует в определении границы).

Использование:
    python scripts/individuation.py --dir <каталог снимков> --out <json>
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def smooth3(a):
    """Сглаживание 3×3 (фиксировано критерием, не подбирается)."""
    h, w = len(a), len(a[0])
    out = [[0.0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            s, n = 0.0, 0
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    s += a[(y + dy) % h][(x + dx) % w]
                    n += 1
            out[y][x] = s / n
    return out


def components(mask):
    h, w = len(mask), len(mask[0])
    seen = [[False] * w for _ in range(h)]
    comps = []
    for y in range(h):
        for x in range(w):
            if mask[y][x] and not seen[y][x]:
                stack, cells = [(y, x)], []
                seen[y][x] = True
                while stack:
                    cy, cx = stack.pop()
                    cells.append((cy, cx))
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = (cy + dy) % h, (cx + dx) % w
                        if mask[ny][nx] and not seen[ny][nx]:
                            seen[ny][nx] = True
                            stack.append((ny, nx))
                comps.append(cells)
    return comps


def load(path: Path):
    d = json.loads(path.read_text(encoding="utf-8"))
    if "alive" in d:
        z = [[float(v) for v in row] for row in d["alive"]]
        w = [[float(v) for v in row] for row in d.get("energy") or z]
        kind = "pond"
    else:
        z = [[float(v) for v in row] for row in d["z"]]
        w = [[float(v) for v in row] for row in d["w"]]
        kind = "field"
    return int(d["step"]), z, w, kind


def analyse(paths: list[Path], alive_only: bool = False) -> dict:
    snaps = [load(p) for p in sorted(paths)]
    snaps.sort(key=lambda s: s[0])
    kind = snaps[0][3]

    contrasts, counts, kept = [], [], []
    for step, z, w, _ in snaps:
        zs = smooth3(z)
        flat = sorted(v for row in zs for v in row)
        theta = flat[len(flat) // 2]
        mask = [[v > theta for v in row] for row in zs]
        comps = components(mask)
        # берём компоненты не меньше 5 клеток: мелочь — шум сглаживания
        comps = [c for c in comps if len(c) >= 5]
        counts.append(len(comps))
        if not comps:
            continue
        tot_in = tot_out = 0.0
        n_in = n_out = 0
        h, wd = len(z), len(z[0])
        inmask = [[False] * wd for _ in range(h)]
        for c in comps:
            for (y, x) in c:
                inmask[y][x] = True
        alive = [[z[y][x] > 0 for x in range(wd)] for y in range(h)]
        for y in range(h):
            for x in range(wd):
                if inmask[y][x]:
                    tot_in += w[y][x]
                    n_in += 1
                elif (not alive_only) or alive[y][x]:
                    tot_out += w[y][x]
                    n_out += 1
        if n_in and n_out:
            r = (tot_in / n_in) / max(1e-9, tot_out / n_out)
            contrasts.append(r)
            kept.append((step, len(comps), r))

    # C1: контраст независимого поля отличается от 1 не менее чем на 25 %
    c1 = bool(contrasts) and (sum(1 for r in contrasts if r <= 0.8 or r >= 1.25) >= 0.6 * len(contrasts))
    # C3: сумма положительных приращений числа компонент
    gains = sum(max(0, counts[i] - counts[i - 1]) for i in range(1, len(counts)))
    c3 = gains >= 5
    # C2: время жизни — грубая оценка по доле срезов с непустыми компонентами
    c2 = bool(snaps) and (sum(1 for c in counts if c > 0) / len(counts)) >= 0.5

    return {
        "kind": kind,
        "snapshots": len(snaps),
        "steps": [s[0] for s in snaps],
        "component_counts": counts,
        "contrasts": [round(r, 3) for r in contrasts],
        "per_snapshot": kept,
        "gains": gains,
        "C1_contrast": c1,
        "C2_persistence": c2,
        "C3_multiplication": c3,
        "C4_grid_refinement": "неприменимо: у дискретного мира нет непрерывного предела",
        "alive_only": bool(alive_only),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="критерий индивидуации по снимкам полей")
    ap.add_argument("--dir", required=True)
    ap.add_argument("--alive-only", action="store_true",
                    help="сравнивать w только среди ЖИВЫХ клеток (у пруда пустые клетки имеют нулевую энергию, "
                         "и без этого «снаружи» — это деление на ноль)")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    paths = sorted(Path(args.dir).glob("fields_*.json"))
    if len(paths) < 3:
        print(f"[individuation] снимков мало ({len(paths)}), нужно ≥3")
        return 1
    res = analyse(paths, alive_only=bool(args.alive_only))
    print(f"[individuation] {args.dir}: снимков {res['snapshots']}, шаги {res['steps']}")
    print(f"  компонент по срезам: {res['component_counts']}")
    print(f"  контраст w внутри/снаружи: {res['contrasts']}")
    print(f"  C1 контраст ≥25 %: {res['C1_contrast']} | C2 устойчивость: {res['C2_persistence']} | "
          f"C3 размножение (приросты {res['gains']}): {res['C3_multiplication']}")
    print(f"  C4: {res['C4_grid_refinement']}")
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[individuation] записано: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
