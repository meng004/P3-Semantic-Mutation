# PR #17 and PR #19 Combined CI Integration Design

```text
Status: Design archived; integration implementation is not authorized
Type: GOVERNANCE_ONLY
Baseline: origin/main 4444061dde0159a5edd62753fe3cef2d881a308c
PR #17: fb20947a102934415dd201665971a711ccc4e0d5
PR #19: 3352cedb5f377b60f0aec5ff80997b2057c7fc14
Current governance tip: 92516bb27687f172db95a36ae75a91d07d247034
Implementation branch: cursor/pr17-pr19-ci-integration-c46c
Implementation pull request: PR #28
Combined replay: 1693 passed, 0 failed
INTEGRATION_IMPLEMENTATION_AUTHORIZED=false
INTEGRATION_IMPLEMENTATION_EXECUTABLE=false
LOCAL_HISTORY_INTEGRATION_AUTHORIZED=false
MAIN_PR_MERGE_AUTHORIZED=false
PR_READY_AUTHORIZED=false
MERGE_AUTHORIZED=false
```

**Node:** `P1BP1I2Q13_CURSOR_VM_PR28_INTEGRATION_PLAN_REMEDIATION`
**Classification:** `MUTUALLY_SHADOWED_INDEPENDENT_CI_REPAIRS`
**Design choice:** A. Independent integration branch preserving both histories
**Claims:** blocked
**Formal denominator membership:** false
**Attempt-2 authorized:** false
**Real qualification authorized:** false

This document is the semantic SSOT for combining pull request 17 and
pull request 19. It is not an implementation grant. Writing or
revising this file does not authorize local history integration,
mark-ready, a GitHub merge into `main`, claims, attempt-2, or
qualification.

Sol already selected design choice A. Later nodes must not reopen
other integration topologies.

## Authority Terms

```text
INTEGRATION_IMPLEMENTATION_AUTHORIZED=false
INTEGRATION_IMPLEMENTATION_EXECUTABLE=false
LOCAL_HISTORY_INTEGRATION_AUTHORIZED=false
MAIN_PR_MERGE_AUTHORIZED=false
PR_READY_AUTHORIZED=false
MERGE_AUTHORIZED=false
```

`LOCAL_HISTORY_INTEGRATION_AUTHORIZED` controls only the two
`git merge --no-ff` commands that construct commit topology on
`cursor/pr17-pr19-ci-integration-c46c`. It does not authorize a
GitHub merge into `main`.

`MAIN_PR_MERGE_AUTHORIZED` and `MERGE_AUTHORIZED` control only
merging a pull request into `main` through GitHub. In this contract,
`MERGE_AUTHORIZED` is an alias for that main-PR merge only. It is
not a local-history-integration grant.

A later node may run the two local history merges only when all
three of these are true:

```text
INTEGRATION_IMPLEMENTATION_AUTHORIZED=true
INTEGRATION_IMPLEMENTATION_EXECUTABLE=true
LOCAL_HISTORY_INTEGRATION_AUTHORIZED=true
```

Even if those three are true, that node still must not:

- mark any pull request ready;
- run `gh pr merge`;
- merge pull request 28 into `main`.

Those remain blocked until a later Sol node sets
`PR_READY_AUTHORIZED=true` and `MAIN_PR_MERGE_AUTHORIZED=true`.
This archival node leaves every flag false.

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
  force-merge that pull request into `main`.

The combined replay was read-only. It created no commit, pushed
nothing, and changed no pull request. It does not authorize local
history integration or a main-PR merge.

## Frozen Inputs

| Item | Value |
|---|---|
| `origin/main` | `4444061dde0159a5edd62753fe3cef2d881a308c` |
| PR #17 branch | `cursor/supplemental-r2-path-scan-ci-repair-c46c` |
| PR #17 head | `fb20947a102934415dd201665971a711ccc4e0d5` |
| PR #19 branch | `cursor/p3-compiler-alias-ci-test-repair-c46c` |
| PR #19 head | `3352cedb5f377b60f0aec5ff80997b2057c7fc14` |
| Current governance tip | `92516bb27687f172db95a36ae75a91d07d247034` |
| Implementation branch | `cursor/pr17-pr19-ci-integration-c46c` |
| Implementation pull request | 28 |
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

Reuse is frozen. Do not invent a second combination branch or a
second combination pull request.

```text
implementation branch =
cursor/pr17-pr19-ci-integration-c46c

implementation pull request =
PR #28

implementation entry =
the exact reviewed governance tip written by Sol
```

The current reviewed governance tip at the start of this
remediation is `92516bb27687f172db95a36ae75a91d07d247034`. A later
`INTEGRATION_IMPLEMENTATION_ENTRY` is the exact 40-character SHA Sol
writes after this remediation is reviewed. That SHA is the
then-current tip of `cursor/pr17-pr19-ci-integration-c46c`
immediately before the two local history merges. Do not treat
`92516bb27687f172db95a36ae75a91d07d247034` as that later entry
unless Sol writes that exact SHA.

A later implementation node, and only after Sol writes
`INTEGRATION_IMPLEMENTATION_ENTRY` and sets
`INTEGRATION_IMPLEMENTATION_AUTHORIZED`,
`INTEGRATION_IMPLEMENTATION_EXECUTABLE`, and
`LOCAL_HISTORY_INTEGRATION_AUTHORIZED` to true, must:

1. Enter the existing branch
   `cursor/pr17-pr19-ci-integration-c46c`. Do not create another
   combination branch.
2. Confirm `HEAD` equals the Sol-written
   `INTEGRATION_IMPLEMENTATION_ENTRY`.
3. Use a non-fast-forward merge to bring in the complete pull
   request 17 history.
4. Use a non-fast-forward merge to bring in the complete pull
   request 19 history.
5. Leave both repairs untouched. Do not rewrite the two fixes by
   hand.
6. Do not squash, rebase, or cherry-pick.
7. Keep provenance for both source design documents, both source
   plans, both implementation commits, and both integration
   documents.
8. Run both focused gates, the `test_pilot_build.py` file, and the
   root suite.
9. Require the root suite to report 1693 passed, or explain any new
   collection-count difference.
10. Update the existing draft pull request 28. Do not create a
    second combination pull request.
11. Leave pull requests 17 and 19 unchanged.
12. Keep pull request 28 draft. A passing combination review is
    not mark-ready and is not a main-PR merge grant.

Pull request 28 starts as a docs-only draft. After the two local
history merges it remains draft and contains the complete source
histories plus the two integration documents. Those two documents
must remain in the final 11-path set.

The later node must verify pull request 28 with:

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

The pull request body must contain motivation, changes, the four
test results, SSOT, and governance state.

## Merge Order

A later implementation plan must freeze this exact order and must
not execute it unless the three local-history flags are true:

```bash
git merge --no-ff \
  origin/cursor/supplemental-r2-path-scan-ci-repair-c46c \
  -m "merge: integrate supplemental R2 path-scan repair"

git merge --no-ff \
  origin/cursor/p3-compiler-alias-ci-test-repair-c46c \
  -m "merge: integrate compiler-alias CI test repair"
```

These two commands construct commit topology on
`cursor/pr17-pr19-ci-integration-c46c` only. They do not merge any
pull request into `main`, do not equal `gh pr merge`, and do not
change the head or draft state of pull request 17 or 19.

Pull request 17 is integrated first so the path-scan gate is
repaired before the compiler-alias fixture is introduced. Pull
request 19 is integrated second. Both merges keep the source branch
histories.

## Rejected Designs

The following designs are rejected and must not be revived without a
new Sol design node:

- Force-merge either currently red pull request onto `main`.
- Mark pull request 17, 19, or 28 ready and rely on a human to
  ignore CI.
- Retarget or stack either source pull request onto the other.
- Create a second combination branch or a second combination pull
  request.
- Squash, rebase, or force-push either history.
- Copy only the final file bytes and drop commit provenance.
- Append the other repair onto pull request 17 or pull request 19.
- Edit workflows, add skip or xfail, or delete tests.
- Close pull request 17 or 19 first.
- Drop the two integration documents from the final write set.
- Promote the combined replay into local history integration,
  main-PR merge, claims, attempt-2, or qualification authorization.

## Allowed File Set

The two integration documents remain in scope. They are not an
optional extra.

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

Any other path is a stop.

## Entry Semantics

`INTEGRATION_IMPLEMENTATION_ENTRY` is the exact reviewed governance
tip of `cursor/pr17-pr19-ci-integration-c46c` immediately before the
two local history merges. Sol must write that SHA as 40 characters.
A later executor must verify:

```text
branch =
cursor/pr17-pr19-ci-integration-c46c

HEAD =
INTEGRATION_IMPLEMENTATION_ENTRY

origin/cursor/pr17-pr19-ci-integration-c46c =
INTEGRATION_IMPLEMENTATION_ENTRY

ahead/behind = 0 0
porcelain = empty
```

Do not derive that entry from branch name, pull request head,
origin tip, merge-base, or clock time.

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
- merge any pull request into `main`;
- run `gh pr merge`;
- run the two local history merges from this archival node;
- create a second combination branch or pull request;
- edit production code or tests in this archival node;
- cherry-pick or copy the pull request 17 or 19 implementation
  commits in this archival node.

## Stop Conditions

A later implementation node must stop immediately when:

- Sol has not written `INTEGRATION_IMPLEMENTATION_ENTRY` as a full
  40-character SHA;
- `INTEGRATION_IMPLEMENTATION_AUTHORIZED` is not true;
- `INTEGRATION_IMPLEMENTATION_EXECUTABLE` is not true;
- `LOCAL_HISTORY_INTEGRATION_AUTHORIZED` is not true, if the node
  is about to run either `git merge --no-ff`;
- `HEAD` is not the Sol-written
  `INTEGRATION_IMPLEMENTATION_ENTRY`;
- `origin/main`, pull request 17, or pull request 19 no longer match
  the frozen SHAs above;
- a merge conflict appears;
- the first-merge diff is not the exact 8-path set;
- the final diff is not the exact 11-path set;
- any required pytest command fails;
- the root suite reports a failure or an unexplained collection
  change;
- pull request 28 is no longer OPEN and draft, or its
  `baseRefName` is not `main`, or its `headRefName` is not
  `cursor/pr17-pr19-ci-integration-c46c`.

Do not derive `INTEGRATION_IMPLEMENTATION_ENTRY` from origin tip,
branch name, merge-base, pull request `headRefOid`, or clock time.

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
after Sol Spec plus Standards PASS. Pull request 28 stays draft
until a later grant says otherwise.
