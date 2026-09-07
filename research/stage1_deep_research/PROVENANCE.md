# Stage 1 Deep Research — 检索溯源说明

本目录保存 P3 v4 论文构思阶段（2026-09-07）的全部 Stage 1 产出。本文件解释目录中两个工具目录的性质，避免后续会话把它们误判为可随手删除的临时垃圾。

## 1. 交付物（正式产出）

| 文件 | 阶段 | 裁决 |
|---|---|---|
| `phase1_rq_brief_provisional.md` | Phase 1a | 临时 RQ + FINER（Novel 已二次下调至 2/5） |
| `phase2_bibliography_A_mr_adequacy.md` | Phase 2 主题 A | `PARTIAL`——「MR 充分性无可信测量」不成立，须窄化 |
| `phase2_bibliography_B_mutation_constructs.md` | Phase 2 主题 B | 术语冲突 + 构念错位论证的强反证 |
| `phase2_bibliography_C_structure_preservation.md` | Phase 2 主题 C | `DIRECT_PRIOR_ART`（本组自己的两篇预印本） |
| `phase2b_audit_consolidation.md` | Phase 2b | ✗=0 / △=68 / 收录 139 |
| `phase3_gap_synthesis.md` | Phase 3a | `INCREMENT_INSUFFICIENT` + O 分量两处设计硬伤 |
| `phase3b_put_population_feasibility.md` | Phase 3b | 满足五项硬要求的求解器总体**不存在**（R1∩R2 绑定） |
| `phase3c_cxx_route_cost_assessment.md` | Phase 3c | 放宽 R1 的 C++ 路线成本与相似度裁决 |

## 2. `_tools/` 与 `.tools/` 的性质：**溯源证据，不是临时文件**

### 为什么存在

Phase 2 执行期间 `user-paper-search` MCP namespace 无法加载（`~/.cursor/mcp.json` 存在 JSON 语法错误——`undermind` 条目前缺逗号）。为满足项目规则 §7 的 paper-search-first 政策、避免降级到 WebSearch，两个 agent 各自写了直连驱动，**在进程内调用 MCP 工具所包装的同一批 searcher 类**（`paper_search_mcp.academic_platforms.*`），因此走的是同一条代码路径与同一批上游 API。

| 文件 | 作用 |
|---|---|
| `_tools/ps.py` | 主驱动。支持 `<tool> <query> [n]`、`doi <doi>`、`batch <jsonfile>` 三种模式；记录 `elapsed` 与 `status`，异常不吞（写入 `error` + `trace`） |
| `.tools/psearch.py` | 等价驱动，直接解析 FastMCP 的 `FunctionTool` 包装 |
| `.tools/batch_search.py`、`.tools/abs_search.py` | 批量与摘要检索封装 |
| `*/q_*.json`、`*/batch_*.json`、`*/titles_*.json` | 检索批次的**输入**（查询串、工具选择、DOI 列表） |
| `_tools/out_*.json` | 检索批次的**原始返回**（约 310 KB） |
| `_tools/err_*.txt` | 对应批次的 stderr |

### 为什么必须保留

1. **审计表溯源**：`phase2b_audit_consolidation.md` 报告的 ✗=0 与 △=68 直接由 `out_*.json` 支撑。删除后审计表退化为不可核验的断言。
2. **工具失效的独立复现记录**：`search_dblp` 与 `search_semantic` 全程返回空载荷。`err_*.txt` 与 `out_*.json` 是该失效的一手证据，也是「主题 A 对抗性检索 A3 与 Chan et al. 1998 核实待 dblp 恢复后重跑」这条未决项的依据。
3. **§9.4 数据归档规则**：原始实验输出属 Raw 类别——只读、版本化、永不修改。

### 已知遗留

- 两个目录功能重叠（两个 agent 并行各写一份）。**不要合并**——按 §9.2，重复目录保留其一为 canonical、另一个移 `archive/`，不做内容合并；此处两份的批次不同，合并会破坏批次与返回的对应关系。
- `.tools/` 是点目录，在 `ls` 下不可见，容易被后续会话遗漏。
- `__pycache__/` 已由 `.gitignore` 屏蔽，不入库。

## 3. 未决检索任务

- `search_dblp` 恢复后重跑：主题 A3 对抗性检索、Chan et al. 1998 核实
- 精读三篇无摘要/决定性文献：Xie 2024 MUT Model、Fu 2024 全文、Yan & Zhu 2025
- 精读 Clark / Dan / Hierons 原文 SCP 78(4):345–363（四条检索路径均未取到全文，现有结论基于后继论文摘要）
