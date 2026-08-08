# P3 Semantic-Mutant Argumentation Experiment: Methodology Re-review

> Date: 2026-08-08  
> Review type: internal methodology self-review, not an independent external audit  
> Reviewed plan: `docs/superpowers/plans/2026-08-08-p3-semantic-mutant-argumentation-experiment.md`  
> Historical review target SHA-256: `c433ea69f51049f50da9b14d53eb7654c9bf2c7843485ebf4dbc7080887c6ab5`
>
> Status: superseded as a current-plan verdict. The plan was revised after a
> scientific-necessity and engineering-scope review; this note remains only the
> audit record for the historical bytes above.

## Verdict

`PASS_FOR_IMPLEMENTATION_PLANNING`

The revised scientific design is suitable for decomposition into implementation
plans. It is not yet authorization to launch Cursor VM experiments or to claim
empirical support. Implementation tests, a compatible successor P12 contract,
repeatable preflight, and an independent evidence audit remain mandatory.

## Finding closure

| Prior finding | Re-review result |
|---|---|
| Patch mechanism used as semantic family | Closed: construction mechanism and semantic-contract family are orthogonal; primary SMS uses only the latter |
| Reference-MR leakage and criterion circularity | Closed at design level: reference MRs, variants, and uncertain semantic duplicates are excluded by an isolated custodian process |
| Contract, patch, and witness co-design | Closed: state order is contract freeze, exact patch freeze, then first canonical independent witness |
| P12 cohort ambiguity and `DIRECT` selection | Closed: `P12_FULL`, `P12_PAIRED`, and `P12_DIRECT` have different estimands; all mapping states remain in primary family-agnostic analysis |
| Logical rather than physical blindness | Closed at design level: construction, controlled execution, and real holdout use separately hashed physical packages |
| MR subset pseudo-replication and infeasible enumeration | Closed: the full lattice is descriptive; confirmatory subsets use bounded combinadic sampling and one total weight per subject-budget cell |
| RQ4 overfitting and weak power | Closed conditionally: small nested-LOPO models require simulation sensitivity and at least 17 projects/60 real-fault families; otherwise claims downgrade |
| Unequal semantic/syntactic equivalence denominators | Closed: both baselines use common strict and conservative policies |
| P12 v1.1.2 contract override | Closed: the new RQ4 requires a prospectively compatible successor contract; v1.1.2 retains its S1–S2/RFDS estimand |
| Eighteen selected versions could not support the RQ4 floor | Closed: the diversity cohort remains sampled, while the criterion cohort enumerates every unique eligible P12 fixed version without outcome-based sampling |
| Independent evaluation-MR inventory could be empty after reference exclusion | Closed: evaluation MRs come from a predeclared P3 source frame; an empty independent inventory is an explicit terminal scope limitation |
| Package B was called final before the syntactic denominator existed | Closed: Phase 4 freezes an immutable semantic segment; Phase 5 binds it with the syntactic segment and MR/job inputs into the final Package B manifest |

## Residual conditions and consequences

1. **Compatible P12 successor absent:** RQ4 remains a bounded case series; no
   predictive or incremental-value claim is permitted.
2. **Criterion cohort too expensive or too small:** retain the complete failure
   and pairing-coverage ledger and downgrade RQ4; do not sample favorable fixed
   versions.
3. **Package or rule enforcement not implemented:** the plan cannot be launched.
   Prose-level isolation is not evidence of actual isolation.
4. **Independent audit not yet performed:** this self-review cannot substitute
   for the Phase 9 clean-environment evidence gate.
5. **Language-independent IR and adapters remain out of scope:** implementation
   must not silently expand P3 into the deferred follow-up paper.

## Scientific interpretation

The plan now supports a non-circular test of a scoped claim: whether an
independently certified semantic-contract fault domain adds interpretable MR-set
adequacy information within a compatible P12 benchmark. It does not guarantee a
positive result. Construction shortfalls, empty independent MR inventories,
insufficient paired projects, null incremental value, and incompatible P12
contracts all lead to prespecified qualified, boundary, or negative outcomes.
