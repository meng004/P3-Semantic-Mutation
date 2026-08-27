#!/usr/bin/env python3
"""Prospective v2 eligibility-search controller.

Slice A identity and preflight only in the first implementation commit.
This module does not authorize a confirmatory Package A continuation.
C3 remains blocked.
"""

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

SUCCESSOR_IDENTITY_KEYS = (
    "successor_ordinal",
    "scale_class",
    "total_effective_lines",
    "pbf_site_count",
    "frozen_slots",
    "neutral_snapshot_id",
    "controlled_subject_source_id",
    "controlled_subject_id",
    "pbf_file_sha256",
    "pbf_artifact_sha256",
)

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


def old_closure_dir(repo_root: Path) -> Path:
    return Path(repo_root) / OLD_CLOSURE_RELDIR


def require_regular_file(path: Path, context: str) -> Path:
    target = Path(path)
    try:
        info = target.lstat()
    except OSError as exc:
        raise EvidenceError("V2_PREFLIGHT_FAIL", f"{context} is unavailable") from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise EvidenceError("V2_PREFLIGHT_FAIL", f"{context} is not a regular file")
    return target


def _preflight_fail(detail: str) -> None:
    raise EvidenceError("V2_PREFLIGHT_FAIL", detail)


def _successor_identity_conflict(detail: str) -> None:
    raise EvidenceError("V2_SUCCESSOR_IDENTITY_CONFLICT", detail)


def _compare_successor_rows(
    observed: Sequence[Mapping[str, object]],
    expected: Sequence[Mapping[str, object]],
) -> None:
    if len(observed) != len(expected):
        _successor_identity_conflict(
            f"successor row count differs: expected {len(expected)}, observed {len(observed)}"
        )
    for index, (left, right) in enumerate(zip(observed, expected, strict=True)):
        for key in SUCCESSOR_IDENTITY_KEYS:
            if left.get(key) != right.get(key):
                _successor_identity_conflict(
                    f"successor identity field {key} differs at ordinal index {index}"
                )


def pbf_identity(path: Path) -> dict[str, object]:
    raw, mode = read_regular_file_snapshot(path, "pbf")
    if not stat.S_ISREG(mode):
        raise EvidenceError("V2_PREFLIGHT_FAIL", "pbf is not a regular file")
    payload = json.loads(raw.decode("utf-8"))
    if not isinstance(payload, Mapping):
        raise EvidenceError("V2_PREFLIGHT_FAIL", "pbf is not an object")
    sites = payload["sites"]
    if not isinstance(sites, list):
        raise EvidenceError("V2_PREFLIGHT_FAIL", "pbf sites must be a list")
    return {
        "file_sha256": hashlib.sha256(raw).hexdigest(),
        "artifact_sha256": payload["artifact_sha256"],
        "controlled_subject_source_id": payload["controlled_subject_source_id"],
        "pbf_site_count": len(sites),
    }


def rebuild_successor_rows(repo_root: Path) -> tuple[dict[str, object], ...]:
    root = Path(repo_root)
    bridge = read_canonical_json(root / BRIDGE_RELPATH)
    if not isinstance(bridge, Mapping):
        _successor_identity_conflict("verified bridge is not an object")
    records = bridge.get("records")
    if not isinstance(records, list) or len(records) != 35:
        _successor_identity_conflict("verified bridge must contain 35 records")
    rebuilt_ids: list[str] = []
    admitted: list[dict[str, object]] = []
    for index, raw in enumerate(records):
        if not isinstance(raw, Mapping):
            _successor_identity_conflict(f"bridge.records[{index}] is not an object")
        neutral = raw["neutral_snapshot_id"]
        if not isinstance(neutral, str):
            _successor_identity_conflict(f"bridge.records[{index}] missing neutral id")
        scale = read_canonical_regular_json(
            source_scale_path(root, neutral), f"source-scale[{index}]"
        )
        workload = read_canonical_regular_json(
            workload_path(root, neutral), f"workload[{index}]"
        )
        identity = pbf_identity(pbf_path(root, neutral))
        subject_id = canonical_sha256(
            {
                "normalized_source_tree_sha256": raw["normalized_source_tree_sha256"],
                "build_descriptor_sha256": raw["build_descriptor_sha256"],
                "public_workload_set_sha256": workload["artifact_sha256"],
                "domain": "P3-SUBJECT-v1",
            }
        )
        rebuilt_ids.append(subject_id)
        site_count = identity["pbf_site_count"]
        if not isinstance(site_count, int) or site_count <= 0:
            continue
        scale_class = scale["scale_class"]
        if scale_class != "L":
            _successor_identity_conflict(
                f"admitted subject {neutral} is not scale class L"
            )
        admitted.append(
            {
                "old_rank": 0,
                "scale_class": scale_class,
                "total_effective_lines": scale["total_effective_lines"],
                "pbf_site_count": site_count,
                "frozen_slots": SLOTS_PER_SUBJECT,
                "neutral_snapshot_id": neutral,
                "controlled_subject_source_id": identity["controlled_subject_source_id"],
                "controlled_subject_id": subject_id,
                "pbf_file_sha256": identity["file_sha256"],
                "pbf_artifact_sha256": identity["artifact_sha256"],
            }
        )
    expected_ids = project_controlled_subject_ids(
        load_phase1_identity_records(
            verified_bridge_path=root / BRIDGE_RELPATH,
            workload_root=root / PHASE1_OUT_RELPATH,
        )
    )
    if tuple(sorted(rebuilt_ids)) != expected_ids:
        _successor_identity_conflict("rebuilt subject IDs differ from Phase-1 projection")
    if len(admitted) != 23:
        _successor_identity_conflict(
            f"admitted successor universe is not 23: observed {len(admitted)}"
        )
    admitted.sort(
        key=lambda row: (
            SCALE_RANK[str(row["scale_class"])],
            int(row["total_effective_lines"]),
            int(row["pbf_site_count"]),
            str(row["neutral_snapshot_id"]),
        )
    )
    if admitted[0]["neutral_snapshot_id"] != CLOSED_RANK1_NEUTRAL_SNAPSHOT_ID:
        _successor_identity_conflict("rebuilt rank 1 is not the closed confirmatory subject")
    if admitted[0]["controlled_subject_id"] != CLOSED_RANK1_CONTROLLED_SUBJECT_ID:
        _successor_identity_conflict("rebuilt rank 1 controlled subject ID differs")
    successors = admitted[1:]
    if len(successors) != MAXIMUM_ATTEMPTS:
        _successor_identity_conflict("successor count after dropping rank 1 is not 22")
    rebuilt: list[dict[str, object]] = []
    for ordinal, row in enumerate(successors, start=1):
        rebuilt.append(
            {
                "successor_ordinal": ordinal,
                "old_rank": ordinal + 1,
                "scale_class": row["scale_class"],
                "total_effective_lines": row["total_effective_lines"],
                "pbf_site_count": row["pbf_site_count"],
                "frozen_slots": SLOTS_PER_SUBJECT,
                "neutral_snapshot_id": row["neutral_snapshot_id"],
                "controlled_subject_source_id": row["controlled_subject_source_id"],
                "controlled_subject_id": row["controlled_subject_id"],
                "pbf_file_sha256": row["pbf_file_sha256"],
                "pbf_artifact_sha256": row["pbf_artifact_sha256"],
            }
        )
    _compare_successor_rows(rebuilt, FROZEN_SUCCESSOR_ROWS)
    return tuple(rebuilt)


def inventory_rows_for_subject(
    authority: Mapping[str, object],
    controlled_subject_id: str,
) -> tuple[dict[str, object], ...]:
    inventory = authority.get("inventory")
    if not isinstance(inventory, Mapping):
        _preflight_fail("authority inventory is required")
    slots = inventory.get("slots")
    if not isinstance(slots, Sequence) or isinstance(slots, (str, bytes)):
        _preflight_fail("authority inventory slots are required")
    rows = [
        dict(row)
        for row in slots
        if isinstance(row, Mapping) and row.get("controlled_subject_id") == controlled_subject_id
    ]
    if len(rows) != SLOTS_PER_SUBJECT:
        _preflight_fail(
            f"subject {controlled_subject_id} frozen slot count is {len(rows)}, not 10"
        )
    return tuple(rows)


def _load_official_authority(repo_root: Path) -> dict[str, object]:
    root = Path(repo_root)
    return load_applicability_authority(
        manifest_path=root / AUTHORITY_RELPATH,
        registry_path=root / REGISTRY_RELPATH,
        inventory_path=root / INVENTORY_RELPATH,
        slot_implementation_path=root / SLOT_IMPL_RELPATH,
        predicate_implementation_path=root / PREDICATE_IMPL_RELPATH,
    )


def _confirm_absent_namespace(path: Path, label: str) -> None:
    if path.exists():
        _preflight_fail(f"{label} namespace already exists")
    try:
        path.lstat()
    except FileNotFoundError:
        return
    _preflight_fail(f"{label} namespace is present")


def validate_v2_preflight(
    *,
    repo_root: Path,
    controller_path: Path,
) -> dict[str, object]:
    root = Path(repo_root)
    expected_controller = root / CONTROLLER_RELPATH
    observed_controller = Path(controller_path)
    require_regular_file(observed_controller, "controller")
    require_regular_file(expected_controller, "controller")
    if observed_controller.resolve() != expected_controller.resolve():
        _preflight_fail("controller path is not the unique v2 controller")
    controller_source_sha256 = file_sha256(observed_controller)

    design_path = require_regular_file(root / DESIGN_RELPATH, "design")
    if file_sha256(design_path) != DESIGN_FILE_SHA256:
        _preflight_fail("design file SHA-256 differs")

    authority_path = require_regular_file(root / AUTHORITY_RELPATH, "authority")
    if file_sha256(authority_path) != AUTHORITY_FILE_SHA256:
        _preflight_fail("authority file SHA-256 differs")

    try:
        authority = _load_official_authority(root)
    except EvidenceError as exc:
        if exc.code in {"V2_PREFLIGHT_FAIL", "V2_SUCCESSOR_IDENTITY_CONFLICT"}:
            raise
        raise EvidenceError("V2_PREFLIGHT_FAIL", str(exc)) from exc
    manifest = authority.get("manifest")
    if not isinstance(manifest, Mapping):
        _preflight_fail("authority manifest is required")
    if (
        manifest.get("authority_id") != AUTHORITY_ID
        or manifest.get("schema_version") != AUTHORITY_SCHEMA
        or manifest.get("artifact_sha256") != AUTHORITY_ARTIFACT_SHA256
    ):
        _preflight_fail("authority identity differs")
    inventory = authority.get("inventory")
    registry = authority.get("registry")
    if not isinstance(inventory, Mapping) or not isinstance(registry, Mapping):
        _preflight_fail("authority inventory and registry are required")
    bindings = {
        "slot_inventory_artifact_sha256": (
            inventory.get("artifact_sha256"),
            INVENTORY_ARTIFACT_SHA256,
        ),
        "predicate_registry_artifact_sha256": (
            registry.get("artifact_sha256"),
            REGISTRY_ARTIFACT_SHA256,
        ),
        "slot_inventory_file_sha256": (
            file_sha256(root / INVENTORY_RELPATH),
            INVENTORY_FILE_SHA256,
        ),
        "predicate_registry_file_sha256": (
            file_sha256(root / REGISTRY_RELPATH),
            REGISTRY_FILE_SHA256,
        ),
        "predicate_implementation_source_sha256": (
            file_sha256(root / PREDICATE_IMPL_RELPATH),
            PREDICATE_IMPL_SHA256,
        ),
        "slot_implementation_source_sha256": (
            file_sha256(root / SLOT_IMPL_RELPATH),
            SLOT_IMPL_SHA256,
        ),
        "canonicalization_implementation_source_sha256": (
            file_sha256(root / CANONICALIZATION_IMPL_RELPATH),
            CANONICALIZATION_IMPL_SHA256,
        ),
        "site_policy_sha256": (
            file_sha256(root / SITE_POLICY_RELPATH),
            SITE_POLICY_SHA256,
        ),
        "operator_catalogue_sha256": (
            file_sha256(root / OPERATOR_CATALOGUE_RELPATH),
            OPERATOR_CATALOGUE_SHA256,
        ),
    }
    for field, (observed, expected) in bindings.items():
        if observed != expected:
            _preflight_fail(f"{field} binding differs")
    if (
        manifest.get("slot_inventory_artifact_sha256") != INVENTORY_ARTIFACT_SHA256
        or manifest.get("predicate_registry_artifact_sha256") != REGISTRY_ARTIFACT_SHA256
        or manifest.get("slot_implementation_source_sha256") != SLOT_IMPL_SHA256
        or manifest.get("predicate_implementation_source_sha256") != PREDICATE_IMPL_SHA256
        or manifest.get("canonicalization_implementation_source_sha256")
        != CANONICALIZATION_IMPL_SHA256
        or manifest.get("site_policy_sha256") != SITE_POLICY_SHA256
        or manifest.get("operator_catalogue_sha256") != OPERATOR_CATALOGUE_SHA256
    ):
        _preflight_fail("authority binding table differs")

    rows = rebuild_successor_rows(root)
    _compare_successor_rows(rows, FROZEN_SUCCESSOR_ROWS)

    for row in rows:
        subject_rows = inventory_rows_for_subject(
            authority, str(row["controlled_subject_id"])
        )
        if len(subject_rows) != SLOTS_PER_SUBJECT:
            _preflight_fail("each successor must have exactly 10 frozen slots")
        path = require_regular_file(
            pbf_path(root, str(row["neutral_snapshot_id"])),
            "successor pbf",
        )
        identity = pbf_identity(path)
        if (
            identity["file_sha256"] != row["pbf_file_sha256"]
            or identity["artifact_sha256"] != row["pbf_artifact_sha256"]
            or identity["controlled_subject_source_id"]
            != row["controlled_subject_source_id"]
            or identity["pbf_site_count"] != row["pbf_site_count"]
        ):
            _preflight_fail("successor PBF identity differs from frozen row")

    _confirm_absent_namespace(official_root(root), "official")
    _confirm_absent_namespace(staging_root(root), "staging")

    closure_dir = old_closure_dir(root)
    try:
        entries = sorted(path.name for path in closure_dir.iterdir())
    except OSError as exc:
        _preflight_fail("old rank-1 closure directory is unavailable")
        raise exc
    expected_names = sorted(PRIOR_RANK1_CLOSURE_FILE_SHA256)
    if entries != expected_names:
        _preflight_fail("old rank-1 closure namespace differs")
    for name, expected in PRIOR_RANK1_CLOSURE_FILE_SHA256.items():
        digest = file_sha256(require_regular_file(closure_dir / name, name))
        if digest != expected:
            _preflight_fail(f"old rank-1 closure bytes differ: {name}")

    return {
        "status": "V2_PREFLIGHT_PASS",
        "controller_source_sha256": controller_source_sha256,
        "authority_artifact_sha256": AUTHORITY_ARTIFACT_SHA256,
        "successor_count": 22,
    }


def _execution_fail(detail: str) -> None:
    raise EvidenceError("V2_EXECUTION_FAIL", detail)


def _walk_keys(value: object) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, Mapping):
        keys.update(value)
        for item in value.values():
            keys.update(_walk_keys(item))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for item in value:
            keys.update(_walk_keys(item))
    return keys


def _search_result(
    *,
    status: str,
    code: str | None,
    controller_source_sha256: str | None,
    attempted_count: int,
    first_eligible_successor_ordinal: int | None,
    first_eligible_neutral_snapshot_id: str | None,
    official_terminal_written: bool,
    terminal: dict[str, object] | None,
) -> dict[str, object]:
    return {
        "status": status,
        "code": code,
        "controller_source_sha256": controller_source_sha256,
        "attempted_count": attempted_count,
        "first_eligible_successor_ordinal": first_eligible_successor_ordinal,
        "first_eligible_neutral_snapshot_id": first_eligible_neutral_snapshot_id,
        "official_terminal_written": official_terminal_written,
        "terminal": terminal,
    }


def read_successor_pbf(
    repo_root: Path, successor: Mapping[str, object]
) -> Mapping[str, object]:
    path = pbf_path(repo_root, str(successor["neutral_snapshot_id"]))
    try:
        require_regular_file(path, "successor pbf")
        raw, mode = read_regular_file_snapshot(path, "successor pbf")
    except EvidenceError as exc:
        if exc.code == "V2_PREFLIGHT_FAIL":
            _execution_fail(str(exc))
        raise
    if not stat.S_ISREG(mode):
        _execution_fail("successor pbf is not a regular file")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        _execution_fail("successor pbf is not JSON")
        raise exc
    if not isinstance(payload, Mapping) or canonical_json_bytes(payload) != raw:
        _execution_fail("successor pbf is not canonical JSON")
    sites = payload.get("sites")
    if not isinstance(sites, list):
        _execution_fail("successor pbf sites must be a list")
    identity = {
        "file_sha256": hashlib.sha256(raw).hexdigest(),
        "artifact_sha256": payload.get("artifact_sha256"),
        "controlled_subject_source_id": payload.get("controlled_subject_source_id"),
        "pbf_site_count": len(sites),
    }
    if (
        identity["file_sha256"] != successor["pbf_file_sha256"]
        or identity["artifact_sha256"] != successor["pbf_artifact_sha256"]
        or identity["controlled_subject_source_id"]
        != successor["controlled_subject_source_id"]
        or identity["pbf_site_count"] != successor["pbf_site_count"]
    ):
        _execution_fail("successor PBF identity changed")
    return payload


def canonical_sites_from_pbf(
    controlled_subject_id: str,
    pbf: Mapping[str, object],
) -> list[dict[str, object]]:
    sites = pbf.get("sites")
    if not isinstance(sites, Sequence) or isinstance(sites, (str, bytes)):
        _execution_fail("pbf sites must be a sequence")
    return _sites(controlled_subject_id, sites)


def close_successor_subject(
    *,
    authority: Mapping[str, object],
    successor: Mapping[str, object],
    pbf: Mapping[str, object],
) -> dict[str, object]:
    try:
        rows = inventory_rows_for_subject(
            authority, str(successor["controlled_subject_id"])
        )
    except EvidenceError as exc:
        if exc.code == "V2_PREFLIGHT_FAIL":
            _execution_fail("subject slot count is not 10")
        raise
    if len(rows) != SLOTS_PER_SUBJECT:
        _execution_fail("subject slot count is not 10")
    sites = canonical_sites_from_pbf(str(successor["controlled_subject_id"]), pbf)
    official: list[dict[str, object]] = []
    for row in rows:
        official.append(close_slot_with_authority(authority, row, sites, pbf))
    if len(official) != SLOTS_PER_SUBJECT:
        _execution_fail("closer returned a partial subject")
    attempted = build_attempted_subject(successor=successor, official_closures=official)
    return {"attempted_subject": attempted, "official_closures": tuple(official)}


def derive_subject_eligibility(
    closures: Sequence[Mapping[str, object]],
) -> str:
    if not isinstance(closures, Sequence) or isinstance(closures, (str, bytes)):
        _execution_fail("closures must be a sequence")
    if len(closures) != SLOTS_PER_SUBJECT:
        _execution_fail("subject closure count is not 10")
    states: list[str] = []
    for index, closure in enumerate(closures):
        if not isinstance(closure, Mapping) or "state" not in closure:
            _execution_fail(f"closure {index} is partial")
        state = closure["state"]
        if state not in {
            "SITE_FROZEN",
            "APPLICABILITY_CLOSED_NOT_APPLICABLE",
        }:
            _execution_fail(f"closure {index} has a non-scientific state")
        states.append(state)
    if "SITE_FROZEN" in states:
        return "V2_APPLICABILITY_ELIGIBLE"
    return "V2_APPLICABILITY_INELIGIBLE"


def _official_closure_self_hash(
    *,
    slot_id: object,
    controlled_subject_id: object,
    site_id: object,
    state: object,
) -> str:
    if state == "APPLICABILITY_CLOSED_NOT_APPLICABLE":
        path = "APPLICABILITY_CLOSED_NOT_APPLICABLE"
    elif state == "SITE_FROZEN":
        path = "APPLICABLE"
    else:
        _execution_fail("closure state is not a scientific eligibility state")
    body = {
        "schema_version": "p3-slot-closure-v1",
        "slot_id": slot_id,
        "controlled_subject_id": controlled_subject_id,
        "site_id": site_id,
        "state": state,
        "path": path,
    }
    return canonical_sha256(body)


def closure_terminal_row(closure: Mapping[str, object]) -> dict[str, object]:
    if not isinstance(closure, Mapping):
        _execution_fail("closure must be an object")
    body = {key: value for key, value in closure.items() if key != "artifact_sha256"}
    if closure.get("artifact_sha256") != canonical_sha256(body):
        _execution_fail("official closer self-hash differs")
    row = {
        "slot_id": closure["slot_id"],
        "state": closure["state"],
        "site_id": closure["site_id"],
        "closure_artifact_sha256": closure["artifact_sha256"],
    }
    validate_exact_object(row, TERMINAL_CLOSURE_ROW_SCHEMA, "terminal_closure")
    validate_sha256(row["slot_id"], "terminal_closure.slot_id")
    validate_sha256(row["closure_artifact_sha256"], "terminal_closure.closure_artifact_sha256")
    if row["state"] == "APPLICABILITY_CLOSED_NOT_APPLICABLE":
        if row["site_id"] is not None:
            _execution_fail("not-applicable closure must have null site_id")
    elif row["state"] == "SITE_FROZEN":
        validate_sha256(row["site_id"], "terminal_closure.site_id")
    else:
        _execution_fail("closure state is not a scientific eligibility state")
    if row["closure_artifact_sha256"] != _official_closure_self_hash(
        slot_id=row["slot_id"],
        controlled_subject_id=closure["controlled_subject_id"],
        site_id=row["site_id"],
        state=row["state"],
    ):
        _execution_fail("referenced closure artifact self-hash differs")
    return row


def build_attempted_subject(
    *,
    successor: Mapping[str, object],
    official_closures: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    if len(official_closures) != SLOTS_PER_SUBJECT:
        _execution_fail("attempted subject must contain 10 closures")
    payload = {
        "successor_ordinal": successor["successor_ordinal"],
        "neutral_snapshot_id": successor["neutral_snapshot_id"],
        "controlled_subject_source_id": successor["controlled_subject_source_id"],
        "controlled_subject_id": successor["controlled_subject_id"],
        "eligibility": derive_subject_eligibility(official_closures),
        "closures": [closure_terminal_row(item) for item in official_closures],
    }
    return validate_exact_object(payload, ATTEMPTED_SUBJECT_SCHEMA, "attempted_subject")


def build_cohort_terminal(
    *,
    attempted_subjects: Sequence[Mapping[str, object]],
    controller_source_sha256: str,
) -> dict[str, object]:
    rows = [dict(item) for item in attempted_subjects]
    eligible = [
        row for row in rows if row.get("eligibility") == "V2_APPLICABILITY_ELIGIBLE"
    ]
    if eligible:
        last = rows[-1]
        terminal_status = "V2_ELIGIBLE_SUBJECT_FOUND"
        first_ordinal = last.get("successor_ordinal")
        first_neutral = last.get("neutral_snapshot_id")
    else:
        terminal_status = "V2_COHORT_EXHAUSTED"
        first_ordinal = None
        first_neutral = None
    body = {
        "schema_version": TERMINAL_SCHEMA_VERSION,
        "slice_id": SLICE_ID,
        "design_commit": DESIGN_COMMIT,
        "design_file_sha256": DESIGN_FILE_SHA256,
        "authority_artifact_sha256": AUTHORITY_ARTIFACT_SHA256,
        "controller_source_sha256": controller_source_sha256,
        "prior_closure_commit": PRIOR_CLOSURE_COMMIT,
        "terminal_status": terminal_status,
        "attempted_subjects": rows,
        "first_eligible_successor_ordinal": first_ordinal,
        "first_eligible_neutral_snapshot_id": first_neutral,
    }
    terminal = {**body, "artifact_sha256": canonical_sha256(body)}
    return validate_cohort_terminal(
        terminal, controller_source_sha256=controller_source_sha256
    )


def validate_cohort_terminal(
    terminal: Mapping[str, object],
    *,
    controller_source_sha256: str,
) -> dict[str, object]:
    payload = validate_exact_object(dict(terminal), COHORT_TERMINAL_SCHEMA, "cohort_terminal")
    body = {key: value for key, value in payload.items() if key != "artifact_sha256"}
    if payload["artifact_sha256"] != canonical_sha256(body):
        _execution_fail("cohort terminal self-hash differs")
    if _walk_keys(payload) & FORBIDDEN_LEAK_KEYS:
        _execution_fail("cohort terminal contains forbidden site fields")
    if payload["controller_source_sha256"] != controller_source_sha256:
        _execution_fail("controller source SHA-256 differs")
    if (
        payload["schema_version"] != TERMINAL_SCHEMA_VERSION
        or payload["slice_id"] != SLICE_ID
        or payload["design_commit"] != DESIGN_COMMIT
        or payload["design_file_sha256"] != DESIGN_FILE_SHA256
        or payload["authority_artifact_sha256"] != AUTHORITY_ARTIFACT_SHA256
        or payload["prior_closure_commit"] != PRIOR_CLOSURE_COMMIT
    ):
        _execution_fail("cohort terminal identity bindings differ")
    attempted = payload["attempted_subjects"]
    if not isinstance(attempted, list) or not attempted:
        _execution_fail("attempted_subjects must be nonempty")
    if len(attempted) > MAXIMUM_ATTEMPTS:
        _execution_fail("attempted subject count exceeds 22")
    authority = _load_official_authority(Path(__file__).resolve().parents[2])
    for index, raw in enumerate(attempted):
        row = validate_exact_object(dict(raw), ATTEMPTED_SUBJECT_SCHEMA, f"attempted[{index}]")
        expected_ordinal = index + 1
        if row["successor_ordinal"] != expected_ordinal:
            _execution_fail("attempted successor ordinals are not contiguous")
        if index >= len(FROZEN_SUCCESSOR_ROWS):
            _execution_fail("attempted subject is outside the frozen successor table")
        frozen = FROZEN_SUCCESSOR_ROWS[index]
        if (
            row["neutral_snapshot_id"] != frozen["neutral_snapshot_id"]
            or row["controlled_subject_source_id"]
            != frozen["controlled_subject_source_id"]
            or row["controlled_subject_id"] != frozen["controlled_subject_id"]
        ):
            _execution_fail("attempted subject identity differs from frozen successor")
        validate_sha256(row["neutral_snapshot_id"], "attempted.neutral_snapshot_id")
        validate_sha256(
            row["controlled_subject_source_id"], "attempted.controlled_subject_source_id"
        )
        validate_sha256(row["controlled_subject_id"], "attempted.controlled_subject_id")
        closures = row["closures"]
        if not isinstance(closures, list) or len(closures) != SLOTS_PER_SUBJECT:
            _execution_fail("attempted subject must contain 10 closures")
        expected_rows = inventory_rows_for_subject(
            authority, str(row["controlled_subject_id"])
        )
        if [item["slot_id"] for item in expected_rows] != [
            item["slot_id"] for item in closures
        ]:
            _execution_fail("closure slot order differs from frozen inventory")
        for closure in closures:
            item = validate_exact_object(
                dict(closure), TERMINAL_CLOSURE_ROW_SCHEMA, "closure"
            )
            if item["state"] == "APPLICABILITY_CLOSED_NOT_APPLICABLE":
                if item["site_id"] is not None:
                    _execution_fail("not-applicable closure must have null site_id")
            elif item["state"] == "SITE_FROZEN":
                validate_sha256(item["site_id"], "closure.site_id")
            else:
                _execution_fail("closure state is not a scientific eligibility state")
            if item["closure_artifact_sha256"] != _official_closure_self_hash(
                slot_id=item["slot_id"],
                controlled_subject_id=row["controlled_subject_id"],
                site_id=item["site_id"],
                state=item["state"],
            ):
                _execution_fail("referenced closure artifact self-hash differs")
        derived = derive_subject_eligibility(closures)
        if row["eligibility"] != derived:
            _execution_fail("eligibility is not derived from the 10 closure states")
        attempted[index] = row
    if payload["terminal_status"] == "V2_ELIGIBLE_SUBJECT_FOUND":
        last = attempted[-1]
        earlier = attempted[:-1]
        if last["eligibility"] != "V2_APPLICABILITY_ELIGIBLE":
            _execution_fail("FOUND terminal last subject is not eligible")
        if any(row["eligibility"] != "V2_APPLICABILITY_INELIGIBLE" for row in earlier):
            _execution_fail("FOUND terminal opened a later subject after an eligible one")
        if any(
            closure["state"] != "APPLICABILITY_CLOSED_NOT_APPLICABLE"
            for row in earlier
            for closure in row["closures"]
        ):
            _execution_fail("FOUND terminal earlier subject is not 10/10 not-applicable")
        if not any(closure["state"] == "SITE_FROZEN" for closure in last["closures"]):
            _execution_fail("FOUND terminal last subject has no SITE_FROZEN closure")
        if payload["first_eligible_successor_ordinal"] != last["successor_ordinal"]:
            _execution_fail("FOUND first_eligible_successor_ordinal differs")
        if payload["first_eligible_neutral_snapshot_id"] != last["neutral_snapshot_id"]:
            _execution_fail("FOUND first_eligible_neutral_snapshot_id differs")
    elif payload["terminal_status"] == "V2_COHORT_EXHAUSTED":
        if len(attempted) != MAXIMUM_ATTEMPTS:
            _execution_fail("EXHAUSTED terminal must contain 22 attempted subjects")
        if [row["successor_ordinal"] for row in attempted] != list(
            range(1, MAXIMUM_ATTEMPTS + 1)
        ):
            _execution_fail("EXHAUSTED ordinals are not 1 through 22")
        if any(
            row["eligibility"] != "V2_APPLICABILITY_INELIGIBLE" for row in attempted
        ):
            _execution_fail("EXHAUSTED terminal contains an eligible subject")
        if any(
            closure["state"] != "APPLICABILITY_CLOSED_NOT_APPLICABLE"
            for row in attempted
            for closure in row["closures"]
        ):
            _execution_fail("EXHAUSTED terminal is not 22x10 not-applicable")
        if (
            payload["first_eligible_successor_ordinal"] is not None
            or payload["first_eligible_neutral_snapshot_id"] is not None
        ):
            _execution_fail("EXHAUSTED first-eligible fields must be null")
    else:
        _execution_fail("terminal_status is not a scientific v2 terminal")
    return payload


def write_subject_closures(
    directory: Path,
    official_closures: Sequence[Mapping[str, object]],
) -> None:
    if not isinstance(official_closures, Sequence) or isinstance(
        official_closures, (str, bytes)
    ):
        _execution_fail("official closures must be a sequence")
    if len(official_closures) != SLOTS_PER_SUBJECT:
        _execution_fail("subject directory requires 10 closures")
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    for closure in official_closures:
        if not isinstance(closure, Mapping):
            _execution_fail("official closure must be an object")
        slot_id = validate_sha256(closure["slot_id"], "slot_id")
        write_canonical_json(
            target / f"slot-closure-{slot_id}.json",
            dict(closure),
            exclusive=True,
        )


def place_subject_directory(
    *,
    staging_subject: Path,
    official_subject: Path,
) -> None:
    official = Path(official_subject)
    staging = Path(staging_subject)
    if official.exists() or official.is_symlink():
        _execution_fail("official subject path exists")
    official.parent.mkdir(parents=True, exist_ok=True)
    os.replace(staging, official)


def write_official_cohort_terminal(
    *,
    staging_terminal: Path,
    official_terminal: Path,
    terminal: Mapping[str, object],
) -> None:
    if not isinstance(terminal, Mapping):
        _execution_fail("cohort terminal must be an object")
    validate_cohort_terminal(
        terminal,
        controller_source_sha256=str(terminal["controller_source_sha256"]),
    )
    staging = Path(staging_terminal)
    official = Path(official_terminal)
    write_canonical_json(staging, dict(terminal), exclusive=True)
    if official.exists() or official.is_symlink():
        _execution_fail("official terminal exists")
    official.parent.mkdir(parents=True, exist_ok=True)
    os.replace(staging, official)


def stdout_summary(result: Mapping[str, object]) -> dict[str, object]:
    payload = {
        "status": result["status"],
        "slice_id": SLICE_ID,
        "design_commit": DESIGN_COMMIT,
        "controller_source_sha256": result["controller_source_sha256"],
        "attempted_count": result["attempted_count"],
        "first_eligible_successor_ordinal": result["first_eligible_successor_ordinal"],
        "official_terminal_written": result["official_terminal_written"],
    }
    validate_exact_object(payload, STDOUT_SUMMARY_SCHEMA, "stdout_summary")
    if _walk_keys(payload) & FORBIDDEN_LEAK_KEYS:
        _execution_fail("stdout summary contains forbidden site fields")
    return payload


def run_search(repo_root: Path) -> dict[str, object]:
    root = Path(repo_root)
    controller_path = Path(__file__).resolve()
    controller_source_sha256 = file_sha256(controller_path)
    attempted: list[dict[str, object]] = []
    search_opened = False
    try:
        try:
            validate_v2_preflight(
                repo_root=root, controller_path=root / CONTROLLER_RELPATH
            )
        except EvidenceError as exc:
            if exc.code in {"V2_PREFLIGHT_FAIL", "V2_SUCCESSOR_IDENTITY_CONFLICT"}:
                return _search_result(
                    status="V2_PREFLIGHT_FAIL",
                    code=exc.code,
                    controller_source_sha256=controller_source_sha256,
                    attempted_count=0,
                    first_eligible_successor_ordinal=None,
                    first_eligible_neutral_snapshot_id=None,
                    official_terminal_written=False,
                    terminal=None,
                )
            raise
        search_opened = True
        ordinals = [row["successor_ordinal"] for row in FROZEN_SUCCESSOR_ROWS]
        if ordinals != list(range(1, len(ordinals) + 1)):
            _execution_fail("successor ordinals are not contiguous")
        if len(ordinals) > MAXIMUM_ATTEMPTS:
            _execution_fail("successor table exceeds maximum attempts")
        authority = _load_official_authority(root)
        for expected_ordinal, successor in enumerate(FROZEN_SUCCESSOR_ROWS, start=1):
            if expected_ordinal > MAXIMUM_ATTEMPTS:
                _execution_fail("search exceeded maximum attempts")
            if successor["successor_ordinal"] != expected_ordinal:
                _execution_fail("successor ordinal skipped or reordered")
            pbf = read_successor_pbf(root, successor)
            closed = close_successor_subject(
                authority=authority, successor=successor, pbf=pbf
            )
            subject = dict(closed["attempted_subject"])
            if subject["successor_ordinal"] != expected_ordinal:
                _execution_fail("closed subject ordinal differs")
            if subject["eligibility"] not in {
                "V2_APPLICABILITY_ELIGIBLE",
                "V2_APPLICABILITY_INELIGIBLE",
            }:
                _execution_fail("subject eligibility is not a scientific label")
            official_closures = closed["official_closures"]
            if len(official_closures) != SLOTS_PER_SUBJECT:
                _execution_fail("partial closures cannot be recorded as ineligible")
            write_subject_closures(
                staging_subject_dir(root, str(successor["neutral_snapshot_id"])),
                official_closures,
            )
            place_subject_directory(
                staging_subject=staging_subject_dir(
                    root, str(successor["neutral_snapshot_id"])
                ),
                official_subject=official_subject_dir(
                    root, str(successor["neutral_snapshot_id"])
                ),
            )
            attempted.append(subject)
            if subject["eligibility"] == "V2_APPLICABILITY_ELIGIBLE":
                terminal = build_cohort_terminal(
                    attempted_subjects=attempted,
                    controller_source_sha256=controller_source_sha256,
                )
                write_official_cohort_terminal(
                    staging_terminal=staging_root(root) / "cohort-terminal.json",
                    official_terminal=official_root(root) / "cohort-terminal.json",
                    terminal=terminal,
                )
                return _search_result(
                    status="V2_ELIGIBLE_SUBJECT_FOUND",
                    code=None,
                    controller_source_sha256=controller_source_sha256,
                    attempted_count=len(attempted),
                    first_eligible_successor_ordinal=terminal[
                        "first_eligible_successor_ordinal"
                    ],
                    first_eligible_neutral_snapshot_id=terminal[
                        "first_eligible_neutral_snapshot_id"
                    ],
                    official_terminal_written=True,
                    terminal=terminal,
                )
            if expected_ordinal == MAXIMUM_ATTEMPTS:
                terminal = build_cohort_terminal(
                    attempted_subjects=attempted,
                    controller_source_sha256=controller_source_sha256,
                )
                write_official_cohort_terminal(
                    staging_terminal=staging_root(root) / "cohort-terminal.json",
                    official_terminal=official_root(root) / "cohort-terminal.json",
                    terminal=terminal,
                )
                return _search_result(
                    status="V2_COHORT_EXHAUSTED",
                    code=None,
                    controller_source_sha256=controller_source_sha256,
                    attempted_count=len(attempted),
                    first_eligible_successor_ordinal=None,
                    first_eligible_neutral_snapshot_id=None,
                    official_terminal_written=True,
                    terminal=terminal,
                )
        _execution_fail("search ended without a scientific terminal")
    except EvidenceError as exc:
        if (
            not search_opened
            and exc.code in {"V2_PREFLIGHT_FAIL", "V2_SUCCESSOR_IDENTITY_CONFLICT"}
        ):
            return _search_result(
                status="V2_PREFLIGHT_FAIL",
                code=exc.code,
                controller_source_sha256=controller_source_sha256,
                attempted_count=len(attempted),
                first_eligible_successor_ordinal=None,
                first_eligible_neutral_snapshot_id=None,
                official_terminal_written=False,
                terminal=None,
            )
        return _search_result(
            status="V2_EXECUTION_FAIL",
            code=exc.code,
            controller_source_sha256=controller_source_sha256,
            attempted_count=len(attempted),
            first_eligible_successor_ordinal=None,
            first_eligible_neutral_snapshot_id=None,
            official_terminal_written=False,
            terminal=None,
        )
    except Exception as exc:
        return _search_result(
            status="V2_EXECUTION_FAIL",
            code="V2_EXECUTION_FAIL",
            controller_source_sha256=controller_source_sha256,
            attempted_count=len(attempted),
            first_eligible_successor_ordinal=None,
            first_eligible_neutral_snapshot_id=None,
            official_terminal_written=False,
            terminal=None,
        )


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


if __name__ == "__main__":
    raise SystemExit(main())
