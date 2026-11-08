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


def label_components(mask):
    """4-connected labels of a boolean mask, periodic in both axes (the world is a torus)."""
    import numpy as np
    h, w = mask.shape
    lab = np.zeros((h, w), dtype=np.int32)
    cur = 0
    for y in range(h):
        for x in range(w):
            if mask[y, x] and lab[y, x] == 0:
                cur += 1
                stack = [(y, x)]
                lab[y, x] = cur
                while stack:
                    cy, cx = stack.pop()
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = (cy + dy) % h, (cx + dx) % w
                        if mask[ny, nx] and lab[ny, nx] == 0:
                            lab[ny, nx] = cur
                            stack.append((ny, nx))
    return lab, cur


def match_events(prev_lab, lab_now, min_overlap: float = 0.5):
    """Count real splits and merges by matching components across two snapshots on overlap.

    A component of the previous snapshot is a PARENT of a component now if at least `min_overlap` of the
    current component's cells belonged to it. A parent with two or more children is one split event; a child
    with two or more parents is one merge event. This is the definition the tracker uses for identity, so the
    two agree.
    """
    import numpy as np
    parents_of = {}
    children_of = {}
    for cid in range(1, int(lab_now.max()) + 1):
        cells = lab_now == cid
        total = int(cells.sum())
        if total == 0:
            continue
        vals, counts = np.unique(prev_lab[cells], return_counts=True)
        for v, c in zip(vals, counts):
            if v == 0:
                continue
            if float(c) / total >= min_overlap:
                parents_of.setdefault(int(v), set()).add(cid)
                children_of.setdefault(cid, set()).add(int(v))
    splits = sum(1 for kids in parents_of.values() if len(kids) >= 2)
    merges = sum(1 for ps in children_of.values() if len(ps) >= 2)
    return splits, merges


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
    ap.add_argument("--seed-v", type=float, default=1.0, help="значение v в зародыше (0.5 маргинально)")
    ap.add_argument("--seed-radius", type=float, default=3.0, help="радиус зародыша в ФИЗИЧЕСКИХ единицах")
    ap.add_argument("--no-catalysis", action="store_true",
                    help="нулевая модель: убрать член u*v^2 (нет автокатализа, структуры не должны возникать)")
    ap.add_argument("--seed-cells", type=int, default=0,
                    help="0 = один зародыш в центре; N>0 = N случайных зародышей (для проверки, что деление не наше)")
    ap.add_argument("--dump-fields", default=None,
                    help="каталог для снимков полей z=v, w=u (для критерия индивидуации)")
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
            v = torch.where(m, torch.full_like(v, float(args.seed_v)), v)
            u = torch.where(m, torch.full_like(u, 0.25), u)
    else:
        # радиус задаётся в физических единицах через масштаб h = grid/96, чтобы сравнение по сеткам было честным
        h = g / 96.0
        c, r0 = g // 2, max(2.0, float(args.seed_radius) / h)
        m = ((xx - c) ** 2 + (yy - c) ** 2) <= r0 * r0
        v = torch.where(m, torch.full_like(v, float(args.seed_v)), v)
        u = torch.where(m, torch.full_like(u, 0.25), u)

    Du, Dv, F, k = float(args.Du), float(args.Dv), float(args.F), float(args.k)
    series, prev_n = [], None
    component_count_delta = 0
    split_events = 0
    merge_events = 0
    prev_lab = None
    for step in range(1, int(args.steps) + 1):
        uvv = u * v * v if not bool(args.no_catalysis) else torch.zeros_like(u)
        du = Du * laplacian(u) - uvv + F * (1.0 - u)
        dv = Dv * laplacian(v) + uvv - (F + k) * v
        u = torch.clamp(u + args.dt * du, min=0.0, max=1.0)
        v = torch.clamp(v + args.dt * dv, min=0.0, max=1.0)

        # снимки полей в формате критерия: z = v (материал), w = u (пища) — независимое поле
        if args.dump_fields and step % int(args.sample_every) == 0:
            import json as _json
            from pathlib import Path as _Path
            d = _Path(args.dump_fields)
            d.mkdir(parents=True, exist_ok=True)
            snap = {
                "step": step,
                "z": [[round(float(x), 4) for x in row] for row in v.detach().to("cpu").tolist()],
                "w": [[round(float(x), 4) for x in row] for row in u.detach().to("cpu").tolist()],
            }
            (d / ("fields_%05d.json" % step)).write_text(_json.dumps(snap) + "\n", encoding="utf-8")

        if step % int(args.sample_every) == 0 or step == 1:
            import numpy as np
            p = v.detach().cpu().numpy()
            f = u.detach().cpu().numpy()
            mask = p > float(args.threshold)
            n, sizes = components(mask)
            # `component_count_delta` is what the old `splits` actually measured: the rise in the number of
            # components between two snapshots. It is kept under its honest name.
            if prev_n is not None and n > prev_n:
                component_count_delta += n - prev_n
            # Real events: match the components of this snapshot to those of the previous one by overlap, and
            # count a parent with several children as a split, several parents with one child as a merge.
            # A split plus a merge in one interval gives delta = 0 but two events; the old counter saw nothing.
            lab_now, _ = label_components(mask)
            if prev_lab is not None:
                sp, mg = match_events(prev_lab, lab_now)
                split_events += sp
                merge_events += mg
            prev_lab = lab_now
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
        "component_count_delta": component_count_delta,
        "split_events": split_events,
        "merge_events": merge_events,
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
          f"прирост числа компонент: {component_count_delta}, делений: {split_events}, слияний: {merge_events}")
    if last:
        print(f"[field] занято {last['occupied_share']:.3f}, v внутри {last['v_inside']:.3f} против "
              f"{last['v_outside']:.3f}; u внутри {last['u_inside']:.3f} против {last['u_outside']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
