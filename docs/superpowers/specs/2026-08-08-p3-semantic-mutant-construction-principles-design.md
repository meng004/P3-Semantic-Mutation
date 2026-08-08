# P3 Semantic-Mutant Construction Principles

> Date: 2026-08-08  
> Status: approved principle for subsequent P3 work  
> Scope: P3 Semantic Mutation paper and its reproducible experimental artifacts

## 1. Paper scope

P3 introduces the concept of a semantic mutant and uses controlled semantic
mutants to compare, explain, and evaluate the adequacy of metamorphic-relation
(MR) sets. P3 does not claim to provide a language-independent semantic-
operator intermediate representation, automatic site binding, or a general
cross-language semantic-mutant compiler.

Those automation problems are reserved for a subsequent paper. In P3, program-
version construction is a reproducible experimental protocol, not the primary
engineering contribution.

## 2. Semantic-mutant definition

For an original program version `P` and a declared semantic transformation
`Delta_s`, the mutant program version is:

```text
P_m = apply(P, Delta_s)
```

`Delta_s` belongs to a declared semantic-operator family `s` and must alter a
stated semantic contract while preserving the program's public interface,
executability, and principal computational task.

Every admitted semantic mutant has:

- an immutable original program version;
- a content-addressed patch;
- a declared semantic-operator family;
- a stated semantic contract and expected semantic effect;
- an activation input;
- an MR-independent semantic witness;
- a reproducible mutant program tree or commit; and
- a machine-verifiable certification record.

## 3. Artifact-first construction

P3 uses exact-patch freezing rather than a general mutation compiler.

Candidate patches may be proposed by an author, a project-specific script, or
an LLM. P3 does not evaluate or claim reproducibility of candidate proposal.
The scientific identity is the accepted content-addressed patch and its
certified program version. Reproduction applies the frozen patch; it never
depends on regenerating the same candidate.

Each mutant manifest records at least:

```yaml
mutant_id: immutable neutral identifier
parent_commit: exact original revision
operator_family: declared semantic family
semantic_contract: independently testable property
target_file: repository-relative path
target_symbol: stable symbol or declared region
transformation: exact semantic change
expected_semantic_effect: predicted contract violation
activation_input: content-addressed witness input
independent_oracle: executable non-MR semantic oracle
patch_sha256: canonical patch hash
mutant_tree: exact generated program-tree identity
environment_manifest: content-addressed build and runtime environment
```

The exact schema may be implemented in a later plan, but no field above may be
weakened or replaced by an unstructured reviewer judgment.

## 4. Mechanical certification

An admitted semantic mutant must pass every gate below:

1. `PATCH_SCOPE_PASS`: the committed patch changes only declared paths and
   regions and exactly matches its recorded hash.
2. `BUILD_EXEC_PASS`: the original and mutant versions build and execute in
   the same frozen environment.
3. `INTERFACE_PASS`: the externally evaluated program interface is unchanged.
4. `ACTIVATION_PASS`: the declared target is reached by the frozen witness.
5. `ORIGINAL_CONTRACT_PASS`: the original version satisfies the independent
   semantic contract.
6. `MUTANT_CONTRACT_FAIL`: the mutant violates that same contract.
7. `STABILITY_PASS`: the original/mutant contrast repeats under the frozen
   repetition and determinism policy.
8. `NON_EQUIVALENCE_WITNESS_PASS`: at least one stable semantic-divergence
   witness is preserved.
9. `UNIQUENESS_PASS`: the mutant is not a duplicate patch, program tree, or
   declared semantic instance.

Finite agreement, lack of MR kills, survival under a test suite, or an LLM or
human opinion cannot certify equivalence. Unresolved cases remain visible as
`INCONCLUSIVE` and do not enter the confirmed semantic-mutant denominator.

## 5. Independence from the evaluated MR sets

The semantic contract and construction oracle must be independent of the MRs
whose adequacy is evaluated. A mutant is circular and inadmissible when the
only evidence that it expresses the declared semantic fault is that the target
MR kills it.

All of the following are frozen before MR execution:

- original and mutant identities;
- patches and program trees;
- operator-family assignments;
- semantic contracts and witnesses;
- certification results;
- denominator membership; and
- analysis rules.

MR outcomes may not be used to rewrite a patch, delete a surviving mutant,
change its family, or add a tailored MR within the same confirmatory run.

## 6. MR-set adequacy outputs

P3 evaluates an MR set using more than a single aggregate score. Required
outputs include:

- instance-weighted semantic mutation score;
- semantic-family macro coverage;
- residual semantic families;
- unique contribution of each MR;
- redundancy among MRs; and
- cost-normalized semantic coverage.

These outputs support comparisons between MR sets and explain why two sets
with similar aggregate scores may leave different semantic risks uncovered.

## 7. Empirical evidence layers

P3 separates three evidence roles:

1. Controlled semantic mutants establish operationalization and construct
   coverage.
2. Traditional syntactic mutants provide a comparison signal and do not define
   semantic validity.
3. An immutable P12 Defect4MR benchmark supplies real historical buggy/fixed
   pairs and executable reference-MR outcomes for evaluating whether semantic-
   mutant adequacy has real-defect explanatory or selection value.

Synthetic categories absent from P12 are labelled `CONTROLLED_ONLY` and
`REAL_FAULT_EVIDENCE_ABSENT`. They may support construct coverage but cannot be
reported as observed real-fault prevalence or detection evidence.

## 8. Intended P3 contributions

P3 may claim:

1. a formal and operational concept of semantic mutants;
2. a reproducible artifact-first protocol for constructing and certifying
   controlled semantic-mutant program versions;
3. family-aware adequacy, residual, redundancy, and cost views for comparing MR
   sets; and
4. an empirical test, using P12 under a frozen and non-circular protocol, of
   whether controlled semantic-mutant adequacy explains or improves MR
   selection for MR-detectable real semantic defects.

The construction protocol is necessary method infrastructure, but P3 does not
present a universal automatic semantic-mutant generator as a contribution.

## 9. Deferred subsequent-paper work

The following are explicitly outside P3 and reserved for subsequent work:

- a language-independent semantic-operator intermediate representation;
- automatic semantic-site discovery and binding;
- compiler-grade transformation legality checks;
- reusable Python, C/C++, Julia, Java, Rust, GPU, and mixed-language backends;
- automatic cross-language operator portability;
- automatic synthesis of semantic contracts and independent witnesses; and
- evaluation of end-to-end semantic-mutant generation effectiveness.

P3 artifacts should preserve enough structured information to inform that
future work, but must not imply that the deferred capabilities already exist.

## 10. Prohibited claims

P3 must not claim that:

- semantic operators can be instantiated automatically in arbitrary programs;
- LLM generation is reliable or reproducible merely because accepted patches
  are reproducible;
- the current operator catalogue exhausts the real semantic-fault domain;
- a controlled semantic category absent from P12 is common in real software;
- semantic mutation replaces traditional mutation testing; or
- an MR's ability to kill a mutant proves the mutant's semantic validity.

## 11. Acceptance criteria for subsequent work

Any implementation plan based on this document must preserve all of the
following:

- exact-patch and original-version identity;
- MR-independent construction oracles;
- mechanical, tri-state certification with retained inconclusive cases;
- pre-MR freezing of mutant identities and denominators;
- family-aware and instance-aware reporting;
- separation of controlled-mutant and P12 real-defect claims; and
- explicit exclusion of language-independent automatic generation from the P3
  implementation scope.

