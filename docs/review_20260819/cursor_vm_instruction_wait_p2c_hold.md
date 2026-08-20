# Cursor VM instruction — current hold

**Current authorized executor paste:**
`docs/review_20260819/cursor_vm_instruction_2026-08-20-012.md`.

012 is issued for frozen PROJECT_TEST `[4]`. Official-doc note:
`docs/review_20260819/official_docs_2026-08-20-project-test-kinsol-unit.md`.

Instantiatable argv is `["kin_test_getuserdata"]` only.
Do not use `["ctest", "-R", "^NAME$"]`. Do not `ctest -R`.
Do not pass `SUNDIALS_TEST_UNITTESTS` or
`SUNDIALS_TEST_ENABLE_UNIT_TESTS`.
Do not retry `ltest` / the 011 benchmark. Do not pass
`ENABLE_XBRAID` / `ENABLE_LAPACK` / `BUILD_BENCHMARKS`.
Do not start P2-D.
