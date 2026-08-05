#!/usr/bin/env python3
"""C3 readiness Batch 3 — supplemental-pilot six-case dual-arm queue.

Frozen membership: data/external_slice/BATCH3_MEMBERSHIP.json
Proposed verdicts only in readiness_batch3.json (sheet A2 stays PENDING).
Stops after handoff for Gate A1d. Does not start C4/labelling/freeze/prediction/detection.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import platform
import re
import shlex
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def _load_batch3_helpers():
    path = Path(__file__).resolve().parent / "batch3_a1d_r1.py"
    spec = importlib.util.spec_from_file_location("batch3_a1d_r1", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_helpers = _load_batch3_helpers()
NUMERIC_BLAS_CASES = _helpers.NUMERIC_BLAS_CASES
aggregate_formal_verdict = _helpers.aggregate_formal_verdict
assert_arm_input_parity = _helpers.assert_arm_input_parity
assert_membership_byte_identical = _helpers.assert_membership_byte_identical
discover_blas_lapack_provider = _helpers.discover_blas_lapack_provider
load_execution_matrix = _helpers.load_execution_matrix
reconstruct_formal_per_seed_from_artifacts = (
    _helpers.reconstruct_formal_per_seed_from_artifacts
)
save_execution_outputs = _helpers.save_execution_outputs

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MATRIX = ROOT / "data" / "external_slice" / "BATCH3_EXECUTION_MATRIX.json"
WORK = Path(os.environ.get("C3_BATCH3_WORK", "/tmp/c3_batch3"))
REPRO_ROOT = ROOT / "data" / "external_slice" / "reproduction"
TRIG_ROOT = ROOT / "data" / "external_slice" / "reproducers"
DEFAULT_MEMBERSHIP = ROOT / "data" / "external_slice" / "BATCH3_MEMBERSHIP.json"
DEFAULT_SHEET = ROOT / "data" / "external_slice" / "admission_sheet.csv"
# Prefer a clean host interpreter; PATH may be polluted by prior venvs.
HOST_PY = Path(os.environ.get("C3_HOST_PY", "/usr/bin/python3"))
if not HOST_PY.is_file():
    HOST_PY = Path(sys.executable)
PY39 = Path(os.environ.get("C3_PY39", "/tmp/c3_batch1/work/python39/install/bin/python3.9"))
TOKEN = os.environ.get("github_token") or os.environ.get("GITHUB_TOKEN") or ""
REDACT = "<REDACTED_GITHUB_TOKEN>"
BUILD_TIMEOUT = int(os.environ.get("C3_BATCH3_BUILD_TIMEOUT", "3600"))
NJOBS = str(min(4, os.cpu_count() or 2))

RUNBOOK_RESERVED_PATTERN = (
    r"(?i)(^|[^[:alnum:]_])(C\x45|O\x53|H\x50|T\x46|S\x49|f\x69ber|strat\x75m)"
    r"([^[:alnum:]_]|$)"
)
TOKEN_SCAN_PATTERN = (
    r"ghp_[A-Za-z0-9]{20,}|"
    r"github_pat_[A-Za-z0-9_]{20,}|"
    r"Bearer [A-Za-z0-9][A-Za-z0-9._-]{15,}"
)


class CommandLog:
    def __init__(self) -> None:
        self.entries: list[dict] = []

    def run(
        self,
        command: list[str] | str,
        *,
        cwd: Path | None = None,
        env: dict | None = None,
        label: str = "",
        check: bool = True,
        allow_exit: set[int] | None = None,
        timeout: int | None = None,
    ) -> subprocess.CompletedProcess:
        if isinstance(command, str):
            cmd_display = command
            shell = True
            cmd_arg: list[str] | str = command
        else:
            cmd_display = subprocess.list2cmdline(command)
            shell = False
            cmd_arg = command
        if TOKEN:
            cmd_display = cmd_display.replace(TOKEN, REDACT)
        merged = os.environ.copy()
        if env:
            merged.update(env)
        try:
            proc = subprocess.run(
                cmd_arg,
                cwd=str(cwd) if cwd else None,
                env=merged,
                text=True,
                capture_output=True,
                shell=shell,
                check=False,
                timeout=timeout,
            )
        except FileNotFoundError as exc:
            proc = subprocess.CompletedProcess(cmd_arg, 127, "", f"FileNotFoundError: {exc}")
        except subprocess.TimeoutExpired as exc:
            proc = subprocess.CompletedProcess(
                cmd_arg,
                124,
                (exc.stdout or "") if isinstance(exc.stdout, str) else "",
                ((exc.stderr or "") if isinstance(exc.stderr, str) else "")
                + f"\nTIMEOUT after {timeout}s",
            )
        entry = {
            "label": label,
            "command": cmd_display,
            "cwd": str(cwd) if cwd else str(Path.cwd()),
            "exit_code": proc.returncode,
            "stdout_tail": scrub((proc.stdout or "")[-4000:]),
            "stderr_tail": scrub((proc.stderr or "")[-4000:]),
            "timeout_s": timeout,
        }
        self.entries.append(entry)
        print(f"[{label}] exit={proc.returncode}: {cmd_display[:180]}", flush=True)
        allowed = allow_exit or ({0} if check else {proc.returncode})
        if check and proc.returncode not in allowed:
            raise RuntimeError(
                f"command failed ({proc.returncode}): {cmd_display}\n"
                f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
            )
        return proc


def scrub(text: str) -> str:
    if not text:
        return text
    out = text
    if TOKEN:
        out = out.replace(TOKEN, REDACT)
    out = re.sub(r"Bearer\s+ghp_[A-Za-z0-9]+", f"Bearer {REDACT}", out)
    out = re.sub(r"Bearer\s+github_pat_[A-Za-z0-9_]+", f"Bearer {REDACT}", out)
    out = re.sub(r"ghp_[A-Za-z0-9]{20,}", REDACT, out)
    out = re.sub(r"github_pat_[A-Za-z0-9_]{20,}", REDACT, out)
    return out


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_tree(root: Path) -> str:
    h = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix().encode()
        h.update(rel)
        h.update(b"\0")
        h.update(sha256_file(path).encode())
        h.update(b"\0")
    return h.hexdigest()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def tool_versions() -> dict:
    out = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "machine": platform.machine(),
    }
    for name, cmd in (("gcc", ["gcc", "--version"]), ("g++", ["g++", "--version"])):
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
            out[name] = ((proc.stdout or proc.stderr or "").splitlines() or [""])[0]
        except FileNotFoundError:
            out[name] = "missing"
    out["python39"] = str(PY39) if PY39.is_file() else "missing"
    return out


def parse_artifact_name(filename: str) -> tuple[str, str] | None:
    lower = filename.lower()
    if lower.endswith(".whl"):
        parts = filename[:-4].split("-")
        return parts[0].replace("_", "-"), parts[1]
    if lower.endswith(".tar.gz"):
        stem = filename[: -len(".tar.gz")]
        name, ver = stem.rsplit("-", 1)
        return name.replace("_", "-"), ver
    if lower.endswith(".zip"):
        stem = filename[: -len(".zip")]
        name, ver = stem.rsplit("-", 1)
        return name.replace("_", "-"), ver
    return None


def pip_hash_lock(
    python: Path,
    packages: list[str],
    out: Path,
    log: CommandLog,
    label: str,
    *,
    extra_index: list[str] | None = None,
) -> dict:
    dl = out.parent / f".download-{out.stem}"
    if dl.exists():
        shutil.rmtree(dl)
    dl.mkdir(parents=True)
    cmd = [str(python), "-m", "pip", "download", "-d", str(dl), *packages]
    if extra_index:
        cmd[4:4] = extra_index
    log.run(cmd, label=f"{label}:pip-download", timeout=BUILD_TIMEOUT)
    artifact_hashes: dict[str, str] = {}
    req_to_hash: dict[str, str] = {}
    for path in sorted(p for p in dl.iterdir() if p.is_file()):
        parsed = parse_artifact_name(path.name)
        if parsed is None:
            continue
        name, ver = parsed
        digest = sha256_file(path)
        artifact_hashes[path.name] = digest
        req_to_hash[f"{name}=={ver}"] = digest
    if not req_to_hash:
        raise RuntimeError(f"no hashed artifacts for {packages}")
    lines = [
        f"# Hash-locked requirements for C3 Batch 3 ({label})",
        f"# python={python}",
        f"# root_packages={packages}",
    ]
    ordered: list[str] = []
    for pref in packages:
        base = pref.split("==", 1)[0].replace("_", "-").lower()
        for r in req_to_hash:
            if r.split("==", 1)[0].lower() == base and r not in ordered:
                ordered.append(r)
                break
    for r in sorted(req_to_hash):
        if r not in ordered:
            ordered.append(r)
    for req in ordered:
        lines.append(f"{req} \\")
        lines.append(f"    --hash=sha256:{req_to_hash[req]}")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    shutil.rmtree(dl, ignore_errors=True)
    return {"artifacts": artifact_hashes, "resolved_requirements": ordered}


def github_archive_url(repo: str, sha: str) -> str:
    return f"https://github.com/{repo}/archive/{sha}.tar.gz"


def download(url: str, dest: Path, log: CommandLog, label: str) -> str:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and dest.stat().st_size > 0:
        digest = sha256_file(dest)
        log.entries.append(
            {
                "label": f"{label}:cache-hit",
                "command": f"# reuse {dest} sha256={digest}",
                "cwd": str(ROOT),
                "exit_code": 0,
                "stdout_tail": digest,
                "stderr_tail": "",
                "timeout_s": None,
            }
        )
        return digest
    headers: list[str] = []
    if TOKEN and "github.com" in url:
        headers = ["-H", f"Authorization: Bearer {TOKEN}"]
    log.run(["curl", "-fsSL", "-L", *headers, "-o", str(dest), url], label=label, timeout=600)
    return sha256_file(dest)


def extract_archive(archive: Path, dest: Path, log: CommandLog, label: str) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    log.run(
        ["tar", "-xzf", str(archive), "--strip-components=1", "-C", str(dest)],
        label=label,
    )


def materialize_exact_source(
    *,
    repo: str,
    sha: str,
    dest: Path,
    work: Path,
    arm: str,
    nid: str,
    mode: str,
    log: CommandLog,
) -> dict:
    """Materialize exact SHA source for dual-arm install.

    Modes:
      - archive: GitHub archive only (default)
      - git_checkout: blobless clone + tags + submodule init (versioneer / SVML)
      - archive_with_submodules: archive tree + submodule overlay from git clone
    """
    meta: dict = {"sha": sha, "mode": mode, "repo": repo}
    if mode == "git_checkout":
        clone = work / f"{arm}-git"
        if clone.exists():
            shutil.rmtree(clone)
        log.run(
            [
                "git",
                "clone",
                "--filter=blob:none",
                f"https://github.com/{repo}.git",
                str(clone),
            ],
            label=f"{nid}:{arm}:git-clone",
            timeout=600,
        )
        log.run(
            ["git", "checkout", "--detach", sha],
            cwd=clone,
            label=f"{nid}:{arm}:git-checkout",
        )
        head = log.run(
            ["git", "rev-parse", "HEAD"],
            cwd=clone,
            label=f"{nid}:{arm}:git-rev-parse",
        )
        got = head.stdout.strip()
        if got != sha:
            raise RuntimeError(f"{nid} {arm} checkout mismatch: {got} != {sha}")
        log.run(
            ["git", "fetch", "--tags", "origin"],
            cwd=clone,
            label=f"{nid}:{arm}:git-fetch-tags",
            check=False,
            timeout=600,
        )
        log.run(
            ["git", "submodule", "update", "--init", "--depth", "1"],
            cwd=clone,
            label=f"{nid}:{arm}:git-submodule-update",
            check=False,
            timeout=600,
        )
        status = log.run(
            ["git", "submodule", "status"],
            cwd=clone,
            label=f"{nid}:{arm}:git-submodule-status",
            check=False,
        )
        if dest.exists():
            shutil.rmtree(dest)
        # Keep .git so versioneer / setuptools_scm can resolve versions.
        shutil.copytree(clone, dest, symlinks=True)
        meta.update(
            {
                "source_tree_sha256": sha256_tree(dest),
                "submodule_status": (status.stdout or "").strip().splitlines(),
                "includes_dot_git": True,
            }
        )
        return meta

    # archive (+ optional submodule overlay)
    arch = work / f"{arm}.tar.gz"
    digest = download(
        github_archive_url(repo, sha),
        arch,
        log,
        f"{nid}:{arm}:download-archive",
    )
    extract_archive(arch, dest, log, f"{nid}:{arm}:extract-archive")
    meta["archive_sha256"] = digest

    if mode == "archive_with_submodules":
        clone = work / f"{arm}-git-sub"
        if clone.exists():
            shutil.rmtree(clone)
        log.run(
            [
                "git",
                "clone",
                "--filter=blob:none",
                f"https://github.com/{repo}.git",
                str(clone),
            ],
            label=f"{nid}:{arm}:git-clone-for-submodules",
            timeout=600,
        )
        log.run(
            ["git", "checkout", "--detach", sha],
            cwd=clone,
            label=f"{nid}:{arm}:git-checkout-for-submodules",
        )
        log.run(
            ["git", "submodule", "update", "--init", "--recursive", "--depth", "1"],
            cwd=clone,
            label=f"{nid}:{arm}:git-submodule-update",
            timeout=900,
        )
        status = log.run(
            ["git", "submodule", "status", "--recursive"],
            cwd=clone,
            label=f"{nid}:{arm}:git-submodule-status",
            check=False,
        )
        for line in (status.stdout or "").strip().splitlines():
            parts = line.strip().lstrip("+-U ").split()
            if len(parts) < 2:
                continue
            sub_path = parts[1]
            src_sub = clone / sub_path
            dst_sub = dest / sub_path
            if not src_sub.exists():
                continue
            if dst_sub.exists():
                shutil.rmtree(dst_sub)
            shutil.copytree(src_sub, dst_sub, symlinks=True)
        meta["submodule_status"] = (status.stdout or "").strip().splitlines()
        meta["includes_submodules"] = True

    meta["source_tree_sha256"] = sha256_tree(dest)
    return meta


def choose_python(nid: str) -> Path:
    # sklearn 1.3-era and numpy 1.24-era SHAs are not Python 3.12-ready.
    if nid in {"EXT-numpy-01", "EXT-scikit-learn-01", "EXT-statsmodels-03"} and PY39.is_file():
        return PY39
    return HOST_PY


def finalize_case(
    *,
    member: dict,
    log_slice: list[dict],
    buggy_holds: bool | None,
    fixed_holds: bool | None,
    trigger_exits: dict,
    failure_stage: str | None,
    failure_detail: str | None,
    route: str,
    source_hashes: dict | None = None,
    seed: int,
    extra_env: dict | None = None,
) -> dict:
    nid = member["neutral_id"]
    case_dir = REPRO_ROOT / nid
    case_dir.mkdir(parents=True, exist_ok=True)
    locks = case_dir / "locks"
    locks.mkdir(parents=True, exist_ok=True)

    contrast = (
        buggy_holds is False
        and fixed_holds is True
        and trigger_exits.get("buggy") == 1
        and trigger_exits.get("fixed") == 0
    )
    if failure_stage:
        proposed = "REPRO_FAILED"
    elif contrast:
        proposed = "PASS"
    else:
        proposed = "REPRO_FAILED"
        failure_stage = failure_stage or "contrast"
        failure_detail = failure_detail or (
            f"buggy_holds={buggy_holds} fixed_holds={fixed_holds} exits={trigger_exits}"
        )

    scrubbed = []
    for e in log_slice:
        scrubbed.append(
            {
                **e,
                "command": scrub(e.get("command", "")),
                "stdout_tail": scrub(e.get("stdout_tail", "")),
                "stderr_tail": scrub(e.get("stderr_tail", "")),
            }
        )
    write_json(case_dir / "COMMANDS.json", {"commands": scrubbed})
    write_json(
        locks / "BUILD_TOOLS.json",
        {"captured_at": datetime.now(timezone.utc).isoformat(), "tools": tool_versions()},
    )
    if source_hashes:
        write_json(locks / "SOURCE_HASHES.json", source_hashes)

    env = {
        "neutral_id": nid,
        "batch": 3,
        "route": route,
        "repo": member["repo"],
        "issue_url": member["issue_url"],
        "buggy_sha": member["buggy_sha"],
        "fixed_sha": member["fixed_sha"],
        "seed": seed,
        "platform": tool_versions(),
        "proposed_crit_dual_arm_repro": proposed,
        "sheet_crit_dual_arm_repro_unchanged": "PENDING",
        "failure_stage": failure_stage,
        "failure_detail": failure_detail,
        "dual_arm_contrast": bool(contrast),
        "trigger_exit_codes": trigger_exits,
        "cohort": "supplemental-pilot",
    }
    if extra_env:
        env.update(extra_env)
    write_json(case_dir / "environment.json", env)

    for arm, holds in (("buggy", buggy_holds), ("fixed", fixed_holds)):
        path = case_dir / f"{arm}.json"
        if not path.is_file():
            write_json(
                path,
                {
                    "neutral_id": nid,
                    "seed": seed,
                    "arm": arm,
                    "property_holds": holds,
                    "exit_status": None if holds is None else (0 if holds else 1),
                    "failure_stage": failure_stage,
                    "failure_detail": failure_detail,
                },
            )

    stdout_parts = []
    stderr_parts = []
    for arm in ("buggy", "fixed"):
        for kind, parts in (("stdout", stdout_parts), ("stderr", stderr_parts)):
            p = case_dir / f"{arm}.{kind}.txt"
            if p.is_file():
                parts.append(
                    f"=== {arm} {kind} ===\n"
                    + scrub(p.read_text(encoding="utf-8", errors="replace"))
                )
    (case_dir / "stdout.log").write_text("\n".join(stdout_parts) + "\n", encoding="utf-8")
    (case_dir / "stderr.log").write_text("\n".join(stderr_parts) + "\n", encoding="utf-8")

    out = {
        "neutral_id": nid,
        "repo": member["repo"],
        "issue_url": member["issue_url"],
        "buggy_sha": member["buggy_sha"],
        "fixed_sha": member["fixed_sha"],
        "seed": seed,
        "trigger": str((TRIG_ROOT / f"{nid}.py").relative_to(ROOT)),
        "artifact_dir": str(case_dir.relative_to(ROOT)),
        "locks_dir": str(locks.relative_to(ROOT)),
        "command_count": len(scrubbed),
        "buggy_property_holds": buggy_holds,
        "fixed_property_holds": fixed_holds,
        "dual_arm_contrast": bool(contrast),
        "trigger_exit_codes": trigger_exits,
        "proposed_crit_dual_arm_repro": proposed,
        "sheet_crit_dual_arm_repro_unchanged": "PENDING",
        "observation_status": (
            "case-local observed pending Gate A1d-r3 review"
        ),
        "note": (
            "Supplemental and candidate sheet A2 left PENDING; "
            "proposed verdict only here."
        ),
        "failure_stage": failure_stage,
        "failure_detail": failure_detail,
        "route": route,
        "cohort": "supplemental-pilot",
    }
    if extra_env:
        if extra_env.get("execution_matrix"):
            out["execution_matrix"] = extra_env["execution_matrix"]
        if extra_env.get("formal_aggregation") is not None:
            out["formal_aggregation"] = extra_env["formal_aggregation"]
        if extra_env.get("blas_lapack_providers"):
            out["blas_lapack_providers"] = extra_env["blas_lapack_providers"]
    return out


def _run_trigger_once(
    log: CommandLog,
    *,
    py: Path,
    nid: str,
    arm: str,
    seed: int,
    out_json: Path,
    label: str,
) -> tuple[subprocess.CompletedProcess, dict | None, bool | None]:
    trig = log.run(
        [
            str(py),
            str(TRIG_ROOT / f"{nid}.py"),
            "--seed",
            str(seed),
            "--json-out",
            str(out_json),
        ],
        label=label,
        check=False,
        timeout=300,
    )
    payload = None
    if out_json.is_file():
        try:
            payload = json.loads(out_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = None
    prop = None
    if payload is not None and "property_holds" in payload:
        prop = bool(payload.get("property_holds"))
    elif trig.returncode in (0, 1):
        prop = trig.returncode == 0
    return trig, payload, prop


def run_dual_arm_python_case(
    log: CommandLog,
    member: dict,
    *,
    matrix: dict,
    runtime_pkgs: list[str],
    build_pkgs: list[str],
    python: Path,
    route: str,
    source_mode: str = "archive",
) -> dict:
    nid = member["neutral_id"]
    smoke_seeds = list(matrix["smoke"]["seeds"])
    formal_seeds = list(matrix["formal_repetitions"]["seeds"])
    # Canonical seed for top-level artifact aliases remains smoke/formal seed 0.
    seed = 0
    start = len(log.entries)
    case_dir = REPRO_ROOT / nid
    if case_dir.exists():
        shutil.rmtree(case_dir)
    case_dir.mkdir(parents=True)
    locks = case_dir / "locks"
    locks.mkdir(parents=True)
    work = WORK / nid
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)

    source_hashes: dict = {}
    exits: dict = {}
    holds: dict = {}
    failure_stage = None
    failure_detail = None
    built_arms: set[str] = set()
    blas_records: dict = {}
    per_seed: dict[int, dict] = {}

    try:
        for arm in ("buggy", "fixed"):
            log.run(
                [str(python), "-m", "venv", str(work / f"venv-{arm}")],
                label=f"{nid}:{arm}:venv",
            )

        probe = work / "venv-buggy" / "bin" / "python"
        build_lock = locks / "requirements.build.txt"
        build_meta = pip_hash_lock(probe, build_pkgs, build_lock, log, f"{nid}:build")
        write_json(
            locks / "BUILD_ARTIFACT_HASHES.json",
            {
                "lock": str(build_lock.relative_to(ROOT)),
                "packages": build_pkgs,
                "artifacts": build_meta.get("artifacts", {}),
                "resolved_requirements": build_meta.get(
                    "resolved_requirements", []
                ),
            },
        )
        runtime_lock = locks / "requirements.deps.txt"
        if runtime_pkgs:
            deps_meta = pip_hash_lock(
                probe, runtime_pkgs, runtime_lock, log, f"{nid}:deps"
            )
            write_json(
                locks / "WHEEL_ARTIFACT_HASHES.json",
                {
                    "lock": str(runtime_lock.relative_to(ROOT)),
                    "packages": runtime_pkgs,
                    "artifacts": deps_meta.get("artifacts", {}),
                    "resolved_requirements": deps_meta.get(
                        "resolved_requirements", []
                    ),
                },
            )

        for arm, sha in (("buggy", member["buggy_sha"]), ("fixed", member["fixed_sha"])):
            py = work / f"venv-{arm}" / "bin" / "python"
            log.run(
                [
                    str(py),
                    "-m",
                    "pip",
                    "install",
                    "--require-hashes",
                    "-r",
                    str(build_lock),
                ],
                label=f"{nid}:{arm}:pip-install-build-require-hashes",
                timeout=BUILD_TIMEOUT,
            )
            if runtime_pkgs:
                log.run(
                    [
                        str(py),
                        "-m",
                        "pip",
                        "install",
                        "--require-hashes",
                        "-r",
                        str(runtime_lock),
                    ],
                    label=f"{nid}:{arm}:pip-install-require-hashes",
                    timeout=BUILD_TIMEOUT,
                )
            src = work / f"{arm}-src"
            source_hashes[arm] = materialize_exact_source(
                repo=member["repo"],
                sha=sha,
                dest=src,
                work=work,
                arm=arm,
                nid=nid,
                mode=source_mode,
                log=log,
            )
            pretend = f"0.0.0+g{sha[:7]}"
            env = {
                "CC": "gcc",
                "CXX": "g++",
                "PATH": (
                    f"{work / f'venv-{arm}' / 'bin'}:"
                    f"{os.environ.get('PATH', '')}"
                ),
                "NINJA_NUM_JOBS": NJOBS,
                "SETUPTOOLS_SCM_PRETEND_VERSION": pretend,
                "SETUPTOOLS_SCM_PRETEND_VERSION_FOR_STATSMODELS": pretend,
                "SETUPTOOLS_SCM_PRETEND_VERSION_FOR_SCIPY": pretend,
                "SETUPTOOLS_SCM_PRETEND_VERSION_FOR_SCIKIT_LEARN": pretend,
                "SETUPTOOLS_SCM_PRETEND_VERSION_FOR_NUMPY": pretend,
            }
            src_proc = log.run(
                [
                    str(py),
                    "-m",
                    "pip",
                    "install",
                    "--no-deps",
                    "--no-build-isolation",
                    str(src),
                ],
                label=f"{nid}:{arm}:pip-install-exact-source",
                check=False,
                timeout=BUILD_TIMEOUT,
                env=env,
            )
            text = (src_proc.stdout or "") + "\n" + (src_proc.stderr or "")
            if src_proc.returncode != 0:
                failure_stage = "build"
                failure_detail = (
                    "REPRO_FAILED:build - exact-source install exit "
                    f"{src_proc.returncode} on {arm}"
                )
                (case_dir / f"{arm}.stdout.txt").write_text(
                    src_proc.stdout or "", encoding="utf-8"
                )
                (case_dir / f"{arm}.stderr.txt").write_text(
                    src_proc.stderr or "", encoding="utf-8"
                )
                exits[arm] = src_proc.returncode
                holds[arm] = None
                continue
            if "Installing build dependencies" in text:
                failure_stage = "build"
                failure_detail = (
                    "REPRO_FAILED:build - isolated build dependency "
                    "resolution observed"
                )
                exits[arm] = 1
                holds[arm] = None
                continue
            built_arms.add(arm)

        if failure_stage is None and built_arms != {"buggy", "fixed"}:
            failure_stage = "build"
            failure_detail = (
                f"REPRO_FAILED:build - incomplete arms built={sorted(built_arms)}"
            )

        if failure_stage is None and nid in NUMERIC_BLAS_CASES:
            for arm in ("buggy", "fixed"):
                py = work / f"venv-{arm}" / "bin" / "python"
                rec = discover_blas_lapack_provider(
                    py, label=f"{nid}:{arm}:blas-lapack-provider"
                )
                # Persist full discovery command/stdout/stderr/exit.
                prov_dir = locks / "blas_lapack" / arm
                prov_dir.mkdir(parents=True, exist_ok=True)
                (prov_dir / "command.txt").write_text(
                    subprocess.list2cmdline(rec["command"]) + "\n",
                    encoding="utf-8",
                )
                (prov_dir / "stdout.txt").write_text(
                    rec["stdout"], encoding="utf-8"
                )
                (prov_dir / "stderr.txt").write_text(
                    rec["stderr"], encoding="utf-8"
                )
                (prov_dir / "exit_code.txt").write_text(
                    f"{rec['exit_code']}\n", encoding="utf-8"
                )
                write_json(
                    prov_dir / "provider.json",
                    {
                        "provider_summary": rec["provider_summary"],
                        "parsed": rec["parsed"],
                        "exit_code": rec["exit_code"],
                    },
                )
                log.entries.append(
                    {
                        "label": rec["label"],
                        "command": subprocess.list2cmdline(rec["command"]),
                        "cwd": str(ROOT),
                        "exit_code": rec["exit_code"],
                        "stdout_tail": scrub((rec["stdout"] or "")[-4000:]),
                        "stderr_tail": scrub((rec["stderr"] or "")[-4000:]),
                        "timeout_s": 120,
                    }
                )
                blas_records[arm] = {
                    "provider_summary": rec["provider_summary"],
                    "exit_code": rec["exit_code"],
                    "artifact_dir": str(
                        (prov_dir).relative_to(ROOT)
                    ),
                }
            write_json(
                locks / "BLAS_LAPACK_PROVIDER.json",
                {"neutral_id": nid, "arms": blas_records},
            )

        if failure_stage is None:
            # Per-arm smoke (seed=0) before formal repetitions.
            for arm in ("buggy", "fixed"):
                py = work / f"venv-{arm}" / "bin" / "python"
                for smoke_seed in smoke_seeds:
                    smoke_dir = case_dir / "smoke" / f"seed-{smoke_seed}"
                    out_json = smoke_dir / f"{arm}.json"
                    trig, payload, prop = _run_trigger_once(
                        log,
                        py=py,
                        nid=nid,
                        arm=arm,
                        seed=smoke_seed,
                        out_json=out_json,
                        label=f"{nid}:{arm}:smoke-seed-{smoke_seed}",
                    )
                    save_execution_outputs(
                        smoke_dir,
                        arm,
                        payload=payload,
                        stdout=trig.stdout or "",
                        stderr=trig.stderr or "",
                        raw_return_code=trig.returncode,
                    )
                    if prop is None:
                        failure_stage = "smoke"
                        failure_detail = (
                            f"REPRO_FAILED:smoke - {arm} seed={smoke_seed} "
                            "missing property_holds"
                        )

        if failure_stage is None:
            # Formal repetition matrix with buggy/fixed input parity.
            for formal_seed in formal_seeds:
                seed_dir = case_dir / "repetitions" / f"seed-{formal_seed}"
                arm_payloads: dict[str, dict | None] = {}
                arm_props: dict[str, bool | None] = {}
                arm_rcs: dict[str, int] = {}
                for arm in ("buggy", "fixed"):
                    py = work / f"venv-{arm}" / "bin" / "python"
                    out_json = seed_dir / f"{arm}.json"
                    trig, payload, prop = _run_trigger_once(
                        log,
                        py=py,
                        nid=nid,
                        arm=arm,
                        seed=formal_seed,
                        out_json=out_json,
                        label=(
                            f"{nid}:{arm}:formal-seed-{formal_seed}"
                        ),
                    )
                    save_execution_outputs(
                        seed_dir,
                        arm,
                        payload=payload,
                        stdout=trig.stdout or "",
                        stderr=trig.stderr or "",
                        raw_return_code=trig.returncode,
                    )
                    arm_payloads[arm] = payload
                    arm_props[arm] = prop
                    arm_rcs[arm] = trig.returncode
                parity = assert_arm_input_parity(
                    arm_payloads.get("buggy"),
                    arm_payloads.get("fixed"),
                    formal_seed,
                )
                per_seed[formal_seed] = {
                    "buggy_property_holds": arm_props.get("buggy"),
                    "fixed_property_holds": arm_props.get("fixed"),
                    "buggy_raw_return_code": arm_rcs.get("buggy"),
                    "fixed_raw_return_code": arm_rcs.get("fixed"),
                    "input_parity_ok": parity,
                }
                # Keep seed-0 top-level aliases for prior consumers.
                if formal_seed == 0:
                    for arm in ("buggy", "fixed"):
                        src_json = seed_dir / f"{arm}.json"
                        if src_json.is_file():
                            shutil.copy2(src_json, case_dir / f"{arm}.json")
                        (case_dir / f"{arm}.stdout.txt").write_text(
                            (seed_dir / f"{arm}.stdout.txt").read_text(
                                encoding="utf-8"
                            ),
                            encoding="utf-8",
                        )
                        (case_dir / f"{arm}.stderr.txt").write_text(
                            (seed_dir / f"{arm}.stderr.txt").read_text(
                                encoding="utf-8"
                            ),
                            encoding="utf-8",
                        )
                    holds = {
                        "buggy": arm_props.get("buggy"),
                        "fixed": arm_props.get("fixed"),
                    }
                    exits = {
                        "buggy": (
                            0 if arm_props.get("buggy") else 1
                        ),
                        "fixed": (
                            0 if arm_props.get("fixed") else 1
                        ),
                    }

            aggregation = aggregate_formal_verdict(
                per_seed, formal_seeds=formal_seeds
            )
            write_json(
                case_dir / "REPETITION_MATRIX.json",
                {
                    "neutral_id": nid,
                    "smoke_seeds": smoke_seeds,
                    "formal_seeds": formal_seeds,
                    "per_seed": {
                        str(k): v for k, v in sorted(per_seed.items())
                    },
                    "aggregation": aggregation,
                },
            )
            if aggregation["proposed_crit_dual_arm_repro"] != "PASS":
                failure_stage = "contrast"
                failure_detail = (
                    "REPRO_FAILED:contrast - formal matrix failing_seeds="
                    f"{aggregation['failing_seeds']}"
                )

        return finalize_case(
            member=member,
            log_slice=log.entries[start:],
            buggy_holds=holds.get("buggy"),
            fixed_holds=holds.get("fixed"),
            trigger_exits=exits,
            failure_stage=failure_stage,
            failure_detail=failure_detail,
            route=route,
            source_hashes=source_hashes,
            seed=seed,
            extra_env={
                "hash_locked_build_closure": True,
                "no_build_isolation": True,
                "python_for_case": str(python),
                "execution_matrix": {
                    "smoke_seeds": smoke_seeds,
                    "formal_seeds": formal_seeds,
                },
                "blas_lapack_providers": blas_records,
                "formal_aggregation": (
                    aggregate_formal_verdict(
                        per_seed, formal_seeds=formal_seeds
                    )
                    if per_seed
                    else None
                ),
            },
        )
    except Exception as exc:  # noqa: BLE001
        return finalize_case(
            member=member,
            log_slice=log.entries[start:],
            buggy_holds=holds.get("buggy"),
            fixed_holds=holds.get("fixed"),
            trigger_exits=exits,
            failure_stage="build",
            failure_detail=f"REPRO_FAILED:build - exception: {exc}",
            route=route,
            source_hashes=source_hashes,
            seed=seed,
        )


CASE_SPECS = {
    "EXT-numpy-01": {
        "build_pkgs": ["pip", "setuptools==59.2.0", "wheel==0.37.0", "Cython>=0.29.30,<3.0"],
        "runtime_pkgs": [],
        "route": "exact-source-numpy-setuptools-py39",
        "source_mode": "git_checkout",
    },
    "EXT-scipy-01": {
        "build_pkgs": [
            "pip",
            "setuptools",
            "wheel",
            "packaging",
            "meson-python>=0.15.0",
            "meson>=1.9.0",
            "Cython>=3.0.8",
            "pybind11>=2.13.2",
            "pythran>=0.14.0",
            "ninja",
            "numpy>=2.0.0",
            "setuptools_scm>=8",
        ],
        "runtime_pkgs": ["numpy>=2.0.0"],
        "route": "exact-source-scipy-meson",
        # Full git tree so meson sees submodules (array_api_compat, xsf, boost_math, ...).
        "source_mode": "git_checkout",
    },
    "EXT-scikit-learn-01": {
        "build_pkgs": [
            "pip",
            "setuptools==69.5.1",
            "wheel==0.42.0",
            "packaging",
            # sklearn 1.3-era pyx files fail under Cython 3.x / NumPy 2.x / CPython 3.12.
            "Cython>=0.29.33,<3.0",
            "numpy>=1.21.0,<1.25",
            "scipy>=1.7.0,<1.12",
            "setuptools_scm>=8",
        ],
        "runtime_pkgs": [
            "numpy>=1.21.0,<1.25",
            "scipy>=1.7.0,<1.12",
            "joblib",
            "threadpoolctl",
        ],
        "route": "exact-source-sklearn-setuptools-py39",
        "source_mode": "archive",
    },
    "EXT-statsmodels-01": {
        "build_pkgs": [
            "pip",
            "setuptools",
            "wheel",
            "packaging",
            "meson-python",
            "meson>=1.9.0",
            "ninja",
            "Cython>=3.0.13,<4",
            "numpy>=2.0.0,<3",
            "scipy>=1.13,<2",
            "setuptools_scm>=9.2.0,<10",
        ],
        "runtime_pkgs": ["numpy>=2", "scipy>=1.13", "pandas", "patsy", "packaging"],
        "route": "exact-source-statsmodels-meson",
        "source_mode": "archive",
    },
    "EXT-statsmodels-02": {
        "build_pkgs": [
            "pip",
            "setuptools",
            "wheel",
            "packaging",
            "meson-python",
            "meson>=1.9.0",
            "ninja",
            "Cython>=3.0.13,<4",
            "numpy>=2.0.0,<3",
            "scipy>=1.13,<2",
            "setuptools_scm>=9.2.0,<10",
        ],
        "runtime_pkgs": ["numpy>=2", "scipy>=1.13", "pandas", "patsy", "packaging"],
        "route": "exact-source-statsmodels-meson",
        "source_mode": "archive",
    },
    "EXT-statsmodels-03": {
        # 2016-era setup.py requires pkg_resources (setuptools<81) and older numeric stack.
        "build_pkgs": [
            "pip",
            "setuptools==69.5.1",
            "wheel==0.42.0",
            "packaging",
            "Cython==0.29.36",
            "numpy==1.19.5",
            "scipy==1.5.4",
            "pandas==1.1.5",
            "patsy==0.5.6",
        ],
        "runtime_pkgs": ["numpy==1.19.5", "scipy==1.5.4", "pandas==1.1.5", "patsy==0.5.6"],
        "route": "exact-source-statsmodels-legacy-py39",
        "source_mode": "archive",
    },
}


def hash_tree_files(case_dir: Path) -> dict:
    files = {}
    for name in [
        "environment.json",
        "COMMANDS.json",
        "buggy.json",
        "fixed.json",
        "stdout.log",
        "stderr.log",
        "REPETITION_MATRIX.json",
    ]:
        p = case_dir / name
        if p.exists():
            files[name] = sha256_file(p)
    for sub in ("locks", "smoke", "repetitions"):
        root = case_dir / sub
        if not root.exists():
            continue
        for p in sorted(root.rglob("*")):
            if p.is_file() and not p.name.startswith("."):
                rel = f"{sub}/{p.relative_to(root).as_posix()}"
                files[rel] = sha256_file(p)
    return files


def run_verification(log: CommandLog, membership_path: Path, readiness_path: Path) -> dict:
    start = len(log.entries)
    checks: dict = {}

    proc = log.run(
        [
            str(HOST_PY),
            "scripts/check_external_admission.py",
            "--sheet",
            "data/external_slice/admission_sheet.cursor_candidate.csv",
        ],
        cwd=ROOT,
        env={"PYTHONPATH": "src"},
        label="verify:admission_checker",
        check=False,
    )
    checks["admission_checker"] = {
        "exit_code": proc.returncode,
        "stdout_tail": (proc.stdout or "")[-2000:],
    }

    proc = log.run(
        [str(HOST_PY), "-m", "pytest", "-q"],
        cwd=ROOT,
        env={"PYTHONPATH": "src"},
        label="verify:pytest",
        check=False,
    )
    checks["pytest"] = {
        "exit_code": proc.returncode,
        "stdout_tail": (proc.stdout or "")[-2000:],
    }

    proc = log.run(
        [
            str(HOST_PY),
            "-m",
            "compileall",
            "-q",
            "scripts/external_slice/run_c3_batch3_readiness.py",
            "data/external_slice/reproducers/EXT-numpy-01.py",
            "data/external_slice/reproducers/EXT-scipy-01.py",
            "data/external_slice/reproducers/EXT-scikit-learn-01.py",
            "data/external_slice/reproducers/EXT-statsmodels-01.py",
            "data/external_slice/reproducers/EXT-statsmodels-02.py",
            "data/external_slice/reproducers/EXT-statsmodels-03.py",
        ],
        cwd=ROOT,
        label="verify:compileall",
        check=False,
    )
    checks["compileall"] = {"exit_code": proc.returncode}

    decision_paths = [
        "data/external_slice/readiness_batch3.json",
        "data/external_slice/BATCH3_MEMBERSHIP.json",
        "data/external_slice/HANDOFF_REPRO_BATCH3.json",
    ]
    for nid_path in sorted(REPRO_ROOT.glob("EXT-*")):
        # Only Batch3 members' decision files are required; scanning all EXT is ok if clean.
        for name in ("environment.json", "buggy.json", "fixed.json"):
            p = nid_path / name
            if p.is_file() and nid_path.name in {
                "EXT-numpy-01",
                "EXT-scipy-01",
                "EXT-scikit-learn-01",
                "EXT-statsmodels-01",
                "EXT-statsmodels-02",
                "EXT-statsmodels-03",
            }:
                decision_paths.append(str(p.relative_to(ROOT)))
    # Handoff may not exist yet during first verify pass; create empty skip.
    decision_paths = [
        p
        for p in decision_paths
        if (ROOT / p).exists() or p.endswith("HANDOFF_REPRO_BATCH3.json")
    ]
    existing = [p for p in decision_paths if (ROOT / p).exists()]
    leak_shell = (
        "rg -n "
        + shlex.quote(RUNBOOK_RESERVED_PATTERN)
        + " "
        + " ".join(shlex.quote(p) for p in existing)
        + "; ec=$?; if [ $ec -eq 1 ]; then exit 0; "
        "elif [ $ec -eq 0 ]; then echo 'RESERVED_TERM_LEAK'; exit 1; "
        "else exit $ec; fi"
    )
    proc = log.run(
        ["bash", "-lc", leak_shell],
        cwd=ROOT,
        label="verify:leak_scan_reserved_runbook",
        check=False,
    )
    checks["leak_scan_reserved_runbook"] = {
        "exit_code": proc.returncode,
        "expected_clean_rg_exit": 1,
        "expected_checker_exit": 0,
        "pattern": RUNBOOK_RESERVED_PATTERN,
        "scope": "decision-level Batch 3 artifacts",
        "stdout_tail": (proc.stdout or "")[-1000:],
    }

    token_paths = [
        "data/external_slice/reproduction",
        "data/external_slice/readiness_batch3.json",
        "data/external_slice/BATCH3_MEMBERSHIP.json",
    ]
    if (ROOT / "data/external_slice/HANDOFF_REPRO_BATCH3.json").exists():
        token_paths.append("data/external_slice/HANDOFF_REPRO_BATCH3.json")
    token_shell = (
        "rg -n "
        + shlex.quote(TOKEN_SCAN_PATTERN)
        + " "
        + " ".join(shlex.quote(p) for p in token_paths)
        + "; ec=$?; if [ $ec -eq 1 ]; then exit 0; "
        "elif [ $ec -eq 0 ]; then echo 'TOKEN_LEAK'; exit 1; "
        "else exit $ec; fi"
    )
    proc = log.run(
        ["bash", "-lc", token_shell],
        cwd=ROOT,
        label="verify:token_scan",
        check=False,
    )
    checks["token_scan"] = {
        "exit_code": proc.returncode,
        "expected_clean_rg_exit": 1,
        "expected_checker_exit": 0,
        "pattern": TOKEN_SCAN_PATTERN,
        "stdout_tail": (proc.stdout or "")[-1000:],
    }

    proc = log.run(
        [
            str(HOST_PY),
            "scripts/external_slice/verify_batch3_membership_matrix.py",
        ],
        cwd=ROOT,
        label="verify:membership_and_sheet_pending",
        check=False,
    )
    checks["membership_and_sheet_pending"] = {
        "exit_code": proc.returncode,
        "stdout_tail": (proc.stdout or "")[-500:],
    }
    return {"checks": checks, "commands": log.entries[start:]}


def handoff_hash_checker(handoff_path: Path) -> int:
    handoff = json.loads(handoff_path.read_text(encoding="utf-8"))
    bad = []
    for name, digest in handoff.get("outputs", {}).get("files", {}).items():
        candidates = [
            ROOT / "data" / "external_slice" / name,
            ROOT / "data" / "external_slice" / "reproduction" / name,
            ROOT / name,
        ]
        path = next((p for p in candidates if p.is_file()), None)
        if path is None:
            bad.append((name, "missing", digest))
            continue
        actual = sha256_file(path)
        if actual != digest:
            bad.append((name, actual, digest))
    for nid, files in handoff.get("outputs", {}).get("per_case_artifact_sha256", {}).items():
        case_dir = REPRO_ROOT / nid
        for rel, digest in files.items():
            path = case_dir / rel
            if not path.is_file():
                bad.append((f"{nid}:{rel}", "missing", digest))
                continue
            actual = sha256_file(path)
            if actual != digest:
                bad.append((f"{nid}:{rel}", actual, digest))
    report = REPRO_ROOT / "BATCH3_HANDOFF_HASH_CHECK.json"
    write_json(
        report,
        {"ok": not bad, "mismatches": bad, "checked_at": datetime.now(timezone.utc).isoformat()},
    )
    if bad:
        print("HASH_MISMATCHES", len(bad))
        for row in bad[:20]:
            print(row)
        return 1
    print("HASH_CHECK_OK")
    return 0


def rederive_case_from_artifacts(
    member: dict,
    *,
    matrix: dict,
) -> dict:
    """Rebuild derived verdict fields from frozen execution artifacts.

    Does not rerun dual-arm builds or mutate smoke/repetitions/provider files.
    """
    nid = member["neutral_id"]
    case_dir = REPRO_ROOT / nid
    formal_seeds = list(matrix["formal_repetitions"]["seeds"])
    smoke_seeds = list(matrix["smoke"]["seeds"])
    per_seed = reconstruct_formal_per_seed_from_artifacts(
        case_dir, formal_seeds=formal_seeds
    )
    aggregation = aggregate_formal_verdict(per_seed, formal_seeds=formal_seeds)
    proposed = aggregation["proposed_crit_dual_arm_repro"]
    failure_stage = None if proposed == "PASS" else "contrast"
    failure_detail = None
    if failure_stage:
        failure_detail = (
            "REPRO_FAILED:contrast - formal matrix failing_seeds="
            f"{aggregation['failing_seeds']}"
        )

    seed0 = per_seed.get(0, {})
    buggy_holds = seed0.get("buggy_property_holds")
    fixed_holds = seed0.get("fixed_property_holds")
    trigger_exits = {
        "buggy": seed0.get("buggy_raw_return_code"),
        "fixed": seed0.get("fixed_raw_return_code"),
    }

    # Refresh derived aggregation surfaces only.
    prior_matrix = {}
    matrix_path = case_dir / "REPETITION_MATRIX.json"
    if matrix_path.is_file():
        prior_matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    write_json(
        matrix_path,
        {
            "neutral_id": nid,
            "smoke_seeds": prior_matrix.get("smoke_seeds", smoke_seeds),
            "formal_seeds": formal_seeds,
            "per_seed": {str(k): v for k, v in sorted(per_seed.items())},
            "aggregation": aggregation,
        },
    )

    env_path = case_dir / "environment.json"
    env = json.loads(env_path.read_text(encoding="utf-8"))
    env["formal_aggregation"] = aggregation
    env["proposed_crit_dual_arm_repro"] = proposed
    env["failure_stage"] = failure_stage
    env["failure_detail"] = failure_detail
    env["dual_arm_contrast"] = proposed == "PASS"
    env["trigger_exit_codes"] = trigger_exits
    env["execution_matrix"] = {
        "smoke_seeds": smoke_seeds,
        "formal_seeds": formal_seeds,
    }
    write_json(env_path, env)

    commands_path = case_dir / "COMMANDS.json"
    command_count = 0
    if commands_path.is_file():
        command_count = len(
            json.loads(commands_path.read_text(encoding="utf-8")).get(
                "commands", []
            )
        )
    locks = case_dir / "locks"
    return {
        "neutral_id": nid,
        "repo": member["repo"],
        "issue_url": member["issue_url"],
        "buggy_sha": member["buggy_sha"],
        "fixed_sha": member["fixed_sha"],
        "seed": 0,
        "trigger": str((TRIG_ROOT / f"{nid}.py").relative_to(ROOT)),
        "artifact_dir": str(case_dir.relative_to(ROOT)),
        "locks_dir": str(locks.relative_to(ROOT)),
        "command_count": command_count,
        "buggy_property_holds": buggy_holds,
        "fixed_property_holds": fixed_holds,
        "dual_arm_contrast": proposed == "PASS",
        "trigger_exit_codes": trigger_exits,
        "proposed_crit_dual_arm_repro": proposed,
        "sheet_crit_dual_arm_repro_unchanged": "PENDING",
        "observation_status": (
            "case-local observed pending Gate A1d-r3 review"
        ),
        "note": (
            "Supplemental and candidate sheet A2 left PENDING; "
            "proposed verdict only here."
        ),
        "failure_stage": failure_stage,
        "failure_detail": failure_detail,
        "route": env.get("route", CASE_SPECS[nid]["route"]),
        "cohort": "supplemental-pilot",
        "execution_matrix": {
            "smoke_seeds": smoke_seeds,
            "formal_seeds": formal_seeds,
        },
        "formal_aggregation": aggregation,
        "blas_lapack_providers": env.get("blas_lapack_providers"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sheet", type=Path, default=DEFAULT_SHEET)
    parser.add_argument("--membership", type=Path, default=DEFAULT_MEMBERSHIP)
    parser.add_argument(
        "--matrix",
        type=Path,
        default=DEFAULT_MATRIX,
        help="Frozen A1d-r1 execution matrix",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=0,
        help="Ignored for formal aggregation; matrix seeds govern verdicts",
    )
    parser.add_argument("--only", nargs="*", help="Optional subset of neutral_ids")
    parser.add_argument(
        "--rederive-from-artifacts",
        action="store_true",
        help="Rebuild derived verdicts/handoff without dual-arm rerun",
    )
    args = parser.parse_args()
    args.sheet = args.sheet.resolve()
    args.membership = args.membership.resolve()
    args.matrix = args.matrix.resolve()

    WORK.mkdir(parents=True, exist_ok=True)
    matrix = load_execution_matrix(args.matrix)
    membership_sha = assert_membership_byte_identical(
        args.membership, matrix=matrix
    )
    membership = json.loads(args.membership.read_text(encoding="utf-8"))
    members = membership["members"]
    expected = list(matrix["members"])
    got = [m["neutral_id"] for m in members]
    if got != expected:
        raise SystemExit(f"membership IDs must be exactly {expected}, got {got}")

    sheet_sha = sha256_file(args.sheet)
    if sheet_sha != "77f729b1297ef24d4223d5277b093c93ad84711dfbbe69a1927398d49d387a0a":
        raise SystemExit(f"unexpected sheet sha256: {sheet_sha}")

    log = CommandLog()
    results = []
    for member in members:
        nid = member["neutral_id"]
        if args.only and nid not in args.only:
            continue
        if args.rederive_from_artifacts:
            print(f"===== {nid} rederive-from-artifacts =====", flush=True)
            t0 = time.time()
            result = rederive_case_from_artifacts(member, matrix=matrix)
            print(
                nid,
                result["proposed_crit_dual_arm_repro"],
                result.get("failure_stage"),
                f"elapsed={time.time()-t0:.1f}s",
                flush=True,
            )
            results.append(result)
            continue
        spec = CASE_SPECS[nid]
        py = choose_python(nid)
        print(f"===== {nid} python={py} =====", flush=True)
        t0 = time.time()
        result = run_dual_arm_python_case(
            log,
            member,
            matrix=matrix,
            runtime_pkgs=list(spec["runtime_pkgs"]),
            build_pkgs=list(spec["build_pkgs"]),
            python=py,
            route=spec["route"],
            source_mode=str(spec.get("source_mode", "archive")),
        )
        print(
            nid,
            result["proposed_crit_dual_arm_repro"],
            result.get("failure_stage"),
            f"elapsed={time.time()-t0:.1f}s",
            flush=True,
        )
        results.append(result)

    # Keep sheet order for all 6 even if --only used for debugging.
    if not args.only:
        assert [r["neutral_id"] for r in results] == expected

    gate_name = "A1d-r3" if args.rederive_from_artifacts else "A1d-r1"
    readiness = {
        "batch": 3,
        "batch_name": "supplemental-pilot-six",
        "gate": gate_name,
        "frozen_membership": str(args.membership.relative_to(ROOT)),
        "frozen_membership_sha256": membership_sha,
        "frozen_execution_matrix": str(args.matrix.relative_to(ROOT)),
        "frozen_execution_matrix_sha256": sha256_file(args.matrix),
        "frozen_at_commit": membership.get("frozen_at_commit"),
        "gate_a1c_verdict": membership.get("gate_a1c_verdict"),
        "selection_rule": membership.get("selection_rule"),
        "source_sheet": str(args.sheet.relative_to(ROOT)),
        "source_sheet_sha256": sheet_sha,
        "smoke_seeds": list(matrix["smoke"]["seeds"]),
        "formal_seeds": list(matrix["formal_repetitions"]["seeds"]),
        "seed": 0,
        "cases": results,
        "counts": {
            "batch_size": len(results),
            "proposed_PASS": sum(
                1
                for r in results
                if r.get("proposed_crit_dual_arm_repro") == "PASS"
            ),
            "proposed_REPRO_FAILED": sum(
                1
                for r in results
                if r.get("proposed_crit_dual_arm_repro") == "REPRO_FAILED"
            ),
        },
        "cumulative_note": (
            "Even if all six PASS, Batch1+2+3 ready <= 18 < protocol n>=20; "
            f"Gate {gate_name} cannot unlock canonical freeze; "
            "supplementary-mining loop required."
        ),
        "not_started": membership.get("not_started", []),
        "sheet_mutation_policy": (
            "supplemental and candidate sheet A2 fields remain PENDING"
        ),
        "rederived_from_artifacts": bool(args.rederive_from_artifacts),
    }
    readiness_path = ROOT / "data" / "external_slice" / "readiness_batch3.json"
    write_json(readiness_path, readiness)

    # Global command log from per-case files (after redaction).
    all_cmds: list[dict] = []
    for m in members:
        if args.only and m["neutral_id"] not in args.only:
            continue
        cp = REPRO_ROOT / m["neutral_id"] / "COMMANDS.json"
        cmds = json.loads(cp.read_text(encoding="utf-8")).get("commands", [])
        for e in cmds:
            all_cmds.append(
                {
                    **e,
                    "command": scrub(e.get("command", "")),
                    "stdout_tail": scrub(e.get("stdout_tail", "")),
                    "stderr_tail": scrub(e.get("stderr_tail", "")),
                }
            )
    write_json(
        REPRO_ROOT / "BATCH3_COMMAND_LOG.json",
        {"commands": all_cmds, "command_count": len(all_cmds)},
    )

    verify = run_verification(log, args.membership, readiness_path)
    write_json(
        REPRO_ROOT / "BATCH3_VERIFICATION_LOG.json",
        {
            "checks": verify["checks"],
            "commands": [
                {
                    **e,
                    "command": scrub(e.get("command", "")),
                    "stdout_tail": scrub(e.get("stdout_tail", "")),
                    "stderr_tail": scrub(e.get("stderr_tail", "")),
                }
                for e in verify["commands"]
            ],
        },
    )

    outputs_files = {
        "readiness_batch3.json": sha256_file(readiness_path),
        "BATCH3_MEMBERSHIP.json": sha256_file(args.membership),
        "BATCH3_EXECUTION_MATRIX.json": sha256_file(args.matrix),
        "BATCH3_COMMAND_LOG.json": sha256_file(
            REPRO_ROOT / "BATCH3_COMMAND_LOG.json"
        ),
        "BATCH3_VERIFICATION_LOG.json": sha256_file(
            REPRO_ROOT / "BATCH3_VERIFICATION_LOG.json"
        ),
        "admission_sheet.csv": sheet_sha,
        "admission_sheet.cursor_candidate.csv": sha256_file(
            ROOT / "data/external_slice/admission_sheet.cursor_candidate.csv"
        ),
    }
    # Include per-case BLAS provider JSON files in the handoff digest set.
    for m in members:
        if args.only and m["neutral_id"] not in args.only:
            continue
        blas = (
            REPRO_ROOT
            / m["neutral_id"]
            / "locks"
            / "BLAS_LAPACK_PROVIDER.json"
        )
        if blas.is_file():
            outputs_files[
                f"reproduction/{m['neutral_id']}/locks/BLAS_LAPACK_PROVIDER.json"
            ] = sha256_file(blas)
    per_case = {
        m["neutral_id"]: hash_tree_files(REPRO_ROOT / m["neutral_id"])
        for m in members
        if (not args.only or m["neutral_id"] in args.only)
    }

    case_results = [
        {
            "neutral_id": r["neutral_id"],
            "proposed": r["proposed_crit_dual_arm_repro"],
            "trigger_exit_codes": r.get("trigger_exit_codes"),
            "failure_stage": r.get("failure_stage"),
            "failure_detail": r.get("failure_detail"),
            "formal_seeds": list(matrix["formal_repetitions"]["seeds"]),
            "smoke_seeds": list(matrix["smoke"]["seeds"]),
        }
        for r in results
    ]

    if args.rederive_from_artifacts:
        handoff_task = "C3 readiness Batch 3 A1d-r3 correction"
        handoff_gate = "A1d-r3"
        baseline_commit = "8ef20d26ea0a785bd0209b922a94e7f3bc1e8064"
        parent_handoff_commit = "8ef20d26ea0a785bd0209b922a94e7f3bc1e8064"
    else:
        handoff_task = "C3 readiness Batch 3 A1d-r1 correction"
        handoff_gate = "A1d-r1"
        baseline_commit = "da70fa676ebcab8ef1e98f532aa711c2d01f0c84"
        parent_handoff_commit = "da70fa676ebcab8ef1e98f532aa711c2d01f0c84"
    handoff = {
        "task": handoff_task,
        "gate": handoff_gate,
        "branch": "cursor/grok-phase3-c3-readiness-batch3",
        "baseline_commit": baseline_commit,
        "parent_handoff_commit": parent_handoff_commit,
        "membership_commit": "cc3321da3a9e6f1f7d67e5b90cdf21d6fb9001c1",
        "batch": {
            "number": 3,
            "member_count": len(results),
            "selection": (
                "fixed six supplemental-pilot A1/A3 PASS A2 PENDING rows; "
                "no substitution"
            ),
            "replacement_policy": "forbidden",
            "sheet_a2_policy": (
                "PENDING unchanged on supplemental and candidate sheets"
            ),
            "execution_matrix": str(args.matrix.relative_to(ROOT)),
            "smoke_seeds": list(matrix["smoke"]["seeds"]),
            "formal_seeds": list(matrix["formal_repetitions"]["seeds"]),
            "stop_after_push": True,
            "batch4_started": False,
            "c4_started": False,
            "supplementary_mining_started": False,
            "canonical_freeze_started": False,
            "rederived_from_artifacts": bool(args.rederive_from_artifacts),
            "dual_arm_rerun": (not args.rederive_from_artifacts),
        },
        "counts": readiness["counts"],
        "case_results": case_results,
        "commands": {
            "case_execution_log": (
                "data/external_slice/reproduction/BATCH3_COMMAND_LOG.json"
            ),
            "case_command_count": len(all_cmds),
            "verification_log": (
                "data/external_slice/reproduction/BATCH3_VERIFICATION_LOG.json"
            ),
            "verification_command_count": len(verify["commands"]),
            "hash_check_script": (
                "scripts/external_slice/check_batch3_handoff_hashes.py"
            ),
        },
        "exit_codes": {
            "per_case_trigger": {
                c["neutral_id"]: c.get("trigger_exit_codes") for c in results
            },
            "admission_checker": verify["checks"]["admission_checker"][
                "exit_code"
            ],
            "pytest": verify["checks"]["pytest"]["exit_code"],
            "compileall": verify["checks"]["compileall"]["exit_code"],
            "leak_scan_reserved_runbook": verify["checks"][
                "leak_scan_reserved_runbook"
            ]["exit_code"],
            "token_scan": verify["checks"]["token_scan"]["exit_code"],
            "membership_and_sheet_pending": verify["checks"][
                "membership_and_sheet_pending"
            ]["exit_code"],
        },
        "inputs": {
            "BATCH3_MEMBERSHIP.json": outputs_files["BATCH3_MEMBERSHIP.json"],
            "BATCH3_EXECUTION_MATRIX.json": outputs_files[
                "BATCH3_EXECUTION_MATRIX.json"
            ],
            "admission_sheet.csv": sheet_sha,
            "smoke_seeds": list(matrix["smoke"]["seeds"]),
            "formal_seeds": list(matrix["formal_repetitions"]["seeds"]),
            "build_timeout_s": BUILD_TIMEOUT,
        },
        "outputs": {
            "files": outputs_files,
            "per_case_artifact_sha256": per_case,
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "tools": tool_versions(),
        },
        "failures": [
            c for c in case_results if c["proposed"] == "REPRO_FAILED"
        ],
        "not_started": readiness["not_started"],
        "cumulative_note": readiness["cumulative_note"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    handoff_path = ROOT / "data" / "external_slice" / "HANDOFF_REPRO_BATCH3.json"
    write_json(handoff_path, handoff)

    checker = ROOT / "scripts" / "external_slice" / "check_batch3_handoff_hashes.py"
    handoff_rel = "data/external_slice/HANDOFF_REPRO_BATCH3.json"
    checker.write_text(
        "#!/usr/bin/env python3\n"
        "from pathlib import Path\n"
        "import sys\n"
        "sys.path.insert(0, str(Path(__file__).resolve().parent))\n"
        "from run_c3_batch3_readiness import handoff_hash_checker, ROOT\n"
        f"raise SystemExit(handoff_hash_checker(ROOT / {handoff_rel!r}))\n",
        encoding="utf-8",
    )
    checker.chmod(0o755)

    # Re-run verification including handoff now that it exists; update logs/hashes.
    verify2 = run_verification(log, args.membership, readiness_path)
    hc = log.run(
        [str(HOST_PY), str(checker)],
        cwd=ROOT,
        label="verify:handoff_hash_checker",
        check=False,
    )
    vlog = {
        "checks": {
            **verify2["checks"],
            "handoff_hash_checker": {
                "exit_code": hc.returncode,
                "stdout_tail": scrub((hc.stdout or "")[-1000:]),
            },
        },
        "commands": [
            {
                **e,
                "command": scrub(e.get("command", "")),
                "stdout_tail": scrub(e.get("stdout_tail", "")),
                "stderr_tail": scrub(e.get("stderr_tail", "")),
            }
            for e in verify2["commands"]
        ]
        + [
            {
                "label": "verify:handoff_hash_checker",
                "command": scrub(subprocess.list2cmdline([str(HOST_PY), str(checker)])),
                "cwd": str(ROOT),
                "exit_code": hc.returncode,
                "stdout_tail": scrub((hc.stdout or "")[-1000:]),
                "stderr_tail": scrub((hc.stderr or "")[-1000:]),
                "timeout_s": None,
            }
        ],
    }
    write_json(REPRO_ROOT / "BATCH3_VERIFICATION_LOG.json", vlog)

    outputs_files["BATCH3_VERIFICATION_LOG.json"] = sha256_file(
        REPRO_ROOT / "BATCH3_VERIFICATION_LOG.json"
    )
    outputs_files["BATCH3_COMMAND_LOG.json"] = sha256_file(REPRO_ROOT / "BATCH3_COMMAND_LOG.json")
    outputs_files["readiness_batch3.json"] = sha256_file(readiness_path)
    per_case = {
        m["neutral_id"]: hash_tree_files(REPRO_ROOT / m["neutral_id"])
        for m in members
        if (not args.only or m["neutral_id"] in args.only)
    }
    handoff["outputs"]["files"] = outputs_files
    handoff["outputs"]["per_case_artifact_sha256"] = per_case
    handoff["exit_codes"]["leak_scan_reserved_runbook"] = verify2["checks"][
        "leak_scan_reserved_runbook"
    ]["exit_code"]
    handoff["exit_codes"]["token_scan"] = verify2["checks"]["token_scan"]["exit_code"]
    handoff["exit_codes"]["membership_and_sheet_pending"] = verify2["checks"][
        "membership_and_sheet_pending"
    ]["exit_code"]
    handoff["exit_codes"]["admission_checker"] = verify2["checks"]["admission_checker"]["exit_code"]
    handoff["exit_codes"]["pytest"] = verify2["checks"]["pytest"]["exit_code"]
    handoff["exit_codes"]["compileall"] = verify2["checks"]["compileall"]["exit_code"]
    handoff["commands"]["verification_command_count"] = len(vlog["commands"])
    write_json(handoff_path, handoff)

    final_hc = handoff_hash_checker(handoff_path)
    handoff = json.loads(handoff_path.read_text(encoding="utf-8"))
    handoff["exit_codes"]["handoff_hash_checker"] = final_hc
    write_json(handoff_path, handoff)
    final_hc2 = handoff_hash_checker(handoff_path)
    print("final_hash_checker", final_hc2)
    print(json.dumps(readiness["counts"], indent=2))
    for r in results:
        print(r["neutral_id"], r["proposed_crit_dual_arm_repro"], r.get("failure_stage"))
    return 0 if final_hc2 == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
