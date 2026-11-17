/-!
Sample proofs used to verify the toolchain end to end.
Replace this file with your own formalization.
-/

theorem add_comm_sample (a b : Nat) : a + b = b + a :=
  Nat.add_comm a b

theorem imp_self_sample (p : Prop) : p → p :=
  fun h => h

example : 2 + 2 = 4 := by decide

theorem length_append_sample (xs ys : List α) :
    (xs ++ ys).length = xs.length + ys.length := by
  induction xs with
  | nil => simp
  | cons x xs ih => simp [ih]; omega
