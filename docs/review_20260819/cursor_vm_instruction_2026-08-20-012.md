# Cursor VM instruction — P2-C frozen PROJECT_TEST official argv (012)

Paste into a **new Desktop** VM on
`/Users/limeng/Papers/P3-SemanticMutation`. Do not reuse 009–011 as a
dirty HEAD. Do not use an empty Cloud VM.

## Wrapper

```text
你是 Cursor VM 执行器。只执行下面这一份评审模型指令。
禁止 rtk。禁止自行签发 SOL_* token 或下一 Gate。
做到 HARD STOP 后停止。
禁止 git clone P12。禁止 git clean -x。禁止 cmake --target ltest。
禁止 ENABLE_XBRAID。禁止 ENABLE_LAPACK。禁止 BUILD_BENCHMARKS。
禁止 SUNDIALS_TEST_UNITTESTS。禁止 SUNDIALS_TEST_ENABLE_UNIT_TESTS。
禁止猜 -D。禁止 ctest -R。禁止 argv ^NAME$。禁止 brew/apt。
```

## ENV_INIT

```text
ENV_INIT
PHASE=CURSOR_VM_ENV_INIT
STATUS=LOCAL_TAR_REHASH
ALLOWED_COMMANDS=sha256sum data/p3_v3/p12_intake/archives/1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.tar; python3 --version; command -v cmake
REQUIRED_SHA256=c7c3d38533c01a7366d2511497082af5f30f510d0f95db822d98441a06a1898c
IF_HASH_FAIL=stop; report TAR_HASH_FAIL; do not clone P12
FORBIDDEN_COMMANDS=git clone P12-Defect4MR; git clean -x; git add archives; git add extracted; cmake --build --target ltest; ENABLE_XBRAID; ENABLE_LAPACK; BUILD_BENCHMARKS; SUNDIALS_TEST_UNITTESTS; SUNDIALS_TEST_ENABLE_UNIT_TESTS; brew install; apt-get; guessed cmake -D flags; ctest -R; ^NAME$
```

## CURSOR_VM_INSTRUCTION

```text
CURSOR_VM_INSTRUCTION
PHASE=PHASE2_P2C_LOCAL_TAR_PROJECT_TEST
STATUS=EXECUTING_PACKET_2026-08-20-012
TOKEN=LOCAL_TAR_PROJECT_TEST_OFFICIAL_ARGV=yes
PARENT=4444061dde0159a5edd62753fe3cef2d881a308c
HEAD=4444061dde0159a5edd62753fe3cef2d881a308c
REF=origin/main
PACKET=docs/review_20260819/execution_packet_2026-08-20-012.md
PACKET_REF=origin/cursor/phase2-c0-p2a-packet-a558
BRANCH=cursor/p2c-local-tar-project-test-58d6
WORKTREE=new branch from PARENT; keep gitignored tar
ALLOWED_FILES=scripts/p3_v3/run_p2c_local_tar_project_test.py; data/p3_v3/phase2_profiling/jobs/p2c-20260820-012/; data/p3_v3/phase2_profiling/local-tar-project-test-terminal.json; data/p3_v3/handoff/2026-08-20-012.json; tests/p3_v3/test_phase2_p2c_local_tar_project_test.py
FORBIDDEN=any other tracked file; src/p3_v3; evidence.py; 006-011 scripts; phase1_frames; clone P12; 34 archives; git add extracted/ archives/ _p2c_build/; git clean -x; cmake --target ltest; ENABLE_XBRAID; ENABLE_LAPACK; BUILD_BENCHMARKS; SUNDIALS_TEST_UNITTESTS; SUNDIALS_TEST_ENABLE_UNIT_TESTS; guessed -D; ctest -R; ^NAME$; default all-build; P2-D; claim upgrade; rtk; issue next Gate
READINESS=local tar sha256sum == c7c3d38533c01a7366d2511497082af5f30f510d0f95db822d98441a06a1898c; then HEAD=4444061d and tracked tree clean
EDITS=implement packet 012 acceptance criteria 1-11 exactly
TESTS=PYTHONPATH=src python3 -m pytest tests/p3_v3/test_phase2_p2c_local_tar_project_test.py -q
COMMIT_SUBJECT=p3-v3(2026-08-20-012): P2-C local-tar PROJECT_TEST official argv only
TOPOLOGY=ordinary children of 4444061dde0159a5edd62753fe3cef2d881a308c; name-status only ALLOWED_FILES
PUSH=ordinary push -u origin cursor/p2c-local-tar-project-test-58d6
LS_REMOTE=must return the new tip after push
REPORT_FIELDS=head,parent,tree,subject,name-status,file-sha256,local_tar_sha256,source_is_regular_file,help_has_exact_target,ctest_has_exact_name,project_test_kept_count,result_status,result_failure_code,hard_stop
HARD_STOP=yes
MUST_NOT_ISSUE_NEXT_GATE=yes
```
