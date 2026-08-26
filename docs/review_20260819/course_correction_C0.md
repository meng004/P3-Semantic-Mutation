# Course correction C0 — 2026-08-19

- Reviewer role: 评审模型（流程总控 + 纠偏）；本会话不改生产代码
- Governing init: `docs/task-instructions/2026-08-19-dual-agent-init.md` §1 / §3 / §R
  （当前仅在 `origin/cursor/dual-agent-init-58d6` @ `fc805f33` / PR #20；`main` 尚未收录。流程权威仍按该文，不因此另开基础设施包。）
- Reviewer run: `bc-b2c50c7c-5f96-4fac-86df-5864c15fa558`
- Baseline inspected: `main` @ `4444061dde0159a5edd62753fe3cef2d881a308c`
- Current phase: Phase 2
- Closed P2 targets: （无）
- Open P2 targets: P2-A, P2-B, P2-C, P2-D, P2-E, P2-F
- Last packet scientific yield: 基础设施
- Verdict: REDIRECT
- Next scientific_target: P2-A
- Explicitly not next: Authority Lock 加厚；新资格认证 runner / attempt-2；Boost.Math 授权链；compiler-alias / path-scan CI 计划；standards remediation；launch-packet / 自哈希协议；P2-B 及之后子准则
- Validity vs overdefense: 效度修复（把无 RQ 贡献的资格认证/授权链停掉，回到 §14 第一条未关闭子准则）。不是主张收缩：claim 天花板保持 `blocked`，不改预注册。
- Author decision needed: no

---

## 1. 对照 §14：当前相位与未关闭子准则

科学计划
`docs/superpowers/plans/2026-08-08-p3-semantic-mutant-argumentation-experiment.md`
（文件 SHA-256 `fea00496801c31ba074aa74742f5e6a77019ffc2e344642122a15462d7443830`）
§14 的执行序是 Phase 0 → 1 → 2 → …。回归宪章
`docs/superpowers/plans/2026-08-12-p3-return-to-scientific-critical-path.md`
（文件 SHA-256 `bd9234e3a26557e0036e42415528f983f2c18313295352ddffb4ccc076c1d5e4`）
已把 Phase 0 / Phase 1 标为关闭。

| 科学相位 | 仓库状态 | 依据 |
|---|---|---|
| Phase 0 协议冻结 | 已关闭（Protocol V4） | `data/p3_v3/protocol/protocol.json` 文件 SHA-256 `240d8270d41802c9d5b86f30564eadd1a86fd9ed09de2c7e947d17c1a4d78519` |
| Phase 1 盲化桥 + frames | `PHASE1_CLOSED` | `docs/review_20260815/phase1_sol_high_final_review.md` verdict `PASS`；receipts 文件 SHA-256 `8eeccfe4d1aebb09e6ee9ad2fadb82ac5b8697c40f602592faa6b3878692a440`；实际漏斗 3/9/23；claims 仍 `blocked` |
| Phase 2 | **未开始** | Phase 1 终审明确：关闭不授权 preflight / pilot / profiling / Package A / Package C / P12 揭盲 |

Phase 2 退出准则拆成 P2-A…P2-F 后，**全部未关闭**：

| 编号 | 子准则 | 状态 |
|---|---|---|
| P2-A | 对已准入受试做 capability / dependency / build / smoke / ledger / runner preflight | 未关闭。仓库只有测试夹具与 Boost.Math 旁路 `pilot.py build-preflight`，没有 CONSTRUCTION_A 生产 preflight 收据 |
| P2-B | `PILOT_ONLY` 受试上演练流水线每个终端态 | 未关闭。Boost.Math 线把“一个受试准备”拆成多层裁决，未按退出准则入账 |
| P2-C | 执行已冻结 Profiling Workload | 未关闭。35 个受试 `primary_technique=TECH_UNCERTAIN`，profiling 未执行 |
| P2-D | 类别均衡 `L_t`/`U_t` 与主技术 | 未关闭（依赖 P2-C） |
| P2-E | `C_CONSTRUCT` / `C_CRITERION` 与槽位冻结 | 未关闭。Phase 1 slot-closure = 0 |
| P2-F | Package A 冻结 | 未关闭 |

声明权威
`research/p3-semantic-mutation-core-claims-rqs-v1.3.0.md`
（文件 SHA-256 `684ba68d21f6284375acf589069b7a9a611cf352f117b8ebacc6ef3a0f79d0c6`）
本轮不得升级任何 `blocked` 声明。

---

## 2. 最近完成工作的一句话判定

按 init §3.1：每项只标 `科学产物` / `效度修复` / `基础设施`。

| 工作 | 位置 | 判定 | 理由 |
|---|---|---|---|
| Phase 0 协议 V4 | 已在 `main` | 科学产物 | 关闭 Phase 0 退出准则 |
| Task 2 规则引擎 / Task 4 适配器 / Phase 1 frames | 已在 `main`；frames @ `54a72576` | 科学产物 | 关闭 Phase 1 退出准则；漏斗诚实保留 9+3 失败行 |
| Authority Lock（PR #14, `bdf6a7cb`） | 冻结，禁止 round-6 | 基础设施（已冻结） | 复盘 `docs/review_20260812/authority_lock_r5_retrospective_root_cause_and_goal_alignment_review.md`（SHA-256 `d10db98190def3e52e32f101bc53bf49dbb67e2346c97d934af22b0b56e44a57`）：约 19.7 h，RQ 证据为零 |
| Boost.Math source preparation | `data/p3_v3/pilot/boost_math/` + `docs/review_20260817/` | 基础设施 | 把 `PILOT_ONLY` 准备拆成 plan / capability / Authorization A / launch packet，未关闭任一 P2-* |
| Boost.Math build-preflight attempt-1 | `7b653cb6` 及授权归档 | 基础设施 | 记录的是编译器/libstdc++ 环境失败，不是 Phase 2 退出证据 |
| C++ link qualification | PR #15 合入 `4444061d` | 基础设施 | init §1.1 / §5：已完成的环境探测；**不是** Phase 2 退出准则 |
| Standards remediation 设计 | PR #16 未合入 | 基础设施 | 治理规格，零条 P2 子准则 |
| compiler-alias / path-scan CI 计划 | PR #18 / #19 / #17 未合入 | 基础设施 | CI 仪式，不服务 P2-A |
| 双角色初始化正文 | PR #20 @ `fc805f33` | 基础设施（会话流程，允许存在） | 只定义角色；本身不关闭 P2-* |

`main` 上最近两个**已完成**任务（Boost.Math build-preflight 记录 → C++ qualification）都是基础设施，且 P2-A…P2-F 无新关闭项。按 init §3.1 第 3 条：**强制 `REDIRECT`**。

---

## 3. 为何下一包是 P2-A，而不是 P2-B

init §1.2 菜单按序，禁止跳项发明新治理层。§5 默认剧本要求在 P2-A 与 P2-B 中选更薄的一个。

| 选项 | 现成工具 | 厚度 | 复发风险 |
|---|---|---|---|
| **P2-A** | 已有 `scripts/p3_v3/evidence.py run-preflight` + `src/p3_v3/preflight.py`（`p3-preflight-v1`）；不需要新模块 | 对 **1** 个已准入 `EXECUTABLE` 受试绑定 Phase 1 冻结输入，跑 capability / dependency / smoke / protocol-ledger，写一条终端态收据 | 低：命令已存在 |
| P2-B | `scripts/p3_v3/pilot.py` 现绑 Boost.Math 旁路；终端态演练已被拆成资格认证链 | 若继续 Boost.Math，几乎必然再加 Authorization / attempt-2 | 高：正是 2026-08-15 之后的失败模式 |

选定 **P2-A**，因为：

1. 它是第一条未关闭子准则，跳到 P2-B 即跳项。
2. 它能 100% 复用已冻结 CLI，不必新 runner、新授权、新 schema 代数。
3. P2-B 的现成路径已被资格认证链污染；C0 默认假设禁止再派该线。

受试选择（只点名中性 ID，不揭盲）：

- `neutral_snapshot_id` = `1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72`
- Phase 1 receipts：`CMAKE_CTEST_V1` / `EXECUTABLE` / scale `L` / `TECH_UNCERTAIN`
- 冻结 Profiling Workload 文件 SHA-256 `db46368cc3a8e78ffeceb60c38d46cd903ac49ddc779757ee94f1350bd15382d`
- 选择规则：receipts 数组中第一条 `discovery_status=EXECUTABLE` 的受试（稳定、可复算）。**不是** Boost.Math pilot 对象。

P2-A 在本包的诚实范围：现有 `run-preflight` 已经覆盖 capability（CPU/内存/磁盘/atomic replace/file lock）、dependency lock、smoke。`build` / `runner` / `ledger` **不**通过新探针类型实现，只允许把已有 `validate-protocol` 放进 `smoke_commands`。对本受试做 CMake/编译/链接 = 新资格认证，禁止。诚实失败（preflight `FAIL`）保留在收据里，不进 confirmatory 分母。

---

## 4. 本轮明确不做

至少包括以下项（命中 init §3.4 即时触发器则停线）：

- Authority Lock / verifier / 敌手自证威胁模型加厚（冻结于 `bdf6a7cb`）
- 新的资格认证 runner、compiler-alias、`qualify_cxx_link` 执行、attempt-2
- Boost.Math Authorization / launch-packet / source-prep 加厚
- 通用 schema 代数、claim-state 框架、编排层、launch-packet 自哈希（科学计划 §18）
- Protocol V5、Package A/C、profiling 执行（P2-C）、槽位关闭（P2-E）
- claim 升级、P12 揭盲、把 preflight/pilot 行写入 confirmatory 分母
- 只增加审计台账格式而无科学收据

---

## 5. §R3 科学问题（C0 必须先回答）

1. 本包声称关闭哪一条？**下一包目标 = P2-A**。C0 本身不关闭它；证据路径将是 `data/p3_v3/phase2_preflight/preflight-result.json` 的 `artifact_sha256`（执行后回填）。
2. C0 自身是 **效度修复**：纠正“资格认证代替 Phase 2”的过程偏离。
3. 更薄替代：直接调用已有 `run-preflight`，不要新模块。
4. 未把失败行 / `TECH_UNCERTAIN` / 超时从 Phase 1 分母修没。35 个 `TECH_UNCERTAIN` 保持原状。
5. C0 未读 kill、评价用 MR、Package C、P12 真实缺陷结果。
6. CLAUDE.md §10.1：本轮没有降级可证伪主张。处置是停止零贡献基础设施，不是把 H/RQ 改成描述性。
7. **纠偏裁决：`REDIRECT`**

---

## 6. 最近相关 PR / 计划（C0 用，不发明新口径）

| PR / 计划 | 状态 | C0 用法 |
|---|---|---|
| #15 C++ compile-link qualification | 已合入 `4444061d` | 承认完成；停止该线 |
| #16 standards remediation | 开放 | 不合并进下一科学包 |
| #17 supplemental path-scan CI | 开放 | 不合并进下一科学包 |
| #18 / #19 compiler-alias CI | 开放 | 不合并进下一科学包 |
| #20 dual-agent init | 开放 | 流程宪章来源；不代替 P2-A 收据 |

---

## 7. §10.1 过度防御审计

| 处置 | 分类 | 辩护 |
|---|---|---|
| 停止 qualification / Boost.Math 授权链 | 效度修复 | 保护“机制必须服务命名科学性质”（科学计划 §2.1）；该线不保护 construct validity / blindness / 分母诚实 |
| 不把 P2-A 做成六探针新框架 | 反过度防御 | 复用已有 preflight；缺的 build 编译探针记 backlog，不新写 toolchain |
| 不跳到 P2-B/P2-C | 效度修复 | 菜单按序；profiling 仍 outcome-blind 未执行 |
| claims 保持 `blocked` | 既有天花板 | 不是本轮收缩 |

主张收缩清单：空。无需回调。

---

## Reviewer 2 视角的最严苛审稿意见

- [外部效度] 选 1 个 `EXECUTABLE` 受试做 preflight，不能外推到 35 受试或工业 C++ 工具链。下一包验收必须写明“单受试终端态”，禁止把收据写成 Phase 2 已关闭。
- [方法论] 现有 `run-preflight` 没有独立 build job。若执行方把 CMake 塞进 smoke，会把 P2-A 偷换成 qualification。验收清单必须禁止 `c++` / `cmake` / `qualify_cxx_link` / Boost.Math 路径。
- [统计选择] 不得把 preflight `FAIL` 改写成可进正式分母的成功。
- [霍桑] 看过 Boost.Math attempt-1 失败的会话不得回头改 Phase 1 漏斗或协议。
- [基准] 本包不触及语法基线；无基准不公。

非致命、已写入验收清单。无 publication blocker 需要改冻结科学口径。

Reviewer 2 视角扫描通过——5 类维度均无 publication blocker。

---

## 8. 下一动作

只签发一份最小执行包：`docs/review_20260819/execution_packet_2026-08-19-001.md`（`scientific_target: P2-A`）。
Cursor VM 完成前，评审模型不签发第二包，不启动 P2-B。
