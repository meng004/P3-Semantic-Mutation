# Boost.Math Build-Preflight Attempt-2 Recovery Design Amendment V3

**Status:** Design amendment only; implementation not authorized; attempt-2 execution not authorized
**Task:** `P3_BUILD_PREFLIGHT_ATTEMPT_2_RECOVERY_DESIGN_AMENDMENT_V3`
**Execution class:** `DESIGN_AMENDMENT_ONLY`
**Amends:** V1 design and V2 amendment named below
**V1 path:** `docs/superpowers/specs/2026-08-24-p3-boost-math-build-preflight-attempt-2-recovery-design.md`
**V1 SHA-256:** `a441fd68321e28f769447f19315c4b3bd82943888600126fe91bc66f3aec923b`
**V2 path:** `docs/superpowers/specs/2026-08-24-p3-boost-math-build-preflight-attempt-2-recovery-design-amendment-v2.md`
**V2 SHA-256:** `a75cc3a3fecaafc26b59d32bb79fceac93f1a511f65a206b47ab497eacc2912f`
**Rejected Plan V1 path:** `docs/superpowers/plans/2026-08-24-p3-boost-math-attempt-2-recovery-implementation.md`
**Rejected Plan V1 SHA-256:** `9d5192b78b103fb0213ed2947c15b3e207aec022241b6cac9520e07da73c3e8c`
**Rejected Plan V1 bytes:** `96992`
**Rejected Plan V1 LF:** `1776`
**Formal denominator membership:** false
**Claims:** blocked
**Retry:** forbidden

```text
IMPLEMENTATION_NOT_AUTHORIZED
COMMIT_NOT_AUTHORIZED
ATTEMPT_2_NOT_AUTHORIZED
PLAN_V2_NOT_AUTHORIZED
```

This document does not replace, rename, or delete V1, V2, or rejected
Plan V1. It does not implement recovery. It does not create replacement
Plan V2. It does not authorize implementation, commit, an authorization
file, a verdict file, intent, result, or attempt-2.

## 1. Scope of supersession

V3 supersedes only the following conflicts:

| Locus | Withdrawn conflict |
|---|---|
| V2 §1 final two paragraphs; V2 §2 authorization/verdict "later frozen exact bytes and hash" as a production-code compile-time constant | Requiring production Python at `RECOVERY_IMPLEMENTATION_HEAD` to contain or expect the future implementation-verdict file SHA-256. |
| Any reading of V1/V2 that permits compiling a future authority hash into `RECOVERY_IMPLEMENTATION_HEAD` | Binding production constants to a verdict file that cannot exist until after that HEAD is pinned. |
| Rejected Plan V1 constants `ATTEMPT2_AUTHORIZATION_BYTES = b""`, `ATTEMPT2_AUTHORIZATION_SHA256 = "0" * 64`, `ATTEMPT2_IMPLEMENTATION_VERDICT_SHA256 = "0" * 64` | Empty bytes, all-zero hashes, sentinel hashes, or mutable fallbacks as authority values. |
| Rejected Plan V1 parallel log root `/tmp/p3-boost-math-pilot-build-preflight-attempt-2-logs` | A third attempt-2 runtime root. V1 §5 already froze two runtime roots "and no others". |
| Rejected Plan V1 use of `subprocess.run` for `METADATA_CMAKE_VERSION` | Combining `subprocess.run` with start-marker / PID / PGID / starttime / process-group cleanup. `subprocess.run` does not expose a live `Popen` identity at the required times. |
| V2 §1 sentence that both authority-file hashes remain unfrozen until after implementation review, as applied to user-authorization bytes | Leaving user-authorization bytes unset after this amendment. V3 freezes those bytes now. The implementation-verdict file hash remains unfrozen as a production constant. |

All other non-conflicting V1 and V2 provisions remain in force, including:

- V1 §1 purpose, §3 attempt-1 immutability, §4 source restoration rules,
  §5 durable attempt-2 paths and schemas except the withdrawn log-root
  reading, §7 attempt-1 safety contracts, §9 no-retry, §10 claim
  ceiling, §11 synthetic-test prohibition, §12 allowlist;
- V2 §1 identity split (`QUALIFICATION_BASE_HEAD` versus
  `RECOVERY_IMPLEMENTATION_HEAD`);
- V2 §2 write order: gates, exclusive intent, five phases, exclusive
  result, stop;
- V2 one production CLI `build-preflight-attempt-2` and no
  `restore-source`;
- V2 five-phase ledger and DAG;
- V2 reuse of V5 compiler and host evidence; no `c++ --version`; no
  `git --version`; no `make_environment_snapshot()`;
- V2 control-plane observation versus artifact-hash claim boundary.

## 2. Exact user-authorization bytes

The future authorization file at

```text
data/p3_v3/pilot/boost_math/user-auth-build-preflight-attempt-2.txt
```

is now frozen as these exact UTF-8/ASCII bytes, including one terminal LF:

```text
P3_BUILD_PREFLIGHT_ATTEMPT_2_AUTHORIZED=true\n
```

Exact properties, independently recomputed in this task:

```text
bytes=45
SHA-256=fdb55d342c8e132a7377e4dcde1be16c3a2f736e76fe3edfc0cdc85bcfc79201
```

Production code may contain these frozen bytes and this frozen hash as
constants. Tests may write the same 45 bytes under a temporary path and
assert the same hash.

Freezing these bytes does not create the file and does not authorize
attempt-2. Authorization becomes operational only when all of the
following later events occur:

1. a user sends the exact token `P3_BUILD_PREFLIGHT_ATTEMPT_2_AUTHORIZED=true`;
2. a separately authorized task creates the exact file with these bytes;
3. executor and production gates both observe that file;
4. attempt-2 itself is separately authorized.

Forbidden in production code, tests, plans, and later amendments:

- empty authorization bytes;
- all-zero SHA-256 (`"0" * 64`);
- any other sentinel hash;
- mutable fallback values;
- an environment variable or CLI argument that substitutes different
  authorization bytes.

## 3. Implementation-verdict trust model

V2 required production Python to check a future exact verdict-file
hash. That hash cannot exist when `RECOVERY_IMPLEMENTATION_HEAD` is
committed, because the verdict is created after independent
implementation review pins that HEAD. Compiling a guessed hash, an
empty value, or `"0" * 64` into that HEAD is forbidden.

Frozen later implementation-verdict path remains:

```text
docs/review_20260824/boost_math_attempt_2_recovery_implementation_sol_high_review.md
```

### 3.1 Executor / local reviewer gate

The executor or local reviewer:

- independently reviews the pinned `RECOVERY_IMPLEMENTATION_HEAD`;
- creates or approves one exact canonical implementation-verdict file
  at the frozen path;
- freezes that file's complete SHA-256 in the later execution packet;
- verifies the exact file hash before the production command starts;
- verifies detached HEAD equals the pinned
  `RECOVERY_IMPLEMENTATION_HEAD`;
- verifies permitted porcelain is exactly the verdict file and the
  authorization file, both untracked, and nothing else.

The executor's frozen hash is the external authority gate. Production
Python does not re-prove reviewer identity from that hash.

### 3.2 Production Python gate

Production Python:

- must not contain or expect a future compile-time verdict-file hash;
- must not use an empty, all-zero, or sentinel verdict-file hash;
- reads the verdict as a regular non-symlink snapshot;
- requires canonical JSON and exact-key schema
  `p3-pilot-attempt2-recovery-implementation-verdict-v1`;
- verifies the verdict's `artifact_sha256` self-hash;
- verifies `verdict=PASS`;
- verifies `qualification_base_head` equals
  `0e51252f23dc3be4f82eb99e4f493c103f38c620`;
- verifies `v1_design_sha256`, `v2_design_sha256`, and
  `v3_design_sha256` against current filesystem bytes of those three
  documents;
- verifies `approved_implementation_plan_sha256` against the approved
  replacement Plan V2 bytes;
- verifies every `reviewed_blob_sha256` entry against current
  filesystem bytes of the allowlisted path;
- computes and records the observed verdict-file SHA-256 in attempt-2
  intent and result as `attempt2_implementation_verdict_sha256`;
- does not claim that this self-validation proves the external
  reviewer identity.

The production validator is the byte, schema, and blob-consistency
gate.

### 3.3 Forbidden mechanisms

Do not add:

- a verdict-hash CLI argument;
- a verdict-hash environment variable;
- a mutable configuration file that supplies the verdict hash;
- a new attestation mechanism;
- a second implementation commit whose only purpose is to patch a
  future verdict-file hash into production constants.

## 4. Implementation-verdict schema minimum

Freeze schema version:

```text
p3-pilot-attempt2-recovery-implementation-verdict-v1
```

The later replacement Plan V2 must define an exact-key canonical JSON
schema containing at least these keys and no extras beyond the keys it
freezes:

| Key | Constraint |
|---|---|
| `schema_version` | exactly `p3-pilot-attempt2-recovery-implementation-verdict-v1` |
| `verdict` | exactly `PASS` |
| `reviewed_commit` | equals the later pinned `RECOVERY_IMPLEMENTATION_HEAD` |
| `qualification_base_head` | exactly `0e51252f23dc3be4f82eb99e4f493c103f38c620` |
| `v1_design_sha256` | SHA-256 of the V1 design file bytes |
| `v2_design_sha256` | SHA-256 of the V2 amendment file bytes |
| `v3_design_sha256` | SHA-256 of this V3 amendment file bytes |
| `approved_implementation_plan_sha256` | SHA-256 of replacement Plan V2 bytes |
| `reviewed_blob_sha256` | object whose exact keys are the allowlist below |
| `formal_denominator_membership` | `false` |
| `claims` | `blocked` |
| `attempt_2_authorized` | `false` |
| `rq4_supported` | `false` |
| `artifact_sha256` | canonical self-hash of all other keys |

The exact future verdict-file SHA-256 is intentionally not a
production-code constant.

Frozen `reviewed_blob_sha256` exact key set:

```text
rejected_plan_v1
src/p3_v3/pilot_source.py
src/p3_v3/pilot_build.py
scripts/p3_v3/pilot.py
tests/p3_v3/test_pilot_source.py
tests/p3_v3/test_pilot_build.py
tests/p3_v3/test_pilot.py
```

Each value is the SHA-256 of the current regular-file bytes of that
path. `rejected_plan_v1` maps to
`docs/superpowers/plans/2026-08-24-p3-boost-math-attempt-2-recovery-implementation.md`
and must equal
`9d5192b78b103fb0213ed2947c15b3e207aec022241b6cac9520e07da73c3e8c`.

Replacement Plan V2 may add only documentation fields that V3 already
requires above. It must not add a production constant for the
verdict-file hash.

## 5. Reviewed implementation HEAD content

The later `RECOVERY_IMPLEMENTATION_HEAD` must contain, as tracked
files:

- V1 design, byte-identical to
  `a441fd68321e28f769447f19315c4b3bd82943888600126fe91bc66f3aec923b`;
- V2 amendment, byte-identical to
  `a75cc3a3fecaafc26b59d32bb79fceac93f1a511f65a206b47ab497eacc2912f`;
- this V3 amendment, byte-identical to the file created by this task;
- rejected Plan V1, preserved byte-for-byte at
  `docs/superpowers/plans/2026-08-24-p3-boost-math-attempt-2-recovery-implementation.md`
  and explicitly classified in replacement Plan V2 as
  historical/rejected;
- independently approved replacement Plan V2 at
  `docs/superpowers/plans/2026-08-24-p3-boost-math-attempt-2-recovery-implementation-v2.md`;
- approved production-code changes limited to
  `src/p3_v3/pilot_source.py`, `src/p3_v3/pilot_build.py`, and
  `scripts/p3_v3/pilot.py`;
- approved synthetic-test changes limited to
  `tests/p3_v3/test_pilot_source.py`,
  `tests/p3_v3/test_pilot_build.py`, and
  `tests/p3_v3/test_pilot.py`.

Rejected Plan V1 must never be executed.

The implementation verdict and the user-authorization file remain
untracked authority files created after
`RECOVERY_IMPLEMENTATION_HEAD` is pinned. They are not part of that
commit.

Until independent implementation review pins it:

```text
RECOVERY_IMPLEMENTATION_HEAD=UNSET_UNTIL_INDEPENDENT_IMPLEMENTATION_PASS
```

That lifecycle value is not a SHA and must not be invented.

## 6. Runtime root and log location

No new parallel log root is allowed. V1 §5 remains: attempt-2 uses
exactly two runtime roots and no others.

```text
ATTEMPT2_BUILD_ROOT=/tmp/p3-boost-math-pilot-build-preflight-attempt-2
ATTEMPT2_LOG_ROOT=/tmp/p3-boost-math-pilot-build-preflight-attempt-2/logs
ATTEMPT2_HARNESS_ROOT=/tmp/p3-boost-math-pilot-build-preflight-attempt-2-harness
```

`ATTEMPT2_LOG_ROOT` is a child directory of `ATTEMPT2_BUILD_ROOT`, not
a third runtime root. This matches the existing attempt-1 pattern
`FROZEN_BUILD_ROOT / "logs"`.

After exclusive-create of attempt-2 intent, production:

1. creates the absent `ATTEMPT2_BUILD_ROOT` as a real directory;
2. creates its `logs` child through the existing
   `ensure_safe_log_root` contract;
3. runs `METADATA_CMAKE_VERSION` with that log child;
4. does not give `SOURCE_RESTORE` ownership of the build root;
5. after `SOURCE_RESTORE` PASS, calls `write_harness` to exclusively
   create the absent harness root;
6. runs CMake against the already-existing build root, which at that
   moment contains only the controlled `logs` child and then later
   CMake outputs.

No path outside the frozen production source root, attempt-2 build
root, and attempt-2 harness root may be created.

Forbidden:

```text
/tmp/p3-boost-math-pilot-build-preflight-attempt-2-logs
```

## 7. Metadata process-control seam

`METADATA_CMAKE_VERSION` must not use `subprocess.run`.

It must reuse the existing Popen-based process-control seam
`execute_job` in `src/p3_v3/pilot_build.py`. That function already
provides:

- start marker written by `write_job_start_marker` before Popen;
- `shell=False`;
- `start_new_session=True`;
- PID, PGID, and `/proc` starttime captured immediately after spawn;
- process identity written by `write_process_identity` before waiting;
- stdout/stderr captured through `communicate` without pipe deadlock;
- timeout enforcement;
- process-group termination and reap;
- final raw stdout/stderr publication as
  `{job_id}.stdout` and `{job_id}.stderr`;
- timestamps, exit, CPU, and RSS evidence;
- leak detection.

The replacement implementation plan must choose this one internal
process-runner interface for metadata and for ordinary attempt-2
process phases (`CMAKE_CONFIGURE`, `BASELINE_BUILD`,
`BASELINE_SMOKE`). Do not create a shallow second runner that
duplicates process-group logic.

Metadata spec values:

```text
job_id=METADATA_CMAKE_VERSION
job_kind=METADATA_CMAKE_VERSION
argv=[resolved_cmake_path, "--version"]
timeout_seconds=10
```

`resolved_cmake_path` is obtained before intent by
`shutil.which`, `os.lstat`, and `os.path.realpath` only. The process
starts only after attempt-2 intent exists. `SOURCE_RESTORE` still
starts no subprocess.

Forbidden metadata implementations:

- `subprocess.run`;
- `subprocess.check_output`;
- `os.system`;
- a new `run_metadata_cmake_version` that calls `subprocess.run`
  instead of `execute_job`.

A thin wrapper that only builds the metadata spec and calls
`execute_job` is permitted. A second process-group controller is not.

## 8. Replacement Plan V2 requirements

Rejected Plan V1 at
`docs/superpowers/plans/2026-08-24-p3-boost-math-attempt-2-recovery-implementation.md`
is terminally rejected. It must be preserved byte-for-byte and must
not be executed.

The later replacement plan must:

- use path
  `docs/superpowers/plans/2026-08-24-p3-boost-math-attempt-2-recovery-implementation-v2.md`;
- be complete and self-contained;
- contain no empty authority bytes;
- contain no zero or sentinel authority or verdict hashes;
- contain the frozen 45-byte authorization constant and hash from §2;
- contain no production constant for a future verdict-file hash;
- contain no separate attempt-2 log root;
- contain no `subprocess.run` metadata runner;
- define the exact verdict schema and the `reviewed_blob_sha256` key
  set from §4;
- define `execute_job` as the shared process-control seam from §7;
- preserve attempt-1 implementation and evidence;
- stop before commit;
- use synthetic tests only.

This amendment does not authorize writing that replacement plan.

## 9. Evidence-transfer rule for replacement Plan V2

Rejected Plan V1 plaintext was truncated in chat, so independent
reviewers could not recompute its claimed identity from the message
alone. The replacement-plan task must return deterministic
gzip-compressed Base64 of the complete plan.

Required encoding:

```text
gzip.compress(plan_bytes, compresslevel=9, mtime=0)
then standard Base64 ASCII.
```

The evidence return must include:

- uncompressed byte count and SHA-256;
- compressed byte count and SHA-256;
- complete uninterrupted gzip Base64;
- decoded-byte verification that the decompressed bytes equal the
  written plan file and match the uncompressed SHA-256;
- no `<long_seq>` marker, ellipsis, TextReference, or
  Cloud-only path substitution for the Base64 payload.

This V3 amendment is short enough that Base64 is not required for V3
itself. Complete inline plaintext remains mandatory for V3.

## 10. Preserved claim ceiling

```text
formal_denominator_membership=false
claims=blocked
attempt_2_authorized=false
no_retry=true
rq4_supported=false
execution_class=PILOT_ONLY
```

These flags remain false or blocked in production intent, result,
verdict schema, and later packets. Freezing authorization bytes does
not set `attempt_2_authorized=true` inside production artifacts.

## 11. This task does not grant the next stage

```text
V3 design amendment
→ independent V3 review
→ separately authorized replacement Plan V2
→ independent plan review
→ separately authorized synthetic implementation
→ separately authorized commit
→ independent implementation review pins RECOVERY_IMPLEMENTATION_HEAD
→ create exact verdict
→ create exact user authorization
→ separately authorized one-shot attempt-2
```

No stage grants the next stage.

```text
IMPLEMENTATION_NOT_AUTHORIZED
COMMIT_NOT_AUTHORIZED
ATTEMPT_2_NOT_AUTHORIZED
```
