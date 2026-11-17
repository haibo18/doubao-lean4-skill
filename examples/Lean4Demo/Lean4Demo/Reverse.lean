/-!
Real-task sample: list reversal and a structurally recursive function.
-/

theorem reverse_reverse (xs : List α) : xs.reverse.reverse = xs := by
  induction xs with
  | nil => rfl
  | cons x xs ih => simp [ih]

def fib : Nat → Nat
  | 0 => 0
  | 1 => 1
  | n + 2 => fib (n + 1) + fib n

theorem fib_add_two (n : Nat) : fib (n + 2) = fib (n + 1) + fib n := rfl

example : fib 10 = 55 := by decide
