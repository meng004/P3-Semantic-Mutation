# Execution packet 2026-08-19-005 — one-archive fetch, cmake `ltest`, spawn

Issued after the author authorized (1) one-subject archive fetch/extract
and (2) cmake plus other build dependencies **for that subject**.
Record: `docs/review_20260819/author_authorization_2026-08-19-one-archive-cmake.md`.

This is the only authorized Cursor VM input for this round. Do not reuse
a WAIT VM. Do not continue the 004 worktree.

004 already booked this row as `E_SOURCE_TREE_ABSENT` without fetch.
This packet is a **new attempt** (`p2c-20260819-005`): fetch one tar,
extract, cmake `--target ltest`, spawn `["ltest"]`. Not 20 rows, not
P2-D, not 35 archives, not Boost.Math qualification.

Pinned subject:
`1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72`.
Pinned behavior = `selected_behavior_ids[1]`:
`13b2cddc5341afe2883cad777028d5c534d68c254ae0635792fb43b497e72a45`
(argv `["ltest"]`). Do **not** skip to EXAMPLE. Do **not** re-run index 0.

Reviewer VM at issue time: no `extracted/`, no `archives/`; this token
cannot read `github.com/meng004/P12-Defect4MR` (HTTP 404).

```text
EXECUTION_PACKET
packet_id: 2026-08-19-005
scientific_target: P2-C
correction_verdict: CLOSE_AND_ADVANCE
author_authorization: 只取这一个受试 archive / 只解压；若依赖 cmake 则解禁 cmake 并放行该受试其他构建依赖；仍禁 35 包全量
baseline_commit: 4444061dde0159a5edd62753fe3cef2d881a308c
branch: cursor/p2c-one-archive-spawn-58d6
write_scope:
  - scripts/p3_v3/run_p2c_one_archive_spawn.py
  - data/p3_v3/phase2_profiling/jobs/p2c-20260819-005/
  - data/p3_v3/phase2_profiling/one-archive-terminal.json
  - data/p3_v3/handoff/2026-08-19-005.json
  - tests/p3_v3/test_phase2_p2c_one_archive.py
forbidden:
  - Authority Lock / verifier hardening
  - 新授权链 / launch-packet / 资格认证框架 / 通用 profiler 框架
  - claim 升级 / P12 揭盲 / confirmatory 分母改写
  - 修改 src/p3_v3/、scripts/p3_v3/evidence.py、scripts/p3_v3/pilot.py、scripts/p3_v3/run_p2c_one_row.py、scripts/p3_v3/run_p2c_process_row.py、data/p3_v3/protocol/、data/p3_v3/pilot/、data/p3_v3/phase1_frames/、data/p3_v3/phase2_preflight/、data/p3_v3/phase2_pilot_only/
  - 下载其余 34 个 archive / 全量 3.3GB 包 / git lfs pull 整个 package
  - qualify_cxx_link.py、Boost.Math 资格路径、其他 PUT、改 selected_behavior_ids、index 0 或第三条行为、build-frames、Package A/B/C、P2-D
  - shutil.which / 运行 PATH 上的同名 ltest（只允许本受试 extracted 或 _p2c_build 下的普通文件）
  - git add extracted/ 或 archives/ 或 _p2c_build/
acceptance_criteria:   # ≤8, 可机器核对
  1. scripts/p3_v3/run_p2c_one_archive_spawn.py 存在；`from p3_v3.run_records import create_intent, write_result`；含 `--filter=blob:none` 与 snapshot id `1f67b3f3…` 的单文件 sparse 取回；含 `cmake` 与 `--target ltest`；`subprocess.run(["ltest"], ... executable=...)` 的 executable 不得来自 PATH。源文件不得出现 token：qualify_cxx_link、boost_math、p3-phase1-unexecuted、PHASE1_PROFILING_NOT_EXECUTED。不得循环 `verified_bridge` 的 35 条 records 去拉 tar。
  2. 在 tracked 干净且 HEAD=4444061d… 时独占写出 data/p3_v3/phase2_profiling/jobs/p2c-20260819-005/1/intent.json 与同目录 result.json。可选：同目录 call_trace.json（仅当实际 spawn）。
  3. intent 恰好 18 key：job_id=p2c-20260819-005、protocol_sha256=240d8270d41802c9d5b86f30564eadd1a86fd9ed09de2c7e947d17c1a4d78519、phase=PHASE_1、argv=["ltest"]、cwd_identity=data/p3_v3/p12_intake/extracted/1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72、input_sha256 恰好升序三条 240d8270… / 8eeccfe4d1aebb09e6ee9ad2fadb82ac5b8697c40f602592faa6b3878692a440 / db46368cc3a8e78ffeceb60c38d46cd903ac49ddc779757ee94f1350bd15382d、seed=null、timeout_seconds=60、attempt=1、object_type=PROFILING_BEHAVIOR、object_id=13b2cddc5341afe2883cad777028d5c534d68c254ae0635792fb43b497e72a45、mr_id=not-applicable、evaluation_input_class=E_COMMON、evaluation_input_id=60c34610710b065bb3e0d649ce5a5b5badcfdf7147829445f925f7bdaab899a8、repetition_id=1、environment_id=p2c-one-archive-2026-08-19-005、job_role=PROFILING。environment_sha256 为 64 hex 且 ≠ 396e3df895988aafcaa276a51c6e2b6a46aef1f31017b84b2d22de4b81eb9007。冻结 selected_behavior_ids 自哈希仍为 e398d0a7764d44514d467c9170ba663457b7d38169354c4a310ffa3ffc37eca6。
  4. result 恰好 11 key。scientific_outcome=null。failure_code 不得为 PHASE1_PROFILING_NOT_EXECUTED 或 E_SOURCE_TREE_ABSENT（本包必须尝试 fetch）。允许且仅允许：
     (a) 单 tar 取回失败（404、无权限、路径不唯一、SHA≠c7c3d38533c01a7366d2511497082af5f30f510d0f95db822d98441a06a1898c）→ FAIL_INFRASTRUCTURE E_ARCHIVE_FETCH_FAILED exit_code=null 空列表 trace 37517e5f…
     (b) tar 含 symlink → FAIL_INFRASTRUCTURE E_ARCHIVE_UNSAFE 空列表 trace
     (c) cmake configure 失败 → FAIL_INFRASTRUCTURE E_CMAKE_CONFIGURE 空列表 trace
     (d) cmake --build --target ltest 失败 → FAIL_INFRASTRUCTURE E_CMAKE_BUILD 空列表 trace
     (e) 构建后仍无普通文件 ltest → FAIL_INFRASTRUCTURE E_PROFILE_BINARY_ABSENT 空列表 trace
     (f) 实际 spawn：call_trace.json 恰好一个 event {sequence:1,module:target:ltest,symbol:ltest,call_kind:PROCESS_SPAWN,argument_types:[],keyword_names:[]}；exit 0 → PASS failure_code=""；timeout → INCONCLUSIVE E_PROFILE_TIMEOUT；否则 FAIL_SCIENTIFIC E_PROFILE_NONZERO_EXIT
  5. data/p3_v3/phase2_profiling/one-archive-terminal.json 为 canonical JSON，恰好 keys：schema_version=p3-p2c-one-archive-terminal-v1、packet_id=2026-08-19-005、scientific_target=P2-C、neutral_snapshot_id=1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72、discovery_status=EXECUTABLE、adapter_id=CMAKE_CTEST_V1、behavior_id=13b2cddc5341afe2883cad777028d5c534d68c254ae0635792fb43b497e72a45、process_argv=["ltest"]、denominator=PROFILING_ONE_ROW、formal_denominator_membership=false、claims=blocked、result_status、result_failure_code、workload_file_sha256=db46368cc3a8e78ffeceb60c38d46cd903ac49ddc779757ee94f1350bd15382d、selected_behavior_ids_sha256=e398d0a7764d44514d467c9170ba663457b7d38169354c4a310ffa3ffc37eca6、artifact_sha256 自哈希
  6. git diff --name-only 4444061dde0159a5edd62753fe3cef2d881a308c HEAD 全部落在 write_scope；不得出现 src/p3_v3、evidence.py、pilot.py、qualify_cxx_link、boost_math、phase1_frames、phase2_preflight、phase2_pilot_only、run_p2c_one_row.py、run_p2c_process_row.py；不得 git add extracted/ archives/ _p2c_build/
  7. PYTHONPATH=src python3 -m pytest tests/p3_v3/test_phase2_p2c_one_archive.py -q 退出 0；只核对本包产物与冻结 Phase 1 输入；不跑全量 tests/p3_v3；pytest 本身不调用 cmake
  8. data/p3_v3/handoff/2026-08-19-005.json 含 packet_id、baseline_commit、head_commit、commands[]、input_sha256、output_sha256、failures_exclusions_retries、unresolved、closed_scientific_target（一句：P2-C 单受试 archive+ltest 构建尝试已入账；非 20 行；非 P2-D；非 35 包）
out_of_list_policy: backlog_only
repair_cap: 2
handoff_path: data/p3_v3/handoff/2026-08-19-005.json
review_report_path: docs/review_20260819/2026-08-19-005_review.md
notes_for_executor: 见下文；做完即停，不要做 P2-D。
```

## Notes for executor

One new script. Do not edit `src/p3_v3/`. Start from `4444061d`, not from
004. Do not `git add` trees. Claims stay `blocked`.

1. Pin HEAD to `4444061dde0159a5edd62753fe3cef2d881a308c`. Create
   `cursor/p2c-one-archive-spawn-58d6`. Tracked tree clean
   (`git status --porcelain=v1 --untracked-files=no` empty) when the
   script writes exclusive intent/result.
2. Confirm workload SHA-256 `db46368cc3a8e78ffeceb60c38d46cd903ac49ddc779757ee94f1350bd15382d`
   and `selected_behavior_ids[1]==13b2cddc…`. Else `unresolved`.
3. Fetch **one** archive (skip if local file already hashes to
   `c7c3d38533c01a7366d2511497082af5f30f510d0f95db822d98441a06a1898c`):

```text
git clone --filter=blob:none --no-checkout \
  https://github.com/meng004/P12-Defect4MR.git /tmp/p12-one-archive-005
git -C /tmp/p12-one-archive-005 fetch --depth 1 origin \
  d57fa8119e47baf88c5bcff2d67346864cf3672d
git -C /tmp/p12-one-archive-005 rev-parse FETCH_HEAD
# must equal d57fa8119e47baf88c5bcff2d67346864cf3672d
```

   `git ls-tree -r --name-only FETCH_HEAD` and keep paths that contain
   `1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72`
   and end in `.tar`. **Exactly one** such path. Sparse-checkout that
   path only. Copy to
   `data/p3_v3/p12_intake/archives/1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.tar`.
   `sha256sum` must be `c7c3d38533c01a7366d2511497082af5f30f510d0f95db822d98441a06a1898c`.
   If `find /tmp/p12-one-archive-005 -name '*.tar' | wc -l` is not 1
   after checkout, stop → `E_ARCHIVE_FETCH_FAILED`. Do not `git lfs pull`
   the package directory. Candidate path if ls-tree is slow to scan:
   `release/p3-bridge-v1-package/archives/<neutral>.tar`.
4. Extract with `tarfile`; reject any symlink member → `E_ARCHIVE_UNSAFE`.
   Destination:
   `data/p3_v3/p12_intake/extracted/1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72/`.
5. Configure and build **only** target `ltest` (repair_cap 2 includes one
   apt/dep retry named by the configure error):

```bash
cmake -S data/p3_v3/p12_intake/extracted/1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72 \
      -B data/p3_v3/p12_intake/extracted/1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72/_p2c_build
cmake --build data/p3_v3/p12_intake/extracted/1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72/_p2c_build \
      --target ltest
```

   Allowed deps: cmake, ninja or make, `cc`/`c++`/`gfortran`, and
   libraries this `CMakeLists.txt` / configure error names. Do not
   install Boost.Math qualification tooling. Do not build other P12
   subjects. cmake/configure may take a long time; spawn timeout stays 60s.
6. Locate a non-symlink regular file named `ltest` under the extracted
   tree or `_p2c_build`. Spawn:

```python
subprocess.run(["ltest"], cwd=extracted_tree, timeout=60, capture_output=True, executable=str(binary))
```

7. `environment_sha256` = `canonical_sha256` of
   `{"dependency_lock_sha256":"7706b4ce272d09df13c5212b04ec0f2519932f4225d5eac0d052d3225c7ff35f","domain":"P3-P2C-ONE-ARCHIVE-ENV-v1","platform":<platform.system()>,"python":<platform.python_version()>}`.
8. Launch:

```bash
PYTHONPATH=src python3 scripts/p3_v3/run_p2c_one_archive_spawn.py \
  --root . \
  --workload data/p3_v3/phase1_frames/out/profiling-workload-1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.json \
  --behavior-id 13b2cddc5341afe2883cad777028d5c534d68c254ae0635792fb43b497e72a45 \
  --jobs-root data/p3_v3/phase2_profiling/jobs \
  --job-id p2c-20260819-005 \
  --terminal-output data/p3_v3/phase2_profiling/one-archive-terminal.json
```

9. Packet pytest checks criteria 1–5. Handoff, evidence commit, then
   handoff child if needed:

```text
p3-v3(2026-08-19-005): P2-C one-archive ltest cmake/spawn

Evidence: create_intent/write_result; status <STATUS> <code>
Target: P2-C
```

10. Push and stop. Do not start P2-D or another row.

This environment has no `rtk`. Use `python3`, `pytest`, `sha256sum`, `git`,
`cmake` as needed. `PYTHONPATH=src` when importing `p3_v3`.
