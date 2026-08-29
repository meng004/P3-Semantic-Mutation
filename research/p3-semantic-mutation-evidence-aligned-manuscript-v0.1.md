# Semantic versus Syntactic Mutants: A Single-Project Paired Pilot and a Prospective Applicability Census under Evidence-Bound Scope

[AUTHOR NAMES TO COMPLETE]

[AFFILIATIONS TO COMPLETE]

## Abstract

Construct distinctness between semantic mutants and first-order syntactic mutants cannot be read from a cell-level kill count. A paired comparison also has to keep repeated input measures inside pairs and keep project-level uncertainty visible as a separate cluster. This paper reports an evidence-bound empirical draft rather than a completed multi-project confirmation.

On one NumPy subject we froze four semantic/syntactic pairs and five contract-bound inputs per pair. After a disclosed infrastructure failure and a later clean controlled runtime, all sixty official cells passed. Semantic mutants were killed on four of four pairs. Syntactic baselines were killed on three of four pairs and survived on one. Exact equality of normalized patches was zero of four, and exact equality of mutant trees was zero of four. Those counts form a single-project paired-evidence pilot. They do not identify project-clustered uncertainty, and they do not complete the upgrade condition of the construct-distinctness claim, which remains blocked.

A later prospective applicability census on fourteen successor subjects, run under a frozen authority, produced no Stage II candidate for the current two-stage version. The paper therefore keeps RQ2, shrinks the answerable range to the NumPy pilot, the two exact-overlap measures, and the eligibility bound of the current prospective version, and does not treat cross-project construct distinctness as a delivered contribution.

<!-- Evidence: data/p3_v3/phase3/ordinal8-paired-evidence-rq2-handoff.json; artifact_sha256=a846ca2edded55ed48e0e9071a9aa218efc3dbcc9bd302a77ceb53bce9d822c5 -->
<!-- Evidence: data/p3_v3/phase3/ordinal8-exact-overlap-v1/exact-overlap.json; artifact_sha256=f4ca00694f4a3a0a63df151bf7cce96a66ae957d0d11d85ca056cb0e6b438071 -->

<!-- Internal Chinese companion abstract, not for submission -->

**Internal Chinese companion abstract, not for submission.** 语义变异是否构成不同于一阶句法基线的缺陷构造，取决于配对行为、结构重叠和项目级不确定性是否同时可识别。本文基于已冻结的主张范围，报告一份受证据约束的实证初稿。在一个 NumPy 主体的四个冻结配对上，语义变异体全部被杀死，句法基线为三杀一存活，规范化补丁与变异树的精确重叠均为零。该结果是单项目配对试验，不能外推为跨项目比较，也不能写成语义变异普遍优于句法变异。对十四个预注册后继主体的适用性普查，在冻结行为框架、槽位清单与谓词边界下没有冻结出新的配对位点，因而当前两阶段版本没有第二阶段候选。该普查只回答冻结权威下的适用性闭包问题，不证明这些程序没有目标构造，也不是工业适用率。跨项目构造可区分性与项目聚类不确定性仍不可识别，对应主张保持未解决。当前论文主动收缩主张范围，不再把跨项目确认作为主贡献，也不再沿本路线寻找第二个配对项目。

## Keywords

semantic mutation; syntactic mutation; paired-evidence pilot; construct distinctness; applicability census; metamorphic testing; evidence-bound scope

## 1. Introduction

Mutation testing asks whether a test suite can distinguish a program from systematically altered variants of that program [DeMillo et al. 1978; Jia and Harman 2011]. In the classical first-order setting, those variants are produced by local syntactic operators. The resulting mutants have been used as substitutes for some classes of real faults [Andrews et al. 2005; Just et al. 2014a], and industrial deployments have shown that the method can be run at large scale when equivalent and trivial mutants are controlled [Petrović and Ivanković 2018; Petrović et al. 2021]. The same literature also records persistent construct questions: operator sets differ across tools [Kintis et al. 2018], equivalent mutants remain costly [Delgado-Pérez and Chicano 2020], and a syntactic edit is not automatically a distinct fault construct [Papadakis et al. 2019].

Semantic mutation is one proposed response. Instead of treating an AST-local operator catalog as the defect universe, a semantic mutant is intended to change a declared behavioral contract: an invariant, a comparison obligation, a monotonicity claim, or another family of program-level meaning. Higher-order mutation already showed that combining first-order edits can produce faults that a default operator set does not express [Jia and Harman 2009]. Domain-specific and model-level mutation work makes a related move by targeting faults that matter in a chosen semantic space [Humbatova et al. 2021; Tip et al. 2024]. None of those lines, by itself, answers the narrower question that this paper can actually examine: on the same program version, is a frozen semantic mutant construct-distinct from a frozen first-order syntactic baseline?

That question is easy to over-answer. A kill on five inputs is not five independent experiments. Those five cells share one mutant, one baseline, and one contract. Counting them as five studies would treat repeated measures as a sample of projects. A four-pair contrast is not a project-level sampling distribution either. Four pairs on one library still occupy one cluster. A later empty applicability census is not a statement that industrial programs lack the target construct. It is an answer to a frozen eligibility question on a frozen successor list.

The current claim ledger therefore keeps the construct-distinctness claim, labeled C3, in the blocked state. The upgrade condition remains “RQ2 paired evidence and uncertainty accounting complete.” A single-project pilot cannot meet that condition. Completing four pairs does not complete uncertainty accounting. Completing a census that yields no Stage II candidate does not convert the missing cluster into a negative multi-project finding.

<!-- Evidence: research/evidence/p3_claim_ledger_v1.3.0.yml; C3 status=blocked; upgrade_condition unchanged -->

This draft is written after that contraction, not before it. The paper’s contributions are limited to five items that the official record already supports.

1. A frozen pairing protocol that treats semantic and first-order syntactic mutants as paired variants of the same subject, with contract-bound inputs as repeated measures and the pair as the primary reduction unit.
2. A NumPy single-project pilot with four frozen pairs.
3. Local exact-overlap observations on those pairs: normalized-patch equality and mutant-tree equality are both zero of four.
4. A prospective applicability census of fourteen successor subjects under a frozen Public Behavior Frame, slot inventory, applicability predicates, and first-applicable selection boundary.
5. An explicit statement of what remains unidentifiable: project-clustered uncertainty, multi-project construct distinctness, and any general superiority comparison.

<!-- Evidence: research/p3-semantic-mutation-core-claims-rqs-v1.3.0.md; Current-paper RQ2/C3 scope -->

The paper does not claim that semantic mutants are generally better testing objects than syntactic mutants. It does not treat eighteen manuscript program groups, or thirty-five verified defects, as eighteen runner-ready paired-evidence projects. It does not start another subject table for the present C3 route.

## 2. Background and Related Work

### 2.1 Mutation testing as a construct

The coupling hypothesis and the early mutation-testing literature treated syntactic mutants as a practical fault model for test-data selection [DeMillo et al. 1978; Ammann and Offutt 2008]. Later surveys organized decades of operator design, equivalent-mutant handling, and tool building [Jia and Harman 2011; Papadakis et al. 2019]. Empirical work then asked whether mutants stand in for real faults in experimental studies [Andrews et al. 2005; Just et al. 2014a] and whether popular tools agree on what those mutants are [Kintis et al. 2018].

Two conclusions from that body of work matter here. First, mutation is a construct with an operator-dependent denominator. Changing the operator set changes the claim. Second, a kill matrix is not self-interpreting. Tool disagreement, equivalent mutants, and trivial mutants all sit between a raw kill count and a scientific conclusion [Delgado-Pérez and Chicano 2020; Petrović et al. 2021].

### 2.2 Beyond first-order syntactic catalogs

Higher-order mutation showed that combinations of first-order edits can produce faults that a default first-order catalog does not systematically express [Jia and Harman 2009]. That result is a warning against treating one operator set as the defect universe. It is not, by itself, a semantic-mutation theory.

More recent work mutates programs, models, or tests according to a richer notion of meaning. DeepCrime targets faults observed in deep-learning systems [Humbatova et al. 2021]. LLMorpheus uses a language model to propose mutants outside a fixed operator list [Tip et al. 2024]. Those papers enlarge the mutation target. They do not freeze a paired semantic/syntactic comparison on one scientific-computing subject, and they do not identify project-clustered uncertainty for such a comparison.

Named semantic-mutation operators for conventional programs have also been proposed. [CITATION NEEDED: Clark, Dan, and Hierons semantic mutation testing and the SMT-C tool]. This draft does not reconstruct that lineage from memory. The present study uses a contract-bound pairing protocol already frozen in the P3 record; it does not claim to re-implement a prior semantic-mutation tool.

### 2.3 Metamorphic relations and oracles

Scientific-computing subjects often lack a complete output oracle. Metamorphic testing replaces that missing oracle with relations among executions. [CITATION NEEDED: original metamorphic-testing definition and the Chen, Cheung, and Yau formulation]. A later IST study uses metamorphic relations to validate a test-generation system rather than a scientific kernel [Zhang et al. 2021]. The present paper inherits that oracle problem as context. It does not evaluate an MR set’s adequacy, and it does not treat kill/survival under contract-bound inputs as an MR-adequacy score.

Data-level or relation-level mutation has been used to acquire or test metamorphic relations. [CITATION NEEDED: data-mutation-directed metamorphic-relation studies]. Those objects are not the paired program mutants reported here.

### 2.4 Equivalence, operator validity, and construct validity

Equivalent mutants remain a central threat: a variant that cannot be distinguished from the original is not a usable fault [Delgado-Pérez and Chicano 2020]. Industrial practice therefore spends substantial effort on productive-mutant filtering [Petrović and Ivanković 2018; Petrović et al. 2021]. In this draft, the original baseline surviving on every official input is a local oracle check, not a population equivalence rate.

Construct validity is the remaining gap. If semantic mutants are only first-order edits under another name, a “semantic versus syntactic” comparison is a labeling artifact. Exact patch overlap and exact mutant-tree overlap are two mechanical checks on that risk. They are still not testing-value evidence. They also have a denominator of four pairs in the present record.

[CITATION NEEDED: construct-validity guidance for software-engineering experiments].
[CITATION NEEDED: hierarchical or project-clustered inference for multi-project software studies].

The second missing citation is the reason this paper refuses to invent a confidence interval. The frozen analysis specification asked for exact binomial intervals on overlap counts but did not freeze the confidence level or the exact method. The official overlap artefact therefore reports 0/4 and 0/4 and leaves the interval unmeasured. That choice is a method clarification after the counts were known. It is not a license to compute a substitute interval in the manuscript.

<!-- Evidence: data/p3_v3/phase3/ordinal8-exact-overlap-v1/exact-overlap.json; exact_binomial_interval_status=UNMEASURED_INTERVAL_AUTHORITY_INCOMPLETE -->

## 3. Research Questions and Claim Boundaries

The living claim authority keeps four research questions [core-claims v1.3.0]. Only RQ2 is in scope for this draft, and only in a contracted form.

**RQ2 (frozen wording).** What semantic-contract, behavioral, patch-structure, and family-coverage differences exist between certified semantic mutants and frozen first-order syntactic mutants on the same program versions?

The current paper answers three local questions and no others.

1. On the ordinal-8 NumPy subject, what are the pair-level kill/survival outcomes for the four frozen semantic/syntactic pairs?
2. On those pairs, are the normalized patches exactly equal, and are the mutant trees exactly equal?
3. Under the frozen Stage I authority, does the current prospective version still have a nonempty Stage II candidate universe?

Family-coverage differences that were never measured stay unmeasured. Structural non-overlap is a construct-distinctness observation on these pairs, not a claim about testing value.

**C3 (blocked).** “Semantic mutants are construct-distinct from the chosen syntactic baseline.” Initial status: blocked. Upgrade condition: “RQ2 paired evidence and uncertainty accounting complete.” Current status: blocked. The condition is unmet because `n_projects = 1` and project-clustered uncertainty is unidentifiable.

<!-- Evidence: research/evidence/p3_claim_ledger_v1.3.0.yml; claim_id=C3_SEMANTIC_CONSTRUCT_DISTINCTNESS; n_projects=1 -->

The paper does not test C2 (certified mutants across scales and techniques), C4 (family-aware SMS), or C5 (P12 criterion validity). Those claims remain blocked under their own upgrade conditions. Permanent ceilings also remain in force: universal superiority, language-independent automatic generation, and full operational representativeness of the Profiling Workload are outside this paper.

What the paper does not answer:

- whether semantic mutation is generally better than syntactic mutation;
- whether the fourteen Stage I subjects lack the target construct;
- whether eighteen manuscript program groups can be treated as eighteen paired-evidence projects;
- whether the present NumPy contrast transports to other libraries, languages, or repositories.

## 4. Study Design

### 4.1 Subject and defect foundation

The manuscript-facing defect foundation is a set of 18 program/library groups and 35 `verified_full` defects, each recorded with a fixed version.
<!-- Evidence: docs/review_20260828/p3_claim_path_reprioritization_after_stage1_empty_candidates.md; paper label of 18 libraries; 35 verified_full; not an executable-interface count -->

Those totals describe a catalog, not a runner-ready paired-evidence sample. Eighteen groups are not eighteen projects on which the frozen pairing protocol has been executed. Thirty-five defects were not admitted into the ordinal-8 kill/survival table. This paper does not treat the P12 catalog as a runtime dependency, and it does not open P12 issues, patches, or mutation outcomes.

The executed paired-evidence project count is one: NumPy, ordinal 8.
<!-- Evidence: data/p3_v3/phase3/ordinal8-paired-evidence-rq2-handoff.json; analysis_units.n_projects=1 -->

A catalog such as Defects4J is designed so that each admitted fault has an executable buggy/fixed pair for controlled studies [Just et al. 2014b]. The 18/35 foundation in this paper is not used that way. It explains where the broader P3 program began. It does not enlarge the executed sample.

### 4.2 Frozen pairing design

Each official pair has three variants of the same subject: the original, a contract-bound semantic mutant, and a first-order syntactic baseline. Five frozen inputs are attached to the pair. Those inputs are repeated measures. They are not independent experimental units and not independent pairs.

The official analysis units on the completed subject are: one project, one repository, one subject, two sites, four pairs, four semantic mutants, four syntactic baselines, and five frozen inputs per pair. The record also states, explicitly, that input cells are not independent experimental units and not independent pairs. The primary descriptive unit is the frozen semantic/syntactic pair.

<!-- Evidence: data/p3_v3/phase3/ordinal8-paired-evidence-rq2-handoff.json; analysis_units.n_projects=1; n_pairs=4; n_sites=2; frozen_inputs_per_pair=5 -->

A pair-level reducer is KILL when the variant is killed on the pair’s official cells under the frozen reduction rule, and SURVIVE otherwise. Project is the cluster that would be required for cross-project uncertainty. With one project, that cluster is unidentifiable. Cell-level counts are reported only as repeated-measure detail inside the pair.

The represented contract families on the completed NumPy pairs are INV and CMP. Represented mechanisms are SI and TF. On that same subject, MONO produced a frozen site without a contract, and CONV and DYN produced no frozen site. Those closures stay in the funnel. They are not rewritten as kill failures, and they are not rewritten as proof that the families are absent from the program.

### 4.3 Ordinal-8 NumPy pilot

The pilot used a controlled NumPy runtime (`2.0.0.dev0`) and a single controlled subject. Two sites and four pairs were frozen. Each pair has five inputs, so a complete official execution has 60 valid cells: 20 original, 20 semantic, and 20 syntactic.

The first official attempt on the INV/TF pair produced 15 infrastructure failures (`numpy.array_api` import failure). Kill/survival was not observed on that attempt. The failure record remains in the funnel. It is not deleted and is not counted toward kill/survival. Treating that attempt as SURVIVE would invent an outcome. Treating the later clean replay as a silent replacement would hide an official failure.

A later clean replay, after the controlled runtime removed that import block, produced 15 valid INV/TF cells. A remaining-three batch produced the other 45 valid cells. Combined official evidence is 60 cells, all PASS. Qualification of the runtime is identity and provenance. It is not a scientific kill observation. The two later records share the same controlled runtime identity. They remain separately labeled source records in Table 1 so that the INV/TF clean replay is not confused with the remaining-three batch.

<!-- Evidence: data/p3_v3/phase3/ordinal8-paired-evidence-rq2-handoff.json; valid_cells=60; valid_pass_cells=60; infrastructure_failure_cells=15; clean_replay_valid_cells=15; remaining_three_valid_cells=45 -->

### 4.4 Exact-overlap measurement

After the paired executions, a separate measurement compared each semantic mutant with its syntactic baseline on two identities:

- exact equality of normalized patches;
- exact equality of mutant trees.

The two measures are computed separately. A pair may fail one and pass the other. Neither measure replaces behavioral kill/survival. The official artefact reports counts only. It does not select a confidence level or an exact binomial method, because that authority was incomplete.

<!-- Evidence: data/p3_v3/phase3/ordinal8-exact-overlap-v1/exact-overlap.json; normalized_patch_overlap_count=0; mutant_tree_overlap_count=0; pair_count=4 -->

### 4.5 Stage I prospective applicability census

Stage I asked one frozen question. Under the frozen applicability authority, frozen source identities, and the ordinal 9–22 successor universe, which of each subject’s ten slots close as `SITE_FROZEN`, and which close as `APPLICABILITY_CLOSED_NOT_APPLICABLE`?

The census covered 14 subjects and 140 slots. Each subject has ten inventory slots. Reconstruction of the official terminal accepted the artefact, recovered ordinals 9 through 22, and found a `null` site identity on every closure. Predicates, inventory, and the first-applicable rule were not altered after observation. No second census of the same version was started after the totals were known.

Stage II candidate derivation is a preregistered mechanical rule: a subject enters the candidate universe only if `site_frozen_count >= 1`. With every subject at zero, the derived universe is empty. Stage I does not answer contract existence, pair constructibility, kill/survival, overlap, or C3. An empty candidate universe therefore closes the current Stage II path without creating a behavioral finding about those fourteen programs.

<!-- Evidence: data/p3_v3/phase3/prospective-multiproject-applicability-stage1-v2/cohort-terminal.json; artifact_sha256=45757bb594d582b380ee7955f0caeab92adfd3c10702c31cf788f896a6595a97; n_subjects=14; not_applicable_count sum=140; site_frozen_count sum=0 -->

## 5. Results

### 5.1 NumPy paired pilot

Table 1 reports the four frozen pairs. Pair labels are the frozen family/mechanism names. The reducers are pair-level.

**Table 1.** Pair-level reducers on the ordinal-8 NumPy pilot.

| Pair | Family / mechanism | Source record | Semantic reducer | Syntactic reducer |
|---|---|---|---|---|
| P1 | INV/TF | clean replay | KILL | KILL |
| P2 | INV/SI | remaining-three batch | KILL | SURVIVE |
| P3 | CMP/TF | remaining-three batch | KILL | KILL |
| P4 | CMP/SI | remaining-three batch | KILL | KILL |

<!-- Evidence: data/p3_v3/phase3/ordinal8-paired-evidence-rq2-handoff.json; pairs[].semantic_pair_result / syntactic_pair_result; artifact_sha256=a846ca2edded55ed48e0e9071a9aa218efc3dbcc9bd302a77ceb53bce9d822c5 -->

Summary, at the pair unit:

- semantic mutants: 4/4 KILL;
- syntactic baselines: 3/4 KILL, 1/4 SURVIVE;
- official contingency: both killed = 3, semantic only = 1, syntactic only = 0, neither = 0;
- original baselines: 20/20 SURVIVE;
- official clean cells: 60/60 PASS.

<!-- Evidence: data/p3_v3/phase3/ordinal8-paired-evidence-rq2-handoff.json; reductions.semantic_pair_kill=4/4; syntactic_pair_kill=3/4; original_cell_survive=20/20; paired_contingency -->

Inside each pair, the five-input repeated measures were uniform. On P1, P3, and P4, the original survived on 5/5 cells, the semantic mutant was killed on 5/5, and the syntactic baseline was killed on 5/5. On P2, the original survived on 5/5, the semantic mutant was killed on 5/5, and the syntactic baseline survived on 5/5. Those cell counts explain the pair reducers. They do not create twenty independent experiments.

<!-- Evidence: data/p3_v3/phase3/ordinal8-paired-evidence-rq2-handoff.json; pairs[].original_cell_survive / semantic_cell_kill / syntactic_cell_kill -->

The only discordant pair is P2 (INV/SI): semantic KILL, syntactic SURVIVE. That pattern is a local observation on one frozen pair. The paper does not convert 4/4 versus 3/4 into an aggregate superiority score, a ratio, or a significance test. Input cells remain repeated measures inside pairs. Site-pooled cell rates are not a substitute for the pair table. Semantic cell kills were 20/20 and syntactic cell kills were 15/20 only because P2 contributed five syntactic survivals. Reporting those cell fractions without the pair table would hide the reduction unit.

### 5.2 Exact overlap

On the same four pairs, normalized-patch exact overlap is 0/4 and mutant-tree exact overlap is 0/4. Each pair was compared on both identities. No pair produced a true exact match on either identity. The measurement used the frozen source identities already bound to the paired executions. It did not invent a third overlap metric after seeing the first two zeros.
<!-- Evidence: data/p3_v3/phase3/ordinal8-exact-overlap-v1/exact-overlap.json; normalized_patch_overlap_count=0; mutant_tree_overlap_count=0; artifact_sha256=f4ca00694f4a3a0a63df151bf7cce96a66ae957d0d11d85ca056cb0e6b438071 -->

Interpretation is limited. On this pilot, the frozen semantic mutant is not the same normalized patch as its syntactic baseline, and the two mutant trees are not identical. That is a local construct-distinctness observation for these pairs. It does not say that semantic mutants have greater testing value. It does not say that the same non-overlap would appear on another project. The denominator is four.

### 5.3 Prospective applicability census

Stage I completed 14 subjects at ordinals 9–22 and 140 official closures. The rebuilt totals are 0 `SITE_FROZEN` and 140 `APPLICABILITY_CLOSED_NOT_APPLICABLE`. Under the preregistered rule `site_frozen_count >= 1`, the Stage II candidate universe is 0.

<!-- Evidence: data/p3_v3/phase3/prospective-multiproject-applicability-stage1-v2/cohort-terminal.json; artifact_sha256=45757bb594d582b380ee7955f0caeab92adfd3c10702c31cf788f896a6595a97 -->
<!-- Evidence: docs/review_20260828/p3_c3_stage1_applicability_census_scientific_disclosure.md -->

These totals hold under the frozen PBF, slot inventory, applicability predicates, and first-applicable selection boundary. They are the Stage I answer to the prespecified applicability question for the ordinal 9–22 successor universe. They are not an industrial applicability rate. They do not say that the fourteen subjects, or their programs, lack the target construct. They do not support C3.

Because the candidate universe is empty, the current two-stage prospective version cannot produce another paired project. Stage II of this version does not start.

## 6. Discussion

The NumPy table is a small, complete paired object. Four semantic mutants were killed. Three syntactic baselines were killed. One syntactic baseline survived. The discordant pair points in one direction on this subject. That is all the behavioral contrast the official record contains. Turning the contrast into a general semantic-versus-syntactic finding would ignore the pair unit, the two represented families, and the single project.

Exact non-overlap adds a second local fact. The semantic and syntactic members of each pair are not the same normalized patch and not the same mutant tree. The observation blocks one cheap objection: that the pilot merely renamed first-order edits. It does not block a larger objection: that some other syntactic catalog, or some other semantic encoding, would coincide. The overlap denominator is four, and the interval authority was left incomplete on purpose.

Kill cells cannot replace project-level replication. Twenty original cells, twenty semantic cells, and twenty syntactic cells are repeated measures inside four pairs on one project. A cell bootstrap, a pair bootstrap, or a site bootstrap would still be a within-project interval. The frozen uncertainty account requires a project cluster. With `n_projects = 1`, that account is unidentifiable.

The empty Stage I candidate universe is a lawful closure of the current Stage II path, not a defect in the census. Stage I asked whether any slot in the frozen 9–22 universe satisfied the frozen applicability predicates. None did. The mechanical rule then yields zero Stage II candidates. Changing predicates after seeing that total would replace the prespecified question with a new one. The paper does not do that.

Study governance is visible in the funnel: the infrastructure failure remains disclosed, clean replay is labeled as a new controlled run, and no substitute significance test was added after the 3/4 versus 4/4 split. Those choices protect interpretation. They are not a scientific contribution of their own.

The same discipline applies to family coverage. INV and CMP are the only families with completed pairs on this subject. A reader who wants a family-level hypothesis test does not have one. A reader who wants to treat CONV, DYN, or MONO as killed or as missing constructs does not have that license either. The funnel already records those closures as applicability or contract-boundary events.

The current paper therefore stops seeking a second or third paired-evidence project on this C3 route. The missing object is multi-project uncertainty, and the present version cannot produce it. Author review of this draft can tighten wording. It cannot invent a second executed project.

## 7. Threats to Validity and Limitations

**Construct validity.** Semantic mutation is defined here through frozen contracts and a paired syntactic baseline, not through a universally agreed operator catalog. Exact non-overlap on four pairs reduces the risk that the two arms are identical objects. It does not establish that the semantic arm matches every prior use of the phrase “semantic mutation.” [CITATION NEEDED: Clark/Dan/Hierons and other named semantic-mutation operators, for comparison of constructs]. Family coverage on the completed pairs is INV and CMP only.

**Internal validity.** Mutants and inputs were frozen before valid kill/survival observation. The first INV/TF execution is an infrastructure failure, not a suppressed kill. Clean replay is a disclosed later run. The remaining-three batch was not rewritten from the INV/TF outcomes. The main residual internal threat is that one site’s clean replay and the other site’s batch are different official records, even though both are valid PASS cells under the same controlled runtime.

**External validity.** `n_projects = 1`. The subject is the first eligible completed NumPy subject after a prospective eligibility search, not a random draw from scientific-computing libraries. The 18/35 catalog is not a sampling frame for the pair table. Stage I’s empty frozen-site count is bound to one frozen authority and one successor list. Neither result transports to an industrial population. Language, build system, and numerical library family are all fixed in the executed pilot. A C++ or Java subject, or a second Python library, is not in the pair table.

The Stage I universe is also narrow in a different way. Ordinals 9–22 are the frozen successor list for this version. A later independent version could ask a different applicability question. That possibility is not a warrant to alter the present predicates after seeing the present totals. It is a reminder that the census is version-bound.

**Conclusion validity.** No effect size, *p*-value, confidence interval, superiority ratio, bootstrap interval, or project-level variance is reported, because the official artefacts do not provide those quantities under a frozen method. Exact-binomial clarification for overlap is a post-outcome method clarification: the interval was left unmeasured rather than filled with a writer-chosen procedure. The 3/4 versus 4/4 contrast is not treated as statistically significant. C3 remains blocked.

**Selection and adaptivity.** Stage I predicates were not relaxed after the empty candidate universe was observed. Ordinals 9–22 were not placed again into the same version. The paper does not assemble another subject table or another predicate set for the present C3 route. Collider risk remains: ordinal 8 is the first eligible completed subject, disclosed as such.

**Infrastructure and runtime history.** The `numpy.array_api` failure is part of the official funnel. Readers who ignore it would overstate the cleanliness of the first attempt. Readers who treat it as a scientific SURVIVE would invent an outcome that was not observed.

Further limits already fixed in the claim-scope amendment: the Stage I authority may miss other lawful constructions; 0/140 does not mean the target construct is absent; the exact-overlap denominator is 4; current results cannot support superiority or industrial applicability rates.

## 8. Conclusion

On one NumPy subject and four frozen pairs, semantic mutants were killed on every pair, syntactic baselines were killed on three pairs, and both exact-overlap measures were empty. The result is a single-project paired-evidence pilot. It is a local methodological observation about pairing, reduction units, and overlap checks.

The current prospective version then reached an eligibility bound: under its frozen authority, it has no Stage II candidate. Cross-project construct distinctness and project-clustered uncertainty remain unidentifiable. C3 stays blocked. The paper keeps RQ2 and narrows the claim list to what the official record can carry.

The appropriate next use of this draft is author review and evidence alignment of the prose, not another experiment on the closed two-stage path.

## Data Availability

Machine-readable evidence for this draft is stored in the project repository. The ordinal-8 paired handoff, the exact-overlap artefact, and the Stage I cohort terminal are the authoritative count sources. Internal HTML comments next to first uses of those counts record artefact identities for audit. No permanent archival DOI is minted in this draft. [REPOSITORY PUBLICATION URL AND ARCHIVAL DOI: AUTHOR TO COMPLETE IF AND WHEN RELEASED]

## Ethics Declaration

This study analyzes program variants, frozen inputs, and applicability closures. It does not enroll human participants and does not use personal sensitive data. [AUTHOR TO CONFIRM THIS DECLARATION AGAINST THE FINAL SUBJECT LIST AND ANY ARTIFACT LICENSE CONSTRAINTS]

## Author Contributions

[AUTHOR TO COMPLETE USING CRediT ROLES. NAMES AND ROLE ASSIGNMENTS ARE NOT INFERRED IN THIS DRAFT]

## Conflict of Interest

[AUTHOR TO CONFIRM. NO CONFLICT STATEMENT IS INVENTED IN THIS DRAFT]

## Funding

[AUTHOR TO COMPLETE. NO FUNDER IS INFERRED IN THIS DRAFT]

## AI-use Disclosure

[AUTHOR TO COMPLETE ACCORDING TO TARGET-VENUE POLICY]

## References

Ammann, P., & Offutt, J. (2008). *Introduction to software testing* (1st ed.). Cambridge University Press.

Andrews, J. H., Briand, L. C., & Labiche, Y. (2005). Is mutation an appropriate tool for testing experiments? In *Proc. ICSE 2005* (pp. 402-411). ACM. https://doi.org/10.1145/1062455.1062530

Delgado-Pérez, P., & Chicano, F. (2020). An experimental and practical study on the equivalent mutant connection: An evolutionary approach. *Information and Software Technology*, 124, 106317. https://doi.org/10.1016/j.infsof.2020.106317

DeMillo, R. A., Lipton, R. J., & Sayward, F. G. (1978). Hints on test data selection: Help for the practicing programmer. *Computer*, 11(4), 34-41. https://doi.org/10.1109/C-M.1978.218136

Humbatova, N., Jahangirova, G., & Tonella, P. (2021). DeepCrime: Mutation testing of deep learning systems based on real faults. In *Proc. ISSTA 2021* (pp. 67-78). ACM. https://doi.org/10.1145/3460319.3464825

Jia, Y., & Harman, M. (2009). Higher Order Mutation Testing. *Information and Software Technology*, 51(10), 1379-1393. https://doi.org/10.1016/j.infsof.2009.04.016

Jia, Y., & Harman, M. (2011). An analysis and survey of the development of mutation testing. *IEEE Transactions on Software Engineering*, 37(5), 649-678. https://doi.org/10.1109/TSE.2010.62

Just, R., Jalali, D., Inozemtseva, L., Ernst, M. D., Holmes, R., & Fraser, G. (2014a). Are mutants a valid substitute for real faults in software testing? In *Proc. FSE 2014* (pp. 654-665). ACM. https://doi.org/10.1145/2635868.2635929

Just, R., Jalali, D., & Ernst, M. D. (2014b). Defects4J: A database of existing faults to enable controlled testing studies for Java programs. In *Proc. ISSTA 2014* (pp. 437-440). ACM. https://doi.org/10.1145/2610384.2628055

Kintis, M., Papadakis, M., Papadopoulos, A., Valvis, E., Malevris, N., & Le Traon, Y. (2018). How effective are mutation testing tools? An empirical analysis of Java mutation testing tools with manual analysis and real faults. *Empirical Software Engineering*, 23(4), 2426-2463. https://doi.org/10.1007/s10664-017-9582-5

Papadakis, M., Kintis, M., Zhang, J., Jia, Y., Le Traon, Y., & Harman, M. (2019). Mutation testing advances: An analysis and survey. *Advances in Computers*, 112, 275-378. https://doi.org/10.1016/bs.adcom.2018.03.015

Petrović, G., & Ivanković, M. (2018). State of mutation testing at Google. In *Proc. ICSE-SEIP 2018* (pp. 163-171). ACM. https://doi.org/10.1145/3183519.3183521

Petrović, G., Ivanković, M., Fraser, G., & Just, R. (2021). Practical mutation testing at scale: A view from Google. *IEEE Transactions on Software Engineering*, 48(10), 3900-3912. https://doi.org/10.1109/TSE.2021.3107634

Tip, F., Bell, J., & Schäfer, M. (2024). LLMorpheus: Mutation testing using large language models. *arXiv preprint* arXiv:2404.09952.

Zhang, M., Keung, J. W., Chen, T. Y., & Xiao, Y. (2021). Validating class integration test order generation systems with Metamorphic Testing. *Information and Software Technology*, 132, 106507. https://doi.org/10.1016/j.infsof.2020.106507
