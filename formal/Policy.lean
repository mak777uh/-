/-
Формальные гипотезы F-POLICY-1..6: политика автономии (`lab/autonomy-rules.json`)
непротиворечива, полна и приоритезирована.

Почему это важно проекту: политика решает, что агент может делать без спроса, что
только с владельцем и что запрещено. Пока она живёт только в JSON и в прозе, её
можно нарушить, не заметив — и именно это случилось 08.11: `check_autonomy.py`
проверял структуру файла, но не проверял владельца прогона (проба P2 нашла дыру).
Здесь политика становится объектом с доказуемыми свойствами.

Три уровня (модель herness):
  A. политика  — доказуема (этот файл);
  B. посредник — доказуем для малого кода;
  C. замыкание — только измеряется (`scripts/closure_probe.py`).

Модель: действие — тройка (кто, что, над чем); политика — три списка действий.
Приоритет: запрет сильнее требования владельца, требование владельца сильнее
разрешения. Это не соглашение, а теорема ниже.
-/

namespace Policy

/-- Одно действие: кто, что, над каким ресурсом. -/
structure Action where
  who : String
  what : String
  res : String
  deriving DecidableEq, Repr

/-- Политика: три списка. -/
structure Policy where
  allowed : List Action
  needsOwner : List Action
  forbidden : List Action

/-- Может ли агент сделать это без спроса. -/
def mayWithoutAsking (p : Policy) (a : Action) : Bool :=
  p.allowed.contains a && !p.forbidden.contains a && !p.needsOwner.contains a

/-- Требует ли действие владельца. -/
def needsOwnerNow (p : Policy) (a : Action) : Bool :=
  p.needsOwner.contains a && !p.forbidden.contains a

/-- Запрещено ли действие. -/
def isForbidden (p : Policy) (a : Action) : Bool :=
  p.forbidden.contains a

/-! ### Леммы о Bool

Три короткие леммы, чтобы доказательства ниже не зависели от устройства `simp`. -/

theorem and_true_left {x y : Bool} (h : (x && y) = true) : x = true := by
  cases x <;> cases y <;> simp_all

theorem and_true_right {x y : Bool} (h : (x && y) = true) : y = true := by
  cases x <;> cases y <;> simp_all

theorem not_true_is_false {x : Bool} (h : (!x) = true) : x = false := by
  cases x <;> simp_all

/-- F-POLICY-1: запрет сильнее разрешения.

Если действие есть и в `allowed`, и в `forbidden`, оно НЕ разрешено без спроса.
Это то свойство, отсутствие которого делает политику декоративной: список
разрешений не должен перебивать список запретов. -/
theorem forbid_beats_allow (p : Policy) (a : Action)
    (h : isForbidden p a = true) :
    mayWithoutAsking p a = false := by
  unfold mayWithoutAsking isForbidden at *
  rw [h]
  simp

/-- F-POLICY-2: запрет сильнее требования владельца.

Действие, которое и «только с владельцем», и «запрещено», не может быть
выполнено даже с владельцем — иначе запрет обходится через согласие. -/
theorem forbid_beats_owner (p : Policy) (a : Action)
    (h : isForbidden p a = true) :
    needsOwnerNow p a = false := by
  unfold needsOwnerNow isForbidden at *
  rw [h]
  simp

/-- F-POLICY-3: разрешённое без спроса не требует владельца. -/
theorem allowed_not_owner (p : Policy) (a : Action)
    (h : mayWithoutAsking p a = true) :
    needsOwnerNow p a = false := by
  unfold mayWithoutAsking at h
  have h1 : (p.allowed.contains a && !p.forbidden.contains a) = true := and_true_left h
  have h2 : (!p.needsOwner.contains a) = true := and_true_right h
  have hnoOwner : p.needsOwner.contains a = false := not_true_is_false h2
  unfold needsOwnerNow
  rw [hnoOwner]
  simp

/-- F-POLICY-4: разрешённое без спроса не запрещено. -/
theorem allowed_not_forbidden (p : Policy) (a : Action)
    (h : mayWithoutAsking p a = true) :
    isForbidden p a = false := by
  unfold mayWithoutAsking at h
  have h1 : (p.allowed.contains a && !p.forbidden.contains a) = true := and_true_left h
  have hnoForbid : (!p.forbidden.contains a) = true := and_true_right h1
  unfold isForbidden
  exact not_true_is_false hnoForbid

/-- F-POLICY-5: действие, которое есть только в `allowed`, разрешено без спроса.

Свойство полноты: если действие упомянуто в политике ровно в одном списке,
решение о нём определено, а не остаётся неясным. -/
theorem only_allowed_means_allowed (p : Policy) (a : Action)
    (hallow : p.allowed.contains a = true)
    (hnoForbid : p.forbidden.contains a = false)
    (hnoOwner : p.needsOwner.contains a = false) :
    mayWithoutAsking p a = true ∧ needsOwnerNow p a = false ∧ isForbidden p a = false := by
  refine ⟨?_, ?_, ?_⟩
  · unfold mayWithoutAsking
    rw [hallow, hnoForbid, hnoOwner]
    simp
  · unfold needsOwnerNow
    rw [hnoOwner]
    simp
  · unfold isForbidden
    exact hnoForbid

/-- F-POLICY-6: пустая политика ничего не разрешает.

Отрицательный контроль: если бы эта теорема не проходила, значит разрешение не
зависит от содержимого политики. -/
theorem empty_allows_nothing (a : Action) :
    mayWithoutAsking ⟨[], [], []⟩ a = false := by
  unfold mayWithoutAsking
  simp

end Policy
