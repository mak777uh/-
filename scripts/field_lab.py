"""field_lab.py — непрерывное поле вместо клеток: пятна, которые делятся сами (Грей–Скотт).

Зачем (29.10, ответ пяти моделей на наши 8 вопросов). Наш прежний мир задаёт индивидуума **заранее**:
клетка, масса 24, `if mass == 24: split()`. Это телеология в коде, а не физика. Чтобы индивидуумы
**возникали**, нужно поле, где нет ни тел, ни меток, ни правил размножения — только поток и уравнения.

Система: Грей–Скотт (два поля, автокатализ + подпитка + распад). В ней при определённых (F, k) пятна
**делятся сами** — никакого правила деления в коде нет. Это минимальный честный стенд для вопроса
«возникает ли индивидуум и размножается ли он без того, чтобы мы это прописали».

    du/dt = Du·∇²u − u·v² + F·(1 − u)
    dv/dt = Dv·∇²v + u·v² − (F + k)·v

Что считается — **описательно**, без критериев (порядок: сначала наблюдение, критерий замораживается после):
    * число связных компонент при пороге по v;
    * размеры (максимум, медиана), доля занятой площади;
    * отличие v и u внутри компонент и снаружи (есть ли «внутреннее» против «внешнего»);
    * средний |∇v| — резкость границ;
    * счётчик расщеплений: рост числа компонент между срезами.

Чего НЕТ: клеток, меток, линий, наследования, правил деления. Только уравнения.

Использование:
    python scripts/field_lab.py --steps 8000 --grid 128 --out lab/field/pilot.json
    python scripts/field_lab.py --steps 8000 --grid 128 --F 0.0367 --k 0.0649   # другой режим
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def laplacian(x):
    import torch
    return (torch.roll(x, 1, 0) + torch.roll(x, -1, 0) +
            torch.roll(x, 1, 1) + torch.roll(x, -1, 1) - 4.0 * x)


def components(mask):
    """Число и размеры 4-связных компонент (периодические границы)."""
    import numpy as np
    h, w = mask.shape
    labels = np.zeros((h, w), dtype=np.int32)
    cur, sizes = 0, []
    for y in range(h):
        for x in range(w):
            if mask[y, x] and labels[y, x] == 0:
                cur += 1
                stack = [(y, x)]
                labels[y, x] = cur
                n = 0
                while stack:
                    cy, cx = stack.pop()
                    n += 1
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = (cy + dy) % h, (cx + dx) % w
                        if mask[ny, nx] and labels[ny, nx] == 0:
                            labels[ny, nx] = cur
                            stack.append((ny, nx))
                sizes.append(n)
    return cur, sorted(sizes, reverse=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Грей–Скотт: возникновение и деление пятен без правил деления")
    ap.add_argument("--steps", type=int, default=8000)
    ap.add_argument("--grid", type=int, default=128)
    ap.add_argument("--dt", type=float, default=1.0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--Du", type=float, default=0.16)
    ap.add_argument("--Dv", type=float, default=0.08)
    ap.add_argument("--F", type=float, default=0.035)   # подпитка
    ap.add_argument("--k", type=float, default=0.06)    # распад
    ap.add_argument("--threshold", type=float, default=0.2)
    ap.add_argument("--sample-every", type=int, default=200)
    ap.add_argument("--no-catalysis", action="store_true",
                    help="нулевая модель: убрать член u*v^2 (нет автокатализа, структуры не должны возникать)")
    ap.add_argument("--seed-cells", type=int, default=0,
                    help="0 = один зародыш в центре; N>0 = N случайных зародышей (для проверки, что деление не наше)")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    import torch
    dev = torch.device(args.device if (args.device == "cpu" or torch.cuda.is_available()) else "cpu")
    g = args.grid
    gen = torch.Generator(device=dev).manual_seed(int(args.seed))

    u = torch.ones((g, g), device=dev)
    v = torch.zeros((g, g), device=dev)
    yy = torch.arange(g, device=dev).view(-1, 1).expand(g, g)
    xx = torch.arange(g, device=dev).view(1, -1).expand(g, g)
    if int(args.seed_cells) > 0:
        for _ in range(int(args.seed_cells)):
            cy = int(torch.randint(0, g, (1,), generator=gen).item())
            cx = int(torch.randint(0, g, (1,), generator=gen).item())
            m = ((xx - cx) ** 2 + (yy - cy) ** 2) <= 4
            v = torch.where(m, torch.full_like(v, 0.5), v)
            u = torch.where(m, torch.full_like(u, 0.25), u)
    else:
        c, r0 = g // 2, max(2, g // 32)
        m = ((xx - c) ** 2 + (yy - c) ** 2) <= r0 * r0
        v = torch.where(m, torch.full_like(v, 0.5), v)
        u = torch.where(m, torch.full_like(u, 0.25), u)

    Du, Dv, F, k = float(args.Du), float(args.Dv), float(args.F), float(args.k)
    series, prev_n = [], None
    splits = 0
    for step in range(1, int(args.steps) + 1):
        uvv = u * v * v if not bool(args.no_catalysis) else torch.zeros_like(u)
        du = Du * laplacian(u) - uvv + F * (1.0 - u)
        dv = Dv * laplacian(v) + uvv - (F + k) * v
        u = torch.clamp(u + args.dt * du, min=0.0, max=1.0)
        v = torch.clamp(v + args.dt * dv, min=0.0, max=1.0)

        if step % int(args.sample_every) == 0 or step == 1:
            import numpy as np
            p = v.detach().cpu().numpy()
            f = u.detach().cpu().numpy()
            mask = p > float(args.threshold)
            n, sizes = components(mask)
            if prev_n is not None and n > prev_n:
                splits += n - prev_n
            prev_n = n
            series.append({
                "step": step, "components": n,
                "max_size": int(sizes[0]) if sizes else 0,
                "median_size": int(sorted(sizes)[len(sizes) // 2]) if sizes else 0,
                "occupied_share": round(float(mask.mean()), 4),
                "v_inside": round(float(p[mask].mean()), 4) if mask.any() else 0.0,
                "v_outside": round(float(p[~mask].mean()), 4) if (~mask).any() else 0.0,
                "u_inside": round(float(f[mask].mean()), 4) if mask.any() else 0.0,
                "u_outside": round(float(f[~mask].mean()), 4) if (~mask).any() else 0.0,
                "grad_mean": round(float(torch.abs(laplacian(v)).mean()), 5),
            })

    summary = {
        "kind": "field_lab",
        "model": "Gray-Scott: du=Du*lap(u)-u*v^2+F*(1-u); dv=Dv*lap(v)+u*v^2-(F+k)*v",
        "params": {kk: vv for kk, vv in vars(args).items() if kk != "out"},
        "series": series,
        "splits": splits,
        "final_components": series[-1]["components"] if series else 0,
        "max_components": max((r["components"] for r in series), default=0),
        "note": ("нет клеток, меток и правил деления: пятна делятся сами. Компоненты — описательная величина, "
                 "а не критерий: сначала наблюдение, критерий замораживается после разведки"),
        "not_claimed": [
            "что компоненты — индивидуумы (это описание, а не критерий)",
            "что система воспроизводится при другой сетке или другом dt",
            "что параметры (F, k) оптимальны: это первая точка режима, а не подбор",
        ],
    }
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[field] записано: {out}")
    last = series[-1] if series else {}
    print(f"[field] шагов {args.steps}, сетка {g}, F={F}, k={k}")
    print(f"[field] компонент: конец {summary['final_components']}, максимум {summary['max_components']}, "
          f"событий роста числа компонент: {splits}")
    if last:
        print(f"[field] занято {last['occupied_share']:.3f}, v внутри {last['v_inside']:.3f} против "
              f"{last['v_outside']:.3f}; u внутри {last['u_inside']:.3f} против {last['u_outside']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
