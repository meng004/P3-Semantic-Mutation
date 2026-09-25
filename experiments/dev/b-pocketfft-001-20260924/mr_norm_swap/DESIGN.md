# Norm-swap MR for DST-II ortho (written before any run of this driver)

Developmental MR, designed after the PocketFFT defect and the candidate
mutant were already known. Not a preregistered confirmatory relation.
Not T1, not A1, and not a claim that P12 reference-MR exclusion review
has been passed.

Scope: PocketFFT DST-II, `ortho=true`, `fct=1.0` only.
The check compares two executions of the program. It does not compare
one output with the direct-sum formula.

## Frozen protocol

- `N = {4, 5, 8, 9, 16, 17}`
- `x_n = n + 1` for `n = 0 .. N-1`
- `P` swaps only `x_0` and `x_1`
- Let `D` be the program's DST-II at `ortho=true`, `fct=1.0`
- Verdict for each `N`:

```
| ||D(x)||^2 - ||D(Px)||^2 |
  <= 1e-9 * max(1, ||D(x)||^2, ||D(Px)||^2)
```

`PASS` if the inequality holds, otherwise `VIOLATED`.
The same rule is used for the fixed header, the existing candidate,
and the real-defect header. Input, tolerance, and `P` are not revised
after any arm runs.

If any `N` fails on the fixed header, detection on the other two arms
is not interpreted.

## Derivation from the direct sum

Un-normalized DST-II, then the README boundary scale (`fct = 1`):

```
Y_k = 2 * sum_{n=0}^{N-1} x_n * sin(pi * (n+1/2) * (k+1) / N)
      for k = 0 .. N-2
Y_{N-1} = Y_{N-1} / sqrt(2)
```

The fully orthonormal DST-II, `U`, uses the factor `sqrt(2/N)` on
rows `k < N-1` and `sqrt(1/N)` on the last row. Multiplying `U` by
`sqrt(2N)` reproduces the formulas above, including the last row:

```
sqrt(2N) * sqrt(1/N) * sum_n x_n * (-1)^n = sqrt(2) * sum_n (-1)^n x_n
```

and `sin(pi * (n+1/2) * N / N) = (-1)^n`, so the boundary division by
`sqrt(2)` is exactly that last row. Because `U` is orthogonal,
`U^T U = I`, hence

```
D^T D = 2 N I.
```

For this `P`, `P^T P = I`, so `||Px|| = ||x||` and

```
||D(x)||^2 = 2 N ||x||^2 = ||D(Px)||^2.
```

That is the MR. A uniform change of one output coefficient's scale
breaks `D^T D = 2 N I` while leaving many algebraic relations intact.

## Pre-run prediction for the candidate only

The candidate replaces `sqrt2*0.5` (`1/sqrt(2)`) by `sqrt2` on
`c[N-1]` in the DST-II sine arm. Relative to `D`, that one coefficient
is multiplied by 2. Other coefficients stay equal to `D`. Therefore

```
||D_c(z)||^2 = ||D(z)||^2 + 3 * D(z)_{N-1}^2
||D_c(x)||^2 - ||D_c(Px)||^2 = 3 (D(x)_{N-1}^2 - D(Px)_{N-1}^2)
```

With `D(z)_{N-1} = sqrt(2) * sum_n (-1)^n z_n` and `x_n = n+1`,

```
S(x) = sum_n (-1)^n (n+1)
S(Px) = S(x) + 2
|diff| = 24 * |S(x) + 1|
```

| N | S(x) | predicted absolute gap |
|---|---|---|
| 4 | -2 | 24 |
| 5 | 3 | 96 |
| 8 | -4 | 72 |
| 9 | 5 | 144 |
| 16 | -8 | 168 |
| 17 | 9 | 240 |

These numbers are a pre-run check. The recorded verdict uses the
program output, not this table. The real-defect arm has no predicted
verdict.

## Not the same relation as T1

T1 says the DST-III ortho matrix equals the transpose of the DST-II
ortho matrix (`D3 = D2^T`). The norm-swap MR says `D2^T D2 = 2 N I`
on one program, observed only through `||D2 x||` and `||D2 Px||`.
Either statement can fail while the other holds.

Counterexample A, norm-swap holds and T1 fails. Keep DST-III equal to
the correct `D3`, and replace DST-II by `2 D2`. Then
`(2 D2)^T (2 D2) = 4 * 2 N I`, so both squared norms scale by the same
factor and the swap equality still holds. T1 compares `D3` with
`(2 D2)^T = 2 D2^T`, which is not `D3`.

Counterexample B, T1 holds and norm-swap fails. For `N = 2` set

```
D2 = [[1, 0], [0, 2]],  D3 = D2^T = D2.
```

T1 holds by construction. Take `x = (1, 2)` and `Px = (2, 1)`:

```
||D2 x||^2 = 1^2 + 4^2 = 17
||D2 Px||^2 = 2^2 + 2^2 = 8
```

The swap equality fails. These two matrices are logical counterexamples
for the development argument. They are not a P12 exclusion receipt.

## Difference from B2-7

B2-7 reverses the whole input and checks every output coefficient
against `(-1)^k` times the original coefficient. The same wrong scale
on coefficient `N-1` is applied to both the input and its reverse, so
that coefficient-wise relation can survive. This MR swaps only the
first two samples and compares the squared Euclidean norms of the two
outputs. It does not require a sign pattern on each coefficient.
