# Residual CMakeCache Third-History Integration Design

```text
Status: Design archived; third-history integration is not authorized
Type: GOVERNANCE_ONLY
Classification: RESIDUAL_CMAKECACHE_THIRD_HISTORY_INTEGRATION
Design choice: A. EXTEND_EXISTING_INTEGRATION_WITH_COMPLETE_PR18_HISTORY
Baseline: origin/main 4444061dde0159a5edd62753fe3cef2d881a308c
PR #17: fb20947a102934415dd201665971a711ccc4e0d5
PR #19: 3352cedb5f377b60f0aec5ff80997b2057c7fc14
PR #18 reviewed implementation head: 4b21072add365923799dccc057d4fefffd69918c
Current PR #28 head: e62974af4f5e2cfbc65d98c3b2f028edce57d25c
Implementation branch: cursor/pr17-pr19-ci-integration-c46c
Implementation pull request: PR #28
INTEGRATION_IMPLEMENTATION_AUTHORIZED=false
INTEGRATION_IMPLEMENTATION_EXECUTABLE=false
LOCAL_HISTORY_INTEGRATION_AUTHORIZED=false
MAIN_PR_MERGE_AUTHORIZED=false
PR_READY_AUTHORIZED=false
MERGE_AUTHORIZED=false
```

**Node:** `P1BP1I2Q20_CURSOR_VM_PR28_PR18_THIRD_HISTORY_INTEGRATION_SPEC_PLAN`
**Claims:** blocked
**Formal denominator membership:** false
**Attempt-2 authorized:** false
**Real qualification authorized:** false

This document is the semantic SSOT for extending the existing
pull request 28 integration with the complete history of pull
request 18. Path names stay historical. This file is not an
implementation grant. Writing or revising it does not authorize
local history integration, mark-ready, a GitHub merge into `main`,
claims, attempt-2, or qualification.

Sol selected design choice A. Later nodes must not reopen the
rejected topologies.

## Authority Terms

```text
INTEGRATION_IMPLEMENTATION_AUTHORIZED=false
INTEGRATION_IMPLEMENTATION_EXECUTABLE=false
LOCAL_HISTORY_INTEGRATION_AUTHORIZED=false
MAIN_PR_MERGE_AUTHORIZED=false
PR_READY_AUTHORIZED=false
MERGE_AUTHORIZED=false
```

`LOCAL_HISTORY_INTEGRATION_AUTHORIZED` now controls only the one
remaining `git merge --no-ff` that constructs commit topology on
`cursor/pr17-pr19-ci-integration-c46c`. It does not authorize a
GitHub merge into `main`.

`MAIN_PR_MERGE_AUTHORIZED` and `MERGE_AUTHORIZED` control only
merging a pull request into `main` through GitHub.
`MERGE_AUTHORIZED` is an alias for that main-PR merge only.

A later node may run the one remaining local history merge only
when all three of these are true:

```text
INTEGRATION_IMPLEMENTATION_AUTHORIZED=true
INTEGRATION_IMPLEMENTATION_EXECUTABLE=true
LOCAL_HISTORY_INTEGRATION_AUTHORIZED=true
```

Even if those three are true, that node still must not mark any
pull request ready, run `gh pr merge`, or merge pull request 28
into `main`.

This archival node leaves every flag false and does not execute
the merge.

## Classification

The live remaining defect on pull request 28 is:

```text
RESIDUAL_CMAKECACHE_THIRD_HISTORY_INTEGRATION
```

It is not:

- a pull request 17, 19, or 28 regression of already-integrated
  repairs;
- a production compiler-identity defect;
- a workflow defect;
- qualification or claims evidence.

Pull request 28 already contains the complete histories of pull
request 17 and pull request 19. Those two `--no-ff` merges must
not be repeated, copied, or rewritten.

## Design Choice

Design choice A is frozen:

```text
A. EXTEND_EXISTING_INTEGRATION_WITH_COMPLETE_PR18_HISTORY
```

Meaning:

- reuse `cursor/pr17-pr19-ci-integration-c46c` and pull request 28;
- do not re-merge, copy, or rewrite pull request 17 or 19;
- later add exactly one `--no-ff` merge that brings in the
  complete pull request 18 history through
  `4b21072add365923799dccc057d4fefffd69918c`;
- keep every source commit and both-parent merge topology;
- do not squash, cherry-pick, or copy the single test commit;
- if a merge conflict appears, stop immediately and do not
  resolve it by hand or widen the write set;
- do not create a second integration branch or pull request;
- this governance node does not execute that merge.

Rejected designs:

```text
B. cherry-pick only 4b21072a
C. copy the pull request 18 patch by hand into pull request 28
D. create a second integration pull request
E. squash or rebase already-pushed history
F. mark-ready or merge into main now
```

## Frozen Evidence

### Pull request 18 implementation review

```text
PR18_IMPLEMENTATION_REVIEWED=true
PR18_IMPLEMENTATION_REVIEW_PASS=true
head=4b21072add365923799dccc057d4fefffd69918c
```

### Pull request 18 focused and file evidence

```text
focused = 1 passed
file = 75 passed
```

### Pull request 18 standalone root and CI blocker

This blocker is independent. It is not a pull request 18 defect.

```text
GitHub run =
32475544774

job =
96750989039

collected =
1689

first failure =
tests/external_slice/test_check_supplemental_r2_admission.py::
test_positive_admission_check

result =
1 failed, 81 passed

classification =
known independent supplemental-R2 blocker
```

### Current pull request 28 authoritative RED

```text
head =
e62974af4f5e2cfbc65d98c3b2f028edce57d25c

run =
32449925094

job =
96676383508

collected =
1693

passed before failure =
1197

failure =
test_cmakecache_compiler_generator_root_drift
DID NOT RAISE EvidenceError
```

### Causal expectation

This is a prediction to verify later, not a claim that CI is green.

- Pull request 28 already contains pull request 17, so the
  supplemental R2 blocker is already repaired on this branch.
- Pull request 28 already contains pull request 19, so the
  compile_commands portable mismatch is already repaired.
- Pull request 18 supplies the remaining CMakeCache portable
  mismatch repair.
- Only after all three complete histories are present may a later
  node require root 1693 green.
- That later node must still observe the actual suite.

## Frozen Inputs

| Item | Value |
|---|---|
| `origin/main` | `4444061dde0159a5edd62753fe3cef2d881a308c` |
| PR #17 head | `fb20947a102934415dd201665971a711ccc4e0d5` |
| PR #19 head | `3352cedb5f377b60f0aec5ff80997b2057c7fc14` |
| PR #18 head | `4b21072add365923799dccc057d4fefffd69918c` |
| Current PR #28 head | `e62974af4f5e2cfbc65d98c3b2f028edce57d25c` |
| Implementation branch | `cursor/pr17-pr19-ci-integration-c46c` |
| Implementation pull request | 28 |
| Current PR28 `test_pilot_build.py` SHA-256 | `3278fbce1d0c017d219f450cea76eeb2c962f8d8bdca6b71fc9afad2fb5a0dd6` |
| Future combined `test_pilot_build.py` SHA-256 | `b1af86f556614b28cd41a204255c47a7c0e4b27cd4812c9cd6491b0c3c824e90` |

## Current And Future Path Sets

The current `origin/main...HEAD` set on pull request 28, before the
future third merge, must remain exactly these 11 paths:

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

A fourteenth path is a stop.

## Future Topology Contract

A later `INTEGRATION_IMPLEMENTATION_ENTRY` must be the Sol-written
40-character SHA of the reviewed tip of
`cursor/pr17-pr19-ci-integration-c46c` immediately before the one
remaining merge. Do not derive it from origin tip, branch name,
merge-base, pull request `headRefOid`, or clock time.

Before that merge, the later node must prove:

- pull request 17 head is an ancestor of integration `HEAD`;
- pull request 19 head is an ancestor of integration `HEAD`;
- pull request 18 head is not an ancestor of integration `HEAD`;
- integration `HEAD` still has frozen `origin/main` as merge-base;
- porcelain is empty;
- ahead/behind versus origin integration is `0 0`.

The only future merge command is:

```bash
git merge --no-ff \
  origin/cursor/p3-compiler-alias-ci-repair-c46c \
  -m "merge: integrate residual CMakeCache CI repair"
```

This command constructs topology on
`cursor/pr17-pr19-ci-integration-c46c` only. It does not merge any
pull request into `main`, does not equal `gh pr merge`, and does
not change the head or draft state of pull request 17, 18, or 19.

After that merge, the later node must prove:

- the merge commit first parent is the future
  `INTEGRATION_IMPLEMENTATION_ENTRY`;
- the merge commit second parent is
  `4b21072add365923799dccc057d4fefffd69918c`;
- the three source heads are ancestors of the new `HEAD`;
- there is no hand-written conflict-resolution commit;
- porcelain is empty;
- `tests/p3_v3/test_pilot_build.py` SHA-256 equals
  `b1af86f556614b28cd41a204255c47a7c0e4b27cd4812c9cd6491b0c3c824e90`.

This archival node must not run that merge.

## Future Verification Contract

A later implementation node must run these commands with
`/usr/bin/python3` and without `rtk`:

```bash
PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1 \
  tests/external_slice/test_check_supplemental_r2_admission.py

PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1 \
  tests/p3_v3/test_pilot_build.py::test_compile_commands_compiler_mismatch

PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1 \
  tests/p3_v3/test_pilot_build.py::test_cmakecache_compiler_generator_root_drift

PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1 \
  tests/p3_v3/test_pilot_build.py

PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1
```

Frozen expectations after the third history is present:

```text
external_slice focused: 176 passed
compile_commands focused: 1 passed
CMakeCache focused: 1 passed
test_pilot_build.py: 75 passed
root: collected 1693, passed 1693, failed 0
```

Warnings are allowed and must be counted and named. Any failure is
a stop. A green root suite is not mark-ready and is not a main-PR
merge grant.

## Non-Goals

This design does not:

- re-merge pull request 17 or 19;
- cherry-pick or copy `4b21072a`;
- create a second combination branch or pull request;
- run a real compiler, qualification, CMake, ninja, make, or
  Boost.Math;
- run `scripts/build_paper_numbers.py`;
- execute attempt-2;
- upgrade claims;
- write an implementation verdict;
- mark any pull request ready;
- merge any pull request into `main`;
- run `gh pr merge`;
- run the remaining local history merge from this archival node;
- edit production code or tests in this archival node.

## Stop Conditions

A later implementation node must stop immediately when:

- Sol has not written `INTEGRATION_IMPLEMENTATION_ENTRY` as a full
  40-character SHA;
- any of the three local-history flags is not true;
- `HEAD` is not the Sol-written entry;
- `origin/main` or any source head no longer matches the frozen
  SHA;
- pull request 18 is already an ancestor before the merge;
- pull request 17 or 19 is not an ancestor before the merge;
- a merge conflict appears;
- the post-merge path set is not the exact 13-path set;
- the combined test-file SHA-256 is not
  `b1af86f556614b28cd41a204255c47a7c0e4b27cd4812c9cd6491b0c3c824e90`;
- any required pytest command fails;
- the root suite reports a failure or an unexplained collection
  change;
- pull request 28 is no longer OPEN and draft.

## Governance Stop

```text
INTEGRATION_IMPLEMENTATION_AUTHORIZED=false
INTEGRATION_IMPLEMENTATION_EXECUTABLE=false
LOCAL_HISTORY_INTEGRATION_AUTHORIZED=false
MAIN_PR_MERGE_AUTHORIZED=false
PR_READY_AUTHORIZED=false
MERGE_AUTHORIZED=false
REAL_QUALIFICATION_AUTHORIZED=false
ATTEMPT_2_AUTHORIZED=false
CLAIMS_AUTHORIZED=false
FORMAL_DENOMINATOR_MEMBERSHIP=false
```

A later user node must still write `INTEGRATION_IMPLEMENTATION_ENTRY`
after Sol Spec plus Standards PASS. Pull request 28 stays draft.
This archival node must not start the future implementation tasks.
