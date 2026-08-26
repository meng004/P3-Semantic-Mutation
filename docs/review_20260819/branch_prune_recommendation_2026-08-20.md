# Branch prune recommendation — 2026-08-20

- Reviewer: 评审模型（流程总控）；本会话不改生产代码
- Trigger (author, verbatim): `为减少分支数量，请先评估再给出修剪建议`
- Inventory baseline: `docs/review_20260819/branch_governance_2026-08-20.md`
- `origin` heads at evaluation: **54** (of which `cursor/*` = **32**)
- Archive tags matching `p2a|p2b|p2c|archive`: **none**
- Reviewer branch contains **no** executor job JSON / packet scripts
- This note does **not** delete remotes, close PRs, or create tags

## Evaluation (why not “just delete”)

C1 reviews already record every 001–013 **evidence** and **tip** SHA.
That is enough to *cite* the close. It is **not** enough to *fetch*
the receipts after the only branch ref is gone.

`cursor/phase2-c0-p2a-packet-a558` has docs only. Deleting a
no-PR executor branch without another ref makes
`intent.json` / `result.json` / packet scripts unreachable from
this remote (GitHub may keep objects for a while; that is not an
archival guarantee).

001–004 have draft PRs #22–#25: closing the PR keeps the commits
on the PR page. 005–013 have **no** PR: they need a tag (or an
archive branch) **before** `git push --delete`.

Merging executor slices into `main` to “reduce branches” is
**not** a prune. It would thicken `main` and look like Phase 2
closed.

## Keep (do not prune)

| Ref | Why |
|---|---|
| `main` @ `4444061d` | baseline |
| `cursor/phase2-c0-p2a-packet-a558` (#21) | process-control; packets + C1 |
| `cursor/dual-agent-init-58d6` (#20) | governing init; not on `main` |

Executor paste stays WAIT-after-013. Packet 014 stays unissued.

## Suggested tiers (pick one; default is none)

### Tier 0 — leftover merged heads (lowest risk)

These PRs are already merged. GitHub retains the PR commit graph.
Deleting the leftover head only removes a duplicate pointer.

| PR | Head still on `origin` |
|---|---|
| #15 | `cursor/p3-cxx-qualification-c46c` |
| #14 | `codex/p3-v3-mef-align-repair-01` |
| #12 | `codex/pr7-r2-local-gate-audit` |
| #11 | `codex/ci-strict-failure-timeout` |
| #10 | `codex/ci-fetch-baseline-object` |
| #9 | `codex/ci-fetch-full-history` |
| #8 | `cursor/ci-statsmodels-0146-8f57` |
| #7 | `cursor/grok-phase3-supplemental-mining-r2` |
| #1 | `cursor/theory-enhancement-t0-6320` |

Effect: **54 → 45** heads. No tags. No P2 evidence risk.
Does **not** shrink the 001–013 campaign clutter.

### Tier 1 — P2 campaign science (recommended if the goal is this campaign)

Prerequisite, then delete. Order is a gate.

1. Push **annotated tags** at each tip (parent evidence stays
   reachable from the tip). Suggested names:

| Tag | Tip |
|---|---|
| `archive/p2-001-f270c317` | `f270c317…` |
| `archive/p2-002-c67c0041` | `c67c0041…` |
| `archive/p2-003-86948076` | `86948076…` |
| `archive/p2-004-317e0ba3` | `317e0ba3…` |
| `archive/p2-005-670d697c` | `670d697c…` |
| `archive/p2-006-3c82c05e` | `3c82c05e…` |
| `archive/p2-007-f1613c34` | `f1613c34…` |
| `archive/p2-008-34c6f1dc` | `34c6f1dc…` |
| `archive/p2-009-fd27ba4b` | `fd27ba4b…` |
| `archive/p2-010-ec54e323` | `ec54e323…` |
| `archive/p2-011-fbea0694` | `fbea0694…` |
| `archive/p2-012-0287491e` | `0287491e…` |
| `archive/p2-013-94e6e959` | `94e6e959…` |

   Also tag `archive/p2-004-evidence-51c246f5` if this clone’s
   ancestor walk of #25 remains unreliable.

2. Close draft PRs **#22–#25** without merging (GitHub keeps the
   PR graph in addition to the tags).

3. `git push origin --delete` the 13 `*-58d6` science branches.

Effect after Tier 0+1: **54 → 32** heads. Campaign branch count
goes from 13 science + 1 process to **1 process**. Receipts remain
fetchable via tags.

Do **not** skip step 1 for 005–013.

### Tier 2 — other open campaigns (not recommended from this session)

Open heads #16–#19 (infra), #2–#6 / #13 (Phase 3 / TOSEM / MEF).
Closing them is a **different** campaign decision. This C1 loop
does not have standing to call them stale.

## Not recommended

| Idea | Why not |
|---|---|
| Delete 005–013 with no tag / no PR | unique receipts become unreferenced |
| Merge 001–013 into `main` or #21 | fake Phase 2 close; thickens production |
| Delete #21 or #20 | loses process authority / init text |
| Force-push or rewrite already-reviewed tips | breaks C1 SHAs |

## Author string (required before any prune)

Reply with exactly one:

1. `修剪：只做 Tier 0` — delete the 9 merged leftover heads only.
2. `修剪：Tier 0+1` — tags, close #22–#25, delete 13 science branches.
3. `修剪：只做 Tier 1` — same as 2 without the merged leftovers.
4. `不修剪` — keep all remotes; inventory stands.

After that string, the reviewer will issue a **Desktop** packet
(tags/deletes are write operations on `origin`). This Cloud
reviewer session will not delete remotes on a mere “looks good”.
