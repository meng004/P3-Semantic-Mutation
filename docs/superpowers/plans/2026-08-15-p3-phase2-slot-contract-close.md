# P3 Phase 2 Slot, Contract, Package, and Close Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Freeze 350 slots, apply real family predicates, extract
contracts from mounted public documentation, generate `E_CONTRACT`
inputs from those frozen contracts, build Package A, and close Phase 2
with a production helper that proves full-file shuffle identity.

**Architecture:** Slot inventory and predicates are outcome-blind.
`build_contract_authority` is the only contract source. The five
`E_CONTRACT` generators consume frozen contracts; they do not invent
them. If public documentation cannot yield a real contract for an
applicable slot, authority status is
`PHASE2_CONTRACT_AUTHORITY_BLOCKED`.

**Tech Stack:** Python 3.12; `src/p3_v3/slot_inventory.py`;
`src/p3_v3/applicability_predicates.py`;
`src/p3_v3/contract_authority.py`; `src/p3_v3/phase2_close.py`.

## Global Constraints

Master-plan Global Constraints apply. Dummy contracts are forbidden.
Always-true and always-false production predicates are forbidden.
In-repo Phase 1 artifacts do not include the 35 blinded archives, so
production X8 cannot claim contract emission until materialization
plus extraction succeed.

---

## File map

| File | Responsibility |
|---|---|
| `src/p3_v3/slot_inventory.py` | 350 slots; `slot_id`; `close_subject_slots`; `freeze_contract` |
| `src/p3_v3/applicability_predicates.py` | INV/MONO/CONV/DYN/CMP static rules |
| `src/p3_v3/contract_authority.py` | `build_contract_authority` |
| `src/p3_v3/input_generators/contract_enum_domain_v1.py` | E_CONTRACT generator |
| `src/p3_v3/input_generators/contract_numeric_domain_v1.py` | E_CONTRACT generator |
| `src/p3_v3/input_generators/contract_array_domain_v1.py` | E_CONTRACT generator |
| `src/p3_v3/input_generators/contract_sequence_domain_v1.py` | E_CONTRACT generator |
| `src/p3_v3/input_generators/contract_relation_pair_domain_v1.py` | E_CONTRACT generator |
| `src/p3_v3/packages.py` | `build_phase2_package_a`, `collect_package_leaks` |
| `src/p3_v3/phase2_close.py` | `close_phase2_production` |
| `tests/p3_v3/test_phase2_slot_close.py` | F0/F1 |
| `tests/p3_v3/test_phase2_package_a.py` | G |
| `tests/p3_v3/test_phase2_close.py` | H |

`freeze_contract` and `close_subject_slots` live only in
`src/p3_v3/slot_inventory.py`. Tests and commits import them from that
module.

---

## Predicate rules

Sites have `path`, `symbol`, `start_line`, `start_col`, `end_line`,
`end_col`, `site_id`. Join a site to a public-frame row when
`site.path == row.provenance_path` and `site.symbol` equals the
qualname tail of `row.entrypoint` exactly.

| family | accepted site kinds after join | required fields | decision_rule |
|---|---|---|---|
| INV | PUBLIC_API | path, symbol, category | category==PUBLIC_API and schema_kind in {NUMERIC_ARRAY_DOMAIN_V1, JSON_SCHEMA_DRAFT2020_12_V1} |
| MONO | PUBLIC_API | path, symbol, schema_kind | category==PUBLIC_API and schema_kind==NUMERIC_ARRAY_DOMAIN_V1 |
| CONV | BENCHMARK, EXAMPLE | path, symbol | category in {BENCHMARK, EXAMPLE} and symbol casefold has an exact token from {iterate, step, solve, minimize, converge} |
| DYN | EXAMPLE, PROJECT_TEST | path, symbol | category in {EXAMPLE, PROJECT_TEST} and path casefold has an exact token from {sim, traj, dyn, evolve, integrate} |
| CMP | CLI | path, symbol, schema_kind | category==CLI or schema_kind in {TEXT_IO_SCHEMA_V1, CLI_TOKEN_GRAMMAR_V1} |

No production predicate may return True for every site or False for
every site in the fixture set used to freeze the registry.

---

## Contract authority

```python
class ApplicabilityPredicateSpec(TypedDict):
    predicate_id: str
    semantic_contract_family: str
    accepted_site_kinds: list[str]
    required_static_fields: list[str]
    decision_rule: dict[str, object]
    implementation_path: str
    implementation_source_sha256: str


def build_contract_authority(
    slot_inventory: Mapping[str, object],
    frozen_sites: Sequence[Mapping[str, object]],
    public_behavior_frames: Sequence[Mapping[str, object]],
    public_documentation_manifest: Mapping[str, object],
    predicate_registry: Mapping[str, object],
) -> dict:
    """Extract contracts from public docs. Never read profiling, patch, MR, or outcome."""
```

Extraction algorithm:

1. Close each slot with the family predicate and frozen site order.
2. For `NOT_APPLICABLE`, emit no contract.
3. For applicable slots, scan `public_documentation_manifest` files
   whose class is `PUBLIC_DOC` or whose path matches
   `README*`, `docs/**/*.md`, or `include/**`.
4. Keep sentences that contain the site `symbol` as an exact token and
   contain at least one family token:

   - INV: invariant, conserve, conservation, residual
   - MONO: monotonic, monotone, increasing, decreasing, ordered
   - CONV: converge, convergence, limit, tolerance
   - DYN: trajectory, dynamics, evolve, state
   - CMP: compare, consistent, equivalent, representation

5. The first surviving sentence in canonical file-path then byte-offset
   order becomes the oracle statement.
6. Domain and generator come from the joined public schema kind.
7. Tolerance is the frozen map
   `{NUMERIC_ARRAY_DOMAIN_V1: {"abs": 0.0, "rel": 0.0}, other: {"exact": True}}`.
8. Activation obligation is `{"must_invoke_symbol": site.symbol}`.
9. Expected violation direction is
   `{INV: "break_invariant", MONO: "reverse_order", CONV: "prevent_convergence", DYN: "diverge_state", CMP: "break_consistency"}`.

If step 4 yields no sentence for an applicable slot, return
`{"status": "PHASE2_CONTRACT_AUTHORITY_BLOCKED", "blocked_slot_id": slot_id}`
and do not invent a contract.

Capability tests plant family sentences in fixture public docs. Those
fixtures are not production contracts for the 35 subjects.

Production status on current in-repo materials:
`PHASE2_CONTRACT_AUTHORITY_BLOCKED` until the 35 archives are mounted
and extraction succeeds or the controller changes the rule.

---

### Task F0: 350 slots and predicates

**Files:**
- Create: `src/p3_v3/slot_inventory.py`
- Create: `src/p3_v3/applicability_predicates.py`
- Test: `tests/p3_v3/test_phase2_slot_close.py`

```python
SEMANTIC_CONTRACT_FAMILIES = ("INV", "MONO", "CONV", "DYN", "CMP")
MECHANISM_ORDER = ("CE", "OS", "HP", "TF", "SI")


def slot_id(subject_id: str, family: str, slot_ordinal: int, mechanism: str) -> str:
    return canonical_sha256({
        "domain": "P3-SLOT-IDENTITY-v1",
        "controlled_subject_id": subject_id,
        "semantic_contract_family": family,
        "slot_ordinal": slot_ordinal,
        "permitted_construction_mechanism": mechanism,
    })


def freeze_slot_inventory(subject_ids: Sequence[str]) -> dict:
    """Return exactly 350 pre-bound slots from the V5 matrix."""
```

- [ ] **Step 1: Write the failing tests**

```python
from p3_v3.applicability_predicates import evaluate_predicate
from p3_v3.slot_inventory import SEMANTIC_CONTRACT_FAMILIES, freeze_slot_inventory, slot_id


def test_slot_inventory_has_exactly_350_prebound_slots() -> None:
    subjects = [f"{index:064x}" for index in range(35)]
    inventory = freeze_slot_inventory(subjects)
    assert inventory["expected_count"] == 350
    assert len(inventory["slots"]) == 350
    assert {slot["semantic_contract_family"] for slot in inventory["slots"]} == set(
        SEMANTIC_CONTRACT_FAMILIES
    )
    reconstructed = {
        slot_id(
            slot["controlled_subject_id"],
            slot["semantic_contract_family"],
            slot["slot_ordinal"],
            slot["permitted_construction_mechanism"],
        )
        for slot in inventory["slots"]
    }
    assert reconstructed == {slot["slot_id"] for slot in inventory["slots"]}


def test_inv_predicate_is_not_constant() -> None:
    numeric_api = {
        "path": "src/pkg/mod.py",
        "symbol": "norm",
        "category": "PUBLIC_API",
        "schema_kind": "NUMERIC_ARRAY_DOMAIN_V1",
    }
    cli = {
        "path": "src/pkg/cli.py",
        "symbol": "main",
        "category": "CLI",
        "schema_kind": "CLI_TOKEN_GRAMMAR_V1",
    }
    assert evaluate_predicate("INV", numeric_api) is True
    assert evaluate_predicate("INV", cli) is False
```

- [ ] **Step 2: Run the tests and confirm they fail**

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest \
  tests/p3_v3/test_phase2_slot_close.py::test_slot_inventory_has_exactly_350_prebound_slots \
  tests/p3_v3/test_phase2_slot_close.py::test_inv_predicate_is_not_constant -q
```

Expected: FAIL because the modules are absent.

- [ ] **Step 3: Minimal implementation**

```python
from p3_v3.artifacts import canonical_sha256

SEMANTIC_CONTRACT_FAMILIES = ("INV", "MONO", "CONV", "DYN", "CMP")
MECHANISM_ORDER = ("CE", "OS", "HP", "TF", "SI")
CONV_TOKENS = frozenset({"iterate", "step", "solve", "minimize", "converge"})
DYN_TOKENS = frozenset({"sim", "traj", "dyn", "evolve", "integrate"})


def slot_id(subject_id, family, slot_ordinal, mechanism):
    return canonical_sha256({
        "domain": "P3-SLOT-IDENTITY-v1",
        "controlled_subject_id": subject_id,
        "semantic_contract_family": family,
        "slot_ordinal": slot_ordinal,
        "permitted_construction_mechanism": mechanism,
    })


def freeze_slot_inventory(subject_ids):
    slots = []
    for subject_id in subject_ids:
        for index, family in enumerate(SEMANTIC_CONTRACT_FAMILIES):
            for ordinal in (0, 1):
                mechanism = MECHANISM_ORDER[(index + ordinal) % 5]
                slots.append({
                    "slot_id": slot_id(subject_id, family, ordinal, mechanism),
                    "controlled_subject_id": subject_id,
                    "semantic_contract_family": family,
                    "slot_ordinal": ordinal,
                    "permitted_construction_mechanism": mechanism,
                })
    body = {"expected_count": 350, "slots": slots}
    return {**body, "artifact_sha256": canonical_sha256(body)}


def _has_token(text, tokens):
    parts = str(text).casefold().replace("/", " ").replace("_", " ").split()
    return any(token in parts for token in tokens)


def evaluate_predicate(family, site):
    category = site.get("category")
    schema_kind = site.get("schema_kind")
    if family == "INV":
        return category == "PUBLIC_API" and schema_kind in {
            "NUMERIC_ARRAY_DOMAIN_V1",
            "JSON_SCHEMA_DRAFT2020_12_V1",
        }
    if family == "MONO":
        return category == "PUBLIC_API" and schema_kind == "NUMERIC_ARRAY_DOMAIN_V1"
    if family == "CONV":
        return category in {"BENCHMARK", "EXAMPLE"} and _has_token(site.get("symbol", ""), CONV_TOKENS)
    if family == "DYN":
        return category in {"EXAMPLE", "PROJECT_TEST"} and _has_token(site.get("path", ""), DYN_TOKENS)
    if family == "CMP":
        return category == "CLI" or schema_kind in {"TEXT_IO_SCHEMA_V1", "CLI_TOKEN_GRAMMAR_V1"}
    raise ValueError(family)
```

- [ ] **Step 4: Re-run those tests and confirm they pass**

Same command. Expected: PASS.

- [ ] **Step 5: Commit**

```bash
rtk git add src/p3_v3/slot_inventory.py src/p3_v3/applicability_predicates.py \
  tests/p3_v3/test_phase2_slot_close.py
rtk git commit -m "feat(p3-v3): freeze 350 slots and family predicates" -m "Bind family, mechanism, and non-constant static predicates before profiling outcomes."
```

### Task F1: Contract authority and E_CONTRACT generators

**Files:**
- Create: `src/p3_v3/contract_authority.py`
- Modify: `src/p3_v3/slot_inventory.py` add `freeze_contract`,
  `close_subject_slots`
- Create the five `src/p3_v3/input_generators/contract_*_v1.py` files
- Modify: `src/p3_v3/bridge_and_frames.py` `_CONTRACT_SCHEMA`
- Test: `tests/p3_v3/test_phase2_slot_close.py`

```python
def freeze_contract(applicable_slot: Mapping[str, object], contract: Mapping[str, object]) -> dict:
    """Freeze a complete contract on SITE_FROZEN only."""


def close_subject_slots(
    subject: Mapping[str, object],
    sites: Sequence[Mapping[str, object]],
    registry: Mapping[str, object],
    authority: Mapping[str, object],
) -> list[dict]:
    """One legal path per slot. Contracts come only from authority."""
```

- [ ] **Step 1: Write the failing tests**

```python
import pytest

from p3_v3.artifacts import EvidenceError, canonical_json_bytes
from p3_v3.contract_authority import build_contract_authority
from p3_v3.slot_inventory import close_subject_slots, freeze_contract, freeze_slot_inventory


def fixture_docs(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text(
        "The function norm conserves the residual of the input vector.\n"
        "The function norm is monotonic in the input magnitude.\n",
        encoding="utf-8",
    )
    return {
        "files": [{
            "path": "README.md",
            "class": "PUBLIC_DOC",
            "sha256": "00" * 32,
        }],
        "root": str(tmp_path),
    }


def fixture_sites():
    return [{
        "site_id": "11" * 32,
        "path": "src/pkg/mod.py",
        "symbol": "norm",
        "start_line": 1,
        "start_col": 0,
        "end_line": 2,
        "end_col": 0,
        "category": "PUBLIC_API",
        "schema_kind": "NUMERIC_ARRAY_DOMAIN_V1",
    }]


def test_authority_extracts_inv_contract_from_public_docs(tmp_path) -> None:
    subjects = ["aa" * 32]
    inventory = freeze_slot_inventory(subjects)
    authority = build_contract_authority(
        inventory,
        fixture_sites(),
        [{"rows": [{"provenance_path": "src/pkg/mod.py", "entrypoint": "pkg.mod:norm", "category": "PUBLIC_API", "schema_kind": "NUMERIC_ARRAY_DOMAIN_V1"}]}],
        fixture_docs(tmp_path),
        {"predicates": ["INV"]},
    )
    assert authority["status"] != "PHASE2_CONTRACT_AUTHORITY_BLOCKED"
    inv_slot = next(
        slot for slot in inventory["slots"]
        if slot["semantic_contract_family"] == "INV" and slot["slot_ordinal"] == 0
    )
    contract = authority["contracts"][inv_slot["slot_id"]]
    assert "conserves the residual" in contract["oracle"]["statement"]


def test_authority_blocks_when_docs_lack_family_sentence(tmp_path) -> None:
    readme = tmp_path / "README.md"
    readme.write_text("No relevant sentence.\n", encoding="utf-8")
    subjects = ["aa" * 32]
    inventory = freeze_slot_inventory(subjects)
    authority = build_contract_authority(
        inventory,
        fixture_sites(),
        [{"rows": [{"provenance_path": "src/pkg/mod.py", "entrypoint": "pkg.mod:norm", "category": "PUBLIC_API", "schema_kind": "NUMERIC_ARRAY_DOMAIN_V1"}]}],
        {"files": [{"path": "README.md", "class": "PUBLIC_DOC", "sha256": "00" * 32}], "root": str(tmp_path)},
        {"predicates": ["INV"]},
    )
    assert authority["status"] == "PHASE2_CONTRACT_AUTHORITY_BLOCKED"


def test_not_applicable_rejects_contract() -> None:
    closed = {
        "state": "APPLICABILITY_CLOSED_NOT_APPLICABLE",
        "path": "APPLICABILITY_CLOSED_NOT_APPLICABLE",
        "slot_id": "11" * 32,
        "controlled_subject_id": "aa" * 32,
        "site_id": None,
    }
    with pytest.raises(EvidenceError):
        freeze_contract(closed, {"contract_id": "22" * 32})


def test_outcome_injection_is_rejected(tmp_path) -> None:
    subjects = ["aa" * 32]
    inventory = freeze_slot_inventory(subjects)
    docs = fixture_docs(tmp_path)
    docs["scientific_outcome"] = "MR_VIOLATION"
    with pytest.raises(EvidenceError, match="E_OUTCOME_INJECTION"):
        build_contract_authority(
            inventory,
            fixture_sites(),
            [{"rows": []}],
            docs,
            {"predicates": ["INV"]},
        )
```

Each generator implements `generate(schema_bytes: bytes, seed: int) -> dict`
like the E_COMMON generators. IDs stay
`CONTRACT_ENUM_DOMAIN_V1`, `CONTRACT_NUMERIC_DOMAIN_V1`,
`CONTRACT_ARRAY_DOMAIN_V1`, `CONTRACT_SEQUENCE_DOMAIN_V1`,
`CONTRACT_RELATION_PAIR_DOMAIN_V1`.

- [ ] **Step 2: Run the tests and confirm they fail**

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest \
  tests/p3_v3/test_phase2_slot_close.py -q
```

Expected: FAIL because `contract_authority` or `freeze_contract` is
absent.

- [ ] **Step 3: Minimal implementation**

Implement the extraction algorithm in `build_contract_authority`.
`close_subject_slots` reads `authority["contracts"]` only.

Each generator is a domain sampler. Put this function in all five
modules, changing only `GENERATOR_ID` and the payload key:

```python
from p3_v3.artifacts import EvidenceError, canonical_sha256


def generate(schema_bytes: bytes, seed: int) -> dict:
    if not schema_bytes:
        raise EvidenceError("E_CONTRACT_DOMAIN", "frozen domain bytes are absent")
    payload = {
        "generator_id": GENERATOR_ID,
        "seed": seed,
        "domain_sha256": canonical_sha256({"bytes": schema_bytes.hex()}),
    }
    return {**payload, "artifact_sha256": canonical_sha256(payload)}
```

| file | GENERATOR_ID |
|---|---|
| `contract_enum_domain_v1.py` | `CONTRACT_ENUM_DOMAIN_V1` |
| `contract_numeric_domain_v1.py` | `CONTRACT_NUMERIC_DOMAIN_V1` |
| `contract_array_domain_v1.py` | `CONTRACT_ARRAY_DOMAIN_V1` |
| `contract_sequence_domain_v1.py` | `CONTRACT_SEQUENCE_DOMAIN_V1` |
| `contract_relation_pair_domain_v1.py` | `CONTRACT_RELATION_PAIR_DOMAIN_V1` |

- [ ] **Step 4: Re-run the tests and confirm they pass**

Same command. Expected: PASS.

- [ ] **Step 5: Commit**

```bash
rtk git add src/p3_v3/contract_authority.py src/p3_v3/slot_inventory.py \
  src/p3_v3/bridge_and_frames.py \
  src/p3_v3/input_generators/contract_enum_domain_v1.py \
  src/p3_v3/input_generators/contract_numeric_domain_v1.py \
  src/p3_v3/input_generators/contract_array_domain_v1.py \
  src/p3_v3/input_generators/contract_sequence_domain_v1.py \
  src/p3_v3/input_generators/contract_relation_pair_domain_v1.py \
  tests/p3_v3/test_phase2_slot_close.py
rtk git commit -m "feat(p3-v3): extract contracts from public docs or block" -m "Do not invent dummy contracts. Generators consume frozen domains only."
```

### Task G: Package A

**Files:**
- Modify: `src/p3_v3/packages.py`
- Test: `tests/p3_v3/test_phase2_package_a.py`

```python
def build_phase2_package_a(source_root: Path, file_specs, parents) -> dict:
    return build_package("CONSTRUCTION_A", source_root, file_specs, parents)


def collect_package_leaks(root: Path, manifest: Mapping[str, object]) -> list[dict]:
    """Report class, full relative path, and semantic-field leaks."""
```

- [ ] **Step 1: Write the failing tests**

```python
import pytest

from p3_v3.artifacts import EvidenceError
from p3_v3.packages import (
    PROPOSER_ALLOWED_CLASSES,
    build_phase2_package_a,
    collect_package_leaks,
    materialize_package,
)


def test_clean_proposer_view_has_no_leaks(tmp_path) -> None:
    src = tmp_path / "src"
    (src / "frames").mkdir(parents=True)
    (src / "frames/public-behavior-frame.json").write_text("{}\n", encoding="utf-8")
    specs = [{"path": "frames/public-behavior-frame.json", "class": "PUBLIC_BEHAVIOR_FRAME"}]
    manifest = build_phase2_package_a(src, specs, parents=["aa" * 32])
    materialize_package(src, tmp_path / "proposer", manifest, allowed_classes=PROPOSER_ALLOWED_CLASSES)
    assert collect_package_leaks(tmp_path / "proposer", manifest) == []


def test_poisoned_semantic_field_is_a_leak(tmp_path) -> None:
    src = tmp_path / "src"
    (src / "docs").mkdir(parents=True)
    (src / "docs/readme.json").write_text(
        '{"evaluation_input_class":"E_COMMON","evaluation_input_id":"abc"}\n',
        encoding="utf-8",
    )
    specs = [{"path": "docs/readme.json", "class": "PUBLIC_DOC"}]
    manifest = build_phase2_package_a(src, specs, parents=["aa" * 32])
    with pytest.raises(EvidenceError, match="E_PACKAGE_LEAK"):
        materialize_package(
            src,
            tmp_path / "proposer",
            manifest,
            allowed_classes=PROPOSER_ALLOWED_CLASSES,
        )
```

- [ ] **Step 2: Run the tests and confirm they fail**

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest \
  tests/p3_v3/test_phase2_package_a.py -q
```

Expected: FAIL because `build_phase2_package_a` is absent.

- [ ] **Step 3: Minimal implementation**

Call `build_package("CONSTRUCTION_A", source_root, file_specs, parents,
allowed_classes=ALLOWED_CLASSES["CONSTRUCTION_A"])`. Make
`materialize_package` raise `E_PACKAGE_LEAK` when
`collect_package_leaks` is non-empty on the destination.

- [ ] **Step 4: Re-run the tests and confirm they pass**

Same command. Expected: PASS.

- [ ] **Step 5: Commit**

```bash
rtk git add src/p3_v3/packages.py tests/p3_v3/test_phase2_package_a.py
rtk git commit -m "feat(p3-v3): detect Package A leakage by class, path, and fields" -m "Reject poisoned proposer materialization with E_PACKAGE_LEAK."
```

### Task H: Production close helper

**Files:**
- Create: `src/p3_v3/phase2_close.py`
- Test: `tests/p3_v3/test_phase2_close.py`

```python
def close_phase2_production(
    phase_id: str,
    protocol_sha256: str,
    expected_jobs: Sequence[str],
    ledger_path: Path,
    output_manifest: Mapping[str, object],
    attempt_inventory: Sequence[Mapping[str, object]],
    first_output_root: Path,
    second_output_root: Path,
) -> dict:
    """Close PHASE_1. Shuffle identity compares two output trees."""
```

`expected_job_count` is `len(expected_jobs)`.
`terminal_result_count` is the number of terminal results.
`attempt_count` is `len(attempt_inventory)` and may be larger.
Hash files only, never directories.

- [ ] **Step 1: Write the failing tests**

```python
from pathlib import Path

from p3_v3.artifacts import canonical_sha256, file_sha256
from p3_v3.phase2_close import close_phase2_production


def file_tree(root: Path) -> dict:
    files = []
    for path in sorted(root.rglob("*")):
        if path.is_file():
            files.append({
                "path": path.relative_to(root).as_posix(),
                "sha256": file_sha256(path),
            })
    return {"files": files, "artifact_sha256": canonical_sha256({"files": files})}


def test_phase2_close_helper_compares_two_output_trees(tmp_path: Path) -> None:
    first = tmp_path / "out-a"
    second = tmp_path / "out-b"
    (first / "frames").mkdir(parents=True)
    (second / "frames").mkdir(parents=True)
    (first / "frames/subject-frames.json").write_text("{}\n", encoding="utf-8")
    (second / "frames/subject-frames.json").write_text("{}\n", encoding="utf-8")
    manifest_body = file_tree(first)
    receipt = close_phase2_production(
        "PHASE_1",
        "aa" * 32,
        ["job-1"],
        tmp_path / "ledger.jsonl",
        manifest_body,
        [
            {"job_id": "job-1", "attempt": 1, "status": "FAIL_INFRASTRUCTURE"},
            {"job_id": "job-1", "attempt": 2, "status": "PASS"},
        ],
        first,
        second,
    )
    assert receipt["phase_id"] == "PHASE_1"
    assert receipt["expected_job_count"] == 1
    assert receipt["terminal_result_count"] == 1
    assert receipt["attempt_count"] == 2
    assert receipt["failed_attempt_count"] == 1
    assert receipt["shuffle_byte_identical"] is True
    assert receipt["output_manifest_sha256"] == manifest_body["artifact_sha256"]
    assert receipt["output_manifest_sha256"] != "pending"


def test_phase2_close_rejects_directory_as_file_hash(tmp_path: Path) -> None:
    first = tmp_path / "out-a"
    second = tmp_path / "out-b"
    (first / "frames").mkdir(parents=True)
    (second / "frames").mkdir(parents=True)
    (first / "frames/subject-frames.json").write_text("{}\n", encoding="utf-8")
    (second / "frames/subject-frames.json").write_text("{}\n", encoding="utf-8")
    poisoned = {
        "files": [{"path": "frames", "sha256": "aa" * 32}],
        "artifact_sha256": "bb" * 32,
    }
    from p3_v3.artifacts import EvidenceError
    import pytest

    with pytest.raises(EvidenceError, match="E_PHASE2_CLOSE"):
        close_phase2_production(
            "PHASE_1",
            "aa" * 32,
            ["job-1"],
            tmp_path / "ledger.jsonl",
            poisoned,
            [{"job_id": "job-1", "attempt": 1, "status": "PASS"}],
            first,
            second,
        )
```

`close_phase2_production` compares the two file trees itself. It does
not call `close_phase` and does not require a scientific ledger writer
in this unit test. `terminal_result_count` is the number of distinct
`job_id`s that have a terminal attempt. `attempt_count` is
`len(attempt_inventory)`.

- [ ] **Step 2: Run the tests and confirm they fail**

```bash
rtk env PYTHONPATH=src /opt/anaconda3/bin/python -m pytest \
  tests/p3_v3/test_phase2_close.py -q
```

Expected: FAIL because `close_phase2_production` is absent.

- [ ] **Step 3: Minimal implementation**

Compare `file_tree(first_output_root)` to `file_tree(second_output_root)`.
Count jobs and attempts separately. Hash files only.

- [ ] **Step 4: Re-run the tests and confirm they pass**

Same command. Expected: PASS.

- [ ] **Step 5: Commit**

```bash
rtk git add src/p3_v3/phase2_close.py tests/p3_v3/test_phase2_close.py
rtk git commit -m "feat(p3-v3): add Phase 2 production close helper" -m "Compare two output trees and keep attempt counts separate from job counts."
```

---

## Acceptance

1. 350 slots exist and reconstruct `slot_id`.
2. Predicates are non-constant.
3. Contract authority extracts or blocks. It does not invent.
4. Package A has a clean test and a poisoned `E_PACKAGE_LEAK` test.
5. Close compares two file trees and separates attempt vs job counts.
6. Production contract emission on current in-repo materials remains
   `PHASE2_CONTRACT_AUTHORITY_BLOCKED`.
