#!/usr/bin/env python
"""map_metrics.py — метрики формы по финальной карте живого (Betti, rugosity, плотность).

Зачем: до 24.10 в артефактах пруда не было карт — только скаляры, поэтому разнообразие
ПАТТЕРНОВ не считалось (§10x.1: IDH не проверен). Теперь новые прогоны несут
`final_alive_map` (строки «0/1» через «/»), и по нему считаются:

* **β0** — число 4-связных компонент живого;
* **β1** — число дырок: число 8-связных областей фона, не связанных с краем;
* **плотность** — доля живых;
* **rugosity** — отношение периметра (число рёбер живой/мёртвая) к периметру круга той же
  площади: 1.0 — компактная форма, больше — изрезанная;
* **крупнейшая компонента** — доля живых в самой большой компоненте (одно тело или пыль).

Запуск (из корня):

    python scripts/map_metrics.py --src morphogenesis/experiments/E09_pond \
        --glob "found_*.json" --out morphogenesis/experiments/E09_pond/founding_maps.json
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import statistics
from pathlib import Path


def parse_map(text: str | None) -> list[list[int]] | None:
    if not text:
        return None
    rows = text.split("/")
    grid = [[1 if ch == "1" else 0 for ch in row] for row in rows]
    if not grid or not grid[0]:
        return None
    return grid


def components(grid: list[list[int]], value: int, connectivity: int = 4) -> list[int]:
    """Размеры связных областей клеток со значением `value`."""
    h, w = len(grid), len(grid[0])
    if connectivity == 4:
        steps = ((1, 0), (-1, 0), (0, 1), (0, -1))
    else:
        steps = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))
    seen = [[False] * w for _ in range(h)]
    sizes: list[int] = []
    for y in range(h):
        for x in range(w):
            if grid[y][x] != value or seen[y][x]:
                continue
            stack = [(y, x)]
            seen[y][x] = True
            size = 0
            while stack:
                cy, cx = stack.pop()
                size += 1
                for dy, dx in steps:
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < h and 0 <= nx < w and not seen[ny][nx] and grid[ny][nx] == value:
                        seen[ny][nx] = True
                        stack.append((ny, nx))
            sizes.append(size)
    return sizes


def betti1(grid: list[list[int]]) -> int:
    """Число дырок: области фона (8-связные), не касающиеся края."""
    h, w = len(grid), len(grid[0])
    background = [[1 - v for v in row] for row in grid]
    seen = [[False] * w for _ in range(h)]
    holes = 0
    steps = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))
    for y in range(h):
        for x in range(w):
            if background[y][x] != 1 or seen[y][x]:
                continue
            stack = [(y, x)]
            seen[y][x] = True
            touches_edge = False
            while stack:
                cy, cx = stack.pop()
                if cy in (0, h - 1) or cx in (0, w - 1):
                    touches_edge = True
                for dy, dx in steps:
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < h and 0 <= nx < w and not seen[ny][nx] and background[ny][nx] == 1:
                        seen[ny][nx] = True
                        stack.append((ny, nx))
            if not touches_edge:
                holes += 1
    return holes


def perimeter(grid: list[list[int]]) -> int:
    """Число рёбер между живой и мёртвой клеткой (внешняя граница включена)."""
    h, w = len(grid), len(grid[0])
    edges = 0
    for y in range(h):
        for x in range(w):
            if grid[y][x] != 1:
                continue
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if not (0 <= ny < h and 0 <= nx < w) or grid[ny][nx] == 0:
                    edges += 1
    return edges


def analyse(path: Path) -> dict | None:
    data = json.loads(path.read_text(encoding="utf-8"))
    summary = data.get("summary") or {}
    grid = parse_map(summary.get("final_alive_map"))
    if grid is None:
        return None
    alive = sum(sum(row) for row in grid)
    comps = components(grid, 1, connectivity=4)
    area = len(grid) * len(grid[0])
    per = perimeter(grid)
    compact = 2.0 * math.sqrt(math.pi * alive) if alive else None
    return {
        "artifact": path.name,
        "alive": alive,
        "density": round(alive / area, 4) if area else None,
        "beta0": len(comps),
        "beta1": betti1(grid),
        "largest_component_share": (round(max(comps) / alive, 4) if comps and alive else None),
        "perimeter": per,
        "rugosity": round(per / compact, 3) if compact else None,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", default="morphogenesis/experiments/E09_pond")
    ap.add_argument("--glob", default="found_*.json")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    files = sorted(glob.glob(str(Path(args.src) / args.glob)))
    rows = [row for row in (analyse(Path(f)) for f in files) if row is not None]
    missing = len(files) - len(rows)
    payload = {
        "kind": "map_metrics",
        "note": ("считается только по артефактам с final_alive_map (новые прогоны); "
                 "β0 — 4-связные компоненты живого, β1 — 8-связные дырки фона"),
        "files": len(files),
        "without_map": missing,
        "rows": rows,
        "summary": {
            "n": len(rows),
            "beta0_median": round(statistics.median([r["beta0"] for r in rows]), 2) if rows else None,
            "beta1_median": round(statistics.median([r["beta1"] for r in rows]), 2) if rows else None,
            "rugosity_median": (round(statistics.median([r["rugosity"] for r in rows
                                                         if r["rugosity"] is not None]), 3)
                                if rows else None),
            "density_median": (round(statistics.median([r["density"] for r in rows
                                                        if r["density"] is not None]), 4)
                               if rows else None),
        },
    }
    if args.out:
        Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8")
        print(f"записано: {args.out} | карт {len(rows)} (без карты {missing})")
    print(f"{'артефакт':>34} {'alive':>6} {'dens':>6} {'b0':>4} {'b1':>4} {'rug':>6}")
    for row in rows[:20]:
        print(f"{row['artifact'][:34]:>34} {row['alive']:>6} {str(row['density']):>6} "
              f"{row['beta0']:>4} {row['beta1']:>4} {str(row['rugosity']):>6}")
    print("сводка:", json.dumps(payload["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
