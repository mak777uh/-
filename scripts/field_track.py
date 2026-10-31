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
    ap.add_argument("--global-noise-amp", type=float, default=0.0,
                    help="X18: модуляция притока ВО ВСЕМ ПОЛЕ одновременно (пространственно однородная, "
                         "случайная во времени): F *= 1 + amp*(2*S(t)-1). Отличается от --hetero-amp тем, "
                         "что не создаёт пространственной неоднородности")
    ap.add_argument("--global-noise-rate", type=float, default=0.05,
                    help="X18: как часто меняется глобальный сигнал (доля шага: 1.0 = каждый шаг)")
    ap.add_argument("--global-noise-seed", type=int, default=0, help="X18: сид глобального сигнала")
    ap.add_argument("--trait-field", action="store_true",
                    help="X32: признак живёт В СРЕДЕ (медленно диффундирующее поле h), а не в словаре наблюдателя; "
                         "тогда наследование — следствие динамики, а не присваивания")
    ap.add_argument("--trait-diffusion", type=float, default=0.02, help="X32: коэффициент диффузии признака (<< Du)")
    ap.add_argument("--trait-decay", type=float, default=0.0, help="X32: возврат признака к s_ref за шаг")
    ap.add_argument("--trait-mutation", type=float, default=0.02, help="X32: шум признака в живых клетках за шаг")
    ap.add_argument("--trait-init", type=float, default=1.0, help="X32: стартовое значение признака")
    ap.add_argument("--hetero-amp", type=float, default=0.0,
                    help="E7: сила пространственной неоднородности притока: F(x,y) = F*(1 + amp*(2S(t)-1)*(2G(x,y)-1))")
    ap.add_argument("--hetero-scale", type=float, default=12.0, help="масштаб пространственного узора G (клеток)")
    ap.add_argument("--hetero-signal", default=None,
                    help="файл со значениями S(t) в 0..1 (дамп с железа); без него S = 0.5 (статичный узор)")
    ap.add_argument("--hetero-period", type=float, default=0.0,
                    help="E9: период смены узора в шагах (0 = статика). Узор инвертируется с этим периодом: "
                         "медленно меняющаяся неоднородность против дрожащей")
    ap.add_argument("--hetero-shuffle", action="store_true", help="перемешать S(t) по времени — контроль структуры")
    ap.add_argument("--buffer-tau", type=float, default=0.0,
                    help="E12: время памяти буфера в шагах (0 = буфера нет). Поле B помнит, где была структура, "
                         "и медленно распадается: dB/dt = v - B/tau")
    ap.add_argument("--protect-fading", type=float, default=0.0,
                    help="E12c: буфер через СМЕРТНОСТЬ — ослаблять распад там, где материал гаснет: "
                         "k_eff *= (1 - protect*(1 - v)) при protect в 0..1")
    ap.add_argument("--buffer-rescue", action="store_true",
                    help="E12b: спасать ГАСНУЩЕЕ — усиливать приток там, где v мало, а память высока "
                         "(другой знак обратной связи, чем буфер-награда)")
    ap.add_argument("--buffer-gain", type=float, default=0.0,
                    help="E12: насколько память усиливает приток в месте, где структура была: F_eff *= (1 + gain*B)")
    ap.add_argument("--invade-s", type=float, default=None,
                    help="E11: состав редкого типа, который подсевается отдельной каплей (например 1.4)")
    ap.add_argument("--invade-radius", type=float, default=3.0, help="радиус капли редкого типа")
    ap.add_argument("--invade-at", type=int, default=2000, help="шаг подсева редкого типа")
    ap.add_argument("--invade-threshold", type=float, default=1.2,
                    help="порог состава: компоненты выше считаются редким типом при измерении")
    ap.add_argument("--freq-dep", type=float, default=0.0,
                    help="E6e: частотная зависимость — защита слабеет с ростом доли похожих составов: "
                         "beta_eff = beta·(1 − freq_dep·share)")
    ap.add_argument("--bin-width", type=float, default=0.2, help="ширина корзины по составу для учёта доли")
    ap.add_argument("--beta", type=float, default=0.0,
                    help="E6d: состав влияет на ВЫЖИВАНИЕ (распад), а не на рост: k_eff = k*(1 + beta*(s_ref - s))")
    ap.add_argument("--s-ref", type=float, default=1.0, help="опорный состав (дикий тип)")
    ap.add_argument("--mutation", type=float, default=0.05, help="sigma мутации состава при делении")
    ap.add_argument("--threshold", type=float, default=0.2)
    ap.add_argument("--thresholds", default="",
                    help="X26: список порогов через запятую (например 0.1,0.15,0.2,0.25,0.3) — "
                         "считать число компонент на каждом, чтобы отличить тело от перколяционного кластера")
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
    h_trait = None
    if args.trait_field:
        # X32: признак — поле, а не словарь. Стартует однородным; вариация появляется из шума в живых клетках.
        h_trait = torch.full_like(v, float(args.trait_init))
    v = torch.where(m, torch.full_like(v, 1.0), v)
    u = torch.where(m, torch.full_like(u, 0.25), u)

    rng = np.random.default_rng(int(args.seed))
    rng_g = np.random.default_rng(int(args.global_noise_seed) + 7919)
    buf = torch.zeros((g, g), device=dev)   # E12: память среды
    # E7: пространственный узор G (фиксирован) и временной сигнал S(t)
    hetero_G = None
    hetero_S = None
    if args.hetero_amp > 0:
        ky, kx = 2.0 * np.pi / max(2.0, args.hetero_scale), 2.0 * np.pi / max(2.0, args.hetero_scale)
        hetero_G = (np.sin(ky * np.arange(g))[:, None] * np.cos(kx * np.arange(g))[None, :] + 1.0) / 2.0
        if args.hetero_period and args.hetero_period > 0:
            # E9: прямоугольная смена 0/1 с заданным периодом — «зерно» среды
            hetero_S = [1.0 if (i // max(1, int(args.hetero_period))) % 2 == 0 else 0.0 for i in range(args.steps)]
        elif args.hetero_signal:
            raw = json.loads(Path(args.hetero_signal).read_text(encoding="utf-8")).get("values") or []
            hetero_S = list(raw)
            if args.hetero_shuffle and hetero_S:
                rng.shuffle(hetero_S)
        else:
            hetero_S = None  # узор выключен (S = 0.5)
    next_id = 1
    # состав: id компоненты → s
    comp_s: dict[int, float] = {}
    comp_flag: dict[int, bool] = {}
    threshold_list = [float(x) for x in str(args.thresholds).split(",") if x.strip()]
    threshold_counts: dict[str, list] = {}
    comp_uid: dict[int, int] = {}
    uid_counter = 0
    uid_first: dict[int, int] = {}
    uid_last: dict[int, int] = {}
    uid_peak: dict[int, int] = {}   # True = потомок подсеянного редкого типа
    _invade_pending = False
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
        if h_trait is not None:
            # X32: признак диффундирует медленно, возвращается к s_ref и мутирует ТОЛЬКО в живых клетках.
            # Тогда дочерняя структура получает признак из среды, а не присваиванием.
            h_trait = h_trait + args.dt * (
                args.trait_diffusion * laplacian(h_trait)
                - args.trait_decay * (h_trait - float(args.s_ref))
            )
            h_trait = h_trait + args.trait_mutation * torch.randn(
                h_trait.shape, generator=torch.Generator(device=dev).manual_seed(int(args.seed) + step),
                device=dev) * (v > float(args.threshold)).float()
            h_trait = torch.clamp(h_trait, 0.3, 2.5)
            # распад зависит от ЛОКАЛЬНОГО признака, а не от компоненты
            k_eff = args.k * torch.clamp(1.0 + args.beta * (args.s_ref - h_trait), 0.3, 2.5)
            mod_k = torch.ones_like(k_eff)

        F_eff = args.F * mod
        k_eff = args.k * mod_k if h_trait is None else k_eff
        if args.protect_fading > 0:
            # E12c: защита гаснущего через распад, а не через приток
            k_eff = k_eff * torch.clamp(1.0 - args.protect_fading * torch.clamp(1.0 - v, 0.0, 1.0), 0.3, 1.0)

        if args.global_noise_amp > 0:
            # X18: глобальный сигнал — один и тот же множитель на всё поле (нет пространственной структуры)
            gi = max(0, int(step * float(args.global_noise_rate)) - 1)
            s_g = float(rng_g.random())
            F_eff = F_eff * (1.0 + args.global_noise_amp * (2.0 * s_g - 1.0))

        if args.buffer_tau > 0:
            buf = buf + args.dt * (v - buf / float(args.buffer_tau))
            buf = torch.clamp(buf, 0.0, 5.0)
            if args.buffer_rescue:
                # E12b: подкормка гаснущего: (1 - v) высоко там, где материал исчез, а память осталась
                F_eff = F_eff * (1.0 + args.buffer_gain * buf * torch.clamp(1.0 - v, 0.0, 1.0))
            else:
                F_eff = F_eff * (1.0 + args.buffer_gain * buf)

        if hetero_G is not None and args.hetero_amp > 0:
            s_t = 0.5
            if hetero_S:
                idx = int(round((step - 1) / max(1, args.steps - 1) * (len(hetero_S) - 1)))
                s_t = float(hetero_S[max(0, min(len(hetero_S) - 1, idx))])
            g_t = torch.tensor(hetero_G, device=dev, dtype=torch.float32)
            spatial = (2.0 * g_t - 1.0) * (2.0 * s_t - 1.0)
            F_eff = F_eff * (1.0 + args.hetero_amp * spatial)

        uvv = u * v * v
        du = args.Du * laplacian(u) - uvv + F_eff * (1.0 - u)
        dv = args.Dv * laplacian(v) + uvv - (F_eff + k_eff) * v
        u = torch.clamp(u + args.dt * du, 0.0, 1.0)
        v = torch.clamp(v + args.dt * dv, 0.0, 1.0)

        # --- наблюдатель: компоненты и сопоставление ---
        vn = v.detach().cpu().numpy()
        mask = vn > float(args.threshold)
        lab, n_comp = label(mask)
        # X26: число компонент при разных порогах — перколяция даёт резкий скачок доли главной компоненты.
        # Считаем только на срезах: на каждом шаге это стоило бы 5 лишних разметок поля.
        if threshold_list and step % int(args.sample_every) == 0:
          for th in threshold_list:
            lab_th, n_th = label(vn > th)
            sizes_th = np.bincount(lab_th.ravel())[1:] if n_th else np.array([])
            biggest = int(sizes_th.max()) if len(sizes_th) else 0
            total = int(sizes_th.sum()) if len(sizes_th) else 0
            threshold_counts.setdefault(str(th), []).append(
                {"step": step, "n": n_th, "largest_share": round(biggest / total, 4) if total else None})

        if h_trait is not None:
            # признак компоненты — среднее поля по её клеткам (физическое чтение, а не словарь)
            h_np = h_trait.detach().cpu().numpy()
            comp_s = {cid: float(h_np[lab == cid].mean()) for cid in range(1, n_comp + 1)
                      if int((lab == cid).sum()) > 0}

        sizes = {cid: int((lab == cid).sum()) for cid in range(1, n_comp + 1)}
        keep = [cid for cid, sz in sizes.items() if sz >= args.min_cells]
        new_s: dict[int, float] = {}
        new_flag: dict[int, bool] = {}
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
                new_flag[cid] = comp_flag.get(parent, False)
            else:
                new_s[cid] = float(rng.normal(args.s_ref, args.mutation))
                new_flag[cid] = False
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
        if _invade_pending:
            cy_i, cx_i = g // 4, g // 4
            for cid in keep:
                if lab[cy_i, cx_i] == cid:
                    new_flag[cid] = True
                    new_s[cid] = float(args.invade_s)
                    _invade_pending = False
        # X23: устойчивый идентификатор компоненты (uid) — чтобы измерять ВРЕМЯ ЖИЗНИ, а не счётчик.
        # uid наследуется от родителя (перекрытие >= overlap), иначе компонента считается новой.
        new_uid: dict[int, int] = {}
        for cid in keep:
            cells = (lab == cid)
            parent = None
            if prev_lab is not None:
                cand = prev_lab[cells]
                if cand.size:
                    vals, counts = np.unique(cand[cand > 0], return_counts=True)
                    if len(vals):
                        best = int(vals[int(np.argmax(counts))])
                        if counts.max() / cells.sum() >= args.overlap and best in comp_uid:
                            parent = best
            if parent is not None:
                new_uid[cid] = comp_uid[parent]
            else:
                uid_counter += 1
                new_uid[cid] = uid_counter
            uid_first.setdefault(new_uid[cid], step)
            uid_last[new_uid[cid]] = step
            uid_peak[new_uid[cid]] = max(uid_peak.get(new_uid[cid], 0), int(cells.sum()))
        comp_uid = {cid: u for cid, u in new_uid.items()}

        comp_s = {cid: s_val for cid, s_val in new_s.items()}
        comp_flag = {cid: bool(new_flag.get(cid, False)) for cid in new_s}
        prev_lab = np.where(np.isin(lab, keep), lab, 0)

        # E11: подсев редкого типа отдельной каплей вдали от центра
        if args.invade_s is not None and step == int(args.invade_at):
            cy, cx = g // 4, g // 4
            rr = max(2.0, float(args.invade_radius))
            m_inv = ((xx - cx) ** 2 + (yy - cy) ** 2) <= rr * rr
            v = torch.where(m_inv, torch.full_like(v, 0.8), v)
            u = torch.where(m_inv, torch.full_like(u, 0.3), u)
            # новая компонента получит «дикий» состав; подменяем его на invade_s после ближайшего среза
            _invade_pending = True

        if step % int(args.sample_every) == 0 or step == 1:
            vals = list(comp_s.values())
            inv_area = 0
            for cid, flag in comp_flag.items():
                if flag:
                    inv_area += int((prev_lab == cid).sum())
            series.append({
                "step": step,
                "invader_area": inv_area,
                # X10: площади компонент — без них нельзя посчитать Hill q=1,2 (только счётчик q=0)
                "areas": sorted((int((prev_lab == cid).sum()) for cid in keep), reverse=True),
                "components": len(vals),
                "s_mean": round(float(np.mean(vals)), 4) if vals else 0.0,
                "s_sd_between": round(float(np.std(vals)), 4) if len(vals) > 1 else 0.0,
                "s_wild_fraction": round(float(np.mean([abs(s - args.s_ref) < 1e-9 for s in vals])), 4) if vals else 0.0,
                "occupied": round(float(mask.mean()), 4),
            })

    # E11: удельная скорость роста редкого типа по срезам после подсева
    inv_curve = [(r["step"], r.get("invader_area", 0)) for r in series
                 if args.invade_s is not None and r["step"] > int(args.invade_at)]
    inv_rate = None
    if len(inv_curve) >= 2 and inv_curve[0][1] > 0 and inv_curve[-1][1] > 0:
        dt = inv_curve[-1][0] - inv_curve[0][0]
        inv_rate = round((math.log(inv_curve[-1][1]) - math.log(inv_curve[0][1])) / max(1, dt), 5)

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
            "invader_rate": inv_rate,
            "invader_curve": inv_curve,
        },
        "buffer": {"protect_fading": args.protect_fading, "tau": args.buffer_tau, "gain": args.buffer_gain, "rescue": bool(args.buffer_rescue),
                   "mean_last": round(float(buf.mean()), 4)},
        "global_noise": {"amp": args.global_noise_amp, "rate": args.global_noise_rate},
        "heterogeneity": {
            "amp": args.hetero_amp,
            "scale": args.hetero_scale,
            "signal": args.hetero_signal,
            "shuffled": bool(args.hetero_shuffle),
            "components_last": series[-1]["components"] if series else 0,
        },
        "lifetimes": {
            "n_uids": len(uid_first),
            "median_life_steps": (sorted(uid_last[u] - uid_first[u] for u in uid_first)[len(uid_first) // 2]
                                  if uid_first else None),
            "life_steps": sorted(uid_last[u] - uid_first[u] for u in uid_first)[:2000],
            "peak_sizes": sorted(uid_peak.values(), reverse=True)[:2000],
        },
        "components_by_threshold": threshold_counts,
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
