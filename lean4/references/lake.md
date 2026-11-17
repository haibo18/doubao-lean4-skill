# Lake 工程与依赖

Lake 是 Lean 4 的构建系统兼包管理器，读取 `lakefile.toml`（或 `lakefile.lean`），产物在 `.lake/build/`。

## 官方模板生成的 `lakefile.toml`

`lake new Demo`（`lib` 模板）产出：

```toml
name = "Demo"
version = "0.1.0"
defaultTargets = ["demo"]

[[lean_lib]]
name = "Demo"

[[lean_exe]]
name = "demo"
root = "Main"
```

- `[[lean_lib]] name = "Demo"` → 库根模块为 `Demo.lean`，模块文件放 `Demo/` 子目录。
- `[[lean_exe]]` → 可执行目标，`root = "Main"` 对应 `Main.lean`。
- `defaultTargets` 决定裸 `lake build` 构建哪些目标。

`leanfile.lean` 形式等价（需要更复杂逻辑时用）：

```lean
import Lake
open Lake DSL

package demo

@[default_target]
lean_lib Demo

lean_exe demo where
  root := `Main
```

## 常用命令

```bash
lake build                  # 构建默认目标
lake build Demo.Proofs      # 只构建某个模块
lake build -j 2             # 限制并行（内存不够时）
lake env lean Foo.lean      # 带工程依赖环境编译单文件（推荐）
lake env                  # 打印工程环境变量（LEAN_PATH 等）
lake update                 # 更新依赖并写 lake-manifest.json
lake clean                  # 清理构建产物
lake exe demo               # 运行可执行目标
```

**判断单个文件能否编译，一律用 `lake env lean`**；直接 `lean file.lean` 不带工程依赖，会缺 import。

## 依赖

Lean 依赖用 git 拉取，构建时解析到 `lake-manifest.json`（应提交到版本库以锁定版本）。

Mathlib 是最常见的重依赖：

```bash
# 方式一：用官方模板一步到位（推荐，模板会写入匹配的 lean-toolchain）
lake new MyProof math

# 方式二：已有工程里加依赖（lakefile.lean）
require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git"
```

Mathlib 注意事项：

- 工具链必须与 Mathlib 要求一致，`lean-toolchain` 写错会直接编译失败；用 `math` 模板最省事。
- 首次拉取数 GB，编译数十分钟到数小时；官方提供预编译缓存：`lake exe cache get`。
- 只在确实需要 `ring`、`linarith`、`norm_num`、`positivity`、`aesop` 等 tactic 或大量现成定理时才引入。

## 目录与命名

模块名由路径决定，分隔符是 `.`：

| 文件 | 模块名 |
|---|---|
| `MyProof/Basic.lean` | `MyProof.Basic` |
| `MyProof/Algebra/Group.lean` | `MyProof.Algebra.Group` |

新文件必须满足两点才会被构建：放在库目录内、且被根模块（或某个被根模块 import 的模块）`import`。

## 缓存与体积

`.lake/` 存构建产物与依赖源码，可达数百 MB 到数 GB。清理用 `lake clean`；不要手删 `.lake` 里单个文件来"修构建"，容易留下不一致状态。
