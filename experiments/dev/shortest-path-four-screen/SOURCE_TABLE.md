# 最短路径四项目来源筛查

日期：2026-09-25。未运行 MR 或变异。未改 P12 发布或 P3 锁。确认性实验仍为 NO-GO。未重开 NetworkX／SymPy 窗口。

输入域（四项相同）：2–6 个顶点、正整数边权、无重边的有向图。要求：不可达为无穷大，`d(v,v)=0`，其余距离可由简单路径枚举认证。未核实的条件标为未决，不计入候选。

**结论：结束这组候选的路线。** 没有任何两个项目各有一条合格修复链，因此不值得投入双版本实作。这不是 E1 通过，也不是确认性实验 GO。本窗口不能推断其他项目或其他文件不存在样本。

| 项目 | 接口 | 审查数 | 合格 | 未决 | 版本对 | 构建风险 | 证据窗口 |
|---|---|---:|---:|---:|---|---|---|
| python-igraph | `distances` | 30 | 0 | 0 | 无 | 未进入实作。绑定 C 核心，构建依赖编译工具链 | [distances.c](https://github.com/igraph/igraph/commits/main/src/paths/distances.c) |
| rustworkx | `floyd_warshall` | 30 | 0 | 0 | 无 | 未进入实作。需要 Rust 与 PyO3 | [src/shortest_path](https://github.com/Qiskit/rustworkx/commits/main/src/shortest_path) |
| SciPy | `sparse.csgraph.shortest_path` | 30 | 0 | 0 | 无 | 未进入实作。需要编译 csgraph 扩展 | [_shortest_path.pyx](https://github.com/scipy/scipy/commits/main/scipy/sparse/csgraph/_shortest_path.pyx) |
| NetworKit | APSP | 11 | 0 | 1 | 无 | 未进入实作。需要 C++ 构建；该文件历史短于 30 条 | [APSP.cpp](https://github.com/networkit/networkit/commits/master/networkit/cpp/distance/APSP.cpp) |

排除与未决的具体提交只写在 `screener-only.md`。面向后续 MR 设计：四项资格数量均为 0；NetworKit 另有 1 条未决，不能取得已核实的两版。
