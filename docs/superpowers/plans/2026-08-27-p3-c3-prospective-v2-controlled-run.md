# P3 C3 Prospective Applicability Search v2 Controlled Run Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` or
> `superpowers:executing-plans` for Slice A only. Slice B requires a new,
> explicit user authorization after the implementation commit is fixed.

**Goal:** Implement the smallest production controller for the frozen v2
eligibility search, verify it without opening successor sites, then stop before
the separately authorized official run.

**Architecture:** One narrow controller source file reuses the existing
applicability authority and closer. It derives and validates the fixed
22-subject sequence, completes ten frozen slots per opened subject, stops on the
first eligible subject, and writes existing closure objects plus one canonical
cohort terminal. No second predicate, authority, manifest, ledger, or schema
file is introduced.

**Tech Stack:** Python 3, existing `p3_v3` canonical artifact helpers, pytest,
Git.

---

## 0. Authorization boundary (hard stop)

```text
STOP_AFTER_CONTROLLER_IMPLEMENTATION=true
FORMAL_V2_RUN_NOT_AUTHORIZED=true
```

This plan has two separately authorized slices:

| Slice | Name | Authorized by this plan | Success terminal |
|---|---|---|---|
| A | Minimal production controller + focused validation | Yes, after human review of this plan | `V2_CONTROLLER_IMPLEMENTATION_PASS` |
| B | One official v2 controlled run | **No** | scientific terminals in §17 |

`V2_CONTROLLER_IMPLEMENTATION_PASS` does not authorize Slice B.
Completing any Task 1–3 commit must not invoke the official command.
Slice B is marked `DO_NOT_EXECUTE_WITHOUT_SEPARATE_AUTHORIZATION` in §15.

Cursor Cloud commands use `python3`, `/workspace/.venv/bin/python`, `git`,
`sha256sum`, and `jq`. Do not use `rtk`. Do not install packages.

---

## 1. Frozen baseline

Worktree: `/tmp/p3-c3-applicability-authority`  
Branch: `codex/p3-c3-applicability-authority`  
Implementation start HEAD (design commit): `4ea6f05b44c76ebaa031277872c3711cdd1953eb`

Approved design:

`docs/superpowers/specs/2026-08-27-p3-c3-prospective-v2-successor-and-stopping-rule-design.md`

Design file SHA-256:

`bb0ca5d20f3fec61257b2ba524585fe899d28c8b8963c61273a8ffeb857aa6c6`

Inherited scientific facts (do not edit):

- Old path remains `C3_CONFIRMATORY_PACKAGE_A_PATH_CLOSED`.
- Prior result is already known: rank 1, 10/10 `NOT_APPLICABLE`,
  `SITE_FROZEN=0`, closure commit `e6f9e84a5a71900e0fb6f0655393c5e1b613b6a5`.
- Exact retained observation: 该主体在冻结 authority 下 10/10 slots 不适用。
- v2 purpose is `ELIGIBILITY_SEARCH` only.
- C3 remains `blocked`. Claim ledger is not modified.
- Finding an eligible successor does not upgrade C3.

Before Task 1, re-check:

```bash
cd /tmp/p3-c3-applicability-authority
git rev-parse HEAD
git branch --show-current
git status --porcelain=v1 --untracked-files=all
git diff --check
git ls-remote --heads origin refs/heads/codex/p3-c3-applicability-authority
sha256sum docs/superpowers/specs/2026-08-27-p3-c3-prospective-v2-successor-and-stopping-rule-design.md
```

Required: HEAD, branch, and remote SHA equal `4ea6f05b44c76ebaa031277872c3711cdd1953eb`
plus only this plan file until Task 1 starts; after Task 1 starts, HEAD moves
only by the three Task commits below. Worktree otherwise empty. Design SHA
unchanged. If the design SHA or scientific rules differ, stop:

`V2_RUN_PLAN_BASELINE_CONFLICT`

Do not rebuild or edit the design.

---

## 2. File map (closed)

Slice A may only:

- Create: `scripts/p3_v3/prospective_applicability_search_v2.py`
- Create: `tests/p3_v3/test_prospective_applicability_search_v2.py`

Do not modify:

- `src/p3_v3/applicability_predicates.py`
- `src/p3_v3/slot_inventory.py`
- `src/p3_v3/bridge_and_frames.py`
- `src/p3_v3/artifacts.py`
- `scripts/p3_v3/evidence.py`
- `data/p3_v3/phase2/applicability-authority.json`
- `data/p3_v3/phase2/slot-inventory.json`
- `data/p3_v3/protocol/applicability-predicate-registry.json`
- any existing closure under `data/p3_v3/phase2/site-closures/`
- the approved design
- `research/evidence/p3_claim_ledger_v1.3.0.yml`

Do not create a JSON Schema file, second authority, run manifest, second
ledger, or subject-terminal file.

Survey result: the approved design is implementable with these two files.
The controller imports existing loaders, the existing closer, existing
canonical helpers, and existing `_sites(...)` to attach `site_id` and apply
canonical site order. That import is reuse, not a second closer and not a
modification of `bridge_and_frames.py`.

If implementation later needs a third file or an edit to a frozen module,
stop instead of expanding the map:

`V2_RUN_PLAN_SCOPE_CONFLICT`

---

## 3. Official command and CLI ban

The future official command is exactly:

```text
PYTHONPATH=src python3 scripts/p3_v3/prospective_applicability_search_v2.py
```

`main()` accepts no user arguments. `sys.argv` must be exactly
`[script_path]`. Any extra token, including `--help`, `--dry-run`,
`--preflight-only`, `--resume`, `--retry`, `--skip`, `--start`,
`--max-attempts`, `--output-root`, `--authority`, `--design`, or an
applicability map, is `V2_PREFLIGHT_FAIL` and must not open a successor PBF
or write official output.

Tests import the controller module and call the listed functions. Tests must
not add production CLI flags to inject fixtures.

Slice A must never execute the zero-argument official command against the
real worktree. That command is Slice B only.

---

## 4. Test runtime

Preferred:

```text
cd /tmp/p3-c3-applicability-authority
PYTHONPATH=/tmp/p3-c3-applicability-authority/src \
  /workspace/.venv/bin/python -m pytest <args>
```

This worktree is on `sys.path` via pytest's rootdir, so
`from scripts.p3_v3.prospective_applicability_search_v2 import ...` works the
same way `tests/p3_v3/test_cli.py` imports `scripts.p3_v3.evidence`.

If that interpreter cannot `import pytest`, check:

```text
cd /tmp/p3-c3-applicability-authority
PYTHONPATH=src python3 -m pytest <args>
```

If both fail: `TEST_RUNTIME_UNAVAILABLE`. Do not install dependencies.

Do not run the full pytest suite.

---

## 5. Locked production constants

Write these literals in the controller. Do not read them from argv, env, or
a second manifest.

```python
from __future__ import annotations

import hashlib
import json
import os
import stat
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from p3_v3.applicability_predicates import (
    close_slot_with_authority,
    load_applicability_authority,
)
from p3_v3.artifacts import (
    EvidenceError,
    canonical_json_bytes,
    canonical_sha256,
    file_sha256,
    read_canonical_json,
    read_canonical_regular_json,
    read_regular_file_snapshot,
    validate_exact_object,
    validate_sha256,
    write_canonical_json,
)
from p3_v3.bridge_and_frames import _sites
from p3_v3.slot_inventory import (
    load_phase1_identity_records,
    project_controlled_subject_ids,
)

SLICE_ID = "p3-c3-prospective-applicability-search-v2"
DESIGN_COMMIT = "4ea6f05b44c76ebaa031277872c3711cdd1953eb"
DESIGN_FILE_SHA256 = "bb0ca5d20f3fec61257b2ba524585fe899d28c8b8963c61273a8ffeb857aa6c6"
AUTHORITY_ARTIFACT_SHA256 = "30b08271eafdead14a06707b461f108c1ec5a53eb5d2859a37b2cd6238e20214"
PRIOR_CLOSURE_COMMIT = "e6f9e84a5a71900e0fb6f0655393c5e1b613b6a5"
AUTHORITY_ID = "p3-v3-phase2-applicability-authority-v1"
AUTHORITY_SCHEMA = "p3-applicability-authority-v1"
AUTHORITY_ORIGIN_COMMIT = "03a032fe6cb490930083ab2517ee2dcf2bb8c747"
MAXIMUM_ATTEMPTS = 22
SLOTS_PER_SUBJECT = 10
CLOSED_RANK1_NEUTRAL_SNAPSHOT_ID = (
    "6e05301ec7ec79d16233c086e5fc4a0b714e82a6ec8d6a86ca1218be67135062"
)
CLOSED_RANK1_CONTROLLED_SUBJECT_ID = (
    "942d190c2c3972a6a6e9feb6ef5d4abee1d939cb0aa9ee676232ab0184dead09"
)
CLOSED_RANK1_CONTROLLED_SUBJECT_SOURCE_ID = (
    "12925a111a2d920ecfb2b0669969b61e7b1d4c66962b793417082bbec161b54e"
)

DESIGN_RELPATH = Path(
    "docs/superpowers/specs/2026-08-27-p3-c3-prospective-v2-successor-and-stopping-rule-design.md"
)
AUTHORITY_RELPATH = Path("data/p3_v3/phase2/applicability-authority.json")
INVENTORY_RELPATH = Path("data/p3_v3/phase2/slot-inventory.json")
REGISTRY_RELPATH = Path("data/p3_v3/protocol/applicability-predicate-registry.json")
SLOT_IMPL_RELPATH = Path("src/p3_v3/slot_inventory.py")
PREDICATE_IMPL_RELPATH = Path("src/p3_v3/applicability_predicates.py")
CANONICALIZATION_IMPL_RELPATH = Path("src/p3_v3/artifacts.py")
SITE_POLICY_RELPATH = Path("data/p3_v3/protocol/site_policy.md")
OPERATOR_CATALOGUE_RELPATH = Path("data/p3_v3/protocol/operator_catalogue.md")
BRIDGE_RELPATH = Path("data/p3_v3/p12_intake/verified_bridge.json")
PHASE1_OUT_RELPATH = Path("data/p3_v3/phase1_frames/out")
OLD_CLOSURE_RELDIR = Path(
    "data/p3_v3/phase2/site-closures/"
    "6e05301ec7ec79d16233c086e5fc4a0b714e82a6ec8d6a86ca1218be67135062"
)
OFFICIAL_RELDIR = Path("data/p3_v3/phase2/prospective-applicability-search-v2")
STAGING_RELDIR = Path("data/p3_v3/phase2/prospective-applicability-search-v2.staging")
CONTROLLER_RELPATH = Path("scripts/p3_v3/prospective_applicability_search_v2.py")

AUTHORITY_FILE_SHA256 = "80702537fab92c09506c9e94f8fb6a14e6f52cfcf23e1ae2f134be1d15a471a5"
INVENTORY_ARTIFACT_SHA256 = "5c7f2dae8b0b7fd72926e2569354dbf6e878186f69d512e259e6034026dd0e27"
INVENTORY_FILE_SHA256 = "5846aa3eccb55958955e42b298177cf7692603608ab5eed99929b01d39b4a967"
REGISTRY_ARTIFACT_SHA256 = "26835b99baefad1f8eba12d8196eb34f1567e182d5fdb12767217838276c57e1"
REGISTRY_FILE_SHA256 = "ce05e552122a871d4acb81d2f071d0fa1653228232d5ab7446772206c0b32218"
PREDICATE_IMPL_SHA256 = "6c0c03b43ae895b331122f462f0f778e4f35093b55ff5395067ce6c73c2837c5"
SLOT_IMPL_SHA256 = "ca6365f268ff418b31b0c770998d070db1571d54d82ce7e924810b0d0c2352f1"
CANONICALIZATION_IMPL_SHA256 = "9f619073626003caa7d724a19655b5abae92318afd3f656494a0843613b6f57a"
SITE_POLICY_SHA256 = "9772430e0a2539667a9aaa776b47ecae92a7830e19ec0a6e75a5dda9cfdfdcf7"
OPERATOR_CATALOGUE_SHA256 = "060671a031c36699fe63c7376afbb4714c84b25eab28f06445804ee8d232a635"

TERMINAL_SCHEMA_VERSION = "p3-c3-prospective-applicability-search-v2-terminal-v1"
SCALE_RANK = {"S": 0, "M": 1, "L": 2}
FORBIDDEN_LEAK_KEYS = {
    "path",
    "symbol",
    "start_line",
    "start_col",
    "end_line",
    "end_col",
    "source",
    "span",
    "contract",
    "patch",
    "profiling",
    "technique",
    "outcome",
    "timing",
}

ATTEMPTED_SUBJECT_SCHEMA = {
    "successor_ordinal": int,
    "neutral_snapshot_id": str,
    "controlled_subject_source_id": str,
    "controlled_subject_id": str,
    "eligibility": str,
    "closures": list,
}
TERMINAL_CLOSURE_ROW_SCHEMA = {
    "slot_id": str,
    "state": str,
    "site_id": (str, type(None)),
    "closure_artifact_sha256": str,
}
COHORT_TERMINAL_SCHEMA = {
    "schema_version": str,
    "slice_id": str,
    "design_commit": str,
    "design_file_sha256": str,
    "authority_artifact_sha256": str,
    "controller_source_sha256": str,
    "prior_closure_commit": str,
    "terminal_status": str,
    "attempted_subjects": list,
    "first_eligible_successor_ordinal": (int, type(None)),
    "first_eligible_neutral_snapshot_id": (str, type(None)),
    "artifact_sha256": str,
}
STDOUT_SUMMARY_SCHEMA = {
    "status": str,
    "slice_id": str,
    "design_commit": str,
    "controller_source_sha256": (str, type(None)),
    "attempted_count": int,
    "first_eligible_successor_ordinal": (int, type(None)),
    "official_terminal_written": bool,
}
```

Frozen 22-row successor identity and order (design §3). Copy these values
exactly. Do not sort, skip, or replace any row at runtime except by failing
closed when a rebuild differs.

```python
FROZEN_SUCCESSOR_ROWS: tuple[dict[str, object], ...] = (
    {
        "successor_ordinal": 1,
        "old_rank": 2,
        "scale_class": "L",
        "total_effective_lines": 258766,
        "pbf_site_count": 4028,
        "frozen_slots": 10,
        "neutral_snapshot_id": "74cdc825c3c728c25f5ea857af1565350515a4e631fb0a874c26e810ec437886",
        "controlled_subject_source_id": "e5f21a7d067d641d0a20bfc57c61e630d6f7588ef30235cea49c9a9cf950c7a7",
        "controlled_subject_id": "89b0e6791c611b465b9216e833e0c526a53ffd6946b5cd20de045e3641f43914",
        "pbf_file_sha256": "a740d5019a19ee354f07e73e7c542dd1d79fb8969a2af48d5ef7975e534da4d3",
        "pbf_artifact_sha256": "75ff02923b851a03c9f6e83b6786da591dcd10c3143527f1691ab913318f4441",
    },
    {
        "successor_ordinal": 2,
        "old_rank": 3,
        "scale_class": "L",
        "total_effective_lines": 272416,
        "pbf_site_count": 9286,
        "frozen_slots": 10,
        "neutral_snapshot_id": "822470056d804eebf56b73ea7d7ad7a31099047760b88f561cad77e53fdbf363",
        "controlled_subject_source_id": "6dfbd187d6520f0bd52016beb485f2b8f17c45637ce1c6ad9528bbccb66ac990",
        "controlled_subject_id": "e1af9d59c570c0d5c006124ec9f96573a3dd46cb81e170a85f903a961ada530d",
        "pbf_file_sha256": "c7b70f05a688c7be061b7525a5a306aa6a45afee8781a9abf786aff933ebd63f",
        "pbf_artifact_sha256": "7dff0c0bc10a26e9a6003a522a1cf0bf68790624c8b008df23630ee4d77a77b0",
    },
    {
        "successor_ordinal": 3,
        "old_rank": 4,
        "scale_class": "L",
        "total_effective_lines": 299333,
        "pbf_site_count": 11066,
        "frozen_slots": 10,
        "neutral_snapshot_id": "734d6accd77800469372ff6a578920ec2545e1119c037457628d16cb79c02271",
        "controlled_subject_source_id": "11bb24a1429cbf03eeb863ba7148f41e656a8fea7a063d80415ee2c33cf24574",
        "controlled_subject_id": "3528152e3952c07a1e255eee71a07d3f91d140e846737782a8de9633a34eaacb",
        "pbf_file_sha256": "532d62c2159d7c81a6fed9c9d4f31e28f27e61b677f704c06e34b8895f006f37",
        "pbf_artifact_sha256": "fe9c2cfc36e1a80cb6e5f987e5c56b6a7ef423f39af95594f65486036c0dd055",
    },
    {
        "successor_ordinal": 4,
        "old_rank": 5,
        "scale_class": "L",
        "total_effective_lines": 314450,
        "pbf_site_count": 2048,
        "frozen_slots": 10,
        "neutral_snapshot_id": "b3e0d3cd4e81efb817dc0f2805d855d9c8a82e1bf483e2870e244190716349b3",
        "controlled_subject_source_id": "1c479b03eaa51298b396f8edd4401d65062448489df790bcd7e3c24bc5825640",
        "controlled_subject_id": "038f9ae4b295b98914a4d1f5799db6bda686779ee3dded3e9ef0d0bdb715f183",
        "pbf_file_sha256": "fede8e4b0269c8afd080b45a2936fc436eb026a252ca50697248dc227c97245a",
        "pbf_artifact_sha256": "a6ddb14c3499e1d031bcde6c2d82c18145305f7f8d2e1e27f85a2d43454980f5",
    },
    {
        "successor_ordinal": 5,
        "old_rank": 6,
        "scale_class": "L",
        "total_effective_lines": 372366,
        "pbf_site_count": 2312,
        "frozen_slots": 10,
        "neutral_snapshot_id": "3019d9a64c261c22d1d7af17cc3946dfc29f159d51eabd3e238a0f169d5fac12",
        "controlled_subject_source_id": "c0dac5b06ec432e720310337fd465a86ab1ff7c1b3a86ce182bdfda2c721291a",
        "controlled_subject_id": "e7b69c4b571d4824d12e039cab07ac922161192b4da1356599eb9510d6275d1e",
        "pbf_file_sha256": "f4ab2c8aca30602fd38384a7e45b3c48085afb0a33f224b7796abeb39495bc79",
        "pbf_artifact_sha256": "b10bc7fa1c6ce3e703480f5ffb6902176de091c6c0579bfe55543bc8fb6c3bbd",
    },
    {
        "successor_ordinal": 6,
        "old_rank": 7,
        "scale_class": "L",
        "total_effective_lines": 382261,
        "pbf_site_count": 14029,
        "frozen_slots": 10,
        "neutral_snapshot_id": "b2bfbf1e0511e6e7b01e22853da91b66a2801a6ff7997ed48ac78acef5886f01",
        "controlled_subject_source_id": "6464893a5a2a64fe05118f3da8c59a6d583110f3c41dc50383df596f1b177bc9",
        "controlled_subject_id": "d386a35091e9053fbb3a0124257777c3791469b25186f9ee4b125ef62f938b46",
        "pbf_file_sha256": "89d836be994c11bc4404e86cee3e67fa553525ea1524023a9ca473aaad147fb2",
        "pbf_artifact_sha256": "6eb04ce3f2a92ddc0b2c2b6052f5c543ca24b93f3b5e4b771b9af902699bbfa8",
    },
    {
        "successor_ordinal": 7,
        "old_rank": 8,
        "scale_class": "L",
        "total_effective_lines": 389743,
        "pbf_site_count": 6496,
        "frozen_slots": 10,
        "neutral_snapshot_id": "3c6e698ff35c59ec23d2ccbe722d7c0d40f553cb03d53f4b69e1ad2125343d02",
        "controlled_subject_source_id": "77ab955fae5d9768f35eff6b32f19b09920efeae06984fa297165923cd34e47b",
        "controlled_subject_id": "ff6251cb3d23ab1e49d549054b4dba416fdbec1e2fd8d969c18143ea4fae751f",
        "pbf_file_sha256": "2232d2ebc59f7fd285352bec0498bcf2abca14b75b317d112265ee5a6912cf90",
        "pbf_artifact_sha256": "0ffe0dfcdceaaf6b5fe46f18b8956441f1331a63a24be0824018828215110daf",
    },
    {
        "successor_ordinal": 8,
        "old_rank": 9,
        "scale_class": "L",
        "total_effective_lines": 459888,
        "pbf_site_count": 10811,
        "frozen_slots": 10,
        "neutral_snapshot_id": "4e7e9556b3d621681c88c82f26cd95f5604d7a8b85cc56bf7e6d4db5a274f38b",
        "controlled_subject_source_id": "667f66bbdb3b392af99b044181dcfa861040546fc5550906e30fca2f9aabb5d0",
        "controlled_subject_id": "0fefefc546f7c4519d036849a85279cc7d3aa00fe88d6ed5e259209769b5bb48",
        "pbf_file_sha256": "168bc06564842818224dec76e97287d33d19aea9b60482d2ab674b9e89f7092e",
        "pbf_artifact_sha256": "b5fc46928d1dd5c85a60c36f2e2df2b35c97b8163bc9c14eda9667e1120c0503",
    },
    {
        "successor_ordinal": 9,
        "old_rank": 10,
        "scale_class": "L",
        "total_effective_lines": 532232,
        "pbf_site_count": 22438,
        "frozen_slots": 10,
        "neutral_snapshot_id": "24ab4a18534a3125f49060cc83fca0ea4c66646f701eb5e4091097a7ae1f9d8b",
        "controlled_subject_source_id": "bfaa320be236999863943c8521dd7f3f0f17c2d7f696d22a3667d4c7f021ac82",
        "controlled_subject_id": "6e71e0c72a29aa77a6c83ea81d39af7801b6a6bad3dd053a6ec7eb6df4bbd6db",
        "pbf_file_sha256": "1bd60872bdce13aa6395fc497656ecfcfd6d416d5597bd8608efcfb6f8a02e29",
        "pbf_artifact_sha256": "4bc3aee714b20e2e82ac89c301fba1b5144c6b7e39d2bc2f5a2dd18234929027",
    },
    {
        "successor_ordinal": 10,
        "old_rank": 11,
        "scale_class": "L",
        "total_effective_lines": 557567,
        "pbf_site_count": 23842,
        "frozen_slots": 10,
        "neutral_snapshot_id": "9a76cacce39b2908de91ee2d1ad30c9a6564175f3ab298dbd1d1e0285b386e21",
        "controlled_subject_source_id": "257a39a07c314ef51c4582475730db5dc2387f80bbbfbf518fc2a33d6dd1ffb6",
        "controlled_subject_id": "d81ff7e27069d30df42111cedb08598012076173d94e5f84dfeb1ee2a124e2c8",
        "pbf_file_sha256": "e9fceb133d1cb2d88527a21636776a16ff0300ba8d6efa4dc177e93494d6a907",
        "pbf_artifact_sha256": "1117cb4c1f5417354096a66fb9518c25332eb657e4e95a35a4b0a97c65667b94",
    },
    {
        "successor_ordinal": 11,
        "old_rank": 12,
        "scale_class": "L",
        "total_effective_lines": 557723,
        "pbf_site_count": 23844,
        "frozen_slots": 10,
        "neutral_snapshot_id": "643985b0b045d17be89ebce2defe02cd4953191330bb79db00c36115e34eaa1b",
        "controlled_subject_source_id": "faa1bb211d1677c40c6a2cffc69701fc9458bd1b4f6827705e8b40d2b625a446",
        "controlled_subject_id": "35d537a7639d6bd8966abb2a21f453dbc7d648876ab449d264c9a4690748af20",
        "pbf_file_sha256": "b526da6b9070f4615694711b51e71c326d4346224eea5e3dcbdb12ac61e72df7",
        "pbf_artifact_sha256": "31d662b4ed318b20630054f4e1397120f97656cd3c3bb14eabce2d911ebb0346",
    },
    {
        "successor_ordinal": 12,
        "old_rank": 13,
        "scale_class": "L",
        "total_effective_lines": 578758,
        "pbf_site_count": 24227,
        "frozen_slots": 10,
        "neutral_snapshot_id": "1f67b3f303a09aa91413a2b5451d156cdcd76d425833bdd12669a7d1e140ca72",
        "controlled_subject_source_id": "bf870e2e8a7b10ea91fa9d03c223f041eee7477c7a84ce54f5139ff15d173c45",
        "controlled_subject_id": "43a6370a0fe446cfc2895e283a19c01fed0c94dd2da5f69f14b3ec64ed32bad2",
        "pbf_file_sha256": "a41120f5dfd76a6498d0233fdf2e578090e1755ff36d48e2cd2565d3ef3c4b5a",
        "pbf_artifact_sha256": "d71a01c49bbad08fe56a41549fb14bd768528c60680ece7ac241b170bc753f3f",
    },
    {
        "successor_ordinal": 13,
        "old_rank": 14,
        "scale_class": "L",
        "total_effective_lines": 584475,
        "pbf_site_count": 24378,
        "frozen_slots": 10,
        "neutral_snapshot_id": "d782e757e28052ffc81819c610119dd6ce0176be1b508773d7f43df0aa9cf766",
        "controlled_subject_source_id": "ebc45688ba350b2ba040d79b0c04f42ceca51c574be03da70d86a68818cc09ba",
        "controlled_subject_id": "38b6c8236a5717b3ad99240879cc97221b1a58ad6ccb02e74a0747c4c725c780",
        "pbf_file_sha256": "afdb0a8646645fc8edccfbc6e88d1969c0851917c42d3790e6e0c77e70f29603",
        "pbf_artifact_sha256": "2fc4d78dfc99ac3fe53ecea4edc2166fa95a82e34d65620699a546445da4fdd2",
    },
    {
        "successor_ordinal": 14,
        "old_rank": 15,
        "scale_class": "L",
        "total_effective_lines": 585286,
        "pbf_site_count": 24425,
        "frozen_slots": 10,
        "neutral_snapshot_id": "3640321076e7abba42862bc92045f019333eb0f92f477f6dcabaddf937681710",
        "controlled_subject_source_id": "080c4f0bf035a7297803fa723fc667295538f88288ad13daecba4e2965eb72c0",
        "controlled_subject_id": "7ead91b227c321fd6430a9f9c7f10cf888de0c98848d0b1d9cd05d04896843a5",
        "pbf_file_sha256": "7199d8dc8510cc644860106fd96ee369a495a3df95f5fc9eaa32ba1df2276a85",
        "pbf_artifact_sha256": "b534d0b13a0341f913665bfb989225c7cbf458a0bdce202fe9811f62af471f1d",
    },
    {
        "successor_ordinal": 15,
        "old_rank": 16,
        "scale_class": "L",
        "total_effective_lines": 675990,
        "pbf_site_count": 5994,
        "frozen_slots": 10,
        "neutral_snapshot_id": "92b4ec544c5586ae7458a007c1ef12c65b70c7668128f0ef95006c5d45091b0f",
        "controlled_subject_source_id": "130e24e50e73fe2e25e3c0a453c8e8e269adf1471ac7899ef4b7307b54ef3b60",
        "controlled_subject_id": "25ad02f3b77e0e325385ce63bf0f49dc1aff6081a7b2373f1fcae68c8119a202",
        "pbf_file_sha256": "9095874da884d962cc33561fd1a74d1a20c9da13a7f16f82fae1fa4681c70c71",
        "pbf_artifact_sha256": "72ead1b9087c20aa0ee28de990d3667cdcde6b93a9e814aaf6cdbddcd524540a",
    },
    {
        "successor_ordinal": 16,
        "old_rank": 17,
        "scale_class": "L",
        "total_effective_lines": 788145,
        "pbf_site_count": 6715,
        "frozen_slots": 10,
        "neutral_snapshot_id": "aa19a201f5819c88d7de328c09159867ec6043e2b2f254c267a0cf649ba29176",
        "controlled_subject_source_id": "714f53ef8ae2e4f296b09042e985e8f63f980d8f9e4439c9bcaefb3cc88087bb",
        "controlled_subject_id": "072ad35799114749ca393fa74b3defe9e60c76560450bd9ffa6b6bedbcf83805",
        "pbf_file_sha256": "e28a88c3e8f5b45a4f2da416df475c604159e9c3fb432f9e4d6278f5c18782a7",
        "pbf_artifact_sha256": "b033449bdfe17705d41779bde24bbaecc585caee8d47505790af7780c3ea55c1",
    },
    {
        "successor_ordinal": 17,
        "old_rank": 18,
        "scale_class": "L",
        "total_effective_lines": 818032,
        "pbf_site_count": 6671,
        "frozen_slots": 10,
        "neutral_snapshot_id": "a6fc16a5dd71bd0ee219d6d21ec1ac7d08b7b0d12fd113b525f537cdb16ae8c5",
        "controlled_subject_source_id": "aa441a5251b2548885d91d433d8f1cd013c2298856b2fc54082bf20072059d39",
        "controlled_subject_id": "7e1c0f1a4a5d83730c57088a70763fdaeb452aff00e28a51fa08772157ac0632",
        "pbf_file_sha256": "943533ac3b16964ffc4560baccc5423f823b29aa61516d1d8e9f70ca64353c98",
        "pbf_artifact_sha256": "5e179b38fe494da2762889a2570f7ce433ccb45806a275d094360b8f08cd747d",
    },
    {
        "successor_ordinal": 18,
        "old_rank": 19,
        "scale_class": "L",
        "total_effective_lines": 921535,
        "pbf_site_count": 23732,
        "frozen_slots": 10,
        "neutral_snapshot_id": "75c0e11c4b655a3122b438bb609fdbe7d845ef333c3f212e6c38df6deb730a63",
        "controlled_subject_source_id": "cb8d47f1e3d97ef5d912b7456f365a2c74be1e184bf028599ad82db365c312a6",
        "controlled_subject_id": "821b57e8a17272636dd08d4a6a96cda3965a221ced4fcc225c613648668a28b6",
        "pbf_file_sha256": "77afeafb73de4dc36ccf4c08053bb12317d22a472ef73064d01d2cbaf0e561b0",
        "pbf_artifact_sha256": "9dea8204ccea78b6092708580b12a8b37e4fdb2d3231d2c36193c6a67a73881a",
    },
    {
        "successor_ordinal": 19,
        "old_rank": 20,
        "scale_class": "L",
        "total_effective_lines": 967764,
        "pbf_site_count": 24785,
        "frozen_slots": 10,
        "neutral_snapshot_id": "bb43dfe28f9b3aa58c6daffcc2a50a04b712725c27d386ebc8b4ca139d57e7e2",
        "controlled_subject_source_id": "45a05ea410cc3de9bcf66d3a883bc127f38b9e3b98ecec6c3270a5da1708d3d3",
        "controlled_subject_id": "f5cea2872cbcb90333f087a87f3fe50cfbd1bf79c2de420e6bacec0a1d442b08",
        "pbf_file_sha256": "6690ba09d0b81b65340816feb5685208a730ae549feeb785143d93a0e03ed705",
        "pbf_artifact_sha256": "905c92759aaf8bc489ce010d1d1d56047f162d6684c4d3df604eae41dc3808d8",
    },
    {
        "successor_ordinal": 20,
        "old_rank": 21,
        "scale_class": "L",
        "total_effective_lines": 972891,
        "pbf_site_count": 2409,
        "frozen_slots": 10,
        "neutral_snapshot_id": "f5f00bc450d4daba54f08269c336f5d76d785df620416b1acd080ee14c2496a7",
        "controlled_subject_source_id": "bb34466e627756c6c6c63720392b861d47d65cd767af2999b50df4b2f4904e41",
        "controlled_subject_id": "2fc0e80d3659a765ee931208918d9da1f83cab746476f8463a138d90e4aee455",
        "pbf_file_sha256": "f4e5767abaa6e90d128cb1833a94f8bf9b02afc6d5a2d13d418f6343026c5290",
        "pbf_artifact_sha256": "b67b5524c2acf918ea517d257efac50115659e99d42a30b5f55176de992dd8ea",
    },
    {
        "successor_ordinal": 21,
        "old_rank": 22,
        "scale_class": "L",
        "total_effective_lines": 2776117,
        "pbf_site_count": 57397,
        "frozen_slots": 10,
        "neutral_snapshot_id": "84b70a11f582eab3ce3c5029b2c17cf916e354df09184224875a3ba53000974a",
        "controlled_subject_source_id": "33fe48fd8a0bd0d00e0b52ec4c586d5ab0190f7447ddd9188460e32370f2e748",
        "controlled_subject_id": "0f6ed8e3d9d1107fe96b7f8b2686eaace9dec1cf78235f380d36b3912145ffc2",
        "pbf_file_sha256": "971313d8fd5e8999389802780899701e03e876c5104093b00db4590fdd41bd36",
        "pbf_artifact_sha256": "a85086e0c52d989827dec9040ea129f2bbee39fcff1580bf9848cef481cd7df4",
    },
    {
        "successor_ordinal": 22,
        "old_rank": 23,
        "scale_class": "L",
        "total_effective_lines": 4043349,
        "pbf_site_count": 62240,
        "frozen_slots": 10,
        "neutral_snapshot_id": "494c35cb94f9fd4db2559ad0c7da45f54ca17ac5b3a8ab8d481142b1349280de",
        "controlled_subject_source_id": "14bb2817b2dc0322ebb19f22f864481ff257dcb75bd7e193908fba1c5d327541",
        "controlled_subject_id": "5b811ed080bcce73b009712b8038eaf21f66de1fc397275e0019b6a93c6e0379",
        "pbf_file_sha256": "cf18054b2c574bd59ddc9a4640bfb8156dfeb72b1fe74a8f6f01f7e5cab89e5f",
        "pbf_artifact_sha256": "9deaca70691a71539b900e58c52e86bae4711dd21485f2f4d3e399dbaaa957a5",
    },
)
```

PBF path for a successor:

```text
data/p3_v3/phase1_frames/out/public-behavior-frame-<neutral_snapshot_id>.json
```

Source-scale and workload paths used only for identity rebuild:

```text
data/p3_v3/phase1_frames/out/source-scale-<neutral_snapshot_id>.json
data/p3_v3/phase1_frames/out/profiling-workload-<neutral_snapshot_id>.json
```

Frozen old rank-1 closure file SHA-256 values (byte identity, not site
content):

```python
PRIOR_RANK1_CLOSURE_FILE_SHA256: dict[str, str] = {
    "slot-closure-07effd0eec12658b7206f944a61f6fe29973197baf94ee19a589aaaf6ec3043b.json":
        "20f4c6027cfb328d6876b1bd5670fb81451d168897ea471ba43e1e4d0823a1ed",
    "slot-closure-094c034448d192bead39afc0d76f1d7e54997c9d6db0e49b5b48aae9b5942a28.json":
        "aa713287d9d7045113fee4b6374c262b3f3db996b043297c52ec7bdfdefcca37",
    "slot-closure-1d22cc0f7f6e9d686e378908158ab3a2b2fbbaf64d0e09568a43d500b8f42666.json":
        "e78617722a6b63dd7abe6590b6ec687a68d40df2e950c24b8c05796963e864ed",
    "slot-closure-35ddd421a50d3c575b71cf6a896fc859a8280aacae6c105f245507977141d6ce.json":
        "e31fb44f26092f219b077bd57576589fef1293ddf778b6d46f5cb62feb6e2579",
    "slot-closure-4e1e1a5c23361193c123d86f28b6693600c70043441c0e013fbd3de9a2318cb5.json":
        "260c7f524f2a537a6d948c7340f20040950bb17008f04bcecf898428ced8ba8f",
    "slot-closure-55168a78fecc75049a977d76f608efb9c728aecd7e223c179f56b3e48422dff5.json":
        "ab3669f35ff27419748ce2861e2d94fd1cc7b4a0a7dd6fda9024c797bc5679aa",
    "slot-closure-55436729408cc06ad993d770163dcb0d6ff2d27753b9740b08cba639b7a84ca1.json":
        "a0235ee0129bfb24030cb4345c45835b6f314c1a74c15751ef135169c35f7961",
    "slot-closure-95c9f01bddd92c56a3fdacd6c4ed22835a0a2e81950b4b4adf4a1dca6549e2cb.json":
        "77b6f909c2a1ee81244ff6d3306f47f1526a3fb5ad303d9447f4f78278f097e1",
    "slot-closure-dcc25cd2d13b0b34c5df58bc01cb46a1e660a193ed4c88c23d3dc6a1899ab588.json":
        "db9f83e071ff2657e822a5785837e5b64a490f6f81291636c1c50ceabbcf535c",
    "slot-closure-e648bff0d110061ed7b9c90c8f5b2401496eb2cbae6935e27562a1f5ee64b1ce.json":
        "f9e490bd0c998ac11e6173da6dce32312124a35cbead8199ffdbd6c07460a9e3",
}
```

---

## 6. Final function signatures

These are the complete public/internal functions in the controller file.
No additional production module is added.

```python
def pbf_path(repo_root: Path, neutral_snapshot_id: str) -> Path:
    return Path(repo_root) / PHASE1_OUT_RELPATH / (
        f"public-behavior-frame-{neutral_snapshot_id}.json"
    )

def source_scale_path(repo_root: Path, neutral_snapshot_id: str) -> Path:
    return Path(repo_root) / PHASE1_OUT_RELPATH / (
        f"source-scale-{neutral_snapshot_id}.json"
    )

def workload_path(repo_root: Path, neutral_snapshot_id: str) -> Path:
    return Path(repo_root) / PHASE1_OUT_RELPATH / (
        f"profiling-workload-{neutral_snapshot_id}.json"
    )

def official_root(repo_root: Path) -> Path:
    return Path(repo_root) / OFFICIAL_RELDIR

def staging_root(repo_root: Path) -> Path:
    return Path(repo_root) / STAGING_RELDIR

def official_subject_dir(repo_root: Path, neutral_snapshot_id: str) -> Path:
    return official_root(repo_root) / "subjects" / neutral_snapshot_id

def staging_subject_dir(repo_root: Path, neutral_snapshot_id: str) -> Path:
    return staging_root(repo_root) / neutral_snapshot_id

def require_regular_file(path: Path, context: str) -> Path:
    """lstat: reject symlink and non-regular file. Return path."""

def pbf_identity(path: Path) -> dict[str, object]:
    """Read file SHA, artifact_sha256, controlled_subject_source_id, len(sites).
    Do not iterate site path/symbol/span fields."""

def rebuild_successor_rows(repo_root: Path) -> tuple[dict[str, object], ...]:
    """Rebuild 22 rows from frozen four-key rule. Fail if not identical to
    FROZEN_SUCCESSOR_ROWS on every identity field."""

def inventory_rows_for_subject(
    authority: Mapping[str, object],
    controlled_subject_id: str,
) -> tuple[dict[str, object], ...]:
    """Exactly 10 inventory rows in existing inventory canonical order."""

def validate_v2_preflight(
    *,
    repo_root: Path,
    controller_path: Path,
) -> dict[str, object]:
    """All §10 checks. Must not call close_slot_with_authority or _sites."""

def canonical_sites_from_pbf(
    controlled_subject_id: str,
    pbf: Mapping[str, object],
) -> list[dict[str, object]]:
    """Reuse p3_v3.bridge_and_frames._sites. Not a second closer."""

def close_successor_subject(
    *,
    authority: Mapping[str, object],
    successor: Mapping[str, object],
    pbf: Mapping[str, object],
) -> dict[str, object]:
    """Complete 10 slots. Return attempted-subject exact object plus the 10
    official closer objects needed for directory write."""

def derive_subject_eligibility(
    closures: Sequence[Mapping[str, object]],
) -> str:
    """V2_APPLICABILITY_ELIGIBLE or V2_APPLICABILITY_INELIGIBLE only after
    10 valid states. Partial/unknown state raises V2_EXECUTION_FAIL."""

def closure_terminal_row(closure: Mapping[str, object]) -> dict[str, object]:
    """Exact 4-field terminal closure row from an official closer object."""

def build_attempted_subject(
    *,
    successor: Mapping[str, object],
    official_closures: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    """Exact 6-field attempted-subject object."""

def build_cohort_terminal(
    *,
    attempted_subjects: Sequence[Mapping[str, object]],
    controller_source_sha256: str,
) -> dict[str, object]:
    """Exact 12-field self-hashed cohort terminal."""

def validate_cohort_terminal(
    terminal: Mapping[str, object],
    *,
    controller_source_sha256: str,
) -> dict[str, object]:
    """Fail closed on every design §11.5 rule."""

def write_subject_closures(
    directory: Path,
    official_closures: Sequence[Mapping[str, object]],
) -> None:
    """Write 10 slot-closure-<slot_id>.json files with exclusive=True."""

def place_subject_directory(
    *,
    staging_subject: Path,
    official_subject: Path,
) -> None:
    """Atomic os.replace. Fail if official_subject exists."""

def write_official_cohort_terminal(
    *,
    staging_terminal: Path,
    official_terminal: Path,
    terminal: Mapping[str, object],
) -> None:
    """Validate, exclusive-write staging file, atomic place as last official
    artifact."""

def stdout_summary(result: Mapping[str, object]) -> dict[str, object]:
    """Canonical stdout object. No leak keys."""

def run_search(repo_root: Path) -> dict[str, object]:
    """Unique executing state machine."""

def main() -> int:
    """Reject extra argv. Call run_search once. Write canonical stdout."""
```

`close_successor_subject` return exact shape:

```text
{
  "attempted_subject": <ATTEMPTED_SUBJECT_SCHEMA object>,
  "official_closures": [<10 existing p3-slot-closure-v1 objects>]
}
```

`run_search` return exact shape:

```text
{
  "status": "V2_ELIGIBLE_SUBJECT_FOUND" | "V2_COHORT_EXHAUSTED"
            | "V2_PREFLIGHT_FAIL" | "V2_EXECUTION_FAIL",
  "code": <str or None>,
  "controller_source_sha256": <64 hex>,
  "attempted_count": <int>,
  "first_eligible_successor_ordinal": <int or None>,
  "first_eligible_neutral_snapshot_id": <64 hex or None>,
  "official_terminal_written": <bool>,
  "terminal": <cohort terminal or None>
}
```

`main()` return codes: `0` for FOUND or EXHAUSTED; `2` for PREFLIGHT_FAIL,
EXECUTION_FAIL, or extra argv.

---

## 7. Reuse map (do not copy predicate logic)

| Need | Existing symbol | Import from |
|---|---|---|
| Load frozen authority | `load_applicability_authority(...)` | `p3_v3.applicability_predicates` |
| Close one slot | `close_slot_with_authority(authority, inventory_row, canonical_sites, pbf)` | `p3_v3.applicability_predicates` |
| Attach `site_id` + canonical site order | `_sites(controlled_subject_id, pbf["sites"])` | `p3_v3.bridge_and_frames` |
| Phase-1 identity rebuild | `load_phase1_identity_records` / `project_controlled_subject_ids` | `p3_v3.slot_inventory` |
| JSON / hash / exclusive write / regular-file read | `canonical_sha256`, `file_sha256`, `write_canonical_json`, `read_canonical_regular_json`, `read_regular_file_snapshot`, `validate_exact_object`, `EvidenceError` | `p3_v3.artifacts` |

Survey note used by the closer path, not by preflight dumps:

- Official PBF objects have top-level keys
  `adapter_discovery_sha256`, `artifact_sha256`, `category_accounting`,
  `controlled_subject_source_id`, `discovery_status`, `public_schemas`,
  `rows`, `schema_version`, `sites`.
- `sites` items use the existing `_SITE_SCHEMA` and do not already contain
  `site_id`. The controller must call `_sites(...)` once per opened subject
  after preflight. That is the existing canonicalization seam.
- Preflight only uses `file_sha256`, `artifact_sha256`,
  `controlled_subject_source_id`, and `len(sites)`.
- Official closer objects remain `p3-slot-closure-v1` with keys
  `schema_version`, `slot_id`, `controlled_subject_id`, `site_id`, `state`,
  `path`, `artifact_sha256`. Subject directories store those objects. The
  cohort terminal stores only the 4-field reduction.

Do not reimplement `evaluate_predicate`, `select_first_applicable_site`, or
`close_slot`.

---

## 8. Exact object builders

### 8.1 Terminal closure row

From each official closer object:

```python
{
    "slot_id": closure["slot_id"],
    "state": closure["state"],
    "site_id": closure["site_id"],
    "closure_artifact_sha256": closure["artifact_sha256"],
}
```

Rules:

- `state` is only `SITE_FROZEN` or `APPLICABILITY_CLOSED_NOT_APPLICABLE`.
- `site_id` is `null` iff state is `APPLICABILITY_CLOSED_NOT_APPLICABLE`.
- `site_id` is the closer's 64-hex site identity iff state is `SITE_FROZEN`.
- `closure_artifact_sha256` equals the existing closer self-hash.

### 8.2 Attempted subject

```python
{
    "successor_ordinal": successor["successor_ordinal"],
    "neutral_snapshot_id": successor["neutral_snapshot_id"],
    "controlled_subject_source_id": successor["controlled_subject_source_id"],
    "controlled_subject_id": successor["controlled_subject_id"],
    "eligibility": derive_subject_eligibility(official_closures),
    "closures": [closure_terminal_row(item) for item in official_closures],
}
```

`closures` follow inventory canonical slot order for that
`controlled_subject_id`. Length is exactly 10.

### 8.3 Cohort terminal

Body keys in this meaning, then self-hash:

```python
body = {
    "schema_version": TERMINAL_SCHEMA_VERSION,
    "slice_id": SLICE_ID,
    "design_commit": DESIGN_COMMIT,
    "design_file_sha256": DESIGN_FILE_SHA256,
    "authority_artifact_sha256": AUTHORITY_ARTIFACT_SHA256,
    "controller_source_sha256": controller_source_sha256,
    "prior_closure_commit": PRIOR_CLOSURE_COMMIT,
    "terminal_status": "V2_ELIGIBLE_SUBJECT_FOUND" or "V2_COHORT_EXHAUSTED",
    "attempted_subjects": list(attempted_subjects),
    "first_eligible_successor_ordinal": <int or None>,
    "first_eligible_neutral_snapshot_id": <str or None>,
}
terminal = {**body, "artifact_sha256": canonical_sha256(body)}
```

No timestamp, hostname, nonce, or leak key.

FOUND fields:

- last attempted row is the unique first eligible subject;
- that row has at least one `SITE_FROZEN`;
- every earlier row is 10/10 `APPLICABILITY_CLOSED_NOT_APPLICABLE`;
- `first_eligible_successor_ordinal` equals the last ordinal;
- `first_eligible_neutral_snapshot_id` equals that row's neutral id;
- no later successor appears;
- attempted count is `k` where `1 <= k <= 22`.

EXHAUSTED fields:

- exactly 22 attempted rows, ordinals 1 through 22;
- every eligibility is `V2_APPLICABILITY_INELIGIBLE`;
- all 220 closure states are `APPLICABILITY_CLOSED_NOT_APPLICABLE`;
- both first-eligible fields are `null`.

`V2_PREFLIGHT_FAIL` and `V2_EXECUTION_FAIL` are not `terminal_status`
values and must not be written to `cohort-terminal.json`.

---

## 9. `rebuild_successor_rows` algorithm

Use identity fields only.

1. Read `verified_bridge.json` (`35` records).
2. For each record, read `source-scale-<neutral>.json`,
   `public-behavior-frame-<neutral>.json`, and
   `profiling-workload-<neutral>.json`.
3. Rebuild `controlled_subject_id` with `canonical_sha256` over
   `{normalized_source_tree_sha256, build_descriptor_sha256,
   public_workload_set_sha256=workload["artifact_sha256"],
   domain="P3-SUBJECT-v1"}`.
4. Confirm the 35 rebuilt IDs equal
   `project_controlled_subject_ids(load_phase1_identity_records(...))`.
5. Admit a subject only when `len(pbf["sites"]) > 0`. That yields 23
   subjects. Confirm each admitted `scale_class == "L"`.
6. Sort by `(SCALE_RANK[scale_class], total_effective_lines,
   len(sites), neutral_snapshot_id)`.
7. Confirm rebuilt rank 1 is `CLOSED_RANK1_NEUTRAL_SNAPSHOT_ID` and drop it.
8. Assign successor ordinals `1..22` to the remaining rows.
9. Compare each rebuilt row to `FROZEN_SUCCESSOR_ROWS[i]` on
   `successor_ordinal`, `scale_class`, `total_effective_lines`,
   `pbf_site_count`, `frozen_slots`, `neutral_snapshot_id`,
   `controlled_subject_source_id`, `controlled_subject_id`,
   `pbf_file_sha256`, and `pbf_artifact_sha256`.
10. Any mismatch, duplicate, gap, extra row, or missing row raises
    `EvidenceError("V2_SUCCESSOR_IDENTITY_CONFLICT", ...)`.

`pbf_identity` implementation:

```python
raw, mode = read_regular_file_snapshot(path, "pbf")
if not stat.S_ISREG(mode):
    raise EvidenceError("V2_PREFLIGHT_FAIL", "pbf is not a regular file")
payload = json.loads(raw.decode("utf-8"))
sites = payload["sites"]
return {
    "file_sha256": hashlib.sha256(raw).hexdigest(),
    "artifact_sha256": payload["artifact_sha256"],
    "controlled_subject_source_id": payload["controlled_subject_source_id"],
    "pbf_site_count": len(sites),
}
```

Do not loop site dicts. Do not print site values.

---

## 10. `validate_v2_preflight` checks

Run in this order. Any failure is `V2_PREFLIGHT_FAIL` (identity mismatch
may use code `V2_SUCCESSOR_IDENTITY_CONFLICT` and is still a preflight
failure). Do not call `close_slot_with_authority` or `_sites`.

1. `controller_path` is a regular file equal to
   `repo_root / CONTROLLER_RELPATH`. Record
   `controller_source_sha256 = file_sha256(controller_path)`.
2. `file_sha256(repo_root / DESIGN_RELPATH) == DESIGN_FILE_SHA256`.
3. `file_sha256(authority) == AUTHORITY_FILE_SHA256`.
4. `load_applicability_authority(...)` using the official relative paths
   under `repo_root`. Confirm
   `manifest["authority_id"] == AUTHORITY_ID`,
   `manifest["schema_version"] == AUTHORITY_SCHEMA`,
   `manifest["artifact_sha256"] == AUTHORITY_ARTIFACT_SHA256`,
   and the design §10.1.3 binding table
   (inventory/registry/impl/policy/catalogue SHAs).
5. `rebuild_successor_rows(repo_root)` equals `FROZEN_SUCCESSOR_ROWS`.
6. Each of the 22 `controlled_subject_id` values has exactly 10 inventory
   rows via `inventory_rows_for_subject`.
7. Each of the 22 PBF paths is a regular non-symlink file whose
   `pbf_identity` matches the frozen row.
8. `official_root(repo_root)` and `staging_root(repo_root)` do not exist
   (`Path.exists()` is false; `lstat` raises `FileNotFoundError`).
9. `OLD_CLOSURE_RELDIR` contains exactly the 10 names in
   `PRIOR_RANK1_CLOSURE_FILE_SHA256`, and each `file_sha256` matches.

Return:

```python
{
    "status": "V2_PREFLIGHT_PASS",
    "controller_source_sha256": <digest>,
    "authority_artifact_sha256": AUTHORITY_ARTIFACT_SHA256,
    "successor_count": 22,
}
```

---

## 11. State machine inside `run_search`

`run_search` is the only executor. `main` calls it once.

```text
V2_PREFLIGHT
  -> V2_SUBJECT_OPEN(ordinal=1)
  -> (eligible) V2_SUBJECT_ELIGIBLE -> V2_ELIGIBLE_SUBJECT_FOUND
  -> (ineligible and ordinal<22) V2_SUBJECT_OPEN(ordinal+1)
  -> (ineligible and ordinal=22) V2_COHORT_EXHAUSTED
  -> any exception / partial / identity change / E_EXISTS -> V2_EXECUTION_FAIL
```

Procedure:

1. `controller_path = repo_root / CONTROLLER_RELPATH`.
2. `controller_source_sha256 = file_sha256(controller_path)`.
3. Try `validate_v2_preflight`. On failure return PREFLIGHT_FAIL with
   `official_terminal_written=False` and `terminal=None`. Do not create
   official or staging roots if preflight failed before they were created.
4. `authority = load_applicability_authority(...)`.
5. `attempted: list = []`.
6. For `successor` in `FROZEN_SUCCESSOR_ROWS` in ordinal order:
   - Load that subject's PBF once with `read_canonical_regular_json`.
   - Re-check file SHA / artifact SHA / source ID / `len(sites)` against
     the frozen row. Mismatch is EXECUTION_FAIL, not ineligible.
   - `closed = close_successor_subject(authority=..., successor=..., pbf=...)`.
   - `close_successor_subject` must call `close_slot_with_authority` exactly
     10 times even when the first call returns `SITE_FROZEN`.
   - Append `closed["attempted_subject"]`.
   - Write the 10 official closer objects to
     `staging_subject_dir / slot-closure-<slot_id>.json` only after all 10
     exist in memory.
   - `os.replace` the staging subject directory onto
     `official_subject_dir`. Create `official/subjects/` as needed. Do not
     overwrite an existing official subject path.
   - If eligibility is `V2_APPLICABILITY_ELIGIBLE`: build FOUND terminal,
     `validate_cohort_terminal`, write it last, return FOUND.
   - If eligibility is `V2_APPLICABILITY_INELIGIBLE` and ordinal `< 22`:
     continue.
   - If eligibility is `V2_APPLICABILITY_INELIGIBLE` and ordinal `== 22`:
     build EXHAUSTED terminal, validate, write last, return EXHAUSTED.
7. After the official terminal is written, do not open another PBF and do
   not write another closure.
8. On EXECUTION_FAIL: keep already placed official subject directories and
   any staging residue; do not write `cohort-terminal.json`; do not label
   the failing subject ineligible; do not advance; do not retry.

`close_successor_subject` body:

```python
rows = inventory_rows_for_subject(authority, successor["controlled_subject_id"])
if len(rows) != 10:
    raise EvidenceError("V2_EXECUTION_FAIL", "subject slot count is not 10")
sites = canonical_sites_from_pbf(successor["controlled_subject_id"], pbf)
official: list[dict[str, object]] = []
for row in rows:
    official.append(
        close_slot_with_authority(authority, row, sites, pbf)
    )
attempted = build_attempted_subject(successor=successor, official_closures=official)
return {"attempted_subject": attempted, "official_closures": tuple(official)}
```

---

## 12. Slice A Task 1: identity / preflight core

**Files:**

- Create: `scripts/p3_v3/prospective_applicability_search_v2.py`
- Create: `tests/p3_v3/test_prospective_applicability_search_v2.py`

**Must not:** call `close_slot_with_authority`, call `_sites`, write official
or staging v2 output, invoke `run_search` against the real worktree, or
execute the official command.

### Task 1 RED

```bash
cd /tmp/p3-c3-applicability-authority
test ! -e scripts/p3_v3/prospective_applicability_search_v2.py
test ! -e tests/p3_v3/test_prospective_applicability_search_v2.py
PYTHONPATH=/tmp/p3-c3-applicability-authority/src \
  /workspace/.venv/bin/python - <<'PY'
import importlib
try:
    importlib.import_module("scripts.p3_v3.prospective_applicability_search_v2")
except ModuleNotFoundError:
    print("RED_IMPORT_ABSENT")
else:
    raise SystemExit("controller module already exists")
PY
```

Expected: `RED_IMPORT_ABSENT`.

Write the test file first with the tests below, then:

```bash
cd /tmp/p3-c3-applicability-authority
PYTHONPATH=/tmp/p3-c3-applicability-authority/src \
  /workspace/.venv/bin/python -m pytest \
  tests/p3_v3/test_prospective_applicability_search_v2.py \
  -q --tb=short
```

Expected: collection or import fails, or every new test fails, because the
controller file is still absent or the functions are missing.

Required RED tests (names fixed):

- `test_controller_module_is_absent_before_implementation` is only the
  pre-file shell check above. After the file exists, do not keep a pytest
  that demands absence.
- `test_rebuild_successor_rows_matches_frozen_22_row_table`
- `test_rebuild_successor_rows_rejects_reordered_deleted_or_extra_row`
- `test_validate_v2_preflight_rejects_design_sha_change`
- `test_validate_v2_preflight_rejects_authority_sha_change`
- `test_validate_v2_preflight_rejects_successor_identity_change`
- `test_validate_v2_preflight_rejects_slot_count_other_than_10`
- `test_validate_v2_preflight_rejects_old_rank1_closure_byte_change`
- `test_validate_v2_preflight_rejects_existing_official_or_staging_namespace`
- `test_validate_v2_preflight_passes_current_frozen_identities`
- `test_preflight_does_not_call_closer`

Fail-closed tests use `tmp_path` copies or `monkeypatch`. They must not
edit files in the real worktree.

Concrete fail-closed method:

- Design SHA: copy the design file to `tmp_path`, append one byte, point
  `DESIGN_RELPATH` via a tiny tmp repo layout **or** monkeypatch
  `file_sha256` for that path. Prefer a tmp repo that contains the needed
  relative files, then `validate_v2_preflight(repo_root=tmp_path, ...)`.
- Authority SHA: copy `applicability-authority.json` and flip one hex
  character in a non-self-hash-critical way, or replace the file bytes and
  expect fail closed.
- Successor identity: monkeypatch `rebuild_successor_rows` to return a
  swapped pair, a 21-row tuple, or a 23-row tuple.
- Slot count: monkeypatch `inventory_rows_for_subject` to return 9 or 11
  rows.
- Old closures: copy the 10 official closures into a tmp
  `OLD_CLOSURE_RELDIR` and append one byte to one file.
- Namespace: `mkdir` official or staging under tmp `repo_root`.
- Closer isolation: monkeypatch
  `p3_v3.applicability_predicates.close_slot_with_authority` to raise
  `AssertionError`; `validate_v2_preflight` must still pass on the real
  worktree.

`test_rebuild_successor_rows_matches_frozen_22_row_table` and
`test_validate_v2_preflight_passes_current_frozen_identities` may read the
real worktree. They may hash and count PBF files. They must not assert on
site path, symbol, or span values.

### Task 1 GREEN

Implement constants, path helpers, `pbf_identity`,
`rebuild_successor_rows`, `inventory_rows_for_subject`, and
`validate_v2_preflight`. Leave `run_search` / `main` / closer wrappers
unimplemented or as `raise EvidenceError("V2_EXECUTION_FAIL", "not implemented")`
if referenced; Task 1 tests must not call them.

Re-run the Task 1 pytest command. Expected: all Task 1 tests pass.

Prove closer was not used:

```bash
cd /tmp/p3-c3-applicability-authority
PYTHONPATH=/tmp/p3-c3-applicability-authority/src \
  /workspace/.venv/bin/python -m pytest \
  tests/p3_v3/test_prospective_applicability_search_v2.py::test_preflight_does_not_call_closer \
  tests/p3_v3/test_prospective_applicability_search_v2.py::test_validate_v2_preflight_passes_current_frozen_identities \
  -q --tb=short
```

### Task 1 commit

```bash
git add scripts/p3_v3/prospective_applicability_search_v2.py \
        tests/p3_v3/test_prospective_applicability_search_v2.py
git diff --cached --name-only
# must be exactly those two paths
git commit -m "feat(p3-v3): validate prospective v2 search inputs"
git diff --check HEAD^..HEAD
```

Do not push until all three Slice A tasks and focused verification finish,
unless an intermediate push is required by the executing-plans checkpoint.
This plan's Slice A push happens once at §14.

---

## 13. Slice A Task 2: pure state machine and terminal

**Files:** the same two files only.

**Must not:** read a real successor PBF into `close_successor_subject` or
`_sites`. Use synthetic fixtures.

### Task 2 RED

Add tests, then run:

```bash
cd /tmp/p3-c3-applicability-authority
PYTHONPATH=/tmp/p3-c3-applicability-authority/src \
  /workspace/.venv/bin/python -m pytest \
  tests/p3_v3/test_prospective_applicability_search_v2.py \
  -q --tb=short -k "eligibility or terminal or state_machine or close_successor"
```

Expected: new tests fail.

Required RED tests:

- `test_close_successor_subject_completes_all_10_slots_when_first_is_frozen`
- `test_derive_subject_eligibility_10_of_10_false_is_ineligible`
- `test_derive_subject_eligibility_any_site_frozen_is_eligible`
- `test_run_search_stops_after_first_eligible_and_does_not_open_later_subject`
- `test_run_search_exhausts_22_ineligible_subjects`
- `test_run_search_ordinals_are_contiguous_and_cannot_skip`
- `test_run_search_infrastructure_failure_is_not_ineligible`
- `test_build_and_validate_found_terminal_consistency`
- `test_build_and_validate_exhausted_terminal_consistency`
- `test_validate_cohort_terminal_rejects_controller_sha_change`
- `test_validate_cohort_terminal_rejects_design_sha_change`
- `test_validate_cohort_terminal_rejects_attempted_order_change`
- `test_validate_cohort_terminal_rejects_closure_hash_change`
- `test_validate_cohort_terminal_rejects_terminal_status_change`
- `test_cohort_terminal_has_no_path_symbol_source_or_outcome_fields`

Synthetic fixture rules:

- Build fake SHA-256 strings with `hashlib.sha256(label.encode()).hexdigest()`.
- Synthetic PBF: `{"rows": [], "public_schemas": [], "sites": [<2 synthetic
  _SITE_SCHEMA objects>]}`. Paths may be `a.py` / `b.py`. These are test
  fixtures, not successor sites.
- Synthetic authority: `freeze_slot_inventory(project_controlled_subject_ids(35
  fake identity records))` plus `build_predicate_registry("c"*64)`. Use one
  fake `controlled_subject_id` that matches a successor-shaped row.
- Monkeypatch `close_slot_with_authority` to return canned closer objects and
  to record call counts. The first-frozen test asserts `call_count == 10`.
- For `run_search` tests, monkeypatch `validate_v2_preflight` to pass,
  `rebuild_successor_rows` / `FROZEN_SUCCESSOR_ROWS` consumption to a 3-row
  or 22-row synthetic tuple, `close_successor_subject` to a side-effect
  function that records ordinals, and the write helpers to no-ops or tmp
  writes. A 3-row synthetic is allowed only for stop/skip tests if
  `MAXIMUM_ATTEMPTS` is temporarily monkeypatched to `3` **inside the test**
  and restored; the production constant remains `22`. Exhaustion tests must
  use 22 synthetic ineligible subjects.
- Infrastructure failure: `close_successor_subject` raises
  `EvidenceError("V2_EXECUTION_FAIL", "partial")` on ordinal 2 after ordinal 1
  was ineligible. Assert status is `V2_EXECUTION_FAIL`, ordinal 2 is not
  recorded as ineligible, and no cohort terminal is produced.

FOUND terminal test: one ineligible subject then one eligible subject with
one `SITE_FROZEN` and nine `NOT_APPLICABLE`. Validator accepts. Then mutate
`controller_source_sha256`, `design_file_sha256`, swap attempted order, flip
one `closure_artifact_sha256`, or change `terminal_status` to `EXHAUSTED`;
each mutation fails closed.

EXHAUSTED terminal test: 22 ineligible subjects, 220 NA closures, both
first-eligible fields `null`.

Leak test: walk the terminal dict recursively; `FORBIDDEN_LEAK_KEYS` must
be absent.

### Task 2 GREEN

Implement `canonical_sites_from_pbf`, `close_successor_subject`,
`derive_subject_eligibility`, `closure_terminal_row`,
`build_attempted_subject`, `build_cohort_terminal`,
`validate_cohort_terminal`, and the `run_search` decision loop. Filesystem
placement may still be a no-op helper that Task 3 replaces, but `run_search`
must already stop, exhaust, and refuse to treat failures as ineligible.

Re-run the Task 2 pytest selector. Expected: pass.

### Task 2 commit

```bash
git add scripts/p3_v3/prospective_applicability_search_v2.py \
        tests/p3_v3/test_prospective_applicability_search_v2.py
git commit -m "feat(p3-v3): define prospective v2 search state machine"
git diff --check HEAD^..HEAD
```

---

## 14. Slice A Task 3: filesystem atomicity and CLI

**Files:** the same two files only.

**Must not:** run the official zero-argument command on the real worktree.

### Task 3 RED

```bash
cd /tmp/p3-c3-applicability-authority
PYTHONPATH=/tmp/p3-c3-applicability-authority/src \
  /workspace/.venv/bin/python -m pytest \
  tests/p3_v3/test_prospective_applicability_search_v2.py \
  -q --tb=short -k "atomic or cli or stdout or terminal_write"
```

Expected: new tests fail.

Required RED tests:

- `test_subject_directory_written_only_after_10_closures_exist_in_memory`
- `test_subject_directory_is_placed_atomically`
- `test_cohort_terminal_is_written_last`
- `test_no_pbf_open_or_closure_write_after_terminal`
- `test_failure_does_not_write_cohort_terminal`
- `test_failure_keeps_partial_or_staging`
- `test_existing_official_path_is_not_overwritten`
- `test_main_rejects_help_and_extra_arguments`
- `test_stdout_summary_has_no_site_path_symbol_or_span`
- `test_controller_file_sha_is_bound_into_terminal`

Atomicity method:

- Use `tmp_path` as `repo_root`.
- Monkeypatch `validate_v2_preflight` to return a pass digest of the real
  controller file (`file_sha256(real controller)`).
- Monkeypatch `close_successor_subject` to return 10 in-memory official
  closer objects and to record when it is called.
- Instrument `write_canonical_json` / `place_subject_directory` /
  `write_official_cohort_terminal` to record order.
- Assert order is: 10 memory closures -> 10 staging files -> atomic subject
  place -> (optional next subject) -> terminal construct/validate -> terminal
  place.
- Inject a write failure on closure 7: no official subject dir, staging
  residue allowed, no `cohort-terminal.json`.
- Inject `os.replace` failure on subject place: staging remains, no
  official subject, no terminal.
- Pre-create `official/subjects/<neutral>`: fail closed, original bytes
  unchanged.
- After a FOUND run, monkeypatch PBF open / closer to raise if called;
  invoking any post-terminal hook must not happen.

CLI tests use `subprocess.run` with
`[sys.executable, str(CONTROLLER), "--help"]` and
`[sys.executable, str(CONTROLLER), "--output-root", "x"]`.
`PYTHONPATH` includes `src`. Return code is `2`. Stdout/stderr contain no
site path/symbol/span. Do not run `[sys.executable, str(CONTROLLER)]`
against the real worktree.

Stdout test: call `stdout_summary` / `main` with monkeypatched `run_search`
returning FOUND. Parse canonical JSON. Keys equal `STDOUT_SUMMARY_SCHEMA`.
`FORBIDDEN_LEAK_KEYS` absent. `controller_source_sha256` equals
`file_sha256(controller)`.

### Task 3 GREEN

Implement `write_subject_closures`, `place_subject_directory`,
`write_official_cohort_terminal`, `stdout_summary`, the real write path in
`run_search`, and `main()`.

`place_subject_directory`:

```python
if official_subject.exists() or official_subject.is_symlink():
    raise EvidenceError("V2_EXECUTION_FAIL", "official subject path exists")
official_subject.parent.mkdir(parents=True, exist_ok=True)
os.replace(staging_subject, official_subject)
```

`write_official_cohort_terminal`:

```python
validate_cohort_terminal(terminal, controller_source_sha256=terminal["controller_source_sha256"])
write_canonical_json(staging_terminal, terminal, exclusive=True)
if official_terminal.exists() or official_terminal.is_symlink():
    raise EvidenceError("V2_EXECUTION_FAIL", "official terminal exists")
os.replace(staging_terminal, official_terminal)
```

`main`:

```python
def main() -> int:
    if len(sys.argv) != 1:
        sys.stdout.buffer.write(
            canonical_json_bytes(
                {
                    "status": "V2_PREFLIGHT_FAIL",
                    "slice_id": SLICE_ID,
                    "design_commit": DESIGN_COMMIT,
                    "controller_source_sha256": None,
                    "attempted_count": 0,
                    "first_eligible_successor_ordinal": None,
                    "official_terminal_written": False,
                }
            )
        )
        return 2
    repo_root = Path(__file__).resolve().parents[2]
    result = run_search(repo_root)
    sys.stdout.buffer.write(canonical_json_bytes(stdout_summary(result)))
    if result["status"] in {"V2_ELIGIBLE_SUBJECT_FOUND", "V2_COHORT_EXHAUSTED"}:
        return 0
    return 2
```

Re-run the Task 3 selector. Expected: pass.

### Task 3 commit

```bash
git add scripts/p3_v3/prospective_applicability_search_v2.py \
        tests/p3_v3/test_prospective_applicability_search_v2.py
git commit -m "feat(p3-v3): expose prospective v2 controlled search"
git diff --check HEAD^..HEAD
```

---

## 15. Slice A focused verification

Run only this command. Do not add the rest of `tests/`.

```bash
cd /tmp/p3-c3-applicability-authority
CONTROLLER_SHA=$(sha256sum scripts/p3_v3/prospective_applicability_search_v2.py | awk '{print $1}')
echo "CONTROLLER_SOURCE_SHA256=${CONTROLLER_SHA}"
PYTHONPATH=/tmp/p3-c3-applicability-authority/src \
  /workspace/.venv/bin/python -m pytest \
  tests/p3_v3/test_prospective_applicability_search_v2.py \
  tests/p3_v3/test_applicability_authority.py \
  tests/p3_v3/test_applicability_authority.py::test_close_slot_with_authority_selects_first_or_not_applicable \
  tests/p3_v3/test_bridge_and_frames.py::test_slot_selects_first_applicable_canonical_site_or_none \
  tests/p3_v3/test_bridge_and_frames.py::test_close_slot_two_paths_not_applicable_or_site_frozen \
  tests/p3_v3/test_artifacts.py::test_canonical_file_has_sorted_keys_and_one_terminal_lf \
  tests/p3_v3/test_artifacts.py::test_sha256_and_canonical_hash_require_lowercase_hex \
  tests/p3_v3/test_artifacts.py::test_byte_index_digest_covers_the_complete_self_hashed_artifact \
  tests/p3_v3/test_artifacts.py::test_exclusive_write_preserves_existing_bytes \
  tests/p3_v3/test_cli.py::test_validate_applicability_authority_passes_official_bindings \
  tests/p3_v3/test_prospective_applicability_search_v2.py::test_main_rejects_help_and_extra_arguments \
  -q --tb=short
git diff --check 4ea6f05b44c76ebaa031277872c3711cdd1953eb..HEAD
test ! -e data/p3_v3/phase2/prospective-applicability-search-v2
test ! -e data/p3_v3/phase2/prospective-applicability-search-v2.staging
git status --porcelain=v1 --untracked-files=all
```

The repeated `test_close_slot_with_authority_...` node is included in the
full `test_applicability_authority.py` file; keep the file-level run as the
authority regression and keep the named closer / `select_first_applicable_site`
/ artifact tests as the required narrow set.

Implementation acceptance must show:

- no real successor site was opened (no official v2 subject dirs; tests used
  synthetic sites; preflight tests only hashed/counted PBF files);
- no official/staging v2 output exists in the real worktree;
- the official zero-argument command was not executed;
- `CONTROLLER_SOURCE_SHA256` was printed;
- exactly three implementation commits exist on top of `4ea6f05b...`;
- worktree is empty after those commits;
- `git ls-remote --heads origin refs/heads/codex/p3-c3-applicability-authority`
  equals local HEAD after the Slice A push.

Slice A success terminal:

`V2_CONTROLLER_IMPLEMENTATION_PASS`

This PASS does not authorize Slice B.

Push the three implementation commits with a normal `git push origin
codex/p3-c3-applicability-authority`. No amend. No force-push.

Then stop and report:

- controller commit (HEAD)
- controller source SHA-256
- focused test command and result
- design commit `4ea6f05b44c76ebaa031277872c3711cdd1953eb`
- design file SHA-256 `bb0ca5d20f3fec61257b2ba524585fe899d28c8b8963c61273a8ffeb857aa6c6`
- authority artifact SHA-256 `30b08271eafdead14a06707b461f108c1ec5a53eb5d2859a37b2cd6238e20214`
- worktree / remote identity

---

## 16. Slice A final review

After focused verification, run one `gpt-5.6-sol` / `high` review of the
two new files against the approved design. Check:

- every design rule is implemented, none changed;
- 22-row order and identities are unchanged;
- no user-controllable successor or stopping parameter;
- predicate / closer logic is imported, not copied;
- 10-slot completion holds after the first `SITE_FROZEN`;
- FOUND and EXHAUSTED terminals match §8;
- failure does not write a scientific terminal;
- `controller_source_sha256` is `file_sha256` of the controller file;
- stdout and terminal contain no site path/symbol/span;
- no second authority, schema file, manifest, or ledger;
- C3 is not described as upgraded.

Critical or Important findings: one bounded fix commit and one re-review.
If still failing, stop for human review. Do not start Slice B.

---

## 17. Slice B: official controlled run

`DO_NOT_EXECUTE_WITHOUT_SEPARATE_AUTHORIZATION`

A later user message must bind all of:

- controller implementation commit
- controller source SHA-256
- design commit `4ea6f05b44c76ebaa031277872c3711cdd1953eb`
- design file SHA-256 `bb0ca5d20f3fec61257b2ba524585fe899d28c8b8963c61273a8ffeb857aa6c6`
- authority artifact SHA-256 `30b08271eafdead14a06707b461f108c1ec5a53eb5d2859a37b2cd6238e20214`
- prior closure commit `e6f9e84a5a71900e0fb6f0655393c5e1b613b6a5`
- `P3_C3_PROSPECTIVE_V2_AUTHORIZED=true`
- the explicit sentence: 运行一次，禁止重试

Do not execute any step in this section during Slice A.

### B1. Fix the implementation identity

```bash
cd /tmp/p3-c3-applicability-authority
git fetch origin codex/p3-c3-applicability-authority
git rev-parse HEAD
git branch --show-current
git status --porcelain=v1 --untracked-files=all
git diff --check
git ls-remote --heads origin refs/heads/codex/p3-c3-applicability-authority
sha256sum scripts/p3_v3/prospective_applicability_search_v2.py
sha256sum docs/superpowers/specs/2026-08-27-p3-c3-prospective-v2-successor-and-stopping-rule-design.md
```

Required:

- branch is `codex/p3-c3-applicability-authority`;
- local HEAD equals the authorized controller implementation commit;
- remote SHA equals local HEAD;
- worktree is empty;
- controller file SHA-256 equals the authorized controller source SHA-256;
- design file SHA-256 equals `bb0ca5d20f3fec61257b2ba524585fe899d28c8b8963c61273a8ffeb857aa6c6`.

If any check fails, stop as `V2_PREFLIGHT_FAIL`. Do not run the controller.

### B2. Read-only identity recheck

Confirm, without opening successor site fields:

- `load_applicability_authority` artifact SHA-256 is `30b08271eafdead14a06707b461f108c1ec5a53eb5d2859a37b2cd6238e20214`;
- prior rank-1 closure directory bytes still match `PRIOR_RANK1_CLOSURE_FILE_SHA256`;
- prior closure commit remains `e6f9e84a5a71900e0fb6f0655393c5e1b613b6a5`;
- official root `data/p3_v3/phase2/prospective-applicability-search-v2/` does not exist;
- staging root `data/p3_v3/phase2/prospective-applicability-search-v2.staging/` does not exist.

### B3. One official invocation

Run exactly once:

```text
cd /tmp/p3-c3-applicability-authority
PYTHONPATH=src python3 scripts/p3_v3/prospective_applicability_search_v2.py
```

Forbidden:

- a second invocation;
- extra argv;
- retry after PREFLIGHT_FAIL or EXECUTION_FAIL;
- resume;
- editing authority, predicates, inventory, design, or the controller after the bound commit;
- opening a successor PBF except through this single controller process.

### B4. Read-only acceptance after the one run

Inspect only official/staging output identity and the stdout summary.

If `status` is `V2_ELIGIBLE_SUBJECT_FOUND`:

- official root exists;
- attempted subject directories are exactly `subjects/<neutral>` for ordinals `1..k`;
- each attempted directory contains exactly 10 `slot-closure-<slot_id>.json` files;
- the last attempted subject is the unique first eligible subject;
- no directory exists for ordinal `k+1` or later;
- `cohort-terminal.json` exists, validates, and has `terminal_status=V2_ELIGIBLE_SUBJECT_FOUND`;
- `controller_source_sha256` equals the authorized controller SHA.

If `status` is `V2_COHORT_EXHAUSTED`:

- exactly 22 subject directories;
- exactly 220 closure files;
- `cohort-terminal.json` validates with `terminal_status=V2_COHORT_EXHAUSTED`;
- both first-eligible fields are `null`.

If `status` is `V2_PREFLIGHT_FAIL`:

- no official subject directory;
- no official `cohort-terminal.json`;
- stop. Do not retry.

If `status` is `V2_EXECUTION_FAIL`:

- no official `cohort-terminal.json`;
- keep already placed official subject directories and any staging residue;
- do not label the failed subject ineligible;
- stop. Do not retry.

C3 remains `blocked`. Do not edit the claim ledger.

### B5. Commit official artifacts only on FOUND or EXHAUSTED

Stage only:

`data/p3_v3/phase2/prospective-applicability-search-v2/`

The staged tree must contain only:

- one directory per attempted subject under `subjects/<neutral_snapshot_id>/`;
- exactly 10 closure files per attempted subject;
- exactly one `cohort-terminal.json`.

Do not stage `.staging` residue.

```bash
git add data/p3_v3/phase2/prospective-applicability-search-v2
git diff --cached --name-only
git commit -m "data(p3-v3): record prospective v2 applicability search"
git diff --check HEAD^..HEAD
git push origin codex/p3-c3-applicability-authority
git ls-remote --heads origin refs/heads/codex/p3-c3-applicability-authority
git status --porcelain=v1 --untracked-files=all
```

No amend. No force-push. Final worktree must be empty.

On FAIL, do not commit a fake terminal.

Slice B scientific terminals are only:

- `V2_ELIGIBLE_SUBJECT_FOUND`
- `V2_COHORT_EXHAUSTED`
- `V2_PREFLIGHT_FAIL`
- `V2_EXECUTION_FAIL`

---

## 18. Plan exclusions

This plan does not authorize or include:

- a new design or spec revision;
- edits to authority, predicates, inventory, registry, or existing closures;
- claim-ledger edits;
- a new JSON Schema file, manifest, ledger, or subject terminal;
- retry or resume parameters;
- full pytest;
- package install;
- profiling, mutation, build, or source recovery;
- automatic start of the official run after implementation;
- unauthorized opening of successor sites.

---

## 19. Plan self-review

| Check | Result |
|---|---|
| Slice A and Slice B are separate | Pass. §0, §15, and §17. |
| Slice B is explicitly unauthorized | Pass. `DO_NOT_EXECUTE_WITHOUT_SEPARATE_AUTHORIZATION`. |
| Each code Task has RED/GREEN commands and expected results | Pass. Tasks 1–3. |
| Each implementation step names concrete interfaces | Pass. §6–§11. No placeholder work items. |
| File map is exactly two new files | Pass. §2. |
| Types, fields, and terminal names match the design | Pass. §5–§8. |
| Terminal, attempted-subject, and closure objects are complete | Pass. §8. |
| 22/10/220 and FOUND/EXHAUSTED rules are complete | Pass. §8, §11, §17. |
| Failure and no-retry rules are complete | Pass. §11, §17. |
| Focused tests are complete and not a full suite | Pass. §15. |
| No second authority, schema, manifest, or ledger | Pass. §2, §18. |
| C3 remains blocked | Pass. §1, §17, §18. |
| `git diff --check` is required on every commit | Pass. |

Internal contradictions removed before commit: the 22-row constant is the complete design §3 table, including ordinal 9 `pbf_site_count=22438`. Rank-1 controlled subject ID is `942d190c2c3972a6a6e9feb6ef5d4abee1d939cb0aa9ee676232ab0184dead09`.

---

## 20. After this planning task

This planning task commits only this file, then stops for human review.
Do not start Slice A.

Unique next task after human approval of this plan:

`P3_C3_PROSPECTIVE_V2_CONTROLLER_IMPLEMENTATION`
