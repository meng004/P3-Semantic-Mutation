# P3 项目状态（单一会话入口）

> 每次会话开始**只读这一个文件**即可定位。任何重大 commit 后请同步本文件 + 末尾 `last_synced` 日期。
>
> P2 时代的状态文件已归档至 `archive/process_summaries/P2_STATE_2026-05-03.md`，不再作为入口。

**Last synced:** 2026-09-25
**Stage:** **R-v4 确认性实验 NO-GO** — 理论定义保留；无可投稿件；旧稿件线全部冻结
**当前研究身份:** v4 = ESPR / SPTM / SLRMA；原定 ACM TOSEM 实证路线暂停
**方案文档:** `research/p3-equation-structure-preservation-mr-adequacy-plan-v4-zh.md`
**Claim 权威:** `research/evidence/p3_claim_ledger_v1.3.0.yml`（冻结于 2026-08-12，C1–C8 **全部 `blocked`**）

---

## 0. 一句话现状

三份 2026-08-29 的独立评估一致认定现有稿件存在 claim–evidence 缺口：实证证据只到「单项目 4 配对 pilot」，而论文主张需要跨项目构念效度。2026-09-07 改走 v4 理论重构路线；2026-09-25 的最小理论定义确认：E1–E7 尚缺，尤其缺至少两个不同程序的可执行语义要求与独立认证方法。**在现有硬约束下暂停 v4 确认性实验与结果写作**；旧 60-cell 数据和 PocketFFT 均为开发材料。

---

## 1. 三条稿件线的处置

| 线 | 位置 | 核心内容 | 2026-09-07 处置 |
|---|---|---|---|
| **A. SMS / 12-PUT / 60-cell** | `source/main.tex`（2978 行，7-29）+ `submission/TOSEM_regular_20260729_m1m8/` | 5.14% AST 重叠、δ=0.314、bootstrap CI [0.045, 0.594] | **冻结**。数据可复用为 development set，稿件不再推进 |
| **B. Evidence-aligned v0.1** | 分支 `codex/p3-evidence-aligned-manuscript-v0.1`，316 行 md | 1 NumPy subject / 4 pair / semantic 4-4 kill / syntactic 3-4 / exact overlap 0-4 | **已由其自身审阅关闭**（`P3_C3_CLAIM_SCOPE_PATH_CLOSED=true`） |
| **C. v4 ESPR/SPTM/SLRMA** | `research/p3-equation-structure-preservation-mr-adequacy-plan-v4-zh.md` | 评价对象改为「MR 集合对方程保结构要求谱系的覆盖能力」 | 理论定义保留；确认性实证路线暂停（§1.6） |

线 A 的投稿包（`main.pdf` / `supplementary.pdf` / `main.tex`）此前一直是未跟踪文件，2026-09-07 已入库保存，仅作历史 lineage 凭证。

### 1.1 v4 与已公开预印本的关系（2026-09-07 决策：supersede）

Phase 2 主题 C 的先例裁决为 **`DIRECT_PRIOR_ART`**：v4 计划的 SPTM 与 SLRMA 已被本组自己公开的 **arXiv:2605.17437 (SMS)** 占据——Conservation Erosion 与 Structural Injection 两个算子即保结构性质违反，SMS 本身即被定位为 domain-semantic MR 集合的充分性度量，12-PUT × 5-MP 设计已跑完，且「保结构变异在默认一阶语法配置下不可达」这一结论已发表。**arXiv:2606.08269 (Min-MR-Complete)** 另占据完备性/最小化理论层。

**决策：v4 定位为 arXiv:2605.17437 的后继版本（arXiv supersede），不作为独立新论文。** 因线 A 从未投出且该预印本已在 `declarations.md` 中声明，此路径不构成切香肠。

由此产生四条硬约束，进入写作前必须逐条落实：

1. **SPTM / SLRMA 不得作为 first-of-kind 构念引入**，须写成 SMS 的理论化重述并引用 arXiv:2605.17437。
2. ~~**新颖性只押在 ESPR 五元组 r = (φ, D, κ, B, O) 的 O 分量与 verdict-independence 上**~~ —— **本条已作废，见下方「约束 2 的撤回」。**
3. **必须守住与 arXiv:2606.08269 的边界。** 该篇是**独立**的公开论文；SLRMA 若重复其 layer-relative 完备性判据、Set-Cover 等价、贪心近似或 ILP，即构成真正的切香肠。v4 只能**引用**该理论层，不能重述。
4. **arXiv supersede 的操作时点**：v4 定稿后以新版本替换 2605.17437，而非另开新 arXiv 条目。注意 `submission/arxiv_metadata.md` 已记录该文 Comments 字段的历史遗留问题（曾误称投往 IST），supersede 时一并修正。

FINER 的 Novel 项据此从 4/5 二次下调至 **2/5**（容忍下限），综合 4.0/5。详细证据链见 `research/stage1_deep_research/phase1_rq_brief_provisional.md` §1.2。

### 1.2 约束 2 的撤回（2026-09-07，Phase 3 synthesis 指出的逻辑矛盾）

Phase 3 synthesis（`research/stage1_deep_research/phase3_gap_synthesis.md`）判定原约束 2 与约束 4 **互相矛盾**，该判定成立：

> 若 v4 **supersede** arXiv:2605.17437，则记录中只有**一篇**论文，不存在「对自己的增量」需要辩护，只存在**对外部文献的增量**。约束 2 把本组自己的预印本当成了针对自己的先例，因而放弃了 supersede 框架本来就赋予的 SMS 级贡献，并把全部新颖性负担转嫁给框架中最弱的分量。

补充事实支持这一撤回：arXiv 预印本**不是 archival publication**，`declarations.md` 已声明「The submission is not an extension of any prior archival publication」，TOSEM journal-first 的新颖性门槛本就是对已发表文献而非对自己预印本设定的。

按项目规则 §10.1 的判别速查表，原约束 2 属于「**主张收缩**」而非「效度修复」——它在没有证据要求的情况下预先放弃了理论敢做的主张，辩护不过，**予以回调**。

**修订后的约束 2：** v4 的新颖性对**外部文献**衡量。SPTM/SLRMA/SMS 层的内容属于本论文自身内容，可正常主张，无需引用自己的预印本作为先例（但 supersede 关系须在 arXiv 版本历史与投稿信中如实交代）。真正需要防守的外部先例是 Fu et al. (2024)、Liu et al. (2024)、Bartocci et al. (2023)、Yan & Zhu (2025)。

**约束 1、3、4 不受影响**，其中约束 3（与 arXiv:2606.08269 的边界）**仍然完全成立**——那是一篇未被 supersede 的独立公开论文。

### 1.3 Phase 3 判定的两个设计硬伤（进入实现前必须处理）

1. **O 分量的五个候选认证器中有两个本身就是 MR。** Round-trip residual 即可逆性 MR；grid-refinement order 即 Chen, Feng & Tse (2002) 推导的 refinement MR 族、也是 Roache GCI 所报告的量。两者都是「跨多次执行及其输出的关系」，正是 MR 的标准定义。更严重的是 v4 方案把**可逆性同时列为 ESPR 性质与其认证器**，构成循环。
2. **两个结构上干净的认证器（离散算子对易子、伴随点积检验）在现有程序总体上无法演示。** 前者需要暴露 div/grad/curl 算子，后者需要暴露伴随；而 arXiv:2605.17437 的总体是「four single-output float-to-float classes」，两者都不暴露。要演示 O 必须新建求解器总体。

### 1.4 新求解器总体不存在（2026-09-07，可行性普查结论）

对上条的直接回应：`research/stage1_deep_research/phase3b_put_population_feasibility.md` 的裁决是**满足全部五项硬要求的程序总体在研究所需规模上不存在**。

**约束的绑定点是 R1 ∩ R2**：暴露可检视离散算子（或真实伴随）的代码把这些算子放在 C++/Fortran/生成的 C 里；而 Python 可变异的代码几乎从不把这些算子作为可单独调用的对象暴露。R4（真实缺陷史）在该交点上构成次级绑定——只有 SimPEG 有可用的带标注缺陷语料。

| 候选 | 接近之处 | 硬性失败项 |
|---|---|---|
| `discretize` + SimPEG | 稀疏 `nodal_gradient` / `face_divergence` / `edge_curl`；文档已演示 `CURL@GRAD=0`；体积平衡；SimPEG 有 106 个 `bug` 标注 | **只是一个项目族，不是总体**；14% Cython |
| `findiff` | 纯 Python `Gradient`/`Divergence`/`Curl` + `.matrix()` | R4（仅 1 个标注缺陷） |
| `py-pde` | `grid.make_operator("divergence"\|"gradient"\|…)` | R4（4 个缺陷）；无 curl |
| `jax-cfd` | `finite_differences.{divergence,curl_2d,curl_3d}` + JAX VJP | R4（0 个标注缺陷） |
| Dedalus | 符号 `div`/`grad`/`curl` + PNAS 2026 自动伴随 | 运行时在 C kernel 内；生产级 IVP 不满足 R5 |

**关键警告**：把 `discretize` 内部的示例 PDE 当作「总体」来计数，会恢复 n 但重演已记录的 `n_projects=1` 聚类失败。Julia（`Oceananigans`）在 R1 下不值得考虑；若放宽 R1，Mull / Dextool / Gremlins.jl 存在，但那是更换测试框架而非廉价获得总体。

**后果**：去循环后仅存的两个干净认证器**没有可演示的载体**。第三个幸存者（全局平衡诊断）受 Haworth (1993) 限制——对格式按构造精确守恒的量，不平衡量恒为零，因此恰恰对主守恒 ESPR 失明，而 Conservation Erosion 正是 SMS 五算子之一。**O 分量在当前证据下不可作为承重贡献。**

### 1.5 放宽 R1 的路线（2026-09-07 用户选择，成本评估已完成）

用户选择**放宽 R1**：放弃 Python 变异框架，改用 C++ 变异工具（Mull / Dextool）对成熟 C++ 求解器（MFEM / DOLFINx / deal.II / PETSc）施加变异，以换取真实暴露的离散算子与伴随。

**必须先处理的冲突**：这条路线与 §4 记录的第一次成本失败**是同一条路线**——Boost.Math C++ 尝试终态 `TECH_UNCERTAIN`、8/12 funnel、`FORMAL_PROFILING_RETRY_FORBIDDEN=true`，Attempt-2 停在约 70% 且 `attempt_2_authorized=false`，两周投入**从未离开 build-preflight**。且新目标严格更重：Boost.Math 是 header-only、无外部依赖、无 MPI；MFEM / DOLFINx / PETSc 需要 MPI + BLAS/LAPACK + hypre/METIS。

**唯一可能使其不重演的技术差异**（待核实）：Mull 在 LLVM IR 层变异，将多个变异嵌入单个插桩二进制并在运行时切换，原理上绕开「每变异体重建原生构建链」——正是杀死 Boost.Math 的成本项。Dextool 为源码级变异，不具此性质。另需核实 FFC/TSFC 运行时生成 C 代码的求解器（FEniCS / Firedrake）中 Mull 能否看见算子代码。

成本评估交付物：`research/stage1_deep_research/phase3c_cxx_route_cost_assessment.md`。

#### 1.5.1 评估裁决（2026-09-07）：`PARTIALLY DIFFERENT`

**Mull 的技术假设成立，但它不是 Boost.Math 的死因。** Mull 0.34.0（2026-05-12）是 LLVM IR 层的 Clang plugin：编译一次生成单个插桩二进制，`mull-runner` 在运行时切换变异体；JIT 架构已于 2021-01 移除，2018 年的工具论文在架构描述上已过时。**确实绕开了每变异体重建**，但成本只是转移到一次 Clang/LLVM 版本锁定的首次编译上，而杀死 Boost.Math 的是「合同、证据、gate 的投入超过可执行链本身」这一流程失败，不是编译成本。Dextool 为源码级，但同样有 schemata 模式（带 rebuild 回退）。

**最佳候选：串行 MFEM**（`DiscreteLinearOperator` / `GradientInterpolator` / `CurlInterpolator` / `DivergenceInterpolator`），**不要碰 MPI**。Firedrake / FEniCS 是 Python 路线陷阱的镜像——TSFC / FFCx 运行时生成 C 代码，Mull 无法稳定看见。PETSc / 完整 FEniCSx / deal.II-candi 需 20+ 工程周，应直接拒绝。

**成本：到首次真实 profiling 需 8–15 工程周**（若可执行链是唯一工作则 5–8 周）。Boost.Math 已烧掉 2 周且完全未到达 profiling，本路线是其 4–8 倍。

**决定性事实（评估之外的推论）**：即便全额投入 8–15 周并成功，结果仍是 `n_projects=1`——这恰是 §5 claim ledger 中 C3 已被记录的阻塞原因（「`n_projects=1`，项目聚类不确定性不可识别」）。**这条路线用 4–8 倍于第一次失败的成本，落回同一个已记录的阻塞点。**

**§1.6 的战略裁决已作出：不启动该 C++ 工程路线。**

### 1.6 2026-09-25 路线裁决

**裁决：暂停现有 R-v4 的 TOSEM 确认性实证路线，保留 `research/p3-minimal-theory-v1-zh.md` 作为开发阶段的理论定义，不将其单独包装成已获实证支持的完整论文。** 这不是断言任何数学结构程序总体在客观上不存在，而是基于 §1.4 的既有普查和 §1.5 的成本评估，判定当前五项硬约束与所需项目规模没有可执行路径。

- 只放宽 R1（Python 工具链）并转向串行 MFEM，预计仍为 `n_projects=1`，不能解除跨项目阻断，故不启动 C++ 工程。
- 只放宽 R4（独立真实缺陷）可增加结构程序候选，却会使 RQ3 的准则效度证据缺位，不能维持原三项 RQ 的完整主张。
- 不放宽独立认证、参考 MR 排除或项目级统计单位；这些条件直接约束构念循环和伪重复。
- **另立候选路线**：较广语义范围已在 NetworkX / SymPy 两个独立项目上完成开发性认证演算；NetworkX 两臂区分，SymPy v1 修复后臂为 `EXEC_FAIL`，独立的 v2 数值读取修正后两臂区分（见 `experiments/dev/e1-broad-pair/VERDICT-v2.md`）。这两条公开缺陷只作开发材料。随后按每项目最近 30 条触及目标文件的提交筛查独立缺陷：NetworkX 纳入 0，SymPy 纳入 1、未决 2；这对程序的确认样本路线因此结束（见 `experiments/dev/e1-broad-pair/sample-source-receipt.md`）。该窗口结果不外推为仓库全史无候选。若形成新研究路线，须重新定义总体、分母和 RQ，不能沿用 R-v4 的确认性名义或把 PocketFFT 开发结果转正；仍非新论文已立项。

P12 当前中立快照的参考正控在 macOS arm64 双版本重建中失败，继续标为执行阻断；没有新发布或 P3 换锁。E1–E7 未齐备前不启动确认性评价，不复活 C1–C8。

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

原定目标为 TOSEM；2026-09-25 起该投稿路线暂停。分区口径存在版本差异（2025 中科院升级版为大类 1 区；2026 新锐分区为大类 2 区），若未来恢复投稿再确认单位采用哪一版。

## 7. 下一步

较广范围的 NetworkX / SymPy **开发载体已可执行**，但其指定的确认样本筛查在预定 30 提交窗口内未得到双项目候选，故该配对路线停止。不向更老提交补数，也不把 SymPy 单项目的 1 条候选转为跨项目证据。现有 R-v4 与较广范围的确认性评价均保持 NO-GO。2026-09-25 论文去向已定为停止 P3 新论文投入，见 `research/p3-paper-direction-decision-20260925-zh.md`。不再为不同程序总体开新的确认样本筛查，也不继续 v4 工程准备或预印本更新。

## 8. 仓库卫生（2026-09-07 历史记录）

- 本地 `main` 落后 `origin/main` 2 个 commit（`.cursor/install.sh` 自包含环境），**尚未同步**。下次会话可 `git merge --ff-only origin/main`。
- 2026-09-07 已将 52 个未跟踪文件入库：v4 方案谱系（research/ 5 份）、8 月评审文档（docs/review_2026080{6,7,8}、docs/review_20260829 共 8 份）、19 份 superpowers 计划与规格、TOSEM 投稿包（14 项）、P12 staging zip（2 项）。`.codegraph/` 已加入 `.gitignore`。工作区当前 0 个未跟踪文件。
- `artifacts/*.zip`（P12 staging，合计 1.5 MB）与 `submission/TOSEM_regular_20260729_m1m8_clean.zip`（1.8 MB）体积在 §9.4 的 commit 阈值内。
