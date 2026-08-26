# Execution packet 2026-08-20-013 — frozen PUBLIC_API header, official empty process argv

Issued after author: `点名下一冻结行；你先读官网/issue 再写 argv，不臆造`.
Record: `docs/review_20260819/official_docs_2026-08-20-nvector-serial-header.md`.

012 closed frozen `[4]` PROJECT_TEST as `E_PROFILE_BINARY_ABSENT`.
This packet is a **new attempt** (`p2c-20260820-013`) on frozen
`selected_behavior_ids[5]` only:

`ab27acfcaaf2f1dbdbd965d57f645c4f948520bd4998f62c3cc8ccdfb3ccd320`

Official sources describe this object as an include + link library
API. Official subject process argv written from those sources:

```text
[]
```

`create_intent` rejects empty `argv`. Intent argv is therefore the
packet script invocation (003 precedent). That list is **not** a
subject CLI. Do **not** write `["nvector_serial"]`. Do **not**
redirect to `test_nvector_serial`. Do **not** compile. Do **not**
run cmake. Do **not** start on an empty Cloud VM. Do **not** name
the upstream project.

```text
EXECUTION_PACKET
packet_id: 2026-08-20-013
scientific_target: P2-C
correction_verdict: CLOSE_AND_ADVANCE
author_authorization: 点名下一冻结行；你先读官网/issue 再写 argv，不臆造
baseline_commit: 4444061dde0159a5edd62753fe3cef2d881a308c
branch: cursor/p2c-local-tar-header-serial-58d6
write_scope:
  - scripts/p3_v3/run_p2c_local_tar_header_serial.py
  - data/p3_v3/phase2_profiling/jobs/p2c-20260820-013/
  - data/p3_v3/phase2_profiling/local-tar-header-serial-terminal.json
  - data/p3_v3/handoff/2026-08-20-013.json
  - tests/p3_v3/test_phase2_p2c_local_tar_header_serial.py
forbidden:
  - Authority Lock / verifier hardening / 新授权链 / 资格认证 / Boost.Math
  - 修改 src/p3_v3/、evidence.py、pilot.py、run_p2c_one_row.py、run_p2c_process_row.py、run_p2c_one_archive_spawn.py、run_p2c_local_tar_spawn.py、run_p2c_local_tar_rebuild.py、run_p2c_local_tar_resolve.py、run_p2c_local_tar_object.py、run_p2c_local_tar_example.py、run_p2c_local_tar_benchmark.py、run_p2c_local_tar_project_test.py、phase1_frames、protocol、pilot、preflight
  - git clone / sparse-checkout P12；34 个其他 archive；git clean -x
  - git add extracted/ archives/ _p2c_build/
  - 调用 cmake / ctest / meson / autotools / 编译器 / cc / c++
  - cmake --build --target ltest / cvDiurnal_kry_bp / nvector_serial_benchmark / kin_test_getuserdata / test_nvector_serial
  - ENABLE_XBRAID / ENABLE_LAPACK / BUILD_BENCHMARKS / SUNDIALS_TEST_UNITTESTS / SUNDIALS_TEST_ENABLE_UNIT_TESTS / EXAMPLES_ENABLE_C 作为 -D
  - 臆造 subject CLI（含 nvector_serial、nvector_serial.h 当程序名）
  - 把 test_nvector_serial 或 1000 0 / 10000 0 当作本行 argv 或 spawn
  - 编译探测（cc -c / 写 .c 包一层 main）
  - 猜测的 cmake -D；brew / apt 猜包名
  - spawn POSIX_TIMER_TEST/ltest；改 selected_behavior_ids；P2-D；claim 升级；P12 揭盲
  - 把本关闭抄到 [0]/[9]/[13]/[17]
acceptance_criteria:
  1. scripts/p3_v3/run_p2c_local_tar_header_serial.py 存在；create_intent/write_result；本地 tar file_sha256 == c7c3d38533c01a7366d2511497082af5f30f510d0f95db822d98441a06a1898c。源文件不得出现：cmake、ctest、meson、autotools、--target ltest、--target test_nvector_serial、ENABLE_XBRAID、BUILD_BENCHMARKS、SUNDIALS_TEST_UNITTESTS、git clone、--filter=blob:none、P12-Defect4MR、qualify_cxx_link、boost_math、p3-phase1-unexecuted、PHASE1_PROFILING_NOT_EXECUTED、shutil.which、subprocess。不得循环 35 条 bridge records。
  2. tracked 干净且 HEAD=4444061d… 时独占写出 intent.json 与 result.json。不得写 call_trace.json。同目录必须有 source-presence.json 与 argv-resolution.json。
  3. intent 恰好 18 key：job_id=p2c-20260820-013、protocol_sha256=240d8270d41802c9d5b86f30564eadd1a86fd9ed09de2c7e947d17c1a4d78519、phase=PHASE_1、argv 恰好为 notes 的 14 项脚本调用（不得为空；不得为 nvector_serial / test_nvector_serial）、cwd_identity=data/p3_v3/p12_intake/extracted/1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72、input_sha256 升序三条 240d8270… / 8eeccfe4… / db46368c…、seed=null、timeout_seconds=60、attempt=1、object_type=PROFILING_BEHAVIOR、object_id=ab27acfcaaf2f1dbdbd965d57f645c4f948520bd4998f62c3cc8ccdfb3ccd320、mr_id=not-applicable、evaluation_input_class=E_COMMON、evaluation_input_id=60c34610710b065bb3e0d649ce5a5b5badcfdf7147829445f925f7bdaab899a8、repetition_id=1、environment_id=p2c-local-tar-2026-08-20-013、job_role=PROFILING。environment_sha256 64 hex 且 ≠ 396e3df895988aafcaa276a51c6e2b6a46aef1f31017b84b2d22de4b81eb9007。selected_behavior_ids 自哈希仍为 e398d0a7764d44514d467c9170ba663457b7d38169354c4a310ffa3ffc37eca6。workload[5] 必须等于 object_id。
  4. source-presence.json：{"relative_path":"include/nvector/nvector_serial.h","is_regular_file":<bool>}。
  5. argv-resolution.json canonical keys：schema_version=p3-p2c-local-tar-header-serial-argv-v1、packet_id=2026-08-20-013、behavior_id=ab27acfcaaf2f1dbdbd965d57f645c4f948520bd4998f62c3cc8ccdfb3ccd320、official_process_argv=[]、official_program_name=""、rejected_other_object_argv=["test_nvector_serial","1000","0"]、intent_argv=criterion 3 的 14 项、source_is_regular_file（bool）、subject_process_spawn_authorized=false。
  6. result 恰好 11 key。scientific_outcome=null。failure_code 不得为 PHASE1_PROFILING_NOT_EXECUTED。允许且仅允许：(a) FAIL_INFRASTRUCTURE / E_ARCHIVE_FETCH_FAILED；(b) FAIL_INFRASTRUCTURE / E_ARCHIVE_UNSAFE；(c) MISSING_WITH_REASON / E_SOURCE_TREE_ABSENT（无树且无匹配 archive）；(d) MISSING_WITH_REASON / E_SOURCE_FILE_ABSENT（树在但 header 不是普通文件）；(e) MISSING_WITH_REASON / E_PROFILE_NO_PROCESS_ARGV（header 是普通文件）。禁止 PASS / E_PROFILE_BINARY_ABSENT / E_PROFILE_TIMEOUT / E_PROFILE_NONZERO_EXIT。空列表 trace 仍为 37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570。result.call_trace_sha256 必须等于该空列表 SHA。
  7. local-tar-header-serial-terminal.json canonical，keys：schema_version=p3-p2c-local-tar-header-serial-terminal-v1、packet_id=2026-08-20-013、scientific_target=P2-C、neutral_snapshot_id=1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72、discovery_status=EXECUTABLE、adapter_id=CMAKE_CTEST_V1、behavior_id=ab27acfc…、process_argv=[]、denominator=PROFILING_ONE_ROW、formal_denominator_membership=false、claims=blocked、result_status、result_failure_code、workload_file_sha256=db46368c…、selected_behavior_ids_sha256=e398d0a7…、artifact_sha256 自哈希。
  8. git diff --name-only 4444061d HEAD 全部落在 write_scope；不得 git add extracted/ archives/ _p2c_build/；不得改 006–012 脚本或 src/p3_v3。
  9. PYTHONPATH=src python3 -m pytest tests/p3_v3/test_phase2_p2c_local_tar_header_serial.py -q 退出 0；pytest 不调用 cmake / 编译器。
  10. handoff/2026-08-20-013.json 含 packet_id、baseline_commit、head_commit、commands[]、input_sha256、output_sha256、failures_exclusions_retries、unresolved、closed_scientific_target（一句：P2-C 冻结 PUBLIC_API header 按官网空 process argv 入账；intent argv 仅为脚本调用；未改选 test_nvector_serial；未编译；非 20 行；非 P2-D）。
out_of_list_policy: backlog_only
repair_cap: 0
handoff_path: data/p3_v3/handoff/2026-08-20-013.json
review_report_path: docs/review_20260819/2026-08-20-013_review.md
```

## Notes for executor

Desktop only. New script. Start from `4444061d`. Keep the gitignored
tar. Do not `git clean -x`. Do not reuse 006–012 as HEAD.

Official **subject** process argv is empty. Intent argv is the
script invocation below.

1. Re-hash the local tar; must be `c7c3d38533…`. Else stop.
2. Branch `cursor/p2c-local-tar-header-serial-58d6` from `4444061d`.
3. Extract if needed; reject symlinks. Do **not** `git add` the tree.
4. Confirm
   `extracted/include/nvector/nvector_serial.h`
   is a regular file. Write `source-presence.json`.
5. Do **not** run cmake, ctest, or a compiler. Do **not** spawn.
6. Write `argv-resolution.json` with
   `official_process_argv=[]` and
   `rejected_other_object_argv=["test_nvector_serial","1000","0"]`
   (literals).
7. `environment_sha256` = canonical_sha256 of
   `{"dependency_lock_sha256":"7706b4ce272d09df13c5212b04ec0f2519932f4225d5eac0d052d3225c7ff35f","domain":"P3-P2C-LOCAL-TAR-HEADER-SERIAL-ENV-v1","platform":<platform.system()>,"python":<platform.python_version()>}`.
8. Fixed intent argv (also the script invocation from the repository
   root). `PYTHONPATH=src` is env, not argv:

```bash
PYTHONPATH=src python3 scripts/p3_v3/run_p2c_local_tar_header_serial.py \
  --root . \
  --workload data/p3_v3/phase1_frames/out/profiling-workload-1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.json \
  --behavior-id ab27acfcaaf2f1dbdbd965d57f645c4f948520bd4998f62c3cc8ccdfb3ccd320 \
  --jobs-root data/p3_v3/phase2_profiling/jobs \
  --job-id p2c-20260820-013 \
  --terminal-output data/p3_v3/phase2_profiling/local-tar-header-serial-terminal.json
```

   Intent `argv` must be exactly these 14 strings:

   `["python3","scripts/p3_v3/run_p2c_local_tar_header_serial.py","--root",".","--workload","data/p3_v3/phase1_frames/out/profiling-workload-1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.json","--behavior-id","ab27acfcaaf2f1dbdbd965d57f645c4f948520bd4998f62c3cc8ccdfb3ccd320","--jobs-root","data/p3_v3/phase2_profiling/jobs","--job-id","p2c-20260820-013","--terminal-output","data/p3_v3/phase2_profiling/local-tar-header-serial-terminal.json"]`
9. If the header is a regular file, result is
   `MISSING_WITH_REASON` / `E_PROFILE_NO_PROCESS_ARGV`.
   Empty-list trace `37517e5f…`. stdout/stderr may be empty-bytes
   `e3b0c442…`.
10. Packet pytest; evidence commit; handoff child:

```text
p3-v3(2026-08-20-013): P2-C local-tar PUBLIC_API header official empty argv

Evidence: create_intent/write_result; status <STATUS> <code>
Target: P2-C
```

11. Push `-u origin cursor/p2c-local-tar-header-serial-58d6`. Stop.
    No P2-D. Do not merge 006–013. Do not copy this close onto
    other headers.

This environment has no `rtk`. Use `python3`, `pytest`, `sha256sum`,
`git`. `PYTHONPATH=src` when importing `p3_v3`.
