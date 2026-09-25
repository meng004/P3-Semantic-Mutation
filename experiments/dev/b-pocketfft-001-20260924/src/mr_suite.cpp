/* B-POCKETFFT-001 mutation suite (B1 + B2 + A1; T1 = original
 * dst_adjoint_check_v2.cpp verification driver, run separately).
 *
 * Case: PocketFFT DST-II and DST-III in ortho mode failed to be exact
 * transposes of each other, because the sqrt(2) orthonormalization scale was
 * applied to c[0] for BOTH the cosine (DCT) and sine (DST) branches of
 * T_dcst23::exec; the fix (commit fb21e40, "fix orthonormalization of DST
 * II/III?") applies the scale to c[N-1] for the sine case instead.
 * Buggy arm = 076cb3d (parent); fixed arm = fb21e40. Mutation surface =
 * the fix-touched function T_dcst23::exec in pocketfft_hdronly.h.
 *
 * T1 oracle (verification driver): for N in {4,5,8,9,16,17}, build DST-II
 * matrix D2 and DST-III matrix D3 (ortho=true) by applying each transform to
 * every standard basis vector; require D3 == D2^T elementwise (tol 1e-9).
 * This is the adjoint/dual-transpose-pair family (mr_mapping m_adj/f_adj.dual).
 *
 *   B1-1 repetition determinism        dst2 ortho, twice -> identical
 *   B1-2 linearity / superposition     dst2 ortho: T(a x + b y)=a T(x)+b T(y)
 *   B1-3 reflection equivariance        dct2 ortho: reverse input -> (-1)^k out
 *   B2-*  seeded draws (seed 20260974) from the pool registered below;
 *         shuffle order: B2-1,B2-5,B2-8,B2-3,B2-6,B2-4,B2-7,B2-2;
 *         first three baseline-passers are the group {B2-1,B2-5,B2-8}
 *         (no discards -- all pool signs pass the fixed baseline).
 *   A1-a  降维 ablation of T1: transpose-duality at a SINGLE size N=5 only
 *         (instead of the 6-size sweep).
 *   A1-b  去严格化 ablation of T1: full 6-size sweep but tolerance relaxed
 *         from 1e-9 to 0.5 (order-1 real defect still caught; subtle
 *         perturbations tolerated).
 *
 * Anti-leak note (B1): T1's relation family is the adjoint/transpose duality
 * between the DST-II and DST-III operators (D3 == D2^T). B1-1 (repetition
 * determinism), B1-2 (linearity/superposition of a single operator) and B1-3
 * (input-reversal / reflection equivariance of a single operator) are the
 * repetition, linearity, and permutation/reflection literature families
 * respectively -- none of them pairs DST-II against DST-III, none is an
 * adjoint/transpose/inverse-pair relation. All three exercise the mutated
 * T_dcst23::exec (via the ortho DST/DCT type-2 path) but are structurally
 * blind to a pure boundary-coefficient scaling error, which preserves
 * determinism, linearity, and reflection symmetry.
 *
 * B2 pool (transform x observable x relation), registered:
 *   B2-1 DST-II scaling equivariance     dst2 ortho: T(5x)=5 T(x)
 *   B2-2 DST-II fct-parameter linearity  dst2(fct=2c)=2 dst2(fct=c)
 *   B2-3 DCT-II definition reference      dct2 (ortho=F) == 2*sum cos()
 *   B2-4 DST-II definition reference      dst2 (ortho=F) == 2*sum sin()
 *   B2-5 c2c FFT round-trip              bwd(fwd(x)) == N*x  (往返)
 *   B2-6 DCT-II repetition determinism   dct2 ortho, twice -> identical
 *   B2-7 DST-II reflection ORTHO          dst2 ortho: reverse -> (-1)^k out
 *   B2-8 DCT-II reflection ORTHO          dct2 ortho: reverse -> (-1)^k out
 */
#include "pocketfft_hdronly.h"
#include <cstdio>
#include <cstring>
#include <cmath>
#include <vector>
#include <complex>
using namespace pocketfft;

static const int NSET[] = {5, 8, 12, 16};

static shape_t SHP(size_t N){ return shape_t{N}; }
static stride_t STR(){ return stride_t{sizeof(double)}; }
static stride_t STRC(){ return stride_t{sizeof(std::complex<double>)}; }

static std::vector<double> mkx(size_t N, double phase){
  std::vector<double> x(N);
  for (size_t i=0;i<N;i++) x[i]=std::sin(0.7*i+phase)+0.5*i-0.3;
  return x;
}

static std::vector<double> xform(const std::vector<double>&in,int type,bool cosine,double fct,bool ortho){
  size_t N=in.size(); std::vector<double> out(N,0.0);
  shape_t s=SHP(N); stride_t st=STR(); shape_t ax{0};
  if (cosine) dct<double>(s,st,st,ax,type,in.data(),out.data(),fct,ortho,1);
  else        dst<double>(s,st,st,ax,type,in.data(),out.data(),fct,ortho,1);
  return out;
}

// build NxN DST/DCT matrix (col i = transform of e_i)
static std::vector<double> build_mat(size_t N,int type,bool cosine){
  std::vector<double> M(N*N,0.0);
  for (size_t i=0;i<N;i++){
    std::vector<double> e(N,0.0); e[i]=1.0;
    auto o=xform(e,type,cosine,1.0,true);
    for (size_t j=0;j<N;j++) M[j*N+i]=o[j];
  }
  return M;
}
static double dualdiff(size_t N){ // max|D3 - D2^T|
  auto D2=build_mat(N,2,false), D3=build_mat(N,3,false);
  double m=0;
  for (size_t i=0;i<N;i++) for (size_t j=0;j<N;j++)
    m=std::max(m,std::fabs(D3[j*N+i]-D2[i*N+j]));
  return m;
}

static void verdict(const char* id,int violated){ printf("### %s: %s\n",id,violated?"VIOLATED":"PASS"); }

int main(int argc,char**argv){
  if (argc<2){ fprintf(stderr,"need mr id\n"); return 2; }
  const char* id=argv[1];
  int viol=0;

  if (!strcmp(id,"B1-1")){                       /* determinism dst2 ortho */
    for (int N:NSET){ auto x=mkx(N,0.3);
      auto a=xform(x,2,false,1.0,true), b=xform(x,2,false,1.0,true);
      for (int i=0;i<N;i++) if (a[i]!=b[i]) viol=1; }
    verdict(id,viol);
  } else if (!strcmp(id,"B1-2")){                /* linearity dst2 ortho */
    for (int N:NSET){ auto x=mkx(N,0.3),y=mkx(N,1.1);
      std::vector<double> z(N); for (int i=0;i<N;i++) z[i]=2*x[i]+3*y[i];
      auto tz=xform(z,2,false,1.0,true),tx=xform(x,2,false,1.0,true),ty=xform(y,2,false,1.0,true);
      for (int i=0;i<N;i++){ double r=2*tx[i]+3*ty[i];
        if (std::fabs(tz[i]-r)>1e-9*(1+std::fabs(r))) viol=1; } }
    verdict(id,viol);
  } else if (!strcmp(id,"B1-3")){                /* reflection dct2 ortho -> (-1)^k */
    for (int N:NSET){ auto x=mkx(N,0.3); std::vector<double> y(N);
      for (int i=0;i<N;i++) y[i]=x[N-1-i];
      auto ax=xform(x,2,true,1.0,true),ay=xform(y,2,true,1.0,true);
      for (int k=0;k<N;k++){ double r=(k%2?-1.0:1.0)*ax[k];
        if (std::fabs(ay[k]-r)>1e-9*(1+std::fabs(r))) viol=1; } }
    verdict(id,viol);
  } else if (!strcmp(id,"B2-1")){                /* DST-II scaling equivariance */
    for (int N:NSET){ auto x=mkx(N,0.3); std::vector<double> z(N);
      for (int i=0;i<N;i++) z[i]=5*x[i];
      auto tz=xform(z,2,false,1.0,true),tx=xform(x,2,false,1.0,true);
      for (int i=0;i<N;i++){ double r=5*tx[i];
        if (std::fabs(tz[i]-r)>1e-9*(1+std::fabs(r))) viol=1; } }
    verdict(id,viol);
  } else if (!strcmp(id,"B2-2")){                /* DST-II fct linearity */
    for (int N:NSET){ auto x=mkx(N,0.3);
      auto a=xform(x,2,false,2.0,true),b=xform(x,2,false,1.0,true);
      for (int i=0;i<N;i++){ double r=2*b[i];
        if (std::fabs(a[i]-r)>1e-9*(1+std::fabs(r))) viol=1; } }
    verdict(id,viol);
  } else if (!strcmp(id,"B2-3")){                /* DCT-II definition reference */
    for (int N:NSET){ auto x=mkx(N,0.3); auto a=xform(x,2,true,1.0,false);
      for (int k=0;k<N;k++){ double s=0; for (int n=0;n<N;n++) s+=x[n]*std::cos(M_PI/N*(n+0.5)*k);
        if (std::fabs(a[k]-2*s)>1e-7*(1+std::fabs(2*s))) viol=1; } }
    verdict(id,viol);
  } else if (!strcmp(id,"B2-4")){                /* DST-II definition reference */
    for (int N:NSET){ auto x=mkx(N,0.3); auto a=xform(x,2,false,1.0,false);
      for (int k=0;k<N;k++){ double s=0; for (int n=0;n<N;n++) s+=x[n]*std::sin(M_PI/N*(n+0.5)*(k+1));
        if (std::fabs(a[k]-2*s)>1e-7*(1+std::fabs(2*s))) viol=1; } }
    verdict(id,viol);
  } else if (!strcmp(id,"B2-5")){                /* c2c round-trip bwd(fwd(x))=N x */
    for (int N:NSET){ auto xr=mkx(N,0.3),xi=mkx(N,1.1);
      std::vector<std::complex<double>> in(N),f(N),b(N);
      for (int i=0;i<N;i++) in[i]={xr[i],xi[i]};
      shape_t s=SHP(N); stride_t st=STRC(); shape_t ax{0};
      c2c<double>(s,st,st,ax,true,in.data(),f.data(),1.0,1);
      c2c<double>(s,st,st,ax,false,f.data(),b.data(),1.0,1);
      for (int i=0;i<N;i++) if (std::abs(b[i]-double(N)*in[i])>1e-9*(1+std::abs(double(N)*in[i]))) viol=1; }
    verdict(id,viol);
  } else if (!strcmp(id,"B2-6")){                /* DCT-II determinism ortho */
    for (int N:NSET){ auto x=mkx(N,0.3);
      auto a=xform(x,2,true,1.0,true),b=xform(x,2,true,1.0,true);
      for (int i=0;i<N;i++) if (a[i]!=b[i]) viol=1; }
    verdict(id,viol);
  } else if (!strcmp(id,"B2-7")){                /* DST-II reflection ortho -> (-1)^k */
    for (int N:NSET){ auto x=mkx(N,0.3); std::vector<double> y(N);
      for (int i=0;i<N;i++) y[i]=x[N-1-i];
      auto ax=xform(x,2,false,1.0,true),ay=xform(y,2,false,1.0,true);
      for (int k=0;k<N;k++){ double r=(k%2?-1.0:1.0)*ax[k];
        if (std::fabs(ay[k]-r)>1e-9*(1+std::fabs(r))) viol=1; } }
    verdict(id,viol);
  } else if (!strcmp(id,"B2-8")){                /* DCT-II reflection ortho -> (-1)^k */
    for (int N:NSET){ auto x=mkx(N,0.3); std::vector<double> y(N);
      for (int i=0;i<N;i++) y[i]=x[N-1-i];
      auto ax=xform(x,2,true,1.0,true),ay=xform(y,2,true,1.0,true);
      for (int k=0;k<N;k++){ double r=(k%2?-1.0:1.0)*ax[k];
        if (std::fabs(ay[k]-r)>1e-9*(1+std::fabs(r))) viol=1; } }
    verdict(id,viol);
  } else if (!strcmp(id,"A1-a")){                /* 降维: transpose-duality single N=5 */
    if (dualdiff(5) >= 1e-9) viol=1;
    verdict(id,viol);
  } else if (!strcmp(id,"A1-b")){                /* 去严格化: full sweep, tol relaxed to 0.5 */
    for (int N:{4,5,8,9,16,17}) if (dualdiff((size_t)N) >= 0.5) viol=1;
    verdict(id,viol);
  } else { fprintf(stderr,"unknown mr id %s\n",id); return 2; }
  return 0;
}
