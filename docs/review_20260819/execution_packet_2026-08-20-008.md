# Execution packet 2026-08-20-008 — list cmake/CTest names, then spawn if `ltest` exists

Issued after C1 `PASS_WITH_DISCLOSURE` / `CLOSE_AND_ADVANCE` on
packet 007 (`docs/review_20260819/2026-08-20-007_review.md`).
007 evidence `f21837d0` persisted cmake streams. Build stderr SHA-256
`fb644e2ee7393638777c82438d0a602c87ac671b746d0e6ecc2f9139f65e24c0` is
exactly `make: *** No rule to make target \`ltest'.  Stop.`
Configure had zero `Could NOT find` lines.

This packet is a **new attempt** (`p2c-20260820-008`): same local tar,
configure if needed, **list** cmake targets and CTest tests, persist
those listings plus a find of regular files named `ltest`, then spawn
only if exactly one such file exists.

Do **not** run `cmake --build --target ltest`. Do **not** brew/apt.
Do **not** pass guessed `cmake -D` cache flags. Do **not** start on
an empty Cloud VM. Do **not** name the upstream project.

Prior cmake exception remains:
`docs/review_20260819/author_authorization_2026-08-19-one-archive-cmake.md`.

Pinned subject / behavior / argv unchanged from 007
(`1f67b3f3…`, `13b2cddc…`, `["ltest"]`). Do not skip to EXAMPLE.

```text
EXECUTION_PACKET
packet_id: 2026-08-20-008
scientific_target: P2-C
correction_verdict: CLOSE_AND_ADVANCE
author_authorization: 只取这一个受试 archive / 只解压；若依赖 cmake 则解禁 cmake 并放行该受试其他构建依赖；仍禁 35 包全量
baseline_commit: 4444061dde0159a5edd62753fe3cef2d881a308c
branch: cursor/p2c-local-tar-resolve-58d6
write_scope:
  - scripts/p3_v3/run_p2c_local_tar_resolve.py
  - data/p3_v3/phase2_profiling/jobs/p2c-20260820-008/
  - data/p3_v3/phase2_profiling/local-tar-resolve-terminal.json
  - data/p3_v3/handoff/2026-08-20-008.json
  - tests/p3_v3/test_phase2_p2c_local_tar_resolve.py
forbidden:
  - Authority Lock / verifier hardening / 新授权链 / 资格认证 / Boost.Math
  - 修改 src/p3_v3/、evidence.py、pilot.py、run_p2c_one_row.py、run_p2c_process_row.py、run_p2c_one_archive_spawn.py、run_p2c_local_tar_spawn.py、run_p2c_local_tar_rebuild.py、phase1_frames、protocol、pilot、preflight
  - git clone / sparse-checkout P12；34 个其他 archive；git clean -x
  - git add extracted/ archives/ _p2c_build/
  - cmake --build --target ltest
  - brew / apt / 猜包名
  - 猜测的 cmake -D cache flags
  - ctest -R / ctest -H 作为 spawn 替代（会改测量）
  - 默认 cmake --build（无 target 的全量 all）
  - shutil.which ltest；改 selected_behavior_ids；P2-D；claim 升级；P12 揭盲
acceptance_criteria:
  1. scripts/p3_v3/run_p2c_local_tar_resolve.py 存在；create_intent/write_result；本地 tar file_sha256 == c7c3d38533c01a7366d2511497082af5f30f510d0f95db822d98441a06a1898c；configure 后执行 cmake --build <build> --target help 与 ctest --test-dir <build> -N；把这两条命令的 stdout/stderr 以及 configure 流写入 jobs/p2c-20260820-008/1/；另写 ltest-find.json（普通文件名恰好为 ltest 的相对 posix 路径，已排序，含 count）。spawn 仅当 count==1，且 executable= 该文件，不得 PATH。源文件不得出现：--target ltest、git clone、--filter=blob:none、P12-Defect4MR、qualify_cxx_link、boost_math、p3-phase1-unexecuted、PHASE1_PROFILING_NOT_EXECUTED、shutil.which。不得循环 35 条 bridge records。
  2. tracked 干净且 HEAD=4444061d… 时独占写出 intent.json 与 result.json。可选 call_trace.json（仅实际 spawn）。同目录必须有 resolve-streams.json（各流 path/nbytes/sha256）以及 cmake-help.stdout.txt 或 cmake-help.stderr.txt、ctest-list.stdout.txt 或 ctest-list.stderr.txt、ltest-find.json。
  3. intent 恰好 18 key：job_id=p2c-20260820-008、protocol_sha256=240d8270d41802c9d5b86f30564eadd1a86fd9ed09de2c7e947d17c1a4d78519、phase=PHASE_1、argv=["ltest"]、cwd_identity=data/p3_v3/p12_intake/extracted/1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72、input_sha256 升序三条 240d8270… / 8eeccfe4… / db46368c…、seed=null、timeout_seconds=60、attempt=1、object_type=PROFILING_BEHAVIOR、object_id=13b2cddc5341afe2883cad777028d5c534d68c254ae0635792fb43b497e72a45、mr_id=not-applicable、evaluation_input_class=E_COMMON、evaluation_input_id=60c34610710b065bb3e0d649ce5a5b5badcfdf7147829445f925f7bdaab899a8、repetition_id=1、environment_id=p2c-local-tar-2026-08-20-008、job_role=PROFILING。environment_sha256 64 hex 且 ≠ 396e3df895988aafcaa276a51c6e2b6a46aef1f31017b84b2d22de4b81eb9007。selected_behavior_ids 自哈希仍为 e398d0a7764d44514d467c9170ba663457b7d38169354c4a310ffa3ffc37eca6。
  4. result 恰好 11 key。scientific_outcome=null。failure_code 不得为 PHASE1_PROFILING_NOT_EXECUTED 或 E_SOURCE_TREE_ABSENT。允许且仅允许：(a) E_ARCHIVE_FETCH_FAILED；(b) E_ARCHIVE_UNSAFE；(c) E_CMAKE_CONFIGURE；(d) E_CMAKE_BUILD 仅当 configure 或 listing 命令（--target help / ctest -N）本身失败，不得再对 ltest 调 --target；(e) 清单已落盘但普通文件 ltest 的 count≠1 → E_PROFILE_BINARY_ABSENT；(f) spawn PASS / E_PROFILE_TIMEOUT / E_PROFILE_NONZERO_EXIT。空列表 trace 仍为 37517e5f…。
  5. local-tar-resolve-terminal.json canonical，keys：schema_version=p3-p2c-local-tar-resolve-terminal-v1、packet_id=2026-08-20-008、scientific_target=P2-C、neutral_snapshot_id=1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72、discovery_status=EXECUTABLE、adapter_id=CMAKE_CTEST_V1、behavior_id=13b2cddc…、process_argv=["ltest"]、denominator=PROFILING_ONE_ROW、formal_denominator_membership=false、claims=blocked、result_status、result_failure_code、workload_file_sha256=db46368c…、selected_behavior_ids_sha256=e398d0a7…、artifact_sha256 自哈希。
  6. git diff --name-only 4444061d HEAD 全部落在 write_scope；不得 git add extracted/ archives/ _p2c_build/；不得出现 src/p3_v3、evidence.py、006/007 脚本改动。
  7. PYTHONPATH=src python3 -m pytest tests/p3_v3/test_phase2_p2c_local_tar_resolve.py -q 退出 0；pytest 不调用 cmake 或 ctest。
  8. handoff/2026-08-20-008.json 含 packet_id、baseline_commit、head_commit、commands[]、input_sha256、output_sha256、failures_exclusions_retries、unresolved、closed_scientific_target（一句：P2-C 本地 tar 的 cmake/CTest 目标清单已落盘；非 --target ltest 重试；非 20 行；非 P2-D）。
out_of_list_policy: backlog_only
repair_cap: 0
handoff_path: data/p3_v3/handoff/2026-08-20-008.json
review_report_path: docs/review_20260819/2026-08-20-008_review.md
```

## Notes for executor

Desktop only. New script. Start from `4444061d`. Keep the gitignored
tar. Do not `git clean -x`. You may read 007
`run_p2c_local_tar_rebuild.py` as reference; do not edit it. Do not
reuse the 007 branch as HEAD.

1. Re-hash the local tar; must be `c7c3d38533…`. Else stop, no clone.
2. Branch `cursor/p2c-local-tar-resolve-58d6` from `4444061d`. Tracked
   tree clean when writing exclusive intent/result.
3. Extract; reject symlinks.
4. `cmake -S extracted -B extracted/_p2c_build` (no extra `-D`).
   Persist configure stdout/stderr.
5. Then **only** these listing commands (persist stdout/stderr):

```bash
cmake --build extracted/_p2c_build --target help
ctest --test-dir extracted/_p2c_build -N
```

   Write `resolve-streams.json` with `{path, nbytes, sha256}` for
   configure, help, and ctest-list streams. If a stream exceeds 64 KiB,
   write the last 64 KiB to the `.txt` and still record the full
   sha256/nbytes.
6. Walk the extracted tree (including `_p2c_build`) for **regular,
   non-symlink** files whose name is exactly `ltest`. Write
   `ltest-find.json` as canonical JSON
   `{"count": <int>, "paths": [<relative posix>, ...]}` with paths
   sorted. Do not use `shutil.which`. Do not search PATH.
7. `repair_cap` is 0. Do not brew/apt. Do not pass `-D` flags. Do not
   `cmake --build --target ltest`. Do not default-build `all`.
8. If `count==1`, spawn:

```python
subprocess.run(["ltest"], cwd=extracted_tree, timeout=60, capture_output=True, executable=str(binary))
```

   If `count!=1`, book `E_PROFILE_BINARY_ABSENT` (listings still
   required). Do not pick among multiples. Do not remap to another
   binary name.
9. `environment_sha256` = canonical_sha256 of
   `{"dependency_lock_sha256":"7706b4ce272d09df13c5212b04ec0f2519932f4225d5eac0d052d3225c7ff35f","domain":"P3-P2C-LOCAL-TAR-RESOLVE-ENV-v1","platform":<platform.system()>,"python":<platform.python_version()>}`.
10. Launch:

```bash
PYTHONPATH=src python3 scripts/p3_v3/run_p2c_local_tar_resolve.py \
  --root . \
  --workload data/p3_v3/phase1_frames/out/profiling-workload-1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.json \
  --behavior-id 13b2cddc5341afe2883cad777028d5c534d68c254ae0635792fb43b497e72a45 \
  --jobs-root data/p3_v3/phase2_profiling/jobs \
  --job-id p2c-20260820-008 \
  --terminal-output data/p3_v3/phase2_profiling/local-tar-resolve-terminal.json
```

11. Packet pytest; evidence commit; handoff child:

```text
p3-v3(2026-08-20-008): P2-C local-tar cmake/CTest target list

Evidence: create_intent/write_result; status <STATUS> <code>
Target: P2-C
```

12. Push `-u origin cursor/p2c-local-tar-resolve-58d6`. Stop. No P2-D.
    Do not merge 006/007/008.
