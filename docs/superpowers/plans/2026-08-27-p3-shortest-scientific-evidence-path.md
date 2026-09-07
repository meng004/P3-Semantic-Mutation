# P3 Shortest Scientific Evidence Path Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Status:** DRAFT — awaiting user approval of the two-slice scientific design; this document does not authorize implementation or a formal run.

**Goal:** 在不扩张合同、schema、资格链或运行治理的前提下，尽快产生两类能改变研究决策的数据：先把主 RQ4 cohort eligibility 从“待核实”收口为冻结发布下的确定终态，再为 RQ1 获取第一份非 Boost.Math、可能产生 confirmed technique tag 的正式 profiling receipt。

**Architecture:** 使用两个串联切片。切片 A 只复用现有 P12 pin、bridge validator 和冻结规模门槛，零科学运行地关闭主 RQ4 eligibility；切片 B 只选择一个 outcome-blind、低成本、已有 20 行冻结 workload 的 Python subject，先做源归档和 workload 可执行性审计，通过后才允许最小 runner 实现与一次正式运行。任何 FAIL/INCONCLUSIVE 都作为数据保留，不替换 subject、不重试。

**Tech Stack:** Python 3.10+、现有 `src/p3_v3` / `scripts/p3_v3` CLI、canonical JSON、Git pinned release、SHA-256、pytest、Python `sys.setprofile` 或等价标准库 call tracing。

## Global Constraints

- 科学快照固定为 P3 commit `25f0ebf5944328aa5b436c810739c8f9176213a9` 和 P12 release commit `d57fa8119e47baf88c5bcff2d67346864cf3672d`。
- Boost.Math formal profiling 已终态，`FORMAL_PROFILING_RETRY_FORBIDDEN=true`；不得修改、重跑或用新的 receipt 覆盖。
- P12 bridge 的生产核验必须返回 `status=PASS`；Cursor 未认证导致的 `Repository not found` 不得再次解释为科学失败。
- P12 冻结 release 只有 35 个 formal item；其既有 successor plan 明确写明不足以满足 60 个 `P12_PAIRED` real-fault-family 门槛。不得为主 RQ4 先下载约 3.3 GB 的 35 份归档。
- 不新增 contract、schema、baseline、gate、hash 链、授权格式或通用控制器；只复用现有 identity 和 validator。
- 不跑全量测试。每个实现任务只跑新行为的 focused tests、35 份既有 profiling receipt 回归和 `git diff --check`。
- 新 subject 的正式 profiling 只允许一次；不自动重试，不事后修改 workload、输入生成规则或 entrypoint 映射。
- 正式运行前的实现、测试和 source recovery 不计科学进度；只有 eligibility terminal、正式 receipt 和 claim-impact verdict 计入科学进度。
- 当前计划不进入论文写作，不升级永久 blocked claims C6–C8。

## Model and reasoning allocation

| 工作 | 模型 / 推理 | 理由 |
|---|---|---|
| 固定 SHA、bridge 核验、计数、文件 hash、focused tests、一次命令执行 | `gpt-5.6-luna / low` | 完全机械，避免消耗科学预算 |
| workload 可执行性审计、单 archive 恢复、最小 Python runner 实现 | `gpt-5.6-terra / medium` | 有界工程判断，不扩展科学语义 |
| RQ4 eligibility 终态、正式 profiling 后的 claim-impact 判定 | `gpt-5.6-sol / high` | 只在科学转场和主张强度判断使用 |
| `xhigh` / `max` | 禁止默认使用 | 仅一次 `sol/high` 仍存在证据冲突时另行申请 |

---

### Task 1: 关闭冻结 P12 release 下的主 RQ4 eligibility

**Files:**
- Read: `data/p3_v3/p12_intake/consumer_lock.json`
- Read: `data/p3_v3/p12_intake/verified_bridge.json`
- Read: `data/p3_v3/protocol/analysis_spec.md`
- Read from P12 pin: `docs/superpowers/plans/2026-08-08-defect4mr-successor-release-implementation.md`
- Create: `docs/review_20260827/p3_rq4_frozen_release_eligibility_decision.md`

**Interfaces:**
- Consumes: pinned bridge `eligible_item_count=35`、冻结 RQ4 floor `>=60 real-fault families`、P12 producer 既有明确判断“35 项不足以满足 60 个 P12_PAIRED 门槛”。
- Produces: 一页 narrative decision，不创建新 schema 或 gate；terminal 只能是 `RQ4_CONFIRMATORY_INELIGIBLE_FROZEN_RELEASE` 或 `EVIDENCE_CONFLICT`。

- [ ] **Step 1: 在干净隔离 worktree 固定 P3 身份**

Run:

```bash
rtk git fetch origin cursor/p3-boost-math-rq-handoff-0445
rtk git worktree add --detach /tmp/p3-shortest-science-25f 25f0ebf5944328aa5b436c810739c8f9176213a9
rtk git -C /tmp/p3-shortest-science-25f rev-parse HEAD
rtk git -C /tmp/p3-shortest-science-25f status --porcelain=v1 --untracked-files=all
```

Expected: HEAD 精确匹配；新 worktree porcelain 为空。当前主工作树的既有未跟踪文件不参与判定，也不得删除。

- [ ] **Step 2: 核验 P12 live pin 和 bridge**

Run:

```bash
rtk git clone --no-checkout https://github.com/meng004/P12-Defect4MR.git /tmp/p3-shortest-science-p12
rtk git -C /tmp/p3-shortest-science-p12 cat-file -e d57fa8119e47baf88c5bcff2d67346864cf3672d^{commit}
rtk env PYTHONPATH=/tmp/p3-shortest-science-25f/src python3 /tmp/p3-shortest-science-25f/scripts/p3_v3/evidence.py verify-bridge --repo-root /tmp/p3-shortest-science-p12 --lock /tmp/p3-shortest-science-25f/data/p3_v3/p12_intake/consumer_lock.json
```

Expected: `{"bridge_sha256":"aba70e89b603866f6171ee93a1004d04954e1a3e90b093ba1db889da17690000","status":"PASS"}`。

- [ ] **Step 3: 机械证明 confirmatory floor 不可满足**

核验并在 decision 文档逐项记录：

```text
P12_FULL formal item upper bound = 35
Required P12_PAIRED real-fault families >= 60
35 < 60
Producer plan explicitly states current 35 are insufficient
```

不得把 `eligible_for_criterion=true` 解释为已满足 `P12_PAIRED`；不得用未知的 project/family identity 把 35 扩成 60。

- [ ] **Step 4: 写唯一允许的科学终态**

`p3_rq4_frozen_release_eligibility_decision.md` 必须包含：

```text
RQ4_CONFIRMATORY_INELIGIBLE_FROZEN_RELEASE

The pinned P12 successor release is origin-valid and bridge-valid, but its
35 formal items cannot satisfy the prespecified floor of 60 P12_PAIRED
real-fault families. Primary confirmatory RQ4 is therefore ineligible on this
frozen release. P12 evidence may be retained only for descriptive, sensitivity,
or case-series use under the existing contract. No outcome was opened and no
cohort member was replaced.
```

同时记录：C5 继续 `blocked`，原因从“外部 authority 未知”收口为“冻结发布规模地板不满足”。不编辑冻结 scientific plan。

- [ ] **Step 5: 验证 decision 没有越界主张**

必须出现：bridge `PASS`、35、60、`35 < 60`、descriptive/sensitivity/case-series、C5 `blocked`。

不得出现：P12 repository 不存在、P12 producer authority failure、RQ4 supported、P12_PAIRED complete、归档缺失导致 eligibility fail。

Run:

```bash
rtk git -C /tmp/p3-shortest-science-25f diff --check
```

Expected: exit 0。

**Checkpoint summary:** 这是第一份能直接改变 cohort eligibility 状态的数据。完成后停止所有 confirmatory RQ4 profile/analysis 投入。

---

### Task 2: 冻结唯一 RQ1 下一 subject，避免继续围绕 Boost.Math 优化

**Files:**
- Read: `data/p3_v3/phase1_frames/out/profiling-workload-4e7e9556b3d621681c88c82f26cd95f5604d7a8b85cc56bf7e6d4db5a274f38b.json`
- Read: `data/p3_v3/phase1_frames/out/adapter-discovery-4e7e9556b3d621681c88c82f26cd95f5604d7a8b85cc56bf7e6d4db5a274f38b.json`
- Read: `data/p3_v3/p12_intake/descriptors/4e7e9556b3d621681c88c82f26cd95f5604d7a8b85cc56bf7e6d4db5a274f38b.json`
- Append decision section to: `docs/review_20260827/p3_rq4_frozen_release_eligibility_decision.md`

**Interfaces:**
- Consumes: frozen Phase-1 evidence only; no profiling outcome.
- Produces: fixed RQ1 pilot subject `4e7e9556...` with an outcome-blind rationale.

- [ ] **Step 1: 核验候选身份和冻结输入**

Expected facts:

```text
neutral_snapshot_id = 4e7e9556b3d621681c88c82f26cd95f5604d7a8b85cc56bf7e6d4db5a274f38b
language_family = python
ecosystem = meson
adapter discovery = EXECUTABLE
selected rows = 20
category counts = PUBLIC_API 8 / CLI 1 / EXAMPLE 3 / BENCHMARK 8
normalized_source_tree_sha256 = f8826c3b975f8699e136e0b6b4cd4c29bf0d7e9a3be04fe09b947eb8998e727b
source_archive_sha256 = c73c0ec41ea53ba9ecb0f9903a55a19ed6c1dbfd1de00404d96b58d9c30bb3c9
build_descriptor_sha256 = c6efda5c841b1900a51b69dc3982168098752015351a7e7fa07f201e70f99836
```

- [ ] **Step 2: 固定选择理由**

选择规则必须在任何新运行前写死：

1. 排除已终态且禁止重跑的 Boost.Math；
2. 要求 Phase-1 adapter `EXECUTABLE`；
3. 要求冻结 workload 有完整 20 行；
4. 优先 Python，以降低一次正式动态 call trace 的构建成本；
5. 优先包含非 header-only 的 PUBLIC_API/CLI/EXAMPLE/BENCHMARK 混合行；
6. 不使用任何运行结果或预期 technique tag 排序。

- [ ] **Step 3: 写停止规则**

候选固定后不得因 source recovery、编译、运行或分类结果不理想而替换为第二个 subject。唯一后继是终态记录和一次科学判读。

**Checkpoint summary:** 该步骤不升级 claim，但防止 post-outcome subject shopping，并把下一笔工程预算绑定到一个可证伪数据点。

---

### Task 3: 只恢复一个 source archive，并作 byte/tree 身份验收

**Files:**
- External input only: `/tmp/p3-numpy-formal-profile-input/4e7e9556b3d621681c88c82f26cd95f5604d7a8b85cc56bf7e6d4db5a274f38b.tar`
- Runtime extraction only: `/tmp/p3-numpy-formal-profile-source`
- No tracked file changes.

**Interfaces:**
- Consumes: P12 producer/custodian 提供的单份 content-addressed archive。
- Produces: `SOURCE_IDENTITY_PASS`、`SOURCE_IDENTITY_FAIL` 或 `SOURCE_UNAVAILABLE`。

- [ ] **Step 1: 请求单份 archive，不请求 35 份批量交付**

请求必须同时给出 snapshot ID、archive SHA、normalized tree SHA 和 descriptor SHA。不得用“最新 NumPy”或分支名代替固定字节。

- [ ] **Step 2: 机械核验普通文件和 SHA-256**

Run:

```bash
rtk shasum -a 256 /tmp/p3-numpy-formal-profile-input/4e7e9556b3d621681c88c82f26cd95f5604d7a8b85cc56bf7e6d4db5a274f38b.tar
```

Expected: `c73c0ec41ea53ba9ecb0f9903a55a19ed6c1dbfd1de00404d96b58d9c30bb3c9`。

- [ ] **Step 3: 使用项目既有 normalized-tree 规则验收解包树**

不得手写第二套 normalization。使用 P3 已有 canonical tree implementation；输出必须等于 `f8826c3b...8e727b`。

- [ ] **Step 4: 在任一不匹配时停止**

不下载替代版本、不切换 subject、不改冻结 SHA。`SOURCE_UNAVAILABLE` 是外部缺失终态；`SOURCE_IDENTITY_FAIL` 是身份冲突终态。

**Checkpoint summary:** 只有 `SOURCE_IDENTITY_PASS` 允许 Task 4；其它终态直接结束本执行切片。

---

### Task 4: 审计 20 行 frozen workload 是否能在不重写语义下执行

**Files:**
- Read: frozen workload、adapter discovery、Public Behavior Frame、input generator registry。
- Create: `docs/review_20260827/p3_numpy_frozen_workload_executability_audit.md`
- No production code changes.

**Interfaces:**
- Consumes: 20 个 `selected_rows`、对应 `raw_schema`、`declared_input_schema_sha256`、现有 `JSON_SCHEMA_DRAFT2020_12_V1` generator。
- Produces: `WORKLOAD_EXECUTABLE_AS_FROZEN` 或 `WORKLOAD_EXECUTION_UNDERSPECIFIED`。

- [ ] **Step 1: 对每行建立机械映射表**

每行必须列出：behavior ID、category、entrypoint、schema hash、可复用 generator、唯一 argv/callable 解释、预期 subject-root containment。不得新增参数、测试 case、benchmark selector 或输入类型。

- [ ] **Step 2: 固定可执行性判据**

只有同时满足以下条件才是 `WORKLOAD_EXECUTABLE_AS_FROZEN`：

- 20/20 行都能由现有字段唯一导出 argv 或 Python callable；
- input generator 能从已冻结 raw schema 生成参数；
- 不需要人工选择 pytest case、benchmark method 或 API 参数语义；
- call trace 可限制在受控 source root；
- 每行有预设 timeout 和确定的终态映射。

- [ ] **Step 3: 记录负结果，不补写 workload**

若任一行需要现场解释，terminal 为 `WORKLOAD_EXECUTION_UNDERSPECIFIED`。这时不实现 runner；把该结果作为 Phase-1 workload executable-discovery 与真实可运行性之间的限制，提交科学判读。

- [ ] **Step 4: 仅在 20/20 通过时冻结最小 runner design**

design 只允许：Python argv/callable resolution、既有 generator 调用、subject-contained call trace、timeout、receipt emission。禁止通用多语言 runner、自动修复 entrypoint 和 fallback 到 installed NumPy。

**Checkpoint summary:** 本步骤是最重要的投入止损点；预计半天内给出二元终态，未通过时避免一天以上无效实现。

---

### Task 5: 最小 Python profiling runner（仅在 Task 4 PASS 后）

**Files:**
- Create: `src/p3_v3/python_profiling_runner.py`
- Modify: `scripts/p3_v3/profile.py`
- Test: `tests/p3_v3/test_python_profiling_runner.py`
- Modify only if existing receipt binding requires it: `tests/p3_v3/test_bridge_and_frames.py`
- Test: `tests/p3_v3/test_cli.py`

**Interfaces:**
- Consumes: exact frozen workload, adapter discovery, source root, build descriptor, `JSON_SCHEMA_DRAFT2020_12_V1.generate`。
- Produces: `run_python_workload(...) -> dict[str, object]`，receipt schema 仍为现有 `p3-profiling-results-v1`；CLI subcommand `run-python-workload`。

- [ ] **Step 1: 写 RED tests 固定四个必要行为**

测试必须证明：

1. exactly 20 frozen rows，顺序与 behavior ID 不变；
2. trace 中任何受控 subject module 都位于 source root，installed/system NumPy fallback 变为 `FAILURE`；
3. exit-0 且无 subject call 为 `MISSING_TRACE/NO_SUBJECT_CALL_TRACE`；
4. timeout、nonzero、underspecified entrypoint 分别保留真实终态，不触发 retry。

Run:

```bash
rtk env PYTHONPATH=src .venv/bin/python -m pytest tests/p3_v3/test_python_profiling_runner.py tests/p3_v3/test_cli.py -k 'python_workload' -q
```

Expected RED: 缺少新 runner/CLI，而不是旧测试失败。

- [ ] **Step 2: 实现最小 runner，不改变分类器**

实现边界：

```python
def run_python_workload(
    *,
    workload_path: Path,
    adapter_discovery_path: Path,
    descriptor_path: Path,
    source_root: Path,
    runtime_root: Path,
    receipt_path: Path,
    python_executable: str,
) -> dict[str, object]:
    ...
```

call trace event 复用现有 receipt event schema；不得在 runner 中直接写 `ARRAY_NUMERICAL` 或其它 technique tag，分类仍完全由 `classify_technique` 从 observed trace 派生。

- [ ] **Step 3: 运行 GREEN 与 containment 负控**

Run:

```bash
rtk env PYTHONPATH=src .venv/bin/python -m pytest tests/p3_v3/test_python_profiling_runner.py tests/p3_v3/test_cli.py -k 'python_workload' -q
```

Expected: PASS，包括 installed NumPy fallback 负控。

- [ ] **Step 4: 回归 35 份既有 Phase-1 receipts 和 Boost.Math formal receipt**

只验证 `classify_technique` 仍接受原工件；不得重跑 Boost.Math。

Expected: 35 份历史 receipt 全部接受；Boost.Math reconstruction 仍是 `TECH_UNCERTAIN`、8/12 funnel。

- [ ] **Step 5: focused verification**

Run:

```bash
rtk git diff --check
```

不跑全量套件。通过后提交最小实现，正式运行仍需单独授权。

**Checkpoint summary:** 实现完成不计科学进度；只有 Task 6 receipt 才计。

---

### Task 6: 一次正式 NumPy profiling，禁止重试

**Files:**
- Create: `data/p3_v3/profiling_runs/numpy/profiling-results-4e7e9556b3d621681c88c82f26cd95f5604d7a8b85cc56bf7e6d4db5a274f38b.json`
- Preserve: runtime logs under `/tmp/p3-numpy-formal-profiling-v1`
- No code changes during run.

**Interfaces:**
- Consumes: reviewed implementation commit、Task 3 source identity PASS、Task 4 executability PASS、一次性用户授权。
- Produces: one immutable receipt and one of `FORMAL_PROFILE_VALID` / `FORMAL_PROFILE_INVALID` / `INFRASTRUCTURE_TERMINAL`。

- [ ] **Step 1: preflight 只核验，不修正**

核验 HEAD、reviewed blobs、source/archive/tree、20-row workload、runtime root 不存在、receipt path 不存在、controlled Python path。任何失败停止，不现场修复。

- [ ] **Step 2: 请求一次性授权**

授权必须绑定 implementation commit、verdict、snapshot ID、source/tree/descriptor hashes、runtime root、receipt path，并逐字包含 `P3_FORMAL_PYTHON_PROFILING_AUTHORIZED=true` 和 `RETRY_FORBIDDEN=true`。

- [ ] **Step 3: CLI 只调用一次**

CLI 具体 argv 由 Task 5 的 reviewed interface 固定。执行者记录开始/结束时间、退出码、stdout/stderr 和 receipt SHA；不得第二次调用。

- [ ] **Step 4: 使用现有 validator 和 `classify_technique` 验收**

必须报告 20 行 status/failure-code funnel、successful_count、unresolved_count、confirmed tags、primary technique 和每行 trace containment。

- [ ] **Step 5: 保留所有终态**

0 个 successful trace、20 个 failure 或 `TECH_UNCERTAIN` 都是有效科学结果；不得事后重归因给 harness，除非 Task 4 的预注册边界本身被真实证据证伪，此时也只记录 limitation，不重跑。

**Checkpoint summary:** 这是本计划唯一新的科学运行。

---

### Task 7: Claim-impact 判定与下一科学转场

**Files:**
- Create: `data/p3_v3/profiling_runs/numpy/rq-evidence-handoff-4e7e9556b3d621681c88c82f26cd95f5604d7a8b85cc56bf7e6d4db5a274f38b.json`
- Create: `docs/review_20260827/p3_numpy_formal_profiling_claim_impact.md`
- Modify only after independent scientific review: `research/evidence/p3_claim_ledger_v1.3.0.yml`

**Interfaces:**
- Consumes: Task 1 eligibility terminal、Task 6 receipt、现有 claim ledger。
- Produces: `CLAIM_PROGRESS_ADVANCED`、`BOUNDARY_EVIDENCE_ONLY` 或 `EVIDENCE_INVALID`。

- [ ] **Step 1: 重建分类，不运行 subject**

从 frozen workload + receipt 调用现有 `classify_technique`。重建结果必须与 receipt handoff 一致。

- [ ] **Step 2: 按证据门分类主张**

```text
observed: 20-row execution funnel and exact trace observations
qualified: technique interpretation limited to this frozen workload/version
blocked: NumPy generally uses/does not use a technique; C2 fully supported
speculative: other Python subjects will behave similarly
```

- [ ] **Step 3: 只在满足明确条件时改变 ledger**

- 若至少一行成功、subject-contained trace 使 `confirmed_tags` 非空：记录 C2/RQ1 的 profiling prerequisite 从 `0 confirmed subjects` 变为 `1 confirmed subject`；C2 仍 `blocked`，下一任务是同一 subject 的最小 construction/certification slice。
- 若 receipt 有效但仍 `TECH_UNCERTAIN`：不重复 profiling；记录 `BOUNDARY_EVIDENCE_ONLY`，先判断失败是 Python runner 通用边界还是冻结 workload 信息不足，再决定是否停止 technique-stratified C2 wording。
- 若 evidence invalid：只记录 invalid 原因，不修改 claim ledger。

不得因为单 subject 成功直接把 C2 改为 `supported`。C2 的最终门槛仍包括 75 confirmed non-equivalent semantic mutants、至少 15 subjects、至少 8 repositories、规模和 technique diversity。

- [ ] **Step 4: 独立 `sol/high` 科学复核后才提交 ledger 修改**

复核只判断 evidence-to-claim strength，不追加 implementation review、全量测试或新 gate。

- [ ] **Step 5: 输出唯一下一任务**

终态分支：

```text
confirmed_tags nonempty -> PLAN_ONE_SUBJECT_CONSTRUCTION_CERTIFICATION
valid TECH_UNCERTAIN     -> REVIEW_PROFILING_INFORMATION_BOUNDARY
invalid evidence         -> STOP_AND_PRESERVE
```

---

## Scientific progress dashboard

| Checkpoint | 能改变什么 | 最长投入边界 | 失败后动作 |
|---|---|---|---|
| Task 1 | 主 RQ4 cohort eligibility | 约 1 小时 | 降级为 case series，停止 RQ4 infrastructure |
| Task 3 | RQ1 source availability | 外部交付半天级 | 保留外部缺失终态，不换 subject |
| Task 4 | frozen workload 是否真实可执行 | 半天 | 不写 runner，记录 specification boundary |
| Task 5 | 运行能力，不计科学进度 | 1 个工作日内 | 停止，不扩成通用框架 |
| Task 6 | 第一份非 Boost formal profile | 一次运行 | 保留终态，禁止重试 |
| Task 7 | C2 prerequisite / claim ledger | 约 1 小时 | 保持 blocked，明确下一最小实验 |

## Completion criterion

本计划在以下两项都完成时结束：

1. 主 RQ4 在冻结 P12 release 下得到正式 `RQ4_CONFIRMATORY_INELIGIBLE_FROZEN_RELEASE`，并停止 confirmatory RQ4 工程投入；
2. NumPy candidate 得到一个不可重试终态：正式 receipt、`WORKLOAD_EXECUTION_UNDERSPECIFIED`、`SOURCE_UNAVAILABLE` 或 `SOURCE_IDENTITY_FAIL`。

成功不定义为“得到 confirmed tag”。成功定义为：在冻结输入上取得能改变下一项研究决策的真实数据，并在其后立即停止无收益工作。
