// Independent DST-II / DST-III reference. The sums below do not call
// PocketFFT. PocketFFT is used only as the implementation under test.
#include "pocketfft_hdronly.h"

#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>

namespace {

const double PI = std::acos(-1.0);
const double SQRT2 = std::sqrt(2.0);
const double TOL = 1e-8;
const double MIN_LAST_DEV = 1e-3;
const int NS[] = {4, 5, 8, 9, 16, 17};

std::vector<double> make_x(size_t N) {
  std::vector<double> x(N);
  for (size_t n = 0; n < N; ++n) x[n] = static_cast<double>(n + 1);
  return x;
}

std::vector<double> ref_dst2(const std::vector<double>& x, bool ortho, double fct) {
  const size_t N = x.size();
  std::vector<double> y(N, 0.0);
  for (size_t k = 0; k < N; ++k) {
    double s = 0.0;
    for (size_t n = 0; n < N; ++n)
      s += x[n] * std::sin(PI * (static_cast<double>(n) + 0.5) *
                           static_cast<double>(k + 1) / static_cast<double>(N));
    y[k] = fct * 2.0 * s;
  }
  if (ortho) y[N - 1] /= SQRT2;
  return y;
}

std::vector<double> ref_dst3(const std::vector<double>& x, bool ortho, double fct) {
  const size_t N = x.size();
  std::vector<double> xin = x;
  if (ortho) xin[N - 1] *= SQRT2;
  std::vector<double> y(N, 0.0);
  for (size_t k = 0; k < N; ++k) {
    const double sign = (k % 2 == 0) ? 1.0 : -1.0;
    double s = sign * xin[N - 1];
    for (size_t n = 0; n + 1 < N; ++n)
      s += 2.0 * xin[n] *
           std::sin(PI * static_cast<double>(n + 1) *
                    (static_cast<double>(k) + 0.5) / static_cast<double>(N));
    y[k] = fct * s;
  }
  return y;
}

std::vector<double> pocket_dst(const std::vector<double>& in, int type, bool ortho,
                               double fct) {
  const size_t N = in.size();
  std::vector<double> out(N, 0.0);
  pocketfft::shape_t shape{N};
  pocketfft::stride_t stride{sizeof(double)};
  pocketfft::shape_t axes{0};
  pocketfft::dst<double>(shape, stride, stride, axes, type, in.data(), out.data(),
                         fct, ortho, 1);
  return out;
}

double max_abs(const std::vector<double>& a, const std::vector<double>& b) {
  double m = 0.0;
  for (size_t i = 0; i < a.size(); ++i)
    m = std::max(m, std::fabs(a[i] - b[i]));
  return m;
}

double max_abs_prefix(const std::vector<double>& a, const std::vector<double>& b) {
  double m = 0.0;
  if (a.size() <= 1) return 0.0;
  for (size_t i = 0; i + 1 < a.size(); ++i)
    m = std::max(m, std::fabs(a[i] - b[i]));
  return m;
}

void print_check(const char* name, size_t N, double err, bool ok) {
  std::printf("N=%2zu %-28s max_abs=%.6e  %s\n", N, name, err, ok ? "PASS" : "FAIL");
}

int run_establish() {
  int bad = 0;
  for (int nraw : NS) {
    const size_t N = static_cast<size_t>(nraw);
    const auto x = make_x(N);
    const auto y2 = pocket_dst(x, 2, false, 1.0);
    const auto y3 = pocket_dst(x, 3, false, 1.0);
    const auto y2o = pocket_dst(x, 2, true, 1.0);
    const auto y3o = pocket_dst(x, 3, true, 1.0);
    const auto y2of = pocket_dst(x, 2, true, 2.0);
    const double e2 = max_abs(y2, ref_dst2(x, false, 1.0));
    const double e3 = max_abs(y3, ref_dst3(x, false, 1.0));
    const double e2o = max_abs(y2o, ref_dst2(x, true, 1.0));
    const double e3o = max_abs(y3o, ref_dst3(x, true, 1.0));
    const double e2of = max_abs(y2of, ref_dst2(x, true, 2.0));
    const bool ok = e2 < TOL && e3 < TOL && e2o < TOL && e3o < TOL && e2of < TOL;
    print_check("dst2 ortho=0 fct=1", N, e2, e2 < TOL);
    print_check("dst3 ortho=0 fct=1", N, e3, e3 < TOL);
    print_check("dst2 ortho=1 fct=1", N, e2o, e2o < TOL);
    print_check("dst3 ortho=1 fct=1", N, e3o, e3o < TOL);
    print_check("dst2 ortho=1 fct=2", N, e2of, e2of < TOL);
    const auto ref = ref_dst2(x, true, 1.0);
    std::printf("N=%2zu dst2-ortho last_ref=%.6e last_impl=%.6e\n", N, ref[N - 1],
                y2o[N - 1]);
    if (!ok) bad = 1;
  }
  std::printf("ESTABLISH: %s\n", bad ? "FAIL" : "PASS");
  return bad;
}

int run_expect_last_x2() {
  int bad = 0;
  for (int nraw : NS) {
    const size_t N = static_cast<size_t>(nraw);
    const auto x = make_x(N);
    const auto y2o = pocket_dst(x, 2, true, 1.0);
    const auto y3o = pocket_dst(x, 3, true, 1.0);
    const auto ref2 = ref_dst2(x, true, 1.0);
    const auto ref3 = ref_dst3(x, true, 1.0);
    std::vector<double> doubled = ref2;
    doubled[N - 1] *= 2.0;
    const double prefix = max_abs_prefix(y2o, ref2);
    const double last = std::fabs(y2o[N - 1] - doubled[N - 1]);
    const double gap = std::fabs(y2o[N - 1] - ref2[N - 1]);
    const double e3 = max_abs(y3o, ref3);
    const bool ok = prefix < TOL && last < TOL && gap > MIN_LAST_DEV && e3 < TOL;
    std::printf(
        "N=%2zu prefix_max=%.6e last_vs_2ref=%.6e last_gap=%.6e dst3_max=%.6e "
        "last_ref=%.6e last_impl=%.6e  %s\n",
        N, prefix, last, gap, e3, ref2[N - 1], y2o[N - 1], ok ? "PASS" : "FAIL");
    if (!ok) bad = 1;
  }
  std::printf("EXPECT_DST2_LAST_X2: %s\n", bad ? "FAIL" : "PASS");
  return bad;
}

}  // namespace

int main(int argc, char** argv) {
  if (argc != 2) {
    std::fprintf(stderr, "usage: %s establish|expect-dst2-last-x2\n", argv[0]);
    return 2;
  }
  const std::string mode(argv[1]);
  std::printf("input: x_n=n+1 for n=0..N-1; no PRNG; no seed\n");
  std::printf("tol_abs=%.1e min_last_dev=%.1e\n", TOL, MIN_LAST_DEV);
  if (mode == "establish") return run_establish();
  if (mode == "expect-dst2-last-x2") return run_expect_last_x2();
  std::fprintf(stderr, "unknown mode %s\n", argv[1]);
  return 2;
}
