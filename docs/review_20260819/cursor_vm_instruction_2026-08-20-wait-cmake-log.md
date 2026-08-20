# Cursor VM instruction — WAIT (006 closed; need cmake ltest log)

Issued after C1 `docs/review_20260819/2026-08-20-006_review.md`.
Use a **Desktop** VM on the same checkout that ran 006. Do not use an
empty Cloud VM. Do not retry cmake until 007 is issued.

## Wrapper

```text
你是 Cursor VM 执行器。只执行下面这一份评审模型指令。
禁止 rtk。禁止自行签发 SOL_* token 或下一 Gate。
做到 HARD STOP 后停止。
```

## CURSOR_VM_INSTRUCTION

```text
CURSOR_VM_INSTRUCTION
PHASE=WAIT_P2C_CMAKE_LTEST_LOG
STATUS=P2C_006_CLOSED_NEED_BUILD_LOG
TOKEN=none
PARENT=none
HEAD=none
REF=origin/cursor/p2c-local-tar-cmake-58d6
AUTHORITY=docs/review_20260819/2026-08-20-006_review.md
AUTHORITY_COMMIT=c71383ec
BRANCH=none
WORKTREE=none
ALLOWED_FILES=none
FORBIDDEN=create qualification/successor/forensics/boostmath branches; start P2-D; clone P12; download 34 archives; git add extracted/ archives/ _p2c_build/; git clean -x; write execution_packet_2026-08-20-007; merge #22/#23/#24/#25; claim upgrade; P12 reveal; rtk; issue next Gate; implement a new runner
READINESS=wait
COMMANDS_EXECUTED=none unless reporting an already-existing cmake log
FILES_CHANGED=none
TESTS=do not run tests
COMMIT=none
PUSH=none
EDITS=none
REPORT_FIELDS=phase,status,cmake_ltest_log_excerpt,hard_stop
WAITING_FOR=cmake --build --target ltest stdout/stderr excerpt from this subject's _p2c_build (error lines only; no 35-pack; do not invent package names)
WAITING_STRING_MEANING=006 is closed as E_CMAKE_BUILD. A new 007 needs the actual build error. Repeating 006 without the log is not science.
UNTIL_THEN_FORBIDDEN=P2-C remainder; P2-D; blind cmake retry; 35-pack; claim upgrade
HARD_STOP=yes
MUST_NOT_ISSUE_NEXT_GATE=yes
```

## HARD STOP 回复

```text
PHASE=WAIT_P2C_CMAKE_LTEST_LOG
STATUS=P2C_006_CLOSED_NEED_BUILD_LOG
CMAKE_LTEST_LOG_EXCERPT=<paste error lines, or ABSENT>
COMMANDS_EXECUTED=none
FILES_CHANGED=none
HARD_STOP=yes
```
