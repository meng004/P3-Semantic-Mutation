# Residual CMakeCache Third-History Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:executing-plans only after Sol writes a 40-character
> `INTEGRATION_IMPLEMENTATION_ENTRY` and sets
> `INTEGRATION_IMPLEMENTATION_AUTHORIZED`,
> `INTEGRATION_IMPLEMENTATION_EXECUTABLE`, and
> `LOCAL_HISTORY_INTEGRATION_AUTHORIZED` to true. This archival
> node forbids starting any Task.

**Goal:** Add the complete history of pull request 18 onto the
existing draft pull request 28 branch without rewriting pull
request 17 or 19.

**Architecture:** Design choice A.
`EXTEND_EXISTING_INTEGRATION_WITH_COMPLETE_PR18_HISTORY`. Reuse
`cursor/pr17-pr19-ci-integration-c46c` and pull request 28. Run
exactly one later `--no-ff` merge of
`origin/cursor/p3-compiler-alias-ci-repair-c46c`. Do not
cherry-pick, copy, squash, rebase, or create a second combination
branch or pull request.

**Tech Stack:** Git non-fast-forward merge, `/usr/bin/python3`,
pytest already present in the Cursor VM user site.

The design file identified by SHA-256
`8ad616cb43204f630e0397f99c68ec4c8a69add28111bef83b3fab50bc13f6b4`
is the semantic SSOT for design choice A and the frozen history
values. This plan repeats only frozen values, exact commands,
and fail-closed assertions that a later executor must consume.
Those repeated items are executable assertions, not a second
semantic definition. This authorized revision is the procedure
for final-head integration evidence. If this plan conflicts
with the design on topology or frozen history values, the
executor must stop and return the conflict to Sol.

## Global Constraints

- Implement against
  `docs/superpowers/specs/2026-08-21-pr17-pr19-ci-integration-design.md`
  with SHA-256
  `8ad616cb43204f630e0397f99c68ec4c8a69add28111bef83b3fab50bc13f6b4`.
- Classification is
  `RESIDUAL_CMAKECACHE_THIRD_HISTORY_INTEGRATION`.
- Frozen `origin/main` is `4444061dde0159a5edd62753fe3cef2d881a308c`.
- Frozen pull request 17 head is
  `fb20947a102934415dd201665971a711ccc4e0d5`.
- Frozen pull request 19 head is
  `3352cedb5f377b60f0aec5ff80997b2057c7fc14`.
- Frozen pull request 18 head is
  `4b21072add365923799dccc057d4fefffd69918c`.
- Implementation branch is
  `cursor/pr17-pr19-ci-integration-c46c`.
- Implementation pull request is 28.
- Current pull request 28 `test_pilot_build.py` SHA-256 is
  `3278fbce1d0c017d219f450cea76eeb2c962f8d8bdca6b71fc9afad2fb5a0dd6`.
- Approved combined `test_pilot_build.py` SHA-256 is
  `b1af86f556614b28cd41a204255c47a7c0e4b27cd4812c9cd6491b0c3c824e90`.
- Do not modify pull request 16, 17, 18, or 19.
- Do not mark any pull request ready.
- Do not merge any pull request into main.
- Do not run `gh pr merge`.
- `MAIN_PR_MERGE_AUTHORIZED=false`.
- `MERGE_AUTHORIZED=false` is an alias for main-PR merge only.
- The one remaining local `git merge --no-ff` is permitted only
  when:
  `INTEGRATION_IMPLEMENTATION_AUTHORIZED=true`
  `INTEGRATION_IMPLEMENTATION_EXECUTABLE=true`
  `LOCAL_HISTORY_INTEGRATION_AUTHORIZED=true`.
- In this archival state those three flags remain false.
- Do not squash, rebase, cherry-pick, or force-push.
- Do not edit production code or tests by hand.
- Use `/usr/bin/python3` only. Do not use `rtk`.
- Do not install, upgrade, or delete dependencies.
- Do not run a real compiler, CMake, ninja, make, Boost.Math, or
  `scripts/build_paper_numbers.py`.
- `INTEGRATION_IMPLEMENTATION_ENTRY` must be the full 40-character
  SHA Sol writes after this revised plan is reviewed. If it is
  omitted, stop. Do not derive it from origin tip, branch,
  merge-base, pull request `headRefOid`, or clock time.
- `PR28_MINIMAL_EVIDENCE_SEAM_REDESIGN_AUTHORIZED=true`
  authorizes only this plan-level replacement of the former
  Task 7→Task 9 temporary-directory evidence bundle with the
  existing Git/GitHub final-head CI evidence seam. It does not
  authorize Tasks 1–9 or any other flag.

---

## File Structure

Current `origin/main...HEAD` must remain exactly these 11 paths
until the future merge:

```text
docs/superpowers/plans/2026-08-19-p3-compiler-alias-ci-test-repair.md
docs/superpowers/plans/2026-08-19-supplemental-r2-path-scan-ci-repair.md
docs/superpowers/plans/2026-08-21-pr17-pr19-ci-integration.md
docs/superpowers/specs/2026-08-19-p3-compiler-alias-ci-test-repair-design.md
docs/superpowers/specs/2026-08-19-supplemental-r2-path-scan-ci-repair-design.md
docs/superpowers/specs/2026-08-21-pr17-pr19-ci-integration-design.md
scripts/external_slice/check_supplemental_r2_admission.py
scripts/external_slice/check_supplemental_r2_handoff_hashes.py
scripts/external_slice/mine_supplemental_r2.py
tests/external_slice/test_check_supplemental_r2_admission.py
tests/p3_v3/test_pilot_build.py
```

After the pull request 18 merge, `origin/main...HEAD` contained
exactly these 13 paths:

```text
docs/superpowers/plans/2026-08-19-p3-compiler-alias-ci-repair.md
docs/superpowers/plans/2026-08-19-p3-compiler-alias-ci-test-repair.md
docs/superpowers/plans/2026-08-19-supplemental-r2-path-scan-ci-repair.md
docs/superpowers/plans/2026-08-21-pr17-pr19-ci-integration.md
docs/superpowers/specs/2026-08-19-p3-compiler-alias-ci-repair-design.md
docs/superpowers/specs/2026-08-19-p3-compiler-alias-ci-test-repair-design.md
docs/superpowers/specs/2026-08-19-supplemental-r2-path-scan-ci-repair-design.md
docs/superpowers/specs/2026-08-21-pr17-pr19-ci-integration-design.md
scripts/external_slice/check_supplemental_r2_admission.py
scripts/external_slice/check_supplemental_r2_handoff_hashes.py
scripts/external_slice/mine_supplemental_r2.py
tests/external_slice/test_check_supplemental_r2_admission.py
tests/p3_v3/test_pilot_build.py
```

After the authorized final-head shallow-history CI remediation,
`origin/main...HEAD` must contain exactly these 14 paths. The
added path is `.github/workflows/sanity.yml`.

```text
.github/workflows/sanity.yml
docs/superpowers/plans/2026-08-19-p3-compiler-alias-ci-repair.md
docs/superpowers/plans/2026-08-19-p3-compiler-alias-ci-test-repair.md
docs/superpowers/plans/2026-08-19-supplemental-r2-path-scan-ci-repair.md
docs/superpowers/plans/2026-08-21-pr17-pr19-ci-integration.md
docs/superpowers/specs/2026-08-19-p3-compiler-alias-ci-repair-design.md
docs/superpowers/specs/2026-08-19-p3-compiler-alias-ci-test-repair-design.md
docs/superpowers/specs/2026-08-19-supplemental-r2-path-scan-ci-repair-design.md
docs/superpowers/specs/2026-08-21-pr17-pr19-ci-integration-design.md
scripts/external_slice/check_supplemental_r2_admission.py
scripts/external_slice/check_supplemental_r2_handoff_hashes.py
scripts/external_slice/mine_supplemental_r2.py
tests/external_slice/test_check_supplemental_r2_admission.py
tests/p3_v3/test_pilot_build.py
```

A fifteenth path is a stop. Do not create helper modules. Do not
edit workflows except the one authorized `fetch-depth: 2` to
`fetch-depth: 0` change in `.github/workflows/sanity.yml`. Do not
change the immutable transport-baseline fetch. Do not add fixed
historical SHAs, another fetch step, or a second workflow edit.

## Frozen Evidence

These tuples are executable assertions, not a second semantic
definition.

```text
PR18_IMPLEMENTATION_REVIEWED=true
PR18_IMPLEMENTATION_REVIEW_PASS=true
PR18 head=4b21072add365923799dccc057d4fefffd69918c
PR18 focused=1 passed
PR18 file=75 passed
PR18 standalone root/CI run=32475544774
PR18 standalone job=96750989039
PR18 standalone collected=1689
PR18 standalone first failure=
tests/external_slice/test_check_supplemental_r2_admission.py::
test_positive_admission_check
PR18 standalone result=1 failed, 81 passed
PR18 standalone classification=
known independent supplemental-R2 blocker

PR28 authoritative RED head=
e62974af4f5e2cfbc65d98c3b2f028edce57d25c
PR28 run=32449925094
PR28 job=96676383508
PR28 collected=1693
PR28 passed before failure=1197
PR28 failure=
test_cmakecache_compiler_generator_root_drift
DID NOT RAISE EvidenceError
```

---

### Task 1: Confirm Explicit Entry And Local-History Grants

**Files:** read only

Task 1 checks only whether Sol wrote the required grants. A
pre-fetch remote-tracking ref is diagnostic only and is never a
pass condition.

- [ ] **Step 1: Refuse without an explicit Sol entry and flags**

Stop unless the later node writes all of the following:

```text
INTEGRATION_IMPLEMENTATION_ENTRY is a Sol-written 40-character SHA.
INTEGRATION_IMPLEMENTATION_AUTHORIZED must be true.
INTEGRATION_IMPLEMENTATION_EXECUTABLE must be true.
LOCAL_HISTORY_INTEGRATION_AUTHORIZED must be true.
```

Plan archival is not that grant.

- [ ] **Step 2: Atomic five-destination fetch, then compare**

```bash
export GIT_CONFIG_GLOBAL=/dev/null
export GIT_CONFIG_NOSYSTEM=1
export GIT_CONFIG_COUNT=0

git status --porcelain

git fetch --atomic origin \
  +refs/heads/main:refs/remotes/origin/main \
  +refs/heads/cursor/supplemental-r2-path-scan-ci-repair-c46c:refs/remotes/origin/cursor/supplemental-r2-path-scan-ci-repair-c46c \
  +refs/heads/cursor/p3-compiler-alias-ci-test-repair-c46c:refs/remotes/origin/cursor/p3-compiler-alias-ci-test-repair-c46c \
  +refs/heads/cursor/p3-compiler-alias-ci-repair-c46c:refs/remotes/origin/cursor/p3-compiler-alias-ci-repair-c46c \
  +refs/heads/cursor/pr17-pr19-ci-integration-c46c:refs/remotes/origin/cursor/pr17-pr19-ci-integration-c46c

git switch cursor/pr17-pr19-ci-integration-c46c

git rev-parse --abbrev-ref HEAD
git rev-parse HEAD
git rev-parse origin/cursor/pr17-pr19-ci-integration-c46c
git rev-parse origin/main
git rev-parse origin/cursor/supplemental-r2-path-scan-ci-repair-c46c
git rev-parse origin/cursor/p3-compiler-alias-ci-test-repair-c46c
git rev-parse origin/cursor/p3-compiler-alias-ci-repair-c46c
git merge-base HEAD origin/main
git rev-list --left-right --count \
  HEAD...origin/cursor/pr17-pr19-ci-integration-c46c
git status --porcelain
```

Required:

```text
branch = cursor/pr17-pr19-ci-integration-c46c
HEAD = INTEGRATION_IMPLEMENTATION_ENTRY
origin PR28 tip = INTEGRATION_IMPLEMENTATION_ENTRY
origin/main = 4444061dde0159a5edd62753fe3cef2d881a308c
merge-base =
4444061dde0159a5edd62753fe3cef2d881a308c
PR #17 head = fb20947a102934415dd201665971a711ccc4e0d5
PR #19 head = 3352cedb5f377b60f0aec5ff80997b2057c7fc14
PR #18 head = 4b21072add365923799dccc057d4fefffd69918c
ahead/behind = 0 0
porcelain = empty
```

`git merge-base HEAD origin/main` must equal
`4444061dde0159a5edd62753fe3cef2d881a308c` verbatim. Executing the
command without comparing that printed SHA is not a pass.

- [ ] **Step 3: Confirm the design digest**

```bash
/usr/bin/python3 - <<'PY'
from hashlib import sha256
from pathlib import Path
p = Path(
    "docs/superpowers/specs/"
    "2026-08-21-pr17-pr19-ci-integration-design.md"
)
digest = sha256(p.read_bytes()).hexdigest()
print(digest)
assert digest == (
    "8ad616cb43204f630e0397f99c68ec4c8a69add28111bef83b3fab50bc13f6b4"
)
PY
```

---

### Task 2: Prove Pre-Merge Topology And Current Scope

**Files:** read only

- [ ] **Step 1: Prove ancestors and the current 11-path set**

```bash
git merge-base --is-ancestor \
  fb20947a102934415dd201665971a711ccc4e0d5 HEAD
echo "PR17_ANCESTOR_EXIT=$?"

git merge-base --is-ancestor \
  3352cedb5f377b60f0aec5ff80997b2057c7fc14 HEAD
echo "PR19_ANCESTOR_EXIT=$?"

git merge-base --is-ancestor \
  4b21072add365923799dccc057d4fefffd69918c HEAD
echo "PR18_ANCESTOR_EXIT=$?"

git diff --name-only \
  4444061dde0159a5edd62753fe3cef2d881a308c...HEAD

/usr/bin/python3 - <<'PY'
from hashlib import sha256
from pathlib import Path
digest = sha256(Path("tests/p3_v3/test_pilot_build.py").read_bytes()).hexdigest()
print(digest)
assert digest == (
    "3278fbce1d0c017d219f450cea76eeb2c962f8d8bdca6b71fc9afad2fb5a0dd6"
)
assert digest != (
    "b1af86f556614b28cd41a204255c47a7c0e4b27cd4812c9cd6491b0c3c824e90"
)
PY
```

Required:

```text
PR17_ANCESTOR_EXIT=0
PR19_ANCESTOR_EXIT=0
PR18_ANCESTOR_EXIT=1
current test blob =
3278fbce1d0c017d219f450cea76eeb2c962f8d8bdca6b71fc9afad2fb5a0dd6
path set = the exact current 11-path set
```

If pull request 18 is already an ancestor, stop. If pull request
17 or 19 is not an ancestor, stop. Do not merge.

---

### Task 3: Merge Pull Request 18 History Once

**Files:** introduced only by the merge

- [ ] **Step 1: Re-assert the three local-history flags**

Stop unless all three are true.

- [ ] **Step 2: Non-fast-forward merge pull request 18**

```bash
git merge --no-ff \
  origin/cursor/p3-compiler-alias-ci-repair-c46c \
  -m "merge: integrate residual CMakeCache CI repair"
```

This command constructs topology on
`cursor/pr17-pr19-ci-integration-c46c` only.

Do not use `--ff-only`, `--squash`, cherry-pick, or rebase.

If Git reports a conflict, stop and return the conflict list. Do
not resolve it by hand. Do not abort, reset, or clean. Do not
widen the write set.

---

### Task 4: Prove Post-Merge Topology And Combined Blob

**Files:** read only after the merge

- [ ] **Step 1: Confirm parents, three ancestors, post-merge paths, and hash**

```bash
git log -1 --format='%H%n%P'
git merge-base --is-ancestor \
  fb20947a102934415dd201665971a711ccc4e0d5 HEAD
echo "PR17_ANCESTOR_EXIT=$?"
git merge-base --is-ancestor \
  3352cedb5f377b60f0aec5ff80997b2057c7fc14 HEAD
echo "PR19_ANCESTOR_EXIT=$?"
git merge-base --is-ancestor \
  4b21072add365923799dccc057d4fefffd69918c HEAD
echo "PR18_ANCESTOR_EXIT=$?"
git diff --check \
  4444061dde0159a5edd62753fe3cef2d881a308c...HEAD
git diff --name-only \
  4444061dde0159a5edd62753fe3cef2d881a308c...HEAD
git status --porcelain

/usr/bin/python3 - <<'PY'
from hashlib import sha256
from pathlib import Path
digest = sha256(Path("tests/p3_v3/test_pilot_build.py").read_bytes()).hexdigest()
print(digest)
assert digest == (
    "b1af86f556614b28cd41a204255c47a7c0e4b27cd4812c9cd6491b0c3c824e90"
)
PY
```

Required:

```text
parent 1 = INTEGRATION_IMPLEMENTATION_ENTRY
parent 2 = 4b21072add365923799dccc057d4fefffd69918c
PR17_ANCESTOR_EXIT=0
PR19_ANCESTOR_EXIT=0
PR18_ANCESTOR_EXIT=0
porcelain = empty
combined test blob =
b1af86f556614b28cd41a204255c47a7c0e4b27cd4812c9cd6491b0c3c824e90
path set immediately after the --no-ff merge = the exact 13-path set
path set after the authorized fetch-depth remediation = the exact 14-path set
```

Requiring the 13-path set as the final base→HEAD state after the
checkout remediation is a stop.

Parent 1 must equal the Sol-written
`INTEGRATION_IMPLEMENTATION_ENTRY` verbatim. The future entry
name is only `INTEGRATION_IMPLEMENTATION_ENTRY`. An isolated
`IMPLEMENTATION_ENTRY` alias is a stop. Parent 2 remains
`4b21072add365923799dccc057d4fefffd69918c`.

A hand-written conflict-resolution commit is a stop.

---

### Task 5: Supplemental R2 Focused Gate

**Files:** none

- [ ] **Step 1: Run the admission file**

```bash
PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1 \
  tests/external_slice/test_check_supplemental_r2_admission.py
```

Expected: 176 passed, exit 0.

Any failure is a stop. Do not edit tests.

---

### Task 6: P3 Focused And File Gates

**Files:** none

- [ ] **Step 1: Run the compile_commands named test**

```bash
PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1 \
  tests/p3_v3/test_pilot_build.py::test_compile_commands_compiler_mismatch
```

Expected: 1 passed, exit 0.

- [ ] **Step 2: Run the CMakeCache named test**

```bash
PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1 \
  tests/p3_v3/test_pilot_build.py::test_cmakecache_compiler_generator_root_drift
```

Expected: 1 passed, exit 0.

- [ ] **Step 3: Run the whole file**

```bash
PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1 \
  tests/p3_v3/test_pilot_build.py
```

Expected: 75 passed, exit 0.

Any failure is a stop. Do not expand scope.

---

### Task 7: Root Pre-Push Diagnostic

**Files:** none

Task 7 is a local pre-push diagnostic only. It is not
authoritative cross-process evidence. An executor summary or
self-reported PASS is not independent evidence.

Do not create or hand off a temporary evidence bundle. Do not
add a directory-inode identity cleanup, a `/proc/self/fd`
dependency, a duplicate bundle parser or validator, a manifest
or captured-summary authority, a parent/name cleanup protocol,
or adversarial cleanup fixtures. Do not replace those deleted
mechanisms with a new hash, manifest, lock, baseline, gate,
temporary evidence store, or parallel validation chain.

- [ ] **Step 1: Record FINAL_HEAD**

```bash
FINAL_HEAD="$(git rev-parse HEAD)"
export FINAL_HEAD
echo "FINAL_HEAD=$FINAL_HEAD"
```

`FINAL_HEAD` is the exact local commit identity that later
becomes the pushed tip. Record the 40-character SHA. Do not
derive a substitute identity from a bundle, manifest, or
executor summary.

- [ ] **Step 2: Run the Actions pytest command locally as a diagnostic**

```bash
PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1
```

Expected local diagnostic outcome:

```text
collected = 1693
passed = 1693
failed = 0
exit = 0
```

A local failure is a stop before push. A local success does
not authorize integration, mark-ready, or merge. Do not export
a Task 7 handoff. Do not retain raw output as a cross-process
authority. Do not interpret a green local root suite as
`MAIN_PR_MERGE_AUTHORIZED` or `MERGE_AUTHORIZED`.

- [ ] **Step 3: Do not run SSOT or live builds**

Do not run `scripts/build_paper_numbers.py`.
Do not run CMake, ninja, make, a real compiler, or Boost.Math.

---

### Task 8: Push The Existing Integration Branch

**Files:** none

- [ ] **Step 1: Push without force**

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
git status --porcelain
```

Required:

```text
HEAD = origin integration tip
ahead/behind = 0 0
porcelain = empty
```

---

### Task 9: Update Pull Request 28 And Wait For Final-Head CI

**Files:** none

The existing Git/GitHub seam is the only authoritative
integration evidence:

```text
record the exact FINAL_HEAD
require pull request 28 headRefOid == FINAL_HEAD
identify the GitHub Actions run and job bound to FINAL_HEAD
require that job completed with conclusion=success
require the original CI job log to remain readable
require that log to contain the test command prescribed by
this plan and its terminal outcome
```

The local independent reviewer must directly read and verify:

```text
pull request 28 metadata
pull request 28 headRefOid
the Actions run bound to FINAL_HEAD
the Actions job bound to FINAL_HEAD
the original job log
```

The reviewer must not rely on an executor-produced PASS
summary.

`gh pr edit` is an update action, not a pass. Do not extract a
verifier library. Do not run a pull-request body grammar,
parser, or machine-checked prose protocol. Do not load a Task 7
bundle. Do not create a replacement hash, manifest, lock,
baseline, gate, temporary evidence store, or parallel
validation chain.

- [ ] **Step 1: Record FINAL_HEAD and update the existing draft**

```bash
FINAL_HEAD="$(git rev-parse HEAD)"
echo "FINAL_HEAD=$FINAL_HEAD"
```

Keep pull request 28 OPEN and draft. Do not mark-ready. Do not
merge. Do not edit pull request 17, 18, or 19.

Write only necessary factual statements. The following facts
are the intended content, not a parse grammar:

```text
Pull request 28 remains the residual CMakeCache third-history
integration on cursor/pr17-pr19-ci-integration-c46c.

Authoritative pre-integration RED:
RED head = e62974af4f5e2cfbc65d98c3b2f028edce57d25c
RED run = 32449925094
RED job = 96676383508

PR #18 source head = 4b21072add365923799dccc057d4fefffd69918c
FINAL_HEAD = <the exact SHA recorded above>

One --no-ff merge of cursor/p3-compiler-alias-ci-repair-c46c
with message:
merge: integrate residual CMakeCache CI repair
PR17 history was not rewritten.
PR19 history was not rewritten.
Cherry-pick, rebase, squash, and manual conflict commits were
not used.

Local root pytest is a pre-push diagnostic only.
Authoritative evidence is Git commit identity, pull request
headRefOid, the FINAL_HEAD-bound sanity-check run and job,
completion and conclusion fields, and the original CI job log.

scripts/build_paper_numbers.py was not run and is not
applicable to this history-only integration.

PR #28 remains OPEN and draft.
PR_READY_AUTHORIZED=false
MAIN_PR_MERGE_AUTHORIZED=false
MERGE_AUTHORIZED=false
REAL_QUALIFICATION_AUTHORIZED=false
ATTEMPT_2_AUTHORIZED=false
CLAIMS_AUTHORIZED=false
FORMAL_DENOMINATOR_MEMBERSHIP=false
```

- [ ] **Step 2: Re-read pull request 28 metadata**

```bash
gh pr view 28 \
  --repo meng004/P3-Semantic-Mutation \
  --json number,state,isDraft,baseRefName,headRefName,headRefOid,body,url
```

Required metadata:

```text
number = 28
state = OPEN
isDraft = true
baseRefName = main
headRefName = cursor/pr17-pr19-ci-integration-c46c
headRefOid = FINAL_HEAD
```

`headRefOid != FINAL_HEAD` is a stop.

- [ ] **Step 3: Identify the FINAL_HEAD Actions run and job, then wait**

Select the newest `sanity-check` run whose `headSha` equals
`FINAL_HEAD`. Do not accept a green run from any other commit,
including run `32539725403` if it belongs to an earlier head.

```bash
FINAL_HEAD="$(git rev-parse HEAD)"
export FINAL_HEAD

gh run list \
  --repo meng004/P3-Semantic-Mutation \
  --workflow sanity-check \
  --commit "$FINAL_HEAD" \
  --limit 20 \
  --json databaseId,headSha,status,conclusion,createdAt,url
```

A bounded wait is mandatory: `DISCOVERY_SECONDS = 600` then,
after a FINAL_HEAD run is selected, `COMPLETION_SECONDS = 3600`
on a monotonic clock. An unbounded `while` loop is a stop. The
workflow job timeout is 30 minutes. 3600 seconds is this
plan's finite wait cap, not a success exemption.

Inspect the selected run:

```bash
gh run view "$RUN_ID" \
  --repo meng004/P3-Semantic-Mutation \
  --json headSha,status,conclusion,jobs,url
```

Required job name:

```text
Run pytest (Path-A cache replay smoke)
```

Two jobs with that name are a stop. A terminal run with zero
matches is a stop. A non-terminal run with zero matches may
wait inside the completion deadline. Only the unique match may
be used.

CI states remain:

```text
A. check not yet present
B. queued / pending / in_progress / waiting / requested
C. completed + success
D. completed + any non-success conclusion
```

Only C passes.

Required after the wait:

```text
run.status = completed
run.conclusion = success
run.headSha = FINAL_HEAD
job.name = Run pytest (Path-A cache replay smoke)
job.status = completed
job.conclusion = success
headRefOid = FINAL_HEAD
```

The original job log must remain readable:

```bash
gh run view "$RUN_ID" \
  --repo meng004/P3-Semantic-Mutation \
  --job "$JOB_ID" \
  --log
```

That original log must contain the root pytest command
prescribed by this plan:

```text
PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1
```

and its terminal outcome:

```text
collected = 1693
passed = 1693
failed = 0
exit = 0
```

or the equivalent Actions transcription of that same command
and outcome. An unavailable, truncated, or ambiguous log is a
stop. Integration remains unauthorized.

Any of these conclusions is a stop:

```text
failure
cancelled
timed_out
action_required
startup_failure
stale
skipped
neutral
or any other non-success value
```

On a non-success terminal run the executor must run:

```bash
gh run view "$RUN_ID" \
  --repo meng004/P3-Semantic-Mutation \
  --job "$JOB_ID" \
  --log-failed
```

and return the first failure plus collected, passed, failed,
exit, and warning counts. Then stop. Do not modify code,
re-merge, re-push, mark-ready, or merge main.

Only after pull-request metadata, `headRefOid == FINAL_HEAD`,
the FINAL_HEAD-bound run and job, completed success, and a
readable original job log that contains the prescribed command
and outcome may the later executor stop for the local
independent reviewer. The reviewer repeats those reads
directly. Do not write an implementation verdict.

---

## Stop Conditions

A later implementation node must stop immediately when:

- the isolated alias `IMPLEMENTATION_ENTRY` still appears;
- parent 1 is not the Sol-written
  `INTEGRATION_IMPLEMENTATION_ENTRY`;
- pull request 28 `headRefOid` is not `FINAL_HEAD`;
- no FINAL_HEAD `sanity-check` run appears before
  `DISCOVERY_SECONDS = 600`;
- the selected FINAL_HEAD run or required job is still
  non-terminal when `COMPLETION_SECONDS = 3600` expires;
- the wait loop has no completion deadline;
- two jobs share the required name
  `Run pytest (Path-A cache replay smoke)`;
- a terminal run has zero matches for that job name;
- the FINAL_HEAD run or job has any non-success terminal
  conclusion;
- the executor cannot identify the Actions run and job
  bound to `FINAL_HEAD`;
- the original CI job log is unavailable, unreadable,
  truncated, or ambiguous;
- the original job log does not contain the prescribed
  pytest command and its terminal collected / passed /
  failed / exit outcome;
- a local root diagnostic is treated as authoritative
  cross-process evidence, or an executor PASS summary is
  treated as independent evidence;
- a Task 7→Task 9 temporary evidence bundle, handoff,
  manifest, captured summary, inode identity, or
  `/proc/self/fd` cleanup protocol is reintroduced;
- a replacement hash, manifest, lock, baseline, gate,
  temporary evidence store, or parallel validation chain is
  added;
- a pull-request body grammar, parser, or machine-checked
  prose protocol is added;
- PR17 or PR19 history is rewritten;
- cherry-pick, rebase, squash, or a hand-written conflict
  commit is used;
- a merge conflict appears;
- the final base→HEAD path set is not the exact 14-path set;
- any required pytest command fails.

---

## Non-Goals

This plan does not:

- re-merge pull request 17 or 19
- cherry-pick or copy `4b21072a`
- create a second combination branch or pull request
- change `.github/workflows` except the one authorized
  `fetch-depth: 2` to `fetch-depth: 0` edit, or skip tests
- change production `os.path.realpath` compares
- run CMake, a real compiler, qualification, or Boost.Math
- run `scripts/build_paper_numbers.py`
- treat plan archival as an executable implementation grant
- treat a local root diagnostic or executor PASS summary as
  final-head CI evidence
- reintroduce the deleted Task 7→Task 9 temporary evidence
  bundle or any replacement store

## Governance Stop

```text
INTEGRATION_IMPLEMENTATION_AUTHORIZED=false
INTEGRATION_IMPLEMENTATION_EXECUTABLE=false
LOCAL_HISTORY_INTEGRATION_AUTHORIZED=false
PR_READY_AUTHORIZED=false
MAIN_PR_MERGE_AUTHORIZED=false
MERGE_AUTHORIZED=false
REAL_QUALIFICATION_AUTHORIZED=false
ATTEMPT_2_AUTHORIZED=false
CLAIMS_AUTHORIZED=false
FORMAL_DENOMINATOR_MEMBERSHIP=false
```

Archiving this plan does not authorize implementation. A later
user node must still grant the three local-history flags and write
`INTEGRATION_IMPLEMENTATION_ENTRY` after Sol Spec plus Standards
PASS.

Pull request 28 stays draft. Pull requests 17, 18, and 19 stay
untouched. Merge stays unauthorized. Local-history permission
stays separate from main-PR merge permission.

This archival node must not start Task 1 through Task 9.

## Redesign Rationale

This authorized plan revision deletes the Task 7→Task 9
cross-process temporary-directory evidence bundle and uses the
existing Git/GitHub final-head CI seam instead.

- Protected asset: integrity of the final-head integration
  decision and timely return to the scientific experiment.
- Credible failure: a stale or wrong-head run, or an executor
  summary, is mistaken for successful final-head CI.
- Observable consequence: integration is authorized without
  successful CI evidence for the exact pull-request head.
- Existing mechanism used: Git commit identity, pull request
  `headRefOid`, Actions run/job head binding, completion and
  conclusion fields, and original CI logs.
- Maintenance cost / failure mode: dependence on GitHub
  metadata and log availability. Unavailable or ambiguous
  final-head evidence must leave integration unauthorized.
- Deletion condition: this one-off integration procedure
  ceases to apply after pull request 28 is resolved, or is
  superseded by an explicitly authorized repository-wide CI
  policy.

## Shallow-History CI Remediation

This one-off exception changes only
`.github/workflows/sanity.yml` `fetch-depth: 2` to
`fetch-depth: 0`. The immutable transport-baseline fetch stays
unchanged. The fixed-range history-audit test stays unchanged.

- Protected asset: the existing no-production-artifact history
  audit and trustworthy final-head CI.
- Trigger: a shallow checkout omits commits required by the
  unchanged test.
- Observable consequence: `git diff` exits 128 before the test
  can evaluate its assertion.
- Why Git SHA alone is insufficient: a SHA identifies an object
  but does not materialize it in a depth-2 checkout.
- Minimal existing control: `actions/checkout` `fetch-depth: 0`.
- Deepest seam: CI checkout object availability.
- Proof: the unchanged 1693-test suite on the new FINAL_HEAD.
- Maintenance cost: increased checkout history transfer.
- Failure mode: checkout time or repository-history growth.
- Deletion condition: the fixed-history test is removed or
  redesigned to consume an independently reviewable artifact
  without runtime Git history.

## Self-Review Record

- Finding 1 remains closed. Task 1, Task 4 Post-Merge Required,
  Stop Conditions, and Governance Stop still use
  `INTEGRATION_IMPLEMENTATION_ENTRY` as the only future-entry
  name. Isolated `IMPLEMENTATION_ENTRY` is a stop. `parent 1`
  must equal the Sol-written SHA verbatim. `parent 2` remains
  `4b21072add365923799dccc057d4fefffd69918c`.
- Temporary-bundle finding is superseded by deletion. Task 7
  no longer creates a private directory, `root.raw`,
  `manifest.json`, handoff JSON, inode identity, or
  `/proc/self/fd` cleanup protocol. Task 9 no longer parses or
  loads a Task 7 bundle. Those mechanisms, and the adversarial
  fixtures that existed only to support them, are removed.
- Pull-request body grammar finding is superseded by deletion.
  Task 9 now records necessary factual statements only. There
  is no H2-sequence parser, canonical `key = value` protocol,
  fence grammar, or machine-checked prose verifier.
- Local-root-authority finding is closed by demotion. Task 7
  remains a pre-push diagnostic. A local PASS or executor
  summary is not independent evidence.
- Final-head CI finding is closed by using the existing
  Git/GitHub seam. Required evidence is the exact
  `FINAL_HEAD`, pull request 28 `headRefOid == FINAL_HEAD`,
  the Actions run and job bound to that head, completed
  success, and a readable original job log that contains the
  prescribed pytest command and terminal outcome.
- Independent-reviewer finding is closed. The local
  independent reviewer must read pull-request metadata,
  `headRefOid`, the Actions run, the Actions job, and the
  original job log directly. The reviewer must not rely on an
  executor-produced PASS summary.
- Duplicate-job finding remains closed. Two jobs with the
  required name are a stop. A terminal run with zero matches
  is a stop. Only the unique FINAL_HEAD-bound job may be used.
- Kept contracts: `DISCOVERY_SECONDS = 600`,
  `COMPLETION_SECONDS = 3600`, newest FINAL_HEAD run, atomic
  five-destination fetch, merge-base, source-head checks, 11
  to 13 path set after the merge and the 14-path set after this
  checkout remediation, current and combined test blobs, exactly one
  `--no-ff` merge, pull request 28 OPEN draft on `main`,
  design as semantic SSOT for topology and frozen history
  values, and local-history versus main-PR merge separation.
- Design remains the semantic SSOT for design choice A and
  the frozen history values. This authorized revision is the
  procedure for final-head integration evidence.
- Entry is fail-closed on an explicit Sol SHA and atomic
  five-destination fetch.
- Execution is not offered from this archival node.
