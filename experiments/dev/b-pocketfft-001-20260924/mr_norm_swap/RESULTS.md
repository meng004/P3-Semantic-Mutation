# Norm-swap MR run (developmental, after the known defect)

Not a preregistered P3 result. Designed after the PocketFFT defect and
the candidate were already observed. A hit here is not confirmatory and
does not show an advantage over syntactic mutation.

Fixed arm passed first (`OVERALL: PASS`, exit 0), so the other two arms
are interpretable. Input, tolerance, and swap were not changed.

| Arm | Exit | N=4 | N=5 | N=8 | N=9 | N=16 | N=17 | Overall |
|---|---|---|---|---|---|---|---|---|
| fixed | 0 | PASS | PASS | PASS | PASS | PASS | PASS | relation holds |
| candidate | 1 | VIOLATED | VIOLATED | VIOLATED | VIOLATED | VIOLATED | VIOLATED | relation fails |
| real defect | 1 | VIOLATED | VIOLATED | VIOLATED | VIOLATED | VIOLATED | VIOLATED | observed fail |

Candidate absolute gaps: 24, 96, 72, 144, 168, 240. They match the
pre-run prediction in `DESIGN.md`. Real-defect gaps were only recorded:
5.556, 50.92, 9.000, 85.37, 10.62, 150.7.

Compile line, exit 0 for each arm:

```
clang++ -std=c++17 -O2 -pthread -I../include/<arm> norm_swap_mr.cpp -o build/norm_swap_<arm>
```

Logs: `logs/01_build_fixed.*`, `logs/02_run_fixed.*`,
`logs/03_build_candidate.*`, `logs/04_run_candidate.*`,
`logs/05_build_buggy.*`, `logs/06_run_buggy.*`.
Previous trial logs were not modified.
