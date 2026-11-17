# 报错对照表

按报错原文查。Lean 的诊断格式是 `文件:行:列: error: 消息`，先定位文件和行，再对照原因。

## 编译/证明类

| 报错 | 原因 | 处理 |
|---|---|---|
| `unknown identifier 'foo'` | 未 import、拼写错、命名空间未打开、`autoImplicit` 关闭后未声明 | 加 `import`；`open X`；`variable` 显式声明 |
| `unknown tactic` | tactic 不在当前环境 | `omega`/`simp`/`decide` 属核心；`ring`/`linarith`/`norm_num` 需 `import Mathlib` |
| `type mismatch` | 期望类型与实际类型不一致 | 看 `expected ... but is ...` 两行；加 coercion、`↑`、或改陈述 |
| `failed to synthesize instance` | 缺类型类实例 | 补 `deriving`、提供 `instance`、或 import 相应实例模块 |
| `unsolved goals` | tactic 没把目标证完 | 看剩余 goal；补 `omega`/`simp`/`exact`，或拆分 `have` |
| `Tactic 'rfl' failed` | 目标不是定义相等 | 换 `simp`/`omega`/`ring`；或先 `unfold` 再证 |
| `application type mismatch` | 函数参数类型/数量不对 | `#check f` 看签名；隐式参数用 `@f` 显式给 |
| `maximum recursion depth exceeded` | 定义展开失控 / 实例搜索循环 | 用 `simp only [...]` 限定；`set_option maxRecDepth 4000`（治标） |
| `declaration uses 'sorry'` | 有未完成的证明 | warning 不是 error，但验收不合格；grep `sorry` |
| `failed to prove termination` | 递归函数终止性未证 | 加 `termination_by`、`decreasing_by`，或换结构递归 |
| `invalid field notation` | 字段/方法不存在或类型不明 | 补类型注解，或用完整名 `Namespace.foo` |

## 工程/构建类

| 报错 | 原因 | 处理 |
|---|---|---|
| `bad import 'X.Y'` | 模块名与文件路径不匹配，或文件不在库目录 | 文件须在 `<包名>/...` 下，路径与模块名逐段对应 |
| `no such file or directory (error code: 4058)` | 引用了不存在的模块文件 | 同上；确认 import 的每个模块都有实体文件 |
| `some modules have bad imports or could not be read` | 上面的聚合报错 | 先修第一个被点名的模块 |
| `toolchain '...' is not installed` | `lean-toolchain` 指的版本本地没有 | `elan toolchain install <该版本>`，或改成本地已有版本 |
| `unknown package 'mathlib'` / 依赖解析失败 | `lake-manifest.json` 缺失或网络不通 | `lake update`；检查代理；确认 `require` 写法 |
| `could not resolve host` / 下载超时 | 网络/代理 | 设 `HTTP_PROXY`/`HTTPS_PROXY`；或预装工具链后离线构建 |
| `out of memory` / 构建被 kill | 并行过高 | `lake build -j 2`；关掉其他大内存进程 |
| `LEAN_PATH` 相关找不到模块 | 直接用了 `lean` 而不是工程环境 | 用 `lake env lean file.lean` |
| 构建成功但改动没生效 | 改的文件没被根模块 import | 把模块加入 import 链，或直接 `lake build <模块名>` |
| `Only makefile generators are supported` | 源码构建用了非 Makefile 生成器 | `cmake --preset release`；Windows 走 WSL2/msys2 |

## 环境/安装类

| 报错 | 原因 | 处理 |
|---|---|---|
| `elan: command not found` | PATH 未刷新或未安装 | 新开终端；或 `~/.elan/bin/elan`；或重跑 `install` |
| PowerShell 拒绝执行 `elan-init.ps1` | 执行策略 | `-ExecutionPolicy Bypass` |
| `could not canonicalize path '...\.elan\toolchains'` | Windows 告警 | 可忽略 |
| 中文路径/空格路径构建异常 | 部分工具对非 ASCII 路径敏感 | 工程放到纯 ASCII 路径（如 `C:\lean\proj`） |
| `lake` 在 cmd 里能用、在 IDE 里不能 | IDE 未继承 PATH | 重启 IDE；或在 IDE 设置里指定 `~/.elan/bin` |

## 排查顺序建议

1. `python scripts/lean4ctl.py doctor` —— 先排除环境问题（版本、PATH、工具链缺失）。
2. 单文件 `check` —— 缩小到一个文件，避免整包噪声。
3. 看第一个 error，不要被后续级联报错带偏（Lean 一个根因常引发十几条）。
4. 仍不解时 `#check` / `#print` 打印实际类型与定义，比猜快。
