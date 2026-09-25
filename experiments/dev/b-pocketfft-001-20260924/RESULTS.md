# B-POCKETFFT-001 developmental trial (2026-09-24)

Status: developmental feasibility run. Not a P3 blind confirmatory sample.
B-POCKETFFT-001 is a known defect. T1 is the P12 admission reference MR and
is excluded from the P3 primary detection rate. A1 is its weakened form and
is also excluded. P3 claim ledger, frozen experiment terminals, and paper
claims were not edited.

## Identity

| Item | Value |
|---|---|
| Date | Thu Sep 24 22:48:00 CST 2026 |
| Host | Darwin arm64, xnu-13432.1.9, Apple clang 17.0.0 (clang-1700.0.13.3) |
| P3 HEAD | `e883e5ca20969d6cf23f3a23c4ff4ea3df299c5b` (clean before this trial directory) |
| P12 commit | `fc3bb70e11b93ca207296a1101c35973d96128f0` |
| PocketFFT fixed | `fb21e4016b96f50a83c516fc0acabe8def4b3bb5` |
| PocketFFT real defect | `076cb3d2536b7c5d0629093ad886e10ac05f3623` (parent of the fix) |

## Verdict

- Construction: success. The candidate compiles and runs.
- Independent certification: success. On the fixed header the direct DST-II/III
  formulas match PocketFFT (`ESTABLISH: PASS`, exit 0). On the candidate, the
  pre-specified pattern holds: DST-II ortho `c[N-1]` is 2× the reference and
  every other checked coefficient matches (`EXPECT_DST2_LAST_X2: PASS`, exit 0).
- Non-reference checks: none detects the candidate. B1-1..B1-3 and B2-1..B2-8
  all print `PASS`. B2-3 and B2-4 compare one program output against a direct
  formula, so they are reference-oracle checks rather than MRs. The remaining
  nine checks are MRs; none detects this target deviation. The original P12
  selected B2 group is B2-1, B2-5, B2-8 (0/3 detected); this trial also ran
  the other five B2 pool members as exploratory checks.
- T1 (positive control only) prints `OVERALL: FAIL` on the candidate. That
  result is not a P3 primary detection.
- No new MR was added after seeing these outcomes.

The real-defect arm is a separate measurement. Its T1 errors match the P12
record to the printed buggy digits. Its B1/B2 rows are also all `PASS`.
The candidate is not that defect: the real defect fails the pre-specified
`c[N-1] × 2` check (`EXPECT_DST2_LAST_X2: FAIL`).

## What this run does not show

No budget-matched syntactic-mutant execution was done here. P12's note of 27
compilable syntactic mutants is background only. This run does not show that a
semantic-target method beats syntactic mutation, and it is not confirmatory
evidence for a P3 metric.

## Primary table

Labels: `match` = independent formula agrees; `certified-dev` = pre-specified
numerical deviation; `other-dev` = formula disagrees, but not the pre-specified
candidate pattern; `MR-hit` = relation violated; `MR-miss` = relation holds;
`fail` = compile/run failure. A1 is omitted here (excluded; raw logs exist).

| Version | Certifier | T1 (control) | B1-1 | B1-2 | B1-3 | B2-1 | B2-2 | B2-3 | B2-4 | B2-5 | B2-6 | B2-7 | B2-8 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| fixed | match | MR-miss | MR-miss | MR-miss | MR-miss | MR-miss | MR-miss | MR-miss | MR-miss | MR-miss | MR-miss | MR-miss | MR-miss |
| real defect | other-dev | MR-hit | MR-miss | MR-miss | MR-miss | MR-miss | MR-miss | MR-miss | MR-miss | MR-miss | MR-miss | MR-miss | MR-miss |
| candidate | certified-dev | MR-hit | MR-miss | MR-miss | MR-miss | MR-miss | MR-miss | MR-miss | MR-miss | MR-miss | MR-miss | MR-miss | MR-miss |

Non-reference hits on the candidate: 0/11 checks, comprising 0/9 MRs and
0/2 reference-oracle checks. Original P12 groups: B1 0/3 and selected B2 0/3.
The eight-member B2 pool was run in full here; its result is not the frozen
three-member B2 group result.
`mr_suite` returns exit 0 for both `PASS` and `VIOLATED`; the stdout line is
the verdict. T1 returns 0 on PASS and 1 on FAIL.

## T1 raw errors (this run)

Real defect, exit 1:

```
N= 4  1.306563e+00 FAIL
N= 5  1.414214e+00 FAIL
N= 8  1.387040e+00 FAIL
N= 9  1.414214e+00 FAIL
N=16  1.407404e+00 FAIL
N=17  1.414214e+00 FAIL
```

Fixed, exit 0: `0`, `2.220446e-16`, `4.440892e-16`, `4.440892e-16`,
`4.440892e-16`, `4.440892e-16`.

Candidate, exit 1: `1.414214e+00` at all six N.

## Commands

Compile pattern (exit 0 for every binary in this trial):

```
clang++ -std=c++17 -O2 -pthread -I<include/arm> <src> -o <build/binary>
```

Runs:

| Log stem | Command | Exit |
|---|---|---|
| 02_run_t1_buggy | `build/t1_buggy` | 1 |
| 04_run_t1_fixed | `build/t1_fixed` | 0 |
| 06_cert_fixed_establish | `build/cert_fixed establish` | 0 |
| 08_cert_candidate_expect | `build/cert_candidate expect-dst2-last-x2` | 0 |
| 14_run_t1_candidate | `build/t1_candidate` | 1 |
| 16_mr_* | `build/mr_<arm> <id>` | 0 |

Each stem has `.cmd`, `.stdout`, `.stderr`, and `.exit` under `logs/`.

## Candidate diff

`patches/candidate.diff` is a one-line change at fixed-header line 2637:
`c[N-1]*=sqrt2*T0(0.5)` becomes `c[N-1]*=sqrt2` in the DST-II (`type==2`)
ortho sine arm. The index is unchanged.

## Certifier

Formula, input, and tolerance: `src/CERTIFIER_FORMULA.md`.
Implementation: `src/independent_certifier.cpp`.
Input `x_n = n+1`, no PRNG, no seed. Absolute tolerance `1e-8`, fixed before
the fixed-arm run.
