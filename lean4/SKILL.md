---
name: lean4
description: Lean 4 形式化数学与定理证明工具链：安装与管理 elan 工具链、创建 Lake 工程、编译校验 .lean 文件、定位并修复 Lean 报错，以及从源码构建 leanprover/lean4 仓库。当用户提到 Lean 4 / Lean4、leanprover/lean4、.lean 文件、lake build、elan、Lean 工具链、形式化证明、定理证明器、把数学命题写成可机检证明、或要修改 Lean 源码时使用。
---

# Lean 4

Lean 4 是依赖类型理论（CIC）的交互式定理证明器兼函数式编程语言，仓库 `leanprover/lean4` 提供编译器、`Init`/`Std` 核心库、Lake 构建系统和语言服务器。本技能把「装工具链 → 建工程 → 写证明 → 编译校验 → 排错」固化成可重复流程。

## 三条执行路径

先判断用户属于哪条，不要一律从源码编译：

| 场景 | 路径 |
|---|---|
| 写证明 / 建工程 / 跑 `.lean` | A：elan 预编译工具链（默认，几分钟） |
| 环境体检、版本不对、命令找不到 | A 的 `doctor` 子命令 |
| 改 Lean 编译器/核心库本身、提 PR | B：源码构建，读 `references/build-from-source.md` |

**默认走 A。** 只有用户明确要改 Lean 源码或做编译器开发时才走 B——源码构建在 Windows 原生环境不可行（见下）。

## 环境要求

| 项 | 要求 |
|---|---|
| Python | ≥ 3.8（脚本依赖，标准库即可） |
| 网络 | 可访问 `elan.lean-lang.org`、`releases.lean-lang.org`、GitHub |
| 磁盘 | 工具链约 1.5 GB，工程缓存另计；建议 ≥ 5 GB 空闲 |
| 内存 | 常规证明 4 GB 足够；Mathlib 建议 ≥ 16 GB |
| git | 需要（`lake` 拉依赖用） |
| 平台 | Windows 10+/Linux/macOS。源码构建另需 CMake ≥ 3.21、Makefile 生成器、C++14 编译器、GMP ≥ 6.3、libuv、OpenSSL |

## 脚本

所有操作走 `scripts/lean4ctl.py`，不要手敲一长串 elan/lake 命令。脚本自动把 `~/.elan/bin` 注入子进程 PATH，因此在未重启终端的情况下也能直接工作。

```bash
python scripts/lean4ctl.py <子命令> [参数]
```

| 子命令 | 作用 | 典型调用 |
|---|---|---|
| `doctor` | 体检：平台/CPU/磁盘/git/elan/lean/lake/已装工具链/是否 ready | `doctor` |
| `install` | 装 elan（缺失时）+ 指定工具链 | `install --toolchain leanprover/lean4:stable` |
| `new` | 用官方模板建 Lake 工程，并写入样例证明 | `new MyProof --dir . --template lib` |
| `build` | 跑 `lake build`，统计 error/warning 行 | `build ./MyProof` |
| `check` | 编译单个 `.lean` 文件，有错时打印诊断 | `check Foo.lean --project ./MyProof` |
| `exec` | 打印 elan/lean/lake 绝对路径 | `exec` |

`new --template` 可选 `lib`（默认）、`std`、`exe`、`math`、`math-lax`。`math`/`math-lax` 会拉 Mathlib（数 GB、首次编译数十分钟），非必要不用。

## 标准流程

1. **体检**：`python scripts/lean4ctl.py doctor`。`status: ready` 才继续；`incomplete` 则进入第 2 步。
2. **安装**：`python scripts/lean4ctl.py install`。脚本幂等——已装 elan 时只补工具链，已装工具链不重复下载。装完再跑一次 `doctor` 确认 `lean`/`lake` 版本。
3. **建工程**：`python scripts/lean4ctl.py new <名字> --dir <目录>`。生成 `lakefile.toml`、`lean-toolchain`、根模块、`<名字>/Basic.lean` 与 `Proofs.lean` 样例。
4. **写证明**：把命题写进 `<名字>/<模块>.lean`，并把该模块加到根模块的 `import` 链（Lake 只编译被根模块可达的模块）。
5. **编译**：`python scripts/lean4ctl.py build <工程目录>`。必须看到 `Build completed successfully` 且 `errors=0` 才算通过。
6. **单文件快查**：`python scripts/lean4ctl.py check <文件> --project <工程目录>`，比整包构建快，适合改一处的迭代。
7. **交付前复验**：最终版本再跑一次 `build`，不要用早前的成功结果冒充。

## 工程结构约定

```
MyProof/
├── lean-toolchain        # 形如 leanprover/lean4:v4.36.0，决定用哪个工具链
├── lakefile.toml         # [[lean_lib]] name = "MyProof"，[[lean_exe]] 可选
├── MyProof.lean          # 库根模块，import 所有子模块
└── MyProof/
    ├── Basic.lean
    └── Proofs.lean       # 新增模块必须放这一层
```

要点：库模块的物理路径是 `<包名>/<模块名>.lean`，模块名写作 `<包名>.<模块名>`。把文件放在工程根目录会得到 `bad import` / `no such file` 报错——这是最常见的翻车点。

## 证明工作流

写非平凡证明时按 `agents/proof-agent.md` 的角色规范执行：先形式化陈述，再分解成 `have` 子目标，逐步用 tactic 收敛，每次改动后跑 `check`，最后 `build` 全绿。不要一次写几百行再编译。

- 语法与常用 tactic：`references/language.md`
- 工程/依赖/多工具链：`references/toolchain.md`、`references/lake.md`
- 报错对照：`references/troubleshooting.md`
- 源码构建：`references/build-from-source.md`

## 验收标准

一个任务算完成，必须同时满足：

1. `doctor` 显示 `status: ready`；
2. 目标文件/工程 `build` 退出码 0 且 `errors=0`；
3. 用户要求的命题确实出现在源文件中且被编译通过（不是注释、不是 `sorry`、不是 `axiom`）；
4. `sorry`/`admit` 数量为 0，除非用户明确接受占位。

检查占位：`grep -rn "sorry\|admit" <工程目录> --include=*.lean`。

## 注意

- `lean-toolchain` 是版本唯一真源；换版本改这个文件，不要手动改 PATH 里的默认工具链去"碰运气"。
- 首次在新工程跑 `lake build` 会按 `lean-toolchain` 下载对应工具链，需要网络；离线环境先 `elan toolchain install` 预热。
- Windows 原生（MSVC）不能编译 Lean 源码：`CMakeLists.txt` 强制 Makefile 生成器。源码构建走 WSL2 或 msys2，见 `references/build-from-source.md`。
- Mathlib 相关任务先确认用户是否真的需要；引入 Mathlib 会让构建从秒级变成小时级。
