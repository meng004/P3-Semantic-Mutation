# Execution packet 2026-08-19-002 — P2-B PILOT_ONLY preflight terminals

Issued after C1 `PASS_WITH_DISCLOSURE` / `CLOSE_AND_ADVANCE` on
`docs/review_20260819/2026-08-19-001_review.md`.
This is the only authorized Cursor VM input for this round.

P2-A 单受试 PASS 已入账。本包关闭的是 **P2-B 的最小切片**：一条合成
`PILOT_ONLY` 流水线的成功终端态 **和** 失败终端态。不是整个 Phase 2，
不是 profiling（P2-C），不是 Boost.Math。

```text
EXECUTION_PACKET
packet_id: 2026-08-19-002
scientific_target: P2-B
correction_verdict: CLOSE_AND_ADVANCE
baseline_commit: 4444061dde0159a5edd62753fe3cef2d881a308c
branch: cursor/p2b-pilot-only-terminals-58d6
write_scope:
  - data/p3_v3/phase2_pilot_only/
  - data/p3_v3/handoff/2026-08-19-002.json
  - tests/p3_v3/test_phase2_p2b_pilot_terminals.py
forbidden:
  - Authority Lock / verifier hardening
  - 新授权链 / launch-packet / 资格认证框架
  - claim 升级 / P12 揭盲 / confirmatory 分母改写
  - 修改 src/p3_v3/、scripts/p3_v3/、data/p3_v3/protocol/、data/p3_v3/pilot/、data/p3_v3/phase1_frames/、data/p3_v3/phase2_preflight/
  - 调用 c++、cmake、meson、autotools、qualify_cxx_link.py、pilot.py、Boost.Math 路径
  - 执行 Profiling Workload、build-frames、Package A/B/C、create_intent 科研作业、受试 1f67b3f3…
acceptance_criteria:   # ≤8, 可机器核对
  1. data/p3_v3/phase2_pilot_only/synthetic-subject.json 为 canonical JSON，恰好 keys：schema_version=p3-p2b-synthetic-subject-v1、subject_id=p2b-pilot-only-synthetic-001、denominator=PILOT_ONLY、formal_denominator_membership=false、claims=blocked、artifact_sha256 自哈希
  2. 两个 spec 均为 p3-preflight-v1 / CONSTRUCTION_A / repository_identity=github.com/meng004/P3-Semantic-Mutation / expected_commit=4444061dde0159a5edd62753fe3cef2d881a308c / dependency_lock_path=data/p3_v3/protocol/environment_lock.json / dependency_lock_sha256=7706b4ce272d09df13c5212b04ec0f2519932f4225d5eac0d052d3225c7ff35f / timeout_seconds=60 / 三个 resource minima 与 worker_limit=1；phase_inputs 恰好 2 条升序：synthetic-subject.json（文件 SHA-256=该文件）与 data/p3_v3/protocol/protocol.json（sha256=240d8270d41802c9d5b86f30564eadd1a86fd9ed09de2c7e947d17c1a4d78519）
  3. PASS spec `preflight-spec-pass.json` 的 smoke_commands 仅一条：["python3","scripts/p3_v3/evidence.py","validate-protocol","--protocol","data/p3_v3/protocol/protocol.json"]；FAIL spec `preflight-spec-fail.json` 的 smoke_commands 仅一条：["python3","-c","raise SystemExit(2)"]
  4. 在 tracked 干净且 HEAD=4444061d… 时，分别独占写出 `preflight-result-pass.json` 与 `preflight-result-fail.json`（命令见 notes）。PASS 收据 status=PASS 且 failure_code=""；FAIL 收据 status=FAIL 且 failure_code=E_PREFLIGHT_SMOKE；两者 schema=p3-preflight-result-v1、phase_role=CONSTRUCTION_A、commit=4444061d…、artifact_sha256 可复算
  5. `terminals.json` 为 canonical JSON，恰好 keys：schema_version=p3-p2b-terminals-v1、packet_id=2026-08-19-002、scientific_target=P2-B、subject_id=p2b-pilot-only-synthetic-001、denominator=PILOT_ONLY、formal_denominator_membership=false、claims=blocked、pass_result_sha256=PASS 收据 artifact_sha256、fail_result_sha256=FAIL 收据 artifact_sha256、artifact_sha256 自哈希
  6. git diff --name-only 4444061dde0159a5edd62753fe3cef2d881a308c HEAD 全部落在 write_scope；不得出现 1f67b3f3、boost_math、qualify_cxx_link、src/p3_v3、scripts/p3_v3
  7. PYTHONPATH=src python3 -m pytest tests/p3_v3/test_phase2_p2b_pilot_terminals.py -q 退出 0；只核对本包产物；不跑全量 tests/p3_v3；不 import toolchain_qualification / pilot_build / run_records.create_intent
  8. data/p3_v3/handoff/2026-08-19-002.json 含 packet_id、baseline_commit、head_commit、commands[]、input_sha256、output_sha256、failures_exclusions_retries、unresolved、closed_scientific_target（一句：P2-B 合成 PILOT_ONLY 受试留下 PASS+FAIL 终端态；非 Phase 2 全关）
out_of_list_policy: backlog_only
repair_cap: 2
handoff_path: data/p3_v3/handoff/2026-08-19-002.json
review_report_path: docs/review_20260819/2026-08-19-002_review.md
notes_for_executor: 见下文；做完即停，不要做 P2-C。
```

## Notes for executor

Reuse `scripts/p3_v3/evidence.py run-preflight` only. No new production modules.

1. Fetch and pin HEAD to `4444061dde0159a5edd62753fe3cef2d881a308c`. Create
   `cursor/p2b-pilot-only-terminals-58d6`. Tracked tree must be clean
   (`git status --porcelain=v1 --untracked-files=no` empty) when each
   `run-preflight` runs, so `expected_commit` matches HEAD.
2. Write `synthetic-subject.json` first (canonical JSON, exclusive keys
   in criterion 1). Then write the two specs (criterion 2–3). Do not add
   extra keys.
3. Run, from the repository root, **pass then fail**. Each `--output`
   path must be absent (exclusive write):

```bash
python3 scripts/p3_v3/evidence.py validate-protocol --protocol data/p3_v3/protocol/protocol.json
PYTHONPATH=src python3 scripts/p3_v3/evidence.py run-preflight \
  --root . \
  --spec data/p3_v3/phase2_pilot_only/preflight-spec-pass.json \
  --output data/p3_v3/phase2_pilot_only/preflight-result-pass.json
PYTHONPATH=src python3 scripts/p3_v3/evidence.py run-preflight \
  --root . \
  --spec data/p3_v3/phase2_pilot_only/preflight-spec-fail.json \
  --output data/p3_v3/phase2_pilot_only/preflight-result-fail.json
```

   The FAIL command should still exit 0: `run-preflight` records
   `status=FAIL` in the JSON; it does not turn a booked smoke failure
   into a CLI crash. If the CLI exits nonzero, stop and put the
   exception in `unresolved`. Do not retry by adding a framework.
4. Write `terminals.json` from the two `artifact_sha256` values.
5. Add `tests/p3_v3/test_phase2_p2b_pilot_terminals.py` checking
   criteria 1–5 only (`read_canonical_json` + `canonical_sha256` +
   `sha256sum`). Forbidden tokens in specs/smoke: `c++`, `cmake`,
   `1f67b3f3`, `boost_math`, `qualify_cxx_link`, `pilot.py`.
6. Run only that test file. Write handoff. Commit evidence first, then
   handoff if the handoff cannot embed its own SHA (same pattern as
   2026-08-19-001). Message:

```text
p3-v3(2026-08-19-002): P2-B PILOT_ONLY PASS+FAIL preflight terminals

Evidence: run-preflight pass/fail receipts; catalog <artifact_sha256>
Target: P2-B
```

7. Push and stop. Do not start P2-C, profiling, or another subject.

This environment has no `rtk`. Use `python3`, `pytest`, `sha256sum`, `git`.
`PYTHONPATH=src` when importing `p3_v3`.
