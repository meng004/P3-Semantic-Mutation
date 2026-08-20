# Cursor VM — 新执行器：环境初始化 + 当前任务

Open a **new** Cursor VM. Do not reuse 001–005 or any prior WAIT session.

This file is the only authorized first paste until the reviewer issues a
numbered `EXECUTION_PACKET`. Current science task is still **WAIT**.
Do not install packages. Do not issue packet 006.

Authority for the WAIT slice:
`docs/review_20260819/p12_access_configured_2026-08-20.md` @ `815c9d9c`.

---

## 1. 包装器（先贴）

```text
你是 Cursor VM 执行器。只执行下面这一份评审模型指令。
禁止 rtk。禁止自行签发 SOL_* token 或下一 Gate。
做到 HARD STOP 后停止。
环境没有 rtk。不要安装新依赖。不要配置 GH_TOKEN / PAT。不要 clone P12。
```

---

## 2. 环境初始化指令（只核验，不安装）

Default Cloud Agent images already provide `python3`, `git`, and `gh`.
This WAIT task needs **no** extra library, venv, cmake run, or token.
A missing `cmake` / `GH_TOKEN` is not a defect of this VM.

```text
ENV_INIT
PHASE=CURSOR_VM_ENV_INIT
STATUS=VERIFY_ONLY_NO_INSTALL
TOKEN=none
PARENT=none
HEAD=none
REF=do-not-checkout
BRANCH=none
WORKTREE=whatever default clone this VM already has (main or empty is fine)
ALLOWED_COMMANDS=python3 --version; git --version; command -v gh; command -v cmake; test ! -e data/p3_v3/p12_intake/archives/1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.tar
FORBIDDEN_COMMANDS=apt-get; apt; yum; dnf; pip; pip3; conda; poetry; uv pip; cmake configure/build; git clone; git checkout feature branch; git add; git commit; git push; gh auth login; writing .env or ~/.gitconfig or hosts.yml; export of a pasted PAT; pytest; preflight; sparse-clone P12; download archives
REQUIRED_PACKAGES=none
VENV=do not create
PYTHONPATH=do not set
GH_TOKEN=do not set; this task does not read P12
CMAKE=do not invoke even if /usr/bin/cmake exists
P12_INSTEADOF=do not configure
IF_TAR_PRESENT=do not extract or cmake; report sha256sum in the WAIT reply and stop
```

If an `ALLOWED_COMMANDS` binary is missing, write `TOOL_<name>=absent` in
the report. Do **not** install it.

---

## 3. 当前任务完整指令（环境核验后立刻执行，不要另开科学包）

```text
CURSOR_VM_INSTRUCTION
PHASE=WAIT_P2C_REMAINDER_AND_P2D
STATUS=P12_GIT_REACHABLE_ARCHIVE_BLOB_ABSENT
TOKEN=none
PARENT=none
HEAD=none
REF=origin/cursor/phase2-c0-p2a-packet-a558
AUTHORITY=docs/review_20260819/p12_access_configured_2026-08-20.md
AUTHORITY_COMMIT=815c9d9c
BRANCH=none
WORKTREE=none
ALLOWED_FILES=none
FORBIDDEN=create qualification/successor/forensics/boostmath branches; accept unreviewed heads as paper-citable; start P2-C remainder; start P2-D; retry packet 005; sparse-clone P12 expecting archives/<neutral>.tar in d57fa811; download 34 other archives; full P12 package; cmake other PUTs; claim upgrade; P12 reveal; edit submission/TOSEM_*; open PR; rtk; merge #22/#23/#24/#25; issue next Gate; write execution_packet_2026-08-19-006; apt/pip install; configure GH_TOKEN
READINESS=ENV_INIT verify-only completed; no files changed
COMMANDS_EXECUTED=only ENV_INIT ALLOWED_COMMANDS
FILES_CHANGED=none
TESTS=do not run tests
COMMIT=none
PUSH=none
LS_REMOTE=none
EDITS=none
COMMIT_SUBJECT=none
TOPOLOGY=none
REPORT_FIELDS=phase,status,env_python,env_git,env_gh,env_cmake,tar_status,commands_executed,files_changed,waiting_for,hard_stop
WAITING_FOR_EXACT_STRING=none
WAITING_FOR=one matching tar: data/p3_v3/p12_intake/archives/1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.tar sha256=c7c3d38533c01a7366d2511497082af5f30f510d0f95db822d98441a06a1898c on a reviewer-hashable VM
WAITING_STRING_MEANING=P12 git is reachable on the reviewer VM; the locked commit does not contain the subject archive. Repeating P12_ONE_ARCHIVE_REACHABLE=yes, another ls-remote, or installing cmake is not new evidence. This VM must not start science work.
UNTIL_THEN_FORBIDDEN=P2-C remainder; P2-D; packet 006; 35-pack dump; claim upgrade; any install
HARD_STOP=yes
MUST_NOT_ISSUE_NEXT_GATE=yes
```

---

## 4. HARD STOP 回复模板

```text
PHASE=WAIT_P2C_REMAINDER_AND_P2D
STATUS=P12_GIT_REACHABLE_ARCHIVE_BLOB_ABSENT
ENV_PYTHON=<python3 --version or TOOL_python3=absent>
ENV_GIT=<git --version or TOOL_git=absent>
ENV_GH=<present|absent>
ENV_CMAKE=<present|absent; not invoked>
TAR_STATUS=TAR_ABSENT
COMMANDS_EXECUTED=ENV_INIT verify-only
FILES_CHANGED=none
WAITING_FOR=one matching tar: data/p3_v3/p12_intake/archives/1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72.tar sha256=c7c3d38533c01a7366d2511497082af5f30f510d0f95db822d98441a06a1898c on a reviewer-hashable VM
HARD_STOP=yes
```

Then stop. Do not wait for a follow-up inside this VM.

---

## 5. 作者侧（不要贴进这台 VM）

A later cmake/`ltest` packet will need, on **that** future VM only:

- author-rotated `GH_TOKEN` in the environment (never in git);
- the one gitignored tar at the path and SHA above;
- then cmake / a C toolchain, if still missing after the tar is present.

This document does not authorize those steps.
