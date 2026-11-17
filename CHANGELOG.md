# Changelog

遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 与[语义化版本](https://semver.org/lang/zh-CN/)。

## [v0.1.0] - 2026-11-18

### Added

- `SKILL.md`：三条执行路径（elan 预编译 / 体检 / 源码构建）、环境要求表、Lake 工程结构约定、6 步标准流程、4 条验收标准。
- `scripts/lean4ctl.py`：`doctor` / `install` / `new` / `build` / `check` / `exec` 六个子命令；自动把 `~/.elan/bin` 注入子进程 PATH，`install` 幂等。
- `references/`：`toolchain.md`、`lake.md`、`language.md`、`troubleshooting.md`、`build-from-source.md`。
- `agents/proof-agent.md`：非平凡证明的分解与收敛规范。
- `examples/Lean4Demo`：纯核心库示例工程（列表反转、复数平方、向量点积、位移不等式、化学方程式原子守恒），`lake build` 18 jobs、0 error、0 sorry。

### Fixed

- 模板把库模块放在 `<包>/<包>/` 子目录，样例文件落到工程根目录会触发 `bad import` / `no such file (4058)`；`new` 改为按物理路径写文件，`build` 从 `lakefile.toml` 解析 `[[lean_lib]] name`，兼容包名被 Lake 改写（`lean4-demo` → `Lean4Demo`）。
- 样例证明原用 `rfl` 无法证明 `([] ++ ys).length = [].length + ys.length`，改为 `simp` + `omega`。

### Known limitations

- Windows 原生 MSVC 不支持源码构建 Lean，需 WSL2 / msys2。
- 核心库无 `ring` / `linarith` / `norm_num` / `field_simp`，仅 `omega` / `grind` / `simp` / `decide` 可用。
