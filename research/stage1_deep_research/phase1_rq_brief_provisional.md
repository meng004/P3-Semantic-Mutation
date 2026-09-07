# Phase 1a — Research Question Brief（临时版）

> **状态：PROVISIONAL。** 按用户指定的论证路线（问题→现状→不足→RQ），本文件在 Phase 2 文献检索与 Phase 3 gap analysis 之前产出，作用是给检索提供锚点。Phase 3 完成后必须复冻为正式版；届时 Novel 项评分与 Primary RQ 措辞可能改变。
>
> Agent: `research_question_agent`（deep-research v2.9.4, Phase 1 Scoping）
> Date: 2026-09-07
> Upstream: `research/p3-equation-structure-preservation-mr-adequacy-plan-v4-zh.md`

---

## 1. 问题（Problem Statement）

科学计算程序把连续方程离散化为可执行代码。这类程序普遍缺少廉价的逐输入 oracle：对绝大多数输入，没有已知正确答案可供比对。蜕变测试（MT）通过检查多次执行之间必须成立的关系（MR），把方程性质转化为**部分** oracle，是目前应对该 oracle 问题的主流手段之一。

MT 因此有一个尚未解决的测量学问题：

> **给定一组 MR，如何知道它够不够？**

单条 MR 有效不等于一组 MR 充分。实践中默认的代理指标是句法 mutation score（MS）——用算术符替换、关系符替换、常量修改、语句删除等局部代码编辑生成变异体作为分母，测 MR 集合能杀死多少。

**这个代理指标的分母与被测构念不匹配。** MR 承载的是方程层面的保结构义务：守恒、对称、单调、伴随、可逆、收敛阶。句法变异算子承载的是代码编辑的局部形态。两者之间没有必然映射：一个句法变异可能完全不触及任何结构义务（打乱日志格式、改动未激活分支），而一个真实的结构违反可能不对应任何单一句法编辑（时间积分格式从辛格式退化为非辛格式，往往是多处协同改动的结果）。

后果有三层：

1. **不可诊断** — 无法说出一组 MR 漏掉了哪一类结构风险；
2. **不可比较** — 无法判定两组 MR 孰优孰劣；
3. **无停止准则** — 无法回答「还需不需要再加 MR」。

这三点合起来意味着：MR 充分性目前**没有以外部义务空间为分母的测量方法**，只有以给定 MR 集合或缺陷总体为分母的代理量。

### 1.1 动机主张的收缩（2026-09-07，依 Phase 2 主题 A 证据修订）

原稿此处写的是「MR 充分性目前**没有可信的测量方法**」。该表述已被证伪，必须收缩。Phase 2 主题 A 的对抗性检索裁决为 **`PARTIAL`**，而非 `NO_EXISTING_MR_ADEQUACY_CRITERION`：至少两项 2024 年工作以「MT 测试充分性准则」为名公开发表。

- **Fu, A., Sun, C.-A., Zhang, J., & Liu, H. (2024).** *Test adequacy for metamorphic testing: Criteria, measurement, and implication* (arXiv:2412.20692). 已由 `search_arxiv` 独立核实。其摘要明确写道：「few studies have investigated the test adequacy assessment issue of MT」——**与本文原本主张的 gap 完全相同**——并提出「a new set of criteria that specifies testing requirements from the perspective of necessary properties satisfied by the SUT」。
- **Liu, Y., Li, R., Tao, H., & Zheng, Z. (2024).** *Test adequacy criteria for metamorphic testing.* QRS-C, 527–534. `10.1109/QRS-C63300.2024.00072`. 提出 MTcoverage，并**用变异测试验证该准则**。

这两篇用本文标题关键词一搜即得，遗漏它们不是完整性瑕疵而是选择性报告问题。

**收缩后可辩护的表述**（按强度递减，Phase 3 复冻时择一）：

1. 现有 MT 充分性准则测量的是「**给定** MR 集合下测试套件的充分性」（Fu et al., 2024; Liu et al., 2024），没有一项测量 MR 集合本身相对于程序语义义务的充分性。
2. 现有每一项 MT 充分性准则最终都以缺陷或变异体总体作效度验证，因此该领域尚无独立于「分母是否对齐」这一争议的充分性度量。
3. MR 集合质量目前由排序、选择、多样性与复合来处理，而非由充分性准则来处理。

**为何裁决是 PARTIAL 而非 EXISTS**：没有任何已定位工作以**独立于 MR 集合本身的分母**定义充分性。Fu et al. 的测量单位是 (MR 集合 × 源输入) 联合体——增删 MR 会改变分数，但「这组 MR 是否覆盖了程序的语义义务」它无法回答；一个遗漏整类义务的 MR 集合仍可测得 100% 充分。这个具体缺口仍然开放，也正是本文应当占据的位置。

### 1.2 先例裁决：v4 的三个构念已被本组自己的公开预印本占据（2026-09-07，主题 C）

主题 C 的先例裁决是 **`DIRECT_PRIOR_ART`**，且撞车对象是本课题组已在 arXiv 公开的工作。两篇均经 `search_arxiv` 独立核实（作者串一致：Meng Li; Xiaohua Yang; Jie Liu; Shiyu Yan）。

**arXiv:2605.17437v2 (SMS)** —— 即线 A 的公开版本，`submission/TOSEM_regular_20260729_m1m8/declarations.md` 已声明「An earlier version is available on arXiv as arXiv:2605.17437」。其摘要已经包含：

| v4 计划构念 | 该预印本已有的对应物 |
|---|---|
| SPTM（保结构定向变异） | 五个 domain-semantic 算子中的 **Conservation Erosion** 与 **Structural Injection**——按名称与构造即是保结构性质违反 |
| SLRMA（结构谱系相对 MR 充分性） | SMS 被明确定位为「a backward-compatible adequacy metric for domain-semantic metamorphic-relation sets in scientific computing」 |
| 12-PUT × 5-MP 实验设计 | 已完整执行，四个 single-output float-to-float 程序类 |
| 「保结构变异不可由语法编辑到达」这一核心实证主张 | 已报告：Hyperparameter / Structural Injection / Trajectory Flip 三类**在默认一阶语法配置下不可达** |
| ESPR 的 B（误差预算）分量 | 三层归因分类器，已分离 true semantic fault 与 tolerance / OOD / statistical / artefact |

**arXiv:2606.08269v1 (Min-MR-Complete)** —— 独立的第二篇公开预印本，已给出 layer-relative completeness 判据、support-set domination boundary、Set-Cover 等价与 NP-hardness、贪心近似、精确 ILP，以及 SMS-rank 上界。**SLRMA 若要做「MR 集合充分性的理论层」，这一层已被占。**

**关系的正确读法（修正 C agent 的判断）**：C agent 提出「self-plagiarism 或被抢发」的二分是过重的。实际状态见 `docs/STATE.md`：线 A **从未投出**，当前 stage 是「无可投稿件；旧稿件线全部冻结」，且 NOETHER / Min-MR-Complete 等伴随预印本在 m1m8 的 `references.bib` 与正文中**均已引用**，披露到位。因此这不是抢发，也不是未声明的切香肠。

**但真实约束仍然成立，且有两条**：

1. **对 arXiv:2605.17437**：v4 不能把 ESPR/SPTM/SLRMA 作为 first-of-kind 构念引入。任何审稿人用本文标题关键词搜一次 arXiv 就会看到同作者 2026 年的预印本已定义了算子、度量、设计与不可达结论。可行路径是把 v4 定位为该预印本的**后继版本**（arXiv supersede），而非独立新贡献。
2. **对 arXiv:2606.08269**：这是一篇**独立**的公开论文。v4 的 SLRMA 与它的完备性/最小化理论若重叠，才是真正的切香肠风险——两篇不同论文讲同一套理论。

**尚存的可辩护增量（待 Phase 3 裁定）**：SMS 预印本描述的是「三层归因分类器」，而 v4 的 ESPR 五元组 r = (φ, D, κ, B, O) 要求的是**不使用任何 MR 裁决的独立认证方法 O**，外加显式的适用域 D 与保持模式 κ。O 分量与 verdict-independence 是目前唯一看得见的、未被自己占据的缝隙。这个增量是否撑得起一篇 TOSEM，是 Phase 3 synthesis 的判断，不是检索能回答的。

**独立非自引的最近先例**（约束的是上述增量本身的新颖性）：Bartocci et al. (2023, ICST) 的 property-based mutation testing 已给出 SPTM 的定义内核（mutant 仅当能影响指定性质才 relevant，仅当造成该性质违反才算 killed），距离约 2 个构念——差别在性质来源是外部规约的时序逻辑而非控制方程，且无 κ / B / O。Ding, Li & Hu (2019, QRS) 已在科学计算软件中用不变量关系违反作为注入缺陷的目标。

**定位决策（2026-09-07，用户裁定）**：v4 **定位为 arXiv:2605.17437 的后继版本（arXiv supersede）**，不作为独立新论文。SPTM/SLRMA 写成 SMS 的理论化重述并引用该预印本；新颖性只押在 O 分量与 verdict-independence；**必须守住与 arXiv:2606.08269 的边界**（只引用其完备性理论层，不重述）。四条硬约束的完整表述见 `docs/STATE.md` §1.1。

### 1.3 主题 B：外部文献比预想拥挤（2026-09-07）

约束 2 撤回后新颖性改对外部文献衡量，主题 B 刻画的正是这块。完整论证见 `phase2b_audit_consolidation.md` §2.1，此处只记三条必须在写作前处置的：

1. **术语冲突不可沉默。** 「Semantic Mutation Testing」已被 Clark, Dan & Hierons 占用（变异语言解释函数、程序文本不动），且该术语的原创者已把它用在数值语义上——Dan & Hierons (2012b, ICST 290–299)《Semantic Mutation Analysis of Floating-Point Comparison》。**改名或设显式区分小节，二选一。**
2. **SLRMA 的评价形状有三条更近的先例，semantic mutation 不是最近的。** 「变异程序、以被声明义务集合漏掉哪些变异体来度量该义务集合的完备性」：Budd & Gopal (1985) 变异规约；Knauth et al. (2009) 用 meta-mutation 评契约质量；**Knüppel et al. (2021, FormaliSE)《How much specification is enough? Mutation analysis for software contracts》就是 SLRMA 的评价形状本身**，只是义务载体是 JML 契约而非 MR。三条都必须在相关工作中正面处理。
3. **构念错位主张的最顺手引用已被方法论反驳。** Chen et al. (2020, ASE) 论证测试集规模既非混淆变量也不该被操纵，直接冲击 Papadakis et al. (2018) 的「控规模后相关性弱」；Zhang et al. (2024, TOSEM) 与 Lu et al. (2026, TOSEM) 独立结论是规模处理得当后 mutation score 是**最好**的效度指标。**改用不依赖真实缺陷论证的三条**：Gay & Salahirad (2023) 的 9.92% 强耦合率、Ojdanić et al. (2023) 的句法相似不预测语义相似、Alblwi et al. (2024) 的同名度量两种形式化彼此弱相关。

> ⚠️ 本节的收缩已进行三轮（A → C → B）。Phase 1 复冻时以此三节为准。

---

## 2. 候选研究问题（Step 2–3）

生成 5 个候选，覆盖描述型、比较型、评估型三类。

| # | 候选 RQ | 类型 | FINER 均分 | 处置 |
|---|---|---|---|---|
| 1 | 以方程保结构要求谱系为分母的 MR 充分性度量，能否比以代码编辑为分母的句法 mutation score 更有效地测量科学计算程序 MR 集合的充分性？ | 评估型 | **4.2** | **选定为 Primary** |
| 2 | 方程导出的保结构要求能否被操作化为可独立认证的保结构变异？ | 描述/可行性型 | 4.0 | 降为 Sub-RQ 1（本身不含比较，不足以撑起全文） |
| 3 | 结构谱系相对充分性度量能否恢复质量已知 MR 集合的预注册质量偏序？ | 比较型 | 4.4 | 降为 Sub-RQ 2（单项最高分，但只覆盖判别效度一个侧面） |
| 4 | 结构谱系相对充分性能否解释独立真实缺陷的 MR 检出结果？ | 相关/准则型 | 3.4 | 降为 Sub-RQ 3（受真实缺陷可得性制约，Feasible 偏低） |
| 5 | 谱系宏平均相对于谱系不平衡是否稳健？ | 描述型 | 3.0 | 不采用——属 sensitivity 分析，非主问题 |

**设计判断**：候选 2/3/4 恰好对应构念效度、判别效度、准则效度三个测量学维度，构成一个完整的量表验证逻辑。把它们并列为三个 Primary RQ 会失去论文的单一论点；因此选候选 1 作伞式 Primary RQ，2/3/4 降为 Sub-RQ。这与 v4 方案的三 RQ 结构一致，只是补上了统摄它们的上位问题。

---

## 3. Primary Research Question（临时）

> **以方程导出的保结构要求谱系为分母的 MR 充分性度量，能否比以代码编辑为分母的句法 mutation score 更有效地测量科学计算程序中固定 MR 集合的充分性？**

"更有效地测量"在本文中被操作化为三个可证伪的测量学判据，即下文三个 Sub-RQ。本问题**不**主张语义变异在缺陷检测上普遍优于句法变异（该主张为 C6，永久 blocked）。

---

## 4. FINER 评估

| 准则 | 评分 | 理由 |
|---|---|---|
| **F**easible | **3/5** | 最弱项，且是真实风险。已有基础设施可复用（12-PUT / MR / 冻结协议 / 认证流水线），但本项目的历史记录不支持乐观：Boost.Math C++ 尝试推进数月后停在 ~70% 未完成；NumPy pilot 只产出 1 项目 4 配对；14 主体适用性普查产出 0 个候选。v4 还额外要求新建结构谱系、≥3 个正交认证器和冻结确认集。给 3 分而非 4 分是刻意的——见 §7 风险。 |
| **I**nteresting | **5/5** | 构念错位是软件测试测量学的真问题，不是构造出来的缝隙。安全关键科学计算（核仪控、CFD、气候模式）对「MR 够不够」有直接的工程需求。 |
| **N**ovel | **2/5 (PROVISIONAL，已二次下调)** | 原评 4/5 → 3/5 → 2/5。**主题 C 裁决 `DIRECT_PRIOR_ART`，触发了本行原先自己写下的下调条件**（「若发现有人已用结构性质违反作为变异目标或充分性分母，须下调至 2 分并重构论文定位」）：本组自己的 arXiv:2605.17437 已用 Conservation Erosion / Structural Injection 作变异算子并以 SMS 作 MR 充分性分母，arXiv:2606.08269 已占据完备性/最小化理论层。详见 §1.2。仅存增量为 ESPR 的 O 分量与 verdict-independence。**2 分是 FINER 的下限容忍值，论文定位必须重构后才能继续。** 以下为主题 A 的下调理由，仍然成立：**(a) 方程级 MR 推导已有独立先例**：Yan & Zhu (2025, STVR 35(1), e1912) 明确宣称「formally derive metamorphic relations from the numerical models of differential equations」，因此本文新颖性不能落在「从方程结构推导 MR」这件事本身，只能落在**充分性测量**上。**(b) 自引冲突**：本课题组自己的 NOETHER 预印本 (arXiv:2605.17390) 已按对称性/自伴性/时间反演组织 MR 推导，另有 arXiv:2605.17437 (SMS) 与 arXiv:2606.17529 (DVG-MT) 两篇，以及 Huang, Luo & Li (2022, IAECST) 一篇自合著 A3 条目——四项均须声明为自引，且 NOETHER **不得**被当作「方程级推导仍是开放问题」的独立证据。**此分数在主题 B/C 裁决返回前仍不作数。** 若发现有人已用结构性质违反作为变异目标或充分性分母，须再下调至 2 分并重构论文定位。 |
| **E**thical | **5/5** | 研究对象为开源科学计算库与其缺陷记录，无人类被试，无个人敏感数据。需在最终稿声明所用工件的许可证。 |
| **R**elevant | **5/5** | 直接服务于 IEC 60880 / ASME V&V 类验证实践对测试充分性证据的要求；同时对 MT 方法论社区提供可迁移的量表验证范式。 |
| **平均** | **4.0/5（原 4.4）** | 形式上仍达标（阈值 ≥3.0，无单项 <2），但**这个「达标」不应被当作放行信号**：Novel=2 已落在容忍下限，且约束来自本组自己的公开预印本，不能靠更努力的检索或更好的写作消除，只能靠重构定位消除。最弱项现为 Novel，其次 Feasible=3。 |

---

## 5. Sub-questions

对应 v4 方案的三个 RQ，构成量表验证的三个层次：

1. **构念效度（Sub-RQ 1）** — 方程导出的保结构要求（ESPR）能否被操作化为可认证的保结构变异（SPTM），并比**预算匹配**的一阶与高阶句法变异更集中地产生预声明的结构偏离？
2. **判别效度（Sub-RQ 2）** — 结构谱系相对充分性（SLRMA）能否恢复完整、删族、弱化、冗余、错配五档 MR 集合的**预注册**质量偏序？
3. **准则效度（Sub-RQ 3）** — SLRMA 能否解释**独立准入**真实缺陷的 MR 检出结果，并提供超出句法 mutation score、MR 数量与执行成本的增量信息？

**Sub-RQ 2 是决定性实验**（与 TOSEM 编辑视角评估一致）：若 SLRMA 无法恢复质量已知 MR 集合的偏序，则它不在测量充分性，全文主张坍塌。这也是本研究最愿意失败的地方——见 §7 证伪预设占位。

---

## 6. 范围边界

**IN SCOPE**
- 单输出科学计算 kernel，其治理方程可显式写出，且蕴含守恒 / 对称 / 单调 / 伴随 / 可逆 / 收敛中至少一类性质；
- **固定** MR 集合的**静态**充分性评价；
- 相对于冻结结构谱系 \(G\)、适用域 \(D\)、误差预算 \(B\) 与冻结变异总体的**相对**充分性。

**OUT OF SCOPE**
- MR 的生成、推荐、更新与迭代优化（留给下一篇的动态闭环）；
- 多输出、强耦合多物理场程序；
- 「语义变异普遍优于句法变异」的一般性主张（claim C6，永久 blocked）；
- 语言无关的自动变异生成（claim C7，留给后续论文）；
- 程序正确性证明——SLRMA 高分不表示程序正确。

**KEY ASSUMPTIONS**（每条都是可被证伪的，须在 §7 证伪预设中给出失败判据）
- (a) 目标程序的方程结构可从文档、规范或求解器设计中显式导出，无需逆向工程；
- (b) 存在独立于 MR 判定器的认证方法，能判定 \(P\models_B r\) 是否成立；
- (c) 误差预算 \(B\) 可在实验前先验确定，而非事后调参到使结论成立；
- (d) 结构谱系 \(G\) 的节点划分对领域专家可复现（需二评者一致性证据）。

---

## 7. 待 Phase 3 后补完的部分

以下三项**故意留空**，因为它们必须由文献与 gap analysis 约束，不能先验写死：

- **正式 RQ 复冻** — Primary RQ 的措辞、Novel 评分、以及 §1「没有可信测量方法」这一动机性主张的强度。
- **证伪预设** — 每个 Sub-RQ 的预注册失败判据、点预测或区间预测，以及项目规则 §10.1 的过度防御审计（区分「效度修复」与「主张收缩」）。
- **论证蓝图** — 实验对象、实验方法、评价指标、对比基线，由 `research_architect_agent` 在 Phase 1c 产出。

## 8. 已识别的最大风险（供 Methodology Blueprint 消化）

**Feasible=3 不是形式化的谦虚，是历史数据。** 本项目在「在真实科学计算软件上构造并认证语义变异体」这件事上已有三次可审计的成本记录：Boost.Math 尝试停在 70%、NumPy pilot 只到 4 配对、14 主体普查 0 候选。v4 在此之上还要新增结构谱系、正交认证器与冻结确认集。

若不主动收缩范围，v4 最可能的失败模式不是被审稿人拒稿，而是**再次卡在工程可行性上、永远到不了 RQ2 的决定性实验**。Methodology Blueprint 必须先回答：用几个程序、几个结构谱系节点、几个认证器，就足以让 Sub-RQ 2 成为一个可完成的实验。
