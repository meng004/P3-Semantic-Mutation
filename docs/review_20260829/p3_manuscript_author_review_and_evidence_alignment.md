# P3 manuscript author review and evidence alignment

Task: `P3_MANUSCRIPT_AUTHOR_REVIEW_AND_EVIDENCE_ALIGNMENT`

Review mode: read-only evidence-alignment author review. This is not peer review, manuscript revision, a venue decision, or a new experiment.

Terminal status: `P3_MANUSCRIPT_AUTHOR_REVIEW_PACKET_READY`

`P3_C3_CLAIM_SCOPE_PATH_CLOSED=true`

## Review boundary and input identity

The reviewed manuscript is `research/p3-semantic-mutation-evidence-aligned-manuscript-v0.1.md` at commit `8b36afdb4e6e3f92f2d6aef4f98dd38853bef26c`, parent `c5af89a0c25614dbd9ba97b853e5a62f8091a24e`. The manuscript SHA-256 at review start was `b6f69b0f815f277903fd028a05605b295ca245e0806cc261f7895cad41021889`.

The fixed authority files matched the requested identities:

| Object | SHA-256 |
|---|---|
| `research/evidence/p3_claim_ledger_v1.3.0.yml` | `95184db4db23c84649cb85fbf6f0d4a9503fa45a70297b7c29d9a57d9d5b6ff5` |
| `research/p3-semantic-mutation-core-claims-rqs-v1.3.0.md` | `41a8fa78beb621267223762fe0879f96ecb98e0eee7aea0befac72261d48483f` |
| `docs/superpowers/specs/2026-08-28-p3-c3-claim-scope-and-ledger-amendment-design.md` | `709e3cb59539c8620b50e2c1c232cf90bde365a923a4502b1f6dfae5cddddec2` |
| `docs/review_20260828/p3_c3_stage1_applicability_census_scientific_disclosure.md` | `9f0040f460d48310d764c10a75319b8ec4fb4fdb6b691e78b153d284cdaa0552` |
| `data/p3_v3/phase3/prospective-multiproject-applicability-stage1-v2/cohort-terminal.json` | `f2e9af90ed31bd118a80808a04e3af66c5abee539f0093c6087c176e2bee51ab` |
| `docs/review_20260828/p3_claim_path_reprioritization_after_stage1_empty_candidates.md` | `dcba9d459eb58bf2984d117b826077998f1069120eb630d004a74ae337836079` |

The Stage I terminal records artifact SHA-256 `45757bb594d582b380ee7955f0caeab92adfd3c10702c31cf788f896a6595a97`. The ordinal-8 review used only committed formal Markdown/JSON: the RQ2 handoff, clean replay, remaining-three batch, prior infrastructure-failure record, and exact-overlap artifact. No `/tmp`, Cloud runtime, or `/opt/cursor/artifacts` evidence was used as claim authority.

## Executive author-facing finding

The manuscript is aligned with the fixed empirical record on the core counts and boundaries. It consistently reports one executed project, four NumPy pairs, semantic 4/4 KILL, syntactic 3/4 KILL and 1/4 SURVIVE, both exact-overlap counts at 0/4, and a 14-subject/140-closure Stage I census with 0 `SITE_FROZEN`, 140 `APPLICABILITY_CLOSED_NOT_APPLICABLE`, and zero Stage II candidates. C3 remains `blocked`; no cross-project inference is made.

No core evidence contradiction was found. The main unresolved items are bibliographic completion, direct locator strength for the 18-group/35-defect catalog foundation, two adjacent related-work formulations whose semantic support was not established by the existing repository audits, provisional venue-dependent structure, and author-owned metadata/disclosure choices.

## Section-by-section review

| Section | Finding | Evidence/authority | Disposition | Suggested action |
|---|---|---|---|---|
| Title | The title states the three actual objects: semantic/syntactic comparison, single-project paired pilot, and prospective census. “Evidence-Bound Scope” accurately signals the ceiling, but final wording is an author and venue choice. | Core-claims v1.3.0, current-paper scope; claim-scope design §§1, 3 | `AUTHOR_DECISION_REQUIRED` | Author accepts the present title or requests a venue-calibrated alternative; do not remove the single-project/census boundary. |
| Abstract | All principal counts and C3 status agree with the formal evidence. The Stage I statement is framed as a version-bound eligibility result, not a general negative finding. | Ordinal-8 RQ2 handoff; exact-overlap JSON; Stage I terminal; ledger C3 | `ACCEPT` | Preserve the current scope qualifiers in any later shortening. |
| Internal Chinese companion abstract | Empirical counts and limitations align with the English abstract. Retention is explicitly not a submission default. | Same evidence as Abstract | `AUTHOR_DECISION_REQUIRED` | Author decides whether the internal companion remains in the working manuscript or is removed before submission. |
| Keywords | Terms match the study, but final keyword count and whether “metamorphic testing” is sufficiently central depend on venue policy. | Manuscript study design; venue not confirmed | `ACCEPT` | Revisit only after the target venue is confirmed. |
| Introduction | The motivation, repeated-measure warning, single-cluster ceiling, contribution list, and explicit non-claims match the claim authority. The first contribution is a methodological framing rather than a lifted C1/C3 status. | Ledger; core-claims; ordinal-8 handoff; claim-scope design | `ACCEPT` | If revised later, keep the contribution list explicitly local and do not promote C3. |
| Background and Related Work | Six required citation topics remain unresolved in the prose. Existing audits verify the existence/metadata of several leads but do not provide a complete semantic-alignment certificate for all neighboring claims. | Repository reference audits; `source/references.bib`; theory memoranda | `CITATION_REQUIRED` | Resolve the six gaps only after author authorization; separately check the two possible related-work overclaims listed below. |
| Research Questions and Claim Boundaries | Frozen RQ2 is retained and the answerable range is contracted to three local questions. C3, `n_projects = 1`, and the no-cross-project ceiling are explicit. | Core-claims v1.3.0 §§RQ2 and Current-paper scope; ledger C3 | `AUTHOR_DECISION_REQUIRED` | Author confirms the current contracted RQ2 scope. No automatic RQ rewrite is recommended. |
| Study Design | Catalog foundation, single-project pilot, and prospective census are clearly separated. The 18-group/35-`verified_full`/fixed-version sentence has a repository lead, but its direct locator is weaker than the machine-readable locators used for ordinal 8 and Stage I. | Path-reprioritization report §4.1; ordinal-8 handoff; Stage I terminal | `REVISION_RECOMMENDED` | After approval, add the strongest existing catalog locator or weaken “each recorded with a fixed version” to the exact repository-audited wording. |
| Results | Reports only formal observations, preserves the pair as the reduction unit, retains the infrastructure failure, and does not introduce a post-outcome statistic. | RQ2 handoff; clean replay; remaining-three batch; exact-overlap; Stage I terminal | `ACCEPT` | Preserve the pair table and its denominators. |
| Discussion | Observation, interpretation, limitation, and governance are substantively distinguished, but they remain interleaved in prose. The “blocks one cheap objection” sentence is an authorial interpretation, not a new empirical result. | Exact-overlap artifact; claim-scope design allowed/forbidden interpretations | `REVISION_RECOMMENDED` | After approval, label or reorder observation → interpretation → limitation → future boundary; retain the local-only wording. |
| Threats and Limitations | Correctly distinguishes construct, internal, external, conclusion, selection/adaptivity, and infrastructure threats. It states `n_projects = 1`, first-eligible-subject selection, and the version-bound census. | Handoff methodology audit and limitations; Stage I disclosure §§7, 10 | `ACCEPT` | Preserve all current ceilings; add citations only where author approves. |
| Conclusion | No stronger claim appears than in Results. It retains the pilot, eligibility bound, unidentifiable uncertainty, and blocked C3. | Core-claims current-paper scope; ledger; Stage I path closure | `ACCEPT` | Keep C3 blocked and avoid turning “eligibility bound” into construct absence. |
| Data Availability | Correctly identifies the three authoritative count sources and does not invent a DOI. Public URL/archival DOI policy is unresolved. | Repository evidence paths; author placeholder | `AUTHOR_DECISION_REQUIRED` | Author selects repository publication and archival strategy. |
| Ethics | The draft states no human participants/personal sensitive data but already asks for author confirmation against final subjects and licenses. | Manuscript placeholder; no author attestation in reviewed authority | `AUTHOR_DECISION_REQUIRED` | Author confirms wording and artifact-license implications. |
| Author Contributions | No names or CRediT roles are inferred. | Author-owned facts absent | `AUTHOR_DECISION_REQUIRED` | Author supplies names and CRediT assignments. |
| Conflict of Interest | No statement is invented. | Author-owned fact absent | `AUTHOR_DECISION_REQUIRED` | Author confirms the final declaration. |
| Funding | No funder is inferred. | Author-owned fact absent | `AUTHOR_DECISION_REQUIRED` | Author supplies the final funding statement. |
| AI-use Disclosure | Correctly defers to venue policy, which is not confirmed. | Target venue and disclosure path unresolved | `AUTHOR_DECISION_REQUIRED` | Confirm venue and authorize a separate disclosure task if desired. |
| References | All 15 present entries are cited in text and every current author-year citation resolves to a listed entry. Metadata existence is covered by repository audits, with a known Petrović online-first/print-year advisory. Six additional topics remain citation gaps. | `reference_verification_audit.md`; `reference_verification_round85.md`; U2 foundations audit | `CITATION_REQUIRED` | Complete the six gaps after author authorization; do not claim semantic verification merely from metadata existence. |

Disposition summary: `ACCEPT` 6; `REVISION_RECOMMENDED` 2; `AUTHOR_DECISION_REQUIRED` 9; `CITATION_REQUIRED` 2; `EVIDENCE_CONFLICT` 0; `REMOVE_OR_WEAKEN` 0.

## Complete empirical claim–evidence alignment

| Claim ID | Manuscript location | Exact/condensed claim | Evidence locator | Evidence status | Claim strength | Disposition |
|---|---|---|---|---|---|---|
| E01 | Abstract ¶2 | One NumPy subject, four pairs, five inputs per pair, 60 official PASS cells | RQ2 handoff `analysis_units`, `execution_funnel` | `DIRECTLY_SUPPORTED` | observed | `ACCEPT` |
| E02 | Abstract ¶2 | Semantic 4/4 KILL; syntactic 3/4 KILL and 1/4 SURVIVE | RQ2 handoff `reductions`, `pairs` | `DIRECTLY_SUPPORTED` | observed | `ACCEPT` |
| E03 | Abstract ¶2 | Normalized-patch and mutant-tree exact equality are each 0/4 | exact-overlap JSON count/pair-count fields | `DIRECTLY_SUPPORTED` | observed | `ACCEPT` |
| E04 | Abstract ¶2 | Pilot does not identify project-clustered uncertainty; C3 remains blocked | RQ2 handoff `rq2_coverage`, `claim_ceiling`; ledger C3 | `DIRECTLY_SUPPORTED` | blocked ceiling | `ACCEPT` |
| E05 | Abstract ¶3 | Fourteen successors yielded no Stage II candidate in the current frozen version | Stage I terminal subjects; Stage I disclosure §5 | `SUPPORTED_WITH_SCOPE_QUALIFIER` | qualified | `ACCEPT` |
| E06 | Introduction ¶3 | Inputs are repeated measures inside pairs; four pairs on one library remain one project cluster | RQ2 handoff `analysis_units` and methodology audit | `SUPPORTED_WITH_SCOPE_QUALIFIER` | qualified methods boundary | `ACCEPT` |
| E07 | Introduction ¶4 | C3 is blocked and its upgrade condition remains unmet | Ledger C3 and `status_policy.note` | `DIRECTLY_SUPPORTED` | blocked | `ACCEPT` |
| E08 | Introduction contributions | Five listed items are the current-paper contribution framing | Core-claims current-paper scope; manuscript synthesis | `AUTHORIAL_INTERPRETATION` | authorial contribution framing | `AUTHOR_DECISION_REQUIRED` |
| E09 | Introduction final ¶ | 18 program groups and 35 defects are not 18 runner-ready paired-evidence projects or 35 paired observations | Path-reprioritization §§4.1, 4.6; claim-scope design §6 | `DIRECTLY_SUPPORTED` | negative ceiling | `ACCEPT` |
| E10 | §3 | Frozen RQ2 wording | Core-claims v1.3.0 RQ2 | `DIRECTLY_SUPPORTED` | frozen authority | `ACCEPT` |
| E11 | §3 | Current paper answers only pair reducers, two exact-overlap measures, and Stage II candidate-universe status; family coverage stays unmeasured | Core-claims current-paper scope; exact-overlap; Stage I terminal | `DIRECTLY_SUPPORTED` | contracted scope | `ACCEPT` |
| E12 | §3 C3 paragraph | C3 remains blocked because `n_projects = 1` and clustered uncertainty is unidentifiable | RQ2 handoff `analysis_units.n_projects`, `rq2_coverage`; ledger | `DIRECTLY_SUPPORTED` | blocked | `ACCEPT` |
| E13 | §4.1 ¶1 | Foundation contains 18 program/library groups and 35 `verified_full` defects, each with a fixed version | Path-reprioritization §4.1 and catalog summary references | `INTERNALLY_SUPPORTED_BUT_LOCATOR_WEAK` | descriptive foundation | `REVISION_RECOMMENDED` |
| E14 | §4.1 ¶3 | Executed paired-evidence project count is one: NumPy ordinal 8 | RQ2 handoff `analysis_units.n_projects`, controlled subject identity | `DIRECTLY_SUPPORTED` | observed | `ACCEPT` |
| E15 | §4.2 ¶2 | 1 project, 1 repository, 1 subject, 2 sites, 4 pairs, 4+4 mutants, 5 inputs/pair; cells are not independent | RQ2 handoff `analysis_units` | `DIRECTLY_SUPPORTED` | observed/design-bound | `ACCEPT` |
| E16 | §4.2 final ¶ | INV/CMP and SI/TF represented; MONO lacks a contract; CONV/DYN have no frozen site | RQ2 handoff `contract_category_coverage` | `DIRECTLY_SUPPORTED` | observed funnel | `ACCEPT` |
| E17 | §4.3 ¶1 | Controlled NumPy `2.0.0.dev0`, 2 sites, 4 pairs, 60-cell complete execution | RQ2 handoff `execution_funnel`; clean/batch runtime identity | `DIRECTLY_SUPPORTED` | observed | `ACCEPT` |
| E18 | §4.3 ¶2 | First INV/TF attempt had 15 infrastructure failures and no kill/survival observation | RQ2 handoff `execution_funnel`; prior paired-evidence JSON | `DIRECTLY_SUPPORTED` | observed funnel | `ACCEPT` |
| E19 | §4.3 ¶3 | Clean replay gave 15 cells; remaining-three batch 45; combined 60/60 PASS under one controlled runtime identity | RQ2 handoff `execution_funnel`; clean/batch JSON | `DIRECTLY_SUPPORTED` | observed | `ACCEPT` |
| E20 | §4.4 | Two overlap identities are separate; both are counts only; interval authority is incomplete | exact-overlap JSON fields and interval status/reason | `DIRECTLY_SUPPORTED` | observed plus unmeasured boundary | `ACCEPT` |
| E21 | §4.5 ¶1–2 | Stage I covered 14 subjects and 140 slots under frozen PBF/inventory/predicates/selection | Stage I terminal; Stage I disclosure §§2–4 | `DIRECTLY_SUPPORTED` | observed/design-bound | `ACCEPT` |
| E22 | §4.5 ¶3 | Candidate rule is `site_frozen_count >= 1`; zero frozen sites yields empty Stage II universe | Stage I disclosure §5; terminal per-subject counts | `DIRECTLY_SUPPORTED` | observed mechanical derivation | `ACCEPT` |
| E23 | §5.1 Table 1 | Pair outcomes: P1 K/K, P2 K/S, P3 K/K, P4 K/K | RQ2 handoff `pairs[]` | `DIRECTLY_SUPPORTED` | observed | `ACCEPT` |
| E24 | §5.1 summary | Semantic 4/4; syntactic 3/4; contingency 3/1/0/0; original 20/20; 60/60 PASS | RQ2 handoff `reductions`, `paired_contingency`, `execution_funnel` | `DIRECTLY_SUPPORTED` | observed | `ACCEPT` |
| E25 | §5.1 cell detail | Three pairs have 5/5 KILL in both arms; P2 syntactic is 5/5 SURVIVE while semantic is 5/5 KILL; originals 5/5 SURVIVE | RQ2 handoff `pairs[]` | `DIRECTLY_SUPPORTED` | repeated-measure detail | `ACCEPT` |
| E26 | §5.1 final ¶ | P2 is the sole discordant pair; no superiority score/test is licensed | RQ2 handoff `paired_contingency`, blocked claims | `SUPPORTED_WITH_SCOPE_QUALIFIER` | observed plus negative ceiling | `ACCEPT` |
| E27 | §5.2 ¶1 | Both exact-overlap measures are 0/4 and no pair exactly matches | exact-overlap JSON `pairs[]` and aggregate counts | `DIRECTLY_SUPPORTED` | observed | `ACCEPT` |
| E28 | §5.2 ¶2 | Exact non-overlap is a local construct-distinctness observation, not testing-value evidence or transport | Core-claims RQ2; claim-scope design §§3, 6 | `SUPPORTED_WITH_SCOPE_QUALIFIER` | qualified interpretation | `ACCEPT` |
| E29 | §5.3 ¶1 | Stage I: 14 subjects, 140 closures, 0 `SITE_FROZEN`, 140 not applicable, 0 Stage II candidates | Stage I terminal; Stage I disclosure §§3–5 | `DIRECTLY_SUPPORTED` | observed | `ACCEPT` |
| E30 | §5.3 ¶2–3 | 0/140 is authority-bound, not industrial prevalence/construct absence/C3 support; Stage II does not start | Stage I disclosure §§6–10; path decision | `SUPPORTED_WITH_SCOPE_QUALIFIER` | qualified/blocked | `ACCEPT` |
| E31 | Discussion ¶1 | The only official behavioral contrast is 4/4 versus 3/4 on one subject | RQ2 handoff `reductions`, limitations | `DIRECTLY_SUPPORTED` | observed | `ACCEPT` |
| E32 | Discussion ¶2 | Exact non-overlap blocks the narrow objection that the pilot merely renamed identical edits | exact-overlap data plus manuscript interpretation | `AUTHORIAL_INTERPRETATION` | bounded interpretation | `REVISION_RECOMMENDED` |
| E33 | Discussion ¶3 | 20/20/20 cells cannot identify project uncertainty; a project cluster is missing at `n_projects = 1`, so no cross-project inference is licensed | RQ2 handoff uncertainty accounting and methodology audit | `DIRECTLY_SUPPORTED` | blocked inference | `ACCEPT` |
| E34 | Discussion/Conclusion | Current two-stage route is closed; no second/third paired project is sought on this C3 path | Ledger note; core-claims current-paper scope; path decision | `DIRECTLY_SUPPORTED` | frozen path decision | `ACCEPT` |
| E35 | Conclusion | Pilot and candidate-universe result do not lift C3; RQ2 remains contracted | Ledger; core-claims; Stage I disclosure | `DIRECTLY_SUPPORTED` | blocked/contracted | `ACCEPT` |
| E36 | Data Availability | Three repository artifacts are authoritative count sources; no DOI is currently minted | Manuscript evidence comments and fixed repository objects | `DIRECTLY_SUPPORTED` | repository-state statement | `ACCEPT` |

Claim-table total: 36. Evidence-status counts: `DIRECTLY_SUPPORTED` 28; `SUPPORTED_WITH_SCOPE_QUALIFIER` 5; `INTERNALLY_SUPPORTED_BUT_LOCATOR_WEAK` 1; `AUTHORIAL_INTERPRETATION` 2; `UNSUPPORTED` 0; `CONTRADICTED` 0.

## RQ and argument-structure review

| Question | Assessment | Disposition | Author-facing note |
|---|---|---|---|
| Is the core research question clear and answerable by current evidence? | Yes, after the manuscript's explicit contraction. The frozen RQ2 wording is broader than the three current-paper questions, but the paper states the contraction before Methods/Results. | `ACCEPT` | Keep the frozen wording and the three-question boundary together. |
| Is RQ2 retained but correctly narrowed? | Yes. Pair behavior, two exact-overlap measures, and current-version candidate-universe status are the only answers claimed. | `AUTHOR_DECISION_REQUIRED` | Author confirms this is the intended paper-level RQ2 scope. |
| Is there a logical contradiction between blocked C3 and the paper contribution? | No. The paper presents a pilot, census, and evidence boundary; it does not present completed multi-project C3 confirmation. | `ACCEPT` | Preserve the distinction between local construct observation and lifted claim status. |
| Does Introduction promise cross-project conclusions Results cannot deliver? | No. It explicitly states the missing cluster and rejects transport. | `ACCEPT` | Do not broaden the contribution verbs in later revision. |
| Does Study Design distinguish catalog foundation, single-project pilot, and prospective census? | Yes. The three objects are separately named and have different denominators and roles. | `ACCEPT` | Strengthen only the direct locator for 18/35/fixed versions. |
| Does Results report only formal observations? | Yes. It uses handoff/overlap/terminal counts and retains unmeasured/unidentifiable states. | `ACCEPT` | Keep infrastructure history and pair denominators visible. |
| Does Discussion distinguish observation, interpretation, limitation, and future work? | Substantively yes, but visually they are interleaved. | `REVISION_RECOMMENDED` | A later structural pass can label the four layers without changing claims. |
| Is Conclusion stronger than Results? | No. It is weaker/equivalent and keeps C3 blocked. | `ACCEPT` | Preserve current ceiling. |
| Does the title express pilot + census + evidence boundary? | Yes. It is accurate, though long and venue-facing. | `AUTHOR_DECISION_REQUIRED` | Author decides whether accuracy or brevity dominates. |
| If TOSEM is not confirmed, what remains provisional? | Journal-specific section ordering, abstract/keyword limits, citation style, title length, related-work placement, AI disclosure, data-availability wording, and any cover-letter framing. | `AUTHOR_DECISION_REQUIRED` | Confirm venue before any formatting or policy-compliance pass. |

No RQ rewrite is recommended at this stage. If the author later decides to replace the frozen RQ2 wording in the manuscript while retaining the living authority unchanged, two candidate paper-facing formulations are available for consideration, not selection:

1. “On the frozen NumPy pairs, what behavioral and exact-structural differences are observed between semantic mutants and their first-order syntactic baselines, and which cross-project conclusions remain unidentifiable?”
2. “What pair-level kill/survival and exact-overlap differences are observed in the ordinal-8 pilot, and what eligibility boundary does the frozen prospective census impose on the current multi-project path?”

## Existing-reference audit

The manuscript contains 15 reference-list entries. All 15 are cited in the body, and every current author-year citation has a matching reference-list entry. Repository audits verify metadata existence for all 15. They do not, by themselves, certify every adjacent semantic claim.

| Existing reference | Main manuscript use | Repository-audit result | Citation review status | Note |
|---|---|---|---|---|
| Ammann & Offutt 2008 | Coupling hypothesis / testing foundation | Metadata verified in round85 #20 | `EXISTENCE_VERIFIED_ALIGNMENT_UNCHECKED` | Existing audit confirms the book, not the precise adjacent paraphrase. |
| Andrews et al. 2005 | Mutants as substitutes for real faults | Metadata verified in audits #4/#5 | `EXISTENCE_VERIFIED_ALIGNMENT_UNCHECKED` | Title is directionally aligned; no P3-specific passage audit exists. |
| Delgado-Pérez & Chicano 2020 | Equivalent-mutant problem | Metadata and relevance explicitly discussed in the audit | `VERIFIED_FROM_EXISTING_AUDIT` | Existing audit names the equivalent-mutant relevance directly. |
| DeMillo et al. 1978 | Mutation-testing origin and test-data selection | Metadata verified in audits #1 | `EXISTENCE_VERIFIED_ALIGNMENT_UNCHECKED` | No full-text claim-alignment record for the P3 sentence. |
| Humbatova et al. 2021 | DeepCrime / real-fault-oriented DL mutation | Metadata verified in audits #12/#24 | `EXISTENCE_VERIFIED_ALIGNMENT_UNCHECKED` | Bibliography is clean; neighboring construct comparison remains unaudited. |
| Jia & Harman 2009 | Higher-order mutation beyond first-order catalogs | Metadata verified in audits #3/#4 | `POSSIBLE_OVERCLAIM` | “Does not systematically express” is stronger than the existing metadata/relevance audit establishes. |
| Jia & Harman 2011 | Mutation-testing survey | Metadata verified in audits #2 | `EXISTENCE_VERIFIED_ALIGNMENT_UNCHECKED` | Survey existence is verified; P3-specific synthesis not passage-checked. |
| Just et al. 2014a | Mutants versus real faults | Metadata verified in audits #5/#6 | `EXISTENCE_VERIFIED_ALIGNMENT_UNCHECKED` | No adjacent passage audit in repository. |
| Just et al. 2014b | Defects4J controlled buggy/fixed pairs | Metadata verified in audits #13/#25 | `EXISTENCE_VERIFIED_ALIGNMENT_UNCHECKED` | The design paraphrase is plausible but not semantically certified by the audit. |
| Kintis et al. 2018 | Tool/operator-set disagreement | Metadata verified in audits #7/#8 | `EXISTENCE_VERIFIED_ALIGNMENT_UNCHECKED` | Audit verifies record, not the exact “operator sets differ” sentence. |
| Papadakis et al. 2019 | Mutation-testing survey and construct caveat | Metadata verified in audits #6/#7 | `EXISTENCE_VERIFIED_ALIGNMENT_UNCHECKED` | No P3-specific semantic alignment record. |
| Petrović & Ivanković 2018 | Industrial scale/productive-mutant filtering | Metadata verified in audits #9/#21 | `EXISTENCE_VERIFIED_ALIGNMENT_UNCHECKED` | Adjacent filtering/scale synthesis is not passage-checked. |
| Petrović et al. 2021 | Practical mutation testing at scale | Metadata verified in audits #10/#22 | `EXISTENCE_VERIFIED_ALIGNMENT_UNCHECKED` | 2021 early-access versus 2022 issue year remains a nonblocking audit advisory. |
| Tip et al. 2024 | LLMorpheus beyond a fixed operator list | Metadata verified in audits #11/#23 | `POSSIBLE_OVERCLAIM` | The existing audit verifies arXiv identity, not “outside a fixed operator list.” |
| Zhang et al. 2021 | MT used to validate a test-order-generation system | Metadata and exact relevance discussed in audit candidate 1 / round85 #11 | `VERIFIED_FROM_EXISTING_AUDIT` | Existing audit explicitly characterizes this use. |

Status summary for the 15 entries: `VERIFIED_FROM_EXISTING_AUDIT` 2; `EXISTENCE_VERIFIED_ALIGNMENT_UNCHECKED` 11; `POSSIBLE_OVERCLAIM` 2; `CITATION_REQUIRED` 0; `UNRESOLVED` 0. Metadata existence is 15/15 from existing audits; semantic alignment is not certified 15/15.

## Citation gaps

| Citation gap | Manuscript location | Why needed | Existing repository lead | Author action |
|---|---|---|---|---|
| Clark, Dan, and Hierons semantic mutation testing / SMT-C | §2.2 after named semantic-mutation operators | Establishes the prior named construct and tool lineage; avoids presenting the P3 label as novel terminology. | `reference_verification_round85.md` refs 12–13; `source/references.bib` Clark/Dan entries; theory memorandum bibliography | Approve addition from existing audited leads and, if required, authorize passage-level alignment verification. |
| Chen, Cheung, and Yau metamorphic-testing definition | §2.3 opening | Supports the oracle-problem/relations-among-executions definition with foundational authority. | U2 foundations audit verifies `chen2018metamorphic`; `source/references.bib` contains the survey; no repository audit was found for the exact original Chen/Cheung/Yau item requested by the placeholder. | Decide whether the survey is sufficient or authorize a separate search for the original formulation. |
| Data-mutation-directed MR studies | §2.3 final paragraph | Distinguishes data/relation mutation for MR acquisition from paired program mutants. | round85 refs 15–18; `source/references.bib` `sun2016mumt` and later data-mutation/datamorphic items; theory memorandum §§MR-neighbor evidence | Approve which already-audited lineage items belong in P3 and authorize semantic alignment checking. |
| Construct-validity guidance for software-engineering experiments | §2.4 | Grounds the construct-validity terminology and the interpretation of proxy/label mismatch. | No dedicated verified bibliographic lead was found; only internal study-design uses of “construct validity.” | Author decides whether to authorize targeted literature search. |
| Hierarchical/project-clustered inference for multi-project software studies | §2.4 | Grounds the refusal to treat cells/pairs as project replication and the need for project-level uncertainty. | Internal governing plan and RQ2 handoff specify the analysis boundary, but no verified external methodology citation was found. | Author decides whether to authorize targeted methodology search. |
| Named semantic-mutation operators for construct comparison | Threats: Construct validity | Needed to compare P3's contract-bound construct with prior semantic-variation/operator constructs. | round85 refs 12–14; Clark/Dan/Hierons and Derezińska/Zaremba entries in `source/references.bib`; theory memoranda | Approve a bounded construct-comparison citation set; do not merge it automatically with the general lineage gap. |

## Author decisions required

- [ ] 接受或修改当前标题
- [ ] 接受 RQ2 的当前缩小范围
- [ ] 接受 C3 不作为当前论文主贡献
- [ ] 接受 NumPy 为唯一 paired-evidence project
- [ ] 接受 Stage I 只作为 applicability census
- [ ] 确认 TOSEM 是否为目标期刊
- [ ] 决定是否授权下一任务联网检索 6 个 citation gaps
- [ ] 确认作者姓名
- [ ] 确认单位
- [ ] 确认 CRediT
- [ ] 确认 funding
- [ ] 确认 conflict of interest
- [ ] 确认 ethics wording
- [ ] 确认 AI-use disclosure 路径
- [ ] 确认 Data Availability 的公开 URL/DOI 策略
- [ ] 决定是否保留内部中文伴随摘要

No item above is adjudicated by this review.

## Recommended manuscript revisions after author approval

### `BLOCKING_EVIDENCE_CORRECTION`

None. No core count or fixed claim-authority contradiction was found.

### `CLAIM_SCOPE_CORRECTION`

| Manuscript section | Current issue | Suggested change | Required author authority |
|---|---|---|---|
| §4.1 Subject and defect foundation | The 18-group/35-defect count has an internal lead, but “each recorded with a fixed version” lacks a direct locator comparable to the JSON-backed claims. | Add the strongest existing catalog locator or use the exact audited wording from the path-decision record. | Approval to change study-design prose. |
| Introduction contributions | The frozen pairing protocol is presented as a contribution; this is valid as study design but must not be read as lifting ledger C1 or C3. | Optionally add “for this pilot” to the first contribution item. | Approval of contribution framing. |
| Discussion exact-overlap interpretation | “Blocks one cheap objection” is bounded but rhetorical. | Recast as an explicit inference: exact identity is ruled out for these four pairs; broader construct equivalence is not. | Approval to revise interpretive prose. |

### `CITATION_COMPLETION`

| Manuscript section | Current issue | Suggested change | Required author authority |
|---|---|---|---|
| §§2.2–2.4 and Threats | Six citation gaps remain. | Select sources from existing leads where sufficient; authorize bounded external search only for unresolved gaps. | Source-selection/search authorization. |
| §2.2 Jia & Harman 2009 sentence | Existing audit does not establish the exact “default set does not express” formulation. | Verify against source text or weaken to a statement directly supported by the audited record. | Approval to verify or weaken. |
| §2.2 Tip et al. 2024 sentence | “Outside a fixed operator list” is not semantically verified by the repository audit. | Verify against the paper or narrow to “uses an LLM to generate mutants.” | Approval to verify or narrow. |

### `STRUCTURAL_REVISION`

| Manuscript section | Current issue | Suggested change | Required author authority |
|---|---|---|---|
| Discussion | Observation, interpretation, limitation, and governance/future boundary are interleaved. | Reorder those four layers without introducing new claims. | Approval for structural revision. |
| Whole manuscript | Target venue is unconfirmed. | Defer TOSEM-specific ordering, limits, citation style, and disclosures until venue confirmation. | Venue decision. |

### `STYLE_ONLY`

| Manuscript section | Current issue | Suggested change | Required author authority |
|---|---|---|---|
| Whole manuscript | Mixed “artifact/artefact,” numeric-word and code-token conventions may vary. | Run one consistency pass after substantive author adjudication. | Approval for style pass. |
| Evidence comments | Internal HTML comments are useful for audit but may not be submission-ready. | Decide whether to retain them in the source and strip them only in a derived submission build. | Submission-source policy. |

### `AUTHOR_METADATA`

| Manuscript section | Current issue | Suggested change | Required author authority |
|---|---|---|---|
| Title page / Author Contributions | Names, affiliations, and CRediT are placeholders. | Fill only from author-supplied facts. | Author factual confirmation. |
| Conflict / Funding / Ethics | Statements are unresolved or provisional. | Fill from author/institutional facts and final artifact-license review. | Author/institutional confirmation. |
| AI-use / Data Availability | Venue policy and public repository/DOI path are unresolved. | Complete after venue and release-strategy decisions. | Venue and release authorization. |

## Alignment verdict and milestone deviation check

- Evidence conflict: none found.
- Claim overreach: no obvious core empirical overreach found. Two related-work formulations require semantic verification or narrowing, and two manuscript statements are explicitly classified as authorial interpretation.
- C3: `blocked`.
- `n_projects`: 1.
- Stage II candidates: 0.
- Stage I/II reopened: no.
- Automatic peer-review panel started: no.
- Manuscript rewritten: no.
- Author-owned decision inferred or checked: no.
- New unsupported scientific claim added: no; this report contains audit findings and recommendations only.
- Scientific milestone path: still on author review and evidence alignment of the current paper; no experiment path was reopened.

## Next step

`AUTHOR_ADJUDICATION_REQUIRED`

The next step belongs to the author. This review does not authorize manuscript revision, citation search, venue selection, or metadata completion.
