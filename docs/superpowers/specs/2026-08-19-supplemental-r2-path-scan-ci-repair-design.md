# Supplemental R2 Path-Scan CI Repair Design

**Status:** Design archived; implementation is not authorized
**Node:** `P1BP1I2Q7_CURSOR_VM_SUPPLEMENTAL_R2_CI_REPAIR_SPEC_PLAN`
**Type:** `GOVERNANCE_ONLY`
**Baseline:** `origin/main` `4444061dde0159a5edd62753fe3cef2d881a308c`
**Transport baseline:** `020b60fb83f7eb1d34f143458fca62beab5aa398`
**Claims:** blocked
**Formal denominator membership:** false
**Attempt-2 authorized:** false
**Real qualification authorized:** false
**Merge authorized:** false
**Design choice:** A (minimal parallel repair in three existing functions)

This document archives the approved semantics for scoping the
supplemental R2 forbidden-path gate. It is not an implementation
plan, Authorization, or implementation verdict. Writing or merging
this file does not authorize code edits, workflow edits, CI repair,
or claim upgrades.

This repair is independent of pull request 16. It addresses a
preexisting failure on `origin/main`. It must not copy commits from
`cursor/p3-standards-remediation-c46c`.

## Purpose

The GitHub Actions `sanity-check` job `Run pytest (Path-A cache
replay smoke)` fails on both `origin/main` and pull request 16 with
the same signature. The supplemental R2 forbidden-path scan walks
the entire repository through `git ls-files -co --exclude-standard`.
Any path added after transport baseline `020b60fb` whose relative
name matches readiness, freeze, annotation, prediction, or
detection tokens is treated as downstream contamination.

Legitimate later documents such as
`docs/review_20260812/phase0_protocol_freeze_task_report.md` and
`docs/superpowers/plans/2026-08-12-p3-phase0-protocol-freeze.md`
therefore make a valid synthetic admission fixture fail. That is
repo-global coupling, not a pull request 16 regression.

The repair must confine forbidden-path classification to the
admission artifact root, its sibling boundary, and frozen transport
files. Unrelated repository paths must not fail a legal fixture.

## Frozen CI Evidence

| Item | Value |
|---|---|
| Workflow | `sanity-check` |
| Check | `Run pytest (Path-A cache replay smoke)` |
| Test | `test_positive_admission_check` |
| Path | `tests/external_slice/test_check_supplemental_r2_admission.py` |
| Line | 600 |
| Error | `AssertionError: assert 1 == 0` |
| Message | `ERROR: forbidden data or downstream path present` |
| Count | `1 failed, 81 passed` |
| main run | `32146789008` at `4444061d` |
| PR 16 run | `32213892143` job `95951674266` at `081bb617` |

## Current Defect

Three modules each keep a `_forbidden_path_scan(root, *, repo_root)`:

- `scripts/external_slice/check_supplemental_r2_admission.py`
- `scripts/external_slice/check_supplemental_r2_handoff_hashes.py`
- `scripts/external_slice/mine_supplemental_r2.py`

Each function:

1. Lists every tracked and untracked path under `repo_root` with
   `git ls-files -co --exclude-standard`.
2. Classifies a path with `FORBIDDEN_PATH_NAME_RE`.
3. Allows the path only when it exists on transport baseline
   `020b60fb` and the working bytes match that commit.
4. Also walks the admission root and its parent (sibling boundary)
   for fixture files.

Step 1 is the coupling. Steps 2 through 4, command-log sentinel
scans, transport byte freeze, A2, analysis_id, vocabulary, and
handoff binding stay fail-closed.

`FORBIDDEN_PATH_NAME_RE` tokens remain:

```text
readiness
canonical_freeze
canonical-freeze
freeze
annotation
prediction
detection
```

Do not relax that regular expression.

## Approved Semantics

### Allowed behavior

`_forbidden_path_scan` may classify a path only when the path is
inside one of:

1. the admission artifact root passed as `root`;
2. the sibling boundary, which is the parent directory of `root`;
3. a frozen transport path already compared by
   `_transport_freeze_matches_baseline`.

A later file under `docs/`, `src/`, `tests/p3_v3/`, or any other
tree outside those three places must not flip
`forbidden_data_absent` to false, even when its name contains a
token from `FORBIDDEN_PATH_NAME_RE`.

Transport baseline commit `020b60fb` stays unchanged. Frozen
transport files and trees stay the same set:

```text
SCOPE.json
TRANSPORT_CONTRACT.json
QUOTAS.json
ISSUE_SNAPSHOT.json
COMMAND_LOG.json
PUBLISH_COMMIT.json
transport_pages/
failed_runs/
```

### Required fail-closed behavior

The following must still fail admission or handoff:

- a readiness, freeze, annotation, prediction, or detection
  sentinel created inside the admission root;
- the same sentinel created in the sibling boundary
  (`root.parent`);
- `COMMAND_LOG.json` or `VERIFICATION_LOG.json` recording
  readiness or canonical-freeze behavior;
- any frozen transport file whose bytes drift from `020b60fb`;
- any decision with `crit_dual_arm_repro` other than `PENDING`;
- any non-empty `analysis_id`;
- prohibited downstream vocabulary in mechanism or
  decision_reason;
- handoff, hash, or binding mismatch.

Do not delete the sentinel checks. Do not ignore the whole path
scan. Do not skip, xfail, or delete `test_positive_admission_check`.

### Three-module consistency

The three `_forbidden_path_scan` implementations must keep the same
boundary. This design selects option A: apply the same minimal
edit in each existing function. Do not add a shared helper file.
Option B would need a later file-authorization and is refused
here.

Keep the existing return type:

```text
tuple[bool, bool, bool]
# (forbidden_path_hit, readiness_file_hit, freeze_file_hit)
```

Keep `_classify_forbidden_rel(rel) -> tuple[bool, bool, bool]`.
Keep the historical unchanged-baseline exemption only for paths
that already qualify under the scoped roots.

## Future Implementation Scope

A later implementation node, if authorized, may edit only:

```text
scripts/external_slice/check_supplemental_r2_admission.py
scripts/external_slice/check_supplemental_r2_handoff_hashes.py
scripts/external_slice/mine_supplemental_r2.py
tests/external_slice/test_check_supplemental_r2_admission.py
```

This archival node must not edit those files.

## Required Tests For A Later Node

New tests must prove:

1. An unrelated `docs/...protocol_freeze...` path under a decoy
   `repo_root`, outside the admission root and sibling boundary,
   does not make `_forbidden_path_scan` return a hit and does not
   fail a valid `test_positive_admission_check` fixture.
2. A freeze or readiness file inside the admission root still
   fails both checkers.
3. A freeze or readiness file in the sibling boundary still fails
   both checkers. Existing
   `test_full_chain_downstream_token_filename_positions_rejected`
   remains the sibling contract.
4. The three `_forbidden_path_scan` functions return the same
   triple on the same roots.
5. Existing tamper, binding, and fail-closed tests still pass.
6. `test_positive_admission_check` returns 0.

## Non-Goals

This design does not:

- change `.github/workflows` or skip `external_slice` tests;
- xfail, skip, or delete the failing test;
- shrink the root suite to P3 only;
- change `TRANSPORT_BASELINE_COMMIT`;
- rewrite supplemental R2 data, handoff, or freeze results;
- run readiness, canonical freeze, retrieval, or GitHub mining;
- attribute the failure to pull request 16;
- authorize implementation, merge, attempt-2, or claim upgrades.

## Governance Stop

After this specification and the matching plan are committed and
pushed on the independent repair branch, work stops for Sol
review. Implementation remains unauthorized until a later user
node raises IMPLEMENTATION_AUTHORIZED from false after Sol review.

Pull request 16 stays OPEN and ready. This repair pull request
stays draft.

## Self-Review Record

- Incomplete-marker scan: none found.
- Design choice A is stated; choice B is refused.
- Fail-closed list is explicit.
- Future write set is closed.
- Pull request 16 is out of scope.
- Implementation authorization is withheld.
