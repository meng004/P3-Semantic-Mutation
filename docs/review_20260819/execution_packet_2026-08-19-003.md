# Execution packet 2026-08-19-003 — P2-C one-row profiling attempt

Issued after C1 `PASS_WITH_DISCLOSURE` / `CLOSE_AND_ADVANCE` on
`docs/review_20260819/2026-08-19-002_review.md`, and after the author
replied `授权 P2-C 包` to the C1 question.

This is the only authorized Cursor VM input for this round.

P2-A / P2-B 最小切片已入账。本包关闭的是 **P2-C 的最小切片**：对已冻结
Profiling Workload 的 **一条** 已选行为，留下一对
`create_intent` / `write_result`。不是整个 Phase 2，不是 20 行全跑，
不是 P2-D 技术区间，不是 CMake 构建。

Author authorization (verbatim): packet-scoped script under
`scripts/p3_v3/` (not a new framework); one already-selected
`EXECUTABLE` subject; one intent/result pair; claims stay `blocked`;
selection set must not change.

Pinned subject = first `discovery_status=EXECUTABLE` row in Phase 1
receipts (same as P2-A):
`1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72`.
Pinned behavior = that workload's `selected_behavior_ids[0]`:
`72e1a3e8e8dc8bf0e6c0bd3ad9634299dcc910686c46ce4794021f5ca2eae6db`
(`PUBLIC_API` header; no adapter process argv). Do **not** skip to a
CLI/EXAMPLE row.

```text
EXECUTION_PACKET
packet_id: 2026-08-19-003
scientific_target: P2-C
correction_verdict: CLOSE_AND_ADVANCE
author_authorization: 授权 P2-C 包
baseline_commit: 4444061dde0159a5edd62753fe3cef2d881a308c
branch: cursor/p2c-one-row-profiling-58d6
write_scope:
  - scripts/p3_v3/run_p2c_one_row.py
  - data/p3_v3/phase2_profiling/
  - data/p3_v3/handoff/2026-08-19-003.json
  - tests/p3_v3/test_phase2_p2c_one_row.py
forbidden:
  - Authority Lock / verifier hardening
  - 新授权链 / launch-packet / 资格认证框架 / 通用 profiler 框架
  - claim 升级 / P12 揭盲 / confirmatory 分母改写
  - 修改 src/p3_v3/、scripts/p3_v3/evidence.py、scripts/p3_v3/pilot.py、data/p3_v3/protocol/、data/p3_v3/pilot/、data/p3_v3/phase1_frames/、data/p3_v3/phase2_preflight/、data/p3_v3/phase2_pilot_only/
  - 调用 c++、cmake、meson、autotools、qualify_cxx_link.py、pilot.py、Boost.Math 路径
  - 下载 P12 包 / 改 selected_behavior_ids / 跑第二条行为 / build-frames / Package A/B/C / P2-D
acceptance_criteria:   # ≤8, 可机器核对
  1. scripts/p3_v3/run_p2c_one_row.py 存在；通过 `from p3_v3.run_records import create_intent, write_result` 写收据；源文件不得出现 token：c++、cmake、meson、autotools、qualify_cxx_link、boost_math、p3-phase1-unexecuted、PHASE1_PROFILING_NOT_EXECUTED
  2. 在 tracked 干净且 HEAD=4444061d… 时独占写出 data/p3_v3/phase2_profiling/jobs/p2c-20260819-003/1/intent.json 与同目录 result.json（目录名必须是 job_id/attempt）。调用 create_intent 先于 write_result。
  3. intent 恰好 _INTENT_SCHEMA 的 18 个 key：job_id=p2c-20260819-003、protocol_sha256=240d8270d41802c9d5b86f30564eadd1a86fd9ed09de2c7e947d17c1a4d78519、phase=PHASE_1（现有 write_result 只允许 PHASE_1+PROFILING 绑 call_trace；科学目标仍是 P2-C）、argv 为下面 notes 的固定列表、cwd_identity=github.com/meng004/P3-Semantic-Mutation、input_sha256 恰好升序三条 240d8270… / 8eeccfe4d1aebb09e6ee9ad2fadb82ac5b8697c40f602592faa6b3878692a440 / db46368cc3a8e78ffeceb60c38d46cd903ac49ddc779757ee94f1350bd15382d、seed=null、timeout_seconds=60、attempt=1、object_type=PROFILING_BEHAVIOR、object_id=72e1a3e8e8dc8bf0e6c0bd3ad9634299dcc910686c46ce4794021f5ca2eae6db、mr_id=not-applicable、evaluation_input_class=E_COMMON、evaluation_input_id=60c34610710b065bb3e0d649ce5a5b5badcfdf7147829445f925f7bdaab899a8、repetition_id=1、environment_id=p2c-one-row-2026-08-19-003、job_role=PROFILING。environment_sha256 为 64 hex 且 ≠ 396e3df895988aafcaa276a51c6e2b6a46aef1f31017b84b2d22de4b81eb9007（Phase 1 占位 env）。argv 不得含 p3-phase1-unexecuted。
  4. result 恰好 _RESULT_SCHEMA 的 11 个 key：job_id/attempt 与 intent 一致；status=MISSING_WITH_REASON；failure_code∈{E_SOURCE_TREE_ABSENT,E_PROFILE_NO_PROCESS_ARGV}（无树/无匹配本地 archive → 前者；树在且本行是 PUBLIC_API 无 process argv → 后者）；scientific_outcome=null；call_trace_sha256=37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570（空列表 canonical）；call_trace_identity=canonical_sha256({job_id,attempt:1,behavior_id:object_id,call_trace_sha256,domain:P3-PROFILING-TRACE-v1})；stdout_sha256/stderr_sha256 为 64 hex；duration_seconds≥0；exit_code 可为 null。failure_code 不得为 PHASE1_PROFILING_NOT_EXECUTED。
  5. data/p3_v3/phase2_profiling/row-terminal.json 为 canonical JSON，恰好 keys：schema_version=p3-p2c-one-row-terminal-v1、packet_id=2026-08-19-003、scientific_target=P2-C、neutral_snapshot_id=1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72、discovery_status=EXECUTABLE、adapter_id=CMAKE_CTEST_V1、behavior_id=72e1a3e8e8dc8bf0e6c0bd3ad9634299dcc910686c46ce4794021f5ca2eae6db、denominator=PROFILING_ONE_ROW、formal_denominator_membership=false、claims=blocked、result_status 等于 result.status、result_failure_code 等于 result.failure_code、workload_file_sha256=db46368cc3a8e78ffeceb60c38d46cd903ac49ddc779757ee94f1350bd15382d、selected_behavior_ids_sha256=e398d0a7764d44514d467c9170ba663457b7d38169354c4a310ffa3ffc37eca6、artifact_sha256 自哈希。冻结 workload 文件仍为上述 SHA（不得改选择集）。
  6. git diff --name-only 4444061dde0159a5edd62753fe3cef2d881a308c HEAD 全部落在 write_scope；不得出现 src/p3_v3、evidence.py、pilot.py、qualify_cxx_link、boost_math、phase1_frames、phase2_preflight、phase2_pilot_only
  7. PYTHONPATH=src python3 -m pytest tests/p3_v3/test_phase2_p2c_one_row.py -q 退出 0；只核对本包产物与冻结 Phase 1 输入；不跑全量 tests/p3_v3；不调用编译器
  8. data/p3_v3/handoff/2026-08-19-003.json 含 packet_id、baseline_commit、head_commit、commands[]、input_sha256、output_sha256、failures_exclusions_retries、unresolved、closed_scientific_target（一句：P2-C 单行 intent/result 已入账；非 Phase 2 全关；非 20 行 profiling 已执行）
out_of_list_policy: backlog_only
repair_cap: 2
handoff_path: data/p3_v3/handoff/2026-08-19-003.json
review_report_path: docs/review_20260819/2026-08-19-003_review.md
notes_for_executor: 见下文；做完即停，不要做 P2-D。
```

## Notes for executor

Reuse `p3_v3.run_records.create_intent` / `write_result` as-is. One new
script only. Do not edit `src/p3_v3/`.

1. Fetch and pin HEAD to `4444061dde0159a5edd62753fe3cef2d881a308c`.
   Create `cursor/p2c-one-row-profiling-58d6`. Tracked tree must be
   clean (`git status --porcelain=v1 --untracked-files=no` empty) when
   the script writes the exclusive intent/result.
2. Confirm the frozen workload file SHA-256 is
   `db46368cc3a8e78ffeceb60c38d46cd903ac49ddc779757ee94f1350bd15382d`
   and that `72e1a3e8…` is `selected_behavior_ids[0]`. If either check
   fails, stop and put the exception in `unresolved`. Do not pick
   another row.
3. Tree lookup (do not download):
   `data/p3_v3/p12_intake/extracted/1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72/`.
   Optional: if that directory is absent **and**
   `data/p3_v3/p12_intake/archives/1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.tar`
   exists **and** its SHA-256 equals bridge
   `source_archive_sha256=c7c3d38533c01a7366d2511497082af5f30f510d0f95db822d98441a06a1898c`,
   extract once into the extracted path (gitignore already covers it;
   do not `git add` it). If neither tree nor matching archive exists,
   that is `E_SOURCE_TREE_ABSENT`, not a license to cmake or to fetch
   P12.
4. This pinned row is `PUBLIC_API` /
   `include/nvector/trilinos/SundialsTpetraVectorInterface.hpp`. The
   CMAKE_CTEST_V1 adapter does not give it a process argv. After the
   tree check, the honest result is `E_PROFILE_NO_PROCESS_ARGV` when
   the tree (or just-extracted tree) is present. Do **not** compile a
   translation unit. Do **not** skip to `target:ltest` or an EXAMPLE.
5. `environment_sha256` = `canonical_sha256` of
   `{"dependency_lock_sha256":"7706b4ce272d09df13c5212b04ec0f2519932f4225d5eac0d052d3225c7ff35f","domain":"P3-P2C-ONE-ROW-ENV-v1","platform":<platform.system()>,"python":<platform.python_version()>}`
   (key order does not matter; canonicalization sorts keys).
6. Fixed argv (also the script invocation from the repository root):

```bash
PYTHONPATH=src python3 scripts/p3_v3/run_p2c_one_row.py \
  --root . \
  --workload data/p3_v3/phase1_frames/out/profiling-workload-1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.json \
  --behavior-id 72e1a3e8e8dc8bf0e6c0bd3ad9634299dcc910686c46ce4794021f5ca2eae6db \
  --jobs-root data/p3_v3/phase2_profiling/jobs \
  --job-id p2c-20260819-003 \
  --terminal-output data/p3_v3/phase2_profiling/row-terminal.json
```

   Intent `argv` must be exactly those 14 strings (the `PYTHONPATH=src`
   prefix is env, not argv):
   `["python3","scripts/p3_v3/run_p2c_one_row.py","--root",".","--workload","data/p3_v3/phase1_frames/out/profiling-workload-1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.json","--behavior-id","72e1a3e8e8dc8bf0e6c0bd3ad9634299dcc910686c46ce4794021f5ca2eae6db","--jobs-root","data/p3_v3/phase2_profiling/jobs","--job-id","p2c-20260819-003","--terminal-output","data/p3_v3/phase2_profiling/row-terminal.json"]`
7. Add `tests/p3_v3/test_phase2_p2c_one_row.py` checking criteria 1–5
   (`read_canonical_json` + `canonical_sha256`). Confirm the workload
   file SHA-256 is still `db46368c…` and
   `selected_behavior_ids_sha256` still `e398d0a7…`.
8. Run only that test file. Write handoff. Commit evidence first, then
   handoff if the handoff cannot embed its own SHA (same pattern as
   001/002). Message:

```text
p3-v3(2026-08-19-003): P2-C one-row profiling intent/result

Evidence: create_intent/write_result; status MISSING_WITH_REASON <code>
Target: P2-C
```

9. Push and stop. Do not start P2-D, do not profile another row, do
   not merge this onto the review branch.

This environment has no `rtk`. Use `python3`, `pytest`, `sha256sum`, `git`.
`PYTHONPATH=src` when importing `p3_v3`.
