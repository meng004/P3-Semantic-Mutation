from __future__ import annotations

import copy

import pytest

from p3_v3.artifacts import EvidenceError
from p3_v3.run_records import (
    close_phase,
    create_intent,
    reduce_attempts,
    verify_ledger,
    write_result,
)


def _intent(job_id="job-1", attempt=1):
    return {
        "job_id": job_id,
        "protocol_sha256": "a" * 64,
        "phase": "PHASE-2",
        "argv": ["python3", "-c", "print(1)"],
        "cwd_identity": "fixture-root",
        "environment_sha256": "b" * 64,
        "input_sha256": ["c" * 64],
        "seed": None,
        "timeout_seconds": 30,
        "attempt": attempt,
    }


def _result(job_id="job-1", attempt=1, status="PASS"):
    return {
        "job_id": job_id,
        "attempt": attempt,
        "status": status,
        "exit_code": 0 if status == "PASS" else 1,
        "stdout_sha256": "d" * 64,
        "stderr_sha256": "e" * 64,
        "duration_seconds": 0.25,
        "failure_code": "" if status == "PASS" else "E_SYNTHETIC",
    }


def test_result_requires_existing_intent(tmp_path):
    with pytest.raises(EvidenceError, match="E_RESULT_WITHOUT_INTENT"):
        write_result(tmp_path / "jobs/job-1/1", _result())


def test_intent_and_result_are_exclusive(tmp_path):
    attempt = tmp_path / "jobs/job-1/1"
    create_intent(attempt, _intent())
    with pytest.raises(EvidenceError, match="E_EXISTS"):
        create_intent(attempt, _intent())
    write_result(attempt, _result())
    with pytest.raises(EvidenceError, match="E_EXISTS"):
        write_result(attempt, _result())


def test_result_identity_must_match_intent(tmp_path):
    attempt = tmp_path / "jobs/job-1/1"
    create_intent(attempt, _intent())
    with pytest.raises(EvidenceError, match="E_RESULT_IDENTITY"):
        write_result(attempt, _result(job_id="job-2"))


def test_reducer_retains_failed_attempt_before_success(tmp_path):
    jobs = tmp_path / "jobs"
    first = jobs / "job-1/1"
    second = jobs / "job-1/2"
    create_intent(first, _intent(attempt=1))
    write_result(first, _result(attempt=1, status="FAIL_INFRASTRUCTURE"))
    create_intent(second, _intent(attempt=2))
    write_result(second, _result(attempt=2))
    ledger = tmp_path / "ledger.jsonl"
    events = reduce_attempts(jobs, ledger)
    assert [(event["kind"], event["attempt"]) for event in events] == [
        ("INTENT", 1),
        ("RESULT", 1),
        ("INTENT", 2),
        ("RESULT", 2),
    ]
    verify_ledger(ledger)


def test_reducer_rejects_noncontiguous_or_scientific_retry(tmp_path):
    jobs = tmp_path / "jobs"
    gap = jobs / "job-1/2"
    create_intent(gap, _intent(attempt=2))
    write_result(gap, _result(attempt=2))
    with pytest.raises(EvidenceError, match="E_ATTEMPT_SEQUENCE"):
        reduce_attempts(jobs, tmp_path / "gap.jsonl")

    other_jobs = tmp_path / "other-jobs"
    first = other_jobs / "job-2/1"
    second = other_jobs / "job-2/2"
    create_intent(first, _intent(job_id="job-2", attempt=1))
    write_result(first, _result(job_id="job-2", attempt=1, status="FAIL_SCIENTIFIC"))
    create_intent(second, _intent(job_id="job-2", attempt=2))
    write_result(second, _result(job_id="job-2", attempt=2))
    with pytest.raises(EvidenceError, match="E_RETRY_POLICY"):
        reduce_attempts(other_jobs, tmp_path / "scientific-retry.jsonl")


def test_ledger_tampering_breaks_event_hash(tmp_path):
    jobs = tmp_path / "jobs"
    attempt = jobs / "job-1/1"
    create_intent(attempt, _intent())
    write_result(attempt, _result())
    ledger = tmp_path / "ledger.jsonl"
    events = reduce_attempts(jobs, ledger)
    changed = copy.deepcopy(events)
    changed[0]["job_id"] = "other"
    ledger.write_text("\n".join(__import__("json").dumps(x, sort_keys=True, separators=(",", ":")) for x in changed) + "\n")
    with pytest.raises(EvidenceError, match="E_LEDGER_EVENT_HASH"):
        verify_ledger(ledger)


def test_ledger_rejects_rehashed_non_digest_artifact_identity(tmp_path):
    jobs = tmp_path / "jobs"
    attempt = jobs / "job-1/1"
    create_intent(attempt, _intent())
    write_result(attempt, _result())
    ledger = tmp_path / "ledger.jsonl"
    events = reduce_attempts(jobs, ledger)
    changed = copy.deepcopy(events)
    changed[0]["artifact_sha256"] = "not-a-digest"
    body = {key: value for key, value in changed[0].items() if key != "event_sha256"}
    from p3_v3.artifacts import canonical_sha256

    changed[0]["event_sha256"] = canonical_sha256(body)
    ledger.write_text(
        "\n".join(
            __import__("json").dumps(x, sort_keys=True, separators=(",", ":"))
            for x in changed
        )
        + "\n"
    )
    with pytest.raises(EvidenceError, match="E_SHA256"):
        verify_ledger(ledger)


def test_phase_close_rejects_pending_and_then_binds_complete_ledger(tmp_path):
    jobs = tmp_path / "jobs"
    attempt = jobs / "job-1/1"
    create_intent(attempt, _intent())
    pending_ledger = tmp_path / "pending.jsonl"
    reduce_attempts(jobs, pending_ledger)
    with pytest.raises(EvidenceError, match="E_PHASE_PENDING"):
        close_phase("PHASE-2", "a" * 64, ["job-1"], pending_ledger, "f" * 64)

    write_result(attempt, _result())
    ledger = tmp_path / "ledger.jsonl"
    reduce_attempts(jobs, ledger)
    receipt = close_phase("PHASE-2", "a" * 64, ["job-1"], ledger, "f" * 64)
    assert receipt["terminal_result_count"] == 1
    assert receipt["expected_job_count"] == 1
    assert len(receipt["ledger_raw_sha256"]) == 64


def test_phase_close_rejects_empty_phase_identity(tmp_path):
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_bytes(b"")
    with pytest.raises(EvidenceError, match="E_PHASE_ID"):
        close_phase("", "a" * 64, [], ledger, "f" * 64)
