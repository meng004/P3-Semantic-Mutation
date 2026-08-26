# Cursor VM instruction — WAIT after 012 C1

012 is closed on the reviewer branch. Do **not** start P2-D.
Do **not** book the other 15 frozen rows. Do **not** issue the
next Gate. New Desktop VMs may only confirm the hashes below.

## Wrapper

```text
你是 Cursor VM 执行器。只执行下面这一份评审模型指令。
禁止 rtk。禁止自行签发 SOL_* token 或下一 Gate。
这是 WAIT，不是新的科学包。做到 HARD STOP 后停止。
禁止 git clone P12。禁止 git clean -x。禁止 cmake --target ltest。
禁止 ENABLE_XBRAID / ENABLE_LAPACK / BUILD_BENCHMARKS。
禁止 SUNDIALS_TEST_UNITTESTS / SUNDIALS_TEST_ENABLE_UNIT_TESTS。
禁止猜 -D。禁止 ctest -R。禁止 argv ^NAME$。
禁止 P2-D。禁止合并 006–012。
```

## ENV_INIT

```text
ENV_INIT
PHASE=CURSOR_VM_ENV_INIT
STATUS=WAIT_AFTER_012
ALLOWED_COMMANDS=git ls-remote origin refs/heads/cursor/p2c-local-tar-project-test-58d6; git rev-parse HEAD
REQUIRED_LS_REMOTE=0287491e077df0dc24a135462dccfd84beb94a10
FORBIDDEN_COMMANDS=git clone P12-Defect4MR; git clean -x; git add archives; git add extracted; cmake --build --target ltest; ENABLE_XBRAID; ENABLE_LAPACK; BUILD_BENCHMARKS; SUNDIALS_TEST_UNITTESTS; SUNDIALS_TEST_ENABLE_UNIT_TESTS; brew install; apt-get; guessed cmake -D flags; ctest -R; ^NAME$; P2-D
```

## CURSOR_VM_INSTRUCTION

```text
CURSOR_VM_INSTRUCTION
PHASE=WAIT_AFTER_012
STATUS=WAIT_AUTHOR
TOKEN=WAIT_AFTER_012=yes
PARENT=4444061dde0159a5edd62753fe3cef2d881a308c
HEAD=do not create a new science branch
REF=origin/cursor/p2c-local-tar-project-test-58d6
PACKET=docs/review_20260819/2026-08-20-012_review.md
PACKET_REF=origin/cursor/phase2-c0-p2a-packet-a558
BRANCH=none
ALLOWED_FILES=none
FORBIDDEN=src/p3_v3; evidence.py; 006-012 scripts; phase1_frames; clone P12; 34 archives; git add extracted/ archives/ _p2c_build/; git clean -x; cmake --target ltest; ENABLE_XBRAID; ENABLE_LAPACK; BUILD_BENCHMARKS; SUNDIALS_TEST_UNITTESTS; SUNDIALS_TEST_ENABLE_UNIT_TESTS; guessed -D; ctest -R; ^NAME$; P2-D; claim upgrade; rtk; issue next Gate; merge 006-012
READINESS=ls-remote tip == 0287491e077df0dc24a135462dccfd84beb94a10
EDITS=none
TESTS=none
HARD_STOP=yes
MUST_NOT_ISSUE_NEXT_GATE=yes
```
