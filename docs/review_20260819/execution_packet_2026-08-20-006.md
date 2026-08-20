# Execution packet 2026-08-20-006 — local tar, cmake `ltest`, spawn

Issued after the author attested
`sha256sum` `c7c3d38533c01a7366d2511497082af5f30f510d0f95db822d98441a06a1898c`
for the pinned archive on the Mac checkout
`/Users/limeng/Papers/P3-SemanticMutation`. Record:
`docs/review_20260819/author_sha256_2026-08-20-one-archive.md`.
Prior cmake exception remains:
`docs/review_20260819/author_authorization_2026-08-19-one-archive-cmake.md`.

This is the only authorized Cursor VM input for this round. Do **not**
reuse a WAIT VM or the 005 worktree. Do **not** start this packet on an
empty Cloud VM (no `/Users/limeng` mount). Use the Desktop / local
checkout that already has the tar.

005 already booked sparse-clone `E_ARCHIVE_FETCH_FAILED`. This packet
is a **new attempt** (`p2c-20260820-006`): **local tar only**, then
extract, cmake `--target ltest`, spawn `["ltest"]`. No P12 clone.

Pinned subject:
`1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72`.
Pinned behavior = `selected_behavior_ids[1]`:
`13b2cddc5341afe2883cad777028d5c534d68c254ae0635792fb43b497e72a45`
(argv `["ltest"]`). Do **not** skip to EXAMPLE. Do **not** re-run index 0.

Reviewer VM at issue time: still `TAR_ABSENT`. Author paste matches the
bridge hash; this packet's first gate is an executor re-hash.

```text
EXECUTION_PACKET
packet_id: 2026-08-20-006
scientific_target: P2-C
correction_verdict: CLOSE_AND_ADVANCE
author_authorization: 只取这一个受试 archive / 只解压；若依赖 cmake 则解禁 cmake 并放行该受试其他构建依赖；仍禁 35 包全量
baseline_commit: 4444061dde0159a5edd62753fe3cef2d881a308c
branch: cursor/p2c-local-tar-cmake-58d6
write_scope:
  - scripts/p3_v3/run_p2c_local_tar_spawn.py
  - data/p3_v3/phase2_profiling/jobs/p2c-20260820-006/
  - data/p3_v3/phase2_profiling/local-tar-terminal.json
  - data/p3_v3/handoff/2026-08-20-006.json
  - tests/p3_v3/test_phase2_p2c_local_tar.py
forbidden:
  - Authority Lock / verifier hardening
  - 新授权链 / launch-packet / 资格认证框架 / 通用 profiler 框架
  - claim 升级 / P12 揭盲 / confirmatory 分母改写
  - 修改 src/p3_v3/、scripts/p3_v3/evidence.py、scripts/p3_v3/pilot.py、scripts/p3_v3/run_p2c_one_row.py、scripts/p3_v3/run_p2c_process_row.py、scripts/p3_v3/run_p2c_one_archive_spawn.py、data/p3_v3/protocol/、data/p3_v3/pilot/、data/p3_v3/phase1_frames/、data/p3_v3/phase2_preflight/、data/p3_v3/phase2_pilot_only/
  - git clone / sparse-checkout / ls-remote of P12-Defect4MR
  - 下载其余 34 个 archive / 全量 3.3GB 包 / git lfs pull
  - git clean -x / git clean -fdx（会删掉 gitignored tar）
  - qualify_cxx_link.py、Boost.Math 资格路径、其他 PUT、改 selected_behavior_ids、index 0 或第三条行为、build-frames、Package A/B/C、P2-D
  - shutil.which / 运行 PATH 上的同名 ltest
  - git add extracted/ 或 archives/ 或 _p2c_build/
acceptance_criteria:
  1. scripts/p3_v3/run_p2c_local_tar_spawn.py 存在；`from p3_v3.run_records import create_intent, write_result`；用 file_sha256 核对本机 archives/1f67b3f3….tar == c7c3d38533c01a7366d2511497082af5f30f510d0f95db822d98441a06a1898c；含 cmake 与 --target ltest；subprocess.run(["ltest"], executable=...) 的 executable 不得来自 PATH。源文件不得出现 token：git clone、--filter=blob:none、P12-Defect4MR、qualify_cxx_link、boost_math、p3-phase1-unexecuted、PHASE1_PROFILING_NOT_EXECUTED。不得循环 verified_bridge 的 35 条 records。
  2. 在 tracked 干净且 HEAD=4444061d… 时独占写出 data/p3_v3/phase2_profiling/jobs/p2c-20260820-006/1/intent.json 与同目录 result.json。可选：同目录 call_trace.json（仅当实际 spawn）。
  3. intent 恰好 18 key：job_id=p2c-20260820-006、protocol_sha256=240d8270d41802c9d5b86f30564eadd1a86fd9ed09de2c7e947d17c1a4d78519、phase=PHASE_1、argv=["ltest"]、cwd_identity=data/p3_v3/p12_intake/extracted/1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72、input_sha256 恰好升序三条 240d8270… / 8eeccfe4d1aebb09e6ee9ad2fadb82ac5b8697c40f602592faa6b3878692a440 / db46368cc3a8e78ffeceb60c38d46cd903ac49ddc779757ee94f1350bd15382d、seed=null、timeout_seconds=60、attempt=1、object_type=PROFILING_BEHAVIOR、object_id=13b2cddc5341afe2883cad777028d5c534d68c254ae0635792fb43b497e72a45、mr_id=not-applicable、evaluation_input_class=E_COMMON、evaluation_input_id=60c34610710b065bb3e0d649ce5a5b5badcfdf7147829445f925f7bdaab899a8、repetition_id=1、environment_id=p2c-local-tar-2026-08-20-006、job_role=PROFILING。environment_sha256 为 64 hex 且 ≠ 396e3df895988aafcaa276a51c6e2b6a46aef1f31017b84b2d22de4b81eb9007。冻结 selected_behavior_ids 自哈希仍为 e398d0a7764d44514d467c9170ba663457b7d38169354c4a310ffa3ffc37eca6。
  4. result 恰好 11 key。scientific_outcome=null。failure_code 不得为 PHASE1_PROFILING_NOT_EXECUTED 或 E_SOURCE_TREE_ABSENT。允许且仅允许：
     (a) 本地 tar 缺失或 SHA≠c7c3d38533c01a7366d2511497082af5f30f510d0f95db822d98441a06a1898c → FAIL_INFRASTRUCTURE E_ARCHIVE_FETCH_FAILED exit_code=null 空列表 trace 37517e5f…（不得因此去 clone P12）
     (b) tar 含 symlink → FAIL_INFRASTRUCTURE E_ARCHIVE_UNSAFE 空列表 trace
     (c) cmake configure 失败 → FAIL_INFRASTRUCTURE E_CMAKE_CONFIGURE 空列表 trace
     (d) cmake --build --target ltest 失败 → FAIL_INFRASTRUCTURE E_CMAKE_BUILD 空列表 trace
     (e) 构建后仍无普通文件 ltest → FAIL_INFRASTRUCTURE E_PROFILE_BINARY_ABSENT 空列表 trace
     (f) 实际 spawn：call_trace.json 恰好一个 event {sequence:1,module:target:ltest,symbol:ltest,call_kind:PROCESS_SPAWN,argument_types:[],keyword_names:[]}；exit 0 → PASS failure_code=""；timeout → INCONCLUSIVE E_PROFILE_TIMEOUT；否则 FAIL_SCIENTIFIC E_PROFILE_NONZERO_EXIT
  5. data/p3_v3/phase2_profiling/local-tar-terminal.json 为 canonical JSON，恰好 keys：schema_version=p3-p2c-local-tar-terminal-v1、packet_id=2026-08-20-006、scientific_target=P2-C、neutral_snapshot_id=1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72、discovery_status=EXECUTABLE、adapter_id=CMAKE_CTEST_V1、behavior_id=13b2cddc5341afe2883cad777028d5c534d68c254ae0635792fb43b497e72a45、process_argv=["ltest"]、denominator=PROFILING_ONE_ROW、formal_denominator_membership=false、claims=blocked、result_status、result_failure_code、workload_file_sha256=db46368cc3a8e78ffeceb60c38d46cd903ac49ddc779757ee94f1350bd15382d、selected_behavior_ids_sha256=e398d0a7764d44514d467c9170ba663457b7d38169354c4a310ffa3ffc37eca6、artifact_sha256 自哈希
  6. git diff --name-only 4444061dde0159a5edd62753fe3cef2d881a308c HEAD 全部落在 write_scope；不得出现 src/p3_v3、evidence.py、pilot.py、qualify_cxx_link、boost_math、phase1_frames、phase2_preflight、phase2_pilot_only、run_p2c_one_row.py、run_p2c_process_row.py、run_p2c_one_archive_spawn.py；不得 git add extracted/ archives/ _p2c_build/
  7. PYTHONPATH=src python3 -m pytest tests/p3_v3/test_phase2_p2c_local_tar.py -q 退出 0；只核对本包产物与冻结 Phase 1 输入；不跑全量 tests/p3_v3；pytest 本身不调用 cmake
  8. data/p3_v3/handoff/2026-08-20-006.json 含 packet_id、baseline_commit、head_commit、commands[]、input_sha256、output_sha256、failures_exclusions_retries、unresolved、closed_scientific_target（一句：P2-C 本地单受试 tar+ltest 构建尝试已入账；非 20 行；非 P2-D；非 35 包；非 P12 clone）
out_of_list_policy: backlog_only
repair_cap: 2
handoff_path: data/p3_v3/handoff/2026-08-20-006.json
review_report_path: docs/review_20260819/2026-08-20-006_review.md
notes_for_executor: 见下文；做完即停，不要做 P2-D。
```

## Notes for executor

New script. Do not edit `src/p3_v3/`. Start from `4444061d`, not from
005. You may **read** `origin/cursor/p2c-one-archive-spawn-58d6`
`run_p2c_one_archive_spawn.py` as a reference and drop every clone
path. Do not `git add` trees. Claims stay `blocked`. Do not
`git clean -x`.

1. Confirm the local file exists and hashes **before** branching:

```bash
sha256sum data/p3_v3/p12_intake/archives/1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.tar
# must be c7c3d38533c01a7366d2511497082af5f30f510d0f95db822d98441a06a1898c
```

   If this fails, write nothing, report `TAR_HASH_FAIL` or `TAR_ABSENT`,
   stop. Do not clone P12.
2. Pin HEAD to `4444061dde0159a5edd62753fe3cef2d881a308c` without
   deleting ignored files. Create `cursor/p2c-local-tar-cmake-58d6`.
   Tracked tree clean
   (`git status --porcelain=v1 --untracked-files=no` empty) when the
   script writes exclusive intent/result. Re-check the tar hash after
   checkout.
3. Confirm workload SHA-256 `db46368cc3a8e78ffeceb60c38d46cd903ac49ddc779757ee94f1350bd15382d`
   and `selected_behavior_ids[1]==13b2cddc…`. Else `unresolved`.
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
   `{"dependency_lock_sha256":"7706b4ce272d09df13c5212b04ec0f2519932f4225d5eac0d052d3225c7ff35f","domain":"P3-P2C-LOCAL-TAR-ENV-v1","platform":<platform.system()>,"python":<platform.python_version()>}`.
8. Launch:

```bash
PYTHONPATH=src python3 scripts/p3_v3/run_p2c_local_tar_spawn.py \
  --root . \
  --workload data/p3_v3/phase1_frames/out/profiling-workload-1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.json \
  --behavior-id 13b2cddc5341afe2883cad777028d5c534d68c254ae0635792fb43b497e72a45 \
  --jobs-root data/p3_v3/phase2_profiling/jobs \
  --job-id p2c-20260820-006 \
  --terminal-output data/p3_v3/phase2_profiling/local-tar-terminal.json
```

9. Packet pytest checks criteria 1–5. Handoff, evidence commit, then
   handoff child if needed:

```text
p3-v3(2026-08-20-006): P2-C local-tar ltest cmake/spawn

Evidence: create_intent/write_result; status <STATUS> <code>
Target: P2-C
```

10. Ordinary push `-u origin cursor/p2c-local-tar-cmake-58d6`. Stop.
    Do not start P2-D or another row. Do not merge #22–#25 or 005.

This environment has no `rtk`. Use `python3`, `pytest`, `sha256sum`, `git`,
`cmake` as needed. `PYTHONPATH=src` when importing `p3_v3`.
