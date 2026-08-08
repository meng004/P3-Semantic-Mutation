"""Immutable scientific-attempt records and phase-close receipts."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping, Sequence

from .artifacts import (
    EvidenceError,
    canonical_json_bytes,
    canonical_sha256,
    read_canonical_json,
    validate_exact_object,
    validate_sha256,
    write_canonical_json,
)


TERMINAL_STATES = {
    "PASS",
    "FAIL_SCIENTIFIC",
    "FAIL_INFRASTRUCTURE",
    "INCONCLUSIVE",
    "MISSING_WITH_REASON",
}
_INTENT_SCHEMA = {
    "job_id": str,
    "protocol_sha256": str,
    "phase": str,
    "argv": list,
    "cwd_identity": str,
    "environment_sha256": str,
    "input_sha256": list,
    "seed": (int, type(None)),
    "timeout_seconds": int,
    "attempt": int,
}
_RESULT_SCHEMA = {
    "job_id": str,
    "attempt": int,
    "status": str,
    "exit_code": (int, type(None)),
    "stdout_sha256": str,
    "stderr_sha256": str,
    "duration_seconds": (int, float),
    "failure_code": str,
}
_EVENT_SCHEMA = {
    "sequence": int,
    "kind": str,
    "job_id": str,
    "attempt": int,
    "artifact_sha256": str,
    "status": (str, type(None)),
    "previous_event_sha256": (str, type(None)),
    "event_sha256": str,
}


def _validate_intent(intent: Mapping[str, Any]) -> dict[str, Any]:
    value = validate_exact_object(dict(intent), _INTENT_SCHEMA, "intent")
    if not value["job_id"] or "/" in value["job_id"]:
        raise EvidenceError("E_JOB_ID", "job ID must be a nonempty path segment")
    validate_sha256(value["protocol_sha256"], "intent.protocol_sha256")
    validate_sha256(value["environment_sha256"], "intent.environment_sha256")
    if not value["argv"] or any(type(item) is not str or not item for item in value["argv"]):
        raise EvidenceError("E_INTENT_ARGV", "intent argv must contain nonempty strings")
    if value["input_sha256"] != sorted(set(value["input_sha256"])):
        raise EvidenceError("E_INTENT_INPUTS", "input hashes must be sorted and unique")
    for index, digest in enumerate(value["input_sha256"]):
        validate_sha256(digest, f"intent.input_sha256[{index}]")
    if type(value["seed"]) is bool:
        raise EvidenceError("E_INTENT_SEED", "seed cannot be boolean")
    if value["attempt"] < 1 or value["timeout_seconds"] < 1:
        raise EvidenceError("E_INTENT_RANGE", "attempt and timeout must be positive")
    return value


def _validate_result(result: Mapping[str, Any]) -> dict[str, Any]:
    value = validate_exact_object(dict(result), _RESULT_SCHEMA, "result")
    if value["status"] not in TERMINAL_STATES:
        raise EvidenceError("E_RESULT_STATUS", "result status is not terminal")
    for field in ("stdout_sha256", "stderr_sha256"):
        validate_sha256(value[field], f"result.{field}")
    if value["attempt"] < 1 or type(value["attempt"]) is bool:
        raise EvidenceError("E_RESULT_ATTEMPT", "result attempt must be positive")
    if value["duration_seconds"] < 0 or type(value["duration_seconds"]) is bool:
        raise EvidenceError("E_RESULT_DURATION", "duration cannot be negative")
    if value["status"] == "PASS" and (value["exit_code"] != 0 or value["failure_code"]):
        raise EvidenceError("E_RESULT_PASS", "PASS must have exit 0 and no failure code")
    if value["status"] != "PASS" and not value["failure_code"]:
        raise EvidenceError("E_RESULT_FAILURE_CODE", "non-PASS result needs a failure code")
    return value


def create_intent(attempt_dir: str | Path, intent: Mapping[str, Any]) -> None:
    value = _validate_intent(intent)
    directory = Path(attempt_dir)
    if directory.name != str(value["attempt"]) or directory.parent.name != value["job_id"]:
        raise EvidenceError("E_INTENT_PATH", "attempt path does not match intent identity")
    write_canonical_json(directory / "intent.json", value, exclusive=True)


def write_result(attempt_dir: str | Path, result: Mapping[str, Any]) -> None:
    directory = Path(attempt_dir)
    intent_path = directory / "intent.json"
    if not intent_path.exists():
        raise EvidenceError("E_RESULT_WITHOUT_INTENT", "result has no durable intent")
    intent = _validate_intent(read_canonical_json(intent_path))
    value = _validate_result(result)
    if value["job_id"] != intent["job_id"] or value["attempt"] != intent["attempt"]:
        raise EvidenceError("E_RESULT_IDENTITY", "result identity differs from intent")
    write_canonical_json(directory / "result.json", value, exclusive=True)


def _event(sequence: int, kind: str, payload: Mapping[str, Any], previous: str | None) -> dict:
    body = {
        "sequence": sequence,
        "kind": kind,
        "job_id": payload["job_id"],
        "attempt": payload["attempt"],
        "artifact_sha256": canonical_sha256(payload),
        "status": payload.get("status"),
        "previous_event_sha256": previous,
    }
    return {**body, "event_sha256": canonical_sha256(body)}


def _write_exclusive_bytes(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError as exc:
        raise EvidenceError("E_EXISTS", f"artifact already exists: {path}") from exc
    try:
        view = memoryview(raw)
        while view:
            written = os.write(fd, view)
            if written <= 0:
                raise OSError("short write")
            view = view[written:]
        os.fsync(fd)
    finally:
        os.close(fd)
    directory_fd = os.open(path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def reduce_attempts(job_root: str | Path, ledger_path: str | Path) -> list[dict[str, Any]]:
    root = Path(job_root)
    events: list[dict[str, Any]] = []
    previous: str | None = None
    for job_directory in sorted((item for item in root.iterdir() if item.is_dir()), key=lambda p: p.name):
        attempts: list[tuple[int, Path]] = []
        for attempt_directory in job_directory.iterdir():
            if not attempt_directory.is_dir() or not attempt_directory.name.isdecimal():
                raise EvidenceError("E_ATTEMPT_PATH", f"invalid attempt path: {attempt_directory}")
            attempt_number = int(attempt_directory.name)
            if attempt_number < 1 or str(attempt_number) != attempt_directory.name:
                raise EvidenceError("E_ATTEMPT_PATH", f"noncanonical attempt: {attempt_directory}")
            attempts.append((attempt_number, attempt_directory))
        attempts.sort()
        if [number for number, _ in attempts] != list(range(1, len(attempts) + 1)):
            raise EvidenceError("E_ATTEMPT_SEQUENCE", "attempts must be contiguous from one")
        if len(attempts) > 3:
            raise EvidenceError("E_RETRY_POLICY", "a job may have at most three attempts")
        previous_status: str | None = None
        for attempt_number, attempt_directory in attempts:
            if attempt_number > 1 and previous_status != "FAIL_INFRASTRUCTURE":
                raise EvidenceError(
                    "E_RETRY_POLICY",
                    "only a completed infrastructure failure permits another attempt",
                )
            intent_path = attempt_directory / "intent.json"
            if not intent_path.exists():
                raise EvidenceError("E_ATTEMPT_INTENT", f"missing intent: {attempt_directory}")
            intent = _validate_intent(read_canonical_json(intent_path))
            if intent["job_id"] != job_directory.name or intent["attempt"] != attempt_number:
                raise EvidenceError("E_ATTEMPT_IDENTITY", "attempt directory identity differs")
            intent_event = _event(len(events) + 1, "INTENT", intent, previous)
            events.append(intent_event)
            previous = intent_event["event_sha256"]
            result_path = attempt_directory / "result.json"
            if result_path.exists():
                result = _validate_result(read_canonical_json(result_path))
                if result["job_id"] != intent["job_id"] or result["attempt"] != intent["attempt"]:
                    raise EvidenceError("E_RESULT_IDENTITY", "result identity differs from intent")
                result_event = _event(len(events) + 1, "RESULT", result, previous)
                events.append(result_event)
                previous = result_event["event_sha256"]
                previous_status = result["status"]
            else:
                previous_status = None
    raw = b"".join(canonical_json_bytes(event) for event in events)
    _write_exclusive_bytes(Path(ledger_path), raw)
    return events


def verify_ledger(ledger_path: str | Path) -> list[dict[str, Any]]:
    raw = Path(ledger_path).read_bytes()
    events: list[dict[str, Any]] = []
    previous: str | None = None
    for line_number, line in enumerate(raw.splitlines(keepends=True), 1):
        try:
            event = json.loads(line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise EvidenceError("E_LEDGER_JSON", f"invalid ledger line {line_number}") from exc
        if canonical_json_bytes(event) != line:
            raise EvidenceError("E_LEDGER_CANONICAL", f"noncanonical ledger line {line_number}")
        validate_exact_object(event, _EVENT_SCHEMA, f"ledger[{line_number}]")
        validate_sha256(event["artifact_sha256"], f"ledger[{line_number}].artifact_sha256")
        validate_sha256(event["event_sha256"], f"ledger[{line_number}].event_sha256")
        if event["previous_event_sha256"] is not None:
            validate_sha256(
                event["previous_event_sha256"],
                f"ledger[{line_number}].previous_event_sha256",
            )
        if event["kind"] == "INTENT" and event["status"] is not None:
            raise EvidenceError("E_LEDGER_STATUS", "intent event cannot have status")
        if event["kind"] == "RESULT" and event["status"] not in TERMINAL_STATES:
            raise EvidenceError("E_LEDGER_STATUS", "result event status is not terminal")
        if event["kind"] not in {"INTENT", "RESULT"}:
            raise EvidenceError("E_LEDGER_KIND", f"unknown event kind: {event['kind']}")
        body = {key: value for key, value in event.items() if key != "event_sha256"}
        if event["event_sha256"] != canonical_sha256(body):
            raise EvidenceError("E_LEDGER_EVENT_HASH", f"event hash differs at {line_number}")
        if event["sequence"] != line_number or event["previous_event_sha256"] != previous:
            raise EvidenceError("E_LEDGER_CHAIN", f"event chain differs at {line_number}")
        previous = event["event_sha256"]
        events.append(event)
    return events


def close_phase(
    phase_id: str,
    protocol_sha256: str,
    expected_jobs: Sequence[str],
    ledger_path: str | Path,
    output_manifest_sha256: str,
) -> dict[str, Any]:
    if not isinstance(phase_id, str) or not phase_id or "/" in phase_id:
        raise EvidenceError("E_PHASE_ID", "phase ID must be a nonempty path segment")
    validate_sha256(protocol_sha256, "protocol_sha256")
    validate_sha256(output_manifest_sha256, "output_manifest_sha256")
    expected = list(expected_jobs)
    if expected != sorted(set(expected)) or any(not item or "/" in item for item in expected):
        raise EvidenceError("E_PHASE_JOBS", "expected jobs must be sorted unique path segments")
    events = verify_ledger(ledger_path)
    intents: dict[tuple[str, int], dict] = {}
    results: dict[tuple[str, int], dict] = {}
    for event in events:
        key = (event["job_id"], event["attempt"])
        if event["kind"] == "INTENT":
            intents[key] = event
        elif event["kind"] == "RESULT":
            results[key] = event
        else:
            raise EvidenceError("E_LEDGER_KIND", f"unknown event kind: {event['kind']}")
    if set(intents) != set(results):
        raise EvidenceError("E_PHASE_PENDING", "phase contains pending attempts")
    observed_jobs = sorted({job_id for job_id, _ in intents})
    if observed_jobs != expected:
        raise EvidenceError("E_PHASE_JOB_SET", "ledger jobs differ from expected inventory")
    ledger_raw = Path(ledger_path).read_bytes()
    body = {
        "phase_id": phase_id,
        "protocol_sha256": protocol_sha256,
        "expected_job_inventory_sha256": canonical_sha256(expected),
        "expected_job_count": len(expected),
        "terminal_result_count": len(results),
        "ledger_event_count": len(events),
        "ledger_head_sha256": events[-1]["event_sha256"] if events else None,
        "ledger_raw_sha256": hashlib.sha256(ledger_raw).hexdigest(),
        "output_manifest_sha256": output_manifest_sha256,
    }
    return {**body, "artifact_sha256": canonical_sha256(body)}
