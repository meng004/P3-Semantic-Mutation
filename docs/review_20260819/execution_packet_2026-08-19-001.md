# Execution packet 2026-08-19-001 — P2-A one-subject preflight

Issued by the review model after
`docs/review_20260819/course_correction_C0.md` (`REDIRECT`).
This is the only authorized Cursor VM input for this round.

Paste the block below to a new Cursor VM together with init §1 and §E.

```text
EXECUTION_PACKET
packet_id: 2026-08-19-001
scientific_target: P2-A
correction_verdict: REDIRECT
baseline_commit: 4444061dde0159a5edd62753fe3cef2d881a308c
branch: cursor/p2a-one-subject-preflight-58d6
write_scope:
  - data/p3_v3/phase2_preflight/
  - data/p3_v3/handoff/2026-08-19-001.json
  - tests/p3_v3/test_phase2_p2a_preflight.py
forbidden:
  - Authority Lock / verifier hardening
  - 新授权链 / launch-packet / 资格认证框架
  - claim 升级 / P12 揭盲 / confirmatory 分母改写
  - 修改 src/p3_v3/、scripts/p3_v3/、data/p3_v3/protocol/、data/p3_v3/pilot/、data/p3_v3/phase1_frames/
  - 调用 c++、cmake、meson、autotools、qualify_cxx_link.py、pilot.py、Boost.Math 路径
  - 执行 Profiling Workload 选中行、build-frames、Package A/B/C、揭盲桥
acceptance_criteria:   # ≤8, 可机器核对
  1. data/p3_v3/phase2_preflight/preflight-spec.json 存在且 schema_version=p3-preflight-v1；phase_role=CONSTRUCTION_A；repository_identity=github.com/meng004/P3-Semantic-Mutation；expected_commit=4444061dde0159a5edd62753fe3cef2d881a308c；dependency_lock_path=data/p3_v3/protocol/environment_lock.json；dependency_lock_sha256=7706b4ce272d09df13c5212b04ec0f2519932f4225d5eac0d052d3225c7ff35f
  2. phase_inputs 恰好 3 条、按 path 升序且无重复：data/p3_v3/phase1_frames/out/profiling-workload-1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.json sha256=db46368cc3a8e78ffeceb60c38d46cd903ac49ddc779757ee94f1350bd15382d；data/p3_v3/phase1_frames/receipts.json sha256=8eeccfe4d1aebb09e6ee9ad2fadb82ac5b8697c40f602592faa6b3878692a440；data/p3_v3/protocol/protocol.json sha256=240d8270d41802c9d5b86f30564eadd1a86fd9ed09de2c7e947d17c1a4d78519
  3. smoke_commands 只含下列两条 argv，顺序固定；timeout_seconds=60；resource minima 与 worker_limit 均为 1：["python3","scripts/p3_v3/evidence.py","validate-protocol","--protocol","data/p3_v3/protocol/protocol.json"] 以及 ["python3","-c","import json;p=json.load(open('data/p3_v3/phase1_frames/out/profiling-workload-1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.json'));assert p['schema_version']=='p3-profiling-workload-v1';assert p['scale_class']=='L';print('WORKLOAD_BOUND')"]
  4. data/p3_v3/phase2_preflight/preflight-result.json 由 `PYTHONPATH=src python3 scripts/p3_v3/evidence.py run-preflight --root . --spec data/p3_v3/phase2_preflight/preflight-spec.json --output data/p3_v3/phase2_preflight/preflight-result.json` 独占写出；schema_version=p3-preflight-result-v1；status∈{PASS,FAIL}；failure_code 在 PASS 时为空字符串；artifact_sha256 等于去掉该字段后的 canonical SHA-256；phase_role=CONSTRUCTION_A；commit=4444061dde0159a5edd62753fe3cef2d881a308c
  5. data/p3_v3/phase2_preflight/subject-terminal.json 为 canonical JSON，恰好含 keys：schema_version=p3-p2a-subject-terminal-v1、packet_id=2026-08-19-001、scientific_target=P2-A、neutral_snapshot_id=1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72、discovery_status=EXECUTABLE、adapter_id=CMAKE_CTEST_V1、denominator=PREFLIGHT_ONLY、formal_denominator_membership=false、claims=blocked、preflight_status 等于收据 status、preflight_result_sha256 等于收据 artifact_sha256、artifact_sha256 为自哈希
  6. git diff --name-only 4444061dde0159a5edd62753fe3cef2d881a308c HEAD 的路径全部落在 write_scope；不得出现 src/p3_v3/、scripts/p3_v3/、data/p3_v3/pilot/、data/p3_v3/protocol/、qualify_cxx_link
  7. PYTHONPATH=src python3 -m pytest tests/p3_v3/test_phase2_p2a_preflight.py -q 退出 0；该测试只读本包产物与冻结 Phase 1 输入，不调用编译器，不跑 tests/p3_v3 全量
  8. data/p3_v3/handoff/2026-08-19-001.json 含 packet_id、baseline_commit、head_commit、commands[]（每条 command/env/exit_code）、input_sha256、output_sha256、failures_exclusions_retries、unresolved、closed_scientific_target 一句（关闭 P2-A 或诚实 FAIL 已入账 PREFLIGHT_ONLY）
out_of_list_policy: backlog_only
repair_cap: 2
handoff_path: data/p3_v3/handoff/2026-08-19-001.json
review_report_path: docs/review_20260819/2026-08-19-001_review.md
notes_for_executor: 见下文；做完即停，不要设想 P2-B。
```

## Notes for executor

Do not modify production modules. Reuse `run-preflight` as-is.

1. `git fetch origin` and pin the worktree to
   `4444061dde0159a5edd62753fe3cef2d881a308c`. Create
   `cursor/p2a-one-subject-preflight-58d6` from that commit.
2. Confirm `git status --porcelain=v1 --untracked-files=no` is empty before
   the preflight command. Write new files as untracked first so HEAD still
   equals `expected_commit`.
3. Create `data/p3_v3/phase2_preflight/` and the spec with the exact fields
   in acceptance criteria 1–3. Do not add extra keys.
4. Run, in this order, from the repository root:

```bash
python3 scripts/p3_v3/evidence.py validate-protocol --protocol data/p3_v3/protocol/protocol.json
PYTHONPATH=src python3 scripts/p3_v3/evidence.py run-preflight \
  --root . \
  --spec data/p3_v3/phase2_preflight/preflight-spec.json \
  --output data/p3_v3/phase2_preflight/preflight-result.json
```

   `run-preflight` writes exclusively. If the output path already exists,
   stop and record `unresolved`; do not add a retry framework. A `FAIL`
   status is an honest P2-A account, not a license to compile the subject.
5. Write `subject-terminal.json` from the result. Keep
   `formal_denominator_membership=false` and `denominator=PREFLIGHT_ONLY`
   even when status is `PASS`.
6. Add `tests/p3_v3/test_phase2_p2a_preflight.py` that machine-checks
   criteria 1–5 only (load JSON, compare sha256sum, recompute
   `artifact_sha256` with `p3_v3.artifacts.canonical_sha256`). Do not
   import `toolchain_qualification` or `pilot_build`.
7. Run only that test file. Do not run the full `tests/p3_v3` suite.
8. Write the handoff, commit with

```text
p3-v3(2026-08-19-001): P2-A one-subject CONSTRUCTION_A preflight receipt

Evidence: run-preflight exit <code>; result <artifact_sha256>
Target: P2-A
```

9. Push the branch and stop.

This environment has no `rtk`. Use `python3`, `pytest`, `sha256sum`, `git`.
Set `PYTHONPATH=src` when importing `p3_v3`.
