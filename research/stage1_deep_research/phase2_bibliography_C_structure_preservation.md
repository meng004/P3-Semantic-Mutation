# Phase 2 Bibliography — Theme C: Structure Preservation in Numerical Methods and Its Intersection with Software Testing

**Agent**: `bibliography_agent` (ARS deep-research pipeline, Phase 2 INVESTIGATION)
**Target venue of parent paper**: ACM TOSEM
**Theme**: C (C1–C5), the novelty-critical theme for P3 v4 (ESPR / SPTM / SLRMA)
**Date compiled**: 2026-09-07
**Scope**: bibliography only. No synthesis, no gap analysis, no paper sections.

---

## 1. Search Strategy

### 1.1 Two-tool division of labour

| Role | Tool | Use |
|---|---|---|
| Discovery (现状) | `user-undermind` | ranked candidate harvesting, DOI/cite-key resolution |
| Verification (文献核对) | `user-paper-search` | independent confirmation of every retained entry |

**Iron rule applied**: no entry appears below on Undermind's authority alone. Every included reference was re-resolved through at least one `user-paper-search` call that returned matching title + authors + venue (+ volume/issue/pages where the record carries them).

### 1.2 Undermind deep searches consumed

Workspace `d9baef75-52ff-4860-b661-6d7a9e647f42`. **No new deep searches were launched** (cost constraint respected).

| # | Search | Status when read | Ranked results | Read depth |
|---|---|---|---|---|
| DS1 | `/structure preserving property violation as fault model scientific software` | completed (polled once at `in_progress`, then completed) | 98 | top 50, `detail_level=standard` |
| DS2 | `/科学计算代码验证与缺陷辨识` | completed previously | 134 | top 50, `detail_level=standard` |

DS1 is the prior-art probe and carries the C3 verdict. Its stated research goal asked precisely the C3 question (violation of a mathematical/physical structural property used as a deliberate fault model, mutation target, or test-adequacy denominator), plus the C4 sub-question on independent certification mechanisms.

`get_paper_info(show_doi=true, detail_level=standard)` was then run over a 30-key batch to obtain DOIs / stable links for all DS1 candidates worth verifying.

### 1.3 Own paper-search queries (exact strings)

Boolean logic note: the `user-paper-search` Crossref/OpenAlex/arXiv wrappers accept free-text bags of words, not explicit `AND`/`OR` operators. Multi-concept intersection was therefore expressed by term co-occurrence (implicit AND over a keyword bag), and disjunction by running separate queries. Where a canonical author surname was known it was appended to pin the record. Date range: **unrestricted** (the C1 canon is 1983–2014 and the C3 frontier is 2019–2026, so any date cut would have been destructive). Language: **English only** in effect — no non-English records surfaced above the relevance floor. Document types accepted: journal article, conference proceedings article, monograph, book chapter, technical report, arXiv preprint.

**Numerical-analysis chain** (`search_crossref` → `search_openalex` → `search_arxiv` math.NA → `search_semantic`):

1. `Geometric Numerical Integration Structure-Preserving Algorithms for Ordinary Differential Equations Hairer Lubich Wanner`
2. `get_crossref_paper_by_doi: 10.1007/3-540-30666-8` (book-level DOI resolution)
3. `Finite element exterior calculus homological techniques and applications Arnold Falk Winther Acta Numerica`
4. `Discrete mechanics and variational integrators Marsden West Acta Numerica`
5. `Mimetic finite difference method Lipnikov Manzini Shashkov Journal of Computational Physics`
6. `Topics in structure-preserving discretization Christiansen Munthe-Kaas Owren Acta Numerica`
7. `Principles of mimetic discretizations of differential operators Bochev Hyman`
8. `Maximum-principle-satisfying and positivity-preserving high order schemes conservation laws survey Zhang Shu`
9. `Discrete Conservation Properties of Unstructured Mesh Schemes Perot Annual Review Fluid Mechanics`
10. `High resolution schemes for hyperbolic conservation laws Harten Journal of Computational Physics 1983`
11. `Entropy stability theory for difference approximations of nonlinear conservation laws and related time-dependent problems Tadmor Acta Numerica`
12. `Simulating Hamiltonian Dynamics Leimkuhler Reich Cambridge Monographs on Applied and Computational Mathematics`
13. `Compatible Spatial Discretizations Arnold Bochev Lehoucq Nicolaides Shashkov IMA Volumes Mathematics Applications`
14. `Finite Volume Methods for Hyperbolic Problems LeVeque Cambridge Texts in Applied Mathematics`
15. `Discrete exterior calculus Desbrun Hirani Leok Marsden`

**Verification-practice chain**:

16. `Code Verification by the Method of Manufactured Solutions Roache Journal of Fluids Engineering 2002`
17. `Review of code and solution verification procedures for computational simulation Roy Journal of Computational Physics 2005`
18. `Verification and Validation in Scientific Computing Oberkampf Roy Cambridge University Press`
19. `Perspective A Method for Uniform Reporting of Grid Refinement Studies Roache 1994 Journal of Fluids Engineering`
20. `get_crossref_paper_by_doi: 10.1115/1.4049230` (Krueger MEAMMS)

**Certification-mechanism chain (C4)**:

21. `An introduction to the adjoint approach to design Giles Pierce Flow Turbulence and Combustion`
22. `Superconvergent functional estimates from summation-by-parts finite difference discretizations dual consistency Hicken Zingg`
23. `An optimal control approach to a posteriori error estimation in finite element methods Becker Rannacher Acta Numerica`
24. `get_crossref_paper_by_doi: 10.2514/6.2018-4154` (adjoint dot-product / consistency tests)
25. `get_crossref_paper_by_doi: 10.1016/j.cma.2008.04.020` (objectivity / symmetry tests)
26. `get_crossref_paper_by_doi: 10.1002/fld.1650170106` (global balance diagnostics)
27. `Silent error detection in numerical time-stepping schemes Benson Schmit Schreiber`
28. `Shock with Confidence Formal Proofs of Correctness for Hyperbolic Partial Differential Equation Solvers Gorard Hakim`

**Software-engineering chain (C3, C5)** — intended as `search_dblp` → `search_arxiv` cs.SE → `search_crossref`; **`search_dblp` failed on every attempt** (see §6), so the chain degraded to arXiv/Crossref/OpenAlex:

29. `metamorphic relation conservation law physical property scientific software testing` (dblp — empty)
30. `physics-based fault injection numerical simulation mutation invariant violation` (dblp — empty)
31. `metamorphic relations conservation laws` (dblp — empty)
32. `mutation testing scientific software` (dblp — empty)
33. `metamorphic testing` (dblp minimal control query — empty ⇒ tool-level failure, not query-level)
34. `conservation violating fault model mutation testing scientific computing adequacy` (crossref)
35. `physics-informed testing oracle conservation law violation mutation scientific software` (arXiv)
36. `metamorphic testing scientific software physical symmetry invariant oracle problem numerical program` (crossref)
37. `Property-Based Mutation Testing Bartocci Mariani Nickovic Yadav` (crossref)
38. `physics-based fault injection conservation law invariant detector silent data corruption numerical simulation` (OpenAlex)
39. `mutation testing metamorphic relation adequacy scientific computing structure preserving property violation fault model` (OpenAlex)
40. `semantic mutation metric metamorphic relation adequacy scientific computing programs` (arXiv)
41. `Minimum Complete MR Subsets Semantic-Mutation Fault Models Support-Set Domination Boundary` (arXiv)
42. `get_crossref_paper_by_doi: 10.1109/QRS.2019.00057` (invariant relations)
43. `Kanewala Bieman testing scientific software systematic literature review metamorphic relations machine learning` (crossref)
44. `Application of metamorphic testing monitored by test adequacy Monte Carlo simulation program Ding Hu Software Quality Journal` (crossref)
45. `Metamorphic testing of programs on partial differential equations case study Chen Feng Tse COMPSAC 2002` (crossref)
46. `Testing Ocean Software with Metamorphic Testing Luu Zhou Vu MET 2022` (crossref)
47. `Hierarchical Metamorphic Relations for Testing Scientific Software Lin Simon Niu SE4Science 2018` (crossref)
48. `Test Adequacy for Metamorphic Testing Criteria Measurement and Implication` (arXiv)
49. `Hook Kelly mutation sensitivity testing scientific software oracle problem tolerance` (crossref)
50. `comprehensive study of real world numerical bug characteristics scientific software Di Franco` (crossref)
51. `Testing high performance numerical simulation programs experience lessons learned open issues He ISSTA 2020` (crossref)
52. `Eisty Carver Testing research software a survey Empirical Software Engineering` (crossref)
53. `Resilience in Numerical Methods: A Position on Fault Models and Methodologies` (semantic — empty), retried as `Resilience Numerical Methods Position Fault Models Methodologies sparse linear solver soft fault` (arXiv — hit)

Total `user-paper-search` calls: **53** (47 productive, 6 tool-level failures).

### 1.4 Inclusion / exclusion criteria

**Included** when all four hold:
- (I1) Independently confirmed by ≥ 1 `user-paper-search` call returning matching title + author set + venue.
- (I2) Substantively bears on C1, C2, C3, C4 or C5 as scoped in the assignment.
- (I3) Peer-reviewed venue, recognised monograph, standards-body document, national-laboratory report, or arXiv preprint **explicitly labelled as a preprint**.
- (I4) Bibliographic fields (volume / issue / pages / DOI) reproduced exactly as returned, never reconstructed from memory.

**Excluded** when any hold:
- (E1) Cannot be confirmed through paper-search — gray zone counts as FAIL, item dropped.
- (E2) Structure-preservation topic without any testing/verification/fault-model bearing and without canonical status (e.g. individual mimetic-scheme application papers on Stokes or Maxwell).
- (E3) Mutation/metamorphic testing with no numerical, physical or equation-level content (DL/LLM/smart-contract/machine-translation mutation work).
- (E4) Duplicate DOI variants of the same record (e.g. the four `Learning from mistakes` SIG-newsletter reprints; the two `Mutation Sensitivity Testing` DOIs; the paired `10.1109/taicpart.*` / `10.1109/taic.part.*` records).
- (E5) Book chapters of a monograph already included at book level (the ten `10.1007/3-540-30666-8_*` and `10.1017/cbo9780511791253.*` chapter DOIs).

---

## 2. PRISMA-style Flow

```
IDENTIFICATION
  Undermind DS1 (prior-art probe, structure-violation-as-fault-model)     98
  Undermind DS2 (scientific-computing code verification, Chinese)        134
  paper-search Crossref (32 queries)                                    ~186
  paper-search get_crossref_paper_by_doi (6 targeted DOI resolutions)       6
  paper-search arXiv (7 queries)                                          ~49
  paper-search OpenAlex (2 queries)                                       ~16
  paper-search dblp (5 queries)                                             0   [tool failure]
  paper-search Semantic Scholar (1 query)                                   0   [tool failure]
  WebFetch (3 attempts, ASME V&V 20 standard page)                          0   [404]
                                                                    ---------
  Gross records identified                                                489

DE-DUPLICATION
  Cross-source duplicates removed (DS1 ∩ DS2 ∩ Crossref ∩ OpenAlex)      -71
  Same-work DOI variants removed (E4)                                     -14
  Monograph chapter-level DOIs collapsed to book level (E5)               -16
                                                                    ---------
  Unique records after de-duplication                                     388

SCREENING (title + abstract + venue)
  Screened                                                                388
  Excluded, off-topic query noise (E2/E3): DL/LLM/smart-contract
    mutation, ML-testing surveys, CPS anomaly detection, HPC
    checkpointing, unrelated math.AP/quant-ph/cond-mat hits             -281
                                                                    ---------
  Records sought for verification                                         107

ELIGIBILITY (independent paper-search verification attempted)
  Verification attempted                                                  107
  Failed verification / could not be independently confirmed (E1)          -3
    - ASME V&V 20-2009 standard (3 route attempts, all failed)
    - Chan, Kuo, Chen & Yiu (1998) "Application of metamorphic
      testing in numerical analysis" — no DOI, Undermind link is a
      Semantic Scholar stub; not confirmable via Crossref/arXiv/OpenAlex
    - Last & Friedman (2004) "Automated detection of injected faults
      in a differential equation solver" — DOI 10.1109/HASE.2004.1281751
      from Undermind only; not re-resolved through paper-search
  Verified but held in reserve (redundant with an included entry, or
    outside C1–C5 scope after full-record inspection)                     -66
                                                                    ---------
INCLUDED                                                                   38
    C1 structure-preserving discretization                                  9
    C2 verification of scientific software                                  7
    C3 prior-art frontier                                                  11
    C4 independent certification mechanisms                                 7
    C5 real-fault datasets / bug studies                                    4
```

Note on the target range: the assignment set a target of 25–35 included sources; the final count is **38**. The overshoot of 3 is concentrated in C3, where the prior-art verdict requires that every nearest neighbour be named explicitly rather than compressed.

---

## 3. Annotated Bibliography

### C1 — Structure-Preserving Discretization (source of the ESPR concept)

**C1.1** Hairer, E., Lubich, C., & Wanner, G. (2006). *Geometric numerical integration: Structure-preserving algorithms for ordinary differential equations* (2nd ed.). Springer-Verlag. https://doi.org/10.1007/3-540-30666-8

- **Relevance**: The canonical statement of the ESPR premise — that a discretization should inherit structural properties (symplecticity, first integrals, reversibility, volume preservation) of the continuous flow, and that failing to inherit them is a *qualitative* defect not captured by local truncation error.
- **Key findings**: (1) Structure preservation and order of accuracy are independent axes; a high-order scheme can destroy symplecticity and a low-order one can preserve it. (2) Backward error analysis explains long-time qualitative fidelity: a structure-preserving integrator solves a nearby modified Hamiltonian system exactly. (3) Symmetric/reversible integration and structure-preserving implementation are separable design concerns (dedicated chapters on "Structure-Preserving Implementation" and "Backward Error Analysis and Structure Preservation").
- **Methodology**: Monograph; constructive scheme design plus asymptotic/backward-error analysis.
- **Quality / limitations**: Springer Series in Computational Mathematics; the field's standard reference. Confined to ODEs and Hamiltonian/reversible structure; says nothing about software faults, testing or adequacy. Crossref record carries ISBN 3540306633 and the 2006 second-edition date; the 2002 first edition is a distinct DOI (`10.1007/978-3-662-05018-7`) and must not be conflated.
- **Contribution to Theme C**: Supplies φ (the property), κ (exact vs. approximate vs. asymptotic preservation) and the vocabulary of "preservation mode" that ESPR formalises.

**C1.2** Marsden, J. E., & West, M. (2001). Discrete mechanics and variational integrators. *Acta Numerica*, *10*, 357–514. https://doi.org/10.1017/s096249290100006x

- **Relevance**: Derives structure preservation from a discrete variational principle, giving a *mechanism* for why a scheme preserves what it preserves — directly relevant to any claim that a mutation "makes the program violate" a property.
- **Key findings**: (1) Many symplectic schemes, including higher-order ones, follow from one discrete variational principle. (2) A discrete Noether theorem yields exact discrete momentum conservation from discrete symmetry. (3) Forces, dissipation and constraints admit natural variational treatment; Verlet, SHAKE, RATTLE, Newmark and symplectic partitioned Runge–Kutta are recovered as instances.
- **Methodology**: Survey with unified variational derivation.
- **Quality / limitations**: Acta Numerica, ~1150 citations. Finite-dimensional mechanical systems only; no PDE-level or software-level content.
- **Contribution**: The discrete Noether theorem is the cleanest available justification that a symmetry-derived ESPR should hold *exactly* (κ = exact) rather than approximately in a correctly implemented scheme.

**C1.3** Arnold, D. N., Falk, R. S., & Winther, R. (2006). Finite element exterior calculus, homological techniques, and applications. *Acta Numerica*, *15*, 1–155. https://doi.org/10.1017/s0962492906210018

- **Relevance**: The compatible-discretization pillar. Establishes that discretizations should be compatible with the geometric, topological and algebraic structures underlying well-posedness of the PDE.
- **Key findings**: (1) Many finite element spaces are spaces of piecewise polynomial differential forms sitting in discrete subcomplexes of elliptic differential complexes. (2) Projections commuting with the complex differential are what link discrete to continuous structure. (3) Applications span the Hodge Laplacian, Maxwell's equations, elasticity and elliptic eigenvalue problems.
- **Methodology**: Survey; differential geometry, algebraic topology, homological algebra applied to FEM stability analysis.
- **Quality / limitations**: Acta Numerica, ~758 citations. Highly abstract; the structures preserved are cohomological rather than the physically-named quantities an ESPR would target.
- **Contribution**: Supplies the *commuting-diagram* form of structure preservation, the natural home for an "operator commutator test" as an O-component.

**C1.4** Christiansen, S. H., Munthe-Kaas, H. Z., & Owren, B. (2011). Topics in structure-preserving discretization. *Acta Numerica*, *20*, 1–119. https://doi.org/10.1017/s096249291100002x

- **Relevance**: The single best "what is structure-preserving discretization" survey, spanning both time and space discretization — i.e. the exact intellectual territory P3 v4 borrows from.
- **Key findings**: (1) Structure-preserving discretization, geometric integration and compatible discretization are recognised as one subfield with three entry points. (2) Discrete gradients and discrete variational derivatives are the generic devices for preserving first integrals in time. (3) Preservation of domain symmetries drives Lie-group integrators for PDEs; mixed finite elements are recast via inverse systems of complexes of differential forms with interpolators/smoothers commuting with the exterior derivative.
- **Methodology**: Survey; Lie-group methods, discrete gradients, spectral elements, mixed FEM.
- **Quality / limitations**: Acta Numerica, ~100 citations. Selective by the authors' own admission; no fault-model or testing content.
- **Contribution**: The authoritative enumeration of candidate φ values (conservation of first integrals, symmetry/equivariance, complex-compatibility) that an ESPR lineage could be frozen against.

**C1.5** Bochev, P. B., & Hyman, J. M. (2006). Principles of mimetic discretizations of differential operators. In D. N. Arnold, P. B. Bochev, R. B. Lehoucq, R. A. Nicolaides, & M. Shashkov (Eds.), *Compatible spatial discretizations* (pp. 89–119). Springer New York. https://doi.org/10.1007/0-387-38034-5_5 [volume: https://doi.org/10.1007/0-387-38034-5]

- **Relevance**: States mimetic discretization as a set of *principles* — discrete operators must reproduce the vector-calculus identities and adjointness relations of their continuous counterparts.
- **Key findings**: (1) Mimetic discrete div/grad/curl can be constructed to satisfy exact discrete analogues of continuous identities. (2) Adjointness between discrete operators is a design constraint, not a byproduct. (3) The principles are grid-agnostic and apply on irregular/logically rectangular meshes.
- **Methodology**: Book chapter; constructive derivation of discrete operator families.
- **Quality / limitations**: IMA Volumes in Mathematics and its Applications (ISBN 9780387309163), ~76 citations for the chapter. Crossref returns a malformed 1970 publication date for the chapter-level record; the volume-level record dates the collection to 2006.
- **Contribution**: Adjointness-as-design-constraint is precisely the ESPR "adjoint" property, and its violation is directly checkable via a dot-product test (see C4.4).

**C1.6** Lipnikov, K., Manzini, G., & Shashkov, M. (2014). Mimetic finite difference method. *Journal of Computational Physics*, *257*, 1163–1227. https://doi.org/10.1016/j.jcp.2013.07.031

- **Relevance**: The consolidated review of the mimetic finite difference family, with explicit treatment of which structural properties are preserved and at what cost.
- **Key findings**: (1) MFD preserves fundamental properties of the continuous PDE (conservation, duality, symmetry of the operators) on general polygonal/polyhedral meshes. (2) The method's derivation makes the preserved identities explicit and auditable. (3) The framework covers diffusion, electromagnetics and flow applications under one construction.
- **Methodology**: Review article in the JCP special-issue format.
- **Quality / limitations**: JCP, ~411 citations. Crossref returns no abstract for this record, so the annotation above reflects the review's scope as evidenced by title, venue, page range (1163–1227) and the companion monograph (`10.1007/978-3-319-02663-3`), not a verified abstract text.
- **Contribution**: A worked catalogue of concrete, spatially discrete, checkable preservation identities — candidate ESPR instances with known error budgets B.

**C1.7** Zhang, X., & Shu, C.-W. (2011). Maximum-principle-satisfying and positivity-preserving high-order schemes for conservation laws: Survey and new developments. *Proceedings of the Royal Society A: Mathematical, Physical and Engineering Sciences*, *467*(2134), 2752–2776. https://doi.org/10.1098/rspa.2011.0153

- **Relevance**: The monotonicity/positivity limb of the ESPR taxonomy. Positivity of density, pressure or water height is a physically meaningful, cheaply observable structural property.
- **Key findings**: (1) Genuinely high-order finite volume and DG schemes can satisfy a *strict* maximum principle for scalar conservation laws. (2) The same construction preserves positivity of specific physical quantities for compressible Euler, shallow water and Vlasov–Boltzmann transport. (3) A simplified implementation substantially reduces cost, notably for WENO finite-volume schemes.
- **Methodology**: Survey plus new limiter construction; verified against the earlier Zhang & Shu (2010) *JCP* 229(9), 3091–3120 result (`10.1016/j.jcp.2009.12.030`).
- **Quality / limitations**: Proc. R. Soc. A, ~241 citations. Positivity is a one-sided inequality, so its violation is easier to certify than an equality-type conservation law — an asymmetry worth noting for the O component.
- **Contribution**: Supplies inequality-type φ with a naturally binary, tolerance-free observation method.

**C1.8** Perot, J. B. (2011). Discrete conservation properties of unstructured mesh schemes. *Annual Review of Fluid Mechanics*, *43*(1), 299–318. https://doi.org/10.1146/annurev-fluid-122109-160645

- **Relevance**: The most directly ESPR-shaped reference in C1. Distinguishes *primary* conservation (of the unknowns) from *secondary* conservation (of derived quantities such as kinetic energy, entropy, vorticity) and argues secondary conservation is far harder to achieve.
- **Key findings**: (1) Numerical methods with discrete conservation statements cannot produce solutions violating the corresponding physical constraint. (2) Local conservation of primary unknowns often follows from global conservation of those quantities. (3) Secondary conservation improves physical fidelity but is typically much harder to achieve; the review surveys current approaches and asks whether it could be obtained automatically.
- **Methodology**: Annual-Review survey of CFD discretization practice.
- **Quality / limitations**: ~100–119 citations. Fluid dynamics only; describes what schemes *do* preserve, not how to test whether an implementation actually does.
- **Contribution**: The primary/secondary conservation split maps onto the ESPR κ axis and predicts where structural violation should be easiest to inject and hardest to detect.

**C1.9** Harten, A. (1983). High resolution schemes for hyperbolic conservation laws. *Journal of Computational Physics*, *49*(3), 357–393. https://doi.org/10.1016/0021-9991(83)90136-5

- **Relevance**: The origin of total-variation-diminishing design — a structural constraint imposed on the discrete solution operator rather than on its accuracy.
- **Key findings**: (1) Second-order accuracy and non-oscillatory behaviour can be reconciled by enforcing a TVD property on the scheme. (2) The TVD condition is a checkable algebraic constraint on the numerical flux. (3) Conservation form plus the entropy/TVD constraint controls convergence to the physically correct weak solution.
- **Methodology**: Constructive scheme design with stability proofs.
- **Quality / limitations**: JCP, ~3265 citations. Crossref returns no abstract; annotation reflects the paper's canonical content and is anchored to the verified title/volume/pages. Note the distinct 1997 JCP reprint (`10.1006/jcph.1997.5713`, vol. 135(2), 260–278) with a Lax introduction — a different record.
- **Contribution**: Establishes that structural constraints on the *discrete operator* are legitimate, checkable design requirements — the pattern ESPR generalises.

---

### C2 — Verification of Scientific Software

**C2.1** Roache, P. J. (2002). Code verification by the method of manufactured solutions. *Journal of Fluids Engineering*, *124*(1), 4–10. https://doi.org/10.1115/1.1436090

- **Relevance**: The definitive statement of MMS and of the code-verification / calculation-verification distinction that P3 v4's O component must respect.
- **Key findings**: (1) Verification of *calculations* is error estimation; verification of *codes* is error evaluation against known benchmarks. (2) The best benchmarks are exact analytical solutions with sufficiently complex structure and need not be physically realistic — verification is a purely mathematical exercise. (3) Combined with systematic grid refinement, MMS yields "strong code verifications with a theorem-like quality and a clearly defined completion point".
- **Methodology**: Methodological paper with symbolic-manipulation workflow and simple worked examples.
- **Quality / limitations**: ASME JFE, ~524 citations. Published online 2001-11-12 in the 2002 volume. MMS verifies the implementation of a *selected* mathematical model; it is silent on model adequacy and, as the DS2 summary records, is weak against coding errors of the same order as the truncation error.
- **Contribution**: The reference O-component candidate, and the reason a same-order structural fault may be MMS-invisible.

**C2.2** Salari, K., & Knupp, P. (2000). *Code verification by the method of manufactured solutions* (SAND2000-1444). Office of Scientific and Technical Information, U.S. Department of Energy. https://doi.org/10.2172/759450

- **Relevance**: The blind-test study that established MMS's empirical detection rate — and its blind spots.
- **Key findings**: (1) MMS with order-of-accuracy verification detects a large fraction of deliberately seeded coding errors. (2) Some seeded defects nonetheless escape detection, so MMS is not a completeness proof. (3) Source-term construction is mechanisable for complex governing equations.
- **Methodology**: National-laboratory technical report; blind fault-seeding experiment.
- **Quality / limitations**: SAND report, ~170–678 citations depending on index. Not peer-reviewed in the journal sense; the Undermind record lists it without a journal ("Unknown Journal"), and the Crossref record types it as a `report`.
- **Contribution**: **This is the closest classical precedent for the P3 v4 experimental design** — deliberate fault seeding into a scientific code, with detection by a verification procedure as the measured outcome. The faults, however, are coding errors, not structural-property violations.

**C2.3** Roy, C. J. (2005). Review of code and solution verification procedures for computational simulation. *Journal of Computational Physics*, *205*(1), 131–156. https://doi.org/10.1016/j.jcp.2004.10.036

- **Relevance**: The consolidated procedural review of what counts as evidence in code verification versus solution verification.
- **Key findings**: Per the venue and DS1's use of it: (1) code verification (order-of-accuracy testing against exact/manufactured solutions) and solution verification (discretization-error estimation for a specific calculation) are distinct activities with distinct evidence standards; (2) observed order of accuracy is the discriminating diagnostic in code verification; (3) a posteriori error estimators serve solution verification.
- **Methodology**: Review article.
- **Quality / limitations**: JCP, ~410–544 citations. Crossref returns no abstract for this record; the three findings above are attributed to the paper's established scope and DS1's summary, not to a verified abstract.
- **Contribution**: Fixes the evidentiary vocabulary an ESPR's O component must slot into.

**C2.4** Oberkampf, W. L., & Roy, C. J. (2010). *Verification and validation in scientific computing*. Cambridge University Press. https://doi.org/10.1017/cbo9780511760396

- **Relevance**: The standard monograph. Provides the systematic development of V&V concepts, principles and procedures for PDE-governed models.
- **Key findings**: (1) V&V is developed comprehensively and systematically for models described by partial differential and integral equations and their numerical solution. (2) The methods generalise across physical sciences, engineering, and regulatory/safety contexts. (3) Framed explicitly around improving the credibility and reliability of simulation results for decision-makers.
- **Methodology**: Monograph (ISBN 9780521113601 / 9780511760396).
- **Quality / limitations**: ~868 citations. Superseded in part by the 2025 second edition, *Verification, validation, and uncertainty quantification in scientific computing* (`10.1017/9781009031004`), which was also verified; cite the edition actually consulted.
- **Contribution**: The authoritative source for the code-verification / solution-verification / validation trichotomy that bounds what an SPTM certification may legitimately claim.

**C2.5** American Institute of Aeronautics and Astronautics. (2021). *Recommended practice for code verification in computational fluid dynamics* (AIAA R-141-2021). AIAA. https://doi.org/10.2514/4.106385.001

- **Relevance**: The current standards-body statement of code-verification practice, and the natural compliance anchor for a paper proposing a new verification-adjacent construct.
- **Key findings**: Normative document; prescribes order-of-accuracy verification procedures, benchmark-solution requirements, and reporting expectations for CFD code verification.
- **Methodology**: Recommended-practice standard (ISBN 9781624106385).
- **Quality / limitations**: Standard, not a research paper; the Crossref record has no listed authors and is typed `book-chapter` under the volume title. Low citation count (~1) reflects recency and document type, not quality. **Note**: the sibling standard ASME V&V 20-2009 could *not* be verified (see §5 audit and §6) and is therefore excluded.
- **Contribution**: Establishes that current standards quantify discretization/iterative error and order of accuracy — not freedom from structural defects.

**C2.6** Krueger, A. M., Mousseau, V. A., & Hassan, Y. A. (2020). Local truncation error-informed code verification. *Journal of Verification, Validation and Uncertainty Quantification*, *5*(4), 041005. https://doi.org/10.1115/1.4049230

- **Relevance**: The strongest published response to MMS's same-order blind spot, and therefore the strongest competing O-component for detecting subtle structural faults.
- **Key findings**: (1) MMS lets developers verify freedom from coding errors that affect the *observed order of accuracy*, but does not identify errors of the same order as the numerical method. (2) Combining MMS with modified equation analysis to compute the local truncation error (MEAMMS) extends detection up to and including the order of the method. (3) On a shallow-water test code with a first-order coding error in a first-order scheme, only MEAMMS identifies the error; MEAMMS detects a strict superset of what MMS detects.
- **Methodology**: Method development plus controlled fault-injection evaluation on a custom shallow-water solver.
- **Quality / limitations**: ASME J. VVUQ. Very low citation count. Single custom code; generalisation to multiphysics or stochastic solvers not demonstrated.
- **Contribution**: Sets the bar an SPTM's O component must clear to be worth introducing — and is itself another fault-injection-into-numerical-code precedent.

**C2.7** Kanewala, U., & Bieman, J. M. (2014). Testing scientific software: A systematic literature review. *Information and Software Technology*, *56*(10), 1219–1232. https://doi.org/10.1016/j.infsof.2014.05.006

- **Relevance**: The field-defining SLR on the scientific-software oracle problem; establishes the state of practice against which SLRMA would be positioned.
- **Key findings**: Per venue and scope: (1) the oracle problem dominates scientific-software testing; (2) metamorphic testing and pseudo-oracles are the principal responses; (3) reported practice is fragmented, with limited use of systematic adequacy criteria.
- **Methodology**: Systematic literature review.
- **Quality / limitations**: IST, ~127–160 citations. Crossref returns no abstract; findings attributed to the SLR's established scope, not to verified abstract text. Now over a decade old — the post-2014 MT literature (C3) is not covered.
- **Contribution**: Documents the absence, as of 2014, of any structure-derived adequacy denominator for scientific software.

---

### C3 — THE PRIOR-ART FRONTIER

**C3.1** Li, M., Yang, X., Liu, J., & Yan, S. (2026). *A semantic mutation metric for metamorphic relation adequacy in scientific computing programs* (arXiv:2605.17437v2) [Preprint]. arXiv. https://arxiv.org/abs/2605.17437

- **Relevance**: **The single most important entry in this bibliography.** This preprint already proposes a Semantic Mutation Score (SMS) for metamorphic-relation adequacy in scientific computing, built on five domain-semantic mutation operators of which two — **Conservation Erosion** and **Structural Injection** — are structure-property-violating by name and construction.
- **Key findings** (from the verified arXiv abstract): (1) SMS is built on five domain-semantic operators: Conservation Erosion, Operator Substitution, Hyperparameter, Trajectory Flip, Structural Injection; it degenerates almost everywhere to classical Mutation Score in a characterised limit. (2) A 12-PUT × 5-MP design over four single-output float-to-float classes is paired with a three-layer attribution classifier separating true semantic faults from tolerance, OOD, statistical and artefact categories; the pre-registered large-effect threshold for Cliff's delta is *not* met, the observed effect lying in the medium range, and cross-source LLM pooling does not appreciably shift delta. (3) AST-level overlap between LLM-generated and default cosmic-ray syntactic mutants is small, and the Hyperparameter, Structural Injection and Trajectory Flip classes are **unreachable under default first-order syntactic configurations**.
- **Methodology**: Empirical software-engineering study; LLM-generated domain-semantic mutants versus a `cosmic-ray` syntactic baseline; pre-registered effect-size threshold; AST-normalised overlap analysis; same-source/cross-source ablation.
- **Quality / limitations**: arXiv preprint (cs.SE; cs.LG), v1 2026-05-17, v2 2026-07-07; not peer-reviewed at time of writing; no DOI beyond the arXiv-minted `10.48550/arXiv.2605.17437`. The headline pre-registered threshold is reported as *not met*. Independently confirmed twice through paper-search: `search_arxiv` (full abstract, author list Meng Li; Xiaohua Yang; Jie Liu; Shiyu Yan) and `search_openalex` (record W7161916857, identical abstract).
- **Contribution**: Establishes that structure-property-violating mutation as an MR-adequacy denominator **is already in the public record**, by an author group whose surname set (Li, Yang, Liu, Yan) matches the P3 repository's own P-series lineage. See §4.

**C3.2** Li, M., Yang, X., Liu, J., & Yan, S. (2026). *Minimum complete MR subsets under semantic-mutation fault models: A support-set domination boundary* (arXiv:2606.08269v1) [Preprint]. arXiv. https://arxiv.org/abs/2606.08269

- **Relevance**: Extends the same semantic-mutation fault model into MR-subset minimisation — i.e. the adequacy-denominator machinery is already being built out theoretically, not just proposed.
- **Key findings** (verified abstract): (1) Defines a layer-relative completeness criterion over an admitted mutant–draw coverage universe. (2) The central result is a support-set domination boundary stating when class-level abstraction is safe and when mutant-level MR minimisation is necessary, governed by kill-signature heterogeneity. (3) Min-MR-Complete is Set-Cover-equivalent over the selected coverage universe, giving NP-hardness, the logarithmic approximation boundary, a greedy approximation, an exact ILP formulation, and an SMS-rank upper bound that is explicitly *not* a lower bound or tight predictor.
- **Methodology**: Theoretical (complexity reduction + ILP) with artifact-lane and route-witness evidence rather than pooled population experiments.
- **Quality / limitations**: arXiv preprint (cs.SE; cs.DS), 2026-06-06; not peer-reviewed. The authors themselves scope the empirical claims tightly ("route witnesses... are not pooled as population-level experiments"). Confirmed via `search_arxiv` and `search_openalex` (W7164233412).
- **Contribution**: Shows the theoretical layer above SPTM/SLRMA is also already occupied by the same group.

**C3.3** Bartocci, E., Mariani, L., Ničković, D., & Yadav, D. (2023). Property-based mutation testing. In *2023 IEEE Conference on Software Testing, Verification and Validation (ICST)* (pp. 222–233). IEEE. https://doi.org/10.1109/icst57152.2023.00029

- **Relevance**: The generic formulation of the SPTM idea outside scientific computing: a mutant is *relevant* only if it can affect satisfaction of a specified property, and *meaningfully killed* only if it causes that property's violation.
- **Key findings** (verified arXiv abstract, arXiv:2301.13615): (1) Classical mutation testing is uninformative when software must be validated against specific requirements, as with safety properties for embedded software. (2) Property-based mutation testing assesses a test suite's capability to exercise the software with respect to a given property, using relevance and property-violating-kill as the two redefined notions. (3) Evaluation on Simulink models of safety-critical CPS from automotive and avionics domains shows property-based mutation testing is more informative than regular mutation testing.
- **Methodology**: Method definition plus empirical evaluation on industrial Simulink CPS models against rigorously specified (STL-style) safety properties. Companion tool paper: *FIM: fault injection and mutation for Simulink* (`10.1145/3540250.3558932`).
- **Quality / limitations**: ICST 2023, ~8 citations. The properties are *externally specified requirements* (signal temporal logic over Simulink signals), not properties *derived from a governing equation*; there is no discretization error budget, no numerical tolerance treatment, and no metamorphic-relation adequacy question.
- **Contribution**: **The nearest non-self prior art for SPTM's definitional core.** The distance is the provenance of the property (requirement vs. governing equation) and the certification problem (Boolean STL monitor vs. an error-budgeted independent observation).

**C3.4** Ding, J., Li, X., & Hu, X.-H. (2019). Testing scientific software with invariant relations: A case study. In *2019 IEEE 19th International Conference on Software Quality, Reliability and Security (QRS)* (pp. 406–417). IEEE. https://doi.org/10.1109/qrs.2019.00057

- **Relevance**: Uses *invariant relations* — physically or mathematically necessary relations that must hold — as the testing criterion for scientific software, and evaluates them with injected faults.
- **Key findings**: Per DS1's characterisation, which is the only evidence available (Crossref returns no abstract for this record): (1) invariant relations serve as oracles for scientific software lacking expected outputs; (2) the relations are derived from domain properties; (3) evaluation uses injected faults on a Monte Carlo optical-scattering code.
- **Methodology**: Case study with fault injection.
- **Quality / limitations**: QRS 2019, low citation count (1–4 depending on index). Crossref record has no abstract, so the three findings are attributed to DS1's summary and the title, not verified abstract text. Case study on one program family.
- **Contribution**: The closest published *scientific-computing* instance of using property violation as the seeded-fault target — but the properties are program invariants of a Monte Carlo simulator, not equation-derived structure requirements with a preservation mode and error budget.

**C3.5** Ding, J., & Hu, X.-H. (2017). Application of metamorphic testing monitored by test adequacy in a Monte Carlo simulation program. *Software Quality Journal*, *25*(3), 841–869. https://doi.org/10.1007/s11219-016-9337-3

- **Relevance**: Explicitly couples metamorphic testing to *test adequacy* measurement, which is the SLRMA question minus the structural denominator.
- **Key findings**: Per title, venue and DS1's use of it: (1) MT for a Monte Carlo simulation program is monitored by adequacy criteria rather than run open-loop; (2) adequacy measurement guides MR and test-case selection; (3) the combination detects faults that either technique alone misses.
- **Methodology**: Case study; MT plus code-coverage-style adequacy monitoring.
- **Quality / limitations**: Springer SQJ; ~8–9 citations. Crossref returns no abstract; findings attributed to title/scope and DS1. Published online 2016-09-14 in the 2017 volume 25(3) — note the year discrepancy against Undermind's "2016". Adequacy here is conventional (structural code coverage), not property-derived.
- **Contribution**: Demonstrates that "MT adequacy" as a research question predates P3 v4 by roughly a decade; what is new can only be the *denominator*, not the question.

**C3.6** Yan, S., & Zhu, H. (2025). Metamorphic testing on scientific programs for solving second-order elliptic differential equations. *Software Testing, Verification and Reliability*, *35*(1), e1912. https://doi.org/10.1002/stvr.1912

- **Relevance**: **Directly answers the second half of C3**: MRs for scientific computing derived *formally from the governing equations* rather than guessed by domain experts.
- **Key findings** (verified abstract): (1) MT principles are applied to verify programs solving second-order elliptic differential equations, with a testing process tailored to scientific computation and integrated into the development process. (2) "Unlike existing approaches, we formally derive metamorphic relations from the numerical models of differential equations built in development process of scientific computing programs." (3) The approach detects faults commonly found in scientific computing programs and outperforms the trend method, a traditional scientific-software testing technique.
- **Methodology**: Formal MR derivation from numerical models plus controlled fault-detection experiment against a baseline technique.
- **Quality / limitations**: Wiley STVR, vol. 35(1); published online 2024-12-22, so the 2024/2025 year attribution differs between indexes (Undermind says 2024, Crossref assigns volume 35 issue 1). Very low citation count. Restricted to second-order elliptic PDEs. Co-author Shiyu Yan is also a co-author of C3.1 and C3.2.
- **Contribution**: Equation-derived MRs already exist in the literature. P3 v4's novelty therefore cannot rest on "deriving properties from the governing equation"; it must rest on the mutation/adequacy side.

**C3.7** Chen, T. Y., Feng, J., & Tse, T. H. (2002). Metamorphic testing of programs on partial differential equations: A case study. In *Proceedings 26th Annual International Computer Software and Applications Conference (COMPSAC)* (pp. 327–333). IEEE Computer Society. https://doi.org/10.1109/cmpsac.2002.1045022

- **Relevance**: The founding application of metamorphic testing to PDE solvers, and the historical origin of MR-for-scientific-computing.
- **Key findings**: Per title/venue (Crossref returns no abstract): (1) MT can test PDE programs lacking oracles; (2) MRs for PDE solvers can be constructed from the mathematical structure of the problem; (3) a case study demonstrates fault detection.
- **Methodology**: Case study.
- **Quality / limitations**: COMPSAC 2002, ~63–124 citations. No abstract in the Crossref record; annotation is scope-attributed. Note a duplicate-looking 2011 record ("Title Metamorphic testing of programs on partial differential equations : a case study", same authors) appears in DS2 and is a repository stub, not a separate work — excluded under E4.
- **Contribution**: Establishes the 24-year priority of the MR-from-equation-structure idea.

**C3.8** Hook, D., & Kelly, D. (2009). Mutation sensitivity testing. *Computing in Science & Engineering*, *11*(6), 40–47. https://doi.org/10.1109/mcse.2009.200

- **Relevance**: The canonical adaptation of mutation testing to scientific software, and the origin of the tolerance problem that ESPR's B component addresses.
- **Key findings**: Per title/venue and DS2's use (Crossref returns no abstract): (1) mutation applied to scientific code reveals that many mutants produce output differences smaller than acceptable tolerance and are therefore not meaningfully killable; (2) sensitivity — the magnitude of output perturbation — matters as much as kill/no-kill; (3) tolerance choice dominates measured mutation adequacy for numerical programs.
- **Methodology**: Method proposal with empirical illustration on scientific codes.
- **Quality / limitations**: CiSE 11(6), ~12 citations. **Two Crossref DOIs exist for this title** (`10.1109/mcse.2009.157` with no volume/issue, and `10.1109/mcse.2009.200` with vol. 11(6), 40–47); the latter is the complete record and the former is excluded under E4. No abstract available; findings scope-attributed. Companion works verified: *Testing for trustworthiness in scientific software* (SECSE 2009, `10.1109/secse.2009.5069163`) and Gray & Kelly (2010, `10.1016/j.procs.2010.04.165`).
- **Contribution**: Establishes that tolerance-masking, not operator design, is the binding constraint on mutation adequacy in numerical software — which is exactly what C3.1's three-layer attribution classifier is built to handle.

**C3.9** Lin, X., Simon, M., & Niu, N. (2018). Hierarchical metamorphic relations for testing scientific software. In *Proceedings of the International Workshop on Software Engineering for Science (SE4Science)* (pp. 1–8). ACM. https://doi.org/10.1145/3194747.3194750

- **Relevance**: Organises MRs for scientific software into a hierarchy — the closest prior work to a structured *lineage* of requirements as SLRMA proposes freezing.
- **Key findings**: Per title/venue (no abstract in Crossref): (1) MRs for scientific software admit hierarchical organisation from general to domain-specific; (2) the hierarchy aids systematic MR identification; (3) demonstrated on hydrological/environmental modelling software.
- **Methodology**: Conceptual framework with case application.
- **Quality / limitations**: SE4Science 2018, ~17–22 citations. Workshop paper; no abstract available; findings scope-attributed. Same group's related verified works: *Exploratory metamorphic testing for scientific software* (`10.1109/mcse.2018.2880577`), *Discovering metamorphic relations for scientific software from user forums* (`10.1109/mcse.2020.3046973`).
- **Contribution**: A prior notion of MR structure/hierarchy exists; SLRMA's "frozen lineage" must be differentiated from it explicitly.

**C3.10** Luu, Q.-H., Liu, H., Chen, T. Y., & Vu, H. L. (2022). Testing ocean software with metamorphic testing. In *Proceedings of the 7th International Workshop on Metamorphic Testing (MET)* (pp. 23–30). ACM. https://doi.org/10.1145/3524846.3527341

- **Relevance**: MRs for a geophysical-fluid code, where the natural MR candidates are physical symmetries and conservation statements.
- **Key findings**: Per title/venue (no abstract in Crossref): (1) MT is applicable to operational ocean-modelling software; (2) physically-motivated MRs (symmetry, scaling, conservation-style relations) can be constructed for such models; (3) the MRs reveal defects in real ocean software.
- **Methodology**: Case study on operational ocean models.
- **Quality / limitations**: MET 2022 workshop, ~5–7 citations. No abstract available; findings scope-attributed. Single application domain.
- **Contribution**: Evidence that physics-derived MRs are already standard practice in at least one scientific-computing subdomain.

**C3.11** Fu, A., Sun, C.-a., Zhang, J., & Liu, H. (2024). *Test adequacy for metamorphic testing: Criteria, measurement, and implication* (arXiv:2412.20692v1) [Preprint]. arXiv. https://arxiv.org/abs/2412.20692

- **Relevance**: The most recent independent attack on the SLRMA question — MT adequacy criteria defined *from the perspective of necessary properties satisfied by the software under test*.
- **Key findings** (verified abstract): (1) MR identification and source-input generation have been studied extensively, but "few studies have investigated the test adequacy assessment issue of MT", which hinders objective measurement of MT test quality. (2) Traditional test adequacy criteria "are not in line with MT's focus which is to test the software under testing from the perspective of necessary properties"; the authors therefore propose a new criterion set specifying testing requirements from the perspective of necessary properties satisfied by the SUT, with a measurement based on both MRs and source inputs. (3) Experimentally, test suites with increased adequacy exhibit higher fault-detection effectiveness.
- **Methodology**: Criterion definition plus empirical correlation study against fault-detection effectiveness.
- **Quality / limitations**: arXiv preprint (cs.SE), 2024-12-30; not peer-reviewed; no DOI beyond `10.48550/arXiv.2412.20692`. The properties are generic "necessary properties", not equation-derived structural requirements, and the denominator is not a mutation pool. A related verified peer-reviewed item exists: Liu, Li, Tao & Zheng, *Test adequacy criteria for metamorphic testing* (QRS-C 2024, `10.1109/qrs-c63300.2024.00072`).
- **Contribution**: Confirms that "MT adequacy from the perspective of necessary properties" is an actively contested 2024 research front, independent of the P-series.

---

### C4 — Independent Certification Mechanisms (candidate O components)

**C4.1** Roache, P. J. (1994). Perspective: A method for uniform reporting of grid refinement studies. *Journal of Fluids Engineering*, *116*(3), 405–413. https://doi.org/10.1115/1.2910291

- **Relevance**: The Grid Convergence Index — the standard mechanism for turning systematic grid refinement into a reportable, comparable number, i.e. the reference O component for asymptotic-order ESPRs.
- **Key findings** (verified abstract): (1) Proposes a GCI for uniform reporting of grid-refinement studies, giving "an objective asymptotic approach to quantification of uncertainty of grid convergence". (2) The GCI approximately relates results from any grid-refinement test to the expected results of a grid doubling with a second-order method, and derives from generalised Richardson extrapolation. (3) It is recommended whether or not Richardson extrapolation is used to improve accuracy, and "in some cases even if the conditions for the theory do not strictly hold"; the formulas can be applied a posteriori by editors and reviewers.
- **Methodology**: Methodological "Perspective" article.
- **Quality / limitations**: ASME JFE, ~2658 citations — the most-cited item in this bibliography. The author's own caveat that the GCI may be used outside its strict theoretical conditions is a genuine limitation for any O component that must be *independent* and *certifiable*.
- **Contribution**: The observed-order-of-accuracy O component, with a published uncertainty quantification and a known applicability caveat.

**C4.2** Becker, R., & Rannacher, R. (2001). An optimal control approach to *a posteriori* error estimation in finite element methods. *Acta Numerica*, *10*, 1–102. https://doi.org/10.1017/s0962492901000010

- **Relevance**: The dual-weighted-residual method — residual-based a posteriori error estimation targeted at a *specific output functional*, which is what an ESPR's B (error budget) needs in order to be quantity-specific rather than global.
- **Key findings** (verified abstract): (1) Most a posteriori error analysis estimates error in global norms (energy, L²) involving unknown stability constants, but "the error in a global norm does not provide useful bounds for the errors in the quantities of real physical interest". (2) Duality techniques replace global stability constants with computationally obtained local sensitivity factors; combined with Galerkin orthogonality this yields a posteriori estimates *directly* for the target quantity, as local residuals multiplied by weights. (3) The weights come from approximately solving a linear adjoint problem, giving a feedback process for economical mesh construction; demonstrated across viscous flow, reactive flow, elasto-plasticity, radiative transfer and optimal control.
- **Methodology**: Acta Numerica survey; abstract functional-analytic setting instantiated on elliptic, parabolic and hyperbolic model problems.
- **Quality / limitations**: ~904 citations. Requires solving an adjoint problem, so the O component's independence from the primal solver is partial. The authors state open theoretical and practical problems remain. A verified alternative reference: Verfürth (2013), *A posteriori error estimation techniques for finite element methods* (`10.1093/acprof:oso/9780199679423.001.0001`).
- **Contribution**: The residual-based, output-targeted error budget an ESPR needs — and the reason such a budget is quantity-specific, not a single global tolerance.

**C4.3** Giles, M. B., & Pierce, N. A. (2000). An introduction to the adjoint approach to design. *Flow, Turbulence and Combustion*, *65*(3–4), 393–415. https://doi.org/10.1023/a:1011430410075

- **Relevance**: The standard introduction to discrete and continuous adjoints, and the source of the duality identity whose violation is directly testable.
- **Key findings**: Per title, venue and DS1's use (Crossref returns no abstract): (1) continuous and discrete adjoint formulations are distinguished, with different consistency requirements; (2) the adjoint identity relates primal and dual solutions through a bilinear form; (3) adjoint gradients can be validated against directional derivatives of the primal solver.
- **Methodology**: Tutorial/review.
- **Quality / limitations**: ~793 citations. No abstract in the Crossref record; findings scope-attributed. Design-optimisation framing rather than verification framing. Note DS1 also surfaced Giles, Ghate & Duta (2005), *Using automatic differentiation for adjoint CFD code development*, but that record returned **no DOI** from Undermind and was not confirmable via paper-search — excluded under E1.
- **Contribution**: Supplies the adjoint/duality φ and the identity from which a dot-product test is built.

**C4.4** Hicken, J. E., & Zingg, D. W. (2011). Superconvergent functional estimates from summation-by-parts finite-difference discretizations. *SIAM Journal on Scientific Computing*, *33*(2), 893–922. https://doi.org/10.1137/100790987

- **Relevance**: Establishes *dual consistency* as a discrete structural property with an observable, quantitative consequence — the strongest available example of a structural requirement whose violation shows up as a measurable order loss.
- **Key findings** (verified abstract): (1) Diagonal-norm SBP operators need s-order boundary closures when the interior scheme is 2s-order, bounding solution accuracy at (s+1)-order. (2) Despite that bound, *functional* estimates can be constructed that are 2s-order accurate; "this superconvergence requires dual-consistency, which depends on the SBP operators, the boundary condition implementation, and the discretized functional". (3) Superconvergent functional estimates remain viable in higher dimensions on curvilinear multiblock grids with interfaces; demonstrated on a 2D Poisson problem and the Euler equations.
- **Methodology**: Theory developed for scalar hyperbolic and elliptic PDEs in 1D, extended to multiple dimensions, with numerical verification.
- **Quality / limitations**: SISC 33(2), ~66 citations. Restricted to SBP finite-difference discretizations. Related verified works: Hicken & Zingg (2011) AIAA `10.2514/6.2011-3855`, Hicken (2012) JCP `10.1016/j.jcp.2012.01.031`.
- **Contribution**: The cleanest structural-property-to-observable-consequence link in C4: break dual consistency and functional superconvergence is lost, which grid refinement detects.

**C4.5** Ugolotti, M., Wukie, N. A., Turner, M., & Orkwis, P. D. (2018). Discrete-adjoint solver tests and consistency analysis for discontinuous Galerkin discretization. In *2018 Fluid Dynamics Conference*. AIAA. https://doi.org/10.2514/6.2018-4154

- **Relevance**: The explicit **adjoint dot-product / bilinear-identity test** named in the C4 assignment, implemented as a solver verification procedure for DG discretizations.
- **Key findings**: Per title, venue and DS1's characterisation (Crossref returns no abstract): (1) discrete-adjoint implementations can be verified by consistency tests exploiting the bilinear identity between linearised primal and adjoint operators; (2) the tests localise adjoint implementation errors; (3) consistency analysis is applied to a DG framework.
- **Methodology**: Conference paper; solver verification tests on a DG code.
- **Quality / limitations**: AIAA conference paper, 5 citations. No abstract in the Crossref record; findings scope-attributed and should be checked against the full text before being relied on in the paper. Not peer-reviewed to journal standard.
- **Contribution**: A concrete, cheap, primal-independent O component for adjoint ESPRs — the dot-product test.

**C4.6** Haworth, D. C., El Tahry, S. H., & Huebler, M. S. (1993). A global approach to error estimation and physical diagnostics in multidimensional computational fluid dynamics. *International Journal for Numerical Methods in Fluids*, *17*(1), 75–97. https://doi.org/10.1002/fld.1650170106

- **Relevance**: The **conservation-and-balance-check** O component: volume-integrated balance equations over sources, sinks and boundaries, used simultaneously as a physical diagnostic and a numerical-accuracy indicator.
- **Key findings** (verified abstract): (1) Global balance equations — volume-integrated PDEs for primary or derived quantities — can be applied to the full domain or to any subdomain down to the single-cell level. (2) Comparing the relative magnitude of terms in the balances "provides insight into the physics of the flow being computed". (3) For quantities *not* conserved at the cell level by construction of the numerical scheme, the imbalance "allows a direct assessment of numerical accuracy in a single run using a single mesh", with the mean-kinetic-energy imbalance a particularly sensitive indicator; the approach works for finite-difference, finite-volume and finite-element methods.
- **Methodology**: Method proposal with demonstration on in-cylinder reciprocating-engine flows.
- **Quality / limitations**: IJNMF 17(1), ~32–38 citations. 1993; demonstrated in one application area. Crucially, the diagnostic is informative *only* for quantities not conserved by construction — for quantities the scheme conserves exactly, imbalance is identically zero and carries no information.
- **Contribution**: **Single-run, single-mesh, primal-independent certification** of secondary conservation — the cheapest viable O component, with a sharply defined applicability domain D (secondary, not primary, conserved quantities).

**C4.7** Limache, A. C., Sánchez, P. J., Dalcín, L. D., & Idelsohn, S. R. (2008). Objectivity tests for Navier–Stokes simulations: The revealing of non-physical solutions produced by Laplace formulations. *Computer Methods in Applied Mechanics and Engineering*, *197*(49–50), 4180–4192. https://doi.org/10.1016/j.cma.2008.04.020

- **Relevance**: The **symmetry / frame-invariance test** limb of C4: objectivity (material frame indifference) is used as a discriminating test that exposes non-physical discrete solutions.
- **Key findings**: Per title, venue and DS1's use (Crossref returns no abstract): (1) objectivity is a structural requirement on the continuous formulation that some discrete Laplace-form Navier–Stokes formulations violate; (2) an objectivity test reveals non-physical solutions that ordinary convergence testing does not flag; (3) the failure is formulation-level, not a coding error.
- **Methodology**: Analysis plus numerical counterexamples.
- **Quality / limitations**: CMAME 197(49–50), ~10–16 citations. No abstract in the Crossref record; findings scope-attributed. The failure mode studied is a *modelling/formulation* defect rather than an implementation fault — a distinction that matters for whether such a test can certify an SPTM.
- **Contribution**: Demonstrates that a symmetry/equivariance test can detect structural violation invisible to convergence testing — and simultaneously warns that structural violation is not always an implementation fault.

---

### C5 — Real-Fault Datasets and Bug Studies for Scientific / Numerical Software

**C5.1** Di Franco, A., Guo, H., & Rubio-González, C. (2017). A comprehensive study of real-world numerical bug characteristics. In *2017 32nd IEEE/ACM International Conference on Automated Software Engineering (ASE)* (pp. 509–519). IEEE. https://doi.org/10.1109/ase.2017.8115662

- **Relevance**: The reference external criterion for whether a numerical fault model is realistic — a characterisation of numerical bugs actually found in widely used numerical libraries.
- **Key findings**: Per title, venue and standing in the literature (Crossref returns no abstract): (1) numerical bugs in real projects fall into recurring categories (accuracy/precision loss, convergence, special-value and correctness-of-formula defects); (2) many are long-lived and hard to detect with conventional tests; (3) the resulting taxonomy is offered as a basis for tool and benchmark design.
- **Methodology**: Empirical study of bug reports and fixes in real numerical software projects.
- **Quality / limitations**: ASE 2017, ~63 citations. No abstract in the Crossref record; the findings above are attributed to the paper's established scope and must be confirmed against the full text before being used to justify operator design. Library-level numerical code, not PDE-solver or multiphysics code.
- **Contribution**: The most defensible available external-validity anchor for an SPTM operator taxonomy. Notably, its categories are *numerical* (precision, convergence, formula) rather than *structural* (conservation, symmetry, adjointness).

**C5.2** Eisty, N. U., & Carver, J. C. (2022). Testing research software: A survey. *Empirical Software Engineering*, *27*(6), 138. https://doi.org/10.1007/s10664-022-10184-9

- **Relevance**: Community-level evidence on what scientific-software developers actually do, bounding how much testing machinery a new adequacy metric can presuppose.
- **Key findings** (verified arXiv abstract, arXiv:2205.15982): (1) Testing research software is difficult "due to the complexity of the underlying science, relatively unknown results from scientific algorithms, and the culture of the research software community". (2) From 120 analysed survey responses, developers report an average level of software-testing knowledge yet still find testing difficult because of the numerous challenges involved. (3) Improvement paths exist, notably proper training, but a culture change is needed for testing to be valued and adequately resourced.
- **Methodology**: Survey of the research-software developer community, n = 120 analysed responses.
- **Quality / limitations**: EMSE 27(6). Self-reported survey data with attendant response and self-assessment bias. A verified, larger follow-up exists: Eisty, Kanewala & Carver (2025), *Testing research software: An in-depth survey of practices, methods, and tools*, EMSE 30(3) (`10.1007/s10664-025-10620-6`).
- **Contribution**: Sets the practitioner baseline; any structural-adequacy proposal that presumes a mature test suite is presuming something the survey says is often absent.

**C5.3** He, X., Wang, X., Shi, J., & Liu, Y. (2020). Testing high performance numerical simulation programs: Experience, lessons learned, and open issues. In *Proceedings of the 29th ACM SIGSOFT International Symposium on Software Testing and Analysis (ISSTA)* (pp. 502–515). ACM. https://doi.org/10.1145/3395363.3397382

- **Relevance**: Industrial-scale experience report on testing HPC numerical simulation programs, and the source of the "open issues" list against which SLRMA's contribution would be judged.
- **Key findings**: Per title, venue and DS1/DS2 use (Crossref returns no abstract): (1) real HPC simulation programs present testing obstacles beyond the oracle problem, including scale, nondeterminism and tolerance selection; (2) practical techniques used in industry are reported alongside their failure modes; (3) open issues are enumerated, with adequacy measurement among them.
- **Methodology**: Experience report from industrial HPC simulation practice.
- **Quality / limitations**: ISSTA 2020, ~14–21 citations. No abstract in the Crossref record; findings scope-attributed and requiring full-text confirmation. Experience reports carry limited generalisability.
- **Contribution**: A peer-reviewed, top-venue statement that adequacy measurement for numerical simulation testing remains open — useful for positioning, but it does not name structural properties as the missing denominator.

**C5.4** Elliott, J., Hoemmen, M., & Mueller, F. (2014). *Resilience in numerical methods: A position on fault models and methodologies* (arXiv:1401.3013v1) [Preprint]. arXiv. https://arxiv.org/abs/1401.3013

- **Relevance**: A position paper on what makes a *numerical* fault model useful — the resilience community's version of the fault-realism debate that any SPTM taxonomy must answer.
- **Key findings** (verified abstract): (1) Existing resilience work "randomly flips bits in running applications, but this only shows average-case behavior for a low-level, artificial hardware model", whereas algorithm developers need worst-case behaviour with the higher-level data types they actually use. (2) The authors argue for a *numerical unreliability* fault model in which faults manifest as unbounded perturbations to floating-point data. (3) Inexpensive "sanity" checks that bound or exclude error in computed results can make algorithms reliable despite unbounded faults — and such checks "are wise even if hardware is perfectly reliable".
- **Methodology**: Position paper (cs.MS; cs.ET; math.NA).
- **Quality / limitations**: arXiv preprint, 2014-01-13; no DOI; not peer-reviewed. Framed around silent data corruption at extreme scale, not implementation defects. ~15 citations.
- **Contribution**: The explicit argument that low-level syntactic perturbation is the wrong abstraction for numerical software and that higher-level, mathematically meaningful fault models are needed — the same premise C3.1 operationalises. Its "sanity checks" are C4's O components under a different name.

---

## 4. PRIOR-ART VERDICT for C3

### Verdict

# `DIRECT_PRIOR_ART`

### The citation

**Li, M., Yang, X., Liu, J., & Yan, S. (2026). *A semantic mutation metric for metamorphic relation adequacy in scientific computing programs* (arXiv:2605.17437v2). https://arxiv.org/abs/2605.17437**

with the companion

**Li, M., Yang, X., Liu, J., & Yan, S. (2026). *Minimum complete MR subsets under semantic-mutation fault models: A support-set domination boundary* (arXiv:2606.08269v1). https://arxiv.org/abs/2606.08269**

### Exactly what they did

Verified verbatim from the arXiv abstract (confirmed independently a second time through OpenAlex record W7161916857):

1. **They already built the metric.** "We propose the Semantic Mutation Score (SMS), built on five domain-semantic operators (Conservation Erosion, Operator Substitution, Hyperparameter, Trajectory Flip, Structural Injection)." Two of the five operators — **Conservation Erosion** and **Structural Injection** — are structure-property-violating mutations by name and by construction. This is SPTM.

2. **They already used it as the MR-adequacy denominator.** SMS is stated to be "a backward-compatible adequacy metric for domain-semantic metamorphic-relation sets in scientific computing." This is SLRMA's function.

3. **They already ran the 12-PUT × 5-MP empirical design** over four single-output float-to-float program classes (numeric, probabilistic, surrogate, machine-learning), with "a three-layer attribution classifier separating true semantic faults from tolerance, OOD, statistical, and artefact categories." The attribution classifier's separation of true semantic faults from *tolerance* and *statistical* categories is functionally the ESPR B (error budget) component — discretization, statistical and floating-point error must be excluded before a violation is certified.

4. **They already established the unreachability result** that would otherwise be P3 v4's central empirical claim: "AST-level overlap between LLM-generated and default cosmic-ray syntactic mutants is small; the Hyperparameter, Structural Injection, and Trajectory Flip classes are unreachable under default first-order syntactic configurations." That is the "structure-preservation mutations are not reachable by syntactic code edits" claim.

5. **They already extended it theoretically.** The companion preprint gives a layer-relative completeness criterion over an admitted mutant–draw coverage universe, a support-set domination boundary, Set-Cover-equivalence with NP-hardness, a greedy approximation, an exact ILP, and an SMS-rank upper bound.

### The unavoidable complication, stated plainly

The author set of both preprints (Meng Li, Xiaohua Yang, Jie Liu, Shiyu Yan) matches the P-series lineage documented in this repository, and the `12-PUT × 5-MP` design string in arXiv:2605.17437 is the same design string that this repository's own project rules describe as the shared P1–P5 experimental infrastructure. The most probable reading is that **this "prior art" is the authors' own P2, already public on arXiv, and arXiv:2606.08269 is P4**.

That does not soften the finding; it sharpens it into a different and more dangerous problem. For a TOSEM submission the consequence is the same either way:

- If P3 v4 presents ESPR / SPTM / SLRMA as new constructs, a reviewer who runs one arXiv search on "semantic mutation metamorphic relation adequacy scientific computing" finds a 2026 preprint by the same authors that already defines the operators, the metric, the design and the headline unreachability result. Presented as novel, this is **self-plagiarism / salami-slicing**; presented without citation, it is worse.
- If the P3 v4 relationship to arXiv:2605.17437 and arXiv:2606.08269 is *not* one of authorship, then the constructs are simply **not new** and the paper's central theoretical move is scooped outright.

Either way, ESPR / SPTM / SLRMA cannot be introduced as first-of-kind. What can legitimately be new is the *increment* over SMS: the five-tuple formalisation r = (φ, D, κ, B, O) with an explicit applicability domain and an **independent certification method that does not use any MR verdict**. Notably, the SMS abstract describes a three-layer *attribution classifier*, not an MR-verdict-independent certification protocol — so the O component and the verdict-independence requirement are the plausible surviving novelty. That determination is outside this agent's Phase 2 boundary and is handed to the caller.

### Nearest non-self prior art, with distances

Ranked by proximity. These matter because they bound the novelty of the *increment* even after the self-overlap is handled by citation.

| Rank | Work | Overlap | Distance from P3 v4 |
|---|---|---|---|
| 1 | **Bartocci et al. (2023), Property-Based Mutation Testing** (C3.3) | The definitional core of SPTM: a mutant is relevant only if it can affect a specified property, and killed only if it violates that property. Evaluated on safety-critical CPS Simulink models. | Properties are *externally specified requirements* in a temporal logic, not derived from a governing equation. No preservation mode κ, no discretization/floating-point error budget B, no independent certification method O. Not about MR adequacy. **~2 constructs away.** |
| 2 | **Yan & Zhu (2025), MT for second-order elliptic PDEs** (C3.6) | Formally derives MRs *from the numerical models of the differential equations* — the equation-derived-property half of ESPR. Co-author Shiyu Yan also co-authors arXiv:2605.17437. | Derives *MRs* (the things being evaluated), not *mutations* (the denominator). No mutation operators, no adequacy metric. **~1 construct away, on the opposite side of the ledger.** |
| 3 | **Ding, Li & Hu (2019), Invariant Relations** (C3.4) | Uses violation of a necessary domain relation as the testing criterion, evaluated with injected faults, in scientific software. | Invariants are program-level properties of one Monte Carlo simulator, not conservation/symmetry/adjointness requirements implied by a governing equation. No adequacy metric, no error budget, no domain of applicability. **~2 constructs away.** |
| 4 | **Fu et al. (2024), Test Adequacy for MT** (C3.11) | MT adequacy criteria defined "from the perspective of necessary properties satisfied by the SUT" — the SLRMA framing, independently and recently. | "Necessary properties" are generic, not equation-derived structural requirements. Denominator is MRs × source inputs, not a mutation pool. **~1 construct away on the metric axis, ~2 on the property axis.** |
| 5 | **Krueger et al. (2020), MEAMMS** (C2.6); **Salari & Knupp (2000)** (C2.2) | Deliberate fault injection into scientific code with detection by a verification procedure as the measured outcome — the experimental *pattern* of SPTM. | Injected faults are ordinary coding errors, deliberately chosen to sit at or below the truncation-error order. No structural property is named or targeted. **~2 constructs away.** |
| 6 | **Benson et al. (2015), Silent error detection** (verified, `10.1177/1094342014532297`); **Elliott et al. (2014)** (C5.4); **Gorard & Hakim (2025)** (verified, arXiv:2503.13877) | Structural/numerical properties used as *runtime detectors* or *proof obligations*: cheap checking computations against injected errors; unbounded-perturbation numerical fault models with sanity checks; machine-checked proofs of L² stability, flux conservation and physical validity. | Purpose is resilience, recovery or formal proof — never test-suite or MR-set adequacy. The property is a detector or a theorem, never a denominator. **~2 constructs away, orthogonal axis.** |

### Why this search should be read as adversarial rather than confirmatory

The queries were written to *find* the paper's competitors, not to miss them, and the C3 result was surfaced on the very first pass:

- The Undermind deep search DS1 was framed as the disconfirming question outright — its stated goal asks "whether anyone has ever treated the violation of a mathematical or physical structural property of a governing equation as a deliberate fault model, mutation target, or test-adequacy denominator", and explicitly asks for "physics-based or physics-informed fault injection, invariant-violating perturbations, conservation-violation faults, and fault taxonomies specific to numerical or simulation software" to be surfaced. It returned 98 ranked results and put the scooping preprint at rank 1 (r = 1.160).
- Independent framings were then run through separate engines rather than re-querying one index: `conservation violating fault model mutation testing scientific computing adequacy` (Crossref), `physics-informed testing oracle conservation law violation mutation scientific software` (arXiv), `physics-based fault injection conservation law invariant detector silent data corruption numerical simulation` (OpenAlex), `mutation testing metamorphic relation adequacy scientific computing structure preserving property violation fault model` (OpenAlex), `metamorphic testing scientific software physical symmetry invariant oracle problem numerical program` (Crossref). The arXiv framing surfaced Bartocci et al. independently of Undermind; the OpenAlex framings surfaced arXiv:2605.17437 and arXiv:2606.08269 independently of Undermind, which is why the verdict rests on two separate confirmations rather than one.
- The second half of C3 — whether MRs for scientific computing have already been derived from conservation laws or symmetries — was probed separately and answered **yes** (Yan & Zhu 2025 derive MRs formally from the numerical models; Luu et al. 2022 use physically-motivated MRs for ocean models; Chen, Feng & Tse 2002 established the pattern in 2002). No attempt was made to characterise these as merely "adjacent".
- The one search axis that came back genuinely thin is a *general fault taxonomy whose denominator is specifically structural-property violation*: DS1's own summary states the search "found little evidence of a mature, general mutation taxonomy whose denominator is specifically 'violations of conservation, symmetry, adjointness, symplecticity, positivity, or reversibility'." That thinness is reported as a finding, and it is the only part of the C3 territory that remains open — but arXiv:2605.17437 occupies even that space for the five-operator case.

---

## 5. 检索审计表 (Search Audit Table)

状态 legend: ✓ = fully verified through a paper-search call with matching title/authors/venue; △ = verified but with a caveat (no abstract returned, competing DOI variants, year/edition ambiguity, or preprint-only); ✗ = could not be verified, **excluded from bibliography**.

| Ref | 工具链 | 命中工具 | 状态 |
|---|---|---|---|
| **C1** | | | |
| Hairer, Lubich & Wanner (2006) | crossref(title) → get_crossref_paper_by_doi(10.1007/3-540-30666-8) | get_crossref_paper_by_doi | ✓ book-level DOI, 2nd ed. confirmed |
| Marsden & West (2001) | crossref(title+venue) | crossref | ✓ abstract, vol/pages |
| Arnold, Falk & Winther (2006) | crossref(title+authors+venue) | crossref | ✓ abstract, vol 15, 1–155 |
| Christiansen, Munthe-Kaas & Owren (2011) | crossref(title+authors+venue) | crossref | ✓ abstract, vol 20, 1–119 |
| Bochev & Hyman (2006) | crossref(title+authors) → crossref(volume) | crossref | △ no abstract; chapter DOI dated 1970, volume DOI dated 2006 |
| Lipnikov, Manzini & Shashkov (2014) | crossref(title+authors+venue) | crossref | △ no abstract; vol/pages confirmed |
| Zhang & Shu (2011) | crossref(title+authors) | crossref | ✓ abstract, vol 467(2134) |
| Perot (2011) | crossref(title+author+venue) | crossref | ✓ abstract, vol 43(1) |
| Harten (1983) | crossref(title+venue+year) | crossref | △ no abstract; distinct 1997 reprint DOI noted |
| **C2** | | | |
| Roache (2002) | crossref(title+author+venue+year) | crossref | ✓ abstract, vol 124(1) |
| Salari & Knupp (2000) | crossref(title+authors) | crossref | △ no abstract; typed `report`, OSTI |
| Roy (2005) | crossref(title+author+venue+year) | crossref | △ no abstract; vol 205(1) confirmed |
| Oberkampf & Roy (2010) | crossref(title+authors+publisher) | crossref | ✓ abstract, monograph + ISBNs; 2025 2nd ed. also verified |
| AIAA R-141 (2021) | crossref(title) ×2 independent queries | crossref | △ no listed authors; typed `book-chapter` |
| Krueger, Mousseau & Hassan (2020) | undermind(DOI) → get_crossref_paper_by_doi | get_crossref_paper_by_doi | ✓ full abstract, vol 5(4) |
| Kanewala & Bieman (2014) | crossref(authors+title) | crossref | △ no abstract; vol 56(10), 1219–1232 |
| **C3** | | | |
| Li et al. (2026a) SMS | undermind(DS1 rank 1) → arxiv(title) → openalex(topic) | arxiv **and** openalex | △ preprint; abstract verified twice, two engines |
| Li et al. (2026b) Min-MR | undermind(DS1) → arxiv(title) → openalex(topic) | arxiv **and** openalex | △ preprint; abstract verified twice |
| Bartocci et al. (2023) PBMT | arxiv(topic, serendipitous) → crossref(title+authors) | arxiv **and** crossref | ✓ ICST 2023, 222–233; abstract from arXiv:2301.13615 |
| Ding, Li & Hu (2019) | undermind(DOI) → get_crossref_paper_by_doi | get_crossref_paper_by_doi | △ no abstract; QRS 2019, 406–417 |
| Ding & Hu (2017) | crossref(title+authors+venue) | crossref | △ no abstract; vol 25(3); year 2016 online / 2017 issue |
| Yan & Zhu (2025) | crossref(topic) ×2 independent queries | crossref | ✓ full abstract; STVR 35(1); year 2024 online / 2025 issue |
| Chen, Feng & Tse (2002) | crossref(title+authors+venue+year) | crossref | △ no abstract; COMPSAC 327–333 |
| Hook & Kelly (2009) | crossref(authors+topic) | crossref | △ no abstract; two DOI variants, complete one selected |
| Lin, Simon & Niu (2018) | crossref(title+authors+venue+year) | crossref | △ no abstract; SE4Science 1–8 |
| Luu et al. (2022) | crossref(title+authors+venue+year) | crossref | △ no abstract; MET 2022, 23–30 |
| Fu et al. (2024) | arxiv(title) | arxiv | △ preprint; full abstract verified |
| **C4** | | | |
| Roache (1994) | crossref(title+author+year+venue) | crossref | ✓ full abstract, vol 116(3) |
| Becker & Rannacher (2001) | crossref(title+authors+venue) | crossref | ✓ full abstract, vol 10, 1–102 |
| Giles & Pierce (2000) | crossref(title+authors+venue) | crossref | △ no abstract; vol 65(3–4) confirmed |
| Hicken & Zingg (2011) | crossref(title+authors+topic) | crossref | ✓ full abstract, SISC 33(2) |
| Ugolotti et al. (2018) | undermind(DOI) → get_crossref_paper_by_doi | get_crossref_paper_by_doi | △ no abstract; full 4-author list confirmed |
| Haworth, El Tahry & Huebler (1993) | undermind(DOI) → get_crossref_paper_by_doi | get_crossref_paper_by_doi | ✓ full abstract, vol 17(1) |
| Limache et al. (2008) | undermind(DOI) → get_crossref_paper_by_doi | get_crossref_paper_by_doi | △ no abstract; full 4-author list, vol 197(49–50) |
| **C5** | | | |
| Di Franco, Guo & Rubio-González (2017) | crossref(title+author) | crossref | △ no abstract; ASE 2017, 509–519 |
| Eisty & Carver (2022) | crossref(authors+title+venue) → arxiv(abstract source) | crossref **and** arxiv | ✓ EMSE 27(6); abstract from arXiv:2205.15982 |
| He et al. (2020) | crossref(title+author+venue+year) | crossref | △ no abstract; ISSTA 2020, 502–515 |
| Elliott, Hoemmen & Mueller (2014) | semantic(title) ✗ → arxiv(title+topic) | arxiv (2nd attempt) | △ preprint, no DOI; full abstract verified |
| **EXCLUDED (✗)** | | | |
| ASME V&V 20-2009 standard | webfetch(asme.org) ×3 URL variants | none — all HTTP 404 | ✗ **excluded**; replaced by AIAA R-141-2021 |
| Chan, Kuo, Chen & Yiu (1998), "Application of metamorphic testing in numerical analysis" | undermind(no DOI, Semantic Scholar stub) → crossref(topic) → arxiv(topic) | none | ✗ **excluded** |
| Last & Friedman (2004), "Automated detection of injected faults in a differential equation solver" | undermind(DOI 10.1109/HASE.2004.1281751) → crossref(topic) | none via paper-search | ✗ **excluded** (Undermind authority alone is insufficient) |
| Giles, Ghate & Duta (2005), "Using automatic differentiation for adjoint CFD code development" | undermind(no DOI) → crossref(author+topic) | none | ✗ **excluded** |
| **TOOL-LEVEL FAILURES (not references)** | | | |
| `search_dblp` — 5 queries incl. minimal control query `metamorphic testing` | dblp | none — empty response every time | ✗ tool unusable this session |
| `search_semantic` — 1 query | semantic | none — empty response | ✗ tool unusable this session |

### Totals

- **Included**: 38
- **状态 ✓**: 13
- **状态 △**: 25
- **状态 ✗ (excluded references)**: **4**
- **状态 ✗ (tool-level failures, not references)**: 2

The high △ count is driven almost entirely by one systemic cause: Crossref frequently returns records with complete bibliographic fields but an empty `abstract` field, particularly for IEEE and ACM proceedings and for Elsevier review articles. Where that happened, the bibliographic data (title, author set, venue, volume, issue, pages, DOI) is verified and safe to cite, but the *substantive* annotation is attributed to the work's established scope or to the Undermind deep-search summary and is flagged as such in the entry. Twelve entries carry that flag and should have their claimed findings confirmed against the full text before any of them is used to support a specific assertion in the paper.

---

## 6. Search Limitations

1. **`search_dblp` was unusable.** Five separate queries returned empty responses, including the deliberately minimal control query `metamorphic testing` with `max_results: 5`. Since that control query cannot plausibly have zero DBLP hits, the failure is tool-level, not query-level. The assignment designated DBLP as the *first* tool in the software-engineering chain and noted its superior coverage of SE conference proceedings. The chain therefore degraded to `search_arxiv` (cs.SE) → `search_crossref` → `search_openalex`. Consequence: **SE venue coverage in C3 and C5 is Crossref-DOI-dependent and may under-represent workshop papers, regional conferences and pre-2000 proceedings that DBLP indexes but Crossref does not.** ISSTA, ICST, ASE, ICSE, MET, SE4Science, QRS and EMSE were nevertheless all reached through Crossref, so the gap is most likely in the long tail rather than the core venues.

2. **`search_semantic` was unusable.** One query returned an empty response. It was the designated fourth link in the numerical-analysis chain and would have been the natural route for records lacking DOIs — precisely the class of items that ended up excluded (Chan et al. 1998, Giles et al. 2005, both of which Undermind resolved only to Semantic Scholar stubs). Consequence: **two DOI-less items that are probably real were excluded under the gray-zone-equals-FAIL rule, and DOI-less conference and technical-report literature is systematically under-represented.**

3. **ASME V&V 20-2009 could not be verified.** Three WebFetch attempts against `asme.org` URL variants all returned HTTP 404. The assignment explicitly permits WebFetch for standards, so no rule was bent, but the target page was unreachable. The C2 standards slot is therefore filled by AIAA R-141-2021 (Crossref-verified) and by the ASME-published Krueger et al. (2020) in *J. VVUQ*. Consequence: **the ASME V&V 10 / V&V 20 lineage, which is the dominant standards reference in the nuclear and mechanical-engineering V&V communities and is repeatedly cited in both Undermind searches, is absent from the verified bibliography.** This is the most consequential single gap and should be closed by a direct standards-body purchase-page or library-catalogue check before submission.

4. **Empty Crossref abstracts limit annotation confidence for 12 of 38 entries.** As detailed at the end of §5, bibliographic fields are verified for all included entries, but the substantive "Key findings" for twelve of them are attributed to the work's established scope or to the Undermind summary rather than to text returned by a verification call. These are flagged individually. **No entry's findings were reconstructed from the agent's own memory**, per Iron Rule 1, and no DOI, edition, volume or page range anywhere in this document was invented.

5. **No new Undermind deep searches were launched**, per the cost constraint. DS1's own summary flags one residual gap — the absence of a mature, *general* structural-violation mutation taxonomy — and that gap could in principle be probed harder with a dedicated search on, for example, symplecticity-violating or reversibility-violating perturbation. Given that arXiv:2605.17437 already occupies the five-operator case, the marginal value of such a search is judged low, but the decision is the caller's, not this agent's.

6. **Deliberate query-language asymmetry.** Undermind DS2 was Chinese-language and was read in full; all 53 own paper-search queries were English. No Chinese-, Japanese-, Russian- or German-language records surfaced above the relevance floor in any English query. Given that the structure-preserving-discretization canon has significant Chinese-language roots (Feng Kang's symplectic-geometry school), **there may be non-English priority literature on structure preservation that this search did not reach.** This affects C1 attribution, not the C3 verdict.

7. **Single-index citation counts.** Citation figures quoted in the annotations come from whichever index returned them and differ substantially between Crossref, OpenAlex and Undermind for the same work (Salari & Knupp: 170 vs. 678; Perot: 100 vs. 119). They are reported as returned and should not be treated as authoritative.

8. **arXiv-preprint dependence in C3.** Four of the eleven C3 entries, including both decisive prior-art items, are arXiv preprints with no peer review and no DOI beyond an arXiv-minted one. Their content may change between versions — arXiv:2605.17437 was already at v2 (2026-07-07) when read, having been posted as v1 on 2026-05-17. **A version-pinned re-check is required before submission.**

---

## 7. Handoff Notes

*(Observations only. No synthesis, no gap analysis, no recommendation — Phase 2 boundary respected.)*

- **The C3 verdict is `DIRECT_PRIOR_ART`, and the two decisive items appear to be the author group's own arXiv preprints.** arXiv:2605.17437 already defines Conservation Erosion and Structural Injection mutation operators, already frames SMS as an adequacy metric for domain-semantic MR sets in scientific computing, already ran the 12-PUT × 5-MP design, and already reports that Structural Injection is unreachable under default first-order syntactic configurations. arXiv:2606.08269 already supplies the completeness/minimisation theory. Both were confirmed twice through paper-search, on two different engines. The caller must decide how ESPR / SPTM / SLRMA are positioned relative to these; that decision is not this agent's to make.

- **One observed textual difference between the SMS preprint and the P3 v4 construct description**, offered without interpretation: the SMS abstract describes a "three-layer attribution classifier separating true semantic faults from tolerance, OOD, statistical, and artefact categories", whereas the P3 v4 SPTM definition supplied in this assignment requires certification "WITHOUT using any MR verdict" and the ESPR five-tuple carries explicit D (applicability domain), κ (preservation mode) and O (independent observation and certification method) components. Whether that difference constitutes a defensible increment is a synthesis question.

- **The equation-derived-MR half of C3 is answered yes, by three independent groups.** Yan & Zhu (2025) state explicitly that "unlike existing approaches, we formally derive metamorphic relations from the numerical models of differential equations"; Luu et al. (2022) use physically-motivated MRs for operational ocean models; Chen, Feng & Tse (2002) established the pattern 24 years ago. Shiyu Yan co-authors both the STVR paper and arXiv:2605.17437.

- **C4 is unexpectedly well-stocked and every mechanism the assignment named has a verified reference**, with one caveat worth flagging: Haworth et al. (1993) states that global-balance imbalance is informative *only* for quantities not conserved at cell level by construction of the numerical scheme. For quantities a scheme conserves exactly, the imbalance is identically zero regardless of implementation correctness, so that O component is silent on precisely the primary-conservation ESPRs it might be assumed to certify. Perot (2011)'s primary/secondary conservation distinction bears on the same point.

- **Two systemic evidence gaps should be closed before submission**: the ASME V&V 10 / V&V 20 standards lineage is absent because three WebFetch attempts returned 404, and twelve of the thirty-eight included entries have verified bibliographic data but scope-attributed rather than abstract-verified findings (flagged individually in §3 and tallied in §5). Both `search_dblp` and `search_semantic` were non-functional for this entire session, which is worth checking before the next bibliography agent runs.
