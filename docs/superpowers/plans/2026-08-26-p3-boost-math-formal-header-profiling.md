# P3 Boost.Math Formal Header Profiling Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the smallest production runner and CLI that execute the 20 frozen
Boost.Math header-compilation behaviors and emit an existing-schema formal
profiling receipt without inventing subject-level call traces.

**Architecture:** `src/p3_v3/profiling_runner.py` owns translation-unit
generation, C++ process control, depfile containment, raw evidence, and receipt
construction. `src/p3_v3/bridge_and_frames.py` makes one narrow compatibility
change: choose the expected runner source SHA from the single `runner_version`
in the receipt, preserving all 35 historical receipts. A thin
`scripts/p3_v3/profile.py` exposes one command and adds no scientific behavior.

**Tech Stack:** Python 3.11, standard-library `argparse`, `subprocess`, `pathlib`,
and `hashlib`; existing `p3_v3.artifacts` canonical JSON primitives; pytest;
Clang-compatible `/usr/bin/c++` with C++14 depfiles.

## Global Constraints

- Governing design:
  `docs/superpowers/specs/2026-08-26-p3-boost-math-formal-header-profiling-design.md`
  at SHA-256
  `0903d8fc00f8fe0a66466eca3f9b16b9a3a3aeab21076e673599cb7a90ea2998`.
- Implementation base is commit
  `533d18bf3838530ea637d7c3a3b249978b43ee72` on
  `codex/p3-boost-math-formal-profiling`.
- The only new production files are `src/p3_v3/profiling_runner.py` and
  `scripts/p3_v3/profile.py`.
- In `src/p3_v3/bridge_and_frames.py`, change only the existing profiling
  runner-source binding and the Phase-1 unresolved receipt's corresponding
  historical value.
- Test changes stay in `tests/p3_v3/test_bridge_and_frames.py` and
  `tests/p3_v3/test_cli.py`.
- Do not add a schema, authority file, qualification, authorization, verdict,
  baseline, gate, dependency, package, or unrelated refactor.
- Do not modify the frozen workload, tracked placeholder receipt, derived
  subject, technique profile, or any RQ claim.
- Do not run qualification, Attempt-2, formal profiling, or the full test suite
  during this implementation slice.
- Cursor Cloud commands use native commands without `rtk`; local commands obey
  the repository's `rtk` wrapper rule.
- Formal profiling execution remains separately authorized and is not a step in
  this plan.

### Frozen Boost.Math identities

```text
neutral_snapshot_id = 74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886
controlled_subject_source_id = e5f21a7d067d641d0a20bfc57c61e630d6f7588ef30235cea49c9a9cf950c7a7
normalized_source_tree_sha256 = 93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8
build_descriptor_sha256 = 68d2e0fd34b845bb0df22b29003f26259d5655d2ec80c18895ff36904db2d95d
profiling_workload_sha256 = 982375e1fedb6ff26aa25e39cb1d65e45ff14474d4d34fca634c95ef352b036e
adapter_implementation_source_sha256 = 18a7f223ef2482cd8a4a099f531ca17d4f961a8047b8d682a2e644d66aea2208
historical_runner_source_sha256 = 978fa53c66ae15f9c51b5fa73dc03afdb2d23448f7714d752bccf92c09503ad0
```

---

### Task 1: Header mapping and depfile containment

**Files:**
- Create: `src/p3_v3/profiling_runner.py`
- Modify: `tests/p3_v3/test_bridge_and_frames.py`

**Interfaces:**
- Consumes: one frozen workload row with `category`, `entrypoint`, and
  `behavior_id`; one controlled source root.
- Produces:
  - `RUNNER_VERSION = "p3-cxx-header-compile-profiler-v1"`
  - `COMPILE_TIMEOUT_SECONDS = 120`
  - `header_include(entrypoint: str) -> str`
  - `translation_unit_bytes(entrypoint: str) -> bytes`
  - `compile_argv(compiler: Path, include_root: Path, source: Path,
    object_path: Path, depfile: Path) -> list[str]`
  - `validate_depfile_containment(depfile_bytes: bytes, include_root: Path,
    requested_header: str) -> None`

- [ ] **Step 1: Write failing header-mapping and command tests**

Add imports for `p3_v3.profiling_runner` to
`tests/p3_v3/test_bridge_and_frames.py`, then add these focused tests:

```python
def test_cxx_profile_maps_frozen_entrypoint_to_attempt2_include_boundary(tmp_path):
    from p3_v3 import profiling_runner

    source = tmp_path / "source"
    include = source / "include"
    cpp = tmp_path / "probe.cpp"
    obj = tmp_path / "probe.o"
    dep = tmp_path / "probe.d"
    entrypoint = "include/boost/math/statistics/runs_test.hpp"

    assert profiling_runner.header_include(entrypoint) == (
        "boost/math/statistics/runs_test.hpp"
    )
    assert profiling_runner.translation_unit_bytes(entrypoint) == (
        b"#include <boost/math/statistics/runs_test.hpp>\n"
        b"int main() { return 0; }\n"
    )
    assert profiling_runner.compile_argv(
        Path("/usr/bin/c++"), include, cpp, obj, dep
    ) == [
        "/usr/bin/c++",
        "-std=c++14",
        "-DBOOST_MATH_STANDALONE=1",
        "-I",
        include.as_posix(),
        "-MD",
        "-MF",
        dep.as_posix(),
        "-MT",
        obj.as_posix(),
        "-c",
        cpp.as_posix(),
        "-o",
        obj.as_posix(),
    ]


@pytest.mark.parametrize(
    "entrypoint",
    [
        "boost/math/statistics/runs_test.hpp",
        "include/not-boost/header.hpp",
        "include/boost/../escape.hpp",
        "/include/boost/math/header.hpp",
    ],
)
def test_cxx_profile_rejects_noncanonical_header_entrypoint(entrypoint):
    from p3_v3 import profiling_runner

    with pytest.raises(EvidenceError, match="E_PROFILE_HEADER_ENTRYPOINT"):
        profiling_runner.header_include(entrypoint)
```

- [ ] **Step 2: Run the mapping tests and verify RED**

Run:

```bash
PYTHONPATH=src .venv/bin/python -m pytest \
  tests/p3_v3/test_bridge_and_frames.py \
  -k 'cxx_profile_maps_frozen_entrypoint or cxx_profile_rejects_noncanonical' -q
```

Expected: collection fails with `ImportError` because
`p3_v3.profiling_runner` does not exist.

- [ ] **Step 3: Implement the exact header mapping and compile command**

Create `src/p3_v3/profiling_runner.py` with the imports, constants, and helpers
needed by the tests. Use `PurePosixPath` and reject absolute paths, dot segments,
backslashes, empty components, and anything outside `include/boost/`.

The essential implementation is:

```python
RUNNER_VERSION = "p3-cxx-header-compile-profiler-v1"
COMPILE_TIMEOUT_SECONDS = 120


def header_include(entrypoint: str) -> str:
    if type(entrypoint) is not str or "\\" in entrypoint:
        raise EvidenceError("E_PROFILE_HEADER_ENTRYPOINT", "entrypoint is invalid")
    path = PurePosixPath(entrypoint)
    parts = entrypoint.split("/")
    if (
        path.is_absolute()
        or path.as_posix() != entrypoint
        or any(part in {"", ".", ".."} for part in parts)
        or parts[:2] != ["include", "boost"]
    ):
        raise EvidenceError("E_PROFILE_HEADER_ENTRYPOINT", "entrypoint escaped include/boost")
    return PurePosixPath(*parts[1:]).as_posix()


def translation_unit_bytes(entrypoint: str) -> bytes:
    include = header_include(entrypoint)
    return f"#include <{include}>\nint main() {{ return 0; }}\n".encode("utf-8")


def compile_argv(
    compiler: Path,
    include_root: Path,
    source: Path,
    object_path: Path,
    depfile: Path,
) -> list[str]:
    return [
        compiler.as_posix(), "-std=c++14", "-DBOOST_MATH_STANDALONE=1",
        "-I", include_root.as_posix(), "-MD", "-MF", depfile.as_posix(),
        "-MT", object_path.as_posix(), "-c", source.as_posix(),
        "-o", object_path.as_posix(),
    ]
```

- [ ] **Step 4: Write failing depfile-containment tests**

Add:

```python
def test_cxx_profile_depfile_accepts_only_controlled_boost_headers(tmp_path):
    from p3_v3 import profiling_runner

    include = tmp_path / "source" / "include"
    requested = "boost/math/statistics/runs_test.hpp"
    depfile = (
        f"probe.o: probe.cpp {include / requested} \\\n"
        f" {include / 'boost/math/tools/config.hpp'} /usr/include/c++/v1/vector\n"
    ).encode("utf-8")

    profiling_runner.validate_depfile_containment(depfile, include, requested)


def test_cxx_profile_depfile_rejects_system_boost_fallback(tmp_path):
    from p3_v3 import profiling_runner

    include = tmp_path / "source" / "include"
    depfile = (
        f"probe.o: probe.cpp {include / 'boost/math/statistics/runs_test.hpp'} "
        "/usr/include/boost/math/tools/config.hpp\n"
    ).encode("utf-8")

    with pytest.raises(EvidenceError, match="SYSTEM_BOOST_FALLBACK"):
        profiling_runner.validate_depfile_containment(
            depfile, include, "boost/math/statistics/runs_test.hpp"
        )


def test_cxx_profile_depfile_requires_requested_controlled_header(tmp_path):
    from p3_v3 import profiling_runner

    include = tmp_path / "source" / "include"
    depfile = b"probe.o: probe.cpp /usr/include/c++/v1/vector\n"

    with pytest.raises(EvidenceError, match="E_PROFILE_DEPFILE"):
        profiling_runner.validate_depfile_containment(
            depfile, include, "boost/math/statistics/runs_test.hpp"
        )
```

- [ ] **Step 5: Run the depfile tests and verify RED**

Run the same focused command with
`-k 'cxx_profile_depfile or cxx_profile_maps or cxx_profile_rejects'`.

Expected: mapping tests pass; depfile tests fail because
`validate_depfile_containment` is absent.

- [ ] **Step 6: Implement minimal depfile parsing and containment**

Normalize backslash-newline continuations, split the dependency side after the
first unescaped colon, and resolve each token without requiring the file to
exist. Use `Path.is_relative_to()` against `include_root.resolve()`. Inspect
every dependency whose path parts contain `boost`; raise:

```python
EvidenceError(
    "E_PROFILE_DEPFILE",
    "SYSTEM_BOOST_FALLBACK",
)
```

when any such dependency escapes the frozen include prefix. Raise
`E_PROFILE_DEPFILE` if the requested controlled header is absent. Do not use
`-MMD`: the command deliberately uses `-MD` so system Boost dependencies remain
visible.

- [ ] **Step 7: Run Task 1 tests and commit**

Run:

```bash
PYTHONPATH=src .venv/bin/python -m pytest \
  tests/p3_v3/test_bridge_and_frames.py \
  -k 'cxx_profile_maps or cxx_profile_rejects or cxx_profile_depfile' -q
git diff --check
```

Expected: all selected tests pass and `git diff --check` exits 0.

Commit:

```bash
git add src/p3_v3/profiling_runner.py tests/p3_v3/test_bridge_and_frames.py
git commit -m "feat: define cxx header profiling boundary"
```

---

### Task 2: Process execution and formal receipt construction

**Files:**
- Modify: `src/p3_v3/profiling_runner.py`
- Modify: `tests/p3_v3/test_bridge_and_frames.py`

**Interfaces:**
- Consumes: Task 1 helpers, a validated fixed workload object, source root,
  compiler, runtime root, and exclusive receipt path.
- Produces:
  - `run_compile_probe(argv: list[str], *, env: dict[str, str], timeout_seconds:
    int, popen: Callable) -> CompileProbe`
  - `run_cxx_header_workload(workload: Mapping[str, Any], *, source_root: Path,
    compiler: Path, runtime_root: Path, receipt_path: Path,
    popen: Callable = subprocess.Popen) -> dict[str, Any]`

- [ ] **Step 1: Add fake-process fixtures and failing row-semantics tests**

Define a small fake `Popen` in the test file whose queued outcomes are exit 0,
nonzero, timeout, or start error. Add a 20-row workload fixture with canonical
entrypoints such as `include/boost/math/statistics/runs_test.hpp`; queue the two
outcomes under assertion first and exit-0 outcomes for the remaining rows.
Assert:

```python
assert [row["behavior_id"] for row in receipt["results"]] == sorted(
    workload["selected_behavior_ids"]
)
assert receipt["results"][0]["status"] == "MISSING_TRACE"
assert receipt["results"][0]["failure_code"] == "NO_SUBJECT_CALL_TRACE"
assert receipt["results"][0]["exit_code"] == 0
assert receipt["results"][0]["call_trace"] == []
assert receipt["results"][0]["observed_site_ids"] == []
assert receipt["results"][1]["status"] == "FAILURE"
assert receipt["results"][1]["failure_code"] == "COMPILE_NONZERO_EXIT"
```

The fake successful process must write the expected object and depfile under the
row directory so the test exercises containment rather than bypassing it.

- [ ] **Step 2: Run row-semantics tests and verify RED**

Run:

```bash
PYTHONPATH=src .venv/bin/python -m pytest \
  tests/p3_v3/test_bridge_and_frames.py \
  -k 'cxx_profile_receipt_rows' -q
```

Expected: FAIL because `run_cxx_header_workload` is absent.

- [ ] **Step 3: Implement safe process execution**

Add a frozen `CompileProbe` dataclass carrying `exit_code`, `stdout`, `stderr`,
and `timed_out`. `run_compile_probe` must call `popen` with `shell=False`,
`stdout=PIPE`, `stderr=PIPE`, `start_new_session=True`, and the explicit
environment. On timeout, kill only the spawned process group, call
`communicate()` again to reap, and return a null exit. A start failure becomes a
row-level `COMPILER_START_ERROR`; a process-control or cleanup failure raises
`EvidenceError("E_PROFILE_PROCESS", "process control failed")` and prevents
receipt publication.

- [ ] **Step 4: Implement one-to-one row execution**

`run_cxx_header_workload` must:

1. require the fixed workload artifact SHA and exactly 20 selected rows;
2. require the fixed source root's real `include` directory and a real,
   non-symlink compiler;
3. require absent, non-symlink runtime and receipt paths;
4. create each row directory by `behavior_id`;
5. exclusively write `probe.cpp`, `stdout`, and `stderr`;
6. invoke the exact Task 1 command;
7. classify nonzero and timeout rows immediately;
8. after exit 0, parse the depfile before assigning `MISSING_TRACE`;
9. convert `SYSTEM_BOOST_FALLBACK` into a `FAILURE` row rather than aborting the
   remaining workload; and
10. sort and cover all 20 rows before constructing the receipt.

Use these fixed receipt parent values from Global Constraints. Compute
`runner_implementation_source_sha256` with
`file_sha256(Path(__file__))`. Compute each raw-byte SHA with `hashlib.sha256`,
`call_trace_sha256` with `canonical_sha256([])`, the body self-hash with
`canonical_sha256(body)`, and publish via
`write_canonical_json(receipt_path, receipt, exclusive=True)`.

- [ ] **Step 5: Add timeout, continuation, containment, and exclusivity tests**

Add four focused tests that assert:

```python
assert timeout_row["status"] == "TIMEOUT"
assert timeout_row["failure_code"] == "COMPILE_TIMEOUT"
assert timeout_row["timed_out"] is True
assert timeout_row["exit_code"] is None

assert len(receipt["results"]) == len(workload["selected_rows"])

assert escaped_row["status"] == "FAILURE"
assert escaped_row["failure_code"] == "SYSTEM_BOOST_FALLBACK"

with pytest.raises(EvidenceError, match="E_PROFILE_OUTPUT"):
    run_cxx_header_workload(
        workload,
        source_root=source_root,
        compiler=compiler,
        runtime_root=runtime_root,
        receipt_path=preexisting,
        popen=fake_popen,
    )
assert preexisting.read_bytes() == b"do-not-overwrite\n"
```

The containment regression is mandatory: an exit-0 compile whose depfile names
`/usr/include/boost/math/tools/config.hpp` must not become `MISSING_TRACE`.

- [ ] **Step 6: Run Task 2 tests and commit**

Run:

```bash
PYTHONPATH=src .venv/bin/python -m pytest \
  tests/p3_v3/test_bridge_and_frames.py \
  -k 'cxx_profile_' -q
git diff --check
```

Expected: all `cxx_profile_` tests pass.

Commit:

```bash
git add src/p3_v3/profiling_runner.py tests/p3_v3/test_bridge_and_frames.py
git commit -m "feat: execute cxx header profiling workload"
```

---

### Task 3: Version-specific runner-source validation

**Files:**
- Modify: `src/p3_v3/bridge_and_frames.py` at
  `build_phase1_unresolved_profiling_receipt` and
  `_validated_profiling_rows`
- Modify: `tests/p3_v3/test_bridge_and_frames.py`

**Interfaces:**
- Consumes: historical Phase-1 receipts and Task 2 formal receipts.
- Produces:
  - `PHASE1_UNEXECUTED_RUNNER_SHA256 =
    "978fa53c66ae15f9c51b5fa73dc03afdb2d23448f7714d752bccf92c09503ad0"`
  - `_expected_profiling_runner_sha256(results: list[Mapping[str, Any]]) -> str`
  - version-specific validation with unknown and mixed versions rejected.

- [ ] **Step 1: Write RED tests for historical, formal, mixed, and unknown versions**

Update the profiling test helpers so historical synthetic receipts use
`p3-phase1-unexecuted-v1` and the frozen historical source SHA. Add tests that:

1. accept an existing historical receipt after `bridge_and_frames.py` changes;
2. accept a Task 2 receipt whose source SHA equals
   `file_sha256(Path(profiling_runner.__file__))`;
3. reject mixed historical/formal row versions; and
4. reject an unknown runner version even when the receipt is rehashed.

Run the four tests before implementation. Expected: the historical receipt
fails because the current validator still expects the current
`bridge_and_frames.py` file SHA.

- [ ] **Step 2: Implement the narrow source selector**

Add the frozen historical constant. The selector must implement exactly:

```python
def _expected_profiling_runner_sha256(results: list[Mapping[str, Any]]) -> str:
    versions = {row.get("runner_version") for row in results}
    if not results:
        return PHASE1_UNEXECUTED_RUNNER_SHA256
    if versions == {"p3-phase1-unexecuted-v1"}:
        return PHASE1_UNEXECUTED_RUNNER_SHA256
    if versions == {"p3-cxx-header-compile-profiler-v1"}:
        from p3_v3 import profiling_runner

        return file_sha256(Path(profiling_runner.__file__))
    raise EvidenceError("E_PROFILE_RUNNER_BINDING", "runner version is unknown or mixed")
```

Change `build_phase1_unresolved_profiling_receipt` to write the frozen historical
constant instead of `file_sha256(Path(__file__))`. In
`_validated_profiling_rows`, compare the receipt field against the selector's
result. Do not change any other profiling schema or classification rule.

- [ ] **Step 3: Add the mandatory 35-receipt compatibility regression**

Add one test that enumerates exactly the tracked files:

```python
def test_all_35_phase1_profiling_receipts_keep_historical_runner_binding():
    root = Path(__file__).resolve().parents[2] / "data/p3_v3/phase1_frames/out"
    receipts = sorted(root.glob("profiling-results-*.json"))
    assert len(receipts) == 35
    for receipt_path in receipts:
        neutral = receipt_path.stem.removeprefix("profiling-results-")
        workload_path = root / f"profiling-workload-{neutral}.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        workload = json.loads(workload_path.read_text(encoding="utf-8"))
        assert receipt["runner_implementation_source_sha256"] == (
            frames_module.PHASE1_UNEXECUTED_RUNNER_SHA256
        )
        classify_technique(workload, receipt)
```

This is the only required broad historical check. Do not rebuild or rewrite the
35 receipts.

- [ ] **Step 4: Run the binding and 35-receipt tests**

Run:

```bash
PYTHONPATH=src .venv/bin/python -m pytest \
  tests/p3_v3/test_bridge_and_frames.py \
  -k 'profiling_runner_binding or all_35_phase1_profiling_receipts or phase1_unresolved_receipt' -q
```

Expected: all selected tests pass, including empty-workload historical receipt
coverage.

- [ ] **Step 5: Run all profiling-focused bridge tests and commit**

Run:

```bash
PYTHONPATH=src .venv/bin/python -m pytest \
  tests/p3_v3/test_bridge_and_frames.py \
  -k 'profiling or cxx_profile or classify_technique' -q
git diff --check
```

Commit:

```bash
git add src/p3_v3/bridge_and_frames.py tests/p3_v3/test_bridge_and_frames.py
git commit -m "fix: bind profiling receipts to runner versions"
```

---

### Task 4: Thin production CLI

**Files:**
- Create: `scripts/p3_v3/profile.py`
- Modify: `tests/p3_v3/test_cli.py`

**Interfaces:**
- Consumes: `profiling_runner.run_cxx_header_workload` and five explicit CLI
  paths.
- Produces: `profile.py run-cxx-header-workload --workload PATH --source-root
  PATH --compiler PATH --runtime-root PATH --output PATH`.

- [ ] **Step 1: Write failing parser and delegation tests**

Load `scripts/p3_v3/profile.py` as a module using the same pattern already used
for repository CLIs. Add tests asserting that the parser requires exactly one
subcommand and five required path options, and that:

```python
assert module.main([
    "run-cxx-header-workload",
    "--workload", str(workload),
    "--source-root", str(source_root),
    "--compiler", "/usr/bin/c++",
    "--runtime-root", str(runtime_root),
    "--output", str(output),
]) == 0
assert called == [(workload, source_root, Path("/usr/bin/c++"), runtime_root, output)]
```

Monkeypatch only `run_cxx_header_workload`; the CLI must not inspect or mutate
scientific data itself.

- [ ] **Step 2: Run the CLI tests and verify RED**

Run:

```bash
PYTHONPATH=src .venv/bin/python -m pytest \
  tests/p3_v3/test_cli.py -k 'cxx_header_workload_cli' -q
```

Expected: FAIL because `scripts/p3_v3/profile.py` does not exist.

- [ ] **Step 3: Implement the thin CLI**

Follow `scripts/p3_v3/pilot.py`'s root-path setup and error handling. The main
branch must be only:

```python
if args.command == "run-cxx-header-workload":
    workload = read_canonical_json(args.workload)
    run_cxx_header_workload(
        workload,
        source_root=Path(args.source_root),
        compiler=Path(args.compiler),
        runtime_root=Path(args.runtime_root),
        receipt_path=Path(args.output),
    )
```

Catch `EvidenceError`, print it once to stderr, and return 1. Return 0 on
successful receipt publication. Do not add a dry-run, retry, cleanup, or
profiling-analysis subcommand.

- [ ] **Step 4: Run CLI and profiling-focused tests**

Run:

```bash
PYTHONPATH=src .venv/bin/python -m pytest \
  tests/p3_v3/test_cli.py -k 'cxx_header_workload_cli' -q
PYTHONPATH=src .venv/bin/python -m pytest \
  tests/p3_v3/test_bridge_and_frames.py \
  -k 'profiling or cxx_profile or classify_technique' -q
git diff --check
```

Expected: both focused selections pass.

- [ ] **Step 5: Commit the CLI**

```bash
git add scripts/p3_v3/profile.py tests/p3_v3/test_cli.py
git commit -m "feat: expose cxx header profiling cli"
```

---

### Task 5: Final focused implementation verification

**Files:**
- Verify only; no planned file modification.

**Interfaces:**
- Consumes: Tasks 1-4 implementation commits.
- Produces: one implementation commit range ready for narrow Standards/Spec
  review; no formal profiling receipt.

- [ ] **Step 1: Verify exact scope**

Run:

```bash
git diff --name-only \
  533d18bf3838530ea637d7c3a3b249978b43ee72..HEAD -- \
  scripts/p3_v3 src/p3_v3 tests/p3_v3
```

Expected files only:

```text
scripts/p3_v3/profile.py
src/p3_v3/bridge_and_frames.py
src/p3_v3/profiling_runner.py
tests/p3_v3/test_bridge_and_frames.py
tests/p3_v3/test_cli.py
```

The path filter deliberately excludes the already committed design and this
implementation plan from the production/test scope check.

- [ ] **Step 2: Run the complete focused verification**

Run only:

```bash
PYTHONPATH=src .venv/bin/python -m pytest \
  tests/p3_v3/test_bridge_and_frames.py \
  -k 'profiling or cxx_profile or classify_technique' -q
PYTHONPATH=src .venv/bin/python -m pytest \
  tests/p3_v3/test_cli.py -k 'cxx_header_workload_cli' -q
git diff --check 533d18bf3838530ea637d7c3a3b249978b43ee72..HEAD
git status --porcelain=v1
```

Required results:

- both pytest selections pass;
- the mandatory system-Boost depfile test passes;
- the mandatory 35-receipt compatibility test passes;
- `git diff --check` exits 0; and
- porcelain is empty.

- [ ] **Step 3: Record the review handoff**

Report:

- implementation HEAD and parent chain from
  `533d18bf3838530ea637d7c3a3b249978b43ee72`;
- each commit subject;
- exact changed-file list;
- focused test counts and exit codes;
- explicit confirmation that no qualification, Attempt-2, formal profiling,
  full suite, dependency installation, tracked evidence rewrite, commit push, or
  formal execution occurred.

Stop for narrow Standards/Spec review. Formal profiling requires separate user
authorization after that review passes.
