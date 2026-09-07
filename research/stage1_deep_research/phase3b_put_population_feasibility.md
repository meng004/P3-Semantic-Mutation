# Phase 3b — PUT-population feasibility for white-box operator probes

**Date:** 2026-09-07
**Scope:** literature / software-landscape survey, not a codebase exploration.
**Question:** does a program-under-test (PUT) population exist that can host the two structurally clean ESPR certifiers (discrete-operator commutator; adjoint bilinear identity) plus a single-run conservation diagnostic, under the existing Python mutation harness (`cosmic-ray` / `mutmut`)?
**Predecessor population:** arXiv:2605.17437 — “four single-output float-to-float classes”. That population cannot expose inspectable discrete operators or adjoints (`docs/STATE.md` §1.3).
**Population bar used here:** enough *independently developed programs* for per-program analysis. The P-series confirmation design treats the statistical unit as the program / solver (`docs/STATE.md` §3). Example PDEs inside one library are not independent PUTs. A usable bar is on the order of the old 12-PUT design, or at least n large enough that project-clustering uncertainty is identifiable. n = 1 has already been recorded as a C3 blocker.

`search_dblp` and `search_semantic` were not used (non-functional). Papers were verified via `user-paper-search` (`search_crossref`, `get_crossref_paper_by_doi`, `search_arxiv`, `search_openalex`). Repo facts via GitHub API + project docs.

---

## 2. Verdict

**A population that satisfies all five hard requirements at empirical-study scale does not exist.**

What exists is one project family that is close (`discretize` + SimPEG) and three or four near-miss Python libraries that each fail at least one hard requirement. That is a single-project confirmation kit, not a population.

**Binding constraint: R1 ∩ R2.**

- Codes that expose inspectable, separately callable discrete operators (or a genuine adjoint) put those operators in C++ / Fortran / generated C, or in a JIT that the existing harness does not mutate as source.
- Codes whose numerically meaningful operator implementation is Python source almost never expose those operators as first-class objects on which a commutator or ⟨Au, v⟩ = ⟨u, A\*v⟩ test can be run.
- The intersection is one library family (`discretize`), plus two small operator kits (`findiff`, `py-pde`) and one JAX CFD kit (`jax-cfd`). That is not n ≈ 8–12 independent programs.

**Secondary binding constraint: R4 at that intersection.** Among the R1∩R2 survivors, only the SimPEG family has a usable independently admitted defect corpus (106 `bug`-labelled issues). `findiff` has 1 labelled bug; `py-pde` has 4; `jax-cfd` has 0 labelled bugs (32 unlabelled issues). RQ3 therefore also collapses to one project.

Treating “many example PDEs inside `discretize` / SimPEG” as a population would restore n and repeat the already-recorded `n_projects=1` clustering failure. That is not a population.

Julia (`Oceananigans`) is not worth considering under R1. See §5 and the rejected list.

---

## 1. Ranked shortlist (closest, not passing)

Pass / fail is against the five hard requirements as written. “Partial” means the capability exists but is not in the form the certifiers require, or is too thin for an empirical study.

| Rank | Candidate | R1 Python-mutable core | R2 operators / adjoint | R3 single-run conservation | R4 defect history | R5 mutant-campaign runtime | All five? |
|---|---|---|---|---|---|---|---|
| 1 | `discretize` + SimPEG | Partial (operators in Python; 14% Cython / 4% C++) | **Yes** | **Yes** | **Yes** (SimPEG) | **Yes** (operator probes) | Closest; one family |
| 2 | `findiff` | **Yes** (100% Python) | **Yes** | Partial (must be built) | **No** (1 labelled bug) | **Yes** | No — R4 |
| 3 | `py-pde` | Partial (Python + numba JIT) | Partial (no curl; callables, not matrices) | Partial | **No** (4 labelled bugs) | Partial (JIT per mutant) | No — R4, weak R2/R3 |
| 4 | `jax-cfd` | Partial (Python/JAX; JIT) | **Yes** (ops + AD adjoint) | Partial (div-free projection) | **No** (0 labelled bugs) | Partial (JIT compile cost) | No — R4 |
| 5 | Dedalus | Partial (Python graph; C kernels at runtime) | **Yes** (ops + automated adjoint) | Partial (`integ`) | Partial (48 labelled bugs) | **No** for production IVPs | No — R1/R5 |

### 1.1 `discretize` (SimPEG) — only candidate close to all five

**Language reality.** https://github.com/simpeg/discretize. GitHub linguist (2026-09-07): Python 1.74 MB (81.5%), Cython 0.30 MB (14.2%), C++ 84 kB (3.9%). The discrete operators themselves are Python (`discretize/operators/differential_operators.py`) assembling `scipy.sparse` matrices. Cython/C++ is concentrated in TreeMesh / interpolation hot paths, not in the TensorMesh operator construction. SimPEG itself is 100% Python (4.73 MB). **Flag:** mutating `discretize` with `cosmic-ray`/`mutmut` hits the operator construction; it does not hit the Cython TreeMesh paths. Restrict the campaign to TensorMesh operators.

**R2 — operators, with commutator evidence.** First-class sparse matrices on every mesh:

- `mesh.nodal_gradient` — nodes → edges
- `mesh.face_divergence` — faces → cell centres
- `mesh.edge_curl` — edges → faces
- `mesh.cell_gradient` — centres → faces

Docs demonstrate the identities the certifier needs, as matrix products that are exactly zero:

- `CURL @ GRAD == 0` and `DIV @ CURL == 0`
- source: https://discretize.simpeg.xyz/en/v0.12.0/tutorials/operators/2_differential.html

Adjoint / transpose is the sparse-matrix transpose. The inner-product tutorial uses `mesh.edge_curl.T` as the faces→edges curl and writes the discrete pairing `u.T @ M @ G @ phi`:

- https://discretize.simpeg.xyz/en/v0.12.0/tutorials/inner_products/3_calculus.html

This is the only surveyed library whose public documentation already runs the exact commutator check v4 needs.

**R3 — single-run conservation.** Finite-volume balance from one state: `ψᵀ diag(vol) D v`, with `D = mesh.face_divergence` and `vol = mesh.cell_volumes`. That is a volume-integrated source–sink–boundary residual, not a multi-run comparison.

**R4.** https://github.com/simpeg/discretize/issues — 15 issues labelled `bug` (example: #409, incorrect TreeMesh interpolation). https://github.com/simpeg/simpeg/issues — **106** issues labelled `bug` (example: #1780, `Simulation3DDifferential` result change between 0.23 and 0.25). No published independent bug-mining study of this codebase was found; the GitHub labels are the defect history.

**Size / runtime.** Operator application on a few-thousand-cell TensorMesh is milliseconds. A thousands-of-mutants campaign on *operator probes* (build G, D, C; check `C@G`, `D@C`, and an adjoint pairing) is tractable. A campaign on full 3-D inversions is not required for the certifiers.

**Paper (verified).** Cockett, Kang, Heagy, Pidlisecky & Oldenburg, “SimPEG: An open source framework for simulation and gradient based parameter estimation in geophysical applications,” *Computers & Geosciences* 85:142–154 (2015), doi:10.1016/j.cageo.2015.09.015. Crossref, 373 citations.

**Why it still does not make a population.** It is one operator kernel and one inversion framework. Multiple SimPEG physics modules (DC, magnetics, EM) share `discretize` operators and one defect process. That is one program family.

### 1.2 `findiff`

**Language.** https://github.com/maroba/findiff — 100% Python (310 kB). Pure source-text mutation.

**R2.** First-class callables `Gradient`, `Divergence`, `Curl`, `Laplacian`, plus `Diff`; matrix form via `.matrix()`. README documents these as “standard operators from vector calculus” and “matrix representations of arbitrary linear differential operators.” Adjoint of a linear operator is the matrix transpose. Commutator checks are user-constructed (`Curl(Gradient(φ))`, `Divergence(Curl(v))`) and are *not* mimetic identities on unstructured meshes — they hold only to truncation error on Cartesian grids.

**R3.** No built-in volume-integrated balance. A user can form `sum(Divergence(v) * cell_volume)`, but that is not a library diagnostic and has no source/sink/boundary accounting.

**R4.** 1 issue labelled `bug` (#100). Unusable as an independently admitted real-defect corpus.

**R5.** Tiny. Operator application on a 64³ grid is cheap.

**Paper.** No archival paper verified. Crossref / arXiv searches for a `findiff` software paper returned nothing usable.

**Verdict.** Best *clean* Python operator kit. Fails R4. Weak R3. Cartesian-only, so it cannot carry a mimetic-structure claim.

### 1.3 `py-pde`

**Language.** https://github.com/zwicker-group/py-pde — Python 2.31 MB, no C/Cython in-repo. Numerically meaningful operators are Python that `numba` (or jax/torch) compiles at first call. **Flag:** `cosmic-ray` mutates the Python; the executed kernel is compiled. Cache invalidation per mutant is a campaign-cost risk, not a mutability block.

**R2.** `grid.make_operator("divergence"|"gradient"|"laplacian"|"vector_gradient"|"vector_laplace"|"tensor_divergence")` returns a separately callable operator. Documented at https://py-pde.readthedocs.io/en/latest/manual/advanced_usage.html (also `docs/source/manual/advanced_usage.rst`). **No curl.** Operators are compiled callables, not inspectable sparse matrices, so a commutator is a numerical residual on fields, not a matrix identity.

**R3.** `ScalarField.integral` gives a volume integral from one state. There is no packaged source–sink–boundary balance.

**R4.** 4 issues labelled `bug`. Unusable corpus.

**R5.** Small grids are cheap after the first JIT. Thousands of mutants each paying a numba compile is the risk.

**Paper (verified).** Zwicker, “py-pde: A Python package for solving partial differential equations,” *JOSS* 5(48):2158 (2020), doi:10.21105/joss.02158. Crossref, 74 citations.

### 1.4 `jax-cfd`

**Language.** https://github.com/google/jax-cfd — library Python 720 kB; notebooks dominate linguist. Operators are Python/JAX. **Flag:** `jax.jit` compiles the traced Python. Mutation of `jax_cfd/base/finite_differences.py` is source-level and meaningful; each mutant pays compile cost. JAX primitives themselves are out of scope.

**R2.** Separately callable functions in `jax_cfd.base.finite_differences` (fetched 2026-09-07): `central_difference`, `forward_difference`, `backward_difference`, `laplacian`, `divergence`, `centered_divergence`, `gradient_tensor`, `curl_2d`, `curl_3d`. Adjoint via JAX reverse-mode (`jax.vjp` / `jax.grad`) on those functions — a bilinear identity can be run. Not a stored sparse matrix.

**R3.** Staggered MAC / Arakawa-C grid; `filtered_velocity_field` enforces a divergence-free initial condition; pressure projection keeps `divergence(v) ≈ 0`. Domain-sum of `divergence(v)` is a single-state mass residual. Not a general source–sink–boundary ledger.

**R4.** 0 issues labelled `bug`. 32 issues total, unlabelled. Experimental Google research repo. No published bug study.

**R5.** Demo 256² Navier–Stokes: ~1.8 s per trajectory after JIT (project notebook). Operator-only probes are cheap; full rollouts × thousands of mutants are not, because of compile + time stepping.

**Paper (verified).** Kochkov, Smith, Alieva, Wang, Brenner & Hoyer, “Machine learning–accelerated computational fluid dynamics,” *PNAS* 118(21):e2101784118 (2021), doi:10.1073/pnas.2101784118. Crossref, 941 citations.

### 1.5 Dedalus

**Language.** https://github.com/DedalusProject/dedalus — Python 1.34 MB (95.7%), Cython 61 kB (4.3%). The paper states a typical high-resolution run “will spend a majority of its time in optimized C libraries” (FFTW / LAPACK; not in-repo). The *operator graph* (`div`, `grad`, `lap`, `curl`, `integ`) is Python and symbolically inspectable. **Flag:** mutating Python changes composition of operators; it does not mutate spectral differentiation kernels.

**R2.** Symbolic operators are first-class (`problem.add_equation("div(u) + tau_p = 0")`; `d3.grad`, `d3.div`, `d3.curl`). Automated discrete adjoints: Skene & Burns, “Fast automated adjoints for spectral PDE solvers,” *PNAS* 123(15) (2026), doi:10.1073/pnas.2530440123, arXiv:2506.14792; implementation on the `adjoint` branch, examples at https://github.com/csskene/dedalus_adjoint_examples.

**R3.** `integ(...)` appears in the public equation API (gauge conditions, global constraints). A volume integral of a residual is available from one state. Not packaged as a conservation ledger.

**R4.** 48 issues labelled `bug` (example: #287, vector-field output scales crash). Usable but smaller than FiPy / SimPEG, and many issues are I/O or parallelism rather than operator identities.

**R5.** Production IVPs (3-D convection, spherical shells) are far too expensive for thousands of mutants. A tiny 1-D/2-D LBVP used only as an operator probe could be cheap; that is no longer “Dedalus as used.”

**Paper (verified).** Burns, Vasil, Oishi, Lecoanet & Brown, “Dedalus: A flexible framework for numerical simulations with spectral methods,” *Phys. Rev. Research* 2:023068 (2020), doi:10.1103/PhysRevResearch.2.023068. Crossref, 502 citations. arXiv:1905.10388.

---

## 3. Rejected list (one line each)

| Candidate | One-line reason |
|---|---|
| FiPy | 99.9% Python and the best conservation + bug corpus (415 `bug` labels; Guyer, Wheeler & Warren, *CiSE* 11(3):6–15, 2009, doi:10.1109/mcse.2009.52), but operators are field methods (`CellVariable.faceGrad`, `FaceVariable.divergence`), not separately callable discrete maps for a commutator. |
| scikit-fem | Pure Python (Gustafsson & McBain, *JOSS* 5(52):2369, 2020, doi:10.21105/joss.02369); `skfem.helpers.{grad,div,curl}` act on `DiscreteField` *inside* form assembly, not as inspectable operators. 15 labelled bugs, thin. |
| Firedrake + pyadjoint / dolfin-adjoint | Python frontend over PETSc / generated C (Rathgeber et al., *TOMS* 43(3), 2016, doi:10.1145/2998441). Adjoints exist (`pyadjoint.org`). R1 fail: numerically meaningful assembly is not Python source. |
| Thetis | Firedrake coastal model (Kärnä et al., *GMD* 11:4359–4382, 2018, doi:10.5194/gmd-11-4359-2018). Same R1 failure; conservation is real but not a Python-mutable operator kit. |
| Devito | Repo is Python; compiler emits C stencils (Louboutin et al., *GMD* 12:1165–1187, 2019, doi:10.5194/gmd-12-1165-2019). Adjoints exist (`AdjointOperator`, `jacobian_adjoint`). Mutating the DSL is not mutating the executed operator. |
| PyClaw / Clawpack | Hyperbolic conservation laws, but kernels are Fortran via f2py (Ketcheson et al., *SISC* 34(4):C210–C231, 2012, doi:10.1137/110856976). `kernel_language='Python'` exists for some Riemann solvers; the default and the performance path are Fortran. |
| pyMFEM | Documented SWIG binding of C++ MFEM (`mfem/PyMFEM`). Thin wrapper. R1 fail. |
| SfePy | Mostly Python + 10% C (Cimrman, Lukeš & Rohan, *Adv. Comput. Math.* 45:1897–1921, 2019, doi:10.1007/s10444-019-09666-0; also arXiv:1404.6391). Weak-form *terms*, not inspectable discrete div/grad/curl maps. |
| Underworld 2/3 | UW2: Python UI over C PIC/FEM (Mansour et al., *JOSS* 5(47):1797, 2020, doi:10.21105/joss.01797). UW3: SymPy → generated C → PETSc. R1 fail. |
| Oceananigans.jl | Julia (Ramadhan et al., *JOSS* 5:2018, 2020, doi:10.21105/joss.02018). Violates R1. See §5. |
| PyAMG | Python AMG solvers (Bell, Olson, Schroder & Southworth, *JOSS* 8(87):5495, 2023, doi:10.21105/joss.05495). No discrete differential operators, no conservation diagnostic. |
| torchdiffeq | ODE adjoints (`odeint_adjoint`), not spatial discrete operators or a PDE conservation ledger. Chen et al., *Neural ODEs*, NeurIPS 2018, arXiv:1806.07366 (this session’s Crossref keyword search did not isolate the record; arXiv id is the canonical identifier). |
| diffrax | JAX ODE/SDE adjoints (`RecursiveCheckpointAdjoint`, `BacksolveAdjoint`; Kidger, Oxford thesis 2021). Same rejection as torchdiffeq: time-adjoint, not spatial operator / FV balance. |
| pyoperators | Tiny (14 stars). Generic `Operator` + `.T`. No PDE operators, no conservation, no defect corpus. |
| `scipy.sparse.linalg.LinearOperator` codes | Interface only (`.T` / `.H` / `_rmatvec`). Not a PUT population; wrapping SciPy does not create independent programs or a defect history. |
| FEniCS / DOLFINx, PETSc, MFEM, deal.II | Named in the brief as thin-binding exclusions. Confirmed: numerically meaningful operators are C++. |

---

## 4. Cost to harness a shortlisted candidate

Estimates are engineer-weeks for one person who already has the P-series mutation harness, not calendar-months of a team. They assume *operator-probe* executions (build operators, run commutator / adjoint / volume balance), not production CFD.

| Work | Effort | Main technical risks |
|---|---|---|
| `discretize` TensorMesh operator harness (G, D, C, `C@G`, `D@C`, adjoint pairing, `vol * D @ flux`) | 2–4 weeks | Cython TreeMesh must be excluded or the campaign silently mutates the wrong code; identity residuals are exact 0 only for the mimetic pair — do not mix `cell_gradient` with `nodal_gradient` without reading the docs. |
| Attach SimPEG labelled bugs to those operators for RQ3 | +4–8 weeks | Most of the 106 bugs are inversion / survey / mapping, not operator identities. Mapping bugs onto ESPR lineages will be sparse; many will be NA. |
| `findiff` operator harness | 1–2 weeks | Commutators hold only to FD truncation error — a different certifier than `discretize`. R4 cannot be manufactured. |
| `py-pde` operator harness | 2–3 weeks | numba cache; no curl; conservation must be written. |
| `jax-cfd` operator + VJP harness | 3–5 weeks | JIT compile-per-mutant; 0 labelled bugs; Google research-repo churn. |
| Dedalus tiny-LBVP + adjoint-branch harness | 8–16 weeks | MPI, FFTW, adjoint-branch install, Cython extensions. Production IVPs are out of budget. |
| Engineer FiPy stencil matrices to *create* R2 | 6–12 weeks | High risk of building an operator that FiPy does not actually use. Not recommended. |
| New C++ toolchain on Firedrake / MFEM / PETSc | 3–6 months | New mutation tool, new build, new kill harness. Throws away the existing Python infrastructure. |

**If the goal is a confirmation *experiment* rather than a population:** the only honest cheap path is `discretize` TensorMesh operator probes, with SimPEG’s labelled bugs as a thin RQ3 add-on, and the n = 1 clustering limitation stated in the paper. That does not satisfy the population requirement this survey was asked to find.

---

## 5. Could R1 be relaxed? Mutation tools for C++ / Fortran / Julia

Relaxing “Python source + `cosmic-ray`/`mutmut`” opens the large C++ scientific stack (deal.II, MFEM, PETSc, FEniCS/DOLFINx) and Julia (`Oceananigans`). It does **not** produce a drop-in replacement for the existing harness. Verified tools:

| Language | Tool | Status (verified) | Useable here? |
|---|---|---|---|
| C / C++ | **Mull** (LLVM IR + JIT) | Denisov & Pankevich, ICSTW 2018, doi:10.1109/ICSTW.2018.00024; https://github.com/mull-project/mull, latest release 0.33.0 (2026-04-11). | Real tool. Applying it to PETSc-scale codes is itself a research project. Fortran via flang is not a supported path. |
| C / C++ | **Dextool Mutate** | https://github.com/joakim-brannstrom/dextool (plugin `mutate`); compared as the C++ tool in Agroce et al. FSE 2024. | Real. Clang-based; same build-system cost as Mull. |
| C / C++ / Fortran / … | **universalmutator** | Agroce et al., ICSE 2018 tool paper; “Syntax Is All You Need,” FSE 2024, https://agroce.github.io/fse24.pdf. Explicit Fortran in the supported-language list. Regex / Comby rewrites; `--noCheck` dumps mutants for an external build. | Can *generate* Fortran mutants. Does not compile or run them. A Clawpack / PETSc campaign would still need a per-mutant rebuild of the scientific stack. |
| Fortran | **Mothra** | King & Offutt, *Softw. Pract. Exper.* 21(7), 1991, doi:10.1002/spe.4380210704. Fortran 77 research system. | Dead. No maintained modern Fortran mutation engine was found. |
| Julia | **Gremlins.jl** | https://github.com/SuperSeriousLab/Gremlins.jl. JuliaSyntax-based; replacement for abandoned Mutation.jl (last real commit ~2019). | Real and current. Using it means abandoning the Python harness and starting over. |

**Implication.** Relaxing R1 is possible in principle (Mull or Dextool on a C++ FEM library; Gremlins.jl on `Oceananigans`). It does not create a cheap population. It replaces one missing population with a new toolchain whose cost is larger than the v4 confirmation experiment. `Oceananigans` is therefore not worth considering *given R1 as written*, and not a bargain if R1 is relaxed.

---

## Requirements recap (why the conjunction binds)

1. **Python-mutable numerically meaningful code** — excludes Firedrake, Thetis, Devito kernels, PyClaw Fortran, pyMFEM, Underworld, FEniCS, PETSc, Oceananigans.
2. **Inspectable discrete operators or an adjoint object** — excludes FiPy, scikit-fem, SfePy, PyAMG, torchdiffeq, diffrax, LinearOperator-as-population.
3. **Single-run conservation / balance** — easy for FV (`discretize`, FiPy); constructible elsewhere; never the unique blocker.
4. **Independently admitted real defects** — kills `findiff`, `py-pde`, `jax-cfd` as RQ3 subjects; leaves SimPEG and FiPy. FiPy already failed R2.
5. **Thousands of mutant executions** — kills production Dedalus / Firedrake / Oceananigans runs; operator-only probes on `discretize` / `findiff` survive.

R3 and R5 are satisfiable. R1∩R2 is not, at population scale. R4 is not, at the R1∩R2 intersection.

---

## Search audit

| Item | Toolchain | Hit tool | Status |
|-----|-----------|----------|--------|
| SimPEG Cockett 2015 | `get_crossref_paper_by_doi` 10.1016/j.cageo.2015.09.015 | crossref | ✓ |
| Dedalus Burns 2020 | `get_crossref_paper_by_doi` 10.1103/PhysRevResearch.2.023068; `search_openalex`; arXiv:1905.10388 | crossref | ✓ |
| Dedalus adjoint Skene & Burns | `search_arxiv` 2506.14792; `get_crossref_paper_by_doi` 10.1073/pnas.2530440123 | arxiv + crossref | ✓ |
| scikit-fem Gustafsson 2020 | `search_crossref` | crossref 10.21105/joss.02369 | ✓ |
| FiPy Guyer 2009 | `search_crossref` | crossref 10.1109/mcse.2009.52 | ✓ |
| py-pde Zwicker 2020 | `search_crossref` | crossref 10.21105/joss.02158 | ✓ |
| PyAMG Bell et al. | `search_crossref` | crossref 10.21105/joss.05495 | ✓ |
| SfePy Cimrman 2019 | `get_crossref_paper_by_doi` 10.1007/s10444-019-09666-0 | crossref | ✓ |
| PyClaw Ketcheson 2012 | `get_crossref_paper_by_doi` 10.1137/110856976 | crossref | ✓ |
| jax-cfd Kochkov 2021 | `get_crossref_paper_by_doi` 10.1073/pnas.2101784118 | crossref | ✓ |
| Firedrake Rathgeber 2016 | `get_crossref_paper_by_doi` 10.1145/2998441 | crossref | ✓ |
| Thetis Kärnä 2018 | `get_crossref_paper_by_doi` 10.5194/gmd-11-4359-2018 | crossref | ✓ |
| Devito Louboutin 2019 | `get_crossref_paper_by_doi` 10.5194/gmd-12-1165-2019 | crossref | ✓ |
| Underworld2 Mansour 2020 | `search_crossref` | crossref 10.21105/joss.01797 | ✓ |
| Oceananigans Ramadhan 2020 | `search_openalex` | openalex 10.21105/joss.02018 | ✓ |
| Mull Denisov 2018 | `get_crossref_paper_by_doi` 10.1109/ICSTW.2018.00024 | crossref | ✓ |
| Mothra King 1991 | WebSearch + Wiley page | webfetch doi:10.1002/spe.4380210704 | ✓ |
| universalmutator FSE 2024 | WebFetch agroce.github.io/fse24.pdf | webfetch | ✓ |
| findiff software paper | `search_crossref` / `search_arxiv` | none | △ no archival paper found |
| torchdiffeq Chen 2018 | `search_crossref` “Neural Ordinary Differential Equations Chen 2018” | did not isolate | △ cited as arXiv:1806.07366 |
| Language / bug counts | GitHub API `languages` + `search/issues?q=label:bug` | GitHub | ✓ snapshot 2026-09-07 |
| discretize operator docs | WebFetch discretize.simpeg.xyz tutorials | webfetch | ✓ |
| jax-cfd operators | WebFetch raw `finite_differences.py` | webfetch | ✓ |
| py-pde `make_operator` | WebFetch advanced_usage.rst | webfetch | ✓ |

`search_arxiv` title-style queries (`ti:…`) returned empty or off-topic hits for several software names; those items were recovered via DOI / Crossref / OpenAlex as above. `search_dblp` and `search_semantic` not used.
