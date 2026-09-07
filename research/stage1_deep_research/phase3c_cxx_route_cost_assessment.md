# Phase 3c — C++-route cost and risk assessment (Mull / Dextool vs Boost.Math failure)

**Date:** 2026-09-07
**Scope:** cost/risk assessment for relaxing R1 (Python-mutable) and targeting a C++ FEM/solver stack with Mull or Dextool. Not an experiment plan and not an authorization.
**Trigger:** `phase3b_put_population_feasibility.md` found no R1∩R2 population. The decision under test is: drop R1, mutate a mature C++ solver.
**Prior failure that this must be scored against:** Boost.Math C++ attempt, terminal `TECH_UNCERTAIN`, 8/12 funnel, `FORMAL_PROFILING_RETRY_FORBIDDEN=true`, Attempt-2 stalled at ~70% in *build preflight*. Never reached mutant generation or formal profiling (`docs/STATE.md` §4; `docs/superpowers/notes/2026-08-25-p3-attempt2-next-session-initialization.md`).
**Dense calendar window used as the cost baseline:** 2026-08-13 → 2026-08-27 (~2 engineer-weeks). Phase 1 FINER text also records a longer C++ line that never closed.

Paper search used `user-paper-search` first (`search_crossref`, `get_crossref_paper_by_doi`, `search_arxiv`, `search_openalex`). `search_dblp` returned empty (recorded). `search_semantic` not used (known non-functional). Tool docs / GitHub facts via WebFetch + `gh`. Snapshot date for GitHub counts: 2026-09-07.

---

## 1. Headline verdict (30 seconds)

**Mull does avoid per-mutant native rebuild. That is not what killed Boost.Math, and it does not make this route cheap.**

Current Mull (0.34.0, 2026-05-12) is an LLVM IR compiler plugin. It embeds mutants in **one instrumented binary** and `mull-runner` re-executes that binary, toggling one mutant per run. LLVM JIT is gone (deprecated January 2021). The 2018 ICSTW paper still describes the old JIT design; do not cite that paper as the current architecture.

The recorded Boost.Math failure was **build-preflight / infrastructure investment exceeding the executable chain**. It never reached the per-mutant rebuild that Mull would have saved. The proposed route still has to pass that same gate, now with a **mandatory Clang/LLVM version pin**, on a target that is at best comparable (serial MFEM) and at worst strictly heavier (PETSc / DOLFINx / deal.II / Firedrake). The existing Python harness is abandoned.

**Similarity verdict: PARTIALLY DIFFERENT, not a repeat and not an escape.**
The material difference is Mull’s compile-once economics *after* a green instrumented binary exists. The shared failure mechanism is everything before that binary exists. If the project repeats the Boost.Math process culture (contracts, evidence adapters, and qualification layers before a real compile-link-run), this *will* repeat failure #1. If the target is Firedrake or “FEniCS as used” (UFL → FFCx/TSFC → generated C), Mull cannot see the operator code; that is a **repeat of the Python-route trap, inverted**.

**Best candidate:** serial **MFEM**, mutating `DiscreteLinearOperator` / `GradientInterpolator` / `CurlInterpolator` / `DivergenceInterpolator` (and the `DiscreteGrad` / `DiscreteCurl` helpers), with operator-probe tests only. Stay off MPI.

**Cost to first real profiling run (not a green library build):** **8–15 engineer-weeks** under this project’s recorded process; **5–8** only if the executable chain is the only work. That is 4–8× the 2 weeks Boost.Math already consumed with zero profiling. A PETSc / full-FEniCSx / deal.II-candi stack is 20+ weeks and should be treated as a refusal.

Relaxing R1 still does **not** create a population. Success on MFEM is `n_projects=1` again. That is the already-recorded C3 blocker, now in C++.

---

## 2. Q1 — Does Mull avoid the per-mutant rebuild cost?

### 2.1 Answer

**Yes, qualified.** Current Mull compiles once (instrumented) and pays per-mutant *execution*, not per-mutant *rebuild*. Dextool is source-level; it *can* also compile once via mutant schemata, and falls back to per-mutant rebuild when a schema fails. The hypothesis “Dextool would not have this property” is **false as a blanket claim**.

### 2.2 Mull architecture today (0.34.0 docs, not the 2018 paper)

Official “How Mull works” (docs 0.34.0, fetched 2026-09-07, https://mull.readthedocs.io/en/latest/HowMullWorks.html):

- Mutations are found and created **in memory, on LLVM bitcode**.
- “All mutations are injected into original program’s code. Each injected mutation is hidden under a **conditional flag** that enables that specific mutation. The resulting program is compiled into a **single binary** which is run multiple times, one run per mutation.”
- Child subprocesses isolate mutant runs from the parent `mull-runner`.
- **“Mull no longer uses LLVM JIT.”** Historical note: JIT-related code removed by January 2021 (`PSA: Moving away from JIT`).
- Clang AST is used only for junk detection / validity, not as the mutation site.

Hello World and CMake tutorials confirm the operational loop:

```text
clang-N -fpass-plugin=/usr/lib/mull-ir-frontend-N -g -grecord-command-line  # embed
mull-runner-N ./the_same_binary                                           # toggle + run
```

The fmtlib tutorial (https://mull.readthedocs.io/en/latest/tutorials/CMakeIntegration.html) runs **164 mutants in 363 ms** after one instrumented `make core-test`. That is the compile-once property, measured on a real CMake C++ project.

**What this is not:**
- Not JIT (2018 paper is stale on this point).
- Not a per-mutant relink.
- Not “free.” The *first* instrumented compile is a full `-O0 -g` rebuild of every translation unit that the plugin sees. Changing the mutator set in a way that affects generation, or enabling coverage instrumentation, requires another compile. Incremental + ccache is a documented corruption risk (open issue “Incremental Mutation Testing with CCACHE Corrupts Full Run Results”).

### 2.3 The 2018 paper (what it actually claimed)

Denisov & Pankevich, “Mull It Over: Mutation Testing Based on LLVM,” ICSTW 2018, pp. 25–31, doi:10.1109/ICSTW.2018.00024. Crossref: 24 citations. arXiv preprint 1908.01540 (2019-08-05).

Abstract (arXiv, verbatim on the architecture): Mull “works with LLVM IR … and uses **LLVM JIT** for just-in-time compilation.” “only modified fragments of IR code are recompiled.” Evaluation subjects: **RODOS, OpenSSL, LLVM**. No FEM, no MPI, no numerical PDE library.

Use the paper for: IR-level mutation, language-agnostic-in-principle, historical design. Do **not** use it for: current runner, single-binary flags, or build integration. Those are the 2021–2026 plugin + `mull-runner` stack.

### 2.4 Build integration and LLVM pin

| Fact | Evidence |
|---|---|
| Plugin version **must match** Clang/LLVM | Docs: “the plugin version must match the Clang version used to compile the code.” Binaries are `mull-ir-frontend-N` / `mull-runner-N`. |
| Supported LLVM in 0.34.0 | 13 through 22 (Ubuntu mapping in `MODULE.bazel`; packages per LLVM version). |
| Required flags | `-fpass-plugin=...`, `-g`, `-grecord-command-line`. Tutorials also use `-O0`. Coverage needs `-fprofile-instr-generate -fcoverage-mapping` and a second compile. |
| CMake | Documented on **fmtlib**, not on a scientific stack. Pattern: `CXX=clang++-N` + `CMAKE_CXX_FLAGS` carrying the plugin. |
| Config | `mull.yml` / `MULL_CONFIG`. Exclude paths (e.g. gtest) can be applied at runner time without recompile; generation-time filters cannot. |
| Fragile? | **Yes, version-pinned.** Open issue: “mull 19 fails (ends with an error) more often than mull 18.” Another: “Mull 21 for macos.” Scientific stacks that want GCC, Intel, NVCC, or a distro Clang that is not `N` are a setup fight. |

`mull-instrument` was added in 0.34.0 for cases where the LLVM plugin is unavailable (PR #1185). That is a fallback, not the documented happy path.

### 2.5 MPI, CMake scientific stacks, numerical C++

- **CMake:** yes, documented (fmtlib). Transferable in principle.
- **MPI-parallel programs:** **not documented.** `mull-runner` execs the binary as a child process. An `mpirun` wrapper is conceivable and untested in Mull’s own docs. MPI mutation is a separate literature (e.g. Souza et al., LATW 2012, doi:10.1109/latw.2012.6261240) and is not in Mull.
- **Numerical / scientific C++:** **no documented Mull use** on MFEM, PETSc, deal.II, FEniCS, or Firedrake. Published / tutorial subjects: hello-world, OpenSSL, fmtlib, plus the 2018 paper’s RODOS / OpenSSL / LLVM. Treating “Mull works on fmtlib, therefore it works on hypre-linked MFEM” is an extrapolation, not a fact.

Stay serial. If the campaign needs MPI to exist, the Mull unknown becomes a first-class risk, not a footnote.

### 2.6 One-time vs marginal cost

| Cost | What you pay | When you pay it again |
|---|---|---|
| **One-time (large)** | Matching Clang-N + Mull-N install; force the PUT through that compiler; `-O0 -g` instrumented CMake; filter TUs so you do not instrument gtest / third_party / all of hypre | Compiler or Mull upgrade; CMake flag mistake; deciding to instrument a different file set |
| **Per-mutant (small)** | Process start + one run of the operator probe | Every mutant × input |
| **Hidden one-time** | Coverage rebuild; junk-detection surprises on heavily templated FEM code; binary-size growth if the plugin is aimed at the whole library rather than operator TUs | First time you see 10k mutants in `Operator::Mult` templates |

Vercammen, Demeyer, Borg, Pettersson & Hedin, *STVR* 2023, doi:10.1002/stvr.1865 (OpenAlex: 6 citations; arXiv:2210.17215): on CppCheck, an unoptimised campaign of 55,000 mutants took **11.8 days, of which 4.3 days was recompilation**. That is the cost Mull’s current design removes. It is also **not** the cost that stopped Boost.Math.

### 2.7 Is Mull maintained?

| Item | Value (2026-09-07, `gh`) |
|---|---|
| Latest release | **0.34.0**, 2026-05-12 |
| Previous | 0.33.0 (2026-04-11), 0.32.0 (2026-04-05) — active 2026 cadence |
| Last release commit | `a83b055f`, 2026-05-12 |
| `pushed_at` | 2026-07-31 |
| Stars | 835 |
| Open issues | 22 (search); repo `open_issues_count` 23 |
| Closed issues | 281 |
| Label `bug` | 21 total, **0 open** |
| Open issue character | Feature requests, LLVM-version friction, ccache corruption, no Windows, missing operators (ABS, SBR, memory). No open labelled crash-the-tool bug. |

**Verdict on maintenance:** actively maintained in 2026. The live risk is **toolchain matching**, not abandonment.

### 2.8 Dextool mutate (brief)

- **What it is:** Clang-AST / source-level mutation plugin in **Dextool**, implemented in **D** (repo language: D). https://github.com/joakim-brannstrom/dextool ; docs: http://joakim-brannstrom.github.io/dextool/plugin/mutate/
- **Default algorithm (README):** inject one mutant → run `build_cmd` → run `test_cmd`. `build_cmd` is “called to compile the program **each time a mutant is injected**.” That *is* per-mutant rebuild.
- **Schemata:** README advertises “Uses mutant schemata to compile and link **once per SUT**, rather than once per mutant.” Config key `mutants_per_schema`. A Chalmers MSc comparison (ODR bitstream, fetched 2026-09-07) states schemata “do not always compile”; on failure, Dextool **falls back to compiling mutants individually**.
- **Maintenance:** latest release **v5.3 “Chert”**, 2025-09-09; last commit 2026-04-20 (`32bdcad6`, mutate analyze-stop bugfix). 112 stars, 11 open issues, 7 labelled `bug`. Alive, smaller community than Mull, **adds a D toolchain**.
- **Papers:** no Dextool-mutate archival paper was recovered via Crossref / OpenAlex / arXiv under the tool name. Phase 3b’s Agroce et al. FSE 2024 comparison (`agroce.github.io/fse24.pdf`) was not re-retrieved this session: Crossref/OpenAlex queries on that title returned off-topic or empty. Recorded △.
- **Use here?** Only if Mull’s plugin cannot be aimed at the PUT. Schemata help, but the D toolchain + schema fallback re-opens the rebuild cost Mull is designed to close. **Do not pick Dextool to save build cost.**

### 2.9 Q1 one-liner

Mull: **yes, compile-once / run-many**, after a version-pinned Clang plugin build. Dextool: **source-level, schemata optional, rebuild fallback**. Neither has a documented path through MPI scientific stacks.

---

## 3. Q2 — Which C++ targets satisfy R2 + R4 + R5?

R1 is waived. R3 is not re-litigated (FV/FE balance is constructible once operators exist). The trap that matters is **where the operator code lives**: C++ TUs Mull can see, versus Python / generated C / JIT that it cannot.

GitHub linguist and issue counts are 2026-09-07 snapshots via `gh api`.

### 3.1 Scoreboard

| Target | R2 operators / adjoint | R4 labelled defects | R5 campaign-scale | Mull-visible operator code? | Use? |
|---|---|---|---|---|---|
| **MFEM (serial)** | **Yes** — first-class discrete G/C/D | **Yes** — 282 `bug` | **Yes** if operator-probe, serial | **Yes**, C++ | **Best** |
| DOLFINx C++ `discrete_*` | **Yes** — `discrete_gradient` / `discrete_curl` | Weak — **no `bug` label**; 154 title-hits / 992 issues | Partial — PETSc+MPI stack | **Yes for those two C++ fns**; **No for FFCx kernels** | Second, only if restricted to C++ discrete ops |
| deal.II | Partial — spaces + `FEValuesViews::{curl,gradient,divergence}` + `transpose_operator`; **no** MFEM-style discrete G/C/D objects | **Yes** — 464 `Bug` | Weak — hours-scale library; `-O0` + plugin will hurt | Yes (C++), but you are mutating assembly helpers, not a stored operator | Not first |
| PETSc | Adjoint **yes** (`TSAdjoint`, `MatMultTranspose`); discrete G/C/D **no** | GitLab **338** `bug` / 1921 issues (964 open); GitHub issues disabled | No for a library-wide campaign; probe-only still needs MPI+BLAS+hypre | C, not the de Rham operators you need | No for R2 commutator |
| Firedrake | Adjoint **yes** (pyadjoint); operators are UFL symbols | **Yes** — 346 `bug` | No for production; probes possible | **No** — TSFC → generated C | **Refuse** (inverted Python trap) |
| FEniCS-as-used (UFL forms) | Same trap as Firedrake | DOLFINx issues, no `bug` label | Same | **No** for form kernels | Refuse as the PUT |

No curated Defects4J-style dataset was found for any of these. R4 is GitHub/GitLab labels only.

### 3.2 MFEM — best candidate

**Paper (verified).** Anderson et al., “MFEM: A modular finite element methods library,” *Computers & Mathematics with Applications* 81:42–74 (2021), doi:10.1016/j.camwa.2020.06.009. Crossref, 393 citations. arXiv:1911.09220. Follow-on: Andrej et al., arXiv:2402.15940, *IJHPCA* 2024, doi:10.1177/10943420241261981.

**Language.** `mfem/mfem`: C++ 20.3 MB, C 76 kB, CMake 313 kB. Stars 2231. This is a C++ library, not a Python wrapper.

**R2 — APIs (concrete).**

- `mfem::DiscreteLinearOperator` / `mfem::ParDiscreteLinearOperator` — rectangular operator between two `FiniteElementSpace`s.
- `AddDomainInterpolator(DiscreteInterpolator*)` with `GradientInterpolator`, `CurlInterpolator`, `DivergenceInterpolator`.
- Helpers: `mfem::DiscreteGrad(edge_fes, vert_fes)`, `mfem::DiscreteCurl(face_fes, edge_fes)` (docs.mfem.org namespace pages, v4.1–v4.9).
- Convenience: `mfem::common::ParDiscreteGradOperator`, `ParDiscreteCurlOperator` (`pfem_extras.hpp`).
- Adjoint of a linear `Operator`: `MultTranspose` / assembled transpose. There is **no** dolfin-adjoint-style automated discrete adjoint of a nonlinear time-dependent model. For the bilinear-identity certifier, `Mult` vs `MultTranspose` on the discrete interpolators is enough.

These are separately callable objects. A commutator is a matrix (or operator) product, the same shape as `discretize`’s `CURL @ GRAD == 0`.

**R4.** 282 issues labelled `bug` (of 2496 issues). Example class: real numerical/assembly defects, not a toy tracker. No independent published bug-mining corpus found. Usable as an admitted defect history; mapping those 282 onto ESPR lineages will be sparse, same warning as SimPEG’s 106.

**R5.**

- Serial build is first-class: `make serial -j` or `cmake .. && cmake --build . -j` (https://mfem.org/building/, `INSTALL`). **MPI, hypre, METIS are optional.** This is the only named target that can look like Boost.Math’s “no MPI, no TPL” constraint while still exposing G/C/D.
- Official docs do not publish a wall-clock. Serial library+examples on a laptop is typically minutes, not hours. GPU/CUDA builds are a different universe (issue #5363: sm_120 compile RSS tens of GB) — **do not enable CUDA**.
- Operator-probe runtime: assemble G, C, D on a tiny mesh; products and a transpose pairing. Milliseconds to seconds. Hundreds–thousands of mutant×input cells fit **if** the instrumented binary is serial and the probe is the test program.
- Library-wide `-O0` instrumentation of all 20 MB of C++ is the failure mode. Restrict the plugin to interpolator / `DiscreteLinearOperator` TUs.

**Mull visibility.** The operators *are* the C++. This is the rare case where relaxing R1 actually buys R2.

### 3.3 FEniCS / DOLFINx — operators exist; the used path is the trap

**Papers (verified).**
- Alnæs et al., “The FEniCS Project Version 1.5,” *Archive of Numerical Software* (2015), doi:10.11588/ans.2015.100.20553. OpenAlex, 1990 citations. `get_crossref_paper_by_doi` returned empty this session (△ Crossref; recovered via OpenAlex).
- Baratta et al., “DOLFINx: The next generation FEniCS problem solving environment,” Zenodo preprint, doi:10.5281/zenodo.18101307 (2025-12-31 version in OpenAlex). Not a journal article.
- Scroggs, Dokken, Richardson & Wells, *TOMS* 48(2) (2022), doi:10.1145/3524456, 216 citations — DOF maps for curl/div-conforming elements, implemented in the FEniCSx stack.
- Farrell, Ham, Funke & Rognes, “Automated Derivation of the Adjoint…,” *SISC* 35(4):C369–C393 (2013), doi:10.1137/120873558, 233 citations — **dolfin-adjoint**.
- Mitusch, Funke & Dokken, “dolfin-adjoint 2018.1,” *JOSS* 4(38):1292 (2019), doi:10.21105/joss.01292, 187 citations.

**R2.** Python API (docs 0.11 / main, fetched 2026-09-07):

- `dolfinx.fem.discrete_gradient(V0, V1) -> MatrixCSR`
- `dolfinx.fem.discrete_curl(V0, V1) -> MatrixCSR`

These wrap `dolfinx.cpp.fem.discrete_gradient` / `discrete_curl`. Unit test `python/test/unit/fem/test_discrete_operators.py` multiplies `G` and checks it against `ufl.grad` interpolation. That is a real, inspectable discrete gradient. Adjoint: dolfin-adjoint / pyadjoint on the **form** graph, not on those two matrices.

**The trap.** Typical FEniCS numerics are UFL forms compiled by **FFC / FFCx** to C and then JIT/compiled. Mull aimed at the DOLFINx C++ library sees `discrete_gradient` / `discrete_curl` implementation and PETSc wrappers. It does **not** see the generated form kernels that execute a user’s PDE. Mutating Python UFL is the old R1 path. Mutating ephemeral generated C is not a stable PUT.

**Language.** `FEniCS/dolfinx`: C++ 2.40 MB, Python 1.59 MB. Mixed. Stars 1191.

**R4.** **No `bug` label** in the DOLFINx label set. 992 issues; 154 with `bug` in the title; 218 with `bug` in title or body. That is not an admitted labelled corpus. FFCx has 22 labelled `bug`; Basix 23. Thin and split across repos.

**R5.** DOLFINx is not a standalone C++ tarball. It wants PETSc, MPI, Basix, UFCx/FFCx, HDF5. Habera & Hale (2026) ran a DOLFINx Poisson solver to 512 MPI ranks — that is the production shape, not a mutation-campaign shape. A *restricted* C++ unit that only constructs `discrete_gradient`/`discrete_curl` on a tiny mesh could be fast. Getting that unit built with `clang-N` + Mull plugin through the FEniCSx dependency DAG is the expensive part.

**Verdict.** R2 is real. R4 is weak. R5 is a stack problem. Use only if MFEM is impossible and the PUT is defined as “the two C++ discrete-operator functions,” not “FEniCS applications.”

### 3.4 deal.II — C++ visible, operators not first-class

**Papers (verified).**
- Bangerth, Hartmann & Kanschat, *TOMS* 33(4):24 (2007), doi:10.1145/1268776.1268779, 995 citations.
- Arndt et al., “The deal.II finite element library: Design, features, and insights,” *CAMWA* 81:407–422 (2021), doi:10.1016/j.camwa.2020.02.022, 273 citations; arXiv:1910.13247.

**Language.** `dealii/dealii`: C++ **212 MB** (linguist). Stars 1722. Template-heavy.

**R2.** `FE_Nedelec`, `FE_RaviartThomas`; `FEValuesViews::Vector::{curl,gradient,divergence}`; `LocalIntegrators::Maxwell::{curl_matrix,curl_curl_matrix}`; `LinearOperator` + `transpose_operator()`. Interpolation/curl commuting is documented for Nédélec on rectangular cells. There is **no** public `DiscreteGrad`/`DiscreteCurl` matrix object analogous to MFEM or DOLFINx. A commutator certifier must be *assembled by the experiment*, which is the FiPy failure mode from phase 3b (building an operator the library does not actually expose as such).

Adjoint: `transpose_operator` for linear maps; no dolfin-adjoint.

**R4.** 464 issues labelled `Bug` / `bug` (GitHub treats them as one). Strong admitted history.

**R5.** Official readme: full configure+build+install+`make test` “should take **between a few minutes and an hour**.” candi stacks with Trilinos/p4est/HDF5 are **~1 hour** in published install notes (Heron 2017: deal.II 1718 s + Trilinos 1546 s). `-O0 -g` + Mull plugin on 212 MB of templates is a compile-time risk, not a runtime risk. Incremental helps the library; it does not help the first instrumented cold build.

**Verdict.** C++ and R4 are fine. R2 is the wrong shape. Do not pick deal.II over MFEM.

### 3.5 PETSc — real adjoint, wrong operators, wrong tracker shape

**Papers (verified).**
- Zhang, Constantinescu & Smith, “PETSc TSAdjoint…,” *SISC* 44(1):C1–C24 (2022), doi:10.1137/21M140078X, 14 citations.
- Users’ manuals, e.g. Balay et al., Rev. 3.15, doi:10.2172/1814627 (2021).

**Language.** `petsc/petsc` is a **mirror** of https://gitlab.com/petsc/petsc (`has_issues: false`). Linguist: C 46.3 MB, C++ 3.8 MB, Python 3.2 MB, Fortran 0.95 MB. Stars 538.

**R2.**
- Adjoint: `TSAdjoint`, `TSAdjointSolve`, callbacks; `MatMultTranspose` / `MatMultHermitianTranspose` on `Mat`. This is a **time-stepping / linear-algebra adjoint**, not a discrete `curl∘grad`.
- Discrete div/grad/curl as separately callable de Rham maps: **not a PETSc public API**. `PetscFE` / `DMPlex` can discretize PDEs; they do not give you MFEM’s interpolators.

**R4.** GitHub issue search returns 0 (issues disabled). GitLab API (2026-09-07): **1921** issues, **964** open, **338** labelled `bug` (0 labelled `Bug`). Title/body search for “bug” returned 130. Primary historical channel is still `petsc-maint@mcs.anl.gov`. The labelled GitLab corpus is usable and larger than MFEM’s 282; it does not supply discrete G/C/D.

**R5.** `./configure` + MPI + BLAS/LAPACK + often hypre/METIS/SuperLU. Cold builds are tens of minutes; the dependency surface is the Boost.Math failure multiplied. A library-wide Mull campaign is not a study, it is a compiler research project. Fortran paths are out of Mull’s supported happy path.

**Verdict.** Buys a real adjoint (TSAdjoint) and fails the commutator. Heavier than Boost.Math in every build-system axis. Not the first target.

### 3.6 Firedrake — refuse for Mull

**Papers (verified).**
- Rathgeber et al., *TOMS* 43(3):1–27 (2016), doi:10.1145/2998441, 380 citations.
- Homolya, Mitchell, Luporini & Ham, “TSFC: A Structure-Preserving Form Compiler,” *SISC* 40(3):C401–C428 (2018), doi:10.1137/17M1130642, 34 citations. TSFC “produces **low-level code** that carries out the finite element assembly.”
- dolfin-adjoint / pyadjoint as above.

**Language.** `firedrakeproject/firedrake`: Python 5.24 MB, Cython 261 kB, C++ 21 kB. Stars 672.

**R2.** UFL `grad`/`div`/`curl` + pyadjoint. The executed operator is **TSFC-generated C**, scheduled through loopy (Firedrake 2026.4 docs, `slate.slac.compiler`).

**R4.** 346 labelled `bug` (of 1704 issues). Fine as a corpus, irrelevant if Mull cannot mutate the operator.

**R5 / visibility.** Mull on the Firedrake Python repo mutates the DSL and compiler, not the discrete operator. Mull on generated kernels mutates **ephemeral, cache-keyed C**. That is the phase 3b Python-route trap run in reverse. **Refuse.**

### 3.7 Other credible names (one line)

| Name | Why not |
|---|---|
| hypre / METIS | Solvers / partitioners. No de Rham operators. |
| deal.II + ASPECT | Application on deal.II; still no first-class G/C/D; candi build is hours. |
| FEniCSx Basix | Basis evaluation (Scroggs et al. JOSS 10.21105/joss.03982). Not G/C/D maps. |
| Gridap (Julia) | Badia & Verdugo, JOSS 10.21105/joss.02520. Wrong language; R1-relaxed still needs Gremlins.jl, not Mull. |

### 3.8 Population, even if R1 is gone

Independently developed C++ programs that expose inspectable G/C/D **and** are Mull-visible: **MFEM**, plus a *narrow* DOLFINx C++ slice. That is one library and a maybe. It is not 8–12 PUTs. Treating MFEM miniapps as a population repeats `n_projects=1`.

---

## 4. Q3 — Similarity to the Boost.Math failure

### 4.1 What Boost.Math actually had to build

From `2026-08-15-p3-boost-math-pilot-only.md` and `2026-08-17-p3-boost-math-pilot-build-preflight-only.md`:

- Subject: header-only Boost.Math, **standalone**, `BOOST_MATH_STANDALONE`, **no other Boost**, **no MPI**, **no CUDA**, CMake consumer harness.
- Frozen tree: 4396 files, ~95.6 MB, `add_library(boost_math INTERFACE)`.
- Authorized production slice that was planned: CMAKE_CONFIGURE → BASELINE_BUILD → BASELINE_SMOKE of **one** executable checking `pi<double>()` ∈ (3.14, 3.15).
- What was *not* in that slice: mutants, MRs, profiling, full CTest.
- What the project actually spent the time on: schemas, hash chains, intent/result writers, synthetic-CMake tests, Cloud/local contract layers, Attempt-2 coordinator. Handoff of 2026-08-25: Attempt-2 ~70%, `attempt_2_authorized=false`, “合同、证据和 gate 的投入曾经超过可执行链本身.”
- Formal outcome: `TECH_UNCERTAIN`, 8/12, retry forbidden. **Zero mutant generation.**

Boost.Math was the *easy* C++ subject. The failure was not “hypre would not link.”

### 4.2 Comparison table

| Axis | Failed Boost.Math attempt | Proposed C++ solver route (Mull + MFEM serial, best case) | Proposed route if PETSc / DOLFINx-full / deal.II-candi / Firedrake |
|---|---|---|---|
| Language | C++ (header-only) | C++ (compiled library) | C++ / C / Python / generated C |
| Build-system complexity | CMake interface lib + consumer harness | CMake or GNU make; documented 3-command serial | configure/CMake + MPI + BLAS + hypre/METIS/HDF5/Basix/FFCx |
| External dependencies | None in standalone mode | None required for serial | Many; this is strictly heavier than Boost.Math |
| MPI | No | **No (must stay serial)** | Yes — Mull-undocumented |
| Per-mutant rebuild | Would have been required under a source-patch harness; **never reached** | **No** (Mull single binary) | Mull: no, *if* a binary exists; Firedrake: no stable binary for operators |
| Harness | New C++ pilot alongside Python confirmatory stack; still unfinished | **Rewrite.** `cosmic-ray` / `mutmut` discarded. New wrap of `mull-runner` + kill/certify oracles | Same rewrite, larger PUT |
| Operator exposure | None (float-to-float special functions) | **The thing being bought:** Discrete G/C/D | Firedrake/FEniCS-as-used: bought then lost to codegen |
| Defect corpus | Not the point of the pilot | 282 labelled bugs | deal.II 464; Firedrake 346; PETSc GitLab 338 `bug` / 1921 issues |
| Recorded failure mechanism | Infrastructure / build-preflight exceeded the executable chain | **Same mechanism is still on the critical path** (Clang-N + plugin + first instrumented binary + new harness) | Same, larger |
| Scientific payoff if it works | Pilot feasibility only | Commutator + transpose identity on a real de Rham library | Same only if operators are Mull-visible |

### 4.3 Verdict

**PARTIALLY DIFFERENT.**

What is different, and real:

1. **Mull compile-once** — would have mattered *after* Boost.Math had a binary. It did not have one.
2. **R2 payoff** — Boost.Math could never host the two clean certifiers. Serial MFEM can.

What is the same:

3. Language C++, CMake, a new harness, and a project that has already shown it will spend weeks on the gate in front of `clang`/`cmake`.
4. No reuse of the Python mutation engine.

What is worse than Boost.Math unless MFEM-serial is enforced:

5. MPI, TPLs, LLVM version pin, codegen traps.

Calling this a **REPEAT** would ignore (1) and (2). Calling it **MATERIALLY DIFFERENT** would ignore (3)–(5) and the fact that failure #1 never touched the axis Mull fixes. **PARTIALLY DIFFERENT** is the accurate label. The difference is conditional on (a) serial MFEM, (b) plugin aimed at operator TUs, (c) no second infrastructure theatre.

---

## 5. Q4 — Engineer-week cost to first real profiling

“First real profiling” = one authorized run that generates mutants on a frozen MFEM operator site, executes the two certifiers (commutator, adjoint pairing) on a frozen input set, and writes an atomic profiling record. A green `libmfem.a` is not profiling. A green `mull-runner` on fmtlib is not profiling.

### 5.1 Breakdown (one person who already knows the P-series evidence rules)

| Work | Ruthless executable-chain (weeks) | Expected under recorded P3 process (weeks) | What burns the time |
|---|---|---|---|
| Toolchain setup | 0.5–1 | 1–2 | Clang-N + Mull-N match; prove Hello World + fmtlib tutorial; Darwin vs Linux (Mull is “great” on macOS/Linux, not Windows). Open issue: macOS LLVM 21. |
| Harness rewrite | 2–3 | 4–8 | Abandon `cosmic-ray`. Wrap `mull-runner`, map killed/survived onto existing evidence schemas **without** inventing a new contract family. This is where Boost.Math went to die. |
| PUT selection + build | 1–2 | 2–4 | Serial MFEM, no MPI/hypre/CUDA; consumer or miniapp that only builds G/C/D; plugin flags on **operator TUs only**. |
| Mutant generation | 0.5 | 1 | Mull does this at compile. Cost is filtering junk on templates and locking include/exclude paths. |
| Certification implementation | 1 | 1–2 | `C*G` residual; `D*C` residual; `<Au,v> − <u,Aᵀv>`; freeze tolerances *before* seeing mutants. |
| Campaign execution | 0.5 | 1 | Hundreds–low-thousands of mutant×probe cells. Runtime is not the risk; flaky timeouts and coverage rebuilds are. |
| **Total to first profiling** | **5–8** | **8–15** | |

**Compare:** Boost.Math consumed **~2 weeks** of dense work and produced **no profiling**. The ruthless column is already 2.5–4× that, on a compiled library plus a new tool. The expected column is 4–8×. Phase 3b’s “3–6 months” applies if the target is PETSc/Firedrake/full FEniCSx — accept that number and **do not start**.

### 5.2 What would make the estimate a lie

- Picking Firedrake or UFL-FEniCS as the PUT (Mull never sees operators).
- Enabling MPI “because the library supports it.”
- Instrumenting the entire MFEM tree at `-O0`.
- Replaying Attempt-2’s contract/hash/gate expansion before a single `mull-runner` line on an MFEM probe.
- Treating first profiling as a population. It is n=1. RQ3 on 282 bugs is a later, separate 4–8 weeks and will be sparse.

### 5.3 Bottom line

Pay **8–15 engineer-weeks** for a chance at one solver and two certifiers, with Mull actually removing the rebuild term. Do not tell ourselves this is cheaper than Boost.Math. It is more expensive, with a better scientific object if — and only if — the executable chain is allowed to exist.

---

## 6. Search audit

| Ref | Toolchain | Hit tool | Status |
|-----|-----------|----------|--------|
| Denisov & Pankevich 2018 Mull | `get_crossref_paper_by_doi` 10.1109/ICSTW.2018.00024; `search_arxiv` 1908.01540 | crossref + arxiv | ✓ |
| Mull current architecture / JIT deprecation | WebFetch mull.readthedocs.io HowMullWorks + HelloWorld + CMakeIntegration (docs **0.34.0**) | webfetch | ✓ |
| Mull releases / issues | `gh release list` + `gh api` search | GitHub | ✓ 0.34.0 (2026-05-12); 0 open labelled bugs; 22 open issues |
| Dextool mutate docs + schemata | WebFetch GitHub README + joakim-brannstrom.github.io | webfetch | ✓ source-level; schemata advertised; rebuild fallback documented |
| Dextool releases / issues | `gh` | GitHub | ✓ v5.3 2025-09-09; last commit 2026-04-20; language D |
| Dextool archival paper | `search_crossref` / `search_openalex` / `search_arxiv` | none on tool name | △ no paper recovered |
| Agroce FSE 2024 / Dextool comparison | `search_crossref` “Syntax Is All You Need Agroce”; `search_openalex` | off-topic / miss | △ not re-verified this session; phase 3b used webfetch of agroce.github.io/fse24.pdf |
| Vercammen et al. STVR 2023 C++ mutation cost | `search_openalex` | openalex 10.1002/stvr.1865 | ✓ |
| F-ASTMut schemata | `search_openalex` | openalex 10.1016/j.simpa.2023.100500 | ✓ |
| Souza et al. MPI mutation operators | WebSearch → doi:10.1109/latw.2012.6261240 | webfetch/doi | ✓ (existence; not a Mull integration) |
| Anderson et al. 2021 MFEM | `get_crossref_paper_by_doi` 10.1016/j.camwa.2020.06.009; `search_arxiv` 1911.09220 | crossref + arxiv | ✓ |
| Andrej et al. 2024 MFEM | `search_arxiv` 2402.15940 | arxiv | ✓ |
| MFEM DiscreteGrad/Curl APIs | WebSearch + docs.mfem.org class pages | webfetch | ✓ |
| MFEM / deal.II / DOLFINx / Firedrake bug counts | `gh api search/issues` | GitHub | ✓ 282 / 464 / (no label; 154 title) / 346 |
| Alnæs et al. 2015 FEniCS 1.5 | `search_openalex`; `get_crossref_paper_by_doi` 10.11588/ans.2015.100.20553 empty | openalex | △ Crossref miss; OpenAlex ✓ |
| Baratta et al. DOLFINx preprint | `search_openalex` | openalex 10.5281/zenodo.18101307 | ✓ preprint, not journal |
| Scroggs et al. 2022 TOMS DOF maps | `get_crossref_paper_by_doi` 10.1145/3524456 | crossref | ✓ |
| Farrell et al. 2013 dolfin-adjoint | `get_crossref_paper_by_doi` 10.1137/120873558 | crossref | ✓ |
| Mitusch et al. 2019 dolfin-adjoint JOSS | `search_crossref` | crossref 10.21105/joss.01292 | ✓ |
| Rathgeber et al. 2016 Firedrake | `get_crossref_paper_by_doi` 10.1145/2998441 | crossref | ✓ |
| Homolya et al. 2018 TSFC | `get_crossref_paper_by_doi` 10.1137/17M1130642 | crossref | ✓ |
| DOLFINx `discrete_gradient` / `discrete_curl` | WebFetch docs.fenicsproject.org + GitHub test file | webfetch | ✓ |
| Arndt et al. 2021 deal.II | `get_crossref_paper_by_doi` 10.1016/j.camwa.2020.02.022; `search_arxiv` 1910.13247 | crossref + arxiv | ✓ |
| Bangerth et al. 2007 deal.II | `search_crossref` | crossref 10.1145/1268776.1268779 | ✓ |
| deal.II build time | WebFetch dealii.org readme | webfetch | ✓ “a few minutes and an hour” |
| Zhang et al. 2022 TSAdjoint | `search_crossref` / `get_crossref_paper_by_doi` 10.1137/21M140078X | crossref | ✓ |
| PETSc Users Manual 3.15 | `search_crossref` | crossref 10.2172/1814627 | ✓ |
| PETSc issue tracker | `gh api` (GitHub issues disabled); GitLab API `x-total` + `labels=bug` | GitHub + curl GitLab | ✓ mirror; **1921** issues, 964 open, **338** labelled `bug` |
| `search_dblp` Mull / Dextool | `search_dblp` | empty | △ non-functional as previously observed |
| `search_semantic` | not called | — | △ known non-functional; not used |

`search_arxiv` title-style queries for “DOLFINx Baratta” returned off-topic hits; the DOLFINx preprint was recovered via OpenAlex. Crossref keyword search for “Dextool mutate” and “Syntax Is All You Need Agroce” was polluted by biological mutation / meme titles.
