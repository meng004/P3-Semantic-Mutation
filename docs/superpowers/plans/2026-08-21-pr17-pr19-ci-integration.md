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
is the semantic SSOT. This plan repeats only frozen values, exact
commands, and fail-closed assertions that a later executor must
consume. Those repeated items are executable assertions, not a
second semantic definition. If this plan conflicts with the
design, the executor must stop and return the conflict to Sol.

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

After the future pull request 18 merge, `origin/main...HEAD` must
contain exactly these 13 paths:

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

A fourteenth path is a stop. Do not create helper modules. Do not
edit workflows.

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

- [ ] **Step 1: Confirm parents, three ancestors, 13 paths, and hash**

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
path set = the exact 13-path set
```

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

### Task 7: Root Gate

**Files:** none

- [ ] **Step 1: Reproduce the Actions pytest command**

```bash
PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1
```

Frozen expectation:

```text
collected = 1693
passed = 1693
failed = 0
exit = 0
```

Warnings are allowed. Record the exact warning count and types.
Any failure is a stop. Do not widen scope. Do not interpret a
green root suite as `MAIN_PR_MERGE_AUTHORIZED` or
`MERGE_AUTHORIZED`.

- [ ] **Step 2: Do not run SSOT or live builds**

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

Running `gh pr edit` is not a pass. The later executor must
re-read pull request 28 and prove every heading, field, and
test fact. Empty `statusCheckRollup` is not a pass.

CI states are:

```text
A. check not yet present
B. queued / pending / in_progress
C. completed + success
D. completed + any non-success conclusion
```

Only C passes.

- [ ] **Step 1: Freeze FINAL_HEAD and update the existing draft**

```bash
FINAL_HEAD="$(git rev-parse HEAD)"
echo "FINAL_HEAD=$FINAL_HEAD"
```

Keep pull request 28 OPEN and draft. Do not mark-ready. Do not
merge. Do not edit pull request 17, 18, or 19.

The body must contain these exact headings:

```text
## Motivation
## Changes
## Tests
## SSOT integrity
## Governance
```

Required body facts:

- Motivation: current pull request 28 authoritative RED, pull
  request 18 as the third-history source, and the final
  integration head
- Changes: exactly one `--no-ff` merge of the complete pull
  request 18 history; pull request 17 and 19 histories were not
  rewritten
- Tests: external focused 176 passed; compile_commands named 1
  passed; CMakeCache named 1 passed; pilot file 75 passed; the
  real root collected, passed, failed, exit, and warning counts
- SSOT integrity: `scripts/build_paper_numbers.py` was not run
  and is not applicable to a history-only integration
- Governance: pull request 28 remains OPEN draft; mark-ready,
  main merge, qualification, and claims remain unauthorized

A missing heading, field, or real test fact is a stop.

- [ ] **Step 2: Re-read pull request 28 and verify metadata plus body**

```bash
gh pr view 28 \
  --repo meng004/P3-Semantic-Mutation \
  --json number,state,isDraft,baseRefName,headRefName,headRefOid,body,url,statusCheckRollup
```

Required:

```text
number = 28
state = OPEN
isDraft = true
baseRefName = main
headRefName = cursor/pr17-pr19-ci-integration-c46c
headRefOid = FINAL_HEAD
body contains exact headings:
## Motivation
## Changes
## Tests
## SSOT integrity
## Governance
```

```bash
FINAL_HEAD="$(git rev-parse HEAD)"
export FINAL_HEAD
/usr/bin/python3 - <<PY
import json
import os
import subprocess

final_head = os.environ["FINAL_HEAD"]
raw = subprocess.check_output(
    [
        "gh",
        "pr",
        "view",
        "28",
        "--repo",
        "meng004/P3-Semantic-Mutation",
        "--json",
        "number,state,isDraft,baseRefName,headRefName,headRefOid,body,url,statusCheckRollup",
    ]
)
pr = json.loads(raw)
body = pr["body"]
assert pr["number"] == 28
assert pr["state"] == "OPEN"
assert pr["isDraft"] is True
assert pr["baseRefName"] == "main"
assert pr["headRefName"] == "cursor/pr17-pr19-ci-integration-c46c"
assert pr["headRefOid"] == final_head
for heading in (
    "## Motivation",
    "## Changes",
    "## Tests",
    "## SSOT integrity",
    "## Governance",
):
    assert heading in body, heading
print("PR28_BODY_AND_HEAD_OK")
print("FINAL_HEAD", final_head)
print("headRefOid", pr["headRefOid"])
PY
```

`headRefOid != FINAL_HEAD` is a stop.

- [ ] **Step 3: Discover and wait for the FINAL_HEAD sanity-check**

Select the newest `sanity-check` run whose `headSha` equals
`FINAL_HEAD`. Do not accept a green run from any other commit,
including run `32539725403` if it belongs to an earlier head.

```bash
FINAL_HEAD="$(git rev-parse HEAD)"
export FINAL_HEAD

/usr/bin/python3 - <<'PY'
import json
import subprocess
import sys
import time

REPO = "meng004/P3-Semantic-Mutation"
FINAL_HEAD = subprocess.check_output(
    ["git", "rev-parse", "HEAD"], text=True
).strip()
DISCOVERY_SECONDS = 600
POLL_SECONDS = 15
JOB_NAME = "Run pytest (Path-A cache replay smoke)"
NON_SUCCESS = {
    "failure",
    "cancelled",
    "timed_out",
    "action_required",
    "startup_failure",
    "stale",
    "skipped",
    "neutral",
}


def list_runs():
    raw = subprocess.check_output(
        [
            "gh",
            "run",
            "list",
            "--repo",
            REPO,
            "--workflow",
            "sanity-check",
            "--commit",
            FINAL_HEAD,
            "--limit",
            "20",
            "--json",
            "databaseId,headSha,status,conclusion,createdAt,url",
        ]
    )
    runs = json.loads(raw)
    return [r for r in runs if r.get("headSha") == FINAL_HEAD]


def view_run(run_id):
    raw = subprocess.check_output(
        [
            "gh",
            "run",
            "view",
            str(run_id),
            "--repo",
            REPO,
            "--json",
            "headSha,status,conclusion,jobs,url",
        ]
    )
    return json.loads(raw)


def classify(run):
    status = (run.get("status") or "").lower()
    conclusion = (run.get("conclusion") or "").lower()
    if status in {"queued", "pending", "in_progress", "waiting", "requested"}:
        return "B"
    if status == "completed" and conclusion == "success":
        return "C"
    if status == "completed":
        return "D"
    return "A"


deadline = time.time() + DISCOVERY_SECONDS
selected = None
while time.time() < deadline and selected is None:
    runs = list_runs()
    if runs:
        selected = sorted(runs, key=lambda r: r.get("createdAt") or "", reverse=True)[0]
        break
    print("CI_STATE=A no FINAL_HEAD sanity-check yet")
    time.sleep(POLL_SECONDS)

if selected is None:
    print("CI_STATE=A discovery window expired")
    print("FINAL_HEAD", FINAL_HEAD)
    sys.exit(2)

run_id = selected["databaseId"]
print("DISCOVERED_RUN", run_id, selected.get("url"))
print("CI_STATE", classify(selected))

detail = view_run(run_id)
if detail.get("headSha") != FINAL_HEAD:
    print("viewed run is not bound to FINAL_HEAD")
    sys.exit(3)

while classify(detail) == "B":
    print("CI_STATE=B waiting for terminal run", run_id)
    time.sleep(POLL_SECONDS)
    detail = view_run(run_id)
    if detail.get("headSha") != FINAL_HEAD:
        print("run headSha drifted from FINAL_HEAD")
        sys.exit(3)

state = classify(detail)
print("CI_STATE", state)
print("run.status", detail.get("status"))
print("run.conclusion", detail.get("conclusion"))
print("run.headSha", detail.get("headSha"))
print("run.url", detail.get("url"))

jobs = detail.get("jobs") or []
job = next((j for j in jobs if j.get("name") == JOB_NAME), None)
if job is None:
    print("required job missing")
    sys.exit(4)
print("job.name", job.get("name"))
print("job.status", job.get("status"))
print("job.conclusion", job.get("conclusion"))
print("job.url", job.get("url"))

if state != "C":
    print("CI_STATE=D or non-success terminal")
    print("run.id", run_id)
    print("run.url", detail.get("url"))
    print("job.id", job.get("databaseId") or job.get("id"))
    print("job.url", job.get("url"))
    print("stop; do not edit code, re-merge, or re-push")
    sys.exit(5)
if (detail.get("status") or "").lower() != "completed":
    sys.exit(5)
if (detail.get("conclusion") or "").lower() != "success":
    sys.exit(5)
if (job.get("status") or "").lower() != "completed":
    sys.exit(5)
if (job.get("conclusion") or "").lower() != "success":
    sys.exit(5)
if (detail.get("conclusion") or "").lower() in NON_SUCCESS:
    sys.exit(5)

raw_pr = subprocess.check_output(
    [
        "gh",
        "pr",
        "view",
        "28",
        "--repo",
        REPO,
        "--json",
        "headRefOid,statusCheckRollup",
    ]
)
pr = json.loads(raw_pr)
if pr.get("headRefOid") != FINAL_HEAD:
    print("headRefOid drifted from FINAL_HEAD")
    sys.exit(3)
rollup = pr.get("statusCheckRollup") or []
if not rollup:
    print("empty statusCheckRollup is not a pass")
    sys.exit(6)
print("FINAL_HEAD_CI_OK")
print("RUN_ID", run_id)
PY
```

Required after the wait:

```text
run.status = completed
run.conclusion = success
run.headSha = FINAL_HEAD
job.name = Run pytest (Path-A cache replay smoke)
job.status = completed
job.conclusion = success
```

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

On failure record run id and URL, job id and URL, head SHA,
status, conclusion, the first failure, and collected, passed,
and failed counts when available. Then stop. Do not modify
code, re-merge, or re-push.

Only after pull-request metadata, body facts, and FINAL_HEAD CI
state C all pass may the later executor stop for Sol
implementation review. Do not write an implementation verdict.

---

## Stop Conditions

A later implementation node must stop immediately when:

- the isolated alias `IMPLEMENTATION_ENTRY` still appears;
- any required pull request 28 body heading or field is missing;
- pull request 28 `headRefOid` is not `FINAL_HEAD`;
- no FINAL_HEAD `sanity-check` run appears before the 10-minute
  discovery window ends;
- the FINAL_HEAD check is still non-terminal;
- the FINAL_HEAD run or job has any non-success terminal
  conclusion;
- `statusCheckRollup` is empty or contains only results for an
  older head;
- the executor cannot prove the run and job bind `FINAL_HEAD`;
- parent 1 is not the Sol-written
  `INTEGRATION_IMPLEMENTATION_ENTRY`;
- a merge conflict appears;
- the post-merge path set is not the exact 13-path set;
- any required pytest command fails.

---

## Non-Goals

This plan does not:

- re-merge pull request 17 or 19
- cherry-pick or copy `4b21072a`
- create a second combination branch or pull request
- change `.github/workflows` or skip tests
- change production `os.path.realpath` compares
- run CMake, a real compiler, qualification, or Boost.Math
- run `scripts/build_paper_numbers.py`
- treat plan archival as an executable implementation grant

## Governance Stop

```text
INTEGRATION_IMPLEMENTATION_AUTHORIZED=false
INTEGRATION_IMPLEMENTATION_EXECUTABLE=false
LOCAL_HISTORY_INTEGRATION_AUTHORIZED=false
PR_READY_AUTHORIZED=false
MAIN_PR_MERGE_AUTHORIZED=false
MERGE_AUTHORIZED=false
```

Archiving this plan does not authorize implementation. A later
user node must still grant the three local-history flags and write
`INTEGRATION_IMPLEMENTATION_ENTRY` after Sol Spec plus Standards
PASS.

Pull request 28 stays draft. Pull requests 17, 18, and 19 stay
untouched. Merge stays unauthorized.

This archival node must not start Task 1 through Task 9.

## Self-Review Record

- Finding 1 is closed. Task 1, Task 4 Post-Merge Required,
  Stop Conditions, and Governance Stop use
  `INTEGRATION_IMPLEMENTATION_ENTRY` as the only future-entry
  name. Isolated `IMPLEMENTATION_ENTRY` is a stop. `parent 1`
  must equal the Sol-written SHA verbatim. `parent 2` remains
  `4b21072add365923799dccc057d4fefffd69918c`.
- Finding 2 is closed. Task 9 Required verifies the five exact
  body headings (`## Motivation`, `## Changes`, `## Tests`,
  `## SSOT integrity`, `## Governance`) and the Motivation /
  Changes / Tests / SSOT / Governance facts after a fresh
  `gh pr view`. Running `gh pr edit` alone is not a pass.
- Finding 3 is closed. Task 9 classifies final-head
  `sanity-check` as A / B / C / D and accepts only C
  (`completed` + `success` on `headSha = FINAL_HEAD`). Empty
  rollup, pending, discovery timeout, and any non-success
  terminal conclusion are stops. The wait loop pins one run id
  and selects the newest `headSha == FINAL_HEAD` run. It does
  not reuse older-head green runs.
- Spec coverage: reuse of pull request 28, one remaining
  `--no-ff` merge, pre-merge 11-path and post-merge 13-path
  sets, current and combined test hashes, three-ancestor
  contract, four pytest gates plus recorded root counts, draft
  stop.
- Design remains the semantic SSOT.
- Entry is fail-closed on an explicit Sol SHA and atomic
  five-destination fetch.
- Incomplete-marker scan: clean.
- Execution is not offered from this archival node.
