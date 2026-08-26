<claude-mem-context>
# Memory Context

# [MT完备性] recent context, 2026-04-28 8:02pm GMT+8

No previous sessions found.
</claude-mem-context>

## 科学关键路径与模型状态机

以“真实实验终态 → 正式 profiling → RQ 证据”为最高优先级。测试、合同、资格验证、review 和运行治理只保留完成当前实验切片所需的最小部分；它们不能作为独立目标持续扩张。

| 状态 | 适用任务 | 默认模型 / 推理 |
| --- | --- | --- |
| 机械执行 | 固定命令、diff、哈希、日志收集、状态摘要、等待、已选定的测试 | `gpt-5.6-luna / low` |
| 有界工程判断 | 最小实现、相关测试范围、版本消歧、既有规格核对、一次性运行 preflight | `gpt-5.6-terra / medium` |
| 科学判断 | 科学转场、跨模块疑难归因、profiling 数据解释与 RQ 结论 | `gpt-5.6-sol / high` |

- 从最低足够状态开始；只有出现证据冲突、跨模块因果不明或科学结论风险时才升级。高推理完成判定后必须立即降回低状态；`xhigh` 仅在一次 `sol/high` 分析仍无法消歧时使用，默认不使用 `max`。
- 一次性运行严格分离：`terra/medium` 绑定既有授权与精确命令，`luna/low` 原样执行，`terra/medium` 机械归类，只有是否进入 profiling 的科学判定使用 `sol/high`。
- 不因机械步骤追加设计、计划、合同、schema、hash、gate、review 轮次或全量测试。若某项工作不能直接产生本轮运行证据、解除 profiling 的实质阻断或解释 profiling 数据，则停止并进入 backlog。
- 当前 Attempt-2 的唯一顺序是：核实本轮可审计的原始运行证据 → 固定 PASS/FAIL/TIMEOUT/infrastructure 终态且不重试 → 回到正式 profiling。实现、测试、verdict 和授权材料仅计工程准备，不计科学进度。
