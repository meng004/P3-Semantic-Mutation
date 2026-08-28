# P3 claim-path reprioritization after Stage I empty candidates

Task: `P3_CLAIM_PATH_REPRIORITIZATION_AFTER_STAGE1_EMPTY_CANDIDATES`
Model / reasoning: `gpt-5.6-sol` / high
Mode: one-shot scientific path decision. Compare exactly three paths. Do not design the selected path, write code, or run an experiment.
Unique terminal: `NEXT_PATH_CLAIM_SCOPE_REDUCTION`

This decision is binding. A second round of the same reprioritization is forbidden. The selected path's unique next task is the only authorized continuation.

## 1. Evidence baseline

Worktree: `/tmp/p3-c3-ordinal9-22-source-recovery`
Branch: `cursor/content-addressed-source-join-b65d`

| Object | Value |
|---|---|
| HEAD at decision start | `9d222f42c14d23f5f29e4e05dccf626fd5de1622` |
| Parent | `c64fa70840e10f7a4729047bd407ea1ea68f8fd7` |
| Remote branch | `origin/cursor/content-addressed-source-join-b65d` = `9d222f42c14d23f5f29e4e05dccf626fd5de1622` |
| Porcelain at start | empty |
| Stage I slice | `p3-c3-prospective-multiproject-applicability-stage1-v2` |
| Stage I terminal status | `STAGE1_APPLICABILITY_CENSUS_COMPLETE` |
| Stage I terminal file SHA-256 | `f2e9af90ed31bd118a80808a04e3af66c5abee539f0093c6087c176e2bee51ab` |
| Stage I terminal artifact SHA-256 | `45757bb594d582b380ee7955f0caeab92adfd3c10702c31cf788f896a6595a97` |
| Stage I disclosure SHA-256 | `9f0040f460d48310d764c10a75319b8ec4fb4fdb6b691e78b153d284cdaa0552` |
| Claim ledger SHA-256 | `bf4979662697b2d0565bb70eec88b22673e84bee93b61234555342efb4082a68` |
| C3 | `blocked` |
| `n_projects` | 1 (ordinal 8 only) |

Identity reconstruction that passed before comparison:

- `validate_stage1_terminal()` accepted the official terminal.
- 14 subjects, ordinals 9→22; 140 closures.
- 0 `SITE_FROZEN`; 140 `APPLICABILITY_CLOSED_NOT_APPLICABLE`.
- Stage II candidate universe = 0 under `site_frozen_count >= 1`.
- Stage II and old Slice B official/staging namespaces do not exist.
- Ledger bytes are unchanged.

Fixed premises that this decision does not reopen:

- Ordinals 9–22 have a completed official Stage I.
- The current version forbids rerun or predicate edits.
- The current Stage II candidate universe is empty and permanently closed.
- 0/140 applies only under the frozen PBF, predicates, inventory, and first-applicable boundary.
- 0/140 does not mean these programs lack target semantic constructs.
- Ordinal 8 remains the only paired project.
- C3's original upgrade condition remains unmet.

## 2. Why current Stage II is closed

The approved Stage II candidate rule keeps a subject only when rebuilt `site_frozen_count >= 1`. The official census rebuilt 0 such subjects. An authorized Stage II of this version therefore cannot produce a new `PAIRED_EVIDENCE_COMPLETE` project. The Stage I disclosure already closed that path. This task does not reopen it, does not create a Stage II controller, and does not re-enroll ordinals 9–22 in the same version.

## 3. A / B / C comparison

The three candidates are exactly:

- A: `NEW_COHORT`
- B: `NEW_AUTHORITY_SAME_COHORT`
- C: `CLAIM_SCOPE_REDUCTION`

Design files, test PASS, and controller READY are not observations.

### 3.1 Path A: NEW_COHORT

A new prospective cohort is allowed only if admission is frozen before project pick, and only if admitted objects already have unique recoverable source identity, at least two distinct non-NumPy repositories, an executable or statically checkable public interface, PBF evidence that can publish contract-authority schema/interface objects, a prior applicability rule, prior contract-generator plus invocation plus oracle authority, a prior semantic/syntactic pair-construction seam, and a controlled runner. Site choice must not depend on the 0/140 outcome. Adding more ordinary source projects that repeat the current 0-candidate profile is forbidden.

| Question | Answer |
|---|---|
| 1. Next new observation | Official applicability or paired observation on a new admitted cohort. Not available until admission and the missing seams exist. |
| 2. What it can change | New-subject eligibility and, if paired execution later succeeds, a C3 evidence component (`n_projects` > 1). |
| 3. Frozen inputs now | 35-subject identities, descriptors, PBFs, slot inventory, applicability registry, contract-generator registry. Archives exist only for the already-closed 9–22 set (14/35). |
| 4. Production seams now | Successor `freeze_production_contracts()` returns `()`. Successor pair construction and controlled runner raise if given nonempty input. Only ordinal 8 has paired seams, and it is NumPy. |
| 5. Independent stages to first new observation | 9: admission design; acquire ≥2 qualifying non-NumPy objects; archive/identity recovery; PBF with contract-authority schema evidence; freeze applicability; freeze contract/invocation/oracle; freeze pair seam; freeze runner; authorize and observe. |
| 6. New external objects | Yes. No current non-NumPy object satisfies the full admission list. |
| 7. Outcome-adaptive selection risk | Material if objects are chosen because 9–22 failed. Pre-frozen admission reduces but does not remove that risk. |
| 8. Second and third project | Not with current objects. Requires at least two new distinct non-NumPy projects that already meet the full list. |
| 9. What C3 still lacks even if successful | RQ2 uncertainty accounting (project-clustered interval, frozen overlap on the new projects) and the original upgrade condition. A 3-project pilot still does not automatically upgrade C3. |
| 10. Earliest stop | Admission design finds fewer than two interface-ready non-NumPy projects; or first official observation is empty under the new frozen rule. |
| 11. Scientific value if it fails | A negative admission audit, if the rule is frozen first. Not a C3 upgrade. |
| 12. Design/governance-without-data risk | High. Most required seams do not exist. The next work would be protocol construction, not data. |

### 3.2 Path B: NEW_AUTHORITY_SAME_COHORT

A new disclosed exploratory version on the same ordinals 9–22, for example a new PBF/interface authority or predicate. It is a post-outcome redesign after 0/140. It is not the original confirmatory slice. The old 140 closures stay and must not be overwritten. New results are exploratory/adaptive only. A stronger claim would need an independent validation cohort. Relaxing predicates until a site appears is forbidden. A new authority must have a direct relation to family semantics, contract, invocation, and oracle.

| Question | Answer |
|---|---|
| 1. Next new observation | An exploratory re-census under a new authority identity, leaving the old 140 intact. |
| 2. What it can change | Exploratory eligibility under the new authority. It cannot restore confirmatory Stage II of this version. |
| 3. Frozen inputs now | The closed 9–22 identities, archives, PBFs, old 140 closures, and the pre-outcome contract-authority design. |
| 4. Production seams now | Same successor gap: empty contract freeze; no pair seam; no controlled runner; no non-NumPy oracle. |
| 5. Independent stages to first new observation | 5: exploratory authority design with an independent semantic rationale; new authority/PBF/predicate identity; new official exploratory namespace; authorization; exploratory census. Confirmatory use would still need contract, runner, and a validation cohort. |
| 6. New external objects | A future validation cohort is required for any stronger claim and is not present as a ready set. |
| 7. Outcome-adaptive selection risk | High and inherent. The redesign is after seeing 0/140. INV/MONO have a pre-outcome schema-kind gap, but CONV/DYN/CMP also closed 0/140 under predicates that do not require those kinds. Changing CONV/DYN/CMP after that outcome is adaptive. |
| 8. Second and third project | No. Same cohort still lacks contract, invocation, oracle, and runner. |
| 9. What C3 still lacks even if successful | Confirmatory status, validation cohort, paired execution, overlap, and project-clustered uncertainty. Exploratory `SITE_FROZEN` counts are not C3. |
| 10. Earliest stop | No independent semantic rationale that also covers invocation and oracle; or the new authority is only a loosened predicate. |
| 11. Scientific value if it fails | A disclosed exploratory negative, if old 140 remain untouched. Not confirmatory C3. |
| 12. Design/governance-without-data risk | High. Another applicability protocol on the same C/Fortran/C++ frames would repeat Stage I's engineering shape. |

### 3.3 Path C: CLAIM_SCOPE_REDUCTION

Stop seeking confirmatory multi-project support for the current C3. Position existing results as: an ordinal-8 single-project paired pilot; a Stage I 14-subject applicability census; 0/140 under the frozen authority; and keep cross-project construct-distinctness `blocked` or remove it from the paper's main contributions. Do not rewrite missing evidence as support.

Three later actions remain distinct and are not performed here:

- shrink the paper claim;
- change claim-ledger status;
- delete a research question.

This task only selects the direction.

| Question | Answer |
|---|---|
| 1. Next new observation | None experimental. The next scientific product is a designed claim-scope and ledger-amendment freeze that uses the already written observations. |
| 2. What it can change | Manuscript claim scope, and later a proposed ledger wording. It does not add a C3 evidence component. |
| 3. Frozen inputs now | Ordinal-8 paired handoff; Stage I terminal and 140 closures; Stage I disclosure; claim ledger v1.3.0; core-claims authority. |
| 4. Production seams now | Not required. The path consumes completed observations. |
| 5. Independent stages to first scientific product | 1: `P3_C3_CLAIM_SCOPE_AND_LEDGER_AMENDMENT_DESIGN`. |
| 6. New external objects | No. |
| 7. Outcome-adaptive selection risk | Low. No new subject, site, or predicate is selected. |
| 8. Second and third project | No. The path stops seeking them on the current confirmatory C3 route. |
| 9. What C3 still lacks | The original upgrade condition. C3 stays `blocked`, or the cross-project claim leaves the main contribution list. RQ2 is not deleted by this choice. |
| 10. Earliest stop | The amendment design records the reduced scope and the three-way distinction (paper claim / ledger status / RQ deletion). No new experiment is opened. |
| 11. Scientific value if the later amendment is rejected | The Stage I empty-candidate fact and the ordinal-8 pilot remain. The current Stage II path stays closed. |
| 12. Design/governance-without-data risk | Low. The path refuses another protocol round that cannot yet produce paired data. |

## 4. Input / seam availability

Mechanical checks used existing JSON identities, PBF `public_schemas[].schema_kind` counts, archive filenames, and production-function return/raise behavior. Successor source, path, symbol, and span were not read. Predicates were not rerun. P12 reveal, patch, and mutation outcomes were not read.

### 4.1 P3 35-subject frozen cohort

- Bridge: `data/p3_v3/p12_intake/verified_bridge.json`, `eligible_item_count = 35`.
- Distinct repositories: 19. NumPy subjects: 1. Non-NumPy subjects: 34.
- `eligible_for_construct=true` is bridge admission. It does not mean Package A applicability, first-applicable site existence, or C3 evidence.
- V2 successor table: ordinals 1–22. Stage I used 9–22. Ordinals 1–7 are already documented 10/10 `APPLICABILITY_CLOSED_NOT_APPLICABLE`. Ordinal 8 is the NumPy paired pilot.

### 4.2 PBF / schema / interface evidence

| Scope | `public_schemas` kinds |
|---|---|
| Full 35 | `CLI_TOKEN_GRAMMAR_V1` 471; `JSON_SCHEMA_DRAFT2020_12_V1` 973; `TEXT_IO_SCHEMA_V1` 5; `NUMERIC_ARRAY_DOMAIN_V1` 1 |
| Non-NumPy 34 | `CLI_TOKEN_GRAMMAR_V1` 470 only |
| Stage I 14 | `CLI_TOKEN_GRAMMAR_V1` 434 only |

The only subject with `JSON_SCHEMA_DRAFT2020_12_V1` or `NUMERIC_ARRAY_DOMAIN_V1` is ordinal 8 NumPy. SciPy (3 subjects) and the 13 non-successor subjects have empty `public_schemas` or CLI-only kinds. No successor `public_schemas` kind matches a registered `CONTRACT_*` generator.

### 4.3 Recoverable source archives

`data/p3_v3/p12_intake/archives/` contains 14 tarballs. They match the Stage I 9–22 snapshots and their bridge `source_archive_sha256`. The other 21/35 subjects, including NumPy ordinal 8 and all SciPy/Julia/Python non-NumPy subjects, have no archive bytes in this worktree.

### 4.4 Contract, invocation, oracle, pair, runner

- Contract-generator registry exists: five `CONTRACT_*_DOMAIN_V1` generators.
- `freeze_production_contracts()` returns `()` for every successor and forbids ordinal 8.
- `construct_production_pairs()` and `execute_production_pairs()` raise on nonempty successor input.
- CMake/Autotools adapters are PBF discovery adapters, not contract, oracle, or paired-execution adapters.
- The only documented production oracles and controlled runner belong to the ordinal-8 NumPy path.

### 4.5 P12 as external input

P12 checkouts are readable (`/tmp/p12-current-main-authority` and siblings). Allowed design/plan counts: 64 curated candidates; 35 `verified_full`; paper label of 18 libraries. Those totals are not executable-interface readiness.

P12 producer plans forbid computing `P12_PAIRED` on the producer side. No allowed design file lists interface-ready, contract-ready, or runner-ready objects for P3. The v2.0.0 consumer protocol is adopted but not binding until its §11 freeze. The P12 claim ledger still records W4 as undelivered. P12 expansion tiers (FFTW, CuPy, SuiteSparse, and others) are design targets, not admitted P3 objects.

### 4.6 Executable-interface readiness

To obtain a second and a third project observation, admission needs at least two distinct non-NumPy projects, each satisfying all of:

1. unique recoverable source identity;
2. executable or statically checkable public interface;
3. PBF able to publish schema/interface evidence required for source-authorized contracts;
4. prior applicability rule;
5. prior contract generator, invocation, and oracle authority;
6. prior semantic/syntactic pair-construction seam;
7. controlled runner.

Current count of non-NumPy projects that satisfy the full list: **0**.
Current count of runner-ready projects of any kind: **1** (NumPy ordinal 8), which cannot fill the two-project non-NumPy requirement.
`18 programs / 35 defects` is not a substitute for that count.

## 5. Lexicographic decision

Rules applied in order. No subjective score.

| Rule | A | B | C | Survivor |
|---|---|---|---|---|
| 1. Legal without rerunning old observation or post-hoc site pick | Can be legal if admission is frozen first and 9–22 are not rerun | Legal only as disclosed exploratory redesign; confirmatory reuse is illegal | Legal; consumes completed observations | A, B, C |
| 2. Next product can change a C3 evidence component or manuscript scope | Could change C3 evidence only after missing objects exist | Can change exploratory eligibility, not confirmatory C3 | Changes manuscript scope now | A, B, C |
| 3. Fewest independent stages to the first new scientific product | 9, and stages 2/6/7/8 have no current objects | 5 to an exploratory census; still no paired project | 1 amendment-design stage; no new experiment | **C** |
| 4. Most current frozen inputs and production seams | Uses identities/PBFs but lacks archives and paired seams for new objects | Uses 9–22 archives and old 140; still no paired seams | Uses ordinal-8 paired evidence, Stage I terminal, disclosure, and ledger | C remains |
| 5. Lowest outcome-adaptive risk | Material | High | Low | C remains |
| 6. Can form a second and third project | Not with current objects | No | No, by choice | already decided |
| 7. Engineering serves data rather than governance | No: would start a new protocol stack | No: another authority round on the same empty-candidate cohort | Yes: stops protocol substitution | C remains |

Expected-tendency check, not used as a weight:

- At least two interface-ready, runner-ready non-NumPy projects: **no**. NEW_COHORT is not preferred.
- Same-cohort new authority with independent semantic basis and a ready validation cohort: partial rationale exists for INV/MONO schema kinds, but CONV/DYN/CMP already failed without those kinds, and no validation cohort is ready. NEW_AUTHORITY is not selected.
- A and B both need multiple new protocol rounds and missing inputs: **yes**. CLAIM_SCOPE_REDUCTION is preferred.

The original C3 multi-project target is not a reason to keep A or B.

## 6. Selected unique path

`CLAIM_SCOPE_REDUCTION`

Reason: after Stage I emptied the Stage II candidate universe, the current confirmatory two-stage path cannot produce a second paired project. The 35-subject pool and P12 design counts do not contain two non-NumPy objects that already have contract-authority schema evidence, invocation, oracle, pair construction, and a controlled runner. Opening a new cohort or a same-cohort authority would start another design/governance sequence whose first experimental observation is several independent stages away. The existing observations are enough to freeze a reduced claim scope.

## 7. Exact next observation

No new experimental observation is authorized.

The unique next scientific product is a designed, frozen statement of:

- ordinal-8 single-project paired pilot;
- Stage I 14-subject applicability census;
- 0/140 under the frozen PBF, inventory, predicates, and first-applicable boundary;
- cross-project construct-distinctness remaining `blocked` or removed from main contributions;
- missing evidence not rewritten as support.

That product is created by the mapped next task, not by this file.

## 8. Evidence ceiling

| Item | Ceiling after this decision |
|---|---|
| Current Stage II | closed; candidate count remains 0 |
| Current version rerun / predicate edit | forbidden |
| C3 confirmatory multi-project support | not sought on this path |
| C3 status in this task | still `blocked`; ledger not edited |
| `n_projects` | still 1 |
| Stage I 0/140 | qualified census, not an industrial rate, not construct absence |
| Ordinal-8 pairs | local paired pilot only |
| Abstract / Contributions / Conclusion | still forbidden as a general negative finding until the amendment design says otherwise |
| New cohort or new authority | not opened by this decision |

## 9. Stop conditions

1. Do not start Stage I or Stage II.
2. Do not reopen ordinals 9–22 in this version.
3. Do not relax predicates, change site policy, or rerun to "repair" 0/140.
4. Do not treat P12 18-library / 35-defect counts as admission.
5. Do not start a second reprioritization.
6. The next task may design paper-claim reduction, a later ledger-status proposal, or an explicit non-deletion of RQ2. It may not run a new experiment.
7. A future independent prospective version, if ever wanted, is a new research question with new authority. It is not a continuation of this empty-candidate Stage II.

## 10. Claim / ledger implications

This task does not edit the ledger or the manuscript.

| Action | Selected now? | Meaning |
|---|---|---|
| Shrink the paper claim | Direction selected | Stop presenting current C3 as a multi-project confirmatory result. Use ordinal-8 pilot plus Stage I census with frozen boundaries. |
| Change claim-ledger status | Not performed | Ledger remains `blocked` with the same upgrade condition until a later amendment design proposes a wording. `blocked` is not flipped to supported. |
| Delete a research question | Not selected | RQ2 remains. The missing cross-project evidence is not converted into a deleted question and not converted into a positive finding. |

C3's upgrade condition, `RQ2 paired evidence and uncertainty accounting complete`, remains unmet. Path C records that the current program will not try to meet it by building another successor Stage II.

## 11. Unique next task

`P3_C3_CLAIM_SCOPE_AND_LEDGER_AMENDMENT_DESIGN`

That task designs paper/ledger contraction only. It does not run a new experiment. This file does not start it.

Mapped terminals not used:

- `NEXT_PATH_NEW_COHORT` → `P3_C3_INTERFACE_READY_NEW_COHORT_ADMISSION_DESIGN`
- `NEXT_PATH_NEW_AUTHORITY_EXPLORATORY` → `P3_C3_DISCLOSED_EXPLORATORY_AUTHORITY_DESIGN`
- `NO_DEFENSIBLE_CONTINUATION` → `P3_EMPIRICAL_PROGRAM_STOP_AND_PAPER_HANDOFF`

## 12. Milestone deviation check

| Check | Result |
|---|---|
| Current deviation grade | 未偏离 |
| Continue substituting engineering for data | 否。选择收缩 claim，而不是再开 cohort 或 authority 协议。 |
| Can the selected path produce a new observation inside an explicit stop | 该路径不以新实验 observation 为目标。它在一阶段设计内把已有 observation 冻成缩小后的论文/ledger 范围，并在该设计完成后停止。 |
