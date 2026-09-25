# Batch-? case B-POCKETFFT-001 (2026-07-04): DST-II/III ortho transpose-duality break

## Provenance note: header-only PocketFFT re-instantiated from mreineck/pocketfft
## git (assets lost with old container). Buggy arm = 076cb3d (parent of the
## fix, "Merge pull request #7"); fixed arm = fb21e40 ("fix orthonormalization
## of DST II/III?"). Two git worktrees under work/pocketfft-repro/{buggy,fixed}.
## Header-only C++17 -> per-mutant rebuild = driver recompile only (g++ -I<arm>).
## Mutation target: the fix-touched function T_dcst23::exec in
## pocketfft_hdronly.h (fixed-arm lines 2609-2661; the ortho sqrt(2) scale the
## fix moves from c[0] to c[N-1] for the sine branch is lines 2636-2637 & 2641-2642).

## Arms-reproduction gate (vs report) -- EXACT match
Recompiled the report's T1 driver (dst_adjoint_check_v2.cpp) against both
worktrees. max|D3 - D2^T| over N={4,5,8,9,16,17}:
  Buggy 076cb3d: 1.306563, 1.414214, 1.387040, 1.414214, 1.407404, 1.414214  -> OVERALL FAIL
  Fixed fb21e40: 0, 3.33e-16, 4.44e-16, 4.44e-16, 4.44e-16, 6.66e-16        -> OVERALL PASS
These reproduce the verification report's numbers to the printed digits (order-1
FAIL on buggy, machine-epsilon PASS on fixed). No deviation on the gate.

## Real-defect face (buggy arm 076cb3d; logs/mutation-b-pocketfft-001-realdefect-buggy076cb3d.log)
T1 DETECTS (OVERALL FAIL). B1 0/3 -- ALL structurally blind: the defect is a
pure boundary-coefficient scaling error that preserves determinism (B1-1),
linearity/superposition (B1-2) and reflection/(-1)^k equivariance (B1-3); each
relation holds identically on the buggy arm. B2 0/3 -- B2-1 (DST-II scaling
equivariance) and B2-8 (DCT-II reflection ortho) blind for the same reason;
B2-5 (c2c FFT round-trip) structurally cannot see it (c2c does not route through
the mutated T_dcst23). A1-a VIOLATED (transpose-duality at single N=5 still
fails -- the defect breaks the duality at every size). A1-b VIOLATED (relaxed
tol 0.5 < the order-1 real error 1.31). This mirrors C-GSL-001: the defect face
is a scalar range/scaling error to which the generic algebraic MR families
(repetition/linearity/permutation) are all blind; only the adjoint/transpose
oracle the fix is actually about, and its ablations, catch it.

## B2 draw log (seed 20260974)
Pool (8, registered in mr_suite.cpp header: transform x observable x relation).
Shuffle order (random.Random(20260974).shuffle): B2-1, B2-5, B2-8, B2-3, B2-6,
B2-4, B2-7, B2-2. First three baseline-passers taken -> ALL pass the fixed
baseline, no discards. Group = {B2-1 (DST-II scaling equivariance),
B2-5 (c2c round-trip), B2-8 (DCT-II reflection ortho)}.

## Anti-leak (B1): T1's family is the adjoint/dual-transpose pairing of the two
distinct operators DST-II vs DST-III (D3 == D2^T). B1-1 repetition-determinism,
B1-2 linearity-of-a-single-operator, B1-3 input-reversal/reflection-of-a-single-
operator are the repetition, linearity, and permutation/reflection literature
families -- none pairs the two transforms, none is an adjoint/transpose/inverse
relation. Argument recorded in the suite header.

## Mutgen surface (--lines justification)
mutgen --func exec FAILS ("no function bodies found") -- T_dcst23::exec is a
templated member with an out-of-line `template<typename T> ... void exec(...)`
signature the brace-body regex does not match, and there are 8 overloaded exec()
bodies in the header. Fell back to --lines 2609:2661 = exactly the fix-touched
T_dcst23::exec body (the class's only exec). 35 mutants generated
(18 SDL, 14 ROR, 3 BVR; no AOR -- the region's arithmetic is index/ternary the
AOR regex skips). 8 nocompile -> 27 applied (below the 30-40 quota; this is the
natural yield of a 53-line region after nocompile removal, recorded honestly, no
padding).

## Mutant face (27 applied; 8 nocompile excluded)
  per-MR kills: T1 22 | B1-1 1  B1-2 1  B1-3 8 | B2-1 1  B2-5 0  B2-8 8 | A1-a 19  A1-b 21
  KR all(27):            T1 22/27=0.815  B1 9/27=0.333  B2 9/27=0.333  A1 21/27=0.778
  KR excl-allsurvive(23):T1 22/23=0.957  B1 9/23=0.391  B2 9/23=0.391  A1 21/23=0.913
  kill reasons: 72 oracle_violated + 9 crash_rc-6 (SIGABRT: ROR '<'->'<=' on a
  loop bound -> out-of-bounds c[] access; m010 L2658, m013 L2618).
  4/27 all-survive (m003, m004, m022, m031).

  CAVEAT on "suspected-equivalent": aggregate.py reports all 4 all-survivors as
  "bitwise-identical-to-baseline", but this signal is VACUOUS here -- every
  driver emits only "### X: PASS", so out_sha collapses to the verdict text and
  cannot witness a value change. Verified by hand that m031 (BVR c[0]->c[1] on
  the DCT-II ortho scale, L2637) genuinely changes the transform output
  (dct2-ortho out[0] 16.93 -> 23.95) yet survives ALL MRs: the reflection
  relations survive because x and reverse(x) receive the SAME mis-scaling so
  (-1)^k symmetry is preserved, and T1 is DST-only. So m031 (and by the same
  logic m022, the DST-III-ortho c[0]->c[1] at L2642) are NOT true equivalents --
  they are real behavioral changes UNOBSERVED by this MR set. m003/m004 are
  off-by-one loop-bound relaxations that this driver's inputs do not exercise.

INVERSION note (T1 dominant, one honest counter): T1 out-kills B1/B2 on both
denominators (22 vs 9). 14 mutants killed by T1 but missed by B1; only ONE
(m034, ROR `type==2`->`type!=2`, L2615) is killed by B1/B2 but NOT by T1.
m034 swaps the type-2 and type-3 code paths: T1's oracle D3==D2^T is symmetric
under swapping D2<->D3, so it survives; but the DCT reflection relations
(B1-3/B2-8) run DCT-II input through DCT-III code, breaking (-1)^k, so they
kill it. Opposite direction from C-GSL-001/C-BOOSTMATH-001 (where B1 out-reached
T1): here the defect-specific adjoint oracle dominates a self-inverse-symmetric
mutation surface, and the general reflection relation catches exactly the one
mutant whose symmetry defeats T1. A1 tracks T1 closely (A1-b 21 ~ T1 22):
de-strictifying the tolerance to 0.5 barely weakens it because the killing
mutants produce gross order-1 errors; 降维 to a single N (A1-a 19) loses 3
mutants that only violate at sizes other than N=5.

## Protocol deviations
- Assets rebuilt from git worktrees (not archives); both arms built with a
  single g++ -I<worktree> (header-only). Arms discrimination reproduced exactly
  (see gate above).
- mutgen --func unusable on templated exec; used --lines 2609:2661 over the
  fix-touched T_dcst23::exec body (justified above).
- 27 applied mutants (< 30 quota floor) after 8 nocompile; --limit 40 never
  bound. Recorded, not padded.
- First batch run hit the 2-min foreground wall (SIGTERM) mid-mutant, leaving
  one SDL edit in the header; restored via `git checkout -- pocketfft_hdronly.h`
  in the fixed worktree, then re-ran the full batch clean in background. Final
  header verified pristine (git diff empty).
- build_cmd effectiveness verified end-to-end pre-batch: sine-branch edit
  c[N-1]->c[0] at L2637 -> rebuild -> T1 OVERALL FAIL + A1-a VIOLATED (kill);
  restore -> T1 OVERALL PASS. Confirms header-only recompile truly re-links.
