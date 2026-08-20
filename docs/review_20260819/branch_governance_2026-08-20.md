# Branch governance — 2026-08-20 (after 013 C1)

- Reviewer: 评审模型（流程总控）；本会话不改生产代码
- Trigger (author, verbatim): `治理分支`
- Process-control branch: `cursor/phase2-c0-p2a-packet-a558`
- Process-control tip: `098b91ad5e68a47b438ebf4fb5ee9c5d4cb3d872` (before this note)
- Baseline / `origin/main`: `4444061dde0159a5edd62753fe3cef2d881a308c`
- Draft PR: https://github.com/meng004/P3-Semantic-Mutation/pull/21

This note is an inventory and merge policy. It does **not** merge,
delete remotes, close PRs, start packet 014, or open P2-D.

## Policy (hard)

| Action | Allowed from this reviewer session |
|---|---|
| Merge `#22`–`#25` or 005–013 executor branches into `main` | **no** |
| Merge those executor branches into `phase2-c0-p2a-packet-a558` | **no** |
| Merge `#16`–`#20` infra / init PRs | **no** |
| Delete remote executor branches | **no** (author only) |
| Amend / reset / force-push already-reviewed tips | **no** |
| Issue packet 014 / start P2-D | **no** (WAIT after 013) |
| Keep executor tips as ordinary children of `4444061d` | **yes** (already true except the 004 clone caveat below) |

Executor science stays on `*-58d6` branches. Reviewer process docs
stay on `*-a558`. Those two lineages must not be squash-merged
together from this session.

## Process-control branch

| Field | Value |
|---|---|
| Branch | `cursor/phase2-c0-p2a-packet-a558` |
| PR | #21 draft → `main` |
| Tip at inventory | `098b91ad…` |
| Merge-base with `main` | `4444061d…` |
| Contents | `docs/review_20260819/` packets, C1 notes, official-doc argv records, VM instructions |
| Production code | none (`src/p3_v3/` unchanged vs `main`) |

Current executor paste remains
`docs/review_20260819/cursor_vm_instruction_2026-08-20-wait-after-013.md`.

## Executor science branches (do not merge)

All tips below were read from `git ls-remote` / `origin/*` on
2026-08-20. `main` ancestor means `git merge-base --is-ancestor
4444061d <tip>` succeeded in this clone.

| Packet | Branch | Tip | PR | `main` ancestor | C1 |
|---|---|---|---|---|---|
| 001 P2-A | `cursor/p2a-one-subject-preflight-58d6` | `f270c317…` | #22 draft | yes | closed |
| 002 P2-B | `cursor/p2b-pilot-only-terminals-58d6` | `c67c0041…` | #23 draft | yes | closed |
| 003 header `[0]` | `cursor/p2c-one-row-profiling-58d6` | `86948076…` | #24 draft | yes | closed |
| 004 CLI attempt | `cursor/p2c-process-row-profiling-58d6` | `317e0ba3…` | #25 draft | see caveat | closed |
| 005 archive fetch | `cursor/p2c-one-archive-spawn-58d6` | `670d697c…` | none | yes | closed |
| 006 local tar cmake | `cursor/p2c-local-tar-cmake-58d6` | `3c82c05e…` | none | yes | closed |
| 007 rebuild | `cursor/p2c-local-tar-rebuild-58d6` | `f1613c34…` | none | yes | closed |
| 008 resolve | `cursor/p2c-local-tar-resolve-58d6` | `34c6f1dc…` | none | yes | closed |
| 009 CLI object | `cursor/p2c-local-tar-object-58d6` | `fd27ba4b…` | none | yes | closed |
| 010 EXAMPLE | `cursor/p2c-local-tar-example-58d6` | `ec54e323…` | none | yes | closed |
| 011 BENCHMARK | `cursor/p2c-local-tar-benchmark-58d6` | `fbea0694…` | none | yes | closed |
| 012 PROJECT_TEST | `cursor/p2c-local-tar-project-test-58d6` | `0287491e…` | none | yes | closed |
| 013 PUBLIC_API `[5]` | `cursor/p2c-local-tar-header-serial-58d6` | `94e6e959…` | none | yes | closed |

Standing handoff convention: paper-facing evidence is the parent of
the tip; the tip only adds `data/p3_v3/handoff/2026-08-2*-0xx.json`.

### 004 caveat (this clone)

GitHub PR #25 lists ordinary commits `51c246f5` then `317e0ba3`
on top of `4444061d`. `git cat-file -p 317e0ba3` in this clone
also names parent `51c246f5`, and `51c246f5` itself is an ordinary
child of `4444061d`. `git merge-base --is-ancestor 51c246f5
317e0ba3` nevertheless failed here. Treat that as a **clone walk
limitation**, not a license to rewrite or merge #25.

## Init / frozen infrastructure (do not thicken)

| PR | Branch | Role | Merge from this session |
|---|---|---|---|
| #20 draft | `cursor/dual-agent-init-58d6` @ `b74eb2b2…` | governing init text | no |
| #16 open | `cursor/p3-standards-remediation-c46c` | infra design | no |
| #17–#19 draft | compiler-alias / path-scan CI | infra | no |
| #15 merged | C++ qualification | already on `main` @ `4444061d` | n/a; do not reopen |

Older Phase 3 / TOSEM draft PRs (#2–#6, #13) are out of this
campaign. This session does not touch them.

## Local C1 worktrees

Reviewer-created detached checkouts under `/tmp/p2c-00{6..13}-c1-review`
are audit clones only. This governance pass removes them. It does
**not** delete remotes.

`/workspace` stays on `cursor/phase2-c0-p2a-packet-a558`.

## Still blocked

| Target | Status |
|---|---|
| P2-C remainder (14 frozen rows after `[5]`) | blocked; official-doc argv only |
| P2-D | blocked (no technique-site traces) |
| Claims | `blocked` |
| Packet 014 | not issued |

## Author-only later (not done here)

1. Keep all of the above as lineage (recommended).
2. Close unused draft PRs without merging.
3. Delete a remote executor branch after its C1 SHA is recorded
   elsewhere (this note already records tips).
4. Merge process docs (#21) or init (#20) into `main` only after
   an explicit author string.

## Reviewer 2

No publication blocker in this inventory. The risk is merging an
executor slice and calling Phase 2 closed. That merge is forbidden
above.
