"""Nine-stage production processor for frozen multiproject successors.

The public entry remains ``process_production_subject(successor, *, repo_root)``.
Private seams may be injected for synthetic fixture tests. Default seams reuse
existing production modules; they do not copy ordinal-8 scripts.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from p3_v3.artifacts import EvidenceError, file_sha256, read_canonical_json, validate_sha256
from p3_v3.applicability_predicates import close_slot_with_authority, load_applicability_authority
from p3_v3.bridge_and_frames import validate_contract_generator_registry
from p3_v3.prospective_multiproject import (
    AUTHORITY_RELPATH,
    FIRST_SUCCESSOR_ORDINAL,
    LAST_SUCCESSOR_ORDINAL,
    MAX_PAIRS_PER_SUBJECT,
    OFFICIAL_RELDIR,
    PRODUCTION_PROCESSOR_STAGES,
    STAGING_RELDIR,
    SubjectPipelineResult,
    SubjectTerminal,
    SuccessorIdentity,
    VERIFIED_BRIDGE_RELPATH,
    _require_production_successor,
    bind_production_project_identity,
    load_frozen_bridge_identity_records,
    load_frozen_successors,
    production_project_binder,
)

PROCESSOR_IMPLEMENTATION_KIND = "nine_stage_orchestration"
ARCHIVE_RELDIR = Path("data/p3_v3/p12_intake/archives")
EXTRACTED_RELDIR = Path("data/p3_v3/p12_intake/extracted")
DESCRIPTOR_RELDIR = Path("data/p3_v3/p12_intake/descriptors")
PBF_RELDIR = Path("data/p3_v3/phase1_frames/out")
INVENTORY_RELPATH = Path("data/p3_v3/phase2/slot-inventory.json")
PREDICATE_REGISTRY_RELPATH = Path("data/p3_v3/protocol/applicability-predicate-registry.json")
CONTRACT_REGISTRY_RELPATH = Path("data/p3_v3/protocol/contract-generator-registry.json")
SLOT_IMPLEMENTATION_RELPATH = Path("src/p3_v3/slot_inventory.py")
PREDICATE_IMPLEMENTATION_RELPATH = Path("src/p3_v3/applicability_predicates.py")
FROZEN_INPUTS_PER_PAIR = 5
_VARIANT_ORDER = ("original", "semantic", "syntactic")
_SITE_FROZEN = "SITE_FROZEN"
_NOT_APPLICABLE = "APPLICABILITY_CLOSED_NOT_APPLICABLE"
_PIPELINE_FAILURE_CODES = frozenset({
    SubjectTerminal.IDENTITY_CONFLICT.value,
    SubjectTerminal.INFRASTRUCTURE_FAILURE.value,
})
_AUTHORITY_GAP_CODES = frozenset({
    "SOURCE_RECOVERY_AUTHORITY_REQUIRED",
    "APPLICABILITY_EXECUTION_AUTHORITY_REQUIRED",
    "CONTRACT_AUTHORITY_REQUIRED",
    "PAIRED_CONSTRUCTION_AUTHORITY_REQUIRED",
    "CONTROLLED_RUNNER_AUTHORITY_REQUIRED",
    "OVERLAP_EXECUTION_AUTHORITY_REQUIRED",
})


@dataclass(frozen=True)
class FrozenSubjectBinding:
    successor: SuccessorIdentity
    bridge_record: Mapping[str, object]
    project_cluster_key: str


@dataclass(frozen=True)
class RecoveredSource:
    archive_path: Path
    archive_sha256: str
    tree_sha256: str
    extracted_root: Path
    build_descriptor_sha256: str


@dataclass(frozen=True)
class SlotClosureRecord:
    slot_id: str
    controlled_subject_id: str
    state: str
    site_id: str | None = None


@dataclass(frozen=True)
class AuthorizedContract:
    slot_id: str
    contract_id: str
    generator_id: str
    site_id: str
    input_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class CanonicalPair:
    slot_id: str
    input_ids: tuple[str, ...]
    semantic_kind: str
    syntactic_kind: str
    semantic_patch_sha256: str
    syntactic_patch_sha256: str
    semantic_tree_sha256: str
    syntactic_tree_sha256: str


@dataclass(frozen=True)
class VariantResult:
    variant: str
    input_ids: tuple[str, ...]
    complete: bool


@dataclass(frozen=True)
class PairExecutionRecord:
    pair: CanonicalPair
    original: VariantResult
    semantic: VariantResult
    syntactic: VariantResult
    execution_order: tuple[str, ...]


@dataclass(frozen=True)
class PairOverlapRecord:
    pair: CanonicalPair
    normalized_patch_exact: bool
    mutant_tree_exact: bool
    normalized_patch_present: bool = True
    mutant_tree_present: bool = True


@dataclass(frozen=True)
class ProductionProcessorSeams:
    recover_source: Callable[[FrozenSubjectBinding, Path], RecoveredSource]
    close_applicability: Callable[
        [FrozenSubjectBinding, RecoveredSource, Path], Sequence[SlotClosureRecord]
    ]
    freeze_contracts: Callable[
        [FrozenSubjectBinding, Sequence[SlotClosureRecord], Path],
        Sequence[AuthorizedContract],
    ]
    construct_pairs: Callable[
        [FrozenSubjectBinding, Sequence[AuthorizedContract], Path],
        Sequence[CanonicalPair],
    ]
    execute_pairs: Callable[
        [FrozenSubjectBinding, Sequence[CanonicalPair], Path],
        Sequence[PairExecutionRecord],
    ]
    measure_overlap: Callable[
        [FrozenSubjectBinding, Sequence[PairExecutionRecord], Path],
        Sequence[PairOverlapRecord],
    ]


def production_processor_is_unconditional_stub() -> bool:
    return False


def _record_stage(stage_trace: list[str] | None, name: str) -> None:
    if stage_trace is None:
        return
    if name in stage_trace:
        raise EvidenceError("IDENTITY_CONFLICT", f"stage {name} invoked more than once")
    if name not in PRODUCTION_PROCESSOR_STAGES:
        raise EvidenceError("IDENTITY_CONFLICT", f"unknown processor stage {name}")
    expected = [item for item in PRODUCTION_PROCESSOR_STAGES if item in {*stage_trace, name}]
    if tuple(stage_trace) + (name,) != tuple(expected):
        raise EvidenceError("IDENTITY_CONFLICT", "processor stages ran out of frozen order")
    stage_trace.append(name)


def freeze_subject_identity(successor: SuccessorIdentity, repo_root: Path) -> FrozenSubjectBinding:
    locked = _require_production_successor(successor)
    records = load_frozen_bridge_identity_records(repo_root)
    matches = [
        row for row in records if row.get("neutral_snapshot_id") == locked.neutral_snapshot_id
    ]
    if len(matches) != 1:
        raise EvidenceError("IDENTITY_CONFLICT", "frozen identity does not uniquely match successor")
    key = bind_production_project_identity(locked, repo_root=repo_root)
    return FrozenSubjectBinding(
        successor=locked,
        bridge_record=matches[0],
        project_cluster_key=key,
    )


def _archive_path(repo_root: Path, snapshot: str) -> Path:
    return Path(repo_root) / ARCHIVE_RELDIR / f"{snapshot}.tar"


def _extracted_path(repo_root: Path, snapshot: str) -> Path:
    return Path(repo_root) / EXTRACTED_RELDIR / snapshot


def _descriptor_path(repo_root: Path, snapshot: str) -> Path:
    return Path(repo_root) / DESCRIPTOR_RELDIR / f"{snapshot}.json"


def _pbf_path(repo_root: Path, snapshot: str) -> Path:
    return Path(repo_root) / PBF_RELDIR / f"public-behavior-frame-{snapshot}.json"


def inspect_regular_identity_file(path: Path) -> None:
    target = Path(path)
    if target.is_symlink():
        raise EvidenceError("IDENTITY_CONFLICT", f"identity file must not be a symlink: {target}")
    if not target.is_file():
        raise EvidenceError("IDENTITY_CONFLICT", f"identity file is absent: {target}")


def recover_production_source(binding: FrozenSubjectBinding, repo_root: Path) -> RecoveredSource:
    snapshot = binding.successor.neutral_snapshot_id
    record = binding.bridge_record
    expected_archive = validate_sha256(record["source_archive_sha256"], "source_archive_sha256")
    expected_tree = validate_sha256(
        record["normalized_source_tree_sha256"], "normalized_source_tree_sha256"
    )
    expected_descriptor = validate_sha256(
        record["build_descriptor_sha256"], "build_descriptor_sha256"
    )
    archive = _archive_path(repo_root, snapshot)
    if archive.is_symlink():
        raise EvidenceError("IDENTITY_CONFLICT", "source archive must not be a symlink")
    if not archive.is_file():
        raise EvidenceError(
            "SOURCE_RECOVERY_AUTHORITY_REQUIRED",
            "no unique approved source archive is present for this successor",
        )
    observed_archive = file_sha256(archive)
    if observed_archive != expected_archive:
        raise EvidenceError("IDENTITY_CONFLICT", "source archive SHA does not match verified_bridge")

    descriptor = _descriptor_path(repo_root, snapshot)
    try:
        from scripts.p3_v3.build_phase1_frames import load_descriptor

        load_descriptor(descriptor, expected_descriptor)
    except EvidenceError as exc:
        raise EvidenceError("IDENTITY_CONFLICT", str(exc)) from exc
    except OSError as exc:
        raise EvidenceError("INFRASTRUCTURE_FAILURE", str(exc)) from exc

    destination = _extracted_path(repo_root, snapshot)
    try:
        from scripts.p3_v3.build_phase1_frames import ensure_extracted_source

        source_root, _snapshot, _action = ensure_extracted_source(
            archive,
            destination,
            expected_archive,
            expected_tree,
        )
    except EvidenceError as exc:
        if exc.code in {"E_ARCHIVE_HASH", "E_SOURCE_TREE_COMMITMENT"}:
            raise EvidenceError("IDENTITY_CONFLICT", str(exc)) from exc
        if exc.code in {"E_ARCHIVE", "E_ARCHIVE_DESTINATION", "E_ARCHIVE_MEMBER"}:
            raise EvidenceError("INFRASTRUCTURE_FAILURE", str(exc)) from exc
        raise
    except OSError as exc:
        raise EvidenceError("INFRASTRUCTURE_FAILURE", f"source extraction failed: {exc}") from exc
    return RecoveredSource(
        archive_path=archive,
        archive_sha256=expected_archive,
        tree_sha256=expected_tree,
        extracted_root=Path(source_root),
        build_descriptor_sha256=expected_descriptor,
    )


def _subject_inventory_rows(
    inventory: Mapping[str, object],
    controlled_subject_id: str,
) -> list[dict[str, object]]:
    slots = inventory.get("slots")
    if not isinstance(slots, Sequence) or isinstance(slots, (str, bytes)):
        raise EvidenceError("IDENTITY_CONFLICT", "slot inventory is absent")
    rows = [
        dict(row)
        for row in slots
        if isinstance(row, Mapping) and row.get("controlled_subject_id") == controlled_subject_id
    ]
    if len(rows) != 10:
        raise EvidenceError("IDENTITY_CONFLICT", "subject must have exactly 10 inventory slots")
    return rows


def close_production_applicability(
    binding: FrozenSubjectBinding,
    source: RecoveredSource,
    repo_root: Path,
) -> tuple[SlotClosureRecord, ...]:
    del source
    root = Path(repo_root)
    try:
        authority = load_applicability_authority(
            manifest_path=root / AUTHORITY_RELPATH,
            registry_path=root / PREDICATE_REGISTRY_RELPATH,
            inventory_path=root / INVENTORY_RELPATH,
            slot_implementation_path=root / SLOT_IMPLEMENTATION_RELPATH,
            predicate_implementation_path=root / PREDICATE_IMPLEMENTATION_RELPATH,
        )
    except EvidenceError as exc:
        raise EvidenceError(
            "APPLICABILITY_EXECUTION_AUTHORITY_REQUIRED",
            str(exc),
        ) from exc
    rows = _subject_inventory_rows(
        authority["inventory"],
        binding.successor.controlled_subject_id,
    )
    pbf_path = _pbf_path(root, binding.successor.neutral_snapshot_id)
    inspect_regular_identity_file(pbf_path)
    try:
        frame = json.loads(pbf_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvidenceError("INFRASTRUCTURE_FAILURE", f"public behavior frame unreadable: {exc}") from exc
    if not isinstance(frame, Mapping):
        raise EvidenceError("IDENTITY_CONFLICT", "public behavior frame must be an object")
    if frame.get("controlled_subject_source_id") != binding.successor.controlled_subject_source_id:
        raise EvidenceError("IDENTITY_CONFLICT", "public behavior frame source identity mismatch")
    sites = frame.get("sites")
    if not isinstance(sites, Sequence) or isinstance(sites, (str, bytes)):
        raise EvidenceError("IDENTITY_CONFLICT", "public behavior frame sites are absent")
    closures: list[SlotClosureRecord] = []
    for row in rows:
        closed = close_slot_with_authority(authority, row, sites, frame)
        closures.append(
            SlotClosureRecord(
                slot_id=str(closed["slot_id"]),
                controlled_subject_id=str(closed["controlled_subject_id"]),
                state=str(closed["state"]),
                site_id=closed.get("site_id") if isinstance(closed.get("site_id"), str) else None,
            )
        )
    if len(closures) != 10:
        raise EvidenceError("IDENTITY_CONFLICT", "applicability must close exactly 10 slots")
    return tuple(closures)


def freeze_production_contracts(
    binding: FrozenSubjectBinding,
    closures: Sequence[SlotClosureRecord],
    repo_root: Path,
) -> tuple[AuthorizedContract, ...]:
    del closures
    root = Path(repo_root)
    registry_path = root / CONTRACT_REGISTRY_RELPATH
    inspect_regular_identity_file(registry_path)
    try:
        validate_contract_generator_registry(read_canonical_json(registry_path), root)
    except EvidenceError as exc:
        raise EvidenceError("CONTRACT_AUTHORITY_REQUIRED", str(exc)) from exc
    if binding.successor.successor_ordinal == 8:
        raise EvidenceError("IDENTITY_CONFLICT", "ordinal 8 must not enter contract freeze")
    # Successors have no source-authorized contract freeze. The existing
    # registry is loaded above; no generator is invented and ordinal-8
    # templates are not transferred.
    return ()


def construct_production_pairs(
    binding: FrozenSubjectBinding,
    contracts: Sequence[AuthorizedContract],
    repo_root: Path,
) -> tuple[CanonicalPair, ...]:
    del binding, repo_root
    if not contracts:
        return ()
    raise EvidenceError(
        "PAIRED_CONSTRUCTION_AUTHORITY_REQUIRED",
        "no reusable production pair-construction seam exists for this successor",
    )


def execute_production_pairs(
    binding: FrozenSubjectBinding,
    pairs: Sequence[CanonicalPair],
    repo_root: Path,
) -> tuple[PairExecutionRecord, ...]:
    del binding, repo_root
    if not pairs:
        return ()
    raise EvidenceError(
        "CONTROLLED_RUNNER_AUTHORITY_REQUIRED",
        "no reusable production controlled runner exists for this successor",
    )


def measure_production_overlap(
    binding: FrozenSubjectBinding,
    executions: Sequence[PairExecutionRecord],
    repo_root: Path,
) -> tuple[PairOverlapRecord, ...]:
    del binding, repo_root
    if not executions:
        return ()
    from scripts.p3_v3.measure_ordinal8_exact_overlap import exact_overlap

    measured: list[PairOverlapRecord] = []
    for item in executions:
        measured.append(
            PairOverlapRecord(
                pair=item.pair,
                normalized_patch_exact=exact_overlap(
                    item.pair.semantic_patch_sha256,
                    item.pair.syntactic_patch_sha256,
                ),
                mutant_tree_exact=exact_overlap(
                    item.pair.semantic_tree_sha256,
                    item.pair.syntactic_tree_sha256,
                ),
            )
        )
    return tuple(measured)


def default_production_seams() -> ProductionProcessorSeams:
    return ProductionProcessorSeams(
        recover_source=recover_production_source,
        close_applicability=close_production_applicability,
        freeze_contracts=freeze_production_contracts,
        construct_pairs=construct_production_pairs,
        execute_pairs=execute_production_pairs,
        measure_overlap=measure_production_overlap,
    )


def load_production_processor_adapters(repo_root: Path | None = None) -> dict[str, object]:
    del repo_root
    from scripts.p3_v3.build_phase1_frames import ensure_extracted_source, load_descriptor
    from scripts.p3_v3.measure_ordinal8_exact_overlap import exact_overlap

    adapters = {
        "ensure_extracted_source": ensure_extracted_source,
        "load_descriptor": load_descriptor,
        "load_applicability_authority": load_applicability_authority,
        "close_slot_with_authority": close_slot_with_authority,
        "validate_contract_generator_registry": validate_contract_generator_registry,
        "exact_overlap": exact_overlap,
        "bind_production_project_identity": bind_production_project_identity,
        "recover_production_source": recover_production_source,
        "close_production_applicability": close_production_applicability,
        "freeze_production_contracts": freeze_production_contracts,
        "construct_production_pairs": construct_production_pairs,
        "execute_production_pairs": execute_production_pairs,
        "measure_production_overlap": measure_production_overlap,
    }
    for name, item in adapters.items():
        if not callable(item):
            raise EvidenceError("PREFLIGHT_FAIL", f"production adapter is not callable: {name}")
    return adapters


def reduce_subject_for_stopping_rule(
    binding: FrozenSubjectBinding,
    terminal: SubjectTerminal,
    pair_count: int,
) -> SubjectPipelineResult:
    if pair_count > MAX_PAIRS_PER_SUBJECT:
        raise EvidenceError("IDENTITY_CONFLICT", "pair_count exceeds 4")
    if terminal is SubjectTerminal.PAIRED_EVIDENCE_COMPLETE and pair_count < 1:
        raise EvidenceError("IDENTITY_CONFLICT", "complete subject requires 1-4 pairs")
    return SubjectPipelineResult(
        successor_ordinal=binding.successor.successor_ordinal,
        project_cluster_key=binding.project_cluster_key,
        subject_terminal=terminal,
        pair_count=pair_count,
    )


def _failure_result(binding: FrozenSubjectBinding, code: str) -> SubjectPipelineResult:
    return reduce_subject_for_stopping_rule(binding, SubjectTerminal(code), 0)


def _pair_is_complete(execution: PairExecutionRecord, overlap: PairOverlapRecord | None) -> bool:
    if overlap is None:
        return False
    if not overlap.normalized_patch_present or not overlap.mutant_tree_present:
        return False
    return (
        execution.original.complete
        and execution.semantic.complete
        and execution.syntactic.complete
    )


def run_production_subject_pipeline(
    successor: SuccessorIdentity,
    *,
    repo_root: Path,
    seams: ProductionProcessorSeams | None = None,
    stage_trace: list[str] | None = None,
) -> SubjectPipelineResult:
    if production_processor_is_unconditional_stub():
        raise EvidenceError(
            "SLICE_B_PROCESSOR_AUTHORITY_REQUIRED",
            "production processor remains an unconditional stub",
        )
    active = seams if seams is not None else default_production_seams()
    root = Path(repo_root)
    _record_stage(stage_trace, "frozen_subject_identity")
    binding = freeze_subject_identity(successor, root)

    def finish(terminal: SubjectTerminal, pair_count: int) -> SubjectPipelineResult:
        _record_stage(stage_trace, "subject_terminal")
        _record_stage(stage_trace, "project_stopping_rule_reduction")
        return reduce_subject_for_stopping_rule(binding, terminal, pair_count)

    try:
        _record_stage(stage_trace, "source_identity_recovery")
        source = active.recover_source(binding, root)
        _record_stage(stage_trace, "authority_bound_applicability_closure")
        closures = tuple(active.close_applicability(binding, source, root))
        if len(closures) != 10:
            raise EvidenceError("IDENTITY_CONFLICT", "applicability must close exactly 10 slots")
        if all(item.state == _NOT_APPLICABLE for item in closures):
            return finish(SubjectTerminal.ALL_SLOTS_NOT_APPLICABLE, 0)
        _record_stage(stage_trace, "source_authorized_contract_freeze")
        contracts = tuple(active.freeze_contracts(binding, closures, root))
        eligible = tuple(item for item in closures if item.state == _SITE_FROZEN)
        if eligible and not contracts:
            return finish(SubjectTerminal.SITE_ELIGIBLE_NO_AUTHORIZED_CONTRACT, 0)
        _record_stage(stage_trace, "canonical_paired_constructions")
        pairs = tuple(active.construct_pairs(binding, contracts, root))
        if len(pairs) > MAX_PAIRS_PER_SUBJECT:
            raise EvidenceError("IDENTITY_CONFLICT", "pair_count exceeds 4")
        if contracts and not pairs:
            return finish(SubjectTerminal.PAIR_CONSTRUCTION_UNAVAILABLE, 0)
        for pair in pairs:
            if len(pair.input_ids) != FROZEN_INPUTS_PER_PAIR:
                raise EvidenceError("IDENTITY_CONFLICT", "each pair must use exactly 5 frozen inputs")
            if pair.semantic_kind != "semantic" or pair.syntactic_kind != "first-order syntactic":
                raise EvidenceError("IDENTITY_CONFLICT", "pair kinds must be semantic plus syntactic")
        _record_stage(stage_trace, "controlled_paired_execution")
        executions = tuple(active.execute_pairs(binding, pairs, root))
        if len(executions) != len(pairs):
            raise EvidenceError("IDENTITY_CONFLICT", "execution must cover constructed pairs once")
        for item in executions:
            if item.execution_order != _VARIANT_ORDER:
                raise EvidenceError("IDENTITY_CONFLICT", "original must execute before mutants")
            if (
                item.original.input_ids != item.pair.input_ids
                or item.semantic.input_ids != item.pair.input_ids
                or item.syntactic.input_ids != item.pair.input_ids
            ):
                raise EvidenceError("IDENTITY_CONFLICT", "variant input identities must stay frozen")
        _record_stage(stage_trace, "exact_overlap")
        overlaps = tuple(active.measure_overlap(binding, executions, root))
        by_slot = {item.pair.slot_id: item for item in overlaps}
        if len(by_slot) != len(overlaps):
            raise EvidenceError("IDENTITY_CONFLICT", "overlap records must be unique by slot")
        complete_count = 0
        for item in executions:
            overlap = by_slot.get(item.pair.slot_id)
            if overlap is None or not overlap.normalized_patch_present or not overlap.mutant_tree_present:
                raise EvidenceError(
                    "OVERLAP_EXECUTION_AUTHORITY_REQUIRED",
                    "both exact-overlap measures are required before a pair can complete",
                )
            if _pair_is_complete(item, overlap):
                complete_count += 1
        if complete_count < 1:
            raise EvidenceError(
                "OVERLAP_EXECUTION_AUTHORITY_REQUIRED",
                "no pair obtained original, semantic, syntactic, and both overlaps",
            )
        return finish(SubjectTerminal.PAIRED_EVIDENCE_COMPLETE, complete_count)
    except EvidenceError as exc:
        if exc.code in _PIPELINE_FAILURE_CODES:
            return finish(SubjectTerminal(exc.code), 0)
        if exc.code in _AUTHORITY_GAP_CODES:
            raise
        raise


def inspect_successor_source_inputs(repo_root: Path) -> dict[str, object]:
    """Identity-only inspection of ordinals 9-22. Does not execute predicates."""

    root = Path(repo_root)
    from scripts.p3_v3.build_phase1_frames import load_descriptor
    from scripts.p3_v3.prospective_applicability_search_v2 import FROZEN_SUCCESSOR_ROWS

    successors = load_frozen_successors()
    binder = production_project_binder(repo_root=root)
    records = {
        row["neutral_snapshot_id"]: row for row in load_frozen_bridge_identity_records(root)
    }
    inventory = read_canonical_json(root / INVENTORY_RELPATH)
    rows_by_subject: dict[str, int] = {}
    for raw in inventory.get("slots", []):
        if isinstance(raw, Mapping):
            subject = str(raw.get("controlled_subject_id"))
            rows_by_subject[subject] = rows_by_subject.get(subject, 0) + 1
    authority = read_canonical_json(root / AUTHORITY_RELPATH)
    projection = authority.get("subject_identity_projection")
    if not isinstance(projection, list):
        raise EvidenceError("PREFLIGHT_FAIL", "applicability authority projection is absent")
    frozen_rows = {
        int(row["successor_ordinal"]): row
        for row in FROZEN_SUCCESSOR_ROWS
        if FIRST_SUCCESSOR_ORDINAL <= int(row["successor_ordinal"]) <= LAST_SUCCESSOR_ORDINAL
    }
    subjects: list[dict[str, object]] = []
    archives_ready = True
    for successor in successors:
        record = records[successor.neutral_snapshot_id]
        frozen = frozen_rows[successor.successor_ordinal]
        descriptor = _descriptor_path(root, successor.neutral_snapshot_id)
        inspect_regular_identity_file(descriptor)
        load_descriptor(descriptor, record["build_descriptor_sha256"])
        pbf = _pbf_path(root, successor.neutral_snapshot_id)
        inspect_regular_identity_file(pbf)
        if file_sha256(pbf) != frozen["pbf_file_sha256"]:
            raise EvidenceError("PREFLIGHT_FAIL", "public behavior frame file SHA mismatch")
        if successor.controlled_subject_id not in projection:
            raise EvidenceError("PREFLIGHT_FAIL", "applicability authority does not cover successor")
        if rows_by_subject.get(successor.controlled_subject_id) != 10:
            raise EvidenceError("PREFLIGHT_FAIL", "10-slot inventory does not cover successor")
        binder(successor)
        archive = _archive_path(root, successor.neutral_snapshot_id)
        archive_ready = archive.is_file() and not archive.is_symlink()
        archive_sha_match = False
        if archive_ready:
            archive_sha_match = file_sha256(archive) == record["source_archive_sha256"]
            if not archive_sha_match:
                raise EvidenceError("PREFLIGHT_FAIL", "source archive SHA does not match verified_bridge")
        extracted = _extracted_path(root, successor.neutral_snapshot_id)
        if extracted.exists():
            if extracted.is_symlink() or not extracted.is_dir():
                raise EvidenceError("PREFLIGHT_FAIL", "extracted tree identity is unsafe")
        if not archive_ready:
            archives_ready = False
        subjects.append(
            {
                "successor_ordinal": successor.successor_ordinal,
                "archive_ready": archive_ready,
                "descriptor_ready": True,
                "pbf_ready": True,
                "inventory_ready": True,
                "authority_ready": True,
            }
        )
    return {
        "successor_count": len(subjects),
        "archives_ready": archives_ready,
        "descriptor_pbf_authority_ready": True,
        "subjects": subjects,
    }


def assess_production_processor_readiness(repo_root: Path) -> dict[str, object]:
    root = Path(repo_root)
    side_effects = {
        "predicates_executed": False,
        "sites_selected": False,
        "contracts_frozen": False,
        "mutants_constructed": False,
        "subjects_executed": False,
    }
    if production_processor_is_unconditional_stub():
        raise EvidenceError("PREFLIGHT_FAIL", "production processor is an unconditional stub")
    adapters = load_production_processor_adapters(root)
    binder = production_project_binder(repo_root=root)
    keys = [binder(item) for item in load_frozen_successors()]
    if len(keys) != 14 or any("/" not in key for key in keys):
        raise EvidenceError("PREFLIGHT_FAIL", "production binder does not cover ordinals 9-22")
    if (root / OFFICIAL_RELDIR).exists() or (root / STAGING_RELDIR).exists():
        raise EvidenceError("PREFLIGHT_FAIL", "official or staging namespace already exists")
    source_inputs = inspect_successor_source_inputs(root)
    return {
        "processor_implementation_kind": PROCESSOR_IMPLEMENTATION_KIND,
        "unconditional_stub": False,
        "processor_executable": True,
        "stages": list(PRODUCTION_PROCESSOR_STAGES),
        "adapters_loadable": sorted(adapters),
        "binder_covers_successors": True,
        "official_absent": True,
        "staging_absent": True,
        "source_inputs": source_inputs,
        "side_effects": side_effects,
    }
