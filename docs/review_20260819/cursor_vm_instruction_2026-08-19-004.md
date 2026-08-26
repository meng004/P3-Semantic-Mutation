# Cursor VM instruction — P2-C process-argv row (004)

Paste the wrapper plus the instruction block into a **new** Cursor VM.
Do not reuse a WAIT VM and do not continue a 003 worktree.

## Wrapper

```text
你是 Cursor VM 执行器。只执行下面这一份评审模型指令。
禁止 rtk。禁止自行签发 SOL_* token 或下一 Gate。
做到 HARD STOP 后停止。
```

## CURSOR_VM_INSTRUCTION

```text
CURSOR_VM_INSTRUCTION
PHASE=PHASE2_P2C_PROCESS_ROW
STATUS=EXECUTING_PACKET_2026-08-19-004
TOKEN=P2C_TREE_AND_PROCESS_ARGV_SEAM_READY=yes
PARENT=4444061dde0159a5edd62753fe3cef2d881a308c
HEAD=4444061dde0159a5edd62753fe3cef2d881a308c
REF=origin/main
PACKET=docs/review_20260819/execution_packet_2026-08-19-004.md
PACKET_REF=origin/cursor/phase2-c0-p2a-packet-a558
BRANCH=cursor/p2c-process-row-profiling-58d6
WORKTREE=new branch from PARENT
ALLOWED_FILES=scripts/p3_v3/run_p2c_process_row.py; data/p3_v3/phase2_profiling/jobs/p2c-20260819-004/; data/p3_v3/phase2_profiling/process-row-terminal.json; data/p3_v3/handoff/2026-08-19-004.json; tests/p3_v3/test_phase2_p2c_process_row.py
FORBIDDEN=any other file; src/p3_v3; evidence.py; pilot.py; run_p2c_one_row.py; phase1_frames; protocol; cmake; meson; autotools; c++; qualify_cxx_link; Boost.Math; download P12; git add extracted/ or archives/; amend/reset/force-push; rtk; P2-D; second behavior; claim upgrade; submission/TOSEM_*; issue next Gate
READINESS=git rev-parse HEAD == 4444061dde0159a5edd62753fe3cef2d881a308c and tracked tree clean
EDITS=implement packet 004 acceptance criteria 1-8 exactly
TESTS=PYTHONPATH=src python3 -m pytest tests/p3_v3/test_phase2_p2c_process_row.py -q
COMMIT_SUBJECT=p3-v3(2026-08-19-004): P2-C process-argv row intent/result
TOPOLOGY=ordinary children of 4444061dde0159a5edd62753fe3cef2d881a308c; name-status only ALLOWED_FILES
PUSH=ordinary push -u origin cursor/p2c-process-row-profiling-58d6
LS_REMOTE=must return the new tip after push
REPORT_FIELDS=head,parent,tree,subject,name-status,file-sha256,result_status,result_failure_code,hard_stop
HARD_STOP=yes
MUST_NOT_ISSUE_NEXT_GATE=yes
```
