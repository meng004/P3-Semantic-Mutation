```yaml
task_id: b-pocketfft-001-verification
candidate_ids: ["B-POCKETFFT-001"]
branch: claude/defect4mr-b-fftw-002-cloud-fcn18k (coordinator branch; user-authorized live
  experiment naming this specific candidate)
phase: verified_full promotion attempt (first candidate in the entire defect4MR ledger
  to reach a full buggy-fails / fixed-passes experimental closure with both revisions
  identified)
scope: >
  Build the buggy and fixed revisions of PocketFFT (mreineck/pocketfft) identified by
  the Tier-1 expansion scan for B-POCKETFFT-001, and experimentally verify the proposed
  MR oracle (DST-II and DST-III orthonormal transforms must be exact transposes of each
  other) against both revisions.
commands_run:
  - "git clone https://github.com/mreineck/pocketfft.git"
  - "git checkout 076cb3d (buggy revision, parent of the fix commit)"
  - "g++ -std=c++17 -O2 -I. dst_adjoint_check.cpp -o dst_check_buggy -pthread"
  - "./dst_check_buggy  (initial version, N=8 only, included an additional flawed orthonormality assertion -- see negative_evidence)"
  - "git checkout fb21e40 (fixed revision)"
  - "g++ -std=c++17 -O2 -I. dst_adjoint_check.cpp -o dst_check_fixed -pthread"
  - "./dst_check_fixed"
  - "(corrected oracle, dropping the flawed orthonormality assertion, sweeping N={4,5,8,9,16,17} to cover both even and odd sizes)"
  - "git checkout 076cb3d && g++ ... dst_adjoint_check_v2.cpp -o dst_check_v2_buggy && ./dst_check_v2_buggy"
  - "git checkout fb21e40 && g++ ... dst_adjoint_check_v2.cpp -o dst_check_v2_fixed && ./dst_check_v2_fixed"
environment: >
  Cloud sandbox, x86_64 Ubuntu 24.04. g++ version captured in
  logs/cloud/b-pocketfft-001-verification/environment.log. PocketFFT is a header-only
  C++ library (pocketfft_hdronly.h) -- no build system, external dependencies, or
  special environment needed beyond a C++17 compiler.
source_urls:
  - https://github.com/mreineck/pocketfft/commit/fb21e40
  - https://github.com/mreineck/pocketfft/commit/ecd78ca
  - https://github.com/scipy/scipy/issues/21693
artifacts: []
raw_logs:
  - logs/cloud/b-pocketfft-001-verification/result_v1_single_N.log
  - logs/cloud/b-pocketfft-001-verification/result_v2_multi_N.log
  - logs/cloud/b-pocketfft-001-verification/environment.log
scripts:
  - scripts/cloud/b-pocketfft-001-verification/dst_adjoint_check.cpp (initial version, N=8, includes a flawed extra assertion -- kept for transparency)
  - scripts/cloud/b-pocketfft-001-verification/dst_adjoint_check_v2.cpp (corrected, multi-N version -- this is the actual MR oracle used for the final result)
mr_mapping: "m_adj/f_adj.dual (unchanged from the Tier-1 scan proposal)"
proposed_mr_oracle: >
  CORRECTED from the original scan proposal (which incorrectly bundled a caller-side
  normalization assertion into the oracle -- see negative_evidence): For any transform
  size N, build the NxN matrix D2 by applying dst(type=2, ortho=true) to each standard
  basis vector, and the NxN matrix D3 by applying dst(type=3, ortho=true) similarly.
  D3 must equal the transpose of D2, elementwise, within floating-point tolerance. This
  is a pure adjoint/dual-transform-pair property (m_adj/f_adj.dual): DST-II and DST-III
  are mathematically defined as adjoint/transpose operators of each other, and this must
  hold regardless of any external normalization convention -- it is statable and
  checkable purely from that mathematical definition, without reading the fix.
evidence_summary: |
  FULL BUGGY-FAILS / FIXED-PASSES EXPERIMENTAL CLOSURE, the first such result in the
  entire defect4MR ledger with BOTH revisions built and run:

  Buggy revision (076cb3d, the direct parent of the fix commit), swept across N in
  {4, 5, 6=8, 9, 16, 17} (both even and odd sizes):
    N= 4: max|D3 - D2^T| = 1.306563e+00  FAIL
    N= 5: max|D3 - D2^T| = 1.414214e+00  FAIL
    N= 8: max|D3 - D2^T| = 1.387040e+00  FAIL
    N= 9: max|D3 - D2^T| = 1.414214e+00  FAIL
    N=16: max|D3 - D2^T| = 1.407404e+00  FAIL
    N=17: max|D3 - D2^T| = 1.414214e+00  FAIL
  All six sizes fail by an error of order 1 -- far beyond any floating-point tolerance
  explanation, consistent with a genuine algorithmic defect, not numerical noise.

  Fixed revision (fb21e40, "fix orthonormalization of DST II/III?"), same sweep:
    N= 4: max|D3 - D2^T| = 0.000000e+00  PASS
    N= 5: max|D3 - D2^T| = 3.330669e-16  PASS
    N= 8: max|D3 - D2^T| = 4.440892e-16  PASS
    N= 9: max|D3 - D2^T| = 4.440892e-16  PASS
    N=16: max|D3 - D2^T| = 4.440892e-16  PASS
    N=17: max|D3 - D2^T| = 6.661338e-16  PASS
  All six sizes pass at exact double-precision machine epsilon (1-2 ULPs).

  This is a clean, deterministic, multi-point (6 transform sizes, both parities)
  demonstration that the SAME MR oracle fails on the buggy revision and passes on the
  fixed revision -- the defining evidentiary requirement for verified_full status per
  this project's own promotion gate.

  Root cause (confirmed via source diff, matches the WebFetch-based finding from the
  Tier-1 scan): the fix commit changes which boundary coefficient gets the sqrt(2)
  orthonormalization scale factor in the DST branch of T_dcst23::exec (mpi/... no,
  pocketfft_hdronly.h) -- the buggy version applied the scale to c[0] for BOTH cosine
  (DCT) and sine (DST) cases; the fix correctly applies it to c[N-1] for the sine case,
  matching the README's documented convention (which the same commit also corrects).
negative_evidence: >
  The FIRST version of the verification script (dst_adjoint_check.cpp) additionally
  asserted full orthonormality (D2^T @ D2 == I), reasoning that "ortho=true" should
  produce a fully orthonormal transform matrix. This assertion FAILED on both the buggy
  AND the fixed revision (diff ~16-17 on both). Investigation of pocketfft's source
  (ExecDcst / T_dcst23::exec) showed this was this agent's own misunderstanding: the
  "ortho" flag only fixes up the boundary-term scaling asymmetry between DST-II and
  DST-III (which is exactly the transpose-duality property the fix commit addresses);
  achieving full orthonormality additionally requires the CALLER to supply an
  appropriate external "fct" scale factor, which this agent's test passed as a fixed
  1.0. This is NOT related to the actual bug/fix and was NOT used as evidence -- the
  flawed assertion was dropped from the corrected oracle (dst_adjoint_check_v2.cpp),
  and only the transpose-duality property (which the fix commit is actually about) was
  used for the final result. Recorded here transparently rather than silently
  corrected, per this project's no-fabrication standard.
blocked_items: []
proposed_decision: >
  RECOMMEND PROMOTION TO verified_full. This is the strongest evidentiary case in the
  entire ledger: public issue/commit evidence chain (scipy/scipy#21693 downstream
  report + mreineck/pocketfft commit fb21e40 upstream fix, both independently
  fetched and confirmed real), BOTH buggy (076cb3d) and fixed (fb21e40) revisions
  identified AND independently built from source in this session, an MR oracle stated
  purely from the mathematical adjoint/transpose-pair definition of DST-II/III
  (not reverse-engineered from the patch), demonstrated to FAIL deterministically on
  the buggy revision and PASS deterministically on the fixed revision across 6
  different transform sizes (even and odd), not crash-only/API-only/doc-only/
  performance-only, and not attributable to any closed-source backend (PocketFFT is a
  header-only open-source C++ library). This satisfies every criterion this project's
  own subject-pool design doc and candidate schema define for verified_full. Final
  sign-off requested explicitly given how consequential this status is (first
  verified_full in the ledger).
not_a_final_status: false
reviewer_risk: >
  Low. A TOSEM reviewer would find this compelling: the fix commit message itself
  ("fix orthonormalization of DST II/III?") directly names the property being fixed,
  the README correction confirms the documented intent, the buggy-vs-fixed magnitude
  gap (order-1 error vs machine epsilon) is unambiguous, and the multi-N sweep across
  both parities rules out a single-size coincidence. The one point a careful reviewer
  might probe: this agent's own initial oracle-design mistake (the flawed
  orthonormality assertion) -- but that is disclosed transparently here, was corrected
  before drawing any conclusion, and did not affect the final, narrower, mathematically
  well-justified oracle used for the verified_full claim.
drift_check: >
  Stayed within B-POCKETFFT-001 scope only. No candidate status was changed without
  this explicit report requesting sign-off first (the actual JSON promotion is a
  separate, subsequent action pending user confirmation). No other PocketFFT
  candidates (B-POCKETFFT-002/003/004) were touched in this task.
exit_condition_met: true
quality_review:
  evidence_traceability: >
    Maximal: both revisions were independently git-cloned and checked out by commit
    hash (not inferred), both were compiled and executed with output captured verbatim
    in the raw logs, and the multi-N sweep provides internal cross-validation (6 data
    points, not 1). The one imperfection (the abandoned orthonormality assertion) is
    disclosed rather than hidden.
  mr_oracle_validity: >
    High. The final oracle is stated purely from DST-II/DST-III's mathematical
    adjoint-pair definition, independently of the patch, and was empirically shown to
    discriminate cleanly between the buggy and fixed revisions with no ambiguity
    (order-1 vs machine-epsilon errors, not a borderline case).
  defect_type_fit: >
    Clean numeric/semantic MR violation (m_adj/f_adj.dual) -- not crash-only (no
    crash occurred in either revision), not API-only, not documentation-only (though
    the README was also corrected, the actual numeric behavior changed), not
    performance-only.
  backend_attribution_risk: >
    None -- PocketFFT is fully open-source, header-only C++; no closed-source backend
    (oneMKL/cuBLAS/cuSOLVER/cuFFT/cuSPARSE/cuDNN) is involved anywhere in this build or
    execution.
  tosem_reviewer_risk: >
    Low, as detailed in reviewer_risk above -- this is the strongest, most
    self-contained, most rigorously verified finding in the ledger to date.
```

## Prose write-up

### What was verified

PocketFFT's DST-II and DST-III transforms, when both computed in "ortho" mode, are
mathematically defined to be transposes of each other (this is what "orthonormal
transform pair" means for the sine transform family). The fix commit `fb21e40`
("fix orthonormalization of DST II/III?") corrects a bug where the boundary-coefficient
scaling was applied to the wrong array position for the sine (DST) case, breaking this
transpose relationship.

### The experiment

Both the buggy revision (`076cb3d`, the direct parent of the fix) and the fixed revision
(`fb21e40`) were built from source (PocketFFT is header-only, so this is a single g++
invocation, no build system needed) and tested against the same oracle: construct the
NxN DST-II matrix `D2` and DST-III matrix `D3` by applying each transform to every
standard basis vector, then check `D3 == D2^T` elementwise.

Swept across 6 transform sizes (4, 5, 8, 9, 16, 17 -- covering both even and odd N,
since the fix's boundary-scaling logic branches differently for the two parities):

- **Buggy**: every single size fails, with `max|D3 - D2^T|` between 1.3 and 1.41 --
  errors of order 1, nowhere near floating-point noise.
- **Fixed**: every single size passes, with `max|D3 - D2^T|` at 0 to ~6.7e-16 -- exact
  double-precision machine epsilon.

### A transparent correction along the way

The first version of this test additionally asserted full orthonormality
(`D2^T @ D2 == I`), which failed on *both* revisions. Rather than reporting a confusing
or misleading result, this was investigated: PocketFFT's `ortho` flag only corrects the
*relative* boundary scaling between DST-II and DST-III (restoring the transpose
relationship) -- achieving absolute orthonormality additionally requires the caller to
supply a normalization constant via the `fct` parameter, which this test held fixed at
`1.0`. That is a test-construction detail unrelated to the actual bug, so it was dropped
from the final oracle, leaving only the well-justified, patch-independent
transpose-duality check.

### Recommendation

This is proposed for promotion to `verified_full` -- the project's highest evidentiary
tier, requiring a public issue/PR/commit chain, identified buggy AND fixed revisions,
and the fixed revision passing the same oracle the buggy revision fails. All of these
are now satisfied with real, independently-executed evidence. Given how consequential
this status is (the first `verified_full` entry in the entire ledger), this report
requests explicit user sign-off before the ledger is updated, consistent with how the
B-FFTW-001/005 `candidate_full` promotions were handled earlier in this session.
