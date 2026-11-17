/-!
选择题 1 的机检验证：路程与位移是两个不同的量。

题干：总里程约 7500 km，起终点直线距离约 2000 km。
- 路程（轨迹长度）是标量，沿路径累加；
- 位移是矢量，只看起点到终点的直线距离。

本文件用一维折线模型机检两件事：
1. 一般结论：对任意折线，位移大小不超过路程；
2. 本题数据可同时满足「路程 7500、位移 2000」。
-/

/-- 一维折线：`segs` 是各段位移，路程 = 各段位移大小之和 -/
def pathLen : List Int → Nat
  | [] => 0
  | s :: ss => s.natAbs + pathLen ss

/-- 路程不小于位移大小（三角不等式，对任意折线成立） -/
theorem displacement_le_path (segs : List Int) :
    segs.sum.natAbs ≤ pathLen segs := by
  induction segs with
  | nil => simp [pathLen]
  | cons s ss ih =>
    simp only [pathLen, List.sum_cons]
    calc (s + ss.sum).natAbs ≤ s.natAbs + ss.sum.natAbs := Int.natAbs_add_le s ss.sum
      _ ≤ s.natAbs + pathLen ss := Nat.add_le_add_left ih _
      _ = pathLen (s :: ss) := rfl

/-- 具体数据：先走 4750 km，再折返 2750 km -/
example : (([4750, -2750] : List Int).sum).natAbs = 2000 := by decide

example : pathLen [4750, -2750] = 7500 := by decide

/-- 与题干 7500 / 2000 对照：两个数值互换即选项 A、B 的错法 -/
example : (7500 : Nat) ≠ 2000 := by decide

example : (2000 : Nat) ≠ 7500 := by decide

/-- 7500 与 2000 并存不矛盾：路程大于位移 -/
example : (2000 : Nat) ≤ 7500 := by decide
