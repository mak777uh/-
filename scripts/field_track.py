"""field_track.py — L3 в поле: отслеживание компонент и наследование состава.

Зачем (E6c, пре-регистрация `reports/2026-10-29-e6c-inheritance-plan.md`). E6b показал, что пассивная примесь
НЕ наследуется: в Грея–Скотте нет переноса материала, состав каждый шаг пересчитывается из плотности.

Здесь наследование делается иначе: структуры **определяются постфактум** (компоненты порога по v), каждая
получает собственный состав, а при расщеплении дочери наследуют состав родителя с мутацией. Состав влияет на
локальный рост, поэтому возможен отбор.

Что важно: компоненты не заданы в правилах физики — они результат порога и связности. Наблюдатель только
сопоставляет их между шагами по перекрытию.

Критерий (фиксирован до данных):
  S1 сдвиг среднего состава > 2·sd между компонентами (относительно контроля eps=0);
  S2 наследуемость: корреляция «родитель → дочь» ≥ 0.5;
  S3 сдвиг не исчезает при удвоении горизонта;
  S4 в контроле (eps=0) S1 и S3 не выполняются.

Использование:
    python scripts/field_track.py --steps 6000 --eps 0.5 --out <json>
    python scripts/field_track.py --steps 6000 --eps 0.0 --out <json>   # контроль
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def laplacian(x):
    import torch
    return (torch.roll(x, 1, 0) + torch.roll(x, -1, 0) +
            torch.roll(x, 1, 1) + torch.roll(x, -1, 1) - 4.0 * x)


def label(mask):
    """Метки компонент 4-связности (numpy, на сетке 96 — быстро)."""
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


def pearson(a, b):
    n = len(a)
    if n < 3:
        return None
    ma, mb = sum(a) / n, sum(b) / n
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((y - mb) ** 2 for y in b)
    if va <= 0 or vb <= 0:
        return None
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / math.sqrt(va * vb)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="поле с отслеживанием компонент и наследуемым составом")
    ap.add_argument("--steps", type=int, default=6000)
    ap.add_argument("--grid", type=int, default=96)
    ap.add_argument("--dt", type=float, default=1.0)
    ap.add_argument("--seed", type=int, default=171)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--Du", type=float, default=0.16)
    ap.add_argument("--Dv", type=float, default=0.08)
    ap.add_argument("--F", type=float, default=0.035)
    ap.add_argument("--k", type=float, default=0.06)
    ap.add_argument("--eps", type=float, default=0.5,
                    help="влияние состава на рост: F_eff = F*(1+eps*(s - s_ref)), зажато в [0.5, 1.5]")
    ap.add_argument("--freq-dep", type=float, default=0.0,
                    help="E6e: частотная зависимость — защита слабеет с ростом доли похожих составов: "
                         "beta_eff = beta·(1 − freq_dep·share)")
    ap.add_argument("--bin-width", type=float, default=0.2, help="ширина корзины по составу для учёта доли")
    ap.add_argument("--beta", type=float, default=0.0,
                    help="E6d: состав влияет на ВЫЖИВАНИЕ (распад), а не на рост: k_eff = k*(1 + beta*(s_ref - s))")
    ap.add_argument("--s-ref", type=float, default=1.0, help="опорный состав (дикий тип)")
    ap.add_argument("--mutation", type=float, default=0.05, help="sigma мутации состава при делении")
    ap.add_argument("--threshold", type=float, default=0.2)
    ap.add_argument("--min-cells", type=int, default=5)
    ap.add_argument("--overlap", type=float, default=0.5, help="доля клеток дочери, при которой родитель признан")
    ap.add_argument("--sample-every", type=int, default=1000)
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    import numpy as np
    import torch
    dev = torch.device(args.device if (args.device == "cpu" or torch.cuda.is_available()) else "cpu")
    g = args.grid
    gen = torch.Generator(device=dev).manual_seed(int(args.seed))

    u = torch.ones((g, g), device=dev)
    v = torch.zeros((g, g), device=dev)
    yy = torch.arange(g, device=dev).view(-1, 1).expand(g, g)
    xx = torch.arange(g, device=dev).view(1, -1).expand(g, g)
    c, r0 = g // 2, max(2.0, 3.0 / (g / 96.0))
    m = ((xx - c) ** 2 + (yy - c) ** 2) <= r0 * r0
    v = torch.where(m, torch.full_like(v, 1.0), v)
    u = torch.where(m, torch.full_like(u, 0.25), u)

    rng = np.random.default_rng(int(args.seed))
    next_id = 1
    # состав: id компоненты → s
    comp_s: dict[int, float] = {}
    prev_lab = None
    pairs: list[tuple[float, float]] = []   # (s родителя, s дочери)
    splits = 0
    series = []

    for step in range(1, int(args.steps) + 1):
        # поле роста из состава: у каждой компоненты свой F
        mod = torch.ones((g, g), device=dev)
        mod_k = torch.ones((g, g), device=dev)
        if prev_lab is not None and comp_s:
            mod_np = np.ones((g, g), dtype=np.float32)
            modk_np = np.ones((g, g), dtype=np.float32)
            # E6e: доля похожих составов (по корзинам) — на неё ослабляется защита
            all_s = list(comp_s.values())
            shares = {}
            if args.freq_dep > 0 and all_s:
                bins = [round(v / args.bin_width) for v in all_s]
                from collections import Counter
                cnt = Counter(bins)
                for i, cid in enumerate(comp_s.keys()):
                    shares[cid] = cnt[bins[i]] / len(all_s)
            for cid, s_val in comp_s.items():
                mod_np[prev_lab == cid] = float(np.clip(1.0 + args.eps * (s_val - args.s_ref), 0.5, 1.5))
                # E6d: высокая s ЗАЩИЩАЕТ от распада (k_eff меньше), низкая — ускоряет распад
                beta_eff = args.beta * (1.0 - args.freq_dep * shares.get(cid, 0.0))
                modk_np[prev_lab == cid] = float(np.clip(1.0 + beta_eff * (args.s_ref - s_val), 0.3, 2.5))
            mod = torch.tensor(mod_np, device=dev)
            mod_k = torch.tensor(modk_np, device=dev)
        F_eff = args.F * mod
        k_eff = args.k * mod_k

        uvv = u * v * v
        du = args.Du * laplacian(u) - uvv + F_eff * (1.0 - u)
        dv = args.Dv * laplacian(v) + uvv - (F_eff + k_eff) * v
        u = torch.clamp(u + args.dt * du, 0.0, 1.0)
        v = torch.clamp(v + args.dt * dv, 0.0, 1.0)

        # --- наблюдатель: компоненты и сопоставление ---
        vn = v.detach().cpu().numpy()
        mask = vn > float(args.threshold)
        lab, n_comp = label(mask)
        sizes = {cid: int((lab == cid).sum()) for cid in range(1, n_comp + 1)}
        keep = [cid for cid, sz in sizes.items() if sz >= args.min_cells]
        new_s: dict[int, float] = {}
        for cid in keep:
            cells = (lab == cid)
            parent = None
            if prev_lab is not None:
                cand = prev_lab[cells]
                if cand.size:
                    vals, counts = np.unique(cand[cand > 0], return_counts=True)
                    if len(vals):
                        best = int(vals[int(np.argmax(counts))])
                        if counts.max() / cells.sum() >= args.overlap and best in comp_s:
                            parent = best
            if parent is not None:
                new_s[cid] = comp_s[parent]
            else:
                new_s[cid] = float(rng.normal(args.s_ref, args.mutation))
        # расщепление: у одного родителя несколько дочерей
        used_parents: dict[int, int] = {}
        if prev_lab is not None:
            for cid in keep:
                cells = (lab == cid)
                cand = prev_lab[cells]
                if cand.size:
                    vals, counts = np.unique(cand[cand > 0], return_counts=True)
                    if len(vals):
                        best = int(vals[int(np.argmax(counts))])
                        if counts.max() / cells.sum() >= args.overlap:
                            used_parents[best] = used_parents.get(best, 0) + 1
        for parent, k_children in used_parents.items():
            if k_children >= 2 and parent in comp_s:
                splits += 1
                for cid in keep:
                    cells = (lab == cid)
                    cand = prev_lab[cells] if prev_lab is not None else np.array([])
                    if cand.size:
                        vals, counts = np.unique(cand[cand > 0], return_counts=True)
                        if len(vals) and int(vals[int(np.argmax(counts))]) == parent:
                            child_s = comp_s[parent] + float(rng.normal(0.0, args.mutation))
                            new_s[cid] = child_s
                            pairs.append((comp_s[parent], child_s))
        comp_s = {cid: s_val for cid, s_val in new_s.items()}
        prev_lab = np.where(np.isin(lab, keep), lab, 0)

        if step % int(args.sample_every) == 0 or step == 1:
            vals = list(comp_s.values())
            series.append({
                "step": step,
                "components": len(vals),
                "s_mean": round(float(np.mean(vals)), 4) if vals else 0.0,
                "s_sd_between": round(float(np.std(vals)), 4) if len(vals) > 1 else 0.0,
                "s_wild_fraction": round(float(np.mean([abs(s - args.s_ref) < 1e-9 for s in vals])), 4) if vals else 0.0,
                "occupied": round(float(mask.mean()), 4),
            })

    r_parent = pearson([p for p, _ in pairs], [q for _, q in pairs])
    result = {
        "kind": "field_track",
        "model": ("Грей–Скотт + отслеживание компонент: каждая компонента имеет свой состав, наследуемый при "
                  "расщеплении с мутацией; состав влияет на локальный F"),
        "params": {k: v for k, v in vars(args).items() if k != "out"},
        "series": series,
        "selection": {
            "s_mean_first": series[0]["s_mean"] if series else None,
            "s_mean_last": series[-1]["s_mean"] if series else None,
            "s_sd_between_last": series[-1]["s_sd_between"] if series else None,
            "splits": splits,
            "parent_child_pairs": len(pairs),
            "inheritability_r": round(r_parent, 3) if r_parent is not None else None,
        },
        "criteria": {
            "S1_shift_gt_2sd": None,
            "S2_inheritability_ge_0.5": (r_parent is not None and r_parent >= 0.5),
            "S3_survives_doubling": "проверяется сравнением с прогоном вдвое длиннее",
            "S4_control_eps0": "проверяется прогоном с --eps 0",
        },
        "note": ("S1 требует сравнения с контролем: сдвиг среднего считается от контроля, а не от старта, "
                 "потому что состав дрейфует и в контроле"),
        "not_claimed": [
            "что отбор доказан: нужно сравнение с контролем eps=0 и удвоенный горизонт",
            "что правило сопоставления оптимально: порог перекрытия 0.5 фиксирован до данных",
            "что структуры устойчивы к сетке: не проверялось",
        ],
    }
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[track] записано: {out}")
    s = result["selection"]
    print(f"[track] eps={args.eps}: компонент {series[-1]['components'] if series else 0}, "
          f"s средний {s['s_mean_first']} → {s['s_mean_last']}, разброс {s['s_sd_between_last']}, "
          f"расщеплений {s['splits']}, наследуемость r={s['inheritability_r']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
