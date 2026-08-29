# P3 v1.3.0 research-question and claim authority

> **Status:** frozen authority aligned to the governing scientific plan
> **Governing source:** `docs/superpowers/plans/2026-08-08-p3-semantic-mutant-argumentation-experiment.md`
> **Migration:** this authority succeeds v1.2.0 for P3-V3 execution without rewriting the historical v1.2.0 document. The research questions and claim ceiling below are copied verbatim from the governing plan.

## Research questions

### RQ1 — Construction and certification

Can the artifact-first protocol produce executable, independently certified,
non-equivalent semantic-mutant versions across different program scales and
implementation techniques?

Evidence:

- the complete Public Behavior Frame and Profiling Workload/result funnel;
- the complete candidate-to-certified funnel;
- pass, fail, and inconclusive states for every certification gate;
- certification yield by semantic-contract family, program-scale stratum,
  implementation stratum, repository, and target program;
- stable original/mutant semantic witnesses.

RQ1 is descriptive. A failed construction remains evidence about the boundary
of the protocol and is never replaced after confirmatory outcomes are visible.

### RQ2 — Difference from traditional mutation

What semantic-contract, behavioral, patch-structure, and family-coverage
differences exist between certified semantic mutants and frozen first-order
syntactic mutants on the same program versions?

Evidence:

- exact normalized-patch overlap;
- exact mutant-tree overlap;
- independent semantic-contract categories;
- trigger and non-equivalence funnels;
- family and subject coverage.

Structural non-overlap alone does not establish greater testing value. It is a
construct-distinctness result only.

### RQ3 — MR-set adequacy and explanation

Which semantic mutants and semantic-contract families are detected or missed by
each MR set, and what do unique contribution, redundancy, residual risk, and
execution cost reveal beyond a single aggregate mutation score?

The primary controlled-mutant measure is family-balanced semantic mutation
score. Instance-weighted score, conservative equivalence bounds, unique kills,
redundancy, residual families, and cost-normalized coverage are required
secondary views.

### RQ4 — P12 criterion validity and incremental value

On frozen P12 MR-detectable real defects, do semantic-mutant adequacy profiles
explain or predict MR-set detection outcomes, and do they add information beyond
traditional syntactic mutation score?

Primary criterion-validity evidence uses every eligible defect in the paired
P12 cohort and family-agnostic semantic-adequacy features. Outcome-blind
`DIRECT` mappings support a secondary mechanism-concordance analysis.
`ADJACENT`, `OUT_OF_SCOPE`, and `UNCERTAIN` cases remain in the primary
family-agnostic denominator and are reported separately for mapping analyses.

## Claim ceiling

| Claim | Initial status | Upgrade condition |
|---|---|---|
| P3 defines an artifact-first semantic-mutant protocol | `supported` | Governing design and frozen schemas remain consistent |
| The protocol constructs certified mutants across scales and techniques | `blocked` | RQ1 evidence meets behavior-frame, profiling, diversity, and completeness gates |
| Semantic mutants are construct-distinct from the chosen syntactic baseline | `blocked` | RQ2 paired evidence and uncertainty accounting complete |
| Family-aware SMS compares and explains MR-set residuals | `blocked` | Frozen kill matrix and all required adequacy views complete |
| Semantic adequacy adds explanatory value on P12 | `blocked` | RQ4 project-clustered analysis supports the prespecified criterion |
| Semantic mutation is superior for all programs or defects | `blocked` permanently | Outside P3's sampling domain and design |
| P3 provides language-independent automatic mutant generation | `blocked` permanently | Reserved for a later paper |
| The Profiling Workload represents all real-world uses or proves whole-program dynamic reachability | `blocked` permanently | Public repository evidence and selected traces do not identify the full operational population |

Negative or null results do not invalidate the study. They determine which
claims stay blocked and may themselves support a boundary or limitation result.

For the infrastructure-only P3-V3 evidence path, every enumerated claim is
conservatively recorded as `blocked`; this execution ceiling does not alter the
governing table's source status or upgrade condition.

## Current-paper RQ2/C3 scope

On one NumPy subject and four frozen pairs, semantic mutants are
4/4 KILL, syntactic mutants are 3/4 KILL and 1/4 SURVIVE, and both
exact-overlap measures are 0/4. That result is a single-project
paired-evidence pilot, not a multi-project comparison. A later
140-slot applicability census on 14 preregistered successors, under
the frozen Public Behavior Frame, slot inventory, and predicate
bounds, produced 0 SITE_FROZEN. This version therefore has no
Stage II candidate. Multi-project construct-distinctness and
project-clustered uncertainty remain unidentifiable.

### Observed

- NumPy ordinal 8 is a single-project paired-evidence pilot.
- There are 4 frozen pairs.
- Semantic mutants: 4/4 KILL.
- Syntactic mutants: 3/4 KILL, 1/4 SURVIVE.
- Normalized-patch exact overlap: 0/4.
- Mutant-tree exact overlap: 0/4.
- Stage I: 14 subjects, 140 closures, ordinals 9-22.
- 0 SITE_FROZEN, 140 APPLICABILITY_CLOSED_NOT_APPLICABLE.
- Stage II candidate universe = 0.

### Qualified

- The 0/140 count holds only for the frozen Public Behavior Frame,
  slot inventory, applicability predicates, first-applicable
  selection boundary, and the ordinal 9-22 successor universe.
- The current prospective version cannot produce another paired
  project.
- The current Stage II path is lawfully closed.

### Blocked

- C3 remains `blocked`.
- `n_projects = 1`.
- Multi-project construct-distinctness is unidentifiable.
- Project-clustered uncertainty is unidentifiable.
- `RQ2 paired evidence and uncertainty accounting complete` remains
  unmet.

### Current-paper scope

- RQ2 is kept. The current paper answers only single-project paired
  kill/survival on the four frozen NumPy pairs, exact
  normalized-patch and mutant-tree overlap on those pairs, and why
  multi-project construct-distinctness and project-clustered
  uncertainty remain unidentifiable.
- Ordinal 8 is only a single-project paired-evidence pilot.
- Stage I is only a prospective applicability census under a frozen
  authority.
- The original multi-project confirmatory sentence is not a
  current-paper main contribution.
- The current paper does not seek a second or third paired-evidence
  project on this C3 route.
- This amendment does not assemble another subject table, another
  predicate set, or another paired runner, and does not start
  Stage I or Stage II again on this version.
