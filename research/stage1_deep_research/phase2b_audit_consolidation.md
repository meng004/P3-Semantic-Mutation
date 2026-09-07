# Phase 2b — 三路检索审计汇总

**日期：** 2026-09-07
**门槛（项目规则 §3 步骤 2）：** ✗ = 0；△ ≤ 5 且每条有合理解释
**裁定：** ✗ 门槛**通过**；△ 门槛**形式上不通过**，但性质与规则预设不同——见 §3。

---

## 1. 三份交付件

| 主题 | 文件 | 收录 | ✓ | △ | ✗（收录项中） | 因无法核实而排除 |
|---|---|---|---|---|---|---|
| A — MR 充分性 | `phase2_bibliography_A_mr_adequacy.md` | 44 | 24 | 20 | **0** | 2 |
| B — 变异构念 / mutation score 效度 | `phase2_bibliography_B_mutation_constructs.md` | 57 | 71 | 23 | **0** | 5 + 1 重复 + 1 自引 |
| C — 保结构与先例前沿 | `phase2_bibliography_C_structure_preservation.md` | 38 | 13 | 25 | **0** | 4 |
| **合计** | | **139**（含跨主题重复） | | | **0** | **11** |

B 的 ✓/△ 计数基于 94 行审计表（收录 57 项中有版本对与补充项）。

跨主题重复条目（同一文献在多份中出现，Phase 3 需去重）：Fu et al. (2024) 见 A3.1 与 C3.11；Kanewala & Bieman (2014) 见 A2.4 与 C2.7；He et al. (2020) 见 A2.7 与 C5.3；Chen, Feng & Tse (2002) 见 A2.5 与 C3.7；Yan & Zhu (2025) 见 A2.8 与 C3.6；Hook & Kelly (2009) 见 B 与 C3.8。

## 2. 三份裁决

| 主题 | 裁决 | 后果 |
|---|---|---|
| A | **`PARTIAL`** | 「MR 充分性无可信测量」被证伪。Fu et al. (2024)、Liu et al. (2024) 均以「MT 测试充分性准则」为名发表。主张须收缩为「无以外部义务空间为分母的测量」。 |
| B | **术语碰撞 + 强反证** | 详见 §2.1。三项后果：命名冲突、SLRMA 的评价形状有 1985/2009/2021 三条更近的先例、mutation score 构念效度的负面结果本身被方法论反驳。 |
| C | **`DIRECT_PRIOR_ART`** | SPTM / SLRMA 已被本组自己的 arXiv:2605.17437 占据，完备性理论层已被 arXiv:2606.08269 占据。已裁定 v4 走 supersede 路线，四条硬约束见 `docs/STATE.md` §1.1。 |

### 2.1 主题 B 的三项后果（约束 2 撤回后分量加重）

约束 2 撤回后，v4 的新颖性改对**外部文献**衡量。主题 B 恰好刻画的就是这块外部文献，而它比预想拥挤。

**(a) 术语冲突。** 「Semantic Mutation Testing」已被 Clark, Dan & Hierons (2010 ICSTW; 2013 SCP 78(4):345–363) 占用，指**变异语言的解释函数而程序文本不动**，模拟的故障类是「程序员误解语言/平台语义」。该谱系活跃且已扩展到 UML 状态机语义变体、并发内存模型、多智能体平台、解释器（Cazzola & Favalli 2023 JSS）。最要命的是 **Dan & Hierons (2012b, ICST 290–299)《Semantic Mutation Analysis of Floating-Point Comparison》**——该术语的原创者已经把「semantic mutation」用在数值语义上了。本组 SMS 的「semantic mutation」是完全不同的意思（程序数学语义的领域级变异）。**须改名或设立显式区分小节，二选一，不能沉默。**

**(b) SLRMA 的评价形状有三条更近的先例，且 semantic mutation 不是最近的那条。** 「变异程序、以被声明义务集合漏掉哪些变异体来度量该义务集合的完备性」这一形状：

| 先例 | 年份 | 与 SLRMA 的关系 |
|---|---|---|
| Budd & Gopal，*Computer Languages* 10(1):63–73 | **1985** | 变异**规约**而非程序，判定测试数据能否区分规约与其变异体。方向相反，但同属「变异被声明的义务」家族 |
| Knauth, Fetzer & Felber，ICSTW 182–191 | 2009 | meta-mutation 评估**契约**质量，契约质量 = 能检出哪些变异体 |
| **Knüppel, Schaer & Schaefer，FormaliSE 42–53** | **2021** | 《How much specification is enough? Mutation analysis for software contracts》——变异程序，用规约漏掉的变异体度量**规约完备性**，给开发者「a sense of specification coverage」。**这是 SLRMA 的评价形状本身**，只是义务载体是 JML 契约而非 MR |

Jahangirova et al. (2016 ISSTA / 2021 TSE) 的 oracle assessment & improvement 框架则是「用变异评估 oracle」的参考方法，任何新的 oracle 充分性度量都会被拿来跟它比。

**(c) mutation score 构念效度的负面结果本身被方法论反驳——这是最危险的一条。** 本文若要论证「句法 mutation score 构念错位」，最顺手的引用是 Papadakis et al. (2018, ICSE)「控制测试集规模后相关性很弱」。但：

- **Chen et al. (2020, ASE)** 明确论证「test set size **neither** a confounding variable, as previously suggested, **nor** an independent variable that should be experimentally manipulated」。若此说成立，Papadakis 2018 的负面结果建立在错误的实验设计上。**引 Papadakis 2018 而不处理 Chen 2020，是可预期的审稿攻击点。**
- **Zhang et al. (2024, TOSEM 33(4))**：在 ASSENT 框架下以真实缺陷为基准，「mutation score, and subsuming mutation score are the best metrics to quantify test suite effectiveness」。
- **Lu et al. (2026, TOSEM 35(5))**：回归去除规模混淆后，「mutation score demonstrates superior effectiveness in predicting test suite effectiveness」。
- **Schuler & Zeller (2013, STVR 23(7))**：checked coverage 对 oracle 质量「even more sensitive than mutation testing」——若非变异度量在 oracle 质量上更敏感，审稿人会问为何新度量要建在变异基座上。
- **Wang et al. (2026, TOSEM)**：LLM 变异体真实缺陷检出 77.4% vs 规则式 41.6%。这支持「默认句法算子是弱代理」，但也表明**社区选择的修法是 LLM 生成而非规约推导**，并给出一个很高的实证门槛。

**可用的正面证据**：Gay & Salahirad (2023, ICST) 在 32,002 个变异体 / 144 个真实缺陷上测得**仅 9.92% 的变异体与真实缺陷强耦合**，且耦合度在算子间极不均衡；Ojdanić et al. (2023, TSE) 证明句法相似不预测语义相似；Alblwi et al. (2024, AST) 证明「mutation coverage」的两种合理形式化彼此弱相关。这三条支持「分母在很大程度上是惰性的/非单一构念」，且不依赖真实缺陷论证。

**(d) 变异测试用于科学计算的文献确实稀薄**（约四项：Hook & Kelly 2009 ×2、Gray & Kelly 2010、Dan & Hierons 2012b，加 Delgado-Pérez et al. 2018 的核工业案例）。这是真实空白，对本文有利；但也意味着不能靠 deep search 单独确立「不存在更近先例」。

## 3. △ = 68 的性质说明（为何不按规则 §3 的「△ ≤ 5」处置）

规则 §3 设定 △ ≤ 5 的门槛，预设 △ 表示「存在性存疑」。本轮 68 个 △ 中**没有一个是存在性存疑**——三份交付件均执行了「Undermind 仅作发现、paper-search 独立验真」的双工具分离，任何未能经 paper-search 独立解析的条目都已排除（合计 11 项），而非降级为 △。

△ 的实际成因分布：

| 成因 | 数量级 | 风险 |
|---|---|---|
| Crossref 返回完整书目字段但 `abstract` 为空（IEEE / ACM 会议录、Elsevier 综述尤甚） | 最大宗 | **书目可安全引用；但「Key findings」系据题名/venue/Undermind 摘要归属，非验真所得。** 引用其具体论断前须核对全文。 |
| 与 Undermind 元数据的年份/卷期差异（online-first vs. 定卷） | 约 8 | 低，已逐条更正 |
| 仅有预印本、无 version of record | 约 6 | 中，投稿前须复查是否已正式发表 |
| 无 DOI / DOI 变体 / 畸形 DOI | 约 5 | 低，已更正（如 `10.1109/MET.2017..3` → `10.1109/MET.2017.3`） |

**须在写作前精读全文的高优先条目**（论断被实际引用且当前无摘要）：Xie et al. (2024) MUT Model（唯一在 MR *集合* 上给数的度量，最近结构性竞品）、Ding, Li & Hu (2019) QRS、Di Franco et al. (2017) ASE（若用于论证算子分类的外部效度）。

## 4. 三份共有的系统性缺陷

1. **`search_dblp` 与 `search_semantic` 全程失效**，三个 agent 各自独立遭遇，我亦独立复现（`search_dblp` 对 `mutation testing` 最小对照查询返回空）。dblp 是 SE 会议录的权威索引且是规定链条的第一环，其缺席使会议录长尾（workshop、区域会议、2000 年前论文）系统性欠采样，并直接导致 Chan et al. (1998) 等无 DOI 条目被排除。**dblp 恢复后须重跑 A3 对抗性检索。**
2. **主题 A 的对抗性自由文本检索弱于设计意图**：五次对抗扫描中两次因工具失效、一次因 Crossref 排序噪声而失败，三个决定性命中均来自 Undermind 发现 + DOI 定向解析。唯一干净执行的 OpenAlex 对抗查询立刻新增两个近邻，提示 §4.1 的近邻枚举**很可能不完备**。裁决方向可靠，枚举不可当穷尽。
3. **ASME V&V 20 无法核实**（三次 WebFetch 均 404），核工业与机械工程 V&V 的主导标准谱系因此缺席。C2 标准位由 AIAA R-141-2021 填补。投稿前须从标准机构页或馆藏目录补齐。
4. **保结构领域的非英语先例未触及**：结构保持离散化的中文根源（冯康辛几何学派）未被任何英文查询命中。影响 C1 的归属，不影响 C3 裁决。
