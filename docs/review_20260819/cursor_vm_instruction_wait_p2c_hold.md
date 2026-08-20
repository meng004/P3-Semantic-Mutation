# Cursor VM instruction — superseded hold

**Current authorized executor paste:**
`docs/review_20260819/cursor_vm_instruction_2026-08-20-wait-after-013.md`.

013 C1 is closed (`E_PROFILE_NO_PROCESS_ARGV` on frozen PUBLIC_API
`[5]`). Official-doc note:
`docs/review_20260819/official_docs_2026-08-20-nvector-serial-header.md`.
Official subject process argv is `[]`. Do not invent
`nvector_serial`. Do not redirect to `test_nvector_serial` /
`1000 0`. Do not cmake, compile, or spawn. Do not retry `ltest` /
010–012 objects. Do not pass `ENABLE_XBRAID` / `ENABLE_LAPACK` /
`BUILD_BENCHMARKS` / `SUNDIALS_TEST_UNITTESTS`. Do not start P2-D.
Do not issue 014. Do not copy this close onto other headers.
