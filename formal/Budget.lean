/-
Формальные гипотезы о бюджете среды «пруд».

F-BUDGET-1 (один шаг): сумма «ресурс + энергия» сохраняется, ресурс не уходит в
минус, мёртвое поле остаётся мёртвым.

F-BUDGET-2 (любая последовательность): сумма сохраняется для любой
последовательности шагов, в том числе враждебной — доказано индукцией по списку
норм притока.

F-BUDGET-3 (монотонность): при неотрицательной норме притока энергия не убывает.

Опровержение каждой — контрпример: мир и последовательность шагов, после которых
инвариант нарушен. Такого быть не должно, потому что `step` перекладывает ровно
`income`.

Зачем проекту: питон-тест проверяет один шаг; здесь доказано для любой длины и
любого порядка. Критично при паразитизме и горизонтальном переносе, где легко
«напечатать» энергию в коде.

Модель — целые единицы энергии, чтобы доказательства шли на `omega` без
зависимостей (mathlib не нужен).
-/

structure World where
  resource : Int
  energy : Int

/-- Шаг бюджета: доход ограничен ресурсом и нормой притока. -/
def step (w : World) (rate : Int) : World :=
  let income := if w.resource ≤ rate then w.resource else rate
  { resource := w.resource - income, energy := w.energy + income }

/-- Прогон: последовательное применение шага к списку норм притока. -/
def run (w : World) : List Int → World
  | [] => w
  | r :: rs => run (step w r) rs

/-- F-BUDGET-1: сохранение суммы на одном шаге. -/
theorem budget_conserved (w : World) (rate : Int) :
    (step w rate).resource + (step w rate).energy = w.resource + w.energy := by
  unfold step
  simp
  omega

/-- F-BUDGET-2: сохранение суммы на любой последовательности шагов. -/
theorem run_conserves (w : World) (rates : List Int) :
    (run w rates).resource + (run w rates).energy = w.resource + w.energy := by
  induction rates generalizing w with
  | nil => rfl
  | cons r rs ih =>
    simp only [run]
    rw [ih]
    exact budget_conserved w r

/-- Ресурс никогда не растёт: доход не больше остатка. -/
theorem step_resource_le (w : World) (rate : Int)
    (hres : 0 ≤ w.resource) (hrate : 0 ≤ rate) :
    (step w rate).resource ≤ w.resource := by
  unfold step
  simp
  omega

/-- F-BUDGET-3: при неотрицательной норме притока энергия не убывает от шага. -/
theorem step_energy_monotone (w : World) (rate : Int)
    (hres : 0 ≤ w.resource) (hrate : 0 ≤ rate) :
    w.energy ≤ (step w rate).energy := by
  unfold step
  simp
  omega

/-- Доход неотрицателен, если неотрицательны ресурс и приток. -/
theorem income_nonneg (w : World) (rate : Int)
    (hres : 0 ≤ w.resource) (hrate : 0 ≤ rate) :
    0 ≤ (if w.resource ≤ rate then w.resource else rate) := by
  omega

/-- Мёртвое поле (нулевые ресурс и энергия) остаётся мёртвым: печати нет. -/
theorem no_free_energy (rate : Int) (hrate : 0 ≤ rate) :
    (step ⟨0, 0⟩ rate).energy = 0 := by
  unfold step
  simp only
  omega
