# Official-doc lookup — frozen BENCHMARK `[3]` argv

- Reviewer: 评审模型（流程总控）；本会话不改生产代码
- Trigger (author, verbatim): `点名下一冻结行；你先读官网/issue 再写 argv，不臆造`
- Recorded: 2026-08-20
- Named row: frozen `selected_behavior_ids[3]`
  `ade4089bc6d65c77e8aff681d61d4649f4edb42892292a307533513379b8f5ff`
- Entrypoint (public-behavior-frame row 527):
  `benchmarks/nvector/serial/test_nvector_performance_serial.c`
- Category: `BENCHMARK`; `prerequisites: []`; `declared_inputs.source_path` only
- paper-search-mcp: unavailable (`GetMcpTools` catalog miss on
  `paper-search|crossref|arxiv|dblp`; only `cursor-cloud` present).
  Fallback = official HTML + GitHub raw / issues (software-repo docs;
  CLAUDE.md §7 textbook/standard/software-repo skip).

This note records **what the official sources say**. It does not
invent six integers, and it does not treat `SUNDIALS_BENCHMARK_NUM_CPUS`
or any other CMake cache default as those integers.

## 检索审计

| Ref | 工具链 | 命中工具 | 状态 |
|-----|--------|---------|------|
| paper-search-mcp | GetMcpTools catalog | none | ✗ catalog miss; fallback |
| Serial `main` tag `v6.7.0` | curl raw GitHub | curl | ✓ `argc < 7` → usage + `return(-1)` |
| Shared perf `.c` `v6.7.0` | WebFetch raw | WebFetch | ✓ helpers only; no CLI defaults |
| Serial `CMakeLists.txt` `v6.7.0` | WebFetch raw | WebFetch | ✓ target `nvector_serial_benchmark`; no `BENCHMARK_ARGS` |
| `sundials_add_nvector_benchmark` `v6.7.0` | WebFetch raw | WebFetch | ✓ parses `SOURCES` / `SUNDIALS_TARGETS` / `LINK_LIBRARIES` / `INSTALL_SUBDIR` only |
| `BUILD_BENCHMARKS` `v6.7.0` | WebFetch raw `SundialsBuildOptionsPre.cmake` | WebFetch | ✓ `BOOL` “Build the SUNDIALS benchmark suite” default `OFF` |
| `SUNDIALS_BENCHMARK_NUM_CPUS` | same file | WebFetch | ✓ default `"40"`; CPT core count, **not** nvector argv |
| CPT Benchmarking `v6.7.0` | curl readthedocs HTML | curl | ✓ “edit the respective CMakeLists.txt”; `sundials_add_benchmark` |
| Developer Benchmarks index `v6.7.0` | WebFetch raw rst | WebFetch | ✓ toctree = advection_reaction + diffusion only |
| GitHub issues `test_nvector_performance_serial` | WebFetch issues search | WebFetch | ✓ **No results** |
| GitHub issues `nvector_serial_benchmark` | WebFetch issues search | WebFetch | ✓ **No results** |
| GitHub issues `test_nvector_performance` | WebFetch issues search | WebFetch | ✓ **No results** |
| 009 cmake help | `origin/cursor/p2c-local-tar-object-58d6` | git show | ✓ 0 lines matching `nvector` / `benchmark` / `test_nvector` |
| 010 cmake help | `origin/cursor/p2c-local-tar-example-58d6` | git show | ✓ same: 0 lines |

## Official argv schema (written; not invented values)

Quoted `main` at tag `v6.7.0`
`https://raw.githubusercontent.com/LLNL/sundials/v6.7.0/benchmarks/nvector/serial/test_nvector_performance_serial.c`
(exact bytes via curl; HTML conversion of the same URL strips the
format strings):

```text
if (argc < 7){
  printf("ERROR: SIX (6) arguments required: ");
  printf("<vector length> <number of vectors> <number of sums> <number of tests> ");
  printf("<cache size (MB)> <print timing>\n");
  return(-1);
}
```

Field meanings and constraints from the **same** `main` (still not
values):

| argv | Official label | Official constraint |
|---|---|---|
| `[1]` | vector length | `atol`; must be `> 0` else `return(-1)` |
| `[2]` | number of vectors | `atol`; `< 1` prints a warning and disables fused-op tests |
| `[3]` | number of sums | `atol`; `< 1` prints a warning and disables some fused-op tests |
| `[4]` | number of tests | `atol`; must be `> 0` else `return(-1)` |
| `[5]` | cache size (MB) | `atol`; must be `≥ 0` else `return(-1)` |
| `[6]` | print timing | `atoi`; passed to `SetTiming` |

Official sources **do not** give six integers that satisfy those
constraints. Do **not** write `1000 10 10 1 0 0` or any other
fabricated tuple. Do **not** spawn with only the program name in
order to harvest the usage line (`argc < 7` is a documented fail,
not an official run).

## Official program / target name (this is the instantiable argv)

Quoted serial `CMakeLists.txt` tag `v6.7.0`
`https://raw.githubusercontent.com/LLNL/sundials/v6.7.0/benchmarks/nvector/serial/CMakeLists.txt`:

```text
sundials_add_nvector_benchmark(nvector_serial_benchmark
  SOURCES test_nvector_performance_serial.c
  SUNDIALS_TARGETS sundials_nvecserial
  INSTALL_SUBDIR nvector/serial
)
```

There is no `BENCHMARK_ARGS` (or any other runargs keyword) on that
call. The CMake **target / executable name** is
`nvector_serial_benchmark`, not the source stem
`test_nvector_performance_serial`.

Quoted macro
`https://raw.githubusercontent.com/LLNL/sundials/v6.7.0/cmake/macros/SundialsAddExecutable.cmake`:

```text
macro(sundials_add_nvector_benchmark NAME)
  ...
  cmake_parse_arguments(arg
    "${options}" "${singleValueArgs}" "${multiValueArgs}" ${ARGN})
  add_executable(${NAME}
    ${BENCHMARKS_DIR}/nvector/test_nvector_performance.c
    ${arg_SOURCES})
```

`multiValueArgs` are `SOURCES SUNDIALS_TARGETS LINK_LIBRARIES
INSTALL_SUBDIR` only. The macro does not accept or default a
six-integer argv.

**Instantiatable argv written from official text, without
invention:**

```text
["nvector_serial_benchmark"]
```

That is the program name. The six extra tokens remain **schema
only**.

## Official build switch (not passed in packet 011)

Quoted `v6.7.0`
`https://raw.githubusercontent.com/LLNL/sundials/v6.7.0/cmake/SundialsBuildOptionsPre.cmake`:

```text
sundials_option(BUILD_BENCHMARKS BOOL "Build the SUNDIALS benchmark suite" OFF)
```

Same file also defines `SUNDIALS_BENCHMARK_NUM_CPUS` default `"40"`
and `SUNDIALS_BENCHMARK_NUM_GPUS` default `"4"`. Those are CPT worker
counts for `make benchmark`. They are **not**
`<vector length> <number of vectors> …`. Using `40` as argv`[1]`
would be invention.

Quoted CPT page
`https://sundials.readthedocs.io/en/v6.7.0/developers/testing/Benchmarking.html`:

> Turning on the BUILD_BENCHMARKS option will build benchmarks.
> Running make benchmark will execute all the available benchmarks
> and produce .cali output files for each one. To change what
> parameters benchmarks are run with, edit the respective
> CMakeLists.txt. The BENCHMARK_VARS variable determines how many
> tests to run with different parameters. Arguments passed into the
> sundials_add_benchmark macro change how the benchmark is run.

That paragraph names `sundials_add_benchmark`, not
`sundials_add_nvector_benchmark`. The serial nvector
`CMakeLists.txt` does not call `sundials_add_benchmark` and does not
set `BENCHMARK_VARS`. Official docs tell a developer to **edit
CMakeLists.txt** to change parameters. This process will not edit
the extracted tree’s CMakeLists.

Newer docs rename the switch to `SUNDIALS_ENABLE_BENCHMARKS`
(default `OFF`; replaces deprecated `BUILD_BENCHMARKS`). The
developer Benchmarks index at `v6.7.0` only toctrees
advection_reaction and diffusion. Neither page lists six nvector
integers.

GitHub issue searches for
`test_nvector_performance_serial`, `nvector_serial_benchmark`, and
`test_nvector_performance` each returned **No results**.

## What 009 / 010 already listed (default configure)

Independent of this lookup, persisted cmake help on the 009 and 010
executor branches contains **zero** lines matching `nvector`,
`benchmark`, or `test_nvector`. Exact target
`nvector_serial_benchmark` is absent under the standing default
configure (no extra `-D`). That matches `BUILD_BENCHMARKS` default
`OFF`.

## Conclusion used by packet 011

1. Next frozen row is `[3]` (`ade4089bc6d6…`, BENCHMARK).
2. Official extra-argv **meanings** are the six fields above.
3. Official extra-argv **values** are not in source, CMakeLists,
   macro, CPT docs, or issues.
4. Instantiatable argv is therefore **only**
   `["nvector_serial_benchmark"]`.
5. Packet 011 does **not** pass `-DBUILD_BENCHMARKS=ON` or
   `-DSUNDIALS_ENABLE_BENCHMARKS=ON` (standing no guessed `-D`;
   the switch would still not supply six integers).
6. Packet 011 does **not** `--target` or spawn this binary.
7. Expected honest close under default configure:
   `E_PROFILE_BINARY_ABSENT`.

Do not copy this close onto the other 16 frozen rows.
Do not start P2-D.
