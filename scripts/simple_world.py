"""simple_world.py — минимальный мир БЕЗ NCA: проверка, свойство ли это среды или нашей клетки.

Зачем (E2, `reports/2026-10-29-impact-order.md`). Главный вывод линии пруда: «мир ограничен местом, а не
энергией» (×10 по притоку не меняет население). Но в пруде объект задан жёстко: NCA-правило, масса 24,
почкование только в свободную соседнюю клетку. Поэтому неизвестно, свойство это среды или конструкции.

Здесь объект **другой**: нет NCA-правила, нет порога массы, нет почкования «споры». Есть только:
    * клетка с энергией;
    * приток из локального ресурса;
    * трата на поддержание;
    * деление в любую свободную соседнюю клетку при энергии выше порога;
    * смерть при энергии ниже нуля;
    * наследуемая метка с мутацией (чтобы считать линии).

Вопрос, на который отвечает опыт: **меняется ли население при ×10 по притоку**, если объект другой?

    python scripts/simple_world.py --steps 1000 --income 0.20 --out <json>
    python scripts/simple_world.py --steps 1000 --income 0.02    # ×10 меньше
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="минимальный мир без NCA: ёмкость против энергии")
    ap.add_argument("--steps", type=int, default=1000)
    ap.add_argument("--grid", type=int, default=32)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--income", type=float, default=0.20, help="приток ресурса на клетку за шаг")
    ap.add_argument("--maintenance", type=float, default=0.02, help="трата на поддержание")
    ap.add_argument("--divide-at", type=float, default=1.0, help="порог энергии для деления")
    ap.add_argument("--energy-cap", type=float, default=2.0, help="потолок энергии клетки")
    ap.add_argument("--mutation-rate", type=float, default=0.05)
    ap.add_argument("--sample-every", type=int, default=50)
    ap.add_argument("--update-probability", type=float, default=1.0,
                    help="доля клеток, которые вообще действуют за шаг (темп)")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    import torch
    dev = torch.device(args.device)
    g = args.grid
    gen = torch.Generator(device=dev).manual_seed(int(args.seed))

    alive = torch.zeros((g, g), dtype=torch.bool, device=dev)
    energy = torch.zeros((g, g), device=dev)
    tag = torch.full((g, g), -1, dtype=torch.long, device=dev)
    # ресурс: локальный запас, который восстанавливается с притоком
    res = torch.ones((g, g), device=dev)

    c = g // 2
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            alive[c + dy, c + dx] = True
            energy[c + dy, c + dx] = 0.8
            tag[c + dy, c + dx] = 0
    next_tag = 1

    series = []
    for step in range(1, int(args.steps) + 1):
        n_alive = int(alive.sum())
        # приток пропорционален локальному ресурсу и ограничен долей (как в пруде: min(own, k*own))
        gain = args.income * torch.clamp(res, 0.0, 1.0)
        take = torch.where(alive, gain, torch.zeros_like(gain))
        energy = torch.where(alive, torch.clamp(energy + take - args.maintenance, min=0.0), energy)
        # кто действует в этом шаге (темп)
        act = torch.rand((g, g), generator=gen, device=dev) < float(args.update_probability)
        # клетки, готовые делиться
        ready = alive & act & (energy >= float(args.divide_at))
        ys, xs = ready.nonzero(as_tuple=True)
        for y, x in zip(ys.tolist(), xs.tolist()):
            # свободные соседи
            cand = []
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = (y + dy) % g, (x + dx) % g
                if not bool(alive[ny, nx]):
                    cand.append((ny, nx))
            if not cand:
                energy[y, x] = min(float(args.energy_cap), float(energy[y, x]))
                continue
            k = int(torch.randint(0, len(cand), (1,), generator=gen).item())
            ny, nx = cand[k]
            half = float(energy[y, x]) * 0.5
            energy[y, x] = half
            energy[ny, nx] = half
            alive[ny, nx] = True
            parent_tag = int(tag[y, x])
            if float(torch.rand((1,), generator=gen, device=dev).item()) < args.mutation_rate:
                tag[ny, nx] = next_tag
                next_tag += 1
            else:
                tag[ny, nx] = parent_tag
        # смерть от голода
        dead = alive & (energy <= 1e-9)
        alive = alive & ~dead
        energy = torch.where(alive, energy, torch.zeros_like(energy))
        tag = torch.where(alive, tag, torch.full_like(tag, -1))
        # ресурс восстанавливается
        res = torch.clamp(res + 0.02 * (1.0 - res), 0.0, 1.0)

        if step % int(args.sample_every) == 0 or step == 1:
            n = int(alive.sum())
            if n:
                vals = tag[alive]
                uniq, counts = torch.unique(vals, return_counts=True)
                probs = counts.float() / float(n)
                q1 = float(1.0 / float((probs ** 2).sum()))
                ge5 = int((counts >= 5).sum())
            else:
                q1, ge5 = 0.0, 0
            series.append({"step": step, "alive": n, "q1": round(q1, 3), "lineages_ge5": ge5})

    occ = series[-1]["alive"] / float(g * g) if series else 0.0
    summary = {
        "kind": "simple_world",
        "model": ("агент без NCA: энергия, деление при пороге в любую свободную соседнюю клетку, смерть при нуле; "
                  "нет массы, нет почкования-споры, нет правила мира"),
        "params": {k: v for k, v in vars(args).items() if k != "out"},
        "series": series,
        "final_alive": series[-1]["alive"] if series else 0,
        "capacity_used": round(occ, 3),
        "note": ("проверка: меняется ли население при ×10 по притоку, когда объект другой"),
        "not_claimed": [
            "что это модель жизни: это минимальный агент для проверки одного механизма",
            "что население не зависит от притока при любых параметрах",
            "что линии здесь сопоставимы с линиями пруда",
        ],
    }
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[simple] записано: {out}")
    print(f"[simple] income {args.income}: живых {summary['final_alive']}, ёмкость {summary['capacity_used']:.2f}, "
          f"q1 {series[-1]['q1'] if series else 0}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
