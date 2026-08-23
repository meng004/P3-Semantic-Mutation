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

- [ ] **Step 1: Freeze FINAL_HEAD and exclusive-create one private bundle**

```bash
FINAL_HEAD="$(git rev-parse HEAD)"
export FINAL_HEAD
echo "FINAL_HEAD=$FINAL_HEAD"
```

Evidence is one exclusive private directory from
`tempfile.mkdtemp(dir="/tmp")`. The prefix must contain
`FINAL_HEAD`. The directory mode must be `0700`. Each attempt
adds an unpredictable `attempt_nonce`. The exact returned path
is the only handle later steps may use. Glob, latest-mtime,
fixed symlink, and directory guessing are stops.

The bundle contains only:

```text
root.raw
manifest.json
```

Task 7 must, in this order, on one fresh pytest capture:

1. Capture that run's stdout and stderr together.
2. Exclusive-create `root.raw` from those exact bytes.
3. Compute SHA-256 and size from those same raw bytes.
4. Parse every evidence tuple from those same raw bytes.
5. Exclusive-create `manifest.json`.
6. `fsync` both files and the directory.
7. Make the files and directory read-only.
8. Exit non-zero if pytest is non-zero or the frozen tuple
   does not match.

`manifest.json` must contain exactly these fields:

```text
schema_version
final_head
attempt_nonce
command
exit
collected
passed
failed
warning_count
warning_types
raw_sha256
raw_size
bundle_path
```

`bundle_path` must be the exact `mkdtemp` return. It is hashed
into `manifest.json`, so the manifest SHA-256 binds that path.

`command` must equal:

```text
PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1
```

The child must run the complete producer through
`produce_task7_handoff`. That function wraps create, make
handoff, initial load, tuple check, JSON serialization, and
stdout write/flush in one outer `try`/`finally`. The bundle is
retained only after the strict handoff JSON has been written
and flushed and the child is committed to exit 0. Any later
failure, `BaseException`, or `SystemExit` must remove the
exact freshly-created path and prove it absent.

Partial-create cleanup may delete only the exact local
`mkdtemp` return retained inside the producer. It must not
use a glob, an empty path, `/tmp`, a guessed path, or a
relocated path. After cleanup the exact path must be absent.

A later same-`FINAL_HEAD` attempt must create a new nonce and
a new private directory. A failed attempt must not block the
next attempt. Deleting a fixed path is not an unlock.

On success the bundle stays until Task 9 finishes body, run,
job, and rollup verification. The Task 7 child must write one
strict JSON handoff object to stdout. The parent shell captures
that object into `TASK7_HANDOFF_JSON` and exports it. The object
contains exactly:

```text
bundle_path
attempt_nonce
raw_sha256
manifest_sha256
final_head
bundle_dev
bundle_ino
```

`bundle_dev` and `bundle_ino` are the create-time `lstat`
identity of the `mkdtemp` directory. Handoff cleanup must
open the captured directory with `O_RDONLY | O_DIRECTORY |
O_NOFOLLOW`, `fstat` that handle against the handed-off
identity, and keep every later enumerate / read / chmod /
unlink / rmdir on that same handle. After that check it
must not re-select `root.raw` or `manifest.json` by
pathname. Path, basename, copyable bytes, hash, mode,
owner, and manifest are not enough. If the captured
pathname is missing or names another object before the
final rmdir, cleanup is non-zero and must not delete the
object now at that pathname. A rename of the original
during cleanup must not retarget the handle at a decoy.

Do not use `eval`, glob, latest-mtime, directory scanning,
guessed paths, fixed symlinks, or manually retyped values.
Task 9 parses the captured object and passes every field to
the loader as a separate expected value. Mutual consistency
between a path and its own manifest is not enough.

A later same-`FINAL_HEAD` attempt must emit a new handoff with
a new nonce and path. The previous handoff must not load the
new bundle.

Task 9 must run body, run, job, and rollup work through
`run_task9_with_handoff_cleanup`, so a Python `finally`
controls cleanup. Do not treat an EXIT-trap return status as
the success signal. If a shell fallback remains, capture
`main_rc` and `cleanup_rc`, disarm the trap, and exit
non-zero whenever `cleanup_rc` is non-zero. Preserve the
original main failure when cleanup succeeds. Main success
plus cleanup failure is a stop. Main failure plus cleanup
failure stays non-zero and must report both.

Handoff cleanup has one destructive seam. Validation uses
the no-follow directory handle and the existing
`bundle_dev` / `bundle_ino` fields. Destructive chmod,
unlink, and rmdir of `root.raw`, `manifest.json`, and the
bundle directory run only on that verified handle. There is
no production `after_validate` hook. A validation failure
refuses deletion, returns non-zero, and leaves the
unverified target untouched. A missing captured path, a
relocated original, a byte-identical replacement, a
post-final-identity-check swap, or a pre-rmdir path swap
must fail closed, must not delete the lookalike, and must
not leave the original raw behind when the handle already
unlinked it. A coordinated handoff that points at a
matching-name decoy that already satisfies mode, owner,
schema, hashes, and path/head/nonce must still be rejected
when it is not the original object. Cleanup must not delete
`/tmp`, an empty path, a glob result, a guessed path, a
relocated path, or a directory verified only by basename
substrings. After a validated cleanup of the original
object the exact path must be absent. Raw output must not
remain indefinitely.

- [ ] **Step 2: Reproduce the Actions pytest command and keep its exit**

```bash
FINAL_HEAD="$(git rev-parse HEAD)"
export FINAL_HEAD
set +e
TASK7_HANDOFF_JSON="$(
/usr/bin/python3 - <<'PY'
import os
import subprocess
import sys
from pathlib import Path

final_head = os.environ["FINAL_HEAD"]
plan = Path("docs/superpowers/plans/2026-08-21-pr17-pr19-ci-integration.md").read_text()
begin = "#" + " === VERIFIER_LIB_BEGIN ==="
end_mark = "#" + " === VERIFIER_LIB_END ==="
start = plan.index(begin)
end = plan.index(end_mark) + len(end_mark)
ns = {}
exec(plan[start:end], ns)
cmd = [
    "/usr/bin/python3",
    "-m",
    "pytest",
    "-q",
    "--maxfail=1",
]
env = os.environ.copy()
env["PYTHONPATH"] = "src"
proc = subprocess.run(
    cmd,
    env=env,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
)
output = (proc.stdout or "") + (proc.stderr or "")
try:
    ns["produce_task7_handoff"](
        final_head, output, proc.returncode
    )
except BaseException:
    print("TASK7_BUNDLE_FAILED", file=sys.stderr)
    raise
sys.exit(0)
PY
)"
task7_rc=$?
set -e
if [ "$task7_rc" -ne 0 ] || [ -z "${TASK7_HANDOFF_JSON}" ]; then
  echo "TASK7_HANDOFF_FAILED"
  exit 1
fi
export TASK7_HANDOFF_JSON
```

Frozen success tuple:

```text
collected = 1693
passed = 1693
failed = 0
exit = 0
```

Warnings are allowed only as values parsed from this fresh
output. Record `warning_count` and `warning_types` from the same
file. Any failure is a stop. Do not widen scope. Do not interpret
a green root suite as `MAIN_PR_MERGE_AUTHORIZED` or
`MERGE_AUTHORIZED`. The pytest exit code is propagated unchanged.

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

Running `gh pr edit` is not a pass. `assert heading in body` is
not a pass. The later executor must extract the verifier library
below, run `run_verifier_self_test()` first, then re-read pull
request 28. The H2 parser collects every unfenced column-0 ATX H2,
including bare `##`, `## Motivation`, `##\tMotivation`, and a
legal ATX closing `#` sequence. Fence parsing records the
backtick or tilde character, opener length `>= 3`, the same
closer character, closer length `>=` opener, and legal leading
or trailing spaces. A four-backtick opener is not closed by
three backticks. An unclosed fence is a failure. The required
heading sequence is:

```text
## Motivation
## Changes
## Tests
## SSOT integrity
## Governance
```

The unfenced H2 sequence must equal those five titles exactly.
Any other unfenced H2 fails. Headings that appear only inside
fenced code, in ordinary sentences, or in inline code are not
section headings. Changes and Tests may contain only blank
lines and known canonical `key = value` facts. Unknown,
duplicate, missing, or wrong-value keys fail. Contradictory
prose such as `rebase was used.`,
`manual conflict commit was used.`, or
`warnings were 999 InventedWarning.` fails even when the legal
keys are also present. Tests warning fields must equal the
Task 7 parsed evidence loaded from the exact returned bundle
for this `FINAL_HEAD`.

CI states remain:

```text
A. check not yet present
B. queued / pending / in_progress / waiting / requested
C. completed + success
D. completed + any non-success conclusion
```

Only C passes. Empty `statusCheckRollup` is not a pass. A
non-empty unrelated rollup is not a pass. A bounded wait is
mandatory: `DISCOVERY_SECONDS = 600` then, after a FINAL_HEAD run
is selected, `COMPLETION_SECONDS = 3600` on a monotonic clock.
An unbounded `while` loop is a stop. The workflow job timeout is
30 minutes. 3600 seconds is this plan's finite wait cap, not a
success exemption.

`wait_for_terminal` collects every job named `REQUIRED_JOB`.
Two matches are a stop. A terminal run with zero matches is a
stop. A non-terminal run with zero matches may wait inside the
completion deadline. Only the unique match may be used.

#### Verifier library

This library is the only body, wait-budget, rollup, Task 7
evidence, and self-test authority. Extract it from this file.

```python
# === VERIFIER_LIB_BEGIN ===
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
import time

HEADINGS = (
    "## Motivation",
    "## Changes",
    "## Tests",
    "## SSOT integrity",
    "## Governance",
)
PR18_HEAD = "4b21072add365923799dccc057d4fefffd69918c"
RED_HEAD = "e62974af4f5e2cfbc65d98c3b2f028edce57d25c"
RED_RUN = "32449925094"
RED_JOB = "96676383508"
MERGE_MESSAGE = "merge: integrate residual CMakeCache CI repair"
SOURCE_BRANCH = "cursor/p3-compiler-alias-ci-repair-c46c"
REQUIRED_JOB = "Run pytest (Path-A cache replay smoke)"
REQUIRED_WORKFLOW = "sanity-check"
REPO = "meng004/P3-Semantic-Mutation"
DISCOVERY_SECONDS = 600
COMPLETION_SECONDS = 3600
POLL_SECONDS = 15
NON_SUCCESS = {
    "failure",
    "cancelled",
    "canceled",
    "timed_out",
    "action_required",
    "startup_failure",
    "stale",
    "skipped",
    "neutral",
}
NON_TERMINAL = {
    "queued",
    "pending",
    "in_progress",
    "waiting",
    "requested",
}
ATX_H2 = re.compile(r"^##(?:$|[ \t].*)$")
ATX_H2_TITLE = re.compile(r"^(##)(?:[ \t]+(.*?)(?:[ \t]+#+)?)?[ \t]*$")
FENCE_MARK = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
FACT_RE = re.compile(r"^([A-Za-z][A-Za-z0-9_.]*)\s*=\s*(.*?)\s*$")
SCHEMA_VERSION = "1"
TASK7_COMMAND = "PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1"
RAW_NAME = "root.raw"
MANIFEST_NAME = "manifest.json"
MANIFEST_FIELDS = (
    "schema_version",
    "final_head",
    "attempt_nonce",
    "command",
    "exit",
    "collected",
    "passed",
    "failed",
    "warning_count",
    "warning_types",
    "raw_sha256",
    "raw_size",
    "bundle_path",
)
HANDOFF_FIELDS = (
    "bundle_path",
    "attempt_nonce",
    "raw_sha256",
    "manifest_sha256",
    "final_head",
    "bundle_dev",
    "bundle_ino",
)
_BUNDLE_OBJECT = {}
INT_FIELDS = (
    "exit",
    "collected",
    "passed",
    "failed",
    "warning_count",
    "raw_size",
)
HEAD_RE = re.compile(r"^[0-9a-f]{40}$")
NONCE_RE = re.compile(r"^[0-9a-f]{32}$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
BUNDLE_ENTRIES = (MANIFEST_NAME, RAW_NAME)
BANNED_TOKENS = re.compile(
    r"\b(TBD|TODO|FIXME|TBA|placeholder)\b",
    re.IGNORECASE,
)
RUN_JOB_URL = re.compile(r"/actions/runs/(\d+)/job/(\d+)")
CHANGES_FACTS = {
    "merge.count": "1",
    "merge.mode": "--no-ff",
    "merge.source_branch": SOURCE_BRANCH,
    "merge.source_head": PR18_HEAD,
    "merge.message": MERGE_MESSAGE,
    "pr17_history_rewritten": "false",
    "pr19_history_rewritten": "false",
    "cherry_pick_used": "false",
    "rebase_used": "false",
    "squash_used": "false",
    "manual_conflict_commit_used": "false",
}
FROZEN_TEST_FACTS = {
    "external_focused_passed": "176",
    "compile_commands_passed": "1",
    "cmakecache_passed": "1",
    "pilot_file_passed": "75",
    "root_collected": "1693",
    "root_passed": "1693",
    "root_failed": "0",
    "root_exit": "0",
}
GOVERNANCE_FLAGS = (
    "PR_READY_AUTHORIZED=false",
    "MAIN_PR_MERGE_AUTHORIZED=false",
    "MERGE_AUTHORIZED=false",
    "REAL_QUALIFICATION_AUTHORIZED=false",
    "ATTEMPT_2_AUTHORIZED=false",
    "CLAIMS_AUTHORIZED=false",
    "FORMAL_DENOMINATOR_MEMBERSHIP=false",
)


class VerifierError(Exception):
    pass


class RealClock:
    def monotonic(self):
        return time.monotonic()

    def sleep(self, seconds):
        time.sleep(seconds)


class FakeClock:
    def __init__(self, start=0.0):
        self.t = float(start)

    def monotonic(self):
        return self.t

    def sleep(self, seconds):
        self.t += float(seconds)


def new_nonce():
    return os.urandom(16).hex()


def write_exclusive_bytes(path, data):
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    fd = os.open(path, flags, 0o600)
    try:
        os.write(fd, data)
        os.fsync(fd)
    finally:
        os.close(fd)


def fsync_dir(path):
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def reject_symlink(path, label):
    if os.path.islink(path):
        raise VerifierError("symlink %s" % label)


def assert_safe_bundle_path(bundle, final_head, nonce):
    if not bundle or not final_head or not nonce:
        raise VerifierError("empty bundle path, FINAL_HEAD, or nonce")
    if os.path.islink(bundle):
        raise VerifierError("bundle is symlink")
    abs_path = os.path.abspath(bundle)
    if abs_path in {"/tmp", "/tmp/"}:
        raise VerifierError("refuses /tmp root")
    if not abs_path.startswith("/tmp/"):
        raise VerifierError("bundle not under /tmp")
    if os.path.dirname(abs_path) != "/tmp":
        raise VerifierError("bundle parent is not /tmp")
    base = os.path.basename(abs_path)
    if final_head not in base:
        raise VerifierError("basename missing FINAL_HEAD")
    if nonce not in base:
        raise VerifierError("basename missing nonce")
    return abs_path


def _chmod_if_exists(path, mode):
    if os.path.lexists(path) and not os.path.islink(path):
        os.chmod(path, mode)


def cleanup_partial_create(bundle, final_head, nonce):
    if not bundle or not final_head or not nonce:
        raise VerifierError("empty partial-create cleanup target")
    if os.path.islink(bundle):
        raise VerifierError("refuses symlink partial cleanup")
    abs_path = os.path.abspath(bundle)
    if abs_path in {"/tmp", "/tmp/"}:
        raise VerifierError("refuses /tmp root")
    if os.path.dirname(abs_path) != "/tmp":
        raise VerifierError("bundle parent is not /tmp")
    if os.path.isdir(abs_path):
        _chmod_if_exists(abs_path, 0o700)
        for name in (RAW_NAME, MANIFEST_NAME):
            child = os.path.join(abs_path, name)
            is_file = os.path.isfile(child)
            if is_file and not os.path.islink(child):
                os.chmod(child, 0o600)
                os.remove(child)
        os.rmdir(abs_path)
    _BUNDLE_OBJECT.pop(abs_path, None)
    if os.path.exists(abs_path) or os.path.lexists(abs_path):
        raise VerifierError("bundle still present after cleanup")


def cleanup_task7_bundle(bundle, final_head, nonce, expected_path=None):
    if expected_path is not None:
        if os.path.abspath(expected_path) != os.path.abspath(bundle):
            raise VerifierError("partial cleanup path is not the mkdtemp path")
    cleanup_partial_create(bundle, final_head, nonce)


def _handoff_identity(handoff):
    dev = handoff.get("bundle_dev")
    ino = handoff.get("bundle_ino")
    if type(dev) is not int or type(ino) is not int:
        raise VerifierError("handoff missing original bundle identity")
    return (dev, ino)


def _path_identity(path):
    reject_symlink(path, "bundle")
    st = os.lstat(path)
    return (st.st_dev, st.st_ino)


def _open_bundle_dir(path):
    if not path:
        raise VerifierError("empty captured path")
    if os.path.islink(path):
        raise VerifierError("bundle is symlink")
    missing = not os.path.exists(path) and not os.path.lexists(path)
    if missing:
        raise VerifierError("captured path missing; original not cleaned")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    return os.open(path, flags)


def _read_bundle_entry(dir_fd, name):
    flags = os.O_RDONLY | os.O_NOFOLLOW
    fd = os.open(name, flags, dir_fd=dir_fd)
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            raise VerifierError("%s is not a regular file" % name)
        if st.st_uid != os.geteuid():
            raise VerifierError("wrong %s owner" % name)
        if st.st_mode & 0o777 != 0o444:
            raise VerifierError("wrong %s mode" % name)
        chunks = []
        while True:
            block = os.read(fd, 65536)
            if not block:
                break
            chunks.append(block)
        return b"".join(chunks)
    finally:
        os.close(fd)


def _validate_bundle_fd(dir_fd, handoff, expected_final_head):
    want = _handoff_identity(handoff)
    st = os.fstat(dir_fd)
    if (st.st_dev, st.st_ino) != want:
        raise VerifierError("not the original Task 7 bundle object")
    if not stat.S_ISDIR(st.st_mode):
        raise VerifierError("bundle is not a directory")
    if st.st_uid != os.geteuid():
        raise VerifierError("wrong bundle owner")
    if st.st_mode & 0o777 != 0o500:
        raise VerifierError("wrong bundle mode")
    names = sorted(os.listdir(dir_fd))
    if names != list(BUNDLE_ENTRIES):
        raise VerifierError(
            "bundle entries must be exactly root.raw and manifest.json"
        )
    raw_bytes = _read_bundle_entry(dir_fd, RAW_NAME)
    man_bytes = _read_bundle_entry(dir_fd, MANIFEST_NAME)
    digest = hashlib.sha256(raw_bytes).hexdigest()
    man_digest = hashlib.sha256(man_bytes).hexdigest()
    if digest != handoff["raw_sha256"]:
        raise VerifierError("handed-off raw_sha256 does not match bytes")
    if man_digest != handoff["manifest_sha256"]:
        raise VerifierError("handed-off manifest_sha256 does not match bytes")
    manifest = json.loads(
        man_bytes.decode("utf-8"), object_pairs_hook=_manifest_object
    )
    validate_manifest_schema(manifest)
    if manifest["final_head"] != expected_final_head:
        raise VerifierError("wrong FINAL_HEAD")
    if manifest["attempt_nonce"] != handoff["attempt_nonce"]:
        raise VerifierError("wrong nonce")
    if manifest["bundle_path"] != handoff["bundle_path"]:
        raise VerifierError("manifest bundle_path != handed-off path")
    if manifest["raw_sha256"] != digest:
        raise VerifierError("wrong raw_sha256")
    if manifest["raw_size"] != len(raw_bytes):
        raise VerifierError("wrong raw_size")


def _captured_path_is_original(path, want):
    if os.path.islink(path):
        return False
    if not os.path.exists(path):
        return False
    return _path_identity(path) == want


def _rmdir_original_fd(dir_fd, want):
    current = os.readlink("/proc/self/fd/%d" % dir_fd)
    parent = os.path.dirname(current)
    name = os.path.basename(current)
    if not name or name in (".", ".."):
        raise VerifierError("held directory has unsafe name")
    if os.path.islink(parent):
        raise VerifierError("held directory parent is a symlink")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    pfd = os.open(parent, flags)
    try:
        child = os.open(name, flags, dir_fd=pfd)
        try:
            st = os.fstat(child)
            held = os.fstat(dir_fd)
            ident = (st.st_dev, st.st_ino)
            held_id = (held.st_dev, held.st_ino)
            if ident != want or ident != held_id:
                raise VerifierError("rmdir target is not the original")
        finally:
            os.close(child)
        os.rmdir(name, dir_fd=pfd)
    finally:
        os.close(pfd)


def cleanup_task7_handoff(handoff, expected_final_head):
    path = os.path.abspath(handoff["bundle_path"])
    want = _handoff_identity(handoff)
    dir_fd = None
    try:
        if handoff["final_head"] != expected_final_head:
            raise VerifierError("cleanup FINAL_HEAD mismatch")
        assert_safe_bundle_path(
            path, handoff["final_head"], handoff["attempt_nonce"]
        )
        dir_fd = _open_bundle_dir(path)
        _validate_bundle_fd(dir_fd, handoff, expected_final_head)
    except Exception as exc:
        if dir_fd is not None:
            try:
                os.close(dir_fd)
            except OSError:
                pass
            dir_fd = None
        raise VerifierError(
            "cleanup validation failed; target left untouched: %s"
            % exc
        )
    try:
        os.fchmod(dir_fd, 0o700)
        for name in (RAW_NAME, MANIFEST_NAME):
            os.chmod(name, 0o600, dir_fd=dir_fd)
            os.unlink(name, dir_fd=dir_fd)
        path_ok = _captured_path_is_original(path, want)
        _rmdir_original_fd(dir_fd, want)
        _BUNDLE_OBJECT.pop(path, None)
        if not path_ok:
            raise VerifierError(
                "captured path missing or replaced before rmdir"
            )
        if os.path.exists(path) or os.path.lexists(path):
            raise VerifierError("bundle still present after cleanup")
    finally:
        if dir_fd is not None:
            try:
                os.close(dir_fd)
            except OSError:
                pass


def _manifest_object(pairs):
    seen = {}
    for key, value in pairs:
        if key in seen:
            raise VerifierError("duplicate manifest field %s" % key)
        seen[key] = value
    return seen


def format_warning_types(types):
    return ",".join(types) if types else "-"


def parse_pytest_output(text, exit_code, final_head):
    collected_m = re.search(r"\bcollected\s+(\d+)\b", text)
    passed_m = re.search(r"\b(\d+)\s+passed\b", text)
    failed_m = re.search(r"\b(\d+)\s+failed\b", text)
    warn_m = re.search(r"\b(\d+)\s+warnings?\b", text)
    types = []
    seen = set()
    for match in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*Warning)\b", text):
        name = match.group(1)
        if name not in seen:
            seen.add(name)
            types.append(name)
    if collected_m is None or passed_m is None:
        raise VerifierError("Task 7 output missing collected/passed")
    return {
        "final_head": final_head,
        "collected": int(collected_m.group(1)),
        "passed": int(passed_m.group(1)),
        "failed": int(failed_m.group(1)) if failed_m else 0,
        "exit": int(exit_code),
        "warning_count": int(warn_m.group(1)) if warn_m else 0,
        "warning_types": types,
    }


def sample_task7_raw():
    return (
        "collected 1693 items\n"
        "===== 1693 passed, 10 warnings in 1.23s =====\n"
        "PytestCollectionWarning: demo\n"
    )


def create_task7_bundle(final_head, raw_text, exit_code, nonce=None, fail_after=None):
    nonce = nonce or new_nonce()
    bundle = None
    success = False
    try:
        prefix = "pr28-task7-%s-%s-" % (final_head, nonce)
        bundle = tempfile.mkdtemp(prefix=prefix, dir="/tmp")
        st = os.lstat(bundle)
        _BUNDLE_OBJECT[os.path.abspath(bundle)] = (st.st_dev, st.st_ino)
        os.chmod(bundle, 0o700)
        assert_safe_bundle_path(bundle, final_head, nonce)
        reject_symlink(bundle, "bundle")
        raw_bytes = raw_text.encode("utf-8") if not isinstance(raw_text, bytes) else raw_text
        raw_path = os.path.join(bundle, RAW_NAME)
        man_path = os.path.join(bundle, MANIFEST_NAME)
        write_exclusive_bytes(raw_path, raw_bytes)
        if fail_after == "raw":
            raise VerifierError("injected failure after raw")
        parsed = parse_pytest_output(raw_bytes.decode("utf-8"), exit_code, final_head)
        bundle_path = os.path.abspath(bundle)
        manifest = {
            "schema_version": SCHEMA_VERSION,
            "final_head": final_head,
            "attempt_nonce": nonce,
            "command": TASK7_COMMAND,
            "exit": parsed["exit"],
            "collected": parsed["collected"],
            "passed": parsed["passed"],
            "failed": parsed["failed"],
            "warning_count": parsed["warning_count"],
            "warning_types": list(parsed["warning_types"]),
            "raw_sha256": hashlib.sha256(raw_bytes).hexdigest(),
            "raw_size": len(raw_bytes),
            "bundle_path": bundle_path,
        }
        write_exclusive_bytes(
            man_path, (json.dumps(manifest, sort_keys=True) + "\n").encode("utf-8")
        )
        fsync_dir(bundle)
        os.chmod(raw_path, 0o444)
        os.chmod(man_path, 0o444)
        os.chmod(bundle, 0o500)
        success = True
        return bundle_path, manifest
    finally:
        if bundle and not success:
            cleanup_partial_create(bundle, final_head, nonce)


def _check_owned_mode(path, label, expected_mode, want_dir):
    reject_symlink(path, label)
    st = os.lstat(path)
    if want_dir and not stat.S_ISDIR(st.st_mode):
        raise VerifierError("%s is not a directory" % label)
    if not want_dir and not stat.S_ISREG(st.st_mode):
        raise VerifierError("%s is not a regular file" % label)
    if st.st_uid != os.geteuid():
        raise VerifierError("wrong %s owner" % label)
    if st.st_mode & 0o777 != expected_mode:
        raise VerifierError("wrong %s mode" % label)


def _require_hex(value, regex, label):
    if type(value) is not str or regex.fullmatch(value) is None:
        raise VerifierError("malformed %s" % label)


def validate_manifest_schema(manifest):
    extra = set(manifest) - set(MANIFEST_FIELDS)
    missing = set(MANIFEST_FIELDS) - set(manifest)
    if extra or missing:
        raise VerifierError(
            "manifest fields missing=%s extra=%s" % (sorted(missing), sorted(extra))
        )
    if manifest["schema_version"] != SCHEMA_VERSION:
        raise VerifierError("wrong schema_version")
    if manifest["command"] != TASK7_COMMAND:
        raise VerifierError("wrong command")
    _require_hex(manifest["final_head"], HEAD_RE, "FINAL_HEAD")
    _require_hex(manifest["attempt_nonce"], NONCE_RE, "nonce")
    _require_hex(manifest["raw_sha256"], SHA_RE, "raw_sha256")
    if type(manifest["bundle_path"]) is not str:
        raise VerifierError("bundle_path must be a string")
    for key in INT_FIELDS:
        if type(manifest[key]) is not int:
            raise VerifierError("%s must be int" % key)
    warning_types = manifest["warning_types"]
    if type(warning_types) is not list:
        raise VerifierError("warning_types must be a JSON array of strings")
    if any(type(item) is not str for item in warning_types):
        raise VerifierError("warning_types must be a JSON array of strings")


def make_task7_handoff(bundle, manifest):
    man_path = os.path.join(bundle, MANIFEST_NAME)
    man_bytes = open(man_path, "rb").read()
    path = os.path.abspath(bundle)
    ident = _BUNDLE_OBJECT.get(path)
    if ident is None:
        raise VerifierError("handoff missing create-time bundle identity")
    return {
        "bundle_path": path,
        "attempt_nonce": manifest["attempt_nonce"],
        "raw_sha256": manifest["raw_sha256"],
        "manifest_sha256": hashlib.sha256(man_bytes).hexdigest(),
        "final_head": manifest["final_head"],
        "bundle_dev": ident[0],
        "bundle_ino": ident[1],
    }


def parse_task7_handoff(text, expected_final_head):
    if type(text) is not str or not text.strip():
        raise VerifierError("empty Task 7 handoff")
    handoff = json.loads(text, object_pairs_hook=_manifest_object)
    extra = set(handoff) - set(HANDOFF_FIELDS)
    missing = set(HANDOFF_FIELDS) - set(handoff)
    if extra or missing:
        raise VerifierError(
            "handoff fields missing=%s extra=%s" % (sorted(missing), sorted(extra))
        )
    _require_hex(handoff["final_head"], HEAD_RE, "FINAL_HEAD")
    _require_hex(handoff["attempt_nonce"], NONCE_RE, "nonce")
    _require_hex(handoff["raw_sha256"], SHA_RE, "raw_sha256")
    _require_hex(handoff["manifest_sha256"], SHA_RE, "manifest_sha256")
    if type(handoff["bundle_path"]) is not str:
        raise VerifierError("bundle_path must be a string")
    if type(handoff["bundle_dev"]) is not int:
        raise VerifierError("bundle_dev must be int")
    if type(handoff["bundle_ino"]) is not int:
        raise VerifierError("bundle_ino must be int")
    if handoff["final_head"] != expected_final_head:
        raise VerifierError("handoff FINAL_HEAD mismatch")
    return handoff


def load_task7_evidence(
    bundle_dir,
    expected_final_head,
    expected_nonce,
    expected_raw_sha256,
    expected_manifest_sha256,
    expected_bundle_path,
):
    if bundle_dir != expected_bundle_path:
        raise VerifierError("bundle_dir != handed-off path")
    _require_hex(expected_final_head, HEAD_RE, "FINAL_HEAD")
    _require_hex(expected_nonce, NONCE_RE, "nonce")
    _require_hex(expected_raw_sha256, SHA_RE, "raw_sha256")
    _require_hex(expected_manifest_sha256, SHA_RE, "manifest_sha256")
    abs_dir = assert_safe_bundle_path(
        bundle_dir, expected_final_head, expected_nonce
    )
    if abs_dir != os.path.abspath(expected_bundle_path):
        raise VerifierError("loaded path != handed-off path")
    _check_owned_mode(abs_dir, "bundle", 0o500, True)
    names = sorted(os.listdir(abs_dir))
    if names != list(BUNDLE_ENTRIES):
        raise VerifierError(
            "bundle entries must be exactly root.raw and manifest.json"
        )
    raw_path = os.path.join(abs_dir, RAW_NAME)
    man_path = os.path.join(abs_dir, MANIFEST_NAME)
    _check_owned_mode(raw_path, "raw", 0o444, False)
    _check_owned_mode(man_path, "manifest", 0o444, False)
    raw_bytes = open(raw_path, "rb").read()
    man_bytes = open(man_path, "rb").read()
    digest = hashlib.sha256(raw_bytes).hexdigest()
    man_digest = hashlib.sha256(man_bytes).hexdigest()
    if digest != expected_raw_sha256:
        raise VerifierError("handed-off raw_sha256 does not match bytes")
    if man_digest != expected_manifest_sha256:
        raise VerifierError("handed-off manifest_sha256 does not match bytes")
    manifest = json.loads(
        man_bytes.decode("utf-8"), object_pairs_hook=_manifest_object
    )
    validate_manifest_schema(manifest)
    if manifest["final_head"] != expected_final_head:
        raise VerifierError("wrong FINAL_HEAD")
    if manifest["attempt_nonce"] != expected_nonce:
        raise VerifierError("wrong nonce")
    if manifest["raw_sha256"] != digest:
        raise VerifierError("wrong raw_sha256")
    if manifest["raw_size"] != len(raw_bytes):
        raise VerifierError("wrong raw_size")
    if manifest["bundle_path"] != expected_bundle_path:
        raise VerifierError("manifest bundle_path != handed-off path")
    if manifest["bundle_path"] != abs_dir:
        raise VerifierError("manifest bundle_path != loaded path")
    parsed = parse_pytest_output(
        raw_bytes.decode("utf-8"), manifest["exit"], expected_final_head
    )
    for key in ("collected", "passed", "failed", "exit", "warning_count", "final_head"):
        if parsed[key] != manifest[key]:
            raise VerifierError("manifest %s does not match raw" % key)
    if list(parsed["warning_types"]) != list(manifest["warning_types"]):
        raise VerifierError("manifest warning_types does not match raw")
    parsed["schema_version"] = manifest["schema_version"]
    parsed["attempt_nonce"] = manifest["attempt_nonce"]
    parsed["command"] = manifest["command"]
    parsed["bundle_path"] = manifest["bundle_path"]
    parsed["raw_sha256"] = digest
    parsed["raw_size"] = manifest["raw_size"]
    parsed["manifest_sha256"] = man_digest
    return parsed


def produce_task7_handoff(
    final_head,
    raw_text,
    exit_code,
    stdout=None,
    stderr=None,
    fail_after=None,
    nonce=None,
):
    stdout = sys.stdout if stdout is None else stdout
    stderr = sys.stderr if stderr is None else stderr
    nonce = nonce or new_nonce()
    bundle = None
    committed = False

    class _Gate:
        def __init__(self, real, point):
            self.real = real
            self.point = point

        def write(self, data):
            if self.point == "write":
                raise VerifierError("injected stdout write failure")
            return self.real.write(data)

        def flush(self):
            if self.point == "flush":
                raise VerifierError("injected stdout flush failure")
            return self.real.flush()

    try:
        bundle, manifest = create_task7_bundle(
            final_head, raw_text, exit_code, nonce=nonce
        )
        nonce = manifest["attempt_nonce"]
        if fail_after == "make_handoff":
            os.chmod(bundle, 0o700)
            man_path = os.path.join(bundle, MANIFEST_NAME)
            os.chmod(man_path, 0o600)
            os.remove(man_path)
        handoff = make_task7_handoff(bundle, manifest)
        load_nonce = nonce
        if fail_after == "loader":
            load_nonce = "0" * 32
        evidence = load_task7_evidence(
            handoff["bundle_path"],
            final_head,
            load_nonce,
            handoff["raw_sha256"],
            handoff["manifest_sha256"],
            handoff["bundle_path"],
        )
        tuple_ok = (
            evidence["collected"] == 1693
            and evidence["passed"] == 1693
            and evidence["failed"] == 0
            and evidence["exit"] == 0
            and exit_code == 0
        )
        if fail_after == "tuple" or not tuple_ok:
            raise VerifierError(
                "root tuple is not the planned 1693/1693/0/0 success"
            )
        if fail_after == "serialize":
            json.dumps(object())
        payload = json.dumps(handoff, sort_keys=True) + "\n"
        print(json.dumps(evidence, sort_keys=True), file=stderr)
        out = stdout
        if fail_after in ("write", "flush"):
            out = _Gate(stdout, fail_after)
        out.write(payload)
        out.flush()
        committed = True
        return handoff, evidence
    finally:
        if bundle and not committed:
            cleanup_partial_create(bundle, final_head, nonce)


def run_task9_with_handoff_cleanup(handoff_json, expected_final_head, work):
    handoff = parse_task7_handoff(handoff_json, expected_final_head)
    pending = None
    try:
        return work(handoff)
    except BaseException as exc:
        pending = exc
        raise
    finally:
        cleanup_exc = None
        try:
            cleanup_task7_handoff(handoff, expected_final_head)
        except Exception as exc:
            cleanup_exc = exc
        still_here = os.path.exists(handoff["bundle_path"]) or os.path.lexists(
            handoff["bundle_path"]
        )
        if cleanup_exc is None and still_here:
            cleanup_exc = VerifierError("bundle still present after cleanup")
        if cleanup_exc is not None and pending is None:
            raise VerifierError("cleanup failed: %s" % cleanup_exc)
        if cleanup_exc is not None:
            raise VerifierError(
                "main failed (%s); cleanup failed (%s)"
                % (pending, cleanup_exc)
            )


def normalize_h2(line):
    key = line.rstrip("\n")
    match = ATX_H2_TITLE.match(key)
    if match is None or not ATX_H2.match(key):
        return None
    title = (match.group(2) or "").strip()
    if not title:
        return "##"
    return "## " + title


def iter_unfenced_lines(text):
    in_fence = False
    fence_char = None
    fence_len = 0
    out = []
    for lineno, line in enumerate(text.splitlines(), 1):
        match = FENCE_MARK.match(line)
        if match:
            mark = match.group(1)
            char = mark[0]
            length = len(mark)
            rest = match.group(2)
            if length < 3:
                raise VerifierError("fence opener shorter than 3")
            if not in_fence:
                in_fence = True
                fence_char = char
                fence_len = length
                continue
            if (
                char == fence_char
                and length >= fence_len
                and rest.strip() == ""
            ):
                in_fence = False
                fence_char = None
                fence_len = 0
                continue
        if in_fence:
            continue
        out.append((lineno, line))
    if in_fence:
        raise VerifierError("unclosed fence")
    return out


def extract_h2_sections(body):
    lines = iter_unfenced_lines(body)
    found = []
    for lineno, line in lines:
        key = normalize_h2(line)
        if key is not None:
            found.append((lineno, key))
    names = [key for _lineno, key in found]
    if names != list(HEADINGS):
        raise VerifierError(
            "unfenced H2 sequence must equal HEADINGS exactly; got %s" % (names,)
        )
    sections = {key: [] for key in HEADINGS}
    current = None
    for _lineno, line in lines:
        key = normalize_h2(line)
        if key is not None:
            current = key
            continue
        if current is not None:
            sections[current].append(line)
    out = {}
    for key in HEADINGS:
        text = "\n".join(sections[key])
        if not text.strip():
            raise VerifierError("empty section %s" % key)
        out[key] = text
    return out


def parse_canonical_facts(section_name, text, expected):
    facts = {}
    for line in text.splitlines():
        if line.strip() == "":
            continue
        match = FACT_RE.match(line.strip())
        if match is None:
            raise VerifierError(
                "%s non-canonical line %r" % (section_name, line)
            )
        key, value = match.group(1), match.group(2)
        if key in facts:
            raise VerifierError("%s duplicate key %s" % (section_name, key))
        if key not in expected:
            raise VerifierError("%s unknown key %s" % (section_name, key))
        facts[key] = value
    for key, expected_value in expected.items():
        if key not in facts:
            raise VerifierError("%s missing key %s" % (section_name, key))
        if facts[key] != expected_value:
            raise VerifierError(
                "%s %s expected %r got %r"
                % (section_name, key, expected_value, facts[key])
            )
    return facts


def _require(section_name, text, needle, exact=False):
    haystack = text if exact else text.lower()
    pin = needle if exact else needle.lower()
    if pin not in haystack:
        raise VerifierError("%s missing %r" % (section_name, needle))


def _require_re(section_name, text, pattern, label):
    if re.search(pattern, text, re.IGNORECASE | re.MULTILINE) is None:
        raise VerifierError("%s missing %s" % (section_name, label))


def assert_pr_body(body, final_head, evidence):
    if not re.fullmatch(r"[0-9a-f]{40}", final_head or ""):
        raise VerifierError("FINAL_HEAD must be a 40-character lowercase SHA")
    if not evidence:
        raise VerifierError("Task 7 evidence is required")
    if evidence.get("final_head") != final_head:
        raise VerifierError("evidence.final_head != FINAL_HEAD")
    sections = extract_h2_sections(body)

    motivation = sections["## Motivation"]
    _require("Motivation", motivation, "authoritative")
    _require("Motivation", motivation, "RED")
    _require("Motivation", motivation, RED_HEAD, exact=True)
    _require("Motivation", motivation, RED_RUN, exact=True)
    _require("Motivation", motivation, RED_JOB, exact=True)
    _require("Motivation", motivation, PR18_HEAD, exact=True)
    _require("Motivation", motivation, final_head, exact=True)
    _require_re("Motivation", motivation, r"PR\s*#?\s*28|pull request 28", "PR 28")

    parse_canonical_facts("Changes", sections["## Changes"], CHANGES_FACTS)

    tests = sections["## Tests"]
    if BANNED_TOKENS.search(tests):
        raise VerifierError("Tests contains a banned token")
    expected_tests = dict(FROZEN_TEST_FACTS)
    expected_tests["root_warning_count"] = str(evidence["warning_count"])
    expected_tests["root_warning_types"] = format_warning_types(
        evidence.get("warning_types") or []
    )
    for key in ("collected", "passed", "failed", "exit"):
        if str(evidence[key]) != expected_tests["root_%s" % key]:
            raise VerifierError("evidence root_%s mismatch" % key)
    parse_canonical_facts("Tests", tests, expected_tests)

    ssot = sections["## SSOT integrity"]
    _require("SSOT integrity", ssot, "scripts/build_paper_numbers.py", exact=True)
    _require("SSOT integrity", ssot, "not run")
    _require("SSOT integrity", ssot, "not applicable")
    _require("SSOT integrity", ssot, "history-only")

    gov = sections["## Governance"]
    _require("Governance", gov, "OPEN")
    _require_re("Governance", gov, r"\bdraft\b", "draft")
    for flag in GOVERNANCE_FLAGS:
        if re.search(r"(?<![A-Z_])" + re.escape(flag), gov) is None:
            raise VerifierError("Governance missing %r" % flag)
    return sections


def classify(item):
    if not item:
        return "A"
    status = (item.get("status") or "").lower()
    conclusion = (item.get("conclusion") or "").lower()
    if status in NON_TERMINAL:
        return "B"
    if status == "completed" and conclusion == "success":
        return "C"
    if status == "completed":
        return "D"
    return "A"


def is_non_success_conclusion(conclusion):
    return (conclusion or "").lower() in NON_SUCCESS


def details_url_binds(url, run_id, job_id):
    if not url:
        return False
    match = RUN_JOB_URL.search(url)
    if match is None:
        return False
    return match.group(1) == str(run_id) and match.group(2) == str(job_id)


def select_newest_final_head_run(runs, final_head):
    matched = [run for run in runs if run.get("headSha") == final_head]
    if not matched:
        return None
    return sorted(matched, key=lambda run: run.get("createdAt") or "", reverse=True)[0]


def _job_id(job):
    return job.get("databaseId") or job.get("id")


def wait_for_terminal(get_detail, run_id, final_head, clock, completion_seconds=COMPLETION_SECONDS, poll_seconds=POLL_SECONDS):
    deadline = clock.monotonic() + float(completion_seconds)
    detail = None
    job = None
    while True:
        if clock.monotonic() >= deadline:
            return {
                "expired": True,
                "detail": detail,
                "job": job,
                "run_id": run_id,
                "final_head": final_head,
            }
        detail = get_detail(run_id)
        if detail.get("headSha") != final_head:
            raise VerifierError("run headSha is not FINAL_HEAD")
        jobs = detail.get("jobs") or []
        matching_jobs = [
            item for item in jobs if item.get("name") == REQUIRED_JOB
        ]
        if len(matching_jobs) > 1:
            raise VerifierError(
                "duplicate required jobs: "
                + "; ".join(
                    "id=%s url=%s status=%s conclusion=%s"
                    % (
                        _job_id(item),
                        item.get("url"),
                        item.get("status"),
                        item.get("conclusion"),
                    )
                    for item in matching_jobs
                )
            )
        run_state = classify(detail)
        if len(matching_jobs) == 0:
            if run_state in {"C", "D"}:
                raise VerifierError("required job missing on terminal run")
            job = None
            job_state = "B"
        else:
            job = matching_jobs[0]
            job_state = classify(job)
        if run_state == "D" or job_state == "D":
            return {
                "expired": False,
                "state": "D",
                "detail": detail,
                "job": job,
                "run_id": run_id,
                "final_head": final_head,
            }
        if run_state == "C" and job_state == "C":
            return {
                "expired": False,
                "state": "C",
                "detail": detail,
                "job": job,
                "run_id": run_id,
                "final_head": final_head,
            }
        clock.sleep(poll_seconds)


def format_timeout(result):
    detail = result.get("detail") or {}
    job = result.get("job") or {}
    lines = [
        "COMPLETION_DEADLINE_EXPIRED",
        "FINAL_HEAD %s" % result.get("final_head"),
        "run.id %s" % result.get("run_id"),
        "run.url %s" % detail.get("url"),
        "run.status %s" % detail.get("status"),
        "run.conclusion %s" % detail.get("conclusion"),
        "job.id %s" % _job_id(job),
        "job.url %s" % job.get("url"),
        "job.status %s" % job.get("status"),
        "job.conclusion %s" % job.get("conclusion"),
        "stop; do not edit, re-merge, re-push, mark-ready, or merge main",
    ]
    return "\n".join(lines)


def failure_log_command(run_id, job_id):
    return [
        "gh",
        "run",
        "view",
        str(run_id),
        "--repo",
        REPO,
        "--job",
        str(job_id),
        "--log-failed",
    ]


def assert_rollup_bound(pr, final_head, run_id, job_id, job_url=None):
    if pr.get("headRefOid") != final_head:
        raise VerifierError("headRefOid != FINAL_HEAD")
    rollup = pr.get("statusCheckRollup")
    if not rollup:
        raise VerifierError("empty statusCheckRollup")
    required = []
    for entry in rollup:
        name = entry.get("name")
        workflow = entry.get("workflowName")
        status = (entry.get("status") or "").upper()
        conclusion = (entry.get("conclusion") or "").upper()
        url = entry.get("detailsUrl") or entry.get("url") or ""
        is_required = workflow == REQUIRED_WORKFLOW and name == REQUIRED_JOB
        if not is_required:
            raise VerifierError("unrelated rollup entry %r / %r" % (workflow, name))
        if status in {item.upper() for item in NON_TERMINAL}:
            raise VerifierError("pending rollup entry")
        if status != "COMPLETED":
            raise VerifierError("rollup status %s" % status)
        if is_non_success_conclusion(conclusion) or conclusion != "SUCCESS":
            raise VerifierError("rollup conclusion %s" % conclusion)
        bound = False
        if job_url and url == job_url:
            bound = True
        if details_url_binds(url, run_id, job_id):
            bound = True
        if not bound:
            raise VerifierError("rollup detailsUrl is not bound to selected run/job")
        required.append(entry)
    if len(required) != 1:
        raise VerifierError("required CheckRun missing or ambiguous: %s" % len(required))
    return required[0]


def _reordered_body(final_head, evidence):
    sections = extract_h2_sections(_valid_body(final_head, evidence))
    order = (
        "## Changes",
        "## Motivation",
        "## Tests",
        "## SSOT integrity",
        "## Governance",
    )
    parts = []
    for heading in order:
        parts.append(heading)
        parts.append("")
        parts.append(sections[heading].strip())
        parts.append("")
    return "\n".join(parts)


def _valid_evidence(final_head):
    return {
        "final_head": final_head,
        "collected": 1693,
        "passed": 1693,
        "failed": 0,
        "exit": 0,
        "warning_count": 10,
        "warning_types": ["PytestCollectionWarning"],
    }


def _valid_body(final_head, evidence, extra_h2=None, changes=None, tests_overlay=None):
    warning_types = format_warning_types(evidence.get("warning_types") or [])
    change_lines = "\n".join(
        "%s = %s" % (key, value) for key, value in CHANGES_FACTS.items()
    )
    if changes:
        change_lines = changes
    test_facts = dict(FROZEN_TEST_FACTS)
    test_facts["root_warning_count"] = str(evidence["warning_count"])
    test_facts["root_warning_types"] = warning_types
    if tests_overlay:
        test_facts.update(tests_overlay)
    test_lines = "\n".join("%s = %s" % (key, value) for key, value in test_facts.items())
    body = """## Motivation

Authoritative pull request 28 RED.
RED head %s
RED run %s
RED job %s
PR #18 source head %s
FINAL_HEAD %s

## Changes

%s

## Tests

%s

## SSOT integrity

scripts/build_paper_numbers.py was not run
and is not applicable to history-only integration

## Governance

PR #28 remains OPEN
PR #28 remains draft
PR_READY_AUTHORIZED=false
MAIN_PR_MERGE_AUTHORIZED=false
MERGE_AUTHORIZED=false
REAL_QUALIFICATION_AUTHORIZED=false
ATTEMPT_2_AUTHORIZED=false
CLAIMS_AUTHORIZED=false
FORMAL_DENOMINATOR_MEMBERSHIP=false
""" % (
        RED_HEAD,
        RED_RUN,
        RED_JOB,
        PR18_HEAD,
        final_head,
        change_lines,
        test_lines,
    )
    if extra_h2:
        body += "\n%s\nextra\n" % extra_h2
    return body


def _required_job(job_id, status, conclusion):
    return {
        "name": REQUIRED_JOB,
        "databaseId": job_id,
        "id": job_id,
        "status": status,
        "conclusion": conclusion,
        "url": "https://github.com/%s/actions/runs/1/job/%s" % (REPO, job_id),
    }


def _required_rollup(run_id, job_id, status="COMPLETED", conclusion="SUCCESS"):
    return {
        "workflowName": REQUIRED_WORKFLOW,
        "name": REQUIRED_JOB,
        "status": status,
        "conclusion": conclusion,
        "detailsUrl": "https://github.com/%s/actions/runs/%s/job/%s"
        % (REPO, run_id, job_id),
    }


def _force_rm_bundle(path):
    if not os.path.isdir(path):
        return
    os.chmod(path, 0o700)
    for name in os.listdir(path):
        child = os.path.join(path, name)
        is_file = os.path.isfile(child) and not os.path.islink(child)
        if is_file:
            os.chmod(child, 0o600)
            os.remove(child)
    os.rmdir(path)


def _valid_lookalike(dest, final_head, nonce, raw, path_value):
    dest = os.path.abspath(dest)
    os.mkdir(dest, 0o700)
    raw_b = raw.encode("utf-8") if not isinstance(raw, bytes) else raw
    write_exclusive_bytes(os.path.join(dest, RAW_NAME), raw_b)
    parsed = parse_pytest_output(raw_b.decode("utf-8"), 0, final_head)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "final_head": final_head,
        "attempt_nonce": nonce,
        "command": TASK7_COMMAND,
        "exit": parsed["exit"],
        "collected": parsed["collected"],
        "passed": parsed["passed"],
        "failed": parsed["failed"],
        "warning_count": parsed["warning_count"],
        "warning_types": list(parsed["warning_types"]),
        "raw_sha256": hashlib.sha256(raw_b).hexdigest(),
        "raw_size": len(raw_b),
        "bundle_path": os.path.abspath(path_value),
    }
    write_exclusive_bytes(
        os.path.join(dest, MANIFEST_NAME),
        (json.dumps(manifest, sort_keys=True) + "\n").encode("utf-8"),
    )
    os.chmod(os.path.join(dest, RAW_NAME), 0o444)
    os.chmod(os.path.join(dest, MANIFEST_NAME), 0o444)
    os.chmod(dest, 0o500)
    man_bytes = open(os.path.join(dest, MANIFEST_NAME), "rb").read()
    return {
        "bundle_path": dest,
        "attempt_nonce": nonce,
        "raw_sha256": hashlib.sha256(raw_b).hexdigest(),
        "manifest_sha256": hashlib.sha256(man_bytes).hexdigest(),
        "final_head": final_head,
    }


def _st_expect_fail(failures, name, fn):
    try:
        fn()
    except VerifierError as exc:
        print("REJECT %s: %s" % (name, exc))
        return
    failures.append(name)
    print("UNEXPECTED_ACCEPT %s" % name)


def _st_expect_ok(failures, name, fn):
    try:
        fn()
        print("ACCEPT %s" % name)
    except Exception as exc:
        failures.append(name)
        print("UNEXPECTED_REJECT %s: %s" % (name, exc))


def _st_unlock(bundle):
    os.chmod(bundle, 0o700)
    for name in (RAW_NAME, MANIFEST_NAME):
        path = os.path.join(bundle, name)
        if os.path.isfile(path) and not os.path.islink(path):
            os.chmod(path, 0o600)


def _st_relock(bundle):
    for name in (RAW_NAME, MANIFEST_NAME):
        path = os.path.join(bundle, name)
        if os.path.isfile(path) and not os.path.islink(path):
            os.chmod(path, 0o444)
    os.chmod(bundle, 0o500)


def _st_write_manifest(bundle, manifest):
    man_path = os.path.join(bundle, MANIFEST_NAME)
    _st_unlock(bundle)
    os.remove(man_path)
    payload = (json.dumps(manifest, sort_keys=True) + "\n")
    write_exclusive_bytes(man_path, payload.encode("utf-8"))
    _st_relock(bundle)


def _st_drop(live, final_head, bundle, nonce):
    cleanup_task7_bundle(
        bundle, final_head, nonce, expected_path=bundle
    )
    if bundle in live:
        live.remove(bundle)


def _st_fresh(live, final_head, raw):
    bundle, manifest = create_task7_bundle(
        final_head, raw, 0, nonce=new_nonce()
    )
    handoff = make_task7_handoff(bundle, manifest)
    live.append(bundle)
    return bundle, manifest, handoff


def _st_load(bundle, handoff, **overrides):
    return load_task7_evidence(
        overrides.get("bundle_dir", bundle),
        overrides.get("final_head", handoff["final_head"]),
        overrides.get("attempt_nonce", handoff["attempt_nonce"]),
        overrides.get("raw_sha256", handoff["raw_sha256"]),
        overrides.get("manifest_sha256", handoff["manifest_sha256"]),
        overrides.get("bundle_path", handoff["bundle_path"]),
    )


def suite_producer_lifecycle(final_head, raw, failures, live, drop):
    class _Mem:
        def __init__(self):
            self.parts = []

        def write(self, data):
            self.parts.append(data)
            return len(data)

        def flush(self):
            return None

    def _produce_fail(name, point):
        produced_nonce = new_nonce()
        before = set(os.listdir("/tmp"))
        try:
            produce_task7_handoff(
                final_head,
                raw,
                0,
                stdout=_Mem(),
                fail_after=point,
                nonce=produced_nonce,
            )
            failures.append(name)
            print("UNEXPECTED_ACCEPT %s" % name)
        except Exception:
            leftover = [
                item
                for item in sorted(set(os.listdir("/tmp")) - before)
                if final_head in item and produced_nonce in item
            ]
            if leftover:
                failures.append(name)
                print("UNEXPECTED_ACCEPT %s still present" % name)
            else:
                print("REJECT %s: bundle absent" % name)
                print("CLEANUP_ABSENT")

    _produce_fail("produce_fail_make_handoff", "make_handoff")
    _produce_fail("produce_fail_loader", "loader")
    _produce_fail("produce_fail_tuple", "tuple")
    _produce_fail("produce_fail_serialize", "serialize")
    _produce_fail("produce_fail_write", "write")
    _produce_fail("produce_fail_flush", "flush")
    prod_nonce = new_nonce()
    prod_buf = _Mem()
    prod_h, _prod_ev = produce_task7_handoff(
        final_head, raw, 0, stdout=prod_buf, nonce=prod_nonce
    )
    live.append(prod_h["bundle_path"])
    parsed_prod = parse_task7_handoff("".join(prod_buf.parts), final_head)
    try:
        load_task7_evidence(
            parsed_prod["bundle_path"],
            parsed_prod["final_head"],
            parsed_prod["attempt_nonce"],
            parsed_prod["raw_sha256"],
            parsed_prod["manifest_sha256"],
            parsed_prod["bundle_path"],
        )
        print("ACCEPT producer_stdout_json")
    except Exception as exc:
        failures.append("producer_stdout_json")
        print("UNEXPECTED_REJECT producer_stdout_json: %s" % exc)
    drop(prod_h["bundle_path"], prod_nonce)


def suite_task9_rc(final_head, failures, live, fresh, drop):
    bundle, man, hon = fresh()
    payload = json.dumps(hon, sort_keys=True)

    def _ok_then_break(_handoff):
        os.chmod(bundle, 0o700)
        return "ok"

    try:
        run_task9_with_handoff_cleanup(payload, final_head, _ok_then_break)
        failures.append("main_ok_cleanup_fail")
        print("UNEXPECTED_ACCEPT main_ok_cleanup_fail")
    except VerifierError as exc:
        text = str(exc)
        if "cleanup failed" not in text or os.path.isdir(bundle) is False:
            failures.append("main_ok_cleanup_fail")
            print("UNEXPECTED_REJECT main_ok_cleanup_fail: %s" % exc)
        else:
            print("REJECT main_ok_cleanup_fail: %s" % exc)
            print("CLEANUP_FAILURE_NONZERO")
    if os.path.isdir(bundle):
        drop(bundle, man["attempt_nonce"])

    bundle, man, hon = fresh()
    payload = json.dumps(hon, sort_keys=True)

    def _main_fail(_handoff):
        raise VerifierError("main work failed")

    try:
        run_task9_with_handoff_cleanup(payload, final_head, _main_fail)
        failures.append("main_fail_cleanup_ok")
        print("UNEXPECTED_ACCEPT main_fail_cleanup_ok")
    except VerifierError as exc:
        if str(exc) != "main work failed" or os.path.exists(bundle):
            failures.append("main_fail_cleanup_ok")
            print("UNEXPECTED_REJECT main_fail_cleanup_ok: %s" % exc)
        else:
            print("REJECT main_fail_cleanup_ok: preserved main rc")
            print("CLEANUP_ABSENT")
    if bundle in live:
        live.remove(bundle)

    bundle, man, hon = fresh()
    payload = json.dumps(hon, sort_keys=True)

    def _exit5(_handoff):
        raise SystemExit(5)

    try:
        run_task9_with_handoff_cleanup(payload, final_head, _exit5)
        failures.append("main_exit_cleanup_ok")
        print("UNEXPECTED_ACCEPT main_exit_cleanup_ok")
    except SystemExit as exc:
        if exc.code != 5 or os.path.exists(bundle):
            failures.append("main_exit_cleanup_ok")
            print("UNEXPECTED_REJECT main_exit_cleanup_ok: %s" % exc)
        else:
            print("REJECT main_exit_cleanup_ok: preserved exit 5")
            print("CLEANUP_ABSENT")
    except Exception as exc:
        failures.append("main_exit_cleanup_ok")
        print("UNEXPECTED_REJECT main_exit_cleanup_ok: %s" % exc)
    if bundle in live:
        live.remove(bundle)

    bundle, man, hon = fresh()
    payload = json.dumps(hon, sort_keys=True)

    def _both_fail(_handoff):
        os.chmod(bundle, 0o700)
        raise VerifierError("main work failed")

    try:
        run_task9_with_handoff_cleanup(payload, final_head, _both_fail)
        failures.append("main_fail_cleanup_fail")
        print("UNEXPECTED_ACCEPT main_fail_cleanup_fail")
    except VerifierError as exc:
        text = str(exc)
        both = "main failed" in text and "cleanup failed" in text
        if not both or os.path.isdir(bundle) is False:
            failures.append("main_fail_cleanup_fail")
            print("UNEXPECTED_REJECT main_fail_cleanup_fail: %s" % exc)
        else:
            print("REJECT main_fail_cleanup_fail: %s" % exc)
            print("BOTH_FAILED")
    if os.path.isdir(bundle):
        drop(bundle, man["attempt_nonce"])


def suite_cleanup_refusal(final_head, failures, fresh, drop, unlock, relock):
    def _cleanup_refuse(name, mutate):
        bundle, man, hon = fresh()
        decoy = None
        try:
            decoy = mutate(bundle, hon)
            cleanup_task7_handoff(hon, final_head)
            failures.append(name)
            print("UNEXPECTED_ACCEPT %s" % name)
        except VerifierError as exc:
            target = decoy or bundle
            if not os.path.isdir(target):
                failures.append(name)
                print("UNEXPECTED_REJECT %s deleted: %s" % (name, exc))
            else:
                print("REJECT %s: %s" % (name, exc))
                print("CLEANUP_REFUSED")
        if decoy and os.path.isdir(decoy):
            os.chmod(decoy, 0o700)
            os.rmdir(decoy)
        if os.path.isdir(bundle):
            unlock(bundle)
            extra = os.path.join(bundle, "extra.txt")
            if os.path.isfile(extra):
                os.chmod(extra, 0o600)
                os.remove(extra)
            drop(bundle, man["attempt_nonce"])

    bundle, man, hon = fresh()
    real_geteuid = os.geteuid
    os.geteuid = lambda: real_geteuid() + 1
    try:
        cleanup_task7_handoff(hon, final_head)
        failures.append("cleanup_owner")
        print("UNEXPECTED_ACCEPT cleanup_owner")
    except VerifierError as exc:
        if "owner" not in str(exc) or not os.path.isdir(bundle):
            failures.append("cleanup_owner")
            print("UNEXPECTED_REJECT cleanup_owner: %s" % exc)
        else:
            print("REJECT cleanup_owner: %s" % exc)
            print("CLEANUP_REFUSED")
    finally:
        os.geteuid = real_geteuid
    if os.path.isdir(bundle):
        drop(bundle, man["attempt_nonce"])

    def _mut_mode(bundle, _hon):
        os.chmod(bundle, 0o700)

    def _mut_extra(bundle, _hon):
        unlock(bundle)
        write_exclusive_bytes(os.path.join(bundle, "extra.txt"), b"x\n")
        relock(bundle)

    def _mut_missing(bundle, _hon):
        unlock(bundle)
        os.remove(os.path.join(bundle, RAW_NAME))
        os.chmod(bundle, 0o500)

    def _mut_raw(bundle, hon):
        hon["raw_sha256"] = "0" * 64

    def _mut_man(_bundle, hon):
        hon["manifest_sha256"] = "0" * 64

    def _mut_nonce(_bundle, hon):
        hon["attempt_nonce"] = "0" * 32

    def _mut_head(_bundle, hon):
        hon["final_head"] = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"

    def _mut_path(bundle, hon):
        decoy = bundle + "-pathdecoy"
        os.mkdir(decoy, 0o700)
        hon["bundle_path"] = decoy
        return decoy

    _cleanup_refuse("cleanup_mode", _mut_mode)
    _cleanup_refuse("cleanup_extra_entry", _mut_extra)
    _cleanup_refuse("cleanup_missing_entry", _mut_missing)
    _cleanup_refuse("cleanup_raw_hash", _mut_raw)
    _cleanup_refuse("cleanup_manifest_hash", _mut_man)
    _cleanup_refuse("cleanup_nonce", _mut_nonce)
    _cleanup_refuse("cleanup_head", _mut_head)
    _cleanup_refuse("cleanup_bundle_path", _mut_path)


def suite_object_identity(final_head, raw, failures, live, fresh, drop):
    bundle, man, hon = fresh()
    reloc = bundle + "-reloc"
    os.rename(bundle, reloc)
    try:
        cleanup_task7_handoff(hon, final_head)
        failures.append("relocated_original_cleanup")
        print("UNEXPECTED_ACCEPT relocated_original_cleanup")
    except VerifierError:
        if os.path.isdir(reloc) and not os.path.exists(bundle):
            print("REJECT relocated_original_cleanup")
            print("ORIGINAL_REMAINS_AND_CLEANUP_NONZERO")
        else:
            failures.append("relocated_original_cleanup")
            print("UNEXPECTED_REJECT relocated_original_cleanup")
    if os.path.isdir(reloc):
        cleanup_partial_create(reloc, final_head, man["attempt_nonce"])
    if bundle in live:
        live.remove(bundle)

    bundle, man, hon = fresh()
    reloc = bundle + "-orig"
    os.rename(bundle, reloc)
    _valid_lookalike(bundle, final_head, man["attempt_nonce"], raw, bundle)
    try:
        cleanup_task7_handoff(hon, final_head)
        failures.append("byte_identical_path_swap")
        print("UNEXPECTED_ACCEPT byte_identical_path_swap")
    except VerifierError:
        if os.path.isdir(bundle) and os.path.isdir(reloc):
            print("REJECT byte_identical_path_swap")
            print("DECOY_REMAINS")
            print("ORIGINAL_REMAINS")
            print("CLEANUP_NONZERO")
        else:
            failures.append("byte_identical_path_swap")
            print("UNEXPECTED_REJECT byte_identical_path_swap")
    _force_rm_bundle(bundle)
    if os.path.isdir(reloc):
        cleanup_partial_create(reloc, final_head, man["attempt_nonce"])
    if bundle in live:
        live.remove(bundle)

    bundle, man, hon = fresh()
    reloc = bundle + "-orig"
    fired = []
    real_fchmod = os.fchmod

    def swap_then_fchmod(fd, mode):
        if not fired:
            fired.append(1)
            os.rename(bundle, reloc)
            _valid_lookalike(
                bundle, final_head, man["attempt_nonce"], raw, bundle,
            )
        return real_fchmod(fd, mode)

    os.fchmod = swap_then_fchmod
    try:
        cleanup_task7_handoff(hon, final_head)
        failures.append("post_final_identity_check_swap")
        print("UNEXPECTED_ACCEPT post_final_identity_check_swap")
    except VerifierError:
        raw_left = os.path.isfile(os.path.join(reloc, RAW_NAME))
        if os.path.isdir(bundle) and not raw_left:
            print("REJECT post_final_identity_check_swap")
            print("DECOY_REMAINS")
            print("ORIGINAL_RAW_NOT_LEFT")
            print("CLEANUP_NONZERO")
        else:
            failures.append("post_final_identity_check_swap")
            print("UNEXPECTED_REJECT post_final_identity_check_swap")
    finally:
        os.fchmod = real_fchmod
    _force_rm_bundle(bundle)
    if os.path.isdir(reloc):
        cleanup_partial_create(reloc, final_head, man["attempt_nonce"])
    if bundle in live:
        live.remove(bundle)

    bundle, man, hon = fresh()
    reloc = bundle + "-prerm"
    fired = []
    real_lstat = os.lstat

    def swap_then_lstat(path, *args, **kwargs):
        same = os.path.abspath(path) == os.path.abspath(bundle)
        if same and not fired:
            try:
                names = os.listdir(path)
            except OSError:
                names = None
            if names == []:
                fired.append(1)
                os.rename(bundle, reloc)
                _valid_lookalike(
                    bundle,
                    final_head,
                    man["attempt_nonce"],
                    raw,
                    bundle,
                )
        return real_lstat(path, *args, **kwargs)

    os.lstat = swap_then_lstat
    try:
        cleanup_task7_handoff(hon, final_head)
        failures.append("pre_rmdir_path_swap")
        print("UNEXPECTED_ACCEPT pre_rmdir_path_swap")
    except VerifierError:
        if os.path.isdir(bundle):
            print("REJECT pre_rmdir_path_swap")
            print("DECOY_REMAINS")
            print("CLEANUP_NONZERO")
        else:
            failures.append("pre_rmdir_path_swap")
            print("UNEXPECTED_REJECT pre_rmdir_path_swap")
    finally:
        os.lstat = real_lstat
    _force_rm_bundle(bundle)
    if os.path.isdir(reloc):
        cleanup_partial_create(reloc, final_head, man["attempt_nonce"])
    if bundle in live:
        live.remove(bundle)

    bundle, man, hon = fresh()
    try:
        cleanup_task7_handoff(hon, final_head)
        if os.path.exists(bundle):
            failures.append("original_bundle_cleanup")
            print("UNEXPECTED_ACCEPT original_bundle_cleanup still present")
        else:
            print("ACCEPT original_bundle_cleanup")
            print("CLEANUP_ABSENT")
    except Exception as exc:
        failures.append("original_bundle_cleanup")
        print("UNEXPECTED_REJECT original_bundle_cleanup: %s" % exc)
    if bundle in live:
        live.remove(bundle)

    real_b, real_m, real_h = fresh()
    decoy_nonce = real_m["attempt_nonce"]
    decoy = "/tmp/pr28-task7-%s-%s-decoy" % (final_head, decoy_nonce)
    look = _valid_lookalike(decoy, final_head, decoy_nonce, raw, decoy)
    decoy_h = dict(look)
    decoy_h["bundle_dev"] = real_h["bundle_dev"]
    decoy_h["bundle_ino"] = real_h["bundle_ino"]
    try:
        cleanup_task7_handoff(decoy_h, final_head)
        failures.append("coordinated_decoy_cleanup")
        print("UNEXPECTED_ACCEPT coordinated_decoy_cleanup")
    except VerifierError as exc:
        if os.path.isdir(decoy) and os.path.isdir(real_b):
            print("REJECT coordinated_decoy_cleanup: %s" % exc)
            print("DECOY_REMAINS")
        else:
            failures.append("coordinated_decoy_cleanup")
            print("UNEXPECTED_REJECT coordinated_decoy_cleanup deleted")
    _force_rm_bundle(decoy)
    if os.path.isdir(real_b):
        drop(real_b, decoy_nonce)


def suite_pr_body_parser(final_head, evidence, failures):
    _st_expect_fail(
        failures,
        "empty_headings",
        lambda: assert_pr_body(
            "## Motivation\n\n## Changes\n\n## Tests\n\n## SSOT integrity\n\n## Governance\n",
            final_head,
            evidence,
        ),
    )
    _st_expect_fail(
        failures,
        "fenced_headings",
        lambda: assert_pr_body(
            "```\n" + _valid_body(final_head, evidence) + "\n```\n",
            final_head,
            evidence,
        ),
    )
    _st_expect_fail(
        failures,
        "extra_h2",
        lambda: assert_pr_body(
            _valid_body(final_head, evidence, extra_h2="## Extra"),
            final_head,
            evidence,
        ),
    )
    _st_expect_fail(
        failures,
        "duplicate_heading",
        lambda: assert_pr_body(
            _valid_body(final_head, evidence) + "\n## Motivation\nmore\n",
            final_head,
            evidence,
        ),
    )
    reordered = _reordered_body(final_head, evidence)
    _st_expect_fail(
        failures,
        "reordered_headings",
        lambda: assert_pr_body(reordered, final_head, evidence),
    )
    missing = _valid_body(final_head, evidence).replace(
        "external_focused_passed = 176\n", ""
    )
    _st_expect_fail(
        failures,
        "missing_required_fact",
        lambda: assert_pr_body(missing, final_head, evidence),
    )
    adversarial = (
        "PR17 not rewritten; PR19 rewritten;\n"
        "no cherry-pick; rebase, squash and manual conflict resolution performed."
    )
    _st_expect_fail(
        failures,
        "pr17_false_pr19_true",
        lambda: assert_pr_body(
            _valid_body(final_head, evidence, changes=adversarial),
            final_head,
            evidence,
        ),
    )
    mixed = dict(CHANGES_FACTS)
    mixed["pr19_history_rewritten"] = "true"
    mixed_text = "\n".join("%s = %s" % item for item in mixed.items())
    _st_expect_fail(
        failures,
        "pr19_rewritten_true",
        lambda: assert_pr_body(
            _valid_body(final_head, evidence, changes=mixed_text),
            final_head,
            evidence,
        ),
    )
    mixed2 = dict(CHANGES_FACTS)
    mixed2["rebase_used"] = "true"
    mixed2["squash_used"] = "true"
    mixed2["manual_conflict_commit_used"] = "true"
    mixed2_text = "\n".join("%s = %s" % item for item in mixed2.items())
    _st_expect_fail(
        failures,
        "no_cherrypick_but_other_rewrites",
        lambda: assert_pr_body(
            _valid_body(final_head, evidence, changes=mixed2_text),
            final_head,
            evidence,
        ),
    )
    _st_expect_fail(
        failures,
        "invented_warning",
        lambda: assert_pr_body(
            _valid_body(
                final_head,
                evidence,
                tests_overlay={
                    "root_warning_count": "999",
                    "root_warning_types": "InventedWarning",
                },
            ),
            final_head,
            evidence,
        ),
    )

    _st_expect_fail(
        failures,
        "bare_h2",
        lambda: assert_pr_body(
            _valid_body(final_head, evidence) + "\n##\n",
            final_head,
            evidence,
        ),
    )
    _st_expect_fail(
        failures,
        "tab_extra_h2",
        lambda: assert_pr_body(
            _valid_body(final_head, evidence) + "\n##\tExtra\n",
            final_head,
            evidence,
        ),
    )
    four_open = "````\n" + _valid_body(final_head, evidence) + "\n```\n"
    _st_expect_fail(
        failures,
        "four_backtick_open_three_close",
        lambda: assert_pr_body(four_open, final_head, evidence),
    )
    _st_expect_fail(
        failures,
        "unclosed_backtick_fence",
        lambda: assert_pr_body(
            "```\n" + _valid_body(final_head, evidence),
            final_head,
            evidence,
        ),
    )
    _st_expect_fail(
        failures,
        "unclosed_tilde_fence",
        lambda: assert_pr_body(
            "~~~\n" + _valid_body(final_head, evidence),
            final_head,
            evidence,
        ),
    )
    changes_plus_prose = (
        "\n".join("%s = %s" % item for item in CHANGES_FACTS.items())
        + "\nrebase was used.\nmanual conflict commit was used.\n"
    )
    _st_expect_fail(
        failures,
        "canonical_changes_plus_contradictory_prose",
        lambda: assert_pr_body(
            _valid_body(final_head, evidence, changes=changes_plus_prose),
            final_head,
            evidence,
        ),
    )
    prose_tests = _valid_body(final_head, evidence).replace(
        "root_warning_types = PytestCollectionWarning\n",
        "root_warning_types = PytestCollectionWarning\nwarnings were 999 InventedWarning.\n",
    )
    _st_expect_fail(
        failures,
        "canonical_tests_plus_invented_warning_prose",
        lambda: assert_pr_body(prose_tests, final_head, evidence),
    )

    tab_motivation = _valid_body(final_head, evidence).replace(
        "## Motivation\n", "##\tMotivation\n", 1
    )
    _st_expect_ok(
        failures,
        "tab_motivation_heading",
        lambda: assert_pr_body(tab_motivation, final_head, evidence),
    )
    closing_hash = _valid_body(final_head, evidence).replace(
        "## Tests\n", "## Tests ##\n", 1
    )
    _st_expect_ok(
        failures,
        "legal_atx_closing_sequence",
        lambda: assert_pr_body(closing_hash, final_head, evidence),
    )
    _st_expect_ok(
        failures,
        "valid_body_and_evidence",
        lambda: assert_pr_body(_valid_body(final_head, evidence), final_head, evidence),
    )


def suite_ci_discovery_wait_rollup(final_head, failures):
    pending = {
        "headSha": final_head,
        "status": "in_progress",
        "conclusion": "",
        "url": "https://example.test/run/1",
        "jobs": [_required_job(2, "in_progress", "")],
    }
    pending_result = wait_for_terminal(
        lambda _rid: pending,
        1,
        final_head,
        FakeClock(),
        completion_seconds=30,
        poll_seconds=15,
    )
    if not pending_result.get("expired"):
        failures.append("permanent_pending")
        print("UNEXPECTED_ACCEPT permanent_pending")
    else:
        print("REJECT permanent_pending: COMPLETION_DEADLINE_EXPIRED")

    dup_jobs = {
        "headSha": final_head,
        "status": "in_progress",
        "conclusion": "",
        "jobs": [
            _required_job(2, "in_progress", ""),
            _required_job(3, "in_progress", ""),
        ],
    }
    _st_expect_fail(
        failures,
        "duplicate_required_jobs",
        lambda: wait_for_terminal(
            lambda _rid: dup_jobs,
            1,
            final_head,
            FakeClock(),
            completion_seconds=30,
            poll_seconds=15,
        ),
    )
    missing_job = {
        "headSha": final_head,
        "status": "completed",
        "conclusion": "success",
        "jobs": [],
    }
    _st_expect_fail(
        failures,
        "missing_job_on_terminal_run",
        lambda: wait_for_terminal(
            lambda _rid: missing_job,
            1,
            final_head,
            FakeClock(),
            completion_seconds=30,
            poll_seconds=15,
        ),
    )
    _st_expect_fail(
        failures,
        "unrelated_rollup",
        lambda: assert_rollup_bound(
            {
                "headRefOid": final_head,
                "statusCheckRollup": [{
                    "workflowName": "other",
                    "name": "unrelated",
                    "status": "COMPLETED",
                    "conclusion": "SUCCESS",
                    "detailsUrl": "https://github.com/%s/actions/runs/1/job/2" % REPO,
                }],
            },
            final_head,
            1,
            2,
        ),
    )
    _st_expect_fail(
        failures,
        "duplicate_required_rollup",
        lambda: assert_rollup_bound(
            {
                "headRefOid": final_head,
                "statusCheckRollup": [
                    _required_rollup(1, 2),
                    _required_rollup(1, 2),
                ],
            },
            final_head,
            1,
            2,
        ),
    )
    _st_expect_fail(
        failures,
        "old_url",
        lambda: assert_rollup_bound(
            {
                "headRefOid": final_head,
                "statusCheckRollup": [_required_rollup(999, 888)],
            },
            final_head,
            1,
            2,
        ),
    )
    for conclusion in ("FAILURE", "CANCELLED", "STALE", "SKIPPED"):
        _st_expect_fail(
        failures,
            "rollup_%s" % conclusion.lower(),
            lambda c=conclusion: assert_rollup_bound(
                {
                    "headRefOid": final_head,
                    "statusCheckRollup": [_required_rollup(1, 2, conclusion=c)],
                },
                final_head,
                1,
                2,
            ),
        )
    _st_expect_fail(
        failures,
        "pending_rollup",
        lambda: assert_rollup_bound(
            {
                "headRefOid": final_head,
                "statusCheckRollup": [_required_rollup(1, 2, status="IN_PROGRESS", conclusion="")],
            },
            final_head,
            1,
            2,
        ),
    )

    success = {
        "headSha": final_head,
        "status": "completed",
        "conclusion": "success",
        "url": "https://example.test/run/1",
        "jobs": [_required_job(2, "completed", "success")],
    }
    _st_expect_ok(
        failures,
        "valid_wait",
        lambda: (
            None
            if wait_for_terminal(
                lambda _rid: success,
                1,
                final_head,
                FakeClock(),
                completion_seconds=30,
                poll_seconds=15,
            ).get("state")
            == "C"
            else (_ for _ in ()).throw(VerifierError("expected C"))
        ),
    )
    _st_expect_ok(
        failures,
        "valid_rollup",
        lambda: assert_rollup_bound(
            {
                "headRefOid": final_head,
                "statusCheckRollup": [_required_rollup(1, 2)],
            },
            final_head,
            1,
            2,
        ),
    )


def suite_raw_manifest_mutation(final_head, raw, failures, live):
    bundle, manifest, handoff = _st_fresh(live, final_head, raw)
    raw_path = os.path.join(bundle, RAW_NAME)
    _st_unlock(bundle)
    with open(raw_path, "ab") as handle:
        handle.write(b"\nTAMPER\n")
    _st_relock(bundle)
    _st_expect_fail(
        failures,
        "raw_changed_manifest_unchanged",
        lambda: _st_load(bundle, handoff),
    )
    _st_drop(live, final_head, bundle, manifest["attempt_nonce"])

    bundle, manifest, handoff = _st_fresh(live, final_head, raw)
    tampered = dict(manifest)
    tampered["warning_count"] = 999
    tampered["warning_types"] = ["InventedWarning"]
    _st_write_manifest(bundle, tampered)
    _st_expect_fail(
        failures,
        "manifest_warning_changed_raw_unchanged",
        lambda: _st_load(bundle, handoff),
    )
    _st_drop(live, final_head, bundle, manifest["attempt_nonce"])

    bundle, manifest, handoff = _st_fresh(live, final_head, raw)
    bad_hash = dict(manifest)
    bad_hash["raw_sha256"] = "0" * 64
    _st_write_manifest(bundle, bad_hash)
    _st_expect_fail(failures, "wrong_raw_sha256", lambda: _st_load(bundle, handoff))
    _st_drop(live, final_head, bundle, manifest["attempt_nonce"])

    bundle, manifest, handoff = _st_fresh(live, final_head, raw)
    bad_size = dict(manifest)
    bad_size["raw_size"] = int(manifest["raw_size"]) + 7
    _st_write_manifest(bundle, bad_size)
    _st_expect_fail(failures, "wrong_raw_size", lambda: _st_load(bundle, handoff))
    _st_drop(live, final_head, bundle, manifest["attempt_nonce"])

    bundle, manifest, handoff = _st_fresh(live, final_head, raw)
    _st_expect_fail(
        failures,
        "wrong_final_head",
        lambda: _st_load(
            bundle,
            handoff,
            final_head="bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        ),
    )
    _st_drop(live, final_head, bundle, manifest["attempt_nonce"])

    bundle, manifest, handoff = _st_fresh(live, final_head, raw)
    bad_nonce = dict(manifest)
    bad_nonce["attempt_nonce"] = "0" * 32
    _st_write_manifest(bundle, bad_nonce)
    _st_expect_fail(failures, "wrong_nonce", lambda: _st_load(bundle, handoff))
    _st_drop(live, final_head, bundle, manifest["attempt_nonce"])

    bundle, manifest, handoff = _st_fresh(live, final_head, raw)
    missing_field = dict(manifest)
    del missing_field["attempt_nonce"]
    _st_write_manifest(bundle, missing_field)
    _st_expect_fail(failures, "missing_manifest_field", lambda: _st_load(bundle, handoff))
    extra_field = dict(manifest)
    extra_field["unexpected"] = "x"
    _st_write_manifest(bundle, extra_field)
    _st_expect_fail(
        failures,
        "duplicate_or_extra_manifest_field",
        lambda: _st_load(bundle, handoff),
    )
    dup_json = (
        '{"schema_version":"1","final_head":"%s","final_head":"%s",'
        '"attempt_nonce":"%s","command":"%s","exit":0,"collected":1693,'
        '"passed":1693,"failed":0,"warning_count":10,'
        '"warning_types":["PytestCollectionWarning"],'
        '"raw_sha256":"%s","raw_size":%s,"bundle_path":"%s"}'
        % (
            final_head,
            final_head,
            manifest["attempt_nonce"],
            TASK7_COMMAND,
            manifest["raw_sha256"],
            manifest["raw_size"],
            bundle,
        )
    )
    _st_unlock(bundle)
    man_path = os.path.join(bundle, MANIFEST_NAME)
    os.remove(man_path)
    write_exclusive_bytes(man_path, (dup_json + "\n").encode("utf-8"))
    _st_relock(bundle)
    _st_expect_fail(failures, "duplicate_manifest_field", lambda: _st_load(bundle, handoff))
    _st_drop(live, final_head, bundle, manifest["attempt_nonce"])


def suite_manifest_schema(final_head, raw, failures, live):
    def _schema_fail(name, mutate):
        bundle, manifest, handoff = _st_fresh(live, final_head, raw)
        bad = dict(manifest)
        mutate(bad)
        _st_write_manifest(bundle, bad)
        current = make_task7_handoff(bundle, bad)
        _st_expect_fail(failures, name, lambda: _st_load(bundle, current))
        _st_drop(live, final_head, bundle, manifest["attempt_nonce"])

    _schema_fail("numeric_string_exit", lambda bad: bad.__setitem__("exit", "0"))
    _schema_fail(
        "bool_integer_collected",
        lambda bad: bad.__setitem__("collected", True),
    )
    _schema_fail(
        "object_warning_types",
        lambda bad: bad.__setitem__("warning_types", {"W": 1}),
    )
    _schema_fail(
        "string_warning_types",
        lambda bad: bad.__setitem__("warning_types", "PytestCollectionWarning"),
    )
    _schema_fail(
        "mixed_warning_types",
        lambda bad: bad.__setitem__(
            "warning_types", ["PytestCollectionWarning", 1]
        ),
    )
    _schema_fail(
        "malformed_nonce",
        lambda bad: bad.__setitem__("attempt_nonce", "xyz"),
    )
    _schema_fail(
        "malformed_raw_sha256",
        lambda bad: bad.__setitem__("raw_sha256", "0" * 63),
    )
    _schema_fail(
        "malformed_final_head",
        lambda bad: bad.__setitem__("final_head", "A" * 40),
    )
    _schema_fail(
        "wrong_command",
        lambda bad: bad.__setitem__("command", "wrong"),
    )
    _schema_fail(
        "wrong_schema_version",
        lambda bad: bad.__setitem__("schema_version", "9"),
    )


def suite_handoff_path_guards(final_head, raw, failures, live):
    real_bundle, real_man, real_h = _st_fresh(live, final_head, raw)
    link_bundle = "/tmp/pr28-task7-link-%s" % new_nonce()
    os.symlink(real_bundle, link_bundle)
    _st_expect_fail(
        failures,
        "symlink_bundle",
        lambda: _st_load(
            link_bundle,
            real_h,
            bundle_dir=link_bundle,
            bundle_path=link_bundle,
        ),
    )
    if os.path.islink(link_bundle):
        os.unlink(link_bundle)
    raw_real = os.path.join(real_bundle, RAW_NAME)
    raw_backup = raw_real + ".bak"
    _st_unlock(real_bundle)
    os.rename(raw_real, raw_backup)
    os.symlink(raw_backup, raw_real)
    os.chmod(real_bundle, 0o500)
    _st_expect_fail(failures, "symlink_file", lambda: _st_load(real_bundle, real_h))
    os.chmod(real_bundle, 0o700)
    os.unlink(raw_real)
    os.rename(raw_backup, raw_real)
    _st_relock(real_bundle)
    _st_drop(live, final_head, real_bundle, real_man["attempt_nonce"])

    bundle, manifest, handoff = _st_fresh(live, final_head, raw)
    os.chmod(bundle, 0o700)
    os.chmod(os.path.join(bundle, RAW_NAME), 0o644)
    os.chmod(bundle, 0o500)
    _st_expect_fail(failures, "wrong_mode", lambda: _st_load(bundle, handoff))
    _st_drop(live, final_head, bundle, manifest["attempt_nonce"])

    bundle, manifest, handoff = _st_fresh(live, final_head, raw)
    reloc = "/tmp/pr28-task7-%s-%s-reloc" % (
        final_head,
        manifest["attempt_nonce"],
    )
    _st_unlock(bundle)
    os.rename(bundle, reloc)
    os.chmod(reloc, 0o500)
    _st_expect_fail(
        failures,
        "relocated_bundle",
        lambda: _st_load(reloc, handoff, bundle_dir=reloc),
    )
    _st_drop(live, final_head, reloc, manifest["attempt_nonce"])
    if bundle in live:
        live.remove(bundle)

    bundle, manifest, handoff = _st_fresh(live, final_head, raw)
    coord = dict(manifest)
    coord["attempt_nonce"] = new_nonce()
    coord["bundle_path"] = "/tmp/pr28-task7-%s-%s-coord" % (
        final_head,
        coord["attempt_nonce"],
    )
    _st_write_manifest(bundle, coord)
    _st_expect_fail(
        failures,
        "coordinated_nonce_path_tamper",
        lambda: _st_load(bundle, handoff),
    )
    _st_drop(live, final_head, bundle, manifest["attempt_nonce"])

    bundle, manifest, handoff = _st_fresh(live, final_head, raw)
    _st_unlock(bundle)
    write_exclusive_bytes(os.path.join(bundle, "extra.txt"), b"x\n")
    _st_relock(bundle)
    _st_expect_fail(failures, "extra_directory_entry", lambda: _st_load(bundle, handoff))
    _st_unlock(bundle)
    extra_path = os.path.join(bundle, "extra.txt")
    if os.path.isfile(extra_path):
        os.chmod(extra_path, 0o600)
        os.remove(extra_path)
    _st_drop(live, final_head, bundle, manifest["attempt_nonce"])

    bundle, manifest, handoff = _st_fresh(live, final_head, raw)
    _st_unlock(bundle)
    os.remove(os.path.join(bundle, RAW_NAME))
    os.chmod(bundle, 0o500)
    _st_expect_fail(failures, "missing_directory_entry", lambda: _st_load(bundle, handoff))
    _st_drop(live, final_head, bundle, manifest["attempt_nonce"])

    bundle, manifest, handoff = _st_fresh(live, final_head, raw)
    decoy = "/tmp/pr28-task7-%s-%s-decoy" % (
        final_head,
        manifest["attempt_nonce"],
    )
    os.mkdir(decoy, 0o700)
    cleanup_task7_bundle(
        bundle, final_head, manifest["attempt_nonce"], expected_path=bundle
    )
    if os.path.isdir(decoy) and not os.path.exists(bundle):
        print("ACCEPT decoy_not_deleted")
        os.rmdir(decoy)
        if bundle in live:
            live.remove(bundle)
    else:
        failures.append("decoy_not_deleted")
        print("UNEXPECTED_REJECT decoy_not_deleted")
        if os.path.isdir(decoy):
            os.rmdir(decoy)

    injected_nonce = new_nonce()
    created_before = set(os.listdir("/tmp"))
    try:
        create_task7_bundle(final_head, raw, 0, nonce=injected_nonce, fail_after="raw")
        failures.append("partial_failure_cleanup")
        print("UNEXPECTED_ACCEPT partial_failure_cleanup")
    except VerifierError:
        created_after = set(os.listdir("/tmp"))
        leftovers = [
            name
            for name in sorted(created_after - created_before)
            if final_head in name and injected_nonce in name
        ]
        if leftovers:
            failures.append("partial_failure_cleanup")
            print("UNEXPECTED_ACCEPT partial_failure_cleanup still present")
        else:
            print("REJECT partial_failure_cleanup: bundle absent")
            print("CLEANUP_ABSENT")


def suite_same_head_retry(final_head, raw, failures, live):
    first, first_man, first_h = _st_fresh(live, final_head, raw)
    second, second_man, second_h = _st_fresh(live, final_head, raw)
    if (
        first == second
        or first_h["attempt_nonce"] == second_h["attempt_nonce"]
        or os.path.basename(first) == os.path.basename(second)
    ):
        failures.append("same_head_retry_nonce")
        print("UNEXPECTED_REJECT same_head_retry_nonce")
    else:
        _st_load(first, first_h)
        _st_load(second, second_h)
        print("ACCEPT same_head_retry_nonce")
    _st_expect_fail(
        failures,
        "old_handoff_rejects_new_bundle",
        lambda: load_task7_evidence(
            second_h["bundle_path"],
            first_h["final_head"],
            first_h["attempt_nonce"],
            first_h["raw_sha256"],
            first_h["manifest_sha256"],
            first_h["bundle_path"],
        ),
    )
    _st_drop(live, final_head, first, first_man["attempt_nonce"])
    _st_drop(live, final_head, second, second_man["attempt_nonce"])
    if os.path.exists(first) or os.path.exists(second):
        failures.append("same_head_retry_cleanup")
        print("UNEXPECTED_ACCEPT same_head_retry_cleanup still present")
    else:
        print("CLEANUP_ABSENT")


def suite_manifest_handoff(final_head, raw, failures, live):
    suite_raw_manifest_mutation(final_head, raw, failures, live)
    suite_manifest_schema(final_head, raw, failures, live)
    suite_handoff_path_guards(final_head, raw, failures, live)
    suite_same_head_retry(final_head, raw, failures, live)


def suite_lifecycle_orchestration(final_head, raw, failures, live):
    def fresh():
        return _st_fresh(live, final_head, raw)

    def drop(bundle, nonce):
        _st_drop(live, final_head, bundle, nonce)

    round_bundle, round_man, round_h = _st_fresh(live, final_head, raw)
    text = json.dumps(round_h, sort_keys=True)
    parsed = parse_task7_handoff(text, final_head)
    _st_expect_ok(
        failures,
        "valid_raw_manifest_round_trip",
        lambda: load_task7_evidence(
            parsed["bundle_path"],
            parsed["final_head"],
            parsed["attempt_nonce"],
            parsed["raw_sha256"],
            parsed["manifest_sha256"],
            parsed["bundle_path"],
        ),
    )
    _st_expect_ok(
        failures,
        "handoff_through_task9_load",
        lambda: load_task7_evidence(
            parsed["bundle_path"],
            parsed["final_head"],
            parsed["attempt_nonce"],
            parsed["raw_sha256"],
            parsed["manifest_sha256"],
            parsed["bundle_path"],
        ),
    )
    if os.path.isdir(round_bundle):
        print("ACCEPT success_retained_until_consumption")
    else:
        failures.append("success_retained_until_consumption")
        print("UNEXPECTED_REJECT success_retained_until_consumption")

    def _consume(h):
        return load_task7_evidence(
            h["bundle_path"],
            h["final_head"],
            h["attempt_nonce"],
            h["raw_sha256"],
            h["manifest_sha256"],
            h["bundle_path"],
        )

    run_task9_with_handoff_cleanup(text, final_head, _consume)
    if os.path.exists(round_bundle):
        failures.append("success_final_cleanup")
        print("UNEXPECTED_ACCEPT success_final_cleanup still present")
    else:
        print("CLEANUP_ABSENT")
        if round_bundle in live:
            live.remove(round_bundle)

    def _inject(name, work):
        bundle, _manifest, hon = _st_fresh(live, final_head, raw)
        payload = json.dumps(hon, sort_keys=True)
        try:
            run_task9_with_handoff_cleanup(payload, final_head, work)
            failures.append(name)
            print("UNEXPECTED_ACCEPT %s" % name)
        except (VerifierError, SystemExit):
            if os.path.exists(bundle):
                failures.append(name)
                print("UNEXPECTED_ACCEPT %s still present" % name)
            else:
                print("REJECT %s: bundle absent" % name)
                print("CLEANUP_ABSENT")
        if bundle in live:
            live.remove(bundle)

    def _body_fail(handoff):
        ev = load_task7_evidence(
            handoff["bundle_path"],
            handoff["final_head"],
            handoff["attempt_nonce"],
            handoff["raw_sha256"],
            handoff["manifest_sha256"],
            handoff["bundle_path"],
        )
        assert_pr_body("## Extra\nbad\n", final_head, ev)

    def _discovery_fail(_handoff):
        selected = select_newest_final_head_run([], final_head)
        if selected is None:
            raise VerifierError("discovery timeout")

    def _wait_fail(_handoff):
        def get_detail(_rid):
            return {
                "headSha": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                "status": "in_progress",
                "jobs": [],
            }

        return wait_for_terminal(
            get_detail,
            1,
            final_head,
            FakeClock(),
            completion_seconds=30,
            poll_seconds=15,
        )

    def _d_state(_handoff):
        def get_detail(_rid):
            return {
                "headSha": final_head,
                "status": "completed",
                "conclusion": "failure",
                "jobs": [_required_job(2, "completed", "failure")],
            }

        result = wait_for_terminal(
            get_detail,
            1,
            final_head,
            FakeClock(),
            completion_seconds=30,
            poll_seconds=15,
        )
        if result.get("state") == "D":
            raise VerifierError("CI_STATE=D")
        raise VerifierError("expected D")

    def _rollup_fail(_handoff):
        assert_rollup_bound(
            {"headRefOid": final_head, "statusCheckRollup": []},
            final_head,
            1,
            2,
        )

    def _loader_fail(handoff):
        return load_task7_evidence(
            handoff["bundle_path"],
            handoff["final_head"],
            "0" * 32,
            handoff["raw_sha256"],
            handoff["manifest_sha256"],
            handoff["bundle_path"],
        )

    _inject("body_failure_cleanup", _body_fail)
    _inject("discovery_timeout_cleanup", _discovery_fail)
    _inject("wait_failure_cleanup", _wait_fail)
    _inject("d_state_cleanup", _d_state)
    _inject("rollup_failure_cleanup", _rollup_fail)
    _inject("loader_failure_cleanup", _loader_fail)
    suite_producer_lifecycle(final_head, raw, failures, live, drop)
    suite_task9_rc(final_head, failures, live, fresh, drop)
    suite_cleanup_refusal(
        final_head, failures, fresh, drop, _st_unlock, _st_relock
    )
    suite_object_identity(final_head, raw, failures, live, fresh, drop)


def run_verifier_self_test():
    final_head = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    evidence = _valid_evidence(final_head)
    raw = sample_task7_raw()
    failures = []
    live = []
    suite_pr_body_parser(final_head, evidence, failures)
    suite_ci_discovery_wait_rollup(final_head, failures)
    suite_manifest_handoff(final_head, raw, failures, live)
    suite_lifecycle_orchestration(
        final_head, raw, failures, live
    )
    leftovers = [path for path in live if os.path.exists(path)]
    if leftovers:
        failures.append("self_test_leftover_bundles")
        print("UNEXPECTED_ACCEPT leftover %s" % leftovers)
    if failures:
        print("VERIFIER_SELF_TEST_FAILED", ",".join(failures))
        raise SystemExit(1)
    print("VERIFIER_SELF_TEST_OK")
# === VERIFIER_LIB_END ===
```

`NON_SUCCESS` is consumed by `is_non_success_conclusion`, which
fail-closes rollup conclusions and identifies D-state
non-success terminals. It is not dead data.

Required body facts. Heading presence alone does not prove them.

```text
unfenced H2 sequence ==
## Motivation
## Changes
## Tests
## SSOT integrity
## Governance
each section body is non-empty
no extra unfenced H2

Motivation:
authoritative
RED
RED head = e62974af4f5e2cfbc65d98c3b2f028edce57d25c
RED run = 32449925094
RED job = 96676383508
PR18 source head = 4b21072add365923799dccc057d4fefffd69918c
dynamically computed FINAL_HEAD

Changes section may contain only blank lines and these
canonical keys, each once, exact values. Any other line fails:
merge.count = 1
merge.mode = --no-ff
merge.source_branch = cursor/p3-compiler-alias-ci-repair-c46c
merge.source_head = 4b21072add365923799dccc057d4fefffd69918c
merge.message = merge: integrate residual CMakeCache CI repair
pr17_history_rewritten = false
pr19_history_rewritten = false
cherry_pick_used = false
rebase_used = false
squash_used = false
manual_conflict_commit_used = false

Tests section may contain only blank lines and these
canonical keys, each once. Any other line fails:
external_focused_passed = 176
compile_commands_passed = 1
cmakecache_passed = 1
pilot_file_passed = 75
root_collected = 1693
root_passed = 1693
root_failed = 0
root_exit = 0
root_warning_count = <Task 7 evidence.warning_count>
root_warning_types = <Task 7 evidence.warning_types>
banned tokens fail

SSOT integrity:
scripts/build_paper_numbers.py
not run
not applicable to history-only integration

Governance:
PR #28 remains OPEN
PR #28 remains draft
PR_READY_AUTHORIZED=false
MAIN_PR_MERGE_AUTHORIZED=false
MERGE_AUTHORIZED=false
REAL_QUALIFICATION_AUTHORIZED=false
ATTEMPT_2_AUTHORIZED=false
CLAIMS_AUTHORIZED=false
FORMAL_DENOMINATOR_MEMBERSHIP=false
```

- [ ] **Step 0: Run the extractable verifier self-test**

This step uses `FakeClock`. It must run before any live
`gh pr view` or CI wait. A failed self-test is a stop.

```bash
/usr/bin/python3 - <<'PY'
from pathlib import Path

plan = Path("docs/superpowers/plans/2026-08-21-pr17-pr19-ci-integration.md").read_text()
begin = "#" + " === VERIFIER_LIB_BEGIN ==="
end_mark = "#" + " === VERIFIER_LIB_END ==="
start = plan.index(begin)
end = plan.index(end_mark) + len(end_mark)
ns = {}
exec(plan[start:end], ns)
ns["run_verifier_self_test"]()
PY
```

Required: `VERIFIER_SELF_TEST_OK` and exit 0. Do not continue to
Step 1 if this fails.

- [ ] **Step 1: Freeze FINAL_HEAD and update the existing draft**

```bash
FINAL_HEAD="$(git rev-parse HEAD)"
echo "FINAL_HEAD=$FINAL_HEAD"
```

Keep pull request 28 OPEN and draft. Do not mark-ready. Do not
merge. Do not edit pull request 17, 18, or 19. Write the five
unfenced headings and the canonical Changes / Tests keys,
including `FINAL_HEAD` in Motivation and the Task 7 warning
fields in Tests.

- [ ] **Step 2: Re-read pull request 28 and run the body verifier**

```bash
gh pr view 28 \
  --repo meng004/P3-Semantic-Mutation \
  --json number,state,isDraft,baseRefName,headRefName,headRefOid,body,url,statusCheckRollup
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

```bash
FINAL_HEAD="$(git rev-parse HEAD)"
export FINAL_HEAD
if [ -z "${TASK7_HANDOFF_JSON:-}" ]; then
  echo "TASK7_HANDOFF_JSON missing; do not glob or guess"
  exit 1
fi
/usr/bin/python3 - <<'PY'
import json
import os
import subprocess
import sys
from pathlib import Path

final_head = os.environ["FINAL_HEAD"]
plan = Path("docs/superpowers/plans/2026-08-21-pr17-pr19-ci-integration.md").read_text()
begin = "#" + " === VERIFIER_LIB_BEGIN ==="
end_mark = "#" + " === VERIFIER_LIB_END ==="
start = plan.index(begin)
end = plan.index(end_mark) + len(end_mark)
ns = {}
exec(plan[start:end], ns)
handoff = ns["parse_task7_handoff"](
    os.environ["TASK7_HANDOFF_JSON"], final_head
)
try:
    evidence = ns["load_task7_evidence"](
        handoff["bundle_path"],
        handoff["final_head"],
        handoff["attempt_nonce"],
        handoff["raw_sha256"],
        handoff["manifest_sha256"],
        handoff["bundle_path"],
    )
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
    assert pr["number"] == 28
    assert pr["state"] == "OPEN"
    assert pr["isDraft"] is True
    assert pr["baseRefName"] == "main"
    assert pr["headRefName"] == "cursor/pr17-pr19-ci-integration-c46c"
    assert pr["headRefOid"] == final_head
    ns["assert_pr_body"](pr["body"], final_head, evidence)
    print("PR28_BODY_FACTS_OK")
    print("FINAL_HEAD", final_head)
    print("headRefOid", pr["headRefOid"])
except BaseException:
    ns["cleanup_task7_handoff"](handoff, final_head)
    if os.path.exists(handoff["bundle_path"]):
        print("CLEANUP_LEFT_BUNDLE")
        sys.exit(1)
    raise
PY
```

`headRefOid != FINAL_HEAD` is a stop. Missing Task 7 evidence is
a stop. A body that only has the five headings is a stop.

- [ ] **Step 3: Discover, wait with a completion deadline, and bind rollup**

Select the newest `sanity-check` run whose `headSha` equals
`FINAL_HEAD`. Do not accept a green run from any other commit,
including run `32539725403` if it belongs to an earlier head.

```bash
FINAL_HEAD="$(git rev-parse HEAD)"
export FINAL_HEAD
if [ -z "${TASK7_HANDOFF_JSON:-}" ]; then
  echo "TASK7_HANDOFF_JSON missing; do not glob or guess"
  exit 1
fi
task9_cleanup() {
  /usr/bin/python3 - <<'PY'
import os
from pathlib import Path

final_head = os.environ["FINAL_HEAD"]
plan = Path("docs/superpowers/plans/2026-08-21-pr17-pr19-ci-integration.md").read_text()
begin = "#" + " === VERIFIER_LIB_BEGIN ==="
end_mark = "#" + " === VERIFIER_LIB_END ==="
start = plan.index(begin)
end = plan.index(end_mark) + len(end_mark)
ns = {}
exec(plan[start:end], ns)
handoff = ns["parse_task7_handoff"](
    os.environ["TASK7_HANDOFF_JSON"], final_head
)
ns["cleanup_task7_handoff"](handoff, final_head)
if os.path.exists(handoff["bundle_path"]):
    raise SystemExit("CLEANUP_LEFT_BUNDLE")
print("TASK7_CLEANED")
PY
}
trap task9_cleanup EXIT
set +e
/usr/bin/python3 - <<'PY'
import json
import os
import subprocess
import sys
from pathlib import Path

final_head = os.environ["FINAL_HEAD"]
plan = Path("docs/superpowers/plans/2026-08-21-pr17-pr19-ci-integration.md").read_text()
begin = "#" + " === VERIFIER_LIB_BEGIN ==="
end_mark = "#" + " === VERIFIER_LIB_END ==="
start = plan.index(begin)
end = plan.index(end_mark) + len(end_mark)
ns = {}
exec(plan[start:end], ns)

REPO = ns["REPO"]
DISCOVERY_SECONDS = ns["DISCOVERY_SECONDS"]
COMPLETION_SECONDS = ns["COMPLETION_SECONDS"]
POLL_SECONDS = ns["POLL_SECONDS"]
clock = ns["RealClock"]()


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
            final_head,
            "--limit",
            "20",
            "--json",
            "databaseId,headSha,status,conclusion,createdAt,url",
        ]
    )
    return json.loads(raw)


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


def work(handoff):
    raw_body = subprocess.check_output(
        [
            "gh",
            "pr",
            "view",
            "28",
            "--repo",
            REPO,
            "--json",
            "body,headRefOid",
        ]
    )
    body_pr = json.loads(raw_body)
    evidence0 = ns["load_task7_evidence"](
        handoff["bundle_path"],
        handoff["final_head"],
        handoff["attempt_nonce"],
        handoff["raw_sha256"],
        handoff["manifest_sha256"],
        handoff["bundle_path"],
    )
    ns["assert_pr_body"](body_pr["body"], final_head, evidence0)
    discovery_deadline = clock.monotonic() + DISCOVERY_SECONDS
    selected = None
    while clock.monotonic() < discovery_deadline and selected is None:
        selected = ns["select_newest_final_head_run"](list_runs(), final_head)
        if selected is None:
            print("CI_STATE=A no FINAL_HEAD sanity-check yet")
            clock.sleep(POLL_SECONDS)

    if selected is None:
        print("CI_STATE=A discovery window expired")
        print("FINAL_HEAD", final_head)
        sys.exit(2)

    run_id = selected["databaseId"]
    print("DISCOVERED_RUN", run_id, selected.get("url"))
    print("CI_STATE", ns["classify"](selected))

    try:
        result = ns["wait_for_terminal"](
            view_run,
            run_id,
            final_head,
            clock,
            completion_seconds=COMPLETION_SECONDS,
            poll_seconds=POLL_SECONDS,
        )
    except ns["VerifierError"] as exc:
        print("WAIT_FAILED", exc)
        print("stop; do not edit, re-merge, re-push, mark-ready, or merge main")
        sys.exit(4)

    if result.get("expired"):
        print(ns["format_timeout"](result))
        sys.exit(7)

    detail = result["detail"]
    job = result["job"]
    if job is None:
        print("required job missing after wait")
        print("FINAL_HEAD", final_head)
        print("run.id", run_id)
        print("run.url", detail.get("url"))
        print("run.status", detail.get("status"))
        print("run.conclusion", detail.get("conclusion"))
        sys.exit(4)

    job_id = job.get("databaseId") or job.get("id")
    print("CI_STATE", result["state"])
    print("run.status", detail.get("status"))
    print("run.conclusion", detail.get("conclusion"))
    print("run.headSha", detail.get("headSha"))
    print("run.url", detail.get("url"))
    print("job.name", job.get("name"))
    print("job.status", job.get("status"))
    print("job.conclusion", job.get("conclusion"))
    print("job.url", job.get("url"))

    if result["state"] != "C":
        print("CI_STATE=D or non-success terminal")
        print("run.id", run_id)
        print("run.url", detail.get("url"))
        print("job.id", job_id)
        print("job.url", job.get("url"))
        cmd = ns["failure_log_command"](run_id, job_id)
        print("EVIDENCE_CMD", " ".join(cmd))
        try:
            log = subprocess.check_output(
                cmd, text=True, stderr=subprocess.STDOUT
            )
            print(log)
        except subprocess.CalledProcessError as exc:
            print(exc.output)
        print("record first failure and collected/passed/failed/exit/warning counts")
        print("stop; do not edit, re-merge, re-push, mark-ready, or merge main")
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
    try:
        ns["assert_rollup_bound"](
            pr,
            final_head,
            run_id,
            job_id,
            job_url=job.get("url"),
        )
    except ns["VerifierError"] as exc:
        print("ROLLUP_BIND_FAILED", exc)
        sys.exit(6)

    evidence = ns["load_task7_evidence"](
        handoff["bundle_path"],
        handoff["final_head"],
        handoff["attempt_nonce"],
        handoff["raw_sha256"],
        handoff["manifest_sha256"],
        handoff["bundle_path"],
    )
    print("TASK7_BUNDLE", evidence["bundle_path"])
    print("TASK7_RAW_SHA256", evidence["raw_sha256"])
    print("TASK7_MANIFEST_SHA256", evidence["manifest_sha256"])
    print("FINAL_HEAD_CI_OK")
    print("RUN_ID", run_id)
    print("JOB_ID", job_id)
    return evidence


ns["run_task9_with_handoff_cleanup"](
    os.environ["TASK7_HANDOFF_JSON"], final_head, work
)
PY
main_rc=$?
trap - EXIT
exit "$main_rc"
```

Required after the wait:

```text
run.status = completed
run.conclusion = success
run.headSha = FINAL_HEAD
job.name = Run pytest (Path-A cache replay smoke)
job.status = completed
job.conclusion = success
headRefOid = FINAL_HEAD
exactly one rollup CheckRun:
workflowName = sanity-check
name = Run pytest (Path-A cache replay smoke)
status = COMPLETED
conclusion = SUCCESS
detailsUrl bound to /actions/runs/{run_id}/job/{job_id}
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

On a non-success terminal run the executor must run:

```bash
gh run view "$RUN_ID" \
  --repo meng004/P3-Semantic-Mutation \
  --job "$JOB_ID" \
  --log-failed
```

and return the first failure plus collected, passed, failed, exit,
and warning counts. Then stop. Do not modify code, re-merge,
re-push, mark-ready, or merge main.

Only after self-test, pull-request metadata, structured body
facts bound to Task 7 evidence, FINAL_HEAD CI state C, and a
rollup bound to that run and job all pass may the later executor
stop for Sol implementation review. Do not write an
implementation verdict.

---

## Stop Conditions

A later implementation node must stop immediately when:

- the isolated alias `IMPLEMENTATION_ENTRY` still appears;
- parent 1 is not the Sol-written
  `INTEGRATION_IMPLEMENTATION_ENTRY`;
- `run_verifier_self_test` fails;
- the unfenced H2 sequence is not exactly the five required
  titles, including extra, missing, duplicate, or reordered H2;
- headings are only inside a fence or only proven by
  `assert heading in body`;
- any required section body is empty;
- Changes or Tests contain any non-blank line that is not a
  known canonical `key = value` fact, including contradictory
  prose such as `rebase was used.` or
  `warnings were 999 InventedWarning.`;
- Changes lacks a canonical key, repeats a key, or uses a value
  other than the frozen false/exact merge facts;
- Task 7 evidence is not one `tempfile.mkdtemp(dir="/tmp")`
  private directory whose prefix contains `FINAL_HEAD`;
- Task 7 evidence uses glob, latest-mtime, a fixed symlink, or
  a guessed directory instead of the exact returned path;
- Task 7 evidence is missing `root.raw` or `manifest.json`, or
  the directory contains any other name;
- `manifest.json` lacks, repeats, or invents fields outside
  `schema_version`, `final_head`, `attempt_nonce`, `command`,
  `exit`, `collected`, `passed`, `failed`, `warning_count`,
  `warning_types`, `raw_sha256`, `raw_size`, and `bundle_path`;
- any integer field is a numeric string or bool, or
  `warning_types` is not a JSON array of strings;
- `FINAL_HEAD`, nonce, or SHA-256 values are not lowercase hex
  of the required length;
- `command` is not
  `PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1`;
- Task 7 evidence bundle or file is a symlink, has the wrong
  owner or mode, or is not read-only after create;
- the parent shell has no `TASK7_HANDOFF_JSON` object with
  exactly `bundle_path`, `attempt_nonce`, `raw_sha256`,
  `manifest_sha256`, `final_head`, `bundle_dev`, and
  `bundle_ino`;
- cleanup treats a missing, relocated, or replaced captured
  path as success, deletes a lookalike, re-selects
  `root.raw` / `manifest.json` by pathname after the handle
  check, rmdirs a pathname that is no longer the original,
  or skips the create-time directory object identity;
- Task 9 loads from a path or nonce that is only self-consistent
  with its own manifest and is not the independently captured
  handoff;
- raw bytes, SHA-256, size, parsed tuples, handed-off values,
  and manifest fields do not all bind one another and
  `FINAL_HEAD`;
- Task 9 consumes a bundle from another `FINAL_HEAD` or nonce,
  a relocated path, or an old same-HEAD handoff;
- a partial Task 7 failure, or any post-create producer
  failure, leaves its exact `mkdtemp` directory behind, or
  cleanup uses glob, an empty path, `/tmp`, a relocated path,
  or a wide recursive delete;
- Task 7 does not run create, make handoff, load, tuple check,
  serialize, and stdout write/flush through one protected
  producer `try`/`finally`;
- Task 9 body, discovery, wait, D-state, rollup, load, success,
  or any exception/`SystemExit` skips
  `run_task9_with_handoff_cleanup`;
- Task 9 treats an EXIT-trap return status as the only
  success signal, or main success plus cleanup failure exits 0;
- handoff cleanup deletes a path that failed owner, mode,
  entry, hash, schema, head, nonce, or `bundle_path`
  validation, or deletes a coordinated matching-name decoy;
- a same-`FINAL_HEAD` retry reuses a nonce, directory, or
  handoff, or a failed attempt blocks a new attempt;
- PR17 and PR19 rewritten flags are not independently `false`;
- cherry-pick, rebase, squash, or manual conflict flags are not
  independently `false`;
- Tests canonical keys do not equal the frozen focused counts
  plus Task 7 evidence fields;
- `root_warning_count` / `root_warning_types` do not equal the
  exclusive-created Task 7 evidence for this `FINAL_HEAD`;
- Task 7 evidence is missing, reused, or not exclusive-created;
- pull request 28 `headRefOid` is not `FINAL_HEAD`;
- no FINAL_HEAD `sanity-check` run appears before
  `DISCOVERY_SECONDS = 600`;
- the selected FINAL_HEAD run or required job is still
  non-terminal when `COMPLETION_SECONDS = 3600` expires;
- the wait loop has no completion deadline;
- two jobs share `REQUIRED_JOB`;
- a terminal run has zero `REQUIRED_JOB` matches;
- the FINAL_HEAD run or job has any non-success terminal
  conclusion;
- `statusCheckRollup` is empty;
- `statusCheckRollup` is non-empty but unrelated, duplicate and
  ambiguous, pending, failed, cancelled, stale, skipped, or bound
  to an older run or job;
- the executor cannot prove the run, job, pull-request head, and
  rollup `detailsUrl` all bind `FINAL_HEAD` and the selected
  `run_id` / `job_id`;
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

## Self-Review Record

- Finding 1 remains closed. Task 1, Task 4 Post-Merge Required,
  Stop Conditions, and Governance Stop still use
  `INTEGRATION_IMPLEMENTATION_ENTRY` as the only future-entry
  name. Isolated `IMPLEMENTATION_ENTRY` is a stop. `parent 1`
  must equal the Sol-written SHA verbatim. `parent 2` remains
  `4b21072add365923799dccc057d4fefffd69918c`.
- H2-sequence finding is closed. The parser collects every
  unfenced line-start ATX H2 and requires the exact five-title
  sequence. Extra `## Extra`, duplicates, reorder, fence-only,
  and empty sections fail.
- Changes-negation finding is closed. Changes uses unique
  canonical keys. PR17, PR19, cherry-pick, rebase, squash, and
  manual conflict are independently `false`. The prose fixture
  `PR17 not rewritten; PR19 rewritten; no cherry-pick; rebase,
  squash and manual conflict resolution performed.` is a reject.
- Fence-length finding is closed. The parser records fence
  character and opener length `>= 3`. A closer must use the
  same character, length `>=` opener, and only legal leading
  or trailing spaces. A four-backtick opener is not closed by
  three backticks. An unclosed fence fails. Bare `##` and
  `##\tExtra` are extra H2 titles. `##\tMotivation` and a
  legal ATX closing sequence normalize to the required title.
  Required headings are documented outside any four-backtick
  fence.
- Canonical-only finding is closed. Changes and Tests reject
  any non-blank non-`key = value` line, including
  `rebase was used.` and `warnings were 999 InventedWarning.`
  even when the legal keys are also present.
- Warning-evidence finding is closed. Task 7 creates one
  `tempfile.mkdtemp(dir="/tmp")` private directory whose prefix
  contains `FINAL_HEAD` and an unpredictable `attempt_nonce`.
  The successful child writes one JSON handoff object to stdout.
  The parent captures it into `TASK7_HANDOFF_JSON`. Manifest
  includes `bundle_path`, so the manifest SHA-256 binds the
  exact path. Task 9 parses that object and passes every field
  to the loader as a separate expected value. Integer fields
  require `type(value) is int`. Directory entries must be
  exactly `root.raw` and `manifest.json`. Relocated paths,
  coordinated nonce/path tampers, extra files, and old
  same-HEAD handoffs fail. Task 7 post-create failures run
  through `produce_task7_handoff` and remove the exact path.
  Task 9 runs body, wait, and rollup through
  `run_task9_with_handoff_cleanup`. Handoff cleanup opens the
  captured directory no-follow, binds `fstat` to
  `bundle_dev` / `bundle_ino`, and performs enumerate, read,
  unlink, and rmdir relative to that handle. Path, copyable
  bytes, hash, mode, owner, and manifest are not enough. A
  missing or replaced captured path is a non-zero stop and
  does not delete the substitute. A coordinated matching-name
  decoy that already satisfies those early checks is refused
  when it is not the original object. Cleanup failure makes
  the real orchestration non-zero.
- Duplicate-job finding is closed. `wait_for_terminal` collects
  all `REQUIRED_JOB` matches. `len > 1` raises. Terminal
  `len == 0` raises. Non-terminal `len == 0` may wait. Only one
  match may be used. First-match job selection without a
  count check is gone.
- Self-test finding is closed. Task 9 Step 0 runs
  `run_verifier_self_test()` on `FakeClock` before live PR/CI.
  Existing H2, fence, reorder, and canonical-only tests remain.
  New fixtures reject numeric-string and bool integers, object
  or mixed `warning_types`, malformed nonce/SHA/head, wrong
  command/schema, relocated bundles, coordinated nonce/path
  tamper, extra or missing directory entries, and old same-HEAD
  handoffs. The Task 7 handoff object is parsed and loaded by
  Task 9. Success is retained until final consumption. Body,
  discovery, wait, D-state, rollup, and loader failures each
  prove the exact path absent by exercising those branches.
  Post-create producer failures at make handoff, loader,
  tuple, serialize, write, and flush prove exact-path
  absence. Main success plus cleanup failure is non-zero.
  Main failure plus cleanup success preserves the main rc.
  Main failure plus cleanup failure reports both. Owner,
  mode, extra/missing entry, raw hash, manifest hash, nonce,
  head, and `bundle_path` cleanup-validation failures refuse
  deletion.   Relocated original, byte-identical path swap,
  post-final-identity-check swap, pre-rmdir path swap, and a
  coordinated decoy that already satisfies mode 0500 / file
  0444 / owner / schema / hashes / path/head/nonce all reach
  object-identity refusal. Swap fixtures monkeypatch
  `os.fchmod` or `os.lstat`; they do not add a production
  hook. The original-bundle cleanup path still deletes the
  exact object and proves it absent. PR-body, CI wait/rollup,
  manifest/handoff, and lifecycle fixtures are named suites.
  The self-test entry only orchestrates those suites and the
  leftover-path teardown. They do not add a second source of
  truth. `VERIFIER_SELF_TEST_OK` requires every expected
  REJECT, every valid fixture ACCEPT, and cleanup paths
  absent.
- Object-identity control: create already `lstat`s the
  `mkdtemp` directory for owner/mode. Cleanup reuses that
  identity on the open directory handle. No second hash,
  manifest, or parallel gate. Failure mode: a lookalike at
  the captured path, or a missing/relocated captured path,
  raises, leaves the substitute, and still rmdirs the held
  original when validation already passed. The control is
  removable only if exclusive-create plus same-process fd
  ownership replace the Task 7 to Task 9 JSON handoff.
- Kept contracts: `DISCOVERY_SECONDS = 600`,
  `COMPLETION_SECONDS = 3600`, newest FINAL_HEAD run, four-way
  run/job/headRefOid/detailsUrl bind, atomic five-destination
  fetch, merge-base, source-head gates, 11 to 13 path set,
  current and combined test blobs, exactly one `--no-ff` merge,
  pull request 28 OPEN draft on `main`, design as semantic SSOT,
  and local-history versus main-PR merge separation.
- Design remains the semantic SSOT.
- Entry is fail-closed on an explicit Sol SHA and atomic
  five-destination fetch.
- Execution is not offered from this archival node.
