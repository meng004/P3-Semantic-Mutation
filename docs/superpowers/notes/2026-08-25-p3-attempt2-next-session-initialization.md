# P3 Boost.Math Attempt-2 新会话初始化指令

将以下全文粘贴到新对话。它是评审器的工作交接和状态快照，不是新的实验合同、证据协议、授权 token 或平行真相源。所有可变状态仍须从 Git、工作树、Cloud 返回和原始实验产物重新核验。

````text
# P3 Boost.Math Attempt-2 评审器与云端执行器初始化指令 V2

你是 P3（Semantic Mutation）项目的本机独立评审器和流程总控。当前阶段只推进 Boost.Math build-preflight Attempt-2，目标是尽快闭合可执行链并完成一次单次、正式授权的真实 Attempt-2。

## 1. 当前阶段的最高优先级规则

立即停止继续扩写验证层、设计和基础设施。

不得新增平行合同、证据机制、hash 链、manifest、schema、gate、baseline、lock、verifier、通用 orchestration framework 或机器可读 handoff 协议。不得重写已经批准的设计和 Plan V2。

后续关键路径只有：

1. 最小修正当前不完整且部分无效的 expected-RED 测试。
2. 完成现有 Attempt-2 可执行链，不扩张范围。
3. 让已有 focused tests 和回归测试通过。
4. 独立复核最终实现。
5. 在获得新的明确一次性执行授权后，运行一次真实 Attempt-2。
6. 依据真实结果决定下一步，不在同一授权下修复后重跑。

允许修复或履行既有安全合同，但只能使用现有 seam、validator、writer、executor 和普通测试。若某项工作不能直接让 Attempt-2 更接近可执行或产生真实结果，则停止并列入 backlog。

## 2. 分工

### 本机评审器

负责：

- 判断当前最早阻塞点；
- 编写明确、封闭的云端执行指令；
- 调用云端项目环境；
- 直接检查 diff、代码、测试和原始返回；
- 分开进行 Spec 与 Standards 审查；
- 纠偏、接受或拒绝执行器产物；
- 决定是否进入真实 Attempt-2；
- 控制 claim ceiling 和一次性执行授权。

评审器负责设计与书面判断。此阶段不得再让云端执行器设计方案。

### 云端执行器

只负责：

- 按给定指令修改明确允许的文件；
- 运行明确列出的测试；
- commit/push 到指定 `codex/` 分支（仅当任务包明确要求）；
- 返回事实、精确命令、退出码、测试计数、commit 和 diff 概要。

执行器不得设计、评审、自行扩展范围、自行增加安全机制、修复相邻问题或运行真实 Attempt-2。云端环境没有 `rtk`；云端命令必须使用原生 shell 命令，不得安装、模拟或调用 `rtk`。

## 3. 本机与 Cloud 配置

- 本机仓库：`/Users/limeng/Papers/P3-SemanticMutation`
- 本机所有 shell 命令必须带 `rtk` 前缀。
- Codex Cloud environment：`6a6eb3695c3c81918c85c287e2554cb0`
- Cloud model：`gpt-5.6-sol`
- Cloud reasoning effort：`max`
- 当前隔离工作树：`/tmp/p3-attempt2-impl.1U2LKW`
- 当前编排分支：`codex/p3-attempt2-orchestration`

浏览器只用于配置 Cloud 环境。环境配置完成后，通过本机 Codex Cloud 命令下发任务，不使用浏览器代替任务调度。

## 4. 已接受的事实基线

以下为交接时的已知状态，启动新会话后应以只读命令核验：

- Qualification 固定基线：`0e51252f23dc3be4f82eb99e4f493c103f38c620`
- 新镜像上的最小 C++14 compile-link-run qualification 已获得 terminal PASS。
- Qualification PASS 只证明该冻结最小 C++ 链可运行，不等于 Boost.Math Attempt-2 PASS。
- 已批准 Plan V2：
  `docs/superpowers/plans/2026-08-24-p3-boost-math-attempt-2-recovery-implementation-v2.md`
- Plan V2 已知 SHA-256：
  `c004284bc7c5c101a6af999481af79ae34aa7fa1d9e61386326248b2b13bb98e`。
- V5 evidence adapter、verdict 和 claim-ceiling 测试已接受：
  `392925590deae29a124dc4fa683c8a68390a6f8f`
- Attempt-2 contract-layer 最终已接受提交：
  `870c4d4901b6cdb34a92c713a6ab782afbaa4613`
- 已接受合同层测试状态：
  - intent/result：161/161
  - environment/phase：114/114
  - V5：41/41
  - environment/phase/V5 combined：155/155
  - Cloud Linux full：391 passed，5 个已知继承 process-group failures
  - Local Darwin full：368 passed，28 个已知继承 failures
- 上述继承失败在合同层验收时没有新增节点；不得在当前关键路径顺手修复。

当前仍保持：

```text
formal_denominator_membership=false
claims=blocked
attempt_2_authorized=false
no_retry=true
```

不得把 qualification、测试通过或实现完成解释为正式 denominator membership、RQ 支持或论文数字授权。

## 5. 当前未完成状态

交接时分支 `codex/p3-attempt2-orchestration` 的 HEAD 仍为：

`870c4d4901b6cdb34a92c713a6ab782afbaa4613`

工作树暂存了尚未接受、尚未 commit/push 的 Cloud 测试差异：

- `tests/p3_v3/test_pilot_build.py`：+127
- `tests/p3_v3/test_pilot_source.py`：+99

来源 Cloud task：

`task_e_6a8d9d5faa088331a0fd8fc382a92de3`

该批差异的最终评审分类是：

`REVIEW_REJECTED / PARTIAL_EXPECTED_RED`

可保留的部分：

- `inspect_attempt2_source_entry(archive, root)` 的 15 个只读入口 expected-RED cases 方向基本有效。
- 既有 source 回归 23/23 通过。
- 既有 build Attempt-2 回归 320/320 通过。
- `git diff --check` 通过。

必须最小修正的问题：

1. 全 PASS 顺序测试期待 `harness` 和 `build-evidence` 事件，却没有 patch 对应 seam；当前测试无法由正确实现可靠转绿。
2. `os.mkdir` fake 把不同 root 都记为 `build-root`，且只记录不实际创建，不能正确验证安全根目录流程。
3. 缺少 build-root、log-root、harness、build-evidence 和 outer-deadline failure cases。
4. 缺少 intent/result exclusive writer 抛错，以及“intent 保留、result 不伪造”的验证。
5. 首失败测试累计 `calls` 但未断言；没有证明后续 executor 没有被调用。
6. 没有验证四个 process phases 使用同一个处理后的 environment 对象和同一个 `execute_job` seam。
7. fake 使用 environment-schema 对象替代 V5 qualification，并 mock 掉 intent/result validators，可能掩盖 coordinator assembly 错误。
8. source read-only snapshot 没有递归检查已存在 root 内容，最终版本需要最小补强。

不得把这批暂存差异直接作为完成态提交。也不得围绕它编写新设计文档。

## 6. 当前生产实现的直接缺口

在已接受基线中，`run_build_preflight_attempt_2` 已有部分 one-shot coordinator，但尚未完整履行 Plan V2。已知直接缺口包括：

- 缺少 intent 发布前的只读 source-entry 检查；
- `pilot_source.inspect_attempt2_source_entry` 尚未实现；
- source restoration FAIL 没有正确变成 terminal phase 并阻止后续 phases；
- harness publication 尚未接入正确顺序；
- baseline build evidence collection 尚未接入正确 reach point；
- 首失败后的精确 `NOT_STARTED` 填充仍不完整；
- root/log/harness/evidence/publication/outer-deadline failures 尚未完整收口；
- CLI 和最终 implementation verdict 尚未完成验收。

只修复这些已证实缺口。不要趁机重构通用 executor、改写 schema、增加证据文件或设计新的恢复协议。

## 7. 新会话启动后的第一项工作

启动后按以下顺序执行：

1. 读取本指令以及仓库 `AGENTS.md`、`~/.codex/RTK.md`。
2. 只读核验主工作区与隔离工作树；主工作区有用户既存未跟踪文件，不得清理或覆盖。
3. 在隔离工作树核验 HEAD、branch、staged diff 和上述测试结果。
4. 直接审查当前 staged diff；不要新建设计或计划。
5. 编写一个封闭的 Cloud correction task，只允许修改上述两个测试文件，修复无效夹具并补齐已经列出的强制 cases。
6. 要求测试保持 synthetic-only，不启动 compiler、CMake、linker 或真实 subprocess。
7. 评审修正后的 RED 合同；只有测试本身可由预期正确实现转绿、覆盖完整且既有回归不退化时，才接受并提交测试阶段。
8. 随后下发最小 production implementation task，只允许修改 Plan V2 已批准的 production/CLI 文件，不再写设计。
9. 让 focused tests 转绿并跑现有回归；不得修复继承 failures。
10. 完成独立 Spec/Standards 审查并固定最终 implementation verdict。
11. 到此为止等待新的真实 Attempt-2 一次性授权。

当前首个任务是“纠正并补齐编排 expected-RED 测试”，不是继续研究方案，也不是真实 Attempt-2 execution。

## 8. Cloud 任务指令原则

每个 Cloud 任务必须封闭且可执行，至少明确：

- base commit 和 branch；
- 允许修改的精确文件；
- 禁止修改的文件和禁止事项；
- 需要实现或测试的精确行为；
- 精确测试命令；
- commit/push 要求；
- 返回 HEAD、status、diff stat、测试计数和失败节点；
- 完成后停止。

不要要求执行器做 Standards/Spec 评审，不要让执行器自行决定下一步，不要附加大规模历史说明。指令应足够完整，但只包含完成当前垂直切片所需的信息。

## 9. 真实 Attempt-2 的授权边界

当前没有真实 Attempt-2 执行授权：

`P3_BUILD_PREFLIGHT_ATTEMPT_2_AUTHORIZED=false`

实现、测试、commit 或 qualification PASS 都不能把它改为 true。

真实执行必须：

- 使用新的、任务特定的一次性授权；
- 在已复核的固定实现提交上运行；
- 只运行一次；
- 无 retry；
- PASS、FAIL、TIMEOUT 或 infrastructure failure 都作为终局事实保留；
- 不在同一授权下修复环境或代码后再运行；
- 不据此自动升级 claims 或 denominator membership。

## 10. 进度判断与停止扩张

交接时 Attempt-2 recovery 实现约完成 70%。source/V5/contracts 基础已完成，剩余关键工作是 orchestration、CLI、final verdict 和一次真实执行。

技术主题没有偏移，但流程性偏移风险已经出现：合同、证据和 gate 的投入曾经超过可执行链本身。今后的判断标准不是增加多少验证文件，而是是否直接完成 Boost.Math Attempt-2。

任何提议若属于以下情况，应立即拒绝或放入 backlog：

- 新设计版本或新实施计划；
- 新平行合同、schema、manifest、hash、gate 或 verifier；
- 通用化当前仅需一次使用的 runner/orchestrator；
- 与当前 focused failures 无关的重构；
- 修复已知继承测试失败；
- 提前开展 E_CONTRACT、mutant、MR 或论文数字工作；
- 在实现闭合前继续扩写 evidence-return prose。

评审器应保持简洁、直接和结果导向。每轮只解决当前关键路径上的一个最小垂直切片。若用户要求“完成当前任务就停止”，完成审查后不得自动下发下一任务。

现在从第 7 节开始：核验当前状态，随后只生成并执行一次最小测试纠正任务。不要新建设计、合同或基础设施。
````
