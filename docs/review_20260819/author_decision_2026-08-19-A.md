# Author decision 2026-08-19 — ESCALATE_AUTHOR = A

- Reviewer: 评审模型（流程总控）；本会话不改生产代码
- Trigger: C1 on `docs/review_20260819/2026-08-19-003_review.md`
- Author reply (verbatim intent): `ESCALATE_AUTHOR：选择A`
- Recorded: 2026-08-19
- Reviewer commit parent: `4b4734a1`
- Post-004 C1 commit: `e9cdbf32`

## Decision

**(A)** P2-C remainder and P2-D stay **blocked** until both exist
**outside** this dual-agent loop:

1. an extracted tree (or hash-matching local archive) for a pinned
   `EXECUTABLE` subject; and
2. a process-argv execution seam that can produce a usable profiling
   trace without inventing cmake / P12-download / a new profiler
   framework inside this loop.

**(B)** is rejected: booking the remaining frozen rows as the same
honest-missing terminals, while cmake and download remain forbidden,
is ledger thickening and would not feed `L_t`/`U_t`.

## What stays closed

| Slice | Status |
|---|---|
| P2-A minimum (1/35 `PREFLIGHT_ONLY`) | closed (`PASS_WITH_DISCLOSURE`) |
| P2-B minimum (synthetic `PILOT_ONLY` PASS+FAIL) | closed (`PASS_WITH_DISCLOSURE`) |
| P2-C header row (`72e1a3e8…`, packet 003) | closed (`PASS_WITH_DISCLOSURE`, `E_SOURCE_TREE_ABSENT`) |
| P2-C process-argv row (`13b2cddc…` / `["ltest"]`, packet 004) | closed (`PASS_WITH_DISCLOSURE`, `E_SOURCE_TREE_ABSENT`; C1 `docs/review_20260819/2026-08-19-004_review.md`) |

## What stays open / blocked

| Target | Status |
|---|---|
| Real `ltest` spawn (one-archive fetch + cmake `--target ltest`) | 005 **closed** as `E_ARCHIVE_FETCH_FAILED` (P12 404); cmake/spawn still blocked |
| P2-C remainder (other frozen rows) | **blocked** until (1); do not book as missing-only copies |
| P2-D (`L_t`/`U_t` / primary technique) | **blocked** (no usable traces) |
| P2-E / P2-F | later |
| Phase 2 as a whole | open |
| Claims | `blocked` |

Condition (2) after packet 004: process-argv seam exists in-repo
(`scripts/p3_v3/run_p2c_process_row.py`, PR #25). Condition (1) for this
pinned subject is now authorized as packet 005 (one archive + cmake
`--target ltest` + that tree's build deps). Other rows stay blocked.

## Process state

- **After 003:** author string `P2C_TREE_AND_PROCESS_ARGV_SEAM_READY=yes` licensed packet 004.
- **After 004 C1:** `WAIT` (no tree). Packet 004 booked `E_SOURCE_TREE_ABSENT`.
- **After `P2C_EXTRACTED_TREE_PRESENT_ON_EXECUTOR_VM=yes`:** refused (no disk tree). Record `author_string_2026-08-19-tree-present-refused.md`.
- **After author exception (one archive + cmake/deps for this subject):**
  packet 005 issued.
- **After 005 C1:** fetch booked `E_ARCHIVE_FETCH_FAILED` (P12 404).
  C1 `docs/review_20260819/2026-08-19-005_review.md`. No packet 006.
  **WAIT** until `P12_ONE_ARCHIVE_REACHABLE=yes` plus independent
  confirm of clone access or matching tar digest.
- **Cursor VM while waiting:** `docs/review_20260819/cursor_vm_instruction_wait_p2c_hold.md`
- C2 is **not** due.

## §10.1

| 处置 | 分类 |
|---|---|
| 接受 (A)，拒绝 (B) | 效度修复：保护推断，不把空 trace 台账伪装成 P2-C/P2-D 进度 |
| 不另开下载/cmake 包 | 反基础设施复发 |

主张收缩清单：空。P2-C 余量与 P2-D 仍在菜单上，只是停在循环外前置条件。

## Reviewer 2 视角的最严苛审稿意见

- [方法论] 无 process-argv 执行缝则不能算技术区间。HOLD 正确。
- [外部效度] 未用 1 行缺失外推。
- [统计选择] 未授权只登记易关的缺失行。
- [基准] 未重新打开 cmake / Boost.Math。
- [霍桑] 未改 Phase 1 选择集。

Reviewer 2 视角扫描通过——5 类维度均无 publication blocker。
