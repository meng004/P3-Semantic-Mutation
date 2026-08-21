# P3 Compiler-Alias CI Test Repair Design

**Status:** Design archived; implementation is not authorized
**Node:** `P1BP1I2Q9_CURSOR_VM_P3_COMPILER_ALIAS_CI_REPAIR_SPEC_PLAN`
**Type:** `GOVERNANCE_ONLY`
**Baseline:** `origin/main` `4444061dde0159a5edd62753fe3cef2d881a308c`
**Classification:** `LATENT_PREEXISTING_PLATFORM_DEPENDENT_TEST_FAILURE`
**Claims:** blocked
**Formal denominator membership:** false
**Attempt-2 authorized:** false
**Real qualification authorized:** false
**Merge authorized:** false
**Design choice:** A (portable compile_commands-only mismatch fixture)

This document archives the approved semantics for a host-independent
`compile_commands` compiler-mismatch test. It is not an implementation
plan or implementation verdict. Writing or merging this file does not
authorize code edits, workflow edits, or claim upgrades.

This repair is independent of pull requests 16 and 17. It must not copy
commits from those branches. PR 17 did not change
`src/p3_v3/pilot_build.py` or `tests/p3_v3/test_pilot_build.py`.

## Problem Classification

This failure is:

```text
LATENT_PREEXISTING_PLATFORM_DEPENDENT_TEST_FAILURE
```

It is not:

- a supplemental R2 implementation regression;
- a production compiler-identity defect;
- a pull request 16 regression;
- a workflow defect.

`origin/main` already contains the fixture. GitHub Actions run
`32225095224` reached this test only after supplemental R2
`external_slice` passed. The first `--maxfail=1` stop on `origin/main`
is a different, already-classified path-scan failure.

## Frozen CI Evidence

| Item | Value |
|---|---|
| Workflow | `sanity-check` |
| Check | `Run pytest (Path-A cache replay smoke)` |
| Run | `32225095224` |
| Job | `95983092497` |
| Run head | `fb20947a102934415dd201665971a711ccc4e0d5` |
| Test | `test_compile_commands_compiler_mismatch` |
| Path | `tests/p3_v3/test_pilot_build.py` |
| Line | 1306 |
| Error | `Failed: DID NOT RAISE EvidenceError` |
| Count | `1 failed, 1196 passed, 9 warnings` |

Authoritative RED is that GitHub Actions Linux signature. A local PASS
does not close the defect.

## Frozen Diagnosis

`_synthetic_build_evidence_tree` writes one `compiler` value into:

- `CMakeCache.txt` `CMAKE_CXX_COMPILER`;
- `compile_commands.json` `arguments[0]`;
- `environment["cxx_compiler_path"]`.

The current test then changes only the environment path to
`/usr/bin/g++`. The tree still holds `/usr/bin/c++` in CMakeCache and
`compile_commands.json`.

`collect_baseline_build_evidence` compares with `os.path.realpath`:

1. CMakeCache compiler versus environment compiler;
2. `compile_commands` argv0 versus environment compiler.

On Ubuntu, `/usr/bin/c++` and `/usr/bin/g++` may resolve to the same
binary. The current fixture then creates no realpath mismatch, so
neither check raises.

Read-only reproduction on this Cursor VM, with `PYTHONNOUSERSITE`
temporarily cleared so the already-installed user-site pytest could
load. No package was installed.

```text
/usr/bin/c++ realpath = /usr/lib/llvm-18/bin/clang
/usr/bin/g++ realpath = /usr/bin/x86_64-linux-gnu-g++-13
equal = False
test_compile_commands_compiler_mismatch = PASS
```

This local PASS is host-specific. The GitHub Actions RED remains the
cross-platform authority.

This is a test-fixture platform dependency. Production realpath compare
is the intended contract.

## Approved Design: A

A later implementation node may edit only:

```text
tests/p3_v3/test_pilot_build.py
```

Keep the test name `test_compile_commands_compiler_mismatch`.

The future fixture must:

1. Build two different absolute synthetic paths under `tmp_path`,
   called compiler A and compiler B.
2. Call `_synthetic_build_evidence_tree` with `compiler=A`.
3. Leave CMakeCache compiler equal to A.
4. Leave `environment["cxx_compiler_path"]` equal to A.
5. Rewrite only `compile_commands.json` entry 0 `arguments[0]` to B.
6. Write the file back as legal JSON.
7. Call `collect_baseline_build_evidence`.
8. Assert exactly:

```python
pytest.raises(
    EvidenceError,
    match="compile_commands compiler differs",
)
```

The failure must come from the `compile_commands` check, not from the
earlier CMakeCache compiler check. A and B must have different
realpaths. They need not exist as executables. Do not invoke a real
compiler.

## Refused Designs

### B. Monkeypatch `os.path.realpath`

Refused. It binds the test to an implementation detail and does not
prove that the real path inputs are wrong.

### C. Change production to lexical string compare

Refused. It would reject a legal symlink or alias pair, change frozen
evidence semantics, and exceed this node's write set.

### D. Change the workflow, skip, xfail, or delete the test

Refused. That would hide the failure.

## Contracts That Stay

- `collect_baseline_build_evidence` production bytes stay unchanged.
- realpath compare semantics stay unchanged.
- The independent CMakeCache mismatch coverage in
  `test_cmakecache_compiler_generator_root_drift` stays.
- The compile_commands mismatch must hit
  `compile_commands compiler differs` exactly.
- No real compiler, CMake, ninja, make, or Boost.Math.
- Pull requests 16 and 17 stay unmodified.
- claims, attempt-2, and merge stay unauthorized.

## Future Verification

A later implementation node must record:

- the GitHub Actions Linux RED before the test edit;
- focused GREEN of the same named test;
- `tests/p3_v3/test_pilot_build.py`;
- root `pytest -q --maxfail=1`;
- `git diff --check`;
- a one-file implementation scope check.

If the root suite exposes an unrelated first failure, stop and triage.
Do not widen scope.

## Non-Goals

This design does not authorize implementation, merge, attempt-2, or
claim upgrades. It does not change `.github/workflows`.

## Governance Stop

After this specification and the matching plan are committed and
pushed, work stops for Sol review. Implementation remains
unauthorized until a later user node writes a 40-character
IMPLEMENTATION_ENTRY after dual-axis PASS.

## Self-Review Record

- Classification is explicit.
- Choice A isolates the compile_commands check.
- Choices B, C, and D are refused.
- Future write set is one test file.
- Pull requests 16 and 17 are out of scope.
