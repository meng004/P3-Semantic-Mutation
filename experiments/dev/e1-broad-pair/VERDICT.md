# 逐版本判定

设计固定于 `DESIGN.md`。四次运行均未改输入、顺序或容差。v4 确认性实验仍为 NO-GO。本表不是确认性样本。

Python 均为 3.14.5。求积自检：`self_check_abs 0.0`，通过。

| 臂 | 退出码 | 判定 | 导入路径 | 观测 |
|---|---:|---|---|---|
| NetworkX 修复前 `dba6e0fa…` | 1 | `CERT_BREAK` | `venvs/nx-pre/.../networkx/__init__.py` | 控制图 `dist[0][0]=0`；自环权重 5，`dist[0][0]=5` |
| NetworkX 修复后 `772c8dcf…` | 0 | `CERT_HOLD` | `venvs/nx-post/.../networkx/__init__.py` | 控制图通过；自环 `dist[0][0]=0` |
| SymPy 修复前 `b3b1f28e…` | 1 | `CERT_BREAK` | `venvs/sy-pre/.../sympy/__init__.py` | 代入前 \(F=0\)；\(\lvert F(1)-F(0)-\int\rvert=\pi/4>10^{-8}\) |
| SymPy 修复后 `b4b30c27…` | 2 | `EXEC_FAIL` | `venvs/sy-post/.../sympy/__init__.py` | 代入前已得到含 `log` 的 \(F\)；代入后为 `-I*log(t-I)/2+I*log(t+I)/2`。`evalf(80)` 含虚部尾巴，`mpmath.mpf` 拒绝该字符串，没有端点差 |

原始日志：`logs/{nx-pre,nx-post,sy-pre,sy-post}.{stdout,stderr,exit}`。

**开发阶段可执行性：未通过。** NetworkX 两版有区分。SymPy 修复前呈现预定破缺，修复后认证器没有给出数值，不能记为 `CERT_HOLD`。E2–E7 与 v4 的 NO-GO 不变。
