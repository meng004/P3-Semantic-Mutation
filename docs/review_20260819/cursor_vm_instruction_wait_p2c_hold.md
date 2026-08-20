# Cursor VM instruction — superseded hold

**Current authorized executor paste:**
`docs/review_20260819/cursor_vm_instruction_2026-08-20-wait-after-011.md`.

011 C1 is closed (`E_PROFILE_BINARY_ABSENT` on frozen BENCHMARK
`[3]`). Official-doc note:
`docs/review_20260819/official_docs_2026-08-20-nvector-serial-benchmark.md`.
Do not invent six integers. Do not pass `BUILD_BENCHMARKS` or
`SUNDIALS_ENABLE_BENCHMARKS`. Do not spawn this binary.
Do not retry `ltest`. Do not pass `ENABLE_XBRAID` or `ENABLE_LAPACK`.
Do not start P2-D. Do not issue 012.
