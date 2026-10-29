"""field_inherit.py — L3 в поле: наследуемый состав, который влияет на рост.

Зачем. В `field_lab.py` структуры возникают и делятся, но у них нет наследственности — значит нет отбора,
и это уровень L2, а не L3. Здесь добавлено третье поле `s` — «состав», который:

  * переносится вместе с материалом (пассивная примесь: `ds/dt = Ds·∇²s + P·v − λ·s`);
  * слегка мутирует (шум на каждом шаге);
  * влияет на скорость роста: `F_eff = F · (1 + eps·(s − s̄))`.

Тогда, если высокая `s` полезна, структуры с высокой `s` растут быстрее, и распределение `s` **сдвигается**.
Это и есть отбор без заданного «генома»: наследственность — свойство переноса примеси, а не сущность.

Что считается:
  * средний `s` внутри структур и снаружи;
  * сдвиг среднего `s` во времени (есть ли отбор);
  * разнообразие `s` между структурами (дисперсия — топливо отбора);
  * число компонент и доля занятого поля.

Использование:
    python scripts/field_inherit.py --steps 12000 --eps 0.5 --out <json>
    python scripts/field_inherit.py --steps 12000 --eps 0.0 --out <json>   # контроль: состав не влияет
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
    import numpy as np
    h, w = mask.shape
    labels = np.zeros((h, w), dtype=np.int32)
    cur, cells = 0, []
    for y in range(h):
        for x in range(w):
            if mask[y, x] and labels[y, x] == 0:
                cur += 1
                stack, acc = [(y, x)], []
                labels[y, x] = cur
                while stack:
                    cy, cx = stack.pop()
                    acc.append((cy, cx))
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = (cy + dy) % h, (cx + dx) % w
                        if mask[ny, nx] and labels[ny, nx] == 0:
                            labels[ny, nx] = cur
                            stack.append((ny, nx))
                cells.append(acc)
    return cells


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="поле с наследуемым составом (L3)")
    ap.add_argument("--steps", type=int, default=12000)
    ap.add_argument("--grid", type=int, default=96)
    ap.add_argument("--dt", type=float, default=1.0)
    ap.add_argument("--seed", type=int, default=171)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--Du", type=float, default=0.16)
    ap.add_argument("--Dv", type=float, default=0.08)
    ap.add_argument("--Ds", type=float, default=0.10, help="диффузия состава")
    ap.add_argument("--F", type=float, default=0.0367)
    ap.add_argument("--k", type=float, default=0.0649)
    ap.add_argument("--eps", type=float, default=0.5,
                    help="насколько состав влияет на рост: F_eff = F*(1+eps*(s-s̄))")
    ap.add_argument("--s-production", type=float, default=0.25)
    ap.add_argument("--s-decay", type=float, default=0.25)
    ap.add_argument("--s-ref", type=float, default=0.25,
                    help="опорный состав: F_eff = F*(1+eps*(s-s_ref)); фиксирован, иначе отбор невозможен")
    ap.add_argument("--s-noise", type=float, default=0.02, help="мутация состава")
    ap.add_argument("--threshold", type=float, default=0.2)
    ap.add_argument("--sample-every", type=int, default=1000)
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    import torch
    dev = torch.device(args.device if (args.device == "cpu" or torch.cuda.is_available()) else "cpu")
    g = args.grid
    gen = torch.Generator(device=dev).manual_seed(int(args.seed))

    u = torch.ones((g, g), device=dev)
    v = torch.zeros((g, g), device=dev)
    s = torch.zeros((g, g), device=dev)
    yy = torch.arange(g, device=dev).view(-1, 1).expand(g, g)
    xx = torch.arange(g, device=dev).view(1, -1).expand(g, g)
    h_scale = g / 96.0
    c, r0 = g // 2, max(2.0, 3.0 / h_scale)
    m = ((xx - c) ** 2 + (yy - c) ** 2) <= r0 * r0
    v = torch.where(m, torch.full_like(v, 1.0), v)
    u = torch.where(m, torch.full_like(u, 0.25), u)
    # стартовый состав: у зародыша средний, дальше он разносится делением
    s = torch.where(m, torch.full_like(s, 1.0), s)

    series = []
    for step in range(1, int(args.steps) + 1):
        uvv = u * v * v
        s_mean = float(s[v > args.threshold].mean()) if bool((v > args.threshold).any()) else 0.0
        # модуляция ограничена: без зажима s накапливается, F_eff растёт, и член (F_eff + k)·v душит материал
        # ВАЖНО: опорная точка ФИКСИРОВАНА, а не равна среднему. Центровка по среднему (s − s̄) убирает
        # направление отбора: структуры выше среднего растут быстрее, но среднее пересчитывается каждый шаг
        # и не может сдвинуться. С фиксированной s0 появляется градиент, и среднее может уехать.
        _mod = torch.clamp(1.0 + args.eps * (s - args.s_ref), 0.5, 1.5)
        F_eff = args.F * _mod
        du = args.Du * laplacian(u) - uvv + F_eff * (1.0 - u)
        dv = args.Dv * laplacian(v) + uvv - (F_eff + args.k) * v
        ds = (args.Ds * laplacian(s) + args.s_production * v
              - args.s_decay * s + args.s_noise * torch.randn((g, g), generator=gen, device=dev) * v)
        u = torch.clamp(u + args.dt * du, 0.0, 1.0)
        v = torch.clamp(v + args.dt * dv, 0.0, 1.0)
        s = torch.clamp(s + args.dt * ds, 0.0, 5.0)

        if step % int(args.sample_every) == 0 or step == 1:
            import numpy as np
            pv = v.detach().cpu().numpy()
            ps = s.detach().cpu().numpy()
            mask = pv > float(args.threshold)
            cells = [c_ for c_ in components(mask) if len(c_) >= 5]
            per = [float(ps[y, x].mean()) for c_ in cells for (y, x) in [np.array(c_).T] if len(c_) >= 5]
            per = []
            for c_ in cells:
                ys = [p[0] for p in c_]
                xs = [p[1] for p in c_]
                per.append(float(ps[ys, xs].mean()))
            series.append({
                "step": step,
                "components": len(cells),
                "occupied": round(float(mask.mean()), 4),
                "s_inside": round(float(ps[mask].mean()), 4) if mask.any() else 0.0,
                "s_outside": round(float(ps[~mask].mean()), 4) if (~mask).any() else 0.0,
                "s_between_sd": round(float(np.std(per)), 4) if len(per) > 1 else 0.0,
                "s_between_min": round(min(per), 4) if per else 0.0,
                "s_between_max": round(max(per), 4) if per else 0.0,
            })

    first, last = (series[0] if series else {}), (series[-1] if series else {})
    summary = {
        "kind": "field_inherit",
        "model": ("Грей–Скотт + пассивный наследуемый состав s: ds = Ds·lap(s) + P·v − λ·s + шум·v; "
                  "F_eff = F·(1 + eps·(s − s̄)) — состав влияет на рост, поэтому возможен отбор"),
        "params": {k: v for k, v in vars(args).items() if k != "out"},
        "series": series,
        "selection": {
            "s_inside_first": first.get("s_inside"),
            "s_inside_last": last.get("s_inside"),
            "shift": (round(last.get("s_inside", 0) - first.get("s_inside", 0), 4)
                      if series and "s_inside" in first else None),
            "s_between_sd_last": last.get("s_between_sd"),
        },
        "note": ("наследование здесь — свойство переноса примеси вместе с материалом, а не заданный геном; "
                 "сдвиг s внутри структур интерпретируется как отбор, только если он больше разброса между структурами"),
        "not_claimed": [
            "что сдвиг s — непременно отбор: контроль при eps = 0 обязателен",
            "что структуры устойчивы к сетке (для этого нужен прогон вдвое мельче)",
            "что состав передаётся точно: мутация задана шумом, а не механизмом деления",
        ],
    }
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[inherit] записано: {out}")
    print(f"[inherit] eps={args.eps}: компонент {summary['series'][-1]['components'] if series else 0}, "
          f"s внутри {summary['selection']['s_inside_first']} → {summary['selection']['s_inside_last']}, "
          f"разброс между структурами {summary['selection']['s_between_sd_last']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
