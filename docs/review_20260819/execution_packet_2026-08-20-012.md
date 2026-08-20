# Execution packet 2026-08-20-012 — frozen PROJECT_TEST, official argv only

Issued after author: `2，点名下一冻结行；你先读官网/issue 再写 argv，不臆造`.
Record: `docs/review_20260819/official_docs_2026-08-20-project-test-kinsol-unit.md`.

011 closed frozen `[3]` BENCHMARK as `E_PROFILE_BINARY_ABSENT`.
This packet is a **new attempt** (`p2c-20260820-012`) on frozen
`selected_behavior_ids[4]` only:

`04321f42383ae60108c6113034b91f1bda7e03a21090fe400895e58f70e2f69d`

Frozen `declared_inputs` `["ctest", "-R", "^NAME$"]` is the
unexpanded CMake keyword from `add_test(NAME ${test_name} …)`.
Official CMakeLists registers `kin_test_getuserdata` with **empty**
extra args. Instantiatable argv:

```text
["kin_test_getuserdata"]
```

Do **not** spawn `ctest -R`. Do **not** pass
`SUNDIALS_TEST_UNITTESTS`. Do **not** start on an empty Cloud VM.
Do **not** name the upstream project.

Prior cmake exception remains:
`docs/review_20260819/author_authorization_2026-08-19-one-archive-cmake.md`.

```text
EXECUTION_PACKET
packet_id: 2026-08-20-012
scientific_target: P2-C
correction_verdict: CLOSE_AND_ADVANCE
author_authorization: 2，点名下一冻结行；你先读官网/issue 再写 argv，不臆造
baseline_commit: 4444061dde0159a5edd62753fe3cef2d881a308c
branch: cursor/p2c-local-tar-project-test-58d6
write_scope:
  - scripts/p3_v3/run_p2c_local_tar_project_test.py
  - data/p3_v3/phase2_profiling/jobs/p2c-20260820-012/
  - data/p3_v3/phase2_profiling/local-tar-project-test-terminal.json
  - data/p3_v3/handoff/2026-08-20-012.json
  - tests/p3_v3/test_phase2_p2c_local_tar_project_test.py
forbidden:
  - Authority Lock / verifier hardening / 新授权链 / 资格认证 / Boost.Math
  - 修改 src/p3_v3/、evidence.py、pilot.py、run_p2c_one_row.py、run_p2c_process_row.py、run_p2c_one_archive_spawn.py、run_p2c_local_tar_spawn.py、run_p2c_local_tar_rebuild.py、run_p2c_local_tar_resolve.py、run_p2c_local_tar_object.py、run_p2c_local_tar_example.py、run_p2c_local_tar_benchmark.py、phase1_frames、protocol、pilot、preflight
  - git clone / sparse-checkout P12；34 个其他 archive；git clean -x
  - git add extracted/ archives/ _p2c_build/
  - cmake --build --target ltest
  - cmake --build --target cvDiurnal_kry_bp
  - cmake --build --target nvector_serial_benchmark
  - SUNDIALS_TEST_UNITTESTS / SUNDIALS_TEST_ENABLE_UNIT_TESTS / SUNDIALS_TEST_DEVTESTS 作为 -D
  - BUILD_BENCHMARKS / SUNDIALS_ENABLE_BENCHMARKS
  - ENABLE_XBRAID / XBRAID_DIR / ENABLE_LAPACK
  - spawn argv ["ctest", "-R", "^NAME$"] 或任何 ctest -R
  - 猜测的 cmake -D；brew / apt 猜包名
  - 默认 cmake --build（all）
  - spawn POSIX_TIMER_TEST/ltest；改 selected_behavior_ids；P2-D；claim 升级；P12 揭盲
acceptance_criteria:
  1. scripts/p3_v3/run_p2c_local_tar_project_test.py 存在；create_intent/write_result；本地 tar file_sha256 == c7c3d38533c01a7366d2511497082af5f30f510d0f95db822d98441a06a1898c。源文件不得出现：--target ltest、--target cvDiurnal_kry_bp、--target nvector_serial_benchmark、SUNDIALS_TEST_UNITTESTS、SUNDIALS_TEST_ENABLE_UNIT_TESTS、ENABLE_XBRAID、git clone、--filter=blob:none、P12-Defect4MR、qualify_cxx_link、boost_math、p3-phase1-unexecuted、PHASE1_PROFILING_NOT_EXECUTED、shutil.which。不得把 ctest -R 或 ^NAME$ 当作 spawn argv（写入 argv-resolution.rejected_unexpanded_argv 的字面量除外）。不得循环 35 条 bridge records。
  2. tracked 干净且 HEAD=4444061d… 时独占写出 intent.json 与 result.json。可选 call_trace.json（仅实际 spawn）。同目录必须有 project-test-streams.json、cmake-help.stdout.txt 或 stderr、ctest-list.stdout.txt 或同时写 head+tail 且 streams 记全文 sha256/nbytes、source-presence.json、project-test-find.json、argv-resolution.json。
  3. intent 恰好 18 key：job_id=p2c-20260820-012、protocol_sha256=240d8270d41802c9d5b86f30564eadd1a86fd9ed09de2c7e947d17c1a4d78519、phase=PHASE_1、argv=["kin_test_getuserdata"]（仅官网测试/可执行名；无额外 token；不得为 ctest -R ^NAME$）、cwd_identity=data/p3_v3/p12_intake/extracted/1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72、input_sha256 升序三条 240d8270… / 8eeccfe4… / db46368c…、seed=null、timeout_seconds=60、attempt=1、object_type=PROFILING_BEHAVIOR、object_id=04321f42383ae60108c6113034b91f1bda7e03a21090fe400895e58f70e2f69d、mr_id=not-applicable、evaluation_input_class=E_COMMON、evaluation_input_id=60c34610710b065bb3e0d649ce5a5b5badcfdf7147829445f925f7bdaab899a8、repetition_id=1、environment_id=p2c-local-tar-2026-08-20-012、job_role=PROFILING。environment_sha256 64 hex 且 ≠ 396e3df895988aafcaa276a51c6e2b6a46aef1f31017b84b2d22de4b81eb9007。selected_behavior_ids 自哈希仍为 e398d0a7764d44514d467c9170ba663457b7d38169354c4a310ffa3ffc37eca6。workload[4] 必须等于 object_id。
  4. source-presence.json：{"relative_path":"test/unit_tests/kinsol/C_serial/kin_test_getuserdata.c","is_regular_file":<bool>}。project-test-find.json：普通文件名恰好为 kin_test_getuserdata 的相对 posix 路径（排除路径分量 POSIX_TIMER_TEST、CMakeFiles、CMakeTmp、CompilerIdC、CompilerIdCXX）。
  5. 本包新持久化 cmake --build <build> --target help 与 ctest --test-dir <build> -N。禁止 all。仅当本包新持久化的 cmake help 含恰好一行 `... kin_test_getuserdata` 时，才允许 cmake --build <build> --target kin_test_getuserdata。把 configure / help / ctest -N /（若发生）该 build 的 stdout/stderr 写入 job 目录；ctest -N 写全文（STREAM_LIMIT≥131072）；streams 记全文 sha256/nbytes。
  6. argv-resolution.json canonical keys：schema_version=p3-p2c-local-tar-project-test-argv-v1、packet_id=2026-08-20-012、behavior_id=04321f42383ae60108c6113034b91f1bda7e03a21090fe400895e58f70e2f69d、official_program_name=kin_test_getuserdata、official_ctest_name=kin_test_getuserdata、rejected_unexpanded_argv=["ctest","-R","^NAME$"]、official_extra_argv=[]、intent_argv=["kin_test_getuserdata"]、help_has_target_kin_test_getuserdata（bool；help 的 `... <name>` 恰好为 kin_test_getuserdata）、ctest_has_name_kin_test_getuserdata（bool；`Test #<n>: <name>` 的 name 恰好为 kin_test_getuserdata）、source_is_regular_file（bool）。
  7. result 恰好 11 key。scientific_outcome=null。failure_code 不得为 PHASE1_PROFILING_NOT_EXECUTED。允许且仅允许：(a) E_ARCHIVE_FETCH_FAILED；(b) E_ARCHIVE_UNSAFE；(c) E_CMAKE_CONFIGURE；(d) E_CMAKE_BUILD（configure / help / ctest -N listing / 列出的 --target 失败）；(e) 源文件缺失或 help 无精确 target 或 kept 二进制 count≠1 → E_PROFILE_BINARY_ABSENT；(f) 对 kept 文件 spawn：PASS / E_PROFILE_TIMEOUT / E_PROFILE_NONZERO_EXIT。spawn 必须是 subprocess.run(["kin_test_getuserdata"], cwd=extracted_tree, timeout=60, capture_output=True, executable=str(binary))，不得附加其他 token，不得改走 ctest -R。空列表 trace 仍为 37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570。
  8. local-tar-project-test-terminal.json canonical，keys：schema_version=p3-p2c-local-tar-project-test-terminal-v1、packet_id=2026-08-20-012、scientific_target=P2-C、neutral_snapshot_id=1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72、discovery_status=EXECUTABLE、adapter_id=CMAKE_CTEST_V1、behavior_id=04321f42…、process_argv=["kin_test_getuserdata"]、denominator=PROFILING_ONE_ROW、formal_denominator_membership=false、claims=blocked、result_status、result_failure_code、workload_file_sha256=db46368c…、selected_behavior_ids_sha256=e398d0a7…、artifact_sha256 自哈希。
  9. git diff --name-only 4444061d HEAD 全部落在 write_scope；不得 git add extracted/ archives/ _p2c_build/；不得改 006–011 脚本或 src/p3_v3。
  10. PYTHONPATH=src python3 -m pytest tests/p3_v3/test_phase2_p2c_local_tar_project_test.py -q 退出 0；pytest 不调用 cmake 或 ctest。
  11. handoff/2026-08-20-012.json 含 packet_id、baseline_commit、head_commit、commands[]、input_sha256、output_sha256、failures_exclusions_retries、unresolved、closed_scientific_target（一句：P2-C 冻结 PROJECT_TEST 仅按官网 kin_test_getuserdata 空额外 argv 与本包 listing 尝试；未用 ^NAME$；未 ctest -R；非 20 行；非 P2-D）。
out_of_list_policy: backlog_only
repair_cap: 0
handoff_path: data/p3_v3/handoff/2026-08-20-012.json
review_report_path: docs/review_20260819/2026-08-20-012_review.md
```

## Notes for executor

Desktop only. New script. Start from `4444061d`. Keep the gitignored
tar. Do not `git clean -x`. Do not reuse 009–011 as HEAD.

Official extra-argv is **empty**. Rejected unexpanded argv is
`["ctest", "-R", "^NAME$"]`.

1. Re-hash the local tar; must be `c7c3d38533…`. Else stop.
2. Branch `cursor/p2c-local-tar-project-test-58d6` from `4444061d`.
3. Extract; reject symlinks.
4. Confirm
   `extracted/test/unit_tests/kinsol/C_serial/kin_test_getuserdata.c`
   is a regular file. Write `source-presence.json`.
5. `cmake -S extracted -B extracted/_p2c_build` (no extra `-D`).
   Then listing only:

```bash
cmake --build extracted/_p2c_build --target help
ctest --test-dir extracted/_p2c_build -N
```

   Persist full streams. `ctest -N` on 009 was 69144 bytes; write
   the **entire** stream (limit at least 131072).
6. Record `help_has_target_kin_test_getuserdata` and
   `ctest_has_name_kin_test_getuserdata`. Write
   `argv-resolution.json` with
   `rejected_unexpanded_argv=["ctest","-R","^NAME$"]` and
   `official_extra_argv=[]` (literals).
7. **Only if** this job’s help has the exact target:

```bash
cmake --build extracted/_p2c_build --target kin_test_getuserdata
```

   Do not pass `SUNDIALS_TEST_UNITTESTS`. Do not default-build `all`.
8. Find kept regular files named `kin_test_getuserdata` (exclusion
   list in criterion 4). Spawn **only** if `count==1`:

```python
subprocess.run(["kin_test_getuserdata"], cwd=extracted_tree, timeout=60, capture_output=True, executable=str(binary))
```

   If help lacks the exact target or kept≠1 →
   `E_PROFILE_BINARY_ABSENT`. Do not `ctest -R`.
9. `environment_sha256` = canonical_sha256 of
   `{"dependency_lock_sha256":"7706b4ce272d09df13c5212b04ec0f2519932f4225d5eac0d052d3225c7ff35f","domain":"P3-P2C-LOCAL-TAR-PROJECT-TEST-ENV-v1","platform":<platform.system()>,"python":<platform.python_version()>}`.
10. Launch:

```bash
PYTHONPATH=src python3 scripts/p3_v3/run_p2c_local_tar_project_test.py \
  --root . \
  --workload data/p3_v3/phase1_frames/out/profiling-workload-1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.json \
  --behavior-id 04321f42383ae60108c6113034b91f1bda7e03a21090fe400895e58f70e2f69d \
  --jobs-root data/p3_v3/phase2_profiling/jobs \
  --job-id p2c-20260820-012 \
  --terminal-output data/p3_v3/phase2_profiling/local-tar-project-test-terminal.json
```

11. Packet pytest; evidence commit; handoff child:

```text
p3-v3(2026-08-20-012): P2-C local-tar PROJECT_TEST official argv only

Evidence: create_intent/write_result; status <STATUS> <code>
Target: P2-C
```

12. Push `-u origin cursor/p2c-local-tar-project-test-58d6`. Stop.
    No P2-D. Do not merge 006–012.
