# E1 开发载体：NetworkX 与 SymPy 认证器

性质：开发阶段可执行性。v4 确认性实验保持 NO-GO。两条公开缺陷不转为确认性样本。E2–E7 不因本次改变。

运行前固定。观察结果后不改输入、计算顺序或容差。不运行 MR、语法变异或其他缺陷版本。认证脚本不读取 MR 的 PASS/VIOLATED。

## 四个版本

| 臂 | 提交 |
|---|---|
| NetworkX 修复前 | `dba6e0fade37fc8a649ae31a9ec4f27a78773482` |
| NetworkX 修复后 | `772c8dcf1f615e239511277ee90241f3396c7648` |
| SymPy 修复前 | `b3b1f28efdc16d7643f536a08b26eaa174723e36` |
| SymPy 修复后 | `b4b30c276093345697da9ade1e94c39e76dc6b38` |

每个版本单独虚拟环境，从该提交安装。日志记录提交号、`sys.version` 和实际 `__file__`。

## NetworkX

线索：PR #8425。不测负权自环。

1. 控制图：无向边 `(0,1)`，权重 `1`。调用 `floyd_warshall_predecessor_and_distance`。调用必须返回，且 `dist[0][0]==0`。失败则本次为 `EXEC_FAIL`，不给出 `CERT_BREAK`。
2. 目标图：一个顶点 `0`，正权自环权重 `5`。认证器只检查输入边权均 `>=0`。若出现负权，`CERT_INCONCLUSIVE`。独立期望是空行走代价 `0`。比较 `dist[0][0]` 与 `0`，绝对差阈值 `0`。
3. `dist[0][0]==0` 为 `CERT_HOLD`，否则 `CERT_BREAK`。

退出码：`CERT_HOLD` 为 0，`CERT_BREAK` 为 1，`EXEC_FAIL` 或 `CERT_INCONCLUSIVE` 为 2。

## SymPy

线索：issue #28186 与 PR #28189。`roots_binomial` 的其他变化不并入本要求。

1. 先用 mpmath 以 80 位精度求 \(\int_0^1 1/(1+t^2)\,dt\)。与 \(\pi/4\) 的绝对差必须 `< 10^{-8}`。自检失败则为 `CERT_INCONCLUSIVE`，且不得用该求积裁判被测结果。
2. 实符号 `a,b,c,t`。**先** `F = integrate(1/(a*t**2+b*t+c), t)`，**后**代入 `a=1,b=0,c=1`。
3. 用表达式数值求值计算 `F(1)-F(0)`。参考值只用步骤 1 的求积。禁止调用 SymPy 的 `integrate` 或 `diff` 来产生参考值。
4. 绝对容差 `10^{-8}`。差小于容差为 `CERT_HOLD`，否则 `CERT_BREAK`。被测调用抛错为 `EXEC_FAIL`。

退出码与 NetworkX 相同。

## 预期角色

修复后版本若满足上述固定规则，应为 `CERT_HOLD`。修复前版本若呈现预定破缺，应为 `CERT_BREAK`。这只说明要求与认证方法在这两个公开案例上可执行且有区分力。
