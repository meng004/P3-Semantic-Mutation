# P3 Boost.Math Attempt-2 Archive Contract Update Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the unrecoverable historical Attempt-2 tar identity with the reproducible public Git projection approved in the 2026-08-26 design, publish only the exact verified archive, and regenerate the implementation verdict without running Attempt-2.

**Architecture:** Keep the source object and runtime workflow unchanged. Update the two active archive identity constants and their tests, append the supersession to the active V3 recovery amendment, rebind the implementation-verdict reader to this approved plan and the amended V3 hash, then publish the already generated Git archive only after independent byte and tree checks.

**Tech Stack:** Python 3.12, pytest, Git archive, Python `tarfile`, SHA-256, canonical JSON, Git.

## Global Constraints

- Upstream repository is `https://github.com/boostorg/math.git`.
- Witness commit is `04c2c248dfc5e35eeb7638152d5bd7c2985feef2`.
- Mainline witness is `03ea9c8d7dff1083facd134c8f641e006b68fdae`.
- Common Git root tree is `dc86f3259c84f68ac7c4e2be11a1ed8567011240`.
- Exclude only `build/Jamfile.v2`.
- Replacement archive SHA-256 is `e97524b457326fdb4d0ccd8f6d83cb33cdad920a76dffc4b508f628a0a70393d`.
- Replacement archive size is `99092480` bytes and format is `TAR`.
- Retained source identity stays `4396` files, `95635487` bytes, normalized tree SHA-256 `93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8`.
- Frozen archive path stays `/tmp/p3-boost-math-public-source-discovery/content-equivalence-r1/boost-math-dc86f3259c84f68ac7c4e2be11a1ed8567011240-projected.tar`.
- Claim ceiling stays `claims=blocked`, `rq4_supported=false`, and `formal_denominator_membership=false`.
- Do not run Attempt-2 or profiling in this plan.
- Preserve the historical 2026-08-17 launch packet and durable source-preparation evidence byte-for-byte.
- Prefix every shell command with `rtk`.

---

### Task 1: Update the active archive identity with a red-green test

**Files:**
- Modify: `tests/p3_v3/test_pilot_source.py:2199-2275`
- Modify: `src/p3_v3/pilot_source.py:76-83`
- Modify: `docs/superpowers/specs/2026-08-24-p3-boost-math-build-preflight-attempt-2-recovery-design-amendment-v3.md`

**Interfaces:**
- Consumes: existing `ATTEMPT2_ARCHIVE_PATH`, `ATTEMPT2_ARCHIVE_SHA256`, `ATTEMPT2_ARCHIVE_BYTES`, and `validate_source_restoration_evidence()`.
- Produces: active Attempt-2 archive identity equal to the approved reproducible Git projection, with unchanged restoration behavior.

- [ ] **Step 1: Add the focused identity test before changing production constants**

Add this test immediately before `_attempt2_fixture` in `tests/p3_v3/test_pilot_source.py`. It exercises the real source-entry consumer: the approved replacement identity must pass the archive gate, while the superseded identity must be rejected.

```python
def test_attempt2_source_entry_accepts_replacement_archive_identity(
    tmp_path, monkeypatch
):
    from p3_v3 import pilot_source

    archive = tmp_path / "projected.tar"
    source_root = tmp_path / "source"
    staging = tmp_path / "source.staging"
    replacement = pilot_source.ArchiveSnapshot(
        raw=b"",
        sha256="e97524b457326fdb4d0ccd8f6d83cb33cdad920a76dffc4b508f628a0a70393d",
        size=99092480,
        archive_format="TAR",
    )
    superseded = pilot_source.ArchiveSnapshot(
        raw=b"",
        sha256="6cad33704c8341995f271d93811dd3cf9751ed5edf8b9a73882662acd3db0392",
        size=99676160,
        archive_format="TAR",
    )
    observed = replacement
    monkeypatch.setattr(pilot_source, "ATTEMPT2_ARCHIVE_PATH", archive)
    monkeypatch.setattr(pilot_source, "ATTEMPT2_SOURCE_ROOT", source_root)
    monkeypatch.setattr(pilot_source, "ATTEMPT2_SOURCE_STAGING_ROOT", staging)
    monkeypatch.setattr(
        pilot_source, "read_production_archive_bytes", lambda _path: observed
    )
    monkeypatch.setattr(pilot_source, "verify_production_gate_chain", object)
    monkeypatch.setattr(
        pilot_source,
        "_inspect_state",
        lambda _chain, _root: ("INVALID_PASS_NO_ROOT", None, None),
    )

    assert (
        pilot_source._inspect_attempt2_source_entry(archive, source_root)
        == "INVALID_PASS_NO_ROOT"
    )

    observed = superseded
    with pytest.raises(EvidenceError, match="archive identity differs"):
        pilot_source._inspect_attempt2_source_entry(archive, source_root)
```

- [ ] **Step 2: Run the focused test and verify the expected red state**

Run:

```bash
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/p3_v3/test_pilot_source.py::test_attempt2_source_entry_accepts_replacement_archive_identity -q
```

Expected: FAIL because `ATTEMPT2_ARCHIVE_SHA256` is still `6cad3370...0392` and `ATTEMPT2_ARCHIVE_BYTES` is still `99676160`.

- [ ] **Step 3: Apply the minimal constant and evidence-fixture update**

In `src/p3_v3/pilot_source.py`, replace only the two identity bindings:

```python
ATTEMPT2_ARCHIVE_SHA256 = "e97524b457326fdb4d0ccd8f6d83cb33cdad920a76dffc4b508f628a0a70393d"
ATTEMPT2_ARCHIVE_BYTES = 99092480
```

In `test_source_restoration_evidence_rejects_missing_extra_type_value_timestamp_and_hash`, replace the hard-coded PASS sample with:

```python
        "disposition": "REVALIDATED",
        "archive_sha256": pilot_source.ATTEMPT2_ARCHIVE_SHA256,
        "archive_bytes": pilot_source.ATTEMPT2_ARCHIVE_BYTES,
```

Append a dated supersession section to the active V3 amendment. It must record the canonical `git archive` command, replacement SHA/size, unchanged normalized source identity, unchanged paths and claim ceiling, preservation of historical launch evidence, and the prohibition on starting Attempt-2 in this change.

Append exactly this section:

```markdown
## 2026-08-26 Archive Serialization Supersession

For missing-source restoration only, the active archive serialization identity
is superseded by the deterministic output of:

`git archive --format=tar --output=boost-math-dc86f3259c84f68ac7c4e2be11a1ed8567011240-projected.tar 04c2c248dfc5e35eeb7638152d5bd7c2985feef2 -- . ':(exclude)build/Jamfile.v2'`

The replacement archive SHA-256 is
`e97524b457326fdb4d0ccd8f6d83cb33cdad920a76dffc4b508f628a0a70393d`;
its size is `99092480` bytes and its format is `TAR`. The upstream repository,
witness commits, common Git root tree, excluded path, frozen archive path,
production source root, normalized tree SHA-256, file count, retained byte
count, claim ceiling, and no-retry state do not change. The 2026-08-17 launch
packet and durable source-preparation evidence remain historical records and
must not be rewritten. This supersession does not authorize or start another
Attempt-2 invocation or profiling run.
```

- [ ] **Step 4: Verify green for the focused identity and restoration evidence tests**

Run:

```bash
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/p3_v3/test_pilot_source.py::test_attempt2_source_entry_accepts_replacement_archive_identity tests/p3_v3/test_pilot_source.py::test_source_restoration_evidence_rejects_missing_extra_type_value_timestamp_and_hash -q
```

Expected: `2 passed`.

- [ ] **Step 5: Run the complete source-restoration test file**

Run:

```bash
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/p3_v3/test_pilot_source.py -q
```

Expected: all tests pass with no warnings or errors.

- [ ] **Step 6: Commit the identity update**

Run:

```bash
rtk git add src/p3_v3/pilot_source.py tests/p3_v3/test_pilot_source.py docs/superpowers/specs/2026-08-24-p3-boost-math-build-preflight-attempt-2-recovery-design-amendment-v3.md
rtk git diff --cached --check
rtk git commit -m "fix: update attempt2 archive identity"
```

Expected: one commit containing only the active archive identity, its tests, and the V3 supersession text.

---

### Task 2: Rebind formal implementation review to the amended contract and approved plan

**Files:**
- Modify: `tests/p3_v3/test_pilot_build.py:2830-2930`
- Modify: `src/p3_v3/pilot_build.py:175-186`

**Interfaces:**
- Consumes: the amended V3 design file and this implementation plan.
- Produces: `ATTEMPT2_AUTHORITY_HASHES` that verifies the current V3 amendment and `docs/superpowers/plans/2026-08-26-p3-boost-math-attempt2-archive-contract-update.md`.

- [ ] **Step 1: Add a failing authority-binding test**

Add this test next to the existing implementation-verdict tests in `tests/p3_v3/test_pilot_build.py`:

```python
def test_attempt2_archive_update_binds_current_design_and_plan():
    from p3_v3 import pilot_build

    expected_plan = Path(
        "docs/superpowers/plans/"
        "2026-08-26-p3-boost-math-attempt2-archive-contract-update.md"
    )
    assert pilot_build.ATTEMPT2_APPROVED_PLAN_PATH == expected_plan
    for field, (path, expected_sha256) in pilot_build.ATTEMPT2_AUTHORITY_HASHES.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected_sha256, field
```

- [ ] **Step 2: Run the new test and verify the expected red state**

Run:

```bash
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/p3_v3/test_pilot_build.py::test_attempt2_archive_update_binds_current_design_and_plan -q
```

Expected: FAIL because `ATTEMPT2_APPROVED_PLAN_PATH` still names the 2026-08-24 plan and the V3 hash still describes the pre-supersession file.

- [ ] **Step 3: Compute the two current document hashes**

Run:

```bash
rtk shasum -a 256 docs/superpowers/specs/2026-08-24-p3-boost-math-build-preflight-attempt-2-recovery-design-amendment-v3.md
rtk shasum -a 256 docs/superpowers/plans/2026-08-26-p3-boost-math-attempt2-archive-contract-update.md
```

Record the full 64-character digests from this exact worktree state.

- [ ] **Step 4: Update only the V3 and approved-plan bindings**

In `src/p3_v3/pilot_build.py`, keep the V1 and V2 paths and hashes unchanged. Set:

```python
ATTEMPT2_APPROVED_PLAN_PATH = Path(
    "docs/superpowers/plans/"
    "2026-08-26-p3-boost-math-attempt2-archive-contract-update.md"
)
```

Replace `ATTEMPT2_AUTHORITY_HASHES["v3_design_sha256"]` with the digest printed for the amended V3 file and replace `ATTEMPT2_AUTHORITY_HASHES["approved_implementation_plan_sha256"]` with the digest printed for this plan. Do not change the verdict schema or the V1/V2 bindings.

- [ ] **Step 5: Verify green for authority and verdict-reader tests**

Run:

```bash
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/p3_v3/test_pilot_build.py::test_attempt2_archive_update_binds_current_design_and_plan tests/p3_v3/test_pilot_build.py::test_attempt2_implementation_verdict_accepts_exact_pass tests/p3_v3/test_pilot_build.py::test_attempt2_implementation_verdict_rejects_missing_extra_and_wrong_values -q
```

Expected: all selected tests pass.

- [ ] **Step 6: Commit the formal authority rebinding**

Run:

```bash
rtk git add src/p3_v3/pilot_build.py tests/p3_v3/test_pilot_build.py
rtk git diff --cached --check
rtk git commit -m "fix: rebind attempt2 archive review authority"
```

Expected: the new HEAD is the recovery implementation commit reviewed by the replacement verdict.

---

### Task 3: Regenerate and independently validate the public-source projection

**Files:**
- Read: `/tmp/p3-boost-math-upstream.fUiwS5/.git`
- Create: `/tmp/p3-boost-math-upstream.fUiwS5/candidate-git-archive-excluded.tar`
- Create temporarily: `/tmp/p3_verify_attempt2_archive.py`
- Create: `/tmp/p3-boost-math-public-source-discovery/content-equivalence-r1/boost-math-dc86f3259c84f68ac7c4e2be11a1ed8567011240-projected.tar`

**Interfaces:**
- Consumes: official upstream clone and fixed witness commit.
- Produces: one regular mode-0644 TAR at the frozen production archive path.

- [ ] **Step 1: Reverify the upstream commit/tree relation**

Run:

```bash
rtk git -C /tmp/p3-boost-math-upstream.fUiwS5 rev-parse 04c2c248dfc5e35eeb7638152d5bd7c2985feef2^{tree}
rtk git -C /tmp/p3-boost-math-upstream.fUiwS5 rev-parse 03ea9c8d7dff1083facd134c8f641e006b68fdae^{tree}
```

Expected: both commands print `dc86f3259c84f68ac7c4e2be11a1ed8567011240`.

- [ ] **Step 2: Regenerate the candidate with the canonical command**

Run:

```bash
rtk git -C /tmp/p3-boost-math-upstream.fUiwS5 archive --format=tar --output=/tmp/p3-boost-math-upstream.fUiwS5/candidate-git-archive-excluded.tar 04c2c248dfc5e35eeb7638152d5bd7c2985feef2 -- . ':(exclude)build/Jamfile.v2'
```

Expected: exit code 0.

- [ ] **Step 3: Verify candidate bytes, TAR format, file metrics, exclusion, and normalized tree**

Create `/tmp/p3_verify_attempt2_archive.py` with `apply_patch` using this exact content:

```python
import shutil
import tempfile
from pathlib import Path

from p3_v3 import pilot_source

candidate = Path(
    "/tmp/p3-boost-math-upstream.fUiwS5/candidate-git-archive-excluded.tar"
)
snapshot = pilot_source.read_production_archive_bytes(candidate)
assert snapshot.sha256 == (
    "e97524b457326fdb4d0ccd8f6d83cb33cdad920a76dffc4b508f628a0a70393d"
)
assert snapshot.size == 99092480
assert snapshot.archive_format == "TAR"

verification_root = Path(tempfile.mkdtemp(prefix="p3-attempt2-archive-verify."))
staging = verification_root / "tree"
try:
    extracted = pilot_source.extract_archive_to_staging(snapshot, staging)
    assert extracted == staging
    assert not (staging / "build" / "Jamfile.v2").exists()
    tree = pilot_source.capture_materialized_tree(staging)
    assert pilot_source.canonical_source_tree_sha256(tree) == (
        "93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8"
    )
    assert pilot_source._tree_metrics(tree) == (4396, 95635487)
finally:
    shutil.rmtree(verification_root)
```

Run:

```bash
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python /tmp/p3_verify_attempt2_archive.py
```

Expected: exit code 0 and removal of only the verifier-created temporary directory.

- [ ] **Step 4: Require an absent frozen target and publish mode 0644**

Run a read-only existence check first. If the target exists, stop and report its current SHA/size without overwriting it. If absent, run:

```bash
rtk /bin/mkdir -p /tmp/p3-boost-math-public-source-discovery/content-equivalence-r1
rtk /usr/bin/install -m 0644 /tmp/p3-boost-math-upstream.fUiwS5/candidate-git-archive-excluded.tar /tmp/p3-boost-math-public-source-discovery/content-equivalence-r1/boost-math-dc86f3259c84f68ac7c4e2be11a1ed8567011240-projected.tar
```

- [ ] **Step 5: Reverify the published object independently**

Run:

```bash
rtk shasum -a 256 /tmp/p3-boost-math-public-source-discovery/content-equivalence-r1/boost-math-dc86f3259c84f68ac7c4e2be11a1ed8567011240-projected.tar
rtk /usr/bin/stat -f '%z %Lp %HT' /tmp/p3-boost-math-public-source-discovery/content-equivalence-r1/boost-math-dc86f3259c84f68ac7c4e2be11a1ed8567011240-projected.tar
```

Expected: SHA `e97524b457326fdb4d0ccd8f6d83cb33cdad920a76dffc4b508f628a0a70393d`, size `99092480`, mode `644`, regular file, not a symlink.

---

### Task 4: Generate and validate the replacement implementation verdict

**Files:**
- Modify untracked: `docs/review_20260824/boost_math_attempt_2_recovery_implementation_sol_high_review.md`
- Preserve untracked: `data/p3_v3/pilot/boost_math/user-auth-build-preflight-attempt-2.txt`

**Interfaces:**
- Consumes: final recovery implementation HEAD, current authority hashes, and SHA-256 of every `ATTEMPT2_REVIEWED_FILES` entry.
- Produces: one canonical JSON implementation verdict accepted by `read_attempt2_implementation_verdict()`.

- [ ] **Step 1: Capture the final reviewed commit and blob hashes**

Run:

```bash
rtk git rev-parse HEAD
rtk git status --porcelain=v1 --untracked-files=all
rtk shasum -a 256 src/p3_v3/pilot_source.py src/p3_v3/pilot_build.py scripts/p3_v3/pilot.py tests/p3_v3/test_pilot_source.py tests/p3_v3/test_pilot_build.py tests/p3_v3/test_pilot.py docs/superpowers/plans/2026-08-24-p3-boost-math-attempt-2-recovery-implementation.md
```

Expected: no tracked changes; exactly the canonical verdict and authorization are untracked.

- [ ] **Step 2: Replace the old verdict with canonical JSON for the current commit**

Use the existing verdict schema. Set:

```json
{
  "schema_version": "p3-pilot-attempt2-recovery-implementation-verdict-v1",
  "verdict": "PASS",
  "qualification_base_head": "0e51252f23dc3be4f82eb99e4f493c103f38c620",
  "formal_denominator_membership": false,
  "claims": "blocked",
  "attempt_2_authorized": false,
  "rq4_supported": false
}
```

Set `reviewed_commit` to the exact 40-character output of `rtk git rev-parse HEAD` from Step 1. Populate the four authority SHA fields from `ATTEMPT2_AUTHORITY_HASHES`, populate every reviewed blob with the Step 1 digest, keep the rejected-plan digest fixed, compute `artifact_sha256` with `canonical_sha256()` over the object without that field, serialize with `canonical_json_bytes()`, and write exactly one terminal LF using `apply_patch`.

- [ ] **Step 3: Validate the verdict and frozen archive through production readers**

Run:

```bash
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -c 'from p3_v3.pilot_build import read_attempt2_implementation_verdict; from p3_v3.pilot_source import ATTEMPT2_ARCHIVE_PATH, ATTEMPT2_SOURCE_ROOT, _inspect_attempt2_source_entry; print(read_attempt2_implementation_verdict()); print(_inspect_attempt2_source_entry(ATTEMPT2_ARCHIVE_PATH, ATTEMPT2_SOURCE_ROOT))'
```

Expected: verdict returns current HEAD and its file digest; source entry returns `INVALID_PASS_NO_ROOT` or `ALREADY_COMPLETE`. The command must not start Attempt-2.

---

### Task 5: Final verification and handoff

**Files:**
- Verify all tracked and untracked artifacts above.

**Interfaces:**
- Consumes: Tasks 1-4.
- Produces: evidence that the updated contract and archive are ready for a separate run-authorization decision.

- [ ] **Step 1: Run the full scoped test suite fresh**

Run:

```bash
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/p3_v3/test_pilot_source.py tests/p3_v3/test_pilot_build.py tests/p3_v3/test_pilot.py -q
```

Expected: all tests pass with no warnings or errors.

- [ ] **Step 2: Run syntax and Git hygiene checks**

Run:

```bash
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m py_compile src/p3_v3/pilot_source.py src/p3_v3/pilot_build.py scripts/p3_v3/pilot.py
rtk git diff --check
rtk git status --porcelain=v1 --untracked-files=all
```

Expected: syntax and diff checks exit 0; no tracked changes; exactly the verdict and authorization paths remain untracked.

- [ ] **Step 3: Report the transition state without running Attempt-2**

Report the design commit, plan commit, final recovery implementation commit, verdict SHA-256, archive SHA-256/size/mode, source-entry reconciliation state, and full test count. State explicitly that the previous Attempt-2 invocation remains consumed and that a separate explicit run decision is required before any further Attempt-2 or profiling command.
