# Author string refused — 2026-08-20 P12 reachable

- Reviewer: 评审模型（流程总控）；本会话不改生产代码
- Received (verbatim): `P12_ONE_ARCHIVE_REACHABLE=yes`
- Authority that named this string: C1 `docs/review_20260819/2026-08-19-005_review.md` @ `294d8f27`
- Independent check time: 2026-08-20 (this reviewer VM)
- Packet issued: **none** (no 006, no same-404 retry)

## Why the string is not accepted

C1 required an independent confirm of clone access **or** a matching
local tar **before** a cmake/spawn retry. The string licenses the
reviewer to look; it does not grant GitHub access or create a file.

Packet 005 already booked `E_ARCHIVE_FETCH_FAILED` after a sparse
clone 404 (`e6acee9d`). Re-issuing that attempt is ledger thickening.

## Independent check (this C1-gate)

| Check | Result |
|---|---|
| `test -e data/p3_v3/p12_intake/extracted` | `EXTRACTED_ABSENT` |
| `test -e data/p3_v3/p12_intake/archives` | `ARCHIVES_DIR_ABSENT` |
| `test -e …/archives/1f67b3f3….tar` | `TAR_ABSENT` |
| `gh api repos/meng004/P12-Defect4MR` | HTTP 404 |
| `git ls-remote https://github.com/meng004/P12-Defect4MR.git d57fa811…` | `remote: Repository not found` |
| last executor (packet 005) | `E_ARCHIVE_FETCH_FAILED` |

## Process verdict

**`WAIT` continues.** Do not issue `execution_packet_2026-08-19-006`.
Do not pull 35 archives. Do not treat a second paste of the same
string as new evidence.

## What would count next (any one)

1. This reviewer VM can `git ls-remote` the pinned commit (non-empty
   SHA line, not “not found”).
2. File
   `data/p3_v3/p12_intake/archives/1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.tar`
   exists here with SHA-256
   `c7c3d38533c01a7366d2511497082af5f30f510d0f95db822d98441a06a1898c`.
3. Author attaches **named** executor evidence (bcId + `ls-remote` or
   `sha256sum`) showing (1) or (2) already succeeded. A new empty VM
   is not evidence.

Access work (org invite, deploy key, placing the one tar) happens
**outside** this dual-agent science loop.

## §10.1

| 处置 | 分类 |
|---|---|
| 拒绝在 404 未变时签发 cmake/spawn retry | 效度修复 |
| 不把口头 yes 当成可达 | 效度修复 |

主张收缩清单：空。真实 `ltest` spawn 仍在菜单上。

## Reviewer 2 视角的最严苛审稿意见

- [方法论] 口头 REACHABLE 后独立 `ls-remote` 仍失败。再开包只会再记 4(a)。
- [外部效度] 未用 404 外推。
- [统计选择] 未授权其余行失败副本。
- [基准] 未拉 35 包；未打开资格认证。
- [霍桑] 未改选择集。

Reviewer 2 视角扫描通过——5 类维度均无 publication blocker。
