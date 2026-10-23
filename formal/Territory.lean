/-
Формальная гипотеза F-BUDGET-4: неудачное размножение не тратит энергию.

Откуда (цикл «библиотека → Lean», после результата randmask про «фильтр
статистик»): в мире правило «спора в свободные соседние клетки» означает, что при
плотной популяции потомка нет. В коде это ветка `return None`, и там легко
случайно списать энергию у родителя. Тест проверяет один вызов; здесь
доказывается для любых значений.

Плюс отдельно фиксируется, что успешная спора только перекладывает энергию:
суммарный бюджет пары «родитель + потомок» не растёт. Это инвариант, который
станет критичным при паразитизме.
-/

structure PondState where
  parent : Int
  child : Int

/-- Почка: если есть свободное место, родитель платит и потомок получает;
если места нет — состояние не меняется. -/
def bud (s : PondState) (free : Bool) (pay : Int) : PondState :=
  match free with
  | true => { parent := s.parent - pay, child := s.child + pay }
  | false => s

/-- Суммарный запас пары «родитель + потомок». -/
def total (s : PondState) : Int := s.parent + s.child

/-- F-BUDGET-4a: при отсутствии свободных соседей ничего не меняется. -/
theorem blocked_bud_is_noop (s : PondState) (pay : Int) :
    bud s false pay = s := by
  rfl

/-- F-BUDGET-4b: неудачное размножение сохраняет суммарный запас. -/
theorem blocked_bud_conserves (s : PondState) (pay : Int) :
    total (bud s false pay) = total s := by
  rfl

/-- F-BUDGET-4c: успешное размножение только перекладывает энергию. -/
theorem bud_conserves (s : PondState) (pay : Int) :
    total (bud s true pay) = total s := by
  unfold total bud
  simp
  omega

/-- Следствие: потомок не может получить больше, чем заплатил родитель. -/
theorem child_gain_le_parent_loss (s : PondState) (pay : Int) (h : 0 ≤ pay) :
    (bud s true pay).child - s.child ≤ s.parent - (bud s true pay).parent := by
  unfold bud
  simp
  omega
