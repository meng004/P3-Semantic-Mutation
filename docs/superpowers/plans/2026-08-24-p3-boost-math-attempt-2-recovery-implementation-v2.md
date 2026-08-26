# Boost.Math build-preflight Attempt-2 recovery implementation plan V2

> **Status:** controlling synthesized plan only. Implementation, qualification, and execution remain unauthorized. `RECOVERY_IMPLEMENTATION_HEAD=UNSET_UNTIL_INDEPENDENT_IMPLEMENTATION_PASS` until an independent implementation PASS pins it.

## 1. Scope and fixed authority

The frozen V1/V2/V3 designs and rejected Plan V1 are authority inputs, not content to re-embed. This plan preserves the single synthesized truth source. The implementation allowlist is exactly:

The frozen design authorities that the implementation verdict must bind are exactly:

```text
V1_PATH=docs/superpowers/specs/2026-08-24-p3-boost-math-build-preflight-attempt-2-recovery-design.md
V1_SHA256=a441fd68321e28f769447f19315c4b3bd82943888600126fe91bc66f3aec923b
V2_PATH=docs/superpowers/specs/2026-08-24-p3-boost-math-build-preflight-attempt-2-recovery-design-amendment-v2.md
V2_SHA256=a75cc3a3fecaafc26b59d32bb79fceac93f1a511f65a206b47ab497eacc2912f
V3_PATH=docs/superpowers/specs/2026-08-24-p3-boost-math-build-preflight-attempt-2-recovery-design-amendment-v3.md
V3_SHA256=b99c72f89704f582692dffdad8478efca56b4f75d17b0b7541b84cb0f311f3e3
REJECTED_PLAN_V1_PATH=docs/superpowers/plans/2026-08-24-p3-boost-math-attempt-2-recovery-implementation.md
REJECTED_PLAN_V1_SHA256=9d5192b78b103fb0213ed2947c15b3e207aec022241b6cac9520e07da73c3e8c
```

```text
src/p3_v3/pilot_source.py
src/p3_v3/pilot_build.py
scripts/p3_v3/pilot.py
tests/p3_v3/test_pilot_source.py
tests/p3_v3/test_pilot_build.py
tests/p3_v3/test_pilot.py
```

No runner, retry, resume, repair protocol, generic framework, root, schema, validator, or environment model may be added beyond the exact seams below. Tests are synthetic and may not run a real compiler, linker, CMake, qualification, workload, package manager, or network operation.

```python
QUALIFICATION_BASE_HEAD = "0e51252f23dc3be4f82eb99e4f493c103f38c620"
ATTEMPT2_AUTHORIZATION_PATH = Path("data/p3_v3/pilot/boost_math/user-auth-build-preflight-attempt-2.txt")
ATTEMPT2_AUTHORIZATION_BYTES = b"P3_BUILD_PREFLIGHT_ATTEMPT_2_AUTHORIZED=true\n"
ATTEMPT2_AUTHORIZATION_SHA256 = "fdb55d342c8e132a7377e4dcde1be16c3a2f736e76fe3edfc0cdc85bcfc79201"
ATTEMPT2_IMPLEMENTATION_VERDICT_PATH = Path("docs/review_20260824/boost_math_attempt_2_recovery_implementation_sol_high_review.md")
ATTEMPT2_INTENT_PATH = Path("data/p3_v3/pilot/boost_math/build-preflight-attempt-2-intent.json")
ATTEMPT2_RESULT_PATH = Path("data/p3_v3/pilot/boost_math/build-preflight-attempt-2-result.json")
ATTEMPT2_ARCHIVE_PATH = Path("/tmp/p3-boost-math-public-source-discovery/content-equivalence-r1/boost-math-dc86f3259c84f68ac7c4e2be11a1ed8567011240-projected.tar")
ATTEMPT2_SOURCE_ROOT = Path("/tmp/p3-boost-math-pilot-production-source")
ATTEMPT2_SOURCE_STAGING_ROOT = Path("/tmp/p3-boost-math-pilot-production-source.staging")
ATTEMPT2_BUILD_ROOT = Path("/tmp/p3-boost-math-pilot-build-preflight-attempt-2")
ATTEMPT2_LOG_ROOT = ATTEMPT2_BUILD_ROOT / "logs"
ATTEMPT2_HARNESS_ROOT = Path("/tmp/p3-boost-math-pilot-build-preflight-attempt-2-harness")
```

The new production interfaces are frozen exactly; do not rename them, add caller-selected authority paths, or vary their parameters or return types:

```python
# src/p3_v3/pilot_source.py
def validate_source_restoration_evidence(value: object) -> dict[str, Any]: ...
def run_restore_production_source(archive: Path, materialize_root: Path) -> dict[str, Any]: ...

# src/p3_v3/pilot_build.py
def read_v5_qualification_evidence(
    qualification_root: Path = QUALIFICATION_ROOT,
) -> dict[str, Any]: ...
def resolve_cmake_executable_path() -> str: ...
def run_metadata_cmake_version(cmake_path: str, log_root: Path) -> dict[str, Any]: ...
def validate_attempt2_intent(value: object) -> dict[str, Any]: ...
def validate_attempt2_result(value: object) -> dict[str, Any]: ...
def validate_attempt2_phase_result(value: object) -> dict[str, Any]: ...
def validate_attempt2_environment(value: object) -> dict[str, Any]: ...
def run_build_preflight_attempt_2(
    archive: Path,
    source_root: Path,
    build_root: Path,
) -> dict[str, Any]: ...
```

There are exactly two Attempt-2 runtime roots, build and harness; `logs` is a safe child of build. The source staging sibling is not another durable runtime root. `include/boost/math` is validated content beneath the published production root and is never a staging-root constant.

The frozen archive is the exact path above, SHA-256 `6cad33704c8341995f271d93811dd3cf9751ed5edf8b9a73882662acd3db0392`, `99676160` bytes, format `TAR`. Its normalized materialized tree is SHA-256 `93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8`, `4396` files, `95635487` bytes. The closed PASS pair is the tracked `data/p3_v3/pilot/boost_math/source-manifest.json` and `data/p3_v3/pilot/boost_math/source-preparation-result.json`; preserve it byte-for-byte.

Existing identities used by intent/result remain:

```text
P12_ITEM_ID=C-BOOSTMATH-001
NEUTRAL_SNAPSHOT_ID=74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886
normalized_source_tree_sha256=93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8
CONTROLLED_SUBJECT_ID=89b0e6791c611b465b9216e833e0c526a53ffd6946b5cd20de045e3641f43914
CONTROLLED_SUBJECT_SOURCE_ID=e5f21a7d067d641d0a20bfc57c61e630d6f7588ef30235cea49c9a9cf950c7a7
BUILD_DESCRIPTOR_SHA256=68d2e0fd34b845bb0df22b29003f26259d5655d2ec80c18895ff36904db2d95d
SOURCE_PREPARATION_RESULT_VERDICT_SHA256=43cedfd21621496f61feec1418b2ec4d9e02b51096c477b0d221067d1e1ed7f2
SOURCE_MANIFEST_FILE_SHA256=d774143f6a0dc6cf24a9ddda8b4e9760b3d547e03cbd21e16d84220f826073c5
SOURCE_PREPARATION_RESULT_FILE_SHA256=6a525ff074f5ab67f4a58af0a4f7f2264f3888757513a8fc80fb6760c8b577b9
SOURCE_PREPARATION_REVIEWED_COMMIT=44acee8882b004f50005cd39ca732bc6f09604fa
HARNESS_CMAKE_SHA256=2bdbb40e8d6fbd488ddde7bda4b855047361bedc1e7c4c9a5e72bf971d602a8b
HARNESS_CXX_SHA256=609c8990cef0cad5a1e448f11e8353dbc6c040e88778b72fac64ea6a6b4002ed
```

Attempt-1 durable paths remain `data/p3_v3/pilot/boost_math/build-preflight-intent.json` and `data/p3_v3/pilot/boost_math/build-preflight-result.json`; runtime paths remain `/tmp/p3-boost-math-pilot-build-preflight` and `/tmp/p3-boost-math-pilot-build-preflight-harness`. Its focused regression checks only those paths, recorded `NONZERO_EXIT`, refusal `E_PILOT_BUILD_PREEXISTING`, and that Attempt-2 writes nothing into Attempt-1.

## 2. Canonical objects and claim ceiling

The existing artifact helper truth is exact: `canonical_json_bytes` produces sorted, compact UTF-8 JSON with exactly one terminal LF; `canonical_sha256` hashes all those bytes, including that LF. Every self-hash is computed over the object without `artifact_sha256`, using that helper. No byte baseline or broad string gate is introduced.

Every Attempt-2 schema/object uses `execution_class="PILOT_ONLY"`, `denominator="PILOT_ONLY"`, `claims="blocked"`, `formal_denominator_membership=False`, `rq4_supported=False`, `attempt_2_authorized=False`, and `no_retry=True` wherever those fields are present. `PILOT_BUILD_PREFLIGHT_ATTEMPT_2` is not an execution-class value. The result has five ordered phases and never `jobs`; `NOT_STARTED` has no process/output/time/resource evidence.

The following maps are the complete exact-key schemas; no focused-draft or chat reference is required:

```python
ATTEMPT2_ENVIRONMENT_SCHEMA = "p3-pilot-build-preflight-attempt-2-environment-v1"
ATTEMPT2_PHASE_SCHEMA = "p3-pilot-build-preflight-attempt-2-phase-v1"
ATTEMPT2_INTENT_SCHEMA = "p3-pilot-build-preflight-attempt-2-intent-v1"
ATTEMPT2_RESULT_SCHEMA = "p3-pilot-build-preflight-attempt-2-result-v1"
```

```python
ATTEMPT2_ENVIRONMENT_EXACT = {
 "schema_version": str, "execution_class": str, "denominator": str,
 "cmake_executable": str, "cmake_executable_path": str, "cmake_version": (str, type(None)),
 "cxx_compiler_executable": (str, type(None)), "cxx_compiler_path": (str, type(None)),
 "cxx_compiler_identity": (str, type(None)), "cxx_compiler_version": (str, type(None)),
 "cmake_generator": str, "os_name": str, "os_release": str, "python_version": str,
 "git_version": (str, type(None)), "build_parallelism": int, "nvcc_present": bool,
 "native_profiling_present": bool, "cuda_absence_blocking": bool,
 "fetchcontent_fully_disconnected": bool, "system_boost_fallback_accepted": bool,
 "disconnected_environment": dict, "qualification_evidence_sha256": str,
 "verification_scope": str, "executor_cloud_run_id": (str, type(None)),
 "executor_build_snapshot_id": (str, type(None)), "claims": str, "artifact_sha256": str,
}
ATTEMPT2_PHASE_EXACT = {
 "schema_version": str, "execution_class": str, "denominator": str, "phase_id": str,
 "phase_kind": str, "dependency_phase_ids": list, "argv": list, "timeout_seconds": int,
 "process_started": bool, "process_group_terminated": (bool, type(None)),
 "infrastructure_phase": (str, type(None)), "terminal_status": str,
 "failure_reason": (str, type(None)), "exit_code": (int, type(None)),
 "stdout_sha256": (str, type(None)), "stderr_sha256": (str, type(None)),
 "stdout_bytes": (int, type(None)), "stderr_bytes": (int, type(None)),
 "started_at": (str, type(None)), "ended_at": (str, type(None)),
 "wall_seconds": (float, type(None)), "cpu_seconds": (float, type(None)),
 "peak_rss_bytes": (int, type(None)), "source_restoration_evidence": (dict, type(None)),
 "claims": str, "artifact_sha256": str,
}
ATTEMPT2_INTENT_EXACT = {
 "schema_version": str, "execution_class": str, "denominator": str, "plan_class": str,
 "p12_item_id": str, "neutral_snapshot_id": str, "normalized_source_tree_sha256": str,
 "controlled_subject_id": str, "controlled_subject_source_id": str, "build_descriptor_sha256": str,
 "source_preparation_verdict_sha256": str, "source_manifest_sha256": str,
 "source_preparation_result_sha256": str, "source_preparation_reviewed_commit": str,
 "attempt1_implementation_verdict_sha256": str, "attempt2_implementation_verdict_sha256": str,
 "authorization_sha256": str, "harness_cmake_sha256": str, "harness_cxx_sha256": str,
 "source_root": str, "build_root": str, "harness_root": str, "log_root": str, "archive_path": str,
 "qualification_base_head": str, "qualification_evidence_sha256": str,
 "cmake_metadata_argv": list, "cmake_configure_argv": list, "baseline_build_argv": list,
 "baseline_smoke_argv": list, "cmake_version_timeout_seconds": int,
 "cmake_configure_timeout_seconds": int, "baseline_build_timeout_seconds": int,
 "baseline_smoke_timeout_seconds": int, "outer_timeout_seconds": int, "build_parallelism": int,
 "planned_count": int, "dependency_dag": list, "phase_order": list,
 "environment_snapshot": dict, "environment_snapshot_sha256": str, "producer_pid": int,
 "producer_starttime": str, "predecessor_sha256": list, "no_retry": bool, "claims": str,
 "formal_denominator_membership": bool, "rq4_supported": bool, "attempt_2_authorized": bool,
 "verification_scope": str, "executor_cloud_run_id": (str, type(None)),
 "executor_build_snapshot_id": (str, type(None)), "artifact_sha256": str,
}
ATTEMPT2_RESULT_EXACT = {
 "schema_version": str, "execution_class": str, "denominator": str, "p12_item_id": str,
 "neutral_snapshot_id": str, "normalized_source_tree_sha256": str, "controlled_subject_id": str,
 "controlled_subject_source_id": str, "build_descriptor_sha256": str,
 "source_preparation_verdict_sha256": str, "source_manifest_sha256": str,
 "source_preparation_result_sha256": str, "attempt1_implementation_verdict_sha256": str,
 "attempt2_implementation_verdict_sha256": str, "intent_sha256": str, "authorization_sha256": str,
 "qualification_base_head": str, "qualification_evidence_sha256": str,
 "environment_snapshot": dict, "environment_snapshot_sha256": str,
 "harness_cmake_sha256": str, "harness_cxx_sha256": str,
 "cmake_cache_sha256": (str, type(None)), "compile_commands_sha256": (str, type(None)),
 "compiler_depfile_sha256": (str, type(None)), "dependency_list_sha256": (str, type(None)),
 "smoke_executable_sha256": (str, type(None)), "source_root": str, "build_root": str,
 "harness_root": str, "log_root": str, "archive_path": str, "planned_count": int,
 "started_count": int, "terminal_count": int, "not_started_count": int, "phase_order": list,
 "phases": list, "source_restoration_disposition": (str, type(None)), "terminal_status": str,
 "failure_reason": (str, type(None)), "build_root_exists": bool, "build_root_is_symlink": bool,
 "no_retry": bool, "claims": str, "formal_denominator_membership": bool, "rq4_supported": bool,
 "attempt_2_authorized": bool, "verification_scope": str,
 "executor_cloud_run_id": (str, type(None)), "executor_build_snapshot_id": (str, type(None)),
 "predecessor_sha256": list, "artifact_sha256": str,
}
IMPLEMENTATION_VERDICT_EXACT = {
 "schema_version": str, "verdict": str, "reviewed_commit": str,
 "qualification_base_head": str, "v1_design_sha256": str, "v2_design_sha256": str,
 "v3_design_sha256": str, "approved_implementation_plan_sha256": str,
 "reviewed_blob_sha256": dict, "formal_denominator_membership": bool, "claims": str,
 "attempt_2_authorized": bool, "rq4_supported": bool, "artifact_sha256": str,
}
IMPLEMENTATION_VERDICT_REVIEWED_BLOB_EXACT = {
 "rejected_plan_v1": str,
 "src/p3_v3/pilot_source.py": str, "src/p3_v3/pilot_build.py": str,
 "scripts/p3_v3/pilot.py": str, "tests/p3_v3/test_pilot_source.py": str,
 "tests/p3_v3/test_pilot_build.py": str, "tests/p3_v3/test_pilot.py": str,
}
```

Schema constraints are exact: environment reuses the V5 compiler/git/host evidence and current baseline fields; nested `environment_snapshot_sha256` equals its `artifact_sha256`. Intent requires the frozen identities/paths/argv/timeouts, `plan_class="PILOT_BUILD_PREFLIGHT_ATTEMPT_2_ONLY"`, planned count 5, the five dependency lists, producer PID/starttime, and all predecessor bindings; its CMake version is null before metadata. Each phase requires `phase_id == phase_kind`, the dependency list in Section 3, and status in `PASS|FAIL|TIMEOUT|FAIL_INFRASTRUCTURE|NOT_STARTED`; only `SOURCE_RESTORE` carries restoration evidence and starts no process. Result repeats the intent bindings, contains exactly five ordered phases, derives all counts from them, binds the current intent hash, and enforces `NOT_STARTED` after the first non-PASS. The implementation verdict requires schema `p3-pilot-attempt2-recovery-implementation-verdict-v1`, `verdict="PASS"`, the later pinned reviewed commit, frozen qualification/design/approved-plan hashes, the exact seven current regular-file hashes (including rejected Plan V1 `9d5192b78b103fb0213ed2947c15b3e207aec022241b6cac9520e07da73c3e8c`), the claim ceiling, and canonical self-hash.

### Source restoration evidence

```python
SOURCE_RESTORATION_SCHEMA = "p3-pilot-source-restoration-evidence-v1"
SOURCE_RESTORATION_EVIDENCE_EXACT = {
    "schema_version": str,
    "execution_class": str,
    "claims": str,
    "disposition": str,
    "archive_sha256": str,
    "archive_bytes": int,
    "normalized_tree_sha256": str,
    "materialized_file_count": int,
    "materialized_total_bytes": int,
    "staging_published": bool,
    "root_published": bool,
    "started_at": str,
    "ended_at": str,
    "terminal_status": str,
    "failure_reason": (str, type(None)),
    "artifact_sha256": str,
}
```

Keys are exact. Values require the schema above, `execution_class="PILOT_ONLY"`, `claims="blocked"`, disposition in `RESTORED|REVALIDATED|NOT_APPLIED`, and terminal status in `PASS|FAIL`. Timestamps are nonempty UTC timestamps with `started_at <= ended_at`. PASS requires null failure, the frozen archive/tree metrics, and either `(RESTORED, staging_published=True, root_published=True)` or `(REVALIDATED, False, False)`. FAIL requires `NOT_APPLIED`, a non-null reason, and both publication flags false. The complete frozen failure-reason set is `WRONG_ARCHIVE_PATH`, `WRONG_SOURCE_ROOT`, `ARCHIVE_UNSAFE`, `ARCHIVE_HASH_MISMATCH`, `ARCHIVE_SIZE_MISMATCH`, `ARCHIVE_FORMAT_MISMATCH`, `EXTRACTION_UNSAFE`, `STAGING_EXISTS`, `STAGING_SYMLINK`, `ROOT_SYMLINK`, `INVALID_RECONCILIATION_STATE`, `TREE_HASH_MISMATCH`, `FILE_COUNT_MISMATCH`, `BYTE_COUNT_MISMATCH`, and `INVALID_PASS_PAIR`. `artifact_sha256` is the canonical self-hash, including canonical LF.

Legal reconciliation states remain only `INVALID_PASS_NO_ROOT` and `ALREADY_COMPLETE`. For the former, extract the frozen archive into exactly `/tmp/p3-boost-math-pilot-production-source.staging`, validate the complete normalized tree, metrics, tracked manifest/result pair, and `include/boost/math`, then and only then publish with atomic `os.replace(staging, production_root)`. For the latter, change nothing and fully revalidate the published root. Partial, mismatched, symlink, or preexisting staging states fail without repair.

### V5 qualification binding

```python
QUALIFICATION_ROOT = Path("/tmp/p3-cxx-link-qualification")
QUALIFICATION_INTENT_NAME = "qualification-intent.json"
QUALIFICATION_RESULT_NAME = "qualification-result.json"
QUALIFICATION_MANIFEST_NAME = "qualification-manifest.json"
QUALIFICATION_SOURCE_NAME = "qualify.cpp"
QUALIFICATION_EXECUTABLE_NAME = "qualify"
QUALIFICATION_CXX_STDOUT_NAME = "METADATA_CXX_VERSION.stdout"
QUALIFICATION_CXX_STDERR_NAME = "METADATA_CXX_VERSION.stderr"
QUALIFICATION_INTENT_SHA256 = "0a13766c565e89e32a21bc69ba0f449dc8a79c48a66a7bcace54c63faa224860"
QUALIFICATION_RESULT_SHA256 = "68aaac07c2d5ad4f834f114e1a0ac011052176f2a20ea63793f483357c31f6c2"
QUALIFICATION_MANIFEST_SHA256 = "5ef4c89e9601303b9e40e3fcda07c68055664cf53fb578d6efb1d39fc5f27c9a"
QUALIFICATION_SOURCE_SHA256 = "91193433e324b0a1e525cfecac51f43ca0f6bd882e1c34292510c9740115bf5c"
QUALIFICATION_EXECUTABLE_SHA256 = "9d24d5298272942e95333acf18b05052b4c9d701aeaf92f7252a4d9666228b3b"
FROZEN_CXX_PATH = "/usr/bin/c++"
FROZEN_CXX_REALPATH = "/usr/lib/llvm-18/bin/clang"
ATTEMPT2_QUALIFICATION_EVIDENCE_EXACT = {
 "schema_version": str, "execution_class": str, "claims": str,
 "qualification_root": str, "qualification_base_head": str,
 "intent_sha256": str, "result_sha256": str, "manifest_sha256": str,
 "source_sha256": str, "executable_sha256": str,
 "compiler_version_stdout_sha256": str, "compiler_version_stderr_sha256": str,
 "compiler_version_stdout": str, "compiler_version_stderr": str,
 "requested_compiler": str, "resolved_compiler_path": str,
 "resolved_compiler_realpath": str, "current_cxx_realpath": str,
 "host_git_version": str, "host_snapshot_sha256": str,
 "terminal_status": str, "failure_reason": (str, type(None)),
 "verification_scope": str, "artifact_sha256": str,
}
```

The qualification schema is `p3-pilot-attempt-2-qualification-evidence-v1`; keys are exact, Cloud IDs are absent, `execution_class="PILOT_ONLY"`, `claims="blocked"`, root/base HEAD/hashes/compiler paths equal the frozen values, status is PASS with null failure, and scope is `ARTIFACT_HASH_AND_HOST_SNAPSHOT`. The adapter re-reads all seven safe regular files, validates fixed hashes and the canonical intent/result/manifest cross-links, re-reads and hashes compiler-version stdout/stderr, cross-validates their bytes against V5 result records, and cross-validates the host snapshot and git version between V5 intent/result. It may use `os.path.realpath` to confirm current `/usr/bin/c++`; it must not rerun qualification, `c++ --version`, `git --version`, `probe_identity`, or `make_environment_snapshot`, and makes no Cloud-ID proof claim. Its `artifact_sha256` is the canonical-LF self-hash.

## 3. Environment and process seam

Do not create the draft's `PATH/LANG/LC_ALL/TZ` allowlist and make no `cwd` claim. Copy the current environment, call existing `reject_system_boost_environment`, update only the existing `DISCONNECTED_ENVIRONMENT`, and call existing `reject_unbound_toolchain` using the V5-qualified `/usr/bin/c++`. This preserves all current forbidden Boost and toolchain environment controls and the single deep environment model.

All four process phases call the same existing `execute_job(spec, env=environment, log_root=ATTEMPT2_LOG_ROOT)` object. There is no `cwd` parameter or extension, no reimplementation, `subprocess.run`, `check_output`, or `os.system`. Preserve start marker, `shell=False`, new session/process group, PID/PGID/starttime identity, communicate/timeout termination and reap, leak check, raw timing/CPU/RSS evidence. Logs are exactly `{job_id}.start.json`, `{job_id}.identity.json`, `{job_id}.stdout`, `{job_id}.stderr` below build-root `logs`.

Every argv item below is a string:

| phase | exact dependency list | argv | timeout |
|---|---|---|---:|
| `METADATA_CMAKE_VERSION` | `[]` | `[resolved_cmake_path, "--version"]` | 10 |
| `SOURCE_RESTORE` | `["METADATA_CMAKE_VERSION"]` | `[]` (no process/log) | 0 |
| `CMAKE_CONFIGURE` | `["SOURCE_RESTORE"]` | `[resolved_cmake_path,"-S","/tmp/p3-boost-math-pilot-build-preflight-attempt-2-harness","-B","/tmp/p3-boost-math-pilot-build-preflight-attempt-2","-G","Unix Makefiles","-DCMAKE_BUILD_TYPE=Release","-DCMAKE_CXX_STANDARD=14","-DCMAKE_CXX_STANDARD_REQUIRED=ON","-DBOOST_MATH_STANDALONE=1","-DBOOST_MATH_PILOT_SOURCE_INCLUDE=/tmp/p3-boost-math-pilot-production-source/include","-DCMAKE_DISABLE_SOURCE_CHANGES=ON","-DCMAKE_DISABLE_IN_SOURCE_BUILD=ON","-DFETCHCONTENT_FULLY_DISCONNECTED=ON","-DFETCHCONTENT_UPDATES_DISCONNECTED=ON","-DCMAKE_FIND_USE_PACKAGE_REGISTRY=OFF","-DCMAKE_FIND_USE_SYSTEM_PACKAGE_REGISTRY=OFF","-DCMAKE_EXPORT_COMPILE_COMMANDS=ON","-DCMAKE_CXX_COMPILER=/usr/bin/c++"]` | 900 |
| `BASELINE_BUILD` | `["CMAKE_CONFIGURE"]` | `[resolved_cmake_path,"--build","/tmp/p3-boost-math-pilot-build-preflight-attempt-2","--parallel","4"]` | 3600 |
| `BASELINE_SMOKE` | `["BASELINE_BUILD"]` | `["/tmp/p3-boost-math-pilot-build-preflight-attempt-2/boost_math_pilot_smoke"]` | 1800 |

The configure/build/smoke forms are the existing frozen forms adapted only to Attempt-2 roots. Build evidence validation remains focused on safe current CMake cache, compile commands, depfile/dependency list, and smoke executable identities.

## 4. One-shot DAG and publication

The five phase dependency lists are exactly those in the table; the order is metadata, source, configure, build, smoke. The one-shot sequence is:

1. Read-only entry gates validate detached recovery commit, tracked identity, exact permitted untracked authorities, authorization bytes, current verdict, V5 evidence, frozen archive, focused Attempt-1 evidence, absent safe Attempt-2 paths, and one of the two legal source states. Failure writes nothing.
2. Exclusive-create canonical intent **before** build/log/harness root creation and before every process. A preexisting intent/result permanently refuses with `E_PILOT_ATTEMPT2_PREEXISTING`; no retry/resume.
3. After intent, exclusively create build root and safe `logs`, call the common executor for metadata, restore/revalidate source, exclusively publish harness, then configure, build, and smoke through the same executor.
4. On the first non-PASS, append exact `NOT_STARTED` records for every later phase. Exclusively create and validate result; preserve intent if result publication fails; stop.

Intent and result use the exact maps and constraints above, including the seven-key verdict binding, fixed identities, exact two roots, paths, timeout `OUTER_TIMEOUT_SECONDS=7200`, `BUILD_PARALLELISM=4`, `planned_count=5`, predecessor hashes, and ceiling. Result publication is exclusive, has exactly five phases, counts derived from them, and records restoration disposition `RESTORED` or `REVALIDATED` only when reached.

Add exactly one CLI command, `build-preflight-attempt-2`, using existing CLI style and three frozen path arguments. There is no restore CLI. Preserve all existing command names, arguments, delegation, exit mapping, and output schemas.

## 5. Executable TDD tasks

1. **Restoration seam:** in `pilot_source.py` and its test, first add synthetic failures for the exact staging sibling, archive hash/bytes/format, normalized tree hash/file/byte metrics, content under published `include/boost/math`, both legal reconciliation states, exact evidence keys/allowed dispositions/PASS-FAIL constraints/failure set/timestamps/publication flags/canonical-LF hash, atomic publication, and no repair. Implement minimally at existing archive/extraction/tree/manifest seams.
2. **V5 adapter and schemas:** in `pilot_build.py` and its test, first cover all seven required filenames, five fixed hashes, compiler paths, cross-links, stdout/stderr and host snapshot re-read, canonical-LF self-hash, symlink/mismatch/non-PASS rejection, `PILOT_ONLY` ceiling, and monkeypatch all process/probe entry points to prove no process. Implement only `read_v5_qualification_evidence` at existing authority readers.
3. **Environment/process/DAG:** add behavior tests that the exact same monkeypatched `execute_job` object receives metadata/configure/build/smoke, each with copied/current environment processed by existing rejection helpers plus only `DISCONNECTED_ENVIRONMENT`, no `cwd`, exact string argv, Attempt-2 roots/log names, all five exact dependency lists, intent-before-root/process, and failure padding with `NOT_STARTED`. Do not add a brittle implementation-shape test.
4. **Orchestration/publication:** cover permanent preexistence refusal, exclusive intent/result, safe roots, source then exclusive harness, first-failure stop, ceiling fields, focused build evidence, and no Attempt-1 writes. Implement the one-shot coordinator using existing validators/writers/`execute_job`.
5. **CLI and observable regressions:** add only the one command and synthetic delegation tests; retain focused regressions for existing commands and Attempt-1 paths, `NONZERO_EXIT`, and `E_PILOT_BUILD_PREEXISTING`. Do not baseline source/function/parser bytes and do not use broad string scans.

For every task, add the named tests first and run the corresponding focused command before production edits; expected RED is collection failure or assertion failure caused only by the absent Attempt-2 seam. Add the smallest Green change described above, rerun the same command, and require every selected test to PASS:

```bash
PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot_source.py -k 'attempt2_restore or source_restoration_evidence' -q
PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot_build.py -k 'attempt2_v5_adapter or attempt2_exact_schema or implementation_verdict_exact or canonical_lf' -q
PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot_build.py -k 'attempt2_descriptor or attempt2_execute_job or attempt2_dependency or attempt2_environment' -q
PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot_build.py -k 'attempt2_orchestration or attempt2_publication or attempt2_not_started' -q
PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot.py tests/p3_v3/test_pilot_build.py -k 'build_preflight_attempt_2 or attempt1_observable or e_pilot_build_preexisting' -q
```

After all focused Green steps, run exactly the three synthetic test modules and the two ordinary diff checks:

```bash
PYTHONPATH=src python3 -m pytest tests/p3_v3/test_pilot_source.py tests/p3_v3/test_pilot_build.py tests/p3_v3/test_pilot.py -q
git diff --check -- src/p3_v3/pilot_source.py src/p3_v3/pilot_build.py scripts/p3_v3/pilot.py tests/p3_v3/test_pilot_source.py tests/p3_v3/test_pilot_build.py tests/p3_v3/test_pilot.py
git diff --name-only
```

Expected final verification: all synthetic tests PASS, `diff --check` is empty, and `diff --name-only` is a subset of the exact six-file allowlist. Do not run broad string scans or real tools/workloads. Stop before commit; implementation remains unauthorized until independent review pins a real recovery commit and a valid current verdict.
