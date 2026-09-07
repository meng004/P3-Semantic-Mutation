# Phase 3 — Gap Synthesis and Verdict on the Surviving Increment

**Agent:** `synthesis_agent` (ARS deep-research, Phase 3 SYNTHESIS)
**Date:** 2026-09-07
**Target venue of parent paper:** ACM TOSEM
**Upstream read in full:** `phase1_rq_brief_provisional.md`; `phase2_bibliography_A_mr_adequacy.md`; `phase2_bibliography_B_mutation_constructs.md`; `phase2_bibliography_C_structure_preservation.md`; `phase2b_audit_consolidation.md`; `docs/STATE.md` §1–§1.1; `research/p3-equation-structure-preservation-mr-adequacy-plan-v4-zh.md`; `research/p3-tosem-editorial-assessment-v4-zh.md`
**Primary text fetched independently by this agent:** arXiv:2605.17437v2 and arXiv:2606.08269v1 abstracts, both via `user-paper-search` → `search_arxiv` (verbatim, quoted below). `search_dblp` and `search_semantic` not attempted, per caller instruction.

> **Boundary.** This document is Phase 3 only: synthesis, contradiction resolution, gap mapping, judgement. It contains no paper sections, no experiment redesign, no editorial review, no revision. Where downstream work is required it is named and handed back.

---

## Claim Intent Manifest

```json
{
  "manifest_version": "1.0",
  "manifest_id": "M-2026-09-07T19:20:00Z-p3s1",
  "emitted_by": "synthesis_agent",
  "emitted_at": "2026-09-07T19:20:00Z",
  "claims": [
    {
      "claim_id": "C-001",
      "claim_text": "The increment scoped in STATE.md §1.1 constraint 2 — the ESPR O component plus verdict-independence, with D and kappa — cannot carry a TOSEM paper on its own; verdict INCREMENT_INSUFFICIENT.",
      "intended_evidence_kind": "theoretical",
      "planned_refs": ["arxiv2605.17437", "arxiv2606.08269", "C3.3", "C4.5", "C4.6", "A3.1"],
      "negative_constraints": [
        {"constraint_id": "NC-C001-1", "rule": "No claim that arXiv:2605.17437 contains or lacks a verdict-independence protocol beyond what its abstract states; full-text status must stay hedged."}
      ]
    },
    {
      "claim_id": "C-002",
      "claim_text": "Two of the five certifiers proposed for the O component (round-trip residual; grid-refinement order) are isomorphic to established metamorphic-relation families and therefore fail verdict-independence by construction.",
      "intended_evidence_kind": "theoretical",
      "planned_refs": ["A1.4", "A2.5", "C4.1"],
      "negative_constraints": [
        {"constraint_id": "NC-C002-1", "rule": "No claim that these certifiers are useless; only that they cannot serve as MR-verdict-independent certification."}
      ]
    },
    {
      "claim_id": "C-003",
      "claim_text": "The two structurally safe certifiers (discrete operator commutator; adjoint bilinear identity) require a program that exposes discrete operators, which the four single-output float-to-float PUT classes of arXiv:2605.17437 do not.",
      "intended_evidence_kind": "empirical",
      "planned_refs": ["arxiv2605.17437", "C1.3", "C4.5"]
    },
    {
      "claim_id": "C-004",
      "claim_text": "The boundary against arXiv:2606.08269 is crossed by any claim about MR-subset selection, minimality, completeness, hardness, approximation, or safety-of-class-level-abstraction; the citation-removal test operationalises the line.",
      "intended_evidence_kind": "definitional",
      "planned_refs": ["arxiv2606.08269"]
    },
    {
      "claim_id": "C-005",
      "claim_text": "Theme A's PARTIAL and Theme C's DIRECT_PRIOR_ART are not in conflict; the slot Theme A finds empty in the independent literature is the slot Theme C finds filled by the authors themselves, and under the supersede decision this is an entitlement rather than a collision.",
      "intended_evidence_kind": "theoretical",
      "planned_refs": ["A3.1", "A3.2", "C3.1", "arxiv2605.17437"]
    },
    {
      "claim_id": "C-006",
      "claim_text": "STATE.md §1.1 constraint 2 is itself an over-defensive claim-shrinkage under project rule §10.1, because the supersede decision dissolves the self-prior-art problem it was written to avoid.",
      "intended_evidence_kind": "normative",
      "planned_refs": ["arxiv2605.17437"]
    },
    {
      "claim_id": "C-007",
      "claim_text": "The 'semantic mutation' terminology collision with Clark, Dan and Hierons is a credibility and findability threat rather than a novelty threat, aggravated by Dan and Hierons having already applied semantic mutation to floating-point comparison semantics in numerical code.",
      "intended_evidence_kind": "literature",
      "planned_refs": ["B3-1", "B3-2", "B3-4", "B3-5"]
    },
    {
      "claim_id": "C-008",
      "claim_text": "The single highest-value unresolved evidence conflict is whether Fu et al. (2024) generate testing requirements from the MR set or independently from SUT necessary properties; Theme A's central distinction rests on an abstract-level inference its own limitation section undercuts.",
      "intended_evidence_kind": "literature",
      "planned_refs": ["A3.1"]
    }
  ],
  "manifest_negative_constraints": [
    {"constraint_id": "MNC-1", "rule": "No paper sections, no experiment design, no editorial review, no revision — Phase 3 deliverable only."},
    {"constraint_id": "MNC-2", "rule": "No claim sourced from model memory; every claim traces to a Phase 1/2 artefact or to primary text fetched in this session."},
    {"constraint_id": "MNC-3", "rule": "No claim about the contents of any full text that Phase 2 recorded as unretrievable; such claims must be marked as pending a full-text read."},
    {"constraint_id": "MNC-4", "rule": "No recommendation presented as a decision; author-facing options must be labelled as options."}
  ]
}
```

---

## §1. Verdict on the Surviving Increment

### 1.1 Verdict

# `INCREMENT_INSUFFICIENT`

The increment as scoped — the ESPR five-tuple's **O** component plus verdict-independence, with explicit **D** and **κ** — cannot carry an ACM TOSEM paper. It is a validity repair to a protocol the authors have already published, assembled from certification instruments that are individually published prior art, and its two structurally sound instances are inapplicable to the program population on which the published work rests.

That verdict is about the increment **as the load-bearing novelty of a standalone contribution**. §1.5 argues that under the author's own supersede decision this is the wrong test to be applying, and that the constraint which forces it is itself a claim-shrinkage that project rule §10.1 requires to be challenged.

### 1.2 What arXiv:2605.17437 actually says

Fetched independently in this session via `search_arxiv`, arXiv:2605.17437v2 (v1 2026-05-17, v2 2026-07-07; cs.SE, cs.LG; Meng Li, Xiaohua Yang, Jie Liu, Shiyu Yan). The abstract, quoted in the parts that bear on the increment:

> "Context. Metamorphic Testing addresses the test-oracle problem in scientific computing, but classical Mutation Score operates on syntactic AST mutations and misses domain semantics."

> "Objective. We propose the Semantic Mutation Score (SMS), built on five domain-semantic operators (Conservation Erosion, Operator Substitution, Hyperparameter, Trajectory Flip, Structural Injection). SMS degenerates almost everywhere to MS in a characterised limit …"

> "Method. A 12-PUT x 5-MP design over four single-output float-to-float classes (numeric, probabilistic, surrogate, machine-learning) is paired with a three-layer attribution classifier separating true semantic faults from tolerance, OOD, statistical, and artefact categories."

> "Results. The pre-registered large-effect threshold for Cliff's delta is not met under the point-estimate criterion; the observed effect lies in the medium-effect range. … AST-level overlap between LLM-generated and default cosmic-ray syntactic mutants is small; the Hyperparameter, Structural Injection, and Trajectory Flip classes are unreachable under default first-order syntactic configurations."

> "Conclusion. SMS is a backward-compatible adequacy metric for domain-semantic metamorphic-relation sets in scientific computing. The first-order unreachability evidence is independent of the effect-size question."

(arXiv:2605.17437v2 abstract) <!--ref:arxiv2605.17437--><!--anchor:quote:SMS%20is%20a%20backward%2Dcompatible%20adequacy%20metric%20for%20domain%2Dsemantic%20metamorphic%2Drelation%20sets%20in%20scientific%20computing-->

Four things follow directly from that text, and the v4 plan's framing does not survive any of them.

**(a) The adequacy-metric slot is explicitly claimed.** Not "a metric that could be read as an adequacy metric" — the conclusion sentence asserts it in those words. SLRMA cannot be introduced as the first adequacy measure for domain-semantic MR sets in scientific computing, because that assertion is already in the public record under the same author string. Theme C reached the same conclusion from the same text and graded it `DIRECT_PRIOR_ART` <!--ref:C3.1--><!--anchor:section:C3.1-->.

**(b) The B component is already operational, under another name.** The three-layer attribution classifier "separat[es] true semantic faults from tolerance, OOD, statistical, and artefact categories" <!--ref:arxiv2605.17437--><!--anchor:quote:a%20three%2Dlayer%20attribution%20classifier%20separating%20true%20semantic%20faults%20from%20tolerance%2C%20OOD%2C%20statistical%2C%20and%20artefact%20categories-->. Excluding discretisation, statistical and floating-point error before declaring a violation *is* the error-budget function that ESPR names **B**. Theme C recorded this reading in the same terms <!--ref:C3.1--><!--anchor:section:C3.1-->. So B is a renaming, and a reviewer who reads the two documents side by side will say so.

**(c) The headline empirical asset is the unreachability result, not the effect size.** The abstract states the pre-registered large-effect threshold was not met and that the observed effect is medium <!--ref:arxiv2605.17437--><!--anchor:quote:The%20pre%2Dregistered%20large%2Deffect%20threshold%20for%20Cliff%27s%20delta%20is%20not%20met%20under%20the%20point%2Destimate%20criterion-->. It also states that "the Hyperparameter, Structural Injection, and Trajectory Flip classes are unreachable under default first-order syntactic configurations" and that this evidence "is independent of the effect-size question" <!--ref:arxiv2605.17437--><!--anchor:quote:the%20Hyperparameter%2C%20Structural%20Injection%2C%20and%20Trajectory%20Flip%20classes%20are%20unreachable%20under%20default%20first%2Dorder%20syntactic%20configurations-->. Any v4 narrative that leads with a positive effect-size claim contradicts the record it is superseding.

**(d) The abstract is silent on whether the attribution classifier consumes MR verdicts.** It does not say the classifier is verdict-independent, and it does not say it is verdict-dependent. This is the single fact on which the size of the increment turns, and it cannot be settled from the abstract. Phase 2 recorded the same observation and handed it forward without interpretation <!--ref:C3.1--><!--anchor:section:C3.1-->. **Pending verification of the classifier's per-layer inputs, the increment's magnitude is unknown, and every statement about it in this document is conditional on that read.**

### 1.3 Why the O component, as scoped, does not clear the bar

Five reasons, in descending order of how hard they are to remove.

**R1 — The verdict-independent certifier pool is far smaller than the plan assumes, because two of its five members are metamorphic relations wearing a different label.** The plan's certifier list is conservation (source–sink–boundary balance), symmetry (discrete operator commutator), adjointness (bilinear identity), reversibility (round-trip residual), and convergence (independent grid sequence and error order) <!--ref:STATE-md--><!--anchor:section:§3-->. Chen et al. define the central element of MT as "a set of metamorphic relations, which are necessary properties of the target function or algorithm **in relation to multiple inputs and their expected outputs**" <!--ref:A1.4--><!--anchor:quote:a%20set%20of%20metamorphic%20relations%2C%20which%20are%20necessary%20properties%20of%20the%20target%20function%20or%20algorithm%20in%20relation%20to%20multiple%20inputs-->. Under that definition:

| Proposed certifier | Structure | Verdict-independent? |
|---|---|---|
| Round-trip / reversibility residual | Relation between two executions of the program and their outputs | **No.** This is a reversibility MR by construction. The v4 plan lists 可逆 (reversibility) as an ESPR property φ *and* as a certifier — the same object on both sides of the ledger <!--ref:v4-plan--><!--anchor:section:§2.1--> |
| Grid-refinement order / GCI | Relation across executions at multiple resolutions | **No.** Refinement is one of the founding MRs for numerical programs: Chen, Feng & Tse derived an MR "from the numerical property that refining grid points or step size yields a better approximation" <!--ref:A2.5--><!--anchor:quote:refining%20grid%20points%20or%20step%20size%20yields%20a%20better%20approximation-->. Roache's GCI is the reporting instrument for exactly that family <!--ref:C4.1--><!--anchor:page:405-413--> |
| Discrete operator commutator | Algebraic identity on discrete operators; no input/output pairing | **Yes.** Arnold, Falk & Winther supply the commuting-diagram form of structure preservation that this test instantiates <!--ref:C1.3--><!--anchor:page:1-155--> |
| Adjoint bilinear identity (dot-product test) | Identity between linearised primal and adjoint operators | **Yes.** Ugolotti et al. implement it as a solver verification procedure <!--ref:C4.5--><!--anchor:section:C4.5--> |
| Global source–sink–boundary balance | Single-run, single-mesh volume-integrated balance | **Conditionally.** Verdict-independent, but Haworth et al. state the imbalance is informative *only* for quantities not conserved at cell level by construction; where the scheme conserves exactly, the imbalance is identically zero regardless of implementation correctness <!--ref:C4.6--><!--anchor:quote:allows%20a%20direct%20assessment%20of%20numerical%20accuracy%20in%20a%20single%20run%20using%20a%20single%20mesh--> |

The editorial assessment demands at least three genuinely orthogonal certifiers <!--ref:editorial-v4--><!--anchor:section:§3-->. On this analysis the plan has two clean ones and one that is silent on precisely the primary-conservation properties it would be assumed to certify. This is not a presentational problem; it is the failure mode the caller asked to be named. **If reversibility or refinement is used to certify SPTM mutants, a reviewer characterises the certification as an MR verdict in disguise, and the increment collapses in one sentence.**

**R2 — The two clean certifiers do not apply to the existing program population.** A discrete operator commutator test requires a program that exposes discrete divergence, gradient or curl operators. An adjoint dot-product test requires an exposed adjoint or linearised operator. arXiv:2605.17437's population is "four single-output float-to-float classes (numeric, probabilistic, surrogate, machine-learning)" <!--ref:arxiv2605.17437--><!--anchor:quote:four%20single%2Doutput%20float%2Dto%2Dfloat%20classes%20%28numeric%2C%20probabilistic%2C%20surrogate%2C%20machine%2Dlearning%29-->. A single-output float-to-float function exposes neither. So O cannot be demonstrated on the development set at all; it requires a new PUT population of operator-exposing solvers. That collides head-on with FINER Feasible = 3/5 and the three documented cost records behind it: Boost.Math stalled at roughly 70%, the NumPy pilot reached one project and four pairs, and the 14-subject applicability survey produced zero Stage II candidates <!--ref:phase1-brief--><!--anchor:section:§8-->.

**R3 — O's definitional core is published, non-self prior art.** Bartocci et al. define property-based mutation testing so that a mutant is relevant only if it can affect satisfaction of a specified property and is meaningfully killed only if it causes that property's violation, evaluated on safety-critical Simulink models <!--ref:C3.3--><!--anchor:section:C3.3-->. That is certification of a mutant against a declared obligation using a monitor that is not the test suite's verdict. Theme C ranks it the nearest non-self prior art at roughly two constructs' distance, the difference being property provenance (temporal-logic requirement versus governing equation) and the absence of κ, B and O <!--ref:C3.3--><!--anchor:section:C3.3-->. Ding, Li & Hu had already used violation of a necessary domain relation as the injected-fault target in scientific software <!--ref:C3.4--><!--anchor:section:C3.4-->.

**R4 — The evaluation shape is established practice in a lineage the project has not yet engaged.** Theme B records that mutation analysis already measures the completeness of *declared obligations*: the program is mutated, and the fraction of mutants the contracts or specifications fail to reject is the measure of specification weakness (Knauth et al., ICSTW 2009, 182–191; Knüppel et al., FormaliSE 2021, 42–53) <!--ref:B4.3-lineages--><!--anchor:section:§4.3-->. Substituting "MR set" for "contract set" changes the obligation's provenance, not the measurement architecture. This is a closer structural neighbour than the semantic-mutation-testing collision and it is currently unaddressed in the plan.

**R5 — Formalisation cannot be cashed out, because the theory layer is fenced.** The usual way a tuple formalism earns a TOSEM contribution is by yielding a theorem, a bound, or a prediction the informal version cannot make. arXiv:2606.08269 already holds the completeness criterion, the domination boundary, the Set-Cover equivalence, NP-hardness, the greedy approximation, the exact ILP and the SMS-rank upper bound <!--ref:arxiv2606.08269--><!--anchor:quote:giving%20NP%2Dhardness%2C%20the%20classical%20logarithmic%20approximation%20boundary%2C%20a%20greedy%20approximation%2C%20an%20exact%20ILP%20formulation-->, and hard constraint 3 forbids restating any of it <!--ref:STATE-md--><!--anchor:section:§1.1-->. So the formalisation route is closed at the same time the empirical route (R2) is expensive. That squeeze is the structural reason the increment is insufficient rather than merely thin.

### 1.4 What O would have to do and demonstrate to count

Concretely, and each item falsifiable:

1. **Name, for every node of the structural lineage G, a certifier that is not a relation over program executions.** Operationally: the certifier must be computable from a single execution plus static artefacts (discrete operator matrices, adjoint operators, integrated balances), or from no execution at all. Any certifier requiring a (source, follow-up) execution pair is disqualified on its face. Expected consequence, stated in advance so it can fail: G shrinks to the property classes for which such a certifier exists, which on present evidence is symmetry/equivariance, adjointness, and secondary conservation — not reversibility, not convergence order.
2. **Publish an applicability matrix with the silence cases marked.** For each certifier, the property classes it can certify, the classes it provably cannot, and why. Haworth et al.'s zero-imbalance case must appear as an explicit silence entry <!--ref:C4.6--><!--anchor:section:C4.6-->, and Limache et al.'s warning that an objectivity failure may be a formulation defect rather than an implementation fault must appear as a scope entry <!--ref:C4.7--><!--anchor:section:C4.7-->.
3. **Demonstrate that verdict-independent admission changes the measurement.** Recompute the adequacy scores on the same programs under certified-only mutant admission and report the difference against the published SMS numbers. This is the only way O becomes a result rather than hygiene. **Pre-register the direction and a minimum detectable difference.** If the recomputed scores sit inside noise of the published ones, O has no measurable consequence and belongs in the threats section — and, per §1.3, nothing else in the scoped increment is load-bearing.
4. **Show independence, not just assert it.** A reviewer will ask for the certifier's decision function and check whether any argument to it is derived from an MR outcome. The paper must therefore print the certifier's inputs, per layer, and state which of them are also inputs to any MR in R. Overlap of even one observable is enough to sustain the "verdict in disguise" objection.
5. **Distinguish O from the three published lineages simultaneously.** Bartocci et al.'s property-violating kill <!--ref:C3.3--><!--anchor:section:C3.3-->, the contract-completeness mutation lineage <!--ref:B4.3-lineages--><!--anchor:section:§4.3-->, and the code-verification fault-seeding pattern of Salari & Knupp and Krueger et al. <!--ref:C2.2--><!--anchor:section:C2.2--> <!--ref:C2.6--><!--anchor:section:C2.6-->. Krueger et al.'s MEAMMS sets the concrete bar: it detects a strict superset of what MMS detects, including errors at the same order as the numerical method <!--ref:C2.6--><!--anchor:section:C2.6-->. A new certification apparatus that detects less than MEAMMS will be asked why it exists.

### 1.5 The question the caller asked is, under the author's own decision, the wrong question

This is the part of §1 that project rule §10.1 obliges me to raise rather than route around.

Hard constraint 2 says novelty rests only on O and verdict-independence, because SPTM and SLRMA are occupied by arXiv:2605.17437 <!--ref:STATE-md--><!--anchor:section:§1.1-->. But hard constraint 4 says v4 will **replace** arXiv:2605.17437 as a new version of the same arXiv entry rather than opening a new one <!--ref:STATE-md--><!--anchor:section:§1.1-->. Those two constraints cannot both do work at once. If v4 supersedes 2605.17437, then after supersede there is exactly **one** paper in the public record. A paper does not need to establish novelty against the version of itself that it replaced. Reviewers assess the increment over the *external* literature.

So the self-prior-art problem that constraint 2 was written to avoid is dissolved by constraint 4. What constraint 2 actually does is voluntarily surrender the SMS-level contribution the supersede framing entitles the author to claim, and reassign the entire novelty burden to the weakest component of the framework. By the §10.1 judgement table that is **主张收缩 (claim shrinkage), not 效度修复 (validity repair)**: it narrows the claim range not because evidence showed the larger claim untestable, but to pre-empt an accusation that the supersede decision has already answered. The honest handling is to defend it or retract it, and on this analysis it does not survive defence.

Reframed correctly, the novelty test v4 must pass is:

> Against Fu et al. (2024) <!--ref:A3.1--><!--anchor:section:A3.1-->, Liu et al. (2024) <!--ref:A3.2--><!--anchor:section:A3.2-->, Bartocci et al. (2023) <!--ref:C3.3--><!--anchor:section:C3.3-->, Yan & Zhu (2025) <!--ref:C3.6--><!--anchor:section:C3.6-->, Xie et al. (2024) MUT <!--ref:A3.10--><!--anchor:section:A3.10--> and the contract-completeness lineage <!--ref:B4.3-lineages--><!--anchor:section:§4.3-->, what does this paper establish that none of them does?

That question has a defensible answer (§3.4), and the answer is not O. Retaining constraint 2 makes the paper both weaker and harder to falsify, which is the specific failure mode project rule §10 prohibits.

---

## §2. The arXiv:2606.08269 Boundary

### 2.1 The preprint's results, verbatim

Fetched independently in this session via `search_arxiv`. arXiv:2606.08269v1, 2026-06-06, cs.SE / cs.DS, Meng Li, Xiaohua Yang, Jie Liu, Shiyu Yan:

> "We define a layer-relative completeness criterion over an admitted mutant–draw coverage universe. The central result is a support-set domination boundary: it states when class-level abstraction is safe and when mutant-level MR minimization is necessary. The boundary is governed by kill-signature heterogeneity, which yields a scoped fault-signature kernel and separates the MR-specific question from ordinary fault-class counting. The resulting Min-MR-Complete problem is Set-Cover-equivalent over the selected coverage universe, giving NP-hardness, the classical logarithmic approximation boundary, a greedy approximation, an exact ILP formulation, and an SMS-rank upper bound that is not a lower bound or tight predictor. Artifact lanes provide lane-local minimization and audit evidence; separately, route witnesses instantiate both collapse and non-collapse regimes for the boundary theorem and are not pooled as population-level experiments."

(arXiv:2606.08269v1 abstract) <!--ref:arxiv2606.08269--><!--anchor:quote:The%20central%20result%20is%20a%20support%2Dset%20domination%20boundary%3A%20it%20states%20when%20class%2Dlevel%20abstraction%20is%20safe-->

### 2.2 Cite-only inventory

Every item below is **cite-only** for v4. None may be derived, re-proved, re-stated in different notation, or presented as a v4 result.

| # | Result | Cite-only | What restating looks like |
|---|---|---|---|
| B1 | Layer-relative completeness criterion over the admitted mutant-draw coverage universe | Yes | v4 defining any completeness notion for MR sets, at any layer, in any notation |
| B2 | Support-set domination boundary — when class-level abstraction is safe versus when mutant-level minimisation is necessary | Yes | **The highest-risk item.** Any v4 argument that aggregating at lineage-node level is or is not adequate, or that mutant-level resolution is or is not required |
| B3 | Kill-signature heterogeneity as the governing quantity; the scoped fault-signature kernel | Yes | v4 introducing any heterogeneity, signature or kernel construct over kill patterns to justify an aggregation choice |
| B4 | Separation of the MR-specific question from ordinary fault-class counting | Yes | v4 arguing that its structural lineage is more than fault-class counting *by that route* |
| B5 | Set-Cover equivalence of Min-MR-Complete over the selected coverage universe | Yes | Any reduction, equivalence or correspondence between MR selection and a covering problem |
| B6 | NP-hardness | Yes | Any hardness or intractability statement about MR-set selection |
| B7 | Classical logarithmic approximation boundary | Yes | Any approximation-ratio statement |
| B8 | Greedy approximation algorithm | Yes | Any greedy or incremental MR-selection procedure with a quality argument |
| B9 | Exact ILP formulation | Yes | Any optimisation program over MR subsets |
| B10 | SMS-rank upper bound, explicitly not a lower bound and not a tight predictor | Yes | Any statement connecting an adequacy score or its rank to the size of a sufficient MR set |
| B11 | Artifact-lane / route-witness evidence architecture, including the collapse and non-collapse regimes | Yes | v4 adopting lane-local minimisation or witness-regime language as its own evidence design |

### 2.3 The concrete test the authors can apply to any draft paragraph

Three questions, in order. The first that returns a verdict wins.

**Q1 — What does the paragraph's conclusion range over?**
- Over **subsets of R** (which MRs to keep, drop, add, select, minimise, or declare sufficient) → arXiv:2606.08269 side. Cite only.
- Over **the mutant population M given a fixed R** (whether R kills a certified mutant; what fraction of lineage node g is covered; whether a certifier fires) → v4 side.

**Q2 — What is the paragraph's main verb?** If it is *select, minimise, suffice, complete, dominate, bound, reduce-to, is-hard, approximate,* or *is-safe-to-abstract*, the paragraph is on the arXiv:2606.08269 side regardless of Q1.

**Q3 — The citation-removal test (decisive).** Delete the citation to arXiv:2606.08269 from the paragraph and reread it.
- If the paragraph still asserts the result, with its own supporting argument intact → **it is restating.** Rewrite or delete.
- If the paragraph becomes unsupported, and a reader would ask "on what authority?" → **it is citing.** Restore the citation and keep.

One-line form for a draft margin: **v4 evaluates a given R against a certified M; 2606.08269 selects an R. If deleting the citation leaves the claim still standing on its own legs, you have restated it.**

### 2.4 The live collision the authors must resolve first

The editorial assessment requires v4 to explain why the lineage-imbalance aggregation is a macro-average and whether alternative aggregations are robust <!--ref:editorial-v4--><!--anchor:section:§3-->. SLRMA's macro-average over G is a class-level abstraction of the mutant population <!--ref:v4-plan--><!--anchor:section:§2.3-->. The question "when is class-level abstraction safe?" is verbatim B2 <!--ref:arxiv2606.08269--><!--anchor:quote:it%20states%20when%20class%2Dlevel%20abstraction%20is%20safe%20and%20when%20mutant%2Dlevel%20MR%20minimization%20is%20necessary-->.

So the editorial requirement and hard constraint 3 point in opposite directions on the same paragraph. Only two exits exist, and the authors must pick one before drafting: **(i)** justify the macro-average on a ground that is not abstraction-safety — for example measurement-theoretic comparability across unbalanced lineage nodes, with the aggregation choice pre-registered and a sensitivity analysis reported descriptively; or **(ii)** cite arXiv:2606.08269 for the abstraction-safety condition and state, without deriving it, that the macro-average is used inside the regime that preprint characterises. Exit (i) is cleaner for the supersede narrative; exit (ii) is cheaper but makes v4 dependent on a non-peer-reviewed preprint for a load-bearing design choice.

---

## §3. Integrated Gap Map

### 3.1 Literature matrix — the six positions that matter

| Position | Occupied by | Denominator of adequacy | Validation currency | Evidence level | Distance to v4 |
|---|---|---|---|---|---|
| Suite adequacy given an MR set | Fu et al. (2024) <!--ref:A3.1--><!--anchor:section:A3.1--> | MR set × source inputs | Correlation with fault detection | Preprint, criteria + experiment | ~1 construct on the metric axis |
| MR coverage as adequacy | Liu et al. (2024) MTcoverage <!--ref:A3.2--><!--anchor:section:A3.2--> | Degree to which given MRs are exercised | **Mutation testing** | Workshop-companion, 8 pp | Moderate |
| Diversity as a set-level number | Xie et al. (2024) MUT model <!--ref:A3.10--><!--anchor:section:A3.10--> | Pairwise MR dissimilarity | Not retrievable — abstract unavailable | Journal, **unread** | Closest structural competitor, **contents unknown** |
| Property-violating kill | Bartocci et al. (2023) <!--ref:C3.3--><!--anchor:section:C3.3--> | Mutants relevant to a specified STL property | More informative than regular mutation testing | ICST, industrial Simulink | ~2 constructs |
| Obligation-set completeness by program mutation | Knauth et al. (2009); Knüppel et al. (2021) <!--ref:B4.3-lineages--><!--anchor:section:§4.3--> | Program mutants the contracts fail to reject | Specification weakness | ICSTW / FormaliSE | Same measurement architecture, different obligation provenance |
| Structural-obligation denominator for MR adequacy | **arXiv:2605.17437 (self)** <!--ref:arxiv2605.17437--><!--anchor:quote:SMS%20is%20a%20backward%2Dcompatible%20adequacy%20metric%20for%20domain%2Dsemantic%20metamorphic%2Drelation%20sets-->; theory layer **arXiv:2606.08269 (self)** | Certified domain-semantic mutant pool | Cliff's delta versus syntactic pool; **threshold not met** | Preprints | **Zero — this is v4** |

### 3.2 Resolving the Theme A / Theme C tension

The tension is apparent, not real, and the resolution matters for how §1's verdict should be read.

Theme A's verdict is `PARTIAL`: MT adequacy criteria exist by name, but "no located work defines adequacy of an MR set against a denominator external to the MR set itself. Every criterion found is either internal … or empirical" <!--ref:A-verdict--><!--anchor:section:§4.2-->. Theme C's verdict is `DIRECT_PRIOR_ART` on the structural-denominator idea, with the occupant being the authors' own preprints <!--ref:C-verdict--><!--anchor:section:§4-->.

These describe **different populations**. Theme A searched the independent literature and found the external-obligation-denominator slot empty. Theme C searched prior art including self and found that slot filled by the authors. Both are true, and together they say something precise: *the position v4 wants is unoccupied in the independent literature and occupied by the authors themselves.*

Whether that is a problem depends entirely on the paper's identity. As a **separate** paper it is salami-slicing risk. As a **superseding version** it is the paper's own claim, restated with better method — which is what a new version of a preprint is for. Theme C said as much and handed the determination forward rather than deciding it <!--ref:C-handoff--><!--anchor:section:§7-->; the Phase 1 brief also corrected the C agent's harsher framing, noting line A was never submitted and the companion preprints are cited in the m1m8 `references.bib` <!--ref:phase1-brief--><!--anchor:section:§1.2-->.

**Consequence for §1:** the verdict `INCREMENT_INSUFFICIENT` should be read as "the increment-over-self is insufficient *and the increment-over-self is the wrong measure*." The correct measure is increment-over-independent-literature, and §3.4 identifies where that increment is non-empty.

### 3.3 The counter-pressure Theme B applies to the whole framing

Theme B is the theme most likely to be underweighted, and it is the one that constrains the motivating claim hardest. Its counter-evidence section establishes that syntactic mutation score is, on the field's own best evidence, the strongest available predictor of test-suite effectiveness: Just et al. (2014) found mutant detection correlated with real-fault detection across 357 real faults, more strongly than statement coverage, and surviving control for suite size; Zhang et al. (2024, TOSEM) found "mutation score, and subsuming mutation score are the best metrics to quantify test suite effectiveness"; Lu et al. (2026, TOSEM) found mutation score superior after regressing out the size confound; and Chen et al. (2020, ASE) contests the very confound analysis on which the construct-invalidity critique rests <!--ref:B-counter--><!--anchor:section:§5.1-->.

Two implications the plan has not absorbed.

**First, the misalignment premise must be localised, not general.** arXiv:2605.17437's own degeneration result — "SMS degenerates almost everywhere to MS in a characterised limit" <!--ref:arxiv2605.17437--><!--anchor:quote:SMS%20degenerates%20almost%20everywhere%20to%20MS%20in%20a%20characterised%20limit--> — says the two denominators agree almost everywhere. A construct-misalignment claim and an almost-everywhere-agreement theorem cannot both be stated at full strength in the same paper. The defensible form of the claim is confined to the classes the abstract reports as unreachable: Hyperparameter, Structural Injection, Trajectory Flip.

**Second, the field's chosen remedy is a competitor with a published number.** Wang et al. (2026, TOSEM) report LLM-generated mutants reaching 77.4% real-bug detection against 41.6% for rule-based techniques, and Tip et al. (2025, TSE) point the same way <!--ref:B-counter--><!--anchor:section:§5.6-->. A reviewer will ask how a structure-targeted mutant family compares. Note the awkwardness: arXiv:2605.17437's mutants *are* LLM-generated <!--ref:arxiv2605.17437--><!--anchor:quote:LLM%2Dgenerated%20mutants%20are%20compared%20against%20a%20default%2Dconfiguration%20cosmic%2Dray%20syntactic%20pool-->, so v4 is on the same side of that fence as the competitor and must say what the *structural targeting* adds over LLM generation alone. Its own cross-source ablation is relevant here: "Cross-source pooling under an identical prompt does not appreciably shift delta, indicating that LLM identity is not the lever within this design" <!--ref:arxiv2605.17437--><!--anchor:quote:Cross%2Dsource%20pooling%20under%20an%20identical%20prompt%20does%20not%20appreciably%20shift%20delta-->.

### 3.4 Where the genuinely unoccupied territory is

Four candidates, graded by how much of a paper each can carry.

**U1 — Validation by recovery of a pre-registered quality ordering. Strongest.** Every adequacy or MR-evaluation instrument located across all three themes validates itself against a fault or mutant population: Fu et al. by correlation with fault-detection effectiveness <!--ref:A3.1--><!--anchor:section:A3.1-->; Liu et al. explicitly "by means of mutation testing" <!--ref:A3.2--><!--anchor:section:A3.2-->; Chen et al. (2004) and Mayer & Guderlei (2006) by observed fault detection <!--ref:A3.5--><!--anchor:section:A3.5--> <!--ref:A3.6--><!--anchor:section:A3.6-->; Cao et al. (2013) by a two-step proxy chain through execution dissimilarity <!--ref:A3.7--><!--anchor:section:A3.7-->; Ayerdi et al. (2024) by making mutation score the search objective itself <!--ref:A4.4--><!--anchor:section:A4.4-->. **No located work validates an MR-adequacy measure by testing whether it recovers an independently pre-registered ordering over MR sets of known relative quality.** That is a different validation logic, not a different metric, and it is precisely v4's RQ2 — already flagged as decisive by both the RQ brief <!--ref:phase1-brief--><!--anchor:section:§5--> and the editorial assessment <!--ref:editorial-v4--><!--anchor:section:§3-->. The convergence of three independent readings on the same experiment is the strongest signal in this synthesis.

**U2 — Reachability characterisation across mutation configurations. Cheapest and most robust.** arXiv:2605.17437 establishes unreachability under *default first-order syntactic configurations* and states this evidence is independent of the contested effect-size question <!--ref:arxiv2605.17437--><!--anchor:quote:The%20first%2Dorder%20unreachability%20evidence%20is%20independent%20of%20the%20effect%2Dsize%20question-->. Nothing located maps which structural obligations become reachable under which configurations — higher-order operators, budget-matched pools, alternative tools, LLM generation at the Wang et al. bar. Theme B documents that the field's own self-criticism of mutation-based MR evaluation is that the mutant pool is *too small*, not that it is the wrong denominator (Jafari & Nadeem, 2024) <!--ref:A4.1--><!--anchor:section:A4.1-->; a reachability map answers that self-criticism on its own terms.

**U3 — Applicability domain D derived forwards from equation semantics. Narrow but clean.** Duque-Torres et al. attack MR applicability domain empirically, deriving constraints backwards from observed violations with a manual inspection step <!--ref:A3.12--><!--anchor:section:A3.12-->, and their follow-on characterises the input data space over which an MR holds <!--ref:A3.13--><!--anchor:section:A3.13-->. Deriving D forwards from the governing equation is unoccupied. It is one component, not a paper.

**U4 — Not unoccupied: κ and B.** Preservation mode (exact / approximate / asymptotic) is the vocabulary of geometric numerical integration <!--ref:C1.1--><!--anchor:section:C1.1-->; the primary/secondary conservation split that maps onto κ is Perot's <!--ref:C1.8--><!--anchor:section:C1.8-->; quantity-specific error budgeting is the dual-weighted-residual method <!--ref:C4.2--><!--anchor:section:C4.2-->; tolerance-masking in numerical mutation is Hook & Kelly's <!--ref:C3.8--><!--anchor:section:C3.8-->. These are borrowed instruments, correctly cited, and cannot be presented as contributions.

**Where v4 actually sits.** On the evidence assembled, v4's defensible position is a **measurement-validation paper**: the object of contribution is the validation logic for MR-adequacy instruments (construct, discriminant, criterion validity), the instrument under test is SMS — the authors' own, superseded, and cited as such — and verdict-independent certification is the protocol that makes the validation admissible rather than the contribution itself. Under that reading O moves from headline to method section, which is where §1 concludes it belongs, and the paper's novelty rests on U1 plus U2, both of which survive contact with the independent literature.

### 3.5 Evidence convergence map

```
Strong:     [==========]  Mutation score predicts suite fault-detection effectiveness
                          (Just 2014; Andrews 2005/2006; Chekam 2017; Zhang 2024 TOSEM;
                           Lu 2026 TOSEM; Chen 2020 ASE) — 7 sources, top venues
Strong:     [=========.]  MR quality is handled by ranking / selection / diversity /
                          composition rather than by sufficiency
                          (Chen 2004; Mayer 2006; Cao 2013; Srinivasan 2022; Qiu 2022;
                           Xie 2024) — 6 sources
Strong:     [=========.]  Structure preservation is a well-founded, checkable design
                          requirement in numerical analysis
                          (Hairer 2006; Marsden & West 2001; Arnold 2006; Christiansen 2011;
                           Perot 2011; Harten 1983) — 6+ sources, Acta Numerica class
Moderate:   [======....]  MT-specific adequacy criteria exist
                          (Fu 2024 preprint; Liu 2024 QRS-C; Huang 2022 IAECST — self)
                          — 3 sources, none heavyweight, one self-cited
Moderate:   [======....]  Equation-derived MRs already exist
                          (Yan & Zhu 2025 STVR; Luu 2022 MET; Chen/Feng/Tse 2002) — 3 sources
Moderate:   [=====.....]  Verdict-independent certification instruments exist per-property
                          (Roache 1994; Becker & Rannacher 2001; Hicken & Zingg 2011;
                           Ugolotti 2018; Haworth 1993; Limache 2008) — 6 sources,
                          but never assembled as an adequacy-admission protocol
Emerging:   [===.......]  Property-violating kill as a mutation criterion
                          (Bartocci 2023 ICST; Ding 2019 QRS) — 2 sources
Emerging:   [===.......]  Structural-obligation denominator for MR adequacy
                          (arXiv:2605.17437; arXiv:2606.08269) — 2 sources, BOTH SELF,
                          both preprints, headline threshold not met
Gap:        [..........]  Adequacy instrument validated by recovering a pre-registered
                          MR-set quality ordering — 0 sources located (U1)
Gap:        [..........]  Reachability map of structural obligations across mutation
                          configurations — 0 sources located (U2)
Gap:        [..........]  Demonstrated numerical consequence of admitting uncertified
                          mutants into an adequacy denominator — 0 sources located
```

---

## §4. Terminology Collision

### 4.1 The facts

"Semantic mutation testing" is an established named technique. Clark, Dan & Hierons introduced it at ICSTW 2010, pp. 100–109 <!--ref:B3-1--><!--anchor:page:100-109-->, developed it in *Science of Computer Programming* 78(4), 345–363 <!--ref:B3-2--><!--anchor:page:345-363-->, and realised it in SMT-C at ICST 2012, pp. 654–663 <!--ref:B3-3--><!--anchor:page:654-663-->. Its definition, quoted by Theme B from a successor paper whose abstract is verbatim retrievable:

> "Recently, a new approach known as semantic mutation testing has been proposed. **This approach mutates the semantics of the language in which the program is written. The mutants generated misunderstandings of the language which are different classes of faults.**"

(Ghani, 2013, *JSEA* 6(10), abstract) <!--ref:B3-5--><!--anchor:quote:This%20approach%20mutates%20the%20semantics%20of%20the%20language%20in%20which%20the%20program%20is%20written-->

The mutated object is the interpretation function; the program text is held fixed; operators are indexed by semantic variation points <!--ref:B-memo--><!--anchor:section:§4.1-->. The authors' "semantic mutation" holds the language fixed and mutates the program text so that it violates a derived mathematical obligation — the exact inverse assignment of what is fixed and what varies <!--ref:B-memo--><!--anchor:section:§4.2-->.

### 4.2 How damaging

**Not a novelty threat. A credibility and findability threat, and a serious one.** Three aggravating factors, in order of severity.

1. **The two lines are not in disjoint domains.** Dan & Hierons applied semantic mutation to floating-point comparison semantics — numerical code, by the technique's originators, at ICST 2012, pp. 290–299 <!--ref:B3-4--><!--anchor:page:290-299-->. Theme B calls it "the single closest prior art in the entire theme" <!--ref:B3-4--><!--anchor:section:B3-4-->. So a reviewer can truthfully say semantic mutation of numerical code already exists, under that name, by those authors. Any v4 sentence of the form "we introduce semantic mutation for numerical programs" is falsified by a single citation.
2. **The audience is exactly the population that knows this.** TOSEM's mutation-testing reviewer pool is the community that produced the Clark/Dan/Hierons line; John Clark also co-authors the nuclear-industry mutation study Theme B lists as counter-evidence <!--ref:B4-4--><!--anchor:section:B4-4-->. This is not an obscure collision.
3. **It is already in the public record twice, under the authors' names.** arXiv:2605.17437's title uses "semantic mutation metric" and arXiv:2606.08269's title uses "Semantic-Mutation Fault Models" <!--ref:arxiv2606.08269--><!--anchor:quote:Minimum%20Complete%20MR%20Subsets%20under%20Semantic%2DMutation%20Fault%20Models-->. Renaming in v4 alone creates a terminology split across a pair of related preprints. This is the argument for acting **now**, at supersede time, rather than later: the cost only rises.

One mitigating factor: the collision is **not** a prior-art bar, because the object mutated genuinely differs, and Theme B's memo tabulates the difference on seven dimensions without judgement of merit <!--ref:B-memo--><!--anchor:section:§4.2-->.

One honest limit that must gate the wording: **Theme B could not obtain the full text of Clark, Dan & Hierons (2010) or (2013), or of Dan & Hierons (2012a, 2012b)** across four retrieval routes, and its definitions rest on successor-paper abstracts plus verified titles and venues <!--ref:B-retrieval-limit--><!--anchor:section:§4.4-->. **Pending a full-text read of SCP 78(4), 345–363, no v4 sentence may assert what those papers do or do not contain at section granularity.**

### 4.3 Recommendation: both rename and disambiguate

A rename alone leaves reviewers who know the earlier arXiv titles confused; a disambiguation alone leaves the title misleading in search results. Do both.

**Rename.** Remove "semantic mutation" from the title, abstract and keywords. Keep **SPTM (Structure-Preservation-Targeted Mutation)**, which already names the target rather than asserting semanticness, and which the v4 plan already uses <!--ref:v4-plan--><!--anchor:section:§2.2-->. For the metric, the cheapest consistent option is to rename in step with the tuple — for example *structure-lineage-relative MR adequacy*, already the plan's SLRMA <!--ref:v4-plan--><!--anchor:section:§2.3--> — and to retain "SMS" only inside the lineage note that records what the superseded version called it.

**Disambiguate.** Exact wording, to sit as the last subsection of Related Work, before the gap statement:

> **Terminology: two distinct senses of "semantic mutation."** The phrase *semantic mutation testing* already names an established technique in which the semantics of the language in which a program is written are mutated while the program text is held fixed, so that the generated mutants represent misunderstandings of language or platform semantics rather than incorrect edits (Clark, Dan & Hierons, 2010, 2013). That technique has been realised for C (Dan & Hierons, 2012a) and applied to the semantics of floating-point comparison (Dan & Hierons, 2012b), and it has been instantiated for UML state machines, concurrency, agent platforms and language interpreters. The present paper does something different, and the difference is an exchange of what is held fixed. Here the language semantics are fixed and the *program text* is mutated, so that the mutated program provably fails a structure-preservation requirement derived from the governing equation. To keep the two senses apart we use **structure-preservation-targeted mutation** throughout and reserve *semantic mutation testing* for the Clark, Dan and Hierons sense. An earlier version of this work used "semantic mutation" for the present sense; that usage is superseded here.
>
> Two further lineages mutate a program against a declared obligation and must also be separated. Specification mutation (Budd & Gopal, 1985) mutates the specification and judges test data by its ability to distinguish specification from specification-mutant, which is the inverse direction. Mutation analysis for specification and contract completeness (Knauth et al., 2009; Knüppel et al., 2021) mutates the program and measures which mutants the declared contracts fail to reject, which is the same measurement architecture used here with a different obligation provenance: a contract written by a developer, rather than a structural property implied by a governing equation and certified independently of any test verdict.

The second paragraph is not optional garnish. Theme B's memo states the distinction must be drawn against three lineages, not one <!--ref:B4.3-lineages--><!--anchor:section:§4.3-->, and the contract-completeness lineage is the closer neighbour of the two.

---

## §5. Evidence Conflicts

### 5.1 Contradictions and resolutions

| # | Claim A | Claim B | Resolution |
|---|---|---|---|
| X1 | v4 plan: syntactic mutation's code-edit denominator is construct-misaligned with the equation-level semantics MRs carry <!--ref:v4-plan--><!--anchor:section:§1--> | arXiv:2605.17437: "SMS degenerates almost everywhere to MS in a characterised limit" <!--ref:arxiv2605.17437--><!--anchor:quote:SMS%20degenerates%20almost%20everywhere%20to%20MS%20in%20a%20characterised%20limit--> | **Reconcilable, at a cost.** Almost-everywhere agreement bounds the misalignment to a small set. The claim must be localised to the classes reported unreachable (Hyperparameter, Structural Injection, Trajectory Flip) and cannot be stated as a general misalignment. The degeneration theorem is the authors' own strongest limit on their own motivation |
| X2 | v4 premise: MR-set adequacy needs measuring | Liu, Kuo, Towey & Chen (2014, TSE): a small number of diverse, even ad hoc, MRs had fault-detection capability similar to a test oracle <!--ref:A2.6--><!--anchor:section:A2.6--> | **Reconcilable.** The equivalence is a fault-detection-rate equivalence over a specific seeded-fault population on specific programs, not a completeness claim; it silently makes the fault population the denominator, which is the move under critique. Theme A flags this as the paper to engage head-on rather than in passing <!--ref:A2.6--><!--anchor:section:A2.6--> |
| X3 | v4 premise: mutation score is the wrong instrument for MR-set adequacy | Zhang et al. (2024, TOSEM) and Lu et al. (2026, TOSEM): mutation score is the best available metric for test-suite effectiveness; Chen et al. (2020, ASE) contests the size-confound critique <!--ref:B-counter--><!--anchor:section:§5.1--> | **Reconcilable by construct separation.** These results establish mutation score as a predictor of *suite fault-detection effectiveness*, a different construct from *MR-set coverage of equation-level obligations*. But the separation must be argued explicitly, and Papadakis et al. (2018) cannot be cited without engaging Chen et al. (2020) |
| X4 | Liu et al. (2024): proposes an MT adequacy criterion, MTcoverage | Same paper validates that criterion "by means of mutation testing" <!--ref:A3.2--><!--anchor:section:A3.2--> | **Not a conflict to resolve — an exhibit to use.** It simultaneously defeats "no MT adequacy criterion exists" and supplies the cleanest single illustration that adequacy work in MT falls back on the syntactic-mutant denominator. Both facts must be reported together |
| X5 | STATE.md §3 and the editorial assessment list conservation (source–sink–boundary balance) as the first recommended certifier <!--ref:STATE-md--><!--anchor:section:§3--> | Haworth et al. (1993): the imbalance is informative only for quantities not conserved at cell level by construction; where the scheme conserves exactly it is identically zero regardless of correctness <!--ref:C4.6--><!--anchor:section:C4.6--> | **Reconcilable by design change, not by wording.** The balance certifier is admissible only for *secondary* conserved quantities in Perot's sense <!--ref:C1.8--><!--anchor:section:C1.8-->. It is structurally silent on primary-conservation ESPRs. Load-bearing consequence: the feasible lineage G is defined by which properties are *certifiable*, not by which are *derivable* |
| X6 | SPTM premise: a certified structural violation is a seeded fault | Limache et al. (2008): objectivity failure in Navier–Stokes formulations is a formulation-level defect, not a coding error <!--ref:C4.7--><!--anchor:section:C4.7--> | **Reconcilable by scoping, and it must be stated.** SPTM injects into a program pre-certified to satisfy the property, so post-injection violation is attributable to the injection. Without that pre-certification step written into the protocol, a symmetry certifier can fire on a defect the mutation did not create |
| X7 | Editorial assessment proposes reusing the 5.14% AST overlap and δ = 0.314 as pilot evidence <!--ref:editorial-v4--><!--anchor:section:可利用的内容--> | STATE.md §4: the exact binomial interval is `UNMEASURED_INTERVAL_AUTHORITY_INCOMPLETE` because the frozen analysis specification fixed neither confidence level nor method, and post-hoc computation is forbidden <!--ref:STATE-md--><!--anchor:section:§4--> | **Reconcilable with a restriction.** The development-set numbers may be reported as descriptives with no inferential statistics attached. Any confidence interval computed now violates the freeze |
| X8 | Terminology: the authors' "semantic mutation" | Dan & Hierons (2012b): semantic mutation analysis of floating-point comparison — same name, numerical code, different object <!--ref:B3-4--><!--anchor:page:290-299--> | **Resolved by §4**: rename plus a two-paragraph disambiguation covering three lineages |
| X9 | v4 plan lists 可逆 (reversibility) as an ESPR property φ <!--ref:v4-plan--><!--anchor:section:§2.1--> | STATE.md §3 lists 可逆：往返残差 (round-trip residual) as a certifier <!--ref:STATE-md--><!--anchor:section:§3--> | **Irreconcilable as written.** The same object cannot be both the obligation under test and the independent instrument that certifies its violation, and a round-trip residual satisfies the standard MR definition <!--ref:A1.4--><!--anchor:quote:necessary%20properties%20of%20the%20target%20function%20or%20algorithm%20in%20relation%20to%20multiple%20inputs%20and%20their%20expected%20outputs-->. One of the two roles must be dropped. Same argument applies to convergence order versus the refinement MR family <!--ref:A2.5--><!--anchor:section:A2.5--> |

### 5.2 Unresolvable on present evidence

**Y1 — What Fu et al. (2024) actually take as their denominator. HIGHEST VALUE UNRESOLVED ITEM.** Theme A's §4.1 gap 2 asserts that Fu et al.'s "criterion's requirements are generated *from the MRs the tester already has*", so an MR set omitting a whole obligation class can still measure 100% adequate <!--ref:A-verdict--><!--anchor:section:§4.1-->. But the abstract Theme A itself quotes says the criteria specify "testing requirements from the perspective of necessary properties satisfied by the SUT" <!--ref:A3.1--><!--anchor:quote:a%20new%20set%20of%20criteria%20that%20specifies%20testing%20requirements%20from%20the%20perspective%20of%20necessary%20properties%20satisfied%20by%20the%20SUT-->, which reads as a denominator drawn from the SUT rather than from the MR set. Theme A also records that it read no full texts <!--ref:A-limits--><!--anchor:section:§7-->. So v4's entire remaining positioning rests on an abstract-level inference that the abstract arguably contradicts. **Resolving evidence: the full text of arXiv:2412.20692, specifically the criteria definition.** If the requirements are generated independently of the MR set, Theme A's verdict moves toward `EXISTS`, the "no external-obligation denominator" claim must be deleted, and §1's verdict hardens.

**Y2 — What Xie et al. (2024) MUT model measures.** It is the only located instrument that puts a number on an MR *set* and is therefore the closest structural competitor, and its abstract was unavailable through both Crossref and OpenAlex <!--ref:A3.10--><!--anchor:section:A3.10-->. Theme A marks it a priority read; the Phase 2b consolidation repeats that <!--ref:phase2b--><!--anchor:section:§3-->. **Resolving evidence: the full text of *Software Quality Journal* 32(4), 1413–1455.**

**Y3 — Whether the three-layer attribution classifier consumes MR verdicts.** As set out in §1.2(d). **Resolving evidence: the full text of arXiv:2605.17437, per-layer input specification.** Until then the size of the O increment is indeterminate, and this document's estimate of it is conditional.

**Y4 — Whether the near-neighbour enumeration is complete.** `search_dblp` and `search_semantic` were dead for all three Phase 2 agents and independently reproduced dead by the consolidator, including on a minimal control query <!--ref:phase2b--><!--anchor:section:§4-->. Theme A records that two of five adversarial free-text sweeps failed for tool reasons, that the three decisive hits came from Undermind discovery plus DOI resolution rather than adversarial querying, and that the one clean adversarial query immediately produced two unseen near-neighbours — so it judges the enumeration probably incomplete <!--ref:A-limits--><!--anchor:section:§7-->. **The direction of all three verdicts is safe; the enumerations behind them are not exhaustive, and §1's verdict could only get worse, never better, with better retrieval.**

**Y5 — Papadakis et al. (2018) versus Chen et al. (2020) on the test-suite-size confound.** A live methodological dispute in the mutation-testing literature that this synthesis cannot adjudicate <!--ref:B-counter--><!--anchor:section:§5.2-->. v4 must cite both and take no side it cannot defend.

### 5.3 Over-defensive claim audit (project rule §10.1)

Both directions, as required.

| Item | Direction | Assessment |
|---|---|---|
| STATE.md §1.1 constraint 2 — novelty only on O and verdict-independence | **Claim shrinkage** | **Fails.** Narrows the claim to pre-empt a self-prior-art accusation that constraint 4's supersede decision already dissolves, not because evidence showed the larger claim untestable. Recommend recall to the SMS-level claim measured against the independent literature (§1.5) |
| FINER Novel downgraded 4 → 3 → 2 | Claim shrinkage | **Passes as validity repair.** Driven by located prior art, with the downgrade condition written in advance and then triggered <!--ref:phase1-brief--><!--anchor:section:§4--> |
| Motivating claim narrowed from "no trustworthy measurement" to "no external-obligation denominator" | Claim shrinkage | **Passes**, conditional on Y1. It was a falsified claim, correctly retracted <!--ref:A-verdict--><!--anchor:section:§4.4--> |
| Localising the misalignment claim to the unreachable classes (X1) | Claim shrinkage | **Passes as validity repair.** Forced by the authors' own degeneration theorem, not by risk aversion |
| Reporting development-set numbers descriptively only (X7) | Claim shrinkage | **Passes as validity repair.** Required by the freeze protocol |
| RQ2 as the decisive experiment with a pre-registered failure criterion | **Risk-taking** | **Correct and must be preserved.** This is the paper's willingness to fail. Any drift toward reporting RQ2 descriptively, or dropping the pre-registered ordering, would be the over-defensive move to watch for |
| "Structural violations are unreachable by syntactic edits" as a point claim | Risk-taking | **Correct.** It is a falsifiable point prediction, already published, and independent of the contested effect size |
| Claim C6 (semantic mutation universally superior) permanently blocked | Claim shrinkage | **Passes.** Out of scope by design, not evasion <!--ref:phase1-brief--><!--anchor:section:§6--> |

### 5.4 Cross-Paper Tension Inventory (#262)

```yaml
cross_paper_tensions:
  - pair_id: CP-001
    paper_a: "arxiv2605.17437"
    paper_b: "C3.3"
    candidate_basis: "shared construct/outcome/measure"
    overlap_topic: "whether a mutant should be certified as property-violating independently of the test suite's verdict"
    a_finding: "Domain-semantic mutants are attributed through a three-layer classifier separating true semantic faults from tolerance, OOD, statistical and artefact categories"
    a_evidence_pointer: "arXiv:2605.17437v2 abstract, Method sentence (primary text fetched this session)"
    b_finding: "A mutant is relevant only if it can affect satisfaction of a specified property and meaningfully killed only if it causes that property's violation"
    b_evidence_pointer: "Theme C bibliography entry C3.3, Key findings (abstract-verified via arXiv:2301.13615)"
    pair_assessment: "conditional_difference"
    resolution_status: "resolved_in_synthesis"
    resolution_pointer: "Synthesis Report > §1.3 R3"
    scholar_confirmation: "pending"

  - pair_id: CP-002
    paper_a: "arxiv2605.17437"
    paper_b: "A3.1"
    candidate_basis: "shared RQ subtopic"
    overlap_topic: "what serves as the denominator when measuring metamorphic-testing adequacy"
    a_finding: "A certified domain-semantic mutant pool serves as the adequacy denominator for MR sets"
    a_evidence_pointer: "arXiv:2605.17437v2 abstract, Conclusion sentence"
    b_finding: "Testing requirements are specified from the perspective of necessary properties satisfied by the SUT, measured over both MRs and source inputs"
    b_evidence_pointer: "Theme A bibliography entry A3.1, Key findings (2)–(3), abstract-verified"
    pair_assessment: "conditional_difference"
    resolution_status: "flagged_unresolved"
    scholar_confirmation: "pending"

  - pair_id: CP-003
    paper_a: "A3.2"
    paper_b: "arxiv2605.17437"
    candidate_basis: "opposite finding direction"
    overlap_topic: "whether syntactic mutation is a suitable instrument for validating metamorphic-testing adequacy"
    a_finding: "The effectiveness of the MTcoverage adequacy criterion was demonstrated by means of mutation testing"
    a_evidence_pointer: "Theme A bibliography entry A3.2, Key findings (3), abstract-verified"
    b_finding: "Classical Mutation Score operates on syntactic AST mutations and misses domain semantics"
    b_evidence_pointer: "arXiv:2605.17437v2 abstract, Context sentence"
    pair_assessment: "contradiction"
    resolution_status: "resolved_in_synthesis"
    resolution_pointer: "Synthesis Report > §5.1 X4"
    scholar_confirmation: "pending"

  - pair_id: CP-004
    paper_a: "B-counter-Zhang2024-Lu2026"
    paper_b: "arxiv2605.17437"
    candidate_basis: "opposite finding direction"
    overlap_topic: "whether mutation score is a valid measure of test-suite or oracle quality"
    a_finding: "Mutation score and subsuming mutation score are the best metrics for quantifying test-suite effectiveness, and remain superior after the size confound is regressed out"
    a_evidence_pointer: "Theme B counter-evidence §5.1, items 4 and 5 (TOSEM records, verbatim-quoted)"
    b_finding: "Classical Mutation Score misses domain semantics, motivating a domain-semantic replacement"
    b_evidence_pointer: "arXiv:2605.17437v2 abstract, Context sentence"
    pair_assessment: "conditional_difference"
    resolution_status: "resolved_in_synthesis"
    resolution_pointer: "Synthesis Report > §5.1 X3"
    scholar_confirmation: "pending"

  - pair_id: CP-005
    paper_a: "B-Papadakis2018"
    paper_b: "B-Chen2020"
    candidate_basis: "opposite finding direction"
    overlap_topic: "whether test-suite size confounds the mutation-score / fault-detection relationship"
    a_finding: "The mutation-score to fault-detection relationship weakens substantially once suite size is controlled"
    a_evidence_pointer: "Theme B counter-evidence §5.2, framing of the contested result"
    b_finding: "Test-set size is neither a confounding variable nor an independent variable that should be experimentally manipulated"
    b_evidence_pointer: "Theme B counter-evidence §5.2, item 8"
    pair_assessment: "contradiction"
    resolution_status: "flagged_unresolved"
    scholar_confirmation: "pending"

  - pair_id: CP-006
    paper_a: "B3-4"
    paper_b: "arxiv2605.17437"
    candidate_basis: "shared construct/outcome/measure"
    overlap_topic: "what the phrase 'semantic mutation' denotes when applied to numerical code"
    a_finding: "Semantic mutation applied to the semantics of floating-point comparison, holding the program text fixed"
    a_evidence_pointer: "Theme B bibliography entry B3-4 and disambiguation memo §4.1 table"
    b_finding: "Semantic mutation denotes domain-level mutation of the program's mathematical meaning, holding the language semantics fixed"
    b_evidence_pointer: "arXiv:2605.17437v2 abstract, Objective sentence; Theme B memo §4.2 table"
    pair_assessment: "conditional_difference"
    resolution_status: "resolved_in_synthesis"
    resolution_pointer: "Synthesis Report > §4.3"
    scholar_confirmation: "pending"

  - pair_id: CP-007
    paper_a: "A2.6"
    paper_b: "arxiv2605.17437"
    candidate_basis: "opposite finding direction"
    overlap_topic: "whether a small ad hoc MR set is already sufficient"
    a_finding: "A small number of diverse MRs, even ones identified ad hoc, had fault-detection capability similar to a test oracle"
    a_evidence_pointer: "Theme A bibliography entry A2.6, Key findings (2), abstract-verified"
    b_finding: "MR-set adequacy requires a domain-semantic denominator because classical measures miss domain semantics"
    b_evidence_pointer: "arXiv:2605.17437v2 abstract, Context and Conclusion sentences"
    pair_assessment: "conditional_difference"
    resolution_status: "resolved_in_synthesis"
    resolution_pointer: "Synthesis Report > §5.1 X2"
    scholar_confirmation: "pending"

  - pair_id: CP-008
    paper_a: "C4.6"
    paper_b: "C1.8"
    candidate_basis: "shared construct/outcome/measure"
    overlap_topic: "when a discrete conservation diagnostic carries information about implementation correctness"
    a_finding: "Global balance imbalance permits direct assessment of numerical accuracy from a single run on a single mesh, but only for quantities not conserved at cell level by construction"
    a_evidence_pointer: "Theme C bibliography entry C4.6, Key findings (3), abstract-verified"
    b_finding: "Primary conservation of the unknowns often follows from global conservation, whereas secondary conservation of derived quantities is much harder to achieve"
    b_evidence_pointer: "Theme C bibliography entry C1.8, Key findings (2)–(3), abstract-verified"
    pair_assessment: "no_material_conflict"
    resolution_status: "not_applicable"
    scholar_confirmation: "pending"

  - pair_id: CP-009
    paper_a: "C3.6"
    paper_b: "arxiv2605.17437"
    candidate_basis: "shared RQ subtopic"
    overlap_topic: "deriving testing artefacts from the mathematics of the governing equations"
    a_finding: "Metamorphic relations are formally derived from the numerical models of differential equations built during development"
    a_evidence_pointer: "Theme C bibliography entry C3.6, Key findings (2), abstract-verified"
    b_finding: "Domain-semantic mutation operators, including Conservation Erosion and Structural Injection, form the adequacy denominator"
    b_evidence_pointer: "arXiv:2605.17437v2 abstract, Objective sentence"
    pair_assessment: "no_material_conflict"
    resolution_status: "not_applicable"
    scholar_confirmation: "pending"

  - pair_id: CP-010
    paper_a: "B-Wang2026"
    paper_b: "arxiv2605.17437"
    candidate_basis: "shared construct/outcome/measure"
    overlap_topic: "whether LLM-generated mutants outperform rule-based mutant generation"
    a_finding: "LLM-generated mutants reach 77.4% real-bug detection against 41.6% for rule-based techniques"
    a_evidence_pointer: "Theme B counter-evidence §5.6, item 19 (TOSEM record)"
    b_finding: "LLM-generated domain-semantic mutants versus a default cosmic-ray syntactic pool yield a medium effect, with the pre-registered large-effect threshold not met, and LLM identity is not the lever"
    b_evidence_pointer: "arXiv:2605.17437v2 abstract, Results sentences"
    pair_assessment: "conditional_difference"
    resolution_status: "resolved_in_synthesis"
    resolution_pointer: "Synthesis Report > §3.3"
    scholar_confirmation: "pending"

  - pair_id: CP-011
    paper_a: "arxiv2605.17437"
    paper_b: "arxiv2606.08269"
    candidate_basis: "bibliographic coupling"
    overlap_topic: "the relationship between an adequacy score and the sufficiency of an MR set"
    a_finding: "SMS is a backward-compatible adequacy metric for domain-semantic MR sets"
    a_evidence_pointer: "arXiv:2605.17437v2 abstract, Conclusion sentence"
    b_finding: "An SMS-rank upper bound exists that is explicitly not a lower bound and not a tight predictor of minimum complete MR-subset size"
    b_evidence_pointer: "arXiv:2606.08269v1 abstract, central-result sentence"
    pair_assessment: "no_material_conflict"
    resolution_status: "not_applicable"
    scholar_confirmation: "pending"
```

**Coverage Note.** 139 bibliography entries across the three Phase 2 deliverables (Theme A = 44, Theme B = 57, Theme C = 38, with six recorded cross-theme duplicates) plus two preprint abstracts fetched as primary text in this session; 11 candidate pairs considered, on the candidate-edge signals *shared RQ subtopic*, *shared construct / outcome / measure*, *opposite finding direction*, and *bibliographic coupling*. This is a **scoped advisory scan, not complete pairwise contradiction detection** — cross-neighbourhood pairs not surfaced here may exist and are not claimed absent, and Phase 2's own limitation notes make that likelier than usual, since `search_dblp` and `search_semantic` were non-functional for all three bibliography agents and Theme A judges its near-neighbour enumeration probably incomplete. Bibliographic coupling was used as an inclusion signal only, never to exclude a pair. The scholar confirms each `resolution_pointer` and may flag additional cross-pairs.

---

## §6. What Must Be True for v4 to Proceed

Ordered by dependency. Each precondition is falsifiable and carries exactly one owner class.

| # | Precondition | Falsification test | Owner class |
|---|---|---|---|
| **P1** | The paper's identity is settled: either (a) the superseding version of arXiv:2605.17437, in which case constraint 2 is lifted and the novelty unit is the metric plus its validation measured against the independent literature; or (b) a separate paper, in which case §1's `INCREMENT_INSUFFICIENT` stands and the project needs a different framing | STATE.md §1.1 records the choice, constraint 2 is explicitly lifted or explicitly retained with a defence, and the paper's contribution list matches the choice | **author decision** |
| **P2** | Fu et al. (2024) do **not** generate testing requirements independently of the MR set | Read arXiv:2412.20692's criteria definition. If the requirements are SUT-derived and MR-set-independent, delete the "no external-obligation denominator" claim and re-grade Theme A | **full-text read** |
| **P3** | The three-layer attribution classifier of arXiv:2605.17437 consumes at least one MR verdict or kill outcome | Read the classifier's per-layer input specification. If no layer consumes one, O is a formalisation of existing practice and cannot be the headline under P1(b) | **full-text read** |
| **P4** | Xie et al. (2024) MUT model measures diversity and not adequacy | Read *Software Quality Journal* 32(4), 1413–1455. If it measures obligation coverage, it is a direct competitor, not an adjacent one | **full-text read** |
| **P5** | The disambiguation rests on the primary Clark / Dan / Hierons text, not on successor abstracts | Read SCP 78(4), 345–363 and ICST 2012, 290–299. The §4.3 subsection then carries section-level locators | **full-text read** |
| **P6** | Terminology is fixed before drafting | Grep the draft: "semantic mutation" appears only inside the disambiguation subsection and the supersede lineage note; zero hits elsewhere in title, abstract, keywords or body | **settled now** |
| **P7** | Every theory paragraph passes the §2.3 citation-removal test | An auditor deletes each arXiv:2606.08269 citation in turn; each affected paragraph must become unsupported rather than remain self-derived | **settled now** |
| **P8** | The macro-average over G is justified on a ground that is not abstraction-safety, or is cited to arXiv:2606.08269 without derivation | The justification paragraph passes P7, and the aggregation choice plus its sensitivity analysis are pre-registered | **author decision** |
| **P9** | Every reversibility-type and refinement-type instrument is assigned to exactly one role — obligation under test, or certifier — never both | For each certifier, print its inputs and cross-check against the input set of every MR in R. Overlap of one observable disqualifies it as verdict-independent | **settled now** |
| **P10** | The structural lineage G is built from **certifiable**, not merely derivable, ESPRs, with an applicability matrix that marks the silence cases | Every node g in G names a certifier whose documented applicability domain covers the PUTs; the matrix records Haworth's zero-imbalance silence and Limache's formulation-defect scope; at least three certifiers share no observable | **new experiment** |
| **P11** | A PUT population exists that exposes discrete operators or adjoints, so the two clean certifiers are applicable at all | Name the solvers. If the population remains single-output float-to-float, the commutator and dot-product certifiers are inapplicable and P10 cannot be satisfied | **new experiment** |
| **P12** | Verdict-independent admission demonstrably changes the measurement | Recompute adequacy under certified-only admission on the same programs; pre-register direction and minimum detectable difference. Null result ⇒ demote O to threats and fall back to P1(a) | **new experiment** |
| **P13** | RQ2 recovers the pre-registered five-level MR-quality ordering on a frozen confirmation set, with program or solver as the statistical unit | Ordering and pass line fixed before data collection; failure to recover falsifies the instrument and must be reported as such | **new experiment** |
| **P14** | The RQ4 / P12-queue ineligibility determination exists in writing before any RQ3 claim references it | The one-page terminal-verdict document exists; STATE.md §4 currently records it as never landed, with 35 formal items against a pre-registered threshold of 60 | **author decision** |
| **P15** | A feasibility ceiling is fixed in advance: minimum viable number of programs, lineage nodes and certifiers that makes P13 completable, plus a stop rule | The numbers are written down before implementation starts, and the stop rule fires on schedule slip rather than being renegotiated. Prior record: Boost.Math stalled at ~70%, NumPy pilot reached 4 pairs, 14-subject survey produced 0 candidates | **author decision** |

**Ordering note.** P2 and P3 are cheap, are the two reads that can most change the verdict, and should be done before any of P8–P15 is funded. P11 is the precondition most likely to fail outright, and it gates P10, P12 and P13. If P11 fails, the O component cannot be demonstrated at all and P1(a) becomes the only viable path.

---

## §7. Alternative Framings (options for the author, not decisions)

Because §1 returns `INCREMENT_INSUFFICIENT`, three framings that the existing evidence base and infrastructure could actually support. **These are options. The choice is the author's.**

**Option A — Measurement-validation paper.** Contribution: the validation logic for MR-adequacy instruments — construct validity, discriminant validity against a pre-registered quality ordering, criterion validity against independently admitted real faults. The instrument under test is the authors' own metric, superseded and cited; verdict-independent certification is the admissibility protocol, in the method section. External novelty rests on U1: no located adequacy or MR-evaluation work validates by recovering a pre-registered ordering, all validating instead by fault-detection correlation. Requires P1(a), P13, and P10–P11 at reduced scope. Risk: if RQ2 fails, the paper becomes a negative result — publishable at TOSEM but a smaller paper, and the failure criterion must be pre-registered so that outcome stays honest.

**Option B — Reachability and complementarity paper.** Contribution: hardening and generalising the unreachability result, which arXiv:2605.17437 itself flags as independent of the contested effect size. Move from "unreachable under default first-order syntactic configurations" to a map of which structural obligations become reachable under which mutation configurations — higher-order operators, budget-matched pools, at least two independent tools, and LLM generation benchmarked against the 77.4% real-bug-detection figure in the TOSEM record. Cheapest of the three, reuses existing infrastructure, and engages the field's own remedy rather than sidestepping it. Risk: reviewers may read it as a finding about one mutation tool's default configuration, so more than one tool is mandatory.

**Option C — Certification-protocol and artefact paper.** Contribution: an executable, verdict-independent certification suite for structural-property violation in numerical code, assembled from the published instruments Theme C verified — global balance check, adjoint dot-product test, discrete operator commutator, observed order of accuracy — together with an applicability theory stating which certifier can certify which property class and where each is provably silent. This is the honest home for O: it stops pretending O is a new mechanism and makes the assembly plus the silence analysis the contribution. Requires P10 and P11. Risk: it is an artefact paper, and TOSEM will want it paired with a measurement result, which pushes it back toward Option A.

**Not recommended as framings, for the record:** any version whose headline is the ESPR five-tuple as a formalism (R5 closes that route), and any version whose headline is a positive effect-size claim for semantic over syntactic mutation (contradicted by the record being superseded, and by claim C6's permanent block).

---

## §8. Synthesis Limitations

1. **No full texts were read in this phase.** Every characterisation of a third-party work in this document derives from a Phase 2 annotation or from an abstract fetched in this session. Phase 2b records that twelve to twenty Theme C entries and eight Theme A entries have verified bibliographic data but scope-attributed rather than abstract-verified findings; §1 and §3 inherit that limitation wherever those entries are load-bearing.
2. **The verdict in §1 is conditional on P3.** The size of the O increment cannot be determined without reading the attribution classifier's input specification in arXiv:2605.17437. Every statement about it here is hedged accordingly, and the verdict would need revisiting if the classifier turns out to be verdict-dependent in a way the abstract does not reveal.
3. **§3's claim that U1 and U2 are unoccupied is bounded by Phase 2's retrieval failures.** Two of six prescribed verification tools were dead across all three agents, the adversarial Theme A sweep was weaker than designed, and the conservation-law query was heavily contaminated by geological false positives. Both gaps could close with better retrieval. Neither could open wider.
4. **Only 11 candidate paper-pairs were assessed** out of a corpus of 139 entries. This is a scoped scan, not pairwise contradiction detection.
5. **This agent performed no audit.** No verification step was simulated and no external review was run. The two arXiv abstracts were fetched directly; nothing else in this document was independently re-verified against a source outside the Phase 1 and Phase 2 artefacts.
6. **Downstream work is named, not executed.** Report compilation, editorial review, and any revision of the RQ brief's Novel score or Primary RQ wording remain with their respective phases.
