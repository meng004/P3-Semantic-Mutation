# Boost.Math Formal Header Profiling RQ Evidence Handoff

- Date: 2026-08-27
- Mode: experiment validation / research evidence gate
- Origin: formal profiling receipt + read-only failure attribution
- Verification status: `ANALYZED`
- Reproducibility: `CANNOT_VERIFY` (formal run retry is forbidden)
- Evidence gate: `PASS_WITH_QUALIFIED_CLAIMS`
- Reviewed implementation commit: `99dbfab0cd703c478597e7d73806570a601a2e29`
- Machine-readable companion:
  `data/p3_v3/profiling_runs/boost_math/rq-evidence-handoff-74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886.json`
- Companion `artifact_sha256`: `4192f8f54bc9d24063d598e8bbae5289a974d68bc19424171eeb78e0a1c12415`
- Companion file SHA-256: `34b98800fc7e53aa815f1cf570532aa688b3a46181b36ae056097a65186a4064`

This handoff is the RQ consumer package for the completed Boost.Math formal
header-profiling run. It does not rerun profiling, does not rewrite the frozen
workload, and does not overwrite Phase-1 frames.

`FORMAL_PROFILING_RETRY_FORBIDDEN=true`

## 1. Material passport

| Field | Value |
|---|---|
| Subject snapshot | `74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886` |
| Controlled source id | `e5f21a7d067d641d0a20bfc57c61e630d6f7588ef30235cea49c9a9cf950c7a7` |
| Denominator | `PILOT_ONLY` |
| Formal-denominator membership | false |
| P3 claim-ledger upgrade | false |
| RQ4 supported | false |
| P3 paper-claim status | `blocked` |

The frozen P3 ledger
`research/evidence/p3_claim_ledger_v1.3.0.yml`
(file SHA-256 `bf4979662697b2d0565bb70eec88b22673e84bee93b61234555342efb4082a68`)
is unchanged. Subject-level profiling claims below are not an upgrade of that
ledger.

## 2. Identity chain

| Binding | Path or value | SHA-256 |
|---|---|---|
| Formal receipt file | `data/p3_v3/profiling_runs/boost_math/profiling-results-74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886.json` | `19f5f6b04ac23a5691c5e70e1af4948891c87100067801bc5f392d784e9828d9` |
| Formal receipt `artifact_sha256` | same file | `407958e8b429bc680567a133e007e4f967406d2e3e82e515b04359373a0c9385` |
| Formal runner source | `src/p3_v3/profiling_runner.py` | `08d8caa226e1fa2171739ef9a183b5695c0b41c0a605e6428f45936bd920105a` |
| CLI source | `scripts/p3_v3/profile.py` | `6bbbafaf0d0bced0712997ca8233d7050d741e43c628ece7ab90711bb579f099` |
| Frozen workload file | `data/p3_v3/phase1_frames/out/profiling-workload-74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886.json` | `e6cd3b5054bdac30dea8e6fbc613c29758be6a97ead4d6d134d33dfdfc8c8380` |
| Workload `artifact_sha256` | same file | `982375e1fedb6ff26aa25e39cb1d65e45ff14474d4d34fca634c95ef352b036e` |
| Normalized source tree | `/tmp/p3-boost-math-pilot-production-source` | `93a62859d7fdd6b2068e494bbe6e3e27180b874cbd27055ac27f941e507a90d8` |
| Build descriptor | existing binding | `68d2e0fd34b845bb0df22b29003f26259d5655d2ec80c18895ff36904db2d95d` |
| Design | `docs/superpowers/specs/2026-08-26-p3-boost-math-formal-header-profiling-design.md` | `0903d8fc00f8fe0a66466eca3f9b16b9a3a3aeab21076e673599cb7a90ea2998` |
| Phase-1 placeholder receipt file | `data/p3_v3/phase1_frames/out/profiling-results-74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886.json` | `5a1de4c1a9e52efcc100a448e018229abc984bc350a805c530133f7e689cc133` |
| Phase-1 placeholder `artifact_sha256` | same file | `3adcce7bcc5bda7925c6830be8fb7a55b276fc9ebe3b02f67451c04f3971d371` |
| Phase-1 technique profile file | `data/p3_v3/phase1_frames/out/technique-profile-74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886.json` | `da09281afcfb30d41f6f52823afbca9a994a543ae1ef8b82198b5aea58a5c91f` |
| Phase-1 technique profile `artifact_sha256` | same file | `a95549ebc5b8f52e316a800cecc5c138fbce49cadbdc0e68573615aab92a71bd` |

Runtime context of the completed run (not rebuilt):

- runtime root: `/tmp/p3-boost-math-formal-header-profiling-v1`
- source root: `/tmp/p3-boost-math-pilot-production-source`
- compiler: `/usr/bin/c++`
- compile boundary: `-std=c++14 -DBOOST_MATH_STANDALONE=1`

The formal receipt validator accepted the 20-row receipt. This handoff
reconstructs `classify_technique` from that receipt and the frozen workload. It
does not invoke the compiler.

## 3. Observed funnel and reconstructed classification

| Count | Status / code |
|---|---|
| 20/20 | frozen behaviors executed and retained |
| 8 | `MISSING_TRACE` / `NO_SUBJECT_CALL_TRACE` |
| 12 | `FAILURE` / `COMPILE_NONZERO_EXIT` |
| 0 | `SUCCESS`, `TIMEOUT` |
| 20/20 | unresolved |

Reconstructed classification from the formal receipt:

- `primary_technique = TECH_UNCERTAIN`
- `confirmed_tags = []`
- `lower_scores = {}`
- six-technique `upper_scores` all `"1"`
- `PUBLIC_API` funnel: `n_c=20`, `successful_count=0`, `unresolved_count=20`

This classification is identical to the Phase-1 placeholder classification. The
scientific change is provenance only:

- before: `PHASE1_PROFILING_NOT_EXECUTED`
- after: executed; 8 compile-exit-0 rows with no subject-level call trace;
  12 real nonzero compile exits

`TECH_UNCERTAIN` is therefore not an experimental failure. It is the correct
classifier output for a frozen workload that produced no confirmable dynamic
technique evidence.

## 4. Formal RQ statement

In the frozen Boost.Math header workload and the C++14 standalone compile
boundary, all 20 preselected behaviors received a formal execution terminal
state. Eight headers compiled successfully but produced no subject-level call
trace. The remaining 12 headers exited the compiler with a nonzero status. All
behaviors therefore remain unresolved. The classification is `TECH_UNCERTAIN`,
and there are no confirmed technique tags. This result shows that the
prespecified workload did not supply dynamic evidence sufficient to confirm a
technique class. It does not show that Boost.Math lacks those techniques.

Chinese canonical wording (also stored in the companion JSON `rq_statement`):

> 在冻结的 Boost.Math header workload 和 C++14 standalone 编译边界下，20 个预选行为均获得了正式执行终态。其中 8 个头文件编译成功，但未产生 subject-level call trace；其余 12 个发生非零编译退出。所有行为因此均保持 unresolved，分类结果为 `TECH_UNCERTAIN`，且没有 confirmed technique tags。该结果表明预设 workload 未提供足以确认技术类别的动态证据，而不表明 Boost.Math 缺少这些技术。

Failure attribution may appear as a limitation or diagnosis. It must not change
the statement above, and it must not be used to rewrite the workload after the
fact.

## 5. Subject-level claim ledger

These statuses govern what an RQ consumer may write about this subject. They do
not change `research/evidence/p3_claim_ledger_v1.3.0.yml`.

| Claim id | Status | Allowed wording | Consumer use |
|---|---|---|---|
| `BM_FORMAL_PROFILING_EXECUTED` | `observed` | 在该正式运行中，20 个冻结行为均获得终态。 | Results |
| `BM_EIGHT_COMPILE_NO_TRACE` | `observed` | 8 个 header 编译成功但无 subject-level call trace。 | Results |
| `BM_TWELVE_COMPILE_FAIL_CXX14_STANDALONE` | `observed` | 12 个 header 在 C++14 + standalone 边界下编译失败。 | Results; keep the boundary |
| `BM_HORNER_INTERNAL_HEADER_PRELUDE` | `qualified` | 8 个生成式 Horner/rational 头缺少父级 include 前置。 | Limitations or diagnosis; these frozen internal headers and this boundary only |
| `BM_CXX17_BOUNDARY_TWO_HEADERS` | `qualified` | `ccmath/div.hpp` 与 `univariate_statistics.hpp` 涉及 C++17 边界。 | Limitations or diagnosis; not Boost.Math as a whole |
| `BM_NO_CONFIRMED_TECHNIQUE_TAG` | `observed` | 当前证据无法确认任何 technique tag。 | Results; `TECH_UNCERTAIN`, empty `confirmed_tags` |
| `BM_NO_RELEVANT_TECHNIQUES` | `blocked` | Boost.Math 不包含相关技术。 | Forbidden in Results or Conclusion |
| `BM_PUBLIC_API_CXX14_UNIVERSAL_FAIL` | `blocked` | Boost.Math 公共 API 普遍不能在 C++14 下编译。 | Forbidden; the sample includes internal headers |
| `BM_PUBLIC_OR_CXX17_YIELDS_TECHNIQUE_EVIDENCE` | `speculative` | 换公共头或 C++17 后一定得到 technique evidence。 | Future-work hypothesis only |

## 6. Failure attribution as limitation only

Read-only stderr, depfile, and controlled-source attribution of the 12
`COMPILE_NONZERO_EXIT` rows remains diagnostic. It does not alter the receipt,
the classifier, or the RQ statement.

| Cluster | n | Proven first cause | RQ use |
|---|---|---|---|
| Generated `tools/detail` Horner/rational headers | 8 | Missing parent prelude (`std::integral_constant`, `BOOST_MATH_NOEXCEPT`); not a self-contained translation unit | Limitation: some frozen entries are internal generated headers |
| `ccmath/div.hpp` | 1 | Header `#error` under C++14 (`BOOST_MATH_NO_CCMATH`) | Limitation: one frozen entry is C++17-gated |
| `tools/univariate_statistics.hpp` | 1 | C++17 `std::is_same_v` under standalone, which skips the non-standalone `#error` | Limitation: one deprecated statistics header at this boundary |
| `special_functions/detail/bessel_i0.hpp` | 1 | Missing `boost::math::tools::digits` from `tools/precision.hpp` | Limitation: one internal special-function header |
| `special_functions/detail/hypergeometric_cf.hpp` | 1 | Missing `std::pair`; no inbound include in this tree | Limitation: one internal fragment |

These clusters must not be merged by pathname. They also must not be rewritten
as harness failure.

## 7. Fallacy scan

Coverage: 11/11.

- Simpson, Berkson, collider, base-rate, regression to the mean, and reverse
  causation do not apply to this descriptive terminal-state report.
- Survivorship bias: not found; all 12 failures are retained.
- Look-elsewhere effect: not found; all 20 rows were frozen in advance and are
  fully reported.
- Garden of forking paths: constrained by the frozen workload, the single
  formal run, and the retry prohibition.
- Correlation is not treated as causation: the RQ statement is observational.
- Ecological fallacy: generalizing from these 20 headers to Boost.Math or to
  all public APIs is an overgeneralization; the corresponding claims are
  `blocked`.

## 8. RQ consumer contract

An RQ consumer may:

- cite the formal receipt and this handoff as executed Boost.Math
  header-profiling evidence;
- report `TECH_UNCERTAIN`, empty `confirmed_tags`, and the 8/12 funnel;
- record that provenance moved from "not executed" to "executed, no
  confirmable dynamic technique evidence";
- place the five failure-attribution clusters in Limitations.

An RQ consumer may not:

- upgrade P3 paper claims, formal-denominator membership, or RQ4 support;
- overwrite the Phase-1 placeholder receipt or Phase-1 technique profile;
- treat `TECH_UNCERTAIN` as a failed experiment;
- claim that Boost.Math lacks the relevant techniques;
- claim that Boost.Math public APIs generally fail under C++14;
- rewrite the workload after seeing the 12 compile failures;
- rerun formal profiling.

No further implementation, qualification, or experimental step is required to
use this package as Boost.Math profiling RQ evidence.
