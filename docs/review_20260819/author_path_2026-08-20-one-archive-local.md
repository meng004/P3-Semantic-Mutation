# Author path received — 2026-08-20 one-archive (not yet hashed here)

- Reviewer: 评审模型（流程总控）；本会话不改生产代码
- Received (verbatim path):
  `/Users/limeng/Papers/P3-SemanticMutation/data/p3_v3/p12_intake/archives/1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.tar`
- Packet issued: **none** (no 006)
- Note: local folder is `P3-SemanticMutation` (no hyphen). GitHub repo is
  `P3-Semantic-Mutation`. That spelling difference is not a defect.

## Independent check (this reviewer VM)

| Check | Result |
|---|---|
| workspace `data/p3_v3/p12_intake/archives/1f67b3f3….tar` | `TAR_ABSENT_REL` |
| `/Users/limeng/Papers/P3-SemanticMutation/…` on this VM | `TAR_ABSENT_MAC` (path is on the author Mac, not mounted) |
| `archives/` / `extracted/` directories | absent |
| `.gitignore` | `data/p3_v3/p12_intake/archives/` still ignored |

A Mac absolute path is a delivery lead. It is not a SHA-256 on a
reviewer-hashable disk. Same rule as refusing verbal
`P12_ONE_ARCHIVE_REACHABLE=yes`.

## What would count next (any one)

1. This reviewer VM can `sha256sum` the file at
   `data/p3_v3/p12_intake/archives/1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.tar`
   and get
   `c7c3d38533c01a7366d2511497082af5f30f510d0f95db822d98441a06a1898c`.
2. A **named** executor (bcId) reports that same `sha256sum` from a
   machine that actually has the bytes. A new empty Cloud VM is not
   that machine.

Do not `git add` the tar. Do not copy the other 34 archives.

## §10.1

| 处置 | 分类 |
|---|---|
| 记录本机路径但不把路径当成已哈希 | 效度修复 |
| 不签发 006 | 效度修复 |

主张收缩清单：空。

## Reviewer 2 视角的最严苛审稿意见

- [方法论] 作者磁盘路径未经本机 `sha256sum`。未当通过。
- [外部效度] 未用路径外推 20 行。
- [统计选择] 未授权其余 archive。
- [基准] 未拉 35 包。
- [霍桑] 选择集未改。

Reviewer 2 视角扫描通过——5 类维度均无 publication blocker。
