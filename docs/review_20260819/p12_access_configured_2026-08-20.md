# P12 private-repo access configured (2026-08-20)

- Reviewer: 评审模型（流程总控）；本会话不改生产代码
- Trigger: author provided a fine-grained PAT via `GH_Token` for this VM
- Packet issued: **none** (no 006)
- Secret handling: the PAT is **not** in this repository, this file, or
  any tracked artifact. It lives only on this VM under `$HOME`.

## What was configured (this reviewer VM only)

Standard GitHub CLI name is `GH_TOKEN`. The author name `GH_Token` is
exported as an alias. Both point at the same value on this VM.

| Location | Role |
|---|---|
| `$HOME/.config/p3/gh-p12.env` (mode 0600, outside the repo) | `export GH_TOKEN` / `GH_Token` |
| `$HOME/.bashrc` and `$HOME/.profile` | source that file |
| `$HOME/.gitconfig` (mode 0600) | P12-only `insteadOf` so `git ls-remote` does not use the Cursor token |

The default `https://github.com/` rewrite still uses the Cursor
installation token. That token cannot see private P12 (HTTP 404). The
longer P12 URL rewrite wins for
`https://github.com/meng004/P12-Defect4MR.git` only.

Executor VMs do **not** inherit this home directory. A later packet
must read `GH_TOKEN` from **that** VM's environment. Do not paste a
PAT into a packet, PR body, or tracked file.

## Independent check (this reviewer VM, after config)

| Check | Result |
|---|---|
| `gh auth status` with `GH_TOKEN` set | logged in as `meng004` via `GH_TOKEN` |
| `gh api user` | `login=meng004` |
| `gh api repos/meng004/P12-Defect4MR` | `full_name=meng004/P12-Defect4MR`, `private=true` |
| `git ls-remote … HEAD` / `refs/heads/main` | `5ef13bc745a479e810fd25c9e80612de148563f1` |
| `git ls-remote … d57fa8119e47baf88c5bcff2d67346864cf3672d` | empty (exit 0): a raw commit is not an advertised ref |
| `gh api repos/meng004/P12-Defect4MR/commits/d57fa811…` | commit exists (`release: publish p3-bridge-v1 …`) |
| `gh api …/git/ref/tags/p3-bridge-v1` | HTTP 404 (tag ref still missing; commit is the lock) |
| GitHub Releases `v1.0.0` / `v1.0.1` | 0 assets |
| recursive tree at `d57fa811` | 1706 entries, **0** paths containing `1f67b3f3`; **2** `.tar` blobs, both `evidence/defect4mr/candidates/b-pocketfft-001/git-capsule/{buggy,fixed}.tar` (unrelated) |
| `release/p3-bridge-v1-package/` top level | `CONTEXT.md`, `data`, `docs`, `schemas` (no `archives/`) |
| local `data/p3_v3/p12_intake/archives/` | `ARCHIVES_DIR_ABSENT` |
| local `…/extracted/` | `EXTRACTED_ABSENT` |
| token string in `/workspace` | not written; `workspace .env` absent |

`P12_ONE_ARCHIVE_REACHABLE=yes` is now **git-reachable** on this VM.
It is **not** archive-reachable. Packet 005 assumed a sparse checkout
could find
`release/p3-bridge-v1-package/archives/<neutral>.tar`. That path is
not in the locked commit.

## Process verdict

**`WAIT` continues.** Do not issue `execution_packet_2026-08-19-006`.
A cmake/`ltest` retry that sparse-clones `d57fa811` will not obtain
`source_archive_sha256=c7c3d38533c01a7366d2511497082af5f30f510d0f95db822d98441a06a1898c`.
That would be another `E_ARCHIVE_FETCH_FAILED` booking, not science.

## What would count next

Place **one** file (gitignored; do not `git add`) at

`data/p3_v3/p12_intake/archives/1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.tar`

with SHA-256
`c7c3d38533c01a7366d2511497082af5f30f510d0f95db822d98441a06a1898c`
on a VM this reviewer can hash. A named non-git one-file URL that
produces that digest is also acceptable. Do not upload the other 34
archives.

## Security (author action)

The PAT was pasted into the agent chat. **Revoke and rotate it** in
GitHub → Settings → Developer settings → Fine-grained tokens. Put the
replacement only in the VM environment (`GH_TOKEN`), never in git.

## §10.1

| 处置 | 分类 |
|---|---|
| 配置本 VM 的 `GH_TOKEN` / P12 `insteadOf`，不写入仓库 | 效度修复：独立确认 git 可达 |
| 确认锁定提交里没有受试 `.tar` 后仍不签发 006 | 效度修复：拒绝把“仓库可读”写成“archive 可读” |
| cmake/`ltest` 仍留在菜单上 | 不是主张收缩 |

主张收缩清单：空。

## Reviewer 2 视角的最严苛审稿意见

- [方法论] git 可达 ≠ 受试 archive 在树内。005 的 sparse 路径在锁定提交上不存在。
- [外部效度] 未用 pocketfft 两个 133 KiB capsule tar 冒充受试源码包。
- [统计选择] 未把其余 34 行登记为同一失败。
- [基准] 未拉 35 包；未打开资格认证。
- [霍桑] 选择集未改。

Reviewer 2 视角扫描通过——5 类维度均无 publication blocker。
