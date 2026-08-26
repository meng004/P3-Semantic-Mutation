# Execution packet 2026-08-20-007 — persist cmake ltest logs, then spawn

Issued after the Desktop WAIT reported
`CMAKE_LTEST_LOG_EXCERPT=absent`. Record:
`docs/review_20260819/author_wait_2026-08-20-cmake-log-absent.md`.
006 booked `E_CMAKE_BUILD` but dropped `--build` stdout/stderr. This
packet is a **new attempt** (`p2c-20260820-007`): same local tar, write
configure/build streams to the job dir, then cmake `--target ltest` and
spawn if the binary exists.

Do **not** reuse the 006 worktree as a dirty HEAD. Do **not** start on
an empty Cloud VM. Do **not** invent package names before the new logs
exist. `repair_cap` 2 may install only names that appear in the
**captured** logs (same “Could NOT find …” / missing-package lines).

Prior cmake exception remains:
`docs/review_20260819/author_authorization_2026-08-19-one-archive-cmake.md`.

Pinned subject / behavior / argv unchanged from 006
(`1f67b3f3…`, `13b2cddc…`, `["ltest"]`). Do not skip to EXAMPLE.

```text
EXECUTION_PACKET
packet_id: 2026-08-20-007
scientific_target: P2-C
correction_verdict: CLOSE_AND_ADVANCE
author_authorization: 只取这一个受试 archive / 只解压；若依赖 cmake 则解禁 cmake 并放行该受试其他构建依赖；仍禁 35 包全量
baseline_commit: 4444061dde0159a5edd62753fe3cef2d881a308c
branch: cursor/p2c-local-tar-rebuild-58d6
write_scope:
  - scripts/p3_v3/run_p2c_local_tar_rebuild.py
  - data/p3_v3/phase2_profiling/jobs/p2c-20260820-007/
  - data/p3_v3/phase2_profiling/local-tar-rebuild-terminal.json
  - data/p3_v3/handoff/2026-08-20-007.json
  - tests/p3_v3/test_phase2_p2c_local_tar_rebuild.py
forbidden:
  - Authority Lock / verifier hardening / 新授权链 / 资格认证 / Boost.Math
  - 修改 src/p3_v3/、evidence.py、pilot.py、run_p2c_one_row.py、run_p2c_process_row.py、run_p2c_one_archive_spawn.py、run_p2c_local_tar_spawn.py、phase1_frames、protocol、pilot、preflight
  - git clone / sparse-checkout P12；34 个其他 archive；git clean -x
  - git add extracted/ archives/ _p2c_build/
  - 在日志落盘前 brew/apt 猜包名
  - shutil.which ltest；改 selected_behavior_ids；P2-D；claim 升级；P12 揭盲
acceptance_criteria:
  1. scripts/p3_v3/run_p2c_local_tar_rebuild.py 存在；create_intent/write_result；本地 tar file_sha256 == c7c3d38533c01a7366d2511497082af5f30f510d0f95db822d98441a06a1898c；把 cmake configure 与 cmake --build --target ltest 的 stdout/stderr 写入 jobs/p2c-20260820-007/1/（全文或前 64KiB + 全文 sha256/nbytes）；含 spawn executable= 且不得 PATH。源文件不得出现 git clone、--filter=blob:none、P12-Defect4MR、qualify_cxx_link、boost_math、p3-phase1-unexecuted、PHASE1_PROFILING_NOT_EXECUTED。不得循环 35 条 bridge records。
  2. tracked 干净且 HEAD=4444061d… 时独占写出 intent.json 与 result.json。可选 call_trace.json（仅实际 spawn）。同目录必须有 cmake 流文件（至少 build stdout 或 stderr 之一，nbytes≥0）。
  3. intent 恰好 18 key：job_id=p2c-20260820-007、protocol_sha256=240d8270d41802c9d5b86f30564eadd1a86fd9ed09de2c7e947d17c1a4d78519、phase=PHASE_1、argv=["ltest"]、cwd_identity=data/p3_v3/p12_intake/extracted/1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72、input_sha256 升序三条 240d8270… / 8eeccfe4… / db46368c…、seed=null、timeout_seconds=60、attempt=1、object_type=PROFILING_BEHAVIOR、object_id=13b2cddc5341afe2883cad777028d5c534d68c254ae0635792fb43b497e72a45、mr_id=not-applicable、evaluation_input_class=E_COMMON、evaluation_input_id=60c34610710b065bb3e0d649ce5a5b5badcfdf7147829445f925f7bdaab899a8、repetition_id=1、environment_id=p2c-local-tar-2026-08-20-007、job_role=PROFILING。environment_sha256 64 hex 且 ≠ 396e3df895988aafcaa276a51c6e2b6a46aef1f31017b84b2d22de4b81eb9007。selected_behavior_ids 自哈希仍为 e398d0a7764d44514d467c9170ba663457b7d38169354c4a310ffa3ffc37eca6。
  4. result 恰好 11 key。scientific_outcome=null。failure_code 不得为 PHASE1_PROFILING_NOT_EXECUTED 或 E_SOURCE_TREE_ABSENT。允许且仅允许与 006 相同的 (a)–(f)：E_ARCHIVE_FETCH_FAILED / E_ARCHIVE_UNSAFE / E_CMAKE_CONFIGURE / E_CMAKE_BUILD / E_PROFILE_BINARY_ABSENT / spawn PASS|E_PROFILE_TIMEOUT|E_PROFILE_NONZERO_EXIT。空列表 trace 仍为 37517e5f…。
  5. local-tar-rebuild-terminal.json canonical，keys：schema_version=p3-p2c-local-tar-rebuild-terminal-v1、packet_id=2026-08-20-007、scientific_target=P2-C、neutral_snapshot_id=1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72、discovery_status=EXECUTABLE、adapter_id=CMAKE_CTEST_V1、behavior_id=13b2cddc…、process_argv=["ltest"]、denominator=PROFILING_ONE_ROW、formal_denominator_membership=false、claims=blocked、result_status、result_failure_code、workload_file_sha256=db46368c…、selected_behavior_ids_sha256=e398d0a7…、artifact_sha256 自哈希。
  6. git diff --name-only 4444061d HEAD 全部落在 write_scope；不得 git add extracted/ archives/ _p2c_build/；不得出现 src/p3_v3、evidence.py、006 脚本。
  7. PYTHONPATH=src python3 -m pytest tests/p3_v3/test_phase2_p2c_local_tar_rebuild.py -q 退出 0；pytest 不调用 cmake。
  8. handoff/2026-08-20-007.json 含 packet_id、baseline_commit、head_commit、commands[]、input_sha256、output_sha256、failures_exclusions_retries、unresolved、closed_scientific_target（一句：P2-C 本地 tar 的 cmake ltest 日志已落盘并再尝试构建；非 20 行；非 P2-D；非 35 包）。
out_of_list_policy: backlog_only
repair_cap: 2
handoff_path: data/p3_v3/handoff/2026-08-20-007.json
review_report_path: docs/review_20260819/2026-08-20-007_review.md
```

## Notes for executor

Desktop only. New script. Start from `4444061d`. Keep the gitignored
tar. Do not `git clean -x`. You may read 006
`run_p2c_local_tar_spawn.py` as reference; do not edit it.

1. Re-hash the local tar; must be `c7c3d38533…`. Else stop, no clone.
2. Branch `cursor/p2c-local-tar-rebuild-58d6` from `4444061d`. Tracked
   tree clean when writing exclusive intent/result.
3. Extract; reject symlinks.
4. `cmake -S extracted -B extracted/_p2c_build` and
   `cmake --build … --target ltest`. Write streams under
   `data/p3_v3/phase2_profiling/jobs/p2c-20260820-007/1/` as e.g.
   `cmake-configure.stdout.txt`, `cmake-configure.stderr.txt`,
   `cmake-build.stdout.txt`, `cmake-build.stderr.txt`, plus
   `cmake-streams.json` `{path, nbytes, sha256}` for each full stream.
   If a stream exceeds 64 KiB, write the last 64 KiB to the `.txt` and
   still record the full sha256/nbytes.
5. One repair only after those files exist, and only for package names
   the captured text already contains. Do not invent names.
6. `environment_sha256` = canonical_sha256 of
   `{"dependency_lock_sha256":"7706b4ce272d09df13c5212b04ec0f2519932f4225d5eac0d052d3225c7ff35f","domain":"P3-P2C-LOCAL-TAR-REBUILD-ENV-v1","platform":<platform.system()>,"python":<platform.python_version()>}`.
7. Launch:

```bash
PYTHONPATH=src python3 scripts/p3_v3/run_p2c_local_tar_rebuild.py \
  --root . \
  --workload data/p3_v3/phase1_frames/out/profiling-workload-1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.json \
  --behavior-id 13b2cddc5341afe2883cad777028d5c534d68c254ae0635792fb43b497e72a45 \
  --jobs-root data/p3_v3/phase2_profiling/jobs \
  --job-id p2c-20260820-007 \
  --terminal-output data/p3_v3/phase2_profiling/local-tar-rebuild-terminal.json
```

8. Packet pytest; evidence commit; handoff child:

```text
p3-v3(2026-08-20-007): P2-C local-tar cmake ltest logs+retry

Evidence: create_intent/write_result; status <STATUS> <code>
Target: P2-C
```

9. Push `-u origin cursor/p2c-local-tar-rebuild-58d6`. Stop. No P2-D.
   Do not merge 006/007.
