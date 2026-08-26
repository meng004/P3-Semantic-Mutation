# Boost.Math Build-Preflight Attempt-2 Recovery Design

**Status:** Design only; implementation not authorized; attempt-2 execution not authorized
**Task:** `P3_BUILD_PREFLIGHT_ATTEMPT_2_RECOVERY_DESIGN_V1`
**Execution class:** `PILOT_ONLY`
**Formal denominator membership:** false
**Claims:** blocked
**Retry:** forbidden
**Fixed HEAD:** `0e51252f23dc3be4f82eb99e4f493c103f38c620`

This document freezes the minimum recovery mechanism, the attempt-2
namespace, the V5 qualification binding, the implementation boundary, the
validation requirements, and the later one-shot execution sequence.

It does not implement that mechanism. It does not authorize implementation.
It does not authorize attempt-2 execution. It does not create authorization,
verdict, intent, or result artifacts.

## 1. Purpose and scientific delta

Independently verified V5 qualification PASS proves only that this exact
Cloud VM completed one frozen minimal C++14 compile-link-run.

Two blockers remain before any later attempt-2 authorization can be
considered:

1. The production source runtime root
   `/tmp/p3-boost-math-pilot-production-source` is absent. Existing
   `src/p3_v3/pilot_source.py` classifies "tracked PASS pair present,
   runtime root absent" as `INVALID_PASS_NO_ROOT` and refuses automatic
   restoration.
2. Attempt-1 durable objects
   `data/p3_v3/pilot/boost_math/build-preflight-intent.json` and
   `data/p3_v3/pilot/boost_math/build-preflight-result.json` are terminal.
   Existing `src/p3_v3/pilot_build.py` raises `E_PILOT_BUILD_PREEXISTING`
   and must continue to do so for those exact paths.

This design freezes a later recovery that:

- restores the production source by read-only reuse of the existing PASS
  source manifest and preparation result;
- executes any later build-preflight only in a new attempt-2 namespace;
- binds that later execution to the already-verified V5 identity.

## 2. Binding identity

The later implementation and any later attempt-2 execution must bind all of
the following. Drift is terminal.

| Binding | Frozen value |
|---|---|
| Repository commit | `0e51252f23dc3be4f82eb99e4f493c103f38c620` |
| Cloud run | `bc-91edc0b7-4ef1-45a6-8100-da57ef8626e7` |
| Build / snapshot | `bld-20260824-7e7cfa3e-e25a-49bc-ba56-87ba178424a5` |
| Evidence pack SHA-256 | `05f687ef8360e669265a9196422b1a48d70a7b6833c9592d1d90c08095578a7b` |
| Qualification intent SHA-256 | `0a13766c565e89e32a21bc69ba0f449dc8a79c48a66a7bcace54c63faa224860` |
| Qualification result SHA-256 | `68aaac07c2d5ad4f834f114e1a0ac011052176f2a20ea63793f483357c31f6c2` |
| Qualification manifest SHA-256 | `5ef4c89e9601303b9e40e3fcda07c68055664cf53fb578d6efb1d39fc5f27c9a` |
| Qualification executable SHA-256 | `9d24d5298272942e95333acf18b05052b4c9d701aeaf92f7252a4d9666228b3b` |
| Compiler path | `/usr/bin/c++` |
| Compiler realpath | `/usr/lib/llvm-18/bin/clang` |
| Qualification root | `/tmp/p3-cxx-link-qualification` |
| Qualification terminal status | `PASS` |
| Source archive SHA-256 | `6cad33704c8341995f271d93811dd3cf9751ed5edf8b9a73882662acd3db0392` |
| Source archive bytes | `99676160` |
| Source archive format | `TAR` |
| Normalized source-tree SHA-256 | `93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8` |
| Materialized files | `4396` |
| Materialized bytes | `95635487` |

The qualification root is input evidence only. No later stage may rerun
`python3 scripts/p3_v3/qualify_cxx_link.py`, probe `c++ --version` outside
the already-recorded V5 evidence, replace qualification files, or mint a
second qualification root.

## 3. Attempt-1 immutability

The following attempt-1 objects remain immutable historical evidence.
They must never be deleted, rewritten, renamed, reused, reclassified in
place, parameterized, aliased, or redirected as attempt-2 objects.

Durable attempt-1 paths:

- `data/p3_v3/pilot/boost_math/user-auth-build-preflight.txt`
- `data/p3_v3/pilot/boost_math/build-preflight-intent.json`
- `data/p3_v3/pilot/boost_math/build-preflight-result.json`

Runtime attempt-1 roots:

- `/tmp/p3-boost-math-pilot-build-preflight`
- `/tmp/p3-boost-math-pilot-build-preflight-harness`

The recorded attempt-1 result remains:

- `terminal_status`: `FAIL`
- recorded `failure_reason`: `NONZERO_EXIT`
- first started job: `CMAKE_CONFIGURE` with exit `1`
- `BASELINE_BUILD` and `BASELINE_SMOKE`: `NOT_STARTED`

A local explanatory classification may identify the observed attempt-1
failure as `TOOLCHAIN_LINK_DEPENDENCY_MISSING`. That label is commentary
only. It must not be written back into attempt-1 artifacts, must not
replace `NONZERO_EXIT`, and must not be used to reopen attempt-1.

Existing `run_build_preflight` must continue to treat the attempt-1
namespace as closed. `E_PILOT_BUILD_PREEXISTING` remains the correct
refusal if that function is invoked again against the attempt-1 paths.

## 4. Source restoration

### 4.1 Authority

Restoration is explicit read-only reuse of the existing tracked PASS
source pair:

- `data/p3_v3/pilot/boost_math/source-manifest.json`
- `data/p3_v3/pilot/boost_math/source-preparation-result.json`

Those files must be re-read and re-validated. They must not be rewritten.

The implementation seam is `src/p3_v3/pilot_source.py`. Callers, including
`scripts/p3_v3/pilot.py`, may only invoke a new restoration entrypoint
defined in that module. Ad hoc extraction in a caller is forbidden.

### 4.2 Legal start state

Restoration may start only when all of the following hold:

- source-manifest is present and valid;
- source-preparation-result is present, valid, and `PASS`;
- the closed pair is consistent
  (`result.source_manifest_sha256` equals the manifest file SHA-256);
- `/tmp/p3-boost-math-pilot-production-source` is absent
  (`os.path.lexists` is false);
- `/tmp/p3-boost-math-pilot-production-source.staging` is absent;
- the current reconciliation state is exactly `INVALID_PASS_NO_ROOT`.

Any other state is terminal for that authorization. Restoration must not
treat `FRESH`, `MANIFEST_ONLY`, `MANIFEST_AND_ROOT`, `ALREADY_COMPLETE`,
`ORPHAN_ROOT`, or any `INVALID_*` state other than `INVALID_PASS_NO_ROOT`
as a restore opportunity.

### 4.3 Archive identity

The current source-manifest schema records archive SHA-256, byte count,
and format. It does not store a filesystem path field. The exact archive
path bound by the closed PASS production command, and therefore the path
that restoration must open, is:

`/tmp/p3-boost-math-public-source-discovery/content-equivalence-r1/boost-math-dc86f3259c84f68ac7c4e2be11a1ed8567011240-projected.tar`

Before extraction, restoration must:

1. require that exact path to exist as a regular, non-symlink file;
2. open it through the existing `read_production_archive_bytes` snapshot;
3. require `archive_format == TAR`;
4. require `archive_bytes == 99676160`;
5. require SHA-256
   `6cad33704c8341995f271d93811dd3cf9751ed5edf8b9a73882662acd3db0392`;
6. reject any other caller-supplied path.

A different path, a symlink, a non-regular file, a hash mismatch, a byte
mismatch, or a format mismatch is terminal. The archive must not be
regenerated or substituted.

### 4.4 Safe extraction and publish

Restoration must reuse the existing fail-closed extractor and staging
rules in `pilot_source.py`:

- extract only into a newly created staging directory
  `/tmp/p3-boost-math-pilot-production-source.staging`;
- reject a pre-existing staging path;
- apply `EXTRACTOR_POLICY_V1` without weakening it;
- recompute the Phase 1 normalized tree SHA-256, file count, and total
  bytes on staging before publish;
- require tree SHA-256
  `93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8`;
- require `4396` files and `95635487` bytes;
- publish only by atomic `os.replace` of staging onto
  `/tmp/p3-boost-math-pilot-production-source`.

Restoration may write only:

- the temporary staging root;
- the materialized production source root.

It must not write:

- `source-manifest.json`;
- `source-preparation-result.json`;
- attempt-1 or attempt-2 build/harness roots;
- authorization, verdict, intent, or result files.

After a successful publish, a later read-only revalidation of the closed
PASS pair plus the new root must classify as `ALREADY_COMPLETE`. The
tracked PASS artifacts remain the original files.

### 4.5 Why current logic cannot restore

`classify_reconciliation` already names the observed state
`INVALID_PASS_NO_ROOT`. `run_validate_source` then falls through to
`E_PILOT_SOURCE_OUTPUT_EXISTS`. That refusal is correct for an
unauthorized or incomplete caller. The later restoration entrypoint is
the only approved way to leave that state, and only after a separate
implementation review and a separate attempt-2 execution authorization.

## 5. Separate attempt-2 namespace

Attempt-2 must use these exact durable paths and no others:

- `data/p3_v3/pilot/boost_math/user-auth-build-preflight-attempt-2.txt`
- `data/p3_v3/pilot/boost_math/build-preflight-attempt-2-intent.json`
- `data/p3_v3/pilot/boost_math/build-preflight-attempt-2-result.json`

Attempt-2 must use these exact runtime roots and no others:

- `/tmp/p3-boost-math-pilot-build-preflight-attempt-2`
- `/tmp/p3-boost-math-pilot-build-preflight-attempt-2-harness`

The independently restored production source root remains:

- `/tmp/p3-boost-math-pilot-production-source`

Attempt-1 constants in `pilot_build.py` stay frozen:

- `INTENT_PATH`
- `RESULT_PATH`
- `AUTHORIZATION_PATH`
- `FROZEN_BUILD_ROOT`
- `FROZEN_HARNESS_ROOT`

Attempt-2 must add new constants and a new entrypoint. It must not
parameterize, alias, redirect, or reuse the attempt-1 constants as
attempt-2 paths. `run_build_preflight` must keep its current path
equality checks and must keep refusing a second attempt-1 run.

Attempt-2 schemas must be distinct from attempt-1 schemas so that neither
validator can accept the other namespace:

- intent: `p3-pilot-build-preflight-attempt-2-intent-v1`
- result: `p3-pilot-build-preflight-attempt-2-result-v1`

This design does not create the attempt-2 authorization file and does not
freeze an authorization token. The exact token bytes are reserved for a
later explicit user authorization after independent implementation review.

## 6. V5 qualification binding

Any later attempt-2 intent must embed, and any later attempt-2 result must
repeat, the Section 2 qualification bindings.

At attempt-2 entry, before intent creation:

1. require Cloud run
   `bc-91edc0b7-4ef1-45a6-8100-da57ef8626e7`;
2. require build and snapshot
   `bld-20260824-7e7cfa3e-e25a-49bc-ba56-87ba178424a5`;
3. require HEAD
   `0e51252f23dc3be4f82eb99e4f493c103f38c620`, detached, empty porcelain;
4. require `/tmp/p3-cxx-link-qualification` to be a real directory and not
   a symlink;
5. re-hash the immutable qualification intent, result, manifest, and
   executable and require the Section 2 SHA-256 values;
6. require recorded compiler path `/usr/bin/c++` and realpath
   `/usr/lib/llvm-18/bin/clang`;
7. require qualification `terminal_status == PASS` and
   `failure_reason is null`;
8. stop without repair if any check fails.

The qualification files are not inputs to CMake. They are identity
evidence. Attempt-2 CMake must still pass
`-DCMAKE_CXX_COMPILER=/usr/bin/c++` exactly as attempt-1 did, using the
same resolved compiler identity, without a new compiler probe.

## 7. Authority separation

The following gates remain sequential and exclusive:

1. This design document: reviewable freeze only.
2. Later implementation: requires a later explicit implementation
   authorization and an implementation plan. Design approval does not
   grant it.
3. Later independent implementation review: required before any
   attempt-2 execution authorization.
4. Later attempt-2 execution: requires a new, exact user authorization
   file at the attempt-2 authorization path. Implementation PASS does
   not grant it.

Existing attempt-1 safety contracts remain in force and must not be
weakened or bypassed:

- `docs/superpowers/plans/2026-08-17-p3-boost-math-pilot-build-preflight-only.md`
- `docs/review_20260817/boost_math_pilot_build_preflight_plan_sol_high_review.md`
- `docs/review_20260817/boost_math_pilot_build_preflight_implementation_sol_high_review.md`
- `_require_plan_and_implementation_verdicts` in `pilot_build.py`
- source-preparation plan, capability, launch, and Authorization A
  contracts in `pilot_source.py`

Attempt-2 may add new review artifacts for the recovery implementation.
It may not rewrite or substitute the attempt-1 verdict files. This design
task must not create authorization or verdict files.

## 8. Later one-shot execution order

A later authorized attempt-2 run must execute this order exactly once:

1. Verify exact V5 execution identity and immutable qualification
   evidence (Section 6).
2. Restore and verify the production source (Section 4). If the root is
   already `ALREADY_COMPLETE` and the tree hashes match, do not extract
   again. If the state is `INVALID_PASS_NO_ROOT`, restore once. Any other
   source state is terminal.
3. Verify attempt-2 entry gates and the separate namespace: attempt-2
   authorization, intent, and result must be absent before intent
   creation; attempt-2 build and harness roots must be absent; attempt-1
   durable objects must still exist unchanged.
4. Exclusive-create the attempt-2 intent.
5. Run `CMAKE_CONFIGURE` exactly once against the attempt-2 harness and
   attempt-2 build root, with
   `-DBOOST_MATH_PILOT_SOURCE_INCLUDE=/tmp/p3-boost-math-pilot-production-source/include`
   and `-DCMAKE_CXX_COMPILER=/usr/bin/c++`.
6. Run baseline build only if configure is `PASS`.
7. Run smoke only if baseline build is `PASS`.
8. Exclusive-create the attempt-2 result.
9. Stop.

No additional job, repair, or confirmatory rebuild is permitted.

## 9. Failure and retry policy

Every validation or workload failure is terminal for that authorization.

Forbidden:

- command retry;
- a second configure;
- automatic repair;
- attempt-1 fallback;
- deletion, rename, or rewrite of evidence to obtain a clean retry;
- reuse of a failed attempt-2 intent or result path.

Any later retry requires a new VM or a new evidence namespace when
applicable, and a new explicit authorization. This design does not grant
that authorization.

## 10. Claim ceiling

Even a later successful attempt-2 establishes only consumer-harness build
readiness for the frozen source and this environment.

It must not set:

- `formal_denominator_membership=true`
- `claims=unblocked`
- `attempt_2_authorized=true` outside the later execution authorization
- Boost.Math readiness beyond the tested harness
- any mutant, MR, certification, or paper-number claim

Attempt-2 intent and result must record:

```text
execution_class=PILOT_ONLY
formal_denominator_membership=false
claims=blocked
no_retry=true
rq4_supported=false
```

## 11. Implementation test boundary

A later implementation stage must use synthetic fixtures for unit and
integration tests.

Those tests must not run:

- the real compiler or linker;
- CMake;
- a package manager;
- real Boost source preparation;
- a real build-preflight workload;
- `qualify_cxx_link.py`.

They must directly cover:

- wrong archive hash;
- unsafe archive member;
- partial root;
- staging collision;
- wrong normalized tree, file count, or byte count;
- existing attempt-2 intent or result;
- wrong V5 identity (run, snapshot, HEAD, qualification hash, compiler
  path or realpath);
- attempt-1 immutability (attempt-1 paths still refuse reuse and still
  raise `E_PILOT_BUILD_PREEXISTING`).

Synthetic archives, temporary directories, and monkeypatched process
runners are the required test surface.

## 12. Required later implementation allowlist

This design identifies the smallest justified later allowlist. It does
not authorize edits to these paths.

| Path | Justification |
|---|---|
| `src/p3_v3/pilot_source.py` | Only legal seam for `INVALID_PASS_NO_ROOT` restoration, archive snapshot, safe extract, tree rehash, and publish-without-rewrite of the PASS pair. |
| `src/p3_v3/pilot_build.py` | Only legal seam for a new attempt-2 namespace, V5 identity gate, attempt-2 intent/result schemas, and the one-shot configure/build/smoke sequence without touching attempt-1 constants. |
| `scripts/p3_v3/pilot.py` | Only existing production CLI. It must grow explicit restore and attempt-2 subcommands that call the new module entrypoints and accept only the frozen paths. |
| `tests/p3_v3/test_pilot_source.py` | Direct coverage of restoration start states, archive/tree failures, and no-rewrite of the PASS pair. |
| `tests/p3_v3/test_pilot_build.py` | Direct coverage of attempt-2 namespace isolation, V5 identity failures, and attempt-1 immutability. |
| `tests/p3_v3/test_pilot.py` | Direct coverage that the CLI dispatches the new commands and still refuses attempt-1 reuse. |
| One later implementation plan under `docs/superpowers/plans/` | Required by the existing plan-then-implement-then-verdict contract. This design is not that plan. |
| Later independent review verdict artifacts under `docs/review_*/` | Required before attempt-2 execution authorization. This design does not create them. |

No other production path is justified. In particular, this design does
not allow edits to attempt-1 durable JSON, qualification code, package
policy, mutant/MR machinery, or paper-number builders.

Expected later CLI shape, not authorized here:

```text
python3 scripts/p3_v3/pilot.py restore-source \
  --archive /tmp/p3-boost-math-public-source-discovery/content-equivalence-r1/boost-math-dc86f3259c84f68ac7c4e2be11a1ed8567011240-projected.tar \
  --materialize-root /tmp/p3-boost-math-pilot-production-source

python3 scripts/p3_v3/pilot.py build-preflight-attempt-2 \
  --source-root /tmp/p3-boost-math-pilot-production-source \
  --build-root /tmp/p3-boost-math-pilot-build-preflight-attempt-2
```

Any other archive, source, or build path must be rejected.

## 13. What this task does not do

This design task does not:

- implement recovery or attempt-2;
- extract or restore source;
- run CMake, Boost, compiler, linker, or package-manager commands;
- rerun V5 qualification;
- create authorization, verdict, intent, or result files;
- modify any path other than this document;
- commit, push, or open a pull request;
- set `attempt_2_authorized=true`.

## 14. Preserved flags

```text
formal_denominator_membership=false
claims=blocked
attempt_2_authorized=false
no_retry=true
P3_BUILD_PREFLIGHT_ATTEMPT_2_RECOVERY_IMPLEMENTATION_V1_AUTHORIZED=false
P3_BUILD_PREFLIGHT_ATTEMPT_2_AUTHORIZED=false
P3_ECONTRACT_PRODUCTION_SEAM_IMPLEMENTATION_AUTHORIZED=false
```
