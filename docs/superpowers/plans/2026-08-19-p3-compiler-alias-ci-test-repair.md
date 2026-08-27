# P3 Compiler-Alias CI Test Repair Implementation Plan

> **For agentic workers:** Use executing-plans only after Sol writes a
> 40-character IMPLEMENTATION_ENTRY and sets implementation executable.
> This archival node forbids starting any Task.

**Goal:** Make `test_compile_commands_compiler_mismatch` prove a
compile_commands-only realpath mismatch on every host.

**Architecture:** Design choice A. Keep production
`collect_baseline_build_evidence` bytes and `os.path.realpath` compares.
Build the fixture with compiler A, then rewrite only
`compile_commands.json` arguments[0] to compiler B.

**Tech Stack:** Python 3.12 invoked as `/usr/bin/python3`, pytest,
existing `p3_v3.pilot_build`.

## Global Constraints

- Implement against
  `docs/superpowers/specs/2026-08-19-p3-compiler-alias-ci-test-repair-design.md`
  with SHA-256
  `6f677b3c87fe5dff724a45f9032aaf0125a8be53f548aa07ebd0ddceb78bc95b`.
- Classification is
  `LATENT_PREEXISTING_PLATFORM_DEPENDENT_TEST_FAILURE`.
- A later implementation node may edit only
  `tests/p3_v3/test_pilot_build.py`.
- Keep the test name `test_compile_commands_compiler_mismatch`.
- Do not modify `src/p3_v3/pilot_build.py`, workflows, PR 16, or PR 17.
- Do not monkeypatch `os.path.realpath`.
- Do not change production to lexical string compare.
- Do not skip, xfail, or delete the test.
- Use `/usr/bin/python3` only. Do not use `rtk`.
- Do not install or upgrade dependencies.
- Do not run a real compiler, CMake, ninja, make, or Boost.Math.
- Do not run `scripts/build_paper_numbers.py`.
- `IMPLEMENTATION_AUTHORIZED=false`
- `IMPLEMENTATION_EXECUTABLE=false`
- `MERGE_AUTHORIZED=false`
- `IMPLEMENTATION_ENTRY` must be the full 40-character SHA Sol writes
  in the implementation instruction after PASS. If it is omitted,
  stop. Do not derive it from origin tip, branch, merge-base, PR head,
  or clock time.

---

## File Structure

- Modify: `tests/p3_v3/test_pilot_build.py`
  function `test_compile_commands_compiler_mismatch` only, plus the
  smallest local JSON rewrite needed by that test.
- Do not create a helper module.

## Frozen CI Evidence

| Item | Value |
|---|---|
| Run | `32225095224` job `95983092497` |
| Head | `fb20947a102934415dd201665971a711ccc4e0d5` |
| Test | `test_compile_commands_compiler_mismatch` |
| Error | `DID NOT RAISE EvidenceError` |

---

### Task 1: Confirm Implementation Entry

**Files:** read only

Frozen invariants:

```text
branch: cursor/p3-compiler-alias-ci-test-repair-c46c
origin/main: 4444061dde0159a5edd62753fe3cef2d881a308c
merge-base: 4444061dde0159a5edd62753fe3cef2d881a308c
```

- [ ] **Step 1: Refuse without an explicit Sol entry**

Stop unless the later node writes `IMPLEMENTATION_ENTRY` as a full
40-character SHA and sets implementation executable. Plan archival
is not that grant. `IMPLEMENTATION_AUTHORIZED=false` and
`IMPLEMENTATION_EXECUTABLE=false` until then.

- [ ] **Step 2: Verify exact SHAs and a clean tree**

```bash
git fetch origin
git rev-parse --abbrev-ref HEAD
git rev-parse HEAD
git rev-parse origin/cursor/p3-compiler-alias-ci-test-repair-c46c
git rev-parse origin/main
git merge-base HEAD origin/main
git rev-list --left-right --count \
  HEAD...origin/cursor/p3-compiler-alias-ci-test-repair-c46c
git status --porcelain
```

Required:

```text
branch = cursor/p3-compiler-alias-ci-test-repair-c46c
HEAD = IMPLEMENTATION_ENTRY
origin repair tip = IMPLEMENTATION_ENTRY
origin/main = 4444061dde0159a5edd62753fe3cef2d881a308c
merge-base = 4444061dde0159a5edd62753fe3cef2d881a308c
ahead/behind = 0	0
porcelain = empty
```

Do not reset, rebase, amend, or force-push to hide a mismatch.

- [ ] **Step 3: Confirm the design digest**

```bash
/usr/bin/python3 - <<'PY'
from hashlib import sha256
from pathlib import Path
p = Path(
    "docs/superpowers/specs/"
    "2026-08-19-p3-compiler-alias-ci-test-repair-design.md"
)
digest = sha256(p.read_bytes()).hexdigest()
print(digest)
assert digest == (
    "6f677b3c87fe5dff724a45f9032aaf0125a8be53f548aa07ebd0ddceb78bc95b"
)
PY
```

---

### Task 2: Record RED Without Production Edits

**Files:** none

- [ ] **Step 1: Keep the GitHub Actions Linux RED**

```text
Failed: DID NOT RAISE <class 'p3_v3.artifacts.EvidenceError'>
tests/p3_v3/test_pilot_build.py:1306
1 failed, 1196 passed, 9 warnings
run 32225095224 job 95983092497
```

That signature is the authoritative pre-edit RED.

- [ ] **Step 2: Optionally rerun the current test locally**

```bash
PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1 \
  tests/p3_v3/test_pilot_build.py::\
test_compile_commands_compiler_mismatch
```

If `PYTHONNOUSERSITE=1` hides the existing pytest, clear that
variable for the command only. Do not install pytest. A local PASS
does not replace the Actions RED.

Do not edit `src/p3_v3/pilot_build.py`.

---

### Task 3: Rewrite Only The Named Test

**Files:**
- Modify: `tests/p3_v3/test_pilot_build.py`

- [ ] **Step 1: Replace the host-coupled fixture**

Keep the function name. Do not use `/usr/bin/c++` or `/usr/bin/g++`
as the mismatch pair. Use two different `tmp_path` absolute paths.
Call `_synthetic_build_evidence_tree` with compiler A. Keep
CMakeCache and the environment on A. Rewrite only
`compile_commands.json` arguments[0] to B.

```python
def test_compile_commands_compiler_mismatch(tmp_path, monkeypatch):
    import json
    import p3_v3.pilot_build as pilot_build

    compiler_a = str((tmp_path / "compiler-a").resolve())
    compiler_b = str((tmp_path / "compiler-b").resolve())
    build, env = _synthetic_build_evidence_tree(
        tmp_path,
        pilot_build,
        monkeypatch,
        compiler=compiler_a,
    )
    assert env["cxx_compiler_path"] == compiler_a
    cache = (build / "CMakeCache.txt").read_text(encoding="utf-8")
    assert f"CMAKE_CXX_COMPILER:FILEPATH={compiler_a}" in cache
    commands_path = build / "compile_commands.json"
    payload = json.loads(commands_path.read_text(encoding="utf-8"))
    payload[0]["arguments"][0] = compiler_b
    commands_path.write_text(
        json.dumps(payload) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(
        EvidenceError,
        match="compile_commands compiler differs",
    ):
        pilot_build.collect_baseline_build_evidence(build, env)
```

The raise must be the compile_commands check. CMakeCache still
equals A, so that earlier check cannot fire.

---

### Task 4: Focused GREEN And Same-Identity Proof

- [ ] **Step 1: Run the named test**

```bash
PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1 \
  tests/p3_v3/test_pilot_build.py::\
test_compile_commands_compiler_mismatch
```

Expected: PASS.

- [ ] **Step 2: Keep the A/A identity asserts**

The assertions in Task 3 already prove CMakeCache and the
environment remain compiler A after the JSON rewrite. Do not add
a host `/usr/bin/c++` versus `/usr/bin/g++` check.

---

### Task 5: File Suite And Root Gate

- [ ] **Step 1: Run the pilot_build file**

```bash
PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1 \
  tests/p3_v3/test_pilot_build.py
```

Expected: the file PASS count is recorded. The independent
CMakeCache mismatch cases remain.

- [ ] **Step 2: Run the Actions pytest command**

```bash
PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1
```

If the first failure is this named test, stop. If it is an
unrelated failure, stop and triage. Do not widen scope. Do not
xfail. Path-scan on `origin/main` remains a separate repair.

- [ ] **Step 3: Do not run live builds**

Do not run a real compiler, CMake, ninja, make, or Boost.Math.
Do not run `scripts/build_paper_numbers.py`.

---

### Task 6: Scope, Commit, Push, Draft Stop

**Files:** only `tests/p3_v3/test_pilot_build.py`

- [ ] **Step 1: Working-tree scope before commit**

```bash
git status --porcelain
git diff --check
git diff --name-only
git diff --cached --name-only
git ls-files --others --exclude-standard
```

The only allowed path is `tests/p3_v3/test_pilot_build.py`.

- [ ] **Step 2: Independent implementation commit**

```bash
git add tests/p3_v3/test_pilot_build.py
git commit -m "test(p3-v3): make compiler mismatch portable"
```

Do not amend, squash, or rebase already-pushed commits.

- [ ] **Step 3: History scope before push**

```bash
git diff --check origin/main...HEAD
git diff --name-only origin/main...HEAD
git show --name-only --format= HEAD
git rev-list --left-right --count \
  HEAD...origin/cursor/p3-compiler-alias-ci-test-repair-c46c
```

`origin/main...HEAD` may contain only the two archive documents
and the one test file. The newest implementation commit may
contain only the test file. Push-time ahead/behind must be
`1	0`.

- [ ] **Step 4: Push and keep the new PR draft**

```bash
git push -u origin cursor/p3-compiler-alias-ci-test-repair-c46c
```

Do not mark the new PR ready. Do not merge. Do not edit PR 16 or
PR 17.

- [ ] **Step 5: Confirm the other pull requests**

```bash
gh pr view 16 \
  --repo meng004/P3-Semantic-Mutation \
  --json state,isDraft,headRefOid
gh pr view 17 \
  --repo meng004/P3-Semantic-Mutation \
  --json state,isDraft,headRefOid
```

Required:

```text
PR 16 state=OPEN isDraft=false
PR 16 headRefOid=081bb6176d25d47f9bd58ee688c12dadae06fa68
PR 17 state=OPEN isDraft=true
PR 17 headRefOid=fb20947a102934415dd201665971a711ccc4e0d5
```

---

## Non-Goals

This plan does not:

- change production realpath compares
- monkeypatch `os.path.realpath`
- change the workflow, skip, or xfail
- modify PR 16 or PR 17
- treat plan archival as an executable grant

## Governance Stop

`IMPLEMENTATION_AUTHORIZED=false`
`IMPLEMENTATION_EXECUTABLE=false`
`MERGE_AUTHORIZED=false`

A later user node must still write `IMPLEMENTATION_ENTRY` after
Sol Spec + Standards PASS. The new repair PR stays draft.

## Self-Review Record

- Spec coverage: compile_commands-only rewrite, exact error match,
  one-file write set, fail-closed entry.
- Incomplete-marker scan: clean.
- Execution is not offered from this archival node.
