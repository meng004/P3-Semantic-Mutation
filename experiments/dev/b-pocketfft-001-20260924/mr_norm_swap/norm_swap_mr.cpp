// DST-II ortho norm-swap MR. Two program executions only.
// Protocol is frozen in DESIGN.md. Not T1 and not A1.
#include "pocketfft_hdronly.h"

#include <cmath>
#include <cstdio>
#include <vector>

namespace {

const int NS[] = {4, 5, 8, 9, 16, 17};
const double REL = 1e-9;

std::vector<double> make_x(size_t N) {
  std::vector<double> x(N);
  for (size_t n = 0; n < N; ++n) x[n] = static_cast<double>(n + 1);
  return x;
}

std::vector<double> swap01(const std::vector<double>& x) {
  std::vector<double> y = x;
  if (y.size() >= 2) std::swap(y[0], y[1]);
  return y;
}

std::vector<double> dst2_ortho(const std::vector<double>& in) {
  const size_t N = in.size();
  std::vector<double> out(N, 0.0);
  pocketfft::shape_t shape{N};
  pocketfft::stride_t stride{sizeof(double)};
  pocketfft::shape_t axes{0};
  pocketfft::dst<double>(shape, stride, stride, axes, 2, in.data(), out.data(),
                         1.0, true, 1);
  return out;
}

double sqnorm(const std::vector<double>& v) {
  double s = 0.0;
  for (double a : v) s += a * a;
  return s;
}

}  // namespace

int main() {
  int viol = 0;
  std::printf("mr: DST-II ortho fct=1 norm after swap x0 with x1\n");
  std::printf("rule: abs(n2x-n2px) <= 1e-9 * max(1, n2x, n2px)\n");
  for (int nraw : NS) {
    const size_t N = static_cast<size_t>(nraw);
    const auto x = make_x(N);
    const auto px = swap01(x);
    const double n2x = sqnorm(dst2_ortho(x));
    const double n2px = sqnorm(dst2_ortho(px));
    const double gap = std::fabs(n2x - n2px);
    const double thr = REL * std::max(1.0, std::max(n2x, n2px));
    const bool pass = gap <= thr;
    if (!pass) viol = 1;
    std::printf(
        "N=%2zu n2x=%.16e n2px=%.16e abs=%.16e thr=%.16e %s\n", N, n2x, n2px,
        gap, thr, pass ? "PASS" : "VIOLATED");
  }
  std::printf("OVERALL: %s\n", viol ? "VIOLATED" : "PASS");
  return viol ? 1 : 0;
}
