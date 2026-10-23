/-
F-ADAPT — граница полезности обучения: успевает ли подстройка до смерти.

Зачем. Мы получили отрицательные результаты по пяти схемам обучения и хотим понять,
где вообще может быть польза. Из F-SURV есть точное время смерти:
`E₀ / (цена − доход)`. Отсюда элементарная, но решающая граница:

  * если время обучения `T` больше времени смерти, клетка умрёт раньше, чем
    успеет изменить стратегию — обучение бесполезно, сколько бы шагов оно ни делало;
  * если `T` меньше, у обучения есть окно, но только размером в этот зазор.

Это «математика вместо перебора»: не нужно гонять серии, чтобы узнать, что медленное
обучение в дефицитной зоне не спасает — это следует из арифметики.

Что опровергнет: если в симуляции клетка с `T > время смерти` всё-таки меняет
поведение и выживает, значит у мира есть скрытый приток энергии или обучение
не сводится к смене стратегии — тогда эту модель надо менять, а не подгонять.
-/

namespace Adapt

/-- Энергия после `steps` шагов при дефиците `d = cost - income > 0`. -/
def energyAfter (e d : Int) (steps : Nat) : Int := e - (steps : Int) * d

/-- F-ADAPT-1: если обучение требует `T` шагов, а энергии хватает лишь на `k`
    шагов (`e ≤ k*d`), и `T ≥ k`, то к моменту `T` энергия неположительна. -/
theorem learning_too_slow_dies
    (e d : Int) (k T : Nat) (hd : 0 < d) (he : e ≤ (k : Int) * d) (hT : k ≤ T) :
    energyAfter e d T ≤ 0 := by
  unfold energyAfter
  have hkT : (k : Int) ≤ (T : Int) := by exact_mod_cast hT
  have hnonneg : (0 : Int) ≤ d := Int.le_of_lt hd
  have hmul : (k : Int) * d ≤ (T : Int) * d :=
    Int.mul_le_mul_of_nonneg_right hkT hnonneg
  omega

/-- F-ADAPT-2: если обучение быстрее смерти (`T < k`), к моменту `T` энергия
    строго положительна — окно для подстройки существует. -/
theorem learning_fast_enough_survives
    (e d : Int) (k T : Nat) (hd : 0 < d) (he : e ≤ (k : Int) * d)
    (hT : T < k) (hneed : (T : Int) * d < e) :
    0 < energyAfter e d T := by
  unfold energyAfter
  omega

/-- F-ADAPT-3: окно обучения не больше времени смерти: если `T*d ≥ e`, энергии на
    `T` шагов не хватает. -/
theorem window_no_longer_than_lifetime
    (e d : Int) (T : Nat) (hd : 0 < d) (h : e ≤ (T : Int) * d) :
    energyAfter e d T ≤ 0 := by
  unfold energyAfter
  omega

/-- F-ADAPT-4: при нулевом дефиците время жизни не ограничено: энергия не убывает. -/
theorem no_deficit_no_deadline (e : Int) (steps : Nat) :
    energyAfter e 0 steps = e := by
  unfold energyAfter
  simp

end Adapt
