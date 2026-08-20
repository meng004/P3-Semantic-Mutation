# Execution packet 2026-08-20-010 — listed EXAMPLE target, documented empty extra-argv

Issued after author: `读取被测程序的官网帮助文档或issue，不瞎猜参数取值及其意义。`
Record: `docs/review_20260819/official_docs_2026-08-20-ltest-and-example.md`.

009 closed the pinned CLI (`ltest`) as `E_PROFILE_BINARY_ABSENT`.
Official install/issues show `ltest` is a CMake TPL/Check\* binary,
not a user CLI. This packet does **not** pass `ENABLE_XBRAID` or
retry `ltest`.

This is a **new attempt** (`p2c-20260820-010`) on frozen
`selected_behavior_ids[2]` only. cmake `--target cvDiurnal_kry_bp`
is allowed because that **exact** name is already in 009
`cmake-help.stdout.txt`. Official example `main` is `int main(void)`:
**no extra argv tokens**.

Do **not** start on an empty Cloud VM. Do **not** name the upstream
project. Do **not** guess `-D` or flags.

Prior cmake exception remains:
`docs/review_20260819/author_authorization_2026-08-19-one-archive-cmake.md`.

```text
EXECUTION_PACKET
packet_id: 2026-08-20-010
scientific_target: P2-C
correction_verdict: CLOSE_AND_ADVANCE
author_authorization: 读取被测程序的官网帮助文档或issue，不瞎猜参数取值及其意义。
baseline_commit: 4444061dde0159a5edd62753fe3cef2d881a308c
branch: cursor/p2c-local-tar-example-58d6
write_scope:
  - scripts/p3_v3/run_p2c_local_tar_example.py
  - data/p3_v3/phase2_profiling/jobs/p2c-20260820-010/
  - data/p3_v3/phase2_profiling/local-tar-example-terminal.json
  - data/p3_v3/handoff/2026-08-20-010.json
  - tests/p3_v3/test_phase2_p2c_local_tar_example.py
forbidden:
  - Authority Lock / verifier hardening / 新授权链 / 资格认证 / Boost.Math
  - 修改 src/p3_v3/、evidence.py、pilot.py、run_p2c_one_row.py、run_p2c_process_row.py、run_p2c_one_archive_spawn.py、run_p2c_local_tar_spawn.py、run_p2c_local_tar_rebuild.py、run_p2c_local_tar_resolve.py、run_p2c_local_tar_object.py、phase1_frames、protocol、pilot、preflight
  - git clone / sparse-checkout P12；34 个其他 archive；git clean -x
  - git add extracted/ archives/ _p2c_build/
  - cmake --build --target ltest
  - ENABLE_XBRAID / XBRAID_DIR / 任何未在 009 help 中出现的 --target
  - 猜测的 cmake -D；brew / apt 猜包名
  - 给示例加 --help / --version / cvode.* 等额外 token
  - 默认 cmake --build（all）
  - spawn POSIX_TIMER_TEST/ltest；改 selected_behavior_ids；P2-D；claim 升级；P12 揭盲
acceptance_criteria:
  1. scripts/p3_v3/run_p2c_local_tar_example.py 存在；create_intent/write_result；本地 tar file_sha256 == c7c3d38533c01a7366d2511497082af5f30f510d0f95db822d98441a06a1898c。源文件不得出现：--target ltest、ENABLE_XBRAID、git clone、--filter=blob:none、P12-Defect4MR、qualify_cxx_link、boost_math、p3-phase1-unexecuted、PHASE1_PROFILING_NOT_EXECUTED、shutil.which。不得循环 35 条 bridge records。
  2. tracked 干净且 HEAD=4444061d… 时独占写出 intent.json 与 result.json。可选 call_trace.json（仅实际 spawn）。同目录必须有 example-streams.json、cmake-help.stdout.txt 或 stderr、source-presence.json、example-find.json。
  3. intent 恰好 18 key：job_id=p2c-20260820-010、protocol_sha256=240d8270d41802c9d5b86f30564eadd1a86fd9ed09de2c7e947d17c1a4d78519、phase=PHASE_1、argv=["cvDiurnal_kry_bp"]（仅程序名；无额外 token）、cwd_identity=data/p3_v3/p12_intake/extracted/1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72、input_sha256 升序三条 240d8270… / 8eeccfe4… / db46368c…、seed=null、timeout_seconds=60、attempt=1、object_type=PROFILING_BEHAVIOR、object_id=c103b0c611dded134d189f8deedb54ad7a7170b1d78fb12a7851b88ce4115e4f、mr_id=not-applicable、evaluation_input_class=E_COMMON、evaluation_input_id=60c34610710b065bb3e0d649ce5a5b5badcfdf7147829445f925f7bdaab899a8、repetition_id=1、environment_id=p2c-local-tar-2026-08-20-010、job_role=PROFILING。environment_sha256 64 hex 且 ≠ 396e3df895988aafcaa276a51c6e2b6a46aef1f31017b84b2d22de4b81eb9007。selected_behavior_ids 自哈希仍为 e398d0a7764d44514d467c9170ba663457b7d38169354c4a310ffa3ffc37eca6。workload[2] 必须等于 object_id。
  4. source-presence.json：{"relative_path":"examples/cvode/serial/cvDiurnal_kry_bp.c","is_regular_file":<bool>}。example-find.json：普通文件名恰好为 cvDiurnal_kry_bp 的相对 posix 路径（排除路径分量 POSIX_TIMER_TEST、CMakeFiles、CMakeTmp、CompilerIdC、CompilerIdCXX）。
  5. 仅当本包新持久化的 cmake help 含恰好一行 `... cvDiurnal_kry_bp` 时，才允许 cmake --build <build> --target cvDiurnal_kry_bp。禁止 all。把 configure / help / 该 build 的 stdout/stderr 写入 job 目录；streams 记全文 sha256/nbytes（STREAM_LIMIT≥131072）。
  6. result 恰好 11 key。scientific_outcome=null。failure_code 不得为 PHASE1_PROFILING_NOT_EXECUTED。允许且仅允许：(a) E_ARCHIVE_FETCH_FAILED；(b) E_ARCHIVE_UNSAFE；(c) E_CMAKE_CONFIGURE；(d) E_CMAKE_BUILD（configure / help / 列出的 --target 失败）；(e) 源文件缺失或 help 无精确 target 或 kept 二进制 count≠1 → E_PROFILE_BINARY_ABSENT；(f) 对 kept 文件 spawn：PASS / E_PROFILE_TIMEOUT / E_PROFILE_NONZERO_EXIT。spawn 必须是 subprocess.run(["cvDiurnal_kry_bp"], cwd=extracted_tree, timeout=60, capture_output=True, executable=str(binary))，不得附加其他 token。空列表 trace 仍为 37517e5f…。
  7. local-tar-example-terminal.json canonical，keys：schema_version=p3-p2c-local-tar-example-terminal-v1、packet_id=2026-08-20-010、scientific_target=P2-C、neutral_snapshot_id=1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72、discovery_status=EXECUTABLE、adapter_id=CMAKE_CTEST_V1、behavior_id=c103b0c6…、process_argv=["cvDiurnal_kry_bp"]、denominator=PROFILING_ONE_ROW、formal_denominator_membership=false、claims=blocked、result_status、result_failure_code、workload_file_sha256=db46368c…、selected_behavior_ids_sha256=e398d0a7…、artifact_sha256 自哈希。
  8. git diff --name-only 4444061d HEAD 全部落在 write_scope；不得 git add extracted/ archives/ _p2c_build/；不得改 006–009 脚本或 src/p3_v3。
  9. PYTHONPATH=src python3 -m pytest tests/p3_v3/test_phase2_p2c_local_tar_example.py -q 退出 0；pytest 不调用 cmake。
  10. handoff/2026-08-20-010.json 含 packet_id、baseline_commit、head_commit、commands[]、input_sha256、output_sha256、failures_exclusions_retries、unresolved、closed_scientific_target（一句：P2-C 冻结 EXAMPLE 仅按已列出 target 与官网 main(void) 空额外 argv 尝试；非 ltest；非 20 行；非 P2-D）。
out_of_list_policy: backlog_only
repair_cap: 0
handoff_path: data/p3_v3/handoff/2026-08-20-010.json
review_report_path: docs/review_20260819/2026-08-20-010_review.md
```

## Notes for executor

Desktop only. New script. Start from `4444061d`. Keep the gitignored
tar. Do not `git clean -x`. Do not reuse 009 as HEAD.

1. Re-hash the local tar; must be `c7c3d38533…`. Else stop.
2. Branch `cursor/p2c-local-tar-example-58d6` from `4444061d`.
3. Extract; reject symlinks.
4. Confirm
   `extracted/examples/cvode/serial/cvDiurnal_kry_bp.c`
   is a regular file. Write `source-presence.json`.
5. `cmake -S extracted -B extracted/_p2c_build` (no extra `-D`).
   Then `cmake --build … --target help`. If help lacks exact
   `cvDiurnal_kry_bp`, book `E_PROFILE_BINARY_ABSENT` (do not invent
   another target).
6. Only then:

```bash
cmake --build extracted/_p2c_build --target cvDiurnal_kry_bp
```

7. Find kept regular files named `cvDiurnal_kry_bp` (exclusion list
   in criterion 4). If `count==1`, spawn with **only** argv
   `["cvDiurnal_kry_bp"]` and `executable=` that path. Official
   `main(void)` documents no further tokens. Timeout 60s may
   honestly yield `E_PROFILE_TIMEOUT`.
8. `environment_sha256` = canonical_sha256 of
   `{"dependency_lock_sha256":"7706b4ce272d09df13c5212b04ec0f2519932f4225d5eac0d052d3225c7ff35f","domain":"P3-P2C-LOCAL-TAR-EXAMPLE-ENV-v1","platform":<platform.system()>,"python":<platform.python_version()>}`.
9. Launch:

```bash
PYTHONPATH=src python3 scripts/p3_v3/run_p2c_local_tar_example.py \
  --root . \
  --workload data/p3_v3/phase1_frames/out/profiling-workload-1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.json \
  --behavior-id c103b0c611dded134d189f8deedb54ad7a7170b1d78fb12a7851b88ce4115e4f \
  --jobs-root data/p3_v3/phase2_profiling/jobs \
  --job-id p2c-20260820-010 \
  --terminal-output data/p3_v3/phase2_profiling/local-tar-example-terminal.json
```

10. Packet pytest; evidence commit; handoff child:

```text
p3-v3(2026-08-20-010): P2-C local-tar listed EXAMPLE target

Evidence: create_intent/write_result; status <STATUS> <code>
Target: P2-C
```

11. Push `-u origin cursor/p2c-local-tar-example-58d6`. Stop. No P2-D.
    Do not merge 006–010.
