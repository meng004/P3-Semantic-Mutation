# PR #17 and PR #19 Combined CI Integration Design

```text
Status: Design archived; integration implementation is not authorized
Type: GOVERNANCE_ONLY
Baseline: origin/main 4444061dde0159a5edd62753fe3cef2d881a308c
PR #17: fb20947a102934415dd201665971a711ccc4e0d5
PR #19: 3352cedb5f377b60f0aec5ff80997b2057c7fc14
Combined replay: 1693 passed, 0 failed
Merge authorized: false
```

**Node:** `P1BP1I2Q12_CURSOR_VM_PR17_PR19_INTEGRATION_SPEC_PLAN`
**Classification:** `MUTUALLY_SHADOWED_INDEPENDENT_CI_REPAIRS`
**Design choice:** A. Independent integration branch preserving both histories
**Claims:** blocked
**Formal denominator membership:** false
**Attempt-2 authorized:** false
**Real qualification authorized:** false
**PR ready authorized:** false
**Integration implementation authorized:** false
**Integration implementation executable:** false

This document archives the Sol-frozen topology for combining pull
request 17 and pull request 19. It is not an implementation grant.
Writing or merging this file does not authorize code edits, test
edits, workflow edits, mark-ready, merge, claims, attempt-2, or
qualification.

Sol already selected design choice A. Later nodes must not reopen
other integration topologies.

## Problem Classification

This situation is:

```text
MUTUALLY_SHADOWED_INDEPENDENT_CI_REPAIRS
```

It is not a production regression, a workflow defect, or claims
evidence.

Each repair is independently reviewed and independently effective on
its own files. Each repair is invisible to GitHub Actions `--maxfail=1`
while the other first failure remains:

- Pull request 17 alone applies the supplemental R2 path-scan repair.
  After that gate, the suite continues and exposes the compiler-alias
  test failure that pull request 19 repairs.
- Pull request 19 alone applies the portable compiler-alias fixture.
  The root suite still stops first on the supplemental R2 path-scan
  failure that pull request 17 repairs.
- The two repairs edit disjoint files. The isolated combined replay
  applied both implementation commits with no apply conflict.
- That isolated replay collected 1693 tests and passed 1693, with 10
  warnings, in 1429.77 seconds.
- A single red light on either open pull request is not a reason to
  force-merge that pull request.

The combined replay was read-only. It created no commit, pushed
nothing, and changed no pull request. It does not authorize merge.

## Frozen Inputs

| Item | Value |
|---|---|
| `origin/main` | `4444061dde0159a5edd62753fe3cef2d881a308c` |
| PR #17 branch | `cursor/supplemental-r2-path-scan-ci-repair-c46c` |
| PR #17 head | `fb20947a102934415dd201665971a711ccc4e0d5` |
| PR #19 branch | `cursor/p3-compiler-alias-ci-test-repair-c46c` |
| PR #19 head | `3352cedb5f377b60f0aec5ff80997b2057c7fc14` |
| Combined replay collected | 1693 |
| Combined replay passed | 1693 |
| Combined replay failed | 0 |
| Combined replay warnings | 10 |
| Combined replay duration | 1429.77 seconds |
| Combined replay reviewed | true |
| Combined replay pass | true |
| PR #17 implementation reviewed | true |
| PR #17 implementation review pass | true |
| PR #19 implementation reviewed | true |
| PR #19 implementation review pass | true |

## Approved Integration Design

Design choice A is frozen:

```text
A. Independent integration branch preserving both histories
```

A later implementation node, and only after Sol writes a full
40-character `INTEGRATION_IMPLEMENTATION_ENTRY` and sets both
`INTEGRATION_IMPLEMENTATION_AUTHORIZED` and
`INTEGRATION_IMPLEMENTATION_EXECUTABLE` to true, must:

1. Create the combination branch from the frozen `origin/main`.
2. Use a non-fast-forward merge to bring in the complete pull
   request 17 history.
3. Use a non-fast-forward merge to bring in the complete pull
   request 19 history.
4. Leave both repairs untouched. Do not rewrite the two fixes by
   hand.
5. Do not squash, rebase, or cherry-pick.
6. Keep provenance for both design documents, both plans, and both
   implementation commits.
7. Run both focused gates, the `test_pilot_build.py` file, and the
   root suite.
8. Require the root suite to report 1693 passed, or explain any new
   collection-count difference.
9. Create an independent draft pull request for the combination.
10. Leave pull requests 17 and 19 unchanged until that combination
    pull request receives its own implementation review.
11. Treat a passing combination review as insufficient for
    mark-ready or merge. Those remain unauthorized until a later
    Sol node writes the corresponding grants.

The archival governance branch created by this node is
`cursor/pr17-pr19-ci-integration-c46c`. It may contain only the two
integration documents written here. It is not the later
implementation combination branch.

## Merge Order

A later implementation plan must freeze this exact order and must
not execute it from this archival node:

```bash
git merge --no-ff \
  origin/cursor/supplemental-r2-path-scan-ci-repair-c46c \
  -m "merge: integrate supplemental R2 path-scan repair"

git merge --no-ff \
  origin/cursor/p3-compiler-alias-ci-test-repair-c46c \
  -m "merge: integrate compiler-alias CI test repair"
```

Pull request 17 is merged first so the path-scan gate is repaired
before the compiler-alias fixture is introduced. Pull request 19 is
merged second. Both merges keep the source branch histories.

## Rejected Designs

The following designs are rejected and must not be revived without a
new Sol design node:

- Force-merge either currently red pull request onto `main`.
- Mark pull request 17 or 19 ready and rely on a human to ignore CI.
- Retarget or stack either pull request onto the other.
- Squash, rebase, or force-push either history.
- Copy only the final file bytes and drop commit provenance.
- Append the other repair onto pull request 17 or pull request 19.
- Edit workflows, add skip or xfail, or delete tests.
- Close pull request 17 or 19 first.
- Promote the combined replay into merge, claims, attempt-2, or
  qualification authorization.

## Allowed Future File Set

After both non-fast-forward merges, `origin/main...HEAD` on the later
implementation combination branch may contain only:

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
documents created in this node. Those two files are not part of the
later implementation combination write set unless a later Sol node
explicitly adds them.

## Verification Contract

A later implementation node must run these commands with
`/usr/bin/python3` and without `rtk`:

```bash
PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1 \
  tests/external_slice/test_check_supplemental_r2_admission.py

PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1 \
  tests/p3_v3/test_pilot_build.py::test_compile_commands_compiler_mismatch

PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1 \
  tests/p3_v3/test_pilot_build.py

PYTHONPATH=src /usr/bin/python3 -m pytest -q --maxfail=1
```

Frozen reference results from the isolated combined replay:

```text
external_slice focused: 176 passed
compiler-alias focused: 1 passed
test_pilot_build.py: 75 passed
root: 1693 passed, 10 warnings
```

Duration need not match 1429.77 seconds. Collection count must match
1693, or the later node must record the new count and stop for Sol
review if any test fails.

## Non-Goals

This design does not:

- run a real compiler, qualification, CMake, ninja, make, or
  Boost.Math;
- run `scripts/build_paper_numbers.py`;
- execute attempt-2;
- upgrade claims;
- write an implementation verdict;
- mark any pull request ready;
- merge any pull request;
- edit production code or tests in this archival node;
- cherry-pick or copy the pull request 17 or 19 implementation
  commits onto this governance branch.

## Stop Conditions

A later implementation node must stop immediately when:

- Sol has not written `INTEGRATION_IMPLEMENTATION_ENTRY` as a full
  40-character SHA;
- `INTEGRATION_IMPLEMENTATION_AUTHORIZED` is not true;
- `INTEGRATION_IMPLEMENTATION_EXECUTABLE` is not true;
- `origin/main`, pull request 17, or pull request 19 no longer match
  the frozen SHAs above;
- a merge conflict appears;
- the combined diff contains any path outside the allowed future
  file set;
- any required pytest command fails;
- the root suite reports a failure or an unexplained collection
  change.

Do not derive `INTEGRATION_IMPLEMENTATION_ENTRY` from origin tip,
branch name, merge-base, pull request head, or clock time.

## Governance Stop

```text
INTEGRATION_IMPLEMENTATION_AUTHORIZED=false
INTEGRATION_IMPLEMENTATION_EXECUTABLE=false
PR_READY_AUTHORIZED=false
MERGE_AUTHORIZED=false
REAL_QUALIFICATION_AUTHORIZED=false
ATTEMPT_2_AUTHORIZED=false
CLAIMS_AUTHORIZED=false
FORMAL_DENOMINATOR_MEMBERSHIP=false
```

A later user node must still write `INTEGRATION_IMPLEMENTATION_ENTRY`
after Sol Spec plus Standards PASS. The combination pull request
stays draft until a later grant says otherwise.
