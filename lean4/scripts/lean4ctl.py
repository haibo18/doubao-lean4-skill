#!/usr/bin/env python3
"""Lean 4 control CLI: bootstrap elan, scaffold projects, compile and verify .lean files.

Subcommands:
  doctor   Inspect the local toolchain environment.
  install  Install elan (if missing) and a Lean toolchain.
  new      Create a Lake project from an official template.
  build    Run `lake build` in a project and report diagnostics.
  check    Compile one .lean file and report errors.
  exec     Print the resolved path of elan/lean/lake for scripting.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

EXE = ".exe" if os.name == "nt" else ""
ELAN_HOME = Path(os.environ.get("ELAN_HOME") or (Path.home() / ".elan"))
ELAN = ELAN_HOME / "bin" / f"elan{EXE}"
LEAN = ELAN_HOME / "bin" / f"lean{EXE}"
LAKE = ELAN_HOME / "bin" / f"lake{EXE}"

DEFAULT_TOOLCHAIN = "leanprover/lean4:stable"
ELAN_INIT_PS1 = "https://elan.lean-lang.org/elan-init.ps1"
ELAN_INIT_SH = "https://elan.lean-lang.org/elan-init.sh"

SAMPLE_PROOFS = """\
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
"""


def child_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PATH"] = str(ELAN_HOME / "bin") + os.pathsep + env.get("PATH", "")
    return env


def run(cmd: list[str], cwd: Path | None = None, timeout: int | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        env=child_env(),
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=timeout,
    )


def tool_version(path: Path, args: list[str] | None = None) -> str | None:
    if not path.exists():
        return None
    try:
        out = run([str(path)] + (args or ["--version"]), timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    text = (out.stdout or out.stderr).strip().splitlines()
    return text[0] if text else "unknown"


def require_elan() -> bool:
    if ELAN.exists():
        return True
    print(f"[missing] elan not found at {ELAN}", file=sys.stderr)
    print("Run: python lean4ctl.py install", file=sys.stderr)
    return False


def installed_toolchains() -> list[str]:
    if not ELAN.exists():
        return []
    out = run([str(ELAN), "toolchain", "list"], timeout=120)
    lines = []
    for line in (out.stdout or "").splitlines():
        line = line.strip()
        if not line or line.startswith(("info:", "warning:")):
            continue
        lines.append(line.split(" ", 1)[-1] if " " in line else line)
    return lines


def parse_errors(text: str) -> list[str]:
    """Collect Lean diagnostic lines that carry an error marker."""
    hits = [ln.rstrip() for ln in text.splitlines() if re.search(r"\berror\b", ln, re.IGNORECASE)]
    warnings = [ln.rstrip() for ln in text.splitlines() if re.search(r"\bwarning\b", ln, re.IGNORECASE)]
    return hits, warnings


def cmd_doctor(_: argparse.Namespace) -> int:
    print("== Lean 4 environment ==")
    print(f"platform        : {sys.platform} / python {sys.version.split()[0]}")
    print(f"cpu_cores       : {os.cpu_count()}")
    try:
        free_gb = shutil.disk_usage(Path.cwd()).free / 1024**3
        print(f"disk_free_gb    : {free_gb:.1f}")
    except OSError:
        pass
    print(f"elan_home       : {ELAN_HOME}")
    print(f"git             : {tool_version(Path(shutil.which('git') or 'git')) or 'not found'}")
    for name, path in (("elan", ELAN), ("lean", LEAN), ("lake", LAKE)):
        version = tool_version(path)
        print(f"{name:<15} : {version or 'not installed'}")
    chains = installed_toolchains()
    print(f"toolchains      : {', '.join(chains) if chains else 'none'}")
    if ELAN.exists():
        show = run([str(ELAN), "show"], timeout=120)
        active = [ln.strip() for ln in (show.stdout or "").splitlines() if "active toolchain" in ln.lower()]
        if active:
            print(f"active          : {active[0].split(':')[-1].strip()}")
    ok = all(p.exists() for p in (ELAN, LEAN, LAKE))
    print(f"status          : {'ready' if ok else 'incomplete - run: python lean4ctl.py install'}")
    return 0 if ok else 1


def bootstrap_elan(toolchain: str) -> bool:
    print(f"[install] bootstrapping elan (default toolchain: {toolchain})")
    with tempfile.TemporaryDirectory(prefix="lean4ctl-") as tmp:
        tmp_dir = Path(tmp)
        if os.name == "nt":
            script = tmp_dir / "elan-init.ps1"
            urllib.request.urlretrieve(ELAN_INIT_PS1, script)
            shell = shutil.which("powershell") or "powershell"
            code = run([shell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script),
                        "-NoPrompt", "$true", "-DefaultToolchain", toolchain], timeout=1800)
        else:
            script = tmp_dir / "elan-init.sh"
            urllib.request.urlretrieve(ELAN_INIT_SH, script)
            code = run(["sh", str(script), "-y", "--default-toolchain", toolchain], timeout=1800)
    if code.returncode != 0:
        print(code.stdout, code.stderr, sep="\n", file=sys.stderr)
        return False
    return ELAN.exists()


def cmd_install(args: argparse.Namespace) -> int:
    toolchain = args.toolchain
    if not ELAN.exists() and not bootstrap_elan(toolchain):
        print("[fail] elan bootstrap failed; see messages above", file=sys.stderr)
        return 1
    print(f"[install] elan: {tool_version(ELAN)}")
    print(f"[install] ensuring toolchain {toolchain}")
    out = run([str(ELAN), "toolchain", "install", toolchain], timeout=3600)
    if out.returncode != 0:
        print(out.stdout, out.stderr, sep="\n", file=sys.stderr)
        print("[fail] toolchain install failed (check network / proxy)", file=sys.stderr)
        return 1
    print(f"[install] lean: {tool_version(LEAN)}")
    print(f"[install] lake: {tool_version(LAKE)}")
    print(f"[hint] add {ELAN_HOME / 'bin'} to PATH, or call the binaries by absolute path.")
    return 0


def lib_name_from_lakefile(target: Path, fallback: str) -> str:
    """Read the [[lean_lib]] name from lakefile.toml; Lake may rewrite the module name."""
    lakefile = target / "lakefile.toml"
    if lakefile.exists():
        text = lakefile.read_text(encoding="utf-8", errors="replace")
        block = re.search(r"\[\[lean_lib\]\](.*?)(?=\n\[\[|\Z)", text, re.S)
        if block:
            name = re.search(r'name\s*=\s*"([^"]+)"', block.group(1))
            if name:
                return name.group(1)
    return fallback


def cmd_new(args: argparse.Namespace) -> int:
    if not require_elan():
        return 1
    if not re.match(r"^[A-Za-z_][A-Za-z0-9_']*$", args.name):
        print(f"[warn] '{args.name}' is not a plain Lean identifier; "
              "Lake may rename the module (e.g. 'my-proj' -> 'MyProj'). Prefer letters/digits/underscore.")
    parent = Path(args.dir).resolve()
    parent.mkdir(parents=True, exist_ok=True)
    target = parent / args.name
    if target.exists() and any(target.iterdir()):
        print(f"[fail] {target} already exists and is not empty; choose another name or delete it",
              file=sys.stderr)
        return 1
    cmd = [str(LAKE), "new", args.name] + ([args.template] if args.template else [])
    out = run(cmd, cwd=parent, timeout=600)
    if out.returncode != 0:
        print(out.stdout, out.stderr, sep="\n", file=sys.stderr)
        return 1
    if args.toolchain:
        (target / "lean-toolchain").write_text(args.toolchain + "\n", encoding="utf-8")
    if args.with_sample:
        lib_name = lib_name_from_lakefile(target, args.name)
        lib_dir = target / lib_name
        sample_dir = lib_dir if lib_dir.is_dir() else target
        (sample_dir / "Proofs.lean").write_text(SAMPLE_PROOFS, encoding="utf-8")
        root_mod = target / f"{lib_name}.lean"
        if root_mod.exists():
            text = root_mod.read_text(encoding="utf-8")
            if f"{lib_name}.Proofs" not in text:
                root_mod.write_text(text.rstrip() + f"\nimport {lib_name}.Proofs\n", encoding="utf-8")
    print(f"[ok] project created: {target}")
    print(f"[ok] toolchain file  : {(target / 'lean-toolchain').read_text(encoding='utf-8').strip()}")
    print(f"[next] cd {target} && lake build")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    if not require_elan():
        return 1
    project = Path(args.project).resolve()
    if not (project / "lakefile.toml").exists() and not (project / "lakefile.lean").exists():
        print(f"[fail] no lakefile in {project}", file=sys.stderr)
        return 1
    cmd = [str(LAKE), "build"] + list(args.targets)
    out = run(cmd, cwd=project, timeout=args.timeout)
    text = (out.stdout or "") + (out.stderr or "")
    errors, warnings = parse_errors(text)
    print(text.strip()[-4000:])
    print(f"[result] exit={out.returncode} errors={len(errors)} warnings={len(warnings)}")
    return out.returncode


def cmd_check(args: argparse.Namespace) -> int:
    if not require_elan():
        return 1
    path = Path(args.file).resolve()
    if not path.exists():
        print(f"[fail] file not found: {path}", file=sys.stderr)
        return 1
    project = Path(args.project).resolve() if args.project else None
    if project and (project / "lakefile.toml").exists():
        cmd = [str(LAKE), "env", "lean", str(path)]
        cwd = project
    else:
        cmd = [str(LEAN), str(path)]
        cwd = path.parent
    out = run(cmd, cwd=cwd, timeout=args.timeout)
    text = (out.stdout or "") + (out.stderr or "")
    errors, warnings = parse_errors(text)
    if text.strip():
        print(text.strip()[-4000:])
    if out.returncode == 0:
        print(f"[ok] {path.name}: no errors ({len(warnings)} warnings)")
    else:
        print(f"[fail] {path.name}: {len(errors)} error line(s)", file=sys.stderr)
        for line in errors[:10]:
            print(f"  {line}", file=sys.stderr)
    return out.returncode


def cmd_exec(_: argparse.Namespace) -> int:
    for name, path in (("elan", ELAN), ("lean", LEAN), ("lake", LAKE)):
        print(f"{name}={path}" if path.exists() else f"{name}=missing")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Lean 4 toolchain and project helper")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("doctor", help="inspect the environment").set_defaults(func=cmd_doctor)
    sub.add_parser("exec", help="print resolved binary paths").set_defaults(func=cmd_exec)

    p_install = sub.add_parser("install", help="install elan and a Lean toolchain")
    p_install.add_argument("--toolchain", default=DEFAULT_TOOLCHAIN)
    p_install.set_defaults(func=cmd_install)

    p_new = sub.add_parser("new", help="create a Lake project")
    p_new.add_argument("name", help="project / package name (Lean identifier)")
    p_new.add_argument("--dir", default=".", help="parent directory")
    p_new.add_argument("--template", choices=["lib", "std", "exe", "math", "math-lax"],
                       default="lib", help="official lake template")
    p_new.add_argument("--toolchain", help="pin lean-toolchain to this value, e.g. leanprover/lean4:stable")
    p_new.add_argument("--no-sample", dest="with_sample", action="store_false",
                       help="skip the Proofs.lean smoke-test file")
    p_new.set_defaults(func=cmd_new, with_sample=True)

    p_build = sub.add_parser("build", help="run lake build")
    p_build.add_argument("project", nargs="?", default=".")
    p_build.add_argument("targets", nargs="*", help="optional build targets")
    p_build.add_argument("--timeout", type=int, default=1800)
    p_build.set_defaults(func=cmd_build)

    p_check = sub.add_parser("check", help="compile a single .lean file")
    p_check.add_argument("file")
    p_check.add_argument("--project", help="project root for `lake env`")
    p_check.add_argument("--timeout", type=int, default=900)
    p_check.set_defaults(func=cmd_check)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
