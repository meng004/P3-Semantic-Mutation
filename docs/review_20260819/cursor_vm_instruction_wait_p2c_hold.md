# Cursor VM instruction — WAIT (P12 reachable string refused)

Issued after `docs/review_20260819/author_string_2026-08-20-p12-reachable-refused.md`.
This is the only authorized Cursor VM input until the reviewer issues a
new `EXECUTION_PACKET`.

The verbal token `P12_ONE_ARCHIVE_REACHABLE=yes` was received and
refused (ls-remote still 404; no local tar). This WAIT VM must not act
on that string or retry packet 005.

---

## Wrapper (paste first)

```text
你是 Cursor VM 执行器。只执行下面这一份评审模型指令。
禁止 rtk。禁止自行签发 SOL_* token 或下一 Gate。
做到 HARD STOP 后停止。
```

## CURSOR_VM_INSTRUCTION

```text
CURSOR_VM_INSTRUCTION
PHASE=WAIT_P2C_REMAINDER_AND_P2D
STATUS=AUTHOR_STRING_REFUSED_NO_P12
TOKEN=none
PARENT=none
HEAD=none
REF=origin/cursor/phase2-c0-p2a-packet-a558
AUTHORITY=docs/review_20260819/author_string_2026-08-20-p12-reachable-refused.md
AUTHORITY_COMMIT=pending-this-commit
BRANCH=none
WORKTREE=none
ALLOWED_FILES=none
FORBIDDEN=create qualification/successor/forensics/boostmath branches; accept unreviewed heads as paper-citable; start P2-C remainder; start P2-D; retry packet 005 against the same 404; download 34 other archives; full P12 package; cmake other PUTs; claim upgrade; P12 reveal; edit submission/TOSEM_*; open PR; rtk; merge #22/#23/#24/#25; issue next Gate; write execution_packet_2026-08-19-006
READINESS=wait
COMMANDS_EXECUTED=none
FILES_CHANGED=none
TESTS=do not run tests
COMMIT=none
PUSH=none
LS_REMOTE=none
EDITS=none
COMMIT_SUBJECT=none
TOPOLOGY=none
REPORT_FIELDS=phase,status,commands_executed,files_changed,waiting_for,hard_stop
WAITING_FOR_EXACT_STRING=none
WAITING_FOR=reviewer-confirmable one-archive: git ls-remote of github.com/meng004/P12-Defect4MR at d57fa811 returns a SHA OR archives/1f67b3f3....tar sha256=c7c3d38533c01a7366d2511497082af5f30f510d0f95db822d98441a06a1898c
WAITING_STRING_MEANING=the token P12_ONE_ARCHIVE_REACHABLE=yes was received and refused on 2026-08-20. Repeating it is not new evidence. This WAIT VM must not start work.
UNTIL_THEN_FORBIDDEN=P2-C remainder; P2-D; packet 006 same-404 retry; 35-pack dump; claim upgrade
HARD_STOP=yes
MUST_NOT_ISSUE_NEXT_GATE=yes
```

## Closed vs blocked

Closed: P2-A; P2-B; P2-C header missing (003); P2-C process-argv missing
(004); P2-C one-archive fetch attempt (005, `E_ARCHIVE_FETCH_FAILED`).
Blocked: extract+cmake+spawn, P2-C remainder, P2-D. Claims `blocked`.

## HARD STOP checklist

1. Do not `git checkout` a feature branch for this instruction.
2. Do not create or modify files.
3. Do not run pytest, preflight, cmake, or clone P12.
4. Reply with `PHASE=WAIT_P2C_REMAINDER_AND_P2D`, `COMMANDS_EXECUTED=none`,
   `FILES_CHANGED=none`, then stop.
