# P3 项目状态（单一会话入口）

> 每次会话开始**只读这一个文件**即可定位。任何重大 commit 后请同步本文件 + 末尾 `last_synced` 日期。
>
> P2 时代的状态文件已归档至 `archive/process_summaries/P2_STATE_2026-05-03.md`，不再作为入口。

**Last synced:** 2026-09-07
**Stage:** **理论重构期（v4 立项）** — 无可投稿件；旧稿件线全部冻结
**当前论文身份:** v4 = ESPR / SPTM / SLRMA，目标 ACM TOSEM
**方案文档:** `research/p3-equation-structure-preservation-mr-adequacy-plan-v4-zh.md`
**Claim 权威:** `research/evidence/p3_claim_ledger_v1.3.0.yml`（冻结于 2026-08-12，C1–C8 **全部 `blocked`**）

---

## 0. 一句话现状

三份 2026-08-29 的独立评估一致认定现有稿件存在 claim–evidence 缺口：实证证据只到「单项目 4 配对 pilot」，而论文主张需要跨项目构念效度。2026-09-07 决策：**放弃在旧证据上重写主张，改走 v4 理论重构路线**，旧 60-cell 数据降级为 development/pilot set。

---

## 1. 三条稿件线的处置

| 线 | 位置 | 核心内容 | 2026-09-07 处置 |
|---|---|---|---|
| **A. SMS / 12-PUT / 60-cell** | `source/main.tex`（2978 行，7-29）+ `submission/TOSEM_regular_20260729_m1m8/` | 5.14% AST 重叠、δ=0.314、bootstrap CI [0.045, 0.594] | **冻结**。数据可复用为 development set，稿件不再推进 |
| **B. Evidence-aligned v0.1** | 分支 `codex/p3-evidence-aligned-manuscript-v0.1`，316 行 md | 1 NumPy subject / 4 pair / semantic 4-4 kill / syntactic 3-4 / exact overlap 0-4 | **已由其自身审阅关闭**（`P3_C3_CLAIM_SCOPE_PATH_CLOSED=true`） |
| **C. v4 ESPR/SPTM/SLRMA** | `research/p3-equation-structure-preservation-mr-adequacy-plan-v4-zh.md` | 评价对象改为「MR 集合对方程保结构要求谱系的覆盖能力」 | **当前唯一活跃路线** |

线 A 的投稿包（`main.pdf` / `supplementary.pdf` / `main.tex`）此前一直是未跟踪文件，2026-09-07 已入库保存，仅作历史 lineage 凭证。

## 2. v4 方案要点

三个核心构念：

- **ESPR**（Equation-Derived Structure-Preservation Requirement）：\(r=(\phi,D,\kappa,B,O)\)，方程蕴含的守恒/对称/单调/伴随/可逆/收敛性质 + 适用域 + 保持方式 + 误差预算 + 独立观测方法。
- **SPTM**（Structure-Preservation-Targeted Mutation）：以 ESPR 为目标的语义变异 \(\mu_{r,\theta}\)；认证**不得**使用 MR 判定器或 kill 结果。
- **SLRMA**（Structure-Lineage-Relative MR Adequacy）：\(A_G(R)=\frac{1}{|G|}\sum_{g\in G}\frac{|K_R\cap M_g^{neq}|}{|M_g^{neq}|}\)，谱系宏平均。

三个 RQ：RQ1 构念效度（ESPR 能否操作化为可认证 SPTM，且比预算匹配的 FOM/HOM 更集中产生预声明结构偏离）；RQ2 判别效度（SLRMA 能否恢复完整/删族/弱化/冗余/错配 MR 集合的预注册质量偏序）；RQ3 准则效度（能否解释独立真实缺陷的 MR 检出，并提供超出句法分数、MR 数量与执行成本的增量信息）。

**RQ2 是决定性实验。**

方案谱系（均为 2026-08-29 产出，按时间序）：
`p3-vnext-background-rqs-hypotheses-method-zh.md` → `p3-vnext-structured-theory-research-plan-v2-zh.md` → `p3-structure-survival-mr-adequacy-plan-v3-zh.md` → `p3-equation-structure-preservation-mr-adequacy-plan-v4-zh.md` → `p3-tosem-editorial-assessment-v4-zh.md`（编辑视角评估）。

## 3. v4 的四个开口问题（进入实现前必须先关闭）

编辑评估（`research/p3-tosem-editorial-assessment-v4-zh.md`）列出的阻塞：

1. **结构谱系尚未真正建立** — 节点是什么、派生关系是什么、多标签如何计分、NA/合法离散破缺/等价未决如何影响分母、为何宏平均。若只是把五类算子改名，审稿人仍会判定为经验分类。
2. **独立认证必须可执行** — 至少需要守恒（源—汇—边界平衡）、对称（离散算子交换子）、伴随（双线性恒等式）、可逆（往返残差）、收敛（独立网格序列与误差阶）等正交认证器。现有 E1/E2 只检查运行一致性与采样等价，不足以认证结构偏离。
3. **必须新增确认性实验** — 旧对象为开发集，新方程 + 独立求解器为冻结确认集；统计单位是程序/求解器，不是变异体或输入。
4. **现稿需显著删减** — LLM 来源效应、Pattern Coverage 相关性、部署/标准/air-gap 讨论、次级 Friedman 分析、退化定理作为主创新的叙述，全部移出主线。

## 4. 已终态的实验事实（不得重跑或改写）

- **Boost.Math formal profiling**：终态 `TECH_UNCERTAIN`，8/12 funnel，`FORMAL_PROFILING_RETRY_FORBIDDEN=true`。
- **Boost.Math Attempt-2 recovery**：停在约 70%，`attempt_2_authorized=false`。v4 路线下**不再推进**；交接说明见 `docs/superpowers/notes/2026-08-25-p3-attempt2-next-session-initialization.md`。
- **Ordinal-8 NumPy pilot**：1 项目 / 2 site / 4 pair / 每 pair 5 冻结输入 / 60 正式 cell 全 PASS；semantic 4/4 KILL，syntactic 3/4 KILL + 1/4 SURVIVE；规范化补丁与变异树精确重叠均 0/4。exact binomial 区间为 `UNMEASURED_INTERVAL_AUTHORITY_INCOMPLETE`（冻结分析规范未固定置信水平与方法，事后不得补算）。
- **Stage I 适用性普查**：14 个后继 subject、140 个 closure，0 个 `SITE_FROZEN`，140 个 `APPLICABILITY_CLOSED_NOT_APPLICABLE`，Stage II 候选为 0。这是冻结权威下的资格结论，**不是**「这些程序不存在目标构造」。
- **RQ4 / P12**：冻结 release 只有 35 个 formal item，低于预注册的 60 个 `P12_PAIRED` 门槛，机械上不可满足。**注意：正式的 ineligibility 终态文档从未落地**（`docs/superpowers/plans/2026-08-27-p3-shortest-scientific-evidence-path.md` 的 Task 1 未执行），RQ4 目前仍挂在「待核实」而非「已判定不合格」。若 v4 需要引用 RQ4 状态，须先补这份一页决策。

## 5. Claim ledger 状态

`research/evidence/p3_claim_ledger_v1.3.0.yml`，冻结于 2026-08-12，`status: frozen-execution-ceiling`：

| Claim | 主张 | 状态 |
|---|---|---|
| C1 | artifact-first 语义变异协议 | `blocked`（尽管 `governing_initial_status: supported`）|
| C2 | 跨规模跨技术的已认证变异体 | `blocked` |
| C3 | 语义变异与句法基线构念可区分 | `blocked`（`n_projects=1`，项目聚类不确定性不可识别）|
| C4 | family-aware SMS 解释 MR 集合残差 | `blocked` |
| C5 | 语义充分性在 P12 上有增量价值 | `blocked` |
| C6 / C7 / C8 | 普遍优越性 / 语言无关自动生成 / profiling 代表性 | **永久 `blocked`** |

v4 会引入新的构念（ESPR/SPTM/SLRMA），需要一份新的 claim ledger（v2.0.0），而不是在 v1.3.0 上改状态。

## 6. 期刊定位

`docs/review_20260829/P3_journal_fit_and_acceptance_assessment_zh.md` 的主观接收概率估计（非期刊公布数据）：

| 期刊 | 现稿直投 | 完成跨项目效度验证后 |
|---|---|---|
| ACM TOSEM | < 5% | 15%–25% |
| IEEE TSE | < 3% | 10%–20% |
| EMSE | 3%–8% | 15%–30% |
| IST / JSS | 5%–12% | 25%–40% |

目标：TOSEM。分区口径存在版本差异（2025 中科院升级版为大类 1 区；2026 新锐分区为大类 2 区），投稿前须确认单位采用哪一版。

## 7. 下一步

按依赖顺序：

1. **建立结构谱系 \(G\)** — 关闭 §3 问题 1。这是 SLRMA 分母的定义，先于任何实现。
2. **设计正交认证器** — 关闭 §3 问题 2。至少 3 个可执行认证器（建议先做守恒、对称、可逆）。
3. **选定确认集** — 新方程 + 独立求解器，outcome-blind 选择规则须在任何运行前写死。
4. **预注册 RQ2 的 MR 质量梯度** — 完整/删族/弱化/冗余/错配五档，偏序在数据收集前固定。
5. **新建 claim ledger v2.0.0** — 承载 ESPR/SPTM/SLRMA 的主张与上限。

步骤 1–2 属理论工作，无需实验授权。步骤 3 起须走 `superpowers:writing-plans` 出阶段化计划。

## 8. 仓库卫生

- 本地 `main` 落后 `origin/main` 2 个 commit（`.cursor/install.sh` 自包含环境），**尚未同步**。下次会话可 `git merge --ff-only origin/main`。
- 2026-09-07 已将 52 个未跟踪文件入库：v4 方案谱系（research/ 5 份）、8 月评审文档（docs/review_2026080{6,7,8}、docs/review_20260829 共 8 份）、19 份 superpowers 计划与规格、TOSEM 投稿包（14 项）、P12 staging zip（2 项）。`.codegraph/` 已加入 `.gitignore`。工作区当前 0 个未跟踪文件。
- `artifacts/*.zip`（P12 staging，合计 1.5 MB）与 `submission/TOSEM_regular_20260729_m1m8_clean.zip`（1.8 MB）体积在 §9.4 的 commit 阈值内。
