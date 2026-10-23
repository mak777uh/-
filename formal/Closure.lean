/-
Формальная гипотеза F-CLOSURE-1: без притока энергия исчерпывается за конечное
число шагов.

Откуда пришла (цикл «библиотека → Lean»): F12 (регуляция как вывод о своём месте,
Friston/Levin) говорит, что регуляция — это минимизация расхождения между
предсказанием и сигналом; но чтобы регулировать, нужно быть живым. Наш
эмпирический результат по мембране: без производства ограничения приток
прекращается, и тело гибнет за 133 шага. Здесь фиксируется арифметическая суть
этого результата: при нулевом притоке энергия убывает линейно, поэтому для любого
начального запаса найдётся длина, после которой она неположительна.

Модель: цена шага = 1 (произвольная цена масштабируется — это отмечено в тексте
теоремы, а не спрятано).
-/

structure Cell where
  energy : Int

/-- Шаг без притока: энергия падает на единицу (цена). -/
def stepNoIncome (c : Cell) : Cell :=
  { energy := c.energy - 1 }

/-- Прогон n шагов без притока. -/
def runNoIncome (c : Cell) : Nat → Cell
  | 0 => c
  | n + 1 => runNoIncome (stepNoIncome c) n

/-- Энергия после n шагов равна начальной минус n. -/
theorem energy_after_no_income (c : Cell) (n : Nat) :
    (runNoIncome c n).energy = c.energy - (n : Int) := by
  induction n generalizing c with
  | zero => simp [runNoIncome]
  | succ n ih =>
      simp only [runNoIncome]
      rw [ih (stepNoIncome c)]
      simp [stepNoIncome]
      omega

/-- F-CLOSURE-1: если шагов не меньше начального запаса, энергия исчерпана. -/
theorem dies_if_long_enough (c : Cell) (n : Nat) (h : c.energy ≤ (n : Int)) :
    (runNoIncome c n).energy ≤ 0 := by
  rw [energy_after_no_income]
  omega

/-- Следствие: для любого запаса существует длина, на которой тело гибнет. -/
theorem death_time_exists (c : Cell) :
    ∃ n : Nat, (runNoIncome c n).energy ≤ 0 := by
  refine ⟨c.energy.toNat + 1, ?_⟩
  rw [energy_after_no_income]
  omega
