# P3 Boost.Math Formal Header Profiling Design

**Date:** 2026-08-26  
**Status:** User-approved design; implementation and profiling execution remain separate steps  
**Scope:** Boost.Math snapshot
`74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886`
only

## Goal

Replace the 20 `PHASE1_PROFILING_NOT_EXECUTED` placeholder rows for the fixed
Boost.Math profiling workload with real, auditable C++ header-compilation
observations. Preserve the frozen workload and controlled-subject identity. Do
not invent function calls or claim dynamic technique evidence that the workload
cannot supply.

The preceding Attempt-2 PASS establishes that the controlled source can be
restored and that CMake, the C++14 compiler, the baseline build, and the smoke
executable work in the selected Cursor Cloud environment. It does not itself
execute the profiling workload or determine a profiling technique.

## Scientific boundary

All 20 selected rows are `PUBLIC_API` declarations whose frozen input is a
header path. They do not specify a callable symbol, arguments, or an input
value. The formal profiling slice therefore tests the declared behavior that
is actually frozen: whether a translation unit can include and compile each
header in the controlled source environment.

A successful header compilation is not a subject API call. The runner must not
turn a compiler process, generated `main`, dependency edge, or guessed symbol
into a subject-level call trace. Consequently, successful compilation is
reported as `MISSING_TRACE`, not `SUCCESS`, and the expected aggregate
classification remains `TECH_UNCERTAIN`. This is an admissible scientific
result: it replaces "not executed" with observed execution while retaining the
information limit of the prespecified workload.

The slice must not:

- change the workload or controlled-subject identity;
- infer or synthesize function invocations;
- report dynamically reached mutation sites from compile dependencies;
- overwrite the Phase-1 placeholder receipt;
- add qualification, authorization, verdict, baseline, or hash-contract chains;
- upgrade formal-denominator membership or an RQ conclusion.

## Architecture

The production runner lives in `src/p3_v3/profiling_runner.py`. It owns header
harness generation, compiler process control, raw-log publication, and receipt
construction. It depends on the existing canonical artifact primitives but not
on `bridge_and_frames.py`, so receipt validation can import it lazily without a
circular dependency.

The existing validator currently assumes that every profiling receipt was
produced by `bridge_and_frames.py`. Adding execution code to that file would
change its SHA-256 and invalidate every existing Phase-1 receipt. Instead, the
validator selects the expected implementation source from the single
`runner_version` used by all rows in a receipt:

- `p3-phase1-unexecuted-v1` remains bound to the frozen historical
  `bridge_and_frames.py` runner SHA-256 already recorded in Phase-1 receipts;
- `p3-cxx-header-compile-profiler-v1` is bound to the current
  `profiling_runner.py` source SHA-256; and
- an unknown version, mixed versions, or a source-hash mismatch is rejected.

This corrects the existing runner-source binding so that it names the code that
actually produced each receipt. It does not add a second receipt schema or
rewrite historical evidence.

`scripts/p3_v3/profile.py` is a thin CLI adapter with one command,
`run-cxx-header-workload`. It accepts:

- the fixed `p3-profiling-workload-v1` JSON path;
- the restored controlled source root;
- the C++ compiler path;
- a new profiling runtime root; and
- a new profiling receipt path.

The output receipt uses the existing `p3-profiling-results-v1` schema and is
written with the existing canonical JSON primitives. The output path must not
already exist and is created exclusively. The formal receipt is separate from
the tracked Phase-1 placeholder.

The fixed Boost.Math execution uses:

- workload:
  `data/p3_v3/phase1_frames/out/profiling-workload-74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886.json`;
- workload artifact SHA-256:
  `982375e1fedb6ff26aa25e39cb1d65e45ff14474d4d34fca634c95ef352b036e`;
- source root: `/tmp/p3-boost-math-pilot-production-source`;
- compiler: `/usr/bin/c++`;
- runtime root: `/tmp/p3-boost-math-formal-header-profiling-v1`; and
- receipt:
  `data/p3_v3/profiling_runs/boost_math/profiling-results-74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886.json`.

## Per-behavior execution

The runner validates the workload before starting and requires exactly the 20
frozen rows for the selected Boost.Math snapshot. Results are executed and
serialized in ascending `behavior_id` order. Each behavior gets a distinct
directory beneath the new runtime root and this translation unit:

```cpp
#include "<frozen entrypoint>"
int main() { return 0; }
```

The compiler invocation uses the Attempt-2-proven C++ boundary:

- the explicitly supplied `/usr/bin/c++` compiler;
- `-std=c++14`;
- the controlled source root as the include root;
- compile-only output; and
- a compiler depfile for diagnostic evidence.

Each invocation uses `shell=False`, a new process session, a 120-second timeout,
captured stdout/stderr, and process-group termination and reap on timeout. A
failure or timeout for one row does not remove or replace that row and does not
prevent later frozen rows from running.

## Receipt semantics

Every selected behavior produces exactly one existing-schema result row:

| Observation | `status` | `failure_code` | Other required state |
| --- | --- | --- | --- |
| Compiler exits 0 | `MISSING_TRACE` | `NO_SUBJECT_CALL_TRACE` | exit 0, not timed out |
| Compiler exits nonzero | `FAILURE` | `COMPILE_NONZERO_EXIT` | observed nonzero exit |
| Compiler timeout | `TIMEOUT` | `COMPILE_TIMEOUT` | null exit, timed out |
| Compiler cannot start | `FAILURE` | `COMPILER_START_ERROR` | null exit, not timed out |

For every row:

- `argv` is the actual compiler argument vector;
- `input_sha256` binds the exact generated translation-unit bytes;
- `environment_sha256` binds compiler path, realpath, version output, C++14,
  include root, and relevant host identity;
- stdout and stderr are retained as raw files and hashed in the receipt;
- `call_trace` and `observed_site_ids` are empty;
- `call_trace_sha256` is the canonical hash of the empty list; and
- `runner_version` is a fixed implementation version string.

The complete receipt binds the existing workload, neutral snapshot, normalized
source tree, build descriptor, adapter implementation, and actual runner source.
It is passed through the existing receipt validator and `classify_technique`.

## Failure and durability behavior

Pre-entry failures, including a wrong workload, unsafe source/runtime path, or a
pre-existing output, produce no formal receipt. A missing compiler discovered
at entry also blocks the run; a per-row compiler start failure after entry is
recorded as `COMPILER_START_ERROR`. Once execution begins, row-level compiler
failures and timeouts remain in the full 20-row funnel. A process-control,
process-group cleanup, raw-log publication, or receipt-publication failure
aborts formal receipt publication and retains partial runtime evidence. Receipt
publication occurs only after all 20 terminal rows exist and validate.

Raw logs and generated translation units remain under the profiling runtime
root for diagnosis. The runner does not delete Attempt-2 evidence, the restored
source, qualification evidence, or its own completed output. A later execution
must use a new runtime root and output path; this design does not introduce a
global one-shot authorization mechanism.

## Minimal verification

Focused tests cover only the new behavior:

1. compile exit 0 yields `MISSING_TRACE`, never `SUCCESS`;
2. nonzero exit and timeout use the specified terminal classifications;
3. a failed row does not prevent complete workload coverage;
4. result rows are sorted and correspond one-to-one with the workload;
5. canonical receipt, self-hash, runner-source binding, existing validator, and
   classifier all accept the generated result;
6. a pre-existing output is not overwritten; and
7. the CLI passes its explicit paths to the production runner without adding
   scientific behavior.

No full-suite run, qualification rerun, Attempt-2 rerun, or unrelated refactor
is part of the implementation slice.

## Completion criterion

Implementation is ready for formal execution when focused tests pass and a
narrow Standards/Spec review finds no blocking issue. Formal execution is
complete when the production CLI produces a validator-accepted 20-row receipt
from the preserved Boost.Math source and reports the observed status funnel and
derived technique profile without claim inflation.
