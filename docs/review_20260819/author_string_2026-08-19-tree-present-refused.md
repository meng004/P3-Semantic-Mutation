# Author string refused — 2026-08-19 tree-present

- Reviewer: 评审模型（流程总控）；本会话不改生产代码
- Received (verbatim): `P2C_EXTRACTED_TREE_PRESENT_ON_EXECUTOR_VM=yes`
- Authority that named this string: C1 `docs/review_20260819/2026-08-19-004_review.md` @ `e9cdbf32`
- Independent check time: 2026-08-19 (this reviewer VM)
- Packet issued: **none** (no 005, no spawn-retry, no missing-copy)

## Why the string is not accepted

C1 required an independent confirm of `extracted/` or a hash-matching
`archives/` blob **before** a spawn-retry packet. The string licenses
the reviewer to look; it does not create a tree.

Packet 004 already showed a fresh executor VM had no tree
(`MISSING_WITH_REASON` / `E_SOURCE_TREE_ABSENT`, evidence `51c246f5`).
Re-issuing that missing booking is rejected option (B).

## Independent check (this C1-gate)

| Check | Result |
|---|---|
| `test -e data/p3_v3/p12_intake/extracted` | `EXTRACTED_ABSENT` |
| `test -e data/p3_v3/p12_intake/archives` | `ARCHIVES_DIR_ABSENT` |
| `test -e data/p3_v3/p12_intake/archives/1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.tar` | `TAR_ABSENT` |
| `find data/p3_v3 -name '*.tar'` | empty |
| subject descriptor | present (`descriptors/1f67b3f3….json` only; not a source tree) |
| bridge `source_archive_sha256` for `1f67b3f3…` | `c7c3d38533c01a7366d2511497082af5f30f510d0f95db822d98441a06a1898c` (expected if an archive later appears) |
| `.gitignore` | `data/p3_v3/p12_intake/extracted/` and `archives/` (trees are local-only; not on `main`) |
| this run `environment-info` | `environment=null`, `build=null`, no linked snapshot that could inject P12 onto a new executor |
| last executor (packet 004) | no spawn; `E_SOURCE_TREE_ABSENT` |

## Process verdict

**`WAIT` continues.** Do not issue `execution_packet_2026-08-19-005`.
Do not download P12. Do not cmake. Do not treat a second paste of the
same string as new evidence.

## What would count next (any one)

1. On **this reviewer VM**: directory
   `data/p3_v3/p12_intake/extracted/1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72/`
   exists (then reviewer re-checks and may issue a spawn-retry of the
   existing `ltest` seam; still no cmake / no download).
2. On **this reviewer VM**: archive file at
   `data/p3_v3/p12_intake/archives/1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.tar`
   with SHA-256 `c7c3d38533c01a7366d2511497082af5f30f510d0f95db822d98441a06a1898c`.
3. Author attaches **named** executor evidence (bcId + `ls` + `sha256sum`)
   showing (1) or (2) already on that VM. A request to spawn a new empty
   VM is not evidence.

## §10.1

| 处置 | 分类 |
|---|---|
| 拒绝在无树时签发 spawn-retry / 缺失副本包 | 效度修复：避免 004 再演一遍 |
| 不把口头 yes 当成树 | 效度修复 |

主张收缩清单：空。真实 `ltest` spawn 仍在菜单上。

## Reviewer 2 视角的最严苛审稿意见

- [方法论] 口头 READY 第二次仍无磁盘树。再开包只会再记 `E_SOURCE_TREE_ABSENT`。
- [外部效度] 未用缺失行外推。
- [统计选择] 未授权其余行缺失副本。
- [基准] 未打开 cmake / P12 下载。
- [霍桑] 未改选择集。

Reviewer 2 视角扫描通过——5 类维度均无 publication blocker。
