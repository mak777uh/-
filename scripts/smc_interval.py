"""smc_interval.py — интервалы вместо счёта «N из M».

Почему. Мы пишем «10 из 10 сидов» или «17 из 20», а это не утверждение о вероятности: у счёта нет
погрешности. Идея взята из статистической проверки моделей (SMC), где свойство формулируется как
`P(успех) ≥ p` с уверенностью `1 − α`, а не как «все прогоны прошли».

Две оценки доли (обе двусторонние, 95 % по умолчанию):
  * Клоппер–Пирсон (`exact`) — точный интервал по биномиальному распределению;
  * Уилсон (`wilson`) — приближённый, устойчив при малых n.

Использование:
    python scripts/smc_interval.py 10 10
    python scripts/smc_interval.py 17 20 --level 0.95
    python scripts/smc_interval.py 3 7 --format json
"""
from __future__ import annotations

import argparse
import json
import math


def _norm_ppf(p: float) -> float:
    """Обратная функция стандартного нормального распределения (Acklam, точность ~1e-9)."""
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
                ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    q = p - 0.5
    r = q * q
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / \
           (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)


def _beta_cdf(x: float, a: float, b: float) -> float:
    """Регуляризованная неполная бета-функция (продолженная дробь, Numerical Recipes)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    front = math.exp(math.log(x) * a + math.log(1 - x) * b + lbeta)

    def cf(a_: float, b_: float, x_: float) -> float:
        tiny = 1e-30
        qab, qap, qam = a_ + b_, a_ + 1.0, a_ - 1.0
        c, d = 1.0, 1.0 - qab * x_ / qap
        d = tiny if abs(d) < tiny else d
        d = 1.0 / d
        h = d
        for m in range(1, 300):
            m2 = 2 * m
            aa = m * (b_ - m) * x_ / ((qam + m2) * (a_ + m2))
            d = 1.0 + aa * d
            d = tiny if abs(d) < tiny else d
            c = 1.0 + aa / c
            c = tiny if abs(c) < tiny else c
            d = 1.0 / d
            h *= d * c
            aa = -(a_ + m) * (qab + m) * x_ / ((a_ + m2) * (qap + m2))
            d = 1.0 + aa * d
            d = tiny if abs(d) < tiny else d
            c = 1.0 + aa / c
            c = tiny if abs(c) < tiny else c
            d = 1.0 / d
            delta = d * c
            h *= delta
            if abs(delta - 1.0) < 1e-12:
                break
        return h

    if x < (a + 1.0) / (a + b + 2.0):
        return front * cf(a, b, x) / a
    return 1.0 - front * cf(b, a, 1.0 - x) / b


def _beta_ppf(p: float, a: float, b: float) -> float:
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if _beta_cdf(mid, a, b) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def clopper_pearson(k: int, n: int, level: float = 0.95) -> tuple[float, float]:
    alpha = 1.0 - level
    lo = 0.0 if k == 0 else _beta_ppf(alpha / 2, k, n - k + 1)
    hi = 1.0 if k == n else _beta_ppf(1 - alpha / 2, k + 1, n - k)
    return lo, hi


def wilson(k: int, n: int, level: float = 0.95) -> tuple[float, float]:
    if n == 0:
        return 0.0, 1.0
    z = _norm_ppf(1 - (1 - level) / 2)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("k", type=int, help="число успехов")
    ap.add_argument("n", type=int, help="число испытаний")
    ap.add_argument("--level", type=float, default=0.95)
    ap.add_argument("--format", default="text", choices=["text", "json"])
    args = ap.parse_args(argv)
    if not (0 <= args.k <= args.n) or args.n == 0:
        print(f"[smc] некорректно: k={args.k}, n={args.n}")
        return 1
    cp = clopper_pearson(args.k, args.n, args.level)
    wl = wilson(args.k, args.n, args.level)
    out = {
        "k": args.k, "n": args.n, "level": args.level,
        "share": args.k / args.n,
        "clopper_pearson": {"low": round(cp[0], 4), "high": round(cp[1], 4)},
        "wilson": {"low": round(wl[0], 4), "high": round(wl[1], 4)},
        "statement": (f"{args.k} из {args.n} ⇒ доля {args.k/args.n:.3f}, "
                      f"{int(args.level*100)} % ДИ [{cp[0]:.3f}, {cp[1]:.3f}] (Клоппер–Пирсон)"),
    }
    if args.format == "json":
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(f"[smc] {out['statement']}")
        print(f"      Уилсон: [{wl[0]:.3f}, {wl[1]:.3f}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
