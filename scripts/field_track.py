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
    # X96 (owner-approved 02.11): третье поле w — медленный ингибитор со СВОЕЙ длиной диффузии. Это новое правило мира, а
    # не параметр, поэтому по умолчанию выключено: без флага уравнения бит-в-бит прежние, и якорь проверяется по
    # закоммиченному артефакту x100_f030_s291.json, а не по свежему прогону.
    ap.add_argument("--second-species", action="store_true",
                    help="X96: включить третье поле w: uvv/(1+gamma*w), dw/dt = Dw*lap(w) + beta_w*(v - w)")
    ap.add_argument("--Dw", type=float, default=0.32, help="X96: коэффициент диффузии w (по умолчанию 4*Dv)")
    ap.add_argument("--gamma", type=float, default=1.0, help="X96: сила ослабления автокатализа третьим полем")
    ap.add_argument("--beta-w", type=float, default=0.05, help="X96: скорость релаксации w к v")
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
    ap.add_argument("--trait-mutation-local", action="store_true",
                    help="X34: шум только там, где геометрия напряжена (|∇²v| велик, то есть у мест пережима). "
                         "Тогда сёстры расходятся, и отбор получает материал")
    ap.add_argument("--trait-init", type=float, default=1.0, help="X32: стартовое значение признака")
    # X45: канал внешнего — поле-подсказка, которое НЕ потребляется, предсказывает будущее и не является
    # следствием организма. При `off` поведение обязано остаться бит-в-бит (якорь).
    ap.add_argument("--cue-mode", choices=["off", "moving", "static", "shuffled"], default="off",
                    help="X45: поле-подсказка. moving — полоса едет с постоянной скоростью (предсказуемо); "
                         "static — стоит; shuffled — положение случайно каждый срез (связи с будущим нет)")
    ap.add_argument("--cue-speed", type=float, default=1.0, help="X45: скорость полосы, клеток за срез")
    ap.add_argument("--cue-width", type=float, default=6.0, help="X45: полушырина полосы, клеток")
    ap.add_argument("--cue-gamma", type=float, default=0.0,
                    help="X45: сила влияния подсказки на распад: k_eff *= (1 + gamma*c)")
    ap.add_argument("--cue-kappa", type=float, default=0.0,
                    help="X45: сила влияния подсказки на признак: h += kappa*c (только при trait-field)")
    ap.add_argument("--cue-period", type=int, default=0,
                    help="X49: период импульсных событий в шагах (0 = не импульсы). Событие = вспышка k-модуляции")
    ap.add_argument("--cue-skip-from", type=int, default=-1,
                    help="X49: с этого шага импульсы в окне [from, to) ПРОПУСКАЮТСЯ (дизайн Саигусы)")
    ap.add_argument("--cue-skip-to", type=int, default=-1,
                    help="X49: до этого шага импульсы пропускаются")
    ap.add_argument("--cue-memory-tau", type=float, default=0.0,
                    help="X48: медленная переменная-память m(x,y), интегрирующая поле события: "
                         "m += (1/tau)*(c - m). Распад зависит от m, а не от мгновенного c. 0 = памяти нет")
    ap.add_argument("--cue-kappa-local", action="store_true",
                    help="X47: сенсор действует только у границы (где |∇²v| велик), а не по всему полю — "
                         "иначе подсказка сдвигает признак везде одинаково и мир схлопывается (§10dp)")
    ap.add_argument("--cue-seed", type=int, default=0, help="X45: сид для режима shuffled")
    ap.add_argument("--cue-lead", type=int, default=0,
                    help="X46: на сколько шагов подсказка ОПЕРЕЖАЕТ событие. 0 = подсказка и есть событие "
                         "(тогда предвосхищать нечего, см. §10dp-доп)")
    ap.add_argument("--hetero-amp", type=float, default=0.0,
                    help="E7: сила пространственной неоднородности притока: F(x,y) = F*(1 + amp*(2S(t)-1)*(2G(x,y)-1))")
    ap.add_argument("--hetero-scale", type=float, default=12.0, help="масштаб пространственного узора G (клеток)")
    # X78b: составной узор — две длины волны в одном G. По умолчанию выключено, поэтому старая ветка бит-в-бит прежняя.
    ap.add_argument("--hetero-scale2", type=float, default=0.0,
                    help="X78b: вторая длина волны узора G (0 = выключено)")
    ap.add_argument("--hetero-mix2", type=float, default=0.5,
                    help="X78b: вес второй длины волны в составном узоре (0..1)")
    # X81: предписанный спектр вместо смеси двух узоров. По умолчанию выключено (None), поэтому старая ветка бит-в-бит прежняя.
    ap.add_argument("--spectrum-share", type=float, default=None,
                    help="X81: предписанное отношение МОЩНОСТИ второго пика к первому (0 = одна шкала, 1 = равные мощности); "
                         "фазы тянутся из отдельного генератора, при 0 фазы нулевые и узор совпадает со старым")
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
    # X70: при делении давать дочерям СВОИ идентичности, иначе пики родителя и дочери неразделимы
    # и «наследование размера» измерить нельзя — обе записи несут один uid.
    ap.add_argument("--split-new-uid", action="store_true",
                    help="X70: при расщеплении выдавать дочерям новые uid и писать пары (родитель, дочь)")
    ap.add_argument("--sample-every", type=int, default=1000)
    ap.add_argument("--out", default=None)
    # X60: сохранить само поле, а не только счётчики. Без этого нельзя посчитать β0/β1,
    # спектр и длину волны, а значит нельзя ни нормировать число на λ², ни определить
    # время жизни персистентностью вместо правила перекрытия. Флаг не трогает ГПСЧ.
    ap.add_argument("--save-fields", default=None,
                    help="X60: каталог, куда писать v на выбранных срезах (.npy, float32)")
    ap.add_argument("--init-jitter", action="store_true",
                    help="X70r: сдвинуть стартовую каплю по сиду (реплика нейтрального мира; выключено = прежнее поведение)")
    ap.add_argument("--init-spots", default="", help="X134: два диска радиуса R на расстоянии SEP клеток; формат R:SEP")
    # X96b: вторая шкала в начальном условии вместо притока. По умолчанию выключено (0), поэтому старая ветка бит-в-бит прежняя.
    ap.add_argument("--init-pattern-cells", type=float, default=0.0,
                    help="X96b: длина волны стартового узора в клетках (0 = выключено, старт с одной капли)")
    ap.add_argument("--init-pattern-fill", type=float, default=0.5,
                    help="X96b: амплитуда стартового узора (0..1): v += fill*pattern, u -= 0.75*fill*pattern")
    ap.add_argument("--init-pattern-binary", action="store_true",
                    help="X96b: бинаризовать узор (полосы 0/1) вместо гладкой синусоиды")
    # X100: писать поле на каждом N-м логируемом шаге (0 = выключено). Нужно для размера без среза.
    ap.add_argument("--save-fields-every", type=int, default=0,
                    help="X100: сохранять поле на каждом N-м логируемом шаге (0 = только --save-fields-at)")
    ap.add_argument("--save-fields-at", default="2000,4000,6000",
                    help="X60: шаги, на которых сохраняется поле (по умолчанию 2000,4000,6000)")
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
    # X70r: в нейтральном мире (beta=0, eps=0) геометрия ОТ СИДА НЕ ЗАВИСИТ: стартовая капля фиксирована, а сид
    # достаётся только каналу признака, который ни на что не влияет. Пять «сидов» тогда — одна и та же вселенная.
    # Флаг сдвигает и слегка меняет размер запала по сиду: это реплика нейтрального мира, а не новый мир.
    # С выключенным флагом ветка не исполняется — якорь остаётся бит-в-бит.
    if args.init_jitter:
        _jr = np.random.default_rng(int(args.seed) + 6067)
        _dx, _dy = (int(x) for x in _jr.integers(-g // 4, g // 4 + 1, size=2))
        _r = float(r0) * float(_jr.uniform(0.8, 1.2))
        c = ((g // 2 + _dx) % g, (g // 2 + _dy) % g)
        r0 = max(2.0, _r)
        m = ((((xx - c[0] + g // 2) % g) - g // 2) ** 2 + (((yy - c[1] + g // 2) % g) - g // 2) ** 2) <= r0 * r0
    else:
        m = ((xx - c) ** 2 + (yy - c) ** 2) <= r0 * r0
    h_trait = None
    mem_t = None   # X48: медленная память о ходе события
    cue_pos = 0.0
    cue_rng = np.random.default_rng(int(args.cue_seed) + 4241)

    def cue_field(shape, g, step_i):
        """Полоса-подсказка: 1 в полосе, 0 вне. Не потребляется, в реакциях не участвует."""
        nonlocal cue_pos
        if args.cue_mode == "off":
            return None
        if args.cue_mode == "moving":
            pos = (float(args.cue_speed) * step_i) % g
            centre = pos
        elif args.cue_mode == "static":
            # X45: полоса НЕ на затравке (затравка в центре) — иначе мир гибнет в первый шаг и контроль невалиден
            centre = g / 4.0
        else:  # shuffled: положение случайно каждый срез, связи с будущим нет
            centre = float(cue_rng.uniform(0, g))
        xs = np.arange(g, dtype=float)
        d = np.abs(((xs - centre + g / 2) % g) - g / 2)   # тороидальное расстояние
        prof = np.exp(-0.5 * (d / max(1e-6, float(args.cue_width))) ** 2)
        return np.tile(prof, (g, 1))

    if args.trait_field:
        # X32: признак — поле, а не словарь. Стартует однородным; вариация появляется из шума в живых клетках.
        h_trait = torch.full_like(v, float(args.trait_init))
    v = torch.where(m, torch.full_like(v, 1.0), v)
    u = torch.where(m, torch.full_like(u, 0.25), u)

    # X134: интервенция вместо наблюдения за расколом — два диска на заданном расстоянии и ничего больше.
    # По умолчанию флага нет, ветка не исполняется, старая инициализация остаётся бит-в-бит (якорь).
    if args.init_spots:
        try:
            _rs, _ss = str(args.init_spots).split(":")
            _rad, _sep = float(_rs), float(_ss)
        except ValueError:
            raise SystemExit("--init-spots expects R:SEP, e.g. 3:12")
        v = torch.zeros_like(v)
        u = torch.ones_like(u)
        _yses = ((yy - g / 2.0 + g / 2) % g) - g / 2
        _disc = torch.zeros((g, g), device=dev)
        for _off in (-_sep / 2.0, _sep / 2.0):
            _xses = ((xx - (g / 2.0 + _off) + g / 2) % g) - g / 2
            _disc = torch.maximum(_disc, ((_yses ** 2 + _xses ** 2) <= _rad * _rad).to(_disc.dtype))
        v = torch.clamp(v + _disc, 0.0, 1.0)
        u = torch.clamp(u - 0.75 * _disc, 0.0, 1.0)

    # X96b: вторая шкала не в притоке, а в НАЧАЛЬНОМ УСЛОВИИ. Приток задаёт узор непрерывно, и среда его игнорирует
    # (X82: до 16x мощности период не двигается). Здесь вместо одной капли поле стартует синусоидой заданной длины,
    # и вопрос ставится иначе: удержится ли навязанная шкала, если она — единственное, что есть в t = 0.
    # Выключено по умолчанию, поэтому старая ветка бит-в-бит прежняя.
    if args.init_pattern_cells > 0:
        q0 = float(g) / max(2.0, float(args.init_pattern_cells))
        phase = np.random.default_rng(int(args.seed) * 7919 + 11).uniform(0.0, 2.0 * np.pi, size=2)
        y0 = np.arange(g)[:, None]
        x0 = np.arange(g)[None, :]
        pat = np.sin(2.0 * np.pi * q0 * y0 / g + phase[0]) * np.sin(2.0 * np.pi * q0 * x0 / g + phase[1])
        pat = (pat > 0.0).astype(np.float32) if args.init_pattern_binary else pat.astype(np.float32)
        pat_t = torch.tensor(pat, device=dev, dtype=torch.float32)
        fill = float(np.clip(args.init_pattern_fill, 0.0, 1.0))
        v = torch.clamp(v + fill * pat_t, 0.0, 1.0)
        u = torch.clamp(u - 0.75 * fill * pat_t, 0.0, 1.0)

    rng = np.random.default_rng(int(args.seed))
    rng_g = np.random.default_rng(int(args.global_noise_seed) + 7919)
    buf = torch.zeros((g, g), device=dev)   # E12: память среды
    # X96: третье поле стартует равным v, чтобы на первом шаге не было импульса от разности (v - w). При выключенном флаге
    # переменной нет вовсе, поэтому старая ветка не меняется ни на бит.
    w = v.clone() if args.second_species else None
    # E7: пространственный узор G (фиксирован) и временной сигнал S(t)
    hetero_G = None
    hetero_S = None
    if args.hetero_amp > 0:
        ky, kx = 2.0 * np.pi / max(2.0, args.hetero_scale), 2.0 * np.pi / max(2.0, args.hetero_scale)
        hetero_G = (np.sin(ky * np.arange(g))[:, None] * np.cos(kx * np.arange(g))[None, :] + 1.0) / 2.0
        if args.spectrum_share is not None:
            # X81: prescribe the spectrum instead of mixing two patterns. The dominant peak stays at `--hetero-scale`
            # (q = g/scale), the second sits at `--hetero-scale2`, and `--spectrum-share` is the prescribed POWER ratio of
            # the second peak to the first (0 = single scale, 1 = equal power). Phases are drawn per world from a private
            # generator, so seeds realise distinct worlds and the main RNG stream is untouched; at share = 0 the phases are
            # zero and the pattern is the old single-scale one bit-for-bit (anchor on the flags-off path).
            q1, q2 = float(g) / max(2.0, args.hetero_scale), float(g) / max(2.0, args.hetero_scale2)
            share = max(0.0, float(args.spectrum_share))
            rng_phase = np.random.default_rng(int(args.seed) * 1000003 + 17)
            if share > 0:
                ph1 = rng_phase.uniform(0.0, 2.0 * np.pi, size=2)
                ph2 = rng_phase.uniform(0.0, 2.0 * np.pi, size=2)
            else:
                ph1 = np.zeros(2)
                ph2 = np.zeros(2)
            y = np.arange(g)[:, None]
            x = np.arange(g)[None, :]
            wave1 = np.sin(2.0 * np.pi * q1 * y / g + ph1[0]) * np.cos(2.0 * np.pi * q1 * x / g + ph1[1])
            wave2 = np.sin(2.0 * np.pi * q2 * y / g + ph2[0]) * np.cos(2.0 * np.pi * q2 * x / g + ph2[1])
            # a product of two unit waves has std 1/2, so power is proportional to the squared amplitude of the wave
            amp2 = share ** 0.5
            G = wave1 + amp2 * wave2
            # same amplitude normalisation as the composite path: equal modulation strength in every cell
            _sigma1 = float(hetero_G.std()) or 1.0
            _sd = float(G.std())
            if _sd > 0:
                G = (G - float(G.mean())) / _sd * _sigma1 + 0.5
            hetero_G = np.clip(G, 0.0, 1.0)
        elif args.hetero_scale2 and args.hetero_scale2 > 0:
            # X78b: вторая шкала складывается с первой в один узор; обе нормированы в [0,1], вес задаёт смесь.
            ky2, kx2 = 2.0 * np.pi / max(2.0, args.hetero_scale2), 2.0 * np.pi / max(2.0, args.hetero_scale2)
            G2 = (np.sin(ky2 * np.arange(g))[:, None] * np.cos(kx2 * np.arange(g))[None, :] + 1.0) / 2.0
            w2 = min(1.0, max(0.0, float(args.hetero_mix2)))
            # X79: смесь двух независимых узоров имеет дисперсию (1-w)^2 + w^2, то есть МИНИМУМ при w = 0.5 — вес и амплитуда
            # двигались вместе, и развёртка по весу мерила две вещи сразу. Нормируем смесь к амплитуде одиночного узора:
            # теперь любой вес даёт одинаковую силу модуляции, и меняется только спектральный состав.
            _sigma1 = float(hetero_G.std()) or 1.0
            hetero_G = (1.0 - w2) * hetero_G + w2 * G2
            _sd = float(hetero_G.std())
            if _sd > 0:
                hetero_G = (hetero_G - float(hetero_G.mean())) / _sd * _sigma1 + 0.5
            hetero_G = np.clip(hetero_G, 0.0, 1.0)
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
    uid_peak: dict[int, int] = {}
    uid_s_birth: dict[int, float] = {}   # True = потомок подсеянного редкого типа
    _invade_pending = False
    prev_lab = None
    pairs: list[tuple[float, float]] = []   # (s родителя, s дочери)
    # X70: пары (площадь родителя, площадь дочери) на момент деления — чтобы мерить
    # наследование РАЗМЕРА, а не навязанного состава. Логгер, ГПСЧ не трогает.
    size_pairs: list[tuple[int, int]] = []
    uid_pairs: list[tuple[int, int]] = []   # (uid родителя, uid дочери) при --split-new-uid
    splits = 0
    series = []
    _save_at = {int(x) for x in str(args.save_fields_at).split(",") if x.strip()}
    fields_saved: list[str] = []

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
        # X46: событие действует СЕЙЧАС, подсказка показывает, где оно будет через `lead` шагов.
        # При lead = 0 оба поля совпадают и поведение прежнее (якорь).
        pulse_on = True
        if args.cue_period > 0:
            # X49: импульс в начале каждого периода; ширина импульса — cue_width шагов
            phase = step % int(args.cue_period)
            pulse_on = phase < max(1, int(args.cue_width))
            if args.cue_skip_from >= 0 and args.cue_skip_to > args.cue_skip_from:
                if int(args.cue_skip_from) <= step < int(args.cue_skip_to):
                    pulse_on = False
        effect_np = cue_field((g, g), g, step) if pulse_on else None
        cue_np = cue_field((g, g), g, step + int(args.cue_lead)) if args.cue_lead else effect_np
        cue_t = torch.tensor(effect_np, device=dev, dtype=torch.float32) if effect_np is not None else None
        # X48: память о прошлом ходе события. Обновляется ДО применения к распаду, поэтому в момент t
        # распад видит смесь прошлых положений полосы (а не текущее).
        cue_lead_t = (torch.tensor(cue_np, device=dev, dtype=torch.float32)
                      if (cue_np is not None and args.cue_lead) else None)
        # X48: память интегрирует ОПЕРЕЖАЮЩУЮ подсказку (то, что сообщает о будущем), а не текущее событие.
        # Иначе опережение снова окажется не подключено к динамике — та же ошибка, что в X46.
        mem_src = cue_lead_t if cue_lead_t is not None else cue_t
        if args.cue_memory_tau > 0 and mem_src is not None:
            if mem_t is None:
                mem_t = mem_src.clone()
            else:
                mem_t = mem_t + (1.0 / float(args.cue_memory_tau)) * (mem_src - mem_t)
        cue_decay_t = mem_t if (args.cue_memory_tau > 0 and mem_t is not None) else cue_t

        if h_trait is not None:
            # X32: признак диффундирует медленно, возвращается к s_ref и мутирует ТОЛЬКО в живых клетках.
            # Тогда дочерняя структура получает признак из среды, а не присваиванием.
            h_trait = h_trait + args.dt * (
                args.trait_diffusion * laplacian(h_trait)
                - args.trait_decay * (h_trait - float(args.s_ref))
            )
            noise = torch.randn(
                h_trait.shape, generator=torch.Generator(device=dev).manual_seed(int(args.seed) + step),
                device=dev)
            if args.trait_mutation_local:
                # X34: мутация там, где геометрия напряжена — у пережимов, где и происходит деление.
                # |∇²v| максимален на границе и в шейках; нормируем на 95-й процентиль, чтобы шум не взрывался.
                curv = torch.abs(laplacian(v))
                scale = float(torch.quantile(curv.flatten(), 0.95)) if float(curv.max()) > 0 else 1.0
                weight = torch.clamp(curv / max(scale, 1e-6), 0.0, 2.0)
                h_trait = h_trait + args.trait_mutation * noise * weight
            else:
                h_trait = h_trait + args.trait_mutation * noise * (v > float(args.threshold)).float()
            if cue_lead_t is not None and args.cue_kappa != 0.0:
                # X46: признак двигается по ПОДСКАЗКЕ (опережающей), а распад — по событию (текущему).
                # X47: при `--cue-kappa-local` связь действует только там, где геометрия напряжена (у границы).
                if args.cue_kappa_local:
                    curv_h = torch.abs(laplacian(v))
                    scale_h = float(torch.quantile(curv_h.flatten(), 0.95)) if float(curv_h.max()) > 0 else 1.0
                    w_h = torch.clamp(curv_h / max(scale_h, 1e-6), 0.0, 2.0)
                    h_trait = h_trait + args.cue_kappa * cue_lead_t * w_h
                else:
                    h_trait = h_trait + args.cue_kappa * cue_lead_t * (v > float(args.threshold)).float()
            if cue_t is not None and args.cue_kappa != 0.0:
                # X45: подсказка двигает признак в живых клетках; она НЕ расходуется и не даёт энергии
                h_trait = h_trait + args.cue_kappa * cue_t * (v > float(args.threshold)).float()
            h_trait = torch.clamp(h_trait, 0.3, 2.5)
            # распад зависит от ЛОКАЛЬНОГО признака, а не от компоненты
            k_eff = args.k * torch.clamp(1.0 + args.beta * (args.s_ref - h_trait), 0.3, 2.5)
            if cue_t is not None and args.cue_gamma != 0.0:
                k_eff = k_eff * (1.0 + args.cue_gamma * cue_decay_t)
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
        if args.second_species:
            # X96: медленное поле гасит автокатализ пропорционально своей амплитуде; длина волны задаётся отношением
            # длин диффузии Dv и Dw. Порядок явный: w обновляется по СТАРОМУ v, как и остальные уравнения.
            uvv = uvv / (1.0 + float(args.gamma) * w)
        du = args.Du * laplacian(u) - uvv + F_eff * (1.0 - u)
        dv = args.Dv * laplacian(v) + uvv - (F_eff + k_eff) * v
        u = torch.clamp(u + args.dt * du, 0.0, 1.0)
        v = torch.clamp(v + args.dt * dv, 0.0, 1.0)
        if args.second_species:
            dw = args.Dw * laplacian(w) + args.beta_w * (v - w)
            w = torch.clamp(w + args.dt * dw, 0.0, 1.0)

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
        split_children: set[int] = set()   # X70: cid, которым при этом шаге достаётся новая идентичность
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
                            size_pairs.append((int(sizes.get(parent, 0)), int(sizes.get(cid, 0))))
                            split_children.add(cid)
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
            if parent is not None and args.split_new_uid and cid in split_children:
                # X70: дочь получает собственную идентичность, иначе её пик неотделим от пикового
                # значения родителя и «наследование размера» измерить невозможно
                uid_counter += 1
                new_uid[cid] = uid_counter
                uid_pairs.append((comp_uid.get(parent, 0), uid_counter))
            elif parent is not None:
                new_uid[cid] = comp_uid[parent]
            else:
                uid_counter += 1
                new_uid[cid] = uid_counter
            uid_first.setdefault(new_uid[cid], step)
            if new_uid[cid] not in uid_s_birth and cid in comp_s:
                uid_s_birth[new_uid[cid]] = round(float(comp_s[cid]), 4)
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
                # X37/X39: журнал компонент по срезам — uid, признак, площадь.
                # Без него нельзя ни дифференциал отбора по выжившим (X37), ни активность по типам (X39).
                "event_centre": (float(np.argmax(effect_np[0])) if effect_np is not None else None),
                "pulse_on": bool(pulse_on),   # X49: было ли событие в этом шаге (не зависит от положения среза)
                "cue_centre": (float(np.argmax(cue_np[0])) if cue_np is not None else None),
                "components_log": [
                    {"uid": comp_uid.get(cid), "s": round(float(comp_s[cid]), 4) if cid in comp_s else None,
                     "area": int((prev_lab == cid).sum()),
                     # X45: центроид нужен, чтобы считать, где признак относительно полосы-подсказки
                     "cx": round(float(np.argwhere(prev_lab == cid)[:, 1].mean()), 2),
                     "cy": round(float(np.argwhere(prev_lab == cid)[:, 0].mean()), 2)}
                    for cid in keep if cid in comp_s
                ],
            })
            # X60: поле пишется ПОСЛЕ записи среза и не меняет ни порядок, ни ГПСЧ —
            # иначе якорь (сравнение series с прежним прогоном) не сойдётся.
            # X100: --save-fields-every N пишет поле на каждом N-м логируемом шаге, а не только в перечисленных.
            # Выключено по умолчанию (0), поэтому старая ветка бит-в-бит прежняя.
            if args.save_fields and (step in _save_at or (args.save_fields_every and step % int(args.save_fields_every) == 0)):
                _dir = Path(args.save_fields)
                _dir.mkdir(parents=True, exist_ok=True)
                _tag = Path(args.out).stem if args.out else f"seed{args.seed}"
                _path = _dir / f"{_tag}_t{step}.npy"
                np.save(_path, v.detach().to("cpu").numpy().astype("float32"))
                fields_saved.append(str(_path).replace("\\", "/"))

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
        # X70: сырые пары размеров, чтобы наследование размера считалось без правила копирования
        "size_pairs": size_pairs,
        "uid_pairs": uid_pairs,
        "fields_saved": fields_saved,   # X60: пути .npy, если --save-fields
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
        "uid_outcomes": [
            {"uid": u, "first": uid_first[u], "last": uid_last[u], "peak": uid_peak.get(u, 0),
             "s_at_birth": uid_s_birth.get(u)}
            for u in sorted(uid_first)
        ],
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
