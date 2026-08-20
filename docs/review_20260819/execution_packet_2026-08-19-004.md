# Execution packet 2026-08-19-004 — P2-C one process-argv row

Issued after the author sent the unblocking string
`P2C_TREE_AND_PROCESS_ARGV_SEAM_READY=yes` to the 评审模型
(recorded in `docs/review_20260819/author_decision_2026-08-19-A.md`).

This is the only authorized Cursor VM input for this round.

Independent check on the reviewer VM at issue time: `data/p3_v3/p12_intake/extracted/`
and `archives/` are still absent. The string licenses a **future executor**
to use a tree if that VM has it. It does **not** license downloading P12,
cmake, or rewriting `selected_behavior_ids`.

P2-C 单行 header 缺失已入账。本包关闭的是 **P2-C 的下一条最小切片**：
对冻结选择集里 **第一条带 process argv 的已选行为** 留下一对
`create_intent` / `write_result`，并在树存在时 **实际 subprocess** 该 argv。
不是 20 行全跑，不是 P2-D，不是改选，不是编译。

Pinned subject (unchanged):
`1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72`.
Pinned behavior = `selected_behavior_ids[1]` (first process-capable;
index 0 remains the PUBLIC_API header already booked in 003):
`13b2cddc5341afe2883cad777028d5c534d68c254ae0635792fb43b497e72a45`
(`CLI` / `target:ltest` → argv `["ltest"]`). Do **not** skip to EXAMPLE.
Do **not** re-run index 0.

```text
EXECUTION_PACKET
packet_id: 2026-08-19-004
scientific_target: P2-C
correction_verdict: CLOSE_AND_ADVANCE
author_authorization: P2C_TREE_AND_PROCESS_ARGV_SEAM_READY=yes
baseline_commit: 4444061dde0159a5edd62753fe3cef2d881a308c
branch: cursor/p2c-process-row-profiling-58d6
write_scope:
  - scripts/p3_v3/run_p2c_process_row.py
  - data/p3_v3/phase2_profiling/jobs/p2c-20260819-004/
  - data/p3_v3/phase2_profiling/process-row-terminal.json
  - data/p3_v3/handoff/2026-08-19-004.json
  - tests/p3_v3/test_phase2_p2c_process_row.py
forbidden:
  - Authority Lock / verifier hardening
  - 新授权链 / launch-packet / 资格认证框架 / 通用 profiler 框架
  - claim 升级 / P12 揭盲 / confirmatory 分母改写
  - 修改 src/p3_v3/、scripts/p3_v3/evidence.py、scripts/p3_v3/pilot.py、scripts/p3_v3/run_p2c_one_row.py、data/p3_v3/protocol/、data/p3_v3/pilot/、data/p3_v3/phase1_frames/、data/p3_v3/phase2_preflight/、data/p3_v3/phase2_pilot_only/
  - 调用 c++、cmake、meson、autotools、qualify_cxx_link.py、pilot.py、Boost.Math 路径
  - 下载 P12 包 / 改 selected_behavior_ids / 跑 index 0 或第三条行为 / build-frames / Package A/B/C / P2-D
  - shutil.which / 运行宿主编译器树上的同名二进制（只允许 extracted 树内的 ltest 文件）
acceptance_criteria:   # ≤8, 可机器核对
  1. scripts/p3_v3/run_p2c_process_row.py 存在；`from p3_v3.run_records import create_intent, write_result`；先 create_intent 再（若树在且 tree/ltest 为普通文件）subprocess.run(["ltest"], cwd=extracted_tree, timeout=60, capture_output=True)；脚本源不得出现 token：c++、cmake、meson、autotools、qualify_cxx_link、boost_math、p3-phase1-unexecuted、PHASE1_PROFILING_NOT_EXECUTED
  2. 在 tracked 干净且 HEAD=4444061d… 时独占写出 data/p3_v3/phase2_profiling/jobs/p2c-20260819-004/1/intent.json 与同目录 result.json。可选：同目录 call_trace.json（仅当实际 spawn 时独占写出）。
  3. intent 恰好 18 key：job_id=p2c-20260819-004、protocol_sha256=240d8270d41802c9d5b86f30564eadd1a86fd9ed09de2c7e947d17c1a4d78519、phase=PHASE_1、argv=["ltest"]、cwd_identity=data/p3_v3/p12_intake/extracted/1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72、input_sha256 恰好升序三条 240d8270… / 8eeccfe4d1aebb09e6ee9ad2fadb82ac5b8697c40f602592faa6b3878692a440 / db46368cc3a8e78ffeceb60c38d46cd903ac49ddc779757ee94f1350bd15382d、seed=null、timeout_seconds=60、attempt=1、object_type=PROFILING_BEHAVIOR、object_id=13b2cddc5341afe2883cad777028d5c534d68c254ae0635792fb43b497e72a45、mr_id=not-applicable、evaluation_input_class=E_COMMON、evaluation_input_id=60c34610710b065bb3e0d649ce5a5b5badcfdf7147829445f925f7bdaab899a8、repetition_id=1、environment_id=p2c-process-row-2026-08-19-004、job_role=PROFILING。environment_sha256 为 64 hex 且 ≠ 396e3df895988aafcaa276a51c6e2b6a46aef1f31017b84b2d22de4b81eb9007。argv 不得含 p3-phase1-unexecuted。冻结 workload 的 selected_behavior_ids[1] 必须等于 object_id；selected_behavior_ids 自哈希仍为 e398d0a7764d44514d467c9170ba663457b7d38169354c4a310ffa3ffc37eca6。
  4. result 恰好 11 key。scientific_outcome=null。failure_code 不得为 PHASE1_PROFILING_NOT_EXECUTED。允许且仅允许：
     (a) 无树且无哈希匹配本地 archive → status=MISSING_WITH_REASON failure_code=E_SOURCE_TREE_ABSENT exit_code=null call_trace_sha256=37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570（空列表）
     (b) 树在但 extracted/.../ltest 不是普通文件 → FAIL_INFRASTRUCTURE E_PROFILE_BINARY_ABSENT exit_code=null 空列表 trace
     (c) 实际 spawn：call_trace.json 为恰好一个 event {sequence:1,module:target:ltest,symbol:ltest,call_kind:PROCESS_SPAWN,argument_types:[],keyword_names:[]}；call_trace_sha256=canonical_sha256(该列表)；若 exit_code=0 则 status=PASS failure_code=""；若 timeout 则 INCONCLUSIVE E_PROFILE_TIMEOUT；否则 FAIL_SCIENTIFIC E_PROFILE_NONZERO_EXIT。call_trace_identity=canonical_sha256({job_id,attempt:1,behavior_id:object_id,call_trace_sha256,domain:P3-PROFILING-TRACE-v1})
  5. data/p3_v3/phase2_profiling/process-row-terminal.json 为 canonical JSON，恰好 keys：schema_version=p3-p2c-process-row-terminal-v1、packet_id=2026-08-19-004、scientific_target=P2-C、neutral_snapshot_id=1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72、discovery_status=EXECUTABLE、adapter_id=CMAKE_CTEST_V1、behavior_id=13b2cddc5341afe2883cad777028d5c534d68c254ae0635792fb43b497e72a45、process_argv=["ltest"]、denominator=PROFILING_ONE_ROW、formal_denominator_membership=false、claims=blocked、result_status、result_failure_code、workload_file_sha256=db46368cc3a8e78ffeceb60c38d46cd903ac49ddc779757ee94f1350bd15382d、selected_behavior_ids_sha256=e398d0a7764d44514d467c9170ba663457b7d38169354c4a310ffa3ffc37eca6、artifact_sha256 自哈希
  6. git diff --name-only 4444061dde0159a5edd62753fe3cef2d881a308c HEAD 全部落在 write_scope；不得出现 src/p3_v3、evidence.py、pilot.py、qualify_cxx_link、boost_math、phase1_frames、phase2_preflight、phase2_pilot_only；不得 git add extracted/ 或 archives/
  7. PYTHONPATH=src python3 -m pytest tests/p3_v3/test_phase2_p2c_process_row.py -q 退出 0；只核对本包产物与冻结 Phase 1 输入；不跑全量 tests/p3_v3；不调用编译器
  8. data/p3_v3/handoff/2026-08-19-004.json 含 packet_id、baseline_commit、head_commit、commands[]、input_sha256、output_sha256、failures_exclusions_retries、unresolved、closed_scientific_target（一句：P2-C 冻结选择集第 1 条 process-argv 行已入账；非 Phase 2 全关；非 20 行；非 P2-D）
out_of_list_policy: backlog_only
repair_cap: 2
handoff_path: data/p3_v3/handoff/2026-08-19-004.json
review_report_path: docs/review_20260819/2026-08-19-004_review.md
notes_for_executor: 见下文；做完即停，不要做 P2-D。
```

## Notes for executor

Reuse `create_intent` / `write_result`. One new script only. Do not edit
`src/p3_v3/`. Do not edit `run_p2c_one_row.py`. Start from `4444061d`, not
from the 003 branch.

1. Pin HEAD to `4444061dde0159a5edd62753fe3cef2d881a308c`. Create
   `cursor/p2c-process-row-profiling-58d6`. Tracked tree clean when the
   script writes exclusive intent/result.
2. Confirm workload file SHA-256 `db46368c…` and
   `selected_behavior_ids[1]==13b2cddc…`. If not, stop → `unresolved`.
3. Tree lookup (do not download):
   `data/p3_v3/p12_intake/extracted/1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72/`.
   Optional local archive extract if
   `data/p3_v3/p12_intake/archives/1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.tar`
   SHA-256 equals `c7c3d38533c01a7366d2511497082af5f30f510d0f95db822d98441a06a1898c`.
   Do not `git add` extracted files.
4. Process binary: only that directory's regular file named `ltest`.
   Do not search PATH. Do not cmake.
5. `environment_sha256` = `canonical_sha256` of
   `{"dependency_lock_sha256":"7706b4ce272d09df13c5212b04ec0f2519932f4225d5eac0d052d3225c7ff35f","domain":"P3-P2C-PROCESS-ROW-ENV-v1","platform":<platform.system()>,"python":<platform.python_version()>}`.
6. Launch (env `PYTHONPATH=src` is not part of intent.argv):

```bash
PYTHONPATH=src python3 scripts/p3_v3/run_p2c_process_row.py \
  --root . \
  --workload data/p3_v3/phase1_frames/out/profiling-workload-1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.json \
  --behavior-id 13b2cddc5341afe2883cad777028d5c534d68c254ae0635792fb43b497e72a45 \
  --jobs-root data/p3_v3/phase2_profiling/jobs \
  --job-id p2c-20260819-004 \
  --terminal-output data/p3_v3/phase2_profiling/process-row-terminal.json
```

7. Packet test checks criteria 1–5. Confirm selection-set hash unchanged.
8. Handoff, evidence commit then handoff child if needed. Message:

```text
p3-v3(2026-08-19-004): P2-C process-argv row intent/result

Evidence: create_intent/write_result; status <STATUS> <code>
Target: P2-C
```

9. Push and stop. Do not start P2-D or another row.

This environment has no `rtk`. Use `python3`, `pytest`, `sha256sum`, `git`.
`PYTHONPATH=src` when importing `p3_v3`.
