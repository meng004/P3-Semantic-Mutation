# PR #17 and PR #19 Combined CI Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:executing-plans only after Sol writes a 40-character
> `INTEGRATION_IMPLEMENTATION_ENTRY` and sets both
> `INTEGRATION_IMPLEMENTATION_AUTHORIZED` and
> `INTEGRATION_IMPLEMENTATION_EXECUTABLE` to true. This archival
> node forbids starting any Task.

**Goal:** Combine the complete histories of pull request 17 and pull
request 19 on an independent branch while keeping both provenances
and both draft source pull requests unchanged.

**Architecture:** Design choice A. Create a combination branch from
frozen `origin/main`. Non-fast-forward merge pull request 17 first,
then non-fast-forward merge pull request 19. Do not squash, rebase,
cherry-pick, or rewrite either repair.

**Tech Stack:** Git non-fast-forward merge, `/usr/bin/python3`,
pytest already present in the Cursor VM user site.

## Global Constraints

- Implement against
  `docs/superpowers/specs/2026-08-21-pr17-pr19-ci-integration-design.md`.
- Classification is `MUTUALLY_SHADOWED_INDEPENDENT_CI_REPAIRS`.
- Frozen `origin/main` is `4444061dde0159a5edd62753fe3cef2d881a308c`.
- Frozen pull request 17 head is
  `fb20947a102934415dd201665971a711ccc4e0d5`.
- Frozen pull request 19 head is
  `3352cedb5f377b60f0aec5ff80997b2057c7fc14`.
- Do not modify pull request 16, 17, 18, or 19.
- Do not mark any pull request ready and do not merge.
- Do not squash, rebase, cherry-pick, or force-push.
- Do not edit production code or tests by hand.
- Use `/usr/bin/python3` only. Do not use `rtk`.
- Do not install, upgrade, or delete dependencies.
- Do not create or modify a venv or pip-target.
- Do not run a real compiler, CMake, ninja, make, Boost.Math, or
  `scripts/build_paper_numbers.py`.
- `INTEGRATION_IMPLEMENTATION_AUTHORIZED=false`
- `INTEGRATION_IMPLEMENTATION_EXECUTABLE=false`
- `MERGE_AUTHORIZED=false`
- `INTEGRATION_IMPLEMENTATION_ENTRY` must be the full 40-character
  SHA Sol writes in a later implementation instruction after PASS.
  If it is omitted, stop. Do not derive it from origin tip, branch,
  merge-base, pull request head, or clock time.

---

## File Structure

Later implementation may introduce only the union of the two source
pull requests:

```text
docs/superpowers/plans/2026-08-19-supplemental-r2-path-scan-ci-repair.md
docs/superpowers/specs/2026-08-19-supplemental-r2-path-scan-ci-repair-design.md
docs/superpowers/plans/2026-08-19-p3-compiler-alias-ci-test-repair.md
docs/superpowers/specs/2026-08-19-p3-compiler-alias-ci-test-repair-design.md
scripts/external_slice/check_supplemental_r2_admission.py
scripts/external_slice/check_supplemental_r2_handoff_hashes.py
scripts/external_slice/mine_supplemental_r2.py
tests/external_slice/test_check_supplemental_r2_admission.py
tests/p3_v3/test_pilot_build.py
```

This governance branch may additionally contain the two integration
documents created by the archival node. Those files are not an
implementation write-set grant.

Do not create helper modules. Do not edit workflows.

## Frozen Replay Evidence

| Item | Value |
|---|---|
| Collected | 1693 |
| Passed | 1693 |
| Failed | 0 |
| Warnings | 10 |
| Duration | 1429.77 seconds |
| external_slice focused | 176 passed |
| compiler-alias focused | 1 passed |
| `test_pilot_build.py` | 75 passed |

Duration need not be reproduced. Collection count must match 1693
or be explained and stopped for Sol review if any test fails.

---

### Task 1: Confirm Integration Implementation Entry

**Files:** read only

- [ ] **Step 1: Refuse without an explicit Sol entry**

Stop unless the later node writes `INTEGRATION_IMPLEMENTATION_ENTRY`
as a full 40-character SHA and sets both authorized and executable
flags to true. Plan archival is not that grant.

- [ ] **Step 2: Confirm the executable flags**

Required later-node values:

```text
INTEGRATION_IMPLEMENTATION_AUTHORIZED=true
INTEGRATION_IMPLEMENTATION_EXECUTABLE=true
```

If either flag is false or missing, stop.

---

### Task 2: Verify The Three Frozen SHAs

**Files:** read only

- [ ] **Step 1: Fetch and print the frozen identities**

```bash
export GIT_CONFIG_GLOBAL=/dev/null
export GIT_CONFIG_NOSYSTEM=1
export GIT_CONFIG_COUNT=0

git status --porcelain
git fetch origin \
  main \
  cursor/supplemental-r2-path-scan-ci-repair-c46c \
  cursor/p3-compiler-alias-ci-test-repair-c46c

git rev-parse origin/main
git rev-parse origin/cursor/supplemental-r2-path-scan-ci-repair-c46c
git rev-parse origin/cursor/p3-compiler-alias-ci-test-repair-c46c
```

Required:

```text
origin/main = 4444061dde0159a5edd62753fe3cef2d881a308c
PR #17 head = fb20947a102934415dd201665971a711ccc4e0d5
PR #19 head = 3352cedb5f377b60f0aec5ff80997b2057c7fc14
porcelain = empty
```

If any SHA differs or the worktree is dirty, stop. Do not reset,
rebase, clean, or guess a new entry.

---

### Task 3: Create Or Enter The Combination Branch

**Files:** none yet

- [ ] **Step 1: Start from frozen main**

```bash
git switch -c <later-combination-branch> \
  4444061dde0159a5edd62753fe3cef2d881a308c
```

The later Sol instruction names the combination branch. Do not reuse
`cursor/pr17-pr19-ci-integration-c46c` unless that later instruction
explicitly names it as the implementation branch.

- [ ] **Step 2: Confirm HEAD and merge-base**

```bash
git rev-parse HEAD
git merge-base HEAD origin/main
git status --porcelain
```

Required:

```text
HEAD = 4444061dde0159a5edd62753fe3cef2d881a308c
merge-base = 4444061dde0159a5edd62753fe3cef2d881a308c
porcelain = empty
```

---

### Task 4: Merge Pull Request 17 History

**Files:** introduced only by the merge

- [ ] **Step 1: Non-fast-forward merge pull request 17**

```bash
git merge --no-ff \
  origin/cursor/supplemental-r2-path-scan-ci-repair-c46c \
  -m "merge: integrate supplemental R2 path-scan repair"
```

Do not use `--ff-only`, `--squash`, cherry-pick, or rebase.

If Git reports a conflict, stop and return the conflict list. Do not
resolve by rewriting the repair.

---

### Task 5: Verify The First Merge

**Files:** read only after the merge

- [ ] **Step 1: Confirm ancestry and first-wave files**

```bash
git merge-base --is-ancestor \
  fb20947a102934415dd201665971a711ccc4e0d5 HEAD
echo "PR17_ANCESTOR_EXIT=$?"

git log --oneline \
  4444061dde0159a5edd62753fe3cef2d881a308c..HEAD
git diff --name-only \
  4444061dde0159a5edd62753fe3cef2d881a308c...HEAD
```

Required: `PR17_ANCESTOR_EXIT=0`. The first-wave names must be a
subset of:

```text
docs/superpowers/plans/2026-08-19-supplemental-r2-path-scan-ci-repair.md
docs/superpowers/specs/2026-08-19-supplemental-r2-path-scan-ci-repair-design.md
scripts/external_slice/check_supplemental_r2_admission.py
scripts/external_slice/check_supplemental_r2_handoff_hashes.py
scripts/external_slice/mine_supplemental_r2.py
tests/external_slice/test_check_supplemental_r2_admission.py
```

---

### Task 6: Merge Pull Request 19 History

**Files:** introduced only by the merge

- [ ] **Step 1: Non-fast-forward merge pull request 19**

```bash
git merge --no-ff \
  origin/cursor/p3-compiler-alias-ci-test-repair-c46c \
  -m "merge: integrate compiler-alias CI test repair"
```

Do not use `--ff-only`, `--squash`, cherry-pick, or rebase.

If Git reports a conflict, stop and return the conflict list. Do not
resolve by rewriting the repair.

---

### Task 7: Verify The Second Merge

**Files:** read only after the merge

- [ ] **Step 1: Confirm both ancestries**

```bash
git merge-base --is-ancestor \
  fb20947a102934415dd201665971a711ccc4e0d5 HEAD
echo "PR17_ANCESTOR_EXIT=$?"

git merge-base --is-ancestor \
  3352cedb5f377b60f0aec5ff80997b2057c7fc14 HEAD
echo "PR19_ANCESTOR_EXIT=$?"

git log --oneline --graph --decorate \
  4444061dde0159a5edd62753fe3cef2d881a308c..HEAD
```

Required: both ancestor exits are 0. The graph must show two
non-fast-forward merge commits, not a rewritten linear history.

---

### Task 8: Verify The Combined Diff

**Files:** the union listed in File Structure

- [ ] **Step 1: Name-only and whitespace check**

```bash
git diff --check \
  4444061dde0159a5edd62753fe3cef2d881a308c...HEAD
git diff --name-only \
  4444061dde0159a5edd62753fe3cef2d881a308c...HEAD
git status --porcelain
```

The name list must equal the nine-path union in File Structure. Any
extra path is a stop. Porcelain must be empty.

---

### Task 9: Run Pull Request 17 Focused Tests

**Files:** none

- [ ] **Step 1: Run the supplemental R2 admission file**

```bash
PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1 \
  tests/external_slice/test_check_supplemental_r2_admission.py
```

Expected: 176 passed, exit 0.

If the command fails, record the first failure and stop. Do not
edit tests.

---

### Task 10: Run Pull Request 19 Focused Test

**Files:** none

- [ ] **Step 1: Run the named compiler-mismatch test**

```bash
PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1 \
  tests/p3_v3/test_pilot_build.py::test_compile_commands_compiler_mismatch
```

Expected: 1 collected, 1 passed, exit 0.

If the command fails, record the full failure and stop. Do not edit
tests.

---

### Task 11: Run The Pilot Build File

**Files:** none

- [ ] **Step 1: Run the whole file**

```bash
PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1 \
  tests/p3_v3/test_pilot_build.py
```

Expected: 75 passed, exit 0.

If the command fails, record the first failure and stop. Do not
edit tests.

---

### Task 12: Run The Root Suite

**Files:** none

- [ ] **Step 1: Run the Actions pytest command**

```bash
PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1
```

Expected reference: 1693 passed, 0 failed, 10 warnings.

Record collected, passed, failed, warnings, duration, and exit
code. If collected is not 1693, explain the new count and stop for
Sol review unless the suite is otherwise green and Sol already
accepted a new denominator. Any failure is a stop.

Do not interpret a green root suite as merge authorization.

---

### Task 13: Recheck Diff, Topology, And Worktree

**Files:** read only

- [ ] **Step 1: Repeat the scope and ancestry checks**

```bash
git diff --check \
  4444061dde0159a5edd62753fe3cef2d881a308c...HEAD
git diff --name-only \
  4444061dde0159a5edd62753fe3cef2d881a308c...HEAD
git merge-base --is-ancestor \
  fb20947a102934415dd201665971a711ccc4e0d5 HEAD
git merge-base --is-ancestor \
  3352cedb5f377b60f0aec5ff80997b2057c7fc14 HEAD
git status --porcelain
```

Required: the nine-path union, both ancestries present, porcelain
empty, no extra tracked edits from tests.

---

### Task 14: Push The Combination Branch

**Files:** none

- [ ] **Step 1: Push the later combination branch**

```bash
git push -u origin <later-combination-branch>
```

Do not force-push. Before push, confirm the later instruction named
that branch. After push, require ahead/behind `0 0` against the
origin combination branch.

---

### Task 15: Create Or Update The Independent Draft Pull Request

**Files:** none

- [ ] **Step 1: Keep the combination pull request draft**

Create a new draft pull request against `main` if none exists for
that head. If one exists, update it only when the later instruction
allows, and keep `isDraft=true`.

Do not mark it ready. Do not merge. Passing tests do not change
those rules.

---

### Task 16: Read-Only Confirmation Of Source Pull Requests

**Files:** none

- [ ] **Step 1: View pull requests 17 and 19 without editing**

```bash
gh pr view 17 \
  --repo meng004/P3-Semantic-Mutation \
  --json state,isDraft,headRefOid,url

gh pr view 19 \
  --repo meng004/P3-Semantic-Mutation \
  --json state,isDraft,headRefOid,url
```

Expected unless Sol records a later drift:

```text
PR #17: OPEN, draft, head fb20947a102934415dd201665971a711ccc4e0d5
PR #19: OPEN, draft, head 3352cedb5f377b60f0aec5ff80997b2057c7fc14
```

If either value differs, record the actual value. Do not correct
those pull requests from the combination node.

---

### Task 17: Stop For Sol Implementation Review

**Files:** none

- [ ] **Step 1: Leave the combination pull request draft**

Stop after the draft combination pull request exists and the source
pull requests are unchanged. Do not write an implementation verdict.
Do not upgrade claims. Do not start attempt-2. Do not mark ready.
Do not merge.

---

## Non-Goals

This plan does not:

- change production realpath compares
- rewrite the supplemental R2 path scan
- monkeypatch `os.path.realpath`
- change the workflow, skip, or xfail
- modify pull request 16, 17, 18, or 19
- treat plan archival as an executable grant

## Governance Stop

```text
INTEGRATION_IMPLEMENTATION_AUTHORIZED=false
INTEGRATION_IMPLEMENTATION_EXECUTABLE=false
MERGE_AUTHORIZED=false
```

A later user node must still write `INTEGRATION_IMPLEMENTATION_ENTRY`
after Sol Spec plus Standards PASS. The combination pull request
stays draft.

## Self-Review Record

- Spec coverage: independent combination branch, PR 17 then PR 19
  `--no-ff` merges, nine-path union, four pytest gates, frozen 1693
  replay, rejected force-merge and retarget designs, fail-closed
  entry, source pull requests left unchanged.
- Placeholder scan: clean.
- Execution is not offered from this archival node.
