/-
Бюджет среды «пруд»: энергия не берётся из ниоткуда.

Модель шага (целые единицы энергии, чтобы доказательство шло на `omega` без
зависимостей):

  income    = min resource rate     -- клетка забирает из ресурса не больше притока
  resource' = resource - income     -- ресурс убывает ровно на доход
  energy'   = energy + income       -- энергия растёт ровно на доход

Доказываем: сумма (ресурс + энергия) сохраняется, ресурс не становится
отрицательным, доход неотрицателен при неотрицательном притоке. Это ровно тот
инвариант, который в питоне проверяется тестом на одном шаге, а здесь — для всех
шагов сразу.
-/

structure World where
  resource : Int
  energy : Int

/-- Шаг бюджета: доход ограничен ресурсом и нормой притока. -/
def step (w : World) (rate : Int) : World :=
  let income := min w.resource rate
  { resource := w.resource - income, energy := w.energy + income }

/-- Сохранение суммы: сколько ушло из ресурса, столько пришло в энергию. -/
theorem budget_conserved (w : World) (rate : Int) :
    (step w rate).resource + (step w rate).energy = w.resource + w.energy := by
  unfold step
  simp
  omega

/-- Ресурс никогда не уходит в минус (доход не больше остатка по построению). -/
theorem resource_nonneg (w : World) (rate : Int) :
    0 ≤ (step w rate).resource := by
  unfold step
  simp
  omega

/-- Доход неотрицателен, если неотрицательны и ресурс, и приток. -/
theorem income_nonneg (w : World) (rate : Int)
    (_hres : 0 ≤ w.resource) (hrate : 0 ≤ rate) :
    0 ≤ min w.resource rate := by
  omega

/-- Мёртвое поле (нулевой ресурс, нулевая энергия) остаётся мёртвым: печати нет. -/
theorem no_free_energy (rate : Int) (hrate : 0 ≤ rate) :
    (step ⟨0, 0⟩ rate).energy = 0 := by
  unfold step
  simp
  omega

/-- При неотрицательном притоке энергия не убывает: шаг только добавляет. -/
theorem energy_monotone (w : World) (rate : Int)
    (_hres : 0 ≤ w.resource) (hrate : 0 ≤ rate) :
    w.energy ≤ (step w rate).energy := by
  unfold step
  simp
  omega
