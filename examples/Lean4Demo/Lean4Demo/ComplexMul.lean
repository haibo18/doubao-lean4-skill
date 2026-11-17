/-!
选择题 1 的机检验证：(1 - 3i)² 的值。

用整数对 `⟨实部, 虚部⟩` 表示复数，乘法按
`(a + bi)(c + di) = (ac - bd) + (ad + bc)i`。
-/

structure Cx where
  re : Int
  im : Int
  deriving Repr, DecidableEq

def Cx.mul (z w : Cx) : Cx :=
  ⟨z.re * w.re - z.im * w.im, z.re * w.im + z.im * w.re⟩

/-- 平方展开的一般式：`(a + bi)² = (a² - b²) + (ab + ba)i` -/
theorem sq_formula (a b : Int) :
    Cx.mul ⟨a, b⟩ ⟨a, b⟩ = ⟨a * a - b * b, a * b + b * a⟩ := rfl

/-- 本题：a = 1，b = -3，故实部 1 - 9 = -8，虚部 -3 + -3 = -6 -/
example : Cx.mul ⟨1, -3⟩ ⟨1, -3⟩ = ⟨-8, -6⟩ := by decide

/-- 逐项排除错误选项 -/
example : Cx.mul ⟨1, -3⟩ ⟨1, -3⟩ ≠ ⟨-8, 6⟩ := by decide
example : Cx.mul ⟨1, -3⟩ ⟨1, -3⟩ ≠ ⟨8, 6⟩ := by decide
example : Cx.mul ⟨1, -3⟩ ⟨1, -3⟩ ≠ ⟨8, -6⟩ := by decide
