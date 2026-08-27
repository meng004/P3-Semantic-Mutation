# P3 C3 Prospective Applicability Search v2 Successor and Stopping Rule Design

Date: 2026-08-27
Status: `DESIGN_FOR_REVIEW`
Task: `P3_C3_PROSPECTIVE_V2_SUCCESSOR_AND_STOPPING_RULE_DESIGN`
Model / reasoning: `gpt-5.6-sol` / high
Mode: freeze already-approved eligibility-search rules as the unique v2 design specification
Verification status: `ANALYZED`
Reproducibility: `NOT_APPLICABLE` (this task produces a design, not an observation)
Correction: `P3_C3_PROSPECTIVE_V2_DESIGN_TERMINAL_BINDING_CORRECTION`
Correction mode: bind the unique `cohort-terminal.json` exact object and the unique future controller identity; do not change successor universe, order, eligibility, stopping, failure semantics, or evidence ceiling

This document is the only prospective v2 successor/stopping authority. It is
not a second applicability-authority manifest, not a second claim ledger, and
not a scientific observation. It does not authorize a confirmatory Package A
continuation. C3 remains `blocked`.

## 1. Background and disclosed prior result

### 1.1 Closed confirmatory path

The old confirmatory Package A path is already closed:

`C3_CONFIRMATORY_PACKAGE_A_PATH_CLOSED`

That closure is recorded in
`docs/review_20260827/p3_c3_selected_subject_not_applicable_scientific_path_review.md`
(file SHA-256
`47fb4c89d1204648b3b9e54d95df9f33e5362a4904c007cf54c9b978c488e850`)
and in the official selected-subject closures. This design inherits those
facts. It does not reopen, rewrite, or continue that path.

Closed subject (old rank 1; not a v2 successor):

| Field | Frozen value |
|---|---|
| Neutral snapshot ID | `6e05301ec7ec79d16233c086e5fc4a0b714e82a6ec8d6a86ca1218be67135062` |
| Controlled subject source ID | `12925a111a2d920ecfb2b0669969b61e7b1d4c66962b793417082bbec161b54e` |
| Controlled subject ID | `942d190c2c3972a6a6e9feb6ef5d4abee1d939cb0aa9ee676232ab0184dead09` |
| Official closure commit | `e6f9e84a5a71900e0fb6f0655393c5e1b613b6a5` |
| Official closure directory | `data/p3_v3/phase2/site-closures/6e05301ec7ec79d16233c086e5fc4a0b714e82a6ec8d6a86ca1218be67135062` |
| Frozen slots closed | 10 |
| Closure state / path | `APPLICABILITY_CLOSED_NOT_APPLICABLE` for all 10 |
| `SITE_FROZEN` objects | `0` |

Exact retained observation:

该主体在冻结 authority 下 10/10 slots 不适用。

That sentence is the entire confirmatory observation. It does not say that
the subject lacks the target constructs, that Eigen has no mutable site, or
that the five families are absent from the project.

### 1.2 Prior information disclosure

The 10/10 `NOT_APPLICABLE` result is prior information already known when
this v2 design is written. It is disclosed here and must remain disclosed in
every later v2 plan, run, and report. v2 is not an outcome-blind first look
at applicability. It is a new eligibility search that starts after that
known negative result.

### 1.3 What v2 is and is not

v2 is only:

`ELIGIBILITY_SEARCH`

v2 is not:

- a continuation of confirmatory Package A;
- a rewrite of the old rank table into a hidden successor trigger;
- an authorization of old rank 2 under the pre-result confirmatory design;
- a C3 upgrade path;
- a prevalence sample of cohort applicability;
- a second applicability authority, predicate set, slot inventory, or claim
  ledger.

The pre-result confirmatory design
(`0d566371a27448196177cd911850a56826f94bfc`, later incorporated into the
single-subject Package A design) froze one subject and said no second
subject was authorized. Phase-0 protocol files frozen on 2026-08-12 and the
applicability-authority design likewise define slot-level non-transfer; they
do not define a successor sequence, a maximum attempted-subject count, or a
cohort-exhaustion rule. The scientific-path review therefore selected
`NO_PREEXISTING_SUCCESSOR_RULE` and later closed the old path. This document
creates the missing successor/stopping rule as a new explicit version, after
the 10/10 result is disclosed.

### 1.4 Inherited scientific hold state

| Item | Inherited value | v2 effect |
|---|---|---|
| Old path terminal | `C3_CONFIRMATORY_PACKAGE_A_PATH_CLOSED` | remains closed |
| Old closures / ranking / predicates / authority | frozen bytes | not retroactively edited |
| Claim ledger | `research/evidence/p3_claim_ledger_v1.3.0.yml` | not modified |
| C3 `status` | `blocked` | remains `blocked` |
| C3 `upgrade_condition` | `RQ2 paired evidence and uncertainty accounting complete` | remains unsatisfied |
| v2 purpose | eligibility search only | cannot complete analysis-spec §11.2 |

C3 remains `blocked` after this design and after any later eligible-subject
find. Finding an eligible successor does not upgrade C3.

## 2. v2 identity

These identities are frozen by this design. A later controller must bind
them before any successor PBF site is opened.

| Field | Frozen value |
|---|---|
| Prospective slice ID | `p3-c3-prospective-applicability-search-v2` |
| Purpose | `ELIGIBILITY_SEARCH` |
| Document status | `DESIGN_FOR_REVIEW` |
| Selection mode | `ORDERED_STOP_ON_FIRST_ELIGIBLE` |
| Successor universe size | 22 |
| Maximum attempted successor subjects | 22 |
| Per-subject slot count | 10 |
| Retry policy | `NO_SCIENTIFIC_RETRY` |
| C3 evidence ceiling | eligibility only |
| Prior observed result | rank 1, 10/10 `NOT_APPLICABLE`, closure commit `e6f9e84a5a71900e0fb6f0655393c5e1b613b6a5` |
| Frozen authority commit | `03a032fe6cb490930083ab2517ee2dcf2bb8c747` |
| Frozen authority ID | `p3-v3-phase2-applicability-authority-v1` |
| Authority manifest artifact SHA-256 | `30b08271eafdead14a06707b461f108c1ec5a53eb5d2859a37b2cd6238e20214` |
| Authority schema | `p3-applicability-authority-v1` |
| Unique future controller path | `scripts/p3_v3/prospective_applicability_search_v2.py` |
| Official cohort terminal path | `data/p3_v3/phase2/prospective-applicability-search-v2/cohort-terminal.json` |

This design does not create a second applicability authority. Future v2
execution must use exactly one small production controller at
`scripts/p3_v3/prospective_applicability_search_v2.py`. That controller
must load the existing authority through the existing
`load_applicability_authority(...)` / `close_slot_with_authority(...)`
seam and the existing canonical JSON/hash helpers. Successor order and
stopping are authorized only by this document and by the Git commit /
SHA-256 of this file. This correction names the controller path. It does
not create the controller file.

Document path:

`docs/superpowers/specs/2026-08-27-p3-c3-prospective-v2-successor-and-stopping-rule-design.md`

This file's SHA-256 is computed after write and recorded in the task
return. It is not embedded here, because a digest that contains itself is
not a self-hash of this design.

## 3. Complete frozen successor table

The v2 successor universe is the old approved 23-subject admission set minus
closed rank 1. Old ranks 2-23 become successor ordinals 1-22, in that same
order. Rank 1 is not reinserted.

Each successor has exactly 10 frozen inventory slots under the existing
authority. No successor is omitted for missing archive, expected difficulty,
expected applicability, or other experimental results.

| Ord | Old rank | Scale | `total_effective_lines` | PBF sites | Frozen slots | Neutral snapshot ID | Controlled subject source ID | Controlled subject ID | PBF file SHA-256 | PBF `artifact_sha256` |
|---:|---:|---|---:|---:|---:|---|---|---|---|---|
| 1 | 2 | L | 258766 | 4028 | 10 | `74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886` | `e5f21a7d067d641d0a20bfc57c61e630d6f7588ef30235cea49c9a9cf950c7a7` | `89b0e6791c611b465b9216e833e0c526a53ffd6946b5cd20de045e3641f43914` | `a740d5019a19ee354f07e73e7c542dd1d79fb8969a2af48d5ef7975e534da4d3` | `75ff02923b851a03c9f6e83b6786da591dcd10c3143527f1691ab913318f4441` |
| 2 | 3 | L | 272416 | 9286 | 10 | `822470056d804eebf56b73ea7d7ad7a31099047760b88f561cad77e53fdbf363` | `6dfbd187d6520f0bd52016beb485f2b8f17c45637ce1c6ad9528bbccb66ac990` | `e1af9d59c570c0d5c006124ec9f96573a3dd46cb81e170a85f903a961ada530d` | `c7b70f05a688c7be061b7525a5a306aa6a45afee8781a9abf786aff933ebd63f` | `7dff0c0bc10a26e9a6003a522a1cf0bf68790624c8b008df23630ee4d77a77b0` |
| 3 | 4 | L | 299333 | 11066 | 10 | `734d6accd77800469372ff6a578920ec2545e1119c037457628d16cb79c02271` | `11bb24a1429cbf03eeb863ba7148f41e656a8fea7a063d80415ee2c33cf24574` | `3528152e3952c07a1e255eee71a07d3f91d140e846737782a8de9633a34eaacb` | `532d62c2159d7c81a6fed9c9d4f31e28f27e61b677f704c06e34b8895f006f37` | `fe9c2cfc36e1a80cb6e5f987e5c56b6a7ef423f39af95594f65486036c0dd055` |
| 4 | 5 | L | 314450 | 2048 | 10 | `b3e0d3cd4e81efb817dc0f2805d855d9c8a82e1bf483e2870e244190716349b3` | `1c479b03eaa51298b396f8edd4401d65062448489df790bcd7e3c24bc5825640` | `038f9ae4b295b98914a4d1f5799db6bda686779ee3dded3e9ef0d0bdb715f183` | `fede8e4b0269c8afd080b45a2936fc436eb026a252ca50697248dc227c97245a` | `a6ddb14c3499e1d031bcde6c2d82c18145305f7f8d2e1e27f85a2d43454980f5` |
| 5 | 6 | L | 372366 | 2312 | 10 | `3019d9a64c261c22d1d7af17cc3946dfc29f159d51eabd3e238a0f169d5fac12` | `c0dac5b06ec432e720310337fd465a86ab1ff7c1b3a86ce182bdfda2c721291a` | `e7b69c4b571d4824d12e039cab07ac922161192b4da1356599eb9510d6275d1e` | `f4ab2c8aca30602fd38384a7e45b3c48085afb0a33f224b7796abeb39495bc79` | `b10bc7fa1c6ce3e703480f5ffb6902176de091c6c0579bfe55543bc8fb6c3bbd` |
| 6 | 7 | L | 382261 | 14029 | 10 | `b2bfbf1e0511e6e7b01e22853da91b66a2801a6ff7997ed48ac78acef5886f01` | `6464893a5a2a64fe05118f3da8c59a6d583110f3c41dc50383df596f1b177bc9` | `d386a35091e9053fbb3a0124257777c3791469b25186f9ee4b125ef62f938b46` | `89d836be994c11bc4404e86cee3e67fa553525ea1524023a9ca473aaad147fb2` | `6eb04ce3f2a92ddc0b2c2b6052f5c543ca24b93f3b5e4b771b9af902699bbfa8` |
| 7 | 8 | L | 389743 | 6496 | 10 | `3c6e698ff35c59ec23d2ccbe722d7c0d40f553cb03d53f4b69e1ad2125343d02` | `77ab955fae5d9768f35eff6b32f19b09920efeae06984fa297165923cd34e47b` | `ff6251cb3d23ab1e49d549054b4dba416fdbec1e2fd8d969c18143ea4fae751f` | `2232d2ebc59f7fd285352bec0498bcf2abca14b75b317d112265ee5a6912cf90` | `0ffe0dfcdceaaf6b5fe46f18b8956441f1331a63a24be0824018828215110daf` |
| 8 | 9 | L | 459888 | 10811 | 10 | `4e7e9556b3d621681c88c82f26cd95f5604d7a8b85cc56bf7e6d4db5a274f38b` | `667f66bbdb3b392af99b044181dcfa861040546fc5550906e30fca2f9aabb5d0` | `0fefefc546f7c4519d036849a85279cc7d3aa00fe88d6ed5e259209769b5bb48` | `168bc06564842818224dec76e97287d33d19aea9b60482d2ab674b9e89f7092e` | `b5fc46928d1dd5c85a60c36f2e2df2b35c97b8163bc9c14eda9667e1120c0503` |
| 9 | 10 | L | 532232 | 22438 | 10 | `24ab4a18534a3125f49060cc83fca0ea4c66646f701eb5e4091097a7ae1f9d8b` | `bfaa320be236999863943c8521dd7f3f0f17c2d7f696d22a3667d4c7f021ac82` | `6e71e0c72a29aa77a6c83ea81d39af7801b6a6bad3dd053a6ec7eb6df4bbd6db` | `1bd60872bdce13aa6395fc497656ecfcfd6d416d5597bd8608efcfb6f8a02e29` | `4bc3aee714b20e2e82ac89c301fba1b5144c6b7e39d2bc2f5a2dd18234929027` |
| 10 | 11 | L | 557567 | 23842 | 10 | `9a76cacce39b2908de91ee2d1ad30c9a6564175f3ab298dbd1d1e0285b386e21` | `257a39a07c314ef51c4582475730db5dc2387f80bbbfbf518fc2a33d6dd1ffb6` | `d81ff7e27069d30df42111cedb08598012076173d94e5f84dfeb1ee2a124e2c8` | `e9fceb133d1cb2d88527a21636776a16ff0300ba8d6efa4dc177e93494d6a907` | `1117cb4c1f5417354096a66fb9518c25332eb657e4e95a35a4b0a97c65667b94` |
| 11 | 12 | L | 557723 | 23844 | 10 | `643985b0b045d17be89ebce2defe02cd4953191330bb79db00c36115e34eaa1b` | `faa1bb211d1677c40c6a2cffc69701fc9458bd1b4f6827705e8b40d2b625a446` | `35d537a7639d6bd8966abb2a21f453dbc7d648876ab449d264c9a4690748af20` | `b526da6b9070f4615694711b51e71c326d4346224eea5e3dcbdb12ac61e72df7` | `31d662b4ed318b20630054f4e1397120f97656cd3c3bb14eabce2d911ebb0346` |
| 12 | 13 | L | 578758 | 24227 | 10 | `1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72` | `bf870e2e8a7b10ea91fa9d03c223f041eee7477c7a84ce54f5139ff15d173c45` | `43a6370a0fe446cfc2895e283a19c01fed0c94dd2da5f69f14b3ec64ed32bad2` | `a41120f5dfd76a6498d0233fdf2e578090e1755ff36d48e2cd2565d3ef3c4b5a` | `d71a01c49bbad08fe56a41549fb14bd768528c60680ece7ac241b170bc753f3f` |
| 13 | 14 | L | 584475 | 24378 | 10 | `d782e757e28052ffc81819c610119dd6ce0176be1b508773d7f43df0aa9cf766` | `ebc45688ba350b2ba040d79b0c04f42ceca51c574be03da70d86a68818cc09ba` | `38b6c8236a5717b3ad99240879cc97221b1a58ad6ccb02e74a0747c4c725c780` | `afdb0a8646645fc8edccfbc6e88d1969c0851917c42d3790e6e0c77e70f29603` | `2fc4d78dfc99ac3fe53ecea4edc2166fa95a82e34d65620699a546445da4fdd2` |
| 14 | 15 | L | 585286 | 24425 | 10 | `3640321076e7abba42862bc92045f019333eb0f92f477f6dcabaddf937681710` | `080c4f0bf035a7297803fa723fc667295538f88288ad13daecba4e2965eb72c0` | `7ead91b227c321fd6430a9f9c7f10cf888de0c98848d0b1d9cd05d04896843a5` | `7199d8dc8510cc644860106fd96ee369a495a3df95f5fc9eaa32ba1df2276a85` | `b534d0b13a0341f913665bfb989225c7cbf458a0bdce202fe9811f62af471f1d` |
| 15 | 16 | L | 675990 | 5994 | 10 | `92b4ec544c5586ae7458a007c1ef12c65b70c7668128f0ef95006c5d45091b0f` | `130e24e50e73fe2e25e3c0a453c8e8e269adf1471ac7899ef4b7307b54ef3b60` | `25ad02f3b77e0e325385ce63bf0f49dc1aff6081a7b2373f1fcae68c8119a202` | `9095874da884d962cc33561fd1a74d1a20c9da13a7f16f82fae1fa4681c70c71` | `72ead1b9087c20aa0ee28de990d3667cdcde6b93a9e814aaf6cdbddcd524540a` |
| 16 | 17 | L | 788145 | 6715 | 10 | `aa19a201f5819c88d7de328c09159867ec6043e2b2f254c267a0cf649ba29176` | `714f53ef8ae2e4f296b09042e985e8f63f980d8f9e4439c9bcaefb3cc88087bb` | `072ad35799114749ca393fa74b3defe9e60c76560450bd9ffa6b6bedbcf83805` | `e28a88c3e8f5b45a4f2da416df475c604159e9c3fb432f9e4d6278f5c18782a7` | `b033449bdfe17705d41779bde24bbaecc585caee8d47505790af7780c3ea55c1` |
| 17 | 18 | L | 818032 | 6671 | 10 | `a6fc16a5dd71bd0ee219d6d21ec1ac7d08b7b0d12fd113b525f537cdb16ae8c5` | `aa441a5251b2548885d91d433d8f1cd013c2298856b2fc54082bf20072059d39` | `7e1c0f1a4a5d83730c57088a70763fdaeb452aff00e28a51fa08772157ac0632` | `943533ac3b16964ffc4560baccc5423f823b29aa61516d1d8e9f70ca64353c98` | `5e179b38fe494da2762889a2570f7ce433ccb45806a275d094360b8f08cd747d` |
| 18 | 19 | L | 921535 | 23732 | 10 | `75c0e11c4b655a3122b438bb609fdbe7d845ef333c3f212e6c38df6deb730a63` | `cb8d47f1e3d97ef5d912b7456f365a2c74be1e184bf028599ad82db365c312a6` | `821b57e8a17272636dd08d4a6a96cda3965a221ced4fcc225c613648668a28b6` | `77afeafb73de4dc36ccf4c08053bb12317d22a472ef73064d01d2cbaf0e561b0` | `9dea8204ccea78b6092708580b12a8b37e4fdb2d3231d2c36193c6a67a73881a` |
| 19 | 20 | L | 967764 | 24785 | 10 | `bb43dfe28f9b3aa58c6daffcc2a50a04b712725c27d386ebc8b4ca139d57e7e2` | `45a05ea410cc3de9bcf66d3a883bc127f38b9e3b98ecec6c3270a5da1708d3d3` | `f5cea2872cbcb90333f087a87f3fe50cfbd1bf79c2de420e6bacec0a1d442b08` | `6690ba09d0b81b65340816feb5685208a730ae549feeb785143d93a0e03ed705` | `905c92759aaf8bc489ce010d1d1d56047f162d6684c4d3df604eae41dc3808d8` |
| 20 | 21 | L | 972891 | 2409 | 10 | `f5f00bc450d4daba54f08269c336f5d76d785df620416b1acd080ee14c2496a7` | `bb34466e627756c6c6c63720392b861d47d65cd767af2999b50df4b2f4904e41` | `2fc0e80d3659a765ee931208918d9da1f83cab746476f8463a138d90e4aee455` | `f4e5767abaa6e90d128cb1833a94f8bf9b02afc6d5a2d13d418f6343026c5290` | `b67b5524c2acf918ea517d257efac50115659e99d42a30b5f55176de992dd8ea` |
| 21 | 22 | L | 2776117 | 57397 | 10 | `84b70a11f582eab3ce3c5029b2c17cf916e354df09184224875a3ba53000974a` | `33fe48fd8a0bd0d00e0b52ec4c586d5ab0190f7447ddd9188460e32370f2e748` | `0f6ed8e3d9d1107fe96b7f8b2686eaace9dec1cf78235f380d36b3912145ffc2` | `971313d8fd5e8999389802780899701e03e876c5104093b00db4590fdd41bd36` | `a85086e0c52d989827dec9040ea129f2bbee39fcff1580bf9848cef481cd7df4` |
| 22 | 23 | L | 4043349 | 62240 | 10 | `494c35cb94f9fd4db2559ad0c7da45f54ca17ac5b3a8ab8d481142b1349280de` | `14bb2817b2dc0322ebb19f22f864481ff257dcb75bd7e193908fba1c5d327541` | `5b811ed080bcce73b009712b8038eaf21f66de1fc397275e0019b6a93c6e0379` | `cf18054b2c574bd59ddc9a4640bfb8156dfeb72b1fe74a8f6f01f7e5cab89e5f` | `9deaca70691a71539b900e58c52e86bae4711dd21485f2f4d3e399dbaaa957a5` |

Counts in this table: 22 rows; ordinals 1-22; old ranks 2-23; 22 unique
neutral snapshot IDs; 22 unique controlled subject source IDs; 22 unique
controlled subject IDs; frozen slot count = 10 on every row.

Successor ordinal 1 is old rank 2. That identity is in the v2 sequence
because the frozen four-key ranking placed it there. It is not authorized
by the old confirmatory design, and it is not skipped because other
experiments exist for that identity.

## 4. Successor universe and ranking proof

### 4.1 Candidate universe and admission set

The candidate universe remains the 35 `verified_bridge.json` records. The
admitted set remains the same 23 subjects already used by the
single-subject Package A design: those that passed the frozen descriptor,
adapter-discovery, Public Behavior Frame, and source-scale gates.

This design reconstructs that admission set from frozen identity and count
fields only:

- 35 Phase-1 source-scale objects supply `neutral_snapshot_id`,
  `scale_class`, `total_effective_lines`, and
  `controlled_subject_source_id`;
- 35 PBF objects supply identity, file SHA-256, `artifact_sha256`, and
  `len(sites)` only;
- 35 profiling-workload objects supply identity and `artifact_sha256`
  only, used to rebuild `controlled_subject_id`;
- the existing authority projection confirms the rebuilt IDs.

Operational reconstruction of the old 23-subject set: PBF `sites` length
is nonzero. That yields 23 subjects, all `scale_class=L`, all
`discovery_status=EXECUTABLE`, all present in the authority projection.
The other 12 Phase-1 subjects have PBF site count 0 and were outside the
old ranking. They remain outside v2. They are not added now.

No archive existence check, no difficulty judgment, and no applicability
prediction entered admission or order.

### 4.2 Four-key order

The executable frozen keys, already approved before the old subject freeze,
are exactly:

1. scale: `S < M < L`
2. frozen `total_effective_lines` ascending
3. Public Behavior Frame site count ascending
4. `neutral_snapshot_id` ASCII/UTF-8 lexicographic ascending

`normalized source total bytes`, archive size, download status, expected
design difficulty, profiling results, technique profile, mutation or MR
outcome, and project name are not sort keys.

`controlled_subject_id` is rebuilt with production `canonical_sha256` over

```text
{
  "normalized_source_tree_sha256": <verified_bridge record>,
  "build_descriptor_sha256": <verified_bridge record>,
  "public_workload_set_sha256": <profiling-workload artifact_sha256>,
  "domain": "P3-SUBJECT-v1"
}
```

The 35 rebuilt IDs equal
`applicability-authority.json` `subject_identity_projection`. Every
admitted and excluded subject has exactly 10 inventory slots.

### 4.3 Reconstruction versus the old recorded ranking

Rebuilding the 23 admitted subjects under the four keys yields this first
five, which must and do match the old design table:

| Rank | Scale | `total_effective_lines` | PBF site count | Neutral snapshot ID |
|---:|---|---:|---:|---|
| 1 | L | 201553 | 3338 | `6e05301ec7ec79d16233c086e5fc4a0b714e82a6ec8d6a86ca1218be67135062` |
| 2 | L | 258766 | 4028 | `74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886` |
| 3 | L | 272416 | 9286 | `822470056d804eebf56b73ea7d7ad7a31099047760b88f561cad77e53fdbf363` |
| 4 | L | 299333 | 11066 | `734d6accd77800469372ff6a578920ec2545e1119c037457628d16cb79c02271` |
| 5 | L | 314450 | 2048 | `b3e0d3cd4e81efb817dc0f2805d855d9c8a82e1bf483e2870e244190716349b3` |

Rank 1 is the closed confirmatory subject. It is excluded from v2.
Ranks 2-23 become successor ordinals 1-22 without reordering.

If a later rebuild differs in identity, order, count, or slot count, the
terminal is `V2_SUCCESSOR_IDENTITY_CONFLICT`. This design is then invalid
and must not be executed.

### 4.4 Explicit non-skips

The following are forbidden reasons to drop, replace, or reorder any of
the 22 successors:

- local source archive missing;
- project judged hard or easy;
- expected predicate applicability;
- other formal results already existing for successor ordinal 1 or any
  later ordinal;
- profiling, technique, mutation, or MR information;
- putting rank 1 back into v2.

## 5. Within-subject 10-slot completion rule

A future official v2 execution, for each successor that the controller is
allowed to open, must do all of the following.

1. Load the existing frozen authority. Use exactly the 10 inventory rows
   whose `controlled_subject_id` equals that successor's frozen controlled
   subject ID. Use those rows in the inventory's existing canonical order.
   Do not add a slot. Do not drop a slot. Do not reorder slots. Do not
   change family or mechanism.
2. Open that subject's frozen PBF file once, as a regular file. Verify the
   PBF file SHA-256, `artifact_sha256`, controlled subject source ID, and
   frozen site count recorded in §3. Do not open a second PBF. Do not
   substitute another subject's PBF.
3. For each of the 10 slots, call the existing
   `close_slot_with_authority(authority, inventory_row, canonical_sites, pbf)`
   exactly once.
4. If any earlier slot, including the first, yields `SITE_FROZEN`, still
   finish the remaining slots of that same subject. Eligibility is a
   subject-level judgment after all 10 valid closures exist.
5. Judge eligibility only after all 10 closures are complete and
   verified.
6. An inapplicable slot does not transfer to another family of the same
   subject, to another subject, or to another mechanism.
7. Do not create an 11th slot.
8. Do not modify a predicate, the registry, the inventory, or site order.

The existing closer remains the only site-selection implementation. This
design does not replace it and does not add a parallel closer.

## 6. Eligibility definition

Subject eligibility is defined only after 10 valid official closures exist
for that successor.

| 10-slot result | v2 subject terminal |
|---|---|
| At least one `SITE_FROZEN` | `V2_APPLICABILITY_ELIGIBLE` |
| 10/10 `APPLICABILITY_CLOSED_NOT_APPLICABLE` | `V2_APPLICABILITY_INELIGIBLE` |

These terminals are v2 eligibility labels. They do not update
`eligible_for_construct`, Phase-1 admission, the old confirmatory
closures, or the claim ledger.

The following are not eligibility terminals:

- infrastructure failure;
- identity mismatch;
- missing, extra, or unverified closures;
- partial subject output;
- atomic-placement failure;
- preflight failure.

Those conditions are `V2_EXECUTION_FAIL` or `V2_PREFLIGHT_FAIL`. They must
not be recorded as `V2_APPLICABILITY_INELIGIBLE`.

`UNPROFILED` is not `NOT_APPLICABLE`. That Phase-0 rule remains.

## 7. Controller state machine

Future official execution must be one pre-authorized controller invocation.
It is not a sequence of human next-subject decisions.

States:

| State | Meaning | Allowed next states |
|---|---|---|
| `V2_PREFLIGHT` | identity and isolation checks; no successor PBF site opened | `V2_SUBJECT_OPEN` for ordinal 1; or `V2_PREFLIGHT_FAIL` |
| `V2_PREFLIGHT_FAIL` | preflight failed | terminal; no subject selection |
| `V2_SUBJECT_OPEN` | current ordinal's 10 slots are being closed in memory | `V2_SUBJECT_ELIGIBLE`; `V2_SUBJECT_INELIGIBLE`; `V2_EXECUTION_FAIL` |
| `V2_SUBJECT_ELIGIBLE` | current subject has a verified eligible 10-slot set | `V2_ELIGIBLE_SUBJECT_FOUND` |
| `V2_SUBJECT_INELIGIBLE` | current subject has a verified 10/10 inapplicable set | `V2_SUBJECT_OPEN` for ordinal+1; or `V2_COHORT_EXHAUSTED` if ordinal = 22 |
| `V2_ELIGIBLE_SUBJECT_FOUND` | first eligible successor recorded; later PBFs not opened | terminal |
| `V2_COHORT_EXHAUSTED` | ordinals 1-22 all ineligible | terminal |
| `V2_EXECUTION_FAIL` | run exception, identity change, partial result, or atomic-place failure | terminal; no automatic continuation |

Transition rules:

1. Start in `V2_PREFLIGHT`.
2. Leave preflight only after every check in §10 passes.
3. The first subject state is successor ordinal 1, never old rank 1.
4. The controller may enter `V2_SUBJECT_OPEN` for ordinal *k* only if
   ordinals `1..k-1` have verified `V2_APPLICABILITY_INELIGIBLE`
   terminals.
5. The current subject's 10 closures must all be valid before any later
   state is entered.
6. No human choice of the next subject is a legal transition.
7. No transition skips a failed subject, enlarges the universe, or
   restarts from rank 1.

### 7.1 Unique controller source file

The future controlled run uses one independent small production
controller and no other runner:

`scripts/p3_v3/prospective_applicability_search_v2.py`

That file's duties are only:

- read and verify this v2 design identity;
- load the existing applicability authority;
- run the 22-row order written in §3;
- complete 10 closures per opened subject;
- execute `ORDERED_STOP_ON_FIRST_ELIGIBLE`;
- atomically write each official subject-closure directory;
- write the unique cohort terminal last.

The controller must reuse:

- `load_applicability_authority(...)`;
- `close_slot_with_authority(...)`;
- the existing canonical JSON and hash helpers.

The controller must not:

- implement a second predicate set;
- implement a second closer;
- rewrite the inventory;
- read source, profiling, technique, or mutation outcome;
- create a second manifest, ledger, or schema file;
- accept a user-supplied successor order;
- accept a user-supplied maximum attempt count;
- accept a user-supplied applicability map;
- accept skip, retry, or resume parameters.

This correction only freezes that path. It does not create the
controller file.

## 8. Stop-on-first-eligible rule

Selection mode is `ORDERED_STOP_ON_FIRST_ELIGIBLE`.

After a current subject is verified `V2_APPLICABILITY_ELIGIBLE`:

1. Record `V2_ELIGIBLE_SUBJECT_FOUND`.
2. Record that subject's frozen identity and successor ordinal.
3. Stop immediately.
4. Do not open any later successor PBF.
5. Do not close any later successor slot.
6. Do not continue in order to estimate a rate.

Continuing after the first eligible subject would convert a stopping rule
into an undeclared prevalence sample. That is forbidden.

Maximum attempted successor subjects remains 22. Finding an eligible
subject earlier does not raise or lower that maximum. It only stops the
search.

## 9. Cohort exhaustion

If successor ordinals 1 through 22 are all verified
`V2_APPLICABILITY_INELIGIBLE`:

1. Record `V2_COHORT_EXHAUSTED`.
2. Stop.
3. Do not add a 23rd successor.
4. Do not return to old rank 1.
5. Do not reinterpret the 22 ineligible labels as a statement that the
   35-subject cohort, Eigen, or any project lacks the target constructs.

`V2_COHORT_EXHAUSTED` is a v2 eligibility-search terminal. It is not a C3
result and is not a prevalence estimate.

## 10. Preflight

The future controller must run one preflight before any successor site is
opened. Preflight may read file bytes and metadata. It must not emit,
print, log, or inspect concrete site path, symbol, or span values.

### 10.1 Required checks

All of the following must pass in one preflight:

1. Current code commit is recorded and is the authorized execution
   commit for the later run plan.
2. Authority identity equals
   `p3-v3-phase2-applicability-authority-v1` /
   `p3-applicability-authority-v1`, artifact SHA-256
   `30b08271eafdead14a06707b461f108c1ec5a53eb5d2859a37b2cd6238e20214`,
   originating from frozen authority commit
   `03a032fe6cb490930083ab2517ee2dcf2bb8c747`.
3. Registry, inventory, and implementation SHAs still match the frozen
   authority bindings:

   | Binding | Expected value |
   |---|---|
   | Authority file SHA-256 | `80702537fab92c09506c9e94f8fb6a14e6f52cfcf23e1ae2f134be1d15a471a5` |
   | Slot-inventory artifact SHA-256 | `5c7f2dae8b0b7fd72926e2569354dbf6e878186f69d512e259e6034026dd0e27` |
   | Slot-inventory file SHA-256 | `5846aa3eccb55958955e42b298177cf7692603608ab5eed99929b01d39b4a967` |
   | Predicate-registry artifact SHA-256 | `26835b99baefad1f8eba12d8196eb34f1567e182d5fdb12767217838276c57e1` |
   | Predicate-registry file SHA-256 | `ce05e552122a871d4acb81d2f071d0fa1653228232d5ab7446772206c0b32218` |
   | Predicate implementation SHA-256 | `6c0c03b43ae895b331122f462f0f778e4f35093b55ff5395067ce6c73c2837c5` |
   | Slot implementation SHA-256 | `ca6365f268ff418b31b0c770998d070db1571d54d82ce7e924810b0d0c2352f1` |
   | Canonicalization implementation SHA-256 | `9f619073626003caa7d724a19655b5abae92318afd3f656494a0843613b6f57a` |
   | Site-policy file SHA-256 | `9772430e0a2539667a9aaa776b47ecae92a7830e19ec0a6e75a5dda9cfdfdcf7` |
   | Operator-catalogue file SHA-256 | `060671a031c36699fe63c7376afbb4714c84b25eab28f06445804ee8d232a635` |

4. This design file exists and matches the SHA-256 recorded by the later
   authorized run plan.
5. The 22 successor identities in §3 rebuild from the frozen four-key
   rule and remain unique.
6. Each of the 22 controlled subject IDs has exactly 10 frozen inventory
   slots.
7. Each of the 22 PBF paths is an ordinary file, not a symlink and not a
   directory.
8. Each PBF file SHA-256, `artifact_sha256`, controlled subject source
   ID, and frozen site count equals the §3 row.
9. Official v2 output namespaces in §11.1 do not exist.
10. The 10 old rank-1 closures remain the original bytes under
    `data/p3_v3/phase2/site-closures/6e05301ec7ec79d16233c086e5fc4a0b714e82a6ec8d6a86ca1218be67135062`.

### 10.2 Preflight failure

If any check fails:

`V2_PREFLIGHT_FAIL`

The controller must not enter subject selection, must not open a successor
PBF site, and must not write an official v2 subject directory.

## 11. Failure semantics

### 11.1 Official and temporary paths

Future official v2 artifacts use a new namespace. They must not overwrite
the old confirmatory closure directory or any other existing path.

| Role | Path |
|---|---|
| Official cohort root | `data/p3_v3/phase2/prospective-applicability-search-v2/` |
| Official subject directory | `data/p3_v3/phase2/prospective-applicability-search-v2/subjects/<neutral_snapshot_id>/` |
| Official cohort terminal | `data/p3_v3/phase2/prospective-applicability-search-v2/cohort-terminal.json` |
| Temporary sibling root | `data/p3_v3/phase2/prospective-applicability-search-v2.staging/` |
| Temporary subject directory | `data/p3_v3/phase2/prospective-applicability-search-v2.staging/<neutral_snapshot_id>/` |

Preflight requires that both the official cohort root and the temporary
sibling root are absent.

Write chronology, in this exact order:

1. The controller source-file SHA-256 is already fixed by the later
   authorization.
2. Preflight in §10 all passes.
3. Subjects execute in successor ordinal order.
4. Each opened subject's 10 closures complete in memory first.
5. That subject's directory is verified in the temporary sibling path,
   then placed atomically into the official subject path. Do not
   overwrite an existing official path.
6. After `V2_ELIGIBLE_SUBJECT_FOUND` or `V2_COHORT_EXHAUSTED` is reached,
   construct the cohort terminal in staging.
7. Rebuild and verify every consistency rule in §11.5.
8. Place the terminal atomically as official
   `data/p3_v3/phase2/prospective-applicability-search-v2/cohort-terminal.json`.
9. The official cohort terminal is the last official artifact.
10. After that terminal is written, do not open another PBF and do not
    write another closure.

### 11.2 Execution failure

Any of the following during a subject or during atomic placement is:

`V2_EXECUTION_FAIL`

- run exception;
- identity change;
- partial closures;
- unexpected extra files;
- atomic placement failure;
- official path already present.

Rules after `V2_PREFLIGHT_FAIL` or `V2_EXECUTION_FAIL`:

- do not write an official `cohort-terminal.json`;
- do not write any object that masquerades as a scientific cohort
  terminal;
- do not label the abnormal subject `V2_APPLICABILITY_INELIGIBLE`;
- do not advance to the next ordinal;
- do not retry;
- keep already officially placed prior ineligible subjects;
- keep the temporary or partial path for audit;
- record the failure in the task log and the final return;
- stop for a separate infrastructure and evidence review;
- do not auto-resume.

Infrastructure failure must not enter eligibility evidence.

This design does not create a retry-authorization format. Retry remains
undefined. `NO_SCIENTIFIC_RETRY` is the only retry policy.

### 11.3 Unique cohort-terminal exact object

The unique future official terminal is:

`data/p3_v3/phase2/prospective-applicability-search-v2/cohort-terminal.json`

It must be a canonical JSON exact object. Its keys are exactly the
following, in this meaning, with no extra field:

```json
{
  "schema_version": "p3-c3-prospective-applicability-search-v2-terminal-v1",
  "slice_id": "p3-c3-prospective-applicability-search-v2",
  "design_commit": "<authorized design commit SHA>",
  "design_file_sha256": "<authorized design file SHA-256>",
  "authority_artifact_sha256": "30b08271eafdead14a06707b461f108c1ec5a53eb5d2859a37b2cd6238e20214",
  "controller_source_sha256": "<SHA-256 of scripts/p3_v3/prospective_applicability_search_v2.py>",
  "prior_closure_commit": "e6f9e84a5a71900e0fb6f0655393c5e1b613b6a5",
  "terminal_status": "<V2_ELIGIBLE_SUBJECT_FOUND or V2_COHORT_EXHAUSTED>",
  "attempted_subjects": [],
  "first_eligible_successor_ordinal": null,
  "first_eligible_neutral_snapshot_id": null,
  "artifact_sha256": "<canonical self-hash>"
}
```

`schema_version`, `slice_id`, `authority_artifact_sha256`, and
`prior_closure_commit` are the literal values above.
`design_commit`, `design_file_sha256`, and `controller_source_sha256`
are filled only by the later authorized run. `terminal_status` is
exactly one of the two scientific strings named above. Any other
terminal string fails closed.

Do not add a timestamp, hostname, nonce, path snapshot, or any other
non-deterministic field.

Self-hash:

```text
artifact_sha256 = canonical_sha256(body without artifact_sha256)
```

The existing `canonical_sha256` helper is the only allowed hash.

### 11.4 Attempted-subject and closure exact objects

`attempted_subjects` is a JSON array ordered by `successor_ordinal`
ascending.

Each attempted-subject row is a canonical exact object with exactly
these fields:

```json
{
  "successor_ordinal": 1,
  "neutral_snapshot_id": "<64-char SHA-256>",
  "controlled_subject_source_id": "<64-char SHA-256>",
  "controlled_subject_id": "<64-char SHA-256>",
  "eligibility": "<V2_APPLICABILITY_ELIGIBLE or V2_APPLICABILITY_INELIGIBLE>",
  "closures": []
}
```

`successor_ordinal` is an integer. The three identity fields are
lowercase 64-character SHA-256 strings. `eligibility` is exactly one of
the two labels in §6.

`closures` is a JSON array ordered by the frozen inventory's canonical
slot order for that `controlled_subject_id`.

Each closure row is a canonical exact object with exactly these fields:

```json
{
  "slot_id": "<64-char SHA-256>",
  "state": "<SITE_FROZEN or APPLICABILITY_CLOSED_NOT_APPLICABLE>",
  "site_id": "<64-char SHA-256 or null>",
  "closure_artifact_sha256": "<64-char SHA-256>"
}
```

Each attempted subject must contain exactly 10 closure rows.
`closure_artifact_sha256` is the existing closure object's self-hash.
`site_id` is `null` when `state` is
`APPLICABILITY_CLOSED_NOT_APPLICABLE`. When `state` is `SITE_FROZEN`,
`site_id` is the existing closer's site identity hash.

The terminal must not contain:

- site path;
- symbol;
- source span;
- contract;
- patch;
- profiling result;
- technique;
- mutation or MR outcome;
- runtime timing;
- project-quality judgment.

### 11.5 Terminal consistency rules

A later validator must fail closed unless every rule below holds.

General rules:

- `attempted_subjects` is nonempty.
- ordinals start at 1, increase by 1, have no gap, and have no
  duplicate.
- each attempted row's `successor_ordinal`,
  `neutral_snapshot_id`, `controlled_subject_source_id`, and
  `controlled_subject_id` equal the matching §3 successor exactly.
- attempted count is at most 22.
- each attempted subject has exactly the 10 frozen slot IDs already
  bound to that `controlled_subject_id`.
- each referenced closure artifact passes its existing self-hash.
- each closure `state` is only `SITE_FROZEN` or
  `APPLICABILITY_CLOSED_NOT_APPLICABLE`.
- each row's `eligibility` is derived mechanically from that subject's
  10 closure states using §6: at least one `SITE_FROZEN` yields
  `V2_APPLICABILITY_ELIGIBLE`; 10/10
  `APPLICABILITY_CLOSED_NOT_APPLICABLE` yields
  `V2_APPLICABILITY_INELIGIBLE`.

If `terminal_status = V2_ELIGIBLE_SUBJECT_FOUND`:

- the last attempted subject is the unique first eligible subject;
- that last subject has at least one `SITE_FROZEN`;
- every earlier attempted subject is 10/10
  `APPLICABILITY_CLOSED_NOT_APPLICABLE` and
  `V2_APPLICABILITY_INELIGIBLE`;
- `first_eligible_successor_ordinal` equals the last attempted
  ordinal;
- `first_eligible_neutral_snapshot_id` equals that last subject's
  `neutral_snapshot_id`;
- no later successor appears.

If `terminal_status = V2_COHORT_EXHAUSTED`:

- `attempted_subjects` contains exactly 22 rows;
- ordinals are exactly 1 through 22;
- every `eligibility` is `V2_APPLICABILITY_INELIGIBLE`;
- all 220 closures are `APPLICABILITY_CLOSED_NOT_APPLICABLE`;
- `first_eligible_successor_ordinal` is `null`;
- `first_eligible_neutral_snapshot_id` is `null`.

Any other `terminal_status` string fails closed.

`V2_PREFLIGHT_FAIL` and `V2_EXECUTION_FAIL` are not values of
`terminal_status` and must not appear in
`cohort-terminal.json`.

### 11.6 No independent schema, manifest, ledger, or subject terminal

The exact-object structures in §11.3 and §11.4 belong to this v2
design. They are not a second authority.

Do not create:

- a JSON Schema file;
- a subject-terminal file;
- a run manifest;
- a second applicability authority;
- a second claim ledger.

The machine-readable official output is exactly the already-defined
per-subject official closures plus this one cohort terminal.

## 12. Information isolation

This design task did not read successor site path, symbol, or span;
successor source or archive bytes; profiling results; technique profiles;
RQ handoffs; claim outcomes other than C3 status / upgrade condition; P12
issue, PR, patch, or reveal material; or mutation / MR outcomes.

Future preflight and controller isolation:

- Preflight may hash and count PBF files. It may not dump or check site
  contents.
- The controller may open a successor PBF only after preflight, and only
  for the current ordinal, and only through the existing closer.
- Later ordinals remain unopened after stop.
- Old rank-1 closures are prior information. They are not inputs to
  predicate evaluation for a successor.
- Derived-subject files remain forbidden authority inputs because they
  embed sites, technique fields, and profiling results.

## 13. Evidence ceiling

v2 may later report only:

- the 10-slot closure distribution of an executed successor;
- that subject's `V2_APPLICABILITY_ELIGIBLE` or
  `V2_APPLICABILITY_INELIGIBLE` label;
- the frozen identity of the first eligible successor, if one exists;
- the successor ordinals actually inspected;
- the cohort terminal `V2_ELIGIBLE_SUBJECT_FOUND` or
  `V2_COHORT_EXHAUSTED`.

v2 must not:

- estimate a cohort applicability rate;
- treat the stop-before-exhaustion fraction as prevalence;
- compare projects as better or worse;
- infer properties of unexecuted successors;
- infer that Eigen or any project lacks the target constructs;
- infer that the five families are absent from a project;
- describe the first eligible successor as a representative sample;
- write v2 results as old confirmatory Package A results;
- use v2 eligibility to upgrade C3;
- replace a contract, `E_CONTRACT`, semantic mutant, syntactic baseline,
  or paired evidence.

If an eligible successor is found, the only later scientific door this
design opens is source-identity / Package A work on that one frozen
subject, under a later separate authorization. That later work is not
authorized here and still cannot upgrade C3 by itself.

## 14. Minimal defensive-control statement

Concrete failure scenario:
After observing the rank-1 failure, a human reorders, skips, or endlessly
appends subjects until an applicable result appears.

Harmed asset:
Prospective validity of the v2 eligibility search, the stopping rule, and
the interpretability of C3 evidence.

Trigger sequence:
Observe a prior result → hand-pick the next subject or enlarge the sample
→ find an eligible subject → hide the adaptive process.

Observable consequence:
The same v2 version, on the same inputs, uses a different successor
sequence or a different stopping position.

Why existing mechanisms are not enough:
Git and tests already bind predicate, inventory, and authority bytes.
They do not define a cross-subject successor sequence or stopping rule.
The old rank table recorded a first-subject selection order and then
forbade a second confirmatory subject. Using that table after the 10/10
result would disguise optional stopping as a pre-registered rule.

Minimal added control:
Use only this versioned design specification and its commit / SHA-256 as
successor/stopping authority. Do not create a second manifest or ledger.

Why this seam:
The unique future controller must verify this design identity before
opening any successor PBF site, then execute the sequence written here.

Proof method:
Rebuild the 22-row sequence from the frozen identities. Replacing,
deleting, reordering, or adding any subject must fail future preflight.

Maintenance cost:
One v2 specification and one future controller binding to its identity.

Future deletion condition:
If a later main protocol natively contains prospective successor and
stopping rules, absorb these rules and delete this independent v2
authority. Two effective successor/stopping authorities must not coexist.

### 14.1 Controller identity binding

Concrete failure scenario:
The same design and authority are reused, but a different
stop/skip/controller implementation produces a different attempted
sequence and is still labeled the same v2 run.

Harmed asset:
Successor chronology, stop-on-first-eligible, and reconstructability of
the official terminal.

Why Git, the design SHA, and the authority SHA are not enough:
They bind rule text and predicate/slot bytes. They do not bind the
actual execution loop or the write logic.

Minimal added control:
The terminal uniquely adds `controller_source_sha256` and requires one
independent small controller file. Do not create a second manifest or
ledger.

Why the whole `evidence.py` file is not bound:
That file contains many unrelated commands. Later unrelated edits would
force a needless rebind. The independent controller is a deeper and
narrower common seam.

Proof tests that the later run plan must include:

- the authorized original controller SHA passes;
- changing any controller byte makes terminal validation fail;
- changing the design SHA makes terminal validation fail;
- changing attempted order, a closure hash, or `terminal_status` makes
  terminal validation fail.

Maintenance cost and deletion condition:
One small controller SHA field. When a later main protocol absorbs the
v2 runner identity, delete this independent binding. Do not keep two
effective controller authorities.

## 15. C3 and claim-ledger interpretation

Ledger file: `research/evidence/p3_claim_ledger_v1.3.0.yml`
Ledger file SHA-256: `bf4979662697b2d0565bb70eec88b22673e84bee93b61234555342efb4082a68`

| Claim | Current `status` | Frozen `upgrade_condition` | This design |
|---|---|---|---|
| `C3_SEMANTIC_CONSTRUCT_DISTINCTNESS` | `blocked` | RQ2 paired evidence and uncertainty accounting complete | unchanged; not edited |
| `C2_CERTIFIED_MUTANTS_ACROSS_SCALES_TECHNIQUES` | `blocked` | RQ1 behavior-frame, profiling, diversity, and completeness gates | background only; not edited |
| `C4_FAMILY_AWARE_SMS_RESIDUAL_EXPLANATION` | `blocked` | Frozen kill matrix and all required adequacy views complete | still downstream; not edited |

Analysis-spec §11.2 still requires certified-mutant / syntactic overlap
and paired funnels. v2 eligibility labels are not those artifacts.

This design does not modify the claim ledger. Completing the design does
not upgrade C3. A later eligible subject does not upgrade C3. Exhausting
the 22 successors does not upgrade or falsify C3.

## 16. Implementation exclusions

This task does not:

- run applicability search;
- open any successor site, source, or archive;
- implement a controller, closer, schema, manifest, or ledger;
- create `scripts/p3_v3/prospective_applicability_search_v2.py`;
- modify existing authority, predicates, inventory, ranking, or closures;
- create a retry-authorization format;
- create a second applicability authority;
- create a JSON Schema file, subject-terminal file, or run manifest;
- write official or staging v2 output directories;
- recover a source archive;
- start Package A, contract, `E_CONTRACT`, mutant, baseline, or C3
  upgrade work;
- treat this document as a scientific observation.

The later controlled-run plan may specify how the unique controller binds
this design. It may not change the successor set, order, maximum
attempts, within-subject completion rule, eligibility definition,
stopping rule, failure semantics, or evidence ceiling.

## 17. Review checklist

- Status is `DESIGN_FOR_REVIEW`.
- Old path remains `C3_CONFIRMATORY_PACKAGE_A_PATH_CLOSED`.
- The 10/10 prior result is disclosed as already known.
- v2 purpose is `ELIGIBILITY_SEARCH`, not confirmatory continuation.
- Slice ID, authority commit, authority ID, and authority artifact SHA
  are the frozen values in §2.
- Successor universe is exactly 22; maximum attempts is 22.
- Ordinals are 1-22 and old ranks are 2-23.
- Neutral snapshot IDs, controlled subject source IDs, and controlled
  subject IDs are unique.
- Every successor has frozen slot count 10.
- Rebuilt rank 1 and ranks 1-5 match the old design.
- Rank 1 is excluded from v2.
- No successor site path, symbol, or span is recorded.
- Within-subject rule finishes all 10 slots even after the first
  `SITE_FROZEN`.
- Eligibility is `V2_APPLICABILITY_ELIGIBLE` or
  `V2_APPLICABILITY_INELIGIBLE` only after 10 valid closures.
- Infrastructure or partial failure is not ineligible.
- Controller is one pre-authorized invocation.
- Stop-on-first-eligible and cohort exhaustion are exclusive terminals.
- Preflight failure is `V2_PREFLIGHT_FAIL` and opens no subject.
- Execution failure is `V2_EXECUTION_FAIL`, with no retry format.
- Evidence ceiling is eligibility only.
- C3 remains `blocked`; claim ledger is not modified.
- No second authority manifest, ledger, or schema is created.
- The unique controller path is
  `scripts/p3_v3/prospective_applicability_search_v2.py`.
- The unique official terminal is `cohort-terminal.json` with the
  exact fields in §11.3 through §11.5.
- Failure does not write a scientific cohort terminal.
- Unique next task is `P3_C3_PROSPECTIVE_V2_CONTROLLED_RUN_PLAN`.

## 18. Unique next task

`P3_C3_PROSPECTIVE_V2_CONTROLLED_RUN_PLAN`

That later plan may contain only two consecutive but separately
authorized slices:

1. Minimal controller implementation and focused validation.
2. After the controller commit, this design commit, this design-file
   SHA-256, and the authority identity are fixed, one official
   controlled run.

Completing the implementation must not automatically start the official
run. The official run still requires a separate explicit authorization.
The run plan must not change these v2 scientific rules. It may not open
a successor site in the planning slice, and it may not treat the plan as
a C3 result.

This design waits for human review. It does not authorize controller
implementation or v2 execution.
