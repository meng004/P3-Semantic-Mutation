# Official-doc lookup — `ltest` and frozen EXAMPLE argv

- Reviewer: 评审模型（流程总控）；本会话不改生产代码
- Trigger (author, verbatim): `读取被测程序的官网帮助文档或issue，不瞎猜参数取值及其意义。`
- Recorded: 2026-08-20
- paper-search-mcp: unavailable in this environment (catalog miss);
  fallback = official HTML/PDF + GitHub raw/issues

This note only records **what the official sources say**. It does not
guess `-D` values or invent CLI tokens.

## 检索审计

| Ref | 工具链 | 命中 | 状态 |
|-----|--------|------|------|
| Install (XBraid options) | WebSearch → readthedocs v7.2.1 | `ENABLE_XBRAID` default **OFF**; needs `XBRAID_DIR`, MPI, index 32, double | ✓ |
| `cmake/tpl/SundialsXBRAID.cmake` master | WebFetch raw GitHub | no `ltest` token; `try_compile` of `test.c` | ✓ |
| same file tag `v6.7.0` | WebFetch raw GitHub | `project(ltest C)` + `add_executable(ltest ltest.c)` (~L96) | ✓ |
| GitHub issue #4 | WebFetch | maintainer patch quotes `PROJECT(ltest C)` in a TPL check `CMakeLists.txt` | ✓ |
| GitHub issue #74 | WebSearch | build log `CMakeFiles/ltest.dir/ltest.o -o ltest` (link check) | ✓ |
| EXAMPLE source | WebFetch raw `examples/cvode/serial/cvDiurnal_kry_bp.c` | `int main(void)` — no `argc`/`argv` | ✓ |
| EXAMPLE target name | 009 evidence `cmake-help.stdout.txt` | exact line `... cvDiurnal_kry_bp` | ✓ (already in-repo) |

## What official text says about `ltest`

1. User install docs describe `ENABLE_XBRAID` as the **ARKStep +
   XBraid interface**, default **OFF**. They do **not** document a
   user program named `ltest`, nor `--help` / `--version` for it.
   Source:
   `https://sundials.readthedocs.io/en/v7.2.1/sundials/Install_link.html`

2. Phase 1 provenance path `cmake/tpl/SundialsXBRAID.cmake` L96 on
   tag `v6.7.0` is the generated TPL check
   `add_executable(ltest ltest.c)`, not a product CLI.
   Current `master` dropped that name.

3. Issues #4 and #74 show the same `ltest` string as a **CMake TPL /
   Check\* link-test executable**, not a documented command.

**Conclusion (docs, not a guess):** the pinned CLI token `ltest` is
the adapter reading a configure-time check binary. Official user
help does not give parameters for it. Enabling `ENABLE_XBRAID` is
**not** documented as “build the CLI `ltest`.” Do not pass that
`-D` to manufacture a CLI. 009 `E_PROFILE_BINARY_ABSENT` stays the
close for `13b2cddc…` under default configure.

## What official text says about frozen `[2]` EXAMPLE

- Frozen path:
  `examples/cvode/serial/cvDiurnal_kry_bp.c`
  (`c103b0c611dded134d189f8deedb54ad7a7170b1d78fb12a7851b88ce4115e4f`).
- Official `main` is `int main(void)`. No command-line parameters
  are read. Extra tokens would be invented.
- 009 cmake help (evidence `5ca76737`) already lists the exact
  target `cvDiurnal_kry_bp`. Using `--target cvDiurnal_kry_bp` is
  listing-backed, not a guessed name.
- Documented spawn extra-argv: **none**. `argv[0]` may be the
  program name only.

## Packet licensed by this note

`docs/review_20260819/execution_packet_2026-08-20-010.md`

Not licensed: `ENABLE_XBRAID`, extra EXAMPLE flags, default `all`,
re-spawn `POSIX_TIMER_TEST/ltest`, P2-D.
