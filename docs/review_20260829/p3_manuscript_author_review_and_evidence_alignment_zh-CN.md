# P3 稿件作者审阅与证据对齐报告（简体中文版）

本文件是英文审阅报告 `p3_manuscript_author_review_and_evidence_alignment.md` 的简体中文对应版本。状态枚举、证据标识、数字、SHA、作者裁决边界和终态均保持不变；本译文不构成新的审阅或裁决。

任务：`P3_MANUSCRIPT_AUTHOR_REVIEW_AND_EVIDENCE_ALIGNMENT`

审阅模式：只读的证据对齐作者审阅。本任务不是同行评审、稿件修订、目标期刊决定或新实验。

终态：`P3_MANUSCRIPT_AUTHOR_REVIEW_PACKET_READY`

`P3_C3_CLAIM_SCOPE_PATH_CLOSED=true`

## 审阅边界与输入身份

受审稿件为 commit `8b36afdb4e6e3f92f2d6aef4f98dd38853bef26c`（parent：`c5af89a0c25614dbd9ba97b853e5a62f8091a24e`）上的 `research/p3-semantic-mutation-evidence-aligned-manuscript-v0.1.md`。审阅开始时的稿件 SHA-256 为 `b6f69b0f815f277903fd028a05605b295ca245e0806cc261f7895cad41021889`。

固定权威文件与要求的身份一致：

| 对象 | SHA-256 |
|---|---|
| `research/evidence/p3_claim_ledger_v1.3.0.yml` | `95184db4db23c84649cb85fbf6f0d4a9503fa45a70297b7c29d9a57d9d5b6ff5` |
| `research/p3-semantic-mutation-core-claims-rqs-v1.3.0.md` | `41a8fa78beb621267223762fe0879f96ecb98e0eee7aea0befac72261d48483f` |
| `docs/superpowers/specs/2026-08-28-p3-c3-claim-scope-and-ledger-amendment-design.md` | `709e3cb59539c8620b50e2c1c232cf90bde365a923a4502b1f6dfae5cddddec2` |
| `docs/review_20260828/p3_c3_stage1_applicability_census_scientific_disclosure.md` | `9f0040f460d48310d764c10a75319b8ec4fb4fdb6b691e78b153d284cdaa0552` |
| `data/p3_v3/phase3/prospective-multiproject-applicability-stage1-v2/cohort-terminal.json` | `f2e9af90ed31bd118a80808a04e3af66c5abee539f0093c6087c176e2bee51ab` |
| `docs/review_20260828/p3_claim_path_reprioritization_after_stage1_empty_candidates.md` | `dcba9d459eb58bf2984d117b826077998f1069120eb630d004a74ae337836079` |

Stage I 终态记录中的 artifact SHA-256 为 `45757bb594d582b380ee7955f0caeab92adfd3c10702c31cf788f896a6595a97`。Ordinal-8 审阅只使用已提交的正式 Markdown/JSON：RQ2 handoff、clean replay、remaining-three batch、先前的基础设施失败记录和 exact-overlap artifact。没有使用 `/tmp`、Cloud runtime 或 `/opt/cursor/artifacts` 证据作为 claim 权威来源。

## 面向作者的执行摘要

稿件的核心数字与边界和固定实证记录一致。稿件始终报告 1 个已执行项目、4 个 NumPy pair、semantic 4/4 KILL、syntactic 3/4 KILL 和 1/4 SURVIVE、两项 exact-overlap 均为 0/4，以及覆盖 14 个 subject、140 个 closure 的 Stage I census，其中 0 个 `SITE_FROZEN`、140 个 `APPLICABILITY_CLOSED_NOT_APPLICABLE`、Stage II candidate 为 0。C3 仍为 `blocked`；稿件没有进行跨项目推断。

未发现核心证据矛盾。主要未决事项包括：补全参考文献；增强 18-group/35-defect catalog foundation 的直接证据定位；核验两处相关工作表述，因为仓库现有 audit 尚未确立其语义支持；在目标期刊未确定时保留结构的暂定性质；以及由作者拥有的元数据和披露决定。

## 逐节审阅

| 章节 | 发现 | 证据/权威 | 处置 | 建议行动 |
|---|---|---|---|---|
| 标题 | 标题准确呈现三个实际对象：semantic/syntactic 比较、单项目 paired pilot 和 prospective census。“Evidence-Bound Scope”准确表达证据上限，但最终措辞由作者结合目标期刊决定。 | Core-claims v1.3.0 的 current-paper scope；claim-scope design §§1、3 | `AUTHOR_DECISION_REQUIRED` | 作者接受当前标题或提出适配目标期刊的备选标题；不得移除单项目/census 边界。 |
| 摘要 | 所有主要数字和 C3 状态均与正式证据一致。Stage I 表述被限定为特定版本下的资格结果，而不是广义负面结论。 | Ordinal-8 RQ2 handoff；exact-overlap JSON；Stage I terminal；ledger C3 | `ACCEPT` | 后续压缩摘要时保留当前 scope qualifier。 |
| 内部中文伴随摘要 | 实证数字和局限性与英文摘要一致，并明确说明保留该摘要不是投稿默认选择。 | 与摘要相同的证据 | `AUTHOR_DECISION_REQUIRED` | 作者决定内部伴随摘要保留在工作稿中，还是投稿前移除。 |
| 关键词 | 关键词与研究匹配，但最终数量以及“metamorphic testing”是否足够核心取决于目标期刊政策。 | 稿件 study design；目标期刊未确认 | `ACCEPT` | 仅在目标期刊确认后重新审视。 |
| 引言 | 动机、重复测量警告、单 cluster 上限、贡献清单和明确的非主张均与 claim 权威一致。第一项贡献是方法学框架，而不是提升后的 C1/C3 状态。 | Ledger；core-claims；ordinal-8 handoff；claim-scope design | `ACCEPT` | 后续修订时保持贡献清单的局部性，不得提升 C3。 |
| 背景与相关工作 | 正文中仍有 6 个必须解决的引用主题。现有 audit 验证了若干候选来源的存在性/元数据，但没有为所有相邻 claim 提供完整的语义对齐证书。 | 仓库 reference audits；`source/references.bib`；理论备忘录 | `CITATION_REQUIRED` | 仅在作者授权后处理 6 个缺口；另行核验下列两处可能的 related-work overclaim。 |
| 研究问题与主张边界 | 保留冻结的 RQ2，并把当前可回答范围收缩为三个局部问题。C3、`n_projects = 1` 和禁止跨项目推断的上限均明确呈现。 | Core-claims v1.3.0 的 RQ2 和 Current-paper scope；ledger C3 | `AUTHOR_DECISION_REQUIRED` | 作者确认当前收缩后的 RQ2 范围。不建议自动重写 RQ。 |
| 研究设计 | Catalog foundation、single-project pilot 和 prospective census 区分清楚。18-group/35-`verified_full`/fixed-version 句子在仓库中有线索，但其直接 locator 弱于 ordinal 8 和 Stage I 的机器可读 locator。 | Path-reprioritization report §4.1；ordinal-8 handoff；Stage I terminal | `REVISION_RECOMMENDED` | 获得批准后，加入最强的现有 catalog locator，或把“each recorded with a fixed version”收窄为仓库已审计的准确措辞。 |
| 结果 | 仅报告正式 observation，以 pair 作为 reduction unit，保留基础设施失败记录，且没有引入事后统计量。 | RQ2 handoff；clean replay；remaining-three batch；exact-overlap；Stage I terminal | `ACCEPT` | 保留 pair 表及其 denominator。 |
| 讨论 | Observation、interpretation、limitation 和 governance 在实质上有所区分，但在正文中仍交织呈现。“blocks one cheap objection”是作者解释，而不是新的实证结果。 | Exact-overlap artifact；claim-scope design 允许/禁止的解释 | `REVISION_RECOMMENDED` | 获批后，标注或重排为 observation → interpretation → limitation → future boundary；保留仅适用于本地证据的措辞。 |
| 威胁与局限 | 正确区分 construct、internal、external、conclusion、selection/adaptivity 和 infrastructure threats。明确写出 `n_projects = 1`、first-eligible-subject selection 和受版本约束的 census。 | Handoff methodology audit 与 limitations；Stage I disclosure §§7、10 | `ACCEPT` | 保留所有现有上限；仅在作者批准后添加引用。 |
| 结论 | 没有出现强于 Results 的 claim，并保留 pilot、eligibility bound、不可识别的 uncertainty 和 blocked C3。 | Core-claims current-paper scope；ledger；Stage I path closure | `ACCEPT` | 保持 C3 blocked，避免把“eligibility bound”改写为 construct absence。 |
| 数据可用性 | 正确识别三个权威计数来源，且没有虚构 DOI。公开 URL/归档 DOI 策略仍未决定。 | 仓库证据路径；作者占位符 | `AUTHOR_DECISION_REQUIRED` | 作者选择仓库发布和归档策略。 |
| 伦理 | 草稿声明不涉及 human participants/personal sensitive data，同时已要求作者根据最终 subjects 和 licenses 进行确认。 | 稿件占位符；受审权威材料中没有作者证明 | `AUTHOR_DECISION_REQUIRED` | 作者确认措辞及 artifact license 的含义。 |
| 作者贡献 | 未推断姓名或 CRediT roles。 | 缺少作者拥有的事实 | `AUTHOR_DECISION_REQUIRED` | 作者提供姓名和 CRediT 分工。 |
| 利益冲突 | 未虚构任何声明。 | 缺少作者拥有的事实 | `AUTHOR_DECISION_REQUIRED` | 作者确认最终声明。 |
| 资助 | 未推断任何资助方。 | 缺少作者拥有的事实 | `AUTHOR_DECISION_REQUIRED` | 作者提供最终 funding statement。 |
| AI 使用披露 | 正确地把决定留给尚未确认的目标期刊政策。 | 目标期刊和披露路径未解决 | `AUTHOR_DECISION_REQUIRED` | 确认目标期刊；如有需要，另行授权 disclosure 任务。 |
| 参考文献 | 当前 15 条文献均在正文中被引用，所有现有 author-year citation 都能解析到参考文献条目。仓库 audit 覆盖元数据存在性，并保留 Petrović online-first/print-year 的已知提示。另有 6 个引用主题缺口。 | `reference_verification_audit.md`；`reference_verification_round85.md`；U2 foundations audit | `CITATION_REQUIRED` | 获得作者授权后补全 6 个缺口；不得仅凭元数据存在性声称已完成语义验证。 |

Disposition 汇总：`ACCEPT` 6；`REVISION_RECOMMENDED` 2；`AUTHOR_DECISION_REQUIRED` 9；`CITATION_REQUIRED` 2；`EVIDENCE_CONFLICT` 0；`REMOVE_OR_WEAKEN` 0。

## 完整实证 claim–evidence 对齐

| Claim ID | 稿件位置 | 准确/压缩后的 claim | 证据定位 | 证据状态 | Claim strength | 处置 |
|---|---|---|---|---|---|---|
| E01 | 摘要 ¶2 | 1 个 NumPy subject、4 个 pair、每个 pair 5 个 input、60 个正式 PASS cell | RQ2 handoff `analysis_units`、`execution_funnel` | `DIRECTLY_SUPPORTED` | observed | `ACCEPT` |
| E02 | 摘要 ¶2 | Semantic 4/4 KILL；syntactic 3/4 KILL 和 1/4 SURVIVE | RQ2 handoff `reductions`、`pairs` | `DIRECTLY_SUPPORTED` | observed | `ACCEPT` |
| E03 | 摘要 ¶2 | Normalized-patch 和 mutant-tree exact equality 均为 0/4 | exact-overlap JSON 的 count/pair-count 字段 | `DIRECTLY_SUPPORTED` | observed | `ACCEPT` |
| E04 | 摘要 ¶2 | Pilot 无法识别 project-clustered uncertainty；C3 仍为 blocked | RQ2 handoff `rq2_coverage`、`claim_ceiling`；ledger C3 | `DIRECTLY_SUPPORTED` | blocked ceiling | `ACCEPT` |
| E05 | 摘要 ¶3 | 在当前冻结版本中，14 个 successor 没有产生 Stage II candidate | Stage I terminal subjects；Stage I disclosure §5 | `SUPPORTED_WITH_SCOPE_QUALIFIER` | qualified | `ACCEPT` |
| E06 | 引言 ¶3 | Input 是 pair 内的重复测量；同一 library 上的 4 个 pair 仍只构成 1 个 project cluster | RQ2 handoff `analysis_units` 和 methodology audit | `SUPPORTED_WITH_SCOPE_QUALIFIER` | qualified methods boundary | `ACCEPT` |
| E07 | 引言 ¶4 | C3 为 blocked，且升级条件仍未满足 | Ledger C3 和 `status_policy.note` | `DIRECTLY_SUPPORTED` | blocked | `ACCEPT` |
| E08 | 引言贡献清单 | 列出的 5 项是当前论文的贡献框架 | Core-claims current-paper scope；稿件综合 | `AUTHORIAL_INTERPRETATION` | authorial contribution framing | `AUTHOR_DECISION_REQUIRED` |
| E09 | 引言末段 | 18 个 program group 和 35 个 defect 不等于 18 个 runner-ready paired-evidence project 或 35 个 paired observation | Path-reprioritization §§4.1、4.6；claim-scope design §6 | `DIRECTLY_SUPPORTED` | negative ceiling | `ACCEPT` |
| E10 | §3 | 冻结的 RQ2 措辞 | Core-claims v1.3.0 RQ2 | `DIRECTLY_SUPPORTED` | frozen authority | `ACCEPT` |
| E11 | §3 | 当前论文只回答 pair reducer、两项 exact-overlap measure 和 Stage II candidate-universe status；family coverage 仍未测量 | Core-claims current-paper scope；exact-overlap；Stage I terminal | `DIRECTLY_SUPPORTED` | contracted scope | `ACCEPT` |
| E12 | §3 C3 段落 | C3 仍为 blocked，因为 `n_projects = 1` 且 clustered uncertainty 不可识别 | RQ2 handoff `analysis_units.n_projects`、`rq2_coverage`；ledger | `DIRECTLY_SUPPORTED` | blocked | `ACCEPT` |
| E13 | §4.1 ¶1 | Foundation 包含 18 个 program/library group 和 35 个 `verified_full` defect，每个都有固定 version | Path-reprioritization §4.1 和 catalog summary reference | `INTERNALLY_SUPPORTED_BUT_LOCATOR_WEAK` | descriptive foundation | `REVISION_RECOMMENDED` |
| E14 | §4.1 ¶3 | 已执行 paired-evidence project 的数量为 1：NumPy ordinal 8 | RQ2 handoff `analysis_units.n_projects`；controlled subject identity | `DIRECTLY_SUPPORTED` | observed | `ACCEPT` |
| E15 | §4.2 ¶2 | 1 project、1 repository、1 subject、2 site、4 pair、4+4 mutant、每个 pair 5 input；cell 不是独立观测 | RQ2 handoff `analysis_units` | `DIRECTLY_SUPPORTED` | observed/design-bound | `ACCEPT` |
| E16 | §4.2 末段 | INV/CMP 和 SI/TF 有表示；MONO 缺少 contract；CONV/DYN 没有 frozen site | RQ2 handoff `contract_category_coverage` | `DIRECTLY_SUPPORTED` | observed funnel | `ACCEPT` |
| E17 | §4.3 ¶1 | 受控 NumPy `2.0.0.dev0`、2 site、4 pair、完整执行 60 个 cell | RQ2 handoff `execution_funnel`；clean/batch runtime identity | `DIRECTLY_SUPPORTED` | observed | `ACCEPT` |
| E18 | §4.3 ¶2 | 第一次 INV/TF attempt 有 15 个 infrastructure failure，没有 kill/survival observation | RQ2 handoff `execution_funnel`；先前 paired-evidence JSON | `DIRECTLY_SUPPORTED` | observed funnel | `ACCEPT` |
| E19 | §4.3 ¶3 | Clean replay 产生 15 个 cell；remaining-three batch 产生 45 个；在同一 controlled runtime identity 下合计 60/60 PASS | RQ2 handoff `execution_funnel`；clean/batch JSON | `DIRECTLY_SUPPORTED` | observed | `ACCEPT` |
| E20 | §4.4 | 两种 overlap identity 相互独立；二者都只是计数；interval authority 不完整 | exact-overlap JSON 字段以及 interval status/reason | `DIRECTLY_SUPPORTED` | observed plus unmeasured boundary | `ACCEPT` |
| E21 | §4.5 ¶1–2 | Stage I 在冻结的 PBF/inventory/predicates/selection 下覆盖 14 个 subject 和 140 个 slot | Stage I terminal；Stage I disclosure §§2–4 | `DIRECTLY_SUPPORTED` | observed/design-bound | `ACCEPT` |
| E22 | §4.5 ¶3 | Candidate rule 为 `site_frozen_count >= 1`；0 个 frozen site 推导出空的 Stage II universe | Stage I disclosure §5；terminal per-subject counts | `DIRECTLY_SUPPORTED` | observed mechanical derivation | `ACCEPT` |
| E23 | §5.1 表 1 | Pair outcome：P1 K/K、P2 K/S、P3 K/K、P4 K/K | RQ2 handoff `pairs[]` | `DIRECTLY_SUPPORTED` | observed | `ACCEPT` |
| E24 | §5.1 汇总 | Semantic 4/4；syntactic 3/4；contingency 3/1/0/0；original 20/20；60/60 PASS | RQ2 handoff `reductions`、`paired_contingency`、`execution_funnel` | `DIRECTLY_SUPPORTED` | observed | `ACCEPT` |
| E25 | §5.1 cell 细节 | 3 个 pair 的两条 arm 均为 5/5 KILL；P2 syntactic 为 5/5 SURVIVE，semantic 为 5/5 KILL；original 为 5/5 SURVIVE | RQ2 handoff `pairs[]` | `DIRECTLY_SUPPORTED` | repeated-measure detail | `ACCEPT` |
| E26 | §5.1 末段 | P2 是唯一 discordant pair；证据不允许给出 superiority score/test | RQ2 handoff `paired_contingency`、blocked claims | `SUPPORTED_WITH_SCOPE_QUALIFIER` | observed plus negative ceiling | `ACCEPT` |
| E27 | §5.2 ¶1 | 两项 exact-overlap measure 均为 0/4，没有任何 pair 完全匹配 | exact-overlap JSON `pairs[]` 和 aggregate counts | `DIRECTLY_SUPPORTED` | observed | `ACCEPT` |
| E28 | §5.2 ¶2 | Exact non-overlap 是局部 construct-distinctness observation，不是 testing-value evidence，也不支持 transport | Core-claims RQ2；claim-scope design §§3、6 | `SUPPORTED_WITH_SCOPE_QUALIFIER` | qualified interpretation | `ACCEPT` |
| E29 | §5.3 ¶1 | Stage I：14 subject、140 closure、0 `SITE_FROZEN`、140 not applicable、0 Stage II candidate | Stage I terminal；Stage I disclosure §§3–5 | `DIRECTLY_SUPPORTED` | observed | `ACCEPT` |
| E30 | §5.3 ¶2–3 | 0/140 受权威边界约束，不代表 industrial prevalence、construct absence 或对 C3 的支持；Stage II 不启动 | Stage I disclosure §§6–10；path decision | `SUPPORTED_WITH_SCOPE_QUALIFIER` | qualified/blocked | `ACCEPT` |
| E31 | 讨论 ¶1 | 唯一正式的行为对比是在 1 个 subject 上的 4/4 与 3/4 | RQ2 handoff `reductions`、limitations | `DIRECTLY_SUPPORTED` | observed | `ACCEPT` |
| E32 | 讨论 ¶2 | Exact non-overlap 排除了“pilot 只是为完全相同的编辑重新命名”这一狭义质疑 | exact-overlap data 加稿件解释 | `AUTHORIAL_INTERPRETATION` | bounded interpretation | `REVISION_RECOMMENDED` |
| E33 | 讨论 ¶3 | 20/20/20 个 cell 无法识别 project uncertainty；`n_projects = 1` 时缺少 project cluster，因此不允许跨项目推断 | RQ2 handoff uncertainty accounting 和 methodology audit | `DIRECTLY_SUPPORTED` | blocked inference | `ACCEPT` |
| E34 | 讨论/结论 | 当前 two-stage route 已关闭；不会在此 C3 路径上寻找第 2/3 个 paired project | Ledger note；core-claims current-paper scope；path decision | `DIRECTLY_SUPPORTED` | frozen path decision | `ACCEPT` |
| E35 | 结论 | Pilot 和 candidate-universe result 不会提升 C3；RQ2 仍保持收缩 | Ledger；core-claims；Stage I disclosure | `DIRECTLY_SUPPORTED` | blocked/contracted | `ACCEPT` |
| E36 | 数据可用性 | 3 个仓库 artifact 是权威计数来源；当前尚未生成 DOI | 稿件 evidence comments 和固定仓库对象 | `DIRECTLY_SUPPORTED` | repository-state statement | `ACCEPT` |

Claim 表总计：36。证据状态计数：`DIRECTLY_SUPPORTED` 28；`SUPPORTED_WITH_SCOPE_QUALIFIER` 5；`INTERNALLY_SUPPORTED_BUT_LOCATOR_WEAK` 1；`AUTHORIAL_INTERPRETATION` 2；`UNSUPPORTED` 0；`CONTRADICTED` 0。

## RQ 与论证结构审阅

| 问题 | 评估 | 处置 | 面向作者的说明 |
|---|---|---|---|
| 核心研究问题是否清楚且可由现有证据回答？ | 是，但前提是采用稿件中明确的范围收缩。冻结的 RQ2 措辞宽于当前论文的三个问题，但论文在 Methods/Results 之前说明了这种收缩。 | `ACCEPT` | 将冻结措辞和三个问题的边界放在一起保留。 |
| RQ2 是否保留但被正确缩小？ | 是。稿件只声称回答 pair behavior、两项 exact-overlap measure 和当前版本 candidate-universe status。 | `AUTHOR_DECISION_REQUIRED` | 作者确认这是否是预期的论文级 RQ2 范围。 |
| Blocked C3 与论文贡献之间是否存在逻辑矛盾？ | 不存在。论文呈现的是 pilot、census 和 evidence boundary，而不是已经完成的多项目 C3 confirmation。 | `ACCEPT` | 保持局部 construct observation 与 lifted claim status 的区别。 |
| Introduction 是否承诺了 Results 无法交付的跨项目结论？ | 没有。引言明确写出缺失的 cluster 并拒绝 transport。 | `ACCEPT` | 后续修订中不得扩大贡献动词的强度。 |
| Study Design 是否区分 catalog foundation、single-project pilot 和 prospective census？ | 是。三类对象分别命名，并具有不同 denominator 和作用。 | `ACCEPT` | 只需增强 18/35/fixed versions 的直接 locator。 |
| Results 是否只报告正式 observation？ | 是。结果使用 handoff/overlap/terminal counts，并保留 unmeasured/unidentifiable 状态。 | `ACCEPT` | 保持基础设施历史和 pair denominator 可见。 |
| Discussion 是否区分 observation、interpretation、limitation 和 future work？ | 实质上已区分，但视觉结构上仍相互交织。 | `REVISION_RECOMMENDED` | 后续结构修订可以标出四个层次，但不得改变 claim。 |
| Conclusion 是否比 Results 更强？ | 没有。结论更弱或等强，并保持 C3 blocked。 | `ACCEPT` | 保持当前上限。 |
| 当前标题是否表达 pilot + census + evidence boundary？ | 是。标题准确，但较长且面向期刊。 | `AUTHOR_DECISION_REQUIRED` | 作者决定准确性与简洁性何者优先。 |
| 如果 TOSEM 尚未确认，哪些内容仍属暂定？ | 期刊特定的章节顺序、摘要/关键词限制、引用格式、标题长度、相关工作位置、AI disclosure、Data Availability 措辞和 cover-letter framing。 | `AUTHOR_DECISION_REQUIRED` | 在任何格式或政策合规检查前确认目标期刊。 |

现阶段不建议重写 RQ。如果作者以后决定在稿件中替换冻结的 RQ2 措辞，同时保持 living authority 不变，可考虑但不由本报告选择以下两个面向论文的候选表述：

1. “在冻结的 NumPy pair 上，semantic mutant 与其 first-order syntactic baseline 之间观察到哪些行为差异和精确结构差异，又有哪些跨项目结论仍不可识别？”
2. “Ordinal-8 pilot 中观察到哪些 pair-level kill/survival 和 exact-overlap 差异，冻结的 prospective census 又为当前 multi-project path 施加了什么 eligibility boundary？”

## 现有参考文献审计

稿件包含 15 条参考文献。15 条全部在正文中被引用，且每条当前 author-year citation 都有匹配的参考文献条目。仓库 audit 验证了全部 15 条的元数据存在性，但这本身并不证明每个相邻语义 claim 都得到支持。

| 现有参考文献 | 稿件中的主要用途 | 仓库 audit 结果 | 引用审阅状态 | 说明 |
|---|---|---|---|---|
| Ammann & Offutt 2008 | Coupling hypothesis / testing foundation | 元数据已在 round85 #20 验证 | `EXISTENCE_VERIFIED_ALIGNMENT_UNCHECKED` | 现有 audit 确认该书存在，但未确认相邻的精确释义。 |
| Andrews et al. 2005 | 用 mutant 替代 real fault | 元数据已在 audits #4/#5 验证 | `EXISTENCE_VERIFIED_ALIGNMENT_UNCHECKED` | 标题与用途方向一致，但不存在 P3 专用的 passage audit。 |
| Delgado-Pérez & Chicano 2020 | Equivalent-mutant problem | Audit 明确讨论了元数据和相关性 | `VERIFIED_FROM_EXISTING_AUDIT` | 现有 audit 直接说明了与 equivalent-mutant 的相关性。 |
| DeMillo et al. 1978 | Mutation-testing 起源和 test-data selection | 元数据已在 audits #1 验证 | `EXISTENCE_VERIFIED_ALIGNMENT_UNCHECKED` | 没有针对 P3 句子的全文 claim-alignment 记录。 |
| Humbatova et al. 2021 | DeepCrime / 面向 real-fault 的 DL mutation | 元数据已在 audits #12/#24 验证 | `EXISTENCE_VERIFIED_ALIGNMENT_UNCHECKED` | Bibliography 干净，但相邻 construct comparison 尚未审计。 |
| Jia & Harman 2009 | 超越 first-order catalog 的 higher-order mutation | 元数据已在 audits #3/#4 验证 | `POSSIBLE_OVERCLAIM` | “does not systematically express”强于现有元数据/相关性 audit 能确立的内容。 |
| Jia & Harman 2011 | Mutation-testing survey | 元数据已在 audits #2 验证 | `EXISTENCE_VERIFIED_ALIGNMENT_UNCHECKED` | Survey 存在性已验证，但 P3 特定综合表述未经 passage check。 |
| Just et al. 2014a | Mutant 与 real fault 的关系 | 元数据已在 audits #5/#6 验证 | `EXISTENCE_VERIFIED_ALIGNMENT_UNCHECKED` | 仓库中没有相邻段落审计。 |
| Just et al. 2014b | Defects4J 的 controlled buggy/fixed pair | 元数据已在 audits #13/#25 验证 | `EXISTENCE_VERIFIED_ALIGNMENT_UNCHECKED` | 设计释义看似合理，但 audit 未对其提供语义证明。 |
| Kintis et al. 2018 | 工具/operator-set 分歧 | 元数据已在 audits #7/#8 验证 | `EXISTENCE_VERIFIED_ALIGNMENT_UNCHECKED` | Audit 验证的是文献记录，不是“operator sets differ”这一准确句子。 |
| Papadakis et al. 2019 | Mutation-testing survey 和 construct caveat | 元数据已在 audits #6/#7 验证 | `EXISTENCE_VERIFIED_ALIGNMENT_UNCHECKED` | 没有 P3 特定的语义对齐记录。 |
| Petrović & Ivanković 2018 | Industrial scale/productive-mutant filtering | 元数据已在 audits #9/#21 验证 | `EXISTENCE_VERIFIED_ALIGNMENT_UNCHECKED` | 相邻的 filtering/scale 综合表述未做 passage check。 |
| Petrović et al. 2021 | 大规模 practical mutation testing | 元数据已在 audits #10/#22 验证 | `EXISTENCE_VERIFIED_ALIGNMENT_UNCHECKED` | 2021 early-access 与 2022 issue year 的差异仍是非阻断性 audit 提示。 |
| Tip et al. 2024 | 超越 fixed operator list 的 LLMorpheus | 元数据已在 audits #11/#23 验证 | `POSSIBLE_OVERCLAIM` | 现有 audit 验证了 arXiv identity，但没有验证“outside a fixed operator list”。 |
| Zhang et al. 2021 | 使用 MT 验证 test-order-generation system | Audit candidate 1 / round85 #11 明确讨论了元数据和准确相关性 | `VERIFIED_FROM_EXISTING_AUDIT` | 现有 audit 明确描述了这一用途。 |

15 条文献的状态汇总：`VERIFIED_FROM_EXISTING_AUDIT` 2；`EXISTENCE_VERIFIED_ALIGNMENT_UNCHECKED` 11；`POSSIBLE_OVERCLAIM` 2；`CITATION_REQUIRED` 0；`UNRESOLVED` 0。现有 audit 对元数据存在性的覆盖为 15/15，但不能声称语义对齐已验证 15/15。

## 引用缺口

| 引用缺口 | 稿件位置 | 为什么需要 | 仓库现有线索 | 作者行动 |
|---|---|---|---|---|
| Clark、Dan 和 Hierons 的 semantic mutation testing / SMT-C | §2.2 named semantic-mutation operator 之后 | 确立已有的具名 construct 和工具谱系，避免把 P3 标签写成新术语。 | `reference_verification_round85.md` refs 12–13；`source/references.bib` 中 Clark/Dan 条目；理论备忘录 bibliography | 批准从现有已审计线索中添加来源；如有必要，授权 passage-level alignment verification。 |
| Chen、Cheung 和 Yau 的 metamorphic-testing 定义 | §2.3 开头 | 以奠基性权威支持 oracle problem/relations among executions 的定义。 | U2 foundations audit 验证了 `chen2018metamorphic`；`source/references.bib` 包含 survey；未发现对占位符要求的 Chen/Cheung/Yau 原始条目进行准确审计的仓库记录。 | 决定 survey 是否足够，或授权另行检索原始表述。 |
| Data-mutation-directed MR studies | §2.3 末段 | 将用于 MR acquisition 的 data/relation mutation 与 paired program mutant 区分开。 | round85 refs 15–18；`source/references.bib` 中的 `sun2016mumt` 和后续 data-mutation/datamorphic 条目；理论备忘录 §§MR-neighbor evidence | 批准哪些已审计谱系条目适用于 P3，并授权语义对齐检查。 |
| 软件工程实验的 construct-validity guidance | §2.4 | 为 construct-validity 术语以及 proxy/label mismatch 的解释提供依据。 | 未发现专门的已验证 bibliographic lead；仅存在内部 study-design 对“construct validity”的使用。 | 作者决定是否授权定向文献检索。 |
| 多项目软件研究的 hierarchical/project-clustered inference | §2.4 | 为拒绝把 cell/pair 当作 project replication，以及要求 project-level uncertainty 提供依据。 | 内部 governing plan 和 RQ2 handoff 规定了分析边界，但未发现已验证的外部方法学引用。 | 作者决定是否授权定向方法学检索。 |
| 用于 construct comparison 的具名 semantic-mutation operator | Threats：Construct validity | 用于比较 P3 的 contract-bound construct 与既有 semantic-variation/operator construct。 | round85 refs 12–14；`source/references.bib` 中 Clark/Dan/Hierons 和 Derezińska/Zaremba 条目；理论备忘录 | 批准一个有界的 construct-comparison 引用集合；不得自动与一般谱系缺口合并。 |

## 需要作者决定的事项

- [ ] 接受或修改当前标题
- [ ] 接受 RQ2 的当前缩小范围
- [ ] 接受 C3 不作为当前论文主贡献
- [ ] 接受 NumPy 为唯一 paired-evidence project
- [ ] 接受 Stage I 只作为 applicability census
- [ ] 确认 TOSEM 是否为目标期刊
- [ ] 决定是否授权下一任务联网检索 6 个 citation gaps
- [ ] 确认作者姓名
- [ ] 确认单位
- [ ] 确认 CRediT
- [ ] 确认 funding
- [ ] 确认 conflict of interest
- [ ] 确认 ethics wording
- [ ] 确认 AI-use disclosure 路径
- [ ] 确认 Data Availability 的公开 URL/DOI 策略
- [ ] 决定是否保留内部中文伴随摘要

本审阅未裁决上述任何事项。

## 经作者批准后建议进行的稿件修订

### `BLOCKING_EVIDENCE_CORRECTION`

无。未发现核心数字或固定 claim authority 矛盾。

### `CLAIM_SCOPE_CORRECTION`

| 稿件章节 | 当前问题 | 建议修改 | 所需作者权限 |
|---|---|---|---|
| §4.1 Subject and defect foundation | 18-group/35-defect 计数有内部线索，但“each recorded with a fixed version”缺少与 JSON-backed claim 同等直接的 locator。 | 添加最强的现有 catalog locator，或采用 path-decision record 中经过审计的准确措辞。 | 批准修改 study-design prose。 |
| 引言贡献清单 | 冻结的 pairing protocol 被表述为一项贡献；这可作为 study design 成立，但不得被理解为提升 ledger C1 或 C3。 | 可在第一项贡献中添加“for this pilot”。 | 批准贡献框架。 |
| Discussion 的 exact-overlap 解释 | “Blocks one cheap objection”有明确边界，但带有修辞色彩。 | 改写为明确推断：这 4 个 pair 排除了 exact identity，但没有排除更广义的 construct equivalence。 | 批准修订解释性正文。 |

### `CITATION_COMPLETION`

| 稿件章节 | 当前问题 | 建议修改 | 所需作者权限 |
|---|---|---|---|
| §§2.2–2.4 和 Threats | 仍有 6 个 citation gap。 | 在现有线索充分时从中选择来源；仅对未解决缺口授权有界的外部检索。 | 来源选择/检索授权。 |
| §2.2 Jia & Harman 2009 句子 | 现有 audit 没有确立准确的“default set does not express”表述。 | 对照原文核验，或弱化为审计记录直接支持的表述。 | 批准核验或弱化。 |
| §2.2 Tip et al. 2024 句子 | 仓库 audit 没有对“outside a fixed operator list”进行语义验证。 | 对照论文核验，或收窄为“uses an LLM to generate mutants”。 | 批准核验或收窄。 |

### `STRUCTURAL_REVISION`

| 稿件章节 | 当前问题 | 建议修改 | 所需作者权限 |
|---|---|---|---|
| Discussion | Observation、interpretation、limitation 和 governance/future boundary 相互交织。 | 在不引入新 claim 的前提下重排四个层次。 | 批准结构修订。 |
| 全文 | 目标期刊尚未确认。 | 在确认期刊前，推迟 TOSEM 特定的章节顺序、篇幅限制、引用格式和披露调整。 | 目标期刊决定。 |

### `STYLE_ONLY`

| 稿件章节 | 当前问题 | 建议修改 | 所需作者权限 |
|---|---|---|---|
| 全文 | “artifact/artefact”、数字/单词和 code-token 规范可能不一致。 | 在实质性作者裁决后进行一次一致性检查。 | 批准 style pass。 |
| Evidence comments | 内部 HTML comments 对审计有用，但可能不适合投稿版本。 | 决定是否在 source 中保留，并只在派生的 submission build 中移除。 | 投稿 source 策略。 |

### `AUTHOR_METADATA`

| 稿件章节 | 当前问题 | 建议修改 | 所需作者权限 |
|---|---|---|---|
| Title page / Author Contributions | 姓名、单位和 CRediT 仍为占位符。 | 只使用作者提供的事实填写。 | 作者事实确认。 |
| Conflict / Funding / Ethics | 声明未解决或仍属暂定。 | 根据作者/机构事实和最终 artifact-license review 填写。 | 作者/机构确认。 |
| AI-use / Data Availability | 目标期刊政策和公开仓库/DOI 路径未解决。 | 在目标期刊和发布策略决定后完成。 | 目标期刊与发布授权。 |

## 对齐结论与里程碑偏离检查

- Evidence conflict：未发现。
- Claim overreach：未发现明显的核心实证 overreach。两处 related-work 表述需要语义验证或收窄，另有两处稿件表述被明确归类为 authorial interpretation。
- C3：`blocked`。
- `n_projects`：1。
- Stage II candidates：0。
- 是否重开 Stage I/II：否。
- 是否启动自动 peer-review panel：否。
- 是否重写 manuscript：否。
- 是否推断或勾选作者拥有的决定：否。
- 是否新增无证据支持的科学 claim：否；本报告只包含审计发现和建议。
- 科学里程碑路径：仍位于当前论文的作者审阅和证据对齐路径，没有重开实验路径。

## 下一步

`AUTHOR_ADJUDICATION_REQUIRED`

下一步属于作者。本审阅不授权稿件修订、引用检索、目标期刊选择或元数据填写。
