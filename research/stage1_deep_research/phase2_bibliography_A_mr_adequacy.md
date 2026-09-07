# Phase 2 Bibliography — Theme A: Metamorphic Testing, MR-Set Quality, and MR Adequacy Measurement

**Agent:** `bibliography_agent` (Phase 2, INVESTIGATION)
**Target venue of parent paper:** ACM TOSEM
**Date compiled:** 2026-09-07
**Workspace:** `/Users/limeng/Papers/P3-SemanticMutation`

> **HEADLINE FINDING (read this first).** The paper's motivating claim — that MR-set adequacy "has no trustworthy measurement" — **cannot be stated in that form.** At least two 2024 publications explicitly propose *test adequacy criteria for metamorphic testing* by name: Fu, Sun, Zhang & Liu (arXiv:2412.20692) and Liu, Li, Tao & Zheng (QRS-C 2024, `10.1109/QRS-C63300.2024.00072`). A third (Huang, Luo & Li, IAECST 2022) uses "test adequacy criteria" in its title. The A3 verdict below is **`PARTIAL`**, not `NO_EXISTING_MR_ADEQUACY_CRITERION`. §4 sets out exactly what each of these does and does not cover, so the claim can be narrowed defensibly rather than abandoned.

---

## 1. Search Strategy

### 1.1 Role separation (per caller instruction)

| Tool family | Role | Used for |
|---|---|---|
| `user-undermind` | **Discovery (现状)** | Harvesting candidates from two pre-paid completed deep searches |
| `user-paper-search` | **Verification (文献核对)** | Independent existence confirmation of every candidate; gap-filling queries |

No candidate entered the bibliography on Undermind's authority alone. Every included entry below was independently resolved through at least one `user-paper-search` call.

### 1.2 Undermind deep searches consumed (no new searches launched)

Workspace `d9baef75-52ff-4860-b661-6d7a9e647f42`. Both read in full via `inspect_deep_searches` (`detail_level='standard'`, full pagination, `status_only` NOT used).

**DS1 — `/近五年蜕变关系有效性与充分性`** (completed Aug 30, 66 papers, read 1–66 in two pages)
Stated goal: peer-reviewed work 2021–2026 systematically covering MR effectiveness, adequacy, diversity, composition, prioritisation, applicability domain, tolerance, false-verdict control, automated generation, and scientific-computing application. Prioritised IEEE TSE, ACM TOSEM, STVR, IST and nuclear-science journals. Excluded pure preprints, generative-model applications without relation-validity argument, and incomplete bibliographic records.

**DS2 — `/蜕变关系可信性与无预期值程序验证`** (completed Aug 30, 117 papers, read 1–117 in three pages)
Stated goal: systematic map of the test-oracle problem, metamorphic testing, and MR effectiveness / adequacy / diversity / prioritisation / automated identification / tolerance / false-verdict control, weighted toward scientific computing and reactor physics, burnup and thermal-hydraulic codes. Prioritised original theory papers, authoritative surveys, and post-2016 methodological progress.

**Assessment of coverage gap:** DS1 and DS2 between them cover MR effectiveness, selection, prioritisation, diversity, composition and automated identification thoroughly, and they did surface the decisive A3 items (`Liu24`, `Fu24`, `Hua22`). Their scope constraints left three real holes, all of which I closed with my own `user-paper-search` queries rather than by launching a new deep search: **(i)** pre-2016 foundations (Weyuker 1982; the 1998 technical report; the 2002–2006 MR-selection papers were only partially covered), **(ii)** mutation testing used *as the yardstick for MR quality* as a distinct practice (A4), and **(iii)** datamorphic testing and LLM-derived MRs. **I did not launch a new deep search.** I judge the remaining gap to be small and adequately covered; the caller may disagree — see Handoff note 5.

### 1.3 My own `user-paper-search` queries (exact strings)

Priority chain attempted per caller instruction: `search_dblp` → `search_arxiv` → `search_crossref`; `get_crossref_paper_by_doi` when a DOI was in hand; fallback `search_openalex` → `search_semantic` → `search_google_scholar`.

**Tool availability problem (material — see §7):** `search_dblp` and `search_semantic` returned empty/omitted payloads on **every** invocation in this session (dblp: 4 attempts across 4 distinct queries and 3 different `max_results` values; semantic: 3 attempts). Neither ever returned a readable record. The verification backbone therefore became `get_crossref_paper_by_doi` → `search_crossref` → `search_openalex` → `search_arxiv`.

| # | Tool | Exact query string | Purpose |
|---|---|---|---|
| Q1 | `search_dblp` | `Test Adequacy Criteria for Metamorphic Testing` | A3 verification — **tool returned nothing** |
| Q2 | `search_arxiv` | `Test Adequacy for Metamorphic Testing: Criteria, Measurement, and Implication` | A3 — verified arXiv:2412.20692 |
| Q3 | `search_dblp` | `metamorphic testing adequacy criteria` | A3 adversarial sweep — **tool returned nothing** |
| Q4 | `search_dblp` | `metamorphic relation` (max_results 5) | dblp smoke test — **tool returned nothing** |
| Q5 | `search_openalex` | `metamorphic relation adequacy criterion` | A3 adversarial sweep — surfaced METTLE, MR-Adopt |
| Q6 | `search_crossref` | `On testing non-testable programs Weyuker` | A2 foundation |
| Q7 | `search_crossref` | `datamorphic testing methodology test morphisms` | A6 |
| Q8 | `search_openalex` | `metamorphic relations derived from conservation laws symmetry physical invariants scientific software` | A5 special interest — heavy geology false-positive contamination |
| Q9 | `search_crossref` | `how many metamorphic relations are enough sufficient set completeness` | A3 adversarial — **zero on-theme hits** |
| Q10 | `search_semantic` | `Metamorphic testing a new approach for generating next test cases technical report HKUST` | A1 canonical — **tool returned nothing** |
| Q11 | `search_arxiv` | `Metamorphic Testing: A New Approach for Generating Next Test Cases Chen Cheung Yiu` | A1 canonical — arXiv full-text search returned unrelated physics records |
| Q12 | `search_openalex` | `Metamorphic Testing A New Approach for Generating Next Test Cases` | A1 canonical — resolved arXiv:2002.12543 |
| Q13 | `search_openalex` | `Case studies on the selection of useful relations in metamorphic testing` | A3 |
| Q14 | `search_openalex` | `Application of metamorphic testing in numerical analysis Chan Chen Cheung Lau Yiu` | A1/A2 — **not found** |
| Q15 | `search_openalex` | `mutation testing evaluate fault detection effectiveness metamorphic relations mutation score` | A4 sweep |
| Q16 | `search_arxiv` | `semantic mutation metric metamorphic relation adequacy scientific computing programs` | Self-citation check |
| Q17 | `search_openalex` | `large language models generate metamorphic relations LLM MR identification` | A5 |
| Q18 | `search_openalex` | `SAME similarity analysis method evaluating metamorphic relations testing AI systems` | A3 |
| Q19 | `search_semantic` | `adequacy criterion for a set of metamorphic relations sufficiency` | A3 final adversarial — **tool returned nothing** |
| Q20 | `search_crossref` | `Application of metamorphic testing in numerical analysis Chan 1998` | A1/A2 — **not found** |
| Q21 | `search_openalex` | `Chan Chen Cheung Lau Yiu metamorphic testing IASTED software engineering 1998 numerical` | A1/A2 — **not found** |
| Q22 | `search_openalex` | `Testing high performance numerical simulation programs experience lessons learned and open issues` | A2 |
| Q23 | `search_openalex` | `A Template-Based Approach to Describing Metamorphic Relations Segura` | A5 |
| Q24 | `search_openalex` | `Exploring a Test Data-Driven Method for Selecting and Constraining Metamorphic Relations` | A3 |
| Q25–Q52 | `get_crossref_paper_by_doi` | 28 individual DOI resolutions (listed in §6) | Per-entry verification |

**Boolean logic.** Neither `search_crossref` nor `search_openalex` in this MCP exposes explicit Boolean operators; both take a free-text relevance query. Conjunction was therefore approximated by term stacking (e.g. Q8 stacks `conservation laws` + `symmetry` + `physical invariants` + `scientific software`), and disjunction by running separate queries (Q5 / Q9 / Q19 are three disjuncts of the same adversarial A3 question). This is a genuine limitation on reproducibility of *ranking*, though not of *membership*: any of the queries above rerun against the same backends will return the same records, in possibly different order.

**Date range.** No hard date filter. Undermind DS1 self-limited to 2021–2026; DS2 weighted post-2016 but admitted foundations. My own queries were deliberately **unbounded backwards** to recover 1981–2006 foundations that DS1's window structurally excluded. Justification: the theme requires establishing both the origin of MT (1998) and the origin of the oracle problem framing (1982), neither reachable inside DS1's window.

**Language.** English only for inclusion. Chinese-language records surfaced by OpenAlex (e.g. Zhang, Chan, Tse & Hu, *Journal of Software* 2009) were screened but excluded as not load-bearing for a TOSEM submission.

**Document types.** Included: journal articles, conference and workshop proceedings papers, one self-archived technical report, three arXiv preprints (each explicitly labelled). Excluded: dissertations, editorials, standards, book chapters, peer-review artefacts.

**Inclusion criteria.** A record was included if it (i) concerns metamorphic testing, metamorphic relations, or the test-oracle problem, **and** (ii) bears on at least one of A1–A6, **and** (iii) was independently confirmed to exist via a `user-paper-search` call.

**Exclusion criteria.** (a) Geological/petrological false positives from the token "metamorphic" — a large and persistent contaminant in OpenAlex, roughly 30% of Q8's returns; (b) domain applications of MT that contribute nothing about MR-set *quality* (DBMS, chatbots, machine translation, autonomous driving, IaC engines, search engines) unless they carry an adequacy or evaluation argument; (c) code-verification and V&V literature (MMS, Richardson extrapolation, CTF/RELAP verification suites) — real and heavily represented in Undermind DS2, but belonging to a different theme, not A; (d) floating-point error analysis (atomic conditions, interval constraints, compilers for reals) — same reason; (e) anything not verifiable.

---

## 2. PRISMA-style flow

```
IDENTIFICATION
  Undermind DS1 /近五年蜕变关系有效性与充分性 ................  66
  Undermind DS2 /蜕变关系可信性与无预期值程序验证 ............. 117
  Own user-paper-search queries (Q5–Q24), new records ........  31
                                                              ----
  Total records identified .................................... 214

DE-DUPLICATION
  Cross-search duplicates (present in both DS1 and DS2) .......  33
  Preprint/version-of-record pairs collapsed ..................   3
      (Li et al. TOSEM 10.1145/3708521 vs arXiv 2406.05397;
       Duque-Torres SEAA 10.1109/seaa60479.2023.00063 vs arXiv 2307.15522;
       Ayerdi GenMorph TSE record vs Undermind duplicate)
                                                              ----
  Duplicates removed ..........................................  36
  Unique records screened ..................................... 178

SCREENING (title + abstract against A1–A6 scope)
  Excluded at screening ....................................... 121
      - code verification / V&V / MMS / Richardson ..........  38
      - floating-point & numerical error analysis ...........  11
      - nuclear-domain application, no MR-quality content ....  17
      - MT domain applications, no MR-quality content ........  33
      - geological "metamorphic" false positives .............  14
      - non-English / dissertation / standard / editorial ....   8
  Records sought for verification ..............................  57

VERIFICATION (independent user-paper-search resolution)
  Excluded: on closer read, out of A-scope .....................  11
  Excluded: COULD NOT BE VERIFIED (IRON RULE 2 — gray zone = FAIL)   2
      - Chan, Chen, Cheung, Lau & Yiu (1998), "Application of
        metamorphic testing in numerical analysis". Attempted
        search_openalex x2, search_crossref x2, search_semantic
        (tool failure), search_dblp (tool failure). Not resolvable.
      - Yan et al. (2016), "Research of Testing for Scientific
        Computing Software in the Area of Nuclear Power Based on
        Metamorphic Testing". Undermind reports "Unknown Journal";
        no DOI; not resolvable via crossref or openalex.
                                                              ----
  INCLUDED ..................................................... 44
```

**Included by subarea:** A1 = 6, A2 = 8, A3 = 13, A4 = 5, A5 = 9, A6 = 3.
A3 is deliberately over-weighted relative to the 30–40 target because it carries the paper's motivating claim and the caller designated it the core question.

---

## 3. Annotated Bibliography

Notation: **[Uxx]** = Undermind cite key of origin, for traceability back to the deep search. Entries with no [Uxx] were found by my own paper-search queries.

---

### A1 — MT foundations and surveys

---

**A1.1** Chen, T. Y., Cheung, S. C., & Yiu, S. M. (2020). *Metamorphic testing: A new approach for generating next test cases* (Technical Report HKUST-CS98-01). arXiv. https://doi.org/10.48550/arXiv.2002.12543 (Original work published 1998) **[Che20]**

- **Relevance.** The origin of metamorphic testing and the single most mis-cited artifact in this literature. See §5 for the canonical-citation ruling.
- **Key findings.** (1) Successful (non-failing) test cases still carry exploitable information and can seed follow-up cases. (2) Test oracles are, in Weyuker's sense, pragmatically unattainable in most situations, so a technique that does not need one has standing. (3) The proposal is framed as a *test case selection* technique that augments existing strategies, not as an oracle substitute — a framing later papers routinely overstate.
- **Methodology.** Conceptual/technical report. No empirical evaluation.
- **Quality/limitations.** 11 pages. Self-archived to arXiv on 2020-02-28 by S. C. Cheung, twenty-two years after issue. Carries an arXiv DataCite DOI but **no publisher DOI**; the 1998 artifact itself is an institutional technical report, not peer-reviewed. Citation counts attributed to it (465 in OpenAlex, 693 in Undermind's index) are aggregated across variant citation forms and should not be quoted precisely.
- **Contribution to Theme A.** Establishes that MRs are *necessary* properties of the target function, never sufficient ones. This asymmetry is the formal root of the entire adequacy question the parent paper attacks: a necessary-condition checker cannot be complete by construction, so "how much of the obligation space does this MR set cover" is well-posed from 1998 onward and was left open by the founding document.

---

**A1.2** Chen, T. Y., Kuo, F.-C., Tse, T. H., & Zhou, Z. Q. (2003). Metamorphic testing and beyond. In *Eleventh Annual International Workshop on Software Technology and Engineering Practice* (pp. 94–100). IEEE. https://doi.org/10.1109/STEP.2003.18

- **Relevance.** First venue-published consolidation of MT after the technical report; the usual peer-reviewed anchor when authors want to avoid citing a technical report.
- **Key findings.** (1) Positions MT as extensible beyond test generation. (2) Identifies MR identification as the practical bottleneck.
- **Methodology.** Position/overview paper.
- **Quality/limitations.** Workshop paper, 7 pages. Crossref carries a null publication date (1970-01-01 placeholder), so the year must be taken from the proceedings title.
- **Contribution.** Useful as the citable early formulation, but it does not resolve the adequacy question either — it names MR identification as the bottleneck and stops.

---

**A1.3** Segura, S., Fraser, G., Sanchez, A. B., & Ruiz-Cortés, A. (2016). A survey on metamorphic testing. *IEEE Transactions on Software Engineering, 42*(9), 805–824. https://doi.org/10.1109/TSE.2016.2532875 **[Seg16]**

- **Relevance.** The Segura-class survey the brief asks for. One of the two standard MT survey citations.
- **Key findings.** (1) Consolidates MT results and application areas from 1998 to 2016. (2) Analyses *common practice in empirical studies of MT* — this section is directly load-bearing for A4, because it documents that evaluation-by-seeded-fault and evaluation-by-mutant is the field's default. (3) Enumerates open challenges, with MR identification and MR quality prominent.
- **Methodology.** Systematic survey.
- **Quality/limitations.** Cut-off 2016; predates every A3 adequacy-criterion paper below. Crossref reports 505 citations, Undermind's index 580 — a reminder not to quote citation counts as if they were stable.
- **Contribution.** The strongest available published evidence that, as of 2016, the field evaluated MRs empirically by fault detection and had no adequacy criterion. It is the correct citation for the *historical* form of the paper's claim.

---

**A1.4** Chen, T. Y., Kuo, F.-C., Liu, H., Poon, P.-L., Towey, D., Tse, T. H., & Zhou, Z. Q. (2018). Metamorphic testing: A review of challenges and opportunities. *ACM Computing Surveys, 51*(1), 1–27. https://doi.org/10.1145/3143561 **[Che18]**

- **Relevance.** The Chen-class review of challenges and opportunities named in the brief.
- **Key findings.** (1) Defines the central element of MT as "a set of metamorphic relations, which are necessary properties of the target function or algorithm in relation to multiple inputs and their expected outputs" — the definition the parent paper should quote when it argues that an MR encodes an equation-level obligation. (2) Reviews MR identification, test case generation, integration with other SE techniques, and validation/evaluation as four separate research strands. (3) Names remaining challenges.
- **Methodology.** Narrative review by the technique's originators and principal school.
- **Quality/limitations.** Authored by the incumbent school, so its framing of "challenges yet to be addressed" is not a neutral gap analysis. Cut-off 2017.
- **Contribution.** Its *set*-level phrasing of MRs is the cleanest published warrant for treating the MR set (not the individual MR) as the unit of adequacy.

---

**A1.5** Chen, T. Y., & Tse, T. H. (2021). New visions on metamorphic testing after a quarter of a century of inception. In *Proceedings of the 29th ACM Joint Meeting on European Software Engineering Conference and Symposium on the Foundations of Software Engineering* (pp. 1487–1490). ACM. https://doi.org/10.1145/3468264.3473136 **[Che21]**

- **Relevance.** The originators' own 2021 statement of where MT theory is thin.
- **Key findings.** (1) Explicitly states that "MT research will be beyond empirical studies and move toward a theoretical foundation" — i.e. the originators concede in 2021 that MT is empirically rather than theoretically grounded. (2) Argues MRs may extend beyond necessary properties of algorithms. (3) Suggests MRs will alleviate the *reliable test set problem*, which is the closest the founding school comes to gesturing at adequacy.
- **Methodology.** Invited vision paper, 4 pages.
- **Quality/limitations.** Vision paper — assertions are not evidenced. Very short.
- **Contribution.** **High rhetorical value and low evidential value.** This is the best available quotable admission from the field's founders that MT lacked theoretical foundations as of 2021. It should be cited for that admission, not as evidence of a gap, and the parent paper must not lean on it harder than a 4-page vision paper can bear.

---

**A1.6** Li, R., Liu, H., Poon, P.-L., Towey, D., Sun, C.-A., Zheng, Z., Zhou, Z. Q., & Chen, T. Y. (2025). Metamorphic relation generation: State of the art and research directions. *ACM Transactions on Software Engineering and Methodology, 34*(5), 1–25. https://doi.org/10.1145/3708521 **[Li24]**

- **Relevance.** The newest systematic mapping of MR generation, and a TOSEM paper — directly relevant to the parent paper's venue positioning.
- **Key findings.** (1) Systematic review of a decade of MR generation from varied sources and domains. (2) Frames future advances as needed in both theory and technique for identifying and constructing MRs. (3) Organises MR generation by source of derivation, which is the taxonomy A5 sits inside.
- **Methodology.** Systematic review.
- **Quality/limitations.** Scoped to *generation*, not evaluation — it does not adjudicate MR-set adequacy, and should not be cited as if it did. Note the citation-metadata discrepancy: Undermind dates it 2024, Crossref's version of record is 2025-05-27 (vol. 34, iss. 5); an earlier arXiv version (2406.05397) carries a slightly different title ("...and Visions for Future Research"). **Cite the TOSEM record, 2025.**
- **Contribution.** Establishes that as of 2025 the field's own state-of-the-art review treats MR *generation* as the organising problem, with evaluation subordinate — supporting evidence that adequacy is under-theorised even where it is not absent.

---

### A2 — MT for scientific computing and the oracle problem

---

**A2.1** Weyuker, E. J. (1982). On testing non-testable programs. *The Computer Journal, 25*(4), 465–470. https://doi.org/10.1093/comjnl/25.4.465

- **Relevance.** The Weyuker-class untestable-programs citation the brief asks for. The origin of the concept MT exists to address.
- **Key findings.** (1) Defines programs for which no oracle exists, or for which the tester cannot practically decide correctness, as "non-testable". (2) Identifies numerical/scientific programs as the canonical case. (3) Proposes pseudo-oracles and property checking as partial remedies — the direct ancestor of MRs.
- **Methodology.** Conceptual.
- **Quality/limitations.** 1982; predates the entire modern testing apparatus. Cited via the token "non-testable" far more often than it is read.
- **Contribution.** The parent paper's problem statement inherits from here. Weyuker's remedy is property checking without a completeness argument — which is precisely the unfinished business the adequacy question represents.

---

**A2.2** Barr, E. T., Harman, M., McMinn, P., Shahbaz, M., & Yoo (2015). The oracle problem in software testing: A survey. *IEEE Transactions on Software Engineering, 41*(5), 507–525. https://doi.org/10.1109/TSE.2014.2372785 **[Bar15]**

- **Relevance.** The Barr-class oracle-problem survey named in the brief. The standard citation for the oracle problem.
- **Key findings.** (1) Taxonomises oracles as specified, derived, implicit, and absent, placing MT under derived oracles. (2) Argues oracle automation is the bottleneck inhibiting overall test automation. (3) Notes that when no automated oracle is adequate, the human remains the residual oracle.
- **Methodology.** Systematic survey, very large corpus.
- **Quality/limitations.** MT is one section among many; the survey does not engage MR-set quality. Cut-off ~2014.
- **Contribution.** Supplies the field-level framing that makes MR quality consequential: if MRs *are* the oracle, then the quality of the MR set is the quality of the oracle, and an unmeasured MR set is an unmeasured oracle.

---

**A2.3** Patel, K., & Hierons, R. M. (2018). A mapping study on testing non-testable systems. *Software Quality Journal, 26*(4), 1373–1413. https://doi.org/10.1007/s11219-017-9392-4

- **Relevance.** Independent (non-Chen-school) mapping of the oracle-problem solution space.
- **Key findings.** (1) Maps N-version testing, MT, assertions, ML oracles, and statistical hypothesis testing as the five families addressing non-testability. (2) Compares them on effectiveness, efficiency and usability. (3) Identifies research opportunities within the non-testable-systems domain.
- **Methodology.** Systematic mapping study.
- **Quality/limitations.** Breadth over depth; MT gets comparative rather than internal treatment.
- **Contribution.** Valuable precisely because it is *outside* the Chen school. Its comparative framing gives an independent basis for asking why MT alone among these five families lacks a settled adequacy notion.

---

**A2.4** Kanewala, U., & Bieman, J. M. (2014). Testing scientific software: A systematic literature review. *Information and Software Technology, 56*(10), 1219–1232. https://doi.org/10.1016/j.infsof.2014.05.006 **[Kan14b]**

- **Relevance.** The standard SLR on testing scientific software; establishes the parent paper's application domain as a recognised problem area.
- **Key findings.** (1) 62 studies analysed. (2) Challenges split into two categories: those intrinsic to scientific software (oracle problems foremost) and those arising from cultural differences between scientists and software engineers. (3) Identifies the scientist tendency to treat code and the model it implements as inseparable — directly relevant to why equation-level obligations are the natural unit in this domain.
- **Methodology.** Systematic literature review.
- **Quality/limitations.** 2014 cut-off; the ML/surrogate era is entirely absent.
- **Contribution.** The finding that scientists treat code and model as inseparable is the strongest published support for the parent paper's move to define adequacy against equation-level structure rather than code structure.

---

**A2.5** Chen, T. Y., Feng, J., & Tse, T. H. (2002). Metamorphic testing of programs on partial differential equations: A case study. In *Proceedings 26th Annual International Computer Software and Applications Conference* (pp. 327–333). IEEE. https://doi.org/10.1109/CMPSAC.2002.1045022 **[Che02]**

- **Relevance.** The earliest MT-on-numerical-PDE-programs case study; the ancestor of the parent paper's application domain.
- **Key findings.** (1) MT applied to an elliptic PDE solver with Dirichlet boundary conditions. (2) One MR identified, derived from the numerical property that refining grid points or step size yields a better approximation. (3) The MR detected the seeded error, and the authors claim transferability to other refinement-based numerical methods.
- **Methodology.** Single case study, single MR.
- **Quality/limitations.** **Extremely thin evidentially** — one program, one MR, one error. Its influence (63–124 citations depending on index) vastly exceeds its evidential weight. Crossref carries a null date placeholder.
- **Contribution.** Historically important as the first derivation of an MR from a *numerical-method property* rather than from a code inspection — a 2002 precedent for A5's equation-level derivation question, but at the level of discretisation behaviour, not conservation structure.

---

**A2.6** Liu, H., Kuo, F.-C., Towey, D., & Chen, T. Y. (2014). How effectively does metamorphic testing alleviate the oracle problem? *IEEE Transactions on Software Engineering, 40*(1), 4–22. https://doi.org/10.1109/TSE.2013.46 **[Liu14]**

- **Relevance.** **The single most important A3 entry that is not an adequacy criterion.** This is the paper the field cites when it wants to say "a few MRs are enough".
- **Key findings.** (1) Inexperienced testers could identify a sufficient number of appropriate MRs after very little training. (2) **A small number of diverse MRs, even ones identified ad hoc, had fault-detection capability similar to a test oracle.** (3) Cost-effectiveness improves with MR diversity.
- **Methodology.** Controlled empirical studies with human participants plus fault-detection measurement.
- **Quality/limitations.** **This is the paper the parent paper must engage most carefully.** Its headline claim ("similar to a test oracle") is a *fault-detection-rate* equivalence measured against a specific seeded-fault population on specific programs — it is not a completeness claim, and it silently makes the fault population the denominator. That substitution is exactly the move the parent paper critiques, and here it is made by the field's most-cited empirical result. Human-subject design details (participant expertise, program selection) constrain generalisation.
- **Contribution.** The strongest existing counter-argument to the parent paper's motivation, and simultaneously the cleanest illustration of its point. If "ad hoc MRs already perform like an oracle", the demand for an adequacy metric weakens — *unless* one observes that the equivalence is defined over a fault population, which is precisely the misaligned denominator. Engage this head-on; do not cite it in passing.

---

**A2.7** He, X., Wang, X., Shi, J., & Liu, Y. (2020). Testing high performance numerical simulation programs: Experience, lessons learned, and open issues. In *Proceedings of the 29th ACM SIGSOFT International Symposium on Software Testing and Analysis* (pp. 502–515). ACM. https://doi.org/10.1145/3395363.3397382 **[He20]**

- **Relevance.** Field report on testing five HPC simulation programs used to design and analyse nuclear power plants — the parent paper's exact domain.
- **Key findings.** (1) Five testing approaches applied; 33 bugs found. (2) **Property-based testing and metamorphic testing were the two effective methods.** (3) The team suffered from lack of domain knowledge, high test costs, shortage of test cases, severe oracle issues, and inadequate automation; the programs remain "not exhaustively tested from the perspective of software testing".
- **Methodology.** Industrial experience report, ISSTA.
- **Quality/limitations.** Experience report — no controlled comparison, no reproducible protocol. Findings are observational.
- **Contribution.** **Independent, non-Chen-school, industrial evidence that MT works in this domain but that practitioners cannot tell when they have done enough.** The explicit statement that the programs are not exhaustively tested "from the perspective of software testing" is a practitioner-side articulation of the adequacy gap, and it is more credible than any advocacy paper because these authors were trying to ship, not to publish a method.

---

**A2.8** Yan, S., & Zhu, H. (2025). Metamorphic testing on scientific programs for solving second-order elliptic differential equations. *Software Testing, Verification and Reliability, 35*(1), Article e1912. https://doi.org/10.1002/stvr.1912 **[Yan24]**

- **Relevance.** The most direct methodological neighbour to the parent paper's derivation strategy.
- **Key findings.** (1) Presents a testing process tailored to scientific computation and integrates it into the scientific-software development process. (2) **"Unlike existing approaches, we formally derive metamorphic relations from the numerical models of differential equations built in the development process"** — an explicit claim to formal, model-based MR derivation. (3) Outperforms the trend method on fault detection.
- **Methodology.** Method paper plus experiment; comparison baseline is the trend method.
- **Quality/limitations.** Derivation is from the *numerical model* (discretised equation), not from conservation laws or symmetry group structure. Fault detection is again the evaluation currency — the paper derives MRs formally but evaluates them empirically, so it does not close the adequacy loop. Published Dec 2024 in the 2025 vol. 35(1) issue; Undermind dates it 2024. **Cite as 2025, vol. 35(1).**
- **Contribution.** **The nearest prior art to A5's equation-level derivation question, and it must be cited as such.** It establishes that formal derivation of MRs from equation structure already exists for elliptic PDEs. The parent paper's novelty must therefore be located in *adequacy measurement*, not in the fact of equation-level derivation.

---

### A3 — How are MR sets currently evaluated? (CORE)

---

**A3.1** Fu, A., Sun, C.-A., Zhang, J., & Liu, H. (2024). *Test adequacy for metamorphic testing: Criteria, measurement, and implication* (arXiv:2412.20692). arXiv. https://doi.org/10.48550/arXiv.2412.20692 **[Fu24]**

> **THIS IS THE MOST IMPORTANT ENTRY IN THIS DOCUMENT. It is the paper most likely to be used by a reviewer to reject the parent paper's motivating claim.**

- **Relevance.** Proposes, by name, a set of test adequacy criteria for metamorphic testing.
- **Key findings.** (1) States that "few studies have investigated the test adequacy assessment issue of MT, which hinders the objective measurement of MT's test quality" — i.e. **these authors independently identified the same gap the parent paper claims.** (2) Argues traditional adequacy criteria "are not in line with MT's focus which is to test the software under testing from the perspective of necessary properties", and therefore proposes **a new set of criteria specifying testing requirements from the perspective of necessary properties satisfied by the SUT.** (3) Designs a test adequacy *measurement* over both MRs and source inputs, and shows empirically that test suites with higher measured adequacy exhibit higher fault-detection effectiveness.
- **Methodology.** Criteria definition plus adequacy measurement plus empirical validation against fault detection.
- **Quality/limitations.** **I verified only the arXiv preprint (submitted 2024-12-30, cs.SE, v1).** No version of record was resolvable through Crossref or OpenAlex in this session; it may since have been published and the parent paper's authors must re-check before submission. The validation is circular in the specific sense that matters here: the criterion is *justified* by showing it correlates with fault-detection effectiveness, so the fault population remains the ultimate arbiter. The adequacy measured is that of a **test suite given an MR set**, jointly over MRs and source inputs — not the adequacy of the MR set as such against an independently characterised obligation space. Authors overlap heavily with the Sun/Liu/Chen school (Sun and Liu appear across A3.9, A5.2, A5.x).
- **Contribution.** Establishes that an MT-specific adequacy criterion **exists** and is grounded in the necessary-properties view. The parent paper cannot claim the absence of an MT adequacy criterion. It can, on this evidence, claim that existing criteria measure suite adequacy relative to a *given* MR set and are validated against a fault population, leaving the adequacy of the MR set itself against equation-level semantics unaddressed. That narrowed claim survives this paper; the original claim does not.

---

**A3.2** Liu, Y., Li, R., Tao, H., & Zheng, Z. (2024). Test adequacy criteria for metamorphic testing. In *2024 IEEE 24th International Conference on Software Quality, Reliability, and Security Companion (QRS-C)* (pp. 527–534). IEEE. https://doi.org/10.1109/QRS-C63300.2024.00072 **[Liu24]**

> **Second-most important entry. Title-level collision with the parent paper's claim.**

- **Relevance.** Proposes MTcoverage, an adequacy criterion for MT.
- **Key findings.** (1) Observes that "while many studies concentrate on the defect monitoring capability of MRs, the adequacy criteria for MT often lack coverage information regarding MRs" — an explicit diagnosis that prior MR evaluation is fault-detection-centric. (2) Proposes **MTcoverage, which integrates the degree of MR coverage into an adequacy criterion**, and uses it to formulate test case generation strategies. (3) **"The effectiveness of this coverage criterion was also demonstrated by means of mutation testing."**
- **Methodology.** Criterion definition, generation strategy, mutation-based evaluation.
- **Quality/limitations.** Workshop-companion track (QRS-C), 8 pages, 1–2 citations. MTcoverage is a *coverage* criterion over MRs — it measures how thoroughly the given MRs are exercised, not whether the MR set is the right set. **Its own validation uses mutation testing**, so it is simultaneously an A3 entry and an A4 exhibit: the paper that proposes an MT adequacy criterion validates it with the very syntactic-mutant yardstick the parent paper argues is misaligned.
- **Contribution.** Dual-edged and should be presented as such. It defeats "no adequacy criterion exists". It simultaneously supplies the parent paper's cleanest single illustration that even adequacy work in MT falls back on the mutation-score denominator.

---

**A3.3** Huang, D., Luo, Y., & Li, M. (2022). Metamorphic relations prioritization and selection based on test adequacy criteria. In *2022 4th International Academic Exchange Conference on Science and Technology Innovation (IAECST)* (pp. 503–508). IEEE. https://doi.org/10.1109/IAECST57965.2022.10062094 **[Hua22]**

- **Relevance.** Uses "test adequacy criteria" in its title in an MR-selection context.
- **Key findings.** (1) States that "most existing studies are summaries of engineering experience and lack theoretical discussions". (2) Provides a **distance-based definition of metamorphic relation validity** and a quantitative model relating distance and test coverage. (3) On four programs and ~50 MRs, outperforms random, coverage-based, and distance-based selection at equal MR count.
- **Methodology.** Model plus experiment on four programs.
- **Quality/limitations.** Regional conference, 6 pages. Despite the title, this is **MR prioritisation and selection guided by an existing coverage-adequacy notion, not a new adequacy criterion for MR sets.** Small program pool. **Note for the parent authors: M. Li is a co-author here and on the P3 preprints — this is a self-citation and must be declared as such.**
- **Contribution.** A genuine near-miss on the A3 question, and its own framing ("lack theoretical discussions") is quotable support for the parent paper's premise. But the title overstates what it delivers; do not concede more to it than it earns.

---

**A3.4** Xie, X., Zhang, Z., Chen, T. Y., Liu, Y., Poon, P.-L., & Xu, B. (2020). METTLE: A metamorphic testing approach to assessing and validating unsupervised machine learning systems. *IEEE Transactions on Reliability, 69*(4), 1293–1322. https://doi.org/10.1109/TR.2020.2972266

- **Relevance.** Surfaced by the adversarial Q5 sweep specifically because it uses the phrase "MR-based adequacy criteria".
- **Key findings.** (1) Formulates 11 generic MRs covering user-expected characteristics of unsupervised ML systems. (2) **"Guided by user-defined MR-based adequacy criteria, end users are able to assess, validate, and select appropriate clustering systems."** (3) Frames assessment from the end-user perspective rather than the designer's.
- **Methodology.** Method, MR catalogue, experiment plus user evaluation study.
- **Quality/limitations.** The "adequacy criteria" here are **user-defined acceptance thresholds on MR satisfaction for selecting among clustering systems** — a decision rule for system selection, not an adequacy criterion for an MR set. Scope is unsupervised ML clustering, far from scientific computing.
- **Contribution.** Included because an adversarial reviewer running the same query will find it and ask. Its distance from the parent paper's target is large but must be stated explicitly rather than left for the reviewer to raise.

---

**A3.5** Chen, T. Y., Huang, D., Tse, T. H., & Zhou, Z. Q. (2004). Case studies on the selection of useful relations in metamorphic testing. In *Proceedings of the 2nd ASERC Workshop on Software Quality* (pp. 72–80). http://hdl.handle.net/1959.3/3611 **[Che04]**

- **Relevance.** The origin of MR *selection* as a research problem.
- **Key findings.** (1) Notes that for a given problem more than one MR is usually identifiable, so practitioners need selection guidance. (2) Proposes a guideline for selecting "good" MRs — MRs whose executions differ substantially from the source execution. (3) Validates through case studies.
- **Methodology.** Case studies.
- **Quality/limitations.** **No DOI.** Verified through `search_openalex` (record W2141933055, 103 citations, institutional handle `hdl.handle.net/1959.3/3611` via Swinburne). The exact venue string varies across indices — Undermind reports "Unknown Journal"; the handle record and the citing literature attribute it to the ASERC Workshop on Software Quality. **Flag: page range and venue should be re-confirmed against the PDF before the parent paper's reference list is frozen.** Guideline is heuristic; "usefulness" is defined by observed fault detection.
- **Contribution.** Establishes 2004 as the start of MR ranking-by-observed-fault-detection, and that the founding school framed the problem as *selection among candidates* rather than *adequacy of a set* — a framing that has persisted for two decades and that the parent paper is trying to break.

---

**A3.6** Mayer, J., & Guderlei, R. (2006). An empirical study on the selection of good metamorphic relations. In *30th Annual International Computer Software and Applications Conference (COMPSAC'06)* (pp. 475–484). IEEE. https://doi.org/10.1109/COMPSAC.2006.24 **[May06]**

- **Relevance.** The first independent (non-Chen-school) empirical study of MR quality.
- **Key findings.** Empirical characterisation of which MRs detect faults, independent of the originating school.
- **Methodology.** Empirical study.
- **Quality/limitations.** Abstract not retrievable through Crossref or OpenAlex in this session; findings above are characterised from title, venue and the citing literature rather than from the abstract text. **The parent paper's authors should read the PDF before making any specific claim about its findings.** 2006; small by modern standards.
- **Contribution.** Corroborates that "good MR" was operationalised as "high observed fault detection" from the mid-2000s onward, by researchers outside the originating group.

---

**A3.7** Cao, Y., Zhou, Z. Q., & Chen, T. Y. (2013). On the correlation between the effectiveness of metamorphic relations and dissimilarities of test case executions. In *2013 13th International Conference on Quality Software* (pp. 153–162). IEEE. https://doi.org/10.1109/QSIC.2013.43 **[Cao13]**

- **Relevance.** The mechanistic explanation underpinning diversity-based MR selection.
- **Key findings.** Establishes a correlation between MR effectiveness and the dissimilarity of the source and follow-up test case executions, supplying the rationale for later diversity-based selection.
- **Methodology.** Correlational empirical study.
- **Quality/limitations.** **Correlational, not causal.** Execution dissimilarity is a *proxy* for MR quality, itself validated against observed fault detection — a two-step proxy chain.
- **Contribution.** The intellectual origin of the diversity heuristic that dominates A3. Important for the parent paper because it shows the field's best mechanistic account of MR quality is a proxy correlated with fault detection, not a semantic criterion.

---

**A3.8** Srinivasan, M., & Kanewala, U. (2022). Metamorphic relation prioritization for effective regression testing. *Software Testing, Verification and Reliability, 32*(3), Article e1807. https://doi.org/10.1002/stvr.1807 **[Sri21]**

- **Relevance.** Representative modern MR prioritisation work.
- **Key findings.** (1) Two prioritisation approaches: fault-based and coverage-based. (2) Both significantly outperform ad hoc MR execution order on fault-detection effectiveness across three open-source systems. (3) Fault-based prioritisation reduces the number of source and follow-up test cases needed and shortens time-to-first-fault.
- **Methodology.** Method plus experiment on three systems.
- **Quality/limitations.** **Prioritisation, explicitly not adequacy** — it orders a given MR set, and cannot say whether the set is complete. "Fault-based" prioritisation requires a known fault set, which is the availability assumption the oracle problem denies. Undermind dates it 2021 (online-first); Crossref's issue assignment is 2022, vol. 32(3).
- **Contribution.** Clean, citable demonstration that the state of the practice for MR-set quality is *ordering*, not *sufficiency* — the precise distinction the parent paper needs to draw.

---

**A3.9** Qiu, K., Zheng, Z., Chen, T. Y., & Poon, P.-L. (2022). Theoretical and empirical analyses of the effectiveness of metamorphic relation composition. *IEEE Transactions on Software Engineering, 48*(3), 1001–1017. https://doi.org/10.1109/TSE.2020.3009698 **[Qiu22]**

- **Relevance.** The most *theoretical* treatment of MR-set structure available.
- **Key findings.** (1) MR composition automatically generates new MRs from existing ones, reducing follow-up test case count. (2) **Prior empirical work had shown some composite MRs detect fewer faults than their components** — a genuine anomaly. (3) Theoretical and empirical analysis identifies the characteristics component MRs must possess for the composite to be at least as fault-detecting, yielding a practical guideline.
- **Methodology.** Theoretical analysis plus empirical validation.
- **Quality/limitations.** The theory is about *composition operations preserving fault-detection capability*, not about set adequacy. Fault detection remains the quantity being preserved, so the theory is built on top of the same denominator.
- **Contribution.** The best evidence that MT theory can be done, and the clearest demonstration of where the field stopped: it theorises the *algebra* of MRs while leaving the *measure* on MR sets untouched. Useful as the "nearest theoretical neighbour" in the parent paper's positioning.

---

**A3.10** Xie, X., Li, Z., Chen, J., Zhang, Y., Wang, X., & Kudjo, P. K. (2024). MUT model: A metric for characterizing metamorphic relations diversity. *Software Quality Journal, 32*(4), 1413–1455. https://doi.org/10.1007/s11219-024-09689-x **[Xie24]**

- **Relevance.** An explicit *metric* on MR sets — structurally the closest thing to a measure, though of diversity rather than adequacy.
- **Key findings.** Proposes the MUT model as a metric characterising the diversity of a set of MRs.
- **Methodology.** Metric definition plus evaluation.
- **Quality/limitations.** **Abstract unavailable through both Crossref and OpenAlex** in this session; the characterisation above rests on title and venue only. **The parent paper's authors must read this before citing it substantively — it is a metric on MR sets and therefore the closest structural competitor to the parent paper's contribution.** Diversity is not adequacy: a maximally diverse MR set can still miss an entire class of semantic obligations.
- **Contribution.** **Treat as a priority read.** It is the only entry that puts a number on an MR *set* rather than on individual MRs, so a reviewer will ask how the parent paper's metric differs.

---

**A3.11** Li, Z., Chen, J., Xie, X., Chen, T. Y., & Cai, S. (2026). SAME: A similarity analysis method for evaluating metamorphic relations in testing AI systems. *Information and Software Technology, 180*, Article 108069. https://doi.org/10.1016/j.infsof.2026.108069 **[Li26h]**

- **Relevance.** The most recent MR *evaluation* method located; same group as A3.10.
- **Key findings.** Similarity-analysis-based evaluation of MRs for AI system testing (clustering/pairwise similarity machinery per index subject terms).
- **Methodology.** Method plus evaluation.
- **Quality/limitations.** **Abstract unavailable in Crossref/OpenAlex**; characterised from title, venue and index terms only. Very recent (2026), low citation base. Scope is AI systems, not scientific computing.
- **Contribution.** Evidence that MR *evaluation* is an active 2026 research front, which strengthens the parent paper's timeliness while narrowing its whitespace. Verify contents before citing.

---

**A3.12** Duque-Torres, A., Pfahl, D., Klammer, C., & Fischer, S. (2023). Exploring a test data-driven method for selecting and constraining metamorphic relations. In *2023 49th Euromicro Conference on Software Engineering and Advanced Applications (SEAA)* (pp. 370–377). IEEE. https://doi.org/10.1109/SEAA60479.2023.00063 **[Duq23b]**

- **Relevance.** Represents the "constrain the MR's applicability domain" line, adjacent to the parent paper's domain-validity concerns.
- **Key findings.** (1) Existing automatic MR-selection techniques are either domain-specific or rest on strict assumptions about the applicability of pre-defined MRs. (2) MetaTrimmer selects and constrains MRs in three steps: random test data generation, transformation with violation logging, then **manual inspection to derive constraints**. (3) Avoids the labelled-dataset requirement of prediction-model approaches.
- **Methodology.** Method plus preliminary evaluation.
- **Quality/limitations.** Explicitly preliminary. **Step 3 is manual**, so the method is not automated end-to-end. Constraints are derived *empirically from observed violations*, i.e. inferred backwards from data rather than forwards from domain semantics.
- **Contribution.** Directly relevant to the parent paper's likely position that MR applicability domains should be derived from domain semantics rather than reverse-engineered from observed behaviour. This is the concrete prior art for the data-driven alternative.

---

**A3.13** Duque-Torres, A., Pfahl, D., Klammer, C., Fischer, S., & Ramler, R. (2024). The metamorphic lighthouse: Understanding the input data space of metamorphic relations. In *2024 50th Euromicro Conference on Software Engineering and Advanced Applications (SEAA)* (pp. 379–386). IEEE. https://doi.org/10.1109/SEAA64295.2024.00064 **[Duq24b]**

- **Relevance.** Follow-on to A3.12; characterises where an MR is valid.
- **Key findings.** Characterisation of the input data space over which a given MR holds.
- **Methodology.** Empirical.
- **Quality/limitations.** Abstract not retrievable through Crossref; characterised from title and venue. Low citation base (1).
- **Contribution.** Confirms that MR *applicability domain* is a recognised open problem being attacked empirically, not semantically — supporting the parent paper's framing while establishing that the problem is already claimed territory.

---

### A4 — Mutation testing used to evaluate MRs

> This subarea is the practice the parent paper critiques. It is **well populated**, which is good for the paper: the critique has real targets, not straw ones. Note that A3.2 (Liu et al. 2024) and A5.4 (Nolasco et al. 2024) also belong here methodologically.

---

**A4.1** Jafari, F., & Nadeem, A. (2024). Measuring effectiveness of metamorphic relations for image processing using mutation testing. *Journal of Imaging, 10*(4), Article 87. https://doi.org/10.3390/jimaging10040087 **[Jaf24]**

- **Relevance.** **The single most explicit statement of the practice the parent paper attacks.** The title alone establishes the pattern.
- **Key findings.** (1) States plainly that "MRs represent the essential properties of the system under test **and are evaluated by their fault detection rates**". (2) Criticises existing MR evaluation as "not comprehensive, as very few mutation operators are used to generate very few mutants" — **so the field's own self-criticism of MR evaluation is that the mutant pool is too small, not that the mutant population is the wrong denominator.** (3) Proposes six new MRs for dilation/erosion, evaluates with eight mutation operators, reports fault-detection rates per MR (76.54%, 69.13%, etc.).
- **Methodology.** MR proposal plus mutation-based evaluation.
- **Quality/limitations.** Narrow domain (morphological image operations). The claim that using all applicable operators "shows that all the faults in the system under test are fully identified" is **a non sequitur** — exhausting the mutation operator set does not exhaust the fault space. Low citation base.
- **Contribution.** **Cite this as the paper's primary exhibit.** Its self-critique — that the problem with mutation-based MR evaluation is *too few mutants* — is precisely the framing the parent paper argues is wrong, and having a 2024 paper state it explicitly is far stronger than asserting the pattern in the abstract.

---

**A4.2** Segura, S., Hierons, R. M., Benavides, D., & Ruiz-Cortés, A. (2010). Automated test data generation on the analyses of feature models: A metamorphic testing approach. In *2010 Third International Conference on Software Testing, Verification and Validation* (pp. 35–44). IEEE. https://doi.org/10.1109/ICST.2010.20

- **Relevance.** Early, high-profile instance of mutation testing as the MR evaluation instrument.
- **Key findings.** (1) Presents MRs between feature models and their product sets. (2) **"The evaluation of our approach using mutation testing as well as real faults and tools reveals that most faults can be automatically detected within a few seconds."**
- **Methodology.** MR set plus generator; evaluated with mutation testing *and* real faults.
- **Quality/limitations.** Domain-specific (software product line feature models).
- **Contribution.** Establishes the mutation-as-yardstick practice at 2010, well before the papers the parent critique might otherwise be accused of cherry-picking. Notably it pairs mutants *with real faults*, which is better practice than most and worth acknowledging.

---

**A4.3** Saha, P., & Kanewala, U. (2019). Fault detection effectiveness of metamorphic relations developed for testing supervised classifiers. In *2019 IEEE International Conference on Artificial Intelligence Testing (AITest)* (pp. 157–164). IEEE. https://doi.org/10.1109/AITEST.2019.00019 **[Sah19]**

- **Relevance.** Title-level instance of MR quality operationalised as fault-detection effectiveness.
- **Key findings.** Measures fault-detection effectiveness of MRs developed for supervised classifiers.
- **Methodology.** Empirical fault-detection measurement.
- **Quality/limitations.** Abstract not retrievable in this session; characterised from title and venue. ML classifier domain.
- **Contribution.** Extends the pattern into ML testing, showing it is not confined to numerical software.

---

**A4.4** Ayerdi, J., Terragni, V., Jahangirova, G., Arrieta, A., & Tonella, P. (2024). GenMorph: Automatically generating metamorphic relations via genetic programming. *IEEE Transactions on Software Engineering, 50*(7), 1888–1900. https://doi.org/10.1109/TSE.2024.3407840 **[Aye23]**

- **Relevance.** State-of-the-art automated MR generation whose fitness function and reporting are both mutation-score-based.
- **Key findings.** (1) Evolutionary search for MRs over Java methods with boolean/numeric/ordered-sequence I/O. (2) Search is guided by **two fitness functions measuring false alarms and missed faults**. (3) **Results are reported as "effective MRs for 18 out of 23 methods (mutation score > 20%)"** — mutation score is literally the acceptance threshold. (4) Beats AUTOMR on fault detection in 9 of 10 methods.
- **Methodology.** Genetic programming; evaluated against Randoop and EvoSuite baselines.
- **Quality/limitations.** Restricted to simple Java method signatures; will not lift to scientific computing kernels without substantial extension. Its notion of a "good" MR is definitionally mutation-score-based, so a mutation-score-misalignment critique applies to the search objective itself, not merely to the evaluation.
- **Contribution.** **The strongest A4 exhibit after A4.1**, because here the mutation score is not just the yardstick but the *search objective*. If the denominator is misaligned, the generated MRs are optimised against a misaligned target — a sharper argument than the evaluation-only critique. Undermind dates it 2023; the TSE version of record is 2024.

---

**A4.5** Dwarakanath, A., Ahuja, M., Podder, S., Vinu, S., Naskar, A., & Koushik, M. V. (2019). *Metamorphic testing of a deep learning based forecaster* (arXiv:1907.06632). arXiv. http://arxiv.org/abs/1907.06632

- **Relevance.** Industrial application that quantifies MR quality by mutation kill rate.
- **Key findings.** (1) 19 MRs developed for a production deep-learning forecasting application, with proofs and algorithms where applicable. (2) Executing the MRs on the live application uncovered 8 previously unknown issues. (3) **"We generated hypothetical bugs, through Mutation Testing, on a reference implementation ... and found that 65.9% of the bugs were caught through the relations."**
- **Methodology.** Industrial case study plus mutation-based quantification.
- **Quality/limitations.** **arXiv preprint; no DOI resolvable.** No publisher version located. Single application; the 65.9% figure is specific to one reference implementation and one mutant pool.
- **Contribution.** Shows the practice reaching industry: a deployed system's MR set is certified by a mutation kill percentage. Cite as a preprint, with that status stated.

---

### A5 — MR derivation from domain properties

> **Direct answer to the caller's special question — "has anyone derived MRs explicitly from conservation laws, symmetries, or other equation-level structural properties?"** — **Yes, partially, and this must not be soft-pedalled.** A2.8 (Yan & Zhu 2025) formally derives MRs from the numerical models of differential equations. A5.9 (Li et al. 2026, NOETHER) explicitly organises MR derivation over symmetry, order, self-adjointness, time-reversal and limit structure in operator algebras — but that is the parent authors' own preprint, so it is self-citation, not independent prior art. **No independent, peer-reviewed work locating MR derivation in conservation laws specifically was found**, and Q8 (the targeted conservation-law query) returned no on-theme independent hit — though Q8 was also the query most degraded by geological false positives, so this negative is weaker than the others.

---

**A5.1** Chen, T. Y., Poon, P.-L., & Xie, X. (2016). METRIC: METamorphic relation identification based on the category-choice framework. *Journal of Systems and Software, 116*, 177–190. https://doi.org/10.1016/j.jss.2015.07.037 **[Che16]**

- **Relevance.** The METRIC-class method named in the brief; first systematic specification-based MR identification.
- **Key findings.** (1) Diagnoses MR identification as done "in an ad hoc manner" for lack of a systematic, specification-based methodology. (2) Derives MRs from complete test frames under the category-choice framework. (3) Tool implemented and experimentally validated.
- **Methodology.** Method, tool, experiment.
- **Quality/limitations.** Requires a category-choice specification, which scientific codes rarely have. Derivation is from the *specification's input partitioning*, not from the mathematics the program implements.
- **Contribution.** Establishes systematic MR derivation as legitimate, but anchored in specification structure rather than equation structure — the gap A5's central question probes.

---

**A5.2** Sun, C.-A., Fu, A., Poon, P.-L., Xie, X., Liu, H., & Chen, T. Y. (2021). METRIC+: A metamorphic relation identification technique based on input plus output domains. *IEEE Transactions on Software Engineering, 47*(9), 1764–1785. https://doi.org/10.1109/TSE.2019.2934848 **[Sun21]**

- **Relevance.** The METRIC successor, and a dual A4/A5 entry.
- **Key findings.** (1) METRIC under-used output-domain information; METRIC+ incorporates it. (2) Tool built; two experiment rounds over four real-life specifications confirm effectiveness and efficiency. (3) **Additional experiments compare fault-detection capability of METRIC+-generated MRs against those from μMT** — i.e. competing MR *identification* techniques are adjudicated by fault detection.
- **Methodology.** Method, tool, two experiment rounds, comparative fault-detection evaluation.
- **Quality/limitations.** Still specification-driven. Four specifications is a small evaluation base for a TSE paper. Fault-detection comparison inherits the denominator problem.
- **Contribution.** Shows that even *derivation* methods are adjudicated by fault detection — extending the parent paper's critique from evaluation into method comparison.

---

**A5.3** Kanewala, U., Bieman, J. M., & Ben-Hur, A. (2016). Predicting metamorphic relations for testing scientific software: A machine learning approach using graph kernels. *Software Testing, Verification and Reliability, 26*(3), 245–269. https://doi.org/10.1002/stvr.1594 **[Kan16]**

- **Relevance.** The main ML-based MR prediction line, targeted at scientific software.
- **Key findings.** (1) Predicts MRs from a graph-based program representation capturing control flow and data dependency. (2) A graph kernel evaluating the contribution of all paths performs best. (3) **Control flow information is more useful than data dependency information** for MR prediction.
- **Methodology.** Supervised learning over program graphs; dataset publicly released.
- **Quality/limitations.** **Predicts MRs from code structure, which is the opposite of deriving them from domain semantics.** A code-derived MR cannot be an independent oracle for that code — a circularity the parent paper may wish to note. Restricted to small numerical functions.
- **Contribution.** Establishes the code-structural derivation pole, against which the parent paper's equation-level position can be contrasted. The finding that control flow beats data dependency is itself evidence that these predictions track code shape rather than mathematical content.

---

**A5.4** Nolasco, A., Molina, F., Degiovanni, R., Gorla, A., Garbervetsky, D., Papadakis, M., Uchitel, S., Aguirre, N., & Frias, M. F. (2024). Abstraction-aware inference of metamorphic relations. *Proceedings of the ACM on Software Engineering, 1*(FSE), 450–472. https://doi.org/10.1145/3643747 **[Nol24]**

- **Relevance.** Recent FSE-track MR inference; also an A4 exhibit.
- **Key findings.** (1) MemoRIA infers MRs asserting equivalences between methods and method sequences, via object-protocol abstraction, fuzzing, and run-time validation. (2) **A SAT-based analysis eliminates redundant relations**, yielding a concise MR set — a rare explicit treatment of MR-set *redundancy*. (3) **Precision of inferred MRs is measured "in terms of mutation analysis"**; the redundancy reduction has small impact on bug-finding ability.
- **Methodology.** Inference pipeline; 22 Java subjects; compared against SBES.
- **Quality/limitations.** Java object-protocol domain; equivalence-type MRs only. Mutation analysis is again the arbiter of MR precision.
- **Contribution.** **The closest existing work to formal reasoning about MR-set structure** — SAT-based redundancy elimination is a logical operation on the set. It stops short of adequacy: removing redundancy tells you the set is not wasteful, not that it is sufficient. Good positioning contrast.

---

**A5.5** Segura, S., Durán, A., Troya, J., & Ruiz-Cortés, A. (2017). A template-based approach to describing metamorphic relations. In *2017 IEEE/ACM 2nd International Workshop on Metamorphic Testing (MET)* (pp. 3–9). IEEE. https://doi.org/10.1109/MET.2017.3 **[Seg17]**

- **Relevance.** MR patterns/templates, named in the brief's A5 scope.
- **Key findings.** Provides a template formalism for describing MRs uniformly.
- **Methodology.** Formalism proposal.
- **Quality/limitations.** Workshop paper, 7 pages; descriptive rather than generative. **Undermind supplied a malformed DOI (`10.1109/MET.2017..3`, double period); the correct DOI is `10.1109/MET.2017.3`, confirmed via Crossref.** A concrete instance of why Undermind metadata must not be trusted unverified.
- **Contribution.** Establishes that MR description can be standardised — a precondition for any set-level metric, since a metric needs comparable units.

---

**A5.6** Blasi, A., Gorla, A., Ernst, M. D., Pezzè, M., & Carzaniga, A. (2021). MeMo: Automatically identifying metamorphic relations in Javadoc comments for test automation. *Journal of Systems and Software, 181*, Article 111041. https://doi.org/10.1016/j.jss.2021.111041 **[Bla21]**

- **Relevance.** MR derivation from natural-language documentation.
- **Key findings.** (1) Derives metamorphic *equivalence* relations from Javadoc natural-language text. (2) Complements dynamic-analysis-based techniques rather than replacing them. (3) MeMo-discovered MRs detect defects when used as oracles in generated or hand-written tests.
- **Methodology.** NLP extraction plus experimental evaluation.
- **Quality/limitations.** Equivalence MRs only. Depends on documentation existing and being accurate — a poor assumption for scientific codes, which are notoriously under-documented.
- **Contribution.** Marks the documentation-derivation pole. Its inapplicability to scientific computing is itself informative for the parent paper's scope argument.

---

**A5.7** Xu, C., Terragni, V., Zhu, H., Wu, J., & Cheung, S.-C. (2024). MR-Scout: Automated synthesis of metamorphic relations from existing test cases. *ACM Transactions on Software Engineering and Methodology, 33*(6), 1–28. https://doi.org/10.1145/3656340 **[Xu23b]**

- **Relevance.** MR derivation from developer-written tests; TOSEM venue.
- **Key findings.** (1) Developer-written test cases embed domain knowledge encoding MRs; 11,000+ MR-encoded test cases discovered across 701 OSS projects. (2) Over 97% of codified MRs are high quality for automated test generation. (3) **Codified-MR-based tests "enhance the test adequacy of programs with developer-written tests, leading to 13.52% and 9.42% increases in line coverage and mutation score"** — "test adequacy" here means line coverage plus mutation score.
- **Methodology.** Mining plus synthesis plus filtering; large-scale empirical evaluation plus qualitative comprehensibility study.
- **Quality/limitations.** **Note the vocabulary collision:** this paper uses "test adequacy" to mean conventional code-coverage and mutation-score adequacy of the resulting test suite, not adequacy of the MR set. The parent paper must disambiguate these senses explicitly or a reviewer will conflate them. Java OSS domain.
- **Contribution.** Establishes at TOSEM that "test adequacy" in the MT literature currently denotes line coverage and mutation score. That is a documented, citable statement of exactly the conflation the parent paper is trying to break, at the parent paper's own target venue.

---

**A5.8** Ying, Z., Towey, D., Bellotti, A., Chua, C., & Zhou, Z. Q. (2025). Metamorphic relation patterns for metamorphic testing, exploration and robustness. *Software Testing, Verification and Reliability, 35*(2), Article e70003. https://doi.org/10.1002/stvr.70003 **[Yin25]**

- **Relevance.** The most developed MR-pattern taxonomy; structurally analogous to what an equation-level derivation framework would need.
- **Key findings.** (1) MRPs are abstractions or templates for multiple concrete MRs. (2) Provides formal definitions of relationships *between* MRPs, enabling classification, and proposes new MRPs plus a framework guiding their identification and application. (3) Constructs **"MRP family trees"** classifying previously published and newly proposed MRPs, so users can locate target MRPs for reuse, reference or inference.
- **Methodology.** Formal definitions plus taxonomy plus case studies.
- **Quality/limitations.** Patterns are abstracted from *observed* MRs — the taxonomy is inductive over the existing literature, so it inherits whatever the literature happens to contain and has no closure or completeness argument. Case-study validation only.
- **Contribution.** **The nearest independent neighbour to a structural theory of MR sets, and it must be cited as such.** It organises MR space by pattern family but never asks whether a family tree covers the obligation space of any particular program. That is exactly the seam the parent paper should claim.

---

**A5.9** Zhang, J., Sun, C.-A., Liu, H., & Dong, S. (2025). Can large language models discover metamorphic relations? A large-scale empirical study. In *2025 IEEE International Conference on Software Analysis, Evolution and Reengineering (SANER)* (pp. 24–35). IEEE. https://doi.org/10.1109/SANER64311.2025.00011

- **Relevance.** The LLM-derived-MR line named in the brief; the largest such study located.
- **Key findings.** (1) 37 SUTs from prior MT studies; prompts to gpt-3.5-turbo-1106 and gpt-4-1106-preview. (2) **29.86% and 43.79% of MR candidates were judged valid** for the corresponding SUT. (3) **24.59% and 38.63% of candidates were MRs never identified in previous studies** — i.e. LLMs surface genuinely novel MRs, but the majority of candidates are invalid.
- **Methodology.** Large-scale empirical study with expert validation.
- **Quality/limitations.** Validity judged by human experts, so it inherits expert judgement variance and no inter-rater reliability is evident from the abstract. Model versions are already superseded. **Sun and Liu also author A3.1**, so the same group is producing both the adequacy criterion and the LLM-MR evidence.
- **Contribution.** Directly relevant if the parent paper uses LLM-generated mutants or MRs: it establishes an independent, quantified baseline for LLM validity rates in MR generation (roughly 30–44%), which is a useful external calibration point.

---

### A6 — Data-level / relation-level mutation adjacent to MT

> **Caller's warning is well taken and the literature confirms it: these objects must not be conflated with program mutants.** Datamorphic testing mutates *test data* through morphisms; data-mutation-directed MR identification mutates *inputs* to suggest MRs. Neither mutates the program. The parent paper's critique of syntactic program mutation does not touch these, and a reviewer conflating them would be making a category error the paper should pre-empt.

---

**A6.1** Sun, C.-A., Jin, H., Wu, S., Fu, A., Wang, Z., & Chan, W. K. (2024). Identifying metamorphic relations: A data mutation directed approach. *Software: Practice and Experience, 54*(3), 394–418. https://doi.org/10.1002/spe.3280 **[Sun23]**

- **Relevance.** The data-mutation-directed MR acquisition work named in the brief.
- **Key findings.** (1) Guides testers to MRs via **a set of data mutation operators and template-style mapping rules**. (2) Alleviates the difficulty of MR identification while improving identification effectiveness. (3) MRs so identified show high fault-detection capability and statement coverage on numeric programs.
- **Methodology.** Method, tool, empirical study.
- **Quality/limitations.** **The mutation operators act on input data, not on the program.** Evaluation reverts to fault-detection capability and statement coverage. Undermind dates it 2023 (online-first); the issue-assigned record is 2024, vol. 54(3).
- **Contribution.** The clearest example of "mutation" meaning something entirely different inside MT. The parent paper should cite this explicitly when distinguishing its semantic *program* mutation operators from data mutation, since the terminological collision is otherwise a live reviewer objection.

---

**A6.2** Zhu, H., Liu, D., Bayley, I., Harrison, R., & Cuzzolin, F. (2019). Datamorphic testing: A method for testing intelligent applications. In *2019 IEEE International Conference on Artificial Intelligence Testing (AITest)* (pp. 149–156). IEEE. https://doi.org/10.1109/AITEST.2019.00018

- **Relevance.** The datamorphic testing origin paper named in the brief.
- **Key findings.** Introduces datamorphisms (test data transformations) and metamorphisms as separate first-class testing entities.
- **Methodology.** Method proposal.
- **Quality/limitations.** Abstract not retrievable in this session; characterised from title, venue, and the follow-on papers. AI application domain.
- **Contribution.** Establishes the datamorphism/metamorphism distinction — a vocabulary the parent paper can borrow to keep its own object types separated cleanly.

---

**A6.3** Zhu, H., Bayley, I., Liu, D., & Zheng, X. (2020). Automation of datamorphic testing. In *2020 IEEE International Conference on Artificial Intelligence Testing (AITest)* (pp. 64–72). IEEE. https://doi.org/10.1109/AITEST49225.2020.00017

- **Relevance.** The tooling maturation of A6.2.
- **Key findings.** Automates the datamorphic testing method.
- **Methodology.** Tool paper.
- **Quality/limitations.** Abstract not retrievable; characterised from title and venue.
- **Contribution.** Confirms datamorphic testing is a sustained line with tool support, not a one-off proposal — worth one sentence of disambiguation in the parent paper rather than silence.

---

## 4. EXISTING-ADEQUACY-CRITERION VERDICT for A3

### VERDICT: **`PARTIAL`**

**An MR/MT adequacy criterion exists in the published literature. The parent paper's motivating claim, as currently stated, is false and will be caught.**

### 4.1 The three nearest neighbours, and exactly how far each falls short

**Neighbour 1 — Fu, Sun, Zhang & Liu (2024), arXiv:2412.20692. NEAREST. Distance: small.**

What it does: proposes "a new set of criteria that specifies testing requirements from the perspective of necessary properties satisfied by the SUT", plus "a test adequacy measurement that evaluates the degree of adequacy based on both MRs and source inputs", validated by showing higher measured adequacy correlates with higher fault detection.

This is a real MT adequacy criterion, built on the necessary-properties view, by authors who state the same gap the parent paper claims. **Three gaps remain, and only these three:**

1. **Unit of adequacy.** The measurement is over *(MR set × source input set)* jointly — it scores a **test suite given an MR set**. It cannot score an MR set against anything external to itself. Add an MR and the score changes; ask whether the MR set covers the program's semantic obligations and the criterion is silent.
2. **No independent denominator.** The criterion's requirements are generated *from the MRs the tester already has*. There is no externally characterised obligation space, so an MR set that omits an entire class of obligations can still be measured 100% adequate. This is the specific formal weakness the parent paper should press.
3. **Fault-detection validation.** The criterion is justified by correlation with fault-detection effectiveness. The fault population remains the final arbiter, so the misaligned-denominator critique reaches the validation even though it does not reach the definition.

**Neighbour 2 — Liu, Li, Tao & Zheng (2024), QRS-C, `10.1109/QRS-C63300.2024.00072`. Distance: moderate.**

MTcoverage integrates degree of MR coverage into an adequacy criterion. It measures **how thoroughly the given MRs are exercised**, which is orthogonal to whether the MR set is right. It also **validates itself by mutation testing**, so it is simultaneously an existence proof against the parent paper's claim and the parent paper's cleanest exhibit of the critiqued practice. Additionally: QRS *Companion* track, 8 pages, 1–2 citations — real, published, citable, but not heavyweight.

**Neighbour 3 — Huang, Luo & Li (2022), IAECST, `10.1109/IAECST57965.2022.10062094`. Distance: large despite the title.**

Title says "based on test adequacy criteria" — the preposition is doing the work. This **applies** a coverage-adequacy notion to rank and select MRs; it does not propose an adequacy criterion for MR sets. It contributes a distance-based definition of MR *validity*, not of set adequacy. **Self-citation: M. Li co-authors this and the P3 preprints — declare it.**

**Also considered and rejected as adequacy criteria:** Xie et al. (2020) METTLE — "user-defined MR-based adequacy criteria" are user acceptance thresholds for selecting clustering systems. Xu et al. (2024) MR-Scout — "test adequacy" means line coverage and mutation score. Xie et al. (2024) MUT Model — a diversity metric on MR sets, structurally the closest measure but measuring diversity, not adequacy (**and I could not retrieve its abstract; this rejection is provisional and must be re-checked**).

### 4.2 Why the verdict is PARTIAL and not EXISTS

No located work defines adequacy of an MR set **against a denominator external to the MR set itself**. Every criterion found is either internal (requirements generated from the MRs in hand: Fu et al., Liu et al.) or empirical (validated against a fault or mutant population: all four). The obligation space an MR set is supposed to cover is nowhere independently characterised. That specific gap is open.

### 4.3 The adversarial queries that produced this verdict

A reviewer should be able to see the search was adversarial, i.e. aimed at *finding* the thing the paper wants to be absent:

| Query | Tool | Outcome |
|---|---|---|
| `Test Adequacy Criteria for Metamorphic Testing` | `search_dblp` | tool failure |
| `metamorphic testing adequacy criteria` | `search_dblp` | tool failure |
| `metamorphic relation adequacy criterion` | `search_openalex` | **hit — METTLE, MR-Adopt** |
| `how many metamorphic relations are enough sufficient set completeness` | `search_crossref` | zero on-theme |
| `adequacy criterion for a set of metamorphic relations sufficiency` | `search_semantic` | tool failure |
| `Test Adequacy for Metamorphic Testing: Criteria, Measurement, and Implication` | `search_arxiv` | **hit — Fu et al. 2024** |
| DOI resolution of `10.1109/QRS-C63300.2024.00072` | `get_crossref_paper_by_doi` | **hit — Liu et al. 2024** |
| DOI resolution of `10.1109/IAECST57965.2022.10062094` | `get_crossref_paper_by_doi` | **hit — Huang et al. 2022** |
| `SAME similarity analysis method evaluating metamorphic relations` | `search_openalex` | **hit — Li et al. 2026** |

**Honest caveat on search strength.** Two of the five dedicated adversarial *free-text* sweeps failed for tool reasons, and one (`search_crossref`, Q9) returned pure noise because Crossref's relevance ranking handles this phrasing badly. The three decisive A3 hits came from Undermind discovery plus targeted DOI resolution, **not** from my own free-text adversarial querying, which was weaker than intended. Given that a *single* OpenAlex adversarial query (Q5) immediately surfaced two additional near-neighbours I had not otherwise seen, **I judge it likely that further adversarial querying with working dblp and Semantic Scholar would surface more.** The verdict `PARTIAL` is safe in direction, but the enumeration of near neighbours should not be treated as exhaustive.

### 4.4 What the parent paper must now do

The claim "MR-set adequacy has no trustworthy measurement" is not defensible. Defensible reformulations, in decreasing strength:

- "Existing MT adequacy criteria measure the adequacy of a test suite relative to a **given** MR set (Fu et al., 2024; Liu et al., 2024); none measures the adequacy of the MR set itself against the program's semantic obligations."
- "Every existing MT adequacy criterion is ultimately validated against a fault or mutant population, so the field has no adequacy measure independent of the denominator whose alignment is in question."
- "MR-set quality is currently addressed by ranking, selection, diversity and composition (Chen et al., 2004; Srinivasan & Kanewala, 2022; Qiu et al., 2022; Xie et al., 2024), not by a sufficiency criterion."

**Fu et al. (2024) and Liu et al. (2024) must both be cited and engaged in the related-work section.** Omitting either would be a selective-reporting problem, not merely a completeness one — they are trivially findable by any reviewer who searches the paper's own title keywords.

---

## 5. CANONICAL-CITATION MEMO

**5.1 The original MT formulation — RESOLVED.**

The 1998 originating document is **Technical Report HKUST-CS98-01**, Department of Computer Science, The Hong Kong University of Science and Technology, by T. Y. Chen, S. C. Cheung and S. M. Yiu, 11 pages. It has **no publisher DOI** and is not a peer-reviewed publication.

**A verifiable, citable artifact exists.** S. C. Cheung self-archived it to arXiv on 2020-02-28 as **arXiv:2002.12543 [cs.SE]**, carrying an arXiv-issued DataCite DOI **`10.48550/arXiv.2002.12543`**. The arXiv record explicitly states `Report number: HKUST-CS98-01` and the comment "11 pages, Technical Report HKUST-CS98-01, Department of Computer Science, The Hong Kong University of Science and Technology". Verified via `search_openalex` (record W3008797115) and, because the item is a technical report with no DOI — the exception the caller granted — confirmed on the arXiv abstract page.

**Recommendation:** cite the arXiv record with the report number and an "original work published 1998" note, as in A1.1. Do **not** cite it as a 1998 conference paper; it never was one.

**5.2 `Chan et al. (1998)`, "Application of metamorphic testing in numerical analysis" — CANNOT BE VERIFIED. EXCLUDED.**

Undermind lists this (`[Cha98]`, 63 citations) with **no DOI**, only a Semantic Scholar link, and an implausible venue string ("International Conference on Software Engineering" — this paper is generally attributed in the citing literature to the IASTED International Conference on Software Engineering, SE'98, which is a different and much smaller venue). I attempted verification through `search_openalex` (two phrasings, Q14 and Q21), `search_crossref` (two phrasings, Q20 and one earlier), `search_semantic` (tool failure) and `search_dblp` (tool failure). **Not resolvable.** Per IRON RULE 2 it is excluded. **If the parent paper wants it, an author must obtain the physical proceedings and cite from the artifact, and should expect the venue to be IASTED SE'98, not ICSE.** This is a known mis-citation trap in the MT literature and worth guarding.

**5.3 The main surveys — ALL VERIFIED, with three metadata corrections.**

| Survey | Status | Note |
|---|---|---|
| Segura et al. (2016), TSE 42(9), 805–824 | ✓ `10.1109/TSE.2016.2532875` | Clean |
| Chen et al. (2018), CSUR 51(1), 1–27 | ✓ `10.1145/3143561` | Clean. Undermind's title "Metamorphic Testing"; the commonly used subtitle "A review of challenges and opportunities" comes from the abstract, not the Crossref title field — **use the Crossref title or expect a copy-editing query** |
| Li et al. (2025), TOSEM 34(5), 1–25 | ✓ `10.1145/3708521` | **Correction: Undermind dates it 2024; version of record is 2025-05-27.** An arXiv version (2406.05397) carries a different subtitle ("Visions for Future Research"). Cite the TOSEM record |
| Barr et al. (2015), TSE 41(5), 507–525 | ✓ `10.1109/TSE.2014.2372785` | Clean |
| Kanewala & Bieman (2014), IST 56(10), 1219–1232 | ✓ `10.1016/j.infsof.2014.05.006` | Clean |
| Altamimi, Elkawakjy & Catal (2023), JSEP 35(1) | ✓ `10.1002/smr.2509` | **Correction: Undermind dates it 2022 (online-first); issue-assigned year is 2023** |

**5.4 Other metadata corrections found while verifying — all Undermind errors.**

- **`Seg17` DOI was malformed in Undermind**: `10.1109/MET.2017..3` (double period). Correct: **`10.1109/MET.2017.3`**.
- `Lin18b` "Exploratory Metamorphic Testing for Scientific Software": Undermind says 2018; Crossref version of record is **2020**, CiSE 22(2), 78–87.
- `Yan24` Yan & Zhu STVR: Undermind says 2024; issue-assigned record is **2025**, vol. 35(1), e1912.
- `Sri21` Srinivasan & Kanewala: Undermind says 2021; issue-assigned record is **2022**, vol. 32(3), e1807.
- `Sun23` Sun et al. SPE: Undermind says 2023; issue-assigned record is **2024**, vol. 54(3), 394–418.
- `Aye23` GenMorph: Undermind says 2023; TSE version of record is **2024**, vol. 50(7), 1888–1900.
- `Che04` and `Che20` have **no publisher DOI**; `Fu24` and `Dwa19` are **arXiv-only** as verified here.

**5.5 Self-citations detected in the Undermind index — DISCLOSURE REQUIRED.**

The workspace index contains at least four artifacts by the parent paper's own author group (Meng Li, Xiaohua Yang, Jie Liu, Shiyu Yan):

- `[Li26e]` **arXiv:2605.17437v2**, "A semantic mutation metric for metamorphic relation adequacy in scientific computing programs" — verified via `search_arxiv`. **This is the parent paper's own preprint (P3).** Its abstract states the pre-registered large-effect Cliff's delta threshold was **not met** under the point-estimate criterion.
- `[Li26d]` **arXiv:2606.17529**, "Domain-Validity-Gated Metamorphic Testing of Scientific ML Surrogates" — verified via `search_openalex` (W7165219653).
- **arXiv:2605.17390**, "NOETHER: A Constructive Framework for Metamorphic Pattern Discovery from Operator Algebras" — verified via `search_openalex` (W7161917061). Directly answers A5's conservation-law/symmetry question, **but as self-citation, not independent prior art**.
- `[Hua22]` Huang, Luo & Li (2022), IAECST — M. Li is a co-author.

All four must be declared as self-citations. **NOETHER in particular must not be presented as independent evidence that equation-level MR derivation is an open problem, because it is the same group's own answer to it.**

---

## 6. 检索审计表 (Reference Verification Audit)

Tool-chain notation: `um` = Undermind (discovery only, never counted as verification); `cr-doi` = `get_crossref_paper_by_doi`; `cr` = `search_crossref`; `oa` = `search_openalex`; `ax` = `search_arxiv`; `dblp`/`sem` = failed tools; `wf` = WebFetch (granted exception, technical report only).

| # | Ref | 工具链 | 命中工具 | 状态 |
|---|---|---|---|---|
| A1.1 | Chen, Cheung & Yiu (2020/1998), arXiv:2002.12543 | um → sem(fail) → ax(noise) → oa → wf | oa + wf | ✓ tech report, no publisher DOI |
| A1.2 | Chen, Kuo, Tse & Zhou (2003), STEP | um → cr-doi | cr-doi | ✓ |
| A1.3 | Segura et al. (2016), TSE | um → cr-doi | cr-doi | ✓ |
| A1.4 | Chen et al. (2018), CSUR | um → cr-doi | cr-doi | ✓ |
| A1.5 | Chen & Tse (2021), ESEC/FSE | um → cr-doi | cr-doi | ✓ |
| A1.6 | Li et al. (2025), TOSEM | um → cr-doi → oa | cr-doi | ✓ △ year corrected 2024→2025 |
| A2.1 | Weyuker (1982), Computer Journal | cr | cr | ✓ |
| A2.2 | Barr et al. (2015), TSE | um → cr-doi → oa | cr-doi | ✓ |
| A2.3 | Patel & Hierons (2018), SQJ | oa | oa | ✓ |
| A2.4 | Kanewala & Bieman (2014), IST | um → cr-doi | cr-doi | ✓ |
| A2.5 | Chen, Feng & Tse (2002), COMPSAC | um → cr-doi | cr-doi | ✓ △ null date in Crossref |
| A2.6 | Liu, Kuo, Towey & Chen (2014), TSE | um → cr-doi | cr-doi | ✓ |
| A2.7 | He, Wang, Shi & Liu (2020), ISSTA | um → oa | oa | ✓ |
| A2.8 | Yan & Zhu (2025), STVR | um → cr-doi | cr-doi | ✓ △ year corrected 2024→2025 |
| A3.1 | **Fu, Sun, Zhang & Liu (2024), arXiv:2412.20692** | um → ax | ax | ✓ △ preprint only, no VoR found |
| A3.2 | **Liu, Li, Tao & Zheng (2024), QRS-C** | um → dblp(fail) → cr-doi | cr-doi | ✓ |
| A3.3 | **Huang, Luo & Li (2022), IAECST** | um → cr-doi | cr-doi | ✓ self-citation |
| A3.4 | Xie et al. (2020), IEEE TR (METTLE) | oa → cr-doi | cr-doi | ✓ |
| A3.5 | Chen, Huang, Tse & Zhou (2004) | um → oa | oa | △ no DOI; venue/pages need PDF confirmation |
| A3.6 | Mayer & Guderlei (2006), COMPSAC | um → cr-doi | cr-doi | ✓ △ abstract unavailable |
| A3.7 | Cao, Zhou & Chen (2013), QSIC | um → cr-doi | cr-doi | ✓ |
| A3.8 | Srinivasan & Kanewala (2022), STVR | um → cr-doi | cr-doi | ✓ △ year corrected 2021→2022 |
| A3.9 | Qiu, Zheng, Chen & Poon (2022), TSE | um → cr-doi | cr-doi | ✓ |
| A3.10 | Xie et al. (2024), SQJ (MUT Model) | um → cr-doi | cr-doi | ✓ △ abstract unavailable |
| A3.11 | Li et al. (2026), IST (SAME) | um → oa | oa | ✓ △ abstract unavailable |
| A3.12 | Duque-Torres et al. (2023), SEAA | um → oa | oa | ✓ |
| A3.13 | Duque-Torres et al. (2024), SEAA | um → cr-doi | cr-doi | ✓ △ abstract unavailable |
| A4.1 | Jafari & Nadeem (2024), J. Imaging | um → cr-doi | cr-doi | ✓ |
| A4.2 | Segura et al. (2010), ICST | oa | oa | ✓ |
| A4.3 | Saha & Kanewala (2019), AITest | um → cr-doi | cr-doi | ✓ △ abstract unavailable |
| A4.4 | Ayerdi et al. (2024), TSE (GenMorph) | um → oa | oa | ✓ △ year corrected 2023→2024 |
| A4.5 | Dwarakanath et al. (2019), arXiv:1907.06632 | ax | ax | ✓ △ preprint, no DOI |
| A5.1 | Chen, Poon & Xie (2016), JSS (METRIC) | um → cr-doi | cr-doi | ✓ |
| A5.2 | Sun et al. (2021), TSE (METRIC+) | um → oa | oa | ✓ |
| A5.3 | Kanewala, Bieman & Ben-Hur (2016), STVR | um → cr-doi | cr-doi | ✓ |
| A5.4 | Nolasco et al. (2024), PACMSE | um → cr-doi | cr-doi | ✓ |
| A5.5 | Segura et al. (2017), MET | um → oa → cr-doi | cr-doi | ✓ △ Undermind DOI malformed, corrected |
| A5.6 | Blasi et al. (2021), JSS (MeMo) | um → oa → cr-doi | cr-doi | ✓ |
| A5.7 | Xu et al. (2024), TOSEM (MR-Scout) | um → cr-doi | cr-doi | ✓ |
| A5.8 | Ying et al. (2025), STVR | um → cr-doi | cr-doi | ✓ |
| A5.9 | Zhang, Sun, Liu & Dong (2025), SANER | oa → cr-doi | cr-doi | ✓ |
| A6.1 | Sun et al. (2024), SPE | um → oa → cr-doi | cr-doi | ✓ △ year corrected 2023→2024 |
| A6.2 | Zhu et al. (2019), AITest | cr | cr | ✓ △ abstract unavailable |
| A6.3 | Zhu et al. (2020), AITest | cr | cr | ✓ △ abstract unavailable |

**Self-citation artifacts verified but NOT included in the numbered bibliography (disclosure only):**

| # | Ref | 工具链 | 命中工具 | 状态 |
|---|---|---|---|---|
| S1 | Li, Yang, Liu & Yan (2026), arXiv:2605.17437 (SMS — the P3 paper) | um → ax | ax | ✓ self |
| S2 | Li, Yang, Liu & Yan (2026), arXiv:2606.17529 (DVG-MT) | um → oa | oa | ✓ self |
| S3 | Li, Yang, Liu & Yan (2026), arXiv:2605.17390 (NOETHER) | oa | oa | ✓ self |

**Excluded for failed verification (IRON RULE 2):**

| Ref | 工具链 | 命中工具 | 状态 |
|---|---|---|---|
| Chan, Chen, Cheung, Lau & Yiu (1998), "Application of metamorphic testing in numerical analysis" | um → oa ×2 → cr ×2 → sem(fail) → dblp(fail) | **none** | ✗ EXCLUDED |
| Yan et al. (2016), "Research of Testing for Scientific Computing Software in the Area of Nuclear Power..." | um → oa → cr | **none** | ✗ EXCLUDED |

### Totals

- **Included references: 44. ✗ count among included: 0.**
- **△ (verified but with a caveat): 20.** Breakdown — 8 abstract-unavailable, 6 year/metadata corrections against Undermind, 2 preprint-only, 2 no-DOI, 1 malformed-DOI corrected, 1 venue/pages needing PDF confirmation.
- **✗ (unverifiable, therefore excluded, not cited): 2.** These are reported here rather than silently dropped.

---

## 7. Search Limitations

1. **Two of the six prescribed verification tools were non-functional for this entire session.** `search_dblp` returned an empty/omitted payload on 4 consecutive invocations across 4 distinct queries and 3 different `max_results` values (3, 5, 10, 30). `search_semantic` did the same on 3 invocations. Since dblp is the **first** link in the prescribed SE chain and is the authoritative index for conference papers without DOIs, its absence is the single largest weakness in this bibliography. It is the most likely direct cause of the Chan et al. (1998) verification failure, since dblp is exactly where a 1998 IASTED proceedings paper would be indexed. **Re-running the audit with a working dblp is the highest-value follow-up.**

2. **The adversarial A3 search was weaker than intended, and I want that on record.** Of five dedicated adversarial free-text sweeps, two failed for tool reasons and one returned pure noise. All three decisive A3 hits came from Undermind discovery plus targeted DOI resolution rather than from my own adversarial querying. The one adversarial free-text query that *did* execute cleanly (Q5, OpenAlex) immediately surfaced two near-neighbours I had not otherwise seen — which suggests the near-neighbour enumeration in §4.1 is **probably incomplete**. The `PARTIAL` verdict is safe in direction; the list supporting it is not exhaustive.

3. **No Boolean operator support.** Neither Crossref nor OpenAlex in this MCP exposes field-scoped Boolean queries. Conjunction was approximated by term stacking, disjunction by separate queries. Query *membership* is reproducible; query *ranking* is not.

4. **Severe lexical contamination on the A5 conservation-law query.** "Metamorphic" is a geology term. Q8 returned serpentinite dehydration, mid-ocean ridge faulting, metapelite mineral stability and shock-metamorphic meteorite effects. Roughly a third of returns were geological. This specific negative result — no independent conservation-law-derived MR work — is therefore **the weakest negative in this document** and should be re-run with a venue or subject filter before the parent paper relies on it.

5. **Eight included entries have no retrievable abstract** through Crossref or OpenAlex (A3.6, A3.10, A3.11, A3.13, A4.3, A6.2, A6.3, and partially A2.3). Their annotations rest on title, venue, index subject terms, and the citing literature. **A3.10 (MUT Model) is the serious one** — it is a metric on MR sets and thus the closest structural competitor to the parent paper's contribution, and I cannot tell you what it actually measures. Read it before writing related work.

6. **Fu et al. (2024) — the decisive A3 paper — was verified only as an arXiv preprint.** No version of record was resolvable in this session. Given it is nine months old at time of writing and by an established group, a peer-reviewed version may well exist and would strengthen the challenge to the parent paper's claim. **Re-check before submission.**

7. **Undermind DS1 and DS2 were both scoped by a Chinese-language goal statement emphasising nuclear science and numerical-error bounds.** Both returned large volumes of code-verification and V&V literature (MMS, Richardson extrapolation, CTF/RELAP verification) that I excluded as off-theme for A. That exclusion is defensible for Theme A but means **DS1/DS2 were not optimally aimed at Theme A**, and the MT-generic literature is likely under-sampled relative to what a Theme-A-specific deep search would return.

8. **Citation counts in this document are unstable and should not be quoted.** Crossref, OpenAlex and Undermind disagree systematically — e.g. Segura et al. (2016) is 505 in Crossref and 580 in Undermind; Chen et al. (2018) is 435 versus 417; Barr et al. (2015) is 887 versus 1091 versus 1171.

9. **I did not read any full texts.** All annotations derive from abstracts and metadata. Claims attributed to papers are claims *their abstracts make*, not claims I verified against their contents. This is a real limit on §4's characterisation of how far each near-neighbour falls short — that assessment rests on abstract-level reading of Fu et al. and Liu et al.

---

## 8. Handoff Notes

- The A3 verdict is **`PARTIAL`, not `NO_EXISTING_MR_ADEQUACY_CRITERION`.** Fu et al. (2024, arXiv:2412.20692) and Liu et al. (2024, QRS-C) both propose MT adequacy criteria by name; Fu et al. additionally states the same gap the parent paper claims and grounds its criteria in the necessary-properties view. Both are trivially findable from the parent paper's own title keywords.

- Liu et al. (2024) validates its MT adequacy criterion **by mutation testing**, and Ayerdi et al. (2024) uses **mutation score as the search objective** for MR generation. Both facts are recorded in their abstracts.

- Yan & Zhu (2025, STVR) claims to "formally derive metamorphic relations from the numerical models of differential equations", so equation-level MR derivation has independent published prior art. The only located work organising MR derivation over conservation laws and symmetry (NOETHER, arXiv:2605.17390) is the parent authors' own preprint, alongside two further self-citations (arXiv:2605.17437, arXiv:2606.17529) and one self-co-authored A3 entry (Huang, Luo & Li 2022).

- Nine Undermind metadata defects were found during verification: one malformed DOI (`10.1109/MET.2017..3`), six year discrepancies against version-of-record, one implausible venue string (Chan et al. 1998 listed as ICSE), and one "Unknown Journal". Two Undermind records could not be verified at all and were excluded.

- Two prescribed tools (`search_dblp`, `search_semantic`) were dead for this entire session, and the one adversarial free-text query that executed cleanly immediately found two near-neighbours I had missed. **My recommendation is a targeted re-run of §4.3's adversarial queries once dblp and Semantic Scholar are working, before this verdict is treated as settled.** I did not launch a new Undermind deep search, per instruction; whether the residual Theme-A-generic gap (noted in Limitation 7) warrants one is the caller's call, not mine.
