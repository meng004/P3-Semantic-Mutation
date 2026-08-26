# Official-doc lookup — frozen PROJECT_TEST `[4]` argv

- Reviewer: 评审模型（流程总控）；本会话不改生产代码
- Trigger (author, verbatim): `2，点名下一冻结行；你先读官网/issue 再写 argv，不臆造`
- Recorded: 2026-08-20
- Named row: frozen `selected_behavior_ids[4]`
  `04321f42383ae60108c6113034b91f1bda7e03a21090fe400895e58f70e2f69d`
- Public-behavior-frame fields:
  - category: `PROJECT_TEST`
  - entrypoint: `ctest:NAME`
  - `declared_inputs.argv_tokens`: `["ctest", "-R", "^NAME$"]`
  - `prerequisites: []`
  - provenance: `test/unit_tests/kinsol/C_serial/CMakeLists.txt` `L60`
- paper-search-mcp: unavailable (`GetMcpTools` catalog miss on
  `paper-search|crossref|arxiv|dblp`; only `cursor-cloud` present).
  Fallback = official HTML + GitHub raw / issues (software-repo docs).

This note records **what the official sources say**. It does not
treat the unexpanded CMake keyword `NAME` as a CTest name, and it
does not pass `SUNDIALS_TEST_UNITTESTS=ON`.

## 检索审计

| Ref | 工具链 | 命中工具 | 状态 |
|-----|--------|---------|------|
| paper-search-mcp | GetMcpTools catalog | none | ✗ catalog miss; fallback |
| KINSOL C serial `CMakeLists.txt` `v6.7.0` | curl raw + nl | curl | ✓ L19 `kin_test_getuserdata` + empty args; L61 `add_test(NAME ${test_name} …)` |
| `kin_test_getuserdata.c` `v6.7.0` | WebFetch raw | WebFetch | ✓ `main` does not consume `argv[1+]`; prints `SUCCESS` |
| Top-level `CMakeLists.txt` `v6.7.0` | WebFetch raw | WebFetch | ✓ `if(SUNDIALS_TEST_UNITTESTS) add_subdirectory(test/unit_tests)` |
| `SUNDIALS_TEST_UNITTESTS` | curl `SundialsBuildOptionsPre.cmake` | curl | ✓ `BOOL` “Include unit tests in make test” default `OFF` |
| Local testing `v6.7.0` | WebFetch readthedocs | WebFetch | ✓ docker `test_driver.sh`; no `^NAME$`; no this-test integers |
| GitHub issues `kin_test_getuserdata` | WebFetch issues search | WebFetch | ✓ **No results** |
| GitHub issues `ctest NAME unit_tests kinsol` | WebFetch issues search | WebFetch | ✓ **No results** |
| 009 cmake help | `origin/cursor/p2c-local-tar-object-58d6` | git show | ✓ 0 lines `kin_test_getuserdata` |
| 009 `ctest_names` | same branch `object-resolution.json` | git show | ✓ 12 names; no `kin_test_getuserdata`; no `NAME` |

## What `ctest:NAME` / `^NAME$` actually is

Quoted file, tag `v6.7.0`, numbered bytes
`https://raw.githubusercontent.com/LLNL/sundials/v6.7.0/test/unit_tests/kinsol/C_serial/CMakeLists.txt`:

```text
18  set(unit_tests
19    "kin_test_getuserdata\;"
20    )
...
53    if("${test_args}" STREQUAL "")
54      set(test_name ${test})
...
60    # add test to regression tests
61    add_test(NAME ${test_name} COMMAND ${test} ${test_args})
```

The frozen provenance span `L60` is the comment immediately above
`add_test`. The CMake keyword after `add_test(` is literally `NAME`.
The adapter stored that keyword as the CTest name. Official CMake
does **not** register a test called `NAME`.

The only tuple in `unit_tests` is `"kin_test_getuserdata\;"`: the
args field is empty, so `test_name` is set to `test`, which is
`kin_test_getuserdata`. Official registration is therefore:

```text
add_test(NAME kin_test_getuserdata COMMAND kin_test_getuserdata)
```

Do **not** write argv `["ctest", "-R", "^NAME$"]`. That regex is
the unexpanded keyword, not an official test.

## Official extra argv (empty)

Quoted unit-test source, same tag
`https://raw.githubusercontent.com/LLNL/sundials/v6.7.0/test/unit_tests/kinsol/C_serial/kin_test_getuserdata.c`:

- Signature is `int main(int argc, char *argv[])`.
- The body never reads `argv[1]` or later.
- Success path prints `SUCCESS` and `return 0`.

The CMake tuple’s args field is empty. Official extra-argv tokens
are **none**.

## Official enable switch (not passed in packet 012)

Quoted top-level `CMakeLists.txt` `v6.7.0`:

```text
if(SUNDIALS_TEST_UNITTESTS)
  add_subdirectory(test/unit_tests)
endif()
```

Quoted `cmake/SundialsBuildOptionsPre.cmake` `v6.7.0`:

```text
sundials_option(SUNDIALS_TEST_UNITTESTS BOOL
  "Include unit tests in make test" OFF ADVANCED)
```

Default is **OFF**. 009’s default-configure `ctest -N` listed 12
example names and neither `kin_test_getuserdata` nor `NAME`. 009
cmake help has 0 lines for `kin_test_getuserdata`. That matches
the official default.

Newer trees rename the switch to `SUNDIALS_TEST_ENABLE_UNIT_TESTS`.
Neither name is passed in packet 012 (standing no guessed `-D`;
the switch would change the default-configure object, not the
official extra argv).

GitHub issue searches for `kin_test_getuserdata` and
`ctest NAME unit_tests kinsol` returned **No results**.

## Instantiatable argv written from official text

```text
["kin_test_getuserdata"]
```

That is the official executable / CTest name, with **no** extra
tokens and **not** `ctest -R`. Official `COMMAND` is the test
binary itself. Packet 009 already forbade `ctest -R` as a spawn
substitute; this row’s CMakeLists agrees.

## Conclusion used by packet 012

1. Next frozen row is `[4]` (`04321f42…`, PROJECT_TEST).
2. `^NAME$` is not official argv.
3. Official name is `kin_test_getuserdata`; extra argv is empty.
4. `SUNDIALS_TEST_UNITTESTS` default is OFF; do not pass it.
5. Packet 012 is default configure + this-job help / `ctest -N`.
   `--target kin_test_getuserdata` only if **this job’s** help has
   that exact name. Spawn only that kept binary, argv program name
   only. Else `E_PROFILE_BINARY_ABSENT`.

Do not copy this close onto the other 15 frozen rows.
Do not start P2-D.
