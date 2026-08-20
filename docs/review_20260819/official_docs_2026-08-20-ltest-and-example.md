# Official-doc lookup — `ltest` and frozen EXAMPLE argv

- Reviewer: 评审模型（流程总控）；本会话不改生产代码
- Trigger (author, verbatim): `读取被测程序的官网帮助文档或issue，不瞎猜参数取值及其意义。`
- First recorded: 2026-08-20 (commit `c8810529`)
- Independently re-fetched: 2026-08-20 (this file)
- paper-search-mcp: unavailable (GetMcpTools catalog miss on
  `paper-search|crossref|arxiv|dblp|semantic`; only `cursor-cloud`
  present). Fallback = official HTML/PDF + GitHub raw/issues.

This note only records **what the official sources say**. It does not
guess `-D` values or invent CLI tokens.

## 检索审计

| Ref | 工具链 | 命中工具 | 状态 |
|-----|--------|---------|------|
| paper-search-mcp | GetMcpTools catalog | none | ✗ catalog miss; fallback |
| Install `ENABLE_XBRAID` | WebFetch readthedocs v7.2.1 | WebFetch | ✓ Default `OFF`; “ARKStep + XBraid interface” |
| Install §1.2.4.14 XBraid | same page | WebFetch | ✓ enable = `ON` + `XBRAID_DIR`; MPI / index 32 / double |
| `cmake/tpl/SundialsXBRAID.cmake` `v6.7.0` | WebFetch raw GitHub | WebFetch | ✓ `project(ltest C)` + `add_executable(ltest ltest.c)` + `try_compile(... ltest)` |
| same file `master` | WebFetch raw GitHub | WebFetch | ✓ name dropped; `try_compile` of `test.c` |
| GitHub issue #4 | WebFetch | WebFetch | ✓ maintainer patch quotes `PROJECT(ltest C)` in Hypre TPL check |
| GitHub issue #74 | WebFetch | WebFetch | ✓ `CMakeFiles/ltest.dir/ltest.o -o ltest` under `ENABLE_LAPACK=ON` |
| EXAMPLE source `master` | WebFetch raw | WebFetch | ✓ `int main(void)` — no `argc`/`argv` |
| EXAMPLE source tag `v6.7.0` | WebFetch raw | WebFetch | ✓ `int main()` — still no `argc`/`argv` |
| CVODE Examples PDF v5.7.0 | WebFetch LLNL | WebFetch | ✓ describes the PDE / left-then-right preconditioning; no CLI tokens |
| CVODE Usage `CVodeSetOptions` | WebFetch readthedocs latest | WebFetch | ✓ library API for programs that opt in; this example does **not** call it |
| EXAMPLE target name | 009 evidence `cmake-help.stdout.txt` | in-repo | ✓ exact `... cvDiurnal_kry_bp` |

## What official text says about `ltest`

Quoted install option
(`https://sundials.readthedocs.io/en/v7.2.1/sundials/Install_link.html`):

> ENABLE_XBRAID — Enable or disable the ARKStep + XBraid interface.
> Default: `OFF`

> To enable XBraid support, set `ENABLE_XBRAID` to `ON`, set
> `XBRAID_DIR` to the root install location of XBraid …

The same page does **not** document a user program named `ltest`,
nor `--help` / `--version` for it. `ENABLE_XBRAID=ON` is documented
as turning on an **ARKStep library interface**, not as “build CLI
`ltest`.”

Quoted TPL check, tag `v6.7.0`
`https://raw.githubusercontent.com/LLNL/sundials/v6.7.0/cmake/tpl/SundialsXBRAID.cmake`:

> `project(ltest C)`
> `add_executable(ltest ltest.c)`
> `try_compile(... ltest)`

Current `master` of that file dropped the `ltest` name and compiles
`test.c` instead.

Quoted issues (same string, different TPLs):

- #4 (`https://github.com/LLNL/sundials/issues/4`): maintainer
  `gardner48` patch quotes `PROJECT(ltest C)` inside a **Hypre**
  TPL `CMakeLists.txt`.
- #74 (`https://github.com/LLNL/sundials/issues/74`): reporter log
  is `CMakeFiles/ltest.dir/ltest.o -o ltest` while configuring
  `ENABLE_LAPACK=ON`.

**Conclusion (docs, not a guess):** `ltest` is a **CMake TPL /
Check\* try_compile executable** reused across Hypre / LAPACK /
XBraid checks. Official user help gives it no parameters. Do **not**
pass `-DENABLE_XBRAID=ON`, `-DENABLE_LAPACK=ON`, or any other guessed
`-D` to manufacture a CLI. 009 `E_PROFILE_BINARY_ABSENT` stays the
close for `13b2cddc…` under default configure.

## What official text says about frozen `[2]` EXAMPLE

Frozen path:
`examples/cvode/serial/cvDiurnal_kry_bp.c`
(`c103b0c611dded134d189f8deedb54ad7a7170b1d78fb12a7851b88ce4115e4f`).

Official sources (not a guess):

1. Tag `v6.7.0` source:
   `https://raw.githubusercontent.com/LLNL/sundials/v6.7.0/examples/cvode/serial/cvDiurnal_kry_bp.c`
   — entry is `int main()` (empty parameter list). No `argc`, no
   `argv`, no `CVodeSetOptions`.
2. Current `master` of the same file — entry is `int main(void)`.
   Still no `argc`/`argv`.
3. Official CVODE Examples booklet v5.7.0
   (`https://computing.llnl.gov/sites/default/files/cv_examples-5.7.0.pdf`):
   “cvDiurnal kry bp solves the same problem as cvDiurnal kry, with
   the BDF/GMRES method and a banded preconditioner … The problem is
   solved twice: with preconditioning on the left, then on the right.”
   The booklet describes the **PDE / solver setup**, not command-line
   flags.
4. Source header (both tags): time interval `0 <= t <= 86400 sec
   (1 day)`, `NOUT 12` output times, left then right preconditioning.
   A 60 s spawn timeout may honestly become `E_PROFILE_TIMEOUT`.
5. CVODE Usage documents `CVodeSetOptions(..., argc, argv)` and
   examples such as `cvode.max_order 3`. That is a **library API for
   programs that call it**. This example source does not call it.
   Passing `cvode.*` / `--help` / `--version` would be invented.

009 cmake help (evidence `5ca76737`) already lists the exact target
`cvDiurnal_kry_bp`. Using `--target cvDiurnal_kry_bp` is
listing-backed.

Documented spawn extra-argv: **none**. `argv[0]` may be the program
name only.

## Packet licensed by this note

`docs/review_20260819/execution_packet_2026-08-20-010.md`

Not licensed: `ENABLE_XBRAID`, `ENABLE_LAPACK`, extra EXAMPLE tokens
(`--help`, `cvode.max_order`, …), default `all`, re-spawn
`POSIX_TIMER_TEST/ltest`, P2-D.
