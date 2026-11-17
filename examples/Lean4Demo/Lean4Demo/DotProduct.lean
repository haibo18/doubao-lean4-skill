/-!
选择题 2 的机检验证：

已知 `|a + b| = 1`、`|a - b| = √3`，求 `a · b`。

为避免无理数 `√3`，用平方范数表述（对实范数二者等价）：
`|a + b|² = 1`、`|a - b|² = 3`。
向量取平面坐标 `(x, y)`，在有理数域 `Rat` 上完成推导——与实数域共用同一套环运算，
恒等式与线性结论不依赖任何具体数值。
-/

/-- 平面向量点积 `a · b = x₁x₂ + y₁y₂` -/
def dot (x1 y1 x2 y2 : Rat) : Rat :=
  x1 * x2 + y1 * y2

/-- 平方范数 `|v|² = x² + y²` -/
def normSq (x y : Rat) : Rat :=
  x * x + y * y

/-- 平方展开：`|a+b|² - |a-b|² = 4(a·b)`，交叉项相消 -/
theorem normSq_sub_normSq (x1 y1 x2 y2 : Rat) :
    normSq (x1 + x2) (y1 + y2) - normSq (x1 - x2) (y1 - y2)
      = 4 * dot x1 y1 x2 y2 := by
  grind [dot, normSq]

/-- 本题：两式相减得 `4(a·b) = 1 - 3 = -2`，故 `a·b = -1/2` -/
theorem dot_eq_neg_half (x1 y1 x2 y2 : Rat)
    (h1 : normSq (x1 + x2) (y1 + y2) = 1)
    (h2 : normSq (x1 - x2) (y1 - y2) = 3) :
    dot x1 y1 x2 y2 = -1 / 2 := by
  grind [dot, normSq]

/-- 数值自检：`-2 / 4` 确为 `-1/2` -/
example : ((-2 : Rat) / 4) = -1 / 2 := by
  grind
