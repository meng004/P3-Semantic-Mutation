# PR #17 and PR #19 Combined CI Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:executing-plans only after Sol writes a 40-character
> `INTEGRATION_IMPLEMENTATION_ENTRY` and sets
> `INTEGRATION_IMPLEMENTATION_AUTHORIZED`,
> `INTEGRATION_IMPLEMENTATION_EXECUTABLE`, and
> `LOCAL_HISTORY_INTEGRATION_AUTHORIZED` to true. This archival
> node forbids starting any Task.

**Goal:** Integrate the complete histories of pull request 17 and
pull request 19 onto the existing draft pull request 28 branch
while keeping both provenances and both source pull requests
unchanged.

**Architecture:** Design choice A. Reuse
`cursor/pr17-pr19-ci-integration-c46c` and pull request 28.
Non-fast-forward merge pull request 17 first, then
non-fast-forward merge pull request 19. Do not squash, rebase,
cherry-pick, rewrite either repair, or create a second combination
branch or pull request.

**Tech Stack:** Git non-fast-forward merge, `/usr/bin/python3`,
pytest already present in the Cursor VM user site.

```text
The design document is the semantic SSOT.
Repeated SHAs, path sets, results, and flags in this plan are
executable fail-closed assertions. Any mismatch is a stop.
```

The current reviewed governance tip at the start of this
remediation is `92516bb27687f172db95a36ae75a91d07d247034`. A later
`INTEGRATION_IMPLEMENTATION_ENTRY` is the exact Sol-written SHA of
the reviewed tip of `cursor/pr17-pr19-ci-integration-c46c`
immediately before the two local history merges.

## Global Constraints

- Implement against
  `docs/superpowers/specs/2026-08-21-pr17-pr19-ci-integration-design.md`.
- Classification is `MUTUALLY_SHADOWED_INDEPENDENT_CI_REPAIRS`.
- Frozen `origin/main` is `4444061dde0159a5edd62753fe3cef2d881a308c`.
- Frozen pull request 17 head is
  `fb20947a102934415dd201665971a711ccc4e0d5`.
- Frozen pull request 19 head is
  `3352cedb5f377b60f0aec5ff80997b2057c7fc14`.
- Implementation branch is
  `cursor/pr17-pr19-ci-integration-c46c`.
- Implementation pull request is 28.
- Do not modify pull request 16, 17, 18, or 19.
- Do not mark any pull request ready.
- Do not merge any pull request into main.
- Do not run `gh pr merge`.
- `MAIN_PR_MERGE_AUTHORIZED=false`.
- `MERGE_AUTHORIZED=false` is an alias for main-PR merge only.
- The two local `git merge --no-ff` operations are permitted only
  when:
  `INTEGRATION_IMPLEMENTATION_AUTHORIZED=true`
  `INTEGRATION_IMPLEMENTATION_EXECUTABLE=true`
  `LOCAL_HISTORY_INTEGRATION_AUTHORIZED=true`.
- In this archival state those three flags remain false.
- Do not squash, rebase, cherry-pick, or force-push.
- Do not edit production code or tests by hand.
- Use `/usr/bin/python3` only. Do not use `rtk`.
- Do not install, upgrade, or delete dependencies.
- Do not create or modify a venv or pip-target.
- Do not run a real compiler, CMake, ninja, make, Boost.Math, or
  `scripts/build_paper_numbers.py`.
- `INTEGRATION_IMPLEMENTATION_ENTRY` must be the full 40-character
  SHA Sol writes in a later implementation instruction after PASS.
  If it is omitted, stop. Do not derive it from origin tip, branch,
  merge-base, pull request `headRefOid`, or clock time.

---

## File Structure

After the first local history merge, `origin/main...HEAD` must
contain exactly these 8 paths:

```text
docs/superpowers/specs/2026-08-21-pr17-pr19-ci-integration-design.md
docs/superpowers/plans/2026-08-21-pr17-pr19-ci-integration.md
docs/superpowers/plans/2026-08-19-supplemental-r2-path-scan-ci-repair.md
docs/superpowers/specs/2026-08-19-supplemental-r2-path-scan-ci-repair-design.md
scripts/external_slice/check_supplemental_r2_admission.py
scripts/external_slice/check_supplemental_r2_handoff_hashes.py
scripts/external_slice/mine_supplemental_r2.py
tests/external_slice/test_check_supplemental_r2_admission.py
```

After the second local history merge, `origin/main...HEAD` must
contain exactly these 11 paths:

```text
docs/superpowers/specs/2026-08-21-pr17-pr19-ci-integration-design.md
docs/superpowers/plans/2026-08-21-pr17-pr19-ci-integration.md
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

### Task 1: Confirm Explicit Authorization Values

**Files:** read only

Task 1 checks only whether Sol wrote the required grants. It must
not treat a pre-fetch remote-tracking ref as the authoritative
entry. A pre-fetch `rev-parse origin/...` result is diagnostic
only and is never a pass condition.

- [ ] **Step 1: Refuse without an explicit Sol entry and flags**

Stop unless the later node writes all of the following:

```text
INTEGRATION_IMPLEMENTATION_ENTRY is a Sol-written 40-character SHA.
INTEGRATION_IMPLEMENTATION_AUTHORIZED must be true.
INTEGRATION_IMPLEMENTATION_EXECUTABLE must be true.
LOCAL_HISTORY_INTEGRATION_AUTHORIZED must be true.
```

Plan archival is not that grant. The current reviewed governance
tip `92516bb27687f172db95a36ae75a91d07d247034` is not that later
entry unless Sol writes that exact SHA. Do not fetch. Do not
compare `HEAD` or `origin/cursor/pr17-pr19-ci-integration-c46c`
here. Task 2 is the only authoritative entry and ref gate.

---

### Task 2: Post-Fetch Entry And Frozen Ref Gate

**Files:** read only

This task is the only authoritative entry and ref gate. The
sequence is fixed: inspect porcelain, fetch, switch onto the
existing branch, then compare every required SHA.

- [ ] **Step 1: Fetch, then compare the live checkout to the Sol entry**

```bash
export GIT_CONFIG_GLOBAL=/dev/null
export GIT_CONFIG_NOSYSTEM=1
export GIT_CONFIG_COUNT=0

git status --porcelain

git fetch --atomic origin \
  +refs/heads/main:refs/remotes/origin/main \
  +refs/heads/cursor/pr17-pr19-ci-integration-c46c:refs/remotes/origin/cursor/pr17-pr19-ci-integration-c46c \
  +refs/heads/cursor/supplemental-r2-path-scan-ci-repair-c46c:refs/remotes/origin/cursor/supplemental-r2-path-scan-ci-repair-c46c \
  +refs/heads/cursor/p3-compiler-alias-ci-test-repair-c46c:refs/remotes/origin/cursor/p3-compiler-alias-ci-test-repair-c46c

git switch cursor/pr17-pr19-ci-integration-c46c

git rev-parse --abbrev-ref HEAD
git rev-parse HEAD
git rev-parse origin/cursor/pr17-pr19-ci-integration-c46c
git rev-parse origin/main
git rev-parse origin/cursor/supplemental-r2-path-scan-ci-repair-c46c
git rev-parse origin/cursor/p3-compiler-alias-ci-test-repair-c46c
git merge-base HEAD origin/main
git rev-list --left-right --count \
  HEAD...origin/cursor/pr17-pr19-ci-integration-c46c
git status --porcelain
```

After fetch, every line must hold:

```text
branch = cursor/pr17-pr19-ci-integration-c46c
HEAD = INTEGRATION_IMPLEMENTATION_ENTRY
origin integration tip = INTEGRATION_IMPLEMENTATION_ENTRY
origin/main = 4444061dde0159a5edd62753fe3cef2d881a308c
PR #17 head = fb20947a102934415dd201665971a711ccc4e0d5
PR #19 head = 3352cedb5f377b60f0aec5ff80997b2057c7fc14
merge-base = 4444061dde0159a5edd62753fe3cef2d881a308c
ahead/behind = 0 0
porcelain = empty
```

```text
No local history merge may run unless this post-fetch gate passed.
A pre-fetch remote-tracking ref is never authoritative.
Each command-line refspec has an explicit refs/remotes/origin/*
destination. The fetch is atomic: either all four remote-tracking
refs update, or none do.
FETCH_HEAD alone is not an authoritative gate.
The authoritative values are the four explicitly updated
refs/remotes/origin/* destinations read after the atomic fetch.
```

Do not use a source-only command-line refspec such as
`git fetch origin main`. Do not rely on an unverified
`remote.origin.fetch` mapping. If any value differs, stop. Do not
reset, rebase, clean, or guess a new entry. Do not fetch again
after this snapshot unless a later task explicitly commands it.
Task 2's fetch snapshot is the authoritative remote snapshot for
the rest of this node.

---

### Task 3: Hold The Existing Combination Branch

**Files:** none

- [ ] **Step 1: Reaffirm the Task 2 post-fetch gate**

Do not create a branch. Do not switch to another branch. Do not
fetch. Task 2 already placed the checkout on
`cursor/pr17-pr19-ci-integration-c46c` after fetch.

Confirm the Task 2 post-fetch gate passed. Then confirm, without
fetching:

```bash
git rev-parse --abbrev-ref HEAD
git rev-parse HEAD
git status --porcelain
```

Required:

```text
branch = cursor/pr17-pr19-ci-integration-c46c
HEAD = INTEGRATION_IMPLEMENTATION_ENTRY
porcelain = empty
```

`HEAD` must still be the Sol-written
`INTEGRATION_IMPLEMENTATION_ENTRY`. It must not be
`4444061dde0159a5edd62753fe3cef2d881a308c`.

---

### Task 4: Merge Pull Request 17 History

**Files:** introduced only by the merge

- [ ] **Step 1: Re-assert the three local-history flags**

Stop unless all three are true:

```text
INTEGRATION_IMPLEMENTATION_AUTHORIZED=true
INTEGRATION_IMPLEMENTATION_EXECUTABLE=true
LOCAL_HISTORY_INTEGRATION_AUTHORIZED=true
```

- [ ] **Step 2: Reconfirm the post-fetch entry gate without fetching**

Immediately before the first `git merge --no-ff`, and without
fetching again:

```bash
git rev-parse HEAD
git rev-parse origin/cursor/pr17-pr19-ci-integration-c46c
git rev-list --left-right --count \
  HEAD...origin/cursor/pr17-pr19-ci-integration-c46c
git status --porcelain
```

Required:

```text
HEAD = INTEGRATION_IMPLEMENTATION_ENTRY
origin integration tip = INTEGRATION_IMPLEMENTATION_ENTRY
ahead/behind = 0 0
porcelain = empty
```

Task 2's fetch snapshot remains the authoritative remote snapshot.
If this reconfirm fails, stop. Do not merge.

- [ ] **Step 3: Non-fast-forward merge pull request 17**

```bash
git merge --no-ff \
  origin/cursor/supplemental-r2-path-scan-ci-repair-c46c \
  -m "merge: integrate supplemental R2 path-scan repair"
```

This command constructs commit topology on
`cursor/pr17-pr19-ci-integration-c46c` only. It does not merge any
pull request into `main`, does not equal `gh pr merge`, and does
not change the head or draft state of pull request 17 or 19.

Do not use `--ff-only`, `--squash`, cherry-pick, or rebase.

If Git reports a conflict, stop and return the conflict list. Do not
resolve by rewriting the repair.

---

### Task 5: Verify The First Merge

**Files:** read only after the merge

- [ ] **Step 1: Confirm ancestry and the exact 8-path set**

```bash
git merge-base --is-ancestor \
  fb20947a102934415dd201665971a711ccc4e0d5 HEAD
echo "PR17_ANCESTOR_EXIT=$?"

git log --oneline \
  4444061dde0159a5edd62753fe3cef2d881a308c..HEAD
git diff --name-only \
  4444061dde0159a5edd62753fe3cef2d881a308c...HEAD
```

Required: `PR17_ANCESTOR_EXIT=0`. The names must equal exactly:

```text
docs/superpowers/specs/2026-08-21-pr17-pr19-ci-integration-design.md
docs/superpowers/plans/2026-08-21-pr17-pr19-ci-integration.md
docs/superpowers/plans/2026-08-19-supplemental-r2-path-scan-ci-repair.md
docs/superpowers/specs/2026-08-19-supplemental-r2-path-scan-ci-repair-design.md
scripts/external_slice/check_supplemental_r2_admission.py
scripts/external_slice/check_supplemental_r2_handoff_hashes.py
scripts/external_slice/mine_supplemental_r2.py
tests/external_slice/test_check_supplemental_r2_admission.py
```

Any missing or extra path is a stop.

---

### Task 6: Merge Pull Request 19 History

**Files:** introduced only by the merge

- [ ] **Step 1: Re-assert the three local-history flags**

Stop unless all three are true:

```text
INTEGRATION_IMPLEMENTATION_AUTHORIZED=true
INTEGRATION_IMPLEMENTATION_EXECUTABLE=true
LOCAL_HISTORY_INTEGRATION_AUTHORIZED=true
```

- [ ] **Step 2: Non-fast-forward merge pull request 19**

```bash
git merge --no-ff \
  origin/cursor/p3-compiler-alias-ci-test-repair-c46c \
  -m "merge: integrate compiler-alias CI test repair"
```

This command constructs commit topology on
`cursor/pr17-pr19-ci-integration-c46c` only. It does not merge any
pull request into `main`, does not equal `gh pr merge`, and does
not change the head or draft state of pull request 17 or 19.

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

**Files:** the exact 11-path set

- [ ] **Step 1: Name-only and whitespace check**

```bash
git diff --check \
  4444061dde0159a5edd62753fe3cef2d881a308c...HEAD
git diff --name-only \
  4444061dde0159a5edd62753fe3cef2d881a308c...HEAD
git status --porcelain
```

The names must equal exactly:

```text
docs/superpowers/specs/2026-08-21-pr17-pr19-ci-integration-design.md
docs/superpowers/plans/2026-08-21-pr17-pr19-ci-integration.md
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

Any extra or missing path is a stop. Porcelain must be empty.

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

Do not interpret a green root suite as `MAIN_PR_MERGE_AUTHORIZED`
or `MERGE_AUTHORIZED`.

---

### Task 13: Recheck Diff, Topology, And Worktree

**Files:** read only

- [ ] **Step 1: Repeat the 11-path and ancestry checks**

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

Required: the exact 11-path set, both ancestries present, porcelain
empty, no extra tracked edits from tests.

---

### Task 14: Push The Existing Combination Branch

**Files:** none

- [ ] **Step 1: Push the frozen implementation branch**

```bash
git push origin cursor/pr17-pr19-ci-integration-c46c
```

Do not create, rename, or force-push another combination branch.

- [ ] **Step 2: Confirm the origin tip**

```bash
git rev-parse HEAD
git rev-parse origin/cursor/pr17-pr19-ci-integration-c46c
git rev-list --left-right --count \
  HEAD...origin/cursor/pr17-pr19-ci-integration-c46c
```

Required:

```text
HEAD = origin branch HEAD
ahead/behind = 0 0
```

---

### Task 15: Update And Verify Pull Request 28

**Files:** none

- [ ] **Step 1: Update the existing draft, do not create a new PR**

Keep pull request 28 OPEN and draft. Update its description so the
body contains at least:

- Motivation: two mutually shadowed independent CI repairs;
- Changes: complete histories of pull request 17 and pull request
  19, with no hand rewrite;
- Tests: 176 passed, 1 passed, 75 passed, and root 1693 passed;
- SSOT: `scripts/build_paper_numbers.py` was not run and its
  related files were not modified;
- Governance: pull request 28 stays draft; ready and main-PR merge
  remain unauthorized;
- Source PRs: pull request 17 and pull request 19 were not
  modified.

Do not mark it ready. Do not run `gh pr merge`. Passing tests do
not change those rules.

- [ ] **Step 2: Verify pull request 28 fields**

```bash
gh pr view 28 \
  --repo meng004/P3-Semantic-Mutation \
  --json number,state,isDraft,baseRefName,headRefName,headRefOid,body,url
```

Required:

```text
number = 28
state = OPEN
isDraft = true
baseRefName = main
headRefName = cursor/pr17-pr19-ci-integration-c46c
headRefOid = final implementation HEAD
```

The body must contain motivation, changes, the four test results,
SSOT, and governance state. If any field differs, stop and record
the actual value. Do not create a second pull request.

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

- [ ] **Step 1: Leave pull request 28 draft and stop**

Stop after pull request 28 remains draft, its `headRefOid` is the
final implementation HEAD, and pull requests 17 and 19 are
unchanged. Do not write an implementation verdict. Do not upgrade
claims. Do not start attempt-2. Do not mark ready. Do not merge
into `main`.

Required stop flags:

```text
LOCAL_HISTORY_INTEGRATION_COMPLETE=true
INTEGRATION_IMPLEMENTATION_REVIEWED=false
PR_READY_AUTHORIZED=false
MAIN_PR_MERGE_AUTHORIZED=false
MERGE_AUTHORIZED=false
```

---

## Stop Conditions

A later implementation node must stop immediately when:

- the post-fetch integration origin tip does not equal
  `INTEGRATION_IMPLEMENTATION_ENTRY`;
- the post-fetch ahead/behind count is not `0 0`;
- a fetch runs after Task 2 without an explicit later-task command;
- the first local history merge begins without reconfirming the
  entry gate in Task 4 Step 2;
- Sol has not written `INTEGRATION_IMPLEMENTATION_ENTRY` as a full
  40-character SHA;
- any of `INTEGRATION_IMPLEMENTATION_AUTHORIZED`,
  `INTEGRATION_IMPLEMENTATION_EXECUTABLE`, or
  `LOCAL_HISTORY_INTEGRATION_AUTHORIZED` is not true;
- `origin/main`, pull request 17, or pull request 19 no longer match
  the frozen SHAs;
- a merge conflict appears;
- the first-merge diff is not the exact 8-path set;
- the final diff is not the exact 11-path set;
- any required pytest command fails;
- the atomic fetch fails;
- any explicit destination ref is not updated;
- Task 2 uses a source-only command-line refspec;
- the gate relies only on FETCH_HEAD.

Do not derive a replacement entry. Do not treat a pre-fetch
remote-tracking ref as authoritative.

## Non-Goals

This plan does not:

- change production realpath compares
- rewrite the supplemental R2 path scan
- monkeypatch `os.path.realpath`
- change the workflow, skip, or xfail
- modify pull request 16, 17, 18, or 19
- create a second combination branch or pull request
- merge any pull request into `main`
- treat plan archival as an executable grant

## Governance Stop

```text
INTEGRATION_IMPLEMENTATION_AUTHORIZED=false
INTEGRATION_IMPLEMENTATION_EXECUTABLE=false
LOCAL_HISTORY_INTEGRATION_AUTHORIZED=false
MAIN_PR_MERGE_AUTHORIZED=false
PR_READY_AUTHORIZED=false
MERGE_AUTHORIZED=false
```

A later user node must still write `INTEGRATION_IMPLEMENTATION_ENTRY`
after Sol Spec plus Standards PASS. Pull request 28 stays draft.

## Self-Review Record

- Spec coverage: reuse of
  `cursor/pr17-pr19-ci-integration-c46c` and pull request 28,
  local-history versus main-PR authority split, exact 8-path then
  11-path sets, fail-closed Sol entry compare, four pytest gates,
  pull request 28 `baseRefName` / `headRefName` / `headRefOid`
  verification, source pull requests left unchanged.
- Entry ordering: fetch first, then compare branch, HEAD, integration
  origin tip, source refs, merge-base, ahead/behind, and porcelain.
- Fetch destinations: all four command-line refspecs explicitly map
  refs/heads/* to refs/remotes/origin/*, and --atomic prevents a
  partial remote-tracking snapshot.
- Placeholder scan: clean.
- Execution is not offered from this archival node.
