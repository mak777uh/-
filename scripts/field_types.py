"""field_types.py — два типа структур и скорость роста редкого (правильный прибор для сосуществования).

Зачем (E11, `docs/world-design.md` §10cf). Первый прибор был негоден: подсеянная капля сливается с местными
структурами, флаг родословной распространяется на всё слитое, и «редкий тип» оказывается большинством.

Здесь тип определяется **значением признака**, а не родословной:

  * два хорошо разделённых типа: `s_A = s_ref` (резидент) и `s_B = s_ref + delta` (редкий);
  * дочь наследует тип родителя;
  * мутация **переключает тип** (а не сдвигает значение) с вероятностью `p_flip`;
  * состав влияет на распад: `k_eff = k·(1 + beta·(s_ref − s))`, то есть тип B защищён сильнее;
  * на шаге `invade_at` вдали от центра подсевается капля типа B.

Что считается:
  * доля площади типа B (`fraction_B`) по срезам;
  * удельная скорость роста редкого `d ln(fraction_B)/dt` после подсева;
  * число компонент, интеграл по времени, разброс типов.

Критерий сосуществования (записан до данных): редкий тип сосуществует, если при начальной доле < 10 %
скорость роста **положительна** и удерживается до конца прогона; если отрицательна — это отсрочка исчезновения,
а не сосуществование.

Использование:
    python scripts/field_types.py --steps 6000 --out <json>
    python scripts/field_types.py --steps 6000 --hetero-period 3000 --out <json>
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


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="два типа структур: скорость роста редкого")
    ap.add_argument("--steps", type=int, default=6000)
    ap.add_argument("--grid", type=int, default=96)
    ap.add_argument("--dt", type=float, default=1.0)
    ap.add_argument("--seed", type=int, default=171)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--Du", type=float, default=0.16)
    ap.add_argument("--Dv", type=float, default=0.08)
    ap.add_argument("--F", type=float, default=0.035)
    ap.add_argument("--k", type=float, default=0.06)
    ap.add_argument("--beta", type=float, default=0.2, help="защита типа B от распада: k_eff = k*(1+beta*(s_ref-s))")
    ap.add_argument("--s-ref", type=float, default=1.0, help="признак резидента")
    ap.add_argument("--delta", type=float, default=0.4, help="насколько редкий тип выше резидента")
    ap.add_argument("--gamma", type=float, default=0.0,
                    help="частотная зависимость: редкий тип получает больше защиты (Chesson-style); "
                         "beta_eff = beta*(1 + gamma*(1 - 2*share))")
    ap.add_argument("--p-flip", type=float, default=0.02, help="вероятность смены типа при делении")
    ap.add_argument("--threshold", type=float, default=0.2)
    ap.add_argument("--min-cells", type=int, default=5)
    ap.add_argument("--invade-at", type=int, default=2000)
    ap.add_argument("--invade-radius", type=float, default=3.0)
    ap.add_argument("--hetero-amp", type=float, default=0.0)
    ap.add_argument("--hetero-period", type=float, default=0.0, help="0 = статичный узор")
    ap.add_argument("--sample-every", type=int, default=500)
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    import numpy as np
    import torch
    dev = torch.device(args.device if (args.device == "cpu" or torch.cuda.is_available()) else "cpu")
    g = args.grid
    gen = torch.Generator(device=dev).manual_seed(int(args.seed))
    rng = np.random.default_rng(int(args.seed))

    u = torch.ones((g, g), device=dev)
    v = torch.zeros((g, g), device=dev)
    yy = torch.arange(g, device=dev).view(-1, 1).expand(g, g)
    xx = torch.arange(g, device=dev).view(1, -1).expand(g, g)
    c, r0 = g // 2, max(2.0, 3.0 / (g / 96.0))
    m = ((xx - c) ** 2 + (yy - c) ** 2) <= r0 * r0
    v = torch.where(m, torch.full_like(v, 1.0), v)
    u = torch.where(m, torch.full_like(u, 0.25), u)

    # узор неоднородности
    G = None
    if args.hetero_amp > 0:
        ky = 2.0 * np.pi / 12.0
        G = (np.sin(ky * np.arange(g))[:, None] * np.cos(ky * np.arange(g))[None, :] + 1.0) / 2.0

    comp_type: dict[int, int] = {}      # 0 = резидент, 1 = редкий
    _invade_site = (g // 4, g // 4)
    _invade_step = None
    prev_lab = None
    series = []
    invaded = False

    for step in range(1, int(args.steps) + 1):
        # поле распада из типов
        modk_np = np.ones((g, g), dtype=np.float32)
        if prev_lab is not None and comp_type:
            area_by_type = {0: 0, 1: 0}
            for cid, tp in comp_type.items():
                area_by_type[tp] = area_by_type.get(tp, 0) + int((prev_lab == cid).sum())
            total_area = max(1, area_by_type[0] + area_by_type[1])
            for cid, tp in comp_type.items():
                share = area_by_type.get(tp, 0) / total_area
                beta_eff = args.beta * (1.0 + args.gamma * (1.0 - 2.0 * share))
                s_val = args.s_ref + (args.delta if tp == 1 else 0.0)
                modk_np[prev_lab == cid] = float(np.clip(1.0 + beta_eff * (args.s_ref - s_val), 0.3, 2.5))
        k_eff = args.k * torch.tensor(modk_np, device=dev)

        F_field = args.F
        if G is not None:
            s_t = 1.0 if (args.hetero_period <= 0 or (step // max(1, int(args.hetero_period))) % 2 == 0) else 0.0
            spatial = (2.0 * torch.tensor(G, device=dev, dtype=torch.float32) - 1.0) * (2.0 * s_t - 1.0)
            F_eff = args.F * (1.0 + args.hetero_amp * spatial)
        else:
            F_eff = torch.full((g, g), float(F_field), device=dev)

        uvv = u * v * v
        du = args.Du * laplacian(u) - uvv + F_eff * (1.0 - u)
        dv = args.Dv * laplacian(v) + uvv - (F_eff + k_eff) * v
        u = torch.clamp(u + args.dt * du, 0.0, 1.0)
        v = torch.clamp(v + args.dt * dv, 0.0, 1.0)

        # подсев редкого типа
        if not invaded and step == int(args.invade_at):
            # ищем место, где структуры нет: иначе подсев сливается с местной и тип размазывается
            vn_now = v.detach().cpu().numpy()
            best = None
            for cy_t in range(8, g - 8, 4):
                for cx_t in range(8, g - 8, 4):
                    if ((yy[cy_t, cx_t] - c) ** 2 + (xx[cy_t, cx_t] - c) ** 2) < (g // 3) ** 2:
                        continue
                    block = vn_now[max(0, cy_t - 6):cy_t + 7, max(0, cx_t - 6):cx_t + 7]
                    if block.size and float(block.max()) < 0.05:
                        best = (cy_t, cx_t)
                        break
                if best:
                    break
            cy, cx = best if best else (g // 4, g // 4)
            rr = max(2.0, float(args.invade_radius))
            m_inv = ((xx - cx) ** 2 + (yy - cy) ** 2) <= rr * rr
            v = torch.where(m_inv, torch.full_like(v, 0.8), v)
            u = torch.where(m_inv, torch.full_like(u, 0.3), u)
            _invade_site = (cy, cx)
            invaded = True

        # наблюдатель
        vn = v.detach().cpu().numpy()
        mask = vn > float(args.threshold)
        lab, n_comp = label(mask)
        sizes = {cid: int((lab == cid).sum()) for cid in range(1, n_comp + 1)}
        keep = [cid for cid, sz in sizes.items() if sz >= args.min_cells]
        new_type: dict[int, int] = {}
        for cid in keep:
            cells = (lab == cid)
            parent = None
            if prev_lab is not None:
                cand = prev_lab[cells]
                if cand.size:
                    vals, counts = np.unique(cand[cand > 0], return_counts=True)
                    if len(vals):
                        best = int(vals[int(np.argmax(counts))])
                        if counts.max() / cells.sum() >= 0.5 and best in comp_type:
                            parent = best
            if parent is not None:
                tp = comp_type[parent]
                if rng.random() < args.p_flip:
                    tp = 1 - tp
            else:
                tp = 0
            # подсев: компонента, накрывающая точку подсева, получает тип 1
            iy, ix = _invade_site
            if invaded and lab[iy, ix] == cid and (step - int(args.invade_at)) <= int(args.sample_every):
                tp = 1
            new_type[cid] = tp
        comp_type = new_type
        prev_lab = np.where(np.isin(lab, keep), lab, 0)

        near_invasion = invaded and 0 <= (step - int(args.invade_at)) <= 1500
        every = 50 if near_invasion else int(args.sample_every)
        if step % every == 0 or step == 1:
            area_b = 0
            for cid, tp in comp_type.items():
                if tp == 1:
                    area_b += int((prev_lab == cid).sum())
            total = int(mask.sum()) or 1
            series.append({
                "step": step,
                "components": len(keep),
                "fraction_B": round(area_b / total, 4),
                "area_B": area_b,
                "occupied": round(float(mask.mean()), 4),
            })

    post = [r for r in series if r["step"] >= int(args.invade_at) and r["fraction_B"] > 0]
    # скорость меряем ТОЛЬКО пока тип редкий: иначе измеряется уже не вторжение
    rare_phase = [r for r in post if r["fraction_B"] < 0.20]
    rate = None
    if len(rare_phase) >= 2:
        dt = rare_phase[-1]["step"] - rare_phase[0]["step"]
        rate = round((math.log(rare_phase[-1]["fraction_B"]) - math.log(rare_phase[0]["fraction_B"])) / max(1, dt), 5)

    result = {
        "kind": "field_types",
        "model": ("Грей–Скотт + два типа по значению признака (s_ref и s_ref+delta), наследование с переключением "
                  "типа, разная защита от распада; подсев редкого типа отдельной каплей"),
        "params": {k: v for k, v in vars(args).items() if k != "out"},
        "series": series,
        "coexistence": {
            "fraction_B_first_after_invasion": post[0]["fraction_B"] if post else None,
            "fraction_B_last": post[-1]["fraction_B"] if post else None,
            "growth_rate": rate,
            "rare_phase_samples": len(rare_phase),
            "verdict": ("сосуществование" if (rate is not None and rate > 0)
                        else "отсрочка исчезновения (скорость не положительна)"),
        },
        "criteria": {
            "start_share_below_10pct": (post[0]["fraction_B"] < 0.10) if post else None,
            "positive_growth": (rate is not None and rate > 0),
        },
        "not_claimed": [
            "что типы — виды: это два значения признака, а не биологические виды",
            "что скорость > 0 доказывает устойчивое сосуществование: нужен ещё анализ вторжения при разных долях",
            "что результат переносится на другую сетку и шаг",
        ],
    }
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[types] записано: {out}")
    c_ = result["coexistence"]
    print(f"[types] beta={args.beta}, amp={args.hetero_amp}, period={args.hetero_period}: "
          f"доля B {c_['fraction_B_first_after_invasion']} → {c_['fraction_B_last']}, "
          f"скорость {c_['growth_rate']} → {c_['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
