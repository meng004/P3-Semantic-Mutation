# P3 NumPy Frozen Workload Executability Audit

## Terminal status

`WORKLOAD_EXECUTION_UNDERSPECIFIED`

The frozen 20-row workload cannot be executed completely without adding
post-freeze execution semantics. Seventeen rows have a mechanically derivable
Python callable or argv boundary. Three `EXAMPLE` rows provide only a source
path and do not freeze the action needed to execute that source. The workload
is therefore not eligible for runner implementation or a formal profiling run.

## Frozen identity

- P3 snapshot: `25f0ebf5944328aa5b436c810739c8f9176213a9`
- Neutral snapshot: `4e7e9556b3d621681c88c82f26cd95f5604d7a8b85cc56bf7e6d4db5a274f38b`
- Source archive SHA-256: `c73c0ec41ea53ba9ecb0f9903a55a19ed6c1dbfd1de00404d96b58d9c30bb3c9`
- Observed normalized source tree SHA-256: `f8826c3b975f8699e136e0b6b4cd4c29bf0d7e9a3be04fe09b947eb8998e727b`
- Materialized source entries: 2,047
- Descriptor SHA-256: `c6efda5c841b1900a51b69dc3982168098752015351a7e7fa07f201e70f99836`
- Phase-1 adapter status: `EXECUTABLE`
- Frozen rows: 20

## Prespecified audit rule

A row is executable as frozen only when existing fields uniquely determine an
argv or Python callable, the committed input schema has an existing generator,
the execution can be contained to the controlled source, and no human must
choose a setup action, compiler invocation, test case, benchmark method, or API
meaning. All 20 rows must pass. One underspecified row makes the workload
terminally underspecified; rows are not dropped or replaced.

## Per-row result

| # | Behavior | Category | Frozen entrypoint | Mapping | Verdict |
|---:|---|---|---|---|---|
| 1 | `21c3fbce…ab37` | PUBLIC_API | `numpy.lib.tests.test_stride_tricks:test_same` | direct zero-argument callable | derivable |
| 2 | `4b791667…22e3` | CLI | `f2py = numpy.f2py.f2py2e:main` | frozen `argv_tokens=["f2py"]` | derivable |
| 3 | `8c1ab782…12da` | EXAMPLE | `numpy/_core/tests/examples/cython/setup.py` | source path only; no setup command/action | **underspecified** |
| 4 | `637f4653…16c5` | BENCHMARK | `python benchmarks/benchmarks/bench_core.py` | frozen Python argv | derivable |
| 5 | `432bf4f2…3b96` | PUBLIC_API | `numpy.distutils.tests.test_shell_utils:test_roundtrip` | direct callable + committed schema generator | derivable |
| 6 | `8d7480fa…6714` | EXAMPLE | `numpy/_core/tests/examples/limited_api/setup.py` | source path only; no setup command/action | **underspecified** |
| 7 | `923f8cfd…6c89` | BENCHMARK | `python benchmarks/benchmarks/bench_trim_zeros.py` | frozen Python argv | derivable |
| 8 | `f9b72545…b48cf` | PUBLIC_API | `numpy.testing.tests.test_utils:TestAssertAllclose` | direct zero-argument class construction | derivable |
| 9 | `b5887a06…13db` | EXAMPLE | `numpy/_core/tests/examples/limited_api/limited_api1.c` | source path only; no compiler, flags, harness, or invocation | **underspecified** |
| 10 | `367a578a…e2f1` | BENCHMARK | `python benchmarks/benchmarks/bench_reduce.py` | frozen Python argv | derivable |
| 11 | `d58ee489…4321` | PUBLIC_API | `numpy.distutils.tests.test_log:test_log_prefix` | direct callable + committed schema generator | derivable |
| 12 | `9388a52e…3965` | BENCHMARK | `python benchmarks/benchmarks/common.py` | frozen Python argv | derivable |
| 13 | `3d77e0bc…e2aa` | PUBLIC_API | `numpy.matlib:ones` | direct callable + committed schema generator | derivable |
| 14 | `d7c82268…52e0` | BENCHMARK | `python benchmarks/benchmarks/bench_ufunc_strides.py` | frozen Python argv | derivable |
| 15 | `0ba742bf…7bef` | PUBLIC_API | `numpy.f2py.tests.test_common:TestCommonWithUse` | direct zero-argument class construction | derivable |
| 16 | `85f69772…67cb` | BENCHMARK | `python benchmarks/benchmarks/__init__.py` | frozen Python argv | derivable |
| 17 | `93ff5490…dfef` | PUBLIC_API | `numpy.f2py.crackfortran:crack2fortran` | direct callable + committed schema generator | derivable |
| 18 | `486fa0bb…b345` | BENCHMARK | `python benchmarks/benchmarks/bench_strings.py` | frozen Python argv | derivable |
| 19 | `a41458f4…4e14` | PUBLIC_API | `numpy.ma.core:diag` | direct callable + committed schema generator | derivable |
| 20 | `f96a32a8…af04` | BENCHMARK | `python benchmarks/benchmarks/bench_import.py` | frozen Python argv | derivable |

Summary: 17 derivable / 3 underspecified / 20 audited.

## Why Phase-1 `EXECUTABLE` does not override this result

The Meson adapter's `EXECUTABLE` discovery status means that its frozen
syntactic rules admitted declarations into the Public Behavior Frame. For the
Python-package branch, paths below top-level `examples/` or `benchmarks/` receive
explicit argv declarations, while other path-evidenced examples can retain only
`declared_inputs.source_path`. The three failing rows are the latter kind. The
adapter does not supply the missing build action, compiler boundary, or setup
command, and no existing production profiling runner defines them.

## Scientific interpretation

- Observed: the frozen Phase-1 selection contains three rows whose discovery
  evidence does not uniquely specify execution.
- Qualified: this is a limitation of this frozen NumPy workload and the current
  adapter-to-runner boundary, not a claim that NumPy cannot be profiled.
- Blocked: removing the three rows, inventing setup/compile commands, replacing
  the subject, or treating a 17-row receipt as the frozen 20-row workload.
- Speculative: a future prospectively frozen workload with explicit argv/harness
  fields could yield subject-level technique evidence.

## Required stop

Do not implement `python_profiling_runner.py`, do not create a formal receipt,
and do not request formal profiling authorization for this workload. The next
scientific decision is whether to retain technique-stratified C2 wording as a
future-work target or amend the protocol prospectively for a new cohort. This
decision must not rewrite the frozen NumPy or Boost.Math observations.

## Actions not taken

- No workload row, schema, generator, adapter, or source file was modified.
- No NumPy command, setup script, compiler, benchmark, test, or callable was run.
- No production runner or profiling receipt was created.
- No subject was substituted and no formal profiling retry occurred.
