# 从源码构建 leanprover/lean4

只在需要修改 Lean 本身（编译器、核心库、Lake、语言服务器）时使用。日常写证明走 elan 预编译工具链。

## 平台结论（先看这个）

| 平台 | 可行性 | 做法 |
|---|---|---|
| Linux | 官方支持 | 直接 cmake + make |
| macOS | 官方支持 | 同上，`nproc` 换成 `sysctl -n hw.logicalcpu` |
| Windows | **原生 MSVC 不可行** | 用 WSL2，或 msys2 的 mingw 环境 |
| Nix / NixOS | 支持 | 仓库根目录 `nix develop` 后按下面命令构建 |

原因：`CMakeLists.txt` 开头有硬检查——生成器必须匹配 `Makefiles`，否则直接 `FATAL_ERROR`。MSVC 默认生成 Visual Studio 工程，因此原生 Windows 构建必然失败。

## 依赖

- C++14 兼容编译器（官方 release 用 Clang）
- CMake ≥ 3.21
- GMP ≥ 6.3.0（低于此版本可能导致不健全结果；可用 `-DUSE_GMP=OFF` 走内置大数实现，安全但有性能损失）
- libuv、OpenSSL
- `make`、`git`、`curl`
- ccache（可选，强烈建议；Lean 会用来自动跳过重复编译）
- 资源：≥ 16 GB 内存、≥ 10 GB 磁盘，构建 30–60 分钟（8 核量级）

Ubuntu/Debian 一次装齐：

```bash
sudo apt-get update
sudo apt-get install -y build-essential cmake libgmp-dev libuv1-dev libssl-dev ccache git curl
```

WSL2 里同样按上面装，然后在 WSL 文件系统内克隆（不要放在 `/mnt/c`，跨文件系统构建极慢）。

msys2：按仓库内 `doc/make/msys2.md` 的包列表安装（该文件是权威版本），并在 MSYS2 MinGW shell 里构建，不要用普通 cmd。

## 构建命令

```bash
git clone https://github.com/leanprover/lean4
cd lean4

# 配置（产物在 build/release）
cmake --preset release

# 编译（stage0 → stage1）
make -C build/release -j$(nproc)          # macOS: -j$(sysctl -n hw.logicalcpu)
```

开发用 `cmake --preset dev-release`（保留调试符号，复用同一 `build/release` 目录）。可选 preset：`release`、`dev-release`、`debug`、`sandebug`、`relwithassert`。

产物：`build/release/stage1/bin/lean`、`lake`、`leanc`。**不要**在成功后跑 `cmake --install`。

常用 CMake 开关：

```bash
-DCMAKE_BUILD_TYPE=RELEASE|DEBUG|RELWITHDEBINFO|MINSIZEREL
-DCMAKE_C_COMPILER=clang  -DCMAKE_CXX_COMPILER=clang++
-DUSE_GMP=OFF             # 不依赖外部 GMP
-DFORCE_GMP=ON            # 强制用系统 GMP（不推荐）
```

加 `VERBOSE=1` 可打印实际编译命令：

```bash
make -C build/release -j$(nproc) VERBOSE=1
```

## 测试

```bash
# 全量测试
CTEST_PARALLEL_LEVEL="$(nproc)" CTEST_OUTPUT_ON_FAILURE=1 \
  make -C build/release -j "$(nproc)" test

# 单个/正则筛选
CTEST_PARALLEL_LEVEL="$(nproc)" CTEST_OUTPUT_ON_FAILURE=1 \
  make -C build/release -j "$(nproc)" test ARGS="-R 'grind_ematch'"

# 只重跑上次失败的
... test ARGS='--rerun-failed'
```

脱离 ctest 手跑单个用例：

```bash
tests/with_stage1_test_env.sh tests/elab/run_test.sh some_test.lean
tests/lake/run_test.sh tests/ltar
```

## 仓库结构

```
lean4/
├── CMakeLists.txt          # 顶层构建，强制 Makefile 生成器
├── CMakePresets.json       # release / dev-release / debug / sandebug ...
├── lean-toolchain          # 内容是 build/release/stage1（自举用）
├── src/
│   ├── Init/  Std/         # 核心库（Lean 源码）
│   ├── Lean/               # 编译器/elaborator/LSP 主体（Lean 源码）
│   ├── kernel/ runtime/    # C++ 内核与运行时
│   ├── library/ shell/ util/ bin/
│   ├── lake/               # Lake 源码
│   └── CMakeLists.txt
├── stage0/src/             # src 的快照，用于自举
├── tests/                  # 测试套件（ctest）
├── doc/                    # 开发文档：make/、dev/、examples/
└── script/                 # 发布、格式化、stage0 同步等脚本
```

构建是自举的：`stage0` 先用预编译二进制，`stage1` 用 stage0 编译 `src/`，产出正式工具链。

## 硬性规则

1. **不要手改 `stage0/`**：它是 `src/` 的快照。改 `src/` 后执行 `make update-stage0` 同步。
2. **不要手删 `build/`、`stage0/`、`stage1/`**。构建坏了先看报错，需要清理时征询用户。
3. 提交前必须「干净构建 + 相关测试通过」双确认，不能只看编译过。
4. `src/Lean/`、`src/Std/`、`src/lake/Lake/` 下的文件需要 `module` + `prelude` 头，`prelude` 之后所有 `Init.*` 都要显式 import。`tests/`、`script/` 下只需 `module`。
5. 新增文件需要版权头，年份用 `date +%Y` 现取。

## 构建排错

| 现象 | 处理 |
|---|---|
| `Only makefile generators are supported` | 换了生成器。用 `cmake --preset release`，别用 VS/Ninja 生成器 |
| `gmp.h not found` | 装 `libgmp-dev`；NixOS 上多半是 store 路径失效，跑 `script/refresh-cmake-deps.sh` |
| `ccache` 只读文件系统报错 | 设 `CCACHE_READONLY`、`CCACHE_TEMPDIR`，不要直接禁用 |
| 编译 OOM / 卡死 | 降并行：`make -C build/release -j4` |
| 改了 C++ 但行为没变 | 增量没触发，确认在 `src/` 改的；stage0 需 `make update-stage0` |
| 构建成功后 IDE 报错 | LSP 诊断滞后，以命令行结果为准 |
