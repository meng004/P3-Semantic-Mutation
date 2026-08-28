在一个受控 NumPy subject 的四个冻结 semantic–syntactic pairs 上，semantic mutants 为 4/4 KILL，syntactic baselines 为 3/4 KILL；唯一 discordant pair 的方向是 semantic-only kill。该结果是局部、有效的 paired execution evidence，但单一 project 无法支持冻结规格要求的 project-clustered uncertainty，因此 C3 仍为 blocked。

## Observed results

- subject / project / sites / pairs / valid cells: n_subjects = 1, n_projects = 1, n_sites = 2, n_pairs = 4, 60 valid PASS cells.
- original baseline: 20/20 SURVIVE.
- semantic: pair-level 4/4 KILL; cell-level 20/20 KILL.
- syntactic: pair-level 3/4 KILL; cell-level 15/20 KILL.
- `INV/TF` site `f37fc591…`, slot `a2f7a216…`: original 5/5 SURVIVE; semantic 5/5 KILL; syntactic 5/5 KILL (both_killed).
- `INV/SI` site `f37fc591…`, slot `e8fd94d6…`: original 5/5 SURVIVE; semantic 5/5 KILL; syntactic 0/5 SURVIVE (semantic_only).
- `CMP/TF` site `c7ca9add…`, slot `e0b42ce7…`: original 5/5 SURVIVE; semantic 5/5 KILL; syntactic 5/5 KILL (both_killed).
- `CMP/SI` site `c7ca9add…`, slot `06556e4b…`: original 5/5 SURVIVE; semantic 5/5 KILL; syntactic 5/5 KILL (both_killed).

## Execution funnel including prior infrastructure failure

- Historical INV/TF attempt: 15/15 `FAIL_INFRASTRUCTURE` (`numpy.array_api` import failure). Kill/survival was not observed. That record remains provenance and is excluded from kill/survival estimates.
- Qualification of the controlled NumPy `2.0.0.dev0` runtime is identity and provenance only; it is not a scientific kill observation and was not rerun.
- Clean replay then produced 15 valid INV/TF cells. Remaining-three batch produced 45 valid cells. Combined valid evidence is 60 cells, all PASS.
- Clean replay is a disclosed new controlled run after the infrastructure failure. It does not delete or replace that failure.

## Paired comparison

- both killed: 3
- semantic only: 1
- syntactic only: 0
- neither: 0
- tied pairs: 3
- 在该单一受控 subject 的四个冻结 paired mutants 中，semantic mutant 的观察 kill 比例比 syntactic baseline 高 25 个百分点。
- This 0.25 figure is not a population effect, mean improvement, significant advantage, or general superiority.
- Primary descriptive unit is the frozen pair (4), not the 20 input cells and not the 60 valid cells.

## Contract-category coverage

- represented families: CMP, INV
- represented mechanisms: SI, TF
- successful frozen pairs: 4
- MONO: SITE_FROZEN but no contract; not a KILL failure and not construct absence.
- CONV and DYN: no SITE_FROZEN (`APPLICABILITY_CLOSED_NOT_APPLICABLE`).
- Unrepresented families are not written as kill failures.

## Uncertainty accounting

- project_cluster_count = 1
- project_clustered_bootstrap_status = UNIDENTIFIABLE
- A single project cannot identify cross-project sampling uncertainty. Cell, pair, or site bootstrap is not a substitute for the frozen project-clustered bootstrap.
- normalized-patch exact overlap: `UNMEASURED_MISSING_FROZEN_INPUT`
- mutant-tree exact overlap: `UNMEASURED_MISSING_FROZEN_INPUT`
- exact binomial: `UNMEASURED`; RQ2 exact binomial intervals attach to independent normalized-patch and mutant-tree exact-overlap trials. Those fields are absent from the frozen execution records and are not inferred from patch text.
- No McNemar, Fisher, Wald, Wilson, Bayesian posterior, cell bootstrap, pair bootstrap, or site bootstrap was computed.

## RQ2 coverage gaps

- `paired semantic/syntactic execution observations`: `OBSERVED`
- `complete execution funnel`: `OBSERVED`
- `normalized-patch exact overlap`: `UNMEASURED`
- `mutant-tree exact overlap`: `UNMEASURED`
- `exact binomial uncertainty`: `UNMEASURED`
- `contract-category coverage`: `OBSERVED`
- `paired subject-level difference`: `OBSERVED`
- `project-clustered bootstrap interval`: `UNIDENTIFIABLE`
- `multi-subject coverage`: `UNIDENTIFIABLE`
- `multi-project coverage`: `UNIDENTIFIABLE`

The observed local paired executions do not complete RQ2 uncertainty accounting. C3 therefore remains blocked.

## Allowed and blocked claims

Allowed observed statements:
- On this NumPy ordinal-8 subject, two frozen sites, four frozen pairs, and five frozen inputs per pair, all four semantic mutants were killed.
- Three syntactic baselines were killed and one survived.
- The only discordant pair is semantic KILL / syntactic SURVIVE.
- The original baseline survived on all 20 valid inputs.
- The clean controlled runtime removed the prior numpy.array_api infrastructure block.
- The present results are local paired execution evidence.

Blocked statements:
- semantic mutants are generally superior to syntactic mutants
- semantic mutation is construct-distinct as a completed C3 result
- a NumPy or Python population effect
- effects outside INV and CMP
- cross-subject, cross-repository, or cross-project inference
- C3 upgrade_condition is satisfied
- the 20 valid input cells are 20 independent experimental units
- the 3/4 versus 4/4 contrast is statistically significant

Limits:
- n_subjects = 1
- n_projects = 1
- n_sites = 2
- n_pairs = 4
- project-clustered uncertainty is unidentifiable
- family coverage is INV and CMP only
- this is a local result from the first eligible subject after prospective-v2 eligibility search
- the first infrastructure failure is retained; clean replay is a disclosed new controlled run, not a deletion of that failure

## Methodology audit

- **Simpson’s paradox**: RISK_ADDRESSED: primary unit is the frozen pair, not a site-pooled cell rate; both sites are disclosed.
- **ecological fallacy**: RISK_ADDRESSED: pair-level 0.25 is not transported to mutants, inputs, subjects, or projects.
- **Berkson’s paradox**: NOT_APPLICABLE: inclusion is eligibility-frozen, not conditioning on both arms being killed.
- **collider bias**: RISK: first eligible completed subject after prospective search; disclosed, not treated as a random project draw.
- **base-rate neglect**: NOT_APPLICABLE: no prevalence claim; original 20/20 SURVIVE is the local oracle base, not a population rate.
- **regression to the mean**: NO_EVIDENCE: each pair has one frozen scientific execution; clean replay followed unobserved infrastructure failure, not a prior kill.
- **survivorship bias**: RISK_ADDRESSED: CONV/DYN closed-not-applicable and MONO-without-contract remain in the funnel and are not coded as KILL failures.
- **look-elsewhere effect**: RISK_ADDRESSED: contrasts are the four frozen pairs and the frozen RQ2 list; no post-hoc family or statistic shopping.
- **garden of forking paths**: RISK_ADDRESSED: no McNemar, Fisher, Wald, Wilson, Bayesian, or substitute bootstrap was added after seeing the 3/4 versus 4/4 split.
- **correlation/causation confusion**: RISK_ADDRESSED: paired executions are not a causal proof that semantic operators produce kills.
- **reverse causality**: NOT_APPLICABLE: mutants and inputs were frozen before valid kill/survival observation; remaining-three designs were not rewritten from INV/TF outcomes.
- **pseudo_replication**: RISK_ADDRESSED: 20 input cells and 60 valid cells are repeated measures inside four pairs, not 20 or 60 independent experiments.
- **single_project_extrapolation**: RISK_ADDRESSED: project-clustered bootstrap is UNIDENTIFIABLE; no transport.
- **outcome_disclosed_clean_replay**: RISK_ADDRESSED: the 15-cell infrastructure failure remains in the funnel; clean replay is a new controlled run after that disclosure.

## Next scientific gap

The next scientific gap is project-clustered uncertainty accounting and the missing frozen overlap measurements, not another mutant, input, or rerun on this subject. This handoff does not start that task. `FORMAL_V2_RUN_RETRY_FORBIDDEN=true` remains in force.
