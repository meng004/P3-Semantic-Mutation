# Cursor VM instruction — WAIT after 013 C1

013 is closed on the reviewer branch. Do **not** start P2-D.
Do **not** book the other 14 frozen rows. Do **not** issue the
next Gate. New Desktop VMs may only confirm the hashes below.

## Wrapper

```text
你是 Cursor VM 执行器。只执行下面这一份评审模型指令。
禁止 rtk。禁止自行签发 SOL_* token 或下一 Gate。
这是 WAIT，不是新的科学包。做到 HARD STOP 后停止。
禁止 git clone P12。禁止 git clean -x。禁止 cmake。禁止编译器。
禁止 ENABLE_XBRAID / ENABLE_LAPACK / BUILD_BENCHMARKS。
禁止 SUNDIALS_TEST_UNITTESTS。禁止猜 -D。
禁止把 test_nvector_serial 或 1000 0 当作 argv。
禁止臆造 nvector_serial 程序名。
禁止 P2-D。禁止合并 006–013。
```

## ENV_INIT

```text
ENV_INIT
PHASE=CURSOR_VM_ENV_INIT
STATUS=WAIT_AFTER_013
ALLOWED_COMMANDS=git ls-remote origin refs/heads/cursor/p2c-local-tar-header-serial-58d6; git rev-parse HEAD
REQUIRED_LS_REMOTE=94e6e9597c604cbca3ec73511b7c8a448b443629
FORBIDDEN_COMMANDS=git clone P12-Defect4MR; git clean -x; git add archives; git add extracted; cmake; ctest; cc; c++; ENABLE_XBRAID; ENABLE_LAPACK; BUILD_BENCHMARKS; SUNDIALS_TEST_UNITTESTS; brew install; apt-get; guessed cmake -D flags; test_nvector_serial; invented nvector_serial CLI; P2-D
```

## CURSOR_VM_INSTRUCTION

```text
CURSOR_VM_INSTRUCTION
PHASE=WAIT_AFTER_013
STATUS=WAIT_AUTHOR
TOKEN=WAIT_AFTER_013=yes
PARENT=4444061dde0159a5edd62753fe3cef2d881a308c
HEAD=do not create a new science branch
REF=origin/cursor/p2c-local-tar-header-serial-58d6
PACKET=docs/review_20260819/2026-08-20-013_review.md
PACKET_REF=origin/cursor/phase2-c0-p2a-packet-a558
BRANCH=none
ALLOWED_FILES=none
FORBIDDEN=src/p3_v3; evidence.py; 006-013 scripts; phase1_frames; clone P12; 34 archives; git add extracted/ archives/ _p2c_build/; git clean -x; cmake; compiler; spawn; ENABLE_XBRAID; ENABLE_LAPACK; BUILD_BENCHMARKS; SUNDIALS_TEST_UNITTESTS; guessed -D; test_nvector_serial; P2-D; claim upgrade; rtk; issue next Gate; merge 006-013
READINESS=ls-remote tip == 94e6e9597c604cbca3ec73511b7c8a448b443629
EDITS=none
TESTS=none
HARD_STOP=yes
MUST_NOT_ISSUE_NEXT_GATE=yes
```
