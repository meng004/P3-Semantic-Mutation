# Residual CMakeCache Compiler-Mismatch Repair Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:executing-plans only after Sol writes a 40-character
> `IMPLEMENTATION_ENTRY` and sets `IMPLEMENTATION_AUTHORIZED` and
> `IMPLEMENTATION_EXECUTABLE` to true. This archival node forbids
> starting any Task.

**Goal:** Make the residual CMakeCache compiler-mismatch subcase in
`test_cmakecache_compiler_generator_root_drift` host-independent
without changing production realpath identity.

**Architecture:** Design choice A. Keep `os.path.realpath` in
`collect_baseline_build_evidence`. Replace only the CMakeCache
compiler oracle with a `tmp_path` identity named `cache-other-cxx`.
Do not retouch the pull request 19 compile_commands repair. Do not
add a helper module or an extra alias acceptance test.

**Tech Stack:** Python 3.12 invoked as `/usr/bin/python3`, pytest,
existing `p3_v3.pilot_build`.

The design file identified by SHA-256
`853001ef80c48de4ce17c47439b58609c893180b5a2b97592ef8746c61899cdc`
is the semantic SSOT. This plan repeats only the frozen values,
exact patch, and fail-closed assertions that a later executor
must consume. Those repeated items are executable assertions, not
a second semantic definition. If this plan conflicts with the
design, the executor must stop and return the conflict to Sol.

## Global Constraints

- Implement against
  `docs/superpowers/specs/2026-08-19-p3-compiler-alias-ci-repair-design.md`
  with SHA-256
  `853001ef80c48de4ce17c47439b58609c893180b5a2b97592ef8746c61899cdc`.
- Classification is
  `RESIDUAL_PREEXISTING_PLATFORM_DEPENDENT_CMAKECACHE_TEST_FAILURE`.
- Design choice is A. Lexical production compare and
  `os.path.realpath` monkeypatches are refused.
- A later implementation node may edit only
  `tests/p3_v3/test_pilot_build.py`, and only
  `test_cmakecache_compiler_generator_root_drift`.
- Frozen write-set hashes for that file:
  pre-edit SHA-256
  `3757f4289f0b0efdc4726a513b97fc56a402e708c5053d24ca48bd246283310e`
  approved post-edit SHA-256
  `c82d6413dd6fb1c6ac651e518da5e0524e5a415ef768ebe344e51543b728ce2a`
- `git merge-base HEAD origin/main` must equal
  `4444061dde0159a5edd62753fe3cef2d881a308c`. Running the command
  or checking `origin/main` alone is not enough.
- Do not modify `src/p3_v3/pilot_build.py`, qualification modules,
  `.github/workflows`, supplemental R2 scanners, PR 16, PR 17,
  PR 19, or PR 28.
- Keep production realpath compare at the CMakeCache and
  compile_commands checks.
- Use `/usr/bin/python3` only. Do not use `rtk`.
- Do not run CMake, a real compiler, ninja, make, or Boost.Math.
- Do not run `scripts/build_paper_numbers.py` in any form.
- Keep pull request 18 draft. Do not mark-ready. Do not merge.
- Claims stay blocked. Formal denominator membership stays false.
- Archiving this plan does not authorize implementation.
- `IMPLEMENTATION_AUTHORIZED=false` at archival.
- `IMPLEMENTATION_EXECUTABLE=false` at archival.
- `PR_READY_AUTHORIZED=false`.
- `MAIN_PR_MERGE_AUTHORIZED=false`.
- `MERGE_AUTHORIZED=false`.
- `IMPLEMENTATION_ENTRY` must be the full 40-character commit SHA
  that Sol writes after this revised plan is reviewed. If that
  instruction omits it, stop. Do not derive it from the origin tip,
  branch name, merge-base, PR head, or clock time.

---

## File Structure

- Modify: `tests/p3_v3/test_pilot_build.py`
  - only `test_cmakecache_compiler_generator_root_drift`
  - only the CMakeCache compiler subcase
- Do not modify `src/p3_v3/pilot_build.py`.
- Do not modify `test_compile_commands_compiler_mismatch`.

## Frozen CI Evidence

The following tuple is an executable assertion for Task 2, not a
second semantic definition. The authoritative RED is pull request
28 GitHub Actions.

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

GitHub Actions RED is authoritative. A local pre-edit PASS does not
close the defect.

---

### Task 1: Confirm The Explicit Future Entry

**Files:**
- Read only: this plan, the design spec, `origin/main`,
  `tests/p3_v3/test_pilot_build.py`

**Interfaces:**
- Consumes: spec SHA-256
  `853001ef80c48de4ce17c47439b58609c893180b5a2b97592ef8746c61899cdc`
  pre-edit test SHA-256
  `3757f4289f0b0efdc4726a513b97fc56a402e708c5053d24ca48bd246283310e`
  approved post-edit test SHA-256
  `c82d6413dd6fb1c6ac651e518da5e0524e5a415ef768ebe344e51543b728ce2a`
- Produces: a written entry record. No code edits.

The future implementation entry must be the Sol-written 40-character
SHA of the reviewed tip of
`cursor/p3-compiler-alias-ci-repair-c46c` after this revised plan
passes review.

- [ ] **Step 1: Refuse unless implementation is executable**

Archiving this plan is not a grant. Stop unless Sol has set
`IMPLEMENTATION_AUTHORIZED=true`,
`IMPLEMENTATION_EXECUTABLE=true`, and written
`IMPLEMENTATION_ENTRY` as a full 40-character SHA.

- [ ] **Step 2: Atomic explicit-destination fetch, then compare**

Do not start from PR 16, PR 17, PR 19, or PR 28. Do not
cherry-pick those commits. Do not reset, rebase, amend, or
force-push. If any value differs, stop.

```bash
export GIT_CONFIG_GLOBAL=/dev/null
export GIT_CONFIG_NOSYSTEM=1
export GIT_CONFIG_COUNT=0

git status --porcelain

git fetch --atomic origin \
  +refs/heads/main:refs/remotes/origin/main \
  +refs/heads/cursor/p3-compiler-alias-ci-repair-c46c:refs/remotes/origin/cursor/p3-compiler-alias-ci-repair-c46c

git switch cursor/p3-compiler-alias-ci-repair-c46c

git rev-parse --abbrev-ref HEAD
git rev-parse HEAD
git rev-parse origin/cursor/p3-compiler-alias-ci-repair-c46c
git rev-parse origin/main
git merge-base HEAD origin/main
git rev-list --left-right --count \
  HEAD...origin/cursor/p3-compiler-alias-ci-repair-c46c
git status --porcelain
```

Required results:

```text
branch = cursor/p3-compiler-alias-ci-repair-c46c
HEAD = IMPLEMENTATION_ENTRY
origin PR18 tip = IMPLEMENTATION_ENTRY
origin/main = 4444061dde0159a5edd62753fe3cef2d881a308c
merge-base =
4444061dde0159a5edd62753fe3cef2d881a308c
ahead/behind = 0 0
porcelain = empty
```

`git merge-base HEAD origin/main` must equal
`4444061dde0159a5edd62753fe3cef2d881a308c` verbatim. Executing the
command without comparing that printed SHA, or verifying only
`origin/main`, is not a pass. A different merge-base is an
immediate stop. Do not start test edits.

- [ ] **Step 3: Confirm the design digest**

```bash
/usr/bin/python3 - <<'PY'
from hashlib import sha256
from pathlib import Path
p = Path(
    "docs/superpowers/specs/"
    "2026-08-19-p3-compiler-alias-ci-repair-design.md"
)
digest = sha256(p.read_bytes()).hexdigest()
print(digest)
assert digest == (
    "853001ef80c48de4ce17c47439b58609c893180b5a2b97592ef8746c61899cdc"
)
PY
```

- [ ] **Step 4: Confirm the pre-edit test-file digest**

The future implementation entry must verify this hash before any
test edit. A mismatch is a stop. Do not start test edits.

```bash
/usr/bin/python3 - <<'PY'
from hashlib import sha256
from pathlib import Path
p = Path("tests/p3_v3/test_pilot_build.py")
digest = sha256(p.read_bytes()).hexdigest()
print(digest)
assert digest == (
    "3757f4289f0b0efdc4726a513b97fc56a402e708c5053d24ca48bd246283310e"
)
assert digest != (
    "c82d6413dd6fb1c6ac651e518da5e0524e5a415ef768ebe344e51543b728ce2a"
)
PY
```

The approved post-edit digest
`c82d6413dd6fb1c6ac651e518da5e0524e5a415ef768ebe344e51543b728ce2a`
must not already match. A premature match is a stop.

---

### Task 2: Record The Authoritative RED

**Files:** none. Read-only host-path inspection and optional named
pytest only.

- [ ] **Step 1: Record the local host realpaths**

```bash
/usr/bin/python3 - <<'PY'
import os
print(os.path.realpath("/usr/bin/c++"))
print(os.path.realpath("/usr/bin/g++"))
print(os.path.realpath("/usr/bin/c++") == os.path.realpath("/usr/bin/g++"))
PY
```

Record the printed paths. Do not treat local inequality as a
closed defect. Do not invent a local RED.

- [ ] **Step 2: Optionally run the current named test**

A local pre-edit PASS is allowed and expected on hosts where
`/usr/bin/c++` and `/usr/bin/g++` have different realpaths.

```bash
PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1 \
  tests/p3_v3/test_pilot_build.py::test_cmakecache_compiler_generator_root_drift
```

Keep the frozen GitHub signature as the RED:

```text
Failed: DID NOT RAISE EvidenceError
tests/p3_v3/test_pilot_build.py:1344
expected match = CMakeCache compiler differs
run = 32449925094
job = 96676383508
head = e62974af4f5e2cfbc65d98c3b2f028edce57d25c
```

Do not xfail, skip, or delete the test.

---

### Task 3: Replace Only The CMakeCache Oracle

**Files:**
- Modify: `tests/p3_v3/test_pilot_build.py`

**Interfaces:**
- Consumes: `_synthetic_build_evidence_tree`,
  `collect_baseline_build_evidence`
- Produces: a portable CMakeCache mismatch subcase whose whole-file
  SHA-256 is
  `c82d6413dd6fb1c6ac651e518da5e0524e5a415ef768ebe344e51543b728ce2a`

- [ ] **Step 1: Replace only the compiler subcase**

In `test_cmakecache_compiler_generator_root_drift`, replace the
host-coupled cache compiler assignment with this exact patch.
The patch is an executable assertion, not a second semantic
definition.

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

Keep the environment compiler as the fixture default. Keep the
`compile_commands` compiler as the fixture default. Only the
CMakeCache compiler may be `cache_other`. `cache_other` must live
under `tmp_path`. Do not invoke a real compiler.

Do not change the generator-drift or source-root-drift cases.
Do not rename the test function.
Do not modify `test_compile_commands_compiler_mismatch`.
Do not add an alias acceptance test.

---

### Task 4: Focused GREEN

**Files:** none

- [ ] **Step 1: Run the named residual test**

```bash
PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1 \
  tests/p3_v3/test_pilot_build.py::test_cmakecache_compiler_generator_root_drift
```

Expected: `1 passed`, exit 0.

If the command fails, record the first failure and stop. Do not
edit production or expand scope.

---

### Task 5: File-Level GREEN

**Files:** none

- [ ] **Step 1: Run the whole pilot_build file**

```bash
PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1 \
  tests/p3_v3/test_pilot_build.py
```

Expected on the Cursor Ubuntu VM: `75 passed`, exit 0.

If the count differs, record the new count and stop unless the
file is otherwise green and Sol already accepted a new
denominator. Any failure is a stop.

---

### Task 6: Root Gate

**Files:** none

- [ ] **Step 1: Reproduce the Actions pytest command**

```bash
PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1
```

Pull request 18 is an independent branch from `origin/main`. The
first failure may still be the known supplemental R2 path-scan
stop:

```text
tests/external_slice/test_check_supplemental_r2_admission.py::
test_positive_admission_check
ERROR: forbidden data or downstream path present
```

If that exact first failure appears, record it as an independent
blocker. Do not widen scope. Do not claim root green.

Any other first failure is a stop.

- [ ] **Step 2: Do not run SSOT or live builds**

Do not run `scripts/build_paper_numbers.py`.
Do not run CMake, ninja, make, a real compiler, or Boost.Math.

---

### Task 7: Scope, Commit, And Push

**Files:** only `tests/p3_v3/test_pilot_build.py`

**Interfaces:**
- Consumes: pre-edit SHA-256
  `3757f4289f0b0efdc4726a513b97fc56a402e708c5053d24ca48bd246283310e`
  approved post-edit SHA-256
  `c82d6413dd6fb1c6ac651e518da5e0524e5a415ef768ebe344e51543b728ce2a`
- Produces: one implementation commit whose test file matches the
  approved post-edit digest

`--name-only` is not sufficient proof of function-level scope.

- [ ] **Step 1: Prove the exact write set before commit**

After the Task 3 edit and before `git add` / `git commit`:

```bash
git status --porcelain
git diff --check
git diff -- tests/p3_v3/test_pilot_build.py
git diff --name-only
git diff --cached --name-only
git ls-files --others --exclude-standard

/usr/bin/python3 - <<'PY'
from hashlib import sha256
from pathlib import Path
digest = sha256(Path("tests/p3_v3/test_pilot_build.py").read_bytes()).hexdigest()
print(digest)
assert digest == (
    "c82d6413dd6fb1c6ac651e518da5e0524e5a415ef768ebe344e51543b728ce2a"
)
assert digest != (
    "3757f4289f0b0efdc4726a513b97fc56a402e708c5053d24ca48bd246283310e"
)
PY
```

Required before commit:

- whole-file SHA-256 equals
  `c82d6413dd6fb1c6ac651e518da5e0524e5a415ef768ebe344e51543b728ce2a`
- `git diff --check` is 0
- `git diff -- tests/p3_v3/test_pilot_build.py` contains only the
  approved CMakeCache compiler subcase replacement
- deletions contain only that subcase `/usr/bin/g++` oracle and
  the one-line `pytest.raises` form
- additions contain only the approved `cache_other`,
  `str(cache_other)`, and formatted `pytest.raises`
- generator and source-root subcases are unchanged
- `test_compile_commands_compiler_mismatch` is unchanged
- no other test function, import, helper, production, or
  workflow change
- the only path that may appear is
  `tests/p3_v3/test_pilot_build.py`

Any extra or missing change is a stop.

- [ ] **Step 2: Independent commit**

```bash
git add tests/p3_v3/test_pilot_build.py
git commit -m "test(p3-v3): make CMakeCache mismatch portable"
```

Do not amend, rebase, squash, or force-push.

- [ ] **Step 3: Re-read the committed file and history before push**

```bash
/usr/bin/python3 - <<'PY'
from hashlib import sha256
from subprocess import check_output

data = check_output(
    ["git", "show", "HEAD:tests/p3_v3/test_pilot_build.py"]
)
digest = sha256(data).hexdigest()
print(digest)
assert digest == (
    "c82d6413dd6fb1c6ac651e518da5e0524e5a415ef768ebe344e51543b728ce2a"
)
PY

git diff --check origin/main...HEAD
git diff --name-only origin/main...HEAD
git show --name-only --format= HEAD
```

The post-edit hash must be re-verified from `HEAD`, not from the
working tree alone. `origin/main...HEAD` may contain only:

```text
docs/superpowers/specs/2026-08-19-p3-compiler-alias-ci-repair-design.md
docs/superpowers/plans/2026-08-19-p3-compiler-alias-ci-repair.md
tests/p3_v3/test_pilot_build.py
```

The newest implementation commit may contain only the test file.

- [ ] **Step 4: Push the existing branch**

```bash
git push origin cursor/p3-compiler-alias-ci-repair-c46c
```

Do not create a second branch. Do not force-push.

---

### Task 8: Pull Request 18 Draft Stop

**Files:** none

- [ ] **Step 1: Update pull request 18 and keep it draft**

Push is already done in Task 7. Update the existing pull request
18 body to the residual CMakeCache implementation record. Keep
the pull request OPEN and draft.

The body must contain these exact headings:

```text
## Motivation
## Changes
## Tests
## SSOT integrity
## Governance
```

The implementation body must record:

- Motivation: pull request 28 authoritative RED, run
  `32449925094`, job `96676383508`, and
  `test_cmakecache_compiler_generator_root_drift`
- Changes: only the CMakeCache compiler oracle was replaced
- Tests: the real focused, 75-test file, and root-gate results
- If the root gate hits the known supplemental R2 blocker, the
  body must say blocked and must not say root green
- SSOT integrity: `scripts/build_paper_numbers.py` was not run
  and is not applicable to this test-only change
- Governance: OPEN draft; mark-ready, main merge,
  qualification, and claims remain unauthorized

Do not mark-ready. Do not merge. Do not edit pull request 28.
Do not edit pull request 19.

- [ ] **Step 2: Confirm remote sync, body, and the untouched combined PR**

```bash
git rev-parse HEAD
git rev-parse origin/cursor/p3-compiler-alias-ci-repair-c46c
git rev-list --left-right --count \
  HEAD...origin/cursor/p3-compiler-alias-ci-repair-c46c
git status --porcelain

gh pr view 18 \
  --repo meng004/P3-Semantic-Mutation \
  --json number,state,isDraft,baseRefName,headRefName,headRefOid,url,body

gh pr view 28 \
  --repo meng004/P3-Semantic-Mutation \
  --json state,isDraft,headRefOid,url
```

Required:

```text
HEAD = origin PR18 tip
ahead/behind = 0 0
PR #18:
state = OPEN
isDraft = true
baseRefName = main
headRefName = cursor/p3-compiler-alias-ci-repair-c46c
headRefOid = final HEAD
body contains ## Motivation, ## Changes, ## Tests,
## SSOT integrity, and ## Governance
PR #28: OPEN, draft,
        headRefOid=e62974af4f5e2cfbc65d98c3b2f028edce57d25c
```

Re-read the body and confirm each required section. Stop for Sol
implementation review. Do not write an implementation verdict.

---

## Non-Goals

This plan does not:

- change `.github/workflows` or skip `tests/p3_v3`
- xfail, skip, or delete the failing test
- change production `os.path.realpath` compares
- retouch the pull request 19 compile_commands repair
- add an extra symlink alias acceptance test
- resurrect the superseded compile_commands / extra alias /
  pull request 17 `1196 passed` scope
- change qualification, supplemental R2, PR 16, PR 17, PR 19, or
  PR 28
- run CMake, a real compiler, or Boost.Math
- treat plan archival as an executable implementation grant

## Governance Stop

```text
IMPLEMENTATION_AUTHORIZED=false
IMPLEMENTATION_EXECUTABLE=false
PR_READY_AUTHORIZED=false
MAIN_PR_MERGE_AUTHORIZED=false
MERGE_AUTHORIZED=false
```

Archiving this plan does not authorize implementation. A later
user node must still grant implementation and write
`IMPLEMENTATION_ENTRY` after Sol Spec plus Standards PASS.

Pull request 18 stays draft. Pull requests 19 and 28 stay
untouched. Merge stays unauthorized.

This archival node must not start Task 1 through Task 8.

## Self-Review Record

- Spec coverage: residual CMakeCache oracle, production realpath
  kept, one-function write set, merge-base gate, pre-edit and
  post-edit file hashes consumed by Task 1 and Task 7, PR 19 and
  PR 28 isolation, authoritative PR 28 RED, Task 8 body and
  `headRefOid = final HEAD`.
- Design remains the semantic SSOT; repeated tuples are
  executable assertions.
- Entry is fail-closed on an explicit Sol SHA, atomic
  destination fetch, and verbatim merge-base.
- Incomplete-marker scan: clean.
- Execution is not offered from this archival node.
