# lean4-skill

把 Lean 4 的「装工具链 → 建工程 → 写证明 → 编译校验 → 排错」固化成一套可直接执行的 Skill，给 AI Agent（豆包工作模式 / Claude Code 等支持 `SKILL.md` 的运行时）使用。

它不是 Lean 教程，而是一组**可复用操作契约**：一个命令行脚本 + 若干参考文档 + 一条证明工作流，让 Agent 不必每次手敲 elan/lake 命令、也不必重新摸索报错含义。

## 能力

| 子命令 | 作用 |
|---|---|
| `doctor` | 体检：平台 / CPU / 磁盘 / git / elan / lean / lake / 已装工具链 / 是否 ready |
| `install` | 装 elan（缺失时）+ 指定工具链，幂等 |
| `new` | 用官方模板建 Lake 工程，并写入样例证明 |
| `build` | 跑 `lake build`，统计 error / warning 行 |
| `check` | 编译单个 `.lean` 文件，有错时打印诊断 |
| `exec` | 打印 elan / lean / lake 绝对路径 |

## 目录结构

```text
lean4-skill/
├── lean4/                      # 技能本体，可整体拷进 .user_skills
│   ├── SKILL.md                # 唯一入口：何时用、三条执行路径、工程约定、验收标准
│   ├── scripts/lean4ctl.py     # 全部操作走这里，不手敲 elan/lake
│   ├── references/             # 按需加载的细节文档
│   │   ├── toolchain.md        # elan、多版本、PATH
│   │   ├── lake.md             # 工程布局、依赖、构建目标
│   │   ├── language.md         # 语法与常用 tactic
│   │   ├── troubleshooting.md  # 报错对照
│   │   └── build-from-source.md# 源码构建（WSL2 / msys2）
│   └── agents/proof-agent.md   # 非平凡证明的角色规范
├── examples/Lean4Demo/         # 可复现的示例工程（纯核心库，无 Mathlib）
├── CHANGELOG.md
└── .gitignore
```

## 安装

把 `lean4/` 整个目录复制到目标运行时的 `workspace/.user_skills/` 下（技能加载器只认该层目录）：

```bash
cp -r lean4 <你的 workspace>/.user_skills/lean4
```

Windows PowerShell：

```powershell
Copy-Item -Recurse .\lean4 "<workspace>\.user_skills\lean4"
```

## 快速开始

```bash
python lean4/scripts/lean4ctl.py doctor
python lean4/scripts/lean4ctl.py install --toolchain leanprover/lean4:stable
python lean4/scripts/lean4ctl.py new MyProof --dir .
python lean4/scripts/lean4ctl.py build ./MyProof
python lean4/scripts/lean4ctl.py check MyProof/Proofs.lean --project ./MyProof
```

预期：`doctor` 给出 `status: ready`；`build` 输出 `Build completed successfully` 且 `errors=0`。

## 环境要求

| 项 | 要求 |
|---|---|
| Python | ≥ 3.8（脚本只用标准库） |
| 网络 | 可访问 `elan.lean-lang.org`、`releases.lean-lang.org`、GitHub |
| 磁盘 | 工具链约 1.5 GB；建议 ≥ 5 GB 空闲 |
| 内存 | 常规证明 4 GB；Mathlib ≥ 16 GB |
| git | 需要（`lake` 拉依赖） |

## 已验证

- Lean `4.36.0` + elan `4.3.0`，Windows 10 / PowerShell 7。
- `examples/Lean4Demo`：`build` 18 jobs 全绿，`errors=0`、`warnings=0`、`sorry/admit = 0`。
- 示例覆盖：列表反转、复数乘法、向量点积、位移不等式、化学方程式原子守恒——刻意全部只用核心库，避免把 Mathlib 的数小时构建拖进日常练习。

## 已知边界

- Windows 原生 MSVC 无法从源码编译 Lean（上游 `CMakeLists.txt` 强制 Makefile 生成器），源码构建走 WSL2 / msys2。
- 核心库没有 `ring` / `linarith` / `norm_num` / `field_simp`；日常可用 `omega`（Nat/Int）、`grind`（有理数代数与线性推理）、`simp`、`decide`。需要重量级代数时再引 Mathlib。
- `scripts/quick_validate.py`（skill-creator 官方校验器）依赖 PyYAML；环境缺该包时改用等价的 frontmatter / 链接 / 空文件检查。

## 版本管理

- 分支：`main` 为唯一主线，功能改动走短分支后合并。
- 版本：语义化 `vMAJOR.MINOR.PATCH` 标签；技能行为或验收标准变化升 MINOR，破坏性接口变化升 MAJOR。
- 记录：每次发版同步更新 `CHANGELOG.md`。
- 当前版本：`v0.1.0`。
