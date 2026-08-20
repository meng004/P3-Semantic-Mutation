# Author authorization 2026-08-19 — one-archive extract + subject deps

- Reviewer: 评审模型（流程总控）；本会话不改生产代码
- Received (verbatim): `只取这一个受试 archive / 只解压，仍禁止 cmake 和 35 包全量`
- Follow-on (verbatim): `如果受试archive依赖cmake，解禁cmake，同理，也放行其他依赖项。`
- Recorded: 2026-08-19
- Packet issued: `docs/review_20260819/execution_packet_2026-08-19-005.md`

## Scope of the exception

Pinned subject
`1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72`
(`CMAKE_CTEST_V1`, `language_family=c`). Descriptor requires cmake.
Pinned process-argv row remains `selected_behavior_ids[1]` /
`target:ltest` / argv `["ltest"]`.

**Allowed for this subject only:**

1. Fetch **one** archive whose SHA-256 is
   `c7c3d38533c01a7366d2511497082af5f30f510d0f95db822d98441a06a1898c`
   from pinned P12 release `d57fa8119e47baf88c5bcff2d67346864cf3672d`
   (`github.com/meng004/P12-Defect4MR`, tag `p3-bridge-v1`).
2. Extract that archive into
   `data/p3_v3/p12_intake/extracted/<neutral>/`.
3. cmake / C compiler / make or ninja / apt or FetchContent packages
   that **this extracted tree** needs to configure and to
   `--target ltest`.

**Still forbidden:**

- the other 34 archives / full 3.3 GB dump
- cmake of Boost.Math qualification, `qualify_cxx_link.py`, other PUTs
- rewriting `selected_behavior_ids`, P12 reveal, claim upgrade, P2-D
- `git add` of `extracted/` / `archives/` / build trees

## Independent notes at issue time

- This reviewer VM: `extracted/` and `archives/` still absent.
- `gh api repos/meng004/P12-Defect4MR` with this run's token: HTTP 404
  (private). The executor must use a principal that can read that
  commit. Fetch failure is `E_ARCHIVE_FETCH_FAILED`, not a license to
  pull 35 tars.
- Archive is a **fixed-version source** snapshot. `ltest` is expected
  only after cmake `--target ltest`. PATH `ltest` remains forbidden.

## §10.1

| 处置 | 分类 |
|---|---|
| 单受试 fetch + 为 `ltest` 解禁 cmake/依赖 | 效度修复：让 process-argv 行可被证伪 |
| 仍禁 35 包 / 资格认证 / 改选择集 | 反基础设施复发 |

主张收缩清单：空。
