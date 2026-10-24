/-
Формальная гипотеза F-17: гейт зажигания не даёт зажечь клетку без живого соседа,
поэтому пустое поле остаётся пустым при любом числе шагов.

Откуда пришла (цикл «данные → Lean»): серия основания (§10af) стоит на том, что с
`--ignition-gate` правило не может зажечь клетку из мёртвого состояния. Без гейта
обученное правило из нулевого поля зажигает всё (1024 из 1024 на шаге 1, §10ae), и
вопрос «основывает ли колонию N клеток» не задаётся. Сейчас это свойство держится на
коде, который мы проверили руками; здесь оно фиксируется как утверждение о шаге мира,
чтобы флаг не мог тихо изменить семантику.

Что опровергнет теорему: реализация, в которой новая живая клетка может появиться без
живого 4-соседа (тогда `newAlive` не вкладывается в `alive ∪ N(alive)`), или гейт,
гасящий уже живые клетки (тогда пустое поле перестаёт быть инвариантом по другой
причине).

Модель: булева решётка `Nat × Nat`; живость — предикат. Гейт: множество живых на шаге
t+1 есть «старые живые» ∪ (то, что зажгло правило, но только в клетках с живым
4-соседом на шаге t). Это ровно то, что делает `PondRun._gate_ignition`.
-/

/-- Соседство: 4-сосед (манхэттенское расстояние 1). -/
def nbr4 (a b : Nat × Nat) : Prop :=
  (a.1 = b.1 ∧ (a.2 + 1 = b.2 ∨ b.2 + 1 = a.2)) ∨
  (a.2 = b.2 ∧ (a.1 + 1 = b.1 ∨ b.1 + 1 = a.1))

/-- Живость в мире: множество клеток. -/
def Alive := Nat × Nat → Prop

/-- Шаг мира с гейтом: правило предлагает `fire`, но зажигается только то, у чего был
живой 4-сосед; уже живые клетки не гасятся. -/
def gateStep (alive fire : Alive) : Alive :=
  fun c => alive c ∨ (fire c ∧ ∃ n, nbr4 c n ∧ alive n)

/-- Новые живые клетки на шаге: были живы и не были. -/
def newAlive (alive next : Alive) : Alive :=
  fun c => next c ∧ ¬ alive c

/-- F-IGNITE-1 (рабочий номер F-17), основное утверждение: каждая новая живая клетка
имеет живого 4-соседа на предыдущем шаге. -/
theorem new_alive_has_live_neighbour (alive fire : Alive) :
    ∀ c, newAlive alive (gateStep alive fire) c → ∃ n, nbr4 c n ∧ alive n := by
  intro c hc
  have hnext : gateStep alive fire c := hc.1
  have hnot : ¬ alive c := hc.2
  rcases hnext with hold | ⟨hfire, n, hnbr, halive⟩
  · exact absurd hold hnot
  · exact ⟨n, hnbr, halive⟩

/-- F-IGNITE-1, следствие 1: пустое поле остаётся пустым после одного шага гейта. -/
theorem empty_stays_empty_step (fire : Alive) :
    ∀ c, ¬ gateStep (fun _ => False) fire c := by
  intro c h
  rcases h with h0 | ⟨_, n, _, hn⟩
  · exact h0
  · exact hn

/-- Прогон n шагов гейта. -/
def gateRun (fire : Alive) : Nat → Alive
  | 0 => fun _ => False
  | n + 1 => gateStep (gateRun fire n) fire

/-- Следствие 2 (индукция по t): из пустого поля гейт не зажигает ничего ни на одном
шаге. Это и есть формальная опора серии основания. -/
theorem empty_stays_empty (fire : Alive) : ∀ n c, ¬ gateRun fire n c := by
  intro n
  induction n with
  | zero => intro c h; exact h
  | succ n ih =>
      intro c h
      -- шаг (n+1) начинается с пустого поля по индукционному предположению:
      -- либо «было живо» (противоречит ih), либо «зажглось у живого соседа» (тоже ih)
      simp only [gateRun, gateStep] at h
      rcases h with h0 | ⟨_, n', _, hn⟩
      · exact ih c h0
      · exact ih n' hn

/-- Следствие 3: если поле пусто, то и «новых» клеток нет — гейт ничего не добавляет. -/
theorem no_new_from_empty (fire : Alive) (n : Nat) :
    ∀ c, ¬ newAlive (gateRun fire n) (gateRun fire (n + 1)) c := by
  intro c hc
  exact empty_stays_empty fire (n + 1) c hc.1
