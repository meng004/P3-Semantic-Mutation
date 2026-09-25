# Independent certifier (written before any candidate-mutant run)

This file is the pre-specified mathematical reference for the
B-POCKETFFT-001 developmental trial. It does not call PocketFFT and it
does not treat an MR verdict as evidence of a semantic deviation.

The candidate edit is also fixed here, before that edit is compiled.

## Program versions

- Fixed: mreineck/pocketfft `fb21e4016b96f50a83c516fc0acabe8def4b3bb5`
- Real defect: parent `076cb3d2536b7c5d0629093ad886e10ac05f3623`
- Candidate: the fixed header with exactly one substitution, below.
  This is not the real defect. The real defect applies the sine-branch
  ortho scale to `c[0]` rather than `c[N-1]`.

## Candidate edit (one site)

In `T_dcst23::exec`, the `type==2` arm, the `ortho` statement

```
cosine ? c[0]*=sqrt2*T0(0.5) : c[N-1]*=sqrt2*T0(0.5);
```

becomes

```
cosine ? c[0]*=sqrt2*T0(0.5) : c[N-1]*=sqrt2;
```

Index `c[N-1]` stays. No other line changes.

`sqrt2*T0(0.5)` equals `1/sqrt(2)`, which is the README rule for DST
type 2 ortho ("divide last output value by sqrt(2)"). Replacing it by
`sqrt2` multiplies that one output by exactly 2 relative to the
README rule. The predicted deviation is therefore confined to DST-II,
`ortho=true`, coefficient `N-1`.

## Direct formulas

`N` is the length. `fct` is the caller scale. Indices `n,k` run over
`0 .. N-1`. These are the FFTPACK / FFTW RODFT10 and RODFT01 sums
(the factor 2 is part of the un-normalized transform). PocketFFT's
README adds only the boundary ortho corrections below; it does not
divide by `sqrt(2N)`. `fct=1.0` leaves that un-normalized scale in
place.

DST-II, `ortho=false`:

```
Y_k = fct * 2 * sum_{n=0}^{N-1} x_n * sin(pi * (n+1/2) * (k+1) / N)
```

DST-II, `ortho=true`: the same `Y`, then `Y_{N-1} = Y_{N-1} / sqrt(2)`.

DST-III, `ortho=false`:

```
Y_k = fct * [ (-1)^k * x_{N-1}
      + 2 * sum_{n=0}^{N-2} x_n * sin(pi * (n+1) * (k+1/2) / N) ]
```

DST-III, `ortho=true`: replace `x_{N-1}` by `sqrt(2) * x_{N-1}` and
then use the `ortho=false` sum. This is the README rule "multiply last
input value by sqrt(2)", applied before the transform.

`sqrt(2)` is `std::sqrt(2.0)`. `pi` is `acos(-1)`.

## Input

No PRNG and no seed.

```
x_n = n + 1,    n = 0 .. N-1
```

The same vector is used for every arm. Lengths: `N = {4,5,8,9,16,17}`.

## Tolerance

Absolute tolerance `1e-8` on the maximum absolute coefficient error.
This is fixed before the fixed-arm check and is not revised after any
arm is run.

## Fixed-arm establishment

The certifier is established only if, on the fixed header, every `N`
satisfies all of:

1. DST-II, `ortho=false`, `fct=1.0`: max abs error `< 1e-8`
2. DST-III, `ortho=false`, `fct=1.0`: max abs error `< 1e-8`
3. DST-II, `ortho=true`, `fct=1.0`: max abs error `< 1e-8`
4. DST-III, `ortho=true`, `fct=1.0`: max abs error `< 1e-8`
5. DST-II, `ortho=true`, `fct=2.0`: max abs error `< 1e-8`
   (checks that `fct` scales the whole vector, including the ortho
   boundary term)

If any row fails, mutant detection is not interpreted.

## Candidate deviation, pre-specified

On the candidate header, DST-II `ortho=true` `fct=1.0` must satisfy,
for every `N`:

- `k < N-1`: `|y_k - Y_k| < 1e-8`
- `|y_{N-1} - 2 Y_{N-1}| < 1e-8`
- `|y_{N-1} - Y_{N-1}| > 1e-3`

and DST-III `ortho=true` `fct=1.0` must still match `Y` within `1e-8`
on every coefficient. Any miss is a failed candidate. The input, the
index, and the tolerance are not changed to recover a pass.
