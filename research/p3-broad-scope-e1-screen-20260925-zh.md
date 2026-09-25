# 较广语义范围的 E1 入口筛查（2026-09-25）

性质：一次限界资料核对。未运行变异或 MR，未执行两版程序。  
v4 确认性实验保持 **NO-GO**。本裁决只回答“是否值得进入 E1 实作”，不等于 E1 完成，也不等于确认性实验 GO。  
依据：`docs/STATE.md` §1.6、§7；`research/p3-minimal-theory-v1-zh.md` §6.3–6.4。较广范围若立项，必须另定总体、分母和 RQ。

**裁决：可进入 E1 实作。** 两个项目都有可定位的修复链、一条可陈述的语义要求、一个不调用被测算法的认证设想，以及可安装的 Python 接口。认证器本身尚未实现，故 E1 仍未通过。

---

## NetworkX

| 项 | 记录 |
|---|---|
| 仓库 | https://github.com/networkx/networkx |
| 线索 | 合并的 PR [#8425](https://github.com/networkx/networkx/pull/8425)，只追溯这一条 |
| 修复提交 | `772c8dcf1f615e239511277ee90241f3396c7648`（2025-12-23，已合入标签 `networkx-3.7` 的历史） |
| 修复前版本 | 第一父提交 `dba6e0fade37fc8a649ae31a9ec4f27a78773482`（2025-12-23）。它在 `networkx-3.6.1` 之后 23 个提交，且不包含该修复 |
| API | `networkx.algorithms.shortest_paths.dense.floyd_warshall_predecessor_and_distance` |
| 源码 | `networkx/algorithms/shortest_paths/dense.py` 的 `_init_pred_dist`：修复前先写 `dist[u][u]=0`，再把自环权写入同一格；修复后先写边权，再把对角线置 0 |

语义要求：

\[
r_{\mathrm{FW}}=(\phi,D,\kappa,B,O)
\]

- \(\phi\)：边权均非负时，每个顶点到自身的最短路距离等于空行走的代价 0。正权自环不能把它改大。
- \(D\)：有限无向或有向简单图，外加权为正的自环；权重为整数或有理数。本条不覆盖负权或负环。
- \(\kappa\)：精确。
- \(B\)：绝对差 0。
- \(O\)：只读图的边权。若存在负权则返回 \(\mathsf{CERT\_INCONCLUSIVE}\)。若全部边权 \(\ge 0\)，独立结论是 \(d(u,u)=0\)，再与被测 API 的 `dist[u][u]` 比较。它不调用 Floyd–Warshall，也不读取任何 MR 的 PASS/VIOLATED。

缺陷是否触及 \(\phi\)：触及。PR 给出 `G.add_edge(0,0,weight=5)` 时期望 `dist[0][0]==0`，修复前断言得到 5。测试补丁在 `test_zero_distance` 中加入正权自环 `("x","x",3)`。

最小运行依赖：CPython 与对应提交的 NetworkX（纯 Python）。不需要 BLAS 或编译扩展。

候选 MR 方向（未在缺陷版上运行）：加入一条正权自环后，`dist[u][u]` 应与无自环时相同。这是两次调用被测 API 的关系。\(O\) 只读边权并套用空行走定义，不比较两次 API 输出。

尚未核实：没有签出两版并运行。未追溯后续讨论 [#8576](https://github.com/networkx/networkx/issues/8576)。负权自环被修复代码强制写成 0，所以 \(D\) 必须停在非负权；这一点没有跑测试确认。

## SymPy

| 项 | 记录 |
|---|---|
| 仓库 | https://github.com/sympy/sympy |
| 线索 | issue [#28186](https://github.com/sympy/sympy/issues/28186) 与其修复 PR [#28189](https://github.com/sympy/sympy/pull/28189)，只追溯这一条 |
| 修复提交 | 合并提交 `b4b30c276093345697da9ade1e94c39e76dc6b38`（2025-07-09）。发行说明指向 1.15，不在已发布的 `1.14.0` 中 |
| 修复前版本 | 合并的第一父提交 `b3b1f28efdc16d7643f536a08b26eaa174723e36`（2025-07-09）。标签 `1.14.0`（`fe935ceb303891d1f8bea4c03b19fd9ec9464b02`）是它的祖先，issue 作者在 1.14.0 上报告失败 |
| API | `sympy.integrate` 进入的有理函数路径 `sympy.integrals.rationaltools.ratint` / `log_to_real` |
| 源码 | `sympy/integrals/rationaltools.py`。PR 同时改了 `sympy/polys/polyroots.py` 的 `roots_binomial` |

语义要求：

\[
r_{\mathrm{rat}}=(\phi,D,\kappa,B,O)
\]

- \(\phi\)：对分母在区间上无零点的有理函数，返回的表达式 \(F\) 应满足微积分基本定理：\(F(b)-F(a)\) 等于该区间上被积函数的定积分。
- \(D\)：issue 中的具体族，实符号代入固定实数后的有理函数，以及维护者给出的 \(1/(a x^2+b x+c)\)（\(a,b,c,x\) 为实数，判别式使区间内无实极点）。固定区间取 \([0,1]\)。
- \(\kappa\)：数值近似。
- \(B\)：绝对差 \(10^{-8}\)（开发用预算，尚未预注册）。
- \(O\)：用 mpmath 的高精度求积计算 \(\int_0^1 f\)，与 \(F(1)-F(0)\) 比较。求积不调用 `integrate` 或 `ratint`。被测 API 只负责产生 \(F\)。\(O\) 不读取 MR 判定。

缺陷是否触及 \(\phi\)：触及。维护者在 issue 中记录，实符号下 `ratint` 丢掉分母根，`integrate(1/(a*x**2+b*x+c), x)` 得到 0；原例子在代入 \(x=1\) 后，错误原函数的导数不能还原被积函数。PR 说明 `log_to_real` 因根集不完整而丢掉积分项。区间 \([0,1]\) 上 \(1/(x^2+1)\) 的定积分不为 0，故常数 0 不能通过上述 \(O\)。该数值比较尚未执行。

最小运行依赖：CPython、对应提交的 SymPy，以及其自带的 mpmath。不需要外部编译库。

候选 MR 方向（未在缺陷版上运行）：先把实参数代入再积分，与先积分再代入，两个结果在固定点上应一致。这是两次调用 `integrate`。\(O\) 用独立求积对照一个原函数的端点差，不把另一次 `integrate` 当作裁判。

尚未核实：没有安装 1.14.0 与合并提交并运行求积。PR 还改了 `roots_binomial`，该部分是否为这条 \(\phi\) 所必需，未拆开核对。\(B=10^{-8}\) 只是筛查用数字。

## 边界

- 两例都是公开缺陷，只能作为可行性开发材料，不能计入确认性检出率。
- 未给出检出率、跨项目效果或论文结果。
- 未改 P12 发布，未改 P3 consumer lock，未改 v4 的 NO-GO。
- E1 仍须在后续实际运行这两个认证器后另行判定。E2–E7 未开始。
