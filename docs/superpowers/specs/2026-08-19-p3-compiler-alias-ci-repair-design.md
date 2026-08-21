# P3 Residual CMakeCache Compiler-Mismatch Repair Design

**Status:** Design archived; implementation is not authorized
**Node:** `P1BP1I2Q17_CURSOR_VM_PR18_RESIDUAL_CMAKECACHE_SPEC_PLAN`
**Type:** `GOVERNANCE_ONLY`
**Classification:** `RESIDUAL_PREEXISTING_PLATFORM_DEPENDENT_CMAKECACHE_TEST_FAILURE`
**Baseline:** `origin/main` `4444061dde0159a5edd62753fe3cef2d881a308c`
**Branch:** `cursor/p3-compiler-alias-ci-repair-c46c`
**Pull request:** 18
**Claims:** blocked
**Formal denominator membership:** false
**Attempt-2 authorized:** false
**Real qualification authorized:** false
**Merge authorized:** false
**Design choice:** A (test-only; keep production realpath identity)

This document archives the narrowed semantics for the residual
CMakeCache host-coupled mismatch oracle. It is not an implementation
plan or implementation verdict. Writing or merging this file does not
authorize code edits, workflow edits, CI repair, or claim upgrades.

## Classification

The live defect is:

```text
RESIDUAL_PREEXISTING_PLATFORM_DEPENDENT_CMAKECACHE_TEST_FAILURE
```

It is not:

- a pull request 17, 19, or 28 regression;
- a production compiler-identity defect;
- a workflow defect;
- qualification or claims evidence.

GitHub Actions RED is the authoritative RED. A local pre-edit PASS
does not close the defect.

## Purpose

Pull request 19 already repaired
`test_compile_commands_compiler_mismatch`. Pull request 28 integrated
that complete history. The next `--maxfail=1` failure on the combined
branch is the CMakeCache compiler subcase inside
`test_cmakecache_compiler_generator_root_drift`.

The fixture never constructs a portable realpath mismatch. Production
`os.path.realpath` comparison is correct and must stay. The future
repair may change only that CMakeCache subcase.

## Frozen CI Evidence

The authoritative RED is pull request 28 GitHub Actions, not the
superseded pull request 17 compile_commands failure.

```text
PR #28 head =
e62974af4f5e2cfbc65d98c3b2f028edce57d25c

run =
32449925094

job =
96676383508

test =
tests/p3_v3/test_pilot_build.py::
test_cmakecache_compiler_generator_root_drift

line =
1344

failure =
DID NOT RAISE EvidenceError

expected match =
CMakeCache compiler differs

collected =
1693

passed before failure =
1197

failed =
1

warnings =
9

duration =
1164.65 seconds
```

| Item | Value |
|---|---|
| Workflow | `sanity-check` |
| Check | `Run pytest (Path-A cache replay smoke)` |
| Command | `pytest -q --maxfail=1` with `PYTHONPATH=src` |
| Combined head | `e62974af4f5e2cfbc65d98c3b2f028edce57d25c` |

## Root Cause

`_synthetic_build_evidence_tree` defaults `compiler` to `/usr/bin/c++`.
That default is written into the environment snapshot, `CMakeCache.txt`,
and `compile_commands.json`.

The failing subcase changes only `cache_compiler` to `/usr/bin/g++`.
The environment compiler and the `compile_commands` argv0 stay at the
fixture default.

Production compares:

```text
os.path.realpath(cache_compiler)
os.path.realpath(environment compiler)
```

at `src/p3_v3/pilot_build.py`:

```text
if cache_compiler is None or os.path.realpath(cache_compiler) != os.path.realpath(compiler):
    raise EvidenceError("E_PILOT_BUILD_ENVIRONMENT", "CMakeCache compiler differs")
```

On the GitHub runner those two host paths can resolve to the same
compiler. The fixture therefore does not construct a real mismatch, and
the test reports `DID NOT RAISE EvidenceError`.

Production realpath semantics are correct and must be retained. The
defect is the host-coupled oracle, not the production compare.

## Relation To Pull Request 19 And Pull Request 28

- Pull request 19 already repaired
  `test_compile_commands_compiler_mismatch` at
  `3352cedb5f377b60f0aec5ff80997b2057c7fc14`.
- Pull request 18 must not modify that function again.
- This node must not copy, replace, or rewrite pull request 19
  commits.
- Pull request 28 already contains the complete history of pull
  request 19 at `e62974af4f5e2cfbc65d98c3b2f028edce57d25c`.
- This node handles only the CMakeCache subcase that became visible
  after that integration.

## Approved Minimal Future Change

A later implementation node, if authorized, may edit only:

```text
tests/p3_v3/test_pilot_build.py
```

and only the function:

```text
test_cmakecache_compiler_generator_root_drift
```

Only the compiler subcase may be replaced, with this exact form:

```python
    cache_other = tmp_path / "cache-other-cxx"
    build, env = _synthetic_build_evidence_tree(
        tmp_path / "compiler",
        pilot_build,
        monkeypatch,
        cache_compiler=str(cache_other),
    )
    with pytest.raises(
        EvidenceError,
        match="CMakeCache compiler differs",
    ):
        pilot_build.collect_baseline_build_evidence(build, env)
```

The later node must keep:

- the environment compiler as the fixture default compiler;
- the `compile_commands` compiler as the fixture default compiler;
- only the CMakeCache compiler set to `cache_other`;
- `cache_other` under `tmp_path`;
- no real compiler invocation;
- the generator mismatch subcase unchanged;
- the source-root mismatch subcase unchanged;
- production unchanged;
- the test function name unchanged;
- an exact match on `CMakeCache compiler differs`.

The later implementation commit title must be:

```text
test(p3-v3): make CMakeCache mismatch portable
```

This archival node must not edit that file.

## Refused Designs

Refuse:

- changing production to lexical string compare;
- monkeypatching `os.path.realpath`;
- keeping `/usr/bin/g++` as the mismatch oracle;
- editing the pull request 19 compile_commands test;
- adding a symlink-alias acceptance test unrelated to this residual
  failure;
- skip, xfail, deleting the test, or editing the workflow;
- modifying pull request 28 from this node;
- treating plan archival as an implementation grant.

## Historical Superseded Context

The original archival design treated three compiler-alias scenes as one
repair: `test_compile_commands_compiler_mismatch`, the CMakeCache
subcase, and a new symlink alias acceptance test. It also treated pull
request 17 CI run `32225095224` (`1 failed, 1196 passed`) as the primary
RED.

That broader scope is superseded. Pull request 19 closed the
compile_commands oracle. The 1196-passed RED is historical only. Pull
request 18 must not claim to close every compiler-alias test in one
change.

## Non-Goals

This design does not:

- change `.github/workflows` or skip `tests/p3_v3`;
- xfail, skip, or delete the failing test;
- change `src/p3_v3/pilot_build.py` or qualification modules;
- change supplemental R2 scanners or pull request 17;
- rewrite or duplicate pull request 19;
- edit pull request 28;
- run CMake, a real compiler, ninja, make, or Boost.Math;
- run readiness, canonical freeze, retrieval, or SSOT writes;
- authorize implementation, merge, attempt-2, or claim upgrades.

## Governance Stop

After this specification and the matching plan are committed and
pushed on `cursor/p3-compiler-alias-ci-repair-c46c`, work stops for
Sol review. Implementation remains unauthorized until a later user
node raises `IMPLEMENTATION_AUTHORIZED` from false after Sol review
and writes a 40-character `IMPLEMENTATION_ENTRY` in that instruction.

Pull request 18 stays draft. Pull requests 19 and 28 stay untouched.

## Self-Review Record

- Classification is residual CMakeCache host coupling, not a
  production or workflow defect.
- Authoritative RED is pull request 28 run `32449925094`.
- Future write set is one function in one test file.
- Pull request 19 compile_commands repair is out of scope.
- Implementation authorization is withheld.
