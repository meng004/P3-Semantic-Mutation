# Cover Letter

Dear Editor,

We submit "A Semantic Mutation Metric for Metamorphic-Relation Adequacy in
Scientific Computing Programs" as a Journal-First Paper for ACM Transactions on
Software Engineering and Methodology (TOSEM). The manuscript is intended for
Fast-Impact Track handling if it satisfies TOSEM's page-length eligibility
condition.

The manuscript contributes Semantic Mutation Score (SMS), a
backward-compatible adequacy metric that preserves the denominator logic of
classical mutation testing while making the observed semantic effect explicit
for metamorphic-relation sets. The empirical evidence combines a 12-program
stress test, an AST-normalized syntactic-overlap audit, boundary and adjoint
arms, and an industrial real-defect arm: result-level statistics over
reproduced, MR-detectable defects from widely used scientific-computing
libraries, used to confirm the paper's construct separation among aggregate
kill-rate, semantic alignment, and real-defect detection.

Related-work disclosure. The industrial arm draws its result-level statistics
from a defect dataset curated and archived by the authors (Zenodo DOI
10.5281/zenodo.21203424). Benchmark construction, curation protocol, and
governance are not claimed as contributions of this manuscript and are
intended for a separate benchmark/artifact paper; the two manuscripts do not
overlap in claimed contributions (metric and construct validation here;
dataset construction methodology there).

An earlier version is available on arXiv as arXiv:2605.17437. The current
submission substantially sharpens the semantic-mutation framework, adds
formal terminology and argument-evidence mapping, clarifies non-claims, and uses
real-defect evidence only to support the paper's argument. The work is not
under simultaneous archival review elsewhere.

The replication package is archived on Zenodo under DOI
10.5281/zenodo.20250664. Extended proofs, protocol details, sensitivity
analyses, and the result-level real-defect evidence summary is provided as
supplementary material.

Journal-first novelty statement. This submission reports a new archival
contribution rather than an extension of any prior archival publication. The
work is available as arXiv:2605.17437, and that preprint is disclosed here for
transparency; it has not appeared in a conference, journal, or workshop
proceedings. Relative to the public preprint and to the closest
mutation-testing and metamorphic-testing literature, the TOSEM submission is
novel in five respects. First, it makes the adequacy object an MR set and makes
the denominator an admitted universe of nonequivalent domain-semantic mutants,
rather than syntactic mutants, MR obligations, or execution coverage. Second,
it introduces an explicit semantic-certificate and equivalence discipline and
establishes the degeneration of SMS to classical mutation score under the syntactic
limit. Third, it instantiates five semantic operator families for
scientific-computing kernels and audits their first-order syntactic
reachability. Fourth, it separates MR alignment, aggregate kill rate, and
real-defect detection using boundary and adjoint arms plus an industrial
real-defect arm with a four-group mutation comparison pre-registered in the
dataset protocol over reproduced library defects. Fifth, it narrows the claim from benchmark construction to construct
validation, with supplementary material and artifacts separating
reproducibility details from the main argument.

Length statement. The main manuscript is 40 pages including references in the
ACM manuscript-review format; the text before the bibliography remains below
the 45-page Fast-Impact threshold stated in the TOSEM author guidance.

Sincerely,

Meng Li
