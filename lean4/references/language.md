# 语法与 tactic 速查

只列高频用法。核心库（`Init`/`Std`，无需 Mathlib）自带 `rfl`、`simp`、`decide`、`omega`、`induction`、`cases`、`rw`、`exact`、`apply`、`intro`、`constructor`、`calc`；`ring`、`linarith`、`norm_num`、`positivity`、`field_simp`、`aesop` 需要 Mathlib。

## 声明

```lean
def double (n : Nat) : Nat := 2 * n

theorem add_comm_sample (a b : Nat) : a + b = b + a :=
  Nat.add_comm a b

example : 2 + 2 = 4 := by decide

inductive Color where
  | red | green | blue
  deriving Repr, DecidableEq

structure Point where
  x : Int
  y : Int
  deriving Repr

class HasSize (α : Type) where
  size : α → Nat

instance : HasSize (List α) where
  size xs := xs.length
```

要点：`def` 定义可计算函数，`theorem`/`lemma` 定义命题证明，`example` 匿名（不进入环境）。类型注解可省略，Lean 会推断，但公开 API 建议写全。

## 绑定与隐式参数

```lean
variable {α : Type} [DecidableEq α]      -- 隐式类型 + 类型类实例
def head? (xs : List α) : Option α := xs.head?
def map2 (f : α → β) (xs : List α) : List β := xs.map f
```

`{α : Type}` 花括号 = 隐式，调用时自动推断；`[C α]` 方括号 = 类型类实例；`(x : T)` 圆括号 = 显式。显式传隐式参数写 `@f α x`。

## 证明结构

```lean
theorem length_append_sample (xs ys : List α) :
    (xs ++ ys).length = xs.length + ys.length := by
  induction xs with
  | nil => simp
  | cons x xs ih => simp [ih]; omega
```

模式：

- `by` 进入 tactic 模式；`:= fun h => ...` 是项模式。
- `have h : P := by ...` 引入中间命题；`have := ...` 省略名字与类型。
- `calc a = b := by ... _ = c := by ...` 链式推导。
- `obtain ⟨a, b⟩ := h` 解构存在/合取；`rcases h with ⟨a, b⟩ | h` 分支解构。
- `show P` 改变目标显示形式；`suffices P by ...` 反向充分条件。
- `termination_by` / `decreasing_by` 处理递归函数终止性证明。

## tactic 表

| tactic | 作用 | 备注 |
|---|---|---|
| `rfl` | 定义相等闭包 | 只在 defeq 时成立 |
| `simp` | 化简重写 | `simp [h1, h2]`、`simp only [...]`、`simp at h` |
| `decide` | 可判定命题直接算 | 目标需 `Decidable` 实例 |
| `omega` | 线性整数/自然数算术 | 核心库可用，证 `⊢ n + 0 = n` 之类 |
| `ring` | 环上多项式恒等 | 需 Mathlib |
| `linarith` | 线性不等式 | 需 Mathlib |
| `norm_num` | 数值计算 | 需 Mathlib |
| `rw [h]` | 重写目标 | `rw [← h]` 反向，`rw [h] at h2` |
| `exact e` | 给出完整证明项 | 类型须匹配 |
| `apply h` | 后向推理 | 目标与 `h` 结论合一 |
| `intro h` | 引入蕴含/全称 | `intro` 多个可写 `intros` |
| `constructor` | 拆分 ∧ / ↔ / 构造子 | |
| `cases h` | 分类讨论 | `cases h with \| a => ...` |
| `induction n with` | 归纳 | `\| zero => ... \| succ n ih => ...` |
| `contrapose` / `by_contra h` | 反证与逆否 | |
| `unfold f` | 展开定义 | 慎用，容易炸开表达式 |
| `simp_all` | 全上下文化简 | 大上下文时慢 |
| `exact_mod_cast` | 类型转换 | |
| `aesop` | 自动搜索 | 需 Mathlib |

## 求值与小工具

```lean
#check Nat.add_comm      -- 查类型
#print Nat.add_comm      -- 查定义/定理
#eval double 21           -- 运行可计算项
#reduce (2 + 2 : Nat)     -- 归一化
#check (rfl : 1 = 1)
```

## 常见写法陷阱

- **`rfl` 失败**：目标不是 defeq，例如 `([] ++ ys).length = [].length + ys.length`——`[].length + ys.length` 是 `0 + ys.length`，不会自动化成 `ys.length`。改用 `simp` 或 `omega`。
- **`simp` 卡住不收敛**：加 `only` 限定重写集，或 `simp [← h]` 定向。
- **`omega` 失败**：目标含非线性乘法、除法、或非 `Int`/`Nat` 的数值类型。
- **`autoImplicit`**：新版默认可能关闭；未声明的标识符会报 `unknown identifier`，需显式 `variable`。
- **`sorry` 会让构建"成功"**：`sorry` 只产生 warning 不产生 error，验收时必须单独 grep。
