# Boost.Math Build-Preflight Attempt-2 Recovery Design Amendment V2

**Status:** Design amendment only; implementation not authorized; attempt-2 execution not authorized
**Task:** `P3_BUILD_PREFLIGHT_ATTEMPT_2_RECOVERY_DESIGN_AMENDMENT_V2`
**Execution class:** `DESIGN_AMENDMENT_ONLY`
**Amends:** `docs/superpowers/specs/2026-08-24-p3-boost-math-build-preflight-attempt-2-recovery-design.md`
**V1 SHA-256:** `a441fd68321e28f769447f19315c4b3bd82943888600126fe91bc66f3aec923b`
**Formal denominator membership:** false
**Claims:** blocked
**Retry:** forbidden

This amendment supersedes only the conflicting V1 provisions named below.
Every non-conflicting V1 constraint remains in force. This document does
not replace, rename, or delete V1. It does not implement recovery. It
does not authorize an implementation plan, implementation, commit,
authorization file, verdict file, intent, result, or attempt-2.

## 0. Scope of supersession

The following V1 clauses are withdrawn and replaced by this amendment:

| V1 locus | Withdrawn conflict |
|---|---|
| Header `Fixed HEAD`; §2 row `Repository commit`; §6 item 3; §8 step 6 context | Binding later attempt-2 execution, empty porcelain, and new recovery code to the same commit `0e51252f23dc3be4f82eb99e4f493c103f38c620`. |
| §6 items 1-2; §11 identity-failure tests phrased as qualification-hash proof of Cloud IDs | Treating Cloud run ID and build/snapshot ID as identities that production Python can cryptographically prove from V5 qualification artifacts. |
| §6 item 3 empty porcelain; §8 step 3 | Requiring attempt-2 authorization to be absent, while also requiring an authorization check, and requiring empty porcelain at `0e512...`. |
| §8 steps 1-9 entire order | Restoring source before exclusive-create of attempt-2 intent, and checking authorization after a write. |
| §4.1 caller CLI wording; §12 expected later CLI shape; §12 `pilot.py` allowlist sentence | A standalone production `restore-source` CLI plus a second `build-preflight-attempt-2` CLI. |
| §2 / §6 "no later `c++ --version` probe" without a replacement snapshot | Forbidding compiler probes while leaving `make_environment_snapshot()` (`cmake --version`, `c++ --version`, `git --version`) unspecified for attempt-2. |

V1 §1 purpose, §3 attempt-1 immutability, §4.2-§4.5 source identity and
safe extract/publish rules, §5 attempt-2 namespace paths and schemas,
§7 existing attempt-1 safety contracts, §9 failure-and-no-retry policy
except as refined by §2 of this amendment, §10 claim ceiling, §11
synthetic-test prohibition on real compiler/CMake/Boost/qualification,
and §12 allowlist membership (the six production/test paths plus later
plan and review artifacts) remain in force except where a row above
names a specific sentence.

## 1. Identity model

Two repository identities are frozen. They are not interchangeable.

```text
QUALIFICATION_BASE_HEAD=0e51252f23dc3be4f82eb99e4f493c103f38c620
RECOVERY_IMPLEMENTATION_HEAD=UNSET_UNTIL_INDEPENDENT_IMPLEMENTATION_PASS
```

`RECOVERY_IMPLEMENTATION_HEAD` is a deliberate lifecycle state. It is
not a placeholder that implementation may invent, guess, or fill with
the current working-tree SHA. No later stage may substitute
`QUALIFICATION_BASE_HEAD` for it, or the reverse.

Binding rules:

- V5 qualification remains bound to `QUALIFICATION_BASE_HEAD`. The V5
  intent, result, manifest, executable, compiler-version evidence, and
  host snapshot continue to identify that commit as the qualification
  repository state.
- Recovery implementation starts from `QUALIFICATION_BASE_HEAD`. A later
  authorized implementation commit must contain the approved design
  documents (V1 plus this V2 amendment), the approved implementation
  plan, the production changes, and the synthetic tests.
- Independent implementation review must pin the exact resulting commit
  SHA as `RECOVERY_IMPLEMENTATION_HEAD`. Until that pin exists, the
  value remains `UNSET_UNTIL_INDEPENDENT_IMPLEMENTATION_PASS`.
- Attempt-2 must run detached at that exact reviewed implementation
  commit, not at `QUALIFICATION_BASE_HEAD`.
- No code modification may remain outside that commit. Working-tree
  edits, uncommitted recovery code, or a second unpublished commit are
  terminal for attempt-2 entry.

The later implementation verdict and the later attempt-2 user
authorization may remain exact, untracked authority files so that they
can be created after the reviewed implementation commit is pinned.

Frozen later implementation-verdict path:

```text
docs/review_20260824/boost_math_attempt_2_recovery_implementation_sol_high_review.md
```

Frozen later attempt-2 authorization path:

```text
data/p3_v3/pilot/boost_math/user-auth-build-preflight-attempt-2.txt
```

Before attempt-2 intent creation, entry porcelain must contain exactly
those two explicitly permitted untracked authority files and nothing
else. Tracked files at `RECOVERY_IMPLEMENTATION_HEAD` must match that
commit. No other untracked, modified, or staged path is permitted.

The exact hashes and bytes of both authority files will be frozen only
after independent implementation review and a separate user
authorization. This amendment does not invent those bytes or hashes.

This section supersedes V1 header `Fixed HEAD`, V1 §2 row
`Repository commit` as the attempt-2 execution HEAD, and V1 §6 item 3
to the extent that item required detached empty porcelain at
`0e51252f23dc3be4f82eb99e4f493c103f38c620` for attempt-2.

V1 §2 qualification hashes, archive identity, compiler path/realpath,
qualification root, and source-tree bindings remain in force as V5
qualification identity, not as the attempt-2 repository HEAD.

## 2. Authority and durability order

This section supersedes V1 §8 in full and corrects V1 §8 step 3.

V1 §8 step 3 is contradictory: it required a check of attempt-2
authorization and simultaneously required that authorization to be
absent. The corrected rule is:

- attempt-2 authorization must be present and must match the later
  frozen exact bytes and hash;
- the later implementation verdict must be present and must match the
  later frozen exact bytes and hash;
- only the attempt-2 intent and the attempt-2 result must be absent
  before exclusive-create of the intent.

A later authorized attempt-2 run must execute this order exactly once.

### A. Executor-level read-only gates

The executor, not production Python, performs these checks before the
production command starts. They create or modify nothing.

- Verify control-plane run identity
  `bc-91edc0b7-4ef1-45a6-8100-da57ef8626e7`.
- Verify control-plane build/snapshot identity
  `bld-20260824-7e7cfa3e-e25a-49bc-ba56-87ba178424a5`.
- Verify exact `RECOVERY_IMPLEMENTATION_HEAD` after that value has been
  pinned. If the value is still
  `UNSET_UNTIL_INDEPENDENT_IMPLEMENTATION_PASS`, entry is blocked.
- Verify detached HEAD at that exact commit.
- Verify exact two-line permitted entry porcelain: the implementation
  verdict path and the attempt-2 authorization path, both untracked,
  and nothing else.
- Verify that the qualification root
  `/tmp/p3-cxx-link-qualification` and the bound archive path are not
  symlinks.
- Do not create or modify any file, directory, intent, result, source
  root, staging root, build root, or harness root.

### B. Production entry gates

Production Python then checks, still without writing:

- the authorization file must EXIST and match the later frozen exact
  bytes and hash;
- the implementation verdict must EXIST and match the later frozen
  exact bytes and hash;
- attempt-2 intent
  `data/p3_v3/pilot/boost_math/build-preflight-attempt-2-intent.json`
  must be absent;
- attempt-2 result
  `data/p3_v3/pilot/boost_math/build-preflight-attempt-2-result.json`
  must be absent;
- attempt-2 build root
  `/tmp/p3-boost-math-pilot-build-preflight-attempt-2` must be absent;
- attempt-2 harness root
  `/tmp/p3-boost-math-pilot-build-preflight-attempt-2-harness` must be
  absent;
- source staging root
  `/tmp/p3-boost-math-pilot-production-source.staging` must be absent;
- source production root may be absent (`INVALID_PASS_NO_ROOT`) or
  already complete (`ALREADY_COMPLETE` with matching tree identity);
  any other source state is terminal;
- attempt-1 evidence must remain present and unchanged
  (V1 §3 paths and recorded `NONZERO_EXIT`);
- qualification evidence file hashes must match V1 §2;
- archive identity must match V1 §4.3 through read-only inspection.

No process start, staging directory, or source-root write may occur
during A or B.

### C. Exclusive-create attempt-2 intent

Only after A and B pass may production exclusive-create the attempt-2
intent. That create is the durable consumption of the attempt-2
authorization and namespace.

### D. Workload only after intent creation

Only after intent creation may production:

1. collect the recorded CMake metadata (`METADATA_CMAKE_VERSION`);
2. restore or revalidate the source (`SOURCE_RESTORE`);
3. configure (`CMAKE_CONFIGURE`);
4. build (`BASELINE_BUILD`);
5. smoke (`BASELINE_SMOKE`);
6. exclusive-create the attempt-2 result;
7. stop.

No additional job, repair, or confirmatory rebuild is permitted.

### Failure classes

Any failure after intent creation must attempt exclusive publication of
a terminal attempt-2 result. If result publication itself fails, the
existing intent permanently closes that authorization and namespace.
No command retry is permitted.

A failure before intent creation is `ENTRY_BLOCKED`:

- workload attempt count remains unchanged;
- no root or durable artifact is written;
- the dispatch authorization is nevertheless closed;
- no command retry is permitted.

This refines V1 §9: the V1 no-retry and no-repair rules remain, and
`ENTRY_BLOCKED` is added as the pre-intent terminal class that writes
nothing while still consuming the dispatch authorization.

## 3. One deep production interface

This section supersedes V1 §12 expected later CLI shape and the V1 §12
`pilot.py` sentence that required explicit restore and attempt-2
subcommands. It also supersedes the V1 §4.1 wording to the extent that
wording allowed `scripts/p3_v3/pilot.py` to expose a production
restoration command.

There must be exactly one new production CLI interface:

```text
python3 scripts/p3_v3/pilot.py build-preflight-attempt-2 \
  --archive /tmp/p3-boost-math-public-source-discovery/content-equivalence-r1/boost-math-dc86f3259c84f68ac7c4e2be11a1ed8567011240-projected.tar \
  --source-root /tmp/p3-boost-math-pilot-production-source \
  --build-root /tmp/p3-boost-math-pilot-build-preflight-attempt-2
```

No standalone production `restore-source` CLI is permitted. A later
implementation must not add `restore-source` to `pilot.py`. Callers
must not perform archive extraction, staging publication, hashing,
authorization checks, or job sequencing themselves.

Frozen module seams:

- `pilot_build.py` owns the external one-shot orchestration interface.
- `pilot_source.py` owns one internal restoration interface that
  returns source-restoration evidence. That interface is not a
  production CLI.
- `pilot.py` only adapts CLI arguments to the single `pilot_build`
  interface.

V1 §12 allowlist membership is unchanged: the same six code/test paths
remain the only justified later edit surface, plus one later plan and
later review artifacts. The justified change to `pilot.py` is addition
of the single `build-preflight-attempt-2` adapter, not a second
restore command.

The later implementation plan must define the exact Python function
signatures for those seams. This amendment does not invent
implementation code, function names beyond the module ownership above,
or test fixtures.

Any other archive, source, or build path must be rejected. Attempt-1
CLI `build-preflight` and its frozen constants remain unchanged and
must keep raising `E_PILOT_BUILD_PREEXISTING` on attempt-1 paths.

## 4. Attempt-2 phase ledger

The ordered phase set is frozen:

1. `METADATA_CMAKE_VERSION`
2. `SOURCE_RESTORE`
3. `CMAKE_CONFIGURE`
4. `BASELINE_BUILD`
5. `BASELINE_SMOKE`

The attempt-2 intent must be created before phase 1. The result must
record all five phases. After the first non-`PASS` phase, later phases
are `NOT_STARTED`.

`SOURCE_RESTORE` must record:

- whether the source was `RESTORED` or `REVALIDATED`;
- archive SHA-256 and bytes;
- normalized tree SHA-256;
- materialized file count and bytes;
- staging/root publication status;
- started and ended timestamps;
- terminal status and failure reason;
- no subprocess claim.

`SOURCE_RESTORE` remains the V1 §4 restoration: extract only from the
bound archive into the bound staging path, publish only by atomic
replace onto the bound source root, or revalidate an already complete
root. It must not rewrite the tracked PASS pair. It must not claim that
a compiler, linker, CMake, or git subprocess ran inside this phase.

Dependencies:

- `CMAKE_CONFIGURE` depends on `SOURCE_RESTORE`;
- `BASELINE_BUILD` depends on `CMAKE_CONFIGURE`;
- `BASELINE_SMOKE` depends on `BASELINE_BUILD`.

`METADATA_CMAKE_VERSION` is metadata only, but it must still be durable
because it starts a subprocess. A missing or failing CMake metadata
phase is terminal and prevents `SOURCE_RESTORE` and all build phases.

Configure, when reached, remains the V1 §8 CMake invocation against the
attempt-2 harness and attempt-2 build root, with

```text
-DBOOST_MATH_PILOT_SOURCE_INCLUDE=/tmp/p3-boost-math-pilot-production-source/include
-DCMAKE_CXX_COMPILER=/usr/bin/c++
```

No process, staging directory, or source-root write may occur before
intent creation.

This section supersedes V1 §8 steps 2 and 5-8 as to order and phase
names. V1 attempt-1 recorded phase names stay historical and must not
be rewritten.

## 5. Environment evidence

Existing `make_environment_snapshot()` runs `cmake --version`,
`c++ --version`, and `git --version`. Attempt-2 must not call that
function as a substitute for the rules below.

Compiler:

- Do not run `c++ --version` again.
- Re-read and validate the V5 qualification intent, result, manifest,
  compiler-version stdout/stderr, and their hashes against V1 §2.
- Require current `/usr/bin/c++` to resolve to
  `/usr/lib/llvm-18/bin/clang`.
- Reuse the V5 compiler-version evidence in the attempt-2 environment
  record.

Git:

- Do not run `git --version`.
- Reuse the V5 qualification host-snapshot git-version field.

CMake:

- Resolve the CMake executable path without starting it before intent
  creation. Path resolution may inspect the filesystem (existence,
  regular-file/symlink classification, and realpath). It must not
  execute CMake.
- After intent creation, run `cmake --version` exactly once as
  `METADATA_CMAKE_VERSION`.
- Record its argv, stdout, stderr, exit, timestamps, and hashes.
- A missing or failing CMake metadata phase is terminal and prevents
  `SOURCE_RESTORE` and all build phases.

This section supersedes the underspecified V1 §2 / §6 prohibition on
new compiler probes by defining the replacement evidence rules. The
prohibition on a second `c++ --version` and on rerunning
`qualify_cxx_link.py` remains.

## 6. Control-plane claim boundary

Cloud run ID
`bc-91edc0b7-4ef1-45a6-8100-da57ef8626e7` and build/snapshot ID
`bld-20260824-7e7cfa3e-e25a-49bc-ba56-87ba178424a5` are
executor/control-plane observations.

The V5 qualification JSON files do not contain those IDs. Production
Python must not claim that qualification artifact hashes
cryptographically prove those IDs.

The executor checks those IDs before the command (Section 2.A).
Attempt-2 intent and result may record them only as:

```text
verification_scope=EXECUTOR_CONTROL_PLANE_OBSERVATION
```

Artifact-level verification covers qualification files, repository
commit (`RECOVERY_IMPLEMENTATION_HEAD` for attempt-2 execution;
`QUALIFICATION_BASE_HEAD` as the frozen V5 binding), host snapshot, and
compiler evidence only.

No new attestation mechanism is authorized by this design.

This section supersedes V1 §6 items 1-2 as production-Python gates and
narrows V1 §11 "wrong V5 identity (run, snapshot, ...)" tests: later
synthetic tests may still fail closed when an executor-supplied
observation is missing or mismatched, but they must not encode a claim
that qualification file hashes prove the Cloud IDs.

## 7. Promotion and review sequence

The later sequence is frozen. No earlier stage grants authority to a
later stage.

1. Independent review of this V2 amendment.
2. Implementation-plan-only task.
3. Independent plan review.
4. Separately authorized implementation using synthetic tests.
5. Separately authorized commit of the approved allowlist.
6. Independent implementation review pins
   `RECOVERY_IMPLEMENTATION_HEAD`.
7. Create the exact implementation-verdict authority at the frozen
   verdict path.
8. Separately create the exact attempt-2 user authorization at the
   frozen authorization path.
9. One-shot attempt-2 execution at the pinned
   `RECOVERY_IMPLEMENTATION_HEAD`.

This section supersedes V1 §7 items 1-4 only by inserting the V2
review, plan, pin, and two-file porcelain steps. Existing attempt-1
safety contracts in V1 §7 remain in force.

## 8. Preserved claim ceiling

This amendment preserves:

```text
formal_denominator_membership=false
claims=blocked
attempt_2_authorized=false
no_retry=true
rq4_supported=false
```

Even attempt-2 `PASS` proves only frozen consumer-harness build
readiness for the frozen source and this environment. It does not
establish Boost.Math readiness beyond the tested harness, mutant or MR
readiness, certification support, paper-number support, or formal
denominator membership.

Attempt-2 intent and result must continue to record the V1 §10 flag
block:

```text
execution_class=PILOT_ONLY
formal_denominator_membership=false
claims=blocked
no_retry=true
rq4_supported=false
```

This amendment does not set, and does not authorize setting:

```text
P3_BUILD_PREFLIGHT_ATTEMPT_2_RECOVERY_IMPLEMENTATION_PLAN_V1_AUTHORIZED=true
P3_BUILD_PREFLIGHT_ATTEMPT_2_RECOVERY_IMPLEMENTATION_V1_AUTHORIZED=true
P3_BUILD_PREFLIGHT_ATTEMPT_2_AUTHORIZED=true
```

## 9. What this amendment does not do

This amendment task does not:

- edit, replace, rename, or delete V1;
- create an implementation plan;
- implement recovery or attempt-2;
- extract or restore source;
- run CMake, Boost, compiler, linker, git-version, or package-manager
  commands;
- rerun V5 qualification;
- create authorization, verdict, intent, or result files;
- pin `RECOVERY_IMPLEMENTATION_HEAD` to any SHA;
- commit, push, or open a pull request.

## 10. Preserved flags

```text
formal_denominator_membership=false
claims=blocked
attempt_2_authorized=false
no_retry=true
rq4_supported=false
P3_BUILD_PREFLIGHT_ATTEMPT_2_RECOVERY_IMPLEMENTATION_PLAN_V1_AUTHORIZED=false
P3_BUILD_PREFLIGHT_ATTEMPT_2_RECOVERY_IMPLEMENTATION_V1_AUTHORIZED=false
P3_BUILD_PREFLIGHT_ATTEMPT_2_AUTHORIZED=false
P3_ECONTRACT_PRODUCTION_SEAM_IMPLEMENTATION_AUTHORIZED=false
```
