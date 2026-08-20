# Official-doc lookup — frozen PUBLIC_API `[5]` argv

- Reviewer: 评审模型（流程总控）；本会话不改生产代码
- Trigger (author, verbatim): `点名下一冻结行；你先读官网/issue 再写 argv，不臆造`
- Recorded: 2026-08-20
- Named row: frozen `selected_behavior_ids[5]`
  `ab27acfcaaf2f1dbdbd965d57f645c4f948520bd4998f62c3cc8ccdfb3ccd320`
- Public-behavior-frame row 70 / selected_rows[5]:
  - category: `PUBLIC_API`
  - entrypoint: `include/nvector/nvector_serial.h`
  - `declared_inputs`: `{"header":"include/nvector/nvector_serial.h"}` only
  - `prerequisites: []`
  - provenance: `include/nvector/nvector_serial.h` / `path`
- paper-search-mcp: unavailable (`GetMcpTools` catalog miss on
  `paper-search|crossref|arxiv|dblp|semantic|openalex`; only
  `cursor-cloud` present). Fallback = official HTML + GitHub raw /
  issues (software-repo docs; CLAUDE.md §7 textbook/standard/software
  repo skip).

This note records **what the official sources say**. It does not
invent a process name, a compile probe, or a redirect to another
frozen row.

## 检索审计

| Ref | 工具链 | 命中工具 | 状态 |
|-----|--------|---------|------|
| paper-search-mcp | GetMcpTools catalog | none | ✗ catalog miss; fallback |
| Header tag `v6.7.0` | WebFetch raw | WebFetch | ✓ “header file for the serial implementation of the NVECTOR module”; exports `N_VNew_Serial` etc.; **no `main`** |
| User guide §9.9 `v6.7.0` | WebFetch readthedocs | WebFetch | ✓ include `nvector_serial.h`; link `libsundials_nvecserial.lib`; constructor is a library call |
| GitHub issues `nvector_serial.h` | WebFetch issues search | WebFetch | ✓ hits are unrelated (deprecated warnings, Kokkos install, MATLAB, CVode segfaults, …); **no CLI for this header** |
| GitHub issues `N_VNew_Serial argv` | WebFetch issues search | WebFetch | ✓ no process-argv recipe for this header |
| `sundials_cli.h` `v6.7.0` | WebFetch raw | WebFetch | ✓ **404** at `include/sundials/sundials_cli.h` |
| Other-object example CMakeLists `v6.7.0` | WebFetch raw | WebFetch | ✓ `test_nvector_serial` + official tuples `1000 0` / `10000 0` — **different entrypoint** |
| Other-object `test_nvector_serial.c` `v6.7.0` | WebFetch raw | WebFetch | ✓ `argc < 3` usage; not this frozen header |
| GitHub issues `test_nvector_serial` | WebFetch issues search | WebFetch | ✓ build/spack noise; does not reassign this PUBLIC_API row |

## Official object (this frozen row)

Quoted header, tag `v6.7.0`
`https://raw.githubusercontent.com/LLNL/sundials/v6.7.0/include/nvector/nvector_serial.h`:

```text
 * This is the header file for the serial implementation of the
 * NVECTOR module.
```

The same file exports constructors and vector operations
(`N_VNew_Serial`, `N_VLinearSum_Serial`, …). It does **not**
declare `main`. It has **no** usage `printf` and **no** `argc` /
`argv` contract.

Quoted user guide, tag `v6.7.0`
`https://sundials.readthedocs.io/en/v6.7.0/nvectors/NVector_links.html`
(§9.9 The NVECTOR_SERIAL Module):

> The header file to be included when using this module is
> `nvector_serial.h`. The installed module library to link to is
> `libsundials_nvecserial.lib` where `.lib` is typically `.so` for
> shared libraries and `.a` for static libraries.

Quoted constructor on the same page:

```text
N_Vector N_VNew_Serial(sunindextype vec_length, SUNContext sunctx)
This function creates and allocates memory for a serial N_Vector.
Its only argument is the vector length.
```

That is a **library call**, not a process. Official docs do not
give a program name, extra CLI tokens, or a `cc -c` recipe for
this header.

Frozen `declared_inputs` has only `header`. The adapter did not
store process argv. That matches the official sources.

## Official process argv written (not invented)

```text
[]
```

There is no instantiable subject process. Do **not** write
`["nvector_serial"]`. Do **not** write
`["nvector_serial.h"]`. Do **not** compile a translation unit.

`create_intent` still rejects an empty intent `argv` list
(`src/p3_v3/run_records.py`: “intent argv must contain nonempty
strings”). Packet 013 therefore uses the same **script-invocation**
intent argv as packet 003. That list is the packet runner, **not**
a subject CLI.

## Other object (must not be substituted)

Quoted `examples/nvector/serial/CMakeLists.txt` tag `v6.7.0`:

```text
set(nvector_serial_examples
  "test_nvector_serial\;1000 0\;"
  "test_nvector_serial\;10000 0\;"
)
```

Quoted `examples/nvector/serial/test_nvector_serial.c` tag `v6.7.0`:

```text
if (argc < 3){
  printf("ERROR: TWO (2) Inputs required: vector length, print timing \n");
  ...
  return(-1);
}
```

Those tuples belong to **example** entrypoint
`examples/nvector/serial/test_nvector_serial.c`, not to frozen
`[5]`. Using `["test_nvector_serial","1000","0"]` here would
rewrite the selection set. Packet 013 forbids that redirect.

GitHub issue searches for `nvector_serial.h` and
`N_VNew_Serial argv` do not supply a process for this header.
`include/sundials/sundials_cli.h` is **absent** at tag `v6.7.0`.

## Conclusion used by packet 013

1. Next frozen row is `[5]` (`ab27acfc…`, PUBLIC_API header).
2. Official subject process argv is **empty**.
3. Intent argv is the 013 script invocation (nonempty; 003
   precedent; not a fake subject CLI).
4. No cmake `-D`, no `--target`, no compiler, no spawn.
5. Expected honest close when the header is a regular file:
   `MISSING_WITH_REASON` / `E_PROFILE_NO_PROCESS_ARGV`.
6. Do **not** re-book frozen `[0]` as the same close.
7. Do **not** copy this close onto frozen headers `[9]`, `[13]`,
   or `[17]`.

Do not start P2-D.
