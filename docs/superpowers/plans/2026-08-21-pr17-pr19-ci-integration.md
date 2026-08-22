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

- [ ] **Step 1: Freeze FINAL_HEAD and exclusive-create evidence files**

```bash
FINAL_HEAD="$(git rev-parse HEAD)"
export FINAL_HEAD
echo "FINAL_HEAD=$FINAL_HEAD"
```

Evidence is a bundle directory
`/tmp/pr28-task7-{FINAL_HEAD}-{nonce}/` containing exclusive-created
`raw.txt` and `manifest.json`. The directory must not exist before
`os.mkdir`. Files are created with `O_CREAT|O_EXCL`. Symlinked
bundles or files are a stop. A later attempt on the same
`FINAL_HEAD` must use a new nonce and must not be blocked by the
earlier bundle. Any partial failure must delete the new bundle so
it is absent. The manifest binds `final_head`, `nonce`,
`raw_sha256`, `raw_size`, collected, passed, failed, exit,
`warning_count`, and `warning_types`. Task 9 loads that bundle
through `TASK7_BUNDLE` and compares Tests keys to the verified
manifest.

- [ ] **Step 2: Reproduce the Actions pytest command and keep its exit**

```bash
FINAL_HEAD="$(git rev-parse HEAD)"
export FINAL_HEAD
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
    bundle, manifest = ns["create_task7_bundle"](
        final_head, output, proc.returncode
    )
except Exception:
    print("TASK7_BUNDLE_FAILED")
    raise
print("TASK7_BUNDLE", bundle)
print("TASK7_NONCE", manifest["nonce"])
evidence = ns["load_task7_evidence"](bundle, final_head)
print(json.dumps(evidence, sort_keys=True))
if (
    evidence["collected"] != 1693
    or evidence["passed"] != 1693
    or evidence["failed"] != 0
    or evidence["exit"] != 0
):
    print("root tuple is not the planned 1693/1693/0/0 success")
    sys.exit(proc.returncode if proc.returncode != 0 else 1)
sys.exit(proc.returncode)
PY
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
including bare `##` and `##` plus tab text. Fence openers of
three or more backticks or tildes close only with the same
character and a mark at least as long as the opener. A
four-backtick opener is not closed by three backticks. Content
after an unclosed fence stays fenced. The required heading
sequence is:

```text
## Motivation
## Changes
## Tests
## SSOT integrity
## Governance
```

Extra unfenced H2 titles fail. Headings that appear only inside
fenced code, in ordinary sentences, or in inline code are not
section headings. Changes and Tests use unique canonical keys,
not natural-language heuristics. Tests warning fields must equal
the Task 7 parsed evidence for this `FINAL_HEAD`.

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
import shutil
import sys
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
FENCE_MARK = re.compile(r"^ {0,3}(`{3,}|~{3,})")
FACT_RE = re.compile(r"^([A-Za-z][A-Za-z0-9_.]*)\s*=\s*(.*?)\s*$")
MANIFEST_FIELDS = (
    "final_head",
    "nonce",
    "raw_sha256",
    "raw_size",
    "collected",
    "passed",
    "failed",
    "exit",
    "warning_count",
    "warning_types",
)
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
    return os.urandom(8).hex()


def task7_bundle_dir(final_head, nonce):
    return "/tmp/pr28-task7-%s-%s" % (final_head, nonce)


def write_exclusive(path, text, mode="w"):
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    fd = os.open(path, flags, 0o600)
    with os.fdopen(fd, mode) as handle:
        handle.write(text)


def reject_symlink(path, label):
    if os.path.islink(path):
        raise VerifierError("symlink %s" % label)


def cleanup_task7_bundle(bundle):
    if os.path.islink(bundle):
        os.unlink(bundle)
        return
    if os.path.isdir(bundle):
        shutil.rmtree(bundle)


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
    bundle = task7_bundle_dir(final_head, nonce)
    created = False
    try:
        reject_symlink(bundle, "bundle")
        os.mkdir(bundle)
        created = True
        raw_path = os.path.join(bundle, "raw.txt")
        man_path = os.path.join(bundle, "manifest.json")
        raw_bytes = raw_text.encode("utf-8")
        write_exclusive(raw_path, raw_text)
        if fail_after == "raw":
            raise VerifierError("injected failure after raw")
        parsed = parse_pytest_output(raw_text, exit_code, final_head)
        manifest = {
            "final_head": final_head,
            "nonce": nonce,
            "raw_sha256": hashlib.sha256(raw_bytes).hexdigest(),
            "raw_size": len(raw_bytes),
            "collected": parsed["collected"],
            "passed": parsed["passed"],
            "failed": parsed["failed"],
            "exit": parsed["exit"],
            "warning_count": parsed["warning_count"],
            "warning_types": list(parsed["warning_types"]),
        }
        write_exclusive(man_path, json.dumps(manifest, sort_keys=True) + "\n")
        return bundle, manifest
    except Exception:
        if created:
            cleanup_task7_bundle(bundle)
        raise


def load_task7_evidence(bundle_dir, expected_final_head):
    reject_symlink(bundle_dir, "bundle")
    if not os.path.isdir(bundle_dir):
        raise VerifierError("missing Task 7 bundle %s" % bundle_dir)
    raw_path = os.path.join(bundle_dir, "raw.txt")
    man_path = os.path.join(bundle_dir, "manifest.json")
    for path, label in ((raw_path, "raw"), (man_path, "manifest")):
        reject_symlink(path, label)
        if not os.path.isfile(path):
            raise VerifierError("missing %s" % label)
    raw_bytes = open(raw_path, "rb").read()
    raw_text = raw_bytes.decode("utf-8")
    manifest = json.loads(open(man_path, "r").read(), object_pairs_hook=_manifest_object)
    extra = set(manifest) - set(MANIFEST_FIELDS)
    missing = set(MANIFEST_FIELDS) - set(manifest)
    if extra or missing:
        raise VerifierError(
            "manifest fields missing=%s extra=%s" % (sorted(missing), sorted(extra))
        )
    if manifest["final_head"] != expected_final_head:
        raise VerifierError("wrong FINAL_HEAD")
    digest = hashlib.sha256(raw_bytes).hexdigest()
    if manifest["raw_sha256"] != digest:
        raise VerifierError("wrong raw_sha256")
    if int(manifest["raw_size"]) != len(raw_bytes):
        raise VerifierError("wrong raw_size")
    parsed = parse_pytest_output(raw_text, manifest["exit"], expected_final_head)
    for key in ("collected", "passed", "failed", "exit", "warning_count"):
        if parsed[key] != manifest[key] and parsed[key] != int(manifest[key]):
            raise VerifierError("manifest %s does not match raw" % key)
    if list(parsed["warning_types"]) != list(manifest["warning_types"]):
        raise VerifierError("manifest warning_types does not match raw")
    parsed["nonce"] = manifest["nonce"]
    parsed["raw_sha256"] = manifest["raw_sha256"]
    parsed["raw_size"] = manifest["raw_size"]
    return parsed


def iter_unfenced_lines(text):
    in_fence = False
    fence_char = None
    fence_len = 0
    for lineno, line in enumerate(text.splitlines(), 1):
        match = FENCE_MARK.match(line)
        if match:
            mark = match.group(1)
            char = mark[0]
            length = len(mark)
            rest = line[match.end():]
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
        yield lineno, line




def extract_h2_sections(body):
    found = []
    for lineno, line in iter_unfenced_lines(body):
        key = line.rstrip()
        if ATX_H2.match(key):
            found.append((lineno, key))
    names = [key for _lineno, key in found]
    if names != list(HEADINGS):
        raise VerifierError(
            "unfenced H2 sequence must equal HEADINGS exactly; got %s" % (names,)
        )
    sections = {key: [] for key in HEADINGS}
    current = None
    for _lineno, line in iter_unfenced_lines(body):
        key = line.rstrip()
        if ATX_H2.match(key):
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


def run_verifier_self_test():
    final_head = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    evidence = _valid_evidence(final_head)
    failures = []

    def expect_fail(name, fn):
        try:
            fn()
        except VerifierError as exc:
            print("REJECT %s: %s" % (name, exc))
            return
        failures.append(name)
        print("UNEXPECTED_ACCEPT %s" % name)

    def expect_ok(name, fn):
        try:
            fn()
            print("ACCEPT %s" % name)
        except Exception as exc:
            failures.append(name)
            print("UNEXPECTED_REJECT %s: %s" % (name, exc))

    expect_fail(
        "empty_headings",
        lambda: assert_pr_body(
            "## Motivation\n\n## Changes\n\n## Tests\n\n## SSOT integrity\n\n## Governance\n",
            final_head,
            evidence,
        ),
    )
    expect_fail(
        "fenced_headings",
        lambda: assert_pr_body("```\n" + _valid_body(final_head, evidence) + "\n```\n", final_head, evidence),
    )
    expect_fail(
        "extra_h2",
        lambda: assert_pr_body(
            _valid_body(final_head, evidence, extra_h2="## Extra"),
            final_head,
            evidence,
        ),
    )
    expect_fail(
        "duplicate_heading",
        lambda: assert_pr_body(
            _valid_body(final_head, evidence) + "\n## Motivation\nmore\n",
            final_head,
            evidence,
        ),
    )
    reordered = _reordered_body(final_head, evidence)
    expect_fail(
        "reordered_headings",
        lambda: assert_pr_body(reordered, final_head, evidence),
    )
    missing = _valid_body(final_head, evidence).replace(
        "external_focused_passed = 176\n", ""
    )
    expect_fail("missing_required_fact", lambda: assert_pr_body(missing, final_head, evidence))
    adversarial = (
        "PR17 not rewritten; PR19 rewritten;\n"
        "no cherry-pick; rebase, squash and manual conflict resolution performed."
    )
    expect_fail(
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
    expect_fail(
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
    expect_fail(
        "no_cherrypick_but_other_rewrites",
        lambda: assert_pr_body(
            _valid_body(final_head, evidence, changes=mixed2_text),
            final_head,
            evidence,
        ),
    )
    expect_fail(
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
    expect_fail(
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
    expect_fail(
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
    expect_fail(
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
    expect_fail(
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
    expect_fail(
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
        expect_fail(
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
    expect_fail(
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

    expect_fail(
        "bare_h2",
        lambda: assert_pr_body(
            _valid_body(final_head, evidence) + "\n##\n",
            final_head,
            evidence,
        ),
    )
    expect_fail(
        "tab_extra_h2",
        lambda: assert_pr_body(
            _valid_body(final_head, evidence) + "\n##\tExtra\n",
            final_head,
            evidence,
        ),
    )
    four_open = "````\n" + _valid_body(final_head, evidence) + "\n```\n"
    expect_fail(
        "four_backtick_open_three_close",
        lambda: assert_pr_body(four_open, final_head, evidence),
    )
    expect_fail(
        "unclosed_backtick_fence",
        lambda: assert_pr_body("```\n" + _valid_body(final_head, evidence), final_head, evidence),
    )
    expect_fail(
        "unclosed_tilde_fence",
        lambda: assert_pr_body("~~~\n" + _valid_body(final_head, evidence), final_head, evidence),
    )
    changes_plus_prose = (
        "\n".join("%s = %s" % item for item in CHANGES_FACTS.items())
        + "\nrebase was used.\nmanual conflict commit was used.\n"
    )
    expect_fail(
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
    expect_fail(
        "canonical_tests_plus_invented_warning_prose",
        lambda: assert_pr_body(prose_tests, final_head, evidence),
    )

    raw = sample_task7_raw()
    bundles = []

    def _write_manifest(bundle, manifest):
        man_path = os.path.join(bundle, "manifest.json")
        os.remove(man_path)
        write_exclusive(man_path, json.dumps(manifest, sort_keys=True) + "\n")

    bundle, manifest = create_task7_bundle(final_head, raw, 0, nonce=new_nonce())
    bundles.append(bundle)
    raw_path = os.path.join(bundle, "raw.txt")
    with open(raw_path, "ab") as handle:
        handle.write(b"\\nTAMPER\\n")
    expect_fail(
        "raw_changed_manifest_unchanged",
        lambda: load_task7_evidence(bundle, final_head),
    )
    cleanup_task7_bundle(bundle)
    bundles.pop()

    bundle, manifest = create_task7_bundle(final_head, raw, 0, nonce=new_nonce())
    bundles.append(bundle)
    tampered = dict(manifest)
    tampered["warning_count"] = 999
    tampered["warning_types"] = ["InventedWarning"]
    _write_manifest(bundle, tampered)
    expect_fail(
        "manifest_warning_changed_raw_unchanged",
        lambda: load_task7_evidence(bundle, final_head),
    )
    cleanup_task7_bundle(bundle)
    bundles.pop()

    bundle, manifest = create_task7_bundle(final_head, raw, 0, nonce=new_nonce())
    bundles.append(bundle)
    bad_hash = dict(manifest)
    bad_hash["raw_sha256"] = "0" * 64
    _write_manifest(bundle, bad_hash)
    expect_fail("wrong_raw_sha256", lambda: load_task7_evidence(bundle, final_head))
    cleanup_task7_bundle(bundle)
    bundles.pop()

    bundle, manifest = create_task7_bundle(final_head, raw, 0, nonce=new_nonce())
    bundles.append(bundle)
    bad_size = dict(manifest)
    bad_size["raw_size"] = int(manifest["raw_size"]) + 7
    _write_manifest(bundle, bad_size)
    expect_fail("wrong_raw_size", lambda: load_task7_evidence(bundle, final_head))
    cleanup_task7_bundle(bundle)
    bundles.pop()

    bundle, manifest = create_task7_bundle(final_head, raw, 0, nonce=new_nonce())
    bundles.append(bundle)
    expect_fail(
        "wrong_final_head",
        lambda: load_task7_evidence(bundle, "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"),
    )
    cleanup_task7_bundle(bundle)
    bundles.pop()

    bundle, manifest = create_task7_bundle(final_head, raw, 0, nonce=new_nonce())
    bundles.append(bundle)
    missing_field = dict(manifest)
    del missing_field["nonce"]
    _write_manifest(bundle, missing_field)
    expect_fail("missing_manifest_field", lambda: load_task7_evidence(bundle, final_head))
    extra_field = dict(manifest)
    extra_field["unexpected"] = "x"
    _write_manifest(bundle, extra_field)
    expect_fail("duplicate_or_extra_manifest_field", lambda: load_task7_evidence(bundle, final_head))
    dup_json = (
        '{"final_head":"%s","final_head":"%s","nonce":"%s",'
        '"raw_sha256":"%s","raw_size":%s,"collected":1693,"passed":1693,'
        '"failed":0,"exit":0,"warning_count":10,'
        '"warning_types":["PytestCollectionWarning"]}'
        % (
            final_head,
            final_head,
            manifest["nonce"],
            manifest["raw_sha256"],
            manifest["raw_size"],
        )
    )
    man_path = os.path.join(bundle, "manifest.json")
    os.remove(man_path)
    write_exclusive(man_path, dup_json + "\n")
    expect_fail("duplicate_manifest_field", lambda: load_task7_evidence(bundle, final_head))
    cleanup_task7_bundle(bundle)
    bundles.pop()

    staging = "/tmp/pr28-task7-symlink-staging-%s" % new_nonce()
    os.mkdir(staging)
    real_bundle, _man = create_task7_bundle(final_head, raw, 0, nonce=new_nonce())
    link_bundle = staging + "-link"
    os.symlink(real_bundle, link_bundle)
    expect_fail("symlink_bundle", lambda: load_task7_evidence(link_bundle, final_head))
    raw_real = os.path.join(real_bundle, "raw.txt")
    raw_backup = raw_real + ".bak"
    os.rename(raw_real, raw_backup)
    os.symlink(raw_backup, raw_real)
    expect_fail("symlink_file", lambda: load_task7_evidence(real_bundle, final_head))
    os.unlink(raw_real)
    os.rename(raw_backup, raw_real)
    cleanup_task7_bundle(real_bundle)
    os.unlink(link_bundle)
    os.rmdir(staging)

    injected_nonce = new_nonce()
    injected_bundle = task7_bundle_dir(final_head, injected_nonce)
    try:
        create_task7_bundle(final_head, raw, 0, nonce=injected_nonce, fail_after="raw")
        failures.append("partial_failure_cleanup")
        print("UNEXPECTED_ACCEPT partial_failure_cleanup")
    except VerifierError:
        if os.path.exists(injected_bundle):
            failures.append("partial_failure_cleanup")
            print("UNEXPECTED_ACCEPT partial_failure_cleanup still present")
        else:
            print("REJECT partial_failure_cleanup: bundle absent")
            print("CLEANUP_ABSENT")

    first, first_man = create_task7_bundle(final_head, raw, 0)
    second, second_man = create_task7_bundle(final_head, raw, 0)
    if first == second or first_man["nonce"] == second_man["nonce"]:
        failures.append("same_head_retry_nonce")
        print("UNEXPECTED_REJECT same_head_retry_nonce")
    else:
        load_task7_evidence(first, final_head)
        load_task7_evidence(second, final_head)
        print("ACCEPT same_head_retry_nonce")
    cleanup_task7_bundle(first)
    cleanup_task7_bundle(second)

    round_bundle, _round_man = create_task7_bundle(final_head, raw, 0)
    expect_ok(
        "valid_raw_manifest_round_trip",
        lambda: load_task7_evidence(round_bundle, final_head),
    )
    cleanup_task7_bundle(round_bundle)

    expect_ok(
        "valid_body_and_evidence",
        lambda: assert_pr_body(_valid_body(final_head, evidence), final_head, evidence),
    )
    success = {
        "headSha": final_head,
        "status": "completed",
        "conclusion": "success",
        "url": "https://example.test/run/1",
        "jobs": [_required_job(2, "completed", "success")],
    }
    expect_ok(
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
    expect_ok(
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
/usr/bin/python3 - <<'PY'
import json
import os
import subprocess
from pathlib import Path

final_head = os.environ["FINAL_HEAD"]
plan = Path("docs/superpowers/plans/2026-08-21-pr17-pr19-ci-integration.md").read_text()
begin = "#" + " === VERIFIER_LIB_BEGIN ==="
end_mark = "#" + " === VERIFIER_LIB_END ==="
start = plan.index(begin)
end = plan.index(end_mark) + len(end_mark)
ns = {}
exec(plan[start:end], ns)
bundle = os.environ["TASK7_BUNDLE"]
evidence = ns["load_task7_evidence"](bundle, final_head)
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
        log = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)
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

print("FINAL_HEAD_CI_OK")
print("RUN_ID", run_id)
print("JOB_ID", job_id)
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
- Task 7 evidence bundle is a symlink, a reused path, a wrong
  `raw_sha256` / `raw_size` / `FINAL_HEAD`, a tampered raw or
  manifest, or is not exclusive-created with a unique nonce;
- a partial Task 7 failure leaves a bundle behind;
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
- Fence-length finding is closed. Openers of three or more
  backticks or tildes close only on the same character with at
  least that length and no info string. A four-backtick opener
  is not closed by three backticks. Unclosed fences keep later
  headings fenced. Bare `##` and `##\tExtra` are extra H2
  titles. Required headings are documented outside any
  four-backtick fence.
- Canonical-only finding is closed. Changes and Tests reject
  any non-blank non-`key = value` line, including
  `rebase was used.` and `warnings were 999 InventedWarning.`
  even when the legal keys are also present.
- Warning-evidence finding is closed. Task 7 exclusive-creates
  a `{FINAL_HEAD}-{nonce}` bundle with `raw.txt` plus a
  manifest. Load verifies sha256, size, FINAL_HEAD, and
  raw-vs-manifest fields. Tamper, symlink, missing/duplicate
  fields, and leftover partial bundles fail. Same-HEAD retry
  uses a new nonce.
- Duplicate-job finding is closed. `wait_for_terminal` collects
  all `REQUIRED_JOB` matches. `len > 1` raises. Terminal
  `len == 0` raises. Non-terminal `len == 0` may wait. Only one
  match may be used. First-match job selection without a
  count check is gone.
- Self-test finding is closed. Task 9 Step 0 runs
  `run_verifier_self_test()` on `FakeClock` before live PR/CI.
  Existing negatives remain. New fixtures cover bare H2, tab
  H2, four-backtick/three-backtick mismatch, unclosed fences,
  true reorder, canonical-plus-prose, raw/manifest tamper,
  symlink, partial cleanup, and same-HEAD nonce retry.
  `duplicate_heading` and `reordered_headings` are separate.
  `VERIFIER_SELF_TEST_OK` requires every expected REJECT, the
  valid fixtures ACCEPT, and the cleanup fixture absent.
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
