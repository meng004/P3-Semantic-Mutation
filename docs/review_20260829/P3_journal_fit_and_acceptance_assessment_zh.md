# P3 期刊适配度与接收可能性评估

日期：2026-08-29  
评估对象：当前 evidence-aligned P3 稿件，以及恢复“语义变异评价 MR 集合有效性与充分性”原始命题后的拟议版本  
性质：作者侧投稿判断，不是期刊官方录用率

## 结论摘要

1. 当前 evidence-aligned 稿件不适合直接投稿 IEEE TSE 或 ACM TOSEM。它是单项目、四组配对的 pilot，而且正文明确声明“不评价 MR 集合充分性”“不主张语义变异更优”。这与恢复后的旗舰命题之间存在直接的 claim–evidence 缺口。
2. P3 的选题、形式化符号体系和方法论定位与 TOSEM 最匹配；如果补齐实证效度，TOSEM 是首选。
3. TSE 同样高度适配，但通常需要更强的跨项目证据、对软件测试实践更清楚的普遍影响，以及理论与实证两方面同时达到旗舰水平。
4. 分区存在版本差异：公开数据库显示，TSE 和 TOSEM 在 2025 年 3 月中科院升级版均为计算机科学大类 1 区、软件工程小类 1 区；2026 年 3 月“新锐分区”则均显示为大类 2 区、小类 1 区。投稿前必须确认作者单位采用哪一版本。
5. 如果单位硬性要求 2026 新锐分区大类 1 区，Science China Information Sciences 是可考虑选项，但其软件工程主题匹配度低于 TSE/TOSEM，不宜只为分区牺牲审稿人匹配。

## 当前稿件的接收可能性

以下区间是基于稿件成熟度的主观预测，不是期刊公布的录用率。

| 期刊 | 主题适配 | 当前稿件直接投稿 | 完成理论重构但不补实验 | 完成跨项目效度验证后 |
|---|---:|---:|---:|---:|
| ACM TOSEM | 很高 | 低于 5% | 约 3%–8% | 约 15%–25% |
| IEEE TSE | 很高 | 低于 3% | 约 2%–6% | 约 10%–20% |
| Empirical Software Engineering | 高，但偏实证 | 约 3%–8% | 约 5%–12% | 约 15%–30% |
| Information and Software Technology | 高 | 约 5%–12% | 约 10%–20% | 约 25%–40% |
| Journal of Systems and Software | 高 | 约 5%–12% | 约 10%–20% | 约 20%–35% |
| Science China Information Sciences | 中等 | 低于 5% | 约 3%–8% | 约 8%–15% |

“完成跨项目效度验证”至少指：多个项目和 MR 集合、独立或留出的语义变异体、已知质量梯度或真实缺陷外部基准、与句法变异的增量效度比较，以及以项目为聚类单位的分析。它不等同于增加若干输入或在同一项目继续增加 mutant。

## 当前稿件的主要拒稿风险

### 1. 论文主张与现有实验不一致

恢复后的核心主张是“语义变异更适合评价 MR 集合有效性与充分性”，而当前稿件只报告一个 NumPy 项目、四组配对，并明确拒绝把结果解释为 MR adequacy 或一般优越性。审稿人会把这视为旗舰贡献尚未被实验回答，而不是普通 limitation。

### 2. 评价对象没有真正变化

若要评价“MR 集合质量”，实验必须比较多个质量不同的 MR 集合。当前实验主要变化的是 mutant 类型，并未系统改变 MR 集合，因此不能证明指标能够区分完整、弱化、冗余或缺失 MR 集合。

### 3. 缺少外部准则效度

当前的 4/4 与 3/4 只能表明一个局部差异。尚未证明语义变异分数更能预测真实缺陷检测、恢复已知 MR 质量排序，或提供超出句法 mutation score 的增量信息。

### 4. 存在循环验证风险

如果语义变异体根据待评价 MR 本身构造，再用同一 MR 检测这些变异体，较高杀死率可能来自设计耦合。顶级期刊会要求独立构造、held-out MR source，或其他能够切断这一循环的设计。

### 5. 单项目不能支持跨项目推断

五个输入是配对内重复测量，四个 pair 仍属于一个项目。当前设计无法识别项目级不确定性，也不能支持“更适合软件系统中的 MR 集合”这一跨项目命题。

### 6. 形式体系需要证明“有用”，而不只是“可定义”

符号、概念和定义是重要贡献，但 TOSEM/TSE 还会追问：该体系是否具有健全性、单调性、退化兼容性、等价不确定性边界、残余风险分解或其他非平凡性质；这些性质是否产生可检验预测并被数据支持。

## 稿件的竞争优势

- 研究问题重要：传统句法变异与 MR 语义义务之间的构念失配是真正的软件测试测量问题。
- 理论身份清晰：P3 提出符号体系、概念和定义，而不是只提供一组新的 mutation operators。
- 可能形成“理论—度量—实验”闭环，具备 TOSEM/TSE 所需的旗舰贡献潜力。
- 当前工作对配对单位、重复测量、项目聚类和证据边界的处理很克制。
- 冻结协议、证据链和可复现材料是加分项，尤其适合强调方法学可信度的期刊。

## 期刊推荐

### 首选：ACM Transactions on Software Engineering and Methodology（TOSEM）

TOSEM 与恢复后的论文身份最一致。P3 的核心是软件测试评价方法的重新定义：建立语义变异形式体系，定义 MR 集合有效性与充分性的度量，并验证其构念效度和准则效度。这比单纯报告大规模实验更偏“software engineering methodology”。

投稿 TOSEM 的前提是：形式体系成为全文主骨架；至少给出一个具有实质内容的性质或定理群；使用多个质量已知的 MR 集合；通过 held-out 或独立构造避免循环；提供真实缺陷或其他外部质量基准。若这些条件未完成，不建议用当前 pilot 直接试投。

### 第二选择：IEEE Transactions on Software Engineering（TSE）

TSE 的官方 scope 明确包括 well-defined theoretical results、software testing and validation、assessment methods，以及软件过程和产品的 measurement and evaluation，因此主题完全在范围内。相较 TOSEM，TSE 更适合“形式体系已经成熟，而且跨项目实证表明它对软件测试实践具有广泛影响”的版本。

如果后续实验能覆盖多个项目、语言或语义义务家族，并显示语义变异在真实缺陷预测或 MR 集合质量判别上具有稳定增量价值，TSE 可以升为首选。仅凭当前 NumPy pilot，TSE 的 desk-reject/reject 风险高于 TOSEM。

### 分区硬约束选项：Science China Information Sciences（SCIS）

公开的 2026 新锐分区信息将 SCIS 列为计算机科学大类 1 区。其官方 scope 覆盖整个 information sciences，包括 computer science and technology，理论上可以接收软件工程方法论文。但它不是专门的软件工程或软件测试期刊，目标读者和审稿人匹配度不如 TOSEM/TSE。

只有在作者单位明确采用 2026 新锐分区、且“大类 1 区”是不可妥协的行政条件时，才建议优先考虑 SCIS；否则不建议为分区改投主题匹配更弱的刊物。

### 稳健备选：EMSE、IST、JSS

- EMSE 适合把论文改成以跨项目实证效度为中心的版本；当前单项目 pilot 不足。
- IST 与 JSS 对软件测试、质量度量和有验证的技术贡献均有较好匹配，完成中等规模扩展后接收可能性会明显高于 TSE/TOSEM。
- 公开的 2025 中科院升级版信息将 EMSE、IST、JSS 列为计算机科学大类 2 区；若目标必须是大类 1 区，它们只能作为退而求其次的质量选择。

## 推荐的投稿决策

按论文质量与主题适配排序：

1. **TOSEM**：形式化方法与 MR adequacy measurement 为主，首选。
2. **TSE**：完成更广泛跨项目验证后，可作为最高挑战目标。
3. **EMSE**：若最终论文以实证验证为主。
4. **IST / JSS**：若希望在保持高质量软件工程期刊的同时提高现实接收概率。

按分区行政约束排序：

1. 采用 2025 中科院升级版：TOSEM 或 TSE 均为大类 1 区，优先 TOSEM。
2. 采用 2026 新锐分区：TSE/TOSEM 均显示为大类 2 区；若必须大类 1 区，可考察 SCIS，但须接受主题匹配度下降。

## 投稿前的最低科学完成线

1. 将语义变异符号体系、概念和定义确立为第一贡献，并证明关键性质。
2. 分别操作化 MR 集合的“有效性”和“充分性”，不能只用一个 kill rate 同时代表二者。
3. 构造多个具有已知质量梯度的 MR 集合，如完整、删减、弱化和冗余集合。
4. 使用独立或 held-out 的语义变异体，避免 MR—mutant 循环设计。
5. 与位置、成本或执行预算匹配的句法变异基线比较。
6. 引入真实缺陷、独立语义义务或已知 MR 质量排序作为外部标准。
7. 扩展到多个项目，并以项目而不是输入 cell 作为外部推断单位。
8. 证明语义变异评价相对句法 mutation score 具有增量效度。

## 查询口径与来源

- [IEEE TSE Call for Papers / scope](https://www.computer.org/digital-library/journals/ts/cfp-ieee-transactions-on-software-engineering)
- [ACM TOSEM journal page](https://dl.acm.org/journal/tosem)
- [Empirical Software Engineering journal site](https://emsejournal.github.io/)
- [Science China Information Sciences official introduction](https://scis.scichina.com/)
- [TSE 2025/2026 分区信息](https://sci.justscience.cn/details.html?id=2358&sci=1)
- [TOSEM 2025/2026 分区信息](https://www.ablesci.com/journal/detail?id=85mnD9)
- [SCIS 2026 新锐分区信息](https://www.ais.cn/journal/database/7396)
- [EMSE 2025/2026 分区信息](https://www.ablesci.com/journal/detail?id=pLax25)
- [IST 2025/2026 分区信息](https://www.ais.cn/journal/database/3557)
- [JSS 2025/2026 分区信息](https://www.ais.cn/journal/database/5206)

分区网页属于公开二级数据库，不等同于作者单位的正式认定文件。最终应以单位图书馆或科研管理部门采用的版本为准。
