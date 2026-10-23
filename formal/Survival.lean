/-
F-SURV — порог выживания и время смерти: математика, которая сужает перебор.

Зачем это нужно. Мы собирались подбирать «смертельную цену» перебором прогонов.
Но у модели есть точное решение: при доходе `i` и цене `c` энергия меняется на
`i - c` за шаг. Значит

  * клетка не голодает ровно тогда, когда `i ≥ c`;
  * если `i < c`, она умирает за `⌈E₀ / (c - i)⌉` шагов;
  * при равновесии число клеток ограничено бюджетом: `N · c ≤ I`.

Эти три факта заменяют перебор: они говорят, какие параметры вообще могут дать
смерти за десятки шагов, а какие — только за тысячи. Ниже — машинная проверка
арифметического ядра; в питоне те же формулы проверяются тестом `test_survival_math.py`.

Что опровергнет: если в симуляции клетка живёт при `i < c` дольше предсказанного
(или гибнет при `i ≥ c`), значит в модели есть скрытый приток/расход, которого нет
в этой арифметике — и его надо найти, а не подбирать.
-/

namespace Survival

/-- Один шаг: энергия после шага. -/
def step (energy income cost : Int) : Int := energy + income - cost

/-- Повтор шага `n` раз. -/
def run : Nat → Int → Int → Int → Int
  | 0, e, _, _ => e
  | n + 1, e, i, c => step (run n e i c) i c

/-- F-SURV-1: при доходе не меньше цены энергия не убывает. -/
theorem no_deficit_if_income_covers_cost
    (e i c : Int) (h : c ≤ i) : e ≤ step e i c := by
  unfold step
  omega

/-- F-SURV-2: при доходе меньше цены энергия строго убывает. -/
theorem deficit_if_cost_exceeds_income
    (e i c : Int) (h : i < c) : step e i c < e := by
  unfold step
  omega

/-- F-SURV-3: мёртвая клетка остаётся мёртвой, если доход не покрывает цену. -/
theorem dead_stays_dead
    (e i c : Int) (hdead : e ≤ 0) (hdef : i ≤ c) : step e i c ≤ 0 := by
  unfold step
  omega

/-- F-SURV-4: за один шаг энергия меняется ровно на `income - cost` (без деления). -/
theorem run_succ (n : Nat) (e i c : Int) :
    run (n + 1) e i c = run n e i c + i - c := by
  simp [run, step]

/-- F-SURV-5: если доход не покрывает цену, энергия не может вырасти ни за сколько шагов. -/
theorem never_grows_under_deficit
    (n : Nat) (e i c : Int) (h : i ≤ c) : run n e i c ≤ e := by
  induction n with
  | zero => simp [run]
  | succ k ih =>
    rw [run_succ]
    unfold step at ih
    omega

/-- F-SURV-6: порог выживания в долях бюджета: при равновесии суммарные траты
    не превышают суммарного дохода (`cells * cost ≤ budget`). -/
theorem equilibrium_within_budget
    (cells cost budget : Nat) (hc : 0 < cost) : cells * cost ≤ budget → cells ≤ budget / cost := by
  intro h
  exact Nat.le_div_iff_mul_le hc |>.mpr h

end Survival
