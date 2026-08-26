# Cursor VM instruction — P2-C list cmake/CTest names (008)

Paste into a **new Desktop** VM on
`/Users/limeng/Papers/P3-SemanticMutation`. Do not reuse the 007
session as a dirty HEAD. Do not use an empty Cloud VM.

## Wrapper

```text
你是 Cursor VM 执行器。只执行下面这一份评审模型指令。
禁止 rtk。禁止自行签发 SOL_* token 或下一 Gate。
做到 HARD STOP 后停止。
禁止 git clone P12。禁止 git clean -x。禁止 cmake --target ltest。禁止 brew/apt。禁止猜 -D。
```

## ENV_INIT

```text
ENV_INIT
PHASE=CURSOR_VM_ENV_INIT
STATUS=LOCAL_TAR_REHASH
ALLOWED_COMMANDS=sha256sum data/p3_v3/p12_intake/archives/1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.tar; python3 --version; command -v cmake; command -v ctest
REQUIRED_SHA256=c7c3d38533c01a7366d2511497082af5f30f510d0f95db822d98441a06a1898c
IF_HASH_FAIL=stop; report TAR_HASH_FAIL; do not clone P12
FORBIDDEN_COMMANDS=git clone P12-Defect4MR; git clean -x; git add archives; git add extracted; cmake --build --target ltest; brew install; apt-get; guessed cmake -D flags
```

## CURSOR_VM_INSTRUCTION

```text
CURSOR_VM_INSTRUCTION
PHASE=PHASE2_P2C_LOCAL_TAR_RESOLVE
STATUS=EXECUTING_PACKET_2026-08-20-008
TOKEN=LOCAL_TAR_TARGET_RESOLVE=yes
PARENT=4444061dde0159a5edd62753fe3cef2d881a308c
HEAD=4444061dde0159a5edd62753fe3cef2d881a308c
REF=origin/main
PACKET=docs/review_20260819/execution_packet_2026-08-20-008.md
PACKET_REF=origin/cursor/phase2-c0-p2a-packet-a558
BRANCH=cursor/p2c-local-tar-resolve-58d6
WORKTREE=new branch from PARENT; keep gitignored tar
ALLOWED_FILES=scripts/p3_v3/run_p2c_local_tar_resolve.py; data/p3_v3/phase2_profiling/jobs/p2c-20260820-008/; data/p3_v3/phase2_profiling/local-tar-resolve-terminal.json; data/p3_v3/handoff/2026-08-20-008.json; tests/p3_v3/test_phase2_p2c_local_tar_resolve.py
FORBIDDEN=any other tracked file; src/p3_v3; evidence.py; run_p2c_local_tar_rebuild.py; run_p2c_local_tar_spawn.py; phase1_frames; clone P12; 34 archives; git add extracted/ archives/ _p2c_build/; git clean -x; cmake --target ltest; brew/apt; guessed -D; default all-build; P2-D; claim upgrade; rtk; issue next Gate
READINESS=local tar sha256sum == c7c3d38533c01a7366d2511497082af5f30f510d0f95db822d98441a06a1898c; then HEAD=4444061d and tracked tree clean
EDITS=implement packet 008 acceptance criteria 1-8 exactly
TESTS=PYTHONPATH=src python3 -m pytest tests/p3_v3/test_phase2_p2c_local_tar_resolve.py -q
COMMIT_SUBJECT=p3-v3(2026-08-20-008): P2-C local-tar cmake/CTest target list
TOPOLOGY=ordinary children of 4444061dde0159a5edd62753fe3cef2d881a308c; name-status only ALLOWED_FILES
PUSH=ordinary push -u origin cursor/p2c-local-tar-resolve-58d6
LS_REMOTE=must return the new tip after push
REPORT_FIELDS=head,parent,tree,subject,name-status,file-sha256,local_tar_sha256,cmake_help_log_sha256,ctest_list_log_sha256,ltest_find_count,result_status,result_failure_code,hard_stop
HARD_STOP=yes
MUST_NOT_ISSUE_NEXT_GATE=yes
```
