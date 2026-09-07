# P3 Phase 2 Preflight and Pilot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Phase 2 preflight over an exact 35-subject blinded
source-materialization manifest, and a labelled `PILOT_ONLY` path that
never enters confirmatory schemas.

**Architecture:** A user-authorized archive root supplies 35 blinded
fixed-source tarballs. Preflight verifies archive, descriptor, and
normalized-tree hashes, runs 23 smokes, and retains 12 frozen failures.
Pilot uses independent intent/result/ledger schemas so scientific
`_INTENT_SCHEMA` and `SubjectProfile` stay untouched.

**Tech Stack:** Python 3.12; `src/p3_v3/preflight.py`;
`src/p3_v3/source_materialization.py`; `src/p3_v3/pilot.py`.

## Global Constraints

Master-plan Global Constraints apply. Additional rules:

- Archives are blinded fixed-source material, not P12 reveal.
- The input root is user-authorized. The plan does not invent archive
  paths from `derived-subject` hashes.
- Missing archive or hash mismatch blocks preflight.
- Do not recapture source or rerun Phase 1 discovery.
- Do not add `PILOT_ONLY` fields to scientific `_INTENT_SCHEMA`.

---

## File map

| File | Responsibility |
|---|---|
| `src/p3_v3/source_materialization.py` | 35-row archive bindings and safe extract |
| `src/p3_v3/preflight.py` | `run_phase2_preflight` |
| `src/p3_v3/pilot.py` | independent pilot schemas and driver |
| `scripts/p3_v3/evidence.py` | `run-phase2-preflight`, `pilot-only` |
| `tests/p3_v3/test_phase2_preflight.py` | Task A |
| `tests/p3_v3/test_phase2_pilot.py` | Task B |

---

## Source materialization contract

```python
from typing import Literal, TypedDict


class SourceArchiveBinding(TypedDict):
    neutral_snapshot_id: str
    controlled_subject_source_id: str
    archive_relative_path: str
    archive_sha256: str
    descriptor_relative_path: str
    descriptor_sha256: str
    normalized_source_tree_sha256: str
    build_descriptor_sha256: str
    extraction_policy_id: Literal["P3-SAFE-TAR-V1"]
    materialized_root_identity: str


class SourceMaterializationManifest(TypedDict):
    schema_version: Literal["p3-source-materialization-manifest-v1"]
    bindings: list[SourceArchiveBinding]
    expected_subject_count: Literal[35]
    artifact_sha256: str
```

Rules:

1. Manifest covers exactly 35 subjects from Phase 1 receipts.
2. `archive_sha256` must equal the bridge `source_archive_sha256`.
3. `normalized_source_tree_sha256` and `build_descriptor_sha256` must
   equal the derived-subject / bridge values.
4. `P3-SAFE-TAR-V1` extracts regular files only. It rejects symlink,
   absolute path, `..`, and device nodes.
5. `materialized_root_identity` is the canonical hash of the extracted
   file list after verification. Only that root may become cwd.
6. Absence or mismatch → `E_SOURCE_MATERIALIZATION` and preflight
   BLOCK.
7. Do not guess archive identity from a checkpoint.

---

### Task SM1: Source materialization manifest and safe extract

**Files:**
- Create: `src/p3_v3/source_materialization.py`
- Test: `tests/p3_v3/test_phase2_preflight.py`

**Interfaces:**

```python
def build_source_materialization_manifest(
    bindings: list[SourceArchiveBinding],
) -> SourceMaterializationManifest:
    """Require len(bindings)==35 and unique controlled_subject_source_id."""


def extract_verified_source(
    mount_root: Path,
    binding: SourceArchiveBinding,
    destination: Path,
) -> str:
    """Return materialized_root_identity or raise E_SOURCE_MATERIALIZATION."""
```

Production caller: `run_phase2_preflight`.

- [ ] **Step 1: Write the failing tests**

```python
import hashlib
import io
import tarfile
from pathlib import Path

import pytest

from p3_v3.artifacts import EvidenceError, canonical_sha256, file_sha256
from p3_v3.source_materialization import (
    build_source_materialization_manifest,
    extract_verified_source,
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _binding(index: int, archive_sha: str, tree_sha: str, desc_sha: str) -> dict:
    return {
        "neutral_snapshot_id": f"{index:064x}",
        "controlled_subject_source_id": f"{index + 100:064x}",
        "archive_relative_path": f"archives/{index:02d}.tar",
        "archive_sha256": archive_sha,
        "descriptor_relative_path": f"archives/{index:02d}.descriptor.json",
        "descriptor_sha256": desc_sha,
        "normalized_source_tree_sha256": tree_sha,
        "build_descriptor_sha256": desc_sha,
        "extraction_policy_id": "P3-SAFE-TAR-V1",
        "materialized_root_identity": "00" * 32,
    }


def test_manifest_requires_exactly_thirty_five_bindings() -> None:
    with pytest.raises(EvidenceError, match="E_SOURCE_MATERIALIZATION"):
        build_source_materialization_manifest([])


def test_extract_rejects_symlink(tmp_path: Path) -> None:
    archive = tmp_path / "archives"
    archive.mkdir()
    tar_path = archive / "00.tar"
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w") as handle:
        info = tarfile.TarInfo(name="link")
        info.type = tarfile.SYMTYPE
        info.linkname = "target"
        handle.addfile(info)
    tar_path.write_bytes(buffer.getvalue())
    descriptor = archive / "00.descriptor.json"
    descriptor.write_text("{}\n", encoding="utf-8")
    binding = _binding(0, file_sha256(tar_path), "11" * 32, file_sha256(descriptor))
    with pytest.raises(EvidenceError, match="E_SOURCE_MATERIALIZATION"):
        extract_verified_source(tmp_path, binding, tmp_path / "out")
```

- [ ] **Step 2: Run the tests and confirm they fail**

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest \
  tests/p3_v3/test_phase2_preflight.py::test_manifest_requires_exactly_thirty_five_bindings \
  tests/p3_v3/test_phase2_preflight.py::test_extract_rejects_symlink -q
```

Expected: FAIL because `source_materialization` is absent.

- [ ] **Step 3: Minimal implementation**

`build_source_materialization_manifest` validates length 35, unique
source IDs, and self-hash. `extract_verified_source` opens the tar,
rejects non-regular members, writes files under `destination`, and
returns `canonical_sha256` of the sorted `{path, sha256}` list. It
compares `file_sha256(archive)` and `file_sha256(descriptor)` to the
binding before extraction.

- [ ] **Step 4: Re-run those tests and confirm they pass**

Same command. Expected: PASS.

- [ ] **Step 5: Commit**

```bash
rtk git add src/p3_v3/source_materialization.py tests/p3_v3/test_phase2_preflight.py
rtk git commit -m "feat(p3-v3): bind 35 blinded source archives" -m "Safe-extract only after archive, descriptor, and path checks."
```

### Task A: Phase 2 preflight

**Files:**
- Modify: `src/p3_v3/preflight.py`
- Modify: `scripts/p3_v3/evidence.py`
- Test: `tests/p3_v3/test_phase2_preflight.py`

**Interfaces:**

```python
FORBIDDEN_PHASE2_INPUT_CLASSES = frozenset({
    "P12_IDENTITY", "P12_BUGGY", "P12_REVEAL", "REAL_JOB_INPUT",
    "DEFECT_PATCH", "REFERENCE_MR", "EVALUATED_MR",
})
FORBIDDEN_PHASE2_IDENTITY_FIELDS = frozenset({
    "p12_identity", "p12_identities", "p12_fault_id", "buggy_revision",
    "defect_patch", "reference_mr", "evaluated_mr", "package_c",
    "real_holdout",
})


def run_phase2_preflight(repo_root: Path, specification: Mapping[str, object]) -> dict:
    """Validate 35 bindings, run 23 smokes, retain 12 failures, reject Package C."""
```

Validation order for each phase input:

1. declared `class` against `FORBIDDEN_PHASE2_INPUT_CLASSES` →
   `E_PREFLIGHT_PACKAGE_C_CLASS`
2. file SHA-256 and directory tree SHA-256 against the spec →
   `E_PREFLIGHT_INPUT`
3. JSON objects for `FORBIDDEN_PHASE2_IDENTITY_FIELDS` →
   `E_PREFLIGHT_PACKAGE_C_FIELD`
4. path-marker defense → `E_PREFLIGHT_PACKAGE_C`

Inventory: exactly 35 rows from Phase 1 receipts plus the
materialization manifest. 23 `EXECUTABLE` rows have nonempty argv
derived from the execution-strategy registry smoke recipe. 12 retained
rows keep the frozen status and original reason and are not executed.

This task must not run the real 23 snapshots.

- [ ] **Step 1: Write the failing tests**

```python
import json
import subprocess
from pathlib import Path

import pytest

from p3_v3.artifacts import EvidenceError, canonical_sha256, file_sha256
from p3_v3.preflight import run_phase2_preflight


def _run(root: Path, *argv: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *argv],
        capture_output=True,
        check=True,
        text=True,
    ).stdout.strip()


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    _run(root, "init")
    _run(root, "config", "user.name", "Fixture")
    _run(root, "config", "user.email", "fixture@example.invalid")
    _run(root, "remote", "add", "origin", "git@github.com:Example/Repo.git")
    lock = root / "requirements.lock"
    lock.write_text("dependency==1\n", encoding="utf-8")
    input_path = root / "input.json"
    input_path.write_text("{}\n", encoding="utf-8")
    _run(root, "add", "requirements.lock", "input.json")
    _run(root, "commit", "-m", "fixture")
    return root


def git_repo_head(root: Path) -> str:
    return _run(root, "rev-parse", "HEAD")


def _write(path: Path, payload: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return file_sha256(path)


def _tree_sha(root: Path) -> str:
    files = []
    for path in sorted(root.rglob("*")):
        if path.is_file():
            files.append({"path": path.relative_to(root).as_posix(), "sha256": file_sha256(path)})
    return canonical_sha256(files)


def valid_phase2_spec(git_repo: Path, inventory: list[dict]) -> dict:
    lock = git_repo / "requirements.lock"
    lock_digest = _write(lock, b"lock\n")
    return {
        "schema_version": "p3-preflight-v1",
        "repository_identity": "github.com/meng004/P3-Semantic-Mutation",
        "expected_commit": "0" * 40,
        "dependency_lock_path": "requirements.lock",
        "dependency_lock_sha256": lock_digest,
        "phase_inputs": [],
        "smoke_commands": [],
        "timeout_seconds": 5,
        "phase_role": "CONSTRUCTION_A",
        "minimum_cpu_count": 0,
        "minimum_memory_bytes": 0,
        "minimum_disk_free_bytes": 0,
        "worker_limit": 1,
        "expected_os": "Darwin",
        "expected_python": "3.12",
        "compiler_commands": [],
        "model_label": "Grok 4.5 High",
        "environment_label": "phase2-fixture",
        "subject_inventory": inventory,
    }


def fixture_inventory() -> list[dict]:
    rows = []
    for index in range(23):
        rows.append({
            "neutral_snapshot_id": f"{index:064x}",
            "controlled_subject_id": f"{index + 200:064x}",
            "discovery_status": "EXECUTABLE",
            "original_failure_reason": None,
            "normalized_source_tree_sha256": f"{index + 300:064x}",
            "blinded_source_archive_sha256": f"{index + 400:064x}",
            "cwd_identity": f"cwd-{index}",
            "argv": ["/opt/anaconda3/bin/python", "-c", "print(0)"],
            "prerequisites": [],
            "expected_stdout_sha256": None,
            "expected_stderr_sha256": None,
        })
    reasons = (
        ["pyproject.toml is absent"] * 2
        + ["pyproject [project].name is absent"] * 2
        + ["CMakeLists.txt is absent"] * 5
        + ["ADAPTER_UNSUPPORTED"] * 3
    )
    statuses = ["ADAPTER_EXECUTION_FAILED"] * 9 + ["ADAPTER_UNSUPPORTED"] * 3
    for offset, (status, reason) in enumerate(zip(statuses, reasons)):
        index = 23 + offset
        rows.append({
            "neutral_snapshot_id": f"{index:064x}",
            "controlled_subject_id": f"{index + 200:064x}",
            "discovery_status": status,
            "original_failure_reason": reason,
            "normalized_source_tree_sha256": f"{index + 300:064x}",
            "blinded_source_archive_sha256": f"{index + 400:064x}",
            "cwd_identity": f"cwd-{index}",
            "argv": [],
            "prerequisites": [],
            "expected_stdout_sha256": None,
            "expected_stderr_sha256": None,
        })
    return rows


def test_phase2_preflight_inventory_covers_all_thirty_five_subjects(git_repo: Path) -> None:
    spec = valid_phase2_spec(git_repo, fixture_inventory())
    spec["expected_commit"] = git_repo_head(git_repo)
    receipt = run_phase2_preflight(git_repo, spec)
    assert len(receipt["subject_inventory"]) == 35
    assert receipt["smoke_executed_count"] == 23
    assert receipt["smoke_retained_count"] == 12


def test_phase2_preflight_rejects_forbidden_class_on_computed_hashes(git_repo: Path) -> None:
    spec = valid_phase2_spec(git_repo, fixture_inventory())
    spec["expected_commit"] = git_repo_head(git_repo)
    target = git_repo / "docs" / "notes.json"
    digest = _write(target, b"{}\n")
    spec["phase_inputs"].append({
        "path": "docs/notes.json",
        "sha256": digest,
        "class": "P12_REVEAL",
        "tree_sha256": _tree_sha(git_repo / "docs"),
    })
    with pytest.raises(EvidenceError, match="E_PREFLIGHT_PACKAGE_C_CLASS"):
        run_phase2_preflight(git_repo, spec)


def test_phase2_preflight_rejects_identity_field_on_computed_hashes(git_repo: Path) -> None:
    spec = valid_phase2_spec(git_repo, fixture_inventory())
    spec["expected_commit"] = git_repo_head(git_repo)
    target = git_repo / "public" / "notes.json"
    digest = _write(target, json.dumps({"p12_identity": "hidden"}).encode("utf-8") + b"\n")
    spec["phase_inputs"].append({
        "path": "public/notes.json",
        "sha256": digest,
        "class": "PUBLIC_DOC",
        "tree_sha256": _tree_sha(git_repo / "public"),
    })
    with pytest.raises(EvidenceError, match="E_PREFLIGHT_PACKAGE_C_FIELD"):
        run_phase2_preflight(git_repo, spec)
```

The `git_repo` fixture and `git_repo_head` helper are defined in this
test file. Do not import them from another test module. Do not use
`"ab" * 32` as a file digest in these tests.

- [ ] **Step 2: Run the tests and confirm they fail**

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest \
  tests/p3_v3/test_phase2_preflight.py::test_phase2_preflight_inventory_covers_all_thirty_five_subjects \
  tests/p3_v3/test_phase2_preflight.py::test_phase2_preflight_rejects_forbidden_class_on_computed_hashes \
  tests/p3_v3/test_phase2_preflight.py::test_phase2_preflight_rejects_identity_field_on_computed_hashes -q
```

Expected: FAIL because `run_phase2_preflight` is absent.

- [ ] **Step 3: Minimal implementation**

Add `run_phase2_preflight`. Call `run_preflight` after extra-field,
inventory, and Package C checks. Execute only the 23 executable smoke
rows. Do not call `create_intent`.

- [ ] **Step 4: Re-run those tests and confirm they pass**

Same command. Expected: PASS.

- [ ] **Step 5: Commit**

```bash
rtk git add src/p3_v3/preflight.py scripts/p3_v3/evidence.py \
  tests/p3_v3/test_phase2_preflight.py
rtk git commit -m "feat(p3-v3): add Phase 2 preflight with 35-subject inventory" -m "Run 23 smokes, retain 12 frozen failures, and reject Package C by class, tree, and fields."
```

### Task B: Independent PILOT_ONLY path

**Files:**
- Create: `src/p3_v3/pilot.py`
- Modify: `scripts/p3_v3/evidence.py`
- Test: `tests/p3_v3/test_phase2_pilot.py`

**Interfaces:**

```python
from typing import Literal, TypedDict

PILOT_ROLES = (
    "PASS",
    "FAIL_SCIENTIFIC",
    "FAIL_INFRASTRUCTURE",
    "INCONCLUSIVE",
    "MISSING_WITH_REASON",
    "SLOT_NOT_APPLICABLE",
    "SLOT_APPLICABLE",
)


class PilotIntent(TypedDict):
    schema_version: Literal["p3-pilot-intent-v1"]
    pilot_job_id: str
    pilot_subject_id: str
    execution_class: Literal["PILOT_ONLY"]
    denominator: Literal["PILOT_ONLY"]
    argv: list[str]
    cwd_identity: str
    input_sha256: list[str]
    timeout_seconds: int
    expected_terminal: str
    protocol_sha256: str
    environment_sha256: str
    artifact_sha256: str


def pilot_subject_id(role: str) -> str:
    return canonical_sha256({"domain": "P3-PILOT-SUBJECT-v1", "role": role})


def create_pilot_intent(attempt_dir: Path, intent: PilotIntent) -> None:
    """Write exclusive pilot intent.json. Do not call create_intent."""


def write_pilot_result(attempt_dir: Path, result: Mapping[str, object]) -> None:
    """Write exclusive pilot result.json."""


def verify_pilot_ledger(ledger_path: Path) -> list[dict]:
    """Verify the independent pilot ledger."""


def close_pilot_receipt(ledger_path: Path, expected_jobs: list[str]) -> dict:
    """Close the independent pilot receipt."""


def reject_pilot_artifact(candidate: Mapping[str, object]) -> None:
    """Raise E_PILOT_DENOMINATOR if schema_version startswith p3-pilot or execution_class==PILOT_ONLY."""


def run_pilot_only(root: Path, spec: Mapping[str, object]) -> dict:
    """Exercise the frozen synthetic pilot spec."""
```

Frozen synthetic pilot spec (exact):

| role | argv | expected_terminal |
|---|---|---|
| PASS | `["/opt/anaconda3/bin/python", "-c", "print('pilot-pass')"]` | PASS |
| FAIL_SCIENTIFIC | `["/opt/anaconda3/bin/python", "-c", "raise SystemExit(2)"]` | FAIL_SCIENTIFIC |
| FAIL_INFRASTRUCTURE | timeout 1 second against `["/opt/anaconda3/bin/python", "-c", "import time; time.sleep(30)"]` | FAIL_INFRASTRUCTURE plus one retry |
| INCONCLUSIVE | `["/opt/anaconda3/bin/python", "-c", "print('inconclusive')"]` mapped by fixture oracle to INCONCLUSIVE | INCONCLUSIVE |
| MISSING_WITH_REASON | argv names a missing fixture file | MISSING_WITH_REASON |
| SLOT_NOT_APPLICABLE | no job argv; slot predicate false | APPLICABILITY_CLOSED_NOT_APPLICABLE |
| SLOT_APPLICABLE | no job argv; slot predicate true | SITE_FROZEN |

Ledger path: `root / "pilot-ledger.jsonl"`.
Seeds: `canonical_sha256({"domain":"P3-PILOT-SEED-v1","role": role})`.
No P12 neutral IDs. No confirmatory ledger writes.

Confirmatory builders call `reject_pilot_artifact` at the entry
before any `SubjectProfile` validation.

- [ ] **Step 1: Write the failing tests**

```python
from pathlib import Path

import pytest

from p3_v3.artifacts import EvidenceError, canonical_sha256
from p3_v3.pilot import (
    PILOT_ROLES,
    close_pilot_receipt,
    create_pilot_intent,
    pilot_subject_id,
    reject_pilot_artifact,
    run_pilot_only,
)


def synthetic_pilot_spec(root: Path) -> dict:
    return {
        "schema_version": "p3-pilot-spec-v1",
        "ledger_path": str(root / "pilot-ledger.jsonl"),
        "roles": list(PILOT_ROLES),
    }


def test_pilot_subjects_are_labelled_and_rejected_by_class(tmp_path: Path) -> None:
    receipt = run_pilot_only(tmp_path, synthetic_pilot_spec(tmp_path))
    expected_ids = {pilot_subject_id(role) for role in PILOT_ROLES}
    assert receipt["denominator"] == "PILOT_ONLY"
    assert receipt["execution_class"] == "PILOT_ONLY"
    assert set(receipt["subject_ids"]) == expected_ids
    assert set(receipt["job_statuses"]) == {
        "PASS",
        "FAIL_SCIENTIFIC",
        "FAIL_INFRASTRUCTURE",
        "INCONCLUSIVE",
        "MISSING_WITH_REASON",
    }
    assert receipt["ledger_path"].endswith("pilot-ledger.jsonl")
    for artifact in receipt["pilot_artifacts"]:
        with pytest.raises(EvidenceError, match="E_PILOT_DENOMINATOR"):
            reject_pilot_artifact(artifact)


def test_pilot_not_applicable_slot_has_no_downstream_artifacts(tmp_path: Path) -> None:
    receipt = run_pilot_only(tmp_path, synthetic_pilot_spec(tmp_path))
    closed = receipt["not_applicable_slot"]
    assert closed["state"] == "APPLICABILITY_CLOSED_NOT_APPLICABLE"
    assert closed["contract"] is None
    assert closed["e_contract"] is None
    assert closed["patch"] is None
    assert closed["certification_witness"] is None


def test_create_pilot_intent_does_not_use_scientific_schema(tmp_path: Path) -> None:
    intent = {
        "schema_version": "p3-pilot-intent-v1",
        "pilot_job_id": "pilot-pass",
        "pilot_subject_id": pilot_subject_id("PASS"),
        "execution_class": "PILOT_ONLY",
        "denominator": "PILOT_ONLY",
        "argv": ["/opt/anaconda3/bin/python", "-c", "print('pilot-pass')"],
        "cwd_identity": str(tmp_path),
        "input_sha256": [canonical_sha256({"domain": "P3-PILOT-INPUT-v1", "role": "PASS"})],
        "timeout_seconds": 5,
        "expected_terminal": "PASS",
        "protocol_sha256": "aa" * 32,
        "environment_sha256": "bb" * 32,
        "artifact_sha256": "cc" * 32,
    }
    create_pilot_intent(tmp_path / "pilot-pass" / "1", intent)
    written = (tmp_path / "pilot-pass" / "1" / "intent.json").read_text(encoding="utf-8")
    assert "p3-pilot-intent-v1" in written
    assert "PRIMARY_CONTROLLED" not in written
```

- [ ] **Step 2: Run the tests and confirm they fail**

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest \
  tests/p3_v3/test_phase2_pilot.py -q
```

Expected: FAIL because `p3_v3.pilot` is absent.

- [ ] **Step 3: Minimal implementation**

Implement the independent schemas and `run_pilot_only` against the
frozen argv table. Write only `pilot-ledger.jsonl`. Do not import
`create_intent`.

- [ ] **Step 4: Re-run the tests and confirm they pass**

Same command. Expected: PASS.

- [ ] **Step 5: Commit**

```bash
rtk git add src/p3_v3/pilot.py scripts/p3_v3/evidence.py \
  tests/p3_v3/test_phase2_pilot.py
rtk git commit -m "feat(p3-v3): add independent PILOT_ONLY schemas" -m "Keep pilot artifacts out of scientific intent and subject schemas."
```

---

## Acceptance

1. Manifest requires 35 bindings.
2. Safe extract rejects symlinks.
3. Preflight covers 23/12 and rejects Package C by computed hashes.
4. Pilot uses `p3-pilot-intent-v1` and an independent ledger.
5. Claims remain blocked.
