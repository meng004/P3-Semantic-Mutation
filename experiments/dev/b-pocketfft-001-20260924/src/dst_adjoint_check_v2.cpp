#include "pocketfft_hdronly.h"
#include <cstdio>
#include <cmath>
#include <vector>

using namespace pocketfft;

// MR oracle (corrected/narrowed): DST-II and DST-III with ortho=true must be
// exact transposes of each other, for any N. This is the precise property
// the fix commit (fb21e40) addresses -- it does not depend on any
// caller-supplied normalization constant.
std::vector<double> build_dst_matrix(size_t N, int type) {
  std::vector<double> M(N * N, 0.0);
  shape_t shape{N};
  stride_t stride{sizeof(double)};
  shape_t axes{0};
  for (size_t i = 0; i < N; i++) {
    std::vector<double> in(N, 0.0), out(N, 0.0);
    in[i] = 1.0;
    dst<double>(shape, stride, stride, axes, type, in.data(), out.data(),
                1.0, /*ortho=*/true, 1);
    for (size_t j = 0; j < N; j++)
      M[j * N + i] = out[j];
  }
  return M;
}

double max_abs_diff(const std::vector<double>& A, const std::vector<double>& B, size_t N) {
  double m = 0.0;
  for (size_t i = 0; i < N * N; i++) m = std::max(m, std::fabs(A[i] - B[i]));
  return m;
}

std::vector<double> transpose(const std::vector<double>& A, size_t N) {
  std::vector<double> T(N * N);
  for (size_t i = 0; i < N; i++)
    for (size_t j = 0; j < N; j++)
      T[i * N + j] = A[j * N + i];
  return T;
}

int main() {
  const double tol = 1e-9;
  bool all_pass = true;
  for (size_t N : {4, 5, 8, 9, 16, 17}) {
    auto D2 = build_dst_matrix(N, 2);
    auto D3 = build_dst_matrix(N, 3);
    auto D2T = transpose(D2, N);
    double diff = max_abs_diff(D3, D2T, N);
    bool pass = diff < tol;
    all_pass = all_pass && pass;
    printf("N=%2zu max|D3 - D2^T| = %.6e  %s\n", N, diff, pass ? "PASS" : "FAIL");
  }
  printf("OVERALL: %s\n", all_pass ? "PASS" : "FAIL");
  return all_pass ? 0 : 1;
}
