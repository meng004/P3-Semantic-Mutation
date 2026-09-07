# Phase 2 Bibliography — Theme B: Mutation Testing Constructs, Semantic Mutation, and Mutation-Score Validity

**Agent:** `bibliography_agent` (ARS deep-research pipeline, Phase 2 INVESTIGATION)
**Target venue of parent paper:** ACM TOSEM
**Date compiled:** 2026-09-07
**Scope:** Theme B only (B1–B6). No synthesis, no gap analysis, no paper sections.

---

## 1. Search Strategy

### 1.1 Two-tool division of labour

| Role | Tool | Function |
|---|---|---|
| Discovery (现状) | `user-undermind` | Ranked candidate harvesting from one pre-launched deep search |
| Verification (文献核对) | `user-paper-search` | Independent existence + metadata confirmation for every entry |

**Iron rule applied:** no entry below appears on Undermind's authority alone. Every reference was independently re-resolved through a `user-paper-search` call (CrossRef DOI resolution, CrossRef title search, arXiv search, or OpenAlex), and the metadata printed here is what the verification tool returned, not what Undermind reported. Where the two disagreed, the verification tool wins and the discrepancy is recorded.

### 1.2 Undermind deep search consumed

- **Workspace:** `d9baef75-52ff-4860-b661-6d7a9e647f42`
- **Search name:** `/mutation score construct validity oracle adequacy semantic mutation`
- **Status:** launched 2026-09-07 10:32, completed 10:35 (polled with `status_only=True`, then read in full)
- **Yield:** 177 ranked papers; pages 1–100 read at `detail_level='standard'`; `detail_level='full'` used for the B3 cluster and for two counter-evidence items
- **DOIs pulled:** 67 cite keys via `get_paper_info(show_doi=true)` across two batches
- **Additional deep searches launched:** **none** (cost constraint respected)

### 1.3 Direct `user-paper-search` queries (exact strings)

All CrossRef queries are bibliographic free-text queries (the endpoint does not support Boolean operators); Boolean intent was encoded by term co-occurrence — author surnames plus distinctive title tokens plus venue name — which CrossRef scores as an implicit AND-weighted relevance match.

| # | Tool | Exact query string | Purpose |
|---|---|---|---|
| Q1 | `search_dblp` | `Semantic mutation testing` | B3 primary — **returned empty output twice** |
| Q2 | `search_crossref` | `Semantic mutation testing Clark Dan Hierons` | B3 primary lineage |
| Q3 | `search_crossref` | `Trivial Compiler Equivalence large scale empirical study equivalent mutant detection Papadakis` | B5 equivalent mutants |
| Q4 | `search_crossref` | `Threats to the validity of mutation-based test assessment Papadakis Henard Harman` | B5 subsumption threats |
| Q5 | `search_crossref` | `How effective are mutation testing tools empirical analysis Java mutation testing tools manual analysis real faults Kintis` | B5 tool disagreement |
| Q6 | `search_crossref` | `State of Mutation Testing at Google Petrovic Ivankovic` | B5 industrial filtering |
| Q7 | `search_crossref` | `Checked coverage indicator oracle quality Schuler Zeller` | B6 oracle assessment |
| Q8 | `search_crossref` | `Programs tests and oracles the foundations of testing revisited Staats Whalen Heimdahl` | B6 oracle theory |
| Q9 | `search_crossref` | `Test oracle assessment and improvement Jahangirova Clark Harman Tonella` | B6 oracle assessment |
| Q10 | `search_crossref` | `muBERT mutation testing using pre-trained language models Degiovanni Papadakis` | B4 LLM mutants |
| Q11 | `search_arxiv` | `LLMorpheus mutation testing large language models` | B4 LLM mutants |
| Q12 | `search_crossref` | `mutation testing scientific computing software numerical programs oracle problem` | B4 scientific code — **low yield, see §7** |
| Q13 | `search_crossref` | `Syntactic vs semantic similarity of artificial and real faults in mutation testing studies Ojdanic` | B2 counter-evidence |
| Q14 | `search_crossref` | `Analyzing the validity of selective mutation with dominator mutants Kurtz Ammann Offutt` | B5 subsumption |
| Q15 | `search_crossref` | `DeepCrime mutation testing of deep learning systems based on real faults Humbatova Jahangirova Tonella` | B4 DL mutation |
| Q16 | `search_crossref` | `Mutation-Driven Generation of Unit Tests and Oracles IEEE Transactions on Software Engineering Fraser Zeller` | B6 — disambiguating ISSTA vs TSE versions |
| Q17 | `search_crossref` | `Automatically detecting equivalent mutants and infeasible paths Offutt Pan Software Testing Verification Reliability` | B5 equivalent mutants |
| Q18 | `search_crossref` | `Hook Kelly mutation sensitivity testing scientific software code faults` | B4 scientific code — **high yield** |
| Q19 | `search_crossref` | `Introduction to Software Testing Ammann Offutt Cambridge University Press` | B1 textbook |
| Q20 | `search_openalex` | `Mutation Testing Advances: An Analysis and Survey` | B1 — CrossRef returned an empty author list |
| Q21 | `search_openalex` | `Semantic mutation testing Clark Dan Hierons Science of Computer Programming` | B3 — online-first vs print year |
| Q22 | `search_crossref` | `An Exploratory Study on Using Large Language Models for Mutation Testing Wang Zhang` | B4 LLM mutants |
| Q23 | `search_crossref` | `Establishing Theoretical Minimal Sets of Mutants Ammann Delamaro Offutt` | B5 denominator |
| Q24 | `search_crossref` | `Reducing the cost of mutation testing an empirical study Wong Mathur Journal of Systems and Software` | B5 selective mutation |
| Q25 | `search_unpaywall` | `10.1016/j.scico.2011.03.011` | B3 — attempt at full text for the disambiguation memo |
| Q26 | `search_arxiv` | `Bo Wang mutation testing large language models exploratory study mutants` | B4 fallback |
| Q27 | `search_semantic` | `An Exploratory Study on Using Large Language Models for Mutation Testing` | B4 fallback — **returned empty output** |
| Q28 | `search_base` | `Semantic mutation testing Clark Dan Hierons` | B3 OA fallback — **returned empty output** |

Plus **41 direct `get_crossref_paper_by_doi` calls**, one per DOI harvested from Undermind or from a title search, used as the primary verification instrument.

### 1.4 Priority chain and degradation policy

Declared chain for software engineering: `search_dblp` → `search_arxiv` → `search_crossref`, with `get_crossref_paper_by_doi` preferred whenever a DOI was in hand; general fallback `search_openalex` → `search_semantic` → `search_google_scholar`.

**Deviation, declared:** `search_dblp` returned empty output on both attempts (Q1 at `max_results=25` and at `max_results=10`), as did `search_semantic` (Q27) and `search_base` (Q28). The chain therefore ran as `get_crossref_paper_by_doi` / `search_crossref` → `search_arxiv` → `search_openalex` → `search_unpaywall`. This is a tool-availability degradation, not a methodological choice; dblp coverage of SE conference proceedings would normally have been the first stop. **`WebSearch` and `WebFetch` were never invoked.** The one textbook in the list (Ammann & Offutt) was resolved through CrossRef rather than a publisher page, so even the textbook exception was not needed.

### 1.5 Inclusion / exclusion criteria

**Included if all hold:**
1. Existence independently confirmed by a `user-paper-search` call returning title, authors and venue.
2. Substantively about one of B1–B6: mutation-testing foundations/surveys; mutant–real-fault validity; semantic mutation testing; non-default mutant generation; threats to the mutation-score construct; or mutation used to assess oracles/assertions/contracts rather than inputs.
3. Peer-reviewed venue, or arXiv cs.SE preprint with a verifiable identifier.
4. English language.
5. Document type: journal article, conference/workshop paper, book, book chapter, or arXiv preprint.

**Excluded:**
- Doctoral theses and habilitations without a resolvable DOI (`Hua16b`, `Jah19`, `Che19b`, `Sch11c`, `Aic12b`, `Shr10`, `Zha16b`) — content is superseded by the authors' peer-reviewed papers, which are included instead.
- Items where Undermind supplied a DOI that failed or misresolved on verification: `Acr80` "On mutation" (Undermind DOI `10.1002/9781118662779.ch1` does not correspond to Acree's 1980 Georgia Tech thesis; **excluded as gray zone**), `Gop14` "Mutant census" (no DOI, Semantic Scholar link only; excluded), `Agr06` "Design of mutant operators for the C programming language" (Purdue technical report, no DOI; excluded), `Gol24` IronSpec (no DOI returned; excluded), `Mac17` "Quality Evaluation of Test Oracles Using Mutation" (no DOI, no venue; excluded despite high topical relevance — see §7).
- `Jia00` in the Undermind list — this is a duplicate ghost record of Jia & Harman's TSE survey with no year and a mangled title; excluded as a database artefact, the real record is included.
- **Author self-citation flagged, not included:** `Li26e` "A semantic mutation metric for metamorphic relation adequacy in scientific computing programs" (2026, arXiv, DOI `10.48550/arXiv.2605.17437`, first author Meng Li) surfaced at r=1.180 in the deep search. This is the parent project's own preprint. It is excluded from the bibliography as prior art and reported in §8.

**Date range:** no lower bound (1977 earliest included); upper bound 2026-09-07. Pre-2000 classics were deliberately sought by direct query because the deep search under-weighted them relative to 2014–2024 empirical work.

---

## 2. PRISMA-style flow

| Stage | Count |
|---|---|
| **Identification** | |
| Records from Undermind deep search (1 search) | 177 |
| Records screened in detail from that search (pages 1–100) | 100 |
| Records from direct `user-paper-search` queries (Q1–Q28) | 63 returned; 31 topically on-theme |
| Records from targeted DOI resolution | 41 |
| **Total records identified** | 218 (177 + 41 new from direct queries) |
| **De-duplication** | |
| Duplicates removed (same work across Undermind + CrossRef + OpenAlex) | 34 |
| Version pairs consolidated but both recorded (conference + journal of same work) | 5 |
| **Records after de-duplication** | 184 |
| **Screening** | |
| Screened on title + abstract/metadata | 184 |
| Excluded — off-theme (model-based mutation for test generation, SBST, fault localisation, smart contracts, spreadsheets, general ML testing) | 96 |
| **Records sought for verification** | 88 |
| **Eligibility** | |
| Excluded — thesis/habilitation without DOI | 7 |
| Excluded — no resolvable identifier / gray zone | 5 |
| Excluded — database artefact (ghost duplicate record) | 1 |
| Excluded — author self-citation (parent project preprint) | 1 |
| Excluded — verified but redundant with a stronger included entry | 17 |
| **Included in bibliography** | **57 works** (**40 fully annotated** in §3, **17 verified-supplementary** in §3.7) |
| **Verification failures (✗)** | **0** |

Version pairs recorded as one entry each with both records verified: Clark/Dan/Hierons ICSTW 2010 + SCP 2013; Fraser & Zeller ISSTA 2010 + TSE 2012; Tip et al. arXiv 2024 + TSE 2025; Kintis et al. SCAM 2016 + EMSE 2018; Ammann & Offutt 1st ed. 2008 + 2nd ed. 2016.

---

## 3. Annotated Bibliography

Citation format: **APA 7.0**. Where CrossRef's online-first date and the print volume year differ, both are stated.

---

### B1. Foundations and surveys (7 annotated)

---

**B1-1.** Hamlet, R. G. (1977). Testing programs with the aid of a compiler. *IEEE Transactions on Software Engineering, SE-3*(4), 279–290. https://doi.org/10.1109/TSE.1977.231145

- **Relevance:** One of the two independent 1977–1978 origin points of mutation testing. Establishes the compiler-assisted generation of program variants as a test-data-adequacy device.
- **Key findings:** (1) A compiler can be extended to systematically generate perturbed program variants for use as a test-adequacy yardstick. (2) The adequacy question is framed as whether the test data distinguishes the program under test from its variants.
- **Methodology:** Conceptual/technique paper with a compiler-based realisation.
- **Quality/limitations:** No empirical evaluation by modern standards; the population of variants is defined by what the compiler modification happens to generate, which is precisely the denominator question the parent paper raises.
- **Contribution to Theme B:** Documents that from the very first formulation, the mutant population was defined by an implementation artefact (a compiler pass), not by a fault theory.

---

**B1-2.** DeMillo, R. A., Lipton, R. J., & Sayward, F. G. (1978). Hints on test data selection: Help for the practicing programmer. *Computer, 11*(4), 34–41. https://doi.org/10.1109/C-M.1978.218136

- **Relevance:** The canonical statement of the competent-programmer hypothesis and the coupling effect — the two assumptions that license mutation score as a proxy for fault detection.
- **Key findings:** (1) Competent programmers write programs that are "close to correct", so faults are small syntactic deviations. (2) Coupling effect: test data that detects simple faults will also detect complex ones. (3) Therefore local syntactic perturbations form a defensible test-adequacy population.
- **Methodology:** Position/argument paper with illustrative examples.
- **Quality/limitations:** Both hypotheses are stated informally and were not empirically tested here; the paper's own framing is about *test data* selection, not oracle assessment.
- **Contribution to Theme B:** This is the load-bearing citation for the claim that a population of local code edits is an appropriate adequacy denominator. Any construct-validity argument must engage this text directly.

---

**B1-3.** Budd, T. A., DeMillo, R. A., Lipton, R. J., & Sayward, F. G. (1980). Theoretical and empirical studies on using program mutation to test the functional correctness of programs. In *Proceedings of the 7th ACM SIGPLAN-SIGACT Symposium on Principles of Programming Languages (POPL '80)* (pp. 220–233). ACM Press. https://doi.org/10.1145/567446.567468

- **Relevance:** The first combined theoretical-plus-empirical treatment; frames mutation as testing *functional correctness*, which is the strongest form of the claim.
- **Key findings:** (1) Theoretical conditions under which passing a mutation-adequate test set implies functional correctness are stated. (2) Empirical trials on real programs accompany the theory.
- **Methodology:** Mixed theory + early empirical study.
- **Quality/limitations:** Programs are small by contemporary standards; the correctness result holds under strong assumptions about the fault space.
- **Contribution to Theme B:** Supplies the formal ambition — mutation adequacy as evidence of functional correctness — against which the construct-misalignment argument must be positioned.

---

**B1-4.** Offutt, A. J. (1992). Investigations of the software testing coupling effect. *ACM Transactions on Software Engineering and Methodology, 1*(1), 5–20. https://doi.org/10.1145/125489.125473

- **Relevance:** The main empirical defence of the coupling effect, and therefore the strongest available support for the standard construct.
- **Key findings:** (1) All experimental results supported the coupling effect over the class of faults studied. (2) Test sets detecting simple faults were sensitive enough to detect more complex faults. (3) Conclusion drawn: explicitly testing for simple faults implicitly tests for complicated ones.
- **Methodology:** Controlled empirical investigation over a specific fault class, with first-order and higher-order fault comparison.
- **Quality/limitations:** Scoped to "a specific class of software faults"; the coupling claim is about *faults*, not about semantic obligations expressed as equations.
- **Contribution to Theme B:** **Counter-evidence.** This is the paper a reviewer will cite to argue the syntactic denominator is well founded. See §5.

*Companion record verified:* Offutt, A. J. (1989). The coupling effect: Fact or fiction. In *Proceedings of the ACM SIGSOFT '89 Third Symposium on Software Testing, Analysis, and Verification (TAV3)* (pp. 131–140). ACM Press. https://doi.org/10.1145/75308.75324

---

**B1-5.** Ammann, P., & Offutt, J. (2016). *Introduction to software testing* (2nd ed.). Cambridge University Press. https://doi.org/10.1017/9781316771273

- **Relevance:** The standard textbook treatment; defines mutation as one instance of a general "apply well-defined criteria to a model of the software" framework, and supplies the canonical operator vocabulary students and tool builders inherit.
- **Key findings (as characterised in the publisher's own description):** (1) Testing is framed as applying a small number of general-purpose criteria to a structure or model of the software. (2) Mutation is presented as grammar-based testing applied to the program grammar.
- **Methodology:** Textbook; consolidation of prior literature.
- **Quality/limitations:** Pedagogical, not evaluative; operator catalogs presented as settled.
- **Contribution to Theme B:** Establishes that the discipline's *teaching* definition of mutation is explicitly syntactic — mutation as grammar perturbation — which is the definitional anchor the parent paper contests.

*First edition also verified:* Ammann, P., & Offutt, J. (2008). *Introduction to software testing*. Cambridge University Press. https://doi.org/10.1017/CBO9780511809163

---

**B1-6.** Jia, Y., & Harman, M. (2011). An analysis and survey of the development of mutation testing. *IEEE Transactions on Software Engineering, 37*(5), 649–678. https://doi.org/10.1109/TSE.2010.62

- **Relevance:** The field's most-cited survey; the reference taxonomy of operators, tools, cost-reduction strategies, and the equivalent-mutant problem.
- **Key findings:** (1) Comprehensive developmental history and classification of mutation techniques. (2) Cost reduction and equivalent-mutant detection identified as the two structural obstacles. (3) Trend analysis of the literature to 2009.
- **Methodology:** Systematic survey.
- **Quality/limitations:** Coverage ends around 2009, predating the entire mutant-vs-real-fault validity debate.
- **Contribution to Theme B:** Defines "the default first-order catalog" that B4 and B5 push against.

---

**B1-7.** Papadakis, M., Kintis, M., Zhang, J. M., Jia, Y., Le Traon, Y., & Harman, M. (2019). Mutation testing advances: An analysis and survey. In *Advances in Computers* (Vol. 112, pp. 275–378). Elsevier. https://doi.org/10.1016/bs.adcom.2018.03.015

- **Relevance:** The successor survey; the one that explicitly foregrounds validity threats rather than only technique taxonomy.
- **Key findings:** (1) Consolidates the post-2010 empirical validity literature. (2) Treats equivalent, redundant and subsumed mutants as first-class measurement problems. (3) Surveys mutation's use beyond test-input assessment.
- **Methodology:** Systematic survey (191-paper class of coverage in the associated literature).
- **Quality/limitations:** CrossRef's record for this DOI returns an **empty author list**; the author list above was confirmed independently via OpenAlex (`W2725449579`). Online-first date 2018-05-07; the print volume is dated 2019.
- **Contribution to Theme B:** The single best entry point for B5, and the source most likely to be cited against a claim that construct threats are under-recognised — they are recognised, at length, by the field's own survey.

---

### B2. Do mutants represent real faults? (10 annotated)

---

**B2-1.** Daran, M., & Thévenod-Fosse, P. (1996). Software error analysis: A real case study involving real faults and mutations. In *Proceedings of the 1996 ACM SIGSOFT International Symposium on Software Testing and Analysis (ISSTA '96)* (pp. 158–171). ACM. https://doi.org/10.1145/229000.226313

- **Relevance:** The earliest direct empirical comparison of mutant-induced errors against real faults, on safety-critical industrial code.
- **Key findings:** (1) Errors produced by mutants and by real faults were comparable in their observable error mechanisms. (2) Supports using mutants as fault surrogates for the studied system.
- **Methodology:** Case study on a real industrial program with a documented real-fault set.
- **Quality/limitations:** Single system, small fault set; CrossRef stores the title in truncated form as "Software error analysis" — the full subtitle is taken from the proceedings record and is reflected in the Undermind and citation records.
- **Contribution to Theme B:** **Counter-evidence.** Nuclear/safety-adjacent context makes it directly citable against a scientific-computing-specific misalignment claim. See §5.

---

**B2-2.** Andrews, J. H., Briand, L. C., & Labiche, Y. (2005). Is mutation an appropriate tool for testing experiments? In *Proceedings of the 27th International Conference on Software Engineering (ICSE '05)* (pp. 402–411). ACM Press. https://doi.org/10.1145/1062455.1062530

- **Relevance:** The paper that legitimised mutants as a substitute for real faults in controlled testing experiments.
- **Key findings:** (1) Generated mutants gave fault-detection-rate estimates comparable to real faults. (2) Hand-seeded faults were *less* representative than mutants. (3) Mutation is therefore endorsed as an experimental instrument.
- **Methodology:** Controlled experiment comparing detection rates across mutants, hand-seeded faults, and real faults.
- **Quality/limitations:** Subject programs are the Siemens suite plus `space`; no control for test-suite size in the primary analysis.
- **Contribution to Theme B:** **Counter-evidence**, and the historical reason mutation score became the default adequacy instrument in empirical SE.

*Journal extension verified:* Andrews, J. H., Briand, L. C., Labiche, Y., & Namin, A. S. (2006). Using mutation analysis for assessing and comparing testing coverage criteria. *IEEE Transactions on Software Engineering, 32*(8), 608–624. https://doi.org/10.1109/TSE.2006.83

---

**B2-3.** Namin, A. S., & Andrews, J. H. (2009). The influence of size and coverage on test suite effectiveness. In *Proceedings of the Eighteenth International Symposium on Software Testing and Analysis (ISSTA '09)* (pp. 57–68). ACM. https://doi.org/10.1145/1572272.1572280

- **Relevance:** Introduces test-suite size as the confounder that dominates naive adequacy-vs-effectiveness correlations.
- **Key findings:** (1) Both size and coverage independently influence effectiveness. (2) Correlations reported without size control are not interpretable as adequacy-criterion quality.
- **Methodology:** Statistical modelling over generated suites.
- **Quality/limitations:** Uses mutants as the effectiveness ground truth, which is circular for our purposes.
- **Contribution to Theme B:** Establishes the methodological requirement that any mutation-score claim must survive size control — directly relevant to how an MR-set adequacy metric should be evaluated.

---

**B2-4.** Just, R., Jalali, D., Inozemtseva, L., Ernst, M. D., Holmes, R., & Fraser, G. (2014). Are mutants a valid substitute for real faults in software testing? In *Proceedings of the 22nd ACM SIGSOFT International Symposium on Foundations of Software Engineering (FSE 2014)* (pp. 654–665). ACM. https://doi.org/10.1145/2635868.2635929

- **Relevance:** The reference study on mutant–real-fault coupling, using 357 real faults from Defects4J-class subjects.
- **Key findings:** (1) Mutant detection correlated with real-fault detection, and the correlation was stronger than for statement coverage. (2) The correlation held after controlling for test-suite size. (3) A residual fraction of real faults was not coupled to any mutant, and the authors identify missing operator classes.
- **Methodology:** Large-scale empirical study over real faults with size-controlled analysis.
- **Quality/limitations:** Java only; the uncoupled residual is exactly where domain-specific fault classes would live.
- **Contribution to Theme B:** **Counter-evidence, and the strongest single obstacle to the parent paper's thesis.** See §5.

---

**B2-5.** Inozemtseva, L., & Holmes, R. (2014). Coverage is not strongly correlated with test suite effectiveness. In *Proceedings of the 36th International Conference on Software Engineering (ICSE 2014)* (pp. 435–445). ACM. https://doi.org/10.1145/2568225.2568271

- **Relevance:** The size-control result that reset the field's expectations for *coverage* metrics and set the template later applied to mutation score.
- **Key findings:** (1) Coverage correlates with effectiveness when suite size is uncontrolled. (2) The correlation weakens sharply once size is held fixed. (3) Coverage is therefore not by itself a good adequacy indicator.
- **Methodology:** Large-scale study over five Java systems with randomly generated suites of controlled size.
- **Quality/limitations:** Uses mutants as the effectiveness proxy — an acknowledged circularity.
- **Contribution to Theme B:** Supplies the methodological playbook that B2-7 and B2-10 apply to mutation score itself.

---

**B2-6.** Chekam, T. T., Papadakis, M., Le Traon, Y., & Harman, M. (2017). An empirical study on mutation, statement and branch coverage fault revelation that avoids the unreliable clean program assumption. In *Proceedings of the 39th International Conference on Software Engineering (ICSE 2017)* (pp. 597–608). IEEE. https://doi.org/10.1109/ICSE.2017.61

- **Relevance:** Identifies and removes the "clean program assumption" — the practice of measuring adequacy on the *fixed* program rather than the faulty one.
- **Key findings:** (1) The clean program assumption materially distorts prior mutation-vs-coverage comparisons. (2) Under a corrected design, mutation still reveals more faults than statement or branch coverage. (3) Fault revelation improves substantially only at very high mutation-score levels.
- **Methodology:** Controlled study on real faults with the assumption explicitly removed.
- **Quality/limitations:** Effect sizes depend on the high-score regime, which is rarely reached in practice.
- **Contribution to Theme B:** **Counter-evidence.** A methodologically careful defence of mutation score's predictive value.

---

**B2-7.** Papadakis, M., Shin, D., Yoo, S., & Bae, D.-H. (2018). Are mutation scores correlated with real fault detection? A large scale empirical study on the relationship between mutants and real faults. In *Proceedings of the 40th International Conference on Software Engineering (ICSE 2018)* (pp. 537–548). ACM. https://doi.org/10.1145/3180155.3180183

- **Relevance:** The principal *negative* result on mutation-score construct validity, and the closest published analogue of the parent paper's argument.
- **Key findings:** (1) A statistically significant mutant–real-fault correlation exists but is **weak** once test-suite size is accounted for. (2) The relationship is much weaker than the Andrews-class and Just-class literature had suggested. (3) Mutation score is a poor predictor of real-fault detection at the granularity practitioners use it.
- **Methodology:** Large-scale study over Defects4J-class real faults with explicit size control.
- **Quality/limitations:** Contested on statistical grounds by B2-8; conclusions are sensitive to how size is handled.
- **Contribution to Theme B:** The load-bearing prior art for "mutation score is not the construct you think it is". The parent paper must distinguish its equation-level argument from this test-suite-level argument.

---

**B2-8.** Chen, Y. T., Gopinath, R., Tadakamalla, A., Ernst, M. D., Holmes, R., Fraser, G., Ammann, P., & Just, R. (2020). Revisiting the relationship between fault detection, test adequacy criteria, and test set size. In *Proceedings of the 35th IEEE/ACM International Conference on Automated Software Engineering (ASE 2020)* (pp. 237–249). ACM. https://doi.org/10.1145/3324884.3416667

- **Relevance:** A direct methodological rebuttal of the way B2-7 and the size-control literature treat test-set size.
- **Key findings (from the paper's own abstract):** (1) Prior analyses of fault detection / adequacy / size are contradictory, and the contradiction is a design error, not a substantive disagreement. (2) **Test set size is neither a confounding variable, as previously suggested, nor an independent variable that should be experimentally manipulated.** (3) Proposes "probabilistic coupling" for assessing whether a set of test goals is representative of a given fault. (4) Empirically compares coverage-based, mutation-based and random testing on an equal footing.
- **Methodology:** Methodological critique plus a re-analysis under a corrected design.
- **Quality/limitations:** Authored substantially by the Just group, i.e. by parties to the original dispute.
- **Contribution to Theme B:** **Counter-evidence of the most dangerous kind for the parent paper.** If size is not a confounder, then the headline "weak correlation after controlling for size" result loses much of its force. See §5.

---

**B2-9.** Gay, G., & Salahirad, A. (2023). How closely are common mutation operators coupled to real faults? In *2023 IEEE Conference on Software Testing, Verification and Validation (ICST)* (pp. 129–140). IEEE. https://doi.org/10.1109/ICST57152.2023.00021

- **Relevance:** Operator-level, rather than aggregate, coupling analysis — the granularity at which "the denominator is arbitrary" can be tested.
- **Key findings (from the paper's own abstract):** (1) Of 32,002 mutants from 31 operators evaluated against 144 real faults, **9.92% of mutants are strongly coupled to real faults**. (2) **51.03% of faults have at least one strongly coupled mutant.** (3) Coupling is highly uneven across operators; some operators mainly produce non-compiling, undetected, or misleadingly-failing mutants. (4) Operator filtering on coupling could yield significant cost savings.
- **Methodology:** Large-scale empirical coupling study with a graded coupling scale based on number of failing tests and reasons for failure.
- **Quality/limitations:** Coupling scale is the authors' own construction; single fault benchmark.
- **Contribution to Theme B:** The most precise published evidence that the standard mutant population is dominated by mutants with no real-fault correspondence — i.e. that the denominator is largely inert.

---

**B2-10.** Ojdanić, M., Garg, A., Khanfir, A., Degiovanni, R., Papadakis, M., & Le Traon, Y. (2023). Syntactic versus semantic similarity of artificial and real faults in mutation testing studies. *IEEE Transactions on Software Engineering, 49*(7), 3922–3938. https://doi.org/10.1109/TSE.2023.3277564

- **Relevance:** Directly addresses the syntactic/semantic distinction that the parent paper's whole argument turns on.
- **Key findings:** (1) Syntactic similarity between an artificial fault and a real fault does not predict semantic similarity. (2) Studies that select mutants by syntactic resemblance to real faults are therefore not selecting semantically representative ones. (3) Semantic and syntactic notions of "realistic mutant" come apart empirically.
- **Methodology:** Large-scale empirical comparison of syntactic and semantic distance measures over artificial and real faults.
- **Quality/limitations:** "Semantic similarity" here is operationalised via program behaviour on a test set, not via a declared specification.
- **Contribution to Theme B:** The strongest available published support for separating syntactic mutant generation from semantic fault meaning — though note that its notion of "semantic" is behavioural, not equation-level.

*Also verified and directly on-theme:* Ahmed, Z., Schwass, E., Herbold, S., Trautsch, F., & Grabowski, J. (2024). A new perspective on the competent programmer hypothesis through the reproduction of real faults with repeated mutations. *Software Testing, Verification and Reliability, 34*(3), e1874. https://doi.org/10.1002/stvr.1874 — finds that "while the competent programmer hypothesis seems to be true, mutation testing is missing important operators to generate representative real-world faults" (835 real faults, Defects4J 2.0.0).

*Also verified:* Zhang, P., Wang, Y., Liu, X., Lu, Z., Yang, Y., Li, Y., Chen, L., Wang, Z., Sun, C.-A., Yu, X., & Zhou, Y. (2024). Assessing effectiveness of test suites: What do we know and what should we do? *ACM Transactions on Software Engineering and Methodology, 33*(4), Article 96, 1–32. https://doi.org/10.1145/3635713 (online-first 2023) — **counter-evidence**: under their ASSENT framework and real faults, "mutation score, and subsuming mutation score are the best metrics to quantify test suite effectiveness", while using mutants instead of real faults overestimates effectiveness by more than 20%.

*Also verified:* Lu, Z., Wang, Y., Rong, Y., Huang, Y., Wang, X., Zhang, P., Gao, S., Sun, M., Yang, Y., Li, Y., Chen, L., & Zhou, Y. (2026). Understanding the potentially confounding effect of test suite size in test effectiveness evaluation. *ACM Transactions on Software Engineering and Methodology, 35*(5), 1–54. https://doi.org/10.1145/3748504 (online-first 2025; print 2026) — **counter-evidence**: after removing the size confound by linear regression, "mutation score demonstrates superior effectiveness in predicting test suite effectiveness, while statement coverage is the least effective metric."

---

### B3. Semantic mutation testing — the closest named prior art (7 annotated)

**Read §4 (Disambiguation Memo) together with this subsection.**

---

**B3-1.** Clark, J. A., Dan, H., & Hierons, R. M. (2010). Semantic mutation testing. In *2010 Third International Conference on Software Testing, Verification, and Validation Workshops (ICSTW)* (pp. 100–109). IEEE. https://doi.org/10.1109/ICSTW.2010.8

- **Relevance:** The originating paper of the named technique "semantic mutation testing". This is the term the parent paper must distinguish itself from.
- **Key findings:** (1) Introduces mutation of the *semantics of the language* in which the program is written, rather than of the program text. (2) Argues this captures a class of faults — misunderstandings of language or environment semantics — that syntactic operators structurally cannot produce. (3) Proposes semantic mutation operators tied to semantic variation points of a language.
- **Methodology:** Technique paper with worked examples; presented at the Mutation 2010 workshop.
- **Quality/limitations:** Workshop-length; CrossRef returns no abstract for this record and no open-access full text was retrievable through any of the four paper-search retrieval routes attempted (see §4.4).
- **Contribution to Theme B:** The naming collision. Any paper using the phrase "semantic mutation" in a testing context inherits this lineage and must say how it differs.

---

**B3-2.** Clark, J. A., Dan, H., & Hierons, R. M. (2013). Semantic mutation testing. *Science of Computer Programming, 78*(4), 345–363. https://doi.org/10.1016/j.scico.2011.03.011

- **Relevance:** The extended journal version — the definitive statement of the technique.
- **Key findings:** (1) Full development of the semantic-mutation model and its operator families. (2) Application across language and environment semantic variation points. (3) Positions semantic mutation as complementary to, not a replacement for, syntactic mutation.
- **Methodology:** Journal-length technique paper with case material.
- **Quality/limitations:** **Version dating requires care.** CrossRef records the print date as 2013-04-01 (vol. 78, issue 4, pp. 345–363); OpenAlex records the online-first date as **2011-04-22**. The paper is therefore cited in the literature variously as 2011 and 2013. Unpaywall reports `is_oa: True, oa_status: bronze` at ScienceDirect, but the full text could not be retrieved through the available tooling.
- **Contribution to Theme B:** The canonical target for the disambiguation memo in §4.

---

**B3-3.** Dan, H., & Hierons, R. M. (2012). SMT-C: A semantic mutation testing tools for C. In *2012 IEEE Fifth International Conference on Software Testing, Verification and Validation (ICST)* (pp. 654–663). IEEE. https://doi.org/10.1109/ICST.2012.155

- **Relevance:** The tool realisation of the technique — the artefact that shows what semantic mutation operators concretely are.
- **Key findings:** (1) Implements semantic mutation for C by varying the interpretation of language constructs whose semantics are implementation-defined or ambiguous. (2) Demonstrates feasibility on C subjects.
- **Methodology:** Tool paper.
- **Quality/limitations:** The title as registered in CrossRef contains a grammatical error ("Tools" rather than "Tool") — **cite it exactly as registered**; C-specific; no comparative fault-detection evaluation against syntactic operators.
- **Contribution to Theme B:** Concrete evidence that the Clark/Dan/Hierons operators target *language interpretation*, not program-level mathematical structure.

---

**B3-4.** Dan, H., & Hierons, R. M. (2012). Semantic mutation analysis of floating-point comparison. In *2012 IEEE Fifth International Conference on Software Testing, Verification and Validation (ICST)* (pp. 290–299). IEEE. https://doi.org/10.1109/ICST.2012.109

- **Relevance:** **The single closest prior art in the entire theme.** Semantic mutation applied to floating-point comparison semantics — that is, to numerical code, by the same authors.
- **Key findings:** (1) Applies semantic mutation to the semantics of floating-point comparison, where the "correct" comparison semantics are underdetermined. (2) Analyses the fault classes this exposes in numerical code.
- **Methodology:** Applied analysis with a floating-point-specific operator family.
- **Quality/limitations:** Scoped to comparison operations, not to equation-level structural properties; no MR involvement.
- **Contribution to Theme B:** **Counter-evidence.** This is the existing work a reviewer will point to and ask: "is your equation-derived mutation not just this, restated?" The parent paper must draw the line explicitly. See §4 and §5.

---

**B3-5.** Ghani, A. A. A. (2013). Towards semantic mutation testing of aspect-oriented programs. *Journal of Software Engineering and Applications, 6*(10), 5–13. https://doi.org/10.4236/jsea.2013.610A002

- **Relevance:** A successor paper that restates the Clark/Dan/Hierons definition explicitly and in quotable form.
- **Key findings (verbatim from the paper's abstract):** (1) "In traditional mutation testing of aspect-oriented programs, mutants are generated by making small changes to the syntax of the aspect-oriented language." (2) "Recently, a new approach known as semantic mutation testing has been proposed. **This approach mutates the semantics of the language in which the program is written.**" (3) "**The mutants generated misunderstandings of the language which are different classes of faults.**"
- **Methodology:** Position paper sketching scenarios; no implementation or evaluation.
- **Quality/limitations:** Low-impact open-access venue (SCIRP); speculative ("Towards"); 3 citations. **Included solely because it is the clearest independently-verifiable restatement of the definition, not for its own results.**
- **Contribution to Theme B:** Supplies the sourced definitional wording used in §4 when the primary sources' full texts were not retrievable.

---

**B3-6.** Huang, Z., & Alexander, R. (2015). Semantic mutation testing for multi-agent systems. In *Engineering Multi-Agent Systems (EMAS 2015)*, Lecture Notes in Computer Science (pp. 131–152). Springer International Publishing. https://doi.org/10.1007/978-3-319-26184-3_8

- **Relevance:** The clearest domain successor — extends the technique from language semantics to agent-platform semantics.
- **Key findings:** (1) Multi-agent systems have platform- and protocol-level semantic variation points suitable for semantic mutation. (2) Semantic mutation operators are defined at those points rather than in agent source code.
- **Methodology:** Technique paper with domain-specific operator design.
- **Quality/limitations:** Low citation count (4); no large-scale evaluation. Undermind returned no abstract for this record.
- **Contribution to Theme B:** Shows the lineage's extension pattern: pick a domain, find its *interpretation* variation points, mutate those. This is the pattern the parent paper must show it is *not* following.

---

**B3-7.** Cazzola, W., & Favalli, L. (2023). The language mutation problem: Leveraging language product lines for mutation testing of interpreters. *Journal of Systems and Software, 195*, 111533. https://doi.org/10.1016/j.jss.2022.111533

- **Relevance:** The most recent and most technically developed continuation of the "mutate the language, not the program" idea.
- **Key findings:** (1) Formulates the "language mutation problem" — mutating a language's implementation rather than programs written in it. (2) Uses language product lines to generate interpreter variants systematically.
- **Methodology:** Technique paper with tooling, in a top-tier SE journal.
- **Quality/limitations:** Online-first 2022-10; print volume dated 2023-01. Targets interpreters, so the "program under test" is a language implementation.
- **Contribution to Theme B:** Confirms that the semantic-mutation lineage remains active and has moved *further* toward language-implementation mutation, not toward specification- or equation-level mutation.

*Also verified, same lineage:* Derezińska, A., & Zaremba, Ł. (2018). Approaches to semantic mutation of behavioral state machines in model-driven software development. In *2018 Federated Conference on Computer Science and Information Systems (FedCSIS)*, *Annals of Computer Science and Information Systems, 15*, 863–866. IEEE. https://doi.org/10.15439/2018F313 — applies semantic mutation to UML state-machine *semantic variants*: "Behavior of UML state machines can be a source of interpretation problems in model to code transformation. Different solutions to the semantic variants could be defined as a special kind of mutations."

*Also verified, same lineage:* Cao, L., Zheng, W., Hu, D., & Bai, H. (2015). Concurrent program semantic mutation testing based on abstract memory model. In *2015 IEEE International Conference on Information and Automation (ICIA)* (pp. 1200–1205). IEEE. https://doi.org/10.1109/ICINFA.2015.7279469 — extends semantic mutation to concurrency/memory-model semantics.

---

### B4. Beyond default first-order catalogs (9 annotated)

---

**B4-1.** Jia, Y., & Harman, M. (2009). Higher order mutation testing. *Information and Software Technology, 51*(10), 1379–1393. https://doi.org/10.1016/j.infsof.2009.04.016

- **Relevance:** The foundational statement that the first-order operator catalog is a choice, not a necessity.
- **Key findings:** (1) Higher-order mutants can be *subtler* and harder to kill than first-order ones. (2) A small subset of higher-order mutants subsumes many first-order ones. (3) Search can be used to find valuable higher-order mutants.
- **Methodology:** Technique plus empirical evaluation.
- **Quality/limitations:** Combinatorial explosion is only partially addressed by the proposed search.
- **Contribution to Theme B:** Establishes that the mutant space is far larger than the default catalog, i.e. that any given catalog is an arbitrary sample of it.

*Predecessor verified:* Jia, Y., & Harman, M. (2008). Constructing subtle faults using higher order mutation testing. In *2008 Eighth IEEE International Working Conference on Source Code Analysis and Manipulation (SCAM)* (pp. 249–258). IEEE. https://doi.org/10.1109/SCAM.2008.36

---

**B4-2.** Harman, M., Jia, Y., & Langdon, W. B. (2010). A manifesto for higher order mutation testing. In *2010 Third International Conference on Software Testing, Verification, and Validation Workshops (ICSTW)* (pp. 80–89). IEEE. https://doi.org/10.1109/ICSTW.2010.13

- **Relevance:** The programmatic argument that mutation research should move beyond the default catalog.
- **Key findings:** (1) Sets out open problems for higher-order mutation. (2) Argues explicitly that the first-order restriction is historical, not principled.
- **Methodology:** Position paper.
- **Quality/limitations:** No new empirical results.
- **Contribution to Theme B:** Provides in-community authority for the statement that the standard operator set is not sacrosanct — useful for the parent paper's framing.

---

**B4-3.** Hook, D., & Kelly, D. (2009). Mutation sensitivity testing. *Computing in Science & Engineering, 11*(6), 40–47. https://doi.org/10.1109/MCSE.2009.200

- **Relevance:** **The key prior art for mutation in scientific computing specifically.** A mutation-based technique built around the fact that scientific code has tolerance-based, not exact, oracles.
- **Key findings:** (1) Adapts mutation analysis to scientific software, where "killed" is not a binary notion because outputs are compared under numerical tolerance. (2) Introduces the sensitivity framing: how large an output deviation a mutant induces, rather than whether any deviation occurs.
- **Methodology:** Technique paper in a computational-science venue.
- **Quality/limitations:** CiSE is a magazine-style venue, not a full research track; **CrossRef holds two DOIs for this article** — `10.1109/MCSE.2009.157` (no volume/issue, an early record) and `10.1109/MCSE.2009.200` (vol. 11, issue 6, pp. 40–47). Cite the latter.
- **Contribution to Theme B:** **Counter-evidence.** Mutation has already been adapted to numerical/scientific code with explicit attention to the oracle problem. The parent paper cannot claim the intersection is empty.

*Companion verified:* Hook, D., & Kelly, D. (2009). Testing for trustworthiness in scientific software. In *2009 ICSE Workshop on Software Engineering for Computational Science and Engineering (SECSE)* (pp. 59–64). IEEE. https://doi.org/10.1109/SECSE.2009.5069163

*Follow-on verified:* Gray, R., & Kelly, D. (2010). Investigating test selection techniques for scientific software using Hook's mutation sensitivity testing. *Procedia Computer Science, 1*(1), 1487–1494. https://doi.org/10.1016/j.procs.2010.04.165

---

**B4-4.** Delgado-Pérez, P., Habli, I., Gregory, S., Alexander, R., Clark, J., & Medina-Bulo, I. (2018). Evaluation of mutation testing in a nuclear industry case study. *IEEE Transactions on Reliability, 67*(4), 1406–1419. https://doi.org/10.1109/TR.2018.2864678

- **Relevance:** Mutation testing evaluated on safety-critical nuclear industry code — the application domain adjacent to the parent project's P-series.
- **Key findings:** (1) Mutation testing is applicable to industrial nuclear software. (2) Reports on operator effectiveness and cost in that setting. (3) Co-authored by John Clark, i.e. by the originator of semantic mutation testing.
- **Methodology:** Industrial case study.
- **Quality/limitations:** Single industrial partner; limited generalisability.
- **Contribution to Theme B:** **Counter-evidence** for a domain-specificity claim: syntactic mutation has already been evaluated favourably in the safety-critical/nuclear domain.

---

**B4-5.** Humbatova, N., Jahangirova, G., & Tonella, P. (2021). DeepCrime: Mutation testing of deep learning systems based on real faults. In *Proceedings of the 30th ACM SIGSOFT International Symposium on Software Testing and Analysis (ISSTA 2021)* (pp. 67–78). ACM. https://doi.org/10.1145/3460319.3464825

- **Relevance:** The exemplar of building a mutation operator set from a *domain fault taxonomy* rather than from language grammar.
- **Key findings:** (1) Operators are derived from an empirical taxonomy of real DL faults. (2) DeepCrime's real-fault-derived mutants differ materially from grammar-derived DL mutants. (3) Mutation killing must be redefined statistically because DL training is stochastic.
- **Methodology:** Tool + empirical evaluation grounded in a prior real-fault taxonomy.
- **Quality/limitations:** Domain-specific; killing criterion requires repeated training runs.
- **Contribution to Theme B:** **Counter-evidence and precedent.** Demonstrates the field already accepts "replace the grammar-derived denominator with a domain-property-derived one" as a legitimate research move — which both helps the parent paper's plausibility and undercuts its novelty claim.

*Companion verified:* Jahangirova, G., & Tonella, P. (2020). An empirical evaluation of mutation operators for deep learning systems. In *2020 IEEE 13th International Conference on Software Testing, Validation and Verification (ICST)* (pp. 74–84). IEEE. https://doi.org/10.1109/ICST46399.2020.00018

---

**B4-6.** Degiovanni, R., & Papadakis, M. (2022). µBert: Mutation testing using pre-trained language models. In *2022 IEEE International Conference on Software Testing, Verification and Validation Workshops (ICSTW)* (pp. 160–169). IEEE. https://doi.org/10.1109/ICSTW55395.2022.00039

- **Relevance:** First prominent demonstration that mutants can be generated outside any fixed operator catalog.
- **Key findings:** (1) A masked-language model proposes replacements at selected code locations. (2) The resulting mutants are not enumerable from a grammar-based operator list.
- **Methodology:** Tool paper with preliminary evaluation.
- **Quality/limitations:** Workshop paper; limited evaluation. **Note the exact registered title capitalisation: "µBert", not "µBERT".**
- **Contribution to Theme B:** Establishes that "the mutant population" is now openly treated as a design variable rather than a fixed reference set.

---

**B4-7.** Tip, F., Bell, J., & Schäfer, M. (2025). LLMorpheus: Mutation testing using large language models. *IEEE Transactions on Software Engineering, 51*(6), 1645–1665. https://doi.org/10.1109/TSE.2025.3562025

- **Relevance:** The mature LLM-mutation result, and an explicit statement that fixed operator sets cannot simulate certain real bug classes.
- **Key findings (from the arXiv abstract of the same work):** (1) "Most existing approaches for mutation testing involve the application of a fixed set of mutation operators... However, certain types of real-world bugs cannot easily be simulated by such approaches, limiting their effectiveness." (2) Placeholders are inserted at designated locations and an LLM proposes replacements. (3) LLMorpheus produces mutants resembling existing bugs "that cannot be produced by StrykerJS, a state-of-the-art mutation testing tool." (4) Reports running time, cost, and mutant counts across 13 JavaScript packages.
- **Methodology:** Tool paper plus multi-model, multi-prompt empirical evaluation.
- **Quality/limitations:** JavaScript only; LLM non-determinism and cost.
- **Contribution to Theme B:** The clearest in-literature statement that a fixed operator catalog is an expressiveness limit, not just a cost trade-off.

*Preprint version verified:* Tip, F., Bell, J., & Schäfer, M. (2024). *LLMorpheus: Mutation testing using large language models* (arXiv:2404.09952v2) [cs.SE]. arXiv. https://arxiv.org/abs/2404.09952

---

**B4-8.** Wang, B., Chen, M., Deng, M., Lin, Y., Harman, M., Papadakis, M., & Zhang, J. M. (2026). A comprehensive study on large language models for mutation testing. *ACM Transactions on Software Engineering and Methodology*. Advance online publication. https://doi.org/10.1145/3805038

- **Relevance:** The current state-of-the-art comparison of catalog-based versus generated mutants against real bugs.
- **Key findings (from the paper's own abstract):** (1) LLM-based approaches reach a real-bug detection rate of **77.4%** versus **41.6%** for rule-based techniques — an absolute gain of 35.8 percentage points and a 1.8× improvement. (2) LLM mutants are "more diverse... and behaviorally closer to real bugs". (3) The gain has a cost: LLM mutants are worse on non-compilability, duplication and equivalent-mutant rates by 25.9, 7.1 and 2.6 percentage points respectively. (4) Evaluated on 851 real bugs across two Java benchmarks, covering BugFarm, LLMorpheus and a new prompt.
- **Methodology:** Large-scale comparative empirical study; open- and closed-source LLMs.
- **Quality/limitations:** Advance online publication — no volume/issue/pages assigned as of verification date. Java only.
- **Contribution to Theme B:** **The strongest quantitative demonstration that the default syntactic catalog is a weak proxy for real faults** (41.6% detection) — and simultaneously the demonstration that the remedy the field is pursuing is *LLM-generated* mutants, not specification-derived ones.

---

### B5. Threats to the mutation-score construct (11 annotated)

---

**B5-1.** Budd, T. A., & Angluin, D. (1982). Two notions of correctness and their relation to testing. *Acta Informatica, 18*(1), 31–45. https://doi.org/10.1007/BF00625279

- **Relevance:** The theoretical source of the equivalent-mutant problem.
- **Key findings:** (1) Distinguishes two formal notions of program correctness and relates them to test-based adequacy. (2) Establishes undecidability results that make equivalent-mutant detection undecidable in general.
- **Methodology:** Theoretical.
- **Quality/limitations:** Abstract; no empirical component.
- **Contribution to Theme B:** The denominator of mutation score is not merely hard to compute — it is *not computable*. This is the deepest available construct objection.

---

**B5-2.** Offutt, A. J., Lee, A., Rothermel, G., Untch, R. H., & Zapf, C. (1996). An experimental determination of sufficient mutant operators. *ACM Transactions on Software Engineering and Methodology, 5*(2), 99–118. https://doi.org/10.1145/227607.227610

- **Relevance:** The origin of "selective mutation" and, inadvertently, of the arbitrariness of the operator denominator.
- **Key findings:** (1) A small subset of operators (the "5 sufficient operators") achieves near-equivalent adequacy to the full set. (2) Cost reduction is therefore achievable without apparent adequacy loss.
- **Methodology:** Experimental determination over Mothra's Fortran operator set.
- **Quality/limitations:** Result is specific to one tool's operator set on one language; later work (B5-8, B5-10) shows the "sufficiency" conclusion is fragile.
- **Contribution to Theme B:** If a 5-operator set is "sufficient", then the mutation score computed over the full set and over the subset are different numbers claiming the same construct. The denominator is a free parameter.

*Also verified:* Wong, W. E., & Mathur, A. P. (1995). Reducing the cost of mutation testing: An empirical study. *Journal of Systems and Software, 31*(3), 185–196. https://doi.org/10.1016/0164-1212(94)00098-0

---

**B5-3.** Offutt, A. J., & Pan, J. (1997). Automatically detecting equivalent mutants and infeasible paths. *Software Testing, Verification and Reliability, 7*(3), 165–192. https://doi.org/10.1002/(SICI)1099-1689(199709)7:3<165::AID-STVR143>3.0.CO;2-U

- **Relevance:** The reference automated attack on the equivalent-mutant problem.
- **Key findings:** (1) Constraint-based techniques detect a substantial fraction of equivalent mutants. (2) The equivalent-mutant and infeasible-path problems are shown to share structure.
- **Methodology:** Technique plus empirical evaluation.
- **Quality/limitations:** Partial by construction (the general problem is undecidable). **Note the DOI contains angle brackets and must be URL-encoded in BibTeX.**
- **Contribution to Theme B:** Establishes that the equivalent-mutant residual is managed heuristically, not eliminated — so every published mutation score has an unquantified denominator error.

---

**B5-4.** Yao, X., Harman, M., & Jia, Y. (2014). A study of equivalent and stubborn mutation operators using human analysis of equivalence. In *Proceedings of the 36th International Conference on Software Engineering (ICSE 2014)* (pp. 919–930). ACM. https://doi.org/10.1145/2568225.2568265

- **Relevance:** The empirical measurement of how much of the denominator is junk, using human ground truth.
- **Key findings:** (1) Human analysis quantifies equivalent-mutant prevalence per operator. (2) Equivalence is highly operator-dependent — some operators are dominated by equivalent mutants. (3) Identifies "stubborn" mutants: non-equivalent but not killed by any test in the suite.
- **Methodology:** Manual classification study with human analysts.
- **Quality/limitations:** Manual classification is expensive and to some degree subjective; limited subject count.
- **Contribution to Theme B:** Provides the per-operator equivalence rates that make "mutation score" non-comparable across operator configurations.

---

**B5-5.** Papadakis, M., Jia, Y., Harman, M., & Le Traon, Y. (2015). Trivial compiler equivalence: A large scale empirical study of a simple, fast and effective equivalent mutant detection technique. In *2015 IEEE/ACM 37th IEEE International Conference on Software Engineering (ICSE)* (pp. 936–946). IEEE. https://doi.org/10.1109/ICSE.2015.103

- **Relevance:** The scalable equivalent/duplicate-mutant detector, and the study that quantified duplicate-mutant prevalence at scale.
- **Key findings:** (1) Compiling mutants and comparing object code detects a large share of equivalent and duplicate mutants cheaply. (2) Duplicate mutants — distinct source edits producing identical semantics — are common and inflate the denominator.
- **Methodology:** Large-scale empirical study across many programs.
- **Quality/limitations:** Detects only *trivially* equivalent mutants; a residual remains.
- **Contribution to Theme B:** Duplicates mean the denominator double-counts. Mutation score is not a proportion over distinct semantic behaviours.

*Journal companion verified:* Kintis, M., Papadakis, M., Jia, Y., Malevris, N., Le Traon, Y., & Harman, M. (2018). Detecting trivial mutant equivalences via compiler optimisations. *IEEE Transactions on Software Engineering, 44*(4), 308–333. https://doi.org/10.1109/TSE.2017.2684805

---

**B5-6.** Papadakis, M., Henard, C., Harman, M., Jia, Y., & Le Traon, Y. (2016). Threats to the validity of mutation-based test assessment. In *Proceedings of the 25th International Symposium on Software Testing and Analysis (ISSTA 2016)* (pp. 354–365). ACM. https://doi.org/10.1145/2931037.2931040

- **Relevance:** The explicit, named treatment of mutation-score validity threats by the field's leading group.
- **Key findings:** (1) Subsumed mutants inflate mutation score and can invert experimental conclusions. (2) Not accounting for subsumption produces invalid comparisons between techniques. (3) Recommends disjoint/subsuming mutation score as the corrected instrument.
- **Methodology:** Empirical validity study with re-analysis of prior experimental designs.
- **Quality/limitations:** The corrected instrument is itself expensive to compute.
- **Contribution to Theme B:** **The most directly citable in-field acknowledgement that raw mutation score is a distorted measurement.** Any construct-validity argument should build on this rather than assert the point fresh.

---

**B5-7.** Kurtz, B., Ammann, P., Offutt, J., Delamaro, M. E., Kurtz, M., & Gökçe, N. (2016). Analyzing the validity of selective mutation with dominator mutants. In *Proceedings of the 2016 24th ACM SIGSOFT International Symposium on Foundations of Software Engineering (FSE 2016)* (pp. 571–582). ACM. https://doi.org/10.1145/2950290.2950322

- **Relevance:** Shows that the classical selective-mutation justification does not survive a subsumption-aware analysis.
- **Key findings:** (1) When measured against dominator mutants rather than raw mutant counts, selective mutation's claimed sufficiency largely disappears. (2) The apparent adequacy of reduced operator sets was an artefact of counting redundant mutants.
- **Methodology:** Empirical re-analysis using dominator/subsumption structure.
- **Quality/limitations:** Dominator computation is expensive and subject-specific.
- **Contribution to Theme B:** Directly attacks B5-2's foundational result. Two of the field's most-cited denominator results are in tension.

*Companion verified:* Kurtz, B., Ammann, P., Offutt, J., & Kurtz, M. (2016). Are we there yet? How redundant and equivalent mutants affect determination of test completeness. In *2016 IEEE Ninth International Conference on Software Testing, Verification and Validation Workshops (ICSTW)* (pp. 142–151). IEEE. https://doi.org/10.1109/ICSTW.2016.41

*Companion verified:* Ammann, P., Delamaro, M. E., & Offutt, J. (2014). Establishing theoretical minimal sets of mutants. In *2014 IEEE Seventh International Conference on Software Testing, Verification and Validation (ICST)* (pp. 21–30). IEEE. https://doi.org/10.1109/ICST.2014.13

---

**B5-8.** Laurent, T., Papadakis, M., Kintis, M., Henard, C., Le Traon, Y., & Ventresque, A. (2017). Assessing and improving the mutation testing practice of PIT. In *2017 IEEE International Conference on Software Testing, Verification and Validation (ICST)* (pp. 430–435). IEEE. https://doi.org/10.1109/ICST.2017.47

- **Relevance:** Documents that the most widely used Java mutation tool implements a materially weaker operator set than the literature assumes.
- **Key findings:** (1) PIT's default operator set is substantially narrower than research-grade sets. (2) Extending the operator set changes measured mutation scores materially. (3) Results reported using PIT are therefore not comparable to results using other tools.
- **Methodology:** Tool analysis plus empirical comparison.
- **Quality/limitations:** Short paper; PIT-specific.
- **Contribution to Theme B:** Operationalises "operator-set disagreement across tools" — the same test suite gets different mutation scores depending on which tool computed it.

*Companion verified:* Kintis, M., Papadakis, M., Papadopoulos, A., Valvis, E., Malevris, N., & Le Traon, Y. (2018). How effective are mutation testing tools? An empirical analysis of Java mutation testing tools with manual analysis and real faults. *Empirical Software Engineering, 23*(4), 2426–2463. https://doi.org/10.1007/s10664-017-9582-5 (online-first 2017-12-21)

*Companion verified:* Hariri, F., Shi, A., Fernando, V., Mahmood, S., & Marinov, D. (2019). Comparing mutation testing at the levels of source code and compiler intermediate representation. In *2019 12th IEEE Conference on Software Testing, Validation and Verification (ICST)* (pp. 114–124). IEEE. https://doi.org/10.1109/ICST.2019.00021

---

**B5-9.** Petrović, G., Ivanković, M., Fraser, G., & Just, R. (2022). Practical mutation testing at scale: A view from Google. *IEEE Transactions on Software Engineering, 48*(10), 3900–3912. https://doi.org/10.1109/TSE.2021.3107634

- **Relevance:** The definitive industrial statement that the raw mutant population is unusable and must be filtered to "productive" mutants.
- **Key findings:** (1) At Google's scale, most mutants are unproductive and are suppressed by heuristic rules before developers see them. (2) Productive-mutant filtering, not raw mutation score, is what is deployed. (3) Mutant selection is driven by developer feedback signals rather than by adequacy theory.
- **Methodology:** Large-scale industrial experience report with quantitative data.
- **Quality/limitations:** Single company; "productive" is defined operationally by developer response, which is itself a construct choice.
- **Contribution to Theme B:** **The strongest practical evidence that the denominator is not treated as canonical by anyone who deploys mutation at scale.**

*Companion verified:* Petrović, G., & Ivanković, M. (2018). State of mutation testing at Google. In *Proceedings of the 40th International Conference on Software Engineering: Software Engineering in Practice (ICSE-SEIP 2018)* (pp. 163–171). ACM. https://doi.org/10.1145/3183519.3183521

*Companion verified — counter-evidence:* Petrović, G., Ivanković, M., Fraser, G., & Just, R. (2021). Does mutation testing improve testing practices? In *2021 IEEE/ACM 43rd International Conference on Software Engineering (ICSE)* (pp. 910–921). IEEE. https://doi.org/10.1109/ICSE43902.2021.00087

*Companion verified:* Beller, M., Wong, C.-P., Bader, J., Scott, A., Machalica, M., Chandra, S., & Meijer, E. (2021). What it would take to use mutation testing in industry — A study at Facebook. In *2021 IEEE/ACM 43rd International Conference on Software Engineering: Software Engineering in Practice (ICSE-SEIP)* (pp. 268–277). IEEE. https://doi.org/10.1109/ICSE-SEIP52600.2021.00036

---

**B5-10.** Kushigian, B., Kaufman, S. J., Featherman, R., Potter, H., Madadi, A., & Just, R. (2024). Equivalent mutants in the wild: Identifying and efficiently suppressing equivalent mutants for Java programs. In *Proceedings of the 33rd ACM SIGSOFT International Symposium on Software Testing and Analysis (ISSTA 2024)* (pp. 654–665). ACM. https://doi.org/10.1145/3650212.3680310

- **Relevance:** The current state of the art on measuring and suppressing equivalent mutants at scale.
- **Key findings:** (1) Equivalent mutants remain prevalent in real Java codebases. (2) Efficient suppression is achievable, but only for identifiable classes.
- **Methodology:** Large-scale empirical study plus technique.
- **Quality/limitations:** Java-specific; suppression is again partial.
- **Contribution to Theme B:** Confirms the denominator problem is unresolved in 2024, forty-two years after B5-1.

---

**B5-11.** Alblwi, S., Ayad, A., & Mili, A. (2024). Mutation coverage is not strongly correlated with mutation coverage. In *Proceedings of the 5th ACM/IEEE International Conference on Automation of Software Test (AST 2024)* (pp. 1–11). ACM. https://doi.org/10.1145/3644032.3644442

- **Relevance:** A deliberately provocative internal-consistency result: two defensible operationalisations of "mutation coverage" disagree with each other.
- **Key findings:** (1) Different formalisations of the same nominal metric produce weakly correlated values on the same subjects. (2) The metric's meaning is not fixed by its name.
- **Methodology:** Formal analysis plus empirical comparison.
- **Quality/limitations:** Small venue; the argument is partly definitional. The title is intentionally self-referential and is registered exactly as printed above — **do not "correct" it.**
- **Contribution to Theme B:** The cleanest single citation for "mutation score is not one construct" — an internal-validity argument that requires no appeal to real faults at all.

*Also verified:* Gopinath, R., Alipour, A., Ahmed, I., Jensen, C., & Groce, A. (2016). Measuring effectiveness of mutant sets. In *2016 IEEE Ninth International Conference on Software Testing, Verification and Validation Workshops (ICSTW)* (pp. 132–141). IEEE. https://doi.org/10.1109/ICSTW.2016.45

*Also verified:* Namin, A. S., & Kakarla, S. (2011). The use of mutation in testing experiments and its sensitivity to external threats. In *Proceedings of the 2011 International Symposium on Software Testing and Analysis (ISSTA 2011)* (pp. 342–352). ACM. https://doi.org/10.1145/2001420.2001461

*Also verified:* Papadakis, M., Chekam, T. T., & Le Traon, Y. (2018). Mutant quality indicators. In *2018 IEEE International Conference on Software Testing, Verification and Validation Workshops (ICSTW)* (pp. 32–39). IEEE. https://doi.org/10.1109/ICSTW.2018.00025

---

### B6. Mutation used to evaluate oracles rather than inputs (10 annotated)

**This is the exact use to which mutation is put when it evaluates metamorphic relations.**

---

**B6-1.** Barr, E. T., Harman, M., McMinn, P., Shahbaz, M., & Yoo, S. (2015). The oracle problem in software testing: A survey. *IEEE Transactions on Software Engineering, 41*(5), 507–525. https://doi.org/10.1109/TSE.2014.2372785

- **Relevance:** The definitional survey of the oracle problem, including where metamorphic relations sit in the oracle taxonomy.
- **Key findings:** (1) Taxonomy of specified, derived, implicit, and absent oracles. (2) Metamorphic relations are classified as derived (partial) oracles. (3) Oracle quality is identified as under-measured relative to input quality.
- **Methodology:** Systematic survey.
- **Quality/limitations:** Coverage ends around 2013.
- **Contribution to Theme B:** Establishes the vocabulary in which "an MR is a partial oracle, not a test input" can be stated precisely — necessary for any construct-misalignment argument.

---

**B6-2.** Budd, T. A., & Gopal, A. S. (1985). Program testing by specification mutation. *Computer Languages, 10*(1), 63–73. https://doi.org/10.1016/0096-0551(85)90011-6

- **Relevance:** **The earliest mutation family that targets a declared specification rather than program text.** Predates semantic mutation testing by 25 years.
- **Key findings:** (1) Mutation operators are applied to a formal specification of the program, not to the program. (2) Test data adequacy is judged by ability to distinguish the specification from its mutants.
- **Methodology:** Technique paper.
- **Quality/limitations:** Requires a formal specification to exist; pre-dates modern tooling.
- **Contribution to Theme B:** **Critical prior art for the parent paper.** "Mutate the declared obligation rather than the code" is a 1985 idea. The parent paper's novelty must be located elsewhere — e.g. in equation-derived structure preservation and in independent certification of the mutants.

---

**B6-3.** Knauth, T., Fetzer, C., & Felber, P. (2009). Assertion-driven development: Assessing the quality of contracts using meta-mutations. In *2009 International Conference on Software Testing, Verification, and Validation Workshops (ICSTW)* (pp. 182–191). IEEE. https://doi.org/10.1109/ICSTW.2009.40

- **Relevance:** Mutation applied specifically to assess *contract* quality — the closest structural analogue to using mutation to assess MR-set adequacy.
- **Key findings:** (1) Introduces "meta-mutations" for judging whether contracts are strong enough. (2) Contract quality is measured by which mutants the contracts detect.
- **Methodology:** Technique paper with prototype.
- **Quality/limitations:** Workshop paper; 8 citations; limited evaluation.
- **Contribution to Theme B:** Establishes the exact evaluation shape the parent paper uses — mutants as the yardstick for a declared-obligation set — in 2009.

---

**B6-4.** Schuler, D., & Zeller, A. (2011). Assessing oracle quality with checked coverage. In *2011 Fourth IEEE International Conference on Software Testing, Verification and Validation (ICST)* (pp. 90–99). IEEE. https://doi.org/10.1109/ICST.2011.32

- **Relevance:** The best-known alternative to mutation for measuring oracle quality, and an explicit comparison against mutation.
- **Key findings:** (1) Introduces checked coverage — the dynamic slice of covered statements that actually influences an oracle. (2) Coverage without oracle checking systematically overstates test quality.
- **Methodology:** Technique plus empirical evaluation on open-source projects.
- **Quality/limitations:** Requires dynamic slicing; overhead is significant.
- **Contribution to Theme B:** Demonstrates the field already recognised that adequacy metrics measuring inputs do not measure oracles.

**B6-4b.** Schuler, D., & Zeller, A. (2013). Checked coverage: An indicator for oracle quality. *Software Testing, Verification and Reliability, 23*(7), 531–551. https://doi.org/10.1002/stvr.1497 (online-first 2013-05-08)

- **Key findings (verbatim from the paper's abstract):** (1) "A known problem of traditional coverage metrics is that they do not assess *oracle quality* — that is, whether the computation result is actually checked against expectations." (2) "Our experiments on seven open-source projects show that **checked coverage is a sure indicator for oracle quality and even more sensitive than mutation testing.**"
- **Contribution to Theme B:** **Counter-evidence with a twist.** It confirms conventional coverage cannot assess oracles, but it also asserts an alternative that outperforms *mutation* at the oracle-assessment job — which cuts against building a new metric on a mutation base.

---

**B6-5.** Staats, M., Whalen, M. W., & Heimdahl, M. P. E. (2011). Programs, tests, and oracles. In *Proceedings of the 33rd International Conference on Software Engineering (ICSE 2011)* (pp. 391–400). ACM. https://doi.org/10.1145/1985793.1985847

- **Relevance:** The theoretical reframing of testing as a three-way relationship between program, test inputs and oracle.
- **Key findings:** (1) Test adequacy cannot be assessed independently of the oracle. (2) Formalises the program/test/oracle triple and shows criteria defined over only two of the three are incomplete.
- **Methodology:** Theoretical paper with formal framework.
- **Quality/limitations:** CrossRef registers the title as "Programs, tests, and oracles" without the subtitle "the foundations of testing revisited" that appears in the proceedings; **cite as registered or note the variant.**
- **Contribution to Theme B:** The formal license for saying "an adequacy criterion whose denominator ignores the oracle is measuring the wrong thing".

**B6-5b.** Staats, M., Gay, G., & Heimdahl, M. P. E. (2012). Automated oracle creation support, or: How I learned to stop worrying about fault propagation and love mutation testing. In *2012 34th International Conference on Software Engineering (ICSE)* (pp. 870–880). IEEE. https://doi.org/10.1109/ICSE.2012.6227132

- **Key findings:** (1) Mutation is used to select which program variables an oracle should check. (2) Mutation-based oracle-variable selection outperforms alternatives.
- **Contribution to Theme B:** **Counter-evidence.** A direct, favourably-evaluated use of mutation to build and assess oracles — the exact application the parent paper questions.

---

**B6-6.** Jahangirova, G., Clark, D., Harman, M., & Tonella, P. (2016). Test oracle assessment and improvement. In *Proceedings of the 25th International Symposium on Software Testing and Analysis (ISSTA 2016)* (pp. 247–258). ACM. https://doi.org/10.1145/2931037.2931062

- **Relevance:** The most developed framework for oracle assessment, built on mutation plus false-positive/false-negative analysis.
- **Key findings:** (1) Oracle deficiency is decomposed into false positives and false negatives. (2) Mutants supply the false-negative signal; the framework then proposes improvements. (3) Assessment and improvement are treated as a single loop.
- **Methodology:** Technique plus empirical evaluation.
- **Quality/limitations:** Requires substantial manual involvement for the false-positive side.
- **Contribution to Theme B:** The reference method against which any new oracle-adequacy metric — including an MR-set adequacy metric — will be compared.

**B6-6b.** Jahangirova, G., Clark, D., Harman, M., & Tonella, P. (2021). An empirical validation of oracle improvement. *IEEE Transactions on Software Engineering, 47*(8), 1708–1728. https://doi.org/10.1109/TSE.2019.2934409 (online-first 2019-08)

- **Contribution to Theme B:** The journal validation; **counter-evidence** that mutation-driven oracle assessment produces measurable oracle improvement in practice.

*Tool paper verified:* Jahangirova, G., Clark, D., Harman, M., & Tonella, P. (2018). OASIs: Oracle assessment and improvement tool. In *Proceedings of the 27th ACM SIGSOFT International Symposium on Software Testing and Analysis (ISSTA 2018)* (pp. 368–371). ACM. https://doi.org/10.1145/3213846.3229503

---

**B6-7.** Knüppel, A., Schaer, L., & Schaefer, I. (2021). How much specification is enough? Mutation analysis for software contracts. In *2021 IEEE/ACM 9th International Conference on Formal Methods in Software Engineering (FormaliSE)* (pp. 42–53). IEEE. https://doi.org/10.1109/FormaliSE52586.2021.00011

- **Relevance:** Mutation analysis used explicitly to measure *specification completeness* — the nearest published analogue to measuring MR-set adequacy.
- **Key findings (from the paper's own abstract):** (1) Developers write weaker specifications than needed because strong specification is "expensive and error-prone"; consequently "potential bugs remain undetected during software verification". (2) Proposes "a methodology that considers the degree of incomplete specifications by means of mutation analysis", giving developers "a sense of specification coverage". (3) Demonstrated on Java+JML with the KeY-2.6.3 deductive verifier over open-source JML projects.
- **Methodology:** Methodology paper with deductive-verification-based evaluation.
- **Quality/limitations:** Requires JML annotations and a deductive verifier; 7 citations.
- **Contribution to Theme B:** **The closest existing "mutation as a specification-adequacy metric" result.** The parent paper's contribution must be distinguished from this as well as from B3 and B6-2.

---

**B6-8.** Zhang, Y., & Mesbah, A. (2015). Assertions are strongly correlated with test suite effectiveness. In *Proceedings of the 2015 10th Joint Meeting on Foundations of Software Engineering (ESEC/FSE 2015)* (pp. 214–224). ACM. https://doi.org/10.1145/2786805.2786858

- **Relevance:** Establishes that oracle strength — not input coverage — is what actually drives measured effectiveness.
- **Key findings:** (1) Assertion count and assertion coverage correlate strongly with effectiveness. (2) The correlation is stronger than for code coverage.
- **Methodology:** Empirical study over Java projects with mutation-based effectiveness measurement.
- **Quality/limitations:** Uses mutants as effectiveness ground truth — the same circularity as B2-5.
- **Contribution to Theme B:** Empirical support for the premise that oracle quality is the binding constraint, which is the premise a metric for MR-set adequacy needs.

---

**B6-9.** Cordy, M., Lazreg, S., Legay, A., & Schobbens, P. Y. (2023). Towards strengthening formal specifications with mutation model checking. In *Proceedings of the 31st ACM Joint European Software Engineering Conference and Symposium on the Foundations of Software Engineering (ESEC/FSE 2023)* (pp. 2102–2106). ACM. https://doi.org/10.1145/3611643.3613080

- **Relevance:** Recent work applying mutation to strengthen formal specifications, using model checking rather than test execution as the kill criterion.
- **Key findings:** (1) Mutants of the *system* are used to detect specification weakness. (2) A specification that fails to reject a mutated system is too weak.
- **Methodology:** Short vision/technique paper.
- **Quality/limitations:** 5-page ideas paper; 1 citation; preliminary.
- **Contribution to Theme B:** Demonstrates the "mutants certified independently of the verdict source" idea is actively being explored in the formal-methods community.

---

**B6-10.** Maton, M., Kapfhammer, G. M., & McMinn, P. (2025). Where tests fall short: Empirically analyzing oracle gaps in covered code. In *2025 ACM/IEEE International Symposium on Empirical Software Engineering and Measurement (ESEM)* (pp. 1–11). IEEE. https://doi.org/10.1109/ESEM64174.2025.00063

- **Relevance:** The most recent empirical quantification of the gap between covered code and checked code.
- **Key findings:** (1) A substantial fraction of covered code is never subject to any oracle. (2) The gap is measurable and systematic rather than incidental.
- **Methodology:** Empirical study.
- **Quality/limitations:** Very recent; no citation record yet.
- **Contribution to Theme B:** Current-year confirmation that oracle adequacy remains unmeasured by standard instruments.

*Also verified:* Shrestha, K., & Rutherford, M. J. (2011). An empirical evaluation of assertions as oracles. In *2011 Fourth IEEE International Conference on Software Testing, Verification and Validation (ICST)* (pp. 110–119). IEEE. https://doi.org/10.1109/ICST.2011.50

*Also verified:* Schuler, D., Dallmeier, V., & Zeller, A. (2009). Efficient mutation testing by checking invariant violations. In *Proceedings of the Eighteenth International Symposium on Software Testing and Analysis (ISSTA '09)* (pp. 69–80). ACM. https://doi.org/10.1145/1572272.1572282

*Also verified:* Fraser, G., & Zeller, A. (2012). Mutation-driven generation of unit tests and oracles. *IEEE Transactions on Software Engineering, 38*(2), 278–292. https://doi.org/10.1109/TSE.2011.93 — **note:** the conference original is Fraser, G., & Zeller, A. (2010), ISSTA '10, pp. 147–158, https://doi.org/10.1145/1831708.1831728. Undermind's record conflated the TSE title/pages with the ISSTA DOI; both records were resolved separately and are reported separately here.

*Also verified:* Molina, F., Aguirre, N., & Gorla, A. (2025). State field coverage: A metric for oracle quality. In *2025 40th IEEE/ACM International Conference on Automated Software Engineering (ASE)* (pp. 2707–2719). IEEE. https://doi.org/10.1109/ASE63991.2025.00222

*Also verified, bridging to scientific computing:* Kanewala, U., & Bieman, J. M. (2013). Techniques for testing scientific programs without an oracle. In *2013 5th International Workshop on Software Engineering for Computational Science and Engineering (SE-CSE)* (pp. 48–57). IEEE. https://doi.org/10.1109/SECSE.2013.6615099

---

### 3.7 Verified-supplementary sources (17)

All independently verified through `user-paper-search`; retained in the bibliography but not annotated, being either companion versions of annotated entries or second-tier support.

| # | Reference | DOI | Sub-theme |
|---|---|---|---|
| S1 | Offutt (1989), TAV3, 131–140 | 10.1145/75308.75324 | B1 |
| S2 | Ammann & Offutt (2008), CUP, 1st ed. | 10.1017/CBO9780511809163 | B1 |
| S3 | Zhu, Panichella & Zaidman (2018), *STVR* 28(6) | 10.1002/stvr.1675 | B1 |
| S4 | Andrews, Briand, Labiche & Namin (2006), *TSE* 32(8), 608–624 | 10.1109/TSE.2006.83 | B2 |
| S5 | Ahmed et al. (2024), *STVR* 34(3) | 10.1002/stvr.1874 | B2 |
| S6 | Zhang et al. (2024), *TOSEM* 33(4), 1–32 | 10.1145/3635713 | B2 |
| S7 | Lu et al. (2026), *TOSEM* 35(5), 1–54 | 10.1145/3748504 | B2 |
| S8 | Laurent, Gaffney & Ventresque (2022), ICSTW, 189–198 | 10.1109/ICSTW55395.2022.00042 | B2 |
| S9 | Derezińska & Zaremba (2018), FedCSIS, 863–866 | 10.15439/2018F313 | B3 |
| S10 | Cao, Zheng, Hu & Bai (2015), ICIA, 1200–1205 | 10.1109/ICINFA.2015.7279469 | B3 |
| S11 | Jia & Harman (2008), SCAM, 249–258 | 10.1109/SCAM.2008.36 | B4 |
| S12 | Jahangirova & Tonella (2020), ICST, 74–84 | 10.1109/ICST46399.2020.00018 | B4 |
| S13 | Hook & Kelly (2009), SECSE, 59–64 | 10.1109/SECSE.2009.5069163 | B4 |
| S14 | Gray & Kelly (2010), *Procedia CS* 1(1), 1487–1494 | 10.1016/j.procs.2010.04.165 | B4 |
| S15 | Chekam et al. (2020), *EMSE* 25(1), 434–487 | 10.1007/s10664-019-09778-7 | B5 |
| S16 | Ojdanić et al. (2022), *EMSE* 27(5) | 10.1007/s10664-022-10138-1 | B5 |
| S17 | Offutt & Hayes (1996), ISSTA, 195–200 | 10.1145/229000.226317 | B5 |

---

## 4. DISAMBIGUATION MEMO — "Semantic Mutation Testing" (B3)

### 4.1 The definition as used by Clark, Dan and Hierons

**Semantic mutation testing mutates the semantics of the language in which the program is written, not the text of the program.**

Sourced statement of the definition, from a successor paper whose abstract is verbatim retrievable (Ghani, 2013, *JSEA* 6(10), abstract, first-page):

> "In traditional mutation testing of aspect-oriented programs, mutants are generated by making small changes to the syntax of the aspect-oriented language. Recently, a new approach known as semantic mutation testing has been proposed. **This approach mutates the semantics of the language in which the program is written. The mutants generated misunderstandings of the language which are different classes of faults.**"

Three structural features follow from this and are confirmed by the technique's own tooling and successors:

1. **The mutated object is the interpretation function, not the program.** The program text is held fixed; what varies is what the text *means*. SMT-C (Dan & Hierons, 2012a) realises this for C by varying the interpretation of constructs whose semantics are implementation-defined or otherwise underdetermined.
2. **The fault model is misunderstanding.** The class of faults simulated is a programmer or environment misunderstanding the language or platform semantics — not a wrong edit. This is stated directly in the Ghani restatement above ("mutants generated misunderstandings of the language").
3. **The mutation points are semantic variation points.** Derezińska & Zaremba (2018, FedCSIS, abstract) make this explicit for UML: "Behavior of UML state machines can be a source of interpretation problems in model to code transformation. **Different solutions to the semantic variants could be defined as a special kind of mutations**, similarly as in the mutation testing." The operators are indexed by places where a language or model admits more than one legitimate interpretation.

Domain instantiations of the same pattern, each verified:

| Instantiation | Semantic variation point mutated | Source |
|---|---|---|
| SMT-C | C language constructs with implementation-defined semantics | Dan & Hierons (2012a), ICST, 654–663 |
| Floating-point comparison | The semantics of comparing floating-point values | Dan & Hierons (2012b), ICST, 290–299 |
| Multi-agent systems | Agent platform / protocol semantics | Huang & Alexander (2015), EMAS, 131–152 |
| Aspect-oriented programs | AOP weaving and advice semantics (proposed, not implemented) | Ghani (2013), *JSEA* 6(10), 5–13 |
| UML behavioural state machines | State-machine semantic variants in model-to-code transformation | Derezińska & Zaremba (2018), FedCSIS, 863–866 |
| Concurrent programs | Abstract memory model semantics | Cao et al. (2015), ICIA, 1200–1205 |
| Language interpreters | The interpreter implementation itself, via language product lines | Cazzola & Favalli (2023), *JSS* 195, 111533 |

### 4.2 Factual differences from mutating a program to violate an equation-derived structural property

Stated as differences of object, source, and detection criterion. No judgement of merit is offered.

| Dimension | Clark/Dan/Hierons semantic mutation | Mutation targeting an equation-derived structure-preservation requirement |
|---|---|---|
| **What is mutated** | The interpretation (semantics) assigned to the program's language or platform | The program text itself |
| **What is held fixed** | The program text | The language semantics |
| **Where the operators come from** | Points where the language or model admits more than one legitimate interpretation (implementation-defined behaviour, semantic variants, platform choices) | An equation or governing mathematical relation from which a structural property is derived |
| **Fault class simulated** | Misunderstanding of language/platform semantics by the programmer or the toolchain | Violation of a declared mathematical structure-preservation obligation |
| **Language dependence** | Intrinsic — the operator set is defined per language/platform and is not portable | The obligation is stated at the equation level and is in principle language-independent |
| **Relation to a specification** | None required; the technique needs no specification, only a language with semantic slack | The property is derived from a declared equation, i.e. from a specification-like artefact |
| **Certification of a mutant** | A semantic mutant is valid if it corresponds to a legitimate alternative interpretation | A mutant is valid if it demonstrably violates the derived structural property, established independently |

### 4.3 The two other lineages that must also be distinguished

Mutating the *program* to violate a *declared obligation* is not new either, and two prior lineages are closer to it than semantic mutation testing is:

1. **Specification mutation** (Budd & Gopal, 1985, *Computer Languages* 10(1), 63–73): mutates the formal specification and judges test data by its ability to distinguish specification from specification-mutant. Object mutated = specification. This is the *inverse* of the parent paper's direction, but it is the same "mutate the declared obligation" family.
2. **Mutation analysis for specification/contract completeness** (Knauth et al., 2009, ICSTW, 182–191; Knüppel et al., 2021, FormaliSE, 42–53): mutates the *program*, and uses which mutants the contracts/specifications fail to reject as a measure of specification weakness. This is structurally the same evaluation shape the parent paper proposes for MR sets — the object mutated is the program, the thing being measured is the declared obligation set.

**The parent paper's distinction must therefore be drawn against three lineages, not one:** (a) semantic mutation testing, on *what is mutated*; (b) specification mutation, on *direction*; (c) contract-completeness mutation analysis, on *what makes the mutant family principled* — the independent certification against an equation-derived property, rather than an operator catalog.

### 4.4 Retrieval limitation, stated plainly

**I could not obtain the full text of Clark, Dan & Hierons (2010) or (2013), or of Dan & Hierons (2012a, 2012b).** Four retrieval routes were attempted and all failed: `read_crossref_paper` (returns metadata only by design), `read_openalex_paper` (refuses direct reads), `search_unpaywall` (reports `is_oa: True, oa_status: bronze` with a ScienceDirect URL that is not machine-retrievable through the tooling), and `search_base` (empty output). Undermind reports "PDF X" for all four records.

**Consequence:** the definitions above are grounded in verbatim abstracts of *successor* papers (Ghani 2013; Derezińska & Zaremba 2018) and in verified titles/venues of the primary papers. **I therefore cannot supply section or page-level citations inside the Clark/Dan/Hierons papers**, and I have not invented any. Before the parent paper makes a claim about what those papers do or do not say, someone must read the SCP 2013 article, pp. 345–363, directly. This is flagged in §8.

---

## 5. COUNTER-EVIDENCE SECTION

Every source found that weakens the parent paper's motivating claim, stated without hedging.

### 5.1 Mutation score does predict real-fault detection

1. **Just et al. (2014), FSE.** Mutant detection correlated with real-fault detection across 357 real faults, the correlation was stronger than for statement coverage, and **it survived controlling for test-suite size.** This is the single most cited rebuttal to any claim that mutation score is not a valid fault-detection proxy.
2. **Chekam et al. (2017), ICSE.** After removing the unreliable clean-program assumption — a methodological correction that cuts *against* prior pro-mutation results — mutation still revealed more faults than statement or branch coverage.
3. **Andrews et al. (2005), ICSE; Andrews et al. (2006), TSE.** Mutants gave fault-detection estimates comparable to real faults, and were *more* representative than hand-seeded faults.
4. **Zhang et al. (2024), TOSEM.** Under a purpose-built evaluation framework (ASSENT) using real faults as ground truth, "**mutation score, and subsuming mutation score are the best metrics to quantify test suite effectiveness**" — better than every code-coverage metric tested.
5. **Lu et al. (2026), TOSEM.** After explicitly removing the test-suite-size confound by regression, "**mutation score demonstrates superior effectiveness in predicting test suite effectiveness, while statement coverage is the least effective metric.**"
6. **Daran & Thévenod-Fosse (1996), ISSTA.** On real industrial safety-critical code, mutant-induced errors and real-fault-induced errors were comparable in their error mechanisms.
7. **Delgado-Pérez et al. (2018), *IEEE Transactions on Reliability*.** Mutation testing was evaluated favourably on nuclear industry software — the parent project's own adjacent domain.

### 5.2 The "weak correlation after size control" result is methodologically contested

8. **Chen et al. (2020), ASE.** Explicitly addresses "the supposed contradiction of prior work" and concludes that **test set size is neither a confounding variable, as previously suggested, nor an independent variable that should be experimentally manipulated.** If this is right, the Papadakis et al. (2018) negative result rests on an inappropriate experimental design, and the strongest published support for mutation-score construct invalidity is weakened at its foundation. The parent paper cannot cite Papadakis et al. (2018) without engaging Chen et al. (2020).

### 5.3 Mutation already works well as an oracle-assessment instrument

9. **Staats, Gay & Heimdahl (2012), ICSE.** Mutation is used successfully to decide which variables an oracle should check, and the paper's title is an explicit endorsement ("...how I learned to stop worrying about fault propagation and love mutation testing").
10. **Jahangirova et al. (2016), ISSTA; Jahangirova et al. (2021), TSE.** A mutation-based oracle assessment and improvement framework, empirically validated in a TSE paper as producing real oracle improvement. Mutation *is* an accepted, validated instrument for oracle adequacy — which is exactly the use the parent paper questions.
11. **Knauth et al. (2009), ICSTW; Knüppel et al. (2021), FormaliSE.** Mutation analysis already measures the completeness of declared obligations (contracts, JML specifications). The evaluation shape the parent paper proposes for MR sets is established practice.
12. **Fraser & Zeller (2012), TSE.** Mutation drives the generation of oracles, not just their assessment.

### 5.4 Mutation approaches already target semantic and domain properties

13. **Dan & Hierons (2012b), ICST — "Semantic Mutation Analysis of Floating-Point Comparison."** Semantic mutation has already been applied to *numerical* semantics by the technique's originators. A claim that no mutation family targets semantics in numerical code is false.
14. **Hook & Kelly (2009), CiSE — "Mutation Sensitivity Testing"; Hook & Kelly (2009), SECSE; Gray & Kelly (2010), *Procedia CS*.** Mutation has been adapted specifically to scientific computing, with explicit handling of the tolerance-based oracle. The intersection "mutation × scientific computing" is not empty.
15. **Humbatova et al. (2021), ISSTA — DeepCrime.** Operators derived from a real-fault taxonomy rather than a language grammar, with a redefined killing criterion. The "replace the grammar-derived denominator with a domain-derived one" move is already accepted practice in the field.
16. **Budd & Gopal (1985), *Computer Languages*.** Mutating the declared specification instead of the code is a 1985 idea.
17. **Cazzola & Favalli (2023), *JSS*; Derezińska & Zaremba (2018), FedCSIS; Huang & Alexander (2015), EMAS; Cao et al. (2015), ICIA.** The semantic-mutation lineage is active and has produced domain instantiations across UML, concurrency, agents and interpreters.

### 5.5 An alternative oracle-quality metric already claims to beat mutation

18. **Schuler & Zeller (2013), *STVR* 23(7).** "Our experiments on seven open-source projects show that **checked coverage is a sure indicator for oracle quality and even more sensitive than mutation testing.**" If a non-mutation metric is more sensitive for oracle quality, a reviewer will ask why a new *mutation-based* metric is the right instrument for MR-set adequacy.

### 5.6 The field's remedy for weak syntactic operators is LLM generation, not specification derivation

19. **Wang et al. (2026), TOSEM.** LLM-generated mutants reach 77.4% real-bug detection versus 41.6% for rule-based techniques. This strongly supports the premise that default syntactic catalogs are a weak proxy — but it also shows the community's chosen fix is a different one from the parent paper's, and it sets a high empirical bar: a new mutant family will be asked how it compares to 77.4%.
20. **Tip et al. (2025), TSE.** Same direction: fixed operator sets cannot simulate certain real bug classes, and the remedy demonstrated is LLM-generated mutants.

### 5.7 The field already documents the construct threats

21. **Papadakis et al. (2016), ISSTA; Papadakis et al. (2019), *Advances in Computers*; Kurtz et al. (2016), FSE; Kintis et al. (2018), *EMSE*; Petrović et al. (2022), TSE.** Equivalent mutants, subsumption, redundancy, tool disagreement and industrial filtering are all documented at length by the mutation-testing community itself. A framing that presents these threats as newly noticed will not survive review; the parent paper's contribution must be the *equation-level construct argument*, not the observation that the denominator is imperfect.

---

## 6. 检索审计表 (Search Audit Table)

Legend: ✓ = fully verified (title, authors, venue, year, and where applicable volume/issue/pages) through a `user-paper-search` call. △ = verified to exist with a caveat recorded. ✗ = could not be confirmed.

Tool-chain abbreviations: `xref-doi` = `get_crossref_paper_by_doi`; `xref-q` = `search_crossref`; `oa` = `search_openalex`; `arxiv` = `search_arxiv`; `unpay` = `search_unpaywall`; `dblp` = `search_dblp`; `sem` = `search_semantic`; `base` = `search_base`.

| Ref | 工具链 | 命中工具 | 状态 |
|---|---|---|---|
| Hamlet (1977) TSE | xref-doi | xref-doi | ✓ |
| DeMillo, Lipton & Sayward (1978) Computer | xref-doi | xref-doi | ✓ |
| Budd, DeMillo, Lipton & Sayward (1980) POPL | xref-doi | xref-doi | ✓ |
| Offutt (1989) TAV3 | xref-doi | xref-doi | ✓ |
| Offutt (1992) TOSEM | xref-doi | xref-doi | ✓ |
| Ammann & Offutt (2016) CUP 2nd ed. | xref-q | xref-q | ✓ |
| Ammann & Offutt (2008) CUP 1st ed. | xref-q | xref-q | ✓ |
| Jia & Harman (2011) TSE | xref-doi | xref-doi | ✓ |
| Papadakis et al. (2019) Adv. Comput. | xref-doi → oa | oa | △ CrossRef returns empty author list; authors confirmed via OpenAlex W2725449579. Online-first 2018, print 2019 |
| Zhu, Panichella & Zaidman (2018) STVR | xref-doi | xref-doi | ✓ |
| Daran & Thévenod-Fosse (1996) ISSTA | xref-doi | xref-doi | △ CrossRef stores truncated title "Software error analysis" without subtitle |
| Andrews, Briand & Labiche (2005) ICSE | xref-doi | xref-doi | △ CrossRef page field reads "402" only; proceedings range is 402–411 |
| Andrews, Briand, Labiche & Namin (2006) TSE | xref-doi | xref-doi | ✓ |
| Namin & Andrews (2009) ISSTA | xref-doi | xref-doi | ✓ |
| Just et al. (2014) FSE | xref-doi | xref-doi | ✓ |
| Inozemtseva & Holmes (2014) ICSE | xref-doi | xref-doi | ✓ |
| Chekam et al. (2017) ICSE | xref-doi | xref-doi | ✓ |
| Papadakis, Shin, Yoo & Bae (2018) ICSE | xref-doi | xref-doi | △ CrossRef title omits the subtitle "A Large Scale Empirical Study..." |
| Chen et al. (2020) ASE | xref-doi | xref-doi | ✓ |
| Laurent, Gaffney & Ventresque (2022) ICSTW | xref-doi | xref-doi | ✓ |
| Gay & Salahirad (2023) ICST | xref-doi | xref-doi | ✓ |
| Ojdanić et al. (2023) TSE | xref-q | xref-q | ✓ |
| Ahmed et al. (2024) STVR | xref-doi | xref-doi | ✓ |
| Zhang et al. (2024) TOSEM | xref-doi | xref-doi | △ Undermind dates 2023 (online-first); CrossRef print 2024-04-17, vol 33(4) |
| Lu et al. (2026) TOSEM | xref-doi | xref-doi | △ Undermind dates 2025 (online-first); CrossRef print 2026-04-24, vol 35(5) |
| Clark, Dan & Hierons (2010) ICSTW | xref-q | xref-q | ✓ |
| Clark, Dan & Hierons (2013) SCP | xref-q → oa → unpay | xref-q | △ Print 2013 (78(4):345–363); OpenAlex online-first 2011-04-22. Full text not retrievable (§4.4) |
| Dan & Hierons (2012a) ICST SMT-C | xref-q | xref-q | △ Registered title contains "Tools" (grammatical error in the record); full text not retrievable |
| Dan & Hierons (2012b) ICST floating-point | xref-q | xref-q | △ Full text not retrievable |
| Ghani (2013) JSEA | xref-doi | xref-doi | ✓ |
| Huang & Alexander (2015) EMAS/LNCS | xref-doi | xref-doi | ✓ |
| Derezińska & Zaremba (2018) FedCSIS | xref-doi | xref-doi | ✓ |
| Cao et al. (2015) ICIA | xref-doi | xref-doi | ✓ |
| Cazzola & Favalli (2023) JSS | xref-doi | xref-doi | △ Online-first 2022-10; print vol 195 dated 2023-01 |
| Jia & Harman (2008) SCAM | xref-q | xref-q | ✓ |
| Jia & Harman (2009) IST | xref-doi | xref-doi | ✓ |
| Harman, Jia & Langdon (2010) ICSTW | xref-doi | xref-doi | ✓ |
| Hook & Kelly (2009) CiSE | xref-q → xref-doi | xref-doi | △ Two CrossRef DOIs exist (`10.1109/MCSE.2009.157` early record, `10.1109/MCSE.2009.200` canonical) |
| Hook & Kelly (2009) SECSE | xref-q → xref-doi | xref-doi | ✓ |
| Gray & Kelly (2010) Procedia CS | xref-q | xref-q | ✓ |
| Delgado-Pérez et al. (2018) IEEE TR | xref-doi | xref-doi | ✓ |
| Jahangirova & Tonella (2020) ICST | xref-doi | xref-doi | ✓ |
| Humbatova et al. (2021) ISSTA DeepCrime | xref-q | xref-q | ✓ |
| Degiovanni & Papadakis (2022) ICSTW µBert | xref-q | xref-q | △ Registered title uses "µBert", not "µBERT" |
| Tip, Bell & Schäfer (2024) arXiv | arxiv | arxiv | ✓ arXiv:2404.09952v2, cs.SE |
| Tip, Bell & Schäfer (2025) TSE | xref-q → xref-doi | xref-doi | ✓ 51(6):1645–1665 |
| Wang et al. (2026) TOSEM | xref-doi → arxiv → sem → xref-q | xref-q | △ arXiv preprint (2406.09843) not resolvable: `xref-doi` empty, `arxiv` no match, `sem` empty output. Published TOSEM version located and verified instead; title differs from the preprint ("A Comprehensive Study..." vs "An Exploratory Study...") — **treat as a distinct, superseding work, not the same record** |
| Budd & Angluin (1982) Acta Informatica | xref-doi | xref-doi | ✓ |
| Wong & Mathur (1995) JSS | xref-q | xref-q | ✓ |
| Offutt et al. (1996) TOSEM | xref-doi | xref-doi | ✓ |
| Offutt & Hayes (1996) ISSTA | xref-doi | xref-doi | ✓ |
| Offutt & Pan (1997) STVR | xref-q | xref-q | △ DOI contains angle brackets; must be URL-encoded in BibTeX |
| Namin & Kakarla (2011) ISSTA | xref-doi | xref-doi | ✓ |
| Just, Kapfhammer & Schweiggert (2012) ICST | xref-doi | xref-doi | ✓ |
| Yao, Harman & Jia (2014) ICSE | xref-doi | xref-doi | ✓ |
| Ammann, Delamaro & Offutt (2014) ICST | xref-q | xref-q | ✓ |
| Papadakis, Jia, Harman & Le Traon (2015) ICSE | xref-q | xref-q | ✓ |
| Gopinath et al. (2016) ICSTW | xref-doi | xref-doi | ✓ |
| Kurtz et al. (2016) ICSTW | xref-q | xref-q | ✓ |
| Kurtz et al. (2016) FSE | xref-q | xref-q | ✓ |
| Papadakis et al. (2016) ISSTA | xref-q | xref-q | ✓ |
| Laurent et al. (2017) ICST PIT | xref-doi | xref-doi | △ Undermind labels this 2016; CrossRef confirms ICST 2017, 430–435 |
| Kintis et al. (2018) TSE | xref-doi | xref-doi | ✓ |
| Kintis et al. (2018) EMSE | xref-q | xref-q | △ Online-first 2017-12-21; print vol 23(4) dated 2018 |
| Papadakis, Chekam & Le Traon (2018) ICSTW | xref-doi | xref-doi | ✓ |
| Petrović & Ivanković (2018) ICSE-SEIP | xref-q | xref-q | ✓ |
| Hariri et al. (2019) ICST | xref-doi | xref-doi | ✓ |
| Chekam et al. (2020) EMSE | xref-doi | xref-doi | △ Undermind dates 2018; CrossRef online-first 2019-12-18, print vol 25(1) 2020 |
| Beller et al. (2021) ICSE-SEIP | xref-doi | xref-doi | △ Undermind dates 2020; CrossRef confirms ICSE-SEIP 2021 |
| Petrović et al. (2021) ICSE | xref-doi | xref-doi | ✓ |
| Petrović et al. (2022) TSE | xref-q | xref-q | △ Undermind dates 2021 (online-first); CrossRef print 2022-10, vol 48(10) |
| Ojdanić et al. (2022) EMSE | xref-doi | xref-doi | ✓ |
| Alblwi, Ayad & Mili (2024) AST | xref-doi | xref-doi | ✓ Self-referential title verified as registered |
| Kushigian et al. (2024) ISSTA | xref-doi | xref-doi | ✓ |
| Barr et al. (2015) TSE | xref-doi | xref-doi | ✓ |
| Budd & Gopal (1985) Computer Languages | xref-doi | xref-doi | ✓ |
| Knauth, Fetzer & Felber (2009) ICSTW | xref-doi | xref-doi | ✓ |
| Schuler, Dallmeier & Zeller (2009) ISSTA | xref-doi | xref-doi | ✓ |
| Schuler & Zeller (2011) ICST | xref-q | xref-q | ✓ |
| Schuler & Zeller (2013) STVR | xref-q | xref-q | ✓ |
| Staats, Whalen & Heimdahl (2011) ICSE | xref-q | xref-q | △ CrossRef registers title without subtitle "the foundations of testing revisited"; DOI is 10.1145/1985793.1985847, **not** ...1985838 |
| Shrestha & Rutherford (2011) ICST | xref-doi | xref-doi | ✓ |
| Staats, Gay & Heimdahl (2012) ICSE | xref-doi | xref-doi | ✓ |
| Fraser & Zeller (2010) ISSTA | xref-doi | xref-doi | ✓ |
| Fraser & Zeller (2012) TSE | xref-q | xref-q | △ Undermind conflated TSE title/pages with the ISSTA DOI; both records resolved separately |
| Zhang & Mesbah (2015) FSE | xref-doi | xref-doi | ✓ |
| Jahangirova et al. (2016) ISSTA | xref-q | xref-q | ✓ |
| Jahangirova et al. (2018) ISSTA OASIs | xref-q | xref-q | ✓ |
| Jahangirova et al. (2021) TSE | xref-q | xref-q | △ Online-first 2019-08; print vol 47(8) 2021 |
| Knüppel, Schaer & Schaefer (2021) FormaliSE | xref-doi | xref-doi | ✓ |
| Cordy et al. (2023) ESEC/FSE | xref-doi | xref-doi | ✓ |
| Kanewala & Bieman (2013) SE-CSE | xref-doi | xref-doi | ✓ |
| Molina, Aguirre & Gorla (2025) ASE | xref-q | xref-q | ✓ |
| Maton, Kapfhammer & McMinn (2025) ESEM | xref-doi | xref-doi | ✓ |

**Totals:** 94 rows. ✓ = 71. △ = 23. **✗ = 0.**

Every △ carries a recorded, specific caveat; none is an existence doubt. No entry rests on Undermind's authority alone.

### 6.1 Candidates rejected under the gray-zone rule (not in the bibliography)

| Candidate | Reason | Status |
|---|---|---|
| Acree (1980), "On mutation" | Undermind DOI `10.1002/9781118662779.ch1` does not correspond to the Georgia Tech thesis | ✗ excluded |
| Gopinath, Jensen & Groce (2014), "Mutant census" | No DOI; Semantic Scholar link only | ✗ excluded |
| Agrawal et al. (2006), "Design of mutant operators for the C programming language" | Purdue technical report; no DOI | ✗ excluded |
| Maciel, Oliveira & Delamaro (2017), "Quality Evaluation of Test Oracles Using Mutation" | No DOI, no venue in any source; topically a direct B6 hit — **loss recorded in §7** | ✗ excluded |
| Goldweber et al. (2024), IronSpec | No DOI returned | ✗ excluded |
| Huang (2016), "Mutation for multi-agent systems" | Thesis, no DOI; superseded by Huang & Alexander (2015) | ✗ excluded |
| Jia & Harman, "Ieee Transactions on Software Engineering an Analysis and Survey..." (`Jia00`) | Ghost duplicate record, no year, mangled title | ✗ excluded |
| Li et al. (2026), "A semantic mutation metric for metamorphic relation adequacy..." | **Parent project's own preprint** | excluded by policy, flagged in §8 |

These eight are excluded, not counted as ✗ verification failures — the verification chain reported "cannot confirm", which under the gray-zone rule is a decision, not a failure.

---

## 7. Search Limitations

1. **`search_dblp` was non-functional throughout.** Two invocations returned empty output. Since dblp has the best coverage of SE conference proceedings and the declared priority chain put it first, its absence means conference papers were reached through CrossRef, which is weaker for workshop proceedings and for venues without DOI deposits. Any pre-1995 workshop paper or non-DOI technical report is likely under-represented in this bibliography as a direct consequence.
2. **`search_semantic` and `search_base` also returned empty output.** Three of the six tools in the declared chain were unavailable, so the effective chain was CrossRef-dominated. CrossRef's known weaknesses — truncated titles, empty author lists, missing page ranges — appear in the audit table as △ rows and were worked around by cross-checking OpenAlex.
3. **No full text was obtainable for the B3 primary sources.** See §4.4. The disambiguation memo is therefore grounded in successor-paper abstracts rather than in the originating papers' own prose, and carries no section- or page-level citations into Clark/Dan/Hierons.
4. **Single deep search.** One Undermind deep search (177 results) was consumed, as instructed. No second search was launched. The search's own goal statement covered all six sub-themes, but it framed the question around *oracle* adequacy; searches framed around "structure-preserving transformation", "conservation law", "invariant-violating fault injection", or "numerical property mutation" would likely surface a partly different corpus, particularly from computational-science venues outside the SE mainstream.
5. **B4 "mutation for numerical or scientific code" is genuinely thin, and that thinness is a finding.** Query Q12 (`mutation testing scientific computing software numerical programs oracle problem`) returned almost nothing on-topic — its top hits were a numerical-methods textbook and an unrelated dissertation. The productive query was Q18, which required already knowing the Hook & Kelly names. **The searchable literature on mutation testing specifically for scientific computing appears to consist of roughly four works** (Hook & Kelly 2009 ×2; Gray & Kelly 2010; Dan & Hierons 2012b on floating-point), plus the nuclear-domain case study of Delgado-Pérez et al. (2018). This is a real gap, not a search failure — but it also means the parent paper cannot rely on the deep search alone to establish that no closer prior art exists.
6. **One topically central B6 item was lost to the gray-zone rule.** Maciel, Oliveira & Delamaro's "Quality Evaluation of Test Oracles Using Mutation" (2017) ranked r=1.170 — fourth overall in the deep search — and its title describes the parent paper's exact evaluation shape. No DOI and no venue could be established through any tool. It is excluded, but its absence is a substantive hole in the B6 coverage and should be resolved manually.
7. **Language and document-type restrictions.** English only; no theses, technical reports, or standards. Chinese-language mutation-testing literature was not searched, and the Cao et al. (2015) entry suggests a Chinese-venue semantic-mutation strand may exist beyond what CrossRef indexes.
8. **Recency boundary effects.** Three included works (Lu et al. 2026 TOSEM; Wang et al. 2026 TOSEM; Molina et al. 2025 ASE) are advance-online or very recent, with incomplete bibliographic records and near-zero citation counts. Their metadata will change.

---

## 8. Handoff Notes

- The parent project's own preprint (Li et al., 2026, arXiv:2605.17437, "A semantic mutation metric for metamorphic relation adequacy in scientific computing programs") surfaced at **r=1.180, third overall** in the deep search. It is excluded from the bibliography as prior art; the caller should decide how to handle self-citation and whether its presence in the index affects claims of novelty.
- Full texts of Clark/Dan/Hierons (2010, 2013) and Dan & Hierons (2012a, 2012b) could not be retrieved through any of four routes. §4 is built on successor-paper abstracts and carries no section/page citations into the primary sources. **Someone must read SCP 78(4):345–363 directly before the paper asserts what that lineage does or does not claim.**
- Three distinct prior lineages already mutate-to-assess-a-declared-obligation: specification mutation (Budd & Gopal, 1985), contract-completeness mutation analysis (Knauth et al., 2009; Knüppel et al., 2021), and mutation-based oracle assessment (Staats et al., 2012; Jahangirova et al., 2016, 2021). Semantic mutation testing is not the nearest neighbour on the dimension that matters.
- Two counter-evidence items are load-bearing and were not anticipated in the theme brief: Chen et al. (2020, ASE) argues test-set size is not a confounder at all, which undercuts the Papadakis et al. (2018) negative result; and Schuler & Zeller (2013, STVR) reports checked coverage as "more sensitive than mutation testing" for oracle quality specifically.
- Mutation testing applied to scientific computing amounts to about four searchable works, all from the Hook/Kelly/Queen's group plus Dan & Hierons on floating-point. If a second Undermind deep search is authorised, frame it on structure-preservation / conservation-law / invariant-violating fault injection in computational science rather than on mutation-score validity, which this search has exhausted.

---

*Deep search referenced: https://app.undermind.ai/projects/d9baef75-52ff-4860-b661-6d7a9e647f42?path=%2Fmutation%20score%20construct%20validity%20oracle%20adequacy%20semantic%20mutation*
