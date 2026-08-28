# P3 C3 Stage I applicability census: scientific disclosure and Stage II path closure

Task: `P3_C3_STAGE1_CENSUS_DISCLOSURE_AND_STAGE2_PATH_CLOSURE`
Model / reasoning: `gpt-5.6-sol` / high
Mode: formal observation verification, disclosure, and path closure. No new experiment, no Stage II implementation, no claim-ledger edit.
Terminal status after this disclosure: `STAGE1_DISCLOSED_STAGE2_CANDIDATE_UNIVERSE_EMPTY`

The official Stage I terminal remains the unique machine-readable evidence. This file is the unique human-readable disclosure of that already-written observation.

## 1. Evidence identity

Worktree: `/tmp/p3-c3-ordinal9-22-source-recovery`
Branch: `cursor/content-addressed-source-join-b65d`

| Object | Value |
|---|---|
| Observation HEAD at disclosure start | `c64fa70840e10f7a4729047bd407ea1ea68f8fd7` |
| Parent / Stage I authorization activation | `8f4e431f423dcb63abcbe5310fad4b89996e736b` |
| Remote branch at disclosure start | `origin/cursor/content-addressed-source-join-b65d` = `c64fa70840e10f7a4729047bd407ea1ea68f8fd7` |
| Implementation commit bound by authorization | `ee12a75b6dbd3905dcc6acc967beb638ddcc4410` |
| Design commit (`design_commit` in terminal) | `270025608be7db631484b77ffda181438100d785` |
| Stage I slice | `p3-c3-prospective-multiproject-applicability-stage1-v2` |
| Official root | `data/p3_v3/phase3/prospective-multiproject-applicability-stage1-v2/` (regular directory, not a symlink) |
| Staging sibling | absent (`…-stage1-v2.staging` does not exist) |
| Terminal file | `data/p3_v3/phase3/prospective-multiproject-applicability-stage1-v2/cohort-terminal.json` |
| Terminal `terminal_status` | `STAGE1_APPLICABILITY_CENSUS_COMPLETE` |
| Terminal artifact SHA-256 | `45757bb594d582b380ee7955f0caeab92adfd3c10702c31cf788f896a6595a97` |
| Terminal file SHA-256 | `f2e9af90ed31bd118a80808a04e3af66c5abee539f0093c6087c176e2bee51ab` |
| Controller SHA-256 | `5ab44c9840f44468c556a94b93a7a294858549688c11ca282e660adb5f71c341` |
| Design file SHA-256 | `a8828022ee2095b4209261c26d0ecbab66141e59b2c9f18ce3df2045f6dd79c5` |
| Applicability-authority artifact SHA-256 | `30b08271eafdead14a06707b461f108c1ec5a53eb5d2859a37b2cd6238e20214` |
| Slot-inventory artifact SHA-256 | `5c7f2dae8b0b7fd72926e2569354dbf6e878186f69d512e259e6034026dd0e27` |
| Project-cluster authority artifact SHA-256 | `802ec9a8db866c1c1d79b29e03d4e5dc0f55d4961a3f415a2486dd562fbf810e` |
| Claim ledger SHA-256 (unchanged) | `bf4979662697b2d0565bb70eec88b22673e84bee93b61234555342efb4082a68` |
| Authorization path | `data/p3_v3/phase3/inputs/user-auth-prospective-multiproject-applicability-stage1-v2.txt` |
| Authorization file | regular file, not a symlink; 287 bytes |
| Authorization SHA-256 | `cde781bbe0bd25514b117c55563ac2b88720574da274bf98d3f3f0a56308d60d` |

Identity checks that passed before reconstruction:

1. HEAD, parent, and remote matched the frozen values above; porcelain was empty.
2. Official root contained exactly 140 `p3-slot-closure-v1` files and one `cohort-terminal.json`.
3. Old Slice B official/staging namespaces did not exist.
4. Stage II official/staging namespaces did not exist.
5. Controller, design, authority, inventory, and project-cluster identities rebound to the terminal.

If any of those checks had failed, this task would have stopped as `EVIDENCE_IDENTITY_CONFLICT`. They did not fail.

## 2. Prespecified Stage I question

The frozen design asks exactly one Stage I question:

Under the frozen applicability authority, frozen source identities, and frozen ordinal 9–22 universe, which of each subject's ten slots close as `SITE_FROZEN`, and which close as `APPLICABILITY_CLOSED_NOT_APPLICABLE`?

Stage I does not answer contract existence, pair constructibility, `KILL` / `SURVIVE`, construct distinctness, testing value, or C3 upgrade.

## 3. Observed totals

Read-only reconstruction used `validate_stage1_terminal()`, `read_canonical_json()`, `inventory_slot_ids_for_subject()`, `sort_stage1_inventory_rows()`, `rebuild_stage1_counts()`, and `canonical_sha256` / `file_sha256`. It did not call source recovery, site selection, predicates, contract, mutant, or runner code.

Reconstruction result:

- `validate_stage1_terminal()` returned `valid=True`, `terminal_status=STAGE1_APPLICABILITY_CENSUS_COMPLETE`, `subject_count=14`, `closure_count=140`, and the terminal artifact SHA above.
- Terminal self-hash matched `artifact_sha256`.
- Ordinals were exactly 9→22.
- Subjects were exactly 14.
- Each subject had exactly 10 closures.
- Closures totaled exactly 140.
- Closure slot identity and order matched the frozen inventory.
- Every closure `state` was `APPLICABILITY_CLOSED_NOT_APPLICABLE`.
- Every closure `site_id` was `null`.
- Rebuilt `site_frozen_count` sum = 0.
- Rebuilt `not_applicable_count` sum = 140.

Observed totals used at the required strength:

- 冻结 ordinal 9–22 successor universe 的 14/14 主体已完成 Stage I。
- 140/140 slots 获得正式 terminal。
- 0 个 `SITE_FROZEN`。
- 140 个 `APPLICABILITY_CLOSED_NOT_APPLICABLE`。
- 按批准设计的机械规则，Stage II candidate universe 为空。

These 140 closures are one census. They are not 140 independent statistical samples.

## 4. Per-subject, repository, family, and mechanism summaries

The following tables regroup the same 140-slot census. They are descriptive partitions, not independent samples and not prevalence estimates.

### 4.1 Per-subject (14 rows)

| Ordinal | `controlled_subject_id` | `project_cluster_key` | SITE_FROZEN | NOT_APPLICABLE |
|---|---|---|---:|---:|
| 9 | `6e71e0c72a29aa77a6c83ea81d39af7801b6a6bad3dd053a6ec7eb6df4bbd6db` | `github.com/llnl/sundials` | 0 | 10 |
| 10 | `d81ff7e27069d30df42111cedb08598012076173d94e5f84dfeb1ee2a124e2c8` | `github.com/llnl/sundials` | 0 | 10 |
| 11 | `35d537a7639d6bd8966abb2a21f453dbc7d648876ab449d264c9a4690748af20` | `github.com/llnl/sundials` | 0 | 10 |
| 12 | `43a6370a0fe446cfc2895e283a19c01fed0c94dd2da5f69f14b3ec64ed32bad2` | `github.com/llnl/sundials` | 0 | 10 |
| 13 | `38b6c8236a5717b3ad99240879cc97221b1a58ad6ccb02e74a0747c4c725c780` | `github.com/llnl/sundials` | 0 | 10 |
| 14 | `7ead91b227c321fd6430a9f9c7f10cf888de0c98848d0b1d9cd05d04896843a5` | `github.com/llnl/sundials` | 0 | 10 |
| 15 | `25ad02f3b77e0e325385ce63bf0f49dc1aff6081a7b2373f1fcae68c8119a202` | `github.com/reference-lapack/lapack` | 0 | 10 |
| 16 | `072ad35799114749ca393fa74b3defe9e60c76560450bd9ffa6b6bedbcf83805` | `github.com/reference-lapack/lapack` | 0 | 10 |
| 17 | `7e1c0f1a4a5d83730c57088a70763fdaeb452aff00e28a51fa08772157ac0632` | `github.com/reference-lapack/lapack` | 0 | 10 |
| 18 | `821b57e8a17272636dd08d4a6a96cda3965a221ced4fcc225c613648668a28b6` | `gitlab.com/petsc/petsc` | 0 | 10 |
| 19 | `f5cea2872cbcb90333f087a87f3fe50cfbd1bf79c2de420e6bacec0a1d442b08` | `gitlab.com/petsc/petsc` | 0 | 10 |
| 20 | `2fc0e80d3659a765ee931208918d9da1f83cab746476f8463a138d90e4aee455` | `github.com/drtimothyaldendavis/graphblas` | 0 | 10 |
| 21 | `0f6ed8e3d9d1107fe96b7f8b2686eaace9dec1cf78235f380d36b3912145ffc2` | `github.com/openmathlib/openblas` | 0 | 10 |
| 22 | `5b811ed080bcce73b009712b8038eaf21f66de1fc397275e0019b6a93c6e0379` | `github.com/trilinos/trilinos` | 0 | 10 |
| **Total** | 14 subjects | 6 clusters | **0** | **140** |

### 4.2 Per-repository cluster

| `project_cluster_key` | Subjects | Ordinals | SITE_FROZEN | NOT_APPLICABLE |
|---|---:|---|---:|---:|
| `github.com/llnl/sundials` | 6 | 9–14 | 0 | 60 |
| `github.com/reference-lapack/lapack` | 3 | 15–17 | 0 | 30 |
| `gitlab.com/petsc/petsc` | 2 | 18–19 | 0 | 20 |
| `github.com/drtimothyaldendavis/graphblas` | 1 | 20 | 0 | 10 |
| `github.com/openmathlib/openblas` | 1 | 21 | 0 | 10 |
| `github.com/trilinos/trilinos` | 1 | 22 | 0 | 10 |
| **Total** | **14** | 9–22 | **0** | **140** |

### 4.3 Per-family

Each family has two inventory slots per subject, so 14 × 2 = 28 closures.

| Family | Slots | SITE_FROZEN | NOT_APPLICABLE |
|---|---:|---:|---:|
| INV | 28 | 0 | 28 |
| MONO | 28 | 0 | 28 |
| CONV | 28 | 0 | 28 |
| DYN | 28 | 0 | 28 |
| CMP | 28 | 0 | 28 |
| **Total** | **140** | **0** | **140** |

### 4.4 Per-mechanism

Mechanism counts follow the frozen inventory assignment on these 14 subjects. They are not a balanced 28-per-mechanism design.

| Mechanism | Slots | SITE_FROZEN | NOT_APPLICABLE |
|---|---:|---:|---:|
| CE | 30 | 0 | 30 |
| OS | 25 | 0 | 25 |
| HP | 25 | 0 | 25 |
| TF | 25 | 0 | 25 |
| SI | 35 | 0 | 35 |
| **Total** | **140** | **0** | **140** |

### 4.5 Family × mechanism

Each cell is a count of the same 140 closures after joining closure `slot_id` to the frozen inventory. Empty cells do not occur in this 14-subject subset: every family appears with every mechanism.

| Family × mechanism | Slots | SITE_FROZEN | NOT_APPLICABLE |
|---|---:|---:|---:|
| INV × CE | 6 | 0 | 6 |
| INV × OS | 5 | 0 | 5 |
| INV × HP | 5 | 0 | 5 |
| INV × TF | 5 | 0 | 5 |
| INV × SI | 7 | 0 | 7 |
| MONO × CE | 6 | 0 | 6 |
| MONO × OS | 5 | 0 | 5 |
| MONO × HP | 5 | 0 | 5 |
| MONO × TF | 5 | 0 | 5 |
| MONO × SI | 7 | 0 | 7 |
| CONV × CE | 6 | 0 | 6 |
| CONV × OS | 5 | 0 | 5 |
| CONV × HP | 5 | 0 | 5 |
| CONV × TF | 5 | 0 | 5 |
| CONV × SI | 7 | 0 | 7 |
| DYN × CE | 6 | 0 | 6 |
| DYN × OS | 5 | 0 | 5 |
| DYN × HP | 5 | 0 | 5 |
| DYN × TF | 5 | 0 | 5 |
| DYN × SI | 7 | 0 | 7 |
| CMP × CE | 6 | 0 | 6 |
| CMP × OS | 5 | 0 | 5 |
| CMP × HP | 5 | 0 | 5 |
| CMP × TF | 5 | 0 | 5 |
| CMP × SI | 7 | 0 | 7 |
| **Total** | **140** | **0** | **140** |

## 5. Stage II candidate reconstruction

Approved mechanical rule, from the frozen design §9:

1. Read the Stage I success terminal.
2. Rebuild every closure from `closure_artifact_sha256s`.
3. Keep a subject if and only if `site_frozen_count >= 1` and the rebuilt closures confirm at least one `SITE_FROZEN` state.
4. Drop every subject whose ten closures are `APPLICABILITY_CLOSED_NOT_APPLICABLE`.
5. Keep remaining subjects in the original ordinal 9–22 order.
6. Exclude ordinal 8.
7. Add no extra-table subject.

Reconstruction:

- subjects with `site_frozen_count >= 1`: 0
- subjects dropped as 10/10 `APPLICABILITY_CLOSED_NOT_APPLICABLE`: 14
- Stage II candidate count: **0**
- candidate ordinal list: empty

The Stage II candidate universe is therefore the empty set. This disclosure does not write a Stage II terminal. In particular it does not write `STAGE2_CANDIDATE_UNIVERSE_EXHAUSTED`; that code would belong only to an authorized Stage II that this path now must not start.

## 6. Claim-status table

| Status | Statement |
|---|---|
| observed | 冻结 ordinal 9–22 successor universe 的 14/14 主体已完成 Stage I。 |
| observed | 140/140 slots 获得正式 terminal。 |
| observed | 0 个 `SITE_FROZEN`。 |
| observed | 140 个 `APPLICABILITY_CLOSED_NOT_APPLICABLE`。 |
| observed | 按批准设计的机械规则，Stage II candidate universe 为空。 |
| qualified | 在冻结 PBF、slot inventory、applicability predicates 和 first-applicable selection boundary 下，这 14 个 successor 没有 site 满足预注册 applicability 条件。 |
| qualified | 因 candidate universe 为空，已批准的 Stage II 不能产生新的 `PAIRED_EVIDENCE_COMPLETE` project。 |
| qualified | 当前两阶段 prospective C3 路径在 Stage I 后合法关闭。 |
| blocked | C3 remains `blocked`. `n_projects` remains 1 (ordinal 8 only). Stage I added no paired project. RQ2 paired evidence and uncertainty accounting remain incomplete. |
| blocked | The approved Stage II of this version must not start. Ordinals 9–22 must not be re-enrolled in the same version. |
| speculative | None. This disclosure advances no speculative claim about construct presence, industrial applicability, predicate correctness, or C3 truth value. |

## 7. Limitations

The observation is bound to the frozen Public Behavior Frame, the frozen 10-slot inventory, the frozen applicability predicates, and the frozen first-applicable selection boundary. Changing any of those objects would define a different question.

The universe is the 14 frozen successors at ordinals 9–22. The result does not estimate an industrial-population applicability rate and does not transport to repositories, languages, or subjects outside this table.

Family, mechanism, and repository counts partition one 140-slot census. They are not independent trials and are not a family-level or mechanism-level hypothesis test.

Stage I did not inspect contract authority, pair construction, kill/survival, or overlap. Absence of `SITE_FROZEN` is not a paired-evidence result.

Stage I data may enter Limitations, Methods/Flow, or pilot Results, and only with these frozen boundaries stated. It must not enter Abstract, Contributions, or Conclusion as a general negative finding.

## 8. Stage II path closure

Recorded closure of the current two-stage prospective C3 path:

1. Stage II candidate derivation result is 0.
2. Stage II must not start.
3. This task creates no Stage II controller, authority, contract, mutant, or runner.
4. Ordinals 9–22 must not be placed again into the same version.
5. Stage I must not be rerun after adjusting predicates.
6. Old Slice B remains closed and unused.
7. A new cohort, authority, or research question must belong to a future independent prospective version.
8. This task does not choose that future version.

## 9. C3 and ledger status

| Item | Status after this disclosure |
|---|---|
| `C3_SEMANTIC_CONSTRUCT_DISTINCTNESS` | `blocked` |
| C3 `upgrade_condition` | still `RQ2 paired evidence and uncertainty accounting complete` |
| `n_projects` | 1 (ordinal 8 only) |
| New paired projects from Stage I | 0 |
| RQ2 paired evidence and uncertainty accounting | incomplete |
| Claim ledger path | `research/evidence/p3_claim_ledger_v1.3.0.yml` |
| Claim ledger SHA-256 | `bf4979662697b2d0565bb70eec88b22673e84bee93b61234555342efb4082a68` |
| Ledger edited by this task | no |

## 10. Prohibited interpretations

The following readings are forbidden and are not licensed by this census:

- 这些程序没有目标语义构造。
- SUNDIALS / LAPACK / PETSc / GraphBLAS / OpenBLAS / Trilinos 不适合 semantic mutation。
- 这些项目没有可变异 site。
- applicability predicates 错误或失败。
- PBF 缺陷导致结果。
- C3 被证伪。
- 0/140 是工业总体适用率。
- 140 slots 是 140 个独立统计样本。
- 应通过放宽 predicate、改 site policy 或重跑来修复结果。

Zero `SITE_FROZEN` is the Stage I answer to the prespecified applicability question under the frozen boundary. It is not a repair signal.

## 11. Unique next scientific decision task

`P3_CLAIM_PATH_REPRIORITIZATION_AFTER_STAGE1_EMPTY_CANDIDATES`

That next task must choose among a new cohort, a new authority, or a contracted claim. It must not continue the current Stage II. This disclosure does not start that task and does not select among those options.

## 12. Milestone deviation check

| Check | Result |
|---|---|
| Deviation grade | 未偏离 |
| Produced substantive scientific data | 是 |
| Changed cohort eligibility | 是；Stage II candidates = 0 |
| Rerun or post-hoc rule change allowed | 否 |

This disclosure changes the Stage II candidate universe from unknown to the empty set. The result is negative and substantive. The current two-stage C3 path closes after Stage I.
