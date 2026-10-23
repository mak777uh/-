/-
Формальная гипотеза F-ORDER-1: бюджет сохраняется при ЛЮБОМ порядке асинхронных
обновлений.

Почему это важно проекту: GPU обновляет клетки параллельно, CPU — последовательно,
и порядок может отличаться. Если бюджет (ресурс + энергия) сохраняется только при
одном порядке, значит на другом стеке энергия может «напечататься», и выводы о
выживании станут стек-зависимыми. Здесь доказано: сумма сохраняется для любой
последовательности обновлений, в любом порядке, с любыми нормами притока.

Модель: две клетки (`Bool` как индекс), планировщик — список пар «клетка, норма».
-/

structure World where
  resource : Int
  energy : Int

/-- Шаг бюджета одной клетки. -/
def stepCell (w : World) (rate : Int) : World :=
  let income := if w.resource ≤ rate then w.resource else rate
  { resource := w.resource - income, energy := w.energy + income }

/-- F-BUDGET-1: one-step conservation (переиспользуется ниже). -/
theorem cell_conserved (w : World) (rate : Int) :
    (stepCell w rate).resource + (stepCell w rate).energy = w.resource + w.energy := by
  unfold stepCell
  split <;> simp <;> omega

/-- Мир из двух клеток. -/
def Two := Bool → World

/-- Обновить одну клетку, не трогая другую. -/
def update (cells : Two) (i : Bool) (rate : Int) : Two :=
  fun j => if j = i then stepCell (cells j) rate else cells j

/-- Суммарный бюджет двух клеток. -/
def total (cells : Two) : Int :=
  (cells false).resource + (cells false).energy + (cells true).resource + (cells true).energy

/-- Один шаг планировщика сохраняет суммарный бюджет. -/
theorem update_conserved (cells : Two) (i : Bool) (rate : Int) :
    total (update cells i rate) = total cells := by
  unfold total update
  cases i
  · simp
    exact cell_conserved (cells false) rate
  · simp
    have h := cell_conserved (cells true) rate
    omega

/-- Прогон по расписанию: список пар «клетка, норма притока». -/
def runSched (cells : Two) : List (Bool × Int) → Two
  | [] => cells
  | (i, r) :: rest => runSched (update cells i r) rest

/-- F-ORDER-1: для любого расписания суммарный бюджет не меняется. -/
theorem sched_conserved (cells : Two) (sched : List (Bool × Int)) :
    total (runSched cells sched) = total cells := by
  induction sched generalizing cells with
  | nil => rfl
  | cons p rest ih =>
    cases p with
    | mk i r =>
      simp only [runSched]
      rw [ih]
      exact update_conserved cells i r

/-- Следствие: порядок в расписании не важен — оба порядка дают один и тот же бюджет. -/
theorem order_independent (cells : Two) (a b : Bool) (ra rb : Int) :
    total (runSched cells [(a, ra), (b, rb)]) = total (runSched cells [(b, rb), (a, ra)]) := by
  rw [sched_conserved, sched_conserved]
