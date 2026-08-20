# Execution packet 2026-08-20-011 — frozen BENCHMARK, official argv only

Issued after author: `点名下一冻结行；你先读官网/issue 再写 argv，不臆造`.
Record: `docs/review_20260819/official_docs_2026-08-20-nvector-serial-benchmark.md`.

010 closed frozen `[2]` EXAMPLE as `PASS` with empty extra argv.
This packet is a **new attempt** (`p2c-20260820-011`) on frozen
`selected_behavior_ids[3]` only:

`ade4089bc6d65c77e8aff681d61d4649f4edb42892292a307533513379b8f5ff`

Official `main` requires six extra CLI fields. Official docs and
issues give **no integers**. Instantiatable argv written from
official CMakeLists (program / target name only):

```text
["nvector_serial_benchmark"]
```

Do **not** append six numbers. Do **not** spawn. Do **not** pass
`BUILD_BENCHMARKS` / `SUNDIALS_ENABLE_BENCHMARKS`. Do **not** start
on an empty Cloud VM. Do **not** name the upstream project.

Prior cmake exception remains:
`docs/review_20260819/author_authorization_2026-08-19-one-archive-cmake.md`.

```text
EXECUTION_PACKET
packet_id: 2026-08-20-011
scientific_target: P2-C
correction_verdict: CLOSE_AND_ADVANCE
author_authorization: 点名下一冻结行；你先读官网/issue 再写 argv，不臆造
baseline_commit: 4444061dde0159a5edd62753fe3cef2d881a308c
branch: cursor/p2c-local-tar-benchmark-58d6
write_scope:
  - scripts/p3_v3/run_p2c_local_tar_benchmark.py
  - data/p3_v3/phase2_profiling/jobs/p2c-20260820-011/
  - data/p3_v3/phase2_profiling/local-tar-benchmark-terminal.json
  - data/p3_v3/handoff/2026-08-20-011.json
  - tests/p3_v3/test_phase2_p2c_local_tar_benchmark.py
forbidden:
  - Authority Lock / verifier hardening / 新授权链 / 资格认证 / Boost.Math
  - 修改 src/p3_v3/、evidence.py、pilot.py、run_p2c_one_row.py、run_p2c_process_row.py、run_p2c_one_archive_spawn.py、run_p2c_local_tar_spawn.py、run_p2c_local_tar_rebuild.py、run_p2c_local_tar_resolve.py、run_p2c_local_tar_object.py、run_p2c_local_tar_example.py、phase1_frames、protocol、pilot、preflight
  - git clone / sparse-checkout P12；34 个其他 archive；git clean -x
  - git add extracted/ archives/ _p2c_build/
  - cmake --build --target ltest
  - cmake --build --target cvDiurnal_kry_bp
  - cmake --build --target nvector_serial_benchmark
  - cmake --build --target test_nvector_performance_serial
  - BUILD_BENCHMARKS / SUNDIALS_ENABLE_BENCHMARKS / BENCHMARKS_INSTALL_PATH / SUNDIALS_BENCHMARK_NUM_CPUS / SUNDIALS_BENCHMARK_NUM_GPUS 作为 -D 或 argv
  - ENABLE_XBRAID / XBRAID_DIR / ENABLE_LAPACK
  - 任何臆造的六个整数（含 1000 10 10 1 0 0）；把 40 当作 vector length
  - 对本 BENCHMARK 二进制 spawn（含仅程序名以触发 argc<7）
  - 猜测的 cmake -D；brew / apt 猜包名
  - 默认 cmake --build（all）
  - spawn POSIX_TIMER_TEST/ltest；改 selected_behavior_ids；P2-D；claim 升级；P12 揭盲
acceptance_criteria:
  1. scripts/p3_v3/run_p2c_local_tar_benchmark.py 存在；create_intent/write_result；本地 tar file_sha256 == c7c3d38533c01a7366d2511497082af5f30f510d0f95db822d98441a06a1898c。源文件不得出现：--target ltest、--target cvDiurnal_kry_bp、--target nvector_serial_benchmark、BUILD_BENCHMARKS、SUNDIALS_ENABLE_BENCHMARKS、ENABLE_XBRAID、git clone、--filter=blob:none、P12-Defect4MR、qualify_cxx_link、boost_math、p3-phase1-unexecuted、PHASE1_PROFILING_NOT_EXECUTED、shutil.which。不得循环 35 条 bridge records。
  2. tracked 干净且 HEAD=4444061d… 时独占写出 intent.json 与 result.json。不得写 call_trace.json（本包禁止 spawn）。同目录必须有 benchmark-streams.json、cmake-help.stdout.txt 或 stderr、source-presence.json、benchmark-find.json、argv-resolution.json。
  3. intent 恰好 18 key：job_id=p2c-20260820-011、protocol_sha256=240d8270d41802c9d5b86f30564eadd1a86fd9ed09de2c7e947d17c1a4d78519、phase=PHASE_1、argv=["nvector_serial_benchmark"]（仅官网 CMake 目标/可执行名；无六个整数）、cwd_identity=data/p3_v3/p12_intake/extracted/1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72、input_sha256 升序三条 240d8270… / 8eeccfe4… / db46368c…、seed=null、timeout_seconds=60、attempt=1、object_type=PROFILING_BEHAVIOR、object_id=ade4089bc6d65c77e8aff681d61d4649f4edb42892292a307533513379b8f5ff、mr_id=not-applicable、evaluation_input_class=E_COMMON、evaluation_input_id=60c34610710b065bb3e0d649ce5a5b5badcfdf7147829445f925f7bdaab899a8、repetition_id=1、environment_id=p2c-local-tar-2026-08-20-011、job_role=PROFILING。environment_sha256 64 hex 且 ≠ 396e3df895988aafcaa276a51c6e2b6a46aef1f31017b84b2d22de4b81eb9007。selected_behavior_ids 自哈希仍为 e398d0a7764d44514d467c9170ba663457b7d38169354c4a310ffa3ffc37eca6。workload[3] 必须等于 object_id。
  4. source-presence.json：{"relative_path":"benchmarks/nvector/serial/test_nvector_performance_serial.c","is_regular_file":<bool>}。benchmark-find.json：普通文件名恰好为 nvector_serial_benchmark 的相对 posix 路径（排除路径分量 POSIX_TIMER_TEST、CMakeFiles、CMakeTmp、CompilerIdC、CompilerIdCXX）。本包即使 kept count==1 也不得 spawn。
  5. 本包新持久化 cmake --build <build> --target help。禁止 all。禁止任何 --target <name> 构建。把 configure / help 的 stdout/stderr 写入 job 目录；streams 记全文 sha256/nbytes（STREAM_LIMIT≥131072）。
  6. argv-resolution.json canonical keys：schema_version=p3-p2c-local-tar-benchmark-argv-v1、packet_id=2026-08-20-011、behavior_id=ade4089bc6d65c77e8aff681d61d4649f4edb42892292a307533513379b8f5ff、official_program_name=nvector_serial_benchmark、official_extra_argv_field_count=6、official_extra_argv_fields=["vector length","number of vectors","number of sums","number of tests","cache size (MB)","print timing"]、official_numeric_values_found=false、intent_argv=["nvector_serial_benchmark"]、spawn_authorized=false、help_has_target_nvector_serial_benchmark（bool；从 help 的 `... <name>` 解析，name 恰好为 nvector_serial_benchmark）、source_is_regular_file（bool）。
  7. result 恰好 11 key。scientific_outcome=null。failure_code 不得为 PHASE1_PROFILING_NOT_EXECUTED。允许且仅允许：(a) E_ARCHIVE_FETCH_FAILED；(b) E_ARCHIVE_UNSAFE；(c) E_CMAKE_CONFIGURE；(d) E_CMAKE_BUILD（仅 configure 或 help listing 失败）；(e) 源文件缺失或 help 无精确 target 或 official_numeric_values_found 为 false → E_PROFILE_BINARY_ABSENT。禁止 spawn，因此不得出现 PASS / E_PROFILE_TIMEOUT / E_PROFILE_NONZERO_EXIT。空列表 trace 仍为 37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570。result.call_trace_sha256 必须等于该空列表 SHA。
  8. local-tar-benchmark-terminal.json canonical，keys：schema_version=p3-p2c-local-tar-benchmark-terminal-v1、packet_id=2026-08-20-011、scientific_target=P2-C、neutral_snapshot_id=1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72、discovery_status=EXECUTABLE、adapter_id=CMAKE_CTEST_V1、behavior_id=ade4089bc6d6…、process_argv=["nvector_serial_benchmark"]、denominator=PROFILING_ONE_ROW、formal_denominator_membership=false、claims=blocked、result_status、result_failure_code、workload_file_sha256=db46368c…、selected_behavior_ids_sha256=e398d0a7…、artifact_sha256 自哈希。
  9. git diff --name-only 4444061d HEAD 全部落在 write_scope；不得 git add extracted/ archives/ _p2c_build/；不得改 006–010 脚本或 src/p3_v3。
  10. PYTHONPATH=src python3 -m pytest tests/p3_v3/test_phase2_p2c_local_tar_benchmark.py -q 退出 0；pytest 不调用 cmake。
  11. handoff/2026-08-20-011.json 含 packet_id、baseline_commit、head_commit、commands[]、input_sha256、output_sha256、failures_exclusions_retries、unresolved、closed_scientific_target（一句：P2-C 冻结 BENCHMARK 仅按官网程序名 argv 与默认 configure listing 尝试；六个整数未臆造；未 spawn；非 20 行；非 P2-D）。
out_of_list_policy: backlog_only
repair_cap: 0
handoff_path: data/p3_v3/handoff/2026-08-20-011.json
review_report_path: docs/review_20260819/2026-08-20-011_review.md
```

## Notes for executor

Desktop only. New script. Start from `4444061d`. Keep the gitignored
tar. Do not `git clean -x`. Do not reuse 009/010 as HEAD.

Official extra-argv schema (meanings only; do not fill integers):

```text
<vector length> <number of vectors> <number of sums>
<number of tests> <cache size (MB)> <print timing>
```

1. Re-hash the local tar; must be `c7c3d38533…`. Else stop.
2. Branch `cursor/p2c-local-tar-benchmark-58d6` from `4444061d`.
3. Extract; reject symlinks.
4. Confirm
   `extracted/benchmarks/nvector/serial/test_nvector_performance_serial.c`
   is a regular file. Write `source-presence.json`.
5. `cmake -S extracted -B extracted/_p2c_build` (no extra `-D`).
   Then `cmake --build … --target help`. Persist full streams.
   Record `help_has_target_nvector_serial_benchmark`.
6. Find kept regular files named `nvector_serial_benchmark`
   (exclusion list in criterion 4). Write `benchmark-find.json`.
   Do **not** `--target` build. Do **not** spawn, even if `count==1`.
7. Write `argv-resolution.json` with
   `official_numeric_values_found=false` and
   `spawn_authorized=false` (literals).
8. Book `E_PROFILE_BINARY_ABSENT` when source is missing, or help
   lacks the exact target, or numeric values remain unfound (this
   last clause is expected even if a listing line appears).
9. `environment_sha256` = canonical_sha256 of
   `{"dependency_lock_sha256":"7706b4ce272d09df13c5212b04ec0f2519932f4225d5eac0d052d3225c7ff35f","domain":"P3-P2C-LOCAL-TAR-BENCHMARK-ENV-v1","platform":<platform.system()>,"python":<platform.python_version()>}`.
10. Launch:

```bash
PYTHONPATH=src python3 scripts/p3_v3/run_p2c_local_tar_benchmark.py \
  --root . \
  --workload data/p3_v3/phase1_frames/out/profiling-workload-1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.json \
  --behavior-id ade4089bc6d65c77e8aff681d61d4649f4edb42892292a307533513379b8f5ff \
  --jobs-root data/p3_v3/phase2_profiling/jobs \
  --job-id p2c-20260820-011 \
  --terminal-output data/p3_v3/phase2_profiling/local-tar-benchmark-terminal.json
```

11. Packet pytest; evidence commit; handoff child:

```text
p3-v3(2026-08-20-011): P2-C local-tar BENCHMARK official argv only

Evidence: create_intent/write_result; status <STATUS> <code>
Target: P2-C
```

12. Push `-u origin cursor/p2c-local-tar-benchmark-58d6`. Stop. No
    P2-D. Do not merge 006–011.
