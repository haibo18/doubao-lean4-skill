# 工具链管理（elan）

`elan` 是 Lean 的版本管理器，类似 rustup：把 `lean`/`lake` 放到 PATH，按当前目录的 `lean-toolchain` 自动选择并下载对应版本。不要手动下载 Lean 压缩包解压到 PATH，那样多工程必然版本冲突。

## 目录约定

| 路径 | 内容 |
|---|---|
| `~/.elan/bin` | `elan`、`lean`、`lake` 的 shim |
| `~/.elan/toolchains/` | 实际工具链，目录名形如 `leanprover--lean4---v4.36.0` |
| `~/.elan/settings.toml` | 默认工具链等设置 |
| `<工程>/lean-toolchain` | 工程级版本锁定，优先级高于默认 |

Windows 下 `~` 为 `%USERPROFILE%`；可用环境变量 `ELAN_HOME` 改根目录。

## 常用命令

```bash
elan --version                 # 版本
elan show                      # 已装工具链 + 当前生效的（含 override 来源）
elan toolchain list            # 只列已装
elan toolchain install stable  # 装 stable（也接受 leanprover/lean4:v4.36.0）
elan toolchain install leanprover/lean4:v4.35.0
elan default stable            # 设默认（不带 override 的目录生效）
elan toolchain uninstall <名>
elan which lean                # 解析出实际二进制路径
elan self update               # 升级 elan 自身
elan self uninstall            # 卸载（会还原 PATH 修改）
```

`elan show` 里 `active toolchain` 后面会标注 `(overridden by '<路径>/lean-toolchain')`，排版本问题时先看这一行。

## 版本选择规则

1. 当前目录（或祖先目录）有 `lean-toolchain` → 用它；
2. 否则用 `elan default` 设的默认工具链；
3. 都没有 → elan 报错，提示无默认工具链。

`lean-toolchain` 内容是一行工具链标识，例如：

```
leanprover/lean4:v4.36.0
leanprover/lean4:stable
leanprover/lean4:nightly-2026-11-01
```

## 国内网络与离线

官方源是 `releases.lean-lang.org`，下载走 HTTPS，通常可用；若超时：

- 设置代理后再跑 elan/lake：`HTTP_PROXY`、`HTTPS_PROXY`（Windows 用 `$env:HTTP_PROXY=...`）。
- 只装一次、之后离线：提前 `elan toolchain install <目标版本>`，工程里 `lean-toolchain` 固定到该版本，`lake build` 不再联网（除非工程有 git 依赖）。
- 完全离线且没有预装工具链：本技能不适用，需要用户提供内网镜像或离线包。

## 常见坑

- **装了但命令找不到**：安装脚本改的是用户 PATH，已打开的终端不会刷新。新开终端，或在本会话直接用绝对路径 `~/.elan/bin/lean`；本技能的 `lean4ctl.py` 已自动注入 PATH。
- **多工程版本打架**：永远用工程内 `lean-toolchain` 锁定，不要在全局 `elan default` 上反复切换。
- **`elan-init.ps1` 被策略拦截**：用 `powershell -NoProfile -ExecutionPolicy Bypass -File elan-init.ps1 -NoPrompt $true`。
- **`elan` 报 `could not canonicalize path`**：Windows 上偶发告警，不影响使用，可忽略。
