# P3 v3 Minimum Evidence Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` (recommended) or
> `superpowers:executing-plans` to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the smallest tested P3 evidence channel that validates a pinned
P12 bridge, deterministically derives controlled subject frames, materializes
phase packages, records immutable attempts, and runs repeatable preflight without
starting a scientific experiment.

**Architecture:** Five focused Python modules expose small study-specific
interfaces; one thin CLI delegates to them and contains no duplicated scientific
rules. All filesystem authorities are canonical JSON or JSONL. Synthetic Git
fixtures exercise the full Phase 0→Phase 2 path; real Defect4MR data, Package C,
network access, mutant construction, and MR execution remain out of scope.

**Tech Stack:** Python 3.11 standard library, pytest 9, Git subprocesses with
`shell=False`, SHA-256, canonical JSON, POSIX atomic file operations.

## Global Constraints

- Parent scientific-plan revision commit:
  `07287122123b113610b6b8bcde7116ab397da688`.
- Scientific plan SHA-256:
  `911562938a14ad3955a6c1e38080185ba78e92dbf4401efcb10d7c169e4a2772`.
- Evidence-foundation design SHA-256:
  `e2a943b30f8096aa65a72c43aa514df67b8d58e16fcf7209930799ee4444c346`.
- `PINNED_GIT_RELEASE` is the only bridge trust mode.
- Historical P12 v1.1.2 bytes remain immutable; tests use synthetic successor
  releases only.
- No production network call, Cursor launch, P12 reveal, Package C material,
  semantic mutant, MR execution, manuscript change, PR, or merge.
- Local commands use `rtk`; generated Cursor VM commands do not use `rtk`.
- Preflight may be diagnosed and rerun and never creates a scientific job ID.
- Scientific authorization begins only when a later phase durably creates its
  first scientific job intent.
- Every production behavior is introduced RED→GREEN; the focused test suite runs
  after each task and the complete repository suite runs at final verification.

---

### Task 1: Canonical artifact primitives

**Files:**
- Create: `src/p3_v3/__init__.py`
- Create: `src/p3_v3/artifacts.py`
- Create: `tests/p3_v3/__init__.py`
- Create: `tests/p3_v3/test_artifacts.py`

**Interfaces:**
- Produces: `EvidenceError(code, detail)`, `canonical_json_bytes(value)`,
  `canonical_sha256(value)`, `file_sha256(path)`, `validate_exact_object(...)`,
  `safe_relative_path(value)`, `write_canonical_json(path, value, exclusive)`,
  and `read_canonical_json(path)`.
- Invariants: UTF-8, sorted keys, compact separators, no NaN/infinity, exactly
  one terminal LF in files, lowercase 64-hex digests, safe relative POSIX paths,
  same-directory atomic replace, file and parent-directory fsync.

- [ ] **Step 1: Write focused failing tests**

```python
def test_canonical_file_has_one_terminal_lf(tmp_path):
    path = tmp_path / "artifact.json"
    write_canonical_json(path, {"b": 2, "a": 1}, exclusive=True)
    assert path.read_bytes() == b'{"a":1,"b":2}\n'

def test_exclusive_write_preserves_existing_bytes(tmp_path):
    path = tmp_path / "artifact.json"
    path.write_bytes(b"original\n")
    with pytest.raises(EvidenceError, match="E_EXISTS"):
        write_canonical_json(path, {"a": 1}, exclusive=True)
    assert path.read_bytes() == b"original\n"
```

- [ ] **Step 2: Run RED**

Run: `rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/p3_v3/test_artifacts.py -q`

Expected: collection fails because `p3_v3.artifacts` does not exist.

- [ ] **Step 3: Implement the minimal deep artifact module**

```python
class EvidenceError(ValueError):
    def __init__(self, code: str, detail: str):
        super().__init__(f"{code}: {detail}")
        self.code = code

def canonical_json_bytes(value: Any) -> bytes:
    try:
        text = json.dumps(value, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise EvidenceError("E_CANONICAL_JSON", str(exc)) from exc
    return text.encode("utf-8") + b"\n"
```

Implement atomic/exclusive writes with temporary files in the destination
directory, `os.replace`, file fsync, and directory fsync. Reject absolute paths,
empty segments, `.`/`..`, backslashes, NUL, and noncanonical JSON bytes.

- [ ] **Step 4: Run GREEN and mutation cases**

Run: `rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/p3_v3/test_artifacts.py -q`

Expected: all artifact tests pass, including one-byte drift, unsafe path,
noncanonical JSON, NaN, duplicate write, and malformed digest cases.

- [ ] **Step 5: Commit**

```bash
rtk git add src/p3_v3 tests/p3_v3
rtk git commit -m "feat(p3-v3): add canonical evidence artifacts"
```

### Task 2: Pinned P12 bridge and deterministic subject frames

**Files:**
- Create: `src/p3_v3/bridge_and_frames.py`
- Create: `tests/p3_v3/test_bridge_and_frames.py`

**Interfaces:**
- Consumes: artifact primitives from Task 1.
- Produces: `verify_pinned_bridge(repo_root, consumer_lock) -> dict`,
  `build_subject_frames(verified_bridge, feature_records, construct_limit=18)
  -> dict`, and `verify_reveal(bridge_record, reveal_record, package_root) -> None`.
- `verify_pinned_bridge` reads the externally pinned release commit, bridge blob,
  and contract blob
  directly from Git using exact `git -C ...` argv with `shell=False`.
- `build_subject_frames` derives `controlled_subject_id`, deterministic site IDs,
  total-order `C_CONSTRUCT`, and exhaustive unique-subject `C_CRITERION`.

- [ ] **Step 1: Create a synthetic pinned Git release and failing tests**

```python
def test_bridge_requires_pinned_git_blobs(synthetic_p12_repo):
    verified = verify_pinned_bridge(synthetic_p12_repo.root, synthetic_p12_repo.consumer_lock)
    assert verified["trust_mode"] == "PINNED_GIT_RELEASE"

def test_visible_bridge_rejects_tree_oid(synthetic_p12_repo):
    synthetic_p12_repo.mutate_record({"fixed_git_tree_oid": "a" * 40})
    with pytest.raises(EvidenceError, match="E_BRIDGE_VISIBLE_SECRET"):
        verify_pinned_bridge(synthetic_p12_repo.root, synthetic_p12_repo.consumer_lock)
```

Add literal expected IDs for shuffled-input invariance, alias reuse, conflict
rejection, first-applicable site selection, total-order tie handling, exhaustive
criterion inclusion, and nonce/OID/source-tree reveal mutations.

- [ ] **Step 2: Run RED**

Run: `rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/p3_v3/test_bridge_and_frames.py -q`

Expected: collection fails because `p3_v3.bridge_and_frames` does not exist.

- [ ] **Step 3: Implement bridge verification and frame derivation**

```python
def controlled_subject_id(record: Mapping[str, Any]) -> str:
    return canonical_sha256({
        "normalized_source_tree_sha256": record["normalized_source_tree_sha256"],
        "build_descriptor_sha256": record["build_descriptor_sha256"],
        "public_workload_set_sha256": record["public_workload_set_sha256"],
        "domain": "P3-SUBJECT-v1",
    })
```

Validate exact schemas before projection. Derive neutral snapshot IDs rather than
trusting custodian labels. Use `(selection_key, controlled_subject_id)` as the
only rank order. Reject conflicting aliases rather than choosing one. The reveal
verifier recomputes the domain-separated commitment and normalized source hash.

- [ ] **Step 4: Run GREEN**

Run: `rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/p3_v3/test_bridge_and_frames.py -q`

Expected: all bridge/frame tests pass without network access.

- [ ] **Step 5: Commit**

```bash
rtk git add src/p3_v3/bridge_and_frames.py tests/p3_v3/test_bridge_and_frames.py
rtk git commit -m "feat(p3-v3): verify P12 bridge and build frames"
```

### Task 3: Content-addressed phase packages

**Files:**
- Create: `src/p3_v3/packages.py`
- Create: `tests/p3_v3/test_packages.py`

**Interfaces:**
- Consumes: canonical files and safe paths from Task 1.
- Produces: `build_package(role, source_root, file_specs, parents) -> dict`,
  `verify_package(source_root, manifest) -> None`, and
  `materialize_package(source_root, target_root, manifest) -> None`.
- Roles are exactly `CONSTRUCTION_A`, `CONTROLLED_B`, and `REAL_HOLDOUT_C`.

- [ ] **Step 1: Write failing behavioral tests**

```python
def test_package_rejects_symlink(tmp_path):
    (tmp_path / "real").write_text("x")
    (tmp_path / "link").symlink_to("real")
    with pytest.raises(EvidenceError, match="E_PACKAGE_FILE_TYPE"):
        build_package("CONSTRUCTION_A", tmp_path, [{"path": "link", "class": "SOURCE"}], [])
```

Cover traversal, duplicates after normalization, undeclared files, mode/size/hash
drift, role-forbidden content, clean materialization, parent-hash ordering, and
Package C early presence.

- [ ] **Step 2: Run RED**

Run: `rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/p3_v3/test_packages.py -q`

Expected: collection fails because `p3_v3.packages` does not exist.

- [ ] **Step 3: Implement package build/verify/materialize**

```python
ALLOWED_CLASSES = {
    "CONSTRUCTION_A": {"SOURCE", "BUILD", "PUBLIC_DOC", "CONTRACT", "PROPOSAL_INPUT"},
    "CONTROLLED_B": {"SOURCE", "SEMANTIC_MUTANT", "SYNTACTIC_MUTANT", "MR", "JOB_INPUT"},
    "REAL_HOLDOUT_C": {"P12_IDENTITY", "P12_BUGGY", "P12_REVEAL", "REAL_JOB_INPUT"},
}
```

Hash sorted records into a package tree. Verification rereads every regular file
and rejects extras in a materialized target. Materialization uses exclusive files
in a newly created target and never extracts archives or follows links.

- [ ] **Step 4: Run GREEN**

Run: `rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/p3_v3/test_packages.py -q`

- [ ] **Step 5: Commit**

```bash
rtk git add src/p3_v3/packages.py tests/p3_v3/test_packages.py
rtk git commit -m "feat(p3-v3): add phase package manifests"
```

### Task 4: Immutable attempts, ledger, and phase close

**Files:**
- Create: `src/p3_v3/run_records.py`
- Create: `tests/p3_v3/test_run_records.py`

**Interfaces:**
- Produces: `create_intent(job_dir, intent)`, `write_result(job_dir, result)`,
  `reduce_attempts(job_root, ledger_path) -> list[dict]`, and
  `close_phase(phase_id, protocol_sha, expected_jobs, ledger_path, output_manifest)
  -> dict`.
- Workers write only job-local canonical files. One reducer rewrites no attempt;
  it creates the ledger exclusively in frozen job/attempt order.

- [ ] **Step 1: Write failing state-machine tests**

```python
def test_result_requires_existing_intent(tmp_path):
    with pytest.raises(EvidenceError, match="E_RESULT_WITHOUT_INTENT"):
        write_result(tmp_path / "job-1", {"status": "PASS"})

def test_phase_close_detects_pending_job(tmp_path):
    create_intent(tmp_path / "jobs/job-1", literal_intent("job-1"))
    with pytest.raises(EvidenceError, match="E_PHASE_PENDING"):
        close_phase("PHASE-2", "a" * 64, ["job-1"], tmp_path / "ledger.jsonl", "b" * 64)
```

Cover duplicate intents/results, invalid terminal states, sequence/event hash
mutation, suffix truncation, missing/extra jobs, retries retaining earlier
failures, and phase-close raw-ledger hash mismatch.

- [ ] **Step 2: Run RED**

Run: `rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/p3_v3/test_run_records.py -q`

- [ ] **Step 3: Implement the attempt state machine**

```python
TERMINAL_STATES = {
    "PASS", "FAIL_SCIENTIFIC", "FAIL_INFRASTRUCTURE",
    "INCONCLUSIVE", "MISSING_WITH_REASON",
}
```

Intent creation is exclusive and durable. Result creation requires one canonical
intent and is exclusive. Reduction derives contiguous sequence numbers,
`previous_event_sha256`, and `event_sha256`. Phase close binds the expected job
inventory, terminal count, event count/head, raw ledger SHA, and output manifest.

- [ ] **Step 4: Run GREEN**

Run: `rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/p3_v3/test_run_records.py -q`

- [ ] **Step 5: Commit**

```bash
rtk git add src/p3_v3/run_records.py tests/p3_v3/test_run_records.py
rtk git commit -m "feat(p3-v3): record immutable phase attempts"
```

### Task 5: Repeatable preflight and thin CLI

**Files:**
- Create: `src/p3_v3/preflight.py`
- Create: `scripts/p3_v3/evidence.py`
- Create: `tests/p3_v3/test_preflight.py`
- Create: `tests/p3_v3/test_cli.py`

**Interfaces:**
- Produces: `run_preflight(repo_root, specification, executor=subprocess.run)
  -> dict` and CLI commands `validate-protocol`, `verify-bridge`, `build-frames`,
  `verify-mr-inventory`, `build-package`, `verify-package`, `run-preflight`,
  `verify-run-records`, `close-phase`, and `verify-evidence`.
- Preflight commands are explicit argv arrays, `shell=False`, bounded by timeout,
  and captured as hashes. No preflight function can call `create_intent`.

- [ ] **Step 1: Write failing preflight and CLI tests**

```python
def test_preflight_failure_is_repeatable_and_not_scientific(tmp_path, git_repo):
    spec = literal_preflight(smoke=[["python3", "-c", "raise SystemExit(7)"]])
    first = run_preflight(git_repo, spec)
    second = run_preflight(git_repo, spec)
    assert first["status"] == second["status"] == "FAIL"
    assert not list(tmp_path.glob("**/intent.json"))
```

Run the real CLI in subprocess tests. Assert stable JSON output and nonzero exit
for repository, commit, dependency, input, timeout, and smoke failures. Assert
that CLI help lists only the ten frozen commands.

- [ ] **Step 2: Run RED**

Run: `rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/p3_v3/test_preflight.py tests/p3_v3/test_cli.py -q`

- [ ] **Step 3: Implement preflight and CLI dispatch**

```python
def execute(argv: Sequence[str], cwd: Path, timeout: float) -> CompletedProcess[bytes]:
    return subprocess.run(list(argv), cwd=cwd, capture_output=True,
                          shell=False, timeout=timeout, check=False)
```

Normalize GitHub HTTPS/SSH spellings to `owner/repository`, but record raw origin
without using its spelling as an equality gate. Verify exact HEAD, clean declared
inputs, dependency-lock hash, platform facts, resources, package role, and smoke
commands. The CLI prints one canonical JSON result and contains no rule constants
already owned by a module.

- [ ] **Step 4: Run GREEN and focused suite**

Run: `rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/p3_v3 -q`

- [ ] **Step 5: Commit**

```bash
rtk git add src/p3_v3/preflight.py scripts/p3_v3/evidence.py tests/p3_v3
rtk git commit -m "feat(p3-v3): add repeatable preflight CLI"
```

### Task 6: Synthetic phase path, review, and Cursor VM thin instructions

**Files:**
- Create: `tests/p3_v3/test_synthetic_phase_path.py`
- Create: `docs/superpowers/plans/2026-08-08-p3-v3-phase0-phase2-cursor-vm.md`

**Interfaces:**
- The integration test uses the public CLI only and proves synthetic protocol →
  bridge → frames → Package A → repeatable preflight receipt. Scientific intent
  and phase-close invariants remain focused state-machine tests: Phase 2 is
  explicitly non-scientific, and the frozen public CLI has no command that may
  create a scientific job intent.
- The Cursor document contains separate Phase 0 and Phase 2 invocations, no
  inline controller, no live P12 path, and no scientific authorization sentence.

- [ ] **Step 1: Write the failing public-CLI integration test**

```python
def test_synthetic_phase0_to_phase2_path(cli, synthetic_release, tmp_path):
    protocol = cli("validate-protocol", synthetic_release.protocol)
    bridge = cli("verify-bridge", synthetic_release.bridge)
    frames = cli("build-frames", bridge.output, synthetic_release.features)
    package = cli("build-package", "CONSTRUCTION_A", frames.output)
    preflight = cli("run-preflight", package.output)
    assert [protocol.code, bridge.code, frames.code, package.code, preflight.code] == [0] * 5
```

- [ ] **Step 2: Run RED and implement only missing CLI composition**

Run: `rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/p3_v3/test_synthetic_phase_path.py -q`

Expected: fail at the first unimplemented composition or receipt assertion.

- [ ] **Step 3: Run focused and repository suites**

```bash
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest tests/p3_v3 -q
rtk env PYTHONPATH=src /Users/limeng/Papers/P3-SemanticMutation/.venv/bin/python -m pytest -q --maxfail=1
rtk ruff check src/p3_v3 scripts/p3_v3 tests/p3_v3
rtk git diff --check
```

- [ ] **Step 4: Perform two inline review passes**

Review A checks the implementation against every frozen requirement in the
scientific plan and foundation design. Review B checks module depth, duplicate
rules, unsafe filesystem/Git behavior, failure retention, and whether any CLI or
Cursor prose can start a live experiment. Record findings in the implementation
commit message or fix them with a new RED→GREEN cycle. This is an inline review,
not an independent-review claim.

- [ ] **Step 5: Write the thin Cursor VM document**

The document fixes: fresh VM/conversation, Grok 4.5 High, exact implementation
commit, `python3 scripts/p3_v3/evidence.py ...` commands without `rtk`, repeatable
preflight attempts, synthetic fixtures only, stop after Phase 2 receipt, and
explicit prohibitions on network evidence collection, Package C, P12 reveal,
semantic-mutant proposal, MR execution, manuscript work, push, PR, and merge.

- [ ] **Step 6: Commit**

```bash
rtk git add tests/p3_v3/test_synthetic_phase_path.py docs/superpowers/plans/2026-08-08-p3-v3-phase0-phase2-cursor-vm.md
rtk git commit -m "docs(p3-v3): add audited phase0 phase2 VM path"
```

## Inline Review Record

This is a disclosed inline self-review, not an independent audit.

The specification pass found and repaired: exact authority-hash binding,
canonical scale/technique cell iteration, strict round-robin continuation,
explicit empty cells, first-applicable-site selection, preflight receipt
self-hashing, literal `.git` suffix normalization, canonical JSONL verification,
ledger digest/type checks, and contiguous infrastructure-only retry rules. It
also corrected the Task 6 boundary: non-scientific Phase 2 ends at a repeatable
preflight receipt and does not manufacture a scientific intent.

The engineering pass confirms that this slice performs no network fetch, live
P12 reveal, semantic proposal, MR execution, or manuscript mutation; Git and
smoke subprocesses use explicit argv with `shell=False`; preflight creates no
scientific intent; and package/artifact writes are exclusive or atomic.

The following remain explicit blockers before any real P12 or controlled-study
phase can start:

1. the source-derived public-workload, scale, technique, and applicability rule
   engine is not yet implemented, so real feature records are not authoritative;
2. `verify-mr-inventory` currently verifies only the frozen chronology envelope,
   not semantic-signature exclusion or the custodian receipt contents;
3. study-specific claim-evidence and RQ4 `P12_PAIRED` validators are absent; and
4. the synthetic Phase 0→7 commitment-opening path is absent.

Accordingly, completion of this implementation plan supports only synthetic
Phase 0/2 foundation verification and preparation of a non-authorizing VM
instruction. It does not satisfy the design's later-phase acceptance criteria.

## Completion boundary

Completion proves only that the minimum evidence foundation and synthetic Phase
0/2 path are implemented and reproducible. It does not authorize or claim:

- a compatible successor Defect4MR release exists;
- any real P12 item is paired or revealed;
- any semantic mutant or MR portfolio exists;
- any Cursor VM has run;
- any RQ1–RQ4 result is supported.

Those remain blocked until the user separately authorizes the relevant phase and
its frozen inputs satisfy the preceding phase-close receipt.
