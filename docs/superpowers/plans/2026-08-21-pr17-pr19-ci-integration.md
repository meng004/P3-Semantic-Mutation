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

Running `gh pr edit` is not a pass. `assert heading in body` is
not a pass. The later executor must extract the verifier library
below, re-read pull request 28, parse unfenced ATX `##` headings,
and machine-check every required section fact. Headings that
appear only inside fenced code, in ordinary sentences, or in
inline code are not section headings.

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

#### Verifier library

This library is the only body, wait-budget, and rollup authority.
Extract it from this file. Do not re-implement a heading-in-body
check.

```python
# === VERIFIER_LIB_BEGIN ===
import re
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
BANNED_TOKENS = re.compile(
    r"\b(TBD|TODO|FIXME|TBA|placeholder)\b",
    re.IGNORECASE,
)
WARN_COUNT = re.compile(
    r"\bwarn(?:ing)?s?\b\s*[:=]?\s*(\d+)",
    re.IGNORECASE,
)
WARN_TYPE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*Warning\b")
RUN_JOB_URL = re.compile(r"/actions/runs/(\d+)/job/(\d+)")


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


def iter_unfenced_lines(text):
    in_fence = False
    fence_token = None
    for lineno, line in enumerate(text.splitlines(), 1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            token = "```" if stripped.startswith("```") else "~~~"
            if not in_fence:
                in_fence = True
                fence_token = token
            elif stripped.startswith(fence_token):
                in_fence = False
                fence_token = None
            continue
        if in_fence:
            continue
        yield lineno, line


def extract_h2_sections(body):
    found = []
    for lineno, line in iter_unfenced_lines(body):
        key = line.rstrip()
        if key in HEADINGS:
            found.append((lineno, key))
    names = [key for _lineno, key in found]
    if names != list(HEADINGS):
        raise VerifierError(
            "headings must be exact unfenced ATX H2 titles, "
            "each once, in order; got %s" % (names,)
        )
    sections = {key: [] for key in HEADINGS}
    current = None
    for _lineno, line in iter_unfenced_lines(body):
        key = line.rstrip()
        if key in HEADINGS:
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


def _require(section_name, text, needle, exact=False):
    haystack = text if exact else text.lower()
    pin = needle if exact else needle.lower()
    if pin not in haystack:
        raise VerifierError("%s missing %r" % (section_name, needle))


def _require_re(section_name, text, pattern, label):
    if re.search(pattern, text, re.IGNORECASE | re.MULTILINE) is None:
        raise VerifierError("%s missing %s" % (section_name, label))


def assert_pr_body(body, final_head):
    if not re.fullmatch(r"[0-9a-f]{40}", final_head or ""):
        raise VerifierError("FINAL_HEAD must be a 40-character lowercase SHA")
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

    changes = sections["## Changes"]
    _require("Changes", changes, "--no-ff", exact=True)
    _require_re("Changes", changes, r"exactly one", "exactly one merge")
    _require("Changes", changes, SOURCE_BRANCH, exact=True)
    _require("Changes", changes, PR18_HEAD, exact=True)
    _require("Changes", changes, MERGE_MESSAGE, exact=True)
    _require_re("Changes", changes, r"not rewritten", "not rewritten")
    _require_re("Changes", changes, r"\b17\b", "PR 17")
    _require_re("Changes", changes, r"\b19\b", "PR 19")
    for term in ("cherry-pick", "rebase", "squash", "conflict"):
        _require("Changes", changes, term)
    _require_re("Changes", changes, r"\b(no|not|without)\b", "negation")

    tests = sections["## Tests"]
    if BANNED_TOKENS.search(tests):
        raise VerifierError("Tests contains a banned token")
    _require_re("Tests", tests, r"external[^\n]*176\s+passed", "external 176 passed")
    _require_re(
        "Tests",
        tests,
        r"compile_commands[^\n]*1\s+passed",
        "compile_commands 1 passed",
    )
    _require_re("Tests", tests, r"CMakeCache[^\n]*1\s+passed", "CMakeCache 1 passed")
    _require_re("Tests", tests, r"(pilot file|test_pilot_build)[^\n]*75\s+passed", "pilot 75 passed")
    _require_re("Tests", tests, r"collected\s+1693", "collected 1693")
    _require_re("Tests", tests, r"passed\s+1693", "passed 1693")
    _require_re("Tests", tests, r"failed\s+0", "failed 0")
    _require_re("Tests", tests, r"exit\s+0", "exit 0")
    warn = WARN_COUNT.search(tests)
    if warn is None:
        raise VerifierError("Tests missing numeric warning count")
    if WARN_TYPE.search(tests) is None:
        raise VerifierError("Tests missing warning types from the fresh run")

    ssot = sections["## SSOT integrity"]
    _require("SSOT integrity", ssot, "scripts/build_paper_numbers.py", exact=True)
    _require("SSOT integrity", ssot, "not run")
    _require("SSOT integrity", ssot, "not applicable")
    _require("SSOT integrity", ssot, "history-only")

    gov = sections["## Governance"]
    _require("Governance", gov, "OPEN")
    _require_re("Governance", gov, r"\bdraft\b", "draft")
    for flag in (
        "PR_READY_AUTHORIZED=false",
        "MAIN_PR_MERGE_AUTHORIZED=false",
        "MERGE_AUTHORIZED=false",
        "REAL_QUALIFICATION_AUTHORIZED=false",
        "ATTEMPT_2_AUTHORIZED=false",
        "CLAIMS_AUTHORIZED=false",
        "FORMAL_DENOMINATOR_MEMBERSHIP=false",
    ):
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
        job = next((item for item in jobs if item.get("name") == REQUIRED_JOB), None)
        run_state = classify(detail)
        job_state = classify(job) if job is not None else "B"
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
        "job.id %s" % (job.get("databaseId") or job.get("id")),
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
        if conclusion != "SUCCESS":
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
# === VERIFIER_LIB_END ===
```

Required body facts the verifier machine-checks after a fresh
`gh pr view`. Heading presence alone does not prove them.

```text
headings = exact unfenced ATX H2, each once, in this order:
## Motivation
## Changes
## Tests
## SSOT integrity
## Governance
each section body is non-empty

Motivation:
authoritative
RED
RED head = e62974af4f5e2cfbc65d98c3b2f028edce57d25c
RED run = 32449925094
RED job = 96676383508
PR18 source head = 4b21072add365923799dccc057d4fefffd69918c
dynamically computed FINAL_HEAD

Changes:
exactly one --no-ff
source branch = cursor/p3-compiler-alias-ci-repair-c46c
source head = 4b21072add365923799dccc057d4fefffd69918c
merge message = merge: integrate residual CMakeCache CI repair
PR #17 and PR #19 histories were not rewritten
no cherry-pick, rebase, squash or manual conflict commit

Tests:
external focused: 176 passed
compile_commands named test: 1 passed
CMakeCache named test: 1 passed
pilot file: 75 passed
planned successful root tuple:
collected 1693, passed 1693, failed 0, exit 0
numeric warning count
warning types from the future fresh run
banned tokens TBD / TODO / FIXME / TBA / placeholder fail

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

- [ ] **Step 1: Freeze FINAL_HEAD and update the existing draft**

```bash
FINAL_HEAD="$(git rev-parse HEAD)"
echo "FINAL_HEAD=$FINAL_HEAD"
```

Keep pull request 28 OPEN and draft. Do not mark-ready. Do not
merge. Do not edit pull request 17, 18, or 19. Write the five
unfenced headings and every required fact above, including the
dynamic `FINAL_HEAD` value in Motivation and the fresh root
warning count and warning types in Tests.

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
start = plan.index("# === VERIFIER_LIB_BEGIN ===")
end = plan.index("# === VERIFIER_LIB_END ===") + len("# === VERIFIER_LIB_END ===")
ns = {}
exec(plan[start:end], ns)
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
ns["assert_pr_body"](pr["body"], final_head)
print("PR28_BODY_FACTS_OK")
print("FINAL_HEAD", final_head)
print("headRefOid", pr["headRefOid"])
PY
```

`headRefOid != FINAL_HEAD` is a stop. A body that only has the
five headings is a stop.

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
start = plan.index("# === VERIFIER_LIB_BEGIN ===")
end = plan.index("# === VERIFIER_LIB_END ===") + len("# === VERIFIER_LIB_END ===")
ns = {}
exec(plan[start:end], ns)

REPO = ns["REPO"]
JOB_NAME = ns["REQUIRED_JOB"]
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

result = ns["wait_for_terminal"](
    view_run,
    run_id,
    final_head,
    clock,
    completion_seconds=COMPLETION_SECONDS,
    poll_seconds=POLL_SECONDS,
)
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

Only after pull-request metadata, structured body facts, FINAL_HEAD
CI state C, and a rollup bound to that run and job all pass may
the later executor stop for Sol implementation review. Do not
write an implementation verdict.

---

## Stop Conditions

A later implementation node must stop immediately when:

- the isolated alias `IMPLEMENTATION_ENTRY` still appears;
- parent 1 is not the Sol-written
  `INTEGRATION_IMPLEMENTATION_ENTRY`;
- pull request 28 body headings are missing, duplicated, out of
  order, only inside a fence, or only proven by
  `assert heading in body`;
- any required section body is empty;
- any required Motivation, Changes, Tests, SSOT, or Governance
  fact is missing;
- Tests omit the planned root tuple
  `collected 1693, passed 1693, failed 0, exit 0`;
- Tests omit a numeric warning count or warning types from the
  fresh run, or use a banned token;
- pull request 28 `headRefOid` is not `FINAL_HEAD`;
- no FINAL_HEAD `sanity-check` run appears before
  `DISCOVERY_SECONDS = 600`;
- the selected FINAL_HEAD run or required job is still
  non-terminal when `COMPLETION_SECONDS = 3600` expires;
- the wait loop has no completion deadline;
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
- Body-fact finding is closed. Task 9, Stop Conditions, and this
  Self-Review now require the extractable section parser. Five
  exact unfenced ATX H2 titles must appear once in order with
  non-empty bodies. Motivation, Changes, Tests, SSOT, and
  Governance facts are machine-checked. `assert heading in body`
  is not a pass.
- Completion-deadline finding is closed. Discovery stays
  `DISCOVERY_SECONDS = 600`. After the newest FINAL_HEAD run is
  selected, a new monotonic `COMPLETION_SECONDS = 3600` deadline
  bounds queued, pending, in_progress, waiting, and requested
  polling. Timeout prints FINAL_HEAD, run, and job evidence and
  stops. An unbounded wait is a stop. 3600 seconds is not a
  success exemption.
- Rollup-binding finding is closed. `FINAL_HEAD_CI_OK` requires
  run C, required job C, `headRefOid = FINAL_HEAD`, and exactly
  one `sanity-check` / `Run pytest (Path-A cache replay smoke)`
  CheckRun whose `detailsUrl` binds the selected `run_id` and
  `job_id`. Empty, unrelated, pending, failed, cancelled, stale,
  skipped, duplicate, or old-URL rollups fail.
- Kept contracts: atomic five-destination fetch, merge-base
  gate, PR17/PR18/PR19 source-head gates, 11 to 13 path set,
  current and combined test blobs, exactly one `--no-ff` merge,
  pull request 28 OPEN draft on `main`, design as semantic SSOT,
  and local-history versus main-PR merge separation.
- Spec coverage: reuse of pull request 28, one remaining
  `--no-ff` merge, pre-merge 11-path and post-merge 13-path
  sets, current and combined test hashes, three-ancestor
  contract, four pytest gates plus recorded root counts, draft
  stop.
- Design remains the semantic SSOT.
- Entry is fail-closed on an explicit Sol SHA and atomic
  five-destination fetch.
- Execution is not offered from this archival node.
