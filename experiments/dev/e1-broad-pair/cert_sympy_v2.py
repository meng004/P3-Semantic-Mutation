"""Independent SymPy development certifier, with complex endpoint evaluation."""
from __future__ import annotations

import sys
import traceback

import mpmath
import sympy


TOL = mpmath.mpf("1e-8")


def main() -> int:
    print("commit_expected", sys.argv[1] if len(sys.argv) > 1 else "UNKNOWN")
    print("python", sys.version.replace("\n", " "))
    print("sympy_file", sympy.__file__)
    print("sympy_version", sympy.__version__)
    print("mpmath_file", mpmath.__file__)
    print("mpmath_version", mpmath.__version__)

    mpmath.mp.dps = 80
    quad = mpmath.quad(lambda t: 1 / (1 + t**2), [0, 1])
    pi_over_4 = mpmath.pi / 4
    self_check = abs(quad - pi_over_4)
    print("quad_0_1", quad)
    print("pi_over_4", pi_over_4)
    print("self_check_abs", self_check)
    if self_check >= TOL:
        print("verdict", "CERT_INCONCLUSIVE")
        print("reason", "quadrature self-check failed")
        return 2

    a, b, c, t = sympy.symbols("a b c t", real=True)
    integrand = 1 / (a * t**2 + b * t + c)
    try:
        F = sympy.integrate(integrand, t)
        print("F_before_subs", F)
        F_sub = F.subs({a: 1, b: 0, c: 1})
        print("F_after_subs", F_sub)
        endpoint = F_sub.subs(t, 1) - F_sub.subs(t, 0)
        numeric = endpoint.evalf(80)
        observed_real = mpmath.mpf(str(sympy.re(numeric)))
        observed_imag = mpmath.mpf(str(sympy.im(numeric)))
        observed = mpmath.mpc(observed_real, observed_imag)
    except Exception:
        traceback.print_exc()
        print("verdict", "EXEC_FAIL")
        return 2

    diff_abs = abs(observed - quad)
    print("F1_minus_F0_real", observed_real)
    print("F1_minus_F0_imag", observed_imag)
    print("abs_diff_complex", diff_abs)
    print("tolerance", TOL)
    if diff_abs < TOL:
        print("verdict", "CERT_HOLD")
        return 0
    print("verdict", "CERT_BREAK")
    return 1


if __name__ == "__main__":
    sys.exit(main())
