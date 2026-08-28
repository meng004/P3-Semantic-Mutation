from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path

import pytest

from p3_v3.artifacts import EvidenceError, canonical_sha256, file_sha256
from p3_v3.multiproject_production_processor import (
    PROCESSOR_IMPLEMENTATION_KIND,
    AuthorizedContract,
    CanonicalPair,
    PairExecutionRecord,
    PairOverlapRecord,
    ProductionProcessorSeams,
    RecoveredSource,
    SlotClosureRecord,
    VariantResult,
    assess_production_processor_readiness,
    canonicalize_production_sites,
    default_production_seams,
    production_processor_is_unconditional_stub,
)
from p3_v3.prospective_multiproject import (
    DESIGN_FILE_SHA256,
    DESIGN_RELPATH,
    FIRST_SUCCESSOR_ORDINAL,
    HANDOFF_RELPATH,
    LAST_SUCCESSOR_ORDINAL,
    MAX_PAIRS_PER_SUBJECT,
    OFFICIAL_RELDIR,
    OFFICIAL_RUN_AUTHORIZED,
    ORDINAL8_HANDOFF_ARTIFACT_SHA256,
    ORDINAL8_OVERLAP_ARTIFACT_SHA256,
    OVERLAP_RELPATH,
    PRODUCTION_PROCESSOR_STAGES,
    PROJECT_CLUSTER_AUTHORITY_ARTIFACT_SHA256,
    PROJECT_CLUSTER_AUTHORITY_RELPATH,
    STAGING_RELDIR,
    SubjectPipelineResult,
    SubjectTerminal,
    SuccessorIdentity,
    VERIFIED_BRIDGE_RELPATH,
    advance_multiproject_state,
    initial_cohort_state,
    load_frozen_successors,
    process_production_subject,
    run_multiproject_search,
    validate_multiproject_preflight,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _digest(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def _inputs(label: str) -> tuple[str, ...]:
    return tuple(_digest(f"{label}-input-{index}") for index in range(5))


def _ordinal8() -> SuccessorIdentity:
    return SuccessorIdentity(
        successor_ordinal=8,
        neutral_snapshot_id="4e7e9556b3d621681c88c82f26cd95f5604d7a8b85cc56bf7e6d4db5a274f38b",
        controlled_subject_source_id="667f66bbdb3b392af99b044181dcfa861040546fc5550906e30fca2f9aabb5d0",
        controlled_subject_id="0fefefc546f7c4519d036849a85279cc7d3aa00fe88d6ed5e259209769b5bb48",
    )


def _foreign_successor() -> SuccessorIdentity:
    return SuccessorIdentity(
        successor_ordinal=23,
        neutral_snapshot_id=_digest("foreign-snapshot"),
        controlled_subject_source_id=_digest("foreign-source"),
        controlled_subject_id=_digest("foreign-subject"),
    )


def _not_applicable() -> tuple[SlotClosureRecord, ...]:
    subject = load_frozen_successors()[0].controlled_subject_id
    return tuple(
        SlotClosureRecord(
            slot_id=_digest(f"na-slot-{index}"),
            controlled_subject_id=subject,
            state="APPLICABILITY_CLOSED_NOT_APPLICABLE",
        )
        for index in range(10)
    )


def _eligible() -> tuple[SlotClosureRecord, ...]:
    subject = load_frozen_successors()[0].controlled_subject_id
    rows = [
        SlotClosureRecord(
            slot_id=_digest("eligible-slot-0"),
            controlled_subject_id=subject,
            state="SITE_FROZEN",
            site_id=_digest("eligible-site-0"),
        )
    ]
    rows.extend(
        SlotClosureRecord(
            slot_id=_digest(f"na-slot-{index}"),
            controlled_subject_id=subject,
            state="APPLICABILITY_CLOSED_NOT_APPLICABLE",
        )
        for index in range(1, 10)
    )
    return tuple(rows)


def _contracts(count: int = 1) -> tuple[AuthorizedContract, ...]:
    return tuple(
        AuthorizedContract(
            slot_id=_digest(f"eligible-slot-{index}"),
            contract_id=_digest(f"contract-{index}"),
            generator_id="CONTRACT_ARRAY_DOMAIN_V1",
            site_id=_digest(f"eligible-site-{index}"),
            input_ids=_inputs(f"contract-{index}"),
        )
        for index in range(count)
    )


def _pairs(count: int) -> tuple[CanonicalPair, ...]:
    return tuple(
        CanonicalPair(
            slot_id=_digest(f"eligible-slot-{index}"),
            input_ids=_inputs(f"pair-{index}"),
            semantic_kind="semantic",
            syntactic_kind="first-order syntactic",
            semantic_patch_sha256=_digest(f"sem-patch-{index}"),
            syntactic_patch_sha256=_digest(f"syn-patch-{index}"),
            semantic_tree_sha256=_digest(f"sem-tree-{index}"),
            syntactic_tree_sha256=_digest(f"syn-tree-{index}"),
        )
        for index in range(count)
    )


def _executions(pairs: Sequence[CanonicalPair]) -> tuple[PairExecutionRecord, ...]:
    return tuple(
        PairExecutionRecord(
            pair=pair,
            original=VariantResult("original", pair.input_ids, True),
            semantic=VariantResult("semantic", pair.input_ids, True),
            syntactic=VariantResult("syntactic", pair.input_ids, True),
            execution_order=("original", "semantic", "syntactic"),
        )
        for pair in pairs
    )


def _overlaps(pairs: Sequence[CanonicalPair], *, present: bool = True) -> tuple[PairOverlapRecord, ...]:
    return tuple(
        PairOverlapRecord(
            pair=pair,
            normalized_patch_exact=False,
            mutant_tree_exact=False,
            normalized_patch_present=present,
            mutant_tree_present=present,
        )
        for pair in pairs
    )


def _source() -> RecoveredSource:
    return RecoveredSource(
        archive_path=Path("/tmp/synthetic-archive.tar"),
        archive_sha256=_digest("archive"),
        tree_sha256=_digest("tree"),
        extracted_root=Path("/tmp/synthetic-tree"),
        build_descriptor_sha256=_digest("descriptor"),
    )


def _seams(
    *,
    closures: Sequence[SlotClosureRecord],
    contracts: Sequence[AuthorizedContract] = (),
    pairs: Sequence[CanonicalPair] = (),
    executions: Sequence[PairExecutionRecord] | None = None,
    overlaps: Sequence[PairOverlapRecord] | None = None,
    recover_error: EvidenceError | None = None,
    close_error: EvidenceError | None = None,
    close_fn=None,
    execute_error: EvidenceError | None = None,
    calls: list[str] | None = None,
    execution_order: tuple[str, ...] | None = None,
) -> ProductionProcessorSeams:
    observed = calls if calls is not None else []

    def recover(binding, repo_root):
        observed.append("recover")
        if recover_error is not None:
            raise recover_error
        return _source()

    def close(binding, source, repo_root):
        observed.append("close")
        if close_error is not None:
            raise close_error
        if close_fn is not None:
            return tuple(close_fn(binding, source, repo_root))
        return tuple(closures)

    def freeze(binding, closed, repo_root):
        observed.append("freeze")
        return tuple(contracts)

    def construct(binding, frozen, repo_root):
        observed.append("construct")
        return tuple(pairs)

    def execute(binding, constructed, repo_root):
        observed.append("execute")
        if execute_error is not None:
            raise execute_error
        records = list(executions if executions is not None else _executions(constructed))
        if execution_order is not None:
            records = [
                PairExecutionRecord(
                    pair=item.pair,
                    original=item.original,
                    semantic=item.semantic,
                    syntactic=item.syntactic,
                    execution_order=execution_order,
                )
                for item in records
            ]
        return tuple(records)

    def measure(binding, executed, repo_root):
        observed.append("measure")
        if overlaps is not None:
            return tuple(overlaps)
        return _overlaps([item.pair for item in executed])

    return ProductionProcessorSeams(
        recover_source=recover,
        close_applicability=close,
        freeze_contracts=freeze,
        construct_pairs=construct,
        execute_pairs=execute,
        measure_overlap=measure,
    )


def _run(successor=None, **kwargs) -> SubjectPipelineResult:
    item = load_frozen_successors()[0] if successor is None else successor
    return process_production_subject(item, repo_root=_repo_root(), **kwargs)


def test_unconditional_stub_is_gone_and_default_path_is_not_renamed_authority():
    assert production_processor_is_unconditional_stub() is False
    assert PROCESSOR_IMPLEMENTATION_KIND == "nine_stage_orchestration"
    seams = default_production_seams()
    assert seams.close_applicability.__name__ == "close_production_applicability"
    assert seams.close_applicability.__module__ == "p3_v3.multiproject_production_processor"
    result = _run(_seams=_seams(closures=_not_applicable()))
    assert result.subject_terminal is SubjectTerminal.ALL_SLOTS_NOT_APPLICABLE
    assert result.subject_terminal.value != "SLICE_B_PROCESSOR_AUTHORITY_REQUIRED"


def test_nine_stages_are_fixed_and_each_runs_at_most_once():
    assert PRODUCTION_PROCESSOR_STAGES == (
        "frozen_subject_identity",
        "source_identity_recovery",
        "authority_bound_applicability_closure",
        "source_authorized_contract_freeze",
        "canonical_paired_constructions",
        "controlled_paired_execution",
        "exact_overlap",
        "subject_terminal",
        "project_stopping_rule_reduction",
    )
    trace: list[str] = []
    calls: list[str] = []
    pairs = _pairs(2)
    result = _run(
        _seams= _seams(closures=_eligible(), contracts=_contracts(), pairs=pairs, calls=calls),
        _stage_trace=trace,
    )
    assert result.subject_terminal is SubjectTerminal.PAIRED_EVIDENCE_COMPLETE
    assert result.pair_count == 2
    assert trace == list(PRODUCTION_PROCESSOR_STAGES)
    assert len(trace) == len(set(trace))
    assert calls == ["recover", "close", "freeze", "construct", "execute", "measure"]


def test_ordinal_8_and_nonfrozen_successors_are_rejected():
    with pytest.raises(EvidenceError, match="IDENTITY_CONFLICT"):
        _run(_ordinal8())
    with pytest.raises(EvidenceError, match="IDENTITY_CONFLICT"):
        _run(_foreign_successor(), _seams=_seams(closures=_not_applicable()))


def test_funnel_terminals_from_synthetic_fixtures():
    na = _run(_seams=_seams(closures=_not_applicable()), _stage_trace=[])
    assert na.subject_terminal is SubjectTerminal.ALL_SLOTS_NOT_APPLICABLE
    assert na.pair_count == 0
    eligible = _run(_seams=_seams(closures=_eligible()), _stage_trace=[])
    assert eligible.subject_terminal is SubjectTerminal.SITE_ELIGIBLE_NO_AUTHORIZED_CONTRACT
    no_pair = _run(
        _seams=_seams(closures=_eligible(), contracts=_contracts(), pairs=()),
        _stage_trace=[],
    )
    assert no_pair.subject_terminal is SubjectTerminal.PAIR_CONSTRUCTION_UNAVAILABLE


@pytest.mark.parametrize("count", [1, 2, 3, 4])
def test_one_to_four_complete_pairs_are_complete(count: int):
    pairs = _pairs(count)
    result = _run(_seams=_seams(closures=_eligible(), contracts=_contracts(), pairs=pairs))
    assert result.subject_terminal is SubjectTerminal.PAIRED_EVIDENCE_COMPLETE
    assert result.pair_count == count


def test_more_than_four_pairs_are_rejected():
    result = _run(
        _seams=_seams(
            closures=_eligible(),
            contracts=_contracts(),
            pairs=_pairs(MAX_PAIRS_PER_SUBJECT + 1),
        )
    )
    assert result.subject_terminal is SubjectTerminal.IDENTITY_CONFLICT
    assert result.pair_count == 0


def test_source_and_runtime_failures_return_pipeline_terminals():
    conflict = _run(
        _seams=_seams(
            closures=_not_applicable(),
            recover_error=EvidenceError("IDENTITY_CONFLICT", "archive/tree mismatch"),
        )
    )
    assert conflict.subject_terminal is SubjectTerminal.IDENTITY_CONFLICT
    infra = _run(
        _seams=_seams(
            closures=_eligible(),
            contracts=_contracts(),
            pairs=_pairs(1),
            execute_error=EvidenceError("INFRASTRUCTURE_FAILURE", "runtime/build/oracle failed"),
        )
    )
    assert infra.subject_terminal is SubjectTerminal.INFRASTRUCTURE_FAILURE


def test_original_five_inputs_no_retry_and_both_overlaps_required():
    pairs = _pairs(1)
    calls: list[str] = []
    result = _run(
        _seams=_seams(closures=_eligible(), contracts=_contracts(), pairs=pairs, calls=calls)
    )
    assert result.subject_terminal is SubjectTerminal.PAIRED_EVIDENCE_COMPLETE
    assert calls.count("execute") == 1
    assert calls.count("measure") == 1
    assert len(pairs[0].input_ids) == 5
    mutant_first = _run(
        _seams=_seams(
            closures=_eligible(),
            contracts=_contracts(),
            pairs=pairs,
            execution_order=("semantic", "original", "syntactic"),
        )
    )
    assert mutant_first.subject_terminal is SubjectTerminal.IDENTITY_CONFLICT
    with pytest.raises(EvidenceError) as excinfo:
        _run(
            _seams=_seams(
                closures=_eligible(),
                contracts=_contracts(),
                pairs=pairs,
                overlaps=_overlaps(pairs, present=False),
            )
        )
    assert excinfo.value.code == "OVERLAP_EXECUTION_AUTHORITY_REQUIRED"
    with pytest.raises(TypeError):
        process_production_subject(
            load_frozen_successors()[0],
            repo_root=_repo_root(),
            retry=True,
        )
    with pytest.raises(TypeError):
        process_production_subject(
            load_frozen_successors()[0],
            repo_root=_repo_root(),
            resume=True,
        )


def _ordinal8_observation():
    from p3_v3.prospective_multiproject import Ordinal8RetainedObservation

    return Ordinal8RetainedObservation(
        successor_ordinal=8,
        neutral_snapshot_id="4e7e9556b3d621681c88c82f26cd95f5604d7a8b85cc56bf7e6d4db5a274f38b",
        controlled_subject_source_id="667f66bbdb3b392af99b044181dcfa861040546fc5550906e30fca2f9aabb5d0",
        controlled_subject_id="0fefefc546f7c4519d036849a85279cc7d3aa00fe88d6ed5e259209769b5bb48",
        project_cluster_key="github.com/numpy/numpy",
        pair_count=4,
        semantic_pair_kills=4,
        syntactic_pair_kills=3,
        d_subject=0.25,
        normalized_patch_overlap_numerator=0,
        normalized_patch_overlap_denominator=4,
        mutant_tree_overlap_numerator=0,
        mutant_tree_overlap_denominator=4,
        rerun_forbidden=True,
    )


def _process_table(table: Mapping[int, SubjectPipelineResult], seen: list[int]):
    def process(successor: SuccessorIdentity) -> SubjectPipelineResult:
        seen.append(successor.successor_ordinal)
        return table[successor.successor_ordinal]

    return process


def test_search_funnel_failure_same_repo_two_projects_and_no_later_ordinal():
    successors = load_frozen_successors()
    seen: list[int] = []
    table = {
        ordinal: SubjectPipelineResult(
            successor_ordinal=ordinal,
            project_cluster_key="github.com/llnl/sundials",
            subject_terminal=SubjectTerminal.ALL_SLOTS_NOT_APPLICABLE,
            pair_count=0,
        )
        for ordinal in range(FIRST_SUCCESSOR_ORDINAL, LAST_SUCCESSOR_ORDINAL + 1)
    }
    table[9] = SubjectPipelineResult(
        successor_ordinal=9,
        project_cluster_key="github.com/llnl/sundials",
        subject_terminal=SubjectTerminal.SITE_ELIGIBLE_NO_AUTHORIZED_CONTRACT,
        pair_count=0,
    )
    table[10] = SubjectPipelineResult(
        successor_ordinal=10,
        project_cluster_key="github.com/llnl/sundials",
        subject_terminal=SubjectTerminal.PAIRED_EVIDENCE_COMPLETE,
        pair_count=1,
    )
    table[11] = SubjectPipelineResult(
        successor_ordinal=11,
        project_cluster_key="github.com/llnl/sundials",
        subject_terminal=SubjectTerminal.PAIRED_EVIDENCE_COMPLETE,
        pair_count=2,
    )
    table[15] = SubjectPipelineResult(
        successor_ordinal=15,
        project_cluster_key="github.com/reference-lapack/lapack",
        subject_terminal=SubjectTerminal.PAIRED_EVIDENCE_COMPLETE,
        pair_count=1,
    )
    result = run_multiproject_search(
        process_subject=_process_table(table, seen),
        bind_project=lambda successor: table[successor.successor_ordinal].project_cluster_key,
        ordinal8=_ordinal8_observation(),
    )
    assert seen == [9, 10, 11, 12, 13, 14, 15]
    assert 16 not in seen
    assert 22 not in seen
    assert 23 not in seen
    assert result.completed_new_project_keys == (
        "github.com/llnl/sundials",
        "github.com/reference-lapack/lapack",
    )
    failure_seen: list[int] = []
    failure_table = {
        9: SubjectPipelineResult(
            successor_ordinal=9,
            project_cluster_key="github.com/llnl/sundials",
            subject_terminal=SubjectTerminal.IDENTITY_CONFLICT,
            pair_count=0,
        ),
        10: SubjectPipelineResult(
            successor_ordinal=10,
            project_cluster_key="github.com/llnl/sundials",
            subject_terminal=SubjectTerminal.PAIRED_EVIDENCE_COMPLETE,
            pair_count=1,
        ),
    }
    failed = run_multiproject_search(
        process_subject=_process_table(failure_table, failure_seen),
        bind_project=lambda successor: "github.com/llnl/sundials",
        ordinal8=_ordinal8_observation(),
    )
    assert failure_seen == [9]
    assert failed.status.value == "IDENTITY_CONFLICT"

    state = initial_cohort_state(successors, _ordinal8_observation())
    state = advance_multiproject_state(state, table[9])
    assert state.status.value == "IN_PROGRESS"
    state = advance_multiproject_state(state, table[10])
    assert state.completed_new_project_keys == ("github.com/llnl/sundials",)


def test_readiness_function_rejects_stub_without_run_side_effects(monkeypatch):
    import p3_v3.multiproject_production_processor as processor
    import p3_v3.applicability_predicates as predicates
    import p3_v3.contract_authority as contracts

    root = _repo_root()
    called: list[str] = []

    def forbidden(*args, **kwargs):
        called.append("forbidden")
        raise AssertionError("readiness executed a production seam")

    monkeypatch.setattr(predicates, "close_slot_with_authority", forbidden)
    monkeypatch.setattr(predicates, "evaluate_predicate", forbidden)
    monkeypatch.setattr(contracts, "build_ordinal8_contracts", forbidden)
    monkeypatch.setattr(processor, "recover_production_source", forbidden)
    readiness = assess_production_processor_readiness(root)
    assert readiness["processor_executable"] is True
    assert readiness["unconditional_stub"] is False
    payload = validate_multiproject_preflight(
        repo_root=root,
        controller_path=root / "src/p3_v3/prospective_multiproject.py",
    )
    assert payload["status"] == "MULTIPROJECT_PREFLIGHT_PASS"
    assert payload["processor_executable"] is True
    assert called == []
    monkeypatch.setattr(processor, "production_processor_is_unconditional_stub", lambda: True)
    with pytest.raises(EvidenceError, match="PREFLIGHT_FAIL"):
        assess_production_processor_readiness(root)
    with pytest.raises(EvidenceError, match="PREFLIGHT_FAIL"):
        validate_multiproject_preflight(
            repo_root=root,
            controller_path=root / "src/p3_v3/prospective_multiproject.py",
        )


def test_official_staging_absent_and_frozen_bytes_unchanged():
    root = _repo_root()
    assert OFFICIAL_RUN_AUTHORIZED is False
    assert not (root / OFFICIAL_RELDIR).exists()
    assert not (root / STAGING_RELDIR).exists()
    assert file_sha256(root / DESIGN_RELPATH) == DESIGN_FILE_SHA256
    handoff = json.loads((root / HANDOFF_RELPATH).read_text(encoding="utf-8"))
    overlap = json.loads((root / OVERLAP_RELPATH).read_text(encoding="utf-8"))
    assert handoff["artifact_sha256"] == ORDINAL8_HANDOFF_ARTIFACT_SHA256
    assert overlap["artifact_sha256"] == ORDINAL8_OVERLAP_ARTIFACT_SHA256
    authority = json.loads((root / PROJECT_CLUSTER_AUTHORITY_RELPATH).read_text(encoding="utf-8"))
    assert authority["artifact_sha256"] == PROJECT_CLUSTER_AUTHORITY_ARTIFACT_SHA256
    bridge = json.loads((root / VERIFIED_BRIDGE_RELPATH).read_text(encoding="utf-8"))
    assert len(bridge["records"]) == 35


def _synthetic_raw_site(
    path: str,
    symbol: str,
    *,
    start_line: int = 1,
    start_col: int = 0,
    end_line: int = 2,
    end_col: int = 1,
) -> dict[str, object]:
    return {
        "path": path,
        "symbol": symbol,
        "start_line": start_line,
        "start_col": start_col,
        "end_line": end_line,
        "end_col": end_col,
    }


def _p3_site_v1_id(controlled_subject_id: str, raw_site: Mapping[str, object]) -> str:
    return canonical_sha256(
        {
            "controlled_subject_id": controlled_subject_id,
            **dict(raw_site),
            "domain": "P3-SITE-v1",
        }
    )


def test_raw_pbf_sites_canonicalize_through_existing_p3_site_v1_seam():
    subject = load_frozen_successors()[0].controlled_subject_id
    raw = [
        _synthetic_raw_site("synthetic/z_mod.py", "beta"),
        _synthetic_raw_site("synthetic/a_mod.py", "alpha"),
    ]
    assert all("site_id" not in item for item in raw)
    observed = canonicalize_production_sites(subject, raw)
    from p3_v3.bridge_and_frames import _sites

    assert observed == _sites(subject, raw)
    assert [item["path"] for item in observed] == [
        "synthetic/a_mod.py",
        "synthetic/z_mod.py",
    ]
    assert [item["site_id"] for item in observed] == [
        _p3_site_v1_id(subject, _synthetic_raw_site("synthetic/a_mod.py", "alpha")),
        _p3_site_v1_id(subject, _synthetic_raw_site("synthetic/z_mod.py", "beta")),
    ]
    shuffled = canonicalize_production_sites(subject, list(reversed(raw)))
    assert [item["site_id"] for item in shuffled] == [item["site_id"] for item in observed]
    assert [item["path"] for item in shuffled] == [item["path"] for item in observed]


def test_malformed_raw_site_maps_to_identity_conflict_and_does_not_leak():
    subject = load_frozen_successors()[0].controlled_subject_id
    with pytest.raises(EvidenceError) as direct:
        canonicalize_production_sites(subject, [{"path": "synthetic/broken.py"}])
    assert direct.value.code == "IDENTITY_CONFLICT"
    assert direct.value.code != "E_SCHEMA_KEYS"

    def close(binding, source, repo_root):
        canonicalize_production_sites(
            binding.successor.controlled_subject_id,
            [{"path": "synthetic/broken.py"}],
        )
        return _not_applicable()

    result = _run(_seams=_seams(closures=_not_applicable(), close_fn=close))
    assert result.subject_terminal is SubjectTerminal.IDENTITY_CONFLICT
    mapped = _run(
        _seams=_seams(
            closures=_not_applicable(),
            close_error=EvidenceError("E_SCHEMA_KEYS", "canonical_sites[0] keys differ"),
        )
    )
    assert mapped.subject_terminal is SubjectTerminal.IDENTITY_CONFLICT


def test_controlled_subject_id_mismatch_is_fail_closed():
    first, second = load_frozen_successors()[0], load_frozen_successors()[1]
    raw = [_synthetic_raw_site("synthetic/only.py", "gamma")]
    with pytest.raises(EvidenceError) as excinfo:
        canonicalize_production_sites(
            second.controlled_subject_id,
            raw,
            frozen_controlled_subject_id=first.controlled_subject_id,
        )
    assert excinfo.value.code == "IDENTITY_CONFLICT"
    left = canonicalize_production_sites(first.controlled_subject_id, raw)
    right = canonicalize_production_sites(second.controlled_subject_id, raw)
    assert left[0]["site_id"] != right[0]["site_id"]


def test_default_seams_are_production_adapters_not_ordinal8_copies():
    seams = default_production_seams()
    assert seams.recover_source.__module__ == "p3_v3.multiproject_production_processor"
    assert seams.close_applicability.__module__ == "p3_v3.multiproject_production_processor"
    assert seams.freeze_contracts.__module__ == "p3_v3.multiproject_production_processor"
    readiness = assess_production_processor_readiness(_repo_root())
    assert readiness["processor_executable"] is True
    assert "ensure_extracted_source" in readiness["adapters_loadable"]
    assert "close_slot_with_authority" in readiness["adapters_loadable"]
    assert "exact_overlap" in readiness["adapters_loadable"]
    assert readiness["source_inputs"]["successor_count"] == 14
    assert readiness["source_inputs"]["descriptor_pbf_authority_ready"] is True
