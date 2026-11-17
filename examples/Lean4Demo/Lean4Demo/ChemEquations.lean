/-!
选择题 3 的机检：四个方程式的原子守恒核对。

模型：分子 = `(元素, 原子数)` 列表；配平 = 两边各元素原子总数相等。
只检查原子守恒，不检查电荷、氧化还原、反应条件——化学上的"对错"还需人来判断。
-/

/-- 统计某元素在一个式子中的原子数 -/
def countOf (el : String) (f : List (String × Nat)) : Nat :=
  f.foldl (fun acc p => if p.1 == el then acc + p.2 else acc) 0

/-- 本题涉及的元素 -/
def elements : List String := ["H", "O", "Cu", "S", "Al", "Cl", "Na", "C", "Br", "Ag"]

/-- 两边原子数是否逐元素相等 -/
def balanced (l r : List (String × Nat)) : Bool :=
  elements.all (fun e => countOf e l == countOf e r)

/-- 化学计量系数 -/
def scale (k : Nat) (f : List (String × Nat)) : List (String × Nat) :=
  f.map (fun p => (p.1, p.2 * k))

/-- 把一侧的多个分子并成一个原子清单 -/
def side : List (List (String × Nat)) → List (String × Nat) := List.flatten

def cu : List (String × Nat) := [("Cu", 1)]
def h2so4 : List (String × Nat) := [("H", 2), ("S", 1), ("O", 4)]
def cuso4 : List (String × Nat) := [("Cu", 1), ("S", 1), ("O", 4)]
def so2 : List (String × Nat) := [("S", 1), ("O", 2)]
def h2o : List (String × Nat) := [("H", 2), ("O", 1)]

def alcl3 : List (String × Nat) := [("Al", 1), ("Cl", 3)]
def naoh : List (String × Nat) := [("Na", 1), ("O", 1), ("H", 1)]
def aloh3 : List (String × Nat) := [("Al", 1), ("O", 3), ("H", 3)]
def nacl : List (String × Nat) := [("Na", 1), ("Cl", 1)]
def naalo2 : List (String × Nat) := [("Na", 1), ("Al", 1), ("O", 2)]

def c2h4 : List (String × Nat) := [("C", 2), ("H", 4)]
def br2 : List (String × Nat) := [("Br", 2)]
def c2h4br2 : List (String × Nat) := [("C", 2), ("H", 4), ("Br", 2)]

def na2s : List (String × Nat) := [("Na", 2), ("S", 1)]
def agcl : List (String × Nat) := [("Ag", 1), ("Cl", 1)]
def ag2s : List (String × Nat) := [("Ag", 2), ("S", 1)]

/-- A：Cu + 2H₂SO₄(浓) = CuSO₄ + SO₂ + 2H₂O -/
example :
    balanced (side [cu, scale 2 h2so4]) (side [cuso4, so2, scale 2 h2o]) = true := by
  decide

/-- B（题干写法）：AlCl₃ + 3NaOH = Al(OH)₃ + 3NaCl，原子守恒成立 -/
example :
    balanced (side [alcl3, scale 3 naoh]) (side [aloh3, scale 3 nacl]) = true := by
  decide

/-- B 的正确产物（足量烧碱，Al(OH)₃ 溶解）：
    AlCl₃ + 4NaOH = NaAlO₂ + 3NaCl + 2H₂O，同样守恒 -/
example :
    balanced (side [alcl3, scale 4 naoh]) (side [naalo2, scale 3 nacl, scale 2 h2o]) = true := by
  decide

/-- C：CH₂=CH₂ + Br₂ = CH₂BrCH₂Br -/
example :
    balanced (side [c2h4, br2]) (side [c2h4br2]) = true := by
  decide

/-- D：Na₂S + 2AgCl = Ag₂S + 2NaCl -/
example :
    balanced (side [na2s, scale 2 agcl]) (side [ag2s, scale 2 nacl]) = true := by
  decide
