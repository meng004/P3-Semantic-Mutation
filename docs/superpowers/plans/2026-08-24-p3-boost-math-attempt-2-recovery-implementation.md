# Boost.Math Attempt-2 Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the V1 recovery design as corrected by V2, using one
durable attempt-2 orchestration interface and synthetic-only tests.

**Architecture:** `pilot_build.py` owns the deep one-shot orchestration
interface and durable attempt-2 ledger. `pilot_source.py` owns the internal
source-restoration interface. `pilot.py` is only the CLI adapter.

**Tech Stack:** Python 3.12, pytest, canonical JSON artifacts, pathlib,
standard-library archive/process/filesystem modules.

## Global Constraints

- QUALIFICATION_BASE_HEAD is exactly `0e51252f23dc3be4f82eb99e4f493c103f38c620`.
- RECOVERY_IMPLEMENTATION_HEAD remains `UNSET_UNTIL_INDEPENDENT_IMPLEMENTATION_PASS` until a later independent implementation review pins it. This implementation stage must not invent, guess, or write that SHA.
- V5 qualification remains bound to QUALIFICATION_BASE_HEAD. Attempt-2 production execution later runs detached at the pinned RECOVERY_IMPLEMENTATION_HEAD, not at QUALIFICATION_BASE_HEAD.
- V1 path `docs/superpowers/specs/2026-08-24-p3-boost-math-build-preflight-attempt-2-recovery-design.md` and V2 path `docs/superpowers/specs/2026-08-24-p3-boost-math-build-preflight-attempt-2-recovery-design-amendment-v2.md` must remain byte-identical. Later implementation must not edit, rename, or delete them.
- Attempt-1 constants `INTENT_PATH`, `RESULT_PATH`, `AUTHORIZATION_PATH`, `FROZEN_BUILD_ROOT`, and `FROZEN_HARNESS_ROOT` stay frozen. `run_build_preflight` must keep raising `E_PILOT_BUILD_PREEXISTING` on those paths.
- Attempt-2 durable paths are exactly:
  - `data/p3_v3/pilot/boost_math/user-auth-build-preflight-attempt-2.txt`
  - `data/p3_v3/pilot/boost_math/build-preflight-attempt-2-intent.json`
  - `data/p3_v3/pilot/boost_math/build-preflight-attempt-2-result.json`
- Attempt-2 runtime roots are exactly:
  - `/tmp/p3-boost-math-pilot-build-preflight-attempt-2`
  - `/tmp/p3-boost-math-pilot-build-preflight-attempt-2-harness`
  - `/tmp/p3-boost-math-pilot-build-preflight-attempt-2-logs`
- Production source root remains `/tmp/p3-boost-math-pilot-production-source`.
- Frozen archive path remains `/tmp/p3-boost-math-public-source-discovery/content-equivalence-r1/boost-math-dc86f3259c84f68ac7c4e2be11a1ed8567011240-projected.tar`.
- Frozen archive identity remains SHA-256 `6cad33704c8341995f271d93811dd3cf9751ed5edf8b9a73882662acd3db0392`, `99676160` bytes, format `TAR`.
- Frozen tree identity remains SHA-256 `93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8`, `4396` files, `95635487` bytes.
- V5 qualification root is `/tmp/p3-cxx-link-qualification`. Required filenames and file SHA-256 values are frozen in Task 2.
- Authority and durability order is exactly: read-only production entry gates, exclusive-create attempt-2 intent, `METADATA_CMAKE_VERSION`, `SOURCE_RESTORE`, `CMAKE_CONFIGURE`, `BASELINE_BUILD`, `BASELINE_SMOKE`, exclusive-create attempt-2 result, stop.
- Authorization and the later implementation verdict must exist and match later frozen bytes and hashes before intent creation. Attempt-2 intent and result must be absent before exclusive-create of the intent.
- `ATTEMPT2_AUTHORIZATION_BYTES`, `ATTEMPT2_AUTHORIZATION_SHA256`, and `ATTEMPT2_IMPLEMENTATION_VERDICT_SHA256` are fail-closed unbound sentinels in this implementation stage (`b""` and `"0" * 64`). Tests monkeypatch them to synthetic values they write. A later separately authorized constant-freeze, after RECOVERY_IMPLEMENTATION_HEAD is pinned, may replace only those three values. This plan does not invent the later production bytes.
- Later implementation-verdict path is `docs/review_20260824/boost_math_attempt_2_recovery_implementation_sol_high_review.md`.
- No standalone production `restore-source` CLI. Exactly one new CLI: `build-preflight-attempt-2`.
- Do not run `c++ --version`. Reuse and re-validate V5 compiler-version evidence. Require `os.path.realpath("/usr/bin/c++") == "/usr/lib/llvm-18/bin/clang"`.
- Do not run `git --version`. Reuse the V5 host-snapshot `git_version` field.
- Resolve the CMake path without executing CMake before intent. After intent, run `[resolved_cmake_path, "--version"]` exactly once as `METADATA_CMAKE_VERSION` with timeout `10`.
- Do not call `make_environment_snapshot()` from attempt-2.
- Cloud run ID and build/snapshot ID are executor/control-plane observations. Production Python must not claim qualification hashes prove those IDs. Intent and result store `executor_cloud_run_id=None`, `executor_build_snapshot_id=None`, and `verification_scope="EXECUTOR_CONTROL_PLANE_OBSERVATION"`.
- Failure before intent is `ENTRY_BLOCKED`: no durable write, dispatch authorization closed, no retry. Failure after intent must attempt exclusive publication of a terminal attempt-2 result. If result publication fails, the existing intent permanently closes the namespace.
- Claim ceiling: `execution_class=PILOT_ONLY`, `formal_denominator_membership=false`, `claims=blocked`, `no_retry=true`, `rq4_supported=false`, `attempt_2_authorized=false`.
- Tests are synthetic only. They must not execute a real compiler, linker, CMake, Boost archive, package manager, `qualify_cxx_link.py`, real build-preflight, or network access.
- This plan does not authorize implementation, commit, or attempt-2. The later implementation agent must stop after synthetic tests.
- Do not include git add, commit, push, or PR commands in any task.

## File Map

Later authorized implementation may edit only:

| Path | Ownership |
|---|---|
| `src/p3_v3/pilot_source.py` | Internal `run_restore_production_source` and restoration evidence schema. |
| `src/p3_v3/pilot_build.py` | Attempt-2 constants, V5 adapter, schemas, validators, `run_build_preflight_attempt_2`. |
| `scripts/p3_v3/pilot.py` | Single `build-preflight-attempt-2` CLI adapter. |
| `tests/p3_v3/test_pilot_source.py` | Restoration tests. Do not add names to `REQUIRED_SOURCE_PREPARATION_TESTS`. |
| `tests/p3_v3/test_pilot_build.py` | Adapter, schema, orchestrator, and regression tests. |
| `tests/p3_v3/test_pilot.py` | CLI adapter tests. |

This plan is the only file created by the current task. Later implementation must not edit V1, V2, attempt-1 evidence, qualification code, package policy, mutant/MR code, or manuscript builders.

## Frozen Names

| Symbol | Module | Signature or value |
|---|---|---|
| `FROZEN_PRODUCTION_ARCHIVE_PATH` | `pilot_source.py` | `Path("/tmp/p3-boost-math-public-source-discovery/content-equivalence-r1/boost-math-dc86f3259c84f68ac7c4e2be11a1ed8567011240-projected.tar")` |
| `FROZEN_PRODUCTION_SOURCE_ROOT` | `pilot_source.py` | `Path("/tmp/p3-boost-math-pilot-production-source")` |
| `FROZEN_ARCHIVE_SHA256` | `pilot_source.py` | `"6cad33704c8341995f271d93811dd3cf9751ed5edf8b9a73882662acd3db0392"` |
| `FROZEN_ARCHIVE_BYTES` | `pilot_source.py` | `99676160` |
| `FROZEN_ARCHIVE_FORMAT` | `pilot_source.py` | `"TAR"` |
| `FROZEN_MATERIALIZED_FILE_COUNT` | `pilot_source.py` | `4396` |
| `FROZEN_MATERIALIZED_TOTAL_BYTES` | `pilot_source.py` | `95635487` |
| `SOURCE_RESTORATION_SCHEMA` | `pilot_source.py` | `"p3-pilot-source-restoration-evidence-v1"` |
| `validate_source_restoration_evidence` | `pilot_source.py` | `(value: object) -> dict[str, Any]` |
| `run_restore_production_source` | `pilot_source.py` | `(archive: Path, materialize_root: Path) -> dict[str, Any]` |
| `QUALIFICATION_ROOT` | `pilot_build.py` | `Path("/tmp/p3-cxx-link-qualification")` |
| `QUALIFICATION_BASE_HEAD` | `pilot_build.py` | `"0e51252f23dc3be4f82eb99e4f493c103f38c620"` |
| `read_v5_qualification_evidence` | `pilot_build.py` | `(qualification_root: Path = QUALIFICATION_ROOT) -> dict[str, Any]` |
| `resolve_cmake_executable_path` | `pilot_build.py` | `() -> str` |
| `run_metadata_cmake_version` | `pilot_build.py` | `(cmake_path: str, log_root: Path) -> dict[str, Any]` |
| `validate_attempt2_intent` | `pilot_build.py` | `(value: object) -> dict[str, Any]` |
| `validate_attempt2_result` | `pilot_build.py` | `(value: object) -> dict[str, Any]` |
| `validate_attempt2_phase_result` | `pilot_build.py` | `(value: object) -> dict[str, Any]` |
| `validate_attempt2_environment` | `pilot_build.py` | `(value: object) -> dict[str, Any]` |
| `run_build_preflight_attempt_2` | `pilot_build.py` | `(archive: Path, source_root: Path, build_root: Path) -> dict[str, Any]` |

---

### Task 1: Internal source-restoration interface

**Files:**
- Modify: `src/p3_v3/pilot_source.py`
- Test: `tests/p3_v3/test_pilot_source.py`

**Interfaces:**
- Consumes: existing `read_production_archive_bytes`, `extract_archive_to_staging`, `capture_materialized_tree`, `validate_materialized_tree_with_phase1`, `validate_pilot_source_manifest`, `validate_pilot_source_preparation_result`, `classify_reconciliation`, `_staging_path`, `_staging_lexists`, `SOURCE_MANIFEST_PATH`, `SOURCE_PREPARATION_RESULT_PATH`, `FROZEN_NORMALIZED_SOURCE_TREE_SHA256`, `canonical_sha256`, `read_authority_snapshot`, `parse_canonical_authority_object`.
- Produces: `run_restore_production_source(archive: Path, materialize_root: Path) -> dict[str, Any]` returning a self-hashed object with exact keys `schema_version`, `execution_class`, `claims`, `disposition`, `archive_sha256`, `archive_bytes`, `normalized_tree_sha256`, `materialized_file_count`, `materialized_total_bytes`, `staging_published`, `root_published`, `started_at`, `ended_at`, `terminal_status`, `failure_reason`, `artifact_sha256`.
- Accepts no caller-selected manifest or result paths.
- Starts no subprocess.
- Exposes no production CLI.

Disposition values are exactly `RESTORED`, `REVALIDATED`, or `NOT_APPLIED`.
`terminal_status` values are exactly `PASS` or `FAIL`.
`failure_reason` is `None` on PASS. On FAIL it is one of: `WRONG_ARCHIVE_PATH`, `WRONG_SOURCE_ROOT`, `ARCHIVE_UNSAFE`, `ARCHIVE_HASH_MISMATCH`, `ARCHIVE_SIZE_MISMATCH`, `ARCHIVE_FORMAT_MISMATCH`, `EXTRACTION_UNSAFE`, `STAGING_EXISTS`, `STAGING_SYMLINK`, `ROOT_SYMLINK`, `INVALID_RECONCILIATION_STATE`, `TREE_HASH_MISMATCH`, `FILE_COUNT_MISMATCH`, `BYTE_COUNT_MISMATCH`, `INVALID_PASS_PAIR`.
`run_restore_production_source` always returns the validated evidence object. It does not raise `EvidenceError` for the listed failure reasons. It raises only if evidence self-hash construction fails, which is an implementation defect.

- [ ] **Step 1: Write the failing tests**

Append these helpers and tests to `tests/p3_v3/test_pilot_source.py`. Do not add the new test names to `REQUIRED_SOURCE_PREPARATION_TESTS`.

```python
def _forbid_subprocess(monkeypatch) -> list[tuple]:
    import subprocess
    from p3_v3 import pilot_source

    calls: list[tuple] = []

    def boom(*args, **kwargs):
        calls.append((args, kwargs))
        raise AssertionError("subprocess is forbidden in restoration")

    monkeypatch.setattr(subprocess, "Popen", boom)
    monkeypatch.setattr(subprocess, "run", boom)
    if hasattr(pilot_source, "subprocess"):
        monkeypatch.setattr(pilot_source.subprocess, "Popen", boom)
        monkeypatch.setattr(pilot_source.subprocess, "run", boom)
    return calls


def _write_closed_pass_pair(module, tmp_path: Path, snapshot, file_count: int, total_bytes: int) -> tuple[bytes, bytes]:
    from p3_v3.artifacts import write_canonical_json

    predecessors = ["0" * 64]
    manifest = _canonical_manifest(
        predecessors=predecessors,
        archive_sha256=snapshot.sha256,
        archive_bytes=snapshot.size,
        archive_format=snapshot.archive_format,
        file_count=file_count,
        total_bytes=total_bytes,
    )
    write_canonical_json(module.SOURCE_MANIFEST_PATH, manifest, exclusive=True)
    manifest_bytes = module.SOURCE_MANIFEST_PATH.read_bytes()
    manifest_sha256 = _sha256_bytes(manifest_bytes)
    result = _canonical_result(
        predecessors=sorted([*predecessors, manifest_sha256]),
        terminal_status="PASS",
        failure_reason=None,
        source_manifest_sha256=manifest_sha256,
        archive_sha256=snapshot.sha256,
        archive_bytes=snapshot.size,
        materialized_tree_sha256=module.FROZEN_NORMALIZED_SOURCE_TREE_SHA256,
    )
    write_canonical_json(module.SOURCE_PREPARATION_RESULT_PATH, result, exclusive=True)
    return manifest_bytes, module.SOURCE_PREPARATION_RESULT_PATH.read_bytes()


def _bind_restore_paths(monkeypatch, module, tmp_path: Path, archive: Path, root: Path) -> None:
    _patch_outputs(monkeypatch, module, tmp_path)
    monkeypatch.setattr(module, "FROZEN_PRODUCTION_ARCHIVE_PATH", archive)
    monkeypatch.setattr(module, "FROZEN_PRODUCTION_SOURCE_ROOT", root)


def test_restore_function_name_is_run_restore_production_source():
    from p3_v3 import pilot_source

    assert hasattr(pilot_source, "run_restore_production_source")
    assert callable(pilot_source.run_restore_production_source)


def test_restore_invalid_pass_no_root_success(tmp_path, monkeypatch):
    from p3_v3 import pilot_source

    calls = _forbid_subprocess(monkeypatch)
    members = {"payload/include/boost/math/constants/constants.hpp": b"pi\n"}
    archive = _write_tar(tmp_path / "ok.tar", members)
    snapshot = pilot_source.read_production_archive_bytes(archive)
    root = tmp_path / "materialize"
    staging = Path(str(root) + ".staging")
    _bind_restore_paths(monkeypatch, pilot_source, tmp_path, archive, root)
    probe = tmp_path / "probe"
    pilot_source.extract_archive_to_staging(snapshot, probe)
    tree = pilot_source.capture_materialized_tree(probe)
    file_count = len(tree.entries)
    total_bytes = sum(len(entry.content) for entry in tree.entries)
    monkeypatch.setattr(pilot_source, "FROZEN_MATERIALIZED_FILE_COUNT", file_count)
    monkeypatch.setattr(pilot_source, "FROZEN_MATERIALIZED_TOTAL_BYTES", total_bytes)
    _force_frozen_tree_hash(monkeypatch)
    before_manifest, before_result = _write_closed_pass_pair(
        pilot_source, tmp_path, snapshot, file_count, total_bytes
    )
    evidence = pilot_source.run_restore_production_source(archive, root)
    assert evidence["disposition"] == "RESTORED"
    assert evidence["terminal_status"] == "PASS"
    assert evidence["failure_reason"] is None
    assert evidence["archive_sha256"] == snapshot.sha256
    assert evidence["archive_bytes"] == snapshot.size
    assert evidence["normalized_tree_sha256"] == pilot_source.FROZEN_NORMALIZED_SOURCE_TREE_SHA256
    assert evidence["materialized_file_count"] == file_count
    assert evidence["materialized_total_bytes"] == total_bytes
    assert evidence["staging_published"] is True
    assert evidence["root_published"] is True
    assert root.is_dir()
    assert not staging.exists()
    assert (root / "include/boost/math/constants/constants.hpp").read_bytes() == b"pi\n"
    assert pilot_source.SOURCE_MANIFEST_PATH.read_bytes() == before_manifest
    assert pilot_source.SOURCE_PREPARATION_RESULT_PATH.read_bytes() == before_result
    assert calls == []
    validated = pilot_source.validate_source_restoration_evidence(evidence)
    assert validated["artifact_sha256"] == evidence["artifact_sha256"]


def test_restore_already_complete_revalidates(tmp_path, monkeypatch):
    from p3_v3 import pilot_source

    calls = _forbid_subprocess(monkeypatch)
    members = {"payload/include/ok.hpp": b"ok\n"}
    archive = _write_tar(tmp_path / "ok.tar", members)
    snapshot = pilot_source.read_production_archive_bytes(archive)
    root = tmp_path / "materialize"
    _bind_restore_paths(monkeypatch, pilot_source, tmp_path, archive, root)
    pilot_source.extract_archive_to_staging(snapshot, root)
    tree = pilot_source.capture_materialized_tree(root)
    file_count = len(tree.entries)
    total_bytes = sum(len(entry.content) for entry in tree.entries)
    monkeypatch.setattr(pilot_source, "FROZEN_MATERIALIZED_FILE_COUNT", file_count)
    monkeypatch.setattr(pilot_source, "FROZEN_MATERIALIZED_TOTAL_BYTES", total_bytes)
    _force_frozen_tree_hash(monkeypatch)
    before_manifest, before_result = _write_closed_pass_pair(
        pilot_source, tmp_path, snapshot, file_count, total_bytes
    )
    evidence = pilot_source.run_restore_production_source(archive, root)
    assert evidence["disposition"] == "REVALIDATED"
    assert evidence["terminal_status"] == "PASS"
    assert evidence["staging_published"] is False
    assert evidence["root_published"] is False
    assert pilot_source.SOURCE_MANIFEST_PATH.read_bytes() == before_manifest
    assert pilot_source.SOURCE_PREPARATION_RESULT_PATH.read_bytes() == before_result
    assert calls == []


def test_restore_wrong_archive_path(tmp_path, monkeypatch):
    from p3_v3 import pilot_source

    _forbid_subprocess(monkeypatch)
    archive = _write_tar(tmp_path / "ok.tar", {"payload/a.txt": b"a"})
    other = tmp_path / "other.tar"
    other.write_bytes(archive.read_bytes())
    root = tmp_path / "materialize"
    _bind_restore_paths(monkeypatch, pilot_source, tmp_path, archive, root)
    evidence = pilot_source.run_restore_production_source(other, root)
    assert evidence["disposition"] == "NOT_APPLIED"
    assert evidence["terminal_status"] == "FAIL"
    assert evidence["failure_reason"] == "WRONG_ARCHIVE_PATH"
    assert not root.exists()


def test_restore_archive_symlink(tmp_path, monkeypatch):
    from p3_v3 import pilot_source

    _forbid_subprocess(monkeypatch)
    real = _write_tar(tmp_path / "ok.tar", {"payload/a.txt": b"a"})
    link = tmp_path / "link.tar"
    link.symlink_to(real)
    root = tmp_path / "materialize"
    _bind_restore_paths(monkeypatch, pilot_source, tmp_path, link, root)
    evidence = pilot_source.run_restore_production_source(link, root)
    assert evidence["failure_reason"] == "ARCHIVE_UNSAFE"
    assert evidence["terminal_status"] == "FAIL"


def test_restore_archive_hash_size_format_mismatch(tmp_path, monkeypatch):
    from p3_v3 import pilot_source

    _forbid_subprocess(monkeypatch)
    archive = _write_tar(tmp_path / "ok.tar", {"payload/a.txt": b"a"})
    snapshot = pilot_source.read_production_archive_bytes(archive)
    root = tmp_path / "materialize"
    _bind_restore_paths(monkeypatch, pilot_source, tmp_path, archive, root)
    _force_frozen_tree_hash(monkeypatch)
    monkeypatch.setattr(pilot_source, "FROZEN_MATERIALIZED_FILE_COUNT", 1)
    monkeypatch.setattr(pilot_source, "FROZEN_MATERIALIZED_TOTAL_BYTES", 1)
    _write_closed_pass_pair(pilot_source, tmp_path, snapshot, 1, 1)
    wrong_hash = tmp_path / "manifest.json"
    # Re-write manifest with a different archive hash.
    from p3_v3.artifacts import write_canonical_json

    manifest = _canonical_manifest(
        predecessors=["0" * 64],
        archive_sha256="ab" * 32,
        archive_bytes=snapshot.size,
        archive_format="TAR",
        file_count=1,
        total_bytes=1,
    )
    pilot_source.SOURCE_MANIFEST_PATH.write_bytes(b"")
    write_canonical_json(pilot_source.SOURCE_MANIFEST_PATH, manifest, exclusive=False)
    evidence = pilot_source.run_restore_production_source(archive, root)
    assert evidence["failure_reason"] in {
        "ARCHIVE_HASH_MISMATCH",
        "INVALID_PASS_PAIR",
    }


def test_restore_unsafe_tar_member(tmp_path, monkeypatch):
    import tarfile
    import io
    from p3_v3 import pilot_source

    _forbid_subprocess(monkeypatch)
    archive = tmp_path / "unsafe.tar"
    with tarfile.open(archive, "w") as handle:
        info = tarfile.TarInfo("../escape.txt")
        payload = b"x"
        info.size = len(payload)
        handle.addfile(info, io.BytesIO(payload))
    snapshot = type("S", (), {"sha256": "ab" * 32, "size": archive.stat().st_size, "archive_format": "TAR"})
    root = tmp_path / "materialize"
    _bind_restore_paths(monkeypatch, pilot_source, tmp_path, archive, root)
    _force_frozen_tree_hash(monkeypatch)
    monkeypatch.setattr(pilot_source, "FROZEN_MATERIALIZED_FILE_COUNT", 1)
    monkeypatch.setattr(pilot_source, "FROZEN_MATERIALIZED_TOTAL_BYTES", 1)
    real = pilot_source.read_production_archive_bytes(archive)
    _write_closed_pass_pair(pilot_source, tmp_path, real, 1, 1)
    before_manifest = pilot_source.SOURCE_MANIFEST_PATH.read_bytes()
    before_result = pilot_source.SOURCE_PREPARATION_RESULT_PATH.read_bytes()
    evidence = pilot_source.run_restore_production_source(archive, root)
    assert evidence["failure_reason"] == "EXTRACTION_UNSAFE"
    assert not root.exists()
    assert not Path(str(root) + ".staging").exists()
    assert pilot_source.SOURCE_MANIFEST_PATH.read_bytes() == before_manifest
    assert pilot_source.SOURCE_PREPARATION_RESULT_PATH.read_bytes() == before_result


def test_restore_staging_collision_and_symlink(tmp_path, monkeypatch):
    from p3_v3 import pilot_source

    _forbid_subprocess(monkeypatch)
    archive = _write_tar(tmp_path / "ok.tar", {"payload/a.txt": b"a"})
    snapshot = pilot_source.read_production_archive_bytes(archive)
    root = tmp_path / "materialize"
    staging = Path(str(root) + ".staging")
    staging.mkdir()
    _bind_restore_paths(monkeypatch, pilot_source, tmp_path, archive, root)
    _force_frozen_tree_hash(monkeypatch)
    monkeypatch.setattr(pilot_source, "FROZEN_MATERIALIZED_FILE_COUNT", 1)
    monkeypatch.setattr(pilot_source, "FROZEN_MATERIALIZED_TOTAL_BYTES", 1)
    before_manifest, before_result = _write_closed_pass_pair(
        pilot_source, tmp_path, snapshot, 1, 1
    )
    evidence = pilot_source.run_restore_production_source(archive, root)
    assert evidence["failure_reason"] == "STAGING_EXISTS"
    assert staging.is_dir()
    assert pilot_source.SOURCE_MANIFEST_PATH.read_bytes() == before_manifest
    assert pilot_source.SOURCE_PREPARATION_RESULT_PATH.read_bytes() == before_result
    staging.rmdir()
    staging.symlink_to(tmp_path)
    evidence_link = pilot_source.run_restore_production_source(archive, root)
    assert evidence_link["failure_reason"] in {"STAGING_EXISTS", "STAGING_SYMLINK"}


def test_restore_partial_orphan_root(tmp_path, monkeypatch):
    from p3_v3 import pilot_source

    _forbid_subprocess(monkeypatch)
    archive = _write_tar(tmp_path / "ok.tar", {"payload/a.txt": b"a"})
    root = tmp_path / "materialize"
    root.mkdir()
    (root / "orphan.txt").write_text("x", encoding="utf-8")
    _bind_restore_paths(monkeypatch, pilot_source, tmp_path, archive, root)
    evidence = pilot_source.run_restore_production_source(archive, root)
    assert evidence["failure_reason"] == "INVALID_RECONCILIATION_STATE"
    assert (root / "orphan.txt").read_text(encoding="utf-8") == "x"


def test_restore_wrong_tree_count_bytes(tmp_path, monkeypatch):
    from p3_v3 import pilot_source

    _forbid_subprocess(monkeypatch)
    archive = _write_tar(tmp_path / "ok.tar", {"payload/a.txt": b"abc"})
    snapshot = pilot_source.read_production_archive_bytes(archive)
    root = tmp_path / "materialize"
    _bind_restore_paths(monkeypatch, pilot_source, tmp_path, archive, root)
    _force_frozen_tree_hash(monkeypatch)
    monkeypatch.setattr(pilot_source, "FROZEN_MATERIALIZED_FILE_COUNT", 99)
    monkeypatch.setattr(pilot_source, "FROZEN_MATERIALIZED_TOTAL_BYTES", 99)
    before_manifest, before_result = _write_closed_pass_pair(
        pilot_source, tmp_path, snapshot, 99, 99
    )
    evidence = pilot_source.run_restore_production_source(archive, root)
    assert evidence["failure_reason"] in {
        "FILE_COUNT_MISMATCH",
        "BYTE_COUNT_MISMATCH",
        "TREE_HASH_MISMATCH",
    }
    assert not root.exists()
    assert not Path(str(root) + ".staging").exists()
    assert pilot_source.SOURCE_MANIFEST_PATH.read_bytes() == before_manifest
    assert pilot_source.SOURCE_PREPARATION_RESULT_PATH.read_bytes() == before_result


def test_restore_invalid_crossed_pass_pair(tmp_path, monkeypatch):
    from p3_v3 import pilot_source
    from p3_v3.artifacts import write_canonical_json

    _forbid_subprocess(monkeypatch)
    archive = _write_tar(tmp_path / "ok.tar", {"payload/a.txt": b"a"})
    snapshot = pilot_source.read_production_archive_bytes(archive)
    root = tmp_path / "materialize"
    _bind_restore_paths(monkeypatch, pilot_source, tmp_path, archive, root)
    _write_closed_pass_pair(pilot_source, tmp_path, snapshot, 1, 1)
    crossed = _canonical_result(
        predecessors=["0" * 64],
        terminal_status="PASS",
        failure_reason=None,
        source_manifest_sha256="cd" * 32,
        archive_sha256=snapshot.sha256,
        archive_bytes=snapshot.size,
        materialized_tree_sha256=pilot_source.FROZEN_NORMALIZED_SOURCE_TREE_SHA256,
    )
    write_canonical_json(
        pilot_source.SOURCE_PREPARATION_RESULT_PATH,
        crossed,
        exclusive=False,
    )
    before_manifest = pilot_source.SOURCE_MANIFEST_PATH.read_bytes()
    evidence = pilot_source.run_restore_production_source(archive, root)
    assert evidence["failure_reason"] == "INVALID_PASS_PAIR"
    assert pilot_source.SOURCE_MANIFEST_PATH.read_bytes() == before_manifest


def test_restore_cleans_only_owned_staging(tmp_path, monkeypatch):
    from p3_v3 import pilot_source

    _forbid_subprocess(monkeypatch)
    archive = _write_tar(tmp_path / "ok.tar", {"payload/a.txt": b"a"})
    snapshot = pilot_source.read_production_archive_bytes(archive)
    root = tmp_path / "materialize"
    foreign = tmp_path / "foreign.staging"
    foreign.mkdir()
    (foreign / "keep.txt").write_text("keep", encoding="utf-8")
    _bind_restore_paths(monkeypatch, pilot_source, tmp_path, archive, root)
    _force_frozen_tree_hash(monkeypatch)
    monkeypatch.setattr(pilot_source, "FROZEN_MATERIALIZED_FILE_COUNT", 99)
    monkeypatch.setattr(pilot_source, "FROZEN_MATERIALIZED_TOTAL_BYTES", 99)
    _write_closed_pass_pair(pilot_source, tmp_path, snapshot, 99, 99)
    pilot_source.run_restore_production_source(archive, root)
    assert (foreign / "keep.txt").read_text(encoding="utf-8") == "keep"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot_source.py::test_restore_function_name_is_run_restore_production_source tests/p3_v3/test_pilot_source.py::test_restore_invalid_pass_no_root_success tests/p3_v3/test_pilot_source.py::test_restore_already_complete_revalidates tests/p3_v3/test_pilot_source.py::test_restore_wrong_archive_path tests/p3_v3/test_pilot_source.py::test_restore_archive_symlink tests/p3_v3/test_pilot_source.py::test_restore_archive_hash_size_format_mismatch tests/p3_v3/test_pilot_source.py::test_restore_unsafe_tar_member tests/p3_v3/test_pilot_source.py::test_restore_staging_collision_and_symlink tests/p3_v3/test_pilot_source.py::test_restore_partial_orphan_root tests/p3_v3/test_pilot_source.py::test_restore_wrong_tree_count_bytes tests/p3_v3/test_pilot_source.py::test_restore_invalid_crossed_pass_pair tests/p3_v3/test_pilot_source.py::test_restore_cleans_only_owned_staging -q`

Expected: FAIL with `AttributeError: module 'p3_v3.pilot_source' has no attribute 'run_restore_production_source'` or the same missing `validate_source_restoration_evidence`.

- [ ] **Step 3: Write the minimal implementation**

Append to `src/p3_v3/pilot_source.py` immediately before the `EXTRACTOR_POLICY_SHA256` runtime check at the file end:

```python
FROZEN_PRODUCTION_ARCHIVE_PATH = Path(
    "/tmp/p3-boost-math-public-source-discovery/content-equivalence-r1/"
    "boost-math-dc86f3259c84f68ac7c4e2be11a1ed8567011240-projected.tar"
)
FROZEN_PRODUCTION_SOURCE_ROOT = Path("/tmp/p3-boost-math-pilot-production-source")
FROZEN_ARCHIVE_SHA256 = (
    "6cad33704c8341995f271d93811dd3cf9751ed5edf8b9a73882662acd3db0392"
)
FROZEN_ARCHIVE_BYTES = 99676160
FROZEN_ARCHIVE_FORMAT = "TAR"
FROZEN_MATERIALIZED_FILE_COUNT = 4396
FROZEN_MATERIALIZED_TOTAL_BYTES = 95635487
SOURCE_RESTORATION_SCHEMA = "p3-pilot-source-restoration-evidence-v1"
SOURCE_RESTORATION_EVIDENCE_EXACT = {
    "schema_version": str,
    "execution_class": str,
    "claims": str,
    "disposition": str,
    "archive_sha256": str,
    "archive_bytes": int,
    "normalized_tree_sha256": str,
    "materialized_file_count": int,
    "materialized_total_bytes": int,
    "staging_published": bool,
    "root_published": bool,
    "started_at": str,
    "ended_at": str,
    "terminal_status": str,
    "failure_reason": (str, type(None)),
    "artifact_sha256": str,
}


def _restore_timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def validate_source_restoration_evidence(value: object) -> dict:
    validated = validate_exact_object(
        value,
        SOURCE_RESTORATION_EVIDENCE_EXACT,
        "source-restoration-evidence",
    )
    if validated["schema_version"] != SOURCE_RESTORATION_SCHEMA:
        raise EvidenceError("E_PILOT_SOURCE_RESTORE", "schema_version differs")
    if validated["execution_class"] != "PILOT_ONLY":
        raise EvidenceError("E_PILOT_SOURCE_RESTORE", "execution_class differs")
    if validated["claims"] != "blocked":
        raise EvidenceError("E_PILOT_SOURCE_RESTORE", "claims differ")
    if validated["disposition"] not in {"RESTORED", "REVALIDATED", "NOT_APPLIED"}:
        raise EvidenceError("E_PILOT_SOURCE_RESTORE", "disposition differs")
    if validated["terminal_status"] not in {"PASS", "FAIL"}:
        raise EvidenceError("E_PILOT_SOURCE_RESTORE", "terminal_status differs")
    if validated["terminal_status"] == "PASS" and validated["failure_reason"] is not None:
        raise EvidenceError("E_PILOT_SOURCE_RESTORE", "PASS must have null failure_reason")
    if validated["terminal_status"] == "FAIL" and validated["failure_reason"] is None:
        raise EvidenceError("E_PILOT_SOURCE_RESTORE", "FAIL must record failure_reason")
    body = {key: validated[key] for key in validated if key != "artifact_sha256"}
    if canonical_sha256(body) != validated["artifact_sha256"]:
        raise EvidenceError("E_PILOT_SOURCE_RESTORE_HASH", "self-hash differs")
    return validated


def _restoration_evidence(
    *,
    disposition: str,
    archive_sha256: str,
    archive_bytes: int,
    normalized_tree_sha256: str,
    materialized_file_count: int,
    materialized_total_bytes: int,
    staging_published: bool,
    root_published: bool,
    started_at: str,
    ended_at: str,
    terminal_status: str,
    failure_reason: str | None,
) -> dict:
    payload = {
        "schema_version": SOURCE_RESTORATION_SCHEMA,
        "execution_class": "PILOT_ONLY",
        "claims": "blocked",
        "disposition": disposition,
        "archive_sha256": archive_sha256,
        "archive_bytes": archive_bytes,
        "normalized_tree_sha256": normalized_tree_sha256,
        "materialized_file_count": materialized_file_count,
        "materialized_total_bytes": materialized_total_bytes,
        "staging_published": staging_published,
        "root_published": root_published,
        "started_at": started_at,
        "ended_at": ended_at,
        "terminal_status": terminal_status,
        "failure_reason": failure_reason,
        "artifact_sha256": "",
    }
    payload["artifact_sha256"] = canonical_sha256(
        {key: payload[key] for key in payload if key != "artifact_sha256"}
    )
    return validate_source_restoration_evidence(payload)


def _fail_restore(started_at: str, reason: str, snapshot: ArchiveSnapshot | None) -> dict:
    return _restoration_evidence(
        disposition="NOT_APPLIED",
        archive_sha256="" if snapshot is None else snapshot.sha256,
        archive_bytes=0 if snapshot is None else snapshot.size,
        normalized_tree_sha256="",
        materialized_file_count=0,
        materialized_total_bytes=0,
        staging_published=False,
        root_published=False,
        started_at=started_at,
        ended_at=_restore_timestamp(),
        terminal_status="FAIL",
        failure_reason=reason,
    )


def _load_closed_pass_pair() -> tuple[dict, dict, str, str]:
    try:
        manifest_raw, manifest_digest = read_authority_snapshot(
            SOURCE_MANIFEST_PATH, "source-manifest"
        )
        result_raw, result_digest = read_authority_snapshot(
            SOURCE_PREPARATION_RESULT_PATH, "source-preparation-result"
        )
        manifest = validate_pilot_source_manifest(
            parse_canonical_authority_object(manifest_raw, "source-manifest")
        )
        result = validate_pilot_source_preparation_result(
            parse_canonical_authority_object(result_raw, "source-preparation-result")
        )
    except EvidenceError:
        raise
    if result["terminal_status"] != "PASS" or result["source_manifest_sha256"] != manifest_digest:
        raise EvidenceError("E_PILOT_SOURCE_RESTORE", "INVALID_PASS_PAIR")
    return manifest, result, manifest_digest, result_digest


def run_restore_production_source(archive: Path, materialize_root: Path) -> dict:
    started_at = _restore_timestamp()
    archive = Path(archive)
    root = Path(materialize_root)
    if archive != FROZEN_PRODUCTION_ARCHIVE_PATH:
        return _fail_restore(started_at, "WRONG_ARCHIVE_PATH", None)
    if root != FROZEN_PRODUCTION_SOURCE_ROOT:
        return _fail_restore(started_at, "WRONG_SOURCE_ROOT", None)
    if os.path.lexists(root) and os.path.islink(root):
        return _fail_restore(started_at, "ROOT_SYMLINK", None)
    staging = _staging_path(root)
    if os.path.lexists(staging) and os.path.islink(staging):
        return _fail_restore(started_at, "STAGING_SYMLINK", None)
    if _staging_lexists(staging):
        return _fail_restore(started_at, "STAGING_EXISTS", None)
    try:
        manifest, result, _manifest_digest, _result_digest = _load_closed_pass_pair()
    except EvidenceError:
        return _fail_restore(started_at, "INVALID_PASS_PAIR", None)
    root_present = os.path.lexists(root)
    state = classify_reconciliation(
        manifest_present=True,
        result_present=True,
        root_present=root_present,
        manifest_valid=True,
        result_valid=True,
        result_status="PASS",
        closed_pair_consistent=result["source_manifest_sha256"]
        == hashlib.sha256(SOURCE_MANIFEST_PATH.read_bytes()).hexdigest(),
    )
    if state not in {"INVALID_PASS_NO_ROOT", "ALREADY_COMPLETE"}:
        return _fail_restore(started_at, "INVALID_RECONCILIATION_STATE", None)
    try:
        snapshot = read_production_archive_bytes(archive)
    except EvidenceError:
        return _fail_restore(started_at, "ARCHIVE_UNSAFE", None)
    if snapshot.sha256 != manifest["archive_sha256"] or snapshot.sha256 != FROZEN_ARCHIVE_SHA256:
        return _fail_restore(started_at, "ARCHIVE_HASH_MISMATCH", snapshot)
    if snapshot.size != manifest["archive_bytes"] or snapshot.size != FROZEN_ARCHIVE_BYTES:
        return _fail_restore(started_at, "ARCHIVE_SIZE_MISMATCH", snapshot)
    if snapshot.archive_format != FROZEN_ARCHIVE_FORMAT or snapshot.archive_format != "TAR":
        return _fail_restore(started_at, "ARCHIVE_FORMAT_MISMATCH", snapshot)
    if state == "ALREADY_COMPLETE":
        tree = capture_materialized_tree(root)
        try:
            tree_hash = validate_materialized_tree_with_phase1(tree)
        except EvidenceError:
            return _fail_restore(started_at, "TREE_HASH_MISMATCH", snapshot)
        file_count, total_bytes = _tree_metrics(tree)
        if file_count != FROZEN_MATERIALIZED_FILE_COUNT or file_count != manifest["materialized_file_count"]:
            return _fail_restore(started_at, "FILE_COUNT_MISMATCH", snapshot)
        if total_bytes != FROZEN_MATERIALIZED_TOTAL_BYTES or total_bytes != manifest["materialized_total_bytes"]:
            return _fail_restore(started_at, "BYTE_COUNT_MISMATCH", snapshot)
        if tree_hash != result["materialized_tree_sha256"]:
            return _fail_restore(started_at, "TREE_HASH_MISMATCH", snapshot)
        return _restoration_evidence(
            disposition="REVALIDATED",
            archive_sha256=snapshot.sha256,
            archive_bytes=snapshot.size,
            normalized_tree_sha256=tree_hash,
            materialized_file_count=file_count,
            materialized_total_bytes=total_bytes,
            staging_published=False,
            root_published=False,
            started_at=started_at,
            ended_at=_restore_timestamp(),
            terminal_status="PASS",
            failure_reason=None,
        )
    owned_staging = False
    try:
        extract_archive_to_staging(snapshot, staging)
        owned_staging = True
        tree = capture_materialized_tree(staging)
        try:
            tree_hash = validate_materialized_tree_with_phase1(tree)
        except EvidenceError:
            shutil.rmtree(staging, ignore_errors=True)
            return _fail_restore(started_at, "TREE_HASH_MISMATCH", snapshot)
        file_count, total_bytes = _tree_metrics(tree)
        if file_count != FROZEN_MATERIALIZED_FILE_COUNT or file_count != manifest["materialized_file_count"]:
            shutil.rmtree(staging, ignore_errors=True)
            return _fail_restore(started_at, "FILE_COUNT_MISMATCH", snapshot)
        if total_bytes != FROZEN_MATERIALIZED_TOTAL_BYTES or total_bytes != manifest["materialized_total_bytes"]:
            shutil.rmtree(staging, ignore_errors=True)
            return _fail_restore(started_at, "BYTE_COUNT_MISMATCH", snapshot)
        os.replace(staging, root)
        return _restoration_evidence(
            disposition="RESTORED",
            archive_sha256=snapshot.sha256,
            archive_bytes=snapshot.size,
            normalized_tree_sha256=tree_hash,
            materialized_file_count=file_count,
            materialized_total_bytes=total_bytes,
            staging_published=True,
            root_published=True,
            started_at=started_at,
            ended_at=_restore_timestamp(),
            terminal_status="PASS",
            failure_reason=None,
        )
    except EvidenceError:
        if owned_staging:
            shutil.rmtree(staging, ignore_errors=True)
        return _fail_restore(started_at, "EXTRACTION_UNSAFE", snapshot)
```

Call `validate_pilot_source_manifest(parse_canonical_authority_object(manifest_raw, "source-manifest"))`. The production signature already has `expected_predecessors=None`. Do not pass a second argument, do not invent a third validator, and do not change that function's signature.

Add `import time` to `pilot_source.py` if it is not already imported. Do not import `subprocess` into `pilot_source.py`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot_source.py::test_restore_function_name_is_run_restore_production_source tests/p3_v3/test_pilot_source.py::test_restore_invalid_pass_no_root_success tests/p3_v3/test_pilot_source.py::test_restore_already_complete_revalidates tests/p3_v3/test_pilot_source.py::test_restore_wrong_archive_path tests/p3_v3/test_pilot_source.py::test_restore_archive_symlink tests/p3_v3/test_pilot_source.py::test_restore_archive_hash_size_format_mismatch tests/p3_v3/test_pilot_source.py::test_restore_unsafe_tar_member tests/p3_v3/test_pilot_source.py::test_restore_staging_collision_and_symlink tests/p3_v3/test_pilot_source.py::test_restore_partial_orphan_root tests/p3_v3/test_pilot_source.py::test_restore_wrong_tree_count_bytes tests/p3_v3/test_pilot_source.py::test_restore_invalid_crossed_pass_pair tests/p3_v3/test_pilot_source.py::test_restore_cleans_only_owned_staging -q`

Expected: PASS for every listed test.

- [ ] **Step 5: Run restoration-adjacent regression**

Run: `PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot_source.py::test_required_names_are_defined tests/p3_v3/test_pilot_source.py::test_authorization_absent_writes_no_output -q`

Expected: PASS. Existing `run_validate_source` behavior is unchanged.

- [ ] **STOP_BEFORE_COMMIT**

Do not run git add, git commit, git push, or open a pull request.

---

### Task 2: V5 qualification-evidence adapter

**Files:**
- Modify: `src/p3_v3/pilot_build.py`
- Test: `tests/p3_v3/test_pilot_build.py`

**Interfaces:**
- Consumes: existing `read_authority_snapshot`, `parse_canonical_json_object`, `validate_sha256`, `_sha256_bytes`.
- Produces: `read_v5_qualification_evidence(qualification_root: Path = QUALIFICATION_ROOT) -> dict[str, Any]`.
- Must not rerun qualification, must not run `c++ --version`, must not run `git --version`, and must not claim artifact hashes prove Cloud IDs.

Frozen qualification filenames and SHA-256 values:

```python
QUALIFICATION_ROOT = Path("/tmp/p3-cxx-link-qualification")
QUALIFICATION_INTENT_NAME = "qualification-intent.json"
QUALIFICATION_RESULT_NAME = "qualification-result.json"
QUALIFICATION_MANIFEST_NAME = "qualification-manifest.json"
QUALIFICATION_SOURCE_NAME = "qualify.cpp"
QUALIFICATION_EXECUTABLE_NAME = "qualify"
QUALIFICATION_CXX_STDOUT_NAME = "METADATA_CXX_VERSION.stdout"
QUALIFICATION_CXX_STDERR_NAME = "METADATA_CXX_VERSION.stderr"
QUALIFICATION_INTENT_SHA256 = (
    "0a13766c565e89e32a21bc69ba0f449dc8a79c48a66a7bcace54c63faa224860"
)
QUALIFICATION_RESULT_SHA256 = (
    "68aaac07c2d5ad4f834f114e1a0ac011052176f2a20ea63793f483357c31f6c2"
)
QUALIFICATION_MANIFEST_SHA256 = (
    "5ef4c89e9601303b9e40e3fcda07c68055664cf53fb578d6efb1d39fc5f27c9a"
)
QUALIFICATION_EXECUTABLE_SHA256 = (
    "9d24d5298272942e95333acf18b05052b4c9d701aeaf92f7252a4d9666228b3b"
)
QUALIFICATION_SOURCE_SHA256 = (
    "91193433e324b0a1e525cfecac51f43ca0f6bd882e1c34292510c9740115bf5c"
)
QUALIFICATION_BASE_HEAD = "0e51252f23dc3be4f82eb99e4f493c103f38c620"
FROZEN_CXX_PATH = "/usr/bin/c++"
FROZEN_CXX_REALPATH = "/usr/lib/llvm-18/bin/clang"
```

Returned immutable evidence schema `ATTEMPT2_QUALIFICATION_EVIDENCE_EXACT`:

```python
ATTEMPT2_QUALIFICATION_EVIDENCE_SCHEMA = "p3-pilot-attempt-2-qualification-evidence-v1"
ATTEMPT2_QUALIFICATION_EVIDENCE_EXACT = {
    "schema_version": str,
    "execution_class": str,
    "claims": str,
    "qualification_root": str,
    "qualification_base_head": str,
    "intent_sha256": str,
    "result_sha256": str,
    "manifest_sha256": str,
    "source_sha256": str,
    "executable_sha256": str,
    "compiler_version_stdout_sha256": str,
    "compiler_version_stderr_sha256": str,
    "compiler_version_stdout": str,
    "compiler_version_stderr": str,
    "requested_compiler": str,
    "resolved_compiler_path": str,
    "resolved_compiler_realpath": str,
    "current_cxx_realpath": str,
    "host_git_version": str,
    "host_snapshot_sha256": str,
    "terminal_status": str,
    "failure_reason": (str, type(None)),
    "verification_scope": str,
    "artifact_sha256": str,
}
```

`verification_scope` must be exactly `ARTIFACT_HASH_AND_HOST_SNAPSHOT`. It must not be `EXECUTOR_CONTROL_PLANE_OBSERVATION`. Cloud IDs must be absent from this object.

- [ ] **Step 1: Write the failing tests**

Append to `tests/p3_v3/test_pilot_build.py`:

```python
def _forbid_all_subprocess(monkeypatch, module) -> list:
    import subprocess

    calls = []

    def boom(*args, **kwargs):
        calls.append((args, kwargs))
        raise AssertionError("subprocess is forbidden in qualification adapter")

    monkeypatch.setattr(subprocess, "Popen", boom)
    monkeypatch.setattr(subprocess, "run", boom)
    monkeypatch.setattr(module, "probe_identity", boom)
    monkeypatch.setattr(module, "make_environment_snapshot", boom)
    return calls


def _write_qual_tree(root: Path, *, intent=None, result=None, manifest=None, exe=b"ELF", stdout=b"clang\n", stderr=b"") -> None:
    from p3_v3.artifacts import write_canonical_json

    root.mkdir()
    write_canonical_json(root / "qualification-intent.json", intent or {
        "schema_version": "p3-cxx-link-qualification-intent-v1",
        "execution_class": "PILOT_TOOLCHAIN_QUALIFICATION_ONLY",
        "claims": "blocked",
        "formal_denominator_membership": False,
        "attempt_2_authorized": False,
        "no_retry": True,
        "repository_commit": "0e51252f23dc3be4f82eb99e4f493c103f38c620",
        "host_snapshot": {"git_version": "git version 2.43.0", "artifact_sha256": "11" * 32},
        "host_snapshot_sha256": "11" * 32,
        "spec_path": "docs/superpowers/specs/2026-08-18-p3-cursor-vm-cxx-link-qualification-design.md",
        "spec_sha256": "ff" * 32,
        "qualification_root": str(root),
        "requested_compiler": "c++",
        "resolved_compiler_path": "/usr/bin/c++",
        "resolved_compiler_realpath": "/usr/lib/llvm-18/bin/clang",
        "source_text": "int main(){return 0;}\n",
        "source_sha256": "91193433e324b0a1e525cfecac51f43ca0f6bd882e1c34292510c9740115bf5c",
        "compile_link_argv": ["c++"],
        "binary_run_argv": [str(root / "qualify")],
        "compile_timeout_seconds": 60,
        "run_timeout_seconds": 10,
        "compiler_version_timeout_seconds": 10,
        "relevant_environment": {},
        "artifact_sha256": "22" * 32,
    }, exclusive=True)
    write_canonical_json(root / "qualification-result.json", result or {
        "schema_version": "p3-cxx-link-qualification-result-v1",
        "execution_class": "PILOT_TOOLCHAIN_QUALIFICATION_ONLY",
        "claims": "blocked",
        "formal_denominator_membership": False,
        "attempt_2_authorized": False,
        "no_retry": True,
        "intent_sha256": "33" * 32,
        "repository_commit": "0e51252f23dc3be4f82eb99e4f493c103f38c620",
        "host_snapshot": {"git_version": "git version 2.43.0", "artifact_sha256": "11" * 32},
        "host_snapshot_sha256": "11" * 32,
        "spec_sha256": "ff" * 32,
        "compiler_version": {"process_role": "METADATA", "stdout_sha256": "44" * 32, "stderr_sha256": "55" * 32},
        "jobs": [],
        "source_sha256": "91193433e324b0a1e525cfecac51f43ca0f6bd882e1c34292510c9740115bf5c",
        "executable_sha256": "66" * 32,
        "executable_bytes": 4,
        "executable_regular": True,
        "executable_symlink": False,
        "terminal_status": "PASS",
        "failure_reason": None,
        "artifact_sha256": "77" * 32,
    }, exclusive=True)
    write_canonical_json(root / "qualification-manifest.json", manifest or {
        "schema_version": "p3-cxx-link-qualification-manifest-v1",
        "execution_class": "PILOT_TOOLCHAIN_QUALIFICATION_ONLY",
        "claims": "blocked",
        "formal_denominator_membership": False,
        "attempt_2_authorized": False,
        "no_retry": True,
        "intent_sha256": "33" * 32,
        "result_sha256": "88" * 32,
        "files": [],
        "artifact_sha256": "99" * 32,
    }, exclusive=True)
    (root / "qualify.cpp").write_bytes(b"int main(){return 0;}\n")
    (root / "qualify").write_bytes(exe)
    (root / "METADATA_CXX_VERSION.stdout").write_bytes(stdout)
    (root / "METADATA_CXX_VERSION.stderr").write_bytes(stderr)


def test_read_v5_qualification_evidence_name_exists():
    from p3_v3 import pilot_build

    assert callable(pilot_build.read_v5_qualification_evidence)


def test_read_v5_qualification_evidence_success(tmp_path, monkeypatch):
    from p3_v3 import pilot_build

    calls = _forbid_all_subprocess(monkeypatch, pilot_build)
    root = tmp_path / "qual"
    _write_qual_tree(root)
    monkeypatch.setattr(pilot_build, "QUALIFICATION_INTENT_SHA256", _sha256_bytes((root / "qualification-intent.json").read_bytes()))
    monkeypatch.setattr(pilot_build, "QUALIFICATION_RESULT_SHA256", _sha256_bytes((root / "qualification-result.json").read_bytes()))
    monkeypatch.setattr(pilot_build, "QUALIFICATION_MANIFEST_SHA256", _sha256_bytes((root / "qualification-manifest.json").read_bytes()))
    monkeypatch.setattr(pilot_build, "QUALIFICATION_EXECUTABLE_SHA256", _sha256_bytes(b"ELF"))
    monkeypatch.setattr(pilot_build, "os.path.realpath", lambda path: "/usr/lib/llvm-18/bin/clang" if str(path) in {"/usr/bin/c++", path} else path)
    evidence = pilot_build.read_v5_qualification_evidence(root)
    assert evidence["terminal_status"] == "PASS"
    assert evidence["qualification_base_head"] == "0e51252f23dc3be4f82eb99e4f493c103f38c620"
    assert evidence["host_git_version"] == "git version 2.43.0"
    assert evidence["verification_scope"] == "ARTIFACT_HASH_AND_HOST_SNAPSHOT"
    assert "bc-91edc0b7" not in str(evidence)
    assert "bld-20260824" not in str(evidence)
    assert calls == []


def test_read_v5_qualification_missing_and_hash_mismatch(tmp_path, monkeypatch):
    from p3_v3 import pilot_build
    from p3_v3.artifacts import EvidenceError

    _forbid_all_subprocess(monkeypatch, pilot_build)
    missing = tmp_path / "missing"
    with pytest.raises(EvidenceError):
        pilot_build.read_v5_qualification_evidence(missing)
    root = tmp_path / "qual"
    _write_qual_tree(root)
    with pytest.raises(EvidenceError):
        pilot_build.read_v5_qualification_evidence(root)
```

Add one test per missing file by deleting each of `qualification-intent.json`, `qualification-result.json`, `qualification-manifest.json`, `qualify.cpp`, `qualify`, `METADATA_CXX_VERSION.stdout`, and `METADATA_CXX_VERSION.stderr` in turn and expecting `EvidenceError`. Name them `test_read_v5_missing_intent`, `test_read_v5_missing_result`, `test_read_v5_missing_manifest`, `test_read_v5_missing_source`, `test_read_v5_missing_executable`, `test_read_v5_missing_cxx_stdout`, and `test_read_v5_missing_cxx_stderr`. Each body is:

```python
def test_read_v5_missing_intent(tmp_path, monkeypatch):
    from p3_v3 import pilot_build
    from p3_v3.artifacts import EvidenceError

    _forbid_all_subprocess(monkeypatch, pilot_build)
    root = tmp_path / "qual"
    _write_qual_tree(root)
    (root / "qualification-intent.json").unlink()
    with pytest.raises(EvidenceError):
        pilot_build.read_v5_qualification_evidence(root)
```

Repeat that pattern for the other six filenames. Also add `test_read_v5_wrong_commit`, `test_read_v5_wrong_compiler_realpath`, `test_read_v5_non_pass`, and `test_read_v5_symlink_root`, each raising `EvidenceError` and asserting the subprocess boom list stays empty.

- [ ] **Step 2: Run tests to verify they fail**

Run: `PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot_build.py::test_read_v5_qualification_evidence_name_exists tests/p3_v3/test_pilot_build.py::test_read_v5_qualification_evidence_success tests/p3_v3/test_pilot_build.py::test_read_v5_qualification_missing_and_hash_mismatch -q`

Expected: FAIL with `AttributeError: module 'p3_v3.pilot_build' has no attribute 'read_v5_qualification_evidence'`.

- [ ] **Step 3: Write the minimal implementation**

Add the frozen constants and these functions to `src/p3_v3/pilot_build.py`. Do not call `probe_identity`, `subprocess.run`, or `make_environment_snapshot`.

```python
def validate_attempt2_qualification_evidence(value: object) -> dict[str, Any]:
    validated = validate_exact_object(
        value,
        ATTEMPT2_QUALIFICATION_EVIDENCE_EXACT,
        "attempt-2-qualification-evidence",
    )
    if validated["schema_version"] != ATTEMPT2_QUALIFICATION_EVIDENCE_SCHEMA:
        raise EvidenceError("E_PILOT_ATTEMPT2_QUAL", "schema_version differs")
    if validated["verification_scope"] != "ARTIFACT_HASH_AND_HOST_SNAPSHOT":
        raise EvidenceError("E_PILOT_ATTEMPT2_QUAL", "verification_scope differs")
    if validated["qualification_base_head"] != QUALIFICATION_BASE_HEAD:
        raise EvidenceError("E_PILOT_ATTEMPT2_QUAL", "qualification base HEAD differs")
    body = {key: validated[key] for key in validated if key != "artifact_sha256"}
    if canonical_sha256(body) != validated["artifact_sha256"]:
        raise EvidenceError("E_PILOT_ATTEMPT2_QUAL_HASH", "self-hash differs")
    return validated


def read_v5_qualification_evidence(
    qualification_root: Path = QUALIFICATION_ROOT,
) -> dict[str, Any]:
    root = Path(qualification_root)
    if not root.exists() or root.is_symlink() or not root.is_dir():
        raise EvidenceError("E_PILOT_ATTEMPT2_QUAL", "qualification root is absent or unsafe")
    required = [
        QUALIFICATION_INTENT_NAME,
        QUALIFICATION_RESULT_NAME,
        QUALIFICATION_MANIFEST_NAME,
        QUALIFICATION_SOURCE_NAME,
        QUALIFICATION_EXECUTABLE_NAME,
        QUALIFICATION_CXX_STDOUT_NAME,
        QUALIFICATION_CXX_STDERR_NAME,
    ]
    files = {}
    for name in required:
        path = root / name
        raw, digest = read_authority_snapshot(path, name)
        files[name] = (raw, digest)
    if files[QUALIFICATION_INTENT_NAME][1] != QUALIFICATION_INTENT_SHA256:
        raise EvidenceError("E_PILOT_ATTEMPT2_QUAL", "intent hash differs")
    if files[QUALIFICATION_RESULT_NAME][1] != QUALIFICATION_RESULT_SHA256:
        raise EvidenceError("E_PILOT_ATTEMPT2_QUAL", "result hash differs")
    if files[QUALIFICATION_MANIFEST_NAME][1] != QUALIFICATION_MANIFEST_SHA256:
        raise EvidenceError("E_PILOT_ATTEMPT2_QUAL", "manifest hash differs")
    if files[QUALIFICATION_EXECUTABLE_NAME][1] != QUALIFICATION_EXECUTABLE_SHA256:
        raise EvidenceError("E_PILOT_ATTEMPT2_QUAL", "executable hash differs")
    if hashlib.sha256(files[QUALIFICATION_SOURCE_NAME][0]).hexdigest() != QUALIFICATION_SOURCE_SHA256:
        raise EvidenceError("E_PILOT_ATTEMPT2_QUAL", "source hash differs")
    intent = parse_canonical_json_object(files[QUALIFICATION_INTENT_NAME][0], "qual-intent")
    result = parse_canonical_json_object(files[QUALIFICATION_RESULT_NAME][0], "qual-result")
    manifest = parse_canonical_json_object(files[QUALIFICATION_MANIFEST_NAME][0], "qual-manifest")
    if intent.get("repository_commit") != QUALIFICATION_BASE_HEAD:
        raise EvidenceError("E_PILOT_ATTEMPT2_QUAL", "intent commit differs")
    if result.get("repository_commit") != QUALIFICATION_BASE_HEAD:
        raise EvidenceError("E_PILOT_ATTEMPT2_QUAL", "result commit differs")
    if result.get("terminal_status") != "PASS" or result.get("failure_reason") is not None:
        raise EvidenceError("E_PILOT_ATTEMPT2_QUAL", "qualification is not PASS")
    if intent.get("requested_compiler") != "c++":
        raise EvidenceError("E_PILOT_ATTEMPT2_QUAL", "requested compiler differs")
    if intent.get("resolved_compiler_path") != FROZEN_CXX_PATH:
        raise EvidenceError("E_PILOT_ATTEMPT2_QUAL", "resolved compiler path differs")
    if intent.get("resolved_compiler_realpath") != FROZEN_CXX_REALPATH:
        raise EvidenceError("E_PILOT_ATTEMPT2_QUAL", "resolved compiler realpath differs")
    current_real = os.path.realpath(FROZEN_CXX_PATH)
    if current_real != FROZEN_CXX_REALPATH:
        raise EvidenceError("E_PILOT_ATTEMPT2_QUAL", "current c++ realpath differs")
    host = intent["host_snapshot"]
    if not isinstance(host, dict) or not isinstance(host.get("git_version"), str):
        raise EvidenceError("E_PILOT_ATTEMPT2_QUAL", "host git_version missing")
    if manifest.get("intent_sha256") != files[QUALIFICATION_INTENT_NAME][1]:
        if manifest.get("intent_sha256") != intent.get("artifact_sha256"):
            raise EvidenceError("E_PILOT_ATTEMPT2_QUAL", "manifest intent cross-hash differs")
    stdout_raw = files[QUALIFICATION_CXX_STDOUT_NAME][0]
    stderr_raw = files[QUALIFICATION_CXX_STDERR_NAME][0]
    payload = {
        "schema_version": ATTEMPT2_QUALIFICATION_EVIDENCE_SCHEMA,
        "execution_class": PILOT_EXECUTION_CLASS,
        "claims": "blocked",
        "qualification_root": str(root),
        "qualification_base_head": QUALIFICATION_BASE_HEAD,
        "intent_sha256": files[QUALIFICATION_INTENT_NAME][1],
        "result_sha256": files[QUALIFICATION_RESULT_NAME][1],
        "manifest_sha256": files[QUALIFICATION_MANIFEST_NAME][1],
        "source_sha256": hashlib.sha256(files[QUALIFICATION_SOURCE_NAME][0]).hexdigest(),
        "executable_sha256": files[QUALIFICATION_EXECUTABLE_NAME][1],
        "compiler_version_stdout_sha256": hashlib.sha256(stdout_raw).hexdigest(),
        "compiler_version_stderr_sha256": hashlib.sha256(stderr_raw).hexdigest(),
        "compiler_version_stdout": stdout_raw.decode("utf-8", "replace"),
        "compiler_version_stderr": stderr_raw.decode("utf-8", "replace"),
        "requested_compiler": "c++",
        "resolved_compiler_path": FROZEN_CXX_PATH,
        "resolved_compiler_realpath": FROZEN_CXX_REALPATH,
        "current_cxx_realpath": current_real,
        "host_git_version": host["git_version"],
        "host_snapshot_sha256": intent["host_snapshot_sha256"],
        "terminal_status": "PASS",
        "failure_reason": None,
        "verification_scope": "ARTIFACT_HASH_AND_HOST_SNAPSHOT",
        "artifact_sha256": "",
    }
    payload["artifact_sha256"] = canonical_sha256(
        {key: payload[key] for key in payload if key != "artifact_sha256"}
    )
    return validate_attempt2_qualification_evidence(payload)
```

Import `canonical_sha256` from `p3_v3.artifacts` if `pilot_build.py` does not already import it.

Tests monkeypatch the three qualification file SHA-256 constants to the synthetic tree hashes. Production constants remain the V1 values.

- [ ] **Step 4: Run tests to verify they pass**

Run: `PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot_build.py -k read_v5 -q`

Expected: PASS.

- [ ] **Step 5: Regression**

Run: `PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot_build.py::test_required_build_preflight_names_are_frozen tests/p3_v3/test_pilot_build.py::test_no_retry_on_existing_intent -q`

Expected: PASS. Attempt-1 names and refusal remain unchanged.

- [ ] **STOP_BEFORE_COMMIT**

Do not run git add, git commit, git push, or open a pull request.

---

### Task 3: Attempt-2 schemas and validators

**Files:**
- Modify: `src/p3_v3/pilot_build.py`
- Test: `tests/p3_v3/test_pilot_build.py`

**Interfaces:**
- Consumes: Task 1 restoration evidence schema and Task 2 qualification evidence schema.
- Produces: constants and validators listed below. Attempt-1 `validate_intent`, `validate_result`, `INTENT_PATH`, `RESULT_PATH`, `AUTHORIZATION_PATH`, `FROZEN_BUILD_ROOT`, and `FROZEN_HARNESS_ROOT` remain unchanged.

```python
ATTEMPT2_AUTHORIZATION_PATH = Path(
    "data/p3_v3/pilot/boost_math/user-auth-build-preflight-attempt-2.txt"
)
ATTEMPT2_INTENT_PATH = Path(
    "data/p3_v3/pilot/boost_math/build-preflight-attempt-2-intent.json"
)
ATTEMPT2_RESULT_PATH = Path(
    "data/p3_v3/pilot/boost_math/build-preflight-attempt-2-result.json"
)
ATTEMPT2_BUILD_ROOT = Path("/tmp/p3-boost-math-pilot-build-preflight-attempt-2")
ATTEMPT2_HARNESS_ROOT = Path("/tmp/p3-boost-math-pilot-build-preflight-attempt-2-harness")
ATTEMPT2_LOG_ROOT = Path("/tmp/p3-boost-math-pilot-build-preflight-attempt-2-logs")
ATTEMPT2_IMPLEMENTATION_VERDICT_PATH = Path(
    "docs/review_20260824/boost_math_attempt_2_recovery_implementation_sol_high_review.md"
)
ATTEMPT2_AUTHORIZATION_BYTES = b""
ATTEMPT2_AUTHORIZATION_SHA256 = "0" * 64
ATTEMPT2_IMPLEMENTATION_VERDICT_SHA256 = "0" * 64
ATTEMPT2_PHASE_ORDER = (
    "METADATA_CMAKE_VERSION",
    "SOURCE_RESTORE",
    "CMAKE_CONFIGURE",
    "BASELINE_BUILD",
    "BASELINE_SMOKE",
)
ATTEMPT2_DEPENDENCY_DAG = [
    ["METADATA_CMAKE_VERSION", "SOURCE_RESTORE"],
    ["SOURCE_RESTORE", "CMAKE_CONFIGURE"],
    ["CMAKE_CONFIGURE", "BASELINE_BUILD"],
    ["BASELINE_BUILD", "BASELINE_SMOKE"],
]
ATTEMPT2_PLANNED_COUNT = 5
CMAKE_VERSION_TIMEOUT_SECONDS = 10
ATTEMPT2_INTENT_SCHEMA = "p3-pilot-build-preflight-attempt-2-intent-v1"
ATTEMPT2_RESULT_SCHEMA = "p3-pilot-build-preflight-attempt-2-result-v1"
ATTEMPT2_PHASE_SCHEMA = "p3-pilot-build-preflight-attempt-2-phase-v1"
ATTEMPT2_ENVIRONMENT_SCHEMA = "p3-pilot-build-preflight-attempt-2-environment-v1"
```

`ATTEMPT2_ENVIRONMENT_EXACT` keys: `schema_version`, `execution_class`, `denominator`, `cmake_executable`, `cmake_executable_path`, `cmake_version`, `cxx_compiler_executable`, `cxx_compiler_path`, `cxx_compiler_identity`, `cxx_compiler_version`, `cmake_generator`, `os_name`, `os_release`, `python_version`, `git_version`, `build_parallelism`, `nvcc_present`, `native_profiling_present`, `cuda_absence_blocking`, `fetchcontent_fully_disconnected`, `system_boost_fallback_accepted`, `disconnected_environment`, `qualification_evidence_sha256`, `verification_scope`, `executor_cloud_run_id`, `executor_build_snapshot_id`, `claims`, `artifact_sha256`.

Types: `cmake_version` is `(str, type(None))`; `executor_cloud_run_id` and `executor_build_snapshot_id` are `(str, type(None))`; `verification_scope` is `str`; remaining types match `BUILD_PREFLIGHT_ENVIRONMENT_EXACT` plus the new keys.

`ATTEMPT2_PHASE_EXACT` keys: `schema_version`, `execution_class`, `denominator`, `phase_id`, `phase_kind`, `dependency_phase_ids`, `argv`, `timeout_seconds`, `process_started`, `process_group_terminated`, `infrastructure_phase`, `terminal_status`, `failure_reason`, `exit_code`, `stdout_sha256`, `stderr_sha256`, `stdout_bytes`, `stderr_bytes`, `started_at`, `ended_at`, `wall_seconds`, `cpu_seconds`, `peak_rss_bytes`, `source_restoration_evidence`, `claims`, `artifact_sha256`.

`source_restoration_evidence` type is `(dict, type(None))`. Only the `SOURCE_RESTORE` phase may populate it. `METADATA_CMAKE_VERSION` must set `process_started=True` when it runs. `SOURCE_RESTORE` must set `process_started=False`.

`ATTEMPT2_INTENT_EXACT` keys: `schema_version`, `execution_class`, `denominator`, `plan_class`, `p12_item_id`, `neutral_snapshot_id`, `normalized_source_tree_sha256`, `controlled_subject_id`, `controlled_subject_source_id`, `build_descriptor_sha256`, `source_preparation_verdict_sha256`, `source_manifest_sha256`, `source_preparation_result_sha256`, `source_preparation_reviewed_commit`, `attempt1_implementation_verdict_sha256`, `attempt2_implementation_verdict_sha256`, `authorization_sha256`, `harness_cmake_sha256`, `harness_cxx_sha256`, `source_root`, `build_root`, `harness_root`, `log_root`, `archive_path`, `qualification_base_head`, `qualification_evidence_sha256`, `cmake_metadata_argv`, `cmake_configure_argv`, `baseline_build_argv`, `baseline_smoke_argv`, `cmake_version_timeout_seconds`, `cmake_configure_timeout_seconds`, `baseline_build_timeout_seconds`, `baseline_smoke_timeout_seconds`, `outer_timeout_seconds`, `build_parallelism`, `planned_count`, `dependency_dag`, `phase_order`, `environment_snapshot`, `environment_snapshot_sha256`, `producer_pid`, `producer_starttime`, `predecessor_sha256`, `no_retry`, `claims`, `formal_denominator_membership`, `rq4_supported`, `attempt_2_authorized`, `verification_scope`, `executor_cloud_run_id`, `executor_build_snapshot_id`, `artifact_sha256`.

`plan_class` must be `PILOT_BUILD_PREFLIGHT_ATTEMPT_2_ONLY`.
`phase_order` must equal `list(ATTEMPT2_PHASE_ORDER)`.
`planned_count` must equal `5`.
`attempt_2_authorized` must be `False`.
`cmake_metadata_argv` must equal `[cmake_executable_path, "--version"]`.
Intent `environment_snapshot["cmake_version"]` must be `None`.

`ATTEMPT2_RESULT_EXACT` keys: all intent identity fields that `BUILD_PREFLIGHT_RESULT_EXACT` already has, plus `attempt2_implementation_verdict_sha256`, `qualification_base_head`, `qualification_evidence_sha256`, `phase_order`, `phases`, `source_restoration_disposition`, `verification_scope`, `executor_cloud_run_id`, `executor_build_snapshot_id`, `attempt_2_authorized`, `log_root`, `archive_path`. `jobs` must be absent. `phases` is `list` of length 5.

Validators must reject attempt-1 schema versions, wrong namespace paths, wrong phase count or order, a later phase with `terminal_status != "NOT_STARTED"` after an earlier non-PASS phase, `formal_denominator_membership is True`, `claims != "blocked"`, `rq4_supported is True`, `attempt_2_authorized is True`, `no_retry is False`, PASS with missing build evidence, and an intent/result pair whose `intent_sha256` or qualification hashes drift.

- [ ] **Step 1: Write the failing tests**

```python
def test_attempt2_constants_are_distinct():
    from p3_v3 import pilot_build

    assert pilot_build.ATTEMPT2_INTENT_PATH != pilot_build.INTENT_PATH
    assert pilot_build.ATTEMPT2_RESULT_PATH != pilot_build.RESULT_PATH
    assert pilot_build.ATTEMPT2_BUILD_ROOT != pilot_build.FROZEN_BUILD_ROOT
    assert pilot_build.ATTEMPT2_AUTHORIZATION_PATH != pilot_build.AUTHORIZATION_PATH
    assert pilot_build.ATTEMPT2_PHASE_ORDER == (
        "METADATA_CMAKE_VERSION",
        "SOURCE_RESTORE",
        "CMAKE_CONFIGURE",
        "BASELINE_BUILD",
        "BASELINE_SMOKE",
    )


def test_attempt2_intent_rejects_attempt1_schema():
    from p3_v3 import pilot_build
    from p3_v3.artifacts import EvidenceError

    with pytest.raises(EvidenceError):
        pilot_build.validate_attempt2_intent({"schema_version": "p3-pilot-build-preflight-intent-v1"})


def test_attempt2_result_rejects_wrong_phase_order():
    from p3_v3 import pilot_build
    from p3_v3.artifacts import EvidenceError

    value = {"schema_version": "p3-pilot-build-preflight-attempt-2-result-v1", "phases": []}
    with pytest.raises(EvidenceError):
        pilot_build.validate_attempt2_result(value)
```

Add `test_attempt2_phase_source_restore_forbids_subprocess_claim`, which builds a `SOURCE_RESTORE` phase with `process_started=True` and expects `EvidenceError`.
Add `test_attempt2_environment_rejects_cloud_id_proof_scope`, which sets `verification_scope` to `QUALIFICATION_HASH_PROVES_CLOUD_IDS` and expects `EvidenceError`.
Add `test_attempt1_validate_intent_still_rejects_attempt2_schema`, calling `pilot_build.validate_intent` with `schema_version=p3-pilot-build-preflight-attempt-2-intent-v1` and expecting `EvidenceError`.

- [ ] **Step 2: Run tests to verify they fail**

Run: `PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot_build.py::test_attempt2_constants_are_distinct tests/p3_v3/test_pilot_build.py::test_attempt2_intent_rejects_attempt1_schema tests/p3_v3/test_pilot_build.py::test_attempt2_result_rejects_wrong_phase_order -q`

Expected: FAIL with missing `ATTEMPT2_INTENT_PATH` or `validate_attempt2_intent`.

- [ ] **Step 3: Write the minimal implementation**

Add the constants and exact-key maps. Then add the validator functions written immediately below. Do not modify the attempt-1 validators.

`validate_attempt2_phase_result` extra rules:
- `phase_id == phase_kind`
- `phase_id` is in `ATTEMPT2_PHASE_ORDER`
- if `phase_id == "SOURCE_RESTORE"` then `process_started is False` and `argv == []`
- if `phase_id == "METADATA_CMAKE_VERSION"` and `terminal_status != "NOT_STARTED"` then `process_started is True` and `argv` ends with `"--version"`
- if `phase_id != "SOURCE_RESTORE"` then `source_restoration_evidence is None`

Add these validators. Do not modify attempt-1 validators.

```python
def _require_self_hash(validated, context):
    body = {key: validated[key] for key in validated if key != "artifact_sha256"}
    if canonical_sha256(body) != validated["artifact_sha256"]:
        raise EvidenceError("E_PILOT_ATTEMPT2_HASH", f"{context} self-hash differs")
    return validated


def validate_attempt2_environment(value):
    validated = validate_exact_object(value, ATTEMPT2_ENVIRONMENT_EXACT, "attempt-2-environment")
    if validated["schema_version"] != ATTEMPT2_ENVIRONMENT_SCHEMA:
        raise EvidenceError("E_PILOT_ATTEMPT2_ENV", "schema_version differs")
    if validated["verification_scope"] != "EXECUTOR_CONTROL_PLANE_OBSERVATION":
        raise EvidenceError("E_PILOT_ATTEMPT2_ENV", "verification_scope differs")
    if validated["executor_cloud_run_id"] is not None or validated["executor_build_snapshot_id"] is not None:
        raise EvidenceError("E_PILOT_ATTEMPT2_ENV", "production must not bind cloud IDs")
    if validated["claims"] != "blocked":
        raise EvidenceError("E_PILOT_ATTEMPT2_ENV", "claims differ")
    return _require_self_hash(validated, "environment")


def validate_attempt2_phase_result(value):
    validated = validate_exact_object(value, ATTEMPT2_PHASE_EXACT, "attempt-2-phase")
    if validated["schema_version"] != ATTEMPT2_PHASE_SCHEMA:
        raise EvidenceError("E_PILOT_ATTEMPT2_PHASE", "schema_version differs")
    if validated["phase_id"] != validated["phase_kind"] or validated["phase_id"] not in ATTEMPT2_PHASE_ORDER:
        raise EvidenceError("E_PILOT_ATTEMPT2_PHASE", "phase identity differs")
    if validated["phase_id"] == "SOURCE_RESTORE":
        if validated["process_started"] is True or validated["argv"] != []:
            raise EvidenceError("E_PILOT_ATTEMPT2_PHASE", "SOURCE_RESTORE must not start a subprocess")
    if validated["phase_id"] == "METADATA_CMAKE_VERSION" and validated["terminal_status"] != "NOT_STARTED":
        if validated["process_started"] is not True or list(validated["argv"][-1:]) != ["--version"]:
            raise EvidenceError("E_PILOT_ATTEMPT2_PHASE", "METADATA_CMAKE_VERSION argv differs")
    if validated["phase_id"] != "SOURCE_RESTORE" and validated["source_restoration_evidence"] is not None:
        raise EvidenceError("E_PILOT_ATTEMPT2_PHASE", "only SOURCE_RESTORE may carry restoration evidence")
    return _require_self_hash(validated, "phase")


def validate_attempt2_intent(value):
    validated = validate_exact_object(value, ATTEMPT2_INTENT_EXACT, "attempt-2-intent")
    if validated["schema_version"] != ATTEMPT2_INTENT_SCHEMA:
        raise EvidenceError("E_PILOT_ATTEMPT2_INTENT", "schema_version differs")
    if validated["plan_class"] != "PILOT_BUILD_PREFLIGHT_ATTEMPT_2_ONLY":
        raise EvidenceError("E_PILOT_ATTEMPT2_INTENT", "plan_class differs")
    if validated["build_root"] != ATTEMPT2_BUILD_ROOT.as_posix():
        raise EvidenceError("E_PILOT_ATTEMPT2_INTENT", "build_root differs")
    if validated["harness_root"] != ATTEMPT2_HARNESS_ROOT.as_posix():
        raise EvidenceError("E_PILOT_ATTEMPT2_INTENT", "harness_root differs")
    if validated["log_root"] != ATTEMPT2_LOG_ROOT.as_posix():
        raise EvidenceError("E_PILOT_ATTEMPT2_INTENT", "log_root differs")
    if validated["archive_path"] != ATTEMPT2_ARCHIVE_PATH.as_posix():
        raise EvidenceError("E_PILOT_ATTEMPT2_INTENT", "archive_path differs")
    if validated["phase_order"] != list(ATTEMPT2_PHASE_ORDER) or validated["planned_count"] != 5:
        raise EvidenceError("E_PILOT_ATTEMPT2_INTENT", "phase ledger differs")
    if validated["dependency_dag"] != [list(edge) for edge in ATTEMPT2_DEPENDENCY_DAG]:
        raise EvidenceError("E_PILOT_ATTEMPT2_INTENT", "dependency_dag differs")
    if (
        validated["no_retry"] is not True
        or validated["claims"] != "blocked"
        or validated["formal_denominator_membership"] is not False
        or validated["rq4_supported"] is not False
        or validated["attempt_2_authorized"] is not False
    ):
        raise EvidenceError("E_PILOT_ATTEMPT2_INTENT", "claim flags differ")
    if validated["qualification_base_head"] != QUALIFICATION_BASE_HEAD:
        raise EvidenceError("E_PILOT_ATTEMPT2_INTENT", "qualification_base_head differs")
    environment = validate_attempt2_environment(validated["environment_snapshot"])
    if environment["cmake_version"] is not None:
        raise EvidenceError("E_PILOT_ATTEMPT2_INTENT", "intent cmake_version must be null")
    if validated["cmake_metadata_argv"] != [environment["cmake_executable_path"], "--version"]:
        raise EvidenceError("E_PILOT_ATTEMPT2_INTENT", "cmake_metadata_argv differs")
    return _require_self_hash(validated, "intent")


def validate_attempt2_result(value):
    validated = validate_exact_object(value, ATTEMPT2_RESULT_EXACT, "attempt-2-result")
    if validated["schema_version"] != ATTEMPT2_RESULT_SCHEMA:
        raise EvidenceError("E_PILOT_ATTEMPT2_RESULT", "schema_version differs")
    if validated["phase_order"] != list(ATTEMPT2_PHASE_ORDER) or len(validated["phases"]) != 5:
        raise EvidenceError("E_PILOT_ATTEMPT2_RESULT", "phase ledger differs")
    seen_non_pass = False
    for index, phase in enumerate(validated["phases"]):
        checked = validate_attempt2_phase_result(phase)
        if checked["phase_id"] != ATTEMPT2_PHASE_ORDER[index]:
            raise EvidenceError("E_PILOT_ATTEMPT2_RESULT", "phase order differs")
        if seen_non_pass and checked["terminal_status"] != "NOT_STARTED":
            raise EvidenceError("E_PILOT_ATTEMPT2_RESULT", "later phase started after non-PASS")
        if checked["terminal_status"] != "PASS":
            seen_non_pass = True
    if validated["terminal_status"] == "PASS" and validated.get("cmake_cache_sha256") is None:
        raise EvidenceError("E_PILOT_ATTEMPT2_RESULT", "PASS must bind build evidence")
    if (
        validated["no_retry"] is not True
        or validated["claims"] != "blocked"
        or validated["formal_denominator_membership"] is not False
        or validated["rq4_supported"] is not False
        or validated["attempt_2_authorized"] is not False
    ):
        raise EvidenceError("E_PILOT_ATTEMPT2_RESULT", "claim flags differ")
    return _require_self_hash(validated, "result")


def validate_attempt2_pair(intent, intent_sha256, result):
    validate_attempt2_intent(intent)
    validate_attempt2_result(result)
    if result["intent_sha256"] != intent_sha256:
        raise EvidenceError("E_PILOT_ATTEMPT2_PAIR", "intent_sha256 differs")
    if result["qualification_evidence_sha256"] != intent["qualification_evidence_sha256"]:
        raise EvidenceError("E_PILOT_ATTEMPT2_PAIR", "qualification evidence hash differs")
    if result["authorization_sha256"] != intent["authorization_sha256"]:
        raise EvidenceError("E_PILOT_ATTEMPT2_PAIR", "authorization hash differs")
    if result["attempt2_implementation_verdict_sha256"] != intent["attempt2_implementation_verdict_sha256"]:
        raise EvidenceError("E_PILOT_ATTEMPT2_PAIR", "implementation verdict hash differs")
```

Define `ATTEMPT2_ARCHIVE_PATH` in `pilot_build.py` as the frozen archive Path so this module does not import `pilot_source` at import time.

- [ ] **Step 4: Run tests to verify they pass**

Run: `PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot_build.py::test_attempt2_constants_are_distinct tests/p3_v3/test_pilot_build.py::test_attempt2_intent_rejects_attempt1_schema tests/p3_v3/test_pilot_build.py::test_attempt2_result_rejects_wrong_phase_order tests/p3_v3/test_pilot_build.py::test_attempt2_phase_source_restore_forbids_subprocess_claim tests/p3_v3/test_pilot_build.py::test_attempt2_environment_rejects_cloud_id_proof_scope tests/p3_v3/test_pilot_build.py::test_attempt1_validate_intent_still_rejects_attempt2_schema -q`

Expected: PASS.

- [ ] **Step 5: Regression**

Run: `PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot_build.py::test_claims_denominator_rq4_invariants tests/p3_v3/test_pilot_build.py::test_exact_three_job_dag -q`

Expected: PASS.

- [ ] **STOP_BEFORE_COMMIT**

Do not run git add, git commit, git push, or open a pull request.

### Task 4: Durable one-shot orchestrator

**Files:**
- Modify: `src/p3_v3/pilot_build.py`
- Test: `tests/p3_v3/test_pilot_build.py`

**Interfaces:**
- Consumes: `run_restore_production_source`, `read_v5_qualification_evidence`, Task 3 validators, existing `write_harness`, `execute_job`, `write_canonical_json`, `write_job_start_marker`, `write_process_identity`, `producer_identity`, `_require_plan_and_implementation_verdicts`, `_require_source_preparation_identities`.
- Produces: `resolve_cmake_executable_path() -> str`, `run_metadata_cmake_version(cmake_path: str, log_root: Path) -> dict[str, Any]`, `build_attempt2_environment(qual: dict[str, Any], cmake_path: str) -> dict[str, Any]`, `run_build_preflight_attempt_2(archive: Path, source_root: Path, build_root: Path) -> dict[str, Any]`.

`run_build_preflight_attempt_2` accepts only the three frozen paths:

```text
archive = /tmp/p3-boost-math-public-source-discovery/content-equivalence-r1/boost-math-dc86f3259c84f68ac7c4e2be11a1ed8567011240-projected.tar
source_root = /tmp/p3-boost-math-pilot-production-source
build_root = /tmp/p3-boost-math-pilot-build-preflight-attempt-2
```

Owned order: read-only gates, exclusive-create intent, `METADATA_CMAKE_VERSION`, `SOURCE_RESTORE`, `CMAKE_CONFIGURE`, `BASELINE_BUILD`, `BASELINE_SMOKE`, exclusive-create result, stop.

Intent is complete before CMake execution because `resolve_cmake_executable_path` uses `shutil.which("cmake")`, `os.lstat`, and `os.path.realpath` only. Intent stores `cmake_metadata_argv = [resolved_path, "--version"]` and `environment_snapshot["cmake_version"] = None`. After exclusive-create of the intent, `run_metadata_cmake_version` runs `subprocess.run([cmake_path, "--version"], check=False, capture_output=True, timeout=10, shell=False)` exactly once.

Stdout path: `ATTEMPT2_LOG_ROOT / "METADATA_CMAKE_VERSION.stdout"`.
Stderr path: `ATTEMPT2_LOG_ROOT / "METADATA_CMAKE_VERSION.stderr"`.
Start marker: `ATTEMPT2_LOG_ROOT / "METADATA_CMAKE_VERSION.start.json"`.
Process identity: `ATTEMPT2_LOG_ROOT / "METADATA_CMAKE_VERSION.identity.json"`.

V5 compiler and git fields replace `c++ --version` and `git --version`. `build_attempt2_environment` never calls `probe_identity` or `make_environment_snapshot`.

Roots: `ATTEMPT2_BUILD_ROOT`, `ATTEMPT2_HARNESS_ROOT`, and `ATTEMPT2_LOG_ROOT` are absent before intent. After intent, create `ATTEMPT2_LOG_ROOT` before metadata. After SOURCE_RESTORE PASS, create harness and build roots and call `write_harness`.

Configure argv after binding cmake path:

```text
[cmake_path, -S, ATTEMPT2_HARNESS_ROOT, -B, ATTEMPT2_BUILD_ROOT, -G, Unix Makefiles, -DCMAKE_BUILD_TYPE=Release, -DCMAKE_CXX_STANDARD=14, -DCMAKE_CXX_STANDARD_REQUIRED=ON, -DBOOST_MATH_STANDALONE=1, -DBOOST_MATH_PILOT_SOURCE_INCLUDE=/tmp/p3-boost-math-pilot-production-source/include, -DCMAKE_DISABLE_SOURCE_CHANGES=ON, -DCMAKE_DISABLE_IN_SOURCE_BUILD=ON, -DFETCHCONTENT_FULLY_DISCONNECTED=ON, -DFETCHCONTENT_UPDATES_DISCONNECTED=ON, -DCMAKE_FIND_USE_PACKAGE_REGISTRY=OFF, -DCMAKE_FIND_USE_SYSTEM_PACKAGE_REGISTRY=OFF, -DCMAKE_EXPORT_COMPILE_COMMANDS=ON, -DCMAKE_CXX_COMPILER=/usr/bin/c++]
```

Build argv: `[cmake_path, --build, ATTEMPT2_BUILD_ROOT, --parallel, 4]`.
Smoke argv: `[ATTEMPT2_BUILD_ROOT / boost_math_pilot_smoke]`.

Post-intent failure attempts exclusive result publication. Result-publication failure preserves the intent and raises `E_PILOT_ATTEMPT2_RESULT_PUBLICATION`. Pre-intent failure is `E_PILOT_ATTEMPT2_ENTRY_BLOCKED` and writes nothing. Existing intent at entry is `E_PILOT_ATTEMPT2_PREEXISTING` and writes no result. Later phases after the first non-PASS are `NOT_STARTED`. Already-complete source returns `REVALIDATED`. Attempt-1 paths are never opened for write.

- [ ] **Step 1: Write the failing tests**

```python
def test_resolve_cmake_executable_path_does_not_execute(monkeypatch):
    from p3_v3 import pilot_build

    calls = []
    monkeypatch.setattr(pilot_build.shutil, "which", lambda name: "/usr/bin/cmake" if name == "cmake" else None)
    monkeypatch.setattr(pilot_build.os.path, "realpath", lambda path: "/usr/bin/cmake")
    monkeypatch.setattr(pilot_build.os, "lstat", lambda path: type("S", (), {"st_mode": 0o100755})())

    def boom(*args, **kwargs):
        calls.append((args, kwargs))
        raise AssertionError("cmake must not start before intent")

    monkeypatch.setattr(pilot_build.subprocess, "run", boom)
    monkeypatch.setattr(pilot_build, "probe_identity", boom)
    assert pilot_build.resolve_cmake_executable_path() == "/usr/bin/cmake"
    assert calls == []


def test_attempt2_call_order_and_intent_before_metadata(tmp_path, monkeypatch):
    from p3_v3 import pilot_build

    order = []

    def record(name, result):
        def inner(*args, **kwargs):
            order.append(name)
            return result
        return inner

    monkeypatch.setattr(pilot_build, "ATTEMPT2_AUTHORIZATION_PATH", tmp_path / "auth.txt")
    monkeypatch.setattr(pilot_build, "ATTEMPT2_INTENT_PATH", tmp_path / "intent.json")
    monkeypatch.setattr(pilot_build, "ATTEMPT2_RESULT_PATH", tmp_path / "result.json")
    monkeypatch.setattr(pilot_build, "ATTEMPT2_BUILD_ROOT", tmp_path / "build")
    monkeypatch.setattr(pilot_build, "ATTEMPT2_HARNESS_ROOT", tmp_path / "harness")
    monkeypatch.setattr(pilot_build, "ATTEMPT2_LOG_ROOT", tmp_path / "logs")
    monkeypatch.setattr(pilot_build, "ATTEMPT2_IMPLEMENTATION_VERDICT_PATH", tmp_path / "verdict.json")
    monkeypatch.setattr(pilot_build, "ATTEMPT2_AUTHORIZATION_BYTES", b"SYNTH\n")
    monkeypatch.setattr(pilot_build, "ATTEMPT2_AUTHORIZATION_SHA256", _sha256_bytes(b"SYNTH\n"))
    (tmp_path / "auth.txt").write_bytes(b"SYNTH\n")
    (tmp_path / "verdict.json").write_text("PASS\n", encoding="utf-8")
    monkeypatch.setattr(pilot_build, "ATTEMPT2_IMPLEMENTATION_VERDICT_SHA256", _sha256_bytes(b"PASS\n"))
    monkeypatch.setattr(pilot_build, "_require_attempt2_entry_gates", record("gates", {
        "qual": {"artifact_sha256": "aa" * 32, "compiler_version_stdout": "clang\n", "host_git_version": "git version 0"},
        "cmake_path": "/usr/bin/cmake",
        "auth_sha256": _sha256_bytes(b"SYNTH\n"),
        "verdict_sha256": _sha256_bytes(b"PASS\n"),
    }))
    monkeypatch.setattr(pilot_build, "_exclusive_create_attempt2_intent", record("intent", {"artifact_sha256": "bb" * 32}))
    monkeypatch.setattr(pilot_build, "run_metadata_cmake_version", record("metadata", {"terminal_status": "FAIL", "failure_reason": "NONZERO_EXIT"}))
    monkeypatch.setattr(pilot_build, "_write_attempt2_terminal_result", record("result", {"terminal_status": "FAIL"}))
    monkeypatch.setattr("p3_v3.pilot_source.run_restore_production_source", record("restore", {"terminal_status": "PASS"}))
    archive = Path("/tmp/p3-boost-math-public-source-discovery/content-equivalence-r1/boost-math-dc86f3259c84f68ac7c4e2be11a1ed8567011240-projected.tar")
    monkeypatch.setattr(pilot_build, "ATTEMPT2_ARCHIVE_PATH", archive)
    returned = pilot_build.run_build_preflight_attempt_2(
        archive,
        Path("/tmp/p3-boost-math-pilot-production-source"),
        Path("/tmp/p3-boost-math-pilot-build-preflight-attempt-2"),
    )
    assert order[:3] == ["gates", "intent", "metadata"]
    assert "restore" not in order
    assert order[-1] == "result"
    assert returned["terminal_status"] == "FAIL"


def test_entry_blocked_writes_nothing(tmp_path, monkeypatch):
    from p3_v3 import pilot_build
    from p3_v3.artifacts import EvidenceError

    monkeypatch.setattr(pilot_build, "ATTEMPT2_INTENT_PATH", tmp_path / "intent.json")
    monkeypatch.setattr(pilot_build, "ATTEMPT2_RESULT_PATH", tmp_path / "result.json")
    monkeypatch.setattr(
        pilot_build,
        "_require_attempt2_entry_gates",
        lambda: (_ for _ in ()).throw(EvidenceError("E_PILOT_ATTEMPT2_ENTRY_BLOCKED", "auth absent")),
    )
    writes = []
    monkeypatch.setattr(pilot_build, "write_canonical_json", lambda *a, **k: writes.append(a))
    with pytest.raises(EvidenceError, match="E_PILOT_ATTEMPT2_ENTRY_BLOCKED"):
        pilot_build.run_build_preflight_attempt_2(
            Path("/tmp/p3-boost-math-public-source-discovery/content-equivalence-r1/boost-math-dc86f3259c84f68ac7c4e2be11a1ed8567011240-projected.tar"),
            Path("/tmp/p3-boost-math-pilot-production-source"),
            Path("/tmp/p3-boost-math-pilot-build-preflight-attempt-2"),
        )
    assert writes == []
    assert not (tmp_path / "intent.json").exists()


def test_result_publication_failure_preserves_intent(tmp_path, monkeypatch):
    from p3_v3 import pilot_build
    from p3_v3.artifacts import EvidenceError

    intent_path = tmp_path / "intent.json"
    intent_path.write_text("{}\n", encoding="utf-8")
    monkeypatch.setattr(pilot_build, "ATTEMPT2_INTENT_PATH", intent_path)
    monkeypatch.setattr(pilot_build, "ATTEMPT2_RESULT_PATH", tmp_path / "result.json")
    monkeypatch.setattr(pilot_build, "_require_attempt2_entry_gates", lambda: {
        "qual": {"artifact_sha256": "aa" * 32, "compiler_version_stdout": "clang\n", "host_git_version": "git"},
        "cmake_path": "/usr/bin/cmake",
        "auth_sha256": "cc" * 32,
        "verdict_sha256": "dd" * 32,
    })
    monkeypatch.setattr(pilot_build, "_exclusive_create_attempt2_intent", lambda **k: {"artifact_sha256": "bb" * 32})
    monkeypatch.setattr(pilot_build, "run_metadata_cmake_version", lambda *a, **k: {"terminal_status": "FAIL", "failure_reason": "NONZERO_EXIT"})
    monkeypatch.setattr(
        pilot_build,
        "_write_attempt2_terminal_result",
        lambda **k: (_ for _ in ()).throw(EvidenceError("E_PILOT_ATTEMPT2_RESULT_PUBLICATION", "RESULT_PUBLICATION_FAILURE")),
    )
    with pytest.raises(EvidenceError, match="E_PILOT_ATTEMPT2_RESULT_PUBLICATION"):
        pilot_build.run_build_preflight_attempt_2(
            Path("/tmp/p3-boost-math-public-source-discovery/content-equivalence-r1/boost-math-dc86f3259c84f68ac7c4e2be11a1ed8567011240-projected.tar"),
            Path("/tmp/p3-boost-math-pilot-production-source"),
            Path("/tmp/p3-boost-math-pilot-build-preflight-attempt-2"),
        )
    assert intent_path.exists()


def test_orphan_intent_closes_namespace(tmp_path, monkeypatch):
    from p3_v3 import pilot_build
    from p3_v3.artifacts import EvidenceError

    intent = tmp_path / "intent.json"
    intent.write_text("{}\n", encoding="utf-8")
    monkeypatch.setattr(pilot_build, "ATTEMPT2_INTENT_PATH", intent)
    monkeypatch.setattr(pilot_build, "ATTEMPT2_RESULT_PATH", tmp_path / "result.json")
    with pytest.raises(EvidenceError, match="E_PILOT_ATTEMPT2_PREEXISTING"):
        pilot_build.run_build_preflight_attempt_2(
            Path("/tmp/p3-boost-math-public-source-discovery/content-equivalence-r1/boost-math-dc86f3259c84f68ac7c4e2be11a1ed8567011240-projected.tar"),
            Path("/tmp/p3-boost-math-pilot-production-source"),
            Path("/tmp/p3-boost-math-pilot-build-preflight-attempt-2"),
        )
    assert not (tmp_path / "result.json").exists()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot_build.py::test_resolve_cmake_executable_path_does_not_execute tests/p3_v3/test_pilot_build.py::test_attempt2_call_order_and_intent_before_metadata tests/p3_v3/test_pilot_build.py::test_entry_blocked_writes_nothing tests/p3_v3/test_pilot_build.py::test_result_publication_failure_preserves_intent tests/p3_v3/test_pilot_build.py::test_orphan_intent_closes_namespace -q`

Expected: FAIL with missing `run_build_preflight_attempt_2` or `resolve_cmake_executable_path`.

- [ ] **Step 3: Write the minimal implementation**

Add `resolve_cmake_executable_path`, `run_metadata_cmake_version`, `_require_attempt2_entry_gates`, `build_attempt2_environment`, `_exclusive_create_attempt2_intent`, `_pad_phases`, `_phase_from_metadata`, `_phase_from_restoration`, `_phase_from_job`, `_attempt2_configure_spec`, `_attempt2_build_spec`, `_attempt2_smoke_spec`, `_write_attempt2_terminal_result`, and `run_build_preflight_attempt_2` to `src/p3_v3/pilot_build.py`.

`resolve_cmake_executable_path` must not call `subprocess`.
`run_metadata_cmake_version` must use timeout `10` and argv `[cmake_path, "--version"]`.
`_require_attempt2_entry_gates` must require authorization bytes and verdict hash, absent attempt-2 intent/result/roots, present attempt-1 evidence, `_require_source_preparation_identities`, `_require_plan_and_implementation_verdicts`, and `read_v5_qualification_evidence`.
`run_build_preflight_attempt_2` must follow the owned order. If metadata is not PASS, do not call restore. If restore is not PASS, do not configure. Pad remaining phases with `NOT_STARTED`. On result-publication failure, preserve the intent.

`execute_job` is invoked only after intent creation. Tests monkeypatch it.

- [ ] **Step 4: Run tests to verify they pass**

Run: `PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot_build.py::test_resolve_cmake_executable_path_does_not_execute tests/p3_v3/test_pilot_build.py::test_attempt2_call_order_and_intent_before_metadata tests/p3_v3/test_pilot_build.py::test_entry_blocked_writes_nothing tests/p3_v3/test_pilot_build.py::test_result_publication_failure_preserves_intent tests/p3_v3/test_pilot_build.py::test_orphan_intent_closes_namespace -q`

Expected: PASS.

- [ ] **Step 5: Regression**

Run: `PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot_build.py::test_no_retry_on_existing_intent tests/p3_v3/test_pilot_build.py::test_second_invocation_never_reruns tests/p3_v3/test_pilot_build.py::test_preexisting_build_root -q`

Expected: PASS.

- [ ] **STOP_BEFORE_COMMIT**

Do not run git add, git commit, git push, or open a pull request.

### Task 5: CLI adapter

**Files:**
- Modify: `scripts/p3_v3/pilot.py`
- Test: `tests/p3_v3/test_pilot.py`

**Interfaces:**
- Consumes: `run_build_preflight_attempt_2(archive: Path, source_root: Path, build_root: Path) -> dict[str, Any]`.
- Produces: one argparse subcommand `build-preflight-attempt-2` with `--archive`, `--source-root`, and `--build-root`.
- Must not add `restore-source`.

```python
    attempt2 = sub.add_parser("build-preflight-attempt-2")
    attempt2.add_argument("--archive", required=True)
    attempt2.add_argument("--source-root", required=True)
    attempt2.add_argument("--build-root", required=True)
```

```python
        elif args.command == "build-preflight-attempt-2":
            from p3_v3.pilot_build import run_build_preflight_attempt_2

            run_build_preflight_attempt_2(
                Path(args.archive),
                Path(args.source_root),
                Path(args.build_root),
            )
```

Leave `write-plan`, `validate-plan`, `validate-source`, and `build-preflight` unmodified.

- [ ] **Step 1: Write the failing tests**

```python
def test_attempt2_cli_dispatches_single_interface(monkeypatch):
    import scripts.p3_v3.pilot as pilot_cli

    calls = []

    def fake(archive, source_root, build_root):
        calls.append((archive, source_root, build_root))
        return {"terminal_status": "FAIL"}

    monkeypatch.setattr("p3_v3.pilot_build.run_build_preflight_attempt_2", fake)
    argv = [
        "build-preflight-attempt-2",
        "--archive",
        "/tmp/p3-boost-math-public-source-discovery/content-equivalence-r1/boost-math-dc86f3259c84f68ac7c4e2be11a1ed8567011240-projected.tar",
        "--source-root",
        "/tmp/p3-boost-math-pilot-production-source",
        "--build-root",
        "/tmp/p3-boost-math-pilot-build-preflight-attempt-2",
    ]
    assert pilot_cli.main(argv) == 0
    assert len(calls) == 1


def test_attempt2_cli_evidence_error_is_exit_1(monkeypatch):
    import scripts.p3_v3.pilot as pilot_cli
    from p3_v3.artifacts import EvidenceError

    def boom(archive, source_root, build_root):
        raise EvidenceError("E_PILOT_ATTEMPT2_PATH", "CLI paths must equal frozen paths")

    monkeypatch.setattr("p3_v3.pilot_build.run_build_preflight_attempt_2", boom)
    code = pilot_cli.main(
        [
            "build-preflight-attempt-2",
            "--archive",
            "/tmp/wrong.tar",
            "--source-root",
            "/tmp/p3-boost-math-pilot-production-source",
            "--build-root",
            "/tmp/p3-boost-math-pilot-build-preflight-attempt-2",
        ]
    )
    assert code == 1


def test_attempt2_cli_has_no_restore_source():
    import scripts.p3_v3.pilot as pilot_cli

    parser = pilot_cli.build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["restore-source", "--archive", "x", "--materialize-root", "y"])


def test_existing_cli_commands_remain():
    import scripts.p3_v3.pilot as pilot_cli

    parser = pilot_cli.build_parser()
    assert parser.parse_args(["write-plan", "--markdown", "a", "--output", "b"]).command == "write-plan"
    assert parser.parse_args(["validate-plan", "--plan", "a"]).command == "validate-plan"
    assert parser.parse_args(["validate-source", "--archive", "a", "--materialize-root", "b"]).command == "validate-source"
    assert parser.parse_args(
        [
            "build-preflight",
            "--source-root",
            "/tmp/p3-boost-math-pilot-production-source",
            "--build-root",
            "/tmp/p3-boost-math-pilot-build-preflight",
        ]
    ).command == "build-preflight"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot.py::test_attempt2_cli_dispatches_single_interface tests/p3_v3/test_pilot.py::test_attempt2_cli_evidence_error_is_exit_1 tests/p3_v3/test_pilot.py::test_attempt2_cli_has_no_restore_source tests/p3_v3/test_pilot.py::test_existing_cli_commands_remain -q`

Expected: FAIL because `build-preflight-attempt-2` is unknown.

- [ ] **Step 3: Write the minimal implementation**

Apply the parser addition and `main` branch shown above.

- [ ] **Step 4: Run tests to verify they pass**

Run: `PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot.py::test_attempt2_cli_dispatches_single_interface tests/p3_v3/test_pilot.py::test_attempt2_cli_evidence_error_is_exit_1 tests/p3_v3/test_pilot.py::test_attempt2_cli_has_no_restore_source tests/p3_v3/test_pilot.py::test_existing_cli_commands_remain -q`

Expected: PASS.

- [ ] **Step 5: Regression**

Run: `PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot.py::test_build_preflight_cli_accepts_only_frozen_roots tests/p3_v3/test_pilot.py::test_build_preflight_cli_rejects_overrides tests/p3_v3/test_pilot.py::test_validate_source_cli_accepts_only_archive_and_materialize_root -q`

Expected: PASS.

- [ ] **STOP_BEFORE_COMMIT**

Do not run git add, git commit, git push, or open a pull request.

### Task 6: Synthetic integration and regression suite

**Files:**
- Test: `tests/p3_v3/test_pilot_source.py`, `tests/p3_v3/test_pilot_build.py`, `tests/p3_v3/test_pilot.py`

Permitted tests are synthetic pytest tests only. They must not execute a real compiler, linker, CMake, Boost archive, package manager, `qualify_cxx_link.py`, real `run_build_preflight`, or network access.

How tests prove that prohibition:
- `_forbid_subprocess` and `_forbid_all_subprocess` replace `subprocess.Popen`, `subprocess.run`, `probe_identity`, and `make_environment_snapshot` with functions that record calls and raise `AssertionError`.
- Restoration tests use `_write_tar` and `_write_zip` under `tmp_path`. They never open the production 99676160-byte archive.
- Orchestrator tests monkeypatch `run_metadata_cmake_version` and `execute_job`.
- Qualification tests write synthetic JSON under `tmp_path` and monkeypatch the frozen SHA-256 constants.
- CLI tests monkeypatch `run_build_preflight_attempt_2`.

Exact focused commands for the later implementation stage:

```text
PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot_source.py -k restore -q
PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot_build.py -k "read_v5 or attempt2" -q
PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot.py -k attempt2 -q
```

Exact full regression command for the later implementation stage:

```text
PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot_source.py tests/p3_v3/test_pilot_build.py tests/p3_v3/test_pilot.py -q
```

Expected later observation: every collected test PASSes. No test starts `/usr/bin/c++`, `/usr/bin/cmake`, `apt`, or `qualify_cxx_link.py`.

Do not run any of those commands in this plan-only task.

- [ ] **STOP_BEFORE_COMMIT**

Do not run git add, git commit, git push, or open a pull request.

### Task 7: Self-review and handoff

**Files:**
- None. This task edits no production file.

- [ ] **Step 1: Plan self-review checklist**

- V1 §1 purpose remains: restore the missing production root and use a new attempt-2 namespace.
- V1 §3 attempt-1 immutability remains: `run_build_preflight` still raises `E_PILOT_BUILD_PREEXISTING`.
- V1 §4.2-§4.5 source identity, extractor policy, and publish-without-rewrite are implemented by `run_restore_production_source`.
- V2 identity split: QUALIFICATION_BASE_HEAD stays `0e51252f23dc3be4f82eb99e4f493c103f38c620`; RECOVERY_IMPLEMENTATION_HEAD stays `UNSET_UNTIL_INDEPENDENT_IMPLEMENTATION_PASS`.
- V2 authority order: gates, then exclusive intent, then metadata, restore, configure, build, smoke, result.
- V2 one CLI: `build-preflight-attempt-2` only.
- V2 five-phase ledger and DAG are exact: `METADATA_CMAKE_VERSION`, `SOURCE_RESTORE`, `CMAKE_CONFIGURE`, `BASELINE_BUILD`, `BASELINE_SMOKE`.
- V2 environment evidence: no second `c++ --version`, no `git --version`, one post-intent `cmake --version`.
- V2 control-plane boundary: production stores executor IDs as `None` with `verification_scope=EXECUTOR_CONTROL_PLANE_OBSERVATION`.
- No placeholder tokens remain.
- Function names are consistent: `run_restore_production_source`, `read_v5_qualification_evidence`, `run_build_preflight_attempt_2`, `resolve_cmake_executable_path`, `run_metadata_cmake_version`.
- Paths are consistent with V1 §5 and this plan File Map.
- Attempt-1 constants are never reused as attempt-2 paths.
- Claim ceiling remains blocked.
- No real workload is authorized.
- No git add, commit, push, or PR command appears in any task.
- Implementation must stop after synthetic tests.

- [ ] **STOP_BEFORE_COMMIT**

Do not run git add, git commit, git push, or open a pull request.

```text
IMPLEMENTATION_NOT_AUTHORIZED
COMMIT_NOT_AUTHORIZED
ATTEMPT_2_NOT_AUTHORIZED
STOP_AFTER_SYNTHETIC_TESTS
```
